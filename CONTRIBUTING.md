# Contributing

Bug reports, questions and pull requests are all welcome. If you hit a sqlite schema that
does not convert, the schema itself is the most useful thing you can attach.

## Setting up

The project uses [uv](https://docs.astral.sh/uv/) for everything:

```bash
make dev     # uv sync — installs duckdb plus the test deps (pytest, faker, ruff)
make test    # uv run pytest
make lint    # uv run ruff check . && uv run ruff format --check .
make build   # uv build
```

## Before opening a pull request

- `make test` passes. CI runs the same suite on Python 3.9 through 3.13.
- `make lint` passes. Ruff does both the linting and the formatting, so there is no
  separate formatter to run.
- `uv.lock` stays in sync with `pyproject.toml`. CI runs `uv sync --locked` and fails on
  drift, so run `uv sync` after touching dependencies and commit the lock file.
- Anything that changes what gets converted comes with a test.

## Adding a conversion feature

The interesting cases are the ones where sqlite and duckdb disagree, and they only show
up on real schemas: bracket-quoted identifiers, dotted column names, views whose SQL has
no duckdb equivalent. So each of these is pinned by a fixture rather than described in
prose.

`tests/utils.py` builds the sqlite databases the suite runs against — `build_bracket_sqlite`,
`build_views_sqlite`, `build_unique_sqlite` and friends — and `tests/conftest.py` exposes
each one as a session fixture. Adding a case means adding a builder there, wiring the
fixture, and asserting on the converted duckdb file.

`examples/chinook.sqlite.db` is the end-to-end example, and it is a real schema rather
than a synthetic one, so it is worth running against anything that touches the DDL path.

## Releasing

For maintainers:

1. Bump `version` in `pyproject.toml`.
2. Move the `Unreleased` entries of `CHANGELOG.md` into a new `## [x.y.z]` section and
   update the compare links at the bottom of the file.
3. Tag `vX.Y.Z` and push the tag.

The `Publish` workflow takes it from there: it builds, uploads to PyPI through trusted
publishing, and opens the GitHub release with the notes cut from that changelog section.
