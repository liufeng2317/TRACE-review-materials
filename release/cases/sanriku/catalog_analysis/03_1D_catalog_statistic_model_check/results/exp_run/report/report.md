---
author:
- TRACE
date: 2026-05-25
title: Long-Period Evolution of *b*-Value, Magnitude of Completeness, and Seismicity Rate Around M1 and M3 in the 2020–2026 Aomori Catalog
---

# Abstract

This report evaluates catalog-level activation-state evolution in the Aomori 2020–2026 earthquake catalog around the M1 and M3 sequence using a deliberately simple design: an oriented M1–M3 corridor, fixed-count sliding windows, and comparison of *b*-value, magnitude of completeness ($`M_c`$), and event rate. The preferred whole-area study region is a rotated rectangle centered at (39.622$`^{\circ}`$N, 143.332$`^{\circ}`$E), azimuth 328.3$`^{\circ}`$, length 148.6 km, width 120.0 km, containing 23,291 events. This geometry follows the M1–M3 activity corridor and is much more selective than a broad axis-aligned rectangle containing 71,692 events. Across reliable windows, the whole-area phase summaries indicate a pre-M1 reference state with *b* $`\approx 0.81`$, a distinctly lower M1-related state (*b* $`\approx 0.61`$), partial recovery during the middle phase (*b* $`\approx 0.77`$), and renewed lowering in the final pre-M3 phase (*b* $`\approx 0.65`$) while event rates remain elevated relative to pre-M1 background. The post-M3 context remains highly active but is short in duration. M1- and M3-centered subregions show similar first-order behavior, with somewhat lower middle-phase *b*-values in the M1-centered area. Spatial grid results are usable only as secondary context because support is uneven. The evidence supports a descriptive interpretation of a lower-*b*, higher-rate catalog state from M1 to M3 relative to pre-M1 background, especially in the final pre-M3 interval, but does not justify mechanistic claims such as triggering, fluid migration, slow slip, or stress transfer from catalog statistics alone.

# Scientific Objective

The objective was to describe how long-period *b*-value, magnitude of completeness ($`M_c`$), seismicity rate, and optional spatial *b*-value patterns evolved in the region containing M1 and M3, using the 2020–2026 Aomori catalog. The intended interpretation is strictly catalog-level activation-state evolution. The analysis was not designed to prove triggering, slow slip, fluid migration, or stress transfer.

The requested interpretation framework was phase-based: pre-M1 reference, M1-related phase, middle phase, final pre-M3 phase, and post-M3 context. The final report therefore emphasizes phase contrasts and sliding-window trends, while checking that the inferred *b*-value changes remain interpretable alongside $`M_c`$ and event counts.

# Data, Mainshock References, and Implemented Workflow

The analysis used the processed outputs from <a href="<CASE_ROOT>/run/03_1D_catalog_statistic_model_check/exp_run/outputs/01_catalog_bvalue_activation_analysis" class="uri"><CASE_ROOT>/run/03_1D_catalog_statistic_model_check/exp_run/outputs/01_catalog_bvalue_activation_analysis</a>. Key machine-readable tables include the study-area summary, phase summaries, robustness checks, mainshock reference table, sliding-window tables, and spatial support table.

Mainshock reference times and locations used for interpretation are listed in Table <a href="#tab:mainshocks" data-reference-type="ref" data-reference="tab:mainshocks">1</a>. These values are taken from the produced table rather than inferred manually.

<div id="tab:mainshocks">

| Event | Time                | Latitude | Longitude | Depth (km) | Magnitude |
|:------|:--------------------|---------:|----------:|-----------:|----------:|
| M1    | -11-09 08:03:39.240 |   39.402 |   143.507 |       15.9 |       6.9 |
| M2    | -12-08 14:15:10.180 |   40.968 |   142.288 |       53.5 |       7.5 |
| M3    | -04-20 07:52:58.060 |   39.842 |   143.157 |       19.4 |       7.7 |

Mainshock reference events used for time markers in the diagnostic figures and phase definitions.

</div>

The implemented workflow, according to the evidence package, was intentionally compact:

1.  define a simple M1–M3-oriented whole study area and M1/M3-centered subregions;

2.  compute fixed-count sliding-window estimates of $`M_c`$ and *b*-value, with 500-event windows and 100-event steps as the primary setting, assigning results to median window time;

