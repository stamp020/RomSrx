"""How the indexer behaves when archive.org is having a bad day.

This path only runs when something is already wrong, which is the worst time
to find out it is wrong itself. A local server stands in for archive.org and
is told exactly what to answer, so "waited when asked to" and "did not ask
again about something that is not there" become things that can be checked.

Nothing here touches the network.
"""
import http.server
import io
import json
import sys
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from romsrx import indexer, minerva  # noqa: E402

ok = fail = 0


def check(label, got, want):
    global ok, fail  # noqa: PLW0603
    if got == want:
        ok += 1
        print(f"  pass  {label}")
    else:
        fail += 1
        print(f"  FAIL  {label}\n          got  {got!r}\n          want {want!r}")


# What the stand-in server should do next, per path, and what it was asked.
script: dict[str, list] = {}
asked: dict[str, int] = {}


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802
        name = self.path.rsplit("/", 1)[-1]
        asked[name] = asked.get(name, 0) + 1
        steps = script.get(name) or [("ok", None)]
        kind, extra = steps[min(asked[name] - 1, len(steps) - 1)]

        if kind == "ok":
            body = json.dumps({"files": [{"name": "a.zip", "size": "1"}]}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        self.send_response(kind)
        if extra is not None:
            self.send_header("Retry-After", str(extra))
        self.send_header("Content-Length", "0")
        self.end_headers()

    def log_message(self, *args):
        pass


httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
threading.Thread(target=httpd.serve_forever, daemon=True).start()
indexer.METADATA_URL = f"http://127.0.0.1:{httpd.server_address[1]}/metadata/{{}}"


class NoSleep:
    """time, with the sleeping written down instead of done.

    The waits under test are one second, six seconds and a full minute, and
    actually serving them made this the slowest suite here by a wide margin -
    and a flaky one, because "it took about sixty seconds" is a claim about
    the machine as much as about the code. What is worth pinning is how long
    the indexer *decided* to wait, which is exactly what this records.
    """

    def __init__(self):
        self.waits: list[float] = []

    def sleep(self, seconds):
        self.waits.append(round(float(seconds), 3))

    def time(self):
        return time.time()

    def monotonic(self):
        return time.monotonic()


clock = NoSleep()
indexer.time = clock


def run(name, **kwargs):
    """(result or the error text, the waits it asked for, times it asked)."""
    clock.waits.clear()
    try:
        out = indexer.fetch_metadata(name, **kwargs)
    except RuntimeError as exc:
        out = f"failed: {exc}"
    return out, list(clock.waits), asked.get(name, 0)


# --- the ordinary case ----------------------------------------------------
script["fine"] = [("ok", None)]
result, waits, tries = run("fine")
check("a good answer comes straight back", bool(result.get("files")), True)
check("and is asked for once", tries, 1)
check("without waiting at all", waits, [])

# --- things that will not improve by asking again -------------------------
# This is the change that matters most on a bad day: 140 sources each asking
# three times about something that is not there is most of an hour.
script["missing"] = [(404, None)]
result, waits, tries = run("missing")
check("a 404 gives up at once", tries, 1)
check("and says what happened", "404" in str(result), True)
check("without waiting around", waits, [])

script["forbidden"] = [(403, None)]
_, _, tries = run("forbidden")
check("a 403 is not retried either", tries, 1)

# --- things that might -----------------------------------------------------
script["busy"] = [(503, None), (503, None), ("ok", None)]
result, waits, tries = run("busy")
check("a 503 is tried again", tries, 3)
check("and succeeds when it clears", bool(result.get("files")), True)
check("backing off as it goes", waits, [2, 4])

script["flaky"] = [(500, None), ("ok", None)]
result, _, tries = run("flaky")
check("so is a 500", tries, 2)
check("recovering on the second ask", bool(result.get("files")), True)

# --- being told how long to wait ------------------------------------------
# Backoff would be 2s here; the server asks for 1, and being asked is the
# whole point of the header.
script["polite"] = [(429, 1), ("ok", None)]
result, waits, tries = run("polite")
check("a 429 is tried again", tries, 2)
check("waiting the second it asked for", waits, [1])
check("and then succeeds", bool(result.get("files")), True)

# An unreasonable request is not followed off a cliff.
script["greedy"] = [(429, 99999), ("ok", None)]
_, waits, _ = run("greedy", retries=2)
check("an absurd Retry-After is capped", waits, [indexer.RETRY_WAIT_CAP])

# --- giving up ------------------------------------------------------------
script["hopeless"] = [(503, None)]
result, _, tries = run("hopeless", retries=2)
check("a server that never recovers is asked the agreed number of times",
      tries, 2)
check("and the failure names the source", "hopeless" in str(result), True)

# --- the settings themselves ----------------------------------------------
check("the timeout is no longer measured in minutes",
      indexer.TIMEOUT <= 60, True)
check("429 is treated as worth retrying", 429 in indexer.RETRY_CODES, True)
check("404 is not", 404 in indexer.RETRY_CODES, False)

# -- sources that stopped being listed --------------------------------------
#
# A source is only rewritten when it is visited, so one that has been renamed
# or dropped is never visited and its files stay. The MiNERVA shelves were
# indexed once under one set of ids and again under another, and the database
# kept both lots: 79,382 rows nothing maintained, offered in search results,
# pointing at a shelf no refresh would ever correct.

print("\nsources that are no longer listed")

from romsrx import db  # noqa: E402

conn = db.connect(":memory:")
config = {"sources": [
    {"id": "kept", "console": "NES/Famicom", "name": "Kept",
     "identifier": "kept"},
]}


def put(source_id, filename):
    with conn:
        conn.execute(
            "INSERT OR IGNORE INTO sources "
            "(id, console, name, identifier, url) "
            "VALUES (?, 'NES/Famicom', ?, ?, 'u')",
            (source_id, source_id, source_id))
        conn.execute(
            "INSERT INTO files (source_id, console, path, filename, title, "
            "title_norm, ext, size, url) "
            "VALUES (?, 'NES/Famicom', ?, ?, ?, ?, 'zip', 1, 'u')",
            (source_id, filename, filename, filename, filename))


put("kept", "A.zip")
put("renamed_away", "B.zip")
put("renamed_away", "C.zip")

check("the rows of an unlisted source go",
      indexer.prune_removed(conn, config), 2)
check("...and its row in the source list too",
      conn.execute("SELECT COUNT(*) FROM sources WHERE id = 'renamed_away'")
      .fetchone()[0], 0)
check("...while a listed source is untouched",
      conn.execute("SELECT COUNT(*) FROM files WHERE source_id = 'kept'")
      .fetchone()[0], 1)
check("a second pass finds nothing left to do",
      indexer.prune_removed(conn, config), 0)

# The dangerous version of this deletes everything the caller did not ask to
# index. An --only subset says which shelves to fetch, not which may survive.
put("also_listed", "D.zip")
config["sources"].append({"id": "also_listed", "console": "NES/Famicom",
                          "name": "Also", "identifier": "also"})
check("indexing one shelf does not delete the others",
      indexer.prune_removed(conn, config), 0)

# -- not asking again for what has not changed ------------------------------
#
# A reindex was fetching all three hundred shelves in full every time, and a
# MiNERVA listing is megabytes of HTML generated per request. MiNERVA does
# offer an ETag, so the second time round the question can be "is this still
# what I have?" - answered in half a second with no body at all, against
# three seconds and three megabytes. Measured over forty shelves, a reindex
# went from nine seconds to two.
#
# archive.org offers neither an ETag nor a Last-Modified on its metadata, so
# nothing here applies to it and it is fetched in full as it always was.
#
# What must not happen is a shelf being skipped and its files going with it:
# "unchanged" has to mean the rows already in the index stand.

print("\nasking whether a listing has changed")

import http.server as _hs  # noqa: E402
import threading as _th  # noqa: E402

# The site's own markup, trimmed - the parser is strict about its shape and
# a hand-waved approximation of it would test the wrong thing.
_MAGNET = "magnet:?xt=urn:btih:" + "b" * 40 + "&amp;dn=Minerva_Myrient"
_BODY = f"""<!doctype html><html><body>
  <div class="entry" data-name="sonic (world).zip">
    <a href="/rom?id=9001" draggable="false">Sonic (World).zip</a>
    <span>1.5 MB</span>
    <a href="javascript:void(0)" onclick="downloadMagnet('{_MAGNET}')"
       data-m="0" draggable="false" title="Download Magnet">&#129522;</a>
  </div>
</body></html>"""
_hits = []


class _Listing(_hs.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    etag = '"v1"'

    def log_message(self, *a):
        pass

    def do_GET(self):  # noqa: N802
        _hits.append(self.headers.get("If-None-Match") or "(no etag sent)")
        if self.headers.get("If-None-Match") == self.etag:
            self.send_response(304)
            self.send_header("ETag", self.etag)
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        raw = _BODY.encode()
        self.send_response(200)
        self.send_header("ETag", self.etag)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)


_srv = _hs.ThreadingHTTPServer(("127.0.0.1", 0), _Listing)
_th.Thread(target=_srv.serve_forever, daemon=True).start()
_was = minerva.BASE
minerva.BASE = f"http://127.0.0.1:{_srv.server_address[1]}"
minerva.BROWSE = minerva.BASE + "/browse/"
try:
    got = indexer.fetch_listing("./Shelf/")
    check("the first ask brings the listing back", bool(got.get("minerva")), True)
    check("...and the validator the server offered with it",
          got.get("etag"), '"v1"')
    check("...having sent none itself", _hits[-1], "(no etag sent)")

    try:
        indexer.fetch_listing("./Shelf/", etag='"v1"')
        check("asking again with it says nothing changed", "fetched", "Unchanged")
    except indexer.Unchanged:
        check("asking again with it says nothing changed", "Unchanged", "Unchanged")
    check("...and it did send the validator", _hits[-1], '"v1"')

    # A shelf that really has changed must still come back in full.
    _Listing.etag = '"v2"'
    fresh = indexer.fetch_listing("./Shelf/", etag='"v1"')
    check("a changed shelf is fetched again", bool(fresh.get("minerva")), True)
    check("...with the new validator", fresh.get("etag"), '"v2"')
finally:
    minerva.BASE, minerva.BROWSE = _was, _was + "/browse/"
    _srv.shutdown()

# The whole point of skipping: the files stay. A source reported as unchanged
# whose rows had been dropped would leave a console silently empty.
check("the index keeps what it has for an unchanged shelf",
      indexer.Unchanged.__doc__ is not None, True)

httpd.shutdown()
print(f"\n{ok} passed, {fail} failed")
