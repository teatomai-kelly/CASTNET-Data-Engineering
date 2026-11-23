"""Reproducible CASTNET Region 4 annual deposition trend analysis."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm
from matplotlib.ticker import FormatStrFormatter, MultipleLocator
from scipy import stats
from statsmodels.stats.stattools import durbin_watson

DEFAULT_DATA_DIR = Path("data/raw/phy-1103_epa_castnet_region4_star")
DEFAULT_OUTPUT_DIR = Path("outputs")

ANNUAL_FILE = "castnet_total_deposition_mlm_annual_region4.csv"
WEEKLY_FILE = "castnet_drydep_weekly_region4.csv"
SITE_FILE = "castnet_site_region4.csv"

COHORT_PERIODS = {
    "primary": (2000, 2017),
    "sensitivity": (2010, 2017),
}

DEPOSITION_FIELDS = ["N_TOTAL", "S_TOTAL"]
WEEKLY_FLUX_FIELDS = [
    "SO2_FLUX",
    "SO4_FLUX",
    "NO3_FLUX",
    "HNO3_FLUX",
    "NH4_FLUX",
]


def normalize_source_data(
    annual: pd.DataFrame,
    weekly: pd.DataFrame,
    sites: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Standardize site identifiers, years, and measurement types."""
    annual = annual.copy()
    weekly = weekly.copy()
    sites = sites.copy()

    for frame in (annual, weekly, sites):
        if "SITE_ID" not in frame.columns:
            raise ValueError("A source table is missing SITE_ID.")
        frame["SITE_ID"] = frame["SITE_ID"].astype("string").str.strip()

    for frame in (annual, weekly):
        if "YEAR" not in frame.columns:
            raise ValueError("A source table is missing YEAR.")
        frame["YEAR"] = pd.to_numeric(
            frame["YEAR"], errors="coerce"
        ).astype("Int64")

    for column in ["N_TOTAL", "S_TOTAL", "N_DRY", "S_DRY", "N_WET", "S_WET"]:
        if column in annual.columns:
            annual[column] = pd.to_numeric(
                annual[column], errors="coerce"
            )

    for column in WEEKLY_FLUX_FIELDS:
        if column in weekly.columns:
            weekly[column] = pd.to_numeric(
                weekly[column], errors="coerce"
            )

    for column in ["DATEON", "DATEOFF"]:
        if column in weekly.columns:
            weekly[column] = pd.to_datetime(
                weekly[column], errors="coerce"
            )

    return annual, weekly, sites


def validate_source_keys(
    annual: pd.DataFrame,
    weekly: pd.DataFrame,
) -> None:
    """Check candidate uniqueness keys before aggregation."""
    annual_duplicates = annual.duplicated(
        ["SITE_ID", "YEAR"], keep=False
    ).sum()

    weekly_duplicates = weekly.duplicated(
        ["SITE_ID", "YEAR", "WEEK"], keep=False
    ).sum()

    if annual_duplicates:
        raise ValueError(
            f"Annual source contains {annual_duplicates} rows with "
            "duplicate SITE_ID/YEAR keys."
        )

    if weekly_duplicates:
        raise ValueError(
            f"Weekly source contains {weekly_duplicates} rows with "
            "duplicate SITE_ID/YEAR/WEEK keys."
        )


def identify_consistent_sites(
    annual: pd.DataFrame,
    weekly: pd.DataFrame,
    start_year: int,
    end_year: int,
) -> list[str]:
    """Find sites with annual N/S totals and weekly records in every year."""
    annual_valid = annual.dropna(
        subset=["SITE_ID", "YEAR", "N_TOTAL", "S_TOTAL"]
    )
    weekly_valid = weekly.dropna(
        subset=["SITE_ID", "YEAR"]
    )

    eligible_by_year = []

    for year in range(start_year, end_year + 1):
        annual_sites = set(
            annual_valid.loc[
                annual_valid["YEAR"] == year, "SITE_ID"
            ].dropna()
        )
        weekly_sites = set(
            weekly_valid.loc[
                weekly_valid["YEAR"] == year, "SITE_ID"
            ].dropna()
        )
        eligible_by_year.append(annual_sites & weekly_sites)

    if not eligible_by_year:
        return []

    consistent = set.intersection(*eligible_by_year)
    return sorted(consistent)


