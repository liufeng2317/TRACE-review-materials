# Goal

Implement and validate an authenticated NIED Hi-net JMA unified hypocenter catalog download workflow for the Sanriku, northeast Japan study region, producing an ASPECT-ready cleaned catalog CSV and a catalog distribution figure for the fixed half-open interval `2025-06-01 <= datetime < 2026-05-02`.

## Planning Assumptions

- Use observational hypocenter catalog data from the NIED Hi-net JMA unified hypocenter catalog service; do not substitute model, synthetic, or current-date-derived data.
- Required service endpoints:
  - Login: `https://hinetwww11.bosai.go.jp/auth/?LANG=en`
  - Catalog: `https://hinetwww11.bosai.go.jp/auth/JMA/jmalist.php`
- Credentials:
  - Default credential file: `<CASE_ROOT>/data/hinet_account/.env`
  - Required keys: `HINET_USERNAME`, `HINET_PASSWORD`
  - Command-line username/password arguments may override `.env` values.
  - Credentials must not be printed, logged, written to manifests, or embedded in saved request diagnostics.
- Required temporal interval:
  - Start date: `2025-06-01`
  - End date: `2026-05-02`, treated as exclusive.
  - Requests must cover records from `2025-06-01` through `2026-05-01`.
  - Do not replace this interval with the current date, a 2026-only default, or any runtime-derived default.
- Required spatial filter:
  - Latitude: `38.50 <= lat <= 42.50`
  - Longitude: `141.00 <= lon <= 144.50`
  - Bounds must be applied inclusively after catalog parsing and numeric conversion.
- Package/program contract constraints:
  - Use one `requests.Session` for login and all catalog requests.
  - Add retry and bounded backoff for login and catalog requests.
  - Split catalog requests into chunks of no more than 7 days.
  - Parse the JMA fixed-width catalog table; do not use comma splitting as the row parser.
  - If an HTML/text response cannot be parsed, save the original failed response to a debug/raw file and include the saved path in the raised error message.
  - Preserve an optional `raw-dir` argument for saving raw text/HTML from every time chunk.
- Required cleaned CSV:
  - Filename: `Snet_catalog_20250601_20260502.csv`
  - Columns exactly, in order: `datetime,lat,lon,dep,mag`
- Required figure:
  - Filename: `Snet_catalog_20250601_20260502_distribution.png`
  - Must be generated from the cleaned catalog, not from raw or unfiltered rows.

## Analysis Plan

### Task 1 — Implement the authenticated chunked JMA catalog workflow

- Task description:
  - Create one cohesive workflow script, e.g. `download_sanriku_jma_catalog.py`, that performs credential loading, authenticated session setup, chunked JMA catalog downloads, optional raw response saving, fixed-width parsing, cleaning, validation, CSV writing, chunk-manifest writing, and distribution figure generation.
  - Keep request preparation, login validation, per-chunk execution, parsing checks, merged-output validation, and failure evidence collection inside this primary script.

- Required data sources:
  - NIED Hi-net login endpoint: `https://hinetwww11.bosai.go.jp/auth/?LANG=en`
  - NIED Hi-net JMA catalog endpoint: `https://hinetwww11.bosai.go.jp/auth/JMA/jmalist.php`
  - Credential file: `<CASE_ROOT>/data/hinet_account/.env`
  - Existing local JMA catalog workflow scaffold, if available, may be used only to verify form field names and fixed-width table layout; do not copy unrelated example dates, regions, or output names.

