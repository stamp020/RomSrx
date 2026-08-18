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

import concurrent.futures
import json
import os
import re
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from . import rahash, rapi
from .names import normalize_title
from .paths import user

# The emulator-facing endpoint. `officialgameslist` is the one that means
# "games with achievements", as opposed to every ROM the site can identify.
LIST_URL = "https://retroachievements.org/dorequest.php?r=officialgameslist&c={id}"
GAME_URL = "https://retroachievements.org/game/{id}"

# Sent as an emulator rather than as a browser: this is the emulator API, and
# a made-up browser string is the thing their edge is filtering for. Defined
# in rapi with the pacing, and re-exported here because most of the app knows
# it by this name.
USER_AGENT = rapi.USER_AGENT

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


# -- the patches ---------------------------------------------------------
#
# A hack or a translation with an achievement set is not a ROM anybody hands
# out: it is the original game plus a patch. RetroAchievements keeps those
# patches in a public repository of its own, and names every one of them after
# the game it belongs to - `11278-GT2-CombinedDisc.zip` is for game 11278. So
# one listing of that repository is a map from game to patch.
#
# Read whole, once, and kept for a week like the console lists: it is a single
# request that answers for every game at once, and GitHub is strict about how
# often an unauthenticated caller may ask.
PATCH_TREE = ("https://api.github.com/repos/RetroAchievements/RAPatches"
              "/git/trees/main?recursive=1")
PATCH_RAW = "https://github.com/RetroAchievements/RAPatches/raw/main/"
_PATCH_ID_RE = re.compile(r"^(\d{2,6})-")

_patch_memory: dict[int, list[str]] | None = None
_patch_lock = threading.Lock()


def _cache_file(console_id: int):
    return user("retro") / f"console_{console_id}.json"


def _fetch(console_id: int) -> dict[str, str] | None:
    """{game id: title} for one console, or None if it couldn't be had."""
    request = urllib.request.Request(
        LIST_URL.format(id=console_id), headers={"User-Agent": USER_AGENT})
    try:
        payload = json.loads(
            rapi.read(request, timeout=TIMEOUT).decode("utf-8", "replace"))
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


def match_keys(name: str) -> list[str]:
    """Every spelling of one title worth trying, in the order to try them.

    The name as it is first, then the same name with less of it insisted on:
    without the studio in front, without the build number, with its numerals
    as figures, without the spaces. Each is only reached when everything
    before it found nothing, so an alias can never take a match away from a
    game that is named outright.

    Public because the same ladder settles two different questions - which
    RetroAchievements game a file is, and which indexed game one of theirs is
    - and the two were never going to stay in step written out twice.
    """
    key = match_key(name)
    if len(key) < 2:
        return []
    plain = _unbranded(key)
    build = _unversioned(key)
    out: list[str] = []
    for candidate in (key, plain, build, _arabic(key),
                      _squashed(key), _squashed(plain), _squashed(build)):
        if candidate and candidate not in out:
            out.append(candidate)
    return out


def game_id(console: str, name: str) -> int:
    """The RetroAchievements game id for a file, or 0 if there isn't one."""
    console_id = CONSOLES.get((console or "").strip())
    if not console_id or not name:
        return 0
    keys = match_keys(name)
    if not keys:
        return 0
    index = _index(console_id)
    for candidate in keys:
        found = index.get(candidate)
        if found:
            return found
    return 0


def page_url(game_id_: int) -> str:
    return GAME_URL.format(id=int(game_id_))


def _fetch_patches() -> dict[int, list[str]] | None:
    """{game id: patch url} from the repository listing, or None if unread."""
    request = urllib.request.Request(
        PATCH_TREE, headers={"User-Agent": USER_AGENT,
                             "Accept": "application/vnd.github+json"})
    try:
        payload = json.loads(
            rapi.read(request, timeout=TIMEOUT).decode("utf-8", "replace"))
    except (urllib.error.URLError, OSError, ValueError, TimeoutError):
        return None
    except Exception:  # noqa: BLE001 - a bad answer must never break a page
        return None

    tree = payload.get("tree")
    if not isinstance(tree, list):
        return None

    found: dict[int, str] = {}
    for node in tree:
        if not isinstance(node, dict) or node.get("type") != "blob":
            continue
        path = str(node.get("path") or "")
        match = _PATCH_ID_RE.match(path.rsplit("/", 1)[-1])
        if not match:
            continue
        # Every one of them, not just the first. A game can have nineteen -
        # Zelda does - and they are whole translations and hacks rather than
        # variants of one thing, so keeping one and dropping the rest picks
        # for the user without telling them there was a choice.
        found.setdefault(int(match.group(1)), []).append(
            PATCH_RAW + urllib.parse.quote(path))
    for urls in found.values():
        urls.sort()
    return found or None


def patches() -> dict[int, list[str]]:
    """Every game that has a patch, mapped to all of the ones it has.

    Empty when the listing cannot be had, which reads the same as "no patch"
    and costs nothing: the entry simply isn't offered.
    """
    global _patch_memory  # noqa: PLW0603 - one map for the process
    with _patch_lock:
        if _patch_memory is not None:
            return _patch_memory

        found, stale = None, None
        path = user("retro") / "patches.json"
        try:
            with open(path, encoding="utf-8") as fh:
                saved = json.load(fh)
            age = time.time() - float(saved.get("at") or 0)
            limit = RETRY_AFTER if saved.get("failed") else FRESH
            # Written as a single string before a game could have several.
            kept = {int(k): ([v] if isinstance(v, str) else list(v))
                    for k, v in (saved.get("patches") or {}).items()}
            if age < limit:
                found = kept
            else:
                stale = kept or None
        except (OSError, ValueError, TypeError):
            pass

        if found is None:
            fetched = _fetch_patches()
            if fetched is None:
                found = stale or {}
                _write_patches(path, stale or {}, failed=True)
            else:
                found = fetched
                _write_patches(path, found, failed=False)

        _patch_memory = found
        return found


def _write_patches(path, found: dict[int, list[str]], failed: bool) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            json.dump({"at": time.time(), "failed": failed,
                       "patches": {str(k): v for k, v in found.items()}}, fh)
    except OSError:
        pass


def patch_label(url: str) -> str:
    """What to call a patch in a list of them: its name, without the plumbing.

    "1454-LegendofZelda-ModernClassic.zip" is meant to be read as "Modern
    Classic"; the number is the game id and says nothing to anyone.
    """
    name = urllib.parse.unquote(url.rsplit("/", 1)[-1])
    name = re.sub(r"^\d{2,6}-", "", name)
    return re.sub(r"\.(zip|7z|bps|ips|xdelta|vcdiff|ppf)$", "", name,
                  flags=re.I) or name


def patches_for(game_id_: int) -> list[str]:
    return patches().get(int(game_id_ or 0), [])


