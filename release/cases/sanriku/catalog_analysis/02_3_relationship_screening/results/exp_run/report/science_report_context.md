<science_report_context>

## Scientific Objective
<user_request>
You are an earthquake scientist and data-analysis agent.

Current task:
Investigate whether the M1, M2, and M3 earthquake clusters in the Aomori catalog show catalog-level relationships that are worth further scientific investigation.

Goal:
Use quantitative relationship analyses to evaluate whether these clusters are independent, weakly related, pairwise linked, part of a broader regional activation episode, or only apparently related because of burst-like background seismicity and analysis-window choices.

The purpose is not to prove triggering or a physical mechanism from the catalog alone.
The purpose is to identify which relationship hypotheses are supported, which are weak or unresolved, and which deserve follow-up with waveform, relocation, focal-mechanism, geodetic, ocean-bottom pressure, or stress-modeling analyses.

Data folder:
"<CASE_ROOT>/data"

Primary inputs:
- catalog/Snet_catalog_relocate_250930_260501.csv
- catalog/main_earthquake.csv

Context inputs:
- source_mechanism/Snet_mecha.csv
- stations/station.sta

Previous working conclusions:
- M1 is compact and near-field dominated, with weak single-mainshock dominance, strong pre-mainshock activation, and compound/swarm-like catalog organization.
- M2 shows the strongest post-mainshock activation jump, but much of its M4+/M5+ activity is distributed in the 30-100 km outer bands.
- M3 is the most strongly single-mainshock-dominated sequence, with substantial post-mainshock activation and fewer comparable companion events.
- These are catalog-level interpretations, not causal conclusions.

Core scientific question:
Do the M1, M2, and M3 clusters show meaningful catalog-level relationships, and if so, which relationship hypotheses should be prioritized for deeper physical analysis?

Candidate relationship hypotheses:
- independent local clusters
- overlapping activation zones
- delayed activation between clusters
- linked local fault-system activation
- corridor-like migration or expansion
- broader regional activation
- compound/swarm-like multi-event clustering
- apparent relationship caused by burst-like background seismicity or window choices

These are candidate hypotheses, not a closed list. The agent may propose additional relationship patterns if supported by the data.

Analysis principles:

1. Treat M1-M2, M1-M3, and M2-M3 symmetrically at first.
Evaluate all three pairwise relationships using comparable metrics before deciding which pair deserves focused interpretation.
Do not assume in advance that M1-M3, or any other pair, is the strongest relationship.

2. Use event-level relationship evidence.
For relevant M3+, M4+, M5+, and M6+ events, evaluate relative time, distance, azimuth, depth, distance band, nearest mainshock, and pairwise corridor position.

3. Preserve ambiguity.
Do not force every event into a single mainshock sequence.
Allow categories such as:
- uniquely associated with one cluster
- shared or overlapping
- corridor-like
- endpoint-centered
- outer-cluster
- regional/background
- unresolved

4. Use distance-aware interpretation.
Spatial distance is a primary evidence axis, not just background information.
For each pair, evaluate whether the epicentral separation, depth difference, and time separation are compatible with:
- local cluster linkage
- delayed activation between nearby source regions
- broader regional activation
- only regional-scale or apparent association.

Keep raw catalog evidence, control-corrected evidence, and distance-aware plausibility separate.
Do not rank a pair as high-priority based only on short time separation, raw post/pre ratio, or corridor fraction.
If raw evidence conflicts with control-corrected or distance-aware evidence, emphasize the corrected interpretation.

5. Let the agent design appropriate diagnostics.
Use standard earthquake-sequence and cluster-association methods where useful, such as:
- pairwise geometry and time separation
- intervening-event counts and rates
- M4+/M5+/M6+ event-chain analysis
- distance-time and projection analysis
- corridor versus off-corridor comparison
- nearest-mainshock and ambiguity-aware event assignment
- raw versus relationship-corrected sequence metrics
- simple background, random-window, or pseudo-corridor controls

Figures:
Generate a compact set of high-value diagnostic figures, not exhaustive plots.
Useful figure types may include:
- pairwise relationship overview map
- pairwise time-distance or corridor-projection plots
- M4+/M5+ intervening-event chain comparison
- event-association or ambiguity map
- corridor versus off-corridor comparison
- relationship hypothesis evidence matrix
- priority ranking for next physical verification

Design additional figures only if they directly clarify the relationship hypotheses.

Final report:
Provide a concise scientific report with:
- pairwise relationship evidence summary for M1-M2, M1-M3, and M2-M3
- relationship evidence matrix across all hypotheses
- evidence level for each pair-hypothesis combination: low, possible, moderate, or strong
- follow-up priority for each hypothesis: low, medium, or high
- strongest supported relationship signals
- weak, negative, or unresolved evidence
- separate raw catalog evidence, control-corrected evidence, and distance-aware plausibility for each pair
- recommended next research directions and required external data/modeling

Important:
Do not infer physical triggering from temporal order or spatial proximity alone.
Treat all relationship categories as catalog-level hypotheses.
Clearly separate raw mainshock-centered metrics from relationship-aware or corrected metrics.
Report both supporting and contradicting evidence.
Prioritize identifying promising scientific directions rather than forcing one causal story.
</user_request>

## Planned Workflow
<experiment_plan>
# Goal
Determine whether the Aomori M1, M2, and M3 clusters show catalog-level relationships worth further scientific investigation by evaluating all three pairs symmetrically, separating raw catalog evidence from control-corrected evidence and distance-aware plausibility, and prioritizing relationship hypotheses for follow-up with external data and physical analyses.

## Planning Assumptions
- Use observation data only. Core analysis must rely on `catalog/Snet_catalog_relocate_250930_260501.csv` and `catalog/main_earthquake.csv`; `source_mechanism/Snet_mecha.csv` and `stations/station.sta` are contextual follow-up screens only.
- The task is catalog-level only: no causal triggering or physical mechanism claims may be made from timing and location patterns alone.
- Pairwise analyses must start with identical definitions for M1-M2, M1-M3, and M2-M3 before any focused interpretation.
- Raw evidence, control-corrected evidence, and distance-aware plausibility must be computed and reported separately; disagreement between these layers must be preserved.
- Event assignment must be ambiguity-aware. Events may be uniquely associated, shared/overlapping, corridor-like, endpoint-centered, outer-cluster, regional/background, or unresolved.
- Distances must be retained in multiple forms: epicentral distance, depth difference, hypocentral-distance proxy if supported by depth quality, along-pair projection, and cross-corridor offset.
- Window choice is a stated scientific concern, so every main time-window-based metric must be paired with at least one temporal control; every corridor-based metric must be paired with at least one geometric control.
- One cohesive primary task script is preferred because ingestion, feature construction, pairwise metrics, controls, synthesis tables, and figures are tightly coupled; a second script is justified only for concise final report/table assembly from validated outputs.

## Analysis Plan

### Task 1: Build the unified relationship-analysis dataset and symmetric pairwise geometry
- Task description
  - Load the relocated catalog and mainshock table, standardize fields, derive all event-relative geometric and temporal features, and prepare a single analysis table usable for all pairwise, regional, and control tests.
- Required data sources
  - `catalog/Snet_catalog_relocate_250930_260501.csv`
  - `catalog/main_earthquake.csv`
  - Optional context joins from `source_mechanism/Snet_mecha.csv`
  - Optional station context from `stations/station.sta`
- Parameter selection strategy
  - Parse event and mainshock origin times to a consistent datetime standard and verify event ordering.
  - Remove exact duplicate rows if present; do not merge nearby but distinct earthquakes.
  - Treat only the three entries in `main_earthquake.csv` as anchor events M1, M2, and M3.
  - For each catalog event, compute:
    - relative time to each mainshock
    - epicentral distance to each mainshock
    - depth difference to each mainshock
    - nearest mainshock identity by epicentral distance
    - nearest versus second-nearest distance margin and ratio
    - optional hypocentral-distance proxy if depth is complete enough to use consistently
    - magnitude-threshold flags for M3+, M4+, M5+, M6+
  - For each pair (M1-M2, M1-M3, M2-M3), compute:
    - pair origin-time separation
    - pair epicentral separation
    - pair depth offset
    - pair azimuth
    - event along-pair projection
    - event cross-corridor offset
    - normalized endpoint position along the pair segment
    - event distance to pair midpoint
  - If direct event identifiers are absent for `Snet_mecha.csv`, join mechanisms by explicit time-location matching tolerance and record matched/unmatched status rather than forcing full linkage.
