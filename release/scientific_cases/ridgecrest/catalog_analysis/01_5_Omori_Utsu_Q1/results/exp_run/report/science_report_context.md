<science_report_context>

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
- overlay the fitted power-law rate curve
- annotate the fitted `p` with uncertainty
- annotate the period `1.404 [day]`
- label the panel as `b`

### (B) Domain-assignment diagnostic figure
- plot the fixed corridor, split line, events, and mainshocks
- make sure the figure clearly shows which events belong to the entire/north/south domains

### (C) Optional robustness figures
- If useful, add a split-line sensitivity summary for 35.70 / 35.72 / 35.74 degrees N.
- Keep this secondary; do not replace the main two-panel figure with it.

## 7. Interpretation rules
- The primary conclusion must be based on the Entire vs North vs South comparison.
- Do not replace the primary comparison with Region A, Mw6.4/Mw7.1 circles, or all-region diagnostics in this task.
- Focus on whether:
    - north and south are similar in earlier cumulative periods
    - north tends to lower p-values later in the interevent period
    - south remains comparable to or higher than the entire-area reference later in the interevent period
- Do not over-interpret windows with very low counts.
- If the trend is weak or inconsistent, report that honestly.

## 8. Computational requirements
- Process each major step independently and save outputs for that step.
- Use parallel computation for bootstrap uncertainty estimation if helpful.
- Display progress information during long computations whenever possible.
</user_request>

## Planned Workflow
<experiment_plan>
# Goal
Perform a primary Omori-Utsu comparison for the Ridgecrest interevent period between the Mw 6.4 and Mw 7.1 mainshocks, using the fixed Mw 7.1 fault-zone corridor and its northern/southern subdivisions, to test whether the northern subdivision shows systematically smaller fitted pure power-law p-values than the southern subdivision in later cumulative periods.

## Planning Assumptions
- Use only the provided observational catalog and mainshock metadata; no model data are needed.
- Primary analysis window is the open interval `(Mw 6.4 origin time, Mw 7.1 origin time)`.
- Primary magnitude threshold is fixed at `M >= 3.0`; any lower-threshold or Mc-based analysis is secondary and must be executed only after the primary workflow is complete.
- Primary spatial definition is fixed by the user:
  - centerline start `(-117.735813, 35.897499)`
  - centerline end `(-117.362520, 35.559488)`
  - strike `138.0°`
  - total corridor width `6.0 km` (`3.0 km` half-width)
  - primary split latitude `35.72°N`
  - robustness-only split latitudes `35.70°N` and `35.74°N`
- Primary rate model is the two-parameter pure power-law `lambda(t) = K * t^(-p)` fit by maximum likelihood over cumulative windows `[0, t_n]`; do not replace the primary result with a `K-c-p` Omori-Utsu model.
- Because the pure power-law is singular at `t = 0`, the likelihood must explicitly use positive event times only and must document the lower bound used in each fit; recommended rule is to set the fitted interval lower bound to the first observed event time in that domain-window (`t_min = min(t_i)`), while keeping the analysis time reference at Mw 6.4.
- Windows with too few events, degenerate timing, invalid likelihood, non-finite optimum, or failed optimization/bootstrap convergence must be marked explicitly as failure/unconstrained rather than forced.
- Bootstrap uncertainty is required for successful fits and must report at least:
  - median `p`
  - 2.5 percentile
  - 97.5 percentile
  - bootstrap success diagnostics
- Northern-domain windows with `N <= 20` must be flagged for open-circle plotting in the main figure.
- Use the fewest cohesive scripts practical:
  - Script 1: data ingestion, time reference, local projection, corridor/domain assignment, domain diagnostics, count tables, metadata, and validated event-level analysis table
  - Script 2: cumulative-window extraction, MLE fitting, bootstrap estimation, result merging, panel-a/panel-b generation, and optional split-line robustness products

## Analysis Plan

### Task 1: Build the interevent catalog subset and fixed spatial domains
- Task description:
  - Read the relocated catalog and mainshock metadata.
  - Identify the Mw 6.4 and Mw 7.1 mainshocks from `main_shock_events.csv`.
  - Compute time since Mw 6.4 for all catalog events.
  - Restrict to interevent events strictly between Mw 6.4 and Mw 7.1.
  - Project the catalog and corridor to a local metric coordinate system.
  - Construct the fixed Mw 7.1 fault-zone corridor and assign events to the entire, northern, and southern domains.
  - Save reusable event-level outputs for all later fitting and plotting.
- Required data sources:
  - `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/TRACE_ridgecrest_relocated.csv`
  - `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/main_shock_events.csv`
- Parameter selection strategy:
  - Parse `event_time` as UTC timestamps.
  - Identify Mw 6.4 and Mw 7.1 rows by magnitude from `main_shock_events.csv`.
  - Define `T = 0` at the Mw 6.4 origin time and compute `t_days = (event_time - T0)` in days.
  - Interevent subset: keep events with `event_time > T0` and `event_time < T71`.
  - Use a local metric projection centered near the corridor midpoint so along-strike and cross-strike distances are computed consistently in km.
  - Corridor membership:
    - finite centerline segment from the specified start/end points
    - perpendicular distance `<= 3.0 km`
    - projected along-line position within the segment endpoints
  - Primary split:
    - North: corridor events with `latitude > 35.72`
    - South: corridor events with `latitude < 35.72`
    - events exactly on `35.72` remain in Entire only unless a documented deterministic non-duplicating rule is used
  - Also compute north/south assignment flags for `35.70` and `35.74` for robustness-only analysis.
  - Preserve all interevent events regardless of magnitude in the event-level table; apply `M >= 3.0` only in Task 3.