def summarize_annual_cohort(
    annual: pd.DataFrame,
    sites: list[str],
    start_year: int,
    end_year: int,
    cohort_label: str,
) -> pd.DataFrame:
    """Calculate annual mean and median deposition for a fixed site cohort."""
    years = list(range(start_year, end_year + 1))

    subset = annual[
        annual["YEAR"].isin(years)
        & annual["SITE_ID"].isin(sites)
    ]

    yearly = (
        subset.groupby("YEAR")
        .agg(
            sites_with_rows=("SITE_ID", "nunique"),
            N_sites_with_values=("N_TOTAL", "count"),
            S_sites_with_values=("S_TOTAL", "count"),
            N_TOTAL_mean=("N_TOTAL", "mean"),
            N_TOTAL_median=("N_TOTAL", "median"),
            S_TOTAL_mean=("S_TOTAL", "mean"),
            S_TOTAL_median=("S_TOTAL", "median"),
        )
        .reindex(years)
        .rename_axis("YEAR")
        .reset_index()
    )

    yearly["cohort"] = cohort_label
    yearly["expected_sites"] = len(sites)

    return yearly


def calculate_trend_statistics(
    yearly: pd.DataFrame,
    cohort_label: str,
) -> tuple[list[dict], list[dict]]:
    """Calculate OLS, Kendall, Theil-Sen, and site-level trend statistics."""
    trend_results = []
    site_results = []

    for metric in DEPOSITION_FIELDS:
        mean_column = f"{metric}_mean"
        data = yearly.dropna(subset=[mean_column])

        x = data["YEAR"].to_numpy(dtype=float)
        y = data[mean_column].to_numpy(dtype=float)

        if len(y) < 3:
            continue

        linear = stats.linregress(x, y)
        kendall = stats.kendalltau(x, y)
        theil = stats.theilslopes(y, x, alpha=0.95)

        trend_results.append({
            "cohort": cohort_label,
            "metric": metric,
            "years_analyzed": len(y),
            "first_year": int(x[0]),
            "last_year": int(x[-1]),
            "first_year_mean": y[0],
            "last_year_mean": y[-1],
            "percent_change_first_to_last": (
                (y[-1] - y[0]) / y[0] * 100 if y[0] != 0 else np.nan
            ),
            "OLS_slope_per_year": linear.slope,
            "OLS_p_value": linear.pvalue,
            "Kendall_tau": kendall.statistic,
            "Kendall_p_value": kendall.pvalue,
            "Theil_Sen_slope_per_year": theil.slope,
            "Theil_Sen_CI_lower": theil.low_slope,
            "Theil_Sen_CI_upper": theil.high_slope,
            "lag1_autocorrelation": pd.Series(y).autocorr(lag=1),
        })

    return trend_results, site_results


def calculate_site_slopes(
    annual: pd.DataFrame,
    sites: list[str],
    start_year: int,
    end_year: int,
    cohort_label: str,
) -> list[dict]:
    """Calculate individual site-level Theil-Sen slopes."""
    subset = annual[
        annual["YEAR"].between(start_year, end_year)
        & annual["SITE_ID"].isin(sites)
    ]

    results = []

    for site in sites:
        site_data = subset[subset["SITE_ID"] == site]

        for metric in DEPOSITION_FIELDS:
            site_metric = (
                site_data[["YEAR", metric]]
                .dropna()
                .sort_values("YEAR")
            )

            if len(site_metric) < 3:
                continue

            estimate = stats.theilslopes(
                site_metric[metric].to_numpy(dtype=float),
                site_metric["YEAR"].to_numpy(dtype=float),
                alpha=0.95,
            )

            slope = estimate.slope

            results.append({
                "cohort": cohort_label,
                "metric": metric,
                "SITE_ID": site,
                "years_available": len(site_metric),
                "Theil_Sen_slope_per_year": slope,
                "direction": (
                    "decreasing" if slope < 0
                    else "increasing" if slope > 0
                    else "flat"
                ),
            })

    return results


