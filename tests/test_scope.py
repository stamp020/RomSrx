"""What the whole-site orders are allowed to rank.

"Shortest sets", "fastest to beat" and "fastest to master" are built from
RetroAchievements' own lists rather than from a search, and for a while that
meant they could not see one. Typing a title and then asking for the fastest
answered a question about the entire catalogue and threw the title away;
picking a region did nothing at all, because the region never left the page.

So the search box and the filter bar are handed to the ranking as a scope: the
set of (console, title_norm) a plain search would have found. What is pinned
here is that the scope is built from the same query planner and the same
filter SQL a search uses, that a console can be excluded through a filter that
another console satisfies, and that the pool honours it.

Nothing touches the network - the bulk set list is stood in for.
"""
import io
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from romsrx import db, retro, wanted  # noqa: E402

ok = fail = 0


def check(label, got, want):
    global ok, fail  # noqa: PLW0603
    if got == want:
        ok += 1
        print(f"  pass  {label}")
    else:
        fail += 1
        print(f"  FAIL  {label}\n          got  {got!r}\n          want {want!r}")


# -- an index with one game on two machines --------------------------------

box = Path(tempfile.mkdtemp(prefix="scope-"))
conn = db.connect(box / "test.db")
for ident, console, rank in (("ps2", "PlayStation 2", 0),
                             ("ps1", "PlayStation", 1)):
    conn.execute(
        "INSERT INTO sources (id, console, name, identifier, url, console_rank)"
        " VALUES (?, ?, 'Test Set', ?, 'https://example.invalid/s', ?)",
        (ident, console, ident, rank))


def add(source, console, filename, title, norm, regions="USA"):
    conn.execute(
        "INSERT INTO files (source_id, console, path, filename, title,"
        " title_norm, regions, languages, version, disc, tags, ext, size, url)"
        " VALUES (?, ?, ?, ?, ?, ?, ?, '', '', '', '', 'iso', 100, ?)",
        (source, console, filename, filename, title, norm, regions,
         f"https://example.invalid/{filename}"))


# The same game on both machines, but only the PlayStation 2 copy is European.
# That asymmetry is the whole point of scoping by console as well as by title:
# a region filter can be satisfied on one machine and not on the other.
add("ps2", "PlayStation 2", "Chicken Little (Europe).iso",
    "Chicken Little", "chicken little", regions="Europe")
add("ps1", "PlayStation", "Chicken Little (USA).iso",
    "Chicken Little", "chicken little", regions="USA")
add("ps2", "PlayStation 2", "Ratatouille (USA).iso",
    "Ratatouille", "ratatouille")
conn.commit()


# -- the scope itself ------------------------------------------------------

print("\nwhat a search would have found")

check("a query narrows it to the game that was typed",
      db.scope_of(conn, "chicken little"),
      {("PlayStation 2", "chicken little"), ("PlayStation", "chicken little")})

check("a region narrows it to the machine that satisfies it",
      db.scope_of(conn, "chicken little", region=["Europe"]),
      {("PlayStation 2", "chicken little")})

check("a console filter narrows it the same way",
      db.scope_of(conn, console=["PlayStation"]),
      {("PlayStation", "chicken little")})

check("nothing typed and nothing picked is everything",
      db.scope_of(conn),
      {("PlayStation 2", "chicken little"), ("PlayStation", "chicken little"),
       ("PlayStation 2", "ratatouille")})

check("a query nothing matches is empty rather than everything",
      db.scope_of(conn, "kingdom hearts"), set())


# -- the pool the rankings are drawn from ----------------------------------

# Stands in for the bulk per-console set list. Ratatouille has the smaller
# set, so it leads any ordering by size that is allowed to see it.
SETS = {
    "PlayStation 2": {11: {"title": "Chicken Little", "achievements": 16,
                           "points": 200, "modified": "2024-01-01"},
                      12: {"title": "Ratatouille", "achievements": 4,
                           "points": 40, "modified": "2024-01-01"}},
    "PlayStation": {21: {"title": "Chicken Little", "achievements": 9,
                         "points": 90, "modified": "2024-01-01"}},
}
retro.set_sizes = lambda console: SETS.get(console, {})