- Constraints:
  - Use the user-specified geometry exactly; do not optimize strike, width, endpoints, or split latitude from the data.
  - Entire area is defined only by corridor membership; north/south must be strict subsets of the corridor.
  - Domain assignment must be traceable back to source catalog rows.
- Key outputs:
  - Event-level interevent domain table containing at least:
    - `event_time, latitude, longitude, depth_km, magnitude`
    - `t_days`
    - projected coordinates
    - along-strike distance
    - cross-strike distance
    - `in_entire_corridor`
    - `north_35p72`, `south_35p72`
    - `north_35p70`, `south_35p70`
    - `north_35p74`, `south_35p74`
  - Compact primary domain-count CSV for:
    - Entire area
    - Northern area
    - Southern area
  - Metadata CSV or JSON containing:
    - Mw 6.4 time
    - Mw 7.1 time
    - `0.732 day`
    - `1.404 day`
    - corridor geometry
    - width
    - primary split latitude

### Task 2: Generate and validate the domain-definition diagnostics
- Task description:
  - Produce the required domain-assignment figure and validate that the fixed corridor and north/south assignments are internally consistent before any Omori fitting.
- Required data sources:
  - Event-level interevent domain table from Task 1
  - Mainshock metadata from Task 1
- Parameter selection strategy:
  - Plot all interevent events colored by time since Mw 6.4.
  - Overlay:
    - Mw 7.1 centerline
    - corridor boundaries
    - the `35.72°N` split line
    - events assigned to northern and southern domains
    - Mw 6.4 and Mw 7.1 mainshocks
  - Use the same fixed geometry as Task 1; if plotting in lon/lat, transform corridor boundaries back from the projected coordinates consistently.
  - Validate counts in the figure layers against the saved primary domain-count CSV.
- Constraints:
  - The diagnostic figure must clearly distinguish:
    - all interevent events
    - corridor membership
    - north/south subsets
    - the mainshocks
  - This figure is for validating the fixed primary domain definition, not for exploring alternative geometries.
- Key outputs:
  - Domain-assignment diagnostic figure
  - Domain-assignment check table with counts for:
    - all interevent events
    - entire corridor
    - north
    - south
    - exact-on-split events if any

### Task 3: Fit cumulative pure power-law Omori models for the three primary domains
- Task description:
  - For each primary domain and each fixed cumulative period endpoint, fit the pure power-law rate model `lambda(t)=K*t^(-p)` by MLE using only interevent events with `M >= 3.0`.
  - Save fit status, event counts, fitted parameters, and explicit failure reasons.
- Required data sources:
  - Event-level interevent domain table from Task 1
  - Metadata file from Task 1
- Parameter selection strategy:
  - Primary cumulative period endpoints in days:
    - `0.30, 0.50, 0.68, 0.732, 0.85, 1.00, 1.10, 1.22, 1.404`
  - Primary domains:
    - Entire area
    - Northern area at `35.72`
    - Southern area at `35.72`
  - For each domain-period:
    - keep only events with `magnitude >= 3.0`
    - keep only `0 < t_days <= period_days`
    - record event count `N`
    - if `N` is too small or event times are degenerate, mark failure/unconstrained
    - set `t_min_used_days = min(t_i)` for the likelihood lower bound when needed to regularize the singularity at `t=0`
    - set `t_max_used_days = period_days`
    - estimate `p` and `K` under the truncated observation interval `[t_min_used_days, period_days]`
    - store convergence status and any warnings
  - Northern-domain windows with `N <= 20` must set `low_count_open_circle = true`.
  - Southern-domain early windows that fail must remain missing in plots/tables rather than being interpolated.
- Constraints:
  - Apply the same fitting rules to Entire, North, and South to preserve comparability.
  - Do not substitute alternative models for failed windows.
  - Treat `0.732 day` and `1.404 day` as standard endpoints within the fixed endpoint list.
- Key outputs:
  - Primary fit table CSV with at least:
    - `domain_label`
    - `period_days`
    - `event_count`
    - `success_flag`
    - `failure_reason`
    - `p_fit`
    - `K_fit`
    - `t_min_used_days`
    - `t_max_used_days`
    - `low_count_open_circle`
  - Fit-input audit table listing the event times used in each domain-period window

### Task 4: Estimate bootstrap uncertainty for p and merge final primary results
- Task description:
  - For each successful primary-domain/period fit, bootstrap-resample the event times, refit the same pure power-law model, and merge uncertainty summaries into the final results table.
- Required data sources:
  - Primary fit table from Task 3
  - Fit-input audit table from Task 3
- Parameter selection strategy:
  - Bootstrap within each successful domain-period window by resampling event times with replacement.
  - Reuse the same fitting formulation, lower-bound handling rule, and success/failure criteria as in Task 3.
  - Use a fixed bootstrap replicate count across windows when practical; record the chosen replicate count in metadata.
  - Run bootstrap in parallel across domain-period windows or replicate blocks if helpful.
  - Report progress during long bootstrap runs.
  - For each domain-period, summarize:
    - bootstrap median `p`
    - bootstrap 2.5 percentile
    - bootstrap 97.5 percentile
    - number of successful bootstrap replicates
    - number of failed bootstrap replicates
    - bootstrap success fraction
- Constraints:
  - Failed bootstrap replicates must be counted and retained in diagnostics.
  - If bootstrap validity is poor for a window, keep the primary fit but flag the uncertainty estimate as unstable.
