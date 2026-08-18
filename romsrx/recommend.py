"""Games like the ones already on the shelf.

A library is a statement of taste that nobody ever reads back. This reads it:
what is on the disk, what has actually been played, and - through IGDB, which
keeps a "similar games" list for nearly every commercial release - what else is
of that kind. The answer is then narrowed to things this app can actually do
something about: a recommendation you cannot download is a magazine article.

Three things decide the order, in this order:

1. Whether RetroAchievements has a set for it. That is what this app is for,
   and a recommended game with a set is a recommended game with a reason to
   finish it.
2. How many of your games pointed at it. One game saying "you might like this"
   is a guess; five saying it is a pattern.
3. What IGDB's own players think of it, which breaks ties between two games
   nothing else separates.

Without IGDB credentials this still answers, from the index alone: the series
you already own more of. That is a narrower kind of suggestion - it will never
tell somebody who likes Metroid about Castlevania - but it needs no account,
no key and no request to anybody, and "you have three of these five" is a real
answer to "what next".
"""

from __future__ import annotations

import random
import re
import sqlite3
import threading
import time

from . import artwork, db, retro
from .names import normalize_title

# How many of the user's games are asked about. Every seed is a request to
# IGDB, and their limit is four a second - so this is the difference between
# an answer that arrives while somebody is looking at it and one that does not.
# Played games come first, which is the whole point of having a limit: what
# somebody actually plays says more than what they happen to have downloaded.
SEEDS = 16

# ...and how many suggestions come back at a time. Ten is a list somebody
# reads to the end; the rest are one press away, which is a better deal than
# two dozen rows nobody scrolls past.
LIMIT = 10

# Enough of a title to be a series. "Mega Man X4" and "Mega Man 8" share two
# words; "Sonic" and "Sonic 2" share one. Anything shorter than this is a
# coincidence rather than a series, which is why single words are only trusted
# when they are long ones.
_SERIES_WORDS = 2
_MIN_ROOT = 5


def _fold(title: str) -> str:
    """The comparable form of a title, as the index stores it."""
    return normalize_title(_GROUPS.sub(" ", str(title or "")).strip())


_GROUPS = re.compile(r"\s*[\(\[][^\)\]]*[\)\]]")
_WORD = re.compile(r"[a-z0-9]+")


def _series_root(title: str) -> str:
    """The part of a name that a sequel would keep.

    Numerals and the usual sequel words go, so "Mega Man 3" and "Mega Man X"
    fold to the same root as "Mega Man". A root has to be long enough to mean
    something on its own - "The" is not a series.
    """
    words = [w for w in _WORD.findall(_fold(title))
             if not w.isdigit() and w not in _SEQUEL_WORDS]
    root = " ".join(words[:_SERIES_WORDS])
    return root if len(root) >= _MIN_ROOT else ""


_SEQUEL_WORDS = frozenset({
    "ii", "iii", "iv", "v", "vi", "vii", "viii", "ix", "x", "xi", "xii",
    "the", "a", "an", "of", "and",
})


def _seeds(games: list[dict]) -> list[dict]:
    """Which of somebody's games get asked about, most telling first."""
    rows = [g for g in games
            if isinstance(g, dict) and g.get("name") and g.get("console")]
    # Played first, longest first among those: an hour in a game is a stronger
    # statement than a download nobody opened.
    rows.sort(key=lambda g: -(g.get("playSeconds") or 0))
    return rows[:SEEDS]


def _owned(games: list[dict]) -> set[str]:
    return {_fold(g.get("name")) for g in games if isinstance(g, dict)}


def _already_have(norm: str, owned: set[str]) -> bool:
    """Whether this suggestion is a game they have, under another name.

    Exactly, or as the game one of theirs is an edition of: somebody with
    "Bully - Scholarship Edition" does not need to be told about "Bully". The
    test is one-directional on purpose - an owned title that begins with the
    whole of the suggested one plus a space is a longer name for the same game,
    while the reverse is how sequels are named and "Sonic 2" must survive
    owning "Sonic".
    """
    if not norm:
        return True
    if norm in owned:
        return True
    return any(have.startswith(f"{norm} ") for have in owned)


