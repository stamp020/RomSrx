"""The right-click menu this app adds to the page window.

The window shows retroachievements.org, which is somebody else's site, and
until now it had no menu at all - pywebview turns the engine's own off unless
the app was started with debugging on. Turning it back on is one line and is
checked against a real window elsewhere; what is checked here is the part
with a decision in it, which is what the app adds underneath.

The rule that matters: a menu entry that offers to open a page must open that
page. Offering "Open in my browser" for a selection that turns out to be
three words, and quietly running a search instead, is worse than not offering
at all - so what counts as a URL is deliberately strict, and pinned here.

Nothing here needs WebView2; the entries are worked out from a plain object
with the same fields the engine hands over.
"""
import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from romsrx import webmenu  # noqa: E402

ok = fail = 0


def check(label, got, want):
    global ok, fail  # noqa: PLW0603
    if got == want:
        ok += 1
        print(f"  pass  {label}")
    else:
        fail += 1
        print(f"  FAIL  {label}\n          got  {got!r}\n          want {want!r}")


class Target:
    """What CoreWebView2ContextMenuTarget hands over, as far as this reads."""

    def __init__(self, link="", selection="", page="https://x.org/game/1"):
        self.LinkUri = link
        self.HasLinkUri = bool(link)
        self.SelectionText = selection
        self.HasSelection = bool(selection)
        self.PageUri = page


WORDS = webmenu._WORDS["en"]  # noqa: SLF001


def labels(**kw):
    return [label for label, _url in webmenu._entries(Target(**kw), WORDS)]  # noqa: SLF001


def urls(**kw):
    return [url for _label, url in webmenu._entries(Target(**kw), WORDS)]  # noqa: SLF001


# -- what counts as something to open ---------------------------------------

print("\na selection that is a link")
check("a full address", webmenu.looks_like_url("https://retroachievements.org/game/3"),
      "https://retroachievements.org/game/3")
check("a bare host, the way a page prints it",
      webmenu.looks_like_url("retroachievements.org/game/3"),
      "https://retroachievements.org/game/3")
check("surrounding space is not part of it",
      webmenu.looks_like_url("  example.org  "), "https://example.org")

print("\nand a selection that is not")
# Every one of these would have been opened as a web address by a looser
# rule, and every one of them is a thing somebody selects on a game's page.
check("a game's name", webmenu.looks_like_url("Sonic the Hedgehog 2"), "")
check("a filename", webmenu.looks_like_url("Sonic 2 (USA).zip"), "")
check("...even one with no spaces in it",
      webmenu.looks_like_url("Sonic_2_USA.zip"), "")
check("a sentence with a dot in it",
      webmenu.looks_like_url("Beat the game. Twice."), "")
check("a hash", webmenu.looks_like_url("d41d8cd98f00b204e9800998ecf8427e"), "")
check("a version number", webmenu.looks_like_url("1.0.3"), "")
check("nothing at all", webmenu.looks_like_url("   "), "")
# Not a web page, and handing it to the browser is handing over a local path.
check("a file:// address is not offered",
      webmenu.looks_like_url("file:///C:/Windows/win.ini"), "")

# -- what the menu ends up offering -----------------------------------------

print("\nthe entries added under the engine's own")
check("a plain right-click offers the page", labels(), [WORDS["page"]])
check("...pointing at the page", urls(), ["https://x.org/game/1"])

check("on a link, the link comes first",
      labels(link="https://ra.org/x"), [WORDS["link"], WORDS["page"]])

check("selected words become a search",
      labels(selection="Sonic the Hedgehog 2"),
      [WORDS["find"].format(what="Sonic the Hedgehog 2"), WORDS["page"]])
check("...and the search is for those words",
      urls(selection="Sonic the Hedgehog 2")[0],
      "https://duckduckgo.com/?q=Sonic%20the%20Hedgehog%202")

check("a selected address is offered as one",
      labels(selection="example.org/thing"), [WORDS["sel"], WORDS["page"]])

# Right-clicking a link usually selects nothing, but a link can also be
# inside a selection, and two entries opening the same address is clutter.
check("the same address is not offered twice",
      labels(link="https://ra.org/x", selection="https://ra.org/x"),
      [WORDS["link"], WORDS["page"]])

# A long selection has to stay a menu item rather than becoming a paragraph.
long_pick = "Collect every single one of the two hundred and forty stars"
shown = labels(selection=long_pick)[0]
check("a long selection is trimmed", len(shown) <= len(WORDS["find"]) + 44, True)
check("...and says it was trimmed", shown.endswith("…”"), True)
check("...while the search still gets all of it",
      urls(selection=long_pick)[0].endswith("stars"), True)

# The window also opens this app's own pages; offering to send those to a
# browser would be offering to open a link that only works in here.
print("\nand what it must not offer")
check("a page with no address of its own",
      labels(page=""), [])

print(f"\n{ok} passed, {fail} failed")
sys.exit(1 if fail else 0)
