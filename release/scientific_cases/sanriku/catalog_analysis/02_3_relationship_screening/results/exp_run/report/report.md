---
author:
- TRACE
date: 2026-05-24
title: Catalog-Level Relationship Analysis of the Aomori M1, M2, and M3 Earthquake Clusters
---

# Abstract

This report evaluates whether the M1, M2, and M3 earthquake clusters in the Aomori catalog show catalog-level relationships that merit deeper scientific follow-up. The objective is not to prove triggering or any physical mechanism from the catalog alone, but to identify which relationship hypotheses are supported, which are weakened after controls and distance-aware screening, and which should be prioritized for waveform, relocation, focal-mechanism, geodetic, ocean-bottom pressure, or stress-modeling studies. The synthesis uses validated outputs from a prior quantitative relationship-analysis workflow that treated the three pairs symmetrically and separated raw catalog evidence, control-corrected evidence, and distance-aware plausibility. The strongest system-wide result is that the three clusters are better viewed as components of a broader regional activation episode than as a set of uniformly direct pairwise links. Within that broader picture, M1–M3 is the highest-priority pair for deeper physical analysis because it is the only pair that remains geometrically plausible for nearby source-region linkage while retaining moderate-to-strong support for several relationship-aware hypotheses after controls. In contrast, M1–M2 shows strong raw and control-surviving corridor and between-event signals, but these do not remain distance-plausible as a simple local pair linkage. M2–M3 is best treated as predominantly independent local clusters embedded within the same broader regional episode, with substantial competition from background-rate and window-sensitivity explanations. These conclusions remain explicitly catalog-level and should be interpreted as prioritization guidance rather than causal inference.

# Scientific Objective and Scope

The scientific objective was to determine whether the Aomori M1, M2, and M3 earthquake clusters show meaningful catalog-level relationships worth further investigation, and to identify which relationship hypotheses should be prioritized for deeper physical analysis. The request specifically required that M1–M2, M1–M3, and M2–M3 be evaluated symmetrically at first, using comparable metrics, and that raw catalog signals be kept distinct from control-corrected signals and distance-aware plausibility screening.

The candidate hypotheses included independent local clusters, overlapping activation zones, delayed activation between clusters, linked local fault-system activation, corridor-like migration or expansion, broader regional activation, compound or swarm-like multi-event clustering, and apparent relationships caused by burst-like background seismicity or analysis-window choices. These were treated as catalog-level hypotheses only. No result in this report is presented as proof of triggering, rupture interaction, stress transfer, fluid migration, or any other physical mechanism.

# Data Basis and Workflow Implementation

This report is a synthesis of previously validated workflow outputs and does not recompute the core metrics. The primary evidence package is the relationship-analysis workflow in: <a href="<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/01_relationship_analysis" class="uri"><CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/01_relationship_analysis</a> with synthesis products in: <a href="<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/02_report_synthesis" class="uri"><CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/02_report_synthesis</a>.

The upstream analysis built a unified catalog-level relationship dataset, computed symmetric pairwise geometry and timing metrics, evaluated ambiguity-aware event assignment, tested corridor and pseudo-corridor controls, and summarized hypothesis support across raw, corrected, and distance-aware layers. The synthesis stage then consolidated those outputs into concise tables and diagnostic figures without recomputation.

Catalog-scale quality-control values from the validated upstream output `catalog_qc_summary.csv` are:

- 22,096 relocated catalog events,

- catalog span from 2025-09-30 to 2026-05-01,

- 259 events of magnitude M4+,

- 68 events of magnitude M5+,

- 3 mainshocks,

- 354 focal-mechanism rows with 240 conservative mechanism matches,

- 371 station rows in the contextual station file.

The most important synthesis files used here are:

- pairwise quantitative summary: <a href="<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/02_report_synthesis/pairwise_scientific_summary.csv" class="uri"><CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/02_report_synthesis/pairwise_scientific_summary.csv</a>

- raw / corrected / distance-aware summary: <a href="<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/02_report_synthesis/raw_corrected_distance_summary.csv" class="uri"><CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/02_report_synthesis/raw_corrected_distance_summary.csv</a>

