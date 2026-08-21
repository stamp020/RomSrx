"""Did you mean. What to say when a search finds nothing.

The index holds forty-odd thousand titles and the search that reads them is
FTS5 with prefix matching, which is exact about letters: `castlevaina` matches
nothing, and the app answers "no matches, try a shorter or differently spelled
title". That is the app asking somebody to guess again about a catalogue it
has entirely on disk in front of it.

So on a miss - and only on a miss, which is what keeps this free - the typed
words are compared against every title there is, and the closest one is
offered back.

Two stages, because neither is any good alone. A trigram index says which
titles could plausibly be near the query at all, which turns forty thousand
comparisons into a few hundred; then edit distance ranks those few hundred
properly, which trigram overlap on its own does badly for short words. The
index is built once per process, on the first miss, from a query that reads
one column.

Nothing here touches the network, and nothing here writes to the database.
"""

from __future__ import annotations

import sqlite3
import unicodedata
from collections import Counter

# Below this the answer is a different game, not a correction. Tuned so that
# one wrong letter in an ordinary title passes and two unrelated words do not:
# "castlevaina" against "castlevania" scores about .85.
NEAR_ENOUGH = 0.62

# How many the trigram stage hands to the edit-distance stage. Enough that the
# right answer is in there, small enough that ranking them is instant.
SHORTLIST = 400

# A one-word query has few trigrams and matches half the catalogue on any of
# them, so anything shorter than this is not worth guessing about.
MIN_LENGTH = 4

_index: dict = {"rows": None, "grams": None, "stamp": None}


def _fold(text: str) -> str:
    """Lowercased, stripped of accents and of everything but letters, digits
    and single spaces - the same shape on both sides of the comparison."""
    flat = unicodedata.normalize("NFKD", str(text or "").casefold())
    kept = [c if (c.isalnum() or c.isspace()) else " "
            for c in flat if not unicodedata.combining(c)]
    return " ".join("".join(kept).split())


def _grams(text: str) -> set[str]:
    """Its trigrams, padded so the first and last letters count as much as the
    middle ones - without the padding, a wrong first letter costs nothing."""
    padded = f"  {text} "
    return {padded[i:i + 3] for i in range(len(padded) - 2)}


def _distance(a: str, b: str, cap: int) -> int:
    """Levenshtein, abandoned once it is past caring.

    Two rows rather than a full matrix, and a cheap length check first: most
    of what reaches here is nowhere near, and the answer for those only has to
    be "far", not "how far".
    """
    if abs(len(a) - len(b)) > cap:
        return cap + 1
    if a == b:
        return 0
    previous = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        current = [i]
        best = i
        for j, cb in enumerate(b, 1):
            current.append(min(previous[j] + 1,
                               current[j - 1] + 1,
                               previous[j - 1] + (ca != cb)))
            best = min(best, current[j])
        if best > cap:
            return cap + 1          # every path from here is already too long
        previous = current
    return previous[-1]


def _build(conn: sqlite3.Connection) -> None:
    """Every distinct title, and a trigram to find it by.

    One title per game rather than per file: the same game exists in six
    regions and eleven archives, and offering the same correction six times is
    not six answers.
    """
    rows = conn.execute(
        "SELECT title_norm, MIN(title), COUNT(*) FROM files "
        "GROUP BY title_norm").fetchall()
    titles = []
    grams: dict[str, list[int]] = {}
    for norm, shown, count in rows:
        folded = _fold(norm)
        if len(folded) < MIN_LENGTH:
            continue
        at = len(titles)
        titles.append((folded, shown, count))
        for gram in _grams(folded):
            grams.setdefault(gram, []).append(at)
    _index["rows"] = titles
    _index["grams"] = grams
    _index["stamp"] = conn.execute("SELECT COUNT(*) FROM files").fetchone()[0]


def _ready(conn: sqlite3.Connection) -> bool:
    """Built, and built from this many files.

    The file count stands in for "has the index changed": it is one cheap
    query, and a reindex that ends with exactly the same number of files as
    before is not a case worth carrying state for.
    """
    if _index["rows"] is None:
        _build(conn)
        return True
    try:
        now = conn.execute("SELECT COUNT(*) FROM files").fetchone()[0]
    except sqlite3.Error:
        return _index["rows"] is not None
    if now != _index["stamp"]:
        _build(conn)
    return True


def suggest(conn: sqlite3.Connection, query: str) -> dict:
    """The closest title in the index to what was typed.

    Answers `{}` where nothing is close enough, which is the common case and
    the right answer: a wrong suggestion is worse than none, because somebody
    will follow it.
    """
    typed = _fold(query)
    if len(typed) < MIN_LENGTH:
        return {}
    try:
        if not _ready(conn):
            return {}
    except sqlite3.Error:
        return {}

    wanted = _grams(typed)
    hits: Counter[int] = Counter()
    for gram in wanted:
        for at in _index["grams"].get(gram, ()):
            hits[at] += 1
    if not hits:
        return {}

    # Longest titles first among equals would bias towards box sets, so the
    # shortlist is by shared trigrams alone and the ranking below decides.
    best = None
    # A quarter of what was typed, so the allowance grows with the name. A
    # third was too generous at the short end: five letters bought two edits,
    # and two edits from "spyro" reaches "spytoy", which is a different game
    # rather than a correction.
    cap = max(1, len(typed) // 4)
    for at, shared in hits.most_common(SHORTLIST):
        folded, shown, count = _index["rows"][at]
        gap = _distance(typed, folded, cap)
        if gap > cap:
            continue
        # Distance as a fraction of the longer string, so a one-letter slip in
        # a short name is not scored the same as one in a long one.
        score = 1 - gap / max(len(typed), len(folded))
        # Trigram overlap breaks ties, and a game the index has many copies of
        # breaks the rest: with two equally close titles, the one somebody is
        # more likely to have meant is the one that actually exists widely.
        rank = (round(score, 3), shared, count)
        if score >= NEAR_ENOUGH and (best is None or rank > best[0]):
            best = (rank, shown, folded)

    if not best or best[2] == typed:
        return {}
    return {"title": best[1], "score": best[0][0]}
