# Data Descriptions
## NIED Hi-net JMA login endpoint
**Source path**: `https://hinetwww11.bosai.go.jp/auth/?LANG=en`
### Summary
This directory contains a TRACE/SeismoAgent workflow scaffold for constructing a JMA/Hi-net catalog, plus previously parsed regional event, pick, station, and phase files for northeast Japan. The current run output directory for `00_catalog_download` is empty, and no cleaned ASPECT-ready `Snet_catalog_YYYYMMDD_YYYYMMDD.csv` file or distribution figure was found during profiling. Credentials are expected in `data/hinet_account/.env` with `HINET_USERNAME` and `HINET_PASSWORD` keys; values should be treated as sensitive.
### Detail
#### Folder Structure

- Root workflow directory:
  - `00_catalog_download.py`: launches the catalog-download workflow request through `seismoagent.runing.run_seismoagent`; it embeds the user request including Hi-net/JMA endpoints, target interval, Sanriku bounds, 7-day chunking, output schema, and raw-dir/debug requirements.
  - `00_travel_time_download.py`, `01_relocation_HypoDD.py`, `02_repeat_earthuake.py`: related downstream or companion workflow launch scripts.
- `data/hinet_account/.env`: credential file containing the keys `HINET_USERNAME` and `HINET_PASSWORD` only; do not print or commit values.
- `data/regional/`: parsed regional catalog products from an existing/previous workflow run.
- `data/stations/`: source station list text from JMA/Hi-net-style station metadata.
- `run/00_catalog_download/`: current workflow run directory with configuration, request text, logs, state, and an empty `exp_run/outputs/` directory.
- `backup-v1/`: older workflow scripts and many debug/run directories; useful mainly for reference, not the primary active run location.

#### Active Run Metadata

- `run/00_catalog_download/request.txt` mirrors the requested task:
  - login endpoint: `https://hinetwww11.bosai.go.jp/auth/?LANG=en`
  - catalog endpoint: `https://hinetwww11.bosai.go.jp/auth/JMA/jmalist.php`
  - requested exclusive interval: start `2025-06-01`, end `2026-05-02`, i.e. records through `2026-05-01`
  - Sanriku bounds: latitude `38.50–42.50`, longitude `141.00–144.50`
  - output CSV columns required by the future workflow: `datetime,lat,lon,dep,mag`
  - output filename pattern: `Snet_catalog_YYYYMMDD_YYYYMMDD.csv`
- `run/00_catalog_download/exp_run/outputs/` exists but currently contains no files.
- `run/00_catalog_download/config.yaml` is a TRACE/agent configuration file. It sets local container execution options and has `CONTAINER_DISABLE_NETWORK: true`, which future agents may need to account for when implementing an actual online Hi-net download.

#### Existing Regional Catalog Files

`data/regional/events.csv`

- Format: CSV with header.
- Shape: 29,896 rows × 8 columns.
- Columns:
  - `event_id` integer event identifier
  - `origin_time` ISO UTC timestamp string, e.g. `2025-09-30T16:09:25.360000Z`
  - `latitude`, `longitude` decimal degrees
  - `depth_km` depth in km
  - `magnitude` numeric magnitude; 2,853 missing values
  - `region` JMA region name string
  - `npicks` number of associated pick rows
- Observed metadata:
  - time span: `2025-09-30T16:09:25.360000Z` to `2026-05-01T14:58:44.740000Z`
  - latitude range: `38.5` to `42.499833`
  - longitude range: `141.001` to `144.499833`
  - depth range: `0.0` to `151.0` km
  - magnitude range among non-missing rows: `-0.5` to `7.7`
- Note: this is already spatially clipped to approximately the Sanriku bounds but does not cover the full requested start date of `2025-06-01`.

`data/regional/picks.csv`

- Format: CSV with header.
- Shape: 529,165 rows × 7 columns.
- Columns:
  - `event_id`
  - `station_code`
  - `p_pick_time`, `s_pick_time`: ISO UTC timestamp strings or `-1` sentinel for missing arrivals
  - `p_quality`, `s_quality`: pick quality labels; missing values occur where picks are absent
  - `weight`
- Observed metadata:
  - valid P picks: 437,472
  - valid S picks: 344,623
  - P-pick time span: `2025-09-30T16:09:32.740000Z` to `2026-05-01T14:59:06.040000Z`
  - S-pick time span: `2025-09-30T16:09:38.470000Z` to `2026-05-01T14:59:21.380000Z`

`data/regional/main_earthquake.csv`

- Format: small CSV with ASPECT-like column names plus an index label.
- Shape: 3 rows × 6 columns.
- Columns: `index,datetime,lat,lon,dep,mag`.
- Contains three highlighted events labelled `M1`, `M2`, `M3` with datetimes between `2025-11-09` and `2026-04-20`.

`data/regional/station.sta`

