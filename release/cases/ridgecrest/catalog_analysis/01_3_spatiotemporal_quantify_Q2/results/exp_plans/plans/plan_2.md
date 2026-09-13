# Goal
Investigate whether and how the Mw 6.4 Ridgecrest mainshock triggered the Mw 7.1 rupture system by comparing spatiotemporal seismic-rate and energy-release evolution in two fixed fault-oriented corridors, and by resolving the internal spatial ordering of activation within each corridor and within near-mainshock neighborhoods during the interval from catalog start to the Mw 7.1 event.

## Planning Assumptions
- Use only the provided observational relocated catalog, mainshock table, and mapped surface-fault traces; no model data are required.
- The analysis window is fixed to `[catalog start time, Mw 7.1 origin time]`, where the Mw 7.1 origin time is read from `main_shock_events.csv`.
- Region definitions are fixed and must not be data-tuned:
  - Region A centerline: `(-117.635877, 35.555024)` to `(-117.463113, 35.729199)`, strike `39.0°`, half-width `3.0 km`.
  - Region B centerline: `(-117.735813, 35.897499)` to `(-117.362520, 35.559488)`, strike `138.0°`, half-width `3.0 km`.
  - Circular diagnostic domains: epicentral circles centered on the Mw 6.4 and Mw 7.1 hypocenters with radius `10 km` for analysis; map-diagnostic circle outlines should follow the user request exactly where stated.
- Events may belong to both a corridor and a circular domain; masks remain independent and non-exclusive.
- A local metric coordinate system must be constructed before corridor assignment, distance calculation, gridding, and circular-domain masking. Use a projection centered on the Ridgecrest study area or the catalog centroid so all horizontal distances are in kilometers.
- Energy release should be derived consistently from magnitude using one fixed scalar-energy relation for all domains and time bins; store both per-event energy and binned cumulative energy.
- Bayesian change-point analysis is required for both rate and energy time series. If multiple candidate implementations are considered during execution, use one consistent method across All/Region A/Region B/neighborhood series and report the same evidence metrics for every domain.
- Time-series products must be generated at both `30-minute` and `1-hour` resolution.
- Grid products inside corridors use fixed `0.5 km × 0.5 km` cells in local metric coordinates.
- Parallel execution up to 64 cores is appropriate for per-cell time-series construction and cellwise activation statistics; merged scientific outputs must be validated as non-empty for both Region A and Region B.
- Success evidence for each major script is not only completion, but also valid non-empty tables/figures for the required domains and time window.

## Analysis Plan

### Task 1 — Build fixed spatial masks and validate region geometry
- Task description
  - Load the relocated catalog, mainshock table, and fault traces; project all hypocenters and fault polylines into a local metric system; construct fixed corridor polygons, centerlines, along-strike/across-strike coordinates, and circular near-mainshock masks; assign every event to Region A, Region B, both/neither, and the two circular neighborhoods.
- Required data sources
  - `TRACE_ridgecrest_relocated.csv`
  - `main_shock_events.csv`
  - `ridgecrest_surface_faults.json`
- Parameter selection strategy
  - Parse catalog columns exactly as `event_time, latitude, longitude, depth_km, magnitude`.
  - Identify the Mw 6.4 and Mw 7.1 rows from the mainshock table by magnitude and use their event times and epicenters directly.
  - Use the user-specified corridor centerline endpoints, strikes, and 3 km half-width.
  - Compute along-strike coordinate by projection onto each centerline and across-strike distance by signed perpendicular offset.
  - Corridor membership requires projected along-strike coordinate within the finite centerline span and absolute across-strike distance ≤ 3 km.
  - Circular-domain membership requires horizontal epicentral distance ≤ 10 km from the corresponding mainshock.
- Constraints
  - Do not modify corridor width, orientation, or endpoints based on seismicity.
  - Keep All region as the full study catalog window, independent of corridor membership.
  - Preserve overlapping labels rather than forcing exclusive classes.
  - Record unassigned events explicitly.
- Key outputs
  - Event-level assignment table with projected coordinates, domain masks, along-strike and across-strike coordinates, and distances to both mainshocks.
  - Fixed-corridor assignment map with fault traces, centerlines, corridor outlines, mainshocks, event colors by time since Mw 6.4, and assignment classes.
  - Across-centerline distance distributions for Regions A and B with 3 km threshold marked.
  - Along-strike coordinate distributions for Regions A and B with centerline endpoints marked.
  - Unassigned-event diagnostic map.
  - Compact CSV summary with assignment counts, unassigned fraction, median and 95th-percentile across-centerline distance, and along-strike coordinate range for Regions A and B.

### Task 2 — Construct regional seismic-rate and energy-release time series and compare activation timing
- Task description
  - For All, Region A, Region B, Mw6.4-neighborhood, and Mw7.1-neighborhood, build 30-minute and 1-hour event-count and energy-release series from catalog start to Mw 7.1; derive cumulative and normalized cumulative measures; extract onset and peak diagnostics; compare timing offsets between domains.
- Required data sources
  - Event-level assignment table from Task 1
  - `main_shock_events.csv`
