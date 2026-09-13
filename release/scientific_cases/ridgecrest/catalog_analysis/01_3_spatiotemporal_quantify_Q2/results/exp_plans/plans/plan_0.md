# Goal
Investigate whether and how the Mw 6.4 Ridgecrest mainshock triggered the Mw 7.1 earthquake by comparing fixed fault-oriented Region A and Region B, quantifying their relative activation timing and seismic-rate/energy evolution, and resolving the internal spatial ordering of triggering within each region before the Mw 7.1 occurrence.

## Planning Assumptions
- Use only the provided observational catalog, mainshock table, and mapped surface-fault traces; no model-generated seismicity is needed.
- Analysis time window is fixed to `[catalog start time, Mw 7.1 origin time]`, with all post-Mw 6.4 triggering diagnostics referenced to time since the Mw 6.4 mainshock.
- The two fixed fault-oriented corridors are user-prescribed and must not be re-estimated from the data:
  - Region A centerline from `(-117.635877, 35.555024)` to `(-117.463113, 35.729199)`, strike `39.0°`, total width `6.0 km`.
  - Region B centerline from `(-117.735813, 35.897499)` to `(-117.362520, 35.559488)`, strike `138.0°`, total width `6.0 km`.
- Near-mainshock neighborhoods are independent binary masks derived from 10 km epicentral-radius circles centered on the Mw 6.4 and Mw 7.1 mainshocks loaded from `main_shock_events.csv`; they are not exclusive classes relative to Region A/Region B.
- Region-definition diagnostics should be computed in a local metric coordinate system centered on the study area or mainshock pair, so corridor width, along-strike distance, across-strike distance, and 10 km circle radii are all evaluated in kilometers.
- The user’s visualization bullet mentions 5 km circles while the formal domain definition specifies 10 km circles; use 10 km for analysis and add a verification note in the diagnostics that figure annotations must match the analysis radius.
- Seismic rate must be computed for both 30-minute and 1-hour bins for All region, Region A, Region B, and the two near-mainshock neighborhoods.
- Energy release should be derived from magnitude using a standard scalar seismic-energy proxy such as `log10(E[J]) = 1.5*M + 4.8`; use the same formula consistently for all domains and summaries.
- Bayesian change-point extraction is required on both rate and energy time series; if multiple Bayesian implementations are available, prefer one method applied consistently across domains and resolutions rather than mixing methods. Success evidence is non-empty change-point tables and interpretable overlays on the time series.
- Grid analyses are restricted to 0.5 km × 0.5 km cells inside the fixed corridors for Region A and Region B; zero-count cells must be retained in maps/heatmaps.
- Parallel execution up to 64 cores should be applied only to heavy embarrassingly parallel steps such as per-cell binning and first-activation calculations; merged outputs must be validated as non-empty before the step is considered complete.

## Analysis Plan
### Task 1 — Build the fixed geometry framework and event assignment products
- Task description
  - Load the relocated catalog, mainshock table, and fault traces; parse event times; determine catalog start and Mw 7.1 cutoff time from the mainshock table.
  - Construct a local metric projection for the Ridgecrest study area.
  - Build fixed Region A and Region B corridor polygons from the prescribed centerlines and 3 km half-width.
  - Compute for every event: projected coordinates, time since Mw 6.4, time to Mw 7.1, along-strike and across-strike coordinates relative to Region A and Region B centerlines, binary membership in Region A and Region B, epicentral distance to Mw 6.4 and Mw 7.1, and binary membership in the two 10 km near-mainshock neighborhoods.
  - Derive assignment diagnostics and export compact geometry-summary tables needed by later tasks.
- Required data sources
  - `TRACE_ridgecrest_relocated.csv`
  - `main_shock_events.csv`
  - `ridgecrest_surface_faults.json`
- Parameter selection strategy
  - Use all catalog events with `event_time <= Mw 7.1 origin time`.
  - Use the two-row mainshock file to identify the Mw 6.4 and Mw 7.1 reference events by magnitude and event time.
  - Define corridor membership by finite line-segment geometry: event projection must fall between segment endpoints in along-strike coordinate and within `|across-strike| <= 3.0 km`.
  - Keep Region A and Region B assignments independent; if overlap occurs, preserve both flags and report the overlap count explicitly.
  - Use 10 km radii for the two circular diagnostic neighborhoods and preserve these labels independently of corridor labels.
