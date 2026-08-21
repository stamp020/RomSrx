"""Small JSON stores for anything the user would expect to still be there
after closing, updating or reinstalling the app.

These live in the user folder (%APPDATA%\\RomSrx on Windows), not beside the
executable, so replacing the app folder doesn't wipe them. Writes go to a
temporary file first, so a crash mid-write can't leave a truncated file that
would lose the whole list.
"""

from __future__ import annotations

import json
import os
import shutil
import threading
import time
from pathlib import Path

from .paths import user

_lock = threading.Lock()


def _path(name: str) -> Path:
    return user(f"{name}.json")


def load(name: str, default):
    try:
        with open(_path(name), encoding="utf-8") as fh:
            value = json.load(fh)
    except (OSError, ValueError):
        return default
    return value if isinstance(value, type(default)) else default


def save(name: str, value) -> None:
    target = _path(name)
    temp = target.with_suffix(".tmp")
    with _lock:
        try:
            with open(temp, "w", encoding="utf-8") as fh:
                json.dump(value, fh, indent=1)
            os.replace(temp, target)
        except OSError:
            pass  # a lost preference isn't worth breaking a request over


# -- UI preferences ------------------------------------------------------
DEFAULT_PREFS = {
    "cartCompact": False,
    "libView": "grid",
    "libTitles": True,
    "libSize": 160,
    "libSort": "name",
    "cartSort": "added-desc",
    "tone": "default",      # default | dark | light
    # Shut the reindex window once it has nothing left to report.
    "indexAutoClose": False,
    # Let the page fill the window instead of sitting in a column down the
    # middle. Only the width changes; nothing moves anywhere else.
    "wideLayout": False,
    "accent": "blue",
    "lang": "en",           # en | pt
    "libPinned": [],        # consoles kept at the top of the library
    "libShut": [],          # consoles whose games are folded away
    # Which tab the app opens on: "search" or "library". The other is always
    # one click away in the header.
    "startOn": "search",
    # Leave the sets you have already mastered off the shelf. Only applied
    # while it is ordered by how much of each set you have earned.
    "libHideMastered": False,
    # Show only the copies whose hash is not in their achievement set. Offered
    # on the shelf once a check has actually found some.
    "libBadOnly": False,
    # Whether the compatibility tick and cross ride on the tiles: on | off.
    # The answers are kept either way; this is about the shelf, not the check.
    "libMarks": "on",
    # Which RetroAchievements medians sit on every tile regardless of the
    # sort: off | beat | master | both.
    "libTimes": "off",
    # What clicking a cover does: "play" the game, or open its "preview".
    "libClick": "play",
    # The profile window: which blocks are shown in which order, and whether
    # the awards are pictures alone rather than pictures with their names.
    "raProfileOrder": [],
    "raAwardIcons": False,
    # Leave the mastered games out of the beaten list, which otherwise
    # repeats most of the mastered one: every mastery earns a beaten award.
    "raBeatenOnly": False,
    # {tab: [award keys]} - the order awards were dragged into, per tab.
    "raAwardOrder": {},
    # How the people you follow are ordered: "points" or "seen" (most
    # recently at it first).
    "raFriendSort": "points",
    # What opens beside a game when it starts: "off", this app's own "app"
    # achievement list, or the game's page on the "site" itself. Off by
    # default: it is a second window every single launch, which is the point
    # for somebody chasing a set and an intrusion for everyone else.
    "achOnPlay": "off",
    # What the backup window had unticked last time: the parts left out
    # rather than the ones kept. Null until somebody actually changes a box,
    # so a window that has never been touched keeps the defaults written into
    # the markup - which are not simply "all of them", since the search index
    # is deliberately off to begin with.
    "backupSkip": None,
    "libOrder": [],         # consoles in the order they were dragged into
    "libShelf": "",         # playlist being shown, or "" for the whole library
    "cartWide": False,      # download list filling the window
    "dlWide": False,        # downloads panel filling the window
    "notifyDone": True,     # say so when a download finishes
    "muteDone": False,      # ...but without the chime
    # How many unfiled games the "not in any console's folder" note was last
    # dismissed at. It stays hidden until more than that turn up, so saying
    # "yes, I know" once is enough but a new pile still gets mentioned.
    "strayHidden": 0,
    # Where a game's RetroAchievements page opens: "app" for a window of this
    # app's own, "browser" for whichever browser the user has set as theirs.
    # The app's own window is the default because a sign-in there is remembered
    # and it keeps the page next to the library, but somebody already signed in
    # to RetroAchievements in their own browser will want the other one.
    "webTarget": "app",
    # Which shape Continue playing takes: "carousel" or "strip".
    "libRecentView": "carousel",
    # Leave games you have already finished out of the search results. Two
    # switches rather than one: beaten and mastered are different states and
    # people want them gone for different reasons.
    "hideBeaten": False,
    "hideMastered": False,
    # Whether every search result is checked against RetroAchievements as it
    # arrives, or only the cards whose own button is pressed. Automatic costs
    # a request per console behind every card.
    "raAuto": True,
    # -- torrents, for the MiNERVA sources ----------------------------
    #
    # Nothing here is on by default. BitTorrent uploads while it downloads,
    # which tells everyone in the swarm your address rather than just the one
    # server, and that is a thing to opt into with your eyes open. The page
    # says so before the first one runs.
    "torrentAgreed": False,
    # The adapter torrents are bound to. This is the kill switch: named to a
    # VPN's adapter, nothing leaves by any other route, and the transfers stop
    # if it goes away rather than falling back to the ordinary connection.
    "torrent_interface": "",
    # A SOCKS5 endpoint, the kind a VPN provider sells for exactly this. Peer
    # and tracker connections both go through it, and names are resolved at
    # the far end so the local DNS server is not told what is being fetched.
    "torrent_proxy_host": "",
    "torrent_proxy_port": 0,
    "torrent_proxy_user": "",
    "torrent_proxy_pass": "",
    # Strips what it can from what goes on the wire.
    "torrent_anonymous": True,
    # Kilobytes a second, 0 for no ceiling. Separate from the HTTP limit
    # because they are different pipes and people cap them differently -
    # upload especially, which HTTP downloads do not have at all.
    "torrent_down_limit": 0,
    "torrent_up_limit": 0,
    # Minutes to keep sharing a file back after it has finished, 0 for none.
    #
    # Off by default and deliberately so: uploading is what tells a swarm your
    # address, and turning that on for somebody without asking is the one
    # thing the rest of these settings exist to avoid. But MiNERVA is a
    # volunteer archive and this app has, until now, taken from it and given
    # nothing back - if every copy of it does that, there is eventually no
    # archive to take from. So it is offered, plainly, and left to the reader.
    "torrent_seed_minutes": 0,
    # How often the saves are backed up on their own: "off", "daily",
    # "weekly" or "monthly". Off unless asked for - these run to hundreds of
    # megabytes each and three are kept, and quietly taking a gigabyte of
    # somebody's disk is not a decision to make for them.
    "saveBackup": "off",
    # A colour of the reader's own, when none of the nine named ones will do.
    # Only used while `accent` is "custom".
    "accentCustom": "#6ea8fe",
    # How loud the download chime is, as a percentage of the volume it was
    # built at - so 100 is exactly what it has always sounded like.
    "doneVolume": 100,
    # The profile window: how many columns the blocks are laid out in, which
    # column each block is in, and whether the three kinds of award are shown
    # at once rather than behind tabs.
    "raProfileCols": 1,
    "raProfileCol": {},
    # {columns: {order, col}} - one arrangement per column count, since the
    # order that reads well in one tall column is not the one you would pick
    # having spread the same blocks across three.
    "raProfileLayout": {},
    "raAwardAll": False,
    # Which of the three award runs are folded away, by name.
    "raAwardShut": [],
}


