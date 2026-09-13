# Data Descriptions
## data
**Source path**: `<CASE_ROOT>/data`
### Summary
This data tree is centered on a relocated local earthquake catalog and a small mainshock reference table, with optional supporting focal-mechanism and station metadata relevant to the 2025-11-09 JMA M6.9 Sanriku-Oki sequence. The key analysis-ready input is `catalog/Snet_catalog_relocate_250601_260501.csv`, a 25,646-event CSV spanning 2025-06-01 to 2026-05-01 with origin time, latitude, longitude, depth, and magnitude fields and no missing values in those core columns.
### Detail
#### Folder Structure
- Root path: `<CASE_ROOT>/data`
- Main subdirectories relevant to the requested M6.9 catalog-screening workflow:
  - `catalog/` — earthquake catalogs, mainshock table, notebooks, and prior derived sequence-analysis outputs.
  - `source_mechanism/` — focal mechanism catalog that can be used as optional context for selected events.
  - `stations/` — station metadata tables.
- Additional folders exist but are secondary for the requested task:
  - `active_fault/`, `DEM/`, `event_screen/`, `slab2.0/`.

#### Priority Files for Future Agents
1. **Relocated local catalog**
   - Path: `catalog/Snet_catalog_relocate_250601_260501.csv`
   - Format: CSV
   - Size: 1,506,640 bytes
   - Shape: 25,646 rows × 5 columns
   - Columns:
     - `datetime` — origin time string, ISO-like UTC format with trailing `Z`, e.g. `2025-06-01T00:13:38.900000Z`
     - `lat` — latitude in degrees
     - `lon` — longitude in degrees
     - `dep` — depth in km
     - `mag` — magnitude
   - Data quality notes:
     - No missing values in the 5 core columns.
     - All fields are simple flat columns; no event ID column is present in this file.
   - Example rows indicate regional seismicity covering northeastern Japan offshore/onshore coordinates.

2. **Mainshock reference table**
   - Path: `catalog/main_earthquake.csv`
   - Format: CSV
   - Size: 184 bytes
   - Shape: 3 rows × 6 columns
   - Columns:
     - `index` — event label (`M1`, `M2`, `M3`)
     - `datetime`
     - `lat`
     - `lon`
     - `dep`
     - `mag`
   - Contents:
     - `M1`: `2025-11-09 08:03:39.240`, lat `39.402`, lon `143.507`, dep `15.9`, mag `6.9`
     - `M2`: `2025-12-08 14:15:10.180`, mag `7.5`
     - `M3`: `2026-04-20 07:52:58.060`, mag `7.7`
   - Use note:
     - This is the authoritative small lookup table for selecting the target M6.9 event label `M1` before optionally rematching to the relocated catalog.

3. **Optional focal-mechanism context**
   - Path: `source_mechanism/Snet_mecha.csv`
   - Format: CSV
   - Size: 61,681 bytes
   - Shape: 354 rows × 29 columns
   - Main columns:
     - Event identity and hypocenter: `event_code`, `origin_time`, `lat_deg`, `lon_deg`, `depth_km`
     - Magnitudes: `mag_1`, `mag_1_type`, `mag_2`, `mag_2_type`
     - Region/context: `region_name`, `n_hypo_stations`, `m_method`, `m_source`
     - Principal axes: `P_axis_azimuth`, `P_axis_dip`, `T_axis_azimuth`, `T_axis_dip`, `N_axis_azimuth`, `N_axis_dip`
     - Nodal planes: `strike_plane1`, `dip_plane1`, `rake_plane1`, `strike_plane2`, `dip_plane2`, `rake_plane2`
     - Quality/support: `focal_mech_score`, `n_mech_stations`, `focal_mech_projection`, `source_file`
   - Missingness pattern:
     - `mag_2` and many mechanism-specific fields have 215 nulls, implying only a subset of events have full focal-mechanism solutions.
   - Use note:
     - Useful only as optional annotation/context; it is not required for the basic M6.9-centered catalog extraction.

4. **Station metadata**
   - Path: `stations/station.sta`
   - Format: comma-separated text file
   - Size: 16,102 bytes
   - Lines: 372
   - Header:
     - `station_code,station_number,latitude,longitude,elevation_m,matched`
   - Example row:
     - `A.ASMS,5572,40.885667,140.874000,-3,True`
   - Use note:
     - Station geometry may be helpful for context or plotting, but it is not necessary for direct event-window statistics from the relocated catalog.

