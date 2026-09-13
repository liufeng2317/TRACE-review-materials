# Data Descriptions
## data
**Source path**: `<CASE_ROOT>/data`
### Summary
This data folder is organized around an Aomori-region earthquake catalog workflow, with the key inputs for sequence-centered analysis located in `catalog/`, `source_mechanism/`, and `stations/`. The primary event catalog (`Snet_catalog_relocate_250930_260501.csv`) contains 22,096 relocated events with time, latitude, longitude, depth, and magnitude, while `main_earthquake.csv` defines the three target mainshocks (M1, M2, M3) used to build relative-time and distance-based sequence tables.
### Detail
#### Folder Structure

Top-level subdirectories and notable files relevant to the requested sequence-characterization workflow:

- `catalog/`
  - `Snet_catalog_relocate_250930_260501.csv` — primary relocated earthquake catalog for building mainshock-referenced event tables.
  - `main_earthquake.csv` — the three target mainshocks (M1, M2, M3).
  - Additional catalog variants and notebooks are present, including:
    - `Snet_catalog_full_250930_260501.csv`
    - `Snet_catalog_full_251101_260420.csv`
    - `Snet_catalog_relocate_250930_26_0501.csv`
    - `Snet_catalog-v1.csv`, `Snet_catalog-v2.csv`
    - `catalog.ipynb`, `swarm_like.ipynb`
    - `catalog_compare_check.png`
  - `swarm_like_figures/` exists as a subfolder.
- `source_mechanism/`
  - `Snet_mecha.csv` — focal mechanism/event-mechanism context table.
  - `back/` — auxiliary subfolder.
- `stations/`
  - `station.sta` — station metadata in CSV-like text form.
  - `japan_stations.txt` — additional station listing.
- Other contextual but less central directories for this task:
  - `active_fault/` with `japan_active_faults.geojson`
  - `DEM/` with raster products
  - `visualize.ipynb`

For future agents, the analysis-relevant access pattern is:
- event catalog from `catalog/Snet_catalog_relocate_250930_260501.csv`
- mainshock definitions from `catalog/main_earthquake.csv`
- mechanism context from `source_mechanism/Snet_mecha.csv`
- station coverage/context from `stations/station.sta`

#### Primary Catalog: `catalog/Snet_catalog_relocate_250930_260501.csv`

- Format: CSV
- Size: 1,297,948 bytes
- Shape: 22,096 rows × 5 columns
- Columns:
  - `datetime` (`object`, ISO-like UTC string with trailing `Z`)
  - `lat` (`float64`)
  - `lon` (`float64`)
  - `dep` (`float64`) — depth in km
  - `mag` (`float64`)
- Missing values: none in any column

Basic coverage:
- Time range: `2025-09-30T16:09:25.360000Z` to `2026-05-01T14:44:22.450000Z`
- Latitude range: 38.503003 to 42.382633
- Longitude range: 141.001921 to 144.49847
- Depth range: 0.05 to 121.14 km
- Magnitude range: -0.5 to 7.7

Magnitude-count summary useful for later filtering:
- `M >= 4`: 259 events
- `M >= 5`: 68 events
- `M >= 6`: 13 events

Example records:
- `2025-09-30T16:09:25.360000Z, 38.703422, 142.256738, 41.35, 2.8`
- `2025-09-30T16:55:18.670000Z, 38.959892, 142.594434, 27.66, 1.2`
- `2025-09-30T18:47:05.380000Z, 39.934501, 142.485905, 34.75, 1.6`

Implications for loading:
- This file is minimal and well-suited for constructing relative-time, epicentral-distance, and depth-difference tables around each mainshock.
- `datetime` should be parsed explicitly as timezone-aware UTC if using pandas (`parse_dates=['datetime']`).
- No event ID column is present, so future matching to other tables will likely rely on origin time plus location/magnitude tolerance rather than a direct key.

#### Mainshock Definition Table: `catalog/main_earthquake.csv`

