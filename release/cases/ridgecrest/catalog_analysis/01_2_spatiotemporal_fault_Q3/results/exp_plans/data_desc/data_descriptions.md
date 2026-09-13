# Data Descriptions
## TRACE_ridgecrest_relocated.csv
**Source path**: `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/TRACE_ridgecrest_relocated.csv`
### Summary
This Ridgecrest example data directory contains a relocated earthquake catalog CSV, a small CSV with the two key mainshock events, and a large JSON file of mapped surface fault traces. The catalog is already in a simple analysis-ready tabular format with the core fields needed for spatiotemporal selection and mapping: origin time, latitude, longitude, depth, and magnitude.
### Detail
#### Folder Structure
- Base directory: `<REPO_ROOT>/examples/ridgecrest/data`
- Relevant subdirectories:
  - `catalog_TRACE/`
    - `TRACE_ridgecrest_relocated.csv`
    - `main_shock_events.csv`
    - `visualize.ipynb` (not inspected in detail; likely example/utility notebook)
  - `faults/`
    - `ridgecrest_surface_faults.json`

#### Key Files for Future Agents
1. **Relocated earthquake catalog**
   - Path: `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/TRACE_ridgecrest_relocated.csv`
   - Format: CSV
   - Size: `7,662,814` bytes (~7.4 MB)
   - Shape: `84,474 rows x 5 columns`
   - Columns:
     - `event_time` (`object` in CSV; parse as timezone-aware datetime)
     - `latitude` (`float64`)
     - `longitude` (`float64`)
     - `depth_km` (`float64`)
     - `magnitude` (`float64`)
   - Missing values: none detected in any of the 5 columns.
   - Time range:
     - min: `2019-07-04 00:56:37.590000+00:00`
     - max: `2019-07-25 23:59:29.320000+00:00`
   - Spatial/value ranges:
     - latitude: `35.27090479518505` to `36.311627795185046`
     - longitude: `-118.06486693463452` to `-116.9939567617556`
     - depth_km: `0.367625` to `26.3518736`
     - magnitude: `-0.85` to `7.1`
   - Mean values (useful only as rough metadata):
     - latitude mean: `35.76477956613717`
     - longitude mean: `-117.57212935260488`
     - depth mean: `5.525718645130455 km`
     - magnitude mean: `1.0008796942933396`
   - First rows confirm ISO-like UTC timestamps with offsets, e.g. `2019-07-04 00:56:37.590000+00:00`.
   - This is the main event table to filter by time windows and plot seismicity in latitude-longitude space.

2. **Mainshock reference events**
   - Path: `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/main_shock_events.csv`
   - Format: CSV
   - Size: `176` bytes
   - Shape: `2 rows x 5 columns`
   - Columns match the main catalog exactly:
     - `event_time`
     - `latitude`
     - `longitude`
     - `depth_km`
     - `magnitude`
   - Contents:
     - Mw 6.4 event:
       - `event_time`: `2019-07-04 17:33:49.040000+00:00`
       - `latitude`: `35.70421`
       - `longitude`: `-117.49392`
       - `depth_km`: `11.864`
       - `magnitude`: `6.4`
     - Mw 7.1 event:
       - `event_time`: `2019-07-06 03:19:53.040000+00:00`
       - `latitude`: `35.77623`
       - `longitude`: `-117.59286`
       - `depth_km`: `1.986`
       - `magnitude`: `7.1`
   - This file is the cleanest source for defining the inter-mainshock analysis window and plotting the two epicenters consistently.

