# Workflow Overview

## Top-Level Task Dependencies

```mermaid
graph TD
    01_repeat_event_analysis
    01_repeat_event_analysis --> 02_repeat_event_visualization
    style 02_repeat_event_visualization fill:#fdebd3,stroke:#333,stroke-width:1px
    style 01_repeat_event_analysis fill:#f6ddcc,stroke:#333,stroke-width:1px
```
**Description:**
- `01_repeat_event_analysis`: Audit metadata, prefilter candidate event pairs, run baseline phase-aligned waveform cross-correlation in parallel, aggregate pair similarity, build repeat-event families, and write machine-readable outputs.
- `02_repeat_event_visualization`: Generate reviewable figures from the standardized repeat-event outputs and representative SAC waveforms using the baseline processing chain.


## Subtask Dependencies

#### 01_repeat_event_analysis
**Usage**: Audit metadata, prefilter candidate event pairs, run baseline phase-aligned waveform cross-correlation in parallel, aggregate pair similarity, build repeat-event families, and write machine-readable outputs.
```mermaid
graph TD
    audit_metadata_and_paths
    audit_metadata_and_paths --> prefilter_candidate_event_pairs
    prefilter_candidate_event_pairs --> run_parallel_baseline_cross_correlation
    audit_metadata_and_paths --> run_parallel_baseline_cross_correlation
    prefilter_candidate_event_pairs --> classify_repeat_pairs_and_build_families
    run_parallel_baseline_cross_correlation --> classify_repeat_pairs_and_build_families
    audit_metadata_and_paths --> classify_repeat_pairs_and_build_families
    prefilter_candidate_event_pairs --> write_outputs_and_analysis_summary
    run_parallel_baseline_cross_correlation --> write_outputs_and_analysis_summary
    classify_repeat_pairs_and_build_families --> write_outputs_and_analysis_summary
    audit_metadata_and_paths --> write_outputs_and_analysis_summary
    style prefilter_candidate_event_pairs fill:#ebdef0,stroke:#333,stroke-width:1px
    style write_outputs_and_analysis_summary fill:#f9e79f,stroke:#333,stroke-width:1px
    style run_parallel_baseline_cross_correlation fill:#d4e6d4,stroke:#333,stroke-width:1px
    style audit_metadata_and_paths fill:#ebdef0,stroke:#333,stroke-width:1px
    style classify_repeat_pairs_and_build_families fill:#f2f4f4,stroke:#333,stroke-width:1px
```
**Description:**
- `audit_metadata_and_paths`: Check required metadata fields, time coverage, SAC path existence, pick availability, and minimal data issues within the fixed analysis window.
- `prefilter_candidate_event_pairs`: Select physically plausible and computationally tractable candidate event pairs using shared observations, epicentral distance, magnitude difference, and ranking rules.
- `run_parallel_baseline_cross_correlation`: Match common station-components exactly, align by S then P picks, preprocess SAC waveforms consistently, and compute positive-peak-based cross-correlation metrics in multiprocessing batches.
- `classify_repeat_pairs_and_build_families`: Assign loose and high-confidence repeat-pair labels from pair similarity results and construct repeat-event families as connected components.
- `write_outputs_and_analysis_summary`: Validate merged outputs, enforce key field consistency, and write final CSV and JSON deliverables with audit, runtime, threshold, and failure statistics.

#### 02_repeat_event_visualization
**Usage**: Generate reviewable figures from the standardized repeat-event outputs and representative SAC waveforms using the baseline processing chain.
```mermaid
graph TD
    select_representative_pairs_and_families
    generate_spatial_and_statistical_figures
    select_representative_pairs_and_families --> generate_waveform_comparison_figures
    generate_spatial_and_statistical_figures --> validate_figure_outputs
    generate_waveform_comparison_figures --> validate_figure_outputs
    select_representative_pairs_and_families --> validate_figure_outputs
    style validate_figure_outputs fill:#fef9e7,stroke:#333,stroke-width:1px
    style generate_spatial_and_statistical_figures fill:#fef9e7,stroke:#333,stroke-width:1px
    style generate_waveform_comparison_figures fill:#f2f4f4,stroke:#333,stroke-width:1px
    style select_representative_pairs_and_families fill:#d4e6d4,stroke:#333,stroke-width:1px
```
**Description:**
- `select_representative_pairs_and_families`: Choose top-scoring event pairs and major families for waveform and timeline visualization using reproducible ranking rules.
- `generate_spatial_and_statistical_figures`: Create spatial maps, family timelines, and statistical diagnostic plots for repeat-event screening and family structure.
- `generate_waveform_comparison_figures`: Re-read representative SAC waveforms and plot phase-aligned waveform overlays ordered by average station distance with CC and lag annotations.
- `validate_figure_outputs`: Check that all required figures are produced and record figure completion and selection rules for reproducibility.