# Goal

Independently download, parse, subset, and validate JMA/Hi-net arrival-time measure files for the Sanriku study region for 2025-06-01 through 2026-05-01, producing raw chunk files, normalized event/pick CSV tables, project-convention `phase.dat`, `station.sta`, manifests, and QC figures.

## Planning Assumptions

- Use observational data only: JMA arrival-time measure files downloaded through the Hi-net/HinetPy arrival-time interface, plus local project reference files.
- HinetPy package contract:
  - Main API: `HinetPy.Client(username, password)` and `client.get_arrivaltime(startdate, span, filename=None, os='DOS')`.
  - `startdate` may be a string/date/datetime; `span` is an integer number of days.
  - `get_arrivaltime` returns the saved filename.
  - HinetPy/Hi-net times are JST, UTC+09:00.
  - File naming by default follows `measure_YYYYMMDD_N.txt`; the workflow will explicitly pass the required filename.
- JMA measure format contract:
  - Arrival-time measure records are fixed-width records of 96 bytes excluding the line ending.
  - Event/hypocenter records begin with `J`.
  - Station arrival records begin with `_`.
  - Event terminator records begin with `E`.
  - Times in raw records are JST and must be converted to UTC ISO strings in structured outputs.
- Required local inputs:
  - Hi-net account `.env`: `<CASE_ROOT>/data/hinet_account/.env`
  - Existing project phase convention reference: `data/regional/phase.dat`
  - Existing station reference/station product files in the inspected project data tree should be used to construct `station.sta`; if no station-coordinate reference is found, do not fabricate coordinates.
- Time interval:
  - Requests cover `2025-06-01 00:00 JST <= time < 2026-05-02 00:00 JST`.
  - This is equivalent to UTC output coverage beginning at `2025-05-31T15:00:00Z` and ending before `2026-05-01T15:00:00Z`.
  - Use 67 non-overlapping 5-day chunks: `2025-06-01`, `2025-06-06`, ..., `2026-04-27`; each span is `5` days.
- Regional filter:
  - Apply only after parsing.
  - Keep events with `38.50 <= latitude <= 42.50` and `141.00 <= longitude <= 144.50`.
  - Regional picks are all parsed station-arrival rows whose `event_id` belongs to retained regional events.
- Authentication constraints:
  - Read credentials from environment variables first, then from the specified `.env`.
  - Support one or multiple account pairs.
  - Never print or write passwords to logs, manifests, figures, summaries, or exception messages.

## Analysis Plan

### Task Script 1 — End-to-end JMA/Hi-net download, fixed-width parsing, regional filtering, product generation, and QC

#### 1. Configure workflow inputs and chunk schedule

- Task description:
  - Define the fixed time interval, chunk list, filenames, credentials, parsing rules, regional bounds, and output product names.
- Required data sources:
  - `.env` file at `<CASE_ROOT>/data/hinet_account/.env`
  - Existing `data/regional/phase.dat`
  - Existing station reference/station product files in the same project data tree, if available.
- Parameter selection strategy:
  - `request_start_date = 2025-06-01`
  - `request_end_date_exclusive = 2026-05-02`
  - `chunk_span_days = 5`
  - Raw chunk names: `measure_YYYYMMDD_5.txt`
  - Smoke-test chunk: `measure_20250601_5.txt`, covering `2025-06-01 <= JST time < 2025-06-06`.
  - Full-run chunks: 67 total 5-day chunks from `2025-06-01` through `2026-04-27`.
  - Region bounds: latitude `[38.50, 42.50]`, longitude `[141.00, 144.50]`.
- Constraints:
  - Do not use current date defaults.
  - Do not use a 2026-only interval.
  - Do not assume the Hi-net request supports geographic filtering.
  - Do not overwrite existing non-empty raw files unless an explicit overwrite parameter is enabled.
- Key outputs:
  - Internal chunk schedule table with columns: `start_date`, `span_days`, `raw_file`.
  - Credential/account inventory with redacted account labels only, not passwords.

#### 2. Read credentials securely and initialize Hi-net clients

- Task description:
  - Load one or more Hi-net accounts and prepare HinetPy clients for download.
- Required data sources:
  - Process environment variables.
  - `.env` file path specified above.
- Parameter selection strategy:
  - Prefer explicit environment variables if present.
  - If multiple account pairs are present, assign stable redacted labels such as `account_1`, `account_2`.
  - Use the first valid account by default; optionally rotate to another account after repeated request failures.
- Constraints:
  - Never log full credential values.
  - Error messages must identify only missing/invalid credential keys, not values.
- Key outputs:
  - Credential validation status.
  - Redacted account-use log in the machine-readable run summary.

#### 3. Smoke-test download for the first 5-day chunk

