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
