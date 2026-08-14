"""Finding box art, by asking the thumbnail server what it actually has.

The page used to guess: build a URL from the filename, ask for it, and if it
404s try a slightly different filename, up to ten times. That works for a
tidily-named commercial release and falls apart for everything else, and every
miss costs a handful of wasted requests.

This reads the server's directory listing for a system instead - one request,
a few hundred kilobytes, cached on disk - and matches against the names that
are really there. Measured over all 129,849 files in the index, guessing found
art for 70%; this finds 85%, and with the page's guesses left in behind it as
a safety net, 87%.

The other half of the gain is *which* art. Box art only exists for games that
came in a box, so homebrew, hacks, demos and prototypes had nothing - 45% of
them. The server also keeps title screens and in-game snaps, which are
captured from the games themselves and so exist for exactly the releases a box
never will. Preferring the box and falling back through those two takes that
category from 45% to 60%.

Nothing here is on the critical path: if the listing can't be fetched, this
answers "no" and the page falls back to guessing, which is what it did before.
"""

from __future__ import annotations

import gzip
import json
import re
import threading
import time
import urllib.error
import urllib.parse
import urllib.request

from .paths import user

BASE = "https://thumbnails.libretro.com"

# Best first. A box is what the game looked like on a shelf; a title screen is
# a decent stand-in; a snap of the game running is the last resort but still
# far better than a blank tile with a filename on it.
KINDS = ("Named_Boxarts", "Named_Titles", "Named_Snaps")

# Console -> the thumbnail server's name for that system. Mirrors the table in
# web/app.js, which still needs its own copy for the fallback guesses.
SYSTEMS = {
    "PlayStation": "Sony - PlayStation",
    "PlayStation 2": "Sony - PlayStation 2",
    "PSP": "Sony - PlayStation Portable",
    "GameCube": "Nintendo - GameCube",
    "Nintendo DS": "Nintendo - Nintendo DS",
    "Nintendo DSi": "Nintendo - Nintendo DSi",
    "Nintendo Wii": "Nintendo - Wii",
    "Nintendo 3DS": "Nintendo - Nintendo 3DS",
    "NES/Famicom": "Nintendo - Nintendo Entertainment System",
    "Famicom Disk System": "Nintendo - Family Computer Disk System",
    "SNES/Super Famicom": "Nintendo - Super Nintendo Entertainment System",
    "Nintendo 64": "Nintendo - Nintendo 64",
    "Game Boy": "Nintendo - Game Boy",
    "Game Boy Color": "Nintendo - Game Boy Color",
    "Game Boy Advance": "Nintendo - Game Boy Advance",
    "Pokemon Mini": "Nintendo - Pokemon Mini",
    "Virtual Boy": "Nintendo - Virtual Boy",
    "Atari 2600": "Atari - 2600",
    "Atari 7800": "Atari - 7800",
    "Atari Jaguar": "Atari - Jaguar",
    "Atari Jaguar CD": "Atari - Jaguar",
    "Atari Lynx": "Atari - Lynx",
    "SG-1000": "Sega - SG-1000",
    "Master System": "Sega - Master System - Mark III",
    "Genesis/Mega Drive": "Sega - Mega Drive - Genesis",
    "Sega CD": "Sega - Mega-CD - Sega CD",
    "32X": "Sega - 32X",
    "Game Gear": "Sega - Game Gear",
    "Sega Saturn": "Sega - Saturn",
    "Sega Dreamcast": "Sega - Dreamcast",
    "PC-8000/8800": "NEC - PC-8001 - PC-8801",
    "PC Engine/TurboGrafx-16": "NEC - PC Engine - TurboGrafx 16",
    "PC Engine CD/TurboGrafx-CD": "NEC - PC Engine CD - TurboGrafx-CD",
    "PC-FX": "NEC - PC-FX",
    "Neo Geo CD": "SNK - Neo Geo CD",
    "Neo Geo Pocket": "SNK - Neo Geo Pocket",
}
ALSO = {
    "Neo Geo Pocket": "SNK - Neo Geo Pocket Color",
    "PC Engine/TurboGrafx-16": "NEC - PC Engine SuperGrafx",
}

FRESH = 30 * 24 * 3600      # a listing is good for a month
RETRY_AFTER = 15 * 60       # ...and a failed fetch is not retried for this long
TIMEOUT = 45

_lock = threading.Lock()                       # guards _memory and _locks
_memory: dict[tuple[str, str], dict] = {}      # (system, kind) -> key -> name
_locks: dict[tuple[str, str], threading.Lock] = {}


def match_key(name: str) -> str:
    """A name reduced to the part worth comparing.

    Every bracketed group goes - region, revision, dump flags, the lot - along
    with punctuation and case. `Zelda II - The Adventure of Link (USA) [!]` and
    `Zelda II - The Adventure of Link (U)` both come out the same, which is the
    whole point: the two sides are named by different people from different
    sets and agree on the title and almost nothing else.
    """
    stripped = re.sub(r"\s*[\(\[][^\)\]]*[\)\]]", " ", name)
    return re.sub(r"[^a-z0-9]+", "", stripped.lower().replace("&", "and"))


def _cache_file(system: str, kind: str):
    safe = re.sub(r"[^\w]+", "_", f"{system}__{kind}")
    return user("thumbs") / f"{safe}.json"


