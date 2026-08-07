"""Command line entry point: `python -m romsrx [serve|index|stats]`."""

from __future__ import annotations

import argparse

from . import db, indexer, server


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
