"""The signed-in RetroAchievements user, as their own site would show them.

Everything else this app asks RetroAchievements is about a game. This is the
one part that is about the person: their points, their rank, what they are
playing right now, what they have mastered, and who they follow.

Two answers, because they are wanted at different moments and cost different
amounts. `me()` is the strip in the header - one request, small, asked often
enough to keep "playing X" current. `full()` is the window behind it, which
adds the awards, the recently-played list and the people they follow, and asks
for what each of those people is up to on top.

Nothing here works without a username. The API key alone answers about games;
who you are is a second field in Settings, and everything in this file is
absent until it is filled in - which is why the header shows nothing at all
rather than an empty frame for somebody who only wanted box art.
"""

from __future__ import annotations

import concurrent.futures
import json
import threading
import time
import urllib.error
import urllib.parse
import urllib.request

from . import rapi, retro

API = "https://retroachievements.org/API/"
MEDIA = "https://media.retroachievements.org"
SITE = "https://retroachievements.org"

# The header strip goes stale in a way people notice - it says what you are
# playing - so it is short. The window behind it holds a career, which does
# not change while somebody reads it.
ME_LIFE = 3 * 60
FULL_LIFE = 10 * 60

# How many of the people you follow get asked what they are doing. One request
# each, so this is the difference between a window that opens and a window
# that thinks about it. Twelve is more than most people follow.
FRIENDS = 12
RECENT = 6          # ...and how many of your own last games are listed


def _credentials() -> tuple[str, str]:
    from . import artwork  # noqa: PLC0415 - only this module needs them

    conf = artwork.settings()["retroachievements"]
    return conf.get("api_key") or "", conf.get("username") or ""


# Building this window is a dozen requests in a row - the list, then a summary
# and a playtime for every person on it - and RetroAchievements answers a burst
# like that by refusing some of it. Refusals landed as blank rows: no picture,
# no game, "Nothing right now" for somebody who was plainly playing something,
# and a refresh that did it again because the refresh was another burst.
#
# The spacing that fixes it now lives in rapi, in front of every call the whole
# app makes rather than only these. This module kept its own gate for a while
# and that was the bug in miniature: it waited politely for its own last
# request while the library sweep and the want-to-play list, which knew nothing
# about it, were making theirs at the same moment.
#
# What stays here is the second attempt, because it is about this module's
# tolerance rather than the site's: a profile is allowed to be a little slow
# and is not allowed to be blank.
_RETRY_AFTER = 1.5      # before trying a failed one again


def _once(url: str) -> dict | list | None:
    request = urllib.request.Request(url, headers={"User-Agent": retro.USER_AGENT})
    try:
        return json.loads(
            rapi.read(request, timeout=30).decode("utf-8", "replace"))
    except Exception:  # noqa: BLE001 - a profile is never worth an exception
        return None


def _ask(endpoint: str, key: str, **params) -> dict | list | None:
    params["y"] = key
    url = f"{API}{endpoint}?{urllib.parse.urlencode(params)}"
    found = _once(url)
    if found is not None:
        return found
    # One more go. A refusal here is nearly always the burst rather than the
    # question, and asking the same thing a second later gets an answer.
    time.sleep(_RETRY_AFTER)
    return _once(url)


def _image(path: str) -> str:
    """Their image paths are site-relative; the pictures are on the CDN."""
    path = str(path or "")
    return f"{MEDIA}{path}" if path.startswith("/") else ""


def _num(data: dict, *names) -> int:
    for name in names:
        for spelling in (name, name[0].upper() + name[1:]):
            value = data.get(spelling)
            if value not in (None, ""):
                try:
                    return int(value)
                except (TypeError, ValueError):
                    return 0
    return 0


def _str(data: dict, *names) -> str:
    for name in names:
        for spelling in (name, name[0].upper() + name[1:]):
            value = data.get(spelling)
            if value not in (None, ""):
                return str(value)
    return ""


def user_url(name: str) -> str:
    return f"{SITE}/user/{urllib.parse.quote(str(name or ''))}"


_me: tuple[float, dict] | None = None
_me_lock = threading.Lock()


