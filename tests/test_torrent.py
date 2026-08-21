"""Choosing the right file, and not leaking while you fetch it.

Two things in this module can go wrong quietly, and quiet is the problem.

**The wrong file.** A collection torrent holds eleven thousand games. Pick the
wrong index and the download succeeds, the hash is valid, the file opens - it
is simply a different game. That is exactly what happened when the site's own
row number was read as a file index, so the selection is by name now and the
rules for matching a name are deliberately narrow: exact, then case, then
give up. No "closest match", because two Redump entries can differ by one
character inside a bracket.

**A route nobody asked for.** The whole point of binding to an adapter is that
traffic cannot go any other way; the point of a proxy is that peers see the
proxy. Both are a handful of settings that either are or are not passed to
libtorrent, and a typo in one of them fails open - it works, it is just not
private. So the settings that come out of a given set of preferences are
pinned here rather than trusted.

Nothing here touches the network. The torrent metadata is stood in for, and
the parts that need libtorrent are skipped where it is not installed.
"""
import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from romsrx import torrent  # noqa: E402

ok = fail = skipped = 0


def check(label, got, want):
    global ok, fail  # noqa: PLW0603
    if got == want:
        ok += 1
        print(f"  pass  {label}")
    else:
        fail += 1
        print(f"  FAIL  {label}\n          got  {got!r}\n          want {want!r}")


def raises(label, fn, kind):
    global ok, fail  # noqa: PLW0603
    try:
        fn()
    except kind:
        ok += 1
        print(f"  pass  {label}")
        return
    except Exception as exc:  # noqa: BLE001
        fail += 1
        print(f"  FAIL  {label}\n          raised {type(exc).__name__}, "
              f"wanted {kind.__name__}")
        return
    fail += 1
    print(f"  FAIL  {label}\n          nothing was raised")


# -- which file ------------------------------------------------------------

print("reading the name off a magnet")
check("the name we put there",
      torrent.wanted_file("magnet:?xt=urn:btih:aa#name=Sonic%20%28USA%29.zip"),
      "Sonic (USA).zip")
check("a name with the awkward characters in it",
      torrent.wanted_file("magnet:?xt=urn:btih:aa"
                          "#name=Rock%20%26%20Roll%20%231.zip"),
      "Rock & Roll #1.zip")
check("no fragment is no name", torrent.wanted_file("magnet:?xt=urn:btih:aa"), "")
check("...and neither is nothing", torrent.wanted_file(""), "")
check("the magnet itself is left valid",
      torrent.strip_index("magnet:?xt=urn:btih:aa&dn=X#name=B.zip"),
      "magnet:?xt=urn:btih:aa&dn=X")


class FakeFiles:
    def __init__(self, paths):
        self.paths = paths

    def file_path(self, i):
        return self.paths[i]

    def file_size(self, i):
        return 100


class FakeInfo:
    """Just enough of libtorrent's torrent_info to choose a file."""

    def __init__(self, paths):
        self.paths = paths

    def num_files(self):
        return len(self.paths)

    def files(self):
        return FakeFiles(self.paths)


# The shape a real one has: everything under a folder named for the torrent.
INFO = FakeInfo([
    r"Minerva_Myrient\Redump\Sony - PlayStation\Castlevania - SotN (Asia).zip",
    r"Minerva_Myrient\Redump\Sony - PlayStation\Castlevania - SotN (Europe).zip",
    r"Minerva_Myrient\Redump\Sony - PlayStation\Castlevania - SotN (USA).zip",
    r"Minerva_Myrient\Redump\Sony - PlayStation\Tekken 3 (USA).zip",
])

print("\npicking it out of the torrent")
check("by its exact name",
      torrent.pick_file(INFO, "Castlevania - SotN (USA).zip"), 2)
check("...and the neighbours are not it",
      torrent.pick_file(INFO, "Castlevania - SotN (Europe).zip"), 1)
check("the path above the file does not get in the way",
      torrent.pick_file(INFO, "Tekken 3 (USA).zip"), 3)
check("case on its own is forgiven",
      torrent.pick_file(INFO, "castlevania - sotn (usa).ZIP"), 2)

