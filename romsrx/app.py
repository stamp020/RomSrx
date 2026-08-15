"""Desktop entry point: runs the local server and shows it in an app window.

The window is a WebView2 surface (already part of Windows 11), so the whole
existing frontend renders natively without an external browser and without
bundling a browser engine.

If pywebview isn't available the app still works - it falls back to opening
the default browser, which keeps `python -m romsrx serve` behaviour intact.
"""

from __future__ import annotations

import socket
import threading
import webbrowser
from http.server import ThreadingHTTPServer

from . import browse, db, downloads, paths, server, state

TITLE = "RomSrx"

DEFAULT_SIZE = (1280, 860)
MIN_SIZE = (900, 600)

# A page opened beside the app - a game's RetroAchievements page, say. Narrower
# than the app, because it is a page being read rather than a grid being
# scanned, and it has to fit next to something.
SIDE_SIZE = (980, 860)
SIDE_KEY = "webwindow"       # where that window's place and size are kept

# Where the browser engine keeps cookies and local storage.
#
# pywebview browses in private mode unless told otherwise, which throws all of
# that away when the app closes - so signing in to RetroAchievements would
# last exactly as long as the window did. Pointed at the user's own folder
# rather than the app's, so it survives replacing or reinstalling the app,
# like everything else worth keeping.
BROWSER_DIR = "browser"

# How much of the window has to land on a real display for it to count as
# reachable: enough width to aim at, and a title bar that isn't past the
# bottom edge.
GRAB_WIDTH = 80
GRAB_HEIGHT = 40


def free_port(preferred: int = 8770) -> int:
    """Use the usual port when it's free, otherwise let the OS pick one."""
    for candidate in (preferred, 0):
        with socket.socket() as probe:
            try:
                probe.bind(("127.0.0.1", candidate))
                return probe.getsockname()[1]
            except OSError:
                continue
    return preferred