- Format: CSV
- Size: 184 bytes
- Shape: 3 rows × 6 columns
- Columns:
  - `index` (`object`) — sequence labels
  - `datetime` (`object`)
  - `lat` (`float64`)
  - `lon` (`float64`)
  - `dep` (`float64`)
  - `mag` (`float64`)
- Missing values: none

Contents:
- `M1`: `2025-11-09 08:03:39.240`, lat 39.402, lon 143.507, dep 15.9 km, mag 6.9
- `M2`: `2025-12-08 14:15:10.180`, lat 40.968, lon 142.288, dep 53.5 km, mag 7.5
- `M3`: `2026-04-20 07:52:58.060`, lat 39.842, lon 143.157, dep 19.4 km, mag 7.7

Notes for future agents:
- This is the authoritative list of the three mainshock centers requested by the user.
- `index` is already the intended label set (`M1`, `M2`, `M3`) for row-based subplot organization.
- The datetime format here differs slightly from the catalog format (no `Z` suffix), so parsing/normalization will be needed before joining or computing relative times.

#### Mechanism Context: `source_mechanism/Snet_mecha.csv`

- Format: CSV
- Size: 61,681 bytes
- Shape: 354 rows × 29 columns

Columns:
- Event identity and origin:
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
- Region and method metadata:
  - `region_name`
  - `n_hypo_stations`
  - `m_method`
  - `m_source`
- Principal axes:
  - `P_axis_azimuth`, `P_axis_dip`
  - `T_axis_azimuth`, `T_axis_dip`
  - `N_axis_azimuth`, `N_axis_dip`
- Nodal planes:
  - `strike_plane1`, `dip_plane1`, `rake_plane1`
  - `strike_plane2`, `dip_plane2`, `rake_plane2`
- Mechanism quality/support:
  - `focal_mech_score`
  - `n_mech_stations`
  - `focal_mech_projection`
  - `source_file`

Data characteristics:
- Time range: `2025-10-01 02:56:38.820000` to `2026-05-19 10:23:35.210000`
- Common regions include:
  - `E OFF AOMORI PREF` (195 rows)
  - `E OFF IWATE PREF` (34)
  - `E OFF MIYAGI PREF` (22)
  - `KINKAZAN REGION` (22)
  - `NE OFF IWATE PREF` (14)
- Important missingness:
  - `mag_2`: 215 nulls
  - `mag_2_type`: 215 nulls
  - `focal_mech_score`: 215 nulls
  - `n_mech_stations`: 215 nulls

Example content indicates mechanism solutions are available for only a subset of events and may include one or two magnitude estimates plus nodal-plane geometry.

Notes for future agents:
- This table is suitable as contextual evidence for whether larger events around M1/M2/M3 share similar structural domains or mechanism styles.
- There is no obvious direct common key with `Snet_catalog_relocate_250930_260501.csv`; practical matching will likely require tolerance-based joins using `origin_time`, `lat/lon`, `depth`, and magnitude.
- Because many rows lack mechanism-quality fields, coverage should be summarized before any downstream interpretation.

#### Station Metadata: `stations/station.sta`

- Format: comma-separated text file with header
- Size: 16,102 bytes
- Parsed shape: 371 rows × 6 columns
- Header fields:
  - `station_code`
  - `station_number`
  - `latitude`
  - `longitude`
  - `elevation_m`
  - `matched`

Preview:
- `A.ASMS,5572,40.885667,140.874000,-3,True`
- `A.CHOG,5550,41.327167,140.815333,0,True`
- `A.HGTZ,5571,40.982833,140.904000,-11,True`
- `A.HRDA,5549,41.448833,140.881000,2,True`

Coverage summary:
- 371 stations total
- `matched`: all 371 are `True`
- Latitude range: 36.880833 to 44.118833
- Longitude range: 139.245333 to 145.738833