def prefs() -> dict:
    stored = load("prefs", {})
    merged = dict(DEFAULT_PREFS)
    merged.update({k: v for k, v in stored.items() if k in DEFAULT_PREFS})
    return merged


def set_prefs(changes: dict) -> dict:
    current = prefs()
    current.update({k: v for k, v in changes.items() if k in DEFAULT_PREFS})
    save("prefs", current)
    return current


# -- the download list ---------------------------------------------------
def cart() -> list:
    return load("cart", [])


def set_cart(items: list) -> list:
    clean = [i for i in items if isinstance(i, dict) and i.get("url")]
    save("cart", clean)
    return clean


# -- playlists -----------------------------------------------------------
# Lists the user makes themselves. An entry is a game rather than a file on
# disk, so a playlist can hold things that aren't downloaded yet - which is
# the point of them: a wishlist and a shelf are the same list at different
# times. `key` is what identifies a game across both worlds; the page works
# it out from the filename, the same way the "In Library" markers do.
PLAYLIST_NAME_MAX = 60


def playlists() -> list:
    return load("playlists", [])


def set_playlists(items: list) -> list:
    """Store the lists as sent, keeping only what is structurally sound.

    Nothing here interprets an entry beyond needing a key - the page owns
    what a playlist entry holds, and rejecting fields it hasn't invented yet
    would mean a server change for every one it adds.
    """
    clean = []
    seen: set[str] = set()
    for raw in items:
        if not isinstance(raw, dict):
            continue
        ident = str(raw.get("id") or "").strip()
        if not ident or ident in seen:
            continue
        seen.add(ident)
        entries, keys = [], set()
        for entry in raw.get("items") or []:
            if not isinstance(entry, dict):
                continue
            key = str(entry.get("key") or "")
            if not key or key in keys:
                continue
            keys.add(key)
            entries.append(entry)
        clean.append({
            "id": ident,
            "name": (str(raw.get("name") or "").strip()
                     or "Playlist")[:PLAYLIST_NAME_MAX],
            "created": raw.get("created") or 0,
            "items": entries,
        })
    save("playlists", clean)
    return clean

