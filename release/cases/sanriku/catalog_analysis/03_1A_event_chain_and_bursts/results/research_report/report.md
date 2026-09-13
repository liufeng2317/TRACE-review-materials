---
author:
- TRACE
title: Catalog-Level Screening Report for the M1–M3 Event Chain and Burst Structure in the Relocated/Filtered Aomori Active-Year Catalog
---

# Abstract

This report screens the M1–M3 local seismic system in the relocated/filtered Aomori active-year catalog using the requested fixed windows, local-union geometry, endpoint-core classifications, corridor metrics, and raw versus M2-aware comparisons. The evidence supports a non-causal interpretation in which low-rate local activity existed before M1, the M1-related phase dominated the full M1-to-M3 interval, the later interval was not empty after that dominant phase was separated, and the final five weeks before M3 contained renewed local activity. The sequence is better described as separated bursts and endpoint-centered behavior than as one homogeneous continuous activation chain or a robust corridor-migration pattern. M2-aware filtering changes some middle-interval counts but does not remove the main classification. The conclusions are limited to catalog-level description and do not imply triggering or physical causality.

# Scientific objective

The objective of this task was to screen the M1–M3 local system in the relocated/filtered Aomori active-year catalog and determine whether the observed pattern is best described as pre-existing activity before M1, sustained activation between M1 and M3, separated bursts, endpoint-centered activity, pre-M3 local activation, corridor-like activity, or broader local/background activity. The requested design explicitly required separating the M1-related swarm/aftershock-dominated phase from later M1–M3 activity and avoiding causal interpretations based on temporal order or proximity alone.

The primary spatial domain was the M1–M3 local union, defined as events within 60 km of either M1 or M3. Supporting spatial partitions included endpoint core zones within 30 km of M1 or M3, endpoint extended zones within 60 km, and an M1–M3 corridor defined by projected position along the M1–M3 axis plus perpendicular distance thresholds. Events within 100 km of M2 were flagged as M2-related or ambiguous for raw-versus-M2-aware comparison rather than removed by default.

The primary temporal windows were the conservative pre-M1 background baseline ending at M1$`-`$<!-- -->14 d, a sensitivity baseline ending at M1$`-`$<!-- -->7 d, the M1-related dominated phase from M1$`-`$<!-- -->14 d to M1$`+`$<!-- -->21 d, the middle phase from M1$`+`$<!-- -->21 d to M3$`-`$<!-- -->35 d, and the pre-M3 local activation phase from M3$`-`$<!-- -->35 d to M3. Short post-M3 windows were retained only as context and were not mixed into pre-M3 interpretation.

# Implemented analysis and evidence base

According to the task evidence package, the workflow was completed in three stages: (1) construction of a unified M1–M3 event-chain table and derived count/rate summaries, (2) generation of a compact diagnostic figure suite, and (3) synthesis into a final screening classification. The underlying analysis computed event-wise descriptors including time since M1, time before M3, distance to M1, distance to M3, projected distance along the M1–M3 axis, perpendicular distance to the axis, depth, magnitude, spatial category, and M2-related flag.

The task summaries state that the M1–M3 epicentral separation is 57.38 km, with M2 substantially farther away from both endpoints. The present report relies on the concrete outputs listed in the evidence index, especially the CSV summaries in <a href="<CASE_ROOT>/run/03_1A_event_chain_and_bursts/exp_run/outputs/01_m1_m3_event_chain_analysis" class="uri"><CASE_ROOT>/run/03_1A_event_chain_and_bursts/exp_run/outputs/01_m1_m3_event_chain_analysis</a> and the figures in <a href="<CASE_ROOT>/run/03_1A_event_chain_and_bursts/exp_run/outputs/02_m1_m3_diagnostic_figures" class="uri"><CASE_ROOT>/run/03_1A_event_chain_and_bursts/exp_run/outputs/02_m1_m3_diagnostic_figures</a>.

Key tabular evidence used here includes:

