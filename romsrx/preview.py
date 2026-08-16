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
