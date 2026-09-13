# Workflow Overview

## Top-Level Task Dependencies

```mermaid
graph TD
    01_reference_framework
    01_reference_framework --> 02_kde_migration_analysis
    01_reference_framework --> 03_morphology_and_synthesis
    02_kde_migration_analysis --> 03_morphology_and_synthesis
    style 02_kde_migration_analysis fill:#d1f2eb,stroke:#333,stroke-width:1px
    style 03_morphology_and_synthesis fill:#f5eef8,stroke:#333,stroke-width:1px
    style 01_reference_framework fill:#eaf2f8,stroke:#333,stroke-width:1px
```
**Description:**
- `01_reference_framework`: Build the shared inter-mainshock dataset, interval tables, and spatial metadata for Ridgecrest analyses.
- `02_kde_migration_analysis`: Compute fixed-bandwidth interval KDEs, generate stage panel figures, and track hotspot migration between the two mainshocks.
- `03_morphology_and_synthesis`: Compute hourly convex hull and alpha-shape evolution, then summarize focusing, defocusing, and bifurcation diagnostics.


## Subtask Dependencies

#### 01_reference_framework
**Usage**: Build the shared inter-mainshock dataset, interval tables, and spatial metadata for Ridgecrest analyses.
```mermaid
graph TD
    load_and_clean_inputs
    load_and_clean_inputs --> define_intervals_and_spatial_reference
    load_and_clean_inputs --> validate_and_export_shared_products
    define_intervals_and_spatial_reference --> validate_and_export_shared_products
    style load_and_clean_inputs fill:#fdebd0,stroke:#333,stroke-width:1px
    style validate_and_export_shared_products fill:#fdebd3,stroke:#333,stroke-width:1px
    style define_intervals_and_spatial_reference fill:#f6ddcc,stroke:#333,stroke-width:1px
```
**Description:**
- `load_and_clean_inputs`: Read the catalog, mainshock table, and fault traces, then parse and validate required fields.
- `define_intervals_and_spatial_reference`: Create KDE and morphology interval tables, common map extent, and one local projected CRS.
- `validate_and_export_shared_products`: Save reusable shared outputs and verify interval completeness and metadata consistency.

#### 02_kde_migration_analysis
**Usage**: Compute fixed-bandwidth interval KDEs, generate stage panel figures, and track hotspot migration between the two mainshocks.
```mermaid
graph TD
    compute_interval_kde_and_hotspots
    compute_interval_kde_and_hotspots --> generate_kde_panel_figures
    compute_interval_kde_and_hotspots --> compute_hotspot_migration_diagnostics
    style generate_kde_panel_figures fill:#d6eaf8,stroke:#333,stroke-width:1px
    style compute_hotspot_migration_diagnostics fill:#d5f5e3,stroke:#333,stroke-width:1px
    style compute_interval_kde_and_hotspots fill:#e8daef,stroke:#333,stroke-width:1px
```
**Description:**
- `compute_interval_kde_and_hotspots`: Run interval-wise KDE on a common grid and extract the primary hotspot for each interval.
- `generate_kde_panel_figures`: Assemble paginated 2_by_4 KDE map panels with shared extent, normalization, and overlays.
- `compute_hotspot_migration_diagnostics`: Build stage-wise hotspot paths and supporting migration metrics relative to Mw 7.1 and mapped faults.

#### 03_morphology_and_synthesis
**Usage**: Compute hourly convex hull and alpha-shape evolution, then summarize focusing, defocusing, and bifurcation diagnostics.
```mermaid
graph TD
    compute_hourly_geometric_envelopes
    compute_hourly_geometric_envelopes --> generate_morphology_evolution_figures
    compute_hourly_geometric_envelopes --> build_spatiotemporal_synthesis
    style build_spatiotemporal_synthesis fill:#fef9e7,stroke:#333,stroke-width:1px
    style compute_hourly_geometric_envelopes fill:#e8daef,stroke:#333,stroke-width:1px
    style generate_morphology_evolution_figures fill:#fcf3cf,stroke:#333,stroke-width:1px
```
**Description:**
- `compute_hourly_geometric_envelopes`: Derive hourly convex hull and alpha-shape boundaries and interval-level geometric metrics.
- `generate_morphology_evolution_figures`: Plot all valid convex hull and alpha-shape boundaries in a common frame with time-encoded colors.
- `build_spatiotemporal_synthesis`: Combine hotspot and geometry diagnostics into rule-based evidence summaries for focusing, spreading, and bifurcation.