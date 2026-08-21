"""Reading a MiNERVA listing, and the one number that makes it useful.

MiNERVA shares a whole console as a single torrent, so at first glance there
is nothing here a per-game downloader can use. What changes that is the
filename: BitTorrent can fetch one file out of eleven thousand by setting the
rest to priority zero, and the torrent's own metadata says which name is
which.

The name is therefore the address, and this suite exists to keep it exact.
`data-m` is deliberately *not* the address, though it looks like one - it is
the row's place in the site's listing, which holds entries the torrent does
not and sorts them differently. Reading it as a file index fetched a
different game and reported success, which is why what goes on the magnet now
is the name.

The fixture is the real markup, trimmed: the whitespace, the escaped
apostrophes and the empty blocks between the pieces are all as the site
serves them, because those are what a parser gets wrong.

Nothing here touches the network.
"""
import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from romsrx import minerva  # noqa: E402

ok = fail = 0


def check(label, got, want):
    global ok, fail  # noqa: PLW0603
    if got == want:
        ok += 1
        print(f"  pass  {label}")
    else:
        fail += 1
        print(f"  FAIL  {label}\n          got  {got!r}\n          want {want!r}")


HASH = "eaaa169ffd32cbf59cbad17d03e3485bd4fdacbe"
MAGNET = f"magnet:?xt=urn:btih:{HASH}&amp;dn=Minerva_Myrient"


def row(name, size, at):
    """One entry, spaced the way the site spaces them."""
    return f'''
                <div class="entry" data-name="{name.lower()}">

                        <a href="/rom?id={9000 + at}" draggable="false">{name}</a>
                        <span>{size}</span>


                            <a href="javascript:void(0)" onclick="downloadMagnet('{MAGNET}')" data-m="{at}" draggable="false" title="Download Magnet">&#129522;</a>

                </div>'''


PAGE = f"""<!doctype html><html><body>
  <div class="entry"><a href="/browse/./Redump/">Redump</a></div>
  <div class="entry"><a href="/browse/./Redump/Sony%20-%20PlayStation/">Sony - PlayStation</a></div>
  {row("&#39;98 Koushien (Japan).zip", "266.85 MB", 0)}
  {row("Castlevania - Symphony of the Night (Europe).zip", "387.64 MB", 1225)}
  {row("Castlevania - Symphony of the Night (USA).zip", "387.64 MB", 1226)}
  {row("Tiny (Japan).zip", "1.5 KB", 4)}
  {row("Huge (USA).zip", "12.25 GB", 5)}
</body></html>"""

found = minerva.entries(PAGE)

print("what comes out of a listing")
check("only the games, not the folders above them", len(found), 5)
check("names are unescaped", found[0]["filename"], "'98 Koushien (Japan).zip")
check("...and the ordinary ones survive intact",
      found[2]["filename"], "Castlevania - Symphony of the Night (USA).zip")

print("\nthe name, which is the address")
check("it is read off the row", [e["at"] for e in found], [0, 1225, 1226, 4, 5])
check("...but the name is what goes on the magnet",
      found[2]["magnet"],
      f"magnet:?xt=urn:btih:{HASH}&dn=Minerva_Myrient"
      "#name=Castlevania%20-%20Symphony%20of%20the%20Night%20%28USA%29.zip")
check("...and reads back exactly",
      minerva.wanted_name(found[2]["magnet"]),
      "Castlevania - Symphony of the Night (USA).zip")
check("...with the entity in the magnet decoded",
      "&amp;" in found[2]["magnet"], False)
check("two games in one collection share an infohash and differ by index",
      (found[1]["magnet"].split("#")[0] == found[2]["magnet"].split("#")[0],
       found[1]["magnet"] != found[2]["magnet"]), (True, True))

print("\nsizes")
check("megabytes", found[1]["size"], int(387.64 * 1024 ** 2))
check("kilobytes", found[3]["size"], int(1.5 * 1024))
check("gigabytes", found[4]["size"], int(12.25 * 1024 ** 3))
for text in ("", "  ", "unknown", "-", "12", "MB"):
    check(f"{text!r} is no size at all", minerva.parse_size(text), 0)

print("\nrows that are not games")
# No index means no way to say which file is wanted, so there is nothing that
# could be downloaded and nothing worth writing down.
check("a row with no magnet is skipped",
      len(minerva.entries(
          '<div class="entry"><a href="/rom?id=1">A.zip</a><span>1 MB</span></div>')),
      0)
