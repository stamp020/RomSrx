"""The whole path: a game in a library, a patch, a patched file beside it.

The download is stubbed so the test owns both sides and knows the answer.
Everything after that - finding the ROM inside the archive, applying, naming
and writing the result - is the real code.
"""
import io
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from romsrx import patcher  # noqa: E402

ROM = bytes(range(256)) * 16                      # 4,096 bytes, unremarkable
# Write "HI" at offset 4, and cut nothing.
IPS = (b"PATCH" + (4).to_bytes(3, "big") + (2).to_bytes(2, "big") + b"HI"
       + b"EOF")
WANT = ROM[:4] + b"HI" + ROM[6:]

archive = io.BytesIO()
with zipfile.ZipFile(archive, "w") as zf:
    zf.writestr("Some Game (USA).ips", IPS)
    zf.writestr("readme.txt", "not a patch")
patcher.fetch = lambda url: archive.getvalue()    # the one stubbed part

root = Path(tempfile.mkdtemp(prefix="romsrx-patch-"))
ok = fail = 0


def check(label, got, want):
    global ok, fail                                # noqa: PLW0603
    if got == want:
        ok += 1
        print(f"  pass  {label}")
    else:
        fail += 1
        print(f"  FAIL  {label}\n          got  {got!r}\n          want {want!r}")


# --- a game stored as a zip, which is how most of the library looks ---------
zipped = root / "Some Game (USA).zip"
with zipfile.ZipFile(zipped, "w") as zf:
    zf.writestr("Some Game (USA).sfc", ROM)
res = patcher.patch_game(str(zipped), "http://example/patch.zip")
out = Path(res["written"])
check("zip: writes a patched file", out.exists(), True)
check("zip: named beside the original", out.name, "Some Game (USA) (patched).sfc")
check("zip: contents are right", out.read_bytes(), WANT)
check("zip: original untouched", zipped.exists(), True)
check("zip: reports the format", res["kind"], "ips")

# --- a game stored as a bare ROM -------------------------------------------
bare = root / "Bare Game.sfc"
bare.write_bytes(ROM)
res2 = patcher.patch_game(str(bare), "http://example/patch.zip")
check("bare rom: contents are right", Path(res2["written"]).read_bytes(), WANT)

# --- a game stored as a folder ---------------------------------------------
folder = root / "Folder Game"
folder.mkdir()
(folder / "Folder Game.sfc").write_bytes(ROM)
res3 = patcher.patch_game(str(folder), "http://example/patch.zip")
check("folder: contents are right", Path(res3["written"]).read_bytes(), WANT)
check("folder: written inside it", Path(res3["written"]).parent, folder)

# --- the refusals ----------------------------------------------------------
crowded = root / "Crowded"
crowded.mkdir()
(crowded / "Disc 1.sfc").write_bytes(ROM)
(crowded / "Disc 2.sfc").write_bytes(ROM)
try:
    patcher.patch_game(str(crowded), "http://example/patch.zip")
    check("several ROMs refused", "no error", "an error")
except patcher.PatchError as exc:
    check("several ROMs refused", "several ROMs" in str(exc), True)

disc = root / "Disc Game.chd"
disc.write_bytes(b"\x00" * 64)
try:
    patcher.patch_game(str(disc), "http://example/patch.zip")
    check("disc image refused", "no error", "an error")
except patcher.PatchError as exc:
    check("disc image refused", "cartridge ROMs" in str(exc), True)

try:
    patcher.patch_game(str(root / "nothing here.sfc"), "http://example/patch.zip")
    check("missing game refused", "no error", "an error")
except patcher.PatchError as exc:
    check("missing game refused", "no longer where" in str(exc), True)

# --- several patches in one archive: ask rather than guess ------------------
two = io.BytesIO()
with zipfile.ZipFile(two, "w") as zf:
    zf.writestr("Variant A.ips", IPS)
    zf.writestr("Variant B.ips", IPS)
patcher.fetch = lambda url: two.getvalue()
res4 = patcher.patch_game(str(bare), "http://example/two.zip")
check("two patches: offers the choice", res4.get("choices"), ["Variant A.ips", "Variant B.ips"])
res5 = patcher.patch_game(str(bare), "http://example/two.zip", choose="Variant B.ips")
check("two patches: applies the chosen one", res5.get("patch"), "Variant B.ips")

shutil.rmtree(root, ignore_errors=True)
print(f"\n{ok} passed, {fail} failed")
