<science_report_context_compact>

## Context Map
Use this packet in order: objective -> actual methods -> core claims -> evidence index -> limitations/evaluation. Use context references and analysis files only when details are insufficient.

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
Evaluate the strength of post-mainshock activation using short-window post/pre rate changes, immediate post-mainshock concentration, near-field dominance, and time-dependent decay after the mainshock. This dimension measures post-mainshock response only; it does not imply a clean single-mainshock aftershock sequence. Interpret post/pre ratios together with magnitude hierarchy, companion events, and pre-mainshock act
...[truncated]
</user_request>

## Planning Snapshot
Use this only as intent context; prefer actual methods, claims, and evidence below for report content.
plan_summary: Goal Diagnose and compare the mainshock-centered sequence behavior around M1, M2, and M3 in the Aomori relocated earthquake catalog by constructing a unified event–mainshock reference table, generating the required short-window morphology figures, computing matched pre/post metrics across windows and spatial definitions, adding depth and focal-mechanism context, and assigning evidence-based non-exclusive behavior-dimension scores with explicit caveats. Planning Assumptions Use observation data only from the provided project folder: `catalog/Snet_catalog_relocate_250930_260501.csv` `catalog/main_earthquake.csv` `source_mechanism/Snet_mecha.csv` `stations/station.sta` One primary task script should handle input validation, event-reference table construction, mainshock-like matching, metric computation, figure generation, and immediate output checks; one secondary task script should convert saved tables
...[truncated]

## Context References
- full_audit_context: <CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/report/science_report_context.md

## Task Ledger
<task_record>
name: 01_aomori_sequence_analysis
description: Build the mainshock-referenced sequence dataset, compute all requested metrics and context summaries, generate the required figures, score behavior dimensions, assemble the scientific diagnosis, and validate outputs in o
...[truncated]
ancestors: none
handoff_json: <CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/log/coding_progress/task_handoff/01_aomori_sequence_analysis.json
analysis_file: <CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/analysis/01_aomori_sequence_analysis.md
output_dir: <CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis
</task_record>


## Actual Method Summary
This section summarizes what was actually implemented and analyzed. Use it instead of repeating the full plan.
<method_record task="01_aomori_sequence_analysis">
role: final_analysis
summary: A self-contained script generated the analysis products: - `[path]` Implementation evidence confirms that the workflow produced the required mainshock-centered evidence set:
</method_record>
workflow_role: Build the mainshock-referenced sequence dataset, compute all requested metrics and context summaries, generate the required figures, score behavior dimensions, assemble the scienti
...[truncated]


## Core Scientific Claims
Use these claim-oriented summaries as the backbone of the final report. Each major claim should remain tied to the evidence index below.
<scientific_claim task="01_aomori_sequence_analysis">
claim_role: final
The task successfully produced a mainshock-referenced sequence diagnosis for the three Aomori mainshocks, with reusable figures and tables suitable for a report.

The clearest scientific picture is:

- **M1** is the most compact and near-field dominated sequence, but it is not strongly single-mainshock dominated. It has a very small dominance gap (0.3), multiple comparable companion events (2 within 0.5 magnitude units; 6 within 1.0), strong pre-mainshock activation in the ±7 day frame (21 M4+, 8 M5+ pre-events), and modest broader regional participation (post outer-band fraction 0.210). This supports a diagnosis of moderate post-mainshock response combined with moderate compound/swam-like organization and strong pre-mainshock activation, while still lacking evidence for monotonic migration or slow-slip-like behavior. Key evidence: `/liuf
...[truncated]
</scientific_claim>


## Evidence Index
Use these handoff summaries as the primary artifact index. Read full handoff files only when this compact evidence is insufficient.
<task_evidence task="01_aomori_sequence_analysis">
status: success
stage: analysis_done
quality_flags: task_status:success, outputs_truncated
handoff_json: <CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/log/coding_progress/task_handoff/01_aomori_sequence_analysis.json
analysis_file: <CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/analysis/01_aomori_sequence_analysis.md
output_dir: <CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis
result_summary: Build the mainshock-referenced sequence dataset, compute all requested metrics and context summaries, generate the required figures, score behavior dimensions, assemble the scienti...[truncated] Status=success; outputs=28 discovered; primary=8.

primary_outputs:
- behavior_dimension_scores.csv: <CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/behavior_dimension_scores.csv
- behavior_dimension_supporting_metrics.csv: <CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/behavior_dimension_supporting_metrics.csv
- companion_event_metrics.csv: <CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/companion_event_metrics.csv
- depth_summary_by_mainshock.csv: <CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/depth_summary_by_mainshock.csv
- depth_summary_m4_m5.csv: <CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/depth_summary_m4_m5.csv
- largest_event_lists_by_window.csv: <CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/largest_event_lists_by_window.csv
- magnitude_dominance_metrics.csv: <CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/magnitude_dominance_metrics.csv
- mainshock_like_match_summary.csv: <CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/mainshock_like_match_summary.csv
</task_evidence>


## Analysis Source Index
Read these task analysis files only when the method summary, claims, limitations, and evidence index are insufficient.
- 01_aomori_sequence_analysis: analysis=<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/analysis/01_aomori_sequence_analysis.md; output_dir=<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis

## Cross-Task Limitations and Assumptions
Use these limitations to qualify scientific claims in the final report.
<task_limitations task="01_aomori_sequence_analysis">
1. **Catalog-only behavior diagnosis**
   The outputs explicitly caution that several interpretations are catalog-level only. In particular:
   - swarm-like organization does not prove a physical swarm process,
   - post/pre contrasts can be inflated by overlap with neighboring sequences or changing detectability,
   - slow-slip-related behavior cannot be established without geodetic/tremor/pressure data.
   These cautions are recorded in:
   - `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/behavior_dimension_supporting_metrics.csv`

2. **Sequenc
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
- Start from the scientific objective, actual methods, core claims, and evidence index.
- Choose the final report shape according to the request and evidence; do not force a fixed template.
- Tie every major result to task analyses and concrete output files from the evidence index.
- Include warnings, assumptions, partial coverage, failed items, and other limitations when present.
- Inspect full handoff JSON, analyses, or raw outputs only when the compact context is insufficient.
- Do not fabricate results, citations, or file paths.

</science_report_context_compact>
