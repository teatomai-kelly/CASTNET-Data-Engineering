from pathlib import Path

import pandas as pd

from castnet.validation.overlap import build_overlap_audits


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "phy-1103_epa_castnet_region4_star"
)

OUTPUT_DIR = PROJECT_ROOT / "outputs" / "tables"


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Load source tables.
    weekly = pd.read_csv(
        DATA_DIR / "castnet_drydep_weekly_region4.csv"
    )

    annual = pd.read_csv(
        DATA_DIR / "castnet_total_deposition_mlm_annual_region4.csv"
    )

    sites = pd.read_csv(
        DATA_DIR / "castnet_site_region4.csv"
    )

    print("Source data loaded successfully.")

    # Build the overlap audits.
    overlap, yearly, site_summary = build_overlap_audits(
        weekly=weekly,
        annual=annual,
        sites=sites,
    )

    # Save rebuilt outputs separately so we can compare
    # them with our original exploratory results.
    overlap.to_csv(
        OUTPUT_DIR / "overlap_by_site_year_rebuilt.csv",
        index=False,
    )

    yearly.to_csv(
        OUTPUT_DIR / "overlap_by_year_rebuilt.csv",
        index=False,
    )

    site_summary.to_csv(
        OUTPUT_DIR / "site_metadata_for_overlap_rebuilt.csv",
        index=False,
    )

    print("\n=== SOURCE ROW COUNTS ===")
    print(f"Weekly records: {len(weekly):,}")
    print(f"Annual records: {len(annual):,}")
    print(f"Site records: {len(sites):,}")

    print("\n=== SITE-YEAR MATCH RESULTS ===")
    print(overlap["match_status"].value_counts().to_string())

    print("\n=== YEARLY COVERAGE ===")
    print(yearly.to_string(index=False))

    print("\n=== OUTPUT FILES ===")
    print("Overlap:", OUTPUT_DIR / "overlap_by_site_year_rebuilt.csv")
    print("Yearly:", OUTPUT_DIR / "overlap_by_year_rebuilt.csv")
    print("Site metadata:", OUTPUT_DIR / "site_metadata_for_overlap_rebuilt.csv")

    print("\nSUCCESS: Real CASTNET overlap audit completed!")


if __name__ == "__main__":
    main()