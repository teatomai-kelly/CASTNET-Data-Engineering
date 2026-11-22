# CASTNET Data Engineering

An environmental data engineering project using CASTNET (Clean Air Status and Trends Network) data. The initial workspace is based on Project Sulfur starter data kit **phy-1103_epa_castnet_region4_star** (kit 129).

## Project goals

- Inspect and profile the source data before making analytical assumptions.
- Build reproducible ingestion and transformation workflows.
- Preserve source values and document cleaning, joins, exclusions, and quality checks.
- Develop a defensible environmental analysis from multiple CASTNET data sources.
- Present findings with traceable calculations and clear limitations.

## Dataset

The selected starter kit contains CASTNET Region 4 materials, including weekly dry chemistry and dry deposition data, hourly ozone observations, wet concentration measurements, annual total deposition summaries, site and plant reference tables, monthly cloud data, column metadata, and supporting PDF documents.

**Do not commit the downloaded raw dataset or PDFs to this repository.** Keep the original files locally in `data/raw/`; this repository includes code, documentation, and lightweight metadata only. Confirm provenance and licensing details from the starter kit's provenance notes before redistributing any source data.

## Repository layout

```text
CASTNET-Data-Engineering/
├── data/
│   ├── raw/                 # Local source files; gitignored
│   ├── interim/             # Intermediate outputs; gitignored
│   ├── processed/           # Curated outputs; gitignored
│   └── metadata/            # Safe, lightweight source/column metadata
├── docs/
│   ├── data_dictionary/
│   ├── design/
│   └── decisions/
├── notebooks/               # Exploration and profiling
├── src/
│   └── castnet/
│       ├── ingestion/
│       ├── validation/
│       ├── transformations/
│       ├── analysis/
│       └── reporting/
├── sql/
│   ├── staging/
│   ├── transformations/
│   └── marts/
├── tests/
│   ├── unit/
│   └── data_quality/
├── outputs/
│   ├── figures/             # Generated locally; gitignored
│   └── reports/             # Generated locally; gitignored
├── .gitignore
└── pyproject.toml
```

## Getting started on macOS

1. Open this repository in VS Code (or another editor).
2. Create and activate a Python virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. Install the project in editable mode:
   ```bash
   python -m pip install --upgrade pip
   python -m pip install -e ".[dev]"
   ```
4. Place the extracted starter-kit files in `data/raw/`. Keep their original filenames.
5. Start by profiling schemas, row counts, date ranges, missingness, key uniqueness, and join coverage. Do not make cleaning assumptions until the source data and documentation support them.

## Source files observed in the starter-kit preview

The registry preview showed files including:

- `castnet_cloud_month_region4.csv`
- `castnet_drychem_weekly_region4.csv`
- `castnet_drydep_weekly_region4.csv`
- `castnet_ozone_hourly_2023_region4.csv`
- `castnet_total_deposition_mlm_annual_region4.csv`
- `castnet_wet_concentration_region4.csv`
- `castnet_plant.csv`
- `castnet_site_plant_summary_region4.csv`
- `castnet_site_region4.csv`
- `columninfo_drychem.csv`
- `columninfo_drydep_week_web.csv`
- `columninfo_ozone_2023.csv`
- `columninfo_site.csv`
- `columninfo_total_deposition_mlm.csv`
- `columninfo_wet_concentration.csv`
- `castnet_2024_annual_report_executive_summary.pdf`
- `castnet_modernization_plan_2024_2027.pdf`

Verify the exact archive contents against the extracted local folder. Registry previews may show only a subset of rows and fields.

## Working principles

- Never treat a file's presence as proof that it belongs in the analysis.
- Reconcile data grain and keys before joining datasets.
- Distinguish missing, flagged, censored, and measured values rather than silently treating them alike.
- Validate important transformations with explicit checks.
- Keep analysis reproducible and conclusions tied to evidence.

## Status

Initial workspace scaffold created. Next: inspect the extracted files, establish provenance, profile the source tables, and choose a defensible analytical question.
