# Data Descriptions
## data
**Source path**: `<CASE_ROOT>/data`
### Summary
This data directory is organized around an Aomori-region earthquake catalog workflow, with key inputs in `catalog/`, focal mechanisms in `source_mechanism/`, and station metadata in `stations/`. For the requested M1-M3 screening task, the most relevant files are the relocated catalog `catalog/Snet_catalog_relocate_250601_260501.csv`, the three-event mainshock table `catalog/main_earthquake.csv`, the mechanism table `source_mechanism/Snet_mecha.csv`, and the station list `stations/station.sta`; note that the relocated catalog is a headerless 5-column CSV and should be read with explicit column names.
### Detail
#### Folder Structure
- Root data directory contains several topical subfolders rather than one flat catalog dump:
  - `catalog/` — earthquake catalogs and notebook assets.
  - `source_mechanism/` — focal mechanism table(s).
  - `stations/` — station metadata.
  - `active_fault/` — fault geometry context (`japan_active_faults.geojson`).
  - `DEM/` — topography rasters.
  - `event_screen/` — previously generated screening/summary CSVs related to M1-M3-style analyses.
  - top-level notebooks such as `visualize.ipynb`.
- Relevant example paths:
  - `catalog/Snet_catalog_relocate_250601_260501.csv`
  - `catalog/main_earthquake.csv`
  - `source_mechanism/Snet_mecha.csv`
  - `stations/station.sta`
  - optional context/derived files already present: `event_screen/m1_m3_event_chain_table.csv`, `event_screen/m1_m3_event_geometry.csv`, `event_screen/m1_m3_burst_summary.csv`

#### Key Files for the M1-M3 Catalog Task
1. **Relocated/filtered catalog**
   - Path: `catalog/Snet_catalog_relocate_250601_260501.csv`
   - Size: ~1.51 MB
   - Format: CSV with **no header row**.
   - Recommended column names when loading: `time, lat, lon, dep_km, mag`
   - Shape when read correctly with `header=None`: **25,648 rows × 5 columns**
   - Time span: **2025-06-01T00:13:38.900000Z** to **2026-05-01T14:44:22.450000Z**
   - Data types:
     - `time`: string/ISO-like timestamp with trailing `Z`
     - `lat`, `lon`, `dep_km`, `mag`: numeric
   - No missing values detected in these 5 fields.
   - Value ranges:
     - `lat`: 38.50304 to 42.382633
     - `lon`: 141.000635 to 144.49847
     - `dep_km`: 0.0 to 6221.0
     - `mag`: -0.5 to 7.7
   - Important loading note: if read with default `pd.read_csv(...)`, pandas treats the first event row as column names, producing misleading headers such as `2025-06-01T00:13:38.900000Z`, `39.245593`, etc. Future agents should explicitly use `header=None` and assign names.
   - Content pattern: one earthquake per row with only the minimal fields needed for geometry/time screening; no event ID column is present in this file.
   - Sample rows after correct loading:
     - `2025-06-01T00:13:38.900000Z, 39.245593, 142.382422, 29.70, 1.7`
     - `2025-06-01T00:30:20.430000Z, 41.623617, 142.114681, 55.14, 1.7`

2. **Mainshock table**
   - Path: `catalog/main_earthquake.csv`
   - Size: 184 bytes
   - Shape: **3 rows × 6 columns**
   - Columns: `index, datetime, lat, lon, dep, mag`
   - This is the key reference table for defining M1, M2, and M3 endpoint geometry and time windows.
   - Rows:
     - `M1, 2025-11-09 08:03:39.240, 39.402, 143.507, 15.9, 6.9`
     - `M2, 2025-12-08 14:15:10.180, 40.968, 142.288, 53.5, 7.5`
     - `M3, 2026-04-20 07:52:58.060, 39.842, 143.157, 19.4, 7.7`
   - No missing values detected.
   - Practical usage: this file provides the coordinates and times needed to compute distance-to-M1/M2/M3, time since M1, time before M3, corridor projections, and M2-aware flags.

