---
author:
- TRACE
title: Spatial–Depth Structure, Apparent Migration, and Burst-Centroid Evolution of the M1–M3 Local Earthquake System
---

# Abstract

This report screens the relocated/filtered Aomori active-year catalog for spatial–temporal organization within the M1–M3 local system. The objective was to determine whether the activity is better described as endpoint switching, separated local bursts, corridor-like stepwise activation, spatial–depth coherent activation, diffuse local occupancy, or no organized migration, while explicitly avoiding causal interpretation from catalog organization alone. The implemented workflow recomputed phase-level and burst-level spatial-depth summaries, centroid trajectories, projected-axis diagnostics, depth-domain summaries, migration classifications, and robustness checks using the predefined M1–M3 union, endpoint-core, corridor, and M2-flagging framework. Across the primary M1-related, middle, and pre-M3 phases, the dominant spatial category remained M1-endpoint centered for M3+, M4+, and most M5+ subsets. Machine-readable outputs classify the overall pattern as `mixed_endpoint_centered_overlap`, and the final answer fields explicitly state that systematic phase- or burst-level M1-to-M3 movement is not supported after phase separation. Apparent centroid shifts become most obvious only when the post-M3 interval is included; before M3, centroid changes are modest and remain within an endpoint-centered domain rather than tracing a stable corridor progression. Robustness checks against M2-aware filtering, corridor width, and magnitude threshold preserve the conclusion that endpoint occupancy strongly exceeds corridor-noncore occupancy. The results support follow-up relocation, waveform-similarity, and mechanism comparisons focused on separated endpoint-centered bursts, not a homogeneous migration sequence.

# Scientific objective and decision framework

The task was a catalog-level screening analysis of the M1–M3 local earthquake system in the relocated/filtered Aomori active-year catalog. The explicit scientific goal was to test whether the system is better described as endpoint switching, separated local bursts, corridor-like stepwise activation, spatial-depth coherent activation, diffuse local occupancy, or no organized migration.

A key instruction for this task was that the full M1-to-M3 interval must *not* be treated as a homogeneous migration sequence a priori. Instead, the analysis had to recompute spatial-depth and centroid diagnostics after separating the primary temporal phases already identified by prior event-chain screening: (1) a pre-M1 background baseline, (2) an M1-related dominated phase, (3) an M1–M3 middle phase, (4) a final pre-M3 local activation phase, and (5) post-M3 context kept separate from pre-M3 interpretation. The task also required explicit flagging of M2-related events while avoiding default removal of those events. Finally, the instructions prohibited inferring triggering or physical causality from spatial–temporal organization alone.

The main decision criterion was therefore organizational: whether phase-separated and burst-separated summaries support sustained monotonic progression from M1 toward M3, or instead favor endpoint-centered occupancy, switching, overlap, or diffuse usage of the local system.

# Data, spatial framework, and implementation

## Input data and spatial definitions

The analysis used the relocated/filtered catalog at: <a href="<CASE_ROOT>/data/Snet_catalog_relocate_250601_260501.csv" class="uri"><CASE_ROOT>/data/Snet_catalog_relocate_250601_260501.csv</a>.

The M1–M3 local framework followed the task specification:

- M1–M3 local union: events within 60 km of either M1 or M3.

- Endpoint core zones: events within 30 km of M1 or M3.

- Endpoint extended zones: events within 60 km of M1 or M3.

- M1–M3 corridor: projection between M1 and M3 with perpendicular distance threshold tested at 20 km and 30 km, including endpoint buffers.

- M2-related region: events within 100 km of M2; flagged, not removed by default.

Anchor information recorded in the final screening summary gives M1 at (39.402$`^{\circ}`$N, 143.507$`^{\circ}`$E, 15.9 km, $`M6.9`$), M2 at (40.968$`^{\circ}`$N, 142.288$`^{\circ}`$E, 53.5 km, $`M7.5`$), and M3 at (39.842$`^{\circ}`$N, 143.157$`^{\circ}`$E, 19.4 km, $`M7.7`$). The M1–M3 axis length is 57.16 km.

