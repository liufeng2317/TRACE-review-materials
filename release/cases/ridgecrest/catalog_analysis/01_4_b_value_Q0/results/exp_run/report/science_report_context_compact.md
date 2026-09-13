<science_report_context_compact>

## Context Map
Use this packet in order: objective -> actual methods -> core claims -> evidence index -> limitations/evaluation. Use context references and analysis files only when details are insufficient.

## Scientific Objective
<user_request>
You are a senior seismologist and earthquake-catalog analyst.
Your objective is to compute fixed-window b-value contrasts for the Ridgecrest sequence in a simple, reproducible and diagnostic way.

# Scientific question
How do b-values in the future Mw 7.1 hypocentral region compare with the Mw 6.4 hypocentral control region, the full interevent region and the long-term regional background?
Report the contrast direction, magnitude, uncertainty and reliability without assuming the Mw 7.1 region must be lower or higher.

# Data sources
- Interevent catalog: `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/TRACE_ridgecrest_relocated.csv`
  - columns: `event_time,latitude,longitude,depth_km,magnitude`
- Background catalog: `<REPO_ROOT>/examples/ridgecrest/data/catalog_longterm/catalog_2year_background_before_64.csv`
  - map columns: `datetime` -> `event_time`, `latR` -> `latitude`, `lonR` -> `longitude`, `depR` -> `depth_km`, `mag` -> `magnitude`
- Main shocks: `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/main_shock_events.csv`

# Time windows
- Background: use the background catalog only as one larger-area regional b-value reference. For the primary reported background reference, use fixed `Mc = 1.5` so it is directly comparable with the main interevent fixed-Mc results. Also report the catalog-derived Mc result as a QC/supporting value.
- Full interevent: Mw 6.4 origin time to Mw 7.1 origin time, excluding the two mainshocks.
- Early/late interevent: split the interevent period at the fixed separator event M5.37 at `2019-07-05T11:07:52.830000Z`. Use this event only as a boundary marker and exclude it from all b-value estimates.
- Do not perform sliding-window or time-varying b-value analysis.

# Spatial domains
- Background: one larger Ridgecrest regional domain only. Do not subdivide background into Mw 6.4/Mw 7.1 local cores.
- Interevent regional reference: full Ridgecrest interevent study region.
- Interevent Mw 6.4 control: cylindrical hypocentral core centered on Mw 6.4.
- Interevent Mw 7.1 target: cylindrical hypocentral core centered on Mw 7.1.
- Primary local radius: 5 km. Radius sensitivity: 4, 5, 6 and 7 km only.
- Project coordinates to a local metric CRS and use horizontal distance for the radius masks. Keep depth in output tables.
- The Mw 6.4 and Mw 7.1 hypocenters are about 12 km apart; the primary 5 km cores do not overlap. Report overlap counts for all sensitivity radii and use exclusive nearest-hypocenter assignment if any sensitivity radius overlaps.

# b-value method
For every requested subset, report total events, Mc, n >= Mc, b-value, bootstrap uncertainty, magnitude range and reliability.
- Estimate Mc by maximum curvature.
- Also compute conservative Mc per temporal window: `Mc_conservative = max(subset Mc, full-window Mc)`.
- For the main fixed-window comparison, compute fixed-Mc results with `Mc = 1.5` for both interevent subsets and the larger-area background reference. Treat fixed `Mc = 1.5` as the primary value for cross-window/domain comparison; report automatic/conservative Mc results as QC/supporting diagnostics.
- Use the Aki-Utsu maximum-likelihood estimator with magnitude-bin correction:
  `b = log10(e) / (mean(M) - Mc + delta_M / 2)`.
- Infer `delta_M` from magnitude precision.
- Use >=1000 bootstrap samples when feasible and report median, 16th-84th percentile and standard deviation.

# Reliability rules
Compute b-values whenever at least two events remain above Mc, but classify reliability by `n >= Mc`:
- `n >= 100`: robust for primary diagnostics.
- `50 <= n < 100`: usable but moderately uncertain.
- `30 <= n < 50`: exploratory; report the value, but discuss it only if bootstrap intervals and sensitivity tests are consistent.
- `n < 30`: highly unreliable; report only for completeness.
Treat these thresholds as reporting labels rather than sharp scientific boundaries, and interpret estimates near a threshold with extra caution.
Do not use highly unreliable subsets to support conclusions. Interpret any observed low b-value only as consistent with localized stress loading, not as a deterministic precursor.

# Required outputs
Generate CSV tables for:
- cleaned catalog summaries and separator event metadata,
- unified aggregate b-values by window, domain, radius and Mc mode,
- b-value contrasts: Mw7.1-Mw6.4, Mw7.1-full region and late-early within each core,
- radius sensitivity and overlap diagnostics.

