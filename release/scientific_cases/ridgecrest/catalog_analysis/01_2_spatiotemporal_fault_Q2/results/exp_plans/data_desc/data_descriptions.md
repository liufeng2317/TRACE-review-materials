# Data Descriptions
## TRACE_ridgecrest_relocated.csv
**Source path**: `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/TRACE_ridgecrest_relocated.csv`
### Summary
The Ridgecrest example data relevant to the requested onset/activation workflow consists of a relocated earthquake catalog CSV, a two-row mainshock reference CSV, and a surface-fault JSON polyline file. The catalog has 84,474 events with complete time/latitude/longitude/depth/magnitude fields, while the fault file contains 17,792 polylines represented as lists of [longitude, latitude] coordinates suitable for gridding, nearest-fault association, and fault-segment discretization.
### Detail
#### Relevant Data Sources

The user-prioritized files for future analysis are:

- **Relocated catalog:** `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/TRACE_ridgecrest_relocated.csv`
- **Mainshock reference events:** `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/main_shock_events.csv`
- **Mapped surface faults:** `<REPO_ROOT>/examples/ridgecrest/data/faults/ridgecrest_surface_faults.json`

A notebook `visualize.ipynb` is also present in `catalog_TRACE/`, but it was not inspected as a primary data source.

#### Folder Structure

Relevant directory layout:

- `.../data/catalog_TRACE/`
  - `TRACE_ridgecrest_relocated.csv`
  - `main_shock_events.csv`
  - `visualize.ipynb`
- `.../data/faults/`
  - `ridgecrest_surface_faults.json`

This organization cleanly separates earthquake tables from mapped fault geometry. Future agents can load the two CSVs with `pandas.read_csv(...)` and the fault file with `json.load(...)`.

#### Catalog File: `TRACE_ridgecrest_relocated.csv`

**Format:** CSV  
**Size:** ~7.4 MB  
**Shape:** 84,474 rows × 5 columns

**Columns**
- `event_time` — string-like timestamp; examples include timezone-aware UTC strings such as `2019-07-04 00:56:37.590000+00:00`
- `latitude` — float64
- `longitude` — float64
- `depth_km` — float64
- `magnitude` — float64

**Null / completeness**
- No missing values were found in any of the five columns.

**Time coverage**
- Earliest event: `2019-07-04 00:56:37.590000+00:00`
- Latest event: `2019-07-25 23:59:29.320000+00:00`

**Spatial / value ranges**
- Latitude: 35.27090479518505 to 36.311627795185046
- Longitude: -118.06486693463452 to -116.9939567617556
- Depth: 0.367625 to 26.3518736 km
- Magnitude: -0.85 to 7.1

**Example records**
- `2019-07-04 00:56:37.590000+00:00, 36.08852379518505, -117.82790782193672, 9.70163162, 0.66`
- `2019-07-04 02:34:31.210000+00:00, 36.11893979518505, -117.64291706091387, 3.79348124, 0.43`
- `2019-07-04 03:20:28.460000+00:00, 36.11053679518505, -117.62022744201748, 2.27652371, 0.88`

**Usefulness for future agents**
- This file already contains the exact fields needed for time-window selection, gridding, seismicity-rate binning, and epicentral overlays.
- `event_time` should be parsed with `pandas.to_datetime(..., utc=True or equivalent)` before computing times relative to the Mw 6.4 event.
- Latitude/longitude are event hypocenter coordinates for map-based analyses; `depth_km` is available if later filtering by depth is needed.

#### Mainshock Reference File: `main_shock_events.csv`

**Format:** CSV  
**Size:** 176 bytes  
**Shape:** 2 rows × 5 columns

**Columns**
- `event_time`
- `latitude`
- `longitude`
- `depth_km`
- `magnitude`

The schema matches the relocated catalog, which makes it straightforward to merge or compare without renaming fields.

**Contents**
- Mw 6.4 event: `2019-07-04 17:33:49.040000+00:00`, lat `35.70421`, lon `-117.49392`, depth `11.864`, mag `6.4`
- Mw 7.1 event: `2019-07-06 03:19:53.040000+00:00`, lat `35.77623`, lon `-117.59286`, depth `1.986`, mag `7.1`

**Usefulness for future agents**
- This file provides the explicit start and end times for the requested analysis window `[mainshock64, mainshock71]`.
- It also provides the two epicenters needed for overlay on spatial maps and fault-segment activation plots.

#### Fault Geometry File: `ridgecrest_surface_faults.json`

**Format:** JSON  
**Size:** ~17 MB  
**Top-level type:** list  
**Number of polylines:** 17,792

