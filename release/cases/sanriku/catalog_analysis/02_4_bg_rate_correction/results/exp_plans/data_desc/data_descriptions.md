# Data Descriptions
## data
**Source path**: `<CASE_ROOT>/data`
### Summary
This data folder contains an Aomori-focused earthquake analysis workspace with two main earthquake catalogs under `catalog/`: a long-term raw/filtered CSV (2020–2026 reference window, though file timestamps start just before 2020-01-01 UTC) and a shorter relocated catalog for the active period (late 2025 to 2026-05). Supporting context includes a 3-event mainshock table, a focal-mechanism catalog, station metadata, an active-fault GeoJSON, and DEM raster files; the two main catalogs share a simple 5-column schema (`datetime, lat, lon, dep, mag`) but differ in temporal formatting and spatial/depth coverage.
### Detail
#### Folder Structure
- Top-level contents:
  - `catalog/` — primary earthquake catalogs and notebook-based catalog checks.
  - `source_mechanism/` — focal mechanism table for larger events.
  - `stations/` — station metadata files.
  - `active_fault/` — active fault geometry in GeoJSON.
  - `DEM/` — raster/topography resources.
  - `visualize.ipynb` — notebook for visualization.

- Relevant files for future agents:
  - `catalog/Snet_catalog_20200101_20260522_filter.csv` — long-term background-reference catalog.
  - `catalog/Snet_catalog_relocate_250930_260501.csv` — active-period relocated catalog.
  - `catalog/Snet_catalog_relocate.csv` — duplicate of the relocated catalog above (same shape/size in this snapshot).
  - `catalog/main_earthquake.csv` — M1/M2/M3 reference events.
  - `source_mechanism/Snet_mecha.csv` — focal mechanisms and dual-magnitude metadata.
  - `stations/station.sta` — station list used in the study area.

- Also present but not inspected in detail:
  - `active_fault/japan_active_faults.geojson`
  - `DEM/output_hh.tif`
  - `DEM/rasters_COP30.tar.gz`
  - notebook/PNG artifacts in `catalog/`

#### Primary Catalog Files

##### 1) Long-term raw/filtered catalog
- Path: `catalog/Snet_catalog_20200101_20260522_filter.csv`
- Format: CSV
- Size: ~10.8 MB
- Shape: `227755 x 5`
- Columns:
  - `datetime` — string timestamp, format like `2019-12-31 15:26:23.330`
  - `lat` — latitude in decimal degrees
  - `lon` — longitude in decimal degrees
  - `dep` — depth in km
  - `mag` — magnitude (numeric; no explicit magnitude-type column)
- Missing values: none in the five columns.
- Numeric ranges observed:
  - `lat`: 38.001 to 42.999
  - `lon`: 140.001 to 145.999
  - `dep`: 0.0 to 196.0 km
  - `mag`: -1.0 to 7.7
- Time formatting note:
  - Although the filename implies `2020-01-01` to `2026-05-22`, the first rows include UTC timestamps on `2019-12-31`, likely reflecting time-zone or export-boundary handling. Future agents should parse times explicitly and define the intended analysis window in code.
- Organizational note:
  - This is the broader-coverage catalog and should be spatially filtered to the active-period common region before any direct rate comparison.

##### 2) Active-period relocated catalog
- Path: `catalog/Snet_catalog_relocate_250930_260501.csv`
- Alternate duplicate path: `catalog/Snet_catalog_relocate.csv`
- Format: CSV
- Size: ~1.30 MB
- Shape: `22096 x 5`
- Columns:
  - `datetime` — ISO-like UTC string, format like `2025-09-30T16:09:25.360000Z`
  - `lat` — latitude in decimal degrees
  - `lon` — longitude in decimal degrees
  - `dep` — depth in km
  - `mag` — magnitude (numeric; no explicit magnitude-type column)
- Missing values: none in the five columns.
- Numeric ranges observed:
  - `lat`: 38.503003 to 42.382633
  - `lon`: 141.001921 to 144.49847
  - `dep`: 0.05 to 121.14 km
  - `mag`: -0.5 to 7.7
- Content note:
  - This catalog has narrower spatial and depth coverage than the long-term catalog and is the appropriate source for defining the common spatial mask / buffered analysis region.
- Naming note:
  - The user-referenced active-period filename `data/Snet_catalog_20251001_20260501_filter.csv` is not present at the top level; the available relocated active-period file appears to be `catalog/Snet_catalog_relocate_250930_260501.csv`.

