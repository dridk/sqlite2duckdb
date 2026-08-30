import sqlite3 
import duckdb 
from tests import utils
import os 

from sqlite2duckdb import sqlite_to_duckdb

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

def test_quoted_table_names():

	duckdb_path = utils.generate_fake_duckdb()
	sqlite_path = utils.generate_edge_case_sqlite()

	sqlite_to_duckdb(sqlite_path, duckdb_path)

	d_conn = duckdb.connect(duckdb_path)
	tables = {table[0] for table in d_conn.sql("SHOW TABLES").fetchall()}

	assert {"users", "my table", "order"} <= tables

	assert d_conn.sql('SELECT * FROM "my table"').fetchall() == [(1, "x")]
	assert d_conn.sql('SELECT * FROM "order"').fetchall() == [(7,)]

def test_constraints_preserved():

	duckdb_path = utils.generate_fake_duckdb()
	sqlite_path = utils.generate_edge_case_sqlite()

	sqlite_to_duckdb(sqlite_path, duckdb_path)

	d_conn = duckdb.connect(duckdb_path)

	constraints = {
		row[0]
		for row in d_conn.sql(
			"SELECT constraint_type FROM duckdb_constraints() WHERE table_name = 'users'"
		).fetchall()
	}

	assert "PRIMARY KEY" in constraints
	assert "NOT NULL" in constraints

	indexes = {
		row[0] for row in d_conn.sql("SELECT index_name FROM duckdb_indexes()").fetchall()
	}

	assert "idx_users_age" in indexes

def test_bracket_quoted_view():
	"""Regression test for issue #3: a view whose SQL uses [bracket] identifiers
	cannot be parsed by duckdb, which used to break table discovery."""

	duckdb_path = utils.generate_fake_duckdb()
	sqlite_path = utils.generate_bracket_sqlite()

	sqlite_to_duckdb(sqlite_path, duckdb_path)

	d_conn = duckdb.connect(duckdb_path)

	assert d_conn.sql('SELECT * FROM "Order Details" ORDER BY OrderID').fetchall() == [
		(1, 5),
		(2, 7),
	]