- Format: CSV with header.
- Shape: 371 rows × 6 columns.
- Columns:
  - `station_code`
  - `station_number`
  - `latitude`, `longitude`
  - `elevation_m`
  - `matched` boolean
- Observed coordinate coverage:
  - latitude range: `36.880833` to `44.118833`
  - longitude range: `139.245333` to `145.738833`

`data/regional/phase.dat` and `data/regional/phase_new.dat`

- Format: plain-text comma-separated phase/event blocks, not a single rectangular CSV table.
- Both contain 559,061 lines.
- Event header rows contain event origin information; pick rows follow until the next event header.
- `phase.dat` event-header example pattern:
  - `2025-09-30T16:09:25.360000Z,38.702667,142.256833,41.340,2.80,1`
- `phase_new.dat` event-header example pattern:
  - `20250930160925.36,38.702667,142.256833,41.340,2.80,1`
- Pick-row example pattern:
  - `N.313S,2025-09-30T16:09:32.740000Z,2025-09-30T16:09:38.470000Z,0.000e+00,1.00`
- Missing arrival times are represented by `-1`.

`data/regional/summary.txt`

- Text summary of a previous JMA measure parse:
  - `raw_events: 178623`
  - `kept_events: 29896`
  - `kept_station_rows: 529165`
  - `p_picks: 437472`
  - `s_picks: 344623`
  - `lat_range: 38.5000, 42.4998`
  - `lon_range: 141.0010, 144.4998`

#### Station Source File

`data/stations/station.txt`

- Format: fixed-width/plain-text station listing with Japanese text and station rows.
- Size: 2,550 lines.
- Header indicates columns like JMA code, station number, latitude, longitude, height, active dates, and seismograph information.
- Example station-row pattern:
  - `ABASH2  201  43 50.65  143 51.96   180          20000317 EMT ...`
- Text includes non-UTF-8 or mixed-encoding characters; read with encoding fallback such as `errors='replace'` if needed.

#### File Naming and Access Notes

- Existing parsed catalog files use names such as:
  - `data/regional/events.csv`
  - `data/regional/picks.csv`
  - `data/regional/phase.dat`
  - `data/regional/phase_new.dat`
- No current file matching `Snet_catalog_YYYYMMDD_YYYYMMDD.csv` was found under the active `run/00_catalog_download/exp_run/outputs/` directory.
- Future download code should load credentials from `data/hinet_account/.env`, preserve raw chunk responses in an optional raw directory, and write cleaned ASPECT-ready output with exactly the columns `datetime,lat,lon,dep,mag`.

------------------------------

## NIED Hi-net JMA catalog endpoint
**Source path**: `https://hinetwww11.bosai.go.jp/auth/JMA/jmalist.php`
### Summary
The relevant data source is the authenticated NIED Hi-net JMA unified hypocenter catalog endpoint, with local workflow scaffolding and previously parsed regional catalog files under the `catalog_construction_from_JMA` example directory. Existing local files include regional event, pick, station, and phase products, but the active `00_catalog_download` output directory currently contains no cleaned `Snet_catalog_YYYYMMDD_YYYYMMDD.csv` file or distribution figure.
### Detail
#### Catalog Endpoint and Workflow Context

- Primary catalog endpoint specified for future download workflow:
  - `https://hinetwww11.bosai.go.jp/auth/JMA/jmalist.php`
- Login endpoint referenced by the local request/workflow:
  - `https://hinetwww11.bosai.go.jp/auth/?LANG=en`
- Local workflow root:
  - `<CASE_ROOT>`
- Credential file:
  - `data/hinet_account/.env`
  - Contains keys `HINET_USERNAME` and `HINET_PASSWORD`; values should be treated as sensitive and not printed.

#### Directory Structure

- `00_catalog_download.py`
  - Python launcher for the catalog-download workflow request.
  - Embeds the task metadata: Hi-net/JMA endpoints, requested interval, Sanriku bounds, 7-day chunking, output filename pattern, and required CSV schema.
- `00_travel_time_download.py`, `01_relocation_HypoDD.py`, `02_repeat_earthuake.py`
  - Related workflow launch scripts for later or companion processing steps.
- `data/hinet_account/`
  - Contains `.env` credentials for Hi-net authentication.
- `data/regional/`
  - Contains previously parsed regional catalog, pick, phase, station, and summary files.
- `data/stations/`
  - Contains a source station listing text file.
- `run/00_catalog_download/`
  - Active run directory with configuration, request text, logs, trajectory/state files, and an empty output folder.
- `run/00_catalog_download/exp_run/outputs/`
  - Exists, but no current cleaned catalog CSV or figure was found.
- `backup-v1/`
  - Older scripts and debug/run directories; useful for reference only.

#### Active Run Files

