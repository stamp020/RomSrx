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

from . import arcade, db, hacks, rapi, retro

API = ("https://retroachievements.org/API/API_GetUserWantToPlayList.php")
PAGE = 100                  # their maximum
PAGES = 20                  # ...so up to 2,000, which is a long list
LIFE = 10 * 60              # a list somebody edits by hand, on another device

# Their tags for a set that is not a ROM anybody can download: a hack and a
# translation are a patch applied over a ROM, and a subset is a second board
# of achievements for a game that already has its own page.
#
# Homebrew, unlicensed, prototype and demo used to be on this list, and that
# was wrong. Those are ordinary standalone dumps - MiNERVA keeps a shelf per
# console for exactly them - and treating them as patches discarded 1,199
# sets before anything went looking. See _kind.
_PATCHED = ("~hack~", "~translation~")

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
    """"patch" for a set no download can satisfy, "" for one a dump can.

    The question is not whether the release is unusual, it is whether there
    is a file to fetch. A homebrew has its own ROM; a hack is a diff against
    somebody else's, and the diff is what the set wants.
    """
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


# The tags in _JUNK_TAGS mean "this is not the finished game", and for almost
# every set that is a reason to offer something else. For a handful it is the
# whole point: RetroAchievements carries sets built from prototypes and from
# demos, and for those the copy everything else avoids is the only one that
# works. Left alone, the picker offered the retail dump for
# '~Prototype~ Addams Family Values' and the set would have refused it.
_WANTS_JUNK = {"~prototype~": ("Proto", "Beta", "Sample"),
               "~demo~": ("Demo", "Taikenban", "Trial", "Kiosk", "Sample")}


def wants_unfinished(title: str) -> tuple[str, ...]:
    """The tags a set actually asks for, when it asks for an unfinished copy."""
    low = str(title or "").lower()
    out: list[str] = []
    for tag, marks in _WANTS_JUNK.items():
        if tag in low:
            out.extend(m for m in marks if m not in out)
    return tuple(out)


def _copies(conn, console: str, norms: set[str],
            unfinished: dict[str, tuple[str, ...]] | None = None
            ) -> dict[str, list[dict]]:
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

    # For the few games whose set was built from an unfinished copy, the same
    # sum is turned upside down: the tag that would have sent a dump to the
    # bottom is what brings it to the top. Done inside the one query, per
    # title, so a want-to-play list holding both kinds is still one trip.
    turned = {n: marks for n, marks in (unfinished or {}).items()
              if n in norms and marks}
    order = f"({junk})"
    if turned:
        cases = []
        for norm, marks in turned.items():
            hit = " OR ".join(
                f"('|' || f.tags || '|') LIKE '%|{mark}%'" for mark in marks)
            cases.append((norm, hit))
        whens = " ".join(
            f"WHEN f.title_norm = ? AND ({hit}) THEN -1" for _n, hit in cases)
        order = f"(CASE {whens} ELSE ({junk}) END)"

    query = f"""
        SELECT {db.FILE_COLUMNS}
        FROM files f
        JOIN sources s ON s.id = f.source_id
        WHERE f.console = ? AND f.title_norm IN ({placeholders})
        ORDER BY {order}, {db.region_rank_sql()}, f.disc, f.filename
    """
    out: dict[str, list[dict]] = {}
    try:
        # SQLite numbers "?" by where it appears in the text, and ORDER BY is
        # written after WHERE - so the CASE arms bind last, not first. Getting
        # this backwards raised inside the except below and returned nothing,
        # which reads exactly like "this game has no copies".
        rows = conn.execute(query, [console, *norms,
                                    *[n for n, _h in
                                      (cases if turned else [])]])
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


# -- the shortest sets on the whole site -----------------------------------
# Ordering a *page* of search results by how many achievements each has was
# never what was wanted: it answers "which of these forty is shortest", not
# "which are the shortest games there are". The difference matters, because
# the second is a way to find a game you had not thought of and the first is
# only a tidier version of what you already typed.
#
# It is answerable, and only because set sizes come in bulk: one request per
# console returns every game that has a set with its achievement count, so
# the whole catalogue can be put in order without a request per game. A time
# could never be ordered this way - that really is one request each.
#
# Narrowed to what can actually be downloaded, since a suggestion nobody can
# fetch is a magazine article: every candidate is matched against the index by
# the same folding the want-to-play list uses.
SHORTEST_MIN = 1        # a "set" of nothing is not a short game


