# Data Descriptions
## magnitude_wood_anderson
**Source path**: `<CASE_ROOT>/catalog_construction/01_step1_data_preprocessing_for_phasepicking/exp_run/outputs/01_preprocess_ridgecrest_stationday_waveforms/magnitude_wood_anderson`
### Summary
This run directory contains the key inputs needed for later GAMMA-based association and location over 2019-07-04 to 2019-07-05: daily PhaseNet pick CSVs, a station metadata table, and daily per-station Wood–Anderson MiniSEED waveform files for magnitude work. The data are already organized by day and station, with consistent naming that makes it straightforward to iterate by date, join picks to stations via `station_id`, and load 24-hour waveform records for amplitude extraction.
### Detail
#### Relevant Data Sources

The user-relevant inputs are located under the run directory:

- **Base run directory**: `<CASE_ROOT>/catalog_construction/run`
- **Processed waveform directory**: `<CASE_ROOT>/catalog_construction/01_step1_data_preprocessing_for_phasepicking/exp_run/outputs/01_preprocess_ridgecrest_stationday_waveforms/magnitude_wood_anderson`
- **PhaseNet picks directory**: `<CASE_ROOT>/catalog_construction/01_step2_phase_picking_PhaseNet/exp_run/outputs/01_phasenet_phase_picking`
- **Station metadata file**: `<CASE_ROOT>/catalog_construction/01_step1_data_preprocessing_for_phasepicking/exp_run/outputs/01_preprocess_ridgecrest_stationday_waveforms/station.sta`

#### Folder Structure

Relevant structure for future agents:

- `01_step1_data_preprocessing_for_phasepicking/exp_run/outputs/01_preprocess_ridgecrest_stationday_waveforms/`
  - `station.sta`
  - `magnitude_wood_anderson/`
    - `20190704/`
    - `20190705/`
- `01_step2_phase_picking_PhaseNet/exp_run/outputs/01_phasenet_phase_picking/`
  - `picks_20190704.csv`
  - `picks_20190705.csv`
  - `manifest.json`
  - `failures.json`
  - `run_summary.json`
  - `diagnostic_case_metadata.json`
  - `phasenet_pick_example.png`
  - `temp/`

Only the daily pick CSVs, `station.sta`, and the `magnitude_wood_anderson/YYYYMMDD/*.mseed` files appear directly relevant to the requested later workflow.

#### Daily Processed Waveforms for Magnitude

Directory pattern:

- `.../magnitude_wood_anderson/YYYYMMDD/{network}.{station}.{start}Z.{end}Z.mseed`

Observed day folders:

- `20190704`
- `20190705`

Observed file counts:

- `20190704`: **27** MiniSEED files
- `20190705`: **31** MiniSEED files

Example file names:

- `CI.CCA.20190704T000000Z.20190705T000000Z.mseed`
- `CI.CCC.20190704T000000Z.20190705T000000Z.mseed`
- `CI.CGO.20190704T000000Z.20190705T000000Z.mseed`
- `NN.GWY.20190704T000000Z.20190705T000000Z.mseed`
- `PB.B916.20190704T000000Z.20190705T000000Z.mseed`

Naming convention implies:

- **network**: first token, e.g. `CI`, `NN`, `PB`
- **station**: second token, e.g. `CCA`, `CCC`, `GWY`, `B916`
- **time span**: one full UTC day, encoded in filename as `YYYYMMDDTHHMMSSZ`

MiniSEED metadata from an inspected example:

- File: `CI.CCA.20190704T000000Z.20190705T000000Z.mseed`
- Contains **3 traces**:
  - `CI.CCA..HHE`
  - `CI.CCA..HHN`
  - `CI.CCA..HHZ`
- Trace timing:
  - start: `2019-07-04T00:00:00.008300Z`
  - end: `2019-07-04T23:59:59.998300Z`
- Sampling rate: **100.0 Hz**
- Samples per trace: **8,640,000**

Implications for loading:

- Each file is a single-station, full-day, 3-component waveform package.
- Trace IDs use `NET.STA..CHAN` form.
- For magnitude/amplitude workflows, the station key is compatible with pick `station_id` values such as `CI.CLC` or `NN.GWY`.

#### PhaseNet Picks CSVs

Relevant files present:

- `picks_20190704.csv`
- `picks_20190705.csv`

Observed shapes:

