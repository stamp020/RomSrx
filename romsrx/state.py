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
