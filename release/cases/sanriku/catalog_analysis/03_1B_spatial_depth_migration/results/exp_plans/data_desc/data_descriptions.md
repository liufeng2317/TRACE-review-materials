# Data Descriptions
## data
**Source path**: `<CASE_ROOT>/data`
### Summary
This data folder contains the relocated Aomori earthquake catalog, event-geometry screening tables, mainshock reference metadata, focal-mechanism metadata, station lists, and supporting geographic context files. For the M1-M3 spatial-depth screening task, the most relevant inputs are the relocated catalog in `catalog/`, the precomputed geometry/burst tables in `event_screen/`, the three-anchor event file `catalog/main_earthquake.csv`, the mechanism table `source_mechanism/Snet_mecha.csv`, and station metadata under `stations/`.
### Detail
#### Folder Structure

Top-level subdirectories relevant to the requested M1-M3 catalog screening:

- `catalog/`
  - Main earthquake catalogs and anchor-event metadata.
  - Relevant files include:
    - `catalog/Snet_catalog_relocate_250601_260501.csv` — relocated/filtered catalog covering roughly 2025-06-01 to 2026-05-01.
    - `catalog/Snet_catalog_relocate_250930_260501.csv` — later-start subset with explicit header.
    - `catalog/main_earthquake.csv` — M1, M2, M3 reference events.
    - Additional notebooks and comparison image files.
- `event_screen/`
  - Precomputed event geometry and screening summaries for the M1-M3 system.
  - Useful for locating prior working-context tables, but future agents should recompute diagnostics as needed rather than treat these as final scientific conclusions.
- `source_mechanism/`
  - `Snet_mecha.csv` with focal-mechanism and principal-axis metadata for a subset of events.
- `stations/`
  - Station metadata in both CSV-like and fixed-column/text-like formats.
- `active_fault/`
  - `japan_active_faults.geojson` for spatial context.
- `DEM/`
  - Raster/topographic context files, not primary for catalog-level screening.

Example paths:

- `/.../data/catalog/Snet_catalog_relocate_250601_260501.csv`
- `/.../data/catalog/main_earthquake.csv`
- `/.../data/event_screen/m1_m3_event_geometry.csv`
- `/.../data/source_mechanism/Snet_mecha.csv`
- `/.../data/stations/station.sta`

#### Primary Catalog File

Most relevant catalog for future analysis:

- `catalog/Snet_catalog_relocate_250601_260501.csv`
  - Size: ~1.51 MB
  - Rows: 25,648 events
  - Format: CSV-like text with **no header row**; should be read with explicit column names.
  - Recommended columns:
    - `datetime`
    - `lat`
    - `lon`
    - `dep`
    - `mag`
  - Time range: `2025-06-01T00:13:38.900000Z` to `2026-05-01T14:44:22.450000Z`
  - Numeric ranges observed:
    - latitude: 38.50304 to 42.382633
    - longitude: 141.000635 to 144.49847
    - depth: 0.0 to 6221.0 km
    - magnitude: -0.5 to 7.7
  - Threshold counts useful for later screening:
    - M3+: 1,350
    - M4+: 266
    - M5+: 69
  - First few records follow the pattern:
    - ISO8601 time, latitude, longitude, depth_km, magnitude

Important ingestion note: this file was initially misread as having headers because the first event row becomes the header under default `read_csv`; future agents should load it with `header=None` and assign names manually.

Related catalog variant:

- `catalog/Snet_catalog_relocate_250930_260501.csv`
  - Size: ~1.30 MB
  - Rows: 22,096
  - Has explicit header: `datetime, lat, lon, dep, mag`
  - Covers a shorter time span beginning 2025-09-30.

#### Main Earthquake Reference File

