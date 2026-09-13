# Goal

Independently download, parse, and validate JMA/Hi-net arrival-time measure files for 2025-06-01 ≤ time < 2026-05-02, then produce full and Sanriku-filtered event, pick, phase.dat, and station.sta products using fixed-width parsing and the existing project phase-file convention.

## Planning Assumptions

- Use observation data only: Hi-net/JMA arrival-time measure files downloaded through HinetPy plus local station reference metadata. Existing `data/regional/phase.dat` is used only to infer the project-specific output convention, not as parsed science input.
- HinetPy package contract:
  - Main interface: `HinetPy.Client`.
  - Arrival-time request method: `client.get_arrivaltime(startdate, span, filename=None, os="DOS")`.
  - `startdate` accepts `str`, `datetime.date`, or `datetime.datetime`.
  - `span` is an integer number of days.
  - `filename` controls the saved raw measure-file name.
  - `os` accepts `"DOS"` or `"UNIX"`.
  - Return value is the saved filename.
- Use the requested half-open interval exactly:
  - start date: `2025-06-01`
  - exclusive end date: `2026-05-02`
  - 335 total days, planned as 67 consecutive 5-day chunks.
  - First smoke-test chunk: `2025-06-01 ≤ time < 2025-06-06`, raw file `measure_20250601_5.txt`.
- Authentication constraints:
  - Read credentials from environment variables first and then from `<CASE_ROOT>/data/hinet_account/.env`.
  - Support one or multiple accounts.
  - Never print passwords or full credential values in logs, manifests, or summaries.
- Parsing constraints:
  - JMA measure records are fixed-width records of 96 bytes excluding line endings.
  - Do not parse raw measure files by comma splitting or free-width splitting.
  - Raw JMA times are JST; all structured output timestamps must be UTC ISO strings.
  - Missing P or S picks must be represented as `-1`.
- Regional filter:
  - Apply locally after parsing.
  - Latitude: 38.50–42.50°N inclusive.
  - Longitude: 141.00–144.50°E inclusive.
- Existing `data/regional/phase.dat` is a custom comma-separated block format with event header lines followed by station pick lines; the new `phase.dat` must preserve this convention rather than using HASH-style, `#`-prefixed, or whitespace-delimited output.

## Analysis Plan

### Task 1 — Build one primary workflow script for credential handling, download, parsing, product generation, and validation

- Task description:
  - Implement a reproducible end-to-end JMA/Hi-net arrival-time workflow with two execution modes:
    - `smoke`: download and parse only `2025-06-01` span 5 days.
    - `full`: after smoke validation succeeds, process all 67 five-day chunks from `2025-06-01` through `2026-05-01`.
- Required data sources:
  - Hi-net/JMA arrival-time service via HinetPy.
  - `.env` credential file: `<CASE_ROOT>/data/hinet_account/.env`.
  - Existing convention reference: `data/regional/phase.dat`.
  - Local station reference text or station metadata products available under the same data tree as the `.env` source.
- Parameter selection strategy:
  - Generate chunk table from the requested half-open date interval, not from current date.
  - Use preferred chunk length of 5 days because 335 days divides exactly into 67 chunks.
  - Raw filenames: `measure_YYYYMMDD_5.txt`.
  - If future reuse requires non-divisible intervals, final chunk span must be `min(5, remaining_days)` and never exceed 7 days.
  - Use HinetPy `get_arrivaltime(startdate, span, filename=raw_file, os="UNIX")` unless verification shows the Hi-net endpoint requires DOS output; parsing must still strip line endings and validate 96-byte record bodies.
  - Skip download by default when the target raw file already exists and has `size_bytes > 0`.
  - Apply retry/backoff per failed request; rotate among available accounts only if multiple accounts are configured and a request fails for account-specific reasons.
- Constraints:
  - Do not log passwords.
  - Do not overwrite non-empty raw files unless an explicit overwrite option is provided.
  - Every attempted or skipped chunk must be represented in `download_manifest.csv`.
  - Treat an empty downloaded file as failed or empty-result evidence requiring explicit status, not as a successful raw download.
- Key outputs:
  - `download_manifest.csv` with columns:
    - `start_date`
    - `span_days`
    - `raw_file`
    - `exists`
    - `size_bytes`
    - `status`
    - `message`
  - Machine-readable run summary, e.g. `workflow_summary.json`, containing chunk counts, parse counts, regional counts, and validation status.

#### Subtask 1.1 — Credential discovery and account handling

- Task description:
  - Load Hi-net account credentials from environment variables and/or the `.env` file.
- Required data sources:
  - Process environment.
  - `.env` file at the specified path.
- Parameter selection strategy:
  - Detect common single-account variable names such as username/user/account and password/pass.
  - Detect multiple-account patterns if present, e.g. indexed or list-style variables.
  - Record only account labels or masked usernames in logs.
- Constraints:
  - Never print password values.
  - If no valid credential pair is found, stop before download and write failure evidence to the manifest/summary.