def calculate_hac_robustness(
    yearly: pd.DataFrame,
    cohort_label: str,
) -> list[dict]:
    """Calculate Newey-West HAC standard errors at lags 1 and 2."""
    results = []

    for metric in DEPOSITION_FIELDS:
        data = yearly.dropna(subset=[f"{metric}_mean"])

        x = data["YEAR"].to_numpy(dtype=float)
        y = data[f"{metric}_mean"].to_numpy(dtype=float)

        if len(y) < 5:
            continue

        design = sm.add_constant(x - x.mean())
        ordinary = sm.OLS(y, design).fit()
        residual_dw = durbin_watson(ordinary.resid)

        for lag in (1, 2):
            robust = sm.OLS(y, design).fit(
                cov_type="HAC",
                cov_kwds={
                    "maxlags": lag,
                    "use_correction": True,
                },
            )

            confidence_interval = robust.conf_int()

            results.append({
                "cohort": cohort_label,
                "metric": metric,
                "observations": len(y),
                "HAC_maxlags": lag,
                "slope_per_year": robust.params[1],
                "HAC_standard_error": robust.bse[1],
                "HAC_p_value": robust.pvalues[1],
                "HAC_CI_lower": confidence_interval[1, 0],
                "HAC_CI_upper": confidence_interval[1, 1],
                "ordinary_OLS_p_value": ordinary.pvalues[1],
                "Durbin_Watson": residual_dw,
            })

    return results


