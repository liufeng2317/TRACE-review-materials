# Data Descriptions
## data
**Source path**: `<CASE_ROOT>/data`
### Summary
This data source contains a relocated regional earthquake catalog for the Aomori/Japan study area, a small table of major earthquakes, a focal-mechanism catalog, and a station inventory. The files are tabular CSV/STA text formats with event time, hypocenter, magnitude, mechanism, and station-geometry fields suitable for catalog matching and regional seismicity profiling.
### Detail
#### Folder Structure
The data are organized into three main subfolders plus related analysis artifacts:

- `catalog/`
  - `Snet_catalog_relocate.csv` — main regional relocated earthquake catalog
  - `main_earthquake.csv` — 3 major earthquakes for matching/context
  - several additional catalog variants and a notebook/figure artifact are present in the folder, but the requested work centers on the two CSV files above
- `source_mechanism/`
  - `Snet_mecha.csv` — focal mechanism / source-mechanism catalog
- `stations/`
  - `station.sta` — station inventory

Example paths:
- `catalog/Snet_catalog_relocate.csv`
- `catalog/main_earthquake.csv`
- `source_mechanism/Snet_mecha.csv`
- `stations/station.sta`

#### File Statistics

**1) `catalog/Snet_catalog_relocate.csv`**
- Format: CSV
- Records: 22,096 data rows, 5 columns
- Columns: `datetime`, `lat`, `lon`, `dep`, `mag`
- Types: `datetime` stored as text; location/depth/magnitude numeric
- Missing values: none in the available columns
- Ranges observed:
  - Latitude: 38.503 to 42.383
  - Longitude: 141.002 to 144.498
  - Depth: 0.05 to 121.14 km
  - Magnitude: -0.5 to 7.7
- Example row format:
  - `2025-09-30T16:09:25.360000Z, 38.703422, 142.256738, 41.35, 2.8`
- Notes for downstream use:
  - This is the primary file for stage-1 cleaning and regional seismicity analysis.
  - No event ID column is present in the file as delivered.

**2) `catalog/main_earthquake.csv`**
- Format: CSV
- Records: 3 rows, 6 columns
- Columns: `index`, `datetime`, `lat`, `lon`, `dep`, `mag`
- Types: `index` is a string label; time as text; location/depth/magnitude numeric
- Missing values: none
- Major-event ranges:
  - Latitude: 39.402 to 40.968
  - Longitude: 142.288 to 143.507
  - Depth: 15.9 to 53.5 km
  - Magnitude: 6.9 to 7.7
- Example rows:
  - `M1, 2025-11-09 08:03:39.240, 39.402, 143.507, 15.9, 6.9`
  - `M2, 2025-12-08 14:15:10.180, 40.968, 142.288, 53.5, 7.5`
  - `M3, 2026-04-20 07:52:58.060, 39.842, 143.157, 19.4, 7.7`
- Notes for downstream use:
  - Contains explicit event labels (`M1`, `M2`, `M3`) that can be used as major-earthquake identifiers.

**3) `source_mechanism/Snet_mecha.csv`**
- Format: CSV
- Records: 354 rows, 29 columns
- Key columns:
  - Event/time/location: `event_code`, `origin_time`, `lat_deg`, `lon_deg`, `depth_km`
  - Magnitudes: `mag_1`, `mag_1_type`, `mag_2`, `mag_2_type`
  - Region metadata: `region_name`, `m_method`, `m_source`, `source_file`
  - Station/mechanism summary: `n_hypo_stations`, `n_mech_stations`, `focal_mech_score`
  - Mechanism geometry: P/T/N axes and two nodal planes (`strike`, `dip`, `rake` pairs)
  - `focal_mech_projection`
- Types: mixed text and numeric; many geometric/mechanism fields are numeric
- Missing values:
  - About 215 rows are missing the secondary magnitude and most focal-mechanism fields, indicating a substantial subset without complete mechanism solutions
  - Core fields (`event_code`, `origin_time`, `lat_deg`, `lon_deg`, `depth_km`, `mag_1`, `mag_1_type`, `region_name`, `n_hypo_stations`, `source_file`) are populated
