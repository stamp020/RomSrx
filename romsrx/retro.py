"""Matching the games on this machine to their page on retroachievements.org.

RetroAchievements has no public "search by name" that works without an
account, and its ordinary web pages sit behind Cloudflare, which turns down
anything that isn't a browser. What it does still answer, to anyone, is the
endpoint its emulators use: one request per console returns every game on that
console that has an achievement set, as {game id: title}. That is the whole
dataset this needs - a title to look up, and the number that makes the URL.

So the same shape as covers.py: one list per console, cached on disk for a
week, matched by a folded title. Nothing here is on the critical path. If the
list can't be fetched the answer is "no page", and the menu entry that would
have opened it simply isn't offered - which is also the right answer for a
game RetroAchievements has never heard of.
"""

from __future__ import annotations

import json
import re
import threading
import time
import urllib.error
import urllib.parse
import urllib.request

from .names import normalize_title
from .paths import user

# The emulator-facing endpoint. `officialgameslist` is the one that means
# "games with achievements", as opposed to every ROM the site can identify.
LIST_URL = "https://retroachievements.org/dorequest.php?r=officialgameslist&c={id}"
GAME_URL = "https://retroachievements.org/game/{id}"

# Sent as an emulator rather than as a browser: this is the emulator API, and
# a made-up browser string is the thing their edge is filtering for.
USER_AGENT = "RomSrx/1.0 (+https://github.com/)"

# This app's console names -> RetroAchievements console ids. Verified against
# the endpoint itself rather than copied from a wiki page.
#
# Absent on purpose:
#   Nintendo 3DS - RetroAchievements does not cover it at all.
# Famicom Disk System is not a console of its own there; its games sit under
# the NES, so it points at the same list.
CONSOLES = {
    "Genesis/Mega Drive": 1,
    "Nintendo 64": 2,
    "SNES/Super Famicom": 3,
    "Game Boy": 4,
    "Game Boy Advance": 5,
    "Game Boy Color": 6,
    "NES/Famicom": 7,
    "Famicom Disk System": 7,
    "PC Engine/TurboGrafx-16": 8,
    "Sega CD": 9,
    "32X": 10,
    "Master System": 11,
    "PlayStation": 12,
    "Atari Lynx": 13,
    "Neo Geo Pocket": 14,
    "Game Gear": 15,
    "GameCube": 16,
    "Atari Jaguar": 17,
    "Nintendo DS": 18,
    "Nintendo Wii": 19,
    "PlayStation 2": 21,
    "Pokemon Mini": 24,
    "Atari 2600": 25,
    "Virtual Boy": 28,
    "SG-1000": 33,
    "Sega Saturn": 39,
    "Sega Dreamcast": 40,
    "PSP": 41,
    "PC-8000/8800": 47,
    "PC-FX": 49,
    "Atari 7800": 51,
    "Neo Geo CD": 56,
    "PC Engine CD/TurboGrafx-CD": 76,
    "Atari Jaguar CD": 77,
    "Nintendo DSi": 78,
}

FRESH = 7 * 24 * 3600       # a console's list is good for a week
RETRY_AFTER = 30 * 60       # ...and a failed fetch is not retried for this long
TIMEOUT = 30

# The word RetroAchievements puts in front of a title to say what kind of
# release it is. A plain title is a commercial release, which is what the
# files in a No-Intro or Redump set almost always are, so those win any tie.
_TAG_RE = re.compile(r"^(?:~[^~]*~\s*)+")
# "Zelda [Subset - Bonus]" is a second achievement set for a game that already
# has its own page, not a game. Its own page is the one worth opening.
_SUBSET_RE = re.compile(r"\[Subset\b", re.I)
# Hacks are fan edits, and RetroAchievements does carry sets for them. This
# index carries the hacks themselves too - 'Pokemon - Yellow Legacy (Hack)',
# 'Mario's Picross X (Hack)' - so a hack in the library has a real page to
# open, and the two should meet.
#
# They are only ever ranked last, though. A hack's title is a version of the
# title it was made from, so if a real release and a hack ever want the same
# key, the real release is what the file almost certainly is.
_HACK_RE = re.compile(r"~Hack~", re.I)

