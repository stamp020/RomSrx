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

from romsrx import history, saves, sync  # noqa: E402

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

# -- one console out of a RetroArch evening ---------------------------------
#
# RetroArch files its saves under the core, so one session's folder holds
# every console played that evening. Somebody who wants Tuesday's Game Boy
# save back should not have to take Tuesday's Nintendo 64 with it - which,
# before this, is exactly what restoring did.

print("\ntelling one console apart from another inside a session")
for _core in ("Gambatte", "Mupen64Plus-Next"):
    (RA_SAVES / _core).mkdir(parents=True, exist_ok=True)
mixed = played((RA_SAVES / "Gambatte" / "Pokemon.srm", "the good run"),
               (RA_SAVES / "Mupen64Plus-Next" / "Zelda.srm", "also tuesday"))
# Earlier tests in this file wrote into the PCSX2 folders moments ago, and a
# snapshot takes everything touched since - so this session has a folder per
# emulator and the RetroArch one is the subject here.
spot = next(Path(one) for one in mixed["places"]
            if Path(one).parent.parent.name == "RetroArch")
# Three files, not two: Sonic.srm sits loose in the saves folder from an
# earlier session above, which is what a RetroArch with its sort-by-core
# setting off looks like. Worth having in the sample rather than tidied away -
# a real install can hold both, and the loose ones still have to go somewhere.
check("everything that evening is kept",
      sum(1 for f in spot.rglob("*") if f.is_file()), 3)

parts = history.groups(spot)
check("each console is offered on its own, loose files last",
      [one["group"] for one in parts], ["Gambatte", "Mupen64Plus-Next", ""])
check("...one file each", [one["files"] for one in parts], [1, 1, 1])
# A core name is not what anybody calls a console. The map that picks a core
# for a console already exists, and this reads it backwards.
check("...named as the consoles they play, not as cores",
      [one["label"] for one in parts],
      ["Gambatte - Game Boy \u00b7 Game Boy Color",
       "Mupen64Plus-Next - Nintendo 64", ""])

print("\nand putting just that one back")
intent = history.plan(spot, only=["Gambatte"])
check("the plan covers one console", len(intent["files"]), 1)
check("...the one asked for",
      Path(intent["files"][0]["to"]).name, "Pokemon.srm")

# Overwrite both, then restore only one, and check the other stayed as it is
# now rather than being dragged back to Tuesday with it.
(RA_SAVES / "Gambatte" / "Pokemon.srm").write_text("later, worse",
                                                   encoding="utf-8")
(RA_SAVES / "Mupen64Plus-Next" / "Zelda.srm").write_text("later, better",
                                                         encoding="utf-8")
done = history.restore(spot, only=["Gambatte"])
check("one file goes back", done["restored"], 1)
check("...and it is the evening's",
      (RA_SAVES / "Gambatte" / "Pokemon.srm").read_text(encoding="utf-8"),
      "the good run")
check("...while the console not chosen is left exactly as it was",
      (RA_SAVES / "Mupen64Plus-Next" / "Zelda.srm").read_text(encoding="utf-8"),
      "later, better")

print("\nand asking for all of it still means all of it")
intent = history.plan(spot)
check("no filter restores the whole session", len(intent["files"]), 3)
check("...and says so", intent["only"], [])

print("\nan emulator with nothing to split on")
# PCSX2 puts its cards straight into `memcards` - there is no folder under
# the kind, so there is no choice to offer and the page shows no picker.
plain = played((CARDS / "Mcd002.ps2", "one card"))
check("its session has one nameless part",
      [one["group"] for one in history.groups(Path(plain["at"]))], [""])

# -- a line about what the evening was --------------------------------------
#
# Fifteen days of "21:07, 3 files" says when somebody played and nothing about
# what happened, and the whole feature is for finding one particular evening
# again. The interesting part is not the writing, it is where the note lives:
# put inside the snapshot it would be an ordinary file in the folder, counted
# among the saves and copied into the emulator's save directory by the restore
# button. So most of what is checked here is that it stays out of everything.

print("\nwriting down what an evening was")
noted = spot                            # the RetroArch session above
before = len(history.plan(noted)["files"])
was_sessions = len(history.sessions(noted.parent))
history.set_note(noted, "before the point of no return")
check("it comes back", history.note(noted), "before the point of no return")
check("...on the session it was written on",
      [one["note"] for day in history.listing()["systems"]
       for d in day["days"] for one in d["sessions"]
       if one["path"] == str(noted)],
      ["before the point of no return"])

