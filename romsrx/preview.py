"""Everything worth knowing about one game, gathered into one answer.

Nothing here is new work. The cover comes from covers.py, the screenshots off
listings it already keeps, the times and the achievement figures from retro.py,
and the paragraph of prose from artwork.py - all of them things this app had
built for other reasons. What was missing was somewhere to show them together,
which is what the preview panel is.

Assembled in one request rather than four so the panel opens once rather than
filling in piece by piece, and gathered in parallel because three of the four
are network calls that have nothing to say to each other. Every one of them is
allowed to fail on its own: a preview with no summary is a preview, and a
preview with no RetroAchievements figures is what every game on a console they
do not cover will be.
"""

from __future__ import annotations

import threading
import time

from . import artwork, covers, names, retro

# Long enough to say what the game is, short enough not to become the panel.
SUMMARY_MAX = 700

# A ceiling rather than a target. Three sources together rarely reach it, but a
# game that does have this many is a game worth paging through, and the strip
# shows three of them whatever the number.
SHOTS_MAX = 20


def _shorten(text: str) -> str:
    """The first part of a summary, cut at a sentence rather than mid-word."""
    if len(text) <= SUMMARY_MAX:
        return text
    cut = text[:SUMMARY_MAX]
    stop = max(cut.rfind(". "), cut.rfind("! "), cut.rfind("? "))
    if stop > SUMMARY_MAX // 2:
        return cut[:stop + 1]
    space = cut.rfind(" ")
    return (cut[:space] if space > 0 else cut).rstrip(" ,;:") + "…"


def _interleave(groups: list[list[str]]) -> list[str]:
    """One from each source in turn, rather than each source's lot together.

    Identical files are already gone - covers._distinct takes those out by
    weight - but a handful survive that: the same capture saved twice at
    different quality is two different files that look like one picture, and
    nothing short of comparing the pixels would tell. What can be arranged
    cheaply is that they do not end up side by side, because two copies of one
    screenshot are only really glaring when they are adjacent.

    Taking one from each source in turn does that on its own: near-duplicates
    come from within a source - two regional captures of one scene, two sizes
    of one publisher shot - so a strip that alternates cannot place them
    together while any other source still has something to offer.

    Round-robin rather than a shuffle, deliberately. A shuffle would sometimes
    put the pair together anyway, and it would draw a different panel every
    time the same game was opened, which looks like a bug even when it isn't.
    This also means the three thumbnails on the panel are one from each source,
    which is a better first impression than three angles on the same room.
    """
    out: list[str] = []
    for round_ in range(max((len(g) for g in groups), default=0)):
        for group in groups:
            if round_ < len(group):
                out.append(group[round_])
    return out


def build(console: str, name: str) -> dict:
    """One game, described as fully as the sources allow.

    `name` arrives as the filename, extension and all, because that is what the
    page has stamped on every row for the RetroAchievements lookup. Everything
    covers.py does is keyed on a name with the extension already off - the page
    strips it before asking for a tile - so it comes off once here rather than
    being a thing three callers have to remember. retro.py takes either.
    """
    stem = names.split_extension(name)[0] or name
    out: dict = {"console": console, "name": name,
                 "cover": "", "shots": [], "ra": {}, "summary": ""}

    game = 0
    try:
        game = retro.game_id(console, name)
    except Exception:  # noqa: BLE001 - a preview never fails as a whole
        game = 0

    def cover() -> None:
        try:
            out["cover"] = covers.resolve(console, stem)
        except Exception:  # noqa: BLE001
            pass

    def pictures() -> None:
        """In-game shots, from all three, best first and never the same twice.

        libretro leads because its captures are of the very releases in the
        index and cost nothing to ask for; RetroAchievements adds one more of
        the same kind; IGDB is last but is the only one that has six or eight,
        which is what takes the strip past a single row.

        No title screens from anywhere. They were how the same picture of the
        same menu ended up in a preview twice, and a title screen says nothing
        a box has not already said better.
        """
        groups: list[list[str]] = []
        for job in (lambda: covers.shots(console, stem),
                    lambda: retro.images(console, name, game) if game else [],
                    lambda: artwork.screenshots(console, stem)):
            try:
                groups.append(list(job() or []))
            except Exception:  # noqa: BLE001 - one source short is not a failure
                groups.append([])

        # Deduplicated, and never the cover again: it is shown beside these.
        seen = {out.get("cover") or ""}
        keep = []
        for url in _interleave(groups):
            if url and url not in seen:
                seen.add(url)
                keep.append(url)
        out["shots"] = keep[:SHOTS_MAX]

    def figures() -> None:
        if not game:
            return
        try:
            found = retro.how_long(console, name, game)
        except Exception:  # noqa: BLE001
            return
        out["ra"] = found if isinstance(found, dict) else {}

    def prose() -> None:
        try:
            out["summary"] = _shorten(artwork.summary(console, stem))
        except Exception:  # noqa: BLE001
            pass

    # The cover first and alone: the screenshots need to know what it is, so
    # they can avoid offering the same picture twice.
    cover()
    threads = [threading.Thread(target=job, daemon=True)
               for job in (pictures, figures, prose)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=45)

    if game:
        out["raUrl"] = retro.GAME_URL.format(id=game)
        out["raId"] = game
    return out


