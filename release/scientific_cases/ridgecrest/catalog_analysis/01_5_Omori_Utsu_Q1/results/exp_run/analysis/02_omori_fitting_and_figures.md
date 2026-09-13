## Scientific Purpose

This task implemented the primary Omori-type comparison for the Ridgecrest interevent period between the Mw 6.4 and Mw 7.1 mainshocks, restricted to the fixed Mw 7.1 fault-zone corridor and its north/south subdivisions. The scientific target was to test whether, later in the interevent period, the northern part of the Mw 7.1 fault zone exhibits systematically smaller pure power-law Omori exponents (`p`) than the southern part.

The analysis used the requested cumulative period endpoints after the Mw 6.4 origin time (`T=0`): 0.30, 0.50, 0.68, 0.732, 0.85, 1.00, 1.10, 1.22, and 1.404 day, with the primary magnitude threshold `M >= 3.0`. The three primary comparison domains were:
- Entire fixed Mw 7.1 corridor,
- Northern corridor subset north of 35.72°N,
- Southern corridor subset south of 35.72°N.

A secondary robustness check repeated the north/south split at 35.70°, 35.72°, and 35.74°N.

## Method and Implementation Evidence

The task outputs show that the implemented model was the requested cumulative pure power-law Omori rate model,
`lambda(t) = K * t^(-p)`,
fit by maximum likelihood for each domain and each cumulative endpoint. The primary fit table records fitted `p`, `K`, log-likelihood, the effective time range used, and event counts for all 27 primary windows (3 domains × 9 periods), with all windows marked successful in this run:
- `<PACKAGE_ROOT>/results/exp_run/outputs/02_omori_fitting_and_figures/primary_fit_table.csv`
- `<PACKAGE_ROOT>/results/exp_run/outputs/02_omori_fitting_and_figures/final_merged_primary_results.csv`

Bootstrap uncertainty estimation was also implemented as requested. Run metadata states 1000 bootstrap replicates, and the merged results table includes bootstrap median `p`, 2.5 percentile, 97.5 percentile, and bootstrap success accounting:
- `<PACKAGE_ROOT>/results/exp_run/outputs/02_omori_fitting_and_figures/bootstrap_summary.csv`
- `<PACKAGE_ROOT>/results/exp_run/outputs/02_omori_fitting_and_figures/final_merged_primary_results.csv`
- `<PACKAGE_ROOT>/results/exp_run/outputs/02_omori_fitting_and_figures/run_metadata.json`

The handling of the `t=0` singularity was explicit rather than implicit: each fit window records a positive `t_min_used_days`, corresponding to the first event time retained in that cumulative window. For example, the entire-area fits use `t_min_used_days = 0.001421` day, and the northern-domain fits use `t_min_used_days = 0.002203` day in the earliest windows. This is documented in:
- `<PACKAGE_ROOT>/results/exp_run/outputs/02_omori_fitting_and_figures/primary_fit_table.csv`
- `<PACKAGE_ROOT>/results/exp_run/outputs/02_omori_fitting_and_figures/fit_input_audit_table.csv`

The requested low-count marking rule for the northern area was implemented. In the primary 35.72° split, the earliest northern window at 0.30 day has `N=19` and is flagged `low_count_open_circle = True`; later northern windows exceed 20 events and are not flagged:
- `<PACKAGE_ROOT>/results/exp_run/outputs/02_omori_fitting_and_figures/final_merged_primary_results.csv`
- `<PACKAGE_ROOT>/results/exp_run/outputs/02_omori_fitting_and_figures/main_two_panel_omori_comparison.png`

The main figure and support table confirm that panel b used the entire-area fit for the final 1.404-day cumulative period, with observed binned rates on log-log axes and an overlaid fitted curve:
- `<PACKAGE_ROOT>/results/exp_run/outputs/02_omori_fitting_and_figures/main_two_panel_omori_comparison.png`
- `<PACKAGE_ROOT>/results/exp_run/outputs/02_omori_fitting_and_figures/panel_b_rate_curve_support.csv`

The split-line robustness analysis was saved separately and kept secondary, matching the requested workflow:
- `<PACKAGE_ROOT>/results/exp_run/outputs/02_omori_fitting_and_figures/split_sensitivity_results.csv`
- `<PACKAGE_ROOT>/results/exp_run/outputs/02_omori_fitting_and_figures/split_sensitivity_summary.png`

## Key Results and Evidence Files

### 1. Entire-corridor interevent decay is consistently sub-unity and relatively stable

The entire fixed Mw 7.1 corridor shows stable pure power-law Omori exponents through the interevent period, mostly in the range `p ≈ 0.70–0.81`. Specifically, fitted `p` progresses from 0.770 at 0.30 day, 0.811 at 0.50 day, 0.787 at 0.732 day, drops modestly to 0.696 at 0.85 day, and ends at 0.739 by 1.404 day. The corresponding final bootstrap summary is median `p = 0.748`, 95% interval `[0.641, 0.860]`, with `N = 106`.
Evidence:
- `<PACKAGE_ROOT>/results/exp_run/outputs/02_omori_fitting_and_figures/final_merged_primary_results.csv`
- `<PACKAGE_ROOT>/results/exp_run/outputs/02_omori_fitting_and_figures/main_two_panel_omori_comparison.png`

