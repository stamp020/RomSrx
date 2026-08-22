"""Local HTTP server: static frontend plus a small JSON search API."""

from __future__ import annotations

import json
import mimetypes
import os
import sys
import threading
import time
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from . import (account, artwork, browse, cores, covers, db, downloads,
               hardcore, indexer, library, patcher, preview, profile, rahash,
               recommend, retro, saves, state, updates, wanted)
from . import (autosave, emufind, history, racred, speedtest, spell,
               sync, syncstore, taskbar,
               times as ratimes)
from .paths import resource

WEB_ROOT = resource("web")

# Shared state for a reindex kicked off from the web UI.
_index_lock = threading.Lock()
_index_state: dict = {"running": False, "log": [], "summary": None,
                      "done": 0, "total": 0, "started": 0.0}

# Reindexing is almost entirely waiting on archive.org, and measurement says
# this number does not matter: a full run takes ~120s at 2, 4 or 8 workers
# alike. The metadata endpoint meters a single caller at roughly one item a
# second however many connections you open - ask for eight at once and each
# one takes eight times as long. Four is kept because it is no slower than
# eight and half the load on someone else's servers.
INDEX_WORKERS = 4

# How far along a patch is, for the bar at the bottom of the page. One at a
# time is the only case worth handling: patching is started from a menu and
# the page waits for it.
_patch_state: dict = {"running": False, "done": 0, "total": 0, "name": ""}

# A sweep of the shelf, checking every copy against the set it belongs to.
# Unlike a patch, this is not something the page waits for: it reads every
# byte of every cartridge in the library, so it runs behind the page and is
# asked how it is getting on. `cancel` is how the button stops it - the sweep
# checks it between files, so it never stops halfway through a hash.
_verify_lock = threading.Lock()
_verify_state: dict = {"running": False, "done": 0, "total": 0, "rows": [],
                       "counts": {}, "started": 0.0, "reason": "",
                       "cancel": False}


def _run_verify(items: list) -> None:
    def progress(done: int, total: int) -> None:
        _verify_state["done"], _verify_state["total"] = done, total

    def stop() -> bool:
        return bool(_verify_state["cancel"])

    try:
        # The whole library is in hand exactly once per sweep, which is the
        # only moment it is safe to drop what was worked out for games that
        # have since been deleted.
        rahash.prune({str(one.get("path") or "") for one in items})
        found = retro.verify(items, progress=progress, stop=stop)
        if found.get("ok"):
            _verify_state["rows"] = found.get("rows") or []
            _verify_state["counts"] = found.get("counts") or {}
        else:
            _verify_state["reason"] = str(found.get("reason") or "unreachable")
    except Exception:  # noqa: BLE001 - surface it as a reason, never a crash
        _verify_state["reason"] = "unreachable"
    finally:
        _verify_state["running"] = False


# Timing every set on the site. One long job, done once and then only ever
# topped up - see times.py - so it is a background thread with a progress
# figure and a way out, exactly like the compatibility sweep.
_times_lock = threading.Lock()
_times_state: dict = {"running": False, "done": 0, "total": 0,
                      "started": 0.0, "cancel": False, "reason": ""}


def _run_times(pool: list) -> None:
    def progress(done: int, total: int) -> None:
        _times_state["done"], _times_state["total"] = done, total

    def stop() -> bool:
        return bool(_times_state["cancel"])

    try:
        ratimes.scan(pool, progress=progress, stop=stop)
    except Exception:  # noqa: BLE001 - surface it, never crash the server
        _times_state["reason"] = "unreachable"
    finally:
        _times_state["running"] = False


def _relaunch() -> None:
    """Start a second copy of this app, however this one was started.

    Detached on purpose: the new copy has to outlive this one, which is about
    to stop. A packaged build is its own executable; from source it is the
    module, since sys.argv[0] there is a file inside the package rather than
    something Python can be pointed at.
    """
    import subprocess  # noqa: PLC0415 - only ever needed here

    if getattr(sys, "frozen", False):
        command = [sys.executable, *sys.argv[1:]]
    else:
        command = [sys.executable, "-m", "romsrx", *sys.argv[1:]]

    extras = {}
    if os.name == "nt":
        # Otherwise the new process is tied to this console and goes down
        # with it, which is exactly what a restart must not do.
        extras["creationflags"] = (subprocess.DETACHED_PROCESS
                                   | subprocess.CREATE_NEW_PROCESS_GROUP)
    else:
        extras["start_new_session"] = True
    subprocess.Popen(command, close_fds=True, **extras)  # noqa: S603


def _run_index(db_path) -> None:
    conn = db.connect(db_path or db.DB_PATH)
    def progress(line: str = "") -> None:
        _index_state["log"].append(str(line))

    def counts(done: int, total: int) -> None:
        _index_state["done"], _index_state["total"] = done, total

    try:
        config = indexer.load_config()
        summary = indexer.index_all(conn, config, progress=progress,
                                    counts=counts, workers=INDEX_WORKERS)
        _index_state["summary"] = summary
        progress(f"Done: {summary['files']:,} files from "
                 f"{summary['ok']} source(s), {summary['failed']} failed.")
    except Exception as exc:  # noqa: BLE001 - surface it in the UI log
        progress(f"ERROR: {exc}")
    finally:
        _index_state["running"] = False


