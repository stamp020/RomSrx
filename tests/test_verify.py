"""Checking a copy against the set it belongs to.

The hashing itself is pinned in test_rahash.py. What is pinned here is the
verdict around it: which of them each situation produces, that the expensive
parts are skipped when they cannot help, and above all that "this copy will
not earn achievements" is never said about a file that was simply never
checked.

RetroAchievements is stood in for throughout - no key, no network, no games.
"""
import io
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from romsrx import artwork, rahash, retro  # noqa: E402

ok = fail = 0


def check(label, got, want):
    global ok, fail  # noqa: PLW0603
    if got == want:
        ok += 1
        print(f"  pass  {label}")
    else:
        fail += 1
        print(f"  FAIL  {label}\n          got  {got!r}\n          want {want!r}")


# -- the site, replaced ----------------------------------------------------

KEY = {"retroachievements": {"api_key": "xyz", "username": "someone"}}
NO_KEY = {"retroachievements": {"api_key": "", "username": ""}}

ids: dict[str, int] = {}         # filename -> the game it is
listed: dict[int, list] = {}     # game -> the dumps its set accepts
asked_for: list[int] = []        # every game hashes() was called about


def fake_game_id(console, name):
    return ids.get(name, 0)


def fake_hashes(game):
    asked_for.append(int(game))
    return listed.get(int(game), [])


retro.game_id = fake_game_id
retro.hashes = fake_hashes
artwork.settings = lambda: KEY

box = Path(tempfile.mkdtemp(prefix="verify-"))
rahash.CACHE = box / "filehashes.json"
rahash._cache = {}

# A Mega Drive cartridge, whose rule is "the file, whole", so the hash the
# set has to carry is one this test can work out for itself.
import hashlib  # noqa: E402

ROM_BYTES = b"sonic" * 400
rom = box / "Sonic (USA).md"
rom.write_bytes(ROM_BYTES)
ROM_MD5 = hashlib.md5(ROM_BYTES).hexdigest()  # noqa: S324

other = box / "Sonic (Europe).md"
other.write_bytes(b"sonic" * 401)

ids["Sonic (USA)"] = 1
ids["Sonic (Europe)"] = 1
ids["Sonic (Japan)"] = 2          # a game whose set lists nothing
ids["Tomb Raider"] = 3            # a disc
listed[1] = [{"name": "Sonic the Hedgehog (USA, Europe).md", "md5": ROM_MD5,
              "labels": ["nointro"], "patch": ""}]
listed[2] = []


def one(path, console, name):
    return {"path": str(path), "console": console, "name": name}


def verdicts(found):
    return [row["verdict"] for row in found["rows"]]


# -- the answers -----------------------------------------------------------

print("verdicts")
found = retro.verify([one(rom, "Genesis/Mega Drive", "Sonic (USA)")])
check("a copy the set is dumped from matches", verdicts(found), ["match"])
check("...and says which dump it is", found["rows"][0]["matched"],
      "Sonic the Hedgehog (USA, Europe).md")
check("...and carries its labels", found["rows"][0]["labels"], ["nointro"])
check("...and the hash it worked out", found["rows"][0]["md5"], ROM_MD5)

found = retro.verify([one(other, "Genesis/Mega Drive", "Sonic (Europe)")])
check("a copy that is not in the list does not match", verdicts(found),
      ["nomatch"])
check("...and still names the game it was checked against",
      found["rows"][0]["id"], 1)

found = retro.verify([one(rom, "Genesis/Mega Drive", "Unknown Game")])
check("a game with no set is not a failure", verdicts(found), ["noset"])

found = retro.verify([one(rom, "Genesis/Mega Drive", "Sonic (Japan)")])
check("nor is a set that lists no dumps", verdicts(found), ["noset"])

found = retro.verify([one(box / "gone.md", "Genesis/Mega Drive",
                          "Sonic (USA)")])
check("a file that isn't there is unreadable", verdicts(found), ["unreadable"])

# -- the one that must not be confused with a failure ----------------------

print("\ndiscs")
asked_for.clear()
found = retro.verify([one(box / "Tomb Raider.chd", "PlayStation",
                          "Tomb Raider")])
check("a disc is not checked", verdicts(found), ["unsupported"])
check("...and nothing was asked of the site to find that out", asked_for, [])
check("...and no hash is offered", found["rows"][0]["md5"], "")

# -- the container cases reach the verdict ---------------------------------

print("\ncontainers")
folder = box / "Sonic (USA) folder"
folder.mkdir()
(folder / "a.md").write_bytes(b"one")
(folder / "b.md").write_bytes(b"two")
found = retro.verify([one(folder, "Genesis/Mega Drive", "Sonic (USA)")])
check("a folder with two ROMs is ambiguous, not a failure",
      verdicts(found), ["ambiguous"])

# -- a shelf at a time -----------------------------------------------------