- Key outputs:
  - Bootstrap summary CSV
  - Final merged primary-results CSV containing at least:
    - `domain_label`
    - `period_days`
    - `event_count`
    - `success_flag`
    - `failure_reason`
    - `p_fit`
    - `bootstrap_p_median`
    - `bootstrap_p_q025`
    - `bootstrap_p_q975`
    - `bootstrap_success_count`
    - `bootstrap_failure_count`
    - `bootstrap_success_fraction`
    - `low_count_open_circle`

### Task 5: Create the required main two-panel figure
- Task description:
  - Produce the required primary two-panel figure with panel a for cumulative p-value comparison and panel b for the final entire-area rate-fit diagnostic.
- Required data sources:
  - Final merged primary-results CSV from Task 4
  - Fit-input audit table from Task 3
  - Metadata from Task 1
- Parameter selection strategy:
  - Panel a:
    - x-axis: `Period [day]`
    - y-axis: `p value`
    - plot Entire in grey, North in blue, South in red
    - use filled circles with vertical uncertainty bars for ordinary successful points
    - use open blue circles for northern points with `N <= 20`
    - leave failed/unconstrained points absent
    - draw vertical lines at `0`, `0.732`, and `1.404` day
    - label panel as `a`
  - Panel b:
    - use only the Entire-area result for the final `1.404 day` period
    - compute observed seismicity rate `lambda [day^-1]` versus time since Mw 6.4 on log-log axes
    - use log-spaced or equivalently documented sparse-safe time bins for visualization only
    - overlay the fitted `K*t^(-p)` curve from the final Entire-area fit
    - annotate fitted `p` with bootstrap uncertainty
    - annotate the period `1.404 [day]`
    - label panel as `b`
- Constraints:
  - Panel a is the primary scientific figure and must remain focused on Entire vs North vs South at the primary split `35.72°N`.
  - Panel b must use only the final `1.404 day` Entire-area fit.
  - Observed rate binning in panel b is a display diagnostic and must not alter the MLE fitting procedure.
- Key outputs:
  - Main two-panel figure
  - Panel-b support table with bin edges, counts, observed rates, and fitted rates

### Task 6: Run split-line robustness checks for 35.70 / 35.72 / 35.74
- Task description:
  - Repeat the north/south cumulative p-value workflow for split latitudes `35.70`, `35.72`, and `35.74` to assess robustness of the later-period north-versus-south contrast.
- Required data sources:
  - Event-level interevent domain table from Task 1
  - Metadata from Task 1
  - Same fitting and bootstrap workflow as Tasks 3–4
- Parameter selection strategy:
  - Keep all non-split parameters fixed:
    - same corridor
    - same `M >= 3.0`
    - same cumulative endpoints
    - same MLE formulation
    - same bootstrap method
  - Save north/south results separately for each split latitude.
  - Summarize later-period contrasts, especially near:
    - `1.10 day`
    - `1.22 day`
    - `1.404 day`
- Constraints:
  - This is secondary and must not replace the primary `35.72°N` comparison or the required main two-panel figure.
  - Entire-area results do not change with split latitude and should not be redundantly redefined.
- Key outputs:
  - Split-sensitivity results CSV for north/south domains across `35.70 / 35.72 / 35.74`
  - Optional split-line robustness figure or compact summary table

### Task 7: Validate deliverables and prepare interpretation-support tables
- Task description:
  - Perform final consistency checks and save compact comparison-ready tables that directly support the user’s scientific question.
- Required data sources:
  - All outputs from Tasks 1–6
- Parameter selection strategy:
  - Validate:
    - Mw 6.4 and Mw 7.1 times in metadata against mainshock file
    - `1.404 day` consistency with the Mw 7.1 endpoint
    - north and south counts do not exceed entire-domain counts
    - every plotted point corresponds to a row in the final results CSV
    - missing points are explicitly flagged as failed/unconstrained
  - Build a compact comparison table for the primary split `35.72` including:
    - north-minus-south `p_fit`
    - north-minus-south bootstrap median difference
    - interval-overlap indicator
    - low-count caution flags
    - later-period markers
- Constraints:
  - Primary interpretation must remain descriptive and count-aware:
    - compare early vs later cumulative periods
    - check whether North tends lower later
    - avoid over-interpreting low-count or failed windows
  - If the trend is weak or inconsistent, preserve that outcome in the saved comparison table rather than collapsing to a forced binary claim.
- Key outputs:
  - Primary north-vs-south comparison table for split `35.72`
  - Workflow manifest listing all saved tables and figures with dependency relationships
  - Final validated deliverable set:
    - event-level interevent/domain table
    - domain-count summary CSV
    - metadata CSV or JSON
    - domain-assignment diagnostic figure
    - primary fit table
    - bootstrap summary CSV
    - final merged primary-results CSV
    - main two-panel figure
    - optional split-sensitivity products
</experiment_plan>

## Implementation Trace
- Task: 01_domain_preparation
  Description: Build the Ridgecrest interevent event table, assign fixed corridor and north-south domains, and save domain diagnostics metadata.
  Ancestors: none
  Handoff JSON: ../log/coding_progress/task_handoff/01_domain_preparation.json
  Output directory: ../outputs/01_domain_preparation
  Analysis file: ../analysis/01_domain_preparation.md
- Task: 02_omori_fitting_and_figures
  Description: Fit cumulative pure power-law Omori models with bootstrap uncertainty, create required figures, and save primary and split-sensitivity results.
  Ancestors: 01_domain_preparation
  Handoff JSON: ../log/coding_progress/task_handoff/02_omori_fitting_and_figures.json
  Output directory: ../outputs/02_omori_fitting_and_figures
  Analysis file: ../analysis/02_omori_fitting_and_figures.md

