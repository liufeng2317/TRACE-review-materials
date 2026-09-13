<science_report_context_compact>

## Context Map
Use this packet in order: objective -> actual methods -> core claims -> evidence index -> limitations/evaluation. Use context references and analysis files only when details are insufficient.

## Scientific Objective
<user_request>
You are an earthquake scientist and data-analysis agent.

Goal:
Build a reliable data foundation, characterize the regional seismicity background, generate publication-quality diagnostic figures, and prepare reusable data products for further sequence analysis.

Data folder:
"<CASE_ROOT>/data"

Files:
- catalog/Snet_catalog_relocate.csv
- catalog/main_earthquake.csv
- source_mechanism/Snet_mecha.csv
- stations/station.sta

Tasks:

1. Data audit and cleaning
Inspect all files for schema, record count, time/location/depth/magnitude ranges, missing values, duplicates, abnormal values, and usable fields.
Create a clean Stage-1 catalog with parsed time, latitude, longitude, depth, magnitude, event ID if available, and quality flags.

2. Major-earthquake matching
Match the major earthquakes in main_earthquake.csv with the regional catalog (a very small time shift caused by relocation).
For each major earthquake, report the nearest matched catalog event, time difference, spatial distance, depth difference, magnitude difference, and match confidence.

3. Regional seismicity background
Characterize the regional catalog in terms of:
- spatial distribution and event density
- temporal activity rate
- magnitude distribution
- depth distribution and depth segmentation
- magnitude-depth relationship
- preliminary completeness magnitude Mc and b-value (estimated with Gutenberg-Richter law)
- station distribution and simple coverage metrics
- focal-mechanism feature and distribution

4. Mainshock regional context
For each major earthquake, summarize its regional context:
- local event density
- surrounding depth distribution
- nearby station distribution and coverage
- nearby focal-mechanism distribution and availability
- whether the event lies in a distinct spatial/depth domain
- whether later sequence analysis should use special radius, depth, or magnitude thresholds

5. Diagnostic figures
Generate **Nature-Style** publication-quality figures
- regional map of earthquakes, major earthquakes, stations, and focal mechanisms if available
- time–magnitude plot
- depth–time plot
- magnitude–depth plot
- magnitude-frequency / Mc plot / b-value plot
- spatial event-density or cluster diagnostic
- depth-distribution or cross-section diagnostic
- station coverage diagnostic
- focal-mechanism distribution and availability diagnostic
- other useful regional-background plots that support further sequence analysis and hypothesis testing

Figures should use clear labels, units, legends, readable fonts, appropriate color scales, and should be saved as high-resolution PNG.

6. Candidate patterns estimation
Identify compact, testable candidate patterns for further sequence analysis and hypothesis testing, such as:
- spatial clusters
- temporal bursts or quiet periods
- depth segmentation
- magnitude-depth-space relationships
- station-coverage effects
- focal-mechanism data gaps
- regional differences around the major earthquakes
</user_request>

## Planning Snapshot
Use this only as intent context; prefer actual methods, claims, and evidence below for report content.
plan_summary: Goal Build a reliable observational data foundation for the Aomori/Japan regional catalog, match the major earthquakes to the relocated catalog, characterize regional seismicity background and station/focal-mechanism context, generate publication-quality diagnostic figures, and prepare reusable Stage-1 products for downstream sequence analysis. Planning Assumptions Use observation data only: relocated regional catalog, major-earthquake reference table, source-mechanism catalog, and station inventory. Core data sources: `catalog/Snet_catalog_relocate.csv` `catalog/main_earthquake.csv` `source_mechanism/Snet_mecha.csv` `stations/station.sta` Package/workflow contracts relevant to implementation: Tabular parsing must preserve raw columns and produce validated cleaned fields before any matching or statistical summaries. Time parsing should use the file’s actual datetime/origin-time fields; d
...[truncated]

## Context References
- full_audit_context: <CASE_ROOT>/run/01_data_foundation/exp_run/report/science_report_context.md

## Task Ledger
<task_record>
name: 01_data_audit_cleaning
description: Audit all source files and build a validated Stage-1 cleaned regional catalog with quality flags.
ancestors: none
handoff_json: <CASE_ROOT>/run/01_data_foundation/exp_run/log/coding_progress/task_handoff/01_data_audit_cleaning.json
analysis_file: <CASE_ROOT>/run/01_data_foundation/exp_run/analysis/01_data_audit_cleaning.md
output_dir: <CASE_ROOT>/run/01_data_foundation/exp_run/outputs/01_data_audit_cleaning
</task_record>