3.  summarize phase-level behavior for the whole oriented area and for 60 km and 80 km subregions around M1 and M3;

4.  compare event-rate evolution with *b*-value evolution;

5.  run limited robustness tests on geometry, window size, radius, and sampled $`M_c`$ method differences.

The scientific interpretation below follows that evidence chain and uses only outputs explicitly present in the task directory.

# Study-Area Design and Spatial Framework

## Preferred whole-area geometry

The preferred whole-area study region is a rotated rectangle with center at 39.622$`^{\circ}`$N, 143.332$`^{\circ}`$E, azimuth 328.3$`^{\circ}`$, length 148.6 km, and width 120.0 km, containing 23,291 events. An ellipse with the same center, orientation, and nominal dimensions was retained as a sensitivity check, and a broad axis-aligned rectangle served as a baseline comparison. Table <a href="#tab:studyarea" data-reference-type="ref" data-reference="tab:studyarea">2</a> summarizes these definitions.

<div id="tab:studyarea">

| Region | Shape | Definition summary | Event count |
|:---|:---|:---|---:|
| Whole oriented area | Rotated rectangle | Center (39.622, 143.332), azimuth 328.3$`^{\circ}`$, length 148.6 km, width 120.0 km | 23,291 |
| Ellipse sensitivity | Ellipse | Same center, azimuth, length, and width as the preferred corridor geometry | 19,986 |
| Broad baseline | Axis-aligned rectangle | Broad comparison region used only as a baseline for selectivity | 71,692 |

Study-area summary from the produced geometry table.

</div>

The corresponding map is shown in Figure <a href="#fig:study-area-map" data-reference-type="ref" data-reference="fig:study-area-map">1</a>. Figure <a href="#fig:study-area-subregions" data-reference-type="ref" data-reference="fig:study-area-subregions">2</a> shows the whole corridor together with the M1- and M3-centered subregions used for local comparison.

<figure id="fig:study-area-map" data-latex-placement="H">
<img src="<CASE_ROOT>/run/03_1D_catalog_statistic_model_check/exp_run/outputs/01_catalog_bvalue_activation_analysis/figures/study_area_selection_map.png" style="width:92.0%" />
<figcaption>Study-area selection map for the preferred M1–M3-oriented corridor. The figure shows seismicity, M1, M3, and the chosen coverage boundary.</figcaption>
</figure>

<figure id="fig:study-area-subregions" data-latex-placement="H">
<img src="<CASE_ROOT>/run/03_1D_catalog_statistic_model_check/exp_run/outputs/01_catalog_bvalue_activation_analysis/figures/study_area_and_subregions.png" style="width:92.0%" />
<figcaption>Preferred whole study area and the M1- and M3-centered expanded subregions used for comparison. Primary subregion summaries use 80 km radii, with 60 km radii as a sensitivity test.</figcaption>
</figure>

## Why this geometry was used

The preferred corridor geometry was selected because it follows the M1–M3 alignment while excluding large amounts of off-corridor activity admitted by the broad baseline. The strongest quantitative support is the event-count reduction from 71,692 events in the broad rectangle to 23,291 events in the oriented corridor. This does not prove perfect exclusion of every unrelated source, but it demonstrates far greater selectivity for the targeted corridor.

A caveat is important. The specific southwestern-cluster metric recorded in the geometry table is zero for both the preferred oriented region and the broad baseline. Therefore, the claim that the oriented region better avoids unrelated dense activity is supported mainly by map geometry and by the large reduction in admitted events, not by that particular cluster metric. This limitation should be stated explicitly rather than hidden.

# Temporal Analysis Design

The main temporal products are based on fixed-count sliding windows. The requested and implemented primary setting used 500-event windows with 100-event steps, and each window was assigned to its median event time. For each window, the workflow tracked $`M_c`$, *b*-value, uncertainty, complete-event count, and a reliability label. To support simple interpretation, the output figures also include smoothed temporal trends.

This design is appropriate for the stated objective because it keeps the analysis interpretable: the number of events per estimate is controlled, the comparison with event rate is straightforward, and major conclusions can be expressed as contrasts among pre-M1, M1-related, middle, final pre-M3, and post-M3 intervals.

# Whole-Area Evolution of *b*-Value, $`M_c`$, and Rate

## Phase summaries

