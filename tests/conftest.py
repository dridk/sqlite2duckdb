import pytest

from tests import utils


def _module_db(tmp_path_factory, name, builder):
    path = tmp_path_factory.mktemp(name) / f"{name}.sqlite"
    builder(path)
    return path


@pytest.fixture(scope="module")
def fake_sqlite(tmp_path_factory):
    return _module_db(tmp_path_factory, "fake", utils.build_fake_sqlite)


@pytest.fixture(scope="module")
def edge_case_sqlite(tmp_path_factory):
    return _module_db(tmp_path_factory, "edge", utils.build_edge_case_sqlite)


@pytest.fixture(scope="module")
def bracket_sqlite(tmp_path_factory):
    return _module_db(tmp_path_factory, "bracket", utils.build_bracket_sqlite)


@pytest.fixture(scope="module")
def dotted_column_sqlite(tmp_path_factory):
    return _module_db(tmp_path_factory, "dotted", utils.build_dotted_column_sqlite)


@pytest.fixture(scope="module")
def fidelity_sqlite(tmp_path_factory):
    return _module_db(tmp_path_factory, "fidelity", utils.build_fidelity_sqlite)


@pytest.fixture(scope="module")
def empty_sqlite(tmp_path_factory):
    return _module_db(tmp_path_factory, "empty", utils.build_empty_sqlite)


@pytest.fixture
def duckdb_path(tmp_path):
    """A path where the target database does not exist yet."""

    return tmp_path / "target.duckdb"


@pytest.fixture(scope="module")
def bracket_index_sqlite(tmp_path_factory):
    return _module_db(tmp_path_factory, "bindex", utils.build_bracket_index_sqlite)
