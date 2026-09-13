## Scientific Purpose

This task quantifies the robustness of event-centered seismic-sequence patterns around the three matched major earthquakes in the Aomori regional catalog, labeled M1, M2, and M3. The goal is to determine which apparent pre-/post-event features persist when the analysis is redefined by radius, time window, depth treatment, and magnitude threshold, and to separate stable sequence signatures from parameter-dependent artifacts.

## Method and Implementation Evidence

The implementation evaluated a full parameter grid around the three matched mainshocks using:

- radii of 30, 44, 50, 80, and 100 km
- time windows of 7, 30, 60, and 90 days
- depth strategies: all depths, mainshock-centered depth windows, and stratified depth windows
- magnitude thresholds: all events, M ≥ 1.2, 1.5, 2.0, and 2.5

The run verified that the source tables contained the fields required for sequence analysis and that the three mainshocks were matched to the relocated catalog. The verification file confirms that all required fields were present in the catalog, mainshock table, mechanism table, and station table, and that the three mainshocks were matched with high confidence.

Evidence:
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/04_robustness_analysis/robustness_verification.json`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/04_robustness_analysis/parameter_grid_summary.csv`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/04_robustness_analysis/robustness_results.csv`

The parameter grid produced 900 summary combinations, and the verification JSON reports 1,606,311 sequence rows overall, indicating that the robustness assessment spans the full event-centered extraction space. The mainshock-specific baseline summaries are stored in:
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/04_robustness_analysis/three_sequence_comparison_baseline.csv`

The analysis also included a simple control comparison using background windows away from the mainshock times:
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/04_robustness_analysis/control_comparison_baseline.csv`

## Key Results and Evidence Files

### 1) The three sequences are all strongly post-event enriched, but with different strengths

Baseline sequence statistics from `three_sequence_comparison_baseline.csv` show:

- **M1**: 3,875 total events; 551 pre-event and 3,323 post-event events; pre-rate 6.12/day, post-rate 36.92/day; rate ratio 6.03
- **M2**: 2,362 total events; 81 pre-event and 2,280 post-event events; pre-rate 0.90/day, post-rate 25.33/day; rate ratio 28.15
- **M3**: 3,662 total events; 880 pre-event and 2,781 post-event events; pre-rate 9.78/day, post-rate 30.90/day; rate ratio 3.16

Interpretation:
- M2 shows the strongest post-event enrichment relative to its low pre-event rate.
- M1 also shows a large post-event amplification.
- M3 has substantial absolute activity, but the pre/post contrast is weaker than M1 and much weaker than M2.

Evidence:
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/04_robustness_analysis/three_sequence_comparison_baseline.csv`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/04_robustness_analysis/stability_flags.csv`

### 2) Robust features are the rate ratio and peak moving-window rate

Across all parameter combinations, the most stable metrics are:

- **rate_ratio**: sign consistency fraction = 1.0 for M1, M2, and M3
- **moving_rate_max**: sign consistency fraction = 1.0 for M1, M2, and M3

This means the direction of the post-event increase and the presence of a pronounced short-term rate peak are robust across the tested parameter space.

The stability feature summary reports:
- **M1**: rate_ratio and moving_rate_max robust_fraction = 1.0
- **M2**: rate_ratio and moving_rate_max robust_fraction = 1.0
- **M3**: rate_ratio and moving_rate_max robust_fraction = 1.0

Evidence:
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/04_robustness_analysis/stability_feature_flags.csv`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/04_robustness_analysis/stability_flags.csv`

### 3) Omori-style post-event decay is robust for M1 and M2, but not for M3

The baseline sequence comparison reports post-event Omori-like fits for:
- **M1**: p = 0.638, R² = 0.913
- **M2**: p = 0.643, R² = 0.957
- **M3**: no finite baseline Omori estimate reported

The robustness summaries show:
- **M1** post-Omori p is stable in 75.0% of windows
- **M2** post-Omori p is stable in 72.33% of windows overall, and 96.44% in the feature-level stability summary
- **M3** has 0.0% stable post-Omori fraction and no usable baseline post-Omori estimate

Interpretation:
- M1 and M2 support a persistent aftershock-decay-like pattern.
- M3 does not yield a robust Omori-style decay across the tested definitions, suggesting stronger parameter sensitivity or a sequence shape not well captured by simple decay fitting.

Evidence:
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/04_robustness_analysis/stability_feature_flags.csv`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/04_robustness_analysis/sensitivity_summary.csv`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/04_robustness_analysis/stability_flags.csv`

