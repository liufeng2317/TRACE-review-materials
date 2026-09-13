# Data Descriptions
## TRACE_ridgecrest_relocated.csv
**Source path**: `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/TRACE_ridgecrest_relocated.csv`
### Summary
The Ridgecrest inputs relevant to the requested workflow consist of a relocated earthquake catalog CSV, a 2-row mainshock CSV, and a surface-fault JSON polyline file stored under the same example data tree. The catalog contains 84,474 fully populated events with UTC timestamps and hypocenter/magnitude fields, while the fault file is a large list of 17,792 longitude-latitude polylines suitable for map overlays and nearest-fault distance calculations.
### Detail
#### Data Sources and Folder Structure
Relevant files are organized under the Ridgecrest example data directory:

- Catalog directory: `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE`
  - `TRACE_ridgecrest_relocated.csv` — relocated earthquake catalog used for time-sliced event mapping and event-wise statistics
  - `main_shock_events.csv` — 2-row reference file containing the Mw 6.4 and Mw 7.1 mainshocks
  - `visualize.ipynb` — notebook present in the folder, but not required for basic loading of the data products above
- Fault directory: `<REPO_ROOT>/examples/ridgecrest/data/faults`
  - `ridgecrest_surface_faults.json` — surface fault traces as polylines

This directory layout is simple: one catalog folder for event tables and one faults folder for map geometry.

#### Catalog File: `TRACE_ridgecrest_relocated.csv`
- Format: CSV
- Size: ~7.4 MB
- Shape: `84474 x 5`
- Columns:
  - `event_time` — timestamp string with timezone offset; successfully parses to UTC datetimes
  - `latitude` — float64
  - `longitude` — float64
  - `depth_km` — float64
  - `magnitude` — float64
- Missing values: none detected in any of the 5 columns

Basic metadata:
- Time range: `2019-07-04 00:56:37.590000+00:00` to `2019-07-25 23:59:29.320000+00:00`
- Latitude range: `35.27090479518505` to `36.311627795185046`
- Longitude range: `-118.06486693463452` to `-116.9939567617556`
- Depth range (km): `0.367625` to `26.3518736`
- Magnitude range: `-0.85` to `7.1`

Example rows follow the naming and typing exactly as expected by the user request, e.g.:
- `2019-07-04 00:56:37.590000+00:00, 36.088524, -117.827908, 9.701632, 0.66`
- `2019-07-04 02:34:31.210000+00:00, 36.118940, -117.642917, 3.793481, 0.43`

Implications for future agents:
- This file is directly usable for temporal filtering, scatter plotting, and computing distances from events to fault polylines.
- `event_time` should be parsed with timezone awareness.
- All required fields for the requested spatiotemporal plots are already present in a single flat table.

#### Mainshock Reference File: `main_shock_events.csv`
- Format: CSV
- Size: 176 bytes
- Shape: `2 x 5`
- Columns match the main catalog exactly:
  - `event_time`
  - `latitude`
  - `longitude`
  - `depth_km`
  - `magnitude`

Contents correspond to the two key anchor events:
- Mw 6.4: `2019-07-04 17:33:49.040000+00:00`, `35.70421`, `-117.49392`, `11.864`, `6.4`
- Mw 7.1: `2019-07-06 03:19:53.040000+00:00`, `35.77623`, `-117.59286`, `1.986`, `7.1`

Implications for future agents:
- This file provides explicit event times and epicenters for defining the analysis windows `[mainshock64, mainshock71]`, stage boundaries, and map annotations.
- Because the schema matches the full catalog, it can be loaded with the same CSV reader logic.

#### Fault Geometry File: `ridgecrest_surface_faults.json`
- Format: JSON
- Size: ~17 MB
- Top-level structure: `list`
- Semantic structure: list of fault polylines, where each polyline is a list of `[longitude, latitude]` coordinate pairs
- Number of polylines: `17792`
- Vertices per polyline:
  - minimum: `2`
  - maximum: `1124`
  - mean: `11.6653`

Spatial bounds of the fault geometry:
- Longitude: `-117.784031723` to `-117.312835696215`
- Latitude: `35.4694304340673` to `35.9385750704832`

