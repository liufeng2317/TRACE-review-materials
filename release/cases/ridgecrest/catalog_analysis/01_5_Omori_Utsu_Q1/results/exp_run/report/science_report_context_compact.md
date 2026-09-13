<science_report_context_compact>

## Context Map
Use this packet in order: objective -> actual methods -> core claims -> evidence index -> limitations/evaluation. Use context references and analysis files only when details are insufficient.

## Scientific Objective
<user_request>
You are a senior seismologist and earthquake-catalog analyst.
Your primary objective is to perform an Omori-Utsu comparison for the Ridgecrest interevent period, using the Mw 7.1 fault-zone entire area and its northern/southern subdivisions.
The main scientific question is whether the northern part of the Mw 7.1 fault-zone shows systematically smaller p-values than the southern part later in the interevent period.

## 1. Data Sources
- Catalog Path: `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/TRACE_ridgecrest_relocated.csv`
    - the first row is the name of the columns: `event_time,latitude,longitude,depth_km,magnitude`
- Main-shock events Path: `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/main_shock_events.csv`
    - Mainshock64: magnitude 6.4
    - Mainshock71: magnitude 7.1
- Primary magnitude threshold:
    - Use `M >= 3.0` as the primary threshold for the main analysis.
    - You may report lower-threshold or `Mc`-based results only as optional secondary sensitivity tests after the primary `M >= 3.0` analysis is complete.

## 2. Primary analysis domains
- Time Window: `(mainshock64, mainshock71)`
- Use a fixed Mw 7.1 fault-zone corridor as the primary Omori-Utsu analysis zone.
- Define the Mw7.1-fault-zone entire area with these fixed geometric parameters:
    - axial strike: 138.0 degrees
    - centerline start in lon/lat: longitude = -117.735813, latitude = 35.897499
    - centerline end in lon/lat: longitude = -117.362520, latitude = 35.559488
    - total corridor width: 6.0 km, i.e., 3.0 km half-width on each side of the centerline
- Inside this entire area, define:
    - Mw7.1-fault-zone northern area: events north of latitude = 35.72 degrees N
    - Mw7.1-fault-zone southern area: events south of latitude = 35.72 degrees N
- Use these three domains as the primary comparison:
    - Entire area
    - Northern area
    - Southern area
- Split-line sensitivity:
    - repeat the north/south partition for 35.70, 35.72 and 35.74 degrees N
    - treat 35.72 degrees N as the primary partition
    - use the neighboring split lines only as a robustness check, not as the main figure

## 3. Domain-definition diagnostics
- Project events and the corridor to a local metric coordinate system.
- Plot a domain-assignment figure that shows:
    - all interevent events colored by time since Mw 6.4
    - the Mw 7.1 fault-zone centerline and corridor boundary
    - the 35.72 degrees N split line
    - the events assigned to the northern area and southern area
    - the Mw 6.4 and Mw 7.1 mainshocks
- Save a compact CSV summary with domain counts for:
    - Entire area
    - Northern area
    - Southern area

## 4. Primary Omori-Utsu fitting design
1. Time reference:
   - Define `T = 0` as the origin time of the Mw 6.4 mainshock.
   - All interevent times are measured relative to this reference.

2. Periods to analyze:
   - Use cumulative periods that end at fixed times after Mw 6.4.
   - Use a fixed set of cumulative comparison periods with these specific endpoints:
       - 0.30 day
       - 0.50 day
       - 0.68 day
       - 0.732 day
       - 0.85 day
       - 1.00 day
       - 1.10 day
       - 1.22 day
       - 1.404 day
   - The periods 0.732 day and 1.404 day correspond to the M5.4 and Mw7.1 endpoints, respectively.

3. Rate model and fitting method:
   - For each domain and each cumulative period `[0, t_n]`, use only interevent events with `M >= 3.0` inside that domain and before `t_n`.
   - Fit a primary Omori rate model of the form:
       `lambda(t) = K * t^(-p)`
     using maximum likelihood estimation.
   - Use this pure power-law rate model as the primary fit for this task.
   - Do not make the three-parameter `K-c-p` Omori-Utsu model the primary result here; keep the primary result focused on the simpler power-law rate comparison described above.
   - If the first event time in a window is needed to avoid singular behavior at `t = 0`, handle that explicitly and document it.
   - Report fitting failures or unconstrained windows explicitly rather than forcing unstable estimates.

