"""A copy of your saves from every session, filed by when you played.

autosave.py answers "my memory card is corrupt" - a whole-saves zip on a
schedule. This answers "I want last Tuesday evening back", which a scheduled
backup cannot: it snapshots at a time unrelated to when anybody was playing,
and keeps one copy of everything rather than one copy per moment worth
returning to.

Two decisions are worth holding in place here, because both could reasonably
have gone the other way and the reasons are not obvious from the code:

  the day is the unit thrown away, not the session - so a heavy weekend
  cannot push out a month of history, and somebody who plays six times on a
  Saturday keeps all six;

  and only what changed is copied - a session that wrote one memory card
  copies one memory card, not the hundreds of megabytes a full RetroArch
  folder holds, which would otherwise be copied again every time.

Nothing here touches the network, and nothing here writes into an emulator's
folder.
"""
import io
import os
import shutil
import sys
import tempfile
import time
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

_box = Path(tempfile.mkdtemp(prefix="romsrx-history-"))
os.environ["APPDATA"] = str(_box)

from romsrx import history, saves  # noqa: E402

ok = fail = 0


def check(label, got, want):
    global ok, fail  # noqa: PLW0603
    if got == want:
        ok += 1
        print(f"  pass  {label}")
    else:
        fail += 1
        print(f"  FAIL  {label}\n          got  {got!r}\n          want {want!r}")


# Stand in for the emulators' own folders; nothing real is read.
CARDS = _box / "emu" / "memcards"
STATES = _box / "emu" / "sstates"
for _d in (CARDS, STATES):
    _d.mkdir(parents=True)
RA_SAVES = _box / "retroarch" / "saves"
RA_SAVES.mkdir(parents=True)
saves.folders = lambda settings=None: [
    {"label": "PCSX2 memcards", "system": "PCSX2", "kind": "memcards",
     "path": str(CARDS)},
    {"label": "PCSX2 sstates", "system": "PCSX2", "kind": "sstates",
     "path": str(STATES)},
    {"label": "RetroArch saves", "system": "RetroArch", "kind": "saves",
     "path": str(RA_SAVES)},
]


def played(*writes, at=None):
    """A session that wrote these files, and then closed."""
    began = time.time()
    time.sleep(0.05)
    for path, text in writes:
        path.write_text(text, encoding="utf-8")
    return history.take(began, now=at)


# -- a session that changed nothing -----------------------------------------

print("\na session that saved nothing")
# Deliberately not an empty folder: a list of moments you can go back to
# should only hold moments there is something to go back to.
quiet = played()
check("keeps nothing", quiet["saved"], 0)
check("...and leaves no folder behind", quiet["at"], "")
check("...so there are no days yet", history.days(), [])


# -- one that did -----------------------------------------------------------

print("\na session that wrote a memory card")
first = played((CARDS / "Mcd001.ps2", "sixty hours"))
check("the card is kept", first["saved"], 1)
spot = Path(first["at"])
check("...under the hour and minute it finished",
      len(spot.name) >= 5 and spot.name[2] == "-", True)
check("...inside a folder named for the day",
      spot.parent.name, datetime.now().strftime("%Y-%m-%d"))
# The emulator comes first, because that is how somebody looks for one of
# these: they know which machine they were playing.
check("...under the emulator it belongs to", spot.parent.parent.name, "PCSX2")
check("...with the emulator's own folder name kept",
      (spot / "memcards" / "Mcd001.ps2").read_text(encoding="utf-8"),
      "sixty hours")
check("...so the whole path reads system / day / time / kind",
      spot.relative_to(history.where()).parts[:2] + ("...",),
      ("PCSX2", datetime.now().strftime("%Y-%m-%d"), "..."))

# The whole point of only copying what moved: the save state was already
# there and was not touched, so it is not copied again.
print("\nand only what that session actually changed")
second = played((CARDS / "Mcd001.ps2", "sixty-one hours"))
check("just the file that moved", second["saved"], 1)
check("...not the ones that did not",
      (Path(second["at"]) / "sstates").exists(), False)


# -- two sessions in the same minute ----------------------------------------

print("\ntwo sessions inside one minute")
# Ending at 21:48 twice is two sessions, not one overwriting the other.
a = played((CARDS / "Mcd001.ps2", "one"), at=1_800_000_000)
b = played((CARDS / "Mcd001.ps2", "two"), at=1_800_000_000)
check("both are kept", Path(a["at"]) != Path(b["at"]), True)
check("...in the same day", Path(a["at"]).parent, Path(b["at"]).parent)
check("...and neither was overwritten",
      (Path(a["at"]) / "memcards" / "Mcd001.ps2").read_text(
          encoding="utf-8"), "one")