def indexed_sets(conn, console: str = "", allow=None) -> list[dict]:
    """Every game with an achievement set that this index can actually fetch.

    The join both site-wide rankings stand on: RetroAchievements' own list of
    games with sets, folded against the index so only downloadable games
    survive, carrying what came free with the bulk list - the set's size, what
    it scores, and when it last changed.

    `console` narrows it to one machine or to a list of them. `allow`, when
    given, is the {(console, title_norm)} a search and the filter bar between
    them left standing - see db.scope_of - and nothing outside it survives.
    Without it the pool is the whole site, which is what it has always been.

    Ordering is the caller's business; this is the pool.
    """
    if isinstance(console, str):
        consoles = [console] if console else _indexed_consoles(conn)
    else:
        consoles = [c for c in (console or []) if c] or _indexed_consoles(conn)
    # Fetched once for the whole pool rather than per console: it is one
    # listing of every patch RetroAchievements publishes, and it is cached.
    published = retro.patches()

    out: list[dict] = []
    for name in consoles:
        table = retro.set_sizes(name)
        if not table:
            continue
        folded = _fold_one(conn, name)
        # Arcade has no folded titles worth having - a romset is named for the
        # board, not the game - and is matched by the name itself instead.
        # See arcade.py.
        shelf = arcade.by_hash(conn, name) if name == arcade.CONSOLE else {}
        accepted = arcade.accepted(name) if shelf else {}
        # What the file is called, which is no longer what the game is called:
        # name_files renames an indexed romset after the game it turned out to
        # be, so the board name has to be looked up separately to be shown.
        boards = arcade.boards(conn, name) if shelf else {}
        if not folded and not shelf:
            continue
        for game, row in table.items():
            title = row.get("title") or ""
            count = row.get("achievements") or 0
            if count < SHORTEST_MIN or not title:
                continue
            # A set that is a patch rather than a ROM earns its place here
            # only when there is a way to build it: RetroAchievements
            # publishes the patch and the index has the game it goes on. Then
            # it is as fetchable as anything else on the list, and the row
            # carries what it takes - see hacks.py.
            #
            # A subset never resolves, and should not: it is a second board of
            # achievements for a game that already has its own page, not a
            # game. The patch folder for one is called "Subset", which
            # hacks.NOT_A_GAME refuses, so they fall out here without needing
            # a rule of their own.
            # An arcade set is answered by name and by nothing else: the
            # hashes it accepts are hashes of romset names, and one of them
            # either is on the shelf or is not. A hack is no different there -
            # RetroAchievements ships arcade hacks as their own romsets rather
            # than as patches - so the ordinary patch question is not asked.
            if shelf:
                names = accepted.get(game) or []
                norm = arcade.match(shelf, names)
                if not norm:
                    continue
                board = arcade.match(boards, names)
                if allow is not None and (name, norm) not in allow:
                    continue
                out.append({"norm": norm, "console": name, "id": game,
                            "title": title, "achievements": count,
                            "points": row.get("points") or 0,
                            "modified": row.get("modified") or "",
                            "patch": "", "base": "",
                            # Which board this is. The card is titled from the
                            # set rather than from the file, because the file
                            # is called "dkaccel" - so the name of the romset
                            # has to be said somewhere, and this is it.
                            "romset": board})
                continue

            plan: dict = {}
            if _kind(title) == "patch":
                plan = hacks.plan(folded, game, published)
                if not plan:
                    continue
                norm = plan["norm"]
            else:
                norm = ""
                for candidate in retro.match_keys(title):
                    norm = folded.get(candidate) or ""
                    if norm:
                        break
            if not norm:
                continue            # nothing in the index to download
            if allow is not None and (name, norm) not in allow:
                continue            # outside what is being searched for
            out.append({"norm": norm, "console": name, "id": game,
                        "title": title, "achievements": count,
                        "points": row.get("points") or 0,
                        "modified": row.get("modified") or "",
                        # Empty for an ordinary game; for a hack, the patch to
                        # apply and the game the download will actually be.
                        "patch": plan.get("patch", ""),
                        "base": plan.get("base", ""),
                        "romset": ""})
    return _one_per_set(out)


def _one_per_set(rows: list[dict]) -> list[dict]:
    """One row per achievement set, however many shelves could fetch it.

    RetroAchievements has no Famicom Disk System of its own - those games are
    filed under the NES and share its list - so this asks for the same list
    twice, and any game sitting on both shelves came back twice. Thirty-seven
    did, which is why Balloon Fight appeared twice in "quickest to beat".

    The shelf that borrows the list loses the tie, so the copy offered is the
    one from the console the set is really filed under.
    """
    best: dict = {}
    for row in rows:
        gid = row["id"]
        first = best.get(gid)
        if first is None or (first["console"] in retro.ALIASES
                             and row["console"] not in retro.ALIASES):
            best[gid] = row
    return list(best.values())


