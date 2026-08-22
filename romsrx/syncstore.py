"""The two places a sync can keep its files, behind one small interface.

Both answer the same four questions - what is there, give me this, take this,
and here is the manifest - so sync.py never learns which it is talking to.

**A folder.** The user points at a directory their own cloud client keeps in
step: OneDrive, Google Drive, Dropbox, iCloud. The client does the carrying;
this only reads and writes. It is almost no code, needs no account, no API
key and no review by anybody, and it covers every provider at once. It is
also the only one that works for the big three, none of which speak the
protocol below.

**WebDAV.** A folder over HTTP: the ordinary GET and PUT, plus PROPFIND to
list a directory and MKCOL to make one. No OAuth and nothing to register - the
user pastes a URL, a username and an app password. This is what reaches
Nextcloud, a NAS, Koofr and Box, which is to say the people who do not have a
desktop sync client running.

Neither stores a RomSrx account, because there is no RomSrx account. See
sync.py.
"""

from __future__ import annotations

import base64
import os
import shutil
import threading
import time
import urllib.parse
import xml.etree.ElementTree as ET
from pathlib import Path

from . import sync


class StoreError(Exception):
    """Something went wrong that is worth putting in front of the user."""


class FolderStore:
    """A directory on this machine, which something else keeps in step."""

    kind = "folder"

    def __init__(self, where: str):
        base = str(where or "").strip()
        if not base:
            raise StoreError("No sync folder is set.")
        self.root = Path(base) / sync.ROOT

    def describe(self) -> str:
        return str(self.root)

    def check(self) -> dict:
        try:
            self.root.mkdir(parents=True, exist_ok=True)
            probe = self.root / ".romsrx-write-test"
            probe.write_text("ok", encoding="utf-8")
            probe.unlink(missing_ok=True)
        except OSError as exc:
            raise StoreError(f"Cannot write there: {exc}") from exc
        return {"ok": True, "where": str(self.root)}

    def listing(self) -> dict[str, dict]:
        out: dict[str, dict] = {}
        if not self.root.is_dir():
            return out
        for spot in self.root.rglob("*"):
            if not spot.is_file():
                continue
            key = spot.relative_to(self.root).as_posix()
            if key == sync.MANIFEST:
                continue
            try:
                out[key] = {"size": spot.stat().st_size,
                            "when": spot.stat().st_mtime,
                            "hash": sync.digest(spot)}
            except OSError:
                continue
        return out

    def get(self, key: str) -> bytes:
        try:
            return (self.root / key).read_bytes()
        except OSError as exc:
            raise StoreError(f"Could not read {key}: {exc}") from exc

    def put(self, key: str, body: bytes) -> None:
        spot = self.root / key
        try:
            spot.parent.mkdir(parents=True, exist_ok=True)
            # Written beside and renamed, so a client watching the folder
            # never uploads a file that is still being written.
            temp = spot.with_name(spot.name + ".part")
            temp.write_bytes(body)
            os.replace(temp, spot)
        except OSError as exc:
            raise StoreError(f"Could not write {key}: {exc}") from exc

    def get_manifest(self) -> bytes | None:
        spot = self.root / sync.MANIFEST
        try:
            return spot.read_bytes() if spot.is_file() else None
        except OSError:
            return None

    def put_manifest(self, body: bytes) -> None:
        self.put(sync.MANIFEST, body)


