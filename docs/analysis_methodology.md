# CASTNET Region 4 Deposition Trend Analysis: Methodology

## 1. Objective

Assess annual total nitrogen and sulfur deposition trends in the
CASTNET Region 4 extract using consistent monitoring-site cohorts.
Evaluate whether observed regional patterns remain consistent when
the selected site population and analysis period are changed.

## 2. Source data

The analysis uses these three CSV tables from the supplied data kit:

| File | Purpose |
|---|---|
| `castnet_total_deposition_mlm_annual_region4.csv` | Annual nitrogen and sulfur deposition measures |
| `castnet_drydep_weekly_region4.csv` | Weekly dry-deposition measurements and site-year coverage |
| `castnet_site_region4.csv` | Site metadata and geographic attributes |

The associated column definitions were consulted to identify field
meaning, measurement units, and time grain.

Annual total deposition is not interchangeable with weekly dry
deposition. The CASTNET modernization plan explains that total
atmospheric deposition estimates combine CASTNET air-quality
observations, NADP precipitation chemistry measurements, and EPA
CMAQ modeled values.

## 3. Data preparation

- Source CSVs were read without modifying the raw files.
- `SITE_ID` values were converted to trimmed strings for consistent joins.
- `YEAR` values were converted to numeric values.
- Deposition measures were converted to numeric values.
- Missing measurement values were retained as missing rather than
  being replaced with zero.
- Annual and weekly data were compared at the `SITE_ID` and `YEAR`
  level.
- Weekly records were checked using the candidate key
  `SITE_ID`, `YEAR`, and `WEEK`.

The candidate weekly key had no duplicate records in the primary
11-site cohort.

## 4. Cohort selection

The analysis uses fixed cohorts to avoid interpreting changes in
the mix of reporting sites as though they were environmental trends.

A site was eligible for a cohort when it had:
1. Annual records with both `N_TOTAL` and `S_TOTAL` populated in
   every year of the selected period.
2. At least one weekly dry-deposition record in every year of that
   period.

| Cohort | Period | Sites |
|---|---:|---:|
| Primary | 2000–2017 | 11 |
| Sensitivity | 2010–2017 | 16 |

The primary cohort provides the longer trend period. The
sensitivity cohort tests whether patterns are broadly consistent
over a later period with a larger site population.

## 5. Annual aggregation

For each cohort and year, the arithmetic mean and median of
`N_TOTAL` and `S_TOTAL` were calculated across the selected sites.

Each site contributes one annual value to the cohort mean.
All selected sites have populated annual nitrogen and sulfur
values in every year of their cohort.

Units:
- `N_TOTAL`: kg-N/ha
- `S_TOTAL`: kg-S/ha

First-to-last percentage change was calculated as:

`(last_year_mean - first_year_mean) / first_year_mean * 100`

This is a comparison of cohort means, not the average of each
site's individual percentage change.

## 6. Trend assessment

The following methods were used:

- Ordinary least squares (OLS) linear regression to estimate the
  descriptive annual slope.
- Kendall's tau to assess monotonic association between year and
  the annual cohort mean.
- Theil-Sen slope to estimate a robust trend slope, with a
  95% confidence interval.
- Newey-West heteroskedasticity-and-autocorrelation-consistent
  (HAC) standard errors for the linear regression, evaluated with
  maximum lags of 1 and 2.

Annual time-series lag-one autocorrelation and the
Durbin-Watson statistic on OLS residuals were examined as
diagnostics.

HAC estimates are treated as robustness checks. They do not
remove all limitations associated with short, autocorrelated
annual time series.

## 7. Weekly coverage assessment

For the primary cohort, weekly data were summarized by site and
year. The assessment included:

- Number of weekly records.
- Number of distinct weeks.
- Percentage of existing weekly rows with nonmissing flux values.
- Relative week coverage compared with the highest number of
  distinct weeks observed at any primary-cohort site in the
  same year.

Relative week coverage is a within-dataset comparison. It is
not a confirmation of the official expected sampling schedule.

## 8. Quality and interpretation rules

- A row existing in both annual and weekly tables does not
  automatically mean all measurements are valid.
- Missing values are not treated as zero.
- Annual total deposition is not calculated by summing weekly
  dry-deposition values.
- The trend analysis uses nonmissing annual total values for
  the selected fixed cohorts.
- This analysis does not apply additional measurement-flag
  screening beyond the nonmissing-value checks described above.
- Statistical significance is not interpreted as proof of
  causation.
- Findings are specific to the selected Region 4 sites and
  analysis periods.

## 9. Reproducibility

The analysis outputs are stored under `outputs/`. The raw data
remain under `data/raw/`.

Key outputs include:
- `annual_fixed_cohort_trends.csv`
- `annual_fixed_cohort_trend_summary.csv`
- `weekly_primary_cohort_coverage.csv`
- `annual_statistical_trend_tests.csv`
- `site_level_trend_slopes.csv`
- `site_trend_direction_summary.csv`
- `annual_hac_trend_robustness.csv`
- `primary_cohort_deposition_trends.png`
- `cohort_indexed_deposition_comparison.png`
