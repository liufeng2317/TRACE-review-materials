<science_report_context>

## Scientific Objective
<user_request>
You are an earthquake scientist and data-analysis agent.

Task:
Diagnose the possible sequence behavior around M1, M2, and M3 in the Aomori earthquake catalog. The focus of this stage is to characterize each mainshock-centered sequence.

Scientific motivation:
The Aomori sequence contains three large earthquakes-clusters and multiple M4-M6 events within a short time span. 
The goal is to describe how seismicity evolved before and after each mainshock, identify the most plausible behavior modes for each sequence, and separate local sequence behavior from broader regional activation signals.

Data:
Use the project data folder:
"<CASE_ROOT>/data"

Primary inputs:
- `catalog/Snet_catalog_relocate_250930_260501.csv`
- `catalog/main_earthquake.csv`

Context inputs:
- `source_mechanism/Snet_mecha.csv`
- `stations/station.sta`

Core analysis:

1. Build a mainshock-referenced event table
For each event and each mainshock, compute relative time, epicentral distance, depth difference, distance band, and whether the event is the mainshock-like event. Use a practical tolerance to identify the mainshock-like event.

2. Visualize short-window sequence morphology (specific window)
Create diagnostic figures for visual comparison of the M1, M2, and M3 short-window sequence morphology.

Generate `magnitude_time_distance_pm7d_100km.png` as a 3x2 subplot figure:
- rows: M1, M2, M3;
- left column: magnitude versus relative time within +/-7 days and <=100 km;
- right column: distance to mainshock versus relative time for the same events;
- color points by distance band: 0-30 km, 30-60 km, 60-100 km;
- scale marker size by magnitude;
- highlight M4+ events with a black edge;
- mark the mainshock-like event with a star;
- draw vertical line at relative time 0 and horizontal reference lines for M4/M5 on magnitude panels and 30/60 km on distance panels.

Generate `m4plus_sequence_views_pm7d_100km.png` as a second 3x2 subplot figure:
- rows: M1, M2, M3;
- left column: M4+ magnitude versus relative time;
- right column: M4+ distance versus relative time, colored by magnitude;
- use the same +/-7 day and <=100 km window;
- exclude the mainshock-like event from supporting statistics but show it as a reference marker when useful.

Generate `prepost_magnitude_distance_counts_pm7d_100km.png` as a supporting summary figure, not the primary behavior-classification figure:
- compare pre/post magnitude-bin counts for each mainshock;
- compare pre/post distance-band counts for each mainshock;
- annotate M4+, M5+, and M6+ totals where possible;
- use this figure to summarize magnitude-bin and near-field versus outer-band contributions, not to diagnose swarm-like organization by itself.
- Do not use this figure alone to infer sequence type, swarm-like behavior, or triggering style. Use it only as a summary of pre/post magnitude and distance-band changes.

Generate `m4_m5_distance_band_contribution_pm7d_100km.png` to make the distance structure of moderate and large events explicit:
- show M4+ and M5+ counts by distance band for M1, M2, and M3;
- include both raw counts and normalized fractions or percentages;
- use this figure to compare whether moderate/large events are near-field dominated or distributed across 30-60 km and 60-100 km.
- Do not treat distance-band concentration alone as evidence for swarm, cascade, or migration. Interpret this figure together with magnitude hierarchy, time ordering, and event-chain structure.

3. Compute quantitative matched-window metrics

For each mainshock-cluster, compute matched pre/post statistics for ±7, ±14, and ±25 days using:
- cumulative radii: <=30 km, <=60 km, <=100 km;
- distance bands: 0-30 km, 30-60 km, 60-100 km.

Save complete metric tables for all time windows and spatial definitions, including M4+/M5+/M6+ counts, rates, post/pre ratios, magnitude-bin counts, largest events, magnitude-dominance gaps, companion-event counts, and distance-band contributions.

For visualization, do not generate separate figures for every window and spatial definition. Generate a curated set of comparison figures across M1, M2, and M3:
- pre/post magnitude-bin and distance-band summary;
- M4+/M5+ distance-band contribution figure with raw counts and normalized fractions;
- magnitude-dominance and companion-event summary;
- sensitivity heatmaps across time windows and radii;
- one optional robustness figure if ±14d or ±25d reveals a distinct pattern.

Use tables for exhaustive metrics and figures for high-level comparison.

4. Add depth and mechanism context
Summarize depth distributions for each mainshock-centered sequence, with separate summaries for M4+ and M5+ events where useful. Use focal mechanisms as contextual evidence where coverage is available, especially for checking whether events within a sequence share a similar structural domain.

5. Diagnose non-mutually-exclusive behavior dimensions

For each mainshock, evaluate the following evidence dimensions with levels: low, possible, moderate, or strong. These dimensions are evidence axes, not mutually exclusive sequence labels. A single sequence may show multiple behaviors, such as pre-mainshock activation followed by post-mainshock response, compact compound rupture, or local activation embedded in broader regional activity.

Base each score on explicit quantitative metrics from matched-window tables and event lists, not on visual impression alone. For every score, report the key metrics supporting it and the main caveats.

- Aftershock response:
Evaluate the strength of post-mainshock activation using short-window post/pre rate changes, immediate post-mainshock concentration, near-field dominance, and time-dependent decay after the mainshock. This dimension measures post-mainshock response only; it does not imply a clean single-mainshock aftershock sequence. Interpret post/pre ratios together with magnitude hierarchy, companion events, and pre-mainshock activity.

- Magnitude hierarchy and compound-event structure:
Report the magnitude gap between the mainshock and the largest non-mainshock event, gaps among the top-ranked events, the number of companion events within 0.5 and 1.0 magnitude units of the mainshock, and moment-release concentration if feasible. Separately score:
  1) single-mainshock dominance
  2) compact-cascade / compound-sequence evidence
A sequence may have strong post-mainshock activation but weak single-mainshock dominance.

- Swarm-like organization:
Evaluate whether the sequence shows weak single-mainshock dominance, repeated M4+/M5+/M6 events, small magnitude gaps, persistent or multi-peak activity, and behavior not well explained by a single post-mainshock decay. Do not equate swarm-like behavior with a confirmed physical swarm. Short-lived near-source comparable large events may indicate compact cascade, compound rupture, or compact swarm-like activity; distinguish these alternatives using duration, rate peaks, Omori/ETAS behavior, waveform similarity, relocation, and mechanism consistency.

