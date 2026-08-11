"""What's actually on disk: scans the download folders for installed games.

A downloaded game is either a single file (Game (USA).chd) or, when the
archive was extracted, a folder of the same name containing the ROM. Both are
treated as one entry, so the library reads the same either way.

Nothing here touches the network - it only looks at the folders the download
manager writes to.
"""

from __future__ import annotations

import hashlib
import json
import shlex
import shutil
import subprocess
from pathlib import Path

from . import names
from .downloads import folder_for, load_settings
from .paths import user

# Covers the user picks themselves, for games the thumbnail server has no art
# for. The image is copied in so it survives the original being moved, and it
# lives in the user folder so reinstalling the app keeps it.
COVERS_DIR = user("covers")
COVERS_INDEX = user("covers.json")
IMAGE_TYPES = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp"}

# Extensions worth showing. Anything else in the folder (notes, saves, logs)
# is ignored rather than presented as a game.
ROM_EXTENSIONS = {
    "zip", "7z", "rar", "chd", "iso", "bin", "cue", "img", "mdf", "nrg",
    "ecm", "gz", "rvz", "wbfs", "cso", "pbp", "gdi", "cdi", "wad", "gcm",
    "gcz", "ciso", "cci", "dax", "wia", "nes", "fds", "sfc", "smc", "gba",
    "gbc", "gb", "n64", "z64", "v64", "nds", "dsi", "md", "gen", "gg", "sms",
    "sg", "pce", "vb", "min", "ngp", "ngc", "a26", "a78", "j64", "jag",
    "lnx", "col", "int", "d88", "vpk", "cia", "3ds", "xci", "nsp", "rom",
}

SKIP_SUFFIXES = (".part", ".tmp", ".crdownload")

# Folders that are never a game, however they turn up. `_internal` is
# PyInstaller's own: it holds base_library.zip, and since a folder containing
# a .zip counts as an extracted game, pointing the download folder at the app
# itself would list the program's insides as a game called "_internal".
SKIP_DIRS = {"_internal", "__pycache__", "$recycle.bin", "system volume information"}

# How far to descend looking for games. Enough for layouts that group by
# letter or region, without walking an entire drive.
MAX_DEPTH = 3


def _load_covers() -> dict:
    try:
        with open(COVERS_INDEX, encoding="utf-8") as fh:
            data_ = json.load(fh)
        return data_ if isinstance(data_, dict) else {}
    except (OSError, ValueError):
        return {}


def _save_covers(mapping: dict) -> None:
    COVERS_INDEX.parent.mkdir(parents=True, exist_ok=True)
    with open(COVERS_INDEX, "w", encoding="utf-8") as fh:
        json.dump(mapping, fh, indent=2)


def _cover_key(game_path: str) -> str:
    return hashlib.sha1(game_path.lower().encode("utf-8")).hexdigest()[:16]


def set_cover(game_path: str, image_path: str) -> dict:
    """Copy a chosen image in and remember it for this game."""
    source = Path(image_path)
    if not source.is_file():
        return {"ok": False, "error": "That file no longer exists."}
    if source.suffix.lower() not in IMAGE_TYPES:
        return {"ok": False, "error": "Pick a PNG, JPG, WEBP, GIF or BMP."}

    COVERS_DIR.mkdir(parents=True, exist_ok=True)
    name = f"{_cover_key(game_path)}{source.suffix.lower()}"
    try:
        shutil.copyfile(source, COVERS_DIR / name)
    except OSError as exc:
        return {"ok": False, "error": f"Could not copy the image: {exc}"}

    mapping = _load_covers()
    mapping[game_path] = name
    _save_covers(mapping)
    return {"ok": True, "cover": f"/covers/{name}"}


def clear_cover(game_path: str) -> dict:
    mapping = _load_covers()
    name = mapping.pop(game_path, None)
    if name:
        try:
            (COVERS_DIR / name).unlink(missing_ok=True)
        except OSError:
            pass
        _save_covers(mapping)
    return {"ok": True}