#### Other Nearby Catalog Files
Within `catalog/`, several related files suggest alternative time spans or processing versions:
- `Snet_catalog_relocate.csv`
- `Snet_catalog_relocate_250601_260625.csv`
- `Snet_catalog_relocate_250930_260501.csv`
- `Snet_catalog_250601_260625_filter.csv`
- `Snet_catalog_20200101_20260522_filter.csv`
- `backup/` contains older catalog versions such as `Snet_catalog-v1.csv`, `Snet_catalog-v2.csv`, and backup full catalogs.

For the user-prioritized task, the requested target file is specifically:
- `catalog/Snet_catalog_relocate_250601_260501.csv`

#### Existing Derived Analysis Outputs Present
The directory already contains prior generated products under:
- `catalog/M69_migration/`
- `catalog/swarm_like_analysis/`
- `event_screen/`

Examples include PNG/PDF/SVG figures and CSV/JSON summaries such as:
- `m69_summary.json`
- `m69_selected_events.csv`
- `m69_phase_rate_summary.csv`
- `m69_distance_front_fits.csv`
- `m69_convex_hull_metrics.csv`

These appear to be downstream outputs rather than raw inputs. Future agents should treat them as existing artifacts for reference only unless the workflow explicitly intends to reuse prior derived products.

#### Naming Conventions and Organization Patterns
- Catalog filenames commonly encode date ranges in `YYMMDD_YYMMDD` form, e.g.:
  - `Snet_catalog_relocate_250601_260501.csv`
- Main event labels use compact identifiers (`M1`, `M2`, `M3`) in `main_earthquake.csv`.
- Derived M6.9 sequence outputs are grouped under `catalog/M69_migration/` with a consistent prefix such as `m69_...`.
- Mechanism files use `Snet_mecha.csv` or dated source files listed in the `source_file` column.

#### Fields Most Relevant to the Requested Future Analysis
For constructing an M6.9-centered event table and computing relative metrics, the essential raw fields are:
- From `catalog/Snet_catalog_relocate_250601_260501.csv`:
  - `datetime`, `lat`, `lon`, `dep`, `mag`
- From `catalog/main_earthquake.csv`:
  - `index`, `datetime`, `lat`, `lon`, `dep`, `mag`

These are sufficient for future agents to derive:
- relative time to M1,
- epicentral distance from the M6.9 reference,
- local east/north Cartesian coordinates,
- window labels (pre/post/mainshock-context),
- event-rate and magnitude-threshold counts,
- spatial footprint metrics.

Optional enrichment fields:
- `source_mechanism/Snet_mecha.csv`: mechanism and quality columns for matched larger events.
- `stations/station.sta`: station geometry metadata.

#### Data Loading Notes
- The relocated catalog uses a UTC-style timestamp string with `T` separator and `Z` suffix; future agents should parse it as timezone-aware or normalize consistently.
- `main_earthquake.csv` uses a space-separated datetime string without `Z`; care is needed to standardize datetime parsing before matching with the relocated catalog.
- The relocated catalog does not include an explicit event identifier, so event matching to `main_earthquake.csv` must be based on time-space proximity if needed.
- All priority files are plain text CSV-like tables and can be loaded with standard `pandas.read_csv` without specialized geophysical I/O libraries.

------------------------------

## Snet_catalog_relocate_250601_260501.csv
**Source path**: `data/catalog/Snet_catalog_relocate_250601_260501.csv`
### Summary
`Snet_catalog_relocate_250601_260501.csv` is the primary relocated earthquake catalog for the requested M6.9-centered screening workflow. It is a flat CSV with 25,646 events and 5 complete core fields—origin time, latitude, longitude, depth, and magnitude—suitable for deriving relative time, epicentral distance, local Cartesian coordinates, and simple phase labels when paired with `main_earthquake.csv`.
### Detail
#### File Overview
- Path: `data/catalog/Snet_catalog_relocate_250601_260501.csv`
- Absolute source: `<CASE_ROOT>/data/catalog/Snet_catalog_relocate_250601_260501.csv`
- Format: CSV
- Size: 1,506,640 bytes
- Shape: 25,646 rows × 5 columns
- Organization: one event per row, with no nested structure and no explicit event ID column.

#### Columns
The file contains exactly these columns:
- `datetime`
  - Type on read: string/object
  - Example: `2025-06-01T00:13:38.900000Z`
  - Notes: ISO-like UTC timestamp with `T` separator and trailing `Z`; appropriate for direct datetime parsing.
