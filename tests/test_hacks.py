"""Reaching a fan hack by patching the game it was made from.

RetroAchievements has 1,241 sets on these consoles that are a hack or a
translation, and none of them is a file anybody hosts. Both halves of the
answer were already in the app - RetroAchievements publishes the patches, the
index has the base ROMs - and the fact that joins them is written in the
patch's own address:

    .../MD/Hacks/Sonic the Hedgehog 2/9043-Sonic2-AmyRose.zip

What is pinned here is the reading of that address and, far more importantly,
the refusals. Patching a hack onto the wrong base ROM does not fail loudly: it
produces a well-formed file of the wrong game, which the set then rejects for
reasons nobody can see. So a base game that cannot be identified must come
back as nothing at all, never as a guess.

Nothing here touches the network.
"""
import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from romsrx import hacks, retro  # noqa: E402

ok = fail = 0


def check(label, got, want):
    global ok, fail  # noqa: PLW0603
    if got == want:
        ok += 1
        print(f"  pass  {label}")
    else:
        fail += 1
        print(f"  FAIL  {label}\n          got  {got!r}\n          want {want!r}")


RAW = "https://github.com/RetroAchievements/RAPatches/raw/main"


def fold_of(*titles):
    """A console's folded-title map, as wanted._fold_one would build it."""
    table = {}
    for title in titles:
        for key in retro.match_keys(title):
            table.setdefault(key, retro.match_key(title))
    return table


# -- reading the base game off the address ----------------------------------

print("\nthe game a patch is a diff against")
check("the folder above the patch names it",
      hacks.base_name(f"{RAW}/MD/Hacks/Sonic%20the%20Hedgehog%202/9043-x.zip"),
      "Sonic the Hedgehog 2")
check("escaping is undone",
      hacks.base_name(f"{RAW}/N64/Hacks/Super%20Mario%2064/1-x.zip"),
      "Super Mario 64")

print("\nand the folders that are not a game")
# Each of these is the layer above - what kind of patch it is, not what it
# patches - and reading one as a title sends the matcher after a game called
# "Subset". Nine sets on the SNES alone were being blocked by exactly that.
for folder in ("Hacks", "Subset", "Translations", "Fix", "Homebrew"):
    check(f"{folder!r} is not a title",
          hacks.base_name(f"{RAW}/SNES/{folder}/123-x.zip"), "")
check("a path too short to hold one", hacks.base_name("x.zip"), "")
check("nothing at all", hacks.base_name(""), "")


# -- placing that game in the index -----------------------------------------

print("\nfinding the base ROM")
fold = fold_of("Sonic the Hedgehog", "Sonic the Hedgehog 2",
               "Super Mario World", "Super Mario World 2 - Yoshi's Island",
               "Pokemon FireRed Version", "Zelda II - The Adventure of Link")

check("a game named outright", hacks.find_base(fold, "Sonic the Hedgehog 2"),
      "sonic the hedgehog 2")
check("...and its neighbour is not it",
      hacks.find_base(fold, "Sonic the Hedgehog"), "sonic the hedgehog")
# The subtitle the repository leaves off and every dump carries.
check("a title that is the start of exactly one other",
      hacks.find_base(fold, "Zelda II"), "zelda ii the adventure of link")

print("\nand the ones it must refuse")
# The whole danger of the prefix rule in one line. 'Super Mario World' is the
# start of 'Super Mario World 2', and answering the longer one would apply a
# Mario World hack to Yoshi's Island - a file that builds cleanly and matches
# nothing. The exact spelling exists, so it wins before any prefix is tried.
check("a title that is also the start of a longer one",
      hacks.find_base(fold, "Super Mario World"), "super mario world")
check("a prefix that fits more than one is refused, not guessed",
      hacks.find_base(fold_of("Mega Man 2", "Mega Man 3"), "Mega Man"), "")
check("a name too short to be a safe prefix",
      hacks.find_base(fold, "Zelda"), "")
check("a game nothing in the index answers to",
      hacks.find_base(fold, "Some Game Nobody Has"), "")
check("an empty index answers nothing", hacks.find_base({}, "Sonic"), "")


# -- the aliases ------------------------------------------------------------

print("\nnames the repository writes differently")
# Every one of these was measured against the real index. The Turtles entry is
# here because guessing it went wrong: "Shredder's Re-Revenge" reads like a
# Turtles game and is a hack of Streets of Rage 2, and the guess would have
# patched it onto Hyperstone Heist.
check("an abbreviation", hacks.ALIASES["loz - ocarina of time"],
      "The Legend of Zelda - Ocarina of Time")
check("a hack named after a series it is not in",
      hacks.ALIASES["tmnt - shredder's re-revenge"], "Streets of Rage 2")
check("the alias is applied when reading the address",
      hacks.base_name(f"{RAW}/N64/Hacks/LoZ%20-%20Ocarina%20of%20Time/1-x.zip"),
      "The Legend of Zelda - Ocarina of Time")


# -- the whole plan ---------------------------------------------------------

print("\nwhat it takes to reach one set")
patches = {9043: [f"{RAW}/MD/Hacks/Sonic%20the%20Hedgehog%202/9043-x.zip"],
           99: [f"{RAW}/MD/Hacks/A%20Game%20Nobody%20Has/99-x.zip"],
           98: [f"{RAW}/MD/Hacks/123-loose.zip"]}

made = hacks.plan(fold, 9043, patches)
check("the patch", made.get("patch", "").endswith("9043-x.zip"), True)
check("...the game it goes on", made.get("base"), "Sonic the Hedgehog 2")
check("...and the copy to fetch", made.get("norm"), "sonic the hedgehog 2")

# All three or none. A plan with a hole in it would offer a download that
# cannot become the thing it was asked for, which is worse than saying no.
check("no patch published, no plan", hacks.plan(fold, 12345, patches), {})
check("no base ROM in the index, no plan", hacks.plan(fold, 99, patches), {})
check("no base game named, no plan", hacks.plan(fold, 98, patches), {})

# -- and the pool the whole-site orders rank --------------------------------
#
# A hack used to be thrown out of the rankings on the grounds that it is "a
# second set for a game rather than a game", and that reasoning covered two
# very different things. A subset really is a second board of achievements for
# a page that already exists. A hack is its own game with its own page, and it
# was only unrankable because nobody hosts the file - which is no longer true
# now that the base ROM and the patch can both be found.
#
# The same comment worried that hacks are "tiny by nature" and would fill the
# front of a list ordered by set size. Measured against the real catalogue
# they are 12.7% of the pool and 15-20% of its shortest thousand, and none of
# the forty shortest. The worry was reasonable and did not survive counting.

print("\nwhat the rankings may carry")

check("a hack with a patch and a base ROM is rankable",
      bool(hacks.plan(fold, 9043, patches)), True)

# A subset's patch, when it has one, is filed under a folder saying so - and
# that is what keeps subsets out without needing a rule of their own.
subset = {7: [f"{RAW}/SNES/Subset/7-something.zip"]}
check("a subset is not", hacks.plan(fold, 7, subset), {})

print(f"\n{ok} passed, {fail} failed")
sys.exit(1 if fail else 0)