def _played(row: dict) -> dict:
    """One game out of a recently-played or summary list."""
    game = _num(row, "gameID", "gameId")
    total = _num(row, "numPossibleAchievements") or _num(row, "achievementsTotal")
    return {
        "id": game,
        "title": _str(row, "title"),
        "console": _str(row, "consoleName"),
        "icon": _image(_str(row, "imageIcon")),
        "box": _image(_str(row, "imageBoxArt")),
        "url": retro.GAME_URL.format(id=game) if game else "",
        "total": total,
        "earned": _num(row, "numAchievedHardcore"),
        "earnedSoft": _num(row, "numAchieved"),
        "points": _num(row, "scoreAchievedHardcore"),
        "possible": _num(row, "possibleScore"),
        "when": _str(row, "lastPlayed"),
        # Filled in by _enrich below, when it is worth the requests.
        "seconds": 0, "award": "", "awardWhen": "",
        "setPoints": 0, "setRetro": 0, "ratio": 0,
    }


# Every one of these is a request per game, and a list of six is a list of
# twelve requests. Sequentially that is most of a minute; in a small pool it is
# a few seconds, because nearly all of it is waiting. Four at a time is gentle
# enough that the pacing gate above still keeps the burst civil.
_POOL = 4


def _enrich(key: str, who: str, games: list[dict], awards: dict) -> None:
    """Fill in the per-game figures a list of games cannot carry by itself.

    How long they played it, what the set is worth, and whether it was beaten
    or mastered and when. The first is per person and per game; the second is
    the same answer for everybody and is already cached for a fortnight by
    retro.how_long; the third is read off the awards we have.
    """
    won = {}
    for row in awards.get("awards") or []:
        game = row.get("game")
        if not game:
            continue
        # Mastery outranks a beaten award for the same game - they are both
        # there, and the higher one is what the site shows.
        if row["kind"] == "Mastery/Completion" or game not in won:
            won[game] = (row["kind"], row["when"])

    def one(game: dict) -> None:
        if not game["id"]:
            return
        kind = won.get(game["id"])
        if kind:
            game["award"] = kind[0]
            game["awardWhen"] = kind[1]
        game["seconds"] = _playtime(key, who, game["id"])
        try:
            found = retro.how_long(game["console"], game["title"], game["id"])
        except Exception:  # noqa: BLE001 - a figure short is not a failure
            found = {}
        if found.get("ok"):
            game["setPoints"] = found.get("points") or 0
            game["setRetro"] = found.get("retropoints") or 0
            game["ratio"] = found.get("ratio") or 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=_POOL) as pool:
        list(pool.map(one, games))


def me(refresh: bool = False) -> dict:
    """Who is signed in, and what they are playing. One request."""
    global _me  # noqa: PLW0603
    key, who = _credentials()
    if not key or not who:
        return {"ok": False, "reason": "nouser"}

    with _me_lock:
        if _me and not refresh and time.time() - _me[0] < ME_LIFE:
            return _me[1]

    # The summary rather than the profile: same fields, plus the rank and the
    # last game with its picture, which is the whole of the header strip.
    data = _ask("API_GetUserSummary.php", key, u=who, g=1, a=1)
    if not isinstance(data, dict) or not _str(data, "user"):
        return {"ok": False, "reason": "unreachable"}

    played = [r for r in (data.get("RecentlyPlayed") or []) if isinstance(r, dict)]
    last = _played(played[0]) if played else None
    # The summary's own per-game tally is more current than the list's, and it
    # is the one the site's header uses.
    awarded = (data.get("Awarded") or {}).get(str(last["id"])) if last else None
    if last and isinstance(awarded, dict):
        last["total"] = _num(awarded, "numPossibleAchievements") or last["total"]
        last["earned"] = _num(awarded, "numAchievedHardcore")
        last["points"] = _num(awarded, "scoreAchievedHardcore")
        last["possible"] = _num(awarded, "possibleScore")
    # What the set is worth, so the card in the header says what the cards in
    # the profile say. Cached for a fortnight, so this costs one ask a game.
    if last:
        _worth(last)

    out = {
        "ok": True,
        "user": _str(data, "user"),
        "url": user_url(_str(data, "user")),
        "pic": _image(_str(data, "userPic")),
        "points": _num(data, "totalPoints"),
        "retropoints": _num(data, "totalTruePoints"),
        "softcore": _num(data, "totalSoftcorePoints"),
        "rank": _num(data, "rank"),
        "ranked": _num(data, "totalRanked"),
        "since": _str(data, "memberSince"),
        "motto": _str(data, "motto"),
        # "Playing Stuart Little 2" - what the site puts under the avatar.
        "playing": _str(data, "richPresenceMsg"),
        "playingAt": _str(data, "richPresenceMsgDate"),
        "last": last,
    }
    with _me_lock:
        _me = (time.time(), out)
    return out


