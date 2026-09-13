# Workflow Overview

## Top-Level Task Dependencies

```mermaid
graph TD
    01_data_audit_cleaning
    01_data_audit_cleaning --> 02_major_earthquake_matching
    01_data_audit_cleaning --> 03_regional_background_characterization
    01_data_audit_cleaning --> 04_mainshock_regional_context
    02_major_earthquake_matching --> 04_mainshock_regional_context
    03_regional_background_characterization --> 04_mainshock_regional_context
    01_data_audit_cleaning --> 05_diagnostic_figures
    02_major_earthquake_matching --> 05_diagnostic_figures
    03_regional_background_characterization --> 05_diagnostic_figures
    04_mainshock_regional_context --> 05_diagnostic_figures
    01_data_audit_cleaning --> 06_candidate_patterns_estimation
    02_major_earthquake_matching --> 06_candidate_patterns_estimation
    03_regional_background_characterization --> 06_candidate_patterns_estimation
    04_mainshock_regional_context --> 06_candidate_patterns_estimation
    style 03_regional_background_characterization fill:#d4e6f1,stroke:#333,stroke-width:1px
    style 01_data_audit_cleaning fill:#fcf3cf,stroke:#333,stroke-width:1px
    style 02_major_earthquake_matching fill:#f9ebea,stroke:#333,stroke-width:1px
    style 06_candidate_patterns_estimation fill:#d5f5e3,stroke:#333,stroke-width:1px
    style 04_mainshock_regional_context fill:#f6ddcc,stroke:#333,stroke-width:1px
    style 05_diagnostic_figures fill:#f9ebea,stroke:#333,stroke-width:1px
```
**Description:**
- `01_data_audit_cleaning`: Audit all source files and build a validated Stage-1 cleaned regional catalog with quality flags.
- `02_major_earthquake_matching`: Match major earthquakes to the relocated catalog and quantify match confidence and differences.
- `03_regional_background_characterization`: Characterize regional seismicity background, station coverage, and mechanism availability from the cleaned catalog.
- `04_mainshock_regional_context`: Summarize local catalog, station, and mechanism context around each major earthquake.
- `05_diagnostic_figures`: Generate Nature-style high-resolution diagnostic figures for audit, background, and context analysis.
- `06_candidate_patterns_estimation`: Convert background and context results into ranked candidate patterns and follow-up analysis suggestions.


## Subtask Dependencies

#### 01_data_audit_cleaning
**Usage**: Audit all source files and build a validated Stage-1 cleaned regional catalog with quality flags.
```mermaid
graph TD
    inspect_inputs
    clean_stage1_catalog
    clean_stage1_catalog --> detect_abnormalities
    clean_stage1_catalog --> validate_stage1_outputs
    inspect_inputs --> validate_stage1_outputs
    style clean_stage1_catalog fill:#d4e6d4,stroke:#333,stroke-width:1px
    style inspect_inputs fill:#f9e79f,stroke:#333,stroke-width:1px
    style validate_stage1_outputs fill:#fdebd0,stroke:#333,stroke-width:1px
    style detect_abnormalities fill:#d6eaf8,stroke:#333,stroke-width:1px
```
**Description:**
- `inspect_inputs`: Inspect schemas, record counts, field names, and raw value ranges for all files.
- `clean_stage1_catalog`: Parse event time and harmonize core event fields into a validated cleaned table.
- `detect_abnormalities`: Flag missing, impossible, duplicate, and physically implausible records.
- `validate_stage1_outputs`: Confirm the cleaned catalog is non-empty and ready for downstream analyses.

#### 02_major_earthquake_matching
**Usage**: Match major earthquakes to the relocated catalog and quantify match confidence and differences.
```mermaid
graph TD
    generate_candidate_windows
    generate_candidate_windows --> rank_and_match_events
    rank_and_match_events --> classify_match_confidence
    style generate_candidate_windows fill:#eaf2f8,stroke:#333,stroke-width:1px
    style rank_and_match_events fill:#eaf2f8,stroke:#333,stroke-width:1px
    style classify_match_confidence fill:#d4e6d4,stroke:#333,stroke-width:1px
```
**Description:**
- `generate_candidate_windows`: Build constrained candidate windows around each reference origin time.
- `rank_and_match_events`: Rank candidates by time, space, depth, and magnitude agreement and select best matches.
- `classify_match_confidence`: Assign confidence tiers based on uniqueness and multi-metric agreement.

