<science_report_context>

## Scientific Objective
<user_request>
Implement and validate a JMA unified hypocenter catalog download workflow for
the Sanriku, northeast Japan study region.

## Task objective

1. Use the NIED Hi-net JMA catalog service:
   - Login endpoint: https://hinetwww11.bosai.go.jp/auth/?LANG=en
   - Catalog endpoint: https://hinetwww11.bosai.go.jp/auth/JMA/jmalist.php
2. Use the manuscript-aligned time interval:
   - start date: 2025-06-01
   - end date: 2026-05-02
   - treat the end date as exclusive when constructing requests, so the
     requested records cover 2025-06-01 through 2026-05-01.
   - do not replace this interval with a current-date or 2026-only default.
3. Use the Sanriku regional bounds:
   - latitude: 38.50 to 42.50 degrees N
   - longitude: 141.00 to 144.50 degrees E
   - apply the bounds inclusively after parsing the catalog.
4. Split requests into chunks of no more than 7 days because of the JMA
   service limit. Record the exact chunk boundaries and actual returned dates.
5. Output an ASPECT-ready CSV with exactly:
   datetime,lat,lon,dep,mag
6. Use the filename pattern:
   Snet_catalog_YYYYMMDD_YYYYMMDD.csv

## Implementation requirements

- Prefer reading HINET_USERNAME and HINET_PASSWORD from the .env file;
  command-line arguments may override them.
  - <CASE_ROOT>/data/hinet_account/.env
- Use requests.Session to maintain the authenticated session.
- Add retry and backoff for network requests.
- If an HTML response cannot be parsed, save the original failed response to a
  debug/raw file and state the saved path in the error message.
- Parse the JMA fixed-width catalog table; do not use fragile comma splitting.
- During cleaning:
  - parse datetime as time;
  - convert lat/lon/dep/mag to numeric values;
  - remove rows with missing values;
  - filter by the Sanriku spatial range;
  - sort by datetime;
  - remove duplicates.
- Keep the optional raw-dir argument for saving the raw text from each time
  chunk.

## Required outputs

- The cleaned catalog CSV file.
- A catalog distribution figure.
</user_request>

## Planned Workflow
<experiment_plan>
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
</experiment_plan>

## Implementation Trace
- Task: 01_download_validate_sanriku_jma_catalog
  Description: Download, parse, clean, validate, and visualize the authenticated Hi-net JMA unified hypocenter catalog for the Sanriku study region.
  Ancestors: none
  Handoff JSON: <CASE_ROOT>/run/00_catalog_download/exp_run/log/coding_progress/task_handoff/01_download_validate_sanriku_jma_catalog.json
  Output directory: <CASE_ROOT>/run/00_catalog_download/exp_run/outputs/01_download_validate_sanriku_jma_catalog
  Analysis file: <CASE_ROOT>/run/00_catalog_download/exp_run/analysis/01_download_validate_sanriku_jma_catalog.md