- `m1_m3_window_summary_counts_rates.csv`: windowed counts, durations, and rates for M3+, M4+, M5+, and M6+.

- `m1_m3_window_summary_composition.csv`: spatial composition by M1-core, M3-core, corridor non-core, and off-corridor local fractions.

- `m1_m3_phase_contribution_summary.csv`: contribution of each phase to the full M1-to-M3 interval.

- `m1_m3_migration_endpoint_switching_summary.csv`: along-axis trend metrics and endpoint-weighting diagnostics.

- `m1_m3_classification_summary.csv` and `m1_m3_screening_report.md`: final classification statements and concise evidence notes.

# Results

## Reference timing and screening windows

The final screening report gives the reference times M1 = 2025-11-09T08:03:39.240000+00:00 and M3 = 2026-04-20T07:52:58.060000+00:00. The conservative pre-M1 baseline ends at 2025-10-26 08:03:39.240000+00:00, corresponding to 146.07 days of available local-union history in the current catalog. The main windows used in interpretation are those requested by the task design and implemented in the tabulated outputs.

## Pre-M1 background and immediate lead-in

The local system was not empty before M1. In the conservative baseline ending at M1$`-`$<!-- -->14 d, the raw catalog contains 20 M3+ events over 146.07 days, a rate of 0.137 day$`^{-1}`$, while M4+, M5+, and M6+ counts are all zero (Table <a href="#tab:counts" data-reference-type="ref" data-reference="tab:counts">1</a>). Using the sensitivity baseline ending at M1$`-`$<!-- -->7 d gives 21 M3+ events over 152.92 days, with the same rounded rate and still no M4+ events. This supports pre-existing local activity, but at a modest level and without larger events.

Spatially, the conservative pre-M1 baseline is much more diffuse than the later sequence. The raw composition is 25.0% M1-core, 20.4% M3-core, 9.2% corridor non-core, and 44.9% off-corridor local activity (Table <a href="#tab:composition" data-reference-type="ref" data-reference="tab:composition">2</a>). Thus, before the immediate M1-related lead-in, the local union contains activity but not a strongly organized endpoint-core or corridor-dominated pattern.

## M1-related dominated phase

The M1-related primary window from M1$`-`$<!-- -->14 d to M1$`+`$<!-- -->21 d is the dominant component of the full interval. In the raw catalog it contains 335 M3+, 83 M4+, 30 M5+, and 4 M6+ events over 34.11 days, corresponding to an M3+ rate of 9.82 day$`^{-1}`$ (Table <a href="#tab:counts" data-reference-type="ref" data-reference="tab:counts">1</a>). Relative to the conservative baseline, this is a rate increase of about 23.94$`\times`$, matching the final classification summary. The same window contributes 83.5% of raw full-interval M3+, 84.7% of raw M4+, and 96.8% of raw M5+ events (Table <a href="#tab:phase" data-reference-type="ref" data-reference="tab:phase">3</a>). In the M2-aware version, the counts remain identical for this phase, and the fractional dominance becomes slightly larger because later intervals lose some flagged events.

Spatial organization during this phase is overwhelmingly M1-centered. The raw composition is 76.5% M1-core, 15.3% M3-core, 3.6% corridor non-core, and 4.3% off-corridor local (Table <a href="#tab:composition" data-reference-type="ref" data-reference="tab:composition">2</a>). The endpoint-core total is therefore about 91.8%, consistent with the classification summary that the M1-related phase is endpoint-centered and strongly M1-core weighted. Figures <a href="#fig:timeline" data-reference-type="ref" data-reference="fig:timeline">1</a>–<a href="#fig:map" data-reference-type="ref" data-reference="fig:map">3</a> provide the corresponding visual evidence: a major burst cluster around M1, high cumulative count growth early in the interval, and map-view concentration near the M1 endpoint.

## Middle phase after separating the M1-related window

