<science_report_context>

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

## Planned Workflow
<experiment_plan>
# Goal
Build a reliable observational data foundation for the Aomori/Japan regional catalog, match the major earthquakes to the relocated catalog, characterize regional seismicity background and station/focal-mechanism context, generate publication-quality diagnostic figures, and prepare reusable Stage-1 products for downstream sequence analysis.

## Planning Assumptions
- Use observation data only: relocated regional catalog, major-earthquake reference table, source-mechanism catalog, and station inventory.
- Core data sources:
  - `catalog/Snet_catalog_relocate.csv`
  - `catalog/main_earthquake.csv`
  - `source_mechanism/Snet_mecha.csv`
  - `stations/station.sta`
- Package/workflow contracts relevant to implementation:
  - Tabular parsing must preserve raw columns and produce validated cleaned fields before any matching or statistical summaries.
  - Time parsing should use the file’s actual datetime/origin-time fields; do not infer temporal precision from decimal places.
  - Spatial matching and local-context summaries must use one consistent geographic distance method across the workflow.
  - Completeness magnitude Mc and Gutenberg–Richter b-value should be estimated from the cleaned catalog using a documented, data-driven magnitude binning and fitting range.
  - Focal-mechanism analysis must separate availability from mechanism-property analysis because coverage may be partial.
  - Success evidence requires non-empty cleaned tables, match tables, summary metrics, and saved figure files; diagnostic or fallback outputs are not sufficient.
- Stage-1 catalog requirements:
  - Preserve original values where valid.
  - Include parsed origin time, latitude, longitude, depth, magnitude, event ID if available, and explicit quality flags.
  - Keep a raw-audit view alongside cleaned outputs.
- Matching requirements:
  - Allow a small relocation-induced time shift, but require spatial and depth consistency.
  - If multiple candidates are close, flag ambiguity rather than forcing a match.
- Figure requirements:
  - Save Nature-style diagnostic figures as high-resolution PNG.
  - Use clear labels, units, legends, readable fonts, and consistent symbol/color conventions.

## Analysis Plan
### 1) Data audit and Stage-1 cleaning
- Task description:
  - Inspect all four files for schema, record counts, field names, missing values, duplicates, time/location/depth/magnitude ranges, abnormal values, and usable fields.
  - Construct a clean Stage-1 regional catalog from `catalog/Snet_catalog_relocate.csv`.
- Required data sources:
  - `catalog/Snet_catalog_relocate.csv`
  - `catalog/main_earthquake.csv`
  - `source_mechanism/Snet_mecha.csv`
  - `stations/station.sta`
- Parameter selection strategy:
  - Parse native time/origin-time fields from each file and validate against ordering and plausible regional date ranges.
  - Harmonize event tables to common fields: time, latitude, longitude, depth, magnitude, event ID, and source-specific metadata.
  - Flag missing essential fields, impossible coordinates, negative or excessive depths, abnormal magnitudes, parse failures, and exact or near-duplicate event signatures.
  - Preserve raw values and create deterministic surrogate IDs only when event IDs are absent or inconsistent.
- Constraints:
  - Do not silently drop records; retain audit evidence for all corrections and exclusions.
  - Do not infer field meaning from row order; verify by headers and value patterns.
  - Abnormal-value checks must be based on physical plausibility and catalog distribution, not decimal precision alone.
- Key outputs:
  - File-level audit summary tables
  - Clean Stage-1 catalog with quality flags
  - Duplicate and abnormal-value report
  - Field-mapping / usable-field summary

### 2) Major-earthquake matching
- Task description:
  - Match each major earthquake in `catalog/main_earthquake.csv` to the nearest event in the relocated regional catalog, accounting for small relocation-related time shifts.
  - Report nearest matched catalog event, time difference, spatial distance, depth difference, magnitude difference, and match confidence.
- Required data sources:
  - `catalog/main_earthquake.csv`
  - `catalog/Snet_catalog_relocate.csv`
  - Clean Stage-1 catalog from Task 1
- Parameter selection strategy:
  - Use a constrained candidate window centered on each reference origin time, then rank candidates by a composite criterion emphasizing time proximity first, followed by spatial distance, depth agreement, and magnitude agreement.
  - Store both the best match and the short candidate list for ambiguous cases.
  - Define confidence tiers from candidate uniqueness and multi-metric agreement.
- Constraints:
  - If no candidate is found in the primary window, widen cautiously and record the fallback rule used.
  - Do not assume the major event appears exactly in the relocated catalog.
  - Resolve ties explicitly and mark near-ties as ambiguous.
- Key outputs:
  - Major-earthquake match table with matched event ID, matched time, and all requested difference metrics
  - Candidate-ranking/ambiguity diagnostics
  - Match-confidence labels

### 3) Regional seismicity background characterization
- Task description:
  - Characterize the relocated regional catalog in terms of spatial distribution and event density, temporal activity rate, magnitude distribution, depth distribution and segmentation, magnitude–depth relationship, preliminary completeness magnitude Mc and b-value, station distribution and coverage metrics, and focal-mechanism feature availability/distribution.
- Required data sources:
  - `catalog/Snet_catalog_relocate.csv`
  - `source_mechanism/Snet_mecha.csv`
  - `stations/station.sta`
  - Clean Stage-1 catalog from Task 1
- Parameter selection strategy:
  - Use the full cleaned regional catalog for background statistics.
  - Choose temporal bins from catalog duration and event density so activity-rate variability is resolved without excessive smoothing.
  - Estimate Mc from the break in the frequency–magnitude relation and fit b-value over the linear tail above Mc using documented magnitude binning.
  - Derive depth segments from the empirical depth distribution and clearly state the segmentation rule.
  - Summarize station coverage with station density and event-to-station proximity metrics.
  - Separate focal-mechanism availability from geometry/statistics; analyze only records with usable mechanism fields.
- Constraints:
  - Report Mc and b-value as preliminary screening metrics, with the fitting range stated explicitly.
  - Do not mix full-catalog summaries with mechanism-subset summaries.
  - Use a single regional extent for all map-based background diagnostics.
- Key outputs:
  - Spatial density summaries
  - Temporal activity-rate summary
  - Magnitude histogram and frequency–magnitude distribution
  - Depth distribution and depth-bin summary
  - Magnitude–depth relationship summary
  - Preliminary Mc and b-value estimates
  - Station coverage metrics
  - Focal-mechanism availability and feature summary

### 4) Mainshock regional context assessment
- Task description:
  - For each major earthquake, summarize its local context: event density, surrounding depth distribution, nearby station distribution and coverage, nearby focal-mechanism availability, and whether it lies in a distinct spatial/depth domain.
  - Derive notes for later sequence-analysis thresholds.
- Required data sources:
  - `catalog/main_earthquake.csv`
  - `catalog/Snet_catalog_relocate.csv`
  - `source_mechanism/Snet_mecha.csv`
  - `stations/station.sta`
  - Match table from Task 2
- Parameter selection strategy:
  - Define local neighborhoods around each matched mainshock using data-driven radii and depth windows tied to regional event density and station spacing.
  - Compare local density and depth statistics against the full-catalog background.
  - Evaluate nearby station count and distance summaries relative to the local event cloud.
  - Quantify mechanism availability in the same neighborhood and compare with regional coverage.
- Constraints:
  - Keep neighborhood definitions explicit and reusable.
  - If a mainshock sits near the catalog edge, note edge effects in density and coverage metrics.
  - Treat sparse mechanism coverage as limited data availability, not as a physical absence.
- Key outputs:
  - Per-mainshock context table
  - Local-versus-regional contrast metrics
  - Suggested radius, depth, and magnitude screening notes for later sequence analysis

### 5) Diagnostic figure suite
- Task description:
  - Produce Nature-style publication-quality figures supporting audit, background characterization, and mainshock context assessment.
- Required data sources:
  - Clean Stage-1 catalog
  - Match table from Task 2
  - `source_mechanism/Snet_mecha.csv`
  - `stations/station.sta`
- Parameter selection strategy:
  - Use consistent geographic extents and symbol conventions across spatial figures.
  - Highlight major earthquakes consistently across all relevant panels.
  - Use binned or density-based representations for crowded event fields.
  - Show focal mechanisms only where usable geometry is available; otherwise show availability counts or density.
- Constraints:
  - Save figures as high-resolution PNG.
  - Ensure labels include units, legends are legible in print, and color scales remain interpretable.
  - Avoid overcrowding by using transparency, density aggregation, or multi-panel layouts.
- Key outputs:
  - Regional map of earthquakes, major earthquakes, stations, and focal mechanisms if available
  - Time–magnitude plot
  - Depth–time plot
  - Magnitude–depth plot
  - Magnitude-frequency / Mc plot / b-value plot
  - Spatial event-density or cluster diagnostic
  - Depth-distribution or cross-section diagnostic
  - Station coverage diagnostic
  - Focal-mechanism distribution and availability diagnostic
  - Any additional compact background plots that materially improve interpretability

### 6) Candidate patterns estimation
- Task description:
  - Convert the background and context results into compact, testable candidate patterns for later sequence analysis and hypothesis testing.
- Required data sources:
  - Outputs from Tasks 1–4
  - Clean Stage-1 catalog
  - Match table
  - Station summary
  - Mechanism summary
- Parameter selection strategy:
  - Identify spatial clusters from density anomalies or localized concentration.
  - Identify temporal bursts or quiet periods from rate deviations.
  - Detect depth segmentation from layered or bimodal depth distributions.
  - Examine magnitude–depth–space relationships for regional contrasts.
  - Assess station-coverage gradients and focal-mechanism data gaps as possible sampling biases.
  - Compare each mainshock neighborhood with regional background to derive event-specific candidate thresholds.
- Constraints:
  - Keep patterns observational and falsifiable; do not over-interpret mechanisms.
  - Separate catalog-wide patterns from mainshock-specific patterns.
- Key outputs:
  - Ranked candidate-pattern list
  - Suggested follow-up thresholds or masks for sequence analysis
  - Machine-readable summary table for downstream use

### Execution flow and dependencies
- Execute Task 1 first to produce the cleaned Stage-1 catalog and quality-flagged audit outputs.
- Use the cleaned Stage-1 catalog in Tasks 2–6 for all matching, summary statistics, and plotting.
- Use Task 2 outputs to anchor mainshock-specific analyses in Task 4.
- Use Task 3 outputs to define background comparison ranges and guide figure design in Task 5.
- Validate that the cleaned catalog is non-empty and that all expected major earthquakes have either a confident match or an explicitly flagged ambiguous/unmatched status before finalizing derived products.
</experiment_plan>

