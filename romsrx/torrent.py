"""Fetching one game out of a whole-console torrent.

MiNERVA shares a collection as a single torrent - eleven thousand PlayStation
games under one infohash. minerva.py records which one is wanted by putting
its filename on the end of the magnet as `#name=...`. This is the part that
acts on it.

BitTorrent has always been able to fetch one file out of a thousand: every
file gets a priority, and zero means "never ask anyone for this". So the whole
job is: join the swarm, wait for the metadata, set every priority to zero
except the one wanted, and let it run. What comes off the wire is that file
plus whatever shares a piece with its neighbours, which is a few megabytes at
the edges.

The file is chosen by name, out of the metadata, and never by position. The
site publishes a per-row number that looks exactly like a file index and is
not one - it counts rows in the listing, which holds entries the torrent does
not and sorts them differently. Trusting it downloaded a working copy of the
wrong game, in silence, which is the worst way for this to fail. The torrent's
own file list is the only thing that cannot be wrong about what is in the
torrent.

Two things are worth saying plainly, because they are not obvious and they are
not this module's to decide.

**BitTorrent uploads.** Downloading over HTTP tells archive.org your address
and nobody else; joining a swarm tells everyone in it. That is the deal, and
the app says so before the first torrent rather than after.

**These magnets carry no trackers.** Peers are found over DHT, which is UDP.
A SOCKS5 proxy generally does not carry UDP, so turning the proxy on can leave
the session with no way to find anybody. The honest arrangement is therefore:
bind to an interface (a VPN adapter) as the way to stay private, and treat the
proxy as the alternative for people whose provider offers one that works. Both
are offered; neither is pretended to be the other.

Nothing here is imported unless libtorrent is installed. It is optional the
way pywebview is - without it MiNERVA games simply offer their magnet to
whatever torrent client the reader already has.
"""

from __future__ import annotations

import re
import threading
import time
import urllib.parse
from pathlib import Path, PurePosixPath

# The fragment minerva.py writes: which file in the collection is wanted.
NAME_IN_MAGNET = re.compile(r"#name=([^#]*)\s*$")

# How long to wait for the torrent's file list before giving up. These are
# trackerless magnets found over DHT, and DHT on a cold session takes a while
# to answer - but not five minutes, and somebody watching a progress bar
# deserves an answer either way.
METADATA_TIMEOUT = 180
# How long to wait for what has been downloaded to reach the disk.
# Generous: it is the tail of one file, and the alternative to waiting
# is handing back a file that is not all there yet.
FLUSH_TIMEOUT = 30

# How often the worker is told where things are.
TICK = 0.5

_lock = threading.Lock()
_state: dict = {"session": None, "settings": None}


def available() -> bool:
    """Whether this build can do it at all."""
    try:
        import libtorrent  # noqa: F401, PLC0415
    except Exception:  # noqa: BLE001 - not installed, or installed broken
        return False
    return True


def wanted_file(magnet: str) -> str:
    """The filename on the end of a magnet, or "" if it has none.

    Empty matters: a magnet with no name on it is a whole collection, and
    starting a two-hundred-terabyte download because a fragment went missing
    is not a thing to do by accident.
    """
    found = NAME_IN_MAGNET.search(str(magnet or ""))
    return urllib.parse.unquote(found.group(1)) if found else ""


def pick_file(info, wanted: str) -> int:
    """Which file in the torrent is the one asked for.

    By exact name first. Failing that, by name ignoring case and the
    difference between the separators archives like to change - and no
    further. There is no "closest match" here on purpose: two games in a
    Redump set can differ by one character in a bracket, and a fuzzy answer
    to "which file" is a wrong game nobody will notice.
    """
    if not wanted:
        raise ValueError("that magnet does not say which file is wanted")

    files = info.files()
    names = [PurePosixPath(files.file_path(i).replace("\\", "/")).name
             for i in range(info.num_files())]
    if wanted in names:
        return names.index(wanted)

    folded = [n.casefold() for n in names]
    if wanted.casefold() in folded:
        return folded.index(wanted.casefold())

    raise FileNotFoundError(
        f"{wanted!r} is not in this torrent - it holds {info.num_files()} "
        "files, and the collection may have been rebuilt since it was indexed")


