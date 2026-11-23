import pandas as pd
import pytest

from castnet.analysis.deposition_trends import (
    identify_consistent_sites,
    summarize_annual_cohort,
    validate_source_keys,
)


def test_identify_consistent_sites_requires_both_sources_every_year():
    annual = pd.DataFrame([
        {"SITE_ID": "A", "YEAR": 2020, "N_TOTAL": 1, "S_TOTAL": 2},
        {"SITE_ID": "A", "YEAR": 2021, "N_TOTAL": 2, "S_TOTAL": 3},
        {"SITE_ID": "B", "YEAR": 2020, "N_TOTAL": 1, "S_TOTAL": 2},
        {"SITE_ID": "B", "YEAR": 2021, "N_TOTAL": 2, "S_TOTAL": 3},
        {"SITE_ID": "C", "YEAR": 2020, "N_TOTAL": 1, "S_TOTAL": 2},
        {"SITE_ID": "C", "YEAR": 2021, "N_TOTAL": 2, "S_TOTAL": None},
    ])

    weekly = pd.DataFrame([
        {"SITE_ID": "A", "YEAR": 2020},
        {"SITE_ID": "A", "YEAR": 2021},
        {"SITE_ID": "B", "YEAR": 2020},
        {"SITE_ID": "C", "YEAR": 2020},
        {"SITE_ID": "C", "YEAR": 2021},
    ])

    result = identify_consistent_sites(
        annual, weekly, start_year=2020, end_year=2021
    )

    assert result == ["A"]


def test_summarize_annual_cohort_calculates_site_means():
    annual = pd.DataFrame([
        {"SITE_ID": "A", "YEAR": 2020, "N_TOTAL": 1, "S_TOTAL": 2},
        {"SITE_ID": "B", "YEAR": 2020, "N_TOTAL": 3, "S_TOTAL": 4},
        {"SITE_ID": "A", "YEAR": 2021, "N_TOTAL": 3, "S_TOTAL": 4},
        {"SITE_ID": "B", "YEAR": 2021, "N_TOTAL": 5, "S_TOTAL": 6},
    ])

    result = summarize_annual_cohort(
        annual,
        sites=["A", "B"],
        start_year=2020,
        end_year=2021,
        cohort_label="Test cohort",
    )

    assert result["N_TOTAL_mean"].tolist() == [2.0, 4.0]
    assert result["S_TOTAL_mean"].tolist() == [3.0, 5.0]
    assert result["sites_with_rows"].tolist() == [2, 2]
    assert result["expected_sites"].tolist() == [2, 2]


def test_validate_source_keys_rejects_duplicate_annual_records():
    annual = pd.DataFrame([
        {"SITE_ID": "A", "YEAR": 2020},
        {"SITE_ID": "A", "YEAR": 2020},
    ])

    weekly = pd.DataFrame(columns=["SITE_ID", "YEAR", "WEEK"])

    with pytest.raises(ValueError, match="duplicate SITE_ID/YEAR"):
        validate_source_keys(annual, weekly)


def test_validate_source_keys_rejects_duplicate_weekly_records():
    annual = pd.DataFrame([
        {"SITE_ID": "A", "YEAR": 2020},
    ])

    weekly = pd.DataFrame([
        {"SITE_ID": "A", "YEAR": 2020, "WEEK": 1},
        {"SITE_ID": "A", "YEAR": 2020, "WEEK": 1},
    ])

    with pytest.raises(ValueError, match="duplicate SITE_ID/YEAR/WEEK"):
        validate_source_keys(annual, weekly)