def delete_games(paths: list[str]) -> dict:
    """Remove games from disk. Only touches things inside a known folder."""
    settings = load_settings()
    roots = [Path(settings["folder"]).resolve()]
    for value in (settings.get("console_folders") or {}).values():
        candidate = Path(value)
        roots.append(candidate.resolve() if candidate.is_absolute()
                     else (Path(settings["folder"]) / candidate).resolve())

    removed, failed = [], []
    mapping = _load_covers()
    for raw in paths:
        target = Path(raw)
        try:
            resolved = target.resolve()
            # Refuse anything that isn't inside a configured download folder.
            if not any(resolved == r or r in resolved.parents for r in roots):
                failed.append({"path": raw, "error": "outside your download folders"})
                continue
            if resolved.is_dir():
                shutil.rmtree(resolved)
            elif resolved.is_file():
                resolved.unlink()
            else:
                failed.append({"path": raw, "error": "not found"})
                continue
            removed.append(raw)
            mapping.pop(raw, None)
        except OSError as exc:
            failed.append({"path": raw, "error": str(exc)[:120]})
    _save_covers(mapping)
    return {"removed": len(removed), "failed": failed}


# Handed to an emulator ahead of anything else in the folder. A .cue or .m3u
# describes the disc that the .bin files beside it only hold pieces of, so
# opening the wrong one gets you a black screen or a single track.
LAUNCH_PREFERENCE = ("m3u", "cue", "gdi", "chd", "iso", "rvz", "wbfs", "cso",
                     "pbp", "nsp", "xci", "3ds", "cia", "wad", "gcm", "nds")


def playable_file(path: str) -> Path | None:
    """The file to hand an emulator for this library entry.

    A game that was never extracted is already the file. An extracted one is a
    folder, and which file inside it counts is not obvious - hence the order
    above, with size as the tie-break so a multi-disc set opens its biggest
    track rather than a stray readme that happens to sort first.
    """
    target = Path(path)
    if target.is_file():
        return target
    if not target.is_dir():
        return None

    candidates = []
    try:
        for item in target.rglob("*"):
            if not item.is_file():
                continue
            ext = names.split_extension(item.name)[1].split(".")[-1].lower()
            # A playlist is not a ROM and so is not in ROM_EXTENSIONS - it
            # would be listed as a game of its own in the library, which it
            # isn't. It is exactly what an emulator wants to be handed, though,
            # so it counts here.
            if ext not in ROM_EXTENSIONS and ext not in LAUNCH_PREFERENCE:
                continue
            rank = (LAUNCH_PREFERENCE.index(ext)
                    if ext in LAUNCH_PREFERENCE else len(LAUNCH_PREFERENCE))
            candidates.append((rank, -item.stat().st_size, item))
    except OSError:
        return None
    if not candidates:
        return None
    return min(candidates, key=lambda c: (c[0], c[1]))[2]


def split_arguments(text: str) -> list[str]:
    """Split a typed argument string the way a shell would, minus the escaping.

    `posix=False` is what makes this usable on Windows: in posix mode a
    backslash is an escape character, so `-L C:\\cores\\x.dll` would come back
    mangled. The trade-off is that quotes survive as part of the token, so they
    are stripped here.
    """
    out = []
    for token in shlex.split(text or "", posix=False):
        if len(token) > 1 and token[0] == token[-1] and token[0] in "\"'":
            token = token[1:-1]
        out.append(token)
    return out


def launch(game_path: str, emulator: Path, arguments: str = "") -> dict:
    """Open a game in the program configured for its console.

    The game goes on the end of the command unless the arguments say otherwise
    with `{game}`. That covers both shapes in one field: a plain emulator wants
    `emulator game`, while RetroArch wants its core first -
    `retroarch -L cores\\x_libretro.dll game` - which falls out of appending.
    `{game}` is there for anything that needs the file somewhere in the middle.
    """
    rom = playable_file(game_path)
    if rom is None:
        return {"ok": False, "error": "Could not find a game file to open."}

    extra = split_arguments(arguments)
    if any("{game}" in part for part in extra):
        command = [str(emulator)] + [p.replace("{game}", str(rom)) for p in extra]
    else:
        command = [str(emulator), *extra, str(rom)]

    try:
        subprocess.Popen(command, cwd=str(emulator.parent))  # noqa: S603
    except OSError as exc:
        return {"ok": False, "error": f"Could not start the emulator: {exc}"}
    return {"ok": True, "opened": str(rom), "command": command}


