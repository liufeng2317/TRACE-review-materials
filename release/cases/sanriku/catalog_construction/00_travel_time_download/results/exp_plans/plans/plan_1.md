# Goal

Independently download, parse, validate, and export JMA/Hi-net arrival-time measure files for 2025-06-01 ≤ time < 2026-05-02, producing full and Sanriku-regional event/pick catalogs plus project-convention `phase.dat` and `station.sta` products.

## Planning Assumptions

- Use observational data from Hi-net/JMA only; no model data are needed.
- Credentials:
  - Read Hi-net credentials from environment variables first, then from `<CASE_ROOT>/data/hinet_account/.env`.
  - Support either one account or multiple accounts.
  - Never print, serialize, or log passwords.
- HinetPy package contract:
  - Main interface: `HinetPy.Client(username, password)`.
  - Arrival-time download entry point: `Client.get_arrivaltime(startdate, span, filename=None, os="DOS" or "UNIX")`.
  - `startdate` is a date/datetime/string, `span` is in days, and the return value is the saved filename.
  - HinetPy/Hi-net times are JST; parsed structured timestamps must be converted to UTC.
- JMA arrival-time format contract:
  - Raw measure files are fixed-width records, 96 bytes per record excluding line endings.
  - Event/hypocenter records begin with `J`.
  - Station arrival records begin with `_`.
  - Event terminator records begin with `E`.
  - Parsing must use documented byte/column slices, not comma splitting or free-width parsing.
- Existing `data/regional/phase.dat` is used only as the format reference for the project-specific block convention; it must not be treated as source data for the new catalog.
- The requested end date is exclusive: download and parse chunks covering 2025-06-01 through 2026-05-01 only.
- Chunking strategy: default 5-day chunks; the final chunk may be shorter; no chunk may exceed 7 days.
- Spatial filtering is applied locally after parsing using event hypocenter latitude/longitude:
  - 38.50 ≤ latitude ≤ 42.50
  - 141.00 ≤ longitude ≤ 144.50

## Analysis Plan

### Task 1 — Build one primary download-parse-validate workflow script

- Task description:
  - Implement the complete workflow in one cohesive script: credential loading, chunk construction, smoke-test download, fixed-width parsing, validation, full-range download, full parsing, regional filtering, and output writing.
  - Keep retry/backoff, manifest generation, parsing validation, and merged-output checks in the same script so that successful execution requires valid scientific outputs, not only successful requests.

- Required data sources:
  - `<CASE_ROOT>/data/hinet_account/.env`
  - `data/regional/phase.dat` for output-format tracing only.
  - Hi-net/JMA arrival-time service through HinetPy.

- Parameter selection strategy:
  - Time interval:
    - `start_date = 2025-06-01`
    - `exclusive_end_date = 2026-05-02`
    - chunk starts are generated as half-open windows `[chunk_start, chunk_end)`.
    - preferred span is 5 days.
    - final span is `min(5, exclusive_end_date - chunk_start)`.
  - Smoke-test window:
    - `2025-06-01 <= time < 2025-06-06`
    - raw filename: `measure_20250601_5.txt`
  - Raw file naming:
    - `measure_YYYYMMDD_N.txt`, where `YYYYMMDD` is chunk start in JST request date and `N` is span in days.
  - Download behavior:
    - If the target raw file already exists and has size > 0, skip download by default and mark manifest status as `skipped_existing`.
    - If absent or zero-byte, request via HinetPy.
    - Use retry with exponential backoff for failed requests.
    - Rotate through multiple available accounts only after a failed request or account-specific error; do not expose account secrets.
  - HinetPy request settings:
    - Use `Client.get_arrivaltime(startdate=chunk_start, span=span_days, filename=raw_file, os="UNIX")` where supported.
    - If line endings differ, normalize only during parsing; preserve downloaded raw files.

- Constraints:
  - Do not use current date, a 2026-only interval, or any default interval.
  - Do not apply geographic bounds during download.
  - Do not overwrite non-empty raw files unless an explicit overwrite option is provided and enabled.
  - Passwords must be redacted from all status messages and exception summaries.
  - Manifest rows must be written for both skipped and attempted chunks.

- Key outputs:
  - `download_manifest.csv` with columns:
    - `start_date`
    - `span_days`
    - `raw_file`
    - `exists`
    - `size_bytes`
    - `status`
    - `message`
  - One raw measure file per chunk, named like `measure_20250601_5.txt`.

---

### Task 1.1 — Credential discovery and account handling

- Task description:
  - Load Hi-net usernames/passwords securely from environment variables or the specified `.env` file.
  - Support both single-account and multi-account conventions.

- Required data sources:
  - `.env` path specified above.
  - Runtime environment variables.

