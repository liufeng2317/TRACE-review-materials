---
author:
- TRACE
date: 2026-09-12
title: Independent Implementation and Validation of a JMA/Hi-net Arrival-Time Download and Parsing Workflow for the Sanriku Region
---

# Abstract

This report documents an independent implementation and validation of a JMA/Hi-net arrival-time workflow for the Sanriku study region. The requested interval was 2025-06-01 through 2026-05-01, implemented as a half-open request interval ending at 2026-05-02. The implemented workflow supports authenticated Hi-net/HinetPy arrival-time retrieval, skip-by-default reuse of non-empty raw files, retry/backoff for network requests, byte-exact fixed-width parsing of 96-byte JMA measure records, conversion of Japanese Standard Time (JST) timestamps to UTC ISO strings, regional subsetting, and export of normalized event/pick tables plus project-compatible `phase.dat` and `station.sta` products. In the completed execution analyzed here, no new network request was made because 73 pre-existing non-empty raw measure files were discovered and reused. The smoke test on the first five-day raw file passed, and final validation passed with zero invalid-length records, zero parser errors, zero orphan picks, zero unterminated event blocks, and zero catalog validation errors. The full parsed catalog contains 287,868 events and 4,054,829 station-pick rows; the Sanriku regional subset contains 36,838 events and 672,005 station-pick rows.

# Objective and Scope

The objective was to implement and validate a reproducible workflow for JMA arrival-time measure files available through the Hi-net/HinetPy arrival-time interface, then parse those files into structured products for the Sanriku study region. The requested temporal and spatial scope was:

- requested time interval: $`2025\text{-}06\text{-}01 \leq t < 2026\text{-}05\text{-}02`$, covering records through 2026-05-01 in JST request time;

- preferred request chunking: no more than 7 days per request, preferably five-day chunks;

- regional filter: latitude 38.50–42.50$`^{\circ}`$N and longitude 141.00–144.50$`^{\circ}`$E;

- spatial filtering requirement: apply the geographic selection locally after parsing, rather than assuming server-side geographic filtering.

The implemented outputs were designed to satisfy two complementary use cases. First, normalized CSV tables preserve event and station-pick information in explicit relational form. Second, `phase.dat` and `station.sta` maintain compatibility with the project relocation convention. The canonical products used by relocation are the expert-processed files under `<CASE_ROOT>/run/00_travel_time_download/exp_run/expert/outputs`.

# Implementation Summary

The implemented script is located at:

<div class="center">

<a href="<CASE_ROOT>/run/00_travel_time_download/exp_run/scripts/01_hinet_jma_arrivals_workflow.py" class="uri"><CASE_ROOT>/run/00_travel_time_download/exp_run/scripts/01_hinet_jma_arrivals_workflow.py</a>

</div>

The main output directory is:

<div class="center">

<a href="<CASE_ROOT>/run/00_travel_time_download/exp_run/outputs/01_hinet_jma_arrivals_workflow" class="uri"><CASE_ROOT>/run/00_travel_time_download/exp_run/outputs/01_hinet_jma_arrivals_workflow</a>

</div>

## Download and Raw-File Handling

The workflow implements authenticated arrival-time retrieval through `HinetPy.Client.get_arrivaltime`. Hi-net credentials are loaded from environment variables or from the configured `.env` file, with support for one or multiple accounts. Passwords are redacted from messages. For direct network retrieval, the script writes one raw file per chunk with names of the form `measure_YYYYMMDD_N.txt`, skips non-empty existing files by default, and performs per-account retry/backoff on failed requests. Download/reuse state is recorded in `download_manifest.csv` with the requested columns `start_date`, `span_days`, `raw_file`, `exists`, `size_bytes`, `status`, and `message`.

In the completed run, the workflow discovered a complete set of 73 non-empty existing raw files in the prior raw-data directory and reused them. Thus, the final products validate the downloader/reuse and parser workflow, but the completed run did not exercise a fresh network transfer. The manifest records every raw input row with status `reused_existing_source`; see Table <a href="#tab:download_scope" data-reference-type="ref" data-reference="tab:download_scope">[tab:download_scope]</a>. The planned five-day schedule is also preserved in `chunk_schedule.csv`; it contains 67 planned half-open five-day windows from 2025-06-01 to 2026-05-02. The reused raw-file collection contains additional month-boundary files but still has a maximum span of 5 days and covers the requested interval through the 2026-05-01 boundary.

## Fixed-Width Parser

The parser treats each non-empty JMA measure record as a 96-byte record excluding line endings. It does not comma-split or use free-width parsing. The parser reads byte slices with CP932 decoding and classifies records as follows:

- event header records beginning with `J`; parsed fields include origin time, latitude, longitude, depth, magnitude, and region;

- station pick records beginning with `_`; parsed fields include station code, station number, first and second pick times, phase quality flags, and weight;

- event terminators beginning with `E`;

- documented auxiliary/non-primary records, including `j` and `W`, counted separately and excluded from the event/pick tables.

All JMA raw times are interpreted as JST and exported as UTC ISO strings ending in `Z`. Missing P or S picks are represented by `-1`. Event identifiers are stable hashes derived from the source file, event sequence, and origin time, enabling foreign-key checks between event and pick tables.

The event-table schema is:

<div class="center">

`event_id, origin_time, latitude, longitude, depth_km, magnitude, region, npicks, source_file`.

</div>

The pick-table schema is:

<div class="center">

`event_id, station_code, station_number, p_pick_time, s_pick_time, p_quality, s_quality, weight, source_file`.

</div>

Both full and Sanriku-regional versions of these tables were written. The files `events.csv` and `picks.csv` are user-facing aliases for the regional products.

## Regional Selection and Compatibility Products

The Sanriku subset was applied after parsing by selecting events with coordinates inside 38.50–42.50$`^{\circ}`$N and 141.00–144.50$`^{\circ}`$E, then retaining only picks whose `event_id` belongs to the selected event set. Regional `npicks` values were recomputed after subsetting.

The `phase.dat` export preserves the existing project convention rather than introducing a new `#`-prefixed or whitespace-delimited format. The inferred convention is comma-delimited, with six event-line fields and five pick-line fields. The event-line example recorded by validation is:

<div class="center">

`2025-09-30T16:09:25.360000Z,38.702667,142.256833,41.340,2.80,1`

</div>

The pick-line example is:

<div class="center">

`N.313S,2025-09-30T16:09:32.740000Z,2025-09-30T16:09:38.470000Z,0.000e+00,1.00`

</div>

A separate traceability file maps each line block in `phase.dat` back to event identifiers, source files, and station codes.

# Validation Procedure

Validation was staged in the requested order. First, the workflow ran a smoke test on the first five-day file, representing $`2025\text{-}06\text{-}01 \leq t < 2025\text{-}06\text{-}06`$. The smoke test verified that the raw file was present and non-empty, that 96-byte fixed-width parsing produced valid event and pick tables, that event–pick foreign keys were consistent, and that P/S pick counts were non-degenerate. After the smoke test passed, the complete reused raw-file collection was parsed and validated.

Final validation checked the following conditions:

1.  required event and pick columns are present in the required order;

2.  event identifiers are unique;

3.  every pick references an existing event;

4.  each event `npicks` value equals the number of linked pick rows;

5.  P and S timestamps are parseable UTC strings when not equal to `-1`;

6.  no pick row has both P and S missing;

7.  regional event coordinates remain inside the requested Sanriku bounds;

8.  fixed-width parser fatal counters are zero: invalid record length, unrecognized record, orphan pick, unterminated event, and parser error.

The authoritative validation summaries are `smoke_qc_summary.json`, `catalog_qc_summary.json`, and `final_validation_summary.json`; the final validation error file is empty apart from the CSV newline.

# Results

## Download/Reuse Coverage

Table <a href="#tab:download_scope" data-reference-type="ref" data-reference="tab:download_scope">[tab:download_scope]</a> summarizes the raw-file coverage and download/reuse evidence. The manifest contains 73 rows, all with status `reused_existing_source`. All accepted rows were non-empty, and the maximum manifest span was 5 days. The first raw input was `measure_20250601_5.txt`; the last was `measure_20260501_1.txt`, which provides the 2026-05-01 boundary day while respecting the exclusive 2026-05-02 upper bound.

<div class="tabular">