- Constraints
  - Use one consistent geodetic distance method for all epicentral distances.
  - Do not infer uncertainty or precision from decimal places.
  - Keep the full catalog span as the base dataset; pairwise/local subsets are derived from it, not preselected.
  - Mechanism and station data must not redefine the core pairwise relationship metrics.
- Key outputs
  - `relationship_event_features.csv`
  - `mainshock_pair_geometry.csv`
  - `catalog_qc_summary.csv`
  - `mechanism_match_summary.csv` if mechanism matching is attempted

### Task 2: Define ambiguity-aware event association classes and pair-centered spatial bands
- Task description
  - Assign descriptive relationship classes for each pair without forcing exclusive sequence membership, and define spatial neighborhoods needed for endpoint, overlap, corridor, and outer-band comparisons.
- Required data sources
  - Outputs from Task 1
  - `catalog/main_earthquake.csv`
- Parameter selection strategy
  - Apply the same association framework to all three pairs.
  - Define pairwise spatial components:
    - endpoint near-field zones around each mainshock
    - intermediate zones
    - outer bands
    - pair corridor segment between endpoints with modest endpoint extensions
    - side-band/off-corridor comparison zones with similar area where feasible
  - Use pair-scaled corridor width plus one narrower and one broader variant for stability checks; summarize sensitivity rather than treating this as a full sensitivity study.
  - Use explicit ambiguity rules combining:
    - nearest-mainshock distance margin or ratio
    - absolute distance to endpoints
    - corridor membership
    - endpoint-centered versus intervening position
  - Assign per-pair classes such as:
    - uniquely associated with endpoint A
    - uniquely associated with endpoint B
    - shared/overlapping
    - corridor-like
    - endpoint-centered but corridor-adjacent
    - outer-cluster
    - regional/background
    - unresolved
  - Export both all-event assignments and magnitude-threshold summaries for M3+, M4+, M5+, and M6+.
- Constraints
  - Categories must remain descriptive and non-causal.
  - Threshold changes must be tracked in a stability summary so no conclusion depends on one arbitrary corridor width or endpoint radius.
  - Do not force events into one sequence when geometry and timing conflict.
- Key outputs
  - `pairwise_event_assignment_M1_M2.csv`
  - `pairwise_event_assignment_M1_M3.csv`
  - `pairwise_event_assignment_M2_M3.csv`
  - `assignment_stability_summary.csv`

### Task 3: Compute symmetric raw pairwise relationship metrics and three-cluster regional diagnostics
- Task description
  - Quantify comparable raw evidence for M1-M2, M1-M3, and M2-M3 using event counts, rates, spatial distributions, intervening chains, and endpoint-versus-corridor contrasts, then place pairwise patterns in a broader three-cluster regional context.
- Required data sources
  - Outputs from Tasks 1–2
- Parameter selection strategy
  - For each pair and magnitude subset (all events, M3+, M4+, M5+, M6+ when sample size permits), compute:
    - counts and rates in matched pre- and post-mainshock windows around each endpoint
    - counts and rates in the between-mainshock interval
    - counts in endpoint near fields, overlap/shared regions, corridor, side bands, outer bands, and outside-pair regional areas
    - nearest-mainshock dominance and ambiguous-assignment fractions
    - endpoint balance metrics
    - corridor fraction and midpoint-centered fraction
    - depth-distribution summaries for endpoint, shared, corridor, and outer-band populations
    - first intervening event time and first M4+/M5+/M6+ intervening event time
    - ordered M4+/M5+/M6+ event-chain descriptors in time-distance space
    - monotonic or stepwise migration indicators along pair axes, reported descriptively if sparse
    - time-lagged activity changes near the opposite endpoint after each mainshock
  - Build regional diagnostics using all three anchors jointly:
    - nearest-mainshock partition of the catalog
    - proportion of moderate/large events not cleanly attributable to any single endpoint
    - regional outer-band activation through time
    - common-rate-pulse indicators showing simultaneous broad activity without clear pair-specific linkage
- Constraints
  - Use matched definitions across all three pairs before interpreting which pair is strongest.
  - Keep endpoint-local activation separate from corridor/intervening activation.
  - Do not rank a pair highly based on short time separation, post/pre ratio, or corridor fraction alone.
  - If M6+ counts are too sparse, keep them descriptive and do not over-weight them.
- Key outputs
  - `pairwise_raw_metrics.csv`
  - `pairwise_intervening_event_chains.csv`
  - `regional_activation_summary.csv`
  - `pairwise_raw_evidence_table.csv`

### Task 4: Apply temporal, geometric, and local-background controls to screen apparent relationships
- Task description
  - Test whether observed pairwise signals exceed expectations from burst-like background seismicity, arbitrary time windows, and generic regional geometry.
- Required data sources
  - Outputs from Tasks 1–3
  - Full relocated catalog from `catalog/Snet_catalog_relocate_250930_260501.csv`
- Parameter selection strategy
  - Implement at least three control families for each pair:
    - temporal controls:
      - random-window or shifted-window comparisons preserving observed window length and broad catalog context
    - geometric controls:
      - pseudo-corridors with preserved length and width but rotated and/or laterally shifted relative to the true pair axis
    - local-background controls:
      - side-band or annulus comparisons distinguishing true corridor or overlap enhancement from broad regional density
  - Where stable enough, add endpoint-label or time-shift checks for chain-like ordering metrics.
  - For each raw metric, compute:
    - control median or comparable baseline
    - observed-minus-control effect
    - percentile or empirical exceedance rank
    - standardized effect size where control spread is stable
  - Summarize whether each signal is:
    - raw-only
    - survives controls
    - strongly weakened by controls
    - unresolved because controls are unstable or sample sizes are too small
  - Track window and corridor sensitivity using a compact set of alternative settings rather than exhaustive sweeps.
- Constraints
  - Controls should preserve catalog burstiness structure as much as practical; naive independence assumptions are not acceptable.
  - Metrics that collapse under controls must remain visible and be downgraded in final interpretation.
  - Negative and null results must be explicitly retained.
- Key outputs
  - `pairwise_control_corrected_metrics.csv`
  - `control_test_summary.csv`
  - `robustness_summary.csv`
  - `artifact_flag_summary.csv`

### Task 5: Evaluate pair-hypothesis evidence with separate raw, corrected, and distance-aware layers
- Task description
  - Translate the measured metrics into hypothesis-oriented evidence statements for each pair without inferring causation, and identify which relationship hypotheses are supported, weak, contradictory, or unresolved.
- Required data sources
  - Outputs from Tasks 3–4
  - `mainshock_pair_geometry.csv`
  - Optional contextual mechanism summary from Task 1
- Parameter selection strategy
  - Evaluate at least the following hypotheses for each pair:
    - independent local clusters
    - overlapping activation zones
    - delayed activation between clusters
    - linked local fault-system activation
    - corridor-like migration or expansion
    - broader regional activation
    - compound/swarm-like multi-event clustering
    - apparent relationship caused by burst-like background seismicity or window choices
    - additional data-driven hypothesis if warranted, such as common regional rate pulse without pair-specific linkage
  - For each pair-hypothesis combination, score three separate evidence columns:
    - raw catalog evidence
    - control-corrected evidence
    - distance-aware plausibility
  - Convert each column to evidence level:
    - low
    - possible
    - moderate
    - strong
  - Distance-aware plausibility should explicitly consider:
    - pair separation scale
    - depth offset
    - timing separation
    - whether activity is localized at endpoints, concentrated in an intervening corridor, or spread mainly through broad outer bands
  - Integrate evidence into follow-up priority:
    - high when corrected support and distance-aware plausibility are at least moderate and external data could discriminate physical explanations
    - medium when support is possible to moderate but ambiguity remains substantial
    - low when evidence is weak, contradictory, or largely control-explained
  - Use focal mechanisms only as a follow-up discriminator:
    - summarize whether matched mechanisms in prioritized regions appear broadly compatible, mixed, or too sparse to judge
    - do not upgrade pair support solely because a few mechanisms are available
