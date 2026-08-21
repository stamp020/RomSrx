"""Background download queue with resume, retry and progress reporting.

Downloads run in worker threads inside this app - no browser involved. Files
are written to a `.part` file and renamed on completion, so an interrupted
transfer resumes from where it stopped instead of starting over.

archive.org intermittently answers 500 on perfectly valid requests (the same
URL will succeed moments later), so transient failures are retried with a
backoff rather than being treated as fatal.
"""

from __future__ import annotations

import json
import os
import queue
import re
import shutil
import subprocess
import sys
import threading
import time
import zipfile
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

from . import paths as _paths
from . import state

CHUNK = 256 * 1024
RETRIES = 5
RETRY_BASE = 2.0          # seconds; doubles each attempt

# Watching for a connection that has gone bad. The window is long enough that
# an ordinary lull - a pause while the disk catches up, a moment of
# congestion - cannot trip it.
SLOW_WINDOW = 45.0        # seconds of evidence before believing it
SLOW_SHARE = 0.25         # ...and this much of the best it has managed
SLOW_GIVEUP = 3           # reconnections for slowness, per download
# Nothing at all for this long is a dead connection whatever the history.
STALL_SECONDS = 90.0
TRANSIENT = {408, 425, 429, 500, 502, 503, 504}
_paths.migrate_user_files(("settings.json", "covers.json"))
SETTINGS_PATH = _paths.user("settings.json")
DEFAULT_FOLDER = str(Path.home() / "Downloads" / "RomSrx")

# How many downloads may run at once. archive.org rate-limits heavy use, so
# more connections mostly buy errors and retries rather than speed.
MAX_WORKERS = 5
DEFAULT_WORKERS = 3

# Only formats we can unpack without an external binary. Everything else in
# the index (chd, iso, wbfs, rvz, wad) is already the playable ROM.
ARCHIVES = {".zip", ".7z"}

_INVALID = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


def safe_name(name: str) -> str:
    """Make a filename Windows-safe without mangling the readable parts."""
    cleaned = _INVALID.sub("_", name).strip(" .")
    return cleaned or "download"


# Bumped every time the settings are written. A reader holding a cached copy
# compares it and knows in one integer whether it is looking at the current
# answer - which is what lets the download loop stop opening the file for
# every chunk without ever acting on a stale setting.
_settings_stamp = 0


def load_settings() -> dict:
    try:
        with open(SETTINGS_PATH, encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError):
        data = {}
    data.setdefault("folder", DEFAULT_FOLDER)
    data.setdefault("workers", 3)
    data.setdefault("extract", True)
    # "folder" puts each archive in one of its own, named after it; "here"
    # unpacks straight into the download folder.
    data.setdefault("extract_mode", "folder")
    data.setdefault("delete_archive", True)
    # Where downloaded patches are kept. Blank means a "Patches" folder beside
    # the downloads, which is where someone would look for them first.
    data.setdefault("patch_folder", "")
    # Off by default: patching should not delete anything unless asked to.
    data.setdefault("patch_replace", False)
    # Which copy of a game is offered first when a title exists in six of
    # them. Best first; anything not named sorts after everything that is.
    data.setdefault("region_priority", ["USA", "Europe"])
    data.setdefault("cover_folders", {})    # console -> where covers are saved
    # console -> fetch the box art too, the moment a game for it lands. Only
    # useful where a cover folder is set, since that is the only place the
    # image could go without asking.
    data.setdefault("cover_auto", {})
    # console -> take the cover away again when the game is deleted from the
    # app. Separate from cover_auto on purpose: fetching art automatically and
    # letting the app delete art are two different amounts of trust, and a
    # cover folder is very often an emulator's shared thumbnails folder that
    # the user curates by hand. Off unless it is asked for.
    data.setdefault("cover_delete", {})
    data.setdefault("emulators", {})        # console -> the program to open games with
    # console -> the libretro core file. RetroArch needs "-L <core>" telling
    # it which system to emulate, and the program alone opens nothing. It is a
    # path, so it gets a box and a picker of its own rather than being typed
    # into the arguments by hand, quoting and all.
    data.setdefault("emulator_cores", {})
    # console -> anything else that program wants, typed as you would type it.
    data.setdefault("emulator_args", {})
    # One game doing its own thing: path -> {emulator, core, args}. Keyed by
    # path because that is what the library and the launcher both already
    # have in hand; a game that moves loses its override, which is the same
    # thing that happens to its cover and its play time.
    data.setdefault("game_overrides", {})
    data.setdefault("per_console", False)   # base/<console> automatically
    data.setdefault("console_folders", {})  # explicit per-console overrides
    data.setdefault("clear_when_done", False)  # tidy the list as things land
    # A ceiling on the whole app in kilobytes a second, 0 for no limit. Shared
    # across the workers rather than applied per download, because what
    # somebody wants capped is the line, not each transfer.
    data.setdefault("speed_limit", 0)
    # Stop pulling while a game is running. The app is the thing that launched
    # it, so unlike a general-purpose downloader it actually knows - and a
    # 6GB disc image arriving in the background is felt by anything online.
    data.setdefault("pause_while_playing", False)
    data["workers"] = _sane_workers(data["workers"])
    return data


def _sane_speed(value) -> int:
    """Kilobytes a second, or 0 for no ceiling.

    Anything unreadable, negative, or below a floor that would make the app
    look broken becomes 0. The floor matters: at 8 KB/s a disc image takes a
    fortnight, and somebody who typed that meant to type something else.
    """
    try:
        speed = int(float(value))
    except (TypeError, ValueError):
        return 0
    if speed <= 0:
        return 0
    return max(32, min(speed, 1_000_000))


def _sane_workers(value) -> int:
    """Always one of the choices the app offers.

    Older builds allowed up to 10, and a 0 meaning "unlimited". Both are still
    sitting in settings files, and either would leave the control showing
    nothing - so they land on the nearest thing that still exists.
    """
    try:
        workers = int(value)
    except (TypeError, ValueError):
        return DEFAULT_WORKERS
    if workers <= 0:            # the old "unlimited": as many as we now allow
        return MAX_WORKERS
    return min(workers, MAX_WORKERS)


_cart_lock = threading.Lock()


def forget_from_cart(url: str) -> None:
    """Drop a finished download from the saved list, if that's switched on.

    Done here rather than in the page so it still happens for downloads that
    finish while the list isn't open - and the lock is because several workers
    can finish at the same moment, and the list is a whole-file rewrite.
    """
    if not load_settings().get("clear_when_done"):
        return
    with _cart_lock:
        items = state.cart()
        keep = [i for i in items if i.get("url") != url]
        if len(keep) != len(items):
            state.set_cart(keep)


def console_dir_name(console: str) -> str:
    """A console name as a folder name. Several contain a slash, which would
    otherwise create an unintended nested folder."""
    return safe_name(console.replace("/", "-").replace("\\", "-"))


def relative_to_base(path: str, base: str) -> str:
    """Store a path inside the base folder as a relative one.

    Keeping it relative means the whole library moves when the main folder
    changes, instead of every console staying pinned to the old location.
    Paths outside the base are left absolute on purpose.
    """
    try:
        target, root = Path(path), Path(base)
        if target.is_absolute() and root.is_absolute():
            return str(target.relative_to(root))
    except (ValueError, OSError):
        pass
    return path


def _free_on(folder: Path) -> int:
    """Bytes free on the disk this folder is on, or -1 if it cannot be asked.

    Walks up to the nearest parent that exists: the folder a console downloads
    into is very often one this app has not created yet, and "the drive it
    would be on" is the question, not "does the folder exist".
    """
    where = folder
    for _ in range(8):
        try:
            return shutil.disk_usage(where).free
        except OSError:
            parent = where.parent
            if parent == where:
                return -1
            where = parent
    return -1


def space_for(items) -> dict:
    """Whether what is about to be queued will fit.

    Grouped by the folder each console lands in, because with a folder per
    console a batch can span two drives and "you have 18 GB free" would be
    the wrong answer about one of them.

    An archive is unpacked where it lands, and for a while both the .zip and
    what came out of it are on the disk at once - so the room needed is more
    than the download. A rule of thumb rather than a measurement, because the
    only way to know is to unpack it: doubled for anything that will be
    extracted, which is the honest worst case.
    """
    settings = load_settings()
    extracting = bool(settings.get("extract", True))
    keeping = not settings.get("delete_archive", True)

    wanted: dict[str, int] = {}
    for item in items or []:
        if not isinstance(item, dict):
            continue
        try:
            size = max(0, int(item.get("size") or 0))
        except (TypeError, ValueError):
            size = 0
        ext = str(item.get("ext") or "").lower().lstrip(".")
        if extracting and ext in ("zip", "7z"):
            size = size * 2 if keeping else int(size * 1.6)
        folder = str(folder_for(str(item.get("console") or "")))
        wanted[folder] = wanted.get(folder, 0) + size

    drives = []
    for folder, need in sorted(wanted.items()):
        free = _free_on(Path(folder))
        drives.append({"folder": folder, "need": need, "free": free,
                       "short": free >= 0 and need > free})
    return {"drives": drives, "ok": not any(d["short"] for d in drives)}


def folder_for(console: str) -> Path:
    """Where a file for this console should land.

    An override wins - relative ones hang off the base folder, absolute ones
    point wherever they say. Otherwise per-console mode appends the console
    name to the base, and failing that everything shares the base.
    """
    settings = load_settings()
    base = Path(settings["folder"])
    override = (settings.get("console_folders") or {}).get(console)
    if override:
        chosen = Path(override)
        return chosen if chosen.is_absolute() else base / chosen
    if settings.get("per_console") and console:
        return base / console_dir_name(console)
    return base


def cover_folder_for(console: str) -> Path | None:
    """Where covers for this console are saved without asking, if anywhere.

    Only an exact match counts. There is no falling back to some general
    covers folder on purpose: writing a PlayStation cover into the PS2
    thumbnails folder because that was the only one set would be worse than
    asking, and the whole feature is about trusting where things land.
    """
    if not console:
        return None
    chosen = (load_settings().get("cover_folders") or {}).get(console)
    return Path(chosen) if chosen else None


def override_for(game_path: str) -> dict:
    """What this one game has been told to use, if anything."""
    if not game_path:
        return {}
    found = (load_settings().get("game_overrides") or {}).get(str(game_path))
    return found if isinstance(found, dict) else {}


def emulator_for(console: str, game_path: str = "") -> Path | None:
    """The program to open this game with: its own, or its console's."""
    own = override_for(game_path).get("emulator")
    if own:
        exe = Path(own)
        return exe if exe.is_file() else None
    if not console:
        return None
    chosen = (load_settings().get("emulators") or {}).get(console)
    if not chosen:
        return None
    exe = Path(chosen)
    return exe if exe.is_file() else None


