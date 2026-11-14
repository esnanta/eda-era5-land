# Stage 1 — Hourly Data Quality Assessment: Implementation Checklist

**Status:** In progress — Step 1 complete; Step 2 loader implemented, runtime tests pending  
**Branch:** `dev` only  
**Scope:** Build and validate the first ERA5-Land EDA notebook using whatever hourly Parquet data is available. Do not assume a fixed analysis period.

This checklist tracks implementation work. Update the checkboxes **in the same commit as the completed work**, or in a small follow-up documentation commit after verification. **Mark `[x]` only after the item is implemented and checked.** Leave blocked, unexecuted, or partially completed items unchecked; explain blockers in the progress log.

## References and working rules

- [AGENTS.md](../AGENTS.md) — agent instructions.
- [docs/app_description.md](../docs/app_description.md) — scientific requirements and acceptance criteria.
- [README.md](../README.md) — actual repository setup and usage.
- [docs/repo_guidelines.md](../docs/repo_guidelines.md) — branch restrictions, small verified commits.
- [docs/python_se_principle.md](../docs/python_se_principle.md) — KISS, DRY, YAGNI first.
- [template/eda_starter.ipynb](../template/eda_starter.ipynb) — notebook narrative/reference structure.
- [ds-notebook/01_exploratory_data_analysis.ipynb](../ds-notebook/01_exploratory_data_analysis.ipynb) — first methodological reference.

Inputs are **read-only** under `data/all/hourly/` (or a configured external data root), with `YYYY_hourly.parquet` files and `manifest.json`. The `data/` directory is Git-ignored. Stage 1 writes **reports and figures**, never modified input Parquet.

## 1. Repository preparation

- [x] Correct outdated `template/eda_starter.ipynb.ipynb` references in `AGENTS.md`, `docs/app_description.md`, and `README.md` to the existing `template/eda_starter.ipynb`.
- [x] Remove the outdated `era5_land_notebook.ipynb` entry from `README.md` if the file remains absent from `dev`.
- [x] Add minimal, compatible analysis/test dependencies (including DuckDB, PyArrow, Pandas, NumPy, Matplotlib, Seaborn, JupyterLab, and pytest) without unnecessary engines or frameworks.
- [x] Verify environment creation, dependency installation, and basic imports.
- [x] Review the diff and commit only this logical preparation change.

**Done when:** documentation links resolve, dependencies install/import successfully, and the preparation commit is verified.

## 2. Simple Parquet loader

- [x] Create a small `data_loader.py` containing `load_hourly()` and `load_daily()`, both returning DuckDB relations.
- [x] Read year-named Parquet files discovered from `data/all/{hourly,daily}/` rather than requiring explicit start/end years.
- [x] Permit a different local or mounted data root through `ERA5_LAND_DATA_DIR`; keep `data/all/` as the default.
- [x] Raise a clear error for missing directories or matching Parquet files.
- [x] Keep all source files and manifests immutable; do not load the entire dataset into Pandas by default.
- [ ] Add focused tests using small temporary Parquet fixtures for both functions, missing files, and configurable paths.
- [ ] Run relevant tests, review the diff, and commit.

**Done when:** both loader functions work on small fixtures and fail clearly on missing input, without changing source files.

## 3. Dataset inventory and provenance

- [ ] Create `notebooks/01_hourly_data_quality_assessment.ipynb` using the EDA Starter narrative structure and the preferred EDA methodology.
- [ ] Discover actual hourly files and inventory filenames, sizes, available years, and metadata row counts.
- [ ] Inspect `manifest.json` and compare listed files, expected coverage, completion state, and source/output hashes with available evidence.
- [ ] Inspect actual Parquet schema, column names, data types, and variable presence before writing scientific queries.
- [ ] Determine minimum/maximum observed UTC timestamps and actual year/month coverage **from data**, not only filenames.
- [ ] Distinguish partial exports, missing months, missing manifest entries, and actual coverage discrepancies.
- [ ] Produce concise, readable inventory tables without materializing the full hourly dataset.
- [ ] Verify results using a small controlled fixture; review and commit.

**Done when:** the notebook can explain what data really exists, what the manifest claims, and any differences between them.

## 4. Temporal and spatial integrity

- [ ] Count distinct hourly UTC timestamps; identify gaps, duplicates, and partial months/years relative to the actual observed span and available-source coverage.
- [ ] Distinguish globally absent timestamps from missing `(timestamp, latitude, longitude)` observations.
- [ ] Detect duplicate `(timestamp, latitude, longitude)` rows, using the verified schema.
- [ ] Validate latitude/longitude ranges and 0.1° regular-grid spacing; compare observed coordinates with the expected **43 × 35 = 1,505** bounding-box grid.
- [ ] Detect missing coordinate pairs and changes in per-point temporal coverage.
- [ ] Plot temporal coverage by month/year and spatial grid coverage with clear denominators and legends.
- [ ] Test gap, duplicate, partial-coverage, and missing-grid scenarios on small fixtures.
- [ ] Review results and commit.

