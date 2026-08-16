"""The PPF patcher, in all three of its versions.

PPF is how disc patches have always been published, and the three versions
differ in ways that are easy to get almost right: how wide an offset is, what
sits between the description and the first record, and whether every record
carries a spare copy of what it overwrote. Getting any of those wrong writes
the right bytes to the wrong places, which no checksum here would catch.

Nothing touches the network.
"""
import io
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from romsrx import patcher  # noqa: E402

ok = fail = 0


def check(label, got, want):
    global ok, fail  # noqa: PLW0603
    if got == want:
        ok += 1
        print(f"  pass  {label}")
    else:
        fail += 1
        print(f"  FAIL  {label}\n          got  {got!r}\n          want {want!r}")


DESCRIPTION = b"a patch".ljust(50, b"\x00")


def ppf1(records):
    out = b"PPF10" + bytes([0]) + DESCRIPTION
    for offset, data in records:
        out += offset.to_bytes(4, "little") + bytes([len(data)]) + data
    return out


def ppf2(records, size=1024):
    out = (b"PPF20" + bytes([1]) + DESCRIPTION
           + size.to_bytes(4, "little") + bytes(1024))
    for offset, data in records:
        out += offset.to_bytes(4, "little") + bytes([len(data)]) + data
    return out


def ppf3(records, undo=False, blockcheck=False):
    out = (b"PPF30" + bytes([2]) + DESCRIPTION
           + bytes([0, 1 if blockcheck else 0, 1 if undo else 0, 0]))
    if blockcheck:
        out += bytes(1024)
    for offset, data in records:
        out += offset.to_bytes(8, "little") + bytes([len(data)]) + data
        if undo:
            out += bytes(len(data))      # what was there before, which we skip
    return out


SOURCE = bytes(range(256)) * 4           # 1,024 bytes


def patched(source, *pairs):
    out = bytearray(source)
    for offset, data in pairs:
        out[offset:offset + len(data)] = data
    return bytes(out)


# --- the three versions ----------------------------------------------------
check("a 1.0 patch is recognised", patcher.detect(ppf1([(0, b"AB")])), "ppf")
check("so is 2.0", patcher.detect(ppf2([(0, b"AB")])), "ppf")
check("so is 3.0", patcher.detect(ppf3([(0, b"AB")])), "ppf")

check("1.0 writes where it says",
      patcher.apply(SOURCE, ppf1([(10, b"HELLO")])),
      patched(SOURCE, (10, b"HELLO")))
check("2.0 writes where it says, past its header",
      patcher.apply(SOURCE, ppf2([(10, b"HELLO")])),
      patched(SOURCE, (10, b"HELLO")))
check("3.0 writes where it says, with its wider offsets",
      patcher.apply(SOURCE, ppf3([(10, b"HELLO")])),
      patched(SOURCE, (10, b"HELLO")))

# The undo copy is the one that silently ruins a patch if it is not skipped:
# every record after the first would be read from the wrong place.
check("3.0 skips the undo data and stays in step",
      patcher.apply(SOURCE, ppf3([(10, b"AAA"), (900, b"ZZZ")], undo=True)),
      patched(SOURCE, (10, b"AAA"), (900, b"ZZZ")))
check("3.0 with a block check reads past it",
      patcher.apply(SOURCE, ppf3([(5, b"QQ")], blockcheck=True)),
      patched(SOURCE, (5, b"QQ")))

check("several records all land",
      patcher.apply(SOURCE, ppf1([(0, b"aa"), (100, b"bb"), (1020, b"cc")])),
      patched(SOURCE, (0, b"aa"), (100, b"bb"), (1020, b"cc")))

# --- the author's notes at the end are not a record ------------------------
noisy = ppf1([(10, b"OK")]) + b"@BEGIN_FILE_ID.DIZ" + b"notes about it" * 4
check("notes after the records are ignored",
      patcher.apply(SOURCE, noisy), patched(SOURCE, (10, b"OK")))

# --- refusals --------------------------------------------------------------
def refuses(label, source, blob, phrase):
    try:
        patcher.apply(source, blob)
        check(label, "no error", "an error")
    except patcher.PatchError as exc:
        check(label, phrase in str(exc), True)


refuses("writing past the end is refused", SOURCE, ppf1([(1020, b"toolong")]),
        "different dump")
refuses("a truncated record is refused", SOURCE,
        ppf1([]) + (5).to_bytes(4, "little") + bytes([9]) + b"only3", "middle")
try:
    patcher.parse_ppf(b"PPF40" + bytes([3]) + DESCRIPTION)
    check("an unknown version is refused", "no error", "an error")
except patcher.PatchError as exc:
    check("an unknown version is refused", "does not know" in str(exc), True)

# --- a file too big to hold ------------------------------------------------
root = Path(tempfile.mkdtemp(prefix="romsrx-ppf-"))
big = root / "disc.iso"
big.write_bytes(SOURCE * 64)             # 64 KB stands in for a disc
out = root / "disc (patched).iso"
written = patcher.apply_ppf_to_file(big, ppf3([(4096, b"PATCHED")]), out)

check("the copy is the same size", written, big.stat().st_size)
check("the change landed in the copy",
      out.read_bytes()[4096:4103], b"PATCHED")
check("the rest of the copy is untouched",
      out.read_bytes()[:4096], big.read_bytes()[:4096])
check("the original is untouched",
      big.read_bytes()[4096:4103], (SOURCE * 64)[4096:4103])

shutil.rmtree(root, ignore_errors=True)
print(f"\n{ok} passed, {fail} failed")