class Handler(BaseHTTPRequestHandler):
    server_version = "RomSrx"
    # Where the index is. Not a connection: each request thread opens its own
    # against this path, because one sqlite3 connection shared between them
    # hands back torn answers. See db.thread_conn.
    db_path = None

    # Keep the connection open between requests. The default here is HTTP/1.0,
    # which closes after every response, so one screen of this app - a cover
    # per card, an achievement check per file, play times, the search itself -
    # opened and threw away a hundred TCP connections, and enough of them were
    # refused outright that the search box regularly showed one query's text
    # over another query's results.
    #
    # Safe because every response has an accurate Content-Length: there are
    # only three shapes, _send_json, _send_file and the one 302, and
    # send_error sets its own. A response without one would hang a 1.1 client
    # waiting for a body that never ends.
    protocol_version = "HTTP/1.1"
    # ...and a connection nobody is using must not hold its thread for ever.
    timeout = 30

    def _name_sources(self) -> None:
        """Fill in where a download came from, for jobs that never recorded it.

        Here rather than in downloads.py because this is where the index is:
        the manager knows each job's URL and nothing at all about shelves.
        Once written the job keeps it, so a queue settles after one poll
        rather than being looked up every two seconds.
        """
        blank = downloads.manager.unnamed()
        if not blank:
            return
        try:
            found = db.sources_for(self.conn, blank.values())
        except Exception:  # noqa: BLE001 - a panel is not worth an exception
            return
        downloads.manager.name_sources(
            {job_id: found.get(url, "") for job_id, url in blank.items()})

    @property
    def conn(self):
        """This thread's connection to the index."""
        return db.thread_conn(self.db_path or db.DB_PATH)

    def finish(self):
        # The thread is about to go back to the pool or end, and the
        # connection it opened should not outlive the work it was for.
        try:
            super().finish()
        finally:
            db.close_thread_conn()

    def log_error(self, fmt, *args):
        # With keep-alive on, a connection nobody is using reaches its
        # timeout and closes, and the base class calls that an error. It is
        # the ordinary end of an idle connection, and printing it once per
        # connection buries anything that matters.
        if "timed out" in str(fmt):
            return
        super().log_error(fmt, *args)

    def log_message(self, fmt, *args):  # quieter console
        if "/api/" in str(args[0] if args else ""):
            return
        super().log_message(fmt, *args)

    # -- helpers ---------------------------------------------------------
    def _send_json(self, payload, status: int = 200) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, path: Path) -> None:
        try:
            body = path.read_bytes()
        except OSError:
            self.send_error(404, "Not found")
            return
        ctype, _ = mimetypes.guess_type(path.name)
        self.send_response(200)
        self.send_header("Content-Type", ctype or "application/octet-stream")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(body)

    # -- routing ---------------------------------------------------------
    def do_GET(self) -> None:  # noqa: N802
        parsed = urllib.parse.urlparse(self.path)
        route = parsed.path.rstrip("/") or "/"
        params = urllib.parse.parse_qs(parsed.query)

        def param(key: str, default: str = "") -> str:
            return params.get(key, [default])[0].strip()

        def param_list(key: str) -> list[str]:
            """Accept repeated params and comma-separated values alike."""
            out: list[str] = []
            for raw in params.get(key, []):
                out.extend(v.strip() for v in raw.split(",") if v.strip())
            return out

        if route == "/api/search":
            try:
                limit = max(1, min(int(param("limit", "40")), 200))
                offset = max(0, int(param("offset", "0")))
            except ValueError:
                limit, offset = 40, 0
            result = db.search(
                self.conn,
                param("q"),
                console=param_list("console"),
                region=param_list("region"),
                ext=param_list("ext"),
                source=param_list("source"),
                ra=param("ra") in ("1", "true", "yes"),
                has_sets=self._only_with_sets(param("sets")),
                limit=limit,
                offset=offset,
            )
            result["limit"] = limit
            result["offset"] = offset
            # Nothing found, and something was typed: the index holds every
            # title there is, so it can say what was probably meant instead of
            # asking somebody to guess again. Only on a miss, and only on the
            # first page, so an ordinary search never pays for it.
            if not result.get("games") and not offset and param("q").strip():
                near = spell.suggest(self.conn, param("q"))
                if near:
                    result["suggest"] = near
            self._send_json(result)
            return

        # Box art, resolved against what the thumbnail server actually has
        # rather than guessed at. Answers with a redirect, so the image itself
        # still comes straight from their CDN and never through here; a 404
        # sends the page back to its own guesses, which is what it did before
        # this existed. See covers.py.
        if route == "/api/cover":
            target = covers.resolve(param("console"), param("name"))
            if not target:
                self.send_error(404, "No art for that game")
                return
            self.send_response(302)
            self.send_header("Location", target)
            # Worth remembering: the answer only changes when the thumbnail
            # server gains a cover, and a page redraw asks for every tile again.
            self.send_header("Cache-Control", "max-age=86400")
            self.send_header("Content-Length", "0")
            self.end_headers()
            return

        # Everything about one game at once, for the preview panel. One game,
        # opened deliberately - see preview.py.
        if route == "/api/preview":
            self._send_json(preview.build(param("console"), param("name")))
            return

        # How long one game takes, from RetroAchievements' own medians. One
        # game, asked for deliberately - see retro.how_long.
        if route == "/api/howlong":
            try:
                game = int(param("id") or 0)
            except ValueError:
                game = 0
            self._send_json(retro.how_long(param("console"), param("name"), game))
            return

        # Every achievement in one set, and which of them the user has. Asked
        # for by pressing "Load achievements", never as part of drawing the
        # window - see retro.achievements. `refresh` is the button beside the
        # list, for somebody who has just earned one.
        if route == "/api/achievements":
            try:
                game = int(param("id") or 0)
            except ValueError:
                game = 0
            self._send_json(retro.achievements(
                game, refresh=param("refresh") == "1"))
            return

        # Who is signed in to RetroAchievements, for the strip in the header:
        # their picture, their points, and what they are playing. One request,
        # kept for a few minutes - see profile.py.
        if route == "/api/ra/me":
            self._send_json(profile.me(refresh=param("refresh") == "1"))
            return

        # ...and everything behind it, for the window: the awards, the last
        # games, and the people they follow.
        if route == "/api/ra/profile":
            self._send_json(profile.full(refresh=param("refresh") == "1"))
            return

        # ...or one panel of it at a time, which is how the window actually
        # asks: it fetches its blocks in the order they are arranged, so the
        # first thing on screen is the first thing fetched. See profile.py.
        if route.startswith("/api/ra/panel/"):
            fresh = param("refresh") == "1"
            panel = {
                "recent": profile.recent,
                "awards": profile.awards,
                "following": profile.following,
                "figures": profile.figures,
            }.get(route.rsplit("/", 1)[-1])
            if not panel:
                self._send_json({"error": "Unknown panel."}, status=404)
                return
            self._send_json(panel(refresh=fresh))
            return

        # One of those people, in more detail. Asked for when their row is
        # opened out, so following a dozen people costs a dozen requests only
        # if you open a dozen rows.
        if route == "/api/ra/user":
            self._send_json(profile.user(param("u")))
            return

        # What one game's set is worth - achievements, points, RetroPoints and
        # the ratio between them. Asked for by a card that is being hovered,
        # so it is one game at a time; retro.how_long keeps the answer for a
        # fortnight, which is what makes that affordable.
        if route == "/api/ra/game":
            try:
                game = int(param("id") or 0)
            except ValueError:
                game = 0
            found = retro.how_long(param("console"), param("name"), game) \
                if game or param("name") else {}
            self._send_json({
                "ok": bool(found.get("ok")),
                "id": found.get("id") or game,
                "title": found.get("title") or "",
                "achievements": found.get("achievements") or 0,
                "points": found.get("points") or 0,
                "retropoints": found.get("retropoints") or 0,
                "ratio": found.get("ratio") or 0,
            })
            return

        # Who is ahead among the people you follow, today, this week or all
        # time. The two windows cost a request per person, so the page asks
        # for them rather than getting them with the profile.
        # How much of each set the user has earned, asked for again. The same
        # table the shelf's badges are drawn from - see retro.progress.
        if route == "/api/ra/progress":
            self._send_json({"progress": {
                str(game): row for game, row
                in retro.progress(refresh=param("refresh") == "1").items()}})
            return

        if route == "/api/ra/ranking":
            self._send_json(profile.ranking(param("window") or "all"))
            return

        # ...and how far through one game that person is, for a row of theirs
        # opened out. See profile.user_game.
        if route == "/api/ra/user/game":
            try:
                game = int(param("g") or 0)
            except ValueError:
                game = 0
            self._send_json(profile.user_game(param("u"), game))
            return

        # The comment thread on one achievement, opened from its row. One
        # achievement at a time - see retro.comments.
        # The game's own set and any subsets built on it, so the window can
        # offer them without the reader going back to the app. See
        # retro.related_sets.
        if route == "/api/achievements/related":
            try:
                game = int(param("id") or 0)
            except (TypeError, ValueError):
                game = 0
            self._send_json(retro.related_sets(game) or
                            {"console": "", "title": "", "sets": []})
            return

        if route == "/api/achievements/comments":
            try:
                one = int(param("id") or 0)
            except ValueError:
                one = 0
            self._send_json(retro.comments(one, refresh=param("refresh") == "1"))
            return

        if route == "/api/facets":
            self._send_json(db.facets(self.conn))
            return

        if route == "/api/stats":
            self._send_json(db.stats(self.conn))
            return

        if route == "/api/account":
            self._send_json(account.status())
            return

        # Which of the two places covers come from first. Asked once when the
        # page loads, because the page tries its own thumbnail-server guesses
        # before it ever gets here and has to know whether to bother. No keys
        # in it, so unlike the rest of /api/artwork it is not local-only.
        # How much there is to back up, so the tick box can say so before it
        # is ticked. See saves.py.
        # What still points at a game that is no longer on the disk.
        if route == "/api/library/stale":
            self._send_json(library.stale())
            return

        # Whether this build can run a torrent at all. libtorrent is
        # optional - it publishes no wheel for every Python - and the page
        # offers the magnet to another client where it is missing rather than
        # a button that would do nothing.
        if route == "/api/torrent/state":
            from . import torrent  # noqa: PLC0415 - optional
            self._send_json({"available": torrent.available()})
            return

        if route == "/api/saves/status":
            self._send_json(autosave.status())
            return

        if route == "/api/saves":
            self._send_json(saves.summary())
            return

        # Every session's saves, filed by emulator and then by when it ended.
        # See history.py.
        if route == "/api/history":
            self._send_json(history.listing())
            return

        # Carrying settings and saves between computers. Local-only: the
        # answer names folders on this machine and how big they are.
        if route == "/api/sync":
            if not self._is_local():
                self._send_json({"error": "Only from this computer."},
                                status=403)
                return
            self._send_json(syncstore.status())
            return

        # Which emulators are signed in to RetroAchievements and which could
        # be. Local-only: the answer names config file paths, and the reply
        # would otherwise say who is logged in to what on this machine.
        if route == "/api/racred":
            if not self._is_local():
                self._send_json({"error": "Only from this computer."},
                                status=403)
                return
            try:
                self._send_json(racred.look())
            except Exception as exc:  # noqa: BLE001 - reported, not raised
                self._send_json({"error": f"{type(exc).__name__}: {exc}"},
                                status=500)
            return

        if route == "/api/artwork/mode":
            self._send_json({"mode": artwork.mode()})
            return

        # The optional artwork services and whether they are usable. Only ever
        # asked for by the settings page, and only from this machine: it comes
        # back with the keys in it so the boxes can be edited rather than
        # retyped from memory.
        if route == "/api/artwork":
            if not self._is_local():
                self._send_json({"error": "Only from this computer."}, status=403)
                return
            self._send_json(artwork.status())
            return

        if route == "/api/downloads":
            self._name_sources()
            self._send_json(downloads.manager.snapshot())
            return

        if route == "/api/downloads/settings":
            self._send_json(downloads.load_settings())
            return

        if route == "/api/prefs":
            self._send_json(state.prefs())
            return

        if route == "/api/patch/progress":
            self._send_json(dict(_patch_state))
            return

        if route == "/api/update":
            self._send_json(updates.check(sys.platform,
                                          force=param("force") == "1"))
            return

        if route == "/api/release":
            self._send_json(updates.notes_for(param("version")
                                              or updates.__version__))
            return

        if route == "/api/cart":
            self._send_json({"items": state.cart()})
            return

        if route == "/api/playlists":
            self._send_json({"playlists": state.playlists()})
            return

        if route == "/api/recent":
            self._send_json({"recent": state.recent()})
            return

        if route == "/api/library":
            consoles = [row["value"] for row in db.facets(self.conn)["consoles"]]
            # The index goes in too: it is what puts a game found loose in the
            # download folder under its own console instead of "Unsorted".
            self._send_json(library.scan(consoles, self.conn))
            return

        if route == "/api/downloads/folders":
            settings = downloads.load_settings()
            overrides = settings.get("console_folders") or {}
            # Not `covers`: that is the module this handler also calls, and
            # a local of the same name shadows it for the whole function.
            cover_dirs = settings.get("cover_folders") or {}
            cover_auto = settings.get("cover_auto") or {}
            cover_delete = settings.get("cover_delete") or {}
            emulators = settings.get("emulators") or {}
            emu_cores = settings.get("emulator_cores") or {}
            emu_args = settings.get("emulator_args") or {}
            consoles = [{
                "console": row["value"],
                "files": row["count"],
                "override": overrides.get(row["value"], ""),
                "effective": str(downloads.folder_for(row["value"])),
                "cover": cover_dirs.get(row["value"], ""),
                "coverAuto": bool(cover_auto.get(row["value"])),
                "coverDelete": bool(cover_delete.get(row["value"])),
                "emulator": emulators.get(row["value"], ""),
                "emulatorCore": emu_cores.get(row["value"], ""),
                "emulatorArgs": emu_args.get(row["value"], ""),
            } for row in db.facets(self.conn)["consoles"]]
            consoles.sort(key=lambda c: c["console"])
            self._send_json({
                "base": settings["folder"],
                # Which consoles this app can fetch a core for. Sent with the
                # folders so the page can draw the button in the right rows
                # without asking a second time.
                "coreConsoles": sorted(cores.BEST),
                "per_console": settings["per_console"],
                "consoles": consoles,
            })
            return

        if route == "/api/emulators/find":
            # Reads directory listings and nothing else. Nothing is launched
            # and nothing is saved - what comes back is a suggestion, and the
            # page asks before it changes a console already pointed at
            # something.
            if not self._is_local():
                self._send_json({"error": "Only from this computer."}, status=403)
                return
            self._send_json(emufind.scan())
            return

        if route == "/api/times/status":
            started = _times_state["started"]
            self._send_json({
                **ratimes.counts(),
                "running": _times_state["running"],
                "done": _times_state["done"],
                "total": _times_state["total"],
                "cancelled": bool(_times_state["cancel"]),
                "reason": _times_state["reason"],
                "elapsed": round(time.time() - started, 1) if started else 0,
            })
            return

        if route == "/api/hardcore":
            # Read-only, and only RetroArch's own file. Nothing is written and
            # the token is never looked at - see hardcore.py.
            self._send_json(hardcore.status())
            return

        if route == "/api/ra/wanted":
            # Their list, joined to the index: what you said you wanted to
            # play, and which of it this app can actually fetch.
            self._send_json(wanted.listing(self.conn,
                                           refresh=param("refresh") == "1"))
            return

        if route == "/api/library/verified":
            # What was worked out on some earlier run. Asked for as the shelf
            # is drawn, so the marks are simply there - no network, no
            # hashing, and nothing for the user to press.
            self._send_json(retro.verdicts())
            return

        if route == "/api/library/verify/status":
            started = _verify_state["started"]
            running = _verify_state["running"]
            self._send_json({
                "running": running,
                "done": _verify_state["done"],
                "total": _verify_state["total"],
                "counts": _verify_state["counts"],
                "reason": _verify_state["reason"],
                "cancelled": bool(_verify_state["cancel"]),
                # Only when there is nothing left to add to them. A shelf of
                # two thousand is a few hundred kilobytes of verdicts, and
                # sending that with every poll would cost more than the
                # hashing does.
                "rows": [] if running else _verify_state["rows"],
                "elapsed": round(time.time() - started, 1) if started else 0,
            })
            return

        if route == "/api/index/status":
            started = _index_state["started"]
            self._send_json({
                "running": _index_state["running"],
                "log": _index_state["log"][-200:],
                "summary": _index_state["summary"],
                "done": _index_state["done"],
                "total": _index_state["total"],
                # Sent rather than an estimate, so the page can work out the
                # time left even when it was opened halfway through a run.
                "elapsed": round(time.time() - started, 1) if started else 0,
            })
            return

        # User-supplied cover images live outside the web folder.
        if route.startswith("/covers/"):
            name = os.path.basename(urllib.parse.unquote(route[len("/covers/"):]))
            image = library.COVERS_DIR / name
            if name and image.is_file():
                self._send_file(image)
            else:
                self.send_error(404, "Not found")
            return

        # Static files. Confinement is a path comparison, not a string one:
        # comparing text let "/../webview/x" through in the packaged build,
        # because ".../_internal/webview" does start with ".../_internal/web".
        rel = route.lstrip("/") or "index.html"
        target = (WEB_ROOT / rel).resolve()
        if not target.is_relative_to(WEB_ROOT.resolve()):
            self.send_error(403, "Forbidden")
            return
        if target.is_dir():
            target = target / "index.html"
        if not target.is_file():
            self.send_error(404, "Not found")
            return
        self._send_file(target)

    def _only_with_sets(self, asked: str) -> bool:
        """Narrow to games RetroAchievements has a set for, if asked to.

        Which games those are is not in the index - it is their catalogue
        matched against this one - so the answer is handed to the connection
        as a temporary table before the query runs. Built once per thread and
        rebuilt only when the answer changes; see db.note_sets.

        False on any failure. A filter that cannot be applied has to show
        everything rather than nothing: an empty page would read as "you own
        nothing with achievements", which is a different and wrong answer.
        """
        if str(asked or "").lower() not in ("1", "true", "yes", "on"):
            return False
        try:
            counted: dict = {}
            for row in wanted.indexed_sets(self.conn):
                if row.get("console") and row.get("norm"):
                    key = (row["console"], row["norm"])
                    counted[key] = counted.get(key, 0) + 1
            if not counted:
                return False
            db.note_sets(self.conn, counted)
            return True
        except Exception:  # noqa: BLE001 - see the docstring
            return False

    def _read_json(self) -> dict:
        try:
            length = int(self.headers.get("Content-Length") or 0)
            if not length:
                return {}
            return json.loads(self.rfile.read(length).decode("utf-8", "replace"))
        except (ValueError, TypeError):
            return {}

    def _ranked_scope(self, body: dict) -> dict:
        """What a whole-site ranking is allowed to rank, from the page's own
        search box and filter bar.

        The three site-wide orders used to be blind to both: they were built
        from RetroAchievements' lists rather than from a search, so typing a
        title and then asking for "quickest to beat" answered a question about
        the entire catalogue and threw the title away - and a region picked in
        the bar was ignored the same way. They are still rankings of the whole
        site; this only says which part of it is on screen.

        `allow` is left as None when nothing has been typed or picked, because
        then it could only ever say "all of it" and working that out means
        reading every row in the index.
        """
        def listed(key: str) -> list[str]:
            raw = body.get(key)
            if isinstance(raw, str):
                raw = [raw]
            out: list[str] = []
            for one in raw or []:
                out.extend(v.strip() for v in str(one).split(",") if v.strip())
            return out

        query = str(body.get("q") or "").strip()
        consoles = listed("console")
        regions = listed("region")
        exts = listed("ext")
        ra = bool(body.get("ra"))

        plan = db.plan_for(self.conn, query) if query else ("", "")
        # The console filter is deliberately left out of the SQL that picks
        # each card's copies: these lists have already chosen one console per
        # game, and the pool itself is narrowed by console below.
        where, params = db.file_filter(None, regions, exts, None, ra)
        narrowed = bool(query or regions or exts or ra)
        return {
            "consoles": consoles,
            "allow": db.scope_of(self.conn, query, console=consoles,
                                 region=regions, ext=exts, ra=ra, plan=plan)
                     if narrowed else None,
            "where": where,
            "params": params,
            "facets": db.search_facets(self.conn, query, console=consoles,
                                       region=regions, ext=exts, ra=ra,
                                       plan=plan),
        }

    def _is_local(self) -> bool:
        """Credentials may only be posted from this machine, never the LAN."""
        return self.client_address[0] in ("127.0.0.1", "::1", "localhost")

    def _save_cover(self, body: dict) -> dict:
        """Write a cover the user right-clicked to a file they choose."""
        url = str(body.get("url") or "")
        suggested = downloads.safe_name(str(body.get("name") or "cover.png"))

        # What the page is showing may be our own resolved-cover address,
        # which is a redirect rather than an image. Turn it back into the
        # real one here - `fetch_image` is handed URLs, not routes.
        if url.startswith("/api/cover?"):
            asked = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
            url = covers.resolve(
                (asked.get("console") or [""])[0], (asked.get("name") or [""])[0])
            if not url:
                return {"error": "That image can no longer be found."}
            # The page suggests a name ending .png because that is what the
            # thumbnail server serves. An artwork service may well have handed
            # back a JPEG, and saving one under a .png name is how you end up
            # with a file nothing will open.
            real = os.path.splitext(urllib.parse.urlparse(url).path)[1].lower()
            if real in (".jpg", ".jpeg", ".webp"):
                suggested = os.path.splitext(suggested)[0] + real

        # A cover the user set themselves is already on disk; every other one
        # has to be fetched from the thumbnail server.
        if url.startswith("/covers/"):
            name = os.path.basename(urllib.parse.unquote(url[len("/covers/"):]))
            source = library.COVERS_DIR / name
            if not name or not source.is_file():
                return {"error": "That image is no longer on disk."}
            try:
                data = source.read_bytes()
            except OSError as exc:
                return {"error": f"Could not read the image: {exc}"}
        else:
            try:
                data = downloads.fetch_image(url)
            except ValueError as exc:
                return {"error": str(exc)}
            except Exception:  # noqa: BLE001 - offline, 404, timeout
                return {"error": "Could not download that image."}

        # A console with a folder set gets saved into it without asking - the
        # whole point of setting one is not being asked again. Everything else
        # goes through the picker, which is only reached once the image is
        # already in hand so a failed download can't waste the trip.
        folder = downloads.cover_folder_for(str(body.get("console") or ""))
        if folder:
            try:
                folder.mkdir(parents=True, exist_ok=True)
                target = str(folder / suggested)
            except OSError as exc:
                return {"error": f"Could not use that cover folder: {exc}"}
        else:
            target = downloads.browse_save(suggested)
            if not target:
                return {"cancelled": True}

        try:
            Path(target).write_bytes(data)
        except OSError as exc:
            return {"error": f"Could not save the image: {exc}"}
        return {"saved": target, "asked": not folder}

    def _ra_playtimes(self, items: list) -> dict:
        """How long RetroAchievements says each of these has been played.

        `items` is [{path, console, name}] - the games the emulators had
        nothing to say about. Each is turned into a game id here, asked about
        in one go, and handed back under the path it came in as.
        """
        asked = [one for one in (items if isinstance(items, list) else [])
                 if isinstance(one, dict) and one.get("path")]
        if not asked:
            return {"ok": True, "times": {}}

        by_game: dict[int, list[str]] = {}
        for one in asked:
            game = retro.game_id(str(one.get("console") or ""),
                                 str(one.get("name") or ""))
            if game:
                by_game.setdefault(game, []).append(str(one["path"]))
        if not by_game:
            return {"ok": True, "times": {}}

        found = profile.playtimes(list(by_game))
        if not found.get("ok"):
            return found

        times: dict[str, int] = {}
        for game, seconds in (found.get("times") or {}).items():
            for path in by_game.get(int(game), []):
                times[path] = int(seconds)
        return {"ok": True, "times": times,
                "remaining": int(found.get("remaining") or 0)}

    def _start_verify(self, items: list) -> dict:
        """Begin sweeping the shelf, unless a sweep is already under way.

        One at a time, and the lock is what makes that true rather than the
        flag: two presses of the button arriving together would otherwise each
        see "not running" and start a thread, and the two would hash the same
        library into the same list of rows.
        """
        wanted = [one for one in (items if isinstance(items, list) else [])
                  if isinstance(one, dict) and one.get("path")]
        if not wanted:
            return {"ok": False, "reason": "nothing"}

        with _verify_lock:
            if _verify_state["running"]:
                return {"ok": False, "reason": "running",
                        "done": _verify_state["done"],
                        "total": _verify_state["total"]}
            _verify_state.update({"running": True, "done": 0,
                                  "total": len(wanted), "rows": [],
                                  "counts": {}, "reason": "", "cancel": False,
                                  "started": time.time()})

        threading.Thread(target=_run_verify, args=(wanted,),
                         daemon=True).start()
        return {"ok": True, "total": len(wanted)}

    def _delete_games(self, body: dict) -> dict:
        """Delete games, and the covers this app fetched for them.

        A console set to get its covers automatically ends up with one image
        per game in a folder the app writes to and nothing else does. Deleting
        the game and leaving the picture behind means the folder fills with
        art for games that are gone - and the next game to take that name
        picks up the old one. So the covers follow the games out, but only for
        the consoles where the app is the thing that put them there.

        `games` carries the name and console for each path; the page has them
        already from the library it is displaying. Only the ones that really
        were deleted are followed up on.
        """
        result = library.delete_games(body.get("paths") or [])
        gone = set(result.get("removedPaths") or [])

        # The downloads panel keeps a finished row for each of these, pointing
        # at a file that no longer exists. Those go too - see forget_paths.
        result["forgotDownloads"] = downloads.manager.forget_paths(gone)

        if not body.get("covers"):
            return result

        wanted = [g for g in (body.get("games") or [])
                  if isinstance(g, dict) and g.get("path") in gone]
        result["coversRemoved"] = len(library.delete_cover_files(wanted))
        return result

    def _delete_cover_file(self, body: dict) -> dict:
        """Delete a cover image that this app saved to the console's folder.

        Deliberately narrow. The only thing it will unlink is a file with the
        given name inside the folder configured for that console - the same
        place "Save cover image" would have written it. No path from the page
        is ever used as a path, so nothing outside a folder the user chose for
        covers can be reached from here.
        """
        console = str(body.get("console") or "")
        folder = downloads.cover_folder_for(console)
        if folder is None:
            return {"error": "No cover folder is set for this console, so the "
                             "app doesn't know where its cover was saved."}

        name = os.path.basename(str(body.get("name") or ""))
        if not name or name in (".", ".."):
            return {"error": "That cover has no filename to look for."}

        target = folder / name
        if not target.is_file():
            return {"missing": True, "path": str(target)}
        try:
            target.unlink()
        except OSError as exc:
            return {"error": f"Could not delete the cover: {exc}"}
        return {"deleted": str(target)}

    def _same_origin(self) -> bool:
        """Whether this request came from the app's own page.

        `_is_local()` cannot answer this, and on its own it is not the
        protection it looks like. Any page on the open web can make the
        browser send a POST here - a plain HTML form needs no permission from
        anybody to do it, and `enctype="text/plain"` gets a JSON body past the
        checks that would otherwise force a preflight. The request then
        arrives from 127.0.0.1, with the user's own privileges, and every
        `_is_local()` gate below waves it through. Routes that delete games or
        rewrite the download folder are reachable that way.

        What a hostile page cannot do is forge `Origin`: the browser sets it
        and refuses to let script change it. So the rule is that an Origin, if
        present, has to be this server. Requests with none are let through -
        that is curl or a script, and a website cannot make anybody run one.
        """
        origin = self.headers.get("Origin")
        if not origin:
            return True
        try:
            sent = urllib.parse.urlparse(origin).netloc.lower()
        except ValueError:
            return False
        # Compared against Host rather than a fixed string, so reaching the
        # app as localhost, as 127.0.0.1, or on a chosen port all still work.
        return bool(sent) and sent == (self.headers.get("Host") or "").lower()

    def do_POST(self) -> None:  # noqa: N802
        route = urllib.parse.urlparse(self.path).path.rstrip("/")

        # Before anything else: every POST here changes something.
        if not self._same_origin():
            self._send_json(
                {"error": "That request came from another site, so it was ignored."},
                status=403)
            return

        if route in ("/api/account/login", "/api/account/logout"):
            if not self._is_local():
                self._send_json(
                    {"error": "Signing in is only allowed from this computer."},
                    status=403)
                return
            try:
                if route.endswith("logout"):
                    result = account.logout()
                    # Signing out revokes what the 🔒 downloads are using, so
                    # they stop here rather than running on and failing.
                    result["paused"] = downloads.manager.pause_login_required()
                    self._send_json(result)
                else:
                    body = self._read_json()
                    # The password is used here and never stored or logged.
                    self._send_json(account.login(body.get("email", ""),
                                                  body.get("password", "")))
            except account.AccountError as exc:
                self._send_json({"error": str(exc)}, status=400)
            return

        if route == "/api/prefs":
            self._send_json(state.set_prefs(self._read_json()))
            return

        if route == "/api/cart":
            self._send_json({"items": state.set_cart(
                self._read_json().get("items") or [])})
            return

        # The whole set is written at once, like the download list: the page
        # holds the lists, and a partial update would need the two copies to
        # agree about ordering before either of them had a reason to.
        if route == "/api/playlists":
            self._send_json({"playlists": state.set_playlists(
                self._read_json().get("playlists") or [])})
            return

        # Both write or read a file the user picks, so they are local-only
        # like the other pickers, and a restore overwrites this machine's
        # settings - not something a page on the network gets to trigger.
        if route in ("/api/backup", "/api/restore"):
            if not self._is_local():
                self._send_json({"error": "Only from this computer."}, status=403)
                return
            if route == "/api/backup":
                # Which parts to carry. Absent means all of it, which is what
                # every caller meant before there was anything to choose.
                asked = self._read_json().get("parts")
                parts = asked if isinstance(asked, list) else None
                chosen = downloads.browse_save_zip()
                self._send_json({"cancelled": True} if not chosen
                                else state.write_backup(chosen, parts))
            else:
                chosen = downloads.browse_open_zip()
                if not chosen:
                    self._send_json({"cancelled": True})
                    return
                result = state.read_backup(chosen)
                # Whether the page should offer to restart. Only the app with
                # a window of its own can: served into somebody's browser,
                # restarting would take the server out from under the tab
                # they are reading this in.
                result["canRestart"] = browse.can_open_window()
                self._send_json(result)
            return

        # Close this copy and start another. Used after restoring a backup,
        # where some of what was restored - the index above all - is only
        # read when the app starts.
        if route == "/api/restart":
            if not self._is_local():
                self._send_json({"error": "Only from this computer."}, status=403)
                return
            try:
                _relaunch()
            except OSError as exc:
                self._send_json({"error": f"Could not start it again: {exc}"},
                                status=500)
                return
            self._send_json({"restarting": True})
            # After the answer is on its way, not before: the page has to hear
            # that this worked, and this process is about to stop being able
            # to tell it anything.
            threading.Timer(0.7, lambda: os._exit(0)).start()  # noqa: SLF001
            return

        # Which of these games have a page on retroachievements.org. A batch,
        # because the page asks about everything it is showing at once and
        # then has the answers ready when a menu opens. The first console in
        # a session waits on one request to their servers; after that it is
        # answered from a file. See retro.py.
        if route == "/api/ra/lookup":
            body = self._read_json()
            # {ids, patches} - the ids in the order asked, and where to get a
            # patch for any of them that needs one. See retro.py.
            self._send_json(retro.lookup(body.get("items") or []))
            return

        # Which of the copies on one search result RetroAchievements' set is
        # actually dumped from. One game, asked for by pressing the button on
        # that game's card - see retro.supported.
        if route == "/api/times/scan":
            body = self._read_json()
            console = str(body.get("console") or "")
            with _times_lock:
                if _times_state["running"]:
                    self._send_json({"ok": False, "reason": "running",
                                     "done": _times_state["done"],
                                     "total": _times_state["total"]})
                    return
                pool = wanted.indexed_sets(self.conn, console)
                todo = ratimes.outstanding(pool)
                _times_state.update({"running": True, "done": 0,
                                     "total": len(todo), "cancel": False,
                                     "reason": "", "started": time.time()})
            threading.Thread(target=_run_times, args=(pool,),
                             daemon=True).start()
            self._send_json({"ok": True, "total": len(todo),
                             "pool": len(pool)})
            return

        if route == "/api/times/cancel":
            _times_state["cancel"] = True
            self._send_json({"cancelled": True})
            return

        if route == "/api/search/fastest":
            # The whole site in order of how long it takes, out of what was
            # timed by the scan above. Nothing is fetched here.
            #
            # "Whole site" means the whole of what is on screen: whatever was
            # typed in the search box and picked in the filter bar comes in
            # with the request and narrows the pool before it is ranked, so
            # this answers "the quickest of these" when there is a search and
            # "the quickest there are" when there is not. See _ranked_scope.
            body = self._read_json()
            try:
                limit = max(1, min(int(body.get("limit") or 40), 200))
                offset = max(0, int(body.get("offset") or 0))
            except (TypeError, ValueError):
                limit, offset = 40, 0
            which = str(body.get("which") or "beat")
            scope = self._ranked_scope(body)
            pool = wanted.indexed_sets(self.conn, scope["consoles"],
                                       scope["allow"])
            ranked = ratimes.rank(pool, which)
            page = ranked[offset:offset + limit]
            groups = db.groups_for(
                self.conn, list(dict.fromkeys(r["norm"] for r in page)),
                where=scope["where"], params=scope["params"])
            by_norm = {g["title_norm"]: g for g in groups}
            out = []
            for row in page:
                found = by_norm.get(row["norm"])
                if not found:
                    continue
                # A copy per row rather than the row itself: one game with a
                # set on two consoles is two entries here, and both were
                # writing their own time into the same shared dict - so the
                # second console's median ended up under the first one's card.
                group = dict(found)
                group["setSize"] = {"achievements": row["achievements"],
                                    "points": row["points"], "id": row["id"],
                                    "console": row["console"],
                                    "patch": row.get("patch") or "",
                                    # What RetroAchievements calls the set. For a hack that is
                                    # not the name of the file being fetched, and the card
                                    # has to show the set rather than the game under it.
                                    "title": row.get("title") or "",
                                    "romset": row.get("romset") or "",
                                    "base": row.get("base") or ""}
                group["span"] = {"which": which, "seconds": row["seconds"],
                                 "players": row["players"], "console": row["console"],
                                 "beat": row.get("beat"), "master": row.get("master")}
                out.append(group)
            self._send_json({"total": len(ranked), "groups": out,
                             "offset": offset, "limit": limit,
                             "more": offset + len(page) < len(ranked),
                             "pool": len(pool),
                             "facets": scope["facets"],
                             "consoles": len({r["console"] for r in ranked})})
            return

        if route == "/api/search/shortest":
            # Every game with a set, in order of how small the set is, and
            # narrowed to what the index can actually fetch. Not a sort of the
            # page - see wanted.shortest. Narrowed by the search box and the
            # filter bar exactly as the fastest list above is.
            body = self._read_json()
            try:
                limit = max(1, min(int(body.get("limit") or 40), 200))
                offset = max(0, int(body.get("offset") or 0))
            except (TypeError, ValueError):
                limit, offset = 40, 0
            scope = self._ranked_scope(body)
            found = wanted.shortest(
                self.conn, scope["consoles"], limit=limit, offset=offset,
                allow=scope["allow"], where=scope["where"],
                params=scope["params"])
            found["facets"] = scope["facets"]
            self._send_json(found)
            return

        if route == "/api/ra/sizes":
            # How many achievements each set has. One bulk request per console
            # and nothing per game, which is why this can order a page on the
            # spot where a time cannot.
            body = self._read_json()
            games = body.get("games")
            self._send_json(retro.sizes(games if isinstance(games, list) else []))
            return

        if route == "/api/ra/worth":
            # What each set scores, filled in behind the list that named them
            # - see wanted.worth for why it is not fetched with the list.
            self._send_json(wanted.worth(self._read_json().get("games") or []))
            return

        if route == "/api/ra/supported":
            body = self._read_json()
            self._send_json(retro.supported(body.get("files") or []))
            return

        # Fetch a patch and put it on a game already downloaded. Writing to
        # the library, so only from this computer. See patcher.py.
        # Downloaded here rather than handed to a browser: the app knows where
        # patches are meant to go, and a browser would drop it wherever it
        # drops everything else.
        if route == "/api/patch/download":
            if not self._is_local():
                self._send_json({"error": "Only from this computer."}, status=403)
                return
            body = self._read_json()
            try:
                self._send_json(patcher.save_patch(
                    str(body.get("url") or ""), downloads.patch_folder(),
                    str(body.get("name") or "")))
            except patcher.PatchError as exc:
                self._send_json({"error": str(exc)}, status=400)
            return

        # Fetch this console's core and say where it landed, so the box can
        # be filled in. Local-only: it writes into RetroArch's folder.
        if route == "/api/cores/install":
            if not self._is_local():
                self._send_json({"error": "Only from this computer."}, status=403)
                return
            body = self._read_json()
            try:
                self._send_json(cores.install(str(body.get("console") or "")))
            except cores.CoreError as exc:
                self._send_json({"error": str(exc)}, status=400)
            return

        # The patch tool's own file pickers.
        if route == "/api/patch/browse":
            if not self._is_local():
                self._send_json({"error": "Only from this computer."}, status=403)
                return
            body = self._read_json()
            chosen = downloads.browse_patchable(str(body.get("kind") or "game"),
                                                str(body.get("start") or ""))
            self._send_json({"file": chosen or ""})
            return

        if route == "/api/patch/apply":
            if not self._is_local():
                self._send_json({"error": "Only from this computer."}, status=403)
                return
            body = self._read_json()

            def moved(done: int, total: int) -> None:
                _patch_state["done"], _patch_state["total"] = done, total

            _patch_state.update({"running": True, "done": 0, "total": 0,
                                 "name": Path(str(body.get("path") or "")).name})
            try:
                self._send_json(patcher.patch_game(
                    str(body.get("path") or ""), str(body.get("url") or ""),
                    str(body.get("choose") or ""),
                    str(body.get("patchPath") or ""),
                    # A setting rather than something the page sends, so the
                    # answer is the same wherever patching was started from.
                    bool(downloads.load_settings().get("patch_replace")),
                    moved))
            except patcher.PatchError as exc:
                self._send_json({"error": str(exc)}, status=400)
            finally:
                _patch_state["running"] = False
            return

        # Copying the RetroAchievements login into the emulators that have
        # not got it. Writes into other programs' settings files, so local
        # only - and never asks for a password: see racred.
        if route == "/api/racred/apply":
            if not self._is_local():
                self._send_json({"error": "Only from this computer."},
                                status=403)
                return
            only = self._read_json().get("only")
            try:
                self._send_json(racred.apply(
                    only=[str(one) for one in only] if only else None))
            except racred.CredError as why:
                self._send_json({"error": str(why)}, status=400)
            except Exception as exc:  # noqa: BLE001 - reported, not raised
                self._send_json({"error": f"{type(exc).__name__}: {exc}"},
                                status=500)
            return

        # Putting one session's saves back. This writes into an emulator's
        # own folders, so local-only - and always through a plan the page has
        # already shown, because history.restore snapshots what is there
        # before it overwrites any of it.
        # A line about what one evening was, so fifteen days of "21:07, 3
        # files" can be found through again. Local-only for the same reason
        # as the two below: it names a path on this machine.
        if route == "/api/history/note":
            if not self._is_local():
                self._send_json({"error": "Only from this computer."},
                                status=403)
                return
            body = self._read_json()
            try:
                self._send_json(history.set_note(str(body.get("at") or ""),
                                                 str(body.get("text") or "")))
            except history.Refused as why:
                self._send_json({"error": str(why)}, status=400)
            except Exception as exc:  # noqa: BLE001 - reported, not raised
                self._send_json({"error": f"{type(exc).__name__}: {exc}"},
                                status=500)
            return

        # Showing one session's folder in the file manager. Local-only for
        # the obvious reason, and through history.folder so the path is
        # checked to be a snapshot rather than taken as given.
        if route == "/api/history/reveal":
            if not self._is_local():
                self._send_json({"error": "Only from this computer."},
                                status=403)
                return
            try:
                where = history.folder(str(self._read_json().get("at") or ""))
                self._send_json({"opened": downloads.reveal(where)})
            except history.Refused as why:
                self._send_json({"error": str(why)}, status=400)
            except Exception as exc:  # noqa: BLE001 - reported, not raised
                self._send_json({"error": f"{type(exc).__name__}: {exc}"},
                                status=500)
            return

        # What one session weighs, and throwing it away. Two routes rather
        # than one so the page can ask before it asks the reader: the figures
        # in the confirmation are read at the moment it is put up, not taken
        # from a panel that may have been open for a while.
        # Keeping one session past the fortnight.
        # Setting up, testing, and running a sync. All local-only: they name
        # folders on this machine, carry a server password, and move files
        # about in the emulators' own directories.
        if route.startswith("/api/sync"):
            if not self._is_local():
                self._send_json({"error": "Only from this computer."},
                                status=403)
                return
            body = self._read_json()
            try:
                if route == "/api/sync/settings":
                    keep = {}
                    for key in ("syncKind", "syncFolder", "syncDavUrl",
                                "syncDavUser", "syncDavPass",
                                "syncDeviceName"):
                        if key in body:
                            keep[key] = str(body.get(key) or "")
                    if "syncParts" in body:
                        asked = body.get("syncParts") or []
                        keep["syncParts"] = [p for p in asked
                                             if p in sync.CARRIES]
                    if "syncAuto" in body:
                        keep["syncAuto"] = bool(body.get("syncAuto"))
                    # A blank password means "keep the one already there".
                    # The page is never sent it, so it cannot echo it back,
                    # and an empty box must not silently erase it.
                    if keep.get("syncDavPass") == "":
                        keep.pop("syncDavPass", None)
                    state.set_prefs(keep)
                    self._send_json(syncstore.status())
                elif route == "/api/sync/check":
                    store = syncstore.store_for()
                    if store is None:
                        self._send_json({"error": "Nothing is set up yet."},
                                        status=400)
                        return
                    self._send_json(store.check())
                elif route == "/api/sync/run":
                    asked = body.get("parts")
                    parts = ([p for p in asked if p in sync.CARRIES]
                             if isinstance(asked, list) else None)
                    self._send_json(syncstore.run(
                        parts=parts, dry=bool(body.get("dry"))))
                else:
                    self.send_error(404, "Not found.")
                return
            except syncstore.StoreError as why:
                self._send_json({"error": str(why)}, status=400)
                return
            except Exception as exc:  # noqa: BLE001 - reported, not raised
                self._send_json({"error": f"{type(exc).__name__}: {exc}"},
                                status=500)
                return

        # Which of the shelves carrying this file is quickest right now.
        # Local-only: it opens a handful of connections on this machine's
        # line, which is not something a page on another one gets to do.
        if route == "/api/sources/speed":
            if not self._is_local():
                self._send_json({"error": "Only from this computer."},
                                status=403)
                return
            items = self._read_json().get("items")
            self._send_json(speedtest.measure(
                items if isinstance(items, list) else []))
            return

        # Where the games on a playlist can be downloaded from.
        #
        # A list built out of the library holds no URLs - it was made from
        # files that were already there - so this is what lets it be acted on
        # once they are not. See wanted.copies_for.
        if route == "/api/playlist/copies":
            body = self._read_json()
            items = body.get("items")
            self._send_json({"copies": wanted.copies_for(
                self.conn, items if isinstance(items, list) else [])})
            return

        if route == "/api/history/pin":
            if not self._is_local():
                self._send_json({"error": "Only from this computer."},
                                status=403)
                return
            body = self._read_json()
            try:
                self._send_json(history.set_pinned(
                    str(body.get("at") or ""), bool(body.get("pinned"))))
            except history.Refused as why:
                self._send_json({"error": str(why)}, status=400)
            except Exception as exc:  # noqa: BLE001 - reported, not raised
                self._send_json({"error": f"{type(exc).__name__}: {exc}"},
                                status=500)
            return

        if route in ("/api/history/weight", "/api/history/delete"):
            if not self._is_local():
                self._send_json({"error": "Only from this computer."},
                                status=403)
                return
            at = str(self._read_json().get("at") or "")
            try:
                self._send_json(history.weight(at) if route.endswith("weight")
                                else history.remove(at))
            except history.Refused as why:
                self._send_json({"error": str(why)}, status=400)
            except Exception as exc:  # noqa: BLE001 - reported, not raised
                self._send_json({"error": f"{type(exc).__name__}: {exc}"},
                                status=500)
            return

        if route in ("/api/history/plan", "/api/history/restore"):
            if not self._is_local():
                self._send_json({"error": "Only from this computer."},
                                status=403)
                return
            body = self._read_json()
            spot = str(body.get("at") or "")
            # Which consoles out of that session, for RetroArch - one evening
            # there holds every core played. Absent means all of it.
            only = body.get("only")
            only = [str(one) for one in only] if only else None
            try:
                self._send_json(
                    history.plan(spot, only=only) if route.endswith("plan")
                    else history.restore(spot, only=only))
            except history.Refused as why:
                self._send_json({"error": str(why)}, status=400)
            except Exception as exc:  # noqa: BLE001 - reported, not raised
                self._send_json({"error": f"{type(exc).__name__}: {exc}"},
                                status=500)
            return

        # A page opened in a window of the app's own. Answers whether it
        # worked, because when there is no native window - `serve` in a
        # browser - there is nothing to open and the page falls back to
        # handing it to the user's own browser instead. See browse.py.
        if route == "/api/browse/window":
            if not self._is_local():
                self._send_json({"error": "Only from this computer."}, status=403)
                return
            body = self._read_json()
            self._send_json({"opened": browse.open_window(
                str(body.get("url") or ""), str(body.get("title") or ""),
                # Set only by the launch path, so only those windows are
                # closed again when the game exits. See browse.close_beside.
                beside=bool(body.get("beside")))})
            return

        # A page handed to the user's own browser.
        if route == "/api/browse/open":
            if not self._is_local():
                self._send_json({"error": "Only from this computer."}, status=403)
                return
            self._send_json({"opened": browse.open_external(
                str(self._read_json().get("url") or ""))})
            return

        # Keys for the artwork services, the "does this work" button, and
        # forgetting what has already been looked up. All three carry or reveal
        # credentials, so all three are local-only.
        if route.startswith("/api/artwork"):
            if not self._is_local():
                self._send_json({"error": "Only from this computer."}, status=403)
                return
            body = self._read_json()
            if route == "/api/artwork/settings":
                artwork.set_settings(body)
                self._send_json(artwork.status())
            elif route == "/api/artwork/test":
                self._send_json(artwork.check(str(body.get("provider") or "")))
            elif route == "/api/artwork/forget":
                # Everything, not just the misses: this is the button for "the
                # cover it picked is wrong", and a wrong one is a hit.
                gone = artwork.forget()
                self._send_json({"forgotten": gone, **artwork.status()})
            else:
                self._send_json({"error": "Unknown request."}, status=404)
            return

        # What to start next, out of what has never been started. The page
        # sends the shelf it is already holding rather than the server reading
        # it again. See preview.suggest.
        # How long each game on the shelf takes, for the two time-based sorts.
        # Answers with everything already known and prices a bounded number of
        # the rest, so a big library fills in over a few goes.
        if route == "/api/times":
            body = self._read_json()
            games = body.get("games")
            self._send_json(preview.times(
                games if isinstance(games, list) else []))
            return

        # How far along the downloads are, said on the window itself: the
        # title, so the taskbar tooltip and alt-tab say it too, and the bar
        # behind the taskbar icon. This replaced notifications, which could
        # not be made to appear from a hosted WebView at all.
        # The saves, backed up on their own. Asked for by the page rather
        # than run on a timer in here: the app is only worth backing up while
        # somebody is using it, and "when they next open it" is both the right
        # moment and the one that needs no scheduler.
        if route == "/api/saves/backup":
            body = self._read_json()
            self._send_json(autosave.run(
                str(body.get("every") or state.prefs().get("saveBackup", "off")),
                force=bool(body.get("force"))))
            return

        # Room for what is about to be queued. Asked before anything starts,
        # because finding out at 94% of a forty-gigabyte batch is the worst
        # possible moment to find out.
        if route == "/api/downloads/space":
            body = self._read_json()
            self._send_json(downloads.space_for(body.get("items") or []))
            return

        if route == "/api/window":
            body = self._read_json()
            said = taskbar.title(str(body.get("title") or ""))
            drawn = taskbar.progress(int(body.get("done") or 0),
                                     int(body.get("total") or 0),
                                     str(body.get("state") or "normal"))
            self._send_json({"title": said, "progress": drawn})
            return

        if route == "/api/suggest":
            body = self._read_json()
            games = body.get("games")
            self._send_json({"games": preview.suggest(
                games if isinstance(games, list) else [],
                played=bool(body.get("all")))})
            return

        # Games like the ones already on the shelf. The page sends the shelf,
        # as it does for every other question of this shape. See recommend.py.
        if route == "/api/recommend":
            body = self._read_json()
            games = body.get("games")
            try:
                offset = max(0, int(body.get("offset") or 0))
            except (TypeError, ValueError):
                offset = 0
            try:
                seed = int(body.get("seed") or 0)
            except (TypeError, ValueError):
                seed = 0
            self._send_json(recommend.suggest(
                self.conn, games if isinstance(games, list) else [],
                offset=offset,
                only_ra=bool(body.get("onlyRa")),
                console=str(body.get("console") or ""),
                seed=seed))
            return

        if route in ("/api/cover/save", "/api/cover/delete"):
            if not self._is_local():
                self._send_json({"error": "Only from this computer."}, status=403)
                return
            body = self._read_json()
            self._send_json(self._save_cover(body) if route.endswith("save")
                            else self._delete_cover_file(body))
            return

        if route.startswith("/api/library"):
            body = self._read_json()
            if route in ("/api/library/delete", "/api/library/cover",
                         "/api/library/reveal", "/api/library/m3u",
                         "/api/library/tidy", "/api/library/play",
                         # These read files by path, which is reason enough
                         # not to take them from another machine.
                         "/api/library/verify", "/api/library/verify/all",
                         "/api/library/verify/cancel") and not self._is_local():
                self._send_json({"error": "Only from this computer."}, status=403)
                return
            if route == "/api/library/delete":
                self._send_json(self._delete_games(body))
            elif route == "/api/library/play":
                path = body.get("path", "")
                emulator = downloads.emulator_for(body.get("console", ""), path)
                if emulator is None:
                    self._send_json({"ok": False, "noEmulator": True})
                else:
                    console_ = body.get("console", "")
                    result = library.launch(
                        path, emulator,
                        downloads.emulator_args_for(console_, path),
                        downloads.emulator_core_for(console_, path))
                    # Only a game that actually started counts as played.
                    if result.get("ok"):
                        result["recent"] = state.push_recent({
                            "key": body.get("key", ""), "path": path,
                            "name": body.get("name", ""), "console": console_})
                    self._send_json(result)
            elif route == "/api/library/cover":
                chosen = downloads.browse_image()
                if not chosen:
                    self._send_json({"ok": False, "cancelled": True})
                else:
                    self._send_json(library.set_cover(body.get("path", ""), chosen))
            elif route == "/api/library/tidy":
                self._send_json(library.tidy())
            elif route == "/api/library/m3u":
                self._send_json(library.write_m3u(str(body.get("path") or "")))
            elif route == "/api/library/cover/clear":
                self._send_json(library.clear_cover(body.get("path", "")))
            elif route == "/api/library/emulator":
                # Read or set what one game uses, rather than its console.
                path = str(body.get("path") or "")
                # `in`, not truthiness: clearing sends an empty object, and
                # an empty dict is false - so asking "did they send one" the
                # obvious way skipped exactly the case that removes it.
                if "set" in body:
                    settings = downloads.load_settings()
                    overrides = dict(settings.get("game_overrides") or {})
                    chosen = body.get("set") or {}
                    keep = {f: str(chosen.get(f) or "")
                            for f in ("emulator", "core", "args")}
                    # Nothing set means no override at all, rather than an
                    # empty one that would quietly stop the console's from
                    # applying.
                    if any(keep.values()):
                        overrides[path] = keep
                    else:
                        overrides.pop(path, None)
                    downloads.save_settings({"game_overrides": overrides})
                self._send_json({"override": downloads.override_for(path)})
            elif route == "/api/library/replacement":
                # The other half of a failed check: which copy would have
                # worked, and can it be fetched from here.
                self._send_json(wanted.replacement(
                    self.conn, str(body.get("console") or ""),
                    str(body.get("name") or ""), int(body.get("game") or 0)))
            elif route == "/api/library/playtime":
                # The hours the emulator kept no log of. Keyed by path on the
                # way out, because that is what the shelf has to hand - the
                # ids are worked out here so the page does not have to have
                # resolved them first.
                self._send_json(self._ra_playtimes(body.get("items") or []))
            elif route == "/api/library/verify":
                # A game, or the handful on one card. Answered here and now,
                # because this is somebody pressing a menu entry and waiting.
                self._send_json(retro.verify(body.get("items") or []))
            elif route == "/api/library/verify/all":
                self._send_json(self._start_verify(body.get("items") or []))
            elif route == "/api/library/verify/cancel":
                _verify_state["cancel"] = True
                self._send_json({"cancelled": True})
            elif route == "/api/library/reveal":
                self._send_json({"opened": downloads.reveal(body.get("path", ""))})
            else:
                self.send_error(404, "Not found")
            return

        if route.startswith("/api/downloads"):
            body = self._read_json()
            if route == "/api/downloads":
                ids = downloads.manager.add(body.get("items") or [])
                self._send_json({"added": len(ids), "ids": ids})
            elif route == "/api/downloads/badcopy/seen":
                # The warning has been shown, so it should not come back on
                # the next poll two seconds later.
                downloads.manager.clear_bad_copy()
                self._send_json({"ok": True})
            elif route == "/api/downloads/cancel":
                ok = downloads.manager.cancel(int(body.get("id") or 0))
                self._send_json({"cancelled": ok})
            elif route == "/api/downloads/pause":
                self._send_json({"paused": downloads.manager.pause(int(body.get("id") or 0))})
            elif route == "/api/downloads/resume":
                self._send_json(downloads.manager.resume(int(body.get("id") or 0)))
            elif route == "/api/downloads/requeue":
                self._send_json({"requeued":
                                 downloads.manager.requeue(int(body.get("id") or 0))})
            elif route == "/api/downloads/startnext":
                self._send_json({"moved":
                                 downloads.manager.start_next(int(body.get("id") or 0))})
            elif route == "/api/downloads/forget":
                self._send_json(downloads.manager.forget(int(body.get("id") or 0)))
            elif route == "/api/downloads/clear":
                self._send_json({"removed": downloads.manager.clear_finished()})
            elif route == "/api/downloads/discard":
                self._send_json(downloads.manager.discard(int(body.get("id") or 0)))
            elif route == "/api/downloads/pauseall":
                self._send_json({"paused": downloads.manager.pause_all()})
            elif route == "/api/downloads/resumeall":
                self._send_json(downloads.manager.resume_all())
            elif route == "/api/downloads/discardall":
                self._send_json(downloads.manager.discard_all())
            elif route == "/api/downloads/settings":
                self._send_json(downloads.save_settings(body))
            elif route == "/api/downloads/browse":
                if not self._is_local():
                    self._send_json({"error": "Only from this computer."}, status=403)
                    return
                chosen = downloads.browse_folder(body.get("start", ""))
                self._send_json({"folder": chosen})
            elif route == "/api/downloads/relink":
                # Lists folders and rewrites where downloads go, so it belongs
                # with the other pickers rather than with the settings.
                if not self._is_local():
                    self._send_json({"error": "Only from this computer."}, status=403)
                    return
                consoles = [row["value"] for row in db.facets(self.conn)["consoles"]]
                self._send_json(downloads.relink_console_folders(consoles))
            elif route == "/api/downloads/browse-exe":
                if not self._is_local():
                    self._send_json({"error": "Only from this computer."}, status=403)
                    return
                self._send_json({"file": downloads.browse_exe(
                    body.get("start", ""), str(body.get("kind") or "program"))})
            elif route == "/api/downloads/reveal":
                if not self._is_local():
                    self._send_json({"error": "Only from this computer."}, status=403)
                    return
                job = downloads.manager.job(int(body.get("id") or 0))
                self._send_json({"opened": bool(job) and downloads.reveal(job.path)})
            else:
                self.send_error(404, "Not found")
            return

        if route != "/api/index":
            self.send_error(404, "Not found")
            return

        with _index_lock:
            if _index_state["running"]:
                self._send_json({"running": True, "started": False})
                return
            _index_state.update(running=True, log=[], summary=None,
                                done=0, total=0, started=time.time())
            # Its own connection, opened on that thread. Handing it this
            # request's would put two threads back on one connection - the
            # exact thing db.thread_conn exists to stop - and this one runs
            # for minutes.
            threading.Thread(target=_run_index, args=(self.db_path,),
                             daemon=True).start()
        self._send_json({"running": True, "started": True})


