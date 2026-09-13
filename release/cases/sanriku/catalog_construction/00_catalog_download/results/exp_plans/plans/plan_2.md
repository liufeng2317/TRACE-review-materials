# Goal

Implement and validate an authenticated NIED Hi-net JMA unified hypocenter catalog download workflow for the Sanriku, northeast Japan study region, producing an ASPECT-ready cleaned CSV and catalog distribution figure for 2025-06-01 to 2026-05-02 with the end date treated as exclusive.

## Planning Assumptions

- Observation data are available and suitable through the authenticated NIED Hi-net JMA unified hypocenter catalog service; no model data are needed.
- Authentication must use:
  - Login endpoint: `https://hinetwww11.bosai.go.jp/auth/?LANG=en`
  - Catalog endpoint: `https://hinetwww11.bosai.go.jp/auth/JMA/jmalist.php`
- Credentials should be read first from:
  - `<CASE_ROOT>/data/hinet_account/.env`
  - keys: `HINET_USERNAME`, `HINET_PASSWORD`
  - command-line username/password arguments may override the `.env` values.
- Credentials must not be written to logs, manifests, raw files, error messages, figures, or CSV outputs.
- The requested time interval is fixed by the user:
  - start: `2025-06-01`
  - end exclusive: `2026-05-02`
  - requested records should cover `2025-06-01` through `2026-05-01`.
- The Sanriku bounds are fixed and must be applied inclusively after parsing:
  - latitude: `38.50 <= lat <= 42.50`
  - longitude: `141.00 <= lon <= 144.50`
- JMA request chunks must be no longer than 7 days.
- The cleaned ASPECT-ready CSV must contain exactly these columns, in this order:
  - `datetime,lat,lon,dep,mag`
- Primary output filename:
  - `Snet_catalog_20250601_20260502.csv`
- Distribution figure filename:
  - `Snet_catalog_20250601_20260502_distribution.png`
- A chunk/request manifest should also be produced to satisfy validation requirements:
  - `Snet_catalog_20250601_20260502_chunk_manifest.csv`
- Package/program contract constraints:
  - Use `requests.Session` for login and all catalog requests.
  - Add retry and exponential backoff or equivalent bounded backoff for login and catalog requests.
  - Preserve an optional `raw-dir` argument for saving raw response text from each chunk.
  - If an HTML/catalog response cannot be parsed, save the original failed response to a debug/raw file and include that saved path in the raised error message.
  - Parse the JMA fixed-width catalog table; do not parse the catalog by comma splitting.
  - Successful execution requires a valid, non-empty cleaned CSV when events exist for the requested interval and region, a valid distribution figure, and a manifest recording chunk boundaries and actual returned dates.

## Analysis Plan

### Task 1 — Implement the authenticated JMA catalog download, parsing, cleaning, validation, and plotting workflow

- Task description:
  - Create one cohesive workflow script that logs in to Hi-net, queries the JMA unified hypocenter catalog in 7-day-or-shorter chunks, parses fixed-width catalog rows, cleans and filters the catalog for the Sanriku region, writes the ASPECT-ready CSV, records chunk metadata, and produces a distribution figure.

- Required data sources:
  - `https://hinetwww11.bosai.go.jp/auth/?LANG=en`
  - `https://hinetwww11.bosai.go.jp/auth/JMA/jmalist.php`
  - `<CASE_ROOT>/data/hinet_account/.env`
  - Existing local workflow scaffold and previously parsed regional products under the surrounding `catalog_construction_from_JMA` directory, used only to verify login/request field names and fixed-width parsing conventions if needed.

- Parameter selection strategy:
  - Hard-code or expose as defaults the manuscript-aligned interval:
    - `start_date = 2025-06-01`
    - `end_date_exclusive = 2026-05-02`
  - Generate request chunks as half-open intervals `[chunk_start, chunk_end)` with `chunk_end <= chunk_start + 7 days` and `chunk_end <= 2026-05-02`.
  - Expected chunk sequence:
    - `2025-06-01` to `2025-06-08`
    - `2025-06-08` to `2025-06-15`
    - continue in 7-day increments
    - final chunk ending at `2026-05-02`
  - Use inclusive spatial filtering after parsing:
    - `lat_min = 38.50`
    - `lat_max = 42.50`
    - `lon_min = 141.00`
    - `lon_max = 144.50`
  - Credentials:
    - default source: `.env`
    - optional CLI overrides: username/password
    - fail early with a clear non-sensitive error if credentials are missing.
  - Optional raw output:
    - if `raw-dir` is supplied, save raw text/HTML for every successful chunk.
    - always save failed/unparseable responses to a debug/raw file, even if `raw-dir` was not supplied.