- Ranges observed:
  - Latitude: 38.177 to 42.950
  - Longitude: 140.158 to 145.617
  - Depth: 0.0 to 16,180.0 (as stored; this contains very large outliers / possible unit or parsing issues worth auditing)
  - `mag_1`: 3.2 to 7.5
  - `mag_2`: 3.5 to 7.4 where present
  - `n_hypo_stations`: 7 to 41
  - `focal_mech_score`: 86 to 100
- Example row format:
  - `J2025100111563882, 2025-10-01 02:56:38.820, 41.813333, 142.668167, 56.44, 3.5, V, ...`
- Notes for downstream use:
  - This file is the focal-mechanism source of record.
  - The extreme depth maximum suggests a cleaning check is needed before use.

**4) `stations/station.sta`**
- Format: comma-delimited text/STA-style table
- Records: 371 data rows (372 lines total including header)
- Columns: `station_code`, `station_number`, `latitude`, `longitude`, `elevation_m`, `matched`
- Types: station identifiers as text; coordinates/elevation numeric; `matched` appears boolean-like
- Missing values: none observed in the loaded columns
- Ranges observed:
  - Latitude: 36.881 to 44.119
  - Longitude: 139.245 to 145.739
  - Elevation: -6680 to 1205 m
  - `matched` is uniformly `True`
- Example row format:
  - `A.ASMS,5572,40.885667,140.874000,-3,True`
- Notes for downstream use:
  - Useful for station-coverage diagnostics and proximity queries around the catalog and major earthquakes.

#### Organization and Naming Conventions
- Event catalogs are stored as CSV tables with compact column names (`lat`, `lon`, `dep`, `mag`) or more verbose mechanism fields (`lat_deg`, `lon_deg`, `depth_km`).
- Major earthquakes are stored separately with an `index` label (`M1`, `M2`, `M3`) and their origin time/location/magnitude.
- Mechanism rows use an `event_code` identifier and a timestamp formatted as text.
- Station entries use dot-separated network.station codes such as `A.ASMS`.

#### Practical Loading Notes
- For stage-1 catalog construction, the key fields to parse from `Snet_catalog_relocate.csv` are `datetime`, `lat`, `lon`, `dep`, and `mag`.
- For major-event matching, `main_earthquake.csv` provides the target event list and `Snet_catalog_relocate.csv` provides the candidate regional events.
- For background characterization and coverage diagnostics, combine the relocated catalog, station file, and mechanism catalog; however, the mechanism file includes incomplete rows and at least one conspicuous depth outlier that should be inspected before analysis.

------------------------------

## catalog/Snet_catalog_relocate.csv
**Source path**: `catalog/Snet_catalog_relocate.csv`
### Summary
This file is the main relocated regional earthquake catalog for the study area. It contains 22,096 events with origin time, latitude, longitude, depth, and magnitude, and has no missing values or duplicate rows in the inspected version.
### Detail
#### File Overview
- **Format:** CSV
- **Purpose:** Main regional relocated earthquake catalog for background seismicity and event matching
- **Records:** 22,096
- **Columns:** 5

#### Schema
| Column | Type (observed) | Notes |
|---|---:|---|
| `datetime` | string | ISO-like UTC timestamp, e.g. `2025-09-30T16:09:25.360000Z` |
| `lat` | float64 | Event latitude |
| `lon` | float64 | Event longitude |
| `dep` | float64 | Depth in km |
| `mag` | float64 | Magnitude |

#### Basic Data Quality
- **Missing values:** none in any column
- **Duplicate rows:** none detected
- **Event ID column:** not present
- **Usable fields for Stage-1 catalog:** `datetime`, `lat`, `lon`, `dep`, `mag`

#### Observed Value Ranges
- **Time span:** `2025-09-30T16:09:25.360000Z` to `2026-05-01T14:44:22.450000Z`
- **Latitude:** 38.503003 to 42.382633
- **Longitude:** 141.001921 to 144.498470
- **Depth:** 0.05 to 121.14 km
- **Magnitude:** -0.5 to 7.7

#### Content Notes
- The catalog is suitable for parsing into a clean Stage-1 earthquake table with standardized time and numeric hypocenter/magnitude fields.
- The magnitude range includes a small number of very small/negative values, so downstream cleaning may wish to preserve them but flag them as low-magnitude events.
- No event identifiers, quality flags, or mechanism/station fields are included in this file; those must be joined from other tables if needed.