## Implementation Trace
- Task: 01_data_audit_cleaning
  Description: Audit all source files and build a validated Stage-1 cleaned regional catalog with quality flags.
  Ancestors: none
  Handoff JSON: <CASE_ROOT>/run/01_data_foundation/exp_run/log/coding_progress/task_handoff/01_data_audit_cleaning.json
  Output directory: <CASE_ROOT>/run/01_data_foundation/exp_run/outputs/01_data_audit_cleaning
  Analysis file: <CASE_ROOT>/run/01_data_foundation/exp_run/analysis/01_data_audit_cleaning.md
- Task: 02_major_earthquake_matching
  Description: Match major earthquakes to the relocated catalog and quantify match confidence and differences.
  Ancestors: 01_data_audit_cleaning
  Handoff JSON: <CASE_ROOT>/run/01_data_foundation/exp_run/log/coding_progress/task_handoff/02_major_earthquake_matching.json
  Output directory: <CASE_ROOT>/run/01_data_foundation/exp_run/outputs/02_major_earthquake_matching
  Analysis file: <CASE_ROOT>/run/01_data_foundation/exp_run/analysis/02_major_earthquake_matching.md
- Task: 03_regional_background_characterization
  Description: Characterize regional seismicity background, station coverage, and mechanism availability from the cleaned catalog.
  Ancestors: 01_data_audit_cleaning
  Handoff JSON: <CASE_ROOT>/run/01_data_foundation/exp_run/log/coding_progress/task_handoff/03_regional_background_characterization.json
  Output directory: <CASE_ROOT>/run/01_data_foundation/exp_run/outputs/03_regional_background_characterization
  Analysis file: <CASE_ROOT>/run/01_data_foundation/exp_run/analysis/03_regional_background_characterization.md
- Task: 04_mainshock_regional_context
  Description: Summarize local catalog, station, and mechanism context around each major earthquake.
  Ancestors: 01_data_audit_cleaning, 02_major_earthquake_matching, 03_regional_background_characterization
  Handoff JSON: <CASE_ROOT>/run/01_data_foundation/exp_run/log/coding_progress/task_handoff/04_mainshock_regional_context.json
  Output directory: <CASE_ROOT>/run/01_data_foundation/exp_run/outputs/04_mainshock_regional_context
  Analysis file: <CASE_ROOT>/run/01_data_foundation/exp_run/analysis/04_mainshock_regional_context.md
- Task: 05_diagnostic_figures
  Description: Generate Nature-style high-resolution diagnostic figures for audit, background, and context analysis.
  Ancestors: 01_data_audit_cleaning, 02_major_earthquake_matching, 03_regional_background_characterization, 04_mainshock_regional_context
  Handoff JSON: <CASE_ROOT>/run/01_data_foundation/exp_run/log/coding_progress/task_handoff/05_diagnostic_figures.json
  Output directory: <CASE_ROOT>/run/01_data_foundation/exp_run/outputs/05_diagnostic_figures
  Analysis file: <CASE_ROOT>/run/01_data_foundation/exp_run/analysis/05_diagnostic_figures.md
- Task: 06_candidate_patterns_estimation
  Description: Convert background and context results into ranked candidate patterns and follow-up analysis suggestions.
  Ancestors: 01_data_audit_cleaning, 02_major_earthquake_matching, 03_regional_background_characterization, 04_mainshock_regional_context
  Handoff JSON: <CASE_ROOT>/run/01_data_foundation/exp_run/log/coding_progress/task_handoff/06_candidate_patterns_estimation.json
  Output directory: <CASE_ROOT>/run/01_data_foundation/exp_run/outputs/06_candidate_patterns_estimation
  Analysis file: <CASE_ROOT>/run/01_data_foundation/exp_run/analysis/06_candidate_patterns_estimation.md

## Result Evidence Index
Use handoff JSON files as compact indexes to important outputs. Use per-task analyses for scientific interpretation. Inspect raw outputs only when the handoff and analysis are insufficient.
<task_evidence task="01_data_audit_cleaning">
Handoff JSON: <CASE_ROOT>/run/01_data_foundation/exp_run/log/coding_progress/task_handoff/01_data_audit_cleaning.json
{
  "meta": {
    "schema_version": 2,
    "type": "coding_task_handoff",
    "task": "01_data_audit_cleaning",
    "generated_at": "2026-05-23T02:20:05.465285+00:00"
  },
  "status": {
    "state": "success",
    "stage": "analysis_done",
    "elapsed_sec": 500.87,
    "timing": {
      "total_sec": 500.87,
      "coding_agent_sec": 174.024,
      "code_review_sec": 90.232,
      "preflight_sec": 0.407,
      "script_execution_sec": 22.099,
      "result_check_sec": 151.709,
      "task_analysis_sec": 60.692
    },
    "quality_flags": [
      "task_status:success"
    ]
  },
  "paths": {
    "root": "<CASE_ROOT>/run/01_data_foundation",
    "script": "<CASE_ROOT>/run/01_data_foundation/exp_run/scripts/01_data_audit_cleaning.py",
    "output_dir": "<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/01_data_audit_cleaning",
    "analysis": "<CASE_ROOT>/run/01_data_foundation/exp_run/analysis/01_data_audit_cleaning.md",
    "log": "<CASE_ROOT>/run/01_data_foundation/exp_run/log/task/01_data_audit_cleaning/log_0.txt"
  },
  "outputs": {
    "primary": [
      {
        "path": "abnormal_value_report.csv",
        "absolute_path": "<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/01_data_audit_cleaning/abnormal_value_report.csv",
        "kind": "machine_readable"
      },
      {
        "path": "duplicate_signature_report.csv",
        "absolute_path": "<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/01_data_audit_cleaning/duplicate_signature_report.csv",
        "kind": "machine_readable"
      },
      {
        "path": "field_mapping_summary.csv",
        "absolute_path": "<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/01_data_audit_cleaning/field_mapping_summary.csv",
        "kind": "machine_readable"
      },
      {
        "path": "file_level_audit_summary.csv",
        "absolute_path": "<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/01_data_audit_cleaning/file_level_audit_summary.csv",
        "kind": "machine_readable"
      },
      {
        "path": "main_earthquake_clean.csv",
        "absolute_path": "<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/01_data_audit_cleaning/main_earthquake_clean.csv",
        "kind": "machine_readable"
      },
      {
        "path": "main_earthquake_numeric_summary.csv",
        "absolute_path": "<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/01_data_audit_cleaning/main_earthquake_numeric_summary.csv",
        "kind": "machine_readable"
      },
      {
        "path": "mechanism_summary.csv",
        "absolute_path": "<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/01_data_audit_cleaning/mechanism_summary.csv",
        "kind": "machine_readable"
      },
      {
        "path": "quality_summary.csv",
        "absolute_path": "<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/01_data_audit_cleaning/quality_summary.csv",
        "kind": "machine_readable"
      }
    ],
    "all": [
      "abnormal_value_report.csv",
      "duplicate_signature_report.csv",
      "field_mapping_summary.csv",
      "file_level_audit_summary.csv",
      "main_earthquake_clean.csv",
      "main_earthquake_numeric_summary.csv",
      "mechanism_summary.csv",
      "quality_summary.csv",
      "regional_catalog_numeric_summary.csv",
      "source_mechanism_clean.csv",
      "stage1_regional_catalog_clean.csv",
      "station_clean.csv",
      "station_summary.csv"
    ],
    "truncated": false
  },
  "notes": {
    "purpose": "Audit all source files and build a validated Stage-1 cleaned regional catalog with quality flags.",
    "result": "Audit all source files and build a validated Stage-1 cleaned regional catalog with quality flags. Status=success; outputs=13 discovered; primary=8.",
    "warnings": [],
    "assumptions": [],
    "limitations": []
  }
}
</task_evidence>

<task_evidence task="02_major_earthquake_matching">
Handoff JSON: <CASE_ROOT>/run/01_data_foundation/exp_run/log/coding_progress/task_handoff/02_major_earthquake_matching.json
{
  "meta": {
    "schema_version": 2,
    "type": "coding_task_handoff",
    "task": "02_major_earthquake_matching",
    "generated_at": "2026-05-23T02:20:05.471620+00:00"
  },
  "status": {
    "state": "success",
    "stage": "analysis_done",
    "elapsed_sec": 899.606,
    "timing": {
      "total_sec": 899.606,
      "coding_agent_sec": 419.144,
      "code_review_sec": 299.949,
      "preflight_sec": 0.54,
      "script_execution_sec": 40.246,
      "result_check_sec": 55.022,
      "task_analysis_sec": 81.722
    },
    "quality_flags": [
      "task_status:success"
    ]
  },
  "paths": {
    "root": "<CASE_ROOT>/run/01_data_foundation",
    "script": "<CASE_ROOT>/run/01_data_foundation/exp_run/scripts/02_major_earthquake_matching.py",
    "output_dir": "<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/02_major_earthquake_matching",
    "analysis": "<CASE_ROOT>/run/01_data_foundation/exp_run/analysis/02_major_earthquake_matching.md",
    "log": "<CASE_ROOT>/run/01_data_foundation/exp_run/log/task/02_major_earthquake_matching/log_1.txt"
  },
  "outputs": {
    "primary": [
      {
        "path": "major_earthquake_candidates.csv",
        "absolute_path": "<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/02_major_earthquake_matching/major_earthquake_candidates.csv",
        "kind": "machine_readable"
      },
      {
        "path": "major_earthquake_match_summary.csv",
        "absolute_path": "<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/02_major_earthquake_matching/major_earthquake_match_summary.csv",
        "kind": "machine_readable"
      },
      {
        "path": "major_earthquake_matches.csv",
        "absolute_path": "<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/02_major_earthquake_matching/major_earthquake_matches.csv",
        "kind": "machine_readable"
      }
    ],
    "all": [
      "major_earthquake_candidates.csv",
      "major_earthquake_match_summary.csv",
      "major_earthquake_matches.csv"
    ],
    "truncated": false
  },
  "notes": {
    "purpose": "Match major earthquakes to the relocated catalog and quantify match confidence and differences.",
    "result": "Match major earthquakes to the relocated catalog and quantify match confidence and differences. Status=success; outputs=3 discovered; primary=3.",
    "warnings": [],
    "assumptions": [],
    "limitations": []
  }
}
</task_evidence>

