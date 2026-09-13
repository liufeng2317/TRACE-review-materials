# Goal
Investigate whether and how the Mw 6.4 Ridgecrest mainshock triggered the Mw 7.1 event by comparing fault-oriented Region A and Region B, quantifying temporal offsets and differences in seismic-rate/energy evolution, and resolving the internal spatial ordering of activation within each region before the Mw 7.1 mainshock.

## Planning Assumptions
- Use only the provided observation-based relocated catalog, mainshock table, and mapped surface-fault traces; no model data are needed.
- Analysis time window is fixed to `[catalog start time, Mw 7.1 origin time]`, with Mw 6.4 as the triggering reference time for all “time since mainshock” products.
- Region definitions are fixed and must not be re-optimized from the seismicity:
  - Region A corridor: strike 39.0°, centerline from `(-117.635877, 35.555024)` to `(-117.463113, 35.729199)`, half-width 3.0 km.
  - Region B corridor: strike 138.0°, centerline from `(-117.735813, 35.897499)` to `(-117.362520, 35.559488)`, half-width 3.0 km.
- Near-mainshock diagnostic domains are independent masks, not mutually exclusive classes:
  - Mw6.4-neighborhood: 10 km radius centered on Mw 6.4 hypocenter epicenter.
  - Mw7.1-neighborhood: 10 km radius centered on Mw 7.1 hypocenter epicenter.
- Use a single local metric coordinate system for corridor assignment, circular-domain definition, along-/across-strike coordinates, grid construction, and map products; keep lon/lat copies for export and labeling.
- Event assignment to Region A/B must use finite corridor geometry: event projection falls between centerline endpoints and perpendicular distance is within 3.0 km.
- Seismic-rate products must be built at both 30-minute and 1-hour resolution for All region, Region A, Region B, Mw6.4-neighborhood, Mw7.1-neighborhood, and corridor/grid subdivisions.
- Energy release should be computed consistently from magnitude using a standard scalar radiated-energy proxy, e.g. `log10(E[J]) = 1.5*M + 4.8`; use the same conversion everywhere and report it explicitly in outputs.
- Bayesian change-point detection is applied to post-Mw 6.4 rate and energy time series to identify activation onsets, sustained changes, and strongest transitions prior to Mw 7.1; pre-Mw 6.4 data remain available for context plots but triggering interpretation focuses on the post-Mw 6.4 interval.
- Zero-event bins/cells are scientifically meaningful and must be retained in rate grids, cumulative products, and heatmaps.
- Keep the workflow in a small number of cohesive task scripts with explicit intermediate CSV/NPZ/Parquet products so each major analysis stage can be rerun independently.

## Analysis Plan

### Task 1 — Build the unified event table, fixed-region geometry, and diagnostic assignments
- Task description
  - Load the relocated catalog, mainshock table, and fault polylines; parse times; project all epicenters to a local metric system; assign events to Region A, Region B, Mw6.4-neighborhood, Mw7.1-neighborhood, and All region; derive along-strike and across-strike coordinates for corridor-assigned events.
- Required data sources
  - `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/TRACE_ridgecrest_relocated.csv`
  - `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/main_shock_events.csv`
  - `<REPO_ROOT>/examples/ridgecrest/data/faults/ridgecrest_surface_faults.json`
- Parameter selection strategy
  - Read `event_time, latitude, longitude, depth_km, magnitude`.
  - Identify the Mw 6.4 and Mw 7.1 rows from the 2-row mainshock file by magnitude.
  - Use the full catalog start time as analysis start; truncate all derived products at Mw 7.1 origin time inclusive/exclusive by a single documented rule.
  - Construct Region A/B centerlines directly from the user-provided endpoints; define finite-width corridor polygons using 3.0 km half-width.
  - Compute for each event:
    - projected `x_km, y_km`
    - `time_since_mw64_hr`
    - Region A/B boolean membership
    - Mw6.4-/Mw7.1-neighborhood boolean membership using horizontal epicentral distance
    - along-strike distance from corridor start and signed across-strike distance for each corridor
    - nearest/main assigned corridor label only for map symbology, while retaining independent booleans
