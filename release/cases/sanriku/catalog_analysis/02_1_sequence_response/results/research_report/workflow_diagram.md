# Workflow Overview

## Top-Level Task Dependencies

```mermaid
graph TD
    01_data_verification_and_rematch
    01_data_verification_and_rematch --> 02_sequence_extraction
    02_sequence_extraction --> 03_sequence_diagnostics
    03_sequence_diagnostics --> 04_robustness_analysis
    04_robustness_analysis --> 05_three_sequence_comparison
    02_sequence_extraction --> 06_control_comparison
    03_sequence_diagnostics --> 06_control_comparison
    03_sequence_diagnostics --> 07_figure_generation
    04_robustness_analysis --> 07_figure_generation
    05_three_sequence_comparison --> 07_figure_generation
    06_control_comparison --> 07_figure_generation
    01_data_verification_and_rematch --> 08_reusable_outputs
    02_sequence_extraction --> 08_reusable_outputs
    03_sequence_diagnostics --> 08_reusable_outputs
    04_robustness_analysis --> 08_reusable_outputs
    05_three_sequence_comparison --> 08_reusable_outputs
    06_control_comparison --> 08_reusable_outputs
    07_figure_generation --> 08_reusable_outputs
    style 05_three_sequence_comparison fill:#d1f2eb,stroke:#333,stroke-width:1px
    style 06_control_comparison fill:#e8f8f5,stroke:#333,stroke-width:1px
    style 08_reusable_outputs fill:#fadbd8,stroke:#333,stroke-width:1px
    style 04_robustness_analysis fill:#eaf2f8,stroke:#333,stroke-width:1px
    style 07_figure_generation fill:#e8f8f5,stroke:#333,stroke-width:1px
    style 01_data_verification_and_rematch fill:#fdebd0,stroke:#333,stroke-width:1px
    style 03_sequence_diagnostics fill:#d4e6d4,stroke:#333,stroke-width:1px
    style 02_sequence_extraction fill:#f9ebea,stroke:#333,stroke-width:1px
```
**Description:**
- `01_data_verification_and_rematch`: Validate source tables and rematch the three mainshocks to the relocated catalog.
- `02_sequence_extraction`: Extract event-centered sequences around each matched mainshock across the full parameter grid.
- `03_sequence_diagnostics`: Compute counts, rates, distributions, spatial patterns, and decay diagnostics for each sequence.
- `04_robustness_analysis`: Test which sequence features remain stable across alternative parameter definitions.
- `05_three_sequence_comparison`: Compare M1, M2, and M3 using a common baseline and then across alternate definitions.
- `06_control_comparison`: Evaluate observed sequence behavior against simple background or randomized controls.
- `07_figure_generation`: Generate publication-quality sequence-analysis figures for all mainshocks and comparisons.
- `08_reusable_outputs`: Export validated tables and figure-ready datasets for downstream reuse.


## Subtask Dependencies

#### 01_data_verification_and_rematch
**Usage**: Validate source tables and rematch the three mainshocks to the relocated catalog.
```mermaid
graph TD
    load_inputs
    load_inputs --> verify_required_fields
    load_inputs --> rematch_mainshocks
    rematch_mainshocks --> link_context_metadata
    load_inputs --> link_context_metadata
    style verify_required_fields fill:#f5eef8,stroke:#333,stroke-width:1px
    style load_inputs fill:#e8f8f5,stroke:#333,stroke-width:1px
    style link_context_metadata fill:#f5eef8,stroke:#333,stroke-width:1px
    style rematch_mainshocks fill:#f9ebea,stroke:#333,stroke-width:1px
```
**Description:**
- `load_inputs`: Read the catalog, mainshock, mechanism, and station tables.
- `verify_required_fields`: Check that sequence-analysis fields are present and usable.
- `rematch_mainshocks`: Match M1, M2, and M3 to relocated catalog events using tolerant time and location criteria.
- `link_context_metadata`: Summarize station and mechanism availability for downstream sequence analysis.

#### 02_sequence_extraction
**Usage**: Extract event-centered sequences around each matched mainshock across the full parameter grid.
```mermaid
graph TD
    define_parameter_grid
    define_parameter_grid --> extract_event_centered_sequences
    extract_event_centered_sequences --> standardize_sequence_records
    style extract_event_centered_sequences fill:#fef9e7,stroke:#333,stroke-width:1px
    style define_parameter_grid fill:#eaf2f8,stroke:#333,stroke-width:1px
    style standardize_sequence_records fill:#d4e6f1,stroke:#333,stroke-width:1px
```
**Description:**
- `define_parameter_grid`: Set the spatial, temporal, depth, and magnitude definitions for extraction.
- `extract_event_centered_sequences`: Build event-centered subsets for all mainshocks and parameter combinations.
- `standardize_sequence_records`: Annotate each extracted event with relative time, distance, and parameter metadata.

