# Data Descriptions
## data
**Source path**: `<CASE_ROOT>/data`
### Summary
This data folder is organized around a relocated local earthquake catalog, a 3-event mainshock reference table, focal-mechanism metadata, station metadata, and several precomputed event-screening tables relevant to M1-M3 catalog-level screening. The key input catalog is a CSV with an explicit header and 25,646 events spanning 2025-06-01 to 2026-05-01, while supporting tables provide mainshock coordinates/times, mechanism coverage for larger events, and geometry/burst classifications for local-zone subset selection.
### Detail
#### Folder Structure

Top-level subdirectories under `data/`:

- `catalog/` — main earthquake catalogs and notebook assets
- `event_screen/` — precomputed geometry and burst-screening tables for M1-M3 local analyses
- `source_mechanism/` — focal mechanism metadata table
- `stations/` — station metadata files
- `active_fault/` — regional active fault GeoJSON
- `DEM/` — topography rasters

Representative files relevant to the requested catalog screening:

- `data/catalog/Snet_catalog_relocate_250601_260501.csv`
- `data/catalog/main_earthquake.csv`
- `data/source_mechanism/Snet_mecha.csv`
- `data/stations/station.sta`
- `data/event_screen/m1_m3_event_geometry.csv`
- `data/event_screen/m1_m3_burst_table_raw.csv`
- `data/event_screen/m1_m3_burst_table_m2aware.csv`
- `data/event_screen/m1_m3_burst_summary.csv`
- `data/event_screen/m1_m3_depth_domain_summary.csv`
- `data/event_screen/m1_m3_event_chain_table.csv`

Other files exist for context or visualization support, including alternate relocated catalogs, notebooks, a fault GeoJSON, and DEM rasters.

#### Key Catalog Files

##### 1) `catalog/Snet_catalog_relocate_250601_260501.csv`

- Format: CSV with an explicit header row
- Size: 1,506,736 bytes
- Rows: 25,646 events
- Columns: `datetime`, `lat`, `lon`, `dep`, `mag`
- Loading note: preserve the named columns and map `dep` to the working
  `depth_km` field used by the analysis code.

Suggested schema:

- `datetime`: ISO8601 string with trailing `Z`
- `lat`: float
- `lon`: float
- `dep`: float, mapped to the working `depth_km` field
- `mag`: float

Coverage/statistics:

- Time range: `2025-06-01T00:13:38.900000Z` to `2026-05-01T14:44:22.450000Z`
- Duplicate origin times: 0
- Latitude range: 38.50304 to 42.382633
- Longitude range: 141.000635 to 144.49847
- Depth range: 0.0 to 125.3 km
- Magnitude range: -0.5 to 7.7
- Median depth: ~16.495 km
- Median magnitude: 1.5

Example record structure:

- `2025-06-01T00:13:38.900000Z,39.245593,142.382422,29.7,1.7`

Caution for future agents:

- The catalog depth range is 0.0--125.3 km and remains relevant to
  depth-sensitive interpretation.
- The CSV has an explicit header; readers should preserve the named columns and map `dep` to the working `depth_km` field.

##### 2) `catalog/main_earthquake.csv`

- Format: standard CSV with header
- Size: 184 bytes
- Rows: 3
- Columns:
  - `index`
  - `datetime`
  - `lat`
  - `lon`
  - `dep`
  - `mag`

Contents define the three reference events used throughout the M1-M3 framework:

- `M1`: 2025-11-09 08:03:39.240, 39.402, 143.507, 15.9 km, M6.9
- `M2`: 2025-12-08 14:15:10.180, 40.968, 142.288, 53.5 km, M7.5
- `M3`: 2026-04-20 07:52:58.060, 39.842, 143.157, 19.4 km, M7.7

This is the key lookup table for building phase windows and geometric subsets.

#### Precomputed Event-Screening Tables

##### 3) `event_screen/m1_m3_event_geometry.csv`

- Format: CSV with header
- Rows: 25,646
- Columns: 30
- Purpose: event-by-event geometric bookkeeping relative to M1, M2, and M3, plus local/corridor/burst flags

Columns:

- Event basics:
  - `time`, `latitude`, `longitude`, `depth_km`, `magnitude`, `event_id`
- Distances and local coordinates:
  - `dist_m1_km`, `dist_m2_km`, `dist_m3_km`
  - `x_from_m1_km`, `y_from_m1_km`
  - `projected_km`, `perp_km`, `axis_fraction`
