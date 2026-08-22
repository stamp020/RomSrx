"""Signing the emulators in to RetroAchievements, without asking for anything.

Somebody with five emulators installed has to sign in to RetroAchievements
five times, in five different menus, and the app watches them do it while
already knowing who they are. That is the whole problem this solves - and how
it solves it matters more than that it does.

**Nothing is asked for and nothing new is stored.** The obvious way to do this
would be to take the RetroAchievements password, hand it to `dorequest.php?r=
login2`, and write the token that comes back into every emulator. That works,
and it means this app handling an account password - which it has never done
and does not need to, because the token it would be fetching is already
sitting on this machine. Any emulator that has been signed in once has it, and
the token is the *account's*, not that emulator's: every rcheevos-based
emulator accepts the same one.

So this reads the login out of an emulator that already has it and writes it
into the ones that do not. The first sign-in is still done by hand, in
whichever emulator the user prefers; the other four stop being work.

What it will not do
-------------------

**It never invents a config file.** Every emulator here keeps its settings in
its own format, and this app is a guest in all of them. Writing a file for an
emulator that has never run means guessing at a format with nothing to check
the guess against - so an emulator that has not been started yet is reported
as "run it once first" rather than written to.

**It never writes into a file it does not recognise.** Each entry below names
the section its emulator keeps this in. If the file is there and the section
is not, the format is not the one this expects and it is left alone. That is
the check that keeps a wrong guess from becoming a wrong write: the file has
to agree it is the file we think it is.

**It never touches a password field**, only the token. RetroArch has both, and
a `cheevos_password` left over from an older setup is somebody's actual
account password sitting in a text file - copying that to four more text files
would be making a bad situation four times worse.

**It leaves what it does not understand exactly as it was.** These files hold
hundreds of settings that took someone an evening to get right. Every write
here is a line replaced or a line added, on a copy, renamed into place when it
is complete - never a file regenerated from what this module happens to know
about.

Which emulators, and the honest answer about how many
-----------------------------------------------------

Fewer than the five below, and the reason is worth knowing before reading the
table as a promise.

Checking real config files rather than trusting the format turned up something
that changes the shape of this: **PCSX2 and PPSSPP no longer keep the token in
their settings file at all.** Both write the username there and nothing else -
PCSX2's `[Achievements]` runs `Username`, `LoginTimestamp`, and stops - because
the token now lives in the operating system's credential store, which is the
right place for it and is not a text file this can edit. DuckStation, which
shares most of its code with PCSX2, still has both in the ini. RetroArch has
both in `retroarch.cfg`.

So the emulators this can actually sign in are the ones whose file still holds
a token, and that is discovered per machine rather than declared here: `read`
reports whether the key exists, and one that does not is reported as "keeps
its login elsewhere" rather than failed. As emulators move their tokens into
credential stores this feature will quietly cover fewer of them, and it will
say so instead of appearing to work.

The five below are the ones whose file layout is pinned down. The rest of the
RetroAchievements list - melonDS, Flycast, mGBA, Snes9x, Mesen - are absent
for one reason: this cannot confirm what they call these settings, and a wrong
key name is a junk line written into somebody's config. Better to leave them
out than guess.
"""

from __future__ import annotations

import os
import re
import tempfile
from pathlib import Path

from . import playtime


class CredError(Exception):
    """Something went wrong that is worth putting in front of the user."""


# Where each emulator keeps the two settings.
#
# `section` is the check as much as the destination: a file without it is not
# the file this expects, and is left alone. RetroArch has no sections at all -
# `retroarch.cfg` is a flat list of `key = "value"` - so its check is that one
# of the keys is already there.
#
# `enable` is the switch that has to be on for any of it to matter. Set only
# when this writes a login in, and only if the file already has the setting.
LAYOUT: dict[str, dict] = {
    "RetroArch": {
        "style": "flat",
        "section": "",
        "user": "cheevos_username",
        "token": "cheevos_token",
        "enable": "cheevos_enable",
        "on": "true",
    },
    "PCSX2": {
        "style": "ini",
        "section": "Achievements",
        "user": "Username",
        "token": "Token",
        "enable": "Enabled",
        "on": "true",
    },
    "DuckStation": {
        "style": "ini",
        "section": "Cheevos",
        "user": "Username",
        "token": "Token",
        "enable": "Enabled",
        "on": "true",
    },
    "Dolphin": {
        "style": "ini",
        "section": "Achievements",
        "user": "Username",
        "token": "ApiToken",
        "enable": "Enabled",
        "on": "True",
    },
    "PPSSPP": {
        "style": "ini",
        "section": "Achievements",
        "user": "AchievementsUserName",
        "token": "AchievementsToken",
        "enable": "AchievementsEnable",
        "on": "True",
    },
}


