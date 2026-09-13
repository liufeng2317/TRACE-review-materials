# Data Descriptions
## data
**Source path**: `<CASE_ROOT>/data`
### Summary
This data folder is organized around a relocated earthquake catalog, a small mainshock index for the three target events (M1, M2, M3), contextual focal-mechanism metadata, and station metadata. The most relevant analysis inputs are lightweight tabular files: a 22,096-event relocated CSV catalog spanning 2025-09-30 to 2026-05-01, a 3-row mainshock table, a 354-row focal-mechanism table, and a 371-station table.
### Detail
#### Folder Structure
The data directory contains several subfolders, with the most relevant ones for future catalog-level relationship analysis listed below:

- `catalog/`
  - `Snet_catalog_relocate_250930_260501.csv` — primary relocated event catalog used for event-level time/space analyses.
  - `main_earthquake.csv` — 3-event table defining the target mainshocks/clusters `M1`, `M2`, `M3`.
  - Additional catalog versions and notebooks are present, including:
    - `Snet_catalog_full_250930_260501.csv`
    - `Snet_catalog_full_251101_260420.csv`
    - `Snet_catalog_relocate_250930_26_0501.csv`
    - `Snet_catalog-v1.csv`, `Snet_catalog-v2.csv`
    - `catalog.ipynb`, `swarm_like.ipynb`
    - `catalog_compare_check.png`
- `source_mechanism/`
  - `Snet_mecha.csv` — focal-mechanism/context table for a subset of events.
- `stations/`
  - `station.sta` — station metadata table.
  - `japan_stations.txt` — additional station listing.
- `active_fault/`
  - `japan_active_faults.geojson` — contextual fault geometry file.
- `DEM/`
  - raster products (`output_hh.tif`, `rasters_COP30.tar.gz`) for geographic context.
- Root-level notebook:
  - `visualize.ipynb`

The directory is therefore a mixed analysis workspace, but the main machine-readable inputs for future agents are the CSV/STA tables under `catalog/`, `source_mechanism/`, and `stations/`.

#### Primary Catalog Files
**1) `catalog/Snet_catalog_relocate_250930_260501.csv`**
- Format: CSV
- Size: ~1.30 MB
- Shape: `22096 x 5`
- Columns:
  - `datetime` — event origin time in ISO-like UTC string format, e.g. `2025-09-30T16:09:25.360000Z`
  - `lat` — latitude (float)
  - `lon` — longitude (float)
  - `dep` — depth in km (float)
  - `mag` — magnitude (float)
- Time span:
  - min: `2025-09-30 16:09:25.360000+00:00`
  - max: `2026-05-01 14:44:22.450000+00:00`
- Value ranges:
  - `lat`: `38.503003` to `42.382633`
  - `lon`: `141.001921` to `144.49847`
  - `dep`: `0.05` to `121.14` km
  - `mag`: `-0.5` to `7.7`
- Missing values: none detected in the five columns.

This is the core event catalog for pairwise cluster-relationship work because it contains the essential event-level fields required for time separation, epicentral distance, depth difference, magnitude thresholding, corridor tests, and nearest-mainshock assignment.

**2) `catalog/main_earthquake.csv`**
- Format: CSV
- Size: 184 bytes
- Shape: `3 x 6`
- Columns:
  - `index` — cluster/mainshock label
  - `datetime`
  - `lat`
  - `lon`
  - `dep`
  - `mag`
- Rows define the three target mainshocks:
  - `M1` — `2025-11-09 08:03:39.240`, `(39.402, 143.507)`, depth `15.9`, magnitude `6.9`
  - `M2` — `2025-12-08 14:15:10.180`, `(40.968, 142.288)`, depth `53.5`, magnitude `7.5`
  - `M3` — `2026-04-20 07:52:58.060`, `(39.842, 143.157)`, depth `19.4`, magnitude `7.7`
- Missing values: none detected.

This file is the lookup table for the main cluster anchors. Future agents can join or compare all catalog events against these three rows to compute relative time, nearest-mainshock geometry, and pairwise projections.

