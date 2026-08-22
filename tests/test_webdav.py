"""A real WebDAV server, and the app's client talking to it over a socket.

Small on purpose - PROPFIND, MKCOL, GET, PUT, and Basic auth - but it is an
actual HTTP server on an actual port, so the client's XML parsing, its URL
quoting and its directory-making are exercised rather than described.
"""
import base64
import os
import shutil
import sys
import tempfile
import threading
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# A profile of its own, before romsrx is imported: the round trip at the
# bottom runs a real sync, which reads and writes one.
_home = Path(tempfile.mkdtemp(prefix="dav-home-"))
os.environ["APPDATA"] = str(_home)

from romsrx import state, sync, syncstore  # noqa: E402

BOX = Path(tempfile.mkdtemp(prefix="dav-"))
USER, PASSWORD = "someone", "app-password"


class Dav(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, *a):
        pass

    def _spot(self):
        rel = urllib.parse.unquote(urllib.parse.urlparse(self.path).path)
        return BOX / rel.strip("/")

    def _auth(self) -> bool:
        want = "Basic " + base64.b64encode(
            f"{USER}:{PASSWORD}".encode()).decode()
        if self.headers.get("Authorization") == want:
            return True
        self.send_response(401)
        self.send_header("WWW-Authenticate", 'Basic realm="x"')
        self.send_header("Content-Length", "0")
        self.end_headers()
        return False

    def _body(self, code: int, body: bytes = b"", kind="text/plain"):
        self.send_response(code)
        self.send_header("Content-Type", kind)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if body:
            self.wfile.write(body)

    def do_GET(self):  # noqa: N802
        if not self._auth():
            return
        spot = self._spot()
        if not spot.is_file():
            self._body(404)
            return
        self._body(200, spot.read_bytes(), "application/octet-stream")

    def do_PUT(self):  # noqa: N802
        if not self._auth():
            return
        length = int(self.headers.get("Content-Length") or 0)
        data = self.rfile.read(length) if length else b""
        spot = self._spot()
        if not spot.parent.is_dir():
            self._body(409)          # what a real server says: no parent
            return
        spot.write_bytes(data)
        self._body(201)

    def do_MKCOL(self):  # noqa: N802
        if not self._auth():
            return
        spot = self._spot()
        if spot.is_dir():
            self._body(405)          # already there
            return
        if not spot.parent.is_dir():
            self._body(409)
            return
        spot.mkdir()
        self._body(201)

    def do_PROPFIND(self):  # noqa: N802
        if not self._auth():
            return
        spot = self._spot()
        if not spot.exists():
            self._body(404)
            return
        depth = self.headers.get("Depth", "infinity")
        items = [spot]
        if depth != "0":
            items += sorted(spot.rglob("*"))

        rows = []
        for item in items:
            rel = item.relative_to(BOX).as_posix()
            href = "/" + "/".join(urllib.parse.quote(p, safe="")
                                  for p in rel.split("/") if p)
            if item.is_dir():
                href += "/"
                kind = "<D:resourcetype><D:collection/></D:resourcetype>"
                extra = ""
            else:
                kind = "<D:resourcetype/>"
                extra = (f"<D:getcontentlength>{item.stat().st_size}"
                         f"</D:getcontentlength>"
                         f'<D:getetag>"{item.stat().st_mtime_ns}"</D:getetag>')
            rows.append(f"<D:response><D:href>{href}</D:href><D:propstat>"
                        f"<D:prop>{kind}{extra}</D:prop>"
                        f"<D:status>HTTP/1.1 200 OK</D:status>"
                        f"</D:propstat></D:response>")
        body = ('<?xml version="1.0"?><D:multistatus xmlns:D="DAV:">'
                + "".join(rows) + "</D:multistatus>").encode()
        self._body(207, body, 'application/xml; charset="utf-8"')


srv = ThreadingHTTPServer(("127.0.0.1", 0), Dav)
port = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
base = f"http://127.0.0.1:{port}"
print(f"a WebDAV server on {base}, serving {BOX}\n")

ok = fail = 0


def check(label, got, want):
    global ok, fail
    if got == want:
        ok += 1
        print(f"  pass  {label}")
    else:
        fail += 1
        print(f"  FAIL  {label}\n          got  {got!r}\n          want {want!r}")


print("signing in")
try:
    syncstore.WebDavStore(base, USER, "wrong").check()
    check("a bad password is refused", "allowed", "refused")
except syncstore.StoreError as exc:
    check("a bad password is refused", "refused", "refused")
    check("...and says so plainly", "password" in str(exc), True)