- Task description:
  - Download or reuse the first chunk before running the full interval.
- Required data sources:
  - HinetPy arrival-time interface.
  - Credential source from Task 2.
- Parameter selection strategy:
  - Start date: `2025-06-01`
  - Span: `5`
  - Raw file: `measure_20250601_5.txt`
  - HinetPy request uses the arrival-time API; line ending option may be set to `UNIX` for easier parsing, but parsing must remain byte-length based and must also tolerate DOS line endings.
  - Retry policy: retry failed network/service requests with exponential backoff; record every terminal status in the manifest.
- Constraints:
  - If `measure_20250601_5.txt` already exists and is non-empty, skip download and mark as `skipped_existing`.
  - A zero-byte existing file is not accepted as valid and should be redownloaded or marked failed.
  - Raw download success requires a non-empty raw file.
- Key outputs:
  - Raw file: `measure_20250601_5.txt`
  - Initial `download_manifest.csv` row with:
    - `start_date`
    - `span_days`
    - `raw_file`
    - `exists`
    - `size_bytes`
    - `status`
    - `message`

#### 4. Implement fixed-width raw parser and smoke-test parsing

- Task description:
  - Parse the raw 96-byte JMA records into normalized event and pick rows.
- Required data sources:
  - `measure_20250601_5.txt`
  - Official JMA fixed-width field definitions for hypocenter, arrival-time, and end records.
  - Local travel-time/JMA format documentation in the project data tree, if available, to verify quality and weight fields.
- Parameter selection strategy:
  - Read raw files as bytes.
  - Split by line endings while preserving per-record byte-length validation.
  - Validate that every non-empty record is exactly 96 bytes excluding line ending.
  - Decode text fields with Japanese-compatible encoding support, prioritizing the encoding that preserves region names without corrupting fixed byte positions.
  - For `J` records:
    - Parse origin time in JST.
    - Parse latitude from degree/minute fields and convert to decimal degrees.
    - Parse longitude from degree/minute fields and convert to decimal degrees.
    - Parse depth in km.
    - Parse magnitude, using the primary JMA magnitude field where available.
    - Parse region name as the fixed-width region field, stripped of padding.
  - For `_` records:
    - Parse `station_code`.
    - Parse `station_number`.
    - Parse P and S arrival times by phase-name fields and their corresponding fixed-width time fields.
    - Convert P/S pick times from JST to UTC ISO strings.
    - Represent missing P or S as `-1`.
    - Parse phase quality flags from the phase-specific fixed-width quality/data-information fields.
    - Parse `weight` only from the documented fixed-width weight field; if the local/JMA format documentation does not define a usable weight field, output an empty/null weight and record this in parser diagnostics rather than inventing a value.
  - For `E` records:
    - Close the current event and validate record-sequence integrity.
  - `event_id` strategy:
    - Assign deterministic IDs after parsing, based on UTC origin time plus a stable sequence counter for duplicate origin times.
    - Preserve `source_file` for traceability.
  - `npicks` strategy:
    - Count station-arrival rows with at least one valid P or S arrival for each event.
    - Separately compute QC totals for P picks and S picks.
- Constraints:
  - Do not comma-split raw measure files.
  - Do not free-width parse raw records.
  - Do not silently ignore malformed record lengths or unclosed events.
  - Do not treat local JST dates as UTC dates.
- Key outputs:
  - Smoke parsed event table: `events_smoke_full.csv`
  - Smoke parsed pick table: `picks_smoke_full.csv`
  - Parser diagnostics: `parser_diagnostics_smoke.csv`
  - Smoke QC summary: `qc_smoke_summary.json`

#### 5. Smoke-test validation gates

- Task description:
  - Validate the first chunk before the full run proceeds.
- Required data sources:
  - `measure_20250601_5.txt`
  - `events_smoke_full.csv`
  - `picks_smoke_full.csv`
  - `parser_diagnostics_smoke.csv`
- Parameter selection strategy:
  - Required pass checks:
    - Raw file exists and `size_bytes > 0`.
    - All non-empty raw records are 96 bytes excluding line ending.
    - Record types include valid event sequences: `J`, zero or more `_`, and terminating `E`.
    - Every pick row has an `event_id` present in the event table.
    - Every event `npicks` equals the number of associated station rows with at least one valid P or S arrival.
    - P-pick count equals rows where `p_pick_time != -1`.
    - S-pick count equals rows where `s_pick_time != -1`.
    - UTC conversions are exactly JST minus 9 hours.
  - If no events are returned by the service, the parser may pass only if the raw file contains no valid event records and this is explicitly recorded; otherwise treat empty parsed output as a failure requiring inspection.