#### Cross-catalog Metadata Relevance
- Both main catalogs share the same minimal schema: `datetime, lat, lon, dep, mag`.
- Key differences important for loading/comparison:
  - `datetime` string format differs between the two catalogs and should be parsed separately.
  - The long-term catalog spans a larger area and deeper range.
  - Neither catalog includes explicit event IDs, magnitude type, uncertainty fields, or quality flags in the CSV itself.
- Implication for future agents:
  - Event matching across catalogs will require approximate matching by origin time + hypocenter + magnitude rather than ID joins.
  - Completeness/magnitude-type interpretation cannot be resolved from the catalog CSVs alone; supporting context may need to come from documentation or related files.

#### Mainshock Context File
- Path: `catalog/main_earthquake.csv`
- Format: CSV
- Shape: `3 x 6`
- Columns:
  - `index` — labels `M1`, `M2`, `M3`
  - `datetime`
  - `lat`
  - `lon`
  - `dep`
  - `mag`
- Previewed content:
  - `M1`: `2025-11-09 08:03:39.240`, lat 39.402, lon 143.507, dep 15.9 km, mag 6.9
  - `M2`: `2025-12-08 14:15:10.180`, lat 40.968, lon 142.288, dep 53.5 km, mag 7.5
  - `M3`: `2026-04-20 07:52:58.060`, lat 39.842, lon 143.157, dep 19.4 km, mag 7.7
- Usefulness:
  - Provides explicit anchor events for marking active-period rate plots and defining near-field/local windows around major events.

#### Source Mechanism File
- Path: `source_mechanism/Snet_mecha.csv`
- Format: CSV
- Size: ~61.7 KB
- Shape: `354 x 29`
- Columns:
  - Event/source metadata: `event_code`, `origin_time`, `region_name`, `source_file`
  - Hypocenter/magnitude: `lat_deg`, `lon_deg`, `depth_km`, `mag_1`, `mag_1_type`, `mag_2`, `mag_2_type`
  - Station/count metadata: `n_hypo_stations`, `n_mech_stations`
  - Mechanism metadata: `m_method`, `m_source`, `focal_mech_score`, `focal_mech_projection`
  - Axes: `P_axis_azimuth`, `P_axis_dip`, `T_axis_azimuth`, `T_axis_dip`, `N_axis_azimuth`, `N_axis_dip`
  - Nodal planes: `strike_plane1`, `dip_plane1`, `rake_plane1`, `strike_plane2`, `dip_plane2`, `rake_plane2`
- Missingness pattern:
  - Core event metadata are mostly complete.
  - Mechanism-related fields are absent for many rows (`~215` missing in many mechanism columns), implying not every event has a full focal mechanism solution.
- Observed ranges / categories:
  - `origin_time`: 2025-10-01 02:56:38.820 to 2026-05-19 10:23:35.210
  - `lat_deg`: 38.1768 to 42.9495
  - `lon_deg`: 140.1577 to 145.617
  - `depth_km`: 0.0 to 16180.0 (this extreme upper value suggests at least one outlier or unit/parsing issue; future agents should validate depth before use)
  - `mag_1`: 3.2 to 7.5
  - `mag_2`: 3.5 to 7.4 where present
  - `mag_1_type` counts: `V` 220, `D` 131, `v` 3
  - `mag_2_type` counts: missing 215, `V` 93, `W` 38, `d` 8
  - Most frequent `region_name`: `E OFF AOMORI PREF` (195 rows), followed by `E OFF IWATE PREF`, `E OFF MIYAGI PREF`, `KINKAZAN REGION`, etc.
- Usefulness:
  - Good companion table for mechanism/context on larger active-period events, but not a replacement for the main earthquake catalog.

#### Station Metadata
- Path: `stations/station.sta`
- Format: comma-separated text
- Shape: `371 x 6`
- Columns:
  - `station_code`
  - `station_number`
  - `latitude`
  - `longitude`
  - `elevation_m`
  - `matched`
- Coverage:
  - Latitude: 36.880833 to 44.118833
  - Longitude: 139.245333 to 145.738833
- Data quality note:
  - `matched` is `True` for all 371 stations in this snapshot.
- Usefulness:
  - Supports station-map context and potential interpretation of network footprint relative to catalog spatial coverage.

#### Spatial Coverage Patterns
- Long-term catalog bounding box (broader):
  - ~38.0–43.0°N, 140.0–146.0°E
- Relocated active-period catalog bounding box (narrower/common-region candidate):
  - ~38.5–42.4°N, 141.0–144.5°E