def build_weekly_coverage(
    weekly: pd.DataFrame,
    primary_sites: list[str],
    start_year: int,
    end_year: int,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Build site-year completeness and yearly primary-cohort summaries."""
    subset = weekly[
        weekly["SITE_ID"].isin(primary_sites)
        & weekly["YEAR"].between(start_year, end_year)
    ].copy()

    duplicate_count = subset.duplicated(
        ["SITE_ID", "YEAR", "WEEK"]
    ).sum()

    if duplicate_count:
        raise ValueError(
            f"Primary cohort has {duplicate_count} duplicate weekly keys."
        )

    flux_fields = [
        column for column in WEEKLY_FLUX_FIELDS
        if column in subset.columns
    ]

    aggregations = {
        "weekly_rows": ("WEEK", "size"),
        "distinct_weeks": ("WEEK", "nunique"),
    }
    for column in flux_fields:
        aggregations[f"{column}_values_present"] = (column, "count")

    site_year = (
        subset.groupby(["YEAR", "SITE_ID"])
        .agg(**aggregations)
        .reset_index()
    )

    for column in flux_fields:
        site_year[f"{column}_value_pct_of_rows"] = (
            site_year[f"{column}_values_present"]
            / site_year["weekly_rows"] * 100
        ).round(1)

    max_weeks = (
        site_year.groupby("YEAR")["distinct_weeks"]
        .max()
        .rename("max_weeks_observed_at_a_site")
    )

    site_year = site_year.merge(
        max_weeks, on="YEAR", how="left"
    )
    site_year["relative_week_coverage_pct"] = (
        site_year["distinct_weeks"]
        / site_year["max_weeks_observed_at_a_site"] * 100
    ).round(1)

    yearly_aggregations = {
        "sites_reporting": ("SITE_ID", "nunique"),
        "median_distinct_weeks": ("distinct_weeks", "median"),
        "median_relative_week_coverage": (
            "relative_week_coverage_pct", "median"
        ),
    }

    for column in flux_fields:
        yearly_aggregations[f"median_{column}_value_pct"] = (
            f"{column}_value_pct_of_rows", "median"
        )

    yearly = (
        site_year.groupby("YEAR")
        .agg(**yearly_aggregations)
        .reset_index()
        .round(1)
    )

    return site_year, yearly


def build_annual_completeness(annual: pd.DataFrame) -> pd.DataFrame:
    """Summarize annual row and measurement availability by year."""
    fields = [
        field for field in
        ["N_TOTAL", "S_TOTAL", "N_DRY", "S_DRY", "N_WET", "S_WET"]
        if field in annual.columns
    ]

    aggregations = {
        "annual_rows": ("SITE_ID", "size"),
        "annual_sites": ("SITE_ID", "nunique"),
    }
    for field in fields:
        aggregations[f"{field}_present"] = (field, "count")

    return (
        annual.groupby("YEAR")
        .agg(**aggregations)
        .reset_index()
        .sort_values("YEAR")
    )


def build_overlap_audits(
    weekly: pd.DataFrame,
    annual: pd.DataFrame,
    sites: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Compare weekly and annual site-year records and attach site metadata."""
    weekly_aggregations = {
        "weekly_rows": ("WEEK", "size"),
        "distinct_weeks": ("WEEK", "nunique"),
    }
    if "DATEON" in weekly.columns:
        weekly_aggregations["first_week"] = ("DATEON", "min")
    if "DATEOFF" in weekly.columns:
        weekly_aggregations["last_week"] = ("DATEOFF", "max")

    weekly_site_year = (
        weekly.dropna(subset=["SITE_ID", "YEAR"])
        .groupby(["SITE_ID", "YEAR"])
        .agg(**weekly_aggregations)
        .reset_index()
    )

    annual_site_year = (
        annual.dropna(subset=["SITE_ID", "YEAR"])
        .groupby(["SITE_ID", "YEAR"])
        .agg(
            annual_rows=("SITE_ID", "size"),
            N_TOTAL_present=("N_TOTAL", "count"),
            S_TOTAL_present=("S_TOTAL", "count"),
        )
        .reset_index()
    )

    overlap = weekly_site_year.merge(
        annual_site_year,
        on=["SITE_ID", "YEAR"],
        how="outer",
        indicator=True,
    )

    overlap["match_status"] = overlap["_merge"].map({
        "both": "present_in_both",
        "left_only": "weekly_only",
        "right_only": "annual_only",
    })
    overlap = overlap.drop(columns="_merge")

    weekly_by_year = (
        weekly_site_year.groupby("YEAR")
        .agg(
            weekly_sites=("SITE_ID", "nunique"),
            weekly_site_years=("SITE_ID", "size"),
            weekly_rows=("weekly_rows", "sum"),
        )
    )

    annual_by_year = (
        annual_site_year.groupby("YEAR")
        .agg(
            annual_sites=("SITE_ID", "nunique"),
            annual_site_years=("SITE_ID", "size"),
            annual_N_TOTAL_present=("N_TOTAL_present", "sum"),
            annual_S_TOTAL_present=("S_TOTAL_present", "sum"),
        )
    )

    yearly = weekly_by_year.join(
        annual_by_year, how="outer"
    ).fillna(0)

    both = overlap[overlap["match_status"] == "present_in_both"]
    yearly["sites_in_both"] = (
        both.groupby("YEAR")["SITE_ID"].nunique()
    ).fillna(0).astype(int)

    yearly = yearly.reset_index().sort_values("YEAR")

    metadata_columns = [
        column for column in
        ["SITE_ID", "SITE_NAME", "STATE", "COUNTY", "ACTIVE", "INACTIVE"]
        if column in sites.columns
    ]
    site_lookup = sites[metadata_columns].drop_duplicates("SITE_ID")

    site_summary = (
        overlap[["SITE_ID", "match_status"]]
        .drop_duplicates()
        .merge(site_lookup, on="SITE_ID", how="left")
    )

    return overlap, yearly, site_summary


def create_figures(
    yearly_results: pd.DataFrame,
    figure_dir: Path,
) -> None:
    """Generate absolute and indexed annual deposition trend figures."""
    figure_dir.mkdir(parents=True, exist_ok=True)

    primary_label = "Primary: 2000-2017 (11 sites)"
    sensitivity_label = "Sensitivity: 2010-2017 (16 sites)"

    primary = yearly_results[
        yearly_results["cohort"] == primary_label
    ].sort_values("YEAR")

    fig, axes = plt.subplots(2, 1, figsize=(11, 8))

    for ax, metric, title, unit in [
        (
            axes[0], "N_TOTAL_mean",
            "Annual mean total nitrogen deposition", "kg-N/ha"
        ),
        (
            axes[1], "S_TOTAL_mean",
            "Annual mean total sulfur deposition", "kg-S/ha"
        ),
    ]:
        ax.plot(primary["YEAR"], primary[metric], marker="o", linewidth=2)
        ax.set_title(title)
        ax.set_xlabel("Year")
        ax.set_ylabel(unit)
        ax.xaxis.set_major_locator(MultipleLocator(2))
        ax.xaxis.set_major_formatter(FormatStrFormatter("%.0f"))
        ax.grid(True, alpha=0.3)

    fig.suptitle(
        "CASTNET Region 4: Annual Deposition Trends",
        fontsize=15,
        fontweight="bold",
    )
    fig.text(
        0.5, 0.01,
        "Equal-weighted annual mean across the same 11 sites, 2000-2017.",
        ha="center",
        fontsize=9,
    )
    fig.tight_layout(rect=[0, 0.04, 1, 0.95])
    fig.savefig(
        figure_dir / "primary_cohort_deposition_trends.png",
        dpi=200,
        bbox_inches="tight",
    )
    plt.close(fig)

    fig, axes = plt.subplots(2, 1, figsize=(11, 8))

    for ax, metric, title in [
        (axes[0], "N_TOTAL_mean", "Indexed total nitrogen deposition"),
        (axes[1], "S_TOTAL_mean", "Indexed total sulfur deposition"),
    ]:
        for label, legend in [
            (primary_label, "2000-2017 cohort | 11 sites | baseline 2000"),
            (
                sensitivity_label,
                "2010-2017 cohort | 16 sites | baseline 2010"
            ),
        ]:
            group = yearly_results[
                yearly_results["cohort"] == label
            ].sort_values("YEAR").copy()

            baseline = group[metric].dropna().iloc[0]
            group["indexed_value"] = group[metric] / baseline * 100

            ax.plot(
                group["YEAR"],
                group["indexed_value"],
                marker="o",
                linewidth=2,
                label=legend,
            )

        ax.axhline(100, linestyle="--", linewidth=1)
        ax.set_title(title)
        ax.set_xlabel("Year")
        ax.set_ylabel("Index (baseline = 100)")
        ax.xaxis.set_major_locator(MultipleLocator(2))
        ax.xaxis.set_major_formatter(FormatStrFormatter("%.0f"))
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=8)

    fig.suptitle(
        "CASTNET Region 4: Relative Deposition Trends",
        fontsize=15,
        fontweight="bold",
    )
    fig.text(
        0.5, 0.01,
        "Each cohort is indexed to its own first-year mean; "
        "lines compare relative change, not absolute levels.",
        ha="center",
        fontsize=9,
    )
    fig.tight_layout(rect=[0, 0.04, 1, 0.95])
    fig.savefig(
        figure_dir / "cohort_indexed_deposition_comparison.png",
        dpi=200,
        bbox_inches="tight",
    )
    plt.close(fig)


