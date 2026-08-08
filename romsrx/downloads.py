"""Background download queue with resume, retry and progress reporting.

Downloads run in worker threads inside this app - no browser involved. Files
are written to a `.part` file and renamed on completion, so an interrupted
transfer resumes from where it stopped instead of starting over.

archive.org intermittently answers 500 on perfectly valid requests (the same
URL will succeed moments later), so transient failures are retried with a
backoff rather than being treated as fatal.
"""

from __future__ import annotations

import json
import os
import queue
import re
import shutil
import subprocess
import sys
import threading
import time
import zipfile
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

from . import paths as _paths
from . import state

CHUNK = 256 * 1024
RETRIES = 5
RETRY_BASE = 2.0          # seconds; doubles each attempt
TRANSIENT = {408, 425, 429, 500, 502, 503, 504}
_paths.migrate_user_files(("settings.json", "covers.json"))
SETTINGS_PATH = _paths.user("settings.json")
DEFAULT_FOLDER = str(Path.home() / "Downloads" / "RomSrx")

# How many downloads may run at once. archive.org rate-limits heavy use, so
# more connections mostly buy errors and retries rather than speed.
MAX_WORKERS = 5
DEFAULT_WORKERS = 3

# Only formats we can unpack without an external binary. Everything else in
# the index (chd, iso, wbfs, rvz, wad) is already the playable ROM.
ARCHIVES = {".zip", ".7z"}

_INVALID = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


def safe_name(name: str) -> str:
    """Make a filename Windows-safe without mangling the readable parts."""
    cleaned = _INVALID.sub("_", name).strip(" .")
    return cleaned or "download"


def load_settings() -> dict:
    try:
        with open(SETTINGS_PATH, encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError):
        data = {}
    data.setdefault("folder", DEFAULT_FOLDER)
    data.setdefault("workers", 3)
    data.setdefault("extract", True)
    data.setdefault("delete_archive", True)
    data.setdefault("per_console", False)   # base/<console> automatically
    data.setdefault("console_folders", {})  # explicit per-console overrides
    data.setdefault("clear_when_done", False)  # tidy the list as things land
    data["workers"] = _sane_workers(data["workers"])
    return data


def _sane_workers(value) -> int:
    """Always one of the choices the app offers.

    Older builds allowed up to 10, and a 0 meaning "unlimited". Both are still
    sitting in settings files, and either would leave the control showing
    nothing - so they land on the nearest thing that still exists.
    """
    try:
        workers = int(value)
    except (TypeError, ValueError):
        return DEFAULT_WORKERS
    if workers <= 0:            # the old "unlimited": as many as we now allow
        return MAX_WORKERS
    return min(workers, MAX_WORKERS)


_cart_lock = threading.Lock()


def forget_from_cart(url: str) -> None:
    """Drop a finished download from the saved list, if that's switched on.

    Done here rather than in the page so it still happens for downloads that
    finish while the list isn't open - and the lock is because several workers
    can finish at the same moment, and the list is a whole-file rewrite.
    """
    if not load_settings().get("clear_when_done"):
        return
    with _cart_lock:
        items = state.cart()
        keep = [i for i in items if i.get("url") != url]
        if len(keep) != len(items):
            state.set_cart(keep)


def console_dir_name(console: str) -> str:
    """A console name as a folder name. Several contain a slash, which would
    otherwise create an unintended nested folder."""
    return safe_name(console.replace("/", "-").replace("\\", "-"))


def relative_to_base(path: str, base: str) -> str:
    """Store a path inside the base folder as a relative one.

    Keeping it relative means the whole library moves when the main folder
    changes, instead of every console staying pinned to the old location.
    Paths outside the base are left absolute on purpose.
    """
    try:
        target, root = Path(path), Path(base)
        if target.is_absolute() and root.is_absolute():
            return str(target.relative_to(root))
    except (ValueError, OSError):
        pass
    return path


