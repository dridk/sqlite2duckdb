# Changelog

All notable changes to this project are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the
project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `py.typed` marker, so type checkers pick up the annotations the package already ships.

### Changed

- Workflows moved off node20: `actions/checkout@v7` and `astral-sh/setup-uv@v10`.
- Fuller PyPI metadata — classifiers, keywords, and Repository / Documentation /
  Changelog links — and a version and license badge in the README.

## [0.5.0] - 2026-08-30

### Added

- Views are converted, best effort. A view whose SQL uses something duckdb has no
  equivalent for (`MATCH`, `julianday()`) is skipped with a warning instead of failing
  the whole conversion.
- UNIQUE constraints are carried over along with the indexes.

### Documentation

- Say why FOREIGN KEY and CHECK are left out: duckdb enforces both, but it checks
  foreign keys row by row — so a self-referencing table cannot be bulk loaded — and it
  has no `ALTER TABLE ADD CONSTRAINT` to add them once the data is in.

## [0.4.0] - 2026-08-30

### Added

- `-f` / `--force` to overwrite an existing duckdb file, `-q` / `--quiet` to report only
  errors, and `--verbose` to report every step.
- `sqlite_to_duckdb()` returns a `ConversionResult` with the table count, the view count
  and the elapsed time.
- Indexes are copied over, including those on bracket-quoted identifiers.
- `examples/chinook.sqlite.db` as a conversion example, exercised by the test suite.

### Changed

- Copy the database table by table instead of relying on `COPY FROM DATABASE`, which
  gives up on sqlite schemas duckdb's own parser cannot read back — `[bracket]` quoting
  being the common case.
- Packaging and dev tooling moved to uv and hatchling, with PyPI trusted publishing.

## [0.3.0] - 2024-05-23

- First release published to PyPI: convert the tables and data of a sqlite database,
  from the command line or from python.

[Unreleased]: https://github.com/dridk/sqlite2duckdb/compare/v0.5.0...HEAD
[0.5.0]: https://github.com/dridk/sqlite2duckdb/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/dridk/sqlite2duckdb/compare/0.3.0...v0.4.0
[0.3.0]: https://github.com/dridk/sqlite2duckdb/releases/tag/0.3.0