#### Context Files Relevant to Relationship Interpretation
**3) `source_mechanism/Snet_mecha.csv`**
- Format: CSV
- Size: ~61.7 KB
- Shape: `354 x 29`
- Key columns:
  - Event identity and origin:
    - `event_code`, `origin_time`, `lat_deg`, `lon_deg`, `depth_km`
  - Magnitudes:
    - `mag_1`, `mag_1_type`, `mag_2`, `mag_2_type`
  - Region/context:
    - `region_name`, `n_hypo_stations`, `m_method`, `m_source`
  - Principal axes:
    - `P_axis_azimuth`, `P_axis_dip`, `T_axis_azimuth`, `T_axis_dip`, `N_axis_azimuth`, `N_axis_dip`
  - Nodal planes:
    - `strike_plane1`, `dip_plane1`, `rake_plane1`, `strike_plane2`, `dip_plane2`, `rake_plane2`
  - Quality/provenance:
    - `focal_mech_score`, `n_mech_stations`, `focal_mech_projection`, `source_file`
- Time span:
  - min: `2025-10-01 02:56:38.820000`
  - max: `2026-05-19 10:23:35.210000`
- Region distribution (top values):
  - `E OFF AOMORI PREF`: 195
  - `E OFF IWATE PREF`: 34
  - `E OFF MIYAGI PREF`: 22
  - `KINKAZAN REGION`: 22
  - `NE OFF IWATE PREF`: 14
- Focal mechanism projection values:
  - `LOW`: 139
  - missing: 215
- Major missingness pattern:
  - many mechanism-geometry columns are missing for 215 rows, including `mag_2`, principal-axis values, nodal planes, `focal_mech_score`, and `n_mech_stations`.

This table is useful as contextual support for follow-up work on whether event subsets share similar mechanism styles, but it is not a complete mechanism inventory. Future agents should expect partial coverage only.

**4) `stations/station.sta`**
- Format: comma-delimited text table (readable as CSV)
- Size: ~16.1 KB
- Shape: `371 x 6`
- Columns:
  - `station_code`
  - `station_number`
  - `latitude`
  - `longitude`
  - `elevation_m`
  - `matched`
- Spatial extent:
  - latitude: `36.880833` to `44.118833`
  - longitude: `139.245333` to `145.738833`
- Missing values: none detected.
- Example station fields indicate a mix of onshore/offshore or near-coastal stations, with elevations including negative values.

This file is a station metadata reference for later checks on network geometry or catalog support, not a direct event-analysis table.

#### File Naming and Organization Patterns
- Catalog files use descriptive names with versioning/date-window suffixes, e.g.:
  - `Snet_catalog_relocate_250930_260501.csv`
  - `Snet_catalog_relocate_250930_26_0501.csv`
  - `Snet_catalog_full_250930_260501.csv`
- The target mainshock file is a compact manually curated summary table: `main_earthquake.csv`.
- Context metadata are separated by theme:
  - mechanisms under `source_mechanism/`
  - station metadata under `stations/`
  - faults under `active_fault/`
  - topography under `DEM/`

This layout suggests a workflow in which the relocated catalog is primary, while mechanisms, stations, and faults provide secondary interpretation layers.

#### Fields Most Relevant for Future Agents
For the user’s requested cluster-relationship investigation, the highest-priority fields to load first are:

- From `catalog/Snet_catalog_relocate_250930_260501.csv`:
  - `datetime`, `lat`, `lon`, `dep`, `mag`
- From `catalog/main_earthquake.csv`:
  - `index`, `datetime`, `lat`, `lon`, `dep`, `mag`
- From `source_mechanism/Snet_mecha.csv` (contextual only):
  - `event_code`, `origin_time`, `lat_deg`, `lon_deg`, `depth_km`, `mag_1`, `region_name`,
    `strike_plane1`, `dip_plane1`, `rake_plane1`, `strike_plane2`, `dip_plane2`, `rake_plane2`,
    `focal_mech_score`, `n_mech_stations`, `focal_mech_projection`
- From `stations/station.sta`:
  - `station_code`, `latitude`, `longitude`, `elevation_m`, `matched`

These fields are sufficient to support later event filtering by magnitude thresholds (e.g. M3+/M4+/M5+/M6+), time-distance calculations, corridor/projection logic, nearest-mainshock comparisons, and optional mechanism/station context checks.

#### Example Access Paths
- Primary relocated catalog:
  - `<CASE_ROOT>/data/catalog/Snet_catalog_relocate_250930_260501.csv`
