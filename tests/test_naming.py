"""Two patches for one game must not land on one filename.

This is the bug the naming rewrite exists to fix: apply a translation, then
apply a 60fps hack, and before the fix the second silently replaced the first.
"""
import io
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from romsrx import patcher  # noqa: E402

root = Path(tempfile.mkdtemp(prefix="romsrx-naming-"))
ok = fail = 0


def check(label, got, want):
    global ok, fail  # noqa: PLW0603
    if got == want:
        ok += 1
        print(f"  pass  {label}")
    else:
        fail += 1
        print(f"  FAIL  {label}\n          got  {got!r}\n          want {want!r}")


game = root / "Chrono Trigger (USA).sfc"
game.write_bytes(b"\x00" * 16)

name = lambda rom, patch: patcher._output_path(game, rom, patch).name  # noqa: E731, SLF001

# A descriptive patch name becomes the label, so two patches differ.
check("translation named after its patch",
      name("Chrono Trigger (USA).sfc", "Chrono Trigger - English Retranslation.bps"),
      "Chrono Trigger (USA) (Chrono Trigger - English Retranslation).sfc")
check("a second, different patch gets a different name",
      name("Chrono Trigger (USA).sfc", "60fps.ips"),
      "Chrono Trigger (USA) (60fps).sfc")

# A patch that says nothing falls back to the plain word.
check("patch named 'patch'", name("Game.sfc", "patch.ips"), "Game (patched).sfc")
check("patch named like the game", name("Game.sfc", "Game.ips"), "Game (patched).sfc")
check("patch with no name at all", name("Game.sfc", ""), "Game (patched).sfc")
check("very short patch name", name("Game.sfc", "v2.ips"), "Game (patched).sfc")

# An existing file is never written over.
(root / "Game (patched).sfc").write_bytes(b"first")
check("existing file not clobbered", name("Game.sfc", "patch.ips"), "Game (patched 2).sfc")
(root / "Game (patched 2).sfc").write_bytes(b"second")
check("and again", name("Game.sfc", "patch.ips"), "Game (patched 3).sfc")

# A long patch name must not push the path past what Windows accepts.
longish = "A" * 200
out = patcher._output_path(game, "Chrono Trigger (USA).sfc", longish + ".bps")  # noqa: SLF001
check("long name trimmed to a usable path", len(str(out)) <= 240, True)
check("long name keeps the game's own name", out.name.startswith("Chrono Trigger (USA) ("), True)
check("long name keeps the extension", out.suffix, ".sfc")

# The whole thing, twice, through the real entry point: two patches, two files.
ips_a = b"PATCH" + (0).to_bytes(3, "big") + (2).to_bytes(2, "big") + b"AA" + b"EOF"
ips_b = b"PATCH" + (0).to_bytes(3, "big") + (2).to_bytes(2, "big") + b"BB" + b"EOF"
rom = root / "Real Game.sfc"
rom.write_bytes(b"\x00" * 32)

import zipfile  # noqa: E402

for label, blob in (("English Translation.ips", ips_a), ("Speed Hack.ips", ips_b)):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr(label, blob)
    patcher.fetch = lambda url, _b=buf: _b.getvalue()
    patcher.patch_game(str(rom), "http://example/p.zip")

made = sorted(p.name for p in root.glob("Real Game*"))
check("both patches produced their own file", made,
      ["Real Game (English Translation).sfc", "Real Game (Speed Hack).sfc",
       "Real Game.sfc"])
check("first patch survived the second",
      (root / "Real Game (English Translation).sfc").read_bytes()[:2], b"AA")
check("second patch is its own thing",
      (root / "Real Game (Speed Hack).sfc").read_bytes()[:2], b"BB")

shutil.rmtree(root, ignore_errors=True)
print(f"\n{ok} passed, {fail} failed")