- Parameter selection strategy:
  - Credentials:
    - Read `HINET_USERNAME` and `HINET_PASSWORD` from the `.env` file by default.
    - Allow CLI overrides for username and password.
    - Fail early with a non-sensitive error if credentials are unavailable.
  - Time window:
    - Use `start_date = 2025-06-01`.
    - Use `end_date_exclusive = 2026-05-02`.
    - Generate half-open chunks `[chunk_start, chunk_end)` with `chunk_end <= chunk_start + 7 days`.
    - First chunk must be `[2025-06-01, 2025-06-08)`.
    - Final chunk must be `[2026-04-26, 2026-05-02)`.
    - The manifest must contain all 48 generated chunks with exact requested boundaries.
    - If the JMA web form expects inclusive end dates, submit `chunk_end_exclusive - 1 day` as the request end date while preserving the internal half-open boundary in the manifest.
  - Spatial bounds:
    - `lat_min = 38.50`
    - `lat_max = 42.50`
    - `lon_min = 141.00`
    - `lon_max = 144.50`
  - Output filenames:
    - Cleaned catalog: `Snet_catalog_20250601_20260502.csv`
    - Distribution figure: `Snet_catalog_20250601_20260502_distribution.png`
    - Chunk manifest: `Snet_catalog_20250601_20260502_chunk_manifest.csv`
    - Validation summary: `Snet_catalog_20250601_20260502_validation.json`
  - Raw/debug outputs:
    - If `raw-dir` is supplied, save raw text/HTML for every chunk using filenames that encode the chunk start and exclusive end dates.
    - Always save failed or unparseable responses to a debug/raw file and include the saved path in the error.

- Constraints:
  - Authentication and requests:
    - Use a single authenticated `requests.Session` for login and all catalog requests.
    - Apply retry and backoff to login and each chunk request.
    - Treat final failed status codes, timeouts, authentication failures, and unexpected empty responses as workflow failures unless the service page is recognizable as a valid zero-event response.
    - Do not silently skip failed chunks.
  - Request construction:
    - Use the fixed manuscript-aligned dates only.
    - No request may exceed 7 days.
    - Record both internal half-open boundaries and submitted service date parameters.
  - Fixed-width parsing:
    - Extract the JMA table text region from the returned HTML/text.
    - Identify event rows by the verified fixed-width table structure.
    - Extract at minimum origin date/time, latitude, longitude, depth, and magnitude.
    - Convert any JMA degrees/minutes or fixed-field coordinate format into decimal degrees if required by the table layout.
    - Skip headers, separators, navigation text, empty lines, and non-event rows.
    - Do not parse catalog rows by comma splitting.
    - A recognizable valid no-event page should be recorded as a zero-row chunk.
    - An unrecognizable or structurally changed page must be saved as a failed raw response and raised as an error with the saved path.
  - Cleaning order:
    - Parse `datetime` as time.
    - Convert `lat`, `lon`, `dep`, and `mag` to numeric values.
    - Remove rows with missing or non-convertible values in any required field.
    - Enforce `2025-06-01 <= datetime < 2026-05-02`.
    - Apply inclusive Sanriku spatial filtering.
    - Sort by `datetime`.
    - Remove duplicate rows after standardizing the five ASPECT columns.
    - Write only `datetime,lat,lon,dep,mag` to the final CSV.
  - Output validity:
    - Successful execution requires all chunks to be accounted for in the manifest.
    - Successful execution requires the merged CSV to pass schema, time, numeric, spatial, sorting, and duplicate checks.
    - Successful execution requires the distribution figure to be generated from the cleaned CSV.
    - Placeholder, mock, schema-only, or diagnostic-only outputs must not be treated as success when real events are available.

- Key outputs:
  - `Snet_catalog_20250601_20260502.csv`
    - ASPECT-ready catalog with exactly `datetime,lat,lon,dep,mag`.
  - `Snet_catalog_20250601_20260502_chunk_manifest.csv`
    - One row per chunk with requested boundaries, submitted request dates, request status, parse status, row counts, actual returned date range, retained Sanriku date range, raw file path if saved, and debug file path if applicable.
  - `Snet_catalog_20250601_20260502_validation.json`
    - Non-sensitive summary of credentials source, chunk coverage, row counts, cleaning losses, final catalog ranges, duplicate removal, and acceptance status.
  - Optional raw response files for every chunk if `raw-dir` is supplied.
  - Mandatory debug/raw response file for any unparseable response.

### Task 2 — Validate chunking, parsing, cleaning, and merged catalog integrity

- Task description:
  - Run validation within the same workflow after all chunks are processed and the merged catalog is written.