def lookup(items) -> dict:
    """Resolve a batch of {console, name} in one go, answers in the same order.

    The page asks for everything it is showing at once and remembers the
    answers, so opening a menu never has to wait for the network. The patches
    for whatever was found come back with them, for the same reason.
    """
    out: list[int] = []
    for item in items if isinstance(items, list) else []:
        if not isinstance(item, dict):
            out.append(0)
            continue
        out.append(game_id(str(item.get("console") or ""),
                           str(item.get("name") or "")))

    try:
        known = patches()
    except Exception:  # noqa: BLE001 - patches are a nicety, ids are not
        known = {}
    # Each game with the whole list of its patches, named the way a person
    # would recognise them rather than by their file paths.
    found = {str(i): [{"name": patch_label(u), "url": u} for u in known[i]]
             for i in set(out) if i and i in known}
    # What the built-in patcher can rewrite, by file type rather than by
    # console. It was by console once, on the assumption that a disc meant
    # rebuilding a disc; a raw image is just a long run of bytes and patches
    # like anything else. A .chd does not, which is why this is a list of
    # extensions and not a rule about consoles. Imported here because the
    # patcher is a leaf and importing it at module level would make this one.
    from romsrx import patcher
    # How much of each set the user has earned, for the games on this screen.
    # It rides along with the ids because the page asks for those once per
    # screenful anyway - a second round trip for the same list of games would
    # be a second round trip for nothing.
    try:
        earned = progress()
    except Exception:  # noqa: BLE001 - badges are a nicety, ids are not
        earned = {}
    mine = {str(i): earned[i] for i in set(out) if i and i in earned}
    return {"ids": out, "patches": found, "progress": mine,
            "patchExts": sorted({e.lstrip(".") for e
                                 in patcher.ROM_EXTS + patcher.DISC_EXTS}),
            # ...and which consoles a copy on this machine can be checked
            # against its set. Sent for the same reason as patchExts: the page
            # has to know which games to offer it for, and deciding that in two
            # places is how the two come to disagree.
            "verifyConsoles": rahash.supported_consoles()}


# -- how big a set is ------------------------------------------------------
# The one thing about every game on the site that can be had in bulk. One
# request per console returns every game that has a set, with how many
# achievements are in it and what they score - 932 PlayStation 2 games in
# under half a second - where a *time* is a request per game and ordering the
# whole catalogue by it would be twenty thousand of them.
#
# So this is the instant answer to "which of these is short", and it is worth
# being plain about what it is not: the number of achievements is a hint, not
# a duration. A twelve-achievement set can be a forty-hour RPG. It sorts a
# page in no time at all, and the medians above are what settle it.
#
# The same response also carries every accepted hash for every game, which is
# not used here - hashes() answers per game and carries the dump names with
# them, and a name is what a file nobody has downloaded yet must be matched
# on.
SIZES_URL = "https://retroachievements.org/API/API_GetGameList.php"
SIZES_LIFE = 7 * 24 * 3600      # a set gains achievements now and then

_sizes: dict[int, dict[int, dict]] = {}
_sizes_lock = threading.Lock()


def _sizes_file(console_id: int):
    return user("retro") / f"sizes_{console_id}.json"


def _fetch_sizes(console_id: int, key: str) -> dict[int, dict] | None:
    asked = urllib.parse.urlencode({"i": console_id, "f": 1, "h": 0, "y": key})
    request = urllib.request.Request(f"{SIZES_URL}?{asked}",
                                     headers={"User-Agent": USER_AGENT})
    try:
        listed = json.loads(
            rapi.read(request, timeout=90).decode("utf-8", "replace"))
    except Exception:  # noqa: BLE001 - a missing figure is not a failure
        return None
    if not isinstance(listed, list):
        return None

    out: dict[int, dict] = {}
    for row in listed:
        if not isinstance(row, dict):
            continue
        game = _number(row, "id", "ID")
        count = _number(row, "numAchievements", "NumAchievements") or 0
        if game and count:
            out[int(game)] = {"achievements": int(count),
                              "points": _number(row, "points", "Points") or 0}
    return out


def set_sizes(console: str) -> dict[int, dict]:
    """{game id: {achievements, points}} for a whole console, or {}."""
    from . import artwork  # noqa: PLC0415 - only this needs the key

    console_id = CONSOLES.get((console or "").strip())
    key = artwork.settings()["retroachievements"].get("api_key") or ""
    if not console_id or not key:
        return {}

    with _sizes_lock:
        if console_id in _sizes:
            return _sizes[console_id]

    found = None
    path = _sizes_file(console_id)
    try:
        with open(path, encoding="utf-8") as fh:
            saved = json.load(fh)
        if time.time() - float(saved.get("at") or 0) < SIZES_LIFE:
            found = {int(k): v for k, v in (saved.get("sizes") or {}).items()}
    except (OSError, ValueError, TypeError):
        found = None

    if found is None:
        found = _fetch_sizes(console_id, key)
        if found is None:
            return {}
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w", encoding="utf-8") as fh:
                json.dump({"at": time.time(),
                           "sizes": {str(k): v for k, v in found.items()}}, fh)
        except OSError:
            pass

    with _sizes_lock:
        _sizes[console_id] = found
    return found


def sizes(games) -> dict:
    """How big each of these games' sets is, keyed as /api/times keys them.

    Costs one request per console however many games are asked about, and
    nothing at all once that console has been asked about before - which is
    what makes this orderable on the spot where a time never can be.
    """
    asked = [one for one in (games if isinstance(games, list) else [])
             if isinstance(one, dict) and one.get("console") and one.get("name")]
    if not asked:
        return {"sizes": {}}

    out: dict[str, dict] = {}
    per_console: dict[str, dict[int, dict]] = {}
    for one in asked:
        console, name = str(one["console"]), str(one["name"])
        if console not in per_console:
            per_console[console] = set_sizes(console)
        table = per_console[console]
        if not table:
            continue
        try:
            game = game_id(console, name)
        except Exception:  # noqa: BLE001
            continue
        found = table.get(game) if game else None
        if found:
            out[f"{console}	{name}"] = {**found, "id": game}
    return {"sizes": out, "asked": len(asked)}


# -- how long a game takes ------------------------------------------------
# RetroAchievements times how long its players actually take, and publishes
# the median rather than the mean: a mean is wrecked by the one person who
# left the emulator running over a weekend, and by speedrunners at the other
# end. Three numbers per game - beaten, completed, mastered - each with the
# number of players it was taken from, because a median of four people is a
# different sort of fact from a median of two thousand.
#
# This one endpoint needs a key, which is the same Web API key artwork.py
# already asks for. Nothing here is offered until that is filled in.
#
# Asked one game at a time, on demand, when somebody presses the entry in the
# menu. Fetching it for a whole screenful the way the ids are fetched would be
# forty requests to answer a question nobody asked.
PROGRESS_URL = "https://retroachievements.org/API/API_GetGameProgression.php"
TIMES_LIFE = 14 * 24 * 3600      # medians move slowly; a fortnight is fine

