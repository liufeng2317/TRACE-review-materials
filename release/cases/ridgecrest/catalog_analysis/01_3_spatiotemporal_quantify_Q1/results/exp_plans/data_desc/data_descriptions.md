# Data Descriptions
## TRACE_ridgecrest_relocated.csv
**Source path**: `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/TRACE_ridgecrest_relocated.csv`
### Summary
This Ridgecrest data bundle contains three relevant inputs for spatiotemporal earthquake-sequence analysis: a relocated earthquake catalog CSV, a two-row mainshock reference CSV, and a surface-fault geometry JSON. The catalog has 84,474 events with complete time, latitude, longitude, depth, and magnitude fields spanning 2019-07-04 to 2019-07-25 UTC, while the fault file stores 17,792 polyline segments as lists of [longitude, latitude] coordinates.
### Detail
#### Folder Structure
- Base directory: `<REPO_ROOT>/examples/ridgecrest/data`
- Relevant subdirectories:
  - `catalog_TRACE/`
    - `TRACE_ridgecrest_relocated.csv` — relocated earthquake catalog
    - `main_shock_events.csv` — reference file for Mw 6.4 and Mw 7.1 mainshocks
    - `visualize.ipynb` — notebook present in folder, but not inspected as a primary data source
  - `faults/`
    - `ridgecrest_surface_faults.json` — mapped surface-fault polylines

#### Key Files for Future Agents
1. **Catalog**
   - Path: `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/TRACE_ridgecrest_relocated.csv`
   - Size: ~7.4 MB
   - Format: CSV with header row
   - Shape: `84474 x 5`
   - Columns:
     - `event_time` (`object` in CSV; parse as timezone-aware datetime)
     - `latitude` (`float64`)
     - `longitude` (`float64`)
     - `depth_km` (`float64`)
     - `magnitude` (`float64`)
   - Time span:
     - Min: `2019-07-04 00:56:37.590000+00:00`
     - Max: `2019-07-25 23:59:29.320000+00:00`
   - Missing values:
     - `event_time`: 0 null after datetime coercion
     - `latitude`, `longitude`, `depth_km`, `magnitude`: 0 nulls each
   - Value ranges:
     - `latitude`: 35.27090479518505 to 36.311627795185046
     - `longitude`: -118.06486693463452 to -116.9939567617556
     - `depth_km`: 0.367625 to 26.3518736
     - `magnitude`: -0.85 to 7.1
   - Means:
     - `latitude`: 35.76477956613717
     - `longitude`: -117.57212935260488
     - `depth_km`: 5.525718645130455
     - `magnitude`: 1.0008796942933396
   - Example rows:
     - `2019-07-04 00:56:37.590000+00:00, 36.08852379518505, -117.82790782193672, 9.70163162, 0.66`
     - `2019-07-04 02:34:31.210000+00:00, 36.11893979518505, -117.64291706091387, 3.79348124, 0.43`
     - `2019-07-04 03:20:28.460000+00:00, 36.11053679518505, -117.62022744201748, 2.27652371, 0.88`
   - Usage notes:
     - This file already contains the exact fields needed for time-windowing, epicentral mapping, and pairwise directional calculations.
     - `event_time` strings include UTC offsets (`+00:00`), so agents should parse with timezone support.

2. **Mainshock reference file**
   - Path: `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/main_shock_events.csv`
   - Size: 176 bytes
   - Format: CSV with same schema as the catalog
   - Shape: `2 x 5`
   - Columns:
     - `event_time`, `latitude`, `longitude`, `depth_km`, `magnitude`
   - Rows:
     - Mw 6.4: `2019-07-04 17:33:49.040000+00:00, 35.70421, -117.49392, 11.864, 6.4`
     - Mw 7.1: `2019-07-06 03:19:53.040000+00:00, 35.77623, -117.59286, 1.986, 7.1`
   - Usage notes:
     - This file is suitable for defining the analysis window and for plotting/annotating the two mainshock epicenters and times.
     - It matches the catalog schema, so it can be loaded with the same parser.

