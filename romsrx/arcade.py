"""Arcade, where the name of the file is the whole of its identity.

Every other console in this app is matched by title and then, if the file is
on the disk, confirmed by hashing it. Arcade works neither way, and the reason
is worth stating plainly because it makes the hard problem easy.

An arcade "game" is a MAME romset: a zip of chip dumps named for the board,
not for the game. `dkaccel.zip` is Donkey Kong Accelerate and nothing about
the name says so. Title matching cannot work here at all - there is no title
in the filename to match.

What replaces it is better. RetroAchievements does not hash the contents of an
arcade romset; it hashes the romset's short name, and rcheevos does exactly
this and nothing else:

    md5("dkaccel") == 14f9690de97d3c7d4036a83df6df9964

which is the hash their own API lists for that set. So the identity of an
arcade game is a string, the string is the filename, and the answer is exact:
no ladder of spellings, no near misses, and no need to download a byte to be
certain. A romset either is the one the set was built on or it is not, and the
filename settles it.

Measured when this was written: of the 530 arcade sets RetroAchievements has,
504 are on MiNERVA's FinalBurn Neo shelf, matched this way.
"""

from __future__ import annotations

import hashlib
import json
import threading
import time
import urllib.parse
import urllib.request

from . import rapi, retro
from .paths import user

CONSOLE = "Arcade"

# The same endpoint set_sizes uses, asked with h=1 so it answers with the
# hashes as well. One request for the whole console.
LIST_URL = retro.SIZES_URL
LIFE = 7 * 24 * 3600

_hashes: dict[int, dict[int, list[str]]] = {}
_lock = threading.Lock()


def romset_hash(filename: str) -> str:
    """The number RetroAchievements knows a romset by, from its name alone.

    The short name is the filename with its extension off - 'dkaccel.zip'
    becomes 'dkaccel'. Case matters: md5('DKACCEL') is a different number and
    is not one the site has ever heard of, so nothing here folds case.
    """
    name = str(filename or "").strip()
    if not name:
        return ""
    short = name.rsplit(".", 1)[0] if "." in name else name
    return hashlib.md5(short.encode("utf-8")).hexdigest() if short else ""


def _cache_file(console_id: int):
    return user("retro") / f"arcade_{console_id}.json"


def _fetch(console_id: int, key: str) -> dict[int, list[str]] | None:
    asked = urllib.parse.urlencode({"i": console_id, "f": 1, "h": 1, "y": key})
    request = urllib.request.Request(f"{LIST_URL}?{asked}",
                                     headers={"User-Agent": retro.USER_AGENT})
    try:
        listed = json.loads(
            rapi.read(request, timeout=120).decode("utf-8", "replace"))
    except Exception:  # noqa: BLE001 - no answer is not a wrong answer
        return None
    if not isinstance(listed, list):
        return None

    out: dict[int, list[str]] = {}
    for row in listed:
        if not isinstance(row, dict):
            continue
        game = retro._number(row, "id", "ID")  # noqa: SLF001
        found = [str(h).lower() for h in (row.get("Hashes") or []) if h]
        if game and found:
            out[int(game)] = found
    return out


def accepted(console: str = CONSOLE) -> dict[int, list[str]]:
    """{game id: [hash, ...]} for a whole console, or {}.

    Cached on disk for a week beside the set sizes, and for the same reason:
    it is one request that answers for every game on the machine, and asking
    it again on every page draw would be rude to a site that is doing this
    for free.
    """
    from . import artwork  # noqa: PLC0415 - only this needs the key

    console_id = retro.CONSOLES.get((console or "").strip())
    key = artwork.settings()["retroachievements"].get("api_key") or ""
    if not console_id or not key:
        return {}

    with _lock:
        if console_id in _hashes:
            return _hashes[console_id]

    found = None
    path = _cache_file(console_id)
    try:
        with open(path, encoding="utf-8") as fh:
            saved = json.load(fh)
        if time.time() - float(saved.get("at") or 0) < LIFE:
            found = {int(k): v for k, v in (saved.get("hashes") or {}).items()}
    except (OSError, ValueError, TypeError):
        found = None

    if found is None:
        found = _fetch(console_id, key)
        if found is None:
            return {}
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w", encoding="utf-8") as fh:
                json.dump({"at": time.time(),
                           "hashes": {str(k): v for k, v in found.items()}}, fh)
        except OSError:
            pass

    with _lock:
        _hashes[console_id] = found
    return found


