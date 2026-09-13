---
author:
- TRACE
date: 2026-05-25
title: Catalog-Level Screening of b-Value, Magnitude Hierarchy, and Moment-Release Patterns in the Aomori M1–M3 Local Earthquake System
---

# Abstract

This report screens whether the relocated/filtered Aomori active-year catalog for the local M1–M3 earthquake system is more consistent, at catalog level, with independent local ruptures, phase-separated activation, compact or swarm-like compound activation, repeated shallow local activation, or background/window effects. The analysis uses neutral geometric subsets around M1 and M3, fixed-count sliding-window completeness and b-value estimation, magnitude-hierarchy summaries, and magnitude-derived moment-release proxies. The combined local zone is the primary spatial domain. The main result is a cautious but coherent screening outcome: the catalog is not well explained as a simple background or window artifact, and it is more consistent with a temporally phase-structured local system combining a dominant M1-related episode, a weaker but still elevated middle phase, and a clear final pre-M3 local activation phase. The catalog also shows strong single-event moment dominance, especially in the pre-M3 phase, so the sequence is not well described as a uniformly distributed swarm-like compound activation over the full M1-to-M3 interval. Spatial and depth summaries favor mixed M1-centered and M3-centered local overlap or separated local bursts over robust monotonic migration. However, many sliding-window b-value estimates are only exploratory because magnitude-of-completeness estimates are not uniformly stable, and focal-mechanism coverage in the local system is far too sparse to materially resolve the central hypotheses. Accordingly, the results support catalog-level screening only and do not justify causal inference about triggering, stress transfer, fluid migration, or slow slip.

# Scientific objective

The scientific objective was to test, using catalog statistics alone, whether the relocated/filtered Aomori active-year catalog for local events in the M1–M3 system is more consistent with one or more of the following broad interpretations:

1.  largely independent ruptures,

2.  phase-separated activation between the M1 and M3 time periods,

3.  compact or swarm-like compound activation,

4.  repeated shallow local activation, or

5.  background or window-selection effects.

The task was explicitly framed as a *catalog-level screening* problem. The workflow therefore avoids inferring physical triggering, stress transfer, fluid migration, or slow-slip behavior from seismicity statistics alone.

The analysis used the relocated/filtered catalog in <a href="<CASE_ROOT>/data/catalog/Snet_catalog_relocate_250601_260501.csv" class="uri"><CASE_ROOT>/data/catalog/Snet_catalog_relocate_250601_260501.csv</a> and the mainshock table in <a href="<CASE_ROOT>/data/catalog/main_earthquake.csv" class="uri"><CASE_ROOT>/data/catalog/main_earthquake.csv</a>. Supporting context files were available for source mechanisms and stations, but the main evidence chain in this report is driven by the validated catalog-screening and mechanism-coverage audit outputs listed below.

# Implemented workflow and evidence base

## What was actually implemented

The implemented workflow built a validated master catalog and screened it in neutral geometric domains centered on M1 and M3. The primary spatial domain was the combined local zone, defined as events within 60 km of either M1 or M3. Secondary subsets included M1-centered and M3-centered core and extended zones, along-axis subsets, off-axis subsets, and overlap subsets. M2-related events were flagged and used in robustness checks rather than removed by default.

The core implementation products were generated in:

- <a href="<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/01_catalog_screening_analysis" class="uri"><CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/01_catalog_screening_analysis</a>

- <a href="<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/02_mechanism_coverage_audit" class="uri"><CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/02_mechanism_coverage_audit</a>

For b-value analysis, the primary design used fixed-count sliding windows of 500 events with a 100-event step in the combined local zone, assigning each estimate to the median event time of the window. A 200-event step provided a smoothing and robustness sensitivity. For each window, the workflow estimated magnitude of completeness $`M_c`$, b-value, uncertainty, fitting range, and reliability class. Reliability was graded rather than treated as a binary usable/unusable label. The main temporal products are the sliding b-value figure and the reliability timeline in Figures <a href="#fig:btime" data-reference-type="ref" data-reference="fig:btime">1</a> and <a href="#fig:reliability" data-reference-type="ref" data-reference="fig:reliability">2</a>.