Notes for future agents:
- This file is useful for describing network/station context but is not required to compute the requested mainshock-relative event metrics.
- It can support later sanity checks on geographic coverage or plotting network maps if needed.

#### Naming Conventions and Organizational Patterns

- Catalog files are stored under `catalog/` and use descriptive names such as:
  - `Snet_catalog_relocate*.csv` for relocated catalogs
  - `Snet_catalog_full*.csv` for fuller/original variants
  - `main_earthquake.csv` for manually curated target events
- Mechanism products are under `source_mechanism/` with `Snet_mecha.csv` as the main compiled table.
- Station information is under `stations/`, with `station.sta` behaving like a CSV despite the `.sta` suffix.

Useful example paths:
- `<CASE_ROOT>/data/catalog/Snet_catalog_relocate_250930_260501.csv`
- `<CASE_ROOT>/data/catalog/main_earthquake.csv`
- `<CASE_ROOT>/data/source_mechanism/Snet_mecha.csv`
- `<CASE_ROOT>/data/stations/station.sta`

#### Relevance to the Requested Workflow

The most directly relevant fields for future agents building sequence-centered diagnostics are:

- From `Snet_catalog_relocate_250930_260501.csv`:
  - `datetime` for relative time to each mainshock
  - `lat`, `lon` for epicentral distance calculations
  - `dep` for depth difference
  - `mag` for magnitude thresholds, marker scaling, and M4+/M5+/M6+ counts
- From `main_earthquake.csv`:
  - `index`, `datetime`, `lat`, `lon`, `dep`, `mag` for defining M1/M2/M3 reference events
- From `Snet_mecha.csv`:
  - `origin_time`, `lat_deg`, `lon_deg`, `depth_km`, `mag_1`, `region_name`
  - mechanism geometry (`strike*`, `dip*`, `rake*`) and support/quality fields (`focal_mech_score`, `n_mech_stations`)
- From `station.sta`:
  - station coordinates and coverage metadata

#### Practical Loading Notes

- `Snet_catalog_relocate_250930_260501.csv` and `main_earthquake.csv` use different datetime string styles; normalize to a common timezone-aware format before computing relative times.
- The primary catalog has no unique event identifier, so any cross-reference with focal mechanisms will require approximate matching by time and hypocenter parameters.
- `station.sta` can be loaded directly with `pandas.read_csv()` despite its extension.
- The folder also contains notebooks and alternate catalog versions; unless reproducibility checks are needed, future agents should begin with the explicitly named primary inputs listed above.

------------------------------

## Snet_catalog_relocate_250930_260501.csv
**Source path**: `catalog/Snet_catalog_relocate_250930_260501.csv`
### Summary
This is the primary relocated earthquake event catalog for the Aomori workflow. It is a compact CSV with 22,096 events and only the core fields needed for mainshock-centered sequence construction: origin time, latitude, longitude, depth, and magnitude.
### Detail
#### File Overview

- File: `catalog/Snet_catalog_relocate_250930_260501.csv`
- Format: CSV
- Size: 1,297,948 bytes
- Shape: 22,096 rows × 5 columns
- Intended role in the project: primary event catalog for building mainshock-referenced tables and all later time-distance-magnitude summaries.

#### Column Schema

The file contains exactly five columns:

1. `datetime`
   - Type on read: string/object
   - Format example: `2025-09-30T16:09:25.360000Z`
   - Notes:
     - ISO-like timestamp with fractional seconds and trailing `Z`.
     - Should be parsed as UTC-aware datetime for relative-time calculations.
     - This is the key field for pre/post windows such as ±7, ±14, and ±25 days.

2. `lat`
   - Type: `float64`
   - Meaning: event latitude in decimal degrees
   - Use: epicentral distance calculations to each mainshock.

3. `lon`
   - Type: `float64`
   - Meaning: event longitude in decimal degrees
   - Use: epicentral distance calculations to each mainshock.

4. `dep`
   - Type: `float64`
   - Meaning: event depth in km
   - Use: depth-difference calculations relative to each mainshock and depth-distribution summaries.

