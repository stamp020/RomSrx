"""The optional cover services, without ever going near either of them.

Everything here runs against a fake HTTP layer: `artwork._json` is replaced by
a lookup into a dictionary of canned responses, so the tests describe exactly
what RetroAchievements, IGDB and SteamGridDB would have said and then check
what the app does with it. That is the only way this code can be tested at all
- all three want an account, and a test suite that needs one is a test suite
nobody runs.

The three things worth being sure of:

* a cover is only accepted when the titles really match, because a game
  wearing another game's box is worse than a blank tile;
* nothing is asked twice, because these services meter requests by the day; and
* a screenshot never beats a real cover, whichever server each came from.

The user folder is redirected to a temporary directory first. Without that,
running this would overwrite the keys and the lookup cache of whoever ran it.
"""
import io
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from romsrx import paths  # noqa: E402

paths.USER_DIR = Path(tempfile.mkdtemp(prefix="romsrx-artwork-"))

from romsrx import artwork  # noqa: E402

ok = fail = 0


def check(label, got, want):
    global ok, fail  # noqa: PLW0603
    if got == want:
        ok += 1
        print(f"  pass  {label}")
    else:
        fail += 1
        print(f"  FAIL  {label}\n          got  {got!r}\n          want {want!r}")


def reset(**creds):
    """Start each section from nothing remembered and nothing signed in."""
    artwork.forget()
    artwork._platforms = None          # noqa: SLF001
    artwork._igdb_forget_token()       # noqa: SLF001
    artwork.set_settings({
        "retroachievements": {"api_key": "", "on": True},
        "igdb": {"client_id": "", "client_secret": "", "on": True},
        "steamgriddb": {"api_key": "", "on": True},
        "mode": "gaps",
        "order": list(artwork.ORDER),
        **creds,
    })
    # Both cleared: a section registers the answers it wants after calling
    # this, and one left over from the section above is how a test passes for
    # a reason that has nothing to do with what it says it checks.
    canned.clear()
    calls.clear()


# -- the fake service -----------------------------------------------------
# Keyed by URL for GETs and by "URL body" for the POSTs IGDB uses, because
# every IGDB query goes to the same address and only the body differs.
canned: dict[str, object] = {}
calls: list[str] = []


def fake_json(url, *, headers=None, data=None):  # noqa: ARG001
    key = url if data is None else f"{url} {data.decode('utf-8')}"
    calls.append(key)
    return canned.get(key)


artwork._json = fake_json          # noqa: SLF001
# The pacing is real code with real sleeps in it; the tests do not need to
# wait 250ms per call to prove it works.
artwork._igdb_pace.wait = lambda: True   # noqa: SLF001
artwork._sgdb_pace.wait = lambda: True   # noqa: SLF001

TOKEN_URL = artwork.IGDB_TOKEN_URL
GAMES = f"{artwork.IGDB_API}/games"
PLATFORMS = f"{artwork.IGDB_API}/platforms"

IGDB_CREDS = {"igdb": {"client_id": "cid", "client_secret": "sec", "on": True}}
SGDB_CREDS = {"steamgriddb": {"api_key": "key", "on": True}}
RA_CREDS = {"retroachievements": {"api_key": "rakey", "on": True}}

# retro.py turns a filename into a RetroAchievements game id off a cached
# per-console list. That list is its own module's business and is already
# tested by the app using it for the right-click menu, so here it is stubbed:
# what matters is what artwork.py does with the id it gets back.
from romsrx import retro  # noqa: E402

ra_ids = {"Super Mario World": 228}
retro.game_id = lambda console, name: ra_ids.get(name, 0)  # noqa: ARG005

RA_CALL = (f"{artwork.RA_API}?i=228&y=rakey")


def ra_answer(box):
    canned[RA_CALL] = {"ID": 228, "Title": "Super Mario World",
                       "ImageBoxArt": box, "ImageIngame": "/Images/999999.png"}


