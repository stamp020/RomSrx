"""SQLite storage and search queries."""

from __future__ import annotations

import re
import shutil
import sqlite3
import sys
from pathlib import Path

from .names import normalize_title
from .paths import data, user

# The index lives with the user's own files rather than beside the .exe. It is
# rebuildable, but rebuilding it means fetching every source again, so it is
# worth keeping across a reinstall - and worth being able to put in a backup,
# which only reaches the user folder.
DB_NAME = "romsrx.db"
DB_PATH = user(DB_NAME)

# SQLite keeps recent writes in a sidecar until they are folded back in, so
# the database is these three files rather than one.
DB_SIDECARS = ("-wal", "-shm")

# Where a restored index waits. A backup cannot be unpacked straight over a
# database this process has open - Windows will not have it, and on anything
# else it would leave a new file beside a stale sidecar. So a restore writes
# here and the swap happens on the next start, before anything is opened.
RESTORE_SUFFIX = ".restored"


def _adopt_restored(path: Path) -> None:
    """Swap in an index left by a restore, before anything opens the old one."""
    waiting = path.with_name(path.name + RESTORE_SUFFIX)
    if not waiting.is_file():
        return
    try:
        for suffix in DB_SIDECARS:
            path.with_name(path.name + suffix).unlink(missing_ok=True)
        waiting.replace(path)
    except OSError:
        pass          # still openable; the old index simply stays


def _migrate_from_exe_folder(path: Path) -> None:
    """Move an index written by a version that kept it beside the .exe."""
    old = data(DB_NAME)
    if path.exists() or not old.is_file() or old == path:
        return
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(old), str(path))
        for suffix in DB_SIDECARS:
            beside = old.with_name(old.name + suffix)
            if beside.is_file():
                shutil.move(str(beside), str(path.with_name(path.name + suffix)))
    except OSError:
        pass          # left where it was; a reindex fills the new one


def snapshot(target: str | Path, source: Path | str | None = None) -> bool:
    """Copy the index to `target` as one consistent file.

    Through SQLite rather than by copying bytes: with writes still in the
    sidecar, the file on its own is behind, and a copy taken mid-write is not
    a database at all. This asks SQLite for the whole of it, safely, while the
    app carries on using it.
    """
    # Read now rather than bound as a default: a default argument is fixed
    # when the function is defined, which would quietly snapshot the original
    # path forever if anything ever pointed the app at another one.
    source = Path(source if source is not None else DB_PATH)
    if not source.is_file():
        return False
    try:
        live = sqlite3.connect(source)
        try:
            copy = sqlite3.connect(target)
            try:
                live.backup(copy)
            finally:
                copy.close()
        finally:
            live.close()
    except sqlite3.Error:
        return False
    return True

