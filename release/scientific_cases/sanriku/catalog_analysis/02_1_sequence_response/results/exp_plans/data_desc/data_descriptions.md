# Data Descriptions
## data
**Source path**: `<CASE_ROOT>/data`
### Summary
This folder contains an earthquake sequence-analysis dataset for the Aomori regional catalog, including a relocated seismicity catalog, a 3-event mainshock list, focal-mechanism metadata, and station metadata. The core analysis-ready files are CSV tables with straightforward fields for time, location, depth, magnitude, and mechanism attributes, making the directory suitable for event-centered sequence extraction and robustness checks.
### Detail
#### Folder Structure
- `catalog/`: relocated and full catalog products, mainshock list, and an exploratory notebook/plot.
- `source_mechanism/`: focal-mechanism catalog and a backup mechanism file.
- `stations/`: station metadata in text/tabular form.
- Additional context files include `active_fault/japan_active_faults.geojson`, `DEM/output_hh.tif`, and `visualize.ipynb`, but the main sequence-analysis inputs are the CSV/text files above.

#### Key Data Files and Metadata

##### `catalog/Snet_catalog_relocate.csv`
- Format: CSV
- Size: ~1.3 MB
- Shape: 25,646 rows × 5 columns
- Columns:
  - `datetime` (ISO-like UTC timestamp, stored as string)
  - `lat` (float)
  - `lon` (float)
  - `dep` (float, km)
  - `mag` (float)
- This is the primary relocated seismicity catalog and is the main file for event-centered sequence extraction.
- Example record fields indicate analysis-ready event timing and hypocenter coordinates, but no explicit event ID column was present in the inspected version.

##### `catalog/main_earthquake.csv`
- Format: CSV
- Shape: 3 rows × 6 columns
- Columns:
  - `index` (event label: `M1`, `M2`, `M3`)
  - `datetime` (string timestamp)
  - `lat` (float)
  - `lon` (float)
  - `dep` (float, km)
  - `mag` (float)
- Contains the three major earthquakes to be matched against the relocated catalog.
- The three labeled events are present explicitly and can be used as sequence centers.

##### `source_mechanism/Snet_mecha.csv`
- Format: CSV
- Shape: 354 rows × 29 columns
- Key columns for mechanism/context use:
  - `event_code`, `origin_time`, `lat_deg`, `lon_deg`, `depth_km`
  - magnitude fields: `mag_1`, `mag_1_type`, `mag_2`, `mag_2_type`
  - station coverage / method fields: `n_hypo_stations`, `m_method`, `m_source`, `n_mech_stations`
  - focal-mechanism geometry: `P_axis_*`, `T_axis_*`, `N_axis_*`, `strike_plane*`, `dip_plane*`, `rake_plane*`
  - quality/context: `focal_mech_score`, `focal_mech_projection`, `source_file`
- This file supports checking focal-mechanism availability and summarizing mechanism properties within sequence windows.

##### `stations/station.sta`
- Format: CSV-like text file
- Approximate line count: 372
- Previewed columns:
  - `station_code`, `station_number`, `latitude`, `longitude`, `elevation_m`, `matched`
- Contains station locations and a matched/unmatched flag, useful for contextualizing station coverage around the sequences.

#### File Naming and Organization Patterns
- Catalog products follow a consistent `Snet_catalog_*` naming scheme, including relocated and full versions (e.g., `Snet_catalog_relocate.csv`, `Snet_catalog_full_*.csv`, `Snet_catalog-v*.csv`).
- The major-earthquake list is a small, explicitly labeled file: `main_earthquake.csv` with `M1`, `M2`, `M3` in the `index` column.
- Mechanism data are stored under `source_mechanism/` with a compact CSV table and a backup file in `back/`.
- Station metadata are under `stations/` with a simple tabular format.