def emulator_core_for(console: str, game_path: str = "") -> Path | None:
    """The core to load: this game's own, or its console's."""
    own = override_for(game_path).get("core")
    if own:
        core = Path(own)
        return core if core.is_file() else None
    if not console:
        return None
    chosen = (load_settings().get("emulator_cores") or {}).get(console)
    if not chosen:
        return None
    core = Path(chosen)
    return core if core.is_file() else None


def emulator_args_for(console: str, game_path: str = "") -> str:
    """Extra arguments: this game's own, or its console's."""
    own = override_for(game_path)
    # An override that sets an emulator but no arguments means no arguments -
    # the console's are for the console's program, and passing them to a
    # different one is how you get a launcher that fails silently.
    if own.get("emulator") or own.get("core"):
        return own.get("args", "")
    if not console:
        return ""
    return (load_settings().get("emulator_args") or {}).get(console, "")


def _resolve_override(value: str, base: Path) -> Path:
    """Where a stored console folder actually is. Relative ones hang off the
    base, exactly as folder_for() reads them."""
    chosen = Path(value)
    return chosen if chosen.is_absolute() else base / chosen


def _search_roots(base: Path, overrides: dict) -> list[Path]:
    """Every folder worth looking inside for console folders.

    The main folder, obviously - but a collection is very often somewhere else
    entirely, and split across drives at that. If one console is already
    pointed at `D:\\Roms\\PlayStation`, then `D:\\Roms` is a place this user
    keeps consoles, and the rest of them are probably sitting in it. So the
    parent of every folder already configured is searched too.
    """
    roots: list[Path] = [base]
    seen = {str(base).lower()}
    for value in overrides.values():
        if not value:
            continue
        parent = _resolve_override(str(value), base).parent
        key = str(parent).lower()
        if key not in seen and parent.is_dir():
            seen.add(key)
            roots.append(parent)
    return roots


def relink_console_folders(consoles: list[str]) -> dict:
    """Find, re-find and repair the folder each console keeps its games in.

    For a library sorted into per-console folders that the app has no record
    of - an older version, a reinstall, or folders made by hand - the games
    are on disk in the right place and only the app doesn't know it, so they
    all arrive in the library as "Unsorted".

    Three things happen, per console:

      * no folder set, one found      -> linked
      * folder set but no longer there-> repaired, if a replacement is found
      * folder set and still there    -> left exactly alone

    Nothing on disk is moved, renamed or deleted, and a path that is still
    valid is never second-guessed. Undo is "Clear all".
    """
    settings = load_settings()
    base = Path(settings["folder"])
    overrides = dict(settings.get("console_folders") or {})

    roots = _search_roots(base, overrides)
    # name -> full path, first root wins so the main folder takes precedence.
    on_disk: dict[str, Path] = {}
    unreadable = 0
    for root in roots:
        try:
            for path in root.iterdir():
                if path.is_dir():
                    on_disk.setdefault(path.name.lower(), path)
        except OSError:
            unreadable += 1

    if not on_disk and unreadable:
        return {"linked": 0, "repaired": 0, "kept": 0, "consoles": [],
                "repairedConsoles": [], "roots": [str(r) for r in roots],
                "error": "Could not read the download folders."}

    linked, repaired, kept = [], [], 0
    for console in consoles:
        if not console:
            continue
        current = overrides.get(console)
        if current and _resolve_override(str(current), base).is_dir():
            kept += 1
            continue

        match = on_disk.get(console_dir_name(console).lower())
        if match is None:
            continue
        # Inside the main folder it is stored relative, so the whole library
        # still moves when the main folder does; anywhere else stays absolute.
        try:
            value = str(match.relative_to(base))
        except ValueError:
            value = str(match)
        overrides[console] = value
        (repaired if current else linked).append(console)

    if linked or repaired:
        save_settings({"console_folders": overrides})
    return {"linked": len(linked), "repaired": len(repaired), "kept": kept,
            "consoles": linked, "repairedConsoles": repaired,
            "roots": [str(r) for r in roots]}


def save_settings(data: dict) -> dict:
    current = load_settings()
    allowed = ("folder", "workers", "extract", "extract_mode", "delete_archive",
               "per_console", "clear_when_done", "patch_folder", "patch_replace",
               "speed_limit", "pause_while_playing")
    current.update({k: v for k, v in data.items() if k in allowed})
    # Checked here rather than trusted: these end up in an ORDER BY, and
    # db.region_rank_sql writes them into SQL rather than binding them.
    if isinstance(data.get("region_priority"), list):
        from . import db  # noqa: PLC0415 - only for the one check
        current["region_priority"] = [
            r for r in data["region_priority"]
            if isinstance(r, str) and db._REGION_OK.match(r)][:6]
    if "console_folders" in data and isinstance(data["console_folders"], dict):
        # Blank entries mean "fall back to the default", so drop them. Anything
        # inside the base folder is stored relative so it follows the base.
        base = current["folder"]
        current["console_folders"] = {
            k: relative_to_base(str(v).strip(), base)
            for k, v in data["console_folders"].items() if str(v).strip()
        }
    if "game_overrides" in data and isinstance(data["game_overrides"], dict):
        current["game_overrides"] = {
            str(k): {f: str(v.get(f) or "") for f in ("emulator", "core", "args")}
            for k, v in data["game_overrides"].items() if isinstance(v, dict)
        }
    for key in ("emulators", "emulator_cores", "emulator_args"):
        if key in data and isinstance(data[key], dict):
            current[key] = {
                k: str(v).strip() for k, v in data[key].items() if str(v).strip()
            }
    for key in ("cover_auto", "cover_delete"):
        # Booleans, and only the ones switched on - an off toggle is the
        # absence of a key rather than a false sitting in the file forever.
        if key in data and isinstance(data[key], dict):
            current[key] = {k: True for k, v in data[key].items() if v}
    if "cover_folders" in data and isinstance(data["cover_folders"], dict):
        # Always absolute: covers usually live with an emulator's thumbnails,
        # nowhere near the downloads, so there is no base to be relative to.
        current["cover_folders"] = {
            k: str(v).strip() for k, v in data["cover_folders"].items()
            if str(v).strip()
        }
    current["per_console"] = bool(current["per_console"])
    current["extract"] = bool(current["extract"])
    if current["extract_mode"] not in ("folder", "here"):
        current["extract_mode"] = "folder"
    current["delete_archive"] = bool(current["delete_archive"])
    current["clear_when_done"] = bool(current["clear_when_done"])
    current["workers"] = _sane_workers(current["workers"])
    current["speed_limit"] = _sane_speed(current.get("speed_limit"))
    with open(SETTINGS_PATH, "w", encoding="utf-8") as fh:
        json.dump(current, fh, indent=2)
    # Anything holding a cached copy is now looking at the old answer.
    global _settings_stamp  # noqa: PLW0603 - one counter for the process
    _settings_stamp += 1
    manager.ensure_workers(current["workers"])
    return current


def patch_folder() -> Path:
    """Where downloaded patches are kept.

    Beside the downloads by default rather than in the app's own folder: a
    patch is something the user goes looking for later, and it belongs next to
    the games it is for, not somewhere only the app knows about.
    """
    settings = load_settings()
    chosen = str(settings.get("patch_folder") or "").strip()
    if chosen:
        return Path(chosen)
    return Path(settings["folder"]) / "Patches"


def browse_folder(start: str = "") -> str | None:
    """Native folder picker. Runs Tk on its own thread so it can't clash
    with the app's UI loop; returns None if the user cancels."""
    result: list[str | None] = [None]

    def ask():
        try:
            import tkinter  # noqa: PLC0415
            from tkinter import filedialog  # noqa: PLC0415
            root = tkinter.Tk()
            root.withdraw()
            root.attributes("-topmost", True)
            chosen = filedialog.askdirectory(
                initialdir=start or load_settings()["folder"],
                title="Choose where to save downloads")
            root.destroy()
            result[0] = chosen or None
        except Exception:  # noqa: BLE001 - no display, no tkinter, cancelled
            result[0] = None

    thread = threading.Thread(target=ask)
    thread.start()
    thread.join(timeout=180)
    return result[0]


def _remove_file(path: Path, attempts: int = 12, delay: float = 0.25) -> bool:
    """Delete a file, allowing for Windows holding it briefly.

    A worker closes its handle a moment after it stops, and Windows refuses
    to unlink an open file, so a single attempt can fail on a race.
    """
    for _ in range(attempts):
        try:
            if not path.exists():
                return False
            path.unlink()
            return True
        except OSError:
            time.sleep(delay)
    return False


def browse_patchable(kind: str = "game", start: str = "") -> str | None:
    """Native file picker for the patch tool: a game, or a patch to put on it.

    Two lists rather than one, because the two questions have different right
    answers and a picker offering every file on the machine is no help with
    either.
    """
    if kind == "patch":
        title = "Choose a patch"
        kinds = [("Patches", "*.bps *.ips *.xdelta *.vcdiff *.ppf *.zip *.7z"),
                 ("All files", "*.*")]
    else:
        title = "Choose a game to patch"
        kinds = [("Games", "*.nes *.sfc *.smc *.gb *.gbc *.gba *.md *.gen "
                           "*.n64 *.z64 *.nds *.iso *.img *.bin *.zip"),
                 ("All files", "*.*")]

    result: list[str | None] = [None]

    def ask():
        try:
            import tkinter  # noqa: PLC0415
            from tkinter import filedialog  # noqa: PLC0415
            root = tkinter.Tk()
            root.withdraw()
            root.attributes("-topmost", True)
            chosen = filedialog.askopenfilename(
                initialdir=start or load_settings()["folder"],
                title=title, filetypes=kinds)
            root.destroy()
            result[0] = chosen or None
        except Exception:  # noqa: BLE001 - cancelled, or no display
            result[0] = None

    thread = threading.Thread(target=ask)
    thread.start()
    thread.join(timeout=180)
    return result[0]


def browse_image(start: str = "") -> str | None:
    """Native file picker for choosing a cover image."""
    result: list[str | None] = [None]

    def ask():
        try:
            import tkinter  # noqa: PLC0415
            from tkinter import filedialog  # noqa: PLC0415
            root = tkinter.Tk()
            root.withdraw()
            root.attributes("-topmost", True)
            chosen = filedialog.askopenfilename(
                initialdir=start or str(Path.home()),
                title="Choose a cover image",
                filetypes=[("Images", "*.png *.jpg *.jpeg *.webp *.gif *.bmp"),
                           ("All files", "*.*")])
            root.destroy()
            result[0] = chosen or None
        except Exception:  # noqa: BLE001 - cancelled or no display
            result[0] = None

    thread = threading.Thread(target=ask)
    thread.start()
    thread.join(timeout=180)
    return result[0]