**Done when:** temporal and spatial completeness are quantified without equating an absent row with an existing row containing NULL/NaN.

## 5. Missing values and variable quality

- [ ] Count NULL and NaN where distinguishable, plus total missing values, for each available variable.
- [ ] Measure missingness by coordinate, month, and year; separate consistently all-missing points from intermittent missingness.
- [ ] Plot spatial missingness, including marine-looking patterns, **without asserting that NULL/NaN proves a sea location**.
- [ ] If a reliable matching land/sea reference is unavailable, state that classification remains unverified.
- [ ] Compute valid counts, distribution summaries, quantiles, minimum/maximum, and suitable variable-specific anomaly indicators.
- [ ] Check physical units and ERA5-Land-specific temporal semantics, especially accumulated `tp` and `ssrd`; avoid generic aggregations across unlike variables.
- [ ] Flag suspicious extremes for review; do not impute, delete, zero-fill, or modify source data.
- [ ] Verify missing-value denominators and key statistics on controlled fixtures.
- [ ] Review results and commit.

**Done when:** the report separates expected source characteristics, missing observations, and unexplained missing values, with variable-specific evidence.

## 6. Data Quality Report

- [ ] Write a readable Markdown report to `eda/hourly_assessment/reports/`.
- [ ] Save appropriately sized figures to `eda/hourly_assessment/figures/`.
- [ ] Classify findings into **Expected Source Characteristics**, **Data Limitations and Incompleteness**, **Anomalies Requiring Investigation**, and **Confirmed Data Quality Issues**.
- [ ] For significant findings, document **Evidence → Interpretation → Impact → Recommendation**.
- [ ] Reserve “confirmed” for issues supported by verification; otherwise record uncertainty and follow-up work.
- [ ] Record the actual analyzed period, file/manifest provenance, variable coverage, and study limitations.
- [ ] Check that all claims can be traced to computed outputs, then review and commit.

**Done when:** a reader can understand Stage 1 findings without inspecting every notebook cell.

## 7. Final validation and documentation

- [ ] Run focused helper tests, including missing-file, duplicate, missing-timestamp, missing-coordinate, and NULL/NaN cases.
- [ ] Execute the notebook sequentially against a small representative dataset, checking reproducibility and readable outputs.
- [ ] Execute against actual available hourly data **if accessible**, recording resource use and any partial/unrun checks.
- [ ] Verify that DuckDB aggregates before Pandas conversion, and that no operation unnecessarily materializes the full hourly dataset.
- [ ] Confirm source Parquet/manifests remain unchanged and large data/generated outputs are not accidentally committed.
- [ ] Update `README.md` to describe only the setup and commands that were actually implemented.
- [ ] Review final diffs, run relevant checks, and commit the verified work.

**Done when:** Stage 1 meets the acceptance criteria in `docs/app_description.md`, with any unavailable-data limitations explicitly recorded.

## Progress log

Add one short row for each completed logical change. Do not mark incomplete work as complete.

| Date (UTC) | Step | Commit | Verification / notes |
| --- | --- | --- | --- |
| 2026-11-14 | 1 — Documentation references | `62ff86c`, `aed4d02`, `69e7c1c` | Corrected template links; removed the missing notebook reference. Read back and checked files on `dev`. |
| 2026-11-14 | 1 — Dependencies and setup docs | `09e3073`, `24ff093` | Added eight dependencies; updated README installation command. Requirement syntax validated; Python virtual environment created in verification environment. **User independently confirmed all eight imports succeeded in the project environment** with `python -c ...`. |
| 2026-11-14 | 2 — Loader implementation | `536c3de`, `a4b38ad`, `94e5235` | Added two DuckDB Parquet loaders, seven parametrized test cases, and README usage. Python syntax checks passed, and repository files were reviewed. **Pytest requiring real DuckDB not executed** in the assistant runtime because package installation was blocked; `python -m pytest tests/test_data_loader.py -q` remains required. |

## Completion policy

- Use `[ ]` for not started, in progress, blocked, or unverified tasks.
- Use `[x]` only after implementation **and** relevant verification.
- After completing a logical step, update this checklist and the progress log, then commit in a small focused change on `dev`.
- When live Parquet data is not accessible, synthetic tests may establish implementation correctness, but **do not** claim that actual data quality has been assessed.
- Stage 2 is outside this checklist.
