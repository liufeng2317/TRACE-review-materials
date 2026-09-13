# Goal
Quantify and compare spatial b-value structure during the Ridgecrest Mw 6.4–Mw 7.1 interevent period, with emphasis on whether the future Mw 7.1 hypocentral/rupture region shows lower b-values than the Mw 6.4 control region, while reporting uncertainty, data support, and robustness without making a precursor claim.

## Planning Assumptions
- Observation data are sufficient; no model data are needed.
- Main-shock origin times and hypocenters must be read directly from `main_shock_events.csv`; the fixed separator event time is user-specified as `2019-07-05T11:07:52.830000Z`.
- All b-value estimates must exclude the Mw 6.4, Mw 7.1, and the separator M5.37 event from the sampled catalogs.
- Primary spatial maps use fixed `Mc = 1.5` for all nodes and all three interevent windows; dynamic Mc is only a window-level QC diagnostic.
- Use Aki-Utsu / classical maximum-likelihood b-value estimation with magnitude-bin correction. `seismostats` supports classical b-value estimation through `ClassicBValueEstimator` / `estimate_b(magnitudes, mc, delta_m)` and supports Mc estimation via MAXC, KS, and b-stability methods.
- Magnitude bin width `delta_M` must be inferred from the actual magnitude discretization in the catalogs, not from arbitrary assumption. If multiple precisions appear, use the dominant positive spacing after sorting unique magnitudes and verify against FMD binning.
- Fixed-radius circular sampling is the main method. Main analysis radii are 4, 5, 6, and 7 km, with 5 km as primary. Do not extend beyond 7 km except for optional grid-boundary padding logic.
- A valid node requires at least 30 events with `M >= Mc`; reliability labels are fixed by user rule: 30–49 exploratory, 50–99 moderately uncertain, `>=100` robust.
- Bootstrap uncertainty should use at least 500 resamples for valid nodes; parallel execution up to 64 cores is appropriate for node-wise bootstrap and radius-sensitivity loops.
- Preferred execution is one primary analysis script for end-to-end ingestion, preprocessing, estimation, QC, and output generation, plus one compact plotting/assembly stage only if separation improves reuse of tabular outputs.

## Analysis Plan

### Task 1 — Build the cleaned analysis catalogs and QC metadata
- Task description
  - Ingest the three CSV sources, define the three interevent windows, remove excluded marker events, standardize columns, infer magnitude discretization, project coordinates to a local metric system, and generate cleaned catalogs for all downstream calculations.
- Required data sources
  - `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/TRACE_ridgecrest_relocated.csv`
  - `<REPO_ROOT>/examples/ridgecrest/data/catalog_longterm/catalog_2year_background_before_64.csv`
  - `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/main_shock_events.csv`
- Parameter selection strategy
  - Parse event times as UTC timestamps.
  - Identify Mw 6.4 and Mw 7.1 rows from the main-shock file by magnitude and time ordering.
  - Define windows:
    - `full_interevent`: `[Mw6.4_time, Mw7.1_time)`
    - `pre_separator`: `[Mw6.4_time, separator_time)`
    - `post_separator`: `[separator_time, Mw7.1_time)`
  - Exclude from all catalogs:
    - the Mw 6.4 main shock,
    - the Mw 7.1 main shock,
    - the separator event nearest `2019-07-05T11:07:52.830000Z` with magnitude near 5.37.
  - For background regional context, use the long-term catalog before Mw 6.4; rename `datetime, latR, lonR, depR, mag` to the standardized fields.
  - Infer local projected coordinates using a local metric CRS centered on the sequence centroid or the midpoint between the two main shocks; use the same projection for catalogs, grid, and overlays.
  - Infer `delta_M` from sorted unique magnitudes:
    - compute positive magnitude differences after rounding to observed precision,
    - choose the dominant small positive spacing as catalog `delta_M`,
    - verify against the FMD histogram binning used later.
- Constraints
  - Do not alter event magnitudes except optional rounding to the detected catalog discretization for consistent FMD/bin-based calculations.
  - Keep all cleaned catalogs with both geographic and projected coordinates.
  - Preserve exact exclusion logic in validation metadata.
- Key outputs
  - `catalog_full_interevent_clean.csv`
  - `catalog_pre_separator_clean.csv`
  - `catalog_post_separator_clean.csv`
  - `catalog_background_context_clean.csv`
  - `window_markers_and_exclusions.csv`
  - `catalog_validation_checks.csv`
  - `analysis_metadata.json` containing projection choice, inferred `delta_M`, event counts before/after exclusions, and time-window definitions.

