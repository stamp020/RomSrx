"""Where things live, whether running from source or from a built .exe.

Two different roots are needed once frozen:

* RESOURCE_DIR - read-only files bundled into the build (web/, sources.json).
  PyInstaller unpacks these to a temp folder exposed as sys._MEIPASS.
* DATA_DIR - files the app writes and the user keeps (romsrx.db,
  settings.json). These must sit next to the .exe, not in the temp folder,
  or they'd vanish when the app closes.
"""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

FROZEN = getattr(sys, "frozen", False)

# Anything the user would hate to lose lives here rather than beside the .exe,
# so reinstalling or replacing the app folder keeps their list, queue,
# settings and hand-picked covers.
if os.name == "nt":
    USER_DIR = Path(os.environ.get("APPDATA", Path.home())) / "RomSrx"
else:
    USER_DIR = Path.home() / ".romsrx"

if FROZEN:
    RESOURCE_DIR = Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
    DATA_DIR = Path(sys.executable).parent
else:
    RESOURCE_DIR = Path(__file__).resolve().parent.parent
    DATA_DIR = RESOURCE_DIR


def resource(*parts: str) -> Path:
    """A file shipped with the app."""
    return RESOURCE_DIR.joinpath(*parts)


def data(*parts: str) -> Path:
    """A file the app reads and writes, kept beside the executable."""
    return DATA_DIR.joinpath(*parts)


def user(*parts: str) -> Path:
    """A file belonging to the user, kept outside the app folder."""
    USER_DIR.mkdir(parents=True, exist_ok=True)
    return USER_DIR.joinpath(*parts)


def migrate_user_files(names: tuple[str, ...]) -> None:
    """Move settings written by older versions into the user folder."""
    for name in names:
        old, new = DATA_DIR / name, USER_DIR / name
        if not old.exists() or new.exists():
            continue
        try:
            USER_DIR.mkdir(parents=True, exist_ok=True)
            shutil.move(str(old), str(new))
        except OSError:
            pass
