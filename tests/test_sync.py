"""Carrying settings and saves between two computers.

Everything here is two folders pretending to be two machines, with a third
standing in for the cloud folder between them. Nothing touches the network.

The interesting part is not the copying, it is the deciding: what travels,
what must never travel, and what happens when both machines changed the same
memory card. The last of those is the only case where somebody can lose work,
so most of this is about that.
"""
import io
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from romsrx import sync, syncstore  # noqa: E402

ok = fail = 0


def check(label, got, want):
    global ok, fail  # noqa: PLW0603
    if got == want:
        ok += 1
        print(f"  pass  {label}")
    else:
        fail += 1
        print(f"  FAIL  {label}\n          got  {got!r}\n          want {want!r}")


box = Path(tempfile.mkdtemp(prefix="sync-"))


def entry(body: bytes, when: float = 100.0) -> dict:
    return {"hash": sync.digest_bytes(body), "size": len(body), "when": when}


# -- what the two ends decide --------------------------------------------

print("one side changed, the other did not")
here = {"a": entry(b"new")}
there = {"a": entry(b"old")}
seen = {"a": entry(b"old")}
todo = sync.plan(here, there, seen)
check("it is sent", todo["push"], ["a"])
check("...and nothing is fetched", todo["pull"], [])
check("...and it is not a conflict", todo["clash"], [])

todo = sync.plan({"a": entry(b"old")}, {"a": entry(b"new")},
                 {"a": entry(b"old")})
check("the other way round it is fetched", todo["pull"], ["a"])


print("\nsomething that only exists on one side")
todo = sync.plan({"a": entry(b"x")}, {}, {})
check("a file only here is sent", todo["push"], ["a"])
todo = sync.plan({}, {"a": entry(b"x")}, {})
# Newly made there, or deleted here? Nothing on either side can tell, and the
# safe reading of an ambiguity is to copy rather than to delete.
check("a file only there is fetched, never deleted", todo["pull"], ["a"])


print("\nnothing changed at all")
same = {"a": entry(b"same")}
todo = sync.plan(same, dict(same), dict(same))
check("nothing is sent", todo["push"], [])
check("...or fetched", todo["pull"], [])


print("\nboth machines changed the same file")
# The only case where somebody loses work, so it is never silent.
todo = sync.plan({"a": entry(b"from the desktop", when=200)},
                 {"a": entry(b"from the laptop", when=300)},
                 {"a": entry(b"what they agreed on last time")})
check("it is a conflict, not a copy", len(todo["clash"]), 1)
check("...and neither side is sent or fetched blindly",
      (todo["push"], todo["pull"]), ([], []))
check("the newer one wins", todo["clash"][0]["take"], "theirs")

todo = sync.plan({"a": entry(b"desktop", when=900)},
                 {"a": entry(b"laptop", when=300)},
                 {"a": entry(b"older")})
check("...whichever side that is", todo["clash"][0]["take"], "mine")

print("\nand the loser is kept, not dropped")
name = sync.kept_name("Mcd001.ps2", "Smarti", 1_700_000_000)
check("it is filed under the machine it came from",
      name.startswith("Mcd001.ps2.from-Smarti-"), True)
check("...with a name a filesystem will take",
      all(c not in name for c in '<>:"/\\|?*'), True)


# -- what must not travel -------------------------------------------------

print("\nwhere this machine keeps its games never travels")
# Two computers keep their games on different drives. A synced `folder` would
# point the second one at a directory that is not there.
check("`paths` is not among the parts that can be carried",
      "paths" in sync.CARRIES, False)
check("...nor the index, which is hundreds of MB and rebuildable",
      "index" in sync.CARRIES, False)
check("save states are carryable but not by default",
      ("states" in sync.CARRIES, "states" in sync.DEFAULT_PARTS), (True, False))


print("\nand a remote folder cannot write outside the places it names")
for evil in ["../../evil.txt", "app/../../evil", "", "nonsense/x",
             "app/../../../Windows/system.ini", "saves",
             "saves/An Emulator You Do Not Have/x.srm"]:
    if sync.where_for(evil) is not None:
        check(f"refuses {evil!r}", "allowed", "refused")
        break
else:
    check("every attempt to escape is refused", "refused", "refused")


print("\na sync of one part stays about that part")
# The store holds whatever every machine has ever put there. Asking to carry
# just the playlists used to drag the settings and the whole save history with
# them - they were in the store and not in the local list, which reads as "new
# over there" - so a narrow sync quietly became a full one.
everything = {
    "app/prefs.json": entry(b"1"), "app/playlists.json": entry(b"2"),
    "app/recent.json": entry(b"3"), "saves/PCSX2 memcards/M.ps2": entry(b"4"),
    "states/PCSX2 sstates/x.p2s": entry(b"5"),
    "history/PCSX2/2026-08-22/21-07/memcards/M.ps2": entry(b"6"),
}
check("only the part asked for is in scope",
      sorted(sync.only_parts(everything, ["playlists"])),
      ["app/playlists.json"])
