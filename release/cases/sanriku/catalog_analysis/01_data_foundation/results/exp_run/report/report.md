---
author:
- TRACE
date: 2026-05-23
title: Stage-1 Seismicity Data Assessment and Regional Background Characterization for the Japan Aomori Catalog
---

# Abstract

This report documents the Stage-1 data foundation for the Japan Aomori catalog analysis. Using the relocated regional catalog, a three-event major-earthquake reference table, a source-mechanism inventory, and a station list, we completed data auditing and cleaning, matched the major earthquakes to the relocated catalog, characterized the regional seismicity background, summarized the local context around each mainshock, generated a publication-oriented diagnostic figure set, and distilled candidate patterns for later sequence analysis. The cleaned catalog is internally consistent and large enough for robust background characterization, but several inference steps remain screening-level: completeness and Gutenberg–Richter parameters are preliminary, focal-mechanism coverage is partial, and station coverage metrics are simple proximity-based diagnostics rather than full azimuthal-gap or waveform-quality assessments.

# Introduction

The objective of this workflow was to build a reliable observational foundation for subsequent earthquake-sequence analysis in the Aomori region of Japan. The delivered data package includes a relocated regional earthquake catalog, a major-earthquake reference file, a source-mechanism catalog, and a station inventory. The analysis was designed to preserve the scientific evidence chain from audit and cleaning through matching, background characterization, context assessment, and pattern screening.

The report follows the implemented workflow rather than an idealized template: first the source data are audited and cleaned, then major earthquakes are linked to catalog events, followed by regional background characterization, mainshock-centered context analysis, figure generation, and candidate-pattern estimation.

# Data sources and workflow

## Input files

The analysis used the following files from the supplied data folder:

- relocated catalog: <a href="<CASE_ROOT>/data/catalog/Snet_catalog_relocate.csv" class="uri"><CASE_ROOT>/data/catalog/Snet_catalog_relocate.csv</a>

- major-earthquake reference table: <a href="<CASE_ROOT>/data/catalog/main_earthquake.csv" class="uri"><CASE_ROOT>/data/catalog/main_earthquake.csv</a>

- source-mechanism inventory: <a href="<CASE_ROOT>/data/source_mechanism/Snet_mecha.csv" class="uri"><CASE_ROOT>/data/source_mechanism/Snet_mecha.csv</a>

- station inventory: <a href="<CASE_ROOT>/data/stations/station.sta" class="uri"><CASE_ROOT>/data/stations/station.sta</a>

## Implemented processing steps

The implemented workflow produced cleaned machine-readable outputs for the catalog, major earthquakes, mechanisms, and stations, together with audit summaries and diagnostic products. The Stage-1 catalog includes parsed origin time, latitude, longitude, depth, magnitude, event identifiers where available, and Boolean quality flags. Major-earthquake matching used the relocated catalog and selected the nearest catalog event in a time-centered search window, with spatial, depth, and magnitude differences computed as diagnostics. Regional background characterization included depth and magnitude summaries, depth segmentation, temporal activity-rate diagnostics, magnitude-frequency analysis with preliminary completeness magnitude $`M_c`$ and $`b`$-value estimation, station coverage summaries, and focal-mechanism availability metrics. Mainshock context analysis then summarized local event density, local depth structure, nearby stations, nearby mechanisms, and recommended sequence-analysis thresholds.

# Data audit and cleaning

## Audit results

The data audit indicates that the relocated regional catalog is clean, large, and internally consistent. The key result is a validated Stage-1 seismicity foundation with 25,646 events and no detected duplicates or out-of-range coordinate, depth, or magnitude values. Time parsing was successful for the regional catalog, enabling downstream temporal analyses and event matching.

The major-earthquake reference file is small, containing only 3 events, so it must be treated as a sparse reference set rather than a statistical sample. The focal-mechanism dataset is usable but incomplete: only 139 records carry core mechanism/geometry availability, and the mechanism availability metrics therefore support screening-level interpretation only. The station network is broad, with 371 matched stations spanning a large latitudinal and longitudinal range.

## Reusable Stage-1 products

The most important reusable outputs from the audit stage are the cleaned catalog and quality products in the audit output directory, including:

- <a href="<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/01_data_audit_cleaning/quality_summary.csv" class="uri"><CASE_ROOT>/run/01_data_foundation/exp_run/outputs/01_data_audit_cleaning/quality_summary.csv</a>

