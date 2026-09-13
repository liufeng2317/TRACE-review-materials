<science_report_context_compact>

## Context Map
Use this packet in order: objective -> actual methods -> core claims -> evidence index -> limitations/evaluation. Use context references and analysis files only when details are insufficient.

## Scientific Objective
<user_request>
You are a senior seismologist and earthquake-catalog analyst.
Compute spatial b-value diagnostics for the Ridgecrest Mw 6.4-Mw 7.1 interevent period, and compare the future Mw 7.1 hypocentral region with the Mw 6.4 control region.

# Scientific question
Does the interevent catalog show a spatial b-value pattern near the future Mw 7.1 hypocentral/rupture region that is consistent with the Q0/Q1 local b-value results?
Report the pattern, uncertainty and reliability without assuming a predefined anomaly or precursor.

# Data sources
- Interevent catalog: `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/TRACE_ridgecrest_relocated.csv`
  - columns: `event_time,latitude,longitude,depth_km,magnitude`
- Background catalog for regional context only: `<REPO_ROOT>/examples/ridgecrest/data/catalog_longterm/catalog_2year_background_before_64.csv`
- Main shocks: `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/main_shock_events.csv`

# Time windows and markers
- Read Mw 6.4 and Mw 7.1 origin times from the main-shock file.
- Fixed separator event: M5.37 at `2019-07-05T11:07:52.830000Z`.
- Exclude Mw 6.4, Mw 7.1 and the M5.37 separator event from all b-value estimates.
- Analyze:
  1. `full_interevent`: Mw 6.4 to Mw 7.1.
  2. `pre_separator`: Mw 6.4 to M5.37.
  3. `post_separator`: M5.37 to Mw 7.1.
- Use the background catalog only to report a larger-area regional reference b-value.

# Spatial method
Use fixed-radius spatial sampling rather than adaptive rectangular kernels.
- Project events and mainshocks to a local metric coordinate system.
- Build a regular grid over the active interevent region with 0.5-1.0 km spacing.
- At each grid node, use events within a circular horizontal radius.
- Primary radius: 5 km.
- Sensitivity radii: 4, 5, 6 and 7 km.
- Do not use radii larger than 7 km in the main analysis.
- For each node, compute b only if at least 30 events remain above Mc; otherwise report NaN.
- Reliability labels by `n >= Mc`: 30-49 exploratory, 50-99 moderately uncertain, >=100 robust.

# b-value estimation
- Primary maps use fixed `Mc = 1.5` for all spatial nodes and interevent windows.
- Also compute one window-level dynamic Mc for each time window as QC.
- Do not estimate Mc separately at each grid node for the main maps.
- Use the Aki-Utsu maximum-likelihood estimator with magnitude-bin correction:
  `b = log10(e) / (mean(M) - Mc + delta_M / 2)`.
- Infer `delta_M` from magnitude precision.
- Estimate bootstrap uncertainty for valid nodes when feasible, using at least 500 samples.

# Required diagnostics
1. 5 km fixed-Mc map-view b-value maps for `full_interevent`, `pre_separator` and `post_separator`.
   - Use a common color scale.
   - Overlay Mw 6.4, M5.37, Mw 7.1 and 5 km Mw 6.4/Mw 7.1 core circles.
   - Mask no-data nodes.
2. Reliability maps for `n >= Mc`, uncertainty and reliability class.
3. `post_separator - pre_separator` difference map where both windows have valid values.
4. Mw 7.1 fault-oriented cross-section or along-strike b-value profile for the post-separator window.
5. 5 km Mw 6.4 and Mw 7.1 core b-values and FMD plots for full, pre- and post-separator windows.
6. Descriptive low-b summary using `b < 0.9` and/or the lowest 20% of valid grid nodes within each window.

# Required outputs
Generate CSV tables for cleaned window catalogs, grid-node b-values, uncertainty, `n >= Mc`, reliability, core FMD summaries, difference-map source data, low-b summaries and validation checks.

Generate figures for spatial b-value maps, reliability maps, the difference map, the Mw 7.1 fault-oriented profile, core FMD comparison and radius sensitivity.

