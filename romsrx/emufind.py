"""Finding the emulators already installed, so they need not be typed in.

Setting this app up means pointing each console at a program, and on a machine
with a dozen consoles that is a dozen trips through a file picker to name
programs the user installed themselves and could reasonably expect to be
found.

Nothing is executed and nothing is written. This reads directory listings and
the registry's list of installed programs, matches filenames against the table
below, and hands back what it saw as a suggestion - the page decides what to
do with it, and an emulator the user has already chosen is never quietly
replaced. A wrong guess here would send games to the wrong program, so a name
has to match exactly rather than nearly.

Where it looks is the whole difficulty. The first version of this read only
the places an *installer* puts things - Program Files, %LOCALAPPDATA%, and
beside the emulators already configured - and that is not where emulators
actually live. Most of them ship as a zip that gets unpacked wherever there is
room, which on a machine with two drives means somewhere like
`D:\\Emulator\\Retroarch`, and the search walked straight past it. Worse, it
walked past it in exactly the case this button exists for: somebody who has
configured nothing yet, so there is no configured emulator to look beside, so
the search came back empty and the button read as broken.

So the answer has to come from the disk itself, and there are four ways in,
cheapest first:

* **The registry.** Anything installed by an installer records where it went,
  which is a handful of key reads and no walking at all.
* **What this app already knows.** The emulators configured here, and the
  folders the user keeps games in - `D:\\Emulator\\PS2 Games` says a great deal
  about where `D:\\Emulator\\PS2` is - along with whatever sits beside them.
* **The ordinary install folders**, as before.
* **Every drive**, from the root, shallowly.

That last one is the one that has to be kept honest, and it is kept honest two
ways. Folders that only ever hold the system are never opened at all, and the
depth is small - but a folder whose *name* says it is a container rather than
a program ("Games", "Emulators", "steamapps", "common") is stepped through for
free, so `D:\\Steam\\steamapps\\common\\RetroArch` is reached at the same
shallow depth as `D:\\RetroArch`. On top of that sits a cap on how many folders
may be read and how long the whole thing may take, so the worst case is a
search that gives up with less than it might have found rather than one that
sits there.
"""

from __future__ import annotations

import os
import time
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

# How far below a starting point to look. Small, because the starting points
# are many and the folders that matter are named - see FREE. Three levels of
# genuinely unhelpful folder names is already further from a drive root than
# an emulator has ever been.
DEPTH = 3

# Folders that are never opened. The system's own, the caches that sit beside
# them, and the two or three that are famous for holding a hundred thousand
# directories of things that are not programs. Matched on the name alone, at
# any level, since "node_modules" is no more worth walking on D: than on C:.
SKIP = {
    "windows", "winsxs", "system volume information", "recovery", "boot",
    "efi", "config.msi", "msocache", "perflogs", "documents and settings",
    "onedrivetemp", "windowsapps", "packagecache", "package cache",
    "packages", "assembly", "installer", "servicing", "sxs", "locallow",
    "temp", "tmp", "cache", "cache2", "caches", "cachestorage",
    "node_modules", "__pycache__", "site-packages", ".git", ".svn", ".cache",
}

# Folders whose name says "there are programs in here", stepped into without
# spending any of the depth budget. This is what lets a shallow search reach
# `D:\Steam\steamapps\common\RetroArch\retroarch.exe` and
# `E:\Games\Emulators\mGBA\mGBA.exe` - both of which are, by the count of
# folders, deep, and neither of which is hiding.
FREE = {
    "program files", "program files (x86)", "programs", "programdata",
    "apps", "applications", "software", "tools", "utilities", "portable",
    "games", "game", "gaming", "steam", "steamapps", "common",
    "steamlibrary", "emu", "emus", "emulator", "emulators", "emulation",
    "retro", "retrogaming", "roms", "rom", "launchbox", "playnite",
    "downloads", "desktop", "documents", "my documents",
}

# The ceiling on the whole search, whatever it is pointed at. A directory
# listing is cheap and there is a limit to how many of them anybody should pay
# for a button that saves a trip through a file picker; a slow external disk
# is the case these are really for. Reaching either is not a failure - it
# means the answer is whatever had been found by then.
MAX_DIRS = 30000
MAX_SECONDS = 20.0

# Where an installed program says it went. Read-only, and every value is
# checked against the disk before it is believed.
UNINSTALL_KEYS = (
    r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
    r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall",
)


