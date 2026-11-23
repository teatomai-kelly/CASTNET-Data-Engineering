
from pathlib import Path

import pandas as pd


OUTPUT_DIR = Path(__file__).resolve().parents[1] / "outputs" / "tables"

COMPARISONS = [
    (
        "overlap_by_site_year.csv",
        "overlap_by_site_year_rebuilt.csv",
        ["SITE_ID", "YEAR"],
    ),
    (
        "overlap_by_year.csv",
        "overlap_by_year_rebuilt.csv",
        ["YEAR"],
    ),
    (
        "site_metadata_for_overlap.csv",
        "site_metadata_for_overlap_rebuilt.csv",
        ["SITE_ID", "match_status"],
    ),
]


def main():
    # Compare original exploratory outputs with reusable audit outputs.
    for original_name, rebuilt_name, sort_keys in COMPARISONS:
        original = pd.read_csv(OUTPUT_DIR / original_name)
        rebuilt = pd.read_csv(OUTPUT_DIR / rebuilt_name)

        shared_columns = [
            column for column in original.columns
            if column in rebuilt.columns
        ]

        original_check = (
            original[shared_columns]
            .sort_values(sort_keys)
            .reset_index(drop=True)
        )

        rebuilt_check = (
            rebuilt[shared_columns]
            .sort_values(sort_keys)
            .reset_index(drop=True)
        )
        # Treat missing overlap counts as zero for comparison.
        if "sites_in_both" in shared_columns:
            original_check["sites_in_both"] = (
                original_check["sites_in_both"].fillna(0)
            )
            rebuilt_check["sites_in_both"] = (
                rebuilt_check["sites_in_both"].fillna(0)
            )
        pd.testing.assert_frame_equal(
            original_check,
            rebuilt_check,
            check_dtype=False,
            check_exact=False,
            atol=1e-10,
            rtol=1e-10,
        )

        print(f"PASS: {original_name}")
        print(f"      {len(original):,} rows compared")

    # Verify the five weekly flux measurement counts.
    detail = pd.read_csv(
        OUTPUT_DIR / "overlap_by_site_year_rebuilt.csv"
    )

    required_flux_columns = [
        "SO2_FLUX_values",
        "SO4_FLUX_values",
        "NO3_FLUX_values",
        "HNO3_FLUX_values",
        "NH4_FLUX_values",
    ]

    missing = [
        column for column in required_flux_columns
        if column not in detail.columns
    ]

    if missing:
        raise ValueError(f"Missing weekly flux columns: {missing}")

    print("\nPASS: All five weekly flux measurement counts are present.")
    print("\nSUCCESS: Original and rebuilt audits match!")


if __name__ == "__main__":
    main()
