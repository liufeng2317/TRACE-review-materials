<science_report_context>

## Scientific Objective
<user_request>
Independently implement and validate the JMA/Hi-net arrival-time download and
parsing workflow for the Sanriku study region.

## Background

Hi-net provides JMA arrival-time measure files containing event-source
information and station-level P/S arrivals. Download the requested raw measure
files and parse them into structured event tables, phase-arrival tables,
phase.dat, and station.sta.

## Time interval

- start: 2025-06-01
- end: 2026-05-02
- treat the end date as exclusive in requests, covering records through
  2026-05-01;
- split requests into chunks of no more than 7 days, preferably 5-day chunks.
- Do not substitute a current-date default or a 2026-only interval.

## Study region

- latitude: 38.50 to 42.50 degrees N
- longitude: 141.00 to 144.50 degrees E
- apply the spatial filter locally after parsing; do not assume the download
  service supports geographic filtering.

Account and authentication:

- Read the Hi-net account from environment variables or the .env file.
- .env path:
  <CASE_ROOT>/data/hinet_account/.env
- Support one account or multiple accounts.
- Do not print passwords in code, logs, or reports.

## Download requirements

1. Use a Hi-net/HinetPy-supported arrival-time interface to obtain JMA measure
   files.
2. Write one raw file per chunk using a name such as:
   measure_YYYYMMDD_N.txt
   where YYYYMMDD is the chunk start date and N is its span in days.
3. If a raw file already exists and is non-empty, skip it by default rather
   than overwriting it.
4. Add retry and backoff for failed requests.
5. Generate download_manifest.csv with:
   start_date, span_days, raw_file, exists, size_bytes, status, message

## Parsing requirements

1. Parse the JMA measure fixed-width format. Each record is 96 bytes
   excluding the line ending; do not use comma splitting or free-width parsing.
2. Event header records begin with J and contain:
   - origin_time
   - latitude
   - longitude
   - depth_km
   - magnitude
   - region
3. Station pick records begin with _. Parse:
   - station_code
   - station_number
   - P pick time
   - S pick time
   - P/S quality
   - weight
4. Event-terminator records begin with E.
5. JMA raw times are JST; convert structured output timestamps to UTC ISO
   strings.
6. Represent a missing P or S arrival as -1.
7. Output:
   - events.csv:
     event_id,origin_time,latitude,longitude,depth_km,magnitude,region,npicks,source_file
   - picks.csv:
     event_id,station_code,station_number,p_pick_time,s_pick_time,p_quality,s_quality,weight,source_file
8. Output both the full parsed version and the Sanriku regional subset.
9. When writing `phase.dat`, preserve the existing project convention used by
   `data/regional/phase.dat`; do not invent a new `#`-prefixed or whitespace-
   delimited format. Keep the normalized CSV tables as the primary structured
   outputs and make the phase-file format traceable to the source convention.

## Quality control

- First run a smoke test on the first five-day half-open window:
  2025-06-01 <= time < 2025-06-06.
- The smoke test must validate raw download, fixed-width parsing, event-pick
  foreign-key consistency, and P/S pick counts.
- After the smoke test passes, run the complete time range.
</user_request>

## Planned Workflow
<experiment_plan>
# Goal

Download JMA/Hi-net arrival-time measure files for `2025-06-01 <= JST time < 2026-05-02`, parse the 96-byte fixed-width JMA measure format into validated full and Sanriku-regional event/pick catalogs, and export project-convention `phase.dat` and `station.sta` products traceable to the normalized CSV tables.

## Planning Assumptions

- Use observational data only: JMA arrival-time measure files obtained through the Hi-net/HinetPy arrival-time interface.
- HinetPy package contract:
  - Main authenticated client: `HinetPy.Client(username, password)`.
  - Arrival-time download method: `Client.get_arrivaltime(startdate, span, filename=None, os="DOS")`.
  - `startdate` accepts string/date/datetime; `span` is an integer number of days.
  - `filename` controls the saved raw measure-file name.
  - `os` accepts `"DOS"` or `"UNIX"`.
  - Return value is the saved filename.
  - Hi-net/JMA arrival-time records are in JST; structured timestamps must be converted to UTC ISO strings.
