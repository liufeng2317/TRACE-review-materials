# Goal

Implement and validate an authenticated NIED Hi-net JMA unified hypocenter catalog download workflow for the Sanriku, northeast Japan study region, producing an ASPECT-ready cleaned catalog CSV and a catalog distribution figure for 2025-06-01 through 2026-05-01.

## Planning Assumptions

- Use observation/catalog data from the NIED Hi-net JMA unified hypocenter service, not model data.
- Authentication endpoints and inputs:
  - Login endpoint: `https://hinetwww11.bosai.go.jp/auth/?LANG=en`
  - Catalog endpoint: `https://hinetwww11.bosai.go.jp/auth/JMA/jmalist.php`
  - Credential file: `<CASE_ROOT>/data/hinet_account/.env`
  - Credential keys: `HINET_USERNAME`, `HINET_PASSWORD`
  - Command-line credentials may override `.env`; credentials must not be printed to logs.
- Time window:
  - Start date: `2025-06-01`
  - End date: `2026-05-02`, treated as exclusive.
  - Requested records must cover `2025-06-01` through `2026-05-01`.
  - Do not replace this interval with current-date, 2026-only, or runtime-derived defaults.
- Spatial filter:
  - Latitude inclusive range: `38.50 <= lat <= 42.50`
  - Longitude inclusive range: `141.00 <= lon <= 144.50`
  - Apply spatial filtering after fixed-width parsing and numeric conversion.
- JMA request limit:
  - Split requests into chunks of no more than 7 days.
  - Use half-open chunk boundaries internally: `[chunk_start, chunk_end_exclusive)`.
  - If the web form expects inclusive end dates, submit `chunk_end_exclusive - 1 day` as the request end date.
- Required cleaned CSV schema, exactly:
  - `datetime,lat,lon,dep,mag`
- Required cleaned CSV filename:
  - `Snet_catalog_20250601_20260502.csv`
- Required distribution figure filename:
  - `Snet_catalog_20250601_20260502_distribution.png`
- Use `requests.Session` for login and catalog requests.
- Use retry with backoff for login and catalog HTTP requests.
- Parse the JMA fixed-width catalog table; do not use comma splitting as the parsing method.
- If a response cannot be parsed as a JMA catalog table, save the original HTML/text response as a debug raw file and include that saved filename/path in the raised error message.
- Keep an optional `raw-dir` argument for saving raw responses from every time chunk.

## Analysis Plan

### Task 1 — Implement the authenticated JMA catalog download, parsing, cleaning, validation, and plotting workflow

- Task description:
  - Create one primary workflow script that logs in to Hi-net/JMA, downloads chunked JMA unified hypocenter catalog pages, saves optional raw responses, parses fixed-width catalog rows, cleans and filters events, validates outputs, and generates the final CSV and distribution figure.

- Required data sources:
  - `https://hinetwww11.bosai.go.jp/auth/?LANG=en`
  - `https://hinetwww11.bosai.go.jp/auth/JMA/jmalist.php`
  - `<CASE_ROOT>/data/hinet_account/.env`
  - Existing local workflow scaffold and previously parsed regional event/catalog files under the surrounding `catalog_construction_from_JMA` example directory may be used only to confirm fixed-width parsing conventions and expected field meanings.