- Mainshock definitions:
  - `<CASE_ROOT>/data/catalog/main_earthquake.csv`
- Mechanism context:
  - `<CASE_ROOT>/data/source_mechanism/Snet_mecha.csv`
- Station metadata:
  - `<CASE_ROOT>/data/stations/station.sta`

#### Practical Loading Notes
- The catalog and mainshock files use straightforward CSV structure and can be loaded directly with `pandas.read_csv(...)`.
- Time fields should be parsed explicitly (`datetime`, `origin_time`) because formats differ slightly between files:
  - catalog uses UTC `Z` suffix ISO strings,
  - mainshock/mechanism files use space-separated timestamps.
- Mechanism coverage is incomplete, so downstream code should not assume every event has nodal-plane or axis metadata.
- The `station.sta` file is already comma-delimited and does not require special fixed-width parsing.

------------------------------

## Snet_catalog_relocate_250930_260501.csv
**Source path**: `catalog/Snet_catalog_relocate_250930_260501.csv`
### Summary
This file is the primary relocated earthquake catalog for the Aomori study area and contains 22,096 events with only five core fields: origin time, latitude, longitude, depth, and magnitude. It spans late 2025 to early 2026 and is well suited for future agents to compute time-distance relationships, magnitude-threshold subsets, nearest-mainshock associations, and corridor-style spatial diagnostics.
### Detail
#### File Overview
- **Path:** `catalog/Snet_catalog_relocate_250930_260501.csv`
- **Format:** CSV
- **Size:** ~1.30 MB
- **Shape:** `22096 x 5`
- **Role in workflow:** primary event catalog for catalog-level relationship analysis among the `M1`, `M2`, and `M3` clusters.

This is a compact relocated catalog with one row per event and no auxiliary columns beyond the core hypocentral/magnitude fields.

#### Column Structure
The file has the following columns:

1. `datetime`
   - Type: string when read raw; parseable as UTC datetime
   - Example: `2025-09-30T16:09:25.360000Z`
   - Use: event ordering, pre/post windowing, inter-event timing, mainshock-relative timing, event-chain construction

2. `lat`
   - Type: `float64`
   - Use: latitude for epicentral distance, map view, corridor/projection calculations

3. `lon`
   - Type: `float64`
   - Use: longitude for epicentral distance, map view, corridor/projection calculations

4. `dep`
   - Type: `float64`
   - Interpretable as depth in km
   - Use: vertical separation, depth-band comparison, nearest-mainshock 3D context

5. `mag`
   - Type: `float64`
   - Use: threshold subsets such as M3+, M4+, M5+, M6+, and sequence prominence screening

#### Basic Metadata
- **Time coverage:**
  - Start: `2025-09-30 16:09:25.360000+00:00`
  - End: `2026-05-01 14:44:22.450000+00:00`
- **Spatial coverage:**
  - Latitude: `38.503003` to `42.382633`
  - Longitude: `141.001921` to `144.49847`
- **Depth range:** `0.05` to `121.14` km
- **Magnitude range:** `-0.5` to `7.7`
- **Missing values:** none detected in any of the five columns

#### Example Rows
A few example records illustrate the structure:
- `2025-09-30T16:09:25.360000Z, 38.703422, 142.256738, 41.35, 2.8`
- `2025-09-30T16:55:18.670000Z, 38.959892, 142.594434, 27.66, 1.2`
- `2025-09-30T18:47:05.380000Z, 39.934501, 142.485905, 34.75, 1.6`

#### Organization and Access Pattern
- The file is a **flat event table** with one event per row.
- There is **no explicit event ID** column.
- There are **no built-in cluster labels**, region names, station counts, or mechanism fields in this file.
- Future agents will need to derive relationships by comparing these event rows to the target mainshock definitions stored separately in `catalog/main_earthquake.csv`.

A typical loading pattern would be:
- parse `datetime` as timezone-aware timestamp,
- sort by time if needed,
- filter by `mag` threshold,
- compute event-to-mainshock time offsets and distances using `lat`, `lon`, and optionally `dep`.

#### Relevance to the Requested Investigation
For future agents investigating whether `M1`, `M2`, and `M3` are independent, overlapping, corridor-linked, delayed, or regionally related, this catalog provides the essential raw fields needed for:

- pairwise event timing relative to each mainshock,
- epicentral and depth separation analyses,
- magnitude-threshold subsets (`M3+`, `M4+`, `M5+`, `M6+`),
- nearest-mainshock assignment,
- endpoint-vs-corridor spatial classification,
- time-distance and projection diagnostics,
- intervening-event counts and event-chain summaries.

Because the catalog lacks event classification columns, all sequence or pairwise relationship interpretations must be built from these geometric and temporal primitives rather than read directly from metadata.

#### Limitations Visible from Metadata Alone
- No event identifier column for direct joins unless agents construct one from row index and timestamp.
- No uncertainty fields (e.g., location uncertainty, depth uncertainty, origin-time uncertainty).
- No phase counts, station counts, quality flags, or relocation diagnostics.
- No focal mechanism or region descriptors in this file.
- No explicit marker for the three target clusters; those anchors must be supplied externally from `main_earthquake.csv`.

#### Recommended Parsing Notes
- Parse `datetime` explicitly as datetime with UTC handling because values include a trailing `Z`.
- Treat `dep` and `mag` as numeric floats.
- Since there are only five columns and no missing values, this file is straightforward to load with `pandas.read_csv(..., parse_dates=['datetime'])`.

#### Example Path
- Absolute path: `<CASE_ROOT>/data/catalog/Snet_catalog_relocate_250930_260501.csv`

------------------------------

## main_earthquake.csv
**Source path**: `catalog/main_earthquake.csv`
### Summary
This file is a compact 3-row mainshock reference table that defines the anchor events for the target Aomori clusters M1, M2, and M3. It provides the cluster labels, origin times, hypocenters, and magnitudes needed by future agents to compute event-relative timing, pairwise mainshock geometry, nearest-mainshock assignments, and corridor projections against the larger relocated catalog.
### Detail
#### File Overview
- **Path:** `catalog/main_earthquake.csv`
- **Format:** CSV
- **Size:** 184 bytes
- **Shape:** `3 x 6`
- **Role in workflow:** reference table for the three target mainshocks/clusters used to anchor all later relationship analyses.

This is a very small lookup table rather than a full event catalog. Each row corresponds to one named mainshock cluster endpoint.

#### Column Structure
The file contains the following columns:

1. `index`
   - Type: `object` / string
   - Values observed: `M1`, `M2`, `M3`
   - Use: cluster label or sequence anchor identifier

2. `datetime`
   - Type: string when read raw; parseable as datetime
   - Example format: `2025-11-09 08:03:39.240`
   - Use: mainshock-relative time offsets, pairwise mainshock time separation, pre/post window definitions

3. `lat`
   - Type: `float64`
   - Use: epicentral location of each mainshock anchor

4. `lon`
   - Type: `float64`
   - Use: epicentral location of each mainshock anchor

5. `dep`
   - Type: `float64`
   - Interpretable as depth in km
   - Use: depth separation between target mainshocks and comparison to nearby catalog events

6. `mag`
   - Type: `float64`
   - Use: magnitude ranking and contextual comparison among the three target events

#### Row Contents
The three rows define the target cluster anchors:

- **M1**
  - `datetime`: `2025-11-09 08:03:39.240`
  - `lat`: `39.402`
  - `lon`: `143.507`
  - `dep`: `15.9`
  - `mag`: `6.9`

- **M2**
  - `datetime`: `2025-12-08 14:15:10.180`
  - `lat`: `40.968`
  - `lon`: `142.288`
  - `dep`: `53.5`
  - `mag`: `7.5`

- **M3**
  - `datetime`: `2026-04-20 07:52:58.060`
  - `lat`: `39.842`
  - `lon`: `143.157`
  - `dep`: `19.4`
  - `mag`: `7.7`

#### Data Quality / Completeness
- Missing values: none detected.
- All fields are populated for all three rows.
- The file is internally consistent and immediately usable as a mainshock metadata table.

#### Relevance to the Requested Investigation
For future catalog-level relationship analysis, this file is the key source of the three mainshock anchors needed to evaluate:

