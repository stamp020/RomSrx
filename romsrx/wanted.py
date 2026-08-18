"""The list of games you said you wanted to play, and where to get them.

RetroAchievements keeps a "Want to Play" list. You add to it while browsing
their site - on a phone, on somebody else's machine, at two in the morning -
and it is exactly the list this app exists to act on: every one of them is a
game with an achievement set that you have said you intend to play, and this
app's whole job is turning "I want that game" into a file on the disk.

So the two are joined here. The list comes down whole, each game is looked for
in the index, and what comes back is a shelf where the ones that can be
downloaded say so and the ones that cannot say why.

Matching a title of theirs to a title in the index is the same problem retro.py
already solves in the other direction, and it is solved the same way: both
sides are folded through retro.match_keys(), which strips the region, the
studio in front, the article that No-Intro parks in the middle, and settles
Roman numerals and spacing. Measured against a real list of 78, folding one
side matched 55, folding both matched 61, and the whole ladder matched 70 -
the rest being four games no configured source carries and four that are hacks
rather than releases.

Four states, and telling them apart is most of the value here:

  have     already on the disk. Said first, because the commonest reason a
           wanted game cannot be found is that it is not missing.
  get      the index has it; the best copy is named and ready to queue.
  patch    a hack, a translation or a homebrew build. Their "game" is a patch
           over a release, not something anybody hands out finished, so it is
           marked rather than offered - see the patcher for the other half.
  none     nothing in the index. Honest and quite common: an index only holds
           what its sources hold.
"""

from __future__ import annotations

import json
import threading
import time
import urllib.error
import urllib.parse
import urllib.request

from . import db, rapi, retro

API = ("https://retroachievements.org/API/API_GetUserWantToPlayList.php")
PAGE = 100                  # their maximum
PAGES = 20                  # ...so up to 2,000, which is a long list
LIFE = 10 * 60              # a list somebody edits by hand, on another device

# Their tags for something that is not a plain release. A game wearing one of
# these is a patch over a ROM rather than a ROM, and no index carries it.
_PATCHED = ("~hack~", "~homebrew~", "~translation~", "~prototype~",
            "~unlicensed~", "~demo~")

# What a copy can be tagged as that makes it the wrong one to pick blind. A
# search shows every copy and lets somebody choose; this picks one on their
# behalf, so it has to know that "Sly 2 - Band of Thieves (USA) (Demo)" is not
# the game they put on their list - which is exactly what it offered before
# this list existed.
#
# Only the tags that mean "this is not the finished game". 'Alt', 'Rev' and
# the enhancement flags are all perfectly good copies and are left alone.
_JUNK_TAGS = ("Demo", "Beta", "Proto", "Sample", "Kiosk", "Taikenban",
              "Trial", "Pirate", "Program", "Debug")

_cache: tuple[float, list] | None = None
_lock = threading.Lock()

# RetroAchievements' console ids, the other way round. Built from the same map
# the rest of the app matches on, so a console this app does not know is one
# that simply never appears here.
BY_ID = {number: name for name, number in retro.CONSOLES.items()}


def _fetch(key: str, who: str) -> list[dict] | None:
    """Every game on the list, or None if it could not be had."""
    rows: list[dict] = []
    offset = 0
    for _ in range(PAGES):
        asked = urllib.parse.urlencode({"u": who, "y": key,
                                        "c": PAGE, "o": offset})
        request = urllib.request.Request(f"{API}?{asked}",
                                         headers={"User-Agent": retro.USER_AGENT})
        try:
            page = json.loads(
                rapi.read(request, timeout=30).decode("utf-8", "replace"))
        except urllib.error.HTTPError as exc:
            if exc.code in (401, 403):
                return None
            return rows or None
        except Exception:  # noqa: BLE001 - offline, timeout, nonsense JSON
            return rows or None
        if not isinstance(page, dict):
            return rows or None

        got = page.get("Results") or page.get("results") or []
        if not isinstance(got, list) or not got:
            break
        rows.extend(one for one in got if isinstance(one, dict))
        offset += len(got)
        try:
            if offset >= int(page.get("Total") or page.get("total") or 0):
                break
        except (TypeError, ValueError):
            break
    return rows


def _kind(title: str) -> str:
    """"patch" for a hack or a translation, "" for an ordinary release."""
    low = title.lower()
    if any(tag in low for tag in _PATCHED) or "[subset" in low:
        return "patch"
    return ""


# The folded title map, kept between calls. Building it is a pass over every
# distinct title on a console - thirty-odd thousand of them across a typical
# want-to-play list, about half a second - and it was being rebuilt from
# scratch every time the window was opened and again for every failed
# compatibility check.
#
# Held against the number of files the console has indexed, which is what
# changes when the index is rebuilt or a source is added. A rebuild landing on
# exactly the same count would go unnoticed; the cost of that is a title map
# one reindex out of date, which is a worse answer than none for nobody.
_folds: dict[str, tuple[int, dict[str, str]]] = {}
_folds_lock = threading.Lock()


