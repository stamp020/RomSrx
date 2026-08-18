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

import json
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


# -- the controls that window has to bring with it ----------------------
#
# A window made this way has no chrome: no address bar, no back button, no
# menu. That is right for a page you opened to read, and wrong the moment you
# follow a link out of it - which on RetroAchievements is one click away, and
# without this there is no way back short of closing the window.
#
# So the controls are put into the page itself, on every page it loads. Styles
# are set through the CSSOM rather than a style attribute or a <style> element,
# because a site is free to forbid both with Content-Security-Policy and
# several do; assigning to element.style is not something CSP has a say in.
_NAV_JS = r"""
(() => {
  const LABELS = __LABELS__;
  const ID = "romsrx-nav";
  if (document.getElementById(ID)) return;   // this page already has it
  if (!document.body) return;                // nothing to attach to yet

  // The online patcher is one page that does one job - there is nothing to go
  // back to, and the bar only sits on top of the controls it needs.
  if (/(^|\.)marcrobledo\.com$/i.test(location.hostname)) return;

  // Nor on this app's own pages. The achievements window is served from here
  // and has nowhere to go back to either; a floating browser bar over it would
  // be the app putting browser controls on itself.
  if (/^(127\.0\.0\.1|localhost|\[::1\])$/i.test(location.hostname)) return;

  // Set as important, all of them. This bar is a guest on someone else's
  // page, and a site with its own opinion about what a button looks like
  // would otherwise win and leave these the wrong size.
  const put = (el, styles) => {
    for (const [key, value] of Object.entries(styles)) {
      el.style.setProperty(
        key.replace(/[A-Z]/g, (m) => "-" + m.toLowerCase()), value, "important");
    }
  };

  const bar = document.createElement("div");
  bar.id = ID;
  put(bar, {
    position: "fixed", left: "14px", bottom: "14px", zIndex: "2147483647",
    display: "flex", gap: "2px", padding: "4px",
    background: "rgba(18,20,25,0.92)", borderRadius: "11px",
    border: "1px solid rgba(255,255,255,0.14)",
    boxShadow: "0 6px 22px rgba(0,0,0,0.45)",
    font: "15px system-ui, -apple-system, Segoe UI, sans-serif",
    opacity: "0.45", transition: "opacity .15s",
  });
  // Out of the way until wanted: a bar sitting at full strength over someone
  // else's page is a nuisance on every page that did not need it.
  bar.addEventListener("mouseenter", () => { put(bar, {opacity: "1"}); });
  bar.addEventListener("mouseleave", () => { put(bar, {opacity: "0.45"}); });

  const make = (glyph, title, run) => {
    const b = document.createElement("button");
    b.type = "button";
    b.textContent = glyph;
    b.title = title;
    put(b, {
      width: "30px", height: "27px", border: "0", borderRadius: "8px",
      background: "transparent", color: "#e6e8ec", cursor: "pointer",
      font: "inherit", lineHeight: "1", padding: "0",
    });
    b.addEventListener("mouseenter", () => {
      put(b, {background: "rgba(255,255,255,0.13)"});
    });
    b.addEventListener("mouseleave", () => { put(b, {background: "transparent"}); });
    b.addEventListener("click", (ev) => {
      ev.preventDefault();
      if (dragged) return;      // that press was moving the bar, not pressing this
      run();
    });
    bar.appendChild(b);
    return b;
  };

  make("←", LABELS.back, () => history.back());
  make("→", LABELS.forward, () => history.forward());
  make("↻", LABELS.reload, () => location.reload());
  document.body.appendChild(bar);

  // -- where it sits, and moving it ---------------------------------------
  // Dragged anywhere and remembered. Kept in the page's own storage, which
  // outlives the window because this app browses with storage turned on so
  // that signing in sticks; a site that refuses storage just gets the
  // default corner back each time, which is no worse than not having this.
  const KEY = "romsrx-nav-pos";

  // Where it sits is kept as a fraction of the room available, not as a
  // number of pixels. Pixels were only ever clamped back inside a resized
  // window, so a bar put in the middle of a narrow one sat well left of
  // centre the moment the window was widened, and against the right edge
  // when it was narrowed. A fraction means the middle stays the middle and a
  // corner stays that corner, whatever the window does next.
  const room = () => ({
    w: Math.max(0, innerWidth - (bar.offsetWidth || 110)),
    h: Math.max(0, innerHeight - (bar.offsetHeight || 37)),
  });

  const clamp01 = (n) => Math.min(1, Math.max(0, n));

  // Pixels in, fraction out - what a drag produces.
  const settle = (x, y) => {
    const { w, h } = room();
    const at = { fx: w ? clamp01(x / w) : 0, fy: h ? clamp01(y / h) : 0 };
    place(at);
    return at;
  };

  // Fraction in, pixels out - what a resize and a restore need.
  function place(at) {
    const { w, h } = room();
    put(bar, {
      left: Math.round(at.fx * w) + "px",
      top: Math.round(at.fy * h) + "px",
      bottom: "auto", right: "auto",
    });
  }

  let placed = null;
  try {
    const saved = JSON.parse(localStorage.getItem(KEY) || "null");
    if (saved && typeof saved.fx === "number" && typeof saved.fy === "number") {
      placed = { fx: clamp01(saved.fx), fy: clamp01(saved.fy) };
      place(placed);
    } else if (saved && typeof saved.x === "number"
               && typeof saved.y === "number") {
      // Where an older version left it, in pixels. Read once against the
      // window as it is now and kept as a fraction from here on.
      placed = settle(saved.x, saved.y);
    }
  } catch (err) { /* storage refused; the default corner is fine */ }

  addEventListener("resize", () => {
    if (placed) place(placed);
  });

  let dragged = false;
  let from = null;

  bar.addEventListener("pointerdown", (ev) => {
    if (ev.button !== 0) return;
    const box = bar.getBoundingClientRect();
    from = { x: ev.clientX, y: ev.clientY, left: box.left, top: box.top };
    dragged = false;
    // Capture is claimed on the first real movement, not here. Capturing at
    // press time retargets the click that follows to whatever holds the
    // capture - the bar - so it never reaches the button under the pointer,
    // and every button silently stops working.
  });

  bar.addEventListener("pointermove", (ev) => {
    if (!from) return;
    const dx = ev.clientX - from.x;
    const dy = ev.clientY - from.y;
    // A press that has not travelled is still a press on a button. Only past
    // a few pixels does it become a drag, so the buttons stay clickable.
    if (!dragged && Math.abs(dx) < 4 && Math.abs(dy) < 4) return;
    if (!dragged) {
      // Now it is a drag rather than a press, so keeping the pointer is both
      // safe and wanted: the click it retargets is one that should not count.
      try { bar.setPointerCapture(ev.pointerId); } catch (err) { /* none */ }
    }
    dragged = true;
    put(bar, {opacity: "1", cursor: "grabbing"});
    ev.preventDefault();
    placed = settle(from.left + dx, from.top + dy);
  });

  const drop = (ev) => {
    if (!from) return;
    from = null;
    put(bar, {cursor: "grab"});
    try { bar.releasePointerCapture(ev.pointerId); } catch (err) { /* gone */ }
    if (dragged && placed) {
      try { localStorage.setItem(KEY, JSON.stringify(placed)); }
      catch (err) { /* storage refused; it moves for this page only */ }
    }
    // Cleared after the click that follows this release has been and gone.
    setTimeout(() => { dragged = false; }, 0);
  };
  bar.addEventListener("pointerup", drop);
  bar.addEventListener("pointercancel", drop);

  // The same three from the keyboard. Captured, so a page that handles these
  // itself does not get to swallow them, and F5 works the way it does
  // everywhere else - the engine's own shortcuts are switched off in a window
  // like this one.
  addEventListener("keydown", (ev) => {
    const key = ev.key;
    if (key === "F5" || ((ev.ctrlKey || ev.metaKey) && key.toLowerCase() === "r")) {
      ev.preventDefault();
      location.reload();
    } else if (ev.altKey && key === "ArrowLeft") {
      ev.preventDefault();
      history.back();
    } else if (ev.altKey && key === "ArrowRight") {
      ev.preventDefault();
      history.forward();
    }
  }, true);
})();
"""

# The tooltips, in the languages the app itself speaks. Only three strings, so
# they live here rather than reaching into the page's translation table - the
# window they belong to is not the app's own page and cannot read it.
_NAV_WORDS = {
    "en": {"back": "Back", "forward": "Forward", "reload": "Reload"},
    "pt": {"back": "Retroceder", "forward": "Avançar", "reload": "Recarregar"},
}


def nav_js(lang: str = "en") -> str:
    """The controls, with their tooltips in the app's language."""
    words = _NAV_WORDS.get(lang) or _NAV_WORDS["en"]
    return _NAV_JS.replace("__LABELS__", json.dumps(words))


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