- Geometric subset flags:
  - `between_endpoints`
  - `local_union`
  - `m1_core`, `m3_core`
  - `m1_extended`, `m3_extended`
  - `m2_related`
  - `corridor_20`, `corridor_30`
  - `off_corridor_20`, `off_corridor_30`
- Relative time variables:
  - `days_since_start`, `days_since_m1`, `days_until_m3`
- Burst labeling:
  - `burst_id`, `burst_rank`

Observed boolean counts:

- `local_union`: 9,109
- `m1_core`: 4,460
- `m3_core`: 2,851
- `m1_extended`: 7,402
- `m3_extended`: 7,268
- `m2_related`: 10,049
- `corridor_20`: 9,109
- `corridor_30`: 9,109
- `off_corridor_20`: 0
- `off_corridor_30`: 0

Interpretation note for future agents:

- The corridor/off-corridor counts suggest this file may currently encode `corridor_*` identically to `local_union`, with `off_corridor_*` entirely false. That should be audited before using corridor-vs-off-corridor comparisons.
- `burst_rank` contains many missing values (18,282), consistent with only a subset of events belonging to identified bursts.

Example fields in the first records show the table is already aligned to the relocated catalog and includes per-event distances and phase-relative timing.

##### 4) `event_screen/m1_m3_burst_table_raw.csv`

- Format: CSV with header
- Rows: 5
- Columns: 17
- Purpose: summarized burst table for thresholded burst groupings in the raw event set

Columns:

- `burst_id`
- `mode`
- `threshold`
- `start_time`, `end_time`
- `duration_days`
- `event_count`
- `largest_magnitude`
- `depth_min_km`, `depth_max_km`
- `centroid_lat`, `centroid_lon`
- `centroid_along_km`
- `dominant_summary_category`
- `corridor30_fraction`
- `off_corridor_fraction`
- `m2_related_fraction`

Example categories present in preview:

- `M1_core`
- `off_corridor_local`

Companion file:

- `event_screen/m1_m3_burst_table_m2aware.csv` likely mirrors this structure for an M2-aware screening variant.

##### 5) Other `event_screen/` files

These were not fully inspected but are clearly relevant for future agents:

- `m1_m3_burst_summary.csv` — likely aggregate burst metrics by threshold/category
- `m1_m3_depth_domain_summary.csv` — likely precomputed summaries by depth/spatial domain
- `m1_m3_event_chain_table.csv` — likely event-chain or cluster descriptors

Use these as convenience tables, but the authoritative event-level source for subset construction appears to be `m1_m3_event_geometry.csv` plus the base catalog.

#### Focal Mechanism Metadata

##### 6) `source_mechanism/Snet_mecha.csv`

- Format: CSV with header
- Size: 61,681 bytes
- Rows: 354
- Columns: 29
- Purpose: focal mechanism and related source metadata for a subset of events

Columns:

- Event/source identifiers and location:
  - `event_code`, `origin_time`, `lat_deg`, `lon_deg`, `depth_km`
- Magnitudes:
  - `mag_1`, `mag_1_type`, `mag_2`, `mag_2_type`
- Context and method:
  - `region_name`, `n_hypo_stations`, `m_method`, `m_source`
- Principal axes:
  - `P_axis_azimuth`, `P_axis_dip`
  - `T_axis_azimuth`, `T_axis_dip`
  - `N_axis_azimuth`, `N_axis_dip`
- Nodal planes:
  - `strike_plane1`, `dip_plane1`, `rake_plane1`
  - `strike_plane2`, `dip_plane2`, `rake_plane2`
- Quality/provenance:
  - `focal_mech_score`, `n_mech_stations`, `focal_mech_projection`, `source_file`

Coverage/statistics:

- Time range: `2025-10-01 02:56:38.820` to `2026-05-19 10:23:35.210`
- `mag_1` range: 3.2 to 7.5
- `mag_2` range: 3.5 to 7.4

Missingness note:

- Many mechanism-geometry columns have 215 missing values, so only part of this table contains full mechanism solutions.
- This table is sparse relative to the 25k-event catalog and magnitude-biased toward larger events; future agents should audit mechanism coverage by time phase, magnitude, and spatial subset before drawing any mechanism-based summary.

#### Station Metadata

