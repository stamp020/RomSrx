"""Applying a ROM patch, without asking anyone to go and find a tool.

A hack or a translation with an achievement set is never a finished ROM: it
is the original plus a patch, and until now that meant downloading the patch
here and applying it in Flips or Lunar IPS. Both of the formats that matter
are small and well described, so the app can do it.

Four are handled:

  * **BPS** - the modern one, and what RetroAchievements mostly publishes. It
    carries a CRC32 of the file it expects, of the result it should produce,
    and of itself. That is worth more than the patching: the usual reason
    patching fails is having the wrong dump of the original, and a format
    that says so is a format that can be checked before anything is written.
  * **IPS** - the old one. No checksums at all, so it is applied on trust;
    that is the format's limitation, not a shortcut taken here.
  * **xdelta (VCDIFF)** - rebuilt from the patch a window at a time. Big files
    are read through a memory map and written as they are decoded, so a
    three-gigabyte disc image costs megabytes of memory rather than gigabytes.
  * **PPF** - how disc patches have always been published. It names places in
    the file rather than rebuilding it, so patching a disc image means copying
    it and writing over a few hundred bytes.

One thing is refused by name: an xdelta patch using xdelta3's own secondary
compression. Reading it would mean implementing that compressor too, and
neither xdelta nor PPF carries a checksum this app can check a result against
- so a decoder that was subtly wrong would produce a file that looks fine and
is not. Saying so plainly is better.
"""

from __future__ import annotations

import io
import re
import shutil
import urllib.error
import urllib.parse
import urllib.request
import zipfile
import zlib
from pathlib import Path

IPS_MAGIC = b"PATCH"
IPS_END = b"EOF"
BPS_MAGIC = b"BPS1"
# xdelta/VCDIFF, so it can be named rather than called "not a patch".
VCDIFF_MAGIC = b"\xd6\xc3\xc4"

# A result built in memory has to be sane; one written to disk only has to be
# a disc image. A dual-layer DVD is a little under 9 GB, so this leaves room
# for one and still refuses a patch claiming something absurd.
MAX_STREAM_TARGET = 16 * 1024 * 1024 * 1024

# A patch that claims a target larger than this is not a ROM patch. Nothing
# this app deals with is anywhere near it, and the number is what stops a
# malformed length turning into an allocation the size of the disk.
MAX_TARGET = 512 * 1024 * 1024


class PatchError(Exception):
    """Something about the patch or the file it was given."""


def detect(patch: bytes) -> str:
    """Which format this is: "bps", "ips", "xdelta", or "" for none."""
    if patch[:4] == BPS_MAGIC:
        return "bps"
    if patch[:5] == IPS_MAGIC:
        return "ips"
    if patch[:3] == VCDIFF_MAGIC:
        return "xdelta"
    if patch[:3] == PPF_MAGIC and patch[3:5] in (b"10", b"20", b"30"):
        return "ppf"
    return ""


# ---------- BPS ----------

def _varint(patch: bytes, at: int) -> tuple[int, int]:
    """BPS's own number encoding: seven bits at a time, low first.

    The last byte is flagged rather than the continuing ones, and each further
    byte is biased by one so that no number has two encodings.
    """
    value, shift = 0, 1
    while True:
        if at >= len(patch):
            raise PatchError("The patch ends in the middle of a number.")
        byte = patch[at]
        at += 1
        value += (byte & 0x7F) * shift
        if byte & 0x80:
            return value, at
        shift <<= 7
        value += shift


