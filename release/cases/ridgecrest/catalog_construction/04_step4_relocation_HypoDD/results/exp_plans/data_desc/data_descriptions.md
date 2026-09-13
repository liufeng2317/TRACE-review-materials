# Data Descriptions
## 01_gamma_association_location_magnitude
**Source path**: `<CASE_ROOT>/catalog_construction/01_step3_association_Gamma/exp_run/outputs/01_gamma_association_location_magnitude`
### Summary
This directory contains Gamma association and location outputs for the Ridgecrest example, including the two user-relevant day files `phase_20190704.dat`, `phase_20190705.dat`, `catalog_20190704.dat`, and `catalog_20190705.dat`. For future HypoDD-style workflows, the key inputs are the phase files with `EVENT`/`STATION` blocks, the headerless daily catalog files with 5 location columns, and the separate station metadata file `station.sta` containing 47 stations with latitude, longitude, and elevation.
### Detail
#### Folder Structure
Primary source directory:
`<CASE_ROOT>/catalog_construction/01_step3_association_Gamma/exp_run/outputs/01_gamma_association_location_magnitude`

Relevant daily files for the requested 2019-07-04 to 2019-07-26 window:
- `phase_20190704.dat`
- `phase_20190705.dat`
- `catalog_20190704.dat`
- `catalog_20190705.dat`

Other files present in the same folder follow related processing/output patterns and may help trace provenance, but are not required as primary relocation inputs:
- daily CSVs such as `assigned_picks_YYYYMMDD.csv`, `assignments_YYYYMMDD.csv`, `events_YYYYMMDD.csv`, `events_final_YYYYMMDD.csv`, `paired_phases_YYYYMMDD.csv`
- combined summaries such as `all_events_combined.csv`, `all_paired_phases_combined.csv`, `pick_qc_summary.csv`, `validation_summary.csv`
- metadata/summary artifacts such as `region_summary.json`, `run_summary.json`, `stations_projected.csv`
- existing figures such as `association_example.png`, `event_locations.png`, `event_location_statistics.png`

Associated station metadata file referenced by the user:
`<CASE_ROOT>/catalog_construction/01_step1_data_preprocessing_for_phasepicking/exp_run/outputs/01_preprocess_ridgecrest_stationday_waveforms/station.sta`

#### File Naming Conventions
Daily files are date-partitioned by `YYYYMMDD`:
- `phase_YYYYMMDD.dat`: event + station phase associations
- `catalog_YYYYMMDD.dat`: daily location catalog
- related CSV intermediates use the same suffix pattern, e.g. `events_20190705.csv`

This makes it straightforward for future agents to select only the requested time window by filename rather than scanning all days.

#### Phase File Structure
Format: plain text, comma-separated, no global header.

Organization pattern:
- An `EVENT,...` line starts one event block.
- It is followed by one or more `STATION,...` lines representing picks/amplitudes associated with that event.

Observed `EVENT` record schema:
- `EVENT, event_origin_time, event_latitude, event_longitude, event_depth, event_magnitude`

Observed `STATION` record schema:
- `STATION, net.sta, p_pick_time, s_pick_time, s_amplitude`

Important content conventions:
- Times are already stored as ISO UTC strings with trailing `Z`, compatible with `obspy.UTCDateTime`, e.g. `2019-07-04T00:17:12.742000Z`
- Missing phase times are encoded as string `-1`
- Station identifier is stored as `NET.STA` (examples: `CI.WRC2`, `PB.B916`)
- The final station field is a numeric amplitude-like value

Examples from `phase_20190704.dat`:
- `EVENT,2019-07-04T00:17:12.742000Z,36.12685,-117.64984,5.25,2.12`
- `STATION,CI.WRC2,2019-07-04T00:17:16.318300Z,2019-07-04T00:17:19.308300Z,0.00551416759166698`
- `STATION,PB.B916,2019-07-04T00:17:14.698300Z,2019-07-04T00:17:16.068300Z,0.0022359348330476684`

