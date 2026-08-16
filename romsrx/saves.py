"""Where the emulators keep your saves, so a backup can carry them.

Everything else this app writes down can be got back. The index rebuilds from
archive.org, the covers re-download, the settings are a few minutes of typing.
A memory card with sixty hours on it cannot be got back at all, and it is the
one thing here that nobody thinks about until the disk it was on has gone.

Finding the folders is the whole job, and playtime.py had already done most of
it: to read how long you have played, it works out where RetroArch, PCSX2 and
DuckStation actually live - portable installs beside the executable, ordinary
ones under Documents or %APPDATA%, configured or not. The same roots hold the
saves, so this asks that module rather than guessing again.

Nothing here writes to an emulator's folder. A backup reads; a restore unpacks
somewhere of its own and says where. Putting a six-month-old memory card back
over a live one is exactly the sort of thing that should be somebody's decision
rather than a side effect of pressing Restore.
"""

from __future__ import annotations

import os
from pathlib import Path

from . import playtime

# What each emulator calls its saves, and which folders hold them.
#
# Both kinds are taken. A save file is the game's own progress and a save state
# is the emulator's snapshot of the machine; people rely on both, and which one
# matters is not this app's judgement to make.
#
# RetroArch's two can be moved in retroarch.cfg, so those are read from it
# where it says something, exactly as the runtime log directory is.
RETROARCH_DIRS = (("saves", "savefile_directory"),
                  ("states", "savestate_directory"))

# PCSX2 and DuckStation keep theirs in fixed folders under their data root.
PCSX2_DIRS = ("memcards", "sstates")
DUCKSTATION_DIRS = ("memcards", "savestates")

# A ceiling on what a backup will carry. Save states are large - a PlayStation 2
# state is a few megabytes and people keep hundreds - and a backup that silently
# becomes eight gigabytes is a backup that fails on the way to a USB stick.
MAX_BYTES = 2 * 1024 * 1024 * 1024


def _retroarch_roots(settings: dict) -> list[Path]:
    """Every RetroArch install this machine appears to have."""
    roots = list(playtime._candidate_dirs(settings))  # noqa: SLF001
    appdata = os.environ.get("APPDATA")
    if appdata:
        roots.append(Path(appdata) / "RetroArch")
    roots.append(Path.home() / ".config" / "retroarch")
    return [r for r in dict.fromkeys(roots) if (r / "retroarch.cfg").is_file()]


def _from_config(root: Path, setting: str) -> Path | None:
    """A folder retroarch.cfg names, if it names a real one.

    "default" is what it says until somebody changes it, which means the folder
    beside the config - so that reads as "no answer" here, the same way
    playtime.py treats the runtime log directory.
    """
    try:
        with open(root / "retroarch.cfg", encoding="utf-8", errors="replace") as fh:
            for line in fh:
                name, sep, value = line.partition("=")
                if sep and name.strip() == setting:
                    raw = value.strip().strip('"').strip()
                    if raw and raw.lower() != "default":
                        found = Path(os.path.expandvars(raw)).expanduser()
                        if not found.is_absolute():
                            found = root / found
                        return found if found.is_dir() else None
    except OSError:
        pass
    return None


def _measure(path: Path) -> tuple[int, int]:
    """(files, bytes) under a folder, or (0, 0) if it isn't one."""
    files = size = 0
    if not path.is_dir():
        return 0, 0
    for item in path.rglob("*"):
        try:
            if item.is_file():
                files += 1
                size += item.stat().st_size
        except OSError:
            continue
    return files, size


def folders(settings: dict | None = None) -> list[dict]:
    """Every save folder found, with how much is in each.

    `label` is what the zip files it under and what the page shows, so it has
    to be both readable and safe as a folder name.
    """
    if settings is None:
        from . import downloads  # noqa: PLC0415 - avoids a cycle at import
        settings = downloads.load_settings()

    found: list[tuple[str, Path]] = []
    for number, root in enumerate(_retroarch_roots(settings), start=1):
        tag = "RetroArch" if number == 1 else f"RetroArch {number}"
        for folder, setting in RETROARCH_DIRS:
            where = _from_config(root, setting) or (root / folder)
            found.append((f"{tag} {folder}", where))

    for root, runs in playtime._data_roots(settings):  # noqa: SLF001
        # PCSX2's data root is its `inis` folder; the saves sit beside it.
        base = root.parent if root.name.lower() == "inis" else root
        names = (PCSX2_DIRS if runs == playtime.RUNS["pcsx2"]
                 else DUCKSTATION_DIRS)
        tag = "PCSX2" if runs == playtime.RUNS["pcsx2"] else "DuckStation"
        for folder in names:
            found.append((f"{tag} {folder}", base / folder))

    out: list[dict] = []
    seen: set[str] = set()
    for label, path in found:
        try:
            real = str(path.resolve())
        except OSError:
            continue
        if real in seen:
            continue
        seen.add(real)
        files, size = _measure(path)
        if files:
            out.append({"label": label, "path": str(path),
                        "files": files, "bytes": size})
    return out


def summary(settings: dict | None = None) -> dict:
    """What the backup window shows beside the tick box."""
    found = folders(settings)
    return {
        "folders": found,
        "files": sum(f["files"] for f in found),
        "bytes": sum(f["bytes"] for f in found),
        "tooBig": sum(f["bytes"] for f in found) > MAX_BYTES,
        "limit": MAX_BYTES,
    }


def add_to_backup(zf, settings: dict | None = None) -> int:
    """Write every save folder into an open backup zip. Returns files added.

    Filed under `saves/<label>/...`, which keeps two RetroArch installs apart
    and means a person can open the zip and see whose saves are whose.
    """
    written = 0
    budget = MAX_BYTES
    for folder in folders(settings):
        base = Path(folder["path"])
        for item in sorted(base.rglob("*")):
            try:
                if not item.is_file():
                    continue
                size = item.stat().st_size
            except OSError:
                continue
            if size > budget:
                return written          # the ceiling, reached mid-folder
            budget -= size
            inside = Path("saves") / folder["label"] / item.relative_to(base)
            try:
                zf.write(item, str(inside))
            except OSError:
                continue
            written += 1
    return written