- concise relationship evidence matrix: <a href="<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/02_report_synthesis/relationship_evidence_matrix_concise.csv" class="uri"><CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/02_report_synthesis/relationship_evidence_matrix_concise.csv</a>

- concise follow-up priorities: <a href="<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/02_report_synthesis/followup_priorities_concise.csv" class="uri"><CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/02_report_synthesis/followup_priorities_concise.csv</a>

- strongest supported signals: <a href="<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/02_report_synthesis/strongest_supported_signals.csv" class="uri"><CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/02_report_synthesis/strongest_supported_signals.csv</a>

- weak, negative, and unresolved signals: <a href="<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/02_report_synthesis/weak_negative_unresolved_signals.csv" class="uri"><CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/02_report_synthesis/weak_negative_unresolved_signals.csv</a>

# High-Value Diagnostic Figures

Figure <a href="#fig:overview" data-reference-type="ref" data-reference="fig:overview">1</a> provides the pairwise spatial overview. Figure <a href="#fig:timeproj" data-reference-type="ref" data-reference="fig:timeproj">2</a> shows the time-projection relationships used to distinguish corridor-aligned and endpoint-centered behavior. Figure <a href="#fig:corridor" data-reference-type="ref" data-reference="fig:corridor">3</a> compares observed corridor occupancy against pseudo-corridor expectations. Figure <a href="#fig:chains" data-reference-type="ref" data-reference="fig:chains">4</a> summarizes intervening-event chains. Figure <a href="#fig:matrix" data-reference-type="ref" data-reference="fig:matrix">5</a> presents the cross-pair evidence matrix, and Figure <a href="#fig:priority" data-reference-type="ref" data-reference="fig:priority">6</a> summarizes follow-up priorities.

<figure id="fig:overview" data-latex-placement="H">
<img src="<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/02_report_synthesis/fig_pairwise_overview_map.png" style="width:90.0%" />
<figcaption>Pairwise spatial overview of the M1, M2, and M3 relationship geometry.</figcaption>
</figure>

<figure id="fig:timeproj" data-latex-placement="H">
<img src="<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/02_report_synthesis/fig_pairwise_time_projection.png" style="width:90.0%" />
<figcaption>Pairwise time-projection diagnostic used to assess endpoint-centered, delayed, and corridor-aligned activity.</figcaption>
</figure>

<figure id="fig:corridor" data-latex-placement="H">
<img src="<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/02_report_synthesis/fig_corridor_vs_control.png" style="width:90.0%" />
<figcaption>Observed corridor occupancy versus pseudo-corridor control expectations.</figcaption>
</figure>

<figure id="fig:chains" data-latex-placement="H">
<img src="<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/02_report_synthesis/fig_intervening_event_chains.png" style="width:90.0%" />
<figcaption>Intervening-event chain comparison across the three mainshock pairs.</figcaption>
</figure>

<figure id="fig:matrix" data-latex-placement="H">
<img src="<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/02_report_synthesis/fig_relationship_evidence_matrix.png" style="width:90.0%" />
<figcaption>Relationship evidence matrix summarizing raw, corrected, and distance-aware support across pairs and hypotheses.</figcaption>
</figure>

<figure id="fig:priority" data-latex-placement="H">
<img src="<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/02_report_synthesis/fig_followup_priority.png" style="width:90.0%" />
<figcaption>Ranked follow-up priorities derived from the catalog-level relationship synthesis.</figcaption>
</figure>

# Pairwise Quantitative Summary

Table <a href="#tab:pairwise" data-reference-type="ref" data-reference="tab:pairwise">1</a> summarizes the principal pairwise metrics carried into the scientific interpretation. These values directly support the distinction between strong raw signal, control survival, and distance-aware plausibility.

<div id="tab:pairwise">

| Pair | Sep. (km) | $`\Delta z`$ (km) | $`\Delta t`$ (days) | M4+ between | M4+ corridor frac. | Raw | Control | Distance |
|:---|---:|---:|---:|---:|---:|:---|:---|:---|
| M1–M2 | 202.6 | 37.6 | 29.3 | 68 | 0.513 | high | survives_controls | not_local_linkage_plausible |
| M1–M3 | 57.4 | 3.5 | 162.0 | 188 | 0.358 | high | partly_weakened | nearby_plausible |
| M2–M3 | 145.2 | -34.1 | 132.7 | 121 | 0.105 | high | partly_weakened | not_local_linkage_plausible |