#### Recommended Ingestion Pattern
- Parse `datetime` as UTC time.
- Cast `lat`, `lon`, `dep`, and `mag` to numeric types.
- Add derived quality flags during cleaning, such as validity checks for coordinates, depth, and magnitude, and a duplicate indicator if combining with other catalogs.

------------------------------

## catalog/main_earthquake.csv
**Source path**: `catalog/main_earthquake.csv`
### Summary
This file is a small table of three major earthquakes used as reference events for catalog matching and regional-context analysis. It contains event labels, origin times, locations, depths, and magnitudes, with no missing values or duplicate rows in the inspected version.
### Detail
#### File Overview
- **Format:** CSV
- **Purpose:** Reference list of major earthquakes for matching against the relocated regional catalog
- **Records:** 3
- **Columns:** 6

#### Schema
| Column | Type (observed) | Notes |
|---|---:|---|
| `index` | string | Event label / identifier (`M1`, `M2`, `M3`) |
| `datetime` | string | Origin time in a human-readable timestamp format |
| `lat` | float64 | Event latitude |
| `lon` | float64 | Event longitude |
| `dep` | float64 | Depth in km |
| `mag` | float64 | Magnitude |

#### Basic Data Quality
- **Missing values:** none
- **Duplicate rows:** none detected
- **Usable fields for matching:** all six columns are usable
- **Event ID availability:** yes, via `index`

#### Observed Value Ranges
- **Time span:** `2025-11-09 08:03:39.240` to `2026-04-20 07:52:58.060`
- **Latitude:** 39.402 to 40.968
- **Longitude:** 142.288 to 143.507
- **Depth:** 15.9 to 53.5 km
- **Magnitude:** 6.9 to 7.7

#### Content Notes
- The file is intended to be matched to the relocated catalog with allowance for small time differences caused by relocation.
- The event labels (`M1`, `M2`, `M3`) can be used as stable keys in downstream merging and reporting.
- Because the table is very small, it is best treated as a reference/annotation file rather than a catalog for statistical analysis.

#### Recommended Ingestion Pattern
- Parse `datetime` as a timestamp string.
- Preserve `index` as the major-event identifier.
- Join by nearest time/location against `catalog/Snet_catalog_relocate.csv` when building a matched event table.

------------------------------

## source_mechanism/Snet_mecha.csv
**Source path**: `source_mechanism/Snet_mecha.csv`
### Summary
This file is a regional source-mechanism catalog with 354 earthquake records and 29 fields covering origin time, hypocenter, magnitudes, station counts, focal-mechanism geometry, and provenance. Most entries contain core hypocenter/magnitude information, while focal-mechanism details are present only for a subset, making the file useful for mechanism availability and quality audits.
### Detail
#### File Overview
- **Format:** CSV
- **Purpose:** Earthquake source-mechanism catalog for regional events
- **Records:** 354
- **Columns:** 29

#### Schema
| Column | Type (observed) | Notes |
|---|---:|---|
| `event_code` | string | Event identifier |
| `origin_time` | string | Origin time as text timestamp |
| `lat_deg` | float64 | Latitude in degrees |
| `lon_deg` | float64 | Longitude in degrees |
| `depth_km` | float64 | Depth field as stored in kilometers |
| `mag_1` | float64 | Primary magnitude |
| `mag_1_type` | string | Magnitude type for `mag_1` |
| `mag_2` | float64 | Secondary magnitude, partially missing |
| `mag_2_type` | string | Secondary magnitude type, partially missing |
| `region_name` | string | Region label |
| `n_hypo_stations` | int64 | Number of hypocenter stations |
| `m_method` | string | Method code, partially missing |
| `m_source` | string | Source code, partially missing |
| `P_axis_azimuth` | float64 | P-axis azimuth, partially missing |
| `P_axis_dip` | float64 | P-axis dip, partially missing |
| `T_axis_azimuth` | float64 | T-axis azimuth, partially missing |
| `T_axis_dip` | float64 | T-axis dip, partially missing |
| `N_axis_azimuth` | float64 | N-axis azimuth, partially missing |
| `N_axis_dip` | float64 | N-axis dip, partially missing |
| `strike_plane1` | float64 | Nodal-plane 1 strike, partially missing |
| `dip_plane1` | float64 | Nodal-plane 1 dip, partially missing |
| `rake_plane1` | float64 | Nodal-plane 1 rake, partially missing |
| `strike_plane2` | float64 | Nodal-plane 2 strike, partially missing |
| `dip_plane2` | float64 | Nodal-plane 2 dip, partially missing |
| `rake_plane2` | float64 | Nodal-plane 2 rake, partially missing |
| `focal_mech_score` | float64 | Mechanism quality score, partially missing |
| `n_mech_stations` | float64 | Number of mechanism stations, partially missing |
| `focal_mech_projection` | string | Projection label, partially missing |
| `source_file` | string | Provenance file name |