Magnitude hierarchy and moment-release screening were implemented with phase-wise and burst-wise summaries, using a magnitude-derived moment proxy rather than direct source-parameter inversion. These outputs were used only comparatively, to assess whether moment release was distributed or dominated by a few larger events. Spatial comparisons were carried out across the predefined geometric subsets without assuming a migration mechanism.

A separate focal-mechanism audit matched mechanism metadata to catalog events using time, horizontal-distance, and depth tolerances, then tested coverage and representativeness by phase, magnitude threshold, and spatial class.

## Primary output files used in this report

The report relies most directly on the following artifacts:

- sliding b-value evolution: <a href="<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/01_catalog_screening_analysis/figure_sliding_bvalue_temporal_evolution.png" class="uri"><CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/01_catalog_screening_analysis/figure_sliding_bvalue_temporal_evolution.png</a>

- Mc and reliability timeline: <a href="<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/01_catalog_screening_analysis/figure_sliding_mc_reliability_timeline.png" class="uri"><CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/01_catalog_screening_analysis/figure_sliding_mc_reliability_timeline.png</a>

- spatial b-value comparison: <a href="<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/01_catalog_screening_analysis/figure_bvalue_spatial_comparison.png" class="uri"><CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/01_catalog_screening_analysis/figure_bvalue_spatial_comparison.png</a>

- magnitude-frequency summary: <a href="<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/01_catalog_screening_analysis/figure_magnitude_frequency_annotations.png" class="uri"><CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/01_catalog_screening_analysis/figure_magnitude_frequency_annotations.png</a>

- cumulative moment proxy: <a href="<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/01_catalog_screening_analysis/figure_cumulative_moment_proxy.png" class="uri"><CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/01_catalog_screening_analysis/figure_cumulative_moment_proxy.png</a>

- burst and hierarchy summary: <a href="<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/01_catalog_screening_analysis/figure_burst_moment_hierarchy_summary.png" class="uri"><CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/01_catalog_screening_analysis/figure_burst_moment_hierarchy_summary.png</a>

- evidence matrix: <a href="<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/01_catalog_screening_analysis/figure_catalog_mechanism_evidence_matrix.png" class="uri"><CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/01_catalog_screening_analysis/figure_catalog_mechanism_evidence_matrix.png</a>

- mechanism coverage overview: <a href="<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/02_mechanism_coverage_audit/mechanism_coverage_overview.png" class="uri"><CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/02_mechanism_coverage_audit/mechanism_coverage_overview.png</a>

- final synthesis table: <a href="<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/01_catalog_screening_analysis/final_answer_table.csv" class="uri"><CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/01_catalog_screening_analysis/final_answer_table.csv</a>

- conclusion stability: <a href="<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/01_catalog_screening_analysis/conclusion_stability_matrix.csv" class="uri"><CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/01_catalog_screening_analysis/conclusion_stability_matrix.csv</a>

# Results

## Overall screening outcome

The final synthesis products show that the catalog-level screening supports interpretation *with caution*. The synthesis table states that sliding-window b-value estimates are reliable enough to interpret only *with caution*, that phase-level aggregate b-values are mostly consistent with the sliding-window evolution, that moment release is *single-event dominated*, and that the main hypotheses requiring consideration are independent local ruptures, phase-separated activation between M1 and M3, compact/swarm-like compound activation, repeated shallow local activation, and background/window artifact checks. The same table emphasizes follow-up priorities such as relocation quality control, waveform similarity, detection-completeness work, and formal change-point analysis rather than immediate causal interpretation.

The conclusion-stability matrix reports stable conclusions for sliding-b-value interpretability, middle-phase M2 sensitivity, and moment dominance. This means the main screening outcome does not depend on a single fragile implementation choice, although the uncertainty level remains moderate.

## Sliding-window b-value and completeness behavior

The b-value analysis is interpretable at the level of broad temporal tendencies, but many windows are not high-confidence. In the primary combined-local subset, the 500-event, 100-step design yielded 87 interpretable windows, with 24 classified as robust, 4 as usable with caution, and 59 as exploratory; no windows were labeled not interpretable in the summary table. The median b-value for the combined local zone is 0.714 with median $`M_c=1.5`$ (Table <a href="#tab:spatialb" data-reference-type="ref" data-reference="tab:spatialb">1</a>). A nearly identical median b-value of 0.709 was obtained in the M2-aware sensitivity, supporting the statement that M2-aware filtering has limited influence on the main interpretation.