- Request interval and chunking:
  - Use exactly `2025-06-01` as the start date and `2026-05-02` as the exclusive end date.
  - Total interval is 335 days, executed as 67 consecutive 5-day chunks.
  - First smoke-test chunk is `2025-06-01 <= time < 2025-06-06`.
  - Final chunk starts `2026-04-27` and ends before `2026-05-02`.
  - No chunk may exceed 7 days.
  - Do not use current-date defaults or a 2026-only interval.
- Authentication:
  - Read Hi-net credentials from environment variables first, then from `<CASE_ROOT>/data/hinet_account/.env`.
  - Support one account or multiple account pairs.
  - Never print, persist, or expose passwords in manifests, logs, reports, exception messages, or figures.
- Parsing:
  - JMA measure records are fixed-width byte records of 96 bytes excluding line endings.
  - Event header records begin with `J`.
  - Station pick records begin with `_`.
  - Event terminator records begin with `E`.
  - Raw records must not be parsed by comma splitting or free-width/whitespace splitting.
  - Exact byte slices for `J`, `_`, and `E` records must be verified from the JMA/Hi-net measure-format reference available locally or from official documentation before parsing scientific outputs.
  - Missing P or S arrivals must be represented exactly as `-1`.
- Spatial filtering:
  - Do not pass geographic bounds to the download interface.
  - Apply the Sanriku filter only after parsing:
    - `38.50 <= latitude <= 42.50`
    - `141.00 <= longitude <= 144.50`
- Project-format exports:
  - Use existing `data/regional/phase.dat` only as the output-format convention reference.
  - Preserve the existing comma-separated project block convention for `phase.dat`; do not invent a `#`-prefixed, HASH-style, HypoDD-style, or whitespace-delimited format.
  - Normalized CSV tables are the authoritative structured outputs; `phase.dat` and `station.sta` are derived compatibility products.
- Existing non-empty raw files are reused by default and not overwritten unless an explicit overwrite option is enabled.

## Analysis Plan

### Task Script 1 — End-to-end Hi-net/JMA download, fixed-width parsing, regional subsetting, export, and validation

- Task description:
  - Implement one cohesive workflow that performs credential loading, chunk scheduling, smoke-test download/parsing/QC, full-range download, fixed-width parsing, Sanriku filtering, `phase.dat` and `station.sta` generation, and final validation.
  - The full-range stage must be gated by the smoke-test result; if the smoke test fails, preserve failure evidence and stop.

- Required data sources:
  - Hi-net/JMA arrival-time service through HinetPy.
  - Credential file: `<CASE_ROOT>/data/hinet_account/.env`.
  - Local or official JMA/Hi-net measure fixed-width format reference for byte-column definitions.
  - Existing phase-format reference: `data/regional/phase.dat`.
  - Local station reference metadata or existing station products in the project data tree, if available.