5. `mag`
   - Type: `float64`
   - Meaning: event magnitude
   - Use: marker sizing, thresholding for M4+/M5+/M6+, magnitude-bin counts, magnitude-gap metrics, and companion-event statistics.

#### Completeness and Data Quality

- Missing values:
  - `datetime`: 0
  - `lat`: 0
  - `lon`: 0
  - `dep`: 0
  - `mag`: 0
- There is no explicit event ID column.
- There is no uncertainty/error column, phase count, region label, or mechanism information in this file.
- Because no event identifier is provided, future joins to mechanism or other context tables will need tolerance-based matching using origin time and hypocentral parameters.

#### Coverage Summary

- Time range:
  - Start: `2025-09-30 16:09:25.360000+00:00`
  - End: `2026-05-01 14:44:22.450000+00:00`
- Spatial range:
  - Latitude: 38.503003 to 42.382633
  - Longitude: 141.001921 to 144.49847
- Depth range:
  - 0.05 to 121.14 km
- Magnitude range:
  - -0.5 to 7.7

These ranges indicate the catalog spans a broader northeastern Japan offshore/onshore region rather than only a tight Aomori local cluster, which is relevant for later separation of near-field sequence behavior from broader regional activity.

#### Magnitude Distribution Metadata Relevant to Future Sequence Work

Counts above key thresholds:
- `M >= 4`: 259 events
- `M >= 5`: 68 events
- `M >= 6`: 13 events

These threshold counts are directly relevant for:
- M4+/M5+/M6+ counts in matched pre/post windows
- magnitude-bin summaries
- companion-event and dominance-gap metrics
- moderate/large event distance-band contributions

#### Example Records

First few rows:
- `2025-09-30T16:09:25.360000Z, 38.703422, 142.256738, 41.35, 2.8`
- `2025-09-30T16:55:18.670000Z, 38.959892, 142.594434, 27.66, 1.2`
- `2025-09-30T18:47:05.380000Z, 39.934501, 142.485905, 34.75, 1.6`

This preview confirms the file is event-per-row and already normalized into a minimal analysis-friendly schema.

#### Relevance to the Requested Analysis Workflow

This single file provides the raw inputs needed to derive, for each event relative to each mainshock:
- relative time
- epicentral distance
- depth difference
- cumulative-radius membership (e.g., <=30, <=60, <=100 km)
- annular distance band (0-30, 30-60, 60-100 km)
- magnitude-threshold flags (M4+, M5+, M6+)
- candidate mainshock-like identification when compared against a separate mainshock reference table

It is therefore sufficient for constructing:
- mainshock-centered event tables
- short-window time-magnitude and time-distance plots
- pre/post counts by magnitude bin and distance band
- matched-window metrics across different radii and time windows
- magnitude hierarchy and companion-event summaries
- depth summaries

#### Important Limitations for Future Agents

- No direct mainshock labels are included here; mainshock definitions must come from `catalog/main_earthquake.csv`.
- No mechanism data are included; focal mechanism context must come from `source_mechanism/Snet_mecha.csv`.
- No station/network information is included; station context must come from `stations/station.sta`.
- No event ID means cross-dataset association is approximate rather than exact unless another internal key is introduced.

#### Practical Loading Notes

Recommended loading pattern:
- Parse `datetime` explicitly as datetime with UTC awareness.
- Keep `lat`, `lon`, `dep`, and `mag` as numeric floats.
- Expect straightforward CSV ingestion with pandas or similar tools.

Example path:
- `<CASE_ROOT>/data/catalog/Snet_catalog_relocate_250930_260501.csv`

#### Minimal File Description for Downstream Agents

Use this file as the authoritative relocated seismicity table. Combine it with `main_earthquake.csv` to compute event-mainshock relative geometry and timing, and use external context tables only after this core event table has been built.

------------------------------