- Constraints
  - Do not re-fit centerlines, rotate strikes, or expand corridor widths from the data.
  - Use local metric distances for all geometric inclusion tests and distance summaries.
  - Keep unassigned events as an explicit diagnostic class rather than discarding them.
  - Validate that mainshocks fall in the expected projected study area and that the corridor endpoints align with the user-given strike directions.
- Key outputs
  - Event-level enriched table with geometry/time fields and binary masks for All/Region A/Region B/Mw6.4-neighborhood/Mw7.1-neighborhood.
  - Compact CSV summary of assignment counts, overlap count, unassigned fraction, median and 95th-percentile across-centerline distance, and along-strike coordinate range for Region A and Region B.
  - Fixed-corridor assignment map with fault traces, centerlines, corridor boundaries, 10 km neighborhood circles, mainshocks, events colored by time since Mw 6.4, and assignment classes.
  - Across-centerline distance distributions for Region A and Region B with the 3 km threshold marked.
  - Along-strike coordinate distributions for Region A and Region B with centerline endpoint limits marked.
  - Unassigned-event diagnostic map showing whether missed events cluster inside or outside the key Mw 6.4–Mw 7.1 corridor.

### Task 2 — Quantify regional seismic-rate and energy evolution and extract change points
- Task description
  - From the enriched event table, build 30-minute and 1-hour binned time series for All region, Region A, Region B, Mw6.4-neighborhood, and Mw7.1-neighborhood from catalog start to Mw 7.1.
  - For each domain/bin size, compute event count rate, cumulative counts, total energy per bin, cumulative energy, normalized cumulative count fraction, and normalized cumulative energy fraction.
  - For post-Mw 6.4 diagnostics, derive first event time, first sustained activity time, strongest rate-change time, and peak-rate time.
  - Apply Bayesian change-point detection to both rate and energy series and compare the timing/sequence of inferred changes among All region, Region A, Region B, and the two near-mainshock neighborhoods.
  - Produce domain-comparison summaries focused on whether Region A and Region B activate synchronously or with systematic delay and whether the Mw7.1-neighborhood shows delayed activation relative to the Mw6.4-neighborhood.
- Required data sources
  - Event-level enriched table from Task 1
  - `main_shock_events.csv` for vertical reference times and neighborhood labels
- Parameter selection strategy
  - Use both 30-minute and 1-hour bins throughout; maintain a common set of bin edges across all domains for direct comparison.
  - Compute energy consistently from magnitude for every event before binning.
  - Define first event time as the first non-zero post-Mw 6.4 bin or event timestamp within the domain.
  - Define first sustained activity time using a fixed persistence rule chosen before analysis, such as the first time a domain remains active for at least a minimum number of consecutive bins; report the chosen persistence rule in the output metadata.
  - Define strongest rate-change time from either the largest positive first difference in binned rate or the most prominent Bayesian rate change after Mw 6.4; keep one rule consistent across all domains.
  - Define peak-rate time as the time of the maximum post-Mw 6.4 binned rate; if ties occur, use the earliest peak.
  - Optional rate-ratio diagnostics should use a small additive offset only if needed to avoid division by zero; report the offset if used.
- Constraints
  - Do not mix bin resolutions within a single comparative figure.
  - Do not interpret energy and count curves interchangeably; report both because large events can dominate energy.
  - Change-point analysis must be run separately for count-rate and energy series, with outputs clearly labeled by statistic and bin size.
  - Near-mainshock neighborhoods are diagnostics only and must not replace the corridor-based comparison.
- Key outputs
  - Time-series tables for 30-minute and 1-hour rate/count/energy metrics for each domain.
  - Change-point tables for rate and energy series, including domain, bin size, change-point time, and a measure of change magnitude or posterior support if available.
  - Multi-domain seismic-rate time series with Mw 6.4 and Mw 7.1 reference lines.
  - Rate-change diagnostic plots with detected change points for All region, Region A, and Region B.
  - Paired cumulative count plots for Region A and Region B showing both raw cumulative counts and normalized cumulative fractions.
  - Energy-release and cumulative-energy plots for All region, Region A, and Region B with change points marked.
  - Near-mainshock neighborhood comparison figure showing rate, cumulative counts, normalized cumulative fractions, first sustained activity time, strongest rate-change time, and peak-rate time for the Mw6.4 and Mw7.1 neighborhoods.
  - Optional Region A versus Region B rate-ratio or rate-difference diagnostic through time.
  - Compact CSV summary of first event time, first sustained activity time, strongest rate-change time, peak-rate time, cumulative count, and cumulative energy for All region, Region A, and Region B.