## Implemented products

The delivered output directory was: <a href="<CASE_ROOT>/run/03_1B_spatial_depth_migration/exp_run/outputs/01_m1_m3_spatial_depth_screening" class="uri"><CASE_ROOT>/run/03_1B_spatial_depth_migration/exp_run/outputs/01_m1_m3_spatial_depth_screening</a>.

Primary machine-readable outputs used in this report include:

- phase summaries: <a href="<CASE_ROOT>/run/03_1B_spatial_depth_migration/exp_run/outputs/01_m1_m3_spatial_depth_screening/phase_spatial_depth_summary_raw.csv" class="uri"><CASE_ROOT>/run/03_1B_spatial_depth_migration/exp_run/outputs/01_m1_m3_spatial_depth_screening/phase_spatial_depth_summary_raw.csv</a> and <a href="<CASE_ROOT>/run/03_1B_spatial_depth_migration/exp_run/outputs/01_m1_m3_spatial_depth_screening/phase_spatial_depth_summary_m2aware.csv" class="uri"><CASE_ROOT>/run/03_1B_spatial_depth_migration/exp_run/outputs/01_m1_m3_spatial_depth_screening/phase_spatial_depth_summary_m2aware.csv</a>

- burst summaries: <a href="<CASE_ROOT>/run/03_1B_spatial_depth_migration/exp_run/outputs/01_m1_m3_spatial_depth_screening/burst_spatial_depth_summary_raw.csv" class="uri"><CASE_ROOT>/run/03_1B_spatial_depth_migration/exp_run/outputs/01_m1_m3_spatial_depth_screening/burst_spatial_depth_summary_raw.csv</a> and <a href="<CASE_ROOT>/run/03_1B_spatial_depth_migration/exp_run/outputs/01_m1_m3_spatial_depth_screening/burst_spatial_depth_summary_m2aware.csv" class="uri"><CASE_ROOT>/run/03_1B_spatial_depth_migration/exp_run/outputs/01_m1_m3_spatial_depth_screening/burst_spatial_depth_summary_m2aware.csv</a>

- centroid evolution and transition metrics: <a href="<CASE_ROOT>/run/03_1B_spatial_depth_migration/exp_run/outputs/01_m1_m3_spatial_depth_screening/centroid_evolution_table.csv" class="uri"><CASE_ROOT>/run/03_1B_spatial_depth_migration/exp_run/outputs/01_m1_m3_spatial_depth_screening/centroid_evolution_table.csv</a> and <a href="<CASE_ROOT>/run/03_1B_spatial_depth_migration/exp_run/outputs/01_m1_m3_spatial_depth_screening/centroid_transition_metrics.csv" class="uri"><CASE_ROOT>/run/03_1B_spatial_depth_migration/exp_run/outputs/01_m1_m3_spatial_depth_screening/centroid_transition_metrics.csv</a>

- migration classifications: <a href="<CASE_ROOT>/run/03_1B_spatial_depth_migration/exp_run/outputs/01_m1_m3_spatial_depth_screening/migration_support_classification.csv" class="uri"><CASE_ROOT>/run/03_1B_spatial_depth_migration/exp_run/outputs/01_m1_m3_spatial_depth_screening/migration_support_classification.csv</a>

- depth-domain summaries: <a href="<CASE_ROOT>/run/03_1B_spatial_depth_migration/exp_run/outputs/01_m1_m3_spatial_depth_screening/depth_domain_by_phase.csv" class="uri"><CASE_ROOT>/run/03_1B_spatial_depth_migration/exp_run/outputs/01_m1_m3_spatial_depth_screening/depth_domain_by_phase.csv</a> and <a href="<CASE_ROOT>/run/03_1B_spatial_depth_migration/exp_run/outputs/01_m1_m3_spatial_depth_screening/depth_domain_by_burst.csv" class="uri"><CASE_ROOT>/run/03_1B_spatial_depth_migration/exp_run/outputs/01_m1_m3_spatial_depth_screening/depth_domain_by_burst.csv</a>

