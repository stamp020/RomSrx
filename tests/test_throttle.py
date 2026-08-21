"""The speed ceiling, and getting out of the way of a game.

Two things a download manager owes the rest of the machine. Neither existed:
downloads ran as fast as archive.org would serve them, and a 6GB disc image
arriving in the background is felt by anything else using the line.

What is pinned here is that the ceiling is a ceiling on the app rather than on
each transfer - three workers politely staying under 500 KB/s each is 1.5 MB/s
on the wire, which is not what anybody asked for - that it is shared without
the workers queueing behind one another, and that a bad number in the settings
turns the limit off rather than making downloads impossibly slow.

And that a running game stops the chunks, which is the one thing this app can
do that a general-purpose downloader cannot: it launched the game, so it knows.

Nothing here touches the network or writes a file - the bucket is asked for
room and timed.
"""
import io
import sys
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from romsrx import downloads  # noqa: E402

ok = fail = 0


def check(label, got, want):
    global ok, fail  # noqa: PLW0603
    if got == want:
        ok += 1
        print(f"  pass  {label}")
    else:
        fail += 1
        print(f"  FAIL  {label}\n          got  {got!r}\n          want {want!r}")


print("a number that cannot be used is no limit at all")
for value, want in ((None, 0), ("", 0), (0, 0), (-9, 0), ("nonsense", 0),
                    ([], 0), (10, 32), (32, 32), (500, 500), ("750", 750),
                    (10 ** 9, 1_000_000)):
    check(f"{value!r} -> {want}", downloads._sane_speed(value), want)  # noqa: SLF001


# -- the bucket ------------------------------------------------------------
#
# load_settings reads a file on disk, which is the user's real one; it is
# stood in for so this suite neither reads nor changes it.
class Job:
    id = 1


real_settings = downloads.load_settings
manager = downloads.Manager()


def settings_of(**over):
    base = {"speed_limit": 0, "pause_while_playing": False}
    base.update(over)
    return lambda: base


def spend(kb: int, chunk: int = 64 * 1024) -> float:
    """How long it takes to get permission for `kb` kilobytes."""
    manager._tokens, manager._filled = 0.0, 0.0  # noqa: SLF001
    left, start = kb * 1024, time.monotonic()
    while left > 0:
        take = min(chunk, left)
        manager._wait_for_room(take, Job())      # noqa: SLF001
        left -= take
    return time.monotonic() - start


print("\nthe ceiling")
downloads.load_settings = settings_of(speed_limit=0)
check("no limit is not slow", spend(4096) < 0.25, True)

downloads.load_settings = settings_of(speed_limit=512)
# The bucket starts full, so the first 512 KB is free and the next second
# buys the second 512 KB. 1 MB should therefore take about a second.
spent = spend(1024)
check("512 KB/s paces a megabyte to about a second", 0.7 < spent < 1.9, True)

print("\nand it is one ceiling, not one each")
downloads.load_settings = settings_of(speed_limit=512)
manager._tokens, manager._filled = 0.0, 0.0      # noqa: SLF001
times = []


def worker():
    start = time.monotonic()
    for _ in range(8):                            # 512 KB each
        manager._wait_for_room(64 * 1024, Job())  # noqa: SLF001
    times.append(time.monotonic() - start)


threads = [threading.Thread(target=worker) for _ in range(3)]
begin = time.monotonic()
for one in threads:
    one.start()
for one in threads:
    one.join()
together = time.monotonic() - begin
# Three workers, 1.5 MB between them, at 512 KB/s with a full bucket to start:
# about two seconds. Were the ceiling per worker it would be under one.
check("three workers share the limit rather than each getting it",
      1.2 < together < 3.5, True)

print("\nout of the way of a game")
playing = {"yes": True}
import romsrx.library as library  # noqa: E402

real_playing = library.playing_now
library.playing_now = lambda: playing["yes"]
downloads.load_settings = settings_of(pause_while_playing=True)

held = {"done": False}


def hold():
    manager._wait_for_room(1024, Job())          # noqa: SLF001
    held["done"] = True


thread = threading.Thread(target=hold, daemon=True)
thread.start()
time.sleep(1.4)
check("a chunk waits while a game is running", held["done"], False)
playing["yes"] = False
thread.join(timeout=4)
check("...and goes as soon as the game is closed", held["done"], True)

# Turned off, a running game is none of the downloader's business.
playing["yes"] = True
downloads.load_settings = settings_of(pause_while_playing=False)
start = time.monotonic()
manager._wait_for_room(1024, Job())              # noqa: SLF001
check("...unless the setting is off", time.monotonic() - start < 0.3, True)

library.playing_now = real_playing
downloads.load_settings = real_settings
print(f"\n{ok} passed, {fail} failed")
sys.exit(1 if fail else 0)
