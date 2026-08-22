"""Closing the app in the middle of a download, and opening it the next day.

Reported by somebody who started a download one evening and could not get it
going again the next: the row sat there doing nothing, then died after half a
minute with "HTTPError: 416". The file had in fact finished downloading. The
app was closed in the gap between the last byte landing in the .part and the
rename that turns it into the game - so on resume it asked the server for the
byte after the last one, which is past the end of the file, which is what 416
means. That was treated as a network hiccup and retried five times, each with
a longer wait, and then reported as a failure. The download had been complete
the whole time.

So the shapes below are all the states a .part and a final file can be found
in the morning, and what each of them should do. The one rule underneath them
is that nothing may be called finished unless it is the right length: the
alternative is handing somebody a truncated game with a row saying it worked,
and that is worse than any amount of re-downloading.

A local server stands in for archive.org, and honours Range the way one does -
including the 416, which is the whole reason this suite exists.
"""
import http.server
import io
import os
import sys
import tempfile
import hashlib
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# Its own instance, so a real queue is never touched.
_box = Path(tempfile.mkdtemp(prefix="romsrx-resume-"))
os.environ["APPDATA"] = str(_box)

from romsrx import downloads, state  # noqa: E402

ok = fail = 0


def digest(what):
    """A short name for a file's contents, so a mismatch prints one line."""
    raw = what.read_bytes() if hasattr(what, "read_bytes") else what
    return f"{len(raw):,} bytes, md5 {hashlib.md5(raw).hexdigest()[:12]}"


def check(label, got, want):
    global ok, fail  # noqa: PLW0603
    if got == want:
        ok += 1
        print(f"  pass  {label}")
    else:
        fail += 1
        print(f"  FAIL  {label}\n          got  {got!r}\n          want {want!r}")


SIZE = 60_000
BODY = bytes((i * 11 + 7) % 251 for i in range(SIZE))
asked: list[str] = []


class Server(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, *args):
        pass

    def do_GET(self):  # noqa: N802
        rng = self.headers.get("Range")
        asked.append(rng or "(whole)")
        start = int(rng.split("=", 1)[1].split("-", 1)[0]) if rng else 0
        if start >= SIZE:
            # What a server really answers, Content-Range and all.
            self.send_response(416)
            self.send_header("Content-Range", f"bytes */{SIZE}")
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        body = BODY[start:]
        self.send_response(206 if start else 200)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Accept-Ranges", "bytes")
        if start:
            self.send_header("Content-Range", f"bytes {start}-{SIZE-1}/{SIZE}")
        self.end_headers()
        self.wfile.write(body)


httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Server)
PORT = httpd.server_address[1]
threading.Thread(target=httpd.serve_forever, daemon=True).start()

_games = _box / "games"
_games.mkdir(parents=True, exist_ok=True)
downloads.save_settings({"folder": str(_games), "extract": False})


_next_id = [1]


def overnight(name, *, part=None, final=None, total=SIZE):
    """Leave a download in a given state, close the app, open it, resume.

    Yesterday's queue is written straight to disk rather than by running a
    manager and stopping it. A manager starts working the moment a job is
    added, so setting the scene through one is a race against it - the .part
    this is trying to place gets written over by the very download it is
    meant to be resuming, and the test measures the race instead.

    Returns (job, the finished path, how many requests it took).
    """
    asked.clear()
    job_id = _next_id[0]
    _next_id[0] += 1

    folder = downloads.folder_for("NES/Famicom")
    folder.mkdir(parents=True, exist_ok=True)
    part_path, final_path = folder / (name + ".part"), folder / name
    part_path.unlink(missing_ok=True)
    final_path.unlink(missing_ok=True)
    if part is not None:
        part_path.write_bytes(part)
    if final is not None:
        final_path.write_bytes(final)

    state.save("queue", [{
        "id": job_id, "url": f"http://127.0.0.1:{PORT}/{name}",
        "filename": name, "console": "NES/Famicom", "source": "test",
        "login": False, "paused_from": "running", "total": total,
        "done": len(part or b""), "status": "paused",
        "path": str(final_path), "extracted": "", "error": "",
        "added": time.time(), "order": float(job_id),
    }])

    today = downloads.Manager()
    today.restore()
    today.resume(job_id)
    for _ in range(400):
        time.sleep(0.05)
        if today._jobs[job_id].status in ("done", "error"):  # noqa: SLF001
            break
    return today._jobs[job_id], final_path, len(asked)  # noqa: SLF001