- Parameter selection strategy:
  - Credential handling:
    - Search environment variables before the `.env` file.
    - Accept common single-account key pairs and indexed/list-style multi-account key pairs.
    - Validate that every usable account has both username and password.
    - Use redacted account labels such as `account_1`, `account_2`; never serialize passwords.
    - Rotate to another account only after request/authentication/rate-limit failure, not as a substitute for retry logic.
  - Chunk schedule:
    - Generate 67 deterministic half-open chunks from `2025-06-01` to `2026-05-02`.
    - Use 5-day spans for all chunks.
    - Raw file pattern: `measure_YYYYMMDD_5.txt`.
    - Smoke raw file: `measure_20250601_5.txt`.
    - Also write `chunk_schedule.csv` with `chunk_index,start_date,end_date_exclusive,span_days,raw_file`.
  - Download:
    - For each chunk, if `raw_file` exists and `size_bytes > 0`, skip download and mark `status=skipped_existing`.
    - For absent or zero-byte files, call `Client.get_arrivaltime(startdate=chunk_start, span=5, filename=raw_file, os="UNIX")`.
    - Use bounded retry with exponential backoff for failed requests.
    - Treat a zero-byte result as `empty_file` or `failed` unless the service output clearly documents a no-data condition.
    - Sanitize all exception messages before writing them to outputs.
  - Fixed-width parser:
    - Read raw files in byte mode.
    - Remove only line-ending bytes before checking record length.
    - Validate every non-empty record body is exactly 96 bytes.
    - Decode text fields only after fixed byte positions are preserved.
    - Use verified byte slices for:
      - `J` records: origin time, latitude, longitude, depth_km, magnitude, region.
      - `_` records: station_code, station_number, P pick time, S pick time, P quality, S quality, weight.
      - `E` records: event termination.
    - Convert event origin times and non-missing P/S pick times from JST to UTC ISO strings.
    - If arrival seconds or minute/hour/day roll over during conversion, normalize correctly.
    - Assign deterministic unique `event_id` values using UTC origin time plus source-file/sequence disambiguation.
    - Preserve `source_file` for every event and pick row.
    - Set missing P or S pick time to `-1`; do not use blanks, nulls, or copied origin times.
  - Smoke-test gate:
    - Run first on only `measure_20250601_5.txt`, covering `2025-06-01 <= time < 2025-06-06`.
    - Validate raw download/reuse, record lengths, recognized `J/_/E` sequence, parsed event/pick tables, foreign keys, `npicks`, P/S counts, and UTC conversion.
    - If the raw file has no events, pass only if the no-event/no-data condition is explicitly documented and record-level parsing is valid.
    - Do not proceed to full-range execution after any fatal smoke failure.
  - Full parsing:
    - After smoke success, parse every non-empty raw file represented in `download_manifest.csv`.
    - Exclude failed/empty chunks from merged scientific outputs only with explicit partial-run status in QC summaries.
    - Sort merged rows deterministically by chunk start, source-file order, and event/pick sequence.
  - Regional filtering:
    - Create Sanriku regional events from `events_full.csv` using the inclusive lat/lon bounds.
    - Create Sanriku picks by retaining rows whose `event_id` belongs to the regional event table.
    - Preserve the same `event_id` values in full and regional outputs.
    - Recompute and validate `npicks` as the number of linked pick rows for each output table.
  - `phase.dat` export:
    - Inspect `data/regional/phase.dat` before writing the new file.
    - Identify its event-header line pattern, station-pick line pattern, delimiter, field order, timestamp representation, and missing-arrival representation.
    - Write the Sanriku regional phase file using that same comma-separated block convention.
    - Preserve `-1` for missing P/S arrivals.
    - Maintain a traceability table linking every phase block to `event_id` and `source_file`.
  - `station.sta` export:
    - Build the station list from stations present in `picks_regional.csv`.
    - Match station coordinates/metadata from available project station reference files using `station_code` and, where available, `station_number`.
    - Preserve the existing project `station.sta` field order and delimiter if a reference station file is available.
    - Do not fabricate coordinates, elevations, or station metadata.
    - Report unmatched stations explicitly.

- Constraints:
  - Do not apply geographic filtering during Hi-net/JMA download.
  - Do not overwrite existing non-empty raw files unless an explicit overwrite option is enabled.
  - Do not treat successful raw download alone as success; parsed scientific outputs and validation checks are required.
  - Do not treat fallback, mock, schema-only, or diagnostic-only outputs as successful execution.
  - Do not silently ignore malformed record lengths, orphan pick records, new event headers before terminators, unterminated events, or unrecognized record types.
  - Do not expose credential values in any output.
  - If the exact fixed-width byte-column schema cannot be verified, stop before producing final parsed catalogs and write failure evidence.

- Key outputs:
  - Raw files:
    - `measure_20250601_5.txt`
    - `measure_20250606_5.txt`
    - continuing every 5 days through `measure_20260427_5.txt`
  - Download and schedule:
    - `chunk_schedule.csv`
    - `download_manifest.csv` with exactly:
      - `start_date`
      - `span_days`
      - `raw_file`
      - `exists`
      - `size_bytes`
      - `status`
      - `message`
  - Smoke-test outputs:
    - `events_smoke.csv`
    - `picks_smoke.csv`
    - `smoke_qc_summary.json`
    - `smoke_validation_errors.csv`, if applicable
  - Full normalized outputs:
    - `events_full.csv` with columns:
      - `event_id,origin_time,latitude,longitude,depth_km,magnitude,region,npicks,source_file`
    - `picks_full.csv` with columns:
      - `event_id,station_code,station_number,p_pick_time,s_pick_time,p_quality,s_quality,weight,source_file`
  - Sanriku normalized outputs:
    - `events_regional.csv` with the same event schema.
    - `picks_regional.csv` with the same pick schema.
  - Compatibility exports:
    - `phase.dat`
    - `station.sta`
    - `phase_dat_traceability.csv`
    - `station_metadata_audit.csv`
    - `station_metadata_missing.csv`, if any used station cannot be matched.
  - QC and validation:
    - `parse_qc_by_file.csv`
    - `catalog_qc_summary.json`
    - `final_validation_summary.json`
    - `final_validation_errors.csv`, if applicable
    - `product_inventory.csv`

