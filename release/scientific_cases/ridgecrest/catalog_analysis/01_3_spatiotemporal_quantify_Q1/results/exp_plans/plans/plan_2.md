# Goal
Investigate the spatiotemporal evolution of the Ridgecrest earthquake sequence from the Mw 6.4 mainshock to the Mw 7.1 mainshock and +10 hours, with emphasis on identifying temporally evolving directional clustering patterns that may illuminate the triggering transition between the two mainshocks using sector-based directional Ripley’s K/L analysis.

## Planning Assumptions
- Use the provided relocated observational catalog as the primary dataset; no model data are needed.
- The analysis window is fixed by the user as [Mw 6.4 origin time, Mw 7.1 origin time + 10 hours].
- Base computation interval is fixed at 30 minutes.
- Directional sectors are fixed at 5° over [0°, 360°), giving 72 azimuth bins.
- Because Ripley’s K depends on study-window area and edge treatment, the plan should use a clearly defined 2D spatial observation window derived from the seismicity footprint in the selected analysis interval, and the same window definition must be used consistently across all time slices when comparing temporal changes.
- Depth is available but the requested directional Ripley analysis and maps are 2D in longitude-latitude space; depth should be retained for supplementary diagnostics but not mixed into the 2D K/L estimator.
- A characteristic scale r must be selected from catalog geometry rather than guessed; use a documented selection rule based on inter-event spacing / fault-zone width / stability of directional signal across nearby radii, then keep the chosen r fixed for the heatmap and rose-diagram summaries.
- Computationally intensive pairwise calculations should be parallelized across time windows and, if needed, across radius chunks or sector accumulation blocks, with progress logging and non-empty output validation after each batch.
- Success for the main directional-analysis task requires valid per-window sector statistics, a merged time-direction table with no missing expected windows unless explicitly flagged for too-few-events cases, and the requested figure products.

## Analysis Plan

### Task 1 — Build the analysis-ready Ridgecrest sequence dataset and reference timeline
- Task description:
  - Load the relocated catalog, the two mainshocks, and the surface-fault geometry.
  - Define the exact analysis window from Mw 6.4 time to Mw 7.1 time + 10 hours.
  - Construct the regular 30-minute interval sequence and assign each event to an interval.
  - Prepare consistent spatial coordinates for pairwise-distance and orientation calculations.
- Required data sources:
  - `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/TRACE_ridgecrest_relocated.csv`
  - `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/main_shock_events.csv`
  - `<REPO_ROOT>/examples/ridgecrest/data/faults/ridgecrest_surface_faults.json`
- Parameter selection strategy:
  - Parse `event_time` as UTC and sort all tables chronologically.
  - Identify the Mw 6.4 and Mw 7.1 rows from the mainshock file by magnitude and preserve their origin times and epicenters as explicit anchors.
  - Clip catalog events to [mainshock64, mainshock71 + 10 h].
  - Convert event epicenters from lon/lat to a local projected Cartesian system centered on the Ridgecrest sequence for distance and azimuth calculations; retain original lon/lat for plotting.
  - Assign each event to a left-closed 30-minute interval; store interval start/end and interval index.
  - Build three representative-window sets:
    - Whole-window overview: 8 windows of 4 hours, approximately uniformly spaced through the full analysis duration.
    - Near-Mw 6.4 set: 8 representative 30-minute windows after Mw 6.4, approximately uniformly spaced within the early post-6.4 interval before Mw 7.1.
    - Near-Mw 7.1 set: 8 representative 30-minute windows before Mw 7.1, approximately uniformly spaced within the late pre-7.1 interval.
- Constraints:
  - Do not alter the user-specified global analysis window or 30-minute base interval.
  - Preserve all events regardless of magnitude unless a later diagnostic shows a need for a minimum-event threshold for stable K estimation; such windows should be flagged, not silently dropped.
  - Surface-fault JSON is plain nested polyline coordinates, so load directly as segment lists without GeoJSON assumptions.
- Key outputs:
  - Analysis-ready event table with UTC times, interval assignments, projected x-y coordinates, depth, magnitude.
  - Mainshock reference table with times and epicenters.
  - Parsed fault-segment table/polylines for map overlays.
  - Representative-window index table for the three requested figure groups.

### Task 2 — Define the spatial study window, characteristic scale, and directional Ripley computation protocol
- Task description:
  - Establish a reproducible 2D observation window and the sector-based Ripley K/L estimator used for all intervals.
  - Determine the characteristic radius r for summary visualization.
