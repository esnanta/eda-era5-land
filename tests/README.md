# Testing

**Role: CURRENT BEHAVIOR / HOW TO RUN TESTS.** This document describes tests currently present in the EDA repository, their purpose, and commands. For instructions on how an agent should design and change tests, see [tests/AGENTS.md](AGENTS.md). For project setup, see the [root README](../README.md).

## Current test structure

```text
tests/
├── AGENTS.md
├── README.md
├── unit/
│   ├── __init__.py
│   └── test_data_loader.py
└── integration/
    ├── __init__.py
    └── test_data_loader.py
```

**Unit tests** call the actual functions in [`utils/data_loader.py`](../utils/data_loader.py) to check missing/empty input handling and input-path selection. The DuckDB read boundary is mocked only for filename-selection checks; other loader behavior is exercised directly.

**Integration tests** call the same production loader using **real DuckDB and small Parquet files** created under temporary test directories. They verify annual-file discovery, hourly/daily separation, returned relation values, and input/manifest preservation. They do not use the project dataset or download remote data.

## Run tests

From the repository root with the Python environment activated:

```bash
python -m pytest tests/unit -q
python -m pytest tests/integration -q
python -m pytest tests -q
```

To run only the loader integration tests:

```bash
python -m pytest tests/integration/test_data_loader.py -q
```

A successful test run must be reported for **the current revision**. If production imports, paths, test placement, or assertions change, rerun the relevant suite.

## Test isolation and interpretation

Test fixtures belong in `tmp_path`; never write into `data/all/`. Keep cases deterministic and small. The tests protect **implemented loader behavior**, not data-quality findings for real ERA5-Land files.

As Stage 1 assessment functions become available, add tests for verified scientific contracts and calculate expected outcomes independently of the implementation. Do not introduce tests for unimplemented analysis or duplicate a full algorithm inside a test fixture.

## Definition of done

Relevant unit and integration tests pass; source inputs remain unchanged; documentation reflects actual code; and the [Stage 1 checklist](../todo/STAGE_1_HOURLY_DATA_QUALITY_ASSESSMENT.md) records the verified result. Static checks or collection-only runs do not replace executable tests.
