import pandas as pd

def build_overlap_audits(
    weekly: pd.DataFrame,
    annual: pd.DataFrame,
    sites: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Compare weekly and annual site-year records and attach site metadata.

    Returns:
        overlap: Site-year comparison between weekly and annual data.
        yearly: Annual summary of site and measurement coverage.
        site_summary: Site-year status with available site metadata.
    """

    # Validate required columns.
    required_weekly = {"SITE_ID", "YEAR", "WEEK"}
    required_annual = {"SITE_ID", "YEAR", "N_TOTAL", "S_TOTAL"}
    required_sites = {"SITE_ID"}

    if not required_weekly.issubset(weekly.columns):
        raise ValueError(
            f"Weekly data missing columns: {required_weekly - set(weekly.columns)}"
        )

    if not required_annual.issubset(annual.columns):
        raise ValueError(
            f"Annual data missing columns: {required_annual - set(annual.columns)}"
        )

    if not required_sites.issubset(sites.columns):
        raise ValueError("Site metadata must contain SITE_ID.")

    # Work on copies so the original dataframes remain unchanged.
    weekly = weekly.copy()
    annual = annual.copy()
    sites = sites.copy()

    # Standardize join fields.
    for df in (weekly, annual, sites):
        df["SITE_ID"] = df["SITE_ID"].astype("string").str.strip()

    weekly["YEAR"] = pd.to_numeric(weekly["YEAR"], errors="coerce")
    annual["YEAR"] = pd.to_numeric(annual["YEAR"], errors="coerce")

    # Aggregate weekly records to one row per site and year.
    weekly_aggregations = {
        "weekly_rows": ("WEEK", "size"),
        "distinct_weeks": ("WEEK", "nunique"),
    }
    # Count available weekly flux measurements.
    flux_columns = [
        "SO2_FLUX",
        "SO4_FLUX",
        "NO3_FLUX",
        "HNO3_FLUX",
        "NH4_FLUX",
    ]

    for column in flux_columns:
        if column in weekly.columns:
            weekly_aggregations[f"{column}_values"] = (
                column,
                "count",
            )
    if "DATEON" in weekly.columns:
        weekly["DATEON"] = pd.to_datetime(
            weekly["DATEON"], errors="coerce"
        )
        weekly_aggregations["first_week"] = ("DATEON", "min")

    if "DATEOFF" in weekly.columns:
        weekly["DATEOFF"] = pd.to_datetime(
            weekly["DATEOFF"], errors="coerce"
        )
        weekly_aggregations["last_week"] = ("DATEOFF", "max")

    weekly_site_year = (
        weekly.dropna(subset=["SITE_ID", "YEAR"])
        .groupby(["SITE_ID", "YEAR"])
        .agg(**weekly_aggregations)
        .reset_index()
    )

    # Aggregate annual records to one row per site and year.
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

    # Compare weekly and annual site-year coverage.
    overlap = weekly_site_year.merge(
        annual_site_year,
        on=["SITE_ID", "YEAR"],
        how="outer",
        indicator=True,
    )

    overlap["match_status"] = overlap["_merge"].map(
        {
            "both": "present_in_both",
            "left_only": "weekly_only",
            "right_only": "annual_only",
        }
    )

    overlap = overlap.drop(columns="_merge")

    # Summarize weekly coverage by year.
    weekly_by_year = (
        weekly_site_year.groupby("YEAR")
        .agg(
            weekly_sites=("SITE_ID", "nunique"),
            weekly_site_years=("SITE_ID", "size"),
            weekly_rows=("weekly_rows", "sum"),
            median_weeks_per_site=("distinct_weeks", "median"),
        )
    )

    # Summarize annual coverage by year.
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
        annual_by_year,
        how="outer",
    )

    yearly["sites_in_both"] = (
        overlap.loc[overlap["match_status"] == "present_in_both"]
        .groupby("YEAR")["SITE_ID"]
        .nunique()
    )

    yearly = yearly.fillna(0).reset_index()
    yearly["sites_in_both"] = yearly["sites_in_both"].astype(int)
    yearly = yearly.sort_values("YEAR")

    # Attach available site metadata.
    site_columns = [
        column
        for column in [
            "SITE_ID",
            "SITE_NAME",
            "STATE",
            "COUNTY",
            "ACTIVE",
            "INACTIVE",
        ]
        if column in sites.columns
    ]

    site_lookup = sites[site_columns].drop_duplicates("SITE_ID")

    site_summary = (
        overlap[["SITE_ID", "match_status"]]
        .drop_duplicates()
        .merge(site_lookup, on="SITE_ID", how="left")
    )

    return overlap, yearly, site_summary