## main_earthquake.csv
**Source path**: `catalog/main_earthquake.csv`
### Summary
This file is the compact reference table defining the three target mainshocks used throughout the Aomori sequence workflow. It contains exactly three rows, labeled M1, M2, and M3, with the origin time, epicenter, depth, and magnitude needed to center relative-time and relative-distance analyses.
### Detail
#### File Overview

- File: `catalog/main_earthquake.csv`
- Format: CSV
- Size: 184 bytes
- Shape: 3 rows × 6 columns
- Role in workflow: authoritative reference list for the three sequence centers around which all event-relative calculations should be built.

#### Column Schema

The file contains the following columns:

1. `index`
   - Type: `object` / string
   - Meaning: sequence label
   - Values present: `M1`, `M2`, `M3`
   - Use: row ordering in comparison tables/figures and sequence labeling throughout downstream analysis.

2. `datetime`
   - Type on read: string/object
   - Example format: `2025-11-09 08:03:39.240`
   - Use: reference origin time for computing relative event times.
   - Note: unlike the main event catalog, this timestamp string does not include a trailing `Z`, so future agents should normalize timezone handling before joining or comparing with UTC-aware catalog times.

3. `lat`
   - Type: `float64`
   - Meaning: mainshock latitude in decimal degrees
   - Use: epicentral distance calculations.

4. `lon`
   - Type: `float64`
   - Meaning: mainshock longitude in decimal degrees
   - Use: epicentral distance calculations.

5. `dep`
   - Type: `float64`
   - Meaning: mainshock depth in km
   - Use: depth-difference calculations and depth-context summaries.

6. `mag`
   - Type: `float64`
   - Meaning: mainshock magnitude
   - Use: mainshock ranking, marker annotation, magnitude-gap calculations, and companion-event comparisons.

#### Completeness

- Missing values:
  - `index`: 0
  - `datetime`: 0
  - `lat`: 0
  - `lon`: 0
  - `dep`: 0
  - `mag`: 0

This is a complete reference table with no null fields.

#### Full Contents

The file defines exactly three mainshock entries:

- `M1`
  - `datetime`: `2025-11-09 08:03:39.240`
  - `lat`: 39.402
  - `lon`: 143.507
  - `dep`: 15.9 km
  - `mag`: 6.9

- `M2`
  - `datetime`: `2025-12-08 14:15:10.180`
  - `lat`: 40.968
  - `lon`: 142.288
  - `dep`: 53.5 km
  - `mag`: 7.5

- `M3`
  - `datetime`: `2026-04-20 07:52:58.060`
  - `lat`: 39.842
  - `lon`: 143.157
  - `dep`: 19.4 km
  - `mag`: 7.7

#### Relevance to the Requested Workflow

This file is the required reference table for all mainshock-centered derivations, including:

- relative time to each mainshock
- epicentral distance to each mainshock
- depth difference from each mainshock
- practical identification of the mainshock-like event inside the broader catalog
- sequence-specific subsetting for ±7, ±14, and ±25 day windows
- sequence row definitions in 3-row diagnostic figure layouts

Because the user specifically requests M1, M2, and M3 comparisons, this file should be treated as the canonical sequence index and display order.

#### Practical Matching Notes

When linking this table to `Snet_catalog_relocate_250930_260501.csv`:

- Use `datetime`, `lat`, `lon`, `dep`, and `mag` together to identify the mainshock-like event in the event catalog.
- A tolerance-based match will likely be needed because:
  - the catalog file uses UTC-style timestamps with `Z`
  - small formatting or rounding differences may exist between reference and catalog representations
- Suggested future-agent use: keep the original mainshock values from this file as the authoritative reference even if the matched event in the catalog shows tiny formatting or precision differences.

#### Relationship to Other Project Files

This file is most useful in combination with:

- `catalog/Snet_catalog_relocate_250930_260501.csv`
  - supplies all surrounding events to compare against each mainshock
- `source_mechanism/Snet_mecha.csv`
  - may provide mechanism context for the mainshock and nearby larger events if tolerance-based matching is performed
