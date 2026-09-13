# Workflow Overview

## Top-Level Task Dependencies

```mermaid
graph TD
    01_ridgecrest_bvalue_contrast_analysis
    style 01_ridgecrest_bvalue_contrast_analysis fill:#fdebd3,stroke:#333,stroke-width:1px
```
**Description:**
- `01_ridgecrest_bvalue_contrast_analysis`: Execute the complete Ridgecrest fixed-window b-value contrast workflow from catalog harmonization through diagnostics, figures, and validation.


## Subtask Dependencies

#### 01_ridgecrest_bvalue_contrast_analysis
**Usage**: Execute the complete Ridgecrest fixed-window b-value contrast workflow from catalog harmonization through diagnostics, figures, and validation.
```mermaid
graph TD
    ingest_and_clean_catalogs
    ingest_and_clean_catalogs --> define_time_controls_and_separator
    ingest_and_clean_catalogs --> infer_magnitude_discretization
    ingest_and_clean_catalogs --> build_metric_projection_and_radius_masks
    build_metric_projection_and_radius_masks --> quantify_overlap_and_assign_local_cores
    ingest_and_clean_catalogs --> assemble_subset_matrix
    define_time_controls_and_separator --> assemble_subset_matrix
    quantify_overlap_and_assign_local_cores --> assemble_subset_matrix
    assemble_subset_matrix --> estimate_mc_for_all_subsets
    infer_magnitude_discretization --> estimate_mc_for_all_subsets
    assemble_subset_matrix --> compute_bvalues_and_bootstrap_uncertainty
    estimate_mc_for_all_subsets --> compute_bvalues_and_bootstrap_uncertainty
    infer_magnitude_discretization --> compute_bvalues_and_bootstrap_uncertainty
    compute_bvalues_and_bootstrap_uncertainty --> derive_bvalue_contrasts
    ingest_and_clean_catalogs --> generate_tables_figures_and_validation
    define_time_controls_and_separator --> generate_tables_figures_and_validation
    build_metric_projection_and_radius_masks --> generate_tables_figures_and_validation
    infer_magnitude_discretization --> generate_tables_figures_and_validation
    quantify_overlap_and_assign_local_cores --> generate_tables_figures_and_validation
    compute_bvalues_and_bootstrap_uncertainty --> generate_tables_figures_and_validation
    derive_bvalue_contrasts --> generate_tables_figures_and_validation
    estimate_mc_for_all_subsets --> generate_tables_figures_and_validation
    assemble_subset_matrix --> generate_tables_figures_and_validation
    style ingest_and_clean_catalogs fill:#ebdef0,stroke:#333,stroke-width:1px
    style infer_magnitude_discretization fill:#fdebd3,stroke:#333,stroke-width:1px
    style derive_bvalue_contrasts fill:#d4e6f1,stroke:#333,stroke-width:1px
    style define_time_controls_and_separator fill:#fdebd3,stroke:#333,stroke-width:1px
    style assemble_subset_matrix fill:#fadbd8,stroke:#333,stroke-width:1px
    style compute_bvalues_and_bootstrap_uncertainty fill:#d5f5e3,stroke:#333,stroke-width:1px
    style build_metric_projection_and_radius_masks fill:#f5eef8,stroke:#333,stroke-width:1px
    style quantify_overlap_and_assign_local_cores fill:#e8daef,stroke:#333,stroke-width:1px
    style generate_tables_figures_and_validation fill:#fdebd0,stroke:#333,stroke-width:1px
    style estimate_mc_for_all_subsets fill:#fadbd8,stroke:#333,stroke-width:1px
```
**Description:**
- `ingest_and_clean_catalogs`: Read the interevent, background, and mainshock files, harmonize schemas, clean invalid rows, and preserve traceable event identifiers.
- `define_time_controls_and_separator`: Identify the Mw 6.4 and Mw 7.1 origin times, locate the separator event metadata, and define strict interevent windows with required exclusions.
- `infer_magnitude_discretization`: Infer catalog magnitude discretization for Mc and b-value estimation and record any harmonized comparison increment.
- `build_metric_projection_and_radius_masks`: Project events and hypocenters to a local metric CRS, compute horizontal distances, and construct local core memberships for all requested radii.
- `quantify_overlap_and_assign_local_cores`: Compute raw overlap diagnostics for each radius and create exclusive nearest-hypocenter local assignments when overlap occurs.
- `assemble_subset_matrix`: Build the full matrix of background, interevent regional, and local-core subsets across windows, radii, and assignment modes.
- `estimate_mc_for_all_subsets`: Compute automatic and conservative magnitude of completeness values for every supported subset using maximum curvature.
- `compute_bvalues_and_bootstrap_uncertainty`: Estimate b-values and supporting statistics for fixed, automatic, and conservative Mc modes and bootstrap uncertainty summaries in parallel.
- `derive_bvalue_contrasts`: Compute requested fixed-window b-value contrasts and bootstrap difference intervals for core, regional, and temporal comparisons.
- `generate_tables_figures_and_validation`: Write all required CSV outputs, create diagnostic figures, save reproducibility metadata, and validate that required fixed-Mc products are present.