- pairwise mainshock time separation (`M1-M2`, `M1-M3`, `M2-M3`),
- pairwise epicentral geometry,
- pairwise depth differences,
- distance-aware plausibility of linkage,
- nearest-mainshock assignment of catalog events,
- endpoint-centered versus corridor-like spatial organization,
- event projections onto pairwise mainshock axes.

Because the larger relocated catalog has no built-in cluster label column, future agents will need this file to define the reference points for all sequence-relative calculations.

#### How It Connects to Other Files
This file is intended to be used together with:

- `catalog/Snet_catalog_relocate_250930_260501.csv`
  - for mapping all events into time/distance coordinates relative to `M1`, `M2`, and `M3`
- `source_mechanism/Snet_mecha.csv`
  - for optional mechanism context around the three anchor areas
- `stations/station.sta`
  - for optional network/support context

A typical future workflow would:
1. load this table,
2. load the relocated catalog,
3. compute event-to-mainshock time offsets and distances for each of `M1`, `M2`, and `M3`,
4. compare pairwise cluster geometry and event distributions.

#### Practical Parsing Notes
- Parse `datetime` explicitly with `pandas.to_datetime` or `read_csv(..., parse_dates=['datetime'])`.
- The timestamp format differs slightly from the relocated catalog, which uses ISO strings with trailing `Z`; future agents should not assume identical datetime formatting across files.
- Since the table has only three rows, it can be safely inspected manually or loaded into a small dictionary keyed by `index`.

#### Example Access Path
- Absolute path: `<CASE_ROOT>/data/catalog/main_earthquake.csv`

#### Suggested In-Memory Representation for Future Agents
Useful forms after loading include:
- a dataframe indexed by `index` (`M1`, `M2`, `M3`), or
- a dictionary of anchor metadata per mainshock.

This makes it easy to retrieve each mainshock’s `datetime`, `lat`, `lon`, `dep`, and `mag` when computing event-level relationship features from the larger catalog.

------------------------------

## Snet_mecha.csv
**Source path**: `source_mechanism/Snet_mecha.csv`
### Summary
This file is a contextual focal-mechanism table with 354 rows and 29 columns, providing event time, location, magnitude, region labels, principal-axis parameters, nodal planes, and mechanism quality/provenance fields. It is useful for follow-up comparison of source-style consistency across events near M1, M2, and M3, but coverage is partial: many mechanism-geometry columns are missing for 215 rows.
### Detail
#### File Overview
- **Path:** `source_mechanism/Snet_mecha.csv`
- **Format:** CSV
- **Size:** ~61.7 KB
- **Shape:** `354 x 29`
- **Role in workflow:** contextual source-mechanism metadata for a subset of earthquakes, suitable for later cross-checking whether selected events near the target clusters share similar mechanism styles or tectonic context.

This is not the primary catalog. It is a supplementary event table that includes focal-mechanism parameters and event-region descriptors for only part of the broader sequence.

#### Column Structure
The file contains the following columns:

**Event identity and origin**
1. `event_code` — event identifier string
2. `origin_time` — event origin time
3. `lat_deg` — latitude in degrees
4. `lon_deg` — longitude in degrees
5. `depth_km` — depth in km

**Magnitude information**
6. `mag_1` — primary magnitude value
7. `mag_1_type` — primary magnitude type
8. `mag_2` — secondary magnitude value (often missing)
9. `mag_2_type` — secondary magnitude type

**Regional and catalog context**
10. `region_name` — text region label
11. `n_hypo_stations` — number of hypocenter stations
12. `m_method` — mechanism/magnitude method code
13. `m_source` — source code

**Principal axes**
14. `P_axis_azimuth`
15. `P_axis_dip`
16. `T_axis_azimuth`
17. `T_axis_dip`
18. `N_axis_azimuth`
19. `N_axis_dip`

**Nodal plane solutions**
20. `strike_plane1`
21. `dip_plane1`
22. `rake_plane1`
23. `strike_plane2`
24. `dip_plane2`
25. `rake_plane2`

**Mechanism quality / provenance**
26. `focal_mech_score`
27. `n_mech_stations`
28. `focal_mech_projection`
29. `source_file`

#### Basic Metadata
- **Time coverage:**
  - Start: `2025-10-01 02:56:38.820000`
  - End: `2026-05-19 10:23:35.210000`
