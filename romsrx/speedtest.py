"""How fast is each shelf, right now, for one particular file.

The index knows a dozen places a game can be had from and has no opinion about
which is quick. It cannot have one: the copy that flew yesterday is the copy
that crawls tonight, because archive.org answers from whichever of its nodes
the redirect picks and a torrent is only as fast as whoever is seeding it this
minute. Measured against the real thing, the same PlayStation 2 disc came back
at 6.5 MB/s from one archive.org item, 10.5 MB/s from another, 7-9 MB/s over
MiNERVA's torrent, and 401 from a third that wants an account - all inside a
couple of minutes.

So the question "which of these is fastest" has no answer that can be looked
up. It can only be measured, and this measures it: a few seconds of the actual
transfer from each, in parallel, and the bytes thrown away.

What it is careful about
------------------------

**It downloads nothing.** Every probe reads for a moment and drops what it
read; nothing touches the download folder. The one thing on disk it could
affect - a part-finished file - it never opens.

**It asks for the end of the file, not the beginning.** A range request from
part-way in is the same work for the server, and it means a probe cannot be
mistaken by anything downstream for the start of a real download.

**It runs them at once.** Six sources probed one after another is half a
minute of somebody waiting; probed together it is the length of one, and they
are different hosts so they do not compete for anything but the line itself.
That last point is the honest caveat and the reason the numbers are called an
estimate: six transfers sharing one connection each read slower than one would
alone. It is the right trade - what matters is which is fastest, and they are
all handicapped equally.
"""

from __future__ import annotations

import concurrent.futures
import time
import urllib.parse

# Long enough to get past the connection setup and TLS, short enough that
# nobody wanders off. Measured from the first byte, so the handshake is not
# counted against a server that answers quickly afterwards.
SECONDS = 4.0

# A torrent needs its metadata before it can send anything, and for MiNERVA
# that is a 1,053-file list from a trackerless magnet, found over DHT. It
# arrives in about five seconds when it arrives at all - so this had been
# giving it half of the measuring budget, four seconds, and calling a perfectly
# healthy swarm "no peers" about half the time. Its own allowance now.
METADATA_SECONDS = 12.0
TORRENT_SECONDS = 8.0

# Never probe more than this many at once, however many the page sends.
MOST = 8

_SKIP = 4 * 1024 * 1024      # where in the file to read from


def _http_speed(url: str, size: int) -> dict:
    """Read for a few seconds and say how fast it went, in bytes a second."""
    import requests  # noqa: PLC0415 - the app's own dependency

    # From a little way in, so this can never look like the start of a real
    # download to anything watching, and so a server that streams a header
    # quickly and the body slowly is caught out.
    start = _SKIP if size and size > _SKIP * 2 else 0
    headers = {"User-Agent": "RomSrx/0.1"}
    if start:
        headers["Range"] = f"bytes={start}-"

    got = 0
    began = None
    try:
        with requests.get(url, headers=headers, stream=True,
                          timeout=(8, 8)) as resp:
            if resp.status_code == 401 or resp.status_code == 403:
                return {"ok": False, "why": "login"}
            if resp.status_code >= 400:
                return {"ok": False, "why": f"HTTP {resp.status_code}"}
            for chunk in resp.iter_content(128 * 1024):
                if began is None:
                    began = time.monotonic()   # the clock starts at byte one
                got += len(chunk)
                if time.monotonic() - began >= SECONDS:
                    break
    except Exception as exc:  # noqa: BLE001 - every failure is an answer here
        return {"ok": False, "why": type(exc).__name__.replace("Error", "")}

    if not got or began is None:
        return {"ok": False, "why": "nothing"}
    took = max(time.monotonic() - began, 0.05)
    return {"ok": True, "bytes_per_sec": got / took, "sampled": got}