_full: tuple[float, dict] | None = None
_full_lock = threading.Lock()


def _awards(key: str, who: str) -> dict:
    data = _ask("API_GetUserAwards.php", key, u=who)
    if not isinstance(data, dict):
        return {}
    rows = []
    for row in data.get("VisibleUserAwards") or []:
        if not isinstance(row, dict):
            continue
        kind = _str(row, "awardType")
        game = _num(row, "awardData")
        # Game awards point at a game; event and site ones do not, and a link
        # to game 217 for "Collect-a-thon MaRAthon" would be a wrong answer
        # rather than a missing one.
        is_game = kind in ("Mastery/Completion", "Game Beaten")
        rows.append({
            "title": _str(row, "title"),
            "console": _str(row, "consoleName"),
            "icon": _image(_str(row, "imageIcon")),
            "kind": kind,
            "when": _str(row, "awardedAt"),
            "hardcore": _num(row, "awardDataExtra") == 1,
            # The game itself, so the page can group by it and the figures can
            # count games rather than awards.
            "game": game if is_game else 0,
            "url": retro.GAME_URL.format(id=game) if (is_game and game) else "",
        })
    # Newest first: a career reads backwards, and the awards somebody wants to
    # see are the ones they just earned.
    rows.sort(key=lambda r: r["when"], reverse=True)
    return {
        "counts": {
            "total": _num(data, "totalAwardsCount"),
            "mastery": _num(data, "masteryAwardsCount"),
            "beaten": _num(data, "beatenHardcoreAwardsCount"),
            "completion": _num(data, "completionAwardsCount"),
            "event": _num(data, "eventAwardsCount"),
            "site": _num(data, "siteAwardsCount"),
        },
        "awards": rows,
    }


def _following(key: str) -> list[dict]:
    """The people you follow, richest in points first, with what they are up to.

    The list itself carries their plain points and nothing else, so each one is
    asked about separately - which is why it is capped. One request each, and
    the summary is the one that pays: it brings the picture, both point totals,
    their rank and the game they last played with its set icon, which is
    everything a row here shows.

    Anyone who does not answer is still listed, just quietly: a friend list
    that drops people because the site was slow is worse than one that says
    less about them.
    """
    data = _ask("API_GetUsersIFollow.php", key, c=FRIENDS)
    rows = (data or {}).get("Results") if isinstance(data, dict) else None
    out = []
    for row in rows or []:
        if not isinstance(row, dict) or not _str(row, "user"):
            continue
        who = _str(row, "user")
        out.append({
            "user": who,
            "url": user_url(who),
            "points": _num(row, "points"),
            "retropoints": 0, "rank": 0, "ranked": 0, "since": "",
            "mutual": bool(row.get("IsFollowingMe") or row.get("isFollowingMe")),
            "pic": "", "playing": "", "game": None, "seen": "",
        })
    out.sort(key=lambda r: -r["points"])

    def fill(one: dict) -> None:
        found = _ask("API_GetUserSummary.php", key, u=one["user"], g=1, a=0)
        if not isinstance(found, dict):
            # Still listed, with what the list itself said. A person who
            # vanishes because one request was refused is worse than a person
            # described in less detail.
            return
        one["pic"] = _image(_str(found, "userPic"))
        one["playing"] = _str(found, "richPresenceMsg")
        one["points"] = _num(found, "totalPoints") or one["points"]
        one["retropoints"] = _num(found, "totalTruePoints")
        one["rank"] = _num(found, "rank")
        # Everything the site's own card over a name shows: where they stand
        # among ranked players, and how long they have been at it.
        one["ranked"] = _num(found, "totalRanked")
        one["since"] = _str(found, "memberSince")
        # When they were last seen. The site stamps the rich-presence line
        # with the moment the game last said anything, which is as close to
        # "last online" as the API gets - and closer than nothing, which is
        # what LastActivity returns for most people.
        one["seen"] = _str(found, "richPresenceMsgDate")
        played = [r for r in (found.get("RecentlyPlayed") or [])
                  if isinstance(r, dict)]
        if played:
            game = _played(played[0])
            # How far through it they are. The rows in a recently-played list
            # carry no tally of their own - it lives in the summary's own
            # `Awarded` map, keyed by game - which is why this read 0 of 47
            # for somebody halfway through a set.
            tally = (found.get("Awarded") or {}).get(str(game["id"]))
            if isinstance(tally, dict):
                game["total"] = (_num(tally, "numPossibleAchievements")
                                 or game["total"])
                game["earned"] = _num(tally, "numAchievedHardcore")
            # The set's own icon rather than box art: it is what
            # RetroAchievements puts beside a game everywhere on its own site,
            # and at 40 pixels a piece of box art is unreadable anyway.
            one["game"] = {"id": game["id"], "url": game["url"],
                           "title": game["title"], "console": game["console"],
                           "icon": game["icon"], "seconds": 0,
                           "earned": game["earned"], "total": game["total"],
                           "setPoints": 0, "setRetro": 0, "ratio": 0}
            _worth(one["game"])
            # How long they have put into it. This is the one figure that
            # costs a second request per person: it lives only on the
            # game-and-user endpoint, not on any of the summaries. Worth it
            # here because "playing X" without a duration says nothing about
            # whether they just started or have been at it for a week - and it
            # is bounded by the same cap as the list itself.
            one["game"]["seconds"] = _playtime(key, one["user"], game["id"])

    # In a small pool: this is a dozen requests that are almost all waiting,
    # and doing them one after another is what made this window slow to open.
    with concurrent.futures.ThreadPoolExecutor(max_workers=_POOL) as pool:
        list(pool.map(fill, out[:FRIENDS]))
    return out