#### 03_sequence_diagnostics
**Usage**: Compute counts, rates, distributions, spatial patterns, and decay diagnostics for each sequence.
```mermaid
graph TD
    compute_count_metrics
    compute_rate_metrics
    compute_distribution_metrics
    fit_post_event_decay
    summarize_spatial_and_mechanism_context
    style compute_distribution_metrics fill:#ebdef0,stroke:#333,stroke-width:1px
    style compute_count_metrics fill:#e8f8f5,stroke:#333,stroke-width:1px
    style compute_rate_metrics fill:#d1f2eb,stroke:#333,stroke-width:1px
    style fit_post_event_decay fill:#d5f5e3,stroke:#333,stroke-width:1px
    style summarize_spatial_and_mechanism_context fill:#eaf2f8,stroke:#333,stroke-width:1px
```
**Description:**
- `compute_count_metrics`: Calculate event counts and cumulative counts for each sequence window.
- `compute_rate_metrics`: Estimate moving-window seismicity rates and pre/post ratios.
- `compute_distribution_metrics`: Summarize magnitude and depth distributions plus radial and time-distance patterns.
- `fit_post_event_decay`: Fit simple Omori-style decay where the post-event window supports it.
- `summarize_spatial_and_mechanism_context`: Derive spatial concentration indicators and focal-mechanism availability summaries.

#### 04_robustness_analysis
**Usage**: Test which sequence features remain stable across alternative parameter definitions.
```mermaid
graph TD
    build_sensitivity_matrices
    build_sensitivity_matrices --> classify_robust_features
    style build_sensitivity_matrices fill:#e8daef,stroke:#333,stroke-width:1px
    style classify_robust_features fill:#e8f8f5,stroke:#333,stroke-width:1px
```
**Description:**
- `build_sensitivity_matrices`: Assemble feature sensitivities across radius, time, depth, and magnitude settings.
- `classify_robust_features`: Separate stable sequence signatures from parameter-dependent ones.

#### 05_three_sequence_comparison
**Usage**: Compare M1, M2, and M3 using a common baseline and then across alternate definitions.
```mermaid
graph TD
    compare_baseline_sequences
    compare_baseline_sequences --> summarize_definition_sensitivity
    style compare_baseline_sequences fill:#d4e6d4,stroke:#333,stroke-width:1px
    style summarize_definition_sensitivity fill:#fdebd3,stroke:#333,stroke-width:1px
```
**Description:**
- `compare_baseline_sequences`: Contrast background, pre-event, post-event, burstiness, decay, spatial, depth, and magnitude behavior.
- `summarize_definition_sensitivity`: Document how the cross-event comparison changes under alternate sequence definitions.

#### 06_control_comparison
**Usage**: Evaluate observed sequence behavior against simple background or randomized controls.
```mermaid
graph TD
    build_control_windows
    build_control_windows --> compute_control_metrics
    style build_control_windows fill:#eaf2f8,stroke:#333,stroke-width:1px
    style compute_control_metrics fill:#d4e6f1,stroke:#333,stroke-width:1px
```
**Description:**
- `build_control_windows`: Define background or randomized control windows matched to the event-centered study design.
- `compute_control_metrics`: Calculate control-window counts and rate benchmarks for direct comparison.

#### 07_figure_generation
**Usage**: Generate publication-quality sequence-analysis figures for all mainshocks and comparisons.
```mermaid
graph TD
    make_event_centered_maps
    make_sequence_diagnostic_panels
    make_sensitivity_figures
    make_comparison_summary_figure
    style make_sequence_diagnostic_panels fill:#fdebd0,stroke:#333,stroke-width:1px
    style make_comparison_summary_figure fill:#f6ddcc,stroke:#333,stroke-width:1px
    style make_event_centered_maps fill:#d1f2eb,stroke:#333,stroke-width:1px
    style make_sensitivity_figures fill:#fcf3cf,stroke:#333,stroke-width:1px
```
**Description:**
- `make_event_centered_maps`: Plot event-centered maps for M1, M2, and M3.
- `make_sequence_diagnostic_panels`: Plot cumulative counts, rate curves, decay fits, and time-distance or radial-distance views.
- `make_sensitivity_figures`: Plot radius, time-window, magnitude-threshold, and depth-stratified sensitivity summaries.
- `make_comparison_summary_figure`: Plot the three-sequence comparison summary and control benchmarks.

#### 08_reusable_outputs
**Usage**: Export validated tables and figure-ready datasets for downstream reuse.
```mermaid
graph TD
    export_master_tables
    export_robustness_and_controls
    style export_master_tables fill:#fdebd0,stroke:#333,stroke-width:1px
    style export_robustness_and_controls fill:#d6eaf8,stroke:#333,stroke-width:1px
```
**Description:**
- `export_master_tables`: Package core validated sequence-analysis tables into reusable machine-readable outputs.
- `export_robustness_and_controls`: Save robustness, sensitivity, and control-comparison tables for downstream analysis.