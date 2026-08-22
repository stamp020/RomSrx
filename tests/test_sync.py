"""Carrying settings and saves between two computers.

Everything here is two folders pretending to be two machines, with a third
standing in for the cloud folder between them. Nothing touches the network.

The interesting part is not the copying, it is the deciding: what travels,
what must never travel, and what happens when both machines changed the same
memory card. The last of those is the only case where somebody can lose work,
so most of this is about that.
"""
import io
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# A profile of its own, set before romsrx is imported, exactly as
# test_history.py does it: peek and pull read and write the real one
# otherwise.
_box = Path(tempfile.mkdtemp(prefix="romsrx-sync-home-"))
os.environ["APPDATA"] = str(_box)

from romsrx import state, sync, syncstore  # noqa: E402

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


# -- joining a set that already exists -----------------------------------

print("\na machine syncing for the very first time")
# No manifest, so both sides look changed and the newer-wins rule would hand
# it to whichever file was written last - which on a fresh machine is its own
# empty defaults. That is how a second computer pushed an empty playlist over
# the cloud and the first one then pulled the emptiness back.
here = {"a": entry(b"my empty default", when=500.0)}
there = {"a": entry(b"what the others agreed", when=100.0)}
todo = sync.plan(here, there, {}, joining=True)
check("the store wins even though ours is newer",
      [row["take"] for row in todo["clash"]], ["theirs"])
check("...and it is still a clash, so ours is kept beside it",
      len(todo["clash"]), 1)
check("...and nothing of ours goes up over it", todo["push"], [])

print("\nand once that machine has synced before")
todo = sync.plan(here, there, {}, joining=False)
check("the newer one wins again",
      [row["take"] for row in todo["clash"]], ["mine"])


# -- what must not travel, on the way in ---------------------------------

print("\nsettings arriving from another computer")
# The slice has the paths taken out of it - that is the point of the slice -
# so writing it as it stands does not merely fail to carry the paths, it
# deletes the ones already here. A machine lost the folder its games are in.
target = box / "settings-in"
target.mkdir()
(target / "settings.json").write_bytes(
    b'{"folder": "D:/Games", "emulators": {"pcsx2": "D:/p.exe"}, '
    b'"theme": "dark"}')
after = json.loads(state._merged_settings(       # noqa: SLF001
    target / "settings.json", b'{"theme": "light"}').decode("utf-8"))
check("the preference travels", after.get("theme"), "light")
check("...and this machine keeps its games folder",
      after.get("folder"), "D:/Games")
check("...and its emulators", after.get("emulators"), {"pcsx2": "D:/p.exe"})

print("\nand the preferences that name this computer")
check("the device name belongs to this machine",
      state.is_local_pref("syncDeviceName"), True)
check("...as does the id", state.is_local_pref("syncDeviceId"), True)
check("...and the folder it syncs through",
      state.is_local_pref("syncFolder"), True)
check("...and the password", state.is_local_pref("syncDavPass"), True)
check("an ordinary preference does not", state.is_local_pref("theme"), False)

spot = box / "prefs-in"
spot.mkdir()
(spot / "prefs.json").write_bytes(
    b'{"syncDeviceName": "Laptop", "syncDeviceId": "mine", '
    b'"syncFolder": "E:/OneDrive", "cardSize": 3}')
sliced = json.loads(sync._prefs_slice(            # noqa: SLF001
    spot / "prefs.json").decode("utf-8"))
check("nothing about this machine is sent", sorted(sliced), ["cardSize"])

# Both directions, because a store written by an older version of the app
# still has the other machine's name sitting in it.
kept = json.loads(sync._merged_prefs(             # noqa: SLF001
    spot / "prefs.json",
    b'{"syncDeviceName": "Desktop", "syncDeviceId": "theirs", '
    b'"syncFolder": "D:/Other", "cardSize": 9}').decode("utf-8"))
