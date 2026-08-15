"""Opening a web page from inside the app.

There are two places a page can go, and the user chooses which in Settings: a
window of this app's own, or the browser they already use.

Nothing here renders anything. The app briefly had a panel that showed pages
in an iframe beside the library, which worked for most of the web but not for
the one site it was built for - retroachievements.org sends X-Frame-Options
and is refused by the engine before it draws anything. A page in a window of
its own is a top-level page, which that header has nothing to say about, so
the panel went and the window stayed.

The window is made by app.py, since only app.py knows whether there is a
native window to make a second of - started with `serve` there isn't one.
"""

from __future__ import annotations

import urllib.parse
import webbrowser


def is_web_url(url: str) -> bool:
    try:
        parsed = urllib.parse.urlparse(url)
    except ValueError:
        return False
    return parsed.scheme in ("http", "https") and bool(parsed.netloc)


def open_external(url: str) -> bool:
    """Hand a page to the user's own browser."""
    if not is_web_url(url):
        return False
    try:
        return bool(webbrowser.open(url))
    except Exception:  # noqa: BLE001 - no browser configured
        return False


# -- a window of the app's own ------------------------------------------
_opener = None


def set_window_opener(fn) -> None:
    global _opener  # noqa: PLW0603 - one process-wide window factory
    _opener = fn


def can_open_window() -> bool:
    return _opener is not None


def open_window(url: str, title: str = "") -> bool:
    """Show a page in a window of the app's own. False if there can't be one."""
    if not is_web_url(url) or _opener is None:
        return False
    try:
        _opener(url, title or url)
    except Exception:  # noqa: BLE001 - a window that won't open is not fatal
        return False
    return True