Pairwise relationship summary from validated synthesis outputs.

</div>

A key point from Table <a href="#tab:pairwise" data-reference-type="ref" data-reference="tab:pairwise">1</a> is that all three pairs exhibit high raw signal levels, so raw activity alone is not discriminating. The discrimination emerges only after control correction and geometric plausibility screening. M1–M3 is the only pair that remains compatible with a nearby source-region interpretation, with pair separation 57.4 km, depth difference 3.5 km, and a nonzero distance-link score of 0.681. By contrast, M1–M2 has a distance-link score of 0.000 and M2–M3 only 0.193, despite elevated raw activity metrics.

# Pair-by-Pair Scientific Interpretation

## M1–M2: strong catalog linkage signal, but not a plausible simple local pair linkage

M1–M2 shows one of the strongest raw catalog relationship signatures in the dataset. The pair has 68 M4+ events between the mainshocks, an M4+ corridor fraction of 0.513, an M4+ between-count control percentile of 0.842, and a pseudo-corridor percentile of 0.925. These values indicate that the observed concentration of moderate events in the pair corridor is stronger than expected from geometry alone. Figure <a href="#fig:corridor" data-reference-type="ref" data-reference="fig:corridor">3</a> supports this by showing a large excess over pseudo-corridor expectation.

However, the pair is separated by 202.6 km with a depth difference of 37.6 km and receives a distance-link score of 0.000. The distance-aware screening therefore rejects a simple local-linkage interpretation even though the raw and corrected catalog metrics are strong. This is the clearest example in the dataset of why corridor and between-event counts must be interpreted through a distance-aware plausibility layer rather than in isolation.

The concise evidence matrix indicates the following for M1–M2:

- corridor-like migration or expansion: raw **strong**, corrected **strong**, distance-aware **low**;

- linked local fault-system activation: raw **moderate**, corrected **moderate**, distance-aware **low**;

- broader regional activation: raw **strong**, corrected **strong**, distance-aware **strong**;

- common regional rate pulse without pair-specific linkage: raw **moderate**, corrected **moderate**, distance-aware **strong**;

- overlapping activation zones and delayed activation: **low** across all three evidence layers.

The corrected interpretation is therefore not “direct local coupling,” but rather a broader regional episode or common regional rate pulse that happens to produce a strong catalog corridor signal between distant source regions. The evidence also argues against forcing M1–M2 into overlap, delayed local activation, or compound swarm-like interpretations. In this report’s prioritization, M1–M2 deserves follow-up mainly for regional-scale processes, not as the strongest target for local pairwise triggering analysis.

## M1–M3: highest-priority pair for deeper physical testing

M1–M3 is the strongest positive result of the synthesis. It is the only pair that remains distance-plausible for nearby source-region linkage while also retaining moderate-to-strong support across multiple relationship-aware hypotheses after control correction. Quantitatively, the pair has separation 57.4 km, depth difference 3.5 km, time separation 162.0 days, distance-link score 0.681, 188 M4+ events between the mainshocks, M4+ corridor fraction 0.358, and pseudo-corridor percentile 0.975. Although the control screen is labeled `partly_weakened`, the pair still survives as the best local-linkage candidate once geometry is considered.

The concise evidence matrix shows:

- overlapping activation zones: raw **strong**, corrected **moderate**, distance-aware **moderate**;

- delayed activation between clusters: raw **strong**, corrected **moderate**, distance-aware **possible**;

- linked local fault-system activation: raw **strong**, corrected **strong**, distance-aware **moderate**;

- corridor-like migration or expansion: raw **strong**, corrected **strong**, distance-aware **moderate**;

- broader regional activation: raw **strong**, corrected **strong**, distance-aware **moderate**.

These results imply that M1–M3 should not be reduced to a single simple story. The catalog supports several viable interpretations that remain active competitors after controls: overlap, linked local fault-system activation, corridor-aligned activation, delayed or episodic activation, and broader regional activation. Figure <a href="#fig:timeproj" data-reference-type="ref" data-reference="fig:timeproj">2</a> is particularly important for this pair because it indicates episodic endpoint-centered and corridor-aligned activity rather than clean continuous migration. That pattern supports formulations such as delayed or stepwise activation more strongly than a simple propagating front.