_times: dict[int, tuple[float, dict]] = {}
_times_lock = threading.Lock()


def _number(data: dict, *names):
    """One field, however the site happens to be spelling it today.

    Their documentation says medianTimeToBeat and the site returns
    MedianTimeToBeat. Both are accepted rather than betting the feature on
    which of the two is current.
    """
    for name in names:
        for spelling in (name, name[0].upper() + name[1:]):
            value = data.get(spelling)
            if value not in (None, "", 0):
                try:
                    return int(value)
                except (TypeError, ValueError):
                    return None
    return None


def priced(game: int) -> bool:
    """Whether this game's times are already known, so no request is needed.

    Uses the same freshness as how_long, so the two cannot disagree about what
    counts as already answered.
    """
    with _times_lock:
        found = _times.get(int(game or 0))
    return bool(found and time.time() - found[0] < TIMES_LIFE)


def how_long(console: str, name: str, game: int = 0) -> dict:
    """Median times for one game, or a reason there aren't any.

    `game` is the RetroAchievements id when the caller already has it, which
    the page always does - it looks the ids up for everything on screen as the
    screen is drawn. Falling back to the console and filename keeps this usable
    from anywhere else.

    Never raises. Every failure is a `reason` the page can put on screen,
    because this is opened deliberately by somebody who wants an answer, and
    "nothing happened" is the one response that tells them nothing.
    """
    from . import artwork  # noqa: PLC0415 - only this function needs the key

    key = artwork.settings()["retroachievements"].get("api_key") or ""
    if not key:
        return {"ok": False, "reason": "nokey"}

    game = game or game_id(console, name)
    if not game:
        return {"ok": False, "reason": "noset"}

    with _times_lock:
        cached = _times.get(game)
        if cached and time.time() - cached[0] < TIMES_LIFE:
            return cached[1]

    asked = {"i": str(game), "y": key}
    request = urllib.request.Request(
        f"{PROGRESS_URL}?{urllib.parse.urlencode(asked)}",
        headers={"User-Agent": USER_AGENT})
    try:
        data = json.loads(
            rapi.read(request, timeout=30).decode("utf-8", "replace"))
    except urllib.error.HTTPError as exc:
        if exc.code in (401, 403):
            return {"ok": False, "reason": "badkey"}
        # A game they do not have is not the site being down, and saying so
        # sends somebody off to check their connection for nothing.
        return {"ok": False,
                "reason": "noset" if exc.code == 404 else "unreachable"}
    except Exception:  # noqa: BLE001 - offline, timeout, nonsense JSON
        return {"ok": False, "reason": "unreachable"}
    if not isinstance(data, dict):
        return {"ok": False, "reason": "unreachable"}

    # Hardcore throughout, and only two numbers.
    #
    # RetroAchievements publishes each median twice, once for players using
    # save states and rewind and once for those not. The softcore figure
    # measures how long a game takes when you can undo your mistakes, which is
    # a number about the emulator rather than about the game - so the hardcore
    # median is the one carried here, and the softcore ones and the separate
    # "complete every achievement in softcore" figure are dropped rather than
    # fetched and ignored.
    #
    # Mastery is hardcore by definition - that is what the word means there -
    # so it needs no hardcore variant of its own.
    # The same response carries every achievement in the set, so what the site
    # prints at the top of a game's page - how many there are, what they are
    # worth, and the ratio between the two - is arithmetic rather than a second
    # request.
    #
    # RetroRatio is the site's own measure of how hard a set is: the white
    # "RetroPoints" a set awards divided by its plain points. A set nobody
    # struggles with sits near x1; Super Mario 64 is x2.88, which is the figure
    # its page shows.
    listed = data.get("Achievements") or data.get("achievements") or []
    if isinstance(listed, dict):            # keyed by id in some responses
        listed = list(listed.values())
    listed = [a for a in listed if isinstance(a, dict)]
    points = sum(_number(a, "points") or 0 for a in listed)
    retro_points = sum(_number(a, "trueRatio") or 0 for a in listed)

    out = {
        "ok": True,
        "id": game,
        "title": str(data.get("Title") or data.get("title") or ""),
        "url": GAME_URL.format(id=game),
        "players": _number(data, "numDistinctPlayers"),
        # Seconds, which is what they send. The page does the arithmetic.
        "beat": _number(data, "medianTimeToBeatHardcore"),
        "beatFrom": _number(data, "timesUsedInHardcoreBeatMedian"),
        "master": _number(data, "medianTimeToMaster"),
        "masterFrom": _number(data, "timesUsedInMasteryMedian"),
        "achievements": _number(data, "numAchievements") or len(listed) or None,
        "points": points or None,
        "retropoints": retro_points or None,
        "ratio": round(retro_points / points, 2) if points else None,
    }
    # A game nobody has finished in hardcore still has a set worth describing,
    # so the times going missing is a note rather than a dead end. Only when
    # there is nothing at all to show is this a failure.
    out["notimes"] = not (out["beat"] or out["master"])
    if out["notimes"] and not out["achievements"]:
        out = {"ok": False, "reason": "notimes", "id": game,
               "title": out["title"], "url": out["url"]}

    with _times_lock:
        _times[game] = (time.time(), out)
    return out


# -- the pictures on a game's page ----------------------------------------
# Their in-game shot, for the preview panel. The same
# endpoint artwork.py asks for box art, so the answer is kept here rather than
# fetched twice: a preview wants all three pictures and asking for them one at
# a time would be three requests for one panel.
GAME_API = "https://retroachievements.org/API/API_GetGame.php"
MEDIA = "https://media.retroachievements.org"
IMAGE_LIFE = 30 * 24 * 3600

# What they serve when a game has no picture of that kind. Showing it would
# put the same grey square in every preview.
BLANK_IMAGES = frozenset({"000000", "000001", "000002"})

_images: dict[int, tuple[float, list]] = {}
_images_lock = threading.Lock()


def images(console: str, name: str, game: int = 0) -> list[str]:
    """The in-game shot from a game's RetroAchievements page."""
    from . import artwork  # noqa: PLC0415

    key = artwork.settings()["retroachievements"].get("api_key") or ""
    if not key:
        return []
    game = game or game_id(console, name)
    if not game:
        return []

    with _images_lock:
        found = _images.get(game)
        if found and time.time() - found[0] < IMAGE_LIFE:
            return found[1]

    asked = urllib.parse.urlencode({"i": str(game), "y": key})
    request = urllib.request.Request(f"{GAME_API}?{asked}",
                                     headers={"User-Agent": USER_AGENT})
    try:
        data = json.loads(
            rapi.read(request, timeout=30).decode("utf-8", "replace"))
    except Exception:  # noqa: BLE001 - a preview is never worth an exception
        return []
    if not isinstance(data, dict):
        return []

    # In-game only. Their ImageTitle is a picture of the title screen, which
    # libretro also keeps and which said nothing a box has not said better -
    # having both was how the same menu ended up in a preview twice.
    out = []
    for field in ("ImageIngame",):
        path = str(data.get(field) or data.get(field[0].lower() + field[1:]) or "")
        if path.startswith("/") and (
                path.rsplit("/", 1)[-1].split(".")[0] not in BLANK_IMAGES):
            out.append(f"{MEDIA}{path}")

    with _images_lock:
        _images[game] = (time.time(), out)
    return out


