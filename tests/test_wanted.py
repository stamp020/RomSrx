"""Joining the Want to Play list to the index.

Two sides that name the same games differently, which is the whole difficulty.
RetroAchievements writes what is on the box - "The Legend of Spyro: A New
Beginning" - and a preservation set writes "Legend of Spyro, The - A New
Beginning (USA).iso". Neither is wrong and no amount of exact matching will
ever join them, so both are folded through retro.match_keys() and compared in
that form. Measured against a real list of 78 while this was written: folding
one side matched 55, folding both matched 61, and the full ladder - the studio
in front, the numerals, the spacing - matched 70.

What is pinned here is that folding, the four states a row can be in, and the
one thing that has no second chance: which copy gets picked when the app picks
for you. A demo offered as the game is the failure that matters, because
nobody reads the filename before pressing Download.

Nothing touches the network - the list is stood in for.
"""
import io
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from romsrx import artwork, db, wanted  # noqa: E402

ok = fail = 0


def check(label, got, want):
    global ok, fail  # noqa: PLW0603
    if got == want:
        ok += 1
        print(f"  pass  {label}")
    else:
        fail += 1
        print(f"  FAIL  {label}\n          got  {got!r}\n          want {want!r}")


# -- an index with a few games in it ---------------------------------------

box = Path(tempfile.mkdtemp(prefix="wanted-"))
conn = db.connect(box / "test.db")
conn.execute(
    "INSERT INTO sources (id, console, name, identifier, url, console_rank)"
    " VALUES ('ps2', 'PlayStation 2', 'Test Set', 'test_set',"
    " 'https://example.invalid/test_set', 0)")


def add(filename, console, title, norm, tags="", regions="USA", size=100):
    conn.execute(
        "INSERT INTO files (source_id, console, path, filename, title,"
        " title_norm, regions, languages, version, disc, tags, ext, size, url)"
        " VALUES ('ps2', ?, ?, ?, ?, ?, ?, '', '', '', ?, 'iso', ?, ?)",
        (console, filename, filename, title, norm, regions, tags, size,
         f"https://example.invalid/{filename}"))


# The article No-Intro parks in the middle, which is the commonest mismatch.
add("Legend of Spyro, The - A New Beginning (USA).iso", "PlayStation 2",
    "Legend of Spyro, The - A New Beginning", "legend of spyro the a new beginning")
# The studio in front, which RetroAchievements leaves off.
add("DreamWorks Madagascar (USA).iso", "PlayStation 2",
    "DreamWorks Madagascar", "dreamworks madagascar")
# A game with a demo beside it - the copy that must not be chosen.
add("Sly 2 - Band of Thieves (USA) (Demo 1).iso", "PlayStation 2",
    "Sly 2 - Band of Thieves", "sly 2 band of thieves", tags="Demo 1")
add("Sly 2 - Band of Thieves (Europe).iso", "PlayStation 2",
    "Sly 2 - Band of Thieves", "sly 2 band of thieves", regions="Europe")
add("Sly 2 - Band of Thieves (USA).iso", "PlayStation 2",
    "Sly 2 - Band of Thieves", "sly 2 band of thieves")
conn.commit()

artwork.settings = lambda: {"retroachievements":
                            {"api_key": "xyz", "username": "someone"}}


def listed(rows):
    wanted._cache = None                                   # noqa: SLF001
    wanted._fetch = lambda key, who: rows                  # noqa: SLF001
    return {g["title"]: g for g in wanted.listing(conn)["games"]}


def game(title, console_id=21, ident=1, **extra):
    return {"ID": ident, "Title": title, "ConsoleID": console_id,
            "ConsoleName": "PlayStation 2", "PointsTotal": 400,
            "AchievementsPublished": 40, **extra}


# -- the folding ------------------------------------------------------------

print("matching their titles to the index")
found = listed([
    game("The Legend of Spyro: A New Beginning", ident=1),
    game("Madagascar", ident=2),
    game("Sly 2: Band of Thieves", ident=3),
    game("A Game Nobody Indexed", ident=4),
])
check("the article moved to the middle still matches",
      found["The Legend of Spyro: A New Beginning"]["state"], "get")
check("the studio in front is seen past",
      found["Madagascar"]["state"], "get")
