import sqlite3 
import duckdb 
from tests import utils
import os 

from sqlite2duckdb.__main__ import sqlite_to_duckdb

def test_conversion():

	duckdb_path = utils.generate_fake_duckdb()
	sqlite_path = utils.generate_fake_sqlite()

	sqlite_to_duckdb(sqlite_path, duckdb_path)


def test_count():
		
	duckdb_path = utils.generate_fake_duckdb()
	sqlite_path = utils.generate_fake_sqlite()

	sqlite_to_duckdb(sqlite_path, duckdb_path)


	d_conn = duckdb.connect(duckdb_path)
	s_conn = sqlite3.connect(sqlite_path)

	for table in d_conn.sql("SHOW TABLES").fetchall():
		table_name = table[0]

		query = f"SELECT COUNT(*) FROM {table_name}"

		duckdb_count = d_conn.sql(query).fetchone()
		sqlite_count = s_conn.execute(query).fetchone()

		assert duckdb_count == sqlite_count

	
	
	
