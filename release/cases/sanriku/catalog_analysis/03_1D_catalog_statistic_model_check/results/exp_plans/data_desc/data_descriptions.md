# Data Descriptions
## data
**Source path**: `<CASE_ROOT>/data`
### Summary
This data folder is organized around a filtered Aomori-region earthquake catalog, a small mainshock table for M1-M3, and optional contextual datasets for focal mechanisms, stations, faults, and topography. For the requested b-value/rate workflow, the key inputs are a 227,755-row CSV catalog with time-location-magnitude fields, a 3-row mainshock reference table, a 354-row focal-mechanism CSV with many mechanism attributes, and a 372-line station list file.
### Detail
#### Folder Structure
- Root path: `<CASE_ROOT>/data`
- Main subdirectories relevant to future agents:
  - `catalog/` — primary earthquake catalog files and notebook context
  - `source_mechanism/` — focal mechanism table(s)
  - `stations/` — station metadata
  - `active_fault/` — regional fault geometry (`.geojson`)
  - `DEM/` — raster/topography support files
  - `event_screen/` — precomputed screening/event-summary tables
- Notebooks and figures are present for context, but the core analysis-ready inputs for the requested task are the files below.

#### Priority Files for M1-M3 Catalog Profiling
1. **Filtered catalog**  
   Path: `catalog/Snet_catalog_20200101_20260522_filter.csv`
2. **Mainshock table**  
   Path: `catalog/main_earthquake.csv`
3. **Optional focal mechanisms**  
   Path: `source_mechanism/Snet_mecha.csv`
4. **Optional stations**  
   Path: `stations/station.sta`

#### File Statistics
##### 1) Filtered catalog: `catalog/Snet_catalog_20200101_20260522_filter.csv`
- Format: CSV
- Size: `10,848,049` bytes
- Shape: `227,755 rows × 5 columns`
- Columns:
  - `datetime` (`object`) — event origin time as text timestamp
  - `lat` (`float64`) — latitude
  - `lon` (`float64`) — longitude
  - `dep` (`float64`) — depth, likely km
  - `mag` (`float64`) — magnitude
- Missing values: none in any column
- Preview pattern:
  - Example timestamps include fractional seconds, e.g. `2019-12-31 15:26:23.330`
  - Example spatial values near offshore NE Japan/Aomori region
- Notes for loading:
  - Read with standard `pandas.read_csv`
  - `datetime` should be parsed explicitly to datetime in downstream workflows
  - This is the main file for time-windowed Mc, b-value, and event-rate calculations
- Important naming note:
  - The filename suggests `20200101_20260522`, but the first visible rows include times on `2019-12-31`; future agents should inspect actual min/max time after parsing rather than relying only on filename

##### 2) Mainshock table: `catalog/main_earthquake.csv`
- Format: CSV
- Size: `184` bytes
- Shape: `3 rows × 6 columns`
- Columns:
  - `index` (`object`) — event label
  - `datetime` (`object`) — mainshock time
  - `lat` (`float64`)
  - `lon` (`float64`)
  - `dep` (`float64`)
  - `mag` (`float64`)
- Missing values: none
- Contents:
  - `M1` — `2025-11-09 08:03:39.240`, `(39.402, 143.507)`, depth `15.9`, mag `6.9`
  - `M2` — `2025-12-08 14:15:10.180`, `(40.968, 142.288)`, depth `53.5`, mag `7.5`
  - `M3` — `2026-04-20 07:52:58.060`, `(39.842, 143.157)`, depth `19.4`, mag `7.7`
- Use:
  - Direct reference for phase boundaries and map annotation
  - Small enough to load manually or with pandas

##### 3) Focal mechanism table: `source_mechanism/Snet_mecha.csv`
- Format: CSV
- Size: `61,681` bytes
- Shape: `354 rows × 29 columns`
- Main columns:
  - Event identifiers and origin info:
    - `event_code`, `origin_time`, `lat_deg`, `lon_deg`, `depth_km`
  - Magnitudes and types:
    - `mag_1`, `mag_1_type`, `mag_2`, `mag_2_type`
  - Region / metadata:
    - `region_name`, `n_hypo_stations`, `m_method`, `m_source`, `source_file`
  - Principal axes:
    - `P_axis_azimuth`, `P_axis_dip`, `T_axis_azimuth`, `T_axis_dip`, `N_axis_azimuth`, `N_axis_dip`
  - Nodal planes:
    - `strike_plane1`, `dip_plane1`, `rake_plane1`, `strike_plane2`, `dip_plane2`, `rake_plane2`
  - Quality/support:
    - `focal_mech_score`, `n_mech_stations`, `focal_mech_projection`
