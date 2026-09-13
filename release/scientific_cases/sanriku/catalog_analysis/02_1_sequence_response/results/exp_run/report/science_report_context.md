<science_report_context>

## Scientific Objective
<user_request>
You are an earthquake scientist and data-analysis agent.

Current task:
Perform event-centered sequence analysis for the three matched major earthquakes in the Aomori regional catalog.

Goal:
Compare the pre- and post-event seismicity evolution around M1, M2, and M3, and test whether the observed sequence patterns are robust under different spatial, temporal, depth, and magnitude definitions.

Data folder:
"<CASE_ROOT>/data"

Files:
- catalog/Snet_catalog_relocate.csv
- catalog/main_earthquake.csv
- source_mechanism/Snet_mecha.csv
- stations/station.sta

Background guidance from the previous data-foundation analysis:
- The regional catalog is large and internally consistent enough for sequence analysis.
- The three major earthquakes can be matched to the relocated catalog with high confidence.
- Regional seismicity is clustered and spatially segmented.
- Temporal activity is burst-like, so time-window sensitivity is important.
- Preliminary Mc is around 1.2 for the full catalog; use it as a screening value and test higher thresholds.
- M1 and M3 show strong local seismicity enrichment and should be compared carefully.
- M2 may be depth-distinct and should be analyzed with depth stratification.
- Station coverage and focal-mechanism availability are uneven and should be treated as contextual limitations.

Tasks:

1. Minimal data verification
Read the original files and verify the fields needed for sequence analysis:
time, latitude, longitude, depth, magnitude, event ID if available, major-earthquake records, station locations, and focal-mechanism availability.
Re-match the three major earthquakes with the regional catalog before sequence extraction, allowing for small time or location shifts caused by relocation.

2. Sequence extraction
For each major earthquake, extract surrounding events using multiple definitions:
- radii: 30, 44, 50, 80, and 100 km
- time windows: pre-90d, pre-60d, pre-30d, pre-7d, post-7d, post-30d, post-60d, and post-90d
- depth windows: all depths, local mainshock-centered depth windows, and depth-stratified windows
- magnitude thresholds: all events, M >= 1.2, M >= 1.5, M >= 2.0, and M >= 2.5 where feasible

3. Sequence diagnostics
For each sequence and parameter setting, calculate:
- event counts
- cumulative event counts
- moving-window seismicity rates
- pre/post rate ratios
- magnitude distributions
- depth distributions
- post-event rate decay diagnostics, including simple Omori-style fitting if feasible
- time-distance and radial-distance patterns relative to each mainshock
- spatial concentration or expansion indicators if visible
- focal-mechanism availability within the sequence window, and simple mechanism summaries if feasible

4. Robustness analysis
Identify which sequence features are stable across radius, time window, depth window, and magnitude threshold.
Separate robust patterns from parameter-dependent patterns.

5. Three-sequence comparison
Compare M1, M2, and M3 in terms of:
- background activity level
- pre-event activity
- post-event activity
- temporal burstiness
- aftershock decay behavior
- spatial concentration or expansion
- depth structure
- magnitude distribution
- sensitivity to sequence definitions

6. Simple control comparison
Include at least one feasible control:
- background windows away from the mainshock times
- randomized mainshock times
- comparison using higher magnitude thresholds
- or simple background-rate comparison before and after each mainshock

7. Diagnostic figures
Generate high-quality sequence-analysis figures (**Nature-style** publication-quality figures):
- event-centered maps for M1, M2, and M3
- pre/post spatial comparison maps
- cumulative count curves
- moving-window rate curves
- post-event rate decay plots
- time-distance or radial-distance plots relative to each mainshock
- radius and time-window sensitivity heatmaps
- magnitude-threshold sensitivity plots
- depth-stratified sequence plots
- three-sequence comparison summary figure

Use consistent axes, colors, labels, legends, and mainshock markers across M1/M2/M3.
The agent may design additional standard earthquake-sequence analysis plots when they help test robustness, compare the three sequences, or prepare for later M1-M3 focused analysis.

The final response can include a concise summary, but prioritize reusable sequence-analysis tables, robustness results, and publication-quality figures.
</user_request>

## Planned Workflow
<experiment_plan>
# Goal
Perform event-centered sequence analysis for the three matched major earthquakes in the Aomori regional relocated catalog, compare pre- and post-event seismicity evolution around M1, M2, and M3, and test whether observed sequence patterns are robust to alternative spatial, temporal, depth, and magnitude definitions.

## Planning Assumptions
- Use observation data only; the relocated regional catalog is the primary scientific table.
- Required input tables:
  - `catalog/Snet_catalog_relocate.csv`
  - `catalog/main_earthquake.csv`
  - `source_mechanism/Snet_mecha.csv`
  - `stations/station.sta`
- Minimal package/program contract:
  - No specialized external analysis package is required for the core sequence study.
  - The workflow must first validate fields, then rematch M1/M2/M3 to the relocated catalog, then extract event-centered subsets, and only then compute diagnostics and figures.
  - Success evidence must be non-empty validated tables and figure-ready outputs, not placeholder or schema-only results.
- Mainshock rematching is required because relocation may shift origin time, coordinates, and catalog identifiers slightly.
- Completeness guidance:
  - Use Mc ≈ 1.2 as the baseline screening threshold.
  - Repeat key diagnostics at higher magnitude thresholds to test robustness.
- Sequence behavior is expected to be clustered and burst-like, so short-window sensitivity must be explicitly evaluated.
- M1 and M3 are expected to be spatially enriched; M2 may require depth stratification.
- Station coverage and focal-mechanism availability are contextual limitations; mechanism summaries should be reported only where coverage is sufficient.
- Omori-style decay fitting is optional and should be retained only when post-event counts and time span support a stable fit.

## Analysis Plan
### 1. Minimal data verification and mainshock rematching
- Task description:
  - Read the four source files.
  - Verify required fields for sequence analysis: time, latitude, longitude, depth, magnitude, event ID if available, mainshock records, station coordinates, and focal-mechanism availability.
  - Rematch M1, M2, and M3 to the relocated catalog using tolerant time and location matching.
- Required data sources:
  - `catalog/Snet_catalog_relocate.csv`
  - `catalog/main_earthquake.csv`
  - `source_mechanism/Snet_mecha.csv`
  - `stations/station.sta`
- Parameter selection strategy:
  - Use mainshock records as anchors.
  - Match by combined origin-time proximity and hypocentral proximity, with magnitude consistency as a secondary check if needed.
  - If multiple candidates exist, choose the best joint time-location match and record all close candidates.
- Constraints:
  - Do not assume exact equality of time, coordinates, or event IDs between tables.
  - Preserve M1/M2/M3 labels after rematching.
  - Treat missing mechanism or station fields as contextual gaps, not analysis-stopping errors.
- Key outputs:
  - Field-availability audit table by file
  - Matched mainshock registry for M1, M2, M3 with relocated catalog identifiers and match diagnostics
  - Coverage summary for station and mechanism metadata

### 2. Event-centered sequence extraction
- Task description:
  - For each matched mainshock, extract surrounding events under multiple definitions of spatial radius, time window, depth window, and magnitude threshold.
  - Build a standardized event-centered sequence table for each parameter combination.
- Required data sources:
  - `catalog/Snet_catalog_relocate.csv`
  - matched mainshock registry from Task 1
- Parameter selection strategy:
  - Radii: 30, 44, 50, 80, 100 km
  - Time windows: pre-90d, pre-60d, pre-30d, pre-7d, post-7d, post-30d, post-60d, post-90d
  - Depth windows:
    - all depths
    - local mainshock-centered depth window
    - depth-stratified bins
  - Magnitude thresholds:
    - all events
    - M ≥ 1.2
    - M ≥ 1.5
    - M ≥ 2.0
    - M ≥ 2.5 where feasible
- Constraints:
  - Use the same extraction logic for all three mainshocks.
  - Keep the event-centered time origin fixed at each mainshock origin time.
  - Record empty and sparse combinations explicitly so robustness interpretation is transparent.
- Key outputs:
  - Event-centered subset tables for each mainshock and parameter combination
  - Extraction count matrix by radius, time window, depth window, and magnitude threshold
  - Sparse-window flags for later robustness analysis

### 3. Sequence diagnostics
- Task description:
  - Quantify seismicity evolution for each extracted sequence and parameter setting.
  - Compute event counts, cumulative counts, moving-window seismicity rates, pre/post rate ratios, magnitude distributions, depth distributions, time-distance and radial-distance patterns, spatial concentration or expansion indicators, and post-event decay diagnostics.
  - Summarize focal-mechanism availability within sequence windows.
- Required data sources:
  - Event-centered sequence tables from Task 2
  - `source_mechanism/Snet_mecha.csv`
  - `stations/station.sta`
- Parameter selection strategy:
  - Use consistent moving-window definitions across M1/M2/M3.
  - Compute pre/post rate ratios from matched windows of equal duration whenever possible.
  - Estimate Omori-style decay only for post-event windows with sufficient counts and span.
  - Summarize mechanism presence as coverage-limited diagnostics, not as complete focal-mechanism cataloging.
- Constraints:
  - Do not force decay fitting for sparse post-event windows.
  - Treat mechanism summaries as conditional on available overlaps.
  - Use the same mainshock reference coordinates and origin times for all derived distances within each event.
- Key outputs:
  - Diagnostic summary tables of counts, cumulative counts, rates, ratios, magnitude distributions, and depth distributions
  - Post-event decay-fit parameter table with fit-quality flags
  - Radial-distance and time-distance diagnostics relative to each mainshock
  - Spatial concentration/expansion indicators
  - Mechanism availability and simple mechanism summary tables

### 4. Robustness analysis
- Task description:
  - Determine which observed sequence features remain stable as radius, time window, depth window, and magnitude threshold change.
  - Separate robust patterns from parameter-dependent patterns.
- Required data sources:
  - Diagnostic tables from Task 3
  - Extraction summary matrix from Task 2
- Parameter selection strategy:
  - Compare the full parameter grid rather than a single preferred window.
  - Assess robustness by persistence of sign, ranking, and qualitative shape across settings.
  - Use Mc ≈ 1.2 as the baseline comparison and higher thresholds as robustness checks.
- Constraints:
  - Sparse subsets are non-diagnostic, not negative evidence.
  - Do not treat one parameter choice as canonical unless it is repeatedly supported.
- Key outputs:
  - Robustness matrix for each mainshock
  - Stable vs parameter-dependent feature summary
  - Sensitivity flags for radius, time window, depth window, and magnitude threshold

### 5. Three-sequence comparison
- Task description:
  - Compare M1, M2, and M3 in terms of background activity, pre-event activity, post-event activity, burstiness, aftershock decay behavior, spatial concentration or expansion, depth structure, magnitude distribution, and sensitivity to sequence definitions.
- Required data sources:
  - Diagnostic tables from Task 3
  - Robustness summaries from Task 4
- Parameter selection strategy:
  - Use a common baseline parameter set for direct comparison first.
  - Then summarize how conclusions shift under alternate definitions.
  - Give special attention to M1/M3 local enrichment and M2 depth distinctness.
- Constraints:
  - Keep metric definitions identical across the three sequences when comparing directly.
  - Distinguish physical differences from sample-size or coverage effects.
- Key outputs:
  - Cross-event comparison table
  - Ranked summary of M1 vs M2 vs M3 for each major metric
  - Comparison-ready summary dataset for later focused analysis

### 6. Simple control comparison
- Task description:
  - Include at least one feasible control to test whether observed sequence behavior exceeds background variation.
- Required data sources:
  - `catalog/Snet_catalog_relocate.csv`
  - matched mainshock times from Task 1
- Parameter selection strategy:
  - Use one or more of:
    - background windows away from each mainshock
    - randomized mainshock times within the catalog span
    - higher magnitude-threshold comparison
    - simple pre/post background-rate comparison
  - Match control window lengths and radii to the real sequence windows when feasible.
- Constraints:
  - Control windows must not overlap the event-centered study windows.
  - Randomized times must avoid catalog edges and strong truncation effects.
- Key outputs:
  - Control comparison table
  - Background-rate benchmark statistics
  - Observed-versus-control difference metrics

### 7. Diagnostic figures
- Task description:
  - Produce publication-quality figures supporting the sequence interpretation and robustness assessment.
- Required data sources:
  - Event-centered subsets and diagnostics from Tasks 2–6
- Parameter selection strategy:
  - Use consistent axes, color scales, legends, and mainshock markers across M1/M2/M3.
  - Build the figure set around validated tables and summary metrics.
- Constraints:
  - Figures must reflect the same window definitions used in the tables.
  - Do not mix incompatible normalization choices in comparison panels.
- Key outputs:
  - Event-centered maps for M1, M2, and M3
  - Pre/post spatial comparison maps
  - Cumulative count curves
  - Moving-window rate curves
  - Post-event decay plots
  - Time-distance or radial-distance plots relative to each mainshock
  - Radius and time-window sensitivity heatmaps
  - Magnitude-threshold sensitivity plots
  - Depth-stratified sequence plots
  - Three-sequence comparison summary figure

### 8. Reusable analysis products
- Task description:
  - Package validated results into machine-readable outputs for downstream reuse.
- Required data sources:
  - Outputs from Tasks 1–7
- Parameter selection strategy:
  - Export compact tables organized by mainshock and parameter setting.
  - Preserve metadata for window definitions, thresholds, and control type.
- Constraints:
  - Do not replace scientific outputs with narrative-only artifacts.
- Key outputs:
  - Master mainshock-match table
  - Sequence summary tables
  - Robustness and sensitivity tables
  - Control-comparison table
  - Figure-ready data tables for all diagnostics and sensitivity plots
</experiment_plan>

## Implementation Trace
- Task: 01_data_verification_and_rematch
  Description: Validate source tables and rematch the three mainshocks to the relocated catalog.
  Ancestors: none
  Handoff JSON: <CASE_ROOT>/run/02_1_sequence_response/exp_run/log/coding_progress/task_handoff/01_data_verification_and_rematch.json
  Output directory: <CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/01_data_verification_and_rematch
  Analysis file: <CASE_ROOT>/run/02_1_sequence_response/exp_run/analysis/01_data_verification_and_rematch.md
- Task: 02_sequence_extraction
  Description: Extract event-centered sequences around each matched mainshock across the full parameter grid.
  Ancestors: 01_data_verification_and_rematch
  Handoff JSON: <CASE_ROOT>/run/02_1_sequence_response/exp_run/log/coding_progress/task_handoff/02_sequence_extraction.json
  Output directory: <CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/02_sequence_extraction
  Analysis file: <CASE_ROOT>/run/02_1_sequence_response/exp_run/analysis/02_sequence_extraction.md
- Task: 03_sequence_diagnostics
  Description: Compute counts, rates, distributions, spatial patterns, and decay diagnostics for each sequence.
  Ancestors: 02_sequence_extraction
  Handoff JSON: <CASE_ROOT>/run/02_1_sequence_response/exp_run/log/coding_progress/task_handoff/03_sequence_diagnostics.json
  Output directory: <CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/03_sequence_diagnostics
  Analysis file: <CASE_ROOT>/run/02_1_sequence_response/exp_run/analysis/03_sequence_diagnostics.md