# -- recently played -----------------------------------------------------
# What "Continue playing" is built from. Written when a game is actually
# launched, so it records what you played rather than what you clicked on.
# Keyed the same way playlists are, so a shelf can ask "which of these have I
# played" without knowing anything about paths.
RECENT_MAX = 24


def recent() -> list:
    return load("recent", [])


def push_recent(entry: dict) -> list:
    """Move a game to the front of the recently-played list.

    Same game twice running is one entry, not two, so the front of the list
    stays a list of different games rather than a log of one afternoon.
    """
    key = str(entry.get("key") or "")
    path = str(entry.get("path") or "")
    if not key and not path:
        return recent()

    kept = [e for e in recent()
            if isinstance(e, dict)
            and str(e.get("key") or "") != key
            and str(e.get("path") or "") != path]
    kept.insert(0, {
        "key": key,
        "path": path,
        "name": str(entry.get("name") or ""),
        "console": str(entry.get("console") or ""),
        "at": time.time(),
    })
    del kept[RECENT_MAX:]
    save("recent", kept)
    return kept

# -- backup and restore ---------------------------------------------------
# Everything the user built rather than downloaded: settings, lists,
# playlists, the covers they picked by hand. Not the index and not the games -
# those are megabytes and gigabytes respectively, and both rebuild themselves
# from somewhere else. What this carries is the part that cannot be got back.
#
# artwork.json is deliberately not here. It holds the API keys for the optional
# cover services, and a backup is a file people move about and hand to each
# other; the keys take half a minute to paste back in from the accounts they
# came from, which is a better trade than putting them in a portable zip.
# artcache.json is the opposite case - no secrets, and rebuilding it means
# spending a day's worth of somebody's API allowance again.
#
# retro/times.json is the other thing genuinely worth a day of somebody's
# patience: it is what Time every set spent half an hour and thousands of
# requests building (see times.py), and losing it on a reinstall means paying
# that half hour again rather than typing a setting back in. It lives in its
# own subfolder rather than beside these, which is why it needs its own entry
# instead of falling into the plain-file loop below.
BACKUP_FILES = ("prefs.json", "settings.json", "cart.json", "queue.json",
                "playlists.json", "recent.json", "covers.json", "window.json",
                "artcache.json", "retro/times.json")
BACKUP_DIRS = ("covers",)
BACKUP_MARK = "romsrx-backup.json"

# What a backup is made of, in the terms someone would actually pick from.
# Grouped rather than listed file by file: "prefs.json, settings.json,
# window.json" is three questions about one thing, and nobody wants their
# theme without their download folder.
BACKUP_PARTS: dict[str, tuple[tuple[str, ...], tuple[str, ...]]] = {
    # settings.json is not listed here: it is split down the middle between
    # "settings" and "paths" and written by hand. See _settings_slice.
    "settings":  (("prefs.json", "window.json"), ()),
    "paths":     ((), ()),
    "cart":      (("cart.json",), ()),
    "queue":     (("queue.json",), ()),
    "playlists": (("playlists.json",), ()),
    "recent":    (("recent.json",), ()),
    # Its own part rather than folded into "settings" or "covers": it is
    # neither a preference nor a picture, it is the answer to thousands of
    # network requests, and someone restoring onto a fresh machine should be
    # able to carry that answer without also carrying - or leaving behind -
    # anything else.
    "times":     (("retro/times.json",), ()),
    "covers":    (("covers.json", "artcache.json"), ("covers",)),
    # The index of what is on archive.org. Not listed among the plain files
    # below, because it is never copied as it lies: it is open, and written
    # to in a sidecar, so a consistent copy has to be asked of SQLite. See
    # _add_index. Off by default in the page - it is by far the largest thing
    # here, and it is the one part that can be rebuilt from nothing.
    "index":     ((), ()),
    # Not listed as files either: these live in the emulators' own folders,
    # wherever those turned out to be, so they are gathered rather than copied
    # from a known path. See saves.py and _add_saves.
    "saves":     ((), ()),
}