- Foreshock or pre-mainshock activation:
Evaluate M4+/M5+ counts before the mainshock, largest pre-mainshock magnitude, timing and distance of the largest pre-mainshock event, increasing activity toward the mainshock, and whether pre-events are concentrated near the future mainshock or distributed across outer bands. Note whether pre-mainshock events may overlap with another mainshock-centered sequence or broader regional activity.

- Broader regional activation:
Evaluate the fraction and rate of all events and M4+/M5+ events in the 30–60 km and 60–100 km bands, persistence of activity outside the near field, and near-field versus outer-band contributions. Normalize by annulus area and local background rate where feasible. Do not rely only on cumulative-radius counts.

- Radial migration or expansion:
Use distance-time trends, ordered activation of distance bands, M4+ trajectories, and projected distance along relevant directions where useful. A scattered distribution across distance bands is not enough. Report a trend, regression slope, rank correlation, activation-front speed, or explicitly state that no monotonic progression is supported.

- Slow-slip-related candidate behavior:
Use catalog-level indicators only as screening evidence, such as sustained activity, broad spatial distribution, migration-like patterns, depth consistency, or repeated moderate events. Catalog evidence alone cannot establish slow slip. Do not assign moderate or strong support unless there is clear sustained migration-like activity in a plausible structural/depth domain; otherwise classify it only as an external-comparison candidate requiring GNSS, tremor, ocean-bottom pressure, or slow-slip catalog comparison.

If regional prior studies suggest known swarm activity, include swarm-like behavior as a plausible hypothesis to test, but do not assume it by default.

6. Final report:
Write a concise scientific diagnosis that includes:
1. a visual summary of the +/-7 day behavior for M1, M2, and M3;
2. a per-mainshock interpretation using the behavior dimensions above;
3. a compact evidence table showing the behavior-dimension scores and the key metrics supporting each score;
4. a short statement of what should not be over-interpreted from catalog evidence alone;
5. a short list of verification analyses that would be needed to strengthen or reject the candidate behavior interpretations.

7. Notes and Requirements:
Figure Requirements: 
- Nature publishable quality figure
- Figure should be clear and concise, with no unnecessary elements
</user_request>

## Planned Workflow
<experiment_plan>
# Goal
Diagnose and compare the mainshock-centered sequence behavior around M1, M2, and M3 in the Aomori relocated earthquake catalog by constructing a unified event–mainshock reference table, generating the required short-window morphology figures, computing matched pre/post metrics across windows and spatial definitions, adding depth and focal-mechanism context, and assigning evidence-based non-exclusive behavior-dimension scores with explicit caveats.

## Planning Assumptions
- Use observation data only from the provided project folder:
  - `catalog/Snet_catalog_relocate_250930_260501.csv`
  - `catalog/main_earthquake.csv`
  - `source_mechanism/Snet_mecha.csv`
  - `stations/station.sta`
- One primary task script should handle input validation, event-reference table construction, mainshock-like matching, metric computation, figure generation, and immediate output checks; one secondary task script should convert saved tables into behavior-dimension scores and the concise scientific diagnosis.
- Distances should be computed as horizontal epicentral distance in km from each catalog event to each mainshock; retain signed and absolute depth difference in km.
- Mainshock-like event identification must be deterministic and recorded. Use staged matching with time difference as the primary criterion and hypocentral proximity plus magnitude consistency as tie-breakers; preserve ambiguity diagnostics.
- All event rows should be retained in the master event–mainshock table, including events outside 100 km, because regional-activation and overlap diagnostics require the full reference table before filtering.
- Required fixed-window morphology figures are:
  - `magnitude_time_distance_pm7d_100km.png`
  - `m4plus_sequence_views_pm7d_100km.png`
  - `prepost_magnitude_distance_counts_pm7d_100km.png`
  - `m4_m5_distance_band_contribution_pm7d_100km.png`
- Quantitative matched-window analyses must use symmetric windows of ±7, ±14, and ±25 days and both spatial summary types:
  - cumulative radii: `<=30`, `<=60`, `<=100` km
  - annular bands: `0-30`, `30-60`, `60-100` km
- Behavior-dimension scores are evidence axes, not mutually exclusive labels. Scores must come from metric tables and event lists, not from figures alone.
- Distance-band concentration alone must not be used to infer swarm-like organization, compact cascade, migration, or triggering style.
- Focal mechanisms and station metadata are contextual only; sparse or missing coverage is not negative evidence.
- Successful execution requires non-empty merged metric tables for all mainshocks, all requested windows/spatial definitions, the required figure files, and saved evidence tables for the final diagnosis.

## Analysis Plan

### Task 1: Build the unified mainshock-referenced analysis table
- Task description:
  - Load and standardize the relocated catalog and mainshock table, then create one long-format event–mainshock reference table containing every catalog event referenced to M1, M2, and M3.
- Required data sources:
  - `catalog/Snet_catalog_relocate_250930_260501.csv`
  - `catalog/main_earthquake.csv`
- Parameter selection strategy:
  - Parse origin times into a single consistent datetime field.
  - Standardize core fields to event ID, origin time, latitude, longitude, depth, and magnitude; if no stable event ID exists, create one from source row index.
  - For each event relative to each mainshock, compute:
    - relative time in days and hours
    - epicentral distance in km
    - signed depth difference and absolute depth difference in km
    - cumulative-radius membership: `<=30`, `<=60`, `<=100` km
    - annular distance band: `0-30`, `30-60`, `60-100`, `>100` km
    - pre/post flag
    - magnitude-bin labels at minimum: `<4`, `4-<5`, `5-<6`, `>=6`
    - threshold flags: M4+, M5+, M6+
  - Mainshock-like identification:
    - first-pass: minimum absolute time difference within a narrow tolerance
    - tie-breakers: smallest epicentral distance, then smallest absolute depth difference, then smallest magnitude difference
    - fallback: staged tolerance relaxation if no candidate is found initially
    - record chosen event, residuals, tolerance stage, and ambiguity flag
  - Add overlap-diagnostic fields showing whether an event also falls within another mainshock-centered window/radius combination.
