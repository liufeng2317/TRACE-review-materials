# Data Descriptions
## TRACE_ridgecrest_relocated.csv
**Source path**: `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/TRACE_ridgecrest_relocated.csv`
### Summary
The Ridgecrest TRACE relocated catalog is a single CSV table with 84,474 events and 5 core fields needed for spatiotemporal seismicity analysis: event time, latitude, longitude, depth, and magnitude. Companion files in the same data area provide the two mainshock hypocenters in the same schema and mapped surface-fault traces as JSON polylines, which are sufficient for future agents to build the fixed corridors, local metric projections, time windows, and region masks described in the task.
### Detail
#### Data Source Overview
The user-prioritized data relevant to future analysis are organized under:

- `.../data/catalog_TRACE/TRACE_ridgecrest_relocated.csv` — relocated earthquake catalog
- `.../data/catalog_TRACE/main_shock_events.csv` — two reference mainshocks (Mw 6.4 and Mw 7.1)
- `.../data/faults/ridgecrest_surface_faults.json` — mapped surface-fault traces as coordinate polylines

Sibling files/directories also exist, but the three paths above are the primary inputs for catalog filtering, corridor assignment, plotting, and time-window definition.

#### Folder Structure
Relevant directory pattern:

- `.../data/`
  - `catalog_TRACE/`
    - `TRACE_ridgecrest_relocated.csv`
    - `main_shock_events.csv`
    - `visualize.ipynb`
  - `faults/`
    - `ridgecrest_surface_faults.json`
    - `ridgecrest_axis_event_assignment.csv`
    - `ridgecrest_recommended_corridors.csv`
    - `ridgecrest_fault_segment_samples.csv`
    - `ridgecrest_fault_axis_diagnostics.png`
    - `analyze_ridgecrest_fault_axes.py`

This indicates a simple organization: catalogs are in `catalog_TRACE`, and geometric/fault-context resources are in `faults`.

#### Catalog File: `TRACE_ridgecrest_relocated.csv`
Format: CSV with header row.

Shape and completeness:

- Rows: `84,474` events
- Columns: `5`
- Missing values: none detected in any of the 5 columns

Columns:

1. `event_time` — timestamp string with UTC offset included
2. `latitude` — decimal degrees
3. `longitude` — decimal degrees
4. `depth_km` — focal depth in kilometers
5. `magnitude` — event magnitude

Observed dtypes on read:

- `event_time`: string/object on raw CSV load; should be parsed to timezone-aware datetime
- `latitude`, `longitude`, `depth_km`, `magnitude`: float64

Time coverage:

- Earliest event: `2019-07-04 00:56:37.590000+00:00`
- Latest event: `2019-07-25 23:59:29.320000+00:00`

Spatial and value ranges:

- Latitude: `35.27090479518505` to `36.311627795185046`
- Longitude: `-118.06486693463452` to `-116.9939567617556`
- Depth (km): `0.367625` to `26.3518736`
- Magnitude: `-0.85` to `7.1`

Example records:

- `2019-07-04 00:56:37.590000+00:00, 36.08852379518505, -117.82790782193673, 9.70163162, 0.66`
- `2019-07-04 02:34:31.210000+00:00, 36.11893979518505, -117.64291706091389, 3.79348124, 0.43`

Practical loading notes for future agents:

- Parse `event_time` with timezone preservation.
- The file already contains the fields needed for event-count rates, energy proxies derived from magnitude, spatial corridor membership, grid-cell assignment, cumulative counts, and first-activation timing.
- Because the user-defined analysis window ends at the Mw 7.1 mainshock, future code should subset this catalog from catalog start through the Mw 7.1 event time using `main_shock_events.csv`.

#### Mainshock Reference File: `main_shock_events.csv`
Format: CSV with the same schema as the full catalog.

Shape:

- Rows: `2`
- Columns: `5`

Columns:

- `event_time`, `latitude`, `longitude`, `depth_km`, `magnitude`

Contents:

- Mw 6.4 event:
  - Time: `2019-07-04 17:33:49.040000+00:00`
  - Lat/Lon: `(35.70421, -117.49392)`
  - Depth: `11.864 km`
  - Magnitude: `6.4`
