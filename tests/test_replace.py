"""Replacing the original with the patched version.

This is the one option here that destroys something, so what is tested is not
really "does it work" but "what happens when it does not". The ordering is
built so the game never exists under neither name; these check that it holds
even when the rename fails.

Nothing touches the network.
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

ok = fail = 0


def check(label, got, want):
    global ok, fail  # noqa: PLW0603
    if got == want:
        ok += 1
        print(f"  pass  {label}")
    else:
        fail += 1
        print(f"  FAIL  {label}\n          got  {got!r}\n          want {want!r}")


ROM = bytes(range(256)) * 16
IPS = (b"PATCH" + (4).to_bytes(3, "big") + (2).to_bytes(2, "big") + b"HI"
       + b"EOF")
WANT = ROM[:4] + b"HI" + ROM[6:]

archive = io.BytesIO()
with zipfile.ZipFile(archive, "w") as zf:
    zf.writestr("Some Fix.ips", IPS)
patcher.fetch = lambda url: archive.getvalue()

root = Path(tempfile.mkdtemp(prefix="romsrx-replace-"))

# --- off: exactly what it did before --------------------------------------
game = root / "Game A.sfc"
game.write_bytes(ROM)
res = patcher.patch_game(str(game), "http://x/p.zip")
check("off: the original is still there", game.is_file(), True)
check("off: and unchanged", game.read_bytes(), ROM)
check("off: the patched copy is a second file",
      Path(res["written"]) != game, True)
check("off: which holds the patched bytes",
      Path(res["written"]).read_bytes(), WANT)

# --- on: the patched version takes its place ------------------------------
game_b = root / "Game B.sfc"
game_b.write_bytes(ROM)
res = patcher.patch_game(str(game_b), "http://x/p.zip", replace=True)
check("on: the game keeps its own name", Path(res["written"]), game_b)
check("on: and is now the patched one", game_b.read_bytes(), WANT)
check("on: it says so", res.get("replaced"), True)
check("on: nothing else is left beside it",
      sorted(p.name for p in root.glob("Game B*")), ["Game B.sfc"])
check("on: no leftover from moving it aside",
      list(root.glob("*.unpatched")), [])

# --- on, but the game is inside a container -------------------------------
# Replacing a zip or a folder with a bare ROM would leave the library pointing
# at something that is no longer what it says.
zipped = root / "Game C.zip"
with zipfile.ZipFile(zipped, "w") as zf:
    zf.writestr("Game C.sfc", ROM)
res = patcher.patch_game(str(zipped), "http://x/p.zip", replace=True)
check("a zipped game is not replaced", zipped.is_file(), True)
check("and says why", res.get("keptBecauseContainer"), True)
check("the patched ROM is written beside it",
      Path(res["written"]).read_bytes(), WANT)

folder = root / "Game D"
folder.mkdir()
(folder / "Game D.sfc").write_bytes(ROM)
res = patcher.patch_game(str(folder), "http://x/p.zip", replace=True)
check("a folder game is not replaced either", folder.is_dir(), True)
check("its ROM is left alone", (folder / "Game D.sfc").read_bytes(), ROM)

# --- when the rename fails, the game comes back ---------------------------
# The dangerous moment: the original has been moved aside and the patched file
# cannot take its name. Nothing may be lost.
game_e = root / "Game E.sfc"
game_e.write_bytes(ROM)
patched = root / "Game E (Fix).sfc"
patched.write_bytes(WANT)

real_rename = Path.rename
calls = {"n": 0}


def failing_rename(self, target):
    calls["n"] += 1
    if calls["n"] == 2:                 # the second is patched -> original
        raise OSError("denied, for the sake of argument")
    return real_rename(self, target)


Path.rename = failing_rename
try:
    patcher._take_the_place_of(game_e, patched)  # noqa: SLF001
    check("a failed rename is reported", "no error", "an error")
except patcher.PatchError as exc:
    check("a failed rename is reported", "could not take" in str(exc), True)
finally:
    Path.rename = real_rename

check("the original is back under its own name", game_e.is_file(), True)
check("with its own contents", game_e.read_bytes(), ROM)
check("and nothing is left moved aside", list(root.glob("*.unpatched")), [])

shutil.rmtree(root, ignore_errors=True)
print(f"\n{ok} passed, {fail} failed")