- Practical implication:
  - The relocated catalog naturally defines a tighter offshore/northeast Japan analysis region; future agents can derive a buffered bounding box or polygon from this catalog and then subset the long-term catalog to it.

#### File Naming Conventions
- Catalog naming pattern in `catalog/`:
  - `Snet_catalog_<start>_<end>_filter.csv` for filtered event exports.
  - `Snet_catalog_relocate_<start>_<end>.csv` for relocated active-period exports.
- Example paths:
  - `catalog/Snet_catalog_20200101_20260522_filter.csv`
  - `catalog/Snet_catalog_relocate_250930_260501.csv`
- Supporting data naming:
  - `main_earthquake.csv` for key reference events.
  - `Snet_mecha.csv` for mechanism table.
  - `station.sta` for station metadata.

#### Loading Notes for Future Agents
- Recommended parsers:
  - `pandas.read_csv()` is sufficient for all inspected tabular files.
- Datetime handling:
  - Long-term catalog uses space-separated timestamps with fractional seconds.
  - Relocated catalog uses ISO UTC strings ending in `Z`.
  - Mainshock/mechanism files use timestamp strings compatible with pandas datetime parsing.
- Important cautions:
  - Do not assume the long-term and relocated catalogs are homogeneous products.
  - Do not compare full-region long-term rates directly against active-period relocated rates without first defining and applying a common spatial mask.
  - Validate outliers in `source_mechanism/Snet_mecha.csv`, especially `depth_km` values far beyond the earthquake catalog range.
  - Because the catalog CSVs lack IDs and magnitude-type labels, crosswalk and completeness work will need inferred matching and careful threshold checks rather than exact joins.

#### Minimal File Inventory Pattern
- `catalog/`: earthquake event tables + notebooks/plot artifact
- `source_mechanism/`: focal mechanism event table
- `stations/`: station coordinate lists
- `active_fault/`: GIS fault geometry
- `DEM/`: raster elevation/topography resources

This structure is well suited for future agents that need to: load the long-term and active-period catalogs independently, define a common region from the relocated catalog extent, use `main_earthquake.csv` as event anchors, and optionally augment interpretation with station coverage and focal mechanisms.

------------------------------

## Snet_catalog_20200101_20260522_filter.csv
**Source path**: `data/Snet_catalog_20200101_20260522_filter.csv`
### Summary
This file is the long-term background-reference earthquake catalog in CSV format, containing 227,755 events with a minimal 5-column schema: origin time, latitude, longitude, depth, and magnitude. It spans a broader spatial and depth range than the relocated active-period catalog, so future agents should treat it as the raw/reference catalog and spatially subset it to the active-period common region before any direct rate comparison.
### Detail
#### File Overview
- Path: `catalog/Snet_catalog_20200101_20260522_filter.csv`
- Format: CSV
- Size: ~10.8 MB
- Role in workflow: long-term raw/filtered background-reference catalog for regional rate baselines
- Table shape: `227755 x 5`

#### Schema
Columns present:
- `datetime` — event origin time as string
- `lat` — latitude in decimal degrees
- `lon` — longitude in decimal degrees
- `dep` — depth in km
- `mag` — event magnitude as numeric value

Dtypes inferred on read:
- `datetime`: object/string
- `lat`: float64
- `lon`: float64
- `dep`: float64
- `mag`: float64

Missing-data check:
- No missing values were observed in any of the five columns.

#### Content Ranges Relevant for Future Analysis
Observed numeric ranges:
- `lat`: 38.001 to 42.999
- `lon`: 140.001 to 145.999
- `dep`: 0.0 to 196.0 km
- `mag`: -1.0 to 7.7

These ranges indicate:
- broader horizontal coverage than the relocated active-period catalog
- deeper event coverage than the relocated active-period catalog
- inclusion of very small events, including negative magnitudes
- presence of large mainshock-scale events up to M7.7

#### Time Field Notes
- Example values:
  - `2019-12-31 15:26:23.330`
  - `2019-12-31 15:49:03.770`
  - `2019-12-31 15:49:27.280`
- Timestamp format is standard datetime text with fractional seconds, not ISO `T...Z` style.
- Although the filename encodes `20200101_20260522`, the earliest rows inspected begin on `2019-12-31`, so future agents should not rely only on the filename for exact temporal filtering.
- Recommended loading step: parse `datetime` explicitly with pandas datetime conversion and apply the intended analysis window in code.

#### File Naming / Organization Context
- This file is stored under `catalog/` and follows the pattern:
  - `Snet_catalog_<startdate>_<enddate>_filter.csv`
