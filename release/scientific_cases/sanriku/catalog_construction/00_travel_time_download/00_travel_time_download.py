import os
import sys
sys.path.append("<REPO_ROOT>")
from seismoagent.runing import run_seismoagent

user_request = """
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
"""

if __name__ == "__main__":

    run_name = "00_travel_time_download"
    output_dir = "<CASE_ROOT>/run"
    
    run_seismoagent(
        request=user_request,
        run_name=run_name,
        output_dir=output_dir,
        disable_refinement=False,
        max_refinement_rounds=3,
        enable_trajectory=True,
        use_mineru_for_papers=False,
        resume=os.path.join(output_dir, run_name),
        resume_stage="report",
    )