- `picks_20190704.csv`: **45,089 rows × 5 columns**
- `picks_20190705.csv`: **154,317 rows × 5 columns**

Columns:

- `station_id`
- `phase_time`
- `phase_score`
- `phase_amplitude`
- `phase_type`

Example records from `picks_20190704.csv`:

- `CI.CLC, 2019-07-04T00:00:02.328300, 0.344460, 0.000256, P`
- `CI.HAR, 2019-07-04T00:00:03.408300, 0.364403, 0.011767, P`
- `CI.TEH, 2019-07-04T00:00:20.128300, 0.361131, 0.014412, P`

Example records from `picks_20190705.csv`:

- `CI.WMF, 2019-07-05T00:00:01.308300, 0.447313, 0.000062, P`
- `NN.GWY, 2019-07-05T00:00:01.598300, 0.443959, 0.000131, P`
- `CI.CGO, 2019-07-05T00:00:01.798300, 0.300120, 0.000009, P`

Missingness check on inspected files:

- No null values were found in any of the five columns for the two daily CSVs.

Field interpretation useful for later agents:

- `station_id`: station join key in `NET.STA` format
- `phase_time`: ISO-like UTC timestamp string; note sampled examples do **not** include trailing `Z`, so agents should normalize explicitly if downstream tools require strict UTC formatting
- `phase_score`: picker confidence/probability-like score
- `phase_amplitude`: pick-associated amplitude value from PhaseNet output
- `phase_type`: phase label, observed values include at least `P` and likely `S`

#### Station Metadata File

File:

- `.../station.sta`

Observed size:

- **32 lines** (approximately 47 stations)

File format:

- Plain text, **comma-separated** records
- No header line observed

Example lines:

- `CI.CCA,35.152520,-118.016490,710.00,626886820.397744`
- `CI.CCC,35.524950,-117.364530,670.00,627368612.812223`
- `CI.CGO,36.550400,-117.802950,2795.00,629864666.666667`
- `CI.CLC,35.815740,-117.597510,775.00,627369000.000000`
- `CI.CWC,36.439047,-118.080495,1569.50,629865000.000000`

Likely field order based on values:

1. `station_id` (`NET.STA`)
2. `latitude`
3. `longitude`
4. `elevation_m`
5. an additional numeric field (likely internal metadata or projected/auxiliary value; not self-documented from inspection alone)

Practical note:

- The first four fields are directly usable for association/location preprocessing.
- Because the file lacks a header, downstream loaders should assign column names manually.

#### Naming and Join Keys

Common join pattern across files:

- Picks use `station_id` such as `CI.CLC`
- Station metadata first field uses the same `NET.STA` key
- Waveform filenames encode the same network and station as `{network}.{station}`

Recommended path patterns for future agents:

- Picks for a day: `.../01_phasenet_phase_picking/picks_YYYYMMDD.csv`
- Waveforms for a day: `.../magnitude_wood_anderson/YYYYMMDD/*.mseed`
- Station metadata: `.../station.sta`

#### Date Coverage Relevant to Request

Observed explicit coverage in the inspected inputs:

- `2019-07-04` → daily pick file and waveform subdirectory present
- `2019-07-05` → daily pick file and waveform subdirectory present

This matches the note in the request to process only the explicitly defined 22-day range from `2019-07-04` to `2019-07-26`, i.e. the 22 daily windows `20190704` through `20190725`.

#### Loading Notes for Future Coding Agents

- Use `pandas.read_csv()` for `picks_YYYYMMDD.csv`.
- Use `pandas.read_csv(..., header=None)` with comma splitting for `station.sta`, then assign column names explicitly.
- Use `obspy.read(..., headonly=True)` for quick MiniSEED inspection and full `read()` for waveform extraction.
- MiniSEED files are day-long and large enough that station/day selective loading is preferable to bulk loading all files at once.
- Timestamp normalization may be needed because pick CSV `phase_time` values are string timestamps without an observed trailing `Z`, while waveform headers are explicit UTC and later outputs are expected in `obspy.UTCDateTime` style.

------------------------------

