"""How long every game takes, worked out once and kept.

RetroAchievements publishes a median time to beat and to master per game, and
publishes it one game at a time. That is why the app's two time orders have
only ever ranked what was already on screen: ranking the catalogue means
asking about every game in it, and nobody waits twenty minutes for a sort.

So it is asked once, deliberately, from Settings - and then never again. The
answers live in the user folder rather than in memory, so they survive the app
closing, and every list that wants a time reads them instead of the network.

A rescan is cheap, which is the part worth having. The bulk game list carries
the date each set last changed, so a second run asks only about sets that are
new or have been revised since the first - a handful of requests rather than
six thousand.

The scope is the games this index can actually fetch. RetroAchievements has
far more sets than any one collection of sources carries, and timing a game
nobody here can download would be minutes spent on an answer with nothing
behind it.
"""

from __future__ import annotations

import json
import os
import threading
import time

from .paths import user

STORE = user("retro") / "times.json"

# Between calls. The shared gate in rapi already spaces every request; this is
# on top of it, because a scan is thousands of requests in a row and being a
# good guest about that matters more than finishing sooner.
GAP = 0.05

_store: dict[int, dict] | None = None
_lock = threading.Lock()
_dirty = False


def _load() -> dict[int, dict]:
    global _store  # noqa: PLW0603
    if _store is None:
        try:
            with open(STORE, encoding="utf-8") as fh:
                saved = json.load(fh)
            _store = {int(k): v for k, v in (saved.get("times") or {}).items()
                      if isinstance(v, dict)}
        except (OSError, ValueError, TypeError):
            _store = {}
    return _store


def save() -> None:
    global _dirty  # noqa: PLW0603
    with _lock:
        if not _dirty or _store is None:
            return
        payload = {"at": int(time.time()),
                   "times": {str(k): v for k, v in _store.items()}}
        _dirty = False
    try:
        STORE.parent.mkdir(parents=True, exist_ok=True)
        temporary = STORE.with_suffix(".tmp")
        with open(temporary, "w", encoding="utf-8") as fh:
            json.dump(payload, fh)
        os.replace(temporary, STORE)
    except OSError:
        pass


def known() -> dict[int, dict]:
    """Everything timed so far, by game id."""
    with _lock:
        return dict(_load())


def counts() -> dict:
    """What is in the store, for a page that wants to describe it."""
    with _lock:
        rows = _load()
        timed = sum(1 for r in rows.values() if r.get("beat") or r.get("master"))
    at = 0
    try:
        with open(STORE, encoding="utf-8") as fh:
            at = int(json.load(fh).get("at") or 0)
    except (OSError, ValueError, TypeError):
        at = 0
    return {"asked": len(rows), "timed": timed, "at": at}


def outstanding(pool: list[dict]) -> list[dict]:
    """Which of these still need asking about.

    A game is outstanding when it has never been asked about, or when its set
    has been revised since it was - which is what makes a second scan a
    handful of requests instead of the whole thing again.
    """
    rows = known()
    out = []
    for one in pool:
        game = int(one.get("id") or 0)
        if not game:
            continue
        seen = rows.get(game)
        if not seen:
            out.append(one)
        elif (one.get("modified") or "") != (seen.get("modified") or ""):
            out.append(one)
    return out


def _remember(game: int, modified: str, found: dict) -> None:
    global _dirty  # noqa: PLW0603
    with _lock:
        _load()[game] = {
            "beat": found.get("beat"),
            "master": found.get("master"),
            "players": found.get("players"),
            # Kept even when both times are missing, so a game nobody has
            # finished is not asked about again on every single scan.
            "modified": modified,
            "at": int(time.time()),
        }
        _dirty = True


def scan(pool: list[dict], progress=None, stop=None) -> dict:
    """Ask for the times of everything outstanding in `pool`.

    Never raises. A refusal or a game with no progression data is written down
    as "asked and has none", because the alternative is asking again for ever.
    """
    from . import retro  # noqa: PLC0415 - keeps this module a leaf

    todo = outstanding(pool)
    done = 0
    for one in todo:
        if stop is not None and stop():
            break
        game = int(one["id"])
        try:
            found = retro.how_long("", "", game)
        except Exception:  # noqa: BLE001 - one game short is not a failure
            found = {}
        if found.get("ok"):
            _remember(game, one.get("modified") or "", found)
        elif found.get("reason") in ("noset", "notimes"):
            _remember(game, one.get("modified") or "", {})
        # Anything else - unreachable, refused - is left alone so the next run
        # tries it again rather than recording a silence as an answer.
        done += 1
        if progress is not None:
            progress(done, len(todo))
        if GAP:
            time.sleep(GAP)

    save()
    return {"ok": True, "asked": done, "outstanding": len(todo)}


def rank(pool: list[dict], which: str) -> list[dict]:
    """`pool` ordered by the stored time, quickest first.

    Only games that have one. A game with no median is not the longest game
    on the site, it is a game nobody has finished enough times to say - and
    parking those at the end of a list of times reads as though they were
    measured and found slow.

    Both medians ride along on every row, not only the one being sorted by:
    the card this ends up on is showing a game, and "how long to beat" is only
    half of what somebody weighing a "quickest to master" list wants to know.
    Fetching the other one separately would mean asking the network again for
    an answer already sitting right here.
    """
    which = which if which in ("beat", "master") else "beat"
    rows = known()
    out = []
    for one in pool:
        seen = rows.get(int(one.get("id") or 0))
        span = (seen or {}).get(which)
        if not span:
            continue
        out.append({**one, "seconds": int(span),
                    "beat": (seen or {}).get("beat"),
                    "master": (seen or {}).get("master"),
                    "players": (seen or {}).get("players") or 0})
    out.sort(key=lambda r: (r["seconds"], r["title"].lower()))
    return out