# -- the report ------------------------------------------------------------

print("\nthe download that finished but was never renamed")
job, final, calls = overnight("whole.zip", part=BODY)
check("it is finished, not retried to death", job.status, "done")
check("...with the right bytes", digest(final), digest(BODY))
# One request, not none, and the change is deliberate.
#
# This used to assert nothing was asked at all: the part matched the size the
# queue was told, so the file was declared finished without a word to the
# server. That size comes from a listing, and MiNERVA's listings are
# approximate - they drift a few bytes either way - so on a file whose real
# length was a little more than its listing said, "the part matches" meant
# "rename a truncated game and call it done". The other direction was worse: a
# part a few bytes over the listing was read as belonging to some other file
# and deleted, throwing away hours of transfer, every time it was resumed.
#
# So the listing no longer decides. The range request goes out and the answer
# settles it - 416 here, because there really is nothing left - which costs
# one exchange of headers in the one case where the file was already whole.
check("...having asked the server rather than the listing", calls, 1)
check("...and no error is left on the row", job.error, "")


# -- when the size the queue was told is not the size of the file ----------
#
# MiNERVA's listing sizes are approximate - the app says so in as many words
# where it decides whether a finished file is complete - and a download that
# was interrupted has to survive that. Both directions were broken, and both
# only after the app had been closed part-way through, which is exactly how it
# was reported: "he closed the app and it broke".

print("\na listing that undercounts, with the whole file already down")
# Real file SIZE, listing said four bytes fewer, and every byte is on disk.
# This used to read as "longer than it should be, so it is not this file",
# delete the lot, and start again from zero - on every resume, forever.
job, final, calls = overnight("under.zip", part=BODY, total=SIZE - 4)
check("it finishes", job.status, "done")
check("...with every byte of it", digest(final), digest(BODY))
# The assertion that matters. Re-downloading also ends up with the right
# bytes, which is why this has to check that the work was *kept* - one range
# request from the end of the part, and no "(whole)" fetch of the lot.
check("...by asking from where it stopped", asked, [f"bytes={SIZE}-"])

print("\nand a listing that undercounts, with the file nearly down")
# The nastier one. The part matches the listing exactly, so the old code
# renamed it and called the download finished - four bytes short. A truncated
# game, reported as complete, which nothing downstream would question.
job, final, calls = overnight("short.zip", part=BODY[:SIZE - 4], total=SIZE - 4)
check("it is not declared finished at the listing's word", job.status, "done")
check("...the rest is fetched", digest(final), digest(BODY))
check("...asking for exactly the missing bytes", asked[-1], f"bytes={SIZE - 4}-")

print("\nand one that overcounts")
job, final, calls = overnight("over.zip", part=BODY, total=SIZE + 4)
check("a complete file is still finished", job.status, "done")
check("...intact", digest(final), digest(BODY))


# -- the ordinary case, which must keep working ----------------------------

print("\nand the ordinary interruptions")
job, final, calls = overnight("half.zip", part=BODY[:20_000])
check("half a file carries on from the half", job.status, "done")
check("...ending up correct", digest(final), digest(BODY))
check("...asking only for the rest", asked[0], "bytes=20000-")

job, final, _ = overnight("fresh.zip")
check("nothing downloaded yet starts at the beginning", job.status, "done")
check("...ending up correct", digest(final), digest(BODY))


# -- and the states that must never be called finished ---------------------
#
# Every one of these ends with a file of the right length. A download that
# has to start again is a nuisance; a truncated game reported as working is
# a bug somebody finds out about hours later, in an emulator.