Panel b visually supports this result: the observed entire-area rate declines approximately as a straight power-law trend on log-log axes, and the plotted annotation reports `p = 0.74 [0.64, 0.86]` for the final 1.404-day window. The binned rate support table provides the observed and fitted rates used for this panel.
Evidence:
- `<PACKAGE_ROOT>/results/exp_run/outputs/02_omori_fitting_and_figures/main_two_panel_omori_comparison.png`
- `<PACKAGE_ROOT>/results/exp_run/outputs/02_omori_fitting_and_figures/panel_b_rate_curve_support.csv`

### 2. Under the primary 35.72° split, north and south are similar in early to mid cumulative periods, but the north becomes lower later

The primary north-south comparison at 35.72° shows that the earliest cumulative window is not evidence for smaller northern `p`; rather, the north is initially higher than the south. At 0.30 day, the north has `p_fit = 0.976` versus south `0.713`, but the north also has only `N = 19` and is explicitly flagged as a low-count/open-circle point. By 0.50 and 0.68 day, the north and south become very similar (`0.862` vs `0.791`; `0.801` vs `0.794`).
Evidence:
- `<PACKAGE_ROOT>/results/exp_run/outputs/02_omori_fitting_and_figures/north_vs_south_primary_comparison_35p72.csv`
- `<PACKAGE_ROOT>/results/exp_run/outputs/02_omori_fitting_and_figures/final_merged_primary_results.csv`
- `<PACKAGE_ROOT>/results/exp_run/outputs/02_omori_fitting_and_figures/main_two_panel_omori_comparison.png`

After about 0.732–0.85 day, the primary pattern changes. At 0.732 day the two are still nearly identical (`north 0.787`, `south 0.799`). From 0.85 day onward, the northern `p` drops below the southern `p` and remains lower through the late interevent period:
- 0.85 day: north 0.567, south 0.785
- 1.00 day: north 0.579, south 0.805
- 1.10 day: north 0.611, south 0.805
- 1.22 day: north 0.648, south 0.805
- 1.404 day: north 0.583, south 0.858

The north-minus-south fitted differences are therefore negative in all of these later windows, ranging from about `-0.16` to `-0.27`, with the largest separation at the final 1.404-day endpoint (`-0.274` in fitted `p`; `-0.267` in bootstrap median).
Evidence:
- `<PACKAGE_ROOT>/results/exp_run/outputs/02_omori_fitting_and_figures/north_vs_south_primary_comparison_35p72.csv`
- `<PACKAGE_ROOT>/results/exp_run/outputs/02_omori_fitting_and_figures/main_two_panel_omori_comparison.png`

This directly supports the requested qualitative interpretation: north and south are broadly similar through the earlier cumulative periods, while the north tends to lower `p` values later in the interevent period.

### 3. The south remains comparable to or above the entire-area reference later in the period

In the later windows, the southern estimates stay near or above the entire-area values. Examples:
- 0.85 day: south 0.785 vs entire 0.696
- 1.00 day: south 0.805 vs entire 0.717
- 1.10 day: south 0.805 vs entire 0.733
- 1.22 day: south 0.805 vs entire 0.766
- 1.404 day: south 0.858 vs entire 0.739

Thus, the late-time reduction in `p` is not a whole-corridor-wide behavior; it is concentrated in the northern subdivision under the primary split, while the southern domain remains comparable to or higher than the corridor-wide reference.
Evidence:
- `<PACKAGE_ROOT>/results/exp_run/outputs/02_omori_fitting_and_figures/final_merged_primary_results.csv`
- `<PACKAGE_ROOT>/results/exp_run/outputs/02_omori_fitting_and_figures/main_two_panel_omori_comparison.png`

### 4. The late-time north-lower-than-south pattern is present visually, but its magnitude is sensitive to the exact north/south split line

The split-sensitivity figure compares the north/south `p` trajectories for 35.70°, 35.72°, and 35.74°N. In all three panels, the north starts relatively high at short periods and the north-south curves converge near ~0.7–0.8 day. Beyond that, the north lies below the south in the later part of the interevent sequence. This indicates that the sign of the late north-south contrast is robust.
Evidence:
- `<PACKAGE_ROOT>/results/exp_run/outputs/02_omori_fitting_and_figures/split_sensitivity_summary.png`

However, the magnitude of the northern decline depends strongly on the split latitude. Numerical sensitivity results show the final 1.404-day northern `p_fit` changes from:
- 0.699 at 35.70°,
- 0.583 at 35.72°,
- substantially lower at 35.74° in the figure.