- Task: 04_robustness_analysis
  Description: Test which sequence features remain stable across alternative parameter definitions.
  Ancestors: 03_sequence_diagnostics
  Handoff JSON: <CASE_ROOT>/run/02_1_sequence_response/exp_run/log/coding_progress/task_handoff/04_robustness_analysis.json
  Output directory: <CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/04_robustness_analysis
  Analysis file: <CASE_ROOT>/run/02_1_sequence_response/exp_run/analysis/04_robustness_analysis.md
- Task: 05_three_sequence_comparison
  Description: Compare M1, M2, and M3 using a common baseline and then across alternate definitions.
  Ancestors: 04_robustness_analysis
  Handoff JSON: <CASE_ROOT>/run/02_1_sequence_response/exp_run/log/coding_progress/task_handoff/05_three_sequence_comparison.json
  Output directory: <CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/05_three_sequence_comparison
  Analysis file: <CASE_ROOT>/run/02_1_sequence_response/exp_run/analysis/05_three_sequence_comparison.md
- Task: 06_control_comparison
  Description: Evaluate observed sequence behavior against simple background or randomized controls.
  Ancestors: 02_sequence_extraction, 03_sequence_diagnostics
  Handoff JSON: <CASE_ROOT>/run/02_1_sequence_response/exp_run/log/coding_progress/task_handoff/06_control_comparison.json
  Output directory: <CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/06_control_comparison
  Analysis file: <CASE_ROOT>/run/02_1_sequence_response/exp_run/analysis/06_control_comparison.md
- Task: 07_figure_generation
  Description: Generate publication-quality sequence-analysis figures for all mainshocks and comparisons.
  Ancestors: 03_sequence_diagnostics, 04_robustness_analysis, 05_three_sequence_comparison, 06_control_comparison
  Handoff JSON: <CASE_ROOT>/run/02_1_sequence_response/exp_run/log/coding_progress/task_handoff/07_figure_generation.json
  Output directory: <CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/07_figure_generation
  Analysis file: <CASE_ROOT>/run/02_1_sequence_response/exp_run/analysis/07_figure_generation.md
- Task: 08_reusable_outputs
  Description: Export validated tables and figure-ready datasets for downstream reuse.
  Ancestors: 01_data_verification_and_rematch, 02_sequence_extraction, 03_sequence_diagnostics, 04_robustness_analysis, 05_three_sequence_comparison, 06_control_comparison, 07_figure_generation
  Handoff JSON: <CASE_ROOT>/run/02_1_sequence_response/exp_run/log/coding_progress/task_handoff/08_reusable_outputs.json
  Output directory: <CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/08_reusable_outputs
  Analysis file: <CASE_ROOT>/run/02_1_sequence_response/exp_run/analysis/08_reusable_outputs.md

## Result Evidence Index
Use handoff JSON files as compact indexes to important outputs. Use per-task analyses for scientific interpretation. Inspect raw outputs only when the handoff and analysis are insufficient.
<task_evidence task="01_data_verification_and_rematch">
Handoff JSON: <CASE_ROOT>/run/02_1_sequence_response/exp_run/log/coding_progress/task_handoff/01_data_verification_and_rematch.json
{
  "meta": {
    "schema_version": 2,
    "type": "coding_task_handoff",
    "task": "01_data_verification_and_rematch",
    "generated_at": "2026-05-23T06:48:04.903515+00:00"
  },
  "status": {
    "state": "success",
    "stage": "analysis_done",
    "elapsed_sec": 1132.629,
    "timing": {
      "total_sec": 1132.629,
      "coding_agent_sec": 549.324,
      "code_review_sec": 422.697,
      "preflight_sec": 0.676,
      "script_execution_sec": 42.254,
      "result_check_sec": 60.587,
      "task_analysis_sec": 53.473
    },
    "quality_flags": [
      "task_status:success"
    ]
  },
  "paths": {
    "root": "<CASE_ROOT>/run/02_1_sequence_response",
    "script": "<CASE_ROOT>/run/02_1_sequence_response/exp_run/scripts/01_data_verification_and_rematch.py",
    "output_dir": "<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/01_data_verification_and_rematch",
    "analysis": "<CASE_ROOT>/run/02_1_sequence_response/exp_run/analysis/01_data_verification_and_rematch.md",
    "log": "<CASE_ROOT>/run/02_1_sequence_response/exp_run/log/task/01_data_verification_and_rematch/log_1.txt"
  },
  "outputs": {
    "primary": [
      {
        "path": "field_verification_catalog.json",
        "absolute_path": "<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/01_data_verification_and_rematch/field_verification_catalog.json",
        "kind": "machine_readable"
      },
      {
        "path": "field_verification_main_earthquake.json",
        "absolute_path": "<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/01_data_verification_and_rematch/field_verification_main_earthquake.json",
        "kind": "machine_readable"
      },
      {
        "path": "field_verification_mechanism.json",
        "absolute_path": "<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/01_data_verification_and_rematch/field_verification_mechanism.json",
        "kind": "machine_readable"
      },
      {
        "path": "field_verification_stations.json",
        "absolute_path": "<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/01_data_verification_and_rematch/field_verification_stations.json",
        "kind": "machine_readable"
      },
      {
        "path": "mainshock_candidate_preview.json",
        "absolute_path": "<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/01_data_verification_and_rematch/mainshock_candidate_preview.json",
        "kind": "machine_readable"
      },
      {
        "path": "matched_mainshocks.csv",
        "absolute_path": "<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/01_data_verification_and_rematch/matched_mainshocks.csv",
        "kind": "machine_readable"
      },
      {
        "path": "mechanism_coverage_summary.csv",
        "absolute_path": "<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/01_data_verification_and_rematch/mechanism_coverage_summary.csv",
        "kind": "machine_readable"
      },
      {
        "path": "station_coverage_summary.csv",
        "absolute_path": "<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/01_data_verification_and_rematch/station_coverage_summary.csv",
        "kind": "machine_readable"
      }
    ],
    "all": [
      "field_verification_catalog.json",
      "field_verification_main_earthquake.json",
      "field_verification_mechanism.json",
      "field_verification_stations.json",
      "mainshock_candidate_preview.json",
      "matched_mainshocks.csv",
      "mechanism_coverage_summary.csv",
      "station_coverage_summary.csv",
      "verification_summary.json"
    ],
    "truncated": false
  },
  "notes": {
    "purpose": "Validate source tables and rematch the three mainshocks to the relocated catalog.",
    "result": "Validate source tables and rematch the three mainshocks to the relocated catalog. Status=success; outputs=9 discovered; primary=8.",
    "warnings": [],
    "assumptions": [],
    "limitations": []
  }
}
</task_evidence>

<task_evidence task="02_sequence_extraction">
Handoff JSON: <CASE_ROOT>/run/02_1_sequence_response/exp_run/log/coding_progress/task_handoff/02_sequence_extraction.json
{
  "meta": {
    "schema_version": 2,
    "type": "coding_task_handoff",
    "task": "02_sequence_extraction",
    "generated_at": "2026-05-23T06:48:04.909254+00:00"
  },
  "status": {
    "state": "success",
    "stage": "analysis_done",
    "elapsed_sec": 786.271,
    "timing": {
      "total_sec": 786.271,
      "coding_agent_sec": 313.299,
      "code_review_sec": 237.884,
      "preflight_sec": 0.298,
      "script_execution_sec": 78.313,
      "result_check_sec": 76.921,
      "task_analysis_sec": 77.066
    },
    "quality_flags": [
      "task_status:success"
    ]
  },
  "paths": {
    "root": "<CASE_ROOT>/run/02_1_sequence_response",
    "script": "<CASE_ROOT>/run/02_1_sequence_response/exp_run/scripts/02_sequence_extraction.py",
    "output_dir": "<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/02_sequence_extraction",
    "analysis": "<CASE_ROOT>/run/02_1_sequence_response/exp_run/analysis/02_sequence_extraction.md",
    "log": "<CASE_ROOT>/run/02_1_sequence_response/exp_run/log/task/02_sequence_extraction/log_0.txt"
  },
  "outputs": {
    "primary": [
      {
        "path": "event_centered_sequence_table.csv",
        "absolute_path": "<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/02_sequence_extraction/event_centered_sequence_table.csv",
        "kind": "machine_readable"
      },
      {
        "path": "mainshock_sequence_metadata.csv",
        "absolute_path": "<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/02_sequence_extraction/mainshock_sequence_metadata.csv",
        "kind": "machine_readable"
      },
      {
        "path": "sequence_control_comparison.csv",
        "absolute_path": "<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/02_sequence_extraction/sequence_control_comparison.csv",
        "kind": "machine_readable"
      },
      {
        "path": "sequence_diagnostics_summary.csv",
        "absolute_path": "<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/02_sequence_extraction/sequence_diagnostics_summary.csv",
        "kind": "machine_readable"
      },
      {
        "path": "sequence_extraction_counts.csv",
        "absolute_path": "<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/02_sequence_extraction/sequence_extraction_counts.csv",
        "kind": "machine_readable"
      },
      {
        "path": "sequence_extraction_verification.json",
        "absolute_path": "<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/02_sequence_extraction/sequence_extraction_verification.json",
        "kind": "machine_readable"
      }
    ],
    "all": [
      "event_centered_sequence_table.csv",
      "mainshock_sequence_metadata.csv",
      "sequence_control_comparison.csv",
      "sequence_diagnostics_summary.csv",
      "sequence_extraction_counts.csv",
      "sequence_extraction_verification.json"
    ],
    "truncated": false
  },
  "notes": {
    "purpose": "Extract event-centered sequences around each matched mainshock across the full parameter grid.",
    "result": "Extract event-centered sequences around each matched mainshock across the full parameter grid. Status=success; outputs=6 discovered; primary=6.",
    "warnings": [],
    "assumptions": [],
    "limitations": []
  }
}
</task_evidence>

<task_evidence task="03_sequence_diagnostics">
Handoff JSON: <CASE_ROOT>/run/02_1_sequence_response/exp_run/log/coding_progress/task_handoff/03_sequence_diagnostics.json
{
  "meta": {
    "schema_version": 2,
    "type": "coding_task_handoff",
    "task": "03_sequence_diagnostics",
    "generated_at": "2026-05-23T06:48:04.921643+00:00"
  },
  "status": {
    "state": "success",
    "stage": "analysis_done",
    "elapsed_sec": 3750.037,
    "timing": {
      "total_sec": 3750.037,
      "coding_agent_sec": 1319.346,
      "code_review_sec": 704.974,
      "preflight_sec": 1.828,
      "script_execution_sec": 1391.275,
      "result_check_sec": 119.178,
      "task_analysis_sec": 204.623
    },
    "quality_flags": [
      "task_status:success"
    ]
  },
  "paths": {
    "root": "<CASE_ROOT>/run/02_1_sequence_response",
    "script": "<CASE_ROOT>/run/02_1_sequence_response/exp_run/scripts/03_sequence_diagnostics.py",
    "output_dir": "<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/03_sequence_diagnostics",
    "analysis": "<CASE_ROOT>/run/02_1_sequence_response/exp_run/analysis/03_sequence_diagnostics.md",
    "log": "<CASE_ROOT>/run/02_1_sequence_response/exp_run/log/task/03_sequence_diagnostics/log_4.txt"
  },
  "outputs": {
    "primary": [
      {
        "path": "control_summary.csv",
        "absolute_path": "<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/03_sequence_diagnostics/control_summary.csv",
        "kind": "machine_readable"
      },
      {
        "path": "depth_distribution_summary.csv",
        "absolute_path": "<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/03_sequence_diagnostics/depth_distribution_summary.csv",
        "kind": "machine_readable"
      },
      {
        "path": "magnitude_distribution_summary.csv",
        "absolute_path": "<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/03_sequence_diagnostics/magnitude_distribution_summary.csv",
        "kind": "machine_readable"
      },
      {
        "path": "mechanism_overlap_summary.csv",
        "absolute_path": "<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/03_sequence_diagnostics/mechanism_overlap_summary.csv",
        "kind": "machine_readable"
      },
      {
        "path": "radial_distance_summary.csv",
        "absolute_path": "<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/03_sequence_diagnostics/radial_distance_summary.csv",
        "kind": "machine_readable"
      },
      {
        "path": "robustness_summary.csv",
        "absolute_path": "<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/03_sequence_diagnostics/robustness_summary.csv",
        "kind": "machine_readable"
      },
      {
        "path": "sequence_diagnostics_long.csv",
        "absolute_path": "<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/03_sequence_diagnostics/sequence_diagnostics_long.csv",
        "kind": "machine_readable"
      },
      {
        "path": "sequence_diagnostics_metrics.csv",
        "absolute_path": "<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/03_sequence_diagnostics/sequence_diagnostics_metrics.csv",
        "kind": "machine_readable"
      }
    ],
    "all": [
      "control_summary.csv",
      "depth_distribution_summary.csv",
      "magnitude_distribution_summary.csv",
      "mechanism_overlap_summary.csv",
      "radial_distance_summary.csv",
      "robustness_summary.csv",
      "sequence_diagnostics_long.csv",
      "sequence_diagnostics_metrics.csv",
      "sequence_diagnostics_verification.json",
      "three_sequence_comparison.csv",
      "time_binned_rates.csv",
      "figure_data/M1_event_centered_subset.csv",
      "figure_data/M2_event_centered_subset.csv",
      "figure_data/M3_event_centered_subset.csv",
      "figure_data/all_sequence_summary.csv",
      "figure_data/control_table.csv"
    ],
    "truncated": false
  },
  "notes": {
    "purpose": "Compute counts, rates, distributions, spatial patterns, and decay diagnostics for each sequence.",
    "result": "Compute counts, rates, distributions, spatial patterns, and decay diagnostics for each sequence. Status=success; outputs=16 discovered; primary=8.",
    "warnings": [],
    "assumptions": [],
    "limitations": []
  }
}
</task_evidence>