- Parameter selection strategy:
  - Credentials:
    - Read `HINET_USERNAME` and `HINET_PASSWORD` from the `.env` file by default.
    - Allow command-line username/password overrides.
    - Validate that non-empty credentials are available before making requests.
  - Time range:
    - Use fixed start date `2025-06-01`.
    - Use fixed exclusive end date `2026-05-02`.
    - Generate exact 7-day-or-shorter half-open chunks:
      - `2025-06-01` to `2025-06-08`
      - `2025-06-08` to `2025-06-15`
      - `2025-06-15` to `2025-06-22`
      - `2025-06-22` to `2025-06-29`
      - `2025-06-29` to `2025-07-06`
      - `2025-07-06` to `2025-07-13`
      - `2025-07-13` to `2025-07-20`
      - `2025-07-20` to `2025-07-27`
      - `2025-07-27` to `2025-08-03`
      - `2025-08-03` to `2025-08-10`
      - `2025-08-10` to `2025-08-17`
      - `2025-08-17` to `2025-08-24`
      - `2025-08-24` to `2025-08-31`
      - `2025-08-31` to `2025-09-07`
      - `2025-09-07` to `2025-09-14`
      - `2025-09-14` to `2025-09-21`
      - `2025-09-21` to `2025-09-28`
      - `2025-09-28` to `2025-10-05`
      - `2025-10-05` to `2025-10-12`
      - `2025-10-12` to `2025-10-19`
      - `2025-10-19` to `2025-10-26`
      - `2025-10-26` to `2025-11-02`
      - `2025-11-02` to `2025-11-09`
      - `2025-11-09` to `2025-11-16`
      - `2025-11-16` to `2025-11-23`
      - `2025-11-23` to `2025-11-30`
      - `2025-11-30` to `2025-12-07`
      - `2025-12-07` to `2025-12-14`
      - `2025-12-14` to `2025-12-21`
      - `2025-12-21` to `2025-12-28`
      - `2025-12-28` to `2026-01-04`
      - `2026-01-04` to `2026-01-11`
      - `2026-01-11` to `2026-01-18`
      - `2026-01-18` to `2026-01-25`
      - `2026-01-25` to `2026-02-01`
      - `2026-02-01` to `2026-02-08`
      - `2026-02-08` to `2026-02-15`
      - `2026-02-15` to `2026-02-22`
      - `2026-02-22` to `2026-03-01`
      - `2026-03-01` to `2026-03-08`
      - `2026-03-08` to `2026-03-15`
      - `2026-03-15` to `2026-03-22`
      - `2026-03-22` to `2026-03-29`
      - `2026-03-29` to `2026-04-05`
      - `2026-04-05` to `2026-04-12`
      - `2026-04-12` to `2026-04-19`
      - `2026-04-19` to `2026-04-26`
      - `2026-04-26` to `2026-05-02`
  - Spatial range:
    - Use inclusive Sanriku bounds: latitude `38.50–42.50`, longitude `141.00–144.50`.
  - Output names:
    - Cleaned catalog: `Snet_catalog_20250601_20260502.csv`
    - Distribution figure: `Snet_catalog_20250601_20260502_distribution.png`
    - Chunk manifest: `Snet_catalog_20250601_20260502_chunk_manifest.csv`
    - Cleaning summary: `Snet_catalog_20250601_20260502_cleaning_summary.json`
    - Download summary: `Snet_catalog_20250601_20260502_download_summary.json`

- Constraints:
  - Authentication:
    - Maintain a single `requests.Session` across login and all catalog requests.
    - Confirm login success using HTTP status, absence of obvious login-failure markers, and successful access to the catalog endpoint.
  - Network robustness:
    - Apply retry and backoff to login and each catalog request.
    - Record final request status per chunk.
    - Do not silently skip failed chunks.
  - Raw response handling:
    - If `raw-dir` is provided, save raw text/HTML for every chunk.
    - Suggested raw chunk filename pattern: `jma_raw_YYYYMMDD_YYYYMMDD.html`, where the second date is the exclusive chunk end.
    - For unparseable responses, save the failed response as `jma_failed_YYYYMMDD_YYYYMMDD.html` or equivalent and include the saved path in the exception message.
  - Fixed-width parsing:
    - Identify the catalog table region in the returned HTML/text.
    - Parse rows using fixed character positions or a fixed-width reader based on JMA table layout.
    - Extract at minimum event datetime, latitude, longitude, depth, and magnitude.
    - Do not use comma splitting.
    - If the returned page contains no events for a chunk, record a valid zero-row chunk rather than treating it as a parse failure, provided the page structure is recognizable.
  - Cleaning:
    - Parse `datetime` as time.
    - Convert `lat`, `lon`, `dep`, and `mag` to numeric values.
    - Remove rows with missing or non-convertible values in required fields.
    - Filter to `38.50 <= lat <= 42.50` and `141.00 <= lon <= 144.50`.
    - Enforce `2025-06-01 <= datetime < 2026-05-02`.
    - Sort by `datetime`.
    - Remove duplicates after standardizing datetime and numeric fields.
    - Write only the five required columns to the final CSV, in this exact order:
      - `datetime,lat,lon,dep,mag`

- Key calculations:
  - Chunk-level counts:
    - Number of raw parsed rows.
    - Number of rows with valid datetime.
    - Number of rows with valid numeric `lat/lon/dep/mag`.
    - Number of rows inside Sanriku bounds.
    - Minimum and maximum event datetime returned per chunk.
  - Full-catalog cleaning counts:
    - Total parsed rows.
    - Rows removed for missing/invalid required fields.
    - Rows removed outside the requested time interval.
    - Rows removed outside Sanriku bounds.
    - Duplicate rows removed.
    - Final cleaned row count.
  - Final validation metrics:
    - Minimum and maximum datetime in final CSV.
    - Minimum and maximum latitude, longitude, depth, and magnitude.
    - Confirmation that output columns exactly match `datetime,lat,lon,dep,mag`.
    - Confirmation that datetime is sorted monotonically.
    - Confirmation that all rows satisfy inclusive spatial bounds and exclusive end-date rule.