The reliability file shows that many windows were downgraded because of disagreement among $`M_c`$ estimation methods, not because of complete failure of the sliding-window framework. This distinction matters scientifically: the temporal curve is suitable for screening broad tendencies, but short-lived oscillations or visually sharp changes near phase boundaries should not be treated as precise evidence of abrupt physical state changes.

Figure <a href="#fig:btime" data-reference-type="ref" data-reference="fig:btime">1</a> is therefore the primary temporal interpretation product, while Figure <a href="#fig:reliability" data-reference-type="ref" data-reference="fig:reliability">2</a> provides the necessary quality context. Together they support the report statement that sliding-window b-values are *usable for screening, not for fine-scale causal inference*.

<figure id="fig:btime" data-latex-placement="H">
<img src="<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/01_catalog_screening_analysis/figure_sliding_bvalue_temporal_evolution.png" style="width:95.0%" />
<figcaption>Primary sliding-window b-value evolution for the combined local zone. Phase boundaries are overlaid in the source figure and are used for phase-aware interpretation rather than reducing the analysis to one b-value per phase.</figcaption>
</figure>

<figure id="fig:reliability" data-latex-placement="H">
<img src="<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/01_catalog_screening_analysis/figure_sliding_mc_reliability_timeline.png" style="width:95.0%" />
<figcaption>Magnitude-of-completeness and reliability timeline for the sliding-window analysis. Many windows are exploratory because of <span class="math inline"><em>M</em><sub><em>c</em></sub></span>-method disagreement, which limits detailed interpretation of short-timescale fluctuations.</figcaption>
</figure>

## Phase-aware interpretation

The context and output summaries jointly indicate that the pre-M1 conservative baseline, defined from catalog start to M1$`-`$<!-- -->14 days, should exclude the immediate M1 lead-in. Relative to that baseline, the M1–M3 interval shows a clear activation structure:

- activity from M1$`-`$<!-- -->14 days to M1$`+`$<!-- -->21 days is strongly elevated and contains most of the M3+, M4+, and M5+ activity in the full M1-to-M3 interval;

- the middle phase from M1$`+`$<!-- -->21 days to M3$`-`$<!-- -->35 days remains elevated above baseline but is much weaker than the M1-related phase;

- the final pre-M3 local activation from M3$`-`$<!-- -->35 days to M3 is clear and remains stable under M2-aware comparison.

These statements are consistent with the phase-oriented b-value and rate interpretation described in the context package and with the stable-conclusion markers in the conclusion-stability matrix.

The temporal structure is therefore more consistent with *phase-separated activation* than with a stationary background process or a purely window-defined artifact. At the same time, because reliability is mixed, the b-value analysis supports broad phasing rather than exact breakpoint timing or causal interpretation.

## Spatial comparison across geometric subsets

The spatial b-value comparison shows only modest differences in median b-value among major subsets (Table <a href="#tab:spatialb" data-reference-type="ref" data-reference="tab:spatialb">1</a>; Figure <a href="#fig:spatialb" data-reference-type="ref" data-reference="fig:spatialb">3</a>). The combined local zone has median b-value 0.714. M1-centered subsets have medians around 0.648–0.708, M3-centered subsets around 0.695–0.730, along-axis subsets around 0.662–0.683, overlap around 0.677, and off-axis subsets around 0.741–0.746. These amplitudes are small, so they should be interpreted as weak tendencies rather than strong separations.

This pattern supports the context statement that M1-centered, M3-centered, along-axis, and off-axis contributions must be quantified separately and that no corridor-controlled process should be assumed a priori. In particular, the modest and reliability-limited spatial differences do *not* provide strong support for a robust M1-to-M3 migration interpretation. Instead, they are more compatible with mixed local overlap and separated bursts in M1-centered and M3-centered areas.

<figure id="fig:spatialb" data-latex-placement="H">
<img src="<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/01_catalog_screening_analysis/figure_bvalue_spatial_comparison.png" style="width:90.0%" />
<figcaption>Spatial comparison of sliding-window b-value summaries across geometric subsets. Differences are present but small in amplitude, so they are screening-level tendencies rather than strong diagnostic separations.</figcaption>
</figure>

