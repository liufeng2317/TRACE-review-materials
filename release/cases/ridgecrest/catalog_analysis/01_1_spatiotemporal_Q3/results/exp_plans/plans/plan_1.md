# Goal
Investigate the spatiotemporal evolution of the Ridgecrest inter-mainshock seismicity between the Mw 6.4 and Mw 7.1 events, with emphasis on whether seismicity migrates, focuses, spreads, or bifurcates in a way consistent with possible triggering of the Mw 7.1 mainshock.

## Planning Assumptions
- Use the relocated observation catalog as the primary dataset; no model data are needed.
- The analysis window is defined strictly from the origin time of the Mw 6.4 event to the origin time of the Mw 7.1 event using `main_shock_events.csv`.
- Spatial analyses should use one common longitude-latitude extent derived from all catalog events within the inter-mainshock window, expanded slightly by a fixed margin so all figures are directly comparable.
- KDE comparability requires one fixed bandwidth, one fixed grid, and one fixed global color normalization across all interval maps within the KDE workflow.
- Geographic coordinates are acceptable for requested map-based KDE, but geometric metrics and any area/perimeter-like comparisons should also be computed in a locally projected Cartesian system to avoid distortion-related bias.
- Convex hull requires at least 3 non-collinear points; alpha-shape requires enough points and a valid alpha parameter. Intervals with insufficient points must be flagged and skipped rather than forcing invalid geometries.
- Parallelization should be applied at the per-time-window level for KDE and envelope computation, with merged validation after all batches finish. Progress logging should report completed/total windows and any skipped intervals.
- Default to one primary analysis script with two independent computational branches inside it: KDE/hotspot analysis and geometric-envelope analysis. Both branches share the same cleaned event table and mainshock metadata.

## Analysis Plan

### Task 1: Build the inter-mainshock working catalog and common spatial reference
- Task description
  - Read the relocated catalog and two-event mainshock table, identify the Mw 6.4 and Mw 7.1 rows, define the inter-mainshock window, subset the catalog, and prepare shared inputs for all downstream analyses.
- Required data sources
  - `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/TRACE_ridgecrest_relocated.csv`
  - `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/main_shock_events.csv`
- Parameter selection strategy
  - Parse `event_time` to timezone-consistent datetime objects.
  - Identify mainshocks by magnitude values 6.4 and 7.1 from the reference file; if duplicate magnitudes occur, verify by event time ordering and retain the earlier as Mw 6.4 and later as Mw 7.1.
  - Subset all events with `mainshock64_time <= event_time <= mainshock71_time`.
  - Derive common map extent from min/max longitude and latitude of the subset, padded by a small fixed margin.
  - Create a local projected coordinate system centered on the inter-mainshock catalog centroid for geometry calculations.
- Constraints
  - Remove rows with missing or non-finite `event_time`, `latitude`, `longitude`, `depth_km`, or `magnitude`.
  - Remove exact duplicate rows if present and log counts before/after cleaning.
  - Preserve all magnitudes; do not impose an undocumented magnitude cutoff unless a data-quality issue is discovered and explicitly logged.
- Key outputs
  - Cleaned inter-mainshock event table.
  - Mainshock metadata table with Mw 6.4 and Mw 7.1 coordinates and times.
  - Shared analysis metadata file containing spatial extent, projected-coordinate definition, and event counts by window.

### Task 2: Spatial KDE migration analysis for evolving seismic concentration
- Task description
  - Compute interval-based 2D KDE maps over the inter-mainshock period, produce stage-wise map sequences, and identify primary density maxima for hotspot tracking.
- Required data sources
  - Cleaned inter-mainshock event table from Task 1.
  - Mainshock metadata table from Task 1.
- Parameter selection strategy
  - Define Stage 1 windows as consecutive 30-minute intervals from `mainshock64_time` to `mainshock64_time + 4 hours`.
  - Define Stage 2 windows as consecutive 2-hour intervals from `mainshock64_time + 4 hours` to `mainshock71_time`.
  - Use left-closed, right-open intervals internally for non-overlapping counts, with the final window adjusted to include the Mw 7.1 endpoint if needed.
  - Use one fixed KDE bandwidth for all windows, selected from the full inter-mainshock event distribution rather than per-window adaptation; document the chosen bandwidth explicitly.
  - Use one common regular grid over the shared spatial extent for all KDE evaluations.
  - Determine a single global density maximum from all valid windows and use it to normalize all subplot color scales.
  - For each interval, identify the primary hotspot as the grid node with maximum KDE value; optionally store the top few local maxima for diagnostic checking, but use only the primary maximum for the requested qualitative migration path.