3. **Surface fault traces**
   - Path: `<REPO_ROOT>/examples/ridgecrest/data/faults/ridgecrest_surface_faults.json`
   - Format: JSON
   - Size: `16,897,768` bytes (~17 MB)
   - Top-level type: `list`
   - Structure: list of fault trace polylines, where each polyline is a list of `[longitude, latitude]` pairs.
   - Top-level segment count: `17,792`
   - Polyline length range:
     - minimum vertices per segment: `2`
     - maximum vertices per segment: `1,124`
   - Total point count across all segments: `207,549`
   - Overall coordinate bounds:
     - longitude: `-117.784031723` to `-117.312835696215`
     - latitude: `35.4694304340673` to `35.9385750704832`
   - Example points from the first segment:
     - `[-117.375788716276, 35.5757345303244]`
     - `[-117.37578199924, 35.5757218130113]`
     - `[-117.375774406264, 35.5757089536054]`
   - Future agents should treat this as many separate line segments rather than a single continuous fault line.

#### File Naming and Organization Patterns
- Catalog files are grouped under `catalog_TRACE/` and use descriptive CSV filenames.
- The relocated event catalog and the mainshock file share the same schema, which simplifies loading and overlaying.
- Fault geometry is separated into `faults/` and stored as JSON coordinate arrays in `[lon, lat]` order.

#### Metadata Relevant to Spatiotemporal Workflows
- All priority files are lightweight to moderate size and can be loaded directly with `pandas` (CSVs) and `json`/`orjson` (fault file).
- `event_time` should be parsed to timezone-aware UTC datetimes before any windowing.
- Spatial plotting should respect coordinate order differences:
  - catalog/mainshock tables: columns are `latitude`, `longitude`
  - fault JSON points: stored as `[longitude, latitude]`
- The catalog and mainshock files already contain the minimum fields needed for time binning, KDE gridding, convex hull/alpha-shape inputs, and epicenter overlays.

#### Minimal Loading Notes
- CSV loading example pattern:
  - read with `pandas.read_csv(...)`
  - parse `event_time` with `pd.to_datetime(..., utc=True)`
- Fault JSON loading example pattern:
  - `segments = json.load(open(...))`
  - each `segments[i]` is a polyline list of `[lon, lat]`
- Example source paths:
  - `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/TRACE_ridgecrest_relocated.csv`
  - `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/main_shock_events.csv`
  - `<REPO_ROOT>/examples/ridgecrest/data/faults/ridgecrest_surface_faults.json`

------------------------------

## main_shock_events.csv
**Source path**: `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/main_shock_events.csv`
### Summary
This CSV is a compact reference table containing the two Ridgecrest mainshock events used to define the inter-mainshock analysis window and epicenter overlays. It shares the same five-column schema as the relocated event catalog, making it straightforward to join or compare with the larger seismicity table.
### Detail
#### File Overview
- Path: `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/main_shock_events.csv`
- Format: CSV
- Size: `176` bytes
- Shape: `2 rows x 5 columns`
- Header row present: yes

#### Schema
Columns in file order:
1. `event_time`
2. `latitude`
3. `longitude`
4. `depth_km`
5. `magnitude`

Detected data types when read with pandas:
- `event_time`: `object` in CSV; should be parsed to timezone-aware datetime
- `latitude`: `float64`
- `longitude`: `float64`
- `depth_km`: `float64`
- `magnitude`: `float64`

#### Row Contents
This file contains exactly two events:
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

#### Interpretation for Future Agents
- The two rows correspond to the Mw 6.4 and Mw 7.1 mainshocks referenced in the request.
- These records are suitable for:
  - defining the analysis time window `[mainshock64, mainshock71]`
  - constructing relative-time bins from the Mw 6.4 origin time
  - plotting fixed epicenter markers on maps
- Because the schema matches the main relocated catalog (`event_time, latitude, longitude, depth_km, magnitude`), this file can be loaded with the same parsing logic as the larger catalog.

#### Time and Coordinate Notes
- `event_time` strings include explicit UTC offsets (`+00:00`), so parse with UTC-aware datetime handling.
- Coordinates are stored as separate columns in standard tabular form:
  - `latitude` in degrees north
  - `longitude` in degrees east/west (negative here for west)
- For map overlays with the fault JSON, note the ordering difference:
  - this CSV uses separate `latitude` and `longitude` columns
  - the fault JSON stores each point as `[longitude, latitude]`