# Interpretation rules
- Use Q2 as spatial support for Q0/Q1, not as an independent precursor claim.
- Treat sparse pre-separator maps as exploratory.
- Interpret low b-values only as consistent with localized stress loading or relatively higher differential stress.
- Do not claim deterministic prediction.

# Computational requirements
- Save scripts, tables, figures and metadata.
- Use parallel computation up to 64 cores where useful.
- Show progress logs for long bootstrap computations.
- Use `seismostats` where appropriate.
</user_request>

## Planning Snapshot
Use this only as intent context; prefer actual methods, claims, and evidence below for report content.
plan_summary: Goal Compute spatial b-value diagnostics for the Ridgecrest Mw 6.4–Mw 7.1 interevent period using fixed-radius circular sampling, compare the future Mw 7.1 hypocentral/rupture region against the Mw 6.4 control region, and assess whether the spatial pattern is consistent with Q0/Q1 local b-value results while explicitly reporting uncertainty, data support, and robustness without making a precursor claim. Planning Assumptions Observation catalogs are sufficient; no model data are needed. Main-shock origin times and hypocentral markers must be read from `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/main_shock_events.csv`. The fixed separator event is defined by time `2019-07-05T11:07:52.830000Z`; Mw 6.4, Mw 7.1, and the separator event must be excluded from all b-value and Mc estimates, but retained as spatial/temporal markers. Main s
...[truncated]

## Context References
- full_audit_context: science_report_context.md

## Task Ledger
<task_record>
name: 01_spatial_bvalue_diagnostics
description: Execute the full Ridgecrest interevent spatial b-value analysis, figure generation, and scientific validation in one script.
ancestors: none
handoff_json: ../log/coding_progress/task_handoff/01_spatial_bvalue_diagnostics.json
analysis_file: ../analysis/01_spatial_bvalue_diagnostics.md
output_dir: ../outputs/01_spatial_bvalue_diagnostics
</task_record>


## Actual Method Summary
This section summarizes what was actually implemented and analyzed. Use it instead of repeating the full plan.
<method_record task="01_spatial_bvalue_diagnostics">
role: final_analysis
summary: The implementation used the relocated Ridgecrest interevent catalog and main-shock file, with the Mw 6.4, Mw 7.1, and the fixed separator event (M5.37 at 2019-07-05T11:07:52.830000Z) removed from all b-value estimates. Excluded events are documented in `[path]`. A local azimuthal equidistant projection was used for metric analysis, centered at lon -117.543577, lat 35.721467, and a 1 km regular grid with 3920 nodes was constructed over the active region. These implementation details are recorded in `[path]` and `[pa
...[truncated]
</method_record>
workflow_role: Execute the full Ridgecrest interevent spatial b-value analysis, figure generation, and scientific validation in one script.


## Core Scientific Claims
Use these claim-oriented summaries as the backbone of the final report. Each major claim should remain tied to the evidence index below.
<scientific_claim task="01_spatial_bvalue_diagnostics">
claim_role: final
This task successfully produced fixed-radius spatial b-value diagnostics for the Ridgecrest Mw 6.4–Mw 7.1 interevent period using fixed Mc = 1.5, 1 km grid spacing, radii 4–7 km, and bootstrap uncertainty estimation, with the primary interpretation based on the 5 km results. Implementation and validation are documented in `../outputs/01_spatial_bvalue_diagnostics/tables/analysis_metadata.json`, `../outputs/01_spatial_bvalue_diagnostics/tables/validation_report.json`, and `<REPO_ROOT>/examples/ridgecrest/catalog_analysis/r
...[truncated]
</scientific_claim>


## Evidence Index
Use these handoff summaries as the primary artifact index. Read full handoff files only when this compact evidence is insufficient.
<task_evidence task="01_spatial_bvalue_diagnostics">
status: success
stage: analysis_done
quality_flags: task_status:success, outputs_truncated
handoff_json: ../log/coding_progress/task_handoff/01_spatial_bvalue_diagnostics.json
analysis_file: ../analysis/01_spatial_bvalue_diagnostics.md
output_dir: ../outputs/01_spatial_bvalue_diagnostics
result_summary: Execute the full Ridgecrest interevent spatial b-value analysis, figure generation, and scientific validation in one script. Status=success; outputs=69 discovered; primary=8.