- Constraints:
  - Do not drop overlapping events between M1/M2/M3 reference frames.
  - Keep the original catalog rows intact; downstream filtered subsets should be derived from this master table.
  - The mainshock-like event must remain identifiable for plotting and for exclusion from non-mainshock statistics where required.
- Key outputs:
  - `mainshock_reference_event_table.csv`
  - `mainshock_like_match_summary.csv`
  - QA count table by mainshock, window, and distance category

### Task 2: Generate the required ±7 day, <=100 km morphology figures
- Task description:
  - Produce the four requested short-window figures for direct visual comparison of M1, M2, and M3 sequence morphology.
- Required data sources:
  - `mainshock_reference_event_table.csv`
  - `catalog/main_earthquake.csv`
- Parameter selection strategy:
  - Filter to `|relative_time_days| <= 7` and `epicentral_distance_km <= 100`.
  - Use a fixed distance-band color scheme across all figures:
    - `0-30` km
    - `30-60` km
    - `60-100` km
  - Use one consistent marker-size mapping from magnitude across all panels.
  - Highlight M4+ events with a black edge.
  - Show the mainshock-like event with a star marker and consistent labeling.
  - `magnitude_time_distance_pm7d_100km.png`:
    - 3x2 layout
    - rows: M1, M2, M3
    - left: magnitude vs relative time
    - right: distance vs relative time
    - include vertical line at time 0
    - include horizontal reference lines at M4 and M5 on magnitude panels
    - include horizontal reference lines at 30 and 60 km on distance panels
  - `m4plus_sequence_views_pm7d_100km.png`:
    - same 3x2 row structure
    - plot M4+ events only
    - left: magnitude vs relative time
    - right: distance vs relative time colored by magnitude
    - exclude the mainshock-like event from supporting summary statistics, but show it as a reference marker where useful
  - `prepost_magnitude_distance_counts_pm7d_100km.png`:
    - summarize pre/post magnitude-bin counts and pre/post distance-band counts for each mainshock
    - annotate M4+, M5+, M6+ totals
    - use as supporting summary only
  - `m4_m5_distance_band_contribution_pm7d_100km.png`:
    - compare M4+ and M5+ counts by distance band for M1, M2, M3
    - include raw counts and normalized fractions/percentages
- Constraints:
  - Preserve the requested 3x2 layout for the first two figures.
  - Use these figures for comparison and support; do not encode final sequence labels graphically.
  - Exclude unnecessary decorative elements.
- Key outputs:
  - `magnitude_time_distance_pm7d_100km.png`
  - `m4plus_sequence_views_pm7d_100km.png`
  - `prepost_magnitude_distance_counts_pm7d_100km.png`
  - `m4_m5_distance_band_contribution_pm7d_100km.png`
  - provenance subset table for the ±7 d, <=100 km plotted events

### Task 3: Compute matched-window metric tables across windows and spatial definitions
- Task description:
  - Build exhaustive pre/post quantitative evidence tables for all requested time windows and spatial definitions, preserving both cumulative-radius and annular-band views.
- Required data sources:
  - `mainshock_reference_event_table.csv`
- Parameter selection strategy:
  - Time windows: ±7, ±14, ±25 days.
  - Spatial definitions:
    - cumulative radii: `<=30`, `<=60`, `<=100` km
    - annular bands: `0-30`, `30-60`, `60-100` km
  - For each mainshock × window × spatial definition compute pre and post metrics:
    - total event counts and rates
    - M4+, M5+, M6+ counts and rates
    - post/pre count ratios and rate ratios
    - magnitude-bin counts and fractions
    - largest pre-event, largest post-event, and largest non-mainshock event
    - ranked event summaries and magnitude gaps:
      - mainshock minus largest non-mainshock
      - top non-mainshock gaps
    - companion-event counts within 0.5 and 1.0 magnitude units of the mainshock
    - near-field vs outer-band contributions
    - raw and normalized distance-band shares for all events and thresholded subsets
    - annulus-area-normalized counts/rates where feasible for broader-regional interpretation
    - immediate-post concentration metrics:
      - first 6 h, 12 h, 1 d, and 3 d shares within the post window
    - simple post-mainshock decay summaries from fixed time bins
    - optional catalog-derived scalar-moment concentration summary if feasible
  - Compute paired versions of metrics where needed:
    - including the mainshock-like event
    - excluding the mainshock-like event
- Constraints:
  - Keep cumulative-radius tables separate from annular-band tables.
  - Zero denominators must be flagged explicitly rather than regularized silently.
  - Non-mainshock dominance and companion statistics must exclude the mainshock-like event.
- Key outputs:
  - `matched_window_metrics_all.csv`
  - `matched_window_metrics_by_band.csv`
  - `magnitude_dominance_metrics.csv`
  - `companion_event_metrics.csv`
  - `largest_event_lists_by_window.csv`
  - `regional_outerband_metrics.csv`

### Task 4: Derive curated comparison products from the metric tables
- Task description:
  - Convert the exhaustive metric tables into a small set of high-level comparison products across M1, M2, and M3 without generating one figure per window-definition combination.
- Required data sources:
  - Outputs from Task 3
- Parameter selection strategy:
  - Required comparison themes:
    - pre/post magnitude-bin and distance-band summary
    - M4+/M5+ distance-band contribution
    - magnitude-dominance and companion-event comparison
    - sensitivity heatmaps across time windows and radii
  - Build:
    - `magnitude_dominance_companion_summary.png`
      - compare mainshock-minus-largest-companion gap
      - compare counts within 0.5 and 1.0 magnitude units
    - `window_radius_sensitivity_heatmaps.png`
      - heatmaps over window × radius for selected metrics such as:
        - post/pre ratio
        - near-field share
        - M4+ and M5+ concentration
        - dominance-gap indicators
    - one optional robustness figure only if ±14 d or ±25 d changes interpretation relative to ±7 d
- Constraints:
  - Do not duplicate the short-window morphology figures.
  - Optional robustness figure must address a distinct scientific contrast, not merely repeat another summary.
- Key outputs:
  - `magnitude_dominance_companion_summary.png`
  - `window_radius_sensitivity_heatmaps.png`
  - optional robustness figure input table and figure

