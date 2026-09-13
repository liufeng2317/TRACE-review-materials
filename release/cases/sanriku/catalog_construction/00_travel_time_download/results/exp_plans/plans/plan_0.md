# Goal

Independently download, parse, validate, and regionalize JMA/Hi-net arrival-time measure files for the Sanriku study region for 2025-06-01 through 2026-05-01 inclusive, producing raw chunk files, normalized event/pick tables, project-convention phase.dat files, station.sta files, and validation manifests.

## Planning Assumptions

- Use observations only: JMA arrival-time measure files obtained through the Hi-net/HinetPy arrival-time interface.
- HinetPy package contract:
  - Use the Hi-net arrival-time API exposed as `Client.get_arrivaltime(startdate, span, os, filename)`.
  - `startdate` is the request start date; `span` is an integer number of days.
  - `os` may be set to `UNIX` to avoid DOS line-ending ambiguity.
  - Hi-net/HinetPy times and raw arrival-time data are in JST; all structured outputs must be converted to UTC ISO strings.
  - Success evidence is a non-empty raw measure text file at the requested filename plus a completed manifest row.
- Authentication:
  - Read account credentials from environment variables first, then from `<CASE_ROOT>/data/hinet_account/.env`.
  - Support one or multiple accounts; rotate only when needed after failures/rate limits.
  - Never print or write passwords to logs, manifests, figures, or reports.
- Date handling:
  - Requested interval is half-open: 2025-06-01 <= time < 2026-05-02.
  - Chunk requests must not exceed 7 days; use 5-day chunks except the final shorter chunk.
  - Do not replace the user interval with current-date or 2026-only defaults.
- Spatial handling:
  - Download all available records for each time chunk.
  - Apply the Sanriku regional filter only after parsing: latitude 38.50–42.50 N, longitude 141.00–144.50 E.
- Parsing:
  - Parse JMA measure records as fixed-width byte records with expected payload length 96 bytes excluding line ending.
  - Do not comma-split or whitespace-split raw records.
  - Event headers begin with `J`; station pick records begin with `_`; event terminators begin with `E`.
  - Missing P or S arrivals must be represented as `-1`.
- Existing local convention:
  - Use `data/regional/phase.dat` as the reference for the project-specific comma-separated phase-file block convention.
  - Do not create HASH-style, `#`-prefixed, or whitespace-delimited phase.dat.
- Primary structured outputs are CSV tables; phase.dat and station.sta are derived, traceable compatibility products.

## Analysis Plan

### Task 1 — Single primary workflow: authenticated download, fixed-width parsing, validation, and product generation

- Task description:
  - Implement one cohesive executable workflow that performs credential loading, chunk generation, smoke-test download/parsing/QC, full-range download/parsing, regional filtering, station matching, and output validation.
  - The workflow must stop before the full-range run if the smoke test fails.

- Required data sources:
  - Hi-net/JMA arrival-time service accessed through HinetPy.
  - Credential file: `<CASE_ROOT>/data/hinet_account/.env`.
  - Existing reference phase file: `data/regional/phase.dat`.
  - Local station reference text and/or existing station products available in the project data tree, used only to map station codes/numbers to station.sta fields.

- Parameter selection strategy:
  - Credentials:
    - Search for usable username/password pairs in environment variables and the specified `.env` file.
    - Accept both single-account variables and indexed/multiple-account variables.
    - Redact all password-like values in runtime messages.
  - Chunking:
    - Smoke chunk: start_date `2025-06-01`, span_days `5`, covering 2025-06-01 <= time < 2025-06-06.
    - Full chunks: generate consecutive half-open chunks from `2025-06-01` to `2026-05-02`, using 5-day spans except the final remaining span.
    - Raw filename pattern: `measure_YYYYMMDD_N.txt`, where `YYYYMMDD` is chunk start date and `N` is span in days.
  - Download behavior:
    - If the raw file already exists and size_bytes > 0, mark it as skipped/existing and do not overwrite by default.
    - For missing or empty files, call HinetPy arrival-time download with the chunk start date, span_days, `os=UNIX`, and the target filename.
    - Retry failed requests with exponential backoff; after retry exhaustion, record the failure in `download_manifest.csv`.
    - If multiple accounts are available, optionally advance to the next account after authentication/rate-limit failures while preserving redaction.
  - Fixed-width parsing:
    - Open raw files in byte mode.
    - For each physical line, remove only line-ending bytes and validate the remaining byte length is 96 when the record is non-empty.
    - Decode with the encoding required by the JMA measure files, using a deterministic fallback strategy if station/region text decoding fails; preserve parse warnings.
    - Route records by first byte/character:
      - `J`: create a new event context and parse origin_time, latitude, longitude, depth_km, magnitude, and region from documented fixed byte columns.
      - `_`: parse station_code, station_number, P pick time, S pick time, P quality, S quality, and weight from documented fixed byte columns, attaching the row to the current event.
      - `E`: close the current event and finalize npicks.
    - Convert all JMA/JST event and pick timestamps to UTC ISO strings.
    - Use `-1` for missing P or missing S picks in CSV and phase.dat.
  - Event IDs:
    - Generate stable event_id values deterministically from origin time and source ordering, avoiding collisions when two events share the same second.
    - Preserve source_file for every event and pick row.
  - Regional subset:
    - Select events with latitude between 38.50 and 42.50 inclusive and longitude between 141.00 and 144.50 inclusive.
    - Select picks whose event_id belongs to the regional event subset.
  - station.sta:
    - Build full and regional station lists from station codes/numbers present in picks.
    - Join station codes/numbers to local station reference metadata where available.
    - If a station in picks cannot be matched to coordinates, exclude it from station.sta and write it to a station-unmatched QC table; do not silently invent coordinates.
  - phase.dat:
    - Infer the block structure, delimiter use, timestamp representation, event header fields, station pick fields, and missing-arrival representation from `data/regional/phase.dat`.
    - Write derived phase.dat files using the same comma-separated project convention.
    - Preserve traceability by ensuring every phase.dat event and pick line can be linked back to event_id/source_file in the normalized CSV outputs.

