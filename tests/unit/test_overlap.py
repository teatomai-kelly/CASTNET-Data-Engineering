
import pandas as pd
import pytest

from castnet.validation.overlap import build_overlap_audits


def sample_inputs():
    weekly = pd.DataFrame({
        "SITE_ID": ["A", "A", "B"],
        "YEAR": [2020, 2020, 2020],
        "WEEK": [1, 2, 1],
    })

    annual = pd.DataFrame({
        "SITE_ID": ["A", "C"],
        "YEAR": [2020, 2020],
        "N_TOTAL": [3.2, 4.1],
        "S_TOTAL": [1.4, 2.1],
    })

    sites = pd.DataFrame({
        "SITE_ID": ["A", "B", "C"],
        "SITE_NAME": ["Site A", "Site B", "Site C"],
        "STATE": ["GA", "TN", "AL"],
    })

    return weekly, annual, sites


def test_overlap_classifies_site_year_records():
    weekly, annual, sites = sample_inputs()

    overlap, yearly, site_summary = build_overlap_audits(
        weekly, annual, sites
    )

    actual_statuses = dict(
        zip(overlap["SITE_ID"], overlap["match_status"])
    )

    assert actual_statuses == {
        "A": "present_in_both",
        "B": "weekly_only",
        "C": "annual_only",
    }

    assert yearly.loc[0, "sites_in_both"] == 1
    assert yearly.loc[0, "weekly_sites"] == 2
    assert yearly.loc[0, "annual_sites"] == 2

    assert len(site_summary) == 3


def test_overlap_does_not_modify_source_data():
    weekly, annual, sites = sample_inputs()

    original_weekly = weekly.copy(deep=True)
    original_annual = annual.copy(deep=True)
    original_sites = sites.copy(deep=True)

    build_overlap_audits(weekly, annual, sites)

    pd.testing.assert_frame_equal(weekly, original_weekly)
    pd.testing.assert_frame_equal(annual, original_annual)
    pd.testing.assert_frame_equal(sites, original_sites)


def test_overlap_rejects_missing_required_columns():
    weekly, annual, sites = sample_inputs()
    weekly = weekly.drop(columns=["WEEK"])

    with pytest.raises(ValueError, match="Weekly data missing columns"):
        build_overlap_audits(weekly, annual, sites)