Generate figures for:
1. Interevent map with Mw6.4/Mw7.1 hypocenters and 5 km cores; optionally show 4, 6 and 7 km sensitivity circles.
2. Magnitude-frequency distributions with catalog-derived Mc, fixed `Mc = 1.5`, and fitted Gutenberg-Richter lines.
3. Main fixed-window b-value comparison using fixed `Mc = 1.5`.
   - This must explicitly show the 5 km Mw6.4 and Mw7.1 core b-values for three windows: full interevent, pre-separator, and post-separator.
   - The separator is the M5.37 event at `2019-07-05T11:07:52.830000Z`; exclude this event from b-value estimates and use it only to divide pre/post windows.
   - Plot Mw6.4 and Mw7.1 cores side by side within each window, with bootstrap uncertainty intervals and `n >= Mc` labels.
   - Include the larger-area background reference as a separate horizontal line or separate panel, not mixed in a way that obscures the pre/post core comparison.
4. Contrast plot with uncertainty intervals.
5. Radius sensitivity for interevent local cores only.
6. Time-magnitude completeness diagnostic for the interevent catalog.
7. Overlap diagnostic for 4, 5, 6 and 7 km radii.

# Computational requirements
- Keep the workflow reproducible and save all scripts, tables, figures and metadata.
- Use parallel computation up to 64 cores where useful.
- Show progress logs for long bootstrap computations.
- Use `seismostats` where appropriate for Mc, b-value, a-value calculati
...[truncated]
</user_request>

## Planning Snapshot
Use this only as intent context; prefer actual methods, claims, and evidence below for report content.
plan_summary: Goal Compute fixed-window b-value contrasts for the Ridgecrest sequence in a reproducible, diagnostic workflow, comparing the future Mw 7.1 hypocentral core against the Mw 6.4 hypocentral control core, the full interevent region, and the long-term regional background, and report contrast direction, magnitude, uncertainty, overlap behavior, and reliability without assuming the Mw 7.1 core is lower or higher. Planning Assumptions Use only the provided observational catalogs and mainshock reference file; no model data are needed. One primary task script should perform the end-to-end scientific workflow because catalog harmonization, temporal/spatial subset definition, Mc estimation, b-value estimation, bootstrap uncertainty, contrasts, overlap handling, and figure generation are tightly coupled. SeismoStats package contract relevant here: maximum-curvature Mc estimation is available via `es
...[truncated]

## Context References
- full_audit_context: science_report_context.md

## Task Ledger
<task_record>
name: 01_ridgecrest_bvalue_contrast_analysis
description: Execute the complete Ridgecrest fixed-window b-value contrast workflow from catalog harmonization through diagnostics, figures, and validation.
ancestors: none
handoff_json: ../log/coding_progress/task_handoff/01_ridgecrest_bvalue_contrast_analysis.json
analysis_file: ../analysis/01_ridgecrest_bvalue_contrast_analysis.md
output_dir: ../outputs/01_ridgecrest_bvalue_contrast_analysis
</task_record>


## Actual Method Summary
This section summarizes what was actually implemented and analyzed. Use it instead of repeating the full plan.
<method_record task="01_ridgecrest_bvalue_contrast_analysis">
role: final_analysis
summary: The workflow successfully executed as a reproducible end-to-end analysis with preserved metadata, validation checks, tables, and diagnostic figures. The main script is `[path]`, and run metadata are in `[path]`. Implementation evidence shows: - A common local metric CRS was used for distance-based core selection: `+proj=aeqd +lat_0=35.74022 +lon_0=-117.54339 +datum=WGS84 +units=m +no_defs +type=crs`, documented in `[path]` and `[path]`. - The Mw 6.4 and Mw 7.1 hypocentral centers are separated by 11.998 km, matchin
...[truncated]
</method_record>
workflow_role: Execute the complete Ridgecrest fixed-window b-value contrast workflow from catalog harmonization through diagnostics, figures, and validation.


## Core Scientific Claims
Use these claim-oriented summaries as the backbone of the final report. Each major claim should remain tied to the evidence index below.
<scientific_claim task="01_ridgecrest_bvalue_contrast_analysis">
claim_role: final
This task produced a complete, reproducible fixed-window b-value contrast analysis for the Ridgecrest sequence, centered on the question of whether the future Mw 7.1 hypocentral core differs from the Mw 6.4 control core, the full interevent region, and the longer-term regional background. The workflow succeeded and delivered all requested figures and machine-readable tables, with run metadata and validation preserved in `../outputs/01_ridgecrest_bvalue_contrast_analysis/metadata/run_metadata.json` and `../outputs/01_ridgecrest_bvalue_contrast_analysis/tables/run_validatio
...[truncated]
</scientific_claim>


