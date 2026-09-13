# Data Descriptions
## TRACE_ridgecrest_relocated.csv
**Source path**: `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/TRACE_ridgecrest_relocated.csv`
### Summary
This directory contains the relocated Ridgecrest earthquake catalog used for event selection and timing, plus a small companion CSV with the Mw 6.4 and Mw 7.1 mainshock metadata. The key analysis-ready file is `TRACE_ridgecrest_relocated.csv`, a 5-column flat CSV with 84,474 events spanning 2019-07-04 to 2019-07-25 in UTC, with no missing values in the core fields needed for spatial, temporal, and magnitude filtering.
### Detail
#### Folder Structure
- Base directory: `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE`
- Top-level contents observed:
  - `TRACE_ridgecrest_relocated.csv` — primary relocated earthquake catalog
  - `main_shock_events.csv` — two-row table for the mainshock reference events
  - `visualize.ipynb` — notebook present in the same folder, likely exploratory/supporting code rather than source data

#### Primary Files Relevant to Future Agents

##### 1) `TRACE_ridgecrest_relocated.csv`
- Format: CSV
- Size on disk: ~7.4 MB
- Shape: `84474 x 5`
- Columns:
  - `event_time` — string/timestamp field; ISO-like datetime strings with timezone offset (`+00:00`)
  - `latitude` — float64
  - `longitude` — float64
  - `depth_km` — float64
  - `magnitude` — float64
- Null counts:
  - `event_time`: 0
  - `latitude`: 0
  - `longitude`: 0
  - `depth_km`: 0
  - `magnitude`: 0
- Time coverage:
  - minimum: `2019-07-04 00:56:37.590000+00:00`
  - maximum: `2019-07-25 23:59:29.320000+00:00`
- Spatial coverage:
  - latitude range: `35.27090479518505` to `36.311627795185046`
  - longitude range: `-118.06486693463452` to `-116.9939567617556`
- Magnitude range:
  - minimum: `-0.85`
  - maximum: `7.1`
- Example rows indicate UTC-aware event timestamps with fractional seconds, e.g.:
  - `2019-07-04 00:56:37.590000+00:00, 36.088524, -117.827908, 9.701632, 0.66`
  - `2019-07-04 02:34:31.210000+00:00, 36.118940, -117.642917, 3.793481, 0.43`
- Interpretation for loading:
  - This is a simple event catalog table suitable for filtering by time window, magnitude threshold, and geometry.
  - `event_time` should be parsed with timezone awareness (`UTC`) before computing elapsed time from the Mw 6.4 event.
  - The file already contains the minimal fields needed for the user-prioritized workflow: time, hypocenter location, depth, and magnitude.

##### 2) `main_shock_events.csv`
- Format: CSV
- Size on disk: ~176 bytes
- Shape: `2 x 5`
- Columns (same schema as the catalog):
  - `event_time`
  - `latitude`
  - `longitude`
  - `depth_km`
  - `magnitude`
- Null counts: all zero
- Contains exactly two events corresponding to the two key mainshocks:
  - `2019-07-04 17:33:49.040000+00:00, 35.70421, -117.49392, 11.864, 6.4`
  - `2019-07-06 03:19:53.040000+00:00, 35.77623, -117.59286, 1.986, 7.1`
- Time span:
  - minimum: `2019-07-04 17:33:49.040000+00:00`
  - maximum: `2019-07-06 03:19:53.040000+00:00`
- Use for future agents:
  - This file is the authoritative source for the Mw 6.4 and Mw 7.1 origin times and epicentral coordinates needed to define the interevent period and annotate domain figures.
  - The rows are not explicitly labeled by event name, so agents should infer identity from the `magnitude` values (`6.4` and `7.1`) or row order after verification.

#### Schema Consistency
- Both CSVs share the same column layout:
  - `event_time, latitude, longitude, depth_km, magnitude`
- This makes it straightforward to load both with the same parser and combine or cross-reference them if needed.

#### Organization and Naming Conventions
- Directory organization is flat; there are no nested subdirectories at the inspected level.
- File naming is descriptive and task-oriented:
  - `TRACE_ridgecrest_relocated.csv` suggests a processed/relocated full catalog
  - `main_shock_events.csv` is a compact reference-event table