- Constraints
  - A pair may support more than one catalog-level hypothesis simultaneously.
  - Distance-aware plausibility must be allowed to downgrade raw temporal relationships.
  - Broader regional activation must be evaluated from both pairwise and all-three-cluster evidence, not from one pair alone.
- Key outputs
  - `pair_hypothesis_evidence_matrix.csv`
  - `pairwise_distance_aware_plausibility.csv`
  - `followup_priority_table.csv`
  - `strongest_signals_and_gaps.csv`

### Task 6: Produce compact diagnostic figures and concise synthesis products
- Task description
  - Generate the minimum figure set and final structured outputs needed to answer the scientific question and prioritize next analyses.
- Required data sources
  - Outputs from Tasks 1–5
  - Optional context from `source_mechanism/Snet_mecha.csv` and `stations/station.sta`
- Parameter selection strategy
  - Produce a compact, non-redundant figure set:
    - pairwise relationship overview map
      - M1/M2/M3 anchors, pair axes/corridors, event classes, and emphasis on M4+/M5+/M6+ events
    - three-panel pairwise time-distance or along-corridor projection plot
      - one panel per pair with event timing and location relative to endpoints
    - M4+/M5+/M6+ intervening-event chain comparison
      - ordered moderate/large events between and near endpoints
    - corridor versus off-corridor control comparison
      - observed versus pseudo-corridor or side-band enrichment by pair
    - relationship evidence matrix
      - pair-hypothesis combinations with separate raw, corrected, and distance-aware indicators
    - follow-up priority summary
      - which pair-hypothesis combinations justify waveform, relocation, mechanism, geodetic, OBP, or stress-modeling follow-up
  - Add only one optional figure if needed to resolve ambiguity:
    - nearest-mainshock ambiguity map
    - depth versus along-corridor plot
    - regional outer-band activation timeline
  - Assemble concise synthesis products requested by the user:
    - pairwise evidence summary for M1-M2, M1-M3, and M2-M3
    - relationship evidence matrix across hypotheses
    - strongest supported relationship signals
    - weak, negative, and unresolved evidence
    - explicit separation of raw, control-corrected, and distance-aware interpretation
    - recommended next research directions and required external data/modeling
  - Use station metadata only to comment on feasibility of follow-up observations in prioritized zones, not to alter relationship rankings.
- Constraints
  - Every figure must correspond to a specific hypothesis-discrimination or prioritization purpose.
  - Do not create exhaustive plot families or redundant panels.
  - Final synthesis must prioritize corrected and distance-aware evidence over raw co-activation alone.
- Key outputs
  - `fig_pairwise_overview_map`
  - `fig_pairwise_time_projection`
  - `fig_intervening_event_chains`
  - `fig_corridor_vs_control`
  - `fig_relationship_evidence_matrix`
  - `fig_followup_priority`
  - `pairwise_relationship_summary.csv`
  - `cluster_level_synthesis.csv`
  - `recommended_next_steps.csv`
  - Concise final scientific report with the requested pairwise summaries, evidence levels, and follow-up priorities
</experiment_plan>

## Implementation Trace
- Task: 01_relationship_analysis
  Description: Build the unified event-feature dataset, compute symmetric pairwise relationship metrics and controls, evaluate hypotheses, and generate compact diagnostic outputs for the Aomori M1-M2-M3 catalog analysis.
  Ancestors: none
  Handoff JSON: <CASE_ROOT>/run/02_3_relationship_screening/exp_run/log/coding_progress/task_handoff/01_relationship_analysis.json
  Output directory: <CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/01_relationship_analysis
  Analysis file: <CASE_ROOT>/run/02_3_relationship_screening/exp_run/analysis/01_relationship_analysis.md
- Task: 02_report_synthesis
  Description: Assemble the final concise scientific report from validated relationship-analysis outputs without recomputing core metrics.
  Ancestors: 01_relationship_analysis
  Handoff JSON: <CASE_ROOT>/run/02_3_relationship_screening/exp_run/log/coding_progress/task_handoff/02_report_synthesis.json
  Output directory: <CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/02_report_synthesis
  Analysis file: <CASE_ROOT>/run/02_3_relationship_screening/exp_run/analysis/02_report_synthesis.md

## Result Evidence Index
Use handoff JSON files as compact indexes to important outputs. Use per-task analyses for scientific interpretation. Inspect raw outputs only when the handoff and analysis are insufficient.
<task_evidence task="01_relationship_analysis">
Handoff JSON: <CASE_ROOT>/run/02_3_relationship_screening/exp_run/log/coding_progress/task_handoff/01_relationship_analysis.json
{
  "meta": {
    "schema_version": 2,
    "type": "coding_task_handoff",
    "task": "01_relationship_analysis",
    "generated_at": "2026-05-24T06:05:00.543374+00:00"
  },
  "status": {
    "state": "success",
    "stage": "analysis_done",
    "elapsed_sec": 616.019,
    "timing": {
      "total_sec": 616.019,
      "coding_agent_sec": 236.096,
      "code_review_sec": 20.315,
      "preflight_sec": 2.146,
      "script_execution_sec": 121.488,
      "result_check_sec": 86.095,
      "task_analysis_sec": 146.243
    },
    "quality_flags": [
      "task_status:success",
      "outputs_truncated"
    ]
  },
  "paths": {
    "root": "<CASE_ROOT>/run/02_3_relationship_screening",
    "script": "<CASE_ROOT>/run/02_3_relationship_screening/exp_run/scripts/01_relationship_analysis.py",
    "output_dir": "<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/01_relationship_analysis",
    "analysis": "<CASE_ROOT>/run/02_3_relationship_screening/exp_run/analysis/01_relationship_analysis.md",
    "log": "<CASE_ROOT>/run/02_3_relationship_screening/exp_run/log/task/01_relationship_analysis/log_3.txt"
  },
  "outputs": {
    "primary": [
      {
        "path": "artifact_flag_summary.csv",
        "absolute_path": "<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/01_relationship_analysis/artifact_flag_summary.csv",
        "kind": "machine_readable"
      },
      {
        "path": "assignment_stability_summary.csv",
        "absolute_path": "<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/01_relationship_analysis/assignment_stability_summary.csv",
        "kind": "machine_readable"
      },
      {
        "path": "catalog_qc_summary.csv",
        "absolute_path": "<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/01_relationship_analysis/catalog_qc_summary.csv",
        "kind": "machine_readable"
      },
      {
        "path": "cluster_level_synthesis.csv",
        "absolute_path": "<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/01_relationship_analysis/cluster_level_synthesis.csv",
        "kind": "machine_readable"
      },
      {
        "path": "control_test_summary.csv",
        "absolute_path": "<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/01_relationship_analysis/control_test_summary.csv",
        "kind": "machine_readable"
      },
      {
        "path": "followup_priority_table.csv",
        "absolute_path": "<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/01_relationship_analysis/followup_priority_table.csv",
        "kind": "machine_readable"
      },
      {
        "path": "mainshock_pair_geometry.csv",
        "absolute_path": "<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/01_relationship_analysis/mainshock_pair_geometry.csv",
        "kind": "machine_readable"
      },
      {
        "path": "mechanism_match_summary.csv",
        "absolute_path": "<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/01_relationship_analysis/mechanism_match_summary.csv",
        "kind": "machine_readable"
      }
    ],
    "all": [
      "artifact_flag_summary.csv",
      "assignment_stability_summary.csv",
      "catalog_qc_summary.csv",
      "cluster_level_synthesis.csv",
      "control_test_summary.csv",
      "fig_corridor_vs_control.png",
      "fig_followup_priority.png",
      "fig_intervening_event_chains.png",
      "fig_pairwise_overview_map.png",
      "fig_pairwise_time_projection.png",
      "fig_relationship_evidence_matrix.png",
      "followup_priority_table.csv",
      "mainshock_pair_geometry.csv",
      "mechanism_match_summary.csv",
      "pair_hypothesis_evidence_matrix.csv",
      "pairwise_control_corrected_metrics.csv",
      "pairwise_distance_aware_plausibility.csv",
      "pairwise_event_assignment_M1_M2.csv",
      "pairwise_event_assignment_M1_M3.csv",
      "pairwise_event_assignment_M2_M3.csv",
      "pairwise_intervening_event_chains.csv",
      "pairwise_raw_evidence_table.csv",
      "pairwise_raw_metrics.csv",
      "pairwise_relationship_summary.csv",
      "recommended_next_steps.csv",
      "regional_activation_summary.csv",
      "regional_outer_band_timeline.csv",
      "relationship_event_features.csv",
      "robustness_summary.csv",
      "strongest_signals_and_gaps.csv"
    ],
    "truncated": true
  },
  "notes": {
    "purpose": "Build the unified event-feature dataset, compute symmetric pairwise relationship metrics and controls, evaluate hypotheses, and generate compact diagnostic outputs for the Aomori M1-M2-M3 catalog analysis.",
    "result": "Build the unified event-feature dataset, compute symmetric pairwise relationship metrics and controls, evaluate hypotheses, and generate compact diagnostic outputs for the Aomori M...[truncated] Status=success; outputs=30 discovered; primary=8.",
    "warnings": [],
    "assumptions": [],
    "limitations": []
  }
}
</task_evidence>

