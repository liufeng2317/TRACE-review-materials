# Goal
Perform event-centered sequence analysis for the three matched major earthquakes (M1, M2, M3) in the Aomori regional relocated catalog, quantify pre/post seismicity evolution under multiple spatial-temporal-depth-magnitude definitions, and identify robust versus parameter-dependent sequence features with a control comparison and publication-quality diagnostic figures.

## Planning Assumptions
- Primary observation data should be used: relocated regional catalog, mainshock reference table, mechanism catalog, and station inventory.
- Package/API contract not required for the core analysis unless a specific library is chosen later; this plan is data- and analysis-driven.
- Mainshocks must be re-matched to the relocated catalog before extraction using tolerant time/location matching because relocation may shift origin time, coordinates, or catalog identifiers.
- Full-catalog completeness is not assumed uniform; use Mc ≈ 1.2 as a screening threshold and test higher thresholds.
- Sequence windows should be evaluated as a grid of radius, time window, depth, and magnitude-threshold settings, then summarized for robustness rather than relying on a single preferred definition.
- M2 may require separate depth-stratified interpretation; M1 and M3 may show stronger local clustering and should be compared with matched settings.
- Station coverage and focal-mechanism availability are contextual, not guaranteed, so mechanism summaries should be conditional on availability and explicitly report coverage fractions.
- “High-quality figures” should be generated as reusable analysis outputs, but figure-rendering settings are not specified here.

## Analysis Plan

### 1) Minimal data verification and mainshock re-matching
- Task description:
  - Read all four source files and verify required fields exist for sequence analysis.
  - Build a reliable match between M1, M2, M3 and the relocated catalog.
- Required data sources:
  - `catalog/Snet_catalog_relocate.csv`
  - `catalog/main_earthquake.csv`
  - `source_mechanism/Snet_mecha.csv`
  - `stations/station.sta`
- Parameter selection strategy:
  - Use catalog time, latitude, longitude, depth, magnitude, and event-ID-like fields if present.
  - Match each mainshock by combined time proximity and spatial proximity; if multiple candidates exist, prioritize the closest joint time-location match and verify magnitude consistency.
  - Accept small shifts caused by relocation; keep a traceable matching table with alternative candidates if ambiguity remains.
- Constraints:
  - Do not assume identical event IDs across tables.
  - If a field is missing, record it and continue only if a minimal substitute exists.
- Key outputs:
  - Field-availability checklist for each file.
  - Mainshock-to-catalog matched table for M1/M2/M3.
  - QA table of any ambiguities or unmatched records.

### 2) Sequence extraction around each mainshock
- Task description:
  - Extract event-centered catalogs around M1, M2, and M3 for all requested radii, time windows, depth windows, and magnitude thresholds.
- Required data sources:
  - `catalog/Snet_catalog_relocate.csv`
  - `catalog/main_earthquake.csv`
- Parameter selection strategy:
  - Radii: 30, 44, 50, 80, 100 km.
  - Time windows: pre-90d, pre-60d, pre-30d, pre-7d, post-7d, post-30d, post-60d, post-90d.
  - Depth windows:
    - all depths,
    - local mainshock-centered depth window,
    - depth-stratified windows.
  - Magnitude thresholds:
    - all events,
    - M ≥ 1.2,
    - M ≥ 1.5,
    - M ≥ 2.0,
    - M ≥ 2.5 where sample size permits.
  - Define a consistent local depth window centered on each mainshock depth using a documented symmetric interval; use the same rule for all three events.
  - Depth-stratified bins should be chosen to preserve interpretability and sufficient counts, then applied consistently across the three sequences.
- Constraints:
  - Keep extraction nested so that all smaller windows are subsets of the same matched mainshock-centered reference window.
  - Record sample-size limits for sparse combinations; do not force statistics when counts are too low.
- Key outputs:
  - Sequence tables for each mainshock and each parameter combination.
  - Metadata table summarizing counts per window/radius/depth/magnitude setting.

### 3) Sequence diagnostics for each setting
- Task description:
  - Compute event-rate, size, depth, and spatial diagnostics for each extracted sequence.
- Required data sources:
  - `catalog/Snet_catalog_relocate.csv`
  - `source_mechanism/Snet_mecha.csv`
  - `stations/station.sta`
- Parameter selection strategy:
  - Event counts and cumulative counts from the extracted windows.
  - Moving-window seismicity rates using a fixed, documented smoothing window applied consistently across all sequences.
  - Pre/post rate ratios computed for matched pre-event and post-event windows.
  - Magnitude distributions and depth distributions for each sequence and time slice.
  - Post-event decay diagnostics using simple Omori-style fitting if event counts and time span are sufficient.
  - Time-distance and radial-distance patterns relative to the mainshock epicenter and origin time.
  - Spatial concentration/expansion indicators such as median radial distance change, convex-hull-like extent proxy, or percentile-based distance growth.
  - Focal-mechanism availability fractions and simple summaries only where mechanism records overlap the extracted sequence.
