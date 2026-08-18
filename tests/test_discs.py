"""Finding the program a disc boots, and hashing that.

A cartridge rule is "which bytes"; a disc rule is "which file", and getting
there means walking somebody else's filesystem using offsets that are only
ever documented by the code that reads them. Every number in discs.py is one
of those, so the discs here are built byte by byte and the expected hash is
worked out independently in this file - if the walk goes wrong the two will
not agree.

Three geometries, because a disc image is not one format. A .iso keeps 2048
bytes per sector and nothing else; a raw .bin keeps 2352, of which 16 or 24
are a wrapper depending on the mode, and the wrapper is not always what the
.cue claims. Reading the payload from the wrong offset produces a perfectly
well-formed hash of the wrong bytes, which is the failure this whole file
exists to catch.

Nothing touches the network and no real disc is needed.
"""
import hashlib
import io
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from romsrx import discs  # noqa: E402

ok = fail = 0


def check(label, got, want):
    global ok, fail  # noqa: PLW0603
    if got == want:
        ok += 1
        print(f"  pass  {label}")
    else:
        fail += 1
        print(f"  FAIL  {label}\n          got  {got!r}\n          want {want!r}")


def md5(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()  # noqa: S324


# -- building a disc -------------------------------------------------------
# Small but structurally real: a primary volume descriptor at sector 16 whose
# root directory record points at a directory, and records in that directory
# for each file.

SECTOR = 2048


def record(name: bytes, sector: int, size: int) -> bytes:
    """One ISO9660 directory record, laid out where discs.py looks."""
    body = bytearray(33 + len(name))
    body[2:5] = sector.to_bytes(3, "little")
    body[10:14] = size.to_bytes(4, "little")
    body[32] = len(name)
    body[33:] = name
    if len(body) % 2:
        body += b"\0"                     # records are padded to even lengths
    body[0] = len(body)
    return bytes(body)


def build(files: dict, root_sector: int = 20) -> bytes:
    """A disc holding these {name: contents}, as flat 2048-byte sectors."""
    sectors: dict[int, bytes] = {}

    volume = bytearray(SECTOR)
    volume[1:6] = b"CD001"
    volume[128:130] = SECTOR.to_bytes(2, "little")        # logical block size
    volume[156 + 2:156 + 5] = root_sector.to_bytes(3, "little")
    volume[156 + 10:156 + 14] = SECTOR.to_bytes(4, "little")   # one sector
    sectors[16] = bytes(volume)

    at = root_sector + 1
    directory = bytearray()
    for name, body in files.items():
        directory += record(name.encode(), at, len(body))
        for n in range(0, max(len(body), 1), SECTOR):
            sectors[at] = body[n:n + SECTOR].ljust(SECTOR, b"\0")
            at += 1
    sectors[root_sector] = bytes(directory).ljust(SECTOR, b"\0")

    out = bytearray(SECTOR * (max(sectors) + 1))
    for number, body in sectors.items():
        out[number * SECTOR:(number + 1) * SECTOR] = body
    return bytes(out)


def raw(flat: bytes, header: int) -> bytes:
    """The same disc as a 2352-byte-per-sector image, wrapper and all."""
    out = bytearray()
    for at in range(0, len(flat), SECTOR):
        sector = bytearray(2352)
        sector[0:12] = discs.SYNC
        sector[header:header + SECTOR] = flat[at:at + SECTOR]
        out += sector
    return bytes(out)


# A PS-X EXE header states the size of what follows it, and the hash covers
# that much plus the header's own 2048 bytes. Built as exactly those two
# halves so there is no padding to argue about, with a longer variant below
# to prove the stated size is what counts rather than the length of the file.
PSX_HEAD = b"PS-X EXE" + bytes(20) + (2048).to_bytes(4, "little") + bytes(2016)
EXE = PSX_HEAD + b"g" * 2048
PSX = {"SYSTEM.CNF": b"BOOT = cdrom:\\SLUS_007.77;1\r\nTCB = 4\r\n",
       "SLUS_007.77": EXE}
PSX_WANT = md5(b"SLUS_007.77" + EXE)

# The same executable with more file after it than its header admits to.
LONG_EXE = EXE + b"data the header does not count" * 200
PSX_LONG = {"SYSTEM.CNF": b"BOOT = cdrom:\\SLUS_007.77;1\n",
            "SLUS_007.77": LONG_EXE}

ELF = b"\x7fELF" + b"a playstation 2 game" * 300
PS2 = {"SYSTEM.CNF": b"BOOT2 = cdrom0:\\SLUS_123.45;1\nVER = 1.00\n",
       "SLUS_123.45": ELF}
PS2_WANT = md5(b"SLUS_123.45" + ELF)


class Sandbox:
    def __enter__(self):
        self.where = Path(tempfile.mkdtemp(prefix="discs-"))
        return self

    def __exit__(self, *_):
        shutil.rmtree(self.where, ignore_errors=True)

    def file(self, name, data):
        path = self.where / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return path


def hashed(path, console):
    found, reason = discs.md5(path, console)
    return found or f"<{reason}>"


# -- the two consoles ------------------------------------------------------

print("finding the boot executable")
with Sandbox() as box:
    check("a PlayStation 2 .iso",
          hashed(box.file("g.iso", build(PS2)), "PlayStation 2"), PS2_WANT)
    check("a PlayStation .iso",
          hashed(box.file("p.iso", build(PSX)), "PlayStation"), PSX_WANT)
    check("...and the name is part of the hash, not just the contents",
          PS2_WANT == md5(ELF), False)
    # The one that would go unnoticed: hashing the whole executable rather
    # than the length its own header states gives a hash that looks perfectly
    # fine and belongs to nothing.
    check("a PlayStation hash stops where the header says it does",
          hashed(box.file("l.iso", build(PSX_LONG)), "PlayStation"), PSX_WANT)
    check("a console with no rule here is not answered for",
          hashed(box.file("s.iso", build(PS2)), "Sega Saturn"), "<unsupported>")

# -- the geometries --------------------------------------------------------
# The same disc, wrapped three ways. All three must produce one hash.

print("\nsector layouts")
with Sandbox() as box:
    flat = build(PS2)
    check("2048-byte sectors",
          hashed(box.file("a.iso", flat), "PlayStation 2"), PS2_WANT)
    check("2352-byte sectors, 16-byte header (Mode 1)",
          hashed(box.file("b.bin", raw(flat, 16)), "PlayStation 2"), PS2_WANT)
    check("2352-byte sectors, 24-byte header (Mode 2 Form 1)",
          hashed(box.file("c.bin", raw(flat, 24)), "PlayStation 2"), PS2_WANT)
    check("something that is no disc at all",
          hashed(box.file("d.iso", b"nonsense" * 5000), "PlayStation 2"),
          "<notrom>")

# -- what the boot line can look like --------------------------------------

print("\nreading the boot line")
for label, line, want in [
    ("no spaces around the equals", b"BOOT2=cdrom0:\\SLUS_123.45;1\n", "SLUS_123.45"),
    ("extra spaces", b"BOOT2   =   cdrom0:\\SLUS_123.45;1\n", "SLUS_123.45"),
    ("no version marker", b"BOOT2 = cdrom0:\\SLUS_123.45\n", "SLUS_123.45"),
    ("double backslash", b"BOOT2 = cdrom0:\\\\SLUS_123.45;1\n", "SLUS_123.45"),
    ("lines before it", b"VER = 1.00\nBOOT2 = cdrom0:\\SLUS_123.45;1\n", "SLUS_123.45"),
    ("a key that is not there", b"VER = 1.00\n", ""),
]:
    check(label, discs._boot_name(line.decode(), "BOOT2", "cdrom0:"), want)  # noqa: SLF001

# BOOT2 must not be found by a search for BOOT, or every PS2 disc would look
# for the wrong key. They are looked up per console, so this checks the
# PlayStation key does not match the PlayStation 2 line.
check("BOOT does not match a BOOT2 line",
      discs._boot_name("BOOT2 = cdrom0:\\SLUS_123.45;1", "BOOT", "cdrom:"),  # noqa: SLF001
      "")

# -- which file in a folder is the disc ------------------------------------

print("\npicking the image")
with Sandbox() as box:
    flat = build(PS2)
    one = box.where / "One Disc"
    one.mkdir()
    (one / "game.iso").write_bytes(flat)
    check("a folder holding one image", hashed(one, "PlayStation 2"), PS2_WANT)

    # The real case this was written for: a dump, a stray second copy of a
    # track, and a .cue that knows which is which.
    cued = box.where / "Cued"
    cued.mkdir()
    (cued / "game.bin").write_bytes(raw(flat, 24))
    (cued / "game (Track 1).bin").write_bytes(b"a spare copy")
    (cued / "game.cue").write_text('FILE "game.bin" BINARY\n  TRACK 01 MODE2/2352\n')
    check("...and one where a .cue says which of two", hashed(cued, "PlayStation 2"),
          PS2_WANT)

    two = box.where / "Two Discs"
    two.mkdir()
    (two / "disc1.iso").write_bytes(flat)
    (two / "disc2.iso").write_bytes(flat)
    check("a folder holding two is not guessed at",
          hashed(two, "PlayStation 2"), "<unsupported>")

    check("a .chd is not opened",
          hashed(box.file("g.chd", b"MComprHD" + bytes(500)), "PlayStation 2"),
          "<unsupported>")
    check("a file that isn't there",
          hashed(box.where / "nothing.iso", "PlayStation 2"), "<unreadable>")

print(f"\n{ok} passed, {fail} failed")
sys.exit(1 if fail else 0)
