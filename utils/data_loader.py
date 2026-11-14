"""Read existing ERA5-Land Parquet exports without changing source data."""

import os
from pathlib import Path

import duckdb


_DEFAULT_DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "all"


def _load(resolution: str) -> duckdb.DuckDBPyRelation:
    configured_dir = os.environ.get("ERA5_LAND_DATA_DIR")
    data_dir = Path(configured_dir).expanduser() if configured_dir else _DEFAULT_DATA_DIR
    folder = data_dir / resolution

    if not folder.is_dir():
        raise FileNotFoundError(f"{resolution} data directory not found: {folder}")

    pattern = f"[0-9][0-9][0-9][0-9]_{resolution}.parquet"
    files = sorted(folder.glob(pattern))
    if not files:
        raise FileNotFoundError(f"No {resolution} Parquet files found in {folder}")

    return duckdb.read_parquet([str(path) for path in files])


def load_hourly() -> duckdb.DuckDBPyRelation:
    """Return a lazy DuckDB relation for available hourly Parquet files."""
    return _load("hourly")


def load_daily() -> duckdb.DuckDBPyRelation:
    """Return a lazy DuckDB relation for available daily Parquet files."""
    return _load("daily")