## Result Evidence Index
Use handoff JSON files as compact indexes to important outputs. Use per-task analyses for scientific interpretation. Inspect raw outputs only when the handoff and analysis are insufficient.
<task_evidence task="01_domain_preparation">
Handoff JSON: ../log/coding_progress/task_handoff/01_domain_preparation.json
{
  "meta": {
    "schema_version": 2,
    "type": "coding_task_handoff",
    "task": "01_domain_preparation",
    "generated_at": "2026-07-07T02:30:09.873278+00:00"
  },
  "status": {
    "state": "success",
    "stage": "analysis_done",
    "elapsed_sec": 459.273,
    "timing": {
      "total_sec": 459.273,
      "coding_agent_sec": 218.166,
      "code_review_sec": 13.339,
      "preflight_sec": 0.968,
      "script_execution_sec": 67.238,
      "result_check_sec": 105.322,
      "task_analysis_sec": 52.063
    },
    "quality_flags": [
      "task_status:success"
    ]
  },
  "paths": {
    "root": "../..",
    "script": "../scripts/01_domain_preparation.py",
    "output_dir": "../outputs/01_domain_preparation",
    "analysis": "../analysis/01_domain_preparation.md",
    "log": "../log/task/01_domain_preparation/log_2.txt"
  },
  "outputs": {
    "primary": [
      {
        "path": "domain_assignment_checks.csv",
        "absolute_path": "../outputs/01_domain_preparation/domain_assignment_checks.csv",
        "kind": "machine_readable"
      },
      {
        "path": "domain_counts_primary.csv",
        "absolute_path": "../outputs/01_domain_preparation/domain_counts_primary.csv",
        "kind": "machine_readable"
      },
      {
        "path": "domain_metadata.json",
        "absolute_path": "../outputs/01_domain_preparation/domain_metadata.json",
        "kind": "machine_readable"
      },
      {
        "path": "interevent_domain_event_table.csv",
        "absolute_path": "../outputs/01_domain_preparation/interevent_domain_event_table.csv",
        "kind": "machine_readable"
      },
      {
        "path": "domain_assignment_diagnostic.png",
        "absolute_path": "../outputs/01_domain_preparation/domain_assignment_diagnostic.png",
        "kind": "figure"
      }
    ],
    "all": [
      "domain_assignment_checks.csv",
      "domain_assignment_diagnostic.png",
      "domain_counts_primary.csv",
      "domain_metadata.json",
      "interevent_domain_event_table.csv"
    ],
    "truncated": false
  },
  "notes": {
    "purpose": "Build the Ridgecrest interevent event table, assign fixed corridor and north-south domains, and save domain diagnostics metadata.",
    "result": "Build the Ridgecrest interevent event table, assign fixed corridor and north-south domains, and save domain diagnostics metadata. Status=success; outputs=5 discovered; primary=5.",
    "warnings": [],
    "assumptions": [],
    "limitations": []
  }
}
</task_evidence>

<task_evidence task="02_omori_fitting_and_figures">
Handoff JSON: ../log/coding_progress/task_handoff/02_omori_fitting_and_figures.json
{
  "meta": {
    "schema_version": 2,
    "type": "coding_task_handoff",
    "task": "02_omori_fitting_and_figures",
    "generated_at": "2026-07-07T02:30:09.879593+00:00"
  },
  "status": {
    "state": "success",
    "stage": "analysis_done",
    "elapsed_sec": 363.124,
    "timing": {
      "total_sec": 363.124,
      "coding_agent_sec": 112.679,
      "code_review_sec": 61.584,
      "preflight_sec": 0.359,
      "script_execution_sec": 31.099,
      "result_check_sec": 53.819,
      "task_analysis_sec": 102.222
    },
    "quality_flags": [
      "task_status:success"
    ]
  },
  "paths": {
    "root": "../..",
    "script": "../scripts/02_omori_fitting_and_figures.py",
    "output_dir": "../outputs/02_omori_fitting_and_figures",
    "analysis": "../analysis/02_omori_fitting_and_figures.md",
    "log": "../log/task/02_omori_fitting_and_figures/log_0.txt"
  },
  "outputs": {
    "primary": [
      {
        "path": "bootstrap_summary.csv",
        "absolute_path": "../outputs/02_omori_fitting_and_figures/bootstrap_summary.csv",
        "kind": "machine_readable"
      },
      {
        "path": "final_merged_primary_results.csv",
        "absolute_path": "../outputs/02_omori_fitting_and_figures/final_merged_primary_results.csv",
        "kind": "machine_readable"
      },
      {
        "path": "fit_input_audit_table.csv",
        "absolute_path": "../outputs/02_omori_fitting_and_figures/fit_input_audit_table.csv",
        "kind": "machine_readable"
      },
      {
        "path": "north_vs_south_primary_comparison_35p72.csv",
        "absolute_path": "../outputs/02_omori_fitting_and_figures/north_vs_south_primary_comparison_35p72.csv",
        "kind": "machine_readable"
      },
      {
        "path": "panel_b_rate_curve_support.csv",
        "absolute_path": "../outputs/02_omori_fitting_and_figures/panel_b_rate_curve_support.csv",
        "kind": "machine_readable"
      },
      {
        "path": "primary_fit_table.csv",
        "absolute_path": "../outputs/02_omori_fitting_and_figures/primary_fit_table.csv",
        "kind": "machine_readable"
      },
      {
        "path": "run_metadata.json",
        "absolute_path": "../outputs/02_omori_fitting_and_figures/run_metadata.json",
        "kind": "machine_readable"
      },
      {
        "path": "split_sensitivity_results.csv",
        "absolute_path": "../outputs/02_omori_fitting_and_figures/split_sensitivity_results.csv",
        "kind": "machine_readable"
      }
    ],
    "all": [
      "bootstrap_summary.csv",
      "final_merged_primary_results.csv",
      "fit_input_audit_table.csv",
      "main_two_panel_omori_comparison.png",
      "north_vs_south_primary_comparison_35p72.csv",
      "panel_b_rate_curve_support.csv",
      "primary_fit_table.csv",
      "run_metadata.json",
      "split_sensitivity_results.csv",
      "split_sensitivity_summary.png",
      "workflow_manifest.json"
    ],
    "truncated": false
  },
  "notes": {
    "purpose": "Fit cumulative pure power-law Omori models with bootstrap uncertainty, create required figures, and save primary and split-sensitivity results.",
    "result": "Fit cumulative pure power-law Omori models with bootstrap uncertainty, create required figures, and save primary and split-sensitivity results. Status=success; outputs=11 discovered; primary=8.",
    "warnings": [],
    "assumptions": [],
    "limitations": []
  }
}
</task_evidence>


