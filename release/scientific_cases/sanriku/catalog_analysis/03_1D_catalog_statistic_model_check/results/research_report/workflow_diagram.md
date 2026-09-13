# Workflow Overview

## Top-Level Task Dependencies

```mermaid
graph TD
    01_catalog_bvalue_activation_analysis
    style 01_catalog_bvalue_activation_analysis fill:#d4e6f1,stroke:#333,stroke-width:1px
```
**Description:**
- `01_catalog_bvalue_activation_analysis`: Build the Aomori analysis catalog, define the M1-M3 study regions, estimate Mc b-value and rate evolution, run limited robustness checks, and generate the final figures and machine-readable outputs.


## Subtask Dependencies

#### 01_catalog_bvalue_activation_analysis
**Usage**: Build the Aomori analysis catalog, define the M1-M3 study regions, estimate Mc b-value and rate evolution, run limited robustness checks, and generate the final figures and machine-readable outputs.
```mermaid
graph TD
    catalog_ingestion_and_phase_setup
    catalog_ingestion_and_phase_setup --> magnitude_discretization_verification
    catalog_ingestion_and_phase_setup --> study_area_geometry_selection
    catalog_ingestion_and_phase_setup --> subregion_definition_and_support_check
    study_area_geometry_selection --> subregion_definition_and_support_check
    study_area_geometry_selection --> phase_level_summary_estimation
    subregion_definition_and_support_check --> phase_level_summary_estimation
    magnitude_discretization_verification --> phase_level_summary_estimation
    catalog_ingestion_and_phase_setup --> phase_level_summary_estimation
    study_area_geometry_selection --> sliding_mc_bvalue_estimation
    subregion_definition_and_support_check --> sliding_mc_bvalue_estimation
    magnitude_discretization_verification --> sliding_mc_bvalue_estimation
    catalog_ingestion_and_phase_setup --> sliding_mc_bvalue_estimation
    study_area_geometry_selection --> rate_evolution_and_joint_interpretation_metrics
    subregion_definition_and_support_check --> rate_evolution_and_joint_interpretation_metrics
    sliding_mc_bvalue_estimation --> rate_evolution_and_joint_interpretation_metrics
    catalog_ingestion_and_phase_setup --> rate_evolution_and_joint_interpretation_metrics
    phase_level_summary_estimation --> regional_comparison_and_conditional_spatial_mapping
    sliding_mc_bvalue_estimation --> regional_comparison_and_conditional_spatial_mapping
    subregion_definition_and_support_check --> regional_comparison_and_conditional_spatial_mapping
    study_area_geometry_selection --> regional_comparison_and_conditional_spatial_mapping
    magnitude_discretization_verification --> regional_comparison_and_conditional_spatial_mapping
    study_area_geometry_selection --> limited_robustness_checks_and_final_packaging
    sliding_mc_bvalue_estimation --> limited_robustness_checks_and_final_packaging
    subregion_definition_and_support_check --> limited_robustness_checks_and_final_packaging
    magnitude_discretization_verification --> limited_robustness_checks_and_final_packaging
    regional_comparison_and_conditional_spatial_mapping --> limited_robustness_checks_and_final_packaging
    style limited_robustness_checks_and_final_packaging fill:#f2f4f4,stroke:#333,stroke-width:1px
    style regional_comparison_and_conditional_spatial_mapping fill:#eaf2f8,stroke:#333,stroke-width:1px
    style sliding_mc_bvalue_estimation fill:#ebdef0,stroke:#333,stroke-width:1px
    style phase_level_summary_estimation fill:#eaf2f8,stroke:#333,stroke-width:1px
    style catalog_ingestion_and_phase_setup fill:#f9ebea,stroke:#333,stroke-width:1px
    style magnitude_discretization_verification fill:#d1f2eb,stroke:#333,stroke-width:1px
    style subregion_definition_and_support_check fill:#f6ddcc,stroke:#333,stroke-width:1px
    style rate_evolution_and_joint_interpretation_metrics fill:#d4e6d4,stroke:#333,stroke-width:1px
    style study_area_geometry_selection fill:#fcf3cf,stroke:#333,stroke-width:1px
```
**Description:**
- `catalog_ingestion_and_phase_setup`: Load the filtered catalog and mainshock table, standardize fields, sort by origin time, and define the interpretive phase markers.
- `magnitude_discretization_verification`: Verify the catalog magnitude discretization and select a consistent delta_m for Mc and b-value estimation.
- `study_area_geometry_selection`: Construct simple M1-M3-oriented candidate regions, compare them with a broad baseline, and choose the final whole study area based on spatial coverage and exclusion of unrelated clustering.
- `subregion_definition_and_support_check`: Define M1-centered and M3-centered circular subregions and quantify whether they have enough events for the requested sliding analysis.
- `phase_level_summary_estimation`: Compute simple phase-by-region summaries of Mc b-value uncertainty completeness support and average event rate.
- `sliding_mc_bvalue_estimation`: Estimate windowed Mc and b-value series for the whole area and main subregions using fixed-count windows assigned to median event time.
- `rate_evolution_and_joint_interpretation_metrics`: Compute matched-window and simple calendar-bin event-rate measures and pair them with the sliding b-value results.
- `regional_comparison_and_conditional_spatial_mapping`: Compare whole-area M1-centered and M3-centered evolution and optionally compute spatial b-value maps only if support and Mc stability are adequate.
- `limited_robustness_checks_and_final_packaging`: Run only the targeted sensitivity tests that could change the broad interpretation and assemble the compact final deliverables.