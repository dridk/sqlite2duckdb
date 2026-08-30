"""Views and UNIQUE constraints, which duckdb's sqlite extension does not expose
on an attached database and which have to be read back from sqlite_master."""

import logging

import duckdb
import pytest

from sqlite2duckdb import sqlite_to_duckdb


def test_views_are_copied(views_sqlite, duckdb_path):
    result = sqlite_to_duckdb(views_sqlite, duckdb_path)

    d_conn = duckdb.connect(str(duckdb_path))

    assert d_conn.sql("SELECT * FROM by_region ORDER BY region").fetchall() == [
        ("north", 15),
        ("south", 7),
    ]
    assert result.views == 3


def test_view_built_on_another_view(views_sqlite, duckdb_path):
    sqlite_to_duckdb(views_sqlite, duckdb_path)

    d_conn = duckdb.connect(str(duckdb_path))

    assert d_conn.sql("SELECT * FROM big_regions").fetchall() == [("north",)]


def test_bracket_quoted_view_is_translated(views_sqlite, duckdb_path):
    sqlite_to_duckdb(views_sqlite, duckdb_path)

    d_conn = duckdb.connect(str(duckdb_path))

    assert d_conn.sql('SELECT COUNT(*) FROM "north sales"').fetchone() == (2,)


def test_view_duckdb_cannot_parse_is_skipped_with_a_warning(
    views_sqlite, duckdb_path, caplog
):
    with caplog.at_level(logging.WARNING, logger="sqlite2duckdb.sqlite_to_duckdb"):
        sqlite_to_duckdb(views_sqlite, duckdb_path)

    assert "matched" in caplog.text

    d_conn = duckdb.connect(str(duckdb_path))
    views = {
        row[0]
        for row in d_conn.sql(
            "SELECT view_name FROM duckdb_views() WHERE NOT internal"
        ).fetchall()
    }

    assert "matched" not in views
    # The rest of the database must still be intact.
    assert d_conn.sql("SELECT COUNT(*) FROM sales").fetchone() == (3,)


def test_unique_constraints_are_enforced(unique_sqlite, duckdb_path):
    sqlite_to_duckdb(unique_sqlite, duckdb_path)

    d_conn = duckdb.connect(str(duckdb_path))

    # Column level UNIQUE, recorded by sqlite as an autoindex with no SQL.
    with pytest.raises(duckdb.ConstraintException):
        d_conn.sql("INSERT INTO members VALUES (2, 'ada@example.com', 'x', 'y')")

    # Table level UNIQUE over two columns.
    with pytest.raises(duckdb.ConstraintException):
        d_conn.sql(
            "INSERT INTO members VALUES (3, 'other@example.com', 'ada', 'lovelace')"
        )

    # An explicit CREATE UNIQUE INDEX, which does carry its SQL.
    with pytest.raises(duckdb.ConstraintException):
        d_conn.sql("INSERT INTO members VALUES (4, 'x@example.com', 'x', 'lovelace')")


def test_non_unique_rows_still_insert(unique_sqlite, duckdb_path):
    sqlite_to_duckdb(unique_sqlite, duckdb_path)

    d_conn = duckdb.connect(str(duckdb_path))
    d_conn.sql("INSERT INTO members VALUES (5, 'grace@example.com', 'grace', 'hopper')")

    assert d_conn.sql("SELECT COUNT(*) FROM members").fetchone() == (2,)
