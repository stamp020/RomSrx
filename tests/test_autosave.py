"""Backing the saves up on their own: when, and how many are kept.

The feature exists because the manual backup was a button somebody had to
remember to press, and the thing it protects - a memory card with sixty hours
on it - is the one thing in this app that cannot be downloaded again.

What is pinned is the part that would be embarrassing to get wrong. It must
not run when it is off. It must not run twice in a day when it was asked for
weekly. It must keep three and no more, so it cannot quietly eat a disk. And
rotation must never delete a file this app did not write, because these live
in a folder somebody can open and put their own things in.

Nothing here touches the network; the saves are stood in for.
"""
import io
import shutil
import sys
import tempfile
import time
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from romsrx import autosave, saves  # noqa: E402

ok = fail = 0


def check(label, got, want):
    global ok, fail  # noqa: PLW0603
    if got == want:
        ok += 1
        print(f"  pass  {label}")
    else:
        fail += 1
        print(f"  FAIL  {label}\n          got  {got!r}\n          want {want!r}")


box = Path(tempfile.mkdtemp(prefix="autosave-"))
kept = box / "backups"

# The user's real folder is never touched: both ends of this are stood in for.
autosave.where = lambda: kept

# One save folder with a couple of files in it, in the shape saves.folders()
# hands over.
cards = box / "cards"
cards.mkdir(parents=True)
(cards / "Sonic.srm").write_bytes(b"save" * 200)
(cards / "Spyro.srm").write_bytes(b"save" * 300)
saves.folders = lambda settings=None: [{"label": "RetroArch", "path": str(cards)}]


def snapshots():
    return sorted(p.name for p in kept.iterdir()) if kept.exists() else []


print("off means off")
check("nothing is written when it is not asked for",
      autosave.run("off")["made"], False)
check("...nor for a setting that means nothing",
      autosave.run("banana")["made"], False)
check("...and nothing is on disk", snapshots(), [])

print("\nthe first one is always due")
first = autosave.run("weekly")
check("a snapshot is made", first["made"], True)
check("...with the save files in it", first["files"], 2)
check("...and it is a real zip",
      zipfile.is_zipfile(kept / first["newest"]), True)

print("\nand the second one is not")
again = autosave.run("weekly")
check("asking again the same day does nothing", again["made"], False)
check("...and says why", again["why"], "not due")
check("...leaving the one", len(snapshots()), 1)

print("\nunless it is asked for outright")
forced = autosave.run("off", force=True)
check("Back up now works even with the schedule off", forced["made"], True)
check("...and even when one was just taken", len(snapshots()), 2)

print("\nthree, and no more")
# Named for dates far enough apart that the rotation has an order to work in.
for day in ("2020-01-01-0100", "2020-01-02-0100", "2020-01-03-0100"):
    (kept / f"romsrx-saves-{day}.zip").write_bytes(b"PK\x03\x04old")
mine = box / "cards" / "x"
theirs = kept / "my own notes.zip"
theirs.write_bytes(b"PK\x03\x04not ours")

autosave.run("off", force=True)
left = snapshots()
check("only three of ours survive",
      len([n for n in left if n.startswith("romsrx-saves-")]), 3)
check("...the newest three", all(not n.endswith("2020-01-01-0100.zip")
                                for n in left), True)
check("a file this app did not write is left alone", theirs.exists(), True)

print("\nnothing to back up is not a failure")
saves.folders = lambda settings=None: []
none = autosave.run("off", force=True)
check("it says so rather than writing an empty zip", none["made"], False)
check("...and it is not an error", none["ok"], True)
check("...naming the reason", none["why"], "no saves found")

print("\nwhat the settings panel is told")
saves.folders = lambda settings=None: [{"label": "RetroArch", "path": str(cards)}]
now = autosave.status()
check("it counts what is there", now["count"], 3)
check("...and adds up their size", now["bytes"] > 0, True)
check("...and says where they are", now["folder"], str(kept))

print("\nwhen one is due")
day = 86400
check("never run is due", autosave._due("weekly", 0), True)         # noqa: SLF001
check("an hour ago is not", autosave._due("weekly",                  # noqa: SLF001
                                          time.time() - 3600), False)
check("eight days ago is", autosave._due("weekly",                   # noqa: SLF001
                                         time.time() - 8 * day), True)
check("...and daily after a day", autosave._due("daily",             # noqa: SLF001
                                                time.time() - day), True)
check("off is never due", autosave._due("off", 0), False)            # noqa: SLF001

shutil.rmtree(box, ignore_errors=True)
print(f"\n{ok} passed, {fail} failed")
sys.exit(1 if fail else 0)
