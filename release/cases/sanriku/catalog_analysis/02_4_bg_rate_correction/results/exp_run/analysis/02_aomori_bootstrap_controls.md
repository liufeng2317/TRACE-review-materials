## Scientific Purpose

This task adds statistical controls to the Aomori background-rate analysis by testing whether the 2025-10 to 2026-05 active-period rate anomalies remain unusual when compared with many alternative long-term windows. The scientific aim is not to reinterpret the catalogs, but to stress-test the anomaly claims from the prior background-rate analysis using:
- bootstrap/random-window comparisons against the long-term common-region catalog,
- comparisons restricted to long-term windows outside the active dates,
- shifted-window checks within the active period.

The output is directly relevant to the final question of whether the 2025-2026 Aomori activity is exceptional relative to long-term background seismicity, and whether the strongest signals are localized or reflect a broader regional pulse.

## Method and Implementation Evidence

The task completed successfully according to the handoff record at `<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/log/coding_progress/task_handoff/02_aomori_bootstrap_controls.json`.

Implementation evidence from `<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/02_aomori_bootstrap_controls/diagnostics/run_diagnostics.csv` shows:
- the script used was `<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/scripts/02_aomori_bootstrap_controls.py`,
- inputs were taken from the validated outputs of Task 01 in `<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/01_aomori_background_rate_analysis`,
- the active relocated catalog used was `<CASE_ROOT>/data/catalog/Snet_catalog_relocate_250930_260501.csv`,
- only thresholds 3.0, 4.0, and 5.0 were selected for the heavy control analysis,
- `resample_n = 4000`,
- `task_count = 180`,
- `long_term_common_events = 159087`,
- `active_common_events = 22090`.

The primary machine-readable evidence files are:
- `<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/02_aomori_bootstrap_controls/tables/bootstrap_random_window_controls.csv`
- `<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/02_aomori_bootstrap_controls/tables/background_rate_evidence_matrix_with_controls.csv`

These tables include, for each region/depth/threshold/window combination:
- observed counts,
- mean expected counts from random windows and outside-active windows,
- percentile rank of the active-period window,
- exceedance fractions,
- bootstrap ratio means and confidence limits,
- shifted-window comparisons within the active period,
- a qualitative `control_support_level`.

The compact text summary at `<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/02_aomori_bootstrap_controls/summary_report.txt` confirms that the task was designed specifically to merge heavy bootstrap and random-window controls into the anomaly summary.

## Key Results and Evidence Files

### 1. The strongest active-period anomalies remain extreme after bootstrap and random-window controls

The clearest result is that the most prominent anomalies from Task 01 persist under heavy resampling controls. The summary report lists the top active-period anomalies as:
- `m1_m3_local_union | 0-30 km | M>=4`: `obs/exp(primary)=8.80`, `random_ratio_mean=94.10`, `random_percentile=99.1`, `outside_percentile=100.0`, `support=very_strong`
- `m1_m3_local_union | 0-30 km | M>=5`: `obs/exp(primary)=9.64`, `random_ratio_mean=58.97`, `random_percentile=99.1`, `outside_percentile=100.0`, `support=very_strong`
- `m1_m3_local_union | 0-30 km | M>=3`: `obs/exp(primary)=7.70`, `random_ratio_mean=32.49`, `random_percentile=98.9`, `outside_percentile=100.0`, `support=very_strong`

Evidence:
- `<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/02_aomori_bootstrap_controls/summary_report.txt`
- `<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/02_aomori_bootstrap_controls/tables/background_rate_evidence_matrix_with_controls.csv`
- `<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/02_aomori_bootstrap_controls/figures/01_bootstrap_control_ratio_heatmap.png`
- `<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/02_aomori_bootstrap_controls/figures/02_bootstrap_control_percentile_heatmap.png`

The ratio heatmap shows the dominant hotspot at `m1_m3_local_union | 0-30 km`, especially for `M>=4` (94.10), followed by `M>=5` (58.97) and `M>=3` (32.49). The percentile heatmap independently shows these same bins at about the 99th to 100th percentile. Together, these outputs support the conclusion that the local M1-M3 union region remains highly anomalous after long-term control correction.

### 2. The anomaly is not confined to one local window; it extends into the common region and selected M2-related zones, but weakens with distance

The summary report also identifies strong support for:
- `common_region | 0-30 km | M>=5`: `obs/exp(primary)=7.22`, `random_ratio_mean=30.63`, `random_percentile=98.5`, `outside_percentile=100.0`
- `common_region | 0-30 km | M>=4`: `obs/exp(primary)=5.82`, `random_ratio_mean=12.46`, `random_percentile=98.8`, `outside_percentile=100.0`
- `common_region | 0-30 km | M>=3`: `obs/exp(primary)=5.38`, `random_ratio_mean=10.07`, `random_percentile=98.8`, `outside_percentile=100.0`