- **Observed dtypes:**
  - string/object fields: `event_code`, `origin_time`, `mag_1_type`, `mag_2_type`, `region_name`, `m_method`, `m_source`, `focal_mech_projection`, `source_file`
  - numeric fields: event coordinates, depth, magnitudes, station counts, principal axes, nodal plane parameters, scores

#### Example Content Pattern
Example rows show event-level mechanism records such as:
- event code and origin time,
- offshore northeastern Japan regional labels,
- one or two magnitude values,
- P/T/N axis azimuths and dips,
- two nodal plane solutions,
- a quality/projection label such as `LOW`,
- provenance source text file such as `mecha_20251001_7.txt`.

#### Coverage and Missingness
This file has important partial-coverage behavior that future agents should account for.

- Total rows: `354`
- Rows with many mechanism-geometry fields missing: `215`
- Common columns with `215` missing values include:
  - `mag_2`
  - `P_axis_azimuth`, `P_axis_dip`
  - `T_axis_azimuth`, `T_axis_dip`
  - `N_axis_azimuth`, `N_axis_dip`
  - `strike_plane1`, `dip_plane1`, `rake_plane1`
  - `strike_plane2`, `dip_plane2`, `rake_plane2`
  - `focal_mech_score`
  - `n_mech_stations`
- `focal_mech_projection` counts:
  - missing: `215`
  - `LOW`: `139`

Implication for future agents: do not assume complete focal-mechanism availability for all events in this table, and do not assume this table covers all events in the relocated catalog.

#### Region Labels and Distribution
The `region_name` field provides useful coarse geographic grouping. The most frequent observed labels are:
- `E OFF AOMORI PREF`: `195`
- `E OFF IWATE PREF`: `34`
- `E OFF MIYAGI PREF`: `22`
- `KINKAZAN REGION`: `22`
- `NE OFF IWATE PREF`: `14`
- `OFF NEMURO PENINSULA`: `10`
- `S OFF URAKAWA`: `10`
- `NORTHERN IWATE PREF`: `10`

This indicates the mechanism table is centered strongly on the offshore Aomori region but also includes events from a broader northeastern Japan context.

#### Relevance to the Requested Investigation
For future agents studying possible relationships among the `M1`, `M2`, and `M3` clusters, this file is most relevant as **contextual support**, not as the main analysis base. It can help with later tasks such as:

- checking whether large or strategically located events have available focal mechanisms,
- comparing source-style similarity for events assigned to different cluster neighborhoods,
- examining whether corridor or overlapping-zone events differ from endpoint-centered events,
- identifying whether selected events share region labels or mechanism quality information.

However, the file is not sufficient by itself for the cluster-relationship analysis because:
- it does not include all catalog events,
- many rows lack full nodal-plane data,
- it is not explicitly keyed to `M1`, `M2`, or `M3` labels.

#### Most Relevant Fields for Future Agents
If using this file to enrich a relationship study, the highest-priority fields are:
- event matching and timing:
  - `event_code`, `origin_time`, `lat_deg`, `lon_deg`, `depth_km`
- magnitude/context:
  - `mag_1`, `mag_1_type`, `region_name`, `n_hypo_stations`
- mechanism geometry:
  - `strike_plane1`, `dip_plane1`, `rake_plane1`
  - `strike_plane2`, `dip_plane2`, `rake_plane2`
  - `P_axis_azimuth`, `P_axis_dip`, `T_axis_azimuth`, `T_axis_dip`
- quality/provenance:
  - `focal_mech_score`, `n_mech_stations`, `focal_mech_projection`, `source_file`

#### Practical Loading Notes
- Load with `pandas.read_csv(...)` and parse `origin_time` explicitly as datetime.
- Expect partial nulls in the mechanism-related numeric columns.
- Because the primary relocated catalog uses different column names (`datetime`, `lat`, `lon`, `dep`, `mag`), future agents will likely need a custom spatial-temporal matching step rather than a trivial direct merge unless a shared event identifier is available elsewhere.

#### Example Access Path
- Absolute path: `<CASE_ROOT>/data/source_mechanism/Snet_mecha.csv`

#### Interpretation Boundary
This file supports metadata inspection and later mechanism-aware filtering, but metadata alone do not establish physical linkage among clusters. Its main value is to help future agents identify which events have mechanism information available for follow-up comparison after catalog-based relationship candidates have been identified.

