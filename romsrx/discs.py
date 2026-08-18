"""Hashing a game that lives on a disc rather than in a cartridge.

A cartridge is a run of bytes and rahash.py can hash it end to end. A disc is
a filesystem, and RetroAchievements does not hash the disc - it hashes the
program the disc boots. So the work here is finding that program: read
SYSTEM.CNF out of the ISO9660 directory, take the executable it names, and
hash that name followed by its contents.

Ported from rcheevos - hash_disc.c and cdreader.c - the same way the cartridge
rules were, function by function rather than from a description of them.
Every number here is an offset into somebody else's format, and being nearly
right produces a well-formed hash that belongs to nothing.

What is covered: PlayStation and PlayStation 2, from an .iso or a raw .bin,
including one named by a .cue or sitting alone in a folder.

What is not, and why:

  .chd    the format most disc libraries are actually kept in. It is
          compressed, and reading one means implementing its hunk format -
          a project rather than a function.
  .rvz    the same problem wearing Dolphin's colours.
  GameCube, Wii, Dreamcast, Saturn, Sega CD, PSP, PC-FX, Neo Geo CD
          each has a rule of its own in hash_disc.c. They are absent rather
          than approximated.

The honest failure is "not checked". Nothing here may guess: a disc that
cannot be read must never come back as a copy that failed.
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

# The twelve bytes every raw CD sector opens with. Their presence is what
# tells a 2352-byte-per-sector image from a plain 2048 one - a .cue file is
# allowed to be wrong about that, so the image itself is asked instead.
SYNC = bytes([0x00] + [0xFF] * 10 + [0x00])

# ISO9660 puts a volume descriptor at sector 16, and whichever of the two is
# there always carries "CD001". That is the confirmation that a guess at the
# geometry was the right guess.
MAGIC = b"CD001"
TOC_SECTOR = 16

DATA = 2048                      # a sector's payload, whatever its wrapper
CAP = 64 * 1024 * 1024           # rcheevos' MAX_BUFFER_SIZE, as everywhere else

# This app's console names -> the key naming the executable in SYSTEM.CNF, and
# what the disc writes in front of the filename.
CONSOLES = {
    "PlayStation": ("BOOT", "cdrom:"),
    "PlayStation 2": ("BOOT2", "cdrom0:"),
}

IMAGES = (".iso", ".bin", ".img")
DESCRIPTORS = (".cue",)


def handles(console: str) -> bool:
    return (console or "").strip() in CONSOLES


class Track:
    """One disc image, read a sector at a time.

    The first track only. Every executable this looks for is on it, and a
    second track on a PlayStation disc is nearly always audio.
    """

    def __init__(self, handle) -> None:
        self.handle = handle
        self.sector_size = 0
        self.header_size = 0
        self._measure()

    def _measure(self) -> None:
        """Work out the geometry by looking, not by trusting the extension."""
        for size in (2352, 2336):
            head = self._at(TOC_SECTOR * size, 32)
            if len(head) == 32 and head[:12] == SYNC:
                self.sector_size = size
                # Mode 2 Form 1 carries eight more bytes of subheader than
                # Mode 1 does, and where "CD001" lands is what says which.
                self.header_size = 24 if head[25:30] == MAGIC else 16
                return
        head = self._at(TOC_SECTOR * DATA, 32)
        if len(head) == 32 and head[1:6] == MAGIC:
            self.sector_size = DATA
            self.header_size = 0

    def _at(self, offset: int, count: int) -> bytes:
        try:
            self.handle.seek(offset)
            return self.handle.read(count)
        except OSError:
            return b""

    def usable(self) -> bool:
        return self.sector_size > 0

    def sector(self, number: int, count: int = DATA) -> bytes:
        """`count` bytes of one sector's payload, skipping its wrapper."""
        if not self.sector_size:
            return b""
        return self._at(number * self.sector_size + self.header_size,
                        min(count, DATA))


def _u16(data: bytes, at: int) -> int:
    return int.from_bytes(data[at:at + 2], "little")


def _u24(data: bytes, at: int) -> int:
    return int.from_bytes(data[at:at + 3], "little")


def _u32(data: bytes, at: int) -> int:
    return int.from_bytes(data[at:at + 4], "little")


