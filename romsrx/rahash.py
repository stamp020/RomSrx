"""The number RetroAchievements knows a game by, computed from a file on disk.

Everything else in this app asks RetroAchievements about a *title*. A set is
not attached to a title, though - it is attached to particular dumps, and the
site identifies those by a hash. retro.supported() answers the question by
comparing filenames, which is a good guess and says so; this answers it
outright, by working out the same number the site did.

The number is not simply the MD5 of the file. RetroAchievements hashes a
cartridge the way the emulator sees it, which means a headered dump and a
headerless one of the same game must come out alike, and a Nintendo 64 ROM in
any of its three byte orders must come out as the big-endian one. So there is
a rule per console, and the rules are ported from `rcheevos`, which is the
implementation the site itself runs - src/rhash/hash_rom.c, function by
function. Where this file says something surprising, that is where it is
copied from:

  NES, FDS      'NES\\x1a' or 'FDS\\x1a' at the start -> skip 16 bytes.
  Atari 7800    'ATARI7800' at offset 1 -> skip 128 bytes.
  Atari Lynx    'LYNX\\0' at the start -> skip 64 bytes.
  SNES          512 bytes more than a multiple of 8KB -> skip 512.
  PC Engine     any size with bit 9 set -> skip 512. Not the same test as the
                SNES one, however alike the two look, and the difference
                matters for a file that is 512 over a multiple of 1KB.
  Nintendo 64   no header; the file is normalised to big-endian first.
  Nintendo DS   the header, both pieces of boot code and the icon block, and
                nothing else - a DS card is mostly data the hash ignores.
  everything    the file, whole.
  else

Discs are not hashed here at all. Their number comes from a program inside
the image rather than from the bytes of it, which is a filesystem to walk
rather than a rule to apply - see discs.py, which does that for PlayStation
and PlayStation 2 and says "not checked" for the rest. scheme() returns
"disc" for the ones it can answer for and "" for the others, and nobody is
ever told a guess.

Only the first 64MB of a file are ever hashed, because that is the cap
rcheevos uses. It is above every cartridge ever made and below every disc,
which is the reason it can be a constant.
"""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
import threading
import time
import zipfile
from contextlib import contextmanager
from pathlib import Path

from . import discs
from .paths import user

# rcheevos' MAX_BUFFER_SIZE. Applied before the header is looked for, exactly
# as it is there: a file longer than this is hashed as though it ended here.
CAP = 64 * 1024 * 1024

# Enough of the front of a file to recognise every header above. Read in one
# go so the stream is only touched once before hashing starts, which is what
# lets this work on a file inside a zip as readily as on one on the disk.
PEEK = 512

# How much is read at a time once hashing is under way.
CHUNK = 1024 * 1024

# This app's console names -> which rule to apply. The names are retro.py's,
# because that is what the rest of the app calls these machines; a console
# missing from here is one this cannot answer for, which is every disc system
# and anything RetroAchievements identifies by something other than its bytes.
SCHEMES = {
    "NES/Famicom": "nes",
    "Famicom Disk System": "nes",
    "SNES/Super Famicom": "snes",
    "PC Engine/TurboGrafx-16": "pce",
    "Atari 7800": "a7800",
    "Atari Lynx": "lynx",
    "Nintendo 64": "n64",
    "Nintendo DS": "ds",
    "Nintendo DSi": "ds",
    "Game Boy": "plain",
    "Game Boy Color": "plain",
    "Game Boy Advance": "plain",
    "Genesis/Mega Drive": "plain",
    "32X": "plain",
    "Master System": "plain",
    "Game Gear": "plain",
    "SG-1000": "plain",
    "Virtual Boy": "plain",
    "Pokemon Mini": "plain",
    "Neo Geo Pocket": "plain",
    "Atari 2600": "plain",
    "Atari Jaguar": "plain",
}

