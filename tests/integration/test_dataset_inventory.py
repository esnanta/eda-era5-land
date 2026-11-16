"""Test production hourly inventory metadata against real temporary Parquet files."""

import json

import duckdb

from utils.dataset_inventory import inspect_hourly_files, read_hourly_manifest


def test_inventory_reads_footer_schema_and_observed_months(tmp_path):
    folder = tmp_path / "hourly"
    folder.mkdir()
    output = folder / "2024_hourly.parquet"
    duckdb.sql("""
        SELECT TIMESTAMP '2024-05-01 00:00:00' AS valid_time,
               5.0::DOUBLE AS latitude, 96.0::DOUBLE AS longitude,
               289.0::DOUBLE AS t2m
        UNION ALL
        SELECT TIMESTAMP '2024-07-01 01:00:00', 5.0, 96.0, 290.0
    """).write_parquet(str(output))

    rows = inspect_hourly_files(tmp_path)

    assert len(rows) == 1
    actual = rows[0]
    assert actual["file"] == "2024_hourly.parquet"
    assert actual["year_in_filename"] == 2024
    assert actual["row_count"] == 2
    assert actual["row_groups"] >= 1
    assert actual["size_bytes"] > 0
    assert actual["timestamp_column"] == "valid_time"
    assert actual["first_utc"].startswith("2024-05-01")
    assert actual["last_utc"].startswith("2024-07-01")
    assert actual["observed_months"] == ["2024-05", "2024-07"]
    assert "t2m" in actual["columns"]


def test_inventory_does_not_mutate_parquet_or_manifest(tmp_path):
    folder = tmp_path / "hourly"
    folder.mkdir()
    parquet = folder / "2026_hourly.parquet"
    duckdb.sql("SELECT TIMESTAMP '2026-01-01 00:00:00' AS valid_time").write_parquet(str(parquet))
    manifest = folder / "manifest.json"
    manifest.write_text(json.dumps({"note": "small fixture"}), encoding="utf-8")
    original_parquet = parquet.read_bytes()
    original_manifest = manifest.read_bytes()

    assert inspect_hourly_files(tmp_path)[0]["row_count"] == 1
    assert read_hourly_manifest(tmp_path) == {"note": "small fixture"}
    assert parquet.read_bytes() == original_parquet
    assert manifest.read_bytes() == original_manifest