## Per-Task Scientific Analyses
<task_analysis>
Task: 01_domain_preparation
Description: Build the Ridgecrest interevent event table, assign fixed corridor and north-south domains, and save domain diagnostics metadata.
Analysis file: ../analysis/01_domain_preparation.md
Output directory: ../outputs/01_domain_preparation

## Scientific Purpose

This task established the fixed spatial and temporal domain definitions needed for the later Omori-Utsu comparison during the Ridgecrest interevent period between the Mw 6.4 and Mw 7.1 mainshocks. The scientific role of this step was to create a reproducible event table for that interevent interval, assign events to the requested Mw 7.1 fault-zone corridor, and partition the corridor into northern and southern subdomains using the primary split latitude of 35.72°N, with additional split-line flags for 35.70°N and 35.74°N robustness checks.

The output of this task directly supports the later question of whether the northern part of the Mw 7.1 fault zone shows systematically smaller Omori p-values than the southern part later in the interevent period, by ensuring that the event selection and domain assignment are fixed and auditable before any rate-model fitting.

## Method and Implementation Evidence

A local metric coordinate system was used to project interevent events and the prescribed Mw 7.1 centerline/corridor geometry, allowing event positions to be expressed in kilometers and tested against the fixed 6.0 km wide corridor. The corridor geometry stored in metadata matches the requested setup: strike 138.0°, centerline start at (-117.735813, 35.897499), centerline end at (-117.362520, 35.559488), total width 6.0 km, half-width 3.0 km, and derived centerline length 50.47 km. These details are preserved in `../outputs/01_domain_preparation/domain_metadata.json`.

The interevent event table contains, for each event between the Mw 6.4 and Mw 7.1 mainshocks, the original catalog fields plus projected coordinates and domain flags needed for subsequent analysis: `t_days`, `x_km`, `y_km`, `along_strike_km`, `cross_strike_km`, `in_entire_corridor`, and boolean north/south/on-split flags for split latitudes 35.70°, 35.72°, and 35.74°. This structure is documented by `../outputs/01_domain_preparation/interevent_domain_event_table.csv`.

Consistency checks were also saved. The check table confirms that, for the primary 35.72°N split, northern plus southern counts exactly equal the entire-corridor count, with no events falling exactly on the split line. This is important because it shows the primary partition is exhaustive and non-overlapping for the corridor selection. These checks are in `../outputs/01_domain_preparation/domain_assignment_checks.csv`.

The domain-assignment diagnostic figure visually verifies that the mapped event selections are scientifically coherent: the fixed corridor follows the Mw 7.1 fault trend, the 35.72°N split line cuts the corridor as intended, and the north/south assigned subsets occupy the expected sides of the split. This figure is `../outputs/01_domain_preparation/domain_assignment_diagnostic.png`.

## Key Results and Evidence Files

1. **The interevent catalog for this task contains 4,714 events between the Mw 6.4 and Mw 7.1 mainshocks.**  
   - Evidence: `../outputs/01_domain_preparation/domain_assignment_checks.csv` reports `all_interevent_events = 4714`.  
   - Supporting metadata: `../outputs/01_domain_preparation/domain_metadata.json` gives the Mw 6.4 and Mw 7.1 times as `2019-07-04T17:33:49.040000+00:00` and `2019-07-06T03:19:53.040000+00:00`.

2. **The fixed Mw 7.1 fault-zone corridor captures 2,852 of the 4,714 interevent events across all magnitudes.**  
   - Evidence: `../outputs/01_domain_preparation/domain_counts_primary.csv` and `../outputs/01_domain_preparation/domain_assignment_checks.csv`.  
   - The event-table column `in_entire_corridor` in `../outputs/01_domain_preparation/interevent_domain_event_table.csv` preserves this assignment event by event.

3. **For the primary split at 35.72°N, the corridor partition is balanced enough to support later north-vs-south comparison, with slightly more events in the south.**  
   - Entire area: 2,852 events, including 109 with M ≥ 3.0  
   - Northern area: 1,402 events, including 50 with M ≥ 3.0  
   - Southern area: 1,450 events, including 59 with M ≥ 3.0  
   - Evidence: `../outputs/01_domain_preparation/domain_counts_primary.csv` and `../outputs/01_domain_preparation/domain_metadata.json`.

4. **The primary 35.72°N split produces a clean, non-overlapping partition of the corridor.**  
   - `on_split_35p72_all_magnitudes = 0`  
   - `north_plus_south_35p72_all_magnitudes = 2852`  
   - `north_plus_south_minus_entire_35p72_all_magnitudes = 0`  
   - Evidence: `../outputs/01_domain_preparation/domain_assignment_checks.csv`.  
   - This is a key integrity result for later cumulative Omori fitting because it confirms that north and south exactly tile the corridor without double counting or ambiguous boundary cases.

