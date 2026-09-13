# Goal

Independently download, parse, validate, and export JMA/Hi-net arrival-time measure files for 2025-06-01 ≤ time < 2026-05-02, producing full and Sanriku-filtered event/pick tables plus project-convention `phase.dat` and `station.sta`.

## Planning Assumptions

- Use observational data only: Hi-net/JMA arrival-time measure files downloaded through a HinetPy-supported interface.
- HinetPy package contract:
  - Use `HinetPy.Client(username, password)` for authenticated Hi-net access.
  - Use `Client.get_arrivaltime(startdate, span, os, filename)` to request JMA arrival-time data.
  - `startdate` may be a string/date/datetime; `span` is in days; `filename` is the saved output file.
  - Hi-net/HinetPy times are JST, UTC+09:00; parsed structured outputs must be converted to UTC ISO strings.
- Request interval is fixed by the user:
  - Start: `2025-06-01`
  - End exclusive: `2026-05-02`
  - Total span: 335 days
  - Preferred chunk size: 5 days
  - Planned chunks: 67 chunks, all exactly 5 days, beginning with `2025-06-01 <= time < 2025-06-06`.
- Spatial filtering is local after parsing:
  - Latitude: `38.50 <= latitude <= 42.50`
  - Longitude: `141.00 <= longitude <= 144.50`
- Raw JMA measure records must be parsed as fixed-width records of 96 bytes excluding line endings.
- The existing `data/regional/phase.dat` is a project-specific comma-separated block format and must be used only as the format convention reference; it must not be treated as the primary input catalog.
- Do not print, persist, or expose passwords in logs, manifests, figures, or reports.
- Existing non-empty raw files are skipped by default unless an explicit overwrite mode is requested.

## Analysis Plan

### Task 1 — Prepare request schedule, credentials, and fixed-width parsing contract

- Task description:
  - Build the reproducible download/parsing configuration for the complete Sanriku workflow.
  - Inspect the local `.env` file and environment variables for one or more Hi-net accounts.
  - Inspect the official/local JMA measure format reference available in the data tree to define exact fixed-width field slices.
  - Inspect `data/regional/phase.dat` to infer the project’s comma-separated event-header and station-pick block convention for later output.

- Required data sources:
  - `.env` path: `<CASE_ROOT>/data/hinet_account/.env`
  - Existing phase convention reference: `data/regional/phase.dat`
  - Local station reference text from the provided data directory, if present.
  - Local/official JMA arrival-time measure format PDF from the provided data directory, if present.

- Parameter selection strategy:
  - Generate chunk table from `2025-06-01` to `2026-05-02` exclusive using 5-day spans.
  - First smoke-test chunk: start date `2025-06-01`, span `5`, raw file `measure_20250601_5.txt`.
  - Full-run raw file naming pattern: `measure_YYYYMMDD_5.txt`.
  - Credential discovery:
    - Prefer environment variables if present.
    - Otherwise load the specified `.env`.
    - Support either a single username/password pair or indexed/multiple account pairs.
    - Record only account labels or indices, never passwords.
  - Fixed-width parser schema:
    - Confirm record length is 96 bytes excluding line ending.
    - Define slices for `J`, `_`, and `E` record types from the JMA format reference.
    - Treat parsing as invalid if implemented with comma splitting or arbitrary whitespace splitting.

- Constraints:
  - No geographic filter should be sent to the Hi-net request interface.
  - Do not substitute current date or a 2026-only interval.
  - Do not expose credentials.
  - Existing regional outputs may be used only for format comparison, not as replacement data.

- Key outputs:
  - `chunk_schedule.csv` with `start_date,end_exclusive,span_days,raw_file`.
  - `parser_field_schema.json` documenting byte ranges and field meanings for `J`, `_`, and `E` records.
  - `phase_dat_convention_summary.json` documenting the detected block convention from `data/regional/phase.dat`.
  - Credential availability check summary without passwords.

---

### Task 2 — Smoke-test download and validation for 2025-06-01 ≤ time < 2025-06-06

- Task description:
  - Download or reuse the first 5-day raw JMA measure file.
  - Parse the file with the fixed-width parser.
  - Validate raw-file existence, record structure, event-pick linkage, and P/S pick counts before running the full interval.

- Required data sources:
  - Hi-net/JMA arrival-time service through HinetPy.
  - Credentials from environment variables or the specified `.env`.
  - Smoke-test chunk:
    - Start date: `2025-06-01`
    - Span days: `5`
    - Raw file: `measure_20250601_5.txt`
  - Fixed-width parser schema from Task 1.

