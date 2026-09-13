# Goal
Investigate the spatiotemporal evolution of the Ridgecrest sequence using the relocated observational catalog, with emphasis on whether post-Mw 6.4 seismicity evolves synchronously or as a staged/cascade-like process leading toward the Mw 7.1 mainshock.

## Planning Assumptions
- Use only the provided observational catalog and mainshock reference table; no model data are needed.
- `TRACE_ridgecrest_relocated.csv` is the primary event catalog and contains the required fields: `event_time`, `latitude`, `longitude`, `depth_km`, `magnitude`.
- `main_shock_events.csv` provides the authoritative Mw 6.4 and Mw 7.1 event times and epicenters used to define windows and overlays.
- Time handling must be done with timezone-consistent parsing of `event_time`; all relative times are referenced to the Mw 6.4 mainshock origin time.
- Spatial binning for onset analysis is defined in kilometers, so longitude/latitude coordinates must be projected to a local Cartesian system before constructing 0.5 km × 0.5 km cells.
- “No color interpolation within each time bin” means each event inherits a categorical bin color, not a continuous colormap by exact timestamp.
- A “sustained increase” in local seismicity rate should be implemented with an explicit, reproducible rule rather than visual judgment alone; cells without sufficient activity should remain unassigned or flagged as inactive.
- Computationally intensive loops over grid cells and time windows should be parallelized up to 64 cores, but merged outputs must be validated as complete and non-empty before accepting success.

## Analysis Plan

### Task 1 — Build the analysis-ready Ridgecrest sequence dataset
- Task description:
  - Read the relocated catalog and mainshock reference table, identify the Mw 6.4 and Mw 7.1 rows, define the required analysis windows, and generate a unified event table with relative-time and projected-coordinate fields.
- Required data sources:
  - `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/TRACE_ridgecrest_relocated.csv`
  - `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/main_shock_events.csv`
- Parameter selection strategy:
  - Select the Mw 6.4 and Mw 7.1 events from the two-row mainshock table by magnitude.
  - Define two post-Mw 6.4 windows:
    - Short window: `[t64, t64 + 4 hours]`
    - Long window: `[t64, t71]`
  - Compute for every catalog event:
    - relative time in seconds, minutes, and hours from Mw 6.4
    - projected planar coordinates (x_km, y_km) from longitude/latitude using a local projection centered on the sequence area or Mw 6.4 epicenter
- Constraints:
  - Keep only events needed for each downstream window; do not alter catalog magnitudes or depths.
  - Verify that Mw 7.1 occurs after Mw 6.4 and that both are inside the catalog time span.
  - Check for duplicate timestamps/locations only as a diagnostic; do not remove events unless duplicates are exact and demonstrably problematic.
- Key outputs:
  - Cleaned analysis table with added relative-time and projected-coordinate columns
  - Window-specific event subsets for short and long analyses
  - Data-quality summary table: event counts, time span, spatial bounds, projection metadata, counts per window

### Task 2 — Time-binned spatial point-cloud analysis after Mw 6.4
- Task description:
  - Produce two longitude–latitude epicenter scatter plots colored by discrete occurrence-time bins to visually assess temporal layering after Mw 6.4.
- Required data sources:
  - Window-specific subsets from Task 1
  - Mw 6.4 and Mw 7.1 epicenters from `main_shock_events.csv`
- Parameter selection strategy:
  - Short-window binning:
    - 30-minute bins over `[t64, t64 + 4 hours]`
  - Long-window binning:
    - 2-hour bins over `[t64, t71]`
  - Assign each event to exactly one categorical time bin; all events in the same bin share the same color.
  - Use a monotonic sequential palette ordered from early to late time bins.
- Constraints:
  - Plot in longitude–latitude coordinates as requested.
  - No within-bin color interpolation.
  - Include Mw 6.4 and Mw 7.1 epicenters with distinct marker symbols and labels.
  - If a bin has zero events, preserve the bin definition in legends/tables even if no points are plotted.
- Key outputs:
  - Figure 1: short-window time-colored epicenter scatter plot
  - Figure 2: long-window time-colored epicenter scatter plot
  - Companion bin-count tables for each figure
  - Optional diagnostic table listing first/last event time and spatial extent within each time bin