def apply_bps(source: bytes, patch: bytes) -> bytes:
    """Apply a BPS patch, checking everything it gives us to check."""
    if patch[:4] != BPS_MAGIC or len(patch) < 4 + 3 + 12:
        raise PatchError("This is not a BPS patch.")

    # The last twelve bytes are three checksums, not actions.
    body_end = len(patch) - 12
    want_source, want_target, want_patch = (
        int.from_bytes(patch[body_end + n:body_end + n + 4], "little")
        for n in (0, 4, 8))

    if zlib.crc32(patch[:body_end + 8]) & 0xFFFFFFFF != want_patch:
        raise PatchError("The patch file is damaged.")

    at = 4
    source_size, at = _varint(patch, at)
    target_size, at = _varint(patch, at)
    metadata_size, at = _varint(patch, at)
    at += metadata_size

    if len(source) != source_size:
        raise PatchError(
            f"This patch is for a {source_size:,}-byte file, and this one is "
            f"{len(source):,} bytes. It is meant for a different release.")
    if zlib.crc32(source) & 0xFFFFFFFF != want_source:
        raise PatchError(
            "This patch is for a different dump of the game. The file is the "
            "right size but not the one it expects.")
    if target_size > MAX_TARGET:
        raise PatchError("The patch claims an implausibly large result.")

    out = bytearray(target_size)
    at_out = 0
    source_at = target_at = 0

    while at < body_end:
        action, at = _varint(patch, at)
        mode, length = action & 3, (action >> 2) + 1
        if at_out + length > target_size:
            raise PatchError("The patch writes past the end of its own result.")

        if mode == 0:                                   # copy from the same spot
            out[at_out:at_out + length] = source[at_out:at_out + length]
            at_out += length
        elif mode == 1:                                 # bytes carried in the patch
            out[at_out:at_out + length] = patch[at:at + length]
            at += length
            at_out += length
        else:                                           # copy from elsewhere
            offset, at = _varint(patch, at)
            delta = -(offset >> 1) if offset & 1 else (offset >> 1)
            if mode == 2:
                source_at += delta
                if source_at < 0 or source_at + length > len(source):
                    raise PatchError("The patch reads past the end of the file.")
                out[at_out:at_out + length] = source[source_at:source_at + length]
                source_at += length
                at_out += length
            else:
                target_at += delta
                if target_at < 0:
                    raise PatchError("The patch reads before the start of its result.")
                # Byte at a time on purpose: this is allowed to read what it
                # has only just written, which is how BPS encodes a repeat.
                for _ in range(length):
                    out[at_out] = out[target_at]
                    at_out += 1
                    target_at += 1

    if at_out != target_size:
        raise PatchError("The patch finished without filling the result.")
    if zlib.crc32(bytes(out)) & 0xFFFFFFFF != want_target:
        raise PatchError("The patched file did not come out as the patch expects.")
    return bytes(out)


# ---------- IPS ----------

def apply_ips(source: bytes, patch: bytes) -> bytes:
    """Apply an IPS patch.

    IPS carries no checksums of any kind, so there is nothing to verify
    against: it is applied exactly as written and the result is whatever that
    produces. The one sanity check available is that the file ends where it
    says it does.
    """
    if patch[:5] != IPS_MAGIC:
        raise PatchError("This is not an IPS patch.")

    out = bytearray(source)
    at = 5
    while True:
        if at + 3 > len(patch):
            raise PatchError("The patch ends without saying so.")
        if patch[at:at + 3] == IPS_END:
            at += 3
            break
        offset = int.from_bytes(patch[at:at + 3], "big")
        at += 3
        if at + 2 > len(patch):
            raise PatchError("The patch ends in the middle of a record.")
        size = int.from_bytes(patch[at:at + 2], "big")
        at += 2

        if size:                                        # a run of bytes
            chunk = patch[at:at + size]
            if len(chunk) != size:
                raise PatchError("The patch ends in the middle of a record.")
            at += size
        else:                                           # the same byte, repeated
            if at + 3 > len(patch):
                raise PatchError("The patch ends in the middle of a record.")
            run = int.from_bytes(patch[at:at + 2], "big")
            chunk = bytes([patch[at + 2]]) * run
            at += 3
            size = run

        if offset + size > MAX_TARGET:
            raise PatchError("The patch writes implausibly far into the file.")
        if offset + size > len(out):
            out.extend(b"\x00" * (offset + size - len(out)))
        out[offset:offset + size] = chunk

    # Some IPS patches end with three more bytes meaning "and cut it here".
    if at + 3 <= len(patch):
        cut = int.from_bytes(patch[at:at + 3], "big")
        if 0 < cut < len(out):
            del out[cut:]
    return bytes(out)


# ---------- xdelta (VCDIFF, RFC 3284) ----------

# The four things an instruction can say. NOOP is the filler in the half of a
# code table entry that holds only one instruction.
_NOOP, _ADD, _RUN, _COPY = 0, 1, 2, 3


def _build_code_table() -> list[tuple]:
    """The default code table, built the way RFC 3284 section 5.4 builds it.

    An instruction is one byte, which indexes this table of 256 entries; each
    entry is one or two instructions, so the common pairing of "copy a run,
    then add a few literal bytes" costs a single byte. A size of 0 in the
    table means the real size follows the index in the instruction stream.
    """
    table: list[tuple] = [((_RUN, 0, 0), (_NOOP, 0, 0))]
    table += [((_ADD, size, 0), (_NOOP, 0, 0)) for size in range(18)]
    for mode in range(9):
        table.append(((_COPY, 0, mode), (_NOOP, 0, 0)))
        table += [((_COPY, size, mode), (_NOOP, 0, 0)) for size in range(4, 19)]
    for mode in range(6):
        for add_size in range(1, 5):
            for copy_size in range(4, 7):
                table.append(((_ADD, add_size, 0), (_COPY, copy_size, mode)))
    for mode in range(6, 9):
        for add_size in range(1, 5):
            table.append(((_ADD, add_size, 0), (_COPY, 4, mode)))
    table += [((_COPY, 4, mode), (_ADD, 1, 0)) for mode in range(9)]
    return table