<task_record>
name: 02_major_earthquake_matching
description: Match major earthquakes to the relocated catalog and quantify match confidence and differences.
ancestors: 01_data_audit_cleaning
handoff_json: <CASE_ROOT>/run/01_data_foundation/exp_run/log/coding_progress/task_handoff/02_major_earthquake_matching.json
analysis_file: <CASE_ROOT>/run/01_data_foundation/exp_run/analysis/02_major_earthquake_matching.md
output_dir: <CASE_ROOT>/run/01_data_foundation/exp_run/outputs/02_major_earthquake_matching
</task_record>

<task_record>
name: 03_regional_background_characterization
description: Characterize regional seismicity background, station coverage, and mechanism availability from the cleaned catalog.
ancestors: 01_data_audit_cleaning
handoff_json: <CASE_ROOT>/run/01_data_foundation/exp_run/log/coding_progress/task_handoff/03_regional_background_characterization.json
analysis_file: <CASE_ROOT>/run/01_data_foundation/exp_run/analysis/03_regional_background_characterization.md
output_dir: <CASE_ROOT>/run/01_data_foundation/exp_run/outputs/03_regional_background_characterization
</task_record>

<task_record>
name: 04_mainshock_regional_context
description: Summarize local catalog, station, and mechanism context around each major earthquake.
ancestors: 01_data_audit_cleaning, 02_major_earthquake_matching, 03_regional_background_characterization
handoff_json: <CASE_ROOT>/run/01_data_foundation/exp_run/log/coding_progress/task_handoff/04_mainshock_regional_context.json
analysis_file: <CASE_ROOT>/run/01_data_foundation/exp_run/analysis/04_mainshock_regional_context.md
output_dir: <CASE_ROOT>/run/01_data_foundation/exp_run/outputs/04_mainshock_regional_context
</task_record>

<task_record>
name: 05_diagnostic_figures
description: Generate Nature-style high-resolution diagnostic figures for audit, background, and context analysis.
ancestors: 01_data_audit_cleaning, 02_major_earthquake_matching, 03_regional_background_characterization, 04_mainshock_regional_context
handoff_json: <CASE_ROOT>/run/01_data_foundation/exp_run/log/coding_progress/task_handoff/05_diagnostic_figures.json
analysis_file: <CASE_ROOT>/run/01_data_foundation/exp_run/analysis/05_diagnostic_figures.md
output_dir: <CASE_ROOT>/run/01_data_foundation/exp_run/outputs/05_diagnostic_figures
</task_record>

<task_record>
name: 06_candidate_patterns_estimation
description: Convert background and context results into ranked candidate patterns and follow-up analysis suggestions.
ancestors: 01_data_audit_cleaning, 02_major_earthquake_matching, 03_regional_background_characterization, 04_mainshock_regional_context
handoff_json: <CASE_ROOT>/run/01_data_foundation/exp_run/log/coding_progress/task_handoff/06_candidate_patterns_estimation.json
analysis_file: <CASE_ROOT>/run/01_data_foundation/exp_run/analysis/06_candidate_patterns_estimation.md
output_dir: <CASE_ROOT>/run/01_data_foundation/exp_run/outputs/06_candidate_patterns_estimation
</task_record>


## Actual Method Summary
This section summarizes what was actually implemented and analyzed. Use it instead of repeating the full plan.
<method_record task="01_data_audit_cleaning">
role: supporting_analysis
summary: The implementation produced a file-level audit, field mapping, numeric summaries, abnormal-value and duplicate checks, and cleaned machine-readable products for the regional catalog, major earthquakes, focal mechanisms, and stations. Evidence of the implemented workflow is contained in: - `[path]` - `[path]` - `[path]` - `[path]` The cleaned Stage-1 catalog includes parsed origin time, latitude, longitude, depth, magnitude, event identifiers where available, and Boolean quality flags. For the mechanism and station
...[truncated]
</method_record>
workflow_role: Audit all source files and build a validated Stage-1 cleaned regional catalog with quality flags.

