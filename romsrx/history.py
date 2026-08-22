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
         now: float | None = None, played_: str = "") -> dict:
    """Copy whatever the session that began at `started` wrote down.

    Answers with what it did, so a caller can say so and a test can check it:
    {"saved": how many files, "at": the folder, "dropped": days removed}.

    `played_` is the game, when this app was the one that started it - see
    library.watch. Written down beside the snapshot so the panel can say
    "PCSX2 - Spyro the Dragon" rather than "PCSX2, 21:07", which is the
    difference between a list somebody can search and a list of timestamps.

    Only recorded when the session produced exactly one folder. Two means two
    emulators were writing, and this app started one game: labelling both with
    it would be right about one and a lie about the other, and a wrong label
    is worse than none at all. Games started outside the app leave it empty,
    and the panel simply shows no name.
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
        if played_ and len(places) == 1:
            try:
                game_path(Path(places[0])).write_text(
                    " ".join(str(played_).split())[:NOTE_MAX],
                    encoding="utf-8")
            except OSError:
                pass            # a missing label is not worth losing a save
    return {"saved": written, "at": places[0], "places": places,
            "dropped": dropped}


def _safe(label: str) -> str:
    """A folder label that Windows will accept."""
    return re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", label).strip(" .") or "saves"


# What RetroArch calls a core, said as the consoles it plays.
#
# RetroArch files its saves under the core rather than the console -
# `saves/Gambatte/Pokemon.srm` - which is the right thing for it to do and the
# wrong thing to show somebody looking for their Game Boy save. Nobody thinks
# "I was playing Gambatte".
#
# The map from console to core already exists for launching games; this reads
# it backwards. Folded to letters and digits on both sides because the two
# spell the same core differently: "mupen64plus_next" configured here,
# "Mupen64Plus-Next" on disk.
def _core_names() -> dict[str, list[str]]:
    from . import cores  # noqa: PLC0415 - a leaf, and only this needs it

    out: dict[str, list[str]] = {}
    for console, core in (getattr(cores, "BEST", None) or {}).items():
        out.setdefault(re.sub(r"[^a-z0-9]", "", str(core).lower()),
                       []).append(console)
    return out


def group_name(system: str, folder: str) -> str:
    """What to call one subfolder of a snapshot, for somebody choosing.

    The folder's own name unless it is a RetroArch core we can name the
    consoles for, in which case it is both: "Gambatte" alone means nothing to
    most people, and "Game Boy · Game Boy Color" alone would be a puzzle for
    anybody who does know their cores and is looking for the folder they can
    see on disk.
    """
    if not folder:
        return ""
    consoles = _core_names().get(re.sub(r"[^a-z0-9]", "", folder.lower()))
    if not consoles or not system.lower().startswith("retroarch"):
        return folder
    return f"{folder} - " + " · ".join(sorted(consoles))


def _sorts_by_core(system: str) -> bool:
    """Whether this emulator's subfolders are consoles. Only RetroArch's are.

    "RetroArch 2" as well as "RetroArch": a machine with two installs gets one
    folder each, and both sort their saves the same way.
    """
    return str(system or "").lower().startswith("retroarch")


def _group_of(inside: Path, system: str = "") -> str:
    """Which console-sized part of a snapshot a file belongs to.

    A snapshot is `<kind>/<rest>`, and for RetroArch the folder under the kind
    is the core - `saves/Gambatte/Pokemon.srm` - which is a console, and is
    the thing worth choosing between.

    For every other emulator it is not a console and must not be offered as
    one. Found on a real machine: PCSX2 can keep a memory card as a *folder*
    rather than a file, so `memcards/Mcd001_converted.ps2/` is a directory,
    and the rule "the folder under the kind" cheerfully listed a memory card
    in the console picker. A file that belongs to no console answers "",
    meaning "no group", and a snapshot made only of those offers no picker at
    all - which is the whole session's Restore button, as before.
    """
    if not _sorts_by_core(system):
        return ""
    return inside.parts[1] if len(inside.parts) > 2 else ""


def groups(spot: Path) -> list[dict]:
    """The choosable parts of one snapshot, with how much is in each."""
    seen: dict[str, dict] = {}
    system = spot.parent.parent.name
    for item in spot.rglob("*"):
        try:
            if not item.is_file():
                continue
            size = item.stat().st_size
        except OSError:
            continue
        key = _group_of(item.relative_to(spot), system)
        row = seen.setdefault(key, {"group": key,
                                    "label": group_name(system, key),
                                    "files": 0, "bytes": 0})
        row["files"] += 1
        row["bytes"] += size
    # Named ones first and alphabetically; the unsplittable remainder last,
    # because it is the leftovers rather than a console.
    return sorted(seen.values(), key=lambda one: (not one["group"],
                                                  one["group"].lower()))


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
                                "files": files, "bytes": size,
                                # So the page can offer one console out of a
                                # RetroArch session rather than all of them.
                                "groups": groups(spot),
                                "note": note(spot),
                                "game": played(spot)})
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


def _snapshot(spot: Path | str) -> tuple[Path, str]:
    """Check a path from the page really is one snapshot. (folder, emulator).

    Inside the history folder, three levels down, and nowhere else.

    These paths arrive from the page, and what is done with them afterwards is
    "walk everything under here and copy it into the emulators' folders" - so
    an unchecked one is a request to copy any folder on the machine into
    somebody's save directory. It also has to be one snapshot rather than a
    parent of several: handed the day folder, the walk would gather every
    session that day and put the lot back on top of each other.

    Found by a malformed request rather than by thinking about it. A blank
    `at` became `Path("")`, which is `Path(".")`, which is a directory - so a
    request with no path in it walked the app's own install folder.
    """
    root = where().resolve()
    try:
        spot = Path(str(spot) or ".").resolve()
        inside = spot.relative_to(root)
    except (OSError, ValueError):
        raise Refused("That does not look like a snapshot.") from None
    if len(inside.parts) != 3:
        raise Refused("That does not look like a snapshot.")
    if not spot.is_dir():
        raise Refused("That snapshot is no longer there.")
    return spot, inside.parts[0]


# -- a line about what this evening was -------------------------------------
#
# Fifteen days of "21:07, 3 files" tells you when you played and nothing about
# what happened, and the whole feature exists for "I want last Tuesday back" -
# which means somebody has to be able to find last Tuesday. A note is how:
# "before the point of no return", "full health run", "don't lose this one".
#
# Kept beside the snapshot rather than inside it, and that is the whole design
# decision here. Inside, it would be an ordinary file in the folder - counted
# in the file total, offered as something to restore, and copied into the
# emulator's save directory the moment somebody used the button. Beside it,
# `sessions` and `days` never see it (both list directories only), `plan`
# never walks it, and it is thrown away with its day when the fortnight turns,
# because `_rotate` removes the day folder whole.
NOTE_MAX = 400


def note_path(spot: Path) -> Path:
    return spot.parent / (spot.name + ".note")


# What was being played when the session ended, when the app is the one that
# started it. Written by `take` rather than typed, and kept apart from the
# note so that filling one in never disturbs the other.
#
# Beside the snapshot for the same reason the note is: inside, it would be an
# ordinary file to be counted, offered, and copied into somebody's saves.
def game_path(spot: Path) -> Path:
    return spot.parent / (spot.name + ".game")


def played(spot: Path) -> str:
    """The game this session was, if the app knows. "" if it does not."""
    try:
        return game_path(spot).read_text(encoding="utf-8").strip()
    except (OSError, ValueError):
        return ""


def note(spot: Path) -> str:
    """Whatever was written about this session, or ""."""
    try:
        return note_path(spot).read_text(encoding="utf-8").strip()
    except (OSError, ValueError):
        return ""


def set_note(spot: Path | str, text: str) -> dict:
    """Write a line about one session. Blank removes it.

    Removes rather than leaves an empty file: an empty note and no note are
    the same thing to a reader, and only one of them should exist on disk.
    """
    spot, _system = _snapshot(spot)
    words = " ".join(str(text or "").split())[:NOTE_MAX]
    where_ = note_path(spot)
    try:
        if words:
            where_.write_text(words, encoding="utf-8")
        else:
            where_.unlink(missing_ok=True)
    except OSError as exc:
        raise Refused(f"Could not write that down: {exc}") from exc
    return {"at": str(spot), "note": words}


def plan(spot: Path | str, settings: dict | None = None,
         only: list[str] | None = None) -> dict:
    """What restoring this moment would put back, and where.

    Worked out and shown before anything is written. Restoring a save is the
    one thing in this app that overwrites something the reader cannot get back
    from anywhere else, so it should never be the first time they learn what
    it was about to do.

    `only` narrows it to particular groups - see `groups`. A RetroArch session
    holds every console played that evening, and somebody who wants Tuesday's
    Game Boy save back should not have to take Tuesday's Nintendo 64 with it.
    An empty or absent `only` means all of it, as before.
    """
    spot, system = _snapshot(spot)

    homes = _destinations(settings)
    wanted = set(only or [])
    files, missing = [], set()
    for item in sorted(spot.rglob("*")):
        if not item.is_file():
            continue
        inside = item.relative_to(spot)
        if wanted and _group_of(inside, system) not in wanted:
            continue
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
            "only": sorted(wanted), "files": files, "unknown": sorted(missing)}


def restore(spot: Path | str, settings: dict | None = None,
            only: list[str] | None = None) -> dict:
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

    intent = plan(spot, settings, only)
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