### Task 5: Add temporal-structure, depth, and mechanism context
- Task description:
  - Quantify immediate post-mainshock concentration, persistence, and any radial progression, then add depth summaries and focal-mechanism context to distinguish compact local sequence behavior from broader structural-domain activation.
- Required data sources:
  - `mainshock_reference_event_table.csv`
  - `source_mechanism/Snet_mecha.csv`
  - `stations/station.sta`
- Parameter selection strategy:
  - Temporal-structure diagnostics:
    - rolling or fixed-bin event-rate summaries in ±7 d and ±25 d windows
    - local peak counts for all events and M4+ events
    - near-field vs outer-band decay contrasts
  - Radial migration/expansion diagnostics:
    - distance vs time trends for all events and M4+ subsets
    - pre and post regression slope and rank correlation
    - distance-band activation ordering
    - activation-front speed only if monotonic ordering is coherent
    - otherwise explicitly store “no monotonic progression supported”
  - Depth summaries:
    - per mainshock, summarize all events within `<=100` km for ±7, ±14, ±25 d
    - separate summaries for all events, M4+, and M5+ where sample size permits
    - pre/post median, IQR, range, and mainshock-relative depth differences
  - Mechanism context:
    - join `Snet_mecha.csv` to catalog events using time-space matching with ambiguity flags
    - summarize number of matched mechanisms per sequence
    - summarize whether mechanism-covered events appear structurally consistent or mixed
    - compare near-field vs outer-band mechanism-bearing events where coverage exists
  - Station metadata:
    - use only for optional contextual check of geographic coverage around M1, M2, M3
- Constraints:
  - A scattered distance-time cloud is not evidence of migration.
  - Mechanism evidence is contextual and should be labeled as sparse where applicable.
  - Do not infer completeness quantitatively from station positions alone.
- Key outputs:
  - `post_response_temporal_metrics.csv`
  - `migration_diagnostics.csv`
  - `depth_summary_by_mainshock.csv`
  - `depth_summary_m4_m5.csv`
  - `mechanism_match_summary.csv`
  - `mechanism_context_by_sequence.csv`
  - optional station-context summary if needed

### Task 6: Score the non-mutually-exclusive behavior dimensions
- Task description:
  - Translate the metric tables and event lists into explicit per-mainshock evidence scores for the requested behavior dimensions, with supporting metrics and caveats for every score.
- Required data sources:
  - Outputs from Tasks 3–5
  - short-window figures from Task 2 for cross-checking only
- Parameter selection strategy:
  - Score levels: low, possible, moderate, strong.
  - For each mainshock evaluate:
    - Aftershock response
      - post/pre rate change
      - immediate-post concentration
      - near-field post dominance
      - post-mainshock decay behavior
    - Magnitude hierarchy and compound-event structure
      - separate sub-scores for:
        - single-mainshock dominance
        - compact-cascade / compound-sequence evidence
      - use mainshock-largest non-mainshock gap, top-rank gaps, companion counts, and optional moment concentration
    - Swarm-like organization
      - use weak dominance, repeated M4+/M5+/M6 events, small magnitude gaps, persistent or multi-peak activity, and mismatch with a simple single-mainshock decay picture
    - Foreshock or pre-mainshock activation
      - use pre M4+/M5+ counts, largest pre-event magnitude, timing and distance of the largest pre-event, and approach-to-mainshock activity pattern
    - Broader regional activation
      - use fractions and rates in `30-60` and `60-100` km bands, area-normalized annular rates, and outer-band persistence
    - Radial migration or expansion
      - use slope, rank correlation, distance-band activation ordering, and M4+ trajectories where informative
    - Slow-slip-related candidate behavior
      - use only as a screening axis and keep conservative unless there is unusually coherent sustained migration-like activity in a plausible depth/structural domain
  - For every assigned score, store:
    - the metrics used
    - competing explanations
    - the main caveat
    - whether overlap with another mainshock-centered window may contaminate interpretation
- Constraints:
  - Do not force one exclusive sequence type per mainshock.
  - Do not assign moderate or strong slow-slip-related support from catalog evidence alone unless clear sustained migration-like evidence is present.
  - Do not equate swarm-like organization with a confirmed physical swarm.
- Key outputs:
  - `behavior_dimension_scores.csv`
  - `behavior_dimension_supporting_metrics.csv`
  - cross-mainshock evidence matrix for M1, M2, M3

### Task 7: Assemble the concise scientific diagnosis
- Task description:
  - Synthesize the quantitative tables and curated figures into the requested final diagnosis products.
- Required data sources:
  - Outputs from Tasks 2–6
- Parameter selection strategy:
  - Organize the final diagnosis into:
    1. visual summary of the ±7 day behavior for M1, M2, and M3
    2. per-mainshock interpretation across the behavior dimensions
    3. compact evidence table with scores and key metrics
    4. short statement of what should not be over-interpreted from catalog evidence alone
    5. short list of verification analyses needed to strengthen or reject the candidate interpretations
  - Verification priorities should include:
    - completeness/detection-rate assessment
    - Omori or ETAS comparison for post-mainshock decay
    - waveform similarity and repeater testing
    - refined relocation or double-difference checks for compact cascades
    - more systematic mechanism consistency tests
    - GNSS, tremor, ocean-bottom pressure, or slow-slip catalog comparison for slow-slip screening
- Constraints:
  - Keep interpretations concise and metric-based.
  - Explicitly separate local sequence behavior from broader regional activation.
  - Do not treat summary count figures alone as diagnostic of swarm, migration, or triggering style.
- Key outputs:
  - `aomori_mainshock_sequence_diagnosis.md`
  - `sequence_behavior_evidence_table.csv`

### Task 8: Script organization and execution flow
- Task description:
  - Execute the workflow with the fewest cohesive scripts and explicit dependency checks.
- Required data sources:
  - All sources above
- Parameter selection strategy:
  - Primary script:
    - validate inputs
    - build the master event–mainshock table
    - identify mainshock-like catalog matches
    - compute matched-window metrics
    - compute temporal, migration, depth, and mechanism context tables
    - generate all required and curated figures
    - save machine-readable outputs
    - perform immediate non-empty output and row-count checks
  - Secondary script:
    - read saved metric/context tables
    - assign behavior-dimension scores
    - assemble the concise diagnosis and evidence tables
