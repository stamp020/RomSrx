"""Fetch file listings from the archive.org metadata API into the database."""

from __future__ import annotations

import concurrent.futures
import gzip
import json
import sqlite3
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from . import names
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

# However long a server asks to be left alone, it is not worth more than this:
# the whole index is queued behind one source, and a request to wait an hour
# is better answered by giving up on that source and reporting it.
RETRY_WAIT_CAP = 60

# The codes worth trying again. These mean busy, or briefly broken. Everything
# else the server might say - not found, gone, forbidden - it will say just as
# firmly the second and third time, and asking again only makes an index that
# is already struggling slower.
RETRY_CODES = frozenset({408, 425, 429, 500, 502, 503, 504})


def _retry_wait(exc: Exception, attempt: int) -> float:
    """How long to wait before asking again.

    A server that says how long to wait is believed, within reason - honouring
    it is the difference between easing off and making the throttling worse by
    hammering through it. Only the plain "wait this many seconds" form is read;
    the date form is rare here and the fallback covers it.
    """
    if isinstance(exc, urllib.error.HTTPError):
        asked = (exc.headers.get("Retry-After") or "").strip()
        if asked.isdigit():
            return min(int(asked), RETRY_WAIT_CAP)
    return min(2 ** attempt * 2, RETRY_WAIT_CAP)


def fetch_metadata(identifier: str, *, retries: int = 3,
                   timeout: int = TIMEOUT) -> dict:
    """GET the item metadata, retrying with backoff on transient failures."""
    url = METADATA_URL.format(urllib.parse.quote(identifier))
    request = urllib.request.Request(url, headers={
        "User-Agent": USER_AGENT,
        "Accept-Encoding": "gzip",
    })
    last_error: Exception | None = None

    for attempt in range(retries):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                raw = response.read()
                if response.headers.get("Content-Encoding") == "gzip":
                    raw = gzip.decompress(raw)
                return json.loads(raw.decode("utf-8", "replace"))
        # Before URLError, which it is a kind of: a server that answered
        # deserves a different decision from one that never did.
        except urllib.error.HTTPError as exc:
            last_error = exc
            if exc.code not in RETRY_CODES:
                break
            if attempt < retries - 1:
                time.sleep(_retry_wait(exc, attempt))
        except (urllib.error.URLError, TimeoutError, OSError,
                json.JSONDecodeError) as exc:
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


def extract_files(source: dict, metadata: dict, extensions: set[str]) -> list[dict]:
    """Turn a metadata payload into parsed file rows for one source."""
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
                 console_rank: int = 0) -> None:
    """Replace all indexed files for one source inside a single transaction."""
    total = sum(r["size"] for r in rows)
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    item_url = f"https://archive.org/download/{source['identifier']}"
    if source.get("path_prefix"):
        item_url += "/" + source["path_prefix"].strip("/")

    with conn:
        conn.execute("""
            INSERT INTO sources (id, console, name, identifier, path_prefix,
                                 url, file_count, total_size, last_indexed,
                                 last_error, requires_login, console_rank)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
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
              console_rank))

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
               "errors": []}

    # Several sources can share one archive.org item (the Saturn CHD folders
    # are all in chd_saturn), so fetch each identifier once and fan it back out.
    by_identifier: dict[str, list[dict]] = {}
    for source in sources:
        by_identifier.setdefault(source["identifier"], []).append(source)

    progress(f"Indexing {len(sources)} source(s) from "
             f"{len(by_identifier)} item(s) with {workers} workers...\n")

    total = len(sources)
    finished = 0
    if counts:
        counts(0, total)

    # Network fetches run in parallel; database writes stay on this thread.
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(fetch_metadata, ident): ident
                   for ident in by_identifier}

        for done in concurrent.futures.as_completed(futures):
            identifier = futures[done]
            group = by_identifier[identifier]
            try:
                metadata = done.result()
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

            login = needs_login(metadata)
            for source in group:
                label = f"{source['console']}  {source['name']}"
                rows = extract_files(source, metadata, extensions)
                store_source(conn, source, rows, requires_login=login,
                             console_rank=ranks.get(source["console"], 99))
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

    return summary