The middle phase from M1$`+`$<!-- -->21 d to M3$`-`$<!-- -->35 d remains active after the dominant M1-related window is removed. In the raw summary it contains 79 M3+, 20 M4+, 5 M5+, and 2 M6+ events over 105.71 days, giving an M3+ rate of 0.747 day$`^{-1}`$ (Table <a href="#tab:counts" data-reference-type="ref" data-reference="tab:counts">1</a>). Compared with the conservative pre-M1 baseline rate of 0.137 day$`^{-1}`$, this is about 5.46$`\times`$ higher in absolute rate ratio from the table values, while the task-level synthesis describes the local all-event rate as elevated by roughly 3.3–3.5$`\times`$; the difference reflects which metric is being compared. For M3+ counts specifically, the phase contributes 19.7% of raw full-interval events and 17.5% in the M2-aware case (Table <a href="#tab:phase" data-reference-type="ref" data-reference="tab:phase">3</a>).

This means the interval after M1$`+`$<!-- -->21 d is not empty, but it is also clearly much weaker than the M1-related phase. The spatial composition shifts somewhat toward a mixed structure: 60.2% M1-core, 16.2% M3-core, 10.3% corridor non-core, and 12.3% off-corridor local in the raw version (Table <a href="#tab:composition" data-reference-type="ref" data-reference="tab:composition">2</a>). Corridor participation is more visible here than during the M1-related phase, but it remains a minority component and does not dominate the geometry. The screening classification therefore labels this interval as *sustained* rather than quiet, but still not a homogeneous continuous activation chain.

## Pre-M3 local activation

The final five weeks before M3 show renewed local activity. In the primary pre-M3 window from M3$`-`$<!-- -->35 d to M3, the raw catalog contains 52 M3+, 15 M4+, 3 M5+, and 2 M6+ events over 34.82 days, an M3+ rate of 1.49 day$`^{-1}`$ (Table <a href="#tab:counts" data-reference-type="ref" data-reference="tab:counts">1</a>). The screening summary reports a rate increase of about 6.36$`\times`$ relative to the conservative pre-M1 baseline. In the M2-aware comparison the counts become 51 M3+ and 14 M4+, showing only minor reduction.

The pre-M3 phase is therefore a real late-stage component in the local catalog, not just a visual artifact of combining the whole interval into one sequence. However, it is not spatially dominated by a corridor pattern. The raw composition is 67.4% M1-core, 18.0% M3-core, 4.1% corridor non-core, and 9.5% off-corridor local, while the M2-aware composition is similar (Table <a href="#tab:composition" data-reference-type="ref" data-reference="tab:composition">2</a>). The evidence thus supports clear pre-M3 local activation, but still within an endpoint-centered, mixed-endpoint geometry rather than a clean M3-centered corridor migration. This interpretation is also consistent with Figure <a href="#fig:preM3" data-reference-type="ref" data-reference="fig:preM3">5</a>.

## Large-event evolution from M1 to M3

Across the full M1-to-M3 interval, the raw catalog contains 401 M3+, 98 M4+, 31 M5+, and 8 M6+ events, while the M2-aware version contains 389 M3+, 95 M4+, 31 M5+, and 8 M6+ (Table <a href="#tab:counts" data-reference-type="ref" data-reference="tab:counts">1</a>). The dominance of the M1-related phase increases with magnitude threshold: 83.5% of full-interval M3+, 84.7% of M4+, and 96.8% of M5+ occur in that phase. For M6+, the distribution is broader, with 4 events in the M1-related phase, 2 in the middle phase, and 2 in the pre-M3 phase (Table <a href="#tab:phase" data-reference-type="ref" data-reference="tab:phase">3</a>).

This magnitude-dependent distribution supports a two-part interpretation. First, the strongest concentration of larger events belongs to the M1-related dominated phase. Second, later windows are weaker but not negligible, especially for M3+ and M4+, and therefore should not be merged uncritically into a single homogeneous sequence.

## Burst structure, continuity, and migration-style diagnostics

The final classification summary states that the burst table identifies 9 M3+ bursts and that the maximum M3+ inter-event gap over the full M1-to-M3 interval is 11.03 days; for M4+ the maximum gap is 26.16 days. These values support a burst-separated interpretation rather than a uniform continuous chain. The classification correspondingly marks *continuous activation chain* as *not supported* and *separated bursts* as *yes* in both raw and M2-aware screening.

