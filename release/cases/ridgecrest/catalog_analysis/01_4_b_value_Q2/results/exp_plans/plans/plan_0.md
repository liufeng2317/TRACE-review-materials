# Goal
Compute spatial b-value diagnostics for the Ridgecrest Mw 6.4–Mw 7.1 interevent catalog using fixed-radius circular sampling, compare the future Mw 7.1 hypocentral/core region with a Mw 6.4 control core, and assess whether any spatial low-b pattern is consistent with Q0/Q1 local b-value results while explicitly reporting uncertainty and reliability.

## Planning Assumptions
- Observation catalogs are sufficient; no model data are needed.
- Main analysis uses fixed Mc = 1.5 for all spatial nodes and all three interevent windows, per user requirement.
- Window-level dynamic Mc is QC only and should be estimated once per window, not per node.
- Use the classical/Aki-Utsu maximum-likelihood b-value estimator with magnitude discretization correction; SeismoStats supports classical b-value estimation via `estimate_b` or `ClassicBValueEstimator`, and supports catalog-level Mc estimation via `estimate_mc_maxc`, `estimate_mc_ks`, and `estimate_mc_b_stability`.
- Infer `delta_M` from the actual magnitude discretization in the catalog after inspecting unique magnitude spacing; do not infer from display formatting alone if the spacing is inconsistent.
- Exclude the Mw 6.4 main shock, Mw 7.1 main shock, and the fixed separator event at `2019-07-05T11:07:52.830000Z` from all b-value calculations, but retain them as map/profile markers.
- Use a local projected metric coordinate system centered on the Ridgecrest sequence for all distance, radius, grid, circle, and profile calculations; apply the same projection to all catalogs and markers.
- Reliability classes are determined from the number of events with `M >= Mc` used at each node: 30–49 exploratory, 50–99 moderately uncertain, >=100 robust.
- Valid scientific success requires non-empty cleaned window catalogs, non-empty valid-node outputs for at least full and post-separator 5 km maps, and merged radius-sensitivity tables/figures. Sparse pre-separator coverage is acceptable but must be flagged as exploratory rather than treated as failure.

## Analysis Plan
### Task 1 — Primary catalog processing, spatial b-value computation, QC, and figure/table generation
- Task description
  - Build one primary analysis script that ingests the three CSV sources, parses time windows and exclusions, projects coordinates, creates fixed-radius grid-node samples, computes node-wise and core-wise b-values with bootstrap uncertainty, generates requested validation tables, and writes the figure source data plus final figures.
- Required data sources
  - `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/TRACE_ridgecrest_relocated.csv`
  - `<REPO_ROOT>/examples/ridgecrest/data/catalog_longterm/catalog_2year_background_before_64.csv`
  - `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/main_shock_events.csv`
