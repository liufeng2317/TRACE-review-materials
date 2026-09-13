# Goal
Investigate whether and how the Mw 6.4 earthquake triggered the Mw 7.1 earthquake in the Ridgecrest sequence by comparing fixed fault-oriented Region A and Region B, quantifying temporal offsets in activation, differences in seismic-rate/energy evolution, and the internal spatial ordering of post-Mw 6.4 triggering.

## Planning Assumptions
- Use the provided relocated observational catalog as the primary dataset; no model data are needed.
- Analysis time window is fixed to `[catalog start time, Mw 7.1 origin time]`, with post-Mw 6.4 diagnostics referenced to elapsed time since the Mw 6.4 mainshock.
- Region definitions are fixed by the user and must not be re-optimized from the data.
- Corridor membership and circular-neighborhood membership are independent boolean masks; events may belong to multiple masks.
- Local geometric calculations should be done in a local metric projection centered on the Ridgecrest study area so corridor widths, along-strike coordinates, across-strike distances, grid sizes, and circular radii are all computed in kilometers.
- Energy release should be computed from magnitude using a single consistent scalar seismic-energy relation for all domains; use log10(E[J]) = 1.5M + 4.8 unless catalog metadata specifies an alternative magnitude-energy calibration.
- Bayesian change-point analysis should be applied separately to rate and energy time series for All region, Region A, Region B, and the two near-mainshock circular domains; change points are diagnostics and should not by themselves be interpreted as causal proof.
- Keep the workflow in a small number of cohesive scripts: one primary geometry/assignment script, one temporal-statistics script, and one gridded-spatial-ordering script.
- Parallelization up to 64 cores is appropriate for repeated binning and per-cell statistics; merged scientific outputs must be validated as non-empty before treating a task as complete.

## Analysis Plan

### Task 1: Build fixed analysis geometry and assign events to domains
- Task description
  - Load catalog, mainshock table, and fault traces; construct the fixed Region A and Region B corridors, the Mw6.4 and Mw7.1 circular neighborhoods, and assign each catalog event to all relevant masks over the full pre-Mw 7.1 window.
- Required data sources
  - `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/TRACE_ridgecrest_relocated.csv`
  - `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/main_shock_events.csv`
  - `<REPO_ROOT>/examples/ridgecrest/data/faults/ridgecrest_surface_faults.json`
- Parameter selection strategy
  - Parse `event_time, latitude, longitude, depth_km, magnitude`.
  - Identify Mw 6.4 and Mw 7.1 rows from the 2-row mainshock table by magnitude.
  - Use a local metric projection centered near the catalog centroid or mean of the two mainshocks.
  - Region A centerline: start `(-117.635877, 35.555024)`, end `(-117.463113, 35.729199)`, strike `39.0°`, half-width `3.0 km`.
  - Region B centerline: start `(-117.735813, 35.897499)`, end `(-117.362520, 35.559488)`, strike `138.0°`, half-width `3.0 km`.
  - Circular neighborhoods: 10 km radius from Mw 6.4 and Mw 7.1 epicenters in projected coordinates.
  - For each event compute projected x/y, time relative to Mw 6.4 and Mw 7.1, distance to each mainshock, along-strike coordinate and perpendicular distance to each centerline, and boolean masks for Region A, Region B, Mw6.4-neighborhood, Mw7.1-neighborhood, and unassigned-to-corridors.
- Constraints
  - Corridor membership requires event projection to fall within finite centerline endpoints and within 3 km perpendicular distance.
  - Do not force mutual exclusivity between Region A and Region B unless overlap is explicitly diagnosed; preserve both flags.
  - Restrict all downstream tables to events at or before Mw 7.1 origin time.
- Key outputs
  - Event-level assignment table with projected coordinates, relative times, geometric coordinates, distances, and mask columns.
  - Compact summary CSV with assignment counts, unassigned fraction, median and 95th-percentile across-centerline distance, and along-strike range for Region A and Region B.
  - Diagnostic figures:
    - fixed-corridor assignment map with fault traces, centerlines, corridor boundaries, mainshocks, circles, and events colored by time since Mw 6.4
    - across-centerline distance distributions for Region A and Region B with 3 km threshold marked
    - along-strike coordinate distributions for Region A and Region B with finite endpoint limits marked
    - unassigned-event map