<task_evidence task="03_regional_background_characterization">
Handoff JSON: <CASE_ROOT>/run/01_data_foundation/exp_run/log/coding_progress/task_handoff/03_regional_background_characterization.json
{
  "meta": {
    "schema_version": 2,
    "type": "coding_task_handoff",
    "task": "03_regional_background_characterization",
    "generated_at": "2026-05-23T02:20:05.478382+00:00"
  },
  "status": {
    "state": "success",
    "stage": "analysis_done",
    "elapsed_sec": 2699.301,
    "timing": {
      "total_sec": 2699.301,
      "coding_agent_sec": 434.248,
      "code_review_sec": 122.398,
      "preflight_sec": 1.135,
      "script_execution_sec": 91.351,
      "result_check_sec": 240.511,
      "task_analysis_sec": 1805.712
    },
    "quality_flags": [
      "task_status:success",
      "outputs_truncated"
    ]
  },
  "paths": {
    "root": "<CASE_ROOT>/run/01_data_foundation",
    "script": "<CASE_ROOT>/run/01_data_foundation/exp_run/scripts/03_regional_background_characterization.py",
    "output_dir": "<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/03_regional_background_characterization",
    "analysis": "<CASE_ROOT>/run/01_data_foundation/exp_run/analysis/03_regional_background_characterization.md",
    "log": "<CASE_ROOT>/run/01_data_foundation/exp_run/log/task/03_regional_background_characterization/log_2.txt"
  },
  "outputs": {
    "primary": [
      {
        "path": "depth_segmentation_summary.csv",
        "absolute_path": "<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/03_regional_background_characterization/depth_segmentation_summary.csv",
        "kind": "machine_readable"
      },
      {
        "path": "depth_summary_stats.csv",
        "absolute_path": "<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/03_regional_background_characterization/depth_summary_stats.csv",
        "kind": "machine_readable"
      },
      {
        "path": "magnitude_summary_stats.csv",
        "absolute_path": "<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/03_regional_background_characterization/magnitude_summary_stats.csv",
        "kind": "machine_readable"
      },
      {
        "path": "mc_bvalue_estimate.csv",
        "absolute_path": "<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/03_regional_background_characterization/mc_bvalue_estimate.csv",
        "kind": "machine_readable"
      },
      {
        "path": "mechanism_availability_metrics.csv",
        "absolute_path": "<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/03_regional_background_characterization/mechanism_availability_metrics.csv",
        "kind": "machine_readable"
      },
      {
        "path": "mechanism_background_clean.csv",
        "absolute_path": "<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/03_regional_background_characterization/mechanism_background_clean.csv",
        "kind": "machine_readable"
      },
      {
        "path": "mechanism_subset_joined_to_catalog.csv",
        "absolute_path": "<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/03_regional_background_characterization/mechanism_subset_joined_to_catalog.csv",
        "kind": "machine_readable"
      },
      {
        "path": "regional_background_summary.csv",
        "absolute_path": "<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/03_regional_background_characterization/regional_background_summary.csv",
        "kind": "machine_readable"
      }
    ],
    "all": [
      "depth_segmentation_summary.csv",
      "depth_summary_stats.csv",
      "figure_depth_distribution.png",
      "figure_depth_time.png",
      "figure_magnitude_depth.png",
      "figure_mechanism_availability.png",
      "figure_mfd_mc_bvalue.png",
      "figure_regional_map.png",
      "figure_spatial_density.png",
      "figure_station_coverage.png",
      "figure_time_magnitude.png",
      "magnitude_summary_stats.csv",
      "mc_bvalue_estimate.csv",
      "mechanism_availability_metrics.csv",
      "mechanism_background_clean.csv",
      "mechanism_subset_joined_to_catalog.csv",
      "regional_background_summary.csv",
      "regional_catalog_background_clean.csv",
      "station_background_clean.csv",
      "station_coverage_metrics.csv",
      "temporal_activity_rate_90d.csv"
    ],
    "truncated": true
  },
  "notes": {
    "purpose": "Characterize regional seismicity background, station coverage, and mechanism availability from the cleaned catalog.",
    "result": "Characterize regional seismicity background, station coverage, and mechanism availability from the cleaned catalog. Status=success; outputs=21 discovered; primary=8.",
    "warnings": [],
    "assumptions": [],
    "limitations": []
  }
}
</task_evidence>

<task_evidence task="04_mainshock_regional_context">
Handoff JSON: <CASE_ROOT>/run/01_data_foundation/exp_run/log/coding_progress/task_handoff/04_mainshock_regional_context.json
{
  "meta": {
    "schema_version": 2,
    "type": "coding_task_handoff",
    "task": "04_mainshock_regional_context",
    "generated_at": "2026-05-23T02:20:05.488263+00:00"
  },
  "status": {
    "state": "success",
    "stage": "analysis_done",
    "elapsed_sec": 779.27,
    "timing": {
      "total_sec": 779.27,
      "coding_agent_sec": 165.478,
      "code_review_sec": 101.709,
      "preflight_sec": 0.307,
      "script_execution_sec": 25.129,
      "result_check_sec": 53.065,
      "task_analysis_sec": 430.778
    },
    "quality_flags": [
      "task_status:success"
    ]
  },
  "paths": {
    "root": "<CASE_ROOT>/run/01_data_foundation",
    "script": "<CASE_ROOT>/run/01_data_foundation/exp_run/scripts/04_mainshock_regional_context.py",
    "output_dir": "<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/04_mainshock_regional_context",
    "analysis": "<CASE_ROOT>/run/01_data_foundation/exp_run/analysis/04_mainshock_regional_context.md",
    "log": "<CASE_ROOT>/run/01_data_foundation/exp_run/log/task/04_mainshock_regional_context/log_0.txt"
  },
  "outputs": {
    "primary": [
      {
        "path": "mainshock_context_summary.csv",
        "absolute_path": "<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/04_mainshock_regional_context/mainshock_context_summary.csv",
        "kind": "machine_readable"
      },
      {
        "path": "mainshock_local_catalog_windows.csv",
        "absolute_path": "<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/04_mainshock_regional_context/mainshock_local_catalog_windows.csv",
        "kind": "machine_readable"
      },
      {
        "path": "mainshock_local_station_windows.csv",
        "absolute_path": "<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/04_mainshock_regional_context/mainshock_local_station_windows.csv",
        "kind": "machine_readable"
      },
      {
        "path": "regional_context_overview.csv",
        "absolute_path": "<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/04_mainshock_regional_context/regional_context_overview.csv",
        "kind": "machine_readable"
      },
      {
        "path": "sequence_threshold_notes.csv",
        "absolute_path": "<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/04_mainshock_regional_context/sequence_threshold_notes.csv",
        "kind": "machine_readable"
      },
      {
        "path": "figure_mainshock_context_panels.png",
        "absolute_path": "<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/04_mainshock_regional_context/figure_mainshock_context_panels.png",
        "kind": "figure"
      },
      {
        "path": "figure_mainshock_regional_context_map.png",
        "absolute_path": "<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/04_mainshock_regional_context/figure_mainshock_regional_context_map.png",
        "kind": "figure"
      }
    ],
    "all": [
      "figure_mainshock_context_panels.png",
      "figure_mainshock_regional_context_map.png",
      "mainshock_context_summary.csv",
      "mainshock_local_catalog_windows.csv",
      "mainshock_local_station_windows.csv",
      "regional_context_overview.csv",
      "sequence_threshold_notes.csv"
    ],
    "truncated": false
  },
  "notes": {
    "purpose": "Summarize local catalog, station, and mechanism context around each major earthquake.",
    "result": "Summarize local catalog, station, and mechanism context around each major earthquake. Status=success; outputs=7 discovered; primary=7.",
    "warnings": [],
    "assumptions": [],
    "limitations": []
  }
}
</task_evidence>

<task_evidence task="05_diagnostic_figures">
Handoff JSON: <CASE_ROOT>/run/01_data_foundation/exp_run/log/coding_progress/task_handoff/05_diagnostic_figures.json
{
  "meta": {
    "schema_version": 2,
    "type": "coding_task_handoff",
    "task": "05_diagnostic_figures",
    "generated_at": "2026-05-23T02:20:05.498031+00:00"
  },
  "status": {
    "state": "success",
    "stage": "analysis_done",
    "elapsed_sec": 2137.234,
    "timing": {
      "total_sec": 2137.234,
      "coding_agent_sec": 524.456,
      "code_review_sec": 179.022,
      "preflight_sec": 1.649,
      "script_execution_sec": 117.525,
      "result_check_sec": 284.957,
      "task_analysis_sec": 1024.437
    },
    "quality_flags": [
      "task_status:success"
    ]
  },
  "paths": {
    "root": "<CASE_ROOT>/run/01_data_foundation",
    "script": "<CASE_ROOT>/run/01_data_foundation/exp_run/scripts/05_diagnostic_figures.py",
    "output_dir": "<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/05_diagnostic_figures",
    "analysis": "<CASE_ROOT>/run/01_data_foundation/exp_run/analysis/05_diagnostic_figures.md",
    "log": "<CASE_ROOT>/run/01_data_foundation/exp_run/log/task/05_diagnostic_figures/log_2.txt"
  },
  "outputs": {
    "primary": [
      {
        "path": "figure_manifest.csv",
        "absolute_path": "<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/05_diagnostic_figures/figure_manifest.csv",
        "kind": "machine_readable"
      },
      {
        "path": "figure_01_regional_map.png",
        "absolute_path": "<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/05_diagnostic_figures/figure_01_regional_map.png",
        "kind": "figure"
      },
      {
        "path": "figure_02_time_magnitude.png",
        "absolute_path": "<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/05_diagnostic_figures/figure_02_time_magnitude.png",
        "kind": "figure"
      },
      {
        "path": "figure_03_depth_time.png",
        "absolute_path": "<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/05_diagnostic_figures/figure_03_depth_time.png",
        "kind": "figure"
      },
      {
        "path": "figure_04_magnitude_depth.png",
        "absolute_path": "<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/05_diagnostic_figures/figure_04_magnitude_depth.png",
        "kind": "figure"
      },
      {
        "path": "figure_05_magnitude_frequency_mc_bvalue.png",
        "absolute_path": "<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/05_diagnostic_figures/figure_05_magnitude_frequency_mc_bvalue.png",
        "kind": "figure"
      },
      {
        "path": "figure_06_spatial_density.png",
        "absolute_path": "<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/05_diagnostic_figures/figure_06_spatial_density.png",
        "kind": "figure"
      },
      {
        "path": "figure_07_depth_distribution.png",
        "absolute_path": "<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/05_diagnostic_figures/figure_07_depth_distribution.png",
        "kind": "figure"
      }
    ],
    "all": [
      "figure_01_regional_map.png",
      "figure_02_time_magnitude.png",
      "figure_03_depth_time.png",
      "figure_04_magnitude_depth.png",
      "figure_05_magnitude_frequency_mc_bvalue.png",
      "figure_06_spatial_density.png",
      "figure_07_depth_distribution.png",
      "figure_08_depth_cross_section.png",
      "figure_09_station_coverage.png",
      "figure_10_mechanism_diagnostics.png",
      "figure_11_mainshock_context_overview.png",
      "figure_manifest.csv"
    ],
    "truncated": false
  },
  "notes": {
    "purpose": "Generate Nature-style high-resolution diagnostic figures for audit, background, and context analysis.",
    "result": "Generate Nature-style high-resolution diagnostic figures for audit, background, and context analysis. Status=success; outputs=12 discovered; primary=8.",
    "warnings": [],
    "assumptions": [],
    "limitations": []
  }
}
</task_evidence>