Evidence:
- `<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/02_aomori_bootstrap_controls/summary_report.txt`
- `<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/02_aomori_bootstrap_controls/tables/background_rate_evidence_matrix_with_controls.csv`
- `<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/02_aomori_bootstrap_controls/figures/01_bootstrap_control_ratio_heatmap.png`

This means the active-period anomaly survives regionalization: it is not only a local artifact of the M1-M3 area, because the common-region 0-30 km bins are also strongly elevated.

At the same time, the heatmap demonstrates strong spatial decay:
- many `>=60 km` cells are near zero in ratio,
- examples include `m1_m3_local_union | >=60 km = 0.00` for all thresholds and `m2_near_field | >=60 km = 0.00` for all thresholds in the ratio heatmap.

This pattern argues for a localized-to-subregional anomaly rather than a uniformly elevated far-field regional rate.

### 3. M2 near-field and M2 outer-band anomalies are supported, but the support is selective rather than uniform

The control-resampled summary identifies several strong M2-related anomalies:
- `m2_near_field | 30-60 km | M>=4`: `obs/exp(primary)=5.37`, `random_ratio_mean=13.84`, `random_percentile=98.2`, `outside_percentile=100.0`, `support=very_strong`
- `m2_near_field | 30-60 km | M>=5`: `obs/exp(primary)=7.31`, `random_ratio_mean=12.26`, `random_percentile=100.0`, `outside_percentile=100.0`, `support=very_strong`
- `m2_near_field | 0-30 km | M>=3`: `obs/exp(primary)=4.63`, `random_ratio_mean=11.63`, `random_percentile=96.2`, `outside_percentile=100.0`, `support=strong`
- `m2_outer_band | 0-30 km | M>=4`: `obs/exp(primary)=5.05`, `random_ratio_mean=13.64`, `random_percentile=98.9`, `outside_percentile=100.0`, `support=very_strong`
- `m2_outer_band | 0-30 km | M>=3`: `obs/exp(primary)=5.53`, `random_ratio_mean=10.46`, `random_percentile=98.9`, `outside_percentile=100.0`, `support=very_strong`

Evidence:
- `<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/02_aomori_bootstrap_controls/summary_report.txt`
- `<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/02_aomori_bootstrap_controls/tables/background_rate_evidence_matrix_with_controls.csv`
- `<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/02_aomori_bootstrap_controls/figures/01_bootstrap_control_ratio_heatmap.png`
- `<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/02_aomori_bootstrap_controls/figures/02_bootstrap_control_percentile_heatmap.png`

However, support is not spatially uniform:
- `m2_near_field | 0-30 km | M>=5` is 0.00 in the ratio heatmap,
- `m2_outer_band | >=60 km` is near zero or zero in the ratio heatmap,
- percentile values in the farthest bins can be low or highly variable.

Thus, M2 outer-band activity cannot be summarized as a broad, everywhere-elevated anomaly. Instead, the controls support elevated rates mainly in selected near and intermediate distance bins, especially for `M>=3` to `M>=5` in the 0-30 km and 30-60 km bands.

### 4. The choice of control window does not materially change the main conclusions

The scatter plot directly compares bootstrap ratios computed against:
- all long-term random windows, and
- long-term windows outside the active dates.

Most points lie close to the 1:1 line, including the dense cluster of lower-valued combinations and the major outliers. The strongest anomalies remain strong under both control definitions.

Evidence:
- `<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/02_aomori_bootstrap_controls/figures/03_random_vs_outside_control_scatter.png`

The plot shows:
- a dense core near the origin close to the 1:1 reference line,
- the largest outliers still aligned near the line,
- slight tendency for points to lie above the line, implying the outside-active-date control often yields slightly stronger anomalies.

This indicates that the anomaly claims are robust to control choice. Excluding active dates from the long-term controls may sharpen the contrast somewhat, but it does not create the main anomaly pattern.

### 5. Percentile support is generally high for the main target bins, but percentile saturation and far-field instability require caution

The percentile heatmap shows many target bins in the 98th-100th percentile range, including:
- `common_region | 0-30 km` across `M>=3`, `M>=4`, `M>=5`,
- `m1_m3_local_union | 0-30 km` across all three thresholds,
- `m2_near_field | 30-60 km | M>=5 = 100`,
- `m2_outer_band | 30-60 km | M>=5 = 100`.

Evidence:
- `<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/02_aomori_bootstrap_controls/figures/02_bootstrap_control_percentile_heatmap.png`
- `<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/02_aomori_bootstrap_controls/tables/background_rate_evidence_matrix_with_controls.csv`