Table <a href="#tab:phase-summary" data-reference-type="ref" data-reference="tab:phase-summary">3</a> condenses the produced phase-level results for the preferred whole oriented area. All listed windows and phase summaries are flagged reliable in the output table.

<div id="tab:phase-summary">

| Phase | $`N`$ total | Rate (day$`^{-1}`$) | $`M_c`$ | *b* | $`\sigma_b`$ | Reliability |
|:---|---:|---:|---:|---:|---:|:---|
| Pre-M1 reference | 12,094 | 5.69 | 1.5 | 0.811 | 0.011 | reliable |
| M1-related | 3,297 | 94.20 | 1.8 | 0.608 | 0.015 | reliable |
| Middle phase | 1,645 | 15.52 | 1.5 | 0.773 | 0.028 | reliable |
| Final pre-M3 | 953 | 27.23 | 1.5 | 0.653 | 0.031 | reliable |
| Post-M3 context | 5,302 | 162.28 | 1.6 | 0.663 | 0.013 | reliable |

Whole-area phase summary for the preferred oriented corridor. Values are taken directly from the task output table.

</div>

These values support a clear first-order pattern:

- The pre-M1 reference state is relatively high-*b* and low-rate at catalog level (*b* $`\approx 0.81`$, rate $`\approx 5.69`$ day$`^{-1}`$).

- The M1-related phase shows an abrupt shift to much higher seismicity rate and markedly lower *b* (rate $`\approx 94.2`$ day$`^{-1}`$, *b* $`\approx 0.61`$), together with a temporary increase in $`M_c`$ to 1.8.

- The middle phase partially recovers toward higher *b*, but not back to the pre-M1 level (*b* $`\approx 0.77`$ vs 0.81 pre-M1), while rate remains well above background.

- The final pre-M3 phase again shifts to lower *b* (*b* $`\approx 0.65`$) with renewed rate elevation relative to the middle phase.

- The post-M3 context remains very active and relatively low-*b*, but the follow-up interval is short and should be interpreted cautiously.

The concise answer table reports the same pattern in median sliding-window terms: whole-area reliable-window median *b* changed from 0.828 before M1 to 0.798 during the earlier M1-to-M3 interval, with final pre-M3 at 0.560 and post-M3 context at 0.753. Because those medians come from sliding windows rather than the full phase-aggregate summaries in Table <a href="#tab:phase-summary" data-reference-type="ref" data-reference="tab:phase-summary">3</a>, the exact numbers differ slightly, but the qualitative interpretation is consistent.

## Timeline diagnostics

Figure <a href="#fig:whole-timeline" data-reference-type="ref" data-reference="fig:whole-timeline">3</a> provides the primary whole-area time series for *b*-value and $`M_c`$, including the event-window trend and temporal markers. Figure <a href="#fig:rate-vs-b" data-reference-type="ref" data-reference="fig:rate-vs-b">4</a> compares rate evolution with *b*-value evolution directly.

<figure id="fig:whole-timeline" data-latex-placement="H">
<img src="<CASE_ROOT>/run/03_1D_catalog_statistic_model_check/exp_run/outputs/01_catalog_bvalue_activation_analysis/figures/whole_area_bvalue_mc_timeline.png" style="width:95.0%" />
<figcaption>Whole oriented area sliding-window <em>b</em>-value and <span class="math inline"><em>M</em><sub><em>c</em></sub></span> timeline. The primary setup uses fixed-count windows, and the figure includes mainshock markers and smoothed temporal structure for interpretation.</figcaption>
</figure>

<figure id="fig:rate-vs-b" data-latex-placement="H">
<img src="<CASE_ROOT>/run/03_1D_catalog_statistic_model_check/exp_run/outputs/01_catalog_bvalue_activation_analysis/figures/event_rate_vs_bvalue.png" style="width:95.0%" />
<figcaption>Comparison of event-rate evolution and <em>b</em>-value evolution for the preferred whole study area. The figure is intended for descriptive activation-state interpretation rather than mechanistic inference.</figcaption>
</figure>

## Interpretation of the whole-area evolution

The simplest descriptive interpretation is that the catalog moved from a pre-M1 background-like state to a lower-*b*, higher-rate state after M1, did not fully recover during the middle interval, and showed renewed pre-M3 activation before M3. In the language requested by the user, the preferred whole-area evidence is more consistent with sustained elevated activation followed by renewed pre-M3 activation than with a full relaxation back to background.