<div id="tab:spatialb">

| Subset           | Windows | Robust | Caution | Exploratory | Median $`b`$ |
|:-----------------|--------:|-------:|--------:|------------:|-------------:|
| Combined local   |      87 |     24 |       4 |          59 |        0.714 |
| M1 extended      |      70 |     18 |       2 |          50 |        0.708 |
| M1 core          |      40 |      9 |       3 |          28 |        0.648 |
| M3 extended      |      68 |     13 |       1 |          54 |        0.695 |
| M3 core          |      24 |      8 |       3 |          13 |        0.730 |
| Along-axis 20 km |      44 |      8 |       1 |          35 |        0.662 |
| Along-axis 30 km |      47 |     15 |       1 |          31 |        0.683 |
| Off-axis 20 km   |      38 |     14 |       2 |          22 |        0.746 |
| Off-axis 30 km   |      35 |     10 |       2 |          23 |        0.741 |
| Overlap 60 km    |      51 |     13 |       1 |          37 |        0.677 |

Summary of major spatial b-value subsets from `spatial_bvalue_comparison.csv`.

</div>

## Magnitude hierarchy and frequency structure

The magnitude-frequency and hierarchy products indicate that the sequence is not a simple uniform small-event swarm across the full M1-to-M3 interval. The report context specifies that most of the larger-magnitude activity is concentrated in the M1-related lead-in and immediate phase, while the final pre-M3 local activation remains clear but is dominated by the M3-side culmination. This phase structuring weakens a purely background interpretation.

Figure <a href="#fig:mfd" data-reference-type="ref" data-reference="fig:mfd">4</a> documents the frequency and threshold behavior used in the screening. In combination with the phase summaries, it supports two linked conclusions: first, the catalog contains a genuine hierarchy in magnitude release across phases; second, the role of larger events is concentrated in limited parts of the interval rather than being evenly distributed.

<figure id="fig:mfd" data-latex-placement="H">
<img src="<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/01_catalog_screening_analysis/figure_magnitude_frequency_annotations.png" style="width:90.0%" />
<figcaption>Magnitude-frequency diagnostic used to place b-value and hierarchy results in context. The figure supports the interpretation that the sequence is not explained solely by a stationary small-event background.</figcaption>
</figure>

## Moment-release proxy and dominance pattern

The moment-proxy analysis provides one of the clearest screening results. In the combined local zone, the M1-related primary phase has a total moment proxy of approximately $`5.14\times10^{19}`$, with the largest event contributing 54.8% of the phase total and the largest three events contributing 84.0%. The middle phase has a smaller total moment proxy of approximately $`4.13\times10^{18}`$, with the largest event contributing 43.0% and the largest three events 93.8%. The pre-M3 primary phase is much more strongly dominated, with total moment proxy approximately $`4.61\times10^{20}`$ and the largest event contributing 96.9% of the total. Over the full M1-to-M3 interval, the largest single event contributes 86.8% of the total moment proxy, and the largest three events contribute 95.0%.

These results strongly indicate that the sequence is *single-event dominated* in moment release, especially near M3. That dominance is inconsistent with a simple picture of the full M1-to-M3 interval as a compact, swarm-like, evenly distributed compound activation. A compound or clustered character may still apply to some local burst structure in event counts, but the energy-release hierarchy is highly concentrated in a few larger events.

At the same time, the phase pattern is not trivial. The M1-related phase contains the main early concentration of larger events, the middle phase remains elevated but weaker, and the pre-M3 phase culminates in overwhelming dominance by the largest event. This combination is more consistent with *phase-separated activation and repeated local activation* than with a flat background process.

<figure id="fig:cum_moment" data-latex-placement="H">
<img src="<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/01_catalog_screening_analysis/figure_cumulative_moment_proxy.png" style="width:95.0%" />
<figcaption>Cumulative moment-proxy evolution by subset and time. The main message is comparative: release is concentrated into specific phases rather than being smoothly distributed throughout the interval.</figcaption>
</figure>

<figure id="fig:burst_moment" data-latex-placement="H">
<img src="<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/01_catalog_screening_analysis/figure_burst_moment_hierarchy_summary.png" style="width:95.0%" />
<figcaption>Burst-wise and phase-wise hierarchy summary. The figure complements the cumulative curves by showing that moment release is concentrated in a few dominant events and bursts.</figcaption>
</figure>

