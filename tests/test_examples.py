"""Integration test against the real chinook database shipped in examples/.

The synthetic fixtures cover the mechanisms one at a time; this one checks the
whole conversion on a database nobody wrote for the tests. Chinook quotes its
DDL with [brackets], which duckdb's parser rejects.
"""

import sqlite3
from pathlib import Path

import duckdb
import pytest

from sqlite2duckdb import sqlite_to_duckdb

CHINOOK = Path(__file__).resolve().parent.parent / "examples" / "chinook.sqlite.db"

pytestmark = pytest.mark.skipif(
    not CHINOOK.exists(), reason="examples/chinook.sqlite.db is not available"
)


@pytest.fixture(scope="module")
def chinook(tmp_path_factory):
    target = tmp_path_factory.mktemp("chinook") / "chinook.duckdb"
    result = sqlite_to_duckdb(CHINOOK, target)

    return result, duckdb.connect(str(target)), sqlite3.connect(CHINOOK)


def test_every_table_is_copied(chinook):
    result, d_conn, s_conn = chinook

    expected = {
        row[0]
        for row in s_conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
    }
    converted = {row[0] for row in d_conn.sql("SHOW TABLES").fetchall()}

    assert converted == expected
    assert result.tables == len(expected)


def test_every_row_is_copied(chinook):
    _, d_conn, s_conn = chinook

    for (table,) in s_conn.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name"
    ).fetchall():
        query = f'SELECT COUNT(*) FROM "{table}"'

        assert d_conn.sql(query).fetchone() == s_conn.execute(query).fetchone(), table


def test_values_are_unchanged(chinook):
    _, d_conn, s_conn = chinook

    query = "SELECT AlbumId, Title, ArtistId FROM albums ORDER BY AlbumId"
    duck_rows = d_conn.sql(query).fetchall()

    assert duck_rows == s_conn.execute(query).fetchall()
    assert duck_rows[0] == (1, "For Those About To Rock We Salute You", 1)


def test_bracket_quoted_indexes_are_recreated(chinook):
    _, d_conn, s_conn = chinook

    expected = {
        row[0]
        for row in s_conn.execute(
            "SELECT name FROM sqlite_master WHERE type = 'index' AND sql IS NOT NULL"
        )
    }
    converted = {
        row[0]
        for row in d_conn.sql("SELECT index_name FROM duckdb_indexes()").fetchall()
    }

    assert expected <= converted
    assert "IFK_AlbumArtistId" in converted


def test_constraints_are_preserved(chinook):
    _, d_conn, _ = chinook

    constraints = {
        (row[0], row[1])
        for row in d_conn.sql(
            "SELECT table_name, constraint_type FROM duckdb_constraints()"
        ).fetchall()
    }

    assert ("albums", "PRIMARY KEY") in constraints
    assert ("albums", "NOT NULL") in constraints