- overall screening outputs: <a href="<CASE_ROOT>/run/03_1B_spatial_depth_migration/exp_run/outputs/01_m1_m3_spatial_depth_screening/final_screening_summary.json" class="uri"><CASE_ROOT>/run/03_1B_spatial_depth_migration/exp_run/outputs/01_m1_m3_spatial_depth_screening/final_screening_summary.json</a> and <a href="<CASE_ROOT>/run/03_1B_spatial_depth_migration/exp_run/outputs/01_m1_m3_spatial_depth_screening/final_answer_fields.json" class="uri"><CASE_ROOT>/run/03_1B_spatial_depth_migration/exp_run/outputs/01_m1_m3_spatial_depth_screening/final_answer_fields.json</a>.

The figure paths used below were verified to exist under the required output directory before report generation.

# Report logic

This report follows the evidence chain requested by the task: objective, implementation, results, robustness, and limitations. Because this is a screening task, the emphasis is on whether the catalog organization supports or rejects specific descriptive classes. Results are reported separately for phase-level summaries, burst-level summaries, centroid-transition diagnostics, and magnitude-threshold behavior. Post-M3 activity is shown for context but is not used to interpret pre-M3 organization.

# Primary screening result

The final machine-readable classification is unambiguous at the overall-system level. The overall pattern is `mixed_endpoint_centered_overlap` in `final_screening_summary.json`, and `final_answer_fields.json` states that systematic phase- or burst-level M1-to-M3 movement after phase separation is `false`. The same output also describes the pre-M3 connection assessment as `separate_endpoint_centered_or_mixed`.

This conclusion is directly supported by three linked output families:

1.  **Phase dominance.** The three primary pre-M3 phases are each classified as M1-endpoint dominated for M3+ in the raw catalog.

2.  **Trend classification.** `migration_support_classification.csv` reports no robust monotonic migration for the full interval or for the separated M1-related, middle, and pre-M3 phases.

3.  **Robustness structure.** Endpoint fractions strongly exceed corridor-noncore fractions across threshold and corridor-width tests.

Thus, the preferred interpretation is not continuous corridor activation from M1 to M3, but rather a mixed system composed mainly of endpoint-centered occupancy with temporal overlap and separate bursts.

# Phase-level spatial-depth results

## Primary phases at M3+

Table <a href="#tab:primaryphases" data-reference-type="ref" data-reference="tab:primaryphases">1</a> summarizes the three primary pre-M3 phases using the raw M3+ phase summary output.

<div id="tab:primaryphases">

| Phase | Count | Max $`M`$ | Med. depth | Med. proj. | Dist. to M1 | Dist. to M3 |
|:---|:---|:---|:---|:---|:---|:---|
| M1-related primary |  |  |  |  |  |  |
| Middle phase primary |  |  |  |  |  |  |
| Pre-M3 primary |  |  |  |  |  |  |

Primary pre-M3 phase summaries for the raw M3+ catalog, extracted from `phase_spatial_depth_summary_raw.csv`. Distances are in kilometers.

</div>

All three primary pre-M3 phases remain closer in centroid location to M1 than to M3. Their dominant spatial category is M1 endpoint, not corridor and not M3 endpoint. The M1-related phase is the clearest example: 79.4% of M3+ events fall in the M1 endpoint and only 13.4% in the M3 endpoint, with just 0.9% in the corridor-noncore class. The middle phase shifts somewhat toward the center, but still remains M1-endpoint dominated (66.7% M1 endpoint, 16.0% M3 endpoint, 0% corridor-noncore). The pre-M3 primary window also stays M1-endpoint dominated (82.4% M1 endpoint, 13.7% M3 endpoint, 2.0% corridor-noncore).

This phase separation is central to the interpretation. If the system were a stable M1-to-M3 migration sequence, one would expect a later-phase drift into corridor or M3-dominant classes before M3. That pattern is not present in the primary phase summaries.

## Baseline and post-M3 context