def _torrent_speed(url: str, filename: str) -> dict:
    """The same question for a magnet, which has to find peers first."""
    try:
        from . import torrent  # noqa: PLC0415 - optional
        if not torrent.available():
            return {"ok": False, "why": "no torrent support"}
        import libtorrent as lt  # noqa: PLC0415
    except Exception:  # noqa: BLE001
        return {"ok": False, "why": "no torrent support"}

    import shutil  # noqa: PLC0415
    import tempfile  # noqa: PLC0415
    from pathlib import Path  # noqa: PLC0415

    from . import state  # noqa: PLC0415

    box = Path(tempfile.mkdtemp(prefix="romsrx-probe-"))
    ses = handle = None
    try:
        # Its own session, not the one running downloads use: adding a torrent
        # to that would change priorities under a transfer in flight, and a
        # measurement must not slow down the thing it is measuring.
        ses = lt.session(torrent.settings_pack(state.prefs()))
        params = lt.parse_magnet_uri(torrent.strip_index(url))
        params.save_path = str(box)
        params.flags |= lt.torrent_flags.upload_mode
        handle = ses.add_torrent(params)

        began = time.monotonic()
        while not handle.status().has_metadata:
            if time.monotonic() - began > METADATA_SECONDS:
                return {"ok": False, "why": "no peers"}
            time.sleep(0.25)

        info = handle.torrent_file()
        try:
            index = torrent.pick_file(info, filename)
        except Exception:  # noqa: BLE001 - the collection has moved on
            return {"ok": False, "why": "not in this torrent"}
        # Exactly what a real download asks for, so the figure is the figure.
        handle.prioritize_files([0] * info.num_files())
        handle.file_priority(index, 4)
        handle.unset_flags(lt.torrent_flags.upload_mode)

        best = 0.0
        seeds = peers = 0
        deadline = time.monotonic() + TORRENT_SECONDS
        while time.monotonic() < deadline:
            time.sleep(0.5)
            st = handle.status()
            best = max(best, float(st.download_rate))
            seeds = max(seeds, int(st.num_seeds))
            peers = max(peers, int(st.num_peers))
        if not best and not seeds:
            return {"ok": False, "why": "no peers"}
        # Reported as a floor, not an answer, and the page says so.
        #
        # A swarm takes about half a minute to open up: this same magnet reads
        # a few hundred KB/s in the first eight seconds and 7-9 MB/s once it
        # is going. Printing the eight-second figure beside archive.org's
        # full-speed one would send everybody to the slower source, so what
        # goes out is the number *and* the fact that it is still climbing,
        # with the seed count - which is the part that actually predicts where
        # it ends up and is known immediately.
        return {"ok": True, "bytes_per_sec": best, "torrent": True,
                "warming": True, "seeds": seeds, "peers": peers}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "why": type(exc).__name__.replace("Error", "")}
    finally:
        try:
            if ses is not None and handle is not None:
                ses.remove_torrent(handle, lt.session.delete_files)
            del ses
        except Exception:  # noqa: BLE001, S110
            pass
        shutil.rmtree(box, ignore_errors=True)


def one(item: dict) -> dict:
    url = str(item.get("url") or "")
    out = {"url": url}
    if not url:
        return {**out, "ok": False, "why": "no link"}
    if url.lower().startswith("magnet:"):
        return {**out, **_torrent_speed(url, str(item.get("filename") or ""))}
    if not url.lower().startswith(("http://", "https://")):
        return {**out, "ok": False, "why": "not a download"}
    try:
        size = int(item.get("size") or 0)
    except (TypeError, ValueError):
        size = 0
    return {**out, **_http_speed(url, size)}


def measure(items: list[dict]) -> dict:
    """Probe each of these and answer {results: [...]}, fastest first.

    A source that will not answer is a result too, and a useful one: "login"
    and "HTTP 500" are things worth seeing next to a speed, because the
    alternative is choosing that source and finding out slowly.
    """
    # One probe per shelf, not per row. A console's worth of Redump is split
    # across numbered parts that are all the same shelf as far as this
    # question goes, and five probes of it would crowd out the torrent - which
    # is regularly the fastest thing on the list and was being dropped by the
    # cap before this.
    wanted, seen = [], set()
    for item in items or []:
        if not isinstance(item, dict):
            continue
        url = str(item.get("url") or "")
        if not url:
            continue
        shelf = str(item.get("source") or "") or url
        if shelf in seen:
            continue
        seen.add(shelf)
        wanted.append(item)
        if len(wanted) >= MOST:
            break
    if not wanted:
        return {"results": []}

    # Two passes, because the two kinds cannot fairly share a line.
    #
    # A torrent opens slowly - it has to find peers, then ask them - while an
    # archive.org connection is at full speed almost at once. Probed together,
    # the HTTP transfers take the line while the swarm is still warming up and
    # the torrent is recorded at a fraction of what it can do: measured that
    # way the same MiNERVA magnet read 285 KB/s beside two HTTP probes, and
    # 7,000+ with the line to itself. That is not a slow source, it is a
    # rigged race.
    #
    # So the plain links go first, all at once, and the magnets after. It
    # costs one extra pass and there is rarely more than one magnet.
    plain = [i for i in wanted
             if not str(i.get("url") or "").lower().startswith("magnet:")]
    magnets = [i for i in wanted if i not in plain]

    found = []
    for batch in (plain, magnets):
        if not batch:
            continue
        with concurrent.futures.ThreadPoolExecutor(
                max_workers=len(batch)) as pool:
            found.extend(pool.map(one, batch))
    wanted = plain + magnets

    for row, item in zip(found, wanted):
        row["source"] = str(item.get("source") or "")
        row["filename"] = str(item.get("filename") or "")
        if row.get("ok"):
            row["host"] = urllib.parse.urlparse(row["url"]).hostname or ""
    # Fastest first, and everything that failed after everything that worked.
    found.sort(key=lambda r: (not r.get("ok"), -(r.get("bytes_per_sec") or 0)))
    return {"results": found}
