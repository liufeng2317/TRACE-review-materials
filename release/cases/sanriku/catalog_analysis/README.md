# Sanriku Catalog Analysis

This directory contains the formal catalog-analysis runs for the Sanriku
case, kept in the order of the original analysis entry scripts.

```text
catalog_analysis/
├── 01_data_foundation/
├── 02_1_sequence_response/
├── 02_2_behavior_diagnosis/
├── 02_3_relationship_screening/
├── 02_4_bg_rate_correction/
├── 03_1A_event_chain_and_bursts/
├── 03_1B_spatial_depth_migration/
├── 03_1C_mechanism_screening/
├── 03_1D_catalog_statistic_model_check/
├── 04_1A_M1_migration/
└── scientific_synthesis_reference/
```

Each stage contains:

- the public entry script at the stage root;
- `results/config.yaml`, `request.txt`, and execution metadata;
- `results/exp_plans/` with the generated plans;
- `results/exp_run/scripts/` with the agent-generated analysis code;
- `results/exp_run/analysis/` with task-level analysis records;
- `results/exp_run/outputs/` with reviewable tables, summaries, and figures;
- `results/log/trajectory/` with the agent execution trajectories;
- `results/state/` and `results/research_report/` with the final run state and
  textual reports.

The package uses public placeholders for local data, software, and execution
locations. The active model endpoint in the copied run configuration is the
official OpenAI API endpoint.

`scientific_synthesis_reference/` contains the reference synthesis run that
integrates the formal analysis stages into an evidence-based scientific
narrative. Its `results/synthesis/` directory includes the synthesis frame,
run summaries, core observations, candidate scientific stories, story chains,
the generated conceptual figure, and the final Markdown report.

## Data Scope

The analysis branches use the relocated catalog products recorded in each
branch:

- `01_data_foundation` and `02_1_sequence_response` use their saved
  full-period relocated catalog products beginning on `2025-06-01`.
- The `03/04` branches use the saved full-period product
  `Snet_catalog_relocate_250601_260501.csv`.
- `02_2_behavior_diagnosis` and `02_3_relationship_screening` use
  `Snet_catalog_relocate_250930_260501.csv` (22,096 events, beginning
  `2025-09-30`), matching their saved sequence-diagnosis results.
- `02_4_bg_rate_correction` uses the same active-period relocated catalog
  together with the 2020-2026 long-term raw catalog, and applies its own
  2025-10-01 to 2026-05-01 analysis window.

The catalog scope is part of each branch's analysis definition. The exact
event count should be read from the branch output together with its input
filename and time window.

## Paper-facing Outputs

The retained paper-facing tables are aligned with the supplementary PDF data:

- `03_1B_spatial_depth_migration` corresponds to Supplementary Fig. 1.
- `03_1D_catalog_statistic_model_check` corresponds to Supplementary Fig. 2
  and uses the M1-M3-oriented whole area.
- `04_1A_M1_migration` corresponds to Supplementary Fig. 3 and uses the
  focused 80 km M6.9-centered windows.
- `scientific_synthesis_reference/results/synthesis/paper_focused_stage_summary.csv`
  records the five fixed-stage counts and rates reported in the final
  manuscript and Supplementary Note E.3.

The `03_1D` oriented-area rates are not expected to equal either the
five-stage focused-box rates in the reference table or the two-window
M6.9-centered rates in `04_1A`; these are different spatial and temporal
scopes of the same catalog.

## Result Coupling

- `01_data_foundation`: internally sequential data audit, matching, background
  characterization, context, figures, and candidate-pattern outputs.
- `02_1_sequence_response`: internally sequential verification, extraction,
  diagnostics, robustness, comparison, controls, figures, and reusable outputs.
- `02_2_behavior_diagnosis`: independent sequence-behavior diagnosis based on
  the relocated catalog.
- `02_3_relationship_screening`: `01_relationship_analysis` feeds the final
  `02_report_synthesis` outputs.
- `02_4_bg_rate_correction`: primary background-rate analysis feeds the
  bootstrap/control analysis.
- `03_1A_event_chain_and_bursts`: the event-chain analysis feeds its figures
  and screening classification.
- `03_1B_spatial_depth_migration`, `03_1D_catalog_statistic_model_check`, and
  `04_1A_M1_migration`: independent supplementary analysis branches.
- `03_1C_mechanism_screening`: catalog screening feeds the mechanism-coverage
  audit.
- `scientific_synthesis_reference`: integrates the first nine formal analysis
  runs. `04_1A_M1_migration` remains a separate supplementary branch.

The final scientific values should be read from
`results/exp_run/outputs/` and the corresponding reports. `results/state/` and
trajectory files preserve agent execution history, including earlier attempts
and intermediate diagnostics, and are not an alternative source of final
scientific values.