3. **Source mechanism table**
   - Path: `source_mechanism/Snet_mecha.csv`
   - Size: ~61.7 KB
   - Shape: **354 rows × 29 columns**
   - Main columns:
     - event metadata: `event_code`, `origin_time`, `lat_deg`, `lon_deg`, `depth_km`, `region_name`
     - magnitudes: `mag_1`, `mag_1_type`, `mag_2`, `mag_2_type`
     - station/method metadata: `n_hypo_stations`, `m_method`, `m_source`, `n_mech_stations`, `source_file`
     - mechanism axes: `P_axis_azimuth`, `P_axis_dip`, `T_axis_azimuth`, `T_axis_dip`, `N_axis_azimuth`, `N_axis_dip`
     - nodal planes: `strike_plane1`, `dip_plane1`, `rake_plane1`, `strike_plane2`, `dip_plane2`, `rake_plane2`
     - quality/projection: `focal_mech_score`, `focal_mech_projection`
   - Missingness pattern:
     - Many mechanism-specific columns have **215 missing values**, implying only a subset of events has full mechanism solutions.
     - `mag_2`, `mag_2_type`, `m_method`, `m_source`, all axis/plane fields, `focal_mech_score`, `n_mech_stations`, `focal_mech_projection` are sparse.
   - Practical usage: useful as optional context for later follow-up mechanism screening, but not required to parse the base relocated catalog.

4. **Station metadata**
   - Path: `stations/station.sta`
   - Size: ~16.1 KB
   - Plain text/CSV-like file with header row.
   - Total lines: **372** (including header)
   - Header: `station_code,station_number,latitude,longitude,elevation_m,matched`
   - Sample rows:
     - `A.ASMS,5572,40.885667,140.874000,-3,True`
     - `A.CHOG,5550,41.327167,140.815333,0,True`
   - Practical usage: station inventory for network context; not needed for first-pass catalog geometry, but relevant if future agents need station coverage or matching checks.

#### Additional Directory Contents Relevant as Context
- `catalog/` also contains:
  - `Snet_catalog_20200101_20260522_filter.csv` — a larger filtered catalog spanning a broader time range than the relocated subset.
  - `Snet_catalog_relocate.csv`
  - `Snet_catalog_relocate_250930_260501.csv`
  - notebooks such as `catalog.ipynb`, `swarm_like.ipynb`
- `event_screen/` contains precomputed CSV outputs suggestive of prior M1-M3 screening workflows:
  - `m1_m3_event_chain_table.csv`
  - `m1_m3_event_geometry.csv`
  - `m1_m3_burst_table_raw.csv`
  - `m1_m3_burst_table_m2aware.csv`
  - `m1_m3_burst_summary.csv`
  - `m1_m3_depth_domain_summary.csv`
- These files may be useful for cross-checking prior work, but they appear to be derived products rather than raw inputs.

#### File Naming and Organization Patterns
- Catalog files follow date-window naming patterns, e.g.:
  - `Snet_catalog_relocate_250601_260501.csv` → likely relocated catalog from 2025-06-01 to 2026-05-01.
  - `Snet_catalog_relocate_250930_260501.csv` → alternate start-date subset.
- Mainshock/event-role labels use compact identifiers `M1`, `M2`, `M3` in `main_earthquake.csv`.
- Derived analysis products in `event_screen/` use descriptive prefixes such as `m1_m3_...`, indicating geometry tables, burst tables, and summaries.

#### Data Access Notes for Future Agents
- **Primary load sequence for this task**:
  1. Read `catalog/main_earthquake.csv` normally with headers.
  2. Read `catalog/Snet_catalog_relocate_250601_260501.csv` with `header=None` and assign names `['time','lat','lon','dep_km','mag']`.
  3. Optionally read `source_mechanism/Snet_mecha.csv` for focal mechanism follow-up.
  4. Optionally read `stations/station.sta` as CSV/text for station context.
