"""Fetch file listings from the archive.org metadata API into the database."""

from __future__ import annotations

import concurrent.futures
import gzip
import json
import sqlite3
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import requests

from . import minerva, names
from .paths import resource

CONFIG_PATH = resource("sources.json")
METADATA_URL = "https://archive.org/metadata/{}"
DOWNLOAD_URL = "https://archive.org/download/{}/{}"
USER_AGENT = "RomSrx/0.1 (personal local index; +https://archive.org)"


def load_config(path: Path = CONFIG_PATH) -> dict:
    with open(path, encoding="utf-8") as fh:
        config = json.load(fh)
    config["extensions"] = {e.lower() for e in config.get("extensions", [])}
    return config


# A healthy archive.org answers a metadata request in about a second. This
# ceiling is for a bad day, not a normal one, and it is worth keeping close:
# it is what one stalled source costs, three times over, while the rest of the
# index waits behind it. It used to be 120, which was never measured against
# anything and turned a bad hour at archive.org into a reindex of several.
TIMEOUT = 45

# A collection listing is eight megabytes of HTML rather than a page of JSON,
# and it is generated per request. Six seconds is normal; this is the ceiling
# for a bad one.
LISTING_TIMEOUT = 120

# However long a server asks to be left alone, it is not worth more than this:
# the whole index is queued behind one source, and a request to wait an hour
# is better answered by giving up on that source and reporting it.
RETRY_WAIT_CAP = 60

# The codes worth trying again. These mean busy, or briefly broken. Everything
# else the server might say - not found, gone, forbidden - it will say just as
# firmly the second and third time, and asking again only makes an index that
# is already struggling slower.
RETRY_CODES = frozenset({408, 425, 429, 500, 502, 503, 504})


class Unchanged(Exception):
    """The server says the listing is exactly what it was last time."""


class _Busy(Exception):
    """A server saying "not now" - one of RETRY_CODES, and worth waiting for.

    Carries Retry-After when the server sent one, because a server that says
    how long it wants to be left alone should be listened to.
    """

    def __init__(self, message: str, code: int = 0, retry_after=None) -> None:
        super().__init__(message)
        self.code = code
        self.headers = {"Retry-After": retry_after} if retry_after else {}


# One HTTP connection per thread, kept open across sources.
#
# A reindex is three hundred requests to two hosts, and every one of them was
# opening a new connection and negotiating TLS from scratch before asking for
# anything. Reusing the connection removes that handshake from all but the
# first request a thread makes.
_local = threading.local()


def _http():
    session = getattr(_local, "session", None)
    if session is None:
        session = requests.Session()
        session.headers.update({"User-Agent": USER_AGENT,
                                "Accept-Encoding": "gzip"})
        _local.session = session
    return session


def _retry_wait(exc: Exception, attempt: int) -> float:
    """How long to wait before asking again.

    A server that says how long to wait is believed, within reason - honouring
    it is the difference between easing off and making the throttling worse by
    hammering through it. Only the plain "wait this many seconds" form is read;
    the date form is rare here and the fallback covers it.
    """
    headers = getattr(exc, "headers", None)
    if headers:
        asked = str(headers.get("Retry-After") or "").strip()
        if asked.isdigit():
            return min(int(asked), RETRY_WAIT_CAP)
    return min(2 ** attempt * 2, RETRY_WAIT_CAP)