The pre-M1 to post-M1 contrast is especially clear because it appears in both *b*-value and rate. Relative to the pre-M1 reference, the broad M1-to-M3 interval is lower in *b* and higher in rate. The final pre-M3 interval differs from the earlier M1-to-M3 middle interval by combining still-elevated rate with another drop in *b*. This is the most distinctive pre-M3 catalog-level change in the evidence package.

At the same time, this pattern should remain descriptive. A lower *b*-value accompanied by sustained or renewed rate elevation may suggest a shift toward relatively stronger activation or a lower apparent background-like state, but catalog statistics alone do not identify the physical cause.

# Comparison of M1- and M3-Centered Subregions

The 80 km subregions were the requested primary local comparison, with 60 km circles used as a sensitivity check. Figure <a href="#fig:subregion-comparison" data-reference-type="ref" data-reference="fig:subregion-comparison">5</a> summarizes the whole-area and subregion time series.

<figure id="fig:subregion-comparison" data-latex-placement="H">
<img src="<CASE_ROOT>/run/03_1D_catalog_statistic_model_check/exp_run/outputs/01_catalog_bvalue_activation_analysis/figures/whole_vs_subregion_comparison.png" style="width:95.0%" />
<figcaption>Comparison of sliding <em>b</em>-value behavior between the whole oriented area and the expanded M1- and M3-centered subregions.</figcaption>
</figure>

Phase summaries show that both 80 km subregions share the main whole-area pattern: high pre-M1 *b*, strong M1-related lowering, partial middle-phase recovery, and renewed lowering in the final pre-M3 interval. The differences are modest but informative.

For the 80 km M1-centered region:

- pre-M1 *b* $`= 0.809`$,

- M1-related *b* $`= 0.606`$,

- middle-phase *b* $`= 0.765`$,

- final pre-M3 *b* $`= 0.656`$,

- post-M3 *b* $`= 0.657`$.

For the 80 km M3-centered region:

- pre-M1 *b* $`= 0.807`$,

- M1-related *b* $`= 0.599`$,

- middle-phase *b* $`= 0.753`$,

- final pre-M3 *b* $`= 0.641`$,

- post-M3 *b* $`= 0.687`$.

Thus, both local regions behave similarly at first order. The concise report answers table notes middle-phase median sliding-window *b*-values of 0.725 for the M1-centered area and 0.766 for the M3-centered area in the 80 km comparison, suggesting some local contrast, but not a qualitative divergence in regime. The main report conclusion should therefore be that M1- and M3-centered subregions differ in detail, yet both support the same corridor-scale activation narrative.

The 60 km sensitivity results preserve the same sign of the main phase contrasts. For example, the M1 60 km region drops from pre-M1 *b* $`= 0.778`$ to middle-phase *b* $`= 0.756`$ and final pre-M3 *b* $`= 0.646`$, while the M3 60 km region drops from 0.835 to 0.714 and then 0.632. This strengthens confidence that the principal interpretation is not an artifact of the exact 80 km radius choice.

# Spatial *b*-Value Context

Spatial grid products were generated and the main map is shown in Figure <a href="#fig:spatial-grid" data-reference-type="ref" data-reference="fig:spatial-grid">6</a>. The support table indicates that all mapped cells were flagged reliable, but support is uneven across the corridor, especially toward edges where complete-event counts and uncertainty vary substantially.

<figure id="fig:spatial-grid" data-latex-placement="H">
<img src="<CASE_ROOT>/run/03_1D_catalog_statistic_model_check/exp_run/outputs/01_catalog_bvalue_activation_analysis/figures/spatial_bvalue_maps_whole_oriented_area.png" style="width:95.0%" />
<figcaption>Spatial <em>b</em>-value context for the whole oriented corridor. These maps are suitable as secondary context only, not as primary evidence.</figcaption>
</figure>

The support table shows a broad range of cell-scale *b*-values, from about 0.52 to above 1.1, with $`M_c`$ varying from about 1.1 to 1.8 and complete-event counts ranging from a few hundred to several thousand. Because this support is spatially uneven, the grid-cell results are best treated as descriptive context rather than as decisive evidence for spatially localized physical changes. That assessment is consistent with the evaluation summary, which explicitly states that grid-cell maps are suitable only as secondary context.

Accordingly, the report does not use the spatial grid as a main pillar of inference. The main evidence remains the corridor-scale and subregion time series.