check("...and nothing about theirs is taken",
      kept.get("syncDeviceName"), "Laptop")
check("...nor their id", kept.get("syncDeviceId"), "mine")
check("...nor the folder they sync through",
      kept.get("syncFolder"), "E:/OneDrive")
check("but an ordinary preference does arrive", kept.get("cardSize"), 9)


print("\nwhere a fetched file is allowed to land")
check("not up out of the folder", sync.write_local("../../escape.json", b"x"),
      None)
check("...and not a part this app has never heard of",
      sync.write_local("wat/thing.json", b"x"), None)


# -- looking at the cloud, and taking one thing off it -------------------

# Only ever parts that live in this profile. "saves" and "states" are found by
# looking for the emulators themselves, which APPDATA does not move, so a pull
# of those in a test would write into the real RetroArch folder.
SAFE = ["playlists", "cart"]

print("\nlooking at what is out there")
lookat = box / "peeking"
state.set_prefs({"syncKind": "folder", "syncFolder": str(lookat),
                 "syncDeviceName": "Laptop"})
state.set_playlists([{"id": "b", "name": "My own list", "created": 1,
                      "items": []}])
far = syncstore.store_for()
far.put("app/playlists.json", b'[{"id": "a", "name": "Weekend games"}]')
far.put("app/cart.json", b'[{"key": "c"}]')
far.put_manifest(sync.write_manifest({}))

found = syncstore.peek(parts=SAFE)
shared = found["sources"][0]
rows = {row["part"]: row for row in shared["parts"]}
check("the shared lane is offered first", shared["shared"], True)
check("...with both parts", sorted(rows), ["cart", "playlists"])
check("...and what it holds", rows["playlists"]["files"], 1)
check("...against what is here", rows["playlists"]["hereFiles"], 1)
check("...and a part this machine has none of",
      rows["cart"]["hereFiles"], 0)
check("...which is called out as new", rows["cart"]["fresh"], 1)

print("\nand a part nothing out there has is not offered")
check("it is left out", any(
    row["part"] == "recent" for one in syncstore.peek(parts=["recent"])
    ["sources"] for row in one["parts"]), False)


# -- one copy each, so no machine's version is simply gone ---------------

print("\neach machine's own copy, beside the shared one")
# The shared lane can only hold one answer to "what are the playlists", so
# whichever machine syncs second wins it and the other's version is nowhere
# anybody can ask for. That is what this lane is for.
mine = sync.device()
for whose, name, title in (("aaaa1111", "Desktop", "On the desktop"),
                           ("bbbb2222", "Work PC", "At the office")):
    far.put(sync.mine_at("app/playlists.json", whose),
            ('[{"id": "x", "name": "%s"}]' % title).encode())
    far.put(sync.mine_at(sync.WHOAMI, whose),
            json.dumps({"id": whose, "name": name, "at": 1000.0}).encode())

found = syncstore.peek(parts=SAFE)
named = [one["name"] for one in found["sources"] if not one["shared"]]
check("both machines are offered by name", sorted(named),
      ["Desktop", "Work PC"])
check("...and the shared lane as well",
      sum(1 for one in found["sources"] if one["shared"]), 1)
check("a machine's own copy does not join the shared lane's counts",
      {row["part"]: row["files"]
       for row in found["sources"][0]["parts"]}["playlists"], 1)

print("\nand a shared sync cannot see them at all")
# The safety that matters: if these ever took part in a merge, three
# machines' playlists would be folded into one another.
check("they belong to no part",
      sync.part_of("devices/aaaa1111/app/playlists.json"), "")
check("...so a narrow sync passes over them",
      sync.only_parts({"devices/aaaa1111/app/playlists.json": {}},
                      ["playlists"]), {})
check("...and none of them can be written to this machine",
      sync.where_for("devices/aaaa1111/app/playlists.json"), None)