primary_outputs:
- tables/analysis_metadata.json: ../outputs/01_spatial_bvalue_diagnostics/tables/analysis_metadata.json
- figures/figure_core_fmd_comparison.png: ../outputs/01_spatial_bvalue_diagnostics/figures/figure_core_fmd_comparison.png
- figures/figure_radius_sensitivity.png: ../outputs/01_spatial_bvalue_diagnostics/figures/figure_radius_sensitivity.png
- figures/map_bvalue_difference_post_minus_pre_r5.png: ../outputs/01_spatial_bvalue_diagnostics/figures/map_bvalue_difference_post_minus_pre_r5.png
- figures/map_bvalue_full_interevent_r5.png: ../outputs/01_spatial_bvalue_diagnostics/figures/map_bvalue_full_interevent_r5.png
- figures/map_bvalue_full_interevent_r5_geo.png: ../outputs/01_spatial_bvalue_diagnostics/figures/map_bvalue_full_interevent_r5_geo.png
- figures/map_bvalue_post_separator_r5.png: ../outputs/01_spatial_bvalue_diagnostics/figures/map_bvalue_post_separator_r5.png
- figures/map_bvalue_post_separator_r5_geo.png: ../outputs/01_spatial_bvalue_diagnostics/figures/map_bvalue_post_separator_r5_geo.png
</task_evidence>


## Analysis Source Index
Read these task analysis files only when the method summary, claims, limitations, and evidence index are insufficient.
- 01_spatial_bvalue_diagnostics: analysis=../analysis/01_spatial_bvalue_diagnostics.md; output_dir=../outputs/01_spatial_bvalue_diagnostics

## Cross-Task Limitations and Assumptions
Use these limitations to qualify scientific claims in the final report.
<task_limitations task="01_spatial_bvalue_diagnostics">
- The primary maps use fixed Mc = 1.5 by design. Dynamic Mc was computed only for QC and differs among windows, especially for the post-separator and background catalogs. This means the main spatial maps prioritize consistency over local completeness adaptation. Evidence: `../outputs/01_spatial_bvalue_diagnostics/tables/window_level_mc_qc.csv`.

- Pre-separator support near the future Mw 7.1 core is limited. The core has only 49 events above Mc and is classified as exploratory. Its bootstrap uncertainty is larger than for the other core estimates, and map co
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
      "evidence": "Pre-separator Mw 7.1 core has n>=Mc = 49 and is explicitly labeled exploratory in core_bvalues_fmd_summary.csv and the task analysis.",
      "impact": "Limits confidence in any pre-separator spatial low-b inference near the future Mw 7.1 region.",
      "severity": "moderate",
      "type": "sample_size"
    },
    {
      "evidence": "Difference-map coverage is limited to 334 common valid nodes versus 396 pre and 361 post valid nodes, as reported in difference_map_coverage_summary.csv.",
      "impact": "Reduces certainty in spatial change interpretation because some locations cannot be compared directly between windows.",
      "severity": "moderate",
      "type": "data_coverage"
    },
    {
      "evidence": "Primary maps use fixed Mc = 1.5 by design, while dynamic Mc QC varies across windows, especially in the post-separator interval, according to window_level_mc_qc.csv.",
      "impact": "Supports comparability across space and time but means conclusions rely on a fixed-threshold assumption rather than local completeness adaptation.",
      "severity": "low",
      "type": "method_assumption"
    },
    {
      "evidence": "Full-window core contrast is modest and confidence intervals overlap, as summarized in core_bvalues_fmd_summary.csv and core_vs_control_comparison.csv.",
      "impact": "The strongest support for the future Mw 7.1 low-b pattern comes from the post-separator window, while the full-window contrast alone is not decisive.",
      "severity": "low",
      "type": "uncertainty"
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