SCHEMA = """
CREATE TABLE IF NOT EXISTS sources (
    id            TEXT PRIMARY KEY,
    console       TEXT NOT NULL,
    name          TEXT NOT NULL,
    identifier    TEXT NOT NULL,
    path_prefix   TEXT,
    url           TEXT NOT NULL,
    file_count    INTEGER DEFAULT 0,
    total_size    INTEGER DEFAULT 0,
    last_indexed  TEXT,
    last_error    TEXT,
    -- archive.org serves some items only to signed-in accounts.
    requires_login INTEGER NOT NULL DEFAULT 0,
    -- Display order for consoles, taken from the order in sources.json.
    console_rank  INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS files (
    id         INTEGER PRIMARY KEY,
    source_id  TEXT NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    console    TEXT NOT NULL,
    path       TEXT NOT NULL,
    filename   TEXT NOT NULL,
    title      TEXT NOT NULL,
    title_norm TEXT NOT NULL,
    regions    TEXT NOT NULL DEFAULT '',
    languages  TEXT NOT NULL DEFAULT '',
    version    TEXT NOT NULL DEFAULT '',
    disc       TEXT NOT NULL DEFAULT '',
    tags       TEXT NOT NULL DEFAULT '',
    ext        TEXT NOT NULL DEFAULT '',
    size       INTEGER NOT NULL DEFAULT 0,
    url        TEXT NOT NULL,
    UNIQUE (source_id, path)
);

CREATE INDEX IF NOT EXISTS idx_files_norm    ON files(title_norm);
CREATE INDEX IF NOT EXISTS idx_files_console ON files(console);
CREATE INDEX IF NOT EXISTS idx_files_ext     ON files(ext);

CREATE VIRTUAL TABLE IF NOT EXISTS files_fts USING fts5(
    title_norm,
    filename,
    content='files',
    content_rowid='id',
    tokenize='unicode61'
);

CREATE TRIGGER IF NOT EXISTS files_ai AFTER INSERT ON files BEGIN
    INSERT INTO files_fts(rowid, title_norm, filename)
    VALUES (new.id, new.title_norm, new.filename);
END;

CREATE TRIGGER IF NOT EXISTS files_ad AFTER DELETE ON files BEGIN
    INSERT INTO files_fts(files_fts, rowid, title_norm, filename)
    VALUES ('delete', old.id, old.title_norm, old.filename);
END;

CREATE TRIGGER IF NOT EXISTS files_au AFTER UPDATE ON files BEGIN
    INSERT INTO files_fts(files_fts, rowid, title_norm, filename)
    VALUES ('delete', old.id, old.title_norm, old.filename);
    INSERT INTO files_fts(rowid, title_norm, filename)
    VALUES (new.id, new.title_norm, new.filename);
END;
"""

FILE_COLUMNS = """
    f.id, f.source_id, f.console, f.path, f.filename, f.title, f.title_norm,
    f.regions, f.languages, f.version, f.disc, f.tags, f.ext, f.size, f.url,
    s.name AS source_name, s.identifier AS source_identifier,
    s.requires_login
"""


def connect(path: Path | str = DB_PATH) -> sqlite3.Connection:
    # Both of these have to happen before the file is opened: one moves an
    # index written by an older version into the user folder, the other puts
    # a restored one in place. Afterwards is too late - the file would be
    # open, and on Windows that settles the matter.
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    _migrate_from_exe_folder(path)
    _adopt_restored(path)

    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")

    # Reindexing is one commit per source - 178 of them - and each was waiting
    # on the disk to confirm the write. NORMAL only skips that confirmation,
    # which under WAL cannot corrupt the file: the worst case is losing the
    # last transaction if the machine loses power mid-write, and the last
    # transaction here is one source's file list, rebuilt by pressing reindex
    # again. The cache and temp settings are for the FTS index, which is
    # rewritten row by row as files land.
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA cache_size=-65536")      # 64 MB, negative = kibibytes
    conn.execute("PRAGMA temp_store=MEMORY")

    conn.executescript(SCHEMA)

    # Migrations for databases created before these columns existed.
    columns = {r["name"] for r in conn.execute("PRAGMA table_info(sources)")}
    if "requires_login" not in columns:
        conn.execute("ALTER TABLE sources ADD COLUMN "
                     "requires_login INTEGER NOT NULL DEFAULT 0")
    if "console_rank" not in columns:
        conn.execute("ALTER TABLE sources ADD COLUMN "
                     "console_rank INTEGER NOT NULL DEFAULT 0")
    return conn


# Within a console, USA copies come first, then Europe, then everything else,
# with unknown-region files last.
# Which copy of a game is offered first when there are six of them. USA then
# Europe was the assumption for a long time, and it is simply wrong for anyone
# who wants the Japanese release, or who lives in Europe and would rather not
# scroll past four American ones every time. It is a setting now; this is only
# the default.
DEFAULT_REGIONS = ("USA", "Europe")

