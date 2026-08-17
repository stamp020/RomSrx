"""How long each game has been played, according to the emulator that ran it.

played.py works out *when* a game was last opened, by noticing that the
filesystem recorded a read. It cannot say for how long: an access time is a
moment, not a duration. That has to come from whatever was actually running
the game, and only some emulators keep it.

Two families of them do, and they are read in two different ways because they
key their records differently.

**RetroArch** writes one small JSON file per game per core, under
`playlists/logs/<Core Name>/<game>.lrtl`, holding the total runtime, the last
time it was played and how many times. It is on by default
(`content_runtime_log`), and it is named after the file, so matching it to a
game on disk is just the filename.

**PCSX2 and DuckStation** - the same author, and the same format - append to a
plain `playtime.dat`, one fixed-width line per game:

    SLUS-20946                       5447                 1754925600

that is, a disc serial, the total seconds played, and when it was last played.
Nothing about that says which *file* it was, so the serial has to be turned
into a name: both emulators ship a game database keyed by exactly that serial
(`GameIndex.yaml`, `gamedb.yaml`), and both spell an entry the same way. So
the serial becomes a title, and the title is matched against the library.

Everything else on the RetroAchievements list keeps nothing to read. PPSSPP
has no play time at all - it is an open feature request upstream. Dolphin,
BizHawk, Flycast and the standalone RA builds (RANes, RAMeka, RAVBA, RASnes9x,
RAProject64 and the rest) do not record it either. A game played on one of
those has no time against it, which is the honest answer.
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

from .names import normalize_title

# -- RetroArch ----------------------------------------------------------
LOG_EXT = ".lrtl"
DEFAULT_LOGS = ("playlists", "logs")

# "1:30:47", and occasionally "12:05:00" - hours are not padded and can run
# past two digits.
_RUNTIME_RE = re.compile(r"^(\d+):([0-5]?\d):([0-5]?\d)$")

# A cap on how much of someone's disk this will walk. A logs folder holds one
# small file per game per core; a library of a few thousand is still only a
# few thousand files, and anything wildly past that is not a logs folder.
MAX_LOGS = 20000

# -- PCSX2 / DuckStation ------------------------------------------------
PLAYTIME_FILE = "playtime.dat"

# `SLUS-20946   5447   1754925600`, padded out to fixed columns. Split on
# whitespace rather than by column, so a future change to the widths - or a
# hand-edited file - still reads.
_PLAYED_RE = re.compile(r"^(\S+)\s+(\d+)\s+(\d+)\s*$")

# The game databases both emulators ship. Same shape in each: a serial at the
# left margin, then an indented `name:`.
GAME_DBS = ("GameIndex.yaml", "gamedb.yaml")
_SERIAL_RE = re.compile(r"^([A-Za-z0-9][A-Za-z0-9._-]*):\s*$")
_NAME_RE = re.compile(r'^\s+name:\s*"(.*)"\s*$')

# Nothing sensible is longer than this. A serial that ran away with the line
# is a malformed file, not a game.
MAX_SERIAL = 64


def seconds_of(runtime: str) -> int:
    """"1:30:47" -> 5447. Zero for anything that isn't a duration."""
    match = _RUNTIME_RE.match((runtime or "").strip())
    if not match:
        return 0
    hours, minutes, secs = (int(part) for part in match.groups())
    return hours * 3600 + minutes * 60 + secs


def _emulators(settings: dict) -> list[Path]:
    """Every distinct emulator executable the user has configured."""
    found: list[Path] = []
    for raw in (settings.get("emulators") or {}).values():
        exe = str(raw or "").strip()
        if not exe:
            continue
        path = Path(exe)
        if path not in found:
            found.append(path)
    return found


# ---------- RetroArch ----------