def strip_index(magnet: str) -> str:
    """The magnet as BitTorrent understands it, without our fragment."""
    return str(magnet or "").split("#", 1)[0]


# -- how the session is configured -----------------------------------------

def settings_pack(prefs: dict) -> dict:
    """libtorrent settings from the app's own.

    Assembled here rather than at the call site so there is one place to read
    when asking "what exactly is this doing with my connection".
    """
    import libtorrent as lt  # noqa: PLC0415

    interface = str(prefs.get("torrent_interface") or "").strip()
    pack = {
        # Bound to one adapter, or to everything. This is the kill switch:
        # named to a VPN's adapter, nothing leaves by any other route, and if
        # that adapter goes away the transfers stop rather than falling back
        # to the ordinary connection.
        "listen_interfaces": f"{interface}:6881" if interface else "0.0.0.0:6881",
        "outgoing_interfaces": interface,
        # Says as little as possible about the client on the wire.
        "anonymous_mode": bool(prefs.get("torrent_anonymous", True)),
        "alert_mask": lt.alert.category_t.error_notification
                      | lt.alert.category_t.status_notification,
        "user_agent": "",
    }

    host = str(prefs.get("torrent_proxy_host") or "").strip()
    port = int(prefs.get("torrent_proxy_port") or 0)
    user = str(prefs.get("torrent_proxy_user") or "")
    password = str(prefs.get("torrent_proxy_pass") or "")

    if host and port:
        pack.update({
            "proxy_type": int(lt.proxy_type_t.socks5_pw if user
                              else lt.proxy_type_t.socks5),
            "proxy_hostname": host,
            "proxy_port": port,
            "proxy_username": user,
            "proxy_password": password,
            # All three matter. Without peer connections the proxy only hides
            # tracker traffic, which for a trackerless magnet is nothing at
            # all; without proxy_hostnames the names are resolved here, which
            # tells the local DNS server exactly what is being fetched.
            "proxy_peer_connections": True,
            "proxy_tracker_connections": True,
            "proxy_hostnames": True,
            # These find peers by shouting on the local network or asking the
            # router to open a port. Both go around the proxy, so both are off
            # whenever one is set.
            "enable_lsd": False,
            "enable_upnp": False,
            "enable_natpmp": False,
            # DHT is UDP and a SOCKS5 proxy usually will not carry it. Left on
            # because off guarantees no peers, and the app says in Settings
            # that a proxy may mean none are found.
            "enable_dht": True,
        })
    else:
        pack.update({
            "enable_dht": True, "enable_lsd": True,
            "enable_upnp": True, "enable_natpmp": True,
        })

    down = int(prefs.get("torrent_down_limit") or 0)
    up = int(prefs.get("torrent_up_limit") or 0)
    pack["download_rate_limit"] = max(0, down) * 1024
    pack["upload_rate_limit"] = max(0, up) * 1024
    return pack


def session(prefs: dict):
    """The one session, rebuilt when the settings that shape it change.

    One rather than one per download: a session is a listening socket, a DHT
    node and a routing table, and three downloads should share all of that
    rather than each standing up their own.
    """
    import libtorrent as lt  # noqa: PLC0415

    pack = settings_pack(prefs)
    with _lock:
        if _state["session"] is not None and _state["settings"] == pack:
            return _state["session"]
        if _state["session"] is not None:
            # Rebuilt rather than reconfigured: a change of proxy or interface
            # is exactly the change that must not leave an old connection open
            # on the old route.
            try:
                _state["session"] = None
            except Exception:  # noqa: BLE001
                pass
        made = lt.session(pack)
        _state["session"] = made
        _state["settings"] = pack
        return made


# -- giving it back ---------------------------------------------------------
#
# A finished torrent is dropped the moment the file arrives, which is right as
# a default and wrong as the only behaviour: MiNERVA is a volunteer archive,
# and an app that only ever takes from a swarm is one that helps kill the
# thing it depends on. So the handle can be kept for a while instead.
#
# One reaper thread for all of them rather than a thread per file. It holds
# nothing but the handles and the times they are due, and a session rebuilt
# under it - a change of proxy or adapter - takes its torrents with it, which
# is the correct outcome: those are exactly the changes that must not leave an
# old connection open on the old route.