- Example neighboring files in the same folder:
  - `Snet_catalog_relocate_250930_260501.csv` — active-period relocated catalog
  - `Snet_catalog_relocate.csv` — duplicate/alias of relocated catalog in this snapshot
  - `main_earthquake.csv` — three reference mainshocks

#### Metadata Relevance to Requested Workflow
This file contains the core fields needed for later agents to compute or inspect:
- event counts by time window
- spatial masks / common-region filtering
- magnitude-threshold counts
- depth-binned counts
- rolling or monthly rates
- cross-catalog approximate event matching using time/location/magnitude

It does **not** contain:
- event IDs
- magnitude type labels
- location or magnitude uncertainties
- quality flags
- station counts
- mechanism information

Because of these omissions:
- event matching to the relocated catalog must be approximate, not ID-based
- magnitude-type consistency cannot be determined from this file alone
- completeness assessments will need to rely on statistical inspection rather than explicit metadata fields

#### Preview / Example Records
First few records resemble:
- `datetime=2019-12-31 15:26:23.330, lat=41.683, lon=142.956, dep=32.7, mag=1.7`
- `datetime=2019-12-31 15:49:03.770, lat=40.125, lon=141.216, dep=8.1, mag=1.2`
- `datetime=2019-12-31 15:49:27.280, lat=41.686, lon=142.968, dep=34.8, mag=1.3`

#### Practical Loading Notes
- `pandas.read_csv()` is sufficient to load the file.
- Recommended post-load checks for future agents:
  - convert `datetime` to timezone-aware or consistently interpreted datetime objects
  - confirm intended time span after parsing
  - subset by the active-period-derived common spatial mask before long-term vs active-period comparisons
  - inspect `mag` thresholds explicitly, since the catalog includes values below 0
  - inspect depth values directly when constructing bins such as 0–30, 30–60, and >60 km

#### Key Caveat for Future Agents
- This file should be treated as the broad-coverage long-term reference catalog, not as a homogeneous equivalent to the relocated active-period dataset.
- Any anomaly claim comparing long-term and active-period rates should first restrict this catalog to the common analysis region defined from the relocated catalog (optionally with a small buffer), because this file covers a wider area than the active-period relocated product.

------------------------------

## Snet_catalog_20251001_20260501_filter.csv
**Source path**: `data/Snet_catalog_20251001_20260501_filter.csv`
### Summary
The requested active-period file name is not present verbatim in this data folder; the available matching active-period relocated catalog is `catalog/Snet_catalog_relocate_250930_260501.csv`. It is a 22,096-row CSV with the same minimal 5-column event schema as the long-term catalog (`datetime, lat, lon, dep, mag`), but with narrower spatial and depth coverage and ISO-style UTC timestamps, making it the natural source for defining the common analysis region and for fine-scale active-period rate work.
### Detail
#### File Identity and Naming Note
- User-requested file reference: `data/Snet_catalog_20251001_20260501_filter.csv`
- Matching available file in this workspace: `catalog/Snet_catalog_relocate_250930_260501.csv`
- A duplicate copy is also present as:
  - `catalog/Snet_catalog_relocate.csv`
- In this snapshot, the two relocated files have the same size and shape, suggesting they are the same dataset under two names.

#### File Overview
- Path used for inspection: `catalog/Snet_catalog_relocate_250930_260501.csv`
- Format: CSV
- Size: ~1.30 MB
- Role in workflow: active-period relocated/filtered earthquake catalog for fine-scale spatial, depth, and regional rate inspection
- Table shape: `22096 x 5`

#### Schema
Columns present:
- `datetime` — event origin time as string
- `lat` — latitude in decimal degrees
- `lon` — longitude in decimal degrees
- `dep` — depth in km
- `mag` — event magnitude as numeric value

Dtypes inferred on read:
- `datetime`: object/string
- `lat`: float64
- `lon`: float64
- `dep`: float64
- `mag`: float64

Missing-data check:
- No missing values were observed in any of the five columns.

#### Content Ranges Relevant for Future Analysis
Observed numeric ranges:
- `lat`: 38.503003 to 42.382633
- `lon`: 141.001921 to 144.49847
- `dep`: 0.05 to 121.14 km
- `mag`: -0.5 to 7.7

These ranges indicate:
- narrower horizontal footprint than the long-term reference catalog
- shallower maximum depth than the long-term catalog
- inclusion of small events down to sub-M1 values
- inclusion of major active-period events up to M7.7

#### Time Field Notes
- Example values:
  - `2025-09-30T16:09:25.360000Z`
  - `2025-09-30T16:55:18.670000Z`
  - `2025-09-30T18:47:05.380000Z`