def _playtime(key: str, who: str, game: int) -> int:
    """Seconds this person has spent in one game, or 0 if unknown."""
    if not game:
        return 0
    found = _ask("API_GetGameInfoAndUserProgress.php", key, u=who, g=game)
    return _num(found, "userTotalPlaytime") if isinstance(found, dict) else 0


# -- how long each game has been played, as the site counts it -------------
# playtime.py reads the logs the emulators keep, and says plainly that most of
# them keep none: Dolphin, PPSSPP, BizHawk, Flycast and every standalone RA
# build record nothing, so a game played only in those has no time at all on
# this machine.
#
# RetroAchievements has been counting all along, and counting across every
# machine rather than only this one - so its figure is the one the shelf
# leads with, and the emulator's own log is what fills in behind it for the
# games the site has nothing for. (The trade in that order: RetroArch logs
# time whether or not achievements were on, so for a game played mostly
# offline its number is the larger one and the site's is the one shown.)
#
# One request per game, which is why it is bounded three ways: only games
# RetroAchievements could have a time for are asked about, only so many at
# once, and every answer - including "no time" - is kept for a while so a
# redraw costs nothing.
PLAYTIME_LIFE = 30 * 60
PLAYTIME_MAX = 60


_playtimes: dict[int, tuple[float, int]] = {}
_playtimes_lock = threading.Lock()


def playtimes(games) -> dict:
    """{game id: seconds} for the games RetroAchievements has a time for."""
    key, who = _credentials()
    if not key or not who:
        return {"ok": False, "reason": "nouser"}

    wanted: list[int] = []
    for one in games if isinstance(games, list) else []:
        try:
            found = int(one)
        except (TypeError, ValueError):
            continue
        if found and found not in wanted:
            wanted.append(found)
    if not wanted:
        return {"ok": True, "times": {}}

    # Every game this user has ever earned anything in, which arrives as one
    # request however long the list. Anything outside it has no time worth
    # asking for, and asking anyway is how a shelf of four hundred turns into
    # four hundred requests.
    try:
        played = set(retro.progress())
    except Exception:  # noqa: BLE001 - without it, just ask about fewer
        played = set()
    if played:
        wanted = [game for game in wanted if game in played]

    now = time.time()
    out: dict[int, int] = {}
    pending: list[int] = []
    with _playtimes_lock:
        for game in wanted:
            found = _playtimes.get(game)
            if found and now - found[0] < PLAYTIME_LIFE:
                out[game] = found[1]
            else:
                pending.append(game)

    # Only so many new ones per call. A whole shelf asked about at once would
    # be a burst RetroAchievements refuses half of; the caller comes back for
    # the rest, and by then everything already answered is cached.
    ask = pending[:PLAYTIME_MAX]
    if ask:
        with concurrent.futures.ThreadPoolExecutor(max_workers=_POOL) as pool:
            found = list(pool.map(lambda g: (g, _playtime(key, who, g)), ask))
        with _playtimes_lock:
            for game, seconds in found:
                # Remembered even when it is zero, so a game the site has no
                # time for is not asked about again on every redraw.
                _playtimes[game] = (time.time(), seconds)
                out[game] = seconds

    return {"ok": True, "times": {str(g): s for g, s in out.items() if s},
            "asked": len(ask),
            # How many are still waiting behind the cap, so the caller knows
            # there is more to come rather than assuming this was all of it.
            "remaining": max(0, len(pending) - len(ask))}


