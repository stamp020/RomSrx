"""Box art from services you sign in to, for the games the free server misses.

thumbnails.libretro.com is keyed by No-Intro and Redump filenames, and that is
both its strength and its ceiling. When a file is named the way those sets name
it the art is exactly right; when it isn't, there is nothing at all. covers.py
already squeezes what it can out of that by matching against the server's real
directory listings rather than guessing - 87% of the index - and what is left
over is mostly two things: games whose filename never matched a set, and games
that never came in a box to photograph.

The services here are searched by *title* instead. That is a different axis, so
they miss different games, which is the whole reason they are worth asking.
They need an account, which is why none of this is on by default: with nothing
filled in, resolve() returns "" before it does any work at all and every cover
in the app behaves exactly as it did before this file existed.

Three of them, in the order they are asked:

* RetroAchievements - the only one of the three that is about retro games
  rather than games in general, and so the only one carrying art for hacks,
  translations and aftermarket homebrew. Half of it was already here: retro.py
  has kept per-console lists of every game with an achievement set since long
  before this file existed, without any key at all, purely so the right-click
  menu could open a game's page. That gives the numeric id, which was the one
  thing standing between this app and their artwork. A Web API key off the
  user's own settings page turns that id into a picture.
* IGDB - Twitch's games database, the closest thing games have to TMDB. Nearly
  every commercial release on every system this app indexes, one cover each,
  free for non-commercial use with a Twitch client id and secret.
* SteamGridDB - artwork uploaded by people rather than a publisher. Smaller and
  much less even, but it has covers for translations, hacks and homebrew that
  no commercial database will ever carry - exactly the category the thumbnail
  server is weakest on. A free key off a profile page.

A wrong cover is worse than no cover: a game wearing another game's box is
noticed instantly, where a blank tile is merely disappointing. So a candidate
is only accepted when both sides agree on the title exactly once case,
punctuation, accents and bracketed tags are taken out, and IGDB is asked to
answer within the right platform on top of that. SteamGridDB has no idea what a
platform is, which is why the order below is only a default: it is the order
that made sense before anyone had used them, and the settings page lets it be
rearranged by somebody who has.

Every answer is written down, misses included, because these services meter
requests by the day and a library redraw would otherwise spend that budget
asking the same forty questions again.
"""

from __future__ import annotations

import gzip
import json
import re
import threading
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request

from . import covers, state
from .paths import user

TIMEOUT = 20
AGENT = "RomSrx"

# -- what the user fills in ----------------------------------------------
# Stored in the user folder as artwork.json, in plain text. That is the same
# bargain the rest of the app makes with settings.json, and these are
# per-machine API keys for free accounts rather than passwords - but it is why
# the page says so out loud next to the boxes.
STORE = "artwork"

FIELDS: dict[str, tuple[str, ...]] = {
    "retroachievements": ("api_key",),
    "igdb": ("client_id", "client_secret"),
    "steamgriddb": ("api_key",),
}

# Asked in this order, and the first one with an answer wins.
#
# RetroAchievements first: it is the only one of the three that is *about*
# retro games rather than games in general, and it is the only one with art for
# the hacks, translations and aftermarket homebrew the other two have never
# heard of. It is also the cheapest to ask - retro.py already keeps the console
# lists that turn a title into a game id, and has done since before any of this
# existed - so putting it first spends fewer of everyone else's requests.
#
# Then IGDB, because it knows which platform it is answering about, and last
# SteamGridDB, which has no idea what a platform is.
ORDER = ("retroachievements", "igdb", "steamgriddb")


def provider_order() -> list[str]:
    """The order to ask them in, as the user arranged it.

    Rebuilt from ORDER rather than trusted as stored: a saved list from an
    older version will not name a service added since, and one that named a
    service that has been removed would otherwise sit in the list forever.
    Anything unrecognised is dropped, anything missing is appended, so this
    always returns every provider exactly once.
    """
    stored = _store().get("order")
    chosen = []
    for name in stored if isinstance(stored, list) else []:
        if name in FIELDS and name not in chosen:
            chosen.append(name)
    return chosen + [name for name in ORDER if name not in chosen]

# Where these services sit relative to the free thumbnail server.
#
# "gaps" is the default and the conservative one: libretro answers first, and
# what it has never heard of comes here. The other two exist because libretro's
# answer is not always the better one - it falls back to title screens and
# in-game snaps for anything that never came in a box, and a real cover from a
# database beats a screenshot of a title screen.
#
# "only" is the honest version of "stop using libretro": no fallback, so a game
# these services cannot match shows nothing at all. That is a real cost and the
# page says so, rather than quietly falling back and leaving somebody wondering
# why libretro art is still turning up.
MODES = ("gaps", "prefer", "only")
DEFAULT_MODE = "gaps"

