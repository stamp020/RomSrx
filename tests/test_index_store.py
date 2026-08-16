"""Where the index lives, and how it gets into and out of a backup.

This is the one part of the app that touches a large file the user cannot
easily replace - rebuilding it means fetching every source from archive.org
again. So the moving, snapshotting and restoring are all exercised here on
throwaway copies rather than discovered on a real one.

Nothing here touches the network.
"""
import io
import json
import sqlite3
import sys
import tempfile
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from romsrx import db, state  # noqa: E402

ok = fail = 0


def check(label, got, want):
    global ok, fail  # noqa: PLW0603
    if got == want:
        ok += 1
        print(f"  pass  {label}")
    else:
        fail += 1
        print(f"  FAIL  {label}\n          got  {got!r}\n          want {want!r}")


root = Path(tempfile.mkdtemp(prefix="romsrx-index-"))


def make_db(path, rows=5, leave_in_wal=False):
    """A small database. Optionally with rows still only in the sidecar."""
    conn = sqlite3.connect(path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("CREATE TABLE IF NOT EXISTS games (name TEXT)")
    conn.commit()
    conn.executemany("INSERT INTO games VALUES (?)",
                     [(f"game {i}",) for i in range(rows)])
    conn.commit()
    if leave_in_wal:
        # Held open, unchecked-pointed: the rows are committed but still live
        # in the -wal file, exactly as they do while the app is running.
        return conn
    conn.close()
    return None


def count(path):
    """Rows in the copy, or None if it is not a usable database."""
    try:
        conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    except sqlite3.Error:
        return None
    try:
        return conn.execute("SELECT count(*) FROM games").fetchone()[0]
    except sqlite3.Error:
        return None       # no table, or the file is not finished being one
    finally:
        conn.close()


# --- a snapshot must include what is still in the sidecar ------------------
# This is the whole reason the backup does not just copy the file.
live = root / "live.db"
held = make_db(live, rows=7, leave_in_wal=True)

plain_copy = root / "plain-copy.db"
plain_copy.write_bytes(live.read_bytes())      # what copying the file gets you

snapped = root / "snapshot.db"
check("snapshot succeeds while the app holds the file", db.snapshot(snapped, live), True)
check("the snapshot has every row", count(snapped), 7)
# Copying the bytes gets a file that is not the database: with the writes
# still in the sidecar, even the table is missing from it.
check("copying the file instead gets an unusable one",
      (count(plain_copy) != 7, Path(str(live) + "-wal").is_file()), (True, True))
held.close()

check("snapshotting something that is not there says so",
      db.snapshot(root / "out.db", root / "nothing.db"), False)

# --- moving an index out of the folder beside the .exe ---------------------
old_home = root / "beside-the-exe"
new_home = root / "user-folder"
old_home.mkdir()
new_home.mkdir()
make_db(old_home / db.DB_NAME, rows=3)
(old_home / (db.DB_NAME + "-wal")).write_bytes(b"sidecar")
(old_home / (db.DB_NAME + "-shm")).write_bytes(b"sidecar")

real_data = db.data
db.data = lambda name: old_home / name          # pretend that is where it was
try:
    db._migrate_from_exe_folder(new_home / db.DB_NAME)  # noqa: SLF001
finally:
    db.data = real_data

check("the index moves to the user folder", (new_home / db.DB_NAME).is_file(), True)
check("and is left intact", count(new_home / db.DB_NAME), 3)
check("the sidecars come with it",
      [(new_home / (db.DB_NAME + s)).is_file() for s in db.DB_SIDECARS], [True, True])
check("nothing is left behind", (old_home / db.DB_NAME).exists(), False)

# An index already in the user folder is never overwritten by an older one.
make_db(old_home / db.DB_NAME, rows=99)
db.data = lambda name: old_home / name
try:
    db._migrate_from_exe_folder(new_home / db.DB_NAME)  # noqa: SLF001
finally:
    db.data = real_data
check("an index already in place is left alone", count(new_home / db.DB_NAME), 3)

# --- a restored index is picked up on the next start -----------------------
target = root / "adopt.db"
make_db(target, rows=2)
(Path(str(target) + "-wal")).write_bytes(b"stale")
make_db(Path(str(target) + db.RESTORE_SUFFIX), rows=42)

db._adopt_restored(target)  # noqa: SLF001
# Checked before anything opens it: opening a WAL database makes SQLite
# create the sidecar again, so asking afterwards proves nothing.
check("the stale sidecar is cleared",
      Path(str(target) + "-wal").exists(), False)
check("the staging file is gone",
      Path(str(target) + db.RESTORE_SUFFIX).exists(), False)
check("the restored index takes its place", count(target), 42)
check("with nothing waiting, the index is untouched",
      (db._adopt_restored(target), count(target))[1], 42)  # noqa: SLF001

# --- the index in and out of a backup zip ---------------------------------
user_dir = root / "backup-user"
user_dir.mkdir()
(user_dir / "prefs.json").write_text("{}", encoding="utf-8")
index_path = user_dir / db.DB_NAME
make_db(index_path, rows=11)

real_db_path, real_state_path = db.DB_PATH, state._path  # noqa: SLF001
db.DB_PATH = index_path
state._path = lambda name: user_dir / f"{name}.json"  # noqa: SLF001
try:
    with_index = root / "with-index.zip"
    without = root / "without-index.zip"
    state.write_backup(str(with_index), ["settings", "index"])
    state.write_backup(str(without), ["settings"])

    inside = zipfile.ZipFile(with_index).namelist()
    check("ticking it puts the index in the backup", db.DB_NAME in inside, True)
    check("leaving it out keeps it out",
          db.DB_NAME in zipfile.ZipFile(without).namelist(), False)
    check("the backup says which parts it holds",
          "index" in json.loads(
              zipfile.ZipFile(with_index).read(state.BACKUP_MARK))["parts"], True)

    # Restoring must not write over the index this process has open.
    before = count(index_path)
    result = state.read_backup(str(with_index))
    check("restoring reports success", result["ok"], True)
    check("the live index is untouched", count(index_path), before)
    staged = user_dir / (db.DB_NAME + db.RESTORE_SUFFIX)
    check("the restored index waits to one side", staged.is_file(), True)
    check("and holds what was backed up", count(staged), 11)
finally:
    db.DB_PATH, state._path = real_db_path, real_state_path  # noqa: SLF001

import shutil  # noqa: E402

shutil.rmtree(root, ignore_errors=True)
print(f"\n{ok} passed, {fail} failed")