# What the ROM for a console is called, for the times the library entry is a
# folder or a zip and the file inside has to be picked out. Ordered by how
# sure the extension is: the ones that mean one machine come first, and the
# vague ones - '.bin' is a Mega Drive cartridge, a disc track and a firmware
# blob - are only reached when nothing better is there.
#
# A container holding two candidates is reported as ambiguous rather than
# guessed at, which is the same rule patcher._rom_in() follows and for the
# same reason: the wrong file hashes perfectly well and answers about the
# wrong game.
EXTENSIONS = {
    "NES/Famicom": (".nes", ".unf", ".unif"),
    "Famicom Disk System": (".fds",),
    "SNES/Super Famicom": (".sfc", ".smc", ".swc", ".fig"),
    "PC Engine/TurboGrafx-16": (".pce", ".sgx"),
    "Atari 7800": (".a78", ".bin"),
    "Atari Lynx": (".lnx",),
    "Nintendo 64": (".z64", ".n64", ".v64", ".ndd"),
    "Nintendo DS": (".nds",),
    "Nintendo DSi": (".dsi", ".nds"),
    "Game Boy": (".gb",),
    "Game Boy Color": (".gbc", ".gb"),
    "Game Boy Advance": (".gba",),
    "Genesis/Mega Drive": (".md", ".gen", ".smd", ".bin"),
    "32X": (".32x", ".bin"),
    "Master System": (".sms",),
    "Game Gear": (".gg",),
    "SG-1000": (".sg",),
    "Virtual Boy": (".vb",),
    "Pokemon Mini": (".min",),
    "Neo Geo Pocket": (".ngp", ".ngc"),
    "Atari 2600": (".a26", ".bin"),
    "Atari Jaguar": (".j64", ".jag", ".rom", ".abs", ".cof", ".bin"),
}

# Why there is no hash, when there is no hash. The page turns each of these
# into a sentence; none of them is an error in the sense of something having
# gone wrong, which is why this returns them rather than raising.
#
#   unsupported  this console's rule isn't implemented - every disc system.
#   ambiguous    the zip or folder holds more than one thing it could be.
#   archive      it is in a wrapper this cannot open - a .rar, a .gz, or a
#                .7z on a build without py7zr. Not the same as unreadable:
#                the file is fine and the ROM is in there somewhere.
#   notrom       the file is not what its console says: an N64 file whose
#                first byte is none of the three byte orders, a DS file whose
#                header is nonsense. Worth telling apart from unreadable,
#                since nothing is wrong with the disk.
#   unreadable   missing, locked, or a zip that will not open.


def scheme(console: str) -> str:
    """Which rule this console's files are hashed by, or "" for none."""
    console = (console or "").strip()
    if console in SCHEMES:
        return SCHEMES[console]
    # The disc consoles discs.py can walk. Kept out of SCHEMES because none of
    # the machinery below applies to them: there is no header to skip and no
    # run of bytes to hash, only a filesystem to look inside.
    return "disc" if discs.handles(console) else ""


def supported_consoles() -> list[str]:
    return sorted(set(SCHEMES) | set(discs.CONSOLES))


# -- getting at the ROM ---------------------------------------------------
# A library entry is a path, and behind that path is one of three things: the
# ROM, a zip holding the ROM, or a folder holding either. All three end up as
# a stream and a length, which is all the hashing below wants.


def _candidates(names: list[str], console: str) -> list[str]:
    """The entries that could be the ROM, best extension first."""
    wanted = EXTENSIONS.get(console) or ()
    for suffix in wanted:
        found = [n for n in names if n.lower().endswith(suffix)]
        if found:
            return sorted(found)
    return []


class _Missing(Exception):
    """Raised inside _source with the reason to report."""

    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


# What a game is wrapped in, recognised by its first bytes rather than by its
# name. By name was not enough and was quietly wrong: a game stored as a .7z
# fell through to "hash the file as it lies", which produced a perfectly good
# hash of the compressed archive and reported the game as one the set does not
# accept. A wrapper this cannot open has to say so - being unable to look
# inside is not evidence about what is in there.
WRAPPERS = ((b"PK\x03\x04", "zip"), (b"7z\xbc\xaf\x27\x1c", "7z"),
            (b"Rar!", "rar"), (b"\x1f\x8b", "gz"))