# -- how much of each set you have earned ---------------------------------
# The one thing here that is about the person rather than the game. Everything
# else this module asks for is the same answer for everybody; this is yours,
# and so it is the only part that needs a username as well as a key.
#
# One request covers a whole library. RetroAchievements will list every game a
# user has ever played, five hundred at a time, with how many of each set they
# have - so the alternative, asking per game, would be four hundred requests to
# paint one shelf.
PROGRESS_API = "https://retroachievements.org/API/API_GetUserCompletionProgress.php"
PROGRESS_PAGE = 500          # their maximum
PROGRESS_PAGES = 8           # ...so up to 4,000 games, which is a long career
PROGRESS_LIFE = 15 * 60      # earned an achievement? it shows within a quarter hour

_progress: tuple[float, dict] | None = None
_progress_lock = threading.Lock()


def _progress_page(user_name: str, key: str, offset: int) -> dict | None:
    asked = urllib.parse.urlencode({"u": user_name, "y": key,
                                    "c": PROGRESS_PAGE, "o": offset})
    request = urllib.request.Request(f"{PROGRESS_API}?{asked}",
                                     headers={"User-Agent": USER_AGENT})
    try:
        found = json.loads(
            rapi.read(request, timeout=45).decode("utf-8", "replace"))
    except Exception:  # noqa: BLE001 - a shelf without badges is still a shelf
        return None
    return found if isinstance(found, dict) else None


def progress(refresh: bool = False) -> dict[int, dict]:
    """{game id: {earned, hardcore, total}} for the signed-in user, or {}.

    Empty whenever there is no username - which is the default - so nothing
    about the library changes for somebody who has only filled in a key for the
    artwork.
    """
    global _progress  # noqa: PLW0603
    from . import artwork  # noqa: PLC0415

    conf = artwork.settings()["retroachievements"]
    key, who = conf.get("api_key") or "", conf.get("username") or ""
    if not key or not who:
        return {}

    with _progress_lock:
        if _progress and not refresh and time.time() - _progress[0] < PROGRESS_LIFE:
            return _progress[1]

    found: dict[int, dict] = {}
    offset = 0
    for _ in range(PROGRESS_PAGES):
        page = _progress_page(who, key, offset)
        if page is None:
            # A failed fetch keeps whatever was already known rather than
            # blanking every badge on the shelf.
            with _progress_lock:
                return _progress[1] if _progress else {}
        rows = page.get("Results") or page.get("results") or []
        for row in rows if isinstance(rows, list) else []:
            if not isinstance(row, dict):
                continue
            game = _number(row, "gameID") or _number(row, "gameId")
            total = _number(row, "maxPossible") or 0
            if not game or not total:
                continue
            found[int(game)] = {
                "earned": _number(row, "numAwarded") or 0,
                "hardcore": _number(row, "numAwardedHardcore") or 0,
                "total": int(total),
            }
        offset += len(rows) if isinstance(rows, list) else 0
        try:
            if offset >= int(page.get("Total") or page.get("total") or 0):
                break
        except (TypeError, ValueError):
            break
        if not rows:
            break

    with _progress_lock:
        _progress = (time.time(), found)
    return found


# -- which copies of a game a set actually accepts -------------------------
# A set is tied to particular dumps, not to a title: RetroAchievements knows a
# game by the hash of the ROM, and the download that works is the one whose
# hash is in their list. The site publishes that list per game, with the name
# each hash was dumped under - which is the same No-Intro or Redump name the
# preservation sets on archive.org use, because both sides are naming the same
# dumps.
#
# So the question "will this download earn achievements" can be answered
# before downloading a gigabyte to find out, by matching names. It is a name
# match and nothing more - the only certain answer is the hash of the file
# itself, which nobody has until it is on the disk - so the page says so, and
# the matching below is deliberately strict: a name that differs is reported as
# not in the list rather than talked into being close enough.
HASHES_API = "https://retroachievements.org/API/API_GetGameHashes.php"
HASHES_LIFE = 7 * 24 * 3600      # a set gains a hash now and then, not hourly

_hashes: dict[int, tuple[float, list]] = {}
_hashes_lock = threading.Lock()


# Sources that are themselves RetroAchievements sets.
#
# The name check below is strict on purpose and stays that way, but it is not
# the only evidence there is. Some of the items indexed here *are* the site's
# own curated sets - "RetroAchievements Game Boy", "RetroAchievements v5
# (Jaguar)" and sixty-odd others - and a file from one of those is an accepted
# dump by construction, whatever its name has been through on the way into an
# archive listing.
#
# Reported as its own kind of evidence rather than folded into the name match.
# "This is the dump the set was built from" and "this came out of the site's
# own set" are both good answers and they are not the same answer, and saying
# so is the difference between a check somebody can trust and a tick.
_RA_SOURCE_RE = re.compile(r"retro\s*achievements", re.I)


def from_ra_set(source: str) -> bool:
    """Whether a file came from one of RetroAchievements' own collections."""
    return bool(_RA_SOURCE_RE.search(str(source or "")))


def _file_key(name: str) -> str:
    """A filename folded just enough to compare two spellings of one dump.

    Case and spacing only. Everything that tells two dumps apart - the region,
    the revision, the disc, the language list - is left exactly as it is, since
    this is the difference between "this download works" and "this download is
    the European one and does not".

    The extension goes twice over, for the '.bin.gz' pairs, because the two
    sides name the same dump with different wrappers: RetroAchievements lists
    the ROM as '.md' and archive.org serves it inside a '.zip'.
    """
    trimmed = _EXT_RE.sub("", _EXT_RE.sub("", str(name or "")))
    return " ".join(trimmed.lower().split())