def fetch_metadata(identifier: str, *, retries: int = 3,
                   timeout: int = TIMEOUT) -> dict:
    """GET the item metadata, retrying with backoff on transient failures.

    Over the thread's own kept-open connection. A reindex asks archive.org
    about a hundred and ninety items, and each one used to begin by opening a
    socket and negotiating TLS before it could ask anything at all.

    archive.org offers no ETag and no Last-Modified on this endpoint, so
    unlike a MiNERVA listing there is no way to ask whether it has changed -
    the whole thing comes back every time.
    """
    url = METADATA_URL.format(urllib.parse.quote(identifier))
    last_error: Exception | None = None

    for attempt in range(retries):
        try:
            resp = _http().get(url, timeout=timeout)
            if resp.status_code in RETRY_CODES:
                raise _Busy(f"HTTP {resp.status_code}", resp.status_code,
                            resp.headers.get("Retry-After"))
            resp.raise_for_status()
            return resp.json()
        # A server that answered deserves a different decision from one that
        # never did: only the codes that mean "busy, or briefly broken" are
        # worth waiting for.
        except _Busy as exc:
            last_error = exc
            if attempt < retries - 1:
                time.sleep(_retry_wait(exc, attempt))
        except requests.HTTPError as exc:
            last_error = exc
            break
        except (requests.RequestException, TimeoutError, OSError,
                ValueError) as exc:
            last_error = exc
            if attempt < retries - 1:
                time.sleep(_retry_wait(exc, attempt))

    raise RuntimeError(f"failed to fetch {identifier}: {last_error}")


def needs_login(metadata: dict) -> bool:
    """True when archive.org will only serve this item to a signed-in account.

    These items sit in the 'loggedin' collection and/or are flagged
    access-restricted; anonymous downloads get a 401/403 back.
    """
    meta = metadata.get("metadata", {})
    collections = meta.get("collection", [])
    if isinstance(collections, str):
        collections = [collections]
    if "loggedin" in collections:
        return True
    restricted = meta.get("access-restricted-item")
    return str(restricted).lower() == "true"


def probe_source(identifier: str, timeout: int = 45) -> dict:
    """Ask archive.org about one item, once, and say what came back.

    Without the retry ladder `fetch_metadata` uses, on purpose. This is a
    snapshot of whether an item can be reached right now, and retrying is
    exactly what would hide the flakiness it is meant to show.

    The four answers are worth telling apart. An item that is not there
    answers quickly - a 404, or an empty body - and costs an index almost
    nothing. An item that cannot be reached costs it minutes, because that is
    what sends `fetch_metadata` round its ladder. So "unreachable" points at
    the connection, and "gone" or "empty" points at the source.
    """
    url = METADATA_URL.format(urllib.parse.quote(identifier))
    request = urllib.request.Request(url, headers={
        "User-Agent": USER_AGENT,
        "Accept-Encoding": "gzip",
    })
    started = time.time()

    def answer(state, detail="", files=0):
        return {"identifier": identifier, "state": state, "detail": detail,
                "files": files, "seconds": time.time() - started}

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read()
            if response.headers.get("Content-Encoding") == "gzip":
                raw = gzip.decompress(raw)
        body = json.loads(raw.decode("utf-8", "replace"))
    except urllib.error.HTTPError as exc:
        return answer("gone" if exc.code == 404 else "unreachable",
                      f"HTTP {exc.code}")
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return answer("unreachable", str(getattr(exc, "reason", exc))[:70])
    except json.JSONDecodeError:
        return answer("unreachable", "the reply was not readable")

    files = len(body.get("files") or [])
    return answer("ok" if files else "empty", "", files)