def folder_for(console: str) -> Path:
    """Where a file for this console should land.

    An override wins - relative ones hang off the base folder, absolute ones
    point wherever they say. Otherwise per-console mode appends the console
    name to the base, and failing that everything shares the base.
    """
    settings = load_settings()
    base = Path(settings["folder"])
    override = (settings.get("console_folders") or {}).get(console)
    if override:
        chosen = Path(override)
        return chosen if chosen.is_absolute() else base / chosen
    if settings.get("per_console") and console:
        return base / console_dir_name(console)
    return base


def save_settings(data: dict) -> dict:
    current = load_settings()
    allowed = ("folder", "workers", "extract", "delete_archive", "per_console",
               "clear_when_done")
    current.update({k: v for k, v in data.items() if k in allowed})
    if "console_folders" in data and isinstance(data["console_folders"], dict):
        # Blank entries mean "fall back to the default", so drop them. Anything
        # inside the base folder is stored relative so it follows the base.
        base = current["folder"]
        current["console_folders"] = {
            k: relative_to_base(str(v).strip(), base)
            for k, v in data["console_folders"].items() if str(v).strip()
        }
    current["per_console"] = bool(current["per_console"])
    current["extract"] = bool(current["extract"])
    current["delete_archive"] = bool(current["delete_archive"])
    current["clear_when_done"] = bool(current["clear_when_done"])
    current["workers"] = _sane_workers(current["workers"])
    with open(SETTINGS_PATH, "w", encoding="utf-8") as fh:
        json.dump(current, fh, indent=2)
    manager.ensure_workers(current["workers"])
    return current


def browse_folder(start: str = "") -> str | None:
    """Native folder picker. Runs Tk on its own thread so it can't clash
    with the app's UI loop; returns None if the user cancels."""
    result: list[str | None] = [None]

    def ask():
        try:
            import tkinter  # noqa: PLC0415
            from tkinter import filedialog  # noqa: PLC0415
            root = tkinter.Tk()
            root.withdraw()
            root.attributes("-topmost", True)
            chosen = filedialog.askdirectory(
                initialdir=start or load_settings()["folder"],
                title="Choose where to save downloads")
            root.destroy()
            result[0] = chosen or None
        except Exception:  # noqa: BLE001 - no display, no tkinter, cancelled
            result[0] = None

    thread = threading.Thread(target=ask)
    thread.start()
    thread.join(timeout=180)
    return result[0]


def _remove_file(path: Path, attempts: int = 12, delay: float = 0.25) -> bool:
    """Delete a file, allowing for Windows holding it briefly.

    A worker closes its handle a moment after it stops, and Windows refuses
    to unlink an open file, so a single attempt can fail on a race.
    """
    for _ in range(attempts):
        try:
            if not path.exists():
                return False
            path.unlink()
            return True
        except OSError:
            time.sleep(delay)
    return False


def browse_image(start: str = "") -> str | None:
    """Native file picker for choosing a cover image."""
    result: list[str | None] = [None]

    def ask():
        try:
            import tkinter  # noqa: PLC0415
            from tkinter import filedialog  # noqa: PLC0415
            root = tkinter.Tk()
            root.withdraw()
            root.attributes("-topmost", True)
            chosen = filedialog.askopenfilename(
                initialdir=start or str(Path.home()),
                title="Choose a cover image",
                filetypes=[("Images", "*.png *.jpg *.jpeg *.webp *.gif *.bmp"),
                           ("All files", "*.*")])
            root.destroy()
            result[0] = chosen or None
        except Exception:  # noqa: BLE001 - cancelled or no display
            result[0] = None

    thread = threading.Thread(target=ask)
    thread.start()
    thread.join(timeout=180)
    return result[0]


