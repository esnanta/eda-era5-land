# ERA5-Land Exploratory Data Analysis — Aceh

This project continues [`etl-weather`](https://github.com/esnanta/etl-weather) with exploratory data analysis (EDA) of existing **Copernicus CDS ERA5-Land** hourly and daily Parquet data for the Aceh study area. The period covered by each analysis is determined by the **data actually available**, not a fixed range of years. This repository does not download or transform Copernicus source data.

The project is being developed from existing EDA and data-science notebook templates. Original authors and contributors are acknowledged below.

## Project status

**Documentation and design are being established.** The two ERA5-Land analysis notebooks and their supporting loader are **planned**, not yet implemented. Existing template notebooks are references, not completed climate analyses. No results or data-completeness claims should be inferred from this README.

The scientific scope, data contracts, and acceptance criteria are defined in [docs/app_description.md](docs/app_description.md). Development instructions are in [AGENTS.md](AGENTS.md).

## Planned analyses

| Stage | Notebook (planned) | Main purpose |
| --- | --- | --- |
| **1 — Hourly Data Quality Assessment** | `notebooks/01_hourly_data_quality_assessment.ipynb` | Evaluate hourly file/manifest coverage, timestamps, 0.1° spatial grid, NULL/NaN, missing records, distributions, and anomalies |
| **2 — Daily Climate Exploratory Analysis** | `notebooks/02_daily_climate_exploratory_analysis.ipynb` | Explore daily rainfall, temperature, dewpoint, soil moisture, solar radiation, wind, seasonal and interannual variation, and spatial differences |

Stage 1 will report **Expected Source Characteristics**, **Data Limitations and Incompleteness**, **Anomalies Requiring Investigation**, and **Confirmed Data Quality Issues**. Both stages will keep inputs unchanged and explain limitations in each finding.

These notebooks will use the [EDA Starter notebook](template/eda_starter.ipynb.ipynb) for readable presentation and [the data-science EDA notebook](ds-notebook/01_exploratory_data_analysis.ipynb) as the first methodology reference. They are not required to copy template code or generic data-cleaning steps.

## Study area and data

| Item | Scope |
| --- | --- |
| Dataset | Copernicus Climate Data Store (CDS) ERA5-Land (`reanalysis-era5-land`) |
| Analysis period | Determined from available Parquet files, manifests, and observed timestamps |
| Bounding box | North 6.1°, south 1.9°, west 94.9°, east 98.3° |
| Expected grid | Regular 0.1° × 0.1°; 43 latitude values × 35 longitude values = **1,505 grid points** |
| Hourly time | UTC |
| Daily time | UTC+7 calendar days, calculated upstream |
| File format | Parquet with accompanying `manifest.json` |

The bounding box is rectangular: it includes sea and may include areas outside Aceh's administrative boundary. **Not every grid point is expected to have a valid land-surface measurement.** NULL/NaN values must be assessed, not automatically classified as errors or automatically identified as sea. Actual year/month coverage must be checked against the files and manifests.

Upstream provider variables are `tp`, `t2m`, `d2m`, `swvl1`, `swvl2`, `swvl3`, `ssrd`, `u10`, and `v10`. The daily export additionally contains derived `wind_speed` and `wind_direction`. Variable meanings, units, and time-aggregation constraints are specified in [docs/app_description.md](docs/app_description.md).

## Dataset placement

Place the **existing hourly and daily Parquet exports** and their manifests in:

```text
data/
└── all/
    ├── hourly/
    │   ├── YYYY_hourly.parquet
    │   └── manifest.json
    └── daily/
        ├── YYYY_daily.parquet
        └── manifest.json
```

`YYYY` represents any year for which an export is available. The EDA must discover existing files and report actual coverage, partial years, and gaps rather than assuming a predetermined period. Preserve files and manifests together, including their original contents. The repository's `.gitignore` excludes `data/`: do not commit Parquet files, manifests, or other large datasets.

A future small loader module will expose **`load_hourly()`** and **`load_daily()`**, returning DuckDB relations. Local `data/all/` will be the default; an environment variable such as `ERA5_LAND_DATA_DIR` will allow the same directory structure to reside on another accessible drive. No cloud synchronization service is currently implemented.

## Environment setup

The repository currently includes `setup_env.sh` for creating a Python virtual environment:

```bash
sh setup_env.sh
source myenv/bin/activate
```

The script **only creates the virtual environment**; it does not install analysis dependencies. Python, Jupyter, DuckDB, PyArrow, Pandas, NumPy, and plotting dependencies will be configured as notebook implementation is added. Do not assume a pinned `requirements.txt` or finished run command exists yet.

The planned large-data approach is to query and aggregate Parquet with **DuckDB**, and transfer only modest-sized results to Pandas for plotting. Avoid reading the entire hourly dataset into a Pandas DataFrame.

## Repository guide

| Location | Current role |
| --- | --- |
| [AGENTS.md](AGENTS.md) | Instructions for coding agents |
| [docs/app_description.md](docs/app_description.md) | EDA scope, scientific requirements, and acceptance criteria |
| [docs/repo_guidelines.md](docs/repo_guidelines.md) | Branch, review, verification, and commit discipline |
| [docs/python_se_principle.md](docs/python_se_principle.md) | Python design principles (SOLID guided by DRY/KISS/YAGNI) |
| [template/eda_starter.ipynb.ipynb](template/eda_starter.ipynb.ipynb) | Original EDA writing and presentation template |
| [ds-notebook/](ds-notebook/) | Data-science notebook examples from CoenMeintjes |
| [era5_land_notebook.ipynb](era5_land_notebook.ipynb) | Existing inherited notebook; not either of the planned EDA stages |
| [setup_env.sh](setup_env.sh) | Creates the `myenv` virtual environment |

Planned outputs from the completed notebooks will be under `eda/hourly_assessment/{reports,figures}/` and `eda/daily_analysis/{reports,figures}/`. Those output directories are **not evidence of completed analyses**.

## Scientific data attribution

This project uses data produced by the **Copernicus Climate Data Store (CDS)** and operated through the **European Centre for Medium-Range Weather Forecasts (ECMWF)**. When publishing analysis, cite the specific ERA5-Land CDS catalogue entry and relevant documentation according to the provider's citation guidance. Notebook templates and data sources are separate forms of contribution..

- [ERA5-Land hourly data — CDS](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land)
- [The family of ERA5 datasets — ECMWF](https://confluence.ecmwf.int/spaces/CKB/pages/181127817/The+family+of+ERA5+datasets)

## Acknowledgements and project origins

This repository builds on an existing **EDA Starter Jupyter Notebook Template**, with original template authorship associated with [@chuawt](https://chuawt.github.io). We preserve the original acknowledgement below:

Many thanks to the entire Dataquest community especially @Elena_Kosourova for your support and @gorelovaelizaveta01 for [your template](https://community.dataquest.io/t/template-for-jupyter-notebooks/567750) inspiration.

Additional thanks to **[CoenMeintjes](https://github.com/CoenMeintjes)** for [Data Science Jupyter Notebook Templates](https://github.com/CoenMeintjes/data_science_notebook_templates), used as reference material in the `ds-notebook/` directory and as a methodological starting point for the EDA notebooks.

These acknowledgements recognize the contributions of the upstream template creators; the climate-analysis scope and code are being developed separately. Existing copyright and license obligations, where applicable, must still be respected.