- <a href="<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/01_data_audit_cleaning/field_mapping_summary.csv" class="uri"><CASE_ROOT>/run/01_data_foundation/exp_run/outputs/01_data_audit_cleaning/field_mapping_summary.csv</a>

- <a href="<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/01_data_audit_cleaning/abnormal_value_report.csv" class="uri"><CASE_ROOT>/run/01_data_foundation/exp_run/outputs/01_data_audit_cleaning/abnormal_value_report.csv</a>

- <a href="<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/01_data_audit_cleaning/duplicate_signature_report.csv" class="uri"><CASE_ROOT>/run/01_data_foundation/exp_run/outputs/01_data_audit_cleaning/duplicate_signature_report.csv</a>

- <a href="<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/01_data_audit_cleaning/main_earthquake_clean.csv" class="uri"><CASE_ROOT>/run/01_data_foundation/exp_run/outputs/01_data_audit_cleaning/main_earthquake_clean.csv</a>

- <a href="<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/01_data_audit_cleaning/mechanism_summary.csv" class="uri"><CASE_ROOT>/run/01_data_foundation/exp_run/outputs/01_data_audit_cleaning/mechanism_summary.csv</a>

# Major-earthquake matching

Three major earthquakes were matched to the relocated regional catalog with high confidence and no unmatched cases. The best matches show near-zero time offsets, sub-kilometer spatial separations, negligible depth differences, and identical magnitudes, indicating that the relocation-preserved event identities are tightly consistent between the reference table and the regional catalog.

| **Aspect**               | Result                        |
|:-------------------------|:------------------------------|
| **Reference events**     | 3                             |
| **Matched events**       | 3                             |
| **Unmatched events**     | 0                             |
| **Time offset**          | Near zero                     |
| **Spatial separation**   | Sub-kilometer                 |
| **Depth difference**     | Negligible                    |
| **Magnitude difference** | Identical in the best matches |
| **Confidence**           | High                          |

Summary of the major-earthquake matching stage. The detailed per-event matches are provided in the machine-readable output table <a href="<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/02_major_earthquake_matching/major_earthquake_matches.csv" class="uri"><CASE_ROOT>/run/01_data_foundation/exp_run/outputs/02_major_earthquake_matching/major_earthquake_matches.csv</a>.

This linkage provides a reliable event-to-event bridge for the later context analysis around M1, M2, and M3. The matching result should nevertheless be interpreted as produced by the implemented search-window and ranking logic, without an independent false-match benchmark.

# Regional seismicity background

## Spatial distribution and event density

The regional catalog is dominated by clustered seismicity concentrated within a broad corridor around 142–144$`^{\circ}`$E and 38.5–41.5$`^{\circ}`$N. The spatial diagnostics show two prominent density hotspots and several elongated substructures, consistent with tectonically organized and spatially segmented seismicity rather than uniform diffuse activity.

The spatial density and regional map figures are qualitatively strong diagnostics but do not, by themselves, quantify cluster significance or boundary sharpness. They nevertheless support the interpretation that the region contains multiple active seismic domains.

## Temporal activity rate

Temporal activity-rate analysis on 90-day windows indicates burst-like behavior rather than steady uniform seismicity. This supports the view that the catalog contains episodic clusters and quiet intervals, which is important for any future sequence model or declustering attempt.

## Magnitude and depth distributions

The magnitude-frequency structure indicates a complete catalog above the preliminary completeness threshold of $`M_c = 1.20`$ with a Gutenberg–Richter $`b`$-value of approximately 0.60 over the fitted range \[1.20, 7.70\]. This suggests a relatively large-event-rich distribution compared with a $`b \approx 1`$ reference case. The $`M_c`$ and $`b`$ estimates are screening-level metrics and should be treated as preliminary because they may vary with binning and the chosen fitting range.

Depths are strongly skewed toward approximately 10–30 km, with a sparse tail extending to about 120 km. The depth segmentation summary supports a shallow-to-intermediate focus with only limited deeper seismicity. The magnitude–depth relation is therefore shaped by a dominant shallow cloud and a smaller deep tail, rather than a single uniform depth regime.