def _log_dirs(settings: dict) -> list[Path]:
    """Every RetroArch runtime-log folder this machine appears to have.

    The emulators configured here are the first place to look, since that is
    where the user has already said their RetroArch lives. But it need not be
    configured at all - plenty of people launch RetroArch themselves and use
    this app only to find games - so the ordinary install and config folders
    are looked at too.
    """
    found: list[Path] = []
    roots = list(_candidate_dirs(settings))
    # Where RetroArch keeps its configuration when it wasn't unzipped
    # somewhere and run in place.
    appdata = os.environ.get("APPDATA")
    if appdata:
        roots.append(Path(appdata) / "RetroArch")
    roots.append(Path.home() / ".config" / "retroarch")     # Linux

    for root in roots:
        # Only somewhere that is actually a RetroArch: every folder in
        # Program Files is in this list, and most of them are not one.
        if not (root / "retroarch.cfg").is_file() \
                and not root.joinpath(*DEFAULT_LOGS).is_dir():
            continue
        logs = _configured_dir(root) or root.joinpath(*DEFAULT_LOGS)
        if logs.is_dir() and logs not in found:
            found.append(logs)
    return found


def _configured_dir(root: Path) -> Path | None:
    """`runtime_log_directory` out of retroarch.cfg, if it names a real one.

    "default" - which is what it says until someone changes it - means the
    folder beside the playlists, so that reads as "no answer" here.
    """
    try:
        with open(root / "retroarch.cfg", encoding="utf-8", errors="replace") as fh:
            for line in fh:
                key, _, value = line.partition("=")
                if key.strip() != "runtime_log_directory":
                    continue
                where = value.strip().strip('"').strip()
                if not where or where == "default":
                    return None
                path = Path(where)
                return path if path.is_absolute() else root / path
    except OSError:
        pass
    return None


def _read_log(path: Path) -> dict | None:
    """One .lrtl file, or None if it isn't one."""
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            saved = json.load(fh)
    except (OSError, ValueError):
        return None
    if not isinstance(saved, dict):
        return None

    seconds = seconds_of(str(saved.get("runtime") or ""))
    if not seconds:
        return None
    try:
        count = int(str(saved.get("play_count") or 0))
    except (TypeError, ValueError):
        count = 0
    return {"seconds": seconds, "count": max(count, 0)}


def collect_retroarch(settings: dict) -> dict[str, dict]:
    """{lowercased game name: {seconds, count}} across every core.

    A game played on two cores - a Game Boy title on Gambatte and again on
    mGBA - has a log under each, and the two are added together, because the
    question being answered is how long *this game* has been played.
    """
    totals: dict[str, dict] = {}
    seen = 0
    for logs in _log_dirs(settings):
        for core in sorted(logs.iterdir()) if logs.is_dir() else []:
            if not core.is_dir():
                continue
            for entry in sorted(core.iterdir()):
                if seen >= MAX_LOGS:
                    return totals
                if not entry.name.lower().endswith(LOG_EXT):
                    continue
                seen += 1
                found = _read_log(entry)
                if not found:
                    continue
                key = entry.name[: -len(LOG_EXT)].lower()
                into = totals.setdefault(key, {"seconds": 0, "count": 0})
                into["seconds"] += found["seconds"]
                into["count"] += found["count"]
    return totals


# ---------- PCSX2 and DuckStation ----------

def _documents() -> Path:
    """The user's Documents folder, wherever it has actually been put.

    Not `~/Documents`. That is wrong twice over on a normal Windows machine:
    OneDrive moves the folder under its own tree, and a non-English Windows
    names it in that language - this one is `D:\\OneDrive\\Documentos`. Both
    emulators below keep their data there by default, so guessing the path
    means finding nothing and reporting it as "you have not played anything".
    Windows records where it really is, so it is asked.
    """
    if sys.platform == "win32":
        try:
            import winreg  # noqa: PLC0415 - Windows only

            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Explorer"
                r"\User Shell Folders",
            ) as key:
                value, _ = winreg.QueryValueEx(key, "Personal")
            where = Path(os.path.expandvars(str(value)))
            if where.is_dir():
                return where
        except (OSError, ValueError):
            pass
    return Path.home() / "Documents"