<task_evidence task="02_report_synthesis">
Handoff JSON: <CASE_ROOT>/run/02_3_relationship_screening/exp_run/log/coding_progress/task_handoff/02_report_synthesis.json
{
  "meta": {
    "schema_version": 2,
    "type": "coding_task_handoff",
    "task": "02_report_synthesis",
    "generated_at": "2026-05-24T06:05:00.549899+00:00"
  },
  "status": {
    "state": "success",
    "stage": "analysis_done",
    "elapsed_sec": 320.341,
    "timing": {
      "total_sec": 320.341,
      "coding_agent_sec": 125.551,
      "code_review_sec": 29.388,
      "preflight_sec": 0.784,
      "script_execution_sec": 41.204,
      "result_check_sec": 22.709,
      "task_analysis_sec": 97.836
    },
    "quality_flags": [
      "task_status:success"
    ]
  },
  "paths": {
    "root": "<CASE_ROOT>/run/02_3_relationship_screening",
    "script": "<CASE_ROOT>/run/02_3_relationship_screening/exp_run/scripts/02_report_synthesis.py",
    "output_dir": "<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/02_report_synthesis",
    "analysis": "<CASE_ROOT>/run/02_3_relationship_screening/exp_run/analysis/02_report_synthesis.md",
    "log": "<CASE_ROOT>/run/02_3_relationship_screening/exp_run/log/task/02_report_synthesis/log_1.txt"
  },
  "outputs": {
    "primary": [
      {
        "path": "followup_priorities_concise.csv",
        "absolute_path": "<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/02_report_synthesis/followup_priorities_concise.csv",
        "kind": "machine_readable"
      },
      {
        "path": "pairwise_scientific_summary.csv",
        "absolute_path": "<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/02_report_synthesis/pairwise_scientific_summary.csv",
        "kind": "machine_readable"
      },
      {
        "path": "raw_corrected_distance_summary.csv",
        "absolute_path": "<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/02_report_synthesis/raw_corrected_distance_summary.csv",
        "kind": "machine_readable"
      },
      {
        "path": "recommended_next_steps_ranked.csv",
        "absolute_path": "<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/02_report_synthesis/recommended_next_steps_ranked.csv",
        "kind": "machine_readable"
      },
      {
        "path": "relationship_evidence_matrix_concise.csv",
        "absolute_path": "<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/02_report_synthesis/relationship_evidence_matrix_concise.csv",
        "kind": "machine_readable"
      },
      {
        "path": "report_manifest.csv",
        "absolute_path": "<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/02_report_synthesis/report_manifest.csv",
        "kind": "machine_readable"
      },
      {
        "path": "strongest_supported_signals.csv",
        "absolute_path": "<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/02_report_synthesis/strongest_supported_signals.csv",
        "kind": "machine_readable"
      },
      {
        "path": "weak_negative_unresolved_signals.csv",
        "absolute_path": "<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/02_report_synthesis/weak_negative_unresolved_signals.csv",
        "kind": "machine_readable"
      }
    ],
    "all": [
      "executive_summary.txt",
      "fig_corridor_vs_control.png",
      "fig_followup_priority.png",
      "fig_intervening_event_chains.png",
      "fig_pairwise_overview_map.png",
      "fig_pairwise_time_projection.png",
      "fig_relationship_evidence_matrix.png",
      "final_scientific_report.md",
      "followup_priorities_concise.csv",
      "pairwise_scientific_summary.csv",
      "raw_corrected_distance_summary.csv",
      "recommended_next_steps_ranked.csv",
      "relationship_evidence_matrix_concise.csv",
      "report_manifest.csv",
      "strongest_supported_signals.csv",
      "weak_negative_unresolved_signals.csv"
    ],
    "truncated": false
  },
  "notes": {
    "purpose": "Assemble the final concise scientific report from validated relationship-analysis outputs without recomputing core metrics.",
    "result": "Assemble the final concise scientific report from validated relationship-analysis outputs without recomputing core metrics. Status=success; outputs=16 discovered; primary=8.",
    "warnings": [],
    "assumptions": [],
    "limitations": []
  }
}
</task_evidence>


## Per-Task Scientific Analyses
<task_analysis>
Task: 01_relationship_analysis
Description: Build the unified event-feature dataset, compute symmetric pairwise relationship metrics and controls, evaluate hypotheses, and generate compact diagnostic outputs for the Aomori M1-M2-M3 catalog analysis.
Analysis file: <CASE_ROOT>/run/02_3_relationship_screening/exp_run/analysis/01_relationship_analysis.md
Output directory: <CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/01_relationship_analysis

## Scientific Purpose

This task evaluated whether the three catalog-defined earthquake clusters M1, M2, and M3 in the Aomori catalog show pairwise or regional relationships that are scientifically worth deeper follow-up, while explicitly avoiding causal claims from catalog data alone.

The implemented analysis was designed to separate:
- raw catalog co-activity,
- control-corrected relationship signals,
- and distance-aware plausibility,

for the three pairings:
- M1-M2,
- M1-M3,
- M2-M3.

The central scientific aim was to determine which hypotheses are supported at the catalog level, which are weak, and which should be prioritized for relocation, waveform, focal-mechanism, geodetic, ocean-bottom pressure, or stress-modeling follow-up. The main output files supporting this purpose are:
- `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/01_relationship_analysis/pair_hypothesis_evidence_matrix.csv`
- `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/01_relationship_analysis/pairwise_relationship_summary.csv`
- `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/01_relationship_analysis/pairwise_control_corrected_metrics.csv`
- `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/01_relationship_analysis/pairwise_distance_aware_plausibility.csv`
- `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/01_relationship_analysis/cluster_level_synthesis.csv`

## Method and Implementation Evidence

The task successfully built a unified catalog-level relationship dataset and summarized it into symmetric pairwise diagnostics, controls, and hypothesis scoring. Success state and output inventory are documented in:
- `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/log/coding_progress/task_handoff/01_relationship_analysis.json`

Catalog scale and supporting context were quantified in:
- `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/01_relationship_analysis/catalog_qc_summary.csv`

Key catalog facts from that file:
- 22,096 relocated catalog events
- catalog span from 2025-09-30 to 2026-05-01
- 259 M4+ events
- 68 M5+ events
- 3 mainshocks
- 354 mechanism rows, with 240 conservative time-space matches

Mainshock geometry was quantified explicitly in:
- `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/01_relationship_analysis/mainshock_pair_geometry.csv`

Key pair geometries:
- M1-M2: 202.59 km separation, 37.6 km depth difference, 29.26 day time separation
- M1-M3: 57.38 km separation, 3.5 km depth difference, 161.99 day time separation
- M2-M3: 145.22 km separation, 34.1 km depth difference, 132.73 day time separation

These geometry values matter because the analysis deliberately separated apparent raw linkage from what is physically more plausible at pair scale.

The implementation included:
- event-feature construction for pairwise assignments and corridor position:
  - `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/01_relationship_analysis/relationship_event_features.csv`
- ambiguity-aware pairwise event assignment:
  - `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/01_relationship_analysis/pairwise_event_assignment_M1_M2.csv`
  - `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/01_relationship_analysis/pairwise_event_assignment_M1_M3.csv`
  - `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/01_relationship_analysis/pairwise_event_assignment_M2_M3.csv`
