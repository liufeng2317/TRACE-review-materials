# Goal
Perform event-centered sequence analysis for the three major Aomori earthquakes (M1, M2, M3) using the relocated regional catalog, quantify pre- and post-event seismicity evolution under multiple spatial/temporal/depth/magnitude definitions, and evaluate which sequence features are robust versus parameter-dependent.

## Planning Assumptions
- Primary observation data are the relocated catalog `catalog/Snet_catalog_relocate.csv`, the mainshock reference table `catalog/main_earthquake.csv`, the focal-mechanism catalog `source_mechanism/Snet_mecha.csv`, and station inventory `stations/station.sta`.
- The three major earthquakes must be re-matched to the relocated catalog before extraction, allowing small tolerances in origin time and hypocentral position because the catalog is relocated.
- Preliminary completeness level around M1.2 should be treated as a screening threshold, not a fixed truth; higher thresholds must be tested explicitly.
- Sequence behavior may differ strongly by radius, time window, and depth stratification; burstiness means short-window diagnostics are necessary.
- Station and mechanism coverage are contextual constraints, not mandatory filters; mechanism summaries should be reported only where coverage is sufficient.
- Package-contract assumption for analysis tooling:
  - Use standard catalog-processing and plotting workflows rather than model inference.
  - Success evidence should be actual extracted subsets, validated summary tables, and non-empty diagnostic figures for M1/M2/M3.
  - If fitting an Omori-like decay is unstable or unsupported by the windowed counts, report diagnostic failure/fit insufficiency rather than forcing a result.
- Because the request prioritizes reusable scientific outputs, the workflow should produce machine-readable tables for all parameter combinations plus a compact set of publication-style figures.

## Analysis Plan
### 1) Data verification and event matching
- Task description:
  - Read all input tables and verify availability of required fields: origin time, latitude, longitude, depth, magnitude, event identifiers or labels, station coordinates, and focal-mechanism availability flags/fields.
  - Re-match M1, M2, and M3 against the relocated catalog using a small time-location tolerance and select the best matches for sequence anchoring.
- Required data sources:
  - `catalog/Snet_catalog_relocate.csv`
  - `catalog/main_earthquake.csv`
  - `source_mechanism/Snet_mecha.csv`
  - `stations/station.sta`
- Parameter selection strategy:
  - Use mainshock table as the anchor reference, then search the relocated catalog in a narrow neighborhood around each reference event.
  - If exact IDs are absent, match by combined time proximity and hypocentral proximity.
  - Record matching uncertainty and any ambiguity.
- Constraints:
  - Do not assume catalog event IDs exist or are unique.
  - Confirm that time is consistently parsed and that depths/magnitudes are numerically usable.
- Key outputs:
  - Mainshock-to-catalog match table for M1/M2/M3
  - Field-availability audit table
  - Station and mechanism coverage summary

### 2) Sequence extraction across multiple definitions
- Task description:
  - For each of M1, M2, M3, extract event windows around the matched mainshock using combinations of radius, time window, depth window, and magnitude threshold.
- Required data sources:
  - `catalog/Snet_catalog_relocate.csv`
  - matched mainshock table from Task 1
- Parameter selection strategy:
  - Radii: 30, 44, 50, 80, 100 km
  - Time windows: pre-90d, pre-60d, pre-30d, pre-7d, post-7d, post-30d, post-60d, post-90d
  - Depth windows:
    - all depths
    - mainshock-centered local depth window
    - depth-stratified bins
  - Magnitude thresholds:
    - all events
    - M ≥ 1.2
    - M ≥ 1.5
    - M ≥ 2.0
    - M ≥ 2.5 where sample size permits
- Constraints:
  - Use the same extraction logic for all three sequences to enable direct comparison.
  - Keep a record of empty or low-count subsets so parameter sensitivity is transparent.
- Key outputs:
  - Extraction index/table for all M1/M2/M3 combinations
  - Per-sequence event subsets ready for diagnostics

### 3) Sequence diagnostics for each parameter setting
- Task description:
  - Compute event counts, cumulative counts, moving-window rates, pre/post rate ratios, magnitude distributions, depth distributions, and spatial-distance diagnostics for each extracted subset.
  - Evaluate post-event decay behavior with a simple Omori-style fit when event counts support it.
  - Summarize focal-mechanism availability and basic mechanism composition where possible.
- Required data sources:
  - Extracted event subsets from Task 2
  - `source_mechanism/Snet_mecha.csv`