- Constraints
  - Do not tune corridor width, orientation, or endpoints from the data.
  - Keep corridor and circle memberships independent; overlapping masks are allowed.
  - Preserve events outside both corridors as unassigned for diagnostics.
  - Use the same metric projection in all later tasks.
- Key outputs
  - Unified event table with coordinates, times, assignments, distances, and derived metrics.
  - Region geometry table/polygon representation for Region A, Region B, and the two circles.
  - Assignment summary CSV with counts, unassigned fraction, median and 95th-percentile absolute across-centerline distance, and along-strike coordinate range for Region A and Region B.

### Task 2 — Region-definition diagnostics and map validation
- Task description
  - Validate that the fixed corridors and circles capture the intended seismicity and that unassigned events are not concentrated in the key Mw 6.4-to-Mw 7.1 linkage zone.
- Required data sources
  - Unified event table and geometry products from Task 1
  - Fault polylines from the JSON source
- Parameter selection strategy
  - Color events by time since Mw 6.4 for post-mainshock emphasis; optionally mute pre-Mw 6.4 events.
  - Use separate symbols/colors for Region A, Region B, and unassigned events; overlay both mainshocks.
  - Use absolute across-centerline distance histograms/densities for assigned events in each corridor.
  - Use along-strike coordinate distributions clipped to finite centerline span.
- Constraints
  - Corridor diagnostic circles in figures should follow the user’s requested visualization text exactly; if the figure request conflicts with the 10 km analysis definition, note in the task log and use the 10 km analytical circles in all calculations, with any 5 km boundary only as an auxiliary visual if explicitly needed.
  - Unassigned-event diagnostics must be plotted separately from assigned-event maps.
- Key outputs
  - Fixed-corridor assignment map with fault traces, centerlines, corridor boundaries, mainshocks, and circle boundaries.
  - Across-centerline distance distribution plots for Region A and Region B with 3 km threshold marked.
  - Along-strike coordinate distribution plots for Region A and Region B with endpoint limits marked.
  - Unassigned-event diagnostic map.
  - Short validation table/log stating whether assigned clouds are well covered and whether unassigned events cluster inside the inter-mainshock corridor.

### Task 3 — Construct regional seismic-rate and energy-release time series
- Task description
  - Build 30-minute and hourly event-count rates, cumulative counts, energy-release rates, cumulative energy, and normalized cumulative fractions for All region, Region A, Region B, Mw6.4-neighborhood, and Mw7.1-neighborhood.
- Required data sources
  - Unified event table from Task 1
- Parameter selection strategy
  - Use fixed bin widths of 30 minutes and 1 hour from catalog start to Mw 7.1.
  - For each domain and bin, compute:
    - event count
    - rate normalized by bin duration
    - summed energy release from event magnitudes
    - cumulative count and cumulative energy
    - normalized cumulative count fraction and normalized cumulative energy fraction over the post-Mw 6.4 interval
  - Derive post-Mw 6.4 timing metrics:
    - first event time
    - first sustained activity time using a documented persistence rule, e.g. first bin after Mw 6.4 that initiates a run of nonzero or above-baseline bins of minimum duration
    - peak-rate time
    - strongest rate-change time from differenced/smoothed series or change-point posterior maximum
- Constraints
  - Keep both raw and normalized cumulative products; do not replace one with the other.
  - Retain zero-count bins explicitly.
  - Apply the same energy conversion and timing rules to all domains.
- Key outputs
  - Domain-by-bin time-series table for 30-minute and hourly resolutions.
  - Summary CSV with first event time, first sustained activity time, strongest rate-change time, peak-rate time, cumulative count, and cumulative energy for All region, Region A, and Region B.
  - Comparable neighborhood summary table for Mw6.4- and Mw7.1-neighborhoods.