**Geometry structure**
- The file is a **list of polylines**.
- Each polyline is a **list of points**.
- Each point is a 2-element list in the order:
  - `[longitude, latitude]`

**Observed polyline complexity**
- Minimum points per polyline: 2
- Maximum points per polyline: 1124
- Median points per polyline: 4

**Example geometry snippet**
- First polyline begins like:
  - `[[-117.375788716276, 35.5757345303244], [-117.37578199924, 35.5757218130113], ...]`

**Overall coordinate extent**
- Longitude: -117.784031723 to -117.312835696215
- Latitude: 35.4694304340673 to 35.9385750704832

**Usefulness for future agents**
- This geometry is directly compatible with fault discretization into fixed-length segments.
- Because the file stores many short polylines (median length 4 vertices), future segmentation code should not assume every feature is long enough for 1 km subdivision.
- The coordinate order is longitude-first, latitude-second; downstream geodesic or projected-distance calculations should preserve this ordering.

#### Naming and Access Conventions

- Catalog files use descriptive CSV filenames under `catalog_TRACE/`.
- Fault geometry is stored as a single JSON file under `faults/`.
- No nested event subdirectories or partitioned shards were observed for these key inputs; agents can load each file directly from its absolute path.

#### Practical Notes for Loading

- **CSV loading:** `pandas.read_csv(...)`
- **Time parsing:** `pd.to_datetime(df['event_time'], errors='coerce')`
- **Fault JSON loading:** `json.load(open(path))`
- **Geometry interpretation:** each polyline is a coordinate sequence, not a GeoJSON FeatureCollection
- **Distance work:** fault/event association and 1 km segmentation will require projected or geodesic distance calculations, since source coordinates are geographic (lon/lat)

#### Recommended Inputs for the Requested Workflow

For the user’s future spatiotemporal activation workflow, the core fields to rely on are:

- From the relocated catalog:
  - `event_time`
  - `latitude`
  - `longitude`
  - `depth_km`
  - `magnitude`
- From the mainshock file:
  - the two rows defining Mw 6.4 and Mw 7.1 origin times and epicenters
- From the fault JSON:
  - polyline coordinate sequences `[longitude, latitude]`

These inputs are sufficient for time-window filtering, spatial extent definition, 1 km grid construction, 30-minute event counting, nearest-fault assignment, and later segment-level activation analyses.

------------------------------

## main_shock_events.csv
**Source path**: `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/main_shock_events.csv`
### Summary
This CSV is a small reference table containing the two Ridgecrest mainshock events used to define the analysis time window and epicentral overlays. It has 2 rows and 5 columns with the same schema as the relocated catalog: event_time, latitude, longitude, depth_km, and magnitude.
### Detail
#### File Overview

- **Path:** `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/main_shock_events.csv`
- **Format:** CSV
- **Size:** 176 bytes
- **Shape:** 2 rows × 5 columns

This file is a compact event reference table for the two mainshocks mentioned in the workflow: Mw 6.4 and Mw 7.1. It is directly usable for defining the requested time window `[mainshock64, mainshock71]` and for plotting the two epicenters on maps.

#### Column Schema

Columns present in the header row:

- `event_time` — timestamp string
- `latitude` — float64
- `longitude` — float64
- `depth_km` — float64
- `magnitude` — float64

The schema matches the main relocated event catalog, so future agents can load both files consistently without column renaming.

#### Content Summary

The file contains exactly two events:

1. **Mw 6.4 mainshock**
   - `event_time`: `2019-07-04 17:33:49.040000+00:00`
   - `latitude`: `35.70421`
   - `longitude`: `-117.49392`
   - `depth_km`: `11.864`
   - `magnitude`: `6.4`

2. **Mw 7.1 mainshock**
   - `event_time`: `2019-07-06 03:19:53.040000+00:00`
   - `latitude`: `35.77623`
   - `longitude`: `-117.59286`
   - `depth_km`: `1.986`
   - `magnitude`: `7.1`

#### Data Types and Parsing Notes

- `event_time` is stored as a string but uses timezone-aware UTC formatting, e.g. `YYYY-MM-DD HH:MM:SS.ssssss+00:00`.
- The remaining four columns are numeric and were read as floating-point values.
- Future agents should parse time using `pandas.to_datetime(...)` before computing time differences relative to the Mw 6.4 event.

#### Relevance to the Requested Workflow

This file provides the key metadata needed for later analysis steps:

- **Time-window definition:** use the Mw 6.4 origin time as the start and the Mw 7.1 origin time as the end.
- **Epicenter overlays:** use the latitude/longitude pairs for map annotation.
- **Reference magnitudes/depths:** available if later filtering, labeling, or legend text requires them.

#### Example Access Pattern

Typical load pattern for future agents:

- `pandas.read_csv('<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/main_shock_events.csv')`

After loading, agents can identify the two rows by `magnitude` or row order, since the file contains only the two mainshock entries.

------------------------------

## ridgecrest_surface_faults.json
**Source path**: `<REPO_ROOT>/examples/ridgecrest/data/faults/ridgecrest_surface_faults.json`
### Summary
This JSON file stores mapped Ridgecrest surface faults as a top-level list of 17,792 polylines, where each polyline is a list of [longitude, latitude] coordinate pairs. It is the key geometric input for defining the study region, discretizing faults into ~1 km segments, computing strike/orientation, and associating earthquakes to their nearest mapped fault segment.
### Detail
#### File Overview

- **Path:** `<REPO_ROOT>/examples/ridgecrest/data/faults/ridgecrest_surface_faults.json`
- **Format:** JSON
- **Size:** ~17 MB
- **Top-level structure:** `list`
- **Number of polylines:** 17,792

This file contains mapped surface-fault geometry in a lightweight coordinate-only representation rather than GeoJSON features. Future agents should treat it as a collection of independent polylines for segmentation, strike estimation, and nearest-fault distance calculations.

#### Geometry Structure

The JSON structure is:

- top level: **list of polylines**
- each polyline: **list of points**
- each point: **2-element list** in the order:
  - `[longitude, latitude]`

So the nesting pattern is effectively:

- `List[List[List[float, float]]]]`

There are no inspected feature properties, IDs, names, or explicit attributes attached to the polylines in this file; any `line_id` / `segment_id` needed downstream will need to be generated programmatically.

#### Polyline Complexity Statistics

Observed point-count distribution across polylines:

- **Minimum points per polyline:** 2
- **Maximum points per polyline:** 1124
- **Median points per polyline:** 4

This indicates many short traces and some much longer, more detailed traces. For the requested workflow, future agents should not assume all lines are long enough for repeated 1 km segmentation; very short polylines may need to be kept as single segments between endpoints.

#### Coordinate Extent

Overall bounding ranges across all points in the file:

- **Longitude:** -117.784031723 to -117.312835696215
- **Latitude:** 35.4694304340673 to 35.9385750704832

These extents are directly useful for defining the study region from fault distribution before applying the requested 5 km expansion.

#### Example Content Pattern

Representative leading coordinates from the first polyline:

- `[-117.375788716276, 35.5757345303244]`
- `[-117.37578199924, 35.5757218130113]`
- `[-117.375774406264, 35.5757089536054]`
- `[-117.375770692064, 35.575701521608]`

A second polyline starts similarly as another coordinate sequence, confirming the file is organized as many separate fault traces rather than one continuous network object.

#### Relevance to the Requested Workflow

This file provides the core spatial geometry needed for later steps:

- **Study region definition:** use the fault-coordinate bounds, then enlarge by 5 km in all directions.
- **Fault segmentation:** discretize each polyline into contiguous fixed-arclength segments (e.g., 1 km).
- **Strike estimation:** compute local or segment-level azimuth from successive coordinates.
- **Earthquake-to-fault association:** compute event-to-segment minimum distance using these line geometries.
- **Fault-based maps:** plot original traces or derived segments and color by activation timing.

#### Important Parsing and Geometric Notes

- Coordinate order is **longitude first, latitude second**.
- Coordinates are geographic, not projected; future agents should use geodesic or locally projected distances for:
  - 1 km segmentation
  - 3 km event-to-fault thresholding
  - strike/orientation calculations
  - 5 km spatial buffer expansion
- Because the file is not a formal GIS feature table, downstream code will likely need to build its own structures such as:
  - `line_id`
  - `vertex_index`
  - `segment_id`
  - segment length
  - segment strike

#### Access Pattern

Typical loading pattern:

- `json.load(open('<REPO_ROOT>/examples/ridgecrest/data/faults/ridgecrest_surface_faults.json'))`

After loading, a future agent can iterate over each polyline as a simple list of `[lon, lat]` points.

#### Practical Considerations for Future Agents

Given the large number of polylines (17,792), this file is suitable for parallel preprocessing when building a fault backbone or segment library. The combination of many short traces and some long traces suggests that robust preprocessing should handle both trivial two-point lines and highly detailed multi-vertex polylines without assuming uniform spacing or topology.

------------------------------