def _worth(game: dict) -> None:
    """What a set is worth, added to a game in place.

    The same figures every game in a list carries, so the card over a little
    icon says what the card over a big one says. Free after the first ask:
    this is the same answer for everybody who plays it, and retro.how_long
    keeps it for a fortnight.
    """
    if not game.get("id"):
        return
    for attempt in range(2):
        try:
            found = retro.how_long(game.get("console") or "",
                                   game.get("title") or "", game["id"])
        except Exception:  # noqa: BLE001 - a figure short is not a failure
            return
        if found.get("ok"):
            game["setPoints"] = found.get("points") or 0
            game["setRetro"] = found.get("retropoints") or 0
            game["ratio"] = found.get("ratio") or 0
            return
        # A game with no set is a settled answer; anything else is the burst
        # being refused, and one more go a second later usually gets it. This
        # is why one friend's card came back with no figures at all.
        if found.get("reason") in ("noset", "nokey") or attempt:
            return
        time.sleep(_RETRY_AFTER)


# -- the figures a profile page is mostly made of -------------------------
# Their site prints a dozen of these and computes every one of them from two
# things: the list of every game you have touched, and the achievements you
# earned recently. Both are single requests, so all of it is arithmetic.
def _stats(key: str, who: str, mine: dict, awards: dict,
           progress: bool = True) -> dict:
    """The worked-out figures. `progress` is off for anybody but the owner:
    the completion list is a per-user request this app only caches for its
    own, and a friend's panel is not worth four more pages of it."""
    played = retro.progress() if progress else {}
    started = [row for row in played.values() if row.get("hardcore")]
    unlocked = sum(row.get("hardcore") or 0 for row in played.values())
    shares = [min(1.0, (row["hardcore"] / row["total"]))
              for row in started if row.get("total")]

    # Games, not awards. A game you mastered also carries a "beaten" award, so
    # adding the two counts double-counts every mastery - which is how this
    # first reported 69 games beaten out of 36 started. Counting the distinct
    # games behind the awards is the only figure that means anything.
    beaten = len({row["game"] for row in awards.get("awards") or []
                  if row.get("game")})

    now = time.time()
    recent = _ask("API_GetAchievementsEarnedBetween.php", key, u=who,
                  f=int(now - 30 * 86400), t=int(now))
    week = month = 0
    week_count = month_count = 0
    for row in recent or []:
        if not isinstance(row, dict) or not _num(row, "hardcoreMode"):
            continue          # hardcore throughout, as everywhere else here
        points = _num(row, "points")
        when = time.mktime(time.strptime(_str(row, "date")[:19],
                                         "%Y-%m-%d %H:%M:%S")) \
            if _str(row, "date") else 0
        month += points
        month_count += 1
        if when and now - when <= 7 * 86400:
            week += points
            week_count += 1

    # How long they have been at it, for the weekly average. Their own page
    # does the same sum from the same date.
    weeks = 0.0
    since = _str(mine, "since")
    if since:
        try:
            born = time.mktime(time.strptime(since[:19], "%Y-%m-%d %H:%M:%S"))
            weeks = max(1.0, (now - born) / (7 * 86400))
        except ValueError:
            weeks = 0.0

    points = mine.get("points") or 0
    return {
        "unlocked": unlocked,
        "started": len(started),
        "beaten": beaten,
        # What share of the games you have started you went on to finish. The
        # figure people quote when they talk about a backlog.
        "beatenShare": round(beaten / len(started) * 100, 1) if started else 0,
        "completion": round(sum(shares) / len(shares) * 100, 1) if shares else 0,
        "ratio": round((mine.get("retropoints") or 0) / points, 2) if points else 0,
        "week": week, "weekCount": week_count,
        "month": month, "monthCount": month_count,
        "perWeek": round(points / weeks) if weeks else 0,
    }