- Figures to draw:
  - Catalog distribution figure saved as `Snet_catalog_20250601_20260502_distribution.png`.
  - Include a map/scatter view of event longitude vs latitude with the Sanriku bounding box.
  - Encode either depth or magnitude visually so spatial distribution and event properties can be inspected.
  - Include supporting distribution panels if practical:
    - Event count through time.
    - Magnitude distribution.
    - Depth distribution.
  - The figure must be generated from the cleaned CSV, not from unfiltered raw rows.

- Key outputs:
  - `Snet_catalog_20250601_20260502.csv`
  - `Snet_catalog_20250601_20260502_distribution.png`
  - `Snet_catalog_20250601_20260502_chunk_manifest.csv`
  - `Snet_catalog_20250601_20260502_cleaning_summary.json`
  - `Snet_catalog_20250601_20260502_download_summary.json`
  - Optional raw chunk files if `raw-dir` is supplied.
  - Debug raw HTML/text file for any unparseable response.

### Task 2 — Validate scientific and workflow completeness after execution

- Task description:
  - Perform post-run validation using the machine-readable summaries and the final cleaned CSV/figure to ensure the workflow satisfies the requested interval, region, schema, and chunking requirements.

- Required data sources:
  - `Snet_catalog_20250601_20260502.csv`
  - `Snet_catalog_20250601_20260502_distribution.png`
  - `Snet_catalog_20250601_20260502_chunk_manifest.csv`
  - `Snet_catalog_20250601_20260502_cleaning_summary.json`
  - `Snet_catalog_20250601_20260502_download_summary.json`

- Parameter selection strategy:
  - Use the same fixed validation parameters:
    - Time interval: `2025-06-01 <= datetime < 2026-05-02`
    - Latitude: `38.50 <= lat <= 42.50`
    - Longitude: `141.00 <= lon <= 144.50`
    - CSV columns: exactly `datetime,lat,lon,dep,mag`
    - Maximum chunk length: 7 days

- Constraints:
  - Final success requires the cleaned CSV to exist, be readable, and have exactly the required schema.
  - Final success requires the distribution figure to exist and be generated from the cleaned catalog.
  - If the final catalog has zero rows, this is not automatically a failure, but the run must prove:
    - all chunks were requested successfully or validly returned no events;
    - parsing did not fail;
    - the zero-row result follows from filtering/cleaning.
  - Successful per-chunk requests alone are not sufficient; the merged cleaned output must be validated.
  - If any chunk has a failed or unparseable response, the workflow is incomplete unless the failed response file is saved and the error clearly reports its path.

- Key validation checks:
  - Chunking:
    - Confirm all 48 half-open chunks are present in the manifest.
    - Confirm no chunk exceeds 7 days.
    - Confirm first chunk starts `2025-06-01`.
    - Confirm final chunk ends `2026-05-02` exclusive.
    - Confirm actual returned date ranges are recorded per chunk.
  - CSV:
    - Confirm filename is `Snet_catalog_20250601_20260502.csv`.
    - Confirm columns are exactly `datetime,lat,lon,dep,mag`.
    - Confirm all required fields are non-missing.
    - Confirm `datetime` parses as time.
    - Confirm `lat/lon/dep/mag` parse as numeric.
    - Confirm all rows satisfy the Sanriku bounds inclusively.
    - Confirm all rows satisfy the requested time interval with exclusive end.
    - Confirm rows are sorted by `datetime`.
    - Confirm there are no duplicate rows.
  - Figure:
    - Confirm `Snet_catalog_20250601_20260502_distribution.png` exists.
    - Confirm the plotted event count matches the cleaned CSV row count.
  - Summaries:
    - Confirm download and cleaning summaries include counts sufficient to audit row loss and chunk completeness.

- Key outputs:
  - Validation status recorded in `Snet_catalog_20250601_20260502_cleaning_summary.json` or a separate compact validation summary if preferred.
  - Final deliverables:
    - `Snet_catalog_20250601_20260502.csv`
    - `Snet_catalog_20250601_20260502_distribution.png`