check("...without becoming a file in the snapshot",
      sum(1 for f in noted.rglob("*") if f.is_file()), 3)
check("...so the restore does not offer to put it back",
      len(history.plan(noted)["files"]), before)
check("...and it is not mistaken for a console",
      [one["group"] for one in history.groups(noted)],
      ["Gambatte", "Mupen64Plus-Next", ""])
# days() and sessions() both list directories, so the sidecar is invisible to
# the walk that builds the panel.
check("...nor for a session of its own",
      len(history.sessions(noted.parent)), was_sessions)

print("\nchanging it and taking it away")
history.set_note(noted, "actually the run after that")
check("a second note replaces the first",
      history.note(noted), "actually the run after that")
history.set_note(noted, "   ")
check("blank removes it", history.note(noted), "")
# An empty note and no note read the same, so only one of them should be on
# disk - otherwise the fortnight fills up with empty files.
check("...and really removes it", history.note_path(noted).exists(), False)

print("\nand what it will not write down")
long_one = history.set_note(noted, "x" * 900)
check("a very long note is cut to length",
      len(long_one["note"]), history.NOTE_MAX)
history.set_note(noted, "two\nlines   and   gaps")
check("newlines and runs of spaces are flattened",
      history.note(noted), "two lines and gaps")
history.set_note(noted, "")
for _bad, _why in (("", "nothing at all"), (str(_box), "somewhere else")):
    try:
        history.set_note(_bad, "hello")
        check(f"a note refuses {_why}", "allowed", "refused")
    except history.Refused:
        check(f"a note refuses {_why}", "refused", "refused")

# -- which game the session was ---------------------------------------------
#
# A memory card does not say what wrote it, so the only moment this can be
# known is the moment the app starts the game - see library.watch. Written
# down beside the snapshot, like the note, and for the same reason: inside it
# would be a file to count, offer, and copy into somebody's saves.

print("\nremembering which game a session was")
# Every test above left files behind with a mtime of moments ago, and a
# snapshot takes everything touched since the session began - so without this
# each one below would sweep up the lot and land in two emulators at once,
# which is the case that deliberately records no game. Aged rather than
# deleted: the point is a realistic folder, and an empty one is not.
_old = time.time() - 3600


def age_everything():
    for _dir in (CARDS, STATES, RA_SAVES):
        for _f in _dir.rglob("*"):
            if _f.is_file():
                os.utime(_f, (_old, _old))


age_everything()
one = played((CARDS / "Mcd010.ps2", "spyro progress"))
spot = Path(one["at"])
check("nothing is recorded when the app did not start it",
      history.played(spot), "")

age_everything()
began = time.time()
time.sleep(0.05)
(CARDS / "Mcd011.ps2").write_text("more spyro", encoding="utf-8")
one = history.take(began, played_="Spyro the Dragon (USA)")
spot = Path(one["at"])
check("the game comes back", history.played(spot), "Spyro the Dragon (USA)")
check("...on the session, for the panel",
      [s["game"] for sy in history.listing()["systems"]
       for d in sy["days"] for s in d["sessions"] if s["path"] == str(spot)],
      ["Spyro the Dragon (USA)"])
check("...without becoming a file in the snapshot",
      sum(1 for f in spot.rglob("*") if f.is_file()), 1)
check("...and the restore does not offer to put it back",
      [Path(f["to"]).name for f in history.plan(spot)["files"]],
      ["Mcd011.ps2"])

print("\nand when it cannot honestly say")
# Two emulators wrote during the same window, and the app started one game.
# Labelling both with it would be right about one and wrong about the other,
# and a wrong label is worse than none.
age_everything()
began = time.time()
time.sleep(0.05)
(CARDS / "Mcd012.ps2").write_text("ps2 side", encoding="utf-8")
(RA_SAVES / "Sonic.srm").write_text("retroarch side", encoding="utf-8")
one = history.take(began, played_="Spyro the Dragon (USA)")
check("two emulators wrote", len(one["places"]), 2)
check("...so neither is labelled",
      [history.played(Path(where)) for where in one["places"]], ["", ""])