# -- finding the files ------------------------------------------------------

def _documents() -> Path:
    return playtime._documents()  # noqa: SLF001 - one definition of this


def _settings() -> dict:
    # Imported here rather than at the top: downloads pulls in most of the
    # app, and this module is also imported by the tests on its own.
    from . import downloads  # noqa: PLC0415

    return downloads.load_settings()


def _home() -> Path:
    # Through a function rather than called where it is used, so a test can
    # point the profile locations somewhere that is not the tester's own.
    return Path.home()


def _exes(settings: dict | None = None) -> dict[str, Path]:
    """The emulator programs this app has been pointed at, by name.

    Read from the app's own settings rather than by searching the disk: these
    are the ones the user actually plays with, and an emulator they have not
    configured here is not one they are waiting to be signed in to.
    """
    settings = _settings() if settings is None else settings
    found: dict[str, Path] = {}
    for path in (settings.get("emulators") or {}).values():
        if not path:
            continue
        exe = Path(str(path))
        stem = exe.stem.lower()
        for name in LAYOUT:
            # "pcsx2-qt", "duckstation-qt-x64-ReleaseLTCG", "PPSSPPWindows64"
            if stem.startswith(name.lower()) or name.lower() in stem:
                found.setdefault(name, exe)
                break
    return found


def _candidates(name: str, exe: Path | None) -> list[Path]:
    """Every place this emulator's settings file could be, portable first.

    Portable first because a portable install is a deliberate choice - someone
    who unpacked RetroArch onto D: and plays it from there is not also keeping
    a config in their profile that matters.
    """
    docs, home = _documents(), _home()
    beside = exe.parent if exe else None
    spots: list[Path] = []

    if name == "RetroArch":
        if beside:
            spots.append(beside / "retroarch.cfg")
        appdata = os.environ.get("APPDATA")
        if appdata:
            spots.append(Path(appdata) / "RetroArch" / "retroarch.cfg")
        spots.append(home / ".config" / "retroarch" / "retroarch.cfg")
    elif name == "PCSX2":
        if beside:
            spots.append(beside / "inis" / "PCSX2.ini")
        spots.append(docs / "PCSX2" / "inis" / "PCSX2.ini")
        spots.append(home / ".config" / "PCSX2" / "inis" / "PCSX2.ini")
    elif name == "DuckStation":
        if beside:
            spots.append(beside / "settings.ini")
        spots.append(docs / "DuckStation" / "settings.ini")
        spots.append(home / ".local" / "share" / "duckstation" / "settings.ini")
    elif name == "Dolphin":
        if beside:
            spots.append(beside / "User" / "Config" / "RetroAchievements.ini")
        spots.append(docs / "Dolphin Emulator" / "Config"
                     / "RetroAchievements.ini")
        spots.append(home / ".config" / "dolphin-emu" / "RetroAchievements.ini")
    elif name == "PPSSPP":
        if beside:
            spots.append(beside / "memstick" / "PSP" / "SYSTEM" / "ppsspp.ini")
        spots.append(docs / "PPSSPP" / "PSP" / "SYSTEM" / "ppsspp.ini")
        spots.append(home / ".config" / "ppsspp" / "PSP" / "SYSTEM"
                     / "ppsspp.ini")
    return spots


def _settings_file(name: str, exe: Path | None) -> Path | None:
    for spot in _candidates(name, exe):
        try:
            if spot.is_file():
                return spot
        except OSError:
            continue
    return None


# -- reading and writing ----------------------------------------------------

def _text(path: Path) -> str:
    """The file as it is on disk, line endings and all.

    Deliberately not `read_text`, which translates CRLF to LF on the way in.
    That is almost always what you want and here it is the one thing that
    must not happen: the endings are how this decides what to write back, and
    normalising them first would rewrite every line of a Qt-written config to
    say the file had been changed throughout.

    These files belong to programs ranging from Qt to a hand-rolled writer, so
    one odd byte is not a reason to give up on the other nine hundred lines.
    """
    with open(path, encoding="utf-8", errors="replace", newline="") as handle:
        return handle.read()