- `stations/station.sta`
  - provides network context but is not needed to define the mainshocks themselves

#### Minimal Operational Description for Future Agents

Use `main_earthquake.csv` as the seed table for the three target sequences. Each row is a single mainshock definition with the exact fields needed to build mainshock-referenced event metrics and to organize downstream comparisons in the fixed order M1, M2, M3.

------------------------------

## Snet_mecha.csv
**Source path**: `source_mechanism/Snet_mecha.csv`
### Summary
This file is the focal-mechanism context table for the Aomori catalog workflow. It contains 354 mechanism-related event records with origin time, hypocenter, one or two magnitude fields, regional labels, principal-axis and nodal-plane geometry, and partial quality/support metadata that can be used to contextualize sequence structure around M1, M2, and M3.
### Detail
#### File Overview

- File: `source_mechanism/Snet_mecha.csv`
- Format: CSV
- Size: 61,681 bytes
- Shape: 354 rows × 29 columns
- Role in workflow: contextual event-mechanism table for checking whether events near the target mainshocks share similar structural or focal-mechanism characteristics.

#### Column Schema

The file contains 29 columns:

1. `event_code`
   - Type: string/object
   - Likely unique event identifier within the mechanism catalog.

2. `origin_time`
   - Type on read: string/object
   - Example format: `2025-10-01 14:50:06.090`
   - Use: approximate event matching against the relocated catalog.

3. `lat_deg`
   - Type: `float64`
   - Event latitude in decimal degrees.

4. `lon_deg`
   - Type: `float64`
   - Event longitude in decimal degrees.

5. `depth_km`
   - Type: `float64`
   - Event depth in km.

6. `mag_1`
   - Type: `float64`
   - Primary magnitude value.

7. `mag_1_type`
   - Type: string/object
   - Primary magnitude type code.

8. `mag_2`
   - Type: `float64`
   - Secondary magnitude value when available.

9. `mag_2_type`
   - Type: string/object
   - Secondary magnitude type code.

10. `region_name`
    - Type: string/object
    - Regional descriptor for the event.

11. `n_hypo_stations`
    - Type: `int64`
    - Number of stations used for hypocenter estimation.

12. `m_method`
    - Type: string/object
    - Magnitude/method metadata code.

13. `m_source`
    - Type: string/object
    - Magnitude/data source metadata code.

14. `P_axis_azimuth`
15. `P_axis_dip`
16. `T_axis_azimuth`
17. `T_axis_dip`
18. `N_axis_azimuth`
19. `N_axis_dip`
   - Type: `float64`
   - Principal stress/strain axis orientation parameters.

20. `strike_plane1`
21. `dip_plane1`
22. `rake_plane1`
23. `strike_plane2`
24. `dip_plane2`
25. `rake_plane2`
   - Type: `float64`
   - Two nodal-plane solutions for focal mechanism interpretation.

26. `focal_mech_score`
   - Type: `float64`
   - Mechanism quality/support score when available.

27. `n_mech_stations`
   - Type: `float64`
   - Number of stations contributing to the mechanism solution when available.

28. `focal_mech_projection`
   - Type: string/object
   - Projection/category metadata; preview values include `LOW`.

29. `source_file`
   - Type: string/object
   - Original source file name, useful for provenance.

#### Data Completeness and Missingness

Important missing-value pattern:
- `mag_2`: 215 missing
- `mag_2_type`: 215 missing
- `focal_mech_score`: 215 missing
- `n_mech_stations`: 215 missing

Implication:
- Mechanism-support metadata and secondary magnitude fields are available only for a subset of rows.
- Future agents should not assume complete mechanism-quality coverage for all events selected near M1, M2, or M3.

Other columns appear populated in previewed rows, but quality and completeness should still be checked after any event subset is formed.

#### Temporal and Regional Coverage

- Time range:
  - Start: `2025-10-01 02:56:38.820000`
  - End: `2026-05-19 10:23:35.210000`