3. **Surface fault geometry**
   - Path: `<REPO_ROOT>/examples/ridgecrest/data/faults/ridgecrest_surface_faults.json`
   - Size: ~17 MB
   - Format: JSON
   - Top-level type: `list`
   - Structure: list of polyline segments, where each segment is a list of coordinate pairs in the form `[longitude, latitude]`
   - Number of segments: `17792`
   - Segment length range:
     - Minimum vertices per segment: `2`
     - Maximum vertices per segment: `1124`
   - Total coordinate count across all segments: `207549`
   - Bounding box:
     - Longitude: `-117.784031723` to `-117.312835696215`
     - Latitude: `35.4694304340673` to `35.9385750704832`
   - Sample coordinate pattern:
     - `[-117.375788716276, 35.5757345303244]`
     - `[-117.37578199924, 35.5757218130113]`
     - `[-117.375774406264, 35.5757089536054]`
   - Usage notes:
     - This is not GeoJSON feature metadata; it is a plain nested list, so agents should load it with `json.load()` and iterate directly over segments.
     - Coordinates are already in longitude-latitude order, which is important for map plotting and any conversion to projected coordinates.

#### Organizational Pattern and Access
- The dataset is organized by theme:
  - earthquake catalogs in `catalog_TRACE/`
  - fault traces in `faults/`
- File naming is descriptive rather than heavily encoded:
  - `TRACE_ridgecrest_relocated.csv` indicates the main relocated event catalog
  - `main_shock_events.csv` is a compact reference subset for the two principal events
  - `ridgecrest_surface_faults.json` contains mapped surface-fault traces
- Example load targets:
  - Catalog: `.../catalog_TRACE/TRACE_ridgecrest_relocated.csv`
  - Mainshocks: `.../catalog_TRACE/main_shock_events.csv`
  - Faults: `.../faults/ridgecrest_surface_faults.json`

#### Recommended Parsing Notes for Future Agents
- Parse `event_time` with pandas `to_datetime(..., utc=True)` or equivalent.
- Treat catalog and mainshock CSVs as tabular event records with identical schema.
- Treat the fault JSON as a large collection of polyline segments; if performance matters, iterate lazily or pre-convert to arrays for plotting/spatial indexing.
- No missing values were detected in the inspected numeric and time fields of the catalog, so downstream loading should be straightforward.

------------------------------

## main_shock_events.csv
**Source path**: `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/main_shock_events.csv`
### Summary
This CSV is a compact reference table containing the two key Ridgecrest mainshocks used to anchor analysis windows and annotations: the Mw 6.4 event and the Mw 7.1 event. It has the same 5-column schema as the relocated event catalog, with complete UTC timestamps and hypocenter/epicenter information for both rows.
### Detail
#### File Overview
- Path: `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/main_shock_events.csv`
- Format: CSV with header row
- Size: 176 bytes
- Shape: `2 x 5`
- Purpose-relevant role: reference event table for defining the analysis interval and overlaying the two mainshock markers/timelines on later plots

#### Schema
Columns present in the file:
1. `event_time`
2. `latitude`
3. `longitude`
4. `depth_km`
5. `magnitude`

Observed dtypes when read with pandas:
- `event_time`: `object` in raw CSV; should be parsed as timezone-aware datetime
- `latitude`: `float64`
- `longitude`: `float64`
- `depth_km`: `float64`
- `magnitude`: `float64`

#### Row Contents
The file contains exactly two rows:
- Row 1:
  - `event_time`: `2019-07-04 17:33:49.040000+00:00`
  - `latitude`: `35.70421`
  - `longitude`: `-117.49392`
  - `depth_km`: `11.864`
  - `magnitude`: `6.4`
- Row 2:
  - `event_time`: `2019-07-06 03:19:53.040000+00:00`
  - `latitude`: `35.77623`
  - `longitude`: `-117.59286`
  - `depth_km`: `1.986`
  - `magnitude`: `7.1`

#### Temporal Metadata
- Earliest event in file: `2019-07-04 17:33:49.040000+00:00`
- Latest event in file: `2019-07-06 03:19:53.040000+00:00`
- Time encoding includes explicit UTC offset (`+00:00`)
- This makes the file directly usable for constructing time windows such as:
  - start at Mw 6.4 mainshock time
  - end at Mw 7.1 mainshock time plus any additional offset handled downstream

#### Spatial and Magnitude Metadata
- Latitude range: `35.70421` to `35.77623`
- Longitude range: `-117.59286` to `-117.49392`
- Depth range (km): `1.986` to `11.864`
- Magnitudes present: `6.4`, `7.1`