def igdb_ready():
    """The two answers every IGDB conversation starts with."""
    canned[f"{TOKEN_URL} client_id=cid&client_secret=sec"
           "&grant_type=client_credentials"] = {
        "access_token": "tok", "expires_in": 5000000}
    canned[f"{PLATFORMS} fields id,name,alternative_name,abbreviation; "
           "limit 500;"] = [
        {"id": 19, "name": "Super Nintendo Entertainment System",
         "alternative_name": "Super Famicom", "abbreviation": "SNES"},
        {"id": 29, "name": "Sega Mega Drive/Genesis", "abbreviation": "Genesis"},
        {"id": 6, "name": "PC (Microsoft Windows)", "abbreviation": "PC"},
    ]


FIELDS = "fields name,alternative_names.name,cover.image_id,platforms;"
# The unfiltered search, and the narrowed one it only falls back to when the
# first came back completely full.
BARE = f"limit {artwork.IGDB_WIDE};"
NARROW = "where (platforms = (19)); limit 30;"


def igdb_search(where, rows):
    """Register the answer to one search, whichever of the two it is."""
    canned[f'{GAMES} search "Super Mario World"; {FIELDS} {where}'] = rows


def filler(n):
    """`n` results that are nothing to do with what was asked for."""
    return [{"id": 1000 + i, "name": f"Filler {i}",
             "cover": {"image_id": "x"}, "platforms": [19]} for i in range(n)]


# -- names ----------------------------------------------------------------
print("\ntitles")
check("the article comes back to the front",
      artwork.title_of("Legend of Zelda, The - A Link to the Past (USA) [!]"),
      "The Legend of Zelda - A Link to the Past")
check("an article inside a subtitle is left alone",
      artwork.title_of("Chrono Trigger - Bend of Time, The (USA)"),
      "Chrono Trigger - Bend of Time, The")
check("region and dump flags go",
      artwork.title_of("Sonic The Hedgehog 2 (World) (Rev A) [!]"),
      "Sonic The Hedgehog 2")
check("a filename that is all tags has nothing left",
      artwork.title_of("(USA) [!]"), "")

check("accents do not stop two titles matching",
      artwork._key("Pokémon Red Version"),         # noqa: SLF001
      artwork._key("Pokemon - Red Version"))       # noqa: SLF001
check("ampersands and words are the same thing",
      artwork._key("Tom & Jerry"),                 # noqa: SLF001
      artwork._key("Tom and Jerry"))               # noqa: SLF001
check("two different games are not the same",
      artwork._key("Aladdin") == artwork._key("Alladin 2"), False)  # noqa: SLF001


# -- doing nothing at all -------------------------------------------------
print("\nwith nothing signed in")
reset()
check("no credentials means no answer", artwork.resolve("Game Boy", "Tetris"), "")
check("...and nothing was asked", calls, [])
check("...and nothing was written down", artwork.status()["cached"], 0)


# -- IGDB -----------------------------------------------------------------
print("\nIGDB")
reset(**IGDB_CREDS)
igdb_ready()
igdb_search(BARE, [
    {"id": 1, "name": "Super Mario World",
     "cover": {"image_id": "abc"}, "platforms": [19]},
])
check("a match on the right platform is the cover",
      artwork.resolve("SNES/Super Famicom", "Super Mario World (USA)"),
      "https://images.igdb.com/igdb/image/upload/t_cover_big_2x/abc.jpg")

reset(**IGDB_CREDS)
igdb_ready()
igdb_search(BARE, [
    {"id": 2, "name": "Super Mario World 2 - Yoshi's Island",
     "cover": {"image_id": "wrong"}, "platforms": [19]},
])
check("a near miss is refused rather than shown",
      artwork.resolve("SNES/Super Famicom", "Super Mario World (USA)"), "")

reset(**IGDB_CREDS)
igdb_ready()
igdb_search(BARE, [
    {"id": 3, "name": "Super Mario World", "platforms": [19]},   # no cover
])
check("a game with no artwork is a miss, not a broken URL",
      artwork.resolve("SNES/Super Famicom", "Super Mario World (USA)"), "")

reset(**IGDB_CREDS)
igdb_ready()
igdb_search(BARE, [
    {"id": 4, "name": "Super Mario World",
     "cover": {"image_id": "def"}, "platforms": [29]},           # wrong console
])
check("the right name on the wrong platform is refused",
      artwork.resolve("SNES/Super Famicom", "Super Mario World (USA)"), "")