- Missingness pattern:
  - Many mechanism-specific fields have `215` nulls, so only a subset of rows contains full mechanism solutions
  - Basic event metadata columns are complete
- Use:
  - Optional context for interpreting selected M1/M3-region events
  - Not necessary for baseline b-value/rate processing, but useful for follow-up filtering or mechanism summaries

##### 4) Station list: `stations/station.sta`
- Format: text/CSV-like plain text
- Size: `16,102` bytes
- Lines: `372`
- Header:
  - `station_code,station_number,latitude,longitude,elevation_m,matched`
- Example records:
  - `A.ASMS,5572,40.885667,140.874000,-3,True`
- Use:
  - Station map/context only
  - Can be read with `pandas.read_csv` despite `.sta` extension

#### Additional Context Files
- `active_fault/japan_active_faults.geojson`
  - Likely regional active fault geometry for map overlays
- `DEM/output_hh.tif` and `DEM/rasters_COP30.tar.gz`
  - Topographic background data
- `event_screen/*.csv`
  - Includes precomputed event-screening summaries such as:
    - `m1_m3_burst_summary.csv`
    - `m1_m3_burst_table_m2aware.csv`
    - `m1_m3_depth_domain_summary.csv`
    - `m1_m3_event_chain_table.csv`
    - `m1_m3_event_geometry.csv`
  - These appear to be derived/context tables rather than primary catalog inputs
- `catalog/Snet_catalog_relocate*.csv`
  - Additional catalog variants are present, but the user-prioritized file is the filtered catalog above

#### Organization and Naming Conventions
- Catalog file names follow descriptive patterns with embedded date ranges and processing tags, e.g.:
  - `Snet_catalog_20200101_20260522_filter.csv`
  - `Snet_catalog_relocate_250601_260501.csv`
- Main event labels use compact identifiers `M1`, `M2`, `M3`
- Contextual event-screen outputs use `m1_m3_*` prefixes, indicating prior work focused on the same event system
- Example paths:
  - `/.../data/catalog/Snet_catalog_20200101_20260522_filter.csv`
  - `/.../data/catalog/main_earthquake.csv`
  - `/.../data/source_mechanism/Snet_mecha.csv`
  - `/.../data/stations/station.sta`

#### Recommended Loading Order for Future Agents
1. Load `catalog/main_earthquake.csv` to obtain M1/M2/M3 coordinates and times.
2. Load `catalog/Snet_catalog_20200101_20260522_filter.csv` as the primary event catalog.
3. Parse `datetime` and confirm true temporal extent from data values.
4. Optionally load `source_mechanism/Snet_mecha.csv` for event-level mechanism context near M1/M3.
5. Optionally load `stations/station.sta` and `active_fault/japan_active_faults.geojson` for map support.

#### Practical Notes for Downstream Use
- The filtered catalog is compact and analysis-ready: one event per row with only the fields needed for spatial-temporal filtering and magnitude-frequency work.
- The mainshock table is already normalized and small enough for direct use in plotting phase markers and constructing M1/M3-centered subregions.
- Mechanism data are sparse relative to the full catalog, so they should be treated as optional context rather than a complete companion table.
- Station and fault/DEM files are auxiliary and mainly useful for geographic visualization or contextual overlays rather than core catalog statistics.

------------------------------

## Snet_catalog_20200101_20260522_filter.csv
**Source path**: `data/catalog/Snet_catalog_20200101_20260522_filter.csv`
### Summary
This is the primary analysis-ready earthquake catalog for the Aomori workflow: a single CSV with 227,755 events and the core fields needed for spatiotemporal filtering and magnitude-frequency analysis. It contains complete `datetime`, `lat`, `lon`, `dep`, and `mag` columns with no missing values, spanning late 2019 through 2026-05-22 and covering a broad NE Japan offshore/onshore region around the M1-M3 system.
### Detail
#### File Overview
- Path: `<CASE_ROOT>/data/catalog/Snet_catalog_20200101_20260522_filter.csv`
- Format: CSV
- Size: approximately `10.85 MB`
- Shape: `227,755 rows × 5 columns`
- Purpose in workflow:
  - Primary earthquake-event table for constructing study-area subsets
  - Supports event-rate, Mc, and b-value calculations after temporal/spatial filtering
  - Suitable for M1/M3-centered and oriented-region selection because it already contains only essential event attributes