- Timestamp format is ISO-like UTC text with `T` separator and trailing `Z`.
- The filename starts at `250930`, and the first rows also begin on `2025-09-30` UTC, even though the task description references an active period starting `2025-10-01`. Future agents should define the intended temporal window explicitly after parsing.
- Recommended loading step: parse `datetime` with timezone-aware handling and then subset to the target active-period interval as needed.

#### Comparison-Oriented Metadata Relevance
This file is especially important because it can define the common analysis region for later comparison with the broader long-term catalog.

Useful properties for future agents:
- same core fields as the long-term catalog, enabling straightforward column-aligned loading
- narrower extent that can be converted into a bounding box or buffered mask for filtering the long-term catalog
- depth range already compatible with bins such as `0–30 km`, `30–60 km`, `>60 km`
- magnitude field supports threshold filtering such as `M>=1.2`, `M>=2`, `M>=3`, `M>=4`, `M>=5`

Not present in this file:
- event IDs
- magnitude type labels
- uncertainties
- quality flags
- station counts
- relocation residuals / uncertainty ellipses

Because of these omissions:
- crosswalk to the long-term catalog must rely on approximate matching by time, location, depth, and magnitude rather than a unique event key
- magnitude-type consistency cannot be resolved from this CSV alone
- completeness magnitude assessment will need to be statistical rather than metadata-driven

#### Preview / Example Records
First few records resemble:
- `datetime=2025-09-30T16:09:25.360000Z, lat=38.703422, lon=142.256738, dep=41.35, mag=2.8`
- `datetime=2025-09-30T16:55:18.670000Z, lat=38.959892, lon=142.594434, dep=27.66, mag=1.2`
- `datetime=2025-09-30T18:47:05.380000Z, lat=39.934501, lon=142.485905, dep=34.75, mag=1.6`

#### Practical Use in the Aomori Workflow
For future agents, this file is the preferred source to define:
- the common spatial analysis mask
- buffered study bounds for long-term catalog filtering
- fine-scale active-period rate calculations
- local/near-field/outer-band regional subsets
- short-window daily/weekly/14-day/monthly event counts
- active-period depth-stratified rates

It should **not** be treated as directly homogeneous with the long-term raw catalog without first acknowledging catalog differences and restricting comparisons to the common region.

#### Relationship to Other Context Files
Useful companion files in the same workspace:
- `catalog/main_earthquake.csv`
  - contains 3 labeled reference events (`M1`, `M2`, `M3`) with `datetime, lat, lon, dep, mag`
  - suitable for marking key times and defining local windows around main events
- `source_mechanism/Snet_mecha.csv`
  - contains focal mechanism and dual-magnitude metadata for a subset of moderate-to-large events during the active period
- `stations/station.sta`
  - contains station coordinates and match flags, useful for network-coverage context

#### Loading Notes
- `pandas.read_csv()` is sufficient.
- Recommended post-load steps for future agents:
  - convert `datetime` to parsed UTC timestamps
  - confirm the exact start/end window intended for the active-period study
  - compute the actual spatial extent or convex/buffered mask from these relocated hypocenters
  - use that mask to subset the long-term reference catalog before any anomaly comparison
  - inspect magnitude thresholds explicitly because the file includes events below M1.2

#### Key Caveat for Future Agents
- This relocated catalog is the appropriate fine-scale active-period dataset and should be used to define the common spatial comparison region.
- Any long-term-versus-active comparison should filter the broader raw catalog to this same region first; full-domain statistics from the long-term catalog are supplementary context only, not the primary anomaly baseline.

------------------------------

## main_earthquake.csv
**Source path**: `catalog/main_earthquake.csv`
### Summary
This is a small 3-row reference table listing the main labeled events `M1`, `M2`, and `M3`, with origin time, latitude, longitude, depth, and magnitude. It is not a catalog for rate estimation, but it is an important context file for future agents to anchor regional subsetting, mark mainshock times on plots, and define local or near-field windows around the major events.
### Detail
#### File Overview
- Path: `catalog/main_earthquake.csv`
- Format: CSV
- Size: ~184 bytes
- Role in workflow: context/reference table for the three named major events used throughout the Aomori activity analysis
- Table shape: `3 x 6`

#### Schema
Columns present:
- `index` — event label / identifier
- `datetime` — event origin time as string
- `lat` — latitude in decimal degrees
- `lon` — longitude in decimal degrees
- `dep` — depth in km
- `mag` — magnitude