- Constraints:
  - Do not split plotting, metrics, and validation into unnecessary standalone scripts.
  - Batch success is not sufficient unless the merged final tables and required figures are valid and non-empty.
- Key outputs:
  - Script 1 outputs: master table, match diagnostics, metric tables, context tables, all figures
  - Script 2 outputs: score tables, evidence tables, concise diagnosis document
</experiment_plan>

## Implementation Trace
- Task: 01_aomori_sequence_analysis
  Description: Build the mainshock-referenced sequence dataset, compute all requested metrics and context summaries, generate the required figures, score behavior dimensions, assemble the scientific diagnosis, and validate outputs in one self-contained script.
  Ancestors: none
  Handoff JSON: <CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/log/coding_progress/task_handoff/01_aomori_sequence_analysis.json
  Output directory: <CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis
  Analysis file: <CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/analysis/01_aomori_sequence_analysis.md

## Result Evidence Index
Use handoff JSON files as compact indexes to important outputs. Use per-task analyses for scientific interpretation. Inspect raw outputs only when the handoff and analysis are insufficient.
<task_evidence task="01_aomori_sequence_analysis">
Handoff JSON: <CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/log/coding_progress/task_handoff/01_aomori_sequence_analysis.json
{
  "meta": {
    "schema_version": 2,
    "type": "coding_task_handoff",
    "task": "01_aomori_sequence_analysis",
    "generated_at": "2026-05-24T02:40:48.198038+00:00"
  },
  "status": {
    "state": "success",
    "stage": "analysis_done",
    "elapsed_sec": 506.026,
    "timing": {
      "total_sec": 506.026,
      "coding_agent_sec": 193.619,
      "code_review_sec": 49.709,
      "preflight_sec": 0.559,
      "script_execution_sec": 48.078,
      "result_check_sec": 44.767,
      "task_analysis_sec": 167.58
    },
    "quality_flags": [
      "task_status:success",
      "outputs_truncated"
    ]
  },
  "paths": {
    "root": "<CASE_ROOT>/run/02_2_behavior_diagnosis",
    "script": "<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/scripts/01_aomori_sequence_analysis.py",
    "output_dir": "<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis",
    "analysis": "<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/analysis/01_aomori_sequence_analysis.md",
    "log": "<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/log/task/01_aomori_sequence_analysis/log_0.txt"
  },
  "outputs": {
    "primary": [
      {
        "path": "behavior_dimension_scores.csv",
        "absolute_path": "<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/behavior_dimension_scores.csv",
        "kind": "machine_readable"
      },
      {
        "path": "behavior_dimension_supporting_metrics.csv",
        "absolute_path": "<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/behavior_dimension_supporting_metrics.csv",
        "kind": "machine_readable"
      },
      {
        "path": "companion_event_metrics.csv",
        "absolute_path": "<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/companion_event_metrics.csv",
        "kind": "machine_readable"
      },
      {
        "path": "depth_summary_by_mainshock.csv",
        "absolute_path": "<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/depth_summary_by_mainshock.csv",
        "kind": "machine_readable"
      },
      {
        "path": "depth_summary_m4_m5.csv",
        "absolute_path": "<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/depth_summary_m4_m5.csv",
        "kind": "machine_readable"
      },
      {
        "path": "largest_event_lists_by_window.csv",
        "absolute_path": "<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/largest_event_lists_by_window.csv",
        "kind": "machine_readable"
      },
      {
        "path": "magnitude_dominance_metrics.csv",
        "absolute_path": "<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/magnitude_dominance_metrics.csv",
        "kind": "machine_readable"
      },
      {
        "path": "mainshock_like_match_summary.csv",
        "absolute_path": "<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/mainshock_like_match_summary.csv",
        "kind": "machine_readable"
      }
    ],
    "all": [
      "aomori_mainshock_sequence_diagnosis.md",
      "behavior_dimension_scores.csv",
      "behavior_dimension_supporting_metrics.csv",
      "companion_event_metrics.csv",
      "depth_summary_by_mainshock.csv",
      "depth_summary_m4_m5.csv",
      "largest_event_lists_by_window.csv",
      "m4_m5_distance_band_contribution_pm7d_100km.png",
      "m4plus_sequence_views_pm7d_100km.png",
      "magnitude_dominance_companion_summary.png",
      "magnitude_dominance_metrics.csv",
      "magnitude_time_distance_pm7d_100km.png",
      "mainshock_like_match_summary.csv",
      "mainshock_reference_event_table.csv",
      "matched_window_metrics_all.csv",
      "matched_window_metrics_by_band.csv",
      "mechanism_context_by_sequence.csv",
      "mechanism_match_summary.csv",
      "migration_diagnostics.csv",
      "optional_window_robustness_comparison.png",
      "plotted_events_pm7d_100km.csv",
      "post_response_temporal_metrics.csv",
      "prepost_magnitude_distance_counts_pm7d_100km.png",
      "qa_count_table_by_mainshock_window_distance.csv",
      "regional_outerband_metrics.csv",
      "sequence_behavior_evidence_table.csv",
      "station_context_summary.csv",
      "window_radius_sensitivity_heatmaps.png"
    ],
    "truncated": true
  },
  "notes": {
    "purpose": "Build the mainshock-referenced sequence dataset, compute all requested metrics and context summaries, generate the required figures, score behavior dimensions, assemble the scientific diagnosis, and validate outputs in one self-contained script.",
    "result": "Build the mainshock-referenced sequence dataset, compute all requested metrics and context summaries, generate the required figures, score behavior dimensions, assemble the scienti...[truncated] Status=success; outputs=28 discovered; primary=8.",
    "warnings": [],
    "assumptions": [],
    "limitations": []
  }
}
</task_evidence>


## Per-Task Scientific Analyses
<task_analysis>
Task: 01_aomori_sequence_analysis
Description: Build the mainshock-referenced sequence dataset, compute all requested metrics and context summaries, generate the required figures, score behavior dimensions, assemble the scientific diagnosis, and validate outputs in one self-contained script.
Analysis file: <CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/analysis/01_aomori_sequence_analysis.md
Output directory: <CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis

## Scientific Purpose