store = syncstore.WebDavStore(base, USER, PASSWORD)
check("the right one works", store.check()["ok"], True)
check("...and it made its own folder", (BOX / sync.ROOT).is_dir(), True)

print("\nputting files where no folder exists yet")
# WebDAV will not make parents for you: a real server answers 409 and the
# client has to walk the path. This is the case that breaks naive clients.
store.put("saves/PCSX2 memcards/Mcd001.ps2", b"sixty hours")
store.put("app/prefs.json", b'{"theme":"dark"}')
check("a deep path is created on the way",
      (BOX / sync.ROOT / "saves" / "PCSX2 memcards" / "Mcd001.ps2").is_file(),
      True)

print("\nnames with spaces and brackets in them")
odd = "saves/RetroArch saves/Disney's Chicken Little (USA) [!].srm"
store.put(odd, b"awkward")
check("they survive the round trip", store.get(odd), b"awkward")

print("\nlisting what is there")
found = store.listing()
check("every file is listed", sorted(found),
      sorted(["app/prefs.json", odd, "saves/PCSX2 memcards/Mcd001.ps2"]))
check("...with their sizes", found["app/prefs.json"]["size"], 16)
check("...and something that changes when the content does",
      bool(found["app/prefs.json"]["hash"]), True)
check("directories are not mistaken for files",
      any(k.endswith("/") for k in found), False)

print("\nthe manifest")
check("there is none to begin with",
      syncstore.WebDavStore(base, USER, PASSWORD).get_manifest() is None
      or sync.read_manifest(store.get_manifest()) == {}, True)
store.put_manifest(sync.write_manifest({"app/prefs.json": {
    "hash": "abc", "size": 16, "when": 1.0}}))
check("...and it comes back",
      sync.read_manifest(store.get_manifest())["app/prefs.json"]["hash"], "abc")
check("...without appearing as a synced file",
      sync.MANIFEST in store.listing(), False)

print("\nand a file that is not there")
try:
    store.get("app/never-written.json")
    check("asking for it is an error, not empty bytes", "returned", "raised")
except syncstore.StoreError:
    check("asking for it is an error, not empty bytes", "raised", "raised")

print("\nsyncing to it twice over")
# The point of the second run. A WebDAV server will not hash a file for you,
# so its listing answers with an etag, and an etag never equals the blake2b
# taken here - which made every file look changed on the far side, every
# time. A sync that never settles re-fetches the whole selection on every run,
# which is merely wasteful by hand and unusable once it happens on its own.
state.set_prefs({"syncKind": "webdav", "syncDavUrl": base,
                 "syncDavUser": USER, "syncDavPass": PASSWORD,
                 "syncDeviceName": "Desktop"})
state.set_playlists([{"id": "a", "name": "Weekend games", "created": 1,
                      "items": []}])
first = syncstore.run(parts=["playlists"])
check("the first run sends it", first["sent"], 1)

second = syncstore.run(parts=["playlists"])
check("the second has nothing to do", second["sent"], 0)
check("...and fetches nothing back", second["fetched"], 0)
check("...and calls nothing a conflict", second["kept"], 0)

third = syncstore.run(parts=["playlists"])
check("and it stays settled", (third["sent"], third["fetched"]), (0, 0))

print("\nand a change here still travels after that")
state.set_playlists([{"id": "a", "name": "Weekend games", "created": 1,
                      "items": []},
                     {"id": "b", "name": "To finish", "created": 2,
                      "items": []}])
after = syncstore.run(parts=["playlists"])
check("it is sent", after["sent"], 1)
check("...and nothing is written over here", after["fetched"], 0)

print("\nand something the other computer sent")
# Written straight into the store, the way the other machine would leave it.
store.put("app/playlists.json",
          b'[{"id": "c", "name": "Made on the laptop", "created": 3, '
          b'"items": []}]')
came = syncstore.run(parts=["playlists"])
check("it is fetched", came["fetched"], 1)
check("...and it is what is here now",
      [p["name"] for p in state.playlists()], ["Made on the laptop"])

# The one that is easy to get wrong. What the store said about that file was
# an etag; writing the etag down as this machine's own hash makes the file
# look changed here on the next run, and it goes straight back up - an upload
# of everything just fetched, on every run, for ever.
after = syncstore.run(parts=["playlists"])
check("and it is not pushed straight back up", after["sent"], 0)
check("...nor fetched again", after["fetched"], 0)

srv.shutdown()
shutil.rmtree(BOX, ignore_errors=True)
shutil.rmtree(_home, ignore_errors=True)
print(f"\n{ok} passed, {fail} failed")
sys.exit(1 if fail else 0)