print("\na memory card that is a folder")
# From a real machine, not imagination. PCSX2 can keep a memory card as a
# *folder* of files rather than one file, so `memcards/Mcd001_converted.ps2/`
# is a directory - and the rule "the folder under the kind is the console"
# duly offered somebody's memory card in the console picker.
#
# Only RetroArch sorts its saves by core. Everywhere else a subfolder is just
# a subfolder, and the whole session is the only unit worth offering.
age_everything()
card = CARDS / "Mcd001_converted.ps2"
card.mkdir(parents=True, exist_ok=True)
folder_card = played((card / "Superblock1", "card innards"))
spot = Path(folder_card["at"])
check("it is not mistaken for a console",
      [one["group"] for one in history.groups(spot)], [""])
check("...so the whole session is the only thing offered",
      len(history.groups(spot)), 1)
check("...and it still restores",
      [Path(f["to"]).name for f in history.plan(spot)["files"]],
      ["Superblock1"])


print("\nshowing a session's folder in the file manager")
# It only opens a window rather than writing anything, but it takes a path
# from the page like the rest of them - and making an exception for the
# harmless-looking one is how "paths from the page are always checked" quietly
# stops being true.
check("it answers the folder itself",
      Path(history.folder(spot)), spot.resolve())
for _bad, _why in ((str(_box), "somewhere outside the history"),
                   ("", "nothing at all"),
                   (str(history.where() / "PCSX2"), "a whole emulator")):
    try:
        history.folder(_bad)
        check(f"it refuses {_why}", "allowed", "refused")
    except history.Refused:
        check(f"it refuses {_why}", "refused", "refused")


print("\nkeeping one evening past the fortnight")
# The rotation is what stops a save history becoming a disk full of them, and
# the one evening worth keeping is exactly the one somebody will still want in
# a month. A pin is the only thing that overrides the limit, so what it does
# to the limit matters as much as that it works.
root = history.where()
ps2 = root / "PCSX2"
old_day = ps2 / "2026-02-01"
(old_day / "20-00" / "memcards").mkdir(parents=True, exist_ok=True)
(old_day / "20-00" / "memcards" / "Kept.ps2").write_text("keep me")
(old_day / "21-00" / "memcards").mkdir(parents=True, exist_ok=True)
(old_day / "21-00" / "memcards" / "Ordinary.ps2").write_text("let me go")
history.set_pinned(old_day / "20-00", True)
check("it reads back as pinned", history.pinned(old_day / "20-00"), True)
check("...and its neighbour does not",
      history.pinned(old_day / "21-00"), False)

# A day older than the fifteen, holding one of each.
age_everything()
played((CARDS / "Turnover.ps2", "today"))

check("the pinned session survives the rotation",
      (old_day / "20-00" / "memcards" / "Kept.ps2").is_file(), True)
check("...the unpinned one beside it does not",
      (old_day / "21-00").exists(), False)
check("...and the day stays, holding what was kept",
      [p.name for p in history.sessions(old_day)], ["20-00"])

print("\nand a pin does not cost a day of the fifteen")
# The newest fifteen are counted from every day there is, so an evening kept
# from February must not shorten the fortnight being played through now.
recent = [p.name for p in history.days(ps2) if p.name != "2026-02-01"]
check("the fortnight is still a fortnight", len(recent), history.KEEP_DAYS)

print("\nunpinning puts it back under the ordinary rule")
history.set_pinned(old_day / "20-00", False)
check("the marker goes", history.pinned(old_day / "20-00"), False)
age_everything()
played((CARDS / "Turnover2.ps2", "today again"))
check("...and the next turnover takes it", old_day.exists(), False)


print("\nthrowing one session away")
# The only thing in this app that destroys something with nothing kept back -
# a restore snapshots what it overwrites, and this cannot, because reclaiming
# the space is the point. So what it will not reach matters more than what it
# does.
age_everything()
keep = played((CARDS / "Keep.ps2", "not this one"))
keep_spot = Path(keep["at"])
age_everything()
doomed = played((CARDS / "Doomed.ps2", "this one"))
spot = Path(doomed["at"])
history.set_note(spot, "a note that goes with it")

weighed = history.weight(spot)
check("it can say what is there first", weighed["files"], 1)
check("...and what the evening was", weighed["note"],
      "a note that goes with it")

day_of = spot.parent
history.remove(spot)
check("the session is gone", spot.exists(), False)
check("...and its note with it", history.note_path(spot).exists(), False)
check("...while the session beside it is untouched",
      keep_spot.exists(), True)
check("...and so is the day they share", day_of.exists(), True)