- This overlaps most of the relocated event catalog window and extends somewhat later than the end of `Snet_catalog_relocate_250930_260501.csv`.

Most frequent `region_name` values:
- `E OFF AOMORI PREF`: 195
- `E OFF IWATE PREF`: 34
- `E OFF MIYAGI PREF`: 22
- `KINKAZAN REGION`: 22
- `NE OFF IWATE PREF`: 14
- `OFF NEMURO PENINSULA`: 10
- `S OFF URAKAWA`: 10
- `NORTHERN IWATE PREF`: 10
- `HIDAKA MOUNTAINS REGION`: 8
- `SE OFF TOKACHI`: 7

This indicates the mechanism table is regionally broader than a strict Aomori-only subset, although it is strongly dominated by `E OFF AOMORI PREF` events.

#### Example Rows

Previewed examples show the following structure:

- Example 1
  - `event_code`: `J2025100102563882`
  - `origin_time`: `2025-10-01 02:56:38.820`
  - `lat_deg`: ~42.06
  - `lon_deg`: ~143.19
  - `depth_km`: ~52.76
  - `mag_1`: 3.5
  - `mag_1_type`: `V`
  - `region_name`: `S OFF URAKAWA`
  - nodal planes and axis geometry populated
  - `focal_mech_score`: 98
  - `n_mech_stations`: 65

- Example 2
  - `event_code`: `J2025100123500609`
  - `origin_time`: `2025-10-01 14:50:06.090`
  - `lat_deg`: ~38.70
  - `lon_deg`: ~141.98
  - `depth_km`: ~58.73
  - `mag_1`: 4.6
  - `mag_2`: 4.5
  - `mag_2_type`: `W`
  - `region_name`: `KINKAZAN REGION`
  - full mechanism geometry populated

These examples confirm that the table is event-based and contains sufficient hypocentral and geometric metadata for mechanism-context summaries.

#### Relevance to the Requested Workflow

Most relevant fields for future agents examining mainshock-centered sequences are:

- Matching / sequence association:
  - `origin_time`
  - `lat_deg`
  - `lon_deg`
  - `depth_km`
  - `mag_1`
- Context grouping:
  - `region_name`
- Mechanism comparison:
  - `strike_plane1`, `dip_plane1`, `rake_plane1`
  - `strike_plane2`, `dip_plane2`, `rake_plane2`
  - `P_axis_*`, `T_axis_*`, `N_axis_*`
- Quality/support screening:
  - `focal_mech_score`
  - `n_mech_stations`
  - `n_hypo_stations`

This file is especially suitable for:
- checking whether M4+/M5+ events near a given mainshock cluster have similar or mixed focal mechanisms
- screening whether events appear to occupy a common structural domain
- summarizing how much mechanism coverage exists in each sequence-centered subset

#### Relationship to the Primary Catalog

This file does not share an obvious direct key with `catalog/Snet_catalog_relocate_250930_260501.csv`.
Practical cross-dataset association will likely require tolerance-based matching using:
- event time (`origin_time` vs `datetime`)
- latitude / longitude
- depth
- magnitude (`mag_1` as the most likely comparison field)

Important caveats for future agents:
- timestamp formatting differs from the primary catalog
- not every relocated event has a corresponding mechanism row
- some mechanism rows lack quality fields
- `mag_1` and `mag_2` may not map exactly to the magnitude field in the relocated catalog

#### Practical Loading Notes

- Load with `pandas.read_csv()` and parse `origin_time` as datetime.
- Treat `event_code` as mechanism-table internal identity, not as a guaranteed cross-file join key.
- For analysis subsets, consider retaining both raw mechanism geometry and quality/support columns so later filtering can be done without reloading.

Example path:
- `<CASE_ROOT>/data/source_mechanism/Snet_mecha.csv`

#### Minimal Operational Description for Future Agents

