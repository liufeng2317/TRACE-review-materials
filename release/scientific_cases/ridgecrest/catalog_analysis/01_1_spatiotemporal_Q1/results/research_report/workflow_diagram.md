# Workflow Overview

## Top-Level Task Dependencies

```mermaid
graph TD
    01_catalog_windows_qc
    01_catalog_windows_qc --> 02_spatiotemporal_metrics
    02_spatiotemporal_metrics --> 03_visualization_and_evidence
    style 03_visualization_and_evidence fill:#eaf2f8,stroke:#333,stroke-width:1px
    style 01_catalog_windows_qc fill:#f9e79f,stroke:#333,stroke-width:1px
    style 02_spatiotemporal_metrics fill:#e8daef,stroke:#333,stroke-width:1px
```
**Description:**
- `01_catalog_windows_qc`: Build the validated Ridgecrest catalog, verified mainshock references, common map extent, and reusable time-window tables.
- `02_spatiotemporal_metrics`: Compute window-based migration, orientation, spread, and clustering diagnostics for the Ridgecrest sequence.
- `03_visualization_and_evidence`: Generate all requested map figures, comparison plots, machine-readable evidence summaries, and final validation products.


## Subtask Dependencies

#### 01_catalog_windows_qc
**Usage**: Build the validated Ridgecrest catalog, verified mainshock references, common map extent, and reusable time-window tables.
```mermaid
graph TD
    load_and_validate_inputs
    load_and_validate_inputs --> clean_catalog_and_verify_mainshocks
    clean_catalog_and_verify_mainshocks --> derive_extent_and_event_attributes
    clean_catalog_and_verify_mainshocks --> build_window_definitions
    derive_extent_and_event_attributes --> build_window_definitions
    style derive_extent_and_event_attributes fill:#d4e6d4,stroke:#333,stroke-width:1px
    style load_and_validate_inputs fill:#fdebd0,stroke:#333,stroke-width:1px
    style build_window_definitions fill:#ebdef0,stroke:#333,stroke-width:1px
    style clean_catalog_and_verify_mainshocks fill:#fcf3cf,stroke:#333,stroke-width:1px
```
**Description:**
- `load_and_validate_inputs`: Read the catalog and mainshock CSV files, verify schema, and parse event times as UTC.
- `clean_catalog_and_verify_mainshocks`: Remove invalid rows, sort events chronologically, identify Mw 6.4 and Mw 7.1 mainshocks, and verify their order.
- `derive_extent_and_event_attributes`: Compute one padded map extent and reusable projected and elapsed-time attributes for all events.
- `build_window_definitions`: Construct complete time-window tables for whole-sequence, comparison, and post-Mw 6.4 analyses.

#### 02_spatiotemporal_metrics
**Usage**: Compute window-based migration, orientation, spread, and clustering diagnostics for the Ridgecrest sequence.
```mermaid
graph TD
    compute_window_metrics_whole_sequence
    compute_window_metrics_post64_hourly
    compute_cluster_diagnostics
    compute_before_after_change_metrics
    compute_window_metrics_whole_sequence --> validate_metric_completeness
    compute_window_metrics_post64_hourly --> validate_metric_completeness
    compute_cluster_diagnostics --> validate_metric_completeness
    compute_before_after_change_metrics --> validate_metric_completeness
    style validate_metric_completeness fill:#f2f4f4,stroke:#333,stroke-width:1px
    style compute_window_metrics_whole_sequence fill:#fdebd0,stroke:#333,stroke-width:1px
    style compute_cluster_diagnostics fill:#eaf2f8,stroke:#333,stroke-width:1px
    style compute_window_metrics_post64_hourly fill:#eaf2f8,stroke:#333,stroke-width:1px
    style compute_before_after_change_metrics fill:#d4e6d4,stroke:#333,stroke-width:1px
```
**Description:**
- `compute_window_metrics_whole_sequence`: Calculate per-window counts, centroid, spread, orientation, and distance metrics for whole-sequence windows.
- `compute_window_metrics_post64_hourly`: Calculate hourly centroid, spread, orientation, and migration metrics for the post-Mw 6.4 sequence.
- `compute_cluster_diagnostics`: Estimate per-window cluster structure and simultaneous activation diagnostics using fixed projected-space settings.
- `compute_before_after_change_metrics`: Quantify centroid shifts, orientation changes, area changes, and density-center shifts around the two mainshocks.
- `validate_metric_completeness`: Check that all expected windows and comparison intervals have metrics or explicit insufficient-data flags.

#### 03_visualization_and_evidence
**Usage**: Generate all requested map figures, comparison plots, machine-readable evidence summaries, and final validation products.
```mermaid
graph TD
    render_whole_sequence_maps
    render_before_after_comparisons
    render_post64_hourly_maps
    render_whole_sequence_maps --> build_triggering_evidence_products
    render_post64_hourly_maps --> build_triggering_evidence_products
    render_whole_sequence_maps --> validate_outputs_and_manifest
    render_post64_hourly_maps --> validate_outputs_and_manifest
    build_triggering_evidence_products --> validate_outputs_and_manifest
    style render_before_after_comparisons fill:#d5f5e3,stroke:#333,stroke-width:1px
    style validate_outputs_and_manifest fill:#d4e6f1,stroke:#333,stroke-width:1px
    style render_post64_hourly_maps fill:#f9e79f,stroke:#333,stroke-width:1px
    style render_whole_sequence_maps fill:#f5eef8,stroke:#333,stroke-width:1px
    style build_triggering_evidence_products fill:#d5f5e3,stroke:#333,stroke-width:1px
```
**Description:**
- `render_whole_sequence_maps`: Create the chronological 2 by 4 page series for the whole-sequence 2-hour and 6-hour time slices.
- `render_before_after_comparisons`: Create the before and after spatial overlay figures for Mw 6.4 and Mw 7.1 with fixed symbol meanings.
- `render_post64_hourly_maps`: Create the hour-by-hour post-Mw 6.4 map pages with fixed styling and chronological continuity.
- `build_triggering_evidence_products`: Summarize observational evidence for migration, branching, directional change, and new activation zones in machine-readable form.
- `validate_outputs_and_manifest`: Verify page counts, chronological ordering, file completeness, and cross-product consistency, then write the final manifest and validation report.