- `catalog/main_earthquake.csv`
  - Size: 184 bytes
  - Shape: 3 rows × 6 columns
  - Columns:
    - `index` — event label (`M1`, `M2`, `M3`)
    - `datetime`
    - `lat`
    - `lon`
    - `dep`
    - `mag`
  - Contains the three anchor events needed to define the M1-M3 axis and the M2-related flagging region.
  - Values present:
    - `M1`: 2025-11-09 08:03:39.240, 39.402, 143.507, 15.9 km, M6.9
    - `M2`: 2025-12-08 14:15:10.180, 40.968, 142.288, 53.5 km, M7.5
    - `M3`: 2026-04-20 07:52:58.060, 39.842, 143.157, 19.4 km, M7.7

This file is the key source for reproducing axis projection, endpoint distance, phase windows, and M2-aware spatial flagging.

#### Event-Screen / Geometry Files

These files already contain derived spatial labels and summaries relevant to the requested screening task. They are useful for understanding available fields and prior workflow organization.

- `event_screen/m1_m3_event_geometry.csv`
  - Shape: 25,648 rows × 30 columns
  - Appears event-complete and aligned with the relocated catalog.
  - Columns:
    - event metadata: `time`, `latitude`, `longitude`, `depth_km`, `magnitude`, `event_id`
    - distances: `dist_m1_km`, `dist_m2_km`, `dist_m3_km`
    - local projected coordinates from M1: `x_from_m1_km`, `y_from_m1_km`
    - M1-M3 geometry metrics: `projected_km`, `perp_km`, `axis_fraction`, `between_endpoints`
    - zone flags: `local_union`, `m1_core`, `m3_core`, `m1_extended`, `m3_extended`, `m2_related`, `corridor_20`, `corridor_30`, `off_corridor_20`, `off_corridor_30`
    - time offsets: `days_since_start`, `days_since_m1`, `days_until_m3`
    - burst labels: `burst_id`, `burst_rank`
  - This is the most relevant precomputed geometry table for quickly identifying how prior agents encoded endpoint, corridor, and local-union membership.

- `event_screen/m1_m3_event_chain_table.csv`
  - Contains a richer, analysis-oriented event table with spatial classification fields.
  - Previewed columns include:
    - event metadata and distances to M1/M2/M3
    - `is_m1_to_m3`, `is_post_m3_context`
    - axis metrics: `along_m1_m3_km`, `perp_m1_m3_km`, `abs_perp_m1_m3_km`, `segment_fraction_m1_to_m3`
    - zone flags similar to the geometry table: `m1_core`, `m3_core`, `m1_extended`, `m3_extended`, `local_union`, `m2_related`, `m2_ambiguous_local`, `corridor20`, `corridor30`, `corridor30_noncore`, `off_corridor_local`
    - categorical labels: `nearest_endpoint`, `summary_category`
    - threshold flags: `mag_ge_3_0`, `mag_ge_4_0`, `mag_ge_5_0`, `mag_ge_6_0`
  - Useful if future agents want a pre-labeled event-level table with summary categories.

- `event_screen/m1_m3_burst_summary.csv`
  - Shape: 2 rows × 38 columns
  - Burst-level summary table.
  - Key columns include:
    - burst timing: `burst_id`, `start_time`, `end_time`, `peak_time`, `duration_days`
    - counts: `n_events`, `n_m3plus`, `n_m4plus`, `n_m5plus`
    - magnitude: `largest_magnitude`
    - centroid / median location: `centroid_latitude`, `centroid_longitude`, `median_latitude`, `median_longitude`
    - depth stats: `centroid_depth_km`, `median_depth_km`, `depth_min_km`, `depth_max_km`, `depth_iqr_km`
    - projection stats: `median_projected_km`, `projected_iqr_km`, `median_perp_km`, `perp_iqr_km`
    - distances to anchors: `centroid_dist_m1_km`, `centroid_dist_m3_km`, `median_dist_m1_km`, `median_dist_m3_km`
    - composition: `frac_m1_core`, `frac_m3_core`, `frac_corridor_20`, `frac_corridor_30`, `frac_off_corridor_20`, `frac_off_corridor_30`, `frac_m2_related`
    - labels: `dominant_spatial_category`, `ambiguity_flag`
    - axis context: `axis_length_km`, `median_axis_fraction`
  - This file is directly relevant to future burst-centroid screening and burst composition lookup.