- Required data sources:
  - Analysis-ready outputs from Task 1
  - Surface-fault geometry for spatial-context diagnostics
- Parameter selection strategy:
  - Define a single fixed study window for all intervals using the footprint of the clipped sequence, preferably as a buffered convex hull or buffered bounding polygon in projected coordinates; record total area A.
  - Compute pairwise distances and pairwise azimuths for events within each interval.
  - Use sector bins of width 5° over [0°, 360°).
  - For each interval and each sector, count/accumulate only pairs with inter-event distance ≤ r and azimuth in the sector.
  - Normalize the directional K using the common study-window area and event count for that interval; convert to directional L for comparability.
  - Evaluate K/L first over a candidate radius set spanning short to intermediate scales relevant to the catalog footprint; choose one characteristic radius by:
    - excluding radii smaller than typical nearest-neighbor noise scale,
    - excluding radii approaching the study-window width where edge effects dominate,
    - selecting a radius where dominant-direction contrasts are stable across adjacent radii and event counts remain adequate across many intervals.
  - Store both the full radius-dependent directional statistics and the chosen-r summary statistic.
- Constraints:
  - Use the same study-window definition and edge-correction convention across all time intervals.
  - If edge correction cannot be implemented robustly for all sectors, clearly use a no-edge-correction or simplified correction consistently and report it as a limitation; do not mix methods across intervals.
  - Orientation convention must be fixed and documented, e.g., azimuth measured clockwise from east or north; the same convention must be used in heatmaps and roses.
  - Windows with too few events for stable pair statistics must be labeled as insufficient-data windows in the outputs.
- Key outputs:
  - Study-window geometry and area summary.
  - Radius-selection diagnostic table and plot-ready summary.
  - Formal specification table for sector bins, azimuth convention, normalization formula, and insufficient-data criteria.
  - Chosen characteristic radius value for all summary figures.

### Task 3 — Compute 30-minute time-resolved sector-based directional Ripley K/L statistics
- Task description:
  - Execute the main computation for every 30-minute interval across the analysis window, producing a time-direction matrix at the chosen radius and retaining full radius-dependent results.
- Required data sources:
  - Analysis-ready interval event table from Task 1
  - Estimator settings from Task 2
- Parameter selection strategy:
  - Parallelize by time interval as the default strategy, with up to 64 cores.
  - Within each interval:
    - subset events,
    - compute pairwise distances and azimuths,
    - accumulate counts/statistics into 72 sectors,
    - compute directional K(r,θ) and L(r,θ),
    - record event count, pair count, and data-quality flags.
  - For windows with large event counts, optionally use blockwise pair processing to control memory while preserving exact results.
  - Log progress by completed interval count and write intermediate per-interval outputs before merge.
- Constraints:
  - Each interval result must include explicit evidence of success: interval index, event count, non-empty sector array, and quality flag.
  - Do not treat partial batches as complete until the merged full time-direction table is present and covers all expected intervals.
  - Maintain a deterministic interval order for later figure generation.
- Key outputs:
  - Per-interval directional K/L result files.
  - Merged time-direction matrix of L(r_char, θ) with dimensions [time interval × 72 sectors].
  - Full radius-dependent result table for optional validation.
  - QC summary table with event counts, pair counts, insufficient-data flags, and runtime logs.

### Task 4 — Diagnose temporal directional transitions relevant to Mw 6.4-to-Mw 7.1 triggering
- Task description:
  - Extract dominant and secondary directional clustering signals from the time-direction matrix and compare them to the timing of the two mainshocks and mapped surface faults.
- Required data sources:
  - Merged directional-statistics outputs from Task 3
  - Mainshock reference table from Task 1
  - Fault geometry from Task 1
- Parameter selection strategy:
  - For each 30-minute interval at the chosen radius:
    - identify the primary direction as the sector of maximum L,
    - identify the secondary direction as the strongest non-adjacent local maximum,
    - compute directional concentration/anisotropy metrics such as max-minus-median and primary-to-secondary contrast.
  - Track temporal persistence and abrupt changes in dominant direction, especially:
    - immediately after Mw 6.4,
    - in the lead-up to Mw 7.1,
    - across the Mw 7.1 origin time and following 10 hours.
  - Compare dominant azimuth bands with the strike trends implied by the mapped surface-fault segments.
- Constraints:
  - Directional-peak extraction should suppress trivial adjacent-bin duplication when defining primary vs secondary directions.
  - Interpretive metrics must be derived from the computed L values only; do not introduce unvalidated triggering metrics outside the requested framework.