def _wrapper(path: Path) -> str:
    """"zip", "7z", "rar", "gz", or "" for a file that is what it says."""
    try:
        with open(path, "rb") as handle:
            head = handle.read(8)
    except OSError:
        return ""
    for magic, kind in WRAPPERS:
        if head.startswith(magic):
            return kind
    return ""


def _pick(names: list[str], console: str) -> str:
    """The one entry in a container that is the ROM, or a reason it isn't."""
    picked = _candidates(names, console)
    if len(picked) > 1:
        raise _Missing("ambiguous")
    if picked:
        return picked[0]
    # Nothing with the right extension, but only one file in there: a
    # container with a single member is that member however it is named, and
    # plenty of them are named .rom or nothing at all.
    if len(names) == 1:
        return names[0]
    raise _Missing("ambiguous" if names else "unreadable")


@contextmanager
def _from_zip(path: Path, console: str):
    try:
        with zipfile.ZipFile(path) as archive:
            names = [i.filename for i in archive.infolist() if not i.is_dir()]
            item = archive.getinfo(_pick(names, console))
            with archive.open(item) as handle:
                yield handle, item.file_size
    except _Missing:
        raise
    except (zipfile.BadZipFile, OSError, RuntimeError, KeyError) as exc:
        raise _Missing("unreadable") from exc


@contextmanager
def _from_7z(path: Path, console: str):
    """A .7z, which is how a good share of archive.org's sets are packed.

    The one member is unpacked to a temporary folder and hashed from there,
    rather than into memory. That is partly to keep a 64MB cartridge off the
    heap and partly because py7zr's in-memory read() was removed in its 1.0:
    extract() is the call both the old versions and the new ones have.
    """
    try:
        import py7zr  # noqa: PLC0415 - optional, and only this needs it
    except ImportError as exc:
        raise _Missing("archive") from exc

    with tempfile.TemporaryDirectory(prefix="romsrx-hash-") as scratch:
        try:
            with py7zr.SevenZipFile(path) as archive:
                names = [f.filename for f in archive.list() if not f.is_directory]
                wanted = _pick(names, console)
                archive.extract(path=scratch, targets=[wanted])
        except _Missing:
            raise
        except Exception as exc:  # noqa: BLE001 - py7zr raises its own kinds
            raise _Missing("unreadable") from exc

        # Unpacked under whatever folders it was filed in inside the archive.
        out = Path(scratch) / wanted.replace("\\", "/")
        if not out.is_file():
            raise _Missing("unreadable")
        with open(out, "rb") as handle:
            yield handle, out.stat().st_size


@contextmanager
def _source(path: Path, console: str):
    """The ROM itself, as (stream, size), whatever it was wrapped in.

    Streams rather than bytes throughout: a Nintendo 64 cartridge is 64MB and
    a DS card can be half a gigabyte, and reading one into memory to hash it
    would be a spike in a program that is otherwise idle.
    """
    if path.is_dir():
        inside = [p for p in sorted(path.rglob("*")) if p.is_file()]
        picked = _candidates([str(p) for p in inside], console)
        if len(picked) > 1:
            raise _Missing("ambiguous")
        # A folder that holds nothing but one archive is that archive - which
        # is how a game arrives when the downloader has extracted a .7z
        # holding a .zip, or when somebody has filed one by hand. And a folder
        # holding one file is that file, whatever it is called: extensions are
        # how the ROM is picked out of a crowd, and there is no crowd here.
        if not picked:
            wrapped = [p for p in inside if p.suffix.lower() in (".zip", ".7z")]
            picked = ([str(wrapped[0])] if len(wrapped) == 1
                      else [str(inside[0])] if len(inside) == 1 else [])
        if not picked:
            raise _Missing("ambiguous" if inside else "unreadable")
        # Back through here rather than opened outright, so whatever was found
        # is still judged by its first bytes: the one file in a folder is as
        # likely to be a .7z as a ROM.
        with _source(Path(picked[0]), console) as found:
            yield found
        return

    # By what is in the file, not by what it is called: a .zip named .md is
    # still a zip, and - the case that matters - a .7z left to fall through to
    # the branch below would be hashed as itself and answered about wrongly.
    kind = _wrapper(path)
    if kind == "zip":
        with _from_zip(path, console) as found:
            yield found
        return
    if kind == "7z":
        with _from_7z(path, console) as found:
            yield found
        return
    if kind:
        # .rar and .gz. Both could be opened - one needs a library this app
        # does not carry, the other needs the whole thing decompressed to know
        # how long it is - and until they are, "not checked" is the only
        # honest answer.
        raise _Missing("archive")

    try:
        size = os.path.getsize(path)
    except OSError as exc:
        raise _Missing("unreadable") from exc
    with open(path, "rb") as handle:
        yield handle, size