#### Columns and Types
- `datetime` — `object` in raw CSV; should be parsed to datetime
- `lat` — `float64`
- `lon` — `float64`
- `dep` — `float64`
- `mag` — `float64`

#### Data Completeness
- Missing values:
  - `datetime`: `0`
  - `lat`: `0`
  - `lon`: `0`
  - `dep`: `0`
  - `mag`: `0`
- Duplicate full rows: `0`

#### Temporal Coverage
- Parsed minimum time: `2019-12-31 15:26:23.330000`
- Parsed maximum time: `2026-05-22 14:41:14.740000`
- Important note:
  - Although the filename starts with `20200101`, the actual table includes a small number of events from `2019-12-31`.
  - Future agents should use parsed datetimes rather than filename assumptions when defining the pre-M1 baseline.
- Event counts by year:
  - `2019`: `22`
  - `2020`: `30,354`
  - `2021`: `33,677`
  - `2022`: `33,594`
  - `2023`: `32,160`
  - `2024`: `32,411`
  - `2025`: `42,363`
  - `2026`: `23,174`
- Interpretation for future loading:
  - Temporal sampling is dense enough for fixed-count sliding windows at catalog scale.
  - Year 2025 has elevated counts relative to earlier years, which may matter when choosing temporal subsets or plotting densities.

#### Spatial Coverage Metadata
- `lat` range: `38.001` to `42.999`
- `lon` range: `140.001` to `145.999`
- Mean location:
  - latitude `39.9876`
  - longitude `142.3668`
- Median location:
  - latitude `39.757`
  - longitude `142.281`
- Practical implication:
  - The file spans a broad rectangular region that is wider than the targeted M1-M3 system, so future agents will need spatial subsetting to isolate the oriented study area and avoid unrelated clusters.

#### Depth and Magnitude Metadata
- `dep` range: `0.0` to `196.0`
- `dep` mean: `32.1499`
- `dep` median: `27.1`
- `mag` range: `-1.0` to `7.7`
- `mag` mean: `1.2006`
- `mag` median: `1.1`
- Notes:
  - Magnitudes include many small events below 0, indicating a low-threshold catalog.
  - The upper tail includes major events consistent with the M1-M3 context.
  - Because the catalog contains many low-magnitude events, Mc estimation will be necessary before any b-value work, but this file itself is adequate for that step.

#### Magnitude Distribution Snapshot
- Lower-end counts (rounded to 0.1 units) show dense small-event sampling:
  - `-1.0`: `5`
  - `-0.9`: `11`
  - `-0.8`: `22`
  - `-0.7`: `45`
  - `-0.6`: `77`
  - `-0.5`: `165`
  - `-0.4`: `341`
  - `-0.3`: `652`
  - `-0.2`: `1,044`
  - `-0.1`: `1,921`
  - `0.0`: `2,901`
  - `0.1`: `3,920`
  - `0.2`: `5,175`
  - `0.3`: `6,355`
  - `0.4`: `7,711`
- Upper-tail rounded counts include:
  - `5.6`: `11`
  - `5.7`: `8`
  - `5.8`: `5`
  - `5.9`: `6`
  - `6.0`: `5`
  - `6.1`: `6`
  - `6.2`: `6`
  - `6.4`: `2`
  - `6.5`: `1`
  - `6.6`: `2`
  - `6.7`: `1`
  - `6.8`: `1`
  - `6.9`: `3`
  - `7.5`: `1`
  - `7.7`: `1`
- Practical implication:
  - The catalog supports both background seismicity characterization and inclusion of major events, but large-magnitude counts are sparse as expected.

#### Record Structure Example
Example rows follow a simple one-event-per-line format:
- `2019-12-31 15:26:23.330, 41.683, 142.956, 32.7, 1.7`
- `2019-12-31 15:49:03.770, 40.125, 141.216, 8.1, 1.2`
- `2019-12-31 15:49:27.280, 41.686, 142.968, 34.8, 1.3`

#### Access and Loading Notes
- Standard load pattern:
  - `pandas.read_csv(...)`
  - then `pd.to_datetime(df['datetime'])`
