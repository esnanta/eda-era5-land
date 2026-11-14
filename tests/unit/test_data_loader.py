"""Test loader failure handling and path selection without reading Parquet data."""

from pathlib import Path

import pytest

from utils import data_loader


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


def test_loader_passes_matching_files_to_duckdb(monkeypatch, tmp_path):
    """Only the external DuckDB read boundary is replaced; file selection is real."""
    folder = tmp_path / "hourly"
    folder.mkdir()
    (folder / "2024_hourly.parquet").touch()
    (folder / "2022_hourly.parquet").touch()
    (folder / "ignore.parquet").touch()
    (folder / "manifest.json").write_text("{}")
    monkeypatch.setenv("ERA5_LAND_DATA_DIR", str(tmp_path))

    observed = []
    sentinel = object()

    def capture_paths(paths):
        observed.extend(paths)
        return sentinel

    monkeypatch.setattr(data_loader.duckdb, "read_parquet", capture_paths)

    result = data_loader.load_hourly()

    assert result is sentinel
    assert observed == [
        str(folder / "2022_hourly.parquet"),
        str(folder / "2024_hourly.parquet"),
    ]


def test_default_root_is_not_relative_to_working_directory(monkeypatch, tmp_path):
    expected_root = Path(data_loader.__file__).resolve().parent.parent / "data" / "all"
    monkeypatch.delenv("ERA5_LAND_DATA_DIR", raising=False)
    monkeypatch.chdir(tmp_path)

    assert data_loader._DEFAULT_DATA_DIR == expected_root