- Parameter selection strategy
  - Read Mw 6.4 and Mw 7.1 event times, hypocenters, depths, and magnitudes from `main_shock_events.csv`.
  - Define windows exactly from the marker times:
    - `full_interevent`: `[Mw6.4_time, Mw7.1_time)`
    - `pre_separator`: `[Mw6.4_time, separator_time)`
    - `post_separator`: `(separator_time, Mw7.1_time)`
  - Remove events matching the Mw 6.4 and Mw 7.1 main shocks by exact time if available, otherwise by nearest-time plus magnitude/hypocenter cross-check against the two-row file.
  - Remove the separator event by exact timestamp `2019-07-05T11:07:52.830000Z`; if duplicate rows exist at that time, exclude all rows at that timestamp.
  - Standardize interevent columns to `time, lat, lon, depth_km, mag`; standardize background catalog using `datetime, latR, lonR, depR, mag`.
  - Determine `delta_M` from observed catalog magnitude spacing after sorting unique magnitudes; prefer the dominant positive spacing if nearly uniform, otherwise use the minimum stable modal spacing and record the decision in metadata/validation output.
  - Use fixed `Mc = 1.5` for all map, difference, profile, and core calculations.
  - Estimate one dynamic Mc per window and one background-region Mc for QC using MAXC as primary QC and KS / b-stability as supplementary checks if sample size is sufficient; report method agreement rather than substituting dynamic Mc into the main maps.
  - Build a regular 2D grid over the active interevent footprint using projected coordinates of the excluded-cleaned full interevent catalog; use primary spacing 0.5 km if computationally feasible, otherwise 1.0 km, and keep the same grid for all windows and radii.
  - Add a modest margin around the convex hull / min-max event extent so edge nodes near the active sequence are retained; record the final bounds in metadata.
  - For each grid node and each radius in `{4, 5, 6, 7}` km, gather events within horizontal circle radius; compute `n_total`, `n_ge_mc`, mean magnitude above Mc, b-value, bootstrap standard error, and percentile confidence limits when `n_ge_mc >= 30`, else set b/uncertainty to NaN.
  - Bootstrap valid node estimates with at least 500 resamples; if runtime permits, use 1000 for the 5 km primary radius and 500 for sensitivity radii. Parallelize across nodes/windows/radii up to 64 cores and log progress by window/radius.
  - Define two 5 km core circles centered at the Mw 6.4 and Mw 7.1 hypocenters using the same projected coordinates and fixed radius 5 km.
  - For the Mw 7.1 fault-oriented profile, estimate strike from the post-separator seismicity cloud or from the Mw 6.4–Mw 7.1 hypocenter alignment if a clearer rupture-trend estimate is needed; document the chosen strike and use a swath width comparable to the node radius so profile support remains interpretable.
  - Low-b summary per window should use both criteria:
    - absolute threshold `b < 0.9`
    - relative threshold = lowest 20% of valid node b-values
    - summarize overlap, spatial concentration near Mw 7.1 core, and reliability-class composition.
- Constraints
  - Do not estimate node-specific Mc for the main maps.
  - Do not use radii > 7 km in the main analysis.
  - Use common b-value color scale across the three 5 km primary maps and a symmetric scale centered at zero for the `post - pre` difference map.
  - Mask nodes with invalid b-values or insufficient `n_ge_mc`.
  - Interpret pre-separator spatial products as exploratory if valid-node coverage is sparse.
  - Background catalog is for regional reference only; do not merge it into interevent mapping.
  - Keep horizontal-distance sampling circular and fixed-radius; do not switch to adaptive kernels or rectangular moving windows.