- Parameter selection strategy:
  - Use `Client.get_arrivaltime(startdate="2025-06-01", span=5, os="UNIX", filename="measure_20250601_5.txt")` or equivalent HinetPy-supported arrival-time call.
  - If `measure_20250601_5.txt` already exists and `size_bytes > 0`, skip download and mark status as `skipped_existing`.
  - If download is attempted, use retry and backoff:
    - Maximum attempts: 3–5.
    - Backoff: increasing delay between attempts.
    - Switch to another available account only after an authentication/session/request failure that is not caused by malformed parameters.
  - Parse only after raw file is non-empty.

- Constraints:
  - Passwords must not appear in exception messages, logs, or manifest rows.
  - A raw file with zero bytes is not valid and must not be treated as successful.
  - Each parsed line must be checked against the 96-byte fixed-width record expectation.
  - Invalid record type, malformed date/time, malformed numeric coordinate/depth/magnitude, or unterminated event block must be reported with source file and line number.

- Calculations:
  - Parse `J` event headers:
    - `origin_time` in JST, converted to UTC ISO.
    - `latitude`, `longitude`, `depth_km`, `magnitude`, `region`.
    - Assign deterministic `event_id`, preferably from origin time plus file/sequence index to avoid collisions.
  - Parse `_` station pick records:
    - `station_code`, `station_number`.
    - P pick time and S pick time in JST converted to UTC ISO.
    - Missing P or S arrival represented as `-1`.
    - `p_quality`, `s_quality`, `weight`.
  - Parse `E` records as event terminators.
  - Compute:
    - Number of events.
    - Number of picks.
    - Number of P arrivals not equal to `-1`.
    - Number of S arrivals not equal to `-1`.
    - Number of picks per event.
    - Number of orphan picks.
    - Number of unterminated event blocks.
    - Number of event blocks with zero picks.

- Validation criteria:
  - Raw file exists and is non-empty.
  - At least one valid fixed-width record is parsed if the service returns data for the window.
  - Every pick `event_id` exists in the event table.
  - Every event `npicks` equals the number of parsed station-pick records assigned to that event.
  - P and S pick counts are internally consistent with missing-arrival marker `-1`.
  - JST-to-UTC conversion is applied to all non-missing structured timestamps.
  - No comma/free-width parsing is used for the raw measure format.

- Key outputs:
  - `download_manifest_smoke.csv` with columns:
    - `start_date,span_days,raw_file,exists,size_bytes,status,message`
  - `events_full_smoke.csv`:
    - `event_id,origin_time,latitude,longitude,depth_km,magnitude,region,npicks,source_file`
  - `picks_full_smoke.csv`:
    - `event_id,station_code,station_number,p_pick_time,s_pick_time,p_quality,s_quality,weight,source_file`
  - `smoke_qc_summary.json` with counts and pass/fail flags.
  - If smoke test fails: preserve failure evidence and stop before full-range execution.

---

### Task 3 — Full-range download of JMA/Hi-net measure files

- Task description:
  - After smoke-test success, download or reuse all 67 five-day JMA measure chunks covering `2025-06-01 <= time < 2026-05-02`.

- Required data sources:
  - Hi-net/JMA arrival-time service through HinetPy.
  - Credentials from environment variables or `.env`.
  - `chunk_schedule.csv` from Task 1.

- Parameter selection strategy:
  - For each chunk, call the HinetPy-supported arrival-time interface with:
    - `startdate = chunk start date`
    - `span = 5`
    - `filename = measure_YYYYMMDD_5.txt`
    - `os = "UNIX"` unless the service requires otherwise; parser must tolerate standard line endings.
  - Skip any existing raw file if it is non-empty.
  - Reattempt failed downloads with retry/backoff.
  - Use multiple accounts only as fallback or load balancing if the first account cannot complete requests.

- Constraints:
  - Do not request beyond `2026-05-02` exclusive.
  - Do not send Sanriku geographic bounds to the request service.
  - Do not overwrite valid existing raw files by default.
  - A chunk is not complete unless the raw file exists and has `size_bytes > 0`, or the service explicitly returns a documented no-data response that is recorded in the manifest.
  - Download success must be judged by the existence and size of the raw file plus parseability in Task 4, not by API return alone.

- Calculations:
  - For each chunk, record:
    - Start date.
    - Span days.
    - Raw filename.
    - Whether file exists after the operation.
    - File size in bytes.
    - Status:
      - `downloaded`
      - `skipped_existing`
      - `failed`
      - `no_data_documented`, only if unambiguously indicated by the service/output.
    - Sanitized message.

- Key outputs:
  - `download_manifest.csv` with exactly the requested columns:
    - `start_date,span_days,raw_file,exists,size_bytes,status,message`
  - Complete set of expected raw files:
    - `measure_20250601_5.txt`
    - `measure_20250606_5.txt`
    - continuing every 5 days through
    - `measure_20260427_5.txt`

