"""Backing the saves up without being asked.

saves.py makes the case better than this docstring can: everything else the
app writes down can be got back - the index rebuilds from archive.org, the
covers re-download, the settings are a few minutes of typing - and a memory
card with sixty hours on it cannot be got back at all.

And then backing it up was a button somebody had to remember to press, which
means it was a thing that happened until it mattered.

So the same machinery runs on its own. Only the saves: an automatic snapshot
of the search index would be several hundred megabytes a week for something
that rebuilds itself, and the point of doing this quietly is that nobody has
to think about how much room it is taking.

Three snapshots are kept. Not one, because a save file that has gone wrong
usually goes wrong quietly and the newest copy has already caught it; not
twenty, because these are somebody's disk and the oldest of twenty weekly
snapshots is from a game they finished in the spring.

Nothing here touches the network, and nothing here writes into an emulator's
folder - a backup only ever reads.
"""

from __future__ import annotations

import re
import threading
import time
import zipfile
from pathlib import Path

from . import paths, saves, state

FOLDER = "Save backups"
KEEP = 3
# Seconds are in the name because two of these can be a few seconds apart:
# "Back up now" pressed twice, or pressed just after a scheduled one. To the
# minute they would share a filename and the second would silently overwrite
# the first, which is the opposite of what keeping three is for.
NAME = "romsrx-saves-%Y-%m-%d-%H%M%S.zip"
# Four digits as well as six, so snapshots written by an earlier build are
# still recognised as ours and still rotate rather than piling up forever.
STAMP = re.compile(r"^romsrx-saves-\d{4}-\d{2}-\d{2}-\d{4,6}(-\d+)?\.zip$")

# How often, in days, for each setting. "off" is absent on purpose: the code
# below reads a missing key as off rather than carrying a zero that has to be
# checked for everywhere.
EVERY = {"daily": 1, "weekly": 7, "monthly": 30}

_lock = threading.Lock()


def where() -> Path:
    """The folder the snapshots live in, beside the user's other files."""
    return Path(paths.user(FOLDER))


def _snapshots() -> list[Path]:
    """What is already there, oldest first.

    Matched by name rather than by anything else in the folder: somebody may
    well have put their own zip in here, and rotation deleting a file this app
    did not write would be unforgivable.
    """
    try:
        return sorted((p for p in where().iterdir()
                       if p.is_file() and STAMP.match(p.name)),
                      key=lambda p: p.name)
    except OSError:
        return []


def status() -> dict:
    """What the settings panel needs to say: when, and what is there."""
    kept = _snapshots()
    last = 0.0
    if kept:
        try:
            last = kept[-1].stat().st_mtime
        except OSError:
            last = 0.0
    total = 0
    for one in kept:
        try:
            total += one.stat().st_size
        except OSError:
            continue
    return {"folder": str(where()), "count": len(kept), "bytes": total,
            "last": last, "newest": kept[-1].name if kept else ""}


def _due(every: str, last: float) -> bool:
    days = EVERY.get(str(every or ""))
    if not days:
        return False
    if not last:
        return True                 # never run: the first one is due now
    return (time.time() - last) >= days * 86400 - 3600   # an hour of slack


def _free_name() -> Path:
    """A name nothing is using yet.

    Even to the second two of these can collide - a forced backup taken
    straight after a scheduled one - and the loser of that race would be
    silently overwritten, which is precisely what keeping three is meant to
    prevent. So the second one in a second gets a number.
    """
    folder = where()
    target = folder / time.strftime(NAME)
    if not target.exists():
        return target
    stem = target.name[:-len(".zip")]
    for n in range(2, 100):
        nth = folder / f"{stem}-{n}.zip"
        if not nth.exists():
            return nth
    return target          # a hundred in one second: overwrite and move on


def _rotate() -> None:
    for old in _snapshots()[:-KEEP]:
        try:
            old.unlink()
        except OSError:
            continue


def run(every: str, force: bool = False) -> dict:
    """Take a snapshot if one is due. Answers what it did.

    Never raises: this runs on a timer behind an app somebody is using, and a
    backup that cannot be written is a thing to report at the next glance
    rather than an error in the middle of a download.
    """
    if not force and not EVERY.get(str(every or "")):
        return {"ok": True, "made": False, "why": "off"}
    with _lock:
        now = status()
        if not force and not _due(every, now["last"]):
            return {"ok": True, "made": False, "why": "not due", **now}

        folders = saves.folders()
        if not folders:
            # Nothing found is not a failure - plenty of people play in
            # something this app cannot locate - but writing an empty zip
            # every week and calling it a backup would be a lie.
            return {"ok": True, "made": False, "why": "no saves found", **now}

        try:
            where().mkdir(parents=True, exist_ok=True)
            target = _free_name()
            written = 0
            with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as zf:
                zf.writestr(state.BACKUP_MARK, '{"app": "RomSrx", '
                            f'"made": {time.time()}, "version": 1, '
                            '"parts": ["saves"]}')
                written = saves.add_to_backup(zf)
            if not written:
                target.unlink(missing_ok=True)
                return {"ok": True, "made": False, "why": "nothing to save",
                        **status()}
        except (OSError, zipfile.BadZipFile) as exc:
            try:
                target.unlink(missing_ok=True)
            except (OSError, NameError):
                pass          # it may have failed before there was a name
            return {"ok": False, "made": False, "error": str(exc), **now}

        _rotate()
        return {"ok": True, "made": True, "files": written, **status()}