def check_sources(config: dict, only=None, workers: int = 8,
                  timeout: int = 45, progress=print) -> dict:
    """Reach every configured item once and report which ones answered.

    Meant to be run instead of an index when one is being slow, since it asks
    the same servers the same question without downloading anything.
    """
    sources = config["sources"]
    if only:
        wanted = {s.lower() for s in only}
        sources = [s for s in sources
                   if s["id"].lower() in wanted
                   or s["console"].lower() in wanted
                   or s["identifier"].lower() in wanted]
        if not sources:
            raise SystemExit(f"no sources matched: {', '.join(only)}")

    # One check per item, not per source: several sources share an item, and
    # asking about the same one nine times measures nothing but patience.
    labels: dict[str, list[str]] = {}
    for source in sources:
        labels.setdefault(source["identifier"], []).append(
            f"{source['console']}  {source['name']}")

    progress(f"Checking {len(labels)} item(s) behind {len(sources)} source(s)"
             f" with {workers} workers...\n")

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(probe_source, ident, timeout): ident
                   for ident in labels}
        for done in concurrent.futures.as_completed(futures):
            result = done.result()
            result["sources"] = labels[result["identifier"]]
            results.append(result)
            mark = {"ok": "ok   ", "empty": "EMPTY", "gone": "GONE ",
                    "unreachable": "UNREACHABLE"}[result["state"]]
            detail = f"  {result['detail']}" if result["detail"] else ""
            progress(f"  {mark:11}  {result['identifier'][:46]:46} "
                     f"{result['files']:>8,} files  {result['seconds']:5.1f}s"
                     f"{detail}")

    results.sort(key=lambda r: (r["state"] != "unreachable", r["identifier"]))
    tally = {state: sum(1 for r in results if r["state"] == state)
             for state in ("ok", "empty", "gone", "unreachable")}
    return {"results": results, "tally": tally, "items": len(labels),
            "sources": len(sources)}


def _download_url(identifier: str, path: str) -> str:
    quoted = urllib.parse.quote(path, safe="/")
    return DOWNLOAD_URL.format(urllib.parse.quote(identifier), quoted)


def fetch_listing(identifier: str, *, retries: int = 3,
                  etag: str = "") -> dict:
    """One MiNERVA collection, in the shape the rest of this module expects.

    A directory listing rather than a metadata API: eleven thousand games come
    back as eight megabytes of HTML, which is both slower to parse and far
    less to ask of a server than eleven thousand requests would be.

    `etag` is what the server said about this listing last time. Sent back as
    If-None-Match, it lets the server answer "no change" in half a second
    instead of sending three megabytes again - and MiNERVA does offer one,
    which archive.org does not. Raises Unchanged when it says so, and the
    caller keeps the rows it already has.

    The same retry rules as archive.org, and for the same reason - a busy
    server is a reason to wait, not a reason to lose a console.
    """
    url = minerva.listing_url(identifier)
    last: Exception | None = None
    for attempt in range(retries):
        try:
            headers = {"Accept": "text/html"}
            if etag:
                headers["If-None-Match"] = etag
            resp = _http().get(url, headers=headers,
                               timeout=LISTING_TIMEOUT)
            if resp.status_code == 304:
                raise Unchanged(identifier)
            resp.raise_for_status()
            page = resp.text
            found = minerva.entries(page)
            if not found:
                raise ValueError("no games in that listing")
            return {"minerva": found, "etag": resp.headers.get("ETag") or ""}
        except Unchanged:
            raise
        except Exception as exc:  # noqa: BLE001 - retried, then reported
            last = exc
            if attempt + 1 < retries:
                time.sleep(_retry_wait(exc, attempt))
    raise last or RuntimeError("could not read the listing")


def fetch_source(kind: str, identifier: str, etag: str = "") -> dict:
    """Whatever this source's shelf answers with."""
    if kind == "minerva":
        return fetch_listing(identifier, etag=etag)
    # archive.org offers neither an ETag nor a Last-Modified on its metadata,
    # so there is no question to ask it but the whole one.
    return fetch_metadata(identifier)