### Task 2 — Window-level completeness and reference b-value QC
- Task description
  - Estimate one dynamic Mc per analysis window and one regional reference b-value from the background catalog, to contextualize but not replace the fixed-`Mc=1.5` spatial maps.
- Required data sources
  - Cleaned window catalogs from Task 1
  - Cleaned background catalog from Task 1
- Parameter selection strategy
  - For each interevent window and the background catalog:
    - bin magnitudes using inferred `delta_M`,
    - estimate dynamic Mc using at least MAXC and one stricter method for QC:
      - primary QC: `estimate_mc_maxc(fmd_bin=delta_M)` or equivalent,
      - confirmatory QC: `estimate_mc_ks(delta_m=delta_M)` and/or `estimate_mc_b_stability()`.
  - Compute window-level b-values using:
    - fixed `Mc = 1.5` for comparability with maps,
    - dynamic Mc for QC only.
  - Use classical/Aki-Utsu estimator via `seismostats` or equivalent formula:
    - `b = log10(e) / (mean(M) - Mc + delta_M/2)`.
  - Estimate uncertainty by bootstrap for each window-level b-value with at least 1000 resamples because catalog sizes are small enough.
- Constraints
  - Dynamic Mc must not be propagated into node-wise main maps.
  - Report when dynamic Mc exceeds 1.5, because node support under fixed Mc may then be less conservative.
  - Background catalog is for larger-area context only; do not compare it directly as a like-for-like interevent precursor metric.
- Key outputs
  - `window_level_mc_b_qc.csv`
  - `background_reference_bvalue.csv`
  - `window_level_fmd_summary.csv`
  - Figure: `figure_window_level_fmd_qc`

### Task 3 — Primary fixed-radius spatial b-value analysis
- Task description
  - Compute node-wise spatial b-values, support counts, and bootstrap uncertainty for the three windows on a regular projected grid using circular radius sampling.
- Required data sources
  - Cleaned interevent catalogs from Task 1
  - Main-shock markers from Task 1 metadata
- Parameter selection strategy
  - Define the active interevent region from the convex hull or buffered bounding box of interevent events in projected coordinates; expand by at least the primary radius so edge nodes can still sample nearby events.
  - Build a regular grid with spacing selected within the requested 0.5–1.0 km:
    - primary recommendation: 0.5 km if computational load remains manageable,
    - fallback: 1.0 km if 0.5 km creates excessive bootstrap cost.
  - For each node and each window:
    - sample events within horizontal radius = 5 km,
    - retain events with `M >= 1.5`,
    - if `n < 30`, set `b`, uncertainty, and bootstrap CI to `NaN`,
    - else compute:
      - `n_ge_mc`,
      - mean magnitude above Mc,
      - Aki-Utsu b-value,
      - bootstrap mean/median b,
      - bootstrap standard deviation,
      - 2.5–97.5% confidence interval,
      - reliability class from `n_ge_mc`.
  - Use vectorized distance search or spatial indexing to accelerate node-event queries.
  - Parallelize bootstrap and/or node loops up to 64 cores; write progress logs by window and batch.
- Constraints
  - Use only horizontal radius for the main spatial method; depth is retained for later profile/section tasks but not for 2D node membership.
  - Mask nodes with no valid estimate; do not interpolate across NaNs.
  - Use a common color scale across the three 5 km maps derived from the union of valid b-values or a robust clipped range.
- Key outputs
  - `grid_bvalues_full_interevent_r5km.csv`
  - `grid_bvalues_pre_separator_r5km.csv`
  - `grid_bvalues_post_separator_r5km.csv`
  - `grid_validity_reliability_r5km.csv`
  - `bootstrap_progress_log.csv`
  - Figures:
    - `figure_bmap_full_interevent_r5km`
    - `figure_bmap_pre_separator_r5km`
    - `figure_bmap_post_separator_r5km`

### Task 4 — Reliability, uncertainty, and map-difference diagnostics
- Task description
  - Generate reliability-class maps, uncertainty products, and the `post_separator - pre_separator` difference map using only jointly valid nodes.
- Required data sources
  - 5 km node tables from Task 3
- Parameter selection strategy
  - For each window, derive map-ready layers:
    - `n_ge_mc`,
    - reliability class,
    - bootstrap standard deviation,
    - CI width.
  - For the difference map:
    - inner join pre and post node tables on identical grid nodes,
    - retain only nodes where both windows have valid b-values,
    - compute:
      - `delta_b = b_post - b_pre`,
      - uncertainty proxy from bootstrap variances or CI overlap summary,
      - support counts from both windows,
      - a validity flag indicating both windows meet threshold.
  - Summarize how many nodes are valid in each window and in the overlap set.