def user(name: str) -> dict:
    """One other person, in more detail - for a row opened out in the window.

    Asked for when somebody expands a friend rather than with the list, which
    is the difference between one request and one per person you follow. The
    summary answers all of it at once: their totals, their standing, when they
    joined and the last few games they played with how far through each they
    are.
    """
    key, _ = _credentials()
    name = str(name or "").strip()
    if not key:
        return {"ok": False, "reason": "nouser"}
    if not name:
        return {"ok": False, "reason": "noset"}

    data = _ask("API_GetUserSummary.php", key, u=name, g=RECENT, a=0)
    if not isinstance(data, dict) or not _str(data, "user"):
        return {"ok": False, "reason": "unreachable"}

    awarded = data.get("Awarded") or {}
    games = []
    for row in data.get("RecentlyPlayed") or []:
        if not isinstance(row, dict):
            continue
        game = _played(row)
        # The per-game tally lives in its own map rather than on the row.
        tally = awarded.get(str(game["id"]))
        if isinstance(tally, dict):
            game["total"] = _num(tally, "numPossibleAchievements") or game["total"]
            game["earned"] = _num(tally, "numAchievedHardcore")
            game["points"] = _num(tally, "scoreAchievedHardcore")
        games.append(game)

    points = _num(data, "totalPoints")
    # The same per-game figures the owner's own list gets, and the same two
    # numbers about the last month - so a friend's panel answers the questions
    # the owner's page does rather than a smaller set of them.
    won = _awards(key, name)
    _enrich(key, name, games, won)
    mine = {"points": points, "retropoints": _num(data, "totalTruePoints"),
            "since": _str(data, "memberSince")}
    return {
        "ok": True,
        "user": _str(data, "user"),
        "url": user_url(_str(data, "user")),
        "pic": _image(_str(data, "userPic")),
        "points": points,
        "retropoints": _num(data, "totalTruePoints"),
        "rank": _num(data, "rank"),
        "ranked": _num(data, "totalRanked"),
        "since": _str(data, "memberSince"),
        "motto": _str(data, "motto"),
        "playing": _str(data, "richPresenceMsg"),
        "seen": _str(data, "richPresenceMsgDate"),
        # Their own RetroRatio, the same sum this app does for its owner.
        "ratio": round(_num(data, "totalTruePoints") / points, 2) if points else 0,
        "counts": won.get("counts") or {},
        "stats": {**_stats(key, name, mine, won, progress=False),
                  # How many achievements they have in all. One request, and
                  # the same figure the owner's own page leads with.
                  "unlocked": _unlocked(key, name)},
        "recent": games,
    }


def _unlocked(key: str, who: str) -> int:
    """How many achievements somebody has earned, in hardcore.

    Their completion list, one page of it. Five hundred games is more than
    almost anybody has, and the alternative - walking every page for a figure
    printed in a card - is not worth the requests.
    """
    found = _ask("API_GetUserCompletionProgress.php", key, u=who, c=500, o=0)
    rows = (found or {}).get("Results") if isinstance(found, dict) else None
    return sum(_num(r, "numAwardedHardcore") for r in rows or []
               if isinstance(r, dict))


# -- who is ahead, among the people you follow ----------------------------
# All time is the points they already carry, so it costs nothing. Today and
# this week have to be counted from the achievements each of them earned in
# that window - one request per person - so this is asked for rather than
# built with the window, and kept for a few minutes once it has been.
#
# "Today" means since midnight, not "the last twenty-four hours". The two are
# only the same at midnight, and the difference is what made this disagree
# with the site: a ranking that still credits yesterday evening at ten the
# next morning is counting a day nobody else is counting. Same for the week,
# which starts on Sunday as theirs does.
#
# UTC, because that is the clock RetroAchievements resets on - a ranking that
# turned over at midnight in one time zone and not another would be a third
# answer, agreeing with nobody.
_RANK_LIFE = 5 * 60


