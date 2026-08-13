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

from . import db, names, played
from .downloads import folder_for, load_settings, safe_name
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

# What a file extension says about the machine it runs on.
#
# Only the ones that mean a single system. `.zip`, `.chd` and `.iso` are left
# out on purpose: they say how a game is packed, not what it is. This is what
# settles a name the index finds on several consoles - "Sonic the Hedgehog"
# exists on five of them, but Sonic the Hedgehog.md is one.
#
# The names are the index's own labels; anything spelled differently here
# simply never matches, and the game stays unsorted rather than going astray.
EXTENSION_CONSOLES = {
    "nes": ("NES/Famicom",), "fds": ("Famicom Disk System",),
    "sfc": ("SNES/Super Famicom",), "smc": ("SNES/Super Famicom",),
    "gba": ("Game Boy Advance",), "gbc": ("Game Boy Color",),
    "gb": ("Game Boy",), "n64": ("Nintendo 64",), "z64": ("Nintendo 64",),
    "v64": ("Nintendo 64",), "nds": ("Nintendo DS",), "dsi": ("Nintendo DSi",),
    "3ds": ("Nintendo 3DS",), "cia": ("Nintendo 3DS",),
    "md": ("Genesis/Mega Drive",), "gen": ("Genesis/Mega Drive",),
    "gg": ("Game Gear",), "sms": ("Master System",), "sg": ("SG-1000",),
    "pce": ("PC Engine/TurboGrafx-16",), "vb": ("Virtual Boy",),
    "min": ("Pokemon Mini",), "ngp": ("Neo Geo Pocket",),
    "ngc": ("Neo Geo Pocket",), "a26": ("Atari 2600",),
    "a78": ("Atari 7800",), "j64": ("Atari Jaguar",),
    "jag": ("Atari Jaguar",), "lnx": ("Atari Lynx",),
    "gcm": ("GameCube",), "gcz": ("GameCube",), "rvz": ("Nintendo Wii",),
    "wbfs": ("Nintendo Wii",), "wad": ("Nintendo Wii",),
    "cso": ("PSP",), "pbp": ("PSP",), "vpk": ("PSP",),
    "d88": ("PC-8000/8800",),
}

# A disc image that is described by another file rather than being the game
# you open. A PlayStation game is a .cue naming one or more .bin tracks; the
# .bin files are halves of a thing, not things. Listing them turns one game
# into three rows in the library, none of which is the row you want to press
# Play on.
TRACK_EXTENSIONS = {"bin", "img", "iso", "ecm", "wav", "mp3", "sub", "ccd"}

# The file that speaks for a group of them, best first. This is also the order
# LAUNCH_PREFERENCE uses to pick what to hand an emulator, for the same reason.
DESCRIPTOR_EXTENSIONS = ("m3u", "cue", "gdi", "ccd", "toc")

# Folders that are never a game, however they turn up. `_internal` is
# PyInstaller's own: it holds base_library.zip, and since a folder containing
# a .zip counts as an extracted game, pointing the download folder at the app
# itself would list the program's insides as a game called "_internal".
SKIP_DIRS = {
    "_internal", "__pycache__", "$recycle.bin", "system volume information",
    # An emulator's own working folders, which sit right beside the games and
    # are full of files carrying ROM extensions: firmware, fonts, shader
    # caches, save states. None of it is a game, and all of it was arriving in
    # the library as one. The Dolphin region folders are here because they
    # hold IPL.bin and the DSP roms, which are .bin like a disc track is.
    "bios", "system", "systems", "firmware", "cache", "caches",
    "shadercache", "shaders", "saves", "savestates", "savedata", "states",
    "screenshots", "log", "logs", "config", "configs", "temp", "tmp",
    "thumbnails", "cheats", "overlays", "database", "cores", "autoconfig",
    "ntsc-j", "ntsc-u", "ntsc-uc", "pal-e", "sys", "dev_hdd0", "dev_flash",
}

# Cache folders are named after a hash, so only the front of the name is
# predictable. RPCS3 fills a drive with these.
SKIP_DIR_PREFIXES = ("ppu-", "spu-", "shader_", ".")

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