print("\none row per set, not one per shelf")
# A console that borrows another's list makes the app ask for the same games
# twice, and any game on both shelves came back twice - Balloon Fight appeared
# twice in "quickest to beat". Nothing borrows one today: the Famicom Disk
# System used to be pointed at the NES on the belief that its games were filed
# there, and it has a console of its own with 36 sets the NES list has never
# held. The deduplication stays, because the mistake is easy to make again.
check("no console is pointed at another's list", retro.ALIASES, {})
check("...and the Disk System asks for its own",
      retro.CONSOLES["Famicom Disk System"], 81)
check("...which is not the NES one",
      retro.CONSOLES["Famicom Disk System"] != retro.CONSOLES["NES/Famicom"],
      True)

# The mechanism, exercised against a borrowing that does not exist today.
# Written out rather than reaching for a real pair, so that fixing the next
# wrong console id cannot quietly delete the test for the deduplication.
retro.ALIASES["Borrowed Machine"] = "NES/Famicom"

twinned = [
    {"id": 5, "console": "Borrowed Machine", "norm": "a", "title": "A",
     "achievements": 3, "points": 30, "modified": ""},
    {"id": 5, "console": "NES/Famicom", "norm": "a", "title": "A",
     "achievements": 3, "points": 30, "modified": ""},
    {"id": 6, "console": "PlayStation", "norm": "b", "title": "B",
     "achievements": 4, "points": 40, "modified": ""},
]
once = wanted._one_per_set(twinned)  # noqa: SLF001
check("the set is listed once", len(once), 2)
check("...under the console it is really filed on",
      next(r["console"] for r in once if r["id"] == 5), "NES/Famicom")
check("...whichever order they arrived in",
      next(r["console"] for r in
           wanted._one_per_set(list(reversed(twinned)))  # noqa: SLF001
           if r["id"] == 5),
      "NES/Famicom")

print("\nthe pool the whole-site orders rank")

everything = wanted.indexed_sets(conn)
check("without a scope it is every set the index can fetch",
      sorted((r["console"], r["norm"]) for r in everything),
      [("PlayStation", "chicken little"), ("PlayStation 2", "chicken little"),
       ("PlayStation 2", "ratatouille")])

scoped = wanted.indexed_sets(conn, "", db.scope_of(conn, "chicken little"))
check("a scope drops the games that were not searched for",
      sorted((r["console"], r["norm"]) for r in scoped),
      [("PlayStation", "chicken little"), ("PlayStation 2", "chicken little")])

check("...and a region drops the machine that did not satisfy it",
      sorted((r["console"], r["norm"]) for r in wanted.indexed_sets(
          conn, "", db.scope_of(conn, region=["Europe"]))),
      [("PlayStation 2", "chicken little")])

check("several consoles at once, not just the first of them",
      sorted({r["console"] for r in wanted.indexed_sets(
          conn, ["PlayStation", "PlayStation 2"])}),
      ["PlayStation", "PlayStation 2"])

check("an empty list of consoles still means all of them",
      sorted({r["console"] for r in wanted.indexed_sets(conn, [])}),
      ["PlayStation", "PlayStation 2"])


# -- and the list that is actually drawn -----------------------------------

print("\nshortest sets, narrowed the same way")

whole = wanted.shortest(conn)
check("unscoped, the smallest set on the site leads",
      [g["title_norm"] for g in whole["groups"]],
      ["ratatouille", "chicken little"])

narrowed = wanted.shortest(conn, allow=db.scope_of(conn, "chicken little"))
check("a search leaves only what was searched for",
      [g["title_norm"] for g in narrowed["groups"]], ["chicken little"])
check("...and the total counts that, not the whole site", narrowed["total"], 1)

where, params = db.file_filter(None, ["Europe"], None, None, False)
region = wanted.shortest(conn, allow=db.scope_of(conn, region=["Europe"]),
                         where=where, params=params)
check("a region filter reaches the copies listed on the card, too",
      [f["filename"] for g in region["groups"] for f in g["files"]],
      ["Chicken Little (Europe).iso"])

conn.close()
print(f"\n{ok} passed, {fail} failed")
sys.exit(1 if fail else 0)