Examples from `phase_20190705.dat` show the same schema, including missing values such as:
- `STATION,CI.CCC,-1,2019-07-05T00:00:27.898300Z,9.44268269841138e-08`
- `STATION,CI.CGO,2019-07-05T00:00:39.608300Z,-1,2.257371615738812e-09`

Per-file counts:
- `phase_20190704.dat`: 1,928 lines total; 275 `EVENT` records; 1,653 `STATION` records
- `phase_20190705.dat`: 29,731 lines total; 3,241 `EVENT` records; 26,490 `STATION` records

Implication for loaders:
- A parser should read sequentially, creating one event object per `EVENT` line and attaching subsequent `STATION` lines until the next `EVENT`
- Future agents should explicitly treat `-1` as missing pick time rather than a valid timestamp

#### Catalog File Structure
Format: plain text CSV without a header row.

Actual column order inferred from the user description and file inspection:
1. `event_origin_time`
2. `event_latitude`
3. `event_longitude`
4. `event_depth`
5. `event_magnitude`

Note on ingestion:
- If loaded with default `pandas.read_csv(...)`, the first row may be incorrectly interpreted as column names because there is no header.
- Safer pattern is to read with `header=None` and assign the 5 column names explicitly.

Observed metadata:
- `catalog_20190704.dat`: 275 rows
  - time range: `2019-07-04T00:17:12.742000Z` to `2019-07-04T23:58:47.865000Z`
  - latitude range: 34.9208 to 36.15491
  - longitude range: -118.57067 to -116.66343
  - depth range: 0.0 to 30.0
  - magnitude range: -1.14 to 3.94
- `catalog_20190705.dat`: 3,241 rows
  - time range: `2019-07-05T00:00:19.910000Z` to `2019-07-05T23:59:23.426000Z`
  - latitude range: 34.92538 to 36.30259
  - longitude range: -118.53661 to -117.10988
  - depth range: 0.0 to 30.0
  - magnitude range: -1.44 to 4.34

Example row pattern:
- `2019-07-04T00:17:12.742000Z,36.12685,-117.64984,5.25,2.12`

These files appear to correspond one-to-one with the event count in the same-day phase files.

#### Station Metadata File
Path:
`<CASE_ROOT>/catalog_construction/01_step1_data_preprocessing_for_phasepicking/exp_run/outputs/01_preprocess_ridgecrest_stationday_waveforms/station.sta`

Format: plain text CSV, one station per line, no header.

Observed column pattern:
1. `station_id` as `NET.STA`
2. `latitude`
3. `longitude`
4. `elevation_m`
5. `misc_value` (numeric extra field; meaning not inferred here)

Examples:
- `CI.CCA,35.152520,-118.016490,710.00,626886820.397744`
- `CI.CCC,35.524950,-117.364530,670.00,627368612.812223`
- `CI.CGO,36.550400,-117.802950,2795.00,629864666.666667`

Observed metadata:
- 32 station rows
- latitude range: 34.93439 to 36.5504
- longitude range: -118.55743 to -116.6697
- elevation range: 385.0 to 2795.0 m

For future agents, the first four columns are the key fields needed to define station geometry and compute a relocation region or padded latitude/longitude bounds.

#### Data Relationships Relevant to Relocation Preparation
- Daily `phase_YYYYMMDD.dat` files contain the event-wise observation structure needed to recover picks by station.
- Daily `catalog_YYYYMMDD.dat` files provide initial event locations and magnitudes for the same dates.
- `station.sta` provides station coordinates needed to build station tables and determine spatial extent.
- Time values across inspected files already use UTC ISO string format with `Z`, which can be passed directly into `obspy.UTCDateTime` without conversion to numeric timestamps.

#### Recommended Loading Notes for Future Agents
- Restrict filename selection to `20190704` through `20190725` for the requested full-window.
- Read catalog and station files as comma-separated, headerless text.
- Read phase files line-by-line rather than table-wise because they mix two record types (`EVENT` and `STATION`).
- Expect possible missing P or S picks represented by `-1`.
- Match station identifiers using the shared `NET.STA` format between `phase_*.dat` and `station.sta`.