## Evidence Index
Use these handoff summaries as the primary artifact index. Read full handoff files only when this compact evidence is insufficient.
<task_evidence task="01_ridgecrest_bvalue_contrast_analysis">
status: success
stage: analysis_done
quality_flags: task_status:success
handoff_json: ../log/coding_progress/task_handoff/01_ridgecrest_bvalue_contrast_analysis.json
analysis_file: ../analysis/01_ridgecrest_bvalue_contrast_analysis.md
output_dir: ../outputs/01_ridgecrest_bvalue_contrast_analysis
result_summary: Execute the complete Ridgecrest fixed-window b-value contrast workflow from catalog harmonization through diagnostics, figures, and validation. Status=success; outputs=16 discovered; primary=8.

primary_outputs:
- metadata/run_metadata.json: ../outputs/01_ridgecrest_bvalue_contrast_analysis/metadata/run_metadata.json
- tables/bootstrap_run_metadata.csv: ../outputs/01_ridgecrest_bvalue_contrast_analysis/tables/bootstrap_run_metadata.csv
- tables/bvalue_aggregates_unified.csv: ../outputs/01_ridgecrest_bvalue_contrast_analysis/tables/bvalue_aggregates_unified.csv
- tables/bvalue_contrasts.csv: ../outputs/01_ridgecrest_bvalue_contrast_analysis/tables/bvalue_contrasts.csv
- tables/cleaned_catalog_summaries.csv: ../outputs/01_ridgecrest_bvalue_contrast_analysis/tables/cleaned_catalog_summaries.csv
- tables/radius_overlap_diagnostics.csv: ../outputs/01_ridgecrest_bvalue_contrast_analysis/tables/radius_overlap_diagnostics.csv
- tables/run_validation_summary.csv: ../outputs/01_ridgecrest_bvalue_contrast_analysis/tables/run_validation_summary.csv
- tables/separator_event_metadata.csv: ../outputs/01_ridgecrest_bvalue_contrast_analysis/tables/separator_event_metadata.csv
</task_evidence>


## Analysis Source Index
Read these task analysis files only when the method summary, claims, limitations, and evidence index are insufficient.
- 01_ridgecrest_bvalue_contrast_analysis: analysis=../analysis/01_ridgecrest_bvalue_contrast_analysis.md; output_dir=../outputs/01_ridgecrest_bvalue_contrast_analysis

## Cross-Task Limitations and Assumptions
Use these limitations to qualify scientific claims in the final report.
<task_limitations task="01_ridgecrest_bvalue_contrast_analysis">
- The most important limitation is **sample size in the early Mw 7.1 core**. At the primary 5 km radius it has only `n>=Mc = 49`, classified as **exploratory**; at 4 km it drops to 25 and becomes **highly unreliable**. Conclusions that rely on the early Mw 7.1 subset should therefore be framed cautiously and not overinterpreted. This affects both the early Mw 7.1 versus Mw 6.4 contrast and the Mw 7.1 late-minus-early temporal contrast.
- The **full-window Mw 7.1 minus Mw 6.4** contrast at 5 km is small (`-0.050`) and its 16–84% bootstrap interval includes zero (`-0.093 to +0.002`). The direction is negative, but this specific comparison is not cleanly separated from no contrast at the report
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
      "evidence": "The primary 5 km early Mw 7.1 core has n>=Mc = 49 and is labeled exploratory; the 4 km early Mw 7.1 subset has n = 25 and is highly unreliable.",
      "impact": "Early-window contrasts involving the Mw 7.1 core are directionally informative but should not be treated as strong evidence.",
      "severity": "medium",
      "type": "sample_size"
    },
    {
      "evidence": "The 5 km full-window Mw7.1-Mw6.4 contrast is -0.050 with a 16th-84th bootstrap interval of about -0.093 to +0.002.",
      "impact": "The overall full interevent contrast between the two local cores is weak and not cleanly separable from zero at the reported interval.",
      "severity": "medium",
      "type": "uncertainty"
    },
    {
      "evidence": "Background b-value differs substantially between fixed Mc=1.5 (~1.066) and auto Mc (~0.799, Mc~0.81).",
      "impact": "Background comparisons are valid for the requested fixed-Mc cross-domain benchmark, but the absolute background level is Mc-dependent and should be interpreted as a comparison convention rather than a unique value.",
      "severity": "low",
      "type": "method_assumption"
    },
    {
      "evidence": "Local subsets are defined using horizontal cylindrical cores only, as requested, rather than full 3-D hypocentral distance.",
      "impact": "Results characterize horizontal core-centered spatial contrasts and may not capture depth-structured localization.",
      "severity": "low",
      "type": "data_coverage"
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