print("\nwhat must never be mistaken for a finished download")
job, final, _ = overnight("long.zip", part=BODY + b"junk" * 20)
check("a .part longer than the file is thrown away", job.status, "done")
check("...and the file is right afterwards", digest(final), digest(BODY))

job, final, calls = overnight("stub.zip", final=BODY[:5_000])
check("a truncated file under the final name is replaced",
      job.status, "done")
check("...by the whole thing", digest(final), digest(BODY))
check("...which took fetching", calls > 0, True)

job, final, calls = overnight("there.zip", final=BODY)
check("a file that really is complete is left alone", job.status, "done")
check("...and nothing is fetched", calls, 0)
check("...and it says why", job.error, "already downloaded")


# -- what a job carries into the next day ----------------------------------

print("\nwhat the queue remembers overnight")
man = downloads.Manager()
[jid] = man.add([{"url": "https://example.org/x.zip", "filename": "x.zip",
                  "console": "Genesis/Mega Drive", "source": "s", "size": 900,
                  "patch": "https://example.org/patch.zip"}])
before = man._jobs[jid]  # noqa: SLF001
before.done, before.total, before.order = 400, 900, 3.0
man._persist()  # noqa: SLF001
after = downloads.Manager()
after.restore()
back = after._jobs[jid]  # noqa: SLF001

for field in ("url", "filename", "console", "source", "total", "done",
              "order", "login"):
    check(f"{field} survives", getattr(back, field), getattr(before, field))
# The one that was missing. A hack download resumed the next day used to come
# back as an ordinary one and finish as the plain game it was built from,
# with nothing anywhere saying the patch had been dropped.
check("and so does the patch that makes it a hack",
      back.patch_url, "https://example.org/patch.zip")

check("a download in flight comes back paused", back.status, "paused")
check("...remembering that it was running", back.paused_from, "running")

# -- a torrent left half-finished -------------------------------------------
#
# A collection torrent writes into a folder named after itself and only the
# finished file is moved out of it, so a download stopped before that leaves
# its bytes somewhere nothing else looks: not under the game's name, not with
# a .part on the end. Throwing the download away used to remove neither, and
# for a disc image that is gigabytes nobody can find.

print("\nwhat a half-finished torrent leaves behind")

torrent_dir = _games / "Genesis-Mega Drive" / "Minerva_Myrient"
torrent_dir.mkdir(parents=True, exist_ok=True)
stray = torrent_dir / "Sonic.zip"
stray.write_bytes(b"half a game" * 500)
finished = _games / "Genesis-Mega Drive" / "Sonic.zip"

gone = downloads._drop_torrent_partial(str(stray), str(finished))  # noqa: SLF001
check("the part in the torrent's folder is removed", gone, ["Sonic.zip"])
check("...and it really is gone", stray.exists(), False)
check("...along with the empty folder it was in", torrent_dir.exists(), False)

# The two paths are the same once a finished torrent has been moved into
# place. Tidying a download row must never take the game with it.
keep = _games / "Genesis-Mega Drive" / "Kept.zip"
keep.parent.mkdir(parents=True, exist_ok=True)
keep.write_bytes(b"a finished game")
check("the finished file is never the one deleted",
      downloads._drop_torrent_partial(str(keep), str(keep)), [])  # noqa: SLF001
check("...and it is still there", keep.exists(), True)
check("nothing recorded, nothing removed",
      downloads._drop_torrent_partial("", str(finished)), [])  # noqa: SLF001


# -- the size the index promised is not the size on disk --------------------
#
# MiNERVA's listing sizes are approximate: measured against the site's own
# figures for the same files they drift a few bytes either way. An exact
# comparison would decide every finished MiNERVA download was incomplete and
# fetch the whole thing again, which for a disc is hours.

print("\ndeciding whether a file on disk is the whole thing")


