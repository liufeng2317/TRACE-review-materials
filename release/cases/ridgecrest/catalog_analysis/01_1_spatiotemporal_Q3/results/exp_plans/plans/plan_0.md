# Goal
Investigate the spatiotemporal evolution of the Ridgecrest inter-mainshock seismicity between the Mw 6.4 and Mw 7.1 events, with emphasis on whether seismicity progressively focuses toward the Mw 7.1 rupture area, defocuses/spreads, or evolves in a fragmented manner, using time-sliced spatial KDE and geometric envelope analysis.

## Planning Assumptions
- Use only the provided observational relocated catalog and the two-row mainshock reference table; no model data are needed.
- The inter-mainshock analysis window is defined exactly from the Mw 6.4 origin time to the Mw 7.1 origin time read from `main_shock_events.csv`.
- Geographic coordinates are acceptable for requested 2D KDE and envelope visualization, but geometric calculations should also use a local projected coordinate system internally for distance/area/perimeter stability; final plots can remain in longitude-latitude.
- KDE comparability requires one fixed bandwidth, one fixed map extent, one fixed grid, and one global color normalization applied to all interval maps within the full KDE workflow.
- Empty or too-sparse time bins must not be forced into misleading outputs; intervals with insufficient events should be flagged and shown consistently as no-density / no-envelope cases.
- Convex hull requires at least 3 non-collinear points; alpha shape requires enough points and a documented alpha-selection rule. If an interval is too sparse, record null geometry rather than extrapolating.
- Parallel computation may be used for independent time-bin calculations up to 64 cores, but merged scientific outputs must be validated after batch completion.
- Package contract summary:
  - ObsPy tutorial/API may be used only for robust UTC time parsing if needed; the core workflow is standard pandas/numpy/scipy/sklearn/shapely-style catalog analysis rather than a package-driven seismic engine.
  - No retrieved external package contract is required because the request does not hinge on specialized seismic software APIs.

## Analysis Plan
### Task 1 — Time-sliced KDE evolution and hotspot migration
- Task description:
  - Build the inter-mainshock catalog subset, partition it into the requested variable-length intervals, compute 2D spatial KDE on a common grid for each interval, identify the primary density maximum per interval, and generate stage-wise map panels plus hotspot migration figures.
- Required data sources:
  - `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/TRACE_ridgecrest_relocated.csv`
  - `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/main_shock_events.csv`
- Parameter selection strategy:
  - Read `event_time, latitude, longitude, depth_km, magnitude` from both CSVs.
  - Identify the Mw 6.4 and Mw 7.1 rows from `main_shock_events.csv`; use their `event_time` values as start and end of the global analysis window.
  - Filter the full catalog to events with `event_time` in `[Mw6.4_time, Mw7.1_time]`.
  - Define Stage 1 bins over `[Mw6.4_time, Mw6.4_time + 4 hours]` with 30-minute intervals.
  - Define Stage 2 bins over `[Mw6.4_time + 4 hours, Mw7.1_time]` with 2-hour intervals; truncate the final bin at `Mw7.1_time`.
  - Use one common spatial extent from the min/max longitude-latitude of the inter-mainshock subset with a small documented margin so hotspots near edges are not clipped.
  - Use one common regular grid for all KDE maps; grid density should be chosen to balance spatial detail and runtime, then held fixed for all intervals.
  - Select one fixed KDE bandwidth from the full inter-mainshock point cloud, using a documented rule that is independent of individual bins; compute in projected x-y coordinates internally, then map results back to lon-lat for plotting.
  - Determine one global color scale from the full set of interval KDE rasters so all subplots are directly comparable.
  - Define hotspot as the grid node of the maximum KDE value in each interval; if multiple maxima exist, choose one deterministically and record ties if present.
- Constraints:
  - All KDE subplots must share identical spatial extent, bandwidth, grid, and color normalization.
  - No colorbar should be drawn on the requested panel figures.
  - Each figure should contain exactly 8 subplots in a 2 x 4 grid; if the number of intervals exceeds 8 within a stage, split into multiple sequential figures while preserving the same formatting and normalization.
  - Overlay both mainshock epicenters on every KDE subplot and on hotspot migration figures.
  - Handle bins with zero or very few events explicitly; mark them as insufficient for KDE and exclude them from hotspot path segments rather than inventing maxima.
  - Parallelize per-bin KDE calculations and hotspot extraction; after all bins finish, validate that the merged raster stack and hotspot table are non-empty where expected.
- Key outputs:
  - Clean inter-mainshock event table with assigned stage and interval IDs.
  - Interval summary table: interval start/end, event count, KDE status, hotspot longitude/latitude, hotspot density value.
  - Stage 1 KDE panel figure(s), 2 x 4 each.
  - Stage 2 KDE panel figure(s), 2 x 4 each.
  - Stage 1 hotspot migration path figure.
  - Stage 2 hotspot migration path figure.
  - Optional machine-readable raster metadata table documenting extent, grid spacing, bandwidth, and global color normalization.

### Task 2 — Hourly geometric envelope evolution using convex hull and alpha shape
- Task description:
  - Partition the inter-mainshock seismicity into 1-hour bins, compute convex hull and alpha-shape boundaries for each interval, extract geometric descriptors, and plot all hourly boundaries together for temporal comparison.
- Required data sources:
  - `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/TRACE_ridgecrest_relocated.csv`
  - `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/main_shock_events.csv`
- Parameter selection strategy:
  - Reuse the same inter-mainshock filtered catalog from Task 1.
  - Build 1-hour bins over `[Mw6.4_time, Mw7.1_time]`; truncate the last bin at `Mw7.1_time`.
  - Perform geometry calculations in a local projected coordinate system for numerical stability; convert boundaries back to lon-lat for plotting.
  - Compute convex hull for bins with at least 3 non-collinear epicenters.
  - Compute alpha shape for bins with sufficient points using one fixed alpha-selection rule applied consistently across all bins; alpha should be selected from the overall inter-mainshock spatial scale rather than tuned independently per hour.
  - For each valid interval, calculate supporting descriptors such as event count, hull area, alpha-shape area, perimeter, centroid, compactness or elongation metrics, and number of disconnected alpha-shape components if present.
  - Map time since Mw 6.4 mainshock to a continuous color ramp shared by all interval boundaries in each morphology figure.
- Constraints:
  - Plot all interval boundaries in the same spatial frame for the convex hull figure and separately for the alpha-shape figure.
  - Plot boundary curves only; no polygon fills.
  - Overlay both mainshock epicenters.
  - Preserve a single map extent across both morphology figures to support comparison.
  - For sparse or degenerate intervals, record null geometry and omit boundary drawing rather than forcing invalid polygons.
  - If alpha shape returns multiple components, keep all valid boundary components and record component count as evidence for fragmented morphology.
  - Parallelize hourly geometry calculations, but merge and validate all interval geometries before plotting.
- Key outputs:
  - Hourly morphology summary table: interval start/end, event count, convex-hull validity, alpha-shape validity, area/perimeter metrics, centroid coordinates, component count.
  - Convex hull evolution figure with all hourly boundaries colored by time since Mw 6.4.
  - Alpha-shape evolution figure with all hourly boundaries colored by time since Mw 6.4.
  - Optional derived time-series table of morphology metrics for later interpretation of focusing, defocusing, or fragmentation.