- raw relationship metrics:
  - `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/01_relationship_analysis/pairwise_raw_metrics.csv`
  - `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/01_relationship_analysis/pairwise_raw_evidence_table.csv`
- control tests and pseudo-corridor comparisons:
  - `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/01_relationship_analysis/control_test_summary.csv`
  - `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/01_relationship_analysis/pairwise_control_corrected_metrics.csv`
  - `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/01_relationship_analysis/robustness_summary.csv`
- distance-aware plausibility scoring:
  - `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/01_relationship_analysis/pairwise_distance_aware_plausibility.csv`
- final pair-hypothesis synthesis and follow-up ranking:
  - `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/01_relationship_analysis/pair_hypothesis_evidence_matrix.csv`
  - `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/01_relationship_analysis/followup_priority_table.csv`
  - `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/01_relationship_analysis/recommended_next_steps.csv`

The principal report figures are:
- `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/01_relationship_analysis/fig_pairwise_overview_map.png`
- `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/01_relationship_analysis/fig_pairwise_time_projection.png`
- `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/01_relationship_analysis/fig_intervening_event_chains.png`
- `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/01_relationship_analysis/fig_corridor_vs_control.png`
- `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/01_relationship_analysis/fig_relationship_evidence_matrix.png`
- `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/01_relationship_analysis/fig_followup_priority.png`

## Key Results and Evidence Files

### 1. Overall system-level conclusion: broader regional activation is the most robust cross-pair explanation

The most consistent hypothesis across all three pairs is broader regional activation, with supporting but secondary evidence for a common regional rate pulse. This conclusion is clearest in:
- `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/01_relationship_analysis/pair_hypothesis_evidence_matrix.csv`
- `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/01_relationship_analysis/strongest_signals_and_gaps.csv`
- `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/01_relationship_analysis/fig_relationship_evidence_matrix.png`

Evidence matrix summary:
- M1-M2 broader regional activation: raw strong, corrected strong, distance-aware strong
- M1-M3 broader regional activation: raw strong, corrected strong, distance-aware moderate
- M2-M3 broader regional activation: raw strong, corrected moderate, distance-aware strong

Common regional rate pulse is also supported:
- M1-M2: moderate / moderate / strong
- M1-M3: moderate / possible / moderate
- M2-M3: strong / moderate / strong

The evidence matrix figure shows that regional-scale explanations survive control correction more consistently than local linkage hypotheses. This is the clearest positive result of the task.

Additional regional context comes from:
- `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/01_relationship_analysis/regional_activation_summary.csv`

That file shows large monthly outer-band fractions:
- 0.87 in 2025-11
- 0.79 in 2025-12
- 0.85 in 2026-04
- 0.88 in 2026-05

This supports the interpretation that much of the catalog activity occurred outside narrowly pair-centered local zones, consistent with a broader regional activation episode rather than one compact linked sequence.

### 2. M1-M3 is the strongest raw local-pair relationship, but its interpretation weakens after control correction and distance-aware filtering

Among the three pairs, M1-M3 shows the broadest raw support for local interaction-style hypotheses:
- overlapping activation zones: raw strong
- delayed activation: raw strong
- linked local fault-system activation: raw strong
- corridor-like migration/expansion: raw strong
- broader regional activation: raw strong

Evidence files:
- `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/01_relationship_analysis/pair_hypothesis_evidence_matrix.csv`
- `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/01_relationship_analysis/cluster_level_synthesis.csv`
- `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/01_relationship_analysis/strongest_signals_and_gaps.csv`

However, the corrected and distance-aware interpretation is more cautious:
- overlapping activation zones: corrected moderate, distance-aware moderate
- delayed activation: corrected moderate, distance-aware possible
- linked local fault-system activation: corrected strong, distance-aware moderate
- corridor-like migration/expansion: corrected strong, distance-aware moderate
- independent local clusters: corrected low

Geometry helps explain this mixed result:
- only 57.38 km separation
- only 3.5 km depth difference
- but 161.99 day time separation
from `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/01_relationship_analysis/mainshock_pair_geometry.csv`

The overview map supports M1-M3 as the most spatially plausible local pair:
- shortest separation
- embedded in the same southeastern concentration
- strongest apparent local overlap
from `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/01_relationship_analysis/fig_pairwise_overview_map.png`

The time-projection figure supports recurrent endpoint occupancy rather than clean migration:
- two-end occupation through time
- broad central scatter
- no monotonic propagation
from `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/01_relationship_analysis/fig_pairwise_time_projection.png`

Control comparison still shows corridor enrichment for M1-M3:
- observed M4+ corridor count about 92
- pseudo-corridor median about 56-57
from `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/01_relationship_analysis/fig_corridor_vs_control.png`

In the robustness table for M1-M3 M4+:
- observed corridor count 92
- observed sideband count 25
- pseudo-corridor median 56.5
- geometric corridor effect 35.5
from `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/01_relationship_analysis/robustness_summary.csv`

But ambiguity is substantial:
- M1-M3 ambiguous fraction is 0.5097 for M4+
- 0.5882 for M5+
- 0.5385 for M6+
from `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/01_relationship_analysis/regional_activation_summary.csv`

Interpretation: M1-M3 is the best candidate for local or structural follow-up, but the catalog evidence does not isolate a simple direct pairwise link. It is best framed as possible overlap / linked-fault / corridor behavior embedded within broader regional activation.

### 3. M2-M3 is best explained as either independent local clusters or shared regional forcing, not a strong direct local linkage

M2-M3 stands out because its strongest supported pair-level hypothesis is independent local clusters:
- raw strong
- corrected strong
- distance-aware strong

It also supports:
- broader regional activation: strong / moderate / strong
- common regional rate pulse: strong / moderate / strong
- apparent relationship from background/window choices: moderate / moderate / strong

Evidence files:
- `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/01_relationship_analysis/pair_hypothesis_evidence_matrix.csv`
- `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/01_relationship_analysis/artifact_flag_summary.csv`
- `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/01_relationship_analysis/strongest_signals_and_gaps.csv`

By contrast, local pairwise linkage hypotheses are weak:
- overlap: low / low / low
- delayed activation: low / low / low
- linked local fault system: possible / low / low
- corridor migration: possible / possible / low
- compound/swarm-like: low / low / low

Geometry is unfavorable for simple local linkage:
- 145.22 km separation
- 34.1 km depth difference
- 132.73 day time separation
from `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/01_relationship_analysis/mainshock_pair_geometry.csv`

The map supports this interpretation:
- M2 is in the northwestern concentration
- M3 is in a separate southeastern area
- the connection is more diffuse than M1-M3
from `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/01_relationship_analysis/fig_pairwise_overview_map.png`

The time-projection figure shows:
- strong endpoint clustering on both ends
- intermittent corridor occupancy
- no smooth directional migration
from `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/01_relationship_analysis/fig_pairwise_time_projection.png`

The corridor-control figure shows almost no M4+ corridor excess for M2-M3:
- observed corridor about 26
- pseudo-corridor median about 24
from `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/01_relationship_analysis/fig_corridor_vs_control.png`

This near-parity is important because it indicates that much of the apparent corridor occupancy can be reproduced by geometric control alone. Combined with the artifact score and the strong independent-cluster score, M2-M3 should not be prioritized as a direct linkage pair from catalog evidence alone.

### 4. M1-M2 shows strong raw corridor and regional signals, but distance-aware plausibility argues against a simple local pair linkage

M1-M2 shows strong raw and corrected support for:
- corridor-like migration/expansion: strong / strong / low
- broader regional activation: strong / strong / strong
and moderate support for:
- linked local fault-system activation: moderate / moderate / low
- common regional rate pulse: moderate / moderate / strong
- independent local clusters: moderate / possible / strong

Evidence files:
- `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/01_relationship_analysis/pair_hypothesis_evidence_matrix.csv`
- `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/01_relationship_analysis/cluster_level_synthesis.csv`

The major contradiction is that local linkage-style interpretations collapse in the distance-aware panel. This is because M1-M2 is the longest pair:
- 202.59 km separation
- 37.6 km depth difference
- only 29.26 days apart
from `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/01_relationship_analysis/mainshock_pair_geometry.csv`

