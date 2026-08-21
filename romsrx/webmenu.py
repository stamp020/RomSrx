"""The right-click menu in the window that shows somebody else's web page.

pywebview ties the engine's own context menu to debug mode - it sets
`AreDefaultContextMenusEnabled` and `AreBrowserAcceleratorKeysEnabled` to
whether the app was started with debugging on - so in a normal build there is
no menu at all and Ctrl+C does nothing. That is the right default for the
app's own window, which is an application and not a page. It is the wrong one
for this window, which is retroachievements.org: copying a hash, a game's
name or an achievement's description is the ordinary thing to do there, and
nothing offered a way to do it.

The menu is the engine's own rather than one drawn in JavaScript, and that is
the whole point. Copy and paste through a real menu are the engine's, so the
clipboard never passes through this app: nothing here can read what is on it,
and neither can the page. An injected menu could only have offered paste by
fetching the clipboard's contents into the page first, which hands every word
you have ever copied to whichever site you happen to be looking at.

What is added on top is the one thing the engine has no way to know about:
that this window belongs to an app, and that "my browser" means a different
program. See browse.py for the window itself.
"""

from __future__ import annotations

import re
import urllib.parse

from . import browse

# The .NET delegates handed to WebView2 are only referenced from unmanaged
# code once they are attached, so nothing on the Python side would keep them
# alive and the collector is free to take them. It has, in testing - the menu
# stops responding a minute or two in. Held here for the life of the process.
_alive: list = []

_WORDS = {
    "en": {
        "link": "Open link in my browser",
        "page": "Open this page in my browser",
        "sel": "Open in my browser",
        "find": "Search the web for “{what}”",
    },
    "pt": {
        "link": "Abrir ligação no meu navegador",
        "page": "Abrir esta página no meu navegador",
        "sel": "Abrir no meu navegador",
        "find": "Pesquisar na web por “{what}”",
    },
}

SEARCH_URL = "https://duckduckgo.com/?q={q}"

# Long enough to say what was selected, short enough to stay a menu item.
_LABEL_MAX = 42

# What a hostname label may contain. Underscores may not, which is most of
# what separates 'Sonic_2_USA.zip' from a web address.
_LABEL_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9-]*")

# Endings that are real top-level domains and are, on a page about ROMs,
# almost always the end of a filename instead.
_NOT_A_TLD = frozenset({
    "zip", "iso", "bin", "cue", "chd", "rar", "gz", "md", "sh", "app",
})


def looks_like_url(text: str) -> str:
    """The selection as a URL to open, or "" if it isn't one.

    Deliberately strict. A menu entry that offers to open a page and then
    opens a search for the words instead is worse than not offering.
    """
    one = " ".join(str(text or "").split())
    if not one or " " in one:
        return ""
    if browse.is_web_url(one):
        return one
    # A bare host, the way a site prints it: 'retroachievements.org/game/1'.
    host = one.split("/", 1)[0].split("?", 1)[0]
    labels = host.split(".")
    if len(labels) < 2 or not all(_LABEL_RE.fullmatch(bit) for bit in labels):
        return ""
    tail = labels[-1].lower()
    # A hostname's last label is letters. '1.0.3' is a version, not a host.
    if len(tail) < 2 or not tail.isalpha():
        return ""
    # ...and on a page about ROMs, a name ending in one of these is a file,
    # whatever the registry has since sold as a domain. '.zip' is both.
    if tail in _NOT_A_TLD:
        return ""
    return "https://" + one


def search_url(text: str) -> str:
    words = " ".join(str(text or "").split())
    return SEARCH_URL.format(q=urllib.parse.quote(words, safe="")) if words else ""


def shorten(text: str, limit: int = _LABEL_MAX) -> str:
    one = " ".join(str(text or "").split())
    return one if len(one) <= limit else one[: limit - 1].rstrip() + "…"


def _view(window):
    """The WinForms form pywebview built for this window, or None.

    Only the form. Reading `.CoreWebView2` off the control is itself a call
    that has to happen on the thread that owns the window - it throws
    "CoreWebView2 can only be accessed from the UI thread" anywhere else -
    so that read belongs inside whatever _on_ui is about to run, never here.
    """
    from webview.platforms import winforms  # noqa: PLC0415 - Windows only

    return winforms.BrowserView.instances.get(window.uid)