def _window_start(window: str) -> float:
    """The moment the named window began, in UTC.

    Their day turns over at midnight UTC - one in the morning in Lisbon, which
    is where this was checked against the site - and their week turns over at
    the same moment on a Monday. An hour into a Monday, nobody has a weekly
    score yet, and a ranking that still shows last week's is counting a week
    that has ended.
    """
    now = time.gmtime()
    midnight = time.time() - (now.tm_hour * 3600 + now.tm_min * 60 + now.tm_sec)
    if window == "day":
        return midnight
    return midnight - now.tm_wday * 86400        # tm_wday: Monday is 0
_ranking: dict[str, tuple[float, list]] = {}
_ranking_lock = threading.Lock()


def ranking(window: str = "all") -> dict:
    """The people you follow, ordered by points won in that window."""
    key, who = _credentials()
    if not key or not who:
        return {"ok": False, "reason": "nouser"}
    window = window if window in ("day", "week") else "all"

    with _ranking_lock:
        found = _ranking.get(window)
        if found and time.time() - found[0] < _RANK_LIFE:
            kept, quiet = found[1]
            return {"ok": True, "window": window, "players": kept,
                    "quiet": quiet}

    # Everybody you follow, and you - a ranking you are not in is a ranking
    # that cannot answer "am I ahead of them".
    #
    # Taken from the panel rather than asked for again: that one is already
    # built and cached, and asking a second time is another dozen requests for
    # the same answer - which is how somebody ended up in here with no picture
    # and no rank, when one of those requests was refused.
    # Everything the card over a picture needs travels with them, so a row
    # here answers the same questions a row in the list above does.
    people = [{"user": one["user"], "url": one["url"], "pic": one["pic"],
               "points": one["points"], "retropoints": one["retropoints"],
               "rank": one["rank"], "ranked": one.get("ranked") or 0,
               "since": one.get("since") or "", "seen": one.get("seen") or "",
               "me": False}
              for one in (following().get("following") or [])]
    mine = me()
    if mine.get("ok"):
        people.append({"user": mine["user"], "url": mine["url"],
                       "pic": mine["pic"], "points": mine["points"],
                       "retropoints": mine["retropoints"],
                       "rank": mine["rank"], "ranked": mine.get("ranked") or 0,
                       "since": mine.get("since") or "",
                       "seen": mine.get("playingAt") or "", "me": True})

    if window == "all":
        for one in people:
            one["won"] = one["points"]
            one["wonRetro"] = one["retropoints"]
    else:
        started = _window_start(window)
        now = time.time()

        def count(one: dict) -> None:
            rows = [r for r in (_ask("API_GetAchievementsEarnedBetween.php", key,
                                     u=one["user"], f=int(started), t=int(now))
                                or [])
                    if isinstance(r, dict) and _num(r, "hardcoreMode")]
            one["won"] = sum(_num(r, "points") for r in rows)
            # The RetroPoints won in the same window. Their lifetime total
            # beside a day's points is two different questions in one row.
            one["wonRetro"] = sum(_num(r, "trueRatio") for r in rows)
            one["got"] = len(rows)

        with concurrent.futures.ThreadPoolExecutor(max_workers=_POOL) as pool:
            list(pool.map(count, people))

    people.sort(key=lambda one: -(one.get("won") or 0))

    # Over a day or a week, somebody who earned nothing is not in last place -
    # they were not playing. A dozen names at zero pushed the two or three
    # people who actually did something off the bottom of the panel, which is
    # the opposite of what a ranking is for. They are counted instead, and the
    # owner stays whatever they scored: a ranking without you in it cannot
    # answer "am I ahead of them".
    quiet = 0
    if window != "all":
        playing = [one for one in people if one.get("won") or one.get("me")]
        quiet = len(people) - len(playing)
        people = playing

    with _ranking_lock:
        _ranking[window] = (time.time(), (people, quiet))
    return {"ok": True, "window": window, "players": people, "quiet": quiet}