- Constraints
  - Treat sparse pre-separator coverage as exploratory in both tables and figure annotations.
  - Do not interpret difference values where one or both windows are below the minimum-count threshold.
- Key outputs
  - `grid_reliability_full_interevent_r5km.csv`
  - `grid_reliability_pre_separator_r5km.csv`
  - `grid_reliability_post_separator_r5km.csv`
  - `grid_bvalue_difference_post_minus_pre_r5km.csv`
  - `map_coverage_summary.csv`
  - Figures:
    - `figure_reliability_maps_r5km`
    - `figure_uncertainty_maps_r5km`
    - `figure_bdifference_post_minus_pre_r5km`

### Task 5 — Core-region comparison around Mw 6.4 and future Mw 7.1 hypocenters
- Task description
  - Compare fixed 5 km hypocentral core regions centered on the Mw 6.4 and Mw 7.1 main shocks across full, pre-, and post-separator windows using b-values and FMD diagnostics.
- Required data sources
  - Cleaned interevent catalogs from Task 1
  - Main-shock hypocenters from Task 1 metadata
- Parameter selection strategy
  - Define two fixed circular cores:
    - Mw 6.4 control core: 5 km horizontal radius around the Mw 6.4 hypocenter,
    - Mw 7.1 future core: 5 km horizontal radius around the Mw 7.1 hypocenter.
  - For each core and each window:
    - extract events inside the circle,
    - apply fixed `Mc = 1.5`,
    - compute `n_ge_mc`, b-value, bootstrap uncertainty, reliability class,
    - build cumulative and non-cumulative FMD tables,
    - optionally compute dynamic Mc as an auxiliary QC column only.
  - Include event-count contrast between the two cores and between windows.
- Constraints
  - If a core/window combination has `n < 30`, retain the row with `NaN` b and explicit insufficiency flag; still provide raw FMD counts.
  - Keep the same radius definition as the spatial maps for direct interpretability.
- Key outputs
  - `core_region_bvalues_r5km.csv`
  - `core_region_fmd_summary.csv`
  - `core_region_event_counts.csv`
  - `core_region_validation_checks.csv`
  - Figure:
    - `figure_core_fmd_comparison_r5km`

### Task 6 — Low-b spatial summary targeted to the future Mw 7.1 region
- Task description
  - Produce descriptive summaries of low-b areas using the user-defined thresholds and quantify whether the future Mw 7.1 core and nearby fault-zone nodes fall within those low-b subsets.
- Required data sources
  - 5 km grid tables from Task 3
  - Difference and reliability tables from Task 4
  - Main-shock core definitions from Task 5
- Parameter selection strategy
  - For each window:
    - identify valid nodes with `b < 0.9`,
    - identify the lowest 20% of valid nodes by b-value,
    - summarize area-equivalent node count, median b, uncertainty distribution, and reliability distribution.
  - Quantify relation to the future Mw 7.1 region:
    - whether the Mw 7.1 core-center node or nearest valid nodes fall into the low-b subsets,
    - fraction of low-b nodes within a neighborhood around the Mw 7.1 hypocenter versus around the Mw 6.4 control core,
    - distance from Mw 7.1 hypocenter to nearest low-b robust node.
- Constraints
  - This is descriptive support only; avoid threshold-based anomaly language.
  - Low-b summaries must always be reported together with support counts and reliability composition.
- Key outputs
  - `low_b_summary_full_interevent.csv`
  - `low_b_summary_pre_separator.csv`
  - `low_b_summary_post_separator.csv`
  - `future71_vs_control_lowb_comparison.csv`
  - Figure:
    - `figure_low_b_summary_panels`

### Task 7 — Mw 7.1 fault-oriented post-separator profile / cross-section
- Task description
  - Examine whether post-separator b-values organize along the future Mw 7.1 rupture trend using a fault-oriented profile or narrow swath.
- Required data sources
  - Post-separator grid/node tables from Task 3
  - Main-shock locations from Task 1
  - Event hypocenters from post-separator catalog in Task 1
