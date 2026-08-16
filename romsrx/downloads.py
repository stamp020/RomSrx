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
    data["workers"] = _sane_workers(data["workers"])
    return data


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
               "per_console", "clear_when_done", "patch_folder", "patch_replace")
    current.update({k: v for k, v in data.items() if k in allowed})
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
    with open(SETTINGS_PATH, "w", encoding="utf-8") as fh:
        json.dump(current, fh, indent=2)
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
        }


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
        self._workers: list[threading.Thread] = []
        self._slots = Slots(DEFAULT_WORKERS)
        self._started = False

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
                job = Job(
                    id=self._next_id, url=url,
                    filename=safe_name(item.get("filename") or "download"),
                    console=item.get("console", ""), source=item.get("source", ""),
                    login=bool(item.get("login")),
                    total=int(item.get("size") or 0),
                    order=float(self._next_id),
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

        deleted = []
        if path:
            final = Path(path)
            for candidate in (final, Path(f"{final}.part")):
                if _remove_file(candidate):
                    deleted.append(candidate.name)
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
    PERSIST_FIELDS = ("id", "url", "filename", "console", "source", "login",
                      "paused_from", "total", "done", "status", "path",
                      "extracted", "error", "added", "order")

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

    def _open(self, session, url: str, offset: int):
        """Range request from `offset`. Returns (response, is_partial)."""
        headers = {"User-Agent": "RomSrx/0.1"}
        if offset:
            headers["Range"] = f"bytes={offset}-"
        if session is not None:
            resp = session.get(url, headers=headers, stream=True, timeout=60)
            if resp.status_code in TRANSIENT:
                resp.close()
                raise urllib.error.HTTPError(url, resp.status_code,
                                             "transient", None, None)
            resp.raise_for_status()
            return resp, resp.status_code == 206
        request = urllib.request.Request(url, headers=headers)
        resp = urllib.request.urlopen(request, timeout=60)
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

        if final.exists() and final.stat().st_size > 0:
            with self._lock:
                job.done = job.total = final.stat().st_size
                job.status = "done"
                job.finished = time.time()
                job.error = "already downloaded"
            return

        for attempt in range(1, RETRIES + 1):
            job.attempts = attempt
            offset = part.stat().st_size if part.exists() else 0
            try:
                resp, partial = self._open(session, job.url, offset)
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

            # Finished cleanly.
            part.replace(final)
            with self._lock:
                job.done = job.total = final.stat().st_size
                job.speed = 0.0
                job.path = str(final)
            self._maybe_extract(job, final)
            with self._lock:
                job.status = "done"
                job.finished = time.time()
            return

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

    def _stream(self, job: Job, resp, part: Path, offset: int) -> None:
        chunks = (resp.iter_content(CHUNK) if hasattr(resp, "iter_content")
                  else iter(lambda: resp.read(CHUNK), b""))
        written = offset
        last_t, last_b = time.time(), offset

        with open(part, "ab" if offset else "wb") as fh:
            for chunk in chunks:
                if job.id in self._stop:
                    raise _Stopped
                if not chunk:
                    continue
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

        with self._lock:
            job.done = written


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