This task diagnosed how seismicity evolved around the three Aomori mainshocks (M1, M2, M3) by building a mainshock-referenced catalog, comparing matched pre/post windows, and scoring multiple non-exclusive behavior dimensions. The scientific aim was to distinguish local mainshock-centered sequence behavior from broader regional activation, using short-window morphology as the primary visual evidence and matched-window statistics as the quantitative basis.

The completed outputs show that the analysis was designed to answer five core questions:

1. How compact or distributed each sequence was within ±7 days and ≤100 km.
2. Whether activity was mainly pre-mainshock, post-mainshock, or both.
3. Whether each sequence was dominated by a single mainshock or involved comparable companion events.
4. How much of the activity was confined to the near field (0–30 km) versus outer bands (30–60 km, 60–100 km).
5. Whether any clear radial migration, depth-domain coherence, or mechanism coherence supported more specific interpretations.

Key report-ready evidence is concentrated in:
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/magnitude_time_distance_pm7d_100km.png`
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/m4plus_sequence_views_pm7d_100km.png`
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/behavior_dimension_scores.csv`
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/behavior_dimension_supporting_metrics.csv`
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/sequence_behavior_evidence_table.csv`

## Method and Implementation Evidence

A self-contained script generated the analysis products:
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/scripts/01_aomori_sequence_analysis.py`

Implementation evidence confirms that the workflow produced the required mainshock-centered evidence set:

### 1. Mainshock-referenced event construction
A full event table was created:
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/mainshock_reference_event_table.csv`

Mainshock-like events were explicitly matched with small residuals:
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/mainshock_like_match_summary.csv`

The matching is precise and unambiguous:
- M1 matched at 0.01 s time residual, 0.166 km epicentral residual, 0.09 km depth residual, magnitude 6.9.
- M2 matched at 0.00 s, 0.297 km, 0.04 km, magnitude 7.5.
- M3 matched at 0.01 s, 0.158 km, 0.09 km, magnitude 7.7.

### 2. Short-window morphology figures
The required short-window figures were generated and are scientifically interpretable:
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/magnitude_time_distance_pm7d_100km.png`
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/m4plus_sequence_views_pm7d_100km.png`
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/prepost_magnitude_distance_counts_pm7d_100km.png`
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/m4_m5_distance_band_contribution_pm7d_100km.png`

The plotted subset was also saved:
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/plotted_events_pm7d_100km.csv`

### 3. Quantitative matched-window metrics
Matched pre/post metrics were computed for ±7, ±14, and ±25 days, and for cumulative radii and distance bands:
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/matched_window_metrics_all.csv`
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/matched_window_metrics_by_band.csv`
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/qa_count_table_by_mainshock_window_distance.csv`

Sensitivity visualization was generated:
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/window_radius_sensitivity_heatmaps.png`
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/optional_window_robustness_comparison.png`

### 4. Magnitude hierarchy, companion events, and sequence scoring
Magnitude-dominance and companion-event metrics were saved in reusable tables and summarized visually:
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/magnitude_dominance_metrics.csv`
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/companion_event_metrics.csv`
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/magnitude_dominance_companion_summary.png`

Behavior-dimension scoring was provided in machine-readable and summary forms:
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/behavior_dimension_scores.csv`
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/behavior_dimension_supporting_metrics.csv`
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/sequence_behavior_evidence_table.csv`

### 5. Depth, mechanism, migration, and station context
Additional contextual summaries were generated:
- Depth:
  - `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/depth_summary_by_mainshock.csv`
  - `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/depth_summary_m4_m5.csv`
- Mechanism context:
  - `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/mechanism_context_by_sequence.csv`
  - `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/mechanism_match_summary.csv`
- Migration diagnostics:
  - `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/migration_diagnostics.csv`
- Temporal post-response concentration:
  - `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/post_response_temporal_metrics.csv`
- Regional outer-band context:
  - `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/regional_outerband_metrics.csv`
- Station context:
  - `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/station_context_summary.csv`

## Key Results and Evidence Files

### 1. The ±7 day sequence morphology differs strongly among M1, M2, and M3

The primary morphology figure shows three distinct sequence styles:
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/magnitude_time_distance_pm7d_100km.png`

Visual evidence from that figure indicates:
- **M1**: the most compact and near-field concentrated sequence, with dense activity immediately after the mainshock and only limited outer-band participation.
- **M2**: the most spatially distributed post-mainshock response, with substantial activation across 30–60 km and 60–100 km bands and a visually notable secondary burst several days later.
- **M3**: strong post-mainshock activation but broader spatial occupation than M1, with persistent outer-band activity and weaker single-mainshock dominance than a simple isolated aftershock cloud would suggest, though still much more mainshock-dominated than M1.

The M4+ focused figure reinforces these distinctions:
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/m4plus_sequence_views_pm7d_100km.png`

That figure shows:
- **M1** has several substantial companion events, including near-mainshock-sized events in the near field.
- **M2** has mainly post-mainshock M4+ activity and a broad distance distribution rather than a compact near-field cluster.
- **M3** has post-mainshock M4+ activity but far fewer comparable large companions than M1.

Supporting event subset:
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/plotted_events_pm7d_100km.csv`

### 2. All three mainshocks show post-mainshock activation, but the style of that response differs

The sequence summary table scores all three as having **moderate aftershock response**:
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/behavior_dimension_scores.csv`

Supporting metrics:
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/behavior_dimension_supporting_metrics.csv`

Quantitative evidence at ±7 d, ≤100 km:
- **M1**: post/pre ratio = 3.174; M4+ post/pre ratio = 2.619; near-field post fraction = 0.790; 38.3% of post events within 24 h.
- **M2**: post/pre ratio = 86.625; near-field post fraction = 0.180; 26.6% of post events within 24 h; M4+ pre count = 0 within this window so M4+ post/pre is undefined.
- **M3**: post/pre ratio = 14.649; near-field post fraction lower than M1 and higher than M2 only in relative terms of total spatial distribution; the evidence table classifies this as moderate aftershock response.

Post-response concentration through time is tabulated in:
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/post_response_temporal_metrics.csv`

For M1, 85.5% of post M4+ events occurred within 24 h and 94.5% within 72 h, consistent with a strong short-lived local response. The morphology figures suggest M2 and M3 also had major post-mainshock concentration, but M2 and M3 spread that response more broadly in space than M1.

