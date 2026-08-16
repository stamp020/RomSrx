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
REGION_RANK_SQL = """
    CASE
        WHEN (',' || f.regions || ',') LIKE '%,USA,%'    THEN 0
        WHEN (',' || f.regions || ',') LIKE '%,Europe,%' THEN 1
        WHEN f.regions = ''                              THEN 3
        ELSE 2
    END
"""


def region_sort_key(name: str) -> tuple[int, str]:
    """Python-side twin of REGION_RANK_SQL, for ordering badge lists."""
    return ({"USA": 0, "Europe": 1}.get(name, 2), name)




_TOKEN_RE = re.compile(r"\w+", re.UNICODE)


def build_match_query(query: str) -> str:
    """Turn free text into an FTS5 MATCH expression with prefix matching.

    'final fant' becomes '"final"* AND "fant"*', so partial words still hit.
    """
    tokens = _TOKEN_RE.findall(normalize_title(query))
    if not tokens:
        return ""
    return " AND ".join(f'"{t}"*' for t in tokens)


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
    match = build_match_query(query)

    if match:
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
                                 ext=ext, source=source, ra=ra)
    if not norms:
        return {"total": total, "groups": [], "facets": facet_counts}

    placeholders = ",".join("?" * len(norms))
    file_sql = f"""
        SELECT {FILE_COLUMNS}
        FROM files f
        JOIN sources s ON s.id = f.source_id
        WHERE f.title_norm IN ({placeholders})
        {'AND ' + where if where else ''}
        ORDER BY s.console_rank, f.console, {REGION_RANK_SQL},
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
                                      key=region_sort_key)
            group["sources"] = sorted({f["source_name"] for f in group["files"]})

    return {
        "total": total,
        "groups": [g for g in grouped.values() if g["files"]],
        "facets": facet_counts,
    }


def _matched_from(match: str, where: str) -> str:
    """FROM/WHERE clause selecting every file matching a query and filters.

    No bm25 here, so joining files_fts directly is fine.
    """
    if match:
        return f"""
            FROM files f
            JOIN (SELECT rowid AS fid FROM files_fts WHERE files_fts MATCH ?)
                 h ON f.id = h.fid
            {'WHERE ' + where if where else ''}
        """
    return f"FROM files f {'WHERE ' + where if where else ''}"


def search_facets(conn: sqlite3.Connection, query: str = "", *, console=None,
                  region=None, ext=None, source=None, ra=False) -> dict:
    """Facet counts for the current result set, in distinct games.

    Each dimension is counted with the *other* dimensions' filters applied but
    not its own, so selecting 'PSP' doesn't collapse the console list to just
    PSP — you can still see and pick the alternatives.
    """
    match = build_match_query(query)

    def scoped(exclude: str) -> tuple[str, list]:
        # `ra` narrows every dimension, the same way `source` does - it isn't
        # one of the dropdowns, so it is never the excluded one.
        where, params = _filter_sql(
            None if exclude == "console" else console,
            None if exclude == "region" else region,
            None if exclude == "ext" else ext,
            source, ra,
        )
        base = _matched_from(match, where)
        return base, ([match] if match else []) + params

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
