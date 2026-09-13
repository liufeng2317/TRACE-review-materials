# Goal

Implement and validate an authenticated NIED Hi-net JMA unified hypocenter catalog download workflow for the Sanriku, northeast Japan region, producing an ASPECT-ready cleaned catalog CSV and a catalog distribution figure for the half-open interval 2025-06-01 to 2026-05-02.

## Planning Assumptions

- Use observational catalog data from the authenticated NIED Hi-net JMA unified hypocenter catalog service; do not substitute model or synthetic data.
- Login endpoint: https://hinetwww11.bosai.go.jp/auth/?LANG=en
- Catalog endpoint: https://hinetwww11.bosai.go.jp/auth/JMA/jmalist.php
- Credentials are read by default from `<CASE_ROOT>/data/hinet_account/.env` using keys `HINET_USERNAME` and `HINET_PASSWORD`; command-line credential arguments may override the file values. Credential values must not be printed, logged, or written to outputs.
- Use `requests.Session` for login and all catalog requests so that authentication cookies/state are preserved.
- Add retry and backoff to login and catalog requests; failed final HTML/text responses that cannot be parsed must be saved to a debug/raw file, and the raised error must include the saved file path.
- The requested interval is fixed and manuscript-aligned: start date `2025-06-01`, exclusive end date `2026-05-02`; requested records must cover `2025-06-01` through `2026-05-01`. Do not replace with current-date, 2026-only, or other defaults.
- Split catalog requests into chunks of no more than 7 days using half-open boundaries: `[chunk_start, chunk_end)`, with the final chunk ending exactly at `2026-05-02`.
- Apply Sanriku bounds inclusively after parsing: latitude `38.50 <= lat <= 42.50`, longitude `141.00 <= lon <= 144.50`.
- Parse the JMA fixed-width catalog table using column positions or robust fixed-width extraction inferred from the JMA table/scaffold/reference files; do not use comma splitting.
- ASPECT-ready output CSV must contain exactly these columns in this order: `datetime,lat,lon,dep,mag`.
- Primary cleaned catalog filename: `Snet_catalog_20250601_20260502.csv`.
- Catalog distribution figure filename: `Snet_catalog_20250601_20260502_distribution.png`.
- Existing active `00_catalog_download` output is empty, so the workflow must generate fresh cleaned and figure outputs.

## Analysis Plan

### Task 1: Build and validate the authenticated JMA catalog download workflow

- Task description:
  - Implement one primary workflow script, `download_sanriku_jma_catalog.py`, that performs credential loading, authenticated login, chunked catalog requests, optional raw response saving, fixed-width parsing, cleaning, validation, CSV export, and distribution plotting.
  - Keep configuration/input preparation, session validation, execution, chunk-level checks, merged-output validation, and failure evidence collection inside this script.

- Required data sources:
  - NIED Hi-net login endpoint: `https://hinetwww11.bosai.go.jp/auth/?LANG=en`
  - NIED Hi-net JMA catalog endpoint: `https://hinetwww11.bosai.go.jp/auth/JMA/jmalist.php`
  - Credential file: `<CASE_ROOT>/data/hinet_account/.env`
  - Local `catalog_construction_from_JMA` workflow scaffold and previously parsed regional event/pick/station/phase products may be used only to verify request fields and fixed-width parsing expectations.

- Parameter selection strategy:
  - Fixed request interval:
    - `start_date = 2025-06-01`
    - `end_date_exclusive = 2026-05-02`
  - Generate chunk boundaries as half-open windows of length at most 7 days:
    - first chunk starts `2025-06-01`;
    - each chunk end is `min(chunk_start + 7 days, 2026-05-02)`;
    - final chunk must end `2026-05-02`.
  - Record for each chunk:
    - requested `chunk_start`;
    - requested exclusive `chunk_end`;
    - actual minimum and maximum parsed event dates returned;
    - number of parsed rows before cleaning;
    - number of rows after Sanriku filtering.
  - Spatial cleaning bounds:
    - latitude minimum `38.50`, maximum `42.50`, inclusive;
    - longitude minimum `141.00`, maximum `144.50`, inclusive.
  - Output filenames:
    - cleaned CSV: `Snet_catalog_20250601_20260502.csv`;
    - distribution figure: `Snet_catalog_20250601_20260502_distribution.png`;
    - chunk manifest: `Snet_catalog_20250601_20260502_chunks.csv` or JSON equivalent;
    - validation summary: `Snet_catalog_20250601_20260502_validation.json`.
  - Optional raw response argument:
    - If provided, save raw text/HTML response for every chunk using filenames that encode the chunk start and exclusive end dates.
    - If not provided, save only failed/unparseable responses to a debug/raw file.

