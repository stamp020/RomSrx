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
import json
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

    # Its listing hashes the bytes, so both ends speak the same language and
    # a file that has not changed compares equal. See sync.manifest_of.
    content_hashes = True

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

    # Its listing can only offer an etag - see the note in listing below - so
    # what it says about a file cannot be compared against a hash taken here.
    # sync.manifest_of is where that is dealt with.
    content_hashes = False

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
        # What was typed, which is empty until somebody types something. The
        # page needs both: this for the box, and device.name - the computer's
        # own hostname when this is empty - for the placeholder beside it.
        "deviceName": str(prefs.get("syncDeviceName") or ""),
        "parts": parts,
        "carries": list(sync.CARRIES),
        "defaults": list(sync.DEFAULT_PARTS),
        "sizes": sizes,
        "where": where,
        "auto": bool(prefs.get("syncAuto")),
        # So the panel can show that it is actually happening. "Sync on its
        # own" is a promise with nothing to show for it otherwise, and the
        # whole question somebody has about it is whether it is working.
        "lastAuto": _last_auto_at,
        "lastAutoWhy": _last_auto_word,
        "every": EVERY,
    }


# Only ever one sync at a time. Two would race each other over the same files
# and, worse, each would write a manifest that contradicted the other's.
_running = threading.Lock()

# When the last one finished, so a burst of triggers - open the app, close a
# game, close another - does not become a burst of syncs. A folder on a NAS
# that has just been written to is not usefully re-read four seconds later.
_last_auto = 0.0
QUIET = 60.0

# When the last automatic sync finished, by the wall clock rather than the
# monotonic one above, because this one is shown to somebody.
_last_auto_at = 0.0
_last_auto_word = ""

# How often to look, while the app is open, for what another computer has
# sent. Nothing local needs this - a change here says so the moment it
# happens - it is entirely about the other direction, which has nothing to
# announce itself with. Five minutes is short enough that walking to the
# other machine and finding yesterday's playlists cannot happen, and long
# enough that a NAS is not being asked the same question all afternoon.
EVERY = 300.0


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
        global _last_auto_at, _last_auto_word  # noqa: PLW0603
        _last_auto_at = time.time()
        _last_auto_word = why or ""
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


# -- keeping in step without being asked ----------------------------------
#
# Two triggers were not enough to call this automatic.
#
# Sending only happened when a game closed or the app started, so a playlist
# made and then left alone never went anywhere: you had to play something, or
# restart, before your own change existed anywhere but here. And fetching only
# happened at startup, so the second computer - the one sitting open on the
# desk - never saw anything the first one sent until it was restarted.
#
# So: anything that changes here says so, and something looks the other way
# every few minutes. Both go through one thread that owns the timing, rather
# than each caller starting its own and racing the quiet period.

_wake = threading.Event()
_pending = ""
_pacer: threading.Thread | None = None
_pacer_lock = threading.Lock()


def nudge(why: str = "") -> None:
    """Something here changed. Sync shortly - not this instant.

    Shortly, because changes come in bursts: adding four games to a playlist
    is four writes, and a NAS does not want four syncs. The wait also means
    the caller - a page waiting on its answer - is never held up.
    """
    global _pending  # noqa: PLW0603 - one queue for the whole app
    _pending = why or _pending or "something changed"
    start()
    _wake.set()


def start(why: str = "") -> None:
    """Begin keeping in step on its own. Safe to call more than once."""
    global _pacer  # noqa: PLW0603 - one pacer for the whole app
    with _pacer_lock:
        if _pacer is None or not _pacer.is_alive():
            _pacer = threading.Thread(target=_pace, daemon=True,
                                      name="romsrx-sync")
            _pacer.start()
    if why:
        nudge(why)


