# Goal
Quantify and visualize the spatiotemporal activation of the Ridgecrest sequence between the Mw 6.4 and Mw 7.1 mainshocks, with emphasis on whether activation is synchronous, staged/cascade-like, or geometrically complex along mapped fault directions and segments.

## Planning Assumptions
- Use only the provided observational datasets: relocated earthquake catalog, two-event mainshock reference table, and mapped surface-fault polylines.
- The primary analysis window is strictly from the Mw 6.4 origin time to the Mw 7.1 origin time, using the two-row mainshock table to identify these endpoints and epicentral overlays.
- Study-region bounds are derived from all fault coordinates, then expanded by 5 km in longitude/latitude space after converting to a local projected coordinate system; all distance-based operations should be done in projected kilometers, not degrees.
- The user requested 1 km spatial grids, 30-minute temporal bins, nearest-fault association within 3 km, and a fixed fault-segment activation threshold of 10 events/hour; these should be treated as task parameters, not tuned.
- Because 30-minute bins are used, a threshold of 10 events/hour corresponds to at least 5 events in a 30-minute bin.
- “Sustained increase” for grid-cell onset should be implemented reproducibly as a rule-based criterion rather than visual judgment; onset must not be assigned from a single isolated spike without persistence evidence.
- Fault segmentation and event-to-segment distance calculations are computationally intensive; use parallel execution for per-segment/per-event calculations and preserve logs/progress evidence.
- No model data or synthetic simulations are needed because the request is fully addressable with observations.

## Analysis Plan

### Task 1 — Build the common analysis domain and event subset
- Task description:
  - Load the catalog, mainshock reference table, and surface-fault polylines.
  - Parse event times, identify Mw 6.4 and Mw 7.1 events from the reference table, define the analysis window, project all coordinates to a local Cartesian system, build the fault-based expanded study region, and subset earthquakes accordingly.
- Required data sources:
  - `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/TRACE_ridgecrest_relocated.csv`
  - `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/main_shock_events.csv`
  - `<REPO_ROOT>/examples/ridgecrest/data/faults/ridgecrest_surface_faults.json`
- Parameter selection strategy:
  - Select the Mw 6.4 and Mw 7.1 rows from the two-event table by magnitude.
  - Use `event_time` interval [Mw 6.4, Mw 7.1].
  - Convert lon/lat to a local projected CRS centered on the Ridgecrest fault domain.
  - Compute the min/max fault extent in projected coordinates and expand by 5 km on each side.
  - Keep only catalog events inside both the time window and expanded fault-domain box.
- Constraints:
  - Preserve original event IDs by row index if no explicit event identifier exists.
  - Validate that both mainshocks fall inside the projected study region.
  - Record the number of total catalog events, time-window events, and final study-region events.
- Key outputs:
  - Cleaned event table for the Mw 6.4–Mw 7.1 interval
  - Projected fault polyline table
  - Study-region bounds table
  - QC summary table with event counts and time limits
  - Base map showing faults, expanded analysis box, and both mainshocks

### Task 2 — Grid-based onset-time mapping of local seismic activation
- Task description:
  - Discretize the expanded study region into 1 km × 1 km cells, build 30-minute local seismicity-rate series for each populated cell, define a reproducible onset time from sustained rate increase, and map onset time relative to the Mw 6.4 mainshock.
- Required data sources:
  - Time-window, study-region event subset from Task 1
  - Projected faults and mainshock epicenters from Task 1
- Parameter selection strategy:
  - Create a regular 1 km grid covering the expanded region.
  - Count events per 30-minute bin for each cell.
  - Convert counts to rate in events/hour if needed for comparability.
  - Define candidate onset as the first 30-minute bin meeting a sustained-activation rule, for example:
    - bin count exceeds a minimum count floor, and
    - the increase persists across at least 2 consecutive bins or satisfies a moving-sum persistence criterion.
  - Record onset time in hours relative to Mw 6.4.
- Constraints:
  - Use only cells with at least one event in the analysis window for onset assignment.
  - Cells without a sustained activation should be marked as “no onset detected” rather than forced into the color scale.
  - The onset rule must be deterministic and documented in the output metadata.
  - Preserve the user’s 30-minute binning; do not change temporal resolution.