The pre/post count comparison figure is supportive but not diagnostic on its own:
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/prepost_magnitude_distance_counts_pm7d_100km.png`

This figure shows:
- post counts exceed pre counts for all three,
- M2 has the largest absolute post count increase,
- M1 is most near-field concentrated,
- M2 and M3 include much larger outer-band contributions.

### 3. Magnitude hierarchy clearly separates M1 from M3, with M2 intermediate

The magnitude-dominance summary is one of the most report-relevant outputs:
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/magnitude_dominance_companion_summary.png`

Visual and tabulated evidence:
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/magnitude_dominance_metrics.csv`
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/companion_event_metrics.csv`

At ±7 d, ≤100 km:
- **M1**: mainshock magnitude 6.9; largest non-mainshock = 6.6; dominance gap = 0.3; 2 companions within 0.5 magnitude units; 6 within 1.0 magnitude unit.
- **M2**: mainshock magnitude 7.5; largest non-mainshock = 6.9; dominance gap = 0.6; 0 companions within 0.5; 2 within 1.0.
- **M3**: mainshock magnitude 7.7; largest non-mainshock = 5.6; dominance gap = 2.1; no companions within 0.5 or 1.0 magnitude units.

Behavior scores derived from these metrics:
- **Single-mainshock dominance**:
  - M1 = low
  - M2 = possible
  - M3 = strong
- **Compact-cascade / compound structure**:
  - M1 = moderate
  - M2 = low
  - M3 = low

These distinctions are also summarized in:
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/sequence_behavior_evidence_table.csv`

Interpretively, M1 is the clearest case of weak single-mainshock dominance and multiple large companion events; M3 is the clearest case of strong mainshock dominance; M2 falls between those end members.

### 4. Foreshock/pre-mainshock activation is strongest for M1, weak for M2, and limited but nonzero for M3

This is a major discriminant among the three sequences.

Behavior scores:
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/behavior_dimension_scores.csv`

Evidence metrics:
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/behavior_dimension_supporting_metrics.csv`
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/matched_window_metrics_all.csv`

At ±7 d, ≤100 km:
- **M1**: foreshock/pre-mainshock activation = strong. M4+ pre count = 21; M5+ pre count = 8; largest pre-event magnitude = 6.9; largest pre-event time essentially coincident with the mainshock-like time because the mainshock-like event appears in the full matched-window record; caveat explicitly notes frame overlap/regional overlap.
- **M2**: foreshock/pre-mainshock activation = low. M4+ pre count = 0; M5+ pre count = 0.
- **M3**: foreshock/pre-mainshock activation = moderate in the scored table, but the headline metrics indicate only pre M4+ = 1 at ±7 d, ≤100 km. This implies the moderate score likely reflects broader contextual evidence across windows rather than strong short-window pre-mainshock activity.

The main morphology figure supports these contrasts:
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/magnitude_time_distance_pm7d_100km.png`

Visually:
- M1 shows clear pre-mainshock activity within the diagnostic window.
- M2 shows very little meaningful pre-mainshock activity.
- M3 shows some pre-window activity, but much less convincing as a near-mainshock foreshock buildup than M1.

### 5. Broader regional activation is weak for M1, strongest for M2, and moderate for M3

This is one of the clearest quantitative contrasts in the analysis.

Behavior scores:
- M1 = low
- M2 = strong
- M3 = moderate

Evidence:
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/regional_outerband_metrics.csv`
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/m4_m5_distance_band_contribution_pm7d_100km.png`
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/prepost_magnitude_distance_counts_pm7d_100km.png`

At ±7 d:
- **M1**:
  - pre outer-band fraction (30–100 km) = 0.107
  - post outer-band fraction = 0.210
  - post M4+ outer-band fraction = 0.127
  - interpretation: still near-field dominated.
- **M2**:
  - pre outer-band fraction = 0.875
  - post outer-band fraction = 0.820
  - post M4+ outer-band fraction = 0.911
  - interpretation: overwhelmingly outer-band dominated, both for all events and M4+ events.
- **M3**:
  - headline metrics give post outer-band fraction = 0.463
  - interpretation: broader than M1 but much less outer-band dominated than M2.

The dedicated M4+/M5+ distance-band figure is especially clear:
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/m4_m5_distance_band_contribution_pm7d_100km.png`

That figure shows:
- **M1**: M4+ and M5+ overwhelmingly concentrated in 0–30 km.
- **M2**: M4+ and M5+ dominated by 30–60 km and 60–100 km contributions, with very small 0–30 km share.
- **M3**: intermediate distribution, with substantial 0–30 km and 30–60 km contributions and only small or negligible 60–100 km contribution for M5+.

Thus, M2 is the clearest case where local mainshock-centered interpretation must be separated from regional activation.

### 6. Swarm-like or compound behavior is most plausible for M1, only possible for M2 and M3

Behavior scores:
- **M1**: swarm-like organization = moderate
- **M2**: possible
- **M3**: possible

Evidence table:
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/behavior_dimension_supporting_metrics.csv`

For M1, the supporting metrics are unusually suggestive of weak hierarchy and repeated moderate-large events:
- dominance gap = 0.300
- total M4+ = 76
- total M5+ = 28
- companion events within 1.0 magnitude unit = 6

This does not prove a physical swarm, but it does support a catalog-level description of compact, weakly hierarchical, multi-large-event organization.

For M2 and M3, the swarm-like signal is weaker:
- **M2** has broad regional activation and only a few comparable large companions.
- **M3** has strong mainshock dominance, which argues against strong swarm-like classification despite broad spatial activation.

The M4+ sequence view and the dominance-companion summary together are the best figure pair for this interpretation:
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/m4plus_sequence_views_pm7d_100km.png`
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/magnitude_dominance_companion_summary.png`

### 7. No monotonic radial migration is supported for any of the three sequences

All three are scored low for radial migration/expansion:
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/behavior_dimension_scores.csv`

Migration diagnostics:
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/migration_diagnostics.csv`

Key ±7 d post metrics:
- **M1**: all-event slope = 0.894 km/day; Spearman = 0.158; M4+ slope = 2.346 km/day; M4+ Spearman = 0.417; monotonic progression supported = False.
- **M2**: all-event slope = 1.824 km/day; Spearman = 0.071; M4+ slope = -1.184 km/day; M4+ Spearman = -0.224; monotonic progression supported = False.
- **M3**: all-event slope = 2.023 km/day; Spearman = 0.149; M4+ slope = 2.550 km/day; M4+ Spearman = 0.335; monotonic progression supported = False.