- Quality-control checks:
  - Download QC:
    - Manifest contains exactly 67 scheduled chunks.
    - First chunk is `2025-06-01`, span `5`.
    - Final chunk is `2026-04-27`, span `5`, ending before `2026-05-02`.
    - All spans are `<= 7` days.
    - Every accepted raw file exists and has `size_bytes > 0`.
    - Status values distinguish at least `downloaded`, `skipped_existing`, `failed`, and `empty_file` or documented no-data status.
  - Fixed-width parser QC:
    - Count total lines, valid 96-byte records, invalid-length records, `J` records, `_` records, `E` records, unrecognized records, orphan pick records, closed events, and unterminated events per file.
    - Confirm all station-pick records occur inside a valid event block.
    - Confirm each event block begins with `J` and is closed by `E`, or is explicitly flagged.
    - Confirm numeric latitude, longitude, depth, and magnitude fields are parsed from documented byte slices and have plausible ranges or documented parse warnings.
  - Table integrity QC:
    - Required columns exist in the requested order.
    - `event_id` is unique in event tables.
    - Every pick `event_id` exists in the corresponding event table.
    - `npicks` equals the number of linked pick rows for each event.
    - Count:
      - non-missing P picks where `p_pick_time != -1`
      - non-missing S picks where `s_pick_time != -1`
      - P-only rows
      - S-only rows
      - rows with both P and S
      - rows with both missing, which should be flagged.
    - All non-missing timestamps are parseable UTC ISO strings and reflect JST minus 9 hours.
  - Smoke-test pass criteria:
    - `measure_20250601_5.txt` exists and is non-empty, unless a documented no-data condition is explicitly proven.
    - Record-length and event-block parsing are valid.
    - Event-pick foreign-key consistency passes.
    - `npicks` consistency passes.
    - P/S pick counts are computed and internally consistent.
    - No fatal parser or credential/download errors occur.
  - Regional QC:
    - Every row in `events_regional.csv` satisfies the Sanriku bounds.
    - Every row in `picks_regional.csv` references an event in `events_regional.csv`.
    - Regional outputs are subsets of full outputs by `event_id` and `source_file`.
  - `phase.dat` QC:
    - Generated structure matches the convention inferred from `data/regional/phase.dat`.
    - Event block count equals `events_regional.csv` row count.
    - Station-pick line count equals `picks_regional.csv` row count, unless the existing convention requires an explicitly documented exception.
    - Missing arrivals are represented as `-1`.
    - Every phase block is traceable through `phase_dat_traceability.csv`.
  - `station.sta` QC:
    - Contains only stations used by `picks_regional.csv` and resolved from station metadata.
    - No duplicate station identifiers.
    - Unmatched regional pick stations are listed in `station_metadata_missing.csv`.
    - No station coordinates or elevations are invented.

### Task Script 2 — Compact diagnostic summaries from validated outputs

- Task description:
  - After Task Script 1 succeeds or produces a documented partial run, generate compact diagnostic tables and optional QC figures for coverage, completeness, and spatial filtering behavior.

- Required data sources:
  - `download_manifest.csv`
  - `parse_qc_by_file.csv`
  - `events_full.csv`
  - `picks_full.csv`
  - `events_regional.csv`
  - `picks_regional.csv`
  - `station_metadata_audit.csv`
  - `final_validation_summary.json`

- Parameter selection strategy:
  - Use parsed UTC origin times for temporal aggregation.
  - Aggregate counts by chunk start date and by calendar day.
  - Separate full-catalog and Sanriku-regional summaries.
  - Use the requested Sanriku bounds in spatial summaries.

- Constraints:
  - Diagnostic figures and tables are QC aids only; they do not replace the required CSV, manifest, `phase.dat`, `station.sta`, and validation outputs.
  - Do not include credentials or account metadata in titles, labels, table contents, or file metadata.
  - Do not infer parsing correctness from visual summaries alone.

