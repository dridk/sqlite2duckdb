import importlib.metadata

from sqlite2duckdb.sqlite_to_duckdb import ConversionResult, sqlite_to_duckdb

try:
    __version__ = importlib.metadata.version("sqlite2duckdb")
except importlib.metadata.PackageNotFoundError:
    # Running from a source checkout that was never installed.
    __version__ = "0.0.0.dev0"

# Deprecated alias, kept so that existing imports keep working.
__VERSION__ = __version__

__all__ = ["ConversionResult", "__version__", "sqlite_to_duckdb"]
