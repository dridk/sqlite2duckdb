# sqlite2duckdb

![CI](https://github.com/dridk/sqlite2duckdb/actions/workflows/ci.yml/badge.svg)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/sqlite2duckdb)
![PyPI - Downloads](https://img.shields.io/pypi/dm/sqlite2duckdb)

A tool for converting a [sqlite](https://www.sqlite.org/) database into a [duckdb](https://duckdb.org/) database

## Description

Sqlite is an embedded online database designed for transactional reading and writing.
Duckdb is also an embedded database, but column-oriented, designed for analytical process with a very high reading efficiency.

For more details [https://towardsdatascience.com/forget-about-sqlite-use-duckdb-instead-and-thank-me-later-df76ee9bb777](https://towardsdatascience.com/forget-about-sqlite-use-duckdb-instead-and-thank-me-later-df76ee9bb777)

Requires Python >= 3.9 and duckdb >= 1.1.0 (indexes are only copied from that version on).

## Installation

With [uv](https://docs.astral.sh/uv/), no installation is required. `uvx` downloads and runs the tool in one go:

```bash
uvx sqlite2duckdb source.db target.db
```

To keep it around:

```bash
uv tool install sqlite2duckdb
```

Or with pip:

```bash
pip install sqlite2duckdb
```

## Usage

### As a command line

```
usage: sqlite2duckdb [-f] <sqlite_path> <duckdb_path>

Convert Sqlite database to Duckdb database

positional arguments:
  sqlite_path    sqlite file path
  duckdb_path    duckdb file path

options:
  -h, --help     show this help message and exit
  -f, --force    overwrite the duckdb file if it already exists
  -q, --quiet    only report errors
  --verbose      report every step
  -v, --version  show program's version number and exit
```

The tool never overwrites an existing target silently. On a terminal it asks for
confirmation; anywhere else (a script, a CI job, a pipe) it exits with code 1 and tells you
to pass `--force`. Progress is written to stderr, so stdout stays free for pipelines.

### Examples

```bash
uvx sqlite2duckdb source.db target.db
uvx sqlite2duckdb --force source.db target.db   # overwrite target.db without asking
```

### From python

```python
from sqlite2duckdb import sqlite_to_duckdb

result = sqlite_to_duckdb("source.sqlite", "target.duckdb")
print(result.tables, result.views, result.elapsed)
```

`sqlite_to_duckdb(sqlite_db, duck_db, *, overwrite=False)` accepts `str` or `pathlib.Path`
and returns a `ConversionResult` (`target`, `tables`, `views`, `elapsed`). It raises
`FileNotFoundError` if the source is missing and `FileExistsError` if the target already
exists and `overwrite` is False. If the conversion fails halfway, the partially written
target file is removed rather than left behind. Progress is reported through the standard
`logging` module (logger `sqlite2duckdb.sqlite_to_duckdb`), never printed.

## What is converted

| | |
|---|---|
| Tables and data | ✅ |
| Primary keys, NOT NULL and UNIQUE constraints | ✅ |
| Indexes | ✅ |
| Views | ✅ best effort |
| FOREIGN KEY and CHECK constraints | ❌ |

Tables are recreated from the DDL duckdb derives for the attached database, then filled
from it. Everything duckdb's sqlite extension does not expose on an attached database is
read back from `sqlite_master` instead: the indexes and the views with their SQL, and the
UNIQUE constraints through `PRAGMA index_list`, since sqlite records those as autoindexes
carrying no SQL at all.

That detour is also what makes sqlite files quoting their DDL with `[brackets]`
(chinook.db, MS Access exports) convert correctly: duckdb's parser rejects that syntax, so
the quoting is translated first.

Views are best effort because their SQL is sqlite's, not duckdb's. One using a construct
duckdb has no equivalent for (`MATCH`, or a function like `julianday`) is skipped with a
warning rather than failing the whole conversion; everything else still converts. Views
sitting on top of other views are handled whatever order `sqlite_master` lists them in.

FOREIGN KEY and CHECK constraints are the one real gap: duckdb has no
`ALTER TABLE ADD CONSTRAINT`, so there is no way to add them once the table exists.
Carrying them over would mean generating the whole `CREATE TABLE` by hand, with a type
mapping of our own, instead of reusing the one duckdb already derives.

## Todo

- [ ] Custom type mapping
- [ ] FOREIGN KEY and CHECK constraints
- [x] Primary keys, NOT NULL and UNIQUE constraints, indexes and views

## Contributing

The project uses [uv](https://docs.astral.sh/uv/) for everything:

```bash
make dev     # uv sync — installs duckdb plus the test deps (pytest, faker, ruff)
make test    # uv run pytest
make lint    # uv run ruff check . && uv run ruff format --check .
make build   # uv build
make publish # uv publish (PyPI trusted publishing, also run on tags by CI)
```

### See also

- [Harlequin](https://github.com/tconbeer/harlequin): A nice duckdb IDE for your terminal