print("\nand the last session in a day takes the day with it")
age_everything()
lonely = played((CARDS / "Lonely.ps2", "only one"))
lone_spot = Path(lonely["at"])
# Move it to a day of its own, which is what an older evening looks like once
# the others have been cleared out.
own_day = lone_spot.parent.parent / "2026-01-05"
own_day.mkdir(parents=True, exist_ok=True)
moved = own_day / lone_spot.name
lone_spot.rename(moved)
history.remove(moved)
check("the session goes", moved.exists(), False)
check("...and the empty day with it", own_day.exists(), False)

print("\nand what it will not delete")
for _bad, _why in ((str(_box), "somewhere outside the history"),
                   ("", "nothing at all"),
                   (str(history.where() / "PCSX2"), "a whole emulator"),
                   (str(day_of), "a whole day")):
    try:
        history.remove(_bad)
        check(f"it refuses {_why}", "allowed", "refused")
    except history.Refused:
        check(f"it refuses {_why}", "refused", "refused")
check("...and the day it refused is still there", day_of.is_dir(), True)


print("\nwhich computer an evening happened on")
# Somebody plays the same game on two machines. Once the saves are synced,
# both sessions sit in the same list and nothing distinguishes them - which
# matters most at the moment of pressing Restore.
#
# Recorded when the snapshot is taken, not when it is synced: a machine
# receiving a session only knows it came out of the shared folder and cannot
# know from where. Marked at the source, the answer travels with it.
age_everything()
here_now = played((CARDS / "Local.ps2", "played on this machine"))
mine_spot = Path(here_now["at"])
check("a session made here knows which machine that was",
      bool(history.made_on(mine_spot).get("id")), True)
check("...and is not marked as being from anywhere else",
      history.elsewhere(mine_spot), "")

# The same session as it would arrive from another computer: the sidecar
# carries that machine's id, which is not this one's.
import json as _json                                          # noqa: E402
history.device_path(mine_spot).write_text(
    _json.dumps({"id": "not-this-machine", "name": "Laptop"}), encoding="utf-8")
check("one that came from elsewhere says whose it was",
      history.elsewhere(mine_spot), "Laptop")
check("...and the panel carries it",
      [s["from"] for sy in history.listing()["systems"]
       for d in sy["days"] for s in d["sessions"]
       if s["path"] == str(mine_spot)], ["Laptop"])

# A machine that has been renamed is still the same machine: the id decides.
mine_id = history.made_on(mine_spot)
history.device_path(mine_spot).write_text(
    _json.dumps({"id": sync.device()["id"], "name": "An Old Name"}),
    encoding="utf-8")
check("a renamed computer is still this one",
      history.elsewhere(mine_spot), "")

print("\nand a session from before any of this was recorded")
# No sidecar at all. Far likelier to be an old one of your own than a mystery
# from another machine, so it says nothing rather than guessing.
history.device_path(mine_spot).unlink()
check("says nothing rather than guessing", history.elsewhere(mine_spot), "")

print("\nand it is carried, kept and swept like the other sidecars")
history.device_path(mine_spot).write_text(
    _json.dumps({"id": "elsewhere", "name": "Laptop"}), encoding="utf-8")
check("a restore does not offer to put it back",
      any(f["to"].endswith(".device") for f in history.plan(mine_spot)["files"]),
      False)
history.remove(mine_spot)
check("deleting the session takes it too",
      history.device_path(mine_spot).exists(), False)


print("\nwhere a restore will not go")
# This path comes off the page, and everything after it is "walk that folder
# and copy it into the emulators' save directories". So it has to be a real
# snapshot inside the history and nothing else - the alternative is a request
# that copies any folder on the machine over somebody's memory cards.
#
# The blank case is not hypothetical: a malformed request produced exactly it,
# and Path("") is Path("."), which is a directory, so the walk went through
# the app's own install folder looking for saves to restore.
for _bad, _why in ((""             , "nothing at all"),
                   ("."            , "the working directory"),
                   (str(_box)      , "somewhere outside the history"),
                   (str(history.where() / "RetroArch"), "a whole emulator"),
                   (str(history.where() / "RetroArch" / "2026-01-01"),
                    "a whole day")):
    try:
        history.plan(_bad)
        check(f"refuses {_why}", "allowed", "refused")
    except history.Refused:
        check(f"refuses {_why}", "refused", "refused")

shutil.rmtree(_box, ignore_errors=True)
print(f"\n{ok} passed, {fail} failed")
sys.exit(1 if fail else 0)