def find(track: Track, path: str) -> tuple[int, int]:
    """(sector, size) of a file in the disc's filesystem, or (0, 0).

    `path` is backslash-separated, the way a boot line writes it. A path with
    a folder in it is resolved a component at a time, which is what the
    recursion is: find the folder, then look inside it.
    """
    path = path.lstrip("\\")
    if not path:
        return (0, 0)

    at = path.rfind("\\")
    if at >= 0:
        sector, _ = find(track, path[:at])
        if not sector:
            return (0, 0)
        name = path[at + 1:]
        spans = 1
    else:
        # The primary volume descriptor. Its root directory record sits 156
        # bytes in, and the sector holding the table of contents is 2 bytes
        # into that record.
        volume = track.sector(TOC_SECTOR, 256)
        if len(volume) < 170:
            return (0, 0)
        sector = _u24(volume, 156 + 2)
        block = _u16(volume, 128)
        # A big directory runs past one sector; its own record says how far.
        spans = max(1, _u32(volume, 156 + 10) // block) if block else 1
        name = path

    wanted = name.upper().encode("ascii", "replace")
    for _ in range(spans):
        block = track.sector(sector)
        if not block:
            return (0, 0)
        at = 0
        while at + 33 < len(block):
            length = block[at]
            if not length:
                break                    # end of the records in this sector
            size = block[at + 32]
            listed = block[at + 33:at + 33 + size]
            # "NAME;1" for a file and "NAME" for a directory, so a match is
            # the whole name, or the whole name and then the version marker.
            if listed[:len(wanted)].upper() == wanted and (
                    size == len(wanted)
                    or listed[len(wanted):len(wanted) + 1] == b";"):
                return (_u24(block, at + 2), _u32(block, at + 10))
            at += length
        sector += 1
    return (0, 0)


def _contents(track: Track, sector: int, size: int) -> bytes:
    """Read a file out of the disc, a sector at a time."""
    size = min(size, CAP)
    out = bytearray()
    while size > 0:
        block = track.sector(sector, min(DATA, size))
        if not block:
            break
        out += block
        size -= len(block)
        sector += 1
    return bytes(out)


def _boot_name(text: str, key: str, prefix: str) -> str:
    """The executable a boot line names, without its wrapping.

    SYSTEM.CNF writes it as `BOOT2 = cdrom0:\\SLUS_123.45;1`, and the parts
    that are not the filename - the device, the leading slashes, the version
    marker - all come off here.
    """
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.upper().startswith(key.upper()):
            continue
        rest = stripped[len(key):].lstrip()
        if not rest.startswith("="):
            continue
        rest = rest[1:].strip()
        if rest.lower().startswith(prefix.lower()):
            rest = rest[len(prefix):]
        rest = rest.lstrip("\\")
        # Up to the first space or the version marker, which is where the
        # name ends and ";1" or a trailing comment begins.
        return re.split(r"[\s;]", rest, maxsplit=1)[0]
    return ""


def hash_playstation(handle, console: str) -> tuple[str, str]:
    """The md5 RetroAchievements knows a PlayStation disc by.

    The executable's name is hashed before its contents: a handful of games
    share one engine and differ only in their data files, and the serial in
    the boot filename is the only thing telling those apart.
    """
    key, prefix = CONSOLES[console]
    track = Track(handle)
    if not track.usable():
        return "", "notrom"

    name = ""
    size = 0
    sector, _ = find(track, "SYSTEM.CNF")
    if sector:
        text = track.sector(sector).split(b"\0", 1)[0].decode("latin-1", "replace")
        name = _boot_name(text, key, prefix)
        sector, size = find(track, name) if name else (0, 0)
    if not sector and console == "PlayStation":
        # A few early discs carry no SYSTEM.CNF and boot a fixed name.
        sector, size = find(track, "PSX.EXE")
        name = "PSX.EXE" if sector else ""
    if not sector or not name:
        return "", "notrom"

    if console == "PlayStation":
        head = track.sector(sector, 32)
        if len(head) < 32:
            return "", "notrom"
        # A PS-X EXE header states the size of what follows it, so the
        # header's own 2048 bytes go back on to include it in the hash.
        if head[:7] == b"PS-X EX":
            size = _u32(head, 28) + 2048

    if size <= 0:
        return "", "notrom"

    digest = hashlib.md5()  # noqa: S324 - the site's choice, not a security one
    digest.update(name.encode("ascii", "replace"))
    digest.update(_contents(track, sector, size))
    return digest.hexdigest(), ""


def image_in(path: Path) -> Path | None:
    """The disc image behind a library entry, or None if there isn't one.

    An entry is the image itself, a .cue naming one, or a folder holding
    either. A multi-disc game - several images, or an .m3u - is left alone:
    which disc a set was built from is a question this cannot answer, and
    picking one would answer it wrongly about half the time.
    """
    if path.is_dir():
        inside = [one for one in sorted(path.rglob("*")) if one.is_file()]
        # A single .cue is asked first, even when there are several images
        # beside it. It is the thing that knows which of them is the disc -
        # a folder holding a dump and a spare copy of one of its tracks is
        # ambiguous by count and perfectly clear to the descriptor.
        cues = [one for one in inside if one.suffix.lower() in DESCRIPTORS]
        if len(cues) == 1:
            found = image_in(cues[0])
            if found:
                return found
        if cues:
            return None                  # several discs, or a .cue naming none
        images = [one for one in inside if one.suffix.lower() in IMAGES]
        return images[0] if len(images) == 1 else None

    if path.suffix.lower() in DESCRIPTORS:
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return None
        # Only the names it lists, never a path: a hand-edited .cue can say
        # anything, and the only use made of it is picking a file beside it.
        named = [Path(one).name
                 for one in re.findall(r'FILE\s+"([^"]+)"', text, re.I)]
        found = [path.with_name(one) for one in named
                 if Path(one).suffix.lower() in IMAGES]
        found = [one for one in found if one.is_file()]
        return found[0] if len(found) == 1 else None

    return path if path.suffix.lower() in IMAGES else None


def md5(path, console: str) -> tuple[str, str]:
    """(md5, reason) for one disc. Never raises."""
    if not handles(console):
        return "", "unsupported"
    try:
        image = image_in(Path(path))
        if image is None:
            return "", "unsupported"
        with open(image, "rb") as handle:
            return hash_playstation(handle, console)
    except (OSError, ValueError):
        return "", "unreadable"
    except Exception:  # noqa: BLE001 - one odd disc must not stop a sweep
        return "", "unreadable"