def browse_save(suggested: str = "cover.png") -> str | None:
    """Native "save as" picker, for saving an image out of the app.

    The window has no browser chrome, so the right-click > save people expect
    on a picture has to be offered by the app itself.
    """
    result: list[str | None] = [None]
    pictures = Path.home() / "Pictures"

    def ask():
        try:
            import tkinter  # noqa: PLC0415
            from tkinter import filedialog  # noqa: PLC0415
            root = tkinter.Tk()
            root.withdraw()
            root.attributes("-topmost", True)
            suffix = Path(suggested).suffix or ".png"
            chosen = filedialog.asksaveasfilename(
                initialdir=str(pictures if pictures.is_dir() else Path.home()),
                initialfile=suggested,
                defaultextension=suffix,
                title="Save cover image",
                filetypes=[("Images", "*.png *.jpg *.jpeg *.webp"),
                           ("All files", "*.*")])
            root.destroy()
            result[0] = chosen or None
        except Exception:  # noqa: BLE001 - cancelled or no display
            result[0] = None

    thread = threading.Thread(target=ask)
    thread.start()
    thread.join(timeout=180)
    return result[0]


# Where box art comes from. The frontend builds these URLs; this is the only
# host they may point at.
THUMBNAIL_HOST = "thumbnails.libretro.com"
MAX_IMAGE = 8 * 1024 * 1024


def fetch_image(url: str) -> bytes:
    """Download one cover from the thumbnail server.

    The URL arrives from the page and is fetched by the app on the user's
    machine, so it is pinned to that one host rather than trusted as given.
    """
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "https" or parsed.hostname != THUMBNAIL_HOST:
        raise ValueError("Only cover images can be saved.")

    request = urllib.request.Request(url, headers={"User-Agent": "RomSrx/0.1"})
    with urllib.request.urlopen(request, timeout=30) as response:  # noqa: S310
        data = response.read(MAX_IMAGE + 1)
    if len(data) > MAX_IMAGE:
        raise ValueError("That image is too large to save.")
    return data


def reveal(path: str) -> bool:
    """Show a finished download in the system file manager.

    Only Windows and macOS can highlight the file itself; everywhere else the
    best on offer is opening the folder it sits in.
    """
    target = Path(path)
    if not target.exists():
        target = target.parent
        if not target.exists():
            return False
    try:
        if sys.platform == "win32":
            if target.is_dir():
                os.startfile(target)  # noqa: S606
            else:
                subprocess.Popen(["explorer", "/select,", str(target)])  # noqa: S607
        elif sys.platform == "darwin":
            subprocess.Popen(["open", "-R", str(target)])  # noqa: S607
        else:
            folder = target if target.is_dir() else target.parent
            subprocess.Popen(["xdg-open", str(folder)])  # noqa: S607
        return True
    except Exception:  # noqa: BLE001 - no file manager, or none we can drive
        return False


@dataclass
class Job:
    id: int
    url: str
    filename: str
    console: str = ""
    source: str = ""
    total: int = 0
    done: int = 0
    status: str = "queued"      # queued|running|paused|extracting|done|error
    error: str = ""
    speed: float = 0.0          # bytes/sec, smoothed
    path: str = ""              # what "open folder" should reveal
    extracted: str = ""         # folder the archive was unpacked into
    attempts: int = 0
    added: float = field(default_factory=time.time)
    finished: float = 0.0
    # Where this sits in the wait list; lower goes first. Defaults to the job
    # id, so left alone the queue is plain first-come-first-served.
    order: float = 0.0

    def snapshot(self) -> dict:
        pct = (self.done / self.total * 100) if self.total else 0.0
        remaining = max(self.total - self.done, 0)
        eta = remaining / self.speed if self.speed > 1 and remaining else 0
        return {
            "id": self.id, "filename": self.filename, "console": self.console,
            "source": self.source, "status": self.status, "error": self.error,
            "done": self.done, "total": self.total, "percent": round(pct, 1),
            "speed": round(self.speed), "eta": round(eta), "path": self.path,
            "extracted": self.extracted, "attempts": self.attempts,
        }