reset(**IGDB_CREDS)
igdb_ready()
igdb_search(BARE, [
    {"id": 6, "name": "Mario World Super",
     "alternative_names": [{"name": "Super Mario World"}],
     "cover": {"image_id": "ghi"}, "platforms": [19]},
])
check("a game filed under another of its names still matches",
      artwork.resolve("SNES/Super Famicom", "Super Mario World (USA)"),
      "https://images.igdb.com/igdb/image/upload/t_cover_big_2x/ghi.jpg")

reset(**IGDB_CREDS)
igdb_ready()
igdb_search(BARE, filler(artwork.IGDB_WIDE - 1))
check("a short answer that misses is the end of it",
      artwork.resolve("SNES/Super Famicom", "Super Mario World (USA)"), "")
check("...so the narrowed search is never sent",
      [c for c in calls if "where" in c], [])

reset(**IGDB_CREDS)
igdb_ready()
igdb_search(BARE, filler(artwork.IGDB_WIDE))
igdb_search(NARROW, [
    {"id": 7, "name": "Super Mario World",
     "cover": {"image_id": "jkl"}, "platforms": [19]},
])
check("a full answer that misses is asked again, narrowed",
      artwork.resolve("SNES/Super Famicom", "Super Mario World (USA)"),
      "https://images.igdb.com/igdb/image/upload/t_cover_big_2x/jkl.jpg")

reset(**IGDB_CREDS)
igdb_ready()
check("a console IGDB has no platform for asks nothing",
      artwork.resolve("PC-FX", "Super Mario World (USA)"), "")
check("...not even a search", [c for c in calls if c.startswith(GAMES)], [])

reset(**IGDB_CREDS)
canned.clear()
check("a client secret Twitch refuses is a miss, not a crash",
      artwork.resolve("SNES/Super Famicom", "Super Mario World (USA)"), "")


# -- RetroAchievements ----------------------------------------------------
print("\nRetroAchievements")
reset(**RA_CREDS)
ra_answer("/Images/067895.png")
check("a game with a set gets its box art",
      artwork.resolve("SNES/Super Famicom", "Super Mario World"),
      "https://media.retroachievements.org/Images/067895.png")

reset(**RA_CREDS)
ra_answer("/Images/000002.png")
check("their 'no box art' placeholder is not passed off as a cover",
      artwork.resolve("SNES/Super Famicom", "Super Mario World"), "")

reset(**RA_CREDS)
ra_answer("")
check("a game with no box art at all is a miss",
      artwork.resolve("SNES/Super Famicom", "Super Mario World"), "")

reset(**RA_CREDS)
ra_answer("/Images/067895.png")
check("a game they have never heard of costs no request",
      artwork.resolve("SNES/Super Famicom", "Some Aftermarket Thing"), "")
check("...because the id comes first, from a list already on disk", calls, [])

reset(**RA_CREDS)
check("a key they reject is a miss, not a crash",
      artwork.resolve("SNES/Super Famicom", "Super Mario World"), "")

reset(retroachievements={"api_key": "", "on": True})
check("no key means it is not asked at all",
      [p for p in artwork.status()["providers"]
       if p["name"] == "retroachievements"][0]["ready"], False)


# -- the order they are asked in ------------------------------------------
# Which service answers first is the user's arrangement, not a constant.
print("\nthe chosen order")
reset()
check("the default is the one written in the module",
      artwork.provider_order(), list(artwork.ORDER))

artwork.set_settings({"order": ["steamgriddb", "retroachievements", "igdb"]})
check("a rearrangement sticks", artwork.provider_order(),
      ["steamgriddb", "retroachievements", "igdb"])
check("...and status hands the page the same list",
      [p["name"] for p in artwork.status()["providers"]],
      ["steamgriddb", "retroachievements", "igdb"])

artwork.set_settings({"order": ["igdb"]})
check("a short list keeps the rest, in their default order",
      artwork.provider_order(), ["igdb", "retroachievements", "steamgriddb"])

artwork.set_settings({"order": ["igdb", "mobygames", "igdb", "steamgriddb"]})
check("nonsense and repeats are dropped rather than stored",
      artwork.provider_order(), ["igdb", "steamgriddb", "retroachievements"])

