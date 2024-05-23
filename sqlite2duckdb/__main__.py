import duckdb 
import argparse 
import os

def sqlite2duckdb(sqlite_db:str, duck_db:str):

    print(f"Create {duck_db} databases")

    # Remove database if exists
    if os.path.exists(duck_db):
        raise Exception(f"Database {duck_db} already exists")

    # Create databases 
    conn = duckdb.connect(duck_db)
    db_name = conn.sql("SELECT database_name FROM duckdb_databases").fetchone()[0]

    ## Install sqlite
    conn.sql(f"""
    INSTALL sqlite;
    LOAD sqlite;
    ATTACH '{sqlite_db}' as __other;
    """)

    ## Get sqlite Names 
    conn.sql("USE __other")
    tables = [i[0] for i  in conn.sql("SHOW tables").fetchall()]
    print(f"{len(tables)} tables found(s)")
    conn.sql(f"USE {db_name}")

    # Create tables     
    for table in tables:
        print(f"Create duckdb table {table}")
        conn.sql(f"CREATE TABLE {table} AS select * FROM __other.{table}")

    conn.sql(f"DETACH __other")
    conn.close()
    print("Done!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert Sqlite database to Duckdb database')

    parser.add_argument('sqlite_path', type=str, help='sqlite file path')
    parser.add_argument('duckdb_path', type=str, help='duckdb file path')


    # Analyser les arguments
    args = parser.parse_args()

    if os.path.exists(args.duckdb_path):
        delete_input = input(f"{args.duckdb_path} already exists. do you want to delete this file ? (yes/no): ").strip().lower()
        if delete_input in ("yes", "y"):
            os.remove(args.duckdb_path)
        else:
            exit(1)

        

        
    sqlite2duckdb(args.sqlite_path, args.duckdb_path)