def _minerva_rows(source: dict, found: list[dict],
                  extensions: set[str]) -> list[dict]:
    """MiNERVA entries as file rows.

    The url is a magnet with the file's index on the end - see minerva.py for
    why that is the whole address a download needs. The path is the collection
    and the filename together, so two consoles' copies of the same game are
    still two different rows.
    """
    folder = str(source["identifier"]).strip("/").lstrip("./")
    default_region = source.get("default_region")
    rows = []
    for entry in found:
        name = entry["filename"]
        if names.is_metadata_file(name, None):
            continue
        # The translation collections ship a documentation bundle beside the
        # games, named `_<system> [T-En] Docs.zip`. It is two hundred megabytes
        # of readme and it lands in search as a game called "Nintendo Famicom".
        #
        # Matched on both ends rather than on the underscore alone: `_summer
        # Double Sharp (Japan).zip` is a real game, and a rule that read a
        # leading underscore as "not a game" would quietly lose it.
        if name.startswith("_") and name.endswith("Docs.zip"):
            continue
        parsed = names.parse(name, default_region=default_region)
        if extensions and parsed["ext"].split(".")[-1] not in extensions:
            continue
        rows.append({
            "source_id": source["id"],
            "console": source["console"],
            "path": f"{folder}/{name}",
            "filename": name,
            "title": parsed["title"],
            "title_norm": parsed["title_norm"],
            "regions": ",".join(parsed["regions"]),
            "languages": ",".join(parsed["languages"]),
            "version": parsed["version"],
            "disc": parsed["disc"],
            "tags": "|".join(parsed["tags"]),
            "ext": parsed["ext"],
            "size": entry["size"],
            "url": entry["magnet"],
        })
    return rows


def extract_files(source: dict, metadata: dict, extensions: set[str]) -> list[dict]:
    """Turn a metadata payload into parsed file rows for one source."""
    if "minerva" in metadata:
        return _minerva_rows(source, metadata["minerva"], extensions)

    identifier = source["identifier"]
    prefix = (source.get("path_prefix") or "").strip("/")
    default_region = source.get("default_region")
    rows: list[dict] = []

    for entry in metadata.get("files", []):
        path = entry.get("name", "")
        if not path:
            continue
        if prefix and not path.startswith(prefix + "/"):
            continue
        if names.is_metadata_file(path, entry.get("format")):
            continue

        parsed = names.parse(path, default_region=default_region)
        if extensions and parsed["ext"].split(".")[-1] not in extensions:
            continue

        try:
            size = int(entry.get("size") or 0)
        except (TypeError, ValueError):
            size = 0

        rows.append({
            "source_id": source["id"],
            "console": source["console"],
            "path": path,
            "filename": path.rsplit("/", 1)[-1],
            "title": parsed["title"],
            "title_norm": parsed["title_norm"],
            "regions": ",".join(parsed["regions"]),
            "languages": ",".join(parsed["languages"]),
            "version": parsed["version"],
            "disc": parsed["disc"],
            "tags": "|".join(parsed["tags"]),
            "ext": parsed["ext"],
            "size": size,
            "url": _download_url(identifier, path),
        })

    return rows


def console_order(config: dict) -> dict[str, int]:
    """Map each console to a display rank based on its order in sources.json."""
    order: dict[str, int] = {}
    for source in config["sources"]:
        order.setdefault(source["console"], len(order))
    return order


def store_source(conn: sqlite3.Connection, source: dict, rows: list[dict],
                 error: str | None = None, requires_login: bool = False,
                 console_rank: int = 0, etag: str = "") -> None:
    """Replace all indexed files for one source inside a single transaction."""
    total = sum(r["size"] for r in rows)
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    if (source.get("kind") or "archive") == "minerva":
        item_url = minerva.listing_url(source["identifier"])
    else:
        item_url = f"https://archive.org/download/{source['identifier']}"
        if source.get("path_prefix"):
            item_url += "/" + source["path_prefix"].strip("/")

    with conn:
        conn.execute("""
            INSERT INTO sources (id, console, name, identifier, path_prefix,
                                 url, file_count, total_size, last_indexed,
                                 last_error, requires_login, console_rank,
                                 etag)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                etag=excluded.etag,
                console=excluded.console, name=excluded.name,
                identifier=excluded.identifier,
                path_prefix=excluded.path_prefix, url=excluded.url,
                file_count=excluded.file_count,
                total_size=excluded.total_size,
                last_indexed=excluded.last_indexed,
                last_error=excluded.last_error,
                requires_login=excluded.requires_login,
                console_rank=excluded.console_rank
        """, (source["id"], source["console"], source["name"],
              source["identifier"], source.get("path_prefix"), item_url,
              len(rows), total, now, error, int(requires_login),
              console_rank, etag or None))

        if error is None:
            conn.execute("DELETE FROM files WHERE source_id = ?",
                         (source["id"],))
            conn.executemany("""
                INSERT OR REPLACE INTO files
                    (source_id, console, path, filename, title, title_norm,
                     regions, languages, version, disc, tags, ext, size, url)
                VALUES
                    (:source_id, :console, :path, :filename, :title,
                     :title_norm, :regions, :languages, :version, :disc,
                     :tags, :ext, :size, :url)
            """, rows)