# And the order is what resolve() actually walks.
reset(**{**RA_CREDS, **SGDB_CREDS})
artwork.set_settings({"order": ["steamgriddb", "retroachievements"]})
canned[f"{artwork.SGDB_API}/search/autocomplete/Super%20Mario%20World"] = {
    "data": [{"id": 7, "name": "Super Mario World"}]}
canned[f"{artwork.SGDB_API}/grids/game/7?dimensions={artwork.SGDB_SHAPE}"
       "&types=static&nsfw=false&humor=false"] = {
    "data": [{"url": "https://cdn2.steamgriddb.com/grid/1.png"}]}
ra_answer("/Images/067895.png")
check("moving SteamGridDB to the top makes it answer first",
      artwork.resolve("SNES/Super Famicom", "Super Mario World"),
      "https://cdn2.steamgriddb.com/grid/1.png")
check("...and RetroAchievements was not asked", [c for c in calls if "API_" in c], [])


# -- SteamGridDB ----------------------------------------------------------
print("\nSteamGridDB")
SEARCH = f"{artwork.SGDB_API}/search/autocomplete/Super%20Mario%20World"
GRIDS = (f"{artwork.SGDB_API}/grids/game/7?dimensions={artwork.SGDB_SHAPE}"
         "&types=static&nsfw=false&humor=false")

reset(**SGDB_CREDS)
canned[SEARCH] = {"data": [{"id": 7, "name": "Super Mario World"}]}
canned[GRIDS] = {"data": [{"url": "https://cdn2.steamgriddb.com/grid/1.png"}]}
check("a title match yields its grid",
      artwork.resolve("SNES/Super Famicom", "Super Mario World (USA)"),
      "https://cdn2.steamgriddb.com/grid/1.png")

reset(**SGDB_CREDS)
canned[SEARCH] = {"data": [{"id": 8, "name": "Super Mario World 2"}]}
check("a game that only nearly matches is not used",
      artwork.resolve("SNES/Super Famicom", "Super Mario World (USA)"), "")

reset(**SGDB_CREDS)
canned[SEARCH] = {"data": [{"id": 7, "name": "Super Mario World"}]}
canned[GRIDS] = {"data": [{"url": "http://insecure.example/1.png"}]}
check("artwork served over plain http is not offered to the page",
      artwork.resolve("SNES/Super Famicom", "Super Mario World (USA)"), "")


# -- the order they are asked in ------------------------------------------
print("\nboth at once")
reset(**{**IGDB_CREDS, **SGDB_CREDS})
igdb_ready()
igdb_search(BARE, [
    {"id": 1, "name": "Super Mario World",
     "cover": {"image_id": "abc"}, "platforms": [19]},
])
canned[SEARCH] = {"data": [{"id": 7, "name": "Super Mario World"}]}
canned[GRIDS] = {"data": [{"url": "https://cdn2.steamgriddb.com/grid/1.png"}]}
found = artwork.resolve("SNES/Super Famicom", "Super Mario World (USA)")
check("IGDB wins, because it knows which platform it answered about",
      found, "https://images.igdb.com/igdb/image/upload/t_cover_big_2x/abc.jpg")
check("...and SteamGridDB was never asked",
      [c for c in calls if "steamgriddb" in c], [])

reset(**{**IGDB_CREDS, **SGDB_CREDS})
igdb_ready()
igdb_search(BARE, [])
canned[SEARCH] = {"data": [{"id": 7, "name": "Super Mario World"}]}
canned[GRIDS] = {"data": [{"url": "https://cdn2.steamgriddb.com/grid/1.png"}]}
check("SteamGridDB picks up what IGDB could not",
      artwork.resolve("SNES/Super Famicom", "Super Mario World (USA)"),
      "https://cdn2.steamgriddb.com/grid/1.png")

reset(**{**IGDB_CREDS, **SGDB_CREDS})
artwork.set_settings({"igdb": {"on": False}})
canned[SEARCH] = {"data": [{"id": 7, "name": "Super Mario World"}]}
canned[GRIDS] = {"data": [{"url": "https://cdn2.steamgriddb.com/grid/1.png"}]}
artwork.resolve("SNES/Super Famicom", "Super Mario World (USA)")
check("a service switched off keeps its key and is not asked",
      [c for c in calls if c.startswith(TOKEN_URL)], [])