# What each picker is looking for. Per-platform because only Windows uses an
# extension to mean "this is a program", and a libretro core is a shared
# library whose suffix differs on every one of the three.
_CORE_SUFFIX = {"win32": "*.dll", "darwin": "*.dylib"}


def _file_filters(kind: str) -> list[tuple[str, str]]:
    if kind == "core":
        return [("Libretro cores", _CORE_SUFFIX.get(sys.platform, "*.so")),
                ("All files", "*.*")]
    if sys.platform == "win32":
        return [("Programs", "*.exe"), ("All files", "*.*")]
    return [("All files", "*.*")]


def browse_exe(start: str = "", kind: str = "program") -> str | None:
    """Native picker for an emulator, or for the core it needs."""
    result: list[str | None] = [None]
    title = ("Choose the libretro core" if kind == "core"
             else "Choose the emulator")

    def ask():
        try:
            import tkinter  # noqa: PLC0415
            from tkinter import filedialog  # noqa: PLC0415
            root = tkinter.Tk()
            root.withdraw()
            root.attributes("-topmost", True)
            chosen = filedialog.askopenfilename(
                initialdir=start or str(Path.home()),
                title=title, filetypes=_file_filters(kind))
            root.destroy()
            result[0] = chosen or None
        except Exception:  # noqa: BLE001 - cancelled or no display
            result[0] = None

    thread = threading.Thread(target=ask)
    thread.start()
    thread.join(timeout=180)
    return result[0]


def browse_save_zip(suggested: str = "RomSrx-backup.zip") -> str | None:
    """Native "save as" for a backup. Its own function rather than a flag on
    browse_save, which is titled and filtered for pictures."""
    result: list[str | None] = [None]

    def ask():
        try:
            import tkinter  # noqa: PLC0415
            from tkinter import filedialog  # noqa: PLC0415
            root = tkinter.Tk()
            root.withdraw()
            root.attributes("-topmost", True)
            chosen = filedialog.asksaveasfilename(
                initialdir=str(Path.home()), initialfile=suggested,
                defaultextension=".zip", title="Save a RomSrx backup",
                filetypes=[("Zip archive", "*.zip"), ("All files", "*.*")])
            root.destroy()
            result[0] = chosen or None
        except Exception:  # noqa: BLE001 - cancelled or no display
            result[0] = None

    thread = threading.Thread(target=ask)
    thread.start()
    thread.join(timeout=180)
    return result[0]


def browse_open_zip(title: str = "Choose a backup") -> str | None:
    """Native picker for a backup file to restore from."""
    result: list[str | None] = [None]

    def ask():
        try:
            import tkinter  # noqa: PLC0415
            from tkinter import filedialog  # noqa: PLC0415
            root = tkinter.Tk()
            root.withdraw()
            root.attributes("-topmost", True)
            chosen = filedialog.askopenfilename(
                title=title, initialdir=str(Path.home()),
                filetypes=[("RomSrx backup", "*.zip"), ("All files", "*.*")])
            root.destroy()
            result[0] = chosen or None
        except Exception:  # noqa: BLE001 - cancelled or no display
            result[0] = None

    thread = threading.Thread(target=ask)
    thread.start()
    thread.join(timeout=180)
    return result[0]


def browse_save(suggested: str = "cover.png") -> str | None:
    """Native "save as" picker, for saving an image out of the app.

    The window has no browser chrome, so the right-click > save people expect
    on a picture has to be offered by the app itself.
    """
    result: list[str | None] = [None]
    pictures = Path.home() / "Pictures"

    def ask():
        try:
            import tkinter  # noqa: PLC0415
            from tkinter import filedialog  # noqa: PLC0415
            root = tkinter.Tk()
            root.withdraw()
            root.attributes("-topmost", True)
            suffix = Path(suggested).suffix or ".png"
            chosen = filedialog.asksaveasfilename(
                initialdir=str(pictures if pictures.is_dir() else Path.home()),
                initialfile=suggested,
                defaultextension=suffix,
                title="Save cover image",
                filetypes=[("Images", "*.png *.jpg *.jpeg *.webp"),
                           ("All files", "*.*")])
            root.destroy()
            result[0] = chosen or None
        except Exception:  # noqa: BLE001 - cancelled or no display
            result[0] = None

    thread = threading.Thread(target=ask)
    thread.start()
    thread.join(timeout=180)
    return result[0]


# Where box art comes from. The frontend builds these URLs; these are the only
# hosts they may point at. The last two only ever appear once the user has
# signed in to an artwork service - see artwork.py - but "Save cover image" has
# to be able to fetch what the tile is already showing, whichever found it.
THUMBNAIL_HOST = "thumbnails.libretro.com"
IMAGE_HOSTS = (THUMBNAIL_HOST, "images.igdb.com",
               "media.retroachievements.org", "retroachievements.org")
# SteamGridDB serves art off numbered CDN hosts (cdn2, cdn3, ...), so the
# domain is matched rather than the machine.
IMAGE_DOMAINS = ("steamgriddb.com",)
MAX_IMAGE = 8 * 1024 * 1024


def _image_host_allowed(host: str) -> bool:
    return host in IMAGE_HOSTS or any(
        host == domain or host.endswith(f".{domain}") for domain in IMAGE_DOMAINS)


def fetch_image(url: str) -> bytes:
    """Download one cover from wherever the app resolved it.

    The URL arrives from the page and is fetched by the app on the user's
    machine, so it is pinned to the handful of hosts covers can come from
    rather than trusted as given.
    """
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "https" or not _image_host_allowed(parsed.hostname or ""):
        raise ValueError("Only cover images can be saved.")

    request = urllib.request.Request(url, headers={"User-Agent": "RomSrx/0.1"})
    with urllib.request.urlopen(request, timeout=30) as response:  # noqa: S310
        data = response.read(MAX_IMAGE + 1)
    if len(data) > MAX_IMAGE:
        raise ValueError("That image is too large to save.")
    return data


def reveal(path: str) -> bool:
    """Show a finished download in the system file manager.

    Only Windows and macOS can highlight the file itself; everywhere else the
    best on offer is opening the folder it sits in.
    """
    target = Path(path)
    if not target.exists():
        target = target.parent
        if not target.exists():
            return False
    try:
        if sys.platform == "win32":
            if target.is_dir():
                os.startfile(target)  # noqa: S606
            else:
                subprocess.Popen(["explorer", "/select,", str(target)])  # noqa: S607
        elif sys.platform == "darwin":
            subprocess.Popen(["open", "-R", str(target)])  # noqa: S607
        else:
            folder = target if target.is_dir() else target.parent
            subprocess.Popen(["xdg-open", str(folder)])  # noqa: S607
        return True
    except Exception:  # noqa: BLE001 - no file manager, or none we can drive
        return False


def archive_signed_in() -> bool:
    """Whether archive.org would currently serve the login-only sources.

    Imported here rather than at module scope so the download queue keeps
    working if the optional `internetarchive` package is missing.
    """
    try:
        from . import account  # noqa: PLC0415
        return bool(account.status().get("signed_in"))
    except Exception:  # noqa: BLE001 - treat anything unreadable as signed out
        return False


# -- checking a download the moment it lands -------------------------------
# The app has just fetched this file and knows exactly which game it is, so
# the question "will this copy earn achievements" can be answered now rather
# than the evening somebody sits down to play it. Hashing a cartridge is a
# second of disk; the answer is written down and the mark is simply there on
# the shelf next time it is drawn.
#
# On its own thread. A download that succeeded must not be reported as failed
# because RetroAchievements was unreachable, and nothing here is allowed to
# hold up the worker that is about to start the next file in the queue.
#
# It used to be silent as well, filing the answer away for the shelf to draw
# later. That wasted the one moment the answer is worth most: the copy is a
# guess made from its *name* until it is hashed, and the hash is the only
# thing that settles it. So a copy that turns out not to be one the set was
# built from now says so, and stops the queue rather than fetching another
# dozen from a shelf that has just been shown to disagree.
#
# Only "nomatch" is worth interrupting for. Every other answer - no set for
# this game, console rule not implemented, RetroAchievements unreachable -
# means "not checked", and a warning that cannot tell those from a real miss
# is a warning nobody reads twice.


def _patch_now(job) -> bool:
    """Turn a finished base ROM into the hack that was asked for.

    Done here rather than left to the reader, because the download on its own
    is not what they asked for: the queue was given a hack set, and a copy of
    Sonic 2 sitting in the games folder is a step towards it, not the thing.

    Before the hash check, deliberately - the set accepts the *patched* file,
    so checking the base ROM against it would report a mismatch on a download
    that is going exactly to plan.

    A patch that fails is reported on the row and nothing else. The base ROM
    is still a real game and still where it was put, and throwing it away
    because a diff would not apply is not this function's decision.
    """
    if not job.patch_url or not job.path:
        return False
    try:
        from . import patcher  # noqa: PLC0415 - keeps this a leaf

        made = patcher.patch_game(job.path, url=job.patch_url)
        where = str((made or {}).get("written") or "")
        if where:
            job.path = where
        job.patch_note = "done"
        return True
    except Exception as exc:  # noqa: BLE001 - a failed patch is not a failed download
        job.patch_note = str(exc)[:200] or "the patch would not apply"
        return False


def _drop_torrent_partial(where: str, final: str) -> list[str]:
    """Remove what a half-finished torrent left in its own folder.

    A collection torrent writes into a folder named after itself and only the
    finished file is moved out, so a download thrown away before that leaves
    its bytes somewhere nothing else looks. Nobody sees them and nothing ever
    cleans them up; for a disc image it is gigabytes.

    Refuses to touch the finished file, whatever it is handed - the two are
    the same path once a torrent has been moved into place, and deleting a
    game somebody keeps because its download row was tidied away would be
    very much worse than leaving a stray part behind.
    """
    if not where:
        return []
    spot = Path(where)
    if final and spot.resolve() == Path(final).resolve():
        return []
    gone = []
    if _remove_file(spot):
        gone.append(spot.name)
    # And the empty folders the torrent made on its way down, stopping at the
    # console's own folder - which is where the finished file would have gone,
    # and is never this function's to remove.
    if final:
        try:
            _prune_empty(spot.parent, Path(final).parent)
        except OSError:  # a stray empty folder is not a failure
            pass
    return gone