The migration-style metrics also argue against describing the full sequence as a robust along-axis migration. Time–along-axis correlations are 0.192 for the full raw interval, 0.111 for the M1-related phase, 0.032 for the middle phase, and 0.302 for the pre-M3 phase; corresponding M2-aware values are 0.177, 0.111, 0.036, and 0.294 (Table <a href="#tab:migration" data-reference-type="ref" data-reference="tab:migration">4</a>). These are modest correlations, and the phase-separated values do not sustain a strong monotonic migration narrative. In parallel, the nearest-endpoint fractions remain M1-heavy in every pre-M3 phase, and M1-core fractions remain much larger than M3-core fractions even late in the sequence. The screening result is therefore that apparent full-interval migration is *not robust*; the better summary is mixed endpoint sequences or endpoint switching/overlap rather than confirmed migration.

## M2-aware comparison

The raw-versus-M2-aware comparison shows that M2 affects part of the catalog but does not control the main classification. For the full M1-to-M3 interval, M3+ counts change from 401 to 389, a reduction of about 3.0%. The effect is stronger in the middle phase, where M3+ counts change from 79 to 68, corresponding to 13.9% removal, but the pre-M3 phase changes only from 52 to 51 M3+ events, or 1.9% removal. The key qualitative outcomes remain unchanged in the final classification summary: pre-existing activity is present, the M1-related phase is strong, the middle phase is still sustained, separated bursts are supported, endpoint-centered activity dominates, corridor-like activity is not dominant, and pre-M3 local activation remains clear.

# Synthesis: screening classification

Taken together, the tabular summaries and the diagnostic figures support the following catalog-level, non-causal screening interpretation.

1.  **Pre-existing local activity before M1 was present but modest.** The conservative baseline contains 20 M3+ events over 146.1 days, with no M4+ or larger events. The pre-M1 local pattern is diffuse and background-like relative to later phases.

2.  **The full M1-to-M3 interval is dominated by a strong M1-related swarm/aftershock-like phase.** More than four-fifths of M3+ and M4+, and nearly all M5+, occur in the M1-related window.

3.  **After separating the M1-related phase, the middle phase remains active rather than empty.** It is weaker than the M1-related phase but still elevated relative to the conservative baseline and therefore should be described as sustained, not silent.

4.  **The overall pattern is better described as separated bursts than as one homogeneous activation chain.** Gap metrics and the burst table support temporal segmentation.

5.  **Spatial organization is endpoint-centered rather than corridor-dominated.** M1-core and M3-core fractions strongly exceed corridor non-core fractions in the main pre-M3 windows.

6.  **The final five weeks before M3 show clear local activation.** This survives M2-aware comparison and therefore is not removed by the ambiguity screening.

7.  **Apparent migration is not robust after phase separation.** The pattern is better summarized as mixed endpoint-centered behavior with possible switching or overlap.

# Figures

<figure id="fig:timeline" data-latex-placement="H">
<img src="<CASE_ROOT>/run/03_1A_event_chain_and_bursts/exp_run/outputs/02_m1_m3_diagnostic_figures/fig_burst_timeline_summary.png" style="width:92.0%" />
<figcaption>Burst-timeline summary for the M1–M3 local system. This figure is part of the diagnostic suite used to separate the M1-related dominated phase, the middle interval, and the pre-M3 activation phase.</figcaption>
</figure>

<figure id="fig:cumulative" data-latex-placement="H">
<img src="<CASE_ROOT>/run/03_1A_event_chain_and_bursts/exp_run/outputs/02_m1_m3_diagnostic_figures/fig_cumulative_counts_raw_vs_M2aware.png" style="width:92.0%" />
<figcaption>Cumulative large-event counts comparing raw and M2-aware catalogs. The dominant early contribution of the M1-related phase is visually apparent, while raw-to-M2-aware differences are modest relative to the main pattern.</figcaption>
</figure>

