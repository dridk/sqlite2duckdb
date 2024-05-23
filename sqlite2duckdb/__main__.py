import duckdb 
import argparse 
import os
from sqlite2duckdb import sqlite_to_duckdb, __VERSION__

def main_cli():
    
    parser = argparse.ArgumentParser(description='Convert Sqlite database to Duckdb database', usage="sqlite2duckdb <sqlite_path> <duckdb_path>")

    parser.add_argument('sqlite_path', type=str, help='sqlite file path')
    parser.add_argument('duckdb_path', type=str, help='duckdb file path')
    parser.add_argument("-v", "--version", action="version", version=f"sqlite2duckdb {__VERSION__}")

    # Analyser les arguments
    args = parser.parse_args()

    if os.path.exists(args.duckdb_path):
        delete_input = input(f"{args.duckdb_path} already exists. do you want to delete this file ? (yes/no): ").strip().lower()
        if delete_input in ("yes", "y"):
            os.remove(args.duckdb_path)
        else:
            exit(1)
    sqlite_to_duckdb(args.sqlite_path, args.duckdb_path)


if __name__ == "__main__":

    main_cli()
