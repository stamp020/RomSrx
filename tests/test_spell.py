"""What "did you mean" is allowed to say.

Two failures matter here, and they pull in opposite directions. Saying nothing
when the answer was obvious leaves the app telling somebody to guess again
about a catalogue it has in front of it. Saying the wrong thing is worse:
a suggestion gets followed, so a confident wrong answer sends somebody to a
different game and they have no way to know it happened.

So both are pinned. Ordinary typos - a swapped pair, a dropped letter, a
missing space - come back corrected; a real word that simply is not in the
index, and a short query that could be anything, come back with nothing.

Nothing here touches the network; the catalogue is a dozen rows made here.
"""
import io
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from romsrx import db, spell  # noqa: E402

ok = fail = 0


def check(label, got, want):
    global ok, fail  # noqa: PLW0603
    if got == want:
        ok += 1
        print(f"  pass  {label}")
    else:
        fail += 1
        print(f"  FAIL  {label}\n          got  {got!r}\n          want {want!r}")


box = Path(tempfile.mkdtemp(prefix="spell-"))
conn = db.connect(box / "test.db")
conn.execute(
    "INSERT INTO sources (id, console, name, identifier, url) VALUES (?,?,?,?,?)",
    ("s1", "PlayStation", "A shelf", "s1", "http://x"))

CATALOGUE = [
    "Castlevania - Symphony of the Night",
    "Final Fantasy VII",
    "Metal Gear Solid",
    "Crash Bandicoot",
    "Resident Evil 2",
    "Gran Turismo",
    "Tomb Raider",
    "Spyro the Dragon",
    "Silent Hill",
    "Tekken 3",
]
for at, title in enumerate(CATALOGUE):
    conn.execute(
        "INSERT INTO files (source_id, console, path, filename, title, "
        "title_norm, url) VALUES (?,?,?,?,?,?,?)",
        ("s1", "PlayStation", f"/{at}", f"{title}.bin", title,
         title.lower(), f"http://x/{at}"))
conn.commit()


def guess(text):
    return spell.suggest(conn, text).get("title", "")


print("typos it should correct")
for typed, want in (
    ("castlevaina - symphony of the night", "Castlevania - Symphony of the Night"),
    ("final fantsy vii", "Final Fantasy VII"),
    ("metal gear solod", "Metal Gear Solid"),
    ("crash bandicot", "Crash Bandicoot"),
    ("residnt evil 2", "Resident Evil 2"),
    ("silent hil", "Silent Hill"),
    ("tombraider", "Tomb Raider"),          # a missing space is one edit
):
    check(f"{typed!r}", guess(typed), want)

print("\nand what it must not answer")
# A game that is genuinely not here. Answering would send somebody to the
# wrong shelf with no way of noticing.
check("a game the index does not have", guess("chrono trigger"), "")
check("...nor one that only shares a few letters", guess("wipeout"), "")
# Short enough to be near everything.
check("a query too short to guess about", guess("gran"), "")
check("...and nothing at all", guess(""), "")
check("gibberish", guess("qwrtyplkjhg"), "")

print("\nan exact title is not a correction")
# It would have been found by the search, so this is never asked - but
# answering "did you mean Tekken 3" to somebody who typed Tekken 3 is the kind
# of wrong that makes people distrust the rest of it.
check("the title itself", guess("Tekken 3"), "")
check("...however it was capitalised", guess("TEKKEN 3"), "")

print("\nthe index follows the catalogue")
conn.execute(
    "INSERT INTO files (source_id, console, path, filename, title, "
    "title_norm, url) VALUES (?,?,?,?,?,?,?)",
    ("s1", "PlayStation", "/new", "Vagrant Story.bin", "Vagrant Story",
     "vagrant story", "http://x/new"))
conn.commit()
check("a game added after the first guess is found too",
      guess("vagrent story"), "Vagrant Story")

print(f"\n{ok} passed, {fail} failed")
sys.exit(1 if fail else 0)
