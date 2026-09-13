# Workflow Overview

## Top-Level Task Dependencies

```mermaid
graph TD
    01_catalog_windows_and_time_colored_maps
    01_catalog_windows_and_time_colored_maps --> 02_grid_onset_and_trigger_diagnostics
    style 01_catalog_windows_and_time_colored_maps fill:#f6ddcc,stroke:#333,stroke-width:1px
    style 02_grid_onset_and_trigger_diagnostics fill:#f5eef8,stroke:#333,stroke-width:1px
```
**Description:**
- `01_catalog_windows_and_time_colored_maps`: Load and validate the Ridgecrest catalog, derive relative-time and projected-coordinate fields, create analysis windows, and generate time-colored epicenter products with bin summaries.
- `02_grid_onset_and_trigger_diagnostics`: Build the 0.5 km grid, estimate sustained-activation onset times, map onset patterns, and compute Mw 6.4-to-Mw 7.1 trigger diagnostics.


## Subtask Dependencies

#### 01_catalog_windows_and_time_colored_maps
**Usage**: Load and validate the Ridgecrest catalog, derive relative-time and projected-coordinate fields, create analysis windows, and generate time-colored epicenter products with bin summaries.
```mermaid
graph TD
    load_and_validate_inputs
    load_and_validate_inputs --> derive_relative_time_and_projection
    derive_relative_time_and_projection --> extract_analysis_windows
    load_and_validate_inputs --> extract_analysis_windows
    extract_analysis_windows --> assign_discrete_time_bins
    load_and_validate_inputs --> assign_discrete_time_bins
    assign_discrete_time_bins --> generate_time_colored_point_clouds
    load_and_validate_inputs --> generate_time_colored_point_clouds
    assign_discrete_time_bins --> summarize_time_bin_spatial_patterns
    derive_relative_time_and_projection --> summarize_time_bin_spatial_patterns
    load_and_validate_inputs --> summarize_time_bin_spatial_patterns
    style extract_analysis_windows fill:#f9e79f,stroke:#333,stroke-width:1px
    style assign_discrete_time_bins fill:#f5eef8,stroke:#333,stroke-width:1px
    style derive_relative_time_and_projection fill:#d5f5e3,stroke:#333,stroke-width:1px
    style load_and_validate_inputs fill:#f5eef8,stroke:#333,stroke-width:1px
    style generate_time_colored_point_clouds fill:#eaf2f8,stroke:#333,stroke-width:1px
    style summarize_time_bin_spatial_patterns fill:#d5f5e3,stroke:#333,stroke-width:1px
```
**Description:**
- `load_and_validate_inputs`: Read the catalog and mainshock tables, validate required columns, and verify unique Mw 6.4 and Mw 7.1 reference events.
- `derive_relative_time_and_projection`: Compute relative times from Mw 6.4 and project epicenters to local Cartesian coordinates for distance-based analyses.
- `extract_analysis_windows`: Build the short and long post-Mw 6.4 event subsets and summarize their temporal and spatial extents.
- `assign_discrete_time_bins`: Assign fixed categorical time bins for the short and long windows without within-bin interpolation.
- `generate_time_colored_point_clouds`: Create categorical longitude-latitude epicenter scatter plots for both time windows with mainshock overlays.
- `summarize_time_bin_spatial_patterns`: Compute descriptive spatial summaries for each time bin to support assessment of temporal layering and migration.

#### 02_grid_onset_and_trigger_diagnostics
**Usage**: Build the 0.5 km grid, estimate sustained-activation onset times, map onset patterns, and compute Mw 6.4-to-Mw 7.1 trigger diagnostics.
```mermaid
graph TD
    construct_grid_and_assign_cells
    construct_grid_and_assign_cells --> aggregate_local_seismicity_rates
    aggregate_local_seismicity_rates --> detect_sustained_activation_onset
    construct_grid_and_assign_cells --> map_onset_time_and_compute_geometry
    detect_sustained_activation_onset --> map_onset_time_and_compute_geometry
    detect_sustained_activation_onset --> evaluate_mw64_to_mw71_trigger_patterns
    map_onset_time_and_compute_geometry --> evaluate_mw64_to_mw71_trigger_patterns
    construct_grid_and_assign_cells --> validate_outputs_and_capture_failure_evidence
    aggregate_local_seismicity_rates --> validate_outputs_and_capture_failure_evidence
    detect_sustained_activation_onset --> validate_outputs_and_capture_failure_evidence
    evaluate_mw64_to_mw71_trigger_patterns --> validate_outputs_and_capture_failure_evidence
    style validate_outputs_and_capture_failure_evidence fill:#f2f4f4,stroke:#333,stroke-width:1px
    style map_onset_time_and_compute_geometry fill:#fef9e7,stroke:#333,stroke-width:1px
    style detect_sustained_activation_onset fill:#d1f2eb,stroke:#333,stroke-width:1px
    style evaluate_mw64_to_mw71_trigger_patterns fill:#d5f5e3,stroke:#333,stroke-width:1px
    style construct_grid_and_assign_cells fill:#f5eef8,stroke:#333,stroke-width:1px
    style aggregate_local_seismicity_rates fill:#ebdef0,stroke:#333,stroke-width:1px
```
**Description:**
- `construct_grid_and_assign_cells`: Define the 0.5 km study grid from the long-window catalog extent and assign events to spatial cells and 30-minute bins.
- `aggregate_local_seismicity_rates`: Build per-cell 30-minute count series and occupancy summaries while preserving zero-count bins.
- `detect_sustained_activation_onset`: Apply one uniform sustained-rate rule to estimate onset time and quality flags for each occupied cell.
- `map_onset_time_and_compute_geometry`: Create the onset-time spatial map and compute geometric metrics relative to the Mw 6.4-Mw 7.1 frame.
- `evaluate_mw64_to_mw71_trigger_patterns`: Compare Mw 6.4 vicinity, connecting corridor, and Mw 7.1 vicinity activation histories to classify the trigger style.
- `validate_outputs_and_capture_failure_evidence`: Verify merged scientific outputs, check onset coverage and ranges, and record any failures or dropped cells.