### Task 4 — Extract Bayesian change points from rate and energy series
- Task description
  - Detect statistically significant post-Mw 6.4 changes in seismic rate and energy release to test whether Region B and the Mw7.1-neighborhood activate later or differently than Region A and the Mw6.4-neighborhood.
- Required data sources
  - Regional and neighborhood time-series products from Task 3
- Parameter selection strategy
  - Run separate change-point analyses for:
    - All region count/rate series
    - Region A count/rate and energy series
    - Region B count/rate and energy series
    - Mw6.4-neighborhood and Mw7.1-neighborhood count/rate series
  - Evaluate both 30-minute and hourly products; use one as primary and the other as robustness cross-check.
  - Record posterior/score-ranked change times, segment means, and uncertainty intervals where supported.
  - Compare Region A vs Region B change-point timing and the neighborhood pair timing relative to Mw 6.4 and Mw 7.1.
- Constraints
  - Triggering interpretation must focus on post-Mw 6.4 segments only.
  - Change-point output must be non-empty and mapped back to physical time; diagnostic-only failures are not acceptable as final results.
  - Use the same method and comparable priors/penalties across domains so offsets are interpretable.
- Key outputs
  - Change-point tables for rate and energy series with times, confidence/score, and pre/post segment levels.
  - Derived comparison table of temporal offsets between Region A and Region B, and between Mw6.4- and Mw7.1-neighborhoods.
  - Evidence flags for “synchronous,” “lagged,” or “multi-stage” activation patterns based on objective timing thresholds defined before interpretation.

### Task 5 — Plot regional and near-mainshock temporal diagnostics
- Task description
  - Produce the core figures for comparing activation timing, growth style, and energy accumulation between regions and neighborhoods.
- Required data sources
  - Task 3 time-series outputs
  - Task 4 change-point outputs
- Parameter selection strategy
  - Plot on common time axes referenced to Mw 6.4 and annotated with both mainshocks.
  - Required figure families:
    - seismic-rate time series for All region, Region A, Region B
    - change-point/rate-change diagnostics for All region, Region A, Region B
    - cumulative counts for Region A and Region B with raw and normalized cumulative fractions
    - energy-release time series and cumulative energy for All region, Region A, Region B with change points marked
    - normalized cumulative energy fractions for Region A and Region B
    - neighborhood comparison plots for Mw6.4- and Mw7.1-neighborhoods: rate, cumulative counts, normalized cumulative fractions, and annotated first sustained activity / strongest rate change / peak rate
    - optional Region A vs Region B rate ratio or rate difference through time
  - Use the same post-Mw 6.4 temporal origin across all panels.
- Constraints
  - Raw cumulative counts and normalized cumulative fractions must appear together to separate timing from total productivity.
  - Energy plots must not be interpreted alone; pair with normalized cumulative energy fractions because a few larger events may dominate totals.
  - Optional ratio/difference diagnostics must handle zero denominators explicitly.
- Key outputs
  - Figure set for regional time-series comparison.
  - Figure set for neighborhood activation-lag diagnostics.
  - Compact machine-readable panel-metric table for all plotted characteristic times.

### Task 6 — Build 0.5 km corridor grids and cell-level seismicity statistics
- Task description
  - Discretize Region A and Region B into 0.5 km × 0.5 km cells in corridor coordinates and compute cell-level counts, rates, energies, activation times, and distances to both mainshocks.
- Required data sources
  - Unified event table and corridor geometry from Task 1
- Parameter selection strategy
  - Define each corridor grid in local metric coordinates or corridor-aligned coordinates with 0.5 km spacing.
  - For every cell in Region A and Region B, compute:
    - total event count to Mw 7.1
    - 30-minute and hourly count/rate time series
    - first activation time after Mw 6.4
    - peak-rate time
    - cumulative energy
    - cell-center lon/lat and projected coordinates
    - along-strike and across-strike coordinates
    - distance to Mw 6.4 epicenter and Mw 7.1 epicenter
  - Build analogous 0.5 km cell products for the two 10 km circular neighborhoods for the local first-activation comparison.
