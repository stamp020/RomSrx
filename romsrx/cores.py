"""Getting the right libretro core, without sending anyone to a website.

RetroArch opens nothing on its own: every console needs a core, and picking
one means knowing which of several does the job. This fetches the core from
the same place RetroArch's own updater does and puts it where RetroArch looks.

Which core is "best" is decided here on one criterion: whether achievements
work with it. That is what this app is for, and it is not always the most
accurate or the fastest core - bsnes is closer to a Super Nintendo than
Snes9x is, and Snes9x is the one RetroAchievements is built and tested
against. Where the choice is genuinely open, the more widely used one wins,
because it is the one most likely to already be installed and working.
"""

from __future__ import annotations

import io
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

from . import downloads

USER_AGENT = "RomSrx/1.0 (+https://github.com/)"
TIMEOUT = 120
MAX_CORE = 96 * 1024 * 1024        # a core is a few megabytes; this is slack

# Where the libretro project publishes its builds. Nightlies are all there is
# - the same ones RetroArch's own Core Updater installs - so this is not a
# lesser source, it is the source.
BUILDBOT = "https://buildbot.libretro.com/nightly/{platform}/{arch}/latest/"

# Console -> the core to fetch, named as the buildbot names it. Only consoles
# RetroArch actually serves well are here: a PlayStation 2 or a Wii is better
# off with its own emulator, and offering a core for one would be worse advice
# than offering none.
BEST = {
    "NES/Famicom":                "mesen",
    "Famicom Disk System":        "mesen",
    "SNES/Super Famicom":         "snes9x",
    "Game Boy":                   "gambatte",
    "Game Boy Color":             "gambatte",
    "Game Boy Advance":           "mgba",
    "Nintendo 64":                "mupen64plus_next",
    "Nintendo DS":                "melonds",
    "Genesis/Mega Drive":         "genesis_plus_gx",
    "Master System":              "genesis_plus_gx",
    "Game Gear":                  "genesis_plus_gx",
    "Sega CD":                    "genesis_plus_gx",
    "SG-1000":                    "genesis_plus_gx",
    "32X":                        "picodrive",
    "Sega Saturn":                "mednafen_saturn",
    "PlayStation":                "swanstation",
    "PSP":                        "ppsspp",
    "PC Engine/TurboGrafx-16":    "mednafen_pce",
    "PC Engine CD/TurboGrafx-CD": "mednafen_pce",
    "Atari 2600":                 "stella",
    "Atari 7800":                 "prosystem",
    "Atari Lynx":                 "handy",
    "Atari Jaguar":               "virtualjaguar",
    "Neo Geo Pocket":             "mednafen_ngp",
    "Virtual Boy":                "mednafen_vb",
    "WonderSwan":                 "mednafen_wswan",
    "Pokemon Mini":               "pokemini",
}


def core_for(console: str) -> str:
    """The core this app would choose for a console, or "" if it has no view."""
    return BEST.get(console, "")


def _platform() -> tuple[str, str, str]:
    """(platform, architecture, file extension) for this machine."""
    import platform  # noqa: PLC0415
    import sys  # noqa: PLC0415

    bits64 = sys.maxsize > 2**32
    if sys.platform == "win32":
        return "windows", "x86_64" if bits64 else "x86", ".dll"
    if sys.platform == "darwin":
        arm = platform.machine().lower() in ("arm64", "aarch64")
        return "apple/osx", "arm64" if arm else "x86_64", ".dylib"
    arm = platform.machine().lower() in ("aarch64", "arm64")
    return "linux", "arm64" if arm else "x86_64", ".so"


def cores_dir(console: str) -> Path | None:
    """Where RetroArch keeps its cores, worked out from the program itself.

    Returns None when the console's emulator is not RetroArch - there is no
    sensible place to put a libretro core for something that cannot load one,
    and guessing would litter somebody's folders.
    """
    program = downloads.emulator_for(console)
    if not program or "retroarch" not in program.name.lower():
        return None
    beside = program.parent / "cores"
    if beside.is_dir():
        return beside
    # A system-installed RetroArch keeps cores in the user's own folder
    # instead of beside the binary, which is the usual case on Linux.
    import os  # noqa: PLC0415
    import sys  # noqa: PLC0415
    if sys.platform == "win32":
        fallback = Path(os.environ.get("APPDATA", Path.home())) / "RetroArch" / "cores"
    else:
        fallback = Path.home() / ".config" / "retroarch" / "cores"
    return fallback if fallback.is_dir() else beside


def installed_core(console: str) -> Path | None:
    """The chosen core for this console, if it is already on the machine."""
    name = core_for(console)
    folder = cores_dir(console)
    if not name or not folder:
        return None
    _, _, suffix = _platform()
    found = folder / f"{name}_libretro{suffix}"
    return found if found.is_file() else None


def fetch_core(name: str) -> tuple[str, bytes]:
    """Download one core from the buildbot, unzipped. (filename, bytes)."""
    platform_, arch, suffix = _platform()
    filename = f"{name}_libretro{suffix}"
    url = (BUILDBOT.format(platform=platform_, arch=arch)
           + urllib.parse.quote(filename + ".zip"))
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:  # noqa: S310
            blob = response.read(MAX_CORE + 1)
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            raise CoreError(
                f"The libretro project does not publish {name} for this "
                "system.") from exc
        raise CoreError(f"The core could not be downloaded: HTTP {exc.code}") from exc
    except (urllib.error.URLError, OSError, TimeoutError) as exc:
        raise CoreError(f"The core could not be downloaded: {exc}") from exc

    if len(blob) > MAX_CORE:
        raise CoreError("That download is far larger than a core.")
    try:
        with zipfile.ZipFile(io.BytesIO(blob)) as archive:
            inside = [n for n in archive.namelist() if n.endswith(suffix)]
            if not inside:
                raise CoreError("That download holds no core.")
            return Path(inside[0]).name, archive.read(inside[0])
    except zipfile.BadZipFile as exc:
        raise CoreError("The downloaded core could not be opened.") from exc


class CoreError(Exception):
    """Something about finding, fetching or placing a core."""


def install(console: str) -> dict:
    """Make sure this console's core is present, and say where it is.

    Already installed is a success rather than a no-op: the point of the
    button is to end with a working path in the box, and it does.
    """
    name = core_for(console)
    if not name:
        raise CoreError(f"RomSrx has no core to recommend for {console}. "
                        "This console is better served by its own emulator.")

    folder = cores_dir(console)
    if folder is None:
        raise CoreError("Set RetroArch as this console's emulator first - "
                        "the core has to go in its cores folder.")

    already = installed_core(console)
    if already:
        return {"path": str(already), "core": name, "installed": False}

    filename, blob = fetch_core(name)
    try:
        folder.mkdir(parents=True, exist_ok=True)
        target = folder / filename
        target.write_bytes(blob)
    except OSError as exc:
        raise CoreError(f"The core could not be saved: {exc}") from exc
    return {"path": str(target), "core": name, "installed": True}
