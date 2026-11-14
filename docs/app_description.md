# ERA5-Land Aceh EDA — Application Description

**Document role: WHAT.** This is the authoritative specification for the study scope, input data, scientific safeguards, planned analyses, technology choices, and acceptance criteria. [AGENTS.md](../AGENTS.md) governs how to work; [README.md](../README.md) describes what currently exists and how to use it.

## 1. Purpose and scope

This project continues the work of [`etl-weather`](https://github.com/esnanta/etl-weather) by conducting reproducible exploratory data analysis (EDA) of **Copernicus Climate Data Store (CDS) ERA5-Land** hourly and daily Parquet data for the Aceh study area. **The analysis period follows the data actually available**, rather than a predetermined set of years.

Two complementary stages serve distinct purposes:

1. **Stage 1 — Hourly Data Quality Assessment:** assess structural, temporal, spatial, and variable-level data quality before drawing scientific conclusions.
2. **Stage 2 — Daily Climate Exploratory Analysis:** characterize rainfall, temperature, moisture, radiation, wind, spatial patterns, and variability over time.

Their findings may inform later feature engineering or clustering, but **clustering/model training is not part of these two EDA stages**.

This repository is an **analytics consumer**, not an ETL pipeline. It reads exported Parquet files and manifests without downloading or transforming source climate data or coupling to producer code.

## 2. Data contract

### 2.1 Study area and expected grid

The extraction bounding box is:

```python
ACEH_BBOX_COORDINATES = {
    "north_lat": 6.1,
    "south_lat": 1.9,
    "east_lon": 98.3,
    "west_lon": 94.9,
}
```

The expected source grid is a regular **0.1° × 0.1°** latitude/longitude grid:

| Measure | Expected count |
| --- | ---: |
| Latitude coordinates | 43 |
| Longitude coordinates | 35 |
| Grid points in the rectangle | **1,505** |

A rectangular bounding box is **not** the administrative Aceh boundary. It includes marine and potentially non-Aceh locations; the total does not mean 1,505 valid land observations. Distinguish observed coordinate coverage from valid-value coverage. Do not infer land-versus-sea classifications solely from missing values.

### 2.2 Time semantics and coverage

- **Hourly** Parquet represents hourly ERA5-Land observations with **UTC timestamps**.
- **Daily** Parquet represents daily observations already aggregated using **UTC+7 calendar days**.
- **Determine the study window from the available Parquet files, manifests, and observed timestamps.** Include whatever years and months are actually present; identify partial years, missing months, and temporal gaps instead of assuming completeness.
- Do not recompute daily products from hourly data as the main EDA source. Cross-checks against hourly values may be used to investigate suspected daily anomalies, without changing the upstream transformation contract.

### 2.3 Input location and provenance

Use this local layout as the default, preserving upstream filenames and manifests:

```text
data/all/
├── hourly/
│   ├── YYYY_hourly.parquet
│   └── manifest.json
└── daily/
    ├── YYYY_daily.parquet
    └── manifest.json
```

The same relative structure may live on another mounted drive through a configurable data root, such as `ERA5_LAND_DATA_DIR`. Source Parquet and manifests are **read-only**, excluded from version control, and copied together. Manifest fields (including available years/months, completion state, source metadata, and hashes) are evidence for provenance checks; validate relevant fields against actual files before making completeness claims.

### 2.4 Variables

Upstream currently exports nine provider variables:

| Field | Meaning | Hourly physical unit | Daily upstream output |
| --- | --- | --- | --- |
| `tp` | Total precipitation | m (accumulated water equivalent) | daily accumulation, mm/day |
| `t2m` | 2 m air temperature | K | daily mean, °C |
| `d2m` | 2 m dewpoint temperature | K | daily mean, °C |
| `swvl1` | Soil moisture, 0–7 cm | m³/m³ | daily mean, m³/m³ |
| `swvl2` | Soil moisture, 7–28 cm | m³/m³ | daily mean, m³/m³ |
| `swvl3` | Soil moisture, 28–100 cm | m³/m³ | daily mean, m³/m³ |
| `ssrd` | Surface solar radiation downwards | J/m² (accumulated) | daily accumulation, J/m²/day |
| `u10` | 10 m eastward wind component | m/s | daily mean, m/s |
| `v10` | 10 m northward wind component | m/s | daily mean, m/s |

The daily export also contains **derived** `wind_speed` (daily mean of hourly vector magnitudes, m/s) and `wind_direction` (direction derived from the daily mean wind vector, degrees clockwise from north, nullable when calm). These are not additional CDS source variables.

Verify actual Parquet column names, types, units, and temporal meanings against the dataset before implementing queries. The hourly `tp` and `ssrd` values must be interpreted according to **ERA5-Land accumulation semantics**, not assumed to be interchangeable with ERA5 hourly accumulation. Do not use generic `groupby(...).mean()` for every variable or use arithmetic means of wind direction angles.

## 3. Stage 1 — Hourly Data Quality Assessment

**Input:** `data/all/hourly/*_hourly.parquet` plus `manifest.json`.

**Objective:** evaluate the integrity, quality, distribution, and temporal-spatial characteristics of the hourly dataset **without altering source data**.

### Required assessments

**Source inventory and schema:** identify existing annual files, sizes, row counts, columns, types, manifest coverage, and provenance/hash discrepancies where checkable.

**Temporal integrity:** compare observed timestamps to expected UTC hourly coverage; measure missing hours, duplicate `(timestamp, latitude, longitude)` combinations, incomplete months/years, and discrepancies between absent rows and NULL values in present rows. Report coverage by year and month.

**Spatial integrity:** verify unique latitude/longitude values, the expected 43 × 35 grid, coordinate ranges and duplicates, coordinate coverage over time, and points that disappear or are incomplete in certain periods.

**Missing values and marine coverage:** report NULL/NaN by variable, point, month, and year. Clearly distinguish:
- missing rows/timestamps;
- missing values at existing coordinates and timestamps;
- persistent all-missing points and intermittent missingness.

Some marine points may legitimately lack ERA5-Land values. Show their spatial patterns **without equating NULL/NaN with sea**. Any definitive land/sea label requires independent spatial evidence (for example, a compatible land-sea mask or trusted boundary).

**Variable quality:** show valid-value counts, summary statistics, distributions, ranges, suspicious values, temporal jumps, and spatial patterns. Extreme weather is not automatically erroneous. Record potential errors for investigation rather than deleting or imputing them.

### Data Quality Report

Produce readable summaries and figures under:

```text
eda/hourly_assessment/
├── reports/
└── figures/
```

Separate findings into:

1. **Expected Source Characteristics**
2. **Data Limitations and Incompleteness**
3. **Anomalies Requiring Investigation**
4. **Confirmed Data Quality Issues**

For each significant finding, document **evidence, interpretation, impact, and recommended follow-up**. Reserve “confirmed” for verified issues, not merely unusual statistics. Report actual results, not hypothetical outcomes.

## 4. Stage 2 — Daily Climate Exploratory Analysis

**Input:** `data/all/daily/*_daily.parquet` plus `manifest.json`; use Stage 1 findings as context.

**Objective:** characterize daily meteorological patterns over the study region and study period while explicitly accounting for data limitations.

Assess:

- descriptive statistics and valid-data coverage for every available variable;
- rainfall distribution, wet-day definitions, and extreme rainfall;
- air temperature and dewpoint characteristics;
- soil moisture across three depths;
- surface solar radiation;
- wind speed and meteorological direction, respecting circular-angle conventions;
- monthly/seasonal patterns and interannual variability across the available time span;
- spatial differences across valid grid points, noting bbox versus administrative boundaries;
- relationships among meteorological variables, with cautious correlation interpretation;
- candidate variables and feature-engineering questions for future research (**without training clustering models**).

Define thresholds (such as wet days or extremes) with scientific justification. Do not treat missing precipitation as zero or mix partial-coverage periods into unqualified comparisons.

Write reports and figures under:

```text
eda/daily_analysis/
├── reports/
└── figures/
```

Each analysis should communicate methods, evidence, interpretation, limitations, and a concise conclusion.

## 5. Notebook and technology design

Use **two primary notebooks**, one per stage:

```text
notebooks/
├── 01_hourly_data_quality_assessment.ipynb
└── 02_daily_climate_exploratory_analysis.ipynb
```

Use [EDA Starter](../template/eda_starter.ipynb.ipynb) to guide narrative sections, clear explanations, and references. Use [the data science EDA notebook](../ds-notebook/01_exploratory_data_analysis.ipynb) as the first methodological reference; adapt generic “cleaning” examples to immutable scientific assessment.

**Performance design:** DuckDB is the main engine for scanning and aggregating large Parquet files without loading all hourly rows into Pandas. PyArrow may inspect schema and metadata. Use Pandas/NumPy and plotting libraries on reduced results. Avoid adding Polars/Dask or cloud-specific integrations without a demonstrated need.

Prefer **one small module with `load_hourly()` and `load_daily()` functions**, returning lazy DuckDB relations using the configured data root. Keep simple, one-off analysis code in notebook cells. Extract reusable or testable functions only when useful; **KISS, DRY, and YAGNI** constrain SOLID-driven abstraction.

## 6. Acceptance criteria

**Stage 1 is accepted when:**
- existing files/manifests and actual data coverage are enumerated and checked;
- expected versus observed temporal and spatial coverage are explained;
- NULL/NaN, absent observations, and persistent missing grid points are quantified and mapped;
- possible marine-related missingness is shown but not asserted as proven land/sea classification without independent evidence;
- variable distributions and questionable values are assessed without mutating source data;
- the Data Quality Report uses all four evidence categories and records remaining uncertainty;
- the notebook and its important computations are reproducible on available input data.

**Stage 2 is accepted when:**
- the daily notebook covers the listed variable families, spatial/temporal variability, and variable relationships;
- daily UTC+7 semantics and actual available coverage are respected;
- plots and summaries have explanations, units, limitations, and references as needed;
- Stage 1 findings inform interpretation and missing data are not silently dropped or zero-filled;
- the notebook produces traceable reports/figures and does not modify input files.

**Cross-cutting:** notebooks remain readable, resource-conscious, simple, and separate from the upstream ETL implementation. Any unavailable inputs or unexecuted checks must be stated explicitly.

## 7. Scientific references and attribution

Use the supplied ECMWF/Copernicus documentation and authoritative ERA5-Land guidance when interpreting accumulated variables, analysis/forecast distinctions, temperature, and winds. Note that several supplied documents describe **ERA5**, which is related to but not identical with **ERA5-Land**; never transfer dataset-specific timing rules without checking applicability.

Preserve upstream notebook acknowledgements and cite the CDS/ECMWF dataset appropriately in published analysis. Specific acknowledgement and current repository setup belong in [README.md](../README.md).
