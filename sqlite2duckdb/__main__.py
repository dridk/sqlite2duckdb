from __future__ import annotations

import argparse
import logging
import os
import sys

from sqlite2duckdb import __version__, sqlite_to_duckdb


def main_cli() -> int:
    parser = argparse.ArgumentParser(
        prog="sqlite2duckdb",
        description="Convert Sqlite database to Duckdb database",
        usage="sqlite2duckdb [-f] <sqlite_path> <duckdb_path>",
    )

    parser.add_argument("sqlite_path", type=str, help="sqlite file path")
    parser.add_argument("duckdb_path", type=str, help="duckdb file path")
    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="overwrite the duckdb file if it already exists",
    )
    parser.add_argument("-q", "--quiet", action="store_true", help="only report errors")
    parser.add_argument("--verbose", action="store_true", help="report every step")
    parser.add_argument(
        "-v", "--version", action="version", version=f"sqlite2duckdb {__version__}"
    )

    args = parser.parse_args()

    if args.quiet:
        level = logging.WARNING
    elif args.verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO
    # Progress goes to stderr so that stdout stays free for pipelines.
    logging.basicConfig(level=level, format="%(message)s", stream=sys.stderr)

    overwrite = args.force
    if not overwrite and os.path.exists(args.duckdb_path):
        if not sys.stdin.isatty():
            print(
                f"{args.duckdb_path} already exists. Use --force to overwrite it.",
                file=sys.stderr,
            )
            return 1
        try:
            answer = (
                input(
                    f"{args.duckdb_path} already exists. do you want to delete this file ? (yes/no): "
                )
                .strip()
                .lower()
            )
        except EOFError:
            print(f"{args.duckdb_path} already exists.", file=sys.stderr)
            return 1
        if answer not in ("yes", "y"):
            return 1
        overwrite = True

    try:
        sqlite_to_duckdb(args.sqlite_path, args.duckdb_path, overwrite=overwrite)
    except (FileNotFoundError, FileExistsError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main_cli())