#### Access Pattern
- Example load approach:
  - `pandas.read_csv(...)`
  - then `pd.to_datetime(df['event_time'], utc=True)`
- Example source path:
  - `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/main_shock_events.csv`

#### Nearby Related Files
Located in the same directory:
- `TRACE_ridgecrest_relocated.csv` — larger relocated event catalog with the same schema
- `visualize.ipynb` — likely an auxiliary notebook, not required for loading this CSV

------------------------------

## ridgecrest_surface_faults.json
**Source path**: `<REPO_ROOT>/examples/ridgecrest/data/faults/ridgecrest_surface_faults.json`
### Summary
This JSON file stores Ridgecrest surface fault geometry as many separate polyline segments, each represented by lists of `[longitude, latitude]` coordinate pairs. It is a large but straightforward overlay dataset suitable for plotting fault traces together with the earthquake catalog and mainshock epicenters.
### Detail
#### File Overview
- Path: `<REPO_ROOT>/examples/ridgecrest/data/faults/ridgecrest_surface_faults.json`
- Format: JSON
- Size: `16,897,768` bytes (~17 MB)
- Top-level JSON type: `list`

#### Data Structure
- The file is a **list of fault trace segments**.
- Each top-level element is itself a `list` representing one polyline segment.
- Each polyline segment contains coordinate pairs in the form:
  - `[longitude, latitude]`
- Coordinate ordering is important:
  - first value = longitude
  - second value = latitude

In pseudostructure form:
- `segments = [segment_1, segment_2, ..., segment_N]`
- `segment_i = [[lon1, lat1], [lon2, lat2], ...]`

#### Basic Metadata
- Number of top-level segments: `17,792`
- Total coordinate points across all segments: `207,549`
- Segment length statistics:
  - minimum vertices per segment: `2`
  - maximum vertices per segment: `1,124`
- Overall spatial extent:
  - longitude min: `-117.784031723`
  - longitude max: `-117.312835696215`
  - latitude min: `35.4694304340673`
  - latitude max: `35.9385750704832`

#### Example Content
First non-empty segment begins with points like:
- `[-117.375788716276, 35.5757345303244]`
- `[-117.37578199924, 35.5757218130113]`
- `[-117.375774406264, 35.5757089536054]`

This confirms the geometry is stored as dense vertex sequences rather than as named fault objects with attributes.

#### Implications for Future Agents
- Treat this as a pure geometry file with **no per-segment metadata fields** such as fault name, style, hierarchy, or identifiers.
- For map overlays, loop over segments and plot each one independently as a line or a collection of points.
- Because the file contains many short and long segments, it is better handled as segmented polylines rather than concatenated into one path.
- The coordinate range is narrower than the full relocated catalog extent, so agents may want to choose plotting extents based on the union of catalog and fault bounds if both are shown together.

#### Coordinate Convention Notes
- This file uses `[lon, lat]` ordering.
- This differs from the earthquake CSV schema, which stores `latitude` and `longitude` as separate columns.
- When merging or plotting with seismicity data, future agents should explicitly map:
  - fault point x = longitude
  - fault point y = latitude

#### Suitable Uses
This file is directly relevant for:
- top-level fault overlays on KDE maps
- top-level fault overlays on hotspot migration plots
- top-level fault overlays on convex hull and alpha-shape boundary plots
- defining a visual structural context for the inter-mainshock seismicity evolution

#### Loading Notes
- Recommended loading pattern:
  - `import json`
  - `segments = json.load(open(path))`
- Expected object after loading:
  - Python `list` of `list` of 2-element numeric coordinate lists
- Because the file is moderately large (~17 MB), it is still practical to load fully into memory in standard Python workflows.

#### Related Paths
- Fault file:
  - `<REPO_ROOT>/examples/ridgecrest/data/faults/ridgecrest_surface_faults.json`
- Nearby analysis-relevant files:
  - `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/TRACE_ridgecrest_relocated.csv`
  - `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/main_shock_events.csv`

------------------------------

