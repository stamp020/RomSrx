"""Is there a newer release on GitHub?

The check is deliberately thin: one unauthenticated call to the releases API,
a version comparison, and a link. Nothing is downloaded or replaced here - a
running app can't overwrite its own files on Windows, so installing an update
is left to the person using it.

Results are cached for a while so opening the app repeatedly doesn't burn
through GitHub's 60-requests-an-hour allowance for anonymous callers.
"""

from __future__ import annotations

import json
import re
import threading
import time
import urllib.error
import urllib.request

from . import REPO, RELEASES_URL, __version__

API = f"https://api.github.com/repos/{REPO}/releases/latest"
CACHE_SECONDS = 6 * 60 * 60
TIMEOUT = 10

# Which build each platform should be offered. Matched against asset names.
ASSET_HINTS = {
    "win32": ("windows", ".zip"),
    "linux": ("linux", ".tar.gz"),
    "darwin": ("macos", ".tar.gz"),
}

_lock = threading.Lock()
_cache: dict = {"at": 0.0, "value": None}


def parse_version(text: str) -> tuple:
    """`v1.2.3` -> (1, 2, 3). Anything unparsable sorts lowest.

    Trailing text like `1.2.3-beta` is dropped rather than guessed at, so a
    pre-release never looks newer than the release it precedes.
    """
    numbers = re.findall(r"\d+", (text or "").split("-")[0])
    return tuple(int(n) for n in numbers[:3]) or (0,)


def is_newer(candidate: str, current: str) -> bool:
    return parse_version(candidate) > parse_version(current)


def _pick_asset(assets: list, platform: str) -> dict | None:
    """The download built for this platform, if the release carries one."""
    wants = ASSET_HINTS.get(platform)
    if not wants:
        return None
    for asset in assets:
        name = (asset.get("name") or "").lower()
        if all(bit in name for bit in wants):
            return {"name": asset.get("name"),
                    "url": asset.get("browser_download_url"),
                    "size": asset.get("size") or 0}
    return None


def _fetch(platform: str) -> dict:
    request = urllib.request.Request(API, headers={
        "User-Agent": f"RomSrx/{__version__}",
        "Accept": "application/vnd.github+json",
    })
    with urllib.request.urlopen(request, timeout=TIMEOUT) as response:  # noqa: S310
        data = json.loads(response.read().decode("utf-8", "replace"))

    latest = (data.get("tag_name") or data.get("name") or "").lstrip("vV")
    return {
        "current": __version__,
        "latest": latest,
        "update": bool(latest) and is_newer(latest, __version__),
        # Enough for a release that actually lists what changed. The old 2000
        # cut the notes off mid-sentence, which is worse than not showing them
        # - and "What's new" scrolls, so length costs nothing on screen.
        "notes": (data.get("body") or "")[:8000],
        "page": data.get("html_url") or RELEASES_URL,
        "asset": _pick_asset(data.get("assets") or [], platform),
    }


def check(platform: str, force: bool = False) -> dict:
    """What the app should tell the user. Never raises - being offline is
    the normal case, not an error worth interrupting anyone over."""
    now = time.time()
    with _lock:
        fresh = _cache["value"] and now - _cache["at"] < CACHE_SECONDS
        if fresh and not force:
            return dict(_cache["value"], cached=True)

    try:
        result = _fetch(platform)
    except (urllib.error.URLError, OSError, ValueError, TimeoutError) as exc:
        return {"current": __version__, "latest": "", "update": False,
                "error": type(exc).__name__, "page": RELEASES_URL}

    with _lock:
        _cache.update(at=now, value=result)
    return dict(result, cached=False)
