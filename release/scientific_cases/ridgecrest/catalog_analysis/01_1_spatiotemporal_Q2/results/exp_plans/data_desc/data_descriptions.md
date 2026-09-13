# Data Descriptions
## TRACE_ridgecrest_relocated.csv
**Source path**: `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/TRACE_ridgecrest_relocated.csv`
### Summary
This directory contains relocated Ridgecrest earthquake catalogs as CSV files plus a small two-row mainshock reference table. The primary file requested for future analysis is `TRACE_ridgecrest_relocated.csv`, a 94,803-row event catalog with five core fields (`event_time`, `latitude`, `longitude`, `depth_km`, `magnitude`) and no missing values; `main_shock_events.csv` provides the Mw 6.4 and Mw 7.1 reference hypocenters/times needed to define analysis windows.
### Detail
#### Folder Structure
- Directory: `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE`
- Contents follow a simple flat layout (no nested subdirectories observed):
  - `TRACE_ridgecrest_relocated.csv` — primary relocated event catalog referenced in the request
  - `main_shock_events.csv` — two-event table for the Mw 6.4 and Mw 7.1 mainshocks
  - `TRACE_ridgecrest_relocated-v0.csv`, `TRACE_ridgecrest_relocated-v1.csv`, `TRACE_ridgecrest_relocated-v2.csv` — alternate/versioned catalog snapshots
  - `visualize.ipynb` — notebook, likely exploratory/plotting support

#### File Naming Conventions
- Main catalog pattern: `TRACE_ridgecrest_relocated*.csv`
- Versioned variants use suffixes like `-v0`, `-v1`, `-v2`.
- Mainshock reference file has a descriptive name: `main_shock_events.csv`.
- Example paths:
  - `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/TRACE_ridgecrest_relocated.csv`
  - `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/main_shock_events.csv`

#### Primary Catalog: `TRACE_ridgecrest_relocated.csv`
- Format: CSV text table
- Size on disk: ~8.3 MB
- Shape: 94,803 rows × 5 columns
- Columns:
  - `event_time` — event origin time as string, timezone-aware in this file (examples include `+00:00`)
  - `latitude` — decimal degrees
  - `longitude` — decimal degrees
  - `depth_km` — depth in kilometers
  - `magnitude` — event magnitude
- Data types on read:
  - `event_time`: object/string (should be parsed with `pandas.to_datetime(..., utc=True)` or equivalent)
  - other four columns: `float64`
- Missing values: none detected in any column

#### Primary Catalog Metadata Relevant to Requested Analysis
- Time span:
  - earliest event: `2019-07-04 00:56:37.590000+00:00`
  - latest event: `2019-07-25 23:59:29.320000+00:00`
- Spatial extent:
  - latitude: 35.26342979518505 to 36.27444879518505
  - longitude: -118.07426618617616 to -116.99198271420352
- Depth range:
  - 0.37488317 to 29.07368735 km
- Magnitude range:
  - -0.83 to 7.1
- Mean values:
  - latitude: 35.763321625331876
  - longitude: -117.57116189261956
  - depth_km: 5.524614276545784
  - magnitude: 0.9674141080154314
- First rows indicate the catalog is event-based and directly suitable for:
  - filtering by time windows relative to the Mw 6.4 origin time
  - longitude/latitude epicenter scatter plotting
  - gridding in map view for onset-time or rate calculations

#### Mainshock Reference File: `main_shock_events.csv`
- Format: CSV text table
- Size on disk: ~176 bytes
- Shape: 2 rows × 5 columns
- Same schema as the main catalog:
  - `event_time`, `latitude`, `longitude`, `depth_km`, `magnitude`
- Missing values: none detected
- Rows correspond to the two key reference events mentioned in the request:
  1. Mw 6.4: `2019-07-04 17:33:49.040000+00:00`, lat `35.70421`, lon `-117.49392`, depth `11.864` km
  2. Mw 7.1: `2019-07-06 03:19:53.040000+00:00`, lat `35.77623`, lon `-117.59286`, depth `1.986` km
- This file is the authoritative lookup table for defining:
  - `[mainshock64, mainshock64 + 4 hours]`
  - `[mainshock64, mainshock71]`
  - map overlays for the two mainshock epicenters

#### Alternate Catalog Versions
- `TRACE_ridgecrest_relocated-v0.csv`
  - 90,084 rows × 5 columns
  - same column names and numeric structure
  - `event_time` examples do **not** show timezone suffix in sample rows
  - time span: `2019-07-04 00:46:47.750000` to `2019-07-25 23:59:29.840000`
- `TRACE_ridgecrest_relocated-v1.csv`
  - 79,060 rows × 5 columns
  - timezone-aware `event_time` strings in sample rows
  - time span: `2019-07-04 15:42:47.580000+00:00` to `2019-07-25 23:59:29.560000+00:00`
- `TRACE_ridgecrest_relocated-v2.csv`
  - 95,052 rows × 5 columns
  - same schema; appears to be another relocated catalog revision
- These versioned files may be useful for provenance or comparison, but the user-specified target appears to be the unversioned `TRACE_ridgecrest_relocated.csv`.