But some `>=60 km` bins show boundary values of 0 or 100, for example:
- `common_region | >=60 km | M>=3 = 0`,
- `common_region | >=60 km | M>=4 = 0`,
- `control_region | >=60 km | M>=5 = 100`,
- `m2_outer_band | >=60 km | M>=3 = 0`.

These edge values likely reflect sparse counts and ranking saturation rather than stable effect-size separation. Therefore, percentile ranks in low-count far-field bins should be treated as secondary evidence.

### 6. Control support is intentionally restricted to thresholds with stronger catalog comparability

The merged evidence matrix includes threshold 1.2 and 2.0 rows, but these rows are labeled `insufficient_control_data` and contain `NaN` in the control fields. For example, in the evidence matrix:
- `common_region | 0-30 km | 1.2` and `2.0` have observed and expected counts from the primary analysis, but no bootstrap control statistics.

Evidence:
- `<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/02_aomori_bootstrap_controls/tables/background_rate_evidence_matrix_with_controls.csv`
- `<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/02_aomori_bootstrap_controls/diagnostics/run_diagnostics.csv`

This is scientifically consistent with the broader catalog-comparison rule: the heavy cross-catalog background controls were restricted to `M>=3`, `M>=4`, and `M>=5`, which are the more defensible long-term comparison thresholds.

## Limitations and Assumptions

- This task is a control/resampling extension of prior validated outputs, not a fresh catalog audit. Its interpretation depends on the common-region definitions and region masks inherited from Task 01, whose outputs are referenced at `<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/01_aomori_background_rate_analysis`.
- Heavy controls were applied only to thresholds `M>=3`, `M>=4`, and `M>=5`, as shown in `<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/02_aomori_bootstrap_controls/diagnostics/run_diagnostics.csv`. Low-magnitude thresholds (`1.2`, `2.0`) remain unavailable for this long-term control test and are explicitly marked `insufficient_control_data` in `<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/02_aomori_bootstrap_controls/tables/background_rate_evidence_matrix_with_controls.csv`.
- Some figure labels suggest minor terminology inconsistency: the ratio heatmap title refers to bootstrap controls while the colorbar is labeled `random_ratio_mean`. This does not appear to change the underlying table values but should be standardized before publication.
- Several far-field or sparse bins produce exact 0 or 100 percentiles. These likely reflect limited counts and boundary saturation rather than precise effect magnitude; they should not be overinterpreted.
- Extremely large ratio values, such as 94.10 for `m1_m3_local_union | 0-30 km | M>=4`, are compelling but should be paired with the underlying count context from the tables rather than treated as standalone physical measures.
- This task supports statistical anomaly detection only. It does not provide evidence for triggering, slow slip, fluid migration, stress transfer, or fault interaction, and should not be used as mechanism proof.

## Report-Ready Summary

Bootstrap and random-window controls strongly support the conclusion that the 2025-10 to 2026-05 Aomori active period was exceptional relative to the 2020-2026 long-term background within the common analysis region, at least for the robust long-term comparison thresholds `M>=3`, `M>=4`, and `M>=5`. The most compelling anomaly is the `m1_m3_local_union` in the `0-30 km` depth bin, where all three thresholds show very high active/background contrasts and approximately 99th-100th percentile rankings relative to long-term control windows. Key evidence is preserved in `<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/02_aomori_bootstrap_controls/tables/background_rate_evidence_matrix_with_controls.csv`, `<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/02_aomori_bootstrap_controls/summary_report.txt`, and the ratio/percentile heatmaps.

The anomaly is not limited to a single micro-region. The `common_region | 0-30 km` bins are also strongly elevated across `M>=3` to `M>=5`, and selected M2-related regions show substantial excess as well, especially `m2_near_field | 30-60 km` and `m2_outer_band | 0-30 km`. However, the anomaly weakens sharply in many `>=60 km` bins, which argues against a spatially uniform far-field rate increase. The most defensible interpretation is therefore a localized-to-subregional rate pulse rather than a region-wide homogeneous elevation.

The M1-M3 local region remains anomalous after regional background correction and after long-term control resampling; this is the strongest and most stable result of the task. M2 outer-band activity also shows statistically elevated bins, especially at `0-30 km` for `M>=3` and `M>=4`, but the support is more selective than for the M1-M3 local union and should be described as partially explained by a broader regional pulse plus localized enhancement rather than as a uniformly independent anomaly.

The anomaly conclusions are robust to control-window choice. The scatter comparison in `<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/02_aomori_bootstrap_controls/figures/03_random_vs_outside_control_scatter.png` shows that results using all long-term random windows and windows outside the active dates are closely aligned. This makes the strongest anomaly claims suitable for later physical follow-up, while low-count far-field bins and low-magnitude thresholds should remain secondary or provisional.