check("...and it finds the right file",
      found["Madagascar"]["file"]["filename"], "DreamWorks Madagascar (USA).iso")
check("a colon against a dash matches",
      found["Sly 2: Band of Thieves"]["state"], "get")
check("a game no source carries says so",
      found["A Game Nobody Indexed"]["state"], "none")
check("...and offers no file to download",
      found["A Game Nobody Indexed"]["file"], None)

# -- the spellings the ladder is allowed to try -----------------------------
#
# Every rung is a lossier spelling than the one above it, and the danger is
# always the same: a spelling loose enough to join two names is loose enough
# to join two games. Both of the pairs below were produced by rules that
# looked obviously safe while being written.

print("\nspellings that mean the same game")
from romsrx import retro  # noqa: E402


def joins(a, b):
    """Would these two titles meet anywhere on the ladder?"""
    return bool(set(retro.match_keys(a)) & set(retro.match_keys(b)))


# Romaji written long or short. Twenty-odd sets were unreachable over this.
check("Daimao is Daimaou",
      joins("Dragon Ball: Daimao Fukkatsu",
            "Dragon Ball - Daimaou Fukkatsu (Japan)"), True)
check("Cho is Chou", joins("Cho Aniki", "Chou Aniki (Japan)"), True)
check("Genso is Gensou",
      joins("Genso Suikoden Card Stories",
            "Gensou Suikoden - Card Stories (Japan)"), True)
check("Onee is One",
      joins("OneeChanbara Special", "OneChanbara Special (Japan)"), True)

# The word that joins two names, which one set writes and the other does not.
check("'and' between two names may go",
      joins("Battletoads and Double Dragon: The Ultimate Team",
            "Battletoads Double Dragon - The Ultimate Team (USA)"), True)
check("...and an ampersand is the same word",
      joins("The Legend of Zelda: Ocarina of Time - Master Quest",
            "Legend of Zelda, The - Ocarina of Time & Master Quest (USA)"), True)

check("a volume number is a number",
      joins("Famicom Mini Vol. 21: Super Mario Bros. 2",
            "Famicom Mini 21 - Super Mario Bros. 2 (Japan)"), True)

# What kind of release it is, said before what the game is. No dump is named
# that way, so these reached nothing at all until the tags came off.
check("a homebrew is its own game",
      joins("~Homebrew~ ~Demo~ 2048", "2048 (World) (Demo) (Aftermarket)"),
      True)
check("an unlicensed cartridge is a cartridge",
      joins("~Unlicensed~ Cheetahmen II", "Cheetahmen II (USA) (Unl)"), True)
check("a prototype is a dump",
      joins("~Prototype~ Mario Kart XXL", "Mario Kart XXL (Europe)"), True)

# The tags come off last, and that ordering is the whole safety of it: a hack
# undressed is named after the game it was carved out of. The full spelling
# has to be offered - and missed - before the bare one is tried at all.
keys = retro.match_keys("~Hack~ Super Mario Bros. 3")
check("the tagged spelling is offered first",
      keys[0], retro.match_key("~Hack~ Super Mario Bros. 3"))
check("...and the game it was made from only after that",
      keys.index(retro.match_key("Super Mario Bros. 3")) > 0, True)
check("an untagged title gains nothing it did not already have",
      retro.match_keys("Super Mario Bros. 3"),
      retro._ladder("Super Mario Bros. 3"))  # noqa: SLF001

# Four more ways the same game gets written down, found by asking which sets
# the index plainly has and does not match, and then reading what the pairs
# had in common rather than guessing.

print("\ntwo catalogues, one game, different spellings")

# The article, wherever it sits. No-Intro parks it after the part it belongs
# to and that was already handled; this is the one in the middle, and the one
# hiding behind a publisher's name. Both at once, in the reported case.
check("an article in the middle",
      joins("The SpongeBob SquarePants Movie",
            "SpongeBob SquarePants - The Movie"), True)
check("...and behind the studio's name",
      joins("The SpongeBob SquarePants Movie",
            "Nickelodeon The SpongeBob SquarePants Movie"), True)

# RetroAchievements writes both of a game's names either side of a bar. 97
# sets are written that way, and a dump carries one name or the other.
check("a title carrying its other name",
      joins("Marko | Marko's Magic Football", "Marko's Magic Football (Europe)"),
      True)