Example coordinate pattern from the first polyline:
- `[-117.375788716276, 35.5757345303244]`
- `[-117.37578199924, 35.5757218130113]`
- `[-117.375774406264, 35.5757089536054]`

Implications for future agents:
- The file contains dense segmented surface traces appropriate for overlaying on event maps.
- For nearest-fault distance calculations, agents should treat each top-level element as a separate polyline and compute point-to-segment or point-to-polyline distances from earthquake epicenters.
- Coordinates are geographic lon/lat, so projected-distance calculations may require reprojection or geodesic approximations depending on desired accuracy.

#### File Naming and Access Pattern
Observed naming conventions are descriptive and stable:
- Catalog table: `TRACE_ridgecrest_relocated.csv`
- Mainshock subset/reference: `main_shock_events.csv`
- Fault traces: `ridgecrest_surface_faults.json`

Example load paths:
- `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/TRACE_ridgecrest_relocated.csv`
- `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/main_shock_events.csv`
- `<REPO_ROOT>/examples/ridgecrest/data/faults/ridgecrest_surface_faults.json`

#### Practical Loading Notes for Future Agents
- Use a CSV reader such as pandas `read_csv` for both catalog files.
- Parse `event_time` as timezone-aware UTC datetime values.
- The catalog already includes the fields needed for time slicing, plotting, and event filtering; no join is required except optional use of the mainshock file for reference markers.
- Use Python `json.load` for the fault file; expect a large nested list, so iterative processing may be preferable for memory-aware workflows.
- The event catalog spans a broader region and time range than the fault file bounds, so plotting code should explicitly set map extents when comparing subplots.

------------------------------

## main_shock_events.csv
**Source path**: `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/main_shock_events.csv`
### Summary
This CSV is a small 2-row reference table containing the two Ridgecrest mainshocks used to define the key temporal windows and map annotations in downstream workflows. Its schema matches the full relocated catalog exactly, with UTC event times plus latitude, longitude, depth, and magnitude fields, making it easy to load alongside the catalog without transformation.
### Detail
#### File Overview
- Path: `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/main_shock_events.csv`
- Format: CSV
- Size: 176 bytes
- Shape: `2 x 5`
- Role in workflow: reference event table for defining the Mw 6.4 and Mw 7.1 mainshock times and epicenters

#### Column Structure
The file has the following columns, matching the relocated event catalog schema:

- `event_time` — timestamp string with timezone offset; parses cleanly as UTC datetime
- `latitude` — epicenter latitude, float
- `longitude` — epicenter longitude, float
- `depth_km` — focal depth in kilometers, float
- `magnitude` — event magnitude, float

Observed dtypes on read:
- `event_time`: object/string
- `latitude`: float64
- `longitude`: float64
- `depth_km`: float64
- `magnitude`: float64

#### Contents
This file contains exactly two events:

1. Mw 6.4 mainshock
   - `event_time`: `2019-07-04 17:33:49.040000+00:00`
   - `latitude`: `35.70421`
   - `longitude`: `-117.49392`
   - `depth_km`: `11.864`
   - `magnitude`: `6.4`

2. Mw 7.1 mainshock
   - `event_time`: `2019-07-06 03:19:53.040000+00:00`
   - `latitude`: `35.77623`
   - `longitude`: `-117.59286`
   - `depth_km`: `1.986`
   - `magnitude`: `7.1`

#### Temporal Metadata
- Parsed time values are timezone-aware UTC timestamps.
- Earliest event in file: `2019-07-04 17:33:49.040000+00:00`
- Latest event in file: `2019-07-06 03:19:53.040000+00:00`

These two timestamps are the direct anchors for the requested windows such as:
- `[mainshock64, mainshock71]`
- `[mainshock64, mainshock64 + 4 hours]`
- `[mainshock71, mainshock71 + 2 days]`

#### Data Quality / Completeness
- No missing values were detected in any column.
- The schema is identical to `TRACE_ridgecrest_relocated.csv`, so future agents can reuse the same CSV parsing and datetime handling logic.

#### Example Access Pattern
A future agent can load this file with standard CSV tooling and use it as a compact lookup table for:
- temporal window boundaries
- map markers for the two mainshocks
- labeling/legend metadata

Example neighboring file in the same directory:
- `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/TRACE_ridgecrest_relocated.csv`