- Key outputs
  - Cleaned catalogs
    - `catalog_full_interevent_clean.csv`
    - `catalog_pre_separator_clean.csv`
    - `catalog_post_separator_clean.csv`
    - `catalog_background_reference_clean.csv`
    - `excluded_events_log.csv`
  - Metadata and validation
    - `analysis_metadata.json`
    - `window_summary_checks.csv`
    - `magnitude_precision_deltaM_check.csv`
    - `window_level_mc_qc.csv`
    - `background_reference_bvalue.csv`
    - `projection_and_grid_definition.csv`
  - Grid-node tables
    - `grid_bvalues_full_interevent_r4.csv`
    - `grid_bvalues_full_interevent_r5.csv`
    - `grid_bvalues_full_interevent_r6.csv`
    - `grid_bvalues_full_interevent_r7.csv`
    - corresponding files for `pre_separator` and `post_separator`
    - each table should include node ID, projected and geographic coordinates, radius_km, window_name, `n_total`, `n_ge_mc`, mean_mag_ge_mc, b_value, bootstrap_se, bootstrap_ci_low, bootstrap_ci_high, reliability_class, valid_flag
  - Difference/profile/core tables
    - `grid_bvalue_difference_post_minus_pre_r5.csv`
    - `mw71_profile_post_separator_r5.csv`
    - `core_bvalues_fmd_summary.csv`
    - `core_fmd_bins.csv`
    - `low_b_summary_by_window.csv`
    - `low_b_nodes_by_window_r5.csv`
    - `radius_sensitivity_summary.csv`
  - Figures
    - `map_bvalue_full_interevent_r5`
    - `map_bvalue_pre_separator_r5`
    - `map_bvalue_post_separator_r5`
    - `map_reliability_ngeMc_r5_by_window`
    - `map_uncertainty_bootstrap_se_r5_by_window`
    - `map_reliability_class_r5_by_window`
    - `map_bvalue_difference_post_minus_pre_r5`
    - `profile_mw71_post_separator_bvalue`
    - `figure_core_fmd_comparison`
    - `figure_radius_sensitivity`
  - Figure content requirements
    - 5 km maps: common b-scale, overlays for Mw 6.4, M5.37, Mw 7.1, and 5 km core circles for Mw 6.4/Mw 7.1
    - Reliability figures: separate visualization for `n_ge_mc`, bootstrap uncertainty, and reliability class
    - Core FMD figure: Mw 6.4 vs Mw 7.1 cores for full, pre, post windows, with fitted Mc line and b-value annotation
    - Radius sensitivity figure: compare Mw 7.1-core and Mw 6.4-core b-values and/or valid low-b spatial extent across radii 4–7 km
  - Descriptive interpretation-ready summaries
    - concise machine-readable statements in CSV/JSON capturing whether the Mw 7.1 core/profile lies below, within, or above the window-wide valid-node distribution, with uncertainty and reliability tags

### Task 1.1 — Input harmonization and event-window construction
- Task description
  - Parse timestamps, standardize schema, identify and exclude target marker events, and split the interevent sequence into the three user-defined windows.
- Required data sources
  - Interevent catalog and main-shock file; background catalog for regional-reference preprocessing.
- Parameter selection strategy
  - Use UTC-aware datetime parsing.
  - Confirm that main-shock times from `main_shock_events.csv` bound the interevent catalog span.
  - Verify whether the separator event exists exactly in the interevent catalog; if not, keep the separator as a temporal boundary only and log absence.
- Constraints
  - Exclusions must be applied before any Mc, b-value, FMD, or sampling-count calculation.
- Key outputs
  - Clean per-window catalogs and exclusion/consistency logs.

### Task 1.2 — Projection, active-region grid, and sampling geometry
- Task description
  - Convert catalog coordinates to local metric coordinates and define the common spatial sampling framework.
- Required data sources
  - Cleaned interevent catalogs and main-shock markers.
- Parameter selection strategy
  - Center the local projection near the sequence centroid or midpoint of the two main shocks.
  - Grid spacing within requested 0.5–1.0 km; select the finest spacing that keeps 5 km bootstrap runtime practical under 64-core parallel execution.
  - Use the same grid for all windows and radii for direct comparison.
- Constraints
  - Distances for circular sampling and core circles must be computed in projected coordinates.
- Key outputs
  - Grid-definition table and projected event/marker coordinates.

### Task 1.3 — Window-level Mc QC and regional reference b-value
- Task description
  - Estimate dynamic Mc for each window and for the background regional catalog as QC/reference, without changing the main fixed-Mc maps.
- Required data sources
  - Cleaned full/pre/post catalogs and cleaned background catalog.
- Parameter selection strategy
  - Bin magnitudes using inferred `delta_M`.
  - Use MAXC as the primary reported dynamic Mc because it is stable and efficient; supplement with KS and b-stability where event counts above candidate Mc permit meaningful testing.
  - Compute background reference b-value over the larger-area catalog using its dynamic Mc and also report a fixed-Mc=1.5 comparison if sample size supports it.
- Constraints
  - Present these results explicitly as QC/context only.
- Key outputs
  - `window_level_mc_qc.csv`, `background_reference_bvalue.csv`, and FMD source tables for QC.