| **Feature** | Characterization |
|:---|:---|
| **Spatial extent** | Broad Aomori corridor, roughly 142–144$`^{\circ}`$E and 38.5–41.5$`^{\circ}`$N |
| **Spatial pattern** | Clustered, segmented, with two main density hotspots |
| **Temporal pattern** | Burst-like, episodic activity |
| **Depth pattern** | Strong concentration at 10–30 km with a sparse deeper tail |
| **Completeness** | Preliminary $`M_c = 1.20`$ |
| **$`b`$-value** | Preliminary $`b \approx 0.60`$ |
| **Interpretation** | Complete above $`M_c`$, with relatively large-event-rich tail |

Regional background summary. The detailed statistics are stored in the machine-readable outputs from the background characterization task.

## Station coverage

The station network provides moderate to good coverage in the core of the earthquake cloud, with typical nearest-station distances of roughly 14–16 km. Coverage weakens toward the margins of the regional cloud, implying spatially heterogeneous observational support. The station diagnostic is useful for screening, but it does not replace full azimuthal-gap or waveform-quality evaluation.

## Focal-mechanism availability

The focal-mechanism inventory is usable but incomplete and unevenly distributed. Catalog-level mechanism availability is partial, with only 139 of 354 mechanism records carrying core mechanism/geometry availability. This limits mechanism-stratified interpretation and suggests that any later source-property analysis must explicitly account for data gaps.

# Mainshock regional context

The mainshock-context analysis shows that all three matched major earthquakes occur in spatially distinct, seismically active parts of the Aomori region, with local catalog densities above the regional median. The three events are not simply embedded in a homogeneous background cloud; instead, they sample different local seismic contexts.

| **Mainshock** | Context interpretation |
|:---|:---|
| **M1** | Highest local catalog density and strongest density ratio; sparse nearby station coverage and no local mechanism records in the local window. |
| **M2** | Only event flagged as depth-distinct; best nearby mechanism availability; sparse station coverage still limits observational completeness. |
| **M3** | Intermediate local density; limited mechanism coverage; sparse nearby station support. |

Mainshock regional-context synthesis. Detailed per-event values are contained in the machine-readable outputs from the context task.

The context results support a consistent preliminary sequence window of approximately 44 km radius and $`\pm`$<!-- -->26 km depth for all three events, together with a higher magnitude threshold for screening. M2 likely requires the most explicit depth stratification because it is the only event classified as depth-distinct. The sparse station coverage around all three mainshocks implies that later waveform-based or mechanism-based analysis may be unevenly constrained.

# Diagnostic figures

The workflow produced a coherent set of publication-oriented diagnostic figures. The figure package includes the regional map, time–magnitude plot, depth–time plot, magnitude–depth plot, magnitude-frequency / $`M_c`$–$`b`$ diagnostic, spatial density plot, depth-distribution plot, station coverage diagnostic, and mechanism/context panels. The report figures are stored in the figure output directory and are referenced below for reproducibility.

<figure id="fig:regional_map" data-latex-placement="H">
<img src="<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/05_diagnostic_figures/figure_01_regional_map.png" style="width:92.0%" />
<figcaption>Regional map of earthquakes, major earthquakes, stations, and available focal mechanisms. This is the principal spatial context figure for the Stage-1 assessment.</figcaption>
</figure>

<figure id="fig:time_magnitude" data-latex-placement="H">
<img src="<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/05_diagnostic_figures/figure_02_time_magnitude.png" style="width:92.0%" />
<figcaption>Time–magnitude evolution of the cleaned regional catalog, used to identify temporal bursts, quiet periods, and magnitude structure.</figcaption>
</figure>

<figure id="fig:depth_time" data-latex-placement="H">
<img src="<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/05_diagnostic_figures/figure_03_depth_time.png" style="width:92.0%" />
<figcaption>Depth–time plot for the cleaned catalog. The figure highlights the shallow-to-intermediate clustering and the sparse deeper tail.</figcaption>
</figure>

<figure id="fig:mag_depth" data-latex-placement="H">
<img src="<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/05_diagnostic_figures/figure_04_magnitude_depth.png" style="width:92.0%" />
<figcaption>Magnitude–depth scatter plot for the regional catalog. This diagnostic supports screening for depth-dependent magnitude structure and sampling bias.</figcaption>
</figure>

<figure id="fig:mfd" data-latex-placement="H">
<img src="<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/05_diagnostic_figures/figure_05_magnitude_frequency_mc_bvalue.png" style="width:92.0%" />
<figcaption>Magnitude-frequency distribution and preliminary <span class="math inline"><em>M</em><sub><em>c</em></sub></span> / <span class="math inline"><em>b</em></span>-value diagnostic. The figure should be treated as screening-level evidence rather than a final statistical estimate.</figcaption>
</figure>