- Parameter selection strategy:
  - Search for common single-account keys such as username/user and password/pass variants.
  - Search for indexed account patterns if present, such as account 1, account 2, etc.
  - Validate that each account has both a username and password before use.
  - Keep only usernames in diagnostics; mask passwords completely.

- Constraints:
  - If no valid account pair is found, stop before download and write a failure status explaining missing credentials without printing any secret-like value.
  - Do not save credentials into output tables, manifests, or logs.

- Key outputs:
  - Internal validated account list.
  - Redacted credential-loading status in workflow summary.

---

### Task 1.2 — Chunk schedule generation and manifest initialization

- Task description:
  - Generate deterministic non-overlapping request chunks for the full half-open time range.

- Required data sources:
  - User-requested time interval.

- Parameter selection strategy:
  - Generate 5-day chunks from 2025-06-01.
  - Use shorter final chunk if needed to end exactly at 2026-05-02 exclusive.
  - Confirm all spans are between 1 and 5 days and therefore ≤ 7 days.
  - Confirm the union of chunks exactly equals `[2025-06-01, 2026-05-02)`.

- Constraints:
  - No gaps and no overlaps.
  - Do not request 2026-05-02 or later.
  - Do not change the requested interval based on runtime date.

- Key outputs:
  - Internal chunk table.
  - `chunk_schedule.csv` with:
    - `chunk_index`
    - `start_date`
    - `end_date_exclusive`
    - `span_days`
    - `raw_file`

---

### Task 1.3 — Smoke-test download for 2025-06-01 to 2025-06-06 exclusive

- Task description:
  - Before the full run, download or reuse the first five-day measure file and validate the raw and parsed content.

- Required data sources:
  - Hi-net/JMA via HinetPy.
  - `.env` credentials.
  - Raw target file `measure_20250601_5.txt`.

- Parameter selection strategy:
  - Request:
    - `startdate = 2025-06-01`
    - `span = 5`
    - `filename = measure_20250601_5.txt`
  - Retry/backoff:
    - Use a bounded number of retry attempts per account.
    - Increase wait time after each failure.
    - If multiple accounts exist, try the next account after persistent failure.

- Constraints:
  - Non-empty existing raw file is accepted as the smoke-test raw input and marked as skipped-existing.
  - A zero-byte existing file is treated as failed/incomplete and must be re-requested or marked failed.
  - Smoke-test success requires raw-file validation and parsing validation, not only a HinetPy return value.

- Key outputs:
  - Smoke-test manifest row in `download_manifest.csv`.
  - Smoke raw-file QC summary:
    - file exists
    - size in bytes
    - number of records
    - number of invalid-length records
    - count of `J`, `_`, and `E` records

---

### Task 1.4 — Fixed-width parser implementation

- Task description:
  - Parse all downloaded JMA measure files using fixed-width byte/column slices and produce normalized event and pick records.

- Required data sources:
  - Raw `measure_YYYYMMDD_N.txt` files.
  - JMA fixed-width format definition.

- Parameter selection strategy:
  - For every physical line:
    - Strip only line terminators.
    - Validate that the encoded record length is 96 bytes after removing line endings.
    - Identify record type from byte/column 1.
  - Event header `J` records:
    - Parse JST origin time fields.
    - Parse latitude from degrees/minutes fields and convert to decimal degrees.
    - Parse longitude from degrees/minutes fields and convert to decimal degrees.
    - Parse depth in km.
    - Parse magnitude.
    - Parse region text.
    - Convert origin time from JST to UTC ISO string.
  - Station `_` records:
    - Parse station code.
    - Parse station number.
    - Parse first and second phase fields.
    - Identify P and S arrivals from phase-name fields.
    - Parse P/S quality and data information fields according to fixed columns.
    - Parse data weight.
    - Convert arrival times from JST to UTC ISO strings.
    - Represent missing P or missing S as `-1`.
  - Event terminator `E` records:
    - Close the current event block.
    - Finalize event pick counts.
  - Event IDs:
    - Assign deterministic event IDs from source file and event sequence, with an origin-time component when available, e.g. `JMA_YYYYMMDDHHMMSSffffff_<source-stem>_<event_index>`.
    - Ensure uniqueness across all chunks.

- Constraints:
  - Do not parse raw records using comma splitting, whitespace splitting, or project `phase.dat` conventions.
  - Do not infer precision from decimal places alone; use documented fields and store parsed numeric values as normalized floats.
  - If an arrival second rounds to 60.00, normalize timestamp rollover correctly.
  - If arrival records provide day/hour/min/sec without full year context, resolve the date relative to the current event origin and documented record date fields.
  - Preserve the raw source filename in every event and pick record.