##### 7) `stations/station.sta`

- Format: plain text station file
- Preview indicates whitespace-delimited rows
- Example lines:
  - `N.SAIB NH.SAIB. . 40.0133 141.7443 95.1 0.000 0.00`
  - `N.HSWW NH.HSWW. . 40.4297 141.8983 93.7 0.000 0.00`

Likely fields from the preview pattern:

- station/network code string
- alternate station code string
- placeholder/component field
- latitude
- longitude
- elevation or depth-like value
- two additional numeric columns

This file is useful for network geometry context, but column definitions are not self-documented from the preview alone.

##### 8) `stations/japan_stations.txt`

- Additional station list present in the same folder
- Not fully inspected here, but likely redundant or complementary station metadata

#### Context Layers

##### 9) `active_fault/japan_active_faults.geojson`

- Regional active fault geometry in GeoJSON format
- Useful for map context or plotting, not necessary for initial catalog loading

##### 10) `DEM/output_hh.tif` and `DEM/rasters_COP30.tar.gz`

- Raster DEM products for map background/context
- Not required for catalog statistics, but useful for future geographic visualization

#### File Naming and Organization Patterns

- Catalog files use names like `Snet_catalog_relocate_<startYYMMDD>_<endYYMMDD>.csv`
- Burst/geometry summary products in `event_screen/` use `m1_m3_*` prefixes
- Raw vs sensitivity variants are indicated by suffixes like `_raw` and `_m2aware`
- Main reference events are centralized in `catalog/main_earthquake.csv`

Example paths:

- `data/catalog/Snet_catalog_relocate_250601_260501.csv`
- `data/catalog/main_earthquake.csv`
- `data/event_screen/m1_m3_event_geometry.csv`
- `data/event_screen/m1_m3_burst_table_raw.csv`
- `data/source_mechanism/Snet_mecha.csv`
- `data/stations/station.sta`

#### Recommended Loading Notes for Future Agents

- For the relocated catalog, use `pd.read_csv(path)` and map `dep` to the
  working `depth_km` field.
- Parse `time` and `datetime` columns explicitly as datetimes after loading.
- Use `main_earthquake.csv` as the authoritative source for M1/M2/M3 times and coordinates.
- Use `m1_m3_event_geometry.csv` as a convenience table for precomputed local-zone flags, but validate corridor/off-corridor fields before relying on them.
- Treat `Snet_mecha.csv` as partial, magnitude-biased mechanism coverage rather than a complete event-by-event source.
- Depth-sensitive work should retain the catalog quality checks.

------------------------------

## Snet_catalog_relocate_250601_260501.csv
**Source path**: `data/Snet_catalog_relocate_250601_260501.csv`
### Summary
The data directory contains a relocated earthquake catalog plus supporting reference tables needed to build M1-M3 time windows, spatial subsets, mechanism coverage audits, and station-context checks. The main analysis input is a five-column CSV with an explicit header and 25,646 events from 2025-06-01 to 2026-05-01; nearby companion tables provide the M1/M2/M3 reference events, precomputed event geometry flags, burst summaries, and partial focal-mechanism coverage.
### Detail
#### Folder Structure

Relevant subdirectories under `data/` for future catalog-level screening:

- `catalog/` — core earthquake catalogs and the M1/M2/M3 reference table
- `event_screen/` — precomputed event-by-event geometry flags and burst summary tables
- `source_mechanism/` — focal-mechanism metadata for a subset of larger events
- `stations/` — station metadata files for network context
- `active_fault/` and `DEM/` — contextual GIS layers, not required for initial catalog loading

Representative relevant paths:

- `data/catalog/Snet_catalog_relocate_250601_260501.csv`
- `data/catalog/main_earthquake.csv`
- `data/event_screen/m1_m3_event_geometry.csv`
- `data/event_screen/m1_m3_burst_table_raw.csv`
- `data/event_screen/m1_m3_burst_table_m2aware.csv`
- `data/source_mechanism/Snet_mecha.csv`
- `data/stations/station.sta`

#### Primary Catalog File

##### `catalog/Snet_catalog_relocate_250601_260501.csv`

- Format: CSV with an explicit header row
- Size: 1,506,736 bytes
- Event count: 25,646
- Columns: `datetime`, `lat`, `lon`, `dep`, `mag`

Recommended loading pattern:

