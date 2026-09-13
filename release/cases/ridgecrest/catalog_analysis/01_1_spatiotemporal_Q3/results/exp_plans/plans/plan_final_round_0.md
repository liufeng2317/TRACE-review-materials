# Goal
Investigate the spatiotemporal evolution of the Ridgecrest inter-mainshock seismicity between the Mw 6.4 and Mw 7.1 events, with specific focus on whether seismicity shows progressive migration/focusing toward the Mw 7.1 rupture area, spatial spreading/defocusing, or fragmented multi-lobed evolution during the interval from the Mw 6.4 to the Mw 7.1 mainshock.

## Planning Assumptions
- Use only the provided observational relocated catalog and the provided mainshock reference file; no model data are needed.
- The analysis window is defined exactly by the Mw 6.4 and Mw 7.1 origin times read from `main_shock_events.csv`.
- One primary analysis script is sufficient because data ingestion, interval construction, KDE, hotspot tracking, geometric-envelope analysis, plotting, and validation are tightly coupled and share the same catalog subset and metadata.
- All map-based products must use one common spatial extent derived once from the full inter-mainshock catalog, then reused unchanged across KDE and morphology figures wherever comparable.
- KDE comparability requires one fixed bandwidth, one fixed spatial grid, and one fixed global color normalization across all interval KDE maps.
- Geographic coordinates are acceptable for plotting, but distance-sensitive operations should be performed in a local projected coordinate system for numerical stability; results can then be converted back to longitude-latitude for final map outputs.
- Convex hull requires at least 3 non-collinear points; alpha-shape requires sufficient points and one fixed alpha-selection rule applied across all hourly intervals. Intervals failing these conditions must be recorded as insufficient rather than forced into invalid geometries.
- Parallelization may be used for independent interval calculations up to 64 cores, but task success requires valid merged scientific outputs, not only successful per-interval jobs.
- Long computations should emit progress information for interval processing, skipped intervals, and final completion counts.

## Analysis Plan

### Task 1 — Build the inter-mainshock working catalog and shared spatial reference
- Task description:
  - Read the relocated catalog and mainshock file, identify the Mw 6.4 and Mw 7.1 events, subset the inter-mainshock catalog, define all required interval schemes, and prepare the shared spatial reference used by all later analyses.
- Required data sources:
  - `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/TRACE_ridgecrest_relocated.csv`
  - `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/main_shock_events.csv`
- Parameter selection strategy:
  - Parse `event_time` into timezone-consistent datetime values.
  - Identify the Mw 6.4 and Mw 7.1 rows from `main_shock_events.csv`; if duplicate magnitudes exist, confirm by time ordering and retain the earlier event as Mw 6.4 and the later event as Mw 7.1.
  - Filter the catalog to events with `event_time` in `[Mw6.4_time, Mw7.1_time]`.
  - Define three interval sets:
    - KDE Stage 1: contiguous 30-minute bins over `[Mw6.4_time, Mw6.4_time + 4 hours]`
    - KDE Stage 2: contiguous 2-hour bins over `[Mw6.4_time + 4 hours, Mw7.1_time]`
    - Morphology: contiguous 1-hour bins over `[Mw6.4_time, Mw7.1_time]`
  - Use left-closed/right-open binning internally, with the final bin including the endpoint.
  - Derive one common map extent from the min/max longitude-latitude of the inter-mainshock subset with a small fixed margin.
  - Define one local projected coordinate system centered on the inter-mainshock seismicity for bandwidth selection, hotspot-distance calculations, and envelope geometry.
- Constraints:
  - Remove rows with missing or non-finite `event_time`, `latitude`, `longitude`, `depth_km`, or `magnitude`, and log counts before/after cleaning.
  - Do not impose any undocumented magnitude threshold.
  - Preserve the original catalog columns and add only derived fields needed for interval IDs, elapsed time, and projected coordinates.
- Key outputs:
  - Clean inter-mainshock event table
  - Mainshock metadata table with Mw 6.4 and Mw 7.1 times and coordinates
  - Interval-definition table for KDE Stage 1, KDE Stage 2, and morphology windows
  - Shared analysis metadata table containing common extent, projection definition, and per-window event counts

### Task 2 — Time-sliced spatial KDE evolution and hotspot migration
- Task description:
  - Compute interval-wise 2D KDE maps on a common grid, identify the primary density maximum in each interval, generate the requested KDE panel figures, and trace hotspot migration separately for Stage 1 and Stage 2.