## Result Evidence Index
Use handoff JSON files as compact indexes to important outputs. Use per-task analyses for scientific interpretation. Inspect raw outputs only when the handoff and analysis are insufficient.
<task_evidence task="01_download_validate_sanriku_jma_catalog">
Handoff JSON: <CASE_ROOT>/run/00_catalog_download/exp_run/log/coding_progress/task_handoff/01_download_validate_sanriku_jma_catalog.json
{
  "meta": {
    "schema_version": 2,
    "type": "coding_task_handoff",
    "task": "01_download_validate_sanriku_jma_catalog",
    "generated_at": "2026-09-11T19:15:14.845228+00:00"
  },
  "status": {
    "state": "success",
    "stage": "analysis_done",
    "elapsed_sec": 7755.908,
    "timing": {
      "total_sec": 7755.908,
      "coding_agent_sec": 480.241,
      "code_review_sec": 63.781,
      "preflight_sec": 1.971,
      "script_execution_sec": 6969.691,
      "result_check_sec": 104.143,
      "task_analysis_sec": 130.457
    },
    "quality_flags": [
      "task_status:success"
    ]
  },
  "paths": {
    "root": "<CASE_ROOT>/run/00_catalog_download",
    "script": "<CASE_ROOT>/run/00_catalog_download/exp_run/scripts/01_download_validate_sanriku_jma_catalog.py",
    "output_dir": "<CASE_ROOT>/run/00_catalog_download/exp_run/outputs/01_download_validate_sanriku_jma_catalog",
    "analysis": "<CASE_ROOT>/run/00_catalog_download/exp_run/analysis/01_download_validate_sanriku_jma_catalog.md",
    "log": "<CASE_ROOT>/run/00_catalog_download/exp_run/log/task/01_download_validate_sanriku_jma_catalog/log_3.txt"
  },
  "outputs": {
    "primary": [
      {
        "path": "Snet_catalog_20250601_20260502.csv",
        "absolute_path": "<CASE_ROOT>/run/00_catalog_download/exp_run/outputs/01_download_validate_sanriku_jma_catalog/Snet_catalog_20250601_20260502.csv",
        "kind": "machine_readable"
      },
      {
        "path": "Snet_catalog_20250601_20260502_chunk_manifest.csv",
        "absolute_path": "<CASE_ROOT>/run/00_catalog_download/exp_run/outputs/01_download_validate_sanriku_jma_catalog/Snet_catalog_20250601_20260502_chunk_manifest.csv",
        "kind": "machine_readable"
      },
      {
        "path": "Snet_catalog_20250601_20260502_validation.json",
        "absolute_path": "<CASE_ROOT>/run/00_catalog_download/exp_run/outputs/01_download_validate_sanriku_jma_catalog/Snet_catalog_20250601_20260502_validation.json",
        "kind": "machine_readable"
      },
      {
        "path": "Snet_catalog_20250601_20260502_distribution.png",
        "absolute_path": "<CASE_ROOT>/run/00_catalog_download/exp_run/outputs/01_download_validate_sanriku_jma_catalog/Snet_catalog_20250601_20260502_distribution.png",
        "kind": "figure"
      },
      {
        "path": "debug/raw/login_page.html",
        "absolute_path": "<CASE_ROOT>/run/00_catalog_download/exp_run/outputs/01_download_validate_sanriku_jma_catalog/debug/raw/login_page.html",
        "kind": "document"
      },
      {
        "path": "debug/raw/login_response.html",
        "absolute_path": "<CASE_ROOT>/run/00_catalog_download/exp_run/outputs/01_download_validate_sanriku_jma_catalog/debug/raw/login_response.html",
        "kind": "document"
      }
    ],
    "all": [
      "Snet_catalog_20250601_20260502.csv",
      "Snet_catalog_20250601_20260502_chunk_manifest.csv",
      "Snet_catalog_20250601_20260502_distribution.png",
      "Snet_catalog_20250601_20260502_validation.json",
      "debug/raw/login_page.html",
      "debug/raw/login_response.html"
    ],
    "truncated": false
  },
  "notes": {
    "purpose": "Download, parse, clean, validate, and visualize the authenticated Hi-net JMA unified hypocenter catalog for the Sanriku study region.",
    "result": "Download, parse, clean, validate, and visualize the authenticated Hi-net JMA unified hypocenter catalog for the Sanriku study region. Status=success; outputs=6 discovered; primary=6.",
    "warnings": [],
    "assumptions": [],
    "limitations": []
  }
}
</task_evidence>


## Per-Task Scientific Analyses
<task_analysis>
Task: 01_download_validate_sanriku_jma_catalog
Description: Download, parse, clean, validate, and visualize the authenticated Hi-net JMA unified hypocenter catalog for the Sanriku study region.
Analysis file: <CASE_ROOT>/run/00_catalog_download/exp_run/analysis/01_download_validate_sanriku_jma_catalog.md
Output directory: <CASE_ROOT>/run/00_catalog_download/exp_run/outputs/01_download_validate_sanriku_jma_catalog

## Scientific Purpose

This task implemented and validated a workflow to download the authenticated NIED Hi-net/JMA unified hypocenter catalog for the Sanriku, northeast Japan study region. The scientific goal was to produce an ASPECT-ready earthquake catalog for the manuscript-aligned interval from 2025-06-01 through 2026-05-01, using the half-open request interval 2025-06-01 ≤ time < 2026-05-02, and the inclusive Sanriku spatial bounds 38.50–42.50°N and 141.00–144.50°E.

The workflow output is intended to support later seismicity analysis and visualization for the Sanriku region by providing a cleaned catalog with exactly the required ASPECT columns:

`datetime,lat,lon,dep,mag`

## Method and Implementation Evidence

The implemented workflow used the NIED Hi-net authenticated JMA catalog service:

- Login endpoint: `https://hinetwww11.bosai.go.jp/auth/?LANG=en`
- Catalog endpoint: `https://hinetwww11.bosai.go.jp/auth/JMA/jmalist.php`

Implementation evidence is available in the script:

- `<CASE_ROOT>/run/00_catalog_download/exp_run/scripts/01_download_validate_sanriku_jma_catalog.py`

Key implementation features verified from the script and validation outputs include:

- Authentication was performed with `requests.Session`, preserving the authenticated session across catalog requests.
- Credentials were read from the `.env` source unless overridden. The validation JSON records `credential_source: .env`.
- Network requests used retry/backoff logic through a dedicated request wrapper.
- The manuscript-aligned time interval was fixed to:
  - start date inclusive: `2025-06-01`
  - end date exclusive: `2026-05-02`
  - requested coverage note: records cover `2025-06-01` through `2026-05-01`.
- Requests were split into 48 chunks:
  - 47 chunks of 7 days
  - 1 final chunk of 6 days
  - maximum chunk duration was therefore within the required 7-day service limit.
- The JMA catalog table was parsed with fixed-width field positions rather than comma splitting.
- Cleaning steps included:
  - datetime parsing using mixed-format parsing;
  - numeric conversion of latitude, longitude, depth, and magnitude;
  - removal of rows with missing required values;
  - half-open time filtering;
  - inclusive Sanriku spatial filtering;
  - physical sanity filtering;
  - sorting by datetime;
  - duplicate removal.
- Optional raw-response saving was retained through a raw directory argument. In this run, raw chunk files were not saved because no raw directory was provided; only login/debug HTML files were saved.

Primary validation metadata is stored in:

- `<CASE_ROOT>/run/00_catalog_download/exp_run/outputs/01_download_validate_sanriku_jma_catalog/Snet_catalog_20250601_20260502_validation.json`

Chunk-level request and parsing evidence is stored in:

- `<CASE_ROOT>/run/00_catalog_download/exp_run/outputs/01_download_validate_sanriku_jma_catalog/Snet_catalog_20250601_20260502_chunk_manifest.csv`

Login/debug HTML files are stored at:

- `<CASE_ROOT>/run/00_catalog_download/exp_run/outputs/01_download_validate_sanriku_jma_catalog/debug/raw/login_page.html`
- `<CASE_ROOT>/run/00_catalog_download/exp_run/outputs/01_download_validate_sanriku_jma_catalog/debug/raw/login_response.html`

## Key Results and Evidence Files

### Cleaned ASPECT-ready catalog

The cleaned catalog was successfully generated at:

- `<CASE_ROOT>/run/00_catalog_download/exp_run/outputs/01_download_validate_sanriku_jma_catalog/Snet_catalog_20250601_20260502.csv`

Validation confirms that the CSV contains exactly the required columns:

`datetime,lat,lon,dep,mag`

The catalog contains:

- Final event count: **33,711 events**
- Time range:
  - minimum: `2025-06-01 00:09:02.360000`
  - maximum: `2026-05-01 23:58:44.740000`
- Latitude range: **38.5 to 42.5°N**
- Longitude range: **141.0 to 144.5°E**
- Depth range: **0.0 to 149.2 km**
- Magnitude range: **0.0 to 7.7**
- Missing values in required fields: **0**
- Duplicate ASPECT rows: **0**
- Datetime order: sorted monotonically increasing

These checks were verified from both the CSV and the validation file:

- `<CASE_ROOT>/run/00_catalog_download/exp_run/outputs/01_download_validate_sanriku_jma_catalog/Snet_catalog_20250601_20260502_validation.json`

### Download and chunk validation

The chunk manifest confirms that the requested interval was split correctly and that all chunks were successfully downloaded and parsed:

- Evidence file: `<CASE_ROOT>/run/00_catalog_download/exp_run/outputs/01_download_validate_sanriku_jma_catalog/Snet_catalog_20250601_20260502_chunk_manifest.csv`

Key manifest results:

- Total chunks requested: **48**
- Chunk duration range: **6 to 7 days**
- Status counts: **48 success**
- Parse status counts: **48 parsed**
- Attempts: **all chunks completed in 1 attempt**
- HTTP status: **200 for all successful chunks**
- Total parsed rows before Sanriku filtering: **270,338**
- Total retained Sanriku rows after filtering: **33,711**
- Chunks with zero retained Sanriku events: **0**
- Global actual returned datetime range before regional filtering:
  - `2025-06-01 00:03:37.790000` to `2026-05-01 23:58:44.740000`