At the same time, ambiguity is substantial. The M4+ ambiguous fraction is 0.514, indicating that many moderate events can plausibly be considered shared or unresolved in a pairwise framework. This ambiguity is scientifically useful rather than problematic: it is exactly what motivates higher-resolution follow-up with relocation, waveform similarity, mechanism comparison, and stress or fluid-sensitive contextual datasets. M1–M3 is therefore the highest-priority pair for physical verification studies.

## M2–M3: best treated as independent local clusters within a broader regional episode

M2–M3 also shows high raw activity, but the relationship weakens substantially once control and geometry screens are considered. The pair has separation 145.2 km, depth difference $`-34.1`$ km, time separation 132.7 days, distance-link score 0.193, 121 M4+ between events, and a low M4+ corridor fraction of 0.105. Its pseudo-corridor percentile is only 0.558, showing little corridor excess above geometric expectation relative to the other pairs. Figure <a href="#fig:corridor" data-reference-type="ref" data-reference="fig:corridor">3</a> supports that weak local-corridor reading.

The evidence matrix indicates:

- independent local clusters: raw **strong**, corrected **strong**, distance-aware **strong**;

- broader regional activation: raw **strong**, corrected **moderate**, distance-aware **strong**;

- common regional rate pulse without pair-specific linkage: raw **strong**, corrected **moderate**, distance-aware **strong**;

- overlapping activation zones, delayed activation, and linked local fault-system activation: **low** after correction and **low** in distance-aware plausibility;

- apparent relationship from burst-like background or window choices: raw **moderate**, corrected **moderate**, distance-aware **strong**.

This combination of evidence favors a cautious interpretation: M2–M3 is best represented as predominantly independent local clusters embedded within the same regional activation episode. The local-overlap, delayed-linkage, and local-fault-connection hypotheses are not well supported. In contrast, independent-cluster, regional-activation, common-rate-pulse, and background-window-sensitivity explanations remain credible and should be carried forward together. The time-projection diagnostic in Figure <a href="#fig:timeproj" data-reference-type="ref" data-reference="fig:timeproj">2</a> further supports endpoint-centered reactivation rather than a clean inter-cluster migration path.

# Relationship Evidence Matrix and Hypothesis Prioritization

Table <a href="#tab:matrix" data-reference-type="ref" data-reference="tab:matrix">[tab:matrix]</a> condenses the hypothesis evidence levels requested by the user. Evidence levels are reported separately for each pair-hypothesis combination as raw catalog evidence, control-corrected evidence, and distance-aware plausibility. The scientific ranking should follow the corrected and distance-aware interpretation rather than the raw layer alone.

<div class="landscape">

<div class="tabularx">

l l Y Y Y l Pair & Hypothesis & Raw catalog evidence & Control-corrected evidence & Distance-aware plausibility & Follow-up priority  
M1–M2 & Independent local clusters & moderate & possible & strong & medium  
M1–M2 & Overlapping activation zones & low & low & low & low  
M1–M2 & Delayed activation between clusters & low & low & low & low  
M1–M2 & Linked local fault-system activation & moderate & moderate & low & medium  
M1–M2 & Corridor-like migration or expansion & strong & strong & low & low  
M1–M2 & Broader regional activation & strong & strong & strong & high  
M1–M2 & Compound/swarm-like multi-event clustering & low & low & low & low  
M1–M2 & Apparent relationship from background or window choices & low & low & strong & low  
M1–M2 & Common regional rate pulse without pair-specific linkage & moderate & moderate & strong & high  
M1–M3 & Independent local clusters & moderate & low & moderate & medium  
M1–M3 & Overlapping activation zones & strong & moderate & moderate & high  
M1–M3 & Delayed activation between clusters & strong & moderate & possible & medium  
M1–M3 & Linked local fault-system activation & strong & strong & moderate & high  
M1–M3 & Corridor-like migration or expansion & strong & strong & moderate & high  
M1–M3 & Broader regional activation & strong & strong & moderate & high  
M1–M3 & Compound/swarm-like multi-event clustering & possible & possible & possible & medium  
M1–M3 & Apparent relationship from background or window choices & low & low & moderate & medium  
M1–M3 & Common regional rate pulse without pair-specific linkage & moderate & possible & moderate & medium  
M2–M3 & Independent local clusters & strong & strong & strong & high  
M2–M3 & Overlapping activation zones & low & low & low & low  
M2–M3 & Delayed activation between clusters & low & low & low & low  
M2–M3 & Linked local fault-system activation & possible & low & low & low  
M2–M3 & Corridor-like migration or expansion & possible & possible & low & medium  
M2–M3 & Broader regional activation & strong & moderate & strong & high  
M2–M3 & Compound/swarm-like multi-event clustering & low & low & low & low  
M2–M3 & Apparent relationship from background or window choices & moderate & moderate & strong & high  
M2–M3 & Common regional rate pulse without pair-specific linkage & strong & moderate & strong & high  