- Mw 7.1 event:
  - Time: `2019-07-06 03:19:53.040000+00:00`
  - Lat/Lon: `(35.77623, -117.59286)`
  - Depth: `1.986 km`
  - Magnitude: `7.1`

Usefulness for future agents:

- Provides authoritative timestamps for the two vertical reference lines in time-series plots.
- Provides epicenters needed for constructing the user-requested near-mainshock circular domains after projection to a local metric system.
- Can be loaded with identical parsing logic as the main catalog.

#### Fault Geometry File: `ridgecrest_surface_faults.json`
Format: JSON list of polyline traces.

Top-level structure:

- JSON type: `list`
- Number of traces: `17,792`
- Each trace is itself a list of coordinate pairs in the form `[longitude, latitude]`

Observed geometry characteristics:

- Minimum vertices per trace: `2`
- Maximum vertices per trace: `1124`
- Overall longitude range across all trace vertices: `-117.784031723` to `-117.312835696215`
- Overall latitude range across all trace vertices: `35.4694304340673` to `35.9385750704832`

Example first trace vertices:

- `[-117.375788716276, 35.5757345303244]`
- `[-117.37578199924, 35.5757218130113]`
- `[-117.375774406264, 35.5757089536054]`

Usefulness for future agents:

- Suitable for map overlays in lon/lat directly.
- Can be projected to local metric coordinates for corridor diagnostics and activation maps.
- The file appears to store many small to moderate polylines rather than a single merged fault object, so plotting code should iterate over a list of traces.

#### Naming and Organizational Conventions
- Catalog files use descriptive CSV names and share a consistent column schema.
- Fault geometry is stored separately as a pure coordinate JSON file rather than a GIS shapefile or GeoJSON feature collection.
- The presence of files such as `ridgecrest_recommended_corridors.csv` and `ridgecrest_axis_event_assignment.csv` suggests prior corridor-related work exists, but these were not required for this inspection and should be treated as optional context rather than authoritative replacements for the user-specified fixed corridor definitions.

#### Metadata Relevant to the Requested Future Workflow
For the planned corridor- and time-based analysis, the inspected files support the following directly:

- Time-window definition:
  - catalog start from `TRACE_ridgecrest_relocated.csv`
  - Mw 7.1 cutoff from `main_shock_events.csv`
- Spatial assignment inputs:
  - event epicenters from the catalog
  - mainshock epicenters from `main_shock_events.csv`
  - mapped fault overlays from `ridgecrest_surface_faults.json`
- Variables available for downstream profiling/analysis:
  - event occurrence time
  - horizontal location
  - depth
  - magnitude

Additional implementation notes:

- Event times are stored as strings in the CSV and should be converted explicitly to datetime.
- Longitudes are negative western hemisphere values; lat/lon precision is high enough for projection and kilometer-scale corridor assignment.
- Magnitudes include negative values and extend through the Mw 7.1 mainshock, so any energy-release proxy should be computed carefully after filtering to the intended time window.

#### Quick Access Examples
Relevant input paths:

- Catalog: `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/TRACE_ridgecrest_relocated.csv`
- Mainshocks: `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/main_shock_events.csv`
- Fault traces: `<REPO_ROOT>/examples/ridgecrest/data/faults/ridgecrest_surface_faults.json`

#### Minimal Load Expectations
A future agent can expect:

- one flat event catalog table with `84,474` rows
- one 2-row mainshock reference table with the same columns
- one fault-trace JSON containing many polyline segments encoded as `[lon, lat]` lists

These inputs are sufficient to build user-defined fixed corridors, circle-based diagnostic domains, time-binned seismicity summaries, and map overlays without requiring additional mandatory metadata files.

------------------------------

## main_shock_events.csv
**Source path**: `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/main_shock_events.csv`
### Summary
This CSV is a compact 2-row reference table containing the two Ridgecrest mainshocks used to define the key temporal boundaries and near-mainshock diagnostic domains. It uses the same 5-column schema as the full relocated catalog, making it straightforward for future agents to load both files with identical parsing logic and join them into region-definition workflows.
### Detail
#### Data Source Overview
`main_shock_events.csv` is the mainshock reference file for the Ridgecrest sequence. It contains exactly two events—the Mw 6.4 and Mw 7.1 mainshocks—with event time, hypocentral location, and magnitude fields needed for time-window truncation, epicenter-based neighborhood construction, and map/time-series annotation.