- `event_screen/m1_m3_burst_table_raw.csv`
- `event_screen/m1_m3_burst_table_m2aware.csv`
  - Shape: 5 rows × 17 columns each
  - Compact burst summary tables under raw and M2-aware modes.
  - Columns:
    - `burst_id`, `mode`, `threshold`, `start_time`, `end_time`, `duration_days`
    - `event_count`, `largest_magnitude`
    - `depth_min_km`, `depth_max_km`
    - `centroid_lat`, `centroid_lon`, `centroid_along_km`
    - `dominant_summary_category`
    - `corridor30_fraction`, `off_corridor_fraction`, `m2_related_fraction`
  - These are useful for comparing raw vs M2-aware burst classifications.

- `event_screen/m1_m3_depth_domain_summary.csv`
  - Shape: 18 rows × 12 columns
  - Depth-domain summary grouped by subset and magnitude threshold.
  - Columns:
    - `subset`
    - `threshold`
    - `n`
    - `median_depth_km`, `depth_iqr_km`, `min_depth_km`, `max_depth_km`
    - `frac_0_30km`, `frac_30_60km`, `frac_gt_60km`
    - `median_projected_km`, `median_perp_km`
  - Example subset names include `M1_endpoint`; future agents can inspect all subset names after loading.

#### Source Mechanism Metadata

- `source_mechanism/Snet_mecha.csv`
  - Size: ~61.7 KB
  - Shape: 354 rows × 29 columns
  - Purpose: event-level mechanism metadata for a subset of earthquakes, useful for later mechanism comparison once catalog events are matched.
  - Columns:
    - event identity/time/location: `event_code`, `origin_time`, `lat_deg`, `lon_deg`, `depth_km`
    - magnitudes: `mag_1`, `mag_1_type`, `mag_2`, `mag_2_type`
    - region and source metadata: `region_name`, `n_hypo_stations`, `m_method`, `m_source`, `source_file`
    - principal axes: `P_axis_azimuth`, `P_axis_dip`, `T_axis_azimuth`, `T_axis_dip`, `N_axis_azimuth`, `N_axis_dip`
    - nodal planes: `strike_plane1`, `dip_plane1`, `rake_plane1`, `strike_plane2`, `dip_plane2`, `rake_plane2`
    - quality/support: `focal_mech_score`, `n_mech_stations`, `focal_mech_projection`
  - Missingness pattern:
    - Basic origin and `mag_1` fields are complete.
    - Many mechanism-specific columns have 215 missing values, indicating only a subset has full mechanism solutions.

#### Station Metadata

- `stations/station.sta`
  - Size: ~16.1 KB
  - CSV-like text file with header.
  - Header fields:
    - `station_code`, `station_number`, `latitude`, `longitude`, `elevation_m`, `matched`
  - Example records show station code plus location/elevation and a boolean `matched` flag.

- `stations/japan_stations.txt`
  - Size: ~35.7 KB
  - 1,023 records when read as single-column text using default CSV parsing.
  - Appears whitespace-delimited rather than comma-delimited.
  - Example line structure resembles:
    - network/region code, station code, latitude, longitude, elevation
  - Better parsed with whitespace splitting rather than default CSV.

These station files are useful for network-coverage context or spatial plotting, but are not required for basic catalog-only screening.

#### Other Context Files

- `active_fault/japan_active_faults.geojson`
  - Geographic context layer for mapping against known active faults.
- `DEM/output_hh.tif` and `DEM/rasters_COP30.tar.gz`
  - Terrain/topography context, secondary for this task.

#### File Naming and Organization Patterns