# -- the rules ------------------------------------------------------------


def _header(kind: str, head: bytes, size: int) -> int:
    """How many bytes at the front this console's rule ignores.

    `size` is the capped length, not the file's own, because that is the
    length rcheevos has in hand when it makes the same decision - it caps the
    read first and looks for the header in what it got.
    """
    if kind == "nes":
        if size > 16 and head[:4] in (b"NES\x1a", b"FDS\x1a"):
            return 16
    elif kind == "a7800":
        if size > 128 and head[1:10] == b"ATARI7800":
            return 128
    elif kind == "lynx":
        if size > 64 and head[:5] == b"LYNX\0":
            return 64
    elif kind == "snes":
        # 512 more than a multiple of 8KB: the copier header.
        if size - (size // 0x2000) * 0x2000 == 512:
            return 512
    elif kind == "pce":
        # Bit 9 set, which is what the core tests and so what rcheevos tests.
        # Deliberately not the SNES rule: they agree on almost every real
        # dump and disagree on some, and this is the one that is copied.
        if size & 512:
            return 512
    return 0


def _byteswap16(data: bytes) -> bytes:
    """ABCD -> BADC, in whole words, as rc_hash_byteswap16 does.

    The odd bytes at the end of a run that isn't a multiple of four are left
    alone, which is also what it does - the loop there steps a word at a time
    and stops short.
    """
    whole = len(data) - len(data) % 4
    out = bytearray(data)
    out[0:whole:2], out[1:whole:2] = data[1:whole:2], data[0:whole:2]
    return bytes(out)


def _byteswap32(data: bytes) -> bytes:
    """ABCD -> DCBA, in whole words."""
    whole = len(data) - len(data) % 4
    out = bytearray(data)
    for at in range(0, whole, 4):
        out[at:at + 4] = data[at:at + 4][::-1]
    return bytes(out)


# The first byte of a Nintendo 64 file says which order the rest is in. Any
# other value is not an N64 ROM at all, and rcheevos declines to hash it
# rather than hashing it wrongly.
_N64_ORDERS = {
    0x80: None,          # .z64, big-endian, already how the site wants it
    0x37: _byteswap16,   # .v64, byte-swapped pairs
    0x40: _byteswap32,   # .n64, little-endian
    0xE8: None,          # .ndd, the disk drive's own format
    0x22: None,
}


def _hash_n64(stream, size: int) -> tuple[str, str]:
    head = stream.read(PEEK)
    if not head:
        return "", "unreadable"
    if head[0] not in _N64_ORDERS:
        return "", "notrom"
    swap = _N64_ORDERS[head[0]]

    digest = hashlib.md5()  # noqa: S324 - the site's choice, not a security one
    remaining = min(size, CAP)
    block = head[:remaining]
    while True:
        digest.update(swap(block) if swap else block)
        remaining -= len(block)
        if remaining <= 0:
            break
        block = stream.read(min(CHUNK, remaining))
        if not block:
            break
    return digest.hexdigest(), ""


def _int32(data: bytes, at: int) -> int:
    return int.from_bytes(data[at:at + 4], "little")


# What a SuperCard dumper puts in front of a DS ROM. Recognised by the branch
# instruction it opens with and a marker further in, since it carries no name.
_SUPERCARD = (b"\x2e\x00\x00\xea", b"\x44\x46\x96\x00")

DS_HEADER = 0x160        # how much of the header is hashed
DS_ICON = 0xA00          # ...and how much of the icon and title block
DS_CODE_LIMIT = 16 * 1024 * 1024


def _hash_ds(stream, size: int) -> tuple[str, str]:
    """Header, both boot codes and the icon block - not the card.

    A DS card is mostly the game's data, which the hash never touches; what it
    covers is the part that identifies the release. So this reads a few
    hundred kilobytes out of a file that may be half a gigabyte, and is the
    fastest console here rather than the slowest.

    Needs to seek, which is why the source has to be seekable - it is, both
    for a file on disk and for one inside a zip.
    """
    del size
    try:
        header = stream.read(512)
        if len(header) < 512:
            return "", "notrom"
        offset = 0
        if header[:4] == _SUPERCARD[0] and header[0xB0:0xB4] == _SUPERCARD[1]:
            offset = 512
            stream.seek(offset)
            header = stream.read(512)
            if len(header) < 512:
                return "", "notrom"

        arm9_at, arm9_size = _int32(header, 0x20), _int32(header, 0x2C)
        arm7_at, arm7_size = _int32(header, 0x30), _int32(header, 0x3C)
        icon_at = _int32(header, 0x68)
        # The same sanity check rcheevos makes: the boot code is a megabyte or
        # so, and anything claiming far more means this was never a DS ROM and
        # the numbers just read are whatever happened to be at those offsets.
        if arm9_size + arm7_size > DS_CODE_LIMIT:
            return "", "notrom"

        digest = hashlib.md5()  # noqa: S324
        digest.update(header[:DS_HEADER])
        for at, length in ((arm9_at, arm9_size), (arm7_at, arm7_size),
                           (icon_at, DS_ICON)):
            stream.seek(at + offset)
            block = stream.read(length)
            # Short reads are padded rather than shortened, which is what the
            # icon block of a homebrew card often needs - and keeps the answer
            # the same length whatever the file had left.
            digest.update(block + b"\0" * (length - len(block)))
    except (OSError, ValueError):
        return "", "unreadable"
    return digest.hexdigest(), ""


def _hash_flat(stream, size: int, kind: str) -> tuple[str, str]:
    """Every scheme that is "skip nothing or skip a header, then hash"."""
    capped = min(size, CAP)
    head = stream.read(min(PEEK, capped))
    skip = _header(kind, head, capped)

    digest = hashlib.md5()  # noqa: S324
    digest.update(head[skip:capped])
    # By however much the peek fell short of the cap - the header came out of
    # what was already read, so it is not owed a second time.
    remaining = capped - len(head)
    while remaining > 0:
        block = stream.read(min(CHUNK, remaining))
        if not block:
            break
        digest.update(block)
        remaining -= len(block)
    return digest.hexdigest(), ""


def compute(path, console: str) -> tuple[str, str]:
    """The hash of one file, ignoring the cache: (md5, reason).

    Exactly one of the two is ever set. Never raises - a library sweep runs
    this over a few thousand files it did not choose, any of which may be
    locked, half-downloaded or not what its name says.
    """
    kind = scheme(console)
    if not kind:
        return "", "unsupported"
    if kind == "disc":
        # Its own module: a disc is a filesystem rather than a run of bytes,
        # and none of the container handling below means anything for one.
        return discs.md5(path, console)
    try:
        with _source(Path(path), console) as (stream, size):
            if size <= 0:
                return "", "unreadable"
            if kind == "n64":
                return _hash_n64(stream, size)
            if kind == "ds":
                return _hash_ds(stream, size)
            return _hash_flat(stream, size, kind)
    except _Missing as exc:
        return "", exc.reason
    except (OSError, ValueError):
        return "", "unreadable"
    except Exception:  # noqa: BLE001 - one odd file must not stop a sweep
        return "", "unreadable"


# -- remembering what has already been worked out -------------------------
# A hash is expensive to compute and can never change: the same bytes give the
# same answer forever. So this is the one cache in the app with no freshness
# window at all - an entry is good until the file it describes is a different
# file, which its size and its modified time say plainly enough.
#
# Kept beside the console lists rather than in romsrx.db, which is the
# archive.org index and gets rebuilt.

CACHE = user("retro") / "filehashes.json"

_cache: dict[str, dict] | None = None
_dirty = False
_cache_lock = threading.Lock()


def stamp(path: Path) -> tuple[int, int]:
    """(size, modified) - enough to say whether this is still the same game.

    Public because two caches are keyed on it now: the hashes here, and the
    verdicts retro.py keeps beside them. They have to agree about what counts
    as a changed file, or one of them will answer about a file the other has
    already given up on.

    A library entry is as often a folder as a file, and a folder has no size
    of its own - Windows reports zero for one, which read as "this is not
    there any more" and quietly threw away everything worked out about every
    extracted game. So a folder is stamped on what is inside it: the total
    length of its files and the most recent of their times, which is the same
    walk library._folder_size already makes for the shelf.

    (0, 0) means nothing worth remembering - missing, unreadable, or an empty
    folder - and every caller treats it as "ask again".
    """
    try:
        if path.is_dir():
            total = latest = 0
            for item in path.rglob("*"):
                try:
                    if not item.is_file():
                        continue
                    stat = item.stat()
                except OSError:
                    continue
                total += stat.st_size
                latest = max(latest, int(stat.st_mtime))
            return (total, latest) if total else (0, 0)
        stat = path.stat()
    except OSError:
        return (0, 0)
    # Whole seconds: a copied file can come back with its modified time
    # rounded differently by the filesystem, and re-hashing a library because
    # of a fraction of a second would defeat the point of keeping this.
    return (int(stat.st_size), int(stat.st_mtime))


def _load() -> dict[str, dict]:
    global _cache  # noqa: PLW0603 - one cache for the process
    if _cache is None:
        try:
            with open(CACHE, encoding="utf-8") as fh:
                found = json.load(fh)
            _cache = found if isinstance(found, dict) else {}
        except (OSError, ValueError):
            _cache = {}
    return _cache


def md5(path, console: str) -> tuple[str, str]:
    """The hash of one file, from the cache when it is still the same file."""
    global _dirty  # noqa: PLW0603
    where = Path(path)
    key = str(where)
    size, when = stamp(where)
    kind = scheme(console)

    with _cache_lock:
        found = _load().get(key)
        if (found and found.get("md5") and found.get("scheme") == kind
                and found.get("size") == size and found.get("mtime") == when):
            return str(found["md5"]), ""

    digest, reason = compute(where, console)
    if digest:
        with _cache_lock:
            _load()[key] = {"md5": digest, "scheme": kind, "size": size,
                            "mtime": when, "at": int(time.time())}
            _dirty = True
    return digest, reason


def prune(keep: set[str]) -> int:
    """Drop what was worked out for games that are no longer there.

    Called with the whole library in hand, since that is the only moment the
    difference between "deleted" and "not being asked about right now" is
    knowable.
    """
    global _dirty  # noqa: PLW0603
    with _cache_lock:
        cache = _load()
        gone = [key for key in cache if key not in keep]
        for key in gone:
            del cache[key]
        _dirty = _dirty or bool(gone)
    return len(gone)


def flush() -> None:
    """Write the cache out, if anything has been added since the last time."""
    global _dirty  # noqa: PLW0603
    with _cache_lock:
        if not _dirty or _cache is None:
            return
        payload = dict(_cache)
        _dirty = False
    try:
        CACHE.parent.mkdir(parents=True, exist_ok=True)
        temporary = CACHE.with_suffix(".tmp")
        with open(temporary, "w", encoding="utf-8") as fh:
            json.dump(payload, fh)
        os.replace(temporary, CACHE)
    except OSError:
        pass
