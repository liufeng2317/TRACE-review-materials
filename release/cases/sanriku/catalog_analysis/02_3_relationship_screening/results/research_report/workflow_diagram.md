# Workflow Overview

## Top-Level Task Dependencies

```mermaid
graph TD
    01_relationship_analysis
    01_relationship_analysis --> 02_report_synthesis
    style 01_relationship_analysis fill:#fcf3cf,stroke:#333,stroke-width:1px
    style 02_report_synthesis fill:#d5f5e3,stroke:#333,stroke-width:1px
```
**Description:**
- `01_relationship_analysis`: Build the unified event-feature dataset, compute symmetric pairwise relationship metrics and controls, evaluate hypotheses, and generate compact diagnostic outputs for the Aomori M1-M2-M3 catalog analysis.
- `02_report_synthesis`: Assemble the final concise scientific report from validated relationship-analysis outputs without recomputing core metrics.


## Subtask Dependencies

#### 01_relationship_analysis
**Usage**: Build the unified event-feature dataset, compute symmetric pairwise relationship metrics and controls, evaluate hypotheses, and generate compact diagnostic outputs for the Aomori M1-M2-M3 catalog analysis.
```mermaid
graph TD
    ingest_and_qc_catalog_inputs
    ingest_and_qc_catalog_inputs --> derive_event_and_pair_geometry_features
    derive_event_and_pair_geometry_features --> assign_pairwise_relationship_classes
    derive_event_and_pair_geometry_features --> compute_raw_pairwise_and_regional_metrics
    assign_pairwise_relationship_classes --> compute_raw_pairwise_and_regional_metrics
    derive_event_and_pair_geometry_features --> apply_temporal_geometric_and_background_controls
    compute_raw_pairwise_and_regional_metrics --> apply_temporal_geometric_and_background_controls
    compute_raw_pairwise_and_regional_metrics --> evaluate_pair_hypothesis_evidence
    apply_temporal_geometric_and_background_controls --> evaluate_pair_hypothesis_evidence
    derive_event_and_pair_geometry_features --> evaluate_pair_hypothesis_evidence
    ingest_and_qc_catalog_inputs --> evaluate_pair_hypothesis_evidence
    derive_event_and_pair_geometry_features --> generate_figures_and_machine_readable_summaries
    assign_pairwise_relationship_classes --> generate_figures_and_machine_readable_summaries
    compute_raw_pairwise_and_regional_metrics --> generate_figures_and_machine_readable_summaries
    apply_temporal_geometric_and_background_controls --> generate_figures_and_machine_readable_summaries
    evaluate_pair_hypothesis_evidence --> generate_figures_and_machine_readable_summaries
    style ingest_and_qc_catalog_inputs fill:#d4e6f1,stroke:#333,stroke-width:1px
    style derive_event_and_pair_geometry_features fill:#fcf3cf,stroke:#333,stroke-width:1px
    style generate_figures_and_machine_readable_summaries fill:#f9ebea,stroke:#333,stroke-width:1px
    style apply_temporal_geometric_and_background_controls fill:#eaf2f8,stroke:#333,stroke-width:1px
    style compute_raw_pairwise_and_regional_metrics fill:#fdebd3,stroke:#333,stroke-width:1px
    style evaluate_pair_hypothesis_evidence fill:#d4e6f1,stroke:#333,stroke-width:1px
    style assign_pairwise_relationship_classes fill:#f2f4f4,stroke:#333,stroke-width:1px
```
**Description:**
- `ingest_and_qc_catalog_inputs`: Load the relocated catalog and mainshock table, standardize fields, verify anchor events, and record catalog quality checks.
- `derive_event_and_pair_geometry_features`: Compute event-relative temporal and geometric features to each mainshock and to each mainshock pair.
- `assign_pairwise_relationship_classes`: Apply the same ambiguity-aware association framework to all three pairs and summarize stability across spatial settings.
- `compute_raw_pairwise_and_regional_metrics`: Quantify symmetric raw relationship metrics for all three pairs and summarize broader three-cluster regional activation patterns.
- `apply_temporal_geometric_and_background_controls`: Compare observed pairwise signals against temporal, geometric, and local-background controls to identify artifacts and robust effects.
- `evaluate_pair_hypothesis_evidence`: Score each pair-hypothesis combination with separate raw, control-corrected, and distance-aware evidence layers and assign follow-up priorities.
- `generate_figures_and_machine_readable_summaries`: Create the compact diagnostic figure set and export structured summary tables for pairwise interpretation and next-step prioritization.

#### 02_report_synthesis
**Usage**: Assemble the final concise scientific report from validated relationship-analysis outputs without recomputing core metrics.
```mermaid
graph TD
    compile_pairwise_scientific_summary
    compile_pairwise_scientific_summary --> assemble_final_report_products
    style assemble_final_report_products fill:#fdebd0,stroke:#333,stroke-width:1px
    style compile_pairwise_scientific_summary fill:#fdebd3,stroke:#333,stroke-width:1px
```
**Description:**
- `compile_pairwise_scientific_summary`: Summarize the evidence for M1-M2, M1-M3, and M2-M3 with separate raw, corrected, and distance-aware interpretations.
- `assemble_final_report_products`: Produce the final concise report tables and machine-readable synthesis artifacts requested by the study.