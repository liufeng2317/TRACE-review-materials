# Workflow Overview

## Top-Level Task Dependencies

```mermaid
graph TD
    01_ridgecrest_directional_ripley_analysis
    style 01_ridgecrest_directional_ripley_analysis fill:#f9ebea,stroke:#333,stroke-width:1px
```
**Description:**
- `01_ridgecrest_directional_ripley_analysis`: Build the Ridgecrest analysis dataset, compute directional Ripley K and L statistics through time, derive transition metrics, generate the requested figures, and export validated machine-readable outputs.


## Subtask Dependencies

#### 01_ridgecrest_directional_ripley_analysis
**Usage**: Build the Ridgecrest analysis dataset, compute directional Ripley K and L statistics through time, derive transition metrics, generate the requested figures, and export validated machine-readable outputs.
```mermaid
graph TD
    load_and_validate_inputs
    load_and_validate_inputs --> build_analysis_windows_and_coordinates
    build_analysis_windows_and_coordinates --> define_study_window_and_scale_selection
    build_analysis_windows_and_coordinates --> compute_interval_directional_ripley_statistics
    define_study_window_and_scale_selection --> compute_interval_directional_ripley_statistics
    compute_interval_directional_ripley_statistics --> derive_transition_metrics
    build_analysis_windows_and_coordinates --> derive_transition_metrics
    compute_interval_directional_ripley_statistics --> generate_time_direction_heatmap
    derive_transition_metrics --> generate_time_direction_heatmap
    build_analysis_windows_and_coordinates --> generate_time_direction_heatmap
    build_analysis_windows_and_coordinates --> generate_map_and_rose_figures
    define_study_window_and_scale_selection --> generate_map_and_rose_figures
    compute_interval_directional_ripley_statistics --> generate_map_and_rose_figures
    build_analysis_windows_and_coordinates --> validate_and_export_outputs
    compute_interval_directional_ripley_statistics --> validate_and_export_outputs
    generate_map_and_rose_figures --> validate_and_export_outputs
    define_study_window_and_scale_selection --> validate_and_export_outputs
    load_and_validate_inputs --> validate_and_export_outputs
    style validate_and_export_outputs fill:#e8f8f5,stroke:#333,stroke-width:1px
    style build_analysis_windows_and_coordinates fill:#d6eaf8,stroke:#333,stroke-width:1px
    style generate_time_direction_heatmap fill:#d4e6f1,stroke:#333,stroke-width:1px
    style generate_map_and_rose_figures fill:#d6eaf8,stroke:#333,stroke-width:1px
    style load_and_validate_inputs fill:#d4e6f1,stroke:#333,stroke-width:1px
    style derive_transition_metrics fill:#d5f5e3,stroke:#333,stroke-width:1px
    style compute_interval_directional_ripley_statistics fill:#f5eef8,stroke:#333,stroke-width:1px
    style define_study_window_and_scale_selection fill:#d4e6d4,stroke:#333,stroke-width:1px
```
**Description:**
- `load_and_validate_inputs`: Load the catalog, mainshock table, and fault polylines and validate their schema and required fields.
- `build_analysis_windows_and_coordinates`: Define the fixed analysis window, assign 30-minute intervals, create representative windows, and project coordinates for pair calculations.
- `define_study_window_and_scale_selection`: Define the fixed study region, normalization protocol, candidate radii, and characteristic radius used across all directional analyses.
- `compute_interval_directional_ripley_statistics`: Compute interval-wise sector-based directional Ripley K and L statistics in parallel and summarize dominant directional features.
- `derive_transition_metrics`: Derive temporal directional metrics and compare them with mainshock-to-mainshock alignment and fault orientation families.
- `generate_time_direction_heatmap`: Build the requested time-direction heatmap and aligned support timeline products from the characteristic-scale directional matrix.
- `generate_map_and_rose_figures`: Create the three requested 2x4 map-plus-polar-rose figure families and compute exact window-level directional summaries where needed.
- `validate_and_export_outputs`: Validate merged dimensions and consistency across all products and export reusable machine-readable tables and logs.