- Key outputs:
  - Credential availability status in `workflow_summary.json`.
  - No password-containing output.

#### Subtask 1.2 — Chunked raw measure-file download

- Task description:
  - Download one raw JMA measure file per time chunk using HinetPy.
- Required data sources:
  - HinetPy-supported Hi-net arrival-time interface.
- Parameter selection strategy:
  - Smoke mode chunk:
    - `start_date=2025-06-01`
    - `span_days=5`
    - `raw_file=measure_20250601_5.txt`
  - Full mode chunks:
    - 67 rows, all `span_days=5`, starts every 5 days from `2025-06-01` to `2026-04-27`.
  - Retry failed requests with bounded exponential backoff.
  - Status values should distinguish at least:
    - `skipped_existing`
    - `downloaded`
    - `failed`
    - `empty_file`
- Constraints:
  - Local geographic bounds must not be passed as a download filter.
  - Non-empty existing files are considered reusable raw observations unless overwrite is explicitly enabled.
  - A skipped existing file must still have `exists=true` and measured `size_bytes`.
- Key outputs:
  - Raw files named like `measure_20250601_5.txt`.
  - `download_manifest.csv`.

#### Subtask 1.3 — Fixed-width raw measure parsing

- Task description:
  - Parse each raw JMA measure file into normalized event and pick tables.
- Required data sources:
  - Downloaded `measure_YYYYMMDD_5.txt` files.
  - JMA fixed-width layout definition from the local travel-time format PDF or equivalent format reference found in the project data tree.
- Parameter selection strategy:
  - Validate every non-empty record body has exactly 96 bytes after removing `\r\n` or `\n`.
  - Dispatch by first character:
    - `J`: event header.
    - `_`: station pick.
    - `E`: event terminator.
  - Construct stable `event_id` values from source file plus within-file event sequence, or from origin-time/source fields if uniquely available; record the strategy in the summary.
  - Convert all event origin times, P times, and S times from JST to UTC ISO strings.
  - Use `-1` for missing P or S arrivals.
  - Attach `source_file` to every parsed event and pick.
- Constraints:
  - Do not comma-split or whitespace-split raw measure files.
  - If a station pick appears before an event header, mark parse failure for that file.
  - If an event header lacks a matching `E` terminator, retain recoverable parsed rows only if unambiguous and flag the file in validation output.
  - Preserve original raw text separately; normalized CSV tables are the primary structured products.
- Key outputs:
  - Full `events.csv` with columns:
    - `event_id,origin_time,latitude,longitude,depth_km,magnitude,region,npicks,source_file`
  - Full `picks.csv` with columns:
    - `event_id,station_code,station_number,p_pick_time,s_pick_time,p_quality,s_quality,weight,source_file`
  - Parse diagnostics table, e.g. `parse_diagnostics.csv`, containing file name, record counts by type, malformed record count, parsed event count, parsed pick count, and warning messages.

#### Subtask 1.4 — Smoke-test validation gate

- Task description:
  - Validate the first five-day chunk before running the full interval.
- Required data sources:
  - `measure_20250601_5.txt`.
  - Smoke parsed `events.csv` and `picks.csv` or temporary smoke-specific equivalents.
- Parameter selection strategy:
  - Required validation checks:
    - Raw file exists and is non-empty.
    - All parsed raw record bodies are 96 bytes excluding line endings, or all deviations are explicitly reported.
    - At least one valid parser pass over the file occurs.
    - All pick `event_id` values exist in the event table.
    - Event `npicks` equals the number of pick rows assigned to each event after parsing.
    - Count non-missing P picks where `p_pick_time != -1`.
    - Count non-missing S picks where `s_pick_time != -1`.
    - UTC conversion check: parsed UTC times must be 9 hours earlier than JST raw values, with date rollover handled.
  - Smoke pass condition:
    - Download status is `downloaded` or `skipped_existing` with non-empty file.
    - Parser produces internally consistent event/pick tables.
    - No fatal fixed-width or foreign-key errors.
- Constraints:
  - Do not proceed to full download/parse if smoke validation fails.
  - If the smoke file legitimately contains zero events, the workflow must still prove valid record-level parsing and report zero-event status clearly; otherwise, treat unexplained zero parsed events as a failure requiring inspection.
- Key outputs:
  - `smoke_validation.csv` or `smoke_validation.json`.
  - Smoke P/S count summary:
    - event count
    - pick row count
    - non-missing P count
    - non-missing S count
    - malformed record count
    - validation pass/fail.

#### Subtask 1.5 — Full-range parsing and Sanriku regional filtering

- Task description:
  - After smoke success, parse all chunk files and create full and Sanriku-filtered normalized tables.
- Required data sources:
  - All downloaded/skipped raw measure files from the 67 chunk table.
  - Full parsed `events.csv` and `picks.csv`.