def delete_cover_files(games: list[dict]) -> list[str]:
    """Delete the box art this app saved for games that have just been removed.

    Gated on the console's own "Delete covers with the game" switch, and on
    nothing else. Fetching art automatically and letting the app delete art
    are deliberately two separate permissions: a cover folder is very often an
    emulator's shared thumbnails folder that the user has curated by hand, and
    "download these for me" is not consent to "and remove them later". So this
    does nothing at all unless it has been asked for, per console.

    Nothing from the page is used as a path. The console decides the folder -
    the one already configured for it - and the game's name is reduced to a
    filename, so the worst a bad name can do is fail to match anything.
    """
    settings = load_settings()
    allowed = settings.get("cover_delete") or {}
    folders = settings.get("cover_folders") or {}

    gone: list[str] = []
    for game in games:
        console = str(game.get("console") or "")
        chosen = folders.get(console)
        if not console or not chosen or not allowed.get(console):
            continue

        stem = safe_name(str(game.get("name") or "")).strip()
        if not stem or stem == "download":       # nothing usable to look for
            continue
        folder = Path(chosen)
        # Auto-saved covers are always .png, but the same game may also have
        # had one saved by hand into this folder in whatever format it came
        # in, and leaving that behind would put the art of a deleted game
        # under the next one to take its name.
        for suffix in IMAGE_TYPES:
            target = folder / f"{stem}{suffix}"
            try:
                if not target.is_file():
                    continue
                target.unlink()
            except OSError:
                continue
            gone.append(str(target))
    return gone


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
    # The paths as well as the count: whatever cleans up after a deletion has
    # to know which ones actually went, not just how many.
    return {"removed": len(removed), "removedPaths": removed, "failed": failed}


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


def launch(game_path: str, emulator: Path, arguments: str = "",
           core: Path | None = None) -> dict:
    """Open a game in the program configured for its console.

    `core` is RetroArch's `-L`, which is not optional for it: RetroArch on its
    own is a shell with no system to emulate, so without a core it opens its
    own menu and looks, from outside, as though nothing happened. It is passed
    as a path rather than typed into the arguments because that is what it is,
    and a Windows path typed into an argument box has to be quoted correctly to
    survive - which is the part everybody gets wrong.

    The game goes on the end of the command unless the arguments say otherwise
    with `{game}`, which is there for anything that needs the file somewhere in
    the middle rather than last.
    """
    rom = playable_file(game_path)
    if rom is None:
        return {"ok": False, "error": "Could not find a game file to open."}

    lead = ["-L", str(core)] if core else []
    extra = split_arguments(arguments)
    if any("{game}" in part for part in extra):
        command = ([str(emulator), *lead]
                   + [p.replace("{game}", str(rom)) for p in extra])
    else:
        command = [str(emulator), *lead, *extra, str(rom)]

    try:
        subprocess.Popen(command, cwd=str(emulator.parent))  # noqa: S603
    except OSError as exc:
        return {"ok": False, "error": f"Could not start the emulator: {exc}"}
    return {"ok": True, "opened": str(rom), "command": command}


def _folder_size(folder: Path) -> tuple[int, int, tuple[float, float]]:
    """Total bytes, file count, and when this game was last opened.

    The read times ride along with the walk rather than costing a second one:
    the size already needs a stat of every file, and the access time is in the
    same structure. See played.py for what is made of it.
    """
    total = count = 0
    reads: list[tuple[str, float, float]] = []
    try:
        for item in folder.rglob("*"):
            if item.is_file():
                st = item.stat()
                total += st.st_size
                count += 1
                reads.append((item.name, st.st_atime, st.st_mtime))
    except OSError:
        pass
    return total, count, played.best_read(reads)