# Region names are written into SQL rather than bound, because they sit in an
# ORDER BY that several queries share and threading parameters through all of
# them for a value the user picks from a fixed list is a lot of moving parts
# for no gain. So the list is checked instead: letters, spaces and hyphens,
# nothing else, and anything odd is dropped rather than quoted.
_REGION_OK = re.compile(r"^[A-Za-z][A-Za-z \-]{0,23}$")


def region_order() -> list[str]:
    """The user's preferred regions, best first."""
    from . import downloads  # noqa: PLC0415 - db is imported by downloads' users

    try:
        chosen = downloads.load_settings().get("region_priority")
    except Exception:  # noqa: BLE001 - a missing setting is the default
        chosen = None
    if not isinstance(chosen, list):
        return list(DEFAULT_REGIONS)
    kept = [r for r in chosen if isinstance(r, str) and _REGION_OK.match(r)]
    return kept or list(DEFAULT_REGIONS)


def region_rank_sql(order: list[str] | None = None) -> str:
    """A CASE putting the preferred regions first, then everything else.

    A file with no region at all sorts last: it is usually a homebrew release
    or a badly named dump, and either way it is not the copy somebody meant.
    """
    order = order if order is not None else region_order()
    lines = [f"WHEN (',' || f.regions || ',') LIKE '%,{name},%' THEN {at}"
             for at, name in enumerate(order)]
    return ("CASE " + " ".join(lines)
            + f" WHEN f.regions = '' THEN {len(order) + 1}"
            + f" ELSE {len(order)} END")


def region_sort_key(name: str, order: list[str] | None = None) -> tuple[int, str]:
    """Python-side twin of region_rank_sql, for ordering badge lists."""
    order = order if order is not None else region_order()
    return (order.index(name) if name in order else len(order), name)




_TOKEN_RE = re.compile(r"\w+", re.UNICODE)


def build_match_query(query: str) -> str:
    """Turn free text into an FTS5 MATCH expression with prefix matching.

    'final fant' becomes '"final"* AND "fant"*', so partial words still hit.
    """
    return _all_of(_TOKEN_RE.findall(normalize_title(query)))


def _all_of(tokens: list[str]) -> str:
    return " AND ".join(f'"{t}"*' for t in tokens)


# Words that describe the file rather than the game: the region it was released
# in, and what it is packed as. Someone who pastes 'Harry Potter (USA).iso' is
# asking about Harry Potter, and the rest is the label on the box.
#
# Only ever trimmed off the *end*, only as a fallback, and never all of them -
# 'Super Mario World' ends in a region word and is not a search for Mario, so
# this may not touch a query that already finds something. See _plan.
QUERY_NOISE = frozenset({
    "usa", "us", "eur", "europe", "japan", "jpn", "jap", "world", "asia",
    "korea", "china", "taiwan", "brazil", "australia", "canada", "france",
    "germany", "spain", "italy", "netherlands", "sweden", "russia", "uk",
    "ntsc", "pal", "en", "fr", "de", "es", "it", "ja", "rev", "proto",
    "beta", "unl", "disc", "cd",
    "iso", "bin", "cue", "chd", "zip", "7z", "rar", "gz", "rvz", "wbfs",
    "cso", "pbp", "gdi", "cdi", "gcm", "gcz", "img", "nkit", "rom", "nsp",
    "xci", "nds", "gba", "gbc", "sfc", "smc", "nes", "fds", "z64", "n64",
    "v64", "md", "gen", "gg", "sms", "pce", "vb", "ngp", "a26", "a78", "lnx",
})


def _trimmed(tokens: list[str]) -> list[str]:
    """The same words with the file's own vocabulary taken off the end."""
    kept = list(tokens)
    while len(kept) > 1 and kept[-1] in QUERY_NOISE:
        kept.pop()
    return kept


# How many files a query has to reach before it counts as having worked. Below
# this the squashed form is searched as well - see _plan - and above it the
# extra scan is not worth the tenth of a second it costs.
ENOUGH = 10