def hashes(game: int) -> list[dict]:
    """Every dump one set accepts: [{name, md5, labels, patch}]."""
    from . import artwork  # noqa: PLC0415

    key = artwork.settings()["retroachievements"].get("api_key") or ""
    game = int(game or 0)
    if not key or not game:
        return []

    with _hashes_lock:
        found = _hashes.get(game)
        if found and time.time() - found[0] < HASHES_LIFE:
            return found[1]

    asked = urllib.parse.urlencode({"i": str(game), "y": key})
    request = urllib.request.Request(f"{HASHES_API}?{asked}",
                                     headers={"User-Agent": USER_AGENT})
    try:
        data = json.loads(
            rapi.read(request, timeout=30).decode("utf-8", "replace"))
    except Exception:  # noqa: BLE001 - handled as "no list" by the caller
        return []

    rows = []
    listed = (data.get("Results") or data.get("results") or []) \
        if isinstance(data, dict) else []
    for row in listed if isinstance(listed, list) else []:
        if not isinstance(row, dict):
            continue
        name = _text(row, "name")
        if not name:
            continue
        labels = row.get("Labels") or row.get("labels") or []
        if isinstance(labels, str):
            labels = [part.strip() for part in labels.split(",") if part.strip()]
        rows.append({
            "name": name,
            # "MD5", in full capitals - the same trap as the "ID" in
            # _one_achievement, and _text only tries a name and that name with
            # its first letter raised. Asking by name alone read every dump in
            # every set as having no hash, which the feature that compares
            # hashes reported as "this game's set lists nothing".
            "md5": _text(row, "md5", "MD5"),
            "labels": [str(one) for one in labels if one],
            # Set for the hacks and translations, whose "dump" is the original
            # plus a patch. Worth passing on: it is the difference between a
            # file that works as it is and one that needs a step first.
            "patch": _text(row, "patchUrl"),
        })

    with _hashes_lock:
        _hashes[game] = (time.time(), rows)
    return rows


def supported(files: list) -> dict:
    """Which of these copies RetroAchievements' sets are dumped from.

    `files` is what one search result is showing: [{filename, console}]. One
    card is one game and can still span half a dozen systems, and each of those
    is a set of its own with its own list of dumps - so a console at a time,
    every file checked against the list for the machine it is actually for. A
    Mega Drive dump has no business being compared against the Game Gear set.

    The answer keeps the files in the order they were asked about and spelled
    exactly as they were sent, so the page can mark its own rows without
    matching anything a second time and possibly differently.
    """
    from . import artwork  # noqa: PLC0415

    key = artwork.settings()["retroachievements"].get("api_key") or ""
    if not key:
        return {"ok": False, "reason": "nokey"}

    asked = [f for f in (files if isinstance(files, list) else [])
             if isinstance(f, dict) and f.get("filename")]
    if not asked:
        return {"ok": False, "reason": "noset"}

    # One list per console, looked up from the first file for that console and
    # then reused for the rest of them.
    maps: dict[str, dict[str, dict]] = {}
    sets: list[dict] = []
    for console in dict.fromkeys(str(f.get("console") or "") for f in asked):
        first = next(str(f["filename"]) for f in asked
                     if str(f.get("console") or "") == console)
        game = game_id(console, first)
        listed = hashes(game) if game else []
        if not listed:
            continue
        # Built once per console rather than scanned per file: a Redump set
        # lists several hundred dumps and a card can hold dozens of files.
        by_key: dict[str, dict] = {}
        for row in listed:
            by_key.setdefault(_file_key(row["name"]), row)
        maps[console] = by_key
        sets.append({"console": console, "id": game, "listed": len(listed),
                     "url": GAME_URL.format(id=game)})

    if not sets:
        return {"ok": False, "reason": "noset"}

    out = []
    for one in asked:
        filename = str(one["filename"])
        hit = maps.get(str(one.get("console") or ""), {}).get(_file_key(filename))
        curated = from_ra_set(one.get("source"))
        out.append({
            "filename": filename,
            "console": str(one.get("console") or ""),
            # Sent back so the page can tell one answer from another. A card
            # can hold the same filename four times over - "Spider-Man 2
            # (USA).zip" exists on GameCube, DS, PSP and PlayStation 2, and
            # three times on the PS2 alone from different sources - and a
            # answer keyed on the name alone loses all but the last of them.
            "source": str(one.get("source") or ""),
            "ok": bool(hit),
            # Named separately from `ok`: a copy out of the site's own set is
            # very likely to work and has not been checked against anything.
            "raSource": curated,
            "matched": hit["name"] if hit else "",
            "labels": hit["labels"] if hit else [],
            "patch": hit["patch"] if hit else "",
        })

    return {
        "ok": True,
        # Every console on this card that has a set, so the page can say what
        # was actually checked - and which of them had nothing to check
        # against, since a card whose Mega Drive copies matched and whose Game
        # Gear ones were never looked at is two different answers.
        "sets": sets,
        "consoles": len(dict.fromkeys(row["console"] for row in out)),
        "total": sum(one["listed"] for one in sets),
        "matched": sum(1 for row in out if row["ok"]),
        # Copies from the site's own collections that the name check did not
        # also catch - the ones the strict comparison was missing.
        "curated": sum(1 for row in out if row["raSource"] and not row["ok"]),
        "files": out,
    }


# -- and which copy on this machine a set actually accepts -----------------
# supported() answers before the download, by name, and says so. This answers
# afterwards, from the file itself, and is the certain version of the same
# question: rahash.py works out the number RetroAchievements knows the dump by
# and it is either in the set's list or it is not.
#
# The verdicts are a closed list, and the page has a sentence for each. The
# distinction that matters most is between `nomatch` and `unsupported`: the
# first says this copy will not earn achievements, which is a strong claim
# about somebody's game, and the second says nothing at all was checked. A
# disc that could not be hashed must never read as a cartridge that failed.
VERDICTS = ("match", "nomatch", "noset", "unsupported", "ambiguous",
            "archive", "notrom", "unreadable")


# -- and remembering what was found out ------------------------------------
# The hashes survive a restart; without this the verdicts did not, so the
# shelf came back blank every time the app was opened and the only way to get
# the marks back was to sweep the whole library again. Nothing was recomputed
# by that sweep - every hash was already cached - but it still had to be asked
# for, which made a feature that knew the answer look like one that had
# forgotten it.
#
# Kept beside the hashes and stamped the same way, so the two agree about when
# a file has become a different file. A verdict also goes stale for a reason a
# hash never does - a set gains a dump, and yesterday's `nomatch` becomes
# today's `match` - so each carries the day it was reached, and the page is
# told how old the answer is rather than being left to assume it is current.
VERDICT_FILE = user("retro") / "verified.json"
VERDICT_LIFE = 30 * 24 * 3600      # after a month, worth checking again

_verdicts: dict[str, dict] | None = None
_verdicts_dirty = False
_verdicts_lock = threading.Lock()

# What is worth keeping out of a row. The rest - the console, the name - the
# page already has for every game on its shelf.
_KEPT = ("verdict", "id", "url", "md5", "matched", "labels", "patch")

# ...and which verdicts are worth keeping at all. Only the two that came from
# reading the game: they are the ones the shelf draws a mark for, and the ones
# that cost something to reach. A disc is ruled out by a dictionary lookup and
# a game with no set by an index already on disk - writing those down would
# treble the size of this file to save no work.
_WORTH_KEEPING = frozenset({"match", "nomatch"})


