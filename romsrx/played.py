"""Working out which games were played outside this app.

The app knows about the games it launched itself - it started the emulator, so
it wrote the entry. It knows nothing about the far more common case: opening
RetroArch, or Dolphin, or PCSX2, and picking a game there.

The obvious answer is to read each emulator's own history, and it is a worse
answer than it looks. Every emulator stores it differently, several store no
timestamp at all, and several key it by something other than the file - Dolphin
records play time against a six-character disc id, so matching it to a file on
disk means parsing disc headers. Each one supported is one emulator's worth of
coverage, and there are dozens.

What every emulator does, without exception, is *open the ROM*. The filesystem
records that: `st_atime` is the last time something read the file. So the
signal used here is a file that has been read more recently than it was
written - which is emulator-agnostic, needs no configuration, and works for
emulators nobody has heard of.

It is inference, and it is treated as such:

  * Only the *data* files count. A disc game's `.cue` is read by this app's own
    library scan, so a scan would otherwise make every disc game look played;
    the `.bin` beside it is read by the emulator and by nothing else here.
  * The read has to be meaningfully later than the write. Downloading and
    extracting a game leaves atime and mtime together, so a fresh download does
    not arrive looking like it has been played.
  * A sweep is not a play. Antivirus, a backup, or copying the library to
    another drive reads hundreds of files within a few minutes of each other,
    and that shape is thrown away rather than turned into a hundred entries.

Where the filesystem isn't recording reads at all - Windows can be told not to,
and some of them are - none of this fires and nothing is claimed.
"""

from __future__ import annotations

import sys
import time

# Read by our own library scan to find out which files belong to a disc image,
# so a fresh access time on one of these is as likely to be us as the emulator.
# The data files they point at are the evidence instead.
DESCRIPTORS = {"cue", "m3u", "gdi", "ccd", "toc", "sbi"}

# How far a read has to fall after the write before it counts as a separate
# event. Writing a file leaves the two within moments of each other; the
# margin is what keeps "downloaded" from reading as "played".
MIN_LEAD = 120.0

# A play session is a few games over an evening. A virus scan is hundreds of
# files inside a minute. More than this many games sharing a window is the
# second shape, and none of them are counted.
SWEEP_WINDOW = 300.0
SWEEP_COUNT = 12

# Nothing before this is believable - a filesystem with no access-time
# tracking often reports the epoch, or the file's creation date from a
# restore.
OLDEST = 365 * 24 * 3600.0


def is_descriptor(name: str) -> bool:
    return name.rsplit(".", 1)[-1].lower() in DESCRIPTORS if "." in name else False


def evidence(atime: float, mtime: float) -> float:
    """The moment this file says it was opened, or 0 for "no evidence".

    Split out so the rule is in one place and can be tested without a disk.
    """
    now = time.time()
    if not atime or not mtime:
        return 0.0
    # A clock that has gone backwards, or a file stamped in the future, says
    # nothing useful. Neither does one from before the app existed.
    if atime > now + 3600 or atime < now - OLDEST:
        return 0.0
    return atime if atime - mtime >= MIN_LEAD else 0.0


def _drop_sweeps(times: dict[str, float]) -> dict[str, float]:
    """Throw away clusters that look like something reading the whole library.

    Kept deliberately blunt. The alternative to dropping a suspicious cluster
    is showing the user eleven games they did not play, in the one row on the
    shelf that is supposed to be the games they did.
    """
    if len(times) <= SWEEP_COUNT:
        return times

    ordered = sorted(times.items(), key=lambda kv: kv[1])
    keep: dict[str, float] = {}
    start = 0
    for end in range(len(ordered) + 1):
        # Extend the run while everything in it falls inside one window.
        if end < len(ordered) and ordered[end][1] - ordered[start][1] <= SWEEP_WINDOW:
            continue
        run = ordered[start:end]
        if len(run) < SWEEP_COUNT:
            keep.update(run)
        start = end
    return keep


def detect(games: list[dict]) -> int:
    """Stamp `playedAt` on every game that looks like it was opened.

    Reads nothing: the access times were already collected by the scan that
    had to stat these files anyway. Returns how many were stamped.
    """
    found: dict[str, float] = {}
    for game in games:
        when = evidence(game.get("_atime") or 0.0, game.get("_mtime") or 0.0)
        if when:
            found[game["path"]] = when

    found = _drop_sweeps(found)
    for game in games:
        game["playedAt"] = round(found.get(game["path"], 0.0), 3)
        # Internal to the scan; the page has no use for either.
        game.pop("_atime", None)
        game.pop("_mtime", None)
    return len(found)


def best_read(files: list[tuple[str, float, float]]) -> tuple[float, float]:
    """Pick the file that speaks for a game: (atime, mtime).

    A game is often several files - a disc image and its tracks, a multi-disc
    set - and the one worth asking is the most recently read *data* file.
    Descriptors are excluded because this app reads them itself. When a game
    is nothing but descriptors, there is nothing to go on and it says so.
    """
    best = (0.0, 0.0)
    for name, atime, mtime in files:
        if is_descriptor(name) or atime <= best[0]:
            continue
        best = (atime, mtime)
    return best


def tracking_enabled() -> bool:
    """Whether this machine records when a file was read.

    Windows can be told not to, and on a volume where it has been, none of
    this can work - so the page can say that rather than showing an empty row
    and leaving the user to wonder. Anything that isn't Windows is assumed to
    keep access times, which is the usual default; being wrong there costs a
    row that stays empty, which is what it would have been anyway.
    """
    if sys.platform != "win32":
        return True
    try:
        import winreg  # noqa: PLC0415 - Windows only

        with winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SYSTEM\CurrentControlSet\Control\FileSystem",
        ) as key:
            value, _ = winreg.QueryValueEx(key, "NtfsDisableLastAccessUpdate")
    except (OSError, ValueError):
        # Not set at all is the old default, which was "enabled".
        return True
    # The setting is the low two bits: 0 and 2 are the "enabled" pair
    # (user-managed and system-managed), 1 and 3 the matching "disabled" one.
    # Everything above them is a flag - Windows 10 stores system-managed as
    # 0x80000002, not 2, so comparing the whole value reads as "disabled" on a
    # machine where it is very much enabled.
    try:
        return (int(value) & 0b11) in (0, 2)
    except (TypeError, ValueError):
        return True