Dtypes inferred on read:
- `index`: object/string
- `datetime`: object/string
- `lat`: float64
- `lon`: float64
- `dep`: float64
- `mag`: float64

Missing-data check:
- No missing values were observed in any column.

#### Event Contents
The table contains exactly three labeled events:
- `M1`
  - `datetime`: `2025-11-09 08:03:39.240`
  - `lat`: `39.402`
  - `lon`: `143.507`
  - `dep`: `15.9` km
  - `mag`: `6.9`
- `M2`
  - `datetime`: `2025-12-08 14:15:10.180`
  - `lat`: `40.968`
  - `lon`: `142.288`
  - `dep`: `53.5` km
  - `mag`: `7.5`
- `M3`
  - `datetime`: `2026-04-20 07:52:58.060`
  - `lat`: `39.842`
  - `lon`: `143.157`
  - `dep`: `19.4` km
  - `mag`: `7.7`

#### Field Meaning and Usefulness
- `index`:
  - semantic labels used by the project to refer to the three main events
  - appropriate for plot annotations and region naming
- `datetime`:
  - useful for marking vertical lines or event windows in time-series analysis
  - format is standard datetime text with fractional seconds
- `lat`, `lon`:
  - suitable for defining event-centered local, near-field, and outer-band regions
- `dep`:
  - provides mainshock depth context for comparing shallow/intermediate-depth activity windows
- `mag`:
  - indicates the relative size ordering of the three events and can help prioritize event-centered diagnostics

#### Metadata Characteristics Relevant for Future Agents
- This file contains only anchor events, not full seismicity.
- It has the same basic spatial/depth/magnitude fields as the main catalogs, making it easy to join logically in downstream code.
- It does not contain:
  - event IDs matching the long-term or relocated catalogs
  - magnitude types
  - mechanism information
  - uncertainty estimates
  - rupture parameters

Because of that:
- if future agents want to connect these events to entries in the main catalogs, they should match approximately by origin time and hypocenter rather than by an explicit event key.

#### Practical Role in the Requested Workflow
This file is especially useful for future agents to:
- mark `M1`, `M2`, and `M3` on long-term and active-period rate plots
- define event-centered spatial windows for local and near-field analysis
- compare rate evolution before and after each major event
- organize figures and summary tables consistently around the three named events

It is **not** sufficient for:
- background-rate estimation
- completeness analysis
- catalog crosswalk by itself
- mechanism interpretation

#### Loading Notes
- `pandas.read_csv()` is sufficient.
- Recommended post-load steps:
  - parse `datetime` explicitly to pandas datetime
  - preserve `index` as a categorical or string label (`M1`, `M2`, `M3`)
  - use `lat`, `lon`, and optional buffers to construct analysis regions around each main event

#### Relationship to Other Files
Most relevant companion files:
- `catalog/Snet_catalog_20200101_20260522_filter.csv`
  - long-term broad-coverage background-reference catalog
- `catalog/Snet_catalog_relocate_250930_260501.csv`
  - active-period relocated catalog used for common-region definition and fine-scale rate analysis
- `source_mechanism/Snet_mecha.csv`
  - focal-mechanism metadata for a subset of moderate-to-large events during the active period

#### Example Path
- `catalog/main_earthquake.csv`

------------------------------

## Snet_mecha.csv
**Source path**: `source_mechanism/Snet_mecha.csv`
### Summary
This file is a focal-mechanism and event-metadata table for 354 moderate-to-large events during roughly October 2025 to May 2026. It complements the main catalogs with mechanism geometry, station counts, region names, and two magnitude fields/types, but it is sparse in many mechanism-related columns and should be used as contextual metadata rather than as the primary seismicity-rate catalog.
### Detail
#### File Overview
- Path: `source_mechanism/Snet_mecha.csv`
- Format: CSV
- Size: ~61.7 KB
- Role in workflow: contextual event/mechanism metadata for larger active-period earthquakes
- Table shape: `354 x 29`

#### Schema
Columns present:
- Event identifiers / source info:
  - `event_code`
  - `origin_time`
  - `region_name`
  - `source_file`
- Hypocenter / magnitude fields:
  - `lat_deg`
  - `lon_deg`
  - `depth_km`
  - `mag_1`
  - `mag_1_type`
  - `mag_2`
  - `mag_2_type`
- Station / method metadata:
  - `n_hypo_stations`
  - `m_method`
  - `m_source`
  - `n_mech_stations`
  - `focal_mech_score`
  - `focal_mech_projection`