# How much worse than a real title each fallback spelling is. Ten apart so
# every genuine entry, hacks included, is ahead of every alias.
_ALIAS_STEP = 10
# Everything in brackets goes before the title is folded: the RetroAchievements
# title is 'Final Fantasy VII', the file is 'Final Fantasy VII (USA) (Disc 1)'.
_GROUP_RE = re.compile(r"\s*[\(\[][^\)\]]*[\)\]]")
# The same lookup is asked with a filename in some places and with a title
# already parsed out of one in others, so the extension has to come off here.
# Narrow on purpose: a run of letters and digits with no space in it, which
# `.chd` and `.bin.gz` are and the full stops in 'Mr. Do!' and 'Super Mario
# Bros.' are not.
_EXT_RE = re.compile(r"\.[A-Za-z0-9]{1,4}$")
# No-Intro parks the article after the part it belongs to, wherever that part
# ends: 'Legend of Zelda, The - A Link to the Past'. RetroAchievements writes
# the title the way the box does. normalize_title() already handles the article
# at the very end of a name; this is the same move for one in the middle, and
# it is applied to both sides so a title that really does read that way still
# matches itself.
_INNER_ARTICLE_RE = re.compile(
    r",\s*(the|a|an|le|la|les|el|los|das|der|die)\b", re.I)

# The studio's name in front of the title. A disc is labelled "Disney's
# Chicken Little" and "DreamWorks Madagascar"; RetroAchievements files both
# under what the game is actually called, so the two never meet.
#
# Every one of these is a brand rather than part of a name, which is the whole
# test for belonging here - and the list was read off the two sets rather than
# guessed. What the same scan turned up and is deliberately absent:
#
#   'super'      - Super Mario Bros. is not Mario Bros.
#   'battletoads', 'sonic and knuckles', 'sega ages', 'family', 'konamic'
#                - parts of titles, not labels on them.
#   'action replay ultimate codes for use with ...'
#                - a cheat disc for a game is not the game, and matching one
#                  would open the page of something the file isn't.
#
# Written the way match_key() leaves them: lower case, no punctuation. Longest
# first, so 'disney pixar' is tried before 'disney'.
_BRANDS = (
    "walt disney pictures presents",
    "dreamworks animation",
    "disney interactive",
    "from tv animation",
    "walt disney s",
    "disney pixar",
    "nickelodeon",
    "walt disney",
    "dreamworks",
    "lara croft",
    "disney s",
    "saban s",
    "disney",
)


# What a homebrew release puts on the end of its own name: 'Deadeus v1.3.8',
# 'SuperFly DX v1.1'. RetroAchievements lists the game, not the build.
#
# The version is only taken when it is written as one - a 'v' and then the
# numbers - so a trailing number that is part of the name survives: nothing
# here can turn 'Bloody Roar 2' into 'Bloody Roar'.
_VERSION_RE = re.compile(r"(?:\s+v\d+(?:\s+\d+)*)+$")
# 'Homebrew' is a statement about where the game came from. 'Demo' and 'Beta'
# are deliberately not here: a demo of a game is not the game, and trimming it
# would point 'Donkey Kong Country Demo' at Donkey Kong Country's page.
_BUILD_RE = re.compile(r"(?:\s+homebrew)+$")


def _unversioned(key: str) -> str:
    """The title without the build number a homebrew release carries."""
    trimmed = _BUILD_RE.sub("", key)
    trimmed = _BUILD_RE.sub("", _VERSION_RE.sub("", trimmed)).strip()
    return trimmed if trimmed != key and len(trimmed) >= 4 else ""


