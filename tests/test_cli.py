"""End to end tests of the command line entry point.

They run the CLI in a subprocess with stdin closed, which is exactly the
situation (CI, pipes, `uvx ... < /dev/null`) the interactive prompt used to hang in.
"""

import subprocess
import sys

import pytest

REPO_ROOT = str(__import__("pathlib").Path(__file__).resolve().parent.parent)


def run_cli(*args, stdin=subprocess.DEVNULL, timeout=120):
    return subprocess.run(
        [sys.executable, "-m", "sqlite2duckdb", *map(str, args)],
        capture_output=True,
        check=False,
        text=True,
        stdin=stdin,
        cwd=REPO_ROOT,
        timeout=timeout,
    )


def test_version():
    result = run_cli("--version")

    assert result.returncode == 0
    assert result.stdout.startswith("sqlite2duckdb ")


def test_converts(edge_case_sqlite, duckdb_path):
    result = run_cli(edge_case_sqlite, duckdb_path)

    assert result.returncode == 0, result.stderr
    assert duckdb_path.exists()
    # Progress must not pollute stdout.
    assert result.stdout == ""
    assert "3 table(s) found" in result.stderr


def test_quiet_says_nothing(edge_case_sqlite, duckdb_path):
    result = run_cli("--quiet", edge_case_sqlite, duckdb_path)

    assert result.returncode == 0
    assert result.stdout == ""
    assert result.stderr == ""


def test_missing_source_reports_error(tmp_path, duckdb_path):
    result = run_cli(tmp_path / "nope.sqlite", duckdb_path)

    assert result.returncode == 1
    assert "doesn't exist" in result.stderr
    assert "Traceback" not in result.stderr


def test_existing_target_without_tty_fails_instead_of_hanging(
    edge_case_sqlite, duckdb_path
):
    duckdb_path.write_bytes(b"keep me")

    result = run_cli(edge_case_sqlite, duckdb_path, timeout=30)

    assert result.returncode == 1
    assert "--force" in result.stderr
    assert duckdb_path.read_bytes() == b"keep me"


@pytest.mark.parametrize("flag", ["-f", "--force"])
def test_force_overwrites(flag, edge_case_sqlite, duckdb_path):
    duckdb_path.write_bytes(b"stale")

    result = run_cli(flag, edge_case_sqlite, duckdb_path)

    assert result.returncode == 0, result.stderr
    assert duckdb_path.read_bytes() != b"stale"