def _fetch_listing(system: str, kind: str) -> list[str] | None:
    """Every filename the server has for this system and kind, or None."""
    url = f"{BASE}/{urllib.parse.quote(system)}/{kind}/"
    request = urllib.request.Request(url, headers={
        "User-Agent": "RomSrx", "Accept-Encoding": "gzip"})
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:  # noqa: S310
            raw = response.read()
            if response.headers.get("Content-Encoding") == "gzip":
                raw = gzip.decompress(raw)
    except (urllib.error.URLError, OSError, ValueError, TimeoutError):
        return None
    except Exception:  # noqa: BLE001 - a bad listing must never break a page
        return None

    text = raw.decode("utf-8", "replace")
    # An Apache-style index: one <a href="Name.png"> per entry.
    return [urllib.parse.unquote(href)[:-4]
            for href in re.findall(r'href="([^"?][^"]*\.png)"', text)]


def _index(system: str, kind: str) -> dict:
    """key -> exact filename, from memory, then disk, then the network.

    One fetch per system and kind however many covers are asking at once: a
    page of forty games all wanting the same listing would otherwise start
    forty identical downloads.
    """
    slot = (system, kind)
    with _lock:
        if slot in _memory:
            return _memory[slot]
        gate = _locks.setdefault(slot, threading.Lock())

    with gate:
        with _lock:                       # someone may have filled it meanwhile
            if slot in _memory:
                return _memory[slot]

        names, stale = None, None
        path = _cache_file(system, kind)
        try:
            with open(path, encoding="utf-8") as fh:
                saved = json.load(fh)
            age = time.time() - float(saved.get("at") or 0)
            # A failed fetch is remembered too, so an offline app doesn't try
            # the network again for every single tile.
            limit = RETRY_AFTER if saved.get("failed") else FRESH
            if age < limit:
                names = saved.get("names") or []
            else:
                stale = saved.get("names") or None
        except (OSError, ValueError):
            pass

        if names is None:
            fetched = _fetch_listing(system, kind)
            if fetched is None:
                # Keep whatever was there rather than throwing it away: a
                # month-old listing beats no listing at all.
                names = stale or []
                _write_cache(path, [] if stale is None else stale, failed=True)
            else:
                names = fetched
                _write_cache(path, names, failed=False)

        # Every name under each key, not just the first. The key deliberately
        # throws away the region and the revision, so one key routinely covers
        # the USA box, the European one and a prototype's - and keeping only
        # whichever sorted first handed a USA game the Asian box. Choosing
        # between them is resolve()'s job, and it needs to see them all.
        built: dict[str, list[str]] = {}
        for name in names:
            built.setdefault(match_key(name), []).append(name)
        with _lock:
            _memory[slot] = built
        return built


def _write_cache(path, names, failed: bool) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            json.dump({"at": time.time(), "failed": failed, "names": names}, fh)
    except OSError:
        pass


def systems_for(console: str) -> list[str]:
    return [s for s in (SYSTEMS.get(console), ALSO.get(console)) if s]


# The bracketed words that say which release this is, as opposed to the ones
# that say what state the dump is in. Only these are worth matching on.
REGIONS = frozenset({
    "usa", "europe", "japan", "world", "asia", "korea", "china", "taiwan",
    "brazil", "australia", "canada", "france", "germany", "spain", "italy",
    "netherlands", "sweden", "norway", "denmark", "finland", "russia", "uk",
})


def _regions_of(name: str) -> frozenset[str]:
    found: set[str] = set()
    for group in re.findall(r"\(([^()]*)\)", name):
        for part in group.split(","):
            word = part.strip().lower()
            if word in REGIONS:
                found.add(word)
    return frozenset(found)


def _pick(candidates: list[str], wanted: str) -> str:
    """Which of several covers filed under the same title to use.

    The exact filename wins outright - if the server has a picture of the very
    release on disk, that is the picture, and no cleverness improves on it.
    Failing that the one from the same region, because a USA game showing the
    European box is the sort of small wrongness people notice immediately.
    Failing that the plainest name, which is nearly always the original
    release rather than a demo or a prototype of it.
    """
    if len(candidates) == 1:
        return candidates[0]
    for candidate in candidates:
        if candidate == wanted:
            return candidate

    mine = _regions_of(wanted)

    def rank(candidate: str) -> tuple:
        theirs = _regions_of(candidate)
        overlap = bool(mine & theirs)
        return (
            0 if overlap else (1 if not mine or not theirs else 2),
            candidate.count("("),      # fewer tags = the plain release
            len(candidate),
        )

    return min(candidates, key=rank)


def resolve(console: str, name: str) -> str:
    """The best art this server has for one game, or "".

    `name` is the filename with its extension already off. Box art across
    every system this console maps to, then title screens, then snaps - so a
    real box always wins over a screenshot, whichever system supplies it.
    """
    key = match_key(name)
    if not key:
        return ""
    systems = systems_for(console)
    if not systems:
        return ""
    for kind in KINDS:
        for system in systems:
            found = _index(system, kind).get(key)
            if found:
                best = _pick(found, name)
                return (f"{BASE}/{urllib.parse.quote(system)}/{kind}/"
                        f"{urllib.parse.quote(best)}.png")
    return ""