class WebDavStore:
    """A folder on somebody's own server, reached over HTTP."""

    kind = "webdav"

    def __init__(self, url: str, user: str = "", password: str = ""):
        base = str(url or "").strip()
        if not base:
            raise StoreError("No WebDAV address is set.")
        if not base.lower().startswith(("http://", "https://")):
            base = "https://" + base
        self.base = base.rstrip("/") + "/" + sync.ROOT + "/"
        self.user, self.password = user or "", password or ""

    def describe(self) -> str:
        return self.base

    # -- the plumbing --------------------------------------------------------

    def _headers(self, extra: dict | None = None) -> dict:
        head = {"User-Agent": "RomSrx/1.0"}
        if self.user or self.password:
            raw = f"{self.user}:{self.password}".encode()
            head["Authorization"] = "Basic " + base64.b64encode(raw).decode()
        head.update(extra or {})
        return head

    def _url(self, key: str = "") -> str:
        # Each segment quoted on its own, so the slashes that separate them
        # survive and the spaces and brackets in a ROM's name do not.
        path = "/".join(urllib.parse.quote(part, safe="")
                        for part in key.split("/") if part)
        return self.base + path

    def _send(self, method: str, key: str = "", body: bytes | None = None,
              extra: dict | None = None, expect=(200, 201, 204, 207)):
        import requests  # noqa: PLC0415 - the app's own dependency

        try:
            resp = requests.request(method, self._url(key), data=body,
                                    headers=self._headers(extra), timeout=60,
                                    allow_redirects=True)
        except Exception as exc:  # noqa: BLE001
            raise StoreError(
                f"{type(exc).__name__} talking to the server") from exc
        if resp.status_code in (401, 403):
            raise StoreError("The server refused that username or password.")
        if resp.status_code == 404 and method in ("GET", "PROPFIND"):
            return None
        if resp.status_code not in expect:
            raise StoreError(f"The server answered {resp.status_code} to "
                             f"{method}.")
        return resp

    def _mkcol(self, key: str) -> None:
        """Make a directory, and its parents, ignoring the ones that exist.

        WebDAV has no "create the whole path" - MKCOL fails if the parent is
        missing - so the path is walked from the top. 405 means it is already
        there, which is the usual answer and not a problem.
        """
        parts = [p for p in key.split("/") if p][:-1]
        walked = ""
        for part in parts:
            walked = f"{walked}/{part}" if walked else part
            self._send("MKCOL", walked, expect=(201, 405, 301, 200, 204))

    # -- what sync.py asks for ----------------------------------------------

    def check(self) -> dict:
        self._send("MKCOL", "", expect=(201, 405, 301, 200, 204))
        found = self._send("PROPFIND", "", extra={"Depth": "0"})
        if found is None:
            raise StoreError("That folder is not there and could not be made.")
        return {"ok": True, "where": self.base}

    def listing(self) -> dict[str, dict]:
        resp = self._send("PROPFIND", "", extra={"Depth": "infinity"})
        if resp is None:
            return {}
        try:
            tree = ET.fromstring(resp.content)
        except ET.ParseError as exc:
            raise StoreError(
                "The server's directory listing made no sense.") from exc

        here = urllib.parse.urlparse(self.base).path
        out: dict[str, dict] = {}
        ns = "{DAV:}"
        for node in tree.findall(f"{ns}response"):
            href = (node.findtext(f"{ns}href") or "").strip()
            if not href:
                continue
            path = urllib.parse.unquote(urllib.parse.urlparse(href).path)
            if not path.startswith(here):
                continue
            key = path[len(here):].strip("/")
            if not key or key == sync.MANIFEST:
                continue
            props = node.find(f"{ns}propstat/{ns}prop")
            if props is None:
                continue
            if props.find(f"{ns}resourcetype/{ns}collection") is not None:
                continue                                   # a directory
            try:
                size = int(props.findtext(f"{ns}getcontentlength") or 0)
            except ValueError:
                size = 0
            # No hash from the server, and asking for one would mean fetching
            # every file. The etag stands in: it changes when the content
            # does, which is all `plan` compares it for.
            tag = (props.findtext(f"{ns}getetag") or "").strip('"')
            out[key] = {"size": size, "when": 0.0,
                        "hash": tag or f"size:{size}"}
        return out

    def get(self, key: str) -> bytes:
        resp = self._send("GET", key, expect=(200, 206))
        if resp is None:
            raise StoreError(f"{key} is not on the server.")
        return resp.content

    def put(self, key: str, body: bytes) -> None:
        try:
            self._send("PUT", key, body=body, expect=(200, 201, 204))
        except StoreError:
            # Almost always a missing parent directory, which WebDAV will not
            # make for you. Build the path and try once more.
            self._mkcol(key)
            self._send("PUT", key, body=body, expect=(200, 201, 204))

    def get_manifest(self) -> bytes | None:
        try:
            resp = self._send("GET", sync.MANIFEST, expect=(200,))
        except StoreError:
            return None
        return resp.content if resp is not None else None

    def put_manifest(self, body: bytes) -> None:
        self.put(sync.MANIFEST, body)