<figure id="fig:spatial_density" data-latex-placement="H">
<img src="<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/05_diagnostic_figures/figure_06_spatial_density.png" style="width:92.0%" />
<figcaption>Spatial event-density diagnostic showing clustered seismicity and elongated substructures in the regional cloud.</figcaption>
</figure>

<figure id="fig:depth_distribution" data-latex-placement="H">
<img src="<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/05_diagnostic_figures/figure_07_depth_distribution.png" style="width:92.0%" />
<figcaption>Depth-distribution diagnostic for the regional catalog, supporting the interpretation of shallow-to-intermediate dominance with a sparse deeper tail.</figcaption>
</figure>

Additional report-relevant figure products include <a href="<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/04_mainshock_regional_context/figure_mainshock_regional_context_map.png" class="uri"><CASE_ROOT>/run/01_data_foundation/exp_run/outputs/04_mainshock_regional_context/figure_mainshock_regional_context_map.png</a>, <a href="<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/04_mainshock_regional_context/figure_mainshock_context_panels.png" class="uri"><CASE_ROOT>/run/01_data_foundation/exp_run/outputs/04_mainshock_regional_context/figure_mainshock_context_panels.png</a>, <a href="<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/06_candidate_patterns_estimation/figure_candidate_patterns_ranked.png" class="uri"><CASE_ROOT>/run/01_data_foundation/exp_run/outputs/06_candidate_patterns_estimation/figure_candidate_patterns_ranked.png</a>, and <a href="<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/06_candidate_patterns_estimation/figure_mainshock_context_overview.png" class="uri"><CASE_ROOT>/run/01_data_foundation/exp_run/outputs/06_candidate_patterns_estimation/figure_mainshock_context_overview.png</a>.

# Candidate patterns for follow-up analysis

The candidate-pattern estimation stage distilled the background and context results into a concise set of screening-level hypotheses. The strongest candidates are:

1.  mainshock-centered local seismicity enrichment, especially for M1 and M3;

2.  a depth-distinct regime around M2 that warrants separate depth stratification;

3.  spatially segmented regional seismicity with at least two density hotspots;

4.  burst-like temporal behavior that may require time-window sensitivity tests;

5.  station-coverage effects that may bias local detection and characterization near the margins;

6.  focal-mechanism data gaps that should be handled explicitly in any later source-property analysis.

These patterns are useful as testable hypotheses for downstream sequence analysis, but they are not formal statistical conclusions. The recommended working thresholds from the context analysis are approximately 44 km in radius, $`\pm`$<!-- -->26 km in depth, and a more conservative magnitude threshold for screening.

# Limitations and evaluation

Several important limitations should be carried forward into later analysis:

- The $`M_c`$ and $`b`$ estimates are preliminary diagnostics and are sensitive to binning and fit-range choices.

- Focal-mechanism coverage is partial and uneven, which limits mechanism-stratified inference.

- Station coverage metrics are proximity-based and do not replace azimuthal-gap or waveform-availability analysis.

- The mainshock context is descriptive, not causal; it does not test triggering or sequence dynamics.

- The candidate-pattern ranking is a screening output rather than a formal hypothesis test.

- The background snapshot file in the candidate-pattern stage was effectively empty, although the task still produced ranked outputs and summary tables.

Overall scientific confidence is moderate. The delivered products are complete for Stage-1 assessment and provide a defensible observational basis for sequence analysis, but several diagnostic quantities remain preliminary and should be refined in later stages.

# Conclusions

The Japan Aomori Stage-1 assessment successfully built a validated seismicity foundation, matched the three major earthquakes to the relocated catalog with high confidence, and characterized a region dominated by clustered shallow-to-intermediate seismicity, burst-like temporal variability, and heterogeneous station and focal-mechanism coverage. The resulting cleaned products, matched-event table, background summary statistics, context snapshots, and Nature-style diagnostic figures provide a reusable basis for downstream earthquake-sequence analysis.

The most important scientific takeaway is that the three major earthquakes occupy distinct active subdomains of an already clustered regional seismic environment. This makes event-specific context, depth stratification, and coverage-aware thresholding essential for later inference.