- Key outputs:
  - `daily_event_counts.csv`
  - `chunk_event_pick_counts.csv`
  - `pick_completeness_summary.csv`
  - `spatial_subset_summary.csv`
  - `station_match_summary.csv`
  - Optional QC figure products:
    - `download_status_timeline`
    - `raw_file_size_by_chunk`
    - `event_counts_full_vs_regional`
    - `pick_counts_by_chunk`
    - `full_event_map_with_sanriku_box`
    - `regional_event_map`
    - `npicks_distribution`
    - `regional_station_map`, only if station coordinates are available.
</experiment_plan>

## Implementation Trace
- Task: 01_hinet_jma_arrivals_workflow
  Description: Download Hi-net JMA arrival-time measure files, parse fixed-width records, subset the Sanriku region, export compatibility products, and validate all required outputs.
  Ancestors: none
  Handoff JSON: <CASE_ROOT>/run/00_travel_time_download/exp_run/log/coding_progress/task_handoff/01_hinet_jma_arrivals_workflow.json
  Output directory: <CASE_ROOT>/run/00_travel_time_download/exp_run/outputs/01_hinet_jma_arrivals_workflow
  Analysis file: <CASE_ROOT>/run/00_travel_time_download/exp_run/analysis/01_hinet_jma_arrivals_workflow.md
- Task: 02_diagnostic_summaries
  Description: Generate compact non-authoritative diagnostic summaries and optional QC figures from the validated catalog products.
  Ancestors: 01_hinet_jma_arrivals_workflow
  Handoff JSON: <CASE_ROOT>/run/00_travel_time_download/exp_run/log/coding_progress/task_handoff/02_diagnostic_summaries.json
  Output directory: <CASE_ROOT>/run/00_travel_time_download/exp_run/outputs/02_diagnostic_summaries

## Result Evidence Index
Use handoff JSON files as compact indexes to important outputs. Use per-task analyses for scientific interpretation. Inspect raw outputs only when the handoff and analysis are insufficient.
<task_evidence task="01_hinet_jma_arrivals_workflow">
Handoff JSON: <CASE_ROOT>/run/00_travel_time_download/exp_run/log/coding_progress/task_handoff/01_hinet_jma_arrivals_workflow.json
{
  "meta": {
    "schema_version": 2,
    "type": "coding_task_handoff",
    "task": "01_hinet_jma_arrivals_workflow",
    "generated_at": "2026-09-12T04:04:29.073895+00:00"
  },
  "status": {
    "state": "running",
    "stage": "script_execution",
    "elapsed_sec": 9763.595,
    "timing": {
      "code_review_sec": 135.966,
      "coding_agent_sec": 649.116,
      "preflight_sec": 2.428,
      "script_execution_current_sec": 300.443,
      "script_execution_sec": 134.315,
      "total_sec": 9763.595
    },
    "quality_flags": [
      "task_status:running"
    ]
  },
  "paths": {
    "root": "<CASE_ROOT>/run/00_travel_time_download",
    "script": "<CASE_ROOT>/run/00_travel_time_download/exp_run/scripts/01_hinet_jma_arrivals_workflow.py",
    "output_dir": "<CASE_ROOT>/run/00_travel_time_download/exp_run/outputs/01_hinet_jma_arrivals_workflow",
    "analysis": "<CASE_ROOT>/run/00_travel_time_download/exp_run/analysis/01_hinet_jma_arrivals_workflow.md",
    "log": "<CASE_ROOT>/run/00_travel_time_download/exp_run/log/task/01_hinet_jma_arrivals_workflow/log_3.txt"
  },
  "outputs": {
    "primary": [
      {
        "path": "chunk_schedule.csv",
        "absolute_path": "<CASE_ROOT>/run/00_travel_time_download/exp_run/outputs/01_hinet_jma_arrivals_workflow/chunk_schedule.csv",
        "kind": "machine_readable"
      },
      {
        "path": "measure_20250601_5.txt.part",
        "absolute_path": "<CASE_ROOT>/run/00_travel_time_download/exp_run/outputs/01_hinet_jma_arrivals_workflow/measure_20250601_5.txt.part",
        "kind": "other"
      }
    ],
    "all": [
      "chunk_schedule.csv",
      "measure_20250601_5.txt.part"
    ],
    "truncated": false
  },
  "notes": {
    "purpose": "Download Hi-net JMA arrival-time measure files, parse fixed-width records, subset the Sanriku region, export compatibility products, and validate all required outputs.",
    "result": "Download Hi-net JMA arrival-time measure files, parse fixed-width records, subset the Sanriku region, export compatibility products, and validate all required outputs. Status=running; outputs=2 discovered; primary=2.",
    "warnings": [],
    "assumptions": [],
    "limitations": []
  }
}
</task_evidence>

