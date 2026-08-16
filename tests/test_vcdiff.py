"""The xdelta/VCDIFF decoder.

A patch format with no checksum on the result is the dangerous kind: decode it
wrongly and you get a plausible file that is quietly broken. So this checks the
code table against the shape RFC 3284 lays down, then drives every instruction
and every address mode through the decoder.
"""
import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from romsrx import patcher  # noqa: E402
from romsrx.patcher import _ADD, _COPY, _NOOP, _RUN  # noqa: E402

ok = fail = 0


def check(label, got, want):
    global ok, fail  # noqa: PLW0603
    if got == want:
        ok += 1
        print(f"  pass  {label}")
    else:
        fail += 1
        print(f"  FAIL  {label}\n          got  {got!r}\n          want {want!r}")


# ---------- the code table ----------
# Every index is documented, so these are fixed points rather than a
# restatement of the code that builds it.
T = patcher._CODE_TABLE  # noqa: SLF001
check("table has 256 entries", len(T), 256)
check("0 is RUN", T[0], ((_RUN, 0, 0), (_NOOP, 0, 0)))
check("1 is ADD with a separate size", T[1], ((_ADD, 0, 0), (_NOOP, 0, 0)))
check("2 is ADD size 1", T[2], ((_ADD, 1, 0), (_NOOP, 0, 0)))
check("18 is ADD size 17", T[18], ((_ADD, 17, 0), (_NOOP, 0, 0)))
check("19 is COPY mode 0, separate size", T[19], ((_COPY, 0, 0), (_NOOP, 0, 0)))
check("20 is COPY size 4 mode 0", T[20], ((_COPY, 4, 0), (_NOOP, 0, 0)))
check("34 is COPY size 18 mode 0", T[34], ((_COPY, 18, 0), (_NOOP, 0, 0)))
check("35 begins mode 1", T[35], ((_COPY, 0, 1), (_NOOP, 0, 0)))
check("163 is the first ADD+COPY", T[163], ((_ADD, 1, 0), (_COPY, 4, 0)))
check("234 is the last of the six-mode block", T[234], ((_ADD, 4, 0), (_COPY, 6, 5)))
check("235 begins the modes that only copy 4", T[235], ((_ADD, 1, 0), (_COPY, 4, 6)))
check("246 ends it", T[246], ((_ADD, 4, 0), (_COPY, 4, 8)))
check("247 is the first COPY+ADD", T[247], ((_COPY, 4, 0), (_ADD, 1, 0)))
check("255 is the last", T[255], ((_COPY, 4, 8), (_ADD, 1, 0)))
check("every entry is reachable", all(len(e) == 2 for e in T), True)


# ---------- building patches to feed it ----------
def vint(n):
    """A VCDIFF integer: base 128, most significant group first."""
    if n == 0:
        return b"\x00"
    groups = []
    while n:
        groups.append(n & 0x7F)
        n >>= 7
    groups.reverse()
    return bytes(g | (0x80 if i < len(groups) - 1 else 0)
                 for i, g in enumerate(groups))


def one(op, size, mode=0):
    """The table index for a single instruction, or None if it needs a size."""
    for i, ((o, s, m), (o2, _, _)) in enumerate(T):
        if o2 == _NOOP and (o, s, m) == (op, size, mode):
            return i
    return None


def window(target_size, data, insts, addrs, src=None, src_pos=0):
    body = b""
    indicator = 0
    if src is not None:
        indicator = 0x01
        body += vint(src) + vint(src_pos)
    rest = (vint(target_size) + b"\x00" + vint(len(data)) + vint(len(insts))
            + vint(len(addrs)) + data + insts + addrs)
    return bytes([indicator]) + body + vint(len(rest)) + rest


def patch(*windows, app_header=b""):
    head = bytes(patcher.VCDIFF_MAGIC) + b"\x00"
    if app_header:
        return head + b"\x04" + vint(len(app_header)) + app_header + b"".join(windows)
    return head + b"\x00" + b"".join(windows)


# ---------- the instructions ----------
# ADD: literal bytes straight from the data section.
p = patch(window(5, b"HELLO", bytes([one(_ADD, 5)]), b""))
check("ADD copies literal bytes", patcher.apply_vcdiff(b"", p), b"HELLO")

# ADD with a size too big for the table carries its own size.
big = b"x" * 40
p = patch(window(40, big, bytes([one(_ADD, 0)]) + vint(40), b""))
check("ADD with a separate size", patcher.apply_vcdiff(b"", p), big)