- **Timestamp formats differ**:
  - relocated catalog uses ISO-like UTC strings with `T` and `Z`
  - mainshock table uses space-separated timestamps with fractional seconds
  - future agents should normalize both with pandas datetime parsing before any time-window logic.
- **Potential quality flag for inspection**:
  - the relocated catalog contains at least one very large `dep_km` value (`6221.0`), which is likely anomalous and worth checking during downstream QC, though no filtering should be assumed at the metadata stage.

#### Minimal Metadata Summary for Coding Use
- `catalog/Snet_catalog_relocate_250601_260501.csv`
  - schema: `time, lat, lon, dep_km, mag`
  - rows: 25,648
  - headerless CSV
- `catalog/main_earthquake.csv`
  - schema: `index, datetime, lat, lon, dep, mag`
  - rows: 3 (`M1`, `M2`, `M3`)
- `source_mechanism/Snet_mecha.csv`
  - schema: 29 columns, 354 rows, partial mechanism coverage
- `stations/station.sta`
  - schema: `station_code, station_number, latitude, longitude, elevation_m, matched`
  - ~371 station entries plus header

------------------------------

## Snet_catalog_relocate_250601_260501.csv
**Source path**: `data/Snet_catalog_relocate_250601_260501.csv`
### Summary
This directory contains the Aomori catalog inputs needed for an M1-M3 event-chain screening workflow: a headerless relocated earthquake catalog, a 3-row mainshock reference table, an optional focal-mechanism table, and station metadata. The relocated catalog provides only time, latitude, longitude, depth, and magnitude, so future agents must compute all M1/M2/M3-relative geometry and time-window fields themselves after loading it with explicit column names.
### Detail
#### Folder Structure
- Root path: `<CASE_ROOT>/data`
- Main subdirectories relevant to this task:
  - `catalog/` — earthquake catalogs and mainshock reference table
  - `source_mechanism/` — focal mechanism metadata
  - `stations/` — station inventory / coordinates
  - `event_screen/` — previously generated screening outputs already present in the workspace
  - `active_fault/` and `DEM/` — geographic context layers
- Example relevant paths:
  - `catalog/Snet_catalog_relocate_250601_260501.csv`
  - `catalog/main_earthquake.csv`
  - `source_mechanism/Snet_mecha.csv`
  - `stations/station.sta`

#### Primary Catalog File
- Path: `catalog/Snet_catalog_relocate_250601_260501.csv`
- Size: 1,506,736 bytes
- Format: **CSV with no header row**
- Recommended schema when loading:
  - `time`
  - `lat`
  - `lon`
  - `dep_km`
  - `mag`
- Shape: **25,648 rows × 5 columns**
- Example rows:
  - `2025-06-01T00:13:38.900000Z, 39.245593, 142.382422, 29.70, 1.7`
  - `2025-06-01T00:30:20.430000Z, 41.623617, 142.114681, 55.14, 1.7`
  - `2025-06-01T02:20:26.570000Z, 41.533988, 143.589616, 7.08, 1.7`
- Data types after correct loading:
  - `time`: string timestamp
  - `lat`, `lon`, `dep_km`, `mag`: float64
- Missing values: none detected in these five columns
- Temporal extent:
  - minimum: `2025-06-01T00:13:38.900000Z`
  - maximum: `2026-05-01T14:44:22.450000Z`
- Spatial / value ranges:
  - `lat`: 38.50304 to 42.382633
  - `lon`: 141.000635 to 144.49847
  - `dep_km`: 0.0 to 6221.0
  - `mag`: -0.5 to 7.7
- Important ingestion note:
  - If read with default `pandas.read_csv(...)`, the first event row will be misinterpreted as column headers. Future agents should use something like `pd.read_csv(path, header=None, names=['time','lat','lon','dep_km','mag'])`.