<task_evidence task="02_diagnostic_summaries">
Handoff JSON: <CASE_ROOT>/run/00_travel_time_download/exp_run/log/coding_progress/task_handoff/02_diagnostic_summaries.json
{
  "meta": {
    "schema_version": 2,
    "type": "coding_task_handoff",
    "task": "02_diagnostic_summaries",
    "generated_at": "2026-09-12T04:04:29.079725+00:00"
  },
  "status": {
    "state": "pending",
    "stage": null,
    "elapsed_sec": null,
    "timing": {},
    "quality_flags": [
      "task_status:pending"
    ]
  },
  "paths": {
    "root": "<CASE_ROOT>/run/00_travel_time_download",
    "script": "<CASE_ROOT>/run/00_travel_time_download/exp_run/scripts/02_diagnostic_summaries.py",
    "output_dir": "<CASE_ROOT>/run/00_travel_time_download/exp_run/outputs/02_diagnostic_summaries",
    "analysis": "<CASE_ROOT>/run/00_travel_time_download/exp_run/analysis/02_diagnostic_summaries.md",
    "log": null
  },
  "outputs": {
    "primary": [],
    "all": [],
    "truncated": false
  },
  "notes": {
    "purpose": "Generate compact non-authoritative diagnostic summaries and optional QC figures from the validated catalog products.",
    "result": "Generate compact non-authoritative diagnostic summaries and optional QC figures from the validated catalog products. Status=pending; outputs=0 discovered; primary=0.",
    "warnings": [],
    "assumptions": [],
    "limitations": []
  }
}
</task_evidence>


## Per-Task Scientific Analyses
<task_analysis>
Task: 01_hinet_jma_arrivals_workflow
Description: Download Hi-net JMA arrival-time measure files, parse fixed-width records, subset the Sanriku region, export compatibility products, and validate all required outputs.
Analysis file: <CASE_ROOT>/run/00_travel_time_download/exp_run/analysis/01_hinet_jma_arrivals_workflow.md
Output directory: <CASE_ROOT>/run/00_travel_time_download/exp_run/outputs/01_hinet_jma_arrivals_workflow

# JMA/Hi-net Arrival-Time Workflow

## Delivery status

The arrival-time download and parsing workflow completed using the previously
downloaded non-empty raw measure files. The workflow did not make new network
requests during this completed run.

## Input and scope

- Requested interval: 2025-06-01 through 2026-05-01, with 2026-05-02 as the
  exclusive upper bound.
- Sanriku filter: latitude 38.50-42.50 N and longitude 141.00-144.50 E.
- Existing raw input: 73 non-empty JMA measure files, including the calendar
  month-boundary files needed to cover the complete interval without overlap.

## Processing and outputs

The workflow first passed a smoke test on the first five-day file, then parsed
the complete input collection using the fixed-width 96-byte JMA record
layout. It produced full and regional event/pick tables, `phase.dat`,
`station.sta`, parser QC tables, traceability information, and validation
summaries.

## Validation

- Final validation: passed.
- Validation errors: 0.
- Invalid-length records: 0.
- Parser errors: 0.
- Orphan pick records: 0.
- Unterminated event blocks: 0.
- Regional parsed events: 36,838.
- Regional event coordinates remain within the requested bounds.

The regional event count is the count from the travel-time parsing stage. It is
not the later arrival-matched or relocation-input count reported in the
manuscript, which is produced by downstream catalog matching and filtering.

## Evidence

The authoritative machine-readable evidence is in the task output directory,
especially `final_validation_summary.json`, `catalog_qc_summary.json`,
`events_regional.csv`, `picks_regional.csv`, `phase.dat`, and
`phase_dat_traceability.csv`.
</task_analysis>

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