- Constraints
  - Include zero-count cells inside each fixed corridor/circle and preserve them in maps.
  - Corridor cells must respect fixed finite centerline bounds and fixed half-width.
  - Use parallel computation for per-cell time-series construction when beneficial.
- Key outputs
  - Cell-level statistics table for Region A and Region B.
  - Cell-level first-activation table containing the user-requested columns: cell center lon/lat, along-strike coordinate, across-strike coordinate, distance to Mw6.4, distance to Mw7.1, event count, first activation time.
  - Equivalent neighborhood cell table for the two circular domains.

### Task 7 — Resolve internal spatial ordering and inhomogeneity within Region A and Region B
- Task description
  - Diagnose whether activation inside each corridor is spatially coherent, patchy, or directionally evolving using maps, heatmaps, and along-strike summaries.
- Required data sources
  - Cell-level products from Task 6
  - Mainshock coordinates and corridor geometry from Task 1
- Parameter selection strategy
  - Required map products:
    - cumulative seismicity-count maps for Region A and Region B with zero-count cells shown in grey
    - first-activation-time maps for Region A and Region B using common color scale from 0 to Mw 7.1 time
    - two-panel first-activation maps for Mw6.4- and Mw7.1-neighborhoods with the same color scale
  - Required ordering diagnostics:
    - time-versus-along-strike heatmaps for Region A and Region B as primary evidence
    - first-activation time versus along-strike distance scatter/line plots
    - along-strike binned summaries with bin center, event count, first activation time, peak-rate time, cumulative energy
  - For along-strike binning, use a fixed bin width that is an integer multiple of the 0.5 km cell size and yields enough occupancy for stable summaries; choose once and apply to both regions.
  - Quantify spatial ordering by fitting/reporting simple diagnostics:
    - correlation or robust slope between first-activation time and along-strike distance
    - piecewise or monotonicity checks to distinguish migration from delayed patch activation
    - heterogeneity statistics such as interquartile range of activation times across neighboring bins
- Constraints
  - Along-strike heatmaps are primary; distance-to-mainshock secondary heatmaps are optional supplements only.
  - Region A and Region B first-activation maps must share the same time color scale.
  - Interpretation must distinguish true directional trend from sparse occupancy or isolated cells.
- Key outputs
  - Corridor count maps and first-activation maps.
  - Two-panel circular-neighborhood first-activation comparison.
  - Time-versus-along-strike heatmaps for Region A and Region B.
  - First-activation-versus-along-strike plots.
  - Along-strike binned summary tables for Region A and Region B.

### Task 8 — Integrate comparative triggering diagnostics across domains
- Task description
  - Synthesize objective metrics across regional, neighborhood, and cell-level analyses to answer the three scientific questions: synchrony vs temporal offset, systematic rate/triggering differences, and internal ordering of activation.
- Required data sources
  - Outputs from Tasks 3–7
- Parameter selection strategy
  - Compare Region A vs Region B using:
    - onset lag from first event and first sustained activity
    - strongest rate-change lag
    - peak-rate lag
    - cumulative-count and cumulative-energy fractions at matched times after Mw 6.4
    - change-point segment levels and growth contrasts
  - Compare Mw6.4- vs Mw7.1-neighborhoods using the same timing metrics to test delayed activation near the future Mw 7.1 area.
  - Compare internal ordering metrics:
    - fraction of cells activated within early windows after Mw 6.4
    - activation-time spread within each corridor
    - evidence for monotonic migration versus patchy activation
- Constraints
  - Base final scientific inference on convergent evidence from counts, energy, change points, and spatial ordering; no single metric should dominate.
  - Keep comparisons restricted to the pre-Mw 7.1 window.
- Key outputs
  - Final comparative metrics table spanning All region, Region A, Region B, Mw6.4-neighborhood, and Mw7.1-neighborhood.
  - Classification-ready summary fields indicating synchronous/lagged activation, stronger/weaker triggering response, and coherent/directional/heterogeneous internal activation.