- Constraints:
  - The full-run download must not start unless smoke validation passes.
  - A fallback/mock/parser-schema-only result is not acceptable as a successful smoke test.
- Key outputs:
  - `qc_smoke_summary.json`
  - `validation_errors_smoke.csv` if any checks fail.
  - Pass/fail status controlling full execution.

#### 6. Full-range chunk download

- Task description:
  - Download all remaining 5-day raw measure files for the full requested interval.
- Required data sources:
  - HinetPy arrival-time interface.
  - Credentials from Task 2.
  - Existing raw files, if any.
- Parameter selection strategy:
  - Use the 67 scheduled chunks:
    - Start: `2025-06-01`, span `5`
    - Step: 5 days
    - Final chunk: `2026-04-27`, span `5`, ending before `2026-05-02`
  - Raw file naming: `measure_YYYYMMDD_5.txt`.
  - Skip existing non-empty files by default.
  - Retry failed requests with exponential backoff and bounded retry count.
  - Continue independent chunks after a chunk failure, but mark the full run incomplete unless all expected chunks are either downloaded successfully or skipped as valid existing files.
- Constraints:
  - No chunk may exceed 7 days.
  - Do not overwrite non-empty files by default.
  - Do not print passwords in HinetPy exception traces; sanitize failure messages before writing the manifest.
- Key outputs:
  - Raw files:
    - `measure_20250601_5.txt`
    - `measure_20250606_5.txt`
    - continuing every 5 days
    - `measure_20260427_5.txt`
  - Complete `download_manifest.csv` with one row per chunk:
    - `start_date`
    - `span_days`
    - `raw_file`
    - `exists`
    - `size_bytes`
    - `status`
    - `message`

#### 7. Full fixed-width parsing and normalized table generation

- Task description:
  - Parse all valid raw chunk files into full structured event and pick tables.
- Required data sources:
  - All non-empty `measure_YYYYMMDD_5.txt` files listed in `download_manifest.csv`.
  - JMA fixed-width parser specification established in the smoke test.
- Parameter selection strategy:
  - Parse only chunks with status indicating valid existing or successful download.
  - Preserve `source_file` on every event and pick row.
  - Sort events by UTC `origin_time`, then deterministic sequence.
  - Recompute deterministic `event_id` after merging to avoid chunk-local ID collisions.
  - Preserve all parsed events in the full table, regardless of location.
- Constraints:
  - The merged full tables are valid only if all expected chunks are accounted for and parse diagnostics contain no fatal fixed-width errors.
  - Non-fatal row-level issues should be retained in diagnostics with source file and raw line number.
- Key outputs:
  - Full event table: `events_full.csv`
    - Columns: `event_id,origin_time,latitude,longitude,depth_km,magnitude,region,npicks,source_file`
  - Full pick table: `picks_full.csv`
    - Columns: `event_id,station_code,station_number,p_pick_time,s_pick_time,p_quality,s_quality,weight,source_file`
  - Full parser diagnostics: `parser_diagnostics_full.csv`
  - Full merge/QC summary: `qc_full_summary.json`

#### 8. Sanriku regional subset generation

- Task description:
  - Apply the requested spatial filter locally and write regional normalized outputs.
- Required data sources:
  - `events_full.csv`
  - `picks_full.csv`
- Parameter selection strategy:
  - Select events satisfying:
    - `38.50 <= latitude <= 42.50`
    - `141.00 <= longitude <= 144.50`
  - Select picks whose `event_id` is in the retained regional event set.
  - Preserve the same `event_id` values used in full outputs.
- Constraints:
  - Do not filter during download.
  - Do not filter picks independently by station location unless explicitly needed for `station.sta`; event location controls regional event membership.
- Key outputs:
  - Regional event table: `events.csv`
    - Columns: `event_id,origin_time,latitude,longitude,depth_km,magnitude,region,npicks,source_file`
  - Regional pick table: `picks.csv`
    - Columns: `event_id,station_code,station_number,p_pick_time,s_pick_time,p_quality,s_quality,weight,source_file`
  - Regional subset summary: `qc_regional_summary.json`

#### 9. Generate project-convention `phase.dat`

- Task description:
  - Convert regional normalized tables to the existing project’s comma-separated block-style `phase.dat` convention.
- Required data sources:
  - `events.csv`
  - `picks.csv`
  - Reference file: `data/regional/phase.dat`
- Parameter selection strategy:
  - Inspect `data/regional/phase.dat` before writing:
    - Identify event header line structure.
    - Identify station pick line structure.
    - Preserve comma-separated block convention.
    - Preserve use of UTC ISO timestamps and `-1` for missing P/S arrivals.
  - Write one event block per regional event.
  - Within each event block, write station pick rows for associated picks.
  - Ensure pick row count per block equals `npicks`.