### Task 2: Quantify domain-scale seismic-rate and energy evolution before Mw 7.1
- Task description
  - Build 30-minute and hourly seismic rate and energy-release time series for All region, Region A, Region B, Mw6.4-neighborhood, and Mw7.1-neighborhood; extract onset and change diagnostics to test synchronous versus delayed activation.
- Required data sources
  - Event-level assignment table from Task 1
  - Mainshock origin times from `main_shock_events.csv`
- Parameter selection strategy
  - Create two parallel temporal resolutions: 30-minute bins and 1-hour bins.
  - Build for each domain:
    - event count per bin
    - cumulative event count
    - normalized cumulative count fraction
    - energy per bin from magnitude
    - cumulative energy
    - normalized cumulative energy fraction
  - Define diagnostic times for each domain after Mw 6.4:
    - first event time
    - first sustained activity time
    - strongest rate-change time
    - peak-rate time
  - Define “first sustained activity time” with an explicit reproducible rule, e.g., first bin after Mw 6.4 belonging to a run of at least 2–3 consecutive nonzero bins or exceeding a domain-specific baseline threshold estimated from the pre-Mw 6.4 segment.
  - Define strongest rate-change time as the bin of maximum positive first difference or the most probable positive Bayesian change-point jump, computed separately for rate and energy.
  - Apply Bayesian change-point detection independently to each domain and each metric (rate, energy); compare posterior change times between Region A and Region B.
  - Compute optional Region A minus Region B and Region A/Region B rate diagnostics on matched bins where denominators are nonzero.
- Constraints
  - Use the same time-bin edges for all domains to permit direct comparison.
  - When comparing rate curves across domains, distinguish raw counts from normalized fractions to avoid conflating timing with total productivity.
  - For ratios, mask bins with zero denominator and retain difference curves as the more stable default comparison.
  - Report uncertainty or sensitivity of change times across the two bin sizes rather than treating one binning as exact.
- Key outputs
  - Domain-by-bin table for 30-minute and hourly counts, rates, energy, cumulative counts, cumulative energy, normalized cumulative fractions.
  - Compact CSV summary for All region, Region A, and Region B containing first event time, first sustained activity time, strongest rate-change time, peak-rate time, cumulative count, and cumulative energy.
  - Additional diagnostic table for Mw6.4-neighborhood and Mw7.1-neighborhood with the same timing metrics.
  - Figures:
    - seismic-rate time series for All, A, and B with Mw 6.4 and Mw 7.1 vertical lines
    - rate-change and Bayesian change-point diagnostics for All, A, and B
    - cumulative counts for A and B, both raw and normalized
    - energy-release time series and cumulative energy for All, A, and B with change points
    - normalized cumulative energy fractions for A and B
    - near-mainshock neighborhood comparison showing rate, cumulative counts, normalized cumulative counts, and annotated diagnostic times
    - optional A-vs-B rate ratio or rate-difference through time
- Data dependency
  - Uses Task 1 assignment outputs directly; no independent re-reading of raw geometry should be needed.

### Task 3: Resolve spatial inhomogeneity and temporal ordering inside Region A and Region B
- Task description
  - Subdivide each fixed corridor into 0.5 km × 0.5 km cells, compute gridded seismicity statistics, and test whether post-Mw 6.4 activation within each corridor is spatially coherent, patchy, or directionally evolving along strike.
- Required data sources
  - Event-level assignment table from Task 1
  - Mainshock table from `main_shock_events.csv`
  - Fault traces JSON for map overlays
- Parameter selection strategy
  - Build local corridor-aligned coordinates for each assigned event: along-strike and across-strike.
  - Tessellate each corridor into 0.5 km × 0.5 km cells in aligned coordinates over the full finite centerline length and ±3 km width.
  - For each cell and for each temporal resolution (30-minute and hourly), compute:
    - event count per bin
    - cumulative count
    - energy per bin and cumulative energy
    - first activation time after Mw 6.4
    - peak-rate time
  - Also construct analogous 0.5 km gridding for the two 10 km circular neighborhoods for first-activation comparison.
  - Aggregate cells into along-strike bins, if needed, to stabilize heatmaps and trend diagnostics; use a bin width that is an integer multiple of the 0.5 km cell length.
  - For first-activation-versus-along-strike analysis, test for directional ordering using rank correlation or linear trend between along-strike coordinate and first activation time, while also flagging multimodal or patchy deviations.
  - Compare internal ordering relative to distance from Mw 6.4 and Mw 7.1 as a secondary diagnostic only.