4. Uncertainty estimation:
   - Estimate uncertainty in `p` by bootstrap resampling.
   - Save bootstrap summaries including at least:
       - median `p`
       - 2.5 percentile
       - 97.5 percentile
   - Also report event counts used in each fit.
   - For the northern area, if `N <= 20`, mark that period as a low-count point for plotting with an open-circle symbol in the main figure.
   - If the southern area has too few events in the earliest periods and the fit does not converge, leave those points missing rather than fabricating values.

## 5. Required outputs
- Save a CSV table for all fitted periods and all three domains with at least:
    - domain label
    - period_days
    - event count
    - success/failure flag
    - fitted `p`
    - bootstrap median `p`
    - bootstrap lower/upper bounds
    - any low-count/open-circle flag

- Save a CSV or JSON metadata file with:
    - Mw 6.4 time
    - Mw 7.1 time
    - M5.4 separator period = 0.732 day
    - final period = 1.404 day
    - corridor geometry and split latitude

## 6. Required figures
### (A) Main two-panel figure
Create a two-panel figure with the required layout and styling described below.

Panel a:
- x-axis: `Period [day]`
- y-axis: `p value`
- plot the three primary domains together:
    - Entire area in grey
    - Northern area in blue
    - Southern area in red
- use filled circles with vertical uncertainty bars for ordinary points
- use open blue circles for northern-area points with `N <= 20`
- draw vertical lines at:
    - 0 day
    - 0.732 day
    - 1.404 day
- label the panel as `a`
- make this the primary figure of the workflow

Panel b:
- use the entire-area result for the final 1.404 day period
- plot observed seismicity rate `lambda [day^-1]` versus time since Mw 6.4 on log-log axes
- overlay the fitted power-la
...[truncated]
</user_request>

## Planning Snapshot
Use this only as intent context; prefer actual methods, claims, and evidence below for report content.
plan_summary: Goal Perform a primary Omori-Utsu comparison for the Ridgecrest interevent period between the Mw 6.4 and Mw 7.1 mainshocks, using the fixed Mw 7.1 fault-zone corridor and its northern/southern subdivisions, to test whether the northern subdivision shows systematically smaller fitted pure power-law p-values than the southern subdivision in later cumulative periods. Planning Assumptions Use only the provided observational catalog and mainshock metadata; no model data are needed. Primary analysis window is the open interval `(Mw 6.4 origin time, Mw 7.1 origin time)`. Primary magnitude threshold is fixed at `M >= 3.0`; any lower-threshold or Mc-based analysis is secondary and must be executed only after the primary workflow is complete. Primary spatial definition is fixed by the user: centerline start `(-117.735813, 35.897499)` centerline end `(-117.362520, 35.559488)` strike `138.0°` total
...[truncated]

## Context References
- full_audit_context: science_report_context.md

## Task Ledger
<task_record>
name: 01_domain_preparation
description: Build the Ridgecrest interevent event table, assign fixed corridor and north-south domains, and save domain diagnostics metadata.
ancestors: none
handoff_json: ../log/coding_progress/task_handoff/01_domain_preparation.json
analysis_file: ../analysis/01_domain_preparation.md
output_dir: ../outputs/01_domain_preparation
</task_record>

<task_record>
name: 02_omori_fitting_and_figures
description: Fit cumulative pure power-law Omori models with bootstrap uncertainty, create required figures, and save primary and split-sensitivity results.
ancestors: 01_domain_preparation
handoff_json: ../log/coding_progress/task_handoff/02_omori_fitting_and_figures.json
analysis_file: ../analysis/02_omori_fitting_and_figures.md
output_dir: ../outputs/02_omori_fitting_and_figures
</task_record>