- Constraints:
  - Use `requests.Session` from login through all chunk requests.
  - Apply retries and backoff to login and each catalog request.
  - Do not substitute the requested time interval with current date, system date, or a 2026-only default.
  - Respect the JMA service limit by never requesting more than 7 days in a single chunk.
  - Do not use fragile comma splitting for catalog rows.
  - Fixed-width parsing should:
    - extract the catalog text/table region from the returned HTML;
    - identify valid event rows;
    - parse date/time fields into one `datetime`;
    - parse latitude, longitude, depth, and magnitude from their fixed character spans or verified scaffold-derived fixed-width schema;
    - ignore headers, separators, empty lines, and non-event rows.
  - On parse failure:
    - save the full original response to a raw/debug file;
    - include the saved file path in the error message;
    - do not silently return an empty catalog for that chunk.
  - Cleaning must be applied in this order:
    - parse `datetime` as time;
    - convert `lat`, `lon`, `dep`, `mag` to numeric values;
    - remove rows with missing required values;
    - filter inclusively to the Sanriku bounds;
    - sort by `datetime`;
    - remove duplicates.
  - The final CSV must contain exactly:
    - `datetime,lat,lon,dep,mag`
  - The final CSV must not include auxiliary columns such as event ID, place name, chunk ID, quality flags, or raw text.

- Calculations and validation:
  - For each chunk, record:
    - chunk index;
    - requested start date;
    - requested end date exclusive;
    - requested duration in days;
    - HTTP status code;
    - raw response file path if saved;
    - number of parsed rows before cleaning;
    - number of rows after numeric/time parsing;
    - number of rows after Sanriku filtering;
    - earliest and latest parsed event datetime returned by the service;
    - earliest and latest retained Sanriku event datetime;
    - parse status and error/debug path if applicable.
  - After all chunks are processed:
    - concatenate chunk data;
    - verify all retained event datetimes satisfy `2025-06-01 <= datetime < 2026-05-02`;
    - verify all retained lat/lon values satisfy the inclusive Sanriku bounds;
    - verify `dep` and `mag` are numeric and non-missing;
    - verify duplicate rows were removed;
    - verify final rows are sorted by `datetime`;
    - verify the CSV has exactly five columns in the required order.
  - If the cleaned catalog is empty:
    - still write a valid empty CSV with the required header only;
    - write the manifest;
    - produce a diagnostic figure indicating no retained events only if plotting logic can do so unambiguously;
    - report that the query returned no events after cleaning/filtering rather than treating parser failure as success.

- Key outputs:
  - `Snet_catalog_20250601_20260502.csv`
    - ASPECT-ready cleaned catalog with exactly `datetime,lat,lon,dep,mag`.
  - `Snet_catalog_20250601_20260502_chunk_manifest.csv`
    - exact request chunk boundaries and actual returned date ranges/counts.
  - `Snet_catalog_20250601_20260502_distribution.png`
    - catalog distribution figure.
  - Optional raw files:
    - one raw response per chunk if `raw-dir` is provided.
  - Mandatory debug/raw files:
    - saved original response for any unparseable HTML/catalog response.

### Task 2 — Produce the catalog distribution figure and basic scientific diagnostics inside the same workflow

- Task description:
  - Generate a compact distribution figure from the cleaned Sanriku catalog and validate that it reflects the final CSV contents.

- Required data sources:
  - Cleaned in-memory catalog produced by Task 1.
  - Written CSV `Snet_catalog_20250601_20260502.csv` for cross-checking figure data consistency.

- Parameter selection strategy:
  - Use only cleaned, retained Sanriku events.
  - Plot extent should cover at least:
    - latitude `38.50` to `42.50`
    - longitude `141.00` to `144.50`
  - Use `datetime`, `lat`, `lon`, `dep`, and `mag` from the final CSV.
  - If depth and magnitude are available for all retained rows after cleaning, include them in diagnostic summaries.

- Constraints:
  - Do not plot unfiltered raw catalog rows.
  - Do not use events outside the requested date interval or outside the Sanriku bounds.
  - Figure generation should fail if the CSV schema is not exactly `datetime,lat,lon,dep,mag`.

- Recommended figure contents:
  - Map panel:
    - event epicenters within the Sanriku bounds;
    - optional color scale by depth or event time;
    - optional marker scaling by magnitude.
  - Temporal panel:
    - event counts through time, aggregated by day or another documented bin width.
  - Magnitude/depth diagnostic:
    - histogram of magnitude and/or depth, using the cleaned numeric fields.
  - If no retained events exist:
    - create a clear no-events diagnostic figure rather than an empty misleading map.

- Key outputs:
  - `Snet_catalog_20250601_20260502_distribution.png`
  - Optional machine-readable summary:
    - `Snet_catalog_20250601_20260502_summary.json` containing final row count, datetime min/max, lat/lon min/max, depth min/max, magnitude min/max, and duplicate-removal count.