5. **The diagnostic figure supports the intended spatial interpretation of the domains.**  
   - The figure shows:
     - all interevent events,
     - corridor events colored by time since Mw 6.4,
     - the Mw 7.1 centerline,
     - dashed corridor boundaries,
     - the 35.72°N split,
     - north-assigned events in blue,
     - south-assigned events in red,
     - Mw 6.4 and Mw 7.1 mainshocks as star symbols.  
   - Visual assessment indicates the corridor is aligned with the NW-SE Mw 7.1 seismicity trend, and the north/south subsets lie predominantly on the intended sides of the split.  
   - Evidence: `../outputs/01_domain_preparation/domain_assignment_diagnostic.png`.

6. **The output table is ready for later period-by-period Omori-Utsu fitting without redefining domains.**  
   - The event table already includes the required ingredients for cumulative-window filtering: event time, magnitude, time since Mw 6.4 (`t_days`), projected coordinates, corridor membership, and north/south flags for the primary and robustness split lines.  
   - Evidence: `../outputs/01_domain_preparation/interevent_domain_event_table.csv`.

## Limitations and Assumptions

- This task is limited to domain preparation and diagnostics. It does **not** perform Omori-Utsu fitting, bootstrap uncertainty estimation, or any p-value comparison yet.
- Although the overall M ≥ 3.0 counts are adequate for the full interevent interval (109 entire, 50 north, 59 south), some early cumulative periods may still have low counts, especially in the subdivided domains. That later issue is not resolved here and must be handled during fitting.
- The diagnostic figure suggests events cluster densely near the 35.72°N boundary, so later split-line sensitivity using 35.70°N and 35.74°N remains scientifically relevant even though the primary partition is clean.
- The metadata stores a truncated WKT snippet for the local projection rather than a full standalone CRS definition, though the derived projected outputs and corridor metrics indicate the projection step was successfully applied.
- The event table excerpt confirms the presence of the expected fields, but this task report does not independently re-derive the geometry from source code; it relies on the saved outputs and consistency checks.
- No warnings or failures were recorded in the handoff JSON for this task: `../log/coding_progress/task_handoff/01_domain_preparation.json`.

## Report-Ready Summary

Task 01 successfully prepared the fixed Ridgecrest interevent analysis domains required for the later Omori-Utsu comparison. Using the prescribed Mw 7.1 fault-zone corridor geometry and a local metric projection, it built an interevent event table for the period between the Mw 6.4 and Mw 7.1 mainshocks and assigned each event to the entire corridor and to north/south subdivisions for split latitudes 35.70°, 35.72°, and 35.74°. For the primary 35.72°N partition, the corridor contains 2,852 interevent events in total, divided into 1,402 northern and 1,450 southern events, with 109, 50, and 59 events respectively at the primary M ≥ 3.0 threshold. The saved integrity checks show that north plus south exactly equals the entire corridor and that no event lies exactly on the 35.72°N split, confirming a clean non-overlapping partition. The diagnostic map visually supports that the fixed corridor follows the Mw 7.1 fault trend and that the north/south assignments are spatially coherent. The main evidence files are `../outputs/01_domain_preparation/interevent_domain_event_table.csv`, `../outputs/01_domain_preparation/domain_counts_primary.csv`, `../outputs/01_domain_preparation/domain_assignment_checks.csv`, `../outputs/01_domain_preparation/domain_metadata.json`, and `../outputs/01_domain_preparation/domain_assignment_diagnostic.png`.
</task_analysis>

<task_analysis>
Task: 02_omori_fitting_and_figures
Description: Fit cumulative pure power-law Omori models with bootstrap uncertainty, create required figures, and save primary and split-sensitivity results.
Analysis file: ../analysis/02_omori_fitting_and_figures.md
Output directory: ../outputs/02_omori_fitting_and_figures

## Scientific Purpose

This task implemented the primary Omori-type comparison for the Ridgecrest interevent period between the Mw 6.4 and Mw 7.1 mainshocks, restricted to the fixed Mw 7.1 fault-zone corridor and its north/south subdivisions. The scientific target was to test whether, later in the interevent period, the northern part of the Mw 7.1 fault zone exhibits systematically smaller pure power-law Omori exponents (`p`) than the southern part.

The analysis used the requested cumulative period endpoints after the Mw 6.4 origin time (`T=0`): 0.30, 0.50, 0.68, 0.732, 0.85, 1.00, 1.10, 1.22, and 1.404 day, with the primary magnitude threshold `M >= 3.0`. The three primary comparison domains were:
- Entire fixed Mw 7.1 corridor,
- Northern corridor subset north of 35.72°N,
- Southern corridor subset south of 35.72°N.

A secondary robustness check repeated the north/south split at 35.70°, 35.72°, and 35.74°N.

## Method and Implementation Evidence

The task outputs show that the implemented model was the requested cumulative pure power-law Omori rate model,
`lambda(t) = K * t^(-p)`,
fit by maximum likelihood for each domain and each cumulative endpoint. The primary fit table records fitted `p`, `K`, log-likelihood, the effective time range used, and event counts for all 27 primary windows (3 domains × 9 periods), with all windows marked successful in this run:
- `../outputs/02_omori_fitting_and_figures/primary_fit_table.csv`
- `../outputs/02_omori_fitting_and_figures/final_merged_primary_results.csv`

Bootstrap uncertainty estimation was also implemented as requested. Run metadata states 1000 bootstrap replicates, and the merged results table includes bootstrap median `p`, 2.5 percentile, 97.5 percentile, and bootstrap success accounting:
- `../outputs/02_omori_fitting_and_figures/bootstrap_summary.csv`
- `../outputs/02_omori_fitting_and_figures/final_merged_primary_results.csv`
- `../outputs/02_omori_fitting_and_figures/run_metadata.json`

