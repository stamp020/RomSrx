"""Command line entry point: `python -m romsrx [serve|index|stats]`."""

from __future__ import annotations

import argparse
from datetime import datetime

from . import db, indexer, paths, server


def human_size(num: float) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if abs(num) < 1024 or unit == "TB":
            return f"{num:.1f} {unit}" if unit != "B" else f"{num:.0f} B"
        num /= 1024
    return f"{num:.1f} TB"


def main() -> None:
    parser = argparse.ArgumentParser(prog="romsrx", description=__doc__)
    sub = parser.add_subparsers(dest="command")

    p_serve = sub.add_parser("serve", help="run the local web app (default)")
    p_serve.add_argument("--host", default="127.0.0.1")
    p_serve.add_argument("--port", type=int, default=8770)

    p_index = sub.add_parser("index", help="fetch file lists from archive.org")
    p_index.add_argument("--only", nargs="+", metavar="ID",
                         help="limit to source ids, consoles, or identifiers")
    p_index.add_argument("--workers", type=int, default=4)

    p_check = sub.add_parser(
        "checksources",
        help="see which sources archive.org will answer for, without indexing")
    p_check.add_argument("--only", nargs="+", metavar="ID",
                         help="limit to source ids, consoles, or identifiers")
    p_check.add_argument("--workers", type=int, default=8)
    p_check.add_argument("--timeout", type=int, default=45)

    sub.add_parser("stats", help="show what is currently indexed")
    sub.add_parser("app", help="open the desktop app window")

    args = parser.parse_args()
    command = args.command or "serve"

    if command == "app":
        from . import app as desktop
        desktop.main()
        return

    if command == "serve":
        server.serve(getattr(args, "host", "127.0.0.1"),
                     getattr(args, "port", 8770))
        return

    if command == "checksources":
        # Kept as well as printed, because a packaged build has no console to
        # print to - double-clicked or not, `RomSrx.exe checksources` has
        # nowhere to put its output but a file.
        lines: list[str] = []

        def say(text=""):
            lines.append(str(text))
            print(text)

        config = indexer.load_config()
        report = indexer.check_sources(config, only=args.only,
                                       workers=args.workers,
                                       timeout=args.timeout,
                                       progress=say)
        tally = report["tally"]
        say(f"\n{report['items']} item(s) behind {report['sources']} source(s): "
            f"{tally['ok']} answered, {tally['empty']} empty, "
            f"{tally['gone']} gone, {tally['unreachable']} unreachable.")

        for state, note in (("unreachable", "could not be reached"),
                            ("gone", "no longer on archive.org"),
                            ("empty", "there, but holding no files")):
            rows = [r for r in report["results"] if r["state"] == state]
            if not rows:
                continue
            say(f"\n{note}:")
            for row in rows:
                extra = f"  ({row['detail']})" if row["detail"] else ""
                say(f"  {row['identifier']}{extra}")
                for label in row["sources"]:
                    say(f"      {label}")

        # The point of running this at all is usually "is it me or is it
        # them", so answer that rather than leaving a table to interpret.
        #
        # What decides it is not how many failed but how they failed. An item
        # that is not on archive.org says so promptly; it does not sit there
        # until the connection gives up. So a timeout is a statement about the
        # network, and only a clean refusal is a statement about the source.
        unreachable = [r for r in report["results"] if r["state"] == "unreachable"]
        timed_out = [r for r in unreachable if "time" in r["detail"].lower()]
        say()
        if not unreachable:
            say("Everything answered. A slow index is not the connection "
                  "being refused - it is the amount there is to fetch.")
        elif len(timed_out) >= max(1, len(unreachable) // 2):
            say(f"{len(timed_out)} of {len(unreachable)} unreachable item(s) "
                  "timed out rather than answering. Something missing answers "
                  "quickly, so this is the connection - usually archive.org "
                  "throttling - and not the sources. Indexing now will be slow: "
                  "each of those is tried three times before it is given up on. "
                  "The same check an hour later normally comes back clean.")
        else:
            say("These were refused outright rather than timing out, which "
                  "points at the sources themselves. Worth running once more "
                  "before removing any - this asks a single time and does not "
                  "retry, so one bad moment is enough to list one.")
        if report["items"] < 5:
            say("\n(Only a few were checked. Run it without --only for a "
                  "reading on the connection as a whole.)")

        report_file = paths.user("sources-check.txt")
        try:
            stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            report_file.write_text(f"RomSrx source check, {stamp}\n\n"
                                   + "\n".join(lines) + "\n", encoding="utf-8")
            print(f"\nWritten to {report_file}")
        except OSError as exc:
            print(f"\n(could not write the report: {exc})")
        return

    conn = db.connect()
    if command == "index":
        config = indexer.load_config()
        summary = indexer.index_all(conn, config, only=args.only,
                                    workers=args.workers)
        counts = db.stats(conn)
        print(f"\nIndexed {summary['files']:,} files "
              f"({summary['ok']} ok, {summary['failed']} failed).")
        print(f"Database now holds {counts['games']:,} distinct games / "
              f"{counts['files']:,} files, {human_size(counts['bytes'])}.")
        for err in summary["errors"]:
            print(f"  ! {err}")
    elif command == "stats":
        counts = db.stats(conn)
        print(f"{counts['games']:,} games / {counts['files']:,} files / "
              f"{human_size(counts['bytes'])}\n")
        for source in counts["sources"]:
            flag = "!" if source["last_error"] else " "
            print(f" {flag} {source['console']:>4}  {source['name']:<32} "
                  f"{source['file_count']:>6,} files  "
                  f"{human_size(source['total_size']):>9}")
            if source["last_error"]:
                print(f"       error: {source['last_error']}")
    conn.close()


if __name__ == "__main__":
    main()
