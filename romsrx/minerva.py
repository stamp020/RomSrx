"""Reading MiNERVA's directory listings into the same shape archive.org uses.

MiNERVA distributes by BitTorrent rather than HTTP, one torrent per collection
directory - so there is no per-game URL to fetch, and at first glance nothing
this app could index. Two things make it work anyway.

The first is that every collection is a plain server-rendered listing. One GET
of `/browse/./Redump/Sony - PlayStation/` comes back with eleven thousand
games, their names and their sizes, in about six seconds. That is the same
work this app already does against archive.org's metadata API, in a different
dress.

The second is that BitTorrent has always let a client fetch one file out of a
thousand: every file has a priority, and zero means never ask anyone for it.
What that needs is a way to say *which* file, and the name is it.

Every row also carries a `data-m` attribute, contiguous from zero, and it is
tempting to read as the file's index inside the torrent. It is not, and this
was found the way these things usually are - by fetching one and getting a
different game. `data-m` is the row's place in the site's own listing, which
contains entries the torrent does not have (the BIOS files, for one) and sorts
by a different collation. Off by one at the top of the list, off by more
further down, and wrong in a way nothing would have reported: the download
succeeds, it is simply not the game that was asked for.

So a row records the collection's magnet and the filename, written as:

    magnet:?xt=urn:btih:<hash>&dn=<name>#name=<the%20file.zip>

The fragment is this app's own. A magnet has no notion of "and only this
file", and putting it after the # keeps the magnet valid for anything that
ignores fragments - including a torrent client the reader hands it to. The
name is what torrent.py looks up in the metadata once it arrives, which is the
one source that cannot disagree with the torrent about what is in it.

Nothing here downloads anything. This module reads listings; what fetches the
bytes is a separate question with a separate answer.
"""

from __future__ import annotations

import html as htmllib
import re
import urllib.parse

BASE = "https://minerva-archive.org"
BROWSE = BASE + "/browse/"

# Sizes are written the way the site writes them. Which base it means is not
# stated anywhere, and the difference between 1000 and 1024 is a few per cent
# on a number used for a progress bar and a disk-space warning - so the
# commoner convention for this kind of listing is assumed and the error is
# left where it is visible rather than hidden behind a guess.
UNITS = {"B": 1, "KB": 1024, "MB": 1024 ** 2,
         "GB": 1024 ** 3, "TB": 1024 ** 4, "PB": 1024 ** 5}

# One row. Deliberately tolerant about what sits between the pieces - the
# markup has a good deal of whitespace and the odd empty block in it - and
# deliberately strict about the pieces themselves: a link to /rom?id=, a size,
# and a magnet with an index beside it. A directory row has none of those, and
# so is skipped without having to be recognised.
ENTRY = re.compile(
    r'<div class="entry"[^>]*>\s*'
    r'(?:<[^>]+>\s*)*?'
    r'<a href="/rom\?id=(?P<id>\d+)"[^>]*>(?P<name>[^<]+)</a>\s*'
    r'<span>(?P<size>[^<]*)</span>'
    r'.*?'
    r"downloadMagnet\('(?P<magnet>magnet:\?xt=urn:btih:[0-9a-fA-F]{32,40}[^']*)'\)"
    r'"[^>]*?data-m="(?P<at>\d+)"',
    re.S)


def parse_size(text: str) -> int:
    """"387.64 MB" as bytes, and anything unreadable as nothing.

    Zero rather than a guess: a size is used to show a number and to check
    there is room for it, and both of those are better off saying nothing than
    saying something wrong.
    """
    m = re.match(r"\s*([\d.,]+)\s*([KMGTP]?B)\s*$", str(text or ""), re.I)
    if not m:
        return 0
    try:
        amount = float(m.group(1).replace(",", ""))
    except ValueError:
        return 0
    return int(amount * UNITS.get(m.group(2).upper(), 1))


def file_magnet(magnet: str, filename: str) -> str:
    """The collection's magnet, with the wanted file's name on the end.

    The name rather than a number, because the number the site publishes is
    its own row order and not the torrent's - see the note at the top. Quoted,
    so a game with a `#` or a `&` in its name does not end the fragment early.
    """
    clean = htmllib.unescape(str(magnet or "")).strip()
    name = str(filename or "").strip()
    if not clean or not name:
        return ""
    return f"{clean.split('#', 1)[0]}#name={urllib.parse.quote(name, safe='')}"


def wanted_name(magnet: str) -> str:
    """The filename on the end of one of our magnets, or "" if it has none."""
    _, _, fragment = str(magnet or "").partition("#name=")
    return urllib.parse.unquote(fragment) if fragment else ""


def entries(page: str) -> list[dict]:
    """Every game in one listing: its name, size, and where to get it.

    The order is the order the page gives, which is the order the torrent
    gives, which is why the indexes come out contiguous - a useful thing to be
    able to check.
    """
    found = []
    for m in ENTRY.finditer(page or ""):
        name = htmllib.unescape(m.group("name")).strip()
        if not name:
            continue
        found.append({
            "id": int(m.group("id")),
            "filename": name,
            "size": parse_size(m.group("size")),
            # Kept because it is what makes each row distinct in the listing,
            # and because it is worth being able to say where a row came from.
            # Not used to choose a file - see the note at the top.
            "at": int(m.group("at")),
            "magnet": file_magnet(m.group("magnet"), name),
        })
    return found


def listing_url(path: str) -> str:
    """The browse URL for a collection path like `./Redump/Sony - PlayStation/`.

    Quoted a component at a time so the slashes survive and the spaces,
    apostrophes and ampersands in a collection name do not have to be thought
    about by whoever writes one into sources.json.
    """
    clean = str(path or "").strip().strip("/")
    parts = [urllib.parse.quote(p, safe="") for p in clean.split("/") if p]
    return BROWSE + "/".join(parts) + "/"


def page_url(rom_id: int) -> str:
    """Where a single game's page is, for a link out to the site."""
    return f"{BASE}/rom?id={int(rom_id)}"