- Constraints
  - Zero-count cells must be preserved explicitly for maps and heatmaps.
  - Use the same first-activation color scale for Region A and Region B, spanning 0 to Mw 7.1 occurrence time in hours since Mw 6.4.
  - Heatmaps should use time since Mw 6.4 on x-axis and along-strike distance on y-axis as the primary evidence.
  - Circular-neighborhood maps are diagnostic supplements and must not replace corridor-based interpretation.
- Key outputs
  - Cell-level first-activation table with cell center lon/lat, along-strike coordinate, across-strike coordinate, distance to Mw6.4, distance to Mw7.1, event count, first activation time, and peak-rate time.
  - Along-strike binned summary table for Region A and Region B with bin center, event count, first activation time, peak-rate time, and cumulative energy.
  - Figures:
    - cumulative seismicity-count maps for Region A and Region B with zero-count cells grey and corridor geometry overlaid
    - two-panel first-activation maps for Region A and Region B with common color scale and mainshocks labeled
    - two-panel first-activation maps for Mw6.4-neighborhood and Mw7.1-neighborhood with common color scale
    - time-versus-along-strike heatmaps for Region A and Region B
    - first-activation time versus along-strike distance for each region, with trend annotations indicating monotonic migration, delayed patch activation, or heterogeneous activation
    - optional secondary heatmaps versus distance to Mw 6.4 and Mw 7.1
- Data dependency
  - Uses Task 1 geometry/assignment outputs and Task 2 time-reference definitions for consistent post-Mw 6.4 timing.

### Task 4: Integrate triggering-mechanism diagnostics across regions
- Task description
  - Synthesize the comparative evidence needed to answer the three user questions: synchronicity versus temporal offset, systematic differences in triggering behavior between A and B, and internal spatial ordering within each region.
- Required data sources
  - Summary tables and figures from Tasks 2–3
- Parameter selection strategy
  - Compare Region A and Region B across matched diagnostics:
    - first event time and first sustained activity time
    - strongest rate-change time and peak-rate time
    - cumulative-count and cumulative-energy fraction trajectories
    - Bayesian change-point times in rate and energy
    - neighborhood onset comparison around Mw 6.4 and Mw 7.1
    - first-activation spatial gradients and along-strike ordering statistics
  - Use a decision matrix that classifies evidence into:
    - synchronous activation
    - delayed activation of Region B relative to Region A
    - similar total productivity but different onset timing
    - similar onset timing but different persistence/intensification
    - coherent rupture-parallel migration
    - patchy or multi-patch activation
- Constraints
  - Keep causal interpretation tied to observed temporal ordering and spatial organization; do not claim dynamic or static triggering mechanism uniquely without additional stress modeling.
  - Prioritize observational comparisons before any mechanistic speculation.
- Key outputs
  - Final merged summary tables for region-to-region and neighborhood-to-neighborhood comparison.
  - A compact machine-readable comparison table listing, for each domain, onset metrics, change-point metrics, peak metrics, total counts, total energy, and ordering-class labels.
  - Cross-reference between figure panels and diagnostic metrics so each inference is traceable to a plotted observable.

### Task script organization and execution flow
- Primary Script 1: Geometry and assignment
  - Execute Task 1 fully, including data loading, projection, region masks, geometric diagnostics, and assignment summary CSV.
  - Validate that both Region A and Region B have nonzero assigned event counts and that unassigned events are not dominating the key corridor between the two mainshocks.
- Primary Script 2: Temporal rate/energy statistics
  - Consume Task 1 event-assignment table.
  - Execute Task 2 fully for both 30-minute and hourly bins, including change-point detection, summary CSVs, and all time-series figures.
  - Validate non-empty domain time series and successful extraction of diagnostic times for A and B.
- Primary Script 3: Gridded spatial-ordering analysis
  - Consume Task 1 event-assignment table and Task 2 timing references.
  - Execute Task 3 fully, including corridor/circle grids, cell statistics, first-activation tables, along-strike summaries, and spatial figures.
  - Validate that cell-level outputs exist for both corridors and that first-activation maps contain activated cells before Mw 7.1 where expected.