#### Fields Most Relevant for Future Sequence-Analysis Agents
- Event timing: `datetime` / `origin_time`
- Spatial location: `lat`, `lon`, `dep` / `lat_deg`, `lon_deg`, `depth_km`
- Magnitude: `mag` / `mag_1`, `mag_2`
- Mainshock identifiers: `index` in `main_earthquake.csv`
- Mechanism availability/quality: `event_code`, `focal_mech_score`, `n_mech_stations`, `source_file`
- Station context: `station_code`, `latitude`, `longitude`, `matched`

#### Notes for Loading
- The relocated catalog and mainshock file are ready for direct loading with pandas.
- The mechanism file contains mixed numeric and string metadata; `origin_time` appears as a string timestamp and should be parsed as datetime if used.
- No scientific analysis was performed here; this is a structural inventory to help locate the correct files and columns for later event-centered sequence processing.

------------------------------

## catalog/Snet_catalog_relocate.csv
**Source path**: `<CASE_ROOT>/data/catalog/Snet_catalog_relocate.csv`
### Summary
This is the main relocated earthquake catalog for the Aomori regional dataset. It contains 25,646 events with timestamp, latitude, longitude, depth, and magnitude fields, spanning 2025-06-01 to 2026-05-01 and suitable for event-centered sequence extraction around the three mainshocks.
### Detail
#### File Overview
- **Format:** CSV
- **Rows × Columns:** 25,646 × 5
- **Purpose:** Primary relocated seismicity catalog for sequence analysis around M1, M2, and M3.

#### Columns
- `datetime` — event origin time as a string timestamp in UTC-like ISO format (`YYYY-MM-DDTHH:MM:SS.ssssssZ`)
- `lat` — event latitude in decimal degrees (`float64`)
- `lon` — event longitude in decimal degrees (`float64`)
- `dep` — hypocentral depth in kilometers (`float64`)
- `mag` — magnitude (`float64`)

#### Basic Metadata
- **Time range:** `2025-06-01T00:13:38.900000Z` to `2026-05-01T14:44:22.450000Z`
- **Latitude range:** 38.503003 to 42.382633
- **Longitude range:** 141.001921 to 144.498470
- **Depth range:** 0.05 km to 121.14 km
- **Magnitude range:** -0.5 to 7.7
- **Mean values:** lat ~40.156, lon ~142.921, depth ~21.245 km, magnitude ~1.646

#### Notes for Future Agents
- The file does **not** include an explicit event ID or catalog identifier column in the inspected version.
- `datetime` should be parsed as a datetime type before any temporal windowing.
- This file provides the minimum fields needed for spatial, temporal, depth, and magnitude-based sequence extraction and robustness checks.
- No derived analysis has been performed here; this is only a structural and metadata summary.

------------------------------

## catalog/main_earthquake.csv
**Source path**: `<CASE_ROOT>/data/catalog/main_earthquake.csv`
### Summary
This file is a compact mainshock reference table containing the three target earthquakes for sequence analysis. It lists labeled events M1, M2, and M3 with their origin time, epicentral location, depth, and magnitude, and can be used to anchor event-centered extraction from the relocated catalog.
### Detail
#### File Overview
- **Format:** CSV
- **Rows × Columns:** 3 × 6
- **Purpose:** Reference table of the three major earthquakes used as sequence centers.

#### Columns
- `index` — mainshock label (`M1`, `M2`, `M3`)
- `datetime` — origin time as a string timestamp (`YYYY-MM-DD HH:MM:SS.sss`)
- `lat` — latitude in decimal degrees (`float64`)
- `lon` — longitude in decimal degrees (`float64`)
- `dep` — depth in kilometers (`float64`)
- `mag` — magnitude (`float64`)

#### Records
- `M1` — 2025-11-09 08:03:39.240, lat 39.402, lon 143.507, depth 15.9 km, magnitude 6.9
- `M2` — 2025-12-08 14:15:10.180, lat 40.968, lon 142.288, depth 53.5 km, magnitude 7.5
- `M3` — 2026-04-20 07:52:58.060, lat 39.842, lon 143.157, depth 19.4 km, magnitude 7.7

