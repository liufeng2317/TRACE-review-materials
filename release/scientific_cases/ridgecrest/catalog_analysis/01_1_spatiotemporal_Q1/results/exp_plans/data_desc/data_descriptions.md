# Data Descriptions
## TRACE_ridgecrest_relocated.csv
**Source path**: `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/TRACE_ridgecrest_relocated.csv`
### Summary
This directory contains the Ridgecrest earthquake catalog used for plotting and time-window slicing, plus a small two-row file with the Mw 6.4 and Mw 7.1 mainshock epicenters/times. The primary file for future agents is `TRACE_ridgecrest_relocated.csv`, a 94,803-row CSV with complete event-level fields `event_time`, `latitude`, `longitude`, `depth_km`, and `magnitude`, covering 2019-07-04 through 2019-07-25 in UTC.
### Detail
#### Folder Structure
- **Base directory:** `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE`
- **Observed contents:**
  - `TRACE_ridgecrest_relocated.csv` — primary relocated event catalog referenced by the request
  - `main_shock_events.csv` — two mainshock reference events (Mw 6.4 and Mw 7.1)
  - `TRACE_ridgecrest_relocated-v0.csv`, `TRACE_ridgecrest_relocated-v1.csv`, `TRACE_ridgecrest_relocated-v2.csv` — alternate/versioned relocated catalogs with the same column schema
  - `visualize.ipynb` — notebook likely related to inspection/plotting

**Organizational pattern:** the directory is flat (no nested subfolders observed). Catalog files are CSVs with a shared event schema and version suffixes (`-v0`, `-v1`, `-v2`) indicating iterative catalog variants.

#### Primary Files Relevant to Future Agents
1. **Primary catalog:** `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/TRACE_ridgecrest_relocated.csv`
2. **Mainshock reference file:** `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/main_shock_events.csv`

These two files are sufficient for later agents to build time slices, before/after mainshock subsets, and map overlays.

#### File Format and Schema
Both relevant files are standard **CSV** text tables with the same 5 columns:
- `event_time` — timestamp string; examples include timezone-aware UTC strings such as `2019-07-04 17:33:49.040000+00:00`
- `latitude` — decimal degrees
- `longitude` — decimal degrees
- `depth_km` — depth in kilometers
- `magnitude` — event magnitude

**Important loading note:**
- `event_time` is stored as text and should be parsed explicitly (e.g., with `pandas.to_datetime(..., utc=True)`).
- In the primary catalog, timestamps are already in UTC-offset form (`+00:00`).

#### Primary Catalog Metadata
**File:** `TRACE_ridgecrest_relocated.csv`
- **Rows / columns:** 94,803 × 5
- **Approx. size on disk:** 8.3 MB
- **Missing values:** none detected in any column
- **Column dtypes after CSV read:**
  - `event_time`: object/string
  - `latitude`, `longitude`, `depth_km`, `magnitude`: float64

**Temporal coverage:**
- Minimum `event_time`: `2019-07-04 00:56:37.590000+00:00`
- Maximum `event_time`: `2019-07-25 23:59:29.320000+00:00`

**Spatial / numeric ranges:**
- `latitude`: min 35.26342979518505, max 36.27444879518505, mean 35.763321625331876
- `longitude`: min -118.07426618617616, max -116.99198271420352, mean -117.57116189261956
- `depth_km`: min 0.37488317, max 29.07368735, mean 5.524614276545784
- `magnitude`: min -0.83, max 7.1, mean 0.9674141080154314

**First few records pattern:**
- Example row 1: `2019-07-04 00:56:37.590000+00:00, 36.08702179518505, -117.83758371145888, 8.787102200000001, 0.8`
- Example row 2: `2019-07-04 02:34:31.260000+00:00, 36.11755579518505, -117.65615695896209, 3.93138647, 0.43`

**Implications for downstream access:**
- This file is event-based, already in a tidy format suitable for filtering by time windows and plotting lon/lat scatter maps.
- No station/channel structure is present; each row is one earthquake event.
- A future agent can directly subset by `event_time` relative to the mainshock times in `main_shock_events.csv`.

#### Mainshock Reference File Metadata
**File:** `main_shock_events.csv`
- **Rows / columns:** 2 × 5
- **Approx. size on disk:** 176 bytes
- **Missing values:** none detected
- **Schema:** identical to primary catalog

**Contents:**
- Mw 6.4 event:
  - `event_time`: `2019-07-04 17:33:49.040000+00:00`
  - `latitude`: 35.70421
  - `longitude`: -117.49392
  - `depth_km`: 11.864
  - `magnitude`: 6.4
- Mw 7.1 event:
  - `event_time`: `2019-07-06 03:19:53.040000+00:00`
  - `latitude`: 35.77623
  - `longitude`: -117.59286
  - `depth_km`: 1.986
  - `magnitude`: 7.1

**Use in later workflows:**
- Provides exact time anchors for defining windows such as:
  - before/after Mw 6.4
  - between Mw 6.4 and Mw 7.1
  - after Mw 7.1 plus fixed offsets (e.g., +1 day, +2 days, +5 days)
- Provides two epicenters for map overlays.