print("\ntaking the playlists from one named machine")
done = syncstore.pull(["playlists"], source="bbbb2222")
check("it came from there", done["source"], "bbbb2222")
check("...one file", done["fetched"], 1)
check("...and it is what is here now",
      [p["name"] for p in state.playlists()], ["At the office"])
check("...while the cart was not asked for", state.cart(), [])

print("\nand from the other one instead")
done = syncstore.pull(["playlists"], source="aaaa1111")
check("the other machine's copy arrives",
      [p["name"] for p in state.playlists()], ["On the desktop"])
check("...and what was here was kept", done["kept"], 1)

print("\nand the shared lane is still its own thing")
done = syncstore.pull(["playlists"])
check("it is taken from the shared lane", done["source"], "")
check("...which has its own answer",
      [p["name"] for p in state.playlists()], ["Weekend games"])

print("\nasking a machine that has never published")
try:
    syncstore.pull(["playlists"], source="nobody")
    check("it raises", False, True)
except syncstore.StoreError as why:
    check("it says so plainly", "not put anything there" in str(why), True)

print("\nand pulling nothing is refused rather than guessed at")
try:
    syncstore.pull([])
    check("it raises", False, True)
except syncstore.StoreError as why:
    check("it says so", "chosen" in str(why), True)


print("\npublishing this machine's own copy")
sending = box / "publishing"
state.set_prefs({"syncKind": "folder", "syncFolder": str(sending),
                 "syncDeviceName": "Laptop", "syncParts": ["playlists"]})
state.set_playlists([{"id": "z", "name": "Only here", "created": 1,
                      "items": []}])
out = syncstore.run(parts=["playlists"])
check("it goes up with the sync", out["mine"] >= 1, True)
under = sending / sync.ROOT / sync.DEVICES / mine["id"]
check("...under this machine's own id",
      (under / "app" / "playlists.json").is_file(), True)
check("...with a name beside it, so others need not show an id",
      json.loads((under / sync.WHOAMI).read_text(encoding="utf-8"))["name"],
      "Laptop")

print("\nand it is not sent again when nothing changed")
again = syncstore.run(parts=["playlists"])
check("nothing is re-uploaded", again["mine"], 0)
state.set_playlists([{"id": "z", "name": "Changed", "created": 1,
                      "items": []}])
check("...until something does",
      syncstore.run(parts=["playlists"])["mine"], 1)


print("\nand pointing it at somewhere else entirely")
# Both records beside the profile describe one store: what was agreed with
# it, and what has already been published to it. Moving the folder makes both
# false, and the one that bites is the second - it is what stops every sync
# re-uploading this machine's copy, so against a new empty folder it would
# say the files were already there and leave the new place half empty.
first = box / "before-the-move"
state.set_prefs({"syncKind": "folder", "syncFolder": str(first),
                 "syncDeviceName": "Laptop", "syncParts": ["playlists"]})
sync.save_seen({})
sync.save_sent({})
state.set_playlists([{"id": "q", "name": "Carried", "created": 1,
                      "items": []}])
started = syncstore.run(parts=["playlists"])
check("the first folder gets it", started["sent"], 1)
check("...and this machine's own copy", started["mine"], 1)

second = box / "after-the-move"
state.set_prefs({"syncFolder": str(second)})
moved = syncstore.run(parts=["playlists"])
check("the new folder gets the shared copy too", moved["sent"], 1)
check("...and the machine's own copy is not skipped", moved["mine"], 1)
check("...so nothing is missing over there",
      (second / sync.ROOT / sync.DEVICES / mine["id"] / "app"
       / "playlists.json").is_file(), True)
check("...and the shared lane is there as well",
      (second / sync.ROOT / "app" / "playlists.json").is_file(), True)