def _pace() -> None:
    """Sync when something changed, and every EVERY seconds regardless."""
    global _pending  # noqa: PLW0603 - one queue for the whole app
    while True:
        woken = _wake.wait(EVERY)
        _wake.clear()
        why = (_pending or "something changed") if woken else "time passed"
        _pending = ""

        # Wait out the quiet period rather than being turned away by it.
        #
        # `auto` refuses anything inside a minute of the last sync, which is
        # right for a burst and wrong for the one change that happens to land
        # in that minute: refused, it would be forgotten until the next
        # trigger, which for a playlist somebody then walks away from is
        # never. Waiting means it is late, not lost.
        rest = QUIET - (time.monotonic() - _last_auto)
        if rest > 0:
            time.sleep(rest)
            # Anything that arrived while waiting is covered by this run.
            _wake.clear()
            _pending = ""

        auto(why)


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


def _publish(store, here: dict, who: dict) -> int:
    """Leave this machine's own copy where the others can ask for it by name.

    Beside the shared lane, never merged into it. The shared one answers
    "what is the state of my things"; this answers "what does the laptop
    have", which is a question the merge can only ever destroy the answer to.

    Only what changed since last time: without that, every sync would upload
    the whole selection again under our own name, which on a metered
    connection is the difference between usable and not.
    """
    me = sync.device()
    sent_before = sync.load_sent()
    sending = {}
    put = 0

    for key, one in here.items():
        # Hashed here when the caller has not already: local_files describes
        # the files, it does not read them, and without this every sync would
        # think everything had changed and send the lot.
        want = one.get("hash") or (sync.digest(one["path"]) if "path" in one
                                  else sync.digest_bytes(one["body"]))
        if sent_before.get(key) == want:
            sending[key] = want
            continue
        body = (one["body"] if "body" in one
                else Path(one["path"]).read_bytes())
        store.put(sync.mine_at(key, me["id"]), body)
        sending[key] = want
        put += 1

    # The name, so the other machines can offer "Laptop" rather than a random
    # id. Written every time: it is tiny, and it doubles as when this machine
    # was last heard from.
    store.put(sync.mine_at(sync.WHOAMI, me["id"]),
              json.dumps({"id": me["id"], "name": me["name"],
                          "at": time.time()}, indent=1).encode())
    sync.save_sent(sending)
    return put


def _run(parts=None, dry: bool = False) -> dict:
    store = store_for()
    if store is None:
        raise StoreError("No sync folder or server is set up yet.")
    store.check()

    # Both records beside this one describe one particular store: what was
    # agreed with it, and what has already been published to it. Point the
    # app somewhere else and neither is true any more.
    #
    # The one that bites is sync-sent.json. It is what stops every sync
    # re-uploading this machine's own copy, and against a new and empty store
    # it says the files are already there - so the new place would end up
    # with a device lane missing almost everything, quietly, with no error
    # and nothing in the panel to suggest it.
    #
    # An empty record means this is the first run since the app learned to
    # keep track, not that anything moved; note where we are and leave the
    # rest alone.
    where = store.describe()
    if sync.last_where() and sync.last_where() != where:
        sync.save_seen({})
        sync.save_sent({})
    sync.note_where(where)

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
    # No manifest at all means this machine has never synced with this store.
    todo = sync.plan(here, there, seen, joining=not seen)

    if dry:
        return {"ok": True, "dry": True, "where": store.describe(),
                "push": len(todo["push"]), "pull": len(todo["pull"]),
                "clash": len(todo["clash"]),
                "bytes": sum(here[k]["size"] for k in todo["push"]
                             if k in here)}

    who = sync.device()

    # Published before the merge, and that ordering is the whole point.
    #
    # After it, a machine joining an existing set would fetch the shared
    # answer and then republish *that* as its own copy - so all three lanes
    # would say the same thing and the version this computer actually had
    # would exist nowhere but a local file nobody can reach from the other
    # machines. Which is the thing this lane was added to prevent.
    #
    # Before it, "the laptop's copy" means what the laptop had when it last
    # synced, which is the question somebody is asking when they pick it.
    mine = _publish(store, here, who)

    sent = fetched = kept = 0
    # What was fetched, hashed the way this machine hashes things.
    #
    # Not what the store said about it: on a store that answers with an etag,
    # writing that etag down as our own hash makes the file look changed here
    # on the very next run, and it is pushed straight back up. Harmless, and
    # an upload of everything just pulled, every time, which is not what
    # somebody wants from a sync that runs on its own.
    gained: dict[str, dict] = {}
    for key in todo["push"]:
        one = here[key]
        store.put(key, one["body"] if "body" in one
                  else Path(one["path"]).read_bytes())
        sent += 1
    for key in todo["pull"]:
        # write_local, not a bare write: settings.json has to be merged over
        # what is here rather than replace it. It answers None for anything
        # this machine has no place for; see sync.where_for.
        body = store.get(key)
        if sync.write_local(key, body) is None:
            continue
        gained[key] = {"hash": sync.digest_bytes(body), "size": len(body),
                       "when": there[key].get("when", 0.0)}
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
            body = store.get(key)
            sync.write_local(key, body)
            gained[key] = {"hash": sync.digest_bytes(body), "size": len(body),
                           "when": row["theirs"].get("when", 0.0)}
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

    # What the store holds now, when what it says about a file cannot be
    # compared against a hash taken here. One more PROPFIND, and it is the
    # difference between a WebDAV sync that settles and one that fetches the
    # whole selection again on every run for ever. A folder store needs none
    # of this: it hashes the bytes, so the two sides already compare.
    far = {}
    if not getattr(store, "content_hashes", True) and (todo["push"]
                                                       or todo["clash"]):
        try:
            far = sync.only_parts(store.listing(), parts)
        except StoreError:
            far = {}          # the sync worked; only the shortcut is lost

    # Merged into what was already agreed, rather than replacing it: this run
    # only looked at some of the parts, and writing a manifest of just those
    # would tell the next sync that everything else had been deleted.
    agreed = {**seen,
              **sync.manifest_of({**here, **gained},
                                 theirs={**there, **far})}
    store.put_manifest(sync.write_manifest(agreed))
    sync.save_seen(agreed)

    return {"ok": True, "where": store.describe(), "sent": sent,
            "fetched": fetched, "kept": kept, "mine": mine}