def _fold_one(conn, console: str) -> dict[str, str]:
    """{folded title: the index's own title_norm} for one console."""
    try:
        count = conn.execute("SELECT COUNT(*) FROM files WHERE console = ?",
                             (console,)).fetchone()[0]
    except Exception:  # noqa: BLE001 - an index still being built
        return {}

    with _folds_lock:
        known = _folds.get(console)
        if known and known[0] == count:
            return known[1]

    found: dict[str, str] = {}
    try:
        rows = conn.execute(
            "SELECT DISTINCT title, title_norm FROM files WHERE console = ?",
            (console,))
    except Exception:  # noqa: BLE001
        return found
    for title, norm in rows:
        for candidate in retro.match_keys(str(title or "")):
            found.setdefault(candidate, norm)

    with _folds_lock:
        _folds[console] = (count, found)
    return found


def _folded(conn, consoles: set[str]) -> dict[str, dict[str, str]]:
    """{console: {folded title: the index's own title_norm}}.

    Every spelling of each title is written in, so a lookup is a dictionary
    hit whichever form the title arrives in.
    """
    return {console: _fold_one(conn, console) for console in consoles}


def _copies(conn, console: str, norms: set[str]) -> dict[str, list[dict]]:
    """Every copy of each of these games, best first, as {title_norm: files}.

    No new opinion about which dump is best. The ordering is the one db.search
    uses for a search - the regions chosen in Settings first - so the copy
    offered here is the copy that would have been at the top of the list had
    the same game been searched for by hand.

    One query per console rather than one per game: a want-to-play list is
    dozens of titles and they mostly share a handful of machines.
    """
    if not norms:
        return {}
    placeholders = ",".join("?" * len(norms))
    # A demo sorts below a finished game however well its region matches: the
    # region is a preference, and a demo is the wrong game.
    # Matched on the front of the tag rather than the whole of it: they are
    # numbered - 'Demo 1', 'Demo 2', 'Beta 3' - and asking for exactly 'Demo'
    # found none of them, which is how a demo came to be offered as the game.
    junk = " + ".join(
        f"(CASE WHEN ('|' || f.tags || '|') LIKE '%|{tag}%' THEN 1 ELSE 0 END)"
        for tag in _JUNK_TAGS)
    query = f"""
        SELECT {db.FILE_COLUMNS}
        FROM files f
        JOIN sources s ON s.id = f.source_id
        WHERE f.console = ? AND f.title_norm IN ({placeholders})
        ORDER BY ({junk}), {db.region_rank_sql()}, f.disc, f.filename
    """
    out: dict[str, list[dict]] = {}
    try:
        rows = conn.execute(query, [console, *norms])
    except Exception:  # noqa: BLE001 - an index still being built
        return out
    for row in rows:
        item = dict(row)
        item["regions"] = [r for r in (row["regions"] or "").split(",") if r]
        item["languages"] = [l for l in (row["languages"] or "").split(",") if l]
        item["tags"] = [t for t in (row["tags"] or "").split("|") if t]
        # Best first, since that is the order they arrive in: whoever wants
        # one copy takes the head of the list and whoever wants to choose
        # between them has them already sorted.
        out.setdefault(row["title_norm"], []).append(item)
    return out


# -- a copy that would have worked -----------------------------------------
# The other half of retro.verify(). Being told that the file on the disk is
# not one the set accepts is only half an answer; the other half is which file
# would have been, and this app is the thing that can fetch it.
#
# Matched on the dump's name and nothing looser. retro._file_key folds case
# and spacing and takes the extension off - the two sides wrap the same dump
# differently, one as .md and one inside a .zip - and leaves everything that
# tells two dumps apart exactly as it is. The region, the revision, the disc
# and the language list all still have to agree, because this is the
# difference between handing somebody the copy that works and handing them the
# European one.


def replacement(conn, console: str, name: str, game: int) -> dict:
    """Copies in the index that this game's set really is dumped from."""
    listed = retro.hashes(int(game or 0))
    if not listed:
        return {"ok": False, "reason": "nohashes"}

    # Dumps whose "file" is an original plus a patch are left out: there is
    # nothing to download that would be one, and offering it as a fix would
    # send somebody to a file that fails the same check on arrival.
    accepted = {retro._file_key(row["name"]): row  # noqa: SLF001 - same package
                for row in listed if row.get("name") and not row.get("patch")}
    if not accepted:
        return {"ok": False, "reason": "nohashes"}

    table = (_folded(conn, {console}) or {}).get(console) or {}
    norm = ""
    for candidate in retro.match_keys(name):
        norm = table.get(candidate) or ""
        if norm:
            break
    if not norm:
        return {"ok": False, "reason": "none"}

    out = []
    for one in _copies(conn, console, {norm}).get(norm, []):
        hit = accepted.get(retro._file_key(one["filename"]))  # noqa: SLF001
        if hit:
            out.append({**one, "matched": hit["name"],
                        "labels": hit.get("labels") or []})
    if not out:
        return {"ok": False, "reason": "none", "listed": len(accepted)}
    return {"ok": True, "files": out, "listed": len(accepted)}