def prune_removed(conn: sqlite3.Connection, config: dict) -> int:
    """Drop what is left of sources the config no longer lists.

    A source is only ever rewritten when it is visited, and one that has been
    renamed or dropped is never visited again - so its files sat in the index
    forever, offered in search results, pointing at a shelf nothing refreshes.

    It took renaming the MiNERVA shelves to notice: the first pass had filed
    them under one set of ids and the second under another, and the database
    kept both. 79,382 stale rows, every one of them a duplicate of a row that
    was still being maintained.

    Judged against the whole config, never against an --only subset, so that
    indexing one shelf cannot delete the other two hundred.
    """
    keep = {s["id"] for s in config["sources"]}
    have = {r[0] for r in conn.execute("SELECT id FROM sources")}
    have |= {r[0] for r in conn.execute("SELECT DISTINCT source_id FROM files")}
    gone = have - keep
    if not gone:
        return 0
    marks = ",".join("?" * len(gone))
    ids = list(gone)
    with conn:
        dropped = conn.execute(
            f"DELETE FROM files WHERE source_id IN ({marks})", ids).rowcount
        conn.execute(f"DELETE FROM sources WHERE id IN ({marks})", ids)
    return dropped


def index_all(conn: sqlite3.Connection, config: dict, *,
              only: list[str] | None = None, workers: int = 4,
              progress=print, counts=None) -> dict:
    """Index every configured source (or just the ones named in `only`).

    `counts(done, total)` is called as sources are finished, so a caller can
    show how far along it is. Sources are the unit rather than archive.org
    items, because several sources often share one item and "12 of 178
    sources" means something to a person in a way "3 of 60 items" doesn't.
    """
    sources = config["sources"]
    if only:
        wanted = {s.lower() for s in only}
        sources = [s for s in sources
                   if s["id"].lower() in wanted
                   or s["console"].lower() in wanted
                   or s["identifier"].lower() in wanted]
        if not sources:
            raise SystemExit(f"no sources matched: {', '.join(only)}")

    extensions = config["extensions"]
    # Ranks come from the full config so they stay stable under --only.
    ranks = console_order(config)
    summary = {"ok": 0, "failed": 0, "files": 0, "login_required": 0,
               "unchanged": 0, "errors": []}

    # What each source looked like at the end of the last run. A shelf that
    # says it has not changed since then is not fetched, not parsed and not
    # written - which for MiNERVA is three megabytes of HTML and a rewrite of
    # eleven thousand rows, replaced by one question answered in half a second.
    #
    # Only trusted where there are still rows to keep: an ETag remembered for
    # a source whose files have since been pruned would skip the one fetch
    # that would have brought them back.
    known: dict[str, str] = {}
    try:
        for row in conn.execute(
                "SELECT s.id, s.etag FROM sources s WHERE s.etag IS NOT NULL "
                "AND EXISTS (SELECT 1 FROM files f WHERE f.source_id = s.id)"):
            known[row[0]] = row[1] or ""
    except Exception:  # noqa: BLE001 - an older database, or none yet
        known = {}

    # Several sources can share one archive.org item (the Saturn CHD folders
    # are all in chd_saturn), so fetch each identifier once and fan it back
    # out. Keyed by kind as well, because an identifier only means something
    # alongside the thing it identifies: "./Redump/Sony - PlayStation/" is a
    # browse path, not an archive.org item.
    by_identifier: dict[tuple[str, str], list[dict]] = {}
    for source in sources:
        key = (source.get("kind") or "archive", source["identifier"])
        by_identifier.setdefault(key, []).append(source)

    progress(f"Indexing {len(sources)} source(s) from "
             f"{len(by_identifier)} item(s) with {workers} workers...\n")

    total = len(sources)
    finished = 0
    if counts:
        counts(0, total)

    # Network fetches run in parallel; database writes stay on this thread.
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        # One ETag per identifier, and only when every source sharing it
        # agrees on the same one - two sources reading different slices of
        # one shelf must not have one of them skipped on the other's word.
        def validator(group):
            tags = {known.get(one["id"], "") for one in group}
            return tags.pop() if len(tags) == 1 else ""

        futures = {
            pool.submit(fetch_source, kind, ident,
                        validator(by_identifier[(kind, ident)])): (kind, ident)
            for kind, ident in by_identifier}

        for done in concurrent.futures.as_completed(futures):
            key = futures[done]
            group = by_identifier[key]
            try:
                metadata = done.result()
            except Unchanged:
                # Checked, and found to be what it already was. The date is
                # still moved on: "last indexed" answers "when did we last
                # make sure", and the answer is now.
                seen = datetime.now(timezone.utc).isoformat(timespec="seconds")
                try:
                    with conn:
                        conn.executemany(
                            "UPDATE sources SET last_indexed = ?, "
                            "last_error = NULL WHERE id = ?",
                            [(seen, one["id"]) for one in group])
                except Exception:  # noqa: BLE001 - a stale date is not a failure
                    pass
                for source in group:
                    summary["ok"] += 1
                    summary["unchanged"] += 1
                    progress(f"  same  {source['console']}  {source['name']}"
                             f"  (unchanged)")
                finished += len(group)
                if counts:
                    counts(finished, total)
                continue
            except Exception as exc:  # noqa: BLE001 - report and keep going
                for source in group:
                    store_source(conn, source, [], error=str(exc))
                    summary["failed"] += 1
                    summary["errors"].append(f"{source['id']}: {exc}")
                    progress(f"  FAIL  {source['console']}  "
                             f"{source['name']}: {exc}")
                finished += len(group)
                if counts:
                    counts(finished, total)
                continue

            login = "minerva" not in metadata and needs_login(metadata)
            for source in group:
                label = f"{source['console']}  {source['name']}"
                rows = extract_files(source, metadata, extensions)
                store_source(conn, source, rows, requires_login=login,
                             console_rank=ranks.get(source["console"], 99),
                             etag=str(metadata.get("etag") or ""))
                summary["ok"] += 1
                summary["files"] += len(rows)
                if login:
                    summary["login_required"] += 1
                warn = "  <- no files matched!" if not rows else ""
                progress(f"  ok    {label}  ({len(rows):,} files)"
                         f"{'  [login required]' if login else ''}{warn}")

            finished += len(group)
            if counts:
                counts(finished, total)

    # An arcade shelf is a list of board names until RetroAchievements is
    # asked what each board is. Done here, once, so a reindex leaves the games
    # findable by the names people know them by. Silent when there is no key
    # or no network - the romsets keep their board names, as before.
    try:
        from . import arcade  # noqa: PLC0415 - optional, and reads retro

        named = arcade.name_files(conn)
        if named:
            progress(f"\nNamed {named:,} arcade romset(s) after "
                     "their games.")
        summary["named"] = named
    except Exception:  # noqa: BLE001 - never fail an index over this
        summary["named"] = 0

    # After the writes, not before: a run that dies halfway should not have
    # thrown anything away on its way in.
    stale = prune_removed(conn, config)
    if stale:
        progress(f"\nDropped {stale:,} file(s) from sources no longer listed.")
    summary["pruned"] = stale

    return summary