- Required data sources:
  - Clean inter-mainshock event table from Task 1
  - Mainshock metadata table from Task 1
  - KDE interval-definition tables from Task 1
- Parameter selection strategy:
  - Perform KDE in projected planar coordinates, then display the results in the shared longitude-latitude map frame.
  - Select one fixed KDE bandwidth from the full inter-mainshock point cloud using one documented global rule and keep it unchanged for every interval.
  - Use one fixed regular spatial grid over the shared extent for all intervals.
  - Compute KDE separately for:
    - Stage 1: 30-minute bins in the first 4 hours after Mw 6.4
    - Stage 2: 2-hour bins from Mw 6.4 + 4 hours to Mw 7.1
  - Determine one global color normalization from all valid interval KDE grids combined and apply it to every KDE subplot.
  - Define the hotspot for each interval as the global maximum of the KDE field on the common grid.
  - For each interval, also store event count, hotspot coordinates, peak density value, hotspot step length relative to the previous interval, and hotspot distance to the Mw 7.1 epicenter.
- Constraints:
  - All KDE maps must share identical spatial extent, grid, bandwidth, and color normalization.
  - Do not draw a colorbar in the requested KDE panel figures.
  - Each KDE figure must contain exactly 8 subplots in a 2 × 4 layout; if a stage contains more than 8 intervals, paginate into multiple sequential 8-panel figures while preserving identical scales.
  - Overlay both mainshock epicenters on every KDE subplot.
  - Intervals with zero or too few events for stable KDE must be explicitly flagged and retained in the interval summary table; do not replace missing information with fabricated hotspots.
  - Parallelize per-interval KDE calculations and hotspot extraction; after completion, validate that the merged KDE stack and hotspot table are non-empty where expected.
- Key outputs:
  - Interval-level KDE summary table with interval start/end, event count, KDE status, hotspot longitude/latitude, hotspot density value, hotspot step length, and hotspot distance to Mw 7.1
  - Stage 1 KDE panel figure set, 2 × 4 per page
  - Stage 2 KDE panel figure set, 2 × 4 per page
  - Stage 1 hotspot migration path figure
  - Stage 2 hotspot migration path figure
  - KDE parameter manifest documenting extent, grid spacing, fixed bandwidth, and global normalization

### Task 3 — KDE-based focusing, spreading, and bifurcation diagnostics
- Task description:
  - Derive compact interval-wise diagnostics from the KDE products to support interpretation of progressive focusing toward the Mw 7.1 rupture area versus defocusing or spatial bifurcation.
- Required data sources:
  - KDE grids and hotspot table from Task 2
  - Mainshock metadata table from Task 1
- Parameter selection strategy:
  - For each valid KDE interval, compute:
    - Hotspot distance to Mw 7.1
    - Hotspot distance to Mw 6.4
    - Hotspot displacement from the previous interval
    - High-density area using one fixed density threshold applied consistently to all intervals
    - Number of disconnected high-density patches above the same threshold as a bifurcation indicator
  - Compare these diagnostics separately for Stage 1 and Stage 2.
  - Use elapsed time since Mw 6.4 as the common temporal axis.
- Constraints:
  - The high-density threshold must be fixed across all intervals and documented.
  - Patch-count and high-density-area metrics are supplementary; the primary hotspot remains the requested migration tracker.
  - These diagnostics support interpretation but do not constitute a causal triggering model.
- Key outputs:
  - KDE diagnostic table by interval
  - Stage-comparison summary table highlighting evidence for focusing, spreading, or bifurcation
  - Machine-readable merged KDE metrics table for later integration with morphology outputs

### Task 4 — Hourly geometric morphological evolution using convex hull and alpha shape
- Task description:
  - For each 1-hour inter-mainshock interval, compute the convex hull and alpha-shape of the seismic point cloud, extract morphology metrics, and quantify contraction, expansion, elongation, or fragmentation through time.
- Required data sources:
  - Clean inter-mainshock event table from Task 1
  - Morphology interval-definition table from Task 1
  - Mainshock metadata table from Task 1
