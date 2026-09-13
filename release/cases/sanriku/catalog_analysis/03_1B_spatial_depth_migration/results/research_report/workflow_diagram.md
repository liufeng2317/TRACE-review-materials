# Workflow Overview

## Top-Level Task Dependencies

```mermaid
graph TD
    01_m1_m3_spatial_depth_screening
    style 01_m1_m3_spatial_depth_screening fill:#f9ebea,stroke:#333,stroke-width:1px
```
**Description:**
- `01_m1_m3_spatial_depth_screening`: Recompute the M1-M3 local-system spatial, depth, burst, centroid, migration, robustness, and figure diagnostics in one cohesive catalog-analysis script.


## Subtask Dependencies

#### 01_m1_m3_spatial_depth_screening
**Usage**: Recompute the M1-M3 local-system spatial, depth, burst, centroid, migration, robustness, and figure diagnostics in one cohesive catalog-analysis script.
```mermaid
graph TD
    load_catalog_and_anchor_metadata
    load_catalog_and_anchor_metadata --> build_m1_m3_geometry_framework
    build_m1_m3_geometry_framework --> assign_temporal_phases_and_detect_bursts
    load_catalog_and_anchor_metadata --> assign_temporal_phases_and_detect_bursts
    build_m1_m3_geometry_framework --> summarize_phase_and_burst_spatial_depth_patterns
    assign_temporal_phases_and_detect_bursts --> summarize_phase_and_burst_spatial_depth_patterns
    build_m1_m3_geometry_framework --> evaluate_centroid_evolution_and_migration_diagnostics
    assign_temporal_phases_and_detect_bursts --> evaluate_centroid_evolution_and_migration_diagnostics
    summarize_phase_and_burst_spatial_depth_patterns --> evaluate_centroid_evolution_and_migration_diagnostics
    build_m1_m3_geometry_framework --> analyze_depth_domains_and_large_event_consistency
    assign_temporal_phases_and_detect_bursts --> analyze_depth_domains_and_large_event_consistency
    load_catalog_and_anchor_metadata --> analyze_depth_domains_and_large_event_consistency
    summarize_phase_and_burst_spatial_depth_patterns --> run_robustness_checks_and_followup_screening
    evaluate_centroid_evolution_and_migration_diagnostics --> run_robustness_checks_and_followup_screening
    analyze_depth_domains_and_large_event_consistency --> run_robustness_checks_and_followup_screening
    load_catalog_and_anchor_metadata --> run_robustness_checks_and_followup_screening
    build_m1_m3_geometry_framework --> generate_figures_and_final_structured_outputs
    summarize_phase_and_burst_spatial_depth_patterns --> generate_figures_and_final_structured_outputs
    evaluate_centroid_evolution_and_migration_diagnostics --> generate_figures_and_final_structured_outputs
    analyze_depth_domains_and_large_event_consistency --> generate_figures_and_final_structured_outputs
    run_robustness_checks_and_followup_screening --> generate_figures_and_final_structured_outputs
    load_catalog_and_anchor_metadata --> generate_figures_and_final_structured_outputs
    style load_catalog_and_anchor_metadata fill:#fdebd0,stroke:#333,stroke-width:1px
    style run_robustness_checks_and_followup_screening fill:#ebdef0,stroke:#333,stroke-width:1px
    style summarize_phase_and_burst_spatial_depth_patterns fill:#d4e6f1,stroke:#333,stroke-width:1px
    style analyze_depth_domains_and_large_event_consistency fill:#d1f2eb,stroke:#333,stroke-width:1px
    style assign_temporal_phases_and_detect_bursts fill:#f5eef8,stroke:#333,stroke-width:1px
    style build_m1_m3_geometry_framework fill:#ebdef0,stroke:#333,stroke-width:1px
    style generate_figures_and_final_structured_outputs fill:#fcf3cf,stroke:#333,stroke-width:1px
    style evaluate_centroid_evolution_and_migration_diagnostics fill:#f2f4f4,stroke:#333,stroke-width:1px
```
**Description:**
- `load_catalog_and_anchor_metadata`: Load the relocated catalog and main-earthquake metadata and identify M1, M2, and M3 anchors.
- `build_m1_m3_geometry_framework`: Compute event-level distances, axis projections, corridor membership, endpoint flags, and M2-related flags for the M1-M3 local system.
- `assign_temporal_phases_and_detect_bursts`: Assign events to the fixed phase windows and detect major local bursts with transparent rate-based rules.
- `summarize_phase_and_burst_spatial_depth_patterns`: Compute phase-level and burst-level spatial, depth, composition, and magnitude-threshold summaries for raw and M2-aware event sets.
- `evaluate_centroid_evolution_and_migration_diagnostics`: Quantify centroid transitions and event-level time-position trends to distinguish endpoint switching, stepwise activation, diffuse occupancy, and any robust migration.
- `analyze_depth_domains_and_large_event_consistency`: Compare depth occupancy across endpoint, corridor, off-corridor, burst, and large-event subsets to test for common or distinct structural domains.
- `run_robustness_checks_and_followup_screening`: Re-evaluate the main spatial-depth interpretations across thresholds, M2-aware filtering, corridor widths, endpoint definitions, and sensitivity windows, then identify non-causal follow-up targets.
- `generate_figures_and_final_structured_outputs`: Produce the compact diagnostic figure set and structured summary fields answering the catalog-screening questions.