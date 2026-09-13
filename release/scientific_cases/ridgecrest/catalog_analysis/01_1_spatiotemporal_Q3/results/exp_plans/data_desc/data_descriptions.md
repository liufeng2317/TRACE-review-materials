# Data Descriptions
## TRACE_ridgecrest_relocated.csv
**Source path**: `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/TRACE_ridgecrest_relocated.csv`
### Summary
This directory contains a relocated Ridgecrest earthquake catalog and a small companion file with the two mainshock reference events needed to define the inter-mainshock analysis window. The primary catalog is a single CSV with 94,803 events and five core fields (`event_time`, `latitude`, `longitude`, `depth_km`, `magnitude`), while `main_shock_events.csv` has the same schema for the Mw 6.4 and Mw 7.1 events.
### Detail
#### Folder Structure
- Directory: `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE`
- Observed contents follow a simple flat layout:
  - `TRACE_ridgecrest_relocated.csv` — primary relocated seismicity catalog
  - `main_shock_events.csv` — two-row mainshock reference table
  - versioned backups of the main catalog such as:
    - `TRACE_ridgecrest_relocated-v0.csv`
    - `TRACE_ridgecrest_relocated-v1.csv`
    - `TRACE_ridgecrest_relocated-v2.csv`
  - `visualize.ipynb` — notebook artifact in the same folder

This suggests the working dataset is a CSV-based catalog directory with one current catalog plus prior version snapshots using a `-vN` suffix naming convention.

#### File Inventory Relevant to the Requested Analysis
1. **Primary event catalog**
   - Path: `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/TRACE_ridgecrest_relocated.csv`
   - Size: ~8.3 MB
   - Rows: 94,803 data rows
   - Columns: 5
   - Header fields:
     - `event_time`
     - `latitude`
     - `longitude`
     - `depth_km`
     - `magnitude`

2. **Mainshock reference file**
   - Path: `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/main_shock_events.csv`
   - Size: ~176 bytes
   - Rows: 2 data rows
   - Columns: 5
   - Same header schema as the main catalog

#### Schema and Types
Both CSV files share the same column structure, which makes them easy to join or filter consistently.

- `event_time` — timestamp string; successfully parses as timezone-aware UTC datetimes
- `latitude` — `float64`
- `longitude` — `float64`
- `depth_km` — `float64`
- `magnitude` — `float64`

No missing values were detected in either file for these five columns.

#### Primary Catalog Metadata
File: `TRACE_ridgecrest_relocated.csv`

- Shape: `(94803, 5)`
- Time coverage:
  - Earliest event: `2019-07-04 00:56:37.590000+00:00`
  - Latest event: `2019-07-25 23:59:29.320000+00:00`
- Spatial/value ranges:
  - `latitude`: min `35.26342979518505`, max `36.27444879518505`, mean `35.763321625331876`
  - `longitude`: min `-118.07426618617616`, max `-116.99198271420352`, mean `-117.57116189261956`
  - `depth_km`: min `0.37488317`, max `29.07368735`, mean `5.524614276545784`
  - `magnitude`: min `-0.83`, max `7.1`, mean `0.9674141080154314`
- Missing values:
  - `event_time`: 0
  - `latitude`: 0
  - `longitude`: 0
  - `depth_km`: 0
  - `magnitude`: 0
- Example rows show UTC timestamps with sub-second precision and positive/negative longitudes in decimal degrees.

Example record pattern:
- `2019-07-04 00:56:37.590000+00:00, 36.087022, -117.837584, 8.787102, 0.80`

#### Mainshock Reference File Metadata
File: `main_shock_events.csv`

- Shape: `(2, 5)`
- Time coverage:
  - Earliest event: `2019-07-04 17:33:49.040000+00:00`
  - Latest event: `2019-07-06 03:19:53.040000+00:00`
- Missing values: none
- Contents correspond to the two key events for inter-mainshock windowing:
  - Mw 6.4 event:
    - `event_time`: `2019-07-04 17:33:49.040000+00:00`
    - `latitude`: `35.70421`
    - `longitude`: `-117.49392`
    - `depth_km`: `11.864`
    - `magnitude`: `6.4`
  - Mw 7.1 event:
    - `event_time`: `2019-07-06 03:19:53.040000+00:00`
    - `latitude`: `35.77623`
    - `longitude`: `-117.59286`
    - `depth_km`: `1.986`
    - `magnitude`: `7.1`

#### Organization and Access Pattern for Future Agents
- Both files are standard CSVs and can be loaded directly with `pandas.read_csv`.
- For time-based filtering, `event_time` should be parsed with UTC awareness (the strings already include `+00:00`).
- The user-requested analyses are naturally supported by this schema:
  - **Spatiotemporal filtering**: use `event_time`
  - **2D spatial mapping / KDE**: use `latitude`, `longitude`
  - **Hotspot/mainshock overlays**: use coordinates from `main_shock_events.csv`
  - **Depth- or magnitude-aware subsetting if needed later**: use `depth_km`, `magnitude`