## 01_phasenet_phase_picking
**Source path**: `<CASE_ROOT>/catalog_construction/01_step2_phase_picking_PhaseNet/exp_run/outputs/01_phasenet_phase_picking`
### Summary
This PhaseNet output directory contains daily pick tables for the Ridgecrest workflow, with one CSV per day for the requested time window (`the daily `picks_YYYYMMDD.csv` files for the full window`). The key metadata for later association are the station identifier, phase timestamp, phase type, confidence score, and pick amplitude; auxiliary JSON/PNG files are present but are secondary to the daily CSVs.
### Detail
#### Folder Structure

Observed contents of the PhaseNet output directory:

- `picks_20190704.csv`
- `picks_20190705.csv`
- `manifest.json`
- `failures.json`
- `run_summary.json`
- `diagnostic_case_metadata.json`
- `phasenet_pick_example.png`
- `temp/`

For future agents focused on association/location, the primary inputs are the daily CSV files matching the pattern:

- `picks_YYYYMMDD.csv`

Example paths:

- `<CASE_ROOT>/catalog_construction/01_step2_phase_picking_PhaseNet/exp_run/outputs/01_phasenet_phase_picking/picks_20190704.csv`
- `<CASE_ROOT>/catalog_construction/01_step2_phase_picking_PhaseNet/exp_run/outputs/01_phasenet_phase_picking/picks_20190705.csv`

#### Pick File Organization

There is one pick CSV per UTC day. Observed coverage relevant to the request:

- `20190704`
- `20190705`

This matches the 22-day processing window implied by the request (`2019-07-04` to `2019-07-26`, i.e. daily files for 2019-07-04 through 2019-07-25).

#### CSV Schema

Both inspected daily CSVs have the same 5-column schema:

- `station_id`
- `phase_time`
- `phase_score`
- `phase_amplitude`
- `phase_type`

Observed shapes:

- `picks_20190704.csv`: **45,089 rows × 5 columns**
- `picks_20190705.csv`: **154,317 rows × 5 columns**

Missing values in inspected files:

- No nulls observed in any of the five columns for either day.

#### Field Meanings Relevant to Later Agents

- **`station_id`**
  - Station key in `NET.STA` format.
  - Example values: `CI.CLC`, `CI.HAR`, `CI.TEH`, `CI.WMF`, `NN.GWY`, `CI.CGO`
  - This is the main join key to station metadata and station-based waveform files.

- **`phase_time`**
  - Pick timestamp stored as a string in ISO-like UTC format.
  - Example values:
    - `2019-07-04T00:00:02.328300`
    - `2019-07-05T00:00:01.598300`
  - Important note: observed values do **not** include a trailing `Z`, so downstream code should normalize explicitly if strict `obspy.UTCDateTime` formatting is required.

- **`phase_score`**
  - Numeric confidence/probability-like score for each pick.
  - Example values: `0.344460`, `0.364403`, `0.447313`

- **`phase_amplitude`**
  - Numeric amplitude attached to the pick.
  - Example values range from very small positive values such as `0.000009`, `0.000062`, `0.011767`.
  - This field is relevant for later workflows that need a fallback amplitude when an S-pick-specific amplitude is absent.

- **`phase_type`**
  - Phase label for the pick.
  - Observed examples show `P`; the schema is clearly intended for both `P` and `S` picks for later association.

#### Example Rows

From `picks_20190704.csv`:

- `CI.CLC, 2019-07-04T00:00:02.328300, 0.344460, 0.000256, P`
- `CI.HAR, 2019-07-04T00:00:03.408300, 0.364403, 0.011767, P`
- `CI.TEH, 2019-07-04T00:00:20.128300, 0.361131, 0.014412, P`

From `picks_20190705.csv`:

- `CI.WMF, 2019-07-05T00:00:01.308300, 0.447313, 0.000062, P`
- `NN.GWY, 2019-07-05T00:00:01.598300, 0.443959, 0.000131, P`
- `CI.CGO, 2019-07-05T00:00:01.798300, 0.300120, 0.000009, P`

#### Naming Conventions and Access Pattern

Filename pattern:

- `picks_YYYYMMDD.csv`

Typical day-wise access pattern for future agents:

1. Choose explicit date(s), e.g. `20190704` through `20190725`
2. Load `picks_YYYYMMDD.csv`
3. Parse `phase_time` as UTC timestamps
4. Use `station_id` to join with station metadata (`station.sta`) and map to waveform files for the same day

#### Auxiliary Files

The following additional files are present but appear secondary for the core pick-loading workflow:

- `manifest.json`
- `failures.json`
- `run_summary.json`
- `diagnostic_case_metadata.json`
- `phasenet_pick_example.png`
- `temp/`

These likely contain run bookkeeping, diagnostics, or examples rather than the authoritative pick records. Future agents should treat the daily `picks_YYYYMMDD.csv` files as the main source for association inputs.

#### Practical Loading Notes

- `pandas.read_csv()` is sufficient to load the daily pick tables.
- Keep `phase_time` as string until explicit conversion to `obspy.UTCDateTime` or pandas datetime objects.
- Since the tables are already partitioned by day, per-day processing is natural and avoids mixing dates.
- The `station_id` field is already compact and suitable for direct matching against station metadata and station-specific waveform filenames.

------------------------------

## picks_YYYYMMDD.csv
**Source path**: `picks_YYYYMMDD.csv`
### Summary
The `picks_YYYYMMDD.csv` files are daily PhaseNet pick tables containing the core fields needed for later seismic phase association: station identifier, pick time, phase type, confidence score, and pick amplitude. In the inspected Ridgecrest run, the available daily files are `the daily `picks_YYYYMMDD.csv` files for the full window`, both with the same 5-column schema and no missing values in those columns.
### Detail
#### File Pattern

These pick files follow the daily naming convention:

- `picks_YYYYMMDD.csv`

In the inspected dataset, observed examples are:

- `picks_20190704.csv`
- `picks_20190705.csv`

This pattern is intended for day-by-day loading and processing.

#### File Format

- Format: CSV text table
- Header row: present
- Rows: one pick per row
- Time organization: one file per UTC day

#### Column Schema

Inspected files share the same 5 columns:

- `station_id`
- `phase_time`
- `phase_score`
- `phase_amplitude`
- `phase_type`

#### Column Meanings Relevant to Later Agents

- **`station_id`**
  - Station identifier in `NET.STA` format.
  - Example values: `CI.CLC`, `CI.HAR`, `CI.TEH`, `CI.WMF`, `NN.GWY`, `CI.CGO`
  - This is the key field for joining with station metadata and matching waveform files.

- **`phase_time`**
  - Pick time stored as an ISO-like timestamp string.
  - Example values:
    - `2019-07-04T00:00:02.328300`
    - `2019-07-05T00:00:01.598300`
  - Important note for downstream use: inspected values do not include a trailing `Z`, so future agents may need to normalize them before converting to `obspy.UTCDateTime`.

- **`phase_score`**
  - Numeric confidence-like score for the pick.
  - Example values: `0.344460`, `0.364403`, `0.447313`

- **`phase_amplitude`**
  - Numeric amplitude attached to the pick record.
  - Example values: `0.000256`, `0.011767`, `0.000062`, `0.000009`
  - This field is directly relevant for workflows that need pick-level amplitude metadata.

- **`phase_type`**
  - Phase label for the pick.
  - Observed values in preview rows: `P`
  - The schema is designed for P/S association workflows, so future agents should expect `P` and `S` values.

#### Observed File Statistics

From the inspected Ridgecrest run:

- `picks_20190704.csv`: **45,089 rows × 5 columns**
- `picks_20190705.csv`: **154,317 rows × 5 columns**

Missing-value check on inspected files:

- No null values were found in any of the 5 columns.

#### Example Rows

From `picks_20190704.csv`:

- `CI.CLC,2019-07-04T00:00:02.328300,0.344460,0.000256,P`
- `CI.HAR,2019-07-04T00:00:03.408300,0.364403,0.011767,P`
- `CI.TEH,2019-07-04T00:00:20.128300,0.361131,0.014412,P`

From `picks_20190705.csv`:

- `CI.WMF,2019-07-05T00:00:01.308300,0.447313,0.000062,P`
- `NN.GWY,2019-07-05T00:00:01.598300,0.443959,0.000131,P`
- `CI.CGO,2019-07-05T00:00:01.798300,0.300120,0.000009,P`

#### Access and Loading Notes

- These files can be loaded directly with `pandas.read_csv()`.
- The daily partitioning makes them suitable for explicit per-day loops over a fixed date range.
- `station_id` is the primary link to external station metadata and waveform archives.
- `phase_time` should be parsed carefully because downstream tools may require strict UTC formatting with `Z`.

#### Practical Relevance for Future Agents