INDEX_FILE = "romsrx.db"

SETTINGS_FILE = "settings.json"

# The keys inside settings.json that name a place on this machine, or that are
# meaningless without one. Everything else in that file is a preference.
#
# They are separable because they are the one part of a backup that does not
# travel: two computers keep their games on different drives, and restoring a
# backup made on the first would otherwise point the second at folders that
# do not exist there. Splitting the file lets you carry how you like the app
# without carrying where this particular machine keeps things.
SETTINGS_PATH_KEYS = frozenset({
    "folder", "console_folders", "cover_folders", "cover_auto",
    "cover_delete", "emulators", "emulator_cores", "emulator_args",
})


def _settings_slice(root: Path, parts) -> dict | None:
    """The settings.json to put in the zip, or None to leave it out."""
    wants_prefs = parts is None or "settings" in parts
    wants_paths = parts is None or "paths" in parts
    if not wants_prefs and not wants_paths:
        return None
    try:
        with open(root / SETTINGS_FILE, encoding="utf-8") as fh:
            data = json.load(fh)
        if not isinstance(data, dict):
            return None
    except (OSError, ValueError):
        return None
    keep: dict = {}
    for key, value in data.items():
        wanted = wants_paths if key in SETTINGS_PATH_KEYS else wants_prefs
        if wanted:
            keep[key] = value
    return keep or None


def backup_contents(parts=None) -> tuple[list[str], list[str]]:
    """The whole files and folders a backup of these parts would carry.

    settings.json is never among them - it is written a key at a time by
    _settings_slice, because half of it belongs to "paths" and half to
    "settings". An unknown name is ignored rather than trusted: the list
    comes from the page, and the only names that mean anything are above.
    """
    if parts is None:
        return [f for f in BACKUP_FILES if f != SETTINGS_FILE], list(BACKUP_DIRS)
    files: list[str] = []
    dirs: list[str] = []
    for name in parts:
        chosen = BACKUP_PARTS.get(str(name))
        if not chosen:
            continue
        files.extend(chosen[0])
        dirs.extend(chosen[1])
    return files, dirs


def _add_index(zf) -> int:
    """Put a consistent copy of the index into an open backup zip.

    Taken through SQLite into a scratch file first. Copying the database as it
    lies would catch it mid-write and miss whatever is still in its sidecar,
    which produces a backup that looks fine and restores as a broken index.
    """
    import tempfile  # noqa: PLC0415

    from . import db  # noqa: PLC0415 - imported here to keep state.py a leaf

    if not Path(db.DB_PATH).is_file():
        return 0
    handle, scratch = tempfile.mkstemp(prefix="romsrx-index-", suffix=".db")
    os.close(handle)
    try:
        if not db.snapshot(scratch):
            return 0
        zf.write(scratch, INDEX_FILE)
        return 1
    finally:
        try:
            Path(scratch).unlink(missing_ok=True)
        except OSError:
            pass


def _add_saves(zf) -> int:
    """Put the emulators' save files and states into an open backup zip."""
    from . import saves  # noqa: PLC0415 - keeps state.py a leaf

    try:
        return saves.add_to_backup(zf)
    except Exception:  # noqa: BLE001 - a backup without saves is still a backup
        return 0


# Where a restore puts the saves it finds. Never back into the emulators' own
# folders: those hold whatever you have played since, and a six-month-old
# memory card written over a live one is not something to do to somebody as a
# side effect of pressing Restore. They are put here and the app says so.
RESTORED_SAVES = "restored-saves"