#### Practical Notes for Downstream Loading
- The main catalog already includes the mainshock period and extends well beyond it; downstream code should explicitly subset to the interval bounded by the two rows in `main_shock_events.csv` when working on inter-mainshock evolution.
- Because the folder contains versioned catalog variants (`-v0`, `-v1`, `-v2`), downstream agents should use the unversioned file `TRACE_ridgecrest_relocated.csv` unless a comparison across versions is intentionally required.
- The directory is flat rather than nested, so path handling is simple and does not require recursive discovery for the core inputs.

#### Example Paths
- Current catalog: `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/TRACE_ridgecrest_relocated.csv`
- Mainshock file: `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/main_shock_events.csv`
- Example versioned catalog: `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/TRACE_ridgecrest_relocated-v2.csv`

------------------------------

## main_shock_events.csv
**Source path**: `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/main_shock_events.csv`
### Summary
This CSV is a compact two-row reference table containing the Ridgecrest Mw 6.4 and Mw 7.1 mainshock events, using the same five-column schema as the full relocated catalog. It is the key metadata source for defining the inter-mainshock analysis window and for overlaying the two mainshock epicenters on downstream spatial plots.
### Detail
#### File Overview
- Path: `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/main_shock_events.csv`
- Format: CSV with header row
- Size: ~176 bytes
- Shape: 2 rows × 5 columns
- Purpose in this dataset: reference event table for the two mainshocks that bound the requested inter-mainshock analyses

#### Column Schema
The file contains the following columns:
- `event_time` — event origin time as a timestamp string with UTC offset
- `latitude` — epicentral latitude in decimal degrees
- `longitude` — epicentral longitude in decimal degrees
- `depth_km` — focal depth in kilometers
- `magnitude` — event magnitude

Observed dtypes after CSV loading:
- `event_time`: object/string, but parses cleanly to timezone-aware UTC datetimes
- `latitude`: float64
- `longitude`: float64
- `depth_km`: float64
- `magnitude`: float64

#### Row Contents
This file has exactly two records:

1. **Mw 6.4 mainshock**
   - `event_time`: `2019-07-04 17:33:49.040000+00:00`
   - `latitude`: `35.70421`
   - `longitude`: `-117.49392`
   - `depth_km`: `11.864`
   - `magnitude`: `6.4`

2. **Mw 7.1 mainshock**
   - `event_time`: `2019-07-06 03:19:53.040000+00:00`
   - `latitude`: `35.77623`
   - `longitude`: `-117.59286`
   - `depth_km`: `1.986`
   - `magnitude`: `7.1`

#### Time Metadata Relevant to Future Agents
- Parsed time range:
  - Start: `2019-07-04 17:33:49.040000+00:00`
  - End: `2019-07-06 03:19:53.040000+00:00`
- The timestamps include `+00:00`, so downstream code should treat them as UTC-aware datetimes.
- This file directly provides the endpoints for the requested analysis window `[mainshock64, mainshock71]`.

#### Spatial Metadata Relevant to Future Agents
- Latitude range: `35.70421` to `35.77623`
- Longitude range: `-117.59286` to `-117.49392`
- These coordinates are appropriate for:
  - plotting the Mw 6.4 and Mw 7.1 epicenters as reference markers
  - defining directionality for qualitative migration/path visualizations
  - annotating convex hull / alpha-shape / KDE figures

#### Data Quality / Completeness
- Missing values by column:
  - `event_time`: 0
  - `latitude`: 0
  - `longitude`: 0
  - `depth_km`: 0
  - `magnitude`: 0
- `event_time` parsing failures: 0
- The file is clean and minimal, with no extra columns or identifiers.

#### Relationship to the Main Catalog
- Schema matches the full relocated catalog file:
  - `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/TRACE_ridgecrest_relocated.csv`
- Because both files share the same columns, future agents can load them with the same parser and reuse plotting/filtering code.
- Typical downstream use is:
  1. load the two-row mainshock file,
  2. extract the Mw 6.4 and Mw 7.1 event times,
  3. subset the full catalog between those timestamps,
  4. overlay these two epicenters on all spatial products.

#### Example Access Pattern
- Load with `pandas.read_csv(...)`
- Parse `event_time` using `pd.to_datetime(..., utc=True)`
- Identify rows by `magnitude == 6.4` and `magnitude == 7.1` if needed, though row count is only 2

#### Example Path
- `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/main_shock_events.csv`

------------------------------