#### Versioned Alternate Catalogs
Other CSVs in the same directory follow the same schema but different extents and counts:
- `TRACE_ridgecrest_relocated-v0.csv` — 90,084 rows; time span `2019-07-04 00:46:47.750000+00:00` to `2019-07-25 23:59:29.840000+00:00`
- `TRACE_ridgecrest_relocated-v1.csv` — 79,060 rows; time span `2019-07-04 15:42:47.580000+00:00` to `2019-07-25 23:59:29.560000+00:00`
- `TRACE_ridgecrest_relocated-v2.csv` — same 5-column structure; appears to be another intermediate catalog version

These may be useful for provenance checks or comparing catalog revisions, but the request explicitly points to `TRACE_ridgecrest_relocated.csv` as the main working file.

#### Naming Conventions
- **Catalog family:** `TRACE_ridgecrest_relocated*.csv`
- **Version pattern:** `TRACE_ridgecrest_relocated-vN.csv` where `N` is an integer version label
- **Reference event file:** `main_shock_events.csv`

This naming makes it easy for a future agent to glob for catalog versions while selecting the unversioned file as the default/current dataset.

#### Recommended Loading Pattern for Future Agents
- Read with `pandas.read_csv(...)`
- Parse `event_time` using UTC-aware datetime conversion
- Keep all rows; no null handling appears necessary for the inspected files
- Use `main_shock_events.csv` as the authoritative source for:
  - mainshock timestamps
  - mainshock overlay coordinates

#### Minimal Access Examples
- Primary catalog path:
  - `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/TRACE_ridgecrest_relocated.csv`
- Mainshock file path:
  - `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/main_shock_events.csv`

#### Practical Notes for Plotting/Windowing Agents
- The data already contain the only fields needed for longitude-latitude time-sliced maps: time, latitude, longitude, and optional symbol encoding by magnitude/depth.
- Because all requested map panels must share the same extent, a future agent can derive a fixed plotting box from the catalog-wide min/max lon/lat values above, optionally with a small margin.
- Since the mainshock file has exactly two rows, it can be read once and used repeatedly as overlay markers and time cut points.

------------------------------

## main_shock_events.csv
**Source path**: `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/main_shock_events.csv`
### Summary
This CSV is a compact two-row reference table containing the Mw 6.4 and Mw 7.1 Ridgecrest mainshocks, with the same event schema as the full catalog: `event_time`, `latitude`, `longitude`, `depth_km`, and `magnitude`. It is primarily used by future agents to define time-window boundaries and to overlay the two mainshock epicenters on sequence maps.
### Detail
#### File Overview
- **Path:** `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/main_shock_events.csv`
- **Format:** CSV text table
- **Rows / columns:** 2 × 5
- **Approx. size:** 176 bytes
- **Header row:** present

This file is a small event reference table rather than a full seismicity catalog. It provides the two anchor events needed for time slicing and map annotation in later workflows.

#### Column Schema
The file contains these columns:
- `event_time` — event origin time as a timestamp string
- `latitude` — epicentral latitude in decimal degrees
- `longitude` — epicentral longitude in decimal degrees
- `depth_km` — focal depth in kilometers
- `magnitude` — event magnitude

**Read-time dtypes observed from CSV parsing:**
- `event_time`: object/string
- `latitude`: float64
- `longitude`: float64
- `depth_km`: float64
- `magnitude`: float64

**Missing values:** none detected in any column.

#### File Contents
The two records are:
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

#### Temporal and Numeric Metadata
- **Time span covered by this file:**
  - Min `event_time`: `2019-07-04 17:33:49.040000+00:00`
  - Max `event_time`: `2019-07-06 03:19:53.040000+00:00`

- **Value ranges across the two rows:**
  - `latitude`: 35.70421 to 35.77623
  - `longitude`: -117.59286 to -117.49392
  - `depth_km`: 1.986 to 11.864
  - `magnitude`: 6.4 to 7.1

#### Relevance for Future Agents
This file is the authoritative source for the two mainshock markers and should be loaded alongside the main catalog when building:
- time windows before and after Mw 6.4
- time windows before and after Mw 7.1
- interval sequences such as `[mainshock64, mainshock71 + 1 day]`, `[mainshock71 + 1 day, mainshock71 + 5 days]`, or `[mainshock71, mainshock71 + 2 days]`
- map overlays of mainshock epicenters

Because the file shares the same schema as the full relocated catalog, it can be loaded with the same parser and merged or referenced without column renaming.

#### Timestamp and Loading Notes
- `event_time` values are timezone-aware UTC strings with explicit `+00:00` offsets.
- Recommended parsing pattern for future agents: convert `event_time` explicitly with a UTC-aware datetime parser (for example, `pandas.to_datetime(..., utc=True)`).
- Since there are only two rows and no missing values, no cleaning is needed before using this file as a temporal/epicentral reference.

#### Example Access Pattern
- Direct path:
  - `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/main_shock_events.csv`
- Typical downstream usage:
  - read once
  - identify rows by `magnitude` 6.4 and 7.1, or by row order if trusted
  - use `event_time` for slicing the larger catalog and `latitude`/`longitude` for overlay symbols on maps

------------------------------

