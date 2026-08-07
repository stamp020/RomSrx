"""Parsing of No-Intro / Redump style ROM filenames.

A typical name looks like:
    Final Fantasy VII (USA) (Disc 1) (Rev 1).zip
    007 - From Russia with Love (Europe) (En,Fr,De,Es,It,Nl,Sv).chd
    Tekken 3 (Japan) (Demo) [Beta].zip

We pull the base title out from in front of the first bracket group, then
classify each bracket group as a region, a language list, a version, a disc
number, or a free-form tag.
"""

from __future__ import annotations

import re
import unicodedata

# Region names as they appear in Redump / No-Intro sets. Compared lowercase.
REGIONS = {
    "usa", "europe", "japan", "world", "asia", "australia", "austria",
    "belgium", "brazil", "canada", "china", "croatia", "czech", "denmark",
    "finland", "france", "germany", "greece", "hong kong", "hungary", "india",
    "ireland", "israel", "italy", "korea", "latin america", "mexico",
    "netherlands", "new zealand", "norway", "poland", "portugal", "russia",
    "scandinavia", "singapore", "south africa", "spain", "sweden",
    "switzerland", "taiwan", "turkey", "uk", "united kingdom", "unknown",
}

# Two-letter language codes used in the (En,Fr,De) style groups.
LANGUAGES = {
    "en", "fr", "de", "es", "it", "nl", "sv", "no", "da", "fi", "pt", "ru",
    "ja", "ko", "zh", "pl", "cs", "hu", "el", "tr", "ar", "he", "ca", "gl",
    "eu", "sk", "sl", "hr", "ro", "bg", "uk", "th", "vi", "id", "ms", "hi",
}

# Canonical display casing for regions we care about most.
REGION_DISPLAY = {
    "usa": "USA", "uk": "UK", "united kingdom": "UK",
    "hong kong": "Hong Kong", "latin america": "Latin America",
    "new zealand": "New Zealand", "south africa": "South Africa",
}

# Older GoodTools sets (GoodNES and friends) abbreviate the region instead of
# spelling it out: '10-Yard Fight (J) (PRG0) [!]'. Only whole groups that match
# one of these count, so ordinary tags are unaffected. 'No' is deliberately
# absent - it collides with the Norwegian language code.
GOODTOOLS_REGIONS = {
    "u": ["USA"], "j": ["Japan"], "e": ["Europe"], "w": ["World"],
    "ue": ["USA", "Europe"], "ju": ["Japan", "USA"], "uj": ["USA", "Japan"],
    "je": ["Japan", "Europe"], "jue": ["Japan", "USA", "Europe"],
    "f": ["France"], "g": ["Germany"], "i": ["Italy"], "s": ["Spain"],
    "k": ["Korea"], "ch": ["China"], "b": ["Brazil"], "c": ["Canada"],
    "a": ["Australia"], "hk": ["Hong Kong"], "nl": ["Netherlands"],
    "sw": ["Sweden"], "gr": ["Greece"], "as": ["Asia"],
}

_GROUP_RE = re.compile(r"[(\[]([^()\[\]]*)[)\]]")
_DISC_RE = re.compile(r"^dis[ck]\s*(\d+)", re.I)
_VERSION_RE = re.compile(r"^(?:rev\s*([0-9a-z.]+)|v\s*([0-9][0-9a-z.]*))$", re.I)
_ARTICLE_RE = re.compile(r",\s*(the|a|an|le|la|les|el|los|das|der|die)$", re.I)
_PUNCT_RE = re.compile(r"[^\w\s]", re.UNICODE)
_WS_RE = re.compile(r"\s+")

# Files that live in an archive.org item but are not ROMs.
_META_NAMES = re.compile(
    r"(_meta\.xml|_files\.xml|_reviews\.xml|_meta\.sqlite|_archive\.torrent"
    r"|^__ia_thumb|^thumb[_.]|\.torrent$|_itemimage\.|^history/)", re.I)
_META_FORMATS = {
    "metadata", "archive bittorrent", "item tile", "jpeg thumb", "png",
    "jpeg", "item image", "thumbnail", "web page", "web archive gz",
}


def is_metadata_file(name: str, fmt: str | None) -> bool:
    """True for archive.org bookkeeping files that should never be indexed."""
    if _META_NAMES.search(name):
        return True
    return bool(fmt) and fmt.strip().lower() in _META_FORMATS


def _display_region(token: str) -> str:
    low = token.strip().lower()
    return REGION_DISPLAY.get(low, token.strip().title())


def normalize_title(title: str) -> str:
    """Fold a title into a comparable key: no accents, articles, or punctuation.

    'Legend of Dragoon, The' and 'The Legend of Dragoon' both become
    'legend of dragoon', so the same game groups across differently named sets.
    """
    text = unicodedata.normalize("NFKD", title)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = text.lower().strip()
    text = _ARTICLE_RE.sub("", text)                 # 'zelda, the' -> 'zelda'
    text = re.sub(r"^(the|a|an)\s+", "", text)       # 'the zelda'  -> 'zelda'
    text = text.replace("&", " and ")
    text = _PUNCT_RE.sub(" ", text)
    return _WS_RE.sub(" ", text).strip()


def split_extension(filename: str) -> tuple[str, str]:
    """Return (stem, extension) handling double extensions like .bin.gz."""
    stem, _, ext = filename.rpartition(".")
    if not stem:
        return filename, ""
    ext = ext.lower()
    # Keep the meaningful half of things like 'game.bin.ecm' / 'game.cue.gz'.
    inner_stem, _, inner_ext = stem.rpartition(".")
    if inner_stem and inner_ext.lower() in {"bin", "cue", "iso", "img", "tar"}:
        return inner_stem, f"{inner_ext.lower()}.{ext}"
    return stem, ext


def parse(path: str, default_region: str | None = None) -> dict:
    """Parse a file path from an archive.org item into structured fields."""
    filename = path.rsplit("/", 1)[-1]
    stem, ext = split_extension(filename)

    groups = [g.strip() for g in _GROUP_RE.findall(stem)]
    cut = stem.find("(")
    bracket = stem.find("[")
    if cut < 0 or (0 <= bracket < cut):
        cut = bracket
    title = (stem[:cut] if cut >= 0 else stem).strip(" -_")

    regions: list[str] = []
    languages: list[str] = []
    tags: list[str] = []
    version = ""
    disc = ""

    for group in groups:
        if not group:
            continue
        parts = [p.strip() for p in group.split(",") if p.strip()]

        if parts and all(p.lower() in REGIONS for p in parts):
            regions.extend(_display_region(p) for p in parts)
            continue
        if len(parts) == 1 and parts[0].lower() in GOODTOOLS_REGIONS:
            regions.extend(GOODTOOLS_REGIONS[parts[0].lower()])
            continue
        if parts and all(p.lower() in LANGUAGES for p in parts):
            languages.extend(p.capitalize() for p in parts)
            continue

        disc_match = _DISC_RE.match(group)
        if disc_match:
            disc = disc_match.group(1)
            continue

        version_match = _VERSION_RE.match(group)
        if version_match:
            version = group.strip()
            continue

        tags.append(group)

    if not regions and default_region:
        regions.append(default_region)

    # Dedupe while preserving order.
    regions = list(dict.fromkeys(regions))
    languages = list(dict.fromkeys(languages))

    return {
        "title": title or stem,
        "title_norm": normalize_title(title or stem),
        "regions": regions,
        "languages": languages,
        "version": version,
        "disc": disc,
        "tags": tags,
        "ext": ext,
    }