# What each of these emulators actually runs, spelled the way this app spells
# it. A time out of PCSX2 belongs to a PlayStation 2 game and to nothing else:
# plenty of titles were released on three machines at once, and without this a
# PS2 playthrough would be credited to the Wii copy sitting in the library.
RUNS = {"pcsx2": "PlayStation 2", "duckstation": "PlayStation"}


def _data_roots(settings: dict) -> list[tuple[Path, str]]:
    """Every folder that might hold a playtime.dat, and what it runs.

    Both emulators support a portable install, where everything sits beside
    the executable, and an ordinary one under Documents. Both are looked at:
    the only thing being read is one small text file, and looking in a folder
    that isn't there costs nothing.

    The Documents ones are checked whether or not the emulator is configured
    in this app. Someone can perfectly well play their PlayStation games in
    DuckStation and never tell RomSrx about it - the play time is theirs
    either way, and the folder is in a known place.
    """
    docs = _documents()
    home = Path.home()
    roots = [(docs / "PCSX2" / "inis", RUNS["pcsx2"]),
             (docs / "DuckStation", RUNS["duckstation"]),
             # Where both put it on Linux, which this app also ships for.
             (home / ".config" / "PCSX2" / "inis", RUNS["pcsx2"]),
             (home / ".local" / "share" / "duckstation", RUNS["duckstation"])]
    for exe in _emulators(settings):
        name = exe.name.lower()
        if "pcsx2" in name:
            roots.append((exe.parent / "inis", RUNS["pcsx2"]))   # ::Settings
        elif "duckstation" in name:
            roots.append((exe.parent, RUNS["duckstation"]))      # ::DataRoot
    return list(dict.fromkeys(roots))


def _read_playtime(path: Path) -> dict[str, int]:
    """{serial: seconds} out of a playtime.dat."""
    totals: dict[str, int] = {}
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                match = _PLAYED_RE.match(line)
                if not match:
                    continue
                serial, seconds, _last = match.groups()
                if len(serial) > MAX_SERIAL:
                    continue
                totals[serial.upper()] = totals.get(serial.upper(), 0) + int(seconds)
    except (OSError, ValueError):
        pass
    return totals


def _install_roots() -> list[Path]:
    """Folders that hold installed programs, one level up from the program.

    Deliberately short. This is looked through for a `resources` folder, so a
    long list would mean stat-ing every program on the machine every time the
    library is read; these four are where an emulator installer actually puts
    things, and anything unusual is found by way of the emulator the user has
    configured instead.
    """
    found: list[Path] = []
    for var in ("ProgramFiles", "ProgramFiles(x86)", "LOCALAPPDATA"):
        where = os.environ.get(var)
        if not where:
            continue
        base = Path(where)
        found.append(base / "Programs" if var == "LOCALAPPDATA" else base)
    found.append(Path.home())
    return [p for p in dict.fromkeys(found) if p.is_dir()]


def _candidate_dirs(settings: dict) -> list[Path]:
    """Folders an emulator might be installed in, best guess first.

    The emulators configured here, then whatever sits beside them - people
    keep their emulators together, so a DuckStation next to a configured
    PCSX2 is found without being asked about - then the ordinary install
    folders, for a machine where nothing has been configured at all.

    One level down in each, and only ever listing directory names, so this
    stays a handful of listings rather than a search of the disk.
    """
    roots: list[Path] = []
    for exe in _emulators(settings):
        roots.append(exe.parent)
        try:
            roots.extend(p for p in exe.parent.parent.iterdir() if p.is_dir())
        except OSError:
            continue
    for base in _install_roots():
        try:
            roots.extend(p for p in base.iterdir() if p.is_dir())
        except OSError:
            continue
    return list(dict.fromkeys(roots))