<method_record task="02_major_earthquake_matching">
role: supporting_analysis
summary: The implemented matching workflow used the major-earthquake reference file and searched the relocated catalog within a time window large enough to accommodate small relocation-related shifts. For each reference earthquake, the nearest catalog event was selected using time proximity, with spatial and depth differences then computed as match diagnostics. Evidence of implementation and resulting products: - Matching summary: `[path]` - Matched-event table: `[path]` - Candidate list used for ranking/match selection: `[
...[truncated]
</method_record>
workflow_role: Match major earthquakes to the relocated catalog and quantify match confidence and differences.

<method_record task="03_regional_background_characterization">
role: supporting_analysis
summary: The implemented workflow produced a cleaned regional background catalog and a set of summary tables and diagnostic figures from the Stage-1 catalog. Evidence for the implementation is contained in: - `[path]` - `[path]` - `[path]` - `[path]` The regional characterization included: - depth and magnitude descriptive statistics; - depth segmentation summary; - temporal activity-rate analysis on 90-day windows; - magnitude-frequency distribution and preliminary Mc/b-value estimation; - station coverage diagnostics usin
...[truncated]
</method_record>
workflow_role: Characterize regional seismicity background, station coverage, and mechanism availability from the cleaned catalog.

<method_record task="04_mainshock_regional_context">
role: supporting_analysis
summary: The task produced a per-mainshock regional-context assessment using the cleaned regional catalog, station list, and mechanism records from earlier steps. Evidence of the implemented workflow is provided by: - `[path]` - `[path]` - `[path]` - `[path]` - `[path]` The summary tables show that the implementation computed: - a **local catalog window** for each mainshock, - local event counts and density relative to a regional reference, - local depth statistics and comparison with regional depth statistics, - local stat
...[truncated]
</method_record>
workflow_role: Summarize local catalog, station, and mechanism context around each major earthquake.

<method_record task="05_diagnostic_figures">
role: supporting_analysis
summary: The implementation produced a multi-figure diagnostic package in `[path]`, with a machine-readable inventory in `[path]`. The manifest confirms 11 PNG figures were generated and present: - `[path]` - `[path]` - `[path]` - `[path]` - `[path]` - `[path]` - `[path]` - `[path]` - `[path]` - `[path]` - `[path]` The figures collectively implement the intended diagnostic coverage: - regional spatial map with earthquakes, major events, stations, and mechanisms; - temporal activity and magnitude evolution; - depth–time evol
...[truncated]
</method_record>
workflow_role: Generate Nature-style high-resolution diagnostic figures for audit, background, and context analysis.

<method_record task="06_candidate_patterns_estimation">
role: final_analysis
summary: The implementation appears to combine summary statistics from the background catalog and the mainshock-centered context snapshots, then rank candidate hypotheses by a priority score. Evidence of this workflow is provided by: - `"[path]` - `"[path]` - `"[path]` - `"[path]` - `"[path]` The ranked output indicates that the approach uses: - **mainshock-specific local context metrics** such as local density ratio, station count, mechanism-record count, and depth-domain flag; - **catalog-wide pattern flags** such as foca
...[truncated]
</method_record>
workflow_role: Convert background and context results into ranked candidate patterns and follow-up analysis suggestions.


## Core Scientific Claims
Use these claim-oriented summaries as the backbone of the final report. Each major claim should remain tied to the evidence index below.
<scientific_claim task="01_data_audit_cleaning">
claim_role: supporting
This task successfully built a validated Stage-1 seismicity foundation for the Japan Aomori analysis. The regional relocated catalog is clean, large, and internally consistent, with 25,646 events, full time parsing, no detected duplicates, and no out-of-range coordinate/depth/magnitude values. The major-earthquake file was parsed cleanly but contains only 3 events, requiring careful treatment in subsequent matching and contextual analyses. The focal-mechanism dataset is usable but incomplete, with only 139 records carrying core mechanism/geometry availability, and the station network is broad, with 371 matched stations spanning a large latitudinal and longitudinal range. The most important reusable outputs for later stages are the cleaned catalog, cleaned mechanism and station tables, and the quality, numeric-summary, abnormal-value, and
...[truncated]
</scientific_claim>

<scientific_claim task="02_major_earthquake_matching">
claim_role: supporting
Three major earthquakes were matched to the relocated regional catalog with high confidence and no unmatched cases. The best matches show near-zero time offsets, sub-kilometer spatial separations, negligible depth differences, and identical magnitudes, indicating that the relocated catalog preserves the mainshock identities very tightly. These results provide a reliable event-to-event linkage for subsequent sequence analysis around M1, M2, and M3.
</scientific_claim>