Common patterns in this folder:

- Catalogs use date-range names such as `Snet_catalog_relocate_<start>_<end>.csv`.
- Event-screen outputs are grouped under `event_screen/` with `m1_m3_...` prefixes indicating they are already scoped to the M1-M3 analysis workflow.
- Reference/anchor metadata are separated into small support files like `main_earthquake.csv`.
- Mechanism and station metadata are stored in dedicated subdirectories by data type.

#### Practical Loading Notes for Future Agents

- For the main relocated catalog, use explicit column names because `catalog/Snet_catalog_relocate_250601_260501.csv` has no header row.
- `main_earthquake.csv` provides the canonical M1/M2/M3 coordinates, depths, magnitudes, and times needed to reconstruct phase windows and axis geometry.
- If a future agent wants already-derived geometry labels, `event_screen/m1_m3_event_geometry.csv` is the fastest lookup table for endpoint/core/corridor flags and projected-distance fields.
- For mechanism follow-up, `source_mechanism/Snet_mecha.csv` is a partial subset and will likely require time/location matching to the relocated catalog.
- `stations/japan_stations.txt` is not standard CSV; parse as whitespace-delimited text if needed.

------------------------------

## Snet_catalog_relocate_250601_260501.csv
**Source path**: `data/Snet_catalog_relocate_250601_260501.csv`
### Summary
This relocated/filtered Aomori active-year catalog is the main event-level input for future M1-M3 spatial-depth screening. It contains 25,648 earthquake records spanning 2025-06-01 to 2026-05-01 with event time, latitude, longitude, depth, and magnitude; it should be read as a 5-column CSV without a header row.
### Detail
#### File Overview

- File: `catalog/Snet_catalog_relocate_250601_260501.csv`
- Full path: `<CASE_ROOT>/data/catalog/Snet_catalog_relocate_250601_260501.csv`
- Size: 1,506,736 bytes
- Format: plain CSV-like text
- Rows: 25,648 events
- Columns: 5

#### Important Loading Note

This file does **not** contain an explicit header row. If read with default CSV settings, the first event may be misinterpreted as the header. Future agents should load it with explicit column names such as:

- `datetime`
- `lat`
- `lon`
- `dep`
- `mag`

Recommended parsing pattern:

- `header=None`
- `names=['datetime','lat','lon','dep','mag']`

#### Column Structure

Expected event-level fields:

1. `datetime`
   - Type on read: string/object unless explicitly parsed
   - Example: `2025-06-01T00:13:38.900000Z`
   - UTC-style ISO8601 timestamp with trailing `Z`
2. `lat`
   - Type: float
   - Event latitude in degrees
3. `lon`
   - Type: float
   - Event longitude in degrees
4. `dep`
   - Type: float
   - Event depth, likely kilometers
5. `mag`
   - Type: float
   - Event magnitude

Example rows:

- `2025-06-01T00:13:38.900000Z, 39.245593, 142.382422, 29.70, 1.7`
- `2025-06-01T00:30:20.430000Z, 41.623617, 142.114681, 55.14, 1.7`
- `2025-06-01T02:20:26.570000Z, 41.533988, 143.589616, 7.08, 1.7`

#### Basic Metadata

Observed ranges from lightweight inspection:

- Time range:
  - start: `2025-06-01T00:13:38.900000Z`
  - end: `2026-05-01T14:44:22.450000Z`
- Latitude range: `38.50304` to `42.382633`
- Longitude range: `141.000635` to `144.49847`
- Depth range: `0.0` to `6221.0`
- Magnitude range: `-0.5` to `7.7`
- Missing values detected:
  - `datetime`: 0
  - `lat`: 0
  - `lon`: 0
  - `dep`: 0
  - `mag`: 0

#### Threshold Counts Relevant to Later Screening

These counts are useful for future phase/burst filtering but are only descriptive metadata here:

- `M >= 3`: 1,350 events
- `M >= 4`: 266 events
- `M >= 5`: 69 events

#### Relevance to the Requested M1-M3 Screening Workflow

This file provides the core per-event fields needed for future agents to compute:

- phase windows based on event time
- distances to M1, M2, and M3 after joining with `catalog/main_earthquake.csv`
- M1-M3 axis projections and perpendicular distances
- endpoint-core / extended-zone / corridor / off-corridor classifications
- depth-domain summaries
- burst-level centroids and time evolution
- threshold subsets such as M3+, M4+, and M5+

Because this catalog contains only basic event attributes, any M1/M2/M3-relative geometry must be derived by combining it with the anchor-event metadata in `catalog/main_earthquake.csv` or with existing precomputed geometry tables in `event_screen/`.

#### Caveats for Future Agents

- The extreme maximum depth (`6221.0`) is unusual for local earthquake work and may merit quality checking during downstream analysis.
- Magnitudes extend below zero, so thresholding should be explicit rather than assuming nonnegative values.
- Time values are strings by default and should be parsed to timezone-aware datetimes for phase-window operations.

#### Related Files to Pair With This Catalog

For future agents performing the intended M1-M3 screening, the most relevant companion files are:

- `catalog/main_earthquake.csv`
  - M1/M2/M3 anchor times, locations, depths, magnitudes
- `event_screen/m1_m3_event_geometry.csv`
  - precomputed distance/projection/zone flags for the same event set
- `event_screen/m1_m3_burst_summary.csv`
  - burst-level summary metadata
- `event_screen/m1_m3_burst_table_raw.csv`
  - compact raw burst summary table
- `event_screen/m1_m3_burst_table_m2aware.csv`
  - compact M2-aware burst summary table
- `event_screen/m1_m3_depth_domain_summary.csv`
  - precomputed subset-level depth-domain summaries
- `source_mechanism/Snet_mecha.csv`
  - focal-mechanism metadata for a subset of events
- `stations/station.sta`
  - station metadata for network/spatial context

#### File Naming Pattern

This catalog follows the naming convention:

- `Snet_catalog_relocate_<startdate>_<enddate>.csv`

where the suffix appears to encode the covered date range. This suggests other files with similar names in `catalog/` are alternative time windows or processing versions of the same relocated catalog family.

------------------------------

## main_earthquake.csv
**Source path**: `catalog/main_earthquake.csv`
### Summary
This small reference table defines the three anchor earthquakes M1, M2, and M3 used to construct all time windows and spatial relationships in the M1-M3 screening workflow. It contains 3 rows with event label, origin time, latitude, longitude, depth, and magnitude, making it the canonical source for endpoint definitions, the M1-M3 axis, and M2-related flagging.
### Detail
#### File Overview

- File: `catalog/main_earthquake.csv`
- Full path: `<CASE_ROOT>/data/catalog/main_earthquake.csv`
- Size: 184 bytes
- Format: standard CSV with header row
- Shape: 3 rows × 6 columns

#### Column Structure

Columns present:

1. `index`
   - Type: string/object
   - Event identifier label
   - Values observed: `M1`, `M2`, `M3`
2. `datetime`
   - Type on initial read: string/object
   - Origin time for each anchor event
3. `lat`
   - Type: float64
   - Latitude in degrees
4. `lon`
   - Type: float64
   - Longitude in degrees
5. `dep`
   - Type: float64
   - Depth in kilometers
6. `mag`
   - Type: float64
   - Event magnitude

No missing values were observed in any column.

#### Contents

The table contains exactly three reference events:

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

#### Relevance to Future M1-M3 Screening

This file is the key reference needed to derive the following analysis inputs from the relocated catalog:

- M1-centered and M3-centered endpoint distances
- the M1-M3 axis for projected-distance and perpendicular-distance calculations
- endpoint-core and endpoint-extended spatial zones
- M1-M3 corridor definitions after projection onto the endpoint line segment
- M2-related flagging region using distance to M2
- temporal phase boundaries keyed to M1 and M3 times, including:
  - pre-M1 baseline windows
  - M1-related dominated phase
  - middle phase
  - pre-M3 activation window
  - post-M3 context windows

Because the file stores both location and origin time for each of the three anchor events, it serves as the minimal metadata source required to reproduce all geometry and phase logic described in the task.

#### Practical Loading Notes

- Parse `datetime` to timestamp/datetime objects before using it to build relative windows such as `M1-14d`, `M1+21d`, or `M3-35d`.
- Keep the `index` field as the event key when pivoting to a dictionary or lookup table; e.g., many workflows will want to access rows by labels `M1`, `M2`, and `M3`.
- The file is small enough to load directly into memory and convert into a simple parameter structure for repeated use across scripts.

#### Suggested Access Pattern

A future agent will typically:

- read the CSV
- set `index` as the row index
- extract coordinates and times for `M1`, `M2`, and `M3`
- use those values to compute:
  - geodesic distance from each catalog event to M1/M2/M3
  - along-axis and perpendicular coordinates relative to the M1-M3 segment
  - time offsets such as `days_since_m1` and `days_until_m3`

#### Relationship to Other Files

Most relevant companion files:

- `catalog/Snet_catalog_relocate_250601_260501.csv`
  - full relocated event catalog to be joined conceptually with these anchor definitions
- `event_screen/m1_m3_event_geometry.csv`
  - precomputed event-level geometry likely derived using this anchor table
- `event_screen/m1_m3_burst_summary.csv`
  - burst centroids and distances that depend on the M1/M3 reference geometry
- `source_mechanism/Snet_mecha.csv`
  - subset mechanism metadata for later event matching and mechanism comparison

#### File Role in the Directory

Within the broader data folder, `main_earthquake.csv` functions as the canonical event-anchor metadata file rather than a general catalog. It is small, explicit, and stable, and future agents should treat it as the authoritative source for M1/M2/M3 timing and location parameters.

------------------------------

## Snet_mecha.csv
**Source path**: `source_mechanism/Snet_mecha.csv`
### Summary
This file contains focal-mechanism and source-parameter metadata for a subset of catalog events, with 354 records and 29 columns covering event identity, location, depth, magnitudes, principal axes, nodal planes, and quality/support fields. It is most relevant as a follow-up companion to the relocated catalog for later mechanism comparison of M1/M3-related or burst-associated events after matching by time and location.
### Detail
#### File Overview

- File: `source_mechanism/Snet_mecha.csv`
- Full path: `<CASE_ROOT>/data/source_mechanism/Snet_mecha.csv`
- Size: 61,681 bytes
- Format: standard CSV with header row
- Shape: 354 rows × 29 columns

#### Column Structure

Columns present in the file:

1. `event_code`
   - string/object
   - unique event identifier in source catalog format
2. `origin_time`
   - string/object
   - event origin time
3. `lat_deg`
   - float64
   - latitude in degrees
4. `lon_deg`
   - float64
   - longitude in degrees
5. `depth_km`
   - float64
   - event depth in kilometers
6. `mag_1`
   - float64
   - primary magnitude value
7. `mag_1_type`
   - string/object
   - magnitude type code for `mag_1`
8. `mag_2`
   - float64
   - secondary magnitude value when available
9. `mag_2_type`
   - string/object
   - magnitude type code for `mag_2`
10. `region_name`
    - string/object
    - region descriptor
11. `n_hypo_stations`
    - int64
    - number of stations used for hypocenter solution
12. `m_method`
    - string/object
    - mechanism/magnitude method metadata
13. `m_source`
    - string/object
    - source metadata code
14. `P_axis_azimuth`
    - float64
15. `P_axis_dip`
    - float64
16. `T_axis_azimuth`
    - float64
17. `T_axis_dip`
    - float64
18. `N_axis_azimuth`
    - float64
