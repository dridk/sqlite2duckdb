import duckdb
import os
import sqlite3
import time


def sqlite_to_duckdb(sqlite_db: str, duck_db: str):
    print(f"Create {duck_db} databases")

    if not os.path.exists(sqlite_db):
        raise Exception(f"File {sqlite_db} doesn't exists")

    # Remove target db if exists
    if os.path.exists(duck_db):
        raise Exception(f"Database {duck_db} already exists")

    # Create databases

    start_time = time.perf_counter()
    conn = duckdb.connect(duck_db)
    db_name = conn.sql("SELECT database_name FROM duckdb_databases").fetchone()[0]

    ## Install sqlite
    conn.sql("INSTALL sqlite; LOAD sqlite;")

    # Bound parameters are not allowed in ATTACH, so escape the quotes ourselves
    source_path = sqlite_db.replace("'", "''")
    conn.sql(f"ATTACH '{source_path}' AS __other (TYPE SQLITE, READ_ONLY)")

    ## Get sqlite Names
    tables = conn.sql(
        "SELECT table_name FROM duckdb_tables WHERE database_name = '__other'"
    ).fetchall()
    print(f"{len(tables)} tables found(s)")

    # Copy tables, data, constraints and indexes at once
    conn.sql(f'COPY FROM DATABASE __other TO "{db_name}"')

    conn.sql("DETACH __other")
    conn.close()
    end_time = time.perf_counter()
    execution_time = (end_time - start_time) * 1000
    print(f"Done in {execution_time:.2f} ms !")