def _verify_later(job=None, path: str = "", console: str = "") -> None:
    """Say whether the copy just downloaded is one its set was built from."""
    path = path or (job.path if job else "")
    console = console or (job.console if job else "")
    if not path or not console:
        return

    def run() -> None:
        try:
            from . import names, retro  # noqa: PLC0415 - keeps this a leaf

            if job is not None and job.patch_url and job.patch_note != "done":
                _patch_now(job)
                # The patched file is the one the set is about, so everything
                # below now asks about that rather than the base ROM.
                path_ = job.path
            else:
                path_ = path
            where = Path(path_)
            if not where.exists():
                return                       # extracted in place, or tidied away
            # Named the way library._entry names it, so the verdict is stored
            # under the path and name the shelf will ask about.
            stem = (where.name if where.is_dir()
                    else names.split_extension(where.name)[0])
            # A patched file is named for the hack, and the hack is what
            # RetroAchievements has the set for - so the name it is checked
            # under is the one on disk, whichever of the two that now is.
            from . import rahash  # noqa: PLC0415

            if not rahash.can_read(where.name, console):
                # A compressed disc image nothing here can open. Said plainly
                # rather than left blank: an unmarked row is read as one that
                # passed, and this one was never looked at. See rahash.
                job.ra_verdict = "blind"
                return
            answer = retro.verify([{"path": str(where), "console": console,
                                    "name": stem}])
            rows = (answer or {}).get("rows") or []
            verdict = str((rows[0] if rows else {}).get("verdict") or "")
            if job is not None and verdict:
                job.ra_verdict = verdict
                if verdict == "nomatch":
                    manager.on_bad_copy(job)
        except Exception:  # noqa: BLE001 - never let this touch the download
            return

    threading.Thread(target=run, daemon=True).start()


@dataclass
class Job:
    id: int
    url: str
    filename: str
    console: str = ""
    source: str = ""
    login: bool = False         # source is marked 🔒 login on archive.org
    # What it was doing when it was paused, so resuming can put it back there
    # instead of dropping everything into one undifferentiated queue.
    paused_from: str = ""       # "" | "running" | "queued"
    total: int = 0
    done: int = 0
    status: str = "queued"      # queued|running|paused|extracting|done|error
    error: str = ""
    speed: float = 0.0          # bytes/sec, smoothed
    path: str = ""              # what "open folder" should reveal
    extracted: str = ""         # folder the archive was unpacked into
    attempts: int = 0
    # How far through unpacking, 0-100. Downloading and extracting are two
    # different waits and a 2 GB archive can spend minutes on the second one
    # with nothing moving on screen, which reads as a hang.
    extract_pct: float = 0.0
    added: float = field(default_factory=time.time)
    finished: float = 0.0
    # Where this sits in the wait list; lower goes first. Defaults to the job
    # id, so left alone the queue is plain first-come-first-served.
    order: float = 0.0
    # What hashing the finished file said: "" until it has been checked, then
    # "match", "nomatch", or one of the reasons it could not be checked.
    ra_verdict: str = ""
    # A patch to apply once the file is here, for the achievement sets that
    # are a fan hack rather than a release. The download fetches the ordinary
    # game; this is what turns it into the thing that was actually asked for.
    # Empty for every ordinary download. See hacks.py.
    patch_url: str = ""
    patch_note: str = ""        # "" | "done" | the reason it did not work
    # The best sustained rate this download has reached, and how many times
    # it has been reconnected for falling far short of it. Not persisted: what
    # a connection managed yesterday says nothing about the one today.
    best_rate: float = 0.0
    slow_retries: int = 0
    # Where a torrent is writing before the finished file is moved into place.
    # Kept so that throwing the download away can take the half of it that is
    # sitting in the torrent's own folder - which is otherwise invisible, and
    # for a disc image is gigabytes of it.
    torrent_path: str = ""

    def snapshot(self) -> dict:
        pct = (self.done / self.total * 100) if self.total else 0.0
        remaining = max(self.total - self.done, 0)
        eta = remaining / self.speed if self.speed > 1 and remaining else 0
        return {
            "id": self.id, "filename": self.filename, "console": self.console,
            "source": self.source, "status": self.status, "error": self.error,
            "login": self.login,
            "done": self.done, "total": self.total, "percent": round(pct, 1),
            "speed": round(self.speed), "eta": round(eta), "path": self.path,
            "extracted": self.extracted, "attempts": self.attempts,
            "extractPercent": round(self.extract_pct, 1),
            "raVerdict": self.ra_verdict,
            "patchUrl": self.patch_url, "patchNote": self.patch_note,
        }


class _Crawling(Exception):
    """This connection has collapsed to a fraction of what it was managing.

    archive.org answers from whichever of its nodes the redirect picks, and
    they are not alike: the same file, asked for four times in a minute, came
    back at 543 KB/s, 35 KB/s, 22 KB/s and 543 KB/s again. A 2 GB disc at the
    slow end is twenty hours, and the app sat through it because a transfer
    that is moving is not a transfer that has failed.

    Raised only against this download's own best stretch, never against a
    number picked in advance - somebody on a slow line has a slow line, and
    dropping their connection every minute to look for a better one they
    cannot have would be worse than useless. It needs proof that this
    download has already gone faster than it is going now.
    """


class _RangeGone(Exception):
    """The server will not serve from that offset - it is past the end.

    Carries the real length of the file when the server said it, which it is
    required to in the Content-Range of a 416: "bytes */200000".
    """

    def __init__(self, size: int = 0) -> None:
        super().__init__("range past the end of the file")
        self.size = int(size or 0)


def _range_total(header) -> int:
    """The length out of a Content-Range, or 0 if it does not say."""
    text = str(header or "")
    if "/" not in text:
        return 0
    tail = text.rsplit("/", 1)[-1].strip()
    return int(tail) if tail.isdigit() else 0


class Slots:
    """How many downloads may be in flight at once.

    This is what makes the queue roll: a worker takes the next job off the
    queue but only starts it once a slot is free, and a slot frees the instant
    a download finishes, so the next one begins immediately.

    It isn't a plain semaphore because the limit has to be able to *drop*
    while downloads are running - a semaphore can't be resized, which is why
    choosing a smaller number used to do nothing until the app restarted.
    Lowering it never interrupts anything: what is already running finishes,
    and nothing new starts until the number in flight is back under the limit.
    """

    def __init__(self, limit: int) -> None:
        self._cv = threading.Condition()
        self._limit = max(1, limit)
        self._used = 0

    def set_limit(self, limit: int) -> None:
        with self._cv:
            self._limit = max(1, limit)
            self._cv.notify_all()

    def acquire(self) -> None:
        with self._cv:
            while self._used >= self._limit:
                self._cv.wait()
            self._used += 1

    def release(self) -> None:
        with self._cv:
            self._used = max(0, self._used - 1)
            self._cv.notify_all()

    @property
    def in_flight(self) -> int:
        with self._cv:
            return self._used