_seeding: list[tuple] = []
_reaper: threading.Thread | None = None


def _reap() -> None:
    while True:
        time.sleep(5)
        now = time.time()
        with _lock:
            due = [row for row in _seeding if row[2] <= now]
            for row in due:
                _seeding.remove(row)
            done = not _seeding
        for ses, handle, _until in due:
            _drop(ses, handle)
        if done:
            with _lock:
                global _reaper  # noqa: PLW0603 - one reaper, restarted on demand
                if not _seeding:
                    _reaper = None
                    return


def seed_for(ses, handle, minutes: float) -> bool:
    """Keep sharing this torrent back for a while. False if not asked to."""
    if minutes <= 0:
        return False
    global _reaper  # noqa: PLW0603 - see _reap
    with _lock:
        _seeding.append((ses, handle, time.time() + minutes * 60))
        if _reaper is None or not _reaper.is_alive():
            _reaper = threading.Thread(target=_reap, daemon=True)
            _reaper.start()
    return True


def seeding_count() -> int:
    with _lock:
        return len(_seeding)


def _drop(ses, handle) -> None:
    """Let a torrent go, keeping the file and dropping the .parts beside it."""
    import libtorrent as lt  # noqa: PLC0415

    try:
        ses.remove_torrent(handle, lt.session.delete_partfile)
    except Exception:  # noqa: BLE001 - already gone, or an older build
        try:
            ses.remove_torrent(handle)
        except Exception:  # noqa: BLE001
            pass


def interface_is_up(name: str) -> bool:
    """Is the adapter the settings name actually there?

    Asked before starting rather than after failing: bound to a VPN that is
    not running, libtorrent listens on nothing and the download simply never
    begins, which looks like a broken app rather than a disconnected VPN.
    """
    wanted = str(name or "").strip()
    if not wanted:
        return True
    try:
        import socket  # noqa: PLC0415

        if wanted.replace(".", "").isdigit():
            # An address: is anything on this machine using it?
            _, _, addresses = socket.gethostbyname_ex(socket.gethostname())
            return wanted in addresses or wanted == "0.0.0.0"
        # A name: libtorrent resolves it itself, and there is no portable way
        # to check from here, so it is taken on trust.
        return True
    except OSError:
        return True


# -- the download itself ----------------------------------------------------

class Stopped(Exception):
    """Raised out of fetch() when the caller asked it to stop."""