def _load_verdicts() -> dict[str, dict]:
    global _verdicts  # noqa: PLW0603
    if _verdicts is None:
        try:
            with open(VERDICT_FILE, encoding="utf-8") as fh:
                found = json.load(fh)
            _verdicts = found if isinstance(found, dict) else {}
        except (OSError, ValueError):
            _verdicts = {}
    return _verdicts


def _remember(rows: list[dict]) -> None:
    """Keep what a sweep worked out, for the next time the app is opened."""
    global _verdicts_dirty  # noqa: PLW0603

    now = int(time.time())
    with _verdicts_lock:
        kept = _load_verdicts()
        for row in rows:
            path = row.get("path")
            if not path or row.get("verdict") not in _WORTH_KEEPING:
                # A game that used to match and now doesn't is a row that has
                # to go, not one to leave standing at its old answer.
                if path:
                    kept.pop(path, None)
                continue
            size, when = rahash.stamp(Path(path))
            if not size:                    # gone between hashing and now
                kept.pop(path, None)
                continue
            kept[path] = {name: row.get(name) for name in _KEPT}
            kept[path].update({"size": size, "mtime": when, "at": now})
        _verdicts_dirty = True


def _save_verdicts() -> None:
    global _verdicts_dirty  # noqa: PLW0603
    with _verdicts_lock:
        if not _verdicts_dirty or _verdicts is None:
            return
        payload = dict(_verdicts)
        _verdicts_dirty = False
    try:
        VERDICT_FILE.parent.mkdir(parents=True, exist_ok=True)
        temporary = VERDICT_FILE.with_suffix(".tmp")
        with open(temporary, "w", encoding="utf-8") as fh:
            json.dump(payload, fh)
        os.replace(temporary, VERDICT_FILE)
    except OSError:
        pass


def verdicts() -> dict:
    """Every verdict still worth showing, for a page that has just opened.

    Costs nothing: no network, no hashing, no reading of the games themselves
    beyond a stat apiece. A file that has changed since it was checked drops
    out here rather than being reported against its old answer.
    """
    global _verdicts_dirty  # noqa: PLW0603

    now = time.time()
    rows, gone = [], []
    with _verdicts_lock:
        kept = _load_verdicts()
        for path, saved in kept.items():
            if not isinstance(saved, dict) or not saved.get("verdict"):
                gone.append(path)
                continue
            size, when = rahash.stamp(Path(path))
            if not size:                    # deleted, moved, or on a drive
                gone.append(path)           # that isn't plugged in
                continue
            if size != saved.get("size") or when != saved.get("mtime"):
                gone.append(path)           # a different file under one name
                continue
            row = {name: saved.get(name) for name in _KEPT}
            row["path"] = path
            row["labels"] = row.get("labels") or []
            # How long ago, in days, so the page can say "checked last month"
            # rather than implying the answer was reached just now.
            row["age"] = int((now - float(saved.get("at") or 0)) / 86400)
            row["stale"] = (now - float(saved.get("at") or 0)) > VERDICT_LIFE
            rows.append(row)
        for path in gone:
            kept.pop(path, None)
        if gone:
            _verdicts_dirty = True

    _save_verdicts()
    return {"ok": True, "rows": rows}


# How many files are hashed at once. Reading a cartridge is disk rather than
# thought, so this is not about cores - it is about keeping several reads in
# flight while each waits its turn at the drive. Small on purpose: a sweep is
# a background job and should not make the machine feel busy.
VERIFY_WORKERS = 4


def _plan(item: dict, sets: dict[int, dict]) -> dict:
    """Everything about one file that can be settled without reading it.

    Deliberately separate from the hashing. This part asks the network - which
    game is this, and what dumps does its set accept - and the network is
    paced, so it happens one at a time; the hashing that follows is disk and
    happens several at once. Doing both in one pass would have put paced calls
    inside the pool, where they would queue behind each other anyway.
    """
    console = str(item.get("console") or "")
    name = str(item.get("name") or "")
    row = {"path": str(item.get("path") or ""), "console": console,
           "name": name, "id": 0, "url": "", "md5": "", "matched": "",
           "labels": [], "patch": "", "verdict": "noset"}

    if not rahash.scheme(console):
        row["verdict"] = "unsupported"
        return row

    game = game_id(console, name)
    if not game:
        return row
    row["id"] = game
    row["url"] = GAME_URL.format(id=game)

    listed = sets.get(game)
    if listed is None:
        listed = {}
        for one in hashes(game):
            if one.get("md5"):
                listed.setdefault(str(one["md5"]).lower(), one)
        sets[game] = listed
    if not listed:
        return row

    row["verdict"] = ""            # still to be settled by the hash
    return row


def _settle(row: dict, sets: dict[int, dict]) -> None:
    """Read the file and say what it is, in place."""
    digest, reason = rahash.md5(row["path"], row["console"])
    if not digest:
        row["verdict"] = reason if reason in VERDICTS else "unreadable"
        return
    row["md5"] = digest
    hit = (sets.get(row["id"]) or {}).get(digest)
    row["verdict"] = "match" if hit else "nomatch"
    if hit:
        row["matched"] = hit.get("name") or ""
        row["labels"] = hit.get("labels") or []
        row["patch"] = hit.get("patch") or ""


def verify(items, progress=None, stop=None) -> dict:
    """Check copies on this machine against the sets they belong to.

    `items` is [{path, console, name}] - what the library page already holds
    for every game on the shelf. Answers come back in the same order, whatever
    order they were worked out in.

    `progress(done, total)` is called as it goes and `stop()` is asked whether
    to give up, so the whole library can be swept in the background and
    cancelled: this reads every byte of every cartridge it is given, which is
    minutes of disk on a large shelf and is not something to start without a
    way out of.
    """
    from . import artwork  # noqa: PLC0415 - only this function needs the key

    if not artwork.settings()["retroachievements"].get("api_key"):
        return {"ok": False, "reason": "nokey"}

    asked = [one for one in (items if isinstance(items, list) else [])
             if isinstance(one, dict) and one.get("path")]
    if not asked:
        return {"ok": False, "reason": "nothing"}

    # First pass: what each file is, and what its set accepts. Sequential,
    # and stop() is asked once per file here - so calling off a sweep stops it
    # before the expensive half rather than partway through it.
    sets: dict[int, dict] = {}          # game id -> {md5: the dump it names}
    rows: list[dict] = []
    for item in asked:
        if stop is not None and stop():
            break
        try:
            rows.append(_plan(item, sets))
        except Exception:  # noqa: BLE001 - one bad entry cannot end the sweep
            rows.append({"path": str(item.get("path") or ""),
                         "console": str(item.get("console") or ""),
                         "name": str(item.get("name") or ""),
                         "id": 0, "url": "", "md5": "", "matched": "",
                         "labels": [], "patch": "", "verdict": "unreadable"})

    done = 0

    def tick() -> None:
        nonlocal done
        done += 1
        if progress is not None:
            progress(done, len(asked))

    # Anything already settled - a disc, a game with no set - is counted now,
    # so the bar moves through those instantly rather than sitting still while
    # the reading starts.
    todo = []
    for row in rows:
        if row["verdict"]:
            tick()
        else:
            todo.append(row)

    def one(row: dict) -> None:
        try:
            _settle(row, sets)
        except Exception:  # noqa: BLE001 - one bad file cannot end the sweep
            row["verdict"] = "unreadable"

    if todo:
        with concurrent.futures.ThreadPoolExecutor(
                max_workers=VERIFY_WORKERS) as pool:
            for _ in pool.map(one, todo):
                tick()

    # Written out once at the end rather than after every file: a sweep of two
    # thousand games would otherwise be two thousand rewrites of the same
    # growing file.
    rahash.flush()
    _remember(rows)
    _save_verdicts()

    counts = {name: 0 for name in VERDICTS}
    for row in rows:
        counts[row["verdict"]] = counts.get(row["verdict"], 0) + 1
    return {"ok": True, "rows": rows, "counts": counts,
            "checked": len(rows), "asked": len(asked)}