#### Example Paths
- `<CASE_ROOT>/catalog_construction/01_step3_association_Gamma/exp_run/outputs/01_gamma_association_location_magnitude/phase_20190704.dat`
- `<CASE_ROOT>/catalog_construction/01_step3_association_Gamma/exp_run/outputs/01_gamma_association_location_magnitude/catalog_20190705.dat`
- `<CASE_ROOT>/catalog_construction/01_step1_data_preprocessing_for_phasepicking/exp_run/outputs/01_preprocess_ridgecrest_stationday_waveforms/station.sta`

------------------------------

## phase_YYYYMMDD.dat
**Source path**: `phase_YYYYMMDD.dat`
### Summary
The `phase_YYYYMMDD.dat` files are daily plain-text association files organized as repeated `EVENT` records followed by their corresponding `STATION` pick records. For the requested full-window Ridgecrest window, inspected files `phase_20190704.dat` and `phase_20190705.dat` store origin-time/location/magnitude per event and station-level P/S pick times plus an amplitude field, with timestamps already in ISO UTC `...Z` string format suitable for `obspy.UTCDateTime`.
### Detail
#### File Pattern and Context
Target file pattern:
- `phase_YYYYMMDD.dat`

Observed examples in the Ridgecrest Gamma output directory:
- `phase_20190704.dat`
- `phase_20190705.dat`

These files live under:
`<CASE_ROOT>/catalog_construction/01_step3_association_Gamma/exp_run/outputs/01_gamma_association_location_magnitude`

They are the primary daily phase-association files relevant for preparing relocation inputs over the requested 2019-07-04 to 2019-07-26 window.

#### File Format
- Plain text
- Comma-separated fields
- No header row
- Mixed record types within the same file

The file is not a flat rectangular CSV table. It is a sequential event-block format:
1. One `EVENT,...` line starts an event block.
2. The following one or more `STATION,...` lines belong to that event.
3. The next `EVENT,...` line starts the next block.

Because of this structure, future agents should parse line-by-line rather than loading directly as a single uniform table.

#### Record Types
`EVENT` line schema:
- `EVENT, event_origin_time, event_latitude, event_longitude, event_depth, event_magnitude`

`STATION` line schema:
- `STATION, net.sta, p_pick_time, s_pick_time, s_amplitude`

Observed example:
- `EVENT,2019-07-04T17:48:57.839000Z,35.5988,-117.5883,12.52,3.76`
- `STATION,CI.CCC,2019-07-04T17:49:02.398300Z,2019-07-04T17:49:05.638300Z,16823.96728514338`
- `STATION,CI.DTP,-1,2019-07-04T17:49:10.888300Z,1942.8700799410976`

#### Time and Missing-Value Conventions
- Event origin times and pick times are stored as ISO-formatted UTC strings ending with `Z`
- These strings are directly compatible with `obspy.UTCDateTime`
- Missing P or S picks are encoded as the literal string `-1`
- Future agents should preserve the string timestamps until explicitly converting with `obspy.UTCDateTime`; they should not assume numeric timestamps are present

Examples of missing pick patterns seen in the data:
- missing P, present S: `STATION,CI.CCC,-1,2019-07-05T00:00:27.898300Z,...`
- present P, missing S: `STATION,CI.CGO,2019-07-05T00:00:39.608300Z,-1,...`

#### Station Identifier Convention
- Station identifiers appear in `NET.STA` form
- Examples: `CI.WRC2`, `PB.B916`, `CI.CLC`

This naming convention matches the station metadata file format used elsewhere in the workflow and can be used for station joins.

#### Observed Metadata for the Requested Time Window
Inspected files:
- `phase_20190704.dat`
- `phase_20190705.dat`

`phase_20190704.dat`
- total lines: 1,928
- `EVENT` records: 275
- `STATION` records: 1,653
- average associated station records per event: about 6.0
- first observed event time: `2019-07-04T00:17:12.742000Z`

`phase_20190705.dat`
- total lines: 29,731
- `EVENT` records: 3,241
- `STATION` records: 26,490
- average associated station records per event: about 8.2
- first observed event time: `2019-07-05T00:00:19.910000Z`

These counts indicate a much larger event volume on 2019-07-05 than on 2019-07-04.