check("an empty page is empty, not an error", minerva.entries(""), [])
check("...and so is nonsense", minerva.entries("<html>hello</html>"), [])

print("\nthe addresses this builds")
check("a collection path becomes a browse URL",
      minerva.listing_url("./Redump/Sony - PlayStation/"),
      "https://minerva-archive.org/browse/./Redump/Sony%20-%20PlayStation/")
check("...with the awkward characters quoted",
      minerva.listing_url("./No-Intro/Sega - Mega Drive - Genesis/"),
      "https://minerva-archive.org/browse/./No-Intro/"
      "Sega%20-%20Mega%20Drive%20-%20Genesis/")
check("a slash on the end is not required",
      minerva.listing_url("./Redump/Sega - Saturn"),
      minerva.listing_url("./Redump/Sega - Saturn/"))
check("a game's own page", minerva.page_url(1189385),
      "https://minerva-archive.org/rom?id=1189385")

print("\nand a magnet that already had a fragment keeps only ours")
check("no two fragments on one magnet",
      minerva.file_magnet("magnet:?xt=urn:btih:" + HASH + "#file=7", "A.zip"),
      f"magnet:?xt=urn:btih:{HASH}#name=A.zip")
check("nothing in, nothing out", minerva.file_magnet("", "A.zip"), "")
check("...and a nameless row gets no magnet",
      minerva.file_magnet("magnet:?xt=urn:btih:" + HASH, ""), "")

# A name with the characters that would otherwise end the fragment early, or
# be read as another parameter.
awkward = "Rock & Roll #1 (USA) [b].zip"
check("an awkward name survives the round trip",
      minerva.wanted_name(minerva.file_magnet("magnet:?xt=urn:btih:" + HASH,
                                              awkward)),
      awkward)
check("...and does not leak into the magnet itself",
      "&" in minerva.file_magnet("magnet:?xt=urn:btih:" + HASH,
                                 awkward).split("#")[1], False)

print("\nwhat is not a game")
# The translation collections ship a documentation bundle beside the games.
# It is a couple of hundred megabytes of readme and it lands in search as a
# game called "Nintendo Famicom" if nothing drops it.
from romsrx import indexer  # noqa: E402

shelf = {"id": "s", "console": "NES/Famicom", "identifier": "./T-En/X/"}
kept = indexer._minerva_rows(shelf, [  # noqa: SLF001
    {"filename": "_Nintendo Famicom [T-En] Docs.zip", "size": 1, "magnet": "m"},
    {"filename": "Chrono Trigger (Japan) [T-En by X].zip", "size": 2, "magnet": "m"},
    # A real game whose name begins with an underscore. A rule that read that
    # as "not a game" would lose it, so the match is on both ends.
    {"filename": "_summer Double Sharp (Japan).zip", "size": 3, "magnet": "m"},
], set())
check("the docs bundle is dropped and the games are not",
      [r["filename"] for r in kept],
      ["Chrono Trigger (Japan) [T-En by X].zip",
       "_summer Double Sharp (Japan).zip"])

print("\nwhat the download queue will take")
# A magnet is queueable exactly when there is something that can run it.
# Without libtorrent the worker speaks HTTP and nothing else - byte ranges,
# .part resume, redirects - so a magnet job could only ever fail, and it did:
# the Download button on a file row posts straight to the server without
# passing the page's own check. Anything that is neither is refused either way.
from romsrx import downloads, torrent  # noqa: E402

engine = torrent.available()
print(f"  (libtorrent {'is' if engine else 'is not'} installed here)")

manager = downloads.Manager()
took = manager.add([
    {"url": "magnet:?xt=urn:btih:" + HASH + "#name=a.zip", "filename": "a.zip"},
    {"url": "https://example.invalid/b.zip", "filename": "b.zip"},
    {"url": "ftp://example.invalid/c.zip", "filename": "c.zip"},
    {"url": "", "filename": "d.zip"},
])
# The snapshot does not carry urls - the page has no use for them - so the
# filename stands in for which jobs survived.
queued = sorted(j["filename"] for j in manager.snapshot()["jobs"])
check("http is always queued", "b.zip" in queued, True)
check("a magnet is queued only where it can be run",
      "a.zip" in queued, engine)
check("...and nothing else ever is",
      [n for n in queued if n in ("c.zip", "d.zip")], [])
check("so the count follows the engine", len(took), 2 if engine else 1)

print(f"\n{ok} passed, {fail} failed")
sys.exit(1 if fail else 0)