# -- the achievements themselves ------------------------------------------
# Everything above answers "how much of this set have you got". This answers
# "which ones", which is the question somebody actually acts on: a set is 40
# things to do, and the useful view is the ones still to do - especially the
# missable ones, which are the reason people read an achievement list before
# starting rather than after finishing.
#
# Two endpoints, because only one of them is about you. With a username the
# site will say which of these you have unlocked and when; without one there is
# still a set to list, so the list is shown with nothing marked rather than not
# shown at all. The page says which of the two it is looking at.
#
# Asked for by pressing a button, never as part of drawing something. One game
# has dozens of achievements and every one of them has a badge to fetch, so
# this is a page's worth of loading on its own and is not something to do to
# somebody who only wanted to know how long the game takes.
USER_GAME_API = ("https://retroachievements.org/API/"
                 "API_GetGameInfoAndUserProgress.php")
GAME_EXTENDED_API = "https://retroachievements.org/API/API_GetGameExtended.php"
ACHIEVEMENT_URL = "https://retroachievements.org/achievement/{id}"
BADGE_URL = f"{MEDIA}/Badge/{{badge}}.png"

# Short, because this is the one thing here that changes while you play. A
# quarter of an hour matches the progress figures; the refresh button is for
# "I just earned that one" and skips this entirely.
ACHIEVEMENTS_LIFE = 15 * 60

# -- keeping a set between sessions ----------------------------------------
# The list above is held for a quarter of an hour in memory and nowhere else,
# which means the achievement panel is empty on a train and empty again the
# moment RetroAchievements is having a bad afternoon. A set is the same list
# of things to do whether or not the site can be reached, so it is written
# down.
#
# The same file answers a second question for free. A set gets revised - the
# author adds achievements, or reworks what they are worth - and that is worth
# knowing, because a revision can take a mastery away. Comparing what came
# back today against what was stored is the whole of the detection, so the
# cache and the ledger are one thing.
#
# Written per game rather than as one growing file: a career is thousands of
# sets and only ever one of them is being looked at.
SETS_DIR = user("retro") / "sets"


def _set_file(game: int):
    return SETS_DIR / f"{int(game)}.json"


def _remember_set(game: int, out: dict, who: str) -> dict | None:
    """Store a set, and say how it differs from the one stored before.

    The unlock marks belong to whoever was signed in, so the username is kept
    with them - a cached set is only ever handed back to the person it was
    fetched for.
    """
    was = None
    path = _set_file(game)
    try:
        with open(path, encoding="utf-8") as fh:
            saved = json.load(fh)
        if isinstance(saved, dict) and saved.get("user", "") == who:
            was = saved.get("set")
    except (OSError, ValueError):
        was = None

    try:
        SETS_DIR.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(".tmp")
        with open(temporary, "w", encoding="utf-8") as fh:
            json.dump({"at": int(time.time()), "user": who, "set": out}, fh)
        os.replace(temporary, path)
    except OSError:
        pass

    if not was:
        return None
    # Only the two figures that describe the set itself. What you have earned
    # changes constantly and is not a revision.
    if (was.get("total") == out.get("total")
            and was.get("points") == out.get("points")):
        return None
    return {"total": was.get("total") or 0, "points": was.get("points") or 0}


def _stored_set(game: int, who: str) -> dict | None:
    """The last set kept for this game, for a page with no connection."""
    try:
        with open(_set_file(game), encoding="utf-8") as fh:
            saved = json.load(fh)
    except (OSError, ValueError):
        return None
    if not isinstance(saved, dict) or saved.get("user", "") != who:
        return None
    out = saved.get("set")
    if not isinstance(out, dict) or not out.get("achievements"):
        return None
    # Said plainly, because every unlock in it is as old as the file: the page
    # shows the date rather than implying this is how things stand now.
    return {**out, "offline": True, "storedAt": int(saved.get("at") or 0)}


_achievements: dict[int, tuple[float, dict]] = {}
_achievements_lock = threading.Lock()


def _achievement_rows(data: dict) -> list[dict]:
    """Their achievements, however this endpoint happens to hand them over."""
    listed = data.get("Achievements") or data.get("achievements") or []
    if isinstance(listed, dict):        # keyed by id, which is the usual shape
        listed = list(listed.values())
    return [a for a in listed if isinstance(a, dict)]


def _text(row: dict, *names: str) -> str:
    for name in names:
        for spelling in (name, name[0].upper() + name[1:]):
            value = row.get(spelling)
            if value not in (None, ""):
                return str(value)
    return ""


def _one_achievement(row: dict) -> dict | None:
    # "ID", not "Id": _number tries a name and that name with its first letter
    # capitalised, and this is the one field the site spells in full capitals.
    # Getting it wrong drops every achievement in the set for want of an id.
    ident = _number(row, "id", "ID")
    if not ident:
        return None
    badge = _text(row, "badgeName", "badgeURL")
    # Both dates are sent only when there is a username, and only for the ones
    # you have. Hardcore is the one the rest of this app counts, but a softcore
    # unlock is still an unlock and saying so is more honest than a blank.
    earned = _text(row, "dateEarned")
    hardcore = _text(row, "dateEarnedHardcore")
    return {
        "id": int(ident),
        "title": _text(row, "title"),
        "description": _text(row, "description"),
        "points": _number(row, "points") or 0,
        "retropoints": _number(row, "trueRatio") or 0,
        # What the site calls the badge's name is a number; the two pictures
        # are that number and that number with _lock on the end.
        "badge": BADGE_URL.format(badge=badge) if badge else "",
        "badgeLocked": BADGE_URL.format(badge=f"{badge}_lock") if badge else "",
        "url": ACHIEVEMENT_URL.format(id=int(ident)),
        # "missable", "progression", "win_condition", or nothing at all. The
        # first is the one worth knowing before you start.
        "type": _text(row, "type").lower(),
        "unlocked": bool(earned or hardcore),
        "hardcore": bool(hardcore),
        "date": hardcore or earned,
        "awarded": _number(row, "numAwarded") or 0,
        "awardedHardcore": _number(row, "numAwardedHardcore") or 0,
        "order": _number(row, "displayOrder") or 0,
    }


