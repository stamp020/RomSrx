"""Arcade, where the filename is the whole of the identity.

The rest of this app matches a game by its title and then confirms it by
hashing the bytes. Neither works here. A MAME romset is named for the board -
`dkaccel.zip` is Donkey Kong Accelerate - so there is no title in the name to
match, and RetroAchievements never opens the file anyway.

What it does instead is hash the romset's short name, and that single fact is
what this suite exists to hold in place:

    md5("dkaccel") == 14f9690de97d3c7d4036a83df6df9964

which is the hash their own API returns for that set, checked against the live
site when this was written. Every arcade answer in the app is built on it, so
if the rule ever changes, it should fail here rather than quietly stop
matching five hundred games.

Nothing here touches the network.
"""
import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from romsrx import arcade, rahash  # noqa: E402

ok = fail = 0


def check(label, got, want):
    global ok, fail  # noqa: PLW0603
    if got == want:
        ok += 1
        print(f"  pass  {label}")
    else:
        fail += 1
        print(f"  FAIL  {label}\n          got  {got!r}\n          want {want!r}")


# -- the one rule everything else stands on ---------------------------------

print("\nthe number a romset is known by")
# Taken from RetroAchievements' own API_GetGameHashes for game 28363.
check("the short name, hashed",
      arcade.romset_hash("dkaccel.zip"), "14f9690de97d3c7d4036a83df6df9964")
check("...and the extension is not part of it",
      arcade.romset_hash("dkaccel"), arcade.romset_hash("dkaccel.zip"))
check("...nor is the .7z somebody repacked it as",
      arcade.romset_hash("dkaccel.7z"), arcade.romset_hash("dkaccel.zip"))

# Case is not folded, and must not be. MAME romset names are lowercase by
# convention and the hash of an uppercase one is a number the site has never
# heard of - quietly "fixing" the case would invent matches that do not exist.
check("case is left alone",
      arcade.romset_hash("DKACCEL.zip") != arcade.romset_hash("dkaccel.zip"),
      True)
check("nothing at all", arcade.romset_hash(""), "")
check("only an extension", arcade.romset_hash(".zip"), "")


# -- reading the shelf ------------------------------------------------------

print("\nfinding the board a set names")
shelf = {arcade.romset_hash(n): n.rsplit(".", 1)[0]
         for n in ("dkaccel.zip", "sf2ce.zip", "1941.zip")}

check("a set whose romset is on the shelf",
      arcade.match(shelf, [arcade.romset_hash("sf2ce")]), "sf2ce")
check("...whichever of its names matches",
      arcade.match(shelf, ["0" * 32, arcade.romset_hash("1941")]), "1941")

# There is no ladder to fall back on and there must not be: a romset the set
# does not name is a different board, and a different board does not load.
check("a set naming a board nobody has",
      arcade.match(shelf, [arcade.romset_hash("nosuchboard")]), "")
check("a set naming nothing at all", arcade.match(shelf, []), "")
check("an empty shelf", arcade.match({}, [arcade.romset_hash("sf2ce")]), "")


# -- and the app agrees that arcade can be checked --------------------------

print("\nwhat the rest of the app is told")
# This used to answer "no", which put arcade copies under the same "not
# checked" mark as a .chd nothing can open. The opposite is true: arcade is
# the one console whose copies are certain without reading a byte.
check("arcade has a hashing rule", rahash.scheme("Arcade"), "arcade")
check("...and is listed as checkable",
      "Arcade" in rahash.supported_consoles(), True)
check("...whatever the file is packed as",
      rahash.can_read("dkaccel.7z", "Arcade"), True)
check("the hash comes out of the name",
      rahash.compute("C:/anywhere/dkaccel.zip", "Arcade"),
      ("14f9690de97d3c7d4036a83df6df9964", ""))
# Deliberate: the file need not exist, and need not be readable. A romset that
# will not open is still the romset the set names, and saying "unreadable"
# about it would report a problem the site does not have.
check("...even for a file that is not there",
      rahash.compute("C:/nowhere/does-not-exist/sf2ce.zip", "Arcade")[0],
      arcade.romset_hash("sf2ce"))

print(f"\n{ok} passed, {fail} failed")
sys.exit(1 if fail else 0)
