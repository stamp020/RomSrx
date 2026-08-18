"""Finding the emulators already installed, so they need not be typed in.

Setting this app up means pointing each console at a program, and on a machine
with a dozen consoles that is a dozen trips through a file picker to name
programs the user installed themselves and could reasonably expect to be
found. Everything needed to find them is already here: playtime.py walks the
same folders looking for runtime logs, and hardcore.py finds retroarch.cfg the
same way.

Nothing is executed and nothing is written. This reads directory listings,
matches filenames against the table below, and hands back what it saw as a
suggestion - the page decides what to do with it, and an emulator the user has
already chosen is never quietly replaced. A wrong guess here would send games
to the wrong program, so a name has to match exactly rather than nearly.

The search is deliberately shallow. It looks where installers put things and
beside the emulators already configured - people keep their emulators together,
which is the same assumption playtime._candidate_dirs already makes - two
levels down and no further. Walking whole drives to save one file picker is
not a trade worth making.
"""

from __future__ import annotations

import os
from pathlib import Path

from . import playtime

# Executable -> what it is and which consoles it plays. The dedicated
# emulators come first and RetroArch fills in behind them: it plays nearly
# everything, but where somebody has PCSX2 installed it is PCSX2 they meant
# for the PlayStation 2.
#
# Only emulators RetroAchievements supports, since that is what this app is
# for, and only exact filenames - "pcsx2-qt.exe" and "pcsx2x64.exe" are both
# real, "pcsx2-setup.exe" is an installer and must never be launched as one.
KNOWN: tuple[tuple[str, tuple[str, ...], tuple[str, ...]], ...] = (
    ("PCSX2", ("pcsx2-qt.exe", "pcsx2x64.exe", "pcsx2x64-avx2.exe", "pcsx2.exe"),
     ("PlayStation 2",)),
    ("DuckStation", ("duckstation-qt-x64-ReleaseLTCG.exe", "duckstation-qt.exe",
                     "duckstation-nogui-x64-ReleaseLTCG.exe", "duckstation.exe"),
     ("PlayStation",)),
    ("Dolphin", ("Dolphin.exe", "DolphinWx.exe"),
     ("GameCube", "Nintendo Wii")),
    ("PPSSPP", ("PPSSPPWindows64.exe", "PPSSPPWindows.exe", "PPSSPP.exe"),
     ("PSP",)),
    ("melonDS", ("melonDS.exe",), ("Nintendo DS", "Nintendo DSi")),
    ("Flycast", ("flycast.exe",), ("Sega Dreamcast",)),
    ("mGBA", ("mGBA.exe",),
     ("Game Boy Advance", "Game Boy Color", "Game Boy")),
    ("Snes9x", ("snes9x-x64.exe", "snes9x.exe"), ("SNES/Super Famicom",)),
    ("Mesen", ("Mesen.exe",), ("NES/Famicom", "Famicom Disk System")),
    # Last on purpose: everything above is a better answer for its own
    # console, and this takes the consoles none of them claimed.
    ("RetroArch", ("retroarch.exe",), ()),
)

# What RetroArch is offered for: every console this app knows that the
# dedicated emulators above do not already cover. Named rather than computed
# from "everything" so a console nothing can play is not offered a program
# that cannot play it either.
RETROARCH_CONSOLES = (
    "NES/Famicom", "Famicom Disk System", "SNES/Super Famicom",
    "Nintendo 64", "Game Boy", "Game Boy Color", "Game Boy Advance",
    "Nintendo DS", "Nintendo DSi", "Virtual Boy", "Pokemon Mini",
    "Genesis/Mega Drive", "Master System", "Game Gear", "SG-1000", "32X",
    "Sega CD", "Sega Saturn", "PlayStation", "PC Engine/TurboGrafx-16",
    "PC Engine CD/TurboGrafx-CD", "Neo Geo Pocket", "Neo Geo CD",
    "Atari 2600", "Atari 7800", "Atari Lynx", "Atari Jaguar", "WonderSwan",
)

# How far down a candidate folder to look. An installer puts the program
# either in the folder it made or one below it; three levels would mean
# reading half of Program Files to save a file picker.
DEPTH = 2


def _roots(settings: dict) -> list[Path]:
    """Where to look: the same places playtime.py already looks."""
    roots: list[Path] = []
    try:
        roots.extend(playtime._candidate_dirs(settings))  # noqa: SLF001
    except Exception:  # noqa: BLE001 - a bad setting is not a failure
        pass
    for var in ("ProgramFiles", "ProgramFiles(x86)", "LOCALAPPDATA"):
        where = os.environ.get(var)
        if where:
            roots.append(Path(where))
    roots.append(Path.home())
    return [p for p in dict.fromkeys(roots) if p.is_dir()]


def _find_exes(roots: list[Path], wanted: set[str]) -> dict[str, Path]:
    """{lowercased filename: where it is}, for the names asked about."""
    found: dict[str, Path] = {}
    seen: set[str] = set()
    for root in roots:
        stack = [(root, 0)]
        while stack:
            where, depth = stack.pop()
            key = str(where).lower()
            if key in seen:
                continue
            seen.add(key)
            try:
                entries = list(os.scandir(where))
            except OSError:
                continue
            for entry in entries:
                try:
                    if entry.is_file():
                        name = entry.name.lower()
                        if name in wanted and name not in found:
                            found[name] = Path(entry.path)
                    elif entry.is_dir() and depth < DEPTH:
                        stack.append((Path(entry.path), depth + 1))
                except OSError:
                    continue
    return found


def scan(settings: dict | None = None) -> dict:
    """What is installed, and which console each thing would serve.

    Returns suggestions only. Whether any of them is taken up - and whether a
    console that already has a program keeps it - is the page's decision and
    then the user's.
    """
    from . import downloads  # noqa: PLC0415

    if settings is None:
        try:
            settings = downloads.load_settings()
        except Exception:  # noqa: BLE001
            settings = {}

    wanted = {name.lower() for _, names, _ in KNOWN for name in names}
    found = _find_exes(_roots(settings), wanted)

    already = {str(k): str(v) for k, v in
               (settings.get("emulators") or {}).items() if v}

    programs: list[dict] = []
    suggestions: dict[str, dict] = {}
    for label, names, consoles in KNOWN:
        where = next((found[n.lower()] for n in names
                      if n.lower() in found), None)
        if not where:
            continue
        programs.append({"name": label, "path": str(where)})

        # RetroArch takes whatever the dedicated ones did not claim.
        for console in (consoles or RETROARCH_CONSOLES):
            if console in suggestions:
                continue
            suggestions[console] = {
                "name": label,
                "path": str(where),
                # So the page can offer the empty ones without argument and
                # ask before touching a console already set to something.
                "taken": already.get(console, ""),
                "same": already.get(console, "") == str(where),
            }

    fresh = sum(1 for one in suggestions.values() if not one["taken"])
    return {"ok": True, "programs": programs, "consoles": suggestions,
            "found": len(programs), "empty": fresh,
            "occupied": sum(1 for one in suggestions.values()
                            if one["taken"] and not one["same"])}