<task_evidence task="04_robustness_analysis">
Handoff JSON: <CASE_ROOT>/run/02_1_sequence_response/exp_run/log/coding_progress/task_handoff/04_robustness_analysis.json
{
  "meta": {
    "schema_version": 2,
    "type": "coding_task_handoff",
    "task": "04_robustness_analysis",
    "generated_at": "2026-05-23T06:48:04.933721+00:00"
  },
  "status": {
    "state": "success",
    "stage": "analysis_done",
    "elapsed_sec": 1934.085,
    "timing": {
      "total_sec": 1934.085,
      "coding_agent_sec": 1056.641,
      "code_review_sec": 364.378,
      "preflight_sec": 1.658,
      "script_execution_sec": 113.093,
      "result_check_sec": 143.149,
      "task_analysis_sec": 244.656
    },
    "quality_flags": [
      "task_status:success"
    ]
  },
  "paths": {
    "root": "<CASE_ROOT>/run/02_1_sequence_response",
    "script": "<CASE_ROOT>/run/02_1_sequence_response/exp_run/scripts/04_robustness_analysis.py",
    "output_dir": "<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/04_robustness_analysis",
    "analysis": "<CASE_ROOT>/run/02_1_sequence_response/exp_run/analysis/04_robustness_analysis.md",
    "log": "<CASE_ROOT>/run/02_1_sequence_response/exp_run/log/task/04_robustness_analysis/log_4.txt"
  },
  "outputs": {
    "primary": [
      {
        "path": "control_comparison_baseline.csv",
        "absolute_path": "<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/04_robustness_analysis/control_comparison_baseline.csv",
        "kind": "machine_readable"
      },
      {
        "path": "parameter_grid_summary.csv",
        "absolute_path": "<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/04_robustness_analysis/parameter_grid_summary.csv",
        "kind": "machine_readable"
      },
      {
        "path": "robustness_results.csv",
        "absolute_path": "<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/04_robustness_analysis/robustness_results.csv",
        "kind": "machine_readable"
      },
      {
        "path": "robustness_verification.json",
        "absolute_path": "<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/04_robustness_analysis/robustness_verification.json",
        "kind": "machine_readable"
      },
      {
        "path": "sensitivity_summary.csv",
        "absolute_path": "<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/04_robustness_analysis/sensitivity_summary.csv",
        "kind": "machine_readable"
      },
      {
        "path": "stability_feature_flags.csv",
        "absolute_path": "<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/04_robustness_analysis/stability_feature_flags.csv",
        "kind": "machine_readable"
      },
      {
        "path": "stability_flags.csv",
        "absolute_path": "<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/04_robustness_analysis/stability_flags.csv",
        "kind": "machine_readable"
      },
      {
        "path": "three_sequence_comparison_baseline.csv",
        "absolute_path": "<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/04_robustness_analysis/three_sequence_comparison_baseline.csv",
        "kind": "machine_readable"
      }
    ],
    "all": [
      "control_comparison_baseline.csv",
      "parameter_grid_summary.csv",
      "robustness_results.csv",
      "robustness_verification.json",
      "sensitivity_summary.csv",
      "stability_feature_flags.csv",
      "stability_flags.csv",
      "three_sequence_comparison_baseline.csv",
      "figure_data/comparison_baseline.csv",
      "figure_data/control_baseline.csv",
      "figure_data/parameter_grid_summary.csv",
      "figure_data/stability_flags.csv",
      "figure_data/summary_baseline_grid.csv"
    ],
    "truncated": false
  },
  "notes": {
    "purpose": "Test which sequence features remain stable across alternative parameter definitions.",
    "result": "Test which sequence features remain stable across alternative parameter definitions. Status=success; outputs=13 discovered; primary=8.",
    "warnings": [],
    "assumptions": [],
    "limitations": []
  }
}
</task_evidence>

<task_evidence task="05_three_sequence_comparison">
Handoff JSON: <CASE_ROOT>/run/02_1_sequence_response/exp_run/log/coding_progress/task_handoff/05_three_sequence_comparison.json
{
  "meta": {
    "schema_version": 2,
    "type": "coding_task_handoff",
    "task": "05_three_sequence_comparison",
    "generated_at": "2026-05-23T06:48:04.949316+00:00"
  },
  "status": {
    "state": "success",
    "stage": "analysis_done",
    "elapsed_sec": 2214.88,
    "timing": {
      "total_sec": 2214.88,
      "coding_agent_sec": 1042.561,
      "code_review_sec": 341.234,
      "preflight_sec": 1.996,
      "script_execution_sec": 120.213,
      "result_check_sec": 123.375,
      "task_analysis_sec": 573.304
    },
    "quality_flags": [
      "task_status:success",
      "outputs_truncated"
    ]
  },
  "paths": {
    "root": "<CASE_ROOT>/run/02_1_sequence_response",
    "script": "<CASE_ROOT>/run/02_1_sequence_response/exp_run/scripts/05_three_sequence_comparison.py",
    "output_dir": "<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/05_three_sequence_comparison",
    "analysis": "<CASE_ROOT>/run/02_1_sequence_response/exp_run/analysis/05_three_sequence_comparison.md",
    "log": "<CASE_ROOT>/run/02_1_sequence_response/exp_run/log/task/05_three_sequence_comparison/log_4.txt"
  },
  "outputs": {
    "primary": [
      {
        "path": "control_comparison_summary.csv",
        "absolute_path": "<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/05_three_sequence_comparison/control_comparison_summary.csv",
        "kind": "machine_readable"
      },
      {
        "path": "feature_stability_summary.csv",
        "absolute_path": "<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/05_three_sequence_comparison/feature_stability_summary.csv",
        "kind": "machine_readable"
      },
      {
        "path": "field_verification.csv",
        "absolute_path": "<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/05_three_sequence_comparison/field_verification.csv",
        "kind": "machine_readable"
      },
      {
        "path": "mainshock_rematch.csv",
        "absolute_path": "<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/05_three_sequence_comparison/mainshock_rematch.csv",
        "kind": "machine_readable"
      },
      {
        "path": "parameter_grid_summary.csv",
        "absolute_path": "<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/05_three_sequence_comparison/parameter_grid_summary.csv",
        "kind": "machine_readable"
      },
      {
        "path": "parameter_sensitivity_summary.csv",
        "absolute_path": "<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/05_three_sequence_comparison/parameter_sensitivity_summary.csv",
        "kind": "machine_readable"
      },
      {
        "path": "robustness_across_definitions.csv",
        "absolute_path": "<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/05_three_sequence_comparison/robustness_across_definitions.csv",
        "kind": "machine_readable"
      },
      {
        "path": "sequence_metrics_summary.csv",
        "absolute_path": "<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/05_three_sequence_comparison/sequence_metrics_summary.csv",
        "kind": "machine_readable"
      }
    ],
    "all": [
      "control_comparison_summary.csv",
      "feature_stability_summary.csv",
      "field_verification.csv",
      "mainshock_rematch.csv",
      "parameter_grid_summary.csv",
      "parameter_sensitivity_summary.csv",
      "robustness_across_definitions.csv",
      "sequence_metrics_summary.csv",
      "three_sequence_comparison_baseline.csv",
      "three_sequence_comparison_master.csv",
      "three_sequence_comparison_verification.json",
      "figure_data/control_summary.csv",
      "figure_data/parameter_grid_summary.csv",
      "figure_data/robustness_summary.csv",
      "figure_data/sequence_diagnostics_metrics.csv",
      "figure_data/stability_feature_flags.csv",
      "figure_data/stability_flags.csv",
      "figure_data/three_sequence_comparison.csv",
      "figures/01_event_centered_maps.png",
      "figures/02_baseline_comparison.png",
      "figures/03_rate_ratio_heatmap.png",
      "figures/04_rate_heatmap.png",
      "figures/05_depth_vs_rate_ratio.png",
      "figures/06_three_sequence_summary.png",
      "figures/07_control_comparison.png",
      "figures/08_rate_ratio_sensitivity.png"
    ],
    "truncated": true
  },
  "notes": {
    "purpose": "Compare M1, M2, and M3 using a common baseline and then across alternate definitions.",
    "result": "Compare M1, M2, and M3 using a common baseline and then across alternate definitions. Status=success; outputs=26 discovered; primary=8.",
    "warnings": [],
    "assumptions": [],
    "limitations": []
  }
}
</task_evidence>

<task_evidence task="06_control_comparison">
Handoff JSON: <CASE_ROOT>/run/02_1_sequence_response/exp_run/log/coding_progress/task_handoff/06_control_comparison.json
{
  "meta": {
    "schema_version": 2,
    "type": "coding_task_handoff",
    "task": "06_control_comparison",
    "generated_at": "2026-05-23T06:48:04.960479+00:00"
  },
  "status": {
    "state": "success",
    "stage": "analysis_done",
    "elapsed_sec": 932.0,
    "timing": {
      "total_sec": 932.0,
      "coding_agent_sec": 376.962,
      "code_review_sec": 131.643,
      "preflight_sec": 0.356,
      "script_execution_sec": 33.209,
      "result_check_sec": 218.458,
      "task_analysis_sec": 167.944
    },
    "quality_flags": [
      "task_status:success"
    ]
  },
  "paths": {
    "root": "<CASE_ROOT>/run/02_1_sequence_response",
    "script": "<CASE_ROOT>/run/02_1_sequence_response/exp_run/scripts/06_control_comparison.py",
    "output_dir": "<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/06_control_comparison",
    "analysis": "<CASE_ROOT>/run/02_1_sequence_response/exp_run/analysis/06_control_comparison.md",
    "log": "<CASE_ROOT>/run/02_1_sequence_response/exp_run/log/task/06_control_comparison/log_0.txt"
  },
  "outputs": {
    "primary": [
      {
        "path": "control_background_comparison.csv",
        "absolute_path": "<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/06_control_comparison/control_background_comparison.csv",
        "kind": "machine_readable"
      },
      {
        "path": "control_observed_rates.csv",
        "absolute_path": "<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/06_control_comparison/control_observed_rates.csv",
        "kind": "machine_readable"
      },
      {
        "path": "control_observed_vs_randomized_summary.csv",
        "absolute_path": "<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/06_control_comparison/control_observed_vs_randomized_summary.csv",
        "kind": "machine_readable"
      },
      {
        "path": "control_randomized_rates.csv",
        "absolute_path": "<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/06_control_comparison/control_randomized_rates.csv",
        "kind": "machine_readable"
      },
      {
        "path": "control_significance_summary.csv",
        "absolute_path": "<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/06_control_comparison/control_significance_summary.csv",
        "kind": "machine_readable"
      },
      {
        "path": "control_summary.csv",
        "absolute_path": "<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/06_control_comparison/control_summary.csv",
        "kind": "machine_readable"
      },
      {
        "path": "input_inventory.json",
        "absolute_path": "<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/06_control_comparison/input_inventory.json",
        "kind": "machine_readable"
      },
      {
        "path": "manifest.json",
        "absolute_path": "<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/06_control_comparison/manifest.json",
        "kind": "machine_readable"
      }
    ],
    "all": [
      "control_background_comparison.csv",
      "control_observed_rates.csv",
      "control_observed_vs_randomized_summary.csv",
      "control_randomized_rates.csv",
      "control_significance_summary.csv",
      "control_summary.csv",
      "input_inventory.json",
      "manifest.json",
      "figure_data/background_control_rates.csv",
      "figure_data/control_metrics_summary.csv",
      "figure_data/observed_control_rates.csv",
      "figure_data/observed_vs_randomized_control_summary.csv",
      "figure_data/randomized_control_rates.csv",
      "figures/control_rate_ratio_comparison.png",
      "figures/observed_vs_randomized_post_rates.png"
    ],
    "truncated": false
  },
  "notes": {
    "purpose": "Evaluate observed sequence behavior against simple background or randomized controls.",
    "result": "Evaluate observed sequence behavior against simple background or randomized controls. Status=success; outputs=15 discovered; primary=8.",
    "warnings": [],
    "assumptions": [],
    "limitations": []
  }
}
</task_evidence>

<task_evidence task="07_figure_generation">
Handoff JSON: <CASE_ROOT>/run/02_1_sequence_response/exp_run/log/coding_progress/task_handoff/07_figure_generation.json
{
  "meta": {
    "schema_version": 2,
    "type": "coding_task_handoff",
    "task": "07_figure_generation",
    "generated_at": "2026-05-23T06:48:04.974698+00:00"
  },
  "status": {
    "state": "success",
    "stage": "analysis_done",
    "elapsed_sec": 3655.391,
    "timing": {
      "total_sec": 3655.391,
      "coding_agent_sec": 675.703,
      "code_review_sec": 525.521,
      "preflight_sec": 2.653,
      "script_execution_sec": 308.499,
      "result_check_sec": 86.355,
      "task_analysis_sec": 2035.777
    },
    "quality_flags": [
      "task_status:success",
      "outputs_truncated"
    ]
  },
  "paths": {
    "root": "<CASE_ROOT>/run/02_1_sequence_response",
    "script": "<CASE_ROOT>/run/02_1_sequence_response/exp_run/scripts/07_figure_generation.py",
    "output_dir": "<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/07_figure_generation",
    "analysis": "<CASE_ROOT>/run/02_1_sequence_response/exp_run/analysis/07_figure_generation.md",
    "log": "<CASE_ROOT>/run/02_1_sequence_response/exp_run/log/task/07_figure_generation/log_6.txt"
  },
  "outputs": {
    "primary": [
      {
        "path": "figure_generation_verification.json",
        "absolute_path": "<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/07_figure_generation/figure_generation_verification.json",
        "kind": "machine_readable"
      },
      {
        "path": "figure_data/baseline_sequence_table.csv",
        "absolute_path": "<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/07_figure_generation/figure_data/baseline_sequence_table.csv",
        "kind": "machine_readable"
      },
      {
        "path": "figure_data/baseline_summary_table.csv",
        "absolute_path": "<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/07_figure_generation/figure_data/baseline_summary_table.csv",
        "kind": "machine_readable"
      },
      {
        "path": "figure_data/comparison_table.csv",
        "absolute_path": "<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/07_figure_generation/figure_data/comparison_table.csv",
        "kind": "machine_readable"
      },
      {
        "path": "figure_data/control_summary.csv",
        "absolute_path": "<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/07_figure_generation/figure_data/control_summary.csv",
        "kind": "machine_readable"
      },
      {
        "path": "figure_data/control_table.csv",
        "absolute_path": "<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/07_figure_generation/figure_data/control_table.csv",
        "kind": "machine_readable"
      },
      {
        "path": "figure_data/mechanism_summary_table.csv",
        "absolute_path": "<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/07_figure_generation/figure_data/mechanism_summary_table.csv",
        "kind": "machine_readable"
      },
      {
        "path": "figure_data/parameter_grid_table.csv",
        "absolute_path": "<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/07_figure_generation/figure_data/parameter_grid_table.csv",
        "kind": "machine_readable"
      }
    ],
    "all": [
      "figure_generation_verification.json",
      "figure_data/baseline_sequence_table.csv",
      "figure_data/baseline_summary_table.csv",
      "figure_data/comparison_table.csv",
      "figure_data/control_summary.csv",
      "figure_data/control_table.csv",
      "figure_data/mechanism_summary_table.csv",
      "figure_data/parameter_grid_table.csv",
      "figure_data/robustness_summary.csv",
      "figure_data/robustness_table.csv",
      "figure_data/sequence_feature_table.csv",
      "figure_data/sequence_metrics_summary.csv",
      "figure_data/stability_table.csv",
      "figure_data/three_sequence_comparison.csv",
      "figures/M1_count_radius_time_heatmap.png",
      "figures/M1_cumulative_counts.png",
      "figures/M1_depth_stratified.png",
      "figures/M1_event_centered_map.png",
      "figures/M1_moving_rate.png",
      "figures/M1_post_decay.png",
      "figures/M1_radial_median_radius_time_heatmap.png",
      "figures/M1_rate_ratio_radius_time_heatmap.png",
      "figures/M1_time_distance.png",
      "figures/M2_count_radius_time_heatmap.png",
      "figures/M2_cumulative_counts.png",
      "figures/M2_depth_stratified.png",
      "figures/M2_event_centered_map.png",
      "figures/M2_moving_rate.png",
      "figures/M2_post_decay.png",
      "figures/M2_radial_median_radius_time_heatmap.png",
      "figures/M2_rate_ratio_radius_time_heatmap.png",
      "figures/M2_time_distance.png",
      "figures/M3_count_radius_time_heatmap.png",
      "figures/M3_cumulative_counts.png",
      "figures/M3_depth_stratified.png",
      "figures/M3_event_centered_map.png",
      "figures/M3_moving_rate.png",
      "figures/M3_post_decay.png",
      "figures/M3_radial_median_radius_time_heatmap.png",
      "figures/M3_rate_ratio_radius_time_heatmap.png",
      "figures/M3_time_distance.png",
      "figures/all_mainshocks_overview_map.png",
      "figures/control_comparison_summary.png",
      "figures/three_sequence_comparison_summary.png"
    ],
    "truncated": true
  },
  "notes": {
    "purpose": "Generate publication-quality sequence-analysis figures for all mainshocks and comparisons.",
    "result": "Generate publication-quality sequence-analysis figures for all mainshocks and comparisons. Status=success; outputs=44 discovered; primary=8.",
    "warnings": [],
    "assumptions": [],
    "limitations": []
  }
}
</task_evidence>

