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

print(f"\n{ok} passed, {fail} failed")
