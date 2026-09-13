# Workflow Overview

## Top-Level Task Dependencies

```mermaid
graph TD
    01_grid_onset_analysis
    01_grid_onset_analysis --> 02_fault_segment_activation
    01_grid_onset_analysis --> 03_triggering_style_diagnostics
    02_fault_segment_activation --> 03_triggering_style_diagnostics
    style 03_triggering_style_diagnostics fill:#fcf3cf,stroke:#333,stroke-width:1px
    style 01_grid_onset_analysis fill:#f9e79f,stroke:#333,stroke-width:1px
    style 02_fault_segment_activation fill:#f2f4f4,stroke:#333,stroke-width:1px
```
**Description:**
- `01_grid_onset_analysis`: Load and validate Ridgecrest inputs, define the common space-time domain, build the 1 km grid, and compute grid-cell activation onset products.
- `02_fault_segment_activation`: Build the fault-segment backbone, associate earthquakes to segments, compute segment activation time series, and generate fault-based activation figures.
- `03_triggering_style_diagnostics`: Quantify synchrony, along-fault cascading, cross-fault complexity, and the Mw 7.1 nucleation-area activation history and package validated deliverables.


## Subtask Dependencies

#### 01_grid_onset_analysis
**Usage**: Load and validate Ridgecrest inputs, define the common space-time domain, build the 1 km grid, and compute grid-cell activation onset products.
```mermaid
graph TD
    ingest_and_validate_inputs
    ingest_and_validate_inputs --> define_common_domain
    define_common_domain --> construct_grid_and_time_series
    construct_grid_and_time_series --> detect_grid_cell_onset
    define_common_domain --> detect_grid_cell_onset
    define_common_domain --> generate_grid_outputs
    construct_grid_and_time_series --> generate_grid_outputs
    detect_grid_cell_onset --> generate_grid_outputs
    style construct_grid_and_time_series fill:#d5f5e3,stroke:#333,stroke-width:1px
    style detect_grid_cell_onset fill:#fdebd0,stroke:#333,stroke-width:1px
    style ingest_and_validate_inputs fill:#f6ddcc,stroke:#333,stroke-width:1px
    style generate_grid_outputs fill:#f9ebea,stroke:#333,stroke-width:1px
    style define_common_domain fill:#e8f8f5,stroke:#333,stroke-width:1px
```
**Description:**
- `ingest_and_validate_inputs`: Load the catalog, mainshock table, and fault polylines and validate required fields and malformed records.
- `define_common_domain`: Define the Mw 6.4 to Mw 7.1 time window, project coordinates to a local metric system, and build the buffered study region.
- `construct_grid_and_time_series`: Discretize the buffered region into 1 km cells, assign events to cells, and build 30-minute count-rate-cumulative series.
- `detect_grid_cell_onset`: Apply the fixed sustained-activation rule to assign onset times and confidence classes to occupied grid cells.
- `generate_grid_outputs`: Save reusable tables and figures for the study-domain overview and grid-based onset analysis.

#### 02_fault_segment_activation
**Usage**: Build the fault-segment backbone, associate earthquakes to segments, compute segment activation time series, and generate fault-based activation figures.
```mermaid
graph TD
    discretize_fault_backbone
    discretize_fault_backbone --> associate_events_to_segments
    associate_events_to_segments --> build_segment_time_series_and_activation
    discretize_fault_backbone --> build_segment_time_series_and_activation
    discretize_fault_backbone --> generate_fault_activation_outputs
    associate_events_to_segments --> generate_fault_activation_outputs
    build_segment_time_series_and_activation --> generate_fault_activation_outputs
    discretize_fault_backbone --> validate_fault_products
    associate_events_to_segments --> validate_fault_products
    build_segment_time_series_and_activation --> validate_fault_products
    generate_fault_activation_outputs --> validate_fault_products
    style discretize_fault_backbone fill:#eaf2f8,stroke:#333,stroke-width:1px
    style associate_events_to_segments fill:#ebdef0,stroke:#333,stroke-width:1px
    style build_segment_time_series_and_activation fill:#fef9e7,stroke:#333,stroke-width:1px
    style generate_fault_activation_outputs fill:#f5eef8,stroke:#333,stroke-width:1px
    style validate_fault_products fill:#fcf3cf,stroke:#333,stroke-width:1px
```
**Description:**
- `discretize_fault_backbone`: Convert mapped fault polylines into contiguous analyzable segments and compute segment geometry attributes.
- `associate_events_to_segments`: Compute nearest projected point-to-segment distances and assign events within 3 km to their nearest fault segments.
- `build_segment_time_series_and_activation`: Aggregate associated events into 30-minute segment time series and assign activation times using the fixed count threshold.
- `generate_fault_activation_outputs`: Produce fault-centered maps, activation-density products, and reusable summary tables from segment activation results.
- `validate_fault_products`: Validate non-empty fault-segment outputs, association coverage, and consistency of segment activation fields.

#### 03_triggering_style_diagnostics
**Usage**: Quantify synchrony, along-fault cascading, cross-fault complexity, and the Mw 7.1 nucleation-area activation history and package validated deliverables.
```mermaid
graph TD
    compute_system_and_fault_metrics
    evaluate_mw71_nucleation_context
    compute_system_and_fault_metrics --> generate_triggering_diagnostic_figures
    evaluate_mw71_nucleation_context --> generate_triggering_diagnostic_figures
    compute_system_and_fault_metrics --> validate_and_package_deliverables
    evaluate_mw71_nucleation_context --> validate_and_package_deliverables
    style validate_and_package_deliverables fill:#fdebd0,stroke:#333,stroke-width:1px
    style generate_triggering_diagnostic_figures fill:#ebdef0,stroke:#333,stroke-width:1px
    style compute_system_and_fault_metrics fill:#eaf2f8,stroke:#333,stroke-width:1px
    style evaluate_mw71_nucleation_context fill:#e8f8f5,stroke:#333,stroke-width:1px
```
**Description:**
- `compute_system_and_fault_metrics`: Derive system-wide synchrony metrics, per-fault propagation metrics, and cross-fault complexity diagnostics from grid and segment activation products.
- `evaluate_mw71_nucleation_context`: Compare the activation timing of the segment nearest the Mw 7.1 epicenter with its local neighborhood and the full system.
- `generate_triggering_diagnostic_figures`: Create the integrated diagnostic figures needed to assess synchronous, staged, jump-like, or complex activation behavior.
- `validate_and_package_deliverables`: Validate cross-step consistency, summarize run parameters and counts, and package reusable outputs from all scripts.