#### 03_regional_background_characterization
**Usage**: Characterize regional seismicity background, station coverage, and mechanism availability from the cleaned catalog.
```mermaid
graph TD
    summarize_spatiotemporal_background
    estimate_completeness_and_bvalue
    summarize_station_and_mechanism_background
    style summarize_station_and_mechanism_background fill:#f5eef8,stroke:#333,stroke-width:1px
    style summarize_spatiotemporal_background fill:#fdebd3,stroke:#333,stroke-width:1px
    style estimate_completeness_and_bvalue fill:#d5f5e3,stroke:#333,stroke-width:1px
```
**Description:**
- `summarize_spatiotemporal_background`: Compute spatial density, temporal rate, magnitude distribution, and depth distribution summaries.
- `estimate_completeness_and_bvalue`: Estimate preliminary Mc and Gutenberg-Richter b-value from the cleaned catalog.
- `summarize_station_and_mechanism_background`: Assess station coverage and focal-mechanism availability and distribution.

#### 04_mainshock_regional_context
**Usage**: Summarize local catalog, station, and mechanism context around each major earthquake.
```mermaid
graph TD
    derive_local_neighborhoods
    derive_local_neighborhoods --> compute_local_context_metrics
    compute_local_context_metrics --> derive_sequence_threshold_notes
    style derive_sequence_threshold_notes fill:#d1f2eb,stroke:#333,stroke-width:1px
    style derive_local_neighborhoods fill:#f5eef8,stroke:#333,stroke-width:1px
    style compute_local_context_metrics fill:#d4e6f1,stroke:#333,stroke-width:1px
```
**Description:**
- `derive_local_neighborhoods`: Define reusable local neighborhoods around each matched mainshock.
- `compute_local_context_metrics`: Compare local event, depth, station, and mechanism context to the regional background.
- `derive_sequence_threshold_notes`: Produce candidate radius, depth, and magnitude screening notes for later sequence analysis.

#### 05_diagnostic_figures
**Usage**: Generate Nature-style high-resolution diagnostic figures for audit, background, and context analysis.
```mermaid
graph TD
    create_spatial_figures
    create_temporal_and_size_figures
    create_frequency_station_mechanism_figures
    style create_temporal_and_size_figures fill:#ebdef0,stroke:#333,stroke-width:1px
    style create_frequency_station_mechanism_figures fill:#fcf3cf,stroke:#333,stroke-width:1px
    style create_spatial_figures fill:#d1f2eb,stroke:#333,stroke-width:1px
```
**Description:**
- `create_spatial_figures`: Plot regional earthquake, major earthquake, station, and focal-mechanism maps.
- `create_temporal_and_size_figures`: Plot time-magnitude, depth-time, and magnitude-depth diagnostics.
- `create_frequency_station_mechanism_figures`: Plot Mc, b-value, station coverage, and mechanism availability diagnostics.

#### 06_candidate_patterns_estimation
**Usage**: Convert background and context results into ranked candidate patterns and follow-up analysis suggestions.
```mermaid
graph TD
    detect_catalog_wide_patterns
    detect_mainshock_specific_patterns
    style detect_mainshock_specific_patterns fill:#f2f4f4,stroke:#333,stroke-width:1px
    style detect_catalog_wide_patterns fill:#fef9e7,stroke:#333,stroke-width:1px
```
**Description:**
- `detect_catalog_wide_patterns`: Identify spatial, temporal, depth, and magnitude-related candidate patterns across the region.
- `detect_mainshock_specific_patterns`: Compare each mainshock neighborhood with the regional background for event-specific hypotheses.