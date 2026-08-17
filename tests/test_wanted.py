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
found = listed([
    game("~Hack~ Super Mario World Bros", ident=5),
    game("~Homebrew~ Slender: The 8 Pages", ident=6),
    game("~Translation~ Some Game", ident=7),
    game("Sly 2: Band of Thieves [Subset - Bonus]", ident=8),
])
for title in found:
    check(f"{title[:38]} needs the patcher", found[title]["state"], "patch")
check("...and none of them is offered a file",
      [g["file"] for g in found.values()], [None] * 4)

# -- a console this app does not index --------------------------------------

print("\nodds and ends")
found = listed([game("Some Arcade Thing", console_id=27, ident=9)])
row = found["Some Arcade Thing"]
check("a console with no id here is still listed", row["title"],
      "Some Arcade Thing")
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
