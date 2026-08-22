"""Carrying your settings and saves between the computers you play on.

The wish behind this is "log in and have my stuff", and the way it is *not*
done matters more than the way it is.

There is no RomSrx account, and there will not be one. An account means a
server somebody pays for, passwords somebody has to keep safe, other people's
save files sitting on infrastructure with the app author's name on it, and a
deletion request queue. None of that makes the feature better; all of it
scales with how many people like the app.

So the account is one the user already has. They point this at a folder their
own cloud client keeps in step - OneDrive, Drive, Dropbox, iCloud - or at
their own WebDAV server, and RomSrx reads and writes there like any other
folder. The app stores nothing, costs nothing to run, and their saves stay
theirs.

What travels, and what must not
-------------------------------

The parts are the ones the backup already knows - see state.BACKUP_PARTS - because
"what is worth carrying" is the same question a backup asks and it has been
answered once already.

The one part that must never travel is `paths`, and `state.SETTINGS_PATH_KEYS`
already draws that line: two computers keep their games on different drives,
and a synced `folder` setting would point the second machine at a directory
that does not exist on it. Preferences travel; places do not.

Saves travel per *file*, not per part. Two machines that played different
games have both sets of changes and neither is a conflict, which is only true
if the unit is one memory card rather than "the saves".

When two machines disagree
--------------------------

Somebody plays on the desktop, plays the same game on the laptop, and now two
memory cards claim to be the current one. There is no clever answer to that -
whichever is kept, the other is lost work - so the rule is the plain one:

  * A file changed on one side only is copied to the other.
  * A file changed on both is a conflict. The newer one wins, and the older
    one is *kept*, written beside it as `<name>.from-<device>-<when>`.

Nothing is thrown away silently. For emulator saves the history in history.py
is a second net underneath this one, since a save that gets overwritten was
snapshotted when its session ended.

Clocks
------

Two computers do not agree on the time, and a save written at 21:04 on a
laptop whose clock is four minutes slow would look older than one written at
21:01 on the desktop. So *when* is only used to break a tie between two files
that have both genuinely changed, and *whether* something changed is decided
by content - a hash of the bytes - which no clock can get wrong.
"""

from __future__ import annotations

import hashlib
import json
import os
import platform
import time
import uuid
from pathlib import Path

from . import state
from .paths import user

# What the remote folder is called, wherever it is, and what is in it.
ROOT = "RomSrx"

# The store holds two lanes, and the difference between them is the whole of
# how two computers get along.
#
# The shared lane - "app/...", "saves/..." - is one copy of each file, merged,
# and it is what keeping in step on its own works with. It answers "what is
# the current state of my things", and by its nature it can only hold one
# answer: two machines writing a playlist both write the same name, and the
# newer wins.
#
# That is right for staying in step and wrong for everything else. It means
# the other computer's version is not anywhere you can ask for it - it lost,
# and losing is invisible. So each machine also publishes its own copy under
# its own id, untouched by anyone else, and those are what "bring from the
# cloud" offers by name: this computer's, the laptop's, the one at work's.
#
# Nothing under here ever takes part in a merge. part_of answers "" for these
# keys and where_for refuses them, so the shared sync cannot see them even by
# accident - which is what stops three machines' copies from being folded
# into one another.
DEVICES = "devices"

# What a machine writes beside its copy, so the others can show a name rather
# than a random id.
WHOAMI = "who.json"
MANIFEST = "manifest.json"

# Parts that may be carried. Deliberately a subset of state.PARTS:
#
#   `paths`  - where this machine keeps things. See the module docstring.
#   `index`  - the archive.org catalogue, hundreds of megabytes, and rebuilt
#              from nothing by pressing Reindex. Syncing it would fill a free
#              tier to carry something neither machine needs to be told.
CARRIES = ("settings", "cart", "queue", "playlists", "recent", "times",
           "covers", "saves", "states", "history")

# ...and what each is, when it is not simply the part of the same name in
# state.BACKUP_PARTS. These three are gathered rather than copied from a known path.
GATHERED = {"saves", "states", "history"}

# What a fresh install syncs unless told otherwise. Everything that makes the
# app feel like yours, plus the saves that cannot be downloaded again - and
# not the save states, which on one real machine were 366 MB against 74 MB for
# every memory card on it, and which are the least worth carrying.
DEFAULT_PARTS = ("settings", "cart", "queue", "playlists", "recent", "times",
                 "covers", "saves", "history")