The image analysis indicates that the southern trajectory is comparatively stable across split lines, whereas the northern trajectory shows the strongest sensitivity after ~0.8 day. This means the inference that “north becomes lower than south later” is more robust than any exact estimate of how much lower it is.
Evidence:
- `<PACKAGE_ROOT>/results/exp_run/outputs/02_omori_fitting_and_figures/split_sensitivity_results.csv`
- `<PACKAGE_ROOT>/results/exp_run/outputs/02_omori_fitting_and_figures/split_sensitivity_summary.png`

### 5. All requested primary windows were fit successfully, with no bootstrap-warning windows in this run

Run metadata reports:
- 27 successful primary windows,
- 0 failed primary windows,
- 0 bootstrap-warning windows,
- 1000 bootstrap replicates requested,
- primary split latitude 35.72°,
- final period 1.404 day,
- Mw 6.4 and Mw 7.1 origin times saved explicitly.

This confirms that the primary workflow produced a complete result set without forced gap filling.
Evidence:
- `<PACKAGE_ROOT>/results/exp_run/outputs/02_omori_fitting_and_figures/run_metadata.json`
- `<PACKAGE_ROOT>/results/exp_run/outputs/02_omori_fitting_and_figures/workflow_manifest.json`

## Limitations and Assumptions

- The present task output set does not include the requested domain-assignment diagnostic figure; that diagnostic appears to belong to Task 01 domain preparation rather than this task’s output directory. Therefore, geometric event assignment and corridor membership for the Omori fits should be cross-referenced to Task 01 outputs rather than inferred solely from Task 02.
- The pure power-law model is the primary model here by design. No three-parameter `K-c-p` Omori-Utsu comparison is provided in this task, so early-time incompleteness or short-time singular behavior is handled operationally by starting each fit at the first observed event time (`t_min_used_days > 0`), not by estimating `c`.
- The earliest northern point at 0.30 day has only 19 events and is correctly flagged as low-count/open-circle. It should not be over-interpreted. More generally, the northern bootstrap intervals are much wider than those for the entire area and often wider than those for the south, indicating weaker parameter constraint in the northern subset.
- In the primary 35.72° north-vs-south comparison table, the bootstrap-interval-overlap flag remains `True` for all periods, including the later windows where point estimates diverge. This means the late north-lower-than-south pattern is visible and systematic in the fitted trajectories, but not cleanly separated by non-overlapping 95% bootstrap intervals under this implementation.
- The split-sensitivity analysis shows that the late northern `p` decrease is sensitive to the exact latitude used to define north versus south. The sign of the late contrast is relatively stable, but the magnitude is not. This limits how strongly one should interpret the exact numerical north-south difference.
- Panel b represents the entire-area final-period fit only. It validates the whole-corridor decay shape but does not independently diagnose whether the north or south alone obeys the same rate form over the full interval.
- No failed primary fits were reported in this run, so the task does not demonstrate the requested “leave missing rather than fabricate” behavior for underconstrained windows; it only confirms that such missing-value handling was not needed here.

## Report-Ready Summary

This task completed the requested cumulative pure power-law Omori analysis for the Ridgecrest interevent period (`M >= 3.0`) within the fixed Mw 7.1 fault-zone corridor and its north/south subdivisions. The main figure, `<PACKAGE_ROOT>/results/exp_run/outputs/02_omori_fitting_and_figures/main_two_panel_omori_comparison.png`, shows that the entire corridor has a relatively stable sub-unity decay exponent (`p ≈ 0.7–0.8`) across cumulative periods, ending at `p = 0.739` with bootstrap median `0.748` and 95% interval `[0.641, 0.860]` at 1.404 day. The panel-b rate curve is consistent with a whole-corridor power-law decay over the interevent interval.

For the primary 35.72° split, the north and south are similar through the earlier cumulative periods and near-equal by 0.68–0.732 day, but from 0.85 day onward the northern `p` becomes consistently smaller than the southern `p`. By the final 1.404-day endpoint, the north has `p_fit = 0.583` while the south has `p_fit = 0.858`, and the south also remains above the entire-area reference (`0.739`). This supports the intended qualitative conclusion that the northern part tends toward smaller late-interevent `p` values, while the southern part remains comparable to or higher than the whole-corridor behavior. The main numerical evidence is preserved in `<PACKAGE_ROOT>/results/exp_run/outputs/02_omori_fitting_and_figures/final_merged_primary_results.csv` and `<PACKAGE_ROOT>/results/exp_run/outputs/02_omori_fitting_and_figures/north_vs_south_primary_comparison_35p72.csv`.

The robustness analysis, summarized in `<PACKAGE_ROOT>/results/exp_run/outputs/02_omori_fitting_and_figures/split_sensitivity_summary.png`, indicates that the late north-lower-than-south tendency persists across nearby split latitudes, but the magnitude of the northern decrease is boundary-sensitive. Therefore, the report-ready interpretation should be: there is a credible late-period tendency for the northern Mw 7.1 fault-zone subset to exhibit smaller `p` values than the southern subset, but the strength of that contrast is uncertain and should not be overstated, especially given wider northern uncertainties and split-line sensitivity.