- Relevance to requested M1-M3 screening:
  - This file contains the raw event locations, depths, times, and magnitudes needed to derive:
    - time since M1
    - time before M3
    - distance to M1 / M3 / M2
    - along-axis projection and perpendicular distance to the M1-M3 corridor
    - local union/core/extended/corridor/off-corridor categories
    - M2-related flags
  - It does **not** contain event IDs, uncertainty fields, mechanism fields, or precomputed categories.

#### Mainshock Reference Table
- Path: `catalog/main_earthquake.csv`
- Size: 184 bytes
- Shape: **3 rows × 6 columns**
- Columns:
  - `index`
  - `datetime`
  - `lat`
  - `lon`
  - `dep`
  - `mag`
- Rows:
  - `M1, 2025-11-09 08:03:39.240, 39.402, 143.507, 15.9, 6.9`
  - `M2, 2025-12-08 14:15:10.180, 40.968, 142.288, 53.5, 7.5`
  - `M3, 2026-04-20 07:52:58.060, 39.842, 143.157, 19.4, 7.7`
- Missing values: none detected
- Relevance:
  - This is the authoritative table for M1/M2/M3 hypocenters and origin times.
  - Future agents will use it to define the fixed temporal windows and the endpoint/corridor geometry described in the task.

#### Optional Mechanism Context File
- Path: `source_mechanism/Snet_mecha.csv`
- Size: 61,681 bytes
- Shape: **354 rows × 29 columns**
- Columns include:
  - event metadata: `event_code`, `origin_time`, `lat_deg`, `lon_deg`, `depth_km`, `region_name`
  - magnitudes: `mag_1`, `mag_1_type`, `mag_2`, `mag_2_type`
  - source/method info: `n_hypo_stations`, `m_method`, `m_source`, `source_file`
  - focal geometry: `P_axis_azimuth`, `P_axis_dip`, `T_axis_azimuth`, `T_axis_dip`, `N_axis_azimuth`, `N_axis_dip`, `strike_plane1`, `dip_plane1`, `rake_plane1`, `strike_plane2`, `dip_plane2`, `rake_plane2`
  - quality / coverage: `focal_mech_score`, `n_mech_stations`, `focal_mech_projection`
- Missingness pattern:
  - Many mechanism-specific columns have 215 missing values, so full mechanism solutions are only available for a subset of rows.
- Relevance:
  - Useful for follow-up mechanism screening once candidate bursts or endpoint groups are identified.
  - Not required for first-pass event-chain geometry or rate-window construction.

#### Station Metadata
- Path: `stations/station.sta`
- Size: 16,102 bytes
- Format: text file with CSV-style comma-separated rows
- Total lines: 372 including header
- Header:
  - `station_code,station_number,latitude,longitude,elevation_m,matched`
- Example rows:
  - `A.ASMS,5572,40.885667,140.874000,-3,True`
  - `A.CHOG,5550,41.327167,140.815333,0,True`
- Relevance:
  - Provides station-network context for later quality-control or coverage checks.
  - Not needed to compute the requested event-chain geometry from the catalog alone.

#### Additional Existing Files in the Same Data Tree
- `event_screen/` already contains M1-M3-related derived tables such as:
  - `m1_m3_event_chain_table.csv`
  - `m1_m3_event_geometry.csv`
  - `m1_m3_burst_table_raw.csv`
  - `m1_m3_burst_table_m2aware.csv`
  - `m1_m3_burst_summary.csv`
  - `m1_m3_depth_domain_summary.csv`
- These appear to be prior analysis outputs rather than raw source inputs. Future agents may inspect them for cross-checking, but they should not be mistaken for the base catalog.

#### File Naming / Organization Patterns
- Catalog filenames use descriptive prefixes plus date windows, e.g. `Snet_catalog_relocate_250601_260501.csv`.
- Mainshock roles are encoded as `M1`, `M2`, `M3` in `main_earthquake.csv`.
- Derived screening outputs in `event_screen/` use consistent `m1_m3_...` prefixes, which makes them easy to discover by pattern.