def game_by_hash(console: str = CONSOLE) -> dict[str, int]:
    """{romset hash: game id} - the accepted list, read the other way round."""
    out: dict[str, int] = {}
    for game, digests in (accepted(console) or {}).items():
        for digest in digests:
            out.setdefault(str(digest).lower(), int(game))
    return out


def by_hash(conn, console: str = CONSOLE) -> dict[str, str]:
    """{romset hash: title_norm} for every arcade file in the index.

    Built off the filename because that is where the identity is. The norm
    comes back rather than the name so the rest of the app can carry on asking
    for copies the way it does for every other console.
    """
    out: dict[str, str] = {}
    try:
        rows = conn.execute(
            "SELECT filename, title_norm FROM files WHERE console = ?",
            (console,))
    except Exception:  # noqa: BLE001 - an index still being built
        return out
    for filename, norm in rows:
        digest = romset_hash(filename)
        if digest:
            out.setdefault(digest, norm)
    return out


def name_files(conn, console: str = CONSOLE) -> int:
    """Give the indexed romsets the names of the games they are.

    A shelf of arcade files is a list of board names - dkong, sf2ce, locomotn -
    and a person searching for Donkey Kong will not find one of them. The
    romsets were ranked correctly and were unfindable, which is most of the
    way to useless.

    So once the shelf is indexed, every romset RetroAchievements can name gets
    that name written onto its row. The filename is left exactly as it is,
    because the filename is the identity and everything here reads it; only
    `title` and `title_norm` change, which are the two columns the search and
    the FTS index are built on. The update trigger keeps the two in step.

    Idempotent, and safe to run when there is no key or no network: a romset
    nothing can name keeps the board name it already had, which is no worse
    than before.
    """
    from .names import normalize_title  # noqa: PLC0415 - leaf import

    titles: dict[str, str] = {}
    ids = game_by_hash(console)
    if not ids:
        return 0
    # The console's set list, which is where the titles are.
    for game, row in (retro.set_sizes(console) or {}).items():
        title = str(row.get("title") or "").strip()
        if title:
            titles[int(game)] = title
    if not titles:
        return 0

    changed = 0
    rows = list(conn.execute(
        "SELECT id, filename, title FROM files WHERE console = ?", (console,)))
    with conn:
        for row_id, filename, was in rows:
            game = ids.get(romset_hash(filename))
            title = titles.get(game) if game else ""
            if not title or title == was:
                continue
            conn.execute(
                "UPDATE files SET title = ?, title_norm = ? WHERE id = ?",
                (title, normalize_title(title), row_id))
            changed += 1
    return changed


def boards(conn, console: str = CONSOLE) -> dict[str, str]:
    """{romset hash: board name} - the short name, without its extension.

    Separate from by_hash because the two answer different questions now that
    name_files has run: by_hash says which indexed *game* a set is, and this
    says what the file behind it is called. Before the renaming they were the
    same string, which is exactly the sort of coincidence worth not relying on.
    """
    out: dict[str, str] = {}
    try:
        rows = conn.execute(
            "SELECT filename FROM files WHERE console = ?", (console,))
    except Exception:  # noqa: BLE001 - an index still being built
        return out
    for (filename,) in rows:
        digest = romset_hash(filename)
        if digest:
            out.setdefault(digest, str(filename).rsplit(".", 1)[0])
    return out


def match(shelf: dict[str, str], wanted: list[str]) -> str:
    """The indexed title_norm for a set, given the hashes it accepts.

    "" when none of them is on the shelf. There is nothing to fall back to
    and that is the point: a romset whose name is not one the set names is
    a different board, and offering it would be offering a game that cannot
    load.
    """
    for digest in wanted or ():
        found = shelf.get(str(digest).lower())
        if found:
            return found
    return ""