# -- what to play next ----------------------------------------------------
# The shelf knows what has never been started; RetroAchievements knows how long
# each of those takes. Neither is much use alone - "you have forty unplayed
# games" is a guilt trip, not a suggestion - and together they answer the
# question people actually ask, which is "what can I finish this week".
#
# Only the shortlist is priced. Asking how long every unplayed game takes would
# be four hundred requests to rank forty; asking about a couple of dozen and
# showing the shortest is the same answer for a fraction of it.
#
# Everything priced is handed back, not only the handful worth showing. The
# page shows a shortlist and lets you turn it round - shortest to beat, or
# shortest to master - and those are two different orders over the same games.
# Ranking two dozen here and slicing to eight there means changing your mind
# about the order costs nothing, where sending eight would have meant asking
# RetroAchievements the same two dozen questions again to answer the second
# one.
SUGGEST_PRICE = 24          # how many are looked up


def suggest(games: list[dict], limit: int = SUGGEST_PRICE,
            played: bool = False) -> list[dict]:
    """Unplayed games worth starting, shortest to beat first.

    `games` is the shelf as the page holds it: name, console, path and how long
    it has been played. Anything already started is out - the question is what
    to begin, not what to go back to.

    `played` turns this into the whole shelf, for the other question people
    ask of the same window: not "what should I start" but "how long is
    everything here". A shelf where every game has been touched answers the
    first question with nothing at all, which looks like a failure rather
    than an answer.

    With it on, a game is listed whether or not RetroAchievements has a time
    for it. That is the difference between "everything here" and "everything
    here that the site happens to have priced" - and the second is not what
    somebody asking for all of it meant. Only so many are looked up, since
    each is a request; the rest are listed with no time rather than left out,
    which the page already draws as a dash.

    A game with no file behind it is a perfectly good answer. The page sends
    its playlists here as well as its library, and an entry it has not
    downloaded yet has the two things this needs - a name and a console - so it
    is priced like any other. `path` is empty for those, which is how the page
    knows to offer to fetch it rather than to play it.
    """
    fresh = [g for g in games
             if isinstance(g, dict)
             and (played or not (g.get("playSeconds") or 0))
             and g.get("name") and g.get("console")]
    if not fresh:
        return []

    # Priced in the order the shelf is in, so the answer is stable rather than
    # a different set of games every time the panel is opened.
    fresh.sort(key=lambda g: (str(g.get("console") or ""),
                              str(g.get("name") or "").lower()))

    priced: list[dict] = []
    for at, game in enumerate(fresh):
        console, name = str(game["console"]), str(game["name"])
        # Past the budget nothing more is asked; with `played` on they are
        # still listed, because the question was "everything here".
        found = {}
        if at < SUGGEST_PRICE:
            try:
                found = retro.how_long(console, name)
            except Exception:  # noqa: BLE001 - one game short is not a failure
                found = {}
        elif not played:
            break
        # Either figure is enough to be worth listing. Almost every game with
        # a set has a time to beat and that is what this is ordered by, but the
        # page can also order by the time to master, and dropping the odd game
        # that only has that one would leave it out of the very order it is the
        # answer to.
        timed = found.get("ok") and (found.get("beat") or found.get("master"))
        if not timed and not played:
            continue
        priced.append({
            "name": name,
            "console": console,
            "path": game.get("path") or "",
            "beat": found.get("beat"),
            "beatFrom": found.get("beatFrom"),
            # Both figures, because "three hours to finish" and "ninety to
            # master" are two different decisions about the same evening.
            "master": found.get("master"),
            "masterFrom": found.get("masterFrom"),
            "achievements": found.get("achievements"),
            "raId": found.get("id"),
        })

    # Shortest to beat, with the ones that have no such time after them rather
    # than in front pretending to take no time at all.
    priced.sort(key=lambda g: (g["beat"] is None, g["beat"] or 0,
                               str(g["name"]).lower()))
    # The cap is for the shortlist. Asked for the whole shelf, the answer is
    # the whole shelf - cutting it at two dozen would be the same complaint
    # this branch exists to answer.
    return priced if played else priced[:limit]


# -- pricing the shelf ----------------------------------------------------
# Sorting a library by "fastest to beat" needs a time for every game in it, and
# a time costs a request. So this answers with everything already known
# immediately and prices a bounded number of the rest, which means choosing
# that sort fills in over a few goes rather than hanging for four minutes on a
# large library. Times are kept for a fortnight, so it is a one-off either way.
TIMES_BUDGET = 60
TIMES_GAP = 0.25        # seconds between uncached lookups


def times(games: list[dict]) -> dict:
    """{console\tname: {beat, master}} for as many games as can be priced now."""
    found: dict[str, dict] = {}
    spent = 0
    waiting = 0
    for game in games if isinstance(games, list) else []:
        if not isinstance(game, dict):
            continue
        console, name = str(game.get("console") or ""), str(game.get("name") or "")
        if not console or not name:
            continue
        try:
            ident = retro.game_id(console, name)
        except Exception:  # noqa: BLE001
            continue
        if not ident:
            continue
        known = retro.priced(ident)
        if not known and spent >= TIMES_BUDGET:
            waiting += 1
            continue
        if not known:
            # RetroAchievements answers 429 to a burst, and a game that got one
            # was being written off as having no time at all - which put it at
            # the bottom of a shelf sorted by time, looking like a wrong answer
            # rather than a missing one. A quarter-second between uncached
            # lookups buys the answer instead.
            time.sleep(TIMES_GAP)
            spent += 1
        try:
            row = retro.how_long(console, name, ident)
        except Exception:  # noqa: BLE001
            row = {}
        if row.get("ok") and (row.get("beat") or row.get("master")):
            found[f"{console}\t{name}"] = {"beat": row.get("beat"),
                                           "master": row.get("master")}
        elif row.get("reason") != "noset":
            # Nothing came back this time, and it was not "there is no set for
            # this game". Counted as still to do, so the page offers another go
            # rather than leaving it parked at the bottom for ever.
            waiting += 1
    return {"times": found, "priced": len(found), "waiting": waiting}