</div>

</div>

Several conclusions follow directly from Table <a href="#tab:matrix" data-reference-type="ref" data-reference="tab:matrix">[tab:matrix]</a> and Figure <a href="#fig:matrix" data-reference-type="ref" data-reference="fig:matrix">5</a>:

1.  No single relationship model explains all three pairs.

2.  Broader regional activation is the most robust cross-pair hypothesis.

3.  M1–M3 is the only pair that remains a credible candidate for local linkage-style follow-up after both controls and distance-aware screening.

4.  M1–M2 demonstrates that strong corridor signals do not automatically imply local migration or direct pair coupling.

5.  M2–M3 should be prioritized more for testing independent-cluster, regional-rate, and artifact or window-sensitivity explanations than for local linkage.

# Strongest Supported Signals

The strongest supported catalog-level signals from the synthesis are:

- **Broader regional activation across the three-cluster system.** This hypothesis is strong or near-strong across all pairs and remains the most robust system-wide interpretation after synthesis.

- **M1–M3 as the highest-priority local relationship candidate.** This pair uniquely combines nearby-plausible geometry with persistent moderate-to-strong support for overlap, linked local fault-system activation, corridor-aligned activation, and delayed or episodic activation.

- **M1–M2 as a strong regional-scale relationship signal rather than a local one.** The corridor signal is real relative to controls, but the geometry argues strongly against simple local linkage.

- **M2–M3 as independent local clusters within the same broader episode.** This interpretation is supported more consistently than any local-linkage hypothesis for that pair.

The intervening-event chain diagnostic in Figure <a href="#fig:chains" data-reference-type="ref" data-reference="fig:chains">4</a> is consistent with the broader regional activation picture. All three pairs show many M4+ intervening events, but far fewer M6+ bridges, suggesting moderate-event continuity across the catalog without a comparably strong large-event bridge pattern.

# Weak, Negative, and Unresolved Evidence

A major strength of the workflow is that it preserved contradictory and unresolved signals instead of forcing all patterns into positive linkage narratives. The following findings are particularly important:

- M1–M2 overlap, delayed activation, and compound or swarm-like clustering are all low across raw, corrected, and distance-aware layers.

- M2–M3 overlap and delayed activation are also low across all layers.

- M2–M3 linked local fault-system activation drops from possible in the raw layer to low after correction and remains low in distance-aware plausibility.

- M2–M3 retains moderate support for background-rate or window-choice explanations, and those explanations become strong in distance-aware plausibility.

- M1–M3 remains the most promising pair, but even there the control screen is not fully unambiguous; it is partly weakened rather than universally decisive.

These weak and unresolved results matter scientifically because they prevent overinterpretation. They show that the pairwise relationships are heterogeneous and that the most credible next step is targeted physical testing of a few specific hypotheses rather than adoption of a single causal story.

# Recommended Follow-Up Research Directions

Figure <a href="#fig:priority" data-reference-type="ref" data-reference="fig:priority">6</a> and the concise follow-up table indicate that the next physical analyses should be prioritized as follows:

## High priority

- **M1–M3 corridor-like migration or expansion:** waveform migration tests, relocation, and along-strike stress or fluid indicators.

- **M1–M3 linked local fault-system activation:** high-precision relocation, focal mechanisms, and stress modeling.