def _hits(conn: sqlite3.Connection, match: str, cap: int = ENOUGH) -> int:
    """How many files match, counted no further than `cap`."""
    if not match:
        return 0
    try:
        return conn.execute(
            "SELECT COUNT(*) FROM "
            "(SELECT 1 FROM files_fts WHERE files_fts MATCH ? LIMIT ?)",
            (match, cap)).fetchone()[0]
    except sqlite3.OperationalError:
        return 0


def _plan(conn: sqlite3.Connection, query: str) -> tuple[str, str]:
    """How to look this query up: (FTS expression, squashed LIKE pattern).

    Either may be empty. Both empty means "no query" - browse everything. Both
    set means "match either", which is how a thin result gets widened.

    Three expressions are tried, each only because the one before it came back
    thin, so a query that already works is never touched:

    1. Every word, as typed. What this has always done.
    2. The same without the file's own vocabulary on the end, so
       'harry potter usa' and 'harry potter.iso' ask about Harry Potter.
    3. Only the words that match anything at all. One word typed wrongly then
       costs that word rather than the whole search: 'jarry potter' finds
       nothing, 'potter' finds the games, and 'jarry' is simply dropped.

    Whichever wins, a result thinner than ENOUGH is also matched against titles
    with their spaces removed. That is for the apostrophe: "There's Nothing to
    Do in This Town" is indexed as 'there s nothing ...', so 'theres' matches
    neither 'there' nor 's' - but it does prefix 'theresnothing...'.

    It has to widen a thin answer rather than only rescue an empty one, because
    'theres' is not empty: it prefixes 'Theresia', finds two games, and without
    this would stop there perfectly satisfied with the wrong ones.
    """
    tokens = _TOKEN_RE.findall(normalize_title(query))
    if not tokens:
        return "", ""

    trimmed = _trimmed(tokens)
    known = [t for t in trimmed if _hits(conn, f'"{t}"*', 1)]

    best = ""
    for candidate in (tokens, trimmed, known):
        if not candidate:
            continue
        expression = _all_of(candidate)
        if expression == best:
            continue
        found = _hits(conn, expression)
        if found >= ENOUGH:
            return expression, ""
        if found and not best:
            best = expression

    # Built from what was actually typed, not from the trimmed words: this is
    # about somebody running a name together, so the words are theirs to
    # choose. Trimming here turned 'super mario world' into 'supermario%',
    # which is a different game as well as the right one.
    #
    # Anchored to the start of the title rather than floating inside it.
    # Loose, '%theres%' matched 'Rolo to the Rescue' - 'to-there-scue' - and a
    # fallback that drags in nonsense is worse than one that finds nothing.
    return best, "".join(tokens) + "%"


# Titles with their spaces removed, which is what the squashed fallback
# compares against. Written once here so the two places that need it cannot
# drift apart.
SQUASHED = "REPLACE(f.title_norm, ' ', '')"


def _as_list(value) -> list[str]:
    """Accept either a single value or a list; drop blanks."""
    if not value:
        return []
    if isinstance(value, str):
        value = [value]
    return [v.strip() for v in value if v and v.strip()]


# Every RetroAchievements set is named after it, so one pattern covers all of
# them - the list of source ids can grow in sources.json without touching this.
RA_SOURCES = ("f.source_id IN "
              "(SELECT id FROM sources WHERE name LIKE 'RetroAchievements%')")