- Principal axes:
  - `P_axis_azimuth`
  - `P_axis_dip`
  - `T_axis_azimuth`
  - `T_axis_dip`
  - `N_axis_azimuth`
  - `N_axis_dip`
- Nodal planes:
  - `strike_plane1`
  - `dip_plane1`
  - `rake_plane1`
  - `strike_plane2`
  - `dip_plane2`
  - `rake_plane2`

#### Dtypes
Inferred dtypes on read:
- Strings / object:
  - `event_code`, `origin_time`, `mag_1_type`, `mag_2_type`, `region_name`, `m_method`, `m_source`, `focal_mech_projection`, `source_file`
- Numeric:
  - `lat_deg`, `lon_deg`, `depth_km`, `mag_1`, `mag_2`, `n_hypo_stations`, all axis/plane fields, `focal_mech_score`, `n_mech_stations`

#### Missingness Pattern
Core fields are mostly complete:
- `event_code`, `origin_time`, `lat_deg`, `lon_deg`, `depth_km`, `mag_1`, `mag_1_type`, `region_name`, `n_hypo_stations`, `source_file` have no missing values in the inspected table.

Substantial missingness exists in secondary magnitude/mechanism fields:
- `mag_2`: 215 missing
- `mag_2_type`: 215 missing
- `m_method`: 215 missing
- `m_source`: 215 missing
- mechanism geometry / axis / quality columns: typically 215 missing
- `n_mech_stations`: 215 missing
- `focal_mech_projection`: 215 missing

Interpretation for future agents:
- not every event has a full focal mechanism solution
- many rows contain only basic hypocenter plus primary magnitude metadata
- downstream logic should test for non-null mechanism fields before using them

#### Time and Spatial Coverage
Observed ranges:
- `origin_time`: from `2025-10-01 02:56:38.820` to `2026-05-19 10:23:35.210`
- `lat_deg`: 38.176833333333335 to 42.9495
- `lon_deg`: 140.15766666666667 to 145.617
- `depth_km`: 0.0 to 16180.0

Important caution:
- the maximum `depth_km` value (`16180.0`) is far outside the main earthquake catalog depth range and is likely an outlier, parsing issue, or special-case encoding; future agents should validate depth before using this field quantitatively.

#### Magnitude Metadata
Observed ranges:
- `mag_1`: 3.2 to 7.5
- `mag_2`: 3.5 to 7.4 where present

Magnitude-type counts:
- `mag_1_type`:
  - `V`: 220
  - `D`: 131
  - `v`: 3
- `mag_2_type`:
  - missing: 215
  - `V`: 93
  - `W`: 38
  - `d`: 8

Relevance:
- this file is useful for checking magnitude-type metadata that are absent from the main 5-column catalogs
- however, it covers only a subset of events and should not be treated as a complete source for all catalog magnitudes

#### Region / Classification Fields
- `region_name` provides coarse geographic labels for events.
- Most frequent region labels in the inspected file include:
  - `E OFF AOMORI PREF`: 195
  - `E OFF IWATE PREF`: 34
  - `E OFF MIYAGI PREF`: 22
  - `KINKAZAN REGION`: 22
  - `NE OFF IWATE PREF`: 14
  - plus smaller counts in nearby regional names

This is useful for:
- contextual grouping of larger events by named region
- cross-checking whether major active-period mechanism solutions concentrate in the Aomori offshore area versus surrounding regions

#### Example Rows / Content Style
The file contains rows like:
- `event_code`: e.g. `J2025100111563882`
- `origin_time`: standard datetime string with milliseconds
- `lat_deg`, `lon_deg`, `depth_km`: hypocenter fields
- `mag_1`, `mag_1_type`: primary magnitude and type
- optional `mag_2`, `mag_2_type`: secondary magnitude and type
- optional mechanism solutions: axis orientations, nodal planes, score, projection, and number of mechanism stations

#### Relationship to the Main Catalogs
Compared with the two main earthquake catalogs (`datetime, lat, lon, dep, mag` only), this file adds:
- event code identifiers
- region names
- magnitude-type information
- station-count metadata
- focal mechanism geometry and quality descriptors

But it is not a drop-in replacement for the catalog files because:
- it contains far fewer events (`354` rows)
- it is restricted to a subset of mostly larger events
- many mechanism-specific columns are absent for a large fraction of rows

#### Recommended Uses for Future Agents
Suitable uses:
- attach focal mechanism context to major active-period events
- inspect magnitude-type conventions for larger earthquakes
- identify event subsets with valid mechanism solutions
- compare named regions of larger events with the spatial patterns seen in the active-period catalog
- support figure annotations or event summaries for M4+/M5+ events where mechanism information exists

