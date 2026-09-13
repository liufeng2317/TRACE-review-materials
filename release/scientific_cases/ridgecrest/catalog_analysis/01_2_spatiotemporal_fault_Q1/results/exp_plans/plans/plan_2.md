# Goal
Investigate the spatiotemporal evolution of the Ridgecrest earthquake sequence between the Mw 6.4 and Mw 7.1 mainshocks, with emphasis on whether triggered seismicity is aligned with mapped fault directions, whether that alignment changes through time, and whether fault activation is spatially simultaneous or progressively migratory.

## Planning Assumptions
- Use the provided relocated earthquake catalog and mapped surface faults as the primary observational datasets; no model data are needed.
- The catalog schema is fixed as `event_time, latitude, longitude, depth_km, magnitude`; `event_time` should be parsed as UTC datetime.
- `main_shock_events.csv` contains the Mw 6.4 and Mw 7.1 reference events and should define the analysis time windows directly rather than by hard-coded timestamps.
- `ridgecrest_surface_faults.json` contains many geographic polylines; nearest-fault distance should be computed to the line geometry, not only to fault vertices.
- Spatial calculations should be done in a local projected coordinate system appropriate for Ridgecrest so that distances, along-strike projections, and map extents are internally consistent.
- Major computational products should be generated in separate task scripts with reusable outputs; plotting-only tasks should consume validated intermediate tables rather than recomputing geometry.
- Parallelism up to 64 cores is requested and should be used for distance calculations, repeated time-slice statistics, and figure panel generation where safe; each script should include progress logging and checks for empty time bins.
- Success evidence for each script is a non-empty derived table or figure set matching the requested time windows; diagnostic-only or partially filled outputs are not sufficient.

## Analysis Plan

### Task 1 — Build analysis-ready earthquake, mainshock, and fault datasets
- Task description
  - Load the relocated catalog, mainshock table, and fault polylines; standardize time, geometry, and event identifiers; derive the analysis windows and reusable spatial reference objects.
- Required data sources
  - `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/TRACE_ridgecrest_relocated.csv`
  - `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/main_shock_events.csv`
  - `<REPO_ROOT>/examples/ridgecrest/data/faults/ridgecrest_surface_faults.json`
- Parameter selection strategy
  - Identify the Mw 6.4 and Mw 7.1 rows from `main_shock_events.csv` by magnitude and use their `event_time` values as `t64` and `t71`.
  - Define the requested windows exactly:
    - Full pre-Mw7.1 window: `[t64, t71]`
    - Stage 1: `[t64, t64 + 4 h]` with 30-minute bins
    - Stage 2: `[t64 + 4 h, t71]` with 2-hour bins
    - Post-Mw7.1 comparison window: `[t71, t71 + 2 days]`
  - Assign a unique event index if the catalog lacks an event id.
  - Convert event and fault coordinates from geographic lon/lat to a local projected CRS centered on Ridgecrest for all metric calculations.
  - Build one merged fault geometry collection and, separately, a table of individual fault-segment azimuths/lengths for later orientation analysis.
- Constraints
  - Preserve the original UTC timing and use half-open bin conventions consistently except where inclusive endpoints are explicitly required for the main comparison windows.
  - Do not filter events by magnitude unless exploratory completeness issues are later documented; the requested workflow is catalog-based.
  - Validate that `t64 < t71`, both mainshocks fall within the catalog time range, and the fault JSON is non-empty.
- Key outputs
  - Clean catalog table with projected coordinates and event index
  - Mainshock reference table with `t64`, `t71`, projected coordinates, and labels
  - Fault geometry object and fault-segment orientation table
  - Time-bin definition table for all requested windows

### Task 2 — Create time-sliced spatial maps of seismic evolution from Mw 6.4 to Mw 7.1
- Task description
  - Generate a series of 2 × 4 panel maps showing how epicentral distributions evolve through the requested time bins, with prior events faded in the background.
- Required data sources
  - Analysis-ready outputs from Task 1
- Parameter selection strategy
  - Build ordered bins for:
    - Stage 1: 8 bins of 30 minutes each
    - Stage 2: consecutive 2-hour bins from `t64 + 4 h` until `t71`
  - Since each figure must have 8 subplots, paginate bins into figure groups of 8 panels in chronological order.
  - Use identical map extents for all panels, determined once from the union of:
    - all events in `[t64, t71 + 2 days]`
    - both mainshocks
    - all fault polylines
    - then expanded by a small fixed geographic margin so edge events/faults are not clipped.
  - In each panel:
    - brighter scatter: events within the current bin
    - silver transparent scatter: all events in `[t64, current_bin_start)` 
    - fault traces overlaid consistently
    - Mw 6.4 and Mw 7.1 epicenters overlaid with fixed symbols
  - Use fixed point size and transparency rules across all panels so density changes are visually comparable.
- Constraints
  - No colorbar.
  - Fault lines and mainshock symbols should appear at the figure/top plotting layer in every panel.
  - Empty bins must still produce a panel with background events, faults, and mainshocks.
  - Keep the same aspect treatment and extent for all subplots and all paginated figures.
  - Parallelize panel preparation/render-data generation if needed, but ensure deterministic chronological ordering in the final figure sequence.
- Key outputs
  - One or more paginated figure files for Stage 1 and Stage 2 time-sliced maps
  - Per-bin summary table with bin start/end, event count, cumulative prior count, and figure/page assignment

### Task 3 — Compare pre- and post-Mw 7.1 spatial distributions
- Task description
  - Produce a direct spatial comparison of the earthquake distribution before versus after the Mw 7.1 mainshock.
