# Workflow Overview

## Top-Level Task Dependencies

```mermaid
graph TD
    01_download_validate_sanriku_jma_catalog
    style 01_download_validate_sanriku_jma_catalog fill:#fcf3cf,stroke:#333,stroke-width:1px
```
**Description:**
- `01_download_validate_sanriku_jma_catalog`: Download, parse, clean, validate, and visualize the authenticated Hi-net JMA unified hypocenter catalog for the Sanriku study region.


## Subtask Dependencies

#### 01_download_validate_sanriku_jma_catalog
**Usage**: Download, parse, clean, validate, and visualize the authenticated Hi-net JMA unified hypocenter catalog for the Sanriku study region.
```mermaid
graph TD
    load_credentials
    load_credentials --> initialize_authenticated_session
    generate_request_chunks
    initialize_authenticated_session --> download_catalog_chunks
    generate_request_chunks --> download_catalog_chunks
    download_catalog_chunks --> parse_fixed_width_catalog
    parse_fixed_width_catalog --> clean_catalog
    clean_catalog --> write_catalog_and_manifests
    parse_fixed_width_catalog --> write_catalog_and_manifests
    initialize_authenticated_session --> write_catalog_and_manifests
    clean_catalog --> generate_distribution_figure
    write_catalog_and_manifests --> generate_distribution_figure
    write_catalog_and_manifests --> validate_final_outputs
    generate_distribution_figure --> validate_final_outputs
    style parse_fixed_width_catalog fill:#fef9e7,stroke:#333,stroke-width:1px
    style load_credentials fill:#e8daef,stroke:#333,stroke-width:1px
    style initialize_authenticated_session fill:#e8daef,stroke:#333,stroke-width:1px
    style clean_catalog fill:#f9e79f,stroke:#333,stroke-width:1px
    style generate_request_chunks fill:#d6eaf8,stroke:#333,stroke-width:1px
    style write_catalog_and_manifests fill:#f9ebea,stroke:#333,stroke-width:1px
    style generate_distribution_figure fill:#ebdef0,stroke:#333,stroke-width:1px
    style validate_final_outputs fill:#f9ebea,stroke:#333,stroke-width:1px
    style download_catalog_chunks fill:#f5eef8,stroke:#333,stroke-width:1px
```
**Description:**
- `load_credentials`: Load Hi-net credentials from the default environment file with optional command-line overrides.
- `initialize_authenticated_session`: Create a reusable requests session and authenticate against the Hi-net login endpoint.
- `generate_request_chunks`: Build continuous half-open request chunks that cover the fixed manuscript interval without exceeding the service limit.
- `download_catalog_chunks`: Request each catalog chunk through the authenticated session and record request, response, and raw-saving diagnostics.
- `parse_fixed_width_catalog`: Extract event rows from the returned JMA fixed-width catalog tables and capture parse status for each chunk.
- `clean_catalog`: Standardize parsed records, remove invalid rows, apply fixed time and Sanriku bounds, sort events, and remove duplicates.
- `write_catalog_and_manifests`: Write the cleaned ASPECT-ready catalog and non-sensitive machine-readable processing evidence.
- `generate_distribution_figure`: Generate a catalog distribution figure only from the validated cleaned catalog table.
- `validate_final_outputs`: Validate chunk coverage, parsed date evidence, cleaned CSV integrity, duplicate removal, and figure provenance before declaring success.