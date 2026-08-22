"""Closing the window that opened alongside a game, when the game closes.

Opening an achievement list beside a game is a convenience; leaving it on
screen afterwards turns it into one more thing to tidy up, which is the
opposite. So the emulator exiting closes it again.

The line that matters is which windows count. A page somebody went and found
themselves is theirs, and closing it for them would be taking something away -
so only the ones this app opened on the way into a game are tracked, and only
those are closed.

Nothing here opens a real window: `browse` is handed a factory, which is
exactly what the app hands it, and a stand-in that records being destroyed is
enough to see what got closed.
"""
import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from romsrx import browse  # noqa: E402

ok = fail = 0


def check(label, got, want):
    global ok, fail  # noqa: PLW0603
    if got == want:
        ok += 1
        print(f"  pass  {label}")
    else:
        fail += 1
        print(f"  FAIL  {label}\n          got  {got!r}\n          want {want!r}")


class Pretend:
    """A window, as far as this module is concerned: something to destroy."""

    def __init__(self, url):
        self.url = url
        self.gone = False

    def destroy(self):
        self.gone = True


made = []


def factory(url, title):
    made.append(Pretend(url))
    return made[-1]


browse.set_window_opener(factory)

print("a window opened because a game started")
browse.open_window("https://retroachievements.org/game/1", "Sonic",
                   beside=True)
check("it opens", len(made), 1)
check("...and closing time takes it", browse.close_beside(), 1)
check("...and it really went", made[0].gone, True)


print("\nand one the reader opened themselves")
made.clear()
browse.open_window("https://retroachievements.org/user/somebody", "Somebody")
check("it opens too", len(made), 1)
# The whole point. Somebody reading a forum thread beside their game does not
# expect it to vanish when they quit - they went and found that page.
check("...but closing time leaves it alone", browse.close_beside(), 0)
check("...and it is still there", made[0].gone, False)


print("\ntwo games at once")
made.clear()
browse.open_window("https://retroachievements.org/game/1", "Sonic", beside=True)
browse.open_window("https://retroachievements.org/game/2", "Spyro", beside=True)
check("both are remembered", browse.close_beside(), 2)
check("...and both went", [w.gone for w in made], [True, True])


print("\nclosing twice")
made.clear()
browse.open_window("https://retroachievements.org/game/1", "Sonic", beside=True)
browse.close_beside()
# The second emulator to exit must not find the first one's window still
# listed and try to destroy it again.
check("the second time there is nothing left", browse.close_beside(), 0)


print("\na window already closed by hand")
made.clear()


class Awkward(Pretend):
    def destroy(self):
        raise RuntimeError("this window is already gone")


stubborn = Awkward("https://retroachievements.org/game/9")
browse.set_window_opener(lambda url, title: stubborn)
browse.open_window("https://retroachievements.org/game/9", "Gone", beside=True)
# Already closed is the wanted state, not a failure - and it must not stop
# whatever else is on the list from being closed.
try:
    check("it is not counted as closed", browse.close_beside(), 0)
except RuntimeError as exc:
    check("it is not counted as closed", f"raised {exc!r}", "no error")


print("\nwith no window system at all")
# `serve` in a browser: there is no window factory, so there is nothing to
# open and nothing to close.
browse.set_window_opener(None)
check("nothing opens",
      browse.open_window("https://retroachievements.org/game/1", "Sonic",
                         beside=True), False)
check("...and nothing is waiting to be closed", browse.close_beside(), 0)

print(f"\n{ok} passed, {fail} failed")
sys.exit(1 if fail else 0)