_CODE_TABLE = _build_code_table()
_NEAR_SLOTS, _SAME_SLOTS = 4, 3


def _vcd_int(data: bytes, at: int) -> tuple[int, int]:
    """A VCDIFF integer: base 128, most significant group first."""
    value = 0
    for _ in range(8):                  # eight groups is far past any real size
        if at >= len(data):
            raise PatchError("The patch ends in the middle of a number.")
        byte = data[at]
        at += 1
        value = (value << 7) | (byte & 0x7F)
        if not byte & 0x80:
            return value, at
    raise PatchError("The patch file is damaged.")


class _Addresses:
    """The two caches a COPY address can be expressed against.

    Most copies land near the last one, so an address is usually written as a
    small offset from a recent address rather than in full. Both caches are
    part of the format: encoder and decoder keep the same ones in step, and
    reading them differently produces a plausible-looking wrong file.
    """

    def __init__(self) -> None:
        self.near = [0] * _NEAR_SLOTS
        self.same = [0] * (_SAME_SLOTS * 256)
        self.slot = 0

    def remember(self, address: int) -> None:
        self.near[self.slot] = address
        self.slot = (self.slot + 1) % _NEAR_SLOTS
        self.same[address % (_SAME_SLOTS * 256)] = address

    def read(self, mode: int, here: int, data: bytes, at: int) -> tuple[int, int]:
        if mode == 0:                           # a plain address
            address, at = _vcd_int(data, at)
        elif mode == 1:                         # so far back from here
            back, at = _vcd_int(data, at)
            address = here - back
        elif mode - 2 < _NEAR_SLOTS:            # a step on from a recent one
            step, at = _vcd_int(data, at)
            address = self.near[mode - 2] + step
        else:                                   # one seen at this slot before
            if at >= len(data):
                raise PatchError("The patch ends in the middle of a record.")
            address = self.same[(mode - 2 - _NEAR_SLOTS) * 256 + data[at]]
            at += 1
        if address < 0:
            raise PatchError("The patch reads before the start of its result.")
        self.remember(address)
        return address, at


class _MemorySource:
    """A source held in memory, for anything small enough to hold."""

    def __init__(self, data: bytes) -> None:
        self.data = data

    def read(self, at: int, size: int) -> bytes:
        return self.data[at:at + size]

    def __len__(self) -> int:
        return len(self.data)

    def close(self) -> None:
        pass


class _FileSource:
    """A source read straight off the disk, for the ones too big to hold.

    A PlayStation 2 image is a few gigabytes; reading one into memory to patch
    it - and building the result there too - asks for twice that again. Mapped
    instead, so only the parts actually copied are ever touched.
    """

    def __init__(self, path: Path) -> None:
        import mmap  # noqa: PLC0415

        self.handle = path.open("rb")
        try:
            self.view = mmap.mmap(self.handle.fileno(), 0,
                                  access=mmap.ACCESS_READ)
        except (OSError, ValueError):
            self.handle.close()
            raise

    def read(self, at: int, size: int) -> bytes:
        return self.view[at:at + size]

    def __len__(self) -> int:
        return len(self.view)

    def close(self) -> None:
        try:
            self.view.close()
        finally:
            self.handle.close()


class _FileTarget:
    """The result, written as it is decoded rather than assembled first.

    Windows land one after another, so the file only ever grows. Reading back
    is needed because a window is allowed to copy from what earlier windows
    already wrote, and that is now on the disk rather than in memory.
    """

    def __init__(self, path: Path) -> None:
        self.handle = path.open("wb+")
        self.size = 0

    def append(self, chunk: bytes) -> None:
        self.handle.write(chunk)
        self.size += len(chunk)

    def read(self, at: int, size: int) -> bytes:
        here = self.handle.tell()
        self.handle.seek(at)
        try:
            return self.handle.read(size)
        finally:
            self.handle.seek(here)

    def close(self) -> None:
        self.handle.close()


class _MemoryTarget:
    """The result assembled in memory, which is what a cartridge wants."""

    def __init__(self) -> None:
        self.data = bytearray()

    @property
    def size(self) -> int:
        return len(self.data)

    def append(self, chunk: bytes) -> None:
        self.data += chunk

    def read(self, at: int, size: int) -> bytes:
        return bytes(self.data[at:at + size])

    def close(self) -> None:
        pass