def store_for(prefs: dict | None = None):
    """Whichever one the user has set up, or None if neither."""
    from . import state  # noqa: PLC0415

    prefs = state.prefs() if prefs is None else prefs
    kind = str(prefs.get("syncKind") or "").strip()
    if kind == "folder":
        return FolderStore(str(prefs.get("syncFolder") or ""))
    if kind == "webdav":
        return WebDavStore(str(prefs.get("syncDavUrl") or ""),
                           str(prefs.get("syncDavUser") or ""),
                           str(prefs.get("syncDavPass") or ""))
    return None


def status(prefs: dict | None = None) -> dict:
    """Everything the settings panel needs, without touching the network.

    Sizes are measured rather than guessed at, because "sync my saves" means
    something very different at 74 MB and at 440 MB, and the difference is
    entirely whether save states are ticked. Somebody choosing should be
    looking at the number.
    """
    from . import state  # noqa: PLC0415

    prefs = state.prefs() if prefs is None else prefs
    chosen = prefs.get("syncParts")
    parts = (list(chosen) if isinstance(chosen, list)
             else list(sync.DEFAULT_PARTS))

    sizes = {}
    for part in sync.CARRIES:
        try:
            found = sync.local_files([part])
        except Exception:  # noqa: BLE001 - a size is not worth an error
            found = {}
        sizes[part] = {"files": len(found),
                       "bytes": sum(f.get("size", 0) for f in found.values())}

    where = ""
    try:
        store = store_for(prefs)
        where = store.describe() if store else ""
    except StoreError:
        where = ""
    return {
        "kind": str(prefs.get("syncKind") or ""),
        "folder": str(prefs.get("syncFolder") or ""),
        "davUrl": str(prefs.get("syncDavUrl") or ""),
        "davUser": str(prefs.get("syncDavUser") or ""),
        # Never sent back to the page. It is only ever written.
        "davPassSet": bool(prefs.get("syncDavPass")),
        "device": sync.device(),
        "parts": parts,
        "carries": list(sync.CARRIES),
        "defaults": list(sync.DEFAULT_PARTS),
        "sizes": sizes,
        "where": where,
        "auto": bool(prefs.get("syncAuto")),
    }


# Only ever one sync at a time. Two would race each other over the same files
# and, worse, each would write a manifest that contradicted the other's.
_running = threading.Lock()

# When the last one finished, so a burst of triggers - open the app, close a
# game, close another - does not become a burst of syncs. A folder on a NAS
# that has just been written to is not usefully re-read four seconds later.
_last_auto = 0.0
QUIET = 60.0


def auto(why: str = "") -> dict:
    """Sync, if the user asked for that to happen on its own. Never raises.

    Called at the two moments when there is plausibly something new: the app
    opening, and a game closing - which is when a save is final and when
    history.take has just written one down. Closing the app is deliberately
    not one of them: it would either delay the window going away or be killed
    half-done, and neither is worth it when the game closing already covered
    the case.
    """
    from . import state  # noqa: PLC0415

    if not state.prefs().get("syncAuto"):
        return {"ok": False, "why": "not asked for"}
    if store_for() is None:
        return {"ok": False, "why": "nothing set up"}

    global _last_auto  # noqa: PLW0603 - one clock for the whole app
    if time.monotonic() - _last_auto < QUIET:
        return {"ok": False, "why": "too soon after the last one"}
    if not _running.acquire(blocking=False):
        return {"ok": False, "why": "one is already running"}
    try:
        _last_auto = time.monotonic()
        chosen = state.prefs().get("syncParts")
        # `_run`, not `run`: this already holds the lock, and a plain Lock is
        # not reentrant - taking it twice on one thread waits two minutes for
        # itself and then gives up. Caught by the test that starts two.
        found = _run(parts=chosen if isinstance(chosen, list) else None)
        found["auto"] = why or True
        return found
    except Exception as exc:  # noqa: BLE001 - a sync nobody asked to watch
        return {"ok": False, "why": f"{type(exc).__name__}: {exc}"}
    finally:
        _running.release()


