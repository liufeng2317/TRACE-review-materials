# Goal
Investigate the spatiotemporal evolution of the Ridgecrest earthquake sequence between the Mw 6.4 and Mw 7.1 mainshocks, with emphasis on whether triggered seismicity is aligned with mapped fault الاتجاه, whether that alignment changes with time, and whether activation occurs simultaneously across the full fault system or propagates progressively.

## Planning Assumptions
- Use the provided relocated earthquake catalog and fault geometry as the primary observational data; no model data are needed.
- The catalog schema is explicitly given as `event_time, latitude, longitude, depth_km, magnitude`; both mainshock and full catalog files share this schema.
- The Mw 6.4 and Mw 7.1 mainshocks should be identified from `main_shock_events.csv` by magnitude and used as authoritative temporal anchors for all window definitions and annotations.
- Surface faults are provided as geographic polylines in lon-lat coordinates; nearest-fault distance should be computed in a projected Cartesian system or with geodesic segment distance, not by raw degree-space Euclidean distance.
- All map panels must use identical spatial extents derived once from the combined event cloud and/or fault coverage over the Ridgecrest sequence area, then reused for every subplot and comparison panel.
- “Top level overlay” for faults and mainshocks means they should be drawn in every subplot with consistent styling and z-order, not recomputed independently per panel.
- Major analysis stages should be runnable independently with their own saved intermediate tables/figures; use parallel processing for fault-distance and figure-batch generation where runtime is substantial.
- Progress logging should be included for long-running loops over time windows, fault polylines/segments, or figure batches.

## Analysis Plan

### Task 1 — Build the unified Ridgecrest analysis dataset and canonical time windows
- Task description
  - Load the relocated catalog, mainshock table, and fault polylines; standardize timestamps; define the exact analysis windows and panel schedule used by all downstream tasks.
- Required data sources
  - `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/TRACE_ridgecrest_relocated.csv`
  - `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/main_shock_events.csv`
  - `<REPO_ROOT>/examples/ridgecrest/data/faults/ridgecrest_surface_faults.json`
- Parameter selection strategy
  - Parse `event_time` as UTC.
  - Identify `mainshock64` and `mainshock71` from the 2-row mainshock file by magnitude.
  - Define the master interval as `[mainshock64, mainshock71]`.
  - Define Stage 1 windows: consecutive 30-minute bins from `mainshock64` to `mainshock64 + 4 hours`.
  - Define Stage 2 windows: consecutive 2-hour bins from `mainshock64 + 4 hours` to `mainshock71`.
  - Define post-Mw7.1 comparison window: `[mainshock71, mainshock71 + 2 days]`.
  - Precompute a single map extent from catalog events between `mainshock64` and `mainshock71`, expanded slightly to include nearby fault traces and both mainshocks.
- Constraints
  - Keep catalog rows with valid time, latitude, longitude, depth, and magnitude only.
  - Preserve all events; do not magnitude-threshold unless data quality problems require explicit exclusion.
  - Use left-closed/right-open bin definitions for internal time slices to avoid double counting at boundaries; keep the last window end explicitly aligned to `mainshock71`.
- Key outputs
  - Clean event table with parsed UTC times.
  - Mainshock metadata table with exact times and coordinates.
  - Time-window definition table for Stage 1, Stage 2, and pre/post-Mw7.1 comparison.
  - Canonical map bounds and fault-geometry summary for reuse.

### Task 2 — Quantify fault-orientation controls and their temporal evolution between Mw 6.4 and Mw 7.1
- Task description
  - Derive analysis metrics that directly answer whether triggered earthquakes align with fault direction, whether the preferred direction changes over time, and whether activation is simultaneous or progressive along strike.
- Required data sources
  - Clean event table and time-window table from Task 1
  - Fault polylines from the JSON source
- Parameter selection strategy
  - Convert event and fault coordinates to a local projected system centered on Ridgecrest for distance and directional calculations.
  - Represent the fault network as line segments extracted from all polylines.
  - For each event in `[mainshock64, mainshock71]`, compute:
    - nearest fault distance,
    - azimuth/strike of the nearest fault segment,
    - along-strike coordinate on the nearest segment or nearest polyline chain,
    - signed relative position along one or more dominant Ridgecrest fault trends if a principal fault orientation can be robustly estimated.
  - Estimate dominant fault directions from the mapped fault segments using length-weighted strike statistics; if the network is clearly multi-modal, retain the main modes rather than forcing one single strike.
  - For each time bin, compute:
    - event count,
    - fault-distance statistics,
    - strike-alignment statistics of the event cloud,
    - principal-axis orientation of epicenter distribution,
    - along-strike span and center of activity,
    - cumulative occupied along-strike length.