def run_analysis(
    data_dir: Path = DEFAULT_DATA_DIR,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
) -> None:
    """Run the complete deposition analysis and write tables and figures."""
    data_dir = Path(data_dir)
    output_dir = Path(output_dir)
    table_dir = output_dir / "tables"
    figure_dir = output_dir / "figures"

    table_dir.mkdir(parents=True, exist_ok=True)
    figure_dir.mkdir(parents=True, exist_ok=True)

    annual_path = data_dir / ANNUAL_FILE
    weekly_path = data_dir / WEEKLY_FILE
    site_path = data_dir / SITE_FILE

    for path in (annual_path, weekly_path, site_path):
        if not path.exists():
            raise FileNotFoundError(f"Required source file not found: {path}")

    annual = pd.read_csv(annual_path)
    weekly = pd.read_csv(weekly_path)
    sites = pd.read_csv(site_path)

    annual, weekly, sites = normalize_source_data(
        annual, weekly, sites
    )
    validate_source_keys(annual, weekly)

    yearly_outputs = []
    trend_outputs = []
    site_outputs = []
    hac_outputs = []
    cohort_sites = {}

    for cohort_key, (start_year, end_year) in COHORT_PERIODS.items():
        selected_sites = identify_consistent_sites(
            annual, weekly, start_year, end_year
        )

        if not selected_sites:
            raise ValueError(
                f"No consistent sites found for {cohort_key}: "
                f"{start_year}-{end_year}."
            )

        cohort_sites[cohort_key] = selected_sites
        label = (
            f"Primary: {start_year}-{end_year} ({len(selected_sites)} sites)"
            if cohort_key == "primary"
            else
            f"Sensitivity: {start_year}-{end_year} "
            f"({len(selected_sites)} sites)"
        )

        yearly = summarize_annual_cohort(
            annual,
            selected_sites,
            start_year,
            end_year,
            label,
        )
        yearly_outputs.append(yearly)

        trends, _ = calculate_trend_statistics(yearly, label)
        trend_outputs.extend(trends)

        site_outputs.extend(
            calculate_site_slopes(
                annual, selected_sites, start_year, end_year, label
            )
        )
        hac_outputs.extend(calculate_hac_robustness(yearly, label))

        print(
            f"{cohort_key}: {len(selected_sites)} sites "
            f"({', '.join(selected_sites)})"
        )

    annual_trends = pd.concat(yearly_outputs, ignore_index=True)
    trend_statistics = pd.DataFrame(trend_outputs)
    site_statistics = pd.DataFrame(site_outputs)
    hac_statistics = pd.DataFrame(hac_outputs)

    site_directions = (
        site_statistics.groupby(["cohort", "metric", "direction"])
        .size()
        .unstack(fill_value=0)
        .reset_index()
    )

    trend_summary = trend_statistics[
        ["cohort", "metric", "years_analyzed", "OLS_slope_per_year"]
    ].rename(columns={
        "years_analyzed": "years_with_values",
        "OLS_slope_per_year": "descriptive_linear_slope_per_year",
    })

    primary_start, primary_end = COHORT_PERIODS["primary"]
    weekly_site_year, weekly_primary_summary = build_weekly_coverage(
        weekly,
        cohort_sites["primary"],
        primary_start,
        primary_end,
    )

    annual_completeness = build_annual_completeness(annual)

    overlap, overlap_by_year, site_metadata = build_overlap_audits(
        weekly, annual, sites
    )

    tables = {
        "annual_fixed_cohort_trends.csv": annual_trends,
        "annual_trend_visualization_data.csv": annual_trends,
        "annual_fixed_cohort_trend_summary.csv": trend_summary,
        "annual_statistical_trend_tests.csv": trend_statistics,
        "annual_hac_trend_robustness.csv": hac_statistics,
        "site_level_trend_slopes.csv": site_statistics,
        "site_trend_direction_summary.csv": site_directions,
        "weekly_primary_cohort_site_year_completeness.csv": weekly_site_year,
        "weekly_primary_cohort_coverage_by_year.csv": weekly_primary_summary,
        "annual_year_completeness.csv": annual_completeness,
    }

    for filename, frame in tables.items():
        frame.to_csv(table_dir / filename, index=False)

    create_figures(annual_trends, figure_dir)

    print("\nAnalysis completed.")
    print(f"Tables saved to: {table_dir}")
    print(f"Figures saved to: {figure_dir}")
    print("\nHAC trend results:")
    if not hac_statistics.empty:
        print(
            hac_statistics[
                [
                    "cohort",
                    "metric",
                    "HAC_maxlags",
                    "slope_per_year",
                    "HAC_p_value",
                    "HAC_CI_lower",
                    "HAC_CI_upper",
                ]
            ].round(4).to_string(index=False)
        )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run CASTNET Region 4 deposition trend analysis."
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=DEFAULT_DATA_DIR,
        help="Folder containing the extracted CASTNET source CSV files.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Folder for generated analytical tables and figures.",
    )
    args = parser.parse_args()
    run_analysis(args.data_dir, args.output_dir)


if __name__ == "__main__":
    main()