# -- what the index can be asked about ------------------------------------
def _available(conn: sqlite3.Connection,
               titles: list[str]) -> dict[str, list[str]]:
    """{folded title: consoles it can be downloaded for} for what is indexed."""
    found = db.consoles_for_titles(conn, titles)
    return {title: sorted(slots.get("", set()))
            for title, slots in found.items() if slots.get("")}


def _from_series(conn: sqlite3.Connection, games: list[dict],
                 owned: set[str], limit: int) -> list[dict]:
    """The rest of the series you already own part of.

    The whole of this file's answer when IGDB is not set up, and a filler for
    the last few rows when it is: a similar-games list is better advice, but
    "you have three Mega Man games and the index has five more" is advice too.
    """
    roots: dict[str, str] = {}
    for game in _seeds(games):
        root = _series_root(game.get("name"))
        if root:
            roots.setdefault(root, str(game.get("name")))
    if not roots:
        return []

    out: list[dict] = []
    seen = set(owned)
    for root, because in roots.items():
        rows = conn.execute(
            "SELECT DISTINCT title, title_norm, console FROM files "
            "WHERE title_norm LIKE ? LIMIT 40", (f"{root}%",))
        for title, norm, console in rows:
            if not console or norm in seen or _already_have(norm, owned):
                continue
            seen.add(norm)
            out.append({
                "title": title, "norm": norm, "consoles": [console],
                "because": [because], "votes": 1, "rating": 0,
                "source": "series",
            })
            if len(out) >= limit * 3:
                return out
    return out


# -- what IGDB can be asked about -----------------------------------------
# One query per seed, and it brings back the similar games whole - name, cover
# and rating in the same answer - rather than a list of ids to look up
# afterwards. Their expansion syntax is what makes that possible, and it turns
# what would be two requests per game into one.
_SIMILAR_FIELDS = ("fields name, similar_games.name, similar_games.total_rating,"
                   " similar_games.total_rating_count, platforms;")


def _igdb_similar(conf: dict, console: str, name: str) -> list[dict]:
    title = artwork.title_of(name)
    if not title:
        return []
    ids = set(artwork._igdb_ids(conf, console))  # noqa: SLF001 - same package
    quoted = title.replace('"', " ").replace("\\", " ")
    rows = artwork._igdb_query(  # noqa: SLF001
        conf, "games",
        f'search "{quoted}"; {_SIMILAR_FIELDS} limit 5;')
    want = _fold(title)
    for row in rows or []:
        if not isinstance(row, dict):
            continue
        # The right game, and on the right machine where we know which that is.
        if ids and not (set(row.get("platforms") or []) & ids):
            continue
        if _fold(row.get("name")) != want:
            continue
        return [one for one in (row.get("similar_games") or [])
                if isinstance(one, dict) and one.get("name")]
    return []


def _from_igdb(games: list[dict], owned: set[str]) -> list[dict]:
    conf = artwork.settings()["igdb"]
    if not conf.get("on") or not artwork._ready("igdb", conf):  # noqa: SLF001
        return []

    tally: dict[str, dict] = {}
    for seed in _seeds(games):
        try:
            similar = _igdb_similar(conf, str(seed["console"]), str(seed["name"]))
        except Exception:  # noqa: BLE001 - one seed short is not a failure
            continue
        for one in similar:
            norm = _fold(one.get("name"))
            if _already_have(norm, owned):
                continue
            row = tally.setdefault(norm, {
                "title": str(one.get("name")), "norm": norm, "consoles": [],
                "because": [], "votes": 0, "source": "igdb",
                "rating": int(one.get("total_rating") or 0),
            })
            row["votes"] += 1
            because = str(seed["name"])
            if because not in row["because"]:
                row["because"].append(because)
    return list(tally.values())


# -- putting the two together ---------------------------------------------
# The whole ranked list is worked out once and kept for a few minutes, because
# "show me more" must not mean asking IGDB the same sixteen questions again.
# One shelf's worth of suggestions is far more than a screenful - sixteen
# seeds bring back a couple of hundred candidates between them - so paging
# through what was already computed is both instant and more honest than
# recomputing and hoping the order comes out the same way twice.
_RANKED_LIFE = 10 * 60
_ranked: dict[str, tuple[float, list]] = {}
_ranked_lock = threading.Lock()


def _signature(games: list[dict]) -> str:
    """What a shelf is, for the purpose of "is this the same question again"."""
    return "\n".join(sorted(
        f"{g.get('console')}\t{g.get('name')}\t{1 if g.get('playSeconds') else 0}"
        for g in games if isinstance(g, dict)))