<task_evidence task="06_candidate_patterns_estimation">
Handoff JSON: <CASE_ROOT>/run/01_data_foundation/exp_run/log/coding_progress/task_handoff/06_candidate_patterns_estimation.json
{
  "meta": {
    "schema_version": 2,
    "type": "coding_task_handoff",
    "task": "06_candidate_patterns_estimation",
    "generated_at": "2026-05-23T02:20:05.505595+00:00"
  },
  "status": {
    "state": "success",
    "stage": "analysis_done",
    "elapsed_sec": 1126.733,
    "timing": {
      "total_sec": 1126.733,
      "coding_agent_sec": 355.077,
      "code_review_sec": 268.072,
      "preflight_sec": 0.74,
      "script_execution_sec": 52.327,
      "result_check_sec": 207.386,
      "task_analysis_sec": 239.176
    },
    "quality_flags": [
      "task_status:success"
    ]
  },
  "paths": {
    "root": "<CASE_ROOT>/run/01_data_foundation",
    "script": "<CASE_ROOT>/run/01_data_foundation/exp_run/scripts/06_candidate_patterns_estimation.py",
    "output_dir": "<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/06_candidate_patterns_estimation",
    "analysis": "<CASE_ROOT>/run/01_data_foundation/exp_run/analysis/06_candidate_patterns_estimation.md",
    "log": "<CASE_ROOT>/run/01_data_foundation/exp_run/log/task/06_candidate_patterns_estimation/log_1.txt"
  },
  "outputs": {
    "primary": [
      {
        "path": "background_summary_snapshot.csv",
        "absolute_path": "<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/06_candidate_patterns_estimation/background_summary_snapshot.csv",
        "kind": "machine_readable"
      },
      {
        "path": "candidate_patterns_ranked.csv",
        "absolute_path": "<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/06_candidate_patterns_estimation/candidate_patterns_ranked.csv",
        "kind": "machine_readable"
      },
      {
        "path": "candidate_patterns_summary.csv",
        "absolute_path": "<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/06_candidate_patterns_estimation/candidate_patterns_summary.csv",
        "kind": "machine_readable"
      },
      {
        "path": "followup_analysis_suggestions.csv",
        "absolute_path": "<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/06_candidate_patterns_estimation/followup_analysis_suggestions.csv",
        "kind": "machine_readable"
      },
      {
        "path": "mainshock_context_snapshot.csv",
        "absolute_path": "<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/06_candidate_patterns_estimation/mainshock_context_snapshot.csv",
        "kind": "machine_readable"
      },
      {
        "path": "figure_candidate_patterns_ranked.png",
        "absolute_path": "<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/06_candidate_patterns_estimation/figure_candidate_patterns_ranked.png",
        "kind": "figure"
      },
      {
        "path": "figure_mainshock_context_overview.png",
        "absolute_path": "<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/06_candidate_patterns_estimation/figure_mainshock_context_overview.png",
        "kind": "figure"
      }
    ],
    "all": [
      "background_summary_snapshot.csv",
      "candidate_patterns_ranked.csv",
      "candidate_patterns_summary.csv",
      "figure_candidate_patterns_ranked.png",
      "figure_mainshock_context_overview.png",
      "followup_analysis_suggestions.csv",
      "mainshock_context_snapshot.csv"
    ],
    "truncated": false
  },
  "notes": {
    "purpose": "Convert background and context results into ranked candidate patterns and follow-up analysis suggestions.",
    "result": "Convert background and context results into ranked candidate patterns and follow-up analysis suggestions. Status=success; outputs=7 discovered; primary=7.",
    "warnings": [],
    "assumptions": [],
    "limitations": []
  }
}
</task_evidence>


## Per-Task Scientific Analyses
<task_analysis>
Task: 01_data_audit_cleaning
Description: Audit all source files and build a validated Stage-1 cleaned regional catalog with quality flags.
Analysis file: <CASE_ROOT>/run/01_data_foundation/exp_run/analysis/01_data_audit_cleaning.md
Output directory: <CASE_ROOT>/run/01_data_foundation/exp_run/outputs/01_data_audit_cleaning

## Scientific Purpose

This task established the data foundation for the Japan Aomori catalog analysis by auditing all source files, standardizing the regional seismicity catalog into a validated Stage-1 product, and generating quality-control evidence for later sequence and background-seismicity analyses. The primary scientific goal here was to ensure that the earthquake catalog, focal-mechanism file, and station metadata are internally consistent, free of obvious data errors, and sufficiently complete for downstream spatial, temporal, and magnitude-depth characterization.

## Method and Implementation Evidence

The implementation produced a file-level audit, field mapping, numeric summaries, abnormal-value and duplicate checks, and cleaned machine-readable products for the regional catalog, major earthquakes, focal mechanisms, and stations. Evidence of the implemented workflow is contained in:

- `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/01_data_audit_cleaning/file_level_audit_summary.csv`
- `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/01_data_audit_cleaning/field_mapping_summary.csv`
- `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/01_data_audit_cleaning/quality_summary.csv`
- `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/01_data_audit_cleaning/stage1_regional_catalog_clean.csv`

The cleaned Stage-1 catalog includes parsed origin time, latitude, longitude, depth, magnitude, event identifiers where available, and Boolean quality flags. For the mechanism and station datasets, the workflow created cleaned derivatives with standardized fields and availability flags:

- `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/01_data_audit_cleaning/source_mechanism_clean.csv`
- `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/01_data_audit_cleaning/station_clean.csv`

The audit also generated supporting QC tables for numeric distributions, anomalies, and duplicates:

- `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/01_data_audit_cleaning/regional_catalog_numeric_summary.csv`
- `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/01_data_audit_cleaning/main_earthquake_numeric_summary.csv`
- `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/01_data_audit_cleaning/abnormal_value_report.csv`
- `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/01_data_audit_cleaning/duplicate_signature_report.csv`
- `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/01_data_audit_cleaning/mechanism_summary.csv`
- `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/01_data_audit_cleaning/station_summary.csv`

## Key Results and Evidence Files

### 1) Source-file audit and schema coverage
The audit covered four input files, of which three are substantive scientific datasets and one is a station metadata file. The file-level summary shows:

- `Snet_catalog_relocate.csv`: 25,646 records, 5 columns, full time parse success
- `main_earthquake.csv`: 3 records, 6 columns, full time parse success
- `Snet_mecha.csv`: 354 records, 29 columns, full time parse success
- Station file was processed separately into cleaned station metadata

Evidence:
- `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/01_data_audit_cleaning/file_level_audit_summary.csv`
- `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/01_data_audit_cleaning/field_mapping_summary.csv`

### 2) Clean Stage-1 regional catalog
The cleaned regional catalog contains 25,646 events and appears fully valid under the implemented screening rules. The quality table reports:

- 25,646 clean records
- 0 issue records
- 0 duplicate signatures
- 0 time parse failures
- 0 latitude, longitude, depth, or magnitude out-of-bounds values

Evidence:
- `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/01_data_audit_cleaning/quality_summary.csv`
- `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/01_data_audit_cleaning/stage1_regional_catalog_clean.csv`

The regional numeric summary indicates the catalog spans a broad but coherent seismic envelope:

- Latitude: 38.503 to 42.383
- Longitude: 141.002 to 144.498
- Depth: 0.05 to 121.14 km
- Magnitude: -0.5 to 7.7
- Median depth 15.65 km and median magnitude 1.5

Evidence:
- `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/01_data_audit_cleaning/regional_catalog_numeric_summary.csv`

### 3) Major-earthquake file and regional context data
The major-earthquake file contains 3 events, all parsed successfully and without QC issues. Their magnitude range is large, with mean magnitude 7.37 and values from 6.9 to 7.7. Their depths range from 15.9 to 53.5 km.

Evidence:
- `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/01_data_audit_cleaning/main_earthquake_clean.csv`
- `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/01_data_audit_cleaning/main_earthquake_numeric_summary.csv`

### 4) Focal-mechanism dataset completeness
The mechanism catalog contains 354 events, all with parseable origin times and complete hypocenter coordinates and depth values. Only 139 records have core mechanism availability and geometry availability, indicating that focal-mechanism coverage is substantially lower than hypocentral coverage.

Evidence:
- `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/01_data_audit_cleaning/mechanism_summary.csv`
- `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/01_data_audit_cleaning/source_mechanism_clean.csv`

A sample of the cleaned mechanism table shows retained fields for event code, time, hypocenter, two magnitude estimates, nodal planes, principal axes, focal mechanism score, and station-count support, which is suitable for later mechanism-based analysis.

Evidence:
- `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/01_data_audit_cleaning/source_mechanism_clean.csv`

### 5) Station network coverage
The station metadata contains 371 stations, all matched in the cleaned file. The network spans:

- Latitude: 36.880833 to 44.118833
- Longitude: 139.245333 to 145.738833
- Elevation: -6680 to 1205 m

This indicates a geographically broad observational footprint relative to the catalog area, with both land and strongly negative elevation values present, consistent with mixed terrestrial/oceanic station deployments or encoded bathymetric elevations.

Evidence:
- `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/01_data_audit_cleaning/station_summary.csv`
- `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/01_data_audit_cleaning/station_clean.csv`

### 6) Data-quality screening outcome
The abnormal-value and duplicate-signature reports are empty, which means no records were flagged for the implemented range checks or exact-signature duplication criteria.

Evidence:
- `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/01_data_audit_cleaning/abnormal_value_report.csv`
- `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/01_data_audit_cleaning/duplicate_signature_report.csv`

## Limitations and Assumptions