Use `Snet_mecha.csv` as a secondary context table after sequence-centered event subsets have already been defined from the relocated catalog. It is best suited for mechanism-coverage summaries and tolerance-based linkage to moderate/large events near M1, M2, and M3, rather than as the primary event inventory.

------------------------------

## station.sta
**Source path**: `stations/station.sta`
### Summary
This file is a station metadata table used for network context in the Aomori catalog project. It contains 371 stations with code, numeric ID, latitude, longitude, elevation, and a `matched` flag, and can support geographic coverage checks or station-map context for later agents.
### Detail
#### File Overview

- File: `stations/station.sta`
- Format: comma-separated text table with header (CSV-like despite the `.sta` extension)
- Size: 16,102 bytes
- Parsed shape: 371 rows × 6 columns
- Role in workflow: auxiliary station/network context file rather than a primary event-analysis table.

#### Column Schema

The header defines six columns:

1. `station_code`
   - Type: string/object
   - Example values: `A.ASMS`, `A.CHOG`, `A.HGTZ`, `A.HRDA`
   - Likely network-prefixed station identifier.

2. `station_number`
   - Type: integer-like
   - Example values: `5572`, `5550`, `5571`, `5549`
   - Numeric station ID.

3. `latitude`
   - Type: float
   - Station latitude in decimal degrees.

4. `longitude`
   - Type: float
   - Station longitude in decimal degrees.

5. `elevation_m`
   - Type: numeric
   - Station elevation in meters.
   - Preview includes both negative and non-negative values, e.g. `-3`, `0`, `-11`, `2`.

6. `matched`
   - Type: boolean-like
   - Values observed: `True`
   - Likely indicates whether the station was successfully matched to a reference list or retained in the workflow.

#### Example Rows

First rows in the file:
- `A.ASMS,5572,40.885667,140.874000,-3,True`
- `A.CHOG,5550,41.327167,140.815333,0,True`
- `A.HGTZ,5571,40.982833,140.904000,-11,True`
- `A.HRDA,5549,41.448833,140.881000,2,True`

This confirms the file is already cleanly tabular and directly readable with standard CSV parsers.

#### Coverage Summary

- Number of stations: 371
- `matched` distribution:
  - `True`: 371
- Latitude range: 36.880833 to 44.118833
- Longitude range: 139.245333 to 145.738833

These ranges indicate the station table covers a broad northeastern Japan region, extending beyond only the immediate Aomori offshore sequence area.

#### Relevance to the Requested Workflow

This file is not required to compute the core sequence metrics requested by the user, because the mainshock-centered analyses rely primarily on event and mainshock hypocenters. However, it is relevant for future agents that may want to:

- provide network-coverage context for the catalog
- plot station locations with event or mainshock maps
- assess whether the analyzed sequences fall within the denser part of the station footprint
- document the observational context behind relocated hypocenters or mechanism products

Most relevant fields for those purposes are:
- `station_code`
- `latitude`
- `longitude`
- `elevation_m`
- `matched`

#### Relationship to Other Project Files

- Primary event analysis should start from:
  - `catalog/Snet_catalog_relocate_250930_260501.csv`
  - `catalog/main_earthquake.csv`
- Mechanism context comes from:
  - `source_mechanism/Snet_mecha.csv`
- This station file adds observation-network context only; it does not contain event picks, waveforms, or explicit links to catalog rows.

#### Practical Loading Notes

- Despite the `.sta` extension, the file can be loaded directly with `pandas.read_csv()`.
- The schema is simple and consistent enough to treat as a normal CSV table.
- Because all previewed and summarized `matched` values are `True`, future agents may not need to filter on this field unless validating consistency.

Example path:
- `<CASE_ROOT>/data/stations/station.sta`

#### Minimal Operational Description for Future Agents

Use `station.sta` only as supporting network metadata. It is best suited for documenting station distribution and geographic coverage around the M1/M2/M3 study area, not for direct computation of sequence behavior metrics.

------------------------------