Less suitable uses:
- background-rate estimation
- completeness estimation for the full catalog
- total event counting
- direct replacement for the long-term or relocated seismicity tables

#### Loading Notes
- `pandas.read_csv()` is sufficient.
- Recommended post-load safeguards:
  - parse `origin_time` explicitly to datetime
  - filter out rows with null mechanism fields when computing any mechanism-based summaries
  - validate `depth_km` for extreme outliers before using depth statistically
  - standardize magnitude-type strings if needed (`V` vs `v`, `D` vs `d`)

#### Example Path
- `source_mechanism/Snet_mecha.csv`

------------------------------

## station.sta
**Source path**: `stations/station.sta`
### Summary
This file is a comma-separated station metadata table with 371 stations, giving station code, numeric ID, latitude, longitude, elevation, and a match flag. It is not an event catalog, but it provides useful network-footprint context for future agents mapping the Aomori study area, checking spatial coverage, or annotating station distributions relative to seismicity clusters.
### Detail
#### File Overview
- Path: `stations/station.sta`
- Format: comma-separated text table
- Size: ~16.1 KB
- Role in workflow: station metadata / network context file
- Table shape: `371 x 6`

#### Schema
Columns present:
- `station_code` — station identifier string
- `station_number` — numeric station ID
- `latitude` — station latitude in decimal degrees
- `longitude` — station longitude in decimal degrees
- `elevation_m` — station elevation in meters
- `matched` — boolean match flag

Dtypes inferred from the file content:
- `station_code`: string/object
- `station_number`: integer-like
- `latitude`: float
- `longitude`: float
- `elevation_m`: numeric/integer-like
- `matched`: boolean-like

#### Preview / Example Records
First few rows resemble:
- `A.ASMS, 5572, 40.885667, 140.874000, -3, True`
- `A.CHOG, 5550, 41.327167, 140.815333, 0, True`
- `A.HGTZ, 5571, 40.982833, 140.904000, -11, True`
- `A.HRDA, 5549, 41.448833, 140.881000, 2, True`

#### Coverage and Basic Metadata
Observed ranges:
- `latitude`: 36.880833 to 44.118833
- `longitude`: 139.245333 to 145.738833

Match flag summary:
- `matched=True`: 371
- no unmatched stations were observed in this snapshot

Interpretation:
- the station set spans a wider region than the immediate offshore Aomori active-period earthquake footprint
- it likely represents the broader network context available for the catalog workflow rather than a strictly local subset

#### Field Meaning and Practical Use
- `station_code`:
  - useful for labeling station maps or cross-referencing station lists
- `station_number`:
  - internal numeric identifier that may help with joins if other files use numeric station IDs
- `latitude`, `longitude`:
  - appropriate for plotting station distributions relative to catalog event locations, mainshock epicenters, or common-region masks
- `elevation_m`:
  - gives site elevation only; not directly needed for seismicity-rate analysis but useful for metadata completeness
- `matched`:
  - indicates station records accepted or linked in the current station list; all are `True` here

#### Relevance to the Requested Workflow
This file is supportive context, not a primary analysis input for rate calculations. It can help future agents:
- visualize network footprint relative to the long-term and active-period catalog extents
- assess whether study regions lie within the broader station distribution
- add station overlays to maps of seismicity, depth slices, or anomaly regions
- keep track of available stations if later work needs waveform or pick-based follow-up

It is **not** sufficient for:
- computing event rates
- catalog crosswalks
- completeness estimation by itself
- determining location uncertainty directly

#### Relationship to Other Files
Most relevant companion files:
- `catalog/Snet_catalog_20200101_20260522_filter.csv`
  - long-term raw/reference earthquake catalog
- `catalog/Snet_catalog_relocate_250930_260501.csv`
  - active-period relocated earthquake catalog
- `catalog/main_earthquake.csv`
  - three labeled mainshock reference events (`M1`, `M2`, `M3`)
- `source_mechanism/Snet_mecha.csv`
  - focal mechanism metadata for a subset of larger active-period events

#### Loading Notes
- The file can be read directly with `pandas.read_csv()`.
- Despite the `.sta` extension, it is a standard comma-separated text table with a header row.
- Recommended post-load checks for future agents:
  - confirm boolean parsing of `matched`
  - map station coordinates alongside event epicenters if network-context visualization is needed
  - use this file only as spatial/network context, not as a substitute for event metadata

#### Example Path
- `stations/station.sta`

------------------------------