- Required data sources
  - Analysis-ready outputs from Task 1
- Parameter selection strategy
  - Define two windows exactly as requested:
    - Before Mw 7.1: `[t64, t71]`
    - After Mw 7.1: `[t71, t71 + 2 days]`
  - Use the same overall spatial extent as Task 2 for direct comparison.
  - Plot faults and both mainshock epicenters on both comparison panels.
  - Use comparable symbol rules between the two panels; if event counts differ strongly, allow transparency adjustment but keep the same extent and base layers.
- Constraints
  - The Mw 7.1 event lies at the boundary between the two windows; use a documented boundary rule and apply it consistently.
  - Do not mix this comparison with density smoothing unless an additional derived product is explicitly labeled as such.
- Key outputs
  - A two-panel comparison figure of pre- versus post-Mw7.1 spatial distributions
  - Window summary table with event counts and magnitude ranges in each comparison period

### Task 4 — Quantify nearest-fault distance and its temporal evolution
- Task description
  - Compute the nearest distance from each earthquake to the mapped surface-fault network and analyze how the distance distribution changes between Mw 6.4 and Mw 7.1.
- Required data sources
  - Analysis-ready outputs from Task 1
- Parameter selection strategy
  - Restrict the main distance-evolution analysis to events in `[t64, t71]` as requested.
  - Compute nearest distance in projected coordinates from each epicenter point to the full fault polyline geometry.
  - Store both:
    - minimum distance to the fault network
    - identifier of nearest fault polyline/segment if computationally available
  - Parallelize the point-to-line distance computation across events or spatial chunks up to 64 cores.
  - For distribution-over-time analysis, use the same temporal bins as Task 2 so the distance statistics can be compared directly to the map sequence.
  - For each bin, calculate:
    - count
    - median and interquartile range of nearest-fault distance
    - selected quantiles (for example 10th, 50th, 90th)
    - fraction of events within fixed distance thresholds chosen from data-informed map scale after inspecting the distance range
- Constraints
  - Distance must be to line geometry, not simple nearest fault-node distance.
  - If a local CRS is used, report distance in km after conversion from projected meters.
  - Empty or very sparse bins should remain in the summary table with missing or flagged statistics rather than being dropped.
- Key outputs
  - Event-level table with nearest-fault distance for all events in `[t64, t71]`
  - Time-bin statistics table for nearest-fault distance evolution
  - Overall nearest-fault distance distribution figure
  - Time-evolving nearest-fault distance figure

### Task 5 — Test whether triggered earthquakes follow fault direction and whether that direction changes with time
- Task description
  - Derive quantitative measures of alignment between triggered seismicity and mapped fault orientations, and evaluate whether activation is simultaneous across the fault system or migrates in space and orientation.
- Required data sources
  - Analysis-ready outputs from Task 1
  - Event-level nearest-fault table from Task 4
- Parameter selection strategy
  - Use events in `[t64, t71]`, with the same Stage 1 and Stage 2 time bins as the map analysis.
  - For each event, associate the nearest fault segment or locally nearest line portion and extract its strike/azimuth.
  - Quantify event-cloud orientation within each bin using projected epicenters via at least one robust geometric summary:
    - principal-axis orientation from covariance/PCA of epicenter coordinates
    - along-strike versus cross-strike spread relative to the dominant local fault orientation
  - Compare the bin-wise event-cloud orientation to:
    - the dominant orientation of nearby mapped faults
    - the orientation of all activated events cumulatively up to that time
  - To address simultaneous coverage versus progressive evolution, compute along-fault position metrics:
    - project events onto one or more reference fault-aligned axes derived from the dominant fault set near the mainshocks
    - track the evolving occupied along-strike range per bin
    - track cumulative occupied range and newly activated range per bin
  - Summarize whether new seismicity appears across the whole fault length early or whether the active range expands stepwise through time.
- Constraints
  - Because the fault network contains many polylines with variable azimuths, orientation comparisons should be local or segment-based rather than assuming one single regional strike.
  - Report orientation using a consistent azimuth convention and treat 180° ambiguity appropriately for line directions.
  - If a bin has too few events for stable PCA/orientation estimation, flag it and exclude it from directional inference plots while retaining counts.
- Key outputs
  - Bin-wise table of event-cloud orientation, fault-orientation match metrics, along-strike extent, cross-strike width, and newly activated along-strike length
  - Figure of bin-wise dominant seismicity orientation versus dominant local fault orientation
  - Figure of along-strike occupied range through time, suitable for assessing simultaneous versus progressive activation
  - Compact interpretation-ready summary table answering the three main questions quantitatively

### Task 6 — Integrate requested figures and stepwise deliverables
- Task description
  - Package each major analytical step as an independent output set with validation records so results can be reviewed separately.
- Required data sources
  - Outputs from Tasks 2–5
- Parameter selection strategy
  - Organize outputs into distinct result groups:
    - time-sliced map figures
    - Mw7.1 before/after comparison figure
    - nearest-fault distance tables and figures
    - directionality/migration tables and figures
  - For each group, record metadata including time windows, number of events used, map extent, CRS used for distance calculations, and any bins flagged as sparse.
- Constraints
  - Each major step must be independently executable and must not depend on later interpretation steps.
  - Validation should confirm non-empty figures/tables, correct number of bins, and presence of both mainshock markers and fault overlays where required.
- Key outputs
  - Stepwise validated output inventory
  - Metadata table for reproducibility and downstream interpretation