- Use `pd.read_csv(...)`, then rename `dep` to `depth_km` and parse
  `datetime` as a UTC datetime.

Content range:

- Time span: `2025-06-01T00:13:38.900000Z` to `2026-05-01T14:44:22.450000Z`
- Latitude: 38.50304 to 42.382633
- Longitude: 141.000635 to 144.49847
- Depth: 0.0 to 125.3 km
- Magnitude: -0.5 to 7.7
- Median depth: ~16.495 km
- Median magnitude: 1.5
- Duplicate times: 0

Example row structure:

- `2025-06-01T00:13:38.900000Z,39.245593,142.382422,29.7,1.7`

Important caveats for future agents:

- The header should be preserved when loading the catalog, and `dep` should
  be mapped to the working `depth_km` field.
- Depth-dependent workflows should retain the catalog quality checks and
  report the observed 0.0--125.3 km range.
- This file is the authoritative event-level source for time, location, depth, and magnitude.

#### Mainshock Reference Table

##### `catalog/main_earthquake.csv`

- Format: standard CSV with header
- Rows: 3
- Columns:
  - `index`
  - `datetime`
  - `lat`
  - `lon`
  - `dep`
  - `mag`

Entries:

- `M1` — `2025-11-09 08:03:39.240`, lat 39.402, lon 143.507, dep 15.9, mag 6.9
- `M2` — `2025-12-08 14:15:10.180`, lat 40.968, lon 142.288, dep 53.5, mag 7.5
- `M3` — `2026-04-20 07:52:58.060`, lat 39.842, lon 143.157, dep 19.4, mag 7.7

Use this file as the authoritative source for:

- phase-boundary construction
- M1/M2/M3-centered spatial distances
- event classification relative to the three reference shocks

#### Precomputed Geometry and Subset Flags

##### `event_screen/m1_m3_event_geometry.csv`

- Format: CSV with header
- Rows: 25,646
- Columns: 30
- Purpose: event-by-event geometric bookkeeping relative to M1/M2/M3, plus local-zone and burst flags

Columns:

- Base event fields:
  - `time`, `latitude`, `longitude`, `depth_km`, `magnitude`, `event_id`
- Distance and coordinate fields:
  - `dist_m1_km`, `dist_m2_km`, `dist_m3_km`
  - `x_from_m1_km`, `y_from_m1_km`
  - `projected_km`, `perp_km`, `axis_fraction`
- Spatial boolean flags:
  - `between_endpoints`
  - `local_union`
  - `m1_core`, `m3_core`
  - `m1_extended`, `m3_extended`
  - `m2_related`
  - `corridor_20`, `corridor_30`
  - `off_corridor_20`, `off_corridor_30`
- Relative-time fields:
  - `days_since_start`, `days_since_m1`, `days_until_m3`
- Burst labels:
  - `burst_id`, `burst_rank`

Observed counts of key boolean flags:

- `local_union`: 9,109
- `m1_core`: 4,460
- `m3_core`: 2,851
- `m1_extended`: 7,402
- `m3_extended`: 7,268
- `m2_related`: 10,049
- `corridor_20`: 9,109
- `corridor_30`: 9,109
- `off_corridor_20`: 0
- `off_corridor_30`: 0

Practical notes:

- This table is useful for rapidly selecting the user-requested subsets without recomputing distances.
- The current corridor/off-corridor counts imply a likely encoding issue or a placeholder definition: `corridor_20` and `corridor_30` match `local_union`, while both off-corridor flags are always false. Future agents should validate these columns before using them for along-axis vs off-axis comparisons.
- `burst_rank` is missing for many events, consistent with only some events being assigned to bursts.

#### Burst Summary Tables

##### `event_screen/m1_m3_burst_table_raw.csv`

- Format: CSV with header
- Rows: 5
- Columns: 17

Columns:

- `burst_id`
- `mode`
- `threshold`
- `start_time`, `end_time`
- `duration_days`
- `event_count`
- `largest_magnitude`
- `depth_min_km`, `depth_max_km`
- `centroid_lat`, `centroid_lon`
- `centroid_along_km`
- `dominant_summary_category`
- `corridor30_fraction`
- `off_corridor_fraction`
- `m2_related_fraction`

Previewed values show this is a compact burst-level summary table with categories such as:

- `M1_core`
- `off_corridor_local`

Likely use:

- quick burst inventory
- burst durations and counts
- magnitude hierarchy at burst level
- category assignment for raw event set