- `lat`
  - Type: float64
  - Meaning: event latitude in decimal degrees
- `lon`
  - Type: float64
  - Meaning: event longitude in decimal degrees
- `dep`
  - Type: float64
  - Meaning: event depth in km
- `mag`
  - Type: float64
  - Meaning: event magnitude

#### Data Completeness
- Null counts:
  - `datetime`: 0
  - `lat`: 0
  - `lon`: 0
  - `dep`: 0
  - `mag`: 0
- This means the file is immediately usable for distance, time-window, and magnitude-threshold screening without mandatory missing-data cleaning in the core columns.

#### Example Records
First few rows show the row-wise structure:
- `2025-06-01T00:13:38.900000Z, 39.245593, 142.382422, 29.70, 1.7`
- `2025-06-01T00:30:20.430000Z, 41.623617, 142.114681, 55.14, 1.7`
- `2025-06-01T02:20:26.570000Z, 41.533988, 143.589616, 7.08, 1.7`

#### Relevance to the Requested M6.9 Workflow
This file contains the minimum required fields for future agents to build the requested M6.9-centered event table by deriving:
- relative time to the M1 mainshock,
- epicentral distance from the M6.9 reference point,
- local east/north Cartesian coordinates,
- analysis-window phase labels,
- event-rate summaries,
- magnitude threshold counts,
- time-distance migration diagnostics,
- PCA-based rotated coordinates and convex-hull metrics.

#### Required Companion Reference File
To anchor the target event, future agents should pair this catalog with:
- `data/catalog/main_earthquake.csv`

That companion table contains `M1` with:
- `datetime`: `2025-11-09 08:03:39.240`
- `lat`: `39.402`
- `lon`: `143.507`
- `dep`: `15.9`
- `mag`: `6.9`

Because the relocated catalog has no event ID column, rematching `M1` to this catalog must be done by time/space proximity if desired.

#### Access Pattern for Future Agents
Typical loading pattern:
- Read as a standard CSV with `pandas.read_csv`.
- Parse `datetime` into timezone-aware timestamps if possible because of the trailing `Z`.
- Standardize the `main_earthquake.csv` time format before comparing against this catalog, since the mainshock table uses a space-separated datetime string rather than the `T...Z` style used here.

#### Structural Constraints and Practical Notes
- No station, mechanism, uncertainty, or phase-pick metadata are present in this file.
- No explicit catalog event code or unique identifier is present.
- All event geometry for downstream screening must therefore be computed from `lat`, `lon`, and `dep` after loading.
- The file is compact enough for in-memory analysis with standard pandas/numpy workflows.

#### Naming Convention
- Filename: `Snet_catalog_relocate_250601_260501.csv`
- Pattern suggests a relocated catalog spanning approximately `2025-06-01` to `2026-05-01`.
- Related sibling files in the same directory use similar date-range naming and may represent alternate coverage windows or versions, but this specific file is the user-designated target input.

------------------------------

## main_earthquake.csv
**Source path**: `data/catalog/main_earthquake.csv`
### Summary
`main_earthquake.csv` is a small reference table listing three major earthquakes (`M1`–`M3`) with origin time, hypocenter, and magnitude. For the requested workflow, `M1` is the key anchor event: the 2025-11-09 Sanriku-Oki JMA M6.9 mainshock used to define the analysis origin and to optionally rematch against the relocated catalog.
### Detail
#### File Overview
- Path: `data/catalog/main_earthquake.csv`
- Absolute source: `<CASE_ROOT>/data/catalog/main_earthquake.csv`
- Format: CSV
- Size: 184 bytes
- Shape: 3 rows × 6 columns
- Organization: one named large event per row.

#### Columns
The file contains these columns:
- `index`
  - Type: string/object
  - Meaning: event label identifier
  - Values present: `M1`, `M2`, `M3`
- `datetime`
  - Type on read: string/object
  - Example format: `2025-11-09 08:03:39.240`
  - Notes: space-separated timestamp string without trailing `Z`
- `lat`
  - Type: float64
  - Meaning: latitude in decimal degrees
- `lon`
  - Type: float64
  - Meaning: longitude in decimal degrees
- `dep`
  - Type: float64
  - Meaning: depth in km
- `mag`
  - Type: float64
  - Meaning: event magnitude

#### Data Completeness
- Null counts are zero for all six columns:
  - `index`: 0
  - `datetime`: 0
  - `lat`: 0
  - `lon`: 0
  - `dep`: 0
  - `mag`: 0

#### Full Contents
The table contains exactly three events:
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