check("...and the key is still there",
      artwork.settings()["igdb"]["client_id"], "cid")


# -- not asking twice -----------------------------------------------------
print("\nremembering")
reset(**IGDB_CREDS)
igdb_ready()
igdb_search(BARE, [
    {"id": 1, "name": "Super Mario World",
     "cover": {"image_id": "abc"}, "platforms": [19]},
])
artwork.resolve("SNES/Super Famicom", "Super Mario World (USA)")
after_first = len(calls)
artwork.resolve("SNES/Super Famicom", "Super Mario World (USA)")
check("the same game is not looked up twice", len(calls), after_first)
check("a different release of it is the same question",
      artwork.resolve("SNES/Super Famicom", "Super Mario World (Europe) (Rev 1)"),
      "https://images.igdb.com/igdb/image/upload/t_cover_big_2x/abc.jpg")
check("...and cost nothing", len(calls), after_first)

reset(**IGDB_CREDS)
igdb_ready()
igdb_search(BARE, [])
artwork.resolve("SNES/Super Famicom", "Super Mario World (USA)")
missed = len(calls)
artwork.resolve("SNES/Super Famicom", "Super Mario World (USA)")
check("a miss is remembered too", len(calls), missed)

igdb_search(BARE, [
    {"id": 1, "name": "Super Mario World",
     "cover": {"image_id": "abc"}, "platforms": [19]},
])
check("a remembered miss stays a miss until told otherwise",
      artwork.resolve("SNES/Super Famicom", "Super Mario World (USA)"), "")
artwork.set_settings({"steamgriddb": {"api_key": "brand-new"}})
check("changing a key sends it back to look again",
      artwork.resolve("SNES/Super Famicom", "Super Mario World (USA)"),
      "https://images.igdb.com/igdb/image/upload/t_cover_big_2x/abc.jpg")

check("a hit survives a key change",
      artwork._cached(  # noqa: SLF001
          "SNES/Super Famicom\t" + artwork._key("Super Mario World")),  # noqa: SLF001
      "https://images.igdb.com/igdb/image/upload/t_cover_big_2x/abc.jpg")
artwork.set_settings({"steamgriddb": {"api_key": "newer-still"}})
check("...because only the misses are thrown away",
      artwork._cached(  # noqa: SLF001
          "SNES/Super Famicom\t" + artwork._key("Super Mario World")),  # noqa: SLF001
      "https://images.igdb.com/igdb/image/upload/t_cover_big_2x/abc.jpg")

check("and it is on disk, not just in memory",
      json.loads((paths.USER_DIR / "artcache.json").read_text("utf-8")).get(
          "SNES/Super Famicom\t" + artwork._key("Super Mario World"))[0],  # noqa: SLF001
      "https://images.igdb.com/igdb/image/upload/t_cover_big_2x/abc.jpg")


# -- where these sit relative to libretro ---------------------------------
# covers.resolve is the thing that actually decides, so it is what gets asked.
# Its own half is stubbed out: what matters here is which of the two is
# consulted, and in what order, not what the thumbnail server would have said.
print("\nwhich source wins")
from romsrx import covers  # noqa: E402

BOX_ART = "https://thumbnails.libretro.com/box.png"
SCREENSHOT = "https://thumbnails.libretro.com/snap.png"
LIBRETRO = BOX_ART
asked_here: list[tuple] = []

# What the thumbnail server has, as a set of the kinds it can answer with.
# Both by default; a section that cares sets it to one or the other.
has_kinds = {"box", "screens"}


def fake_here(console, name, kinds=covers.KINDS):  # noqa: ARG001
    asked_here.append(tuple(kinds))
    if kinds == covers.BOX:
        return BOX_ART if "box" in has_kinds else ""
    if kinds == covers.SCREENS:
        return SCREENSHOT if "screens" in has_kinds else ""
    return BOX_ART if "box" in has_kinds else (
        SCREENSHOT if "screens" in has_kinds else "")


covers._here = fake_here          # noqa: SLF001

SERVICE = "https://images.igdb.com/igdb/image/upload/t_cover_big_2x/abc.jpg"