#### Notes for Future Agents
- This file contains the only explicit event labels for the three target earthquakes.
- The timestamps are not in the same ISO-UTC style as the relocated catalog, so parsing/normalization will be needed before time-based matching.
- No extra identifiers, uncertainty fields, or mechanism attributes are present in this file; those must be obtained from the relocated catalog and mechanism/station tables.
- No analysis has been performed here; this is a structural metadata summary only.

------------------------------

## source_mechanism/Snet_mecha.csv
**Source path**: `<CASE_ROOT>/data/source_mechanism/Snet_mecha.csv`
### Summary
This file is a focal-mechanism and source-property catalog with 354 events and 29 columns. It includes event timing and location, one or two magnitudes, station-count information, focal-mechanism geometry, and a quality/availability flag, making it useful for checking mechanism coverage within earthquake sequence windows.
### Detail
#### File Overview
- **Format:** CSV
- **Rows × Columns:** 354 × 29
- **Purpose:** Mechanism/source metadata for a subset of catalog events, including focal-mechanism solutions and related quality/context fields.

#### Columns
- Event identity/time/location:
  - `event_code` — event identifier
  - `origin_time` — origin time as a string timestamp
  - `lat_deg`, `lon_deg`, `depth_km` — hypocenter location and depth
- Magnitude fields:
  - `mag_1`, `mag_1_type`
  - `mag_2`, `mag_2_type`
- Regional/context fields:
  - `region_name`
  - `n_hypo_stations`
  - `m_method`, `m_source`
- Focal-mechanism geometry:
  - `P_axis_azimuth`, `P_axis_dip`
  - `T_axis_azimuth`, `T_axis_dip`
  - `N_axis_azimuth`, `N_axis_dip`
  - `strike_plane1`, `dip_plane1`, `rake_plane1`
  - `strike_plane2`, `dip_plane2`, `rake_plane2`
- Quality / provenance:
  - `focal_mech_score`
  - `n_mech_stations`
  - `focal_mech_projection`
  - `source_file`

#### Basic Metadata
- **Datatype pattern:** mixed string, integer, and floating-point values
- **Typical missingness:** many mechanism-geometry fields are sparse; in the inspected file, several axis and plane parameters had 215 missing values each, indicating partial coverage rather than complete catalog-wide solutions.
- **Example content:** the first rows include events in October 2025 with associated regional names, station counts, and focal-mechanism parameters.

#### Notes for Future Agents
- `origin_time` should be parsed as datetime before merging with the earthquake catalog.
- The file is not a complete event catalog; it is a mechanism-capable subset and should be joined to the relocated seismicity catalog via time/location/event-code matching if needed.
- Sparse fields mean mechanism availability should be treated as optional/contextual rather than universal.
- No scientific inference has been done here; this is a structural metadata summary only.

------------------------------

## stations/station.sta
**Source path**: `<CASE_ROOT>/data/stations/station.sta`
### Summary
This station file is a small tabular inventory of seismic stations, with 372 lines including a header and station metadata. It provides station codes, station numbers, coordinates, elevation, and a matched flag, which is useful for assessing station coverage around the earthquake sequences.
### Detail
#### File Overview
- **Format:** CSV-like text
- **Approximate line count:** 372
- **Purpose:** Station metadata for contextualizing monitoring coverage in the Aomori region.

#### Columns
- `station_code` — station identifier
- `station_number` — numeric station ID
- `latitude` — station latitude in decimal degrees
- `longitude` — station longitude in decimal degrees
- `elevation_m` — elevation in meters (can be negative for below sea level or local reference)
- `matched` — boolean flag indicating whether the station was matched in the source workflow

#### Basic Metadata
- The file begins with a standard header row and then one station per line.
- Example entries show a mix of coastal/inland stations with coordinates in the broader northeastern Japan region.
- Values are simple numeric/string fields; there are no event or waveform measurements in this file.

#### Notes for Future Agents
- This file is primarily contextual and should be joined with event data only if station-coverage or geometry is relevant.
- The `matched` flag may help identify stations already aligned in the source workflow.
- No scientific analysis has been performed here; this is only a structure and metadata summary.

------------------------------