19. `N_axis_dip`
    - float64
20. `strike_plane1`
    - float64
21. `dip_plane1`
    - float64
22. `rake_plane1`
    - float64
23. `strike_plane2`
    - float64
24. `dip_plane2`
    - float64
25. `rake_plane2`
    - float64
26. `focal_mech_score`
    - float64
    - quality/confidence-style score
27. `n_mech_stations`
    - float64
    - number of stations supporting the mechanism solution
28. `focal_mech_projection`
    - string/object
    - mechanism quality/projection descriptor
29. `source_file`
    - string/object
    - originating source text file name

#### Missing-Value Pattern

Complete fields:

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

Partially populated fields with 215 missing values each:

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

This indicates that only a subset of the 354 events has a full focal-mechanism solution and associated axis/plane metadata.

#### Example Record Structure

Example values observed:

- `event_code`: `J2025100111563882`
- `origin_time`: `2025-10-01 02:56:38.820`
- `lat_deg`: `41.813333`
- `lon_deg`: `142.668167`
- `depth_km`: `56.44`
- `mag_1`: `3.5`
- `mag_1_type`: `V`
- `region_name`: `S OFF URAKAWA`
- `n_hypo_stations`: `40`
- axis fields and nodal planes populated for events with mechanism solutions
- `focal_mech_projection`: example value `LOW`
- `source_file`: example value `mecha_20251001_7.txt`

Other example regions include `KINKAZAN REGION`.

#### Relevance to Future M1-M3 Workflow

This file is not the main event catalog; instead, it is a companion metadata table for later follow-up after catalog-level spatial-depth screening. It is most useful for future agents that want to:

- compare focal mechanisms among M1-endpoint, M3-endpoint, corridor, or off-corridor subsets
- test whether major bursts share similar or contrasting nodal-plane geometry
- inspect whether larger events in the M1-M3 system have mechanism solutions
- support follow-up mechanism-evidence analysis after events are selected from the relocated catalog

For the requested workflow, the most relevant fields are:

- temporal/location matching fields:
  - `event_code`
  - `origin_time`
  - `lat_deg`
  - `lon_deg`
  - `depth_km`
- magnitude fields:
  - `mag_1`, `mag_1_type`, `mag_2`, `mag_2_type`
- mechanism description fields:
  - `P_axis_azimuth`, `P_axis_dip`
  - `T_axis_azimuth`, `T_axis_dip`
  - `N_axis_azimuth`, `N_axis_dip`
  - `strike_plane1`, `dip_plane1`, `rake_plane1`
  - `strike_plane2`, `dip_plane2`, `rake_plane2`
- quality/support fields:
  - `focal_mech_score`
  - `n_mech_stations`
  - `focal_mech_projection`

#### Relationship to the Main Catalog

Future agents will likely need to match this table to the relocated catalog in `catalog/Snet_catalog_relocate_250601_260501.csv` using time and location, because:

- this mechanism file uses different field names than the relocated catalog
- no direct relocated-catalog event ID was observed in the main catalog preview
- only a subset of events has mechanism information

A practical crosswalk would likely use:

- `origin_time` vs catalog `datetime`
- `lat_deg`, `lon_deg`, `depth_km`
- optionally magnitude consistency via `mag_1`

#### Practical Loading Notes

- Parse `origin_time` as datetime before matching to catalog events or phase windows.
- Treat missing mechanism fields as expected, not as file corruption.
- `n_mech_stations` is stored as float because of missing values; convert carefully if integer semantics are needed after filtering non-null rows.
- `mag_1` appears to be the more complete magnitude field; `mag_2` is optional.

#### File Naming and Provenance Hints

- The `source_file` column suggests this CSV aggregates mechanism solutions from source text files such as `mecha_20251001_7.txt`.
- This supports the interpretation that `Snet_mecha.csv` is a compiled mechanism table rather than a direct export of the relocated event catalog.