##### `event_screen/m1_m3_burst_table_m2aware.csv`

- Not fully inspected, but naming indicates the same burst summary concept under an M2-aware screening variant.

##### Other related `event_screen/` files

- `m1_m3_burst_summary.csv`
- `m1_m3_depth_domain_summary.csv`
- `m1_m3_event_chain_table.csv`

These appear to be convenience summary products for precomputed screening and may help future agents avoid re-deriving some basic partitions.

#### Focal Mechanism Metadata

##### `source_mechanism/Snet_mecha.csv`

- Format: CSV with header
- Size: 61,681 bytes
- Rows: 354
- Columns: 29

Columns:

- Event identification and hypocenter:
  - `event_code`, `origin_time`, `lat_deg`, `lon_deg`, `depth_km`
- Magnitudes:
  - `mag_1`, `mag_1_type`, `mag_2`, `mag_2_type`
- Region/method metadata:
  - `region_name`, `n_hypo_stations`, `m_method`, `m_source`
- Principal axes:
  - `P_axis_azimuth`, `P_axis_dip`
  - `T_axis_azimuth`, `T_axis_dip`
  - `N_axis_azimuth`, `N_axis_dip`
- Nodal planes:
  - `strike_plane1`, `dip_plane1`, `rake_plane1`
  - `strike_plane2`, `dip_plane2`, `rake_plane2`
- Quality/provenance:
  - `focal_mech_score`, `n_mech_stations`, `focal_mech_projection`, `source_file`

Coverage characteristics:

- Time range: `2025-10-01 02:56:38.820` to `2026-05-19 10:23:35.210`
- `mag_1` range: 3.2 to 7.5
- `mag_2` range: 3.5 to 7.4
- Many mechanism geometry fields have 215 missing values, indicating only partial solution coverage

Implications for future agents:

- Mechanism coverage is sparse relative to the full 25,646-event catalog.
- The table is magnitude-biased toward larger events and begins months after the catalog start, so phase-based or spatial-class mechanism comparisons require explicit coverage auditing before interpretation.
- This is appropriate for metadata screening, not for assuming uniform focal-mechanism availability across phases.

#### Station Metadata

##### `stations/station.sta`

- Format: plain text, whitespace-delimited
- Example preview lines:
  - `N.SAIB NH.SAIB. . 40.0133 141.7443 95.1 0.000 0.00`
  - `N.HSWW NH.HSWW. . 40.4297 141.8983 93.7 0.000 0.00`

Likely contents include:

- station/network identifiers
- latitude and longitude
- elevation or depth-like field
- additional numeric metadata columns

Use case:

- station/network context only
- not required for basic catalog statistics, but useful if a future agent needs to document network coverage or quality-control context

#### Additional Context Files

- `active_fault/japan_active_faults.geojson` — fault geometry context for mapping
- `DEM/output_hh.tif` and `DEM/rasters_COP30.tar.gz` — topographic context layers
- notebooks and PNGs in `catalog/` — workflow artifacts, not authoritative input tables

#### Naming and Organization Conventions

Patterns visible in this directory:

- Relocated catalogs use names like `Snet_catalog_relocate_<startYYMMDD>_<endYYMMDD>.csv`
- Event-screening products use `m1_m3_...` prefixes and are grouped in `event_screen/`
- Alternative filtering modes are indicated by suffixes like `_raw` and `_m2aware`
- Main reference events are centralized in `catalog/main_earthquake.csv`

#### Recommended Priority for Future Agents

For the requested M1-M3 catalog screening, inspect in this order:

1. `catalog/Snet_catalog_relocate_250601_260501.csv` — authoritative event list
2. `catalog/main_earthquake.csv` — M1/M2/M3 reference times and locations
3. `event_screen/m1_m3_event_geometry.csv` — precomputed local-zone flags and relative times
4. `event_screen/m1_m3_burst_table_raw.csv` and `_m2aware.csv` — burst-level summary metadata
5. `source_mechanism/Snet_mecha.csv` — only for mechanism-coverage audit, not assumed complete
6. `stations/station.sta` — optional network-context file

#### Minimal Load Recipe

A future agent can safely load the essential tables as:

- Catalog: CSV with an explicit header and named source columns
- Mainshocks: normal CSV
- Event geometry: normal CSV with existing subset flags
- Mechanisms: normal CSV, but with explicit missingness checks

