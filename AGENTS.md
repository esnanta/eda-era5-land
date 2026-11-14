# AGENTS.md — Repository Instructions

**Role: HOW TO WORK.** This document guides coding agents working on the ERA5-Land exploratory data analysis (EDA) repository. It does not replace the scientific specification or describe unimplemented features as current behavior.

## 1. Project boundaries

This repository analyzes **Copernicus CDS ERA5-Land** hourly and daily Parquet data for the Aceh study area. The analysis period is determined from the datasets actually available, not from a fixed range of years.

- This repository performs assessment, exploration, visualization, and reporting. It does **not** download CDS data or update canonical climate observations.
- Treat input Parquet and `manifest.json` files as immutable. Never silently repair, overwrite, delete, or fill source values.
- Do not infer that all grid points are on land or that every NULL/NaN is a data defect.

## 2. Documentation ownership

Read the documents relevant to the task before editing.

| Document | Role | Owns |
| --- | --- | --- |
| [docs/app_description.md](docs/app_description.md) | **WHAT** | Study scope, scientific/data contracts, EDA stages, planned technologies, and acceptance criteria |
| [README.md](README.md) | **CURRENT BEHAVIOR / SETUP** | Actual repository contents, environment setup, data placement, usage, and attribution |
| [docs/repo_guidelines.md](docs/repo_guidelines.md) | **REPOSITORY WORKFLOW** | Branch restrictions, small changes, testing, commits, and push safety |
| [docs/python_se_principle.md](docs/python_se_principle.md) | **PYTHON DESIGN** | Pragmatic SOLID guided by DRY, KISS, and YAGNI |
| [template/eda_starter.ipynb](template/eda_starter.ipynb) | **NOTEBOOK STRUCTURE** | Narrative layout, analysis presentation, interpretation, conclusions, and references |
| [ds-notebook/01_exploratory_data_analysis.ipynb](ds-notebook/01_exploratory_data_analysis.ipynb) | **EDA METHOD REFERENCE** | First choice for data-science EDA methodology |
| **AGENTS.md** | **INSTRUCTIONS** | Agent behavior and navigation |

Keep each rule in its owning document. Link rather than duplicating long explanations. If a requested change conflicts with the scientific contract, update the owning specification deliberately before implementing the change.

## 3. Repository safety and workflow

Follow [repository guidelines](docs/repo_guidelines.md) in full. In particular:

1. **Read and modify only branch `dev`.** Verify the branch and inspect existing files before changes. Never access or modify other branches.
2. Check for concurrent or uncommitted changes and preserve them.
3. Make the **smallest focused change**; avoid unrelated refactoring.
4. Verify each logical change with relevant checks and review its diff.
5. Commit small, verified changes separately, with descriptive English messages.
6. Never force-push, rewrite history, merge branches, or create pull requests without explicit authorization. Push only to `dev` when authorized.
7. Report changed files, tests run, any verification limits, and commit hashes.

## 4. Notebook design: simple and scientific

Plan for exactly two primary EDA notebooks:

- `notebooks/01_hourly_data_quality_assessment.ipynb` — **Stage 1: Hourly Data Quality Assessment**.
- `notebooks/02_daily_climate_exploratory_analysis.ipynb` — **Stage 2: Daily Climate Exploratory Analysis**.

Adapt the EDA Starter template for **readable narrative structure**, and consult `ds-notebook/01_exploratory_data_analysis.ipynb` first for methodology. Neither template's sample code or generic cleaning practices override ERA5-Land scientific requirements.

- Use notebooks for context, methodology, analysis, plots, findings, limitations, and conclusions.
- Keep one-off, simple functions in notebooks. Move repeated or independently testable logic to small Python modules **only when needed**.
- Prefer functions over unnecessary classes, interfaces, patterns, and layers. Apply **KISS and YAGNI first**, then DRY and SOLID where useful. Do not force SOLID onto individual cells.
- Use English for code, identifiers, comments, documentation, and commit messages.
- Keep outputs legible: describe each important figure or table and what the evidence does—and does not—support.
- Avoid saving massive notebook outputs, embedded datasets, or generated artifacts to Git.

## 5. Data access and performance

The intended local input layout is:

```text
data/all/
├── hourly/
│   ├── YYYY_hourly.parquet
│   └── manifest.json
└── daily/
    ├── YYYY_daily.parquet
    └── manifest.json
```

The `data/` directory is ignored by Git. Support a configurable data root so a mounted external drive can use the same layout; do not build cloud-provider integrations prematurely.

Use the small **`utils/data_loader.py`** module with `load_hourly()` and `load_daily()`, returning lazy DuckDB relations. Read the configured Parquet sources directly. Use DuckDB for large scans and aggregations; convert only suitably small results to Pandas for plotting. PyArrow may inspect schemas and metadata.

- Do not materialize the full hourly dataset in memory by default.
- Detect absent files, incomplete years, and manifest/source mismatches explicitly.
- Preserve timestamps, coordinates, units, and missing values. Do not replace NULL/NaN with zero or drop rows merely to simplify analysis.
- Keep the input files read-only; write reports and figures to separate output directories.

## 6. Scientific integrity

Use [the scientific specification](docs/app_description.md) as the authority for study limits, variable meaning, expected grid, and temporal semantics.

- Determine the analysis period dynamically from available files, manifests, and observed timestamps; report gaps and partial coverage. The study bbox is **north 6.1, south 1.9, west 94.9, east 98.3**.
- The expected regular **0.1° grid contains 43 latitudes × 35 longitudes = 1,505 points**, including non-Aceh and marine locations in the bounding rectangle.
- Hourly timestamps are in **UTC**; the daily product uses **UTC+7 local days**. Do not conflate the two.
- Distinguish **missing rows/timestamps**, missing values within existing rows, and **expected land-surface missingness**. An all-NULL grid point does not by itself prove it is a sea point; land/sea classification requires independent spatial evidence.
- Distinguish instantaneous variables from accumulated quantities and derived wind variables; do not apply the same aggregation to all fields.
- Treat extreme values as **investigation candidates**, not automatically removable errors.

Stage 1 must report four evidence-based categories: **Expected Source Characteristics**, **Data Limitations and Incompleteness**, **Anomalies Requiring Investigation**, and **Confirmed Data Quality Issues**. Do not label an issue confirmed without supporting verification.

## 7. Validation and completion

Test focused Python helpers when introduced. For notebooks, validate structure, imports, file-path assumptions, query logic, and key scientific calculations against small representative datasets. Check that large-data queries remain bounded or aggregate before conversion to Pandas.

If full data or an execution environment is unavailable, report precisely what was and was not tested. **When DuckDB or PyArrow cannot be executed in the agent runtime, provide the exact verification command for the user's configured environment instead of requiring installation here or claiming tests passed.** Clearly distinguish user-run results from agent-run checks; reverify whenever code changes. Never fabricate EDA results or claim a dataset is complete without examining its files and manifest.

Preserve upstream authorship, acknowledgements, citations, and relevant license notices. The README must retain the existing Dataquest acknowledgement and credit [CoenMeintjes' data-science notebook templates](https://github.com/CoenMeintjes/data_science_notebook_templates); data attribution for C3S/ECMWF must remain separate from template attribution.

**Core rule:** Small changes on `dev`, simple readable notebooks, immutable sources, reproducible analysis, and scientific claims backed by evidence.
