# Goal

Perform event-centered sequence analysis for the three matched major earthquakes in the Aomori regional catalog, comparing pre- and post-event seismicity evolution around M1, M2, and M3, and testing robustness across spatial, temporal, depth, and magnitude definitions.

## Planning Assumptions

- Primary observation data are the relocated regional catalog, mainshock reference table, focal-mechanism metadata, and station inventory; model data are not needed.
- The three major earthquakes can be re-matched to the relocated catalog using time-location proximity because relocation may shift event attributes slightly.
- The relocated catalog is the scientific base table for all sequence extraction and rate calculations.
- The main analytical challenge is sensitivity to parameter choice; therefore, each sequence must be evaluated across multiple radii, time windows, depth windows, and magnitude thresholds.
- Preliminary completeness screening should use Mc ≈ 1.2 for the full catalog, then test higher magnitude thresholds for robustness.
- M1 and M3 are expected to show localized enrichment; M2 may require explicit depth stratification.
- Station coverage and focal-mechanism availability are contextual constraints, so mechanism summaries should be reported only where coverage is sufficient.
- Package contract note: no external analysis package is explicitly required by the request; the plan should remain data-driven and should preserve intermediate tables for reusable downstream plotting and robustness checks.
- The analysis should produce machine-actionable tabular outputs first, then figures derived from those outputs.

## Analysis Plan

### 1. Minimal data verification and event matching
- Task description:
  - Read all four source files and verify fields needed for sequence analysis.
  - Confirm availability of time, latitude, longitude, depth, magnitude, event identifiers if present, mainshock records, station metadata, and focal-mechanism attributes.
  - Re-match M1, M2, and M3 to the relocated catalog using small tolerances in origin time and hypocentral distance.
- Required data sources:
  - `catalog/Snet_catalog_relocate.csv`
  - `catalog/main_earthquake.csv`
  - `source_mechanism/Snet_mecha.csv`
  - `stations/station.sta`
- Parameter selection strategy:
  - Use the mainshock table as the anchor list.
  - Match candidates in the relocated catalog by nearest origin time and nearest hypocenter; require unambiguous one-to-one matching.
  - If multiple candidates exist, prefer the event with minimum combined time-distance misfit.
- Constraints:
  - Do not assume exact time equality after relocation.
  - Record any unmatched or ambiguous cases explicitly.
- Key outputs:
  - A verification table of required fields per file.
  - A mainshock-to-catalog match table for M1, M2, and M3 with match diagnostics.
  - A catalog coverage summary for mechanism and station metadata.

### 2. Event-centered sequence extraction
- Task description:
  - Extract event sequences around each matched mainshock under multiple radius, time-window, depth-window, and magnitude-threshold definitions.
  - Build a standardized event-centered dataset for each mainshock.
- Required data sources:
  - `catalog/Snet_catalog_relocate.csv`
  - `catalog/main_earthquake.csv`
  - `source_mechanism/Snet_mecha.csv` for mechanism availability tagging
- Parameter selection strategy:
  - Radii: 30, 44, 50, 80, 100 km.
  - Time windows: pre-90d, pre-60d, pre-30d, pre-7d, post-7d, post-30d, post-60d, post-90d.
  - Depth windows:
    - all depths,
    - mainshock-centered local depth window,
    - depth-stratified bins chosen from the catalog’s observed depth distribution.
  - Magnitude thresholds:
    - all events,
    - M ≥ 1.2,
    - M ≥ 1.5,
    - M ≥ 2.0,
    - M ≥ 2.5 where sample size remains viable.
- Constraints:
  - Keep sequence extraction identical across M1, M2, and M3 so comparisons are commensurable.
  - If any threshold yields sparse samples, retain it as a sensitivity case rather than the default.
- Key outputs:
  - Event-centered sequence tables for each mainshock and parameter combination.
  - Summary counts by radius, time window, depth window, and magnitude threshold.

### 3. Sequence diagnostics and rate characterization
- Task description:
  - Compute seismicity statistics for each extracted sequence and parameter setting.
  - Quantify temporal evolution, rate changes, magnitude-depth structure, and spatial organization.
- Required data sources:
  - Event-centered sequence tables from Task 2
  - `source_mechanism/Snet_mecha.csv`
- Parameter selection strategy:
  - Use moving-window rate estimates with a window width chosen to balance burstiness and stability; preserve the same setting across all mainshocks.
  - Calculate pre/post rate ratios using matched pre- and post-windows.
  - For post-event decay, fit a simple Omori-style decay only when event counts are sufficient for stable fitting.