#### Relevance to the Requested M6.9 Workflow
For the user-prioritized task, the key row is:
- `index == 'M1'`

This row provides the reference event needed to:
- define the target Sanriku-Oki M6.9 mainshock,
- establish the reference origin time,
- define the reference epicenter and depth,
- construct pre/post event windows,
- rematch the mainshock against the relocated catalog if a near-time/near-space event exists.

#### Matching and Parsing Notes
- The `datetime` format here differs from the relocated catalog format:
  - `main_earthquake.csv`: `YYYY-MM-DD HH:MM:SS.sss`
  - relocated catalog: `YYYY-MM-DDTHH:MM:SS.ssssssZ`
- Future agents should normalize these time formats before comparing or merging.
- Because this file is only a reference table and not a full catalog, it does not contain event IDs that directly link to rows in the relocated catalog.
- Rematching `M1` to `Snet_catalog_relocate_250601_260501.csv` must therefore rely on time and spatial proximity.

#### Access Pattern
- Can be loaded directly using `pandas.read_csv`.
- Since the file is tiny, it is suitable for immediate in-memory lookup, for example selecting `M1` by `index`.

#### Role in the Directory
This is a compact manual/curated summary table of major target events, distinct from the large row-wise relocated catalog. It is best treated as the authoritative event-reference metadata source for choosing the mainshock origin and analysis center.

------------------------------

## Snet_mecha.csv
**Source path**: `data/source_mechanism/Snet_mecha.csv`
### Summary
`Snet_mecha.csv` is an optional focal-mechanism context catalog containing 354 events with hypocenter, magnitude, nodal-plane, principal-axis, and quality-related fields. It is useful for annotating or cross-checking larger events near the M6.9 sequence, but many mechanism-specific columns are populated only for a subset of rows, so it should be treated as supplemental rather than core input.
### Detail
#### File Overview
- Path: `data/source_mechanism/Snet_mecha.csv`
- Absolute source: `<CASE_ROOT>/data/source_mechanism/Snet_mecha.csv`
- Format: CSV
- Size: 61,681 bytes
- Shape: 354 rows × 29 columns
- Organization: one mechanism record per event.

#### Columns
The file contains the following columns:
- Event identity and location/time:
  - `event_code`
  - `origin_time`
  - `lat_deg`
  - `lon_deg`
  - `depth_km`
- Magnitude fields:
  - `mag_1`
  - `mag_1_type`
  - `mag_2`
  - `mag_2_type`
- Context and source metadata:
  - `region_name`
  - `n_hypo_stations`
  - `m_method`
  - `m_source`
  - `source_file`
- Principal-axis parameters:
  - `P_axis_azimuth`
  - `P_axis_dip`
  - `T_axis_azimuth`
  - `T_axis_dip`
  - `N_axis_azimuth`
  - `N_axis_dip`
- Nodal-plane parameters:
  - `strike_plane1`
  - `dip_plane1`
  - `rake_plane1`
  - `strike_plane2`
  - `dip_plane2`
  - `rake_plane2`
- Quality/support fields:
  - `focal_mech_score`
  - `n_mech_stations`
  - `focal_mech_projection`

#### Data Types
- String/object columns include:
  - `event_code`, `origin_time`, `mag_1_type`, `mag_2_type`, `region_name`, `m_method`, `m_source`, `focal_mech_projection`, `source_file`
- Numeric float/int columns include location, depth, magnitudes, axes, planes, and score/station-count fields.

#### Missingness Pattern
The file is partially sparse in mechanism-specific fields.
- Fully populated or near-fully populated core columns:
  - `event_code`: 0 nulls
  - `origin_time`: 0
  - `lat_deg`: 0
  - `lon_deg`: 0
  - `depth_km`: 0
  - `mag_1`: 0
  - `mag_1_type`: 0
  - `region_name`: 0
  - `n_hypo_stations`: 0
  - `source_file`: 0
- Columns with substantial missing data (215 nulls each):
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

This indicates that only a subset of the 354 events has full focal-mechanism solutions.

#### Example Records
Sample rows show the overall format:
- `J2025100111563882`, `2025-10-01 02:56:38.820`, `41.813333`, `142.668167`, `56.44`, `mag_1=3.5`, region `S OFF URAKAWA`
- `J2025100123500609`, `2025-10-01 14:50:06.090`, `38.698833`, `141.975833`, `58.73`, `mag_1=4.6`, region `KINKAZAN REGION`
- `J2025100317451495`, `2025-10-03 08:45:14.950`, `38.345333`, `141.679500`, `52.98`, `mag_1=3.3`, region `KINKAZAN REGION`