def apply_vcdiff(source, patch: bytes, out_path: Path | None = None,
                 progress=None):
    """Apply an xdelta/VCDIFF patch.

    `source` is either the bytes themselves or something that can read them a
    piece at a time; `out_path` writes the result to a file rather than
    returning it. Together those are what make a multi-gigabyte disc image
    possible: neither side is ever held whole.

    Only patches written without secondary compression are read. xdelta3 can
    squeeze its three sections through its own Huffman codec, and that codec
    is a separate format again; a patch using it is refused by name rather
    than half-decoded.
    """
    if patch[:3] != VCDIFF_MAGIC:
        raise PatchError("This is not an xdelta patch.")
    if len(patch) < 5:
        raise PatchError("The patch file is damaged.")
    if patch[3] != 0:
        raise PatchError("This patch was written for a newer xdelta than this "
                         "app knows.")

    header = patch[4]
    if header & 0x01:
        raise PatchError("This xdelta patch is compressed in a way this app "
                         "cannot read. Use xdelta3 or a tool that supports it.")
    if header & 0x02:
        raise PatchError("This xdelta patch carries its own instruction table, "
                         "which this app cannot read.")
    at = 5
    if header & 0x04:                    # an application header, for humans
        size, at = _vcd_int(patch, at)
        at += size

    if isinstance(source, (bytes, bytearray, memoryview)):
        source = _MemorySource(bytes(source))
    out = _FileTarget(out_path) if out_path is not None else _MemoryTarget()
    ceiling = MAX_STREAM_TARGET if out_path is not None else MAX_TARGET

    while at < len(patch):
        window = patch[at]
        at += 1
        # Where this window copies from, as a place rather than a copy of it:
        # a source segment can be tens of megabytes and there is no reason to
        # duplicate it to read a few runs out.
        base_from, base_at, base_len = None, 0, 0
        if window & 0x03:
            length, at = _vcd_int(patch, at)
            start, at = _vcd_int(patch, at)
            base_from = out if window & 0x02 else source
            if start + length > (base_from.size if window & 0x02
                                 else len(base_from)):
                raise PatchError("The patch reads past the end of the file.")
            base_at, base_len = start, length

        _, at = _vcd_int(patch, at)              # length of what follows
        target_size, at = _vcd_int(patch, at)
        if target_size > ceiling or out.size + target_size > ceiling:
            raise PatchError("The patch claims an implausibly large result.")
        if at >= len(patch):
            raise PatchError("The patch ends in the middle of a record.")
        if patch[at]:
            raise PatchError("This xdelta patch is compressed in a way this app "
                             "cannot read. Use xdelta3 or a tool that supports it.")
        at += 1

        data_size, at = _vcd_int(patch, at)
        inst_size, at = _vcd_int(patch, at)
        addr_size, at = _vcd_int(patch, at)

        # xdelta3 adds a checksum of the window it is about to describe, which
        # is not in RFC 3284 - it announces it with a third bit on the window
        # indicator. Read past it: skipping the announcement leaves every
        # section four bytes out of step, which decodes into nonsense rather
        # than failing outright.
        checksum = b""
        if window & 0x04:
            checksum = patch[at:at + 4]
            if len(checksum) < 4:
                raise PatchError("The patch ends in the middle of a record.")
            at += 4

        if at + data_size + inst_size + addr_size > len(patch):
            raise PatchError("The patch ends in the middle of a record.")
        data = patch[at:at + data_size]
        at += data_size
        instructions = patch[at:at + inst_size]
        at += inst_size
        addresses = patch[at:at + addr_size]
        at += addr_size

        built = bytearray()
        cache = _Addresses()
        take = read = spot = 0
        while read < len(instructions):
            index = instructions[read]
            read += 1
            for kind, size, mode in _CODE_TABLE[index]:
                if kind == _NOOP:
                    continue
                if size == 0:
                    size, read = _vcd_int(instructions, read)
                if len(built) + size > target_size:
                    raise PatchError("The patch writes past the end of its own result.")
                if kind == _ADD:
                    if take + size > len(data):
                        raise PatchError("The patch reads past the end of the file.")
                    built += data[take:take + size]
                    take += size
                elif kind == _RUN:
                    if take >= len(data):
                        raise PatchError("The patch reads past the end of the file.")
                    built += bytes([data[take]]) * size
                    take += 1
                else:
                    here = base_len + len(built)
                    address, spot = cache.read(mode, here, addresses, spot)
                    if address >= here:
                        raise PatchError("The patch reads past the end of the file.")

                    if address + size <= base_len:
                        # Wholly inside what it is copying from: one read.
                        # Doing this a byte at a time is what would turn a
                        # three-gigabyte image into an afternoon.
                        built += base_from.read(base_at + address, size)
                    elif address >= base_len and address + size <= here:
                        start = address - base_len
                        built += built[start:start + size]
                    else:
                        # Either it straddles the join, or it runs into what it
                        # is still writing - which is how a repeat is written.
                        # Byte at a time, so those bytes exist by the time they
                        # are read.
                        for _ in range(size):
                            if address < base_len:
                                built += base_from.read(base_at + address, 1)
                            else:
                                built.append(built[address - base_len])
                            address += 1

        if len(built) != target_size:
            raise PatchError("The patch finished without filling the result.")
        out.append(bytes(built))
        if progress:
            # A window at a time is the natural beat here, and the source's
            # size is the only total available before the last window has been
            # read - close enough for a bar, since a patched game is nearly
            # always about the size of the one it came from.
            progress(out.size, max(len(source), out.size))

    if out_path is not None:
        total = out.size
        out.close()
        return total
    result = bytes(out.data)
    out.close()
    return result