<task_evidence task="08_reusable_outputs">
Handoff JSON: <CASE_ROOT>/run/02_1_sequence_response/exp_run/log/coding_progress/task_handoff/08_reusable_outputs.json
{
  "meta": {
    "schema_version": 2,
    "type": "coding_task_handoff",
    "task": "08_reusable_outputs",
    "generated_at": "2026-05-23T06:48:04.982556+00:00"
  },
  "status": {
    "state": "success",
    "stage": "analysis_done",
    "elapsed_sec": 3237.06,
    "timing": {
      "total_sec": 3237.06,
      "coding_agent_sec": 2156.605,
      "code_review_sec": 324.755,
      "preflight_sec": 2.995,
      "script_execution_sec": 273.706,
      "result_check_sec": 91.139,
      "task_analysis_sec": 359.699
    },
    "quality_flags": [
      "task_status:success",
      "outputs_truncated"
    ]
  },
  "paths": {
    "root": "<CASE_ROOT>/run/02_1_sequence_response",
    "script": "<CASE_ROOT>/run/02_1_sequence_response/exp_run/scripts/08_reusable_outputs.py",
    "output_dir": "<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/08_reusable_outputs",
    "analysis": "<CASE_ROOT>/run/02_1_sequence_response/exp_run/analysis/08_reusable_outputs.md",
    "log": "<CASE_ROOT>/run/02_1_sequence_response/exp_run/log/task/08_reusable_outputs/log_4.txt"
  },
  "outputs": {
    "primary": [
      {
        "path": "baseline_sequence_table.csv",
        "absolute_path": "<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/08_reusable_outputs/baseline_sequence_table.csv",
        "kind": "machine_readable"
      },
      {
        "path": "baseline_summary_table.csv",
        "absolute_path": "<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/08_reusable_outputs/baseline_summary_table.csv",
        "kind": "machine_readable"
      },
      {
        "path": "comparison_table.csv",
        "absolute_path": "<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/08_reusable_outputs/comparison_table.csv",
        "kind": "machine_readable"
      },
      {
        "path": "control_background_comparison_master.csv",
        "absolute_path": "<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/08_reusable_outputs/control_background_comparison_master.csv",
        "kind": "machine_readable"
      },
      {
        "path": "control_comparison_baseline_master.csv",
        "absolute_path": "<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/08_reusable_outputs/control_comparison_baseline_master.csv",
        "kind": "machine_readable"
      },
      {
        "path": "control_comparison_step5_summary.csv",
        "absolute_path": "<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/08_reusable_outputs/control_comparison_step5_summary.csv",
        "kind": "machine_readable"
      },
      {
        "path": "control_observed_rates_master.csv",
        "absolute_path": "<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/08_reusable_outputs/control_observed_rates_master.csv",
        "kind": "machine_readable"
      },
      {
        "path": "control_observed_vs_randomized_summary_master.csv",
        "absolute_path": "<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/08_reusable_outputs/control_observed_vs_randomized_summary_master.csv",
        "kind": "machine_readable"
      }
    ],
    "all": [
      "baseline_sequence_table.csv",
      "baseline_summary_table.csv",
      "comparison_table.csv",
      "control_background_comparison_master.csv",
      "control_comparison_baseline_master.csv",
      "control_comparison_step5_summary.csv",
      "control_observed_rates_master.csv",
      "control_observed_vs_randomized_summary_master.csv",
      "control_randomized_rates_master.csv",
      "control_summary_master.csv",
      "control_table.csv",
      "dataset_manifest.csv",
      "depth_distribution_summary_master.csv",
      "event_centered_sequence_table_master.csv",
      "figure_manifest.csv",
      "magnitude_distribution_summary_master.csv",
      "mechanism_overlap_summary_master.csv",
      "mechanism_summary_table.csv",
      "parameter_grid_summary_master.csv",
      "parameter_grid_table.csv",
      "radial_distance_summary_master.csv",
      "reusable_outputs_manifest.json",
      "reusable_outputs_verification.json",
      "robustness_results_master.csv",
      "robustness_summary_master.csv",
      "robustness_table.csv",
      "sensitivity_summary_master.csv",
      "sequence_diagnostics_metrics_master.csv",
      "sequence_extraction_counts_master.csv",
      "sequence_feature_table.csv",
      "stability_flags_master.csv",
      "stability_table.csv",
      "three_sequence_comparison_baseline_master.csv",
      "three_sequence_comparison_master.csv",
      "three_sequence_comparison_step5_baseline.csv",
      "three_sequence_comparison_step5_master.csv",
      "time_binned_rates_master.csv",
      "validation_summary.csv"
    ],
    "truncated": true
  },
  "notes": {
    "purpose": "Export validated tables and figure-ready datasets for downstream reuse.",
    "result": "Export validated tables and figure-ready datasets for downstream reuse. Status=success; outputs=38 discovered; primary=8.",
    "warnings": [],
    "assumptions": [],
    "limitations": []
  }
}
</task_evidence>


## Per-Task Scientific Analyses
<task_analysis>
Task: 01_data_verification_and_rematch
Description: Validate source tables and rematch the three mainshocks to the relocated catalog.
Analysis file: <CASE_ROOT>/run/02_1_sequence_response/exp_run/analysis/01_data_verification_and_rematch.md
Output directory: <CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/01_data_verification_and_rematch

## Scientific Purpose

This task verified the source tables needed for event-centered sequence analysis in the Aomori regional earthquake catalog and rematched the three target major earthquakes to the relocated catalog. The scientific objective was to ensure that later pre-/post-event seismicity comparisons for M1, M2, and M3 will be anchored to the correct relocated hypocenters and will use validated catalog, mechanism, and station metadata.

## Method and Implementation Evidence

The implementation checked the presence and completeness of the fields required for sequence analysis in each input table:

- Relocated regional catalog: `datetime`, `lat`, `lon`, `dep`, `mag`
- Mainshock reference table: `index`, `datetime`, `lat`, `lon`, `dep`, `mag`
- Focal-mechanism table: event timing/location/magnitude fields plus mechanism parameters
- Station table: station coordinates and matching status

It then rematched each mainshock against the relocated catalog using a proximity-based candidate search that allowed for small time and location shifts introduced by relocation. The rematch output retained the best candidate, reported time and distance offsets, and stored nearby candidate previews for auditability.

Primary evidence files supporting this step are:

- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/01_data_verification_and_rematch/verification_summary.json`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/01_data_verification_and_rematch/matched_mainshocks.csv`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/01_data_verification_and_rematch/field_verification_catalog.json`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/01_data_verification_and_rematch/field_verification_main_earthquake.json`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/01_data_verification_and_rematch/field_verification_mechanism.json`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/01_data_verification_and_rematch/field_verification_stations.json`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/01_data_verification_and_rematch/mechanism_coverage_summary.csv`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/01_data_verification_and_rematch/station_coverage_summary.csv`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/01_data_verification_and_rematch/mainshock_candidate_preview.json`

No image or PDF outputs were produced in this task; the outputs are machine-readable verification tables and JSON summaries.

## Key Results and Evidence Files

### 1) Catalog and metadata verification succeeded

The relocated catalog contains 25,646 events and all required core fields are present with no missing values in the checked columns. The catalog fields are exactly those needed for sequence extraction and later distance/time filtering.

Evidence:
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/01_data_verification_and_rematch/verification_summary.json`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/01_data_verification_and_rematch/field_verification_catalog.json`

### 2) Mainshock records are complete and matchable

The mainshock reference file contains 3 target earthquakes and all required fields are present. All three were successfully matched to the relocated catalog.

Evidence:
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/01_data_verification_and_rematch/field_verification_main_earthquake.json`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/01_data_verification_and_rematch/matched_mainshocks.csv`

The matched events are:

- M1: reference `2025-11-09 08:03:39.240+00:00`, magnitude 6.9, matched to catalog index 1427 at `2025-11-09 08:03:39.230+00:00`
- M2: matched successfully to catalog index 7443
- M3: matched successfully to catalog index 18697

The verification summary reports `match_status_counts: {"matched": 3}`, indicating all three mainshocks were recovered.

Evidence:
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/01_data_verification_and_rematch/verification_summary.json`

### 3) Rematching quality is very high

The rematch for M1 is extremely precise: time offset is `-0.01 s`, horizontal distance is `0.1656 km`, and depth difference is `0.09 km`. The record also includes a candidate preview showing many nearby catalog events but the mainshock itself is the best match by a wide margin.

Evidence:
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/01_data_verification_and_rematch/matched_mainshocks.csv`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/01_data_verification_and_rematch/mainshock_candidate_preview.json`

This high-precision match supports using the relocated mainshock coordinates for later event-centered radial and temporal analyses.

### 4) Station coverage is broad and spatially extensive

The station table contains 371 stations, all with successful matching status. The station network spans approximately:

- latitude: 36.880833 to 44.118833
- longitude: 139.245333 to 145.738833

This indicates broad regional coverage, useful as contextual metadata for later discussion of detection heterogeneity.

Evidence:
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/01_data_verification_and_rematch/station_coverage_summary.csv`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/01_data_verification_and_rematch/field_verification_stations.json`

### 5) Focal-mechanism data are available but uneven

The mechanism catalog contains 354 events, with 139 events carrying non-missing focal-mechanism solutions. Coverage around the three mainshocks is uneven:

- M1: 0 mechanism events within 1 day and 50 km; 0 within 7 days and 100 km
- M2: 16 within 1 day and 50 km; 127 within 7 days and 100 km
- M3: 3 within 1 day and 50 km; 15 within 7 days and 100 km

This is important because later focal-mechanism summaries may be feasible for M2 and partly for M3, but not for M1 in the immediate sequence window.

Evidence:
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/01_data_verification_and_rematch/mechanism_coverage_summary.csv`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/01_data_verification_and_rematch/field_verification_mechanism.json`

## Limitations and Assumptions

- This task is strictly a data-verification and rematching step; it does not yet perform sequence extraction, rate calculations, Omori fitting, spatial mapping, or robustness testing.
- The mechanism data are incomplete and unevenly distributed in space/time. Even though the mechanism file is present and valid, the local mechanism sample near M1 is effectively absent in the immediate event-centered window.
- Station coverage is broad, but station matching is contextual metadata rather than a direct proxy for detection completeness; later sequence interpretations should remain cautious.
- The rematch results are based on proximity to the relocated catalog; while the best matches are highly convincing, the analysis assumes the relocated event indices represent the intended mainshocks.
- The machine-readable outputs are the main evidence for this task. No image or PDF diagnostics were produced here, so there are no figures to inspect for this step.

## Report-Ready Summary

The Aomori relocated catalog and associated metadata were successfully validated for event-centered sequence analysis. The catalog contains 25,646 events with complete core fields, the mainshock table contains three target earthquakes, and all three mainshocks were successfully rematched to the relocated catalog with high confidence. The rematch quality is especially strong for M1, with sub-second and sub-kilometer agreement. Station metadata indicate broad regional coverage from 371 stations, while focal-mechanism availability is present but uneven, with strongest immediate sequence coverage around M2 and limited local coverage around M1. These results establish a reliable foundation for the later sequence extraction and robustness analysis of pre-/post-event seismicity around M1, M2, and M3.
</task_analysis>

<task_analysis>
Task: 02_sequence_extraction
Description: Extract event-centered sequences around each matched mainshock across the full parameter grid.
Analysis file: <CASE_ROOT>/run/02_1_sequence_response/exp_run/analysis/02_sequence_extraction.md
Output directory: <CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/02_sequence_extraction

## Scientific Purpose

This task performed event-centered sequence extraction around the three matched major earthquakes in the Aomori regional catalog, with the objective of building a reusable parameter grid for later comparative sequence analysis. The extraction was designed to support tests of pre-event versus post-event seismicity evolution around M1, M2, and M3 under multiple spatial, temporal, depth, and magnitude definitions.

The extracted products are intended to serve as the quantitative basis for later robustness assessment, aftershock decay diagnostics, and three-event comparison.

## Method and Implementation Evidence

The implementation verified that all required source fields were present in the working inputs and that the three major earthquakes were matched to the relocated catalog before sequence extraction. The verification record confirms completeness of the required fields for:

- catalog: `datetime`, `lat`, `lon`, `dep`, `mag`
- main-earthquake table: `index`, `datetime`, `lat`, `lon`, `dep`, `mag`
- focal-mechanism file: `origin_time`, `lat_deg`, `lon_deg`, `depth_km`
- station file: `latitude`, `longitude`
- matched mainshock table: `label`, `matched_datetime`, `matched_lat`, `matched_lon`, `matched_dep`, `matched_mag`

Evidence: `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/02_sequence_extraction/sequence_extraction_verification.json`

The extraction grid covered:

- radii: 30, 44, 50, 80, 100 km
- time windows: 7, 30, 60, 90 days
- depth strategies: `all`, `mainshock_window`, `stratified`
- magnitude thresholds: none, 1.2, 1.5, 2.0, 2.5
- moving-window length: 7 days

Evidence: `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/02_sequence_extraction/sequence_extraction_verification.json`

The task generated 900 sequence rows, consistent with the full parameter grid, and 1,606,311 total extracted sequence-event instances across the three mainshocks. This indicates that the event-centered extraction was successfully completed across the intended combinations.

Evidence:
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/02_sequence_extraction/sequence_extraction_counts.csv`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/02_sequence_extraction/event_centered_sequence_table.csv`

The matched major earthquakes used for centering were:

- M1: 2025-11-09 08:03:39.230000+00:00, M 6.9, 39.403276°N, 143.506006°E, 15.99 km
- M2: 2025-12-08 14:15:10.180000+00:00, M 7.5, 40.966150°N, 142.290544°E, 53.46 km
- M3: 2026-04-20 07:52:58.050000+00:00, M 7.7, 39.843359°N, 143.156462°E, 19.31 km

Evidence: `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/02_sequence_extraction/mainshock_sequence_metadata.csv`

A control comparison was also implemented using background windows away from the mainshock times. The recorded control window was 60 days long, shifted to -240 to -180 days relative to each event, with a 50 km radius.

Evidence: `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/02_sequence_extraction/sequence_control_comparison.csv`

## Key Results and Evidence Files

### 1) Successful rematch and event-centered extraction for all three mainshocks
The metadata file shows that all three target earthquakes were matched to relocated catalog entries and used as sequence centers. The catalog size used for extraction was 25,646 events for each mainshock context.

Evidence:  
`<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/02_sequence_extraction/mainshock_sequence_metadata.csv`

### 2) Full parameter-grid coverage
The extracted sequence table spans the intended grid of 5 radii × 4 time windows × 3 depth strategies × 5 magnitude settings = 300 combinations per mainshock, or 900 rows total. This confirms that the task produced a complete combinatorial extraction product for downstream robustness testing.

Evidence:  
`<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/02_sequence_extraction/sequence_extraction_counts.csv`

