# Workflow Overview

## Top-Level Task Dependencies

```mermaid
graph TD
    01_region_geometry_assignment
    01_region_geometry_assignment --> 02_temporal_rate_energy_changepoints
    01_region_geometry_assignment --> 03_gridded_activation_ordering
    style 03_gridded_activation_ordering fill:#eaf2f8,stroke:#333,stroke-width:1px
    style 01_region_geometry_assignment fill:#f5eef8,stroke:#333,stroke-width:1px
    style 02_temporal_rate_energy_changepoints fill:#fcf3cf,stroke:#333,stroke-width:1px
```
**Description:**
- `01_region_geometry_assignment`: Build the fixed local metric geometry, assign events to corridors and diagnostic neighborhoods, and generate region-definition quality-control outputs.
- `02_temporal_rate_energy_changepoints`: Construct domain-scale rate and energy time series, extract timing diagnostics, and run Bayesian change-point analysis for corridor and neighborhood domains.
- `03_gridded_activation_ordering`: Compute gridded corridor and neighborhood activation statistics and resolve internal spatial ordering before the Mw 7.1 mainshock.


## Subtask Dependencies

#### 01_region_geometry_assignment
**Usage**: Build the fixed local metric geometry, assign events to corridors and diagnostic neighborhoods, and generate region-definition quality-control outputs.
```mermaid
graph TD
    load_and_standardize_inputs
    load_and_standardize_inputs --> build_local_metric_geometry
    load_and_standardize_inputs --> assign_events_and_compute_spatial_temporal_attributes
    build_local_metric_geometry --> assign_events_and_compute_spatial_temporal_attributes
    assign_events_and_compute_spatial_temporal_attributes --> generate_region_definition_diagnostics
    build_local_metric_geometry --> generate_region_definition_diagnostics
    style build_local_metric_geometry fill:#ebdef0,stroke:#333,stroke-width:1px
    style load_and_standardize_inputs fill:#d1f2eb,stroke:#333,stroke-width:1px
    style assign_events_and_compute_spatial_temporal_attributes fill:#d1f2eb,stroke:#333,stroke-width:1px
    style generate_region_definition_diagnostics fill:#f9ebea,stroke:#333,stroke-width:1px
```
**Description:**
- `load_and_standardize_inputs`: Load the relocated catalog, mainshock table, and fault traces and standardize required fields.
- `build_local_metric_geometry`: Construct one shared local metric coordinate system and fixed corridor and circle geometries for all spatial calculations.
- `assign_events_and_compute_spatial_temporal_attributes`: Compute projected coordinates, relative times, distances, along-strike and across-strike coordinates, and independent boolean domain masks for each event.
- `generate_region_definition_diagnostics`: Produce assignment summaries and diagnostic figures for corridor coverage, along-strike span, and unassigned-event distribution.

#### 02_temporal_rate_energy_changepoints
**Usage**: Construct domain-scale rate and energy time series, extract timing diagnostics, and run Bayesian change-point analysis for corridor and neighborhood domains.
```mermaid
graph TD
    build_domain_time_series
    build_domain_time_series --> derive_activation_timing_metrics
    build_domain_time_series --> detect_bayesian_change_points
    build_domain_time_series --> generate_temporal_comparison_outputs
    derive_activation_timing_metrics --> generate_temporal_comparison_outputs
    detect_bayesian_change_points --> generate_temporal_comparison_outputs
    style derive_activation_timing_metrics fill:#fdebd3,stroke:#333,stroke-width:1px
    style build_domain_time_series fill:#f9e79f,stroke:#333,stroke-width:1px
    style detect_bayesian_change_points fill:#f5eef8,stroke:#333,stroke-width:1px
    style generate_temporal_comparison_outputs fill:#e8daef,stroke:#333,stroke-width:1px
```
**Description:**
- `build_domain_time_series`: Aggregate event counts and energy into shared 30-minute and 1-hour bins for all required domains.
- `derive_activation_timing_metrics`: Compute post-Mw 6.4 timing metrics for first activity, sustained activation, strongest rate change, and peak rate.
- `detect_bayesian_change_points`: Apply one consistent Bayesian change-point method to rate and energy series for all domains and resolutions.
- `generate_temporal_comparison_outputs`: Produce comparative temporal figures and compact summary tables for corridor and neighborhood activation evolution.

#### 03_gridded_activation_ordering
**Usage**: Compute gridded corridor and neighborhood activation statistics and resolve internal spatial ordering before the Mw 7.1 mainshock.
```mermaid
graph TD
    build_fixed_grids_and_assign_events
    build_fixed_grids_and_assign_events --> compute_cellwise_activation_statistics
    compute_cellwise_activation_statistics --> aggregate_along_strike_ordering_metrics
    compute_cellwise_activation_statistics --> generate_gridded_activation_outputs
    aggregate_along_strike_ordering_metrics --> generate_gridded_activation_outputs
    style build_fixed_grids_and_assign_events fill:#fcf3cf,stroke:#333,stroke-width:1px
    style generate_gridded_activation_outputs fill:#d4e6f1,stroke:#333,stroke-width:1px
    style compute_cellwise_activation_statistics fill:#e8f8f5,stroke:#333,stroke-width:1px
    style aggregate_along_strike_ordering_metrics fill:#f5eef8,stroke:#333,stroke-width:1px
```
**Description:**
- `build_fixed_grids_and_assign_events`: Create fixed 0.5 km grids inside both corridors and both circular neighborhoods and assign events to cells while retaining zero-count cells.
- `compute_cellwise_activation_statistics`: Calculate cell-level count, rate, energy, first-activation timing, peak-rate timing, and geometric attributes for corridor and neighborhood grids.
- `aggregate_along_strike_ordering_metrics`: Summarize cell statistics into along-strike bins and quantify internal activation ordering within each corridor.
- `generate_gridded_activation_outputs`: Produce cumulative-count maps, first-activation maps, time-versus-along-strike heatmaps, and export cell-level and along-strike summary tables.