The conservative pre-M1 baseline (catalog start to M1$`-`$<!-- -->14 d) contains 20 M3+ events, no M4+ or M5+ events, median depth 14.19 km, and an M1-endpoint dominant label, but with a larger off-corridor fraction (35%) than the main phases. The M1$`-`$<!-- -->7 d sensitivity baseline is similar but slightly more diffuse. These baseline properties support the prior working context that modest local pre-existing M3-class activity existed before M1, but they do not resemble a preassembled M1-to-M3 corridor.

By contrast, the post-M3 windows shift clearly toward M3. The post-M3 7 d M3+ centroid has projected distance 37.64 km and is classified as M3 endpoint, while the post-M3 14 d window is mixed M3-endpoint/off-corridor. This matters because the strongest centroid jump toward M3 occurs only when M3 and its aftermath are included, not during the separated pre-M3 sequence. In other words, the catalog supports a sharp re-centering around M3 at and after M3, not a robust monotonic approach to M3 beforehand.

## Magnitude-threshold behavior

The full catalog-level threshold comparison from `final_answer_fields.json` shows similar depth structure across M3+, M4+, and M5+:

- M3+: 736 events, median depth 13.48 km, 97.3% within 0 - -30 km depth domain.

- M4+: 158 events, median depth 13.71 km, 96.2% within 0 - -30 km.

- M5+: 50 events, median depth 13.77 km, 94.0% within 0 - -30 km.

The phase summaries reinforce this consistency. For the full M1-to-M3 interval, M4+ and M5+ remain M1-endpoint dominated, with zero corridor-noncore fraction in the raw summaries. In the pre-M3 primary window, M4+ is strongly M1 endpoint (92.9% M1 endpoint), while pre-M3 M5+ contains only three events and is therefore too sparse for strong migration interpretation. The reported evaluation metadata specifically warns that the only subset labeled robust monotonic migration elsewhere in the outputs is the raw pre-M3 M4+ subset with 14 events, and that this limited sample should not be generalized to the full system.

# Burst-level results

## Major burst organization

Burst summaries indicate that the main bursts are not arranged as a clean M1-to-M3 stepping sequence. Instead, they are dominated by a large M1-centered burst before and during the M1-related phase, followed by smaller central-to-mixed bursts, another strong M1-centered burst in the final pre-M3 interval, and finally an M3-centered/post-M3 burst.

The most important bursts from `burst_spatial_depth_summary_raw.csv` are:

- **B09** (2025-10-30 to 2025-12-21 source burst window): 367 M3+, 88 M4+, 30 M5+, dominant category M1 endpoint, centroid only 12.58 km from M1 and 45.03 km from M3.

- **B12** (2026-01-28 to 2026-02-16): 12 M3+, 3 M4+, dominant category mixed M1 endpoint/M3 endpoint, representing one of the few bursts with noticeably split endpoint occupancy.

- **B14** (2026-03-01 to 2026-04-11): 67 M3+, 18 M4+, 5 M5+, dominant category M1 endpoint, centroid 16.01 km from M1 and 42.25 km from M3.

- **B15** (2026-04-15 to 2026-05-01): 258 M3+, 44 M4+, 13 M5+, mixed M3 endpoint/off-corridor after M3, centroid 12.33 km from M3.

The structure of these bursts directly argues against homogeneous migration. B09 and B14, the two largest pre-M3 bursts, are both M1-endpoint dominated despite occurring months apart and despite the later one sitting immediately before M3. A true stepwise corridor activation model would predict later bursts progressively occupying corridor or M3-near positions before M3; instead, the catalog repeatedly reoccupies the M1-side domain.

## Burst categories and ambiguity

Smaller bursts before M1 are spatially mixed, with some off-corridor or low-count M3-endpoint examples, but these are weak and intermittent. The main pre-M3 burst chain remains dominated by low-count or moderate-count M1-endpoint classes, with only B12 classified as mixed between M1 and M3 endpoints. Even B12 is not corridor-dominated. The absence of corridor-noncore dominance in the major bursts is one of the strongest arguments against corridor-like stepwise activation.

# Centroid evolution and apparent movement

## Phase transitions

Centroid transition metrics quantify how much centroids move between successive windows. For the key pre-M3 raw phase transitions:

- full M1-to-M3 $`\rightarrow`$ middle phase: centroid move 12.35 km, projected-axis change +4.42 km

- middle phase $`\rightarrow`$ pre-M3 sensitivity 42 d: centroid move 13.39 km, projected-axis change $`-`$<!-- -->3.93 km

- pre-M3 sensitivity 42 d $`\rightarrow`$ pre-M3 primary: centroid move only 0.11 km

- pre-M3 sensitivity 28 d $`\rightarrow`$ post-M3 14 d: centroid move 29.90 km, projected-axis change +26.34 km

These numbers show that the largest coherent shift toward the M3 side occurs at the transition into the post-M3 interval, not during the separated pre-M3 evolution. Pre-M3 changes are modest and partly reversible, not steadily monotonic along the axis. The middle phase moves somewhat farther from M1 than the M1-related phase, but the subsequent pre-M3 primary window shifts back toward M1 rather than continuing to M3.

## Burst transitions

Burst-to-burst centroid transitions tell the same story. In the main late sequence:

- B11 $`\rightarrow`$ B12: +12.90 km projected change

- B12 $`\rightarrow`$ B13: $`-`$<!-- -->52.15 km

- B13 $`\rightarrow`$ B14: +36.77 km

- B14 $`\rightarrow`$ B15: +27.47 km

This alternation is not a monotonic migration signature. It is more consistent with spatial jumping among local subclusters, repeated occupancy of the M1-side domain, and eventual M3 re-centering only with the M3 sequence itself. The final screening outputs therefore interpret centroid evolution as mixed endpoint-centered overlap rather than directional propagation.

<figure id="fig:trajectory" data-latex-placement="H">
<img src="<CASE_ROOT>/run/03_1B_spatial_depth_migration/exp_run/outputs/01_m1_m3_spatial_depth_screening/fig_phase_centroid_trajectory.png" style="width:90.0%" />
<figcaption>Phase centroid trajectory through time. The main interpretive point is that pre-M3 centroids remain within an endpoint-centered domain and do not trace a stable monotonic path from M1 to M3.</figcaption>
</figure>

<figure id="fig:map" data-latex-placement="H">
<img src="<CASE_ROOT>/run/03_1B_spatial_depth_migration/exp_run/outputs/01_m1_m3_spatial_depth_screening/fig_phase_burst_centroid_map.png" style="width:90.0%" />
<figcaption>Map of phase and burst centroids within the M1–M3 framework. The major pre-M3 centroids cluster on the M1 side, while the most evident shift toward M3 occurs with the M3/post-M3 sequence.</figcaption>
</figure>

# Projected-distance and corridor diagnostics

The corridor hypothesis was tested directly using projected-axis and corridor-noncore occupancy summaries. The machine-readable migration classification file reports:

> `mixed_endpoint_centered_overlap`: “Primary phase dominant categories: M1-related=M1_endpoint, middle=M1_endpoint, pre-M3=M1_endpoint.”

This is reinforced by `robustness_summary.csv`. For the full catalog:

- Raw M3+, corridor width 20 km: endpoint fraction 0.848, corridor-noncore fraction 0.0068.

- Raw M3+, corridor width 30 km: endpoint fraction 0.848, corridor-noncore fraction 0.0122.

- Raw M4+, both corridor widths: endpoint fraction 0.854, corridor-noncore fraction 0.0.

- Raw M5+, both corridor widths: endpoint fraction 0.860, corridor-noncore fraction 0.0.

Thus, widening the corridor from 20 km to 30 km does not reveal hidden corridor dominance. Endpoint occupancy exceeds corridor-noncore occupancy by roughly 0.84–0.87 across all tested thresholds and M2 treatments. This is a decisive screening result against the corridor-like stepwise activation model.

<figure id="fig:projtime" data-latex-placement="H">
<img src="<CASE_ROOT>/run/03_1B_spatial_depth_migration/exp_run/outputs/01_m1_m3_spatial_depth_screening/fig_projected_distance_time.png" style="width:90.0%" />
<figcaption>Projected distance versus time. Any impression of long-interval migration weakens after phase separation; the figure is more consistent with repeated endpoint occupancy plus a sharp post-M3 shift than with a single smooth migration track.</figcaption>
</figure>

