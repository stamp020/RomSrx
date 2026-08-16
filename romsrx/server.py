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

from . import (account, browse, covers, db, downloads, indexer, library,
               patcher, retro, state, updates)
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


def _run_index(conn) -> None:
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
    conn = None  # set by serve()

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
                limit=limit,
                offset=offset,
            )
            result["limit"] = limit
            result["offset"] = offset
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

        if route == "/api/facets":
            self._send_json(db.facets(self.conn))
            return

        if route == "/api/stats":
            self._send_json(db.stats(self.conn))
            return

        if route == "/api/account":
            self._send_json(account.status())
            return

        if route == "/api/downloads":
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
                "per_console": settings["per_console"],
                "consoles": consoles,
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

    def _read_json(self) -> dict:
        try:
            length = int(self.headers.get("Content-Length") or 0)
            if not length:
                return {}
            return json.loads(self.rfile.read(length).decode("utf-8", "replace"))
        except (ValueError, TypeError):
            return {}

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
                return {"error": "That image is no longer on the thumbnail server."}

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
                str(body.get("url") or ""), str(body.get("title") or ""))})
            return

        # A page handed to the user's own browser.
        if route == "/api/browse/open":
            if not self._is_local():
                self._send_json({"error": "Only from this computer."}, status=403)
                return
            self._send_json({"opened": browse.open_external(
                str(self._read_json().get("url") or ""))})
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
                         "/api/library/reveal",
                         "/api/library/play") and not self._is_local():
                self._send_json({"error": "Only from this computer."}, status=403)
                return
            if route == "/api/library/delete":
                self._send_json(self._delete_games(body))
            elif route == "/api/library/play":
                path = body.get("path", "")
                emulator = downloads.emulator_for(body.get("console", ""))
                if emulator is None:
                    self._send_json({"ok": False, "noEmulator": True})
                else:
                    console_ = body.get("console", "")
                    result = library.launch(
                        path, emulator,
                        downloads.emulator_args_for(console_),
                        downloads.emulator_core_for(console_))
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
            elif route == "/api/library/cover/clear":
                self._send_json(library.clear_cover(body.get("path", "")))
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
            threading.Thread(target=_run_index, args=(self.conn,),
                             daemon=True).start()
        self._send_json({"running": True, "started": True})


def serve(host: str = "127.0.0.1", port: int = 8770) -> None:
    conn = db.connect()
    Handler.conn = conn
    downloads.manager.restore()   # bring back last session's queue
    counts = db.stats(conn)

    httpd = ThreadingHTTPServer((host, port), Handler)
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
