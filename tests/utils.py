"""Builders for the sqlite databases used as test fixtures."""

import random
import sqlite3

from faker import Faker

FAKE_ROWS = 1000


def build_fake_sqlite(path, rows=FAKE_ROWS):
    """A database covering every sqlite type affinity, with reproducible data."""

    fake = Faker()
    Faker.seed(1234)
    rng = random.Random(1234)

    conn = sqlite3.connect(path)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS data (
            id INTEGER PRIMARY KEY,
            integer_col INTEGER,
            real_col REAL,
            text_col TEXT,
            boolean_col BOOLEAN,
            date_col DATE,
            time_col TIME,
            datetime_col DATETIME,
            blob_col BLOB,
            numeric_col NUMERIC,
            null_col NULL
        )
        """
    )

    def generate_fake_data():
        integer_col = rng.randint(1, 1000)
        real_col = rng.uniform(1.0, 1000.0)
        return (
            integer_col,
            real_col,
            fake.text(max_nb_chars=20),
            rng.choice([True, False]),
            fake.date(),
            # Adapt datetimes ourselves: sqlite3's implicit adapter is deprecated.
            fake.date_time().isoformat(sep=" "),
            fake.date_time().isoformat(sep=" "),
            fake.binary(length=10),
            rng.choice([integer_col, real_col]),
            None,
        )

    conn.executemany(
        """
        INSERT INTO data (integer_col, real_col, text_col, boolean_col, date_col,
                          time_col, datetime_col, blob_col, numeric_col, null_col)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [generate_fake_data() for _ in range(rows)],
    )
    conn.commit()
    conn.close()

    return path


def build_edge_case_sqlite(path):
    """Quoted and reserved table names, plus constraints and an index."""

    conn = sqlite3.connect(path)
    conn.executescript(
        """
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            age INTEGER
        );
        INSERT INTO users (name, age) VALUES ('alice', 30), ('bob', 40);
        CREATE INDEX idx_users_age ON users(age);

        CREATE TABLE "my table" (a INTEGER, b TEXT);
        INSERT INTO "my table" VALUES (1, 'x');

        CREATE TABLE "order" (x INTEGER);
        INSERT INTO "order" VALUES (7);
        """
    )
    conn.commit()
    conn.close()

    return path


def build_bracket_sqlite(path):
    """Sqlite db using [bracket] quoting, as produced by MS Access exports (issue #3)."""

    conn = sqlite3.connect(path)
    conn.executescript(
        """
        CREATE TABLE [Order Details] ([OrderID] INTEGER, [Qty] INTEGER);
        INSERT INTO [Order Details] VALUES (1, 5), (2, 7);

        CREATE VIEW [Order Subtotals] AS
            SELECT [Order Details].OrderID, Sum([Order Details].Qty) AS Total
            FROM [Order Details]
            GROUP BY [Order Details].OrderID;
        """
    )
    conn.commit()
    conn.close()

    return path


def build_dotted_column_sqlite(path):
    """STRICT table whose column names look like numbers (issue #4)."""

    conn = sqlite3.connect(path)
    conn.executescript(
        """
        CREATE TABLE measures ("2.3.4" INTEGER, "1e5" TEXT) STRICT;
        INSERT INTO measures VALUES (42, 'hello');
        """
    )
    conn.commit()
    conn.close()

    return path


#: Values chosen to survive a sqlite -> duckdb round trip byte for byte.
FIDELITY_ROWS = [
    (1, 0, 0.0, "", b"", None),
    (2, -1, -1.5, "héllo ünicode ✓", b"\x00\x01\xff", 7),
    (3, 9223372036854775807, 1e308, "with 'quotes' and \"double\"", b"\n\r\t", None),
    (4, None, None, None, None, None),
]


def build_fidelity_sqlite(path):
    """A table whose exact values must come out unchanged on the duckdb side."""

    conn = sqlite3.connect(path)
    conn.execute(
        """
        CREATE TABLE roundtrip (
            id INTEGER PRIMARY KEY,
            int_col INTEGER,
            real_col REAL,
            text_col TEXT,
            blob_col BLOB,
            nullable_col INTEGER
        )
        """
    )
    conn.executemany("INSERT INTO roundtrip VALUES (?, ?, ?, ?, ?, ?)", FIDELITY_ROWS)
    conn.commit()
    conn.close()

    return path


def build_empty_sqlite(path):
    """A valid sqlite file holding no table at all."""

    conn = sqlite3.connect(path)
    conn.execute("CREATE TABLE placeholder (x INTEGER)")
    conn.execute("DROP TABLE placeholder")
    conn.commit()
    conn.close()

    return path


def build_bracket_index_sqlite(path):
    """A chinook-shaped database: index DDL written with [bracket] identifiers.

    Duckdb's parser rejects `[`, so that quoting has to be translated on the way in.
    """

    conn = sqlite3.connect(path)
    conn.executescript(
        """
        CREATE TABLE "albums"
        (
            [AlbumId] INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            [Title] NVARCHAR(160) NOT NULL,
            [ArtistId] INTEGER NOT NULL
        );
        INSERT INTO "albums" VALUES (1, 'For Those About To Rock', 1), (2, 'Balls to the Wall', 2);
        CREATE INDEX [IFK_AlbumArtistId] ON "albums" ([ArtistId]);

        CREATE TABLE [track list] ([Track Id] INTEGER, [Label] TEXT);
        INSERT INTO [track list] VALUES (1, 'a [b] c'), (2, NULL);
        CREATE INDEX [idx track] ON [track list] ([Track Id]);
        """
    )
    conn.commit()
    conn.close()

    return path