<figure id="fig:map" data-latex-placement="H">
<img src="<CASE_ROOT>/run/03_1A_event_chain_and_bursts/exp_run/outputs/02_m1_m3_diagnostic_figures/fig_m1_m3_map_time_category.png" style="width:92.0%" />
<figcaption>Map-view spatial categorization of local events by time/category. This figure supports the endpoint-centered interpretation and the subordinate role of corridor non-core activity.</figcaption>
</figure>

<figure id="fig:projected" data-latex-placement="H">
<img src="<CASE_ROOT>/run/03_1A_event_chain_and_bursts/exp_run/outputs/02_m1_m3_diagnostic_figures/fig_projected_distance_time.png" style="width:92.0%" />
<figcaption>Projected along-axis distance versus time. The figure is useful for assessing whether any apparent migration remains after window separation. The corresponding tabulated correlations are modest and do not support a robust continuous migration classification.</figcaption>
</figure>

<figure id="fig:preM3" data-latex-placement="H">
<img src="<CASE_ROOT>/run/03_1A_event_chain_and_bursts/exp_run/outputs/02_m1_m3_diagnostic_figures/fig_preM3_activation_raw_vs_M2aware.png" style="width:92.0%" />
<figcaption>Pre-M3 activation in raw and M2-aware views. This figure supports the conclusion that late local activation before M3 remains present after M2-aware comparison.</figcaption>
</figure>

# Key quantitative tables

<div id="tab:counts">

| Window                                 | Version | M3+ | M4+ | M5+ | M6+ |
|:---------------------------------------|:--------|----:|----:|----:|----:|
| Pre-M1 baseline to M1$`-`$<!-- -->14 d | raw     |  20 |   0 |   0 |   0 |
| Pre-M1 baseline to M1$`-`$<!-- -->14 d | m2aware |  20 |   0 |   0 |   0 |
| Pre-M1 baseline to M1$`-`$<!-- -->7 d  | raw     |  21 |   0 |   0 |   0 |
| Pre-M1 baseline to M1$`-`$<!-- -->7 d  | m2aware |  21 |   0 |   0 |   0 |
| M1-related primary                     | raw     | 335 |  83 |  30 |   4 |
| M1-related primary                     | m2aware | 335 |  83 |  30 |   4 |
| Middle primary                         | raw     |  79 |  20 |   5 |   2 |
| Middle primary                         | m2aware |  68 |  18 |   5 |   2 |
| Pre-M3 primary                         | raw     |  52 |  15 |   3 |   2 |
| Pre-M3 primary                         | m2aware |  51 |  14 |   3 |   2 |
| Full M1 to M3                          | raw     | 401 |  98 |  31 |   8 |
| Full M1 to M3                          | m2aware | 389 |  95 |  31 |   8 |

Windowed counts and rates for the main screening windows. Values are taken directly from `m1_m3_window_summary_counts_rates.csv`.

</div>

<div id="tab:composition">

| Window | Version | M1-core | M3-core | Corridor non-core | Off-corridor local |
|:---|:---|:---|:---|:---|:---|
| Pre-M1 baseline 14 d | raw |  |  |  |  |
| Pre-M1 baseline 14 d | m2aware |  |  |  |  |
| M1-related primary | raw |  |  |  |  |
| M1-related primary | m2aware |  |  |  |  |
| Middle primary | raw |  |  |  |  |
| Middle primary | m2aware |  |  |  |  |
| Pre-M3 primary | raw |  |  |  |  |
| Pre-M3 primary | m2aware |  |  |  |  |
| Full M1 to M3 | raw |  |  |  |  |
| Full M1 to M3 | m2aware |  |  |  |  |

Spatial composition for the main windows from `m1_m3_window_summary_composition.csv`. Fractions sum approximately to one across the listed categories.

</div>

<div id="tab:phase">

