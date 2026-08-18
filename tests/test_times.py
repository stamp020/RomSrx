"""Timing every set once, and never paying for it twice.

The scan is thousands of requests. What makes that acceptable is that it is
asked once and topped up afterwards, so the part worth pinning is the part
that decides what still needs asking: a set nobody has revised must never be
asked about again, and a set that *has* been revised must be.

The other thing pinned here is what happens when an answer does not arrive. A
game with no times is written down as asked - otherwise every scan for ever
re-asks the same hopeless games - but a refusal is not, because recording a
silence as an answer would lose that game's times permanently.

Nothing touches the network.
"""
import io
import json
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from romsrx import retro, times  # noqa: E402

ok = fail = 0


def check(label, got, want):
    global ok, fail  # noqa: PLW0603
    if got == want:
        ok += 1
        print(f"  pass  {label}")
    else:
        fail += 1
        print(f"  FAIL  {label}\n          got  {got!r}\n          want {want!r}")


box = Path(tempfile.mkdtemp(prefix="times-"))
times.STORE = box / "times.json"
times._store = {}                                          # noqa: SLF001
times.GAP = 0                                              # no waiting in tests

# What the site would say, per game.
answers: dict[int, dict] = {}
asked: list[int] = []


def fake_how_long(console, name, game=0):
    asked.append(int(game))
    return answers.get(int(game), {"ok": False, "reason": "unreachable"})


retro.how_long = fake_how_long

POOL = [
    {"id": 1, "title": "Short One", "norm": "short one", "console": "Game Boy",
     "achievements": 6, "points": 35, "modified": "2026-01-01 00:00:00"},
    {"id": 2, "title": "Long One", "norm": "long one", "console": "Game Boy",
     "achievements": 60, "points": 500, "modified": "2026-01-01 00:00:00"},
    {"id": 3, "title": "Nobody Finished", "norm": "nobody", "console": "Game Boy",
     "achievements": 12, "points": 90, "modified": "2026-01-01 00:00:00"},
    {"id": 4, "title": "Site Was Down", "norm": "down", "console": "Game Boy",
     "achievements": 20, "points": 150, "modified": "2026-01-01 00:00:00"},
]
answers[1] = {"ok": True, "beat": 600, "master": 1800, "players": 500}
answers[2] = {"ok": True, "beat": 7200, "master": 36000, "players": 900}
answers[3] = {"ok": False, "reason": "notimes"}
# 4 is left as "unreachable".

print("the first run")
asked.clear()
found = times.scan(POOL)
check("everything is asked about", sorted(asked), [1, 2, 3, 4])
check("...and counted", found["asked"], 4)
check("two have times", times.counts()["timed"], 2)
check("...out of four asked", times.counts()["asked"], 3)

print("\nwhat the second run has left to do")
asked.clear()
left = times.outstanding(POOL)
check("only the one that never answered", [r["id"] for r in left], [4])
times.scan(POOL)
check("...and only it is asked again", asked, [4])

print("\na set that has been revised")
revised = [dict(r) for r in POOL]
revised[0]["modified"] = "2026-06-01 12:00:00"
check("is outstanding again",
      [r["id"] for r in times.outstanding(revised)], [1, 4])
check("...while the untouched ones are not",
      2 in [r["id"] for r in times.outstanding(revised)], False)

print("\nthe order")
ranked = times.rank(POOL, "beat")
check("quickest first", [r["id"] for r in ranked], [1, 2])
check("a game with no time is left out rather than put last",
      3 in [r["id"] for r in ranked], False)
check("...and so is one that was never answered for",
      4 in [r["id"] for r in ranked], False)
check("mastering is its own order",
      [r["seconds"] for r in times.rank(POOL, "master")], [1800, 36000])
check("an unknown order falls back to beating",
      [r["id"] for r in times.rank(POOL, "nonsense")], [1, 2])

print("\nwhat survives the app closing")
times.save()
check("the file is written", times.STORE.is_file(), True)
saved = json.loads(times.STORE.read_text(encoding="utf-8"))
check("...holding what was learned", sorted(saved["times"]), ["1", "2", "3"])
times._store = None                                        # noqa: SLF001
check("...and it is read back", times.counts()["timed"], 2)

print("\nstopping partway")
times._store = {}                                          # noqa: SLF001
asked.clear()
after = [0]


def stop_after_two():
    after[0] += 1
    return after[0] > 2


times.scan(POOL, stop=stop_after_two)
check("a cancelled scan stops asking", len(asked), 2)
check("...and keeps what it had", times.counts()["asked"], 2)

shutil.rmtree(box, ignore_errors=True)
print(f"\n{ok} passed, {fail} failed")
sys.exit(1 if fail else 0)
