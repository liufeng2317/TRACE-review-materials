# Workflow Overview

## Top-Level Task Dependencies

```mermaid
graph TD
    01_hinet_jma_arrivals_workflow
    01_hinet_jma_arrivals_workflow --> 02_diagnostic_summaries
    style 01_hinet_jma_arrivals_workflow fill:#d4e6d4,stroke:#333,stroke-width:1px
    style 02_diagnostic_summaries fill:#d6eaf8,stroke:#333,stroke-width:1px
```
**Description:**
- `01_hinet_jma_arrivals_workflow`: Download Hi-net JMA arrival-time measure files, parse fixed-width records, subset the Sanriku region, export compatibility products, and validate all required outputs.
- `02_diagnostic_summaries`: Generate compact non-authoritative diagnostic summaries and optional QC figures from the validated catalog products.


## Subtask Dependencies

#### 01_hinet_jma_arrivals_workflow
**Usage**: Download Hi-net JMA arrival-time measure files, parse fixed-width records, subset the Sanriku region, export compatibility products, and validate all required outputs.
```mermaid
graph TD
    load_credentials
    build_chunk_schedule
    load_credentials --> run_smoke_download
    build_chunk_schedule --> run_smoke_download
    run_smoke_download --> verify_measure_format_schema
    run_smoke_download --> parse_and_validate_smoke_chunk
    verify_measure_format_schema --> parse_and_validate_smoke_chunk
    load_credentials --> run_full_download
    build_chunk_schedule --> run_full_download
    parse_and_validate_smoke_chunk --> run_full_download
    run_full_download --> parse_merge_full_catalog
    verify_measure_format_schema --> parse_merge_full_catalog
    parse_merge_full_catalog --> apply_sanriku_subset
    apply_sanriku_subset --> export_phase_and_station_products
    build_chunk_schedule --> run_final_validation_and_inventory
    run_full_download --> run_final_validation_and_inventory
    parse_merge_full_catalog --> run_final_validation_and_inventory
    apply_sanriku_subset --> run_final_validation_and_inventory
    export_phase_and_station_products --> run_final_validation_and_inventory
    style run_smoke_download fill:#f2f4f4,stroke:#333,stroke-width:1px
    style run_final_validation_and_inventory fill:#d4e6f1,stroke:#333,stroke-width:1px
    style verify_measure_format_schema fill:#d1f2eb,stroke:#333,stroke-width:1px
    style apply_sanriku_subset fill:#f9e79f,stroke:#333,stroke-width:1px
    style load_credentials fill:#d4e6f1,stroke:#333,stroke-width:1px
    style run_full_download fill:#fef9e7,stroke:#333,stroke-width:1px
    style parse_merge_full_catalog fill:#f9e79f,stroke:#333,stroke-width:1px
    style parse_and_validate_smoke_chunk fill:#d4e6f1,stroke:#333,stroke-width:1px
    style build_chunk_schedule fill:#fef9e7,stroke:#333,stroke-width:1px
    style export_phase_and_station_products fill:#fcf3cf,stroke:#333,stroke-width:1px
```
**Description:**
- `load_credentials`: Load one or more Hi-net accounts from environment variables before the configured dotenv source with password redaction.
- `build_chunk_schedule`: Build deterministic half-open five-day chunks for the full requested JST interval and identify the smoke-test chunk.
- `run_smoke_download`: Download or reuse the first five-day raw measure file through the HinetPy arrival-time interface with retry and backoff.
- `verify_measure_format_schema`: Verify documented byte slices for JMA fixed-width J, station-pick, and E records before producing scientific catalogs.
- `parse_and_validate_smoke_chunk`: Parse the smoke raw file in byte mode and gate full execution on download, fixed-width, event-pick, and P/S count checks.
- `run_full_download`: After smoke-test success, download or reuse all scheduled raw measure files and write a complete sanitized manifest.
- `parse_merge_full_catalog`: Parse all accepted raw measure files into deterministic full event and pick tables with per-file parser QC.
- `apply_sanriku_subset`: Apply the inclusive Sanriku event-location filter locally after parsing and retain linked picks by event identifier.
- `export_phase_and_station_products`: Export Sanriku phase.dat and station.sta products using existing project conventions without fabricating station metadata.
- `run_final_validation_and_inventory`: Validate download schedule, parser QC, table integrity, regional subset consistency, compatibility exports, and product completeness.

#### 02_diagnostic_summaries
**Usage**: Generate compact non-authoritative diagnostic summaries and optional QC figures from the validated catalog products.
```mermaid
graph TD
    aggregate_temporal_coverage
    summarize_pick_completeness
    summarize_spatial_and_station_outputs
    style summarize_pick_completeness fill:#e8daef,stroke:#333,stroke-width:1px
    style aggregate_temporal_coverage fill:#d1f2eb,stroke:#333,stroke-width:1px
    style summarize_spatial_and_station_outputs fill:#d1f2eb,stroke:#333,stroke-width:1px
```
**Description:**
- `aggregate_temporal_coverage`: Summarize download, event, and pick coverage by chunk and UTC calendar day.
- `summarize_pick_completeness`: Compute P/S availability, P-only, S-only, both-present, and both-missing summaries for full and regional pick tables.
- `summarize_spatial_and_station_outputs`: Summarize Sanriku filtering behavior and station metadata matching without changing authoritative outputs.