## Actual Method Summary
This section summarizes what was actually implemented and analyzed. Use it instead of repeating the full plan.
<method_record task="01_domain_preparation">
role: supporting_analysis
summary: A local metric coordinate system was used to project interevent events and the prescribed Mw 7.1 centerline/corridor geometry, allowing event positions to be expressed in kilometers and tested against the fixed 6.0 km wide corridor. The corridor geometry stored in metadata matches the requested setup: strike 138.0°, centerline start at (-117.735813, 35.897499), centerline end at (-117.362520, 35.559488), total width 6.0 km, half-width 3.0 km, and derived centerline length 50.47 km. These details are preserved in `[
...[truncated]
</method_record>
workflow_role: Build the Ridgecrest interevent event table, assign fixed corridor and north-south domains, and save domain diagnostics metadata.

<method_record task="02_omori_fitting_and_figures">
role: final_analysis
summary: The task outputs show that the implemented model was the requested cumulative pure power-law Omori rate model, `lambda(t) = K * t^(-p)`, fit by maximum likelihood for each domain and each cumulative endpoint. The primary fit table records fitted `p`, `K`, log-likelihood, the effective time range used, and event counts for all 27 primary windows (3 domains × 9 periods), with all windows marked successful in this run: - `[path]` - `[path]` Bootstrap uncertainty estimation was also implemented as requested. Run metada
...[truncated]
</method_record>
workflow_role: Fit cumulative pure power-law Omori models with bootstrap uncertainty, create required figures, and save primary and split-sensitivity results.


## Core Scientific Claims
Use these claim-oriented summaries as the backbone of the final report. Each major claim should remain tied to the evidence index below.
<scientific_claim task="01_domain_preparation">
claim_role: supporting
Task 01 successfully prepared the fixed Ridgecrest interevent analysis domains required for the later Omori-Utsu comparison. Using the prescribed Mw 7.1 fault-zone corridor geometry and a local metric projection, it built an interevent event table for the period between the Mw 6.4 and Mw 7.1 mainshocks and assigned each event to the entire corridor and to north/south subdivisions for split latitudes 35.70°, 35.72°, and 35.74°. For the primary 35.72°N partition, the corridor contains 2,852 interevent events in total, divided into 1,402 northern and 1,450 southern events, with 109, 50, and 59 events respectively at the primary M ≥ 3.0 threshold. The saved integrity checks show that north plus south exactly equals the entire corridor and that no event lies exactly on the 35.72°N split, confirming a clean non-overlapping partition. The diagno
...[truncated]
</scientific_claim>

<scientific_claim task="02_omori_fitting_and_figures">
claim_role: final
This task completed the requested cumulative pure power-law Omori analysis for the Ridgecrest interevent period (`M >= 3.0`) within the fixed Mw 7.1 fault-zone corridor and its north/south subdivisions. The main figure, `../outputs/02_omori_fitting_and_figures/main_two_panel_omori_comparison.png`, shows that the entire corridor has a relatively stable sub-unity decay exponent (`p ≈ 0.7–0.8`) across cumulative periods, ending at `p = 0.739` with bootstrap median `0.748` and 95% interval `[0.641, 0.860]` at 1.404 day. The panel-b rate curve is consistent with a whole-corridor power-law decay over the interevent interval.

For the primary 35.72° split, the north and south are similar through the earlier c
...[truncated]
</scientific_claim>


## Evidence Index
Use these handoff summaries as the primary artifact index. Read full handoff files only when this compact evidence is insufficient.
<task_evidence task="01_domain_preparation">
status: success
stage: analysis_done
quality_flags: task_status:success
handoff_json: ../log/coding_progress/task_handoff/01_domain_preparation.json
analysis_file: ../analysis/01_domain_preparation.md
output_dir: ../outputs/01_domain_preparation
result_summary: Build the Ridgecrest interevent event table, assign fixed corridor and north-south domains, and save domain diagnostics metadata. Status=success; outputs=5 discovered; primary=5.

primary_outputs:
- domain_assignment_checks.csv: ../outputs/01_domain_preparation/domain_assignment_checks.csv
- domain_counts_primary.csv: ../outputs/01_domain_preparation/domain_counts_primary.csv
- domain_metadata.json: ../outputs/01_domain_preparation/domain_metadata.json
- interevent_domain_event_table.csv: ../outputs/01_domain_preparation/interevent_domain_event_table.csv
- domain_assignment_diagnostic.png: ../outputs/01_domain_preparation/domain_assignment_diagnostic.png
</task_evidence>

<task_evidence task="02_omori_fitting_and_figures">
status: success
stage: analysis_done
quality_flags: task_status:success
handoff_json: ../log/coding_progress/task_handoff/02_omori_fitting_and_figures.json
analysis_file: ../analysis/02_omori_fitting_and_figures.md
output_dir: ../outputs/02_omori_fitting_and_figures
result_summary: Fit cumulative pure power-law Omori models with bootstrap uncertainty, create required figures, and save primary and split-sensitivity results. Status=success; outputs=11 discovered; primary=8.

primary_outputs:
- bootstrap_summary.csv: ../outputs/02_omori_fitting_and_figures/bootstrap_summary.csv
- final_merged_primary_results.csv: ../outputs/02_omori_fitting_and_figures/final_merged_primary_results.csv
- fit_input_audit_table.csv: ../outputs/02_omori_fitting_and_figures/fit_input_audit_table.csv
- north_vs_south_primary_comparison_35p72.csv: ../outputs/02_omori_fitting_and_figures/north_vs_south_primary_comparison_35p72.csv
- panel_b_rate_curve_support.csv: ../outputs/02_omori_fitting_and_figures/panel_b_rate_curve_support.csv
- primary_fit_table.csv: ../outputs/02_omori_fitting_and_figures/primary_fit_table.csv
- run_metadata.json: ../outputs/02_omori_fitting_and_figures/run_metadata.json
- split_sensitivity_results.csv: ../outputs/02_omori_fitting_and_figures/split_sensitivity_results.csv
</task_evidence>


## Analysis Source Index
Read these task analysis files only when the method summary, claims, limitations, and evidence index are insufficient.
- 01_domain_preparation: analysis=../analysis/01_domain_preparation.md; output_dir=../outputs/01_domain_preparation
- 02_omori_fitting_and_figures: analysis=../analysis/02_omori_fitting_and_figures.md; output_dir=../outputs/02_omori_fitting_and_figures

## Cross-Task Limitations and Assumptions
Use these limitations to qualify scientific claims in the final report.
<task_limitations task="01_domain_preparation">
- This task is limited to domain preparation and diagnostics. It does **not** perform Omori-Utsu fitting, bootstrap uncertainty estimation, or any p-value comparison yet.
- Although the overall M ≥ 3.0 counts are adequate for the full interevent interval (109 entire, 50 north, 59 south), some early cumulative periods may still have low counts, especially in the subdivided domains. That later issue is not resolved here and must be handled during fitting.
- The diagnostic figure suggests events cluster densely near the 35.72°N boundary, so later split-line sensitivity using 35.70°N and 35.74°N remains scientifically relevant even though the primary partition is clean.
- The metadata stores a t
...[truncated]
</task_limitations>

<task_limitations task="02_omori_fitting_and_figures">
- The present task output set does not include the requested domain-assignment diagnostic figure; that diagnostic appears to belong to Task 01 domain preparation rather than this task’s output directory. Therefore, geometric event assignment and corridor membership for the Omori fits should be cross-referenced to Task 01 outputs rather than inferred solely from Task 02.
- The pure power-law model is the primary model here by design. No three-parameter `K-c-p` Omori-Utsu comparison is provided in this task, so early-time incompleteness or short-time singular behavior is handled operationally by starting each fit at the first observed event time (`t_min_used_days > 0`), not by estimating `c`.
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
      "evidence": "The north-vs-south primary comparison reports bootstrap interval overlap remaining true for all periods, including later windows where fitted p values diverge.",
      "impact": "The qualitative late-time north-lower-than-south tendency is supported, but statistical separation is not strong enough to claim a sharply resolved difference.",
      "severity": "moderate",
      "type": "uncertainty"
    },
    {
      "evidence": "The earliest northern window at 0.30 day has N=19 and is flagged as a low-count open-circle point.",
      "impact": "Very early north-domain behavior should not be over-interpreted and does not strongly constrain temporal onset of the north-south contrast.",
      "severity": "low",
      "type": "sample_size"
    },
    {
      "evidence": "The pure power-law model is fit with t_min set to the first observed event time to handle the t=0 singularity, rather than estimating a c parameter.",
      "impact": "Results are valid for the requested primary design, but early-time decay estimates may still reflect sensitivity to incompleteness or lower-bound choice.",
      "severity": "moderate",
      "type": "method_assumption"
    },
    {
      "evidence": "Split-sensitivity results show that the late northern p estimate changes appreciably across 35.70, 35.72, and 35.74 degree partitions, while the southern series is more stable.",
      "impact": "The sign of the later north-south contrast appears reasonably robust, but its magnitude depends on the exact north-south boundary and should be interpreted cautiously.",
      "severity": "moderate",
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
