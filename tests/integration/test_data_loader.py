"""Exercise utils.data_loader against real temporary Parquet files using DuckDB."""

from pathlib import Path

import duckdb
import pytest

from utils import data_loader


def _write_parquet(path: Path, value: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    duckdb.sql(f"SELECT {value} AS observation").write_parquet(str(path))


def test_load_hourly_discovers_available_years(monkeypatch, tmp_path):
    root = tmp_path / "all"
    _write_parquet(root / "hourly" / "2020_hourly.parquet", 20)
    _write_parquet(root / "hourly" / "2022_hourly.parquet", 22)
    _write_parquet(root / "hourly" / "other.parquet", 999)
    (root / "hourly" / "manifest.json").write_text("{}")
    monkeypatch.setenv("ERA5_LAND_DATA_DIR", str(root))

    relation = data_loader.load_hourly()

    assert isinstance(relation, duckdb.DuckDBPyRelation)
    assert relation.order("observation").fetchall() == [(20,), (22,)]
    assert (root / "hourly" / "manifest.json").read_text() == "{}"


def test_load_daily_reads_daily_only(monkeypatch, tmp_path):
    root = tmp_path / "all"
    _write_parquet(root / "daily" / "2019_daily.parquet", 19)
    _write_parquet(root / "hourly" / "2019_hourly.parquet", 1900)
    monkeypatch.setenv("ERA5_LAND_DATA_DIR", str(root))

    assert data_loader.load_daily().fetchall() == [(19,)]


def test_default_data_directory_is_repository_relative(monkeypatch, tmp_path):
    root = tmp_path / "data" / "all"
    _write_parquet(root / "hourly" / "2030_hourly.parquet", 30)
    monkeypatch.delenv("ERA5_LAND_DATA_DIR", raising=False)
    monkeypatch.setattr(data_loader, "_DEFAULT_DATA_DIR", root)

    assert data_loader.load_hourly().fetchall() == [(30,)]


@pytest.mark.parametrize("resolution", ["hourly", "daily"])
def test_missing_directory_raises_file_not_found(monkeypatch, tmp_path, resolution):
    monkeypatch.setenv("ERA5_LAND_DATA_DIR", str(tmp_path / "missing"))
    with pytest.raises(FileNotFoundError, match=f"{resolution} data directory not found"):
        getattr(data_loader, f"load_{resolution}")()


@pytest.mark.parametrize("resolution", ["hourly", "daily"])
def test_empty_directory_raises_file_not_found(monkeypatch, tmp_path, resolution):
    (tmp_path / resolution).mkdir()
    monkeypatch.setenv("ERA5_LAND_DATA_DIR", str(tmp_path))
    with pytest.raises(FileNotFoundError, match=f"No {resolution} Parquet files found"):
        getattr(data_loader, f"load_{resolution}")()
