"""Copying a RetroAchievements login from one emulator into the others.

The whole risk lives in the writing. These are other programs' settings files,
holding hundreds of choices somebody made by hand over an evening, and this
module opens them and changes two lines. So most of what is checked below is
what did *not* change - the sections either side, the settings beside the ones
written, the line endings, the password field - and what the module refuses to
do when it does not recognise what it is looking at.

Nothing here touches the network or a real emulator. The five sample files are
trimmed from the real formats, keeping the parts that matter: the section
names, the key names, and the line endings each one actually uses.
"""
import io
import os
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from romsrx import racred  # noqa: E402

ok = fail = 0


def check(label, got, want):
    global ok, fail  # noqa: PLW0603
    if got == want:
        ok += 1
        print(f"  pass  {label}")
    else:
        fail += 1
        print(f"  FAIL  {label}\n          got  {got!r}\n          want {want!r}")


# RetroArch has no sections - a flat list of quoted keys in alphabetical
# order - and it is the one with a password field that must never be copied.
RETROARCH = "\n".join([
    'audio_driver = "wasapi"',
    'cheevos_appearance_anchor = "0"',
    'cheevos_badges_enable = "true"',
    'cheevos_enable = "false"',
    'cheevos_hardcore_mode_enable = "true"',
    'cheevos_password = ""',
    'cheevos_token = "AbC123token"',
    'cheevos_username = "Someone"',
    'video_driver = "vulkan"',
]) + "\n"

# Qt writes CRLF, and the geometry line is the one nobody wants reset.
PCSX2 = "\r\n".join([
    "[UI]",
    "MainWindowGeometry = AdnQywADAAA",
    "ConfirmShutdown = false",
    "",
    "[Achievements]",
    "Enabled = false",
    "Hardcore = true",
    "Username = ",
    "Token = ",
    "",
    "[EmuCore]",
    "EnableCheats = false",
]) + "\r\n"

DUCKSTATION = "\n".join([
    "[Main]",
    "ConfirmPowerOff = true",
    "",
    "[Cheevos]",
    "Enabled = false",
    "ChallengeMode = false",
    "Username = ",
    "Token = ",
    "",
    "[Display]",
    "Renderer = Vulkan",
]) + "\n"

# Dolphin keeps this in a file of its own, and spells its booleans capitalised.
DOLPHIN = "\n".join([
    "[Achievements]",
    "Enabled = False",
    "Username = ",
    "ApiToken = ",
    "HardcoreEnabled = True",
]) + "\n"

PPSSPP = "\n".join([
    "[General]",
    "FirstRun = False",
    "",
    "[Achievements]",
    "AchievementsEnable = False",
    "AchievementsUserName = ",
    "AchievementsToken = ",
    "AchievementsChallengeMode = True",
    "",
    "[Graphics]",
    "InternalResolution = 2",
]) + "\n"

WHERE = {
    "RetroArch": ("Retroarch/retroarch.exe", "Retroarch/retroarch.cfg",
                  RETROARCH),
    "PCSX2": ("PS2/pcsx2-qt.exe", "PS2/inis/PCSX2.ini", PCSX2),
    "DuckStation": ("Duck/duckstation-qt.exe", "Duck/settings.ini",
                    DUCKSTATION),
    "Dolphin": ("Dolphin/Dolphin.exe",
                "Dolphin/User/Config/RetroAchievements.ini", DOLPHIN),
    "PPSSPP": ("PPSSPP/PPSSPPWindows64.exe",
               "PPSSPP/memstick/PSP/SYSTEM/ppsspp.ini", PPSSPP),
}

box = Path(tempfile.mkdtemp(prefix="racred-"))

# The profile fallbacks - Documents\PCSX2, ~/.config/retroarch - are real
# places on the machine running this, and one of them holding a real config
# would have the tests reading and, worse, writing the tester's own settings.
# Pointed at an empty corner of the temporary folder instead, so the only
# files in play are the ones laid out below.
nowhere = box / "nobody"
nowhere.mkdir()
racred._documents = lambda: nowhere
racred._home = lambda: nowhere
os.environ["APPDATA"] = str(nowhere)