def write_backup(target: str, parts=None) -> dict:
    """Zip the chosen parts of the user folder into a file they picked.

    `parts` of None means everything, which is what every caller before the
    picker existed meant by asking at all.
    """
    import zipfile  # noqa: PLC0415
    root = _path("x").parent
    out = Path(target)
    names, folders = backup_contents(parts)
    written = 0
    try:
        with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
            # The marker says which parts are inside, so a restore can tell
            # the difference between "this backup left playlists out" and
            # "this backup has no playlists in it".
            zf.writestr(BACKUP_MARK, json.dumps(
                {"app": "RomSrx", "made": time.time(), "version": 1,
                 "parts": sorted(BACKUP_PARTS) if parts is None
                          else sorted(p for p in parts if p in BACKUP_PARTS)}))
            chosen_settings = _settings_slice(root, parts)
            if chosen_settings is not None:
                zf.writestr(SETTINGS_FILE,
                            json.dumps(chosen_settings, indent=2))
                written += 1
            if parts is None or "index" in parts:
                written += _add_index(zf)
            if parts is None or "saves" in parts:
                written += _add_saves(zf)
            for name in names:
                path = root / name
                if path.is_file():
                    zf.write(path, name); written += 1
            for folder in folders:
                base = root / folder
                if not base.is_dir():
                    continue
                for item in base.rglob("*"):
                    if item.is_file():
                        zf.write(item, str(Path(folder) / item.relative_to(base)))
                        written += 1
    except (OSError, ValueError) as exc:
        return {"ok": False, "error": f"Could not write the backup: {exc}"}
    return {"ok": True, "path": str(out), "files": written}


def _merged_settings(target: Path, incoming: bytes) -> bytes:
    """The backup's settings keys laid over the ones already here.

    Anything unreadable on either side falls back to the incoming file
    verbatim, which is what this did before it merged at all.
    """
    try:
        fresh = json.loads(incoming.decode("utf-8"))
        if not isinstance(fresh, dict):
            return incoming
    except (UnicodeDecodeError, ValueError):
        return incoming
    try:
        with open(target, encoding="utf-8") as fh:
            current = json.load(fh)
        if not isinstance(current, dict):
            current = {}
    except (OSError, ValueError):
        current = {}

    current.update(fresh)
    return json.dumps(current, indent=2).encode("utf-8")


def _restore_index(zf, root: Path) -> int:
    """Unpack a backed-up index to one side, for the next start to pick up.

    Never straight over the live one: this process has it open, and a database
    replaced underneath an open connection is either refused outright or left
    beside a sidecar describing the file it used to be. Written next to it
    instead, under a name db.connect looks for before it opens anything.
    """
    from . import db  # noqa: PLC0415

    target = root / (INDEX_FILE + db.RESTORE_SUFFIX)
    try:
        with zf.open(INDEX_FILE) as incoming, open(target, "wb") as out:
            shutil.copyfileobj(incoming, out, 1024 * 1024)
    except OSError:
        return 0
    return 1


def read_backup(source: str) -> dict:
    """Put a backup back, over whatever is here now.

    Only the names this app writes are unpacked, and each one is checked to
    land inside the user folder before anything is written: a zip is a file
    like any other and can name `../../somewhere`, which is how an archive
    turns into an overwrite of something it was never given.
    """
    import zipfile  # noqa: PLC0415
    root = _path("x").parent
    src = Path(source)
    if not src.is_file():
        return {"ok": False, "error": "That backup file no longer exists."}

    allowed = set(BACKUP_FILES)
    restored = 0
    try:
        with zipfile.ZipFile(src) as zf:
            if BACKUP_MARK not in zf.namelist():
                return {"ok": False,
                        "error": "That zip is not a RomSrx backup."}
            for name in zf.namelist():
                if name == BACKUP_MARK or name.endswith("/"):
                    continue
                head = name.split("/")[0]
                if name == INDEX_FILE:
                    restored += _restore_index(zf, root)
                    continue
                # Saves go to a folder of their own rather than back over
                # whatever the emulators hold now. See RESTORED_SAVES.
                if head == "saves":
                    target = (root / RESTORED_SAVES
                              / Path(*Path(name).parts[1:])).resolve()
                    if not str(target).startswith(str((root / RESTORED_SAVES).resolve())):
                        continue
                    target.parent.mkdir(parents=True, exist_ok=True)
                    with open(target, "wb") as out:
                        out.write(zf.read(name))
                    restored += 1
                    continue
                if name not in allowed and head not in BACKUP_DIRS:
                    continue
                target = (root / name).resolve()
                if not str(target).startswith(str(root.resolve())):
                    continue          # a zip that names its way out
                target.parent.mkdir(parents=True, exist_ok=True)
                data = zf.read(name)
                # settings.json is merged rather than replaced, and that is
                # what makes leaving "paths" out of a backup mean anything: a
                # backup made without them must not arrive on the second
                # machine and blank the folders it already had. Only the keys
                # actually in the file are written over.
                if name == SETTINGS_FILE:
                    data = _merged_settings(target, data)
                with open(target, "wb") as out:
                    out.write(data)
                restored += 1
    except (OSError, ValueError, zipfile.BadZipFile) as exc:
        return {"ok": False, "error": f"Could not read the backup: {exc}"}
    return {"ok": True, "files": restored}