- Key outputs:
  - Grid-cell table containing cell center coordinates, total events, binned counts, onset flag, and onset time relative to Mw 6.4
  - Spatial onset map: grid colored by onset time, with faults and both mainshocks overlaid
  - Optional companion map of total event count per grid cell for interpretation
  - Histogram or cumulative distribution of grid-cell onset times

### Task 3 — Prepare a fault backbone with 1 km segments and segment attributes
- Task description:
  - Convert mapped fault polylines into contiguous fixed-length segments, compute geometry attributes, and prepare a unique fault-backbone dataset for earthquake association and directional activation analysis.
- Required data sources:
  - `<REPO_ROOT>/examples/ridgecrest/data/faults/ridgecrest_surface_faults.json`
- Parameter selection strategy:
  - For each input polyline, resample/discretize along arclength at ~1 km spacing.
  - If a polyline is shorter than 1 km, keep one segment spanning its endpoints.
  - Assign `line_id`, `segment_id`, segment midpoint, endpoints, length, azimuth/strike, and cumulative distance along parent polyline.
  - Optionally split further at strong curvature/strike-change points only if this can be implemented deterministically from local angle thresholds.
- Constraints:
  - Preserve segment ordering along each polyline.
  - Strike should be normalized to a consistent orientation convention before later density analysis.
  - Do not merge distinct mapped polylines unless explicitly justified by topology rules.
- Key outputs:
  - Fault-segment attribute table
  - Segment geometry file with endpoints and midpoints
  - QC plots:
    - distribution of segment lengths
    - map of segmentized faults colored by strike
    - map labeled by line_id for major structures if readable

### Task 4 — Associate earthquakes to nearest fault segments
- Task description:
  - For each event in the Mw 6.4–Mw 7.1 window, compute nearest distance to all fault segments, assign to the nearest segment when within 3 km, and exclude the rest from fault-segment activation analysis.
- Required data sources:
  - Time-window event subset from Task 1
  - Fault-segment dataset from Task 3
- Parameter selection strategy:
  - Use projected coordinates and point-to-line-segment distance.
  - Assign each event to the nearest segment if distance < 3 km.
  - Store nearest `line_id`, `segment_id`, distance_km, projected position along segment, and segment strike.
- Constraints:
  - Use parallel chunking across events or segment spatial indexing to keep runtime tractable.
  - Retain excluded events in a separate table for later map context and exclusion auditing.
  - Report association fraction overall and by distance bin.
- Key outputs:
  - Event-to-segment association table
  - Excluded-event table with nearest distance
  - QC figures:
    - histogram of nearest event-to-fault distance
    - map of associated vs excluded events
    - map of segment load (number of assigned events per segment)

### Task 5 — Construct fault-segment activation time series and detect activation
- Task description:
  - Build per-segment seismicity time series using associated events, compute cumulative counts and instantaneous rates, assign fault-segment activation times from the user-defined threshold, and summarize activation chronology.
- Required data sources:
  - Event-to-segment association table from Task 4
  - Mw 6.4 and Mw 7.1 times from Task 1
  - Fault-segment attributes from Task 3
- Parameter selection strategy:
  - Bin associated events into 30-minute intervals for each segment.
  - Compute:
    - count per bin
    - rate per bin in events/hour
    - cumulative count through time
  - Define activation time as first 30-minute bin with rate > 10 events/hour, equivalent to count ≥ 5 in a bin.
  - Record activation time in hours since Mw 6.4.
- Constraints:
  - Segments never reaching threshold remain unactivated and should be flagged explicitly.
  - The threshold rule should not be modified across segments.
  - Store both first-threshold time and pre-threshold total count for diagnostics.
- Key outputs:
  - Segment-time-series table
  - Segment activation summary table with activation time, total events, peak rate, cumulative count at activation, and strike
  - QC plots:
    - fraction of segments activated through time
    - distribution of activation times
    - example time series for the earliest, median, and latest activated segments

### Task 6 — Visualize the fault-based activation sequence
- Task description:
  - Produce the requested activation-sequence figures on faults and summarize the density of activated segments through time and strike.