def _sources(store, parts) -> tuple[dict, list[dict]]:
    """The shared lane, and each machine's own copy, told apart.

    One listing, split. Everything under "devices/" belongs to whichever
    machine published it and is never part of a merge; everything else is the
    shared lane. See sync.DEVICES.
    """
    everything = store.listing()
    shared, mine = {}, {}
    for key, about in everything.items():
        whose, inside = sync.under_device(key)
        if whose:
            mine.setdefault(whose, {})[inside] = about
        else:
            shared[key] = about

    me = sync.device()
    rows = []
    for whose, held in mine.items():
        name, when = "", 0.0
        if sync.WHOAMI in held:
            try:
                said = json.loads(store.get(sync.mine_at(
                    sync.WHOAMI, whose)).decode("utf-8"))
                name = str(said.get("name") or "")
                when = float(said.get("at") or 0.0)
            except Exception:  # noqa: BLE001 - a missing name is not an error
                name = ""
            held.pop(sync.WHOAMI, None)
        rows.append({"id": whose, "name": name or whose[:8],
                     "at": when, "ours": whose == me["id"],
                     "files": sync.only_parts(held, parts)})
    rows.sort(key=lambda row: (row["ours"], -row["at"]))
    return sync.only_parts(shared, parts), rows


def _about(there: dict, here: dict, parts) -> list[dict]:
    """One row per part: what is over there, against what is here."""
    out = []
    for part in parts:
        yours = {k: v for k, v in there.items() if sync.part_of(k) == part}
        if not yours:
            continue
        mine = {k: v for k, v in here.items() if sync.part_of(k) == part}
        out.append({
            "part": part,
            "files": len(yours),
            "bytes": sum(int(v.get("size") or 0) for v in yours.values()),
            "when": max((float(v.get("when") or 0.0)
                         for v in yours.values()), default=0.0),
            "hereFiles": len(mine),
            "hereBytes": sum(int(v.get("size") or 0) for v in mine.values()),
            "fresh": sum(1 for k in yours if k not in mine),
        })
    return out