- No special encoding or multi-header structure was detected.
- The table is already tidy and normalized:
  - one event per row
  - no nested columns
  - no obvious duplicate rows
- This makes it straightforward for future agents to:
  - subset by time phase
  - subset by radius around M1/M3
  - subset by oriented polygon/ellipse after geometry construction
  - compute event counts and magnitude-frequency statistics

#### Relevance to the Requested Workflow
For the M1-M3 b-value and rate study, this file contains exactly the core fields needed:
- `datetime` for phase definitions and sliding event windows
- `lat`, `lon` for oriented study-area selection and M1/M3-centered circles
- `dep` for optional depth screening or map coloring
- `mag` for Mc and b-value estimation

#### Cautions for Future Agents
- Do not rely only on the filename for the catalog start time; the actual data begin slightly before 2020-01-01.
- The broad spatial bounds imply that unrelated clusters may be present, so the catalog should be spatially restricted before interpreting rate or b-value changes around M1-M3.
- Because magnitudes extend well below 0, magnitude completeness likely varies in space/time; any downstream b-value workflow should explicitly estimate Mc per subset/window rather than assume a fixed threshold.

------------------------------

## main_earthquake.csv
**Source path**: `catalog/main_earthquake.csv`
### Summary
This is a compact reference table containing the three key large events labeled M1, M2, and M3. It provides event names, origin times, epicenters, depths, and magnitudes, making it the primary lookup file for defining temporal phase markers and M1/M3-centered spatial subsets in later analyses.
### Detail
#### File Overview
- Path: `<CASE_ROOT>/data/catalog/main_earthquake.csv`
- Format: CSV
- Size: `184` bytes
- Shape: `3 rows × 6 columns`
- Role in workflow:
  - Defines the key reference events used to anchor the M1-M3 study
  - Supplies exact timestamps for phase boundaries
  - Supplies coordinates for M1/M3-centered radius selections and map annotation

#### Columns and Types
- `index` — `object`
  - Event label identifier
  - Values present: `M1`, `M2`, `M3`
- `datetime` — `object`
  - Origin time as timestamp string with fractional seconds
  - Should be parsed to datetime in downstream workflows
- `lat` — `float64`
  - Epicentral latitude
- `lon` — `float64`
  - Epicentral longitude
- `dep` — `float64`
  - Depth, likely km
- `mag` — `float64`
  - Magnitude

#### Data Completeness
- Missing values: none in any column
- Duplicate rows: not indicated; table is only 3 rows and appears unique by event label
- The table is already tidy and ready for direct use

#### Event Records
The file contains exactly three labeled events:
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

#### Relevance to the Requested Workflow
This file is the main metadata source for defining the requested temporal and spatial framework:
- **Temporal framework**
  - `M1` time is required to define:
    - pre-M1 reference
    - M1-related phase start/end
  - `M3` time is required to define:
    - final pre-M3 phase
    - post-M3 context
  - `M2` can be used as an intermediate annotation line in time-series figures
- **Spatial framework**
  - `M1` and `M3` coordinates define the axis for an oriented M1-M3 study region
  - `M1` and `M3` are also the centers for the requested 60 km and 80 km subregions

#### Practical Loading Notes
- Standard loading: `pandas.read_csv(...)`
- Recommended follow-up conversion:
  - parse `datetime` with `pd.to_datetime(...)`
- The file is small enough for manual inspection or direct conversion to a dictionary/indexed structure
- Example usage pattern after loading:
  - set `index` as the DataFrame index for direct access to `M1`, `M2`, `M3`

#### Record Structure Example
Each row is a single named event with the format:
- `index, datetime, lat, lon, dep, mag`

Example entries:
- `M1, 2025-11-09 08:03:39.240, 39.402, 143.507, 15.9, 6.9`
- `M3, 2026-04-20 07:52:58.060, 39.842, 143.157, 19.4, 7.7`

#### Notes for Future Agents
- This is a reference table, not a catalog; it should be joined conceptually with the main event catalog rather than analyzed on its own.
- Because the file contains exact event coordinates and times, it should be loaded first in any future workflow that constructs:
  - oriented M1-M3 boundaries
  - phase markers in plots
  - M1/M3-centered distance filters
- No additional preprocessing appears necessary beyond datetime parsing.

------------------------------