Example populated mechanism fields include azimuth/dip values for P/T/N axes and strike/dip/rake for two nodal planes, plus a `focal_mech_score` and `n_mech_stations`.

#### Relevance to the Requested M6.9 Workflow
This file is not required for building the main M6.9-centered seismicity table, but it can support future agents in these limited ways:
- identify whether the M6.9 mainshock or the largest early aftershock has a matching mechanism record,
- annotate selected larger events on figures or tables,
- provide optional mechanism quality context (`focal_mech_score`, `n_mech_stations`, `focal_mech_projection`),
- compare `origin_time` and hypocenter fields with the relocated catalog for approximate event matching.

#### Matching Notes
- There is no obvious direct shared key with the relocated catalog, because the relocated catalog lacks an event ID column.
- Matching must therefore be performed approximately using:
  - time (`origin_time` vs catalog `datetime`),
  - latitude/longitude,
  - depth,
  - possibly magnitude.
- `origin_time` is stored as a string in format like `YYYY-MM-DD HH:MM:SS.sss`, so future agents should normalize this to the same time convention used for the relocated catalog before joining.

#### Practical Use Guidance
- Treat `lat_deg`, `lon_deg`, `depth_km`, `origin_time`, and `mag_1` as the most reliable fields for cross-reference.
- Treat the full mechanism geometry fields as optional and subset-dependent.
- Because many rows lack complete mechanism solutions, downstream code should check for nulls before plotting or summarizing nodal-plane/axis information.

#### File Role in Directory
This file acts as a supplemental event-level metadata table, distinct from the main relocated seismicity catalog. It is best used for context on notable events rather than as the primary source for rate, migration, distance-front, hull, or b-value screening.

------------------------------

## station.sta
**Source path**: `data/stations/station.sta`
### Summary
`station.sta` is a plain-text, comma-separated station metadata table with 372 lines, including a header and rows containing station code, station number, latitude, longitude, elevation, and a match flag. It is optional context for the M6.9 catalog workflow, mainly useful for plotting network geometry or checking whether stations were matched into the local metadata set.
### Detail
#### File Overview
- Path: `data/stations/station.sta`
- Absolute source: `<CASE_ROOT>/data/stations/station.sta`
- Format: plain text, comma-separated values
- Size: 16,102 bytes
- Total lines: 372
- Organization: one station per row, with a single header line followed by station records.

#### Header / Columns
The file begins with this header:
- `station_code,station_number,latitude,longitude,elevation_m,matched`

Column meanings inferred from the header and sample rows:
- `station_code`
  - Station identifier string
  - Example: `A.ASMS`
- `station_number`
  - Numeric station code/id
  - Example: `5572`
- `latitude`
  - Decimal degrees
- `longitude`
  - Decimal degrees
- `elevation_m`
  - Elevation in meters
  - Can be negative for below-sea-level or seafloor-related sites
- `matched`
  - Boolean-like text flag
  - Example: `True`

#### Example Rows
First few records:
- `A.ASMS,5572,40.885667,140.874000,-3,True`
- `A.CHOG,5550,41.327167,140.815333,0,True`
- `A.HGTZ,5571,40.982833,140.904000,-11,True`
- `A.HRDA,5549,41.448833,140.881000,2,True`

These examples show a simple flat table that can be parsed directly with `pandas.read_csv`.

#### Relevance to the Requested M6.9 Workflow
This file is not required for the core catalog-screening steps based on event origin time, location, depth, and magnitude. It may still be useful for future agents to:
- plot station locations as map context behind the M6.9 sequence,
- inspect approximate station coverage near the study region,
- document which stations are marked as `matched` in the local metadata set.

#### Practical Notes for Future Agents
- The file extension is `.sta`, but the content is standard comma-separated text rather than a fixed-width or binary station format.
- Because the structure is CSV-like, standard loading is straightforward with `pandas.read_csv`.
- No event linkage or pick-level information is present, so this file cannot be used alone to reconstruct catalog detection details.
- The most relevant fields for plotting are `station_code`, `latitude`, `longitude`, and optionally `matched`.

#### Role in Directory
`station.sta` is a supplemental metadata table for station geometry, distinct from the earthquake catalogs and focal-mechanism files. For the specific M6.9 pre/post comparison requested by the user, it should be treated as optional display/context data rather than a primary analysis input.

------------------------------