- Constraints
  - Do not infer “fault direction” from epicenters alone; compare event geometry to mapped fault geometry.
  - For principal-axis orientation, use only bins with enough events for stable covariance estimation; bins with too few events should be flagged and excluded from directional interpretation.
  - If multiple dominant fault families exist, report alignment separately by fault family or by nearest-segment assignment.
  - Along-strike evolution should be evaluated both incrementally per bin and cumulatively from `mainshock64` onward.
- Key outputs
  - Event-level table with projected coordinates, nearest-fault distance, nearest-fault strike, nearest-fault identifier/segment identifier, and along-strike coordinate.
  - Bin-level summary table with orientation, span, centroid migration, and cumulative occupancy metrics.
  - Diagnostic statistics answering:
    - alignment with mapped fault strike,
    - time variation in preferred trend,
    - simultaneous versus progressive occupation of fault length.

### Task 3 — Produce the requested time-sliced spatial map series from Mw 6.4 to Mw 7.1
- Task description
  - Generate a sequence of 2×4 map figures that show time-sliced earthquake evolution over the fault network between the two mainshocks.
- Required data sources
  - Clean event table and time-window table from Task 1
  - Mainshock metadata from Task 1
  - Fault geometry from the JSON source
- Parameter selection strategy
  - Group windows into batches of 8 panels per figure in chronological order.
  - For each subplot:
    - brighter-color scatter for events within the active time window,
    - silver/high-transparency scatter for all events earlier than the active window but later than or equal to `mainshock64`,
    - overlay all fault polylines,
    - overlay Mw 6.4 and Mw 7.1 epicenters.
  - Use the same map extent, symbol scaling, and mainshock/fault styling in every panel and every figure.
  - Add panel titles containing absolute UTC range and elapsed time since Mw 6.4.
  - Optionally annotate per-panel event count and median nearest-fault distance from Task 2.
- Constraints
  - No colorbar.
  - Earlier events should not include pre-Mw6.4 catalog events unless explicitly desired; default to sequence-only history beginning at `mainshock64`.
  - Keep subplot chronology monotonic across all multi-panel figures.
  - If the total number of windows is not divisible by 8, create a final partially filled figure with unused axes suppressed.
  - Use parallel batching for figure generation only after all event subsets and overlays are precomputed.
- Key outputs
  - Chronological series of 2×4 time-sliced map figures spanning Stage 1 and Stage 2.
  - Window-level plotting manifest listing each panel’s time range and event counts.

### Task 4 — Compare spatial organization before and after the Mw 7.1 mainshock
- Task description
  - Create a direct spatial comparison of seismicity before versus after the Mw 7.1 mainshock to assess redistribution of activity relative to the fault system.
- Required data sources
  - Clean event table from Task 1
  - Mainshock metadata from Task 1
  - Fault geometry from the JSON source
- Parameter selection strategy
  - Panel A: events in `[mainshock64, mainshock71]`.
  - Panel B: events in `[mainshock71, mainshock71 + 2 days]`.
  - Use the same map extent, fault overlays, and mainshock symbols in both panels.
  - Keep event symbol style comparable across the two panels; if density is high, use transparency or small markers instead of changing extents.
  - Add panel annotations for event count, magnitude summary, and median nearest-fault distance if available from Task 2.
- Constraints
  - Preserve identical axes and geographic framing across both panels.
  - Do not mix before/after events in one panel unless as a faint contextual background explicitly distinguished from focal events.
- Key outputs
  - One two-panel before/after Mw 7.1 spatial comparison figure.
  - Summary table comparing counts, centroid, principal orientation, along-strike span, and fault-distance statistics across the two periods.

### Task 5 — Compute nearest-fault distance statistics for all events between Mw 6.4 and Mw 7.1
- Task description
  - Calculate the minimum distance from each earthquake to the mapped surface fault network and summarize how tightly seismicity follows the faults.
- Required data sources
  - Clean event table from Task 1
  - Fault geometry from the JSON source
- Parameter selection strategy
  - Restrict the primary statistics to events in `[mainshock64, mainshock71]`.
  - Convert faults into segment objects in projected coordinates.
  - Use spatial indexing to accelerate nearest-segment search; then compute exact point-to-segment distance for candidate segments.
  - Parallelize event-distance computation across event chunks, targeting up to 64 cores.
  - Store distance in kilometers.
  - Summarize overall distribution using median, interquartile range, high quantiles, and empirical cumulative fractions within fixed thresholds.
