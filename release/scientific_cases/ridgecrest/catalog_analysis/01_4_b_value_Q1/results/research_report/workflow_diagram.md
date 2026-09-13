# Workflow Overview

## Top-Level Task Dependencies

```mermaid
graph TD
    01_interevent_bvalue_workflow
    style 01_interevent_bvalue_workflow fill:#fcf3cf,stroke:#333,stroke-width:1px
```
**Description:**
- `01_interevent_bvalue_workflow`: Execute the full interevent sliding-window b-value analysis for the Mw 6.4 and Mw 7.1 core regions, including cleaning, assignment, estimation, contrasts, figures, and validation.


## Subtask Dependencies

#### 01_interevent_bvalue_workflow
**Usage**: Execute the full interevent sliding-window b-value analysis for the Mw 6.4 and Mw 7.1 core regions, including cleaning, assignment, estimation, contrasts, figures, and validation.
```mermaid
graph TD
    load_and_filter_catalogs
    load_and_filter_catalogs --> identify_and_remove_separator_event
    identify_and_remove_separator_event --> project_coordinates_and_assign_cores
    load_and_filter_catalogs --> project_coordinates_and_assign_cores
    identify_and_remove_separator_event --> infer_magnitude_discretization
    identify_and_remove_separator_event --> build_sliding_windows_and_compute_bvalues
    project_coordinates_and_assign_cores --> build_sliding_windows_and_compute_bvalues
    load_and_filter_catalogs --> build_sliding_windows_and_compute_bvalues
    infer_magnitude_discretization --> build_sliding_windows_and_compute_bvalues
    build_sliding_windows_and_compute_bvalues --> compute_temporal_contrasts_and_prepost_summaries
    identify_and_remove_separator_event --> compute_temporal_contrasts_and_prepost_summaries
    identify_and_remove_separator_event --> generate_tables_and_figures
    project_coordinates_and_assign_cores --> generate_tables_and_figures
    infer_magnitude_discretization --> generate_tables_and_figures
    build_sliding_windows_and_compute_bvalues --> generate_tables_and_figures
    compute_temporal_contrasts_and_prepost_summaries --> generate_tables_and_figures
    identify_and_remove_separator_event --> validate_outputs_and_save_reproducibility_metadata
    project_coordinates_and_assign_cores --> validate_outputs_and_save_reproducibility_metadata
    infer_magnitude_discretization --> validate_outputs_and_save_reproducibility_metadata
    build_sliding_windows_and_compute_bvalues --> validate_outputs_and_save_reproducibility_metadata
    compute_temporal_contrasts_and_prepost_summaries --> validate_outputs_and_save_reproducibility_metadata
    generate_tables_and_figures --> validate_outputs_and_save_reproducibility_metadata
    style identify_and_remove_separator_event fill:#d1f2eb,stroke:#333,stroke-width:1px
    style build_sliding_windows_and_compute_bvalues fill:#d4e6f1,stroke:#333,stroke-width:1px
    style project_coordinates_and_assign_cores fill:#d4e6f1,stroke:#333,stroke-width:1px
    style compute_temporal_contrasts_and_prepost_summaries fill:#d5f5e3,stroke:#333,stroke-width:1px
    style infer_magnitude_discretization fill:#d6eaf8,stroke:#333,stroke-width:1px
    style validate_outputs_and_save_reproducibility_metadata fill:#eaf2f8,stroke:#333,stroke-width:1px
    style generate_tables_and_figures fill:#e8daef,stroke:#333,stroke-width:1px
    style load_and_filter_catalogs fill:#d5f5e3,stroke:#333,stroke-width:1px
```
**Description:**
- `load_and_filter_catalogs`: Load the relocated catalog and mainshock table, identify the Mw 6.4 and Mw 7.1 events, isolate the strict interevent period, and exclude both mainshocks.
- `identify_and_remove_separator_event`: Identify the fixed M5.37 separator event, record its metadata and elapsed time since Mw 6.4, and remove it from all analysis inputs.
- `project_coordinates_and_assign_cores`: Project events to a local metric CRS, compute horizontal distances to both hypocenters, assign events to primary and sensitivity cores, and resolve overlap by nearest-hypocenter assignment when needed.
- `infer_magnitude_discretization`: Infer the global magnitude bin width from stable non-zero spacing in sorted unique magnitudes and record the selection metadata.
- `build_sliding_windows_and_compute_bvalues`: Construct chronological sliding event windows for each core and radius, then compute fixed-Mc and dynamic-Mc b-values, bootstrap uncertainty, Mc diagnostics, and reliability labels.
- `compute_temporal_contrasts_and_prepost_summaries`: Match Mw 7.1 and Mw 6.4 window estimates by nearest center time, compute b-value contrasts with uncertainty, and summarize pre- and post-separator behavior without fitting a trend model.
- `generate_tables_and_figures`: Save required CSV tables, figure-source tables, and the full figure suite with separator and Mw 7.1 endpoint markers on all time-series panels.
- `validate_outputs_and_save_reproducibility_metadata`: Validate catalog filtering, separator exclusion, window construction, statistical outputs, and figure completeness, then write run metadata, inventory, logs, and failure evidence if needed.