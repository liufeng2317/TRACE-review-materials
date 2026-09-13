# Workflow Overview

## Top-Level Task Dependencies

```mermaid
graph TD
    01_aomori_sequence_analysis
    style 01_aomori_sequence_analysis fill:#f2f4f4,stroke:#333,stroke-width:1px
```
**Description:**
- `01_aomori_sequence_analysis`: Build the mainshock-referenced sequence dataset, compute all requested metrics and context summaries, generate the required figures, score behavior dimensions, assemble the scientific diagnosis, and validate outputs in one self-contained script.


## Subtask Dependencies

#### 01_aomori_sequence_analysis
**Usage**: Build the mainshock-referenced sequence dataset, compute all requested metrics and context summaries, generate the required figures, score behavior dimensions, assemble the scientific diagnosis, and validate outputs in one self-contained script.
```mermaid
graph TD
    validate_and_load_inputs
    validate_and_load_inputs --> match_mainshock_like_events
    validate_and_load_inputs --> build_mainshock_reference_table
    match_mainshock_like_events --> build_mainshock_reference_table
    build_mainshock_reference_table --> generate_short_window_morphology_figures
    match_mainshock_like_events --> generate_short_window_morphology_figures
    validate_and_load_inputs --> generate_short_window_morphology_figures
    build_mainshock_reference_table --> compute_matched_window_metrics
    match_mainshock_like_events --> compute_matched_window_metrics
    compute_matched_window_metrics --> derive_curated_comparison_products
    build_mainshock_reference_table --> compute_temporal_depth_mechanism_and_migration_context
    validate_and_load_inputs --> compute_temporal_depth_mechanism_and_migration_context
    match_mainshock_like_events --> compute_temporal_depth_mechanism_and_migration_context
    compute_matched_window_metrics --> score_behavior_dimensions_and_write_diagnosis
    compute_temporal_depth_mechanism_and_migration_context --> score_behavior_dimensions_and_write_diagnosis
    generate_short_window_morphology_figures --> score_behavior_dimensions_and_write_diagnosis
    build_mainshock_reference_table --> validate_outputs_and_record_run_summary
    match_mainshock_like_events --> validate_outputs_and_record_run_summary
    compute_matched_window_metrics --> validate_outputs_and_record_run_summary
    compute_temporal_depth_mechanism_and_migration_context --> validate_outputs_and_record_run_summary
    score_behavior_dimensions_and_write_diagnosis --> validate_outputs_and_record_run_summary
    generate_short_window_morphology_figures --> validate_outputs_and_record_run_summary
    derive_curated_comparison_products --> validate_outputs_and_record_run_summary
    style compute_matched_window_metrics fill:#d6eaf8,stroke:#333,stroke-width:1px
    style validate_and_load_inputs fill:#fdebd0,stroke:#333,stroke-width:1px
    style match_mainshock_like_events fill:#f5eef8,stroke:#333,stroke-width:1px
    style derive_curated_comparison_products fill:#d4e6f1,stroke:#333,stroke-width:1px
    style score_behavior_dimensions_and_write_diagnosis fill:#f2f4f4,stroke:#333,stroke-width:1px
    style validate_outputs_and_record_run_summary fill:#d5f5e3,stroke:#333,stroke-width:1px
    style generate_short_window_morphology_figures fill:#fdebd0,stroke:#333,stroke-width:1px
    style compute_temporal_depth_mechanism_and_migration_context fill:#f9ebea,stroke:#333,stroke-width:1px
    style build_mainshock_reference_table fill:#ebdef0,stroke:#333,stroke-width:1px
```
**Description:**
- `validate_and_load_inputs`: Load the catalog, mainshock, mechanism, and station inputs and standardize required fields.
- `match_mainshock_like_events`: Identify the catalog event corresponding to each mainshock with deterministic matching and ambiguity diagnostics.
- `build_mainshock_reference_table`: Compute event-to-mainshock relative times, distances, depth differences, bins, flags, and overlap diagnostics for all events.
- `generate_short_window_morphology_figures`: Create the required plus-minus 7 day and within 100 km morphology and summary figures for M1, M2, and M3.
- `compute_matched_window_metrics`: Compute exhaustive matched pre and post metrics across all requested time windows and spatial definitions.
- `derive_curated_comparison_products`: Summarize the exhaustive metric tables into cross-mainshock comparison figures and sensitivity views.
- `compute_temporal_depth_mechanism_and_migration_context`: Quantify temporal concentration, radial progression diagnostics, depth distributions, and focal mechanism context for each mainshock-centered sequence.
- `score_behavior_dimensions_and_write_diagnosis`: Assign evidence-based behavior-dimension scores for each mainshock and assemble the concise scientific diagnosis and evidence tables.
- `validate_outputs_and_record_run_summary`: Verify that all required tables and figures were created, are non-empty, and are recorded in a machine-readable run summary.