#### Fields Most Relevant for Future M1-M3 Agents
- From the relocated catalog:
  - `time` — needed for baseline, M1-related, middle, pre-M3, and post-M3 windows
  - `lat`, `lon` — needed for distance-to-endpoint and corridor geometry
  - `dep_km` — needed for depth summaries and burst descriptions
  - `mag` — needed for M3+/M4+/M5+/M6+ threshold counts and rate comparisons
- From the mainshock table:
  - `datetime`, `lat`, `lon`, `dep`, `mag` for `M1`, `M2`, `M3`
- From mechanism and station files:
  - optional contextual enrichment only

#### Practical Loading Notes
- Use explicit column names for the relocated catalog because it is headerless.
- Normalize timestamps across files before any future screening:
  - relocated catalog uses ISO-like strings with `T` and trailing `Z`
  - `main_earthquake.csv` uses space-separated datetimes with fractional seconds
- The relocated catalog contains an extreme depth value (`6221.0 km`), which is metadata worth flagging for downstream QC even though no scientific filtering is done here.

#### Minimal Load Recipe Summary
- Required inputs for the event-chain task:
  - `catalog/Snet_catalog_relocate_250601_260501.csv` → raw events
  - `catalog/main_earthquake.csv` → M1/M2/M3 references
- Optional context:
  - `source_mechanism/Snet_mecha.csv`
  - `stations/station.sta`
- Recommended first-step schema:
  - events: `['time','lat','lon','dep_km','mag']`
  - mainshocks: `['index','datetime','lat','lon','dep','mag']`

------------------------------

## main_earthquake.csv
**Source path**: `catalog/main_earthquake.csv`
### Summary
This file is a compact 3-row reference table defining the three key earthquakes labeled M1, M2, and M3. It contains the origin time, hypocenter coordinates, depth, and magnitude needed to construct all time-window and distance-based geometry for future M1-M3 event-chain screening.
### Detail
#### File Overview
- Path: `catalog/main_earthquake.csv`
- Size: 184 bytes
- Format: standard CSV with header row
- Shape: **3 rows × 6 columns**
- Purpose: reference table for the three named events used as endpoints / controls in the event-chain workflow

#### Columns
- `index`
  - Type: object/string
  - Values in this file: `M1`, `M2`, `M3`
  - Role: symbolic event labels used throughout downstream logic
- `datetime`
  - Type: object/string as read directly
  - Format examples: `2025-11-09 08:03:39.240`
  - Role: mainshock origin times for defining baseline, M1-related, middle, pre-M3, and post-M3 windows
- `lat`
  - Type: float64
  - Role: epicentral latitude for distance and corridor calculations
- `lon`
  - Type: float64
  - Role: epicentral longitude for distance and corridor calculations
- `dep`
  - Type: float64
  - Units: kilometers (inferred from catalog conventions and numeric values)
  - Role: hypocentral depth for context and potential depth-domain comparisons
- `mag`
  - Type: float64
  - Role: event magnitude for identifying the three mainshocks and later threshold comparisons

#### Rows / Event Metadata
- `M1`
  - `datetime`: `2025-11-09 08:03:39.240`
  - `lat`: `39.402`
  - `lon`: `143.507`
  - `dep`: `15.9`
  - `mag`: `6.9`
- `M2`
  - `datetime`: `2025-12-08 14:15:10.180`
  - `lat`: `40.968`
  - `lon`: `142.288`
  - `dep`: `53.5`
  - `mag`: `7.5`
- `M3`
  - `datetime`: `2026-04-20 07:52:58.060`
  - `lat`: `39.842`
  - `lon`: `143.157`
  - `dep`: `19.4`
  - `mag`: `7.7`

#### Data Quality / Completeness
- No missing values detected in any column.
- All rows are unique and correspond to one labeled main event each.
- Because the file is very small, it can be loaded directly with standard CSV readers without special handling.

#### Relevance to the M1-M3 Event-Chain Workflow
- This file is the anchor metadata for future derived fields such as:
  - time since M1
  - time before M3
  - distance to M1 / M3
  - distance to M2 for M2-aware flagging
  - projected distance along the M1-M3 axis
  - perpendicular distance to the M1-M3 axis