def _ranked_rows(conn: sqlite3.Connection, games: list[dict]) -> list[dict]:
    key = _signature(games)
    with _ranked_lock:
        found = _ranked.get(key)
        if found and time.time() - found[0] < _RANKED_LIFE:
            return found[1]

    rows = _build(conn, games)
    with _ranked_lock:
        _ranked.clear()          # one shelf at a time; this is not a cache farm
        _ranked[key] = (time.time(), rows)
    return rows


def _build(conn: sqlite3.Connection, games: list[dict]) -> list[dict]:
    """Every suggestion this shelf produces, ranked. See suggest()."""
    owned = _owned(games)
    rows = _from_igdb(games, owned)
    used_igdb = bool(rows)
    # Series matches come after the similar-games ones and never displace them.
    # They are the whole answer without IGDB, and with it they are what the
    # deeper pages are made of once the good suggestions run out.
    rows += _from_series(conn, games, owned | {r["norm"] for r in rows}, LIMIT)

    if not rows:
        return []

    # What the index actually has, which decides both what can be offered and
    # which console to ask RetroAchievements about.
    have = _available(conn, [r["norm"] for r in rows])
    for row in rows:
        if not row["consoles"]:
            row["consoles"] = have.get(row["norm"], [])
        row["indexed"] = bool(have.get(row["norm"]))

    # A set is the strongest reason to recommend anything here, so it is worth
    # one lookup each - and the lookup is a folded-title match against a list
    # already in memory, not a request.
    for row in rows:
        row["raId"] = 0
        for console in row["consoles"]:
            try:
                found = retro.game_id(console, row["title"])
            except Exception:  # noqa: BLE001
                found = 0
            if found:
                row["raId"] = found
                row["raConsole"] = console
                row["raUrl"] = retro.GAME_URL.format(id=found)
                break

    rows.sort(key=lambda r: (
        # Things nobody can download go last however good they are.
        0 if r.get("indexed") else 1,
        0 if r.get("raId") else 1,
        -r.get("votes", 0),
        -(r.get("rating") or 0),
        r["title"].lower(),
    ))
    for row in rows:
        row["igdb"] = used_igdb
    return rows


def suggest(conn: sqlite3.Connection, games: list[dict],
            limit: int = LIMIT, offset: int = 0,
            only_ra: bool = False, console: str = "", seed: int = 0) -> dict:
    """A page of suggestions, drawn from the games already owned.

    `offset` walks further down the same ranked list rather than asking for it
    again - see _ranked_rows. `only_ra` and `console` narrow it before the page
    is cut, so "more" always means more of what was asked for rather than more
    of everything with the unwanted ones quietly dropped.

    `seed` deals the same list differently. The ranking is stable by design -
    the same shelf suggests the same games in the same order, for ever - which
    is right for "what should I play" and wrong for "show me something else".
    A seed shuffles it, and shuffles the games with an achievement set and the
    games without separately, so the first thing offered is still one this app
    exists to help with rather than whatever chance put on top.
    """
    if not _owned(games):
        return {"games": [], "reason": "empty", "total": 0, "more": False}

    ranked = _ranked_rows(conn, games)
    if not ranked:
        return {"games": [], "reason": "igdb", "total": 0, "more": False}

    wanted = ranked
    if only_ra:
        wanted = [r for r in wanted if r.get("raId")]
    if console:
        wanted = [r for r in wanted if console in (r.get("consoles") or [])]

    if seed:
        shuffler = random.Random(seed)
        with_set = [r for r in wanted if r.get("raId")]
        without = [r for r in wanted if not r.get("raId")]
        shuffler.shuffle(with_set)
        shuffler.shuffle(without)
        wanted = with_set + without

    page = wanted[max(0, offset):max(0, offset) + max(1, limit)]
    return {
        "games": page,
        # Every console any suggestion is available for, so the page can offer
        # the list without a second request or a guess.
        "consoles": sorted({c for r in ranked for c in (r.get("consoles") or [])}),
        "igdb": bool(ranked and ranked[0].get("igdb")),
        "withSets": sum(1 for r in ranked if r.get("raId")),
        "total": len(wanted),
        "more": offset + len(page) < len(wanted),
        "reason": "" if page else "none",
    }
