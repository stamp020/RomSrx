"""One queue in front of RetroAchievements, shared by the whole app.

profile.py wrote the lesson down first: a burst of requests gets some of them
refused, and the refusals arrive as blank rows rather than as errors. Its fix
paced one module. Three more have since grown that ask the same site the same
kinds of question, and each was polite on its own - which is not pacing, it is
several bursts that happen to be well-mannered individually.

What is pinned here: that calls really are spaced apart, that a refusal is
retried and a real answer is not, and above all that a 404 comes straight back
to the caller. A game with no achievement set answers 404, and turning that
into a retry - or into a different exception - would make "no set for this
game" indistinguishable from "the site is busy".

Nothing touches the network; urlopen is stood in for.
"""
import io
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from romsrx import rapi  # noqa: E402

ok = fail = 0


def check(label, got, want):
    global ok, fail  # noqa: PLW0603
    if got == want:
        ok += 1
        print(f"  pass  {label}")
    else:
        fail += 1
        print(f"  FAIL  {label}\n          got  {got!r}\n          want {want!r}")


class Answer:
    """Stands in for the response urlopen hands back."""

    def __init__(self, body):
        self.body = body

    def read(self):
        return self.body

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False


def refusal(code, retry_after=None):
    headers = {"Retry-After": str(retry_after)} if retry_after else {}
    return urllib.error.HTTPError("https://x", code, "no", headers, None)


calls = []


def stub(answers):
    """urlopen replaced by a list of things to do, one per call."""
    calls.clear()
    queue = list(answers)

    def fake(request, timeout=None):
        calls.append(time.time())
        item = queue.pop(0)
        if isinstance(item, Exception):
            raise item
        return Answer(item)

    urllib.request.urlopen = fake


real_urlopen = urllib.request.urlopen
rapi.RETRY_AFTER = 0.05          # the waits are what is being tested, not endured
rapi.PACE = 0.05

req = urllib.request.Request("https://example.invalid/x")

print("the ordinary case")
stub([b"hello"])
check("a good answer comes straight back", rapi.get("https://example.invalid/x"),
      b"hello")
check("...on one call", len(calls), 1)

print("\nbeing told to slow down")
stub([refusal(429), b"second time"])
check("a 429 is tried again", rapi.read(req), b"second time")
check("...exactly once more", len(calls), 2)

stub([refusal(503), b"after the wobble"])
check("so is a 503, which is their edge under load", rapi.read(req),
      b"after the wobble")

stub([refusal(429), refusal(429)])
try:
    rapi.read(req)
    check("a second refusal gives up", "no error", "an error")
except urllib.error.HTTPError as exc:
    check("a second refusal gives up", exc.code, 429)
check("...without a third attempt", len(calls), 2)

print("\nanswers that are about the question, not the pace")
for code in (404, 401, 403, 500):
    stub([refusal(code), b"never reached"])
    try:
        rapi.read(req)
        got = "no error"
    except urllib.error.HTTPError as exc:
        got = exc.code
    check(f"{code} comes back to the caller", got, code)
    check(f"...on the first attempt, not the second", len(calls), 1)

print("\nwaiting")
stub([b"a", b"b", b"c"])
rapi.PACE = 0.25
start = time.time()
for _ in range(3):
    rapi.read(req)
spent = time.time() - start
# Three calls, two gaps. Generous lower bound so a slow machine cannot fail it.
check("calls are spaced apart", spent >= 0.4, True)
rapi.PACE = 0.05

print("\nhow long they asked for")
check("their Retry-After is honoured",
      rapi._pause_for(refusal(429, retry_after=3)), 3)  # noqa: SLF001
check("...but a wild one is capped",
      rapi._pause_for(refusal(429, retry_after=99999)), rapi.RETRY_MAX)  # noqa: SLF001
check("...and a missing one falls back to ours",
      rapi._pause_for(refusal(429)), rapi.RETRY_AFTER)  # noqa: SLF001

urllib.request.urlopen = real_urlopen
print(f"\n{ok} passed, {fail} failed")
sys.exit(1 if fail else 0)
