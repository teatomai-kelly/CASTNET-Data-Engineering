# CASTNET Region 4 Deposition Trends: Findings

## 1. Executive summary

The fixed 11-site cohort shows a substantial decline in annual
mean total nitrogen and sulfur deposition from 2000 through 2017.
The sulfur decline is larger than the nitrogen decline.

A later 16-site sensitivity cohort from 2010 through 2017 also
shows a clear downward sulfur pattern. Its nitrogen pattern is
weaker and more sensitive to the statistical method.

These findings describe the selected sites and periods. They do
not establish a causal explanation for the observed changes.

## 2. Primary cohort: 2000–2017

The primary cohort contains 11 sites with annual nitrogen and
sulfur values and weekly dry-deposition records throughout the
selected period.

| Measure | 2000 mean | 2017 mean | First-to-last change |
|---|---:|---:|---:|
| Total nitrogen | 6.459 kg-N/ha | 4.082 kg-N/ha | -36.8% |
| Total sulfur | 7.934 kg-S/ha | 2.190 kg-S/ha | -72.4% |

All 11 sites had negative Theil-Sen slopes for both nitrogen and
sulfur.

### Primary cohort trend statistics

| Measure | OLS slope per year | Theil-Sen slope per year | Kendall tau |
|---|---:|---:|---:|
| Total nitrogen | -0.1567 | -0.1531 | -0.7386 |
| Total sulfur | -0.3982 | -0.4009 | -0.8431 |

Both Kendall trend tests had p-values below 0.001. The Theil-Sen
95% confidence intervals were:

- Nitrogen: -0.2001 to -0.1003 kg-N/ha per year.
- Sulfur: -0.4537 to -0.3379 kg-S/ha per year.

### HAC robustness results

| Measure | HAC lag | Slope | 95% confidence interval | p-value |
|---|---:|---:|---:|---:|
| Nitrogen | 1 | -0.1567 | -0.2044 to -0.1090 | <0.001 |
| Nitrogen | 2 | -0.1567 | -0.1998 to -0.1137 | <0.001 |
| Sulfur | 1 | -0.3982 | -0.4793 to -0.3171 | <0.001 |
| Sulfur | 2 | -0.3982 | -0.4818 to -0.3147 | <0.001 |

The negative slopes and confidence intervals excluding zero
remain consistent under both HAC lag settings.

## 3. Sensitivity cohort: 2010–2017

The sensitivity cohort contains 16 sites.

| Measure | 2010 mean | 2017 mean | First-to-last change |
|---|---:|---:|---:|
| Total nitrogen | 4.620 kg-N/ha | 4.308 kg-N/ha | -6.8% |
| Total sulfur | 4.433 kg-S/ha | 2.306 kg-S/ha | -48.0% |

Site-level Theil-Sen slope directions:
- Nitrogen: 12 decreasing sites and 4 increasing sites.
- Sulfur: 15 decreasing sites and 1 increasing site.

### Sensitivity cohort trend statistics

| Measure | OLS slope per year | Theil-Sen slope per year | Kendall tau |
|---|---:|---:|---:|
| Total nitrogen | -0.1236 | -0.1039 | -0.5714 |
| Total sulfur | -0.3383 | -0.3271 | -0.8571 |

Nitrogen's Theil-Sen 95% confidence interval is -0.2622 to
0.0554 kg-N/ha per year, which includes zero. Its Kendall
p-value is 0.061. The OLS p-value is 0.102.

The HAC nitrogen results are more method-sensitive:
- Lag 1: p = 0.0230; 95% CI = -0.2303 to -0.0170.
- Lag 2: p = 0.0054; 95% CI = -0.2107 to -0.0366.

Given the eight annual observations and disagreement among
methods, the sensitivity nitrogen result should be described
as a less conclusive downward pattern, not as definitive
evidence of a statistically significant decline.

For sulfur, the Theil-Sen 95% confidence interval is
-0.4645 to -0.2345 kg-S/ha per year, and Kendall's p-value
is 0.0017. Both HAC confidence intervals also exclude zero.

## 4. Weekly data coverage

For the primary 11-site cohort during 2000–2017:

- All 11 sites had weekly records in every year.
- Each site-year contained 52 or 53 distinct weeks.
- No duplicate `SITE_ID`, `YEAR`, `WEEK` records were found.
- Relative week coverage was 100% in every year under the
  within-cohort maximum-week reference.
- Median nonmissing flux-value coverage was generally 100% for
  the reported components, with some site-year medians of
  98.1%.

The relative-week metric is not an official completeness
percentage against a documented expected sampling calendar.
It should be interpreted only as a comparison within this
extract.

## 5. Interpretation

The strongest and most consistent result is the decline in
total sulfur deposition. This pattern appears in the longer
primary cohort, the later sensitivity cohort, and the
site-level trend directions.

Total nitrogen deposition also declines across the primary
cohort, with all 11 sites showing negative Theil-Sen slopes.
The shorter sensitivity period provides less conclusive
evidence for nitrogen.

The indexed chart compares relative change within each cohort.
The cohorts have different baseline years and different site
populations; the indexed lines should not be interpreted as
absolute comparisons between cohorts.

## 6. Limitations

1. The analysis covers selected CASTNET Region 4 sites, not
   every CASTNET location.
2. Fixed-cohort selection requires available annual nitrogen
   and sulfur values and weekly records in each year. This
   selection may favor sites with more complete records.
3. The primary analysis has 18 annual observations; the
   sensitivity analysis has only 8.
4. Annual time-series observations may be autocorrelated.
   HAC standard errors are a robustness check, not a complete
   solution to small-sample time-series limitations.
5. The sensitivity nitrogen inference varies by method.
6. Weekly dry-deposition measurements and annual total
   deposition estimates have different time grains and
   measurement inputs. They should not be treated as
   interchangeable.
7. This analysis does not establish the causes of deposition
   changes or attribute them to a particular policy.
8. Additional quality-flag screening and formal assessment
   against an official expected weekly sampling schedule
   would be needed for a more comprehensive quality review.

## 7. Figures

- `outputs/primary_cohort_deposition_trends.png`
- `outputs/cohort_indexed_deposition_comparison.png`

The first figure shows annual mean deposition across the
primary fixed cohort. The second shows relative change from
each cohort's own baseline year.