# Robustness Checks Relevant to the Main Conclusion

Only limited robustness tests were requested, and the produced table follows that instruction. Table <a href="#tab:robustness" data-reference-type="ref" data-reference="tab:robustness">4</a> summarizes the parts most relevant to the main interpretation.

<div id="tab:robustness">

| Test type | Setting | Pre$`-`$middle $`\Delta b`$ | Final$`-`$middle $`\Delta b`$ | Note |
|:---|:---|---:|---:|:---|
| Window size | 300 events | 0.068 | -0.122 | Whole oriented area |
| Window size | 500 events | 0.029 | -0.238 | Whole oriented area |
| Window size | 750 events | 0.040 | -0.194 | Whole oriented area |
| Geometry | Rectangle vs ellipse | small phase differences | – | Rectangle-minus-ellipse median reliable phase *b* differences remain small |
| Radius | M1 60 km | 0.046 | -0.195 | Subregion sensitivity |
| Radius | M1 80 km | 0.117 | -0.169 | Subregion sensitivity |
| Radius | M3 60 km | 0.122 | -0.167 | Subregion sensitivity |
| Radius | M3 80 km | 0.047 | -0.205 | Subregion sensitivity |
| $`M_c`$ method | MAXC vs KS checkpoints | 0.250 | 0.046 | Median MAXC$`-`$KS $`M_c`$ difference across sampled whole-area windows |

Limited robustness checks directly relevant to the principal interpretation.

</div>

The key message is that the sign of the principal contrast is stable across the tested window sizes and radii: pre-M1 tends to have higher *b* than the middle interval, and the final pre-M3 interval tends to have lower *b* than the earlier middle phase. The exact amplitudes vary, but the qualitative pattern does not reverse.

The most important methodological caution is the sampled $`M_c`$-method sensitivity. The checkpoint comparison indicates a median MAXC-minus-KS $`M_c`$ difference of about 0.25 in sampled whole-area windows. This means absolute *b*-values retain non-negligible method dependence, so the report should emphasize qualitative temporal contrasts more strongly than precise absolute *b* numbers.

# Answers to the Main Scientific Questions

## What coverage area was used and why?

The preferred coverage area was a rotated rectangle centered at (39.622$`^{\circ}`$N, 143.332$`^{\circ}`$E), azimuth 328.3$`^{\circ}`$, length 148.6 km, width 120.0 km, containing 23,291 events. It was chosen to follow the M1–M3 corridor while retaining roughly 60 km end margins and excluding large amounts of off-corridor activity.

## Did the oriented M1–M3 region avoid unrelated high-density source regions better than the broad rectangle?

Yes, in the practical sense relevant to this study: it is much more selective, admitting 23,291 events rather than 71,692. However, the specific southwestern-cluster metric in the summary table was zero for both geometries, so that specific exclusion metric is not the basis of the conclusion. The conclusion rests mainly on the mapped geometry and the major reduction in admitted events.

## What is the main temporal pattern of *b*-value evolution?

The main pattern is a shift from a pre-M1 higher-*b*, lower-rate state to a lower-*b*, higher-rate state after M1, followed by partial recovery in the middle phase and renewed lowering in the final pre-M3 phase.

## How does *b*-value behave before and after M1?

Before M1, the whole-area phase summary gives *b* $`\approx 0.81`$ with low background-like rate. Immediately after M1, *b* drops to about 0.61 while rate rises sharply, and $`M_c`$ temporarily increases to about 1.8. In the subsequent middle phase, *b* rises again but remains below the pre-M1 reference.

## How does the overall M1-to-M3 state compare with the pre-M1 background?

At catalog level, the M1-to-M3 interval is lower in *b* and more active in rate than the pre-M1 background. This supports a descriptive interpretation of a more activated corridor-scale state between M1 and M3.

## Is the final pre-M3 phase different from the earlier M1-to-M3 interval?

Yes. Relative to the earlier middle phase, the final pre-M3 interval has lower *b* and higher rate. This is one of the clearest temporal contrasts in the report and is robust to the limited window-size and radius checks.

## What possible catalog-level stress or activation-state change is suggested?

The combined decrease in *b*-value and sustained or renewed rate elevation is consistent with a descriptive shift toward relatively stronger activation or a lower apparent background-like state. This wording should remain cautious: it is a catalog-level description, not mechanistic proof of any specific process.

