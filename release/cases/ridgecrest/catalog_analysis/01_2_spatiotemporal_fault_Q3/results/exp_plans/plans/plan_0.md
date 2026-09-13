# Goal
Investigate the spatiotemporal evolution of Ridgecrest inter-mainshock seismicity between the Mw 6.4 and Mw 7.1 mainshocks, with emphasis on whether seismicity migrates by progressive focusing toward the Mw 7.1 rupture area, by spreading/defocusing, or by structurally controlled transfer along complex fault geometry.

## Planning Assumptions
- Use only the provided observation-based relocated catalog, mainshock reference table, and mapped surface fault traces; no model-generated seismicity is needed.
- The relocated catalog and mainshock CSVs share the schema `event_time, latitude, longitude, depth_km, magnitude`; `event_time` must be parsed to a timezone-consistent datetime type before interval selection.
- The analysis window is defined directly from the Mw 6.4 and Mw 7.1 event times in `main_shock_events.csv`; the two mainshocks should also be retained as epicenter overlays in all map products.
- Geographic analysis is requested in latitude-longitude space. For comparability, all interval products must use one common map extent, one common analysis grid, one fixed KDE bandwidth, and one fixed alpha-shape parameter across the full inter-mainshock period.
- Sparse-interval geometry constraints must be enforced: convex hull requires at least 3 non-collinear points; alpha-shape should be skipped or flagged for intervals with insufficient points or invalid geometry rather than forcing a fallback polygon and treating it as valid output.
- Computationally intensive interval loops should be parallelized up to 64 cores, but merged scientific outputs must be validated after batch completion: non-empty interval summary tables, valid KDE rasters where expected, and valid geometry boundaries where expected.
- Fault JSON is a list of polyline segments containing `[longitude, latitude]` pairs; it is used only as a top-level structural overlay and should not be altered except for parsing and optional clipping to the study extent.

## Analysis Plan

### Task 1: Inter-mainshock KDE migration analysis
- Task description
  - Build interval-based 2D spatial density maps for seismicity between the Mw 6.4 and Mw 7.1 events, identify the primary hotspot in each interval, and evaluate whether the cluster migrates toward the Mw 7.1 area by focusing, spreading, or bifurcation.
- Required data sources
  - `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/TRACE_ridgecrest_relocated.csv`
  - `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/main_shock_events.csv`
  - `<REPO_ROOT>/examples/ridgecrest/data/faults/ridgecrest_surface_faults.json`
- Parameter selection strategy
  - Parse the mainshock table, identify the Mw 6.4 and Mw 7.1 rows by magnitude, and set the global analysis window as `[t64, t71]`.
  - Build two interval schedules:
    - Stage 1: `[t64, t64 + 4 hr]` with 30-minute bins.
    - Stage 2: `[t64 + 4 hr, t71]` with 2-hour bins.
  - Use half-open bin logic for internal intervals and a closed final interval so every event is counted once.
  - Define one common map extent from the full inter-mainshock catalog, expanded by a small fixed geographic margin so KDE edges and fault overlays are not clipped.
  - Define one common 2D latitude-longitude grid for all intervals; grid spacing should be selected from the study extent so hotspot position is stable but runtime remains practical.
  - Select one fixed KDE bandwidth from the full inter-mainshock event cloud using a single documented rule applied once for the whole study; retain that value unchanged for every interval.
  - Compute a global KDE maximum from all interval KDE results and use it to normalize subplot color scales consistently across every KDE figure.
  - For each interval, identify the primary hotspot as the grid cell of maximum KDE density; store time, hotspot longitude, hotspot latitude, peak density, event count, and stage label.
- Constraints
  - Keep identical bandwidth, grid, extent, and density normalization across all interval KDE maps.
  - Do not change bandwidth adaptively by interval, event count, or local density.
  - Plot 8 subplots per figure in a 2 x 4 arrangement; if a stage contains more than 8 intervals, emit multiple sequential figures while preserving the same plotting rules.
  - Overlay all fault polylines and both mainshock epicenters on every subplot; do not include a colorbar.
  - Intervals with zero or too few events should still appear in the sequence with explicit empty/insufficient-data marking so the temporal evolution remains complete.
  - Use parallel processing for per-interval KDE computation and hotspot extraction; validate that the merged interval summary is complete and ordered by time.
- Key outputs
  - Interval definition table for Stage 1 and Stage 2 with start time, end time, duration, and event count.
  - Per-interval KDE summary table containing hotspot coordinates and peak density.
  - Stage 1 KDE map sequence figures in 2 x 4 layout blocks.
  - Stage 2 KDE map sequence figures in 2 x 4 layout blocks.
  - One hotspot migration figure for Stage 1 showing ordered hotspot path with faults and both mainshocks.
  - One hotspot migration figure for Stage 2 showing ordered hotspot path with faults and both mainshocks.
  - Compact machine-readable interval metadata file linking each interval to its KDE result and hotspot location.

### Task 2: Geometric morphological evolution of the seismic point cloud
- Task description
  - Quantify and visualize whether the inter-mainshock seismicity envelope contracts toward the Mw 7.1 zone, expands/spreads, or evolves into multi-lobed structures by tracking convex hull and alpha-shape boundaries in 1-hour windows.
- Required data sources
  - `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/TRACE_ridgecrest_relocated.csv`
  - `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/main_shock_events.csv`
  - `<REPO_ROOT>/examples/ridgecrest/data/faults/ridgecrest_surface_faults.json`
- Parameter selection strategy
  - Use the same inter-mainshock window `[t64, t71]` and create consecutive 1-hour intervals.
  - Use the same common map extent as Task 1 for direct spatial comparison between analyses.
  - For each 1-hour interval, extract the event point cloud in longitude-latitude space and compute:
    - Convex hull boundary.
    - Alpha-shape boundary using one fixed alpha value selected once from the full inter-mainshock catalog and then held constant across all intervals.
  - In addition to geometry generation, compute interval-level morphology metrics to support interpretation:
    - Event count.
    - Convex hull area and perimeter.
    - Alpha-shape area and perimeter where valid.
    - Distance from hull/alpha centroid to Mw 7.1 epicenter.
    - Optional fragmentation count for alpha-shape if multiple disconnected polygons arise.
  - Map interval time to a continuous color scale representing elapsed time since the Mw 6.4 mainshock, using the same time-color mapping in both envelope figures.
- Constraints
  - Do not tune alpha separately by interval.
  - Plot only boundary curves; no polygon filling.
  - Overlay faults and both mainshock epicenters at the top level in both figures.
  - Intervals with insufficient points or invalid geometries must be retained in the summary table with reason codes such as too-few-points, collinear-points, or invalid-alpha-geometry.
  - Use parallel processing for interval-wise geometry construction and metric calculation; merged outputs must be checked for chronological completeness and valid geometry counts.
  - Because the request is qualitative-mechanistic, the morphology metrics should be treated as supporting diagnostics rather than replacing the map-based boundary evolution.
- Key outputs
  - One-hour interval table with event counts and geometry validity flags.
  - Convex hull boundary figure showing all interval boundaries in one common frame, colored by time since Mw 6.4.
  - Alpha-shape boundary figure showing all valid interval boundaries in one common frame, colored by time since Mw 6.4.
  - Morphology summary table containing area, perimeter, centroid location, centroid-to-Mw 7.1 distance, and fragmentation diagnostics by interval.
  - Optional derived trend table for early-to-late comparison of envelope contraction, expansion, or fragmentation indicators.