#### Schema Consistency
- All inspected CSV catalogs use the same five-column schema, which simplifies loading and swapping between versions.
- No null values were found in any inspected file.
- The main practical ingestion issue is timestamp parsing consistency:
  - most files use timezone-aware UTC strings (`+00:00`)
  - `v0` sample rows lack an explicit timezone suffix

#### Access and Loading Notes for Future Agents
- Recommended load pattern in Python:
  - `pd.read_csv(path)`
  - then parse `event_time` with `pd.to_datetime(df['event_time'], utc=True, errors='coerce')`
- For map-based gridding or onset-time workflows, the key usable fields are exactly the five columns already present; no extra joins are required except optionally attaching the two-row mainshock reference table.
- Because the requested spatial discretization is in kilometers while the catalog is in latitude/longitude, future agents will need a coordinate conversion/projection step when building 0.5 km × 0.5 km cells.

#### Small Data Preview
- `TRACE_ridgecrest_relocated.csv` first three records:
  - `2019-07-04 00:56:37.590000+00:00, 36.08702179518505, -117.83758371145888, 8.787102200000001, 0.8`
  - `2019-07-04 02:34:31.260000+00:00, 36.11755579518505, -117.65615695896209, 3.93138647, 0.43`
  - `2019-07-04 03:20:28.450000+00:00, 36.11065879518505, -117.62002445100116, 2.31281456, 0.88`
- `main_shock_events.csv` contains exactly the two mainshock rows and can be read trivially into memory.

#### Relevance to the Requested Workflow
- The available metadata are sufficient for future agents to:
  - subset the catalog using the Mw 6.4 and Mw 7.1 event times
  - color-code epicenters by time bins in longitude–latitude space
  - create grid-based local event-count time series from `event_time` and event coordinates
  - overlay the two mainshock epicenters using the separate reference CSV
- No derived rate, onset, or triggering products are precomputed in this directory; only raw/relocated event tables and mainshock references are present.

------------------------------

## main_shock_events.csv
**Source path**: `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/main_shock_events.csv`
### Summary
This file is a small CSV reference table containing exactly two Ridgecrest mainshock events: the Mw 6.4 event and the Mw 7.1 event. It uses the same five-column schema as the relocated catalog and provides the authoritative event times and epicenters needed to define analysis windows and map overlays.
### Detail
#### File Overview
- Path: `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/main_shock_events.csv`
- Format: CSV text file
- Size: ~176 bytes
- Shape: 2 rows × 5 columns
- Purpose: reference metadata for the two mainshock events used to anchor time-window selection and epicenter overlays in later analysis

#### Column Schema
The file has a header row with the following columns:
1. `event_time`
2. `latitude`
3. `longitude`
4. `depth_km`
5. `magnitude`

Observed data types when read with pandas:
- `event_time`: object/string
- `latitude`: float64
- `longitude`: float64
- `depth_km`: float64
- `magnitude`: float64

Missing values:
- No missing values detected in any column

#### Event Records
This file contains exactly these two rows:
- Mw 6.4 mainshock:
  - `event_time`: `2019-07-04 17:33:49.040000+00:00`
  - `latitude`: `35.70421`
  - `longitude`: `-117.49392`
  - `depth_km`: `11.864`
  - `magnitude`: `6.4`
- Mw 7.1 mainshock:
  - `event_time`: `2019-07-06 03:19:53.040000+00:00`
  - `latitude`: `35.77623`
  - `longitude`: `-117.59286`
  - `depth_km`: `1.986`
  - `magnitude`: `7.1`

#### Time Metadata Relevant to Future Agents
- Earliest timestamp: `2019-07-04 17:33:49.040000+00:00`
- Latest timestamp: `2019-07-06 03:19:53.040000+00:00`
- Timestamp strings are timezone-aware and include a `+00:00` UTC offset
- This file can be used directly to derive:
  - the Mw 6.4 origin time (`mainshock64`)
  - the Mw 7.1 origin time (`mainshock71`)
  - the interval `[mainshock64, mainshock64 + 4 hours]`
  - the interval `[mainshock64, mainshock71]`

#### Spatial Metadata Relevant to Future Agents
- Latitude range: 35.70421 to 35.77623
- Longitude range: -117.59286 to -117.49392
- These two points are suitable for direct overlay on longitude–latitude epicenter maps generated from the larger relocated catalog

#### Loading and Access Notes
- Straightforward load pattern:
  - `pd.read_csv('<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/main_shock_events.csv')`
- Recommended timestamp parsing:
  - `df['event_time'] = pd.to_datetime(df['event_time'], utc=True)`
- Since the file contains only two rows, future agents can also safely load it into a small dictionary or extract rows by magnitude or row order if needed

#### Relationship to Other Data
- The schema matches the main relocated event catalog at:
  - `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/TRACE_ridgecrest_relocated.csv`
- This makes it easy to use the file as a reference table without any column renaming or transformation
- No derived labels, bins, or triggering metrics are included; the file is purely a compact mainshock metadata source

------------------------------