def _engine(view):
    """The CoreWebView2, read from the UI thread by the caller."""
    browser = getattr(view, "browser", None)
    control = getattr(browser, "webview", None)
    return getattr(control, "CoreWebView2", None) if control is not None else None


def _on_ui(form, run):
    """Run on the thread that owns the window, wherever this was called from."""
    from System import Action  # noqa: PLC0415 - Windows only

    if getattr(form, "InvokeRequired", False):
        form.Invoke(Action(run))
    else:
        run()


def _entries(target, words):
    """What to offer for this click: (label, url) in the order shown."""
    out = []
    link = str(getattr(target, "LinkUri", "") or "") if \
        getattr(target, "HasLinkUri", False) else ""
    if browse.is_web_url(link):
        out.append((words["link"], link))

    picked = str(getattr(target, "SelectionText", "") or "") if \
        getattr(target, "HasSelection", False) else ""
    if picked.strip():
        as_url = looks_like_url(picked)
        if as_url:
            # Only when the selection is not already the link under the
            # pointer, or the same entry is offered twice.
            if as_url != link:
                out.append((words["sel"], as_url))
        else:
            out.append((words["find"].format(what=shorten(picked)),
                        search_url(picked)))

    page = str(getattr(target, "PageUri", "") or "")
    if browse.is_web_url(page) and page != link:
        out.append((words["page"], page))
    return [(label, url) for label, url in out if url]


def attach(window, lang: str = "en") -> bool:
    """Give one window the engine's menu, plus this app's own entries.

    False whenever any part of it is unavailable - another platform, another
    pywebview, a window whose engine has not finished starting. The window
    still works; it just has the menu it had before, which is none.
    """
    words = _WORDS.get(lang) or _WORDS["en"]
    done = []
    try:
        view = _view(window)
        if view is None:
            return False

        def wire():
            core = _engine(view)
            if core is None:
                return
            settings = core.Settings
            # The menu itself: copy, paste, select all, undo, and the
            # navigation entries, all handled by the engine.
            settings.AreDefaultContextMenusEnabled = True
            # ...and the same commands from the keyboard, which are no use
            # sitting in a menu if Ctrl+C does nothing. Developer tools stay
            # off - that is a separate setting and pywebview leaves it alone.
            settings.AreBrowserAcceleratorKeysEnabled = True

            def on_menu(_sender, args):
                try:
                    _extend(core, args, words)
                except Exception:  # noqa: BLE001 - the engine's menu still shows
                    pass

            core.ContextMenuRequested += on_menu
            _alive.append(on_menu)
            done.append(True)

        _on_ui(view, wire)
        return bool(done)
    except Exception:  # noqa: BLE001 - no menu is survivable, a crash is not
        return False


def snapshot(window) -> dict:
    """What the engine's settings actually say, read from the UI thread.

    Here so that "the menu is on" can be checked rather than assumed - the
    first version of attach() reported success while having thrown on the
    wrong thread.
    """
    out: dict = {}

    def read():
        core = _engine(_view(window))
        if core is None:
            return
        settings = core.Settings
        out["menus"] = bool(settings.AreDefaultContextMenusEnabled)
        out["keys"] = bool(settings.AreBrowserAcceleratorKeysEnabled)
        out["devtools"] = bool(settings.AreDevToolsEnabled)

    try:
        _on_ui(_view(window), read)
    except Exception as exc:  # noqa: BLE001
        out["error"] = f"{type(exc).__name__}: {exc}"
    return out


def _extend(core, args, words) -> None:
    """Append this app's entries to the menu the engine is about to show."""
    from Microsoft.Web.WebView2.Core import (  # noqa: PLC0415
        CoreWebView2ContextMenuItemKind)

    entries = _entries(args.ContextMenuTarget, words)
    if not entries:
        return

    env = core.Environment
    items = args.MenuItems
    items.Insert(items.Count, env.CreateContextMenuItem(
        "", None, CoreWebView2ContextMenuItemKind.Separator))

    for label, url in entries:
        item = env.CreateContextMenuItem(
            label, None, CoreWebView2ContextMenuItemKind.Command)

        def chose(_sender, _args, url=url):
            browse.open_external(url)

        item.CustomItemSelected += chose
        _alive.append(chose)
        items.Insert(items.Count, item)