| Version | Threshold | M1-related frac. | Middle frac. | Pre-M3 frac. | Middle+Pre-M3 frac. |
|:---|:---|:---|:---|:---|:---|
| raw | M3+ |  |  |  |  |
| raw | M4+ |  |  |  |  |
| raw | M5+ |  |  |  |  |
| m2aware | M3+ |  |  |  |  |
| m2aware | M4+ |  |  |  |  |
| m2aware | M5+ |  |  |  |  |

Phase contributions to the full M1-to-M3 interval from `m1_m3_phase_contribution_summary.csv`.

</div>

<div id="tab:migration">

| Version | Phase | Corr.(time, along-axis) | Frac. nearest M1 | Frac. nearest M3 | Median perp. dist. (km) |
|:---|:---|:---|:---|:---|:---|
| raw | Full M1–M3 |  |  |  |  |
| raw | M1-related |  |  |  |  |
| raw | Middle |  |  |  |  |
| raw | Pre-M3 |  |  |  |  |
| m2aware | Full M1–M3 |  |  |  |  |
| m2aware | M1-related |  |  |  |  |
| m2aware | Middle |  |  |  |  |
| m2aware | Pre-M3 |  |  |  |  |

Migration-style and endpoint-switching metrics from `m1_m3_migration_endpoint_switching_summary.csv`.

</div>

# Follow-up priorities

The follow-up table produced by the workflow assigns high priority to spatial-depth screening and b-value/completeness analysis, with medium priority for burst-wise migration screening and mechanism screening. These priorities are appropriate for the current evidence chain: the present task established that the system contains multiple temporally distinct phases and endpoint-heavy spatial organization, but it did not yet test whether those phases separate further by depth distribution, completeness behavior, or focal mechanism. The follow-up target file is <a href="<CASE_ROOT>/run/03_1A_event_chain_and_bursts/exp_run/outputs/01_m1_m3_event_chain_analysis/m1_m3_followup_targets.csv" class="uri"><CASE_ROOT>/run/03_1A_event_chain_and_bursts/exp_run/outputs/01_m1_m3_event_chain_analysis/m1_m3_followup_targets.csv</a>.

# Limitations

This report inherits the cross-task limitations stated in the evidence package.

- The screening is strictly catalog-level and descriptive. Temporal order and spatial proximity were not used to infer triggering or physical causality.

- The main interpretation depends on fixed windows centered on M1$`-`$<!-- -->14 d, M1$`+`$<!-- -->21 d, and M3$`-`$<!-- -->35 d. Limited sensitivity checks were reported, but alternative boundary choices could shift exact counts and rate contrasts.

- The pre-M1 baseline uses the available catalog start and therefore represents only the active-year history available in this dataset, not a longer-term regional background state.

- The pre-M3 activation is supported in both raw and M2-aware summaries, but the degree to which it is fully independent of M2-related ambiguity is less certain than the dominance of the M1-related phase.

- Figure-based auditability is slightly reduced because some labels were reported as partially obscured at image resolution, and the task-03 classification summary and evidence CSVs appear duplicative.

- Control comparisons appear to rely mainly on local off-corridor/background contrasts rather than a strongly matched external regional control analysis, so the distinction between local-chain behavior and broader background is reasonable but not maximally constrained.

# Conclusion

The relocated/filtered Aomori active-year catalog supports a clear, non-causal screening interpretation of the M1–M3 local system. There was already modest local M3-class activity before M1, but the final 14 days before M1 should not be treated as background because the ensuing M1-related dominated phase contains most of the M1-to-M3 large-event activity and is strongly concentrated in the M1 core. After that dominant phase is separated, the middle interval remains active and elevated relative to the conservative baseline, but it is much weaker than the M1-related phase and is not well described as a single homogeneous continuation. The final five weeks before M3 show clear local activation that persists in the M2-aware comparison. Overall, the sequence is best screened as **pre-existing local activity + a strong M1-related dominated phase + a weaker but non-empty middle phase + clear pre-M3 local activation**, with **separated bursts** and **endpoint-centered behavior** rather than a corridor-dominated or robustly migrating chain.