# Horizontal whitespace, never a line ending.
#
# Every setting here is empty far more often than it is not - an emulator that
# has never been signed in writes `Username = ` with nothing after it - and
# `\s` matches newlines. So the value pattern ran straight on to the next line
# and came back holding the name of the setting below it, which read as a
# username, which made an emulator with no login look like one that had one.
SPACE = r"[^\S\n]"


def _value(text: str, key: str) -> str:
    """What `key` is set to, or "" whether it is blank or absent."""
    found = re.search(
        rf'^{SPACE}*{re.escape(key)}{SPACE}*={SPACE}*(.*?){SPACE}*$',
        text, re.M)
    return found.group(1).strip().strip('"') if found else ""


def _flat_get(text: str, key: str) -> str:
    return _value(text, key)


def _ini_get(text: str, section: str, key: str) -> str:
    body = _section_body(text, section)
    return "" if body is None else _value(body, key)


def _section_body(text: str, section: str) -> str | None:
    """The lines inside `[section]`, or None if the file has no such section.

    None and "" mean different things here and the caller depends on it: a
    section that is absent means this is not the file we think it is, and an
    empty one means it is, and has nothing set yet.
    """
    start = re.search(rf'^\s*\[{re.escape(section)}\]\s*$', text, re.M | re.I)
    if not start:
        return None
    rest = text[start.end():]
    nxt = re.search(r'^\s*\[[^\]]+\]\s*$', rest, re.M)
    return rest[:nxt.start()] if nxt else rest


def _has_key(body: str, key: str) -> bool:
    return bool(re.search(rf'^{SPACE}*{re.escape(key)}{SPACE}*=', body, re.M))


def read(name: str, path: Path) -> dict:
    """What this emulator's settings file holds, if it is one we know.

    `has_token` is separate from `token` and matters more. Two of these
    emulators write the username into the file and keep the token somewhere
    else entirely - see KEEPS_TOKEN_ELSEWHERE - and from the outside that is
    indistinguishable from a token that is simply blank. The difference is
    whether the key is there at all.
    """
    how = LAYOUT[name]
    text = _text(path)
    if how["style"] == "flat":
        # No sections to check against, so the check is the key itself.
        if not _has_key(text, how["user"]):
            return {}
        return {"user": _flat_get(text, how["user"]),
                "token": _flat_get(text, how["token"]),
                "has_token": _has_key(text, how["token"])}
    body = _section_body(text, how["section"])
    if body is None:
        return {}
    return {"user": _ini_get(text, how["section"], how["user"]),
            "token": _ini_get(text, how["section"], how["token"]),
            "has_token": _has_key(body, how["token"])}


def _set_line(body: str, key: str, value: str, quoted: bool) -> tuple[str, bool]:
    """Replace `key`'s line in `body`, or report that there was none."""
    written = f'{key} = "{value}"' if quoted else f'{key} = {value}'
    pattern = re.compile(rf'^({SPACE}*){re.escape(key)}{SPACE}*=.*$', re.M)
    if not pattern.search(body):
        return body, False
    # The indent is kept: Qt writes these flush left, others do not, and a
    # diff of this file should show one changed value and nothing else.
    return pattern.sub(lambda m: m.group(1) + written, body, count=1), True


def _write_atomically(path: Path, text: str, newline: str) -> None:
    """Renamed into place, so a crash cannot leave a half-written config.

    This file is the emulator's, and the failure being avoided is not losing
    our two lines - it is truncating hundreds of somebody else's.
    """
    with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", newline="", delete=False,
            dir=str(path.parent), prefix=path.name + ".", suffix=".new") as tmp:
        tmp.write(text)
        spare = Path(tmp.name)
    try:
        os.replace(spare, path)
    except OSError:
        spare.unlink(missing_ok=True)
        raise


