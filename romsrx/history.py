"""A copy of your saves from every session, kept for a fortnight.

autosave.py already answers "my memory card is corrupt": a whole-saves zip on
a schedule, three of them, so there is always something to fall back to. This
answers a different question, and the difference is worth stating because it
decides the whole shape of the thing.

    "I want last Tuesday evening back."

Somebody finishes a session, and a week later finds they walked past the one
chest that had the achievement in it, or overwrote the slot they meant to
keep. A scheduled backup cannot help with that: it took its snapshot at a time
that has nothing to do with when they were playing, and it took one copy of
everything rather than one copy per moment they might want to return to.

So this snapshots when a session *ends* - the emulator closing is the moment a
save is final - and it files each one by when it happened:

    save-history/
        PCSX2/
            2026-08-21/
                18-42/
                    memcards/   ...as they were when that session closed
                    sstates/
                21-07/
            2026-08-22/
                09-15/
        RetroArch/
            2026-08-21/
                18-42/
                    saves/

The emulator comes first because that is how somebody looks for one of these:
they know which machine they were playing. Underneath it the day, then the
time, then the emulator's own folder names - so what is restored goes back
where it came from, and a PCSX2 memory card can never be confused for a
DuckStation one.

A day is the unit that gets thrown away, not a session, and the fifteen are
counted per emulator: playing a lot of PS2 should not shorten the history of
a Mega Drive that has not been touched in a fortnight. Within a day there is
no limit at all - somebody who plays six times on a Saturday wants all six,
and counting sessions would let one heavy weekend push out a month.

Only what changed. A session that ended with no save written leaves nothing
behind, and a session that wrote one memory card copies one memory card rather
than the whole of somebody's saves folder - which for a full RetroArch setup
is hundreds of megabytes, and would be hundreds of megabytes again every time
they stopped playing.

Nothing here writes into an emulator's folder. It only ever reads them.
"""

from __future__ import annotations

import re
import shutil
import threading
import time
from datetime import datetime
from pathlib import Path

from .paths import user

# Days kept, not sessions. See the docstring.
KEEP_DAYS = 15

# A file finished being written slightly before the emulator finished closing,
# and a filesystem's idea of "modified" is not to the microsecond. Anything
# touched from a moment before the session began counts as part of it.
GRACE = 5.0

DAY = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_lock = threading.Lock()


def where() -> Path:
    return user("save-history")


def systems() -> list[Path]:
    """The emulators anything has been kept for."""
    root = where()
    if not root.is_dir():
        return []
    return sorted((p for p in root.iterdir() if p.is_dir()),
                  key=lambda p: p.name)


def days(system: Path | str | None = None) -> list[Path]:
    """One emulator's day folders, oldest first; all of them if not named."""
    if system is None:
        out: list[Path] = []
        for one in systems():
            out += days(one)
        return out
    root = Path(system) if isinstance(system, (str, Path)) else system
    if not root.is_dir():
        return []
    found = [p for p in root.iterdir() if p.is_dir() and DAY.match(p.name)]
    return sorted(found, key=lambda p: p.name)


def sessions(day: Path) -> list[Path]:
    """The moments inside one day, earliest first."""
    if not day.is_dir():
        return []
    return sorted((p for p in day.iterdir() if p.is_dir()),
                  key=lambda p: p.name)


def _changed_since(folders, when: float
                   ) -> list[tuple[str, str, Path, Path]]:
    """(system, kind, the folder it came from, the file) for what was touched.

    Walked rather than globbed so a folder that cannot be read - an emulator
    holding a file open, a permission this app does not have - costs that one
    folder and not the snapshot.
    """
    out = []
    for folder in folders:
        root = Path(folder["path"])
        try:
            walk = list(root.rglob("*"))
        except OSError:
            continue
        for item in walk:
            try:
                if not item.is_file() or item.stat().st_mtime < when - GRACE:
                    continue
            except OSError:
                continue
            # Older callers of saves.folders only had `label`; fall back to it
            # rather than filing somebody's memory card under "None".
            system = folder.get("system") or folder.get("label") or "saves"
            kind = folder.get("kind") or ""
            out.append((system, kind, root, item))
    return out


def _rotate(system: Path) -> list[str]:
    """Drop that emulator's oldest days until only KEEP_DAYS remain."""
    gone = []
    for old in days(system)[:-KEEP_DAYS]:
        try:
            shutil.rmtree(old)
            gone.append(f"{system.name}/{old.name}")
        except OSError:
            pass                    # in use, or already gone
    return gone