# -- what people said about one achievement -------------------------------
# The comment thread from the achievement's own page. Worth having in here
# because it is where the practical knowledge is: which trigger is fussy, what
# order to do things in, that one of them is missable in a way the description
# does not spell out.
#
# Two kinds of row come back mixed together. Most threads on a quiet
# achievement are the site's own bookkeeping - "X promoted this to the Core
# set" - posted as the user "Server", and those are marked here rather than
# dropped: they are the achievement's history, which is occasionally the very
# thing somebody is looking for, and a reader can tell them apart at a glance
# once they are labelled.
#
# Asked for one achievement at a time, when somebody opens that row. A set of
# forty would be forty requests, which is exactly why this is not part of the
# list itself.
COMMENTS_API = "https://retroachievements.org/API/API_GetComments.php"
COMMENTS_LIFE = 60 * 60
COMMENTS_MAX = 50

_comments: dict[int, tuple[float, list]] = {}
_comments_lock = threading.Lock()


def comments(achievement: int, refresh: bool = False) -> dict:
    """The comment thread on one achievement, newest last as the site shows it."""
    from . import artwork  # noqa: PLC0415

    key = artwork.settings()["retroachievements"].get("api_key") or ""
    if not key:
        return {"ok": False, "reason": "nokey"}
    achievement = int(achievement or 0)
    if not achievement:
        return {"ok": False, "reason": "noset"}

    if not refresh:
        with _comments_lock:
            cached = _comments.get(achievement)
            if cached and time.time() - cached[0] < COMMENTS_LIFE:
                return {"ok": True, "id": achievement, "comments": cached[1]}

    asked = urllib.parse.urlencode({"i": str(achievement), "t": "2",
                                    "c": str(COMMENTS_MAX), "y": key})
    request = urllib.request.Request(f"{COMMENTS_API}?{asked}",
                                     headers={"User-Agent": USER_AGENT})
    try:
        data = json.loads(
            rapi.read(request, timeout=30).decode("utf-8", "replace"))
    except urllib.error.HTTPError as exc:
        if exc.code in (401, 403):
            return {"ok": False, "reason": "badkey"}
        return {"ok": False, "reason": "unreachable"}
    except Exception:  # noqa: BLE001
        return {"ok": False, "reason": "unreachable"}
    if not isinstance(data, dict):
        return {"ok": False, "reason": "unreachable"}

    rows = []
    for row in data.get("Results") or data.get("results") or []:
        if not isinstance(row, dict):
            continue
        text = _text(row, "commentText")
        if not text:
            continue
        who = _text(row, "user")
        rows.append({
            "user": who,
            "text": text,
            # Their timestamps are ISO with microseconds and a Z; the date is
            # the part anybody reads, and the page formats it.
            "when": _text(row, "submitted"),
            "server": who.lower() == "server",
        })

    with _comments_lock:
        _comments[achievement] = (time.time(), rows)
    return {"ok": True, "id": achievement, "comments": rows}


def achievements(game: int, refresh: bool = False) -> dict:
    """Every achievement in one set, with which of them you have.

    Never raises: like how_long, every failure comes back as a `reason` the
    page can put on screen, because this is opened by somebody who pressed a
    button and is owed an answer either way.
    """
    from . import artwork  # noqa: PLC0415 - only this function needs the key

    conf = artwork.settings()["retroachievements"]
    key, who = conf.get("api_key") or "", conf.get("username") or ""
    if not key:
        return {"ok": False, "reason": "nokey"}
    game = int(game or 0)
    if not game:
        return {"ok": False, "reason": "noset"}

    if not refresh:
        with _achievements_lock:
            cached = _achievements.get(game)
            if cached and time.time() - cached[0] < ACHIEVEMENTS_LIFE:
                return cached[1]

    # With a username, the endpoint that knows what you have; without one, the
    # endpoint that only knows what there is.
    if who:
        asked = {"g": str(game), "u": who, "y": key}
        where = USER_GAME_API
    else:
        asked = {"i": str(game), "y": key}
        where = GAME_EXTENDED_API
    request = urllib.request.Request(
        f"{where}?{urllib.parse.urlencode(asked)}",
        headers={"User-Agent": USER_AGENT})
    try:
        data = json.loads(
            rapi.read(request, timeout=30).decode("utf-8", "replace"))
    except urllib.error.HTTPError as exc:
        if exc.code in (401, 403):
            return {"ok": False, "reason": "badkey"}
        if exc.code == 404:
            return {"ok": False, "reason": "noset"}
        return _stored_set(game, who) or {"ok": False, "reason": "unreachable"}
    except Exception:  # noqa: BLE001 - offline, timeout, nonsense JSON
        # A set already read once is a better answer than an empty panel, and
        # this is the case it was written down for.
        return _stored_set(game, who) or {"ok": False, "reason": "unreachable"}
    if not isinstance(data, dict):
        return _stored_set(game, who) or {"ok": False, "reason": "unreachable"}

    rows = [a for a in (_one_achievement(r) for r in _achievement_rows(data)) if a]
    if not rows:
        return {"ok": False, "reason": "noachievements", "id": game,
                "title": str(data.get("Title") or data.get("title") or ""),
                "url": GAME_URL.format(id=game)}

    # Their own order first, then by id for the sets that don't set one -
    # which is the order the game's page lists them in, and the order the
    # author meant them to be read in.
    rows.sort(key=lambda a: (a["order"], a["id"]))
    out = {
        "ok": True,
        "id": game,
        "title": str(data.get("Title") or data.get("title") or ""),
        "url": GAME_URL.format(id=game),
        # Empty when nobody is signed in, which is how the page knows the
        # unlocked marks below are absent rather than all false.
        "user": who,
        "total": len(rows),
        "earned": sum(1 for a in rows if a["unlocked"]),
        "hardcore": sum(1 for a in rows if a["hardcore"]),
        "points": sum(a["points"] for a in rows),
        "players": _number(data, "numDistinctPlayers"),
        "achievements": rows,
    }

    was = _remember_set(game, out, who)
    if was:
        # What changed, so the page can say "this set has grown since you last
        # looked" rather than quietly showing different numbers.
        out["revised"] = {"was": was,
                          "now": {"total": out["total"], "points": out["points"]}}

    with _achievements_lock:
        _achievements[game] = (time.time(), out)
    return out
