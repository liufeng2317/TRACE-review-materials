---
author:
- TRACE
date: 2026-05-23
title: Event-Centered Sequence Analysis Around Three Matched Major Earthquakes in the Aomori Regional Catalog
---

# Abstract

We performed an event-centered sequence analysis for three matched major earthquakes in the Aomori regional relocated catalog. The workflow verified the required fields in the relocated catalog, the mainshock reference table, the focal-mechanism inventory, and the station metadata; re-matched the three target earthquakes to the relocated catalog; extracted surrounding seismicity under a grid of spatial, temporal, depth, and magnitude definitions; and computed diagnostic summaries of counts, rates, distributions, and control comparisons. The resulting sequence evidence indicates a robust post-event increase in seismicity around all three mainshocks, but with distinct styles: M1 is the most spatially concentrated and strongly aftershock-like, M2 is the deepest and shows the strongest relative activation, and M3 is the most bursty and spatially extensive. The sign of the post-event response is stable across tested definitions, whereas amplitudes and decay diagnostics are more parameter dependent. Focal-mechanism and station-context summaries are informative but uneven, so they are treated as contextual rather than primary evidence.

# Introduction

Event-centered sequence analysis is a standard way to assess whether a mainshock is associated with localized, time-dependent seismicity changes. Here the objective was to compare the pre- and post-event evolution of seismicity around three matched major earthquakes in the Aomori regional catalog, and to test whether observed sequence patterns remain robust when the radius, time window, depth selection, and magnitude threshold are varied. The analysis was designed to support later focused interpretation of M1, M2, and M3 using the relocated regional catalog as the primary observational dataset.

The scientific setting is favorable for sequence analysis because the catalog is large and internally consistent, seismicity is spatially clustered and segmented, and the activity is burst-like rather than stationary. At the same time, the preliminary completeness magnitude is low enough to support screening-level analyses, while focal-mechanism coverage and station-context information are uneven and therefore require caution in interpretation.

# Data and verification

## Input tables

The following source tables were used:  

|  |  |
|:---|:---|
| Relocated regional catalog | <file://<CASE_ROOT>/data/catalog/Snet_catalog_relocate.csv> |
| Major-earthquake reference table | <file://<CASE_ROOT>/data/catalog/main_earthquake.csv> |
| Focal-mechanism inventory | <file://<CASE_ROOT>/data/source_mechanism/Snet_mecha.csv> |
| Station metadata | <file://<CASE_ROOT>/data/stations/station.sta> |

The verification step confirmed the essential fields needed for event-centered analysis: time, latitude, longitude, depth, magnitude, and event identifiers where available. The verification and rematching products are summarized in the task outputs, especially `field_verification_catalog.json`, `field_verification_main_earthquake.json`, `field_verification_mechanism.json`, `field_verification_stations.json`, and `matched_mainshocks.csv` under <file://<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/01_data_verification_and_rematch/>.

## Mainshock rematching

The three target earthquakes were re-matched to the relocated catalog using a proximity-based candidate search that allowed for small time and location shifts introduced by relocation. This rematching succeeded with high confidence for all three events, and the agreement is especially strong for M1, which shows sub-second and sub-kilometer consistency with the reference record. The rematched events are used as the event centers for all subsequent sequence extraction, diagnostics, robustness testing, and figure generation.

## Coverage context

The station inventory includes broad regional coverage with 371 stations, but station matching is contextual metadata rather than a direct completeness model. Focal-mechanism availability is present but uneven across the sequences: the evidence indicates comparatively strong immediate coverage around M2 and limited local coverage around M1. Consequently, mechanism summaries are included as contextual support, not as the main basis for the event-centered seismicity conclusions.

# Methods

## Sequence extraction design

For each rematched mainshock, event-centered sequences were extracted under a full parameter grid comprising:

- radii of 30, 44, 50, 80, and 100 km;

- temporal windows of pre-90 d, pre-60 d, pre-30 d, pre-7 d, post-7 d, post-30 d, post-60 d, and post-90 d;

- depth strategies including all depths, mainshock-centered depth windows, and depth-stratified windows;

- magnitude thresholds of all events, M $`\geq`$ 1.2, 1.5, 2.0, and 2.5 where feasible.

The full sequence table is available as <file://<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/02_sequence_extraction/event_centered_sequence_table.csv>.

## Diagnostics

The diagnostic workflow computed event counts, cumulative counts, moving-window rates, pre/post rate ratios, magnitude and depth distributions, radial-distance patterns, and simple decay diagnostics including Omori-style fitting where feasible. The analysis also tracked focal-mechanism overlap and station-context summaries when available. Diagnostic tables are archived in <file://<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/03_sequence_diagnostics/>.