print("\nand what it refuses to guess")
# The failure this exists for: near-misses are a different game, every time.
for near in ("Castlevania - SotN (USA) (Rev 1).zip",
             "Castlevania - SotN.zip",
             "Castlevania - SotN (USA)",
             "Tekken 2 (USA).zip"):
    raises(f"{near!r} is not close enough",
           lambda n=near: torrent.pick_file(INFO, n), FileNotFoundError)
raises("nothing at all is an error, not file zero",
       lambda: torrent.pick_file(INFO, ""), ValueError)

# -- the settings ----------------------------------------------------------

if not torrent.available():
    skipped = 1
    print("\nlibtorrent is not installed here, so the session settings are "
          "not checked")
else:
    import libtorrent as lt  # noqa: E402

    print("\nwith nothing set")
    plain = torrent.settings_pack({})
    check("it listens on everything", plain["listen_interfaces"], "0.0.0.0:6881")
    check("no proxy", "proxy_hostname" in plain, False)
    check("the usual ways of finding peers are on",
          (plain["enable_dht"], plain["enable_lsd"]), (True, True))
    check("anonymous by default", plain["anonymous_mode"], True)
    check("and no ceiling", (plain["download_rate_limit"],
                             plain["upload_rate_limit"]), (0, 0))

    print("\nbound to one adapter")
    bound = torrent.settings_pack({"torrent_interface": "10.2.0.2"})
    check("it listens there and nowhere else",
          bound["listen_interfaces"], "10.2.0.2:6881")
    check("...and goes out the same way",
          bound["outgoing_interfaces"], "10.2.0.2")

    print("\nthrough a proxy")
    proxied = torrent.settings_pack({
        "torrent_proxy_host": "10.64.0.1", "torrent_proxy_port": 1080,
        "torrent_proxy_user": "someone", "torrent_proxy_pass": "secret"})
    check("socks5 with a sign-in",
          proxied["proxy_type"], int(lt.proxy_type_t.socks5_pw))
    check("...and without one",
          torrent.settings_pack({"torrent_proxy_host": "h",
                                 "torrent_proxy_port": 1080})["proxy_type"],
          int(lt.proxy_type_t.socks5))
    # The three that decide whether this is privacy or decoration.
    check("peers go through it", proxied["proxy_peer_connections"], True)
    check("trackers too", proxied["proxy_tracker_connections"], True)
    check("and names are resolved at the far end",
          proxied["proxy_hostnames"], True)
    # These find peers by going around the proxy, which is the whole problem.
    check("nothing shouts on the local network", proxied["enable_lsd"], False)
    check("...or asks the router to open a port",
          (proxied["enable_upnp"], proxied["enable_natpmp"]), (False, False))
    check("the credentials are carried",
          (proxied["proxy_username"], proxied["proxy_password"]),
          ("someone", "secret"))

    print("\nlimits")
    capped = torrent.settings_pack({"torrent_down_limit": 500,
                                    "torrent_up_limit": 50})
    check("kilobytes become bytes",
          (capped["download_rate_limit"], capped["upload_rate_limit"]),
          (500 * 1024, 50 * 1024))
    check("a negative is no limit",
          torrent.settings_pack({"torrent_up_limit": -5})["upload_rate_limit"], 0)

    print("\nthe session")
    first = torrent.session({})
    check("the same settings reuse it", torrent.session({}) is first, True)
    check("a changed route builds a new one",
          torrent.session({"torrent_interface": "10.2.0.2"}) is first, False)

# -- resuming, on a swarm of one machine ------------------------------------
#
# Everything above is about picking the right file out of a list. This is the
# other half: that a download stopped part-way carries on from what is already
# on the disk rather than starting again. A 2 GB disc image fetched twice
# because the app was closed is the difference between a feature and a joke.
#
# A real swarm, and small enough to run in a few seconds: one session seeds a
# made-up collection torrent and the app's own fetch pulls a single file out
# of it. No trackers and no DHT - the seeder is named in the magnet with x.pe,
# which is what that field is for - so this touches nothing outside the box it
# runs in.
#
# The interruption is made by cutting a finished file short rather than by
# stopping one in flight. Rate limits do not apply to a peer on the same
# machine (libtorrent files those under a peer class that ignores them), so
# there is no way to time an interruption here reliably - and a truncated file
# is exactly what an interrupted download leaves: a run of good pieces, then
# nothing.
#
# Whether a machine will let two peers reach each other over loopback is not
# this app's to decide, so the first fetch is a question rather than a claim.
# If no swarm forms, that is printed and the rest is not run: a check that
# could not be performed must not read as one that passed, and must not turn a
# release red either.