<figure id="fig:composition" data-latex-placement="H">
<img src="<CASE_ROOT>/run/03_1B_spatial_depth_migration/exp_run/outputs/01_m1_m3_spatial_depth_screening/fig_spatial_composition_by_phase.png" style="width:90.0%" />
<figcaption>Spatial composition by phase. Endpoint fractions dominate the principal windows, while corridor-noncore fractions remain minor.</figcaption>
</figure>

# Depth structure and structural domain

Depth behavior is comparatively coherent even though along-axis migration is not. Most activity across thresholds occupies a shallow-to-mid crustal depth band centered near 13–14 km. The primary phase summaries show:

- M1-related primary M3+: median depth 12.89 km, range 3.82–31.31 km

- Middle phase primary M3+: median depth 14.17 km, range 5.94–36.31 km

- Pre-M3 primary M3+: median depth 14.12 km, range 3.09–25.82 km

The full-threshold comparison shows median depths of 13.48 km, 13.71 km, and 13.77 km for M3+, M4+, and M5+, respectively. More than 94% of events at all three thresholds lie in the 0 - -30 km depth class. This indicates a relatively stable depth domain despite temporal reorganization in plan view.

Therefore, the system is not spatially diffuse in depth even though it is not well described by corridor migration. A more accurate description is endpoint-centered plan-view organization within a fairly consistent depth band.

<figure id="fig:depthproj" data-latex-placement="H">
<img src="<CASE_ROOT>/run/03_1B_spatial_depth_migration/exp_run/outputs/01_m1_m3_spatial_depth_screening/fig_depth_vs_projected_distance.png" style="width:90.0%" />
<figcaption>Depth versus projected distance. The figure supports a comparatively stable depth domain despite mixed along-axis occupancy.</figcaption>
</figure>

# Effect of M2-aware filtering

The requested workflow treated M2-aware processing as a robustness test, not the default basis for interpretation. The final answer fields record the M2-aware change summary as `different`, meaning some numerical details changed. However, the core interpretation did not.

In the robustness summary, endpoint fractions increase slightly after M2-aware filtering: for example, M3+ endpoint fraction rises from 0.848 to 0.874 at 20 km corridor width. The phase-transition metrics also become somewhat smaller in the M2-aware case, but the pre-M3 windows remain M1-endpoint classified. The task context explicitly states that M2-aware flagging has modest overall influence and does not remove the main M1-related, middle-phase, or pre-M3 conclusions. The direct outputs inspected here are consistent with that statement.

<figure id="fig:m2aware" data-latex-placement="H">
<img src="<CASE_ROOT>/run/03_1B_spatial_depth_migration/exp_run/outputs/01_m1_m3_spatial_depth_screening/fig_raw_vs_m2aware_comparison.png" style="width:90.0%" />
<figcaption>Comparison of raw and M2-aware results. Numerical differences are present, but the overall screening outcome remains endpoint-centered rather than corridor-dominated.</figcaption>
</figure>

# Synthesis by candidate descriptive model

Using the requested decision classes, the evidence supports the following ranking.

## Best-supported description: mixed endpoint-centered overlap

This is the formal output classification and the best summary of the evidence. It captures repeated M1-side occupancy during both the M1-related and pre-M3 phases, mixed or ambiguous intermediate bursts, and eventual M3 concentration only with the M3/post-M3 sequence.

## Plausible secondary description: separated local bursts / endpoint switching

Burst-level behavior shows discrete clusters and some temporal jumps, especially among low-count bursts and the B12 mixed burst. If a shorter label is required, “separated local bursts with endpoint-centered occupancy” is faithful to the outputs.

## Not supported as primary description: corridor-like stepwise activation

Corridor-noncore fractions are tiny across all robustness tests, and primary phases are not corridor-dominant. This model is disfavored.

## Not supported as primary description: homogeneous migration sequence

Both the classification file and the final answer fields reject systematic M1-to-M3 movement after phase separation. Apparent long-interval drift arises mainly when phases are merged or when post-M3 activity is included.