# -- two emulators, two histories -------------------------------------------

print("\ntwo emulators are kept apart")
both = played((CARDS / "Mcd001.ps2", "ps2 progress"),
              (RA_SAVES / "Sonic.srm", "mega drive progress"))
check("both are kept", both["saved"], 2)
check("...in a folder each",
      sorted(Path(p).parent.parent.name for p in both["places"]),
      ["PCSX2", "RetroArch"])


# -- what gets thrown away --------------------------------------------------

print("\nfifteen days, and the sixteenth")
root = history.where()
ps2 = root / "PCSX2"
for back in range(1, 17):
    day = ps2 / (datetime.now() - timedelta(days=back)).strftime("%Y-%m-%d")
    (day / "20-00" / "memcards").mkdir(parents=True, exist_ok=True)
    (day / "20-00" / "memcards" / "Mcd001.ps2").write_text("x")
ra_before = len(history.days(root / "RetroArch"))
out = played((CARDS / "Mcd001.ps2", "sixty-two hours"))
check("the oldest days go", len(out["dropped"]) > 0, True)
check("...leaving fifteen", len(history.days(ps2)), history.KEEP_DAYS)
check("...and the oldest is the one that went",
      all(d.split("/")[-1] not in [p.name for p in history.days(ps2)]
          for d in out["dropped"]), True)
check("...while today is still there",
      datetime.now().strftime("%Y-%m-%d") in [p.name for p in history.days(ps2)],
      True)
# The fifteen are counted per emulator: a fortnight of PS2 must not shorten
# the history of a machine that has not been touched.
check("...and the other emulator is untouched by it",
      len(history.days(root / "RetroArch")), ra_before)

# A day is thrown away, never a session inside one: somebody who plays six
# times on a Saturday wants all six, and counting sessions would let one
# heavy weekend push out a month.
print("\nand within a day there is no limit")
day_now = ps2 / datetime.now().strftime("%Y-%m-%d")
count = len(history.sessions(day_now))
for i in range(6):
    played((CARDS / "Mcd001.ps2", f"run {i}"))
check("every session that day is kept",
      len(history.sessions(day_now)) >= count + 6, True)
check("...and it is still one day of the fifteen",
      len(history.days(ps2)), history.KEEP_DAYS)

# -- putting one back -------------------------------------------------------
#
# The only thing in this app that writes over something the reader cannot get
# again from anywhere else. So it is guarded twice: it will not run while the
# game is open, because the emulator writes its save out on the way and would
# undo the restore silently; and it snapshots what is there first, so picking
# the wrong evening is a thing you can walk back.

print("\nputting an earlier save back")

from romsrx import library  # noqa: E402

CARD = CARDS / "Mcd001.ps2"
monday = played((CARD, "chapter 3 - before the missable chest"))
played((CARD, "chapter 5 - walked past it"))
played((CARD, "chapter 9 - far too late"))
check("the card is where the last session left it",
      CARD.read_text(encoding="utf-8"), "chapter 9 - far too late")

# Said before anything is written: the reader should not learn what it was
# about to do by watching it happen.
intent = history.plan(monday["at"])
check("the plan names the emulator", intent["system"], "PCSX2")
check("...and what it would put back",
      [Path(f["to"]).name for f in intent["files"]], ["Mcd001.ps2"])
check("...and that it would write over something",
      [f["replaces"] for f in intent["files"]], [True])

done = history.restore(monday["at"])
check("the file goes back", done["restored"], 1)
check("...and the card reads what it did that evening",
      CARD.read_text(encoding="utf-8"),
      "chapter 3 - before the missable chest")

# The way back from a restore, taken before the restore.
check("what was there first was kept", bool(done["undo"]), True)
history.restore(done["undo"])
check("...so the restore itself can be undone",
      CARD.read_text(encoding="utf-8"), "chapter 9 - far too late")


print("\nand what it refuses to do")


class _Open:
    """An emulator that has not been closed."""

    def poll(self):
        return None


library._running.append(_Open())  # noqa: SLF001
try:
    history.restore(monday["at"])
    check("it will not restore under a running game", "went ahead", "refused")
except history.Refused:
    check("it will not restore under a running game", "refused", "refused")
finally:
    library._running.clear()  # noqa: SLF001
check("...and the card is untouched",
      CARD.read_text(encoding="utf-8"), "chapter 9 - far too late")

try:
    history.restore(_box / "no" / "such" / "moment")
    check("a snapshot that is gone is refused", "went ahead", "refused")
except history.Refused:
    check("a snapshot that is gone is refused", "refused", "refused")

shutil.rmtree(_box, ignore_errors=True)
print(f"\n{ok} passed, {fail} failed")
sys.exit(1 if fail else 0)
