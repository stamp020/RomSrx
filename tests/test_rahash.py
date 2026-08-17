"""The RetroAchievements hash, rule by rule.

Every one of these is a rule about which bytes of a file are hashed, and every
way of getting one wrong produces a hash that is perfectly well-formed and
belongs to nothing. There is no checksum to catch that: the failure looks
exactly like "this dump isn't in the set", which is a thing the app says out
loud about somebody's game. So the rules are pinned here one at a time, and
the two that look alike - SNES and PC Engine - are pinned against each other
as well, on a file where they disagree.

Everything is built here. Nothing touches the network, and no real ROM is
needed: what is being tested is which range of bytes goes into the digest,
and a range of made-up bytes tests that as well as a cartridge would.
"""
import hashlib
import io
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from romsrx import rahash  # noqa: E402

ok = fail = 0


def check(label, got, want):
    global ok, fail  # noqa: PLW0603
    if got == want:
        ok += 1
        print(f"  pass  {label}")
    else:
        fail += 1
        print(f"  FAIL  {label}\n          got  {got!r}\n          want {want!r}")


def digest(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()  # noqa: S324


def body(length: int, seed: int = 0) -> bytes:
    """Bytes that differ from every other run of bytes of the same length."""
    return bytes((seed + i * 7 + (i >> 8)) & 0xFF for i in range(length))


class Sandbox:
    """A folder to put files in, thrown away afterwards."""

    def __enter__(self):
        self.where = Path(tempfile.mkdtemp(prefix="rahash-"))
        return self

    def __exit__(self, *_):
        shutil.rmtree(self.where, ignore_errors=True)

    def file(self, name: str, data: bytes) -> Path:
        path = self.where / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return path

    def zipped(self, name: str, members: dict) -> Path:
        path = self.where / name
        with zipfile.ZipFile(path, "w") as archive:
            for inner, data in members.items():
                archive.writestr(inner, data)
        return path


def hashed(path, console: str) -> str:
    """The hash, or the reason there isn't one - so a mistake reads plainly."""
    found, reason = rahash.compute(path, console)
    return found or f"<{reason}>"


# -- the whole file -------------------------------------------------------

print("plain")
with Sandbox() as box:
    data = body(4096)
    check("Mega Drive is the file itself",
          hashed(box.file("game.md", data), "Genesis/Mega Drive"),
          digest(data))
    check("Game Boy is the file itself",
          hashed(box.file("game.gb", data), "Game Boy"), digest(data))
    check("a disc console is not answered for",
          hashed(box.file("game.chd", data), "PlayStation"), "<unsupported>")
    check("nor is a console nobody named",
          hashed(box.file("game.rom", data), ""), "<unsupported>")

# -- the headers ----------------------------------------------------------

print("\nheaders")
with Sandbox() as box:
    payload = body(32768, seed=3)

    headered = b"NES\x1a" + body(12, seed=9) + payload
    check("an iNES header is skipped",
          hashed(box.file("a.nes", headered), "NES/Famicom"), digest(payload))
    check("...and a file without one is hashed whole",
          hashed(box.file("b.nes", payload), "NES/Famicom"), digest(payload))
    check("an FDS header is skipped too",
          hashed(box.file("c.fds", b"FDS\x1a" + body(12) + payload),
                 "Famicom Disk System"), digest(payload))
    check("a 16-byte file that only looks headered keeps its bytes",
          hashed(box.file("d.nes", b"NES\x1a" + body(12)), "NES/Famicom"),
          digest(b"NES\x1a" + body(12)))

    seven = b"\x01ATARI7800" + body(118, seed=4)
    check("a 7800 header is skipped",
          hashed(box.file("e.a78", seven + payload), "Atari 7800"),
          digest(payload))
    check("...and it is recognised at offset one, not zero",
          hashed(box.file("f.a78", b"ATARI7800" + body(119) + payload),
                 "Atari 7800"),
          digest(b"ATARI7800" + body(119) + payload))

    lynx = b"LYNX\0" + body(59, seed=5)
    check("a Lynx header is skipped",
          hashed(box.file("g.lnx", lynx + payload), "Atari Lynx"),
          digest(payload))
    check("...and 'LYNX' without the nul is not one",
          hashed(box.file("h.lnx", b"LYNXX" + body(59) + payload),
                 "Atari Lynx"),
          digest(b"LYNXX" + body(59) + payload))

# -- the two that look alike ----------------------------------------------

print("\nSNES and PC Engine, which are not the same rule")
with Sandbox() as box:
    copier = body(512, seed=7)

    # 8192 + 512: 512 more than a multiple of 8KB, so both rules skip it.
    both = copier + body(8192, seed=8)
    check("SNES skips 512 over a multiple of 8KB",
          hashed(box.file("a.sfc", both), "SNES/Super Famicom"),
          digest(body(8192, seed=8)))
    check("a SNES file that is a clean multiple of 8KB keeps its head",
          hashed(box.file("b.sfc", body(16384, seed=2)), "SNES/Super Famicom"),
          digest(body(16384, seed=2)))

    # 1536 bytes: bit 9 is set, so PC Engine skips - but 1536 is not 512 over
    # a multiple of 8KB, so the SNES rule would not have. This file is the
    # whole reason the two are written out separately.
    odd = copier + body(1024, seed=6)
    check("PC Engine skips on bit 9 alone",
          hashed(box.file("c.pce", odd), "PC Engine/TurboGrafx-16"),
          digest(body(1024, seed=6)))
    check("...where the SNES rule would not have",
          hashed(box.file("d.sfc", odd), "SNES/Super Famicom"), digest(odd))

# -- byte order -----------------------------------------------------------

print("\nNintendo 64")
with Sandbox() as box:
    native = b"\x80\x37\x12\x40" + body(4092, seed=11)

    def swap16(data):
        out = bytearray(data)
        out[0::2], out[1::2] = data[1::2], data[0::2]
        return bytes(out)

    def swap32(data):
        return b"".join(data[at:at + 4][::-1] for at in range(0, len(data), 4))

    check("a z64 is hashed as it lies",
          hashed(box.file("a.z64", native), "Nintendo 64"), digest(native))
    check("a v64 is byte-swapped back first",
          hashed(box.file("b.v64", swap16(native)), "Nintendo 64"),
          digest(native))
    check("an n64 is word-swapped back first",
          hashed(box.file("c.n64", swap32(native)), "Nintendo 64"),
          digest(native))
    check("something that is no byte order at all is not hashed",
          hashed(box.file("d.z64", b"\x99" + body(4095)), "Nintendo 64"),
          "<notrom>")

# -- the card that is mostly not hashed -----------------------------------

print("\nNintendo DS")


def ds_rom(arm9_at=0x4000, arm9_size=0x200, arm7_at=0x8000, arm7_size=0x100,
           icon_at=0xC000, prefix=b"") -> tuple[bytes, bytes]:
    """A card and the bytes its hash is supposed to cover."""
    card = bytearray(body(0xE000, seed=13))
    header = bytearray(card[:512])
    for at, value in ((0x20, arm9_at), (0x2C, arm9_size),
                      (0x30, arm7_at), (0x3C, arm7_size), (0x68, icon_at)):
        header[at:at + 4] = value.to_bytes(4, "little")
    card[:512] = header
    covered = (bytes(header[:0x160])
               + bytes(card[arm9_at:arm9_at + arm9_size])
               + bytes(card[arm7_at:arm7_at + arm7_size])
               + bytes(card[icon_at:icon_at + 0xA00]))
    return prefix + bytes(card), covered


with Sandbox() as box:
    card, covered = ds_rom()
    check("header, both boot codes and the icon block",
          hashed(box.file("a.nds", card), "Nintendo DS"), digest(covered))
    check("and a DSi card by the same rule",
          hashed(box.file("b.dsi", card), "Nintendo DSi"), digest(covered))

    # The offsets are relative to the real header, which sits after the
    # dumper's own 512 bytes - so a SuperCard dump of a game must come out as
    # that same game.
    supercard = bytearray(body(512, seed=17))
    supercard[0:4] = b"\x2e\x00\x00\xea"
    supercard[0xB0:0xB4] = b"\x44\x46\x96\x00"
    carded, _ = ds_rom(prefix=bytes(supercard))
    check("a SuperCard header is seen through",
          hashed(box.file("c.nds", carded), "Nintendo DS"), digest(covered))

    huge, _ = ds_rom(arm9_size=0x1000000, arm7_size=0x1000000)
    check("boot code the size of a disc means this was never a DS card",
          hashed(box.file("d.nds", huge), "Nintendo DS"), "<notrom>")

    short = body(200)
    check("a file too short to hold a header is not one",
          hashed(box.file("e.nds", short), "Nintendo DS"), "<notrom>")

# -- what the ROM arrived in ----------------------------------------------

print("\ncontainers")
with Sandbox() as box:
    payload = body(9000, seed=21)
    rom = b"NES\x1a" + body(12) + payload

    check("a zip holding one ROM is that ROM",
          hashed(box.zipped("a.zip", {"Game (USA).nes": rom}), "NES/Famicom"),
          digest(payload))
    check("...and the header inside it is still skipped",
          hashed(box.zipped("b.zip", {"g.nes": rom, "readme.txt": b"hello"}),
                 "NES/Famicom"), digest(payload))
    check("a zip holding two ROMs is not guessed at",
          hashed(box.zipped("c.zip", {"one.nes": rom, "two.nes": rom + b"!"}),
                 "NES/Famicom"), "<ambiguous>")
    check("a zip holding one oddly-named file is that file",
          hashed(box.zipped("d.zip", {"cart.rom": payload}),
                 "Genesis/Mega Drive"), digest(payload))
    check("a broken zip is not a hash",
          hashed(box.file("e.zip", b"PK\x03\x04 and then rubbish"),
                 "NES/Famicom"), "<unreadable>")

    folder = box.where / "Game (USA)"
    folder.mkdir()
    (folder / "Game (USA).nes").write_bytes(rom)
    check("a folder holding one ROM is that ROM",
          hashed(folder, "NES/Famicom"), digest(payload))
    (folder / "Game (USA) (Alt).nes").write_bytes(rom + b"!")
    check("a folder holding two is not guessed at",
          hashed(folder, "NES/Famicom"), "<ambiguous>")

    nested = box.where / "Nested"
    nested.mkdir()
    with zipfile.ZipFile(nested / "inner.zip", "w") as archive:
        archive.writestr("Game.nes", rom)
    check("a folder holding one zip is what is in the zip",
          hashed(nested, "NES/Famicom"), digest(payload))

    check("a file that isn't there has no hash",
          hashed(box.where / "nothing.nes", "NES/Famicom"), "<unreadable>")

# -- the wrappers this cannot see inside ----------------------------------
# The bug these exist for: a game stored as a .7z used to fall through to
# "hash the file as it lies", which gave a perfectly good hash of the
# compressed archive and reported the game as one its set does not accept.
# Being unable to open a wrapper is not evidence about what is inside it.

print("\nwrappers")
with Sandbox() as box:
    payload = body(6000, seed=51)
    rom = b"NES\x1a" + body(12) + payload

    check("a .rar is not hashed as though it were the ROM",
          hashed(box.file("a.rar", b"Rar!\x1a\x07\x00" + body(500)),
                 "NES/Famicom"), "<archive>")
    check("nor is a .gz",
          hashed(box.file("b.gz", b"\x1f\x8b\x08" + body(500)),
                 "Genesis/Mega Drive"), "<archive>")

    # By content, not by name. A zip called .md is a zip, and hashing it as a
    # Mega Drive cartridge is the same mistake wearing a different extension.
    disguised = box.where / "c.md"
    with zipfile.ZipFile(disguised, "w") as archive:
        archive.writestr("Game.md", payload)
    check("a zip that calls itself a cartridge is still a zip",
          hashed(disguised, "Genesis/Mega Drive"), digest(payload))

    try:
        import py7zr  # noqa: F401

        seven = box.where / "d.7z"
        with py7zr.SevenZipFile(seven, "w") as archive:
            inner = box.file("inner/Game.nes", rom)
            archive.write(inner, "Game.nes")
        check("a .7z is opened and the ROM inside it hashed",
              hashed(seven, "NES/Famicom"), digest(payload))

        folder = box.where / "packed"
        folder.mkdir()
        shutil.copyfile(seven, folder / "Game.7z")
        check("...including the one sitting alone in a folder",
              hashed(folder, "NES/Famicom"), digest(payload))
    except ImportError:
        print("  skip  .7z (py7zr not installed)")

# -- the cap --------------------------------------------------------------

print("\nthe 64MB cap")
with Sandbox() as box:
    was = rahash.CAP
    try:
        rahash.CAP = 1024
        long_one = body(4096, seed=31)
        check("only the first CAP bytes are hashed",
              hashed(box.file("a.md", long_one), "Genesis/Mega Drive"),
              digest(long_one[:1024]))
        # The cap is applied before the header is looked for, which is what
        # rcheevos does - so the hash covers CAP bytes minus the header.
        headered = b"NES\x1a" + body(12, seed=33) + body(4096, seed=34)
        check("...and the header comes off what is left",
              hashed(box.file("b.nes", headered), "NES/Famicom"),
              digest(headered[16:1024]))
    finally:
        rahash.CAP = was

# -- not doing the work twice ---------------------------------------------

print("\nthe cache")
with Sandbox() as box:
    was_cache, was_memory = rahash.CACHE, rahash._cache
    try:
        rahash.CACHE = box.where / "filehashes.json"
        rahash._cache = {}
        rom = box.file("a.md", body(2048, seed=41))

        first, _ = rahash.md5(rom, "Genesis/Mega Drive")
        check("a hash is remembered", bool(rahash._cache), True)

        # Rewritten with different bytes and a different length, which is what
        # the cache checks. Same path, so a cache that ignored the file itself
        # would hand back the old answer.
        rom.write_bytes(body(3072, seed=42))
        second, _ = rahash.md5(rom, "Genesis/Mega Drive")
        check("a changed file is hashed again", second, digest(body(3072, seed=42)))
        check("...and is not the old answer", second == first, False)

        # A console with a different rule is a different question about the
        # same bytes, and must not be answered from the wrong one.
        entry = next(iter(rahash._cache.values()))
        check("the rule is remembered with the hash", entry["scheme"], "plain")

        rahash.flush()
        check("the cache is written out", rahash.CACHE.is_file(), True)

        rahash.prune(set())
        check("pruning drops what is no longer in the library",
              rahash._cache, {})
    finally:
        rahash.CACHE, rahash._cache = was_cache, was_memory
        rahash._dirty = False

# -- the map ---------------------------------------------------------------

print("\nconsoles")
check("every console with a rule can name its ROM extensions",
      sorted(set(rahash.SCHEMES) - set(rahash.EXTENSIONS)), [])
check("PlayStation is deliberately absent", rahash.scheme("PlayStation"), "")
check("Nintendo DS is present", rahash.scheme("Nintendo DS"), "ds")

print(f"\n{ok} passed, {fail} failed")
sys.exit(1 if fail else 0)