For later association/location workflows, the most important fields in `picks_YYYYMMDD.csv` are:

- `station_id` for station matching
- `phase_time` for origin-time and travel-time workflows
- `phase_type` for separating P and S picks
- `phase_score` for any later pick-quality filtering
- `phase_amplitude` for any later pick-amplitude fallback logic

This is the authoritative per-pick input table format among the inspected PhaseNet outputs.

------------------------------

## station.sta
**Source path**: `<CASE_ROOT>/catalog_construction/01_step1_data_preprocessing_for_phasepicking/exp_run/outputs/01_preprocess_ridgecrest_stationday_waveforms/station.sta`
### Summary
`station.sta` is a plain-text station metadata table containing approximately 47 stations, one record per line, in comma-separated format without a header. The first four fields are directly useful for later association and location workflows: station identifier, latitude, longitude, and elevation; a fifth numeric field is present but not self-documented from file inspection alone.
### Detail
#### File Overview

- File: `station.sta`
- Format: plain text, comma-separated values
- Header: not present
- Number of records observed: **32** lines

This file is the key station metadata source for later agents that need station coordinates for defining map bounds, coordinate projection, and station lookup during phase association and location workflows.

#### Observed Record Pattern

Each line contains 5 comma-separated fields. Example rows:

- `CI.CCA,35.152520,-118.016490,710.00,626886820.397744`
- `CI.CCC,35.524950,-117.364530,670.00,627368612.812223`
- `CI.CGO,36.550400,-117.802950,2795.00,629864666.666667`
- `CI.CLC,35.815740,-117.597510,775.00,627369000.000000`
- `CI.CWC,36.439047,-118.080495,1569.50,629865000.000000`

#### Inferred Column Structure

Based on the observed values, the file can be interpreted as:

1. **`station_id`** — station key in `NET.STA` format
2. **`latitude`** — decimal degrees
3. **`longitude`** — decimal degrees
4. **`elevation_m`** — elevation in meters
5. **`aux_value`** — additional numeric field, likely internal or derived metadata; its meaning is not documented by inspection alone

Suggested provisional column names for loading:

- `station_id`
- `latitude`
- `longitude`
- `elevation_m`
- `aux_value`

#### Key Fields for Future Agents

Most relevant fields for downstream workflows are:

- **`station_id`**
  - Format: `NET.STA`
  - Examples: `CI.CCA`, `CI.CCC`, `CI.CGO`, `CI.CLC`, `CI.CWC`
  - This is the join key to pick tables and station-day waveform files.

- **`latitude`**
  - Decimal degree latitude
  - Example range in preview: about `35.15` to `36.55`
  - Useful for deriving geographic bounds and projected coordinates.

- **`longitude`**
  - Decimal degree longitude
  - Example range in preview: about `-118.08` to `-117.36`
  - Useful for geographic filtering and map projection.

- **`elevation_m`**
  - Elevation in meters
  - Example values: `670.00`, `710.00`, `775.00`, `1569.50`, `2795.00`
  - Potentially useful if later workflows need station elevation corrections.

- **`aux_value`**
  - Numeric value around `6.27e8` to `6.30e8` in previewed rows
  - Since the file has no header or inline documentation, this field should be treated cautiously unless cross-referenced elsewhere.

#### Relationship to Other Inputs

This file is structurally compatible with the other inspected inputs:

- Pick files use `station_id` values such as `CI.CLC` and `NN.GWY`
- Waveform filenames encode the same station identity as `{network}.{station}`

This means future agents can use the first column in `station.sta` as the common station key for:

- joining with `picks_YYYYMMDD.csv`
- locating station-specific MiniSEED files
- deriving geographic bounds from the available stations

#### Loading Notes

Recommended loading behavior:

- Use a CSV reader with comma delimiter
- Specify `header=None`
- Assign column names manually after loading

Example schema assumption for code:

- column 0: string station ID
- columns 1–4: numeric values

Because there is no header, downstream code should not rely on automatic column naming.

#### Practical Relevance for Later Workflows

For future coding agents, this file provides the minimum station metadata required to:

- enumerate available stations
- map pick `station_id` values to coordinates
- compute longitude/latitude bounds from the network geometry
- prepare projected `x/y` coordinates from station locations

The fifth numeric field exists in every row but should be treated as optional or unknown unless documentation elsewhere clarifies its definition.

------------------------------