def take(started: float, settings: dict | None = None,
         now: float | None = None) -> dict:
    """Copy whatever the session that began at `started` wrote down.

    Answers with what it did, so a caller can say so and a test can check it:
    {"saved": how many files, "at": the folder, "dropped": days removed}.
    """
    from . import saves  # noqa: PLC0415 - saves imports downloads, which

    #                     imports this; the cycle only closes at call time.
    stamp = datetime.fromtimestamp(now if now is not None else time.time())
    try:
        folders = saves.folders(settings)
    except Exception:  # noqa: BLE001 - a save this cannot find is not a crash
        return {"saved": 0, "at": "", "dropped": []}

    found = _changed_since(folders, started)
    if not found:
        # Nothing was written, so there is nothing to keep. Deliberately no
        # empty folder: a list of moments should be a list of moments that
        # have something in them.
        return {"saved": 0, "at": "", "dropped": []}

    # One session can touch two emulators only if two were open at once,
    # which is unusual but not impossible - so the files are grouped by the
    # machine they belong to and each gets its own folder under its own day.
    with _lock:
        written = 0
        places: list[str] = []
        dropped: list[str] = []
        for system in sorted({one[0] for one in found}):
            mine = [one for one in found if one[0] == system]
            home = where() / _safe(system)
            day = home / stamp.strftime("%Y-%m-%d")
            spot = day / stamp.strftime("%H-%M")
            # Two sessions ending inside the same minute are two sessions.
            if spot.exists():
                for extra in range(2, 60):
                    candidate = day / f"{stamp:%H-%M}-{extra}"
                    if not candidate.exists():
                        spot = candidate
                        break
            here = 0
            for _system, kind, root, item in mine:
                try:
                    inside = item.relative_to(root)
                except ValueError:
                    inside = Path(item.name)
                target = spot / _safe(kind) / inside
                try:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(item, target)
                    here += 1
                except OSError:
                    continue        # locked, or vanished mid-copy
            if not here:
                try:
                    shutil.rmtree(spot)
                except OSError:
                    pass
                continue
            written += here
            places.append(str(spot))
            dropped += _rotate(home)
        if not written:
            return {"saved": 0, "at": "", "dropped": []}
    return {"saved": written, "at": places[0], "places": places,
            "dropped": dropped}


def _safe(label: str) -> str:
    """A folder label that Windows will accept."""
    return re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", label).strip(" .") or "saves"


def listing() -> dict:
    """Everything kept, for the page that offers it back."""
    out = []
    for system in systems():
        shown = []
        for day in reversed(days(system)):
            moments = []
            for spot in reversed(sessions(day)):
                files = size = 0
                for item in spot.rglob("*"):
                    try:
                        if item.is_file():
                            files += 1
                            size += item.stat().st_size
                    except OSError:
                        continue
                moments.append({"at": spot.name, "path": str(spot),
                                "files": files, "bytes": size})
            shown.append({"day": day.name, "path": str(day),
                          "sessions": moments})
        out.append({"system": system.name, "path": str(system), "days": shown})
    return {"systems": out, "keep": KEEP_DAYS, "where": str(where())}

# -- putting one back -------------------------------------------------------


class Refused(Exception):
    """A restore that must not go ahead, with a reason to show somebody."""


def _destinations(settings: dict | None = None) -> dict[tuple[str, str], Path]:
    """{(system, kind): the folder it came out of}."""
    from . import saves  # noqa: PLC0415 - see take()

    out: dict[tuple[str, str], Path] = {}
    for folder in saves.folders(settings):
        system = folder.get("system") or folder.get("label") or ""
        kind = folder.get("kind") or ""
        if system:
            out[(_safe(system), _safe(kind))] = Path(folder["path"])
    return out


def plan(spot: Path | str, settings: dict | None = None) -> dict:
    """What restoring this moment would put back, and where.

    Worked out and shown before anything is written. Restoring a save is the
    one thing in this app that overwrites something the reader cannot get back
    from anywhere else, so it should never be the first time they learn what
    it was about to do.
    """
    spot = Path(spot)
    if not spot.is_dir():
        raise Refused("That snapshot is no longer there.")
    try:
        system = spot.parent.parent.name
    except (AttributeError, IndexError):       # pragma: no cover - malformed
        raise Refused("That does not look like a snapshot.") from None

    homes = _destinations(settings)
    files, missing = [], set()
    for item in sorted(spot.rglob("*")):
        if not item.is_file():
            continue
        inside = item.relative_to(spot)
        kind = inside.parts[0] if len(inside.parts) > 1 else ""
        home = homes.get((_safe(system), _safe(kind)))
        if home is None:
            missing.add(f"{system} {kind}".strip())
            continue
        target = home.joinpath(*inside.parts[1:])
        files.append({"from": str(item), "to": str(target),
                      "bytes": item.stat().st_size,
                      "replaces": target.exists()})
    return {"system": system, "day": spot.parent.name, "at": spot.name,
            "files": files, "unknown": sorted(missing)}


def restore(spot: Path | str, settings: dict | None = None) -> dict:
    """Put a moment's saves back where they came from.

    Two things happen before a byte is written, and both matter more than the
    copying does:

    The emulator must not be running. A save file is read into memory when a
    game starts and written out when it stops, so restoring underneath a
    running game achieves nothing at all - the game overwrites it on the way
    out, and the reader is left believing they went back and did not.

    And what is there now is snapshotted first. Restoring is the only thing
    here that destroys something, and "I picked the wrong evening" has to be
    survivable - so the current saves become an ordinary moment in the
    history, sitting where the reader would look for them.
    """
    from . import library  # noqa: PLC0415 - library imports downloads, which

    #                       reaches this module; the cycle closes at call time.
    if library.playing_now():
        raise Refused("Close the game first - it would write over the "
                      "restored save when it exits.")

    intent = plan(spot, settings)
    if not intent["files"]:
        raise Refused("There is nothing in that snapshot to put back.")

    # The way back from a restore, taken before the restore. Everything the
    # restore is about to overwrite counts as "changed a moment ago", so an
    # ordinary snapshot of it is exactly the right shape.
    undo = take(time.time(), settings)

    put = 0
    for one in intent["files"]:
        target = Path(one["to"])
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(one["from"], target)
            put += 1
        except OSError as exc:
            raise Refused(f"Could not write {target.name}: {exc}") from exc
    return {"restored": put, "system": intent["system"],
            "day": intent["day"], "at": intent["at"],
            "undo": undo.get("at", ""), "unknown": intent["unknown"]}