<scientific_claim task="03_regional_background_characterization">
claim_role: supporting
The regional background catalog for the Aomori/Japan case is dominated by clustered shallow-to-intermediate seismicity with strong spatial segmentation and burst-like temporal behavior. The main seismicity corridor is concentrated around 142–144°E and 38.5–41.5°N, with two prominent density hotspots and several elongated substructures. Depths are strongly skewed toward ~10–30 km, with a sparse tail reaching ~120 km. The preliminary magnitude completeness is Mc = 1.20 and the Gutenberg–Richter b-value is about 0.60 over the fitted range [1.20, 7.70], indicating a complete catalog above the threshold but a relatively large-event-rich distribution.

Station coverage is moderate to good in the core of the earthquake cloud, with typical nearest-station distances around 14–16 km, but it becomes weaker toward the margins. Focal-mechanism informa
...[truncated]
</scientific_claim>

<scientific_claim task="04_mainshock_regional_context">
claim_role: supporting
The mainshock-regional-context assessment shows that the three matched major earthquakes all occur in **spatially distinct, seismically active parts of the Aomori region**, with local event densities substantially above the regional median. **M1** has the highest local catalog density and the strongest density ratio, **M2** is the only event flagged as **depth-distinct** and also has the best nearby mechanism availability, and **M3** is intermediate in density but has limited mechanism coverage. All three events have only **sparse station coverage** in their local windows, so later sequence analysis should account for possible observational bias. A consistent preliminary sequence window of **~44 km radius** and **~±26 km depth** was recommended for all three events, with a higher magnitude threshold suggested for screening. The most impor
...[truncated]
</scientific_claim>

<scientific_claim task="05_diagnostic_figures">
claim_role: supporting
This task successfully produced a coherent diagnostic figure package that supports background seismicity characterization and downstream sequence analysis. The evidence indicates a region dominated by clustered, episodic seismicity with strong shallow-to-intermediate depth concentration, non-uniform but workable station coverage, and spatially uneven but tectonically structured focal-mechanism availability. The strongest report-ready products are the regional map, time–magnitude plot, depth–time plot, station coverage diagnostic, and mechanism diagnostics; the magnitude-frequency / Mc–b figure remains preliminary and should be treated as a diagnostic rather than final statistical evidence.
</scientific_claim>