- `run/00_catalog_download/request.txt`
  - Contains the full catalog-download task request.
  - Important request metadata for future agents:
    - Start date: `2025-06-01`
    - Exclusive end date: `2026-05-02`
    - Intended covered dates: `2025-06-01` through `2026-05-01`
    - Latitude bounds: `38.50` to `42.50`
    - Longitude bounds: `141.00` to `144.50`
    - Required cleaned CSV columns: `datetime,lat,lon,dep,mag`
    - Required filename pattern: `Snet_catalog_YYYYMMDD_YYYYMMDD.csv`
- `run/00_catalog_download/config.yaml`
  - TRACE/agent runtime configuration.
  - Notable setting: `CONTAINER_DISABLE_NETWORK: true`, which may affect any future online catalog-download implementation unless adjusted by the execution environment.

#### Existing Regional Event Catalog

`data/regional/events.csv`

- Format: CSV with header.
- Shape: 29,896 rows × 8 columns.
- Columns:
  - `event_id`: integer event identifier
  - `origin_time`: ISO UTC timestamp string
  - `latitude`: decimal degrees north
  - `longitude`: decimal degrees east
  - `depth_km`: event depth in km
  - `magnitude`: numeric magnitude; contains missing values
  - `region`: JMA region name string
  - `npicks`: number of associated pick rows
- Observed metadata:
  - Time range: `2025-09-30T16:09:25.360000Z` to `2026-05-01T14:58:44.740000Z`
  - Latitude range: `38.5` to `42.499833`
  - Longitude range: `141.001` to `144.499833`
  - Depth range: `0.0` to `151.0` km
  - Magnitude range among non-missing values: `-0.5` to `7.7`
  - Missing `magnitude` values: 2,853 rows
- Note: this file is already approximately clipped to the Sanriku spatial region, but it begins at `2025-09-30`, not the requested `2025-06-01`.

#### Existing Pick File

`data/regional/picks.csv`

- Format: CSV with header.
- Shape: 529,165 rows × 7 columns.
- Columns:
  - `event_id`
  - `station_code`
  - `p_pick_time`
  - `s_pick_time`
  - `p_quality`
  - `s_quality`
  - `weight`
- Time fields are ISO UTC strings where present; missing arrival times may be represented by `-1`.
- Observed metadata:
  - Valid P picks: 437,472
  - Valid S picks: 344,623
  - P-pick time range: `2025-09-30T16:09:32.740000Z` to `2026-05-01T14:59:06.040000Z`
  - S-pick time range: `2025-09-30T16:09:38.470000Z` to `2026-05-01T14:59:21.380000Z`

#### Existing ASPECT-like Main Event File

`data/regional/main_earthquake.csv`

- Format: small CSV with header.
- Shape: 3 rows × 6 columns.
- Columns:
  - `index`
  - `datetime`
  - `lat`
  - `lon`
  - `dep`
  - `mag`
- Contains three highlighted events labelled `M1`, `M2`, and `M3`.
- Datetime range: `2025-11-09 08:03:39.240` to `2026-04-20 07:52:58.060`.

#### Existing Station Files

`data/regional/station.sta`

- Format: CSV with header.
- Shape: 371 rows × 6 columns.
- Columns:
  - `station_code`
  - `station_number`
  - `latitude`
  - `longitude`
  - `elevation_m`
  - `matched`
- Observed coordinate coverage:
  - Latitude range: `36.880833` to `44.118833`
  - Longitude range: `139.245333` to `145.738833`

`data/stations/station.txt`

- Format: fixed-width/plain-text station listing.
- Size: 2,550 lines.
- Header indicates station metadata fields such as JMA code, station number, latitude, longitude, height, active dates, and seismograph information.
- Contains mixed or non-UTF-8 text; future readers should use an encoding fallback such as `errors='replace'`.

#### Existing Phase Files

`data/regional/phase.dat`

- Format: plain-text comma-separated event/pick block file, not a single rectangular CSV table.
- Size: 559,061 lines.
- Event header rows use ISO UTC origin time followed by event metadata.
- Example event-header pattern:
  - `2025-09-30T16:09:25.360000Z,38.702667,142.256833,41.340,2.80,1`
- Pick-row pattern:
  - `station_code,p_pick_time,s_pick_time,residual_or_placeholder,weight`

`data/regional/phase_new.dat`

- Format: similar block-structured phase file.
- Size: 559,061 lines.
- Event header rows use compact origin-time format.
- Example event-header pattern:
  - `20250930160925.36,38.702667,142.256833,41.340,2.80,1`
- Missing pick times may be represented by `-1`.

#### Parse Summary File

`data/regional/summary.txt`

- Plain-text summary from a previous JMA measure parse.
- Reported fields:
  - `raw_events: 178623`
  - `kept_events: 29896`
  - `kept_station_rows: 529165`
  - `p_picks: 437472`
  - `s_picks: 344623`
  - `lat_range: 38.5000, 42.4998`
  - `lon_range: 141.0010, 144.4998`