- Parameter selection strategy
  - Use fixed bins aligned to the Mw 6.4 origin time for post-mainshock diagnostics and to the catalog start for full-window series.
  - Compute per-bin seismic rate as event count per bin.
  - Compute per-event scalar energy from magnitude with one fixed relation, then aggregate to per-bin and cumulative energy.
  - Derive first event time after Mw 6.4, first sustained activity time, strongest rate-change time, and peak-rate time for each domain.
  - For first sustained activity time, use one explicit persistence rule applied identically across domains, such as the first time a nonzero or above-baseline activity level persists for a minimum number of consecutive bins; store the chosen rule in the output metadata.
  - Produce both raw cumulative counts/energy and normalized cumulative fractions.
  - Compute Region A vs Region B rate ratio or rate difference on bins where denominators are valid.
- Constraints
  - Use the same time bins and onset/peak definitions for all compared domains.
  - Keep neighborhood diagnostics separate from corridor diagnostics.
  - Do not let magnitude outliers dominate interpretation without also inspecting normalized cumulative energy fractions.
- Key outputs
  - 30-minute and hourly time-series tables for all five domains with counts, rates, energy, cumulative counts, cumulative energy, normalized cumulative counts, and normalized cumulative energy.
  - Seismic-rate comparison plots for All/Region A/Region B with Mw 6.4 and Mw 7.1 reference lines.
  - Cumulative count comparison plots for Region A and Region B, including raw and normalized fractions.
  - Energy-release and cumulative-energy plots for All/Region A/Region B.
  - Near-mainshock neighborhood comparison plots for Mw6.4-neighborhood and Mw7.1-neighborhood including rate, cumulative counts, normalized fractions, and timing diagnostics.
  - Optional Region A versus Region B rate-ratio or rate-difference figure.
  - Compact CSV summary with first event time, first sustained activity time, strongest rate-change time, peak-rate time, cumulative count, and cumulative energy for All/Region A/Region B.

### Task 3 — Detect Bayesian change points in rate and energy series
- Task description
  - Apply Bayesian change-point detection to regional and neighborhood rate and energy time series to identify statistically supported transitions in triggering behavior after the Mw 6.4 event and before Mw 7.1.
- Required data sources
  - Time-series outputs from Task 2
- Parameter selection strategy
  - Run change-point analysis separately for:
    - All, Region A, Region B on rate series
    - All, Region A, Region B on energy series
    - Mw6.4-neighborhood and Mw7.1-neighborhood on rate series, and optionally energy if event counts are sufficient
  - Use the same Bayesian model family and prior settings for all compared domains and for both 30-minute and hourly products unless data sparsity requires preferring one resolution as the primary interpretation scale.
  - Evaluate change points relative to the Mw 6.4 and Mw 7.1 origin times and rank them by posterior support or equivalent evidence score.
- Constraints
  - Do not interpret algorithmic candidate points without posterior support diagnostics.
  - Use a single primary time resolution for headline change-point comparisons if both resolutions produce different minor details; keep the second resolution as robustness support, not a separate conclusion stream.
  - Change-point outputs must be linked back to specific time-series segments and not reported as isolated timestamps.
- Key outputs
  - Change-point result tables for each domain and observable, including time, support metric, pre/post segment rates or energies, and temporal distance from Mw 6.4 and Mw 7.1.
  - Rate-change diagnostic plots with detected change points for All/Region A/Region B.
  - Energy-change diagnostic plots with detected change points for All/Region A/Region B.
  - Neighborhood change-point comparison plot/table focused on whether the Mw7.1-neighborhood activates later than the Mw6.4-neighborhood.

### Task 4 — Quantify spatial inhomogeneity and temporal ordering within Region A and Region B
- Task description
  - Subdivide each corridor into 0.5 km × 0.5 km cells; compute cellwise activation metrics and binned temporal evolution to determine whether post-Mw 6.4 triggering is spatially coherent, patchy, or directionally migrating along strike.
- Required data sources
  - Event-level assignment table from Task 1
  - `main_shock_events.csv`
  - Corridor geometries from Task 1
- Parameter selection strategy
  - Generate separate fixed grids clipped to Region A and Region B corridor polygons in local metric coordinates.
  - Assign each corridor event to a corridor cell.
  - Build 30-minute and hourly cellwise count/rate series from Mw 6.4 to Mw 7.1.
  - Define first activation time per cell as the first post-Mw 6.4 bin with at least one event; if desired, also store first sustained activation using the same persistence rule as Task 2.
  - Aggregate cells into along-strike bins for summary products; bin width should be chosen as an integer multiple of the 0.5 km cell size and held fixed within both regions.
  - For each cell and along-strike bin, compute event count, first activation time, peak-rate time, and cumulative energy.
- Constraints
  - Use the same grid spacing in both corridors.
  - Keep zero-count cells and display them distinctly rather than dropping them.
  - Along-strike heatmaps are the primary evidence for internal temporal ordering; secondary distance-to-mainshock summaries are optional only.
  - Validate that cell counts and activation tables are non-empty for both regions before considering the task complete.
