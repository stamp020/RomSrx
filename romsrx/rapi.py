"""One queue in front of RetroAchievements, for the whole process.

profile.py learned this the hard way and wrote it down: build a window out of
a dozen requests in a row and the site refuses some of them, and the refusals
arrive as blank rows rather than as errors - no picture, no game, "Nothing
right now" for somebody plainly playing something. Its answer was to space its
own calls and try a failed one again.

That answer was right and too narrow. It paced *one module*, and the app has
since grown three more places that ask the same site the same kinds of
question: the compatibility sweep, the Want to Play list, and the play-time
backfill. Each was polite on its own and none of them knew about the others,
so opening the library - which starts several at once - produced exactly the
burst profile.py was written to avoid. Asked to audit its own API use during
one long session, this app collected an HTTP 429 doing nothing more unusual
than reading nine endpoints in a row.

So the gate is here, at module scope, and every caller passes through it. The
important word is *process-wide*: two modules each waiting politely for their
own last call is not pacing, it is two bursts.

What this does not do is interpret anything. Callers know what a 404 means for
the question they asked - a game with no set is not the site being down - so
the HTTPError is raised on to them exactly as urllib produced it, and only the
two codes that mean "you are going too fast" are handled here.
"""

from __future__ import annotations

import threading
import time
import urllib.error
import urllib.request

# Sent as an emulator rather than as a browser: these are the emulator-facing
# endpoints, and a made-up browser string is what their edge filters for.
USER_AGENT = "RomSrx/1.0 (+https://github.com/)"

PACE = 0.2              # seconds between calls, across the whole app
RETRY_AFTER = 1.5       # ...and before trying a refused one again
RETRY_MAX = 30          # ...however long the site's own Retry-After says
TRIES = 2

# The two that mean "slow down" rather than "no". 503 is here because their
# edge answers with it under load, and treating that as a real answer is how a
# game ends up reported as having no achievement set at all.
BUSY = (429, 503)

_lock = threading.Lock()
_last = 0.0


def _wait_turn() -> None:
    global _last  # noqa: PLW0603
    with _lock:
        gap = time.time() - _last
        if gap < PACE:
            time.sleep(PACE - gap)
        _last = time.time()


def _pause_for(exc: urllib.error.HTTPError) -> float:
    """How long the site asked to be left alone, within reason.

    Retry-After is theirs to set and is usually a small number of seconds;
    it is capped here because a header saying "an hour" is not something to
    hold a request open for - better to fail and let the caller's own cache
    answer.
    """
    try:
        asked = float(exc.headers.get("Retry-After") or 0)
    except (TypeError, ValueError):
        asked = 0
    return min(max(asked, RETRY_AFTER), RETRY_MAX)


def read(request: urllib.request.Request, timeout: int = 30) -> bytes:
    """Make one request, in turn, retrying only a refusal to serve it.

    Everything else - a 404, a 401, a timeout, a dead connection - comes back
    to the caller untouched and on the first attempt, because those are
    answers about the question rather than about the pace.
    """
    for attempt in range(TRIES):
        _wait_turn()
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310
                return response.read()
        except urllib.error.HTTPError as exc:
            if exc.code not in BUSY or attempt == TRIES - 1:
                raise
            time.sleep(_pause_for(exc))
    raise urllib.error.URLError("gave up")     # unreachable; keeps type checkers happy


def get(url: str, timeout: int = 30, agent: str = USER_AGENT) -> bytes:
    """The same, for a caller that has only a URL."""
    return read(urllib.request.Request(url, headers={"User-Agent": agent}),
                timeout=timeout)