### Task 3 — Quantify whether temporal layering is spatially organized
- Task description:
  - Add quantitative support to the visual interpretation by measuring whether early and late time bins occupy distinct spatial zones after the Mw 6.4 event.
- Required data sources:
  - Long- and short-window binned event tables from Task 2
- Parameter selection strategy:
  - For each time bin, compute:
    - centroid location in projected coordinates
    - covariance ellipse or principal orientation of epicenter distribution
    - nearest-bin centroid distance and cumulative along-strike migration if an organizing fault trend exists
  - Summarize temporal evolution by comparing adjacent-bin centroid shifts and spatial overlap.
  - If the fault trend is not predefined, estimate the dominant spatial axis from PCA of post-Mw 6.4 events.
- Constraints:
  - Use projected coordinates for distance calculations, not raw longitude/latitude.
  - Treat these calculations as supporting diagnostics; they must not replace the requested visual and onset analyses.
- Key outputs:
  - Table of centroid positions and spatial spread by time bin
  - Figure 3: projected-coordinate map with per-bin centroids and migration arrows
  - Quantitative indicators of segregation vs mixing to support interpretation of staged triggering

### Task 4 — Construct gridded local seismicity-rate time series
- Task description:
  - Discretize the study area and build local seismicity-rate time series needed for onset-time detection.
- Required data sources:
  - Events in `[t64, t71]` from Task 1
- Parameter selection strategy:
  - Define the study region as the spatial extent of all events within `[t64, t71]`.
  - Build a regular Cartesian grid with 0.5 km × 0.5 km cells using projected coordinates.
  - Count events in each cell in 30-minute time bins from `t64` to `t71`.
  - Store both:
    - raw counts per 30-minute bin
    - cumulative counts through time
- Constraints:
  - Grid spacing must be exactly 0.5 km in projected units.
  - Use half-open time bins consistently except possibly the final bin; document the convention.
  - Cells with no events throughout the whole window should either be excluded from onset mapping or retained with an inactive flag.
  - This step may be parallelized across grid-cell chunks or spatial tiles.
- Key outputs:
  - Gridded event-count matrix: rows = cells, columns = 30-minute bins
  - Grid metadata table: cell ID, x/y bounds, lon/lat centroid, total events
  - Figure 4: map of total event counts per cell for the full `[t64, t71]` window

### Task 5 — Define and compute onset time for each spatial cell
- Task description:
  - Derive a reproducible activation/onset time from each local seismicity-rate series and distinguish cells with clear activation from weak/noisy cells.
- Required data sources:
  - Cell-wise 30-minute count time series from Task 4
- Parameter selection strategy:
  - Use a sustained-increase rule that is explicit and reproducible. Recommended primary rule:
    - onset bin = first 30-minute bin after Mw 6.4 for which:
      - the local count exceeds a baseline threshold, and
      - activity remains elevated for at least a minimum number of subsequent bins or cumulative counts continue increasing above baseline over a defined persistence window
  - Determine baseline from pre-onset bins within the same post-Mw 6.4 window using robust local statistics such as early-window median and MAD, or from the first one or two bins if no true pre-event baseline exists.
  - Impose a minimum total-event threshold per cell to avoid assigning onset in cells with only isolated single events.
  - Record:
    - onset bin index
    - onset time in hours after Mw 6.4
    - confidence/quality flag
    - inactive/undetermined flag where criteria are unmet
- Constraints:
  - Because the requested window begins at Mw 6.4, there is no long pre-mainshock baseline inside the main onset window; the rule must therefore rely on post-mainshock internal consistency and persistence, not on assumed pre-event quiescence.
  - The onset definition must be applied identically to all cells.
  - Do not fill missing onset times with arbitrary late values; preserve NA/undetermined states.
  - Parallelize across cells up to 64 cores if needed, and validate that all cell results are merged correctly.
- Key outputs:
  - Cell-level onset table with onset time, persistence metrics, and quality flags
  - Summary statistics of onset times: number of active cells, inactive cells, onset-time distribution
  - Diagnostic examples of representative cell time series for early-, intermediate-, late-, and inactive-onset cases