def shortest(conn, console: str = "", limit: int = 40, offset: int = 0,
             allow=None, where: str = "", params: list | None = None) -> dict:
    """Games with the fewest achievements, across every set on the site.

    `console` narrows it to one machine, which is also the fast case: one
    console is one bulk request, where all of them is one per console the
    index carries. Everything is cached for a week afterwards.

    `allow` narrows it further, to the games the search box and the filter bar
    have left standing; `where`/`params` are the same filters again as SQL, so
    the copies listed on each card are the ones that matched rather than every
    copy of the game there is. See db.scope_of.
    """
    ranked = indexed_sets(conn, console, allow)
    ranked.sort(key=lambda r: (r["achievements"], r["title"].lower()))

    # One game can be in the index on several consoles; the shortest set wins
    # and the rest are dropped, so the list is games rather than sets.
    seen: set[str] = set()
    unique = []
    for row in ranked:
        if row["norm"] in seen:
            continue
        seen.add(row["norm"])
        unique.append(row)

    page = unique[max(0, offset):max(0, offset) + max(1, limit)]
    groups = db.groups_for(conn, [r["norm"] for r in page],
                           where=where, params=params)
    # Back into the order the sizes put them in - groups_for answers by title,
    # and the whole point of this list is its order.
    by_norm = {g["title_norm"]: g for g in groups}
    out = []
    for row in page:
        group = by_norm.get(row["norm"])
        if not group:
            continue
        group["setSize"] = {"achievements": row["achievements"],
                            "points": row["points"], "id": row["id"],
                            "console": row["console"],
                            # For a hack: the patch, and the game the download
                            # will really be before it is applied. Empty for
                            # everything else. See hacks.py.
                            "patch": row.get("patch") or "",
                            # What RetroAchievements calls the set. For a hack that is
                            # not the name of the file being fetched, and the card
                            # has to show the set rather than the game under it.
                            "title": row.get("title") or "",
                            "romset": row.get("romset") or "",
                            "base": row.get("base") or ""}
        out.append(group)

    return {"total": len(unique), "groups": out,
            "offset": offset, "limit": limit,
            "more": offset + len(page) < len(unique),
            "consoles": len({r["console"] for r in unique})}


def _indexed_consoles(conn) -> list[str]:
    """Consoles the index actually carries, so nothing is fetched for none."""
    try:
        rows = conn.execute("SELECT DISTINCT console FROM files").fetchall()
    except Exception:  # noqa: BLE001
        return []
    have = {str(r[0]) for r in rows if r[0]}
    return [c for c in retro.CONSOLES if c in have]


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
            # For a hack or a translation: the patch, and the game it is a
            # diff against. Filled in below when both can be found.
            "patch": "",
            "base": "",
        })

    folded = _folded(conn, {one["console"] for one in wanted if one["console"]})

    # A hack is a diff against a game somebody does host, and both halves are
    # reachable: RetroAchievements publishes the patch, the index has the base
    # ROM. Where the two can be found, the row stops saying "you will have to
    # patch this yourself" and offers the download that becomes it. Where they
    # cannot, it says what it always said. See hacks.py.
    published = retro.patches()
    for one in wanted:
        if one["state"] != "patch" or not one["console"]:
            continue
        made = hacks.plan(folded.get(one["console"]) or {},
                          one["id"], published)
        if made:
            one["patch"] = made["patch"]
            one["base"] = made["base"]
            one["norm"] = made["norm"]
            one["state"] = "get"

    # The same for a want-to-play row on the arcade shelf, and before the
    # ordinary title match rather than after it: "Donkey Kong Accelerate" has
    # no spelling that reaches "dkaccel.zip", and letting the ladder try would
    # only give it the chance to reach some other game that happens to fold
    # the same way.
    shelf = arcade.by_hash(conn, arcade.CONSOLE)
    if shelf:
        accepted = arcade.accepted(arcade.CONSOLE)
        for one in wanted:
            if one["console"] != arcade.CONSOLE or one["state"] == "get":
                continue
            norm = arcade.match(shelf, accepted.get(one["id"]) or [])
            if norm:
                one["norm"] = norm
                one["state"] = "get"
                one["patch"] = ""
                one["base"] = ""

    for one in wanted:
        if one["state"] != "none" or not one["console"]:
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
    # Which of these rows is a set built from a prototype or a demo, so the
    # picker can reach for the copy it would otherwise have skipped.
    unfinished = {one["norm"]: wants_unfinished(one["title"])
                  for one in wanted
                  if one["state"] == "get" and wants_unfinished(one["title"])}
    files = {console: _copies(conn, console, norms, unfinished)
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