The handling of the `t=0` singularity was explicit rather than implicit: each fit window records a positive `t_min_used_days`, corresponding to the first event time retained in that cumulative window. For example, the entire-area fits use `t_min_used_days = 0.001421` day, and the northern-domain fits use `t_min_used_days = 0.002203` day in the earliest windows. This is documented in:
- `../outputs/02_omori_fitting_and_figures/primary_fit_table.csv`
- `../outputs/02_omori_fitting_and_figures/fit_input_audit_table.csv`

The requested low-count marking rule for the northern area was implemented. In the primary 35.72° split, the earliest northern window at 0.30 day has `N=19` and is flagged `low_count_open_circle = True`; later northern windows exceed 20 events and are not flagged:
- `../outputs/02_omori_fitting_and_figures/final_merged_primary_results.csv`
- `../outputs/02_omori_fitting_and_figures/main_two_panel_omori_comparison.png`

The main figure and support table confirm that panel b used the entire-area fit for the final 1.404-day cumulative period, with observed binned rates on log-log axes and an overlaid fitted curve:
- `../outputs/02_omori_fitting_and_figures/main_two_panel_omori_comparison.png`
- `../outputs/02_omori_fitting_and_figures/panel_b_rate_curve_support.csv`

The split-line robustness analysis was saved separately and kept secondary, matching the requested workflow:
- `../outputs/02_omori_fitting_and_figures/split_sensitivity_results.csv`
- `../outputs/02_omori_fitting_and_figures/split_sensitivity_summary.png`

## Key Results and Evidence Files

### 1. Entire-corridor interevent decay is consistently sub-unity and relatively stable

The entire fixed Mw 7.1 corridor shows stable pure power-law Omori exponents through the interevent period, mostly in the range `p ≈ 0.70–0.81`. Specifically, fitted `p` progresses from 0.770 at 0.30 day, 0.811 at 0.50 day, 0.787 at 0.732 day, drops modestly to 0.696 at 0.85 day, and ends at 0.739 by 1.404 day. The corresponding final bootstrap summary is median `p = 0.748`, 95% interval `[0.641, 0.860]`, with `N = 106`.
Evidence:
- `../outputs/02_omori_fitting_and_figures/final_merged_primary_results.csv`
- `../outputs/02_omori_fitting_and_figures/main_two_panel_omori_comparison.png`

Panel b visually supports this result: the observed entire-area rate declines approximately as a straight power-law trend on log-log axes, and the plotted annotation reports `p = 0.74 [0.64, 0.86]` for the final 1.404-day window. The binned rate support table provides the observed and fitted rates used for this panel.
Evidence:
- `../outputs/02_omori_fitting_and_figures/main_two_panel_omori_comparison.png`
- `../outputs/02_omori_fitting_and_figures/panel_b_rate_curve_support.csv`

### 2. Under the primary 35.72° split, north and south are similar in early to mid cumulative periods, but the north becomes lower later

The primary north-south comparison at 35.72° shows that the earliest cumulative window is not evidence for smaller northern `p`; rather, the north is initially higher than the south. At 0.30 day, the north has `p_fit = 0.976` versus south `0.713`, but the north also has only `N = 19` and is explicitly flagged as a low-count/open-circle point. By 0.50 and 0.68 day, the north and south become very similar (`0.862` vs `0.791`; `0.801` vs `0.794`).
Evidence:
- `../outputs/02_omori_fitting_and_figures/north_vs_south_primary_comparison_35p72.csv`
- `../outputs/02_omori_fitting_and_figures/final_merged_primary_results.csv`
- `../outputs/02_omori_fitting_and_figures/main_two_panel_omori_comparison.png`

After about 0.732–0.85 day, the primary pattern changes. At 0.732 day the two are still nearly identical (`north 0.787`, `south 0.799`). From 0.85 day onward, the northern `p` drops below the southern `p` and remains lower through the late interevent period:
- 0.85 day: north 0.567, south 0.785
- 1.00 day: north 0.579, south 0.805
- 1.10 day: north 0.611, south 0.805
- 1.22 day: north 0.648, south 0.805
- 1.404 day: north 0.583, south 0.858

The north-minus-south fitted differences are therefore negative in all of these later windows, ranging from about `-0.16` to `-0.27`, with the largest separation at the final 1.404-day endpoint (`-0.274` in fitted `p`; `-0.267` in bootstrap median).
Evidence:
- `../outputs/02_omori_fitting_and_figures/north_vs_south_primary_comparison_35p72.csv`
- `../outputs/02_omori_fitting_and_figures/main_two_panel_omori_comparison.png`

This directly supports the requested qualitative interpretation: north and south are broadly similar through the earlier cumulative periods, while the north tends to lower `p` values later in the interevent period.

### 3. The south remains comparable to or above the entire-area reference later in the period

In the later windows, the southern estimates stay near or above the entire-area values. Examples:
- 0.85 day: south 0.785 vs entire 0.696
- 1.00 day: south 0.805 vs entire 0.717
- 1.10 day: south 0.805 vs entire 0.733
- 1.22 day: south 0.805 vs entire 0.766
- 1.404 day: south 0.858 vs entire 0.739

Thus, the late-time reduction in `p` is not a whole-corridor-wide behavior; it is concentrated in the northern subdivision under the primary split, while the southern domain remains comparable to or higher than the corridor-wide reference.
Evidence:
- `../outputs/02_omori_fitting_and_figures/final_merged_primary_results.csv`
- `../outputs/02_omori_fitting_and_figures/main_two_panel_omori_comparison.png`