P0.30P0.62 Item & Value / evidence  
Planned schedule & 67 five-day half-open windows in <a href="<CASE_ROOT>/run/00_travel_time_download/exp_run/outputs/01_hinet_jma_arrivals_workflow/chunk_schedule.csv" class="uri"><CASE_ROOT>/run/00_travel_time_download/exp_run/outputs/01_hinet_jma_arrivals_workflow/chunk_schedule.csv</a>  
Completed raw inputs & 73 reused non-empty raw files in <a href="<CASE_ROOT>/run/00_travel_time_download/exp_run/outputs/01_hinet_jma_arrivals_workflow/download_manifest.csv" class="uri"><CASE_ROOT>/run/00_travel_time_download/exp_run/outputs/01_hinet_jma_arrivals_workflow/download_manifest.csv</a>  
Manifest statuses & 73 `reused_existing_source`; no `downloaded`, `failed`, or `empty_file` rows in the completed run  
First manifest row & 2025-06-01, span 5 days, raw size 6,841,119 bytes  
Last manifest row & 2026-05-01, span 1 day, raw size 1,292,816 bytes  
Maximum raw-file span & 5 days  
Parsed raw byte total & 478,385,861 bytes across 73 files, summarized in <a href="<CASE_ROOT>/run/00_travel_time_download/exp_run/outputs/01_hinet_jma_arrivals_workflow/parse_qc_by_file.csv" class="uri"><CASE_ROOT>/run/00_travel_time_download/exp_run/outputs/01_hinet_jma_arrivals_workflow/parse_qc_by_file.csv</a>  

</div>

## Smoke-Test Results

The first five-day smoke test passed. It used the raw file <a href="<CASE_ROOT>/data_downloading/travel_time/data/raw/measure_20250601_5.txt" class="uri"><CASE_ROOT>/data_downloading/travel_time/data/raw/measure_20250601_5.txt</a>, whose size was 6,841,119 bytes. Table <a href="#tab:smoke" data-reference-type="ref" data-reference="tab:smoke">1</a> summarizes the smoke-test parsed counts. The smoke-test products are `events_smoke.csv`, `picks_smoke.csv`, `smoke_parse_qc_by_file.csv`, `smoke_parse_errors.csv`, `smoke_validation_errors.csv`, and `smoke_qc_summary.json` in the output directory.

<div id="tab:smoke">

| Metric                         |  Value |
|:-------------------------------|-------:|
| Smoke test passed              |   true |
| Parsed events                  |  4,053 |
| Pick rows                      | 59,895 |
| Rows with both P and S         | 30,089 |
| P-only rows                    | 14,865 |
| S-only rows                    | 14,941 |
| P pick count                   | 44,954 |
| S pick count                   | 45,030 |
| Rows with both P and S missing |      0 |

Smoke-test validation summary for 2025-06-01 through 2025-06-05, represented as the half-open five-day file starting 2025-06-01.

</div>

## Full and Regional Catalog Products

The final parsed catalog counts are listed in Table <a href="#tab:catalog_counts" data-reference-type="ref" data-reference="tab:catalog_counts">2</a>. The full parsed catalog contains 287,868 events and 4,054,829 pick rows. The Sanriku parser-stage subset contains 36,838 events and 672,005 pick rows. The canonical expert-processed relocation handoff contains 33,702 events and 637,812 picks. For the parser-stage regional subset, there are 549,176 non-missing P picks and 442,253 non-missing S picks. The regional catalog time span in UTC is 2025-05-31T15:09:02.360000Z to 2026-05-01T14:58:44.740000Z, consistent with conversion from a JST request window beginning on 2025-06-01 and ending before 2026-05-02.

<div id="tab:catalog_counts">

| Metric                         | Full parsed catalog | Sanriku regional subset |
|:-------------------------------|--------------------:|------------------------:|
| Events                         |             287,868 |                  36,838 |
| Pick rows                      |           4,054,829 |                 672,005 |
| Rows with both P and S         |           2,122,885 |                 319,424 |
| P-only rows                    |             956,246 |                 229,752 |
| S-only rows                    |             975,698 |                 122,829 |
| P pick count                   |           3,079,131 |                 549,176 |
| S pick count                   |           3,098,583 |                 442,253 |
| Rows with both P and S missing |                   0 |                       0 |

Validated full and Sanriku-regional catalog counts from `final_validation_summary.json`.

</div>

The regional coordinate ranges are exactly within the requested filter: latitude 38.500000 to 42.499833$`^{\circ}`$N and longitude 141.000500 to 144.500000$`^{\circ}`$E. Regional depths range from 0.00 to 149.24 km and magnitudes range from -0.5 to 7.7. These descriptive ranges are quality-control summaries of the parsed JMA source information; no relocation or downstream event matching was performed in this workflow.

## Parser Quality Control

Parser quality-control totals are shown in Table <a href="#tab:parser_qc" data-reference-type="ref" data-reference="tab:parser_qc">3</a>. The parser processed 4,931,813 non-empty lines, all of which were valid 96-byte records. The workflow closed 288,453 event blocks, matching the number of `J` headers and `E` terminators counted before exclusions. It then omitted 585 events and 4,303 station-pick records associated with skipped events, primarily malformed or far-field records lacking required local coordinates. These skips are tracked explicitly and are not counted as parser failures. The validation-critical counters—invalid record lengths, parse errors, orphan picks, unrecognized records, and unterminated event blocks—are all zero.