### Task 6 — Map onset time and diagnose staged activation toward the Mw 7.1 region
- Task description:
  - Visualize onset time spatially and test whether activation propagates toward the eventual Mw 7.1 hypocentral area or remains spatially mixed.
- Required data sources:
  - Cell-level onset table from Task 5
  - Mainshock epicenters from `main_shock_events.csv`
- Parameter selection strategy:
  - Map each 0.5 km × 0.5 km cell colored by onset time relative to Mw 6.4:
    - earlier = darker
    - later = lighter
  - Overlay Mw 6.4 and Mw 7.1 epicenters.
  - Compute supplementary gradients:
    - distance from each cell centroid to Mw 6.4 and Mw 7.1
    - onset time versus distance to Mw 7.1
    - onset time projected along the dominant fault-strike axis
  - If useful, subdivide the grid into structural sectors (e.g., southwest/central/northeast or along-strike segments) based on the observed event cloud, then compare onset-time distributions among sectors.
- Constraints:
  - Cells flagged inactive/undetermined must be shown distinctly from valid onset times.
  - Preserve the requested darker-to-lighter temporal ordering.
  - Sector definitions, if used, must be derived from data geometry and documented explicitly rather than chosen arbitrarily.
- Key outputs:
  - Figure 5: onset-time map on the 0.5 km grid
  - Figure 6: onset time versus distance to Mw 7.1
  - Figure 7: onset time projected along strike or across selected structural sectors
  - Interpretation-ready diagnostics indicating synchronous mixing versus cascade-like propagation

### Task 7 — Focused trigger-mechanism assessment from Mw 6.4 to Mw 7.1
- Task description:
  - Integrate the time-binned maps and onset-time products to evaluate whether the Mw 7.1 preparation zone shows delayed activation, migration, or broad immediate triggering after Mw 6.4.
- Required data sources:
  - Outputs from Tasks 2, 3, 5, and 6
- Parameter selection strategy:
  - Define a focused Mw 7.1 neighborhood using distance-based windows around the Mw 7.1 epicenter and compare with the rest of the sequence region.
  - Compare:
    - first activation time in the Mw 7.1 neighborhood
    - event-count growth rate through time
    - fraction of active cells through time
    - centroid migration toward the Mw 7.1 area
  - Construct cumulative event-count curves for:
    - Mw 7.1 neighborhood
    - Mw 6.4 neighborhood
    - remaining sequence area
- Constraints:
  - Neighborhood radii must be chosen from catalog geometry and reported explicitly; they should not exceed the scale at which the Mw 7.1 preparation area loses local meaning.
  - This is still catalog-based inference only; do not claim dynamic triggering mechanisms that require waveform stress analysis or geodetic data.
- Key outputs:
  - Figure 8: cumulative counts through time for Mw 7.1 neighborhood vs other regions
  - Figure 9: fraction of newly activated cells through time by region
  - Regional comparison table summarizing onset delay and activity growth relative to Mw 6.4

### Task 8 — Execution structure, parallelization, and validation
- Task description:
  - Organize computation into independent major analytical products, with progress reporting and intermediate validation at each stage.
- Required data sources:
  - All upstream inputs and derived products
- Parameter selection strategy:
  - Primary script A:
    - data ingest, window construction, projection, time-binned scatter plots, spatial-bin diagnostics
  - Primary script B:
    - grid construction, local rate series, onset detection, onset mapping, regional trigger assessment
  - Parallel execution:
    - distribute grid-cell time-series construction and onset detection across up to 64 cores
    - optionally parallelize heavy plotting preparation for large point subsets
  - Emit progress logs for:
    - file read completion
    - window extraction
    - grid creation
    - processed cell counts
    - merged result validation
- Constraints:
  - Each script must validate its own outputs immediately:
    - non-empty tables
    - expected number of time bins
    - expected presence of Mw 6.4 and Mw 7.1 overlays
    - complete merged onset table with no dropped cells
  - Failure evidence should include counts of missing/invalid cells, empty bins, or projection/parse errors.
- Key outputs:
  - Script-level output inventories
  - Validation logs and summary diagnostics
  - Final figure set and machine-readable tables for all major analytical steps