#### Organizational Notes
- The file lives in `catalog_TRACE/` alongside the larger relocated catalog file:
  - Example sibling path: `.../catalog_TRACE/TRACE_ridgecrest_relocated.csv`
- Naming convention is descriptive and simple:
  - `main_shock_events.csv` = a dedicated reference list of mainshock events

#### Access and Loading Notes for Future Agents
- Load with standard CSV readers (`pandas.read_csv` is sufficient).
- Parse `event_time` with timezone support, e.g. `pd.to_datetime(..., utc=True)`.
- Because the schema matches the relocated catalog, this file can be merged, compared, or used as a direct filter/annotation source without column renaming.
- The file is small enough to inspect entirely in memory and does not require chunked loading.

#### Minimal Example Path Pattern
- `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/main_shock_events.csv`

------------------------------

## ridgecrest_surface_faults.json
**Source path**: `<REPO_ROOT>/examples/ridgecrest/data/faults/ridgecrest_surface_faults.json`
### Summary
This JSON file contains mapped Ridgecrest surface-fault geometry as a plain nested list of polyline segments, not a GeoJSON feature collection. It includes 17,792 segments and 207,549 total coordinate points in `[longitude, latitude]` order, making it suitable for direct map overlay after standard JSON loading.
### Detail
#### File Overview
- Path: `<REPO_ROOT>/examples/ridgecrest/data/faults/ridgecrest_surface_faults.json`
- Format: JSON
- Size: ~17 MB
- Primary role for future agents: background structural geometry for plotting earthquake epicenters relative to mapped surface faults

#### Top-Level Structure
- Top-level JSON type: `list`
- Contents: each top-level element is a fault polyline segment
- Segment representation: each segment is itself a `list` of coordinate pairs
- Coordinate representation: each coordinate pair is a 2-element list in the form:
  - `[longitude, latitude]`

This means the structure is effectively:
- `List[Segment]`
- `Segment = List[[lon, lat]]`

It is **not** a GeoJSON `FeatureCollection`, and there are no inspected per-segment properties, IDs, or metadata fields.

#### Basic Size and Geometry Metadata
- Number of polyline segments: `17792`
- Total coordinate points across all segments: `207549`
- Vertices per segment:
  - Minimum segment length: `2` points
  - Maximum segment length: `1124` points

#### Spatial Extent
Bounding box computed from all coordinates:
- Longitude min: `-117.784031723`
- Longitude max: `-117.312835696215`
- Latitude min: `35.4694304340673`
- Latitude max: `35.9385750704832`

These bounds place the fault traces within the main Ridgecrest study area and make the file directly useful for clipping or setting plotting extents.

#### Sample Structure Preview
Examples from the first few segments show the repeated nested-list pattern:
- Segment example 1:
  - `[-117.375788716276, 35.5757345303244]`
  - `[-117.37578199924, 35.5757218130113]`
  - `[-117.375774406264, 35.5757089536054]`
- Segment example 2:
  - `[-117.375817091685, 35.5756955087408]`
  - `[-117.375811452936, 35.5756885138139]`
  - `[-117.375801799613, 35.5756845343138]`

#### Organizational Notes
- Directory: `.../examples/ridgecrest/data/faults/`
- Naming convention is descriptive:
  - `ridgecrest_surface_faults.json` clearly indicates a Ridgecrest-specific fault-trace dataset
- This file is separate from the catalog files in `catalog_TRACE/`, which implies a clean split between:
  - tabular seismicity inputs
  - line-based structural map inputs

#### Access and Loading Notes for Future Agents
- Load with the Python standard library:
  - `json.load(open(path))`
- Because the file is a large plain nested list, agents should expect to iterate over segments directly rather than extracting `geometry.coordinates` from GeoJSON.
- Preserve coordinate order as `[longitude, latitude]` when plotting.
- If projected distances or spatial indexing are needed later, this file will likely benefit from conversion to arrays or line objects after loading, but no such conversion is required for basic inspection.
- Since the file is moderately large (~17 MB), repeated parsing can be avoided by caching in memory during a session.

#### Practical Interpretation for Data Access
A future agent can treat the file as:
- a collection of polylines for map overlay,
- a source for study-area bounds,
- and a structural reference to compare visually against event epicenters from the earthquake catalog.

#### Example Path
- `<REPO_ROOT>/examples/ridgecrest/data/faults/ridgecrest_surface_faults.json`

------------------------------