This combination is sufficient to reconstruct time windows, local spatial subsets, M2-related flags, burst IDs, and mechanism-coverage metadata without generating derived outputs.

------------------------------

## main_earthquake.csv
**Source path**: `catalog/main_earthquake.csv`
### Summary
This is a small reference CSV defining the three main earthquakes used as anchors for all M1-M3 temporal and spatial bookkeeping. It contains event labels, origin times, hypocenter coordinates, depths, and magnitudes for M1, M2, and M3, and should be treated as the authoritative source for phase-window boundaries and distance-based subset definitions.
### Detail
#### File Overview

- Path: `data/catalog/main_earthquake.csv`
- Format: CSV with header
- Size: 184 bytes
- Shape: 3 rows × 6 columns
- Purpose: reference table for the three principal events used throughout the M1-M3 catalog-screening workflow

This file is the key lookup table for:

- defining M1, M2, and M3 event times
- constructing pre-M1, M1-related, middle-phase, and pre-M3 windows
- computing distances from catalog events to M1, M2, and M3
- defining M1-centered and M3-centered local/core/extended spatial subsets

#### Columns

The file has the following columns:

- `index` — event label (`M1`, `M2`, `M3`)
- `datetime` — origin time as string with fractional seconds
- `lat` — latitude in decimal degrees
- `lon` — longitude in decimal degrees
- `dep` — depth in km
- `mag` — magnitude

Data types as read by pandas:

- `index`: object
- `datetime`: object
- `lat`: float64
- `lon`: float64
- `dep`: float64
- `mag`: float64

No missing values were detected in any column.

#### Row Contents

The three rows are:

- `M1`, `2025-11-09 08:03:39.240`, `39.402`, `143.507`, `15.9`, `6.9`
- `M2`, `2025-12-08 14:15:10.180`, `40.968`, `142.288`, `53.5`, `7.5`
- `M3`, `2026-04-20 07:52:58.060`, `39.842`, `143.157`, `19.4`, `7.7`

#### Metadata Relevant for Future Agents

##### Temporal role

These timestamps are the anchors for the user-requested phase definitions. A future agent can derive windows such as:

- catalog start to `M1 - 14 days`
- catalog start to `M1 - 7 days`
- `M1 - 14 days` to `M1 + 21 days`
- `M1 + 21 days` to `M3 - 35 days`
- `M3 - 35 days` to `M3`
- sensitivity windows around `M1` and `M3`

Because `datetime` is stored as text, it should be parsed explicitly to pandas datetime before use.

##### Spatial role

The `lat`, `lon`, and `dep` columns provide the reference hypocenters needed to compute:

- distance to M1, M2, and M3
- M1-centered and M3-centered core zones
- M1-centered and M3-centered extended zones
- M1-M3 combined local union
- along-axis/corridor projections between M1 and M3
- M2-related flags for sensitivity or exclusion checks

##### Magnitude role

The `mag` column provides the mainshock sizes used for labeling/context, but not for derived catalog calculations by itself. The values are:

- M1: 6.9
- M2: 7.5
- M3: 7.7

#### Loading Notes

Recommended load pattern:

- `pd.read_csv('data/catalog/main_earthquake.csv')`
- then convert `datetime` with `pd.to_datetime(...)`

Suggested indexing pattern for later code:

- set `index` as the dataframe index so rows can be accessed directly as `M1`, `M2`, and `M3`

Example path usage:

- `data/catalog/main_earthquake.csv`

#### Reliability/Usage Notes

- This is a compact, complete reference table with no detected missing values.
- It should be treated as the authoritative source for M1/M2/M3 event metadata rather than retyping values elsewhere.
- Any future geometric or phase-based screening should derive boundaries directly from this file to avoid hard-coded inconsistencies.

------------------------------

## Snet_mecha.csv
**Source path**: `source_mechanism/Snet_mecha.csv`
### Summary
This file is a focal-mechanism metadata table for a subset of larger events, not a complete catalog-wide mechanism inventory. It contains 354 rows with event identifiers, origin times, hypocenters, one or two magnitudes, mechanism axes, nodal planes, and quality/provenance fields, but many mechanism-geometry fields are missing, so coverage should be audited before any phase or spatial comparison.
### Detail
#### File Overview