def start_server(port: int) -> ThreadingHTTPServer:
    conn = db.connect()
    server.Handler.conn = conn
    downloads.manager.restore()   # bring back last session's queue
    httpd = ThreadingHTTPServer(("127.0.0.1", port), server.Handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd


def centre_of_primary(width: int, height: int, screens):
    """Middle of the main display.

    pywebview means to centre a window it wasn't given a position for, but it
    asks for `CenterScreen` after the window handle already exists, which is
    too late to have any effect - the window lands in the default cascade slot
    near the top-left instead. So the position is worked out here.
    """
    if not screens:
        return None, None
    primary = next((s for s in screens if s.x == 0 and s.y == 0), screens[0])
    return (primary.x + (primary.width - width) // 2,
            primary.y + (primary.height - height) // 2)


def reachable(x: int, y: int, width: int, screens) -> bool:
    """Would a window at this spot actually be visible and grabbable?

    Monitors get unplugged and resolutions change between runs. A window
    restored onto a display that is no longer there sits off-screen, where it
    can't be seen or dragged back - so a saved position is only used when its
    title bar still lands somewhere real.
    """
    for screen in screens:
        on_screen_x = (x + width > screen.x + GRAB_WIDTH
                       and x < screen.x + screen.width - GRAB_WIDTH)
        on_screen_y = screen.y <= y <= screen.y + screen.height - GRAB_HEIGHT
        if on_screen_x and on_screen_y:
            return True
    return False


class Geometry:
    """Remembers where and how big the window was, for the next run.

    Move, resize, maximise and restore each arrive on their own thread, so
    their order is not guaranteed - and maximising fires all three. Reading
    them as they come lands the maximised size and its -8,-8 origin in the
    record before the maximise flag gets there.

    So nothing is recorded on the spot: each event only updates a pending
    reading, and that is accepted as "what the user chose" once the window has
    been still for a moment. By then the flag has certainly arrived. That also
    keeps a window drag from writing hundreds of times.
    """

    SETTLE = 0.4      # seconds of stillness before a reading is believed

    def __init__(self, saved: dict, screens, key: str = "window",
                 default_size: tuple[int, int] = DEFAULT_SIZE) -> None:
        self._lock = threading.Lock()
        self._screens = list(screens)
        self._timer: threading.Timer | None = None
        self._key = key          # which window this is, in the settings file
        self.maximized = bool(saved.get("maximized"))

        width = int(saved.get("width") or default_size[0])
        height = int(saved.get("height") or default_size[1])
        self.width = max(width, MIN_SIZE[0])
        self.height = max(height, MIN_SIZE[1])

        # A remembered position is only used if it still lands on an attached
        # display; anything else opens in the middle of the main one.
        self.x = self.y = None
        if saved.get("x") is not None and saved.get("y") is not None:
            x, y = int(saved["x"]), int(saved["y"])
            if reachable(x, y, self.width, self._screens):
                self.x, self.y = x, y
        if self.x is None:
            self.x, self.y = centre_of_primary(self.width, self.height,
                                               self._screens)

        self._pending = [self.x, self.y, self.width, self.height]

    def _fills_a_screen(self, width: int, height: int) -> bool:
        """A maximised window matches the display's work area, which is the
        screen minus the taskbar. Belt and braces behind the maximise flag."""
        return any(width >= screen.width - 16 and height >= screen.height - 96
                   for screen in self._screens)

    def _restart_timer(self) -> None:
        if self._timer:
            self._timer.cancel()
        self._timer = threading.Timer(self.SETTLE, self._accept)
        self._timer.daemon = True
        self._timer.start()

    def _accept(self) -> None:
        """Believe the pending reading, unless the window is maximised."""
        with self._lock:
            x, y, width, height = self._pending
            if self.maximized or self._fills_a_screen(width, height):
                return
            self.x, self.y, self.width, self.height = x, y, width, height

    def place(self, x: int, y: int) -> None:
        """Choose a spot before the window opens, as though the user had left
        it there - so closing it without touching it remembers this one."""
        with self._lock:
            self.x, self.y = int(x), int(y)
            self._pending[0:2] = [self.x, self.y]

    def on_moved(self, x: int, y: int) -> None:
        with self._lock:
            self._pending[0:2] = [int(x), int(y)]
        self._restart_timer()

    def on_resized(self, width: int, height: int) -> None:
        with self._lock:
            self._pending[2:4] = [int(width), int(height)]
        self._restart_timer()

    def on_maximized(self) -> None:
        with self._lock:
            self.maximized = True

    def on_restored(self) -> None:
        with self._lock:
            self.maximized = False

    def save(self) -> None:
        if self._timer:
            self._timer.cancel()
        self._accept()          # take a reading that hasn't settled yet
        with self._lock:
            state.save(self._key, {
                "x": self.x, "y": self.y,
                "width": self.width, "height": self.height,
                "maximized": self.maximized,
            })


def in_browser(url: str, httpd, why: str) -> None:
    """Run without a window of our own, in whatever browser they have.

    Both ways of having no window end here: the Linux build ships without
    pywebview on purpose, and a Windows machine can turn out to have no
    WebView2 to draw with. Neither stops the app working - everything it does
    is served over this URL - so it says which happened and keeps going.
    """
    print(f"{TITLE} running at {url}\n({why} - opening your browser instead. "
          f"Ctrl+C to stop.)")
    webbrowser.open(url)
    try:
        threading.Event().wait()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.shutdown()


def main() -> None:
    port = free_port()
    url = f"http://127.0.0.1:{port}"
    httpd = start_server(port)
    downloads.manager.start()

    try:
        import webview  # noqa: PLC0415
    except ImportError:
        in_browser(url, httpd, "pywebview is not installed")
        return

    try:
        screens = webview.screens
    except Exception:  # noqa: BLE001 - no display info, so centre it
        screens = []
    geometry = Geometry(state.load("window", {}), screens)

    # Matches the page background, so startup doesn't flash white.
    window = webview.create_window(
        TITLE, url,
        width=geometry.width, height=geometry.height,
        x=geometry.x, y=geometry.y,
        maximized=geometry.maximized,
        min_size=MIN_SIZE, background_color="#0f1115",
    )

    def first_spot():
        """Where a side window goes the very first time, before it has a
        remembered place of its own: beside the app, so a game and its page
        are readable together. None means "no room" - centred is better than
        hanging off an edge, and centred is what Geometry already picked."""
        if geometry.maximized:
            return None              # nothing to sit beside; it covers the screen
        gap = 12
        right_edge = geometry.x + geometry.width + gap
        if reachable(right_edge, geometry.y, SIDE_SIZE[0], screens):
            return right_edge, geometry.y
        return None

    # Pages that won't be framed get a window instead of the panel. It keeps
    # its own place and size, separately from the app's, so a page dragged to
    # the second monitor opens there next time - and `reachable` means that
    # once that monitor is gone, it comes back to the main one rather than
    # opening somewhere nobody can reach it.
    def open_beside(url_: str, title_: str):
        saved = state.load(SIDE_KEY, {})
        side = Geometry(saved, screens, key=SIDE_KEY, default_size=SIDE_SIZE)
        if saved.get("x") is None or saved.get("y") is None:
            spot = first_spot()
            if spot:
                side.place(*spot)

        window_ = webview.create_window(
            title_, url_, width=side.width, height=side.height,
            x=side.x, y=side.y, maximized=side.maximized,
            min_size=MIN_SIZE, background_color="#0f1115")

        window_.events.moved += side.on_moved
        window_.events.resized += side.on_resized
        window_.events.maximized += side.on_maximized
        window_.events.restored += side.on_restored
        window_.events.closing += lambda: side.save()
        return window_

    browse.set_window_opener(open_beside)

    window.events.moved += geometry.on_moved
    window.events.resized += geometry.on_resized
    window.events.maximized += geometry.on_maximized
    window.events.restored += geometry.on_restored
    # `closing` is the one event pywebview runs synchronously, so the write
    # finishes before the window goes. Returning False there would cancel the
    # close, so this must return nothing.
    window.events.closing += lambda: geometry.save()

    try:
        # `private_mode=False` is what makes a sign-in outlive the window:
        # without it the engine keeps cookies in memory and drops them on the
        # way out. Both windows share the one profile, so signing in to a site
        # in the side window is remembered the next time it opens.
        webview.start(private_mode=False,
                      storage_path=str(paths.user(BROWSER_DIR)))
    except Exception as exc:  # noqa: BLE001 - whatever went wrong, the answer
        # The window is drawn by WebView2, which is part of Windows 11 and has
        # been delivered to Windows 10 by Windows Update for years - but not
        # on every machine. A stripped or long-unpatched install can be
        # without it, and then this fails here rather than at the import
        # above: pywebview itself is bundled, so it imports perfectly well and
        # only discovers there is nothing to draw with when asked to draw.
        #
        # The app works either way - it is a local web app, and the window is
        # a nicety - so it says what happened and carries on in the browser
        # instead of disappearing with no window and no message.
        # ...and there is no second window to be had either, so the page is
        # told so plainly rather than finding out by way of a failure every
        # time someone opens a game's page.
        browse.set_window_opener(None)
        in_browser(url, httpd,
                   f"this Windows has no WebView2 runtime ({type(exc).__name__})")
        return
    finally:
        geometry.save()          # in case closing never fired

    httpd.shutdown()


if __name__ == "__main__":
    main()