def _filter_sql(console, region, ext, source, ra=False) -> tuple[str, list]:
    """Build the WHERE fragment. Each filter accepts multiple values (OR
    within a dimension, AND across dimensions)."""
    clauses: list[str] = []
    params: list = []

    if ra:
        clauses.append(RA_SOURCES)

    consoles = _as_list(console)
    if consoles:
        clauses.append(f"f.console IN ({','.join('?' * len(consoles))})")
        params.extend(consoles)

    regions = _as_list(region)
    if regions:
        # regions is a comma-joined list, so match on delimited boundaries.
        clauses.append("(" + " OR ".join(
            ["(',' || f.regions || ',') LIKE ?"] * len(regions)) + ")")
        params.extend(f"%,{r},%" for r in regions)

    exts = _as_list(ext)
    if exts:
        clauses.append(f"f.ext IN ({','.join('?' * len(exts))})")
        params.extend(e.lower() for e in exts)

    sources = _as_list(source)
    if sources:
        clauses.append(f"f.source_id IN ({','.join('?' * len(sources))})")
        params.extend(sources)

    return (" AND ".join(clauses), params)


def search(conn: sqlite3.Connection, query: str = "", *, console=None,
           region=None, ext=None, source=None, ra=False,
           limit: int = 50, offset: int = 0) -> dict:
    """Search for games, returning results grouped by normalized title.

    Each group is one game; its `files` are every matching copy across sources.
    """
    where, params = _filter_sql(console, region, ext, source, ra)
    match, squashed = _plan(conn, query)

    if squashed:
        # bm25 needs files_fts queried on its own, which this branch cannot do
        # once the squashed form is an alternative rather than a filter. So the
        # shortest title wins instead: what was typed is a fragment of a name,
        # and the title it is the largest fraction of is the likeliest one.
        #
        # Only ever reached for a query that found almost nothing, where there
        # is little to rank and being found at all is the point.
        finds = f"{SQUASHED} LIKE ?"
        lead = [squashed]
        if match:
            finds = ("(f.id IN (SELECT rowid FROM files_fts "
                     f"WHERE files_fts MATCH ?) OR {finds})")
            lead = [match, squashed]
        like_where = " AND ".join([finds] + ([where] if where else []))
        sql = f"""
            SELECT f.title_norm, 0 AS rank, 0 AS starts
            FROM files f
            WHERE {like_where}
            GROUP BY f.title_norm
            ORDER BY LENGTH(f.title_norm), f.title_norm
            LIMIT ? OFFSET ?
        """
        args = [*lead, *params, limit, offset]
        count_sql = f"""
            SELECT COUNT(DISTINCT f.title_norm) FROM files f WHERE {like_where}
        """
        count_args = [*lead, *params]
    elif match:
        # bm25() only works where files_fts is queried directly. MATERIALIZED
        # stops SQLite flattening this CTE back into the join, which would put
        # bm25 in a context it refuses to run in.
        # Groups are ranked by their single best-matching file, and titles
        # that actually start with what was typed float to the top.
        sql = f"""
            WITH hits AS MATERIALIZED (
                SELECT rowid AS fid, bm25(files_fts, 10.0, 1.0) AS rank
                FROM files_fts WHERE files_fts MATCH ?
            )
            SELECT f.title_norm,
                   MIN(h.rank) AS rank,
                   MIN(CASE WHEN f.title_norm = ?    THEN 0
                            WHEN f.title_norm LIKE ? THEN 1
                            ELSE 2 END) AS starts
            FROM hits h
            JOIN files f ON f.id = h.fid
            {'WHERE ' + where if where else ''}
            GROUP BY f.title_norm
            ORDER BY starts ASC, rank ASC
            LIMIT ? OFFSET ?
        """
        norm = normalize_title(query)
        args = [match, norm, norm + "%", *params, limit, offset]
        count_sql = f"""
            SELECT COUNT(DISTINCT f.title_norm)
            FROM files_fts JOIN files f ON f.id = files_fts.rowid
            WHERE files_fts MATCH ? {'AND ' + where if where else ''}
        """
        count_args = [match, *params]
    else:
        sql = f"""
            SELECT f.title_norm, 0 AS rank, 0 AS starts
            FROM files f
            {'WHERE ' + where if where else ''}
            GROUP BY f.title_norm
            ORDER BY f.title_norm
            LIMIT ? OFFSET ?
        """
        args = [*params, limit, offset]
        count_sql = f"""
            SELECT COUNT(DISTINCT f.title_norm) FROM files f
            {'WHERE ' + where if where else ''}
        """
        count_args = list(params)

    try:
        norms = [r["title_norm"] for r in conn.execute(sql, args)]
        total = conn.execute(count_sql, count_args).fetchone()[0]
    except sqlite3.OperationalError as exc:
        # Usually a malformed FTS expression from odd input; log it so a real
        # query bug can't hide behind an innocent-looking empty result.
        print(f"[romsrx] search failed for {query!r}: {exc}", file=sys.stderr)
        return {"total": 0, "groups": []}

    facet_counts = search_facets(conn, query, console=console, region=region,
                                 ext=ext, source=source, ra=ra,
                                 plan=(match, squashed))
    if not norms:
        return {"total": total, "groups": [], "facets": facet_counts}

    grouped = groups_for(conn, norms, where=where, params=params)
    return {
        "total": total,
        "groups": grouped,
        "facets": facet_counts,
    }