def whole(size, total):
    job = downloads.Job(id=1, url="u", filename="f")
    job.total = total
    spot = _games / "sizecheck.bin"
    spot.write_bytes(b"\0" * size)
    out = downloads.Manager()._already_here(job, spot)  # noqa: SLF001
    spot.unlink()
    return out


check("four bytes short of the listing is the whole file",
      whole(749_666, 749_670), True)
check("...and three bytes over is too", whole(385_546, 385_543), True)
check("a third of a file is not", whole(100_000, 300_000), False)
check("nor is half a disc", whole(1_200_000, 2_400_000), False)
check("with no size to compare, a file is a file", whole(1_000, 0), True)

# -- a connection that goes bad halfway -------------------------------------
#
# archive.org answers from whichever of its nodes the redirect picks, and they
# are not alike: the same file asked for four times in one minute came back at
# 543, 35, 22 and 543 KB/s. At the slow end a 2 GB disc is twenty hours, and
# the app sat through it, because a transfer that is moving is not a transfer
# that has failed.
#
# The rule has to cut both ways, and the second half is the harder one:
# somebody on a slow line has a slow line, and dropping their connection every
# minute to go looking for a better one they cannot have would be worse than
# useless. So it is measured against what this download has itself already
# achieved - never against a number chosen in advance.

print("\na connection that goes bad, and one that was never good")

_SIZE = 48 * 1024 * 1024
downloads.SLOW_WINDOW = 1.5
downloads.STALL_SECONDS = 6.0
_seen = []


def _rate_server(mode):
    """Serves fast then collapses, or is slow from beginning to end."""

    class Rate(http.server.BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def log_message(self, *a):
            pass

        def do_GET(self):  # noqa: N802
            nth = len(_seen)
            _seen.append(mode)
            rng = self.headers.get("Range")
            at = int(rng.split("=", 1)[1].split("-", 1)[0]) if rng else 0
            self.send_response(206 if at else 200)
            self.send_header("Content-Length", str(_SIZE - at))
            self.send_header("Accept-Ranges", "bytes")
            if at:
                self.send_header("Content-Range",
                                 f"bytes {at}-{_SIZE-1}/{_SIZE}")
            self.end_headers()
            sent, began = at, time.time()
            while sent < _SIZE:
                # Only the first connection collapses; a second one is given
                # the good rate, which is the whole point of reconnecting.
                quick = (nth > 0 or time.time() - began < 2.0
                         if mode == "collapse" else False)
                try:
                    self.wfile.write(b"\0" * 65536)
                except OSError:
                    return
                sent += 65536
                time.sleep(0.02 if quick else 0.35)

    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Rate)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def _watch(mode, seconds):
    _seen.clear()
    srv = _rate_server(mode)
    where = _box / f"rate-{mode}"
    where.mkdir(parents=True, exist_ok=True)
    downloads.save_settings({"folder": str(where), "extract": False})
    man = downloads.Manager()
    [jid] = man.add([{"url": f"http://127.0.0.1:{srv.server_address[1]}/x.bin",
                      "filename": "x.bin", "console": "PlayStation",
                      "source": "t", "size": _SIZE}])
    time.sleep(seconds)
    job = man._jobs[jid]  # noqa: SLF001
    man.pause_all()
    srv.shutdown()
    return job, len(_seen)


_job, _conns = _watch("collapse", 9)
check("a collapsed connection is dropped", _job.slow_retries >= 1, True)
check("...and another one taken out", _conns >= 2, True)
# Reconnecting to escape a bad server is not a failed attempt, and must not
# spend one - five of those and the download dies for having gone too well.
check("...without spending a retry", _job.attempts, 1)

_job, _conns = _watch("slow", 9)
check("a line that is only ever slow is left alone", _job.slow_retries, 0)
check("...on the one connection it started with", _conns, 1)

downloads.SLOW_WINDOW = 45.0
downloads.STALL_SECONDS = 90.0

httpd.shutdown()
print(f"\n{ok} passed, {fail} failed")
sys.exit(1 if fail else 0)