_CHUNK = 1024 * 1024


def device() -> dict:
    """This computer, as the other ones will see it named.

    The id is random and kept in the app's own settings: a hostname is not
    unique enough to trust - two machines called DESKTOP-PC would each think
    the other's writes were their own - and not stable enough either, since
    renaming a computer must not orphan everything it has already written.
    """
    prefs = state.prefs()
    ident = str(prefs.get("syncDeviceId") or "")
    if not ident:
        ident = uuid.uuid4().hex[:12]
        state.set_prefs({"syncDeviceId": ident})
    name = str(prefs.get("syncDeviceName") or "").strip()
    if not name:
        try:
            name = platform.node() or "this computer"
        except Exception:  # noqa: BLE001 - a name is a nicety
            name = "this computer"
    return {"id": ident, "name": name}


def digest(path: Path) -> str:
    """What is in this file, as something two computers can compare.

    Content rather than a timestamp, because clocks disagree and a file copied
    by a sync client arrives with whatever time that client felt like giving
    it. Truncated to sixteen bytes: this is telling two versions of a memory
    card apart, not resisting an adversary.
    """
    hasher = hashlib.blake2b(digest_size=16)
    try:
        with open(path, "rb") as fh:
            while True:
                block = fh.read(_CHUNK)
                if not block:
                    break
                hasher.update(block)
    except OSError:
        return ""
    return hasher.hexdigest()


def digest_bytes(body: bytes) -> str:
    """The same thing for something already in hand rather than on disk."""
    return hashlib.blake2b(body or b"", digest_size=16).hexdigest()


def _stamp(path: Path) -> float:
    try:
        return float(path.stat().st_mtime)
    except OSError:
        return 0.0


def local_files(parts) -> dict[str, dict]:
    """Everything on this machine that these parts cover, by its remote name.

    The key is the path the file will have on the other side, so both ends
    speak the same names and neither has to know where the other keeps things.
    """
    wanted = set(parts or ())
    out: dict[str, dict] = {}

    root = user()
    plain, folders = state.backup_contents(
        [p for p in wanted if p not in GATHERED] or None)
    if not wanted - GATHERED:
        plain, folders = [], []

    for name in plain:
        spot = root / name
        if not spot.is_file():
            continue
        if name == state.PREFS_FILE:
            # Sliced rather than copied, for the same reason settings.json is:
            # part of it names this machine. See state.is_local_pref.
            body = _prefs_slice(spot)
            if body is not None:
                out[f"app/{name}"] = {"body": body, "size": len(body),
                                      "when": _stamp(spot)}
            continue
        out[f"app/{name}"] = {"path": spot, "size": spot.stat().st_size,
                              "when": _stamp(spot)}
    for name in folders:
        base = root / name
        if not base.is_dir():
            continue
        for spot in base.rglob("*"):
            if spot.is_file():
                key = f"app/{name}/{spot.relative_to(base).as_posix()}"
                out[key] = {"path": spot, "size": spot.stat().st_size,
                            "when": _stamp(spot)}

    # settings.json is written a key at a time, because half of it is
    # preferences that travel and half is paths that must not. The slice is
    # produced as bytes rather than pointed at, so `path` is absent and the
    # caller reads `body` instead.
    if "settings" in wanted:
        slice_ = state._settings_slice(root, ["settings"])  # noqa: SLF001
        if slice_:
            body = json.dumps(slice_, indent=1).encode("utf-8")
            out[f"app/{state.SETTINGS_FILE}"] = {
                "body": body, "size": len(body),
                "when": _stamp(root / state.SETTINGS_FILE)}

    if wanted & GATHERED:
        out.update(_gathered(wanted))
    return out


def _prefs_slice(spot: Path) -> bytes | None:
    """prefs.json with the settings belonging to this computer taken out."""
    try:
        with open(spot, encoding="utf-8") as fh:
            data = json.load(fh)
        if not isinstance(data, dict):
            return None
    except (OSError, ValueError):
        return None
    keep = {k: v for k, v in data.items() if not state.is_local_pref(k)}
    return json.dumps(keep, indent=1).encode("utf-8")