### Task 1.4 — Node-wise spatial b-value and uncertainty calculation
- Task description
  - Compute spatial b-values for each window and radius on the common grid.
- Required data sources
  - Cleaned window catalogs, projected coordinates, grid definition.
- Parameter selection strategy
  - For each node: select events within circular horizontal radius, retain events with `M >= 1.5`, compute Aki-Utsu b-value with `delta_M` correction, and bootstrap uncertainty.
  - Store both geographic and projected node coordinates so maps and profiles can be reproduced directly from tables.
- Constraints
  - Return NaN when `n_ge_mc < 30`.
  - Reliability class depends only on `n_ge_mc`, not on bootstrap spread.
- Key outputs
  - Per-window, per-radius node CSV files and run-progress logs.

### Task 1.5 — Difference map, Mw 7.1 profile, and core-circle comparison
- Task description
  - Derive the targeted comparative diagnostics requested by the user.
- Required data sources
  - Primary 5 km node tables, main-shock markers, cleaned window catalogs.
- Parameter selection strategy
  - Difference map: merge 5 km post/pre node tables by common node ID and compute `b_post - b_pre` only where both are valid.
  - Mw 7.1 profile: sample node b-values or swath-aggregated event circles along the chosen strike through the Mw 7.1 hypocenter for the post-separator window; include distance along strike, perpendicular offset support, `n_ge_mc`, b, and uncertainty.
  - Core comparison: within each 5 km core circle around Mw 6.4 and Mw 7.1, compute b-values and FMDs for full/pre/post windows, plus bootstrap uncertainty and reliability class.
- Constraints
  - If the Mw 7.1 control/profile geometry choice is ambiguous, preserve the decision and alternatives in metadata instead of silently changing geometry.
- Key outputs
  - Difference, profile, and core comparison tables and figures.

### Task 1.6 — Low-b pattern summary and radius sensitivity synthesis
- Task description
  - Summarize whether low-b nodes cluster near the future Mw 7.1 region and test whether that pattern persists across allowed radii.
- Required data sources
  - 5 km and sensitivity-radius grid tables, core/profile outputs.
- Parameter selection strategy
  - For each window, identify nodes satisfying `b < 0.9` and nodes in the lowest 20% quantile of valid b-values.
  - Quantify counts, fraction of valid nodes, median uncertainty, reliability-class distribution, and distance of low-b nodes to Mw 7.1 and Mw 6.4 hypocenters/core circles.
  - For radii 4, 5, 6, 7 km, compare:
    - Mw 7.1-core b-value
    - Mw 6.4-core b-value
    - core difference
    - fraction of valid nodes within/near the Mw 7.1 core labeled low-b
    - map-correlation or rank-consistency of valid-node b-values between radii where feasible
- Constraints
  - Sensitivity testing supports robustness only within user-approved radii.
- Key outputs
  - `low_b_summary_by_window.csv`, `low_b_nodes_by_window_r5.csv`, `radius_sensitivity_summary.csv`, and `figure_radius_sensitivity`.

### Task 2 — Output validation and packaging
- Task description
  - Run one concise validation/packaging script after Task 1 to check required outputs, verify non-empty tables and valid-node coverage, and assemble an index of deliverables and key diagnostics.
- Required data sources
  - All Task 1 outputs.
- Parameter selection strategy
  - Validate that required CSVs and figures exist.
  - Check that 5 km full and post-separator maps contain valid nodes; allow pre-separator sparsity but report coverage fraction.
  - Verify merged difference-map table is non-empty if overlapping valid nodes exist; otherwise write an explicit reason.
  - Summarize core results, background reference, dynamic Mc QC, low-b counts, and sensitivity consistency in a compact manifest.
- Constraints
  - Do not treat placeholder, empty, or NaN-only scientific outputs as success.
- Key outputs
  - `output_manifest.csv`
  - `validation_report.json`
  - `required_output_checklist.csv`
  - explicit failure-evidence entries for any missing or empty required product