## Robustness and controls

Robustness testing assessed whether the sign of the post-event response persists across changes in radius, time window, depth strategy, and magnitude threshold. In addition, at least one simple control comparison was evaluated, including background-window comparisons and randomized timing controls. These controls are summarized in `control_summary.csv` and related outputs in <file://<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/06_control_comparison/> and the robustness directory.

## Figure generation

A standardized figure set was produced for all three sequences, including event-centered maps, pre/post comparisons, cumulative count curves, moving-window rate curves, rate-decay plots, radial-distance diagnostics, sensitivity heatmaps, depth-stratified plots, and a comparison summary figure. The figure-ready data and verification record are stored in <file://<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/07_figure_generation/>.

# Results

## Summary of the event-centered sequences

The three matched earthquakes all show post-event clustering above pre-event background levels, but the absolute and relative responses differ. The main scientific pattern is robustly directional: post-event seismicity increases after all three mainshocks under the tested definitions. The output tables support the following qualitative ranking:

- M2 shows the strongest relative activation and the clearest depth-distinct behavior;

- M1 shows the tightest spatial concentration and strong aftershock-like decay;

- M3 also shows elevated post-event activity, but with weaker relative amplification and greater burstiness.

The baseline comparison tables and figure-ready summaries are stored in `baseline_sequence_table.csv`, `baseline_summary_table.csv`, `comparison_table.csv`, and the control files in the reusable-output directory <file://<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/08_reusable_outputs/>.

## Pre- versus post-event activity

Across the tested windows, the post-event counts exceed the pre-event counts in the baseline event-centered windows. The control-comparison outputs further indicate that the observed post-event rates are above background-like windows and above randomized medians. This supports a true event-centered seismicity response rather than a trivial artifact of catalog length or the selected time origin.

The strongest short-term concentration is visible in the immediate post-event windows, consistent with aftershock-like behavior. However, the magnitude of the pre/post ratio is not identical across sequences: M2 is the strongest on a relative basis, while M1 often has the largest absolute post-event counts.

## Spatial concentration and expansion

Spatially, M1 is the most concentrated event-centered sequence, whereas M3 appears broader and more spatially extensive. M2 is distinct in both position and depth, indicating that the three earthquake-centered sequences are not merely copies of the same local pattern. This spatial segmentation is consistent with the regional clustering noted in the prior data-foundation analysis.

Figure references intended for the publication-style summary are: event-centered maps for M1, M2, and M3, pre/post comparison maps, and radial-distance diagnostics. The compact evidence packet did not enumerate the exact rendered image filenames, so the figure set is referenced here as a verified output suite rather than with individual file paths. See the figure-generation output directory for the complete verified figure set.

## Temporal evolution and decay behavior

The moving-window rate curves show a sharp post-event increase after each mainshock, with short-term enhancement strongest immediately after the event. Omori-style decay fits were feasible only for a subset of sequences and were less stable for M3. Therefore, decay interpretation is conditional: the qualitative aftershock-like trend is supported, but quantitative decay parameters should not be over-interpreted as uniform across all events and parameter sets.

The cumulative-count curves provide complementary evidence for a rapid post-event accumulation of events relative to the pre-event interval. These curves are especially useful for visualizing the burst-like character of the response.

## Magnitude and depth structure

The magnitude distributions indicate that the event-centered post-event sequences are not driven only by the smallest detected earthquakes, although the lower threshold of M $`\geq`$ 1.2 provides the broadest and most stable screening basis. Testing higher thresholds preserves the qualitative post-event increase, demonstrating that the response is not an artifact of only the lowest-magnitude events.

The depth summaries reinforce the sequence-level distinction among the three mainshocks. M2 is the clearest depth-distinct event, whereas M1 and M3 are more comparable in shallower clustered contexts. Depth-stratified analyses therefore add interpretive value rather than simply reproducing the all-depth signal.

## Control comparisons

The control analyses show that the observed post-event clustering is not explained by simple background windows or by randomized mainshock timing. In the baseline 50 km / 90 d / M $`\geq`$ 1.2 setting, all three events remain above background-like expectations, with M2 strongest, M1 intermediate, and M3 weakest in relative amplification. The randomized-control summaries indicate that the observed post-event rates are systematically above randomized medians, which supports a true event-centered response.

## Mechanism and station context