def groups_for(conn: sqlite3.Connection, norms: list[str], *,
               where: str = "", params: list | None = None) -> list[dict]:
    """The games behind these normalised titles, each with all of its copies.

    Split out of search() because a search is not the only thing that arrives
    holding a list of titles and wanting the games: ordering the whole of
    RetroAchievements by how short its sets are produces a list of titles and
    nothing else, and the games behind them have to be assembled the same way
    a search assembles them or the two would draw differently.

    Answers in the order the titles were given, so a caller that has already
    decided the order keeps it.
    """
    if not norms:
        return []
    params = list(params or [])
    # Read once for this whole answer rather than per row: it is a settings
    # file, and the ordering has to be the same for the SQL and the badges.
    regions = region_order()
    placeholders = ",".join("?" * len(norms))
    file_sql = f"""
        SELECT {FILE_COLUMNS}
        FROM files f
        JOIN sources s ON s.id = f.source_id
        WHERE f.title_norm IN ({placeholders})
        {'AND ' + where if where else ''}
        ORDER BY s.console_rank, f.console, {region_rank_sql(regions)},
                 f.regions, f.title, f.disc, f.filename
    """
    rows = conn.execute(file_sql, [*norms, *params]).fetchall()

    grouped: dict[str, dict] = {n: {"title_norm": n, "title": "", "files": []}
                                for n in norms}
    for row in rows:
        group = grouped[row["title_norm"]]
        item = dict(row)
        item["regions"] = [r for r in row["regions"].split(",") if r]
        item["languages"] = [l for l in row["languages"].split(",") if l]
        item["tags"] = [t for t in row["tags"].split("|") if t]
        group["files"].append(item)

    for group in grouped.values():
        if group["files"]:
            # Shortest title is usually the cleanest form of the name.
            group["title"] = min((f["title"] for f in group["files"]), key=len)
            # Files arrive already sorted, so first appearance gives the
            # console badges the same order as the rows below them.
            group["consoles"] = list(dict.fromkeys(
                f["console"] for f in group["files"]))
            group["regions"] = sorted({r for f in group["files"]
                                       for r in f["regions"]},
                                      key=lambda n: region_sort_key(n, regions))
            group["sources"] = sorted({f["source_name"] for f in group["files"]})

    return [g for g in grouped.values() if g["files"]]


def _matched_from(match: str, squashed: str, where: str) -> str:
    """FROM/WHERE clause selecting every file matching a query and filters.

    No bm25 here, so joining files_fts directly is fine. Arguments go in the
    order they appear: the MATCH sits in a join that is written before the
    WHERE, so it is bound first.
    """
    if squashed:
        # The same "either" shape search() uses, so the facet counts describe
        # the result set the user is actually looking at.
        finds = f"{SQUASHED} LIKE ?"
        if match:
            finds = ("(f.id IN (SELECT rowid FROM files_fts "
                     f"WHERE files_fts MATCH ?) OR {finds})")
        clauses = [finds] + ([where] if where else [])
        return f"FROM files f WHERE {' AND '.join(clauses)}"
    if match:
        return f"""
            FROM files f
            JOIN (SELECT rowid AS fid FROM files_fts WHERE files_fts MATCH ?)
                 h ON f.id = h.fid
            {'WHERE ' + where if where else ''}
        """
    return f"FROM files f {'WHERE ' + where if where else ''}"