- Required data sources:
  - In-memory parsed per-chunk records from Task 1.
  - `Snet_catalog_20250601_20260502.csv`
  - `Snet_catalog_20250601_20260502_chunk_manifest.csv`
  - Saved raw/debug files if any chunk fails or cannot be parsed.

- Parameter selection strategy:
  - Validate only against the fixed requested parameters:
    - Time: `2025-06-01 <= datetime < 2026-05-02`
    - Latitude: `38.50 <= lat <= 42.50`
    - Longitude: `141.00 <= lon <= 144.50`
    - Maximum chunk length: 7 days
    - Required columns: `datetime,lat,lon,dep,mag`

- Constraints:
  - Chunk validation:
    - Confirm exactly 48 half-open chunks are present.
    - Confirm first chunk starts `2025-06-01`.
    - Confirm final chunk ends `2026-05-02`.
    - Confirm chunks are continuous, non-overlapping, and no longer than 7 days.
    - Confirm each chunk records actual returned minimum and maximum event dates, or an explicit valid zero-event status.
  - CSV validation:
    - Confirm `Snet_catalog_20250601_20260502.csv` exists and is readable.
    - Confirm columns are exactly `datetime,lat,lon,dep,mag`.
    - Confirm `datetime` parses as time.
    - Confirm `lat`, `lon`, `dep`, and `mag` parse as numeric.
    - Confirm no missing values remain.
    - Confirm all retained rows satisfy the half-open time interval.
    - Confirm all retained rows satisfy inclusive Sanriku bounds.
    - Confirm rows are sorted by `datetime`.
    - Confirm duplicate rows have been removed.
  - Empty-catalog handling:
    - Do not silently accept an empty final catalog.
    - If final row count is zero, the validation summary must show whether this resulted from valid zero-event responses, temporal/spatial filtering, missing-value removal, or other cleaning steps.
    - Parser failure must not be represented as a valid empty catalog.
  - Acceptance:
    - Successful per-chunk downloads alone are insufficient; the merged cleaned CSV and figure must also pass validation.

- Key outputs:
  - Updated `Snet_catalog_20250601_20260502_validation.json` with:
    - total chunks requested;
    - all requested chunk boundaries;
    - actual returned date ranges;
    - total parsed rows;
    - rows removed for invalid datetime/numeric fields;
    - rows removed outside time interval;
    - rows removed outside Sanriku bounds;
    - duplicates removed;
    - final event count;
    - final datetime, latitude, longitude, depth, and magnitude ranges;
    - final pass/fail status.

### Task 3 — Generate and validate the catalog distribution figure

- Task description:
  - Produce a catalog distribution figure from the final cleaned ASPECT-ready CSV and verify that the plotted data match the cleaned catalog.

- Required data sources:
  - `Snet_catalog_20250601_20260502.csv`

- Parameter selection strategy:
  - Use only rows from the cleaned CSV.
  - Plot spatial extent covering at least:
    - latitude `38.50` to `42.50`
    - longitude `141.00` to `144.50`
  - Use cleaned numeric `lat`, `lon`, `dep`, and `mag`.
  - Use cleaned `datetime` for temporal diagnostics.

- Constraints:
  - Do not plot raw, unfiltered, duplicate, or out-of-bounds records.
  - Figure generation must fail if the CSV schema is not exactly `datetime,lat,lon,dep,mag`.
  - The figure must visually support quality control of the final catalog and Sanriku bounds.
  - If the final catalog is empty after valid processing, generate a clear no-retained-events diagnostic figure and record the reason in the validation summary.

- Figure contents:
  - Map-style epicenter scatter of longitude versus latitude.
  - Sanriku bounding box shown explicitly.
  - Events colored by depth or magnitude.
  - Supporting diagnostic panel or annotation for event count through time, magnitude range, and/or depth range.

- Key outputs:
  - `Snet_catalog_20250601_20260502_distribution.png`
  - Validation summary entry confirming:
    - the figure exists;
    - the plotted event count matches the cleaned CSV row count;
    - the figure was generated from `Snet_catalog_20250601_20260502.csv`.