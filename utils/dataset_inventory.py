"""Inventory existing hourly ERA5-Land Parquet files without modifying them."""

import json
import os
from pathlib import Path

import duckdb
import pyarrow.parquet as pq


def inspect_hourly_files(data_root=None):
    """Return per-file metadata and actual UTC time coverage for available hourly files."""
    default_root = Path(__file__).resolve().parent.parent / "data" / "all"
    root = Path(data_root or os.environ.get("ERA5_LAND_DATA_DIR") or default_root).expanduser()
    folder = root / "hourly"
    if not folder.is_dir():
        raise FileNotFoundError(f"Hourly data directory not found: {folder}")

    files = sorted(folder.glob("[0-9][0-9][0-9][0-9]_hourly.parquet"))
    if not files:
        raise FileNotFoundError(f"No hourly Parquet files found in {folder}")

    records = []
    for path in files:
        parquet = pq.ParquetFile(path)
        schema = parquet.schema_arrow
        columns = schema.names
        time_col = next((col for col in ("valid_time", "time", "timestamp") if col in columns), None)
        record = {
            "file": path.name,
            "year_in_filename": int(path.name[:4]),
            "size_bytes": path.stat().st_size,
            "row_count": parquet.metadata.num_rows,
            "row_groups": parquet.metadata.num_row_groups,
            "columns": columns,
            "schema": {field.name: str(field.type) for field in schema},
            "timestamp_column": time_col,
            "first_utc": None,
            "last_utc": None,
            "observed_months": [],
        }
        if time_col:
            # Project timestamps only. Do not load meteorological values into Pandas.
            relation = duckdb.read_parquet(str(path))
            quoted = '"' + time_col.replace('"', '""') + '"'
            first, last = relation.aggregate(
                f"MIN({quoted}) AS first_time, MAX({quoted}) AS last_time"
            ).fetchone()
            months = (
                relation.project(f"DATE_TRUNC('month', {quoted}) AS month_start")
                .distinct()
                .order("month_start")
                .fetchall()
            )
            record["first_utc"] = str(first) if first is not None else None
            record["last_utc"] = str(last) if last is not None else None
            record["observed_months"] = [str(row[0])[:7] for row in months if row[0] is not None]
        records.append(record)
    return records


def read_hourly_manifest(data_root=None):
    """Read the hourly export manifest as-is; do not assume a fixed JSON schema."""
    default_root = Path(__file__).resolve().parent.parent / "data" / "all"
    root = Path(data_root or os.environ.get("ERA5_LAND_DATA_DIR") or default_root).expanduser()
    path = root / "hourly" / "manifest.json"
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON manifest: {path}") from exc
