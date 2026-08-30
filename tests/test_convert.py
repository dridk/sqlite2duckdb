import sqlite3

import duckdb
import pytest

from sqlite2duckdb import ConversionResult, sqlite_to_duckdb
from tests import utils


def test_conversion(fake_sqlite, duckdb_path):
    result = sqlite_to_duckdb(fake_sqlite, duckdb_path)

    assert isinstance(result, ConversionResult)
    assert result.target == str(duckdb_path)
    assert result.tables == 1
    assert result.elapsed > 0
    assert duckdb_path.exists()


def test_count(fake_sqlite, duckdb_path):
    sqlite_to_duckdb(fake_sqlite, duckdb_path)

    d_conn = duckdb.connect(str(duckdb_path))
    s_conn = sqlite3.connect(fake_sqlite)

    tables = d_conn.sql("SHOW TABLES").fetchall()
    assert tables

    for (table_name,) in tables:
        query = f'SELECT COUNT(*) FROM "{table_name}"'

        assert d_conn.sql(query).fetchone() == s_conn.execute(query).fetchone()


def test_value_fidelity(fidelity_sqlite, duckdb_path):
    """Values must come back identical, not merely in the right number."""

    sqlite_to_duckdb(fidelity_sqlite, duckdb_path)

    d_conn = duckdb.connect(str(duckdb_path))
    s_conn = sqlite3.connect(fidelity_sqlite)

    query = "SELECT * FROM roundtrip ORDER BY id"
    duck_rows = d_conn.sql(query).fetchall()

    assert duck_rows == s_conn.execute(query).fetchall()
    assert duck_rows == utils.FIDELITY_ROWS


def test_quoted_table_names(edge_case_sqlite, duckdb_path):
    sqlite_to_duckdb(edge_case_sqlite, duckdb_path)

    d_conn = duckdb.connect(str(duckdb_path))
    tables = {table[0] for table in d_conn.sql("SHOW TABLES").fetchall()}

    assert {"users", "my table", "order"} <= tables

    assert d_conn.sql('SELECT * FROM "my table"').fetchall() == [(1, "x")]
    assert d_conn.sql('SELECT * FROM "order"').fetchall() == [(7,)]


def test_constraints_preserved(edge_case_sqlite, duckdb_path):
    sqlite_to_duckdb(edge_case_sqlite, duckdb_path)

    d_conn = duckdb.connect(str(duckdb_path))

    constraints = {
        row[0]
        for row in d_conn.sql(
            "SELECT constraint_type FROM duckdb_constraints() WHERE table_name = 'users'"
        ).fetchall()
    }

    assert "PRIMARY KEY" in constraints
    assert "NOT NULL" in constraints

    indexes = {
        row[0]
        for row in d_conn.sql("SELECT index_name FROM duckdb_indexes()").fetchall()
    }

    assert "idx_users_age" in indexes


def test_bracket_quoted_view(bracket_sqlite, duckdb_path):
    """Regression test for issue #3: a view whose SQL uses [bracket] identifiers
    cannot be parsed by duckdb, which used to break table discovery."""

    sqlite_to_duckdb(bracket_sqlite, duckdb_path)

    d_conn = duckdb.connect(str(duckdb_path))

    assert d_conn.sql('SELECT * FROM "Order Details" ORDER BY OrderID').fetchall() == [
        (1, 5),
        (2, 7),
    ]

    # The bracket quoted view built on it comes across too.
    assert d_conn.sql(
        'SELECT * FROM "Order Subtotals" ORDER BY OrderID'
    ).fetchall() == [(1, 5), (2, 7)]


def test_dotted_column_names(dotted_column_sqlite, duckdb_path):
    """Regression test for issue #4: a STRICT table with numeric-looking column
    names used to fail with `Parser Error: syntax error at or near ".1"`."""

    sqlite_to_duckdb(dotted_column_sqlite, duckdb_path)

    d_conn = duckdb.connect(str(duckdb_path))

    assert d_conn.sql('SELECT "2.3.4", "1e5" FROM measures').fetchall() == [
        (42, "hello")
    ]


def test_empty_database(empty_sqlite, duckdb_path):
    result = sqlite_to_duckdb(empty_sqlite, duckdb_path)

    assert result.tables == 0
    assert duckdb_path.exists()


def test_missing_source_raises(tmp_path, duckdb_path):
    with pytest.raises(FileNotFoundError):
        sqlite_to_duckdb(tmp_path / "nope.sqlite", duckdb_path)

    assert not duckdb_path.exists()


def test_existing_target_raises(fake_sqlite, duckdb_path):
    duckdb_path.write_bytes(b"not a database")

    with pytest.raises(FileExistsError):
        sqlite_to_duckdb(fake_sqlite, duckdb_path)

    # The untouched file must still be there.
    assert duckdb_path.read_bytes() == b"not a database"


def test_overwrite(edge_case_sqlite, duckdb_path):
    sqlite_to_duckdb(edge_case_sqlite, duckdb_path)

    result = sqlite_to_duckdb(edge_case_sqlite, duckdb_path, overwrite=True)

    assert result.tables == 3
    d_conn = duckdb.connect(str(duckdb_path))
    assert d_conn.sql("SELECT COUNT(*) FROM users").fetchone() == (2,)


def test_corrupt_source_leaves_no_partial_database(tmp_path, duckdb_path):
    """A failed conversion must not leave a half-written file behind, which would
    otherwise trip the `already exists` guard on the next run."""

    broken = tmp_path / "broken.sqlite"
    broken.write_bytes(b"definitely not a sqlite file" * 10)

    with pytest.raises(duckdb.Error):
        sqlite_to_duckdb(broken, duckdb_path)

    assert not duckdb_path.exists()


def test_source_path_with_quote_and_space(tmp_path, duckdb_path):
    weird = tmp_path / "it's a db.sqlite"
    utils.build_edge_case_sqlite(weird)

    result = sqlite_to_duckdb(weird, duckdb_path)

    assert result.tables == 3


def test_accepts_str_paths(edge_case_sqlite, duckdb_path):
    result = sqlite_to_duckdb(str(edge_case_sqlite), str(duckdb_path))

    assert result.tables == 3


def test_bracket_quoted_index(bracket_index_sqlite, duckdb_path):
    """Regression test: chinook.db writes its index DDL with [bracket] identifiers,
    which duckdb's own parser rejects."""

    result = sqlite_to_duckdb(bracket_index_sqlite, duckdb_path)

    # albums, "track list", plus the sqlite_sequence table AUTOINCREMENT creates.
    assert result.tables == 3

    d_conn = duckdb.connect(str(duckdb_path))

    assert d_conn.sql('SELECT * FROM "albums" ORDER BY AlbumId').fetchall() == [
        (1, "For Those About To Rock", 1),
        (2, "Balls to the Wall", 2),
    ]

    # The index and the constraints must survive too, as they do on the fast path.
    indexes = {
        row[0]
        for row in d_conn.sql("SELECT index_name FROM duckdb_indexes()").fetchall()
    }
    assert {"IFK_AlbumArtistId", "idx track"} <= indexes

    # The fallback quotes identifiers itself, so odd table names must survive.
    assert d_conn.sql('SELECT * FROM "track list" ORDER BY "Track Id"').fetchall() == [
        (1, "a [b] c"),
        (2, None),
    ]

    constraints = {
        row[0]
        for row in d_conn.sql(
            "SELECT constraint_type FROM duckdb_constraints() WHERE table_name = 'albums'"
        ).fetchall()
    }
    assert "PRIMARY KEY" in constraints
    assert "NOT NULL" in constraints