- No output images or PDFs were present in the task output directory, so no figure-specific analysis was possible for this task stage.
- The cleaned catalog quality assessment is based on implemented schema parsing and range checks; it does not by itself validate catalog completeness against the true seismic record or confirm that all events are physically unique.
- `main_earthquake.csv` contains only 3 events, so any later regional-context interpretation must treat this as a very small sample.
- The station file summary indicates broad network coverage, but station-response, temporal availability, and per-event azimuthal gap were not evaluated in this task.
- Focal-mechanism coverage is partial: only 139 of 354 mechanism records have core mechanism availability and geometry availability, so later mechanism-based analysis should explicitly handle missingness.
- The task handoff reports success and no warnings, but several downstream scientific metrics requested in the overall project goal—such as matching major earthquakes to relocated catalog events, completeness magnitude, b-value, spatial clustering, and figure generation—belong to later tasks and are not yet available here.

## Report-Ready Summary

This task successfully built a validated Stage-1 seismicity foundation for the Japan Aomori analysis. The regional relocated catalog is clean, large, and internally consistent, with 25,646 events, full time parsing, no detected duplicates, and no out-of-range coordinate/depth/magnitude values. The major-earthquake file was parsed cleanly but contains only 3 events, requiring careful treatment in subsequent matching and contextual analyses. The focal-mechanism dataset is usable but incomplete, with only 139 records carrying core mechanism/geometry availability, and the station network is broad, with 371 matched stations spanning a large latitudinal and longitudinal range. The most important reusable outputs for later stages are the cleaned catalog, cleaned mechanism and station tables, and the quality, numeric-summary, abnormal-value, and duplicate reports stored in `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/01_data_audit_cleaning/`.
</task_analysis>

<task_analysis>
Task: 02_major_earthquake_matching
Description: Match major earthquakes to the relocated catalog and quantify match confidence and differences.
Analysis file: <CASE_ROOT>/run/01_data_foundation/exp_run/analysis/02_major_earthquake_matching.md
Output directory: <CASE_ROOT>/run/01_data_foundation/exp_run/outputs/02_major_earthquake_matching

## Scientific Purpose

This task established the direct correspondence between the listed major earthquakes and the relocated regional catalog, so that subsequent regional-background and sequence-analysis steps can anchor each mainshock to a single catalog event with quantified uncertainty. The output supports later work on mainshock-centered spatial windows, temporal alignment, and magnitude/depth comparisons.

## Method and Implementation Evidence

The implemented matching workflow used the major-earthquake reference file and searched the relocated catalog within a time window large enough to accommodate small relocation-related shifts. For each reference earthquake, the nearest catalog event was selected using time proximity, with spatial and depth differences then computed as match diagnostics.

Evidence of implementation and resulting products:
- Matching summary: `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/02_major_earthquake_matching/major_earthquake_match_summary.csv`
- Matched-event table: `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/02_major_earthquake_matching/major_earthquake_matches.csv`
- Candidate list used for ranking/match selection: `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/02_major_earthquake_matching/major_earthquake_candidates.csv`

The match table includes:
- reference and matched event IDs
- original and matched origin times
- latitude, longitude, depth, and magnitude
- time difference, hypocentral distance, depth difference, and magnitude difference
- candidate count, search window, confidence, tie flag, and match note

## Key Results and Evidence Files

### 1) All major earthquakes were matched successfully
The summary table reports:
- major_event_count = 3
- matched_count = 3
- unmatched_count = 0
- confidence_high = 3

Evidence:
- `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/02_major_earthquake_matching/major_earthquake_match_summary.csv`

### 2) Matches are extremely tight in time and space
The median absolute time difference is 0.01 s, median distance is 0.165606 km, median depth difference is 0.09 km, and median magnitude difference is 0.0.

Per-event matched differences:
- M1 → CAT_001427: time_diff_sec = -0.01, distance_km = 0.165606, depth_diff_km = 0.09, mag_diff = 0.0
- M2 → CAT_004910: time_diff_sec = 0.00, distance_km = 0.296549, depth_diff_km = -0.04, mag_diff = 0.0
- M3 → CAT_018070: time_diff_sec = -0.01, distance_km = 0.157941, depth_diff_km = -0.09, mag_diff = 0.0

Evidence:
- `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/02_major_earthquake_matching/major_earthquake_matches.csv`

### 3) Match confidence is high for all three earthquakes
Each mainshock has:
- candidate_count > 280
- confidence = high
- tie_flag = False

This indicates that, although many catalog events were present in the search window, the chosen match was unambiguous after ranking by the matching criteria.

Evidence:
- `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/02_major_earthquake_matching/major_earthquake_matches.csv`

### 4) The matched catalog and reference events are effectively equivalent at the resolution of this analysis
The magnitude differences are exactly 0.0 for all three matches, and the time/depth offsets are sub-second and sub-kilometer. This is consistent with a relocated catalog that preserves the mainshock identity while slightly shifting origin estimates.

Evidence:
- `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/02_major_earthquake_matching/major_earthquake_matches.csv`
- `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/02_major_earthquake_matching/major_earthquake_match_summary.csv`

## Limitations and Assumptions

- No image or PDF products were present in this task output directory, so there are no diagnostic figures to assess for this specific matching step.
- The matching result depends on the chosen search-window and ranking logic used by the implemented script; this report reflects the produced outputs, not an independent re-computation of the algorithm.
- The candidate counts are large, so the confidence assessment is based on the uniqueness of the best-ranked solution rather than on a sparse candidate pool.
- The summary files indicate success, but they do not document an explicit false-match benchmark or manual validation against external authoritative catalogs.
- The outputs show only three major earthquakes; conclusions about broader regional behavior should be reserved for later background-characterization tasks.

## Report-Ready Summary

Three major earthquakes were matched to the relocated regional catalog with high confidence and no unmatched cases. The best matches show near-zero time offsets, sub-kilometer spatial separations, negligible depth differences, and identical magnitudes, indicating that the relocated catalog preserves the mainshock identities very tightly. These results provide a reliable event-to-event linkage for subsequent sequence analysis around M1, M2, and M3.

Primary evidence files:
- `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/02_major_earthquake_matching/major_earthquake_match_summary.csv`
- `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/02_major_earthquake_matching/major_earthquake_matches.csv`
- `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/02_major_earthquake_matching/major_earthquake_candidates.csv`
</task_analysis>

<task_analysis>
Task: 03_regional_background_characterization
Description: Characterize regional seismicity background, station coverage, and mechanism availability from the cleaned catalog.
Analysis file: <CASE_ROOT>/run/01_data_foundation/exp_run/analysis/03_regional_background_characterization.md
Output directory: <CASE_ROOT>/run/01_data_foundation/exp_run/outputs/03_regional_background_characterization

## Scientific Purpose

This task establishes the regional seismicity background for the Aomori/Japan catalog analysis, with three goals:  
1. characterize the earthquake population in space, time, magnitude, and depth;  
2. quantify station coverage and focal-mechanism availability as data-quality controls for later sequence analysis;  
3. derive reusable summary products, including a preliminary completeness magnitude and Gutenberg–Richter b-value, to support hypothesis testing in subsequent tasks.

The outputs are intended to define the baseline seismic regime against which major-earthquake sequences, clustering, and possible aftershock or swarm behavior can be interpreted.

## Method and Implementation Evidence

The implemented workflow produced a cleaned regional background catalog and a set of summary tables and diagnostic figures from the Stage-1 catalog. Evidence for the implementation is contained in:

- `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/03_regional_background_characterization/regional_catalog_background_clean.csv`
- `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/03_regional_background_characterization/station_background_clean.csv`
- `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/03_regional_background_characterization/mechanism_background_clean.csv`
- `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/03_regional_background_characterization/mechanism_subset_joined_to_catalog.csv`

The regional characterization included:
- depth and magnitude descriptive statistics;
- depth segmentation summary;
- temporal activity-rate analysis on 90-day windows;
- magnitude-frequency distribution and preliminary Mc/b-value estimation;
- station coverage diagnostics using nearest-station distance;
- mechanism availability metrics and a joined mechanism-catalog subset for later analysis.

The publication-style figures generated for interpretation are:

- `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/03_regional_background_characterization/figure_regional_map.png`
- `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/03_regional_background_characterization/figure_time_magnitude.png`
- `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/03_regional_background_characterization/figure_depth_time.png`
- `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/03_regional_background_characterization/figure_magnitude_depth.png`
- `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/03_regional_background_characterization/figure_mfd_mc_bvalue.png`
- `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/03_regional_background_characterization/figure_spatial_density.png`
- `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/03_regional_background_characterization/figure_depth_distribution.png`
- `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/03_regional_background_characterization/figure_station_coverage.png`
- `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/03_regional_background_characterization/figure_mechanism_availability.png`

## Key Results and Evidence Files

### 1) Regional seismicity is strongly clustered and spatially segmented
The regional map shows earthquakes concentrated in a narrow north–south corridor, with distinct clusters near the northern, central, and southern parts of the domain. The spatial-density diagnostic confirms at least two dominant high-density nuclei and several elongated substructures, indicating nonuniform seismicity rather than a diffuse background.

Evidence:
- `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/03_regional_background_characterization/figure_regional_map.png`
- `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/03_regional_background_characterization/figure_spatial_density.png`
- `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/03_regional_background_summary.csv`

Key visible spatial interpretation:
- the earthquake cloud is organized into compact clusters around approximately 142–144°E and 38.5–41.5°N;
- the density map shows a northern hotspot near ~143.0°E, 40.9°N and a southern hotspot near ~143.3–143.6°E, 39.4–39.7°N;
- station coverage extends more broadly than the seismicity cloud, supporting regional location control.

### 2) Depth structure is dominated by shallow to intermediate events, with a long deep tail
The depth histogram and depth-time plot indicate a strongly right-skewed depth distribution. Most events lie in the shallow–intermediate crust, with a dominant band around roughly 10–30 km and a sparse tail extending to about 120 km.

Evidence:
- `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/03_regional_background_characterization/figure_depth_distribution.png`
- `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/03_regional_background_characterization/figure_depth_time.png`
- `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/03_regional_background_characterization/depth_summary_stats.csv`
- `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/03_regional_background_characterization/depth_segmentation_summary.csv`

Key visible depth interpretation:
- the distribution peaks in the ~15–30 km range;
- shallow events are persistent through the record;
- deeper events exist but are sparse and likely represent a minor population or isolated outliers;
- the depth-time panel shows burst-like episodes with short-lived vertical spreading in depth, especially in December 2025 and late April–early May 2026.

### 3) Magnitude distribution is compatible with Gutenberg–Richter scaling above Mc, but with low b-value
The MFD figure reports a preliminary completeness magnitude of Mc = 1.20 and a fitted Gutenberg–Richter b-value of about 0.60 over the range [1.20, 7.70], using 16,933 events. This suggests the catalog is broadly complete above the threshold but has a relatively low b-value, implying a stronger proportion of larger events than the canonical b≈1 case.