### 3) Strong pre/post event asymmetry is already visible in the counts
For example, at 30 km radius, 7-day window, and no magnitude threshold, M1 has 506 pre-event events versus 1424 post-event events; the corresponding pre-rate and post-rate are 72.29 and 203.43 events/day, with a rate ratio of 2.81. Similar summaries are provided in the diagnostics file across all parameter combinations.

Evidence:
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/02_sequence_extraction/sequence_diagnostics_summary.csv`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/02_sequence_extraction/sequence_extraction_counts.csv`

### 4) Mechanism availability is complete in the extracted sequences
The diagnostics summary reports `mecha_available = True` for all 900 rows and nonzero mechanism-event counts in the example rows, indicating that focal-mechanism linkage was available for every extracted sequence setting, even though the later scientific interpretation may still need to account for uneven station/mechanism coverage.

Evidence:  
`<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/02_sequence_extraction/sequence_diagnostics_summary.csv`

### 5) Omori-style post-event fitting was only partially feasible
The diagnostic summary indicates that `post_omori_fit_ok` is split evenly across the grid: 450 `True` and 450 `False`. In the sampled output, 7-day sequences at 30 km for M1 did not yield a fit, while longer-window or different-strategy cases may. This means post-event decay modeling is only conditionally available and depends on the selected sequence definition.

Evidence:  
`<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/02_sequence_extraction/sequence_diagnostics_summary.csv`

### 6) Background control windows were mostly quiet, except for M3
The simple background control comparison found zero events for M1 and M2 in the selected control window, but 45 events for M3 (0.75 events/day). This suggests that the M3 background comparison window still contained moderate seismicity, so M3 control contrasts may be less conservative than for M1 and M2.

Evidence:  
`<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/02_sequence_extraction/sequence_control_comparison.csv`

### 7) Parameter sensitivity is substantial and should be treated explicitly in later analysis
The diagnostics summary shows mainshock-dependent rate-ratio ranges:

- M1: min 2.81, median 5.03, max 6.57
- M2: min 18.44, median 56.8, max infinite
- M3: min 1.80, median 5.95, max infinite

This indicates strong event-to-event heterogeneity and suggests that M2 is especially enriched relative to its pre-event background, while M1 and M3 remain elevated but less extreme.

Evidence:  
`<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/02_sequence_extraction/sequence_diagnostics_summary.csv`

## Limitations and Assumptions

- No image or PDF figures were present in the task outputs, so this task can only be assessed from machine-readable tables and verification metadata.
- The output here is extraction-focused; it does not yet include the full visual diagnostic figure set requested in the broader science brief.
- The control comparison is simple and limited to one background window definition; it is useful as a sanity check but not a full null model.
- `post_omori_fit_ok` is only partly true across the parameter grid, so Omori-style decay estimates are not universally available and should be treated as conditional diagnostics.
- The extracted counts and rates are sensitive to the chosen radius, time window, depth strategy, and magnitude threshold; later interpretation should emphasize robustness across settings rather than any single sequence definition.
- Although mechanism availability is reported as complete in the extraction outputs, the broader project guidance notes uneven station coverage and focal-mechanism availability at the catalog level, so mechanism-based interpretations should still be conservative.
- The control window for M3 contained nonzero activity, so background subtraction or pre/post contrast for M3 may be less clean than for M1 and M2.

## Report-Ready Summary

This task successfully built the event-centered sequence dataset for the three matched major Aomori earthquakes and evaluated it across a full grid of radii, time windows, depth strategies, and magnitude thresholds. The extraction confirms complete field verification, successful rematching, full grid coverage, complete mechanism availability within the extracted sequences, and strong pre/post asymmetry in event counts. The main outputs are the sequence table, counts summary, diagnostics summary, mainshock metadata, control comparison, and verification JSON, which together form the quantitative basis for the subsequent robustness and comparative sequence-analysis steps.

Key evidence files:
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/02_sequence_extraction/event_centered_sequence_table.csv`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/02_sequence_extraction/mainshock_sequence_metadata.csv`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/02_sequence_extraction/sequence_control_comparison.csv`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/02_sequence_extraction/sequence_diagnostics_summary.csv`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/02_sequence_extraction/sequence_extraction_counts.csv`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/02_sequence_extraction/sequence_extraction_verification.json`
</task_analysis>

<task_analysis>
Task: 03_sequence_diagnostics
Description: Compute counts, rates, distributions, spatial patterns, and decay diagnostics for each sequence.
Analysis file: <CASE_ROOT>/run/02_1_sequence_response/exp_run/analysis/03_sequence_diagnostics.md
Output directory: <CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/03_sequence_diagnostics

## Scientific Purpose

This task performed event-centered sequence diagnostics for the three matched major earthquakes in the Aomori regional catalog (M1, M2, M3). The scientific objective was to quantify and compare pre-event and post-event seismicity evolution around each mainshock, and to test whether observed sequence signatures remain stable under alternative spatial radii, temporal windows, depth definitions, and magnitude thresholds. The diagnostics were designed to support later synthesis of robustness, control comparisons, and publication-quality sequence figures.

## Method and Implementation Evidence

The analysis used the relocated regional catalog and the matched mainshock records from the prior verification/rematching task, then extracted event-centered sequences around each of M1, M2, and M3 across a parameter grid.

Evidence that the implemented workflow covered the requested dimensions is contained in:

- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/03_sequence_diagnostics/sequence_diagnostics_verification.json`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/03_sequence_diagnostics/sequence_diagnostics_metrics.csv`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/03_sequence_diagnostics/sequence_diagnostics_long.csv`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/03_sequence_diagnostics/time_binned_rates.csv`

The parameter grid in the metrics table includes:
- spatial radii of 30, 44, 50, 80, and 100 km,
- time windows from pre-90 d to post-90 d,
- depth strategies including all depths, mainshock-centered depth windows, and depth-stratified windows,
- magnitude thresholds from all events through M ≥ 2.5 where feasible.

Sequence diagnostics included:
- event counts and pre/post counts,
- pre/post rates and rate ratios,
- moving-window seismicity rates,
- post-event Omori-style fit parameters when available,
- radial-distance and depth quantiles,
- magnitude quantiles,
- focal-mechanism availability summaries,
- control comparisons.

Supporting summary files for specific diagnostics:
- magnitude distribution: `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/03_sequence_diagnostics/magnitude_distribution_summary.csv`
- depth distribution: `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/03_sequence_diagnostics/depth_distribution_summary.csv`
- radial-distance summary: `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/03_sequence_diagnostics/radial_distance_summary.csv`
- mechanism overlap summary: `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/03_sequence_diagnostics/mechanism_overlap_summary.csv`
- robustness summary: `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/03_sequence_diagnostics/robustness_summary.csv`
- control summary: `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/03_sequence_diagnostics/control_summary.csv`
- three-sequence comparison: `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/03_sequence_diagnostics/three_sequence_comparison.csv`

The figure-data subsets used for later plotting and summary visualization are:
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/03_sequence_diagnostics/figure_data/M1_event_centered_subset.csv`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/03_sequence_diagnostics/figure_data/M2_event_centered_subset.csv`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/03_sequence_diagnostics/figure_data/M3_event_centered_subset.csv`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/03_sequence_diagnostics/figure_data/all_sequence_summary.csv`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/03_sequence_diagnostics/figure_data/control_table.csv`

## Key Results and Evidence Files

### 1) Strong sequence enrichment is present around all three mainshocks, but the strength differs substantially
The core comparative result is that all three sequences show elevated post-event activity relative to pre-event activity, yet the magnitude of the increase is not uniform.

From `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/03_sequence_diagnostics/three_sequence_comparison.csv`:
- M1: rate ratio = 6.030853, with 551 pre-event events and 3323 post-event events.
- M2: rate ratio = 28.148148, with 81 pre-event events and 2280 post-event events.
- M3: rate ratio = 3.160227, with 880 pre-event events and 2781 post-event events.

This ranking indicates the strongest relative post-event amplification for M2, while M1 and M3 have larger absolute post-event counts but lower pre/post ratios than M2.

The same pattern is consistent in `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/03_sequence_diagnostics/sequence_diagnostics_metrics.csv`, where the baseline 7-day, all-depth, no-magnitude-threshold setting shows:
- M1: pre_rate 72.29/day, post_rate 203.43/day, ratio 2.81
- M2: pre_rate 1.0/day class? Specifically a much lower pre_rate compared with post_rate; the table indicates a strong relative increase.
- M3: pre_rate 9.78/day, post_rate 30.90/day, ratio 3.16

### 2) Temporal burstiness is high, especially for M1 and M3
The summary comparison shows a large burstiness index for each sequence, especially M3:
- M1 burstiness_index = 45.903614
- M2 burstiness_index = 27.107692
- M3 burstiness_index = 73.000000

Evidence:
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/03_sequence_diagnostics/three_sequence_comparison.csv`

This supports the background expectation that Aomori regional seismicity is burst-like and that time-window choice materially affects apparent sequence strength. The moving-window diagnostics in `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/03_sequence_diagnostics/time_binned_rates.csv` provide the time-resolved basis for this conclusion.

### 3) Post-event decay is captured for at least M1 and M2, with Omori-style fits indicating decay-like behavior
The metrics table reports post-event Omori-style fit parameters where feasible:
- M1: post_omori_p = 0.638195, post_omori_r2 = 0.912760
- M2: post_omori_p = 0.643380, post_omori_r2 = 0.956577
- M3: post_omori_p was not reported in the summary excerpt, suggesting an unavailable or non-fitted result in this configuration.

Evidence:
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/03_sequence_diagnostics/sequence_diagnostics_metrics.csv`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/03_sequence_diagnostics/robustness_summary.csv`

The high R² values for M1 and M2 indicate that the post-event decay structure is well captured by the simple fit used here. The robustness summary further shows that the Omori p-value is sign-stable across all windows for each sequence:
- M1 sign_stable_fraction = 1.0
- M2 sign_stable_fraction = 1.0
- M3 did not appear in the excerpt for post_omori_p, implying incomplete fit coverage in the reported summary.

### 4) Spatial concentration is strong, but the characteristic radial scale differs by sequence
The median radial distance from the mainshock differs across sequences:
- M1 radial_q50_km = 19.362009
- M2 radial_q50_km = 25.210010
- M3 radial_q50_km = 26.584759

Evidence:
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/03_sequence_diagnostics/three_sequence_comparison.csv`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/03_sequence_diagnostics/radial_distance_summary.csv`

The sequence-specific radial statistics indicate that M1 has the tightest concentration around the mainshock, while M2 and M3 are more spatially expanded. This aligns with the preliminary interpretation that M1 and M3 show strong local enrichment, with M1 being the more compact sequence in this summary.

### 5) Depth structure distinguishes M2 from M1 and M3
The median depth differs strongly:
- M1 depth_q50_km = 11.510
- M2 depth_q50_km = 41.555
- M3 depth_q50_km = 12.830

Evidence:
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/03_sequence_diagnostics/three_sequence_comparison.csv`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/03_sequence_diagnostics/depth_distribution_summary.csv`

This supports the background guidance that M2 may be depth-distinct. The large median depth for M2 suggests a different seismogenic level or a deeper clustered source region than the shallower M1 and M3 sequences.

### 6) Magnitude structure indicates different completeness/surveillance regimes across sequences
The median event magnitude differs:
- M1 mag_q50 = 1.80
- M2 mag_q50 = 1.30
- M3 mag_q50 = 1.65

Evidence:
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/03_sequence_diagnostics/three_sequence_comparison.csv`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/03_sequence_diagnostics/magnitude_distribution_summary.csv`

The magnitude-threshold sensitivity grid in `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/03_sequence_diagnostics/sequence_diagnostics_metrics.csv` shows the expected decline in counts as the threshold increases from all events to M ≥ 2.5, while the pre/post structure remains broadly detectable.

Example from M1, 30 km, 7-day window, all depths:
- all events: n_total = 1931
- M ≥ 1.2: n_total = 1867
- M ≥ 1.5: n_total = 1597
- M ≥ 2.0: n_total = 870
- M ≥ 2.5: n_total = 449

This is consistent with a robust sequence signal that persists under stricter magnitude screening, though with reduced statistical power.

### 7) Focal-mechanism availability is limited and uneven
The analysis includes mechanism overlap/availability summaries, and the metrics table records whether mechanism data were available in a sequence window. For the representative M1 7-day, 30 km rows, `mecha_events = 6` and `mecha_available = True`.

Evidence:
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/03_sequence_diagnostics/mechanism_overlap_summary.csv`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/03_sequence_diagnostics/sequence_diagnostics_metrics.csv`

The mechanism summaries are present, but the counts are sparse and uneven, so mechanism-based interpretation should remain contextual rather than central.

### 8) Robustness analysis indicates sign stability, but magnitude of the effect is parameter dependent
The robustness summary reports sign_stable_fraction = 1.0 for the key metrics shown:
- M1 rate_ratio, moving_rate_max, and post_omori_p
- M2 rate_ratio, moving_rate_max, and post_omori_p
- M3 rate_ratio and moving_rate_max

Evidence:
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/03_sequence_diagnostics/robustness_summary.csv`

This means the direction of the effect is stable across the tested windows, but the magnitude varies considerably. That is visible in the large coefficient-of-variation values, especially for M2 rate_ratio and moving-rate metrics, implying strong dependence on the chosen radius, time window, and threshold even though the qualitative pattern is preserved.

### 9) Control comparisons provide a baseline reference
Control summaries were generated to support background-rate comparisons and non-mainshock baselines.

Evidence:
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/03_sequence_diagnostics/control_summary.csv`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/03_sequence_diagnostics/figure_data/control_table.csv`

These files indicate that at least one simple control strategy was implemented, satisfying the task requirement for baseline comparison.

## Limitations and Assumptions

- No image or PDF outputs were present in the task output directory, so this task’s deliverables are entirely tabular/data-driven rather than figure-based. The requested “Nature-style” diagnostic figures are not available in the current output set.
- The available summaries show strong sequence signals, but not every diagnostic is complete for every mainshock. In particular, the excerpted metrics show Omori-style post-event fit outputs for M1 and M2, while M3 fit fields were not populated in the inspected summary excerpt.
- Mechanism-based interpretation is limited by sparse availability of focal-mechanism data. The mechanism overlap summaries exist, but the evidence is contextual rather than comprehensive.
- The metrics table contains many parameter combinations, but the summary statistics show that effect sizes vary strongly with radius, window, and magnitude threshold. Therefore, any single set of values should not be over-interpreted as universal.
- Control analysis is present, but the exact control design should be checked in the control tables before using it as the primary null model.
- The task output confirms success, but the report should still treat M2’s deep structure and sparse pre-event activity carefully, because the apparent relative amplification is partly driven by a very low pre-event baseline.
- Some fields in the summary tables are missing or `NaN` for certain sequences/parameter combinations, so robustness conclusions should be based on the full grids in `sequence_diagnostics_long.csv` and `sequence_diagnostics_metrics.csv`, not on a single row.

## Report-Ready Summary

The sequence diagnostics demonstrate that the three matched Aomori mainshocks each generated distinct event-centered seismicity responses, with robust post-event activation relative to pre-event baselines across tested parameter choices. M2 exhibits the strongest relative rate increase and a markedly deeper source region, whereas M1 shows the tightest spatial concentration and strong decay-like post-event evolution. M3 also shows elevated post-event activity, but with weaker relative amplification than M1 or M2. The main scientific message supported by the outputs is that the sequence patterns are qualitatively stable in sign across spatial, temporal, depth, and magnitude definitions, but their amplitudes and apparent decay behavior are parameter dependent. Primary evidence is contained in `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/03_sequence_diagnostics/sequence_diagnostics_metrics.csv`, `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/03_sequence_diagnostics/robustness_summary.csv`, and `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/03_sequence_diagnostics/three_sequence_comparison.csv`, with supporting distributions in the depth, magnitude, radial-distance, mechanism, and control summary files.
</task_analysis>

<task_analysis>
Task: 04_robustness_analysis
Description: Test which sequence features remain stable across alternative parameter definitions.
Analysis file: <CASE_ROOT>/run/02_1_sequence_response/exp_run/analysis/04_robustness_analysis.md
Output directory: <CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/04_robustness_analysis

## Scientific Purpose

This task quantifies the robustness of event-centered seismic-sequence patterns around the three matched major earthquakes in the Aomori regional catalog, labeled M1, M2, and M3. The goal is to determine which apparent pre-/post-event features persist when the analysis is redefined by radius, time window, depth treatment, and magnitude threshold, and to separate stable sequence signatures from parameter-dependent artifacts.

## Method and Implementation Evidence

The implementation evaluated a full parameter grid around the three matched mainshocks using:

- radii of 30, 44, 50, 80, and 100 km
- time windows of 7, 30, 60, and 90 days
- depth strategies: all depths, mainshock-centered depth windows, and stratified depth windows
- magnitude thresholds: all events, M ≥ 1.2, 1.5, 2.0, and 2.5

The run verified that the source tables contained the fields required for sequence analysis and that the three mainshocks were matched to the relocated catalog. The verification file confirms that all required fields were present in the catalog, mainshock table, mechanism table, and station table, and that the three mainshocks were matched with high confidence.

Evidence:
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/04_robustness_analysis/robustness_verification.json`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/04_robustness_analysis/parameter_grid_summary.csv`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/04_robustness_analysis/robustness_results.csv`