#### File Format and Schema
Format: CSV with a header row.

Columns:

1. `event_time` — event origin time as a timestamp string with UTC offset
2. `latitude` — decimal degrees
3. `longitude` — decimal degrees
4. `depth_km` — focal depth in kilometers
5. `magnitude` — event magnitude

Observed dtypes when read directly from CSV:

- `event_time`: string/object until explicitly parsed as datetime
- `latitude`: float64
- `longitude`: float64
- `depth_km`: float64
- `magnitude`: float64

Missingness:

- No missing values detected in any column

#### File Size and Row Count
- Rows: `2`
- Columns: `5`
- Header present: yes

This is a lookup/reference table rather than a time series or full event catalog.

#### Contents
The file contains these two events:

- Mw 6.4 mainshock:
  - `event_time`: `2019-07-04 17:33:49.040000+00:00`
  - `latitude`: `35.70421`
  - `longitude`: `-117.49392`
  - `depth_km`: `11.864`
  - `magnitude`: `6.4`

- Mw 7.1 mainshock:
  - `event_time`: `2019-07-06 03:19:53.040000+00:00`
  - `latitude`: `35.77623`
  - `longitude`: `-117.59286`
  - `depth_km`: `1.986`
  - `magnitude`: `7.1`

#### Relevance to the Requested Workflow
This file provides the key metadata needed by future agents for:

- defining the analysis end time at the Mw 7.1 occurrence
- marking the Mw 6.4 and Mw 7.1 vertical reference lines on time-series plots
- defining circular diagnostic neighborhoods centered on each mainshock epicenter after projection to a local metric coordinate system
- labeling the two mainshocks on corridor, activation, and fault-overlay maps
- calculating time since Mw 6.4 for event coloring and activation-time diagnostics

#### Relationship to Other Inputs
This file matches the schema of:

- `.../catalog_TRACE/TRACE_ridgecrest_relocated.csv`

That consistency allows future agents to:

- parse both files using the same loader
- compare mainshock rows against catalog rows if desired
- use the mainshock table as a trusted source of reference times and epicenters without needing extra field mapping

#### Practical Loading Notes
- Parse `event_time` as timezone-aware datetime; timestamps already include `+00:00`.
- Use epicentral `latitude`/`longitude` for the user-specified circular domains; `depth_km` is present but not required for horizontal 10 km neighborhood masks.
- Because the file has only two rows, future code should not assume any special identifier column exists; event identification will likely rely on the `magnitude` values (`6.4`, `7.1`) or explicit row selection after load.

#### Example Path
- `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/main_shock_events.csv`

#### Minimal Access Pattern for Future Agents
Future agents can expect a small reference CSV with:

- one row for the Mw 6.4 event
- one row for the Mw 7.1 event
- complete values for origin time, epicenter, depth, and magnitude

This makes it a stable metadata source for defining analysis windows and epicenter-centered diagnostic regions.

------------------------------

## ridgecrest_surface_faults.json
**Source path**: `<REPO_ROOT>/examples/ridgecrest/data/faults/ridgecrest_surface_faults.json`
### Summary
This file is a JSON collection of mapped Ridgecrest-area surface-fault traces stored as many polylines, each represented by ordered `[longitude, latitude]` coordinate pairs. It is suitable for geographic or projected map overlays and provides the structural context needed for future agents to visualize the user-defined corridors, mainshocks, and seismicity assignments without containing event-level seismicity data itself.
### Detail
#### Data Source Overview
`ridgecrest_surface_faults.json` is a geometry-only fault-trace file intended for plotting and spatial context. It does not contain event times, magnitudes, or attributes; instead, it stores many fault polylines as nested coordinate lists that can be overlaid on catalog maps and projected into a local metric coordinate system for corridor diagnostics.

#### File Format and Top-Level Structure
Format: JSON

Top-level object:

- Type: `list`
- Interpretation: collection of independent fault traces / polylines

Element structure:

- Each top-level element is a `list` of vertices
- Each vertex is a 2-element coordinate pair in the form:
  - `[longitude, latitude]`

This is a raw coordinate-list structure, not a GeoJSON `FeatureCollection` and not a shapefile-derived attribute table.

#### Geometry Inventory
Observed metadata from inspection:

- Number of fault traces: `17,792`
- Minimum number of vertices in a trace: `2`
- Maximum number of vertices in a trace: `1124`

This indicates the file contains many separate line segments, ranging from very short traces to long, densely sampled polylines.

#### Coordinate Domain
All coordinates are geographic lon/lat values.

Observed bounds across all vertices:

- Longitude range: `-117.784031723` to `-117.312835696215`
- Latitude range: `35.4694304340673` to `35.9385750704832`

These bounds cover the core Ridgecrest fault zone and are spatially compatible with the user-specified Region A and Region B corridor definitions and the mainshock epicenters in the companion CSV files.

#### Example Internal Structure
Representative structure of the first trace:

- `[[ -117.375788716276, 35.5757345303244 ],`
- ` [ -117.37578199924, 35.5757218130113 ],`
- ` [ -117.375774406264, 35.5757089536054 ], ... ]`

This shows that vertices are ordered along each trace and can be drawn directly as connected line segments.

#### Relevance to the Requested Workflow
This file is relevant to future agents for:

- overlaying mapped surface faults on seismicity maps
- visually checking whether user-defined fixed corridors align with known surface structures
- plotting fault traces together with Region A and Region B centerlines and corridor boundaries
- displaying the Mw 6.4 and Mw 7.1 epicenters relative to mapped fault geometry
- supporting projected local-coordinate plotting after conversion from lon/lat to a metric system

It is especially useful for the requested diagnostic figures such as:

- fixed-corridor assignment maps
- unassigned-event maps
- cumulative count maps with corridor outlines
- first-activation maps with centerlines and fault context

#### What the File Does Not Contain
Future agents should not expect any of the following in this JSON:

- event timestamps
- event magnitudes
- event depths
- fault names or segment identifiers
- explicit CRS metadata
- GeoJSON-style properties/attributes

Because there is no embedded projection metadata, future code should assume the coordinates are lon/lat in decimal degrees and apply an appropriate local projection explicitly when metric distances are needed.

#### Relationship to Other Inputs
This geometry file complements:

- `.../catalog_TRACE/TRACE_ridgecrest_relocated.csv` — event catalog
- `.../catalog_TRACE/main_shock_events.csv` — mainshock reference points

Typical usage is to:

1. load event and mainshock tables from CSV,
2. load this JSON as a list of polylines,
3. optionally project all geometry to a common local metric system,
4. draw these traces beneath events, corridor outlines, and circular neighborhoods.

#### Practical Loading Notes
For future agents, the expected loading pattern is simple:

- parse JSON to a Python list
- iterate over each trace
- for each trace, split vertex pairs into lon and lat arrays for plotting
- if metric operations are required, project each vertex from lon/lat to local x/y coordinates before plotting or geometric comparison

Because the file contains many traces (`17,792`), plotting all segments may be visually dense; agents may want to control line width, alpha, or spatial clipping when making figures, but no preprocessing is required just to read the data.

#### File Organization Context
Relevant surrounding files in the same directory include:

- `ridgecrest_axis_event_assignment.csv`
- `ridgecrest_recommended_corridors.csv`
- `ridgecrest_fault_segment_samples.csv`
- `ridgecrest_fault_axis_diagnostics.png`
- `analyze_ridgecrest_fault_axes.py`

These suggest additional corridor/fault-processing artifacts exist nearby, but `ridgecrest_surface_faults.json` is the core mapped-fault geometry source for visualization.

#### Example Path
- `<REPO_ROOT>/examples/ridgecrest/data/faults/ridgecrest_surface_faults.json`

#### Minimal Access Expectations
A future agent can expect this file to provide:

- one top-level list of many fault traces
- each trace as an ordered sequence of `[lon, lat]` pairs
- no missing attribute handling requirements because the file is geometry-only

This makes it a lightweight structural-context input for maps and corridor-definition diagnostics rather than a tabular analytical dataset.

------------------------------