#### Example Content Preview
From `phase_20190704.dat`:
- `EVENT,2019-07-04T00:17:12.742000Z,36.12685,-117.64984,5.25,2.12`
- `STATION,CI.WRC2,2019-07-04T00:17:16.318300Z,2019-07-04T00:17:19.308300Z,0.00551416759166698`
- `STATION,PB.B916,2019-07-04T00:17:14.698300Z,2019-07-04T00:17:16.068300Z,0.0022359348330476684`
- `STATION,PB.B918,2019-07-04T00:17:16.808300Z,2019-07-04T00:17:19.708300Z,0.003712603967668397`
- `EVENT,2019-07-04T00:46:47.562000Z,36.09603,-117.84426,12.56,2.82`
- `STATION,CI.WRC2,2019-07-04T00:46:52.388300Z,-1,0.009343836899530292`

From `phase_20190705.dat`:
- `EVENT,2019-07-05T00:00:19.910000Z,35.60208,-117.58459,8.18,-0.99`
- `STATION,CI.CCA,2019-07-05T00:00:30.928300Z,2019-07-05T00:00:39.058300Z,2.1194544628898722e-08`
- `STATION,CI.CCC,-1,2019-07-05T00:00:27.898300Z,9.44268269841138e-08`
- `STATION,CI.CGO,2019-07-05T00:00:39.608300Z,-1,2.257371615738812e-09`
- `STATION,CI.CLC,2019-07-05T00:00:24.118300Z,2019-07-05T00:00:27.268300Z,6.274618285838143e-09`
- `STATION,CI.DTP,2019-07-05T00:00:27.518300Z,2019-07-05T00:00:33.038300Z,5.837376861831944e-09`

#### Fields Most Relevant for Future Relocation Workflows
From each `EVENT` line:
- `event_origin_time`: initial event time string
- `event_latitude`
- `event_longitude`
- `event_depth`
- `event_magnitude`

From each `STATION` line:
- `net.sta`: station key for linking to station metadata
- `p_pick_time`
- `s_pick_time`
- `s_amplitude`

For relocation-oriented preprocessing, the essential relationships are:
- one event block per candidate event
- multiple station observations per event
- station codes link to external station coordinates
- timestamps are already in UTC text form

#### Parsing Notes for Future Agents
Recommended read strategy:
- Iterate through the file line by line
- When a line begins with `EVENT,`, start a new event object
- Append subsequent `STATION,` lines to that event until the next `EVENT,`
- Convert time strings to `obspy.UTCDateTime` only after checking for `-1`

Potential edge cases to handle:
- events with sparse station coverage
- missing P or S phases represented by `-1`
- scientific notation in amplitude values
- negative magnitudes in some events

#### Example Path
- `<CASE_ROOT>/catalog_construction/01_step3_association_Gamma/exp_run/outputs/01_gamma_association_location_magnitude/phase_20190704.dat`
- `<CASE_ROOT>/catalog_construction/01_step3_association_Gamma/exp_run/outputs/01_gamma_association_location_magnitude/phase_20190705.dat`

------------------------------

## catalog_YYYYMMDD.dat
**Source path**: `catalog_YYYYMMDD.dat`
### Summary
The `catalog_YYYYMMDD.dat` files are daily headerless CSV catalogs containing one event per row with origin time, latitude, longitude, depth, and magnitude. For the requested full-window Ridgecrest window, inspected files `catalog_20190704.dat` and `catalog_20190705.dat` contain 275 and 3,241 events respectively, with origin times already stored as ISO UTC `...Z` strings suitable for `obspy.UTCDateTime`.
### Detail
#### File Pattern and Context
Target file pattern:
- `catalog_YYYYMMDD.dat`

Observed examples in the Ridgecrest Gamma output directory:
- `catalog_20190704.dat`
- `catalog_20190705.dat`

Directory containing these files:
`<CASE_ROOT>/catalog_construction/01_step3_association_Gamma/exp_run/outputs/01_gamma_association_location_magnitude`

These files provide the daily event location catalog corresponding to the same dates as the phase-association files.

