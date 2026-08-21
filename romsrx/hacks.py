"""Reaching the achievement sets that are a patch rather than a ROM.

RetroAchievements carries sets for fan hacks and translations - 1,240 of them
on the consoles this app indexes - and none of them is a file anybody hosts.
A hack is a diff against a commercial release, and the release is the part
that can be downloaded.

Both halves were already here and nothing joined them up. RetroAchievements
publishes the patches themselves in its RAPatches repository, which retro.py
already reads for the "patch this game" button; MiNERVA has the base ROMs.
What was missing is the one fact that connects them, and it turns out to be
sitting in the patch's own address:

    .../MD/Hacks/Sonic the Hedgehog 2/9043-Sonic2-AmyRose.zip
                 ^^^^^^^^^^^^^^^^^^^^ the game it is a diff against

So: read the base game off the path, find a dump of it in the index, download
that, apply the patch. And unlike an ordinary download the result is provable
- the patched file can be hashed and checked against the very list the set
accepts, which is a stronger answer than any plain download can give.

Measured over the whole catalogue when this was written: 1,179 of the 1,240
sets have a patch published, and 989 of those name a base game the index can
already produce.
"""

from __future__ import annotations

import urllib.parse

from . import retro

# Folder names in the repository that are not a game. They are the layer above
# - the kind of patch rather than what it patches - and reading one as a title
# sends the matcher looking for a game called "Subset".
NOT_A_GAME = frozenset({
    "hacks", "hack", "translations", "translation", "subset", "subsets",
    "fix", "fixes", "demos", "demo", "prototypes", "homebrew", "unlicensed",
    "misc", "other", "patches",
})

# Base games the repository writes shorter, or differently, than any dump of
# them is named. Only where the two are genuinely different words: everything
# that is merely a missing subtitle is handled by the prefix rule below, which
# needs no maintaining.
ALIASES = {
    "loz": "The Legend of Zelda",
    "loz - ocarina of time": "The Legend of Zelda - Ocarina of Time",
    "loz - majora's mask": "The Legend of Zelda - Majora's Mask",
    "loz - a link to the past": "The Legend of Zelda - A Link to the Past",
    "loz - link's awakening": "The Legend of Zelda - Link's Awakening",
    # Not a Turtles game at all: "Shredder's Re-Revenge" is a hack of Streets
    # of Rage 2, and the index spells its own copies "SOR2 - Teenage Mutant
    # Ninja Turtles ...". Guessing from the name gave Hyperstone Heist, which
    # would have applied the patch to the wrong game and produced a file that
    # matched nothing.
    "tmnt - shredder's re-revenge": "Streets of Rage 2",
    "spongebob squarepants - bfbb":
        "SpongeBob SquarePants - Battle for Bikini Bottom",
    "goldeneye": "GoldenEye 007",
    # A subtitle the repository leaves off and every dump carries. Spelled out
    # rather than reached by the prefix rule, because the index also holds
    # hacks of these and a prefix that fits several is refused.
    "pokemon red": "Pokemon Red Version",
    "pokemon blue": "Pokemon Blue Version",
    "pokemon yellow": "Pokemon Yellow Version",
    "pokemon gold": "Pokemon Gold Version",
    "pokemon silver": "Pokemon Silver Version",
    "pokemon crystal": "Pokemon Crystal Version",
    "pokemon ruby": "Pokemon Ruby Version",
    "pokemon sapphire": "Pokemon Sapphire Version",
    "pokemon emerald": "Pokemon Emerald Version",
    "pokemon firered": "Pokemon FireRed Version",
    "pokemon leafgreen": "Pokemon LeafGreen Version",
    "zelda ii": "Zelda II - The Adventure of Link",
    "super mario world 2": "Super Mario World 2 - Yoshi's Island",
    "donkey kong country 2": "Donkey Kong Country 2 - Diddy's Kong Quest",
    "donkey kong country 3": "Donkey Kong Country 3 - Dixie Kong's Double Trouble!",
    "super mario advance 2": "Super Mario Advance 2 - Super Mario World",
    "smw": "Super Mario World",
    "sm64": "Super Mario 64",
    "dkc": "Donkey Kong Country",
    "ff": "Final Fantasy",
    "sotn": "Castlevania - Symphony of the Night",
}


def base_name(patch_url: str) -> str:
    """The game a patch is a diff against, from the patch's own address.

    "" when the address does not name one - a patch filed directly under
    Hacks/ with no game folder of its own, which a few are.
    """
    parts = [urllib.parse.unquote(bit)
             for bit in str(patch_url or "").split("/") if bit]
    if len(parts) < 2:
        return ""
    folder = parts[-2].strip()
    if not folder or folder.lower() in NOT_A_GAME:
        return ""
    return ALIASES.get(folder.lower(), folder)


def find_base(fold: dict, name: str) -> str:
    """The indexed title_norm for a base game, or "" if it cannot be placed.

    `fold` is one console's folded-title map, as wanted._fold_one builds it.

    Two rules, in this order, and the order is the safety of it:

      the ordinary ladder   every spelling retro.match_keys will try;
      a unique prefix       one indexed title, and exactly one, that begins
                            with the name.

    The prefix rule is what reaches 'Pokemon FireRed' -> 'Pokemon FireRed
    Version' and 'Zelda II' -> 'Zelda II - The Adventure of Link', which is
    most of what the ladder misses. It is dangerous in exactly one way: a
    title that is the start of a longer one. 'Super Mario World' begins
    'Super Mario World 2', and answering the wrong one would patch a hack of
    the first onto the second.

    Two things stop that. The ladder runs first, so a game that is named
    outright is answered before any prefix is tried at all - and Super Mario
    World is named outright. And a prefix that fits more than one title is
    refused rather than guessed between, so the case where it really is
    ambiguous produces nothing instead of a coin toss.
    """
    if not fold or not name:
        return ""
    for candidate in retro.match_keys(name):
        found = fold.get(candidate)
        if found:
            return found

    key = retro.match_key(name)
    if len(key) < 6:            # too short to be a safe prefix of anything
        return ""
    hits = {norm for spelling, norm in fold.items()
            if spelling.startswith(key + " ")}
    return hits.pop() if len(hits) == 1 else ""


def plan(fold: dict, game_id: int, patches: dict) -> dict:
    """What it would take to reach one hack set: {patch, base, norm}.

    Empty when any part is missing, because all three are needed and a plan
    with a hole in it is worse than none - it would offer a download that
    cannot become the thing it was asked for.
    """
    urls = (patches or {}).get(int(game_id or 0)) or []
    if not urls:
        return {}
    url = urls[0]
    base = base_name(url)
    if not base:
        return {}
    norm = find_base(fold, base)
    if not norm:
        return {}
    return {"patch": url, "base": base, "norm": norm}