def user_game(name: str, game: int) -> dict:
    """One person's progress through one game's set.

    The same endpoint the playtime comes from, read for the rest of what it
    carries: every achievement in the set with the date *that person* earned
    it. So a friend's row can be opened out into the same wall of badges the
    owner's own games get - theirs in colour, the rest still locked.
    """
    key, _ = _credentials()
    name, game = str(name or "").strip(), int(game or 0)
    if not key:
        return {"ok": False, "reason": "nouser"}
    if not name or not game:
        return {"ok": False, "reason": "noset"}

    data = _ask("API_GetGameInfoAndUserProgress.php", key, u=name, g=game)
    if not isinstance(data, dict):
        return {"ok": False, "reason": "unreachable"}

    # Parsed by the module that already knows the shape of an achievement, so
    # a badge here is put together exactly as a badge anywhere else.
    rows = [a for a in (retro._one_achievement(r)  # noqa: SLF001 - same package
                        for r in retro._achievement_rows(data))  # noqa: SLF001
            if a]
    if not rows:
        return {"ok": False, "reason": "noachievements"}
    rows.sort(key=lambda a: (a["order"], a["id"]))
    return {
        "ok": True,
        "user": name,
        "id": game,
        "title": _str(data, "title"),
        "total": len(rows),
        "earned": sum(1 for a in rows if a["unlocked"]),
        "hardcore": sum(1 for a in rows if a["hardcore"]),
        "playtime": _num(data, "userTotalPlaytime"),
        "achievements": rows,
    }


# -- one panel at a time --------------------------------------------------
# The window used to wait for all of it: thirty-odd requests to
# RetroAchievements before anything appeared. Each panel can be asked for on
# its own now, so the page draws itself in the order its own blocks are
# arranged - the first one somebody sees is the first one fetched, and the
# rest arrive underneath while it is being read.
#
# Each keeps its own answer for a few minutes, so a page rearranged or
# reopened costs nothing.
_PANELS: dict[str, tuple[float, dict]] = {}
_panel_lock = threading.Lock()
_PANEL_LIFE = 10 * 60


def _panel(name: str, build, refresh: bool = False) -> dict:
    if not refresh:
        with _panel_lock:
            found = _PANELS.get(name)
            if found and time.time() - found[0] < _PANEL_LIFE:
                return found[1]
    out = build()
    with _panel_lock:
        _PANELS[name] = (time.time(), out)
    return out


def recent(refresh: bool = False) -> dict:
    """The last few games played, with what each one cost and came of it."""
    key, who = _credentials()
    if not key or not who:
        return {"ok": False, "reason": "nouser"}

    def build() -> dict:
        played = _ask("API_GetUserRecentlyPlayedGames.php", key, u=who, c=RECENT)
        games = [_played(r) for r in played or [] if isinstance(r, dict)]
        _enrich(key, who, games, awards(refresh=False))
        return {"ok": True, "user": who, "recent": games}

    return _panel("recent", build, refresh)


def awards(refresh: bool = False) -> dict:
    """Every award, and the counts behind them."""
    key, who = _credentials()
    if not key or not who:
        return {"ok": False, "reason": "nouser"}
    return _panel("awards", lambda: {"ok": True, **_awards(key, who)}, refresh)


def following(refresh: bool = False) -> dict:
    """The people followed, with what each of them is up to."""
    key, _ = _credentials()
    if not key:
        return {"ok": False, "reason": "nouser"}
    return _panel("following",
                  lambda: {"ok": True, "following": _following(key)}, refresh)


def figures(refresh: bool = False) -> dict:
    """The worked-out numbers under the headline four."""
    key, who = _credentials()
    if not key or not who:
        return {"ok": False, "reason": "nouser"}

    def build() -> dict:
        mine = me(refresh=refresh)
        if not mine.get("ok"):
            return mine
        won = awards(refresh=False)
        return {"ok": True, "stats": _stats(key, who, mine, won),
                "counts": won.get("counts") or {}}

    return _panel("figures", build, refresh)


def full(refresh: bool = False) -> dict:
    """Everything the profile window shows. Several requests; kept for a while."""
    global _full  # noqa: PLW0603
    key, who = _credentials()
    if not key or not who:
        return {"ok": False, "reason": "nouser"}

    with _full_lock:
        if _full and not refresh and time.time() - _full[0] < FULL_LIFE:
            return _full[1]

    mine = me(refresh=refresh)
    if not mine.get("ok"):
        return mine

    played = _ask("API_GetUserRecentlyPlayedGames.php", key, u=who, c=RECENT)
    awards = _awards(key, who)
    recent = [_played(r) for r in played or [] if isinstance(r, dict)]
    _enrich(key, who, recent, awards)
    out = {
        **mine,
        "recent": recent,
        **awards,
        "stats": _stats(key, who, mine, awards),
        "following": _following(key),
    }
    with _full_lock:
        _full = (time.time(), out)
    return out
