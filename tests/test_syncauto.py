"""Keeping two computers in step without anybody pressing anything.

The parts that matter are the two that were missing. A change made here has
to leave on its own - otherwise a playlist you make and then walk away from
never exists anywhere else - and something the other machine sent has to
arrive on its own, at a computer that is already open and has no reason to
look.

Both are about timing, so the clocks are wound down to fractions of a second
here rather than the minutes the app uses.
"""
import io
import json
import os
import shutil
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

_home = Path(tempfile.mkdtemp(prefix="romsrx-auto-home-"))
os.environ["APPDATA"] = str(_home)

from romsrx import state, sync, syncstore  # noqa: E402

ok = fail = 0


def check(label, got, want):
    global ok, fail  # noqa: PLW0603
    if got == want:
        ok += 1
        print(f"  pass  {label}")
    else:
        fail += 1
        print(f"  FAIL  {label}\n          got  {got!r}\n          want {want!r}")


def until(answer, seconds=6.0):
    """Wait for something to become true, and say whether it did."""
    end = time.monotonic() + seconds
    while time.monotonic() < end:
        if answer():
            return True
        time.sleep(0.05)
    return False


box = Path(tempfile.mkdtemp(prefix="romsrx-auto-"))
cloud = box / "OneDrive"
cloud.mkdir()

# Minutes are right in the app and useless in a test.
syncstore.QUIET = 0.2
syncstore.EVERY = 0.4

state.set_prefs({"syncKind": "folder", "syncFolder": str(cloud),
                 "syncDeviceName": "Desktop", "syncAuto": True,
                 "syncParts": ["playlists"]})

far = cloud / sync.ROOT / "app" / "playlists.json"


print("a playlist made here, and nobody pressing anything")
syncstore.start("the app opened")
state.set_playlists([{"id": "a", "name": "Weekend games", "created": 1,
                      "items": []}])
syncstore.nudge("a playlist changed")
check("it reaches the cloud on its own", until(lambda: far.is_file()), True)
check("...with what was written", "Weekend games" in
      far.read_text(encoding="utf-8"), True)


print("\nand the other computer sends something back")
# Written straight into the store, the way the other machine would have left
# it. Nothing here asks for it: the only thing that can bring it over is the
# few-minute look, which is the whole point of that look existing.
far.write_text(json.dumps([{"id": "b", "name": "From the laptop",
                            "created": 2, "items": []}]), encoding="utf-8")
check("it arrives without being asked for",
      until(lambda: any(p.get("name") == "From the laptop"
                        for p in state.playlists()), seconds=8.0), True)


print("\nand a burst of changes is not a burst of syncs")
syncstore.QUIET = 3.0                      # long enough to hold them together
syncstore._last_auto = time.monotonic()    # noqa: SLF001 - one has just run
before = syncstore._last_auto_at           # noqa: SLF001
for n in range(5):
    state.set_playlists([{"id": "a", "name": f"Change {n}", "created": 1,
                          "items": []}])
    syncstore.nudge("a playlist changed")
check("none of them goes straight out",
      syncstore._last_auto_at, before)     # noqa: SLF001
check("...and then one does",
      until(lambda: syncstore._last_auto_at > before,  # noqa: SLF001
            seconds=8.0), True)
check("...carrying the last of them",
      "Change 4" in far.read_text(encoding="utf-8"), True)


print("\nand with the tickbox off it stays off")
syncstore.QUIET = 0.2
state.set_prefs({"syncAuto": False})
far.write_text(json.dumps([{"id": "c", "name": "Should not arrive",
                            "created": 3, "items": []}]), encoding="utf-8")
check("nothing is fetched", until(
    lambda: any(p.get("name") == "Should not arrive"
                for p in state.playlists()), seconds=2.0), False)
check("...and it says why", syncstore.auto()["why"], "not asked for")


print("\nand a nudge before anything is set up is not a crash")
state.set_prefs({"syncAuto": True, "syncKind": ""})
syncstore.nudge("nothing is set up")
check("it reports rather than raises", syncstore.auto().get("ok"), False)


shutil.rmtree(box, ignore_errors=True)
shutil.rmtree(_home, ignore_errors=True)
print(f"\n{ok} passed, {fail} failed")
sys.exit(1 if fail else 0)
