"""Reading RetroArch's achievement settings, without touching them.

The failure this exists to prevent is silent: hardcore is a switch inside
another program, and the way anybody finds out it was off is finishing a game
and seeing the unlocks land as softcore, worth no points and no mastery.

Three things are pinned. What each combination of settings means - including
the two defaults, since RetroArch does not write a line for a setting nobody
has changed, and reading an absent line as "off" would send somebody hunting
for a switch already where they want it. That being signed in as a different
person is noticed. And that the token, which sits in the same file three lines
away, is never read.

Nothing touches the network, and no real RetroArch is needed - the config is
written here.
"""
import io
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from romsrx import artwork, hardcore  # noqa: E402

ok = fail = 0


def check(label, got, want):
    global ok, fail  # noqa: PLW0603
    if got == want:
        ok += 1
        print(f"  pass  {label}")
    else:
        fail += 1
        print(f"  FAIL  {label}\n          got  {got!r}\n          want {want!r}")


box = Path(tempfile.mkdtemp(prefix="hardcore-"))
artwork.settings = lambda: {"retroachievements":
                            {"api_key": "xyz", "username": "Someone"}}


def config(**lines):
    """A retroarch.cfg holding exactly what is asked for, plus a token.

    The token is always there, because the point is that it is never taken.
    """
    where = box / "RetroArch"
    where.mkdir(exist_ok=True)
    body = ["cheevos_token = \"NEVER-READ-THIS\"",
            "video_fullscreen = \"true\""]
    body += [f'{key} = "{value}"' for key, value in lines.items()]
    (where / "retroarch.cfg").write_text("\n".join(body) + "\n", encoding="utf-8")
    # Found through the emulator the user has configured, which is how the
    # app finds a RetroArch anywhere but the default folders.
    return {"emulators": {"NES/Famicom": str(where / "retroarch.exe")}}


def issues(**lines):
    return hardcore.status(config(**lines))["issues"]


print("what would stop a session counting")
check("everything on is nothing to report",
      issues(cheevos_enable="true", cheevos_hardcore_mode_enable="true",
             cheevos_username="Someone"), [])
check("achievements off is said first",
      issues(cheevos_enable="false", cheevos_hardcore_mode_enable="true",
             cheevos_username="Someone"), ["off"])
check("...and softcore is not piled on underneath it",
      "softcore" in issues(cheevos_enable="false",
                           cheevos_hardcore_mode_enable="false",
                           cheevos_username="Someone"), False)
check("hardcore off is softcore",
      issues(cheevos_enable="true", cheevos_hardcore_mode_enable="false",
             cheevos_username="Someone"), ["softcore"])
check("nobody signed in is worth saying on its own",
      issues(cheevos_enable="true", cheevos_hardcore_mode_enable="true",
             cheevos_username=""), ["nouser"])
check("signed in as somebody else is noticed",
      issues(cheevos_enable="true", cheevos_hardcore_mode_enable="true",
             cheevos_username="AnotherPerson"), ["otheruser"])
check("...but the same person spelled differently is not",
      issues(cheevos_enable="true", cheevos_hardcore_mode_enable="true",
             cheevos_username="someone"), [])

# RetroArch writes no line for a setting nobody has touched, and its default
# for both of these is on. This is the case that would have produced a warning
# about a switch already in the right place.
print("\nsettings nobody has changed")
check("an unwritten setting is its default, not off",
      issues(cheevos_username="Someone"), [])
found = hardcore.status(config(cheevos_username="Someone"))
check("...and reads as on", (found["achievements"], found["hardcore"]),
      (True, True))

print("\nwhat is read, and what is not")
found = hardcore.status(config(cheevos_enable="true", cheevos_username="Someone"))
check("the username comes back", found["user"], "Someone")
check("the file it read is named", found["where"].endswith("retroarch.cfg"), True)
check("the token is nowhere in the answer",
      "NEVER-READ-THIS" in repr(found), False)
check("...and neither is anything else from the file",
      sorted(found), ["achievements", "found", "hardcore", "issues", "mine",
                      "ok", "user", "where"])

print("\nwith no RetroArch at all")
empty = hardcore.status({"emulators": {"NES/Famicom": str(box / "nowhere.exe")}})
check("nothing found is nothing said", empty["found"], False)
check("...and it is not an error", empty["ok"], True)
check("...with no issues to act on", empty["issues"], [])

# The looking is done in the folders beside the configured emulator, and those
# are whatever happens to be there. This crashed the whole call on Linux: the
# temporary folder above lives in /tmp, /tmp on a CI runner holds root-owned
# systemd-private-* folders at mode 0700, and asking is_file() about something
# inside one raises PermissionError rather than answering False.
print("\nand a folder it is not allowed to look in")
real_is_file = Path.is_file


def refuse(self):
    if "forbidden" in str(self):
        raise PermissionError(13, "Permission denied", str(self))
    return real_is_file(self)


(box / "forbidden").mkdir(exist_ok=True)
Path.is_file = refuse
try:
    walled = hardcore.status(config(cheevos_username="Someone"))
    check("a folder that refuses to answer is skipped, not fatal",
          walled["user"], "Someone")
except OSError as exc:
    check("a folder that refuses to answer is skipped, not fatal",
          f"raised {exc!r}", "no error")
finally:
    Path.is_file = real_is_file

shutil.rmtree(box, ignore_errors=True)
print(f"\n{ok} passed, {fail} failed")
sys.exit(1 if fail else 0)