- Constraints:
  - Omori-style fitting only if post-event counts are adequate; otherwise flag as not reliable.
  - Mechanism summaries should distinguish between catalog coverage and actual focal-mechanism-bearing events.
  - Use the same reference mainshock coordinates and time for all derived diagnostics within an event.
- Key outputs:
  - Per-event diagnostic tables for rates, ratios, magnitude/depth summaries, and spatial metrics.
  - Mechanism-coverage summary table.
  - Decay-fit parameter table with fit-quality flags.

### 4) Robustness analysis across parameter choices
- Task description:
  - Determine which sequence patterns persist across radii, time windows, depth choices, and magnitude thresholds.
- Required data sources:
  - Derived sequence tables from Task 2 and diagnostics from Task 3.
- Parameter selection strategy:
  - Compare signs and relative ordering of key metrics across the full grid of settings:
    - pre/post rate ratio,
    - cumulative growth shape,
    - depth concentration,
    - radial concentration,
    - decay behavior.
  - Treat a feature as robust if it appears consistently across multiple radii and magnitude thresholds and does not flip with modest time-window changes.
- Constraints:
  - Avoid over-interpreting unstable metrics from small samples.
  - Separate “robust” from “parameter-sensitive” findings explicitly.
- Key outputs:
  - Robustness matrix by mainshock and parameter setting.
  - Summary of stable versus unstable sequence characteristics.
  - Sensitivity ranking of the strongest controls on the observed patterns.

### 5) Three-sequence comparison
- Task description:
  - Compare M1, M2, and M3 side by side in background activity, pre-event activity, post-event activity, burstiness, decay behavior, spatial concentration, depth structure, magnitude distribution, and sensitivity.
- Required data sources:
  - Derived outputs from Tasks 2–4.
- Parameter selection strategy:
  - Use a common comparison baseline where possible:
    - same radius,
    - same magnitude threshold,
    - same pre/post windows,
    - same depth treatment.
  - Then highlight where M2 requires depth-stratified treatment and where M1/M3 show stronger local clustering.
- Constraints:
  - Use identical metric definitions for the three events when comparing directly.
  - Report differences due to data availability or sample size separately from physical differences.
- Key outputs:
  - Cross-event comparison table.
  - Ranked comparison of M1 vs M2 vs M3 for each major metric.
  - A concise comparison-ready dataset for later focused analysis.

### 6) Simple control comparison
- Task description:
  - Include at least one control to test whether the observed sequence behavior exceeds background variation.
- Required data sources:
  - `catalog/Snet_catalog_relocate.csv`
  - `catalog/main_earthquake.csv`
- Parameter selection strategy:
  - Use one or more feasible controls:
    - background windows away from each mainshock time,
    - randomized mainshock times within the same catalog span,
    - direct background-rate comparison before versus after each mainshock,
    - higher magnitude-threshold comparison as a sparsity-aware control.
  - Keep the control design simple and matched to the same spatial window used in the main analysis.
- Constraints:
  - Randomized mainshock times must avoid overlaps with actual event-centered windows.
  - Control windows should preserve the same radius and magnitude threshold when feasible.
- Key outputs:
  - Control-vs-observed comparison table.
  - Control diagnostics showing whether the event-centered sequence stands out from background variability.

### 7) Diagnostic figures
- Task description:
  - Produce a coordinated figure suite for publication-style interpretation and robustness assessment.
- Required data sources:
  - Derived outputs from Tasks 1–6.
- Parameter selection strategy:
  - Figure set should include, at minimum:
    - event-centered maps for M1, M2, M3,
    - pre/post spatial comparison maps,
    - cumulative count curves,
    - moving-window rate curves,
    - post-event decay plots,
    - time-distance or radial-distance plots,
    - radius and time-window sensitivity heatmaps,
    - magnitude-threshold sensitivity plots,
    - depth-stratified sequence plots,
    - three-sequence comparison summary figure.
  - Keep axes, color scales, legend structure, and mainshock markers consistent across M1/M2/M3.
- Constraints:
  - Figures should directly reflect the same window definitions used in the tables.
  - The summary figure should be built from validated metrics only.
- Key outputs:
  - Figure panel set for each mainshock and combined comparison panels.
  - Sensitivity heatmaps and summary plots suitable for a manuscript or appendix.

### 8) Final reusable analysis tables
- Task description:
  - Consolidate outputs into machine-readable tables for reuse in later analysis stages.
- Required data sources:
  - All derived outputs from Tasks 1–6.
- Parameter selection strategy:
  - Export one master event-window table, one diagnostics table, one robustness table, and one control-comparison table.
- Constraints:
  - Tables should preserve the event label, parameter setting, and sample-size context.
- Key outputs:
  - Master sequence catalog table.
  - Robustness summary table.
  - Cross-event comparison table.
  - Control summary table.