# One set writes 'Bloody Roar II', the other 'Bloody Roar 2'. Both are the
# same game and neither spelling is wrong, so the number is settled on one
# form before the two are compared.
#
# Only numerals of two letters or more are converted. A lone 'X' is the risk
# that decides this: it is ten in 'Final Fantasy X' and a name in 'Mega Man
# X', and reading the second as 'Mega Man 10' would hand over the page of a
# game that genuinely exists and is a different one. 'I', 'V', 'L', 'C', 'D'
# and 'M' are left alone for the same reason - they are initials as often as
# they are numbers.
_ROMAN = {
    "ii": "2", "iii": "3", "iv": "4", "vi": "6", "vii": "7", "viii": "8",
    "ix": "9", "xi": "11", "xii": "12", "xiii": "13", "xiv": "14", "xv": "15",
    "xvi": "16", "xvii": "17", "xviii": "18", "xix": "19", "xx": "20",
}


def _arabic(key: str) -> str:
    """The title with its Roman numerals written as figures, or "" if it
    hadn't any - so this only ever costs a dictionary lookup when it helps."""
    parts = key.split(" ")
    changed = False
    for at, part in enumerate(parts):
        if part in _ROMAN:
            parts[at] = _ROMAN[part]
            changed = True
    return " ".join(parts) if changed else ""


def _squashed(key: str) -> str:
    """The title with its spaces taken out, for comparing against a set that
    puts them somewhere else: 'Choro Q HG 2' and 'Choro Q HG2', '6th Mix' and
    '6thMix'. Only whitespace goes, so two names that differ in any character
    that means something stay different - 'bloody roar 3' and 'bloody roar 4'
    are as far apart squashed as they were before.
    """
    return key.replace(" ", "")


def _unbranded(key: str) -> str:
    """The same title without the studio in front, or "" if there isn't one.

    What is left has to still look like a title: dropping the brand off
    'Disney's Aladdin' leaves 'aladdin', which is a game, but there is nothing
    to be gained from letting a one-word remainder match half a console.
    """
    for brand in _BRANDS:
        if key.startswith(brand + " "):
            rest = key[len(brand) + 1:].strip()
            return rest if len(rest) >= 4 else ""
    return ""

_lock = threading.Lock()                        # guards _memory and _locks
_memory: dict[int, dict[str, int]] = {}         # console id -> key -> game id
_locks: dict[int, threading.Lock] = {}


def match_key(name: str) -> str:
    """A filename or a title folded down to the part worth comparing.

    The two sides are named by different people from different sets and agree
    on the title and almost nothing else, so the region, the revision and the
    disc number all go before anything is compared.
    """
    # Twice, for the '.bin.gz' and '.cue.gz' pairs the index also holds.
    trimmed = _EXT_RE.sub("", _EXT_RE.sub("", name))
    trimmed = _INNER_ARTICLE_RE.sub("", _GROUP_RE.sub(" ", trimmed))
    return normalize_title(trimmed.strip(" -_"))


def _cache_file(console_id: int):
    return user("retro") / f"console_{console_id}.json"