def lay(root: Path, which: str) -> Path:
    """A portable install of `which`, with its settings file where it goes."""
    exe_rel, cfg_rel, body = WHERE[which]
    exe, cfg = root / exe_rel, root / cfg_rel
    exe.parent.mkdir(parents=True, exist_ok=True)
    exe.write_text("", encoding="utf-8")
    cfg.parent.mkdir(parents=True, exist_ok=True)
    # newline="" so the CRLF in the PCSX2 sample survives being written out.
    with open(cfg, "w", encoding="utf-8", newline="") as handle:
        handle.write(body)
    return cfg


def settings(root: Path, *names: str) -> dict:
    """What the app's own settings would look like with these configured."""
    made = {}
    for name in names:
        lay(root, name)
        made[name] = str(root / WHERE[name][0])
    # Keyed by console in the real thing; only the values are read.
    return {"emulators": made}


def raw(path: Path) -> str:
    with open(path, encoding="utf-8", newline="") as handle:
        return handle.read()


print("reading a login out of an emulator that has one")
root = box / "read"
conf = settings(root, "RetroArch")
found = racred.read("RetroArch", root / "Retroarch/retroarch.cfg")
check("the username comes back", found.get("user"), "Someone")
check("...and the token", found.get("token"), "AbC123token")

seen = racred.look(conf)
check("it counts as signed in", seen["signed_in"], True)
check("...and says which emulator it came from", seen["from"], "RetroArch")
check("...and as whom", seen["user"], "Someone")


print("\ncopying it into the others")
root = box / "copy"
conf = settings(root, "RetroArch", "PCSX2", "DuckStation", "Dolphin", "PPSSPP")
seen = racred.look(conf)
check("the four without a login are the four offered",
      sorted(one["emulator"] for one in seen["ready"]),
      ["Dolphin", "DuckStation", "PCSX2", "PPSSPP"])
check("...and nothing is in the way", seen["blocked"], [])

done = racred.apply(conf)
check("the copy goes through", done["ok"], True)
check("...into all four", len(done["written"]), 4)

for name in ("PCSX2", "DuckStation", "Dolphin", "PPSSPP"):
    got = racred.read(name, root / WHERE[name][1])
    check(f"{name} has the username", got.get("user"), "Someone")
    check(f"...and {name} the token", got.get("token"), "AbC123token")

seen = racred.look(conf)
check("none of them needs it now", seen["ready"], [])
check("...and they are all listed as done", sorted(seen["done"]),
      ["Dolphin", "DuckStation", "PCSX2", "PPSSPP"])


print("\nand the switch that makes it matter")
check("DuckStation's is turned on",
      "Enabled = true" in raw(root / "Duck/settings.ini"), True)
check("...and Dolphin's, spelt the way Dolphin spells it",
      "Enabled = True" in raw(root / WHERE["Dolphin"][1]), True)
# Not the one it was read from, though: that emulator is working already and
# is nobody's business here. Every byte of it is left as it was found.
check("...but the emulator it came from is not touched at all",
      raw(root / "Retroarch/retroarch.cfg"), RETROARCH)


print("\nwhat it leaves exactly as it was")
body = raw(root / "Duck/settings.ini")
check("a later section is untouched", "Renderer = Vulkan" in body, True)
check("...and an earlier one", "ConfirmPowerOff = true" in body, True)
check("...and the settings beside the two written",
      "ChallengeMode = false" in body, True)

body = raw(root / "PS2/inis/PCSX2.ini")
check("PCSX2's line endings survive", "\r\n" in body and "\n\n" not in body,
      True)
check("...and the window geometry nobody wants reset",
      "MainWindowGeometry = AdnQywADAAA" in body, True)

body = raw(root / "Retroarch/retroarch.cfg")
check("the password field is never written to",
      'cheevos_password = ""' in body, True)
check("...nor anything unrelated to achievements",
      'video_driver = "vulkan"' in body, True)


print("\nwhen there is no login to copy")
root = box / "none"
conf = settings(root, "PCSX2")
try:
    racred.apply(conf)
    check("it refuses rather than writing blanks", "no error", "refused")
except racred.CredError:
    check("it refuses rather than writing blanks", "refused", "refused")