- It is also required for defining the fixed temporal windows requested by the task:
  - pre-M1 baseline ending at `M1 - 14d` and `M1 - 7d`
  - M1-related dominated phase from `M1 - 14d` to `M1 + 21d`
  - middle phase from `M1 + 21d` to `M3 - 35d`
  - pre-M3 local activation phase from `M3 - 35d` to `M3`
  - optional post-M3 context windows

#### Geometry Use Notes
- `M1` and `M3` are the two endpoint events for the primary local-union and corridor geometry.
- `M2` is not part of the M1-M3 axis definition, but its coordinates are needed for the requested `within 100 km of M2` flag or ambiguity check.
- Since only latitude/longitude are given, future agents must compute geodesic or local-projected distances themselves.

#### Loading Notes
- Standard `pandas.read_csv` is sufficient.
- Recommended post-load steps for future agents:
  - parse `datetime` to a timestamp type
  - set `index` as a categorical label or lookup key
  - extract M1, M2, and M3 rows by `index`

#### Minimal Example Schema for Coding Agents
- DataFrame columns:
  - `index` (string)
  - `datetime` (parse to datetime64)
  - `lat` (float)
  - `lon` (float)
  - `dep` (float)
  - `mag` (float)
- Canonical lookup labels present:
  - `M1`
  - `M2`
  - `M3`

------------------------------

## Snet_mecha.csv
**Source path**: `source_mechanism/Snet_mecha.csv`
### Summary
This file is an optional focal-mechanism catalog containing 354 events with event metadata, magnitudes, region names, station counts, stress-axis parameters, nodal planes, and mechanism-quality fields. It is useful for later follow-up mechanism screening of M1-M3 bursts or endpoint groups, but only a subset of rows has complete mechanism solutions.
### Detail
#### File Overview
- Path: `source_mechanism/Snet_mecha.csv`
- Size: 61,681 bytes
- Format: standard CSV with header row
- Shape: **354 rows × 29 columns**
- Role in workflow: optional context file for mechanism-based follow-up after spatial-temporal event-chain screening

#### Columns
- Event identification / timing / location:
  - `event_code` — string event identifier
  - `origin_time` — event origin timestamp string
  - `lat_deg` — latitude in degrees
  - `lon_deg` — longitude in degrees
  - `depth_km` — depth in km
  - `region_name` — textual region label
- Magnitudes:
  - `mag_1` — primary magnitude value
  - `mag_1_type` — primary magnitude type code
  - `mag_2` — secondary magnitude value (often missing)
  - `mag_2_type` — secondary magnitude type code (often missing)
- Source / method / station metadata:
  - `n_hypo_stations` — number of stations used for hypocenter
  - `m_method` — mechanism method code
  - `m_source` — mechanism source code
  - `n_mech_stations` — number of stations contributing to mechanism solution
  - `source_file` — original source text filename
- Principal axes:
  - `P_axis_azimuth`, `P_axis_dip`
  - `T_axis_azimuth`, `T_axis_dip`
  - `N_axis_azimuth`, `N_axis_dip`
- Nodal planes:
  - `strike_plane1`, `dip_plane1`, `rake_plane1`
  - `strike_plane2`, `dip_plane2`, `rake_plane2`
- Quality / representation:
  - `focal_mech_score`
  - `focal_mech_projection`

#### Data Types
- String/object fields:
  - `event_code`, `origin_time`, `mag_1_type`, `mag_2_type`, `region_name`, `m_method`, `m_source`, `focal_mech_projection`, `source_file`
- Numeric fields:
  - `lat_deg`, `lon_deg`, `depth_km`, `mag_1`, `mag_2`, `n_hypo_stations`, all axis and plane parameters, `focal_mech_score`, `n_mech_stations`