---

### Task 4 — Full fixed-width parsing, catalog construction, and regional filtering

- Task description:
  - Parse all downloaded raw JMA measure chunks into normalized full event and pick tables.
  - Apply the Sanriku spatial filter locally to produce regional event and pick subsets.
  - Produce station output using available station reference information and stations actually used by the regional picks.

- Required data sources:
  - Full raw measure files from Task 3.
  - `parser_field_schema.json` from Task 1.
  - Local station reference text from the data directory, if present.
  - Existing `data/regional/phase.dat` only for output convention comparison.

- Parameter selection strategy:
  - Input files are all manifest rows where raw file exists and `size_bytes > 0`.
  - Parse in chronological chunk order and preserve source file lineage in every output row.
  - Event IDs must be deterministic and unique across chunks.
  - Regional subset:
    - Select events satisfying:
      - `38.50 <= latitude <= 42.50`
      - `141.00 <= longitude <= 144.50`
    - Select picks whose `event_id` belongs to the regional event subset.
  - `npicks`:
    - For full events: count all station pick records linked to each event.
    - For regional events: keep `npicks` traceable; either preserve full-event `npicks` and document it, or add validation confirming it equals the number of retained regional pick rows. Prefer preserving full-event `npicks` because the regional subset is event-based, not station-based.
  - Station table:
    - Build `station.sta` from station metadata if coordinates are available.
    - Include only stations referenced by regional picks.
    - If station coordinates are unavailable for some station codes/numbers, output a station-metadata gap table rather than inventing coordinates.

- Constraints:
  - Fixed-width parsing only; no comma splitting or whitespace splitting of raw measure files.
  - Enforce 96-byte record length excluding line endings.
  - Convert all non-missing JMA raw JST times to UTC ISO strings.
  - Missing P or S pick time must be exactly `-1`.
  - Event block structure must follow:
    - `J` header starts an event.
    - `_` records add station picks to the current event.
    - `E` terminates the current event.
  - If a new `J` appears before an `E`, or an `_` appears without an active event, flag the issue with source file and line number.
  - Do not use the existing regional CSVs as substitutes for downloaded/parsed data.

- Calculations:
  - Full parsed catalog:
    - `events_full.csv`
    - `picks_full.csv`
  - Regional parsed catalog:
    - `events_regional.csv`
    - `picks_regional.csv`
  - Per-file parser diagnostics:
    - Number of lines.
    - Number of valid `J`, `_`, and `E` records.
    - Number of malformed/unknown records.
    - Number of parsed events.
    - Number of parsed station records.
    - Number of missing P arrivals.
    - Number of missing S arrivals.
  - Catalog-level diagnostics:
    - Total events and picks.
    - Regional events and picks.
    - P-arrival count and S-arrival count.
    - Pick/event foreign-key consistency.
    - Duplicate event IDs.
    - Time range of parsed event origins in UTC and JST-equivalent.
    - Events outside requested time bounds.

- Key outputs:
  - `events_full.csv` with columns:
    - `event_id,origin_time,latitude,longitude,depth_km,magnitude,region,npicks,source_file`
  - `picks_full.csv` with columns:
    - `event_id,station_code,station_number,p_pick_time,s_pick_time,p_quality,s_quality,weight,source_file`
  - `events_regional.csv` with same schema as `events_full.csv`.
  - `picks_regional.csv` with same schema as `picks_full.csv`.
  - `station_metadata_gaps.csv`, if any regional pick station lacks reference metadata.
  - `parse_qc_by_file.csv`.
  - `catalog_qc_summary.json`.

---

### Task 5 — Write project-convention `phase.dat` and `station.sta`

- Task description:
  - Export the regional subset into the project-specific comma-separated phase-file convention used by `data/regional/phase.dat`.
  - Export regional station metadata as `station.sta` using the project’s local station convention.

- Required data sources:
  - `events_regional.csv` from Task 4.
  - `picks_regional.csv` from Task 4.
  - Station reference metadata from Task 4.
  - `phase_dat_convention_summary.json` from Task 1.
  - Existing `data/regional/phase.dat` as format reference only.

- Parameter selection strategy:
  - Write `phase.dat` with event header lines and station pick lines matching the detected comma-separated block structure in the existing project file.
  - Use UTC ISO timestamps in the structured CSV outputs.
  - For `phase.dat`, match the timestamp convention used by the existing project file; if the existing file stores UTC ISO timestamps, write UTC ISO timestamps. If its timezone convention is ambiguous, write from the normalized UTC fields and document that choice in metadata.
  - Missing P or S arrival remains `-1`.
  - Include only Sanriku regional events and their associated picks.
  - Sort order:
    - Events by `origin_time`.
    - Picks within each event by station code/number or by original source-file order, matching the existing convention where inferable.
  - Write `station.sta` for stations present in `picks_regional.csv` and available in the station reference metadata.