- Constraints:
  - Do not create a `#`-prefixed phase format.
  - Do not create a whitespace-delimited HASH-style format.
  - The output must be traceable to `events.csv` and `picks.csv`.
- Key outputs:
  - Regional project-format phase file: `phase.dat`
  - Phase-format validation summary: `phase_dat_validation.csv`

#### 10. Generate `station.sta`

- Task description:
  - Produce station metadata for stations used in the regional pick table.
- Required data sources:
  - `picks.csv`
  - Existing station reference/station product files in the project data tree.
  - Existing regional station product, if found, to infer exact `station.sta` column convention.
- Parameter selection strategy:
  - Build the unique regional station list from `station_code` and `station_number`.
  - Match stations to local reference metadata by station code first, then station number as a secondary key.
  - Preserve the project’s existing `station.sta` comma-separated convention if an existing station product is found.
  - Include only stations appearing in `picks.csv`.
- Constraints:
  - Do not fabricate station latitude, longitude, or elevation.
  - If coordinates are missing for any regional station, write a missing-station report and mark `station.sta` validation as incomplete.
- Key outputs:
  - Regional station file: `station.sta`
  - Station metadata audit: `station_metadata_audit.csv`
  - Missing station report, if needed: `station_metadata_missing.csv`

#### 11. Cross-table validation for final products

- Task description:
  - Validate consistency across raw files, manifests, full tables, regional tables, `phase.dat`, and `station.sta`.
- Required data sources:
  - `download_manifest.csv`
  - `events_full.csv`
  - `picks_full.csv`
  - `events.csv`
  - `picks.csv`
  - `phase.dat`
  - `station.sta`
  - Parser diagnostics.
- Parameter selection strategy:
  - Manifest validation:
    - 67 expected chunks.
    - Every chunk has a raw file name matching `measure_YYYYMMDD_5.txt`.
    - Every accepted raw file is non-empty.
  - Full table validation:
    - Required columns are present in the exact requested order.
    - `event_id` is unique in `events_full.csv`.
    - Every `picks_full.csv.event_id` exists in `events_full.csv`.
    - `npicks` equals associated pick rows with at least one valid P or S.
    - P and S pick times are either UTC ISO strings or `-1`.
  - Regional validation:
    - Every event in `events.csv` satisfies the Sanriku bounds.
    - Every pick in `picks.csv` belongs to an event in `events.csv`.
    - Regional outputs are subsets of full outputs.
  - `phase.dat` validation:
    - Every regional event appears exactly once as an event block.
    - Pick row counts match `picks.csv`.
    - Missing arrivals are represented as `-1`.
  - `station.sta` validation:
    - Every station in `picks.csv` appears in `station.sta`.
    - No extra station is required, but extras should be reported if present.
- Constraints:
  - Do not treat partial batch success as final success unless merged scientific outputs are valid and non-empty when events are expected.
  - If no regional events are found, `events.csv`, `picks.csv`, and `phase.dat` may be empty/zero-event products only if the full parsed catalog is valid and the zero regional count is explicitly documented.
- Key outputs:
  - Final validation summary: `final_validation_summary.json`
  - Final validation errors: `final_validation_errors.csv`
  - Final product inventory: `product_inventory.csv`

#### 12. QC figures and diagnostic tables

- Task description:
  - Create visual checks for download coverage, parsed catalog content, and regional subset consistency.
- Required data sources:
  - `download_manifest.csv`
  - `events_full.csv`
  - `picks_full.csv`
  - `events.csv`
  - `picks.csv`
  - `station.sta`
  - QC summaries.
- Parameter selection strategy:
  - Figure 1: Download chunk timeline/status by `start_date`, showing downloaded/skipped/failed chunks and file sizes.
  - Figure 2: Full-catalog event map with the Sanriku bounding box overlaid.
  - Figure 3: Regional event map with stations from `station.sta` overlaid.
  - Figure 4: Daily or chunk-level event counts for full and regional catalogs.
  - Figure 5: P-pick and S-pick counts by chunk/source file.
  - Figure 6: Distribution of event `npicks` for full and regional catalogs.
  - Figure 7: Depth-magnitude scatter or depth histogram for regional events.
- Constraints:
  - Figures are QC products; scientific success depends on valid downloads, parsing, tables, and cross-table checks, not on figure aesthetics.
  - Do not expose account information in figure titles, labels, or metadata.
- Key outputs:
  - `fig_download_manifest_status`
  - `fig_event_map_full_with_sanriku_box`
  - `fig_event_station_map_regional`
  - `fig_event_counts_by_time`
  - `fig_pick_counts_by_chunk`
  - `fig_npicks_distribution`
  - `fig_regional_depth_magnitude_qc`