Evidence:
- `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/03_regional_background_characterization/figure_mfd_mc_bvalue.png`
- `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/03_regional_background_characterization/mc_bvalue_estimate.csv`
- `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/03_regional_background_characterization/magnitude_summary_stats.csv`

Interpretation from the figure:
- observed counts are suppressed below Mc, consistent with incomplete detection of smaller events;
- above Mc, the frequency decay is approximately Gutenberg–Richter-like;
- the low b-value indicates a relatively “large-event-rich” regional distribution.

### 4) Magnitude–depth relation is weak, with larger events mostly shallow to intermediate
The magnitude-depth scatter shows no strong monotonic relationship across the full dataset. Most events cluster at shallow depths and low-to-moderate magnitudes, while very large events appear mainly at shallow to intermediate depth. Deep events are generally smaller and sparse.

Evidence:
- `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/03_regional_background_characterization/figure_magnitude_depth.png`
- `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/03_regional_background_characterization/magnitude_summary_stats.csv`
- `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/03_regional_background_characterization/depth_summary_stats.csv`

Visible pattern:
- dense concentration near 5–20 km and M ~1–3;
- a practical scarcity threshold near ~60 km depth;
- a few large shallow/intermediate outliers reaching about M 7–7.5.

### 5) Temporal activity is bursty rather than steady
The time–magnitude and depth–time plots show episodic surges in activity, notably around mid-November 2025, mid-December 2025, and late April to early May 2026. These bursts are superimposed on a persistent low-magnitude background.

Evidence:
- `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/03_regional_background_characterization/figure_time_magnitude.png`
- `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/03_regional_background_characterization/figure_depth_time.png`
- `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/03_regional_background_characterization/temporal_activity_rate_90d.csv`

Visible temporal pattern:
- clear burst intervals separated by quieter periods;
- the December 2025 episode is the most structurally distinctive because it broadens the depth distribution;
- the overall chronology suggests repeated activation pulses rather than monotonic evolution.

### 6) Station coverage is moderate-to-good in the core region but heterogeneous at the margins
The station diagnostic shows nearest-station distances centered around ~14–16 km, with most sampled events between ~8 and 22 km and a tail out to ~36 km. This indicates reasonable central coverage but poorer control in fringe areas.

Evidence:
- `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/03_regional_background_characterization/figure_station_coverage.png`
- `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/03_regional_background_characterization/station_coverage_metrics.csv`
- `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/03_regional_background_characterization/station_background_clean.csv`

Interpretation:
- core earthquake zones are likely well detected and reasonably located;
- events beyond ~20–25 km from the nearest station are more uncertain and may have worse depth control;
- coverage is adequate for regional background characterization but nonuniform enough to matter for later sequence thresholds.

### 7) Focal-mechanism availability is partial and incomplete
The mechanism availability figure shows 215 records with no geometry, 0 with geometry only, and 139 with core mechanism. This means mechanism-based analysis is possible for a substantial subset, but a majority of records lack usable mechanism geometry.

Evidence:
- `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/03_regional_background_characterization/figure_mechanism_availability.png`
- `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/03_regional_background_characterization/mechanism_availability_metrics.csv`
- `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/03_regional_background_characterization/mechanism_background_clean.csv`
- `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/03_regional_background_characterization/mechanism_subset_joined_to_catalog.csv`

Visible mechanism summary:
- no geometry: 215
- geometry only: 0
- core mechanism: 139

This is a strong constraint for later sequence analysis: mechanism-stratified testing will be limited to the subset with core mechanism data.

### 8) The figures are publication-ready diagnostic products
The visual outputs are clean, legible, and suitable for downstream reporting:
- map figure includes stations, major earthquakes, earthquake depths, and a depth colorbar;
- MFD figure includes both histogram and cumulative scaling with Mc and b annotations;
- depth, magnitude, and station diagnostics are clearly labeled;
- all figures use standard axes, readable fonts, and report-oriented styling.

Evidence:
- all PNG files listed above.

## Limitations and Assumptions

- The mechanism availability figure only reports record counts by category; it does not show how availability varies with time, depth, or magnitude. Therefore, any claim about temporal or magnitude dependence of mechanism completeness is not supported by that figure alone.
- The spatial-density and map figures are qualitative diagnostics. They clearly show clustering, but they do not by themselves quantify cluster significance, cluster boundaries, or tectonic segmentation.
- The MFD estimate is explicitly preliminary. The reported Mc = 1.20 and b ≈ 0.60 are useful for first-order analysis, but sensitivity to binning, fitting range, and catalog completeness should be evaluated before formal inference.
- The depth histogram appears somewhat blocky/segmented, so some fine-scale structure may reflect binning choices rather than true geological layering.
- Station coverage is summarized through nearest-station distance, which is a useful but simplified proxy. It does not fully capture azimuthal gap, velocity-model sensitivity, or 3-D location quality.
- The task handoff notes that outputs were truncated, so this review relies on the discovered primary tables and PNGs rather than an exhaustive inspection of every internal intermediate file.
- No PDF deliverables were present in the output directory; only the listed PNG and CSV products were available for analysis.

## Report-Ready Summary

The regional background catalog for the Aomori/Japan case is dominated by clustered shallow-to-intermediate seismicity with strong spatial segmentation and burst-like temporal behavior. The main seismicity corridor is concentrated around 142–144°E and 38.5–41.5°N, with two prominent density hotspots and several elongated substructures. Depths are strongly skewed toward ~10–30 km, with a sparse tail reaching ~120 km. The preliminary magnitude completeness is Mc = 1.20 and the Gutenberg–Richter b-value is about 0.60 over the fitted range [1.20, 7.70], indicating a complete catalog above the threshold but a relatively large-event-rich distribution.

Station coverage is moderate to good in the core of the earthquake cloud, with typical nearest-station distances around 14–16 km, but it becomes weaker toward the margins. Focal-mechanism information is only partially available: 139 records have core mechanism data, while 215 lack geometry entirely. These results define a solid background for later sequence analysis, but they also identify where special care is needed: depth-dependent thresholds, spatially localized radii, and mechanism-stratified tests should account for heterogeneous station coverage and incomplete mechanism availability.

Primary reusable evidence files:
- `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/03_regional_background_characterization/regional_background_summary.csv`
- `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/03_regional_background_characterization/mc_bvalue_estimate.csv`
- `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/03_regional_background_characterization/station_coverage_metrics.csv`
- `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/03_regional_background_characterization/mechanism_availability_metrics.csv`
- `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/03_regional_background_characterization/figure_regional_map.png`
- `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/03_regional_background_characterization/figure_mfd_mc_bvalue.png`
</task_analysis>

<task_analysis>
Task: 04_mainshock_regional_context
Description: Summarize local catalog, station, and mechanism context around each major earthquake.
Analysis file: <CASE_ROOT>/run/01_data_foundation/exp_run/analysis/04_mainshock_regional_context.md
Output directory: <CASE_ROOT>/run/01_data_foundation/exp_run/outputs/04_mainshock_regional_context

## Scientific Purpose

This task establishes the **local physical and observational context around each major earthquake** in the Aomori regional catalog. The goal is to determine whether each mainshock sits in a distinct spatial/depth domain, how dense the surrounding seismicity is, how well the area is covered by stations, and whether focal-mechanism data are sufficiently available for sequence analysis.

The outputs are intended to support later aftershock/sequence modeling by identifying:
- local catalog density and depth structure around each mainshock,
- nearby station availability and coverage quality,
- nearby focal-mechanism availability,
- and practical radius/depth thresholds for follow-on sequence studies.

## Method and Implementation Evidence

The task produced a per-mainshock regional-context assessment using the cleaned regional catalog, station list, and mechanism records from earlier steps.

Evidence of the implemented workflow is provided by:
- `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/04_mainshock_regional_context/mainshock_context_summary.csv`
- `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/04_mainshock_regional_context/mainshock_local_catalog_windows.csv`
- `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/04_mainshock_regional_context/mainshock_local_station_windows.csv`
- `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/04_mainshock_regional_context/regional_context_overview.csv`
- `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/04_mainshock_regional_context/sequence_threshold_notes.csv`

The summary tables show that the implementation computed:
- a **local catalog window** for each mainshock,
- local event counts and density relative to a regional reference,
- local depth statistics and comparison with regional depth statistics,
- local station counts and distance metrics,
- local mechanism record counts and fractions of regional mechanism availability,
- and a qualitative flagging of depth/spatial domain distinctness plus suggested sequence thresholds.

The figures generated for the task are:
- `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/04_mainshock_regional_context/figure_mainshock_context_panels.png`
- `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/04_mainshock_regional_context/figure_mainshock_regional_context_map.png`

## Key Results and Evidence Files

### 1) Mainshock-by-mainshock local context

The summary table contains three mainshocks:
- **M1** matched to `CAT_001427`
- **M2** matched to `CAT_004910`
- **M3** matched to `CAT_018070`

From `/.../mainshock_context_summary.csv`:

- **M1**
  - Time: `2025-11-09 08:03:39.240000+00:00`
  - Location: 39.402°N, 143.507°E
  - Depth: 15.9 km
  - Magnitude: 6.9
  - Local event count: **6093**
  - Local density ratio to regional median: **7.594**
  - Local median depth: **11.91 km**
  - Station count local: **6**
  - Mechanism local records: **0**
  - Depth domain flag: **typical**
  - Spatial domain flag: **distinct**
  - Station coverage note: **sparse**
  - Mechanism coverage note: **sparse**

- **M2**
  - Time: `2025-12-08 14:15:10.180000+00:00`
  - Location: 40.968°N, 142.288°E
  - Depth: 53.5 km
  - Magnitude: 7.5
  - Local event count: **2203**
  - Local density ratio to regional median: **2.746**
  - Local median depth: **41.92 km**
  - Station count local: **6**
  - Mechanism local records: **57**
  - Depth domain flag: **distinct**
  - Spatial domain flag: **distinct**
  - Station coverage note: **sparse**
  - Mechanism coverage note: **good**

- **M3**
  - Time: `2026-04-20 07:52:58.060000+00:00`
  - Location: 39.842°N, 143.157°E
  - Depth: 19.4 km
  - Magnitude: 7.7
  - Local event count: **4416**
  - Local density ratio to regional median: **5.504**
  - Local median depth: **12.61 km**
  - Station count local: **5**
  - Mechanism local records: **4**
  - Depth domain flag: **typical**
  - Spatial domain flag: **distinct**
  - Station coverage note: **sparse**
  - Mechanism coverage note: **moderate**

These values indicate that all three mainshocks lie in areas with elevated local seismicity relative to the regional median density proxy, but with substantial differences in local depth regime and mechanism availability.

### 2) Regional reference context

The regional overview file provides the baseline used for comparison:
- Regional event count: **21741**
- Regional depth median: **15.64 km**
- Regional depth IQR: **17.42 km**
- Regional density proxy: **0.130078**
- Regional mechanism geometry fraction: **0.392655**
- Regional mechanism core fraction: **0.392655**
- Regional station count: **371**
- Mainshock count: **3**
- Distinct depth domain count: **1**
- Distinct spatial domain count: **3**
- Edge effect count: **0**

Evidence:
- `/.../regional_context_overview.csv`

This supports the interpretation that:
- the three mainshocks are all spatially distinct from one another,
- only one is classified as depth-distinct (`M2`),
- and no mainshock is flagged as an edge-effect case.

### 3) Sequence threshold recommendations

The threshold notes are identical across all three events:
- use radius near **44 km**
- apply depth window near **±26 km**
- consider a **higher magnitude threshold** for coda/aftershock screening

Evidence:
- `/.../sequence_threshold_notes.csv`

This is an important result for later sequence analysis because it provides a consistent local-window design that appears to have been used for all three mainshocks.

### 4) Spatial and observational context from figures

#### `/.../figure_mainshock_regional_context_map.png`
The map shows:
- a widespread station network,
- three major earthquakes as red stars,
- focal-mechanism points as clustered colored circles,
- and depth encoded by color.

Key map-based interpretation:
- **M1** lies within a dense mechanism cluster near the central/eastern part of the region.
- **M2** is on the northern edge of a compact mechanism cluster and is the only event clearly flagged as depth-distinct in the summary table.
- **M3** is embedded in the southeastern cluster of mechanism records.
- Station coverage is broad but less dense toward the map edges.

#### `/.../figure_mainshock_context_panels.png`
This 2×2 summary plot shows:
- **Local catalog density**: M1 highest, M3 intermediate, M2 lowest.
- **Station coverage**: M1 and M2 have ~6 local stations; M3 has ~5.
- **Mechanism availability**: M2 highest, M3 low, M1 essentially none.
- **Local vs regional density**: all three are above the regional reference line; M1 is strongest, M2 weakest.

This figure is useful because it compresses the main contextual controls relevant to future sequence analysis into a single diagnostic view.

## Limitations and Assumptions

- The current task is a **context characterization**, not a full causal analysis. It identifies local patterns and data-support limitations, but does not test hypotheses about triggering or sequence dynamics.
- The station coverage is summarized from nearby stations, but the table suggests **sparse coverage** around all three mainshocks; that means any later waveform-based or focal-mechanism-based inference may be unevenly constrained.
- Mechanism availability differs strongly by event:
  - M2 has many nearby mechanism records,
  - M3 has only a few,
  - M1 has none in the local window.
  This creates uneven comparability across the three mainshocks.
- The same suggested sequence window appears for all three mainshocks (`~44 km` radius, `~±26 km` depth). This is a practical starting point, but it may be too coarse for event-specific modeling where one mainshock is depth-distinct (`M2`).
- The outputs do not provide explicit numeric time-window metrics for local burst/quiet-period behavior in this task; that should be handled in later sequence analysis steps.
- The CSV files were treated as machine-readable evidence; the PDF analyzer is unsupported for CSV, so all file content was inspected via direct table loading instead.

## Report-Ready Summary

The mainshock-regional-context assessment shows that the three matched major earthquakes all occur in **spatially distinct, seismically active parts of the Aomori region**, with local event densities substantially above the regional median. **M1** has the highest local catalog density and the strongest density ratio, **M2** is the only event flagged as **depth-distinct** and also has the best nearby mechanism availability, and **M3** is intermediate in density but has limited mechanism coverage. All three events have only **sparse station coverage** in their local windows, so later sequence analysis should account for possible observational bias. A consistent preliminary sequence window of **~44 km radius** and **~±26 km depth** was recommended for all three events, with a higher magnitude threshold suggested for screening. The most important evidence files are `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/04_mainshock_regional_context/mainshock_context_summary.csv`, `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/04_mainshock_regional_context/regional_context_overview.csv`, `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/04_mainshock_regional_context/sequence_threshold_notes.csv`, and the two figures `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/04_mainshock_regional_context/figure_mainshock_context_panels.png` and `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/04_mainshock_regional_context/figure_mainshock_regional_context_map.png`.
</task_analysis>

<task_analysis>
Task: 05_diagnostic_figures
Description: Generate Nature-style high-resolution diagnostic figures for audit, background, and context analysis.
Analysis file: <CASE_ROOT>/run/01_data_foundation/exp_run/analysis/05_diagnostic_figures.md
Output directory: <CASE_ROOT>/run/01_data_foundation/exp_run/outputs/05_diagnostic_figures

## Scientific Purpose

The purpose of this task was to generate a complete set of Nature-style diagnostic figures for the Aomori/Japan regional catalog analysis, supporting later sequence analysis, background seismicity characterization, and mainshock-context interpretation. The figure suite is intended to document spatial, temporal, depth, magnitude, station-coverage, and focal-mechanism patterns in a visually consistent, report-ready form.

## Method and Implementation Evidence

The implementation produced a multi-figure diagnostic package in `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/05_diagnostic_figures`, with a machine-readable inventory in `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/05_diagnostic_figures/figure_manifest.csv`.

The manifest confirms 11 PNG figures were generated and present:
- `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/05_diagnostic_figures/figure_01_regional_map.png`
- `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/05_diagnostic_figures/figure_02_time_magnitude.png`
- `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/05_diagnostic_figures/figure_03_depth_time.png`
- `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/05_diagnostic_figures/figure_04_magnitude_depth.png`
- `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/05_diagnostic_figures/figure_05_magnitude_frequency_mc_bvalue.png`
- `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/05_diagnostic_figures/figure_06_spatial_density.png`
- `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/05_diagnostic_figures/figure_07_depth_distribution.png`
- `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/05_diagnostic_figures/figure_08_depth_cross_section.png`
- `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/05_diagnostic_figures/figure_09_station_coverage.png`
- `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/05_diagnostic_figures/figure_10_mechanism_diagnostics.png`
- `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/05_diagnostic_figures/figure_11_mainshock_context_overview.png`

The figures collectively implement the intended diagnostic coverage:
- regional spatial map with earthquakes, major events, stations, and mechanisms;
- temporal activity and magnitude evolution;
- depth–time evolution;
- magnitude–depth relationship;
- preliminary magnitude-frequency / Mc / b-value diagnostic;
- spatial density / clustering diagnostic;
- depth distribution;
- depth cross-section;
- station coverage diagnostic;
- focal-mechanism diagnostics;
- mainshock context overview.

## Key Results and Evidence Files

### 1) Regional spatial structure is strongly clustered
Evidence: `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/05_diagnostic_figures/figure_01_regional_map.png`, `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/05_diagnostic_figures/figure_06_spatial_density.png`

The regional map shows clustered seismicity with distinct concentrations near approximately 42°N, 142–143°E and 39–40°N, 143–143.7°E, plus diffuse background activity. Major earthquakes are plotted as red stars and fall within or near dense seismic clusters. The density diagnostic highlights two dominant density maxima, including a strong core near ~143.0°E, 41.0°N and a second major cluster near ~143.3–143.6°E, 39.4–39.8°N, with some lineation-like structure in the southern cluster.

### 2) Temporal seismicity is episodic, with burst-like sequences
Evidence: `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/05_diagnostic_figures/figure_02_time_magnitude.png`, `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/05_diagnostic_figures/figure_03_depth_time.png`

The time–magnitude plot shows clustered seismicity episodes rather than uniform activity, with notable bursts around mid-November 2025, mid-December 2025, and late April to early May 2026. Most events are small to moderate, and major earthquakes are visually emphasized with red stars. The depth–time plot indicates that these bursts are shallow-dominated, but some sequences extend to intermediate depths and one pronounced event cluster spans shallow to roughly 55 km depth.

### 3) Magnitude and depth jointly indicate shallow-to-intermediate dominance
Evidence: `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/05_diagnostic_figures/figure_04_magnitude_depth.png`, `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/05_diagnostic_figures/figure_07_depth_distribution.png`, `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/05_diagnostic_figures/figure_08_depth_cross_section.png`

The magnitude–depth plot does not show a strong monotonic relation, but it does show that the largest events are shallow to moderate depth, while deeper events are less frequent and generally smaller. The depth histogram is strongly right-skewed and multimodal, with a dominant peak around ~10–18 km and a secondary broader population to ~35–45 km. The cross-section similarly indicates shallow clustering in multiple along-profile domains, a secondary intermediate-depth population, and only sparse deep outliers to ~80–120 km.

### 4) Preliminary Mc / b-value diagnostic remains unresolved
Evidence: `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/05_diagnostic_figures/figure_05_magnitude_frequency_mc_bvalue.png`

The magnitude-frequency plot is clearly diagnostic but does not provide a formal completeness magnitude or b-value estimate. The distribution is right-skewed with a peak around M ~1.4–1.7 and a long high-magnitude tail, but the figure explicitly indicates that b is not estimated. This makes the figure useful as a preliminary audit product, but not yet as a final statistical basis for Gutenberg–Richter interpretation.

### 5) Station coverage is non-uniform but reasonably central
Evidence: `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/05_diagnostic_figures/figure_09_station_coverage.png`

The station diagnostic shows stations spread across the region but clustered more strongly in the west-central portion, with sparser coverage toward the eastern margin and some localized gaps. The nearest-station distance histogram suggests most events fall roughly within ~8–20 km of a station, with a right tail beyond 30 km and an isolated large value near ~45 km. This supports moderate coverage overall, but with edge effects and uneven sampling that may matter for small-event detectability.

### 6) Focal-mechanism availability is spatially uneven and orientation-structured
Evidence: `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/05_diagnostic_figures/figure_10_mechanism_diagnostics.png`, `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/05_diagnostic_figures/figure_01_regional_map.png`

The mechanism diagnostics show broad but uneven availability, concentrated along a north–south belt near ~142°E. The strike distribution is strongly clustered around ~190–210°, with smaller secondary populations elsewhere, suggesting a clear regional tectonic preference rather than random orientation. However, there are spatial gaps and uneven sampling, so interpretation should account for incomplete coverage.

### 7) Mainshock context figure is a compact numeric summary rather than a full spatial overview
Evidence: `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/05_diagnostic_figures/figure_11_mainshock_context_overview.png`

The overview figure summarizes local event count, local density ratio, nearby stations, and nearby mechanisms for the major earthquakes, but it does not visibly include the spatial map, temporal evolution, or depth context that a full “overview” might imply. It is still useful as a compact quantitative companion to the other figures.

## Limitations and Assumptions

- The figure manifest is machine-readable and confirms file existence and sizes, but it does not itself document plotting parameters, source catalog filtering, or any statistical thresholds used.
- The magnitude-frequency figure is preliminary: it explicitly notes that b is not estimated, so Mc/b interpretation remains incomplete in this task output.
- The spatial and cross-section figures are diagnostically useful but are not fully cartographically contextualized; for example, the regional map lacks a basemap/coastline context in the visible output.
- Some panels are dense with overplotted points, especially the depth–time, magnitude–depth, and cross-section plots, which reduces quantitative readability in the most active clusters.
- The station and mechanism diagnostics indicate uneven spatial coverage, so small-event completeness and focal-mechanism representativeness likely vary across the region.
- The mainshock overview figure is compact and informative, but it does not fully integrate spatial, temporal, and depth dimensions in a single view.
- No PDF outputs were present in the evidence set for this task; the attempted PDF analysis on `<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/05_diagnostic_figures/figure_manifest.csv` failed because the file is CSV, not PDF.

## Report-Ready Summary

This task successfully produced a coherent diagnostic figure package that supports background seismicity characterization and downstream sequence analysis. The evidence indicates a region dominated by clustered, episodic seismicity with strong shallow-to-intermediate depth concentration, non-uniform but workable station coverage, and spatially uneven but tectonically structured focal-mechanism availability. The strongest report-ready products are the regional map, time–magnitude plot, depth–time plot, station coverage diagnostic, and mechanism diagnostics; the magnitude-frequency / Mc–b figure remains preliminary and should be treated as a diagnostic rather than final statistical evidence.
</task_analysis>

<task_analysis>
Task: 06_candidate_patterns_estimation
Description: Convert background and context results into ranked candidate patterns and follow-up analysis suggestions.
Analysis file: <CASE_ROOT>/run/01_data_foundation/exp_run/analysis/06_candidate_patterns_estimation.md
Output directory: <CASE_ROOT>/run/01_data_foundation/exp_run/outputs/06_candidate_patterns_estimation

## Scientific Purpose

This task converts the previously derived regional background and mainshock-context diagnostics into a ranked set of **testable candidate seismic patterns** and **follow-up analysis recommendations** for later sequence analysis. The aim is to identify which patterns are most likely to matter for aftershock/sequence interpretation in the Japan Aomori catalog, and to translate those findings into practical thresholds for spatial, temporal, depth, and mechanism-based analysis.

## Method and Implementation Evidence

The implementation appears to combine summary statistics from the background catalog and the mainshock-centered context snapshots, then rank candidate hypotheses by a priority score.

Evidence of this workflow is provided by:

- `"<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/06_candidate_patterns_estimation/background_summary_snapshot.csv"`
- `"<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/06_candidate_patterns_estimation/mainshock_context_snapshot.csv"`
- `"<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/06_candidate_patterns_estimation/candidate_patterns_ranked.csv"`
- `"<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/06_candidate_patterns_estimation/candidate_patterns_summary.csv"`
- `"<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/06_candidate_patterns_estimation/followup_analysis_suggestions.csv"`

The ranked output indicates that the approach uses:
- **mainshock-specific local context metrics** such as local density ratio, station count, mechanism-record count, and depth-domain flag;
- **catalog-wide pattern flags** such as focal-mechanism data gaps;
- **priority ranking** to separate the most actionable hypotheses from lower-priority background effects.

The two figures provide visual summaries of the ranking and of the mainshock context:
- `"<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/06_candidate_patterns_estimation/figure_candidate_patterns_ranked.png"`
- `"<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/06_candidate_patterns_estimation/figure_mainshock_context_overview.png"`

## Key Results and Evidence Files

### 1) Ranked candidate patterns identify mainshock-specific context as the strongest signal

The ranked catalog shows that the highest-priority candidates are the **mainshock local-context patterns** for M1 and M3, both with priority score 1.0.

From `candidate_patterns_ranked.csv`:
- `MS_M1`: local density ratio = **7.59**, stations = **6**, mechanism records = **0**, depth flag = **typical**
- `MS_M3`: local density ratio = **5.50**, stations = **5**, mechanism records = **4**, depth flag = **typical**
- `MS_M2`: local density ratio = **2.75**, stations = **6**, mechanism records = **57**, depth flag = **distinct**

Scientific interpretation:
- **M1 and M3** stand out as the most actionable sequence-analysis targets because they sit in strongly enriched local seismic environments relative to the regional median.
- **M2** is still important, but its local-enrichment signal is weaker than M1/M3 despite much better mechanism support.

Supporting files:
- `"<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/06_candidate_patterns_estimation/candidate_patterns_ranked.csv"`
- `"<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/06_candidate_patterns_estimation/figure_candidate_patterns_ranked.png"`

### 2) Mechanism-availability gap is a major catalog-wide limitation and a candidate pattern itself

The ranked output identifies a catalog-wide focal-mechanism gap:
- `P06`: mechanism geometry available for **39.3%** of mechanism records; core mechanisms for **39.3%**
- priority score ≈ **0.607**

Scientific interpretation:
- Focal-mechanism analysis must be treated as **sparse and incomplete**, and interpretation should distinguish between true physical patterns and simple data-availability bias.
- This is especially relevant because M1 and M3 have very few or no local mechanism records in the context snapshot.

Supporting files:
- `"<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/06_candidate_patterns_estimation/candidate_patterns_ranked.csv"`
- `"<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/06_candidate_patterns_estimation/followup_analysis_suggestions.csv"`

### 3) Mainshock context suggests a common spatial/depth window, but with event-specific differences

The `mainshock_context_snapshot.csv` shows that all three major earthquakes were evaluated with the same local window:
- local radius ≈ **44.31 km**
- local depth window ≈ **26.13 km**

Mainshock-specific context:
- **M1**: 6093 local events, density ratio **7.59**, local depth median **11.91 km**, mechanism records **0**
- **M2**: 2203 local events, density ratio **2.75**, local depth median **41.92 km**, mechanism records **57**
- **M3**: 4416 local events, density ratio **5.50**, local depth median **12.61 km**, mechanism records **4**

Scientific interpretation:
- All three mainshocks occur in locally dense seismic settings, but **M1 and M3 are much more enriched than M2**.
- **M2 is depth-distinct** relative to the background, with a much deeper local median depth than the other two events.
- The analysis therefore supports **shared regional thresholds** for first-pass sequence work, but also **event-specific depth stratification**, especially for M2.

Supporting files:
- `"<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/06_candidate_patterns_estimation/mainshock_context_snapshot.csv"`
- `"<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/06_candidate_patterns_estimation/figure_mainshock_context_overview.png"`

### 4) The background summary indicates a large, usable dataset for follow-up analysis

From `candidate_patterns_summary.csv`:
- catalog events: **21741**
- mainshock events: **3**
- station count: **371**
- mechanism records: **354**

Scientific interpretation:
- The catalog is large enough for robust regional background characterization and for mainshock-centered subsetting.
- However, the mechanism sample is modest relative to the earthquake catalog, consistent with the mechanism-data-gap pattern above.

Supporting file:
- `"<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/06_candidate_patterns_estimation/candidate_patterns_summary.csv"`

### 5) Follow-up analysis suggestions are already concretely thresholded

The follow-up suggestions emphasize:
- **space**: use spatial clusters and mainshock-centered windows
- **time**: use 30-day windows for rate diagnostics and flag bursts/quiet intervals
- **depth**: split analyses by empirical depth bins and mainshock depth domains

The mainshock-specific threshold suggestion repeats:
- use radius near **44 km**
- apply depth window near **±26 km**
- consider a **higher magnitude threshold** for coda/aftershock screening

Scientific interpretation:
- These recommendations are directly usable for later sequence-analysis design, and they encode the key idea that **one-size-fits-all thresholds are not optimal** for this region.

Supporting file:
- `"<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/06_candidate_patterns_estimation/followup_analysis_suggestions.csv"`

## Limitations and Assumptions

- `background_summary_snapshot.csv` is effectively empty in the delivered output directory: the file size is 1 byte and it could not be parsed as a table. This means the task’s final ranking likely relied on other inputs or in-memory values rather than a persistent background snapshot table.
- The ranked patterns are concise and highly actionable, but they are **screening-level hypotheses**, not formal statistical tests.
- The mainshock context metrics depend on the chosen local radius and depth window; the recommended thresholds are useful, but they should still be validated in sensitivity tests.
- Mechanism-based interpretation is limited by sparse coverage: the catalog-level mechanism availability is only partial, and M1/M3 in particular have weak local mechanism support.
- The figure-based interpretation is limited to what is visually encoded in the outputs; any deeper numeric uncertainty, confidence intervals, or model diagnostics are not exposed in the provided files.
- `candidate_patterns_ranked.csv` contains only a small set of patterns, so lower-ranked or subtle effects may not be represented.

## Report-Ready Summary

The candidate-pattern estimation task successfully distilled the regional background and mainshock context into a short list of **high-priority sequence-analysis hypotheses**. The strongest patterns are **mainshock-centered local seismicity enrichment**, especially for **M1** and **M3**, followed by a **catalog-wide focal-mechanism data gap** that should be explicitly handled in any later tectonic or source-property analysis. The outputs support using a **~44 km spatial window**, a **~26 km depth window**, and **event-specific depth stratification**—particularly for the deeper M2 event. The most important reusable evidence files are `candidate_patterns_ranked.csv`, `mainshock_context_snapshot.csv`, `followup_analysis_suggestions.csv`, and the two overview figures in `figure_candidate_patterns_ranked.png` and `figure_mainshock_context_overview.png`.
</task_analysis>


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
- Start from the scientific objective and planned workflow.
- Choose the final report shape according to the request and evidence.
- If the user requested a specific format, follow that requested format unless it conflicts with factuality or available evidence.
- Treat concise result summary, technical workflow report, and research-article style report as common shapes, not fixed templates.
- Use task-specific structures when more appropriate, such as diagnostic review, data-quality assessment, method validation, benchmark comparison, or reproducibility report.
- Hybrid structures are allowed when they better serve the scientific objective.
- Do not force a fixed section template when another structure better serves the scientific request.
- Describe implementation at the level needed to understand the evidence, not as a code log.
- Tie every major result to task analyses and concrete output files from the evidence index.
- Include warnings, assumptions, partial coverage, failed items, and other limitations when present.
- Use debug logs only to explain unresolved limitations or important methodological changes.
- Do not fabricate results, citations, or file paths.

</science_report_context>