- Constraints:
  - Do not create `#`-prefixed event headers.
  - Do not create a whitespace-delimited HASH-style phase file.
  - Do not invent station coordinates or station elevations.
  - Keep normalized CSV files as the primary structured outputs; `phase.dat` is a compatibility export.

- Calculations:
  - Compare generated `phase.dat` structure to `data/regional/phase.dat`:
    - Event header field count.
    - Pick-line field count.
    - Missing-pick marker.
    - Timestamp format.
    - Block ordering.
  - Count events and picks written to `phase.dat`.
  - Count stations written to `station.sta`.

- Key outputs:
  - `phase.dat`
  - `station.sta`
  - `phase_export_qc.json` containing:
    - Number of regional events exported.
    - Number of regional picks exported.
    - Number of P arrivals exported.
    - Number of S arrivals exported.
    - Format-convention checks against `data/regional/phase.dat`.
    - Any station metadata gaps affecting `station.sta`.

---

### Task 6 — Final validation and diagnostic figures

- Task description:
  - Validate the complete workflow outputs and produce concise QC tables and figures demonstrating download completeness, parser consistency, and Sanriku spatial/time coverage.

- Required data sources:
  - `download_manifest.csv`
  - `events_full.csv`
  - `picks_full.csv`
  - `events_regional.csv`
  - `picks_regional.csv`
  - `phase.dat`
  - `station.sta`
  - `parse_qc_by_file.csv`
  - `catalog_qc_summary.json`
  - `phase_export_qc.json`

- Parameter selection strategy:
  - Treat the full workflow as successful only if:
    - Smoke test passed.
    - All 67 chunks have terminal manifest statuses.
    - All non-empty raw files were parsed.
    - Event and pick CSVs are non-empty if downloaded files contain event records.
    - All picks reference existing events.
    - No duplicate `event_id` exists.
    - All structured non-missing timestamps are UTC ISO strings.
    - All regional events fall within Sanriku bounds.
    - `phase.dat` event/pick counts match the regional CSV subset.
  - If the Hi-net service returns true no-data files for any chunk, validate and report those chunks separately rather than marking them as parser failures.

- Constraints:
  - Do not interpret fallback, mock, diagnostic-only, or schema-only outputs as successful scientific execution.
  - Do not hide malformed records; summarize and preserve line-level evidence in QC outputs.
  - Do not expose credentials in any validation output.

- Calculations:
  - Download completeness:
    - Expected chunks: 67.
    - Completed chunks by status.
    - Failed chunks.
    - Existing skipped chunks.
    - Total downloaded/available bytes.
  - Parser consistency:
    - Total `J`, `_`, and `E` records.
    - Events with zero picks.
    - Picks without valid parent event.
    - Events without terminator.
    - Record-length violations.
  - Catalog consistency:
    - Full event count and pick count.
    - Regional event count and pick count.
    - P and S arrival counts.
    - Missing P and missing S counts.
    - Time coverage by chunk.
  - Spatial consistency:
    - Confirm all regional events are within requested latitude/longitude bounds.
    - Count full-catalog events outside bounds.
  - Export consistency:
    - `phase.dat` event count equals `events_regional.csv` row count.
    - `phase.dat` pick count equals `picks_regional.csv` row count.
    - `station.sta` station count equals number of regional pick stations with metadata.

- Figures to draw:
  - Download status timeline by 5-day chunk.
  - Raw file size by chunk start date.
  - Event count per chunk for full catalog and Sanriku subset.
  - P and S pick counts per chunk.
  - Map of full parsed events and highlighted Sanriku regional events with the requested bounding box.
  - Magnitude-time scatter plot for regional events.
  - Depth distribution or depth-vs-time plot for regional events.
  - Station map for stations included in `station.sta`, if station coordinates are available.
  - Histogram of picks per regional event.

- Key outputs:
  - `final_validation_summary.json`
  - `final_validation_summary.csv`
  - Diagnostic figure files:
    - `download_status_timeline`
    - `raw_file_size_by_chunk`
    - `event_counts_by_chunk`
    - `pick_counts_by_chunk`
    - `full_and_regional_event_map`
    - `regional_magnitude_time`
    - `regional_depth_diagnostic`
    - `regional_station_map`, if station coordinates are available
    - `regional_picks_per_event_histogram`