- Constraints
  - Do not vary bandwidth, grid spacing, or extent between windows.
  - Windows with too few events for a stable KDE must be flagged; if KDE is still computed, label them as low-confidence in logs.
  - Each figure must contain exactly 8 subplots arranged 2 × 4, with identical extent, identical normalization, no colorbar, and both mainshock epicenters overlaid.
  - If Stage 2 contains more than 8 windows, paginate into multiple 8-panel figures while preserving identical scales across pages.
  - Use parallel processing across windows, but validate that all merged KDE rasters and hotspot tables are non-empty before marking the task complete.
- Key outputs
  - Interval-level KDE raster summaries and hotspot coordinate table.
  - Stage 1 KDE figure set (2 × 4 layout pages as needed).
  - Stage 2 KDE figure set (2 × 4 layout pages as needed).
  - One hotspot migration-path figure for Stage 1.
  - One hotspot migration-path figure for Stage 2.
  - Compact interval summary table including start/end time, event count, hotspot longitude/latitude, hotspot density value, and distance of hotspot to Mw 7.1 epicenter.

#### Task 2.1: Windowed event counting and data sufficiency checks
- Task description
  - Assign events to KDE windows and quantify counts before computation.
- Required data sources
  - Cleaned inter-mainshock event table.
- Parameter selection strategy
  - Count events per interval and rank windows by density of seismicity.
- Constraints
  - Keep empty and sparse windows in the summary table even if plotting/computation is skipped.
- Key outputs
  - Window-definition table and event-count table.

#### Task 2.2: KDE map computation and normalization
- Task description
  - Compute fixed-bandwidth KDE on a shared grid for each interval and derive common color scaling.
- Required data sources
  - Windowed events and shared map extent.
- Parameter selection strategy
  - Choose grid resolution fine enough to resolve migration without excessive cost; keep the same resolution for every interval.
- Constraints
  - Same grid and bandwidth for all windows.
- Key outputs
  - KDE arrays, global max-density value, and validity log.

#### Task 2.3: Hotspot tracking and migration diagnostics
- Task description
  - Extract primary hotspot coordinates from each interval and characterize qualitative migration.
- Required data sources
  - KDE arrays and mainshock metadata.
- Parameter selection strategy
  - Compute hotspot-to-hotspot step length, cumulative path length, and hotspot distance to Mw 7.1 epicenter through time.
- Constraints
  - Use the primary KDE maximum only for the requested migration path; do not switch to centroid-based tracking mid-analysis.
- Key outputs
  - Hotspot trajectory tables and two stage-specific migration figures.

### Task 3: Geometric morphological evolution of the seismic point cloud
- Task description
  - Compute 1-hour interval convex hulls and alpha-shapes for the inter-mainshock point cloud, then compare whether the seismic envelope contracts, expands, elongates, or fragments toward the Mw 7.1 area.
- Required data sources
  - Cleaned inter-mainshock event table from Task 1.
  - Mainshock metadata table from Task 1.
- Parameter selection strategy
  - Define consecutive 1-hour windows over `[mainshock64_time, mainshock71_time]`.
  - Compute geometries in projected coordinates for robustness, then convert boundaries back to longitude-latitude for mapping.
  - For convex hull, derive polygon boundary, area, perimeter, centroid, major-axis orientation, and centroid distance to Mw 7.1.
  - For alpha-shape, choose one fixed alpha parameter for all windows based on the full inter-mainshock point spacing distribution or another documented global criterion; do not tune alpha separately per interval.
  - For alpha-shape outputs with multiple disjoint polygons, retain all components and record component count as a fragmentation metric.
- Constraints
  - Intervals with insufficient points must be flagged and omitted from the corresponding geometry plot rather than generating invalid polygons.
  - Boundary curves only; no polygon fill.
  - One common spatial frame for all intervals in each figure.
  - Use color to encode elapsed time since Mw 6.4 consistently across both envelope figures.
  - Parallelize geometry construction by interval and validate merged geometry collections after completion.