### Task 3 — Resolve spatial inhomogeneity and temporal ordering inside Region A and Region B
- Task description
  - Subdivide Region A and Region B corridor interiors into 0.5 km × 0.5 km cells in local metric coordinates.
  - Assign events to cells and compute per-cell 30-minute and 1-hour counts/rates, cumulative count, cumulative energy, first activation time after Mw 6.4, and peak-rate time.
  - Build the same first-activation products for the two 10 km circular near-mainshock neighborhoods as secondary local diagnostics.
  - Aggregate cells into along-strike bins for each corridor and summarize event count, first activation time, peak-rate time, and cumulative energy versus along-strike position.
  - Use heatmaps and first-activation-versus-distance diagnostics to test whether activation is coherent, patchy, or directionally evolving.
- Required data sources
  - Event-level enriched table from Task 1
  - Corridor geometry from Task 1
  - `main_shock_events.csv`
  - `ridgecrest_surface_faults.json` for map overlays where needed
- Parameter selection strategy
  - Create corridor grids in projected coordinates, clipping cells to the fixed finite corridor extents.
  - Preserve all cells, including zero-count cells, in cumulative maps and time-versus-along-strike heatmaps.
  - Define first activation time per cell as the first post-Mw 6.4 event time or first non-zero bin center; use one definition consistently and record it in metadata.
  - Use common color scales between Region A and Region B first-activation maps, spanning `0` to `(Mw 7.1 time - Mw 6.4 time)` in hours.
  - For along-strike summaries, bin using either the native 0.5 km grid spacing or an explicitly chosen coarser spacing if smoothing is needed; preserve the original cell-level table regardless.
  - For neighborhood first-activation maps, use the same cell size and same time color scale as the corridor maps for direct comparison.
- Constraints
  - Primary internal-ordering evidence must be time-versus-along-strike heatmaps and first-activation versus along-strike diagnostics; distance-to-mainshock heatmaps are secondary only.
  - Do not omit zero-count cells from spatial maps, because they constrain whether activation is spatially coherent.
  - Corridor overlays, mainshock markers, and cell metrics must all be in the same local metric frame for map products.
  - Parallelize per-cell computations if needed, but merged cell tables for Region A and Region B must be validated as complete and non-empty.
- Key outputs
  - Cell-level table for Region A and Region B with cell center lon/lat, projected x/y, along-strike coordinate, across-strike coordinate, distance to Mw 6.4, distance to Mw 7.1, event count, cumulative energy, first activation time, and peak-rate time.
  - Cumulative seismicity-count maps for Region A and Region B with zero-count cells in grey and corridor geometry overlaid.
  - Two-panel first-activation-time maps for Region A and Region B using a common time scale.
  - Two-panel first-activation-time maps for the Mw6.4-neighborhood and Mw7.1-neighborhood using the same common time scale.
  - Time-versus-along-strike heatmaps for Region A and Region B, for both 30-minute and 1-hour representations if both are retained.
  - First-activation time versus along-strike plots for Region A and Region B, used to assess monotonic migration versus delayed-patch or heterogeneous activation.
  - Along-strike binned summary tables for each region including bin center, event count, first activation time, peak-rate time, and cumulative energy.

### Task dependencies and execution flow
- Task 1 is the prerequisite for all later tasks because it defines the projection, event masks, geometric diagnostics, and assignment tables.
- Task 2 consumes the Task 1 enriched event table and produces regional temporal metrics and change-point products.
- Task 3 consumes the Task 1 enriched event table and corridor geometry, and may optionally reuse Task 2 time-bin definitions to keep heatmaps aligned with the regional time-series analysis.
- Final scientific interpretation should compare:
  - Region A vs Region B onset timing and sustained activation after Mw 6.4,
  - rate and energy change-point ordering relative to Mw 7.1,
  - Mw6.4-neighborhood vs Mw7.1-neighborhood local activation lag,
  - and whether within-region first-activation patterns are synchronous, patchy, or directionally progressive.