Distance-aware scoring for the pair is correspondingly poor for local linkage:
- distance link score 0.000
from `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/01_relationship_analysis/pairwise_distance_aware_plausibility.csv`

The raw corridor signal is still large. In the M4+ corridor-control comparison:
- observed corridor about 155
- pseudo-corridor median about 63
the largest enrichment of the three pairs
from `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/01_relationship_analysis/fig_corridor_vs_control.png`

The robustness table reinforces this:
- M1-M2 M4+ observed corridor count 155
- observed sideband count 55
- geometric corridor effect 92
- corridor vs sideband control ratio 2.403
from `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/01_relationship_analysis/robustness_summary.csv`

However, the map shows that this long connection largely spans two endpoint clusters with only a thinner bridge near M3 rather than a compact direct local zone:
- M2 northwestern cluster
- M1 southeastern cluster
- weaker central bridge
from `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/01_relationship_analysis/fig_pairwise_overview_map.png`

The time-projection figure similarly suggests:
- endpoint clustering
- diffuse interior occupancy
- no clear monotonic migration
from `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/01_relationship_analysis/fig_pairwise_time_projection.png`

Interpretation: M1-M2 has strong raw corridor-style activity, but the corrected interpretation is not “direct linked local pair.” The better catalog-level reading is broad regional activation with a strong pairwise corridor occupancy signal that is not spatially plausible as a simple local interaction over 202 km.

### 5. Intervening-event chains argue against simple direct mainshock-to-mainshock linkage for all three pairs

The intervening-event chain figure shows that all pairs contain many M4+ events between paired mainshocks, with much fewer M5+ and very few M6+ events:
- M1-M2: about 56 intervening M4+, 19 M5+, 4 M6+
- M1-M3: about 86 intervening M4+, 24 M5+, 5 M6+
- M2-M3: about 67 intervening M4+, 15 M5+, 7 M6+
from `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/01_relationship_analysis/fig_intervening_event_chains.png`

This means no pair is isolated from distributed background or regional activity. The chain complexity is greatest for M1-M3, intermediate for M2-M3, and lowest for M1-M2, but even the least crowded pair is not a clean two-event link.

This conclusion is also consistent with:
- `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/01_relationship_analysis/pairwise_intervening_event_chains.csv`

### 6. Event assignment ambiguity is high for M1-M3, moderate for M1-M2, and low for M2-M3

Ambiguity-aware assignment is a major result because it shows whether events fall naturally into one mainshock neighborhood or remain shared/unresolved.

Evidence:
- `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/01_relationship_analysis/assignment_stability_summary.csv`
- `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/01_relationship_analysis/regional_activation_summary.csv`

Assignment stability:
- M1-M3 stable fraction 1.000 with narrow/base widths identical, indicating robust classification under that geometry, but this stability includes a very large shared/overlap category rather than unique separation
- M2-M3 stable fraction 0.966
- M1-M2 stable fraction 0.780, the most sensitive to corridor width choices

Ambiguous/highly shared fractions for higher magnitudes:
- M1-M3 ambiguous fraction: 0.510 at M4+, 0.588 at M5+, 0.538 at M6+
- M1-M2 ambiguous fraction: 0.270 at M4+, 0.250 at M5+, 0.231 at M6+
- M2-M3 ambiguous fraction: 0.062 at M4+, 0.088 at M5+, 0.000 at M6+

Interpretation:
- M1-M3 looks genuinely overlapping in catalog space
- M2-M3 looks much more separable, supporting the independent-local-cluster interpretation
- M1-M2 is intermediate but somewhat unstable to window/width choices

### 7. Mechanism information is present but limited as a discriminant at this task stage

Mechanism matching summary:
- 354 mechanism rows
- 247 time matches
- 240 conservative matches
- conservative match fraction 0.678
- median space mismatch for time matches about 0.08 km
from `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/01_relationship_analysis/mechanism_match_summary.csv`

This confirms mechanism information exists and can support later follow-up, but the current task outputs do not provide a strong pair-diagnostic mechanism contrast by themselves. Mechanisms therefore serve more as a next-step resource than as a decisive result here.

### 8. Follow-up priorities favor regional analyses overall, with M1-M3 as the main local-structure candidate

The follow-up table and figure rank the pair-hypothesis combinations most worth physical verification:
- `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/01_relationship_analysis/followup_priority_table.csv`
- `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/01_relationship_analysis/recommended_next_steps.csv`
- `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/01_relationship_analysis/fig_followup_priority.png`

High-priority combinations include:
- M1-M2 broader regional activation
- M1-M2 common regional rate pulse
- M1-M3 overlapping activation zones
- M1-M3 linked local fault-system activation
- M1-M3 corridor-like migration or expansion
- M1-M3 broader regional activation
- M2-M3 independent local clusters
- M2-M3 broader regional activation
- M2-M3 apparent relationship from background/window choices
- M2-M3 common regional rate pulse

The next-step recommendations are scientifically coherent:
- regional rate modeling, geodesy, OBP, stress-field comparison for regional hypotheses
- relocation refinement, waveform cross-correlation, and focal-mechanism comparison for M1-M3 overlap/linked-fault hypotheses
- expansion of control tests and alternative windows for M2-M3 artifact evaluation

One caution: the follow-up figure is ordinal, not quantitative within tier, so it should be read as categorical prioritization rather than strict ranking magnitude.

## Limitations and Assumptions

- The task handoff marks `outputs_truncated`, so the handoff summary itself is not a complete record; direct file inspection was necessary.
- No PDF outputs were listed or provided for this task, so no PDF-specific analysis was applicable.
- The results are explicitly catalog-level. They do not demonstrate triggering, stress transfer, fluid migration, or any physical mechanism.
- Distance-aware plausibility is a screening layer, not a physical model. It usefully downweights implausible local-link interpretations but does not prove regional forcing.
- Some pairwise interpretations are sensitive to ambiguity and window choice:
  - M1-M2 has the lowest assignment stability (stable fraction 0.780)
  - M2-M3 has a moderate artifact/background score
- M1-M3 has strong raw relationship signals but also very high ambiguous/shared fractions, so apparent pairwise linkage may partly reflect a broader shared activation zone.
- M2-M3 follow-up labeling contains a semantic mismatch: the table marks `independent_local_clusters` as high follow-up but the text says “Low priority; only revisit after improved relocations and background-rate modeling.” This should be checked before final synthesis:
  - `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/01_relationship_analysis/followup_priority_table.csv`
- The corridor-control comparisons are informative but do not by themselves distinguish structural linkage from regional clustering aligned with pair geometry.
- Intervening-event-chain plots indicate distributed activity, but they do not encode full spatiotemporal causality.
- Mechanism information is available but not fully exploited in the current task outputs for pair discrimination.

## Report-Ready Summary