<div id="tab:parser_qc">

| Parser metric            |     Count |
|:-------------------------|----------:|
| Total non-empty lines    | 4,931,813 |
| Valid 96-byte records    | 4,931,813 |
| Invalid-length records   |         0 |
| `J` event-header records |   288,453 |
| Station-pick records     | 4,059,132 |
| `E` terminator records   |   288,453 |
| Auxiliary records        |   295,775 |
| Unrecognized records     |         0 |
| Orphan pick records      |         0 |
| Closed event blocks      |   288,453 |
| Skipped events           |       585 |
| Skipped pick records     |     4,303 |
| Unterminated events      |         0 |
| Parser errors            |         0 |

Fixed-width parser quality-control totals from `catalog_qc_summary.json` and `final_validation_summary.json`.

</div>

## Output Inventory and Traceability

Table <a href="#tab:outputs" data-reference-type="ref" data-reference="tab:outputs">[tab:outputs]</a> lists the principal products. The normalized CSV files are the primary structured outputs. The phase-file export is intentionally secondary and traceable: `phase_dat_traceability.csv` contains 708,843 trace rows, matching 36,838 regional event lines plus 672,005 regional pick lines. The station export contains 371 matched station rows; the station metadata audit contains 522 unique station-code/station-number pairs used by the regional picks, of which 151 lacked matched coordinates in the available reference station metadata and are listed in `station_metadata_missing.csv`.

<div class="longtable">

P0.25P0.15P0.52

  
Product & Size & Role  
Product & Size & Role  
<a href="<CASE_ROOT>/run/00_travel_time_download/exp_run/outputs/01_hinet_jma_arrivals_workflow/events_full.csv" class="uri"><CASE_ROOT>/run/00_travel_time_download/exp_run/outputs/01_hinet_jma_arrivals_workflow/events_full.csv</a> & 42,256,079 bytes & Full parsed event table.  
<a href="<CASE_ROOT>/run/00_travel_time_download/exp_run/outputs/01_hinet_jma_arrivals_workflow/picks_full.csv" class="uri"><CASE_ROOT>/run/00_travel_time_download/exp_run/outputs/01_hinet_jma_arrivals_workflow/picks_full.csv</a> & 480,969,262 bytes & Full parsed station-pick table.  
<a href="<CASE_ROOT>/run/00_travel_time_download/exp_run/outputs/01_hinet_jma_arrivals_workflow/events_regional.csv" class="uri"><CASE_ROOT>/run/00_travel_time_download/exp_run/outputs/01_hinet_jma_arrivals_workflow/events_regional.csv</a> & 5,360,942 bytes & Sanriku regional event table; also duplicated as `events.csv`.  
<a href="<CASE_ROOT>/run/00_travel_time_download/exp_run/outputs/01_hinet_jma_arrivals_workflow/picks_regional.csv" class="uri"><CASE_ROOT>/run/00_travel_time_download/exp_run/outputs/01_hinet_jma_arrivals_workflow/picks_regional.csv</a> & 78,890,170 bytes & Sanriku regional station-pick table; also duplicated as `picks.csv`.  
<a href="<CASE_ROOT>/run/00_travel_time_download/exp_run/outputs/01_hinet_jma_arrivals_workflow/phase.dat" class="uri"><CASE_ROOT>/run/00_travel_time_download/exp_run/outputs/01_hinet_jma_arrivals_workflow/phase.dat</a> & 45,923,345 bytes & Project-convention regional phase file.  
<a href="<CASE_ROOT>/run/00_travel_time_download/exp_run/outputs/01_hinet_jma_arrivals_workflow/phase_dat_traceability.csv" class="uri"><CASE_ROOT>/run/00_travel_time_download/exp_run/outputs/01_hinet_jma_arrivals_workflow/phase_dat_traceability.csv</a> & 52,731,927 bytes & Line/block traceability from `phase.dat` back to normalized event and pick rows.  
<a href="<CASE_ROOT>/run/00_travel_time_download/exp_run/outputs/01_hinet_jma_arrivals_workflow/station.sta" class="uri"><CASE_ROOT>/run/00_travel_time_download/exp_run/outputs/01_hinet_jma_arrivals_workflow/station.sta</a> & 15,968 bytes & Matched station metadata for regional picks.  
<a href="<CASE_ROOT>/run/00_travel_time_download/exp_run/outputs/01_hinet_jma_arrivals_workflow/station_metadata_audit.csv" class="uri"><CASE_ROOT>/run/00_travel_time_download/exp_run/outputs/01_hinet_jma_arrivals_workflow/station_metadata_audit.csv</a> & 19,018 bytes & Audit of station-code/station-number pairs and coordinate-match status.  
<a href="<CASE_ROOT>/run/00_travel_time_download/exp_run/outputs/01_hinet_jma_arrivals_workflow/final_validation_summary.json" class="uri"><CASE_ROOT>/run/00_travel_time_download/exp_run/outputs/01_hinet_jma_arrivals_workflow/final_validation_summary.json</a> & 1,598 bytes & Authoritative final validation summary.  
<a href="<CASE_ROOT>/run/00_travel_time_download/exp_run/outputs/01_hinet_jma_arrivals_workflow/product_inventory.csv" class="uri"><CASE_ROOT>/run/00_travel_time_download/exp_run/outputs/01_hinet_jma_arrivals_workflow/product_inventory.csv</a> & 6,147 bytes & Output inventory with file sizes and modification times.  