## How do $`M_c`$ and event rate evolve alongside *b*-value?

$`M_c`$ is generally stable near 1.5 in many intervals, rises to about 1.8 during the strong M1-related burst, and becomes somewhat more variable during the strongest late-2025 to 2026 activity. Event rate increases sharply in the M1-related phase, remains above pre-M1 background during the middle phase, rises again before M3, and is very high after M3. Therefore, low *b*-value intervals should be read together with $`M_c`$ stability and rate elevation rather than in isolation.

## Do M1-centered and M3-centered subregions behave differently?

They differ in detail but not in first-order narrative. Both show high pre-M1 *b*, strong M1-related lowering, partial middle-phase recovery, and lower final pre-M3 values. Some local contrasts appear in middle-phase medians and post-M3 behavior, but they do not overturn the corridor-scale interpretation.

## Are grid-cell results meaningful?

They are meaningful enough for secondary context only. Because spatial support is uneven and edge cells are weaker, the grid maps should not be used as the primary evidence base.

## What physical follow-up is most justified?

The most justified next step is a targeted, completeness-aware spatiotemporal comparison with independent constraints such as waveforms, focal mechanisms, or geodetic data. Such follow-up could test physical hypotheses without over-interpreting catalog statistics alone.

# Limitations

Several limitations materially affect interpretation:

1.  **$`M_c`$ method sensitivity.** Sampled checkpoint comparisons show a notable MAXC-versus-KS difference, with median MAXC-minus-KS $`M_c`$ around 0.25. Absolute *b*-values are therefore somewhat method-dependent.

2.  **Late-interval completeness variability.** $`M_c`$ increases and becomes more variable during the strongest late-2025 to 2026 activity. Late *b*-value drops remain interpretable, but only when read with $`M_c`$ and reliability information.

3.  **Area-selection quantification.** The superiority of the oriented region over the broad rectangle is strongly supported by geometry and event-count reduction, but one explicit southwestern-cluster metric was not discriminatory.

4.  **Short post-M3 context.** The catalog ends on 2026-05-22, so post-M3 behavior is observed for only a short follow-up interval.

5.  **Secondary value of spatial grids.** Grid support is uneven across the corridor, especially near edges, limiting the interpretability of cell-scale patterns.

6.  **Output inventory truncation.** The task handoff was flagged as outputs-truncated, although the key requested figures and tables used here are present and sufficient for reporting.

# Conclusion

The Aomori 2020–2026 catalog, analyzed with a simple M1–M3 corridor design and fixed-count sliding windows, supports a coherent descriptive pattern. Relative to the pre-M1 background-like state, the corridor entered a lower-*b*, higher-rate state after M1. The middle phase showed only partial recovery, and the final pre-M3 interval displayed renewed lowering of *b*-value together with renewed rate elevation. M1- and M3-centered subregions broadly reinforce the same interpretation. Spatial grid products provide context but are not strong enough to lead the interpretation.

The scientifically defensible takeaway is therefore a catalog-level evolution from pre-M1 background-like behavior to sustained elevated activation after M1, with a stronger low-*b* re-intensification before M3. This is an interpretable catalog pattern, not proof of a specific physical mechanism.

# Key Output Paths

Primary outputs cited in this report are located at:

- Figures directory: <a href="<CASE_ROOT>/run/03_1D_catalog_statistic_model_check/exp_run/outputs/01_catalog_bvalue_activation_analysis/figures" class="uri"><CASE_ROOT>/run/03_1D_catalog_statistic_model_check/exp_run/outputs/01_catalog_bvalue_activation_analysis/figures</a>

- Tables directory: <a href="<CASE_ROOT>/run/03_1D_catalog_statistic_model_check/exp_run/outputs/01_catalog_bvalue_activation_analysis/tables" class="uri"><CASE_ROOT>/run/03_1D_catalog_statistic_model_check/exp_run/outputs/01_catalog_bvalue_activation_analysis/tables</a>

- Spatial outputs: <a href="<CASE_ROOT>/run/03_1D_catalog_statistic_model_check/exp_run/outputs/01_catalog_bvalue_activation_analysis/spatial" class="uri"><CASE_ROOT>/run/03_1D_catalog_statistic_model_check/exp_run/outputs/01_catalog_bvalue_activation_analysis/spatial</a>