#### Basic Data Quality
- **Missing values:** present in many mechanism-related fields
  - Approximately 215 records lack the secondary magnitude and focal-mechanism fields
- **Duplicate rows:** none detected
- **Core usable fields:** `event_code`, `origin_time`, `lat_deg`, `lon_deg`, `depth_km`, `mag_1`, `mag_1_type`, `region_name`, `n_hypo_stations`, `source_file`
- **Mechanism fields available only for a subset:** P/T/N axes, nodal planes, quality score, and projection

#### Observed Value Ranges
- **Time span:** `2025-10-01 02:56:38.820` to `2026-05-19 10:23:35.210`
- **Latitude:** 38.176833333333335 to 42.9495
- **Longitude:** 140.15766666666667 to 145.617
- **Depth:** 0.0 to 16180.0 as stored
- **Primary magnitude (`mag_1`):** 3.2 to 7.5
- **Secondary magnitude (`mag_2`):** 3.5 to 7.4 where present
- **Hypocenter stations (`n_hypo_stations`):** 7 to 41
- **Mechanism stations (`n_mech_stations`):** 45 to 329 where present
- **Focal-mechanism score:** 86 to 100 where present

#### Content Notes
- The `depth_km` maximum of 16,180 is a conspicuous outlier relative to typical earthquake depths and should be checked during cleaning; it may indicate a unit/parsing issue or an exceptional placeholder value.
- The file is mixed-quality: hypocenter and primary magnitude data are broadly complete, while many mechanism descriptors are absent.
- `event_code` is a stable identifier that can be used for joins, deduplication, and provenance tracking.

#### Recommended Ingestion Pattern
- Parse `origin_time` as a timestamp.
- Keep `event_code` as the event key.
- Treat focal-mechanism fields as optional and add availability flags.
- Validate `depth_km` before analysis, especially for extreme values.
- Use `source_file` to trace mechanism records back to their originating text files if needed.

------------------------------

## stations/station.sta
**Source path**: `stations/station.sta`
### Summary
This file is a station inventory table with 371 station records and six fields describing station identity, coordinates, elevation, and a matched-status flag. It has no missing values or duplicate rows, and all stations are marked as matched in the inspected version.
### Detail
#### File Overview
- **Format:** comma-delimited text / STA-style station table
- **Purpose:** station metadata for coverage and geometry diagnostics
- **Records:** 371
- **Columns:** 6

#### Schema
| Column | Type (observed) | Notes |
|---|---:|---|
| `station_code` | string | Station identifier, often network-prefixed (e.g. `A.ASMS`) |
| `station_number` | int64 / numeric | Station numeric code |
| `latitude` | float64 | Station latitude |
| `longitude` | float64 | Station longitude |
| `elevation_m` | float64 | Elevation in meters; includes negative values |
| `matched` | boolean-like | All rows observed as `True` |

#### Basic Data Quality
- **Missing values:** none in any column
- **Duplicate rows:** none detected
- **Usable fields for station-coverage diagnostics:** all columns

#### Observed Value Ranges
- **Station number:** 504 to 8087
- **Latitude:** 36.880833 to 44.118833
- **Longitude:** 139.245333 to 145.738833
- **Elevation:** -6680 to 1205 m
- **Matched flag:** uniformly `True`

#### Content Notes
- The coordinate extent covers a broad regional footprint suitable for earthquake-to-station distance and coverage checks.
- The very low elevation minimum suggests some stations may be offshore or that the elevation field uses bathymetric values; this is worth preserving but may need interpretation during analysis.
- Since all `matched` values are `True`, the file appears to represent a curated station list rather than a partial/failed match result.

#### Recommended Ingestion Pattern
- Read as a simple tabular station inventory.
- Preserve `station_code` as the primary key.
- Cast `matched` to boolean.
- Use `latitude`, `longitude`, and `elevation_m` for spatial coverage summaries and map overlays.

------------------------------