## Snet_mecha.csv
**Source path**: `source_mechanism/Snet_mecha.csv`
### Summary
This is an optional focal-mechanism context table with 354 events and 29 columns covering event metadata, magnitudes, principal axes, nodal planes, and quality/support fields. It is useful for follow-up interpretation of selected M1-M3-region events, but many mechanism-specific columns are only populated for a subset of rows, so it should not be treated as a complete companion catalog.
### Detail
#### File Overview
- Path: `<CASE_ROOT>/data/source_mechanism/Snet_mecha.csv`
- Format: CSV
- Size: `61,681` bytes
- Shape: `354 rows × 29 columns`
- Role in workflow:
  - Optional event-level context for mechanism style and source metadata
  - Potentially useful for inspecting selected larger or spatially focused events near M1/M3
  - Not required for core b-value, Mc, or event-rate estimation

#### Columns and Types
##### Event identity and hypocenter
- `event_code` — `object`
- `origin_time` — `object`
- `lat_deg` — `float64`
- `lon_deg` — `float64`
- `depth_km` — `float64`

##### Magnitude fields
- `mag_1` — `float64`
- `mag_1_type` — `object`
- `mag_2` — `float64`
- `mag_2_type` — `object`

##### Region and source metadata
- `region_name` — `object`
- `n_hypo_stations` — `int64`
- `m_method` — `object`
- `m_source` — `object`
- `source_file` — `object`

##### Principal stress/strain axes style metadata
- `P_axis_azimuth` — `float64`
- `P_axis_dip` — `float64`
- `T_axis_azimuth` — `float64`
- `T_axis_dip` — `float64`
- `N_axis_azimuth` — `float64`
- `N_axis_dip` — `float64`

##### Nodal plane parameters
- `strike_plane1` — `float64`
- `dip_plane1` — `float64`
- `rake_plane1` — `float64`
- `strike_plane2` — `float64`
- `dip_plane2` — `float64`
- `rake_plane2` — `float64`

##### Quality / support fields
- `focal_mech_score` — `float64`
- `n_mech_stations` — `float64`
- `focal_mech_projection` — `object`

#### Data Completeness
Columns with no missing values:
- `event_code`
- `origin_time`
- `lat_deg`
- `lon_deg`
- `depth_km`
- `mag_1`
- `mag_1_type`
- `region_name`
- `n_hypo_stations`
- `source_file`

Columns with substantial missingness (`215` nulls each out of 354 rows):
- `mag_2`
- `mag_2_type`
- `m_method`
- `m_source`
- `P_axis_azimuth`
- `P_axis_dip`
- `T_axis_azimuth`
- `T_axis_dip`
- `N_axis_azimuth`
- `N_axis_dip`
- `strike_plane1`
- `dip_plane1`
- `rake_plane1`
- `strike_plane2`
- `dip_plane2`
- `rake_plane2`
- `focal_mech_score`
- `n_mech_stations`
- `focal_mech_projection`

Practical implication:
- Only about `139` rows appear to contain the fuller mechanism solution set.
- Basic event metadata are complete, but full focal mechanism usage requires filtering to rows with populated mechanism fields.

#### Record Structure Example
Each row represents one event with event metadata and, where available, a focal mechanism solution.

Example fields seen in preview rows:
- `event_code`: e.g. `J2025100111563882`
- `origin_time`: e.g. `2025-10-01 02:56:38.820`
- `lat_deg`, `lon_deg`, `depth_km`
- `mag_1`, `mag_1_type`
- `mag_2`, `mag_2_type` (sometimes missing)
- `region_name`: descriptive location name
- `n_hypo_stations`: number of hypocenter stations
- mechanism axes and nodal plane parameters when available
- `focal_mech_projection`: e.g. `LOW` in preview rows
- `source_file`: e.g. `mecha_20251001_7.txt`

#### Example Content Pattern
Preview rows show that:
- event identifiers are catalog-style strings beginning with `J...`
- times include fractional seconds
- region names are textual geographic descriptions (for example, offshore regional names)
- `mag_1_type` and `mag_2_type` store magnitude code labels
- `source_file` tracks the original mechanism text file source

#### Relevance to the Requested M1-M3 Workflow
This file is best treated as optional context rather than a primary analysis input.