## Only weakly supported: diffuse local occupancy

Off-corridor activity exists, especially in some baseline and post-M3 windows, but the main pre-M3 phases are strongly endpoint centered rather than diffuse.

# Working-context consistency and contradictions

The compact context asked that prior event-chain findings be treated as working guidance, not copied conclusions. The final screening summary explicitly checked several working-context statements and marked them `consistent`. In particular:

- endpoint-core dominance in the main windows is consistent with the recomputed M3+ composition fractions;

- the full interval not being a homogeneous migration sequence is consistent with the trend classes showing no robust monotonic migration in the full and separated windows;

- the pre-M3 activation phase is confirmed by 51 M3+ events in the primary pre-M3 window.

No contradiction requiring reversal of the working context was found in the inspected outputs. The recomputed evidence strengthens, rather than weakens, the earlier screening interpretation that endpoint-centered behavior is favored over continuous migration.

# Follow-up implications

The final answer fields list follow-up targets that are scientifically appropriate for this screening result:

- relocation refinement for endpoint-centered bursts;

- waveform similarity analysis within dominant bursts;

- mechanism comparison for M4+ follow-up candidates;

- stress or Coulomb modeling only after careful catalog-screening review;

- b-value and moment-release comparisons by separated phase.

These recommendations are well aligned with the present findings. Because the catalog suggests repeated occupancy of endpoint-centered subdomains rather than simple migration, higher-resolution follow-up should focus on whether the apparent endpoint clusters resolve into tighter repeating families, distinct structural patches, or mixed populations with different mechanisms.

# Limitations

Several limitations materially affect interpretation.

1.  **Catalog-level scope only.** Spatial–temporal organization alone is not evidence for triggering, stress transfer, fluids, slow slip, or any other physical causal mechanism. This report therefore makes no causal claims.

2.  **Sample-size limits for large-event subsets.** The evaluation metadata notes that the only subset reported elsewhere as robust monotonic migration is the raw pre-M3 M4+ set with 14 events; pre-M3 M5+ has only 3 events. These are too sparse to generalize to the entire M1–M3 system.

3.  **Centroid aggregation can mix subclusters.** Burst identification is rate-based and centroid motion is calculated from aggregated windows. Apparent centroid movement may therefore reflect changing mixture weights among local subclusters rather than literal propagating rupture or triggering fronts.

4.  **Partial handoff embedding.** The handoff metadata includes an `outputs_truncated` quality flag. In this report, major claims were tied directly to inspected primary outputs and verified figures to reduce that limitation.

5.  **No relocation-quality or waveform validation in this task.** The screening is adequate for organizational classification, but not for finer structural linkage or physical interpretation.

Overall scientific confidence is therefore best described as *moderate*, matching the evaluation summary.

<figure id="fig:matrix" data-latex-placement="H">
<img src="<CASE_ROOT>/run/03_1B_spatial_depth_migration/exp_run/outputs/01_m1_m3_spatial_depth_screening/fig_spatial_depth_evidence_matrix.png" style="width:95.0%" />
<figcaption>Integrated spatial-depth evidence matrix summarizing the screening outcome.</figcaption>
</figure>

# Conclusion

Recomputed spatial-depth, phase, burst, centroid, and robustness diagnostics from the relocated/filtered Aomori catalog do *not* support interpreting the M1–M3 local earthquake system as a homogeneous M1-to-M3 migration sequence. After phase separation, the principal pre-M3 windows remain M1-endpoint dominated, the major pre-M3 bursts are again centered near the M1 side, corridor-noncore occupancy stays minimal, and the strongest movement toward M3 appears only with the M3/post-M3 sequence itself. The formal machine-readable classification, `mixed_endpoint_centered_overlap`, is therefore an accurate synthesis of the delivered evidence.

In practical terms, the M1–M3 system is best described as a set of separated or overlapping local bursts with strong endpoint-centered occupancy within a relatively consistent depth band near 13 - -14 km. This is a robust catalog-level organizational result, but it is not by itself evidence of triggering or any particular physical mechanism.
