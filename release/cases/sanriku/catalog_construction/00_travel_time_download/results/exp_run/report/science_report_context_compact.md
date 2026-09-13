<science_report_context_compact>

## Context Map
Use this packet in order: objective -> actual methods -> core claims -> evidence index -> limitations/evaluation. Use context references and analysis files only when details are insufficient.

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

## Planning Snapshot
Use this only as intent context; prefer actual methods, claims, and evidence below for report content.
plan_summary: Goal Download JMA/Hi-net arrival-time measure files for `2025-06-01 <= JST time < 2026-05-02`, parse the 96-byte fixed-width JMA measure format into validated full and Sanriku-regional event/pick catalogs, and export project-convention `phase.dat` and `station.sta` products traceable to the normalized CSV tables. Planning Assumptions Use observational data only: JMA arrival-time measure files obtained through the Hi-net/HinetPy arrival-time interface. HinetPy package contract: Main authenticated client: `HinetPy.Client(username, password)`. Arrival-time download method: `Client.get_arrivaltime(startdate, span, filename=None, os="DOS")`. `startdate` accepts string/date/datetime; `span` is an integer number of days. `filename` controls the saved raw measure-file name. `os` accepts `"DOS"` or `"UNIX"`. Return value is the saved filename. Hi-net/JMA arrival-time records are in JST; structure
...[truncated]

## Context References
- full_audit_context: <CASE_ROOT>/run/00_travel_time_download/exp_run/report/science_report_context.md

## Task Ledger
<task_record>
name: 01_hinet_jma_arrivals_workflow
description: Download Hi-net JMA arrival-time measure files, parse fixed-width records, subset the Sanriku region, export compatibility products, and validate all required outputs.
ancestors: none
handoff_json: <CASE_ROOT>/run/00_travel_time_download/exp_run/log/coding_progress/task_handoff/01_hinet_jma_arrivals_workflow.json
analysis_file: <CASE_ROOT>/run/00_travel_time_download/exp_run/analysis/01_hinet_jma_arrivals_workflow.md
output_dir: <CASE_ROOT>/run/00_travel_time_download/exp_run/outputs/01_hinet_jma_arrivals_workflow
</task_record>

<task_record>
name: 02_diagnostic_summaries
description: Generate compact non-authoritative diagnostic summaries and optional QC figures from the validated catalog products.
ancestors: 01_hinet_jma_arrivals_workflow
handoff_json: <CASE_ROOT>/run/00_travel_time_download/exp_run/log/coding_progress/task_handoff/02_diagnostic_summaries.json
analysis_file: (missing)
output_dir: <CASE_ROOT>/run/00_travel_time_download/exp_run/outputs/02_diagnostic_summaries
</task_record>


## Actual Method Summary
This section summarizes what was actually implemented and analyzed. Use it instead of repeating the full plan.
<method_record task="01_hinet_jma_arrivals_workflow">
role: final_analysis
summary: Download Hi-net JMA arrival-time measure files, parse fixed-width records, subset the Sanriku region, export compatibility products, and validate all required outputs.
</method_record>


## Core Scientific Claims
Use these claim-oriented summaries as the backbone of the final report. Each major claim should remain tied to the evidence index below.
(No compact claims available)

## Evidence Index
Use these handoff summaries as the primary artifact index. Read full handoff files only when this compact evidence is insufficient.
<task_evidence task="01_hinet_jma_arrivals_workflow">
status: running
stage: script_execution
quality_flags: task_status:running
handoff_json: <CASE_ROOT>/run/00_travel_time_download/exp_run/log/coding_progress/task_handoff/01_hinet_jma_arrivals_workflow.json
analysis_file: <CASE_ROOT>/run/00_travel_time_download/exp_run/analysis/01_hinet_jma_arrivals_workflow.md
output_dir: <CASE_ROOT>/run/00_travel_time_download/exp_run/outputs/01_hinet_jma_arrivals_workflow
result_summary: Download Hi-net JMA arrival-time measure files, parse fixed-width records, subset the Sanriku region, export compatibility products, and validate all required outputs. Status=running; outputs=2 discovered; primary=2.

primary_outputs:
- chunk_schedule.csv: <CASE_ROOT>/run/00_travel_time_download/exp_run/outputs/01_hinet_jma_arrivals_workflow/chunk_schedule.csv
- measure_20250601_5.txt.part: <CASE_ROOT>/run/00_travel_time_download/exp_run/outputs/01_hinet_jma_arrivals_workflow/measure_20250601_5.txt.part
</task_evidence>

<task_evidence task="02_diagnostic_summaries">
status: pending
stage: unknown
quality_flags: task_status:pending
handoff_json: <CASE_ROOT>/run/00_travel_time_download/exp_run/log/coding_progress/task_handoff/02_diagnostic_summaries.json
analysis_file: <CASE_ROOT>/run/00_travel_time_download/exp_run/analysis/02_diagnostic_summaries.md
output_dir: <CASE_ROOT>/run/00_travel_time_download/exp_run/outputs/02_diagnostic_summaries
result_summary: Generate compact non-authoritative diagnostic summaries and optional QC figures from the validated catalog products. Status=pending; outputs=0 discovered; primary=0.
</task_evidence>


## Analysis Source Index
Read these task analysis files only when the method summary, claims, limitations, and evidence index are insufficient.
- 01_hinet_jma_arrivals_workflow: analysis=<CASE_ROOT>/run/00_travel_time_download/exp_run/analysis/01_hinet_jma_arrivals_workflow.md; output_dir=<CASE_ROOT>/run/00_travel_time_download/exp_run/outputs/01_hinet_jma_arrivals_workflow

## Report Synthesis Rules
- Start from the scientific objective, actual methods, core claims, and evidence index.
- Choose the final report shape according to the request and evidence; do not force a fixed template.
- Tie every major result to task analyses and concrete output files from the evidence index.
- Include warnings, assumptions, partial coverage, failed items, and other limitations when present.
- Inspect full handoff JSON, analyses, or raw outputs only when the compact context is insufficient.
- Do not fabricate results, citations, or file paths.

</science_report_context_compact>