Useful fields for future agents:
- `origin_time` — for matching to the main catalog in time
- `lat_deg`, `lon_deg`, `depth_km` — for spatial matching near M1/M3 or within the oriented study area
- `mag_1`, `mag_2` — for identifying larger/context events
- `strike_plane1`, `dip_plane1`, `rake_plane1`, `strike_plane2`, `dip_plane2`, `rake_plane2` — for any mechanism-style follow-up
- `focal_mech_score`, `n_mech_stations`, `focal_mech_projection` — for basic quality screening

Less central to the requested task:
- It is not needed to compute b-value, Mc, or event rate.
- It may help annotate whether major/context events in the study region have available mechanism information.

#### Recommended Loading and Filtering Notes
- Load with `pandas.read_csv(...)`
- Parse `origin_time` to datetime explicitly
- For mechanism-only subsets, filter on non-null values in one or more of:
  - `strike_plane1`
  - `rake_plane1`
  - `focal_mech_score`
- If joining to the main catalog, use approximate time-space matching rather than assuming identical event IDs, unless a direct ID relationship has been verified elsewhere

#### Cautions for Future Agents
- Do not assume every row contains a full focal mechanism solution.
- Do not use this file as a replacement for the main event catalog; it is sparse and specialized.
- Mechanism quality/support metadata exist, but completeness is limited, so any mechanism-based summary around M1/M3 should report the reduced sample size.

#### Example Path for Access
- `<CASE_ROOT>/data/source_mechanism/Snet_mecha.csv`

------------------------------

## station.sta
**Source path**: `stations/station.sta`
### Summary
This is an auxiliary station metadata file stored as plain text with a CSV-style header and 372 lines total. It lists station code, station number, coordinates, elevation, and a boolean match flag, and is mainly useful for map context or checking network coverage rather than for direct b-value or rate calculations.
### Detail
#### File Overview
- Path: `<CASE_ROOT>/data/stations/station.sta`
- Format: plain-text, comma-separated table despite the `.sta` extension
- Size: `16,102` bytes
- Total lines: `372`
- Role in workflow:
  - Optional station-location context for plotting or network-coverage interpretation
  - Not required for the core catalog-based computations of event rate, Mc, or b-value

#### Table Structure
The file begins with a standard comma-separated header:
- `station_code`
- `station_number`
- `latitude`
- `longitude`
- `elevation_m`
- `matched`

This indicates the file can be loaded directly with a CSV reader such as `pandas.read_csv(...)`.

#### Column Meanings
- `station_code`
  - Text station identifier
  - Example format: `A.ASMS`, `A.CHOG`
- `station_number`
  - Numeric station ID
- `latitude`
  - Station latitude in decimal degrees
- `longitude`
  - Station longitude in decimal degrees
- `elevation_m`
  - Elevation in meters
  - Can include negative values, likely for near-sea-level or offshore/low-elevation sites
- `matched`
  - Boolean-like field (`True` seen in preview)
  - Likely indicates successful matching to another station inventory or working subset

#### Previewed Content Pattern
First rows inspected:
- `A.ASMS,5572,40.885667,140.874000,-3,True`
- `A.CHOG,5550,41.327167,140.815333,0,True`
- `A.HGTZ,5571,40.982833,140.904000,-11,True`
- `A.HRDA,5549,41.448833,140.881000,2,True`

This suggests:
- decimal-degree coordinates
- one station per row
- simple, analysis-friendly formatting

#### Relevance to the Requested M1-M3 Workflow
For the requested long-period b-value and seismicity-rate study, this file is secondary support only.

Potential uses for future agents:
- add station markers to study-area maps
- visually compare event distribution with network geometry
- provide context when discussing possible catalog-quality differences across space

Less relevant for primary analysis:
- does not contain event times, magnitudes, or event hypocenters
- not needed to define sliding windows, Mc, or b-value estimates

#### Loading Notes
- Recommended load method:
  - `pandas.read_csv('/.../stations/station.sta')`
- The `.sta` extension is not a special binary format here; it is readable as a normal text table
- No complex parsing appears necessary

#### Practical Cautions
- The meaning of `matched` is not documented in the file preview, so future agents should treat it as an inventory flag unless verified elsewhere.
- Because only a few preview lines were inspected, future agents should confirm whether all rows follow the same format, though the header and sample suggest a consistent table.
- This should not be used as evidence for temporal catalog behavior by itself; it is only supporting metadata.

#### Example Access Path
- `<CASE_ROOT>/data/stations/station.sta`

------------------------------