#### File Format
- Plain text CSV
- Comma-separated
- No header row in the file
- One event per line

Important loading note:
- Because there is no header row, a default CSV reader may incorrectly interpret the first event row as column names.
- Future agents should load with explicit column names and `header=None`.

#### Column Schema
Observed/inferred column order:
1. `event_origin_time`
2. `event_latitude`
3. `event_longitude`
4. `event_depth`
5. `event_magnitude`

Example row:
- `2019-07-04T00:17:12.742000Z,36.12685,-117.64984,5.25,2.12`

#### Time Format
- `event_origin_time` is stored as an ISO-formatted UTC string ending with `Z`
- This format is directly compatible with `obspy.UTCDateTime`
- No numeric Unix timestamps are present or needed

Examples:
- `2019-07-04T00:17:12.742000Z`
- `2019-07-05T23:59:23.426000Z`

#### Observed Metadata for Requested Dates
Inspected files:
- `catalog_20190704.dat`
- `catalog_20190705.dat`

`catalog_20190704.dat`
- rows/events: 275
- time range: `2019-07-04T00:17:12.742000Z` to `2019-07-04T23:58:47.865000Z`
- latitude range: 34.9208 to 36.15491
- longitude range: -118.57067 to -116.66343
- depth range: 0.0 to 30.0
- magnitude range: -1.14 to 3.94

`catalog_20190705.dat`
- rows/events: 3,241
- time range: `2019-07-05T00:00:19.910000Z` to `2019-07-05T23:59:23.426000Z`
- latitude range: 34.92538 to 36.30259
- longitude range: -118.53661 to -117.10988
- depth range: 0.0 to 30.0
- magnitude range: -1.44 to 4.34

#### Example Content Preview
From `catalog_20190704.dat`:
- `2019-07-04T00:17:12.742000Z,36.12685,-117.64984,5.25,2.12`
- `2019-07-04T00:46:47.562000Z,36.09603,-117.84426,12.56,2.82`
- `2019-07-04T00:55:32.531000Z,35.36640,-117.80988,9.25,3.09`
- `2019-07-04T00:56:37.679000Z,36.08232,-117.87765,2.57,3.03`

From `catalog_20190705.dat`:
- `2019-07-05T00:00:19.910000Z,35.60208,-117.58459,8.18,-0.99`
- `2019-07-05T00:00:23.641000Z,35.60156,-117.55804,30.00,-1.11`
- `2019-07-05T00:01:01.698000Z,35.68467,-117.50098,8.98,-0.91`
- `2019-07-05T00:01:06.917000Z,35.83689,-117.45930,2.41,-1.08`

#### Relationship to Other Files
- Each `catalog_YYYYMMDD.dat` file corresponds to the same-date `phase_YYYYMMDD.dat` file in the same directory.
- The event counts in the inspected catalog files match the number of `EVENT` blocks observed in the matching phase files:
  - 2019-07-04: 275 events
  - 2019-07-05: 3,241 events
- This suggests these catalog files are the event-level summary representation of the daily association/location results.

#### Fields Most Relevant for Future Relocation Workflows
Most useful columns for downstream relocation preparation:
- `event_origin_time`: initial origin time
- `event_latitude`: initial latitude
- `event_longitude`: initial longitude
- `event_depth`: initial depth
- `event_magnitude`: event size descriptor

These files are especially useful as the initial event catalog for comparison with relocated results and for basic event count and spatial-distribution summaries.

#### Parsing Notes for Future Agents
Recommended loading pattern in pandas:
- read as CSV with `header=None`
- assign column names explicitly: `event_origin_time`, `event_latitude`, `event_longitude`, `event_depth`, `event_magnitude`

Data-type expectations:
- `event_origin_time`: string, convertible to `obspy.UTCDateTime`
- `event_latitude`, `event_longitude`, `event_depth`, `event_magnitude`: numeric

Potential caveats:
- negative magnitudes are present
- depth values include boundary values such as `0.0` and `30.0`
- there is no explicit event ID column in this file format