print("\nsweeping")
shelf = [one(rom, "Genesis/Mega Drive", "Sonic (USA)"),
         one(other, "Genesis/Mega Drive", "Sonic (Europe)"),
         one(box / "Tomb Raider.chd", "PlayStation", "Tomb Raider"),
         one(rom, "Genesis/Mega Drive", "Unknown Game")]

asked_for.clear()
seen: list[tuple] = []
found = retro.verify(shelf, progress=lambda done, total: seen.append((done, total)))
check("answers come back in the order they were asked",
      verdicts(found), ["match", "nomatch", "unsupported", "noset"])
check("one set is fetched once however many files ask for it",
      asked_for, [1])
check("progress is reported for every file", seen,
      [(1, 4), (2, 4), (3, 4), (4, 4)])
check("the counts add up", found["counts"]["match"], 1)
check("...for every verdict", found["counts"]["nomatch"], 1)
check("...including the ones nothing landed on", found["counts"]["notrom"], 0)

stopped = retro.verify(shelf, stop=lambda: True)
check("a sweep can be called off", stopped["checked"], 0)
check("...and says how many it was going to do", stopped["asked"], 4)

after = [0]


def stop_after_two():
    after[0] += 1
    return after[0] > 2


part = retro.verify(shelf, stop=stop_after_two)
check("...or partway through", part["checked"], 2)

# -- what survives closing the app ------------------------------------------
# The hashes were always kept and the verdicts were not, so the shelf came
# back blank and the only way to see the marks again was to sweep a library
# that had nothing left to work out. What is pinned here is the keeping, and -
# more important - the letting go: a remembered verdict about a file that has
# since changed is worse than no verdict, because it is asserted with the same
# confidence as a fresh one.

print("\nremembering")
retro.VERDICT_FILE = box / "verified.json"
retro._verdicts = {}

retro.verify([one(rom, "Genesis/Mega Drive", "Sonic (USA)"),
              one(other, "Genesis/Mega Drive", "Sonic (Europe)"),
              one(box / "Tomb Raider.chd", "PlayStation", "Tomb Raider")])
check("the file is written", retro.VERDICT_FILE.is_file(), True)

kept = {r["path"]: r for r in retro.verdicts()["rows"]}
check("a match is remembered", kept.get(str(rom), {}).get("verdict"), "match")
check("...and so is a copy that fails", kept.get(str(other), {}).get("verdict"),
      "nomatch")
check("...but a disc is not written down at all",
      str(box / "Tomb Raider.chd") in kept, False)
check("...and what it matched comes back with it",
      kept[str(rom)]["matched"], "Sonic the Hedgehog (USA, Europe).md")
check("...with how old the answer is", kept[str(rom)]["age"], 0)

# Rewritten with different bytes. The verdict was about the old ones.
rom.write_bytes(b"a different dump entirely")
kept = {r["path"]: r for r in retro.verdicts()["rows"]}
check("a changed file drops its verdict", str(rom) in kept, False)
check("...and the one beside it is untouched", str(other) in kept, True)

other.unlink()
check("a deleted file drops its verdict too",
      [r["path"] for r in retro.verdicts()["rows"]], [])

# A library entry is as often a folder as a file, and a folder has no size of
# its own - which is what made every extracted game lose its verdict the
# moment it was written down.
print("\nfolders")
kept_folder = box / "Sonic (USA) as a folder"
kept_folder.mkdir()
(kept_folder / "Sonic (USA).md").write_bytes(ROM_BYTES)
size, when = rahash.stamp(kept_folder)
check("a folder is stamped on what is inside it", size, len(ROM_BYTES))
check("...and has a time", when > 0, True)

retro.verify([one(kept_folder, "Genesis/Mega Drive", "Sonic (USA)")])
kept = {r["path"]: r for r in retro.verdicts()["rows"]}
check("so an extracted game is remembered",
      kept.get(str(kept_folder), {}).get("verdict"), "match")

(kept_folder / "Sonic (USA).md").write_bytes(b"swapped for something else")
kept = {r["path"]: r for r in retro.verdicts()["rows"]}
check("...and forgotten when its contents change", str(kept_folder) in kept, False)

check("an empty folder is nothing to remember",
      rahash.stamp(box / "Sonic (USA) folder" / "nope"), (0, 0))

# -- with nothing filled in -------------------------------------------------

print("\nno key")
artwork.settings = lambda: NO_KEY
found = retro.verify([one(rom, "Genesis/Mega Drive", "Sonic (USA)")])
check("without a key there is no answer at all", found,
      {"ok": False, "reason": "nokey"})
artwork.settings = lambda: KEY

check("and nothing to say about nothing",
      retro.verify([]), {"ok": False, "reason": "nothing"})

shutil.rmtree(box, ignore_errors=True)
print(f"\n{ok} passed, {fail} failed")
sys.exit(1 if fail else 0)
