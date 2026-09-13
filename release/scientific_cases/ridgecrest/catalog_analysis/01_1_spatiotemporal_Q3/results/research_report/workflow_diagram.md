# Workflow Overview

## Top-Level Task Dependencies

```mermaid
graph TD
    01_ridgecrest_spatiotemporal_evolution
    style 01_ridgecrest_spatiotemporal_evolution fill:#fdebd3,stroke:#333,stroke-width:1px
```
**Description:**
- `01_ridgecrest_spatiotemporal_evolution`: Build the inter-mainshock catalog, compute KDE and morphology diagnostics, generate figures, and validate merged outputs for the Ridgecrest sequence.


## Subtask Dependencies

#### 01_ridgecrest_spatiotemporal_evolution
**Usage**: Build the inter-mainshock catalog, compute KDE and morphology diagnostics, generate figures, and validate merged outputs for the Ridgecrest sequence.
```mermaid
graph TD
    build_working_catalog_and_intervals
    build_working_catalog_and_intervals --> compute_kde_and_hotspot_evolution
    compute_kde_and_hotspot_evolution --> generate_kde_panels_and_hotspot_paths
    build_working_catalog_and_intervals --> generate_kde_panels_and_hotspot_paths
    build_working_catalog_and_intervals --> compute_hourly_morphology
    compute_hourly_morphology --> generate_morphology_overlay_figures
    build_working_catalog_and_intervals --> generate_morphology_overlay_figures
    compute_kde_and_hotspot_evolution --> integrate_diagnostics_and_validate_outputs
    compute_hourly_morphology --> integrate_diagnostics_and_validate_outputs
    build_working_catalog_and_intervals --> integrate_diagnostics_and_validate_outputs
    style compute_kde_and_hotspot_evolution fill:#f2f4f4,stroke:#333,stroke-width:1px
    style compute_hourly_morphology fill:#d6eaf8,stroke:#333,stroke-width:1px
    style integrate_diagnostics_and_validate_outputs fill:#d5f5e3,stroke:#333,stroke-width:1px
    style build_working_catalog_and_intervals fill:#d4e6f1,stroke:#333,stroke-width:1px
    style generate_morphology_overlay_figures fill:#fdebd3,stroke:#333,stroke-width:1px
    style generate_kde_panels_and_hotspot_paths fill:#fcf3cf,stroke:#333,stroke-width:1px
```
**Description:**
- `build_working_catalog_and_intervals`: Read the catalog and mainshock tables, clean records, subset the inter-mainshock window, and define shared interval schemes and spatial reference.
- `compute_kde_and_hotspot_evolution`: Compute fixed-bandwidth KDE on a common grid for all KDE intervals, extract hotspot maxima, and save interval summaries and manifests.
- `generate_kde_panels_and_hotspot_paths`: Create paginated 2x4 KDE panel figures for both stages and plot hotspot migration paths with mainshock overlays.
- `compute_hourly_morphology`: Compute hourly convex hull and alpha-shape geometries, extract morphology metrics, and serialize boundary coordinates.
- `generate_morphology_overlay_figures`: Plot all hourly convex hull and alpha-shape boundaries in a common frame using time-encoded boundary colors and mainshock overlays.
- `integrate_diagnostics_and_validate_outputs`: Merge KDE and morphology diagnostics, assign machine-readable interpretation labels, and record validation and run logs.