def put(name: str, path: Path, user: str, token: str) -> dict:
    """Write the login into this emulator's settings file.

    Only into keys that are already there. A key this expects and does not
    find means the format has moved on, and adding it would be inventing a
    setting rather than filling one in.
    """
    how = LAYOUT[name]
    text = _text(path)
    newline = "\r\n" if "\r\n" in text else "\n"
    flat = how["style"] == "flat"
    body = text if flat else _section_body(text, how["section"])
    if body is None:
        raise CredError(f"{name}'s settings file is not the one this expects.")

    changed = body
    done = []
    for key, value in ((how["user"], user), (how["token"], token)):
        changed, wrote = _set_line(changed, key, value, quoted=flat)
        if not wrote:
            raise CredError(
                f"{name} does not have a {key!r} setting to fill in. "
                "Sign in to it once by hand and this can take it from there.")
        done.append(key)

    # Only after the two that matter, and only if it is already there - an
    # emulator with achievements deliberately off should stay that way until
    # it has a login, but having given it one, leaving it switched off would
    # make this button look like it did nothing.
    changed, switched = _set_line(changed, how["enable"], how["on"],
                                  quoted=flat)

    if flat:
        whole = changed
    else:
        start = re.search(rf'^\s*\[{re.escape(how["section"])}\]\s*$',
                          text, re.M | re.I)
        whole = text[:start.end()] + changed + text[start.end() + len(body):]

    if whole == text:
        return {"emulator": name, "path": str(path), "written": [],
                "already": True}
    _write_atomically(path, whole, newline)
    return {"emulator": name, "path": str(path), "written": done,
            "enabled": bool(switched), "already": False}


# -- what the page asks for -------------------------------------------------

def look(settings: dict | None = None) -> dict:
    """Who is signed in where, and who could be.

    Answers `{signed_in, from, ready, blocked}`. `from` is the emulator the
    login would be copied out of; `ready` are the ones it would go into;
    `blocked` are the ones that cannot be, each with the reason - which is
    almost always "this has never been run".
    """
    settings = _settings() if settings is None else settings
    exes = _exes(settings)
    have, ready, blocked = [], [], []

    for name in LAYOUT:
        exe = exes.get(name)
        path = _settings_file(name, exe)
        if path is None:
            if exe is not None:
                blocked.append({"emulator": name, "why": "not run yet"})
            continue
        try:
            found = read(name, path)
        except OSError as exc:
            blocked.append({"emulator": name, "why": f"unreadable: {exc}"})
            continue
        if not found:
            blocked.append({"emulator": name, "why": "unfamiliar settings file"})
            continue
        if not found.get("has_token"):
            # See KEEPS_TOKEN_ELSEWHERE. Told apart from the other refusals
            # because it is the only permanent one: the others are "not yet"
            # and this one is "not ever, by this route".
            blocked.append({"emulator": name, "why": "token not in this file"})
            continue
        if found.get("user") and found.get("token"):
            have.append({"emulator": name, "path": str(path),
                         "user": found["user"], "token": found["token"]})
        else:
            ready.append({"emulator": name, "path": str(path),
                          "user": found.get("user") or ""})

    # Any of them will do - they all hold the same account token - so the
    # first is the first in LAYOUT, which is a stable answer rather than
    # whichever the filesystem happened to list first.
    source = have[0] if have else None
    return {
        "signed_in": bool(source),
        "user": source["user"] if source else "",
        "from": source["emulator"] if source else "",
        # Ones that already have it are worth showing as done rather than
        # hidden, so the list adds up to the emulators the user has.
        "done": [one["emulator"] for one in have[1:]],
        "ready": [{"emulator": one["emulator"], "path": one["path"]}
                  for one in ready],
        "blocked": blocked,
    }


def apply(settings: dict | None = None, only: list[str] | None = None) -> dict:
    """Copy the login into the emulators that do not have it.

    `only` narrows it to particular emulators; without it, all of them.
    """
    settings = _settings() if settings is None else settings
    exes = _exes(settings)
    state_now = look(settings)
    if not state_now["signed_in"]:
        raise CredError(
            "None of your emulators is signed in to RetroAchievements yet. "
            "Sign in to one of them and this can copy it to the rest.")

    source = None
    for name in LAYOUT:
        path = _settings_file(name, exes.get(name))
        if path and name == state_now["from"]:
            source = read(name, path)
            break
    if not source or not source.get("token"):
        raise CredError("The login went away between looking and writing.")

    wanted = set(only or [one["emulator"] for one in state_now["ready"]])
    written, failed = [], []
    for one in state_now["ready"]:
        name = one["emulator"]
        if name not in wanted:
            continue
        try:
            written.append(put(name, Path(one["path"]),
                               source["user"], source["token"]))
        except (CredError, OSError) as exc:
            failed.append({"emulator": name, "why": str(exc)})
    return {"ok": not failed, "user": source["user"],
            "from": state_now["from"], "written": written, "failed": failed}