- Key outputs:
  - Full parsed event table in memory.
  - Full parsed pick table in memory.
  - Parser QC table with:
    - `source_file`
    - `n_lines`
    - `n_valid_96byte_records`
    - `n_invalid_length_records`
    - `n_event_headers`
    - `n_pick_records`
    - `n_terminators`
    - `n_unrecognized_records`
    - `n_closed_events`
    - `n_events_with_no_terminator`

---

### Task 1.5 — Smoke-test validation gate

- Task description:
  - Validate the first chunk before permitting the complete time-range run.

- Required data sources:
  - Smoke raw file `measure_20250601_5.txt`.
  - Smoke parsed events and picks.

- Parameter selection strategy:
  - Required checks:
    - raw file exists and is non-empty.
    - all non-empty records are 96 bytes excluding line endings, or invalid records are explicitly counted and investigated.
    - at least one recognized record type is present unless the service legitimately returns an empty no-data file with documented status.
    - every pick `event_id` exists in `events.csv` candidate table.
    - each event `npicks` equals the number of pick rows linked by `event_id`.
    - P/S pick counts are computed:
      - `n_p_picks = count(p_pick_time != -1)`
      - `n_s_picks = count(s_pick_time != -1)`
      - `n_both_ps = count(p_pick_time != -1 and s_pick_time != -1)`
      - `n_missing_p`
      - `n_missing_s`
    - UTC conversion check:
      - timestamps are ISO strings.
      - parsed UTC times are 9 hours earlier than raw JST fields, allowing date rollover.
  - If smoke parsing yields zero events but the raw file is non-empty, treat as failure unless raw records clearly indicate no data.

- Constraints:
  - Full-range processing starts only after this validation gate passes.
  - Parser fallback, mock output, or schema-only output cannot satisfy the smoke test.

- Key outputs:
  - `smoke_qc_summary.csv`
  - Smoke subset candidate outputs:
    - `events_smoke.csv`
    - `picks_smoke.csv`
  - Workflow status flag: `smoke_passed = true/false`

---

### Task 1.6 — Complete time-range download and merged parsing

- Task description:
  - After smoke success, run all chunks from 2025-06-01 to 2026-05-02 exclusive, download missing raw files, and parse all valid raw files into merged full catalogs.

- Required data sources:
  - All scheduled raw measure files.
  - Hi-net/JMA via HinetPy for missing or zero-byte chunks.
  - Smoke-tested parser.

- Parameter selection strategy:
  - Iterate through all chunk rows generated in Task 1.2.
  - Reuse any non-empty raw files.
  - Download only missing or zero-byte files by default.
  - Parse every valid non-empty raw file.
  - Add each chunk’s final status to `download_manifest.csv`.
  - Exclude failed chunks from merged scientific tables but record failure in manifest and QC summary.

- Constraints:
  - The merged catalog is valid only if:
    - all expected chunks are represented in the manifest.
    - all successfully downloaded or skipped-existing non-empty raw files were parsed.
    - event IDs are unique.
    - all pick rows reference existing event IDs.
  - If any chunk fails to download, output partial products only with explicit partial-run status in QC tables.

- Key outputs:
  - `events_full.csv` with columns:
    - `event_id`
    - `origin_time`
    - `latitude`
    - `longitude`
    - `depth_km`
    - `magnitude`
    - `region`
    - `npicks`
    - `source_file`
  - `picks_full.csv` with columns:
    - `event_id`
    - `station_code`
    - `station_number`
    - `p_pick_time`
    - `s_pick_time`
    - `p_quality`
    - `s_quality`
    - `weight`
    - `source_file`
  - `parse_qc_by_file.csv`
  - `catalog_qc_summary.csv`

---

### Task 1.7 — Sanriku regional subset generation

- Task description:
  - Apply the requested Sanriku spatial filter locally to the merged full event table and subset the pick table by retained event IDs.

- Required data sources:
  - `events_full.csv`
  - `picks_full.csv`

- Parameter selection strategy:
  - Regional filter:
    - `38.50 <= latitude <= 42.50`
    - `141.00 <= longitude <= 144.50`
  - Retain all picks associated with retained events.
  - Recompute `npicks` for regional events from the regional pick table.

- Constraints:
  - Do not use any download-side geographic filtering.
  - Do not filter picks independently by station location unless a separate station-level diagnostic is needed.
  - Keep full and regional outputs separate.

- Key outputs:
  - `events_regional.csv`
  - `picks_regional.csv`
  - Regional QC metrics in `catalog_qc_summary.csv`:
    - number of full events
    - number of regional events
    - number of full picks
    - number of regional picks
    - regional P-pick count
    - regional S-pick count
    - regional missing-P count
    - regional missing-S count

