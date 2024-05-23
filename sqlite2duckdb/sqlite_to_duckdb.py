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
    conn.sql(
        f"""
    INSTALL sqlite;
    LOAD sqlite;
    ATTACH '{sqlite_db}' as __other;
    """
    )

    ## Get sqlite Names
    conn.sql("USE __other")
    tables = [i[0] for i in conn.sql("SHOW tables").fetchall()]
    print(f"{len(tables)} tables found(s)")
    conn.sql(f"USE {db_name}")

    # Create tables
    for table in tables:
        print(f"Create duckdb table {table}")
        conn.sql(f"CREATE TABLE {table} AS select * FROM __other.{table}")

    conn.sql(f"DETACH __other")
    conn.close()
    end_time = time.perf_counter()
    execution_time = (end_time - start_time) * 1000
    print(f"Done in {execution_time:.2f} ms !")