def _merged_prefs(spot: Path, incoming: bytes) -> bytes:
    """The other machine's preferences over ours, ours kept where they are
    about this computer.

    The mirror of _prefs_slice: the sender leaves its own out, and the
    receiver keeps its own regardless - because a store written by an older
    version of the app still has them in it.
    """
    try:
        fresh = json.loads(incoming.decode("utf-8"))
        if not isinstance(fresh, dict):
            return incoming
    except (UnicodeDecodeError, ValueError):
        return incoming
    try:
        with open(spot, encoding="utf-8") as fh:
            current = json.load(fh)
        if not isinstance(current, dict):
            current = {}
    except (OSError, ValueError):
        current = {}
    current.update({k: v for k, v in fresh.items()
                    if not state.is_local_pref(k)})
    return json.dumps(current, indent=1).encode("utf-8")


def _gathered(wanted: set) -> dict[str, dict]:
    """The emulators' own folders, and the session history beside them."""
    from . import history, saves  # noqa: PLC0415 - both import downloads

    out: dict[str, dict] = {}
    if {"saves", "states"} & wanted:
        try:
            folders = saves.folders()
        except Exception:  # noqa: BLE001 - a sync without saves is a sync
            folders = []
        for folder in folders:
            # A save state is a different kind of thing from a memory card:
            # far larger, and worth carrying only if somebody says so.
            kind = str(folder.get("kind") or "").lower()
            part = "states" if "state" in kind else "saves"
            if part not in wanted:
                continue
            base = Path(folder["path"])
            label = folder.get("label") or "saves"
            if not base.is_dir():
                continue
            for spot in base.rglob("*"):
                if spot.is_file():
                    key = (f"{part}/{label}/"
                           f"{spot.relative_to(base).as_posix()}")
                    out[key] = {"path": spot, "size": spot.stat().st_size,
                                "when": _stamp(spot)}

    if "history" in wanted:
        base = history.where()
        if base.is_dir():
            for spot in base.rglob("*"):
                if not spot.is_file():
                    continue
                inside = spot.relative_to(base).as_posix()
                # The notes, the pins and the game names travel: they are
                # about the session, and a session that arrives without the
                # line somebody wrote on it has lost the part that made it
                # findable. Only this one does not - it is what happened the
                # last time a game was closed *on this computer*, and carrying
                # it would have each machine reporting the other's last
                # session as its own.
                if inside == history.SESSION_FILE:
                    continue
                out[f"history/{inside}"] = {"path": spot,
                                            "size": spot.stat().st_size,
                                            "when": _stamp(spot)}
    return out


def where_for(key: str) -> Path | None:
    """Where a file with this remote name belongs on this machine.

    The reverse of the naming in `local_files`, and the only place that knows
    both. Answers None for anything it does not recognise, so a remote folder
    that has picked up junk - or a newer version of this app writing a part
    this one has never heard of - cannot write outside the places listed here.
    """
    parts = key.split("/")
    if len(parts) < 2 or ".." in parts:
        return None
    head, rest = parts[0], parts[1:]

    if head == "app":
        return user(*rest)
    if head == "history":
        from . import history  # noqa: PLC0415

        return history.where().joinpath(*rest)
    if head in ("saves", "states") and len(rest) >= 2:
        from . import saves  # noqa: PLC0415

        label, inside = rest[0], rest[1:]
        for folder in saves.folders():
            if (folder.get("label") or "") == label:
                return Path(folder["path"]).joinpath(*inside)
        return None        # that emulator is not set up on this machine
    return None


def write_local(key: str, body: bytes) -> Path | None:
    """Put a fetched file where it belongs, or None if this machine has no
    such place.

    Every path that brings a file down goes through here, because one of them
    cannot simply be written: settings.json arrives as a slice with the paths
    taken out of it - that is the point of the slice - and writing that slice
    over the local file does not merely fail to carry the paths, it deletes
    the ones already there. A machine that synced its preferences lost the
    folder its games are in.

    The same merge the backup restore uses is the right one here: the
    incoming keys laid over what is already on disk, so a preference travels
    and a path stays put.
    """
    spot = where_for(key)
    if spot is None:
        return None
    spot.parent.mkdir(parents=True, exist_ok=True)
    if key == f"app/{state.SETTINGS_FILE}":
        body = state._merged_settings(spot, body)  # noqa: SLF001
    elif key == f"app/{state.PREFS_FILE}":
        body = _merged_prefs(spot, body)
    spot.write_bytes(body)
    return spot


def mine_at(key: str, who: str) -> str:
    """Where this machine's own copy of a shared-lane name lives."""
    return f"{DEVICES}/{who}/{key}"