check("...and the saves when those are asked for",
      sorted(sync.only_parts(everything, ["saves"])),
      ["saves/PCSX2 memcards/M.ps2"])
check("...states and history are their own parts",
      (len(sync.only_parts(everything, ["states"])),
       len(sync.only_parts(everything, ["history"]))), (1, 1))
check("the default carries everything but the states",
      len(sync.only_parts(everything, sync.DEFAULT_PARTS)),
      len(everything) - 1)

print("\nand a file the store holds that means nothing here")
# Somebody's own files in the same folder, or a part written by a newer
# version of the app than this one. Neither belongs to any part, so neither is
# fetched, and nothing outside the places this app names is ever written.
odd = {"holiday-photos/beach.jpg": entry(b"x"), "app/from-v9.json": entry(b"y")}
check("it belongs to no part", sync.only_parts(odd, sync.CARRIES), {})
check("...so a sync never sees it",
      sync.plan({}, sync.only_parts(odd, sync.CARRIES), {})["pull"], [])


print("\nwhat a saved session carries with it")
# The note somebody wrote on an evening, the pin keeping it past the
# fortnight, and the game it was, are all sidecars beside the snapshot rather
# than files inside it - which is what keeps them out of a restore. They still
# have to travel: a session that arrives on another computer without the line
# written on it has lost the part that made it findable.
sidecars = {
    "history/PCSX2/2026-08-22/21-07/memcards/Mcd001.ps2": entry(b"1"),
    "history/PCSX2/2026-08-22/21-07.note": entry(b"2"),
    "history/PCSX2/2026-08-22/21-07.game": entry(b"3"),
    "history/PCSX2/2026-08-22/21-07.pin": entry(b"4"),
}
check("all of them belong to the history part",
      sorted(sync.part_of(k) for k in sidecars), ["history"] * 4)
check("...so all of them are carried",
      len(sync.only_parts(sidecars, ["history"])), 4)
check("...and each maps back to a real place",
      all(sync.where_for(k) is not None for k in sidecars), True)


# -- a whole round trip, through the folder store -------------------------

print("\ntwo machines and a folder between them")
cloud = box / "cloud"
store = syncstore.FolderStore(str(cloud))
check("it makes its own folder", store.check()["ok"], True)
check("...named for the app",
      Path(store.describe()).name, sync.ROOT)

store.put("app/prefs.json", b'{"theme":"dark"}')
store.put("saves/PCSX2 memcards/Mcd001.ps2", b"sixty hours")
found = store.listing()
check("what was put is listed back", sorted(found),
      ["app/prefs.json", "saves/PCSX2 memcards/Mcd001.ps2"])
check("...with the content it was given",
      store.get("app/prefs.json"), b'{"theme":"dark"}')
check("...and a hash that matches", found["app/prefs.json"]["hash"],
      sync.digest_bytes(b'{"theme":"dark"}'))

store.put_manifest(sync.write_manifest(sync.manifest_of(
    {"app/prefs.json": {"hash": sync.digest_bytes(b'{"theme":"dark"}'),
                        "size": 16, "when": 1.0}})))
back = sync.read_manifest(store.get_manifest())
check("the manifest survives the round trip",
      back["app/prefs.json"]["hash"], sync.digest_bytes(b'{"theme":"dark"}'))
check("the manifest is not itself a synced file",
      sync.MANIFEST in store.listing(), False)

print("\nand a manifest that is nonsense is not fatal")
check("empty", sync.read_manifest(b""), {})
check("not json", sync.read_manifest(b"<html>nope</html>"), {})
check("json but wrong", sync.read_manifest(b'{"files": 3}'), {})
check("missing", sync.read_manifest(None), {})


print("\nwriting a file that is being watched by a sync client")
# Written beside and renamed, so a client watching the folder never uploads a
# half-written memory card.
store.put("saves/PCSX2 memcards/Big.ps2", b"x" * 5000)
leftovers = [p.name for p in (cloud / sync.ROOT).rglob("*.part")]
check("no half-written file is left behind", leftovers, [])
check("...and the whole thing arrived",
      len(store.get("saves/PCSX2 memcards/Big.ps2")), 5000)


shutil.rmtree(box, ignore_errors=True)
print(f"\n{ok} passed, {fail} failed")
sys.exit(1 if fail else 0)