def _norm(path: str | Path) -> str:
    """One spelling of a path, so two of them can be compared.

    A path saved by the file picker comes back with backslashes and one saved
    by an earlier version comes back with forward slashes, and on Windows the
    case is not meaningful either. Comparing the raw strings said that
    `D:/Emulator/Retroarch/retroarch.exe` and
    `D:\\Emulator\\Retroarch\\retroarch.exe` were different programs, which
    turned "everything is already set to what I just found" into a dialog
    offering to replace twenty-eight consoles with the emulators they were
    already pointed at.
    """
    try:
        text = os.path.normpath(str(path))
    except (TypeError, ValueError):
        text = str(path)
    return os.path.normcase(text)


def _registry_roots() -> list[Path]:
    """Where the installed programs say they live.

    Free next to walking a disk, and exactly right when it answers: an
    installer records the folder it wrote to, so a DuckStation installed the
    ordinary way is found without opening a single unrelated directory. It
    says nothing at all about the unpacked-zip emulators, which is what the
    rest of the search is for.
    """
    if os.name != "nt":
        return []
    try:
        import winreg  # noqa: PLC0415
    except ImportError:
        return []

    found: list[Path] = []
    for hive in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
        for key in UNINSTALL_KEYS:
            try:
                parent = winreg.OpenKey(hive, key)
            except OSError:
                continue
            with parent:
                try:
                    count = winreg.QueryInfoKey(parent)[0]
                except OSError:
                    continue
                for index in range(count):
                    try:
                        name = winreg.EnumKey(parent, index)
                        with winreg.OpenKey(parent, name) as sub:
                            where, _ = winreg.QueryValueEx(sub, "InstallLocation")
                    except OSError:
                        continue
                    if isinstance(where, str) and where.strip():
                        found.append(Path(where.strip()))
    return found


def _drive_roots() -> list[Path]:
    """Every drive worth walking, and none that would sit there.

    A network share can take a second per listing and an empty card reader can
    take longer than that to say it is empty, so only the disks actually
    attached to this machine are opened.
    """
    if os.name != "nt":
        # Where a second disk gets mounted, rather than "/" - walking a root
        # filesystem three levels deep is a different proposition.
        found = [Path("/media"), Path("/mnt"), Path("/run/media"),
                 Path("/Volumes"), Path("/opt"), Path("/usr/local")]
        return [p for p in found if p.is_dir()]

    kernel32 = None
    try:
        import ctypes  # noqa: PLC0415

        kernel32 = ctypes.windll.kernel32  # type: ignore[attr-defined]
    except Exception:  # noqa: BLE001 - then every letter is simply tried
        kernel32 = None

    # DRIVE_REMOVABLE and DRIVE_FIXED. Removable is in because an external
    # disk full of games is a normal way to keep them; the network and optical
    # kinds are out because they are slow and never hold an installed program.
    keep = (2, 3)
    found: list[Path] = []
    for letter in "CDEFGHIJKLMNOPQRSTUVWXYZAB":
        if kernel32 is not None and kernel32.GetDriveTypeW(f"{letter}:\\") not in keep:
            continue
        root = Path(f"{letter}:\\")
        try:
            if root.is_dir():
                found.append(root)
        except OSError:
            continue
    return found


def _game_roots(settings: dict) -> list[Path]:
    """The folders this app already knows about, and what they sit beside.

    Somebody who keeps `D:\\Emulator\\PS2 Games` almost certainly keeps
    `D:\\Emulator\\PS2` as well, so the parent of a games folder is one of the
    better guesses on the machine - and it is a guess this app can make about
    somebody who has configured nothing but where their downloads go.
    """
    named: list[Path] = []
    folder = str(settings.get("folder") or "").strip()
    if folder:
        named.append(Path(folder))
    for where in (settings.get("console_folders") or {}).values():
        text = str(where or "").strip()
        # A bare name here means a folder inside the downloads folder, which
        # the downloads folder itself already covers.
        if text and os.path.isabs(text):
            named.append(Path(text))

    roots: list[Path] = []
    for path in named:
        roots.append(path)
        roots.append(path.parent)
    return roots