- Parameter selection strategy
  - Define an along-strike axis for the Mw 7.1 structure using one reproducible rule:
    - preferred: line from Mw 6.4 to Mw 7.1 hypocenter as first-order trend proxy,
    - or principal-component orientation of post-separator events within a neighborhood around the Mw 7.1 hypocenter.
  - Project post-separator valid grid nodes onto:
    - along-strike distance,
    - across-strike distance.
  - Build either:
    - a narrow swath average profile along strike, or
    - a cross-section band showing b versus along-strike distance with point color/size by uncertainty or support.
  - Also project post-separator events for structural context.
- Constraints
  - The orientation rule must be saved in metadata and kept independent of observed low-b values.
  - Use only valid nodes; do not smooth across invalid gaps without flagging.
- Key outputs
  - `post_separator_fault_oriented_profile.csv`
  - `profile_orientation_metadata.csv`
  - Figure:
    - `figure_post_separator_fault_oriented_profile`

### Task 8 — Radius sensitivity and validation synthesis
- Task description
  - Test whether the main spatial pattern is stable across radii 4, 5, 6, and 7 km, and compile final validation tables needed for interpretation.
- Required data sources
  - Cleaned interevent catalogs from Task 1
  - Primary grid definition from Task 3
- Parameter selection strategy
  - Repeat the node-wise calculation for radii 4, 6, and 7 km on the same grid and with the same fixed `Mc = 1.5`.
  - For each window and radius, compute:
    - valid-node fraction,
    - median and interquartile range of b,
    - overlap correlation with 5 km node values where both valid,
    - future Mw 7.1 core b-value,
    - Mw 6.4 control core b-value,
    - difference between future and control cores,
    - fraction of valid nodes classified as low-b.
  - Summarize whether the future Mw 7.1 region remains relatively low-b, disappears, or broadens as radius changes.
- Constraints
  - Radii above 7 km are excluded from the main analysis.
  - Sensitivity figures should clearly separate pattern persistence from changes caused by increased smoothing or improved support.
- Key outputs
  - `grid_bvalues_full_interevent_r4_r6_r7km.csv`
  - `grid_bvalues_pre_separator_r4_r6_r7km.csv`
  - `grid_bvalues_post_separator_r4_r6_r7km.csv`
  - `radius_sensitivity_summary.csv`
  - `core_radius_sensitivity_summary.csv`
  - `final_validation_checks.csv`
  - Figure:
    - `figure_radius_sensitivity_summary`

### Task Script Organization

#### Task Script 1 — End-to-end spatial b-value analysis
- Task description
  - Single primary script to execute Tasks 1–8 in one reproducible workflow: read inputs, clean catalogs, project coordinates, estimate window-level Mc QC, build grid, compute node-wise b-values and bootstrap uncertainty for all windows and radii, derive difference/reliability/core/profile/low-b outputs, run validation checks, and save all CSV/JSON products plus figure-ready tables.
- Required data sources
  - All three input CSV files listed above.
- Parameter selection strategy
  - Expose explicit runtime parameters at top of script:
    - fixed `Mc=1.5`
    - `radii_km=[4,5,6,7]`
    - `primary_radius_km=5`
    - `grid_spacing_km=0.5` with fallback to `1.0`
    - `min_events_ge_mc=30`
    - `bootstrap_samples>=500` for nodes, `>=1000` for window/core summaries
    - `max_workers<=64`
    - separator time fixed to user value.
- Constraints
  - Include immediate output checks:
    - cleaned catalogs non-empty,
    - marker exclusions found exactly once,
    - inferred `delta_M` valid,
    - at least some valid 5 km nodes in `full_interevent`,
    - difference map overlap node count recorded even if sparse.
  - Failure evidence must be written if any window or radius has zero valid nodes.
  - Successful execution requires non-empty scientific outputs, not just config generation.
- Key outputs
  - All CSV/JSON tables and metadata listed above.
  - Progress logs and validation tables.

#### Task Script 2 — Figure assembly from validated tables
- Task description
  - Read Task Script 1 outputs and generate the required figures with consistent scales, overlays, masks, and panel structure.
- Required data sources
  - Validated grid tables, core tables, profile tables, and metadata from Task Script 1.
- Parameter selection strategy
  - Use common b-value color limits across the three 5 km window maps and consistent reliability legend.
  - Overlay Mw 6.4, M5.37, Mw 7.1, plus 5 km core circles for Mw 6.4 and Mw 7.1 on map-view figures.
  - For difference maps, plot only jointly valid nodes.
- Constraints
  - Do not regenerate scientific quantities in this script except light reshaping for plotting.
  - If Task Script 1 validation flags missing or empty outputs, this script should stop with failure evidence rather than plotting placeholders.