- **M1–M3 overlapping activation zones:** relocation refinement, waveform cross-correlation, and focal-mechanism comparison.

- **System-wide broader regional activation:** regional rate modeling, geodesy, ocean-bottom pressure data, and stress-field comparison.

- **M2–M3 independent local clusters plus regional context:** improve relocations and background-rate modeling before any stronger physical interpretation.

- **M2–M3 artifact or window sensitivity:** expand the control suite and compare alternative windows before escalating to physical inference.

## Medium priority

- **M1–M3 delayed activation:** lagged rate-change tests, waveform similarity, and stress-change screening.

- **M1–M3 compound or swarm-like organization:** waveform family analysis, relocation, and fluid-sensitive geodetic or ocean-bottom pressure review.

- **M1–M2 independent-cluster or linked-fault alternatives:** revisit only after improved relocations and broader regional modeling are available.

## Low priority

- Immediate escalation of M1–M2 local corridor linkage.

- Overlap or delayed local activation for M1–M2 and M2–M3.

- Compound or swarm-like linkage for M1–M2 or M2–M3.

# Limitations and Required Caution

The scientific confidence of this report is moderate. The delivery status of the underlying workflow is complete and satisfactory, but several limitations materially affect interpretation:

1.  The report is a synthesis stage only and depends on the validity of the upstream relationship-analysis outputs in the `01_relationship_analysis` directory.

2.  All conclusions are explicitly catalog-level. They do not demonstrate physical triggering, rupture interaction, stress transfer, fluid migration, or any other mechanism.

3.  Several interpretations remain split across raw, control-corrected, and distance-aware layers. This is especially important for M1–M3, where ambiguity remains substantial, and for M2–M3, where artifact or background competition remains significant.

4.  Corridor, endpoint, and temporal-window definitions are central to multiple metrics. Pair-specific strengths, especially corridor-style interpretations, should therefore be treated as conditional on the adopted geometric and temporal framing.

5.  The workflow context explicitly notes that M1–M2 has the lowest assignment stability among the pairs, with stable fraction approximately 0.78, which reinforces the need for caution in interpreting pair-specific event assignment.

6.  A low-severity semantic mismatch was reported between one M2–M3 independent-local-clusters follow-up table entry and the narrative text. This does not change the central scientific interpretation, but it can confuse downstream prioritization if read without context.

7.  Mechanism information was matched conservatively and not fully exploited for pair discrimination. This limits how strongly current outputs can separate some follow-up targets.

# Conclusions

The Aomori M1, M2, and M3 earthquake clusters do show catalog-level relationships worth further scientific investigation, but those relationships are not uniform across pairs.

The most robust system-wide conclusion is that the three clusters are better viewed as components of a broader regional activation episode than as a set of uniformly direct pairwise links. This conclusion is supported by the relationship evidence matrix (Figure <a href="#fig:matrix" data-reference-type="ref" data-reference="fig:matrix">5</a>; Table <a href="#tab:matrix" data-reference-type="ref" data-reference="tab:matrix">[tab:matrix]</a>) and by the persistence of regional-activation support across all three pairs after control correction and distance-aware screening.

Within that broader regional picture, M1–M3 is the highest-priority pair for deeper physical analysis. It is the only pair that remains distance-plausible for nearby source-region linkage while retaining moderate-to-strong support for several relationship-aware hypotheses after controls. The most promising next tests are high-precision relocation, waveform cross-correlation, focal-mechanism comparison, and stress or fluid-sensitive contextual analyses.

M1–M2 shows real catalog-level structure, including strong corridor and between-event signals relative to controls, but its geometry does not support a simple local-linkage interpretation. It should therefore be investigated primarily as a regional-scale relationship, not as the strongest candidate for direct local pair coupling.

M2–M3 is best treated as predominantly independent local clusters within the same broader regional episode. For this pair, local-linkage interpretations remain weak, while independent-cluster, regional-rate, and background-window explanations remain active and should be tested first.

Overall, the catalog alone justifies prioritizing M1–M3 local-linkage-style follow-up and system-wide regional-activation follow-up, while discouraging overinterpretation of distant or weakly distance-plausible pairwise patterns.
