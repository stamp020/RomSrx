"""Trying each shelf to see which is quick tonight.

The measuring itself needs the network and other people's servers, so it is
not what is checked here. What is checked is everything around it, which is
where the judgement lives: which sources get probed at all, how the answers
are ordered, and that a source which refuses is reported rather than dropped.

Nothing here opens a connection - the probe is replaced by one that answers
from a table.
"""
import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from romsrx import speedtest  # noqa: E402

ok = fail = 0


def check(label, got, want):
    global ok, fail  # noqa: PLW0603
    if got == want:
        ok += 1
        print(f"  pass  {label}")
    else:
        fail += 1
        print(f"  FAIL  {label}\n          got  {got!r}\n          want {want!r}")


ANSWERS = {
    "https://a/1": {"ok": True, "bytes_per_sec": 1_000_000},
    "https://b/1": {"ok": True, "bytes_per_sec": 8_000_000},
    "https://c/1": {"ok": False, "why": "login"},
    "magnet:?xt=urn:btih:abc": {"ok": True, "bytes_per_sec": 300_000,
                                "torrent": True, "warming": True,
                                "seeds": 12, "peers": 30},
}
asked: list = []


def fake_one(item):
    asked.append(item.get("url"))
    return {"url": item.get("url"),
            **ANSWERS.get(item.get("url"), {"ok": False, "why": "nothing"})}


speedtest.one = fake_one


def measure(items):
    asked.clear()
    return speedtest.measure(items)["results"]


def item(url, source, name="Game (USA).chd", size=0):
    return {"url": url, "source": source, "filename": name, "size": size}


print("one probe per shelf, not one per row")
# A console's Redump is split across numbered parts that are all one shelf as
# far as "is this source quick" goes. Probing each part separately spends the
# budget on the same answer several times over - and it pushed the torrent off
# the end of the list, which is regularly the fastest thing there.
rows = measure([
    item("https://a/1", "Redump PS2 (Part 1)"),
    item("https://a/2", "Redump PS2 (Part 1)"),
    item("https://a/3", "Redump PS2 (Part 1)"),
    item("https://b/1", "PS2 Collection"),
])
check("three rows from one shelf are probed once", len(asked), 2)
check("...and the other shelf too",
      sorted(asked), ["https://a/1", "https://b/1"])
check("an answer comes back per shelf", len(rows), 2)


print("\nfastest first")
rows = measure([
    item("https://a/1", "slow one"),
    item("https://b/1", "quick one"),
])
check("the quick shelf leads", [r["source"] for r in rows],
      ["quick one", "slow one"])


print("\nand a shelf that will not serve you is still an answer")
# Worth seeing next to a speed rather than being dropped: "needs an account"
# is the difference between choosing that source and finding out slowly.
rows = measure([
    item("https://c/1", "wants a login"),
    item("https://a/1", "works"),
])
check("it is reported", [r["source"] for r in rows], ["works", "wants a login"])
check("...after everything that worked", rows[-1]["ok"], False)
check("...saying why", rows[-1]["why"], "login")


print("\na torrent says it is still climbing")
rows = measure([item("magnet:?xt=urn:btih:abc", "MiNERVA")])
check("the reading is marked as a floor", rows[0]["warming"], True)
check("...and carries the seed count", rows[0]["seeds"], 12)


print("\nand the awkward ones")
check("nothing to probe is not an error", measure([]), [])
check("...nor is a row with no link",
      measure([item("", "nowhere")]), [])
rows = measure([item(f"https://x/{n}", f"shelf {n}") for n in range(20)])
check(f"no more than {speedtest.MOST} shelves are tried at once",
      len(asked), speedtest.MOST)

print(f"\n{ok} passed, {fail} failed")
sys.exit(1 if fail else 0)