------------------------------

## station.sta
**Source path**: `stations/station.sta`
### Summary
This file is a station metadata table with 371 rows and 6 columns, listing station codes, numeric identifiers, coordinates, elevation, and a boolean match flag. It is a contextual support dataset for future agents that may want to assess network geometry or station coverage around the M1, M2, and M3 cluster areas, but it is not itself an earthquake-event catalog.
### Detail
#### File Overview
- **Path:** `stations/station.sta`
- **Format:** comma-delimited text table (readable directly as CSV)
- **Size:** ~16.1 KB
- **Shape:** `371 x 6`
- **Role in workflow:** station metadata reference for network context, station distribution checks, and potential later interpretation of catalog support.

This file contains one row per station and does not contain earthquake events, arrival picks, or waveform references.

#### Column Structure
The file has the following columns:

1. `station_code`
   - Type: `object` / string
   - Example: `A.ASMS`, `A.CHOG`, `A.HGTZ`
   - Use: station identifier for mapping or cross-reference

2. `station_number`
   - Type: `int64`
   - Use: numeric station ID

3. `latitude`
   - Type: `float64`
   - Use: station map position

4. `longitude`
   - Type: `float64`
   - Use: station map position

5. `elevation_m`
   - Type: `int64`
   - Units: meters
   - Example values include zero and negative elevations
   - Use: basic station site context

6. `matched`
   - Type: `bool`
   - Use: indicates whether the station is marked as matched in the current workflow

#### Basic Metadata
- **Latitude range:** `36.880833` to `44.118833`
- **Longitude range:** `139.245333` to `145.738833`
- **Missing values:** none detected in any column
- **Coordinate span:** broad northeastern Japan coverage, extending beyond the immediate Aomori cluster area

#### Example Rows
Representative rows include:
- `A.ASMS, 5572, 40.885667, 140.874000, -3, True`
- `A.CHOG, 5550, 41.327167, 140.815333, 0, True`
- `A.HGTZ, 5571, 40.982833, 140.904000, -11, True`

These examples indicate a conventional station inventory table with geographic coordinates and simple per-station attributes.

#### Relevance to the Requested Investigation
For future agents studying catalog-level relationships among `M1`, `M2`, and `M3`, this file is **contextual rather than primary**. It may be useful for:

- plotting station distribution relative to cluster areas,
- checking whether the event region is broadly covered by stations,
- supporting later interpretation of possible spatial variation in detectability or location support,
- identifying whether offshore/near-coastal geometry might matter for subsequent waveform or relocation follow-up.

However, this file does **not** directly provide:
- event times,
- hypocenters,
- magnitudes,
- picks,
- waveform file paths,
- detection thresholds,
- station-event associations.

So it should not be treated as a direct input for the pairwise cluster relationship calculations themselves.

#### Most Relevant Fields for Future Agents
If this file is used in a later workflow, the most relevant fields are:
- `station_code`
- `latitude`
- `longitude`
- `elevation_m`
- `matched`

These are sufficient for quick station map overlays and coarse network-context checks.

#### Practical Loading Notes
- Despite the `.sta` extension, the file is already comma-delimited and can be loaded with standard CSV readers such as `pandas.read_csv(...)`.
- No special fixed-width parsing was needed during inspection.
- Because there are no missing values and only six columns, this is a straightforward metadata table to load.

#### Relationship to Other Inputs
This station table complements but does not replace the main analysis files:
- `catalog/Snet_catalog_relocate_250930_260501.csv` — primary event catalog
- `catalog/main_earthquake.csv` — mainshock anchor definitions
- `source_mechanism/Snet_mecha.csv` — contextual source-mechanism subset

A likely future use is to overlay these station coordinates on maps of the relocated catalog and mainshock locations to provide geographic context for later physical follow-up studies.

#### Example Access Path
- Absolute path: `<CASE_ROOT>/data/stations/station.sta`

#### Interpretation Boundary
This file supports metadata and network-context description only. It cannot by itself establish or refute relationships among the earthquake clusters; it is mainly useful for future agents who need station geometry context when designing relocation, waveform, or detectability follow-up analyses.

------------------------------

