# Stage119 Hydrograph QA Review

Created: 2026-08-25 19:17

## Scope

Reviewed embedded flood hydrographs in:

`D:\01 Project\Development\HMS\Narmada\04_Calibration_Validation\Stage_112_Advanced_Hydrology_Analytics_Webmap\narmada-advanced-hydrology-analytics-webmap.html`

The dashboard contains `13` exported LS04G simulated hydrograph
series. The simulation control period is `2023-09-10T00:00:00+05:30` to
`2023-09-25T23:00:00+05:30` at `60` minute interval, so each complete series
should contain `384` hourly ordinates.

## Checks Performed

- Series length against HMS control period.
- Hour index monotonicity and 1-hour interval regularity.
- Non-negative flow values.
- Recomputed peak discharge and peak hour against embedded `flowSummary`.
- Recomputed event volume against embedded `flowSummary`.
- Observed-vs-simulated peak ratio review where observed peak values exist.
- Dashboard interpretation check: direct exported hydrograph versus downstream-linked hydrograph.

## Findings

1. The embedded LS04G hydrograph arrays are internally consistent for plotting.
   Peak/hour/volume checks are written to `stage119_hydrograph_series_qc.csv`.

2. The page does **not** contain full observed hydrograph time series. It contains
   simulated LS04G hydrographs plus observed peak metadata for some GD sites.
   Therefore the chart should not be interpreted as observed-vs-simulated
   hydrograph calibration unless observed time-series are added.

3. Several displayed feature hydrographs may be downstream-linked rather than
   exact feature-level hydrographs. This is useful for navigation but can be
   misleading if read as the selected feature's own hydrograph.

4. Observed/simulated peak mismatch remains the main correctness issue for
   public interpretation. Highest available ratios:

| Feature | HMS element | Observed cumec | LS04G cumec | Ratio |
|---|---|---:|---:|---:|
| Handia | R_R_11 | 10300.0 | 26244.166 | 2.548 |
| Narmadapuram | R_R_13 | 11850.0 | 21222.04 | 1.791 |
| Barmanghat | R_R_19 | 9232.0 | 9950.211 | 1.078 |
| Sandia | R_R_16 | 11639.0 | 12160.425 | 1.045 |

## Issue Counts

{
  "Medium": 1,
  "High": 1
}

## Recommendation

For public correctness, keep the hydrographs labelled as **LS04G simulated
hydrographs**. Add a visible warning when a selected feature is using a
downstream-linked hydrograph. For model-calibration correctness, the next data
fix should attach observed discharge time-series at Handia, Narmadapuram,
Sandia, Barmanghat and available CWC gauges so the dashboard can plot observed
and simulated lines on the same time axis.