Focal-mechanism availability is uneven across the sequences. The mechanism summaries indicate stronger immediate coverage around M2 than around M1, with M3 also limited relative to the full catalog. Station coverage is broad, but station metadata should not be interpreted as a direct proxy for detection completeness at the sequence scale. These contextual datasets are useful for interpreting potential structural differences, but they do not alter the main conclusion that all three sequences exhibit post-event activation.

# Robustness analysis

The robustness outputs show that the sign of the post-event response is stable across the parameter grid. In particular, the post-event increase in seismicity and the short-term rate peak persist across radii from 30 to 100 km, time windows from 7 to 90 days, depth strategies, and magnitude thresholds from all events to M $`\geq`$ 2.5 where feasible. This is the key stable feature of the analysis.

Parameter dependence appears primarily in the amplitudes and in the stability of Omori-style decay fits. M1 is the most stable across parameter choices, M2 is the most sensitive to spatial and temporal definition yet remains the strongest in relative terms, and M3 is the most variable in burstiness and decay behavior. Thus, the observed sequence styles are robust in sign but not uniform in magnitude or model fit quality.

The robustness and stability tables are `robustness_results.csv`, `sensitivity_summary.csv`, `stability_flags.csv`, `stability_feature_flags.csv`, `robustness_across_definitions.csv`, and related files in <file://<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/04_robustness_analysis/> and <file://<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/05_three_sequence_comparison/>.

# Three-sequence comparison

The three earthquakes share a regional seismicity background but show distinct event-centered behaviors:

- **M1**: strongest spatial concentration, strong aftershock-like decay, and comparatively stable behavior across definitions.

- **M2**: strongest relative activation, deeper source region, and the clearest sensitivity to spatial and temporal definition.

- **M3**: most bursty and spatially extensive, with the smallest post/pre ratio and the weakest decay stability.

The three-sequence comparison tables support a common qualitative conclusion: all three mainshocks are followed by enhanced seismicity, but the response style is not identical. M2 has the largest relative amplification, M1 has the largest absolute post-event count, and M3 has the most diffuse response. These distinctions persist in the comparative summary outputs and in the figure-ready data products.

# Simple control comparison

The control comparison is an important sanity check. It demonstrates that the post-event clustering near M1, M2, and M3 exceeds background-like windows and randomized timing controls. Because the control workflow is intentionally simple, it should be interpreted as a screening-level null comparison rather than a full stochastic model of catalog activity. Even so, the control results substantially strengthen the inference that the mainshock-centered increases are real and not caused by a generic bursty background alone.

# Reusable outputs and reproducibility

A complete set of reusable tables and figure-ready datasets was exported for downstream work. The most important outputs are:

- validated inventories and rematch summaries from task 01;

- the event-centered sequence table and extraction counts from task 02;

- diagnostic summaries of counts, distributions, and decay from task 03;

- robustness and stability summaries from task 04;

- cross-sequence comparison tables from task 05;

- control-comparison tables from task 06;

- figure-ready baseline and comparison tables from task 07; and

- consolidated reusable outputs from task 08.

These outputs are sufficient for later focused interpretation, replotting, and extension of the Aomori earthquake-sequence analysis.

# Limitations

Several limitations should be carried forward into any follow-up analysis:

1.  Some handoff records are truncated, so not every table and figure could be exhaustively inspected from the summaries alone.

2.  Omori-style decay fits are conditional and not uniformly available, especially for M3.

3.  Focal-mechanism and station-context coverage are uneven, limiting mechanism-centered interpretation.

4.  The control model is intentionally simple and should be viewed as a screening-level null rather than a complete statistical model.

5.  Figure filenames were not fully enumerated in the compact evidence packet, so this report references the figure-generation products through the verified figure-data tables and the task output directory.

These limitations do not change the main conclusion that the three matched major earthquakes are followed by robust post-event seismicity increases, but they do constrain the precision with which decay and mechanism-related claims can be made.

# Conclusions

The event-centered sequence analysis in the Aomori regional catalog successfully matched the three mainshocks, extracted a full parameter grid of surrounding seismicity, and demonstrated a robust post-event increase around M1, M2, and M3. The main qualitative findings are stable across spatial, temporal, depth, and magnitude definitions, while quantitative amplitudes and decay behavior remain parameter dependent. M2 is the strongest relative sequence, M1 is the most spatially concentrated and stable, and M3 is the most bursty and spatially extensive. Together, the verified tables, control comparisons, robustness summaries, and figure-ready outputs provide a reusable evidence base for subsequent focused earthquake-sequence interpretation.

# Data and output locations

All primary artifacts were generated under:

> <file://<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/>

The report itself is written for the TRACE workflow and is intended to accompany the reusable analysis outputs.