- Key outputs:
  - Time series of dominant direction, secondary direction, and anisotropy metrics.
  - Transition-point table highlighting intervals with major directional shifts.
  - Fault-strike comparison summary linking seismic clustering directions to mapped fault trends.

### Task 5 — Produce the requested heatmap summarizing time-direction evolution
- Task description:
  - Generate the main time-direction heatmap showing directional clustering through time and annotate it with the two mainshocks.
- Required data sources:
  - Time-direction L-matrix from Task 3
  - Directional-transition summaries from Task 4
  - Mainshock reference times from Task 1
- Parameter selection strategy:
  - X-axis: 30-minute interval centers or starts spanning [Mw 6.4, Mw 7.1 + 10 h].
  - Y-axis: azimuth sector centers from 0° to 355°.
  - Color: directional L at the chosen characteristic radius.
  - Overlay vertical reference lines or markers for Mw 6.4 and Mw 7.1 origin times.
  - Add overlays or annotations for dominant and secondary directions through time using the extracted peak tracks from Task 4.
- Constraints:
  - Use the same azimuth convention as in the computation step.
  - Intervals flagged as insufficient data should be visibly masked or annotated rather than interpolated.
- Key outputs:
  - Time-direction heatmap figure.
  - Plot-ready matrix/table used to create the heatmap.
  - Companion annotation table for dominant/secondary direction trajectories.

### Task 6 — Produce the three requested multi-panel map + polar-rose figure sets
- Task description:
  - Build the three 2×4 figure groups that pair event maps with directional rose summaries.
- Required data sources:
  - Representative-window definitions from Task 1
  - Event subsets and directional L statistics from Task 3
  - Mainshock epicenters from Task 1
  - Surface faults from Task 1
- Parameter selection strategy:
  - Figure set A: 8 representative 4-hour windows approximately uniformly spaced across the full analysis window.
  - Figure set B: 8 representative 30-minute windows after Mw 6.4, approximately uniformly spaced through the early post-6.4 period.
  - Figure set C: 8 representative 30-minute windows before Mw 7.1, approximately uniformly spaced through the pre-7.1 period.
  - In each panel:
    - plot event epicenters in lon-lat,
    - color by event time relative to the specified anchor (relative to Mw 6.4 for the first two sets; relative to Mw 7.1 for the third set),
    - overlay mapped surface-fault segments,
    - overlay Mw 6.4 and Mw 7.1 epicenters,
    - insert a polar rose summarizing directional clustering intensity from sector-based L at the chosen radius for that panel’s window.
  - For 4-hour windows, compute the directional statistic directly for the 4-hour subset rather than aggregating from 30-minute bins if feasible; otherwise aggregate transparently from constituent bins with the rule documented.
- Constraints:
  - Panel ordering must be chronological left-to-right, top-to-bottom.
  - All panels within a figure set should share consistent map bounds and color normalization for comparability.
  - Rose-diagram values must come from the same directional-statistics definition used in earlier tasks.
- Key outputs:
  - Figure A: full-window 8-panel map + rose overview.
  - Figure B: near-Mw 6.4 8-panel map + rose figure.
  - Figure C: near-Mw 7.1 8-panel map + rose figure.
  - Plot-support tables listing each panel’s time window, event count, dominant direction, and secondary direction.

### Task 7 — Independent validation and failure-evidence collection for computational robustness
- Task description:
  - Verify that the directional-analysis outputs are scientifically usable and computationally complete before interpretation.
- Required data sources:
  - Outputs from Tasks 2–6
- Parameter selection strategy:
  - Validate:
    - expected number of 30-minute intervals exists,
    - each interval has 72 sector values or an explicit insufficient-data flag,
    - characteristic-radius heatmap has non-empty data coverage,
    - representative panels all have non-empty event subsets unless intentionally flagged,
    - dominant-direction traces align with maxima in the underlying L matrix.
  - Run spot checks on selected intervals near Mw 6.4, mid-sequence, and just before Mw 7.1 by comparing raw pair-orientation histograms with rose-diagram peaks.
  - Record timing, memory, and any intervals requiring blockwise fallback.
- Constraints:
  - A diagnostic-only run without valid merged scientific outputs is not successful completion.
  - Any dropped or unstable windows must be enumerated explicitly in the QC outputs.
- Key outputs:
  - QC report table with completeness and consistency checks.
  - Validation summaries for selected intervals.
  - Failure/exception log and rerun-needed interval list, if any.