def under_device(key: str) -> tuple[str, str]:
    """(whose it is, what it is called in the shared lane), or ("", "").

    The reverse of mine_at, and the only thing that turns one of those keys
    back into somewhere on this machine - by way of where_for, which still
    gets the final say about whether the name is one it recognises.
    """
    bits = key.split("/")
    if len(bits) < 3 or bits[0] != DEVICES or ".." in bits:
        return "", ""
    return bits[1], "/".join(bits[2:])


def part_of(key: str) -> str:
    """Which part a remote file belongs to, or "" if none of them.

    Needed because the store holds everything every machine has ever synced,
    while a given sync is only about the parts asked for. Without this, asking
    to sync just the playlists pulled down the settings and the save history
    too - they were in the store and not in the local list, which reads as
    "new over there" - and a narrow sync quietly became a full one.

    An unrecognised key answers "", which keeps it out of every part and so
    out of every sync. That is the wanted behaviour for a folder somebody has
    put their own files in, and for a part a newer version of this app writes
    that this one has never heard of.
    """
    head, _, rest = key.partition("/")
    if not rest:
        return ""
    if head in GATHERED:
        return head
    if head != "app":
        return ""
    if rest == state.SETTINGS_FILE:
        return "settings"
    top = rest.split("/")[0]
    for part, (files, folders) in state.BACKUP_PARTS.items():
        if rest in files or top in folders:
            return part
    return ""


def only_parts(files: dict, parts) -> dict:
    """The ones belonging to the parts being synced, and nothing else."""
    wanted = set(parts or ())
    return {k: v for k, v in files.items() if part_of(k) in wanted}


def plan(here: dict, there: dict, seen: dict, joining: bool = False) -> dict:
    """What to send, what to fetch, and what the two ends disagree about.

    `seen` is the manifest as it was after the last sync: it is what makes
    "changed" answerable at all. Without it a file that exists on one side and
    not the other is ambiguous - newly made here, or deleted there? - and the
    only safe reading of an ambiguity is to copy rather than delete, which is
    what this does.

    `joining` says this machine has never synced with this store before, and
    it changes who wins a disagreement. See the clash branch below.
    """
    push, pull, clash = [], [], []
    for key in sorted(set(here) | set(there)):
        mine, yours, last = here.get(key), there.get(key), seen.get(key)
        if mine and not yours:
            push.append(key)
            continue
        if yours and not mine:
            pull.append(key)
            continue
        if mine["hash"] == yours["hash"]:
            continue                                  # already the same

        # Both sides hold something, and they differ. Which of them changed
        # since the last sync is the whole question.
        #
        # "theirs" is what the store said about this file last time, kept
        # apart from our own hash because on WebDAV the two are not the same
        # kind of value. Older manifests have only the one, which is right
        # for a folder store, where both sides are content hashes.
        moved_here = not last or mine["hash"] != last.get("hash")
        moved_there = not last or yours["hash"] != last.get("theirs",
                                                            last.get("hash"))
        if not moved_here and not moved_there:
            # Neither end has moved since they last agreed. Reachable only
            # where the two hashes are not comparable - otherwise the equality
            # above has already caught it - and without this the run below
            # would call it a conflict and write one side over the other for
            # no reason at all.
            continue
        if moved_here and not moved_there:
            push.append(key)
        elif moved_there and not moved_here:
            pull.append(key)
        elif joining:
            # A machine syncing for the first time has no manifest, so every
            # disagreement lands here looking like "both changed" - and the
            # newer-wins rule below then hands it to whichever file was
            # written last, which on a fresh machine is its own empty
            # defaults. That is how a second computer could push an empty
            # playlist over the cloud and the first computer then pull the
            # emptiness back.
            #
            # Joining a set that already exists is the one case where the
            # answer is not in doubt: the store is what the other machines
            # agreed on, so it wins. The local copy is still kept beside it,
            # which is what makes this safe to do without asking.
            clash.append({"key": key, "mine": mine, "theirs": yours,
                          "take": "theirs"})
        else:
            # Both, or neither-that-we-can-tell. The newer wins and the older
            # is kept; see the module docstring.
            clash.append({"key": key, "mine": mine, "theirs": yours,
                          "take": "theirs"
                          if yours.get("when", 0) > mine.get("when", 0)
                          else "mine"})
    return {"push": push, "pull": pull, "clash": clash}