The morphology figure is consistent with band occupancy and broad triggering rather than clean outward propagation:
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/magnitude_time_distance_pm7d_100km.png`

### 8. Slow-slip-related behavior is not supported beyond low-level screening

All three are scored low:
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/behavior_dimension_scores.csv`

The supporting metrics explicitly frame this as a screening-only dimension:
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/behavior_dimension_supporting_metrics.csv`

No sequence shows monotonic migration support, and none is identified as having clear catalog-level evidence sufficient for moderate or strong slow-slip-related candidacy.

### 9. Depth context suggests distinct depth domains among the sequences

Depth summaries:
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/depth_summary_by_mainshock.csv`
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/depth_summary_m4_m5.csv`

At ±7 d:
- **M1**:
  - all-event median depth pre/post ≈ 12.0 / 11.6 km
  - M4+ median depth pre/post ≈ 13.7 / 12.2 km
  - relatively shallow and internally consistent.
- **M2**:
  - all-event median depth pre/post ≈ 22.2 / 18.9 km
  - M4+ post median depth ≈ 20.0 km
  - deeper and much broader depth spread (IQR ~20 km scale).
- **M3**:
  - detailed rows were not fully printed during inspection, but the saved tables provide full values and should be used directly in any integrated synthesis.

These summaries indicate that M1 is a shallower, tighter sequence than M2, while M2 occupies a broader and deeper depth domain. This supports the interpretation that M2 is less a compact local sequence and more a broad regional activation frame.

### 10. Mechanism and station context are available, but mechanism evidence is mainly contextual rather than discriminating among M1/M2/M3

Mechanism context:
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/mechanism_context_by_sequence.csv`
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/mechanism_match_summary.csv`

The mechanism summary reports, for each sequence frame:
- matched mechanism count = 354
- within-primary-tolerance count = 242
- median plane-1 strike/dip/rake = 188 / 26 / 79

However, the nearfield versus outer-band matched counts differ strongly:
- **M1**: nearfield mechanisms 39; outer-band 27
- **M2**: nearfield 27; outer-band 202
- **M3**: nearfield 8; outer-band 88

These counts are consistent with the broader-regional-activation interpretation: M2 and M3 are much more outer-band represented in the mechanism-matched subset than M1.

Station context:
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/station_context_summary.csv`

Coverage within 100 km:
- M1: 22 stations
- M2: 36 stations
- M3: 26 stations

All three have matched_true_fraction = 1.0 in the station summary, indicating the analysis did at least track observational context, though no direct detection-threshold correction is demonstrated in the output tables.

### 11. Robustness across windows preserves the main ranking, though some ratios are sensitive

Sensitivity figure:
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/window_radius_sensitivity_heatmaps.png`

Key patterns from the heatmaps:
- **M1** is the most robust:
  - dominance gap constant at 0.30 across windows and radii.
  - post/pre M4+ ratio stays near ~2.6–3.1.
- **M2** is the most sensitive in M4+ post/pre ratio:
  - undefined at short windows because pre M4+ = 0.
  - very strong radius sensitivity at 25 d.
  - dominance gap stable over time but radius-dependent.
- **M3** is intermediate:
  - dominance gap high at 7–14 d, then drops at 25 d for larger radii.
  - M4+ post/pre ratio is very high in short windows but declines strongly in larger windows/radii.

The optional robustness figure conveys the same ranking succinctly:
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/optional_window_robustness_comparison.png`

It shows:
- M1 and M2 dominance/companion metrics are stable across 7, 14, 25 days.
- M3 changes somewhat with the 25-day window, but still remains more mainshock-dominated than M1 or M2.

### 12. The script also produced an internal written diagnosis that can be compared against the tables

A text diagnosis exists:
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/aomori_mainshock_sequence_diagnosis.md`

For later integrated reporting, the CSV tables and the key figures above should be treated as the primary evidence base, with the markdown diagnosis used as a consistency check rather than as sole evidence.

## Limitations and Assumptions

1. **Catalog-only behavior diagnosis**
   The outputs explicitly caution that several interpretations are catalog-level only. In particular:
   - swarm-like organization does not prove a physical swarm pr
...[truncated]
</task_analysis>


## Evaluation Quality Summary
Use this evaluation metadata to disclose delivery status, scientific confidence, and important limitations in the final report.
<evaluation_quality>
{
  "delivery_status": "complete",
  "is_satisfactory": true,
  "limitations": [
    {
      "evidence": "Sequence diagnosis relies primarily on catalog-based matched-window metrics and morphology, without formal ETAS/Omori or alternative background-rate modeling.",
      "impact": "Supports comparative characterization but limits causal discrimination between aftershock decay, compound multi-event behavior, and broader regional triggering.",
      "severity": "medium",
      "type": "method_assumption"
    },
    {
      "evidence": "M3 is described as having only one M4+ pre-event in the ±7 d, ≤100 km window, yet receives a moderate foreshock/pre-mainshock activation score, implying dependence on broader-window evidence not fully summarized.",
      "impact": "Does not overturn the main interpretation, but some score justification is less transparent than for M1 and M2.",
      "severity": "low",
      "type": "consistency"
    },
    {
      "evidence": "The report explicitly notes overlap among mainshock-centered frames and broader regional activation, especially affecting M1 pre-activity and M2/M3 outer-band interpretations.",
      "impact": "Some pre/post contrasts and behavior scores may mix local sequence behavior with neighboring sequence activity.",
      "severity": "medium",
      "type": "uncertainty"
    },
    {
      "evidence": "Several short-window ratios are undefined or unstable when pre counts are zero, especially for M2 M4+ metrics.",
      "impact": "This weakens ratio-based comparisons for some dimensions but is acknowledged and does not invalidate the broader pattern.",
      "severity": "low",
      "type": "method_assumption"
    },
    {
      "evidence": "Mechanism context appears only weakly sequence-specific in the summary, with identical median strike/dip/rake values reported across M1–M3.",
      "impact": "Mechanism results provide contextual support but limited discriminating power for the final diagnosis.",
      "severity": "low",
      "type": "output_quality"
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