#### Example Paths
- `<CASE_ROOT>/catalog_construction/01_step3_association_Gamma/exp_run/outputs/01_gamma_association_location_magnitude/catalog_20190704.dat`
- `<CASE_ROOT>/catalog_construction/01_step3_association_Gamma/exp_run/outputs/01_gamma_association_location_magnitude/catalog_20190705.dat`

------------------------------

## station.sta
**Source path**: `<CASE_ROOT>/catalog_construction/01_step1_data_preprocessing_for_phasepicking/exp_run/outputs/01_preprocess_ridgecrest_stationday_waveforms/station.sta`
### Summary
The `station.sta` file is a headerless station metadata table with one row per station, storing station code, latitude, longitude, elevation, and one additional numeric field. It contains 47 stations, and the latitude/longitude span is sufficient for future agents to derive relocation bounds with padding, while station IDs match the `NET.STA` format used in the phase files.
### Detail
#### File Structure
Path:
`<CASE_ROOT>/catalog_construction/01_step1_data_preprocessing_for_phasepicking/exp_run/outputs/01_preprocess_ridgecrest_stationday_waveforms/station.sta`

Format characteristics:
- Plain text
- Comma-separated
- No header row
- One station per line

Observed row pattern:
- `station_id, latitude, longitude, elevation_m, misc_value`

This file is a simple station lookup table rather than a nested or block-structured format.

#### Column Schema
Observed/inferred columns:
1. `station_id`
2. `latitude`
3. `longitude`
4. `elevation_m`
5. `misc_value`

Notes:
- `station_id` uses the same `NET.STA` convention seen in the phase files, e.g. `CI.CCA`, `CI.CCC`
- The first four columns are the key metadata needed for station geometry
- The fifth numeric column is present for all rows but its semantic meaning is not inferred here; future agents should preserve it if round-tripping the file, but it is not required for basic station-coordinate loading

#### Example Rows
First lines observed:
- `CI.CCA,35.152520,-118.016490,710.00,626886820.397744`
- `CI.CCC,35.524950,-117.364530,670.00,627368612.812223`
- `CI.CGO,36.550400,-117.802950,2795.00,629864666.666667`
- `CI.CLC,35.815740,-117.597510,775.00,627369000.000000`
- `CI.CWC,36.439047,-118.080495,1569.50,629865000.000000`

#### Basic Metadata
Observed file-level metadata:
- number of station rows: 32
- station ID format: `NET.STA`
- latitude range: 34.93439 to 36.5504
- longitude range: -118.55743 to -116.6697
- elevation range: 385.0 to 2795.0 meters

These ranges are directly relevant for future agents that need to define study-region bounds from station coverage and add padding.

#### Relationship to Other Files
- Station identifiers in this file match the station codes used in `phase_YYYYMMDD.dat` `STATION` records.
- This file provides the station coordinate metadata needed to join phase observations with physical station locations.
- It is the natural source for computing station-based longitude and latitude extents for downstream workflows.

#### Loading Notes for Future Agents
Recommended ingestion pattern:
- Read as CSV with `header=None`
- Assign explicit column names such as:
  - `station_id`
  - `latitude`
  - `longitude`
  - `elevation_m`
  - `misc_value`

Type expectations:
- `station_id`: string
- `latitude`, `longitude`, `elevation_m`, `misc_value`: numeric

Potential caveat:
- Do not read with whitespace splitting; the file is comma-delimited

#### Fields Most Relevant for Relocation Preparation
Most important columns for future scripts:
- `station_id`: joins to `phase_YYYYMMDD.dat`
- `latitude`
- `longitude`
- `elevation_m`

For region setup, the observed station span implies approximate raw bounds before any user-requested padding:
- latitude: 34.93439 to 36.5504
- longitude: -118.55743 to -116.6697

#### Example Usage Context
A future agent can use this file to:
- map `NET.STA` codes from phase records to coordinates
- compute station coverage limits
- derive padded `lat_range` and `lon_range`
- build station tables required by relocation preprocessing

#### Example Path
- `<CASE_ROOT>/catalog_construction/01_step1_data_preprocessing_for_phasepicking/exp_run/outputs/01_preprocess_ridgecrest_stationday_waveforms/station.sta`

------------------------------