def _folder_size(folder: Path) -> tuple[int, int]:
    """Total bytes and file count inside an extracted game folder."""
    total = count = 0
    try:
        for item in folder.rglob("*"):
            if item.is_file():
                total += item.stat().st_size
                count += 1
    except OSError:
        pass
    return total, count


def _entry(path: Path, console: str, size: int, files: int,
           extracted: bool) -> dict:
    stem = path.name if extracted else names.split_extension(path.name)[0]
    parsed = names.parse(path.name if not extracted else f"{stem}.zip")
    return {
        "name": stem,
        "title": parsed["title"],
        "console": console,
        "regions": parsed["regions"],
        "languages": parsed["languages"],
        "version": parsed["version"],
        "disc": parsed["disc"],
        "tags": parsed["tags"],
        "ext": "" if extracted else names.split_extension(path.name)[1],
        "size": size,
        "files": files,
        "extracted": extracted,
        "path": str(path),
    }


def _has_rom_child(folder: Path) -> bool:
    """True when a folder holds ROM files directly, i.e. it *is* a game
    rather than a folder that merely contains games."""
    try:
        for item in folder.iterdir():
            if item.is_file():
                ext = names.split_extension(item.name)[1].split(".")[-1]
                if ext in ROM_EXTENSIONS:
                    return True
    except OSError:
        pass
    return False


def scan_folder(folder: Path, console: str, exclude: set[str] | None = None,
                depth: int = 0) -> list[dict]:
    """Collect games, descending through folders that only group other folders.

    This is what picks up a library that was already there: layouts like
    `PS2/Game/game.iso` or `PS2/A-M/Game/game.iso` are found, not just files
    sitting directly in the console folder.
    """
    found: list[dict] = []
    if not folder.is_dir():
        return found
    try:
        entries = sorted(folder.iterdir(), key=lambda p: p.name.lower())
    except OSError:
        return found

    for entry in entries:
        if entry.name.lower().endswith(SKIP_SUFFIXES) or entry.name.startswith("."):
            continue
        if entry.is_dir() and entry.name.lower() in SKIP_DIRS:
            continue
        # A console's own folder sits inside the base; it holds games, it
        # isn't one itself.
        if exclude and str(entry).lower() in exclude:
            continue
        try:
            if entry.is_file():
                ext = names.split_extension(entry.name)[1].split(".")[-1]
                if ext in ROM_EXTENSIONS:
                    found.append(_entry(entry, console, entry.stat().st_size,
                                        1, False))
            elif entry.is_dir():
                if _has_rom_child(entry):
                    size, count = _folder_size(entry)
                    found.append(_entry(entry, console, size, count, True))
                elif depth < MAX_DEPTH:
                    found.extend(scan_folder(entry, console, None, depth + 1))
        except OSError:
            continue
    return found


def scan(consoles: list[str]) -> dict:
    """Look through every folder the downloader might have written to."""
    settings = load_settings()
    base = Path(settings["folder"])

    # console -> folder, plus the base itself for anything saved unsorted.
    targets: list[tuple[str, Path]] = [(c, folder_for(c)) for c in consoles]
    console_dirs = {str(path).lower() for _, path in targets}
    if not any(path == base for _, path in targets):
        targets.append(("", base))

    covers = _load_covers()
    games: list[dict] = []
    seen: set[str] = set()
    for console, folder in targets:
        skip = console_dirs if folder == base else None
        for item in scan_folder(folder, console, skip):
            custom = covers.get(item["path"])
            item["cover"] = f"/covers/{custom}" if custom else ""
            # A console folder nested inside the base would otherwise be
            # scanned twice.
            if item["path"] in seen:
                continue
            seen.add(item["path"])
            games.append(item)

    by_console: dict[str, int] = {}
    for game in games:
        label = game["console"] or "Unsorted"
        by_console[label] = by_console.get(label, 0) + 1

    games.sort(key=lambda g: (g["console"] or "￿", g["title"].lower()))
    return {
        "games": games,
        "total": len(games),
        "bytes": sum(g["size"] for g in games),
        "consoles": [{"console": k, "count": v}
                     for k, v in sorted(by_console.items())],
        "base": str(base),
    }