check("...either side of the bar",
      joins("Druaga no Tou | The Tower of Druaga", "Tower of Druaga, The (Japan)"),
      True)

# Somebody's dump named with underscores because they could not use spaces.
check("underscores are spaces",
      joins("Sonic Adventure Tournament Disk",
            "sonic_adventure_tournament_disk"), True)

# Main title first or subtitle first - both catalogues do both.
check("a subtitle written first",
      joins("Golgo 13: The Mafat Conspiracy",
            "Mafat Conspiracy - Golgo 13 (USA)"), True)
check("...and a number that moved with it",
      joins("FIFA 98: Road to World Cup", "FIFA - Road to World Cup 98 (USA)"),
      True)
check("...and a Japanese name the other way round",
      joins("Private Idol Disc Vol. 1: Kinoshita Yuu",
            "Private Idol Disc Vol. 1 - Yuu Kinoshita (Japan)"), True)


print("\nthe same words, put in a different order")
# The danger in the rule above, and why numbers are held in place while the
# words move. These are different discs whose entire identity is which number
# comes first; sorting every word merged them, and they were found by counting
# the collisions the rule would cause before it was turned on.
check("two demo discs are not one",
      joins("Euro Demo 01/02", "Euro Demo 02/01"), False)
check("nor are two volumes of the same series",
      joins("PlayStation Underground 3.4", "PlayStation Underground 4.3"), False)
check("a sequel is not its predecessor rearranged",
      joins("Final Fantasy Legend II", "Final Fantasy Legend III"), False)

print("\nand spellings that must never meet")
# In ASCII a Roman numeral is a run of the same vowel. Collapsing those turns
# III into I, and the download succeeds, and it is the wrong game.
check("Dragon Quest III is not Dragon Quest I",
      joins("Dragon Quest III", "Dragon Quest I (Japan)"), False)
check("...nor Dragon Quest II",
      joins("Dragon Quest III", "Dragon Quest II (Japan)"), False)
check("Final Fantasy VIII is not Final Fantasy VI",
      joins("Final Fantasy VIII", "Final Fantasy VI (Japan)"), False)
# Dropping the joiner and then closing the spaces makes "I & II" into "III".
check("Dragon Quest I & II is not Dragon Quest III",
      joins("Dragon Quest I & II", "Dragon Quest III (Japan)"), False)
check("two numbered games stay apart",
      joins("Bloody Roar 3", "Bloody Roar 4 (USA)"), False)
check("a subtitle is not a game",
      joins("Fire Emblem: The Blazing Blade",
            "Fire Emblem - The Binding Blade (Japan)"), False)


# -- picking the copy -------------------------------------------------------

print("\nchoosing which copy")
check("a demo is never the copy offered",
      found["Sly 2: Band of Thieves"]["file"]["filename"],
      "Sly 2 - Band of Thieves (USA).iso")
check("...and the region order decides between the rest",
      "USA" in found["Sly 2: Band of Thieves"]["file"]["regions"], True)

# The demo tags are numbered - 'Demo 1', not 'Demo' - which is exactly how a
# demo came to be offered as the game the first time this was written.
check("a numbered demo tag is still a demo",
      "Demo" in found["Sly 2: Band of Thieves"]["file"]["tags"], False)

# -- what cannot be downloaded at all ---------------------------------------

print("\nthe ones that are not releases")
# The line is not "unusual release" but "there is no file to fetch". A hack
# and a translation are a diff over somebody else's ROM, and a subset is a
# second board of achievements for a page that already exists.
found = listed([
    game("~Hack~ Super Mario World Bros", ident=5),
    game("~Translation~ Some Game", ident=7),
    game("Sly 2: Band of Thieves [Subset - Bonus]", ident=8),
])
for title in found:
    check(f"{title[:38]} needs the patcher", found[title]["state"], "patch")
check("...and none of them is offered a file",
      [g["file"] for g in found.values()], [None] * 3)

# ...and the ones that are. A homebrew, an unlicensed cartridge, a prototype
# and a demo are standalone dumps, and MiNERVA keeps a shelf per console for
# exactly them. All four counted as patches until somebody counted them:
# 1,199 sets thrown away before anything went looking.
print("\nthe ones that are releases, tag or no tag")
found = listed([
    game("~Homebrew~ Slender: The 8 Pages", ident=6),
    game("~Unlicensed~ Some Cart", ident=9),
    game("~Prototype~ Some Build", ident=10),
    game("~Homebrew~ ~Demo~ Some Toy", ident=11),
])
for title in found:
    check(f"{title[:38]} is a game to download", found[title]["state"], "none")