This task successfully quantified catalog-level relationships among the Aomori M1, M2, and M3 clusters using symmetric pairwise metrics, ambiguity-aware event assignment, corridor and pseudo-corridor controls, and distance-aware plausibility screening. The strongest robust result is that the three clusters are best viewed as components of a broader regional activation episode rather than as a set of uniformly direct pairwise links. This conclusion is supported by the cross-pair hypothesis synthesis in `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/01_relationship_analysis/pair_hypothesis_evidence_matrix.csv`, the summary heatmap `<CASE_ROOT>/run/02_step2.6b_seque
...[truncated]
</task_analysis>

<task_analysis>
Task: 02_report_synthesis
Description: Assemble the final concise scientific report from validated relationship-analysis outputs without recomputing core metrics.
Analysis file: <CASE_ROOT>/run/02_3_relationship_screening/exp_run/analysis/02_report_synthesis.md
Output directory: <CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/02_report_synthesis

## Scientific Purpose
This task synthesized previously validated catalog-relationship analyses for the Aomori M1, M2, and M3 earthquake clusters into a compact scientific report, without recomputing core metrics. The scientific goal was to determine which catalog-level relationship hypotheses are supported, which are weakened after controls or distance-aware screening, and which pair–hypothesis combinations merit higher-priority physical follow-up.

The synthesis explicitly separates:
- raw catalog relationship signals,
- control-corrected signals, and
- distance-aware plausibility,

so that temporal coincidence or corridor occupancy alone is not over-interpreted as local linkage or triggering.

## Method and Implementation Evidence
The report synthesis assembled validated quantitative outputs from the upstream relationship-analysis stage into machine-readable tables, a narrative report, and compact diagnostic figures. The implementation evidence shows that this task did not recompute sequence metrics, but consolidated them into pairwise and hypothesis-level summaries.

Key output products confirm this structure:
- Pairwise summary table with separation, depth offset, time separation, between-event counts, corridor fractions, and control metrics: `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/02_report_synthesis/pairwise_scientific_summary.csv`
- Condensed raw / corrected / distance-aware screen table: `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/02_report_synthesis/raw_corrected_distance_summary.csv`
- Hypothesis-by-pair evidence matrix: `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/02_report_synthesis/relationship_evidence_matrix_concise.csv`
- Ranked strongest supported signals: `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/02_report_synthesis/strongest_supported_signals.csv`
- Weak / negative / unresolved signals: `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/02_report_synthesis/weak_negative_unresolved_signals.csv`
- Follow-up priority tables: `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/02_report_synthesis/followup_priorities_concise.csv` and `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/02_report_synthesis/recommended_next_steps_ranked.csv`
- Final narrative report and summary text: `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/02_report_synthesis/final_scientific_report.md` and `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/02_report_synthesis/executive_summary.txt`

The figure set is compact and high-value, matching the requested report-oriented design:
- spatial overview map,
- time-projection relationship plots,
- corridor-versus-control comparison,
- intervening-event chain comparison,
- evidence matrix,
- follow-up priority ranking.

## Key Results and Evidence Files
### 1. The synthesis does not support a single common relationship model for all three pairs
The executive synthesis states that the three pairwise relationships are not explained by one uniform story, and that M1-M3 stands out as the best candidate for further physical testing, while M1-M2 and M2-M3 are better framed as regional-episode candidates than simple local pair linkages.

Evidence:
- `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/02_report_synthesis/executive_summary.txt`
- `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/02_report_synthesis/final_scientific_report.md`

Supporting figure:
- `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/02_report_synthesis/fig_relationship_evidence_matrix.png`

The evidence matrix shows strong pair dependence:
- M1-M3 retains moderate support across several local-linkage-style hypotheses after controls and under distance plausibility.
- M1-M2 and M2-M3 retain stronger support for broader regional activation and common regional rate pulse explanations than for local direct linkage.

### 2. M1-M3 is the clearest pair for deeper physical follow-up
This is the strongest positive synthesis result. M1-M3 is the only pair that is both spatially nearby enough to remain plausible for local linkage and still retains several nontrivial hypotheses after control correction.

Quantitative evidence from `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/02_report_synthesis/pairwise_scientific_summary.csv` and `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/02_report_synthesis/raw_corrected_distance_summary.csv`:
- pair separation: 57.4 km
- depth difference: 3.5 km
- time separation: 162.0 days
- raw signal level: high
- control screen: partly_weakened
- distance plausibility: nearby_plausible
- distance_link_score: 0.681
- M4+ between count: 188
- M4+ corridor fraction: 0.358
- pseudo-corridor percentile: 0.975

Hypothesis-level evidence from `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/02_report_synthesis/relationship_evidence_matrix_concise.csv`:
- overlapping activation zones: raw strong, corrected moderate, distance moderate
- delayed activation between clusters: raw strong, corrected moderate, distance possible
- linked local fault-system activation: raw strong, corrected strong, distance moderate
- corridor-like migration/expansion: raw strong, corrected strong, distance moderate
- broader regional activation: raw strong, corrected strong, distance moderate

High-priority follow-up recommendations emphasize M1-M3 local-relationship hypotheses:
- overlap,
- linked fault-system activation,
- corridor-like migration/expansion,
- regional activation context.

Evidence:
- `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/02_report_synthesis/fig_followup_priority.png`
- `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/02_report_synthesis/recommended_next_steps_ranked.csv`
- `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/02_report_synthesis/strongest_supported_signals.csv`

Figure support:
- `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/02_report_synthesis/fig_pairwise_overview_map.png`
- `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/02_report_synthesis/fig_pairwise_time_projection.png`
- `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/02_report_synthesis/fig_intervening_event_chains.png`

The time-projection figure shows episodic endpoint-centered, corridor-aligned activity rather than clean continuous migration; for M1-M3 this supports delayed or stepwise activation more than a simple migrating front.

### 3. M1-M2 has strong raw and corrected catalog linkage signals, but these are not distance-plausible as a simple local pair linkage
This pair shows a major contrast between raw/control metrics and distance-aware interpretation, which is scientifically important.

Quantitative evidence from `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/02_report_synthesis/raw_corrected_distance_summary.csv`:
- raw signal level: high
- control screen: survives_controls
- distance plausibility: not_local_linkage_plausible
- pair separation: 202.6 km
- depth difference: 37.6 km
- time separation: 29.3 days
- distance_link_score: 0.000
- M4+ between count: 68
- M4+ corridor fraction: 0.513
- M4+ between count control percentile: 0.842
- pseudo-corridor percentile: 0.925

Hypothesis matrix evidence:
- corridor-like migration/expansion: raw strong, corrected strong, distance low
- linked local fault-system activation: raw moderate, corrected moderate, distance low
- broader regional activation: raw strong, corrected strong, distance strong
- common regional rate pulse: raw moderate, corrected moderate, distance strong
- apparent artifact/window-choice explanation: raw low, corrected low, distance strong

Evidence:
- `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/02_report_synthesis/relationship_evidence_matrix_concise.csv`
- `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/02_report_synthesis/weak_negative_unresolved_signals.csv`

The corridor-versus-control plot shows a strong observed excess for M1-M2 (~155 observed vs ~63 pseudo-corridor median M4+ counts), so the corridor signal is real relative to geometry alone. However, the distance-aware screen rejects a simple local-linkage interpretation. Therefore the corrected interpretation is that M1-M2 is better treated as part of a broader regional activation or common rate pulse, not as convincing evidence of direct local pair coupling.

Figure support:
- `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/02_report_synthesis/fig_corridor_vs_control.png`
- `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/02_report_synthesis/fig_relationship_evidence_matrix.png`

This pair is a strong example of why raw or control-surviving corridor signals must still be screened against source-region separation.

### 4. M2-M3 is best treated primarily as independent local clusters within a broader regional episode
The synthesis assigns M2-M3 a different interpretation from M1-M3. It shows high raw activity but weaker evidence for local pair linkage after controls and distance-aware screening.

Quantitative evidence from `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/02_report_synthesis/raw_corrected_distance_summary.csv`:
- raw signal level: high
- control screen: partly_weakened
- distance plausibility: not_local_linkage_plausible
- pair separation: 145.2 km
- depth difference: -34.1 km
- time separation: 132.7 days
- distance_link_score: 0.193
- M4+ between count: 121
- M4+ corridor fraction: 0.105
- pseudo-corridor percentile: 0.558

Hypothesis matrix evidence:
- independent local clusters: raw strong, corrected strong, distance strong
- broader regional activation: raw strong, corrected moderate, distance strong
- common regional rate pulse: raw strong, corrected moderate, distance strong
- overlap, delayed activation, and linked local fault-system activation: low after correction and low in distance-aware plausibility
- artifact/background-window explanation: moderate raw, moderate corrected, strong distance-aware plausibility

Evidence:
- `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/02_report_synthesis/relationship_evidence_matrix_concise.csv`
- `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/02_report_synthesis/weak_negative_unresolved_signals.csv`

The corridor-versus-control plot supports this weak local-linkage interpretation: M2-M3 observed corridor count is only slightly above geometric expectation (~26 vs ~24), unlike M1-M2 and M1-M3. The time-projection figure also favors endpoint-centered reactivation over smooth inter-cluster migration. Thus M2-M3 should be prioritized for testing independent-cluster and broader-regional hypotheses, plus window/background-artifact sensitivity, rather than local corridor linkage.

Evidence:
- `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/02_report_synthesis/fig_corridor_vs_control.png`
- `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/02_report_synthesis/fig_pairwise_time_projection.png`
- `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/02_report_synthesis/fig_followup_priority.png`

### 5. Broader regional activation is the most robust system-wide hypothesis
Across the three pairs, broader regional activation is the most consistently strong or near-strong hypothesis after synthesis.

Evidence from `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/02_report_synthesis/relationship_evidence_matrix_concise.csv`:
- M1-M2: broader regional activation = raw strong, corrected strong, distance strong
- M1-M3: broader regional activation = raw strong, corrected strong, distance moderate
- M2-M3: broader regional activation = raw strong, corrected moderate, distance strong

This result is also reflected in the follow-up priorities and next-step recommendations:
- regional rate modeling,
- geodetic context,
- ocean-bottom pressure context,
- stress-field comparison.

Evidence:
- `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/02_report_synthesis/recommended_next_steps_ranked.csv`
- `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/02_report_synthesis/followup_priorities_concise.csv`
- `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/02_report_synthesis/strongest_supported_signals.csv`

The intervening-event chain figure is consistent with this interpretation: all three pairs show many M4+ intervening events but far fewer M6+ bridges, suggesting regional activation with moderate-event continuity rather than robust large-event chaining.

Evidence:
- `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/02_report_synthesis/fig_intervening_event_chains.png`

### 6. Corridor-like behavior is not uniformly interpretable as local migration
A key synthesis result is that corridor occupancy survives controls for some pairs, but distance-aware plausibility changes the interpretation.

From the figures and tables:
- M1-M2: strong corridor excess over pseudo-corridor controls, but local linkage implausible because of 202.6 km separation and large depth difference.
- M1-M3: strong corridor signal with nearby-plausible geometry, making this a viable follow-up target.
- M2-M3: corridor signal weak relative to control and low in distance-aware plausibility.

Evidence:
- `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/02_report_synthesis/fig_corridor_vs_control.png`
- `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/02_report_synthesis/raw_corrected_distance_summary.csv`
- `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/02_report_synthesis/relationship_evidence_matrix_concise.csv`

The time-projection figure further suggests that the dominant pattern is stepwise or endpoint-centered delayed activation, not clean smooth migration. That weakens simple migration narratives and favors more cautious formulations such as corridor-aligned activation or delayed endpoint reactivation.

### 7. Weak, negative, and unresolved results were preserved rather than forced into positive narratives
This task successfully preserved ambiguity and contradictory evidence, which was a core scientific requirement.

Examples from `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/02_report_synthesis/weak_negative_unresolved_signals.csv`:
- M1-M2 overlapping activation zones: low / low / low
- M1-M2 delayed activation: low / low / low
- M1-M2 compound/swarm-like clustering: low / low / low
- M2-M3 overlapping activation zones: low / low / low
- M2-M3 delayed activation: low / low / low
- M2-M3 linked local fault-system activation: possible / low / low
- M2-M3 artifact/window-choice: moderate / moderate / strong
- M1-M3 independent local clusters: moderate / low / moderate
- M1-M3 artifact/window-choice: low / low / moderate

This demonstrates that the synthesis did not overstate pairwise linkage where evidence remained weak, contradictory, or unresolved.

## Limitations and Assumptions
- This task is a synthesis stage only; it relies on previously validated outputs and does not independently recompute catalog metrics. Scientific validity therefore depends on the upstream relationship-analysis products in `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/01_relationship_analysis`.
- The interpretations are explicitly catalog-level and do not demonstrate physical triggering, rupture interaction, fluid migration, or stress transfer.
- Several hypotheses remain sensitive to the distinction between raw signal, control-corrected signal, and distance-aware plausibility. In particular, strong raw corridor or temporal signals do not imply local linkage if source-region geometry is unfavorable.
- The time-projection and corridor analyses suggest endpoint-centered and episodic activation more than smooth continuous migration; this limits causal interpretation from catalog geometry alone.
- M1-M3 remains the best local-linkage candidate, but even there the control screen is only `partly_weakened` rather than unambiguously surviving all alternatives.
- Artifact and background-window sensitivity remain important competing explanations, especially for M2-M3 and for regional interpretations more generally; the follow-up tables explicitly recommend expanded controls before physical inference.
- No PDFs were listed among the task outputs, so only image and text/CSV outputs were verified in this synthesis review.
- The handoff notes reported no warnings, assumptions, or limitations, but the scientific outputs themselves indicate unresolved ambiguity for several hypotheses and pairings.

## Report-Ready Summary
The report synthesis successfully condensed the validated Aomori M1-M2-M3 relationship analysis into a compact, report-ready evidence package. The main scientific conclusion is that the three pairwise relationships do not share one simple interpretation.

M1-M3 is the highest-priority pair for deeper physical analysis. It is the only pair that remains distance-plausible for nearby source regions while retaining moderate-to-strong support across several relationship-aware hypotheses after controls, especially overlapping activation zones, linked local fault-system activation, corridor-like activation, and delayed/episodic activation. The strongest supporting files are `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/02_report_synthesis/pairwise_scientific_summary.csv`, `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/02_report_synthesis/relationship_evidence_matrix_concise.csv`, `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/02_report_synthesis/fig_pairwise_time_projection.png`, and `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/02_report_synthesis/fig_followup_priority.png`.

M1-M2 shows strong raw and control-surviving corridor and between-event signals, but these do not remain plausible as a simple local pair linkage because the clusters are far apart and have large depth offset. Its best-supported interpretation is broader regional activation or a common regional rate pulse, not direct local coupling. The strongest evidence is in `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/02_report_synthesis/raw_corrected_distance_summary.csv`, `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/02_report_synthesis/fig_corridor_vs_control.png`, and `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/02_report_synthesis/relationship_evidence_matrix_concise.csv`.

M2-M3 is best treated as independent local clusters embedded in a broader regional episode. Local overlap, delayed activation, and linked-fault hypotheses are weak after correction and distance-aware screening, while independent-cluster, regional-activation, and artifact/window-sensitivity explanations remain the main competing models. This interpretation is supported by `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/02_report_synthesis/relationship_evidence_matrix_concise.csv`, `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/02_report_synthesis/weak_negative_unresolved_signals.csv`, and `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/02_report_synthesis/fig_corridor_vs_control.png`.

Across the full system, broader regional activation is the most robust cross-pair explanation and should remain a central competing model in any future physical study. The recommended next-step outputs consistently prioritize regional rate modeling, high-precision relocation, waveform cross-correlation, focal-mechanism comparison, geodesy, ocean-bottom pressure data, and stress-field comparison, as documented in `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/02_report_synthesis/recommended_next_steps_ranked.csv` and `<CASE_ROOT>/run/02_3_relationship_screening/exp_run/outputs/02_report_synthesis/final_scientific_report.md`.
</task_analysis>


## Evaluation Quality Summary
Use this evaluation metadata to disclose delivery status, scientific confidence, and important limitations in the final report.
<evaluation_quality>
{
  "delivery_status": "complete",
  "is_satisfactory": true,
  "limitations": [
    {
      "evidence": "Several pair interpretations remain split across raw, control-corrected, and distance-aware layers; M1-M3 retains substantial ambiguity/shared fractions and M2-M3 retains artifact/background competition.",
      "impact": "Main conclusions are useful for prioritization, but not definitive for discriminating among nearby competing catalog-level hypotheses.",
      "severity": "medium",
      "type": "uncertainty"
    },
    {
      "evidence": "Corridor, endpoint, and temporal-window definitions are central to multiple metrics; M1-M2 assignment stability is only 0.780 and robustness summaries indicate some sensitivity to geometry choices.",
      "impact": "Some pair-specific strengths, especially corridor-style interpretations, should be treated as conditional on the chosen geometric and temporal framing.",
      "severity": "medium",
      "type": "method_assumption"
    },
    {
      "evidence": "A semantic mismatch was explicitly reported between the M2-M3 independent_local_clusters follow-up priority table entry and the narrative text.",
      "impact": "This may confuse downstream prioritization, though it does not materially change the scientific interpretation of the pair.",
      "severity": "low",
      "type": "output_quality"
    },
    {
      "evidence": "Mechanism information was matched conservatively and acknowledged as not fully exploited for pair discrimination in the current outputs.",
      "impact": "The catalog-level conclusions are still valid, but some follow-up-target discrimination remains less constrained than it could be with richer contextual screening.",
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