def peek(parts=None) -> dict:
    """Everywhere something could be brought from, and what each one holds.

    Deliberately cheap: sizes, counts and dates, no hashing. Hashing every
    local file is what a sync does, and for the save states that can be a few
    hundred megabytes of reading to answer a question somebody asked out of
    curiosity. Whether a part is worth taking is a judgement made at the level
    of "twelve files from the laptop, an hour ago", not file by file.
    """
    store = store_for()
    if store is None:
        raise StoreError("No sync folder or server is set up yet.")
    store.check()

    parts = [p for p in (parts or sync.CARRIES) if p in sync.CARRIES]
    shared, machines = _sources(store, parts)
    here = sync.local_files(parts)

    meta = sync.manifest_meta(store.get_manifest())
    sources = [{
        "id": "", "name": "", "shared": True,
        "at": meta.get("at") or 0.0,
        "by": meta.get("byName") or "",
        "ours": bool(meta.get("by")) and meta.get("by") == sync.device()["id"],
        "parts": _about(shared, here, parts),
    }]
    for row in machines:
        sources.append({
            "id": row["id"], "name": row["name"], "shared": False,
            "at": row["at"], "by": row["name"], "ours": row["ours"],
            "parts": _about(row["files"], here, parts),
        })

    # Somewhere with nothing in it is not somewhere to bring anything from.
    sources = [one for one in sources if one["parts"]]
    return {"ok": True, "where": store.describe(), "sources": sources}


def pull(parts, source: str = "") -> dict:
    """Bring these parts down from one place, whatever is here already.

    A sync is a negotiation - it weighs which side changed and can decide the
    answer is "yours". This does not negotiate. Somebody has looked at what is
    there and said they want it on this machine, and the only useful thing to
    do with that is to do it.

    `source` is "" for the shared lane, or a machine's id for its own copy.
    What is here is not thrown away: anything about to be written over is
    copied beside itself first, under the same `from-` name a conflict uses.
    """
    parts = [p for p in (parts or ()) if p in sync.CARRIES]
    if not parts:
        raise StoreError("Nothing was chosen to bring over.")

    store = store_for()
    if store is None:
        raise StoreError("No sync folder or server is set up yet.")

    if not _running.acquire(timeout=120):
        raise StoreError("Another sync is still running.")
    try:
        store.check()
        shared, machines = _sources(store, parts)
        if source:
            found = [row for row in machines if row["id"] == source]
            if not found:
                raise StoreError(
                    "That computer has not put anything there yet.")
            there = found[0]["files"]
        else:
            there = shared

        who = sync.device()
        fetched = kept = skipped = 0
        agreed = {}

        for key in sorted(there):
            spot = sync.where_for(key)
            if spot is None:
                skipped += 1      # nowhere here to put it; see sync.where_for
                continue
            # Where it is read from depends on the lane; where it lands does
            # not - a file from the laptop's copy goes exactly where the same
            # file from the shared lane would.
            far = sync.mine_at(key, source) if source else key
            if spot.is_file() and sync.digest(spot) == there[key].get("hash"):
                continue                          # already exactly this file
            body = store.get(far)
            if spot.is_file():
                shutil.copy2(spot, spot.with_name(Path(sync.kept_name(
                    spot.name, who["name"], spot.stat().st_mtime)).name))
                kept += 1
            if sync.write_local(key, body) is None:
                skipped += 1
                continue
            agreed[key] = {"hash": sync.digest_bytes(body), "size": len(body),
                           "when": there[key].get("when", 0.0)}
            fetched += 1

        # Only the shared lane is something the next sync compares against.
        # Taking the laptop's copy says nothing about what the shared lane
        # holds, and writing it down as though it did would have the next
        # sync push the laptop's files up as this machine's own.
        if not source:
            sync.save_seen({**sync.load_seen(),
                            **sync.manifest_of(agreed, theirs=there)})

        # Counts as a sync for the quiet period. Somebody who pulls and then
        # closes a game should not have an automatic sync start on top of the
        # files they have just brought down.
        global _last_auto  # noqa: PLW0603 - one clock for the whole app
        _last_auto = time.monotonic()

        return {"ok": True, "where": store.describe(), "fetched": fetched,
                "kept": kept, "skipped": skipped, "parts": parts,
                "source": source}
    finally:
        _running.release()