#### Output Availability

- No existing file matching the required cleaned catalog filename pattern `Snet_catalog_YYYYMMDD_YYYYMMDD.csv` was found in the active run output directory.
- No catalog distribution figure was found in the active run output directory.
- Future agents should therefore treat the endpoint plus `.env` credentials as the primary source for generating the required cleaned catalog and figure, while using existing `data/regional/` files only as reference examples of parsed schema and regional metadata.

------------------------------

## hinet_account_env
**Source path**: `<CASE_ROOT>/data/hinet_account/.env`
### Summary
The specified data source is a small Hi-net credential environment file used by the local JMA catalog-download workflow. It contains only the expected credential keys for authenticated access, while the broader workflow and reference regional catalog files are located under the surrounding `catalog_construction_from_JMA` directory.
### Detail
#### Credential File Metadata

- Credential file path:
  - `<CASE_ROOT>/data/hinet_account/.env`
- Format: plain-text dotenv file with one `KEY=VALUE` pair per line.
- Observed keys:
  - `HINET_USERNAME`
  - `HINET_PASSWORD`
- The file is intended for authenticated requests to the NIED Hi-net/JMA services.
- Values are sensitive and should not be printed, logged, or committed.
- Future workflow scripts should load this file first, while allowing command-line arguments to override the credentials if needed.

#### Related Workflow Location

- Parent workflow directory:
  - `<CASE_ROOT>`
- Main catalog workflow launcher:
  - `00_catalog_download.py`
- Active run directory:
  - `run/00_catalog_download/`
- Active output directory:
  - `run/00_catalog_download/exp_run/outputs/`
- At profiling time, the active output directory existed but no cleaned `Snet_catalog_YYYYMMDD_YYYYMMDD.csv` file or catalog distribution figure was found.

#### Endpoint Context for Future Agents

- Login endpoint to use with the credentials:
  - `https://hinetwww11.bosai.go.jp/auth/?LANG=en`
- Catalog endpoint:
  - `https://hinetwww11.bosai.go.jp/auth/JMA/jmalist.php`
- Authentication should be maintained with `requests.Session` in future implementation.

#### Request Metadata Stored in Workflow

The local workflow request specifies the following target catalog structure and constraints:

- Time interval:
  - Start date: `2025-06-01`
  - Exclusive end date: `2026-05-02`
  - Intended coverage: `2025-06-01` through `2026-05-01`
- Spatial bounds:
  - Latitude: `38.50` to `42.50` degrees N
  - Longitude: `141.00` to `144.50` degrees E
- Request chunking:
  - Chunks should be no more than 7 days.
  - Future workflow should record exact chunk boundaries and returned date ranges.
- Required cleaned CSV schema:
  - `datetime,lat,lon,dep,mag`
- Required filename pattern:
  - `Snet_catalog_YYYYMMDD_YYYYMMDD.csv`

#### Existing Reference Data Nearby

The surrounding directory contains previously parsed regional files that may help future agents understand expected schemas, but they are not a substitute for the requested full catalog download.

- `data/regional/events.csv`
  - CSV with 29,896 rows and columns: `event_id`, `origin_time`, `latitude`, `longitude`, `depth_km`, `magnitude`, `region`, `npicks`.
  - Observed time span: `2025-09-30T16:09:25.360000Z` to `2026-05-01T14:58:44.740000Z`.
  - Already approximately clipped to Sanriku bounds, but starts later than the requested `2025-06-01`.
- `data/regional/picks.csv`
  - CSV with 529,165 rows and columns: `event_id`, `station_code`, `p_pick_time`, `s_pick_time`, `p_quality`, `s_quality`, `weight`.
- `data/regional/main_earthquake.csv`
  - Small ASPECT-like CSV with columns: `index`, `datetime`, `lat`, `lon`, `dep`, `mag`.
- `data/regional/station.sta`
  - Station CSV with columns: `station_code`, `station_number`, `latitude`, `longitude`, `elevation_m`, `matched`.
- `data/regional/phase.dat` and `data/regional/phase_new.dat`
  - Block-structured text phase files with event headers followed by station pick rows.
- `data/stations/station.txt`
  - Fixed-width/plain-text station listing with mixed or non-UTF-8 text; read with encoding fallback such as `errors='replace'`.

#### Access Notes

- The `.env` file should be read as a simple dotenv file, e.g. by parsing non-comment `KEY=VALUE` lines or using a dotenv loader.
- Future agents should avoid echoing the credential values in shell output, logs, or exceptions.
- If implementing the online workflow, note that the local `run/00_catalog_download/config.yaml` includes `CONTAINER_DISABLE_NETWORK: true`, so the execution environment may need network access enabled before contacting the Hi-net endpoints.

------------------------------