def _entry(path: Path, console: str, size: int, files: int,
           extracted: bool, read: tuple[float, float] = (0.0, 0.0)) -> dict:
    stem = path.name if extracted else names.split_extension(path.name)[0]
    parsed = names.parse(path.name if not extracted else f"{stem}.zip")
    return {
        # When this game was last read, and last written. Both are stripped
        # again by played.detect() once it has turned them into a verdict -
        # the page is given the answer, not the workings.
        "_atime": read[0],
        "_mtime": read[1],
        "name": stem,
        "title": parsed["title"],
        # How the index spells this title, so a game with no console folder to
        # name it can be looked up there instead of landing in "Unsorted".
        "title_norm": parsed["title_norm"],
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


def _referenced_files(descriptor: Path) -> set[str]:
    """The filenames a .cue, .m3u or .gdi points at, lowercased.

    Only names are taken, never paths: a malformed or hand-edited descriptor
    can say anything at all, and the only use made of this is deciding which
    files *beside it* are its tracks. Nothing is opened, moved or deleted on
    the strength of it.
    """
    try:
        text = descriptor.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return set()

    found: set[str] = set()
    for line in text.splitlines()[:400]:      # a sane cue is a handful of lines
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.upper().startswith("FILE "):
            # FILE "Game (Track 1).bin" BINARY - or unquoted, on old rippers.
            rest = line[5:].strip()
            name = (rest.split('"')[1] if '"' in rest
                    else rest.rsplit(" ", 1)[0].strip())
        else:
            name = line                        # .m3u and .gdi list them plainly
        name = name.replace("\\", "/").rsplit("/", 1)[-1].strip().lower()
        if name:
            found.add(name)
    return found


def _group_siblings(files: list[Path]) -> list[list[Path]]:
    """Fold loose files in one folder into the games they make up.

    Two things get folded. A descriptor and the tracks it names - the usual
    PlayStation `Game.cue` plus `Game (Track 1).bin` - and files that differ
    only by extension, which is the same game ripped or packed twice.

    The first file of each group is the one to show and the one to open.
    """
    by_name = {f.name.lower(): f for f in files}
    claimed: set[str] = set()
    groups: list[list[Path]] = []
    opened: dict[str, list[Path]] = {}   # stem -> the group a descriptor began

    # Descriptors first, so their tracks are spoken for before anything else
    # tries to group them by name. Longest suffix first: an .m3u names the
    # .cue files, so it has to claim them before they claim their own tracks.
    for kind in DESCRIPTOR_EXTENSIONS:
        for path in files:
            if path.name.lower() in claimed:
                continue
            if names.split_extension(path.name)[1].split(".")[-1].lower() != kind:
                continue
            group = [path]
            claimed.add(path.name.lower())
            for ref in _referenced_files(path):
                target = by_name.get(ref)
                if target is not None and ref not in claimed:
                    claimed.add(ref)
                    group.append(target)
            groups.append(group)
            opened.setdefault(names.split_extension(path.name)[0].lower(), group)

    # Then whatever is left, by name without its extension. A leftover that
    # shares a descriptor's name joins it: `Game.cue` beside `Game.bin` is one
    # game whether or not the cue could be read, and a cue that names its
    # track with a path this app can't resolve must not strand the .bin as a
    # game of its own.
    by_stem: dict[str, list[Path]] = {}
    for path in files:
        if path.name.lower() in claimed:
            continue
        stem = names.split_extension(path.name)[0].lower()
        owner = opened.get(stem)
        if owner is not None:
            owner.append(path)
            claimed.add(path.name.lower())
            continue
        by_stem.setdefault(stem, []).append(path)

    for group in by_stem.values():
        for part in _split_by_console(group):
            # A .chd beats the .bin it was made from; anything named in
            # LAUNCH_PREFERENCE beats anything not, and size breaks the rest.
            part.sort(key=lambda p: (_launch_rank(p), -_size_of(p)))
            groups.append(part)
    return groups


def _split_by_console(group: list[Path]) -> list[list[Path]]:
    """Same name, still two games.

    `Aladdin (USA).gba` and `Aladdin (USA).md` are the Game Boy Advance and
    Mega Drive versions, and folding them into one row loses a game. Only
    extensions that name a machine split a group: `.zip` beside `.gba` is one
    game that happens to be here twice, so anything that says nothing about
    the machine leaves the group alone.
    """
    implied = [EXTENSION_CONSOLES.get(
        names.split_extension(p.name)[1].split(".")[-1].lower(), ()) for p in group]
    if len(set(implied)) <= 1 or not all(implied):
        return [group]
    buckets: dict[tuple, list[Path]] = {}
    for path, machine in zip(group, implied):
        buckets.setdefault(machine, []).append(path)
    return list(buckets.values())


def _size_of(path: Path) -> int:
    try:
        return path.stat().st_size
    except OSError:
        return 0


def _launch_rank(path: Path) -> int:
    ext = names.split_extension(path.name)[1].split(".")[-1].lower()
    if ext in LAUNCH_PREFERENCE:
        return LAUNCH_PREFERENCE.index(ext)
    # A bare track sorts last: it is part of a game, not the game.
    return len(LAUNCH_PREFERENCE) + (1 if ext in TRACK_EXTENSIONS else 0)


def _skip_dir(name: str) -> bool:
    """Folders that are never a game, however they turn up."""
    lowered = name.lower()
    return lowered in SKIP_DIRS or lowered.startswith(SKIP_DIR_PREFIXES)


def _rom_children(folder: Path) -> list[Path]:
    """The ROM files sitting directly inside a folder."""
    out = []
    try:
        for item in folder.iterdir():
            if not item.is_file() or item.name.startswith("."):
                continue
            if item.name.lower().endswith(SKIP_SUFFIXES):
                continue
            ext = names.split_extension(item.name)[1].split(".")[-1].lower()
            if ext in ROM_EXTENSIONS:
                out.append(item)
    except OSError:
        pass
    return out


def _folder_role(folder: Path) -> str:
    """Whether a folder is one game, or somewhere games are kept.

    "Holds a ROM file" is not the same question, and answering that one is
    what put `NES Jogos` in the library as a single game called "NES Jogos"
    while the hundred games inside it went unlisted. A folder is a game only
    when the files in it add up to exactly one - an extracted archive, or a
    disc rip whose .cue names its tracks. Anything else is a shelf, and is
    walked into.

    Returns "game", "shelf" or "none".
    """
    files = _rom_children(folder)
    if not files:
        return "none"
    groups = _group_siblings(files)
    if len(groups) == 1:
        return "game"
    # An extracted archive names its parts after the folder they are in:
    # `Game (USA)/Game (USA) (Track 1).bin`. When a .cue cannot be read - it
    # names its tracks by a path, or it is simply damaged - those parts stay
    # ungrouped, and splitting one game into its tracks is a worse answer than
    # trusting the shape of the names.
    stem = folder.name.lower()
    if all(_names_a_part_of(g[0].name, stem) for g in groups):
        return "game"
    return "shelf"


def _names_a_part_of(filename: str, stem: str) -> bool:
    """`Game (USA) (Track 1).bin` is part of `Game (USA)`; `Sonic 2.md` is not
    part of `Sonic`. What follows the folder's name has to be a bracketed
    qualifier, not a different title that happens to start the same way."""
    # Extension off first: what is left of `Game (USA).cue` after the folder's
    # own name is `.cue`, and asking split_extension about a string that is
    # nothing but an extension does not give the empty remainder this wants.
    base = names.split_extension(filename)[0].lower()
    if not base.startswith(stem):
        return False
    rest = base[len(stem):].strip()
    return rest == "" or rest.startswith("(")


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

    # Loose files are decided together rather than one at a time: whether a
    # .bin is a game or one track of the .cue beside it is a question about
    # the folder, not about the file.
    loose: list[Path] = []

    for entry in entries:
        if entry.name.lower().endswith(SKIP_SUFFIXES) or entry.name.startswith("."):
            continue
        if entry.is_dir() and _skip_dir(entry.name):
            continue
        # A console's own folder sits inside the base, and an emulator's
        # folder may too: neither is a game. Carried down the recursion, not
        # just checked at the top, since either can be nested.
        if exclude and str(entry).lower() in exclude:
            continue
        try:
            if entry.is_file():
                ext = names.split_extension(entry.name)[1].split(".")[-1]
                if ext in ROM_EXTENSIONS:
                    loose.append(entry)
            elif entry.is_dir():
                role = _folder_role(entry)
                if role == "game":
                    size, count, read = _folder_size(entry)
                    found.append(_entry(entry, console, size, count, True, read))
                elif depth < MAX_DEPTH:
                    # A shelf, or a folder with nothing of ours in it at all.
                    found.extend(scan_folder(entry, console, exclude, depth + 1))
        except OSError:
            continue

    for group in _group_siblings(loose):
        best = group[0]
        # One stat per file, used for both answers. Size and read time come
        # out of the same structure, and a library of forty thousand games is
        # not the place to ask the disk the same question twice.
        size = 0
        reads: list[tuple[str, float, float]] = []
        for p in group:
            try:
                st = p.stat()
            except OSError:
                continue
            size += st.st_size
            reads.append((p.name, st.st_atime, st.st_mtime))
        # The whole group, because a .cue's tracks are siblings rather than
        # anything inside a folder - and the tracks are the files an emulator
        # actually reads.
        found.append(_entry(best, console, size, len(group), False,
                            played.best_read(reads)))
    return found


def _emulator_dirs(settings: dict) -> set[str]:
    """The folders the user's emulators live in.

    An emulator installed inside the download folder is a thousand files with
    ROM extensions that are not games - firmware, caches, the lot - and the
    surest way to know which folder is an emulator's is that the user already
    told us, by picking the program in Settings. A core is inside `cores/`,
    so its grandparent is the install.
    """
    out: set[str] = set()
    for value in (settings.get("emulators") or {}).values():
        exe = Path(str(value))
        if exe.name:
            out.add(str(exe.parent).lower())
    for value in (settings.get("emulator_cores") or {}).values():
        core = Path(str(value))
        if core.name and core.parent.name:
            out.add(str(core.parent).lower())
            out.add(str(core.parent.parent).lower())
    out.discard("")
    out.discard(".")
    return out


def sort_by_index(conn, games: list[dict]) -> int:
    """Give every console-less game the console the index says it is on.

    Being in the main folder rather than a console folder is the *only* reason
    a game is "Unsorted", and for a collection that was there before the app -
    or one downloaded with per-console folders switched off - that is nearly
    all of it. Nothing about the folder can answer this; the index can, and it
    already has to be present for the app to be any use at all.

    Returns how many were placed. The rest keep their empty console and are
    shown as Unsorted, which is now a much shorter list of things that really
    are unidentifiable.
    """
    if conn is None:
        return 0
    loose = [g for g in games if not g["console"] and g.get("title_norm")]
    if not loose:
        return 0

    try:
        candidates = db.consoles_for_titles(conn, [g["title_norm"] for g in loose])
    except Exception:  # noqa: BLE001 - a bad index must not empty the library
        return 0

    placed = 0
    for game in loose:
        slot = candidates.get(game["title_norm"])
        if not slot:
            continue
        ext = (game.get("ext") or "").lstrip(".").lower()
        # In order of how much each question is worth. A name that is only on
        # one machine needs no help; after that, what the extension means; and
        # last, how the index happens to serve that game, which separates the
        # PlayStation .chd sets from the .zip ones.
        for options in (slot.get(""),
                        slot.get("", set()) & set(EXTENSION_CONSOLES.get(ext, ())),
                        slot.get(ext)):
            if options and len(options) == 1:
                game["console"] = next(iter(options))
                placed += 1
                break
    return placed


def scan(consoles: list[str], conn=None) -> dict:
    """Look through every folder the downloader might have written to."""
    settings = load_settings()
    base = Path(settings["folder"])

    # console -> folder, plus the base itself for anything saved unsorted.
    targets: list[tuple[str, Path]] = [(c, folder_for(c)) for c in consoles]
    console_dirs = {str(path).lower() for _, path in targets}
    emulator_dirs = _emulator_dirs(settings)
    if not any(path == base for _, path in targets):
        targets.append(("", base))

    covers = _load_covers()
    games: list[dict] = []
    seen: set[str] = set()
    for console, folder in targets:
        # A console's folder is only "not a game" while scanning the base it
        # sits inside. An emulator's folder is never a game, wherever it is.
        skip = (console_dirs | emulator_dirs) if folder == base else emulator_dirs
        for item in scan_folder(folder, console, skip):
            custom = covers.get(item["path"])
            item["cover"] = f"/covers/{custom}" if custom else ""
            # A console folder nested inside the base would otherwise be
            # scanned twice.
            if item["path"] in seen:
                continue
            seen.add(item["path"])
            games.append(item)

    # Turns the access times gathered above into a "you played this" verdict,
    # and takes the raw stats back off. Has to run over the whole library at
    # once rather than per game, because telling a play from a virus scan is a
    # question about how many games were touched together.
    detected = played.detect(games)

    # Before the counting: what console a game is on decides which heading it
    # sits under and how the whole list is grouped.
    sorted_by_index = sort_by_index(conn, games)

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
        # How many were placed by name rather than by the folder they were in.
        "sorted_by_index": sorted_by_index,
        # Games that look played from the outside, and whether this machine
        # records the reads that would show it. The second one is what lets
        # the page explain an empty row instead of just having one.
        "played_found": detected,
        "reads_tracked": played.tracking_enabled(),
    }