### 4) M2 is the most depth-distinct sequence

The baseline depth median differs strongly by mainshock:
- **M1**: depth_q50 = 11.51 km
- **M2**: depth_q50 = 41.555 km
- **M3**: depth_q50 = 12.83 km

This confirms the earlier guidance that M2 is depth-distinct. It also means depth stratification is especially important for M2 when comparing sequence behavior across parameter choices.

Evidence:
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/04_robustness_analysis/three_sequence_comparison_baseline.csv`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/04_robustness_analysis/robustness_results.csv`

### 5) M3 is the most parameter-sensitive in Omori behavior, but not in rate-ratio direction

The sensitivity summary indicates:
- M3 retains stable rate-ratio sign across all parameter definitions
- but its post-Omori stability fraction is 0.0 in the parameter summary

So M3 consistently shows post-event enrichment, but the specific decay-form diagnostic is not robust.

Evidence:
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/04_robustness_analysis/sensitivity_summary.csv`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/04_robustness_analysis/stability_flags.csv`

### 6) The simple control comparison is weak but supports event-centric enrichment

The control baseline file reports:
- M1: control rate 0.00/day, relative control rate 0.0
- M2: control rate 0.00/day, relative control rate 0.0
- M3: control rate 0.75/day, relative control rate 0.0767

This indicates that the event-centered windows are much more active than the background control windows, especially for M1 and M2.

Caution: the control file indicates NaN control window bounds for all three rows, so the exact control-window definition should be checked before making stronger inference.

Evidence:
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/04_robustness_analysis/control_comparison_baseline.csv`

### 7) Radii, time windows, and depth strategies do not change the qualitative conclusions

The robustness summaries indicate:
- the sign of the rate-ratio response is stable for all three mainshocks across the full parameter grid
- moving-window rate maxima are also stable in sign for all three mainshocks
- the exact Omori-fit stability is the main point of divergence, with M3 least robust

This supports the interpretation that the main sequence conclusions are not driven by a single arbitrary choice of radius or threshold, although the quantitative decay fit is more sensitive.

Evidence:
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/04_robustness_analysis/parameter_grid_summary.csv`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/04_robustness_analysis/robustness_results.csv`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/04_robustness_analysis/sensitivity_summary.csv`

## Limitations and Assumptions

- No image or PDF files were present in this output directory, so there were no figure products to inspect for this specific task.
- The control comparison output contains NaN window bounds, so the exact control-window geometry is not fully documented in the output table.
- `mecha_overlap_count` and `stations_within_100km` are zero or NaN in the baseline comparison, indicating that focal-mechanism and station-context summaries were not informative in this task output and may reflect data coverage limitations rather than true absence.
- Some Omori fits are missing or unstable, especially for M3, so decay interpretation should remain qualitative unless a more tailored fitting strategy is applied.
- The `sparse_flag` is false for the displayed baseline and summary rows, but very small or highly thresholded subsets may still become sparse in specific combinations.
- The summary tables do not by themselves show the exact maps or time-series shapes; those must be checked in the earlier sequence-extraction and diagnostics tasks for spatial and temporal visual context.

## Report-Ready Summary

The robustness analysis shows that the core event-centered sequence signal is stable: all three matched Aomori mainshocks exhibit a robust post-event increase in seismicity rate and a robust peak in short-term moving-window rate across radii, time windows, depth strategies, and magnitude thresholds. M2 stands out as the strongest relative activation and the clearest depth-distinct sequence, while M1 also shows strong and reproducible post-event enrichment. M3 remains robust in the sign of its response but is less stable in Omori-style decay behavior, indicating greater sensitivity of decay metrics to definition choices. The most important reusable evidence files are `robustness_results.csv`, `sensitivity_summary.csv`, `stability_flags.csv`, `stability_feature_flags.csv`, `three_sequence_comparison_baseline.csv`, `parameter_grid_summary.csv`, and `control_comparison_baseline.csv` at `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/04_robustness_analysis/`.