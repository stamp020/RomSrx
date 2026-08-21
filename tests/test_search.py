"""What a search finds when the words are not quite the words in the title.

Three ways a query misses a game it obviously meant, each with its own answer
in db._plan:

* the apostrophe - "There's Nothing to Do in This Town" is indexed as
  'there s nothing ...', so nobody typing 'theres' ever found it;
* one word wrong - 'jarry potter' matched nothing at all, though 'potter' on
  its own would have found every one of them;
* the file's own vocabulary on the end - 'harry potter usa', 'sonic.iso'.

Built on a small index of its own rather than the real one, so the answers are
the same on any machine and nothing here touches the network.
"""
import io
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from romsrx import db, names  # noqa: E402

ok = fail = 0


def check(label, got, want):
    global ok, fail  # noqa: PLW0603
    if got == want:
        ok += 1
        print(f"  pass  {label}")
    else:
        fail += 1
        print(f"  FAIL  {label}\n          got  {got!r}\n          want {want!r}")


# -- a small index -------------------------------------------------------
GAMES = [
    ("SNES/Super Famicom", "There's Nothing to Do in This Town (USA).sfc"),
    ("Nintendo DS", "Theresia - Dear Emile (USA).nds"),
    ("Game Boy Advance", "Harry Potter and the Chamber of Secrets (USA).gba"),
    ("Game Boy Advance", "Harry Potter and the Goblet of Fire (Europe).gba"),
    ("PlayStation 2", "Harry Potter and the Prisoner of Azkaban (USA).iso"),
    ("SNES/Super Famicom", "Super Mario World (USA).sfc"),
    ("Nintendo 64", "Super Mario 64 (USA).z64"),
    ("Genesis/Mega Drive", "Sonic The Hedgehog (USA, Europe).md"),
    ("PlayStation", "Final Fantasy VII (USA) (Disc 1).cue"),
]

root = Path(tempfile.mkdtemp(prefix="romsrx-search-"))
conn = db.connect(root / "test.db")
conn.execute("INSERT INTO sources (id, console, name, identifier, url) "
             "VALUES ('s1', 'Various', 'Test Source', 'test', 'http://x')")
for number, (console, filename) in enumerate(GAMES, start=1):
    parsed = names.parse(filename)
    conn.execute(
        "INSERT INTO files (id, source_id, console, path, filename, title, "
        "title_norm, regions, languages, version, disc, tags, ext, size, url) "
        "VALUES (?, 's1', ?, ?, ?, ?, ?, ?, '', '', '', '', ?, 0, 'http://x')",
        (number, console, filename, filename, parsed["title"],
         parsed["title_norm"], ",".join(parsed.get("regions") or []),
         parsed.get("ext") or ""))
conn.commit()


def titles(query, **kwargs):
    """Every game one search finds, by name, shortest first."""
    found = db.search(conn, query, limit=50, **kwargs)
    return sorted((g["title"] for g in found["groups"]), key=len)


def finds(query, wanted):
    return any(wanted.lower() in title.lower() for title in titles(query))


# -- the ordinary case is untouched --------------------------------------
print("\nplain searches")
check("a title typed correctly is found",
      finds("super mario world", "Super Mario World"), True)
check("...and does not drag in the other Mario",
      finds("super mario world", "Super Mario 64"), False)
check("a partial word still prefixes",
      finds("final fant", "Final Fantasy VII"), True)
check("a word from the middle of a title works",
      finds("hedgehog", "Sonic The Hedgehog"), True)
check("nonsense finds nothing", titles("qqzzxx"), [])


# -- the apostrophe ------------------------------------------------------
print("\nwords run together")
check("'theres' finds the game with the apostrophe",
      finds("theres", "There's Nothing to Do"), True)
check("...without losing the game that really starts that way",
      finds("theres", "Theresia"), True)
check("more of the run-together title still finds it",
      finds("theres nothing", "There's Nothing to Do"), True)
# The loose version of this matched 'Rolo to the Rescue' on 'to-there-scue'.
check("the run-together match is anchored, not floating",
      db._plan(conn, "theres")[1], "theres%")  # noqa: SLF001


# -- one word wrong ------------------------------------------------------
print("\none word typed wrongly")
check("'jarry potter' still finds Harry Potter",
      finds("jarry potter", "Harry Potter"), True)
check("...all of them, not just one",
      len(titles("jarry potter")), 3)
check("a wrong word on its own finds nothing rather than everything",
      titles("jarry"), [])
check("two words wrong is not a search any more",
      titles("jarry pxtter"), [])


# -- the file's own vocabulary -------------------------------------------
print("\nregion and file type on the end")
check("'harry potter usa' finds the USA ones",
      finds("harry potter usa", "Chamber of Secrets"), True)
check("a file extension typed on the end is not fatal",
      finds("sonic the hedgehog.md", "Sonic The Hedgehog"), True)
check("...nor is one that does not match the file on disk",
      finds("sonic the hedgehog.zip", "Sonic The Hedgehog"), True)
check("a region word that is part of the title is kept",
      finds("super mario world", "Super Mario World"), True)
check("...even though 'world' is one of the words that can be trimmed",
      "world" in db.QUERY_NOISE, True)


# -- filters still apply -------------------------------------------------
print("\nfilters")
check("a console filter narrows a widened search",
      titles("theres", console="Nintendo DS"), ["Theresia - Dear Emile"])
check("a console filter that excludes everything finds nothing",
      titles("theres", console="PSP"), [])
check("facets are counted over the widened set too",
      sorted(f["value"] for f in db.search(
          conn, "theres")["facets"]["consoles"]),
      ["Nintendo DS", "SNES/Super Famicom"])