print("\nand the first run after this was added is not a move")
# An existing profile has an agreement and a published copy but no record of
# where they came from, because nothing wrote one until now. Reading that as
# "it moved" would throw both away and send everything again, which for a
# folder holding a couple of hundred megabytes is a poor way to say hello.
sync.where_path().unlink(missing_ok=True)
check("there is something worth keeping",
      bool(sync.load_seen() and sync.load_sent()), True)
syncstore.run(parts=["playlists"])
check("the agreement survives", sync.load_seen() != {}, True)
check("...and so does what was already published",
      sync.load_sent() != {}, True)
check("...and where it is, is written down from now on",
      sync.last_where() != "", True)


print("\nand staying put still costs nothing")
again = syncstore.run(parts=["playlists"])
check("nothing is re-sent", (again["sent"], again["mine"]), (0, 0))


print("\nwhat the other computers call this one")
naming = box / "naming"
state.set_prefs({"syncKind": "folder", "syncFolder": str(naming),
                 "syncDeviceName": "", "syncParts": ["playlists"]})
sync.save_seen({})
sync.save_sent({})
import platform  # noqa: E402, PLC0415
check("with nothing chosen it is the computer's own name",
      sync.device()["name"], platform.node())

was = sync.device()["id"]
state.set_prefs({"syncDeviceName": "  The one in the study  "})
check("a chosen name is used instead", sync.device()["name"],
      "The one in the study")
# The reason renaming is safe to offer at all: the id is what everything is
# filed under, and it does not move.
check("...and the id underneath does not change", sync.device()["id"], was)

state.set_playlists([{"id": "n", "name": "Named", "created": 1, "items": []}])
syncstore.run(parts=["playlists"])
under = naming / sync.ROOT / sync.DEVICES / was
check("the name goes up beside the files",
      json.loads((under / sync.WHOAMI).read_text(encoding="utf-8"))["name"],
      "The one in the study")

print("\nand renaming it again")
state.set_prefs({"syncDeviceName": "Study PC"})
syncstore.run(parts=["playlists"])
check("the new name is what the others see",
      json.loads((under / sync.WHOAMI).read_text(encoding="utf-8"))["name"],
      "Study PC")
check("...and nothing was filed under a second name",
      sorted(p.name for p in (naming / sync.ROOT / sync.DEVICES).iterdir()),
      [was])
check("...with what was already sent still there",
      (under / "app" / "playlists.json").is_file(), True)


print("\nand what is published is what this machine had, not what it took")
# The ordering that makes the whole lane worth having.
#
# A machine joining a set that already has an answer fetches that answer. If
# its own copy were published afterwards it would be publishing what it just
# took, all the lanes would agree, and the version this computer actually had
# would exist nowhere the other machines can reach - which is the thing the
# lane exists to prevent.
joining = box / "joining"
state.set_prefs({"syncKind": "folder", "syncFolder": str(joining),
                 "syncDeviceName": "Laptop", "syncParts": ["playlists"]})
ahead = syncstore.store_for()
ahead.put("app/playlists.json", b'[{"id": "a", "name": "What everyone has"}]')
ahead.put_manifest(sync.write_manifest({}))
sync.save_seen({})
sync.save_sent({})
state.set_playlists([{"id": "m", "name": "Only ever on the laptop",
                      "created": 1, "items": []}])

out = syncstore.run(parts=["playlists"])
check("it takes the shared answer", [p["name"] for p in state.playlists()],
      ["What everyone has"])
published = (joining / sync.ROOT / sync.DEVICES / mine["id"] / "app"
             / "playlists.json")
check("...and its own copy is still what it had",
      json.loads(published.read_text(encoding="utf-8"))[0]["name"],
      "Only ever on the laptop")
check("...so it can be asked for again",
      [row["name"] for row in syncstore.peek(parts=["playlists"])["sources"]
       if not row["shared"]] != [], True)

shutil.rmtree(_box, ignore_errors=True)

shutil.rmtree(box, ignore_errors=True)
print(f"\n{ok} passed, {fail} failed")
sys.exit(1 if fail else 0)