def _roots(settings: dict) -> list[tuple[Path, int]]:
    """Everywhere to start from, best guess first, each with its own depth.

    The order is the point of this list: the first program of a given name to
    be found is the one that gets offered, so the machine's own record of what
    it installed comes before a guess about where somebody unpacked a zip, and
    the drives come last of all.
    """
    starts: list[tuple[Path, int]] = []

    # Beside the emulators already configured, which is both the best guess
    # there is and free - playtime.py builds the same list.
    try:
        for path in playtime._candidate_dirs(settings):  # noqa: SLF001
            starts.append((path, 2))
    except Exception:  # noqa: BLE001 - a bad setting is not a failure
        pass

    for path in _registry_roots():
        starts.append((path, 2))
    for path in _game_roots(settings):
        starts.append((path, 2))

    for var in ("ProgramFiles", "ProgramFiles(x86)"):
        where = os.environ.get(var)
        if where:
            starts.append((Path(where), 2))
    local = os.environ.get("LOCALAPPDATA")
    if local:
        # The per-user install folder deserves the full depth; the rest of
        # AppData\Local is a great deal of settings and one or two programs.
        starts.append((Path(local) / "Programs", DEPTH))
        starts.append((Path(local), 2))

    home = Path.home()
    for name in ("Downloads", "Desktop", "Documents"):
        starts.append((home / name, 2))
    starts.append((home, 2))

    # ...and then the disks themselves, which is what finds an emulator
    # unpacked somewhere this app had no way to guess.
    for path in _drive_roots():
        starts.append((path, DEPTH))

    seen: set[str] = set()
    roots: list[tuple[Path, int]] = []
    for path, depth in starts:
        key = _norm(path)
        if key in seen:
            continue
        try:
            if not path.is_dir():
                continue
        except OSError:
            continue
        seen.add(key)
        roots.append((path, depth))
    return roots


def _find_exes(roots: list[tuple[Path, int]], wanted: set[str]) -> dict[str, Path]:
    """{lowercased filename: where it is}, for the names asked about.

    Breadth-first and in the order the roots were given, so a program that
    exists in two places is reported from the better guess. It stops the
    moment every name has turned up, which on a tidy machine is long before
    any of the caps comes near.
    """
    found: dict[str, Path] = {}
    seen: set[str] = set()
    deadline = time.monotonic() + MAX_SECONDS
    read = 0

    queue: list[tuple[Path, int]] = list(roots)
    at = 0
    while at < len(queue):
        if len(found) == len(wanted) or read >= MAX_DIRS:
            break
        # Checked against the clock rather than the folder count as well,
        # because the two go wrong in different ways: a thousand folders on a
        # local disk is nothing and a hundred on a sleeping external one is a
        # minute.
        if read % 64 == 0 and time.monotonic() > deadline:
            break

        where, budget = queue[at]
        at += 1
        key = _norm(where)
        if key in seen:
            continue
        seen.add(key)

        try:
            entries = list(os.scandir(where))
        except OSError:
            continue
        read += 1

        for entry in entries:
            try:
                if entry.is_file():
                    name = entry.name.lower()
                    if name in wanted and name not in found:
                        found[name] = Path(entry.path)
                    continue
                if not entry.is_dir() or entry.is_symlink():
                    continue
            except OSError:
                continue

            name = entry.name.lower()
            # The "$" ones are the recycle bin and the leftovers of a Windows
            # upgrade, which between them are most of what is at a drive root.
            if name in SKIP or name.startswith("$"):
                continue
            # A folder that is plainly a container rather than a program does
            # not count against the depth: it is not where the emulator is, it
            # is the shelf the emulator is on.
            left = budget if name in FREE else budget - 1
            if left >= 0:
                queue.append((Path(entry.path), left))
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

    started = time.monotonic()
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
            taken = already.get(console, "")
            suggestions[console] = {
                "name": label,
                "path": str(where),
                # So the page can offer the empty ones without argument and
                # ask before touching a console already set to something.
                "taken": taken,
                # Compared as paths rather than as strings - see _norm.
                "same": bool(taken) and _norm(taken) == _norm(where),
            }

    fresh = sum(1 for one in suggestions.values() if not one["taken"])
    return {"ok": True, "programs": programs, "consoles": suggestions,
            "found": len(programs), "empty": fresh,
            "occupied": sum(1 for one in suggestions.values()
                            if one["taken"] and not one["same"]),
            "seconds": round(time.monotonic() - started, 1)}