<scientific_claim task="06_candidate_patterns_estimation">
claim_role: final
The candidate-pattern estimation task successfully distilled the regional background and mainshock context into a short list of **high-priority sequence-analysis hypotheses**. The strongest patterns are **mainshock-centered local seismicity enrichment**, especially for **M1** and **M3**, followed by a **catalog-wide focal-mechanism data gap** that should be explicitly handled in any later tectonic or source-property analysis. The outputs support using a **~44 km spatial window**, a **~26 km depth window**, and **event-specific depth stratification**—particularly for the deeper M2 event. The most important reusable evidence files are `candidate_patterns_ranked.csv`, `mainshock_context_snapshot.csv`, `followup_analysis_suggestions.csv`, and the two overview figures in `figure_candidate_patterns_ranked.png` and `figure_mainshock_context_over
...[truncated]
</scientific_claim>


## Evidence Index
Use these handoff summaries as the primary artifact index. Read full handoff files only when this compact evidence is insufficient.
<task_evidence task="01_data_audit_cleaning">
status: success
stage: analysis_done
quality_flags: task_status:success
handoff_json: <CASE_ROOT>/run/01_data_foundation/exp_run/log/coding_progress/task_handoff/01_data_audit_cleaning.json
analysis_file: <CASE_ROOT>/run/01_data_foundation/exp_run/analysis/01_data_audit_cleaning.md
output_dir: <CASE_ROOT>/run/01_data_foundation/exp_run/outputs/01_data_audit_cleaning
result_summary: Audit all source files and build a validated Stage-1 cleaned regional catalog with quality flags. Status=success; outputs=13 discovered; primary=8.

primary_outputs:
- abnormal_value_report.csv: <CASE_ROOT>/run/01_data_foundation/exp_run/outputs/01_data_audit_cleaning/abnormal_value_report.csv
- duplicate_signature_report.csv: <CASE_ROOT>/run/01_data_foundation/exp_run/outputs/01_data_audit_cleaning/duplicate_signature_report.csv
- field_mapping_summary.csv: <CASE_ROOT>/run/01_data_foundation/exp_run/outputs/01_data_audit_cleaning/field_mapping_summary.csv
- file_level_audit_summary.csv: <CASE_ROOT>/run/01_data_foundation/exp_run/outputs/01_data_audit_cleaning/file_level_audit_summary.csv
- main_earthquake_clean.csv: <CASE_ROOT>/run/01_data_foundation/exp_run/outputs/01_data_audit_cleaning/main_earthquake_clean.csv
- main_earthquake_numeric_summary.csv: <CASE_ROOT>/run/01_data_foundation/exp_run/outputs/01_data_audit_cleaning/main_earthquake_numeric_summary.csv
- mechanism_summary.csv: <CASE_ROOT>/run/01_data_foundation/exp_run/outputs/01_data_audit_cleaning/mechanism_summary.csv
- quality_summary.csv: <CASE_ROOT>/run/01_data_foundation/exp_run/outputs/01_data_audit_cleaning/quality_summary.csv
</task_evidence>

<task_evidence task="02_major_earthquake_matching">
status: success
stage: analysis_done
quality_flags: task_status:success
handoff_json: <CASE_ROOT>/run/01_data_foundation/exp_run/log/coding_progress/task_handoff/02_major_earthquake_matching.json
analysis_file: <CASE_ROOT>/run/01_data_foundation/exp_run/analysis/02_major_earthquake_matching.md
output_dir: <CASE_ROOT>/run/01_data_foundation/exp_run/outputs/02_major_earthquake_matching
result_summary: Match major earthquakes to the relocated catalog and quantify match confidence and differences. Status=success; outputs=3 discovered; primary=3.

primary_outputs:
- major_earthquake_candidates.csv: <CASE_ROOT>/run/01_data_foundation/exp_run/outputs/02_major_earthquake_matching/major_earthquake_candidates.csv
- major_earthquake_match_summary.csv: <CASE_ROOT>/run/01_data_foundation/exp_run/outputs/02_major_earthquake_matching/major_earthquake_match_summary.csv
- major_earthquake_matches.csv: <CASE_ROOT>/run/01_data_foundation/exp_run/outputs/02_major_earthquake_matching/major_earthquake_matches.csv
</task_evidence>

<task_evidence task="03_regional_background_characterization">
status: success
stage: analysis_done
quality_flags: task_status:success, outputs_truncated
handoff_json: <CASE_ROOT>/run/01_data_foundation/exp_run/log/coding_progress/task_handoff/03_regional_background_characterization.json
analysis_file: <CASE_ROOT>/run/01_data_foundation/exp_run/analysis/03_regional_background_characterization.md
output_dir: <CASE_ROOT>/run/01_data_foundation/exp_run/outputs/03_regional_background_characterization
result_summary: Characterize regional seismicity background, station coverage, and mechanism availability from the cleaned catalog. Status=success; outputs=21 discovered; primary=8.

primary_outputs:
- depth_segmentation_summary.csv: <CASE_ROOT>/run/01_data_foundation/exp_run/outputs/03_regional_background_characterization/depth_segmentation_summary.csv
- depth_summary_stats.csv: <CASE_ROOT>/run/01_data_foundation/exp_run/outputs/03_regional_background_characterization/depth_summary_stats.csv
- magnitude_summary_stats.csv: <CASE_ROOT>/run/01_data_foundation/exp_run/outputs/03_regional_background_characterization/magnitude_summary_stats.csv
- mc_bvalue_estimate.csv: <CASE_ROOT>/run/01_data_foundation/exp_run/outputs/03_regional_background_characterization/mc_bvalue_estimate.csv
- mechanism_availability_metrics.csv: <CASE_ROOT>/run/01_data_foundation/exp_run/outputs/03_regional_background_characterization/mechanism_availability_metrics.csv
- mechanism_background_clean.csv: <CASE_ROOT>/run/01_data_foundation/exp_run/outputs/03_regional_background_characterization/mechanism_background_clean.csv
- mechanism_subset_joined_to_catalog.csv: <CASE_ROOT>/run/01_data_foundation/exp_run/outputs/03_regional_background_characterization/mechanism_subset_joined_to_catalog.csv
- regional_background_summary.csv: <CASE_ROOT>/run/01_data_foundation/exp_run/outputs/03_regional_background_characterization/regional_background_summary.csv
</task_evidence>

<task_evidence task="04_mainshock_regional_context">
status: success
stage: analysis_done
quality_flags: task_status:success
handoff_json: <CASE_ROOT>/run/01_data_foundation/exp_run/log/coding_progress/task_handoff/04_mainshock_regional_context.json
analysis_file: <CASE_ROOT>/run/01_data_foundation/exp_run/analysis/04_mainshock_regional_context.md
output_dir: <CASE_ROOT>/run/01_data_foundation/exp_run/outputs/04_mainshock_regional_context
result_summary: Summarize local catalog, station, and mechanism context around each major earthquake. Status=success; outputs=7 discovered; primary=7.

primary_outputs:
- mainshock_context_summary.csv: <CASE_ROOT>/run/01_data_foundation/exp_run/outputs/04_mainshock_regional_context/mainshock_context_summary.csv
- mainshock_local_catalog_windows.csv: <CASE_ROOT>/run/01_data_foundation/exp_run/outputs/04_mainshock_regional_context/mainshock_local_catalog_windows.csv
- mainshock_local_station_windows.csv: <CASE_ROOT>/run/01_data_foundation/exp_run/outputs/04_mainshock_regional_context/mainshock_local_station_windows.csv
- regional_context_overview.csv: <CASE_ROOT>/run/01_data_foundation/exp_run/outputs/04_mainshock_regional_context/regional_context_overview.csv
- sequence_threshold_notes.csv: <CASE_ROOT>/run/01_data_foundation/exp_run/outputs/04_mainshock_regional_context/sequence_threshold_notes.csv
- figure_mainshock_context_panels.png: <CASE_ROOT>/run/01_data_foundation/exp_run/outputs/04_mainshock_regional_context/figure_mainshock_context_panels.png
- figure_mainshock_regional_context_map.png: <CASE_ROOT>/run/01_data_foundation/exp_run/outputs/04_mainshock_regional_context/figure_mainshock_regional_context_map.png
</task_evidence>

<task_evidence task="05_diagnostic_figures">
status: success
stage: analysis_done
quality_flags: task_status:success
handoff_json: <CASE_ROOT>/run/01_data_foundation/exp_run/log/coding_progress/task_handoff/05_diagnostic_figures.json
analysis_file: <CASE_ROOT>/run/01_data_foundation/exp_run/analysis/05_diagnostic_figures.md
output_dir: <CASE_ROOT>/run/01_data_foundation/exp_run/outputs/05_diagnostic_figures
result_summary: Generate Nature-style high-resolution diagnostic figures for audit, background, and context analysis. Status=success; outputs=12 discovered; primary=8.

primary_outputs:
- figure_manifest.csv: <CASE_ROOT>/run/01_data_foundation/exp_run/outputs/05_diagnostic_figures/figure_manifest.csv
- figure_01_regional_map.png: <CASE_ROOT>/run/01_data_foundation/exp_run/outputs/05_diagnostic_figures/figure_01_regional_map.png
- figure_02_time_magnitude.png: <CASE_ROOT>/run/01_data_foundation/exp_run/outputs/05_diagnostic_figures/figure_02_time_magnitude.png
- figure_03_depth_time.png: <CASE_ROOT>/run/01_data_foundation/exp_run/outputs/05_diagnostic_figures/figure_03_depth_time.png
- figure_04_magnitude_depth.png: <CASE_ROOT>/run/01_data_foundation/exp_run/outputs/05_diagnostic_figures/figure_04_magnitude_depth.png
- figure_05_magnitude_frequency_mc_bvalue.png: <CASE_ROOT>/run/01_data_foundation/exp_run/outputs/05_diagnostic_figures/figure_05_magnitude_frequency_mc_bvalue.png
- figure_06_spatial_density.png: <CASE_ROOT>/run/01_data_foundation/exp_run/outputs/05_diagnostic_figures/figure_06_spatial_density.png
- figure_07_depth_distribution.png: <CASE_ROOT>/run/01_data_foundation/exp_run/outputs/05_diagnostic_figures/figure_07_depth_distribution.png
</task_evidence>

<task_evidence task="06_candidate_patterns_estimation">
status: success
stage: analysis_done
quality_flags: task_status:success
handoff_json: <CASE_ROOT>/run/01_data_foundation/exp_run/log/coding_progress/task_handoff/06_candidate_patterns_estimation.json
analysis_file: <CASE_ROOT>/run/01_data_foundation/exp_run/analysis/06_candidate_patterns_estimation.md
output_dir: <CASE_ROOT>/run/01_data_foundation/exp_run/outputs/06_candidate_patterns_estimation
result_summary: Convert background and context results into ranked candidate patterns and follow-up analysis suggestions. Status=success; outputs=7 discovered; primary=7.

primary_outputs:
- background_summary_snapshot.csv: <CASE_ROOT>/run/01_data_foundation/exp_run/outputs/06_candidate_patterns_estimation/background_summary_snapshot.csv
- candidate_patterns_ranked.csv: <CASE_ROOT>/run/01_data_foundation/exp_run/outputs/06_candidate_patterns_estimation/candidate_patterns_ranked.csv
- candidate_patterns_summary.csv: <CASE_ROOT>/run/01_data_foundation/exp_run/outputs/06_candidate_patterns_estimation/candidate_patterns_summary.csv
- followup_analysis_suggestions.csv: <CASE_ROOT>/run/01_data_foundation/exp_run/outputs/06_candidate_patterns_estimation/followup_analysis_suggestions.csv
- mainshock_context_snapshot.csv: <CASE_ROOT>/run/01_data_foundation/exp_run/outputs/06_candidate_patterns_estimation/mainshock_context_snapshot.csv
- figure_candidate_patterns_ranked.png: <CASE_ROOT>/run/01_data_foundation/exp_run/outputs/06_candidate_patterns_estimation/figure_candidate_patterns_ranked.png
- figure_mainshock_context_overview.png: <CASE_ROOT>/run/01_data_foundation/exp_run/outputs/06_candidate_patterns_estimation/figure_mainshock_context_overview.png
</task_evidence>


## Analysis Source Index
Read these task analysis files only when the method summary, claims, limitations, and evidence index are insufficient.
- 01_data_audit_cleaning: analysis=<CASE_ROOT>/run/01_data_foundation/exp_run/analysis/01_data_audit_cleaning.md; output_dir=<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/01_data_audit_cleaning
- 02_major_earthquake_matching: analysis=<CASE_ROOT>/run/01_data_foundation/exp_run/analysis/02_major_earthquake_matching.md; output_dir=<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/02_major_earthquake_matching
- 03_regional_background_characterization: analysis=<CASE_ROOT>/run/01_data_foundation/exp_run/analysis/03_regional_background_characterization.md; output_dir=<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/03_regional_background_characterization
- 04_mainshock_regional_context: analysis=<CASE_ROOT>/run/01_data_foundation/exp_run/analysis/04_mainshock_regional_context.md; output_dir=<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/04_mainshock_regional_context
- 05_diagnostic_figures: analysis=<CASE_ROOT>/run/01_data_foundation/exp_run/analysis/05_diagnostic_figures.md; output_dir=<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/05_diagnostic_figures
- 06_candidate_patterns_estimation: analysis=<CASE_ROOT>/run/01_data_foundation/exp_run/analysis/06_candidate_patterns_estimation.md; output_dir=<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/06_candidate_patterns_estimation

## Cross-Task Limitations and Assumptions
Use these limitations to qualify scientific claims in the final report.
<task_limitations task="01_data_audit_cleaning">
- No output images or PDFs were present in the task output directory, so no figure-specific analysis was possible for this task stage.
- The cleaned catalog quality assessment is based on implemented schema parsing and range checks; it does not by itself validate catalog completeness against the true seismic record or confirm that all events are physically unique.
- `main_earthquake.csv` contains only 3 events, so any later regional-context interpretation must treat this as a very small sample.
- The station file summary indicates broad network coverage, but station-response, temporal availability, and per-event azimuthal gap were not evaluated in this task.
- Focal-mechanism coverage is par
...[truncated]
</task_limitations>

<task_limitations task="02_major_earthquake_matching">
- No image or PDF products were present in this task output directory, so there are no diagnostic figures to assess for this specific matching step.
- The matching result depends on the chosen search-window and ranking logic used by the implemented script; this report reflects the produced outputs, not an independent re-computation of the algorithm.
- The candidate counts are large, so the confidence assessment is based on the uniqueness of the best-ranked solution rather than on a sparse candidate pool.
- The summary files indicate success, but they do not document an explicit false-match benchmark or manual validation against external authoritative catalogs.
- The outputs show only three m
...[truncated]
</task_limitations>

<task_limitations task="03_regional_background_characterization">
- The mechanism availability figure only reports record counts by category; it does not show how availability varies with time, depth, or magnitude. Therefore, any claim about temporal or magnitude dependence of mechanism completeness is not supported by that figure alone.
- The spatial-density and map figures are qualitative diagnostics. They clearly show clustering, but they do not by themselves quantify cluster significance, cluster boundaries, or tectonic segmentation.
- The MFD estimate is explicitly preliminary. The reported Mc = 1.20 and b ≈ 0.60 are useful for first-order analysis, but sensitivity to binning, fitting range, and catalog completeness should be evaluated before formal i
...[truncated]
</task_limitations>

<task_limitations task="04_mainshock_regional_context">
- The current task is a **context characterization**, not a full causal analysis. It identifies local patterns and data-support limitations, but does not test hypotheses about triggering or sequence dynamics.
- The station coverage is summarized from nearby stations, but the table suggests **sparse coverage** around all three mainshocks; that means any later waveform-based or focal-mechanism-based inference may be unevenly constrained.
- Mechanism availability differs strongly by event:
  - M2 has many nearby mechanism records,
  - M3 has only a few,
  - M1 has none in the local window.
  This creates uneven comparability across the three mainshocks.
- The same suggested sequence window appe
...[truncated]
</task_limitations>

<task_limitations task="05_diagnostic_figures">
- The figure manifest is machine-readable and confirms file existence and sizes, but it does not itself document plotting parameters, source catalog filtering, or any statistical thresholds used.
- The magnitude-frequency figure is preliminary: it explicitly notes that b is not estimated, so Mc/b interpretation remains incomplete in this task output.
- The spatial and cross-section figures are diagnostically useful but are not fully cartographically contextualized; for example, the regional map lacks a basemap/coastline context in the visible output.
- Some panels are dense with overplotted points, especially the depth–time, magnitude–depth, and cross-section plots, which reduces quantitativ
...[truncated]
</task_limitations>

<task_limitations task="06_candidate_patterns_estimation">
- `background_summary_snapshot.csv` is effectively empty in the delivered output directory: the file size is 1 byte and it could not be parsed as a table. This means the task’s final ranking likely relied on other inputs or in-memory values rather than a persistent background snapshot table.
- The ranked patterns are concise and highly actionable, but they are **screening-level hypotheses**, not formal statistical tests.
- The mainshock context metrics depend on the chosen local radius and depth window; the recommended thresholds are useful, but they should still be validated in sensitivity tests.
- Mechanism-based interpretation is limited by sparse coverage: the catalog-level mechanism ava
...[truncated]
</task_limitations>



## Evaluation Quality Summary
Use this evaluation metadata to disclose delivery status, scientific confidence, and important limitations in the final report.
<evaluation_quality>
{
  "delivery_status": "complete",
  "is_satisfactory": true,
  "limitations": [
    {
      "evidence": "Mc and Gutenberg-Richter b-value are reported as preliminary screening metrics, and the report notes sensitivity to binning and fitting range.",
      "impact": "The completeness and b-value estimates are useful for background characterization but should not yet be treated as final inferential results.",
      "severity": "medium",
      "type": "uncertainty"
    },
    {
      "evidence": "Focal-mechanism availability is partial: only 139 of 354 mechanism records have core mechanism/geometry availability.",
      "impact": "Mechanism-stratified interpretations are limited by sparse and uneven coverage.",
      "severity": "medium",
      "type": "data_coverage"
    },
    {
      "evidence": "Station coverage is summarized using nearest-station distance and related simple metrics.",
      "impact": "This is adequate for screening, but it does not fully capture azimuthal gap or full location-quality effects.",
      "severity": "low",
      "type": "method_assumption"
    },
    {
      "evidence": "The figure set is complete and publication-oriented, but the report notes some dense overplotting and that the magnitude-frequency figure is diagnostic rather than final statistical evidence.",
      "impact": "Visual readability is acceptable overall, but some panels may not support fine-scale quantitative inspection.",
      "severity": "low",
      "type": "output_quality"
    },
    {
      "evidence": "One background snapshot file was noted as effectively empty in the candidate-pattern task, though the task still produced ranked outputs and summary tables.",
      "impact": "This is a minor robustness issue, but it does not undermine the delivered conclusions.",
      "severity": "low",
      "type": "runtime_partial_failure"
    }
  ],
  "needs_refinement": false,
  "refinement_priority": "none",
  "scientific_confidence": "moderate"
}
</evaluation_quality>

## Report Synthesis Rules
- Start from the scientific objective, actual methods, core claims, and evidence index.
- Choose the final report shape according to the request and evidence; do not force a fixed template.
- Tie every major result to task analyses and concrete output files from the evidence index.
- Include warnings, assumptions, partial coverage, failed items, and other limitations when present.
- Inspect full handoff JSON, analyses, or raw outputs only when the compact context is insufficient.
- Do not fabricate results, citations, or file paths.

</science_report_context_compact>