- Parameter selection strategy:
  - Use consistent binning across M1/M2/M3 within each diagnostic family.
  - For moving-window rates, use a window length suitable for bursty seismicity and keep it fixed across sequences.
  - For radial and time-distance plots, calculate distance from each event to the matched mainshock.
  - For mechanism summaries, report counts and proportions only for events with mechanism metadata.
- Constraints:
  - Omori fitting should be attempted only on windows with sufficient post-event counts; otherwise label as not reliable.
  - Do not overinterpret sparse bins or incomplete mechanism coverage.
- Key outputs:
  - Diagnostic summary tables per sequence and parameter setting
  - Decay-fit parameter table or fit-status table
  - Mechanism-availability summary

### 4) Robustness analysis
- Task description:
  - Determine which observed sequence features remain stable when radius, time window, depth window, and magnitude threshold are changed.
  - Separate robust features from parameter-dependent ones.
- Required data sources:
  - Diagnostic tables from Task 3
- Parameter selection strategy:
  - Compare signs and rankings of key metrics across all tested parameter settings:
    - pre/post rate ratios
    - cumulative increase after mainshock
    - concentration near the mainshock
    - depth-mode shifts
    - decay presence/absence
  - Define robustness as persistence of direction and qualitative shape, not only exact numeric agreement.
- Constraints:
  - Treat empty or sparse subsets as non-diagnostic rather than evidence against a pattern.
- Key outputs:
  - Robustness matrix across radii/time windows/depth windows/magnitude thresholds
  - Stable-versus-sensitive feature summary for each mainshock

### 5) Three-sequence comparison
- Task description:
  - Compare M1, M2, and M3 in background activity, pre-event activity, post-event activity, burstiness, decay behavior, spatial concentration, depth structure, magnitude distribution, and sensitivity to sequence definitions.
- Required data sources:
  - Diagnostic tables from Task 3
  - Robustness outputs from Task 4
- Parameter selection strategy:
  - Use the same baseline parameter set for the main cross-sequence comparison, then display how results shift under alternate definitions.
  - Give special attention to:
    - M1 vs M3 spatial enrichment
    - M2 depth distinctness
- Constraints:
  - Use matched comparison windows and identical plotting conventions.
- Key outputs:
  - Cross-sequence comparison table
  - Ranked summary of differences between M1, M2, and M3

### 6) Simple control comparison
- Task description:
  - Build at least one control benchmark to check whether observed sequence features exceed background variability.
- Required data sources:
  - `catalog/Snet_catalog_relocate.csv`
  - matched mainshock times from Task 1
- Parameter selection strategy:
  - Prefer at least one of the following:
    - background windows away from each mainshock
    - randomized mainshock times within the same catalog period
    - higher-magnitude threshold comparison
    - before/after background-rate comparison
  - Keep the control simple and directly comparable to the real sequence windows.
- Constraints:
  - Controls should not overlap the target sequences.
  - If randomized times are used, keep them away from catalog edges and known high-activity intervals where possible.
- Key outputs:
  - Control-vs-event summary table
  - Baseline rate comparison figure/table

### 7) Diagnostic figures
- Task description:
  - Generate publication-style figures for each mainshock and for the three-sequence comparison.
- Required data sources:
  - Outputs from Tasks 2–6
- Parameter selection strategy:
  - Use consistent axes, color scales, and markers across sequences.
  - Include mainshock markers and clearly labeled pre/post intervals.
  - Favor figure sets that directly support robustness testing:
    - event-centered maps for M1, M2, M3
    - pre/post spatial comparison maps
    - cumulative count curves
    - moving-window rate curves
    - post-event decay plots
    - time-distance or radial-distance plots
    - radius and time-window sensitivity heatmaps
    - magnitude-threshold sensitivity plots
    - depth-stratified sequence plots
    - three-sequence summary figure
- Constraints:
  - Figures should be comparable across sequences and parameter settings.
  - Do not create decorative figures that do not support the scientific questions.
- Key outputs:
  - Figure set for M1/M2/M3 event-centered analysis
  - Robustness heatmaps and sensitivity panels
  - Summary comparison figure

### 8) Final reusable outputs
- Task description:
  - Consolidate analysis products into reusable tables and figure manifests for later focused interpretation of M1/M2/M3.
- Required data sources:
  - Outputs from all prior tasks
- Parameter selection strategy:
  - Keep one compact summary table per mainshock plus one global robustness table.
- Constraints:
  - Preserve enough metadata to reproduce each subset definition.
- Key outputs:
  - Machine-readable summary tables
  - Figure inventory with parameter settings
  - Final comparison-ready dataset bundles for M1, M2, and M3