def fetch(magnet: str, dest: Path, prefs: dict, *, want: str = "",
          on_target=None,
          on_progress=None, should_stop=None, on_stage=None) -> Path:
    """Fetch the one file wanted out of `magnet`, into `dest`. Returns its path.

    `want` is the filename, and it wins over anything on the magnet. The job
    in the queue already knows what it asked for, and taking it from there
    means an index written by an older build - which put a file *number* on
    the magnet, before that number turned out to be the site's row order and
    not the torrent's - still fetches the right game rather than a neighbour.

    `on_progress(done, total, rate)` is called about twice a second, in the
    same units the HTTP worker reports, so the queue does not have to know
    which kind of job it is looking at.
    """
    import libtorrent as lt  # noqa: PLC0415

    wanted = str(want or "").strip() or wanted_file(magnet)
    if not wanted:
        raise ValueError("nothing says which file in this torrent is wanted")

    stop = should_stop or (lambda: False)
    stage = on_stage or (lambda _text: None)
    ses = session(prefs)

    params = lt.parse_magnet_uri(strip_index(magnet))
    params.save_path = str(dest)
    # Added in upload mode so the metadata arrives without a single byte of
    # game data being requested first. Priorities cannot be set until the file
    # list exists, and without this the swarm starts sending pieces of
    # whatever it likes in the meantime.
    params.flags |= lt.torrent_flags.upload_mode

    handle = ses.add_torrent(params)
    finished = False
    try:
        stage("metadata")
        waited = 0.0
        while not handle.status().has_metadata:
            if stop():
                raise Stopped
            time.sleep(TICK)
            waited += TICK
            if waited > METADATA_TIMEOUT:
                raise TimeoutError(
                    "no peers answered with the file list - these magnets have "
                    "no trackers, so this needs DHT, which some networks block")

        info = handle.torrent_file()
        index = pick_file(info, wanted)

        # Everything off, then the one wanted back on. Done in that order so
        # there is never a moment where the whole collection is wanted.
        handle.prioritize_files([0] * info.num_files())
        handle.file_priority(index, 4)
        handle.unset_flags(lt.torrent_flags.upload_mode)

        files = info.files()
        target = dest / files.file_path(index)
        total = files.file_size(index)
        # Where the bytes are actually going, which is not where they will end
        # up: a collection torrent writes into a folder of its own, and only
        # the finished file is moved out of it. Said out loud because a
        # download that is thrown away half-finished has to be able to find
        # what it left behind - nothing else knows this path. See downloads.
        if on_target:
            try:
                on_target(target)
            except Exception:  # noqa: BLE001 - a listener must not stop a fetch
                pass
        # While libtorrent verifies what is already on disk, nothing is
        # reported at all.
        #
        # `file_progress` answers 0 for the whole of that check, so a resumed
        # download announced itself as starting from nothing and then jumped
        # to what was actually there. Cosmetic on a small file and not on a
        # 2 GB disc, where the first thing somebody sees is "0 bytes" for a
        # transfer that is four-fifths done.
        #
        # It also made the resume test race the checker: it records the first
        # figure it is given, and on a slower machine that figure was the
        # zero. Windows passed and Linux did not, which is the signature of a
        # test measuring how fast the runner is rather than what the code
        # does.
        checking = tuple(
            getattr(lt.torrent_status.states, name)
            for name in ("checking_files", "checking_resume_data")
            if hasattr(lt.torrent_status.states, name))

        stage("checking")
        said_downloading = False
        while True:
            if stop():
                raise Stopped
            status = handle.status()
            if checking and status.state in checking:
                time.sleep(TICK)
                continue
            if not said_downloading:
                stage("downloading")
                said_downloading = True
            done = handle.file_progress()[index] if info.num_files() else 0
            if on_progress:
                on_progress(int(done), int(total), float(status.download_rate))
            if done >= total and total:
                break
            if status.state == lt.torrent_status.states.seeding:
                break
            time.sleep(TICK)

        # Downloaded is not the same as written. `file_progress` counts the
        # bytes that have arrived, and libtorrent buffers before it puts them
        # on the disk - so returning the moment the count was reached handed
        # the caller a path whose tail was still in memory, and the caller's
        # very next act is to move that file. On a fast machine the write
        # always won the race. On a slower one it did not, and what got moved
        # was short - a file that looks finished, is not, and was reported as
        # a successful download.
        try:
            handle.flush_cache()
        except Exception:  # noqa: BLE001 - older builds; the wait still covers it
            pass
        waited = 0.0
        while total and waited < FLUSH_TIMEOUT:
            try:
                if target.stat().st_size >= total:
                    break
            except OSError:
                pass                      # not visible yet
            time.sleep(TICK)
            waited += TICK

        if on_progress:
            on_progress(int(total), int(total), 0.0)
        finished = True
        return target
    finally:
        # Dropped unless the reader has asked to share it back, and dropped
        # outright on a download that failed or was cancelled - there is
        # nothing complete to give anyone in that case.
        #
        # `_drop` uses `delete_partfile` and nothing else. Selecting one file
        # out of a collection still pulls the two part-pieces at its edges,
        # and libtorrent parks those in a hidden .parts file beside the
        # download - which was being left in the games folder, one per
        # torrent, forever. The flag drops that and only that; the file that
        # was asked for is untouched.
        minutes = 0.0
        try:
            minutes = float(prefs.get("torrent_seed_minutes") or 0)
        except (TypeError, ValueError):
            minutes = 0.0
        if not (finished and seed_for(ses, handle, minutes)):
            _drop(ses, handle)