# -- which copy is offered first ---------------------------------------
#
# Two things decide the order of the copies inside a result, and the order of
# the two is the whole of it. Region comes first, because it is what somebody
# actually chose in Settings. MiNERVA comes second, inside whichever region
# tier a file already sits in: it carries the fullest sets and the dumps
# RetroAchievements built its own from, so between two American copies it is
# the one to offer - and it must never turn a Japanese copy into the answer
# for somebody who asked for American.

print("\nwhich copy leads")

conn.execute("INSERT INTO sources (id, console, name, identifier, url) "
             "VALUES ('mv', 'Various', 'MiNERVA', 'mv', 'http://m')")
ORDERED = [
    # (region, how it is fetched) - inserted worst-first on purpose, so any
    # ordering that simply keeps the insertion order fails this.
    ("Japan", "magnet:?xt=urn:btih:1"),
    ("Europe", "http://x/eu.zip"),
    ("Europe", "magnet:?xt=urn:btih:2"),
    ("USA", "http://x/us.zip"),
    ("USA", "magnet:?xt=urn:btih:3"),
]
for number, (region, url) in enumerate(ORDERED, start=100):
    conn.execute(
        "INSERT INTO files (id, source_id, console, path, filename, title, "
        "title_norm, regions, languages, version, disc, tags, ext, size, url) "
        "VALUES (?, ?, 'Nintendo 64', ?, ?, 'Copytest', 'copytest', ?, "
        "'', '', '', '', 'z64', 0, ?)",
        (number, "mv" if url.startswith("magnet:") else "s1",
         f"Copytest ({region}) {number}.z64",
         f"Copytest ({region}) {number}.z64", region, url))
conn.commit()


def copies(order):
    """How each copy of the test game is offered, best first."""
    found = db.search(conn, "copytest", limit=50, region=None)
    rows = found["groups"][0]["files"]
    return [f"{','.join(f['regions']) or '-'} {'MiNERVA' if
            f['url'].startswith('magnet:') else 'http'}" for f in rows]


# The region preference is read from settings, so it is passed in explicitly
# rather than depending on whatever this machine happens to have chosen.
import romsrx.db as _db  # noqa: E402
_real = _db.region_order
_db.region_order = lambda: ["USA", "Europe", "Japan"]
try:
    got = copies(["USA", "Europe", "Japan"])
finally:
    _db.region_order = _real

check("the preferred region leads, and MiNERVA leads it", got, [
    "USA MiNERVA", "USA http",
    "Europe MiNERVA", "Europe http",
    "Japan MiNERVA",
])
# Said again as its own claim, because this is the one that would be lost by
# sorting on the source before the region.
check("a MiNERVA copy does not outrank a better region",
      got.index("USA http") < got.index("Europe MiNERVA"), True)


# -- only the games that have achievements ----------------------------------
#
# Two questions that look alike and are not. The RA logo in the bar asks where
# a *copy* came from - a file off one of RetroAchievements' own shelves. This
# asks whether the *game* has achievements at all, whoever you get it from,
# and the answer is not in the index: it comes from matching their catalogue
# against this one, and is handed to the connection as a table to join.
#
# Done in the query rather than by hiding cards in the page, because the count
# over the list and the numbers in the dropdowns have to mean what they say.
# Hiding them afterwards would leave "589 games" written over a list of eleven.

print("\nnarrowing to games that have achievements")

# Two games, but four sets between them: one game very often answers for
# several, and Super Mario World really does carry 299 of them because every
# hack is patched onto that one cartridge. Both numbers are shown, because
# "8,137 games" on its own reads as though the rest went missing.
db.note_sets(conn, {("SNES/Super Famicom", "super mario world"): 3,
                    ("Nintendo 64", "super mario 64"): 1})

everything = db.search(conn, "", limit=50)
only = db.search(conn, "", limit=50, has_sets=True)
check("without it, every game is listed",
      everything["total"] > only["total"], True)
check("with it, only the ones named", only["total"], 2)
check("...and they are the right ones",
      sorted(g["title_norm"] for g in only["groups"]),
      ["super mario 64", "super mario world"])

# The number over the list is the number in the list. It was counted with the
# same filter, not taken from the unfiltered search and then reduced.
check("the total counts what is shown",
      only["total"], len(only["groups"]))
check("...and the sets those games carry are counted too", only["sets"], 4)
# Counted over the games actually matched, not over the whole catalogue.
one = db.search(conn, "super mario 64", limit=50, has_sets=True)
check("a narrower search counts fewer sets", one["sets"], 1)
# Off, the number would be counting sets for a list of games that mostly
# have none, which is not a question anybody asked.
check("with the filter off there is no set count",
      db.search(conn, "", limit=50).get("sets", 0), 0)

# The dropdowns are counted the same way, or picking a console would offer
# numbers that do not survive being clicked.
faceted = {row["value"] for row in only["facets"]["consoles"]}
check("the console list is narrowed with it",
      faceted, {"SNES/Super Famicom", "Nintendo 64"})

# Told a different set of games, it answers differently - the table is
# rebuilt rather than remembered from the last time.
db.note_sets(conn, {("Nintendo 64", "super mario 64"): 1})
check("a changed answer is not a stale one",
      db.search(conn, "", limit=50, has_sets=True)["total"], 1)
db.note_sets(conn, set())
check("and nothing having a set means nothing is listed",
      db.search(conn, "", limit=50, has_sets=True)["total"], 0)

print(f"\n{ok} passed, {fail} failed")