print("\nan emulator that has never been run")
root = box / "unrun"
exe = root / "PS2" / "pcsx2-qt.exe"
exe.parent.mkdir(parents=True)
exe.write_text("", encoding="utf-8")
lay(root, "RetroArch")
conf = {"emulators": {"PCSX2": str(exe),
                      "RetroArch": str(root / "Retroarch/retroarch.exe")}}
seen = racred.look(conf)
check("it is reported rather than written to",
      [one["why"] for one in seen["blocked"]], ["not run yet"])
check("...and is not offered", seen["ready"], [])
check("...and no settings file is invented for it",
      (root / "PS2/inis/PCSX2.ini").exists(), False)


print("\na settings file it does not recognise")
root = box / "odd"
conf = settings(root, "RetroArch", "DuckStation")
odd = root / "Duck/settings.ini"
odd.write_text("[Main]\nConfirmPowerOff = true\n", encoding="utf-8")
before = raw(odd)
seen = racred.look(conf)
check("a file without the expected section is reported",
      [one["why"] for one in seen["blocked"]], ["unfamiliar settings file"])
racred.apply(conf)
check("...and left alone", raw(odd), before)


print("\nan emulator that keeps its token out of the file")
# Not hypothetical: this is exactly what PCSX2 and PPSSPP look like now. The
# section is there and the username is in it, and the token has moved to the
# operating system's credential store - which reads, from here, as a login
# that is half present. It has to be told apart from a blank one, or the app
# offers to sign in an emulator it has no way to sign in.
root = box / "elsewhere"
conf = settings(root, "RetroArch", "PCSX2")
moved = root / "PS2/inis/PCSX2.ini"
with open(moved, "w", encoding="utf-8", newline="") as handle:
    handle.write("\r\n".join([
        "[Achievements]", "Enabled = true", "Username = Someone",
        "LoginTimestamp = 1782662500", ""]))
before = raw(moved)
seen = racred.look(conf)
check("it is reported as keeping its login elsewhere",
      [one["why"] for one in seen["blocked"]], ["token not in this file"])
check("...and is not offered as something that can be signed in",
      seen["ready"], [])
racred.apply(conf)
check("...and no token line is invented for it", raw(moved), before)


print("\na section with somewhere to put the token and nowhere for the name")
# The half-understood file: enough of it recognised to get as far as writing,
# and then a key missing. It must stop there rather than write one of the two
# and leave the emulator with a token and no account to go with it.
root = box / "partial"
conf = settings(root, "RetroArch", "DuckStation")
thin = root / "Duck/settings.ini"
thin.write_text("[Cheevos]\nEnabled = false\nToken = \n", encoding="utf-8")
before = raw(thin)
done = racred.apply(conf)
check("the failure is reported", done["ok"], False)
check("...naming the emulator",
      [one["emulator"] for one in done["failed"]], ["DuckStation"])
check("...and nothing is written, not even the half it could have",
      raw(thin), before)


print("\nrunning it a second time")
root = box / "twice"
conf = settings(root, "RetroArch", "PCSX2")
racred.apply(conf)
first = (root / "PS2/inis/PCSX2.ini").read_bytes()
check("there is nothing left to do", racred.look(conf)["ready"], [])
try:
    racred.apply(conf)
    check("a second run is harmless", "no error", "no error")
except racred.CredError as exc:
    check("a second run is harmless", f"raised {exc!r}", "no error")
check("...and not one byte changes",
      (root / "PS2/inis/PCSX2.ini").read_bytes(), first)


print("\nan emulator that is already signed in as somebody")
root = box / "swap"
conf = settings(root, "RetroArch", "PCSX2")
racred.apply(conf)
cfg = root / "Retroarch/retroarch.cfg"
cfg.write_text(raw(cfg).replace("Someone", "Somebody Else")
               .replace("AbC123token", "NewToken999"), encoding="utf-8")
done = racred.apply(conf, only=["PCSX2"])
check("it is not quietly signed out and back in as somebody else",
      racred.read("PCSX2", root / "PS2/inis/PCSX2.ini").get("token"),
      "AbC123token")
check("...and nothing was written", done["written"], [])

shutil.rmtree(box, ignore_errors=True)
print(f"\n{ok} passed, {fail} failed")
sys.exit(1 if fail else 0)