#### Practical Notes for Future Agents
- Treat `event_time` as UTC and preserve timezone awareness when comparing against catalog event times.
- Because the file contains only two rows, it is best used as a direct metadata/reference source rather than as a standalone catalog.
- The event order in the file already corresponds to Mw 6.4 first, Mw 7.1 second, but robust code should still identify rows by `magnitude` or parsed timestamp rather than relying only on row order.

------------------------------

## ridgecrest_surface_faults.json
**Source path**: `<REPO_ROOT>/examples/ridgecrest/data/faults/ridgecrest_surface_faults.json`
### Summary
This JSON file stores Ridgecrest surface fault geometry as a large collection of geographic polylines, suitable for map overlays and event-to-fault distance calculations. The file contains 17,792 separate line strings, each encoded as a list of `[longitude, latitude]` coordinate pairs, with spatial coverage focused on the main Ridgecrest fault zone.
### Detail
#### File Overview
- Path: `<REPO_ROOT>/examples/ridgecrest/data/faults/ridgecrest_surface_faults.json`
- Format: JSON
- Size: ~17 MB
- Top-level JSON type: `list`
- Intended use in workflow: plotting fault traces on spatial maps and computing nearest-fault distances from earthquake epicenters

#### Data Structure
The file is organized as:
- a top-level list
- each element of the top-level list is a fault polyline
- each polyline is a list of coordinate pairs
- each coordinate pair is ordered as:
  - `[longitude, latitude]`

In compact schema form:
- `List[List[List[float, float]]]]`

Example beginning of the first polyline:
- `[-117.375788716276, 35.5757345303244]`
- `[-117.37578199924, 35.5757218130113]`
- `[-117.375774406264, 35.5757089536054]`

This is a geometry-only file: there are no feature properties, IDs, timestamps, names, or explicit fault categories attached to the polylines.

#### Geometry Metadata
- Number of fault polylines: `17792`
- Vertices per polyline:
  - minimum: `2`
  - maximum: `1124`
  - mean: `11.6653`

Spatial extent derived from all vertices:
- Longitude range: `-117.784031723` to `-117.312835696215`
- Latitude range: `35.4694304340673` to `35.9385750704832`

These bounds indicate the file is geographically focused on the Ridgecrest rupture/fault-trace region rather than a broad regional tectonic map.

#### Implications for Plotting
For map overlays:
- each top-level list element should be rendered as an independent line string
- coordinates are already in geographic lon/lat form
- no reprojection is strictly required for simple scatter/line overlays if event coordinates are also in lon/lat
- all subplots can share identical spatial extents using either:
  - the fault bounds above, or
  - a joint extent computed from both catalog events and fault traces

Because the file contains many short segments, plotting performance may benefit from batching line collections rather than drawing one segment at a time in pure Python loops.

#### Implications for Distance Computation
For nearest-fault distance workflows:
- each earthquake epicenter can be compared against all polyline segments derived from the coordinate lists
- because the file stores only vertices, distance should be computed to line segments rather than only to vertices if accurate nearest-fault estimates are desired
- coordinates are geographic, so future agents should decide whether to:
  - use a projected coordinate system for planar distance calculations, or
  - use geodesic/approximate spherical methods

The large number of polylines (`17792`) suggests that spatial indexing or chunked/parallel processing may be useful in later analysis stages.

#### Access Pattern
Typical load pattern:
- use Python `json.load(...)`
- expect a nested in-memory list structure
- iterate over top-level elements as separate fault traces

Example neighboring path used with this file:
- Catalog: `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/TRACE_ridgecrest_relocated.csv`
- Mainshocks: `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/main_shock_events.csv`

#### Practical Notes for Future Agents
- Coordinate order is `[longitude, latitude]`, not `[latitude, longitude]`; this is important for both plotting and distance calculations.
- There is no attribute table, so any grouping, ranking, or filtering must be derived from geometry alone.
- The file is substantially larger than the CSV metadata files, so it may dominate I/O and geometry-processing time in downstream tasks.
- Since many polylines are short, agents computing nearest distances should consider converting the nested lists into segment arrays or a spatial index once, then reusing that structure across time-sliced event subsets.

------------------------------

