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


def _fetch_patches() -> dict[int, list[str]] | None:
    """{game id: patch url} from the repository listing, or None if unread."""
    request = urllib.request.Request(
        PATCH_TREE, headers={"User-Agent": USER_AGENT,
                             "Accept": "application/vnd.github+json"})
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:  # noqa: S310
            payload = json.loads(response.read().decode("utf-8", "replace"))
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
    return {"ids": out, "patches": found,
            "patchExts": sorted({e.lstrip(".") for e
                                 in patcher.ROM_EXTS + patcher.DISC_EXTS})}


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
PROGRESS_LIFE = 14 * 24 * 3600      # medians move slowly; a fortnight is fine

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
        if cached and time.time() - cached[0] < PROGRESS_LIFE:
            return cached[1]

    asked = {"i": str(game), "y": key}
    request = urllib.request.Request(
        f"{PROGRESS_URL}?{urllib.parse.urlencode(asked)}",
        headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:  # noqa: S310
            data = json.loads(response.read().decode("utf-8", "replace"))
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
        with urllib.request.urlopen(request, timeout=30) as response:  # noqa: S310
            data = json.loads(response.read().decode("utf-8", "replace"))
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