- Key outputs
  - `figure_bmap_full_interevent_r5km`
  - `figure_bmap_pre_separator_r5km`
  - `figure_bmap_post_separator_r5km`
  - `figure_reliability_maps_r5km`
  - `figure_uncertainty_maps_r5km`
  - `figure_bdifference_post_minus_pre_r5km`
  - `figure_post_separator_fault_oriented_profile`
  - `figure_core_fmd_comparison_r5km`
  - `figure_radius_sensitivity_summary`

## Analysis Plan
### 1. Data preparation and window construction
- Task description
  - Standardize catalogs, define time windows, exclude marker events, infer magnitude discretization, and project coordinates.
- Required data sources
  - Interevent catalog, background catalog, main-shock file.
- Parameter selection strategy
  - Read main-shock times from file; use user-provided separator time; fixed exclusions; infer `delta_M` from catalog precision; adopt one local metric CRS.
- Constraints
  - Keep cleaned catalogs and validation records; no node-level Mc estimation in the main workflow.
- Key outputs
  - Cleaned catalogs, exclusion logs, projection metadata, validation table.

### 2. Window-level completeness and background reference QC
- Task description
  - Estimate dynamic Mc and catalog-level b-values for QC and regional context.
- Required data sources
  - Cleaned window and background catalogs.
- Parameter selection strategy
  - Use `seismostats` MAXC and KS and/or b-stability methods; compute fixed- and dynamic-Mc window b-values.
- Constraints
  - Dynamic Mc used only for QC.
- Key outputs
  - QC tables and window/background FMD summaries.

### 3. Primary 5 km spatial b-value mapping
- Task description
  - Compute 5 km fixed-radius node-wise b-values for full, pre-, and post-separator windows.
- Required data sources
  - Cleaned interevent catalogs and main-shock metadata.
- Parameter selection strategy
  - Grid spacing 0.5–1.0 km; fixed `Mc=1.5`; minimum `n>=30`; bootstrap `>=500`.
- Constraints
  - No interpolation over invalid nodes; common color scale across maps.
- Key outputs
  - 5 km grid-node CSVs and the three primary map figures.

### 4. Reliability and uncertainty diagnostics
- Task description
  - Quantify support and uncertainty for each valid node and visualize data coverage.
- Required data sources
  - 5 km node tables.
- Parameter selection strategy
  - Map `n>=Mc`, reliability class, bootstrap std, and CI width.
- Constraints
  - Sparse pre-separator coverage explicitly labeled exploratory.
- Key outputs
  - Reliability/uncertainty CSVs and figures.

### 5. Pre/post spatial change
- Task description
  - Evaluate spatial changes between pre- and post-separator windows using valid node overlap only.
- Required data sources
  - Pre- and post-separator 5 km node tables.
- Parameter selection strategy
  - Compute `b_post - b_pre` and carry both support counts plus uncertainty proxies.
- Constraints
  - No difference estimate where either node is invalid.
- Key outputs
  - Difference-map source table and figure.

### 6. Mw 6.4 control core vs future Mw 7.1 core
- Task description
  - Compare fixed 5 km cores around the two main shocks using b-values and FMDs in all three windows.
- Required data sources
  - Cleaned interevent catalogs and main-shock hypocenters.
- Parameter selection strategy
  - Same radius and fixed `Mc=1.5` as main maps; bootstrap uncertainty; cumulative and incremental FMDs.
- Constraints
  - Retain insufficient-sample cases as explicit QC rows.
- Key outputs
  - Core comparison tables and FMD comparison figure.

### 7. Future Mw 7.1 region profile
- Task description
  - Test whether post-separator b-values organize along the future rupture trend.
- Required data sources
  - Post-separator node table and post-separator events.
- Parameter selection strategy
  - Use a reproducible fault-orientation rule and project valid nodes into along-strike coordinates.
- Constraints
  - Orientation must not be tuned to maximize low-b appearance.
- Key outputs
  - Profile table and figure.

### 8. Low-b summary and radius sensitivity
- Task description
  - Summarize low-b node subsets and test robustness across radii 4–7 km.
- Required data sources
  - All node tables and core summaries.
- Parameter selection strategy
  - Thresholds: `b<0.9` and lowest 20% of valid nodes; radii 4, 5, 6, 7 km on same grid.
- Constraints
  - Treat this as spatial support for Q0/Q1 only; no deterministic or independent precursor framing.
- Key outputs
  - Low-b summary tables, radius sensitivity tables, and summary figure.