# -- what each set is worth ------------------------------------------------
# The want-to-play list carries how many achievements a set has and what it
# scores, but not its RetroPoints or the ratio between the two - and that
# ratio is the one figure that says how hard a set is. Those come from the
# per-game endpoint, one request each, which is why they are not fetched with
# the list: seventy-eight games would be seventy-eight requests before the
# window could open.
#
# So the list opens with what it has and this fills the rest in behind it, a
# budget at a time, the page coming back for more until there is no more. Once
# fetched they are held for a fortnight by retro.how_long, so a second visit
# costs nothing at all.
WORTH_BUDGET = 25


def worth(games) -> dict:
    """{game id: {points, retropoints, ratio}} for as many as can be had now."""
    wanted: list[int] = []
    for one in games if isinstance(games, list) else []:
        try:
            found = int(one)
        except (TypeError, ValueError):
            continue
        if found and found not in wanted:
            wanted.append(found)

    out: dict[str, dict] = {}
    spent = 0
    remaining = 0
    for game in wanted:
        known = retro.priced(game)
        if not known and spent >= WORTH_BUDGET:
            remaining += 1
            continue
        if not known:
            spent += 1
        try:
            row = retro.how_long("", "", game)
        except Exception:  # noqa: BLE001 - a figure short is not a failure
            continue
        if not row.get("ok"):
            # "No set" is settled; anything else is worth another go later.
            if row.get("reason") not in ("noset", "nokey"):
                remaining += 1
            continue
        out[str(game)] = {"points": row.get("points") or 0,
                          "retropoints": row.get("retropoints") or 0,
                          "ratio": row.get("ratio") or 0,
                          "players": row.get("players") or 0}
    return {"ok": True, "worth": out, "remaining": remaining}


def listing(conn, refresh: bool = False) -> dict:
    """The want-to-play list, each game with what can be done about it."""
    global _cache  # noqa: PLW0603
    from . import artwork  # noqa: PLC0415 - only this needs the credentials

    conf = artwork.settings()["retroachievements"]
    key, who = conf.get("api_key") or "", conf.get("username") or ""
    if not key or not who:
        return {"ok": False, "reason": "nouser"}

    with _lock:
        if _cache and not refresh and time.time() - _cache[0] < LIFE:
            rows = _cache[1]
        else:
            rows = None
    if rows is None:
        rows = _fetch(key, who)
        if rows is None:
            return {"ok": False, "reason": "unreachable"}
        with _lock:
            _cache = (time.time(), rows)

    wanted = []
    for row in rows:
        console = BY_ID.get(retro._number(row, "consoleID", "ConsoleID") or 0)  # noqa: SLF001
        title = retro._text(row, "title")  # noqa: SLF001
        game = retro._number(row, "id", "ID")  # noqa: SLF001
        if not title:
            continue
        icon = retro._text(row, "imageIcon")  # noqa: SLF001
        wanted.append({
            "id": game or 0,
            "title": title,
            # Empty for a console RetroAchievements has and this app does not
            # index - the row is still shown, since it is still on their list.
            "console": console or "",
            "consoleName": retro._text(row, "consoleName") or console or "",  # noqa: SLF001
            "points": retro._number(row, "pointsTotal") or 0,  # noqa: SLF001
            "achievements": retro._number(row, "achievementsPublished") or 0,  # noqa: SLF001
            "icon": f"{retro.MEDIA}{icon}" if icon.startswith("/") else "",
            "url": retro.GAME_URL.format(id=game) if game else "",
            "state": _kind(title) or "none",
            "norm": "",
            "file": None,
        })

    folded = _folded(conn, {one["console"] for one in wanted if one["console"]})
    for one in wanted:
        if one["state"] == "patch" or not one["console"]:
            continue
        table = folded.get(one["console"]) or {}
        for candidate in retro.match_keys(one["title"]):
            norm = table.get(candidate)
            if norm:
                one["norm"] = norm
                one["state"] = "get"
                break

    # The copy to queue for each one that has a match, gathered a console at a
    # time. A game the index named but has no file for goes back to "none" -
    # offering a download that cannot start is worse than saying there isn't
    # one.
    by_console: dict[str, set[str]] = {}
    for one in wanted:
        if one["state"] == "get":
            by_console.setdefault(one["console"], set()).add(one["norm"])
    files = {console: _copies(conn, console, norms)
             for console, norms in by_console.items()}
    for one in wanted:
        if one["state"] != "get":
            continue
        copies = (files.get(one["console"]) or {}).get(one["norm"]) or []
        one["file"] = copies[0] if copies else None
        if not one["file"]:
            one["state"] = "none"

    counts: dict[str, int] = {}
    for one in wanted:
        counts[one["state"]] = counts.get(one["state"], 0) + 1
    return {"ok": True, "user": who, "games": wanted,
            "total": len(wanted), "counts": counts}
