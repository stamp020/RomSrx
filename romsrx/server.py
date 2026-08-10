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

from . import account, db, downloads, indexer, library, state, updates
from .paths import resource

WEB_ROOT = resource("web")

# Shared state for a reindex kicked off from the web UI.
_index_lock = threading.Lock()
_index_state: dict = {"running": False, "log": [], "summary": None,
                      "done": 0, "total": 0, "started": 0.0}

# Reindexing is almost entirely waiting on archive.org, so the useful number
# here is how many requests are in flight, not how many cores there are. Eight
# roughly halves the wall time against four without drawing rate limiting.
INDEX_WORKERS = 8


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

        if route == "/api/library":
            consoles = [row["value"] for row in db.facets(self.conn)["consoles"]]
            self._send_json(library.scan(consoles))
            return

        if route == "/api/downloads/folders":
            settings = downloads.load_settings()
            overrides = settings.get("console_folders") or {}
            consoles = [{
                "console": row["value"],
                "files": row["count"],
                "override": overrides.get(row["value"], ""),
                "effective": str(downloads.folder_for(row["value"])),
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

        # Asked for after the image is in hand, so a failure doesn't waste
        # the trip through the file picker.
        target = downloads.browse_save(suggested)
        if not target:
            return {"cancelled": True}
        try:
            Path(target).write_bytes(data)
        except OSError as exc:
            return {"error": f"Could not save the image: {exc}"}
        return {"saved": target}

    def do_POST(self) -> None:  # noqa: N802
        route = urllib.parse.urlparse(self.path).path.rstrip("/")

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

        if route == "/api/cover/save":
            if not self._is_local():
                self._send_json({"error": "Only from this computer."}, status=403)
                return
            self._send_json(self._save_cover(self._read_json()))
            return

        if route.startswith("/api/library"):
            body = self._read_json()
            if route in ("/api/library/delete", "/api/library/cover",
                         "/api/library/reveal") and not self._is_local():
                self._send_json({"error": "Only from this computer."}, status=403)
                return
            if route == "/api/library/delete":
                self._send_json(library.delete_games(body.get("paths") or []))
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