- Key outputs
  - Interval geometry table with event count, convex-hull metrics, alpha-shape metrics, and fragmentation indicators.
  - One figure with all convex-hull boundaries overlaid and colored by time.
  - One figure with all alpha-shape boundaries overlaid and colored by time.

#### Task 3.1: One-hour window construction and point-cloud quality control
- Task description
  - Partition the inter-mainshock catalog into 1-hour windows and evaluate point counts and geometric feasibility.
- Required data sources
  - Cleaned inter-mainshock event table.
- Parameter selection strategy
  - Track intervals with <3 points, near-collinearity, or unstable geometry inputs.
- Constraints
  - Keep all windows in summary outputs even if geometry is skipped.
- Key outputs
  - Geometry-window summary table.

#### Task 3.2: Convex hull computation and geometric metrics
- Task description
  - Build convex hulls and extract envelope descriptors through time.
- Required data sources
  - Projected interval point clouds.
- Parameter selection strategy
  - Compute centroid migration and area/perimeter trends as simple focusing/defocusing indicators.
- Constraints
  - Use projected coordinates for metric calculations.
- Key outputs
  - Convex hull boundary set and metric table.

#### Task 3.3: Alpha-shape computation and fragmentation diagnostics
- Task description
  - Build alpha-shapes to capture non-convex and multi-lobed seismic envelopes.
- Required data sources
  - Projected interval point clouds.
- Parameter selection strategy
  - Use one globally fixed alpha value and record number of disconnected components, total enclosed area, and boundary length.
- Constraints
  - If alpha-shape degenerates to empty or line-like output, flag and skip that interval in the overlay figure.
- Key outputs
  - Alpha-shape boundary set and fragmentation/shape-metric table.

### Task 4: Comparative interpretation-oriented diagnostics focused on Mw 6.4 to Mw 7.1 triggering
- Task description
  - Combine KDE hotspot evolution and geometric-envelope metrics into a compact diagnostic summary aimed at distinguishing progressive focusing toward the Mw 7.1 rupture area from spreading/defocusing or bifurcation.
- Required data sources
  - Hotspot table from Task 2.
  - Geometry metrics from Task 3.
  - Mainshock metadata table.
- Parameter selection strategy
  - Compare early versus late inter-mainshock stages using:
    - hotspot distance to Mw 7.1 vs time,
    - hotspot step length vs time,
    - convex-hull centroid distance to Mw 7.1 vs time,
    - convex-hull/alpha-shape area vs time,
    - alpha-shape component count vs time.
  - Use the same stage split requested by the user: first 4 hours vs remaining inter-mainshock period.
- Constraints
  - Treat these as diagnostic summaries, not formal causal proof of triggering.
  - Do not introduce model-based stress transfer or ETAS analyses unless explicitly requested later.
- Key outputs
  - Unified CSV summary table merging interval-wise KDE and morphology diagnostics.
  - A concise machine-readable classification per interval or stage: focusing, spreading, bifurcating, or indeterminate, based on predefined metric rules documented in the output metadata.
  - Optional compact trend figures if needed for internal validation: metric-versus-time line plots for hotspot distance, hull area, alpha-shape area, and component count.

### Task 5: Execution flow, validation, and failure evidence collection
- Task description
  - Run the workflow with shared preprocessing, parallel interval computation, merged validation, and explicit evidence capture for skipped or failed windows.
- Required data sources
  - All outputs from Tasks 1–4.
- Parameter selection strategy
  - Use up to 64 cores for per-window KDE and geometry jobs.
  - Emit progress logs by stage and by completed window count.
  - Validate final outputs by checking expected number of windows, non-empty figure products, and non-empty summary tables.
- Constraints
  - A successful run requires valid merged scientific outputs for both KDE and geometry branches, not just completed per-window jobs.
  - Store skipped-window reasons explicitly: empty interval, too few points, invalid geometry, KDE instability, or projection error.
- Key outputs
  - Run log with timing, progress, and warnings.
  - Validation summary listing expected versus completed windows for each branch.
  - Failure/skip evidence table for reproducibility.