# The store is read on the path that resolves every single cover, so it is
# parsed once and kept. Nothing else writes this file.
_store_cache: dict | None = None
_store_lock = threading.Lock()


def _store() -> dict:
    global _store_cache  # noqa: PLW0603
    with _store_lock:
        if _store_cache is None:
            raw = state.load(STORE, {})
            _store_cache = raw if isinstance(raw, dict) else {}
        return _store_cache


def _forget_store() -> None:
    global _store_cache  # noqa: PLW0603
    with _store_lock:
        _store_cache = None


def settings() -> dict:
    """Every provider's saved fields, with the blanks filled in."""
    stored = _store()
    out: dict[str, dict] = {}
    for name, fields in FIELDS.items():
        raw = stored.get(name)
        raw = raw if isinstance(raw, dict) else {}
        out[name] = {field: str(raw.get(field) or "").strip() for field in fields}
        # Absent means on: somebody who has filled in a key wants it used, and
        # the switch exists to turn one off without throwing the key away.
        out[name]["on"] = bool(raw.get("on", True))
    return out


def _ready(provider: str, conf: dict) -> bool:
    return all(conf.get(field) for field in FIELDS[provider])


def set_settings(changes: dict) -> dict:
    """Save what the page sent, ignoring anything not asked for.

    Changing a key throws away the remembered misses. Someone who has just
    pasted a key is, by definition, asking the app to go and look again, and
    the whole point of the cache is that it otherwise would not.
    """
    current = settings()
    if changes.get("mode") in MODES:
        current["mode"] = changes["mode"]
    else:
        current["mode"] = _store().get("mode", DEFAULT_MODE)

    # Stored as sent and tidied on the way out, so a list that is short, long
    # or full of nonsense cannot leave the app with no providers at all.
    if isinstance(changes.get("order"), list):
        current["order"] = [str(n) for n in changes["order"] if n in FIELDS]
    else:
        current["order"] = provider_order()

    touched = False
    for provider, fields in FIELDS.items():
        sent = changes.get(provider)
        if not isinstance(sent, dict):
            continue
        for field in fields:
            if field in sent:
                value = str(sent[field] or "").strip()
                touched = touched or value != current[provider][field]
                current[provider][field] = value
        if "on" in sent:
            was = current[provider]["on"]
            current[provider]["on"] = bool(sent["on"])
            touched = touched or was != current[provider]["on"]

    state.save(STORE, current)
    _forget_store()
    if touched:
        forget(misses_only=True)
        _igdb_forget_token()
    return current


def mode() -> str:
    """Where these services sit relative to libretro, right now.

    Never a mode that would leave the page blank: "only" with nothing signed in
    means no covers anywhere, so a mode that needs a working service is ignored
    until there is one. Someone who fills in a key, chooses "only", and then
    clears the key again gets their libretro covers back rather than a wall of
    filenames.
    """
    chosen = str(_store().get("mode") or DEFAULT_MODE)
    if chosen not in MODES or chosen == DEFAULT_MODE or not _active():
        return DEFAULT_MODE
    return chosen


def status() -> dict:
    """What the settings page shows: the fields, and whether each is usable."""
    conf = settings()
    order = provider_order()
    return {
        "providers": [{
            "name": name,
            "on": conf[name]["on"],
            "ready": _ready(name, conf[name]),
            "fields": {field: conf[name][field] for field in FIELDS[name]},
        } for name in order],
        "order": order,
        # What was chosen, and what is actually happening - which differ while
        # "only" is chosen and nothing is signed in, and the page says so.
        "mode": str(_store().get("mode") or DEFAULT_MODE),
        "effective": mode(),
        "cached": _cache_size(),
        "active": bool(_active()),
    }


def _active() -> list[str]:
    conf = settings()
    return [name for name in provider_order()
            if conf[name]["on"] and _ready(name, conf[name])]


# -- remembering answers --------------------------------------------------
# One file, `key -> [url, when]`, where a blank url is a remembered miss. Both
# services count requests against a daily allowance, and a page of forty tiles
# redrawn a dozen times an evening would eat it on questions already answered.
CACHE = "artcache"
HIT_LIFE = 90 * 24 * 3600
MISS_LIFE = 7 * 24 * 3600
CACHE_MAX = 40000            # a full index is ~130k files but far fewer titles

_cache: dict[str, list] | None = None
_cache_lock = threading.Lock()
_unsaved = 0
_saved_at = 0.0

# Writing the whole file on every answer would mean a few hundred kilobytes per
# cover on a first run. Batched instead: whichever of these comes first.
SAVE_EVERY = 12
SAVE_AFTER = 20.0