def auto_later(why: str = "") -> None:
    """The same thing, off the caller's thread.

    Everything that triggers this is something the user is waiting on - the
    app opening, a game closing - and none of it should wait for a folder on
    a NAS that may be asleep.
    """
    threading.Thread(target=auto, args=(why,), daemon=True).start()


# Kept out of the classes because it is the same for both: what a sync
# actually does, once there is somewhere to do it.
def run(parts=None, dry: bool = False) -> dict:
    """Bring this machine and the store into step. Answers what it did.

    A dry run only reads, so it never waits; a real one takes the same lock
    the automatic syncs use, because two writing at once would race over the
    files and leave contradictory manifests behind them.
    """
    if not dry:
        if not _running.acquire(timeout=120):
            raise StoreError("Another sync is still running.")
        try:
            return _run(parts, dry)
        finally:
            _running.release()
    return _run(parts, dry)


def _run(parts=None, dry: bool = False) -> dict:
    store = store_for()
    if store is None:
        raise StoreError("No sync folder or server is set up yet.")
    store.check()

    parts = list(parts or sync.DEFAULT_PARTS)
    here = sync.local_files(parts)
    for one in here.values():
        one["hash"] = (sync.digest(one["path"]) if "path" in one
                       else sync.digest_bytes(one["body"]))
    # Narrowed to the parts being synced. The store holds whatever every
    # machine has ever put there, and anything outside this sync's parts is
    # none of its business - see sync.part_of.
    there = sync.only_parts(store.listing(), parts)
    seen = sync.load_seen()
    todo = sync.plan(here, there, seen)

    if dry:
        return {"ok": True, "dry": True, "where": store.describe(),
                "push": len(todo["push"]), "pull": len(todo["pull"]),
                "clash": len(todo["clash"]),
                "bytes": sum(here[k]["size"] for k in todo["push"]
                             if k in here)}

    who = sync.device()
    sent = fetched = kept = 0
    for key in todo["push"]:
        one = here[key]
        store.put(key, one["body"] if "body" in one
                  else Path(one["path"]).read_bytes())
        sent += 1
    for key in todo["pull"]:
        spot = sync.where_for(key)
        if spot is None:
            continue          # not a place this machine has; see where_for
        spot.parent.mkdir(parents=True, exist_ok=True)
        spot.write_bytes(store.get(key))
        fetched += 1

    for row in todo["clash"]:
        key = row["key"]
        spot = sync.where_for(key)
        if spot is None:
            continue
        if row["take"] == "theirs":
            # Keep ours beside it before it is written over.
            if spot.is_file():
                shutil.copy2(spot, spot.with_name(
                    Path(sync.kept_name(spot.name, who["name"],
                                        row["mine"].get("when", 0))).name))
                kept += 1
            spot.parent.mkdir(parents=True, exist_ok=True)
            spot.write_bytes(store.get(key))
            fetched += 1
        else:
            # Ours wins; put theirs aside on the store rather than dropping it.
            store.put(sync.kept_name(key, "other",
                                     row["theirs"].get("when", 0)),
                      store.get(key))
            store.put(key, Path(here[key]["path"]).read_bytes()
                      if "path" in here[key] else here[key]["body"])
            sent += 1
            kept += 1

    # Merged into what was already agreed, rather than replacing it: this run
    # only looked at some of the parts, and writing a manifest of just those
    # would tell the next sync that everything else had been deleted.
    agreed = {**seen,
              **sync.manifest_of({**here,
                                  **{k: there[k] for k in todo["pull"]
                                     if k in there}})}
    store.put_manifest(sync.write_manifest(agreed))
    sync.save_seen(agreed)
    return {"ok": True, "where": store.describe(), "sent": sent,
            "fetched": fetched, "kept": kept}