---

### Task 1.8 — Project-convention `phase.dat` and `station.sta` export

- Task description:
  - Write project-compatible phase and station files for the regional subset, using the existing `data/regional/phase.dat` convention as the format reference.

- Required data sources:
  - `data/regional/phase.dat`
  - `events_regional.csv`
  - `picks_regional.csv`
  - Available station reference text in the project data tree, if present.
  - Existing regional station convention, if an existing `station.sta` is found near the reference products.

- Parameter selection strategy:
  - `phase.dat` convention discovery:
    - Read `data/regional/phase.dat`.
    - Identify event header line pattern and station pick line pattern.
    - Preserve comma-separated project block convention.
    - Preserve `-1` representation for missing P or S arrivals.
    - Do not use HASH-style, `#`-prefixed, or whitespace-delimited formats.
  - `phase.dat` regional export:
    - For each regional event, write one event header block line with event metadata.
    - Write following station pick lines for all associated picks.
    - Use UTC ISO timestamps as in the existing convention unless the reference file proves otherwise.
    - Keep source traceability by ensuring event IDs map back to `events_regional.csv`.
  - `station.sta` export:
    - Build the unique regional station list from `picks_regional.csv`.
    - Merge station coordinates and metadata from available station reference text or existing project station reference files.
    - Preserve the existing project `station.sta` field order and delimiter if a reference file is found.
    - If some station coordinates are unavailable, include only validated station metadata in `station.sta` and write a station-metadata gap report.

- Constraints:
  - `events_regional.csv` and `picks_regional.csv` remain the primary structured outputs.
  - `phase.dat` must be traceable to the normalized CSV tables.
  - Do not synthesize station coordinates.
  - Do not silently drop stations from `station.sta`; any missing metadata must be reported.

- Key outputs:
  - `phase_regional.dat`
  - `station_regional.sta`
  - `phase_dat_traceability.csv` with:
    - `event_id`
    - `phase_block_index`
    - `n_pick_rows_written`
    - `source_file`
  - `station_metadata_qc.csv` with:
    - `station_code`
    - `station_number`
    - `in_picks_regional`
    - `metadata_found`
    - `latitude`
    - `longitude`
    - `source_reference`

---

### Task 1.9 — Final validation and diagnostic figures

- Task description:
  - Validate all final outputs and generate diagnostic figures for download completeness, parsing quality, catalog coverage, and pick completeness.

- Required data sources:
  - `download_manifest.csv`
  - `parse_qc_by_file.csv`
  - `events_full.csv`
  - `picks_full.csv`
  - `events_regional.csv`
  - `picks_regional.csv`
  - `phase_regional.dat`
  - `station_regional.sta`

- Parameter selection strategy:
  - Table validation:
    - Required columns exist exactly as requested.
    - `event_id` unique in event tables.
    - all pick `event_id` values exist in corresponding event table.
    - `npicks` equals linked pick count.
    - UTC timestamp strings are parseable.
    - missing arrivals are exactly `-1`.
    - no non-empty parsed raw file has unreported invalid record lengths.
  - Manifest validation:
    - all expected chunk starts are present.
    - all spans are ≤ 7 days.
    - first chunk is exactly 2025-06-01 with span 5.
    - final chunk ends at 2026-05-02 exclusive.
    - statuses are one of:
      - `downloaded`
      - `skipped_existing`
      - `failed`
      - `parse_failed`
      - `empty`
  - Regional validation:
    - all regional event latitudes/longitudes are within requested bounds.
    - all regional picks link to regional events.
  - Phase/station validation:
    - number of event blocks in `phase_regional.dat` equals number of rows in `events_regional.csv`.
    - number of station pick lines in `phase_regional.dat` equals number of rows in `picks_regional.csv`, unless explicitly documented by the existing convention.
    - all stations in `station_regional.sta` are traceable to regional picks and station metadata.

- Constraints:
  - Do not mark the workflow successful if only raw downloads exist but parsed catalogs are empty or invalid.
  - Do not mark partial products as complete if any required chunk failed.
  - Diagnostic-only outputs cannot replace the requested CSV/dat/sta products.

- Key outputs:
  - `final_validation_summary.csv`
  - Diagnostic figures:
    - Chunk timeline/status plot from `download_manifest.csv`.
    - Raw file size by chunk start date.
    - Event count by chunk/date for full and regional catalogs.
    - Map of full events and Sanriku regional subset with requested bounding box.
    - Magnitude-depth scatter or magnitude histogram for full and regional events.
    - P-pick and S-pick count time series by day.
    - Per-event pick-count histogram.
    - Station pick-count map or station pick-count bar chart, depending on available station coordinates.