# -- a console this app does not index --------------------------------------

print("\nodds and ends")
# Whichever console this app has no shelf for, worked out rather than written
# down. It used to say 27, which was Arcade, and Arcade stopped being an
# example the day it gained a shelf - the check went on passing for a while
# and then failed for a reason that had nothing to do with what it was for.
UNKNOWN_CONSOLE = next(n for n in range(1, 200)
                       if n not in set(retro.CONSOLES.values()))
found = listed([game("Some Machine We Skip", console_id=UNKNOWN_CONSOLE,
                     ident=9)])
row = found["Some Machine We Skip"]
check("a console with no id here is still listed", row["title"],
      "Some Machine We Skip")
check("...with nothing to fetch", row["state"], "none")
check("...and no console of ours", row["console"], "")

found = listed([game("Madagascar", ident=2)])
row = found["Madagascar"]
check("the row carries what the set is worth", row["points"], 400)
check("...and how many achievements", row["achievements"], 40)
check("...and a link to their page",
      row["url"], "https://retroachievements.org/game/2")

wanted._cache = None                                       # noqa: SLF001
wanted._fetch = lambda key, who: None                      # noqa: SLF001
check("an unreachable site is a reason, not a crash",
      wanted.listing(conn), {"ok": False, "reason": "unreachable"})

artwork.settings = lambda: {"retroachievements": {"api_key": "", "username": ""}}
wanted._cache = None                                       # noqa: SLF001
check("and without a username there is no list",
      wanted.listing(conn), {"ok": False, "reason": "nouser"})

# -- the copy that would have worked ----------------------------------------
# The other half of a failed compatibility check. Matched on the dump's name
# and nothing looser: the extension comes off, because the two sides wrap the
# same dump differently, and everything that tells two dumps apart - the
# region above all - still has to agree. Handing somebody the European copy
# when the set is dumped from the American one fails in exactly the way the
# check was built to prevent.

print("\nfinding a copy that works")
add("Sonic the Hedgehog (USA, Europe).zip", "PlayStation 2",
    "Sonic the Hedgehog", "sonic the hedgehog")
add("Sonic the Hedgehog (Japan).zip", "PlayStation 2",
    "Sonic the Hedgehog", "sonic the hedgehog", regions="Japan")
conn.commit()

from romsrx import retro  # noqa: E402

retro.hashes = lambda game: {
    1: [{"name": "Sonic The Hedgehog (USA, Europe).md", "md5": "aa",
         "labels": ["nointro"], "patch": ""}],
    2: [{"name": "Sonic The Hedgehog (Brazil).md", "md5": "bb",
         "labels": [], "patch": ""}],
    3: [{"name": "Sonic The Hedgehog (USA, Europe).md", "md5": "cc",
         "labels": [], "patch": "https://example.invalid/p.zip"}],
}.get(int(game), [])

found = wanted.replacement(conn, "PlayStation 2", "Sonic the Hedgehog", 1)
check("the accepted dump is found in the index", found["ok"], True)
check("...and it is the right region",
      found["files"][0]["filename"], "Sonic the Hedgehog (USA, Europe).zip")
check("...named as the set spells it",
      found["files"][0]["matched"], "Sonic The Hedgehog (USA, Europe).md")
check("...and only the one that matched", len(found["files"]), 1)

check("a set dumped from a copy nobody indexes finds nothing",
      wanted.replacement(conn, "PlayStation 2", "Sonic the Hedgehog", 2)["ok"],
      False)
check("a dump that is itself a patch is not offered as a download",
      wanted.replacement(conn, "PlayStation 2", "Sonic the Hedgehog", 3),
      {"ok": False, "reason": "nohashes"})

retro.hashes = lambda game: []
check("no hash list is a reason, not a crash",
      wanted.replacement(conn, "PlayStation 2", "Sonic the Hedgehog", 1),
      {"ok": False, "reason": "nohashes"})

conn.close()
print(f"\n{ok} passed, {fail} failed")
sys.exit(1 if fail else 0)