- Example access paths:
  - `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/TRACE_ridgecrest_relocated.csv`
  - `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/main_shock_events.csv`

#### Loading Notes for Future Coding Agents
- Recommended parsing steps:
  1. Read both CSVs with a standard CSV reader or pandas.
  2. Parse `event_time` using timezone-aware datetime conversion.
  3. Use `main_shock_events.csv` to extract the Mw 6.4 and Mw 7.1 reference times and coordinates.
  4. Filter the main catalog by time, magnitude, and spatial geometry as needed.
- No missing values were observed in the fields required for time-windowing and spatial selection.
- Because magnitudes in the main catalog include values below zero, thresholding should be applied explicitly rather than assumed from file contents.

#### Minimal Metadata Summary
- Data type: earthquake event catalogs in CSV format
- Core variables available: event origin time, latitude, longitude, depth, magnitude
- Main catalog record count: 84,474
- Mainshock reference record count: 2
- Time basis: UTC timestamps with offset included in the text strings
- Suitable for: event filtering, domain assignment, cumulative period construction, and subsequent rate-model fitting by downstream agents

------------------------------

## main_shock_events.csv
**Source path**: `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/main_shock_events.csv`
### Summary
This file is a compact 2-row CSV containing the two mainshock reference events needed to define the Ridgecrest interevent analysis window. It uses the same 5-column schema as the main catalog—`event_time`, `latitude`, `longitude`, `depth_km`, and `magnitude`—with no missing values and UTC timestamps suitable for direct time-difference calculations.
### Detail
#### File Overview
- Path: `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/main_shock_events.csv`
- Format: CSV
- Size on disk: ~176 bytes
- Shape: `2 x 5`
- Purpose: reference-event table for the two mainshocks used to define the primary time window and annotate figures

#### Column Schema
The file contains the following columns:
- `event_time` — event origin time as a string timestamp with timezone offset (`+00:00`)
- `latitude` — hypocenter latitude in decimal degrees
- `longitude` — hypocenter longitude in decimal degrees
- `depth_km` — depth in kilometers
- `magnitude` — event magnitude

Observed dtypes after CSV load:
- `event_time`: object/string
- `latitude`: float64
- `longitude`: float64
- `depth_km`: float64
- `magnitude`: float64

#### Row Contents
The file contains exactly two events:
1. `2019-07-04 17:33:49.040000+00:00, 35.70421, -117.49392, 11.864, 6.4`
2. `2019-07-06 03:19:53.040000+00:00, 35.77623, -117.59286, 1.986, 7.1`

These correspond to the user-described reference events:
- Mainshock64: magnitude `6.4`
- Mainshock71: magnitude `7.1`

#### Basic Metadata
- Null counts:
  - `event_time`: 0
  - `latitude`: 0
  - `longitude`: 0
  - `depth_km`: 0
  - `magnitude`: 0
- Time range:
  - minimum: `2019-07-04 17:33:49.040000+00:00`
  - maximum: `2019-07-06 03:19:53.040000+00:00`
- Latitude range: `35.70421` to `35.77623`
- Longitude range: `-117.59286` to `-117.49392`
- Depth range: `1.986` to `11.864` km
- Magnitude range: `6.4` to `7.1`

#### Relevance for Future Agents
- This file is the authoritative source for the two event origin times needed to define:
  - `T = 0` at the Mw 6.4 event
  - the interevent endpoint at the Mw 7.1 event
- It also provides the mainshock coordinates needed for map/domain-assignment diagnostics.
- The rows are not labeled with explicit names like `Mainshock64` or `Mainshock71`, so identification should be based on `magnitude` values (6.4 and 7.1) or validated row order.

#### Loading Notes
- Parse `event_time` as timezone-aware UTC datetimes before computing elapsed days.
- Because the schema matches the main catalog (`TRACE_ridgecrest_relocated.csv`), this file can be loaded with the same parser and column assumptions.
- No additional metadata fields such as event IDs or names are present; downstream code should attach labels explicitly after loading.

#### Example Access Pattern
- Example path: `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/main_shock_events.csv`
- Typical use:
  - load CSV
  - locate row with `magnitude == 6.4` for Mw 6.4 origin time
  - locate row with `magnitude == 7.1` for Mw 7.1 origin time and map annotation

------------------------------