- Parameter selection strategy:
  - Use projected coordinates for all geometry calculations.
  - For each 1-hour interval, compute:
    - Convex hull boundary
    - Alpha-shape boundary or multi-boundary geometry using one fixed alpha parameter for all intervals
  - Select the alpha parameter from the full inter-mainshock spatial scale using one documented global rule; keep it unchanged across all hourly bins.
  - For each valid interval, derive:
    - Event count
    - Convex hull area, perimeter, and centroid
    - Alpha-shape area, perimeter, centroid, and component count
    - Centroid distance to Mw 7.1
    - Optional elongation/orientation metrics if geometry is valid
- Constraints:
  - If an interval has fewer than 3 valid non-collinear points, record null geometry rather than forcing an envelope.
  - If alpha-shape returns multiple disconnected components, retain all valid components and record the component count as a fragmentation metric.
  - Parallelize per-interval geometry calculations and validate the merged geometry collection before plotting.
  - Use the same map extent for convex hull and alpha-shape evolution figures.
- Key outputs:
  - Hourly morphology summary table with convex-hull validity, alpha-shape validity, area/perimeter metrics, centroid coordinates, centroid distance to Mw 7.1, and alpha-shape component count
  - Serialized boundary-coordinate tables for convex hull and alpha-shape outputs
  - Geometry parameter manifest documenting fixed alpha and geometry-validity rules

### Task 5 — Overlay visualization of envelope evolution
- Task description:
  - Produce the requested time-encoded overlay figures for convex hull and alpha-shape boundaries to visualize whether the spatial envelope contracts toward the Mw 7.1 rupture zone, expands laterally, or develops multi-lobed structure.
- Required data sources:
  - Convex hull and alpha-shape boundary outputs from Task 4
  - Mainshock metadata table from Task 1
- Parameter selection strategy:
  - Plot all hourly convex hull boundaries in one common spatial frame.
  - Plot all hourly alpha-shape boundaries in one common spatial frame.
  - Use a continuous color ramp tied to elapsed time since Mw 6.4, with early intervals shown in cooler colors and late intervals in warmer colors.
  - Plot boundary curves only; do not fill polygons.
  - Overlay Mw 6.4 and Mw 7.1 epicenters on both figures.
- Constraints:
  - Maintain identical spatial extent across the convex hull and alpha-shape evolution figures.
  - Draw every component boundary for multi-component alpha shapes.
  - Omit invalid or insufficient-data intervals from boundary plotting, but keep them in the summary table.
- Key outputs:
  - Convex hull evolution figure with all hourly boundaries colored by time since Mw 6.4
  - Alpha-shape evolution figure with all hourly boundaries colored by time since Mw 6.4

### Task 6 — Integrated triggering-oriented diagnostics and validation
- Task description:
  - Integrate KDE hotspot evolution and geometric-envelope metrics into one compact diagnostic framework focused on the Mw 6.4 to Mw 7.1 transition, while also performing merged output validation and failure evidence collection.
- Required data sources:
  - KDE metrics from Tasks 2–3
  - Morphology metrics from Tasks 4–5
  - Mainshock metadata table from Task 1
- Parameter selection strategy:
  - Compare Stage 1 versus Stage 2 using:
    - Hotspot distance to Mw 7.1 through time
    - Hotspot step length through time
    - High-density area and patch count through time
    - Convex-hull centroid distance to Mw 7.1 through time
    - Convex-hull and alpha-shape area changes through time
    - Alpha-shape component count through time
  - Align all diagnostics by elapsed time since Mw 6.4.
  - Assign compact interval-level or stage-level labels such as focusing, defocusing, fragmented, or insufficient-data using predefined documented metric rules.
  - Use up to 64 cores for interval-based calculations and emit progress logs for KDE and geometry branches.
- Constraints:
  - This integration step must use only already computed observational diagnostics; do not introduce ETAS, Coulomb stress, or other additional triggering models unless explicitly requested later.
  - Successful completion requires valid merged outputs for both the KDE branch and the morphology branch, not merely completed per-interval jobs.
  - Skipped intervals must be recorded with explicit reasons such as empty bin, too few points, invalid geometry, or unstable KDE.
- Key outputs:
  - Unified summary table merging interval-wise KDE and morphology diagnostics
  - Machine-readable interpretation table with per-interval or per-stage labels: focusing, defocusing, fragmented, or insufficient-data
  - Run log with progress, warnings, and completed/skipped interval counts
  - Validation summary listing expected versus completed KDE windows, hotspot records, convex hulls, and alpha-shape geometries