- Key outputs
  - Cell-level table for Regions A and B with cell center lon/lat, projected x/y, along-strike coordinate, across-strike coordinate, distance to Mw 6.4, distance to Mw 7.1, event count, first activation time, peak-rate time, and cumulative energy.
  - Cumulative seismicity-count maps for Region A and Region B with centerlines and corridor boundaries overlaid; zero-count cells shown in grey.
  - Two-panel first-activation-time maps for Regions A and B using a shared color scale from 0 to Mw 7.1 occurrence time.
  - Time-versus-along-strike heatmaps for Regions A and B with light-grey zero-count background.
  - First-activation-time versus along-strike scatter/line summaries for Regions A and B.
  - Along-strike binned summary tables for each region including bin center, event count, first activation time, peak-rate time, and cumulative energy.

### Task 5 — Diagnose local activation around the two mainshock epicentral neighborhoods
- Task description
  - Build parallel spatial activation diagnostics within the two 10 km circular neighborhoods to compare local onset and spreading around the Mw 6.4 and Mw 7.1 epicentral areas.
- Required data sources
  - Event-level assignment table from Task 1
  - `main_shock_events.csv`
- Parameter selection strategy
  - Create 0.5 km × 0.5 km grid cells within each circular neighborhood using the same local metric system.
  - Compute cellwise first activation time after Mw 6.4 and cumulative counts through Mw 7.1.
  - Use the same color scale and timing reference as corridor first-activation maps.
  - Summarize whether the Mw7.1-neighborhood shows delayed initial activation, delayed broad activation, or only isolated early cells.
- Constraints
  - These neighborhood products are diagnostic comparisons and must not replace corridor-based conclusions.
  - Retain independent membership from corridor masks.
- Key outputs
  - Two-panel circular-neighborhood first-activation map for Mw6.4-neighborhood and Mw7.1-neighborhood with shared color scale.
  - Neighborhood cell-level first-activation table, compatible with the corridor cell table schema.
  - Diagnostic summary of first sustained activity time, strongest rate-change time, and peak-rate time for the two neighborhoods.

### Task 6 — Integrate evidence into trigger-mechanism tests focused on synchrony, offsets, and directional evolution
- Task description
  - Combine regional, neighborhood, and cellwise evidence into explicit tests of the user’s three scientific questions: synchrony versus temporal offset between Regions A and B, systematic differences in triggering behavior, and internal spatial ordering within each region.
- Required data sources
  - Outputs from Tasks 2–5
- Parameter selection strategy
  - Compare Region A and Region B using matched metrics:
    - first event time after Mw 6.4
    - first sustained activity time
    - strongest rate-change time
    - peak-rate time
    - dominant change-point times
    - cumulative count and cumulative energy trajectories
    - normalized cumulative count and energy fractions
    - spatial first-activation gradients and along-strike heatmap patterns
  - Quantify temporal offsets as direct time differences between matched metrics for Region A and Region B, and separately for the two circular neighborhoods.
  - Assess directional evolution within each corridor by fitting or testing monotonic trends between first activation time and along-strike coordinate, while also reporting departures such as multi-patch activation or reversed ordering.
- Constraints
  - Use corridor-based evidence as primary for fault-system comparison; use neighborhood evidence as local corroboration.
  - Distinguish true temporal offsets from simple differences in total event productivity by always pairing raw and normalized cumulative diagnostics.
  - If patterns differ between 30-minute and hourly products, report the coarser-scale stable pattern as primary and the finer-scale difference as secondary diagnostic evidence.
- Key outputs
  - Final machine-readable comparison table of Region A vs Region B and Mw6.4-neighborhood vs Mw7.1-neighborhood timing offsets and triggering metrics.
  - Ranked diagnostic indicators of whether activation is synchronous, delayed, front-propagating, patchy, or spatially heterogeneous in each region.
  - Cross-task validation checks showing consistency between map-based, time-series-based, and change-point-based interpretations.

### Task 7 — Script organization and execution flow
- Task description
  - Organize the workflow into a small number of cohesive scripts with clear dependencies and validation checkpoints.
- Required data sources
  - All sources above; downstream tasks depend on upstream outputs.
- Parameter selection strategy
  - Script 1: geometry and assignments
    - Load data, projection, corridor/circle construction, event assignments, geometry diagnostics, assignment summary CSV.
  - Script 2: regional time series and Bayesian change points
    - Build 30-minute/hourly count and energy series for all domains, cumulative/normalized products, timing metrics, change-point extraction, time-series summary CSVs and figures.
  - Script 3: cellwise corridor and neighborhood activation analysis
    - Build 0.5 km grids, cellwise rates, first-activation tables, along-strike summaries, maps, and heatmaps.
  - Script 4: integration and comparison export
    - Merge outputs from Scripts 2 and 3 into final comparison tables and consistency checks.
- Constraints
  - Keep each script scientifically complete for its stage, including immediate validation of outputs.
  - Use parallel computation in Scripts 2 and 3 for per-domain/per-cell operations.
  - Progress logging is required for long-running binning and per-cell computations.
- Key outputs
  - Validated intermediate tables reusable across downstream steps.
  - Non-empty final CSV summaries and all requested diagnostic figures.