#### Best Use by Future Agents

Use this file after the main catalog and M1/M2/M3 geometry have already been established. It is best suited for targeted follow-up on selected bursts, large events, or endpoint/corridor subsets, rather than as the primary source for event counts, phase timing, or migration diagnostics.

------------------------------

## station.sta
**Source path**: `stations/station.sta`
### Summary
This station metadata file is a small CSV-like table listing matched seismic stations with station code, numeric identifier, latitude, longitude, elevation, and a boolean match flag. It is not the main earthquake catalog, but it provides useful network and map-context metadata for future agents preparing spatial plots or checking station coverage around the M1-M3 system.
### Detail
#### File Overview

- File: `stations/station.sta`
- Full path: `<CASE_ROOT>/data/stations/station.sta`
- Size: 16,102 bytes
- Format: comma-separated text with header row
- Purpose: station metadata / station list

#### Column Structure

Header fields observed:

1. `station_code`
   - string/object
   - station identifier, often including a network-like prefix and station name
   - examples: `A.ASMS`, `A.CHOG`, `A.HGTZ`, `A.HRDA`
2. `station_number`
   - numeric/integer-like identifier
   - examples: `5572`, `5550`, `5571`, `5549`
3. `latitude`
   - float
   - station latitude in degrees
4. `longitude`
   - float
   - station longitude in degrees
5. `elevation_m`
   - numeric elevation in meters
   - can be negative for below-sea-level or reference-elevation cases
   - examples: `-3`, `0`, `-11`, `2`
6. `matched`
   - boolean-like field
   - previewed values are `True`

#### Example Records

First few rows show the file structure clearly:

- `A.ASMS,5572,40.885667,140.874000,-3,True`
- `A.CHOG,5550,41.327167,140.815333,0,True`
- `A.HGTZ,5571,40.982833,140.904000,-11,True`
- `A.HRDA,5549,41.448833,140.881000,2,True`

#### Relevance to Future Agents

For the requested M1-M3 catalog-screening workflow, this file is secondary rather than primary. It may still be useful for:

- adding station locations to regional or local maps
- checking observational/network context around the M1-M3 activity area
- supporting later follow-up on catalog quality, relocation context, or station proximity
- labeling or filtering to a matched subset of stations if the `matched` field is used consistently

It is **not** the source for earthquake times, locations, magnitudes, bursts, or M1-M3 geometry. Those should come from the relocated catalog and anchor-event files.

#### Likely Field Uses in Downstream Work

Most useful columns for future plotting or QC:

- `station_code`
  - for labeling or joining to other station metadata
- `latitude`, `longitude`
  - for station maps relative to event clusters, M1, M2, and M3
- `elevation_m`
  - optional topographic/site-context display
- `matched`
  - likely indicates whether the station belongs to a selected or successfully mapped station subset

#### Parsing Notes

- The file can be read directly with standard CSV readers.
- The `matched` field appears text/boolean-like and may be parsed as string or boolean depending on reader settings.
- `station_number` is numeric but should generally be treated as an identifier rather than a quantitative variable.

#### Relationship to Other Files

This station table complements, but does not replace, the main analysis files:

- `catalog/Snet_catalog_relocate_250601_260501.csv`
  - primary earthquake event catalog
- `catalog/main_earthquake.csv`
  - M1/M2/M3 anchor events
- `event_screen/m1_m3_event_geometry.csv`
  - precomputed event-geometry table
- `source_mechanism/Snet_mecha.csv`
  - focal-mechanism metadata for a subset of events

If future agents need broader station context, there is also a separate file in the same folder:

- `stations/japan_stations.txt`

#### Directory Role

Within `data/stations/`, `station.sta` appears to be the compact, clean, analysis-ready station list, whereas `japan_stations.txt` is a larger station inventory in a different text format. For most local mapping and quick metadata lookup, `station.sta` is the easier station file to use.

------------------------------

