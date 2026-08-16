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

from romsrx import indexer  # noqa: E402

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


def run(name, **kwargs):
    """(result or the error text, seconds spent, times the server was asked)."""
    started = time.time()
    try:
        out = indexer.fetch_metadata(name, **kwargs)
    except RuntimeError as exc:
        out = f"failed: {exc}"
    return out, time.time() - started, asked.get(name, 0)


# --- the ordinary case ----------------------------------------------------
script["fine"] = [("ok", None)]
result, spent, tries = run("fine")
check("a good answer comes straight back", bool(result.get("files")), True)
check("and is asked for once", tries, 1)

# --- things that will not improve by asking again -------------------------
# This is the change that matters most on a bad day: 140 sources each asking
# three times about something that is not there is most of an hour.
script["missing"] = [(404, None)]
result, spent, tries = run("missing")
check("a 404 gives up at once", tries, 1)
check("and says what happened", "404" in str(result), True)
check("without waiting around", spent < 1.0, True)

script["forbidden"] = [(403, None)]
_, _, tries = run("forbidden")
check("a 403 is not retried either", tries, 1)

# --- things that might -----------------------------------------------------
script["busy"] = [(503, None), (503, None), ("ok", None)]
result, spent, tries = run("busy")
check("a 503 is tried again", tries, 3)
check("and succeeds when it clears", bool(result.get("files")), True)

script["flaky"] = [(500, None), ("ok", None)]
result, _, tries = run("flaky")
check("so is a 500", tries, 2)
check("recovering on the second ask", bool(result.get("files")), True)

# --- being told how long to wait ------------------------------------------
# Backoff would be 2s here; the server asks for 1, and being asked is the
# whole point of the header.
script["polite"] = [(429, 1), ("ok", None)]
result, spent, tries = run("polite")
check("a 429 is tried again", tries, 2)
check("waiting the second it asked for", 0.9 < spent < 1.9, True)
check("and then succeeds", bool(result.get("files")), True)

# An unreasonable request is not followed off a cliff.
script["greedy"] = [(429, 99999), ("ok", None)]
_, spent, _ = run("greedy", retries=2)
check("an absurd Retry-After is capped",
      spent < indexer.RETRY_WAIT_CAP + 5, True)

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

httpd.shutdown()
print(f"\n{ok} passed, {fail} failed")
