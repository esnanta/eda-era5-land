# Tests — Agent Instructions

**Role: testing rules for `tests/`.** Read [root AGENTS.md](../AGENTS.md), [scientific requirements](../docs/app_description.md), and [repository guidelines](../docs/repo_guidelines.md) first. Human-facing test commands belong in [tests/README.md](README.md).

## Scope

Tests protect the behavior of the **ERA5-Land EDA** tools and scientific assessment logic. Keep tests focused on the code and contracts actually implemented in this repository.

- Prefer fast, deterministic, offline `pytest` tests.
- Use small, temporary Parquet fixtures, with explicitly controlled timestamps, coordinates, values, NULLs, and NaNs where needed.
- Tests must **never write into `data/all/`**, modify source Parquet files, or require a CDS download or live external service.
- Keep the current tests directly under `tests/`. Add subdirectories only if the suite grows enough to need them.
- Use readable test names and a concise module docstring describing what the tests verify.

## Data loader contracts

Test [`utils/data_loader.py`](../utils/data_loader.py) through its public functions `load_hourly()` and `load_daily()`.

- The default data root is the repository's `data/all/`, independent of the current working directory.
- `ERA5_LAND_DATA_DIR` may point to another local or mounted `all/` directory.
- Discover any available `YYYY_hourly.parquet` or `YYYY_daily.parquet` files. Do not require a predetermined year range.
- Reject missing folders or folders without matching files with understandable `FileNotFoundError` messages.
- Return **DuckDB relations**, not eagerly materialized Pandas DataFrames.
- Ignore unrelated files while preserving input Parquet and `manifest.json` contents.

Use `tmp_path` for file fixtures and `monkeypatch` for environment variables. Test the public behavior rather than duplicating the loader implementation in test code.

## Scientific assessment contracts

As notebook analysis grows, add focused tests for calculations that can be verified independently:

- UTC hourly continuity; distinguish absent timestamps/rows from NULL or NaN values in present observations.
- Unique `(timestamp, latitude, longitude)` combinations and spatial grid coverage.
- Missingness denominators and separate NULL/NaN accounting where the schema allows.
- Correct timezones and variable units; use ERA5-Land-specific accumulation semantics when relevant.
- Classification of observations as expected characteristics, limitations, unverified anomalies, or **confirmed** issues only when evidence justifies the claim.

Never infer that every NULL/NaN identifies sea. Do not delete, fill, or silently repair unusual meteorological values.

## Verification and reporting

- Run the narrowest relevant tests after each change, then broaden coverage when appropriate.
- If an agent's runtime lacks DuckDB, PyArrow, or other required packages and installation is unavailable, **do not block preparation or pretend the tests passed**. Check syntax/static structure if feasible, give the exact test command for the user's configured environment, and mark execution as pending.
- A user-provided test result may be recorded as **user-run verification**, clearly distinguished from agent-run tests. After changing imports or behavior, request/rerun verification of the **new code**; prior passing tests do not prove the revision.
- Mark `todo/` checklist items `[x]` only when the specified implementation and relevant verification have actually occurred.
- Review changes and commit small logical steps to `dev` only, following the repository guidelines.

**Keep tests simple and evidence-based.**