- Constraints
  - Distances must be measured to fault segments, not just vertices.
  - Handle events outside the immediate fault bundle without clipping; keep their full distances.
  - Include validation on a random sample by checking nearest segment identity and distance consistency.
- Key outputs
  - Event-level nearest-fault distance table.
  - Overall nearest-fault distance summary table.
  - Cached fault-segment/spatial-index objects or equivalent reusable intermediate products.

### Task 6 — Plot nearest-fault distance distributions and their temporal changes
- Task description
  - Visualize whether triggered earthquakes become closer to or farther from mapped faults over time, and whether fault occupancy broadens or tightens as the sequence evolves.
- Required data sources
  - Event-level nearest-fault distance table from Task 5
  - Time-window table from Task 1
  - Bin-level summaries from Task 2
- Parameter selection strategy
  - Produce an overall nearest-fault distance distribution for `[mainshock64, mainshock71]` using:
    - histogram or kernel-smoothed density,
    - empirical cumulative distribution,
    - optional log-scaled distance axis if the distribution is strongly skewed.
  - Produce temporal change views using the same Stage 1 and Stage 2 bins:
    - boxplots/violin plots of distance by time bin,
    - median and interquartile-range time series,
    - cumulative fraction of events within selected distance thresholds over time.
  - If event counts vary strongly by bin, annotate counts or normalize appropriately.
- Constraints
  - Keep binning identical to the map-series window definitions for direct comparison.
  - Avoid overinterpreting very sparse bins; mark bins below the minimum event threshold.
  - If kernel density is used, keep it supplementary to raw histogram/CDF views.
- Key outputs
  - Overall nearest-fault distance distribution figure.
  - Time-evolving nearest-fault distance figure set.
  - Tabulated per-bin distance summaries.

### Task 7 — Synthesize evidence for progressive versus simultaneous triggering along fault direction
- Task description
  - Integrate the map sequence, along-strike metrics, and fault-distance statistics into explicit tests of the user’s three scientific questions.
- Required data sources
  - Bin-level summaries from Task 2
  - Time-sliced map outputs from Task 3
  - Before/after comparison from Task 4
  - Distance summaries from Tasks 5–6
- Parameter selection strategy
  - Evaluate “along fault direction?” using:
    - angular difference between event-cloud principal axis and nearest/dominant fault strike,
    - concentration of events within small nearest-fault distances,
    - map-based visual agreement.
  - Evaluate “changing over time?” using:
    - time series of principal-axis orientation,
    - time series of nearest-fault-strike assignment proportions,
    - migration of activity centroid and along-strike span.
  - Evaluate “simultaneous or evolving?” using:
    - cumulative occupied along-strike length,
    - first-appearance time of activity in along-strike bins,
    - heatmap of along-strike coordinate versus time.
- Constraints
  - Distinguish genuine migration from simple growth in total event count by using both incremental and cumulative metrics.
  - If the fault system has multiple branches, assess propagation within each branch and across branches separately where possible.
- Key outputs
  - Along-strike-versus-time heatmap or raster of first occupancy and event density.
  - Time series of event-cloud orientation and centroid migration.
  - Compact machine-readable summary table mapping each scientific question to quantitative indicators and figure references.

### Task 8 — Execution structure, independence, and validation
- Task description
  - Organize the workflow into a small number of independent scripts with explicit dependencies, progress reporting, and validation checks.
- Required data sources
  - All sources and intermediate products from Tasks 1–7
- Parameter selection strategy
  - Script 1: data loading, time-window construction, projection setup, fault segmentation, nearest-fault distance computation, and event-level metric export.
  - Script 2: time-binned summaries, directional/along-strike statistics, and derived summary tables.
  - Script 3: figure generation for time-sliced maps, pre/post-Mw7.1 comparison, distance distributions, and along-strike temporal plots.
  - Reuse cached event-level and bin-level tables between scripts to keep major steps independent.
- Constraints
  - Each script should validate that required inputs exist and outputs are non-empty before declaring success.
  - Long loops should emit progress logs for event chunks, time bins, and figure batches.
  - Parallel execution should be applied where computation is embarrassingly parallel; merged outputs must be validated after batching.
- Key outputs
  - One event-level metrics file.
  - One bin-level summary file.
  - Figure set covering map evolution, pre/post comparison, nearest-fault distributions, and along-strike temporal evolution.
  - Validation logs documenting event counts, window counts, and successful figure generation.