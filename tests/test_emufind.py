"""Finding the emulators on a machine that has told this app nothing.

The button exists for the person who has just installed this and configured
nothing, and that was exactly the case it could not answer: the search only
ever looked in Program Files, %LOCALAPPDATA% and beside the emulators already
set up, so somebody with `D:\\Emulator\\Retroarch` - which is what an unpacked
zip looks like, and how most of these are shipped - got "found no emulators"
however many they had.

So what is pinned here is reach: an emulator in a folder this app was never
told about is found from nothing but a drive root, including when it is sat
behind the container folders people actually use ("Games", "Emulators",
"steamapps/common"), and the walk still refuses to wander into the system.

The other thing pinned is the comparison. A path saved with forward slashes
and the same path read back with backslashes are one program, and treating
them as two turned "everything is already set" into an offer to replace every
console with what it was already pointed at.

Nothing here touches the real disk outside a temporary folder, and nothing
touches the network.
"""
import io
import os
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from romsrx import emufind  # noqa: E402

ok = fail = 0


def check(label, got, want):
    global ok, fail  # noqa: PLW0603
    if got == want:
        ok += 1
        print(f"  pass  {label}")
    else:
        fail += 1
        print(f"  FAIL  {label}\n          got  {got!r}\n          want {want!r}")


box = Path(tempfile.mkdtemp(prefix="emufind-"))


def make(*parts: str) -> Path:
    """One executable, and the folders leading to it."""
    path = box.joinpath(*parts)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"MZ")
    return path


def find(root: Path, depth: int = emufind.DEPTH) -> dict:
    """What the walk turns up under one folder, by lowercased filename."""
    wanted = {name.lower() for _, names, _ in emufind.KNOWN for name in names}
    return {k: str(v) for k, v in emufind._find_exes([(root, depth)],  # noqa: SLF001
                                                     wanted).items()}


print("an emulator nobody mentioned")

# The shape that started this: a zip unpacked onto a second drive.
plain = make("drive", "Emulator", "Retroarch", "retroarch.exe")
found = find(box / "drive")
check("found from the drive root", found.get("retroarch.exe"), str(plain))

# ...and the same thing behind the folder names people actually use. None of
# these count against the depth, which is what stops a shallow search from
# missing something that is not hiding.
steam = make("steam", "Steam", "steamapps", "common", "RetroArch", "retroarch.exe")
check("found through steamapps/common",
      find(box / "steam").get("retroarch.exe"), str(steam))

nested = make("deep", "Games", "Emulators", "mGBA", "mGBA.exe")
check("found through Games/Emulators",
      find(box / "deep").get("mgba.exe"), str(nested))

# Depth is still finite, or this would be a search of the whole disk.
make("far", "one", "two", "three", "four", "Dolphin.exe")
check("gives up on a folder nobody could have guessed",
      find(box / "far").get("dolphin.exe"), None)

print("\nwhat it refuses to walk into")
make("sys", "Windows", "System32", "retroarch.exe")
check("never opens Windows", find(box / "sys"), {})
make("junk", "node_modules", "somepackage", "PPSSPP.exe")
check("never opens node_modules", find(box / "junk"), {})

print("\nnaming an installer is not naming an emulator")
make("careful", "PCSX2", "pcsx2-setup.exe")
check("an installer is left alone", find(box / "careful"), {})

print("\nwhich console gets what")
make("mixed", "Emulation", "PCSX2", "pcsx2-qt.exe")
make("mixed", "Emulation", "RetroArch", "retroarch.exe")
picked = find(box / "mixed")
check("both are found", sorted(picked), ["pcsx2-qt.exe", "retroarch.exe"])

# From here on the search is pointed at the temporary folder and nowhere
# else. What _roots() decides to look at is checked above by reach; these
# check what scan() makes of what it found, and that answer should be the
# same on a machine with a dozen emulators installed as on one with none.
emufind._roots = lambda settings: [(box / "mixed", emufind.DEPTH)]  # noqa: SLF001

# The dedicated emulator takes its own console and RetroArch takes what is
# left over.
out = emufind.scan({"emulators": {}})
check("PCSX2 gets the PlayStation 2",
      out["consoles"].get("PlayStation 2", {}).get("name"), "PCSX2")
check("RetroArch gets a console nothing else claimed",
      out["consoles"].get("Nintendo 64", {}).get("name"), "RetroArch")
check("nothing is reported as occupied on a fresh machine", out["occupied"], 0)

print("\none path spelled two ways is one program")
where = box / "mixed" / "Emulation" / "PCSX2" / "pcsx2-qt.exe"
already = {"PlayStation 2": str(where).replace("\\", "/")}
out = emufind.scan({"emulators": already})
same = out["consoles"].get("PlayStation 2", {})
check("the console it is already set to is left alone", same.get("same"), True)
check("...and is not counted as pointed somewhere else", out["occupied"], 0)

check("normalising agrees about slashes",
      emufind._norm("D:/Emulator/Retroarch/retroarch.exe")  # noqa: SLF001
      == emufind._norm("D:\\Emulator\\Retroarch\\retroarch.exe"),  # noqa: SLF001
      os.name == "nt")

print("\nthe caps hold")
check("a folder count that cannot run away", emufind.MAX_DIRS <= 50000, True)
check("...and a clock that cannot either", emufind.MAX_SECONDS <= 30, True)

shutil.rmtree(box, ignore_errors=True)
print(f"\n{ok} passed, {fail} failed")
sys.exit(1 if fail else 0)