def _load_cache() -> dict:
    global _cache  # noqa: PLW0603
    if _cache is None:
        raw = state.load(CACHE, {})
        _cache = {k: v for k, v in raw.items()
                  if isinstance(v, list) and len(v) == 2}
    return _cache


def _cached(key: str):
    """The remembered answer, or None if there isn't a usable one."""
    with _cache_lock:
        entry = _load_cache().get(key)
        if not entry:
            return None
        url, when = str(entry[0] or ""), float(entry[1] or 0)
        if time.time() - when > (HIT_LIFE if url else MISS_LIFE):
            return None
        return url


def _remember(key: str, url: str) -> None:
    global _unsaved, _saved_at  # noqa: PLW0603
    flush = None
    with _cache_lock:
        cache = _load_cache()
        cache[key] = [url, time.time()]
        if len(cache) > CACHE_MAX:
            # Oldest first. This only ever trips on a library far larger than
            # the index, and dropping an entry costs one lookup, not a cover.
            for stale in sorted(cache, key=lambda k: cache[k][1])[:len(cache) // 4]:
                del cache[stale]
        _unsaved += 1
        now = time.time()
        if _unsaved >= SAVE_EVERY or now - _saved_at > SAVE_AFTER:
            flush = dict(cache)
            _unsaved, _saved_at = 0, now
    if flush is not None:
        state.save(CACHE, flush)


def forget(misses_only: bool = False) -> int:
    """Throw away remembered answers. Returns how many went."""
    global _unsaved  # noqa: PLW0603
    with _cache_lock:
        cache = _load_cache()
        before = len(cache)
        if misses_only:
            kept = {k: v for k, v in cache.items() if v[0]}
        else:
            kept = {}
        cache.clear()
        cache.update(kept)
        _unsaved = 0
        flush = dict(cache)
    state.save(CACHE, flush)
    return before - len(flush)


def _cache_size() -> int:
    with _cache_lock:
        return len(_load_cache())


# -- titles ---------------------------------------------------------------
# The article at the end is a No-Intro habit ("Legend of Zelda, The") and
# nobody else's: every database on the other side of this spells it the way the
# box does. Only ever moved from the part before the first " - ", because that
# is where a title ends and a subtitle begins.
ARTICLES = ("The", "A", "An", "Le", "La", "Les", "Los", "Las", "El", "Il",
            "Der", "Die", "Das", "De", "Het", "Een")


def title_of(name: str) -> str:
    """A filename turned back into what the game is called.

    `Legend of Zelda, The - A Link to the Past (USA) [!]` comes out as
    `The Legend of Zelda - A Link to the Past`, which is a thing you can hand a
    search box.
    """
    text = re.sub(r"\s*[\(\[][^\)\]]*[\)\]]", " ", name)
    text = re.sub(r"\s+", " ", text).strip(" -_.")
    head, sep, rest = text.partition(" - ")
    for article in ARTICLES:
        tail = f", {article}"
        if head.lower().endswith(tail.lower()):
            head = f"{article} {head[:-len(tail)]}"
            break
    return (head + sep + rest).strip()


def _key(text: str) -> str:
    """What two titles have to share to be the same game.

    covers.match_key does the work; the accents come off first, because one
    side writes Pokemon and the other writes Pokémon and they are not going
    to agree about it.
    """
    flat = unicodedata.normalize("NFKD", text)
    flat = "".join(ch for ch in flat if not unicodedata.combining(ch))
    return covers.match_key(flat)


# -- being polite ---------------------------------------------------------
class _Pace:
    """No more than so many calls a second, however many threads are asking.

    A library page asks for every tile it can see at once, so without this the
    first redraw after signing in would be forty simultaneous requests and a
    429 from a service that had been perfectly willing to answer them slowly.
    """

    def __init__(self, per_second: float, patience: float = 8.0):
        self._gap = 1.0 / per_second
        self._patience = patience
        self._lock = threading.Lock()
        self._next = 0.0

    def wait(self) -> bool:
        """Hold until this caller's turn. False if the queue is too long."""
        now = time.monotonic()
        with self._lock:
            due = max(now, self._next)
            if due - now > self._patience:
                return False
            self._next = due + self._gap
        delay = due - now
        if delay > 0:
            time.sleep(delay)
        return True


def _request(url: str, *, headers: dict | None = None,
             data: bytes | None = None) -> tuple[int, bytes]:
    """One HTTP call that cannot raise. Status 0 means it never got there."""
    head = {"User-Agent": AGENT, "Accept-Encoding": "gzip"}
    head.update(headers or {})
    request = urllib.request.Request(url, data=data, headers=head)
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:  # noqa: S310
            raw = response.read()
            if response.headers.get("Content-Encoding") == "gzip":
                raw = gzip.decompress(raw)
            return response.status, raw
    except urllib.error.HTTPError as exc:
        return exc.code, b""
    except (urllib.error.URLError, OSError, ValueError, TimeoutError):
        return 0, b""
    except Exception:  # noqa: BLE001 - a cover is never worth an exception
        return 0, b""


def _json(url: str, **kwargs):
    status, raw = _request(url, **kwargs)
    if status != 200 or not raw:
        return None
    try:
        return json.loads(raw.decode("utf-8", "replace"))
    except ValueError:
        return None


# -- IGDB -----------------------------------------------------------------
IGDB_TOKEN_URL = "https://id.twitch.tv/oauth2/token"  # noqa: S105 - a URL
IGDB_API = "https://api.igdb.com/v4"
# 264x374 is IGDB's "big"; this is the same at twice the size, which is what a
# 160-pixel tile on a high-density screen actually wants.
IGDB_IMAGE = "https://images.igdb.com/igdb/image/upload/t_cover_big_2x/{}.jpg"

_igdb_pace = _Pace(4)          # their published limit, exactly
_igdb_lock = threading.Lock()
_igdb_token_value = ""
_igdb_token_until = 0.0
_igdb_retry_at = 0.0

# This app's console -> the names IGDB might file that platform under. Several
# each, matched against IGDB's own name, alternative name and abbreviation,
# because their spelling of "Sega Mega Drive/Genesis" is not something to bet a
# whole console's covers on. The ids behind these names are looked up at run
# time rather than written here for the same reason.
IGDB_PLATFORMS: dict[str, tuple[str, ...]] = {
    "PlayStation": ("playstation", "ps1", "psx"),
    "PlayStation 2": ("playstation 2", "ps2"),
    "PSP": ("playstation portable", "psp"),
    "GameCube": ("nintendo gamecube", "gamecube", "ngc"),
    "Nintendo DS": ("nintendo ds", "nds"),
    "Nintendo DSi": ("nintendo dsi", "dsi"),
    "Nintendo Wii": ("wii",),
    "Nintendo 3DS": ("nintendo 3ds", "3ds"),
    "NES/Famicom": ("nintendo entertainment system", "nes",
                    "family computer", "famicom"),
    "Famicom Disk System": ("family computer disk system",
                            "famicom disk system", "fds"),
    "SNES/Super Famicom": ("super nintendo entertainment system", "snes",
                           "super famicom", "sfc"),
    "Nintendo 64": ("nintendo 64", "n64"),
    "Game Boy": ("game boy", "gb"),
    "Game Boy Color": ("game boy color", "gbc"),
    "Game Boy Advance": ("game boy advance", "gba"),
    "Pokemon Mini": ("pokemon mini", "pokémon mini"),
    "Virtual Boy": ("virtual boy",),
    "Atari 2600": ("atari 2600", "2600"),
    "Atari 7800": ("atari 7800", "7800"),
    "Atari Jaguar": ("atari jaguar", "jaguar"),
    "Atari Jaguar CD": ("atari jaguar cd", "jaguar cd"),
    "Atari Lynx": ("atari lynx", "lynx"),
    "SG-1000": ("sg-1000", "sg1000"),
    "Master System": ("sega master system/mark iii", "sega master system",
                      "master system", "sms", "mark iii"),
    "Genesis/Mega Drive": ("sega mega drive/genesis", "sega mega drive",
                           "mega drive", "genesis", "sega genesis"),
    "Sega CD": ("sega cd", "mega-cd", "mega cd", "sega cd/mega-cd"),
    "32X": ("sega 32x", "32x"),
    "Game Gear": ("sega game gear", "game gear"),
    "Sega Saturn": ("sega saturn", "saturn"),
    "Sega Dreamcast": ("dreamcast", "sega dreamcast", "dc"),
    "PC-8000/8800": ("pc-8801", "pc-8000", "pc-8800", "nec pc-8801"),
    "PC Engine/TurboGrafx-16": ("turbografx-16/pc engine", "pc engine",
                                "turbografx-16", "turbografx 16",
                                "pc engine supergrafx", "supergrafx"),
    "PC Engine CD/TurboGrafx-CD": ("turbografx-16/pc engine cd",
                                   "pc engine cd", "turbografx-cd",
                                   "pc engine cd-rom²"),
    "PC-FX": ("pc-fx", "pcfx"),
    "Neo Geo CD": ("neo geo cd", "neo-geo cd"),
    "Neo Geo Pocket": ("neo geo pocket", "neo geo pocket color", "ngp", "ngpc"),
}

PLATFORM_FILE = "artwork-igdb-platforms.json"
PLATFORM_LIFE = 30 * 24 * 3600

_platforms: list[tuple[int, frozenset[str]]] | None = None
_platform_lock = threading.Lock()


def _igdb_forget_token() -> None:
    global _igdb_token_value, _igdb_token_until, _igdb_retry_at  # noqa: PLW0603
    with _igdb_lock:
        _igdb_token_value, _igdb_token_until, _igdb_retry_at = "", 0.0, 0.0


def _igdb_token(conf: dict) -> str:
    """A Twitch app token, kept until it is nearly out of time.

    A refusal is remembered for five minutes as well. A wrong secret otherwise
    means every single tile on the page goes off and asks Twitch to reject it
    again, which is slow for the user and rude to Twitch.
    """
    global _igdb_token_value, _igdb_token_until, _igdb_retry_at  # noqa: PLW0603
    now = time.time()
    with _igdb_lock:
        if _igdb_token_value and now < _igdb_token_until:
            return _igdb_token_value
        if now < _igdb_retry_at:
            return ""

    body = urllib.parse.urlencode({
        "client_id": conf["client_id"],
        "client_secret": conf["client_secret"],
        "grant_type": "client_credentials",
    }).encode("utf-8")
    data = _json(IGDB_TOKEN_URL, data=body, headers={
        "Content-Type": "application/x-www-form-urlencoded"})
    token = str((data or {}).get("access_token") or "")

    with _igdb_lock:
        if not token:
            _igdb_token_value, _igdb_retry_at = "", time.time() + 300
            return ""
        try:
            life = float(data.get("expires_in") or 0)
        except (TypeError, ValueError):
            life = 0.0
        _igdb_token_value = token
        _igdb_token_until = time.time() + max(300.0, life - 300.0)
        _igdb_retry_at = 0.0
        return token


def _igdb_query(conf: dict, endpoint: str, body: str):
    token = _igdb_token(conf)
    if not token or not _igdb_pace.wait():
        return None
    found = _json(f"{IGDB_API}/{endpoint}", data=body.encode("utf-8"), headers={
        "Client-ID": conf["client_id"],
        "Authorization": f"Bearer {token}",
        "Content-Type": "text/plain",
    })
    return found if isinstance(found, list) else None


def _igdb_platforms(conf: dict) -> list[tuple[int, frozenset[str]]]:
    """IGDB's whole platform list, as (id, every name it goes by).

    Fetched rather than written down. Their ids are stable but their spellings
    are not the sort of thing to hard-code forty of and then discover, one
    console at a time, that three were wrong.
    """
    global _platforms  # noqa: PLW0603
    with _platform_lock:
        if _platforms is not None:
            return _platforms

        path = user(PLATFORM_FILE)
        rows = None
        try:
            with open(path, encoding="utf-8") as fh:
                saved = json.load(fh)
            if time.time() - float(saved.get("at") or 0) < PLATFORM_LIFE:
                rows = saved.get("rows")
        except (OSError, ValueError, TypeError):
            pass

        if rows is None:
            rows = _igdb_query(conf, "platforms",
                               "fields id,name,alternative_name,abbreviation; "
                               "limit 500;")
            if rows is None:
                return []          # not remembered: this is worth retrying
            try:
                path.parent.mkdir(parents=True, exist_ok=True)
                with open(path, "w", encoding="utf-8") as fh:
                    json.dump({"at": time.time(), "rows": rows}, fh)
            except OSError:
                pass

        built = []
        for row in rows:
            if not isinstance(row, dict) or not row.get("id"):
                continue
            names = {str(row.get(field) or "").strip().lower()
                     for field in ("name", "alternative_name", "abbreviation")}
            names.discard("")
            if names:
                built.append((int(row["id"]), frozenset(names)))
        _platforms = built
        return built


def _igdb_ids(conf: dict, console: str) -> list[int]:
    wanted = IGDB_PLATFORMS.get(console)
    if not wanted:
        return []
    aliases = frozenset(wanted)
    return [pid for pid, names in _igdb_platforms(conf) if names & aliases]


IGDB_WIDE = 50            # results asked for when nothing is filtered


def _igdb_pick(rows, want: str, ids: set[int]) -> str:
    """The first row that is unmistakably the game we asked about.

    Unmistakably: the same title once _key has been through it, on a platform
    this console maps to, with a cover to show. Anything less and the tile
    stays blank, which is the better of the two ways to be wrong.
    """
    for row in rows or []:
        if not isinstance(row, dict):
            continue
        cover = row.get("cover")
        image = cover.get("image_id") if isinstance(cover, dict) else None
        if not image or not (set(row.get("platforms") or []) & ids):
            continue
        titles = [str(row.get("name") or "")]
        for alt in row.get("alternative_names") or []:
            if isinstance(alt, dict):
                titles.append(str(alt.get("name") or ""))
        if any(_key(t) == want for t in titles if t):
            return IGDB_IMAGE.format(image)
    return ""


def _igdb_find(conf: dict, console: str, title: str) -> str:
    ids = _igdb_ids(conf, console)
    if not ids:
        return ""
    want = _key(title)
    # A quote would close the search string and leave the rest of the title
    # being read as query syntax.
    quoted = title.replace('"', " ").replace("\\", " ")
    fields = "fields name,alternative_names.name,cover.image_id,platforms;"

    # A plain search, with no filter clause at all. That is deliberate: the
    # platform and the cover are checked below, here, where there is no way to
    # get someone else's filter syntax subtly wrong and quietly see nothing.
    rows = _igdb_query(conf, "games",
                       f'search "{quoted}"; {fields} limit {IGDB_WIDE};')
    found = _igdb_pick(rows, want, set(ids))
    if found:
        return found

    # Fifty results and ours was not among them. Worth a second ask only when
    # the first came back full, which is the case where the right game is
    # ranked below fifty sequels and ports of something with a similar name -
    # games called things like "Mario". A short answer means IGDB has simply
    # never heard of it, and asking again differently will not change that.
    if not rows or len(rows) < IGDB_WIDE:
        return ""
    # One id at a time, OR'd: `= (a,b)` on an array field is not dependably
    # "either of these", and this console may well map to two platforms.
    clause = " | ".join(f"platforms = ({i})" for i in ids)
    rows = _igdb_query(conf, "games",
                       f'search "{quoted}"; {fields} where ({clause}); limit 30;')
    return _igdb_pick(rows, want, set(ids))


# -- SteamGridDB ----------------------------------------------------------
SGDB_API = "https://www.steamgriddb.com/api/v2"
# Their portrait size, which is the shape a box is. Anything else here would
# come back as a wide Steam banner and look nothing like the rest of the grid.
SGDB_SHAPE = "600x900"
SGDB_TRIES = 3                 # candidate games checked before giving up

_sgdb_pace = _Pace(3)


def _sgdb_find(conf: dict, console: str, title: str) -> str:  # noqa: ARG001
    """Community artwork, matched on the title and nothing else.

    `console` is accepted and ignored: SteamGridDB files artwork against a game,
    not a release of it, so there is nothing here to narrow by. That is why the
    title has to match exactly and why this is asked second.
    """
    head = {"Authorization": f"Bearer {conf['api_key']}"}
    if not _sgdb_pace.wait():
        return ""
    found = _json(f"{SGDB_API}/search/autocomplete/"
                  f"{urllib.parse.quote(title)}", headers=head)
    if not isinstance(found, dict):
        return ""

    want = _key(title)
    tried = 0
    for row in found.get("data") or []:
        if not isinstance(row, dict) or _key(str(row.get("name") or "")) != want:
            continue
        game = row.get("id")
        if not game:
            continue
        tried += 1
        if tried > SGDB_TRIES or not _sgdb_pace.wait():
            return ""
        art = _json(f"{SGDB_API}/grids/game/{int(game)}"
                    f"?dimensions={SGDB_SHAPE}&types=static&nsfw=false&humor=false",
                    headers=head)
        for item in (art or {}).get("data") or []:
            url = str(item.get("url") or "") if isinstance(item, dict) else ""
            if url.startswith("https://"):
                return url
    return ""


# -- RetroAchievements ----------------------------------------------------
# The one source here that is about retro games specifically, and so the only
# one with a cover for a translation patch or an aftermarket Mega Drive game.
#
# Half of this was already written. retro.py keeps a per-console list of every
# game with an achievement set - fetched without any key at all, cached for a
# week, matched by a folded title through several fallbacks tuned to the way
# RetroAchievements names things - purely so the right-click menu could open a
# game's page. That gives the numeric id, which was the thing standing in the
# way of using them for art. All that is left is turning an id into a picture,
# and that is one request.
RA_API = "https://retroachievements.org/API/API_GetGame.php"
RA_MEDIA = "https://media.retroachievements.org"

# Their stand-in for "this game has no box art". Serving it would put the same
# grey placeholder on every homebrew tile in the library, which is worse than
# the filename it replaced.
RA_BLANK = frozenset({"000000", "000001", "000002"})

_ra_pace = _Pace(2)          # no published limit; this is simply not greedy


def _ra_find(conf: dict, console: str, name: str) -> str:
    """Box art for a game RetroAchievements has a set for, or "".

    Note this takes the *filename*, not the cleaned-up title: retro.py does its
    own name folding, tuned to their naming, and it wants what was on disk.
    """
    from . import retro  # noqa: PLC0415 - only this one provider needs it

    try:
        game = retro.game_id(console, name)
    except Exception:  # noqa: BLE001 - a missing list is just a miss
        return ""
    if not game or not _ra_pace.wait():
        return ""

    asked = {"i": str(game), "y": conf["api_key"]}
    found = _json(f"{RA_API}?{urllib.parse.urlencode(asked)}")
    if not isinstance(found, dict):
        return ""

    # Only the box. Their title screens and in-game shots are the same kind of
    # thing libretro already falls back to, and covers.py has a place for those
    # that is deliberately behind every real cover - so offering them here
    # would jump a screenshot ahead of IGDB's actual box art.
    path = str(found.get("ImageBoxArt") or "")
    if not path.startswith("/"):
        return ""
    if path.rsplit("/", 1)[-1].split(".")[0] in RA_BLANK:
        return ""
    return f"{RA_MEDIA}{path}"


FINDERS = {"retroachievements": _ra_find,
           "igdb": _igdb_find, "steamgriddb": _sgdb_find}

# Providers that want the filename rather than the tidied-up title, because
# they do their own matching on it.
RAW_NAME = frozenset({"retroachievements"})

# Somewhere between "one at a time" and "however many tiles are on screen".
# Four keeps a first run moving without holding forty sockets open to two
# services that are doing this for free.
_slots = threading.BoundedSemaphore(4)
_asking_lock = threading.Lock()
_asking: dict[str, threading.Lock] = {}


def resolve(console: str, name: str) -> str:
    """The best art these services have for one game, or "".

    `name` is a filename with its extension already off, the same as
    covers.resolve takes. Returns "" immediately - no locks, no files, no
    network - when nobody has filled anything in, which is the case this is on
    the critical path for.
    """
    conf = settings()
    order = [p for p in provider_order()
             if conf[p]["on"] and _ready(p, conf[p])]
    if not order:
        return ""

    title = title_of(name)
    if not title:
        return ""
    key = f"{console}\t{_key(title)}"
    if not key.strip():
        return ""

    # Deliberately keyed on the title rather than the filename, so the USA and
    # European copies of one game are a single question. RetroAchievements is
    # the one provider that could tell them apart - it files a hack under its
    # own id - but a hack's title differs from the original's once the tags are
    # stripped, which is the case that actually matters.
    remembered = _cached(key)
    if remembered is not None:
        return remembered

    # One lookup per game however many tiles want it at once. Forty copies of
    # the same question is forty requests off a daily allowance and one answer.
    with _asking_lock:
        gate = _asking.setdefault(key, threading.Lock())
    with gate:
        remembered = _cached(key)
        if remembered is not None:
            return remembered

        url = ""
        with _slots:
            for provider in order:
                try:
                    url = FINDERS[provider](
                        conf[provider], console,
                        name if provider in RAW_NAME else title)
                except Exception:  # noqa: BLE001 - never break a page over art
                    url = ""
                if url:
                    break
        _remember(key, url)

    with _asking_lock:
        _asking.pop(key, None)
    return url


# Their screenshot size: 889x500, which is a thumbnail in the strip and still
# worth looking at full size.
IGDB_SHOT = "https://images.igdb.com/igdb/image/upload/t_screenshot_big/{}.jpg"


def screenshots(console: str, name: str, limit: int = 14) -> list[str]:
    """In-game pictures from IGDB, or [].

    The only source here that has more than one or two. libretro keeps a single
    snap per release and RetroAchievements one per game; IGDB carries six to
    ten for most commercial releases, which is what makes a strip worth paging
    through rather than a row of three.

    Remembered as one line of space-separated URLs under its own prefix, in the
    same file as the covers - the machinery for "what we found out about this
    title, and when" already exists and none of these ever contain a space.
    """
    conf = settings()["igdb"]
    if not conf["on"] or not _ready("igdb", conf):
        return []
    title = title_of(name)
    if not title:
        return []

    key = f"shots\t{console}\t{_key(title)}"
    remembered = _cached(key)
    if remembered is not None:
        return remembered.split() if remembered else []

    found: list[str] = []
    ids = set(_igdb_ids(conf, console))
    if ids:
        want = _key(title)
        quoted = title.replace('"', " ").replace("\\", " ")
        rows = _igdb_query(conf, "games",
                           f'search "{quoted}"; fields name,'
                           f"alternative_names.name,screenshots.image_id,"
                           f"platforms; limit {IGDB_WIDE};")
        # Every matching record, not merely the first.
        #
        # IGDB files one game per platform family, so a title can have five
        # records - and the one for the console being asked about is often the
        # barest of them. Stopping at the first match meant a record with no
        # pictures hid its siblings, which is how a game with screenshots on
        # IGDB arrived here with none.
        #
        # Still only records on the right platform. The GBA Order of the
        # Phoenix is not the PlayStation 2 one - different game, different
        # pictures - and borrowing across platforms is the same mistake as
        # letting a database with no idea what a platform is answer first.
        for row in rows or []:
            if not isinstance(row, dict):
                continue
            if not (set(row.get("platforms") or []) & ids):
                continue
            titles = [str(row.get("name") or "")]
            for alt in row.get("alternative_names") or []:
                if isinstance(alt, dict):
                    titles.append(str(alt.get("name") or ""))
            if not any(_key(t) == want for t in titles if t):
                continue
            for shot in row.get("screenshots") or []:
                if isinstance(shot, dict) and shot.get("image_id"):
                    found.append(IGDB_SHOT.format(shot["image_id"]))
                if len(found) >= limit:
                    return _keep(key, found)

    return _keep(key, found)


def _keep(key: str, found: list[str]) -> list[str]:
    """Write the answer down and hand it back."""
    _remember(key, " ".join(found))
    return found


def summary(console: str, name: str) -> str:
    """A paragraph about the game, from IGDB, or "".

    The preview panel's least important line and the only one that needs a
    second query, so it is remembered the same way covers are and skipped
    entirely when IGDB is not set up. Stored under its own key prefix in the
    same file: a summary and a cover URL are both "what we found out about
    this title", and one cache with one expiry is easier to reason about than
    two.
    """
    conf = settings()
    igdb = conf["igdb"]
    if not igdb["on"] or not _ready("igdb", igdb):
        return ""
    title = title_of(name)
    if not title:
        return ""

    key = f"sum\t{console}\t{_key(title)}"
    remembered = _cached(key)
    if remembered is not None:
        return remembered

    ids = set(_igdb_ids(igdb, console))
    text = ""
    if ids:
        want = _key(title)
        quoted = title.replace('"', " ").replace("\\", " ")
        rows = _igdb_query(igdb, "games",
                           f'search "{quoted}"; fields name,'
                           f"alternative_names.name,summary,platforms; "
                           f"limit {IGDB_WIDE};")
        for row in rows or []:
            if not isinstance(row, dict) or not row.get("summary"):
                continue
            if not (set(row.get("platforms") or []) & ids):
                continue
            titles = [str(row.get("name") or "")]
            for alt in row.get("alternative_names") or []:
                if isinstance(alt, dict):
                    titles.append(str(alt.get("name") or ""))
            if any(_key(t) == want for t in titles if t):
                text = " ".join(str(row["summary"]).split())
                break

    _remember(key, text)
    return text


# -- the "does this key work" button --------------------------------------
# One known game per service, chosen for being unambiguous in every database
# there is. The point is to tell "your key is wrong" apart from "that game
# isn't in there", which is otherwise a distinction the user has to guess at
# from a tile that stayed blank.
PROBE_CONSOLE = "SNES/Super Famicom"
PROBE_GAME = "Super Mario World"


def check(provider: str) -> dict:
    """Try a provider once and say plainly what happened."""
    if provider not in FIELDS:
        return {"ok": False, "error": "No such artwork service."}
    conf = settings()[provider]
    if not _ready(provider, conf):
        # Named rather than "fill in every box", which would be wrong about a
        # service that only wants one thing.
        missing = [f for f in FIELDS[provider] if not conf.get(f)]
        what = ("every box" if len(missing) != 1
                else "the " + missing[0].replace("_", " "))
        return {"ok": False, "error": f"Fill in {what} first."}

    if provider == "retroachievements":
        from . import retro  # noqa: PLC0415

        game = retro.game_id(PROBE_CONSOLE, PROBE_GAME)
        if not game:
            return {"ok": False,
                    "error": "Could not fetch RetroAchievements' game list. "
                             "That part needs no key, so this is the site "
                             "being unreachable rather than a bad key."}
        asked = {"i": str(game), "y": conf["api_key"]}
        if not isinstance(_json(f"{RA_API}?{urllib.parse.urlencode(asked)}"), dict):
            return {"ok": False,
                    "error": "RetroAchievements would not accept that API key."}

    if provider == "igdb":
        _igdb_forget_token()
        if not _igdb_token(conf):
            return {"ok": False, "error": "Twitch would not accept that client "
                                          "ID and secret."}
        found = _igdb_platforms(conf)
        if not found:
            return {"ok": False, "error": "Signed in, but IGDB did not return "
                                          "its platform list."}
        if not _igdb_ids(conf, PROBE_CONSOLE):
            return {"ok": False, "error": "Signed in, but none of IGDB's "
                                          "platforms matched a console."}

    url = ""
    try:
        url = FINDERS[provider](conf, PROBE_CONSOLE, PROBE_GAME)
    except Exception as exc:  # noqa: BLE001 - the message is the whole point
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}"[:200]}

    if not url:
        return {"ok": False, "error": f"Connected, but no cover came back for "
                                      f"{PROBE_GAME}."}
    return {"ok": True, "url": url,
            "detail": f"Found the {PROBE_GAME} cover."}
