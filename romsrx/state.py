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
    "accent": "blue",
    "lang": "en",           # en | pt
    "libPinned": [],        # consoles kept at the top of the library
    "libShut": [],          # consoles whose games are folded away
    "libShelf": "",         # playlist being shown, or "" for the whole library
    "cartWide": False,      # download list filling the window
    "dlWide": False,        # downloads panel filling the window
    "notifyDone": True,     # say so when a download finishes
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
BACKUP_FILES = ("prefs.json", "settings.json", "cart.json", "queue.json",
                "playlists.json", "recent.json", "covers.json", "window.json")
BACKUP_DIRS = ("covers",)
BACKUP_MARK = "romsrx-backup.json"


def write_backup(target: str) -> dict:
    """Zip the user folder into a file they chose."""
    import zipfile  # noqa: PLC0415
    root = _path("x").parent
    out = Path(target)
    written = 0
    try:
        with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr(BACKUP_MARK, json.dumps(
                {"app": "RomSrx", "made": time.time(), "version": 1}))
            for name in BACKUP_FILES:
                path = root / name
                if path.is_file():
                    zf.write(path, name); written += 1
            for folder in BACKUP_DIRS:
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
                if name not in allowed and head not in BACKUP_DIRS:
                    continue
                target = (root / name).resolve()
                if not str(target).startswith(str(root.resolve())):
                    continue          # a zip that names its way out
                target.parent.mkdir(parents=True, exist_ok=True)
                with zf.open(name) as fh, open(target, "wb") as out:
                    out.write(fh.read())
                restored += 1
    except (OSError, ValueError, zipfile.BadZipFile) as exc:
        return {"ok": False, "error": f"Could not read the backup: {exc}"}
    return {"ok": True, "files": restored}