#### Sample Metadata
- First rows show event codes like `J2025100111563882`, origin times in `YYYY-MM-DD HH:MM:SS.sss` format, and region names such as `S OFF URAKAWA` and `KINKAZAN REGION`.
- Example fields present in one complete row include:
  - location/depth/magnitude
  - principal stress axes
  - both nodal planes
  - quality score and station counts
  - low-level projection label and source filename such as `mecha_20251001_7.txt`

#### Missingness / Completeness
- Several mechanism-specific columns are sparse.
- Missing-value counts observed:
  - `mag_2`: 215 missing
  - `mag_2_type`: 215 missing
  - `m_method`: 215 missing
  - `m_source`: 215 missing
  - `P_axis_azimuth`, `P_axis_dip`: 215 missing each
  - `T_axis_azimuth`, `T_axis_dip`: 215 missing each
  - `N_axis_azimuth`, `N_axis_dip`: 215 missing each
  - `strike_plane1`, `dip_plane1`, `rake_plane1`: 215 missing each
  - `strike_plane2`, `dip_plane2`, `rake_plane2`: 215 missing each
  - `focal_mech_score`: 215 missing
  - `n_mech_stations`: 215 missing
  - `focal_mech_projection`: 215 missing
- Fully populated fields include:
  - `event_code`, `origin_time`, `lat_deg`, `lon_deg`, `depth_km`, `mag_1`, `mag_1_type`, `region_name`, `n_hypo_stations`, `source_file`
- Interpretation for future agents:
  - The file contains a mix of events with and without full focal-mechanism solutions.
  - Mechanism-based subgrouping should therefore be treated as subset analysis rather than full-catalog coverage.

#### Relevance to the M1-M3 Task
- Most relevant fields for later follow-up screening:
  - `origin_time`, `lat_deg`, `lon_deg`, `depth_km`, `mag_1` for matching mechanism events to the relocated catalog in time/space
  - `strike_plane1`, `dip_plane1`, `rake_plane1`, `strike_plane2`, `dip_plane2`, `rake_plane2` for focal-plane comparisons
  - `P_axis_*`, `T_axis_*`, `N_axis_*` for simplified axis-based mechanism grouping
  - `focal_mech_score`, `n_mech_stations`, `focal_mech_projection` for quality assessment
- This file does **not** define M1/M2/M3 windows or corridor geometry by itself.
- It is best used after candidate bursts, endpoint clusters, or corridor segments have already been identified from the main relocated catalog.

#### Joining / Matching Considerations
- There is no obvious direct shared event ID with the headerless relocated catalog, which only contains time/location/depth/magnitude.
- Future agents will likely need to match mechanism entries to relocated events by combinations of:
  - `origin_time`
  - `lat_deg`
  - `lon_deg`
  - `depth_km`
  - `mag_1`
- Because magnitudes may differ by type and rounding, time-space matching may be more reliable than exact magnitude equality.

#### Value / Coverage Characteristics
- Geographic coverage appears regional rather than restricted to the M1-M3 local domain.
- Magnitudes include moderate events (examples include 3.3 to 4.6 in the preview), but the full range was not exhaustively summarized here.
- `n_hypo_stations` is fully populated and may be useful as a basic confidence/context field.
- `focal_mech_projection` includes categorical labels such as `LOW` where present.

#### Practical Use Notes for Future Agents
- Load normally with `pandas.read_csv`.
- Parse `origin_time` to datetime before any matching with the relocated catalog.
- Expect mechanism columns to be missing for many rows; filter on non-null mechanism fields before doing nodal-plane or stress-axis summaries.
- Treat mechanism interpretations as optional catalog-level context, not as required inputs for the initial M1-M3 event-chain screening.

#### Minimal Coding Summary
- Rows: 354
- Columns: 29
- Core useful columns for follow-up:
  - `event_code`
  - `origin_time`
  - `lat_deg`, `lon_deg`, `depth_km`
  - `mag_1`, `mag_1_type`
  - `region_name`
  - `strike_plane1`, `dip_plane1`, `rake_plane1`
  - `strike_plane2`, `dip_plane2`, `rake_plane2`
  - `P_axis_azimuth`, `P_axis_dip`, `T_axis_azimuth`, `T_axis_dip`
  - `focal_mech_score`, `n_mech_stations`