def search_facets(conn: sqlite3.Connection, query: str = "", *, console=None,
                  region=None, ext=None, source=None, ra=False,
                  plan=None) -> dict:
    """Facet counts for the current result set, in distinct games.

    Each dimension is counted with the *other* dimensions' filters applied but
    not its own, so selecting 'PSP' doesn't collapse the console list to just
    PSP — you can still see and pick the alternatives.
    """
    # search() has already worked out how to look this query up; anyone
    # calling this on its own gets the same answer, one probe later.
    match, squashed = plan if plan is not None else _plan(conn, query)

    def scoped(exclude: str) -> tuple[str, list]:
        # `ra` narrows every dimension, the same way `source` does - it isn't
        # one of the dropdowns, so it is never the excluded one.
        where, params = _filter_sql(
            None if exclude == "console" else console,
            None if exclude == "region" else region,
            None if exclude == "ext" else ext,
            source, ra,
        )
        base = _matched_from(match, squashed, where)
        return base, ([match] if match else []) + (
            [squashed] if squashed else []) + params

    def counted(column: str, exclude: str) -> list[dict]:
        base, args = scoped(exclude)
        sql = (f"SELECT f.{column} AS value, "
               f"COUNT(DISTINCT f.title_norm) AS count {base} "
               f"GROUP BY f.{column} ORDER BY count DESC")
        return [dict(r) for r in conn.execute(sql, args)
                if r["value"]]

    try:
        consoles = counted("console", "console")
        extensions = counted("ext", "ext")

        # Regions live in a comma-joined column, so tally them in Python.
        base, args = scoped("region")
        seen: dict[str, set[str]] = {}
        for regions, title in conn.execute(
                f"SELECT f.regions, f.title_norm {base}", args):
            for name in regions.split(","):
                if name:
                    seen.setdefault(name, set()).add(title)
        region_counts = sorted(
            ({"value": k, "count": len(v)} for k, v in seen.items()),
            key=lambda d: (-d["count"], d["value"]))
    except sqlite3.OperationalError as exc:
        print(f"[romsrx] facets failed for {query!r}: {exc}", file=sys.stderr)
        return {"consoles": [], "regions": [], "extensions": []}

    return {"consoles": consoles, "regions": region_counts,
            "extensions": extensions}


def file_filter(console=None, region=None, ext=None, source=None,
                ra=False) -> tuple[str, list]:
    """The WHERE fragment and parameters these filters come to.

    For callers that assemble their own query around groups_for - the
    whole-site orders do - so the copies they list are narrowed by the same
    bar a search is narrowed by, written once here rather than twice.
    """
    return _filter_sql(console, region, ext, source, ra)


def plan_for(conn: sqlite3.Connection, query: str) -> tuple[str, str]:
    """How this query will be looked up, so a caller running several queries
    over it pays for working that out once."""
    return _plan(conn, query)