- Required data sources:
  - Fault-segment activation summary from Task 5
  - Event-to-segment association table from Task 4
  - Fault geometry from Task 3
  - Mainshock table from Task 1
- Parameter selection strategy:
  - Color fault segments by activation time relative to Mw 6.4.
  - Overlay Mw 6.4 and Mw 7.1 epicenters.
  - Overlay associated earthquakes using small marker size and low alpha, colored by event time or local activation time as appropriate.
  - Build time-density panels from activated segments only.
  - For strike–time density, use a strike convention corrected to the fault orientation so equivalent directions are consistently folded if needed (for example 0–180° rather than 0–360°).
- Constraints:
  - Unactivated segments should use a distinct neutral color or mask.
  - Keep time bins aligned exactly with the 30-minute analysis bins.
  - Strike correction must be documented and applied consistently.
- Key outputs:
  - Fault-segment activation map
  - Activated-segment count vs time figure
  - Time × activated-segment density heatmap
  - Strike × activation-time density heatmap
  - Optional line-by-line activation raster: x = time, y = ordered segment position along parent fault

### Task 7 — Diagnose triggering style: synchronous, staged, cascade-like, or complex
- Task description:
  - Convert the activation products into interpretable diagnostics that test whether activation occurred nearly simultaneously, propagated progressively along faults, jumped among faults, or concentrated at structural complexities, including whether the eventual Mw 7.1 initiation segment activated anomalously late.
- Required data sources:
  - Grid-cell onset table from Task 2
  - Segment activation summary from Task 5
  - Segment geometry/ordering from Task 3
  - Event-to-segment association table from Task 4
  - Mainshock epicenters from Task 1
- Parameter selection strategy:
  - Evaluate synchrony using:
    - distribution width of activation times across all activated segments
    - fraction of activated segments within early windows after Mw 6.4
  - Evaluate cascade-like propagation along faults using:
    - activation time versus cumulative distance along each parent polyline
    - monotonicity or rank correlation between along-fault distance and activation time
    - apparent propagation speed from linear fits where patterns are coherent
  - Evaluate cross-fault jumping/complexity using:
    - clustering of early activation near fault intersections, bends, or dense fault zones
    - activation residuals after removing along-fault trends
  - Evaluate Mw 7.1 nucleation behavior by identifying the segment nearest the Mw 7.1 epicenter and comparing its activation time to neighboring and system-wide distributions.
- Constraints:
  - Interpretive labels should be based on quantitative diagnostics, not visual impression alone.
  - Apparent propagation speed should only be reported for faults with enough activated segments and coherent ordering.
  - If multiple segments are equally close to the Mw 7.1 epicenter, treat them as a local nucleation neighborhood.
- Key outputs:
  - Per-fault activation-trend table with correlation, slope, and propagation-class flags
  - Along-fault time–distance diagrams for major activated faults
  - Map of early activation concentrated at bends/intersections if present
  - Summary decision table classifying each major fault or fault group as synchronous, staged, cascade-like, or complex
  - Specific diagnostic comparing Mw 7.1 nucleation segment activation to surrounding segments

### Task 8 — Execution packaging and independent deliverables
- Task description:
  - Organize the workflow into a small number of reproducible scripts with independent intermediate outputs and validation at each stage.
- Required data sources:
  - Outputs from Tasks 1–7
- Parameter selection strategy:
  - Use three primary task scripts:
    - Script A: data loading, projection, region construction, time-window filtering, grid onset analysis
    - Script B: fault segmentation, event-to-segment association, segment time-series/activation detection
    - Script C: triggering diagnostics and all final visualizations that consume validated outputs from A and B
  - Parallelize heavy loops in Scripts A and B, with progress logging.
- Constraints:
  - Each script should validate non-empty outputs before downstream use.
  - Failure evidence should include counts of valid/invalid cells, segments, and associations.
  - Intermediate outputs should be stored as plain tables for reuse across scripts.
- Key outputs:
  - Script-level output manifest
  - Validation tables for each stage
  - Final figure set and summary metrics ready for report synthesis