# RUN: one byte, repeated.
p = patch(window(6, b"z", bytes([one(_RUN, 0)]) + vint(6), b""))
check("RUN repeats one byte", patcher.apply_vcdiff(b"", p), b"zzzzzz")

# COPY from the source, mode 0 - a plain address.
src = b"ABCDEFGHIJ"
p = patch(window(4, b"", bytes([one(_COPY, 4, 0)]), vint(2), src=len(src)))
check("COPY takes from the source", patcher.apply_vcdiff(src, p), b"CDEF")

# COPY that runs into what it is writing, which is how a repeat is expressed.
insts = bytes([one(_ADD, 2)]) + bytes([one(_COPY, 6, 0)])
p = patch(window(8, b"ab", insts, vint(0)))
check("COPY may overlap what it writes", patcher.apply_vcdiff(b"", p), b"abababab")

# Two instructions in one byte: the pairing the table exists for.
p = patch(window(5, b"Z", bytes([163]), vint(0), src=len(src)))
check("one byte, two instructions", patcher.apply_vcdiff(src, p), b"ZABCD")


# ---------- the address modes ----------
# mode 1 counts back from where we are.
insts = bytes([one(_ADD, 4)]) + bytes([one(_COPY, 4, 1)])
p = patch(window(8, b"WXYZ", insts, vint(4)))
check("mode 1 counts back from here", patcher.apply_vcdiff(b"", p), b"WXYZWXYZ")

# mode 2 steps on from the most recent address.
insts = (bytes([one(_COPY, 4, 0)]) + bytes([one(_COPY, 4, 2)]))
p = patch(window(8, b"", insts, vint(0) + vint(4), src=len(src)))
check("mode 2 steps on from a recent address",
      patcher.apply_vcdiff(src, p), b"ABCDEFGH")

# mode 6 quotes an address seen before at the same slot.
insts = (bytes([one(_COPY, 4, 0)]) + bytes([one(_COPY, 4, 6)]))
addr = vint(4) + bytes([4 % 256])
p = patch(window(8, b"", insts, addr, src=len(src)))
check("mode 6 quotes an address seen before",
      patcher.apply_vcdiff(src, p), b"EFGHEFGH")

# An application header is skipped, not read as data.
p = patch(window(5, b"HELLO", bytes([one(_ADD, 5)]), b""), app_header=b"made by xdelta3")
check("an application header is skipped", patcher.apply_vcdiff(b"", p), b"HELLO")

# Several windows join end to end.
p = patch(window(3, b"one", bytes([one(_ADD, 3)]), b""),
          window(3, b"two", bytes([one(_ADD, 3)]), b""))
check("windows join end to end", patcher.apply_vcdiff(b"", p), b"onetwo")


# ---------- the refusals ----------
def refuses(label, blob, phrase, source=b""):
    try:
        patcher.apply_vcdiff(source, blob)
        check(label, "no error", "an error")
    except patcher.PatchError as exc:
        check(label, phrase in str(exc), True)


refuses("secondary compression refused by name",
        bytes(patcher.VCDIFF_MAGIC) + b"\x00\x01", "compressed in a way")
refuses("a custom code table is refused",
        bytes(patcher.VCDIFF_MAGIC) + b"\x00\x02", "own instruction table")
refuses("a newer version is refused",
        bytes(patcher.VCDIFF_MAGIC) + b"\x09\x00", "newer xdelta")
refuses("something that is not a patch", b"nonsense here", "not an xdelta patch")
refuses("a truncated patch", bytes(patcher.VCDIFF_MAGIC) + b"\x00", "damaged")

# A window that promises more than it delivers must not pass silently.
p = patch(window(99, b"HELLO", bytes([one(_ADD, 5)]), b""))
refuses("a window that under-fills its result", p, "without filling")

# A source segment reaching past the end of the file it is given.
p = patch(window(4, b"", bytes([one(_COPY, 4, 0)]), vint(0), src=999))
refuses("a source segment past the end of the file", p, "past the end", source=src)

# Compressed sections inside an otherwise plain window.
bad = (bytes(patcher.VCDIFF_MAGIC) + b"\x00\x00" + b"\x00" + vint(9) + vint(5)
       + b"\x01" + vint(5) + vint(1) + vint(0) + b"HELLO" + bytes([one(_ADD, 5)]))
refuses("compressed sections refused", bad, "compressed in a way")

print(f"\n{ok} passed, {fail} failed")
