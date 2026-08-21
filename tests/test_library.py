"""Reading a shelf that has something unreadable on it.

The folders this walks are folders somebody else chose, and not all of them
answer questions. A OneDrive placeholder, a junction into a directory this
account has no rights to, a network share that dropped between one entry and
the next - asking any of those whether it is a directory raises rather than
returning False.

Every such question in scan_folder is behind a guard except, for a while, two
of them: the check at the top and the skip-list check at the head of the loop.
Either one raising did not lose a folder, it lost the entire library scan - so
one protected folder anywhere under the games directory emptied the shelf.

The same shape took the Linux build's tests down: /tmp on a CI runner holds
root-owned systemd-private-* folders at mode 0700, and something walked into
one. It is worth a test rather than a fix.

Nothing here touches the network, and the shelf is built in a temporary
folder.
"""
import io
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from romsrx import library  # noqa: E402

ok = fail = 0


def check(label, got, want):
    global ok, fail  # noqa: PLW0603
    if got == want:
        ok += 1
        print(f"  pass  {label}")
    else:
        fail += 1
        print(f"  FAIL  {label}\n          got  {got!r}\n          want {want!r}")


box = Path(tempfile.mkdtemp(prefix="library-"))


def game(name: str, filename: str) -> Path:
    """One extracted game: a folder with a single ROM in it."""
    where = box / name
    where.mkdir(parents=True, exist_ok=True)
    (where / filename).write_bytes(b"ROM" * 400)
    return where


game("Sonic (USA)", "Sonic (USA).md")
game("Spyro (USA)", "Spyro (USA).iso")
(box / "Loose Game (USA).nes").write_bytes(b"NES" * 400)

print("an ordinary shelf")
names = sorted(g["name"] for g in library.scan_folder(box, "Genesis/Mega Drive"))
check("every game on it is found", names,
      ["Loose Game (USA)", "Sonic (USA)", "Spyro (USA)"])


print("\nand one with a folder that will not answer")
walled = box / "forbidden"
walled.mkdir(exist_ok=True)
(walled / "Something (USA).md").write_bytes(b"ROM" * 400)

real_is_dir = Path.is_dir


def refuse(self):
    # Exactly what Windows and Linux both raise for a folder this account is
    # not allowed to look at. Raised rather than answered - which is the whole
    # point: `if not folder.is_dir()` cannot see it coming.
    if "forbidden" in str(self):
        raise PermissionError(13, "Permission denied", str(self))
    return real_is_dir(self)


Path.is_dir = refuse
try:
    found = sorted(g["name"] for g in library.scan_folder(box, "Genesis/Mega Drive"))
    check("the rest of the shelf is still read", found,
          ["Loose Game (USA)", "Sonic (USA)", "Spyro (USA)"])
    check("...and the folder that refused is simply not on it",
          "Something (USA)" in found, False)

    # The top of the function, rather than one entry inside it.
    check("a shelf whose own folder refuses is empty, not an error",
          library.scan_folder(walled, "Genesis/Mega Drive"), [])
except OSError as exc:
    check("a folder that refuses to answer is skipped, not fatal",
          f"raised {exc!r}", "no error")
finally:
    Path.is_dir = real_is_dir

shutil.rmtree(box, ignore_errors=True)
print(f"\n{ok} passed, {fail} failed")
sys.exit(1 if fail else 0)
