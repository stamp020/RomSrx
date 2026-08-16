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

import json
import threading
import time
import urllib.error
import urllib.parse
import urllib.request

from . import retro

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
# So calls from this module are spaced, and a failed one is tried a second time
# after a pause. Both numbers are small; what they buy is a friend list that is
# the same list every time it is drawn.
_PACE = 0.2             # seconds between calls
_RETRY_AFTER = 1.5      # ...and before trying a failed one again
_last_call = 0.0
_pace_lock = threading.Lock()


def _wait_turn() -> None:
    global _last_call  # noqa: PLW0603
    with _pace_lock:
        gap = time.time() - _last_call
        if gap < _PACE:
            time.sleep(_PACE - gap)
        _last_call = time.time()


def _once(url: str) -> dict | list | None:
    request = urllib.request.Request(url, headers={"User-Agent": retro.USER_AGENT})
    _wait_turn()
    try:
        with urllib.request.urlopen(request, timeout=30) as response:  # noqa: S310
            return json.loads(response.read().decode("utf-8", "replace"))
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
    }


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
            "retropoints": 0, "rank": 0,
            "mutual": bool(row.get("IsFollowingMe") or row.get("isFollowingMe")),
            "pic": "", "playing": "", "game": None,
        })
    out.sort(key=lambda r: -r["points"])

    for one in out[:FRIENDS]:
        found = _ask("API_GetUserSummary.php", key, u=one["user"], g=1, a=0)
        if not isinstance(found, dict):
            # Still listed, with what the list itself said. A person who
            # vanishes because one request was refused is worse than a person
            # described in less detail.
            continue
        one["pic"] = _image(_str(found, "userPic"))
        one["playing"] = _str(found, "richPresenceMsg")
        one["points"] = _num(found, "totalPoints") or one["points"]
        one["retropoints"] = _num(found, "totalTruePoints")
        one["rank"] = _num(found, "rank")
        played = [r for r in (found.get("RecentlyPlayed") or [])
                  if isinstance(r, dict)]
        if played:
            game = _played(played[0])
            # The set's own icon rather than box art: it is what
            # RetroAchievements puts beside a game everywhere on its own site,
            # and at 40 pixels a piece of box art is unreadable anyway.
            one["game"] = {"id": game["id"], "url": game["url"],
                           "title": game["title"], "console": game["console"],
                           "icon": game["icon"], "seconds": 0}
            # How long they have put into it. This is the one figure that
            # costs a second request per person: it lives only on the
            # game-and-user endpoint, not on any of the summaries. Worth it
            # here because "playing X" without a duration says nothing about
            # whether they just started or have been at it for a week - and it
            # is bounded by the same cap as the list itself.
            one["game"]["seconds"] = _playtime(key, one["user"], game["id"])
    return out


def _playtime(key: str, who: str, game: int) -> int:
    """Seconds this person has spent in one game, or 0 if unknown."""
    if not game:
        return 0
    found = _ask("API_GetGameInfoAndUserProgress.php", key, u=who, g=game)
    return _num(found, "userTotalPlaytime") if isinstance(found, dict) else 0


# -- the figures a profile page is mostly made of -------------------------
# Their site prints a dozen of these and computes every one of them from two
# things: the list of every game you have touched, and the achievements you
# earned recently. Both are single requests, so all of it is arithmetic.
def _stats(key: str, who: str, mine: dict, awards: dict) -> dict:
    played = retro.progress()          # {game: {earned, hardcore, total}}
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
        # Their own RetroRatio, the same sum this app does for its owner.
        "ratio": round(_num(data, "totalTruePoints") / points, 2) if points else 0,
        "recent": games,
    }


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
    out = {
        **mine,
        "recent": [_played(r) for r in played or [] if isinstance(r, dict)],
        **awards,
        "stats": _stats(key, who, mine, awards),
        "following": _following(key),
    }
    with _full_lock:
        _full = (time.time(), out)
    return out