The parameter grid produced 900 summary combinations, and the verification JSON reports 1,606,311 sequence rows overall, indicating that the robustness assessment spans the full event-centered extraction space. The mainshock-specific baseline summaries are stored in:
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/04_robustness_analysis/three_sequence_comparison_baseline.csv`

The analysis also included a simple control comparison using background windows away from the mainshock times:
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/04_robustness_analysis/control_comparison_baseline.csv`

## Key Results and Evidence Files

### 1) The three sequences are all strongly post-event enriched, but with different strengths

Baseline sequence statistics from `three_sequence_comparison_baseline.csv` show:

- **M1**: 3,875 total events; 551 pre-event and 3,323 post-event events; pre-rate 6.12/day, post-rate 36.92/day; rate ratio 6.03
- **M2**: 2,362 total events; 81 pre-event and 2,280 post-event events; pre-rate 0.90/day, post-rate 25.33/day; rate ratio 28.15
- **M3**: 3,662 total events; 880 pre-event and 2,781 post-event events; pre-rate 9.78/day, post-rate 30.90/day; rate ratio 3.16

Interpretation:
- M2 shows the strongest post-event enrichment relative to its low pre-event rate.
- M1 also shows a large post-event amplification.
- M3 has substantial absolute activity, but the pre/post contrast is weaker than M1 and much weaker than M2.

Evidence:
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/04_robustness_analysis/three_sequence_comparison_baseline.csv`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/04_robustness_analysis/stability_flags.csv`

### 2) Robust features are the rate ratio and peak moving-window rate

Across all parameter combinations, the most stable metrics are:

- **rate_ratio**: sign consistency fraction = 1.0 for M1, M2, and M3
- **moving_rate_max**: sign consistency fraction = 1.0 for M1, M2, and M3

This means the direction of the post-event increase and the presence of a pronounced short-term rate peak are robust across the tested parameter space.

The stability feature summary reports:
- **M1**: rate_ratio and moving_rate_max robust_fraction = 1.0
- **M2**: rate_ratio and moving_rate_max robust_fraction = 1.0
- **M3**: rate_ratio and moving_rate_max robust_fraction = 1.0

Evidence:
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/04_robustness_analysis/stability_feature_flags.csv`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/04_robustness_analysis/stability_flags.csv`

### 3) Omori-style post-event decay is robust for M1 and M2, but not for M3

The baseline sequence comparison reports post-event Omori-like fits for:
- **M1**: p = 0.638, R² = 0.913
- **M2**: p = 0.643, R² = 0.957
- **M3**: no finite baseline Omori estimate reported

The robustness summaries show:
- **M1** post-Omori p is stable in 75.0% of windows
- **M2** post-Omori p is stable in 72.33% of windows overall, and 96.44% in the feature-level stability summary
- **M3** has 0.0% stable post-Omori fraction and no usable baseline post-Omori estimate

Interpretation:
- M1 and M2 support a persistent aftershock-decay-like pattern.
- M3 does not yield a robust Omori-style decay across the tested definitions, suggesting stronger parameter sensitivity or a sequence shape not well captured by simple decay fitting.

Evidence:
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/04_robustness_analysis/stability_feature_flags.csv`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/04_robustness_analysis/sensitivity_summary.csv`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/04_robustness_analysis/stability_flags.csv`

### 4) M2 is the most depth-distinct sequence

The baseline depth median differs strongly by mainshock:
- **M1**: depth_q50 = 11.51 km
- **M2**: depth_q50 = 41.555 km
- **M3**: depth_q50 = 12.83 km

This confirms the earlier guidance that M2 is depth-distinct. It also means depth stratification is especially important for M2 when comparing sequence behavior across parameter choices.

Evidence:
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/04_robustness_analysis/three_sequence_comparison_baseline.csv`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/04_robustness_analysis/robustness_results.csv`

### 5) M3 is the most parameter-sensitive in Omori behavior, but not in rate-ratio direction

The sensitivity summary indicates:
- M3 retains stable rate-ratio sign across all parameter definitions
- but its post-Omori stability fraction is 0.0 in the parameter summary

So M3 consistently shows post-event enrichment, but the specific decay-form diagnostic is not robust.

Evidence:
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/04_robustness_analysis/sensitivity_summary.csv`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/04_robustness_analysis/stability_flags.csv`

### 6) The simple control comparison is weak but supports event-centric enrichment

The control baseline file reports:
- M1: control rate 0.00/day, relative control rate 0.0
- M2: control rate 0.00/day, relative control rate 0.0
- M3: control rate 0.75/day, relative control rate 0.0767

This indicates that the event-centered windows are much more active than the background control windows, especially for M1 and M2.

Caution: the control file indicates NaN control window bounds for all three rows, so the exact control-window definition should be checked before making stronger inference.

Evidence:
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/04_robustness_analysis/control_comparison_baseline.csv`

### 7) Radii, time windows, and depth strategies do not change the qualitative conclusions

The robustness summaries indicate:
- the sign of the rate-ratio response is stable for all three mainshocks across the full parameter grid
- moving-window rate maxima are also stable in sign for all three mainshocks
- the exact Omori-fit stability is the main point of divergence, with M3 least robust

This supports the interpretation that the main sequence conclusions are not driven by a single arbitrary choice of radius or threshold, although the quantitative decay fit is more sensitive.

Evidence:
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/04_robustness_analysis/parameter_grid_summary.csv`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/04_robustness_analysis/robustness_results.csv`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/04_robustness_analysis/sensitivity_summary.csv`

## Limitations and Assumptions

- No image or PDF files were present in this output directory, so there were no figure products to inspect for this specific task.
- The control comparison output contains NaN window bounds, so the exact control-window geometry is not fully documented in the output table.
- `mecha_overlap_count` and `stations_within_100km` are zero or NaN in the baseline comparison, indicating that focal-mechanism and station-context summaries were not informative in this task output and may reflect data coverage limitations rather than true absence.
- Some Omori fits are missing or unstable, especially for M3, so decay interpretation should remain qualitative unless a more tailored fitting strategy is applied.
- The `sparse_flag` is false for the displayed baseline and summary rows, but very small or highly thresholded subsets may still become sparse in specific combinations.
- The summary tables do not by themselves show the exact maps or time-series shapes; those must be checked in the earlier sequence-extraction and diagnostics tasks for spatial and temporal visual context.

## Report-Ready Summary

The robustness analysis shows that the core event-centered sequence signal is stable: all three matched Aomori mainshocks exhibit a robust post-event increase in seismicity rate and a robust peak in short-term moving-window rate across radii, time windows, depth strategies, and magnitude thresholds. M2 stands out as the strongest relative activation and the clearest depth-distinct sequence, while M1 also shows strong and reproducible post-event enrichment. M3 remains robust in the sign of its response but is less stable in Omori-style decay behavior, indicating greater sensitivity of decay metrics to definition choices. The most important reusable evidence files are `robustness_results.csv`, `sensitivity_summary.csv`, `stability_flags.csv`, `stability_feature_flags.csv`, `three_sequence_comparison_baseline.csv`, `parameter_grid_summary.csv`, and `control_comparison_baseline.csv` at `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/04_robustness_analysis/`.
</task_analysis>

<task_analysis>
Task: 05_three_sequence_comparison
Description: Compare M1, M2, and M3 using a common baseline and then across alternate definitions.
Analysis file: <CASE_ROOT>/run/02_1_sequence_response/exp_run/analysis/05_three_sequence_comparison.md
Output directory: <CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/05_three_sequence_comparison

## Scientific Purpose

This task compares the three matched mainshock-centered sequences in the Aomori regional catalog, labeled M1, M2, and M3, using a common baseline and then testing how the inferred sequence behavior changes under alternate spatial, temporal, depth, and magnitude definitions. The scientific objective is to determine which pre-/post-event seismicity features are robust across definitions and which are parameter-dependent, so the later integrated report can distinguish stable sequence signatures from artifacts of window choice or thresholding.

## Method and Implementation Evidence

The implementation verified that the necessary source fields were available for catalog sequence analysis, then used the rematched mainshocks as the event centers for all downstream comparison products. Evidence for this is in `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/05_three_sequence_comparison/field_verification.csv` and `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/05_three_sequence_comparison/mainshock_rematch.csv`.

The verified fields include time, latitude, longitude, depth, magnitude, and event identifiers for the catalog; the mainshock table contains matched relocated events with very small time and location shifts relative to the reference records. The rematching quality is high for all three earthquakes, with matched IDs and sub-kilometer horizontal shifts, supporting the use of the relocated catalog for sequence-centered analysis.

The task then computed a baseline comparison and a parameter-grid comparison across radius, time window, depth strategy, and magnitude threshold. These are summarized in:
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/05_three_sequence_comparison/sequence_metrics_summary.csv`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/05_three_sequence_comparison/parameter_grid_summary.csv`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/05_three_sequence_comparison/parameter_sensitivity_summary.csv`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/05_three_sequence_comparison/robustness_across_definitions.csv`

The comparison also includes a simple control/background test, documented in `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/05_three_sequence_comparison/control_comparison_summary.csv`, and a set of publication-style figures under `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/05_three_sequence_comparison/figures/`.

## Key Results and Evidence Files

### 1) Data verification and rematching are strong enough for sequence comparison
`field_verification.csv` shows that the required fields were present in all four source tables: catalog, main earthquake list, focal mechanisms, and stations. `mainshock_rematch.csv` shows that the three mainshocks were matched to relocated catalog events with negligible time offsets and very small spatial/depth differences. This supports using the relocated catalog as the event-centered reference frame.

Evidence:
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/05_three_sequence_comparison/field_verification.csv`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/05_three_sequence_comparison/mainshock_rematch.csv`

### 2) The three sequences differ strongly in baseline counts and post/pre amplification
The baseline comparison and sequence summary show clear differences among the three mainshocks:
- M3 has the largest pre-event count in the baseline comparison figure, while M2 has the smallest pre-event count.
- M1 has the highest post-event count.
- M2 has the largest post/pre rate ratio.
- M3 has the lowest post/pre rate ratio.

These relationships are visible in:
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/05_three_sequence_comparison/figures/02_baseline_comparison.png`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/05_three_sequence_comparison/figures/06_three_sequence_summary.png`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/05_three_sequence_comparison/sequence_metrics_summary.csv`

From `sequence_metrics_summary.csv`, the baseline values are:
- M1: pre-rate 6.122222, post-rate 36.922222, rate ratio 6.030853
- M2: pre-rate 0.900000, post-rate 25.333333, rate ratio 28.148148
- M3: pre-rate 11.850000, post-rate 46.350000, rate ratio 3.911392

This supports a strong post-event increase for all three, but with very different relative amplification.

### 3) Spatial context differs among the three sequences
The event-centered maps show the three mainshocks embedded in the same broad regional seismicity field, but centered on different spatial clusters:
- M1 and M3 are located in the southeastern cluster.
- M2 is centered farther northwest in a deeper/northern cluster.
- The surrounding seismicity is clustered rather than uniform, with multiple dense regional groupings.

Evidence:
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/05_three_sequence_comparison/figures/01_event_centered_maps.png`

The depth-versus-rate-ratio summary indicates that M2 is much deeper than M1 and M3, while also having the largest post/pre rate ratio. The plotted summary gives:
- M1 depth around 11 km with moderate rate ratio
- M2 depth around 42 km with the largest rate ratio
- M3 depth around 13 km with lower rate ratio than M1

Evidence:
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/05_three_sequence_comparison/figures/05_depth_vs_rate_ratio.png`

### 4) Burstiness and spatial extent separate the three sequences
The summary figure shows that:
- M3 is the most bursty and has the largest median radial distance.
- M1 has the highest post activity.
- M2 is generally the lowest in post activity and burstiness.
- Omori p is similar for M1 and M2, with M2 slightly higher.

Evidence:
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/05_three_sequence_comparison/figures/06_three_sequence_summary.png`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/05_three_sequence_comparison/sequence_metrics_summary.csv`

The summary table includes:
- M1: moving_rate_max 272.142857, burstiness_index 45.903614, post_omori_p 0.638195, radial_q50_km 19.362009
- M2: moving_rate_max 125.857143, burstiness_index 27.107692, post_omori_p 0.643380
- M3: moving_rate_max 110.571429, burstiness_index not fully visible in the excerpt but represented in the summary table, with the plotted figure indicating the highest burstiness and largest radial extent

### 5) Time-window and radius sensitivity is substantial, but some patterns are stable
The rate-ratio heatmap and rate heatmap show that parameter choice affects absolute values and the strength of the inferred sequence response:
- M1 shows the broadest and most continuous response across the radius/time grid.
- M2 is sparse and highly dependent on larger radii.
- M3 is strongest at short windows and weaker at longer windows.

Evidence:
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/05_three_sequence_comparison/figures/03_rate_ratio_heatmap.png`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/05_three_sequence_comparison/figures/04_rate_heatmap.png`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/05_three_sequence_comparison/parameter_grid_summary.csv`

The robustness summary quantifies this:
- For M1, rate_ratio has low dispersion and stable sign across windows.
- For M2, the median rate ratio is large and the spread is very wide, indicating high sensitivity.
- For M3, the values are intermediate but still variable.

Evidence:
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/05_three_sequence_comparison/robustness_across_definitions.csv`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/05_three_sequence_comparison/parameter_sensitivity_summary.csv`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/05_three_sequence_comparison/figures/08_rate_ratio_sensitivity.png`

