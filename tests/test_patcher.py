"""Exercise the patcher against patches built here, so the answer is known.

A real patch can only be checked by having the exact ROM it expects. Building
the patches instead means the expected result is known in advance, and every
one of BPS's four actions can be made to appear on purpose - including the
self-referencing copy, which is the one worth getting wrong quietly.
"""
import io
import sys
from pathlib import Path
import zlib

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from romsrx import patcher  # noqa: E402

ok = fail = 0


def check(label, got, want):
    global ok, fail                                    # noqa: PLW0603
    if got == want:
        ok += 1
        print(f"  pass  {label}")
    else:
        fail += 1
        print(f"  FAIL  {label}\n          got  {got!r}\n          want {want!r}")


def varint(n):
    """BPS's encoding, the mirror of the decoder under test."""
    out = bytearray()
    while True:
        low = n & 0x7F
        n >>= 7
        if n == 0:
            out.append(0x80 | low)
            return bytes(out)
        out.append(low)
        n -= 1


def signed(n):
    return varint((abs(n) << 1) | (1 if n < 0 else 0))


def build_bps(source, target, actions):
    body = (patcher.BPS_MAGIC + varint(len(source)) + varint(len(target))
            + varint(0) + actions)
    body += (zlib.crc32(source) & 0xFFFFFFFF).to_bytes(4, "little")
    body += (zlib.crc32(target) & 0xFFFFFFFF).to_bytes(4, "little")
    return body + (zlib.crc32(body) & 0xFFFFFFFF).to_bytes(4, "little")


# --- BPS, with all four actions in one patch -------------------------------
source = b"ABCDEFGH"
target = b"ABC" + b"XYZ" + b"GH" + b"XYZ"
actions = (
    varint(((3 - 1) << 2) | 0)                       # SourceRead "ABC"
    + varint(((3 - 1) << 2) | 1) + b"XYZ"            # TargetRead "XYZ"
    + varint(((2 - 1) << 2) | 2) + signed(6)         # SourceCopy "GH"
    + varint(((3 - 1) << 2) | 3) + signed(3)         # TargetCopy "XYZ"
)
check("BPS: all four actions", patcher.apply_bps(source, build_bps(source, target, actions)), target)

# The self-referencing copy: reading bytes it is still writing, which is how
# BPS spells a repeat. A block copy would get this wrong.
src2 = b"\x00" * 4
tgt2 = b"AB" + b"ABABAB"
acts2 = (varint(((2 - 1) << 2) | 1) + b"AB"
         + varint(((6 - 1) << 2) | 3) + signed(0))
check("BPS: overlapping repeat", patcher.apply_bps(src2, build_bps(src2, tgt2, acts2)), tgt2)

# --- BPS refusals ----------------------------------------------------------
good = build_bps(source, target, actions)
try:
    patcher.apply_bps(b"ABCDEFGX", good)              # right size, wrong dump
    check("BPS: wrong dump refused", "no error", "an error")
except patcher.PatchError as exc:
    check("BPS: wrong dump refused", "different dump" in str(exc), True)

try:
    patcher.apply_bps(b"SHORT", good)
    check("BPS: wrong size refused", "no error", "an error")
except patcher.PatchError as exc:
    check("BPS: wrong size refused", "different release" in str(exc), True)

try:
    patcher.apply_bps(source, good[:20] + b"\x00" + good[21:])
    check("BPS: damaged patch refused", "no error", "an error")
except patcher.PatchError as exc:
    check("BPS: damaged patch refused", "damaged" in str(exc), True)

# --- IPS -------------------------------------------------------------------
ips = (b"PATCH"
       + (2).to_bytes(3, "big") + (2).to_bytes(2, "big") + b"HI"
       + (5).to_bytes(3, "big") + (0).to_bytes(2, "big")
       + (3).to_bytes(2, "big") + b"\xff"
       + b"EOF")
check("IPS: write and run-length",
      patcher.apply_ips(b"\x00" * 10, ips),
      bytes([0, 0, 72, 73, 0, 255, 255, 255, 0, 0]))

check("IPS: truncate footer",
      patcher.apply_ips(b"\x00" * 10, ips + (8).to_bytes(3, "big")),
      bytes([0, 0, 72, 73, 0, 255, 255, 255]))

check("IPS: grows the file when it must",
      len(patcher.apply_ips(b"\x00" * 4,
                            b"PATCH" + (6).to_bytes(3, "big")
                            + (2).to_bytes(2, "big") + b"ZZ" + b"EOF")), 8)

# --- detection -------------------------------------------------------------
check("detect bps", patcher.detect(good), "bps")
check("detect ips", patcher.detect(ips), "ips")
check("detect xdelta", patcher.detect(b"\xd6\xc3\xc4\x00rest"), "xdelta")
check("detect nothing", patcher.detect(b"not a patch at all"), "")

# xdelta is applied now, not refused - so `apply` must route it to the VCDIFF
# decoder rather than to one of the other two. A minimal patch that just adds
# five literal bytes is enough to tell which one ran.
xdelta = (b"\xd6\xc3\xc4\x00\x00"          # magic, version, no header flags
          b"\x00"                          # window: no source segment
          b"\x0b"                          # length of the rest of the window
          b"\x05"                          # target window is five bytes
          b"\x00"                          # sections are not compressed
          b"\x05\x01\x00"                  # data 5, instructions 1, addresses 0
          b"HELLO"                         # the data
          b"\x06")                         # ADD, size 5
check("apply routes xdelta to the decoder", patcher.apply(b"", xdelta), b"HELLO")

# The one xdelta this app still cannot read says so by name, rather than
# failing as though the file were broken.
try:
    patcher.apply(b"", b"\xd6\xc3\xc4\x00\x01")
    check("compressed xdelta refused by name", "no error", "an error")
except patcher.PatchError as exc:
    check("compressed xdelta refused by name", "xdelta" in str(exc), True)

print(f"\n{ok} passed, {fail} failed")