- Constraints:
  - Do not use comma splitting or free-width parsing on raw JMA measure records.
  - Do not assume the Hi-net/JMA download service supports geographic filtering.
  - Do not treat successful downloads alone as success; parsed non-empty scientific outputs and QC checks are required.
  - Do not overwrite non-empty raw files unless an explicit overwrite option is selected.
  - Do not output credentials or password-derived strings.
  - The workflow must record both skipped-existing and newly downloaded files in `download_manifest.csv`.
  - Full-range execution is gated by smoke-test success.

- Quality-control calculations:
  - Raw download QC:
    - For each chunk, compute exists, size_bytes, status, and message.
    - Verify raw files expected to contain data are non-empty; allow empty/no-data chunks only if the service response clearly indicates no records.
  - Fixed-width QC:
    - Count total records, J records, station pick records, E records, malformed-length records, unrecognized records, and decoding warnings per source file.
    - Verify every station pick record is inside an open event context.
    - Verify every event is closed by an E record or explicitly flagged as unterminated.
  - Table integrity QC:
    - Confirm required events.csv columns: event_id, origin_time, latitude, longitude, depth_km, magnitude, region, npicks, source_file.
    - Confirm required picks.csv columns: event_id, station_code, station_number, p_pick_time, s_pick_time, p_quality, s_quality, weight, source_file.
    - Check event-pick foreign-key consistency: every picks.event_id must exist in events.event_id.
    - Recompute npicks from picks and compare with events.npicks.
    - Count P picks where p_pick_time != `-1`, S picks where s_pick_time != `-1`, and both-missing station rows.
    - Verify UTC conversion by checking timestamps are timezone-normalized ISO strings and shifted from JST by 9 hours.
  - Smoke-test gate:
    - Required smoke outputs: one non-empty raw file or explicit no-data status, parsed event/pick tables, QC summary, and manifest row.
    - If the smoke raw file has events, require at least one valid event, consistent foreign keys, matching npicks, and non-negative P/S pick counts.
    - If the smoke interval has no events, require that the no-data condition is documented by the service output and parser status before proceeding.
  - Regional QC:
    - Confirm all regional events satisfy the Sanriku bounds.
    - Confirm all regional picks reference regional event_ids only.
    - Compare regional phase.dat line/event counts with regional CSV event/pick counts.
  - station.sta QC:
    - Count total unique stations in picks, matched stations, and unmatched stations.
    - Validate station.sta contains only stations used by the corresponding pick table and has no duplicate station identifiers.

- Key outputs:
  - `download_manifest.csv`
  - `parse_qc_by_file.csv`
  - `smoke_qc_summary.csv`
  - `events_full.csv`
  - `picks_full.csv`
  - `events_regional.csv`
  - `picks_regional.csv`
  - `phase_full.dat`
  - `phase_regional.dat`
  - `station_full.sta`
  - `station_regional.sta`
  - `station_unmatched.csv`
  - `validation_summary.json`

### Task 2 — Diagnostic visualization and validation artifacts from generated tables

- Task description:
  - Create compact diagnostic figures and tabular summaries to verify time coverage, spatial coverage, parsing completeness, and regional subset behavior after the primary workflow succeeds.

- Required data sources:
  - `download_manifest.csv`
  - `events_full.csv`
  - `picks_full.csv`
  - `events_regional.csv`
  - `picks_regional.csv`
  - `parse_qc_by_file.csv`
  - `station_unmatched.csv`

- Parameter selection strategy:
  - Use the user-specified full interval and Sanriku bounds.
  - Use parsed UTC origin_time values for temporal aggregation.
  - Aggregate event and pick counts by chunk start date and by calendar day.
  - Separate full catalog and regional subset in all count summaries.

- Constraints:
  - Figures are QC artifacts, not substitutes for CSV validation.
  - Do not include credentials or raw account metadata in figure annotations or tables.
  - Do not infer parse correctness from visual plots alone; use validation_summary.json as the success criterion.

- Key calculations and figures:
  - Time coverage:
    - Plot or tabulate chunk statuses from `download_manifest.csv`.
    - Daily event counts for full and regional catalogs.
  - Spatial coverage:
    - Event epicenter map/table summary with Sanriku bounding box applied.
    - Count events inside and outside the regional bounds.
  - Pick completeness:
    - P-only, S-only, both P/S, and both-missing station-pick counts.
    - Distribution of npicks per event for full and regional catalogs.
  - Parsing health:
    - Per-file malformed-length counts, unrecognized-record counts, and unterminated-event counts.
    - Station matching summary: matched versus unmatched stations.

- Key outputs:
  - `daily_event_counts.csv`
  - `pick_count_summary.csv`
  - `spatial_subset_summary.csv`
  - `station_match_summary.csv`
  - `download_status_overview`
  - `daily_event_counts_full_vs_regional`
  - `event_map_full_with_sanriku_box`
  - `npicks_distribution`
  - `pick_completeness_summary`