- Best role: secondary enrichment file for mechanism screening of catalog-defined bursts, endpoint clusters, or corridor activity

------------------------------

## station.sta
**Source path**: `stations/station.sta`
### Summary
This file is a station inventory in comma-separated text format with station codes, numeric IDs, coordinates, elevation, and a boolean match flag. It provides network context for later quality-control or coverage checks, but it is not required for the first-pass M1-M3 catalog geometry or time-window calculations.
### Detail
#### File Overview
- Path: `stations/station.sta`
- Size: 16,102 bytes
- Format: plain text with comma-separated fields and a header row
- Total lines: **372** including header
- Approximate number of station entries: **371**
- Role in workflow: station metadata / network context

#### Header / Schema
The file begins with the header:
- `station_code,station_number,latitude,longitude,elevation_m,matched`

Column descriptions:
- `station_code`
  - Type: string
  - Example: `A.ASMS`, `A.CHOG`
  - Role: station identifier
- `station_number`
  - Type: integer-like identifier
  - Example: `5572`, `5550`
  - Role: numeric station code / catalog reference
- `latitude`
  - Type: float
  - Units: decimal degrees
  - Role: station position
- `longitude`
  - Type: float
  - Units: decimal degrees
  - Role: station position
- `elevation_m`
  - Type: integer/float
  - Units: meters
  - Example values include negative elevations
  - Role: station elevation context
- `matched`
  - Type: boolean-like text (`True` shown in preview)
  - Role: indicates whether the station was matched in a prior workflow step

#### Sample Rows
First few lines of the file:
- `A.ASMS,5572,40.885667,140.874000,-3,True`
- `A.CHOG,5550,41.327167,140.815333,0,True`
- `A.HGTZ,5571,40.982833,140.904000,-11,True`
- `A.HRDA,5549,41.448833,140.881000,2,True`

#### Content Characteristics
- The file appears to be a simple station list rather than waveform or pick metadata.
- Coordinates are given directly in latitude/longitude and can be read without format conversion beyond CSV parsing.
- Elevation includes negative and near-zero values, consistent with coastal/offshore or datum-referenced stations.
- The `matched` column suggests these stations were cross-referenced against another source in a prior processing step.

#### Relevance to the M1-M3 Catalog Task
- Directly **not required** for computing the requested event-chain fields such as:
  - time since M1
  - time before M3
  - distance to M1/M2/M3
  - along-axis and perpendicular corridor distance
  - endpoint/core/corridor/off-corridor categories
- Potential indirect uses for future agents:
  - station coverage/context when interpreting catalog completeness qualitatively
  - checking whether endpoint or corridor regions are well represented by nearby stations
  - documenting network geometry for later mechanism or relocation follow-up

#### Recommended Parsing
- Can be loaded with standard CSV readers, e.g. `pandas.read_csv(...)`.
- Suggested inferred types:
  - `station_code`: string
  - `station_number`: integer
  - `latitude`, `longitude`: float
  - `elevation_m`: numeric
  - `matched`: boolean or string-to-bool conversion

#### Relationship to Other Files
- Most closely related to:
  - `catalog/Snet_catalog_relocate_250601_260501.csv` for general catalog context
  - `source_mechanism/Snet_mecha.csv` if future agents evaluate whether mechanism coverage depends on station distribution
- It does not appear to share event-level keys with the catalog files; it is a station-level reference table only.

#### Minimal Coding Summary
- Rows: ~371 stations
- Columns: 6
- Core fields:
  - `station_code`
  - `station_number`
  - `latitude`
  - `longitude`
  - `elevation_m`
  - `matched`
- Best role: optional station/network context file for later QC, coverage discussion, or follow-up analyses

------------------------------