# ---------- PPF ----------
#
# The format disc patches have always been published in. Unlike the others it
# does not rebuild the file - it lists places in it and what to put there - so
# a three-gigabyte image is patched by copying it and writing over a few
# hundred bytes, which is why it suits discs in the first place.

PPF_MAGIC = b"PPF"


def parse_ppf(patch: bytes) -> list[tuple[int, bytes]]:
    """The (where, what) pairs a PPF patch is made of.

    Three versions exist and they differ in the header and in how wide an
    offset is: 1.0 has no preamble worth the name, 2.0 records the size of the
    file it expects, 3.0 adds an undo copy of every byte it overwrites. All
    three end in the same optional block of author's notes, which is not part
    of the patch and has to be recognised rather than read as one.
    """
    if len(patch) < 6 or patch[:3] != PPF_MAGIC:
        raise PatchError("This is not a PPF patch.")
    version = patch[3:5]
    if version not in (b"10", b"20", b"30"):
        raise PatchError("This PPF patch is a version this app does not know.")

    at = 56                       # magic, encoding byte, then 50 of description
    undo = False
    width = 4
    if version == b"20":
        at += 4                   # the size it expects the file to be
        at += 1024                # the block it checks that size against
    elif version == b"30":
        if len(patch) < 60:
            raise PatchError("The patch file is damaged.")
        blockcheck = patch[57]
        undo = bool(patch[58])
        at = 60
        if blockcheck:
            at += 1024
        width = 8

    records: list[tuple[int, bytes]] = []
    total = 0
    while at < len(patch):
        # Author's notes live after the last record. Everything from here on
        # is for a person to read, not to write into a game.
        if patch[at:at + 18] == b"@BEGIN_FILE_ID.DIZ":
            break
        if at + width + 1 > len(patch):
            raise PatchError("The patch ends in the middle of a record.")
        offset = int.from_bytes(patch[at:at + width], "little")
        at += width
        size = patch[at]
        at += 1
        if at + size > len(patch):
            raise PatchError("The patch ends in the middle of a record.")
        records.append((offset, patch[at:at + size]))
        at += size
        if undo:
            at += size            # the copy it kept of what was there before
        total += size
        if total > MAX_PATCH:
            raise PatchError("The patch writes implausibly far into the file.")
    return records


def apply_ppf(source: bytes, patch: bytes) -> bytes:
    """Apply a PPF patch to something already in memory."""
    out = bytearray(source)
    for offset, chunk in parse_ppf(patch):
        if offset + len(chunk) > len(out):
            raise PatchError("This patch is for a different dump of the game. "
                             "It writes past the end of this file.")
        out[offset:offset + len(chunk)] = chunk
    return bytes(out)


def apply_ppf_to_file(source: Path, patch: bytes, out_path: Path,
                      progress=None) -> int:
    """Apply a PPF patch to a file too big to hold, by copying then editing.

    The copy is the slow part and there is no way round it: the original is
    never touched, so the result has to start life as a duplicate of it.
    """
    records = parse_ppf(patch)
    # Copied in pieces rather than in one call, so there is something to
    # report: on a disc image this copy is nearly the whole wait.
    total = source.stat().st_size
    done = 0
    try:
        with source.open("rb") as src, out_path.open("wb") as dst:
            while True:
                chunk = src.read(8 * 1024 * 1024)
                if not chunk:
                    break
                dst.write(chunk)
                done += len(chunk)
                if progress:
                    progress(done, total)
    except OSError as exc:
        raise PatchError(f"The game could not be copied: {exc}") from exc
    size = out_path.stat().st_size
    with out_path.open("r+b") as handle:
        for offset, chunk in records:
            if offset + len(chunk) > size:
                raise PatchError("This patch is for a different dump of the "
                                 "game. It writes past the end of this file.")
            handle.seek(offset)
            handle.write(chunk)
    return size


# ---------- any of them ----------

def apply(source: bytes, patch: bytes) -> bytes:
    """Apply whichever kind of patch this is."""
    kind = detect(patch)
    if kind == "bps":
        return apply_bps(source, patch)
    if kind == "ips":
        return apply_ips(source, patch)
    if kind == "xdelta":
        return apply_vcdiff(source, patch)
    if kind == "ppf":
        return apply_ppf(source, patch)
    raise PatchError("This file is not a patch this app recognises.")


# ---------- fetching one, and putting it on a game ----------