def _fetch(console_id: int) -> dict[str, str] | None:
    """{game id: title} for one console, or None if it couldn't be had."""
    request = urllib.request.Request(
        LIST_URL.format(id=console_id), headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:  # noqa: S310
            payload = json.loads(response.read().decode("utf-8", "replace"))
    except (urllib.error.URLError, OSError, ValueError, TimeoutError):
        return None
    except Exception:  # noqa: BLE001 - a bad answer must never break a page
        return None

    if not payload.get("Success"):
        return None
    games = payload.get("Response")
    return games if isinstance(games, dict) else None


def _write_cache(path, games, failed: bool) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            json.dump({"at": time.time(), "failed": failed, "games": games}, fh)
    except OSError:
        pass


def _build(games: dict[str, str]) -> dict[str, int]:
    """key -> game id, preferring the plain release over a tagged one.

    A title can arrive as 'Pocket Monsters Kin | Pocket Monsters Gin', which is
    one game under two names; both are worth having, since either could be the
    one the file was named after.
    """
    index: dict[str, int] = {}
    ranked: dict[str, int] = {}          # key -> how good the match we have is

    for raw_id, title in games.items():
        if not isinstance(title, str) or _SUBSET_RE.search(title):
            continue
        try:
            game_id = int(raw_id)
        except (TypeError, ValueError):
            continue

        stripped = _TAG_RE.sub("", title).strip()
        if stripped == title.strip():
            rank = 0                        # a plain commercial release
        elif _HACK_RE.search(title):
            rank = 2                        # a fan edit of one
        else:
            rank = 1                        # homebrew, unlicensed, a demo

        for part in stripped.split("|"):
            key = match_key(part)
            # Short keys are noise - a two-letter title matches half a set.
            if len(key) < 2:
                continue
            # The brandless form as well, for the times it is RetroAchievements
            # carrying the studio's name and the file that doesn't. Ranked
            # below every real title, so it can only ever fill a gap - a game
            # genuinely called what the alias spells still wins the key.
            plain = _unbranded(key)
            step = _ALIAS_STEP
            for candidate, weight in ((key, rank),
                                      (plain, rank + step),
                                      (_arabic(key), rank + step * 2),
                                      (_squashed(key), rank + step * 3),
                                      (_squashed(plain) if plain else "",
                                       rank + step * 4)):
                if not candidate:
                    continue
                if candidate not in index or weight < ranked[candidate]:
                    index[candidate] = game_id
                    ranked[candidate] = weight
    return index


def _index(console_id: int) -> dict[str, int]:
    """A console's title index, from memory, then disk, then the network.

    One fetch per console however many games are asking at once: a library
    page resolving four hundred titles would otherwise start four hundred
    identical downloads.
    """
    with _lock:
        if console_id in _memory:
            return _memory[console_id]
        gate = _locks.setdefault(console_id, threading.Lock())

    with gate:
        with _lock:                     # someone may have filled it meanwhile
            if console_id in _memory:
                return _memory[console_id]

        games, stale = None, None
        path = _cache_file(console_id)
        try:
            with open(path, encoding="utf-8") as fh:
                saved = json.load(fh)
            age = time.time() - float(saved.get("at") or 0)
            # A failed fetch is remembered too, so an offline app doesn't try
            # the network again for every single right-click.
            limit = RETRY_AFTER if saved.get("failed") else FRESH
            if age < limit:
                games = saved.get("games") or {}
            else:
                stale = saved.get("games") or None
        except (OSError, ValueError):
            pass

        if games is None:
            fetched = _fetch(console_id)
            if fetched is None:
                # A week-old list beats no list at all.
                games = stale or {}
                _write_cache(path, {} if stale is None else stale, failed=True)
            else:
                games = fetched
                _write_cache(path, games, failed=False)

        built = _build(games)
        with _lock:
            _memory[console_id] = built
        return built


def game_id(console: str, name: str) -> int:
    """The RetroAchievements game id for a file, or 0 if there isn't one."""
    console_id = CONSOLES.get((console or "").strip())
    if not console_id or not name:
        return 0
    key = match_key(name)
    if len(key) < 2:
        return 0
    index = _index(console_id)
    # The name as it is first, then the same name with less of it insisted
    # on: without the studio in front, then without the spaces. Each is only
    # reached when everything before it found nothing, so an alias can never
    # take a match away from a game that is named outright.
    plain = _unbranded(key)
    build = _unversioned(key)
    for candidate in (key, plain, build, _arabic(key),
                      _squashed(key), _squashed(plain), _squashed(build)):
        if candidate:
            found = index.get(candidate)
            if found:
                return found
    return 0


def page_url(game_id_: int) -> str:
    return GAME_URL.format(id=int(game_id_))


def lookup(items) -> list[int]:
    """Resolve a batch of {console, name} in one go, answers in the same order.

    The page asks for everything it is showing at once and remembers the
    answers, so opening a menu never has to wait for the network.
    """
    out: list[int] = []
    for item in items if isinstance(items, list) else []:
        if not isinstance(item, dict):
            out.append(0)
            continue
        out.append(game_id(str(item.get("console") or ""),
                           str(item.get("name") or "")))
    return out