class Manager:
    """Owns the queue, the workers and the job table."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._jobs: dict[int, Job] = {}
        self._queue: queue.Queue[int] = queue.Queue()
        # job id -> why it should stop ("paused" or "cancelled"). A paused job
        # keeps its .part file and can be put back on the queue as-is.
        self._stop: dict[int, str] = {}
        self._next_id = 1
        # The last download whose hash disagreed with its achievement set, for
        # the page to report once and then dismiss. See on_bad_copy.
        self._bad_copy: dict = {}
        self._workers: list[threading.Thread] = []
        self._slots = Slots(DEFAULT_WORKERS)
        self._started = False
        # The shared speed ceiling: bytes that may go out right now, and when
        # that was last worked out. Its own lock, held for a few microseconds
        # at a time, because the main one is held across whole state changes
        # and every chunk of every download passes through here.
        self._rate_lock = threading.Lock()
        self._tokens = 0.0
        self._filled = 0.0
        # The download settings, re-read a few times a second rather than for
        # every chunk that arrives. See _wait_for_room.
        self._settings_cache = None
        self._settings_at = 0.0
        self._settings_stamp = -1

    # -- session ---------------------------------------------------------
    def _session(self):
        """An authenticated requests session when available, else None."""
        try:
            from internetarchive import get_session  # noqa: PLC0415
            return get_session()
        except Exception:  # noqa: BLE001 - fall back to urllib
            return None

    # -- public API ------------------------------------------------------
    def start(self) -> None:
        self.ensure_workers(load_settings()["workers"])

    def ensure_workers(self, wanted: int) -> None:
        """Set how many downloads run at once, and make sure there are enough
        threads to reach it.

        Raising it starts more immediately. Lowering it stops the newest
        downloads and puts them at the front of the queue, so the number
        actually running matches what was asked for rather than only applying
        to whatever starts next.
        """
        self._started = True
        target = _sane_workers(wanted)
        self._slots.set_limit(target)

        with self._lock:
            alive = [t for t in self._workers if t.is_alive()]
            self._workers = alive
            missing = max(0, target - len(alive))
            # Newest first: the ones furthest down the panel are the ones the
            # user expects to give way, and they have the least to lose.
            running = sorted((j for j in self._jobs.values()
                              if j.status == "running"),
                             key=lambda j: j.id, reverse=True)
            excess = running[:max(0, len(running) - target)]

        for _ in range(missing):
            thread = threading.Thread(target=self._worker, daemon=True)
            thread.start()
            self._workers.append(thread)

        # They keep their .part file, so each carries on from where it stopped
        # once a slot frees up again.
        for job in excess:
            self.requeue(job.id, front=True)

    def job(self, job_id: int) -> Job | None:
        with self._lock:
            return self._jobs.get(job_id)

    def add(self, items: list[dict]) -> list[int]:
        added = []
        with self._lock:
            existing = {j.url for j in self._jobs.values()
                        if j.status in ("queued", "running")}
            for item in items:
                url = (item.get("url") or "").strip()
                if not url or url in existing:
                    continue
                # A magnet is only queueable where there is something that
                # can run it. Without libtorrent this worker speaks HTTP and
                # nothing else - byte ranges, .part resume, redirects, none of
                # which a magnet has an answer to - so the job would exist
                # only to fail, and the page offers the magnet to another
                # client instead. Anything that is neither is refused outright.
                if url.lower().startswith("magnet:"):
                    from . import torrent  # noqa: PLC0415 - optional
                    if not torrent.available():
                        continue
                elif not url.lower().startswith(("http://", "https://")):
                    continue
                job = Job(
                    id=self._next_id, url=url,
                    filename=safe_name(item.get("filename") or "download"),
                    console=item.get("console", ""), source=item.get("source", ""),
                    login=bool(item.get("login")),
                    total=int(item.get("size") or 0),
                    order=float(self._next_id),
                    # Only ever set for a hack set, where what was asked for
                    # is a patch applied to this file rather than this file.
                    patch_url=str(item.get("patch") or "").strip(),
                )
                self._jobs[job.id] = job
                self._next_id += 1
                existing.add(url)
                added.append(job.id)
        for job_id in added:
            self._queue.put(job_id)
        if added:
            self.start()
            self._persist()
        return added

    def _halt(self, job_id: int, reason: str) -> bool:
        with self._lock:
            job = self._jobs.get(job_id)
            if not job or job.status in ("done", "paused", "cancelled"):
                return False
            job.paused_from = ("running" if job.status in ("running", "extracting")
                               else "queued")
            self._stop[job_id] = reason
            if job.status == "queued":
                # Never started, so settle it here rather than waiting for a
                # worker to pick it up.
                job.status = reason
                job.speed = 0.0
                self._stop.pop(job_id, None)
        self._persist()
        return True

    def pause(self, job_id: int) -> bool:
        return self._halt(job_id, "paused")

    def cancel(self, job_id: int) -> bool:
        return self._halt(job_id, "cancelled")

    def start_next(self, job_id: int) -> bool:
        """Send a waiting download to the front of the queue.

        It doesn't push anything aside - it takes the next slot that frees up,
        which is what `requeue` on a running one is for.
        """
        with self._lock:
            job = self._jobs.get(job_id)
            if not job or job.status != "queued":
                return False
            first = min((j.order for j in self._jobs.values()), default=0.0)
            job.order = first - 1.0
        self._persist()
        return True

    def requeue(self, job_id: int, front: bool = False) -> bool:
        """Send a running download back to the wait list, freeing its slot.

        The .part file stays put, so when its turn comes round again it picks
        up from where it stopped rather than starting over.

        `front` puts it next in line instead of last: that is for downloads
        pushed aside by lowering the limit, which should be the first back on
        when it is raised again - they were already part-way through.
        """
        with self._lock:
            job = self._jobs.get(job_id)
            if not job or job.status not in ("running", "queued"):
                return False
            if job.status == "queued":
                return True          # already waiting, nothing to do
            if front:
                job.order = min((j.order for j in self._jobs.values()),
                                default=0.0) - 1.0
            else:
                job.order = max((j.order for j in self._jobs.values()),
                                default=0.0) + 1.0
            # The worker notices this and settles the job as "queued"; it also
            # puts the token back, so something picks it up again later.
            self._stop[job_id] = "queued"
        self._persist()
        return True

    def pause_login_required(self) -> int:
        """Stop everything that archive.org will no longer serve us.

        Signing out mid-download doesn't stop the transfers already in flight -
        the worker holds an open connection - so they run on and only fail
        later, at some unrelated-looking point. Worse, the .part file they
        leave behind is resumed against a session that no longer exists, which
        is where the errors on resume came from. Pausing them at the moment of
        the sign-out keeps the part files intact and makes the reason plain.
        """
        with self._lock:
            # Not "extracting": that one is off the network already, with the
            # whole file on disk. Stopping it would only strand the archive.
            ids = [i for i, j in self._jobs.items()
                   if j.login and j.status in ("running", "queued")]
        return sum(1 for i in ids if self._halt(i, "paused"))

    def resume(self, job_id: int) -> dict:
        """Put a paused job back on the queue; it picks up from its .part.

        A login-only download can't go anywhere while signed out - it would
        fail on the first request - so it is refused here and the page is told
        why, rather than the job being restarted only to break again.
        """
        with self._lock:
            job = self._jobs.get(job_id)
            if not job or job.status not in ("paused", "cancelled", "error"):
                return {"resumed": False}
            needs_login = job.login
        if needs_login and not archive_signed_in():
            return {"resumed": False, "needs_login": True}

        with self._lock:
            job = self._jobs.get(job_id)
            if not job or job.status not in ("paused", "cancelled", "error"):
                return {"resumed": False}
            self._stop.pop(job_id, None)
            job.status = "queued"
            job.error = ""
            job.attempts = 0
            job.paused_from = ""
        self._queue.put(job_id)
        self.start()
        self._persist()
        return {"resumed": True}

    def discard(self, job_id: int) -> dict:
        """Remove a stopped job *and* whatever it left on disk.

        Cancelling keeps the .part file so the download can resume later; this
        is the way to say you don't want it after all. Refused while a job is
        still active, since a worker would be writing to that file.
        """
        with self._lock:
            job = self._jobs.get(job_id)
            if job is None:
                return {"removed": False, "reason": "no such download"}
            active = job.status in ("running", "queued", "extracting")
            if active:
                self._stop[job_id] = "cancelled"

        # Let the worker notice and release the file before we delete it.
        if active:
            for _ in range(60):
                with self._lock:
                    job = self._jobs.get(job_id)
                    if not job or job.status not in ("running", "queued", "extracting"):
                        break
                time.sleep(0.1)

        with self._lock:
            job = self._jobs.get(job_id)
            if job is None:
                return {"removed": True, "deleted": []}
            path, extracted = job.path, job.extracted
            half = job.torrent_path

        deleted = []
        if path:
            final = Path(path)
            for candidate in (final, Path(f"{final}.part")):
                if _remove_file(candidate):
                    deleted.append(candidate.name)
        deleted += _drop_torrent_partial(half, path)
        if extracted:
            try:
                folder = Path(extracted)
                if folder.is_dir():
                    shutil.rmtree(folder, ignore_errors=True)
                    deleted.append(folder.name + "/")
            except OSError:
                pass

        with self._lock:
            self._jobs.pop(job_id, None)
            # The stop flag is deliberately left in place. A worker that
            # hasn't reached its next chunk yet still needs to see it -
            # clearing it here would leave the thread downloading forever
            # for a job that no longer exists, holding the file open.
        self._persist()
        return {"removed": True, "deleted": deleted}

    def on_bad_copy(self, job) -> None:
        """A finished file hashed to something its set does not accept.

        Noted and nothing else. The queue keeps going: one copy being the
        wrong revision says nothing about the next game in the list, and
        stopping everything to ask about it would interrupt a night's
        downloading over a file that is already on disk.

        The file is left exactly where it is, too. It is a real dump of
        something - very often the right game in a revision the set was not
        built from - and deleting somebody's download over a hash is not this
        function's decision to make. The row says so; the reader decides.
        """
        with self._lock:
            self._bad_copy = {"id": job.id, "filename": job.filename,
                              "console": job.console, "at": time.time()}

    def bad_copy(self) -> dict:
        """The last copy that failed its check, for the page to report once."""
        with self._lock:
            return dict(self._bad_copy or {})

    def clear_bad_copy(self) -> None:
        with self._lock:
            self._bad_copy = {}

    def pause_all(self) -> int:
        """Stop everything, in one movement.

        This used to pause the jobs one at a time, which does the opposite of
        what it says: pausing a running download frees its slot, a waiting
        worker immediately claims the next queued job, and by the time the loop
        reached that job it had already started downloading. Pressing "pause
        all" visibly started transfers.

        Holding the lock for the whole sweep closes that window - `_take_next`
        needs the same lock, and once it gets it there is nothing left marked
        queued to take. What each job was at the time is recorded so resuming
        can put it back the way it was rather than shuffling the order.
        """
        paused = 0
        with self._lock:
            for job_id, job in self._jobs.items():
                if job.status in ("running", "extracting"):
                    job.paused_from = "running"
                    self._stop[job_id] = "paused"
                    paused += 1
                elif job.status == "queued":
                    # Never started, so it is settled here and now - waiting for
                    # a worker would mean waiting forever, since a queued job
                    # flagged to stop is one no worker will ever pick up.
                    job.paused_from = "queued"
                    job.status = "paused"
                    job.speed = 0.0
                    paused += 1
        self._persist()
        return paused

    def resume_all(self) -> dict:
        """Restart everything stopped. Anything needing an account we don't
        have is left alone and counted, so the page can say so once rather
        than failing one download at a time."""
        with self._lock:
            stopped = [j for j in self._jobs.values()
                       if j.status in ("paused", "cancelled", "error")]
            ids = [j.id for j in stopped if not j.login]
            locked = [j.id for j in stopped if j.login]
        # Asked once for the whole batch: the check opens an archive.org
        # session, which is far too much work to repeat per download.
        if locked and archive_signed_in():
            ids += locked
            locked = []

        # Whatever was mid-transfer when everything stopped goes back to the
        # front of the wait list, keeping the order it had. Without this,
        # resuming hands the slots to whichever ids happen to sort first, so
        # the downloads that were running - the ones with a part-file and the
        # most to lose - get overtaken by files that had never started.
        with self._lock:
            resuming = [self._jobs[i] for i in ids if i in self._jobs]
            was_running = sorted((j for j in resuming
                                  if j.paused_from == "running"),
                                 key=lambda j: j.order)
            if was_running:
                first = min((j.order for j in self._jobs.values()), default=0.0)
                for n, job in enumerate(was_running):
                    job.order = first - len(was_running) + n

        return {"resumed": sum(1 for i in ids if self.resume(i).get("resumed")),
                "blocked": len(locked)}

    def discard_all(self) -> dict:
        """Stop everything and delete what it left on disk.

        Done in one pass rather than by calling discard() per job. That
        version waits up to six seconds for each active download to let go of
        its file and rewrites the queue afterwards - fine once, but with a
        full list it meant minutes of waiting in series and one whole-file
        write per entry. Here everything is told to stop at once, waited for
        once, and saved once.
        """
        with self._lock:
            jobs = list(self._jobs.values())
            transferring = []
            for job in jobs:
                if job.status in ("running", "extracting"):
                    # A worker is holding this file; it has to be asked.
                    self._stop[job.id] = "cancelled"
                    transferring.append(job)
                elif job.status == "queued":
                    # Settled here and now. Waiting for a worker to do it
                    # would hang forever: `_take_next` skips anything already
                    # flagged to stop, so a cancelled queued job is never
                    # picked up and never changes state.
                    job.status = "cancelled"
                    job.speed = 0.0

        # One wait for all the transfers, not one each.
        if transferring:
            deadline = time.monotonic() + 6.0
            while time.monotonic() < deadline:
                with self._lock:
                    busy = [j for j in transferring
                            if j.id in self._jobs
                            and self._jobs[j.id].status in
                            ("running", "extracting")]
                if not busy:
                    break
                time.sleep(0.05)

        deleted = []
        for job in jobs:
            if job.path:
                final = Path(job.path)
                for candidate in (final, Path(f"{final}.part")):
                    if _remove_file(candidate):
                        deleted.append(candidate.name)
            deleted += _drop_torrent_partial(job.torrent_path, job.path)
            if job.extracted:
                try:
                    folder = Path(job.extracted)
                    if folder.is_dir():
                        shutil.rmtree(folder, ignore_errors=True)
                        deleted.append(folder.name + "/")
                except OSError:
                    pass

        with self._lock:
            for job in jobs:
                self._jobs.pop(job.id, None)
            # Stop flags stay: a worker that hasn't reached its next chunk
            # still needs to see one, or it would download on forever for a
            # job that no longer exists.
        self._persist()
        return {"removed": len(jobs), "deleted": deleted}

    def forget(self, job_id: int) -> dict:
        """Take one entry off the list and leave the files exactly where they
        are. The opposite of discard(), which is the one that deletes.

        Refused while the job is still going: a row vanishing from under a
        download that carries on writing would leave a file nothing in the app
        knows about.
        """
        with self._lock:
            job = self._jobs.get(job_id)
            if job is None:
                return {"forgotten": False, "reason": "no such download"}
            if job.status in ("running", "queued", "extracting"):
                return {"forgotten": False, "reason": "still going"}
            self._jobs.pop(job_id, None)
            self._stop.pop(job_id, None)
        self._persist()
        return {"forgotten": True}

    def forget_paths(self, paths) -> int:
        """Drop finished entries whose files have just been deleted elsewhere.

        Deleting a game in the library leaves its download sitting under
        "Finished", offering to open a folder that is no longer there. The
        row is about a file, so when the file goes the row should go with it.

        Only settled entries: something still downloading to that path is a
        different matter, and taking its row away would leave a transfer
        running with nothing on screen to stop it.
        """
        wanted = {str(p).rstrip("\\/").lower() for p in paths if p}
        if not wanted:
            return 0
        with self._lock:
            gone = [
                job_id for job_id, job in self._jobs.items()
                if job.status in ("done", "cancelled", "error")
                and ({str(job.path).rstrip("\\/").lower(),
                      str(job.extracted).rstrip("\\/").lower()} & wanted)
            ]
            for job_id in gone:
                self._jobs.pop(job_id, None)
                self._stop.pop(job_id, None)
        if gone:
            self._persist()
        return len(gone)

    def clear_finished(self) -> int:
        with self._lock:
            # Paused jobs are deliberately kept - they're unfinished business.
            gone = [i for i, j in self._jobs.items()
                    if j.status in ("done", "cancelled", "error")]
            for i in gone:
                self._jobs.pop(i, None)
                self._stop.pop(i, None)
        self._persist()
        return len(gone)

    # -- persistence -----------------------------------------------------
    # Everything a job needs to be itself again tomorrow. A field left out
    # here is not a small loss: patch_url was missing, so a hack resumed the
    # next day quietly finished as the plain game it was built from, with
    # nothing on the row to say the patch had been forgotten.
    PERSIST_FIELDS = ("id", "url", "filename", "console", "source", "login",
                      "paused_from", "total", "done", "status", "path",
                      "extracted", "error", "added", "order",
                      "patch_url", "patch_note", "ra_verdict", "torrent_path")

    def _persist(self) -> None:
        """Remember the queue so closing the app doesn't lose it."""
        with self._lock:
            rows = [{f: getattr(job, f) for f in self.PERSIST_FIELDS}
                    for job in self._jobs.values()]
        state.save("queue", rows)

    def restore(self) -> int:
        """Reload the queue from disk. Anything mid-flight comes back paused -
        its .part file is still there, so it can pick up where it stopped."""
        rows = state.load("queue", [])
        with self._lock:
            for row in rows:
                if not isinstance(row, dict) or not row.get("url"):
                    continue
                job = Job(id=int(row.get("id") or 0), url=row["url"],
                          filename=row.get("filename", "download"))
                for field in self.PERSIST_FIELDS:
                    if field in row and field not in ("id", "url", "filename"):
                        setattr(job, field, row[field])
                if job.status in ("running", "queued", "extracting"):
                    # Closing the app is a pause like any other, so remember
                    # what each was doing: next launch's "resume all" then
                    # restarts the transfers first and leaves the rest waiting.
                    job.paused_from = ("queued" if job.status == "queued"
                                       else "running")
                    job.status = "paused"
                if not job.order:      # written before the wait list had order
                    job.order = float(job.id)
                job.speed = 0.0
                self._jobs[job.id] = job
                self._next_id = max(self._next_id, job.id + 1)
            return len(self._jobs)

    def snapshot(self) -> dict:
        with self._lock:
            waiting = sorted((j for j in self._jobs.values()
                              if j.status == "queued"),
                             key=lambda j: (j.order, j.id))
            places = {job.id: n for n, job in enumerate(waiting, 1)}
            jobs = [j.snapshot() for j in self._jobs.values()]
            # A running job only becomes "paused" once its worker notices, and
            # a stalled transfer can sit there for a while. Without this the
            # page still counts it as active, and "Pause all" never flips back
            # to "Resume all" however many times it is pressed.
            stopping = set(self._stop)
            for job in jobs:
                job["stopping"] = job["id"] in stopping
        # Where each waiting download sits in the queue, so the panel can say
        # which one is up next after you reorder them.
        for job in jobs:
            job["place"] = places.get(job["id"], 0)
        active = [j for j in jobs if j["status"] == "running"]
        return {
            "jobs": sorted(jobs, key=lambda j: j["id"]),
            "active": len(active),
            "queued": len(waiting),
            "speed": round(sum(j["speed"] for j in active)),
            "folder": load_settings()["folder"],
            # Set once, when a finished file hashes to something its set does
            # not accept. The page reports it and then dismisses it, so a
            # warning that has been read does not come back on every poll.
            "badCopy": self.bad_copy(),
        }

    # -- worker ----------------------------------------------------------
    def _take_next(self) -> Job | None:
        """Claim whichever queued job should go next, or None if none can.

        The job is chosen here rather than being whichever id came off the
        queue, so the wait list can be reordered without rebuilding it. What
        comes off the queue is only a token saying "there is work"; tokens are
        interchangeable, and there is always one per waiting job.
        """
        with self._lock:
            waiting = [j for j in self._jobs.values()
                       if j.status == "queued" and j.id not in self._stop]
            if not waiting:
                return None
            job = min(waiting, key=lambda j: (j.order, j.id))
            job.status = "running"
            return job

    def _worker(self) -> None:
        while True:
            self._queue.get()          # a token: something is waiting
            job = None
            # Looked up per job, not once per thread. Worker threads outlive
            # any number of sign-ins and sign-outs, so a session captured at
            # startup would keep working after logout - and signing in would
            # do nothing until the app was restarted.
            session = self._session()
            try:
                # Wait for a free slot *before* claiming anything, so the panel
                # never shows more in flight than the limit allows. Releasing
                # the slot below is what lets the next one start the moment
                # this download is finished with.
                self._slots.acquire()
                try:
                    job = self._take_next()
                    if job is None:
                        continue       # another worker got there first
                    self._run(job, session)
                    if job.status == "done":
                        forget_from_cart(job.url)
                    elif job.status == "queued":
                        # Sent back to the wait list; put its token back.
                        self._queue.put(job.id)
                finally:
                    self._slots.release()
            except Exception as exc:  # noqa: BLE001 - a worker must not die
                with self._lock:
                    if job is not None:
                        job.status = "error"
                        job.error = str(exc)[:300]
            finally:
                self._queue.task_done()
                self._persist()   # capture the finished/failed state

    def _run_torrent(self, job: Job, folder: Path, final: Path) -> None:
        """One file out of a collection torrent, into the console's folder.

        Reported through the same fields the HTTP path uses, so the panel, the
        queue, the progress bar and the window title all carry on not knowing
        which kind of job they are looking at.
        """
        from . import state, torrent  # noqa: PLC0415 - optional, and circular

        prefs = state.prefs()
        adapter = str(prefs.get("torrent_interface") or "").strip()
        if adapter and not torrent.interface_is_up(adapter):
            with self._lock:
                job.status = "error"
                job.error = (f"the network adapter set for torrents "
                             f"({adapter}) is not up")
            return

        def progress(done, total, rate):
            with self._lock:
                job.done = done
                if total:
                    job.total = total
                job.speed = rate

        def stopping():
            return job.id in self._stop

        def stage(text):
            # "extracting" is the nearest existing state to "waiting for the
            # file list": work is happening, there is no percentage for it
            # yet, and the panel already draws that as a striped bar.
            with self._lock:
                job.status = "running" if text == "downloading" else "extracting"

        def writing_to(target):
            with self._lock:
                job.torrent_path = str(target)

        try:
            got = torrent.fetch(job.url, folder, prefs, want=job.filename,
                                on_progress=progress, should_stop=stopping,
                                on_stage=stage, on_target=writing_to)
        except torrent.Stopped:
            with self._lock:
                job.status = self._stop.pop(job.id, "cancelled")
                job.speed = 0.0
            return
        except Exception as exc:  # noqa: BLE001 - reported on the row
            with self._lock:
                job.status = "error"
                job.error = f"{type(exc).__name__}: {str(exc)[:200]}"
                job.speed = 0.0
            return

        # The torrent writes into a folder named after itself, so the file
        # lands a few levels down. Moved up beside everything else for this
        # console, because "where did my game go" should have one answer.
        with self._lock:
            job.status = "running"
            job.speed = 0.0
        try:
            if got.resolve() != final.resolve():
                final.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(got), str(final))
                _prune_empty(got.parent, folder)
        except OSError as exc:
            with self._lock:
                job.status = "error"
                job.error = f"could not move it into place: {exc}"
            return

        with self._lock:
            job.done = job.total = final.stat().st_size
            job.path = str(final)
            job.torrent_path = ""       # moved out; nothing left behind
        self._maybe_extract(job, final)
        with self._lock:
            job.status = "done"
            job.finished = time.time()
        _verify_later(job)

    def _already_here(self, job: Job, final: Path) -> bool:
        """Is the finished file already sitting there? Then nothing to fetch.

        The size has to agree with the size the queue was told, and that check
        used to be missing - any file of more than nothing counted. A download
        cut short leaves exactly that: a part of a file under the final name,
        which was then reported as complete. The reader gets a truncated game
        and a row saying it worked, which is the worst of both.

        Unknown size is the one case where there is nothing to compare, and
        there the old behaviour is kept: a file is a file.
        """
        if not final.exists():
            return False
        try:
            size = final.stat().st_size
        except OSError:
            return False
        if size <= 0:
            return False
        # Short of what the queue was told, by more than the index could
        # plausibly be wrong about. MiNERVA's listing sizes are approximate -
        # measured against the site's own figures they drift by a few bytes
        # in either direction - so an exact comparison would decide that every
        # finished MiNERVA download was incomplete and fetch it all again. The
        # thing actually being guarded against is a download cut short, which
        # is out by a third of a file, not by four bytes.
        if job.total and size < job.total - max(1024, job.total // 100):
            # Something is there and it is not the whole of this. Left alone
            # rather than deleted - it may be somebody else's copy under the
            # same name - and the download carries on into its .part beside it.
            return False
        with self._lock:
            job.done = job.total = size
            job.status = "done"
            job.finished = time.time()
            job.error = "already downloaded"
            job.path = str(final)
        _verify_later(job)
        return True

    def _open(self, session, url: str, offset: int):
        """Range request from `offset`. Returns (response, is_partial).

        Raises _RangeGone for 416, which is not a failure to retry: it says
        the offset asked from is past the end of the file, and asking again
        more slowly will never change that.
        """
        headers = {"User-Agent": "RomSrx/0.1"}
        if offset:
            headers["Range"] = f"bytes={offset}-"
        if session is not None:
            resp = session.get(url, headers=headers, stream=True, timeout=60)
            if resp.status_code == 416:
                size = _range_total(resp.headers.get("Content-Range"))
                resp.close()
                raise _RangeGone(size)
            if resp.status_code in TRANSIENT:
                resp.close()
                raise urllib.error.HTTPError(url, resp.status_code,
                                             "transient", None, None)
            resp.raise_for_status()
            return resp, resp.status_code == 206
        request = urllib.request.Request(url, headers=headers)
        try:
            resp = urllib.request.urlopen(request, timeout=60)
        except urllib.error.HTTPError as exc:
            if exc.code == 416:
                raise _RangeGone(
                    _range_total(exc.headers.get("Content-Range"))) from exc
            raise
        return resp, resp.status == 206

    @staticmethod
    def _session_signed_in(session) -> bool:
        """Read the sign-in off the session the worker already holds, rather
        than opening another one just to ask."""
        try:
            return session is not None and bool(
                session.cookies.get("logged-in-sig"))
        except Exception:  # noqa: BLE001 - no cookie jar, no sign-in
            return False

    def _run(self, job: Job, session) -> None:
        # Told to stop between being claimed and being started - which is the
        # window "pause all" lands in for whichever job a worker had just
        # picked up. Checked before anything opens a connection, so pausing
        # really does mean nothing starts.
        if job.id in self._stop:
            with self._lock:
                job.status = self._stop.pop(job.id, "paused")
                job.speed = 0.0
            return

        # Last line of defence for a 🔒 download that reached a worker while
        # signed out. Starting it would spend a retry cycle on a 403 and leave
        # a "Failed" row whose reason means nothing to the reader.
        if job.login and not self._session_signed_in(session):
            with self._lock:
                job.status = "paused"
                job.error = ""
                job.speed = 0.0
            return

        folder = folder_for(job.console)
        folder.mkdir(parents=True, exist_ok=True)
        final = folder / job.filename
        part = folder / (job.filename + ".part")
        job.path = str(final)

        # A whole different way of getting bytes, and the only thing above it
        # that applies is where they land. Split here rather than earlier so a
        # torrent job still gets the folder, the "already downloaded" check
        # below, extraction afterwards and the verify - everything about a
        # download that is not the transfer itself.
        if job.url.lower().startswith("magnet:"):
            if self._already_here(job, final):
                return
            self._run_torrent(job, folder, final)
            return

        if self._already_here(job, final):
            return

        # Counted rather than iterated, because a reconnection made to escape
        # a slow server is not a failed attempt and must not spend one - the
        # download is going fine, it is going fine somewhere else.
        attempt = 0
        while attempt < RETRIES:
            attempt += 1
            job.attempts = attempt
            offset = part.stat().st_size if part.exists() else 0

            # The app was closed in the gap between the last byte arriving and
            # the rename. Every byte is already here, so asking for the next
            # one asks for a byte past the end - the server answers 416, which
            # looked like any other failure and was retried five times over
            # thirty seconds before the row died with "HTTPError: 416" on a
            # download that had actually finished. Nothing to fetch: finish it.
            if offset and job.total and offset >= job.total:
                if offset == job.total:
                    self._finish(job, part, final)
                    return
                # Longer than the file is supposed to be, so it is not a
                # part of this file - a rename that got half-way, a leftover
                # from a different dump under the same name. Renaming it
                # would hand over a corrupt game reported as finished, which
                # is the one outcome worse than downloading it again.
                part.unlink(missing_ok=True)
                offset = 0
                with self._lock:
                    job.done = 0

            try:
                resp, partial = self._open(session, job.url, offset)
            except _RangeGone as gone:
                # The server says the offset is past the end and, in the
                # Content-Range it must send with a 416, how long the file
                # really is. Either what is here is the whole thing, or it is
                # not this file at all and starting over is the only answer.
                whole = gone.size
                if whole and offset == whole:
                    self._finish(job, part, final)
                    return
                part.unlink(missing_ok=True)
                with self._lock:
                    job.done = 0
                if attempt == RETRIES:
                    with self._lock:
                        job.status = "error"
                        job.error = ("the part already here does not belong to "
                                     "this file; it has been discarded")
                    return
                continue
            except Exception as exc:  # noqa: BLE001
                if attempt == RETRIES:
                    with self._lock:
                        job.status = "error"
                        job.error = f"{type(exc).__name__}: {str(exc)[:200]}"
                    return
                time.sleep(RETRY_BASE * attempt)
                continue

            # Server ignored our Range - start the file again.
            if offset and not partial:
                offset = 0
                part.unlink(missing_ok=True)

            total = self._content_length(resp, offset)
            with self._lock:
                job.done = offset
                if total:
                    job.total = total

            try:
                self._stream(job, resp, part, offset)
            except _Stopped:
                with self._lock:
                    job.status = self._stop.pop(job.id, "cancelled")
                    job.speed = 0.0
                return
            except _Crawling:
                # Straight round again, with no backoff and without spending
                # an attempt: the point is to be handed a different server,
                # and what is on the disk is kept either way. Bounded by
                # SLOW_GIVEUP inside _stream, so this cannot loop.
                with self._lock:
                    job.speed = 0.0
                attempt -= 1
                try:
                    resp.close()
                except Exception:  # noqa: BLE001, S110
                    pass
                continue
            except Exception as exc:  # noqa: BLE001 - retry transient drops
                if attempt == RETRIES:
                    with self._lock:
                        job.status = "error"
                        job.error = f"{type(exc).__name__}: {str(exc)[:200]}"
                    return
                time.sleep(RETRY_BASE * attempt)
                continue
            finally:
                try:
                    resp.close()
                except Exception:  # noqa: BLE001, S110
                    pass

            self._finish(job, part, final)
            return

    def _finish(self, job: Job, part: Path, final: Path) -> None:
        """Put the finished .part in place and take it from there."""
        part.replace(final)
        with self._lock:
            job.done = job.total = final.stat().st_size
            job.speed = 0.0
            job.path = str(final)
        self._maybe_extract(job, final)
        with self._lock:
            job.status = "done"
            job.finished = time.time()
        _verify_later(job)

    def _maybe_extract(self, job: Job, archive: Path) -> None:
        """Unpack a zip/7z, either into a folder of its own or straight into
        the folder it was downloaded to."""
        settings = load_settings()
        if not settings["extract"] or archive.suffix.lower() not in ARCHIVES:
            return

        here = settings.get("extract_mode") == "here"
        dest = archive.parent if here else archive.with_suffix("")
        with self._lock:
            job.status = "extracting"
            job.speed = 0.0
            job.extract_pct = 0.0
        try:
            dest.mkdir(parents=True, exist_ok=True)
            if archive.suffix.lower() == ".zip":
                self._unzip(job, archive, dest)
            else:
                self._un7z(job, archive, dest)
        except Exception as exc:  # noqa: BLE001 - keep the archive if this fails
            with self._lock:
                job.error = f"downloaded, but extraction failed: {str(exc)[:150]}"
                job.path = str(archive)
            return

        with self._lock:
            # `extracted` is what "delete this download" removes with rmtree,
            # so it may only ever name a folder this download owns. Unpacking
            # in place spreads files through a folder full of other games -
            # recording it here would put the whole download folder one click
            # from being deleted. So it stays empty, `path` keeps pointing at
            # the archive, and "open folder" falls back to the parent when the
            # archive itself has been tidied away.
            if not here:
                job.extracted = str(dest)
                job.path = str(dest)

        if settings["delete_archive"]:
            try:
                archive.unlink()
            except OSError as exc:
                with self._lock:
                    job.error = f"extracted, but could not delete archive: {exc}"

    def _unzip(self, job: Job, archive: Path, dest: Path) -> None:
        """Unpack a zip, reporting progress as the bytes actually land.

        `extractall` gives no sign of life, and on a multi-gigabyte disc image
        that is a long silence in a panel whose whole job is saying what is
        happening.

        Counted in bytes rather than in files, and *within* each file rather
        than after it. Per-file was the obvious way to do this and it is
        useless here: a ROM archive is very nearly always one big file, so the
        percentage went from 0 to 100 in a single step with several minutes of
        nothing in between - which is exactly the silence this was meant to
        fill. Copying the member out in chunks is what makes the bar move.
        """
        with zipfile.ZipFile(archive) as zf:
            members = zf.infolist()
            total = sum(m.file_size for m in members) or 1
            written = 0
            for member in members:
                if job.id in self._stop:      # cancelled mid-unpack
                    raise _Stopped
                written = self._unzip_member(job, zf, member, dest, written, total)

    def _unzip_member(self, job: Job, zf: zipfile.ZipFile,
                      member: zipfile.ZipInfo, dest: Path,
                      written: int, total: int) -> int:
        """Write one member out in chunks. Returns the new running total.

        Only a plain, non-empty file is copied by hand - that is the only case
        with anything to measure. Directories, empty files, and any name this
        cannot place safely are handed to `zf.extract`, which owns the rules
        about drive letters, leading slashes and `..` in member names.
        """
        if member.is_dir() or member.file_size <= 0:
            zf.extract(member, dest)
            return written

        target = _zip_target(member.filename, dest)
        if target is None:
            # An unplaceable name. zipfile sanitises harder than this does
            # (illegal characters on Windows, reserved device names), so it
            # gets the member and the bar simply doesn't move for it.
            zf.extract(member, dest)
            return written + member.file_size

        last = 0.0
        started_at = written
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            with zf.open(member) as src, open(target, "wb") as out:
                while True:
                    if job.id in self._stop:      # cancelled mid-file
                        raise _Stopped
                    chunk = src.read(CHUNK)
                    if not chunk:
                        break
                    out.write(chunk)
                    written += len(chunk)
                    # Four times a second. The panel polls slower than that,
                    # and taking the lock for every chunk would cost more than
                    # the copy it is reporting on.
                    now = time.time()
                    if now - last >= 0.25:
                        last = now
                        with self._lock:
                            job.extract_pct = min(100.0, written / total * 100)
        except OSError:
            # A name this filesystem won't take after all. Let zipfile have
            # its go, and rewind the count past the half-written attempt so
            # the total stays honest.
            written = started_at + member.file_size
            zf.extract(member, dest)

        with self._lock:
            job.extract_pct = min(100.0, written / total * 100)
        return written

    def _un7z(self, job: Job, archive: Path, dest: Path) -> None:
        """Unpack a .7z, reporting the same percentage a zip does.

        A .7z cannot be walked a member at a time the way a zip can - the
        files share one compressed stream, so pulling them out one by one
        re-reads that stream from the start for each. py7zr instead calls a
        callback as it goes, which is what this hands it.

        The sizes come from the archive listing rather than from the callback,
        because what the callback is handed has moved between py7zr versions
        while `list()` has not. Anything unexpected leaves the percentage at
        zero, and the panel falls back to the indeterminate bar and the word
        "Extracting…" - which is all a .7z ever showed before.
        """
        import py7zr  # noqa: PLC0415

        with py7zr.SevenZipFile(archive, "r") as sz:
            try:
                sizes = {f.filename: f.uncompressed for f in sz.list()
                         if not f.is_directory}
            except Exception:  # noqa: BLE001 - a header we can't read is not fatal
                sizes = {}
            total = sum(sizes.values())

            if not total:
                sz.extractall(path=dest)
                return
            try:
                sz.extractall(path=dest,
                              callback=self._seven_zip_progress(job, sizes, total))
            except TypeError:
                # A build whose extractall takes no callback. Unpack it
                # anyway; the bar just has nothing to say while it runs.
                sz.reset()
                sz.extractall(path=dest)

    def _seven_zip_progress(self, job: Job, sizes: dict[str, int], total: int):
        """A py7zr callback that keeps `job.extract_pct` moving.

        Built here rather than at module level because py7zr is optional -
        importing its base class at startup would make a missing .7z library
        break plain zip downloads too.

        Progress is counted twice over, deliberately. `report_end` is the
        honest one: a file is out, add its size. But a .7z holding a single
        4 GB disc image only ends once, so `report_update` also feeds in the
        bytes decompressed so far within the file being worked on - capped at
        that file's own size, so the two can never add up to more than the
        archive.
        """
        from py7zr.callbacks import ExtractCallback  # noqa: PLC0415

        lock, stopping = self._lock, self._stop

        class _Progress(ExtractCallback):
            def __init__(self) -> None:
                self.done = 0        # files finished, in uncompressed bytes
                self.current = 0     # ...and how far into the one in hand
                self.limit = 0       # how big that one is

            def _push(self) -> None:
                with lock:
                    job.extract_pct = min(
                        100.0, (self.done + self.current) / total * 100)

            def report_start_preparation(self) -> None:
                pass

            def report_start(self, processing_file_path, processing_bytes) -> None:
                if job.id in stopping:           # cancelled mid-unpack
                    raise _Stopped
                self.current = 0
                self.limit = sizes.get(processing_file_path, 0)

            def report_update(self, decompressed_bytes) -> None:
                try:
                    self.current = min(self.limit,
                                       self.current + int(decompressed_bytes))
                except (TypeError, ValueError):
                    return
                self._push()

            def report_end(self, processing_file_path, wrote_bytes) -> None:
                size = sizes.get(processing_file_path)
                if size is None:
                    try:
                        size = int(wrote_bytes)
                    except (TypeError, ValueError):
                        size = 0
                self.done += size
                self.current = self.limit = 0
                self._push()

            def report_warning(self, message) -> None:
                pass

            def report_postprocess(self) -> None:
                pass

        return _Progress()

    @staticmethod
    def _content_length(resp, offset: int) -> int:
        headers = getattr(resp, "headers", {})
        rng = headers.get("Content-Range")
        if rng and "/" in rng:
            try:
                return int(rng.rsplit("/", 1)[1])
            except ValueError:
                pass
        try:
            return int(headers.get("Content-Length") or 0) + offset
        except (TypeError, ValueError):
            return 0

    def _wait_for_room(self, size: int, job: Job) -> None:
        """Hold a chunk back until the ceiling allows it, and while a game is
        running.

        One budget for the whole app rather than one per worker: what somebody
        wants capped is the line, and three workers each politely staying
        under 500 KB/s is 1.5 MB/s on the wire.

        A plain token bucket. `_tokens` is how many bytes may go out right
        now, refilled at the rate that was asked for; a chunk that cannot be
        paid for sleeps for exactly as long as the shortfall costs. It is
        deliberately not clever - it does not try to reshape a burst, because
        the thing being protected is somebody else's video call, and being
        approximately right every half second is all that takes.
        """
        # Read at most a few times a second, not once per chunk. This is
        # called for every 256 KB that arrives, and it was opening the
        # settings file and parsing it as JSON each time - for a limit that
        # is almost always "none", answered and thrown away. At the speeds
        # archive.org manages that costs nothing; on a fast source it is a
        # disk read every few milliseconds for an answer that has not changed.
        now = time.monotonic()
        settings = self._settings_cache
        if (settings is None or now - self._settings_at > 0.5
                or self._settings_stamp != _settings_stamp):
            settings = load_settings()
            self._settings_cache = settings
            self._settings_at = now
            self._settings_stamp = _settings_stamp

        # A game is on, and the setting says to get out of the way. Checked in
        # the same place as the ceiling because it is the same question - may
        # this chunk go now - and it means a running download eases off rather
        # than being torn down and restarted.
        # Imported here, not at the top: library.py imports this module, so
        # the other direction has to happen once something is actually asking.
        from .library import playing_now  # noqa: PLC0415

        while settings.get("pause_while_playing") and playing_now():
            if job.id in self._stop:
                raise _Stopped
            time.sleep(1.0)
            settings = load_settings()          # deliberately fresh: this
            self._settings_cache = settings     # loop waits on it changing
            self._settings_at = time.monotonic()

        limit = _sane_speed(settings.get("speed_limit")) * 1024
        if not limit:
            with self._rate_lock:
                self._tokens, self._filled = 0.0, 0.0   # nothing owed later
            return

        with self._rate_lock:
            now = time.monotonic()
            if not self._filled:
                self._filled, self._tokens = now, float(limit)
            self._tokens = min(float(limit),
                               self._tokens + (now - self._filled) * limit)
            self._filled = now
            self._tokens -= size
            owed = -self._tokens / limit if self._tokens < 0 else 0.0

        # Slept outside the lock, or the other workers would queue behind this
        # one instead of sharing the ceiling with it.
        if owed > 0:
            time.sleep(min(owed, 5.0))

    def _stream(self, job: Job, resp, part: Path, offset: int,
                watch: bool = True) -> None:
        chunks = (resp.iter_content(CHUNK) if hasattr(resp, "iter_content")
                  else iter(lambda: resp.read(CHUNK), b""))
        written = offset
        last_t, last_b = time.time(), offset
        # The rolling window this connection is judged over, and the best any
        # window has managed. See _Crawling.
        win_t, win_b = time.time(), offset

        with open(part, "ab" if offset else "wb") as fh:
            for chunk in chunks:
                if job.id in self._stop:
                    raise _Stopped
                if not chunk:
                    # A keep-alive with no payload still says the far end is
                    # alive, so only real silence counts against it.
                    if watch and time.time() - win_t > STALL_SECONDS:
                        raise _Crawling
                    continue
                # Before the write rather than after: a chunk already on the
                # disk cannot be un-hurried, and sleeping first is what keeps
                # the average where it was asked to be.
                self._wait_for_room(len(chunk), job)
                fh.write(chunk)
                written += len(chunk)

                now = time.time()
                if now - last_t >= 0.5:
                    rate = (written - last_b) / (now - last_t)
                    with self._lock:
                        # Smooth it so the UI doesn't flicker.
                        job.speed = rate if not job.speed else job.speed * 0.7 + rate * 0.3
                        job.done = written
                    last_t, last_b = now, written

                if watch and now - win_t >= SLOW_WINDOW:
                    rate = (written - win_b) / (now - win_t)
                    best = max(job.best_rate, rate)
                    # Only against what this download has already achieved,
                    # and only while there is enough left for it to matter.
                    left = job.total - written if job.total else 0
                    if (job.best_rate and rate < job.best_rate * SLOW_SHARE
                            and left > 8 * 1024 * 1024
                            and job.slow_retries < SLOW_GIVEUP):
                        with self._lock:
                            job.slow_retries += 1
                            job.best_rate = best
                        raise _Crawling
                    with self._lock:
                        job.best_rate = best
                    win_t, win_b = now, written

        with self._lock:
            job.done = written


def _prune_empty(start: Path, stop: Path) -> None:
    """Remove the empty folders a torrent left behind, up to but not past
    `stop`. Only ever empty ones, and never the console's own folder."""
    here = start
    for _ in range(8):
        try:
            if here == stop or stop not in here.parents or any(here.iterdir()):
                return
            here.rmdir()
        except OSError:
            return
        here = here.parent


def _zip_target(name: str, dest: Path) -> Path | None:
    """Where a zip member should be written, or None to let zipfile decide.

    Extracting by hand is what makes the progress bar move, and it means this
    has to answer the question `ZipFile.extract` normally answers for itself:
    a member is free to call itself `..\\..\\autorun.inf` or `C:\\Windows\\x`,
    and writing that where it asks is the classic zip-slip. So the name is
    stripped the way zipfile strips it - no drive, no root, no `.` or `..`
    component - and then the result is *checked* to be inside `dest` rather
    than assumed to be. Anything that fails either step returns None and goes
    back to zipfile, which sanitises harder still.
    """
    arcname = name.replace("/", os.path.sep)
    if os.path.altsep:
        arcname = arcname.replace(os.path.altsep, os.path.sep)
    arcname = os.path.splitdrive(arcname)[1]
    skip = ("", os.path.curdir, os.path.pardir)
    arcname = os.path.sep.join(p for p in arcname.split(os.path.sep)
                               if p not in skip)
    if not arcname:
        return None

    target = dest / arcname
    try:
        if not target.resolve().is_relative_to(dest.resolve()):
            return None
    except (OSError, ValueError):
        return None
    return target


class _Stopped(Exception):
    """Raised inside the stream loop when a job is paused or cancelled."""


manager = Manager()