- Constraints:
  - Authentication:
    - Read `.env` credentials by default.
    - Allow command-line overrides for username and password.
    - Use a single `requests.Session` for login and subsequent catalog requests.
    - Do not expose credentials in logs, errors, manifests, or saved request metadata.
  - Network robustness:
    - Apply retry and backoff to login and each chunk request.
    - Treat non-success HTTP status, timeout, login failure, and empty unexpected content as recoverable until retries are exhausted.
    - On final failure, preserve enough non-sensitive evidence for diagnosis.
  - Parsing:
    - Parse fixed-width JMA table records only.
    - Do not split event rows by commas.
    - Detect and skip non-data header/footer/navigation lines.
    - Convert JMA date/time fields into a single `datetime` value.
    - Convert latitude, longitude, depth, and magnitude into numeric fields.
    - If no fixed-width event rows can be parsed from an apparently successful response, save the original response to a debug/raw file and raise an error containing that saved path.
  - Cleaning:
    - Remove rows with missing `datetime`, `lat`, `lon`, `dep`, or `mag`.
    - Apply inclusive Sanriku spatial filtering after numeric conversion.
    - Sort by `datetime`.
    - Remove duplicate events using the cleaned ASPECT columns, with duplicate checking after sorting.
    - Export only `datetime,lat,lon,dep,mag`, in that exact order.
  - Time validation:
    - Ensure all retained datetimes satisfy `2025-06-01 <= datetime < 2026-05-02`.
    - Check that the final date coverage can include events through `2026-05-01`.
    - Do not accept output generated from any default interval other than the requested manuscript interval.
  - Chunk validation:
    - No chunk may exceed 7 days.
    - The concatenated chunks must cover the half-open interval continuously without gaps or overlaps.
    - The manifest must record exact requested boundaries and actual returned date ranges.
  - Output validation:
    - Successful execution requires the cleaned CSV file to exist, be readable, have exactly the required columns, and contain non-empty data unless the service genuinely returns no Sanriku events; if empty, the validation summary must explicitly document parsed pre-filter counts and filtering losses.
    - Successful execution also requires the distribution figure to exist and be generated from the cleaned catalog.
    - A mock, placeholder, schema-only, or diagnostic-only CSV/figure must not be treated as success.

- Key calculations:
  - Chunk construction:
    - Compute all half-open request windows between `2025-06-01` and `2026-05-02` with maximum length 7 days.
  - Catalog parsing:
    - Extract event origin time, latitude, longitude, depth, and magnitude from the fixed-width JMA table.
  - Cleaning metrics:
    - Total rows parsed before cleaning.
    - Rows removed for missing values.
    - Rows removed outside Sanriku bounds.
    - Rows removed as duplicates.
    - Final retained event count.
  - Temporal metrics:
    - Earliest and latest retained event datetime.
    - Per-chunk actual minimum and maximum returned dates.
    - Events per chunk after spatial filtering.
  - Spatial/magnitude/depth metrics:
    - Latitude, longitude, depth, and magnitude min/max.
    - Event counts by month.
    - Optional counts by magnitude bin for figure annotation or validation table, using explicit bin edges chosen in the script rather than inferred from magnitude decimal places.

- Figures to draw:
  - Catalog distribution figure generated from the cleaned catalog:
    - Map-style scatter of longitude versus latitude for retained Sanriku events.
    - Points colored by depth or magnitude.
    - Sanriku bounding box shown explicitly.
    - Optional marginal or companion panels for event counts through time and magnitude/depth distribution if supported in the same figure.
  - The figure must visually confirm that retained events lie within `38.50–42.50°N` and `141.00–144.50°E`.

- Key outputs:
  - `Snet_catalog_20250601_20260502.csv`
    - Columns exactly: `datetime,lat,lon,dep,mag`.
    - Sorted by `datetime`.
    - Deduplicated.
    - Filtered to Sanriku bounds.
  - `Snet_catalog_20250601_20260502_distribution.png`
    - Catalog distribution figure based on the final cleaned CSV.
  - `Snet_catalog_20250601_20260502_chunks.csv` or JSON equivalent
    - Exact chunk request boundaries and actual returned date ranges.
  - `Snet_catalog_20250601_20260502_validation.json`
    - Non-sensitive execution summary, cleaning counts, time/span checks, bounds checks, duplicate count, and output existence checks.
  - Optional raw response files
    - One per chunk if raw-dir is provided.
    - Failed/unparseable response saved automatically with its path reported in the error message.

### Task 2: Execute workflow validation and acceptance checks

- Task description:
  - Run the primary workflow for the fixed Sanriku interval and verify that all required outputs are valid scientific products, not placeholders.

- Required data sources:
  - Outputs from Task 1:
    - `Snet_catalog_20250601_20260502.csv`
    - `Snet_catalog_20250601_20260502_distribution.png`
    - chunk manifest
    - validation summary
    - any saved raw/debug files if parsing failures occur.

- Parameter selection strategy:
  - Use the same fixed parameters as Task 1.
  - Validate against the explicit interval and Sanriku bounds, not against inferred defaults.

- Constraints:
  - Required validation checks:
    - CSV exists and is readable.
    - CSV columns are exactly `datetime,lat,lon,dep,mag`.
    - `datetime` parses as time.
    - `lat`, `lon`, `dep`, and `mag` are numeric.
    - No missing values remain.
    - All retained rows satisfy `2025-06-01 <= datetime < 2026-05-02`.
    - All retained rows satisfy inclusive Sanriku bounds.
    - Rows are sorted by `datetime`.
    - No duplicate rows remain.
    - Chunk manifest has continuous, non-overlapping coverage and every chunk is at most 7 days.
    - Distribution figure exists and is generated from the cleaned CSV.
  - If the final catalog is empty:
    - Do not silently accept it.
    - Confirm that raw parsed rows existed or document that the authenticated service returned no parseable Sanriku events.
    - Include pre-filter and post-filter counts in the validation summary.

- Key outputs:
  - Final acceptance status recorded in `Snet_catalog_20250601_20260502_validation.json`.
  - Cleaned ASPECT-ready CSV and distribution figure ready for downstream Sanriku/ASPECT use.