def _db_paths(settings: dict) -> list[Path]:
    """Every serial-to-title database on this machine that can be found."""
    found: list[Path] = []
    for root in _candidate_dirs(settings):
        for db in GAME_DBS:
            path = root / "resources" / db
            if path.is_file() and path not in found:
                found.append(path)
    return found


def _titles_for(dbs: list[Path], serials: set[str]) -> dict[str, str]:
    """{serial: game name} for the serials asked about.

    The databases run to several megabytes and describe tens of thousands of
    games, of which a handful are ever wanted, so this reads them a line at a
    time and keeps only what was asked for. Nothing is parsed as YAML: the two
    lines that matter have a shape of their own, and a real parser would mean
    loading the whole of it to answer a question about six games.
    """
    found: dict[str, str] = {}
    if not serials:
        return found
    for path in dbs:
        wanted = ""
        try:
            with open(path, encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    serial = _SERIAL_RE.match(line)
                    if serial:
                        candidate = serial.group(1).upper()
                        wanted = candidate if candidate in serials else ""
                        continue
                    if not wanted:
                        continue
                    name = _NAME_RE.match(line)
                    if name:
                        found.setdefault(wanted, name.group(1))
                        wanted = ""
                        if len(found) == len(serials):
                            return found
        except OSError:
            continue
    return found


def collect_serial_based(settings: dict) -> dict[tuple[str, str], dict]:
    """{(console, normalised title): {seconds, count}} - PCSX2, DuckStation.

    There is no play count in these - the file records total time and when it
    was last played, and nothing about how many sittings that took - so the
    count stays zero rather than being invented.
    """
    played: dict[str, dict[str, int]] = {}      # serial -> console -> seconds
    for root, console in _data_roots(settings):
        for serial, seconds in _read_playtime(root / PLAYTIME_FILE).items():
            into = played.setdefault(serial, {})
            into[console] = into.get(console, 0) + seconds

    totals: dict[tuple[str, str], dict] = {}
    if not played:
        return totals

    # Serials with no entry in any database are left out rather than shown
    # under their serial: DuckStation files content it cannot identify as
    # `HASH-…`, and a disc pressed without a proper serial can end up under a
    # date. Neither is a title, and neither matches anything in a library.
    for serial, name in _titles_for(_db_paths(settings), set(played)).items():
        key = normalize_title(name)
        if not key:
            continue
        for console, seconds in played.get(serial, {}).items():
            into = totals.setdefault((console, key), {"seconds": 0, "count": 0})
            into["seconds"] += seconds
    return totals


# ---------- putting it on the games ----------

def attach(games: list[dict], settings: dict) -> int:
    """Stamp `playSeconds` on every game an emulator has a time for.

    RetroArch is matched on the file's own name, which is what it names the
    log after. PCSX2 and DuckStation are matched on the title their database
    gives for the serial - a serial says nothing about which file on this
    machine it was - and on the console that emulator runs, so hours put into
    a PlayStation 2 game are never shown against the Wii release of it. A game
    played in both is the sum of the two.

    Anything unmatched is left at zero rather than guessed at - a time against
    the wrong game is worse than no time at all.

    Note that this is no longer the last word on the shelf. RetroAchievements
    counts across every machine somebody plays on, and covers the emulators
    below that write no log at all, so its figure is the one shown where it
    has one and this is what stands behind it - see profile.playtimes() and
    fillPlaytimes() in the page. Nothing here changed; what changed is which
    of the two is read first.
    """
    try:
        by_name = collect_retroarch(settings)
    except OSError:
        by_name = {}
    try:
        by_title = collect_serial_based(settings)
    except OSError:
        by_title = {}

    stamped = 0
    for game in games:
        found = by_name.get(str(game.get("name") or "").lower())
        titled = by_title.get((str(game.get("console") or ""),
                               str(game.get("title_norm") or "")))

        seconds = (found["seconds"] if found else 0) + \
                  (titled["seconds"] if titled else 0)
        game["playSeconds"] = seconds
        game["playCount"] = found["count"] if found else 0
        if seconds:
            stamped += 1
    return stamped
