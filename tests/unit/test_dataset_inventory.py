"""Verify production inventory and manifest failure behavior using temporary files."""

import pytest

from utils.dataset_inventory import inspect_hourly_files, read_hourly_manifest


def test_inventory_missing_directory_raises(tmp_path):
    with pytest.raises(FileNotFoundError, match="Hourly data directory not found"):
        inspect_hourly_files(tmp_path)


def test_inventory_empty_directory_raises(tmp_path):
    (tmp_path / "hourly").mkdir()
    with pytest.raises(FileNotFoundError, match="No hourly Parquet files"):
        inspect_hourly_files(tmp_path)


def test_missing_manifest_returns_none(tmp_path):
    assert read_hourly_manifest(tmp_path) is None


def test_invalid_manifest_raises_clear_error(tmp_path):
    folder = tmp_path / "hourly"
    folder.mkdir()
    (folder / "manifest.json").write_text("{not-json}", encoding="utf-8")
    with pytest.raises(ValueError, match="Invalid JSON manifest"):
        read_hourly_manifest(tmp_path)