## Mechanism-hypothesis screening synthesis

The evidence matrix and final-answer table together indicate the preferred screening logic. The catalog does not support dismissal of the system as a simple background or window artifact. The temporal organization is too strong, the activity excess above baseline is too clear, and the pre-M3 local activation is too stable under M2-aware comparison for that interpretation to be favored.

The catalog also does not favor a single simple migration narrative from M1 to M3. Spatial-depth screening in the context package favors mixed M1-centered and M3-centered local overlap or separated local bursts rather than robust monotonic migration, and the small-amplitude spatial b-value differences are consistent with that caution.

The remaining plausible catalog-level interpretations are therefore mixed:

- **Phase-separated activation**: supported by the strong M1-related phase, weaker but elevated middle phase, and clear final pre-M3 activation.

- **Repeated shallow local activation**: supported at screening level by the shallow-dominated depth distribution noted in the context package and by repeated local activity around the M1 and M3 zones.

- **Independent local ruptures**: not rejected, especially because the moment release is concentrated in a few dominant larger events and because the catalog does not require a connecting migration process.

- **Compact/swarm-like compound activation**: weakened for the full interval because the moment budget is strongly single-event dominated rather than diffusely shared, though some local bursts may still have compound characteristics in event counts.

- **Background/window effects**: weakened because baseline-to-phase contrasts and pre-M3 activation remain clear and stable.

This synthesis is visualized in Figure <a href="#fig:matrix" data-reference-type="ref" data-reference="fig:matrix">7</a>.

<figure id="fig:matrix" data-latex-placement="H">
<img src="<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/01_catalog_screening_analysis/figure_catalog_mechanism_evidence_matrix.png" style="width:95.0%" />
<figcaption>Catalog-level evidence matrix linking outputs to the screened hypothesis classes. This is the appropriate synthesis level for the present task because the objective is screening, not physical-process attribution.</figcaption>
</figure>

# Focal-mechanism audit and its interpretive value

The standalone mechanism audit shows that event matching is technically successful but scientifically under-representative for the local-system question. The preferred tolerance grid uses 1 s in time, 2 km horizontal distance, and 2 km depth. Under that setting, 240 mechanism rows match catalog events, with median residuals of 0.01 s, 0.085 km, and 0.08 km, and essentially no ambiguity. Thus the matching procedure itself is strong.

However, the same audit shows that mechanism coverage is extremely sparse relative to the catalog size: the full catalog contains 25,646 events, the local zone contains 9,109 events, but only 240 catalog events have matched mechanism rows and the fraction with mechanism coverage in the local zone is only 0.000878. The cross-task limitations further state that the combined M1–M3 local zone contains only 8 matched events, with zero matched events in M1-centered and along-axis local classes and only one complete mechanism in the combined local zone. That coverage is too sparse and too biased to materially support or reject the core catalog hypotheses.

Therefore, focal mechanisms can be mentioned only as an audit result about data availability, not as decisive evidence on rupture style or physical process for this report.

<figure id="fig:mecha_overview" data-latex-placement="H">
<img src="<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/02_mechanism_coverage_audit/mechanism_coverage_overview.png" style="width:90.0%" />
<figcaption>Mechanism coverage overview from the standalone audit. Matching quality is strong, but local-system coverage is far too sparse to materially resolve the main scientific question.</figcaption>
</figure>

<div id="tab:mecha">

| Metric                                      |    Value |
|:--------------------------------------------|---------:|
| Catalog total events                        |   25,646 |
| Catalog local-zone events                   |    9,109 |
| Mechanism rows available                    |      354 |
| Matched mechanism rows                      |      240 |
| Catalog fraction with mechanism, all events |  0.00936 |
| Catalog fraction with mechanism, local zone | 0.000878 |
| Best time tolerance (s)                     |      1.0 |
| Best horizontal tolerance (km)              |      2.0 |
| Best depth tolerance (km)                   |      2.0 |
| Median time residual (s)                    |     0.01 |
| Median horizontal residual (km)             |    0.085 |
| Median depth residual (km)                  |     0.08 |