</div>

# Scientific Interpretation

The implemented workflow successfully converts raw JMA/Hi-net arrival-time measure files into a relational event–pick catalog and compatibility products for Sanriku. The strongest validation evidence is not the event count alone, but the complete evidence chain: non-empty raw inputs are enumerated in the manifest; every parsed non-empty line is a 96-byte fixed-width record; event headers and terminators are balanced; no orphan picks or unterminated event blocks remain; normalized timestamps are parseable as UTC; every pick row references an event; and the regional subset satisfies the requested latitude–longitude bounds.

The full catalog count of 287,868 events is a parsing-stage count after excluding records that lacked required local source information. The Sanriku count of 36,838 events is the locally filtered subset of this parsed catalog. This count should not be confused with any downstream manuscript count produced by later arrival matching, relocation-input filtering, or other catalog construction stages. The regional P/S distribution indicates a large number of usable arrivals: 549,176 P picks and 442,253 S picks, with no rows where both phases are missing. The presence of P-only and S-only rows is expected in station-pick records and is preserved explicitly using `-1` for the missing counterpart.

# Limitations and Caveats

1.  **Fresh network download was not exercised in the completed run.** The implementation includes the HinetPy download path, credential loading, retry/backoff, skip-existing behavior, and manifest writing. However, the completed execution reused 73 previously downloaded non-empty raw measure files and therefore did not validate live Hi-net service availability, account permissions, or network behavior at execution time.

2.  **Manifest differs from the planned five-day schedule because source reuse mode was used.** The workflow wrote a 67-row planned five-day schedule for the requested half-open interval, but the accepted raw input manifest contains 73 previously downloaded files, including month-boundary files. The manifest is the authoritative record for what was parsed in this completed run. All manifest spans are at most 5 days, and the final raw file covers 2026-05-01 with a one-day span.

3.  **Station metadata coverage is incomplete.** The regional picks use 522 unique station-code/station-number pairs. The station metadata audit matched 371 of them and left 151 unmatched in `station_metadata_missing.csv`. The event and pick CSV products remain complete, but `station.sta` contains only matched station metadata.

4.  **Skipped records are explicitly tracked.** The parser skipped 585 event headers and 4,303 pick records associated with events lacking required parseable source coordinates, notably far-field records. These exclusions are documented in parser QC totals and should be considered when comparing full raw JMA record counts to parsed local-source catalog counts.

5.  **Regional product is a source-parameter subset, not a relocated catalog.** Depths, magnitudes, regions, and origin times are parsed from the JMA measure source records. No hypocenter relocation, phase association refinement, or station correction was performed in this workflow.

6.  **Handoff status metadata was stale relative to final products.** The compact handoff JSON retained a `running` status snapshot, but the task analysis and the output directory contain completed validation products. This report relies on the final output artifacts, especially `final_validation_summary.json`, `catalog_qc_summary.json`, and the product inventory.

# Conclusion

The JMA/Hi-net arrival-time workflow was independently implemented and validated for the Sanriku study region. The parser satisfies the fixed-width 96-byte record requirement, preserves JST-to-UTC timestamp conversion, represents missing phase arrivals with `-1`, exports both full and regional normalized tables, and preserves the established comma-delimited project convention for `phase.dat`. The smoke test passed, and final validation passed with zero validation errors. The resulting Sanriku regional catalog contains 36,838 parsed events and 672,005 station-pick rows for the requested 2025-06-01 to 2026-05-01 coverage, with all regional event coordinates inside the specified bounds. The primary scientific products are the normalized CSV tables, while the compatibility phase and station files are traceable secondary exports.