def kept_name(key: str, who: str, when: float) -> str:
    """What the losing side of a conflict is filed as, beside the winner."""
    stamp = time.strftime("%Y-%m-%d-%H%M", time.localtime(when or time.time()))
    safe = "".join(c for c in (who or "other") if c.isalnum() or c in "-_")[:24]
    return f"{key}.from-{safe or 'other'}-{stamp}"


def manifest_of(files: dict, theirs: dict | None = None) -> dict:
    """The record written after a sync, describing what both ends now hold.

    Two hashes, not one, when the store cannot answer with a content hash.

    A WebDAV server will not hash a file for you - asking would mean fetching
    every one of them - so the etag stands in, and an etag is a different kind
    of thing from the blake2b taken here. They never match, which made every
    file look changed on the far side on every run: a sync over WebDAV pulled
    the entire selection down again, every time, for ever. Recording what the
    store said alongside what we computed is what lets "unchanged" be
    answerable at all there.
    """
    out = {}
    for key, one in files.items():
        row = {"hash": one.get("hash") or "",
               "size": int(one.get("size") or 0),
               "when": float(one.get("when") or 0.0)}
        far = (theirs or {}).get(key) or {}
        if far.get("hash"):
            row["theirs"] = far["hash"]
        out[key] = row
    return out


def read_manifest(raw: bytes | None) -> dict:
    try:
        found = json.loads((raw or b"{}").decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return {}
    files = found.get("files") if isinstance(found, dict) else None
    return files if isinstance(files, dict) else {}


def manifest_meta(raw: bytes | None) -> dict:
    """Who wrote the store last, and when. Empty if it has never been written."""
    try:
        found = json.loads((raw or b"{}").decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return {}
    if not isinstance(found, dict):
        return {}
    return {"by": str(found.get("by") or ""),
            "byName": str(found.get("byName") or ""),
            "at": float(found.get("at") or 0.0)}


def write_manifest(files: dict) -> bytes:
    who = device()
    return json.dumps({"version": 1, "at": time.time(),
                       "by": who["id"], "byName": who["name"],
                       "files": files}, indent=1).encode("utf-8")


def seen_path() -> Path:
    """Where this machine remembers what it last agreed with the others."""
    return user("sync-seen.json")


def sent_path() -> Path:
    """What this machine last published as its own copy.

    Kept apart from sync-seen.json because it answers a different question.
    That one is what the two ends agreed the shared lane holds; this one is
    what our own lane holds, so a sync that changed nothing does not upload
    the same files again under our name every time.
    """
    return user("sync-sent.json")


def load_sent() -> dict:
    try:
        with open(sent_path(), encoding="utf-8") as fh:
            found = json.load(fh)
        return found if isinstance(found, dict) else {}
    except (OSError, ValueError):
        return {}


def save_sent(files: dict) -> None:
    try:
        spot = sent_path()
        spot.parent.mkdir(parents=True, exist_ok=True)
        temp = spot.with_suffix(".tmp")
        with open(temp, "w", encoding="utf-8") as fh:
            json.dump(files, fh, indent=1)
        os.replace(temp, spot)
    except OSError:
        pass          # forgetting costs an upload, not a file


def where_path() -> Path:
    """Which store the two records beside this one are about."""
    return user("sync-where.json")


def last_where() -> str:
    try:
        with open(where_path(), encoding="utf-8") as fh:
            found = json.load(fh)
        return str(found.get("where") or "") if isinstance(found, dict) else ""
    except (OSError, ValueError):
        return ""


def note_where(where: str) -> None:
    try:
        spot = where_path()
        spot.parent.mkdir(parents=True, exist_ok=True)
        temp = spot.with_suffix(".tmp")
        with open(temp, "w", encoding="utf-8") as fh:
            json.dump({"where": where, "at": time.time()}, fh, indent=1)
        os.replace(temp, spot)
    except OSError:
        pass


def load_seen() -> dict:
    try:
        with open(seen_path(), encoding="utf-8") as fh:
            found = json.load(fh)
        return found if isinstance(found, dict) else {}
    except (OSError, ValueError):
        return {}


def save_seen(files: dict) -> None:
    try:
        spot = seen_path()
        spot.parent.mkdir(parents=True, exist_ok=True)
        temp = spot.with_suffix(".tmp")
        with open(temp, "w", encoding="utf-8") as fh:
            json.dump(files, fh, indent=1)
        os.replace(temp, spot)
    except OSError:
        pass          # a forgotten manifest costs a redundant compare, no more