- Path: `data/source_mechanism/Snet_mecha.csv`
- Format: CSV with header
- Size: 61,681 bytes
- Shape: 354 rows × 29 columns
- Purpose: focal-mechanism and source metadata for a subset of earthquakes, likely biased toward larger and/or better-observed events

This file is relevant for future agents only as a **mechanism coverage/context table**. It should not be assumed to provide complete or uniform mechanism information across all M1-M3 phases, spatial subsets, or magnitude ranges.

#### Columns

The table contains the following columns:

- `event_code`
- `origin_time`
- `lat_deg`
- `lon_deg`
- `depth_km`
- `mag_1`
- `mag_1_type`
- `mag_2`
- `mag_2_type`
- `region_name`
- `n_hypo_stations`
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
- `source_file`

#### Column Roles

##### Event identification and basic hypocenter information

- `event_code` — event identifier/code
- `origin_time` — origin time string
- `lat_deg`, `lon_deg` — epicentral coordinates in decimal degrees
- `depth_km` — event depth in km

These fields can be used to merge or approximately match with the relocated catalog if exact identifiers/timestamps are compatible.

##### Magnitude fields

- `mag_1`, `mag_1_type`
- `mag_2`, `mag_2_type`

This suggests the table may preserve two magnitude estimates or products per event. Future agents should check which magnitude column is most consistent with the main catalog before using one for threshold audits.

Observed ranges:

- `mag_1`: 3.2 to 7.5
- `mag_2`: 3.5 to 7.4

##### Regional/method metadata

- `region_name`
- `n_hypo_stations`
- `m_method`
- `m_source`

These fields describe source region and possibly the inversion or derivation method. They are useful for coverage auditing and provenance checks.

##### Mechanism geometry

Principal axes:

- `P_axis_azimuth`, `P_axis_dip`
- `T_axis_azimuth`, `T_axis_dip`
- `N_axis_azimuth`, `N_axis_dip`

Nodal planes:

- `strike_plane1`, `dip_plane1`, `rake_plane1`
- `strike_plane2`, `dip_plane2`, `rake_plane2`

These provide the actual focal-mechanism geometry where available.

##### Quality/provenance fields

- `focal_mech_score`
- `n_mech_stations`
- `focal_mech_projection`
- `source_file`

These are the main fields a future agent should inspect first when deciding whether mechanism information is robust enough for any descriptive comparison.

#### Time and Magnitude Coverage

Observed overall coverage:

- Earliest `origin_time`: `2025-10-01 02:56:38.820`
- Latest `origin_time`: `2026-05-19 10:23:35.210`

Implications:

- Mechanism coverage starts well after the catalog start (`2025-06-01` in the relocated catalog).
- The file extends beyond the relocated catalog end (`2026-05-01`), so not all mechanism rows necessarily belong to the exact target catalog interval.
- Mechanism availability is concentrated in moderate-to-large events rather than the full small-event population used for b-value work.

This makes the file suitable for **coverage auditing** but not for assuming representative mechanism sampling across pre-M1 baseline, M1-related, middle-phase, pre-M3, or post-M3 subsets.

#### Missingness / Completeness Notes

Many mechanism fields are incomplete. The largest missing-value counts observed were 215 for several columns, including:

- `P_axis_dip`
- `T_axis_azimuth`
- `T_axis_dip`
- `N_axis_azimuth`
- `dip_plane1`
- `rake_plane1`
- `strike_plane2`
- `m_method`
- `m_source`

Interpretation:

- Only a subset of the 354 rows contains full focal-mechanism geometry.
- Some rows may be source/event metadata without a complete mechanism solution.
- Future agents should explicitly check per-column non-null counts before attempting any mechanism-class summaries.

#### Relevance for the Requested Workflow

For the user’s requested M1-M3 catalog screening, this file is most relevant for:

- auditing whether focal-mechanism coverage exists in each major phase window
- checking whether mechanism coverage is biased toward larger magnitudes
- checking whether M1-centered, M3-centered, corridor-like, or off-corridor subsets have enough mechanism-bearing events to summarize
- documenting when mechanism evidence is unavailable, sparse, or exploratory

This file is **not** sufficient by itself for:

- complete event-level classification across the full catalog
- uniform mechanism comparison across all small events
- physical inference without an explicit coverage and quality audit

#### Recommended Loading / Usage Notes

Recommended load pattern:

- `pd.read_csv('data/source_mechanism/Snet_mecha.csv')`
- parse `origin_time` as datetime
- inspect missingness in mechanism geometry and quality columns before any use

Suggested first checks for future agents:

1. Count non-null rows for mechanism-bearing fields such as strike/dip/rake and principal axes.
2. Intersect `origin_time` with the relocated catalog time window.
3. Compare magnitude coverage with the main catalog to quantify bias.
4. If spatial classes are needed, merge with precomputed event geometry using time/location matching or event IDs if available.

#### Example Path

- `data/source_mechanism/Snet_mecha.csv`

#### Bottom-Line Metadata Summary

This is a partial focal-mechanism metadata table with 354 events and rich geometry/quality columns, but it is incomplete and temporally/magnitude biased. Future agents should treat it as an auxiliary screening dataset for mechanism availability and provenance, not as a complete or phase-balanced mechanism catalog.

------------------------------

## station.sta
**Source path**: `stations/station.sta`
### Summary
This is a plain-text station metadata file containing whitespace-delimited station records with network/station identifiers and geographic coordinates. It is useful as observational-network context for future quality-control or coverage documentation, but it is not a primary catalog-analysis input and its column definitions should be verified before structured use.
### Detail
#### File Overview

- Path: `data/stations/station.sta`
- Format: plain text, whitespace-delimited station list
- Purpose: station/network metadata for the seismic observation system used in or associated with the catalog workflow

This file is relevant mainly for future agents that need to document:

- station distribution around the Aomori study region
- observational-network context for relocation or mechanism availability
- possible quality-control context for depth or magnitude interpretation

It is not required for direct loading of the earthquake catalog or the M1-M3 subset definitions.

#### Previewed Record Structure

The first few lines have the pattern:

- `N.SAIB NH.SAIB. . 40.0133 141.7443 95.1 0.000 0.00`
- `N.HSWW NH.HSWW. . 40.4297 141.8983 93.7 0.000 0.00`

This indicates a whitespace-separated schema with approximately 8 fields per row.

#### Likely Field Layout

Based on the preview only, each row appears to contain:

1. primary station/network code
2. alternate or full station code
3. placeholder/component/channel field (shown as `.` in preview)
4. latitude
5. longitude
6. elevation or depth-like numeric field
7. additional numeric field
8. additional numeric field

Example parsed interpretation from the first row:

- primary code: `N.SAIB`
- alternate code: `NH.SAIB.`
- placeholder: `.`
- latitude: `40.0133`
- longitude: `141.7443`
- numeric field: `95.1`
- numeric field: `0.000`
- numeric field: `0.00`

#### Metadata Characteristics

- File type: human-readable text
- Delimiter style: whitespace rather than commas
- Coordinate fields are clearly present and appear to be decimal degrees
- The station identifiers include dotted code strings, so this should be parsed with generic whitespace splitting rather than assuming simple alphanumeric station names

#### Relevance to the Requested Workflow

For the M1-M3 catalog-level screening task, this file is secondary context only. It may help future agents with:

- documenting network geometry in relation to the M1/M3 local zone
- checking whether focal-mechanism or relocation coverage might be uneven geographically
- providing context if catalog quality or depth outliers need network-based discussion

It is not needed for:

- computing b-values
- constructing phase windows
- selecting M1/M3 local subsets
- calculating magnitude hierarchy or moment proxies

Those tasks should rely primarily on the relocated catalog, mainshock table, and event geometry table.

#### Loading Notes

Recommended approach:

- read as plain text with whitespace splitting
- inspect the number of columns per row before assigning final names
- avoid assuming the last three numeric columns are standardized unless confirmed elsewhere in the workflow

A future agent could start with something like a whitespace-delimited read and then inspect:

- station code columns
- latitude/longitude ranges
- whether the sixth numeric field is elevation, sensor depth, or another site attribute

#### Limitations

- Column names are not self-documented in the inspected preview.
- Full field definitions cannot be confirmed from the first few lines alone.
- Any formal use beyond simple station mapping should first verify the schema against notebooks or companion station files such as `data/stations/japan_stations.txt`.

#### Example Path

- `data/stations/station.sta`

#### Bottom-Line Description

This is a whitespace-delimited station inventory file with station identifiers and coordinates, intended mainly for network-context reference. Future agents should treat it as auxiliary metadata and verify the exact schema before using it in any structured station-level analysis.

------------------------------