def scope_of(conn: sqlite3.Connection, query: str = "", *, console=None,
             region=None, ext=None, source=None, ra=False,
             plan=None) -> set[tuple[str, str]]:
    """{(console, title_norm)} for every game a search would find.

    The whole-site orders - shortest sets, quickest to beat, quickest to
    master - rank a pool built from RetroAchievements' own lists rather than
    from a search, so nothing about them passed through the search box or the
    filter bar: picking "quickest to beat" threw away the word you had typed
    and ignored the region you had chosen. This is the missing half. The
    ranking still happens over the pool, but only over the part of it you are
    actually looking at.

    Consoles ride along with the titles because the pool is per console - one
    game with a set on two machines is two sets with two different times - and
    a region filter can perfectly well be satisfied on one of them and not the
    other. Matching on the title alone would let a console back in through a
    filter that had excluded it.

    A search with nothing typed and nothing picked matches everything, and
    callers are expected to skip this rather than pay for a table scan that
    can only answer "all of it".
    """
    match, squashed = plan if plan is not None else _plan(conn, query)
    where, params = _filter_sql(console, region, ext, source, ra)
    base = _matched_from(match, squashed, where)
    args = ([match] if match else []) + ([squashed] if squashed else []) + params
    try:
        rows = conn.execute(f"SELECT DISTINCT f.console, f.title_norm {base}",
                            args)
        return {(str(c or ""), str(n or "")) for c, n in rows}
    except sqlite3.OperationalError as exc:
        print(f"[romsrx] scope failed for {query!r}: {exc}", file=sys.stderr)
        return set()


def consoles_for_titles(conn: sqlite3.Connection,
                        titles: list[str]) -> dict[str, dict[str, set[str]]]:
    """Which consoles the index has each of these game names on.

    A game sitting loose in the download folder has no console folder to be
    named by, so the library calls it "Unsorted" - honest, and useless when it
    is most of the library. The index already knows what machine a game is
    for, and the game's own name is enough to ask.

    Returns name -> {"": every console it appears on, ext: those offered with
    that extension}. The split matters because archive.org serves most sets as
    .zip but PlayStation ones as .chd, so the extension sometimes narrows a
    name that appears on several machines and sometimes says nothing at all.
    """
    unique = sorted({t for t in titles if t})
    if not unique:
        return {}

    found: dict[str, dict[str, set[str]]] = {}
    for start in range(0, len(unique), 400):     # SQLite caps the parameters
        chunk = unique[start:start + 400]
        marks = ",".join("?" * len(chunk))
        rows = conn.execute(
            f"SELECT DISTINCT title_norm, ext, console FROM files "  # noqa: S608
            f"WHERE title_norm IN ({marks})", chunk)
        for title, ext, console in rows:
            if not console:
                continue
            slot = found.setdefault(title, {})
            slot.setdefault("", set()).add(console)
            slot.setdefault(str(ext or "").lstrip(".").lower(), set()).add(console)
    return found


def facets(conn: sqlite3.Connection) -> dict:
    """Distinct filter values, each with a file count, for the UI dropdowns."""
    consoles = [dict(r) for r in conn.execute(
        "SELECT console AS value, COUNT(*) AS count FROM files "
        "GROUP BY console ORDER BY console")]
    exts = [dict(r) for r in conn.execute(
        "SELECT ext AS value, COUNT(*) AS count FROM files "
        "WHERE ext <> '' GROUP BY ext ORDER BY count DESC")]

    region_counts: dict[str, int] = {}
    for (regions,) in conn.execute(
            "SELECT regions FROM files WHERE regions <> ''"):
        for region in regions.split(","):
            if region:
                region_counts[region] = region_counts.get(region, 0) + 1
    regions = [{"value": k, "count": v} for k, v in
               sorted(region_counts.items(), key=lambda kv: -kv[1])]

    return {"consoles": consoles, "regions": regions, "extensions": exts}


def stats(conn: sqlite3.Connection) -> dict:
    row = conn.execute(
        "SELECT COUNT(*) AS files, COALESCE(SUM(size), 0) AS bytes, "
        "COUNT(DISTINCT title_norm) AS games FROM files").fetchone()
    sources = [dict(r) for r in conn.execute(
        "SELECT * FROM sources ORDER BY console_rank, console, name")]
    return {
        "files": row["files"],
        "games": row["games"],
        "bytes": row["bytes"],
        "sources": sources,
    }