- Global retained Sanriku datetime range:
  - `2025-06-01 00:09:02.360000` to `2026-05-01 23:58:44.740000`

The first chunk covered `2025-06-01` to `2025-06-08` exclusive and submitted an inclusive service end date of `2025-06-07`. It parsed 5,359 rows and retained 502 Sanriku rows.

The final chunk covered `2026-04-26` to `2026-05-02` exclusive and submitted an inclusive service end date of `2026-05-01`. It parsed 5,328 rows and retained 1,543 Sanriku rows.

### Cleaning statistics

The validation JSON provides a reproducible cleaning audit:

- Evidence file: `<CASE_ROOT>/run/00_catalog_download/exp_run/outputs/01_download_validate_sanriku_jma_catalog/Snet_catalog_20250601_20260502_validation.json`

Cleaning statistics:

- Initial parsed rows: **270,338**
- Rows after datetime/numeric parsing and missing-value removal: **270,338**
- Rows removed for invalid datetime or numeric fields: **0**
- Rows after requested time filter: **270,338**
- Rows removed outside requested time: **0**
- Rows after Sanriku spatial filter: **33,711**
- Rows removed outside Sanriku bounds: **236,627**
- Rows after physical sanity filter: **33,711**
- Rows removed by physical sanity filter: **0**
- Duplicates removed: **0**
- Final rows: **33,711**

This confirms that the largest reduction came from applying the Sanriku spatial bounds after parsing the broader returned JMA catalog data.

### Catalog distribution figure

The required catalog distribution figure was generated at:

- `<CASE_ROOT>/run/00_catalog_download/exp_run/outputs/01_download_validate_sanriku_jma_catalog/Snet_catalog_20250601_20260502_distribution.png`

The figure contains two main panels:

1. **Spatial and depth distribution**
   - Longitude axis spans approximately 141.0–144.5°E.
   - Latitude axis spans approximately 38.5–42.5°N.
   - A red rectangle marks the Sanriku selection bounds.
   - Events are colored by hypocentral depth from 0 to about 150 km.
   - The plotted catalog contains events across the full Sanriku domain, with dense offshore-to-nearshore clusters between roughly 142–143.5°E and 39–42°N.
   - Deeper events are more common toward the western side of the domain, while shallower events are more common in the central and eastern portions.

2. **Temporal distribution**
   - Histogram uses 7-day bins.
   - Total plotted events: **N = 33,711**
   - Activity is temporally non-uniform.
   - Background levels during much of June–October 2025 are lower, commonly several hundred events per 7-day bin.
   - Large bursts occur in late 2025, especially around November–December, with a peak exceeding 3,000 events per 7-day bin.
   - Another major increase appears around April 2026, with a peak near 3,000 events per 7-day bin.

The figure annotation confirms:

- Catalog: Hi-net/JMA
- Time span: 2025-06-01 to 2026-05-02
- Event count: **33,711**
- Magnitude range: **M 0.0 to 7.7**
- Depth range: **0.0 to 149.2 km**

## Limitations and Assumptions

- The workflow depends on authenticated access to the NIED Hi-net/JMA catalog service. Reproduction requires valid credentials.
- The validation confirms successful download and parsing for this run, but it does not independently verify the completeness or scientific quality of the JMA catalog itself.
- No magnitude of completeness analysis was performed. The magnitude range is reported as 0.0–7.7, but completeness may vary in space, time, and after large sequences.
- No uncertainty fields were retained in the ASPECT-ready output. The required CSV contains only `datetime,lat,lon,dep,mag`.
- The distribution figure shows spatial, depth, and temporal patterns but does not include a magnitude-frequency distribution or uncertainty diagnostics.
- Raw per-chunk response files were not saved in this execution because the optional raw directory argument was not used. The chunk manifest records `raw_file_path` as empty for all chunks. Login/debug HTML files were saved, but no parse-failure debug files were produced because all chunks parsed successfully.
- The catalog contains strong temporal clustering, especially in late 2025 and April 2026. Any downstream rate-based or training/validation analysis should account for these burst-like sequences.
- The endpoint was queried in 7-day-or-shorter chunks, and all chunks returned dates within the intended half-open interval. However, the returned catalog is still service-dependent and could change if the JMA/Hi-net catalog is revised.