- Constraints:
  - Do not fit decay models where counts are too sparse or where the post-event interval is too short for meaningful estimation.
  - Treat mechanism summaries as optional and availability-limited.
- Key outputs:
  - Event counts, cumulative counts, moving-window rates, and pre/post rate ratios.
  - Magnitude-frequency summaries and depth distributions.
  - Radial-distance and time-distance diagnostics.
  - Post-event decay parameters or a documented note explaining why fitting was not feasible.
  - Mechanism availability fractions and simple mechanism summaries where supported by data.

### 4. Robustness analysis across sequence definitions
- Task description:
  - Identify which sequence features persist under changes in radius, time window, depth window, and magnitude threshold.
  - Separate stable signals from parameter-dependent signals.
- Required data sources:
  - Diagnostic tables from Task 3
- Parameter selection strategy:
  - Compare each diagnostic metric across all radii, time windows, depth windows, and thresholds.
  - Use consistency criteria based on directionality and relative ranking across settings rather than a single absolute cutoff.
- Constraints:
  - Avoid over-interpreting effects that appear only in one narrow parameter setting.
  - Preserve sensitivity cases as such, not as primary claims.
- Key outputs:
  - Robustness matrix/table for each mainshock.
  - Stability classification of observed features, such as robust pre-event increase, robust post-event decay, robust depth concentration, or parameter-sensitive spatial spread.

### 5. Three-sequence comparison
- Task description:
  - Compare M1, M2, and M3 in terms of background activity, pre-event activity, post-event activity, burstiness, decay, spatial concentration, depth structure, magnitude distribution, and sensitivity to sequence definitions.
- Required data sources:
  - Diagnostic tables from Tasks 2–4
- Parameter selection strategy:
  - Compare the same parameter settings across all three sequences first, then summarize cross-setting behavior.
  - Use the Mc ≈ 1.2 screened case as a common baseline, then compare higher thresholds.
- Constraints:
  - Keep comparison metrics standardized so one mainshock is not favored by a larger window or denser reporting.
- Key outputs:
  - A three-sequence comparison table.
  - Rank-order summaries of activity level, pre/post imbalance, and robustness.
  - A concise comparative summary of M1 vs M2 vs M3 sequence styles.

### 6. Simple control comparison
- Task description:
  - Build at least one feasible control to check whether observed patterns exceed background expectations.
- Required data sources:
  - `catalog/Snet_catalog_relocate.csv`
  - Matched mainshock times from Task 1
- Parameter selection strategy:
  - Use one or more of the following:
    - background windows away from each mainshock,
    - randomized mainshock times subject to catalog coverage constraints,
    - higher magnitude-threshold control,
    - simple pre/post background-rate comparison.
- Constraints:
  - Controls must be constructed so they are comparable in duration and spatial selection to the real windows.
  - Randomized controls should avoid periods with catalog truncation or strong edge effects.
- Key outputs:
  - Control-rate table.
  - Comparison of observed pre/post changes against control windows.

### 7. Diagnostic figures for publication-style reporting
- Task description:
  - Produce a compact but comprehensive figure set supporting the sequence interpretation and robustness assessment.
- Required data sources:
  - Diagnostic outputs from Tasks 1–6
- Parameter selection strategy:
  - Use identical plotting conventions across M1, M2, and M3.
  - Keep mainshock markers, axis limits, color scaling, and legends consistent within each figure family.
- Constraints:
  - Figures should emphasize comparability and robustness rather than decorative complexity.
  - Ensure each figure is interpretable without cross-referencing multiple files.
- Key outputs:
  - Event-centered maps for M1, M2, and M3.
  - Pre/post spatial comparison maps.
  - Cumulative count curves.
  - Moving-window rate curves.
  - Post-event decay plots.
  - Time-distance and/or radial-distance plots.
  - Radius and time-window sensitivity heatmaps.
  - Magnitude-threshold sensitivity plots.
  - Depth-stratified sequence plots.
  - Three-sequence comparison summary figure.

### 8. Reusable analysis products for downstream work
- Task description:
  - Package the results into reusable tables and figure-ready summaries for later focused interpretation.
- Required data sources:
  - Outputs from Tasks 1–7
- Parameter selection strategy:
  - Save one compact summary table per mainshock plus one cross-mainshock comparison table.
- Constraints:
  - Keep outputs standardized and explicitly labeled by mainshock and parameter setting.
- Key outputs:
  - Clean summary tables for counts, rates, distributions, robustness, and controls.
  - Figure-ready data tables for all diagnostics and sensitivity plots.