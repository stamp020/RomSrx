"""Whether a session is going to count, asked before it is spent.

Hardcore is the mode RetroAchievements ranks people on: no save states, no
rewind, no cheats. It is also a setting somebody turned on once, months ago,
in a program this app only launches - and the way you find out it was off is
finishing a game and seeing the unlocks land as softcore, where they earn no
points and no mastery.

Nothing here changes anything. It reads RetroArch's own configuration and
says what it found, because the alternative - writing the achievement
settings on somebody's behalf - is reaching into another program's
configuration to alter how their games behave, which is not this app's to do.

Only RetroArch. It is the one emulator on the RetroAchievements list that
keeps its settings in a plain file at a findable path, which is the same
reason playtime.py can read its runtime logs and no others: this reuses that
module's search entirely rather than guessing at paths of its own. An answer
about the emulator somebody actually uses is worth having; a guess about the
rest is not, so a machine with no RetroArch gets "nothing to report" instead
of a warning it cannot act on.

The token is never read. `cheevos_token` sits three lines from the settings
below and is a credential; what is wanted here is whether a name is filled
in, which `cheevos_username` answers without anything secret leaving the file.
"""

from __future__ import annotations

import os
from pathlib import Path

from . import playtime

# What is read, and nothing else. Deliberately a fixed list rather than "every
# cheevos_ line": the file also holds the token, and a function that hoovered
# up everything beginning with the right prefix would carry it out of the file
# the first time somebody added a debug dump.
WANTED = ("cheevos_enable", "cheevos_hardcore_mode_enable", "cheevos_username")


def _config_files(settings: dict) -> list[Path]:
    """Every retroarch.cfg this machine appears to have, best first.

    The same roots playtime.py looks in for the runtime logs - the emulators
    configured here, what sits beside them, the ordinary install folders, and
    the two places RetroArch keeps its own configuration.
    """
    roots = list(playtime._candidate_dirs(settings))  # noqa: SLF001 - same package
    appdata = os.environ.get("APPDATA")
    if appdata:
        roots.append(Path(appdata) / "RetroArch")
    roots.append(Path.home() / ".config" / "retroarch")

    found: list[Path] = []
    for root in roots:
        config = root / "retroarch.cfg"
        if config.is_file() and config not in found:
            found.append(config)
    return found


def _read(config: Path) -> dict[str, str]:
    """The three settings above, as they are written in the file."""
    out: dict[str, str] = {}
    try:
        with open(config, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                key, sep, value = line.partition("=")
                key = key.strip()
                if sep and key in WANTED:
                    out[key] = value.strip().strip('"').strip()
    except OSError:
        return {}
    return out


def _yes(value: str) -> bool:
    return value.strip().lower() == "true"


def status(settings: dict | None = None) -> dict:
    """What would stop the next session counting, if anything.

    Never raises and never guesses: a machine where no RetroArch can be found
    comes back with `found` false and nothing else said, which is the right
    answer for the many people who play in something else entirely.
    """
    from . import artwork, downloads  # noqa: PLC0415

    if settings is None:
        try:
            settings = downloads.load_settings()
        except Exception:  # noqa: BLE001 - a missing setting is not a failure
            settings = {}

    for config in _config_files(settings):
        found = _read(config)
        if not found:
            continue

        # Absent means RetroArch has never written it, which is its default -
        # and its default for both of these is on. Saying "off" for a setting
        # that is merely unwritten would send somebody looking for a switch
        # that is already where they want it.
        achievements = _yes(found.get("cheevos_enable", "true"))
        hardcore = _yes(found.get("cheevos_hardcore_mode_enable", "true"))
        who = found.get("cheevos_username", "")

        issues = []
        if not who:
            issues.append("nouser")
        if not achievements:
            issues.append("off")
        elif not hardcore:
            # Only worth saying when achievements are on at all: told that
            # both are off, the first is the one to fix and the second is
            # noise underneath it.
            issues.append("softcore")

        # Signed in as somebody else is worth noticing - it is how a whole
        # evening lands on an account you are not looking at.
        mine = ""
        try:
            mine = artwork.settings()["retroachievements"].get("username") or ""
        except Exception:  # noqa: BLE001
            mine = ""
        if who and mine and who.lower() != mine.lower():
            issues.append("otheruser")

        return {"ok": True, "found": True, "where": str(config),
                "achievements": achievements, "hardcore": hardcore,
                "user": who, "mine": mine, "issues": issues}

    return {"ok": True, "found": False, "issues": []}