Selected mechanism audit metrics from `mechanism_coverage_audit.csv`.

</div>

# Integrated interpretation

Taken together, the catalog statistics support a cautious integrated interpretation.

First, the sequence is **not well explained as a simple background or window artifact**. The pre-M1 conservative baseline is substantially weaker than the M1–M3 interval, the M1-related phase concentrates much of the larger-event activity, the middle phase remains elevated above baseline, and the final pre-M3 activation is clear and stable under M2-aware comparison.

Second, the sequence is **more consistent with phase-separated activation than with a single stationary process**. The temporal partition into an M1-related dominant phase, a weaker middle phase, and a final pre-M3 local phase is one of the strongest stable conclusions of the analysis.

Third, the sequence is **not strongly supportive of a full-interval compact/swarm-like compound activation** when evaluated by moment release. The largest event dominates 86.8% of the total moment proxy over the full M1-to-M3 interval, and the pre-M3 phase is overwhelmingly dominated by its largest event. That hierarchy is too strong for the full sequence to be described primarily as a diffuse swarm-like release process.

Fourth, the results are **compatible with repeated shallow local activation and/or largely independent local ruptures**, but these possibilities are not fully separable using catalog statistics alone. The shallow-dominated depth pattern, mixed M1-centered and M3-centered local overlap, and absence of robust migration support this cautious interpretation. Still, catalog screening alone cannot distinguish whether similar statistical patterns arise from repeated local preparation, partially independent rupture occurrence, or other unmodeled observational effects.

Finally, the b-value analysis adds useful screening information but does not settle the interpretation. Its greatest value here is to show that temporal and spatial tendencies are not random noise, while its main limitation is that many windows are exploratory because $`M_c`$ is not uniformly stable.

# Limitations

The main limitations are substantial and must bound the interpretation:

1.  **Mixed sliding-window reliability.** Many windows are exploratory because different $`M_c`$ methods do not always agree. Broad temporal tendencies are usable, but short-timescale fluctuations and boundary-adjacent changes should not be over-interpreted.

2.  **Dependence on completeness choice.** Absolute b-values and some phase-to-phase contrasts may shift with alternative $`M_c`$ choices, even if the main conclusions were reported as stable.

3.  **Weak spatial amplitude.** Spatial b-value differences are small, so they should be treated as weak tendencies rather than strong diagnostic separations.

4.  **Sparse mechanism coverage.** The focal-mechanism audit shows excellent matching quality but extremely poor local-system representativeness. Mechanisms cannot materially support or reject the central catalog hypotheses.

5.  **Moment-release proxy only.** Moment analysis is based on magnitude-derived proxy values, not direct source inversions, so it is useful comparatively but cannot establish rupture interaction or source-process physics.

6.  **Catalog-level scope only.** None of the statistics presented here justify inference of triggering, stress transfer, fluid migration, or slow slip.

# Conclusions

The relocated/filtered Aomori active-year M1–M3 local catalog supports the following catalog-level screening conclusions:

1.  The sequence is not adequately described as a simple background or window-selection artifact.

2.  The strongest supported catalog-level picture is a **phase-structured local system**, with a dominant M1-related phase, a weaker but still elevated middle phase, and a clear final pre-M3 local activation phase.

3.  Moment release is **strongly single-event dominated**, especially near M3, which weakens a full-interval compact or uniformly swarm-like compound-activation interpretation.

4.  Spatial summaries favor **mixed M1-centered and M3-centered local overlap or separated local bursts** over robust monotonic migration.

5.  The results remain compatible with **independent local ruptures** and **repeated shallow local activation**, but catalog statistics alone do not cleanly separate those interpretations.

6.  Sliding-window b-values are valuable for screening broad tendencies, but reliability limits require caution and preclude strong causal interpretation.

7.  Focal mechanisms are presently too sparse and biased in the local system to materially resolve the main question.

Accordingly, the best scientific summary is that the M1–M3 catalog is more consistent with a *temporally phase-separated, locally repeated, and moment-hierarchical activation pattern* than with a simple stationary background or a uniformly distributed swarm-like compound process, while still leaving open whether the dominant larger ruptures should be viewed as partly independent local episodes. Any stronger physical interpretation requires independent constraints beyond catalog statistics.
