# CASTNET Data Engineering

An environmental data engineering and analytics project using data from the **Clean Air Status and Trends Network (CASTNET)**.

The project uses Project Sulfur starter data kit **129 — `phy-1103_epa_castnet_region4_star`** — to develop reproducible data workflows, evaluate environmental monitoring data quality, and investigate atmospheric deposition trends across CASTNET Region 4.

## Project Goals

- Inspect and profile source data before making analytical assumptions.
- Develop reproducible ingestion, validation, and transformation workflows.
- Preserve source values and document cleaning, joins, exclusions, and quality checks.
- Evaluate environmental trends using multiple CASTNET data sources.
- Produce traceable analytical results, visualizations, and technical documentation.
- Clearly communicate analytical assumptions, limitations, and findings.

## Dataset

The selected starter kit contains CASTNET Region 4 materials, including:

- Weekly dry chemistry and dry deposition measurements.
- Hourly ozone observations for 2023.
- Wet precipitation chemistry measurements.
- Annual total nitrogen and sulfur deposition estimates.
- Site and plant reference tables.
- Monthly cloud measurements.
- Column definitions and supporting CASTNET reports.

**Source data policy:** Do not commit the downloaded raw dataset or original PDFs to this repository. Keep original files locally in `data/raw/`. Include only appropriate code, documentation, metadata, and reviewed derived outputs. Confirm source provenance and licensing before redistribution.

## Current Analytical Focus

The current analysis investigates annual total nitrogen (`N_TOTAL`) and total sulfur (`S_TOTAL`) deposition trends across CASTNET Region 4.

The analysis uses two fixed monitoring-site cohorts:

| Cohort | Analysis period | Number of sites |
|---|---:|---:|
| Primary | 2000–2017 | 11 |
| Sensitivity | 2010–2017 | 16 |

Fixed cohorts were selected to reduce the influence of changing site populations on comparisons over time. Weekly dry deposition data are also evaluated to assess monitoring coverage and data completeness.

### Preliminary Findings

The primary 11-site cohort shows declining annual mean deposition between 2000 and 2017:

- Total nitrogen deposition decreased approximately **36.8%**.
- Total sulfur deposition decreased approximately **72.4%**.
- All 11 sites showed negative Theil–Sen slopes for both measures.

The 2010–2017 sensitivity cohort also showed a downward sulfur trend, while the nitrogen result was less conclusive and more sensitive to the statistical method.

These findings are specific to the selected sites and analysis periods. They do not establish the causes of the observed changes.

See the methodology and findings documentation for analytical details, statistical results, and limitations.

## Repository Structure

```text
CASTNET-Data-Engineering/
├── data/
│   ├── raw/                 # Original source files; gitignored
│   ├── interim/             # Intermediate data products
│   ├── processed/           # Curated analytical datasets
│   └── metadata/            # Lightweight source and column metadata
├── docs/
│   ├── data_dictionary/
│   ├── design/
│   ├── decisions/
│   ├── analysis_methodology.md
│   ├── analysis_findings.md
│   └── source_context.txt
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
│   ├── figures/             # Analytical visualizations
│   └── reports/             # Derived reports and summaries
├── .gitignore
├── pyproject.toml
└── requirements.txt
```

Generated analysis outputs currently include:

- `annual_fixed_cohort_trends.csv`
- `annual_statistical_trend_tests.csv`
- `annual_hac_trend_robustness.csv`
- `weekly_primary_cohort_coverage.csv`
- `site_level_trend_slopes.csv`
- `site_trend_direction_summary.csv`
- `primary_cohort_deposition_trends.png`
- `cohort_indexed_deposition_comparison.png`

## Getting Started on macOS

The development environment uses Conda and Python 3.12.

1. Clone the repository and open it in VS Code.
2. Create and activate the Conda environment:

```bash
conda create -n castnet python=3.12 -y
conda activate castnet
```

3. Install project dependencies:

```bash
python -m pip install -r requirements.txt
```

4. Place the extracted starter-kit files in:

```text
data/raw/phy-1103_epa_castnet_region4_star/
```

5. Preserve original filenames and source values.
6. Begin analysis by inspecting schemas, row counts, date ranges, missingness, candidate key uniqueness, and join coverage.

## Working Principles

- Never treat a file's presence as proof that it belongs in an analysis.
- Reconcile data grain and candidate keys before joining datasets.
- Distinguish missing, flagged, censored, and measured values.
- Do not silently replace missing measurements with zero.
- Validate important transformations with explicit checks.
- Keep raw source data separate from derived analytical outputs.
- Do not treat annual total deposition estimates as interchangeable with weekly dry deposition measurements.
- Keep analytical conclusions traceable to reproducible calculations.

## Project Status

**Current phase: Exploratory analysis and validation**

Completed:
- Initial repository and development environment setup.
- Starter-kit file inventory and source-data profiling.
- Data dictionary and supporting documentation review.
- Site and year coverage analysis.
- Fixed-cohort selection for annual deposition comparisons.
- Preliminary nitrogen and sulfur trend analysis.
- Statistical robustness checks and analytical visualizations.

Next:
- Consolidate exploratory workflows into reusable project scripts.
- Add automated data validation and unit tests.
- Finalize methodology and findings documentation.
- Review repository organization, reproducibility, and deliverables.
- Validate the completed project against the project requirements.