- Parameter selection strategy:
  - Full event table includes all parsed events from the raw measure files.
  - Regional event subset:
    - `38.50 <= latitude <= 42.50`
    - `141.00 <= longitude <= 144.50`
  - Regional picks subset:
    - Include picks whose `event_id` belongs to the regional event subset.
  - Recompute `npicks` for the regional event table based on included regional pick rows.
- Constraints:
  - Do not spatially filter station picks independently of event filtering unless producing an optional station-use subset.
  - Preserve source-file traceability in both full and regional tables.
- Key outputs:
  - Full:
    - `events.csv`
    - `picks.csv`
  - Regional:
    - `events_sanriku.csv`
    - `picks_sanriku.csv`
  - Regional count summary in `workflow_summary.json`.

#### Subtask 1.6 — Generate project-convention `phase.dat`

- Task description:
  - Write a Sanriku regional phase-arrival file preserving the existing project-specific comma-separated block convention.
- Required data sources:
  - Existing convention reference: `data/regional/phase.dat`.
  - Regional normalized tables: `events_sanriku.csv`, `picks_sanriku.csv`.
- Parameter selection strategy:
  - Inspect `data/regional/phase.dat` to identify:
    - Event header field order.
    - Station pick line field order.
    - Delimiter behavior.
    - Missing-value representation.
    - Timestamp formatting.
  - Map normalized regional event and pick fields into the same convention.
  - Preserve `-1` for missing P or S arrivals.
  - Sort events by `origin_time`, then picks by station code or the ordering used in the source convention.
- Constraints:
  - Do not use `#`-prefixed event headers.
  - Do not use whitespace-delimited HASH/HypoDD phase format unless the reference file proves that is the existing convention, which the data summary indicates it does not.
  - `phase.dat` is a derived compatibility product; CSV tables remain the authoritative structured outputs.
- Key outputs:
  - `phase.dat`
  - `phase_format_mapping.csv` documenting how each output field maps to `events_sanriku.csv` and `picks_sanriku.csv`.

#### Subtask 1.7 — Generate `station.sta`

- Task description:
  - Create a station file compatible with the existing project convention for stations used in the Sanriku regional picks.
- Required data sources:
  - Local station reference text from the provided data tree.
  - Existing station products if present, used only to infer field order/format convention.
  - `picks_sanriku.csv`.
- Parameter selection strategy:
  - Include stations appearing in `picks_sanriku.csv`.
  - Match by `station_code` and, where available, `station_number`.
  - Extract station latitude, longitude, elevation/depth, and station code/name fields from the station reference.
  - Use the same comma-separated field order and missing-value conventions as the existing project station file if available.
- Constraints:
  - If station coordinates cannot be resolved for a used station, keep the station in a missing-station report and exclude or flag it according to the project station-file convention.
  - Do not invent coordinates from event locations.
- Key outputs:
  - `station.sta`
  - `station_lookup_report.csv` containing matched station count, unmatched station count, and station identifiers.

#### Subtask 1.8 — Final quality-control validation

- Task description:
  - Validate full and regional products for consistency, traceability, and expected formatting.
- Required data sources:
  - `download_manifest.csv`
  - `parse_diagnostics.csv`
  - `events.csv`, `picks.csv`
  - `events_sanriku.csv`, `picks_sanriku.csv`
  - `phase.dat`
  - `station.sta`
- Parameter selection strategy:
  - Download validation:
    - 67 chunks represented in the manifest.
    - No chunk spans exceed 5 days.
    - Final chunk covers `2026-04-27 ≤ time < 2026-05-02`.
    - No unexpected current-date or 2026-only interval appears.
  - Parser validation:
    - Raw fixed-width record length compliance.
    - Count `J`, `_`, and `E` records by file.
    - Event/pick foreign-key consistency.
    - `npicks` equals grouped pick counts.
    - Origin and pick timestamps are UTC ISO strings or `-1`.
    - Latitude/longitude/depth/magnitude parse ranges are physically plausible and malformed values are reported.
  - Regional validation:
    - All rows in `events_sanriku.csv` satisfy the Sanriku bounds.
    - All rows in `picks_sanriku.csv` reference regional event IDs.
  - Phase/station validation:
    - `phase.dat` event and pick counts match regional CSV-derived counts.
    - `phase.dat` delimiter and header/pick structure match the reference convention from `data/regional/phase.dat`.
    - `station.sta` contains all resolvable stations used by regional picks.
- Constraints:
  - Do not treat fallback, mock, schema-only, or diagnostic-only outputs as successful execution.
  - Any password-like strings found in logs or outputs should cause a redaction/failure flag.
- Key outputs:
  - `validation_report.csv` or `validation_report.json`
  - Updated `workflow_summary.json`
  - Recommended figures:
    - Download timeline/status plot by chunk start date.
    - Histogram of raw file sizes by chunk.
    - Full event epicenter map with Sanriku bounding box.
    - Regional event epicenter map colored by depth or magnitude.
    - Daily event-count time series for full and Sanriku subsets.
    - P and S pick-count time series by day.
    - Bar chart of top stations by regional pick count.
    - Magnitude-depth scatter plot for regional events.