class Server(ThreadingHTTPServer):
    """The app's own HTTP server, with a listen queue the page cannot overrun.

    socketserver's default backlog is five. One screen of this app asks for
    far more than five things at once - a cover for every card, the
    achievement check for every file on it, play times, the search itself -
    and a connection arriving with five already waiting is refused by the
    kernel rather than queued. In the page that surfaces as `TypeError:
    Failed to fetch` on whichever request lost the race, and for the search
    box that meant the results silently stayed on the previous query while
    the box showed the new one. Measured before this: 39 of 120 requests
    refused. After: none.
    """

    request_queue_size = 128
    # A request still in flight must not hold the app open on the way out.
    daemon_threads = True


def serve(host: str = "127.0.0.1", port: int = 8770) -> None:
    conn = db.connect()
    Handler.db_path = db.DB_PATH
    downloads.manager.restore()   # bring back last session's queue
    counts = db.stats(conn)

    httpd = Server((host, port), Handler)
    print(f"RomSrx running at  http://{host}:{port}")
    print(f"Index: {counts['games']:,} games / {counts['files']:,} files "
          f"across {len(counts['sources'])} sources")
    if not counts["files"]:
        print("Index is empty - run `python -m romsrx index` "
              "(or hit Reindex in the UI).")
    print("Ctrl+C to stop.\n")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        httpd.server_close()
        conn.close()