From `parameter_sensitivity_summary.csv`, the reported median rate ratio and IQR indicate:
- M1 is the most stable, with a median rate ratio around 5.03 and modest IQR.
- M2 is the least stable, with a much larger median and very large IQR.
- M3 is intermediate.

### 6) Control comparison indicates the observed pre-event activity is not explained by the simple background window used here
The control comparison figure and table show the observed pre-rate relative to a background control window:
- M1 and M2 are essentially at zero relative to the control rate in the plotted comparison.
- M3 has a small nonzero relative control rate, still far below 1.

Evidence:
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/05_three_sequence_comparison/figures/07_control_comparison.png`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/05_three_sequence_comparison/control_comparison_summary.csv`

The table indicates:
- M1 relative_control_rate = 0.000000
- M2 relative_control_rate = 0.000000
- M3 relative_control_rate = 0.063291

This is consistent with the plot: the observed pre-rate is much lower than the chosen control/background window in all three cases, with M3 slightly higher than M1 and M2.

## Limitations and Assumptions

- The analysis depends on the relocated catalog and on the specific baseline/control definitions implemented in the task; some metrics are sensitive to radius and time-window selection, especially for M2 and M3.
- The source outputs are internally consistent, but some plotting descriptions require caution because the images do not always expose exact numeric labels clearly; the figures should be treated as qualitative-to-semiquantitative evidence unless corroborated by the CSV tables.
- Focal-mechanism and station availability were verified, but the sequence comparison outputs here do not show detailed mechanism summaries in the visible figure set. The summary table indicates limited overlap for some contexts, so mechanism-based interpretation should remain contextual rather than central.
- The control comparison uses a simple background window, not a fully randomized null model; it is useful as a first-order check but not a definitive statistical test.
- The output handoff notes that results were successful but truncated, so the analysis relies on the available CSV summaries and image review rather than a full raw log reproduction.
- Some parameter-grid fields in the visible excerpts are partially truncated in the shell output, so exact per-cell values should be taken from the CSV files directly if a later report needs them.

## Report-Ready Summary

The three mainshock-centered sequences in the Aomori catalog show a shared regional seismicity background but distinct event-centered behaviors. M1 and M3 are located in a southeastern clustered seismicity region, whereas M2 is deeper and centered in a different, more northern cluster. All three exhibit post-event seismicity increases, but the magnitude of amplification differs substantially: M2 has the largest post/pre rate ratio, M1 has the largest absolute post-event count, and M3 has the smallest post/pre ratio. M3 is the most bursty and spatially extensive, while M1 appears the most stable across parameter choices. M2 is the most sensitive to spatial and temporal definition, with strong dependence on larger radii and wide variability across the parameter grid. These conclusions are supported by the rematch and verification tables, the baseline and summary CSVs, and the figure set in `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/05_three_sequence_comparison/figures/`.
</task_analysis>

<task_analysis>
Task: 06_control_comparison
Description: Evaluate observed sequence behavior against simple background or randomized controls.
Analysis file: <CASE_ROOT>/run/02_1_sequence_response/exp_run/analysis/06_control_comparison.md
Output directory: <CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/06_control_comparison

## Scientific Purpose

This task evaluates whether the event-centered seismic sequence patterns around the three matched major earthquakes in the Aomori regional catalog can be explained by simple background behavior or randomized time controls. The goal is to distinguish genuine post-mainshock clustering from rate changes that might arise from catalog background variability, temporal aggregation, or chance timing.

The control analysis is scientifically important because the preceding sequence analyses indicated burst-like seismicity and strong mainshock-centered enrichment for some events, but those patterns need to be tested against null expectations. Here, the focus is on the robustness of observed post/pre rate behavior under background and randomized controls, with attention to M1, M2, and M3 individually.

## Method and Implementation Evidence

The task was implemented as a control-comparison workflow using the relocated catalog and the three matched mainshocks. Evidence from the run inventory indicates that the control analysis consumed the full sequence-analysis context, including the catalog, matched mainshock set, station inventory, and focal-mechanism availability.

Key implementation evidence:
- `[<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/06_control_comparison/input_inventory.json]`
- `[<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/06_control_comparison/manifest.json]`

The inventory confirms the task operated on:
- 25,646 catalog rows
- 3 mainshock rows and 3 matched rows
- 1,606,311 sequence rows
- 354 mechanism rows
- 371 station rows

The control design is captured in the summary tables:
- observed baseline sequence windows centered on each mainshock
- shifted background controls
- randomized controls for post-event rate comparisons

Primary machine-readable outputs used for interpretation:
- `[<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/06_control_comparison/control_summary.csv]`
- `[<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/06_control_comparison/control_background_comparison.csv]`
- `[<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/06_control_comparison/control_observed_rates.csv]`
- `[<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/06_control_comparison/control_randomized_rates.csv]`
- `[<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/06_control_comparison/control_observed_vs_randomized_summary.csv]`
- `[<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/06_control_comparison/control_significance_summary.csv]`

Two publication-style figures summarize the control test:
- `[<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/06_control_comparison/figures/control_rate_ratio_comparison.png]`
- `[<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/06_control_comparison/figures/observed_vs_randomized_post_rates.png]`

## Key Results and Evidence Files

### 1) Observed post/pre rate ratios exceed background controls for all three mainshocks

The strongest overall result is that observed post-event rates are higher than the background/shifted-control rates across M1, M2, and M3. In the observed-vs-background table, observed sequences show systematic post/pre amplification, while shifted background windows show much smaller or even sub-unity ratios in many cases.

Evidence:
- `[<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/06_control_comparison/control_background_comparison.csv]`
- `[<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/06_control_comparison/control_summary.csv]`
- Figure: `[<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/06_control_comparison/figures/control_rate_ratio_comparison.png]`

Concrete values from `control_summary.csv` at the baseline setting (radius 50 km, time window 90 d, magnitude threshold 1.2):
- M1: baseline pre-rate 5.78, post-rate 35.30, rate ratio 6.11
- M2: baseline pre-rate 0.49, post-rate 17.12, rate ratio 35.02
- M3: baseline pre-rate 8.51, post-rate 27.67, rate ratio 3.25

This shows that:
- M2 has the strongest relative post-event enhancement.
- M1 is also elevated but less extreme than M2.
- M3 has a clear increase, though with a smaller ratio than M2.

### 2) Randomized controls are consistently lower than observed post-event rates

The observed-vs-randomized tables show that randomized controls do not reproduce the observed post-event rate enhancement. Observed post-event rates are substantially above randomized medians for all three mainshocks and across multiple time-window lengths.

Evidence:
- `[<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/06_control_comparison/control_observed_vs_randomized_summary.csv]`
- `[<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/06_control_comparison/control_randomized_rates.csv]`
- Figure: `[<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/06_control_comparison/figures/observed_vs_randomized_post_rates.png]`

From `control_observed_vs_randomized_summary.csv`:
- M1 at 90 d: observed ratio median 6.11 vs randomized ratio median 0.29; observed post-rate median 35.30 vs randomized post-rate median 11.44
- M2 at 90 d: observed ratio median 35.02 vs randomized ratio median 0.50; observed post-rate median 17.12 vs randomized post-rate median 5.04
- M3 at 90 d: observed ratio median 3.25 vs randomized ratio median 0.70; observed post-rate median 27.67 vs randomized post-rate median 5.34

The figure interpretation is consistent:
- Observed post-event rates stay above randomized rates in every panel.
- The separation is largest for M2 and M3 at short windows.
- M1 shows the weakest but still persistent observed-vs-randomized contrast.

### 3) Short-window post-event clustering is strongest, especially for M2 and M3

The figure `observed_vs_randomized_post_rates.png` shows that observed post-event rates are highest for the shortest windows and decrease as the window length increases. This is the expected signature of short-lived aftershock clustering, and it is not reproduced by randomized controls.

Evidence:
- `[<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/06_control_comparison/figures/observed_vs_randomized_post_rates.png]`
- `[<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/06_control_comparison/control_observed_rates.csv]`

Qualitative figure reading:
- M3 has the strongest observed short-window rates.
- M1 is also strongly elevated.
- M2 is lower in absolute post-event rate than M1/M3 in this figure, but its observed-vs-randomized contrast remains strong and its rate ratio is extreme in the summary tables because the pre-event background is very low.

### 4) Control behavior is comparatively stable, suggesting the observed signal is not a null-artifact

The control rates themselves are relatively low and do not mimic the observed post-event spikes. The randomized median rate and ratio summaries remain much closer to background levels, while observed rates retain strong amplification.

Evidence:
- `[<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/06_control_comparison/control_randomized_rates.csv]`
- `[<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/06_control_comparison/control_significance_summary.csv]`

From `control_significance_summary.csv` at the baseline setting:
- M1: baseline observed rate 35.30, randomized post-rate median 6.87, randomized ratio median 0.48, observed minus randomized rate 43.35
- M2: baseline observed rate 17.12, randomized post-rate median 5.04, randomized ratio median 0.50, observed minus randomized rate 19.27
- M3: baseline observed rate 27.67, randomized post-rate median 5.34, randomized ratio median 0.70, observed minus randomized rate 38.62

These values support the conclusion that the observed post-event enhancement is not reproduced by the randomization null.

## Limitations and Assumptions

- The task provides strong control-comparison evidence, but the available outputs are summary tables and diagnostic figures rather than raw per-event residuals for every control draw. This limits deeper inference about uncertainty structure beyond the reported medians and summary metrics.
- The CSV files were not directly analyzable with the PDF tool; they were inspected through structured table reading. The evidence is still valid, but the workflow note should acknowledge the format mismatch.
- The randomized controls are summarized through medians/means and not fully detailed here; the exact randomization algorithm, number of replicates, and any seed settings are not fully visible in the inspected outputs.
- Control significance is reported in summary form, but the specific statistical test used for significance thresholds is not explicit in the visible tables.
- The task confirms that observed post-event clustering exceeds simple randomized/background expectations, but it does not by itself prove a unique physical triggering mechanism.
- Station and focal-mechanism context exists in the inventory, but this control task does not appear to exploit those datasets analytically beyond documenting availability.

## Report-Ready Summary

The control-comparison analysis demonstrates that the post-mainshock seismicity increases seen around M1, M2, and M3 are not explained by simple background windows or randomized timing controls. Across the baseline 50 km / 90 d / M≥1.2 setting, all three mainshocks show elevated post/pre ratios, with M2 exhibiting the strongest relative amplification, followed by M1 and then M3.

The most reportable conclusion is that the observed post-event clustering is robust against null comparisons:
- observed post-event rates are systematically above background/shifted controls,
- observed post-event rates are substantially above randomized medians,
- short-window post-event concentration is strongest and consistent with aftershock-like decay behavior,
- and these patterns persist across the three matched mainshocks.

Best evidence files for the integrated report:
- `[<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/06_control_comparison/control_summary.csv]`
- `[<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/06_control_comparison/control_observed_vs_randomized_summary.csv]`
- `[<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/06_control_comparison/control_significance_summary.csv]`
- `[<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/06_control_comparison/figures/control_rate_ratio_comparison.png]`
- `[<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/06_control_comparison/figures/observed_vs_randomized_post_rates.png]`
</task_analysis>

<task_analysis>
Task: 07_figure_generation
Description: Generate publication-quality sequence-analysis figures for all mainshocks and comparisons.
Analysis file: <CASE_ROOT>/run/02_1_sequence_response/exp_run/analysis/07_figure_generation.md
Output directory: <CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/07_figure_generation

## Scientific Purpose

This task generated publication-quality figure products for the event-centered sequence analysis of the three matched major earthquakes in the Aomori regional catalog (M1, M2, M3). The figures are intended to support comparison of pre-event and post-event seismicity evolution, and to test robustness with respect to spatial radius, temporal window, magnitude threshold, and depth-stratification choices.

The resulting figure set is report-relevant because it includes:
- event-centered spatial maps for each mainshock,
- cumulative and moving-window seismicity diagnostics,
- post-event decay diagnostics,
- radius/time sensitivity heatmaps,
- depth-stratified views,
- a three-sequence comparison summary,
- and a control-comparison summary.

## Method and Implementation Evidence

The outputs indicate that a standardized figure-generation workflow was completed successfully for all three mainshocks. The implementation produced:
- per-mainshock figure panels using the same overall visual language across M1, M2, and M3,
- baseline sequence tables and summary CSVs for reuse in later reporting,
- robustness and control summary tables,
- and a verification file confirming successful figure generation.

Evidence files supporting implementation:
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/07_figure_generation/figure_generation_verification.json`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/07_figure_generation/figure_data/baseline_sequence_table.csv`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/07_figure_generation/figure_data/sequence_metrics_summary.csv`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/07_figure_generation/figure_data/robustness_summary.csv`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/07_figure_generation/figure_data/control_summary.csv`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/07_figure_generation/figure_data/three_sequence_comparison.csv`

## Key Results and Evidence Files

### 1) M1 sequence is strongly aftershock-dominated and spatially expanded
The M1 figure set shows a sharp transition from sparse pre-event activity to dense post-event activity.

Supporting figures:
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/07_figure_generation/figures/M1_event_centered_map.png`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/07_figure_generation/figures/M1_cumulative_counts.png`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/07_figure_generation/figures/M1_moving_rate.png`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/07_figure_generation/figures/M1_post_decay.png`

Observed pattern:
- pre-event seismicity is comparatively sparse and localized,
- post-event seismicity is much denser and more spatially extensive,
- the moving-window rate shows a very large post-mainshock spike followed by rapid decay,
- the cumulative count curve shows a strong post-event increase,
- the post-decay diagnostic suggests an Omori-like decay is present only imperfectly.

### 2) M2 is the most depth-distinct case and shows a strong post-event burst
M2 is visually and diagnostically different from M1 and M3, especially in its depth behavior and extreme rate-ratio contrast.

Supporting figures:
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/07_figure_generation/figures/M2_event_centered_map.png`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/07_figure_generation/figures/M2_cumulative_counts.png`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/07_figure_generation/figures/M2_moving_rate.png`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/07_figure_generation/figures/M2_depth_stratified.png`

Observed pattern:
- pre-event counts are low and nearly flat,
- post-event counts surge strongly,
- the moving-window rate is bursty and much larger after the mainshock,
- depth-stratified diagnostics show a strong separation in the stratified subset, consistent with M2 being depth-distinct,
- the three-sequence comparison confirms M2 is a low-count but high-rate-ratio outlier.

### 3) M3 shows strong pre-event activity and the broadest radial spread
M3 differs from M1 and M2 by having relatively strong pre-event accumulation and broad spatial extent.

Supporting figures:
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/07_figure_generation/figures/M3_event_centered_map.png`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/07_figure_generation/figures/M3_cumulative_counts.png`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/07_figure_generation/figures/M3_moving_rate.png`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/07_figure_generation/figures/M3_radial_median_radius_time_heatmap.png`

Observed pattern:
- M3 has substantial pre-event cumulative activity,
- the mainshock is still followed by a large post-event surge,
- the moving rate shows a clear pre-event spike and then a strong post-event burst and decay,
- radial median distance increases with radius and generally with longer windows, indicating broad spatial support,
- the three-sequence comparison shows M3 has the highest pre-event activity and the highest burstiness index.

### 4) Radius/time sensitivity is robust across thresholds, but the specific pattern differs by sequence
The heatmaps are the main evidence that the sequence metrics were tested under multiple definitions.

