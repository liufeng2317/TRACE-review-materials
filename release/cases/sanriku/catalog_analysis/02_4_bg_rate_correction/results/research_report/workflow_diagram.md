# Workflow Overview

## Top-Level Task Dependencies

```mermaid
graph TD
    01_aomori_background_rate_analysis
    01_aomori_background_rate_analysis --> 02_aomori_bootstrap_controls
    style 01_aomori_background_rate_analysis fill:#eaf2f8,stroke:#333,stroke-width:1px
    style 02_aomori_bootstrap_controls fill:#d6eaf8,stroke:#333,stroke-width:1px
```
**Description:**
- `01_aomori_background_rate_analysis`: Audit the two catalogs, define the common analysis region, estimate long-term background rates, decompose active-period rates, and generate anomaly tables and figures.
- `02_aomori_bootstrap_controls`: Run heavy bootstrap and random-window control resampling from validated intermediate outputs and merge the results into the anomaly summary.


## Subtask Dependencies

#### 01_aomori_background_rate_analysis
**Usage**: Audit the two catalogs, define the common analysis region, estimate long-term background rates, decompose active-period rates, and generate anomaly tables and figures.
```mermaid
graph TD
    ingest_and_standardize_catalogs
    ingest_and_standardize_catalogs --> define_common_region_and_subregions
    define_common_region_and_subregions --> crosswalk_overlap_and_completeness
    define_common_region_and_subregions --> estimate_long_term_background_rates
    crosswalk_overlap_and_completeness --> estimate_long_term_background_rates
    define_common_region_and_subregions --> decompose_active_period_rates
    estimate_long_term_background_rates --> test_background_corrected_anomalies_and_generate_outputs
    decompose_active_period_rates --> test_background_corrected_anomalies_and_generate_outputs
    crosswalk_overlap_and_completeness --> test_background_corrected_anomalies_and_generate_outputs
    define_common_region_and_subregions --> test_background_corrected_anomalies_and_generate_outputs
    style test_background_corrected_anomalies_and_generate_outputs fill:#e8f8f5,stroke:#333,stroke-width:1px
    style define_common_region_and_subregions fill:#fadbd8,stroke:#333,stroke-width:1px
    style estimate_long_term_background_rates fill:#eaf2f8,stroke:#333,stroke-width:1px
    style decompose_active_period_rates fill:#fef9e7,stroke:#333,stroke-width:1px
    style crosswalk_overlap_and_completeness fill:#f6ddcc,stroke:#333,stroke-width:1px
    style ingest_and_standardize_catalogs fill:#f2f4f4,stroke:#333,stroke-width:1px
```
**Description:**
- `ingest_and_standardize_catalogs`: Load the long-term and active-period catalogs, normalize schema and data types, and document any file substitution.
- `define_common_region_and_subregions`: Derive the common spatial mask from the active-period catalog, add a small documented buffer if needed, and freeze named analysis subregions.
- `crosswalk_overlap_and_completeness`: Compare the catalogs over the overlap period within the common region, match larger events where feasible, and assess threshold reliability.
- `estimate_long_term_background_rates`: Compute baseline rates and empirical window distributions from the filtered long-term catalog for the common region and fixed subregions.
- `decompose_active_period_rates`: Resolve active-period rate evolution by region, threshold, depth bin, and timescale using the relocated catalog only.
- `test_background_corrected_anomalies_and_generate_outputs`: Compare active-period observations against long-term expectations, apply controls, and write the compact evidence products and diagnostic figures.

#### 02_aomori_bootstrap_controls
**Usage**: Run heavy bootstrap and random-window control resampling from validated intermediate outputs and merge the results into the anomaly summary.
```mermaid
graph TD
    resample_control_windows
    resample_control_windows --> merge_resampling_results
    style resample_control_windows fill:#eaf2f8,stroke:#333,stroke-width:1px
    style merge_resampling_results fill:#eaf2f8,stroke:#333,stroke-width:1px
```
**Description:**
- `resample_control_windows`: Generate bootstrap and random-window null distributions for predefined region-threshold-depth combinations.
- `merge_resampling_results`: Integrate resampling outputs with the anomaly summary without changing predefined regions or threshold decisions.