USER_AGENT = "RomSrx/1.0 (+https://github.com/)"
TIMEOUT = 60
MAX_PATCH = 64 * 1024 * 1024        # a patch archive, not a disc image

# What a patch inside an archive is called. Everything else in there is a
# readme, which is worth reading and not worth applying.
PATCH_EXTS = (".bps", ".ips", ".xdelta", ".vcdiff", ".ppf")
# Cartridge ROMs, which are patched in memory because they comfortably fit.
# Disc images are patched too - see DISC_EXTS and LARGE_FILE below - but never
# this way, so they are not in this list.
ROM_EXTS = (".nes", ".fds", ".sfc", ".smc", ".gb", ".gbc", ".gba", ".md",
            ".gen", ".smd", ".sms", ".gg", ".n64", ".z64", ".v64", ".pce",
            ".nds", ".vb", ".ws", ".wsc", ".a26", ".a78", ".lnx", ".col",
            ".int", ".rom", ".bin")

# Disc images this app will patch: the raw ones, where the file is simply the
# disc laid out end to end and a patch can address it as bytes. Compressed
# ones - .chd above all - are not here on purpose: a patch made against the
# raw image has nothing to say about a rearranged copy of it.
DISC_EXTS = (".iso", ".img")

# Past this, a file is patched on the disk rather than in memory - whatever
# its extension says it is.
LARGE_FILE = 256 * 1024 * 1024

# The consoles whose games are discs. Patching one means rebuilding a disc
# image, which this app doesn't do - so the menu entry doesn't appear for
# them rather than appearing and always refusing. Named the way the index
# names them, since that is what the page has to compare against.
DISC_CONSOLES = frozenset({
    "PlayStation", "PlayStation 2", "PSP", "Sega Dreamcast", "Sega Saturn",
    "Sega CD", "PC-FX", "PC Engine CD/TurboGrafx-CD", "Neo Geo CD",
    "GameCube", "Nintendo Wii", "Atari Jaguar CD",
})


def fetch(url: str) -> bytes:
    """Download a patch, or whatever archive it arrived in."""
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:  # noqa: S310
            data = response.read(MAX_PATCH + 1)
    except (urllib.error.URLError, OSError, TimeoutError) as exc:
        raise PatchError(f"Could not download the patch: {exc}") from exc
    if len(data) > MAX_PATCH:
        raise PatchError("That patch download is far larger than a patch.")
    return data


def _patches_in(data: bytes) -> list[tuple[str, bytes]]:
    """The patches inside a download, or the download itself if it is one.

    RetroAchievements publishes patches inside a zip, usually beside a readme
    and occasionally several at once - a hack and its variants. All of them
    come back so the caller can say which.
    """
    if detect(data):
        return [("", data)]

    if data[:2] == b"PK":
        try:
            with zipfile.ZipFile(io.BytesIO(data)) as archive:
                return [(name, archive.read(name))
                        for name in archive.namelist()
                        if name.lower().endswith(PATCH_EXTS)]
        except (zipfile.BadZipFile, OSError, RuntimeError) as exc:
            raise PatchError(f"That patch archive could not be opened: {exc}") from exc

    if data[:6] == b"7z\xbc\xaf\x27\x1c":
        try:
            import py7zr  # noqa: PLC0415 - only needed for the few .7z ones

            with py7zr.SevenZipFile(io.BytesIO(data)) as archive:
                wanted = [n for n in archive.getnames()
                          if n.lower().endswith(PATCH_EXTS)]
                if not wanted:
                    return []
                return [(name, blob.read())
                        for name, blob in (archive.read(wanted) or {}).items()]
        except ImportError as exc:
            raise PatchError("This patch is a .7z and py7zr isn't available.") from exc
        except Exception as exc:  # noqa: BLE001 - py7zr raises its own kinds
            raise PatchError(f"That patch archive could not be opened: {exc}") from exc

    raise PatchError("That download is not a patch or an archive of one.")


def _rom_in(path: Path) -> tuple[str, bytes]:
    """The ROM to patch: the file itself, or the one inside it.

    A library entry can be the ROM, a zip holding it, or a folder holding
    either. Anything with more than one ROM in it is left alone rather than
    guessed at - a multi-disc game is not something to patch blind.
    """
    if path.is_dir():
        roms = [p for p in sorted(path.rglob("*"))
                if p.is_file() and p.suffix.lower() in ROM_EXTS]
        if not roms:
            zips = [p for p in sorted(path.rglob("*.zip"))]
            if len(zips) == 1:
                return _rom_in(zips[0])
            raise PatchError("No ROM was found in that game's folder.")
        if len(roms) > 1:
            raise PatchError("That folder holds several ROMs, so which to "
                             "patch is not clear.")
        return roms[0].name, roms[0].read_bytes()

    if path.suffix.lower() == ".zip":
        try:
            with zipfile.ZipFile(path) as archive:
                inside = [n for n in archive.namelist()
                          if n.lower().endswith(ROM_EXTS)]
                if not inside:
                    raise PatchError("There is no ROM inside that archive.")
                if len(inside) > 1:
                    raise PatchError("That archive holds several ROMs, so "
                                     "which to patch is not clear.")
                return Path(inside[0]).name, archive.read(inside[0])
        except (zipfile.BadZipFile, OSError) as exc:
            raise PatchError(f"That game's archive could not be opened: {exc}") from exc

    if path.suffix.lower() not in ROM_EXTS:
        raise PatchError("This app can only patch cartridge ROMs, and that "
                         "file is not one.")
    return path.name, path.read_bytes()


def _output_path(game: Path, rom_name: str, patch_name: str) -> Path:
    """Where the patched copy goes: beside the original, under its own name.

    Named after the patch rather than a fixed "(patched)", because one game
    often has several - a translation and a 60fps hack are different games to
    play, and both landing on the same filename means the second quietly
    replaces the first. A patch whose name says nothing useful falls back to
    the plain word, and an existing file is never written over.
    """
    folder = game.parent if game.is_file() else game
    rom = Path(rom_name)
    label = Path(patch_name).stem.strip(" .") if patch_name else ""
    # A patch is usually named after the game it is for, so using the whole of
    # it repeats the title twice in one filename and then truncates the half
    # that said anything. Only the part that is not already the game's name is
    # worth keeping.
    if label.casefold().startswith(rom.stem.casefold()):
        label = label[len(rom.stem):].strip(" -_()[[]")
    if len(label) < 4 or label.casefold() in {"patch", rom.stem.casefold()}:
        label = "patched"

    # Windows gives up somewhere past 260 characters, and a patch name can be
    # most of a sentence. Trim the label - never the game - until it fits.
    while len(label) > 8:
        candidate = folder / f"{rom.stem} ({label}){rom.suffix}"
        if len(str(candidate)) <= 240:
            break
        label = label[:-8].rstrip(" .-")

    out = folder / f"{rom.stem} ({label}){rom.suffix}"
    count = 2
    while out.exists():
        out = folder / f"{rom.stem} ({label} {count}){rom.suffix}"
        count += 1
    return out


def save_patch(url: str, folder, name: str = "") -> dict:
    """Download a patch and keep it, rather than handing it to a browser.

    The whole archive is saved as it came, not the patch unpacked out of it:
    the readme beside it usually says which release the patch expects, and
    that is worth more than saving one file's worth of space.
    """
    if not url:
        raise PatchError("There is no patch to download.")

    blob = fetch(url)
    stem = name or urllib.parse.unquote(url.rsplit("/", 1)[-1]) or "patch"
    stem = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", stem).strip(" .") or "patch"

    folder = Path(folder)
    try:
        folder.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise PatchError(f"That patch folder could not be made: {exc}") from exc

    out = folder / stem
    # Downloading the same patch twice is not a reason to overwrite the first,
    # which may have been unpacked and worked on already.
    if out.exists():
        base, suffix = Path(stem).stem, Path(stem).suffix
        count = 2
        while out.exists():
            out = folder / f"{base} ({count}){suffix}"
            count += 1

    try:
        out.write_bytes(blob)
    except OSError as exc:
        raise PatchError(f"The patch could not be saved: {exc}") from exc
    return {"saved": str(out), "bytes": len(blob)}


def _take_the_place_of(original: Path, patched: Path) -> Path:
    """Give the patched file the original's name, and remove the original.

    Ordered so there is no moment where the game exists under neither name.
    The original is moved aside rather than deleted, the patched file takes
    the name, and only then is the moved-aside copy removed - so a rename
    that fails partway can be undone instead of costing the game.
    """
    aside = original.with_name(original.name + ".unpatched")
    try:
        aside.unlink(missing_ok=True)        # left by an earlier attempt
        original.rename(aside)
    except OSError as exc:
        raise PatchError(f"The original could not be moved aside: {exc}") from exc

    try:
        patched.rename(original)
    except OSError as exc:
        try:
            aside.rename(original)           # put it back exactly as it was
        except OSError:
            raise PatchError(
                f"The patched copy could not take the original's name, and the "
                f"original is now at {aside}. Rename it back by hand.") from exc
        raise PatchError(
            f"The patched copy could not take the original's name: {exc}") from exc

    try:
        aside.unlink()
    except OSError:
        pass          # the patch worked; a leftover is untidy, not a failure
    return original


def _copy_cue(original: Path, patched: Path) -> Path | None:
    """Give a patched disc track a sheet of its own that points at it.

    A .bin is loaded through its .cue, and that sheet names the file by hand.
    Patch the track and the old sheet still names the old track, so the new
    one is never played and the patching looks as though it did nothing.
    """
    sheets = [p for p in original.parent.glob("*.cue") if p.is_file()]
    if len(sheets) != 1:
        return None            # no sheet, or several and no way to say which
    try:
        text = sheets[0].read_text(encoding="utf-8", errors="replace")
        if original.name not in text:
            return None        # it describes some other track
        beside = patched.with_suffix(".cue")
        beside.write_text(text.replace(original.name, patched.name),
                          encoding="utf-8")
    except OSError:
        return None            # the game is still patched; only the sheet isn't
    return beside


def patch_game(game_path: str, url: str = "", choose: str = "",
               patch_path: str = "", replace: bool = False,
               progress=None) -> dict:
    """Fetch a patch and apply it to a game already on this machine.

    The result is written beside the original rather than over it: patching
    is not something anyone should have to undo, and the unpatched file is
    what every other patch will want as its starting point.
    """
    path = Path(game_path)
    if not path.exists():
        raise PatchError("That game is no longer where the library says.")

    # Either fetched, or a file the user picked themselves. Both arrive here
    # as the same bytes, so everything below this line is the same work.
    if patch_path:
        chosen = Path(patch_path)
        if not chosen.is_file():
            raise PatchError("That patch file is no longer where it was.")
        if chosen.stat().st_size > MAX_PATCH:
            raise PatchError("That file is far larger than a patch.")
        found = _patches_in(chosen.read_bytes())
        # A patch inside an archive is named by the archive; a loose one is
        # named by the file itself, and forgetting that is how a hand-picked
        # patch ends up producing a copy called merely "(patched)".
        if len(found) == 1 and not found[0][0]:
            found = [(chosen.name, found[0][1])]
    elif url:
        found = _patches_in(fetch(url))
    else:
        raise PatchError("There is no patch to apply.")
    if not found:
        raise PatchError("That download holds no patch this app can read.")
    if choose:
        found = [f for f in found if f[0] == choose] or found
    if len(found) > 1:
        return {"choices": [name for name, _ in found]}

    name, blob = found[0]
    kind = detect(blob)

    # Anything big enough to hurt is patched where it lies, whatever it is
    # called. Deciding on size rather than extension matters: a PlayStation
    # track is a .bin, which is also a cartridge extension, and routing it by
    # name sent 700 MB down the path that holds the whole file in memory.
    # A folder counts too, and this is the case that was slipping through: a
    # PlayStation game is usually a folder holding one big .bin beside its
    # .cue, and looking only at the folder sent it down the path that holds
    # the whole thing in memory.
    target = path
    if path.is_dir():
        inside = [p for p in sorted(path.rglob("*"))
                  if p.is_file()
                  and p.suffix.lower() in (*ROM_EXTS, *DISC_EXTS)]
        if len(inside) == 1:
            target = inside[0]

    big = target.is_file() and (target.suffix.lower() in DISC_EXTS
                                or target.stat().st_size > LARGE_FILE)
    if big:
        path = target
        if kind not in ("xdelta", "ppf"):
            raise PatchError("A file this large can only be patched with an "
                             "xdelta or PPF patch, and this is neither.")
        out = _output_path(path, path.name, name)
        try:
            if kind == "ppf":
                written = apply_ppf_to_file(path, blob, out, progress)
            else:
                reader = _FileSource(path)
                try:
                    written = apply_vcdiff(reader, blob, out, progress)
                finally:
                    reader.close()
        except Exception:
            out.unlink(missing_ok=True)   # never leave half an image behind
            raise
        if replace:
            # No companion sheet is needed: the original's own .cue already
            # names this file, because this file now has the original's name.
            out = _take_the_place_of(path, out)
            return {"written": str(out), "kind": kind, "patch": name or "patch",
                    "bytes": written, "cue": "", "replaced": True}
        companion = _copy_cue(path, out)
        return {"written": str(out), "kind": kind, "patch": name or "patch",
                "bytes": written, "cue": str(companion) if companion else ""}

    rom_name, rom = _rom_in(path)
    patched = apply(rom, blob)

    out = _output_path(path, rom_name, name)
    try:
        out.write_bytes(patched)
    except OSError as exc:
        raise PatchError(f"The patched game could not be written: {exc}") from exc

    # Only ever the file that was actually patched. A game kept as a folder or
    # a zip was read from inside it, and replacing the container with a bare
    # ROM would leave the library describing something that is no longer there.
    if replace:
        if path.is_file() and path.name == rom_name:
            out = _take_the_place_of(path, out)
            return {"written": str(out), "kind": kind, "patch": name or "patch",
                    "bytes": len(patched), "replaced": True}
        return {"written": str(out), "kind": kind, "patch": name or "patch",
                "bytes": len(patched), "keptBecauseContainer": True}
    return {"written": str(out), "kind": kind, "patch": name or "patch",
            "bytes": len(patched)}