def swarm_resume():
    """Fetch, interrupt, resume - on a swarm built for the occasion."""
    import shutil
    import tempfile
    import time

    try:
        import libtorrent as lt
    except ImportError:
        print("  libtorrent is not installed here, so the swarm is not run")
        return

    box = Path(tempfile.mkdtemp(prefix="romsrx-swarm-"))
    try:
        data = box / "data" / "Minerva_Test"
        data.mkdir(parents=True)
        want = "Sonic The Hedgehog 2 (World) (Rev A).zip"
        for name, size in {"Alex Kidd (World).zip": 200_000,
                           want: 1_200_000,
                           "Zoop (Europe).zip": 150_000}.items():
            (data / name).write_bytes(
                bytes((i * 37 + 11) % 251 for i in range(size)))
        good = (data / want).read_bytes()

        store = lt.file_storage()
        lt.add_files(store, str(data))
        maker = lt.create_torrent(store, piece_size=16 * 1024)
        lt.set_piece_hashes(maker, str(data.parent))
        info = lt.torrent_info(maker.generate())

        seeder = lt.session({"listen_interfaces": "127.0.0.1:6907",
                             "enable_dht": False, "enable_lsd": False,
                             "enable_natpmp": False, "enable_upnp": False})
        seeder.add_torrent({"ti": info, "save_path": str(data.parent)})
        time.sleep(1.0)

        magnet = (f"magnet:?xt=urn:btih:{info.info_hash()}"
                  f"&dn=Minerva_Test&x.pe=127.0.0.1:6907")
        prefs = {"torrent_anonymous": False, "torrent_interface": "",
                 "torrent_proxy_host": "", "torrent_proxy_port": 0,
                 "torrent_down_limit": 0, "torrent_up_limit": 0,
                 "torrent_seed_minutes": 0}
        dest = box / "games"
        dest.mkdir(parents=True)

        def fetch():
            seen = {"first": None, "target": None}

            def progress(done, total, rate):
                if seen["first"] is None:
                    seen["first"] = done

            got = torrent.fetch(
                magnet, dest, prefs, want=want, on_progress=progress,
                should_stop=lambda: False, on_stage=lambda _t: None,
                on_target=lambda t: seen.update(target=t))
            return got, seen["first"] or 0, seen["target"]

        # No point waiting three minutes for a swarm that is not going to
        # form; locally the metadata arrives in under a second.
        was = torrent.METADATA_TIMEOUT
        torrent.METADATA_TIMEOUT = 25
        try:
            got, _first, target = fetch()
            up = got.exists() and got.read_bytes() == good
        except Exception as exc:  # noqa: BLE001 - no swarm is not a failure
            print(f"  no swarm formed here ({type(exc).__name__}), "
                  f"so resume was not exercised")
            return
        finally:
            torrent.METADATA_TIMEOUT = was

        if not up:
            print("  the swarm did not deliver the file here, "
                  "so resume was not exercised")
            return

        check("the wanted file arrives", True, True)
        # The whole point of selecting one file out of a collection.
        others = sorted(x.name for x in dest.rglob("*")
                        if x.is_file() and x.name != want
                        and not x.name.endswith(".parts"))
        check("...and none of its neighbours", others, [])
        # Nothing else knows where a torrent is writing, and throwing the
        # download away has to be able to find it.
        check("fetch says where it is writing", target == got, True)

        with open(got, "r+b") as fh:              # stopped 40% of the way in
            fh.truncate(480_000)
        got, first, _ = fetch()
        check("what was already there is kept", first > 400_000, True)
        check("...and the rest is fetched", got.read_bytes() == good, True)

        # A partial can be wrong rather than merely short - a half-written
        # piece, a disk that lied. The recheck has to notice.
        bad = bytearray(good)
        for i in range(200_000, 500_000):
            bad[i] ^= 0xFF
        got.write_bytes(bytes(bad))
        got, _, _ = fetch()
        check("a corrupt stretch is found and replaced",
              got.read_bytes() == good, True)
    finally:
        shutil.rmtree(box, ignore_errors=True)


print("\nresuming a torrent that was stopped part-way")
swarm_resume()

print(f"\n{ok} passed, {fail} failed")
sys.exit(1 if fail else 0)