## Report-Ready Summary

A complete authenticated Hi-net/JMA unified hypocenter catalog workflow was implemented and validated for the Sanriku study region. The workflow used the manuscript-aligned half-open interval `2025-06-01 ≤ time < 2026-05-02`, corresponding to requested records from 2025-06-01 through 2026-05-01, and applied inclusive Sanriku bounds of 38.50–42.50°N and 141.00–144.50°E after parsing.

The resulting ASPECT-ready CSV is:

- `<CASE_ROOT>/run/00_catalog_download/exp_run/outputs/01_download_validate_sanriku_jma_catalog/Snet_catalog_20250601_20260502.csv`

It contains **33,711 cleaned events** with exactly the required fields `datetime,lat,lon,dep,mag`. The final catalog spans `2025-06-01 00:09:02.360000` to `2026-05-01 23:58:44.740000`, with depths from **0.0 to 149.2 km** and magnitudes from **0.0 to 7.7**. Validation found no missing required values, no duplicate rows, and all events within the specified time and spatial bounds.

The request audit is preserved in:

- `<CASE_ROOT>/run/00_catalog_download/exp_run/outputs/01_download_validate_sanriku_jma_catalog/Snet_catalog_20250601_20260502_chunk_manifest.csv`

All **48 chunks** succeeded and parsed correctly, with no chunk exceeding the 7-day request limit.

The main visualization is:

- `<CASE_ROOT>/run/00_catalog_download/exp_run/outputs/01_download_validate_sanriku_jma_catalog/Snet_catalog_20250601_20260502_distribution.png`

It confirms the regional spatial selection, shows depth variation across the Sanriku domain, and documents strong temporal clustering, especially around November–December 2025 and April 2026.
</task_analysis>


## Evaluation Quality Summary
Use this evaluation metadata to disclose delivery status, scientific confidence, and important limitations in the final report.
<evaluation_quality>
{
  "delivery_status": "complete",
  "is_satisfactory": true,
  "limitations": [
    {
      "evidence": "The workflow depends on authenticated access to the NIED Hi-net/JMA catalog service and valid credentials from the specified .env file or CLI overrides.",
      "impact": "Future reproducibility may depend on credential availability, endpoint stability, and possible catalog revisions by the provider.",
      "severity": "low",
      "type": "external_dependency"
    },
    {
      "evidence": "The validation confirms successful download, parsing, and cleaning, but does not independently verify the completeness or uncertainty properties of the JMA catalog itself.",
      "impact": "The catalog is suitable as a cleaned ASPECT-ready input, but downstream seismicity-rate or hazard interpretations should consider catalog completeness and detection variability.",
      "severity": "low",
      "type": "uncertainty"
    },
    {
      "evidence": "Raw per-chunk response files were not saved because the optional raw-dir argument was not used; only login/debug HTML files were saved and no parse-failure debug files were needed.",
      "impact": "The chunk manifest and validation JSON provide strong auditability, but full raw-response reproducibility for every chunk is not available from this execution.",
      "severity": "low",
      "type": "output_quality"
    },
    {
      "evidence": "A physical sanity filter was applied during cleaning, although it removed zero rows.",
      "impact": "This does not affect the delivered catalog, but should be documented because it is an additional cleaning check beyond the minimum requested steps.",
      "severity": "low",
      "type": "method_assumption"
    }
  ],
  "needs_refinement": false,
  "refinement_priority": "none",
  "scientific_confidence": "high"
}
</evaluation_quality>

## Report Synthesis Rules
- Start from the scientific objective and planned workflow.
- Choose the final report shape according to the request and evidence.
- If the user requested a specific format, follow that requested format unless it conflicts with factuality or available evidence.
- Treat concise result summary, technical workflow report, and research-article style report as common shapes, not fixed templates.
- Use task-specific structures when more appropriate, such as diagnostic review, data-quality assessment, method validation, benchmark comparison, or reproducibility report.
- Hybrid structures are allowed when they better serve the scientific objective.
- Do not force a fixed section template when another structure better serves the scientific request.
- Describe implementation at the level needed to understand the evidence, not as a code log.
- Tie every major result to task analyses and concrete output files from the evidence index.
- Include warnings, assumptions, partial coverage, failed items, and other limitations when present.
- Use debug logs only to explain unresolved limitations or important methodological changes.
- Do not fabricate results, citations, or file paths.

</science_report_context>