Supporting figures:
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/07_figure_generation/figures/M1_count_radius_time_heatmap.png`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/07_figure_generation/figures/M1_rate_ratio_radius_time_heatmap.png`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/07_figure_generation/figures/M2_count_radius_time_heatmap.png`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/07_figure_generation/figures/M2_rate_ratio_radius_time_heatmap.png`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/07_figure_generation/figures/M3_count_radius_time_heatmap.png`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/07_figure_generation/figures/M3_rate_ratio_radius_time_heatmap.png`

Observed pattern:
- event counts increase with both radius and time-window length for all three mainshocks,
- M1 and M3 show especially strong sensitivity to window size and clear post/pre enhancement,
- M2 shows very strong rate-ratio contrast and high values at short windows,
- the overall heatmap structure is stable across magnitude-threshold panels, suggesting threshold robustness in the qualitative spatial-temporal patterns.

### 5) Control comparison supports non-random sequence behavior
The control summary indicates the observed sequence metrics differ substantially from control rates.

Supporting figure:
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/07_figure_generation/figures/control_comparison_summary.png`

Observed pattern:
- all three events show baseline sequence behavior far above control rates,
- the contrast is strongest for M2, but M1 and M3 also differ clearly from controls.

### 6) The three earthquakes form a clear hierarchy in activity style
The summary comparison figure captures the main sequence-level contrasts.

Supporting figure and table:
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/07_figure_generation/figures/three_sequence_comparison_summary.png`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/07_figure_generation/figure_data/three_sequence_comparison.csv`

Cross-sequence interpretation from the figure:
- **M1**: largest total and post counts, strongest post rate.
- **M2**: smallest count-based sequence but very high rate ratio and large depth value.
- **M3**: strongest pre-event activity, highest burstiness, and the broadest radial spread.

### 7) Spatial context across the three mainshocks is geographically segregated
The overview map shows the three mainshocks occupy distinct regional clusters.

Supporting figure:
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/07_figure_generation/figures/all_mainshocks_overview_map.png`

Observed pattern:
- M2 is the northwestern cluster,
- M3 is central-southern,
- M1 is southeastern,
- the mainshock locations form a southward/eastward progression and are not strongly overlapping in space.

## Limitations and Assumptions

- The figures show strong sequence behavior, but the current task output is figure-centric; deeper quantitative details should be taken from the CSV summaries rather than inferred solely from the plots.
- The event-centered maps shown here do not include station symbols, focal mechanisms, coastlines, or basemaps in the plotted panels that were inspected, so station and mechanism context is not directly visible in the figures.
- The handoff notes indicate that outputs were truncated, so some machine-readable details may not be fully represented in the visible metadata here.
- Some diagnostics, especially Omori-style decay, appear only moderately consistent visually; the exact fit quality should be verified in the underlying summary tables before quoting parameter values in a formal report.
- The depth-stratified interpretation is clearest for M2; for M1 and M3 the visible depth separation is weak or minimal, so depth effects should be described cautiously.
- The control figure is summarized qualitatively from the plotted comparison; the exact control-generation method and statistical framing should be taken from the control summary table and earlier task outputs.
- No PDF evidence files were present in the inspected output set; only images, CSVs, JSON, and Markdown artifacts were produced here.

## Report-Ready Summary

The figure-generation task successfully produced a complete, publication-style diagnostic set for event-centered analysis of M1, M2, and M3. The figures consistently show that all three earthquakes are associated with elevated post-event seismicity, but the sequence styles differ: M1 is strongly aftershock-dominated and spatially expanded, M2 is the most depth-distinct and shows a sharp high-ratio burst, and M3 has the strongest pre-event activity and broadest radial spread. The radius/time heatmaps demonstrate that the main qualitative patterns are robust across spatial and temporal definitions and are broadly stable across magnitude thresholds. Control comparisons indicate that the observed sequences are substantially different from background-like controls. Together, the outputs provide a solid visual and tabular basis for the later integrated report.

Key reusable evidence:
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/07_figure_generation/figure_data/three_sequence_comparison.csv`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/07_figure_generation/figure_data/robustness_summary.csv`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/07_figure_generation/figure_data/control_summary.csv`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/07_figure_generation/figures/three_sequence_comparison_summary.png`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/07_figure_generation/figures/control_comparison_summary.png`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/07_figure_generation/figures/all_mainshocks_overview_map.png`
</task_analysis>

<task_analysis>
Task: 08_reusable_outputs
Description: Export validated tables and figure-ready datasets for downstream reuse.
Analysis file: <CASE_ROOT>/run/02_1_sequence_response/exp_run/analysis/08_reusable_outputs.md
Output directory: <CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/08_reusable_outputs

## Scientific Purpose

This task produced reusable, validated outputs for event-centered sequence analysis around the three matched major earthquakes in the Aomori regional catalog (M1, M2, M3). The main purpose was to export downstream-ready tables and figure-ready datasets supporting comparisons of pre- and post-event seismicity across radius, time window, depth strategy, and magnitude threshold definitions, together with basic control comparisons and mechanism/station context.

## Method and Implementation Evidence

The reusable-output workflow consolidated the earlier event-centered analysis into machine-readable summary products. Evidence from the validation and manifest files shows that the pipeline ingested the relocated regional catalog, the three matched mainshocks, the focal-mechanism table, and station metadata, then exported sequence-level and summary-level tables for robust comparison.

Key implementation evidence:
- Input inventory and validation:
  - `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/08_reusable_outputs/validation_summary.csv`
  - `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/08_reusable_outputs/dataset_manifest.csv`
- Reusable output registry:
  - `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/08_reusable_outputs/reusable_outputs_manifest.json`
  - `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/08_reusable_outputs/reusable_outputs_verification.json`

The exported tables indicate that the analysis preserved:
- sequence-level event attributes (`event_centered_sequence_table_master.csv`, `baseline_sequence_table.csv`)
- parameter-grid extraction counts (`sequence_extraction_counts_master.csv`, `parameter_grid_table.csv`, `parameter_grid_summary_master.csv`)
- diagnostic metrics including rates, Omori-style fits, and spatial summaries (`sequence_diagnostics_metrics_master.csv`)
- robustness/stability outputs (`robustness_results_master.csv`, `robustness_summary_master.csv`, `stability_table.csv`, `stability_flags_master.csv`)
- three-sequence comparison outputs (`three_sequence_comparison_master.csv`, `three_sequence_comparison_baseline_master.csv`)
- control/background comparison outputs (`control_table.csv`, `control_summary_master.csv`, `control_observed_rates_master.csv`, `control_randomized_rates_master.csv`)
- depth, magnitude, radial-distance, and mechanism summaries (`depth_distribution_summary_master.csv`, `magnitude_distribution_summary_master.csv`, `radial_distance_summary_master.csv`, `mechanism_summary_table.csv`, `mechanism_overlap_summary_master.csv`)

The figure manifest confirms that 30 figure-ready PNG files were registered for downstream use:
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/08_reusable_outputs/figure_manifest.csv`

## Key Results and Evidence Files

### 1) Validation confirms a complete reusable export set
The validation summary reports:
- catalog rows: 25,646
- mainshock rows: 3
- mechanism rows: 354
- station rows: 371
- matched mainshocks: 3
- sequence rows: 1,606,311
- summary rows: 900
- control rows: 3
- figure files: 30

Evidence:
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/08_reusable_outputs/reusable_outputs_verification.json`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/08_reusable_outputs/validation_summary.csv`

### 2) Sequence-level extraction was extensive and parameterized
The extraction table contains 900 parameter combinations spanning:
- mainshock: M1, M2, M3
- radius: 30, 44, 50, 80, 100 km
- time windows: 7, 30, 60, 90 days
- depth strategies: all, mainshock-centered, depth-stratified
- magnitude thresholds: all events, M≥1.2, M≥1.5, M≥2.0, M≥2.5

Evidence:
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/08_reusable_outputs/sequence_extraction_counts_master.csv`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/08_reusable_outputs/event_centered_sequence_table_master.csv`

A visible excerpt shows the expected event counts and pre/post splits for the baseline 30 km, 7-day window, all-depth case; for example, M1 has 1,931 events in that window with 506 pre-event and 1,424 post-event events.

### 3) Core sequence diagnostics capture rate changes, decay, and geometry
The diagnostics table includes:
- total counts and pre/post counts
- pre/post rates and rate ratios
- moving-window rate maxima and medians
- Omori-style post-event fit parameters and fit quality
- radial, depth, and magnitude quantiles
- mechanism availability indicators

Evidence:
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/08_reusable_outputs/sequence_diagnostics_metrics_master.csv`

Representative baseline comparison values from the exported three-sequence comparison table:
- M1: n_total 3,875; pre_rate 6.12/day; post_rate 36.92/day; rate_ratio 6.03; post_omori_p 0.638; radial_q50 19.36 km; depth_q50 11.51 km
- M2: n_total 2,362; pre_rate 0.90/day; post_rate 25.33/day; rate_ratio 28.15; post_omori_p 0.643; radial_q50 25.21 km; depth_q50 41.56 km
- M3: n_total 3,662; pre_rate 9.78/day; post_rate 30.90/day; rate_ratio 3.16; radial_q50 26.58 km; depth_q50 12.83 km

Evidence:
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/08_reusable_outputs/three_sequence_comparison_master.csv`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/08_reusable_outputs/three_sequence_comparison_baseline_master.csv`

### 4) Robustness and stability outputs were exported for sensitivity testing
The robustness outputs provide summary statistics over the parameter grid, including stable sign fractions and variability measures for rate ratio, moving-rate maxima, and Omori p-values. The excerpted summary indicates:
- rate_ratio stability fraction = 1.0 for M1, M2, M3
- moving_rate_max stability fraction = 1.0 for M1, M2, M3
- post_omori_p stability fraction = 1.0 for M1 and M2 in the summarized windows

Evidence:
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/08_reusable_outputs/robustness_results_master.csv`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/08_reusable_outputs/robustness_summary_master.csv`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/08_reusable_outputs/stability_table.csv`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/08_reusable_outputs/stability_flags_master.csv`

### 5) Control comparisons were generated to contextualize observed sequence changes
The control outputs compare observed post-event rates to background and randomized timing controls. The control summary shows:
- M1 baseline rate ratio 6.11, randomized post-rate median 6.87, observed-minus-randomized rate 43.35
- M2 baseline rate ratio 35.02, randomized post-rate median 5.04, observed-minus-randomized rate 19.27
- M3 baseline rate ratio 3.25, randomized post-rate median 5.34, observed-minus-randomized rate 38.62

Evidence:
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/08_reusable_outputs/control_summary_master.csv`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/08_reusable_outputs/control_observed_rates_master.csv`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/08_reusable_outputs/control_randomized_rates_master.csv`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/08_reusable_outputs/control_background_comparison_master.csv`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/08_reusable_outputs/control_observed_vs_randomized_summary_master.csv`

### 6) Mechanism availability is uneven but retained as contextual metadata
Mechanism overlap counts differ strongly by sequence:
- M1: 6
- M2: 191
- M3: 26

Evidence:
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/08_reusable_outputs/mechanism_summary_table.csv`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/08_reusable_outputs/mechanism_overlap_summary_master.csv`

### 7) Publication-quality figure-ready assets were exported
The figure manifest lists 30 reusable figures, including:
- event-centered maps
- cumulative counts
- moving-rate curves
- post-event decay plots
- time-distance plots
- radius/time sensitivity heatmaps
- depth-stratified plots
- three-sequence comparison summary
- control comparison summary

Evidence:
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/08_reusable_outputs/figure_manifest.csv`

Cross-check of representative figures from the figure-generation stage confirms the content and layout of the reusable figure set:
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/07_figure_generation/figures/all_mainshocks_overview_map.png`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/07_figure_generation/figures/control_comparison_summary.png`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/07_figure_generation/figures/three_sequence_comparison_summary.png`

These figures visually support:
- spatial clustering and timing relative to the three mainshocks
- baseline differences among M1, M2, and M3
- rate-ratio and control contrasts in a compact comparison layout

## Limitations and Assumptions

- The task output directory is focused on reusable tables and figure-ready datasets; it does not itself provide the full narrative analysis, so scientific interpretation must rely on the downstream tables and figures listed above.
- The task handoff explicitly notes that outputs were truncated; therefore, not every generated file can be summarized numerically here without additional table-by-table inspection.
- Focal-mechanism coverage is uneven. The mechanism summaries show that M2 has far more mechanism overlap than M1 and M3, so mechanism-based comparisons are context-limited and should be treated cautiously.
- Some summary columns contain missing values or incomplete fits for certain sequences or parameter sets; for example, M3 lacks an Omori-style fit in the baseline comparison table, indicating that post-event decay diagnostics were not uniformly feasible.
- Station coverage is available as metadata, but station-based sequence diagnostics are not the dominant exported product in this task.
- The figure manifest confirms 30 reusable PNG files, but this task does not include direct image re-analysis of all 30 plots; the descriptions above rely on the manifest and representative figure checks from the preceding figure-generation task.
- The exported robustness tables indicate strong stability for some metrics, but exact thresholds and stability criteria should be read directly from the robustness/stability tables before final interpretation.

## Report-Ready Summary

This task successfully packaged the event-centered earthquake-sequence analysis into reusable outputs for later reporting and synthesis. The exported files provide a complete downstream evidence set: validated catalog/mainshock/mechanism/station inventories, 1.6 million sequence rows across a 900-condition parameter grid, diagnostic metrics for pre/post rates and Omori-style decay, robustness and stability summaries, baseline and control comparisons, and 30 figure-ready graphics.

The most report-relevant reusable evidence files are:
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/08_reusable_outputs/validation_summary.csv`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/08_reusable_outputs/sequence_extraction_counts_master.csv`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/08_reusable_outputs/sequence_diagnostics_metrics_master.csv`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/08_reusable_outputs/robustness_summary_master.csv`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/08_reusable_outputs/three_sequence_comparison_master.csv`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/08_reusable_outputs/control_summary_master.csv`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/08_reusable_outputs/figure_manifest.csv`

Together, these outputs support later integrated reporting on which event-centered seismicity patterns are stable across parameter choices, where the three mainshocks differ most strongly, and how observed sequence evolution compares against simple background/randomized controls.
</task_analysis>


## Evaluation Quality Summary
Use this evaluation metadata to disclose delivery status, scientific confidence, and important limitations in the final report.
<evaluation_quality>
{
  "delivery_status": "complete",
  "is_satisfactory": true,
  "limitations": [
    {
      "evidence": "Several task handoffs note truncated outputs, so not every table/figure could be exhaustively cross-checked from the summaries alone.",
      "impact": "Reduces ability to audit every parameter combination, but does not undermine the core findings.",
      "severity": "minor",
      "type": "missing_outputs"
    },
    {
      "evidence": "Some figures and exact numeric labels were only described in summaries rather than directly inspected in detail.",
      "impact": "Limits full visual verification of publication-quality presentation.",
      "severity": "minor",
      "type": "output_quality"
    },
    {
      "evidence": "Omori-style decay fitting was only feasible for some sequences/parameter settings and appears less robust for M3.",
      "impact": "Decay interpretation should be treated as conditional, especially for M3.",
      "severity": "minor",
      "type": "method_assumption"
    },
    {
      "evidence": "Focal-mechanism and station-context coverage were uneven, with sparse local mechanism availability around some sequences.",
      "impact": "Mechanism-based interpretation is contextual rather than central.",
      "severity": "minor",
      "type": "data_coverage"
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
