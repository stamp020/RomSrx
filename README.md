# RomSrx

A desktop app that searches ROM collections hosted on archive.org. Type a game
name, get every copy across every configured source — with region, file type,
size — and download them from inside the app, with a queue, resume and retry.

Search is entirely local: the index is a SQLite database built once from
archive.org's metadata API, then queried offline.

## Download

Grab the latest build from [Releases](https://github.com/stamp020/RomSrx/releases/latest):

| | |
| --- | --- |
| **Windows** | `RomSrx-<version>-windows.zip` — unzip, run `RomSrx.exe` |
| **Linux / Steam Deck** | `RomSrx-<version>-linux.tar.gz` — extract, run `./RomSrx` |

Nothing to install; both are self-contained. The app tells you when a newer
release is out, and there's a **Check for updates** link in the footer.

The build ships without an index, so the first launch needs one: press
**Reindex** in the app, or run `python -m romsrx index`. It takes a couple of
minutes and is the only step that touches the network.

### A note on Linux and the Steam Deck

The Windows build opens in a native window. The Linux build opens in your
default browser instead — it runs the same local server and the same interface,
it just doesn't bundle a browser engine of its own. That is deliberate: a
native window needs WebKitGTK present on the machine, which can't be relied on
where the system image is read-only, the Steam Deck included.

Folder pickers on Linux need Tk (`sudo apt install python3-tk` on Debian and
Ubuntu). Without it the **Browse…** buttons do nothing; you can still type
paths in by hand.

## Running from source

```bash
python -m romsrx index
```

```bash
python -m romsrx serve
```

Then open <http://127.0.0.1:8770>.

The first `index` takes a couple of minutes and pulls file listings for all 71
configured sources across 10 consoles. It is the only step that touches the
network; searching afterwards is entirely local and instant.

Currently indexed: **23,380 games / 57,922 files / 35.7 TB** — PlayStation,
PlayStation 2, PSP, GameCube, Nintendo DS, Nintendo Wii, Nintendo 3DS, Sega CD,
Sega Saturn, Sega Dreamcast.

## Commands

| Command | What it does |
| --- | --- |
| `python -m romsrx app` | Run the desktop app (native window, or browser) |
| `python -m romsrx serve` | Run just the web app (default: `127.0.0.1:8770`) |
| `python -m romsrx index` | Fetch/refresh file lists from archive.org |
| `python -m romsrx index --only PSP` | Refresh just one console, source id, or item |
| `python -m romsrx stats` | Show what is currently indexed, per source |

`serve` takes `--host` and `--port`. `index` takes `--workers` (default 4).
You can also trigger a refresh from the **Reindex** button in the UI.

## Building

Dependencies are all optional at runtime — the app degrades rather than
failing — but a build wants them present so they get bundled:

```bash
python -m pip install -r requirements.txt pyinstaller
```

| Platform | Command | Output |
| --- | --- | --- |
| Windows | `powershell -File build.ps1` | `dist\RomSrx\RomSrx.exe` |
| Linux / macOS | `./build.sh` | `dist/RomSrx/RomSrx` |

Both write a `build.log` next to the script. Close the app before building —
the build wipes `dist/`, and Windows won't delete files a running app holds
open. `build.ps1` checks for this and says so rather than failing cryptically.

PyInstaller cannot cross-compile, so each platform must be built on itself.
[.github/workflows/release.yml](.github/workflows/release.yml) does both on
tag push and attaches them to a release.

### Publishing

| Script | What it does |
| --- | --- |
| `tools/first-push.bat` | One-time: connect this folder to GitHub |
| `tools/push.bat` | Send your changes |
| `tools/release.bat` | Bump the version, tag it, and publish builds |

`release.bat` sets `__version__` and the git tag together — the in-app update
check compares the two, so they have to agree.

## Downloads need an archive.org login

53 of the 71 sources are in archive.org's `loggedin` collection and/or flagged
`access-restricted-item`. Anonymous downloads from those get a 401/403 — this
is archive.org's restriction, not something the app can work around. Sign in to
archive.org in the same browser and the download links work normally.

Files from restricted sources are marked 🔒 **login** in the results. The
RetroAchievements sets, the CHD zstd sets (PSP/Dreamcast), the GameCube sets,
the DS pack, and the Wii sets currently download without an account.

Indexing is unaffected either way — the metadata API is public.

## Covers, and filling in the ones that are missing

Box art comes from [thumbnails.libretro.com](https://thumbnails.libretro.com),
which is free, needs no account and is keyed by the filenames the No-Intro and
Redump sets use. The app reads that server's directory listings and matches
against the names really on it, rather than guessing URLs — over the whole
index that finds art for **87%** of files.

Where there is no box at all — homebrew, hacks, prototypes — it falls back to
title screens and then in-game snaps, which takes that category from 45% to
60%. Those two are always the **last** thing tried, after every source that
could supply a real cover, because a screenshot is what you show when nobody
anywhere has one.

The rest is mostly games whose filename never matched a preservation set. Two
optional services search by *title* instead, so they miss a different set of
games, and **Settings → Cover art** is where you turn them on:

| Service | Key from | Good for |
| --- | --- | --- |
| [RetroAchievements](https://retroachievements.org/settings) | Your settings page, under Keys | Hacks, translations and aftermarket homebrew — anything with an achievement set |
| [IGDB](https://dev.twitch.tv/console/apps) | A Twitch application — Client ID and Client Secret | Nearly every commercial release, on every console indexed here |
| [SteamGridDB](https://www.steamgriddb.com/profile/preferences/api) | An account, then generate an API key | Community uploads: bootlegs, multicarts and everything else |

RetroAchievements is asked first, and is nearly free to ask: the app has always
kept their per-console game lists — that is what the right-click **Achievements**
entry opens — so a title already resolves to a numeric game id without any key
at all. The key only turns that id into a picture. It covers just under a fifth
of the files nothing else can match, and they are exactly the ones no commercial
database will ever carry.

Both are free. Neither is used until you paste a key in, and each panel has a
**Test** button that says plainly whether the key works. **Use these** decides
where they sit relative to libretro:

| Setting | Order |
| --- | --- |
| only for games libretro has no cover for *(default)* | libretro box art → services → title screens → snaps |
| first, and fall back to libretro | services → libretro box art → title screens → snaps |
| instead of libretro entirely | services only — an unmatched game shows nothing |

Of the remaining two, IGDB goes first because it can be told which platform to
answer about; SteamGridDB has no idea what a platform is, so it goes last. In
every case a cover is only accepted when
both sides agree on the title exactly, once case, punctuation, accents and
bracketed tags are taken out — a game wearing another game's box is worse than
a blank tile.

Answers are remembered on disk, misses included, because both services meter
requests by the day. **Look everything up again** clears that. Your keys stay in
`artwork.json` in the app's user folder, in plain text, and are deliberately
left out of backups.

## Will this copy earn achievements?

RetroAchievements attaches a set to particular dumps rather than to a title,
and identifies each one by a hash. On a search result the app answers by name —
both sides name the same dumps from the same preservation sets — and says so,
because a name is all that can be known before downloading a gigabyte.

For a game already on the machine it can answer outright. **Settings → Library →
Check every copy** reads each file, works out the number RetroAchievements knows
that dump by, and compares it against the set's own list; the same check is on a
game's right-click menu and in its preview panel. A tick or a cross then rides on
the tile, and the shelf can be narrowed to just the copies that will not earn
anything.

The hash is not simply the MD5 of the file — it is per console, and the rules
are ported from [rcheevos](https://github.com/RetroAchievements/rcheevos),
which is what the site itself runs: headers are skipped for NES, FDS, SNES,
PC Engine, Atari 7800 and Lynx, a Nintendo 64 ROM is normalised to big-endian
first, and a DS card is hashed from its header, boot code and icon block alone.
Zips and folders are looked inside; anything holding two ROMs is reported as
unclear rather than guessed at.

**Discs are partly covered.** A disc's hash comes from the program the disc
boots rather than from its bytes, so PlayStation and PlayStation 2 images are
opened, walked as an ISO9660 filesystem, and hashed from the executable named
in `SYSTEM.CNF` — `.iso` and raw `.bin`, including one named by a `.cue` or
sitting alone in a folder. `.chd` and `.rvz` are compressed formats this app
does not decode, and GameCube, Wii, Dreamcast, Saturn, Sega CD and PSP each
have a rule of their own that is not implemented. All of those are reported as
"not checked", never as a copy that failed.

When a copy does fail, the app looks for one that wouldn't: the set names the
dumps it was built from, and your index is a list of files, so the copy that
works is usually one press away. Matched on the dump's name with nothing
loosened — the region, the revision and the disc all still have to agree —
and dumps that are themselves a patch are never offered as a download.

Each file is read once and the answer kept, keyed on its size and
modified time — so the marks are back on the shelf the next time you open the
app, without checking anything again. A game stored as a folder is keyed on
what is inside it, and any copy that has changed since it was checked quietly
drops its answer rather than showing you a stale one.

## Will this session count?

Hardcore — no save states, no rewind, no cheats — is the mode RetroAchievements
ranks people on, and it is a switch inside RetroArch rather than in here. The
usual way to discover it was off is finishing a game and watching the unlocks
land as softcore, worth no points and no mastery.

**Settings → Library** reads RetroArch's own configuration and says what it
found: achievements off, hardcore off, nobody signed in, or signed in as
somebody other than the account configured here. Nothing is ever written —
changing another program's achievement settings is not this app's to do — and
the login token in the same file is never read. Machines with no RetroArch get
no row at all rather than a warning about an emulator they do not use.

## Your Want to Play list

RetroAchievements keeps a **Want to Play** list, and you add to it wherever you
happen to be — on a phone, on someone else's machine, halfway through reading
about a game. The bookmark button on the library toolbar brings it here and
matches every game on it against your index, so each one says what can be done
about it: already on your shelf, ready to download, a hack that needs the
patcher, or nothing your sources carry.

Anything downloadable can be fetched from the row, added to the download list,
or taken all at once. The copy offered is the one a search would have put at
the top — the region order from Settings — except that demos, betas and
prototypes are pushed below finished releases, since nothing here is chosen by
hand.

Matching their titles to a preservation set's is the awkward part: they write
*The Legend of Spyro: A New Beginning* and No-Intro writes *Legend of Spyro,
The - A New Beginning (USA)*. Both sides are folded the same way — the region,
the studio in front, the article parked in the middle, Roman numerals and
spacing all come off. On a real list of 78, folding one side matched 55,
folding both matched 61, and the full ladder matched 70; of the remaining
eight, four were hacks and four were games no configured source carries.

## Adding sources

Everything lives in [sources.json](sources.json). Add an entry and re-run
`python -m romsrx index`:

```json
{ "id": "gc_a", "console": "GameCube", "name": "GameCube (A)",
  "identifier": "your_archive_item_id" }
```

- **`identifier`** — the part of the URL after `/download/`.
  For `https://archive.org/download/sony_playstation_part1`, that's
  `sony_playstation_part1`.
- **`path_prefix`** *(optional)* — index only a subfolder inside the item, e.g.
  `"CHD-PSX-USA"` for `https://archive.org/download/chd_psx/CHD-PSX-USA/`.
- **`default_region`** *(optional)* — region to assume when a filename carries
  no region tag of its own (some sets are just `Game Name.7z`).

The `extensions` list at the top of the file controls which file types get
indexed; anything not listed is skipped, along with archive.org's own metadata
files. Adding a new console is just new entries — no code changes.

## How it works

```
sources.json ──▶ indexer.py ──▶ SQLite (romsrx.db) ──▶ server.py ──▶ web/
                     │                  │
              metadata API         FTS5 index
```

- **`romsrx/indexer.py`** calls `https://archive.org/metadata/<id>`, which
  returns every file in an item with its size — no HTML scraping.
- **`romsrx/names.py`** parses Redump / No-Intro filenames
  (`Final Fantasy VII (USA) (Disc 1) (Rev 1).zip`) into title, regions,
  languages, disc, version, and tags.
- **`romsrx/db.py`** stores files in SQLite with an FTS5 full-text index and
  groups search hits by a normalised title, so the same game from different
  sources collapses into one result. `Legend of Dragoon, The` and
  `The Legend of Dragoon` normalise to the same key.
- **`romsrx/server.py`** serves the frontend and a small JSON API.

Search does prefix matching per word, so `gran tur` finds Gran Turismo.
Exact title matches rank above prefix matches, so `final fantasy vii` puts
VII above VIII.

### Filter chips

The chips above the results are **contextual** — they only offer values that
exist in the current search, with a count of matching games each. Clicking
toggles them, and several can be active at once: two consoles means "either
console", while a console *and* a region means both must hold.

Each dimension's counts are calculated with the *other* dimensions applied but
not its own, so picking `PSP` doesn't collapse the console row down to just
PSP — the alternatives stay visible so you can switch without clearing first.

`console`, `region`, and `ext` accept comma-separated values, and the API takes
the same form: `/api/search?q=gran+turismo&console=PSP,PlayStation`.

## API

| Endpoint | Notes |
| --- | --- |
| `GET /api/search?q=&console=&region=&ext=&source=&limit=&offset=` | Results grouped by game, plus facet counts |
| `GET /api/facets` | Global filter values with counts |
| `GET /api/stats` | Totals and per-source status |
| `POST /api/index` | Start a reindex; poll `GET /api/index/status` |
| `GET /api/update` | Latest release vs. the running version; `?force=1` skips the cache |
| `GET /api/library` | What is actually on disk, grouped by console |
| `GET /api/ra/wanted` | Your Want to Play list, joined to the index; `?refresh=1` skips the cache |
| `POST /api/library/verify` | Hash the given games and check them against their achievement sets |
| `POST /api/library/verify/all` | Sweep the shelf; poll `GET /api/library/verify/status`, stop with `POST /api/library/verify/cancel` |
| `GET`/`POST` `/api/downloads` | The download queue |
| `GET`/`POST` `/api/cart` | The saved download list |

## Notes

`romsrx.db` is rebuilt per source on each index — deleting it and re-running
`index` is always safe. Sizes come from archive.org's own metadata.
