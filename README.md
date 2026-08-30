# sqlite2duckdb

![CI](https://github.com/dridk/sqlite2duckdb/actions/workflows/ci.yml/badge.svg)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/sqlite2duckdb)
![PyPI - Downloads](https://img.shields.io/pypi/dm/sqlite2duckdb)

A tool for converting a [sqlite](https://www.sqlite.org/) database into a [duckdb](https://duckdb.org/) database

## Description

Sqlite is an embedded online database designed for transactional reading and writing.
Duckdb is also an embedded database, but column-oriented, designed for analytical process with a very high reading efficiency.

For more details [Medium post](https://towardsdatascience.com/forget-about-sqlite-use-duckdb-instead-and-thank-me-later-df76ee9bb777)


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

## What is converted

| | |
|---|---|
| Tables and data | ✅ |
| Primary keys, NOT NULL and UNIQUE constraints | ✅ |
| Indexes | ✅ |
| Views | ✅ best effort |
| FOREIGN KEY and CHECK constraints | ❌ |

A view whose SQL uses something duckdb has no equivalent for (`MATCH`, `julianday()`) is
skipped with a warning instead of failing the conversion.

FOREIGN KEY and CHECK are not copied, though not for lack of support: duckdb accepts and
enforces both in `CREATE TABLE`. It checks foreign keys row by row, so a self-referencing
table cannot be bulk loaded, and there is no `ALTER TABLE ADD CONSTRAINT` to add them once
the data is in.

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