### 4. The late-time north-lower-than-south pattern is present visually, but its magnitude is sensitive to the exact north/south split line

The split-sensitivity figure compares the north/south `p` trajectories for 35.70°, 35.72°, and 35.74°N. In all three panels, the north starts relatively high at short periods and the north-south curves converge near ~0.7–0.8 day. Beyond that, the north lies below the south in the later part of the interevent sequence. This indicates that the sign of the late north-south contrast is robust.
Evidence:
- `../outputs/02_omori_fitting_and_figures/split_sensitivity_summary.png`

However, the magnitude of the northern decline depends strongly on the split latitude. Numerical sensitivity results show the final 1.404-day northern `p_fit` changes from:
- 0.699 at 35.70°,
- 0.583 at 35.72°,
- substantially lower at 35.74° in the figure.

The image analysis indicates that the southern trajectory is comparatively stable across split lines, whereas the northern trajectory shows the strongest sensitivity after ~0.8 day. This means the inference that “north becomes lower than south later” is more robust than any exact estimate of how much lower it is.
Evidence:
- `../outputs/02_omori_fitting_and_figures/split_sensitivity_results.csv`
- `../outputs/02_omori_fitting_and_figures/split_sensitivity_summary.png`

### 5. All requested primary windows were fit successfully, with no bootstrap-warning windows in this run

Run metadata reports:
- 27 successful primary windows,
- 0 failed primary windows,
- 0 bootstrap-warning windows,
- 1000 bootstrap replicates requested,
- primary split latitude 35.72°,
- final period 1.404 day,
- Mw 6.4 and Mw 7.1 origin times saved explicitly.

This confirms that the primary workflow produced a complete result set without forced gap filling.
Evidence:
- `../outputs/02_omori_fitting_and_figures/run_metadata.json`
- `../outputs/02_omori_fitting_and_figures/workflow_manifest.json`

## Limitations and Assumptions

- The present task output set does not include the requested domain-assignment diagnostic figure; that diagnostic appears to belong to Task 01 domain preparation rather than this task’s output directory. Therefore, geometric event assignment and corridor membership for the Omori fits should be cross-referenced to Task 01 outputs rather than inferred solely from Task 02.
- The pure power-law model is the primary model here by design. No three-parameter `K-c-p` Omori-Utsu comparison is provided in this task, so early-time incompleteness or short-time singular behavior is handled operationally by starting each fit at the first observed event time (`t_min_used_days > 0`), not by estimating `c`.
- The earliest northern point at 0.30 day has only 19 events and is correctly flagged as low-count/open-circle. It should not be over-interpreted. More generally, the northern bootstrap intervals are much wider than those for the entire area and often wider than those for the south, indicating weaker parameter constraint in the northern subset.
- In the primary 35.72° north-vs-south comparison table, the bootstrap-interval-overlap flag remains `True` for all periods, including the later windows where point estimates diverge. This means the late north-lower-than-south pattern is visible and systematic in the fitted trajectories, but not cleanly separated by non-overlapping 95% bootstrap intervals under this implementation.
- The split-sensitivity analysis shows that the late northern `p` decrease is sensitive to the exact latitude used to define north versus south. The sign of the late contrast is relatively stable, but the magnitude is not. This limits how strongly one should interpret the exact numerical north-south difference.
- Panel b represents the entire-area final-period fit only. It validates the whole-corridor decay shape but does not independently diagnose whether the north or south alone obeys the same rate form over the full interval.
- No failed primary fits were reported in this run, so the task does not demonstrate the requested “leave missing rather than fabricate” behavior for underconstrained windows; it only confirms that such missing-value handling was not needed here.

## Report-Ready Summary

This task completed the requested cumulative pure power-law Omori analysis for the Ridgecrest interevent period (`M >= 3.0`) within the fixed Mw 7.1 fault-zone corridor and its north/south subdivisions. The main figure, `../outputs/02_omori_fitting_and_figures/main_two_panel_omori_comparison.png`, shows that the entire corridor has a relatively stable sub-unity decay exponent (`p ≈ 0.7–0.8`) across cumulative periods, ending at `p = 0.739` with bootstrap median `0.748` and 95% interval `[0.641, 0.860]` at 1.404 day. The panel-b rate curve is consistent with a whole-corridor power-law decay over the interevent interval.

For the primary 35.72° split, the north and south are similar through the earlier cumulative periods and near-equal by 0.68–0.732 day, but from 0.85 day onward the northern `p` becomes consistently smaller than the southern `p`. By the final 1.404-day endpoint, the north has `p_fit = 0.583` while the south has `p_fit = 0.858`, and the south also remains above the entire-area reference (`0.739`). This supports the intended qualitative conclusion that the northern part tends toward smaller late-interevent `p` values, while the southern part remains comparable to or higher than the whole-corridor behavior. The main numerical evidence is preserved in `../outputs/02_omori_fitting_and_figures/final_merged_primary_results.csv` and `../outputs/02_omori_fitting_and_figures/north_vs_south_primary_comparison_35p72.csv`.

The robustness analysis, summarized in `../outputs/02_omori_fitting_and_figures/split_sensitivity_summary.png`, indicates that the late north-lower-than-south tendency persists across nearby split latitudes, but the magnitude of the northern decrease is boundary-sensitive. Therefore, the report-ready interpretation should be: there is a credible late-period tendency for the northern Mw 7.1 fault-zone subset to exhibit smaller `p` values than the southern subset, but the strength of that contrast is uncertain and should not be overstated, especially given wider northern uncertainties and split-line sensitivity.
</task_analysis>


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