def with_igdb(chosen, kinds=("box", "screens"), hits=True):
    reset(**IGDB_CREDS)
    igdb_ready()
    igdb_search(BARE, [
        {"id": 1, "name": "Super Mario World",
         "cover": {"image_id": "abc"}, "platforms": [19]},
    ] if hits else [])
    artwork.set_settings({"mode": chosen})
    has_kinds.clear()
    has_kinds.update(kinds)
    asked_here.clear()


def cover_for(game="Super Mario World (USA)"):
    return covers.resolve("SNES/Super Famicom", game)


with_igdb("gaps")
check("by default libretro's box art answers and no service is asked",
      cover_for(), BOX_ART)
check("...and nothing was spent on a service",
      [c for c in calls if c.startswith(GAMES)], [])

with_igdb("prefer")
check("'prefer' puts the service in front of libretro's box art",
      cover_for(), SERVICE)

with_igdb("prefer", hits=False)
check("'prefer' still falls back to libretro when the service has nothing",
      cover_for(), BOX_ART)

with_igdb("only", hits=False)
check("'only' means only - no cover rather than a libretro one",
      cover_for(), "")
check("...and libretro was never consulted", asked_here, [])

# The safety net. Choosing "only" and then clearing the key must not leave a
# library of blank tiles.
reset()
artwork.set_settings({"mode": "only"})
has_kinds.update({"box", "screens"})
asked_here.clear()
check("a mode that needs a service is ignored while there is none",
      artwork.mode(), "gaps")
check("...so libretro answers as it always did", cover_for(), BOX_ART)
check("...while the page can still see what was chosen",
      artwork.status()["mode"], "only")

reset(**IGDB_CREDS)
igdb_ready()
artwork.set_settings({"mode": "only"})
check("and it comes back the moment a key does", artwork.mode(), "only")
check("a nonsense mode is refused", artwork.set_settings(
    {"mode": "sideways"})["mode"], "only")


# -- screenshots are the last thing tried, anywhere ------------------------
# The point of the split: a title screen or an in-game snap is what you show
# when nobody has a cover, so it has to lose to a real one from either server.
print("\nscreenshots come last")

with_igdb("gaps", kinds=("screens",))
check("a service's cover beats a libretro screenshot", cover_for(), SERVICE)
check("...and the box art was asked for first, as it always is",
      asked_here[0], covers.BOX)

with_igdb("gaps", kinds=("box", "screens"))
check("but a libretro box still beats the service", cover_for(), BOX_ART)
check("...without the screenshots being consulted at all",
      covers.SCREENS in asked_here, False)

with_igdb("gaps", kinds=("screens",), hits=False)
check("a screenshot is still shown when nothing anywhere has a cover",
      cover_for(), SCREENSHOT)
check("...after both the box art and the service were tried",
      (asked_here[0], asked_here[-1]), (covers.BOX, covers.SCREENS))

with_igdb("gaps", kinds=(), hits=False)
check("and nothing at all is the honest answer when there is nothing",
      cover_for(), "")

with_igdb("prefer", kinds=("screens",))
check("'prefer' keeps screenshots last too", cover_for(), SERVICE)

with_igdb("only", kinds=("box", "screens"), hits=False)
check("'only' does not reach for a screenshot either", cover_for(), "")

# -- the Test button ------------------------------------------------------
print("\nthe test button")
reset()
check("nothing filled in is said plainly, not tried",
      artwork.check("igdb")["error"], "Fill in every box first.")
check("...naming the one box when only one is needed",
      artwork.check("retroachievements")["error"], "Fill in the api key first.")
check("a service that does not exist is refused",
      artwork.check("mobygames")["ok"], False)

reset(**IGDB_CREDS)
canned.clear()
result = artwork.check("igdb")
check("a rejected secret says so", result["ok"], False)
check("...and names Twitch, which is what rejected it",
      "Twitch" in result["error"], True)

reset(**IGDB_CREDS)
igdb_ready()
igdb_search(BARE, [
    {"id": 1, "name": "Super Mario World",
     "cover": {"image_id": "abc"}, "platforms": [19]},
])
check("a working key says so", artwork.check("igdb")["ok"], True)

print(f"\n{ok} passed, {fail} failed")