class Slots:
    """How many downloads may be in flight at once.

    This is what makes the queue roll: a worker takes the next job off the
    queue but only starts it once a slot is free, and a slot frees the instant
    a download finishes, so the next one begins immediately.

    It isn't a plain semaphore because the limit has to be able to *drop*
    while downloads are running - a semaphore can't be resized, which is why
    choosing a smaller number used to do nothing until the app restarted.
    Lowering it never interrupts anything: what is already running finishes,
    and nothing new starts until the number in flight is back under the limit.
    """

    def __init__(self, limit: int) -> None:
        self._cv = threading.Condition()
        self._limit = max(1, limit)
        self._used = 0

    def set_limit(self, limit: int) -> None:
        with self._cv:
            self._limit = max(1, limit)
            self._cv.notify_all()

    def acquire(self) -> None:
        with self._cv:
            while self._used >= self._limit:
                self._cv.wait()
            self._used += 1

    def release(self) -> None:
        with self._cv:
            self._used = max(0, self._used - 1)
            self._cv.notify_all()

    @property
    def in_flight(self) -> int:
        with self._cv:
            return self._used


class Manager:
    """Owns the queue, the workers and the job table."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._jobs: dict[int, Job] = {}
        self._queue: queue.Queue[int] = queue.Queue()
        # job id -> why it should stop ("paused" or "cancelled"). A paused job
        # keeps its .part file and can be put back on the queue as-is.
        self._stop: dict[int, str] = {}
        self._next_id = 1
        self._workers: list[threading.Thread] = []
        self._slots = Slots(DEFAULT_WORKERS)
        self._started = False

    # -- session ---------------------------------------------------------
    def _session(self):
        """An authenticated requests session when available, else None."""
        try:
            from internetarchive import get_session  # noqa: PLC0415
            return get_session()
        except Exception:  # noqa: BLE001 - fall back to urllib
            return None

    # -- public API ------------------------------------------------------
    def start(self) -> None:
        self.ensure_workers(load_settings()["workers"])

    def ensure_workers(self, wanted: int) -> None:
        """Set how many downloads run at once, and make sure there are enough
        threads to reach it.

        Raising it starts more immediately. Lowering it stops the newest
        downloads and puts them at the front of the queue, so the number
        actually running matches what was asked for rather than only applying
        to whatever starts next.
        """
        self._started = True
        target = _sane_workers(wanted)
        self._slots.set_limit(target)

        with self._lock:
            alive = [t for t in self._workers if t.is_alive()]
            self._workers = alive
            missing = max(0, target - len(alive))
            # Newest first: the ones furthest down the panel are the ones the
            # user expects to give way, and they have the least to lose.
            running = sorted((j for j in self._jobs.values()
                              if j.status == "running"),
                             key=lambda j: j.id, reverse=True)
            excess = running[:max(0, len(running) - target)]

        for _ in range(missing):
            thread = threading.Thread(target=self._worker, daemon=True)
            thread.start()
            self._workers.append(thread)

        # They keep their .part file, so each carries on from where it stopped
        # once a slot frees up again.
        for job in excess:
            self.requeue(job.id, front=True)

    def job(self, job_id: int) -> Job | None:
        with self._lock:
            return self._jobs.get(job_id)

    def add(self, items: list[dict]) -> list[int]:
        added = []
        with self._lock:
            existing = {j.url for j in self._jobs.values()
                        if j.status in ("queued", "running")}
            for item in items:
                url = (item.get("url") or "").strip()
                if not url or url in existing:
                    continue
                job = Job(
                    id=self._next_id, url=url,
                    filename=safe_name(item.get("filename") or "download"),
                    console=item.get("console", ""), source=item.get("source", ""),
                    total=int(item.get("size") or 0),
                    order=float(self._next_id),
                )
                self._jobs[job.id] = job
                self._next_id += 1
                existing.add(url)
                added.append(job.id)
        for job_id in added:
            self._queue.put(job_id)
        if added:
            self.start()
            self._persist()
        return added

    def _halt(self, job_id: int, reason: str) -> bool:
        with self._lock:
            job = self._jobs.get(job_id)
            if not job or job.status in ("done", "paused", "cancelled"):
                return False
            self._stop[job_id] = reason
            if job.status == "queued":
                # Never started, so settle it here rather than waiting for a
                # worker to pick it up.
                job.status = reason
                job.speed = 0.0
                self._stop.pop(job_id, None)
        self._persist()
        return True

    def pause(self, job_id: int) -> bool:
        return self._halt(job_id, "paused")

    def cancel(self, job_id: int) -> bool:
        return self._halt(job_id, "cancelled")

    def start_next(self, job_id: int) -> bool:
        """Send a waiting download to the front of the queue.

        It doesn't push anything aside - it takes the next slot that frees up,
        which is what `requeue` on a running one is for.
        """
        with self._lock:
            job = self._jobs.get(job_id)
            if not job or job.status != "queued":
                return False
            first = min((j.order for j in self._jobs.values()), default=0.0)
            job.order = first - 1.0
        self._persist()
        return True

    def requeue(self, job_id: int, front: bool = False) -> bool:
        """Send a running download back to the wait list, freeing its slot.

        The .part file stays put, so when its turn comes round again it picks
        up from where it stopped rather than starting over.

        `front` puts it next in line instead of last: that is for downloads
        pushed aside by lowering the limit, which should be the first back on
        when it is raised again - they were already part-way through.
        """
        with self._lock:
            job = self._jobs.get(job_id)
            if not job or job.status not in ("running", "queued"):
                return False
            if job.status == "queued":
                return True          # already waiting, nothing to do
            if front:
                job.order = min((j.order for j in self._jobs.values()),
                                default=0.0) - 1.0
            else:
                job.order = max((j.order for j in self._jobs.values()),
                                default=0.0) + 1.0
            # The worker notices this and settles the job as "queued"; it also
            # puts the token back, so something picks it up again later.
            self._stop[job_id] = "queued"
        self._persist()
        return True

    def resume(self, job_id: int) -> bool:
        """Put a paused job back on the queue; it picks up from its .part."""
        with self._lock:
            job = self._jobs.get(job_id)
            if not job or job.status not in ("paused", "cancelled", "error"):
                return False
            self._stop.pop(job_id, None)
            job.status = "queued"
            job.error = ""
            job.attempts = 0
        self._queue.put(job_id)
        self.start()
        self._persist()
        return True

    def discard(self, job_id: int) -> dict:
        """Remove a stopped job *and* whatever it left on disk.

        Cancelling keeps the .part file so the download can resume later; this
        is the way to say you don't want it after all. Refused while a job is
        still active, since a worker would be writing to that file.
        """
        with self._lock:
            job = self._jobs.get(job_id)
            if job is None:
                return {"removed": False, "reason": "no such download"}
            active = job.status in ("running", "queued", "extracting")
            if active:
                self._stop[job_id] = "cancelled"

        # Let the worker notice and release the file before we delete it.
        if active:
            for _ in range(60):
                with self._lock:
                    job = self._jobs.get(job_id)
                    if not job or job.status not in ("running", "queued", "extracting"):
                        break
                time.sleep(0.1)

        with self._lock:
            job = self._jobs.get(job_id)
            if job is None:
                return {"removed": True, "deleted": []}
            path, extracted = job.path, job.extracted

        deleted = []
        if path:
            final = Path(path)
            for candidate in (final, Path(f"{final}.part")):
                if _remove_file(candidate):
                    deleted.append(candidate.name)
        if extracted:
            try:
                folder = Path(extracted)
                if folder.is_dir():
                    shutil.rmtree(folder, ignore_errors=True)
                    deleted.append(folder.name + "/")
            except OSError:
                pass

        with self._lock:
            self._jobs.pop(job_id, None)
            # The stop flag is deliberately left in place. A worker that
            # hasn't reached its next chunk yet still needs to see it -
            # clearing it here would leave the thread downloading forever
            # for a job that no longer exists, holding the file open.
        self._persist()
        return {"removed": True, "deleted": deleted}

    def pause_all(self) -> int:
        with self._lock:
            ids = [i for i, j in self._jobs.items()
                   if j.status in ("running", "queued", "extracting")]
        return sum(1 for i in ids if self.pause(i))

    def resume_all(self) -> int:
        with self._lock:
            ids = [i for i, j in self._jobs.items()
                   if j.status in ("paused", "cancelled", "error")]
        return sum(1 for i in ids if self.resume(i))

    def discard_all(self) -> dict:
        """Stop everything and delete what it left on disk.

        Done in one pass rather than by calling discard() per job. That
        version waits up to six seconds for each active download to let go of
        its file and rewrites the queue afterwards - fine once, but with a
        full list it meant minutes of waiting in series and one whole-file
        write per entry. Here everything is told to stop at once, waited for
        once, and saved once.
        """
        with self._lock:
            jobs = list(self._jobs.values())
            transferring = []
            for job in jobs:
                if job.status in ("running", "extracting"):
                    # A worker is holding this file; it has to be asked.
                    self._stop[job.id] = "cancelled"
                    transferring.append(job)
                elif job.status == "queued":
                    # Settled here and now. Waiting for a worker to do it
                    # would hang forever: `_take_next` skips anything already
                    # flagged to stop, so a cancelled queued job is never
                    # picked up and never changes state.
                    job.status = "cancelled"
                    job.speed = 0.0

        # One wait for all the transfers, not one each.
        if transferring:
            deadline = time.monotonic() + 6.0
            while time.monotonic() < deadline:
                with self._lock:
                    busy = [j for j in transferring
                            if j.id in self._jobs
                            and self._jobs[j.id].status in
                            ("running", "extracting")]
                if not busy:
                    break
                time.sleep(0.05)

        deleted = []
        for job in jobs:
            if job.path:
                final = Path(job.path)
                for candidate in (final, Path(f"{final}.part")):
                    if _remove_file(candidate):
                        deleted.append(candidate.name)
            if job.extracted:
                try:
                    folder = Path(job.extracted)
                    if folder.is_dir():
                        shutil.rmtree(folder, ignore_errors=True)
                        deleted.append(folder.name + "/")
                except OSError:
                    pass

        with self._lock:
            for job in jobs:
                self._jobs.pop(job.id, None)
            # Stop flags stay: a worker that hasn't reached its next chunk
            # still needs to see one, or it would download on forever for a
            # job that no longer exists.
        self._persist()
        return {"removed": len(jobs), "deleted": deleted}

    def clear_finished(self) -> int:
        with self._lock:
            # Paused jobs are deliberately kept - they're unfinished business.
            gone = [i for i, j in self._jobs.items()
                    if j.status in ("done", "cancelled", "error")]
            for i in gone:
                self._jobs.pop(i, None)
                self._stop.pop(i, None)
        self._persist()
        return len(gone)

    # -- persistence -----------------------------------------------------
    PERSIST_FIELDS = ("id", "url", "filename", "console", "source", "total",
                      "done", "status", "path", "extracted", "error", "added",
                      "order")

    def _persist(self) -> None:
        """Remember the queue so closing the app doesn't lose it."""
        with self._lock:
            rows = [{f: getattr(job, f) for f in self.PERSIST_FIELDS}
                    for job in self._jobs.values()]
        state.save("queue", rows)

    def restore(self) -> int:
        """Reload the queue from disk. Anything mid-flight comes back paused -
        its .part file is still there, so it can pick up where it stopped."""
        rows = state.load("queue", [])
        with self._lock:
            for row in rows:
                if not isinstance(row, dict) or not row.get("url"):
                    continue
                job = Job(id=int(row.get("id") or 0), url=row["url"],
                          filename=row.get("filename", "download"))
                for field in self.PERSIST_FIELDS:
                    if field in row and field not in ("id", "url", "filename"):
                        setattr(job, field, row[field])
                if job.status in ("running", "queued", "extracting"):
                    job.status = "paused"
                if not job.order:      # written before the wait list had order
                    job.order = float(job.id)
                job.speed = 0.0
                self._jobs[job.id] = job
                self._next_id = max(self._next_id, job.id + 1)
            return len(self._jobs)

    def snapshot(self) -> dict:
        with self._lock:
            waiting = sorted((j for j in self._jobs.values()
                              if j.status == "queued"),
                             key=lambda j: (j.order, j.id))
            places = {job.id: n for n, job in enumerate(waiting, 1)}
            jobs = [j.snapshot() for j in self._jobs.values()]
        # Where each waiting download sits in the queue, so the panel can say
        # which one is up next after you reorder them.
        for job in jobs:
            job["place"] = places.get(job["id"], 0)
        active = [j for j in jobs if j["status"] == "running"]
        return {
            "jobs": sorted(jobs, key=lambda j: j["id"]),
            "active": len(active),
            "queued": len(waiting),
            "speed": round(sum(j["speed"] for j in active)),
            "folder": load_settings()["folder"],
        }

    # -- worker ----------------------------------------------------------
    def _take_next(self) -> Job | None:
        """Claim whichever queued job should go next, or None if none can.

        The job is chosen here rather than being whichever id came off the
        queue, so the wait list can be reordered without rebuilding it. What
        comes off the queue is only a token saying "there is work"; tokens are
        interchangeable, and there is always one per waiting job.
        """
        with self._lock:
            waiting = [j for j in self._jobs.values()
                       if j.status == "queued" and j.id not in self._stop]
            if not waiting:
                return None
            job = min(waiting, key=lambda j: (j.order, j.id))
            job.status = "running"
            return job

    def _worker(self) -> None:
        session = self._session()
        while True:
            self._queue.get()          # a token: something is waiting
            job = None
            try:
                # Wait for a free slot *before* claiming anything, so the panel
                # never shows more in flight than the limit allows. Releasing
                # the slot below is what lets the next one start the moment
                # this download is finished with.
                self._slots.acquire()
                try:
                    job = self._take_next()
                    if job is None:
                        continue       # another worker got there first
                    self._run(job, session)
                    if job.status == "done":
                        forget_from_cart(job.url)
                    elif job.status == "queued":
                        # Sent back to the wait list; put its token back.
                        self._queue.put(job.id)
                finally:
                    self._slots.release()
            except Exception as exc:  # noqa: BLE001 - a worker must not die
                with self._lock:
                    if job is not None:
                        job.status = "error"
                        job.error = str(exc)[:300]
            finally:
                self._queue.task_done()
                self._persist()   # capture the finished/failed state

    def _open(self, session, url: str, offset: int):
        """Range request from `offset`. Returns (response, is_partial)."""
        headers = {"User-Agent": "RomSrx/0.1"}
        if offset:
            headers["Range"] = f"bytes={offset}-"
        if session is not None:
            resp = session.get(url, headers=headers, stream=True, timeout=60)
            if resp.status_code in TRANSIENT:
                resp.close()
                raise urllib.error.HTTPError(url, resp.status_code,
                                             "transient", None, None)
            resp.raise_for_status()
            return resp, resp.status_code == 206
        request = urllib.request.Request(url, headers=headers)
        resp = urllib.request.urlopen(request, timeout=60)
        return resp, resp.status == 206

    def _run(self, job: Job, session) -> None:
        folder = folder_for(job.console)
        folder.mkdir(parents=True, exist_ok=True)
        final = folder / job.filename
        part = folder / (job.filename + ".part")
        job.path = str(final)

        if final.exists() and final.stat().st_size > 0:
            with self._lock:
                job.done = job.total = final.stat().st_size
                job.status = "done"
                job.finished = time.time()
                job.error = "already downloaded"
            return

        for attempt in range(1, RETRIES + 1):
            job.attempts = attempt
            offset = part.stat().st_size if part.exists() else 0
            try:
                resp, partial = self._open(session, job.url, offset)
            except Exception as exc:  # noqa: BLE001
                if attempt == RETRIES:
                    with self._lock:
                        job.status = "error"
                        job.error = f"{type(exc).__name__}: {str(exc)[:200]}"
                    return
                time.sleep(RETRY_BASE * attempt)
                continue

            # Server ignored our Range - start the file again.
            if offset and not partial:
                offset = 0
                part.unlink(missing_ok=True)

            total = self._content_length(resp, offset)
            with self._lock:
                job.done = offset
                if total:
                    job.total = total

            try:
                self._stream(job, resp, part, offset)
            except _Stopped:
                with self._lock:
                    job.status = self._stop.pop(job.id, "cancelled")
                    job.speed = 0.0
                return
            except Exception as exc:  # noqa: BLE001 - retry transient drops
                if attempt == RETRIES:
                    with self._lock:
                        job.status = "error"
                        job.error = f"{type(exc).__name__}: {str(exc)[:200]}"
                    return
                time.sleep(RETRY_BASE * attempt)
                continue
            finally:
                try:
                    resp.close()
                except Exception:  # noqa: BLE001, S110
                    pass

            # Finished cleanly.
            part.replace(final)
            with self._lock:
                job.done = job.total = final.stat().st_size
                job.speed = 0.0
                job.path = str(final)
            self._maybe_extract(job, final)
            with self._lock:
                job.status = "done"
                job.finished = time.time()
            return

    def _maybe_extract(self, job: Job, archive: Path) -> None:
        """Unpack zip/7z into a folder beside it, then drop the archive."""
        settings = load_settings()
        if not settings["extract"] or archive.suffix.lower() not in ARCHIVES:
            return

        dest = archive.with_suffix("")
        with self._lock:
            job.status = "extracting"
            job.speed = 0.0
        try:
            dest.mkdir(parents=True, exist_ok=True)
            if archive.suffix.lower() == ".zip":
                with zipfile.ZipFile(archive) as zf:
                    zf.extractall(dest)
            else:
                import py7zr  # noqa: PLC0415
                with py7zr.SevenZipFile(archive, "r") as sz:
                    sz.extractall(dest)
        except Exception as exc:  # noqa: BLE001 - keep the archive if this fails
            with self._lock:
                job.error = f"downloaded, but extraction failed: {str(exc)[:150]}"
                job.path = str(archive)
            return

        with self._lock:
            job.extracted = str(dest)
            job.path = str(dest)

        if settings["delete_archive"]:
            try:
                archive.unlink()
            except OSError as exc:
                with self._lock:
                    job.error = f"extracted, but could not delete archive: {exc}"

    @staticmethod
    def _content_length(resp, offset: int) -> int:
        headers = getattr(resp, "headers", {})
        rng = headers.get("Content-Range")
        if rng and "/" in rng:
            try:
                return int(rng.rsplit("/", 1)[1])
            except ValueError:
                pass
        try:
            return int(headers.get("Content-Length") or 0) + offset
        except (TypeError, ValueError):
            return 0

    def _stream(self, job: Job, resp, part: Path, offset: int) -> None:
        chunks = (resp.iter_content(CHUNK) if hasattr(resp, "iter_content")
                  else iter(lambda: resp.read(CHUNK), b""))
        written = offset
        last_t, last_b = time.time(), offset

        with open(part, "ab" if offset else "wb") as fh:
            for chunk in chunks:
                if job.id in self._stop:
                    raise _Stopped
                if not chunk:
                    continue
                fh.write(chunk)
                written += len(chunk)

                now = time.time()
                if now - last_t >= 0.5:
                    rate = (written - last_b) / (now - last_t)
                    with self._lock:
                        # Smooth it so the UI doesn't flicker.
                        job.speed = rate if not job.speed else job.speed * 0.7 + rate * 0.3
                        job.done = written
                    last_t, last_b = now, written

        with self._lock:
            job.done = written


class _Stopped(Exception):
    """Raised inside the stream loop when a job is paused or cancelled."""


manager = Manager()
