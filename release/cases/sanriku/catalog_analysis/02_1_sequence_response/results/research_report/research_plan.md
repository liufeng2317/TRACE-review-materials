# Goal
Perform event-centered sequence analysis for the three matched major earthquakes in the Aomori regional relocated catalog, compare pre- and post-event seismicity evolution around M1, M2, and M3, and test whether observed sequence patterns are robust to alternative spatial, temporal, depth, and magnitude definitions.

## Planning Assumptions
- Use observation data only; the relocated regional catalog is the primary scientific table.
- Required input tables:
  - `catalog/Snet_catalog_relocate.csv`
  - `catalog/main_earthquake.csv`
  - `source_mechanism/Snet_mecha.csv`
  - `stations/station.sta`
- Minimal package/program contract:
  - No specialized external analysis package is required for the core sequence study.
  - The workflow must first validate fields, then rematch M1/M2/M3 to the relocated catalog, then extract event-centered subsets, and only then compute diagnostics and figures.
  - Success evidence must be non-empty validated tables and figure-ready outputs, not placeholder or schema-only results.
- Mainshock rematching is required because relocation may shift origin time, coordinates, and catalog identifiers slightly.
- Completeness guidance:
  - Use Mc ≈ 1.2 as the baseline screening threshold.
  - Repeat key diagnostics at higher magnitude thresholds to test robustness.
- Sequence behavior is expected to be clustered and burst-like, so short-window sensitivity must be explicitly evaluated.
- M1 and M3 are expected to be spatially enriched; M2 may require depth stratification.
- Station coverage and focal-mechanism availability are contextual limitations; mechanism summaries should be reported only where coverage is sufficient.
- Omori-style decay fitting is optional and should be retained only when post-event counts and time span support a stable fit.

## Analysis Plan
### 1. Minimal data verification and mainshock rematching
- Task description:
  - Read the four source files.
  - Verify required fields for sequence analysis: time, latitude, longitude, depth, magnitude, event ID if available, mainshock records, station coordinates, and focal-mechanism availability.
  - Rematch M1, M2, and M3 to the relocated catalog using tolerant time and location matching.
- Required data sources:
  - `catalog/Snet_catalog_relocate.csv`
  - `catalog/main_earthquake.csv`
  - `source_mechanism/Snet_mecha.csv`
  - `stations/station.sta`
- Parameter selection strategy:
  - Use mainshock records as anchors.
  - Match by combined origin-time proximity and hypocentral proximity, with magnitude consistency as a secondary check if needed.
  - If multiple candidates exist, choose the best joint time-location match and record all close candidates.
- Constraints:
  - Do not assume exact equality of time, coordinates, or event IDs between tables.
  - Preserve M1/M2/M3 labels after rematching.
  - Treat missing mechanism or station fields as contextual gaps, not analysis-stopping errors.
- Key outputs:
  - Field-availability audit table by file
  - Matched mainshock registry for M1, M2, M3 with relocated catalog identifiers and match diagnostics
  - Coverage summary for station and mechanism metadata

### 2. Event-centered sequence extraction
- Task description:
  - For each matched mainshock, extract surrounding events under multiple definitions of spatial radius, time window, depth window, and magnitude threshold.
  - Build a standardized event-centered sequence table for each parameter combination.
- Required data sources:
  - `catalog/Snet_catalog_relocate.csv`
  - matched mainshock registry from Task 1
- Parameter selection strategy:
  - Radii: 30, 44, 50, 80, 100 km
  - Time windows: pre-90d, pre-60d, pre-30d, pre-7d, post-7d, post-30d, post-60d, post-90d
  - Depth windows:
    - all depths
    - local mainshock-centered depth window
    - depth-stratified bins
  - Magnitude thresholds:
    - all events
    - M ≥ 1.2
    - M ≥ 1.5
    - M ≥ 2.0
    - M ≥ 2.5 where feasible
- Constraints:
  - Use the same extraction logic for all three mainshocks.
  - Keep the event-centered time origin fixed at each mainshock origin time.
  - Record empty and sparse combinations explicitly so robustness interpretation is transparent.
- Key outputs:
  - Event-centered subset tables for each mainshock and parameter combination
  - Extraction count matrix by radius, time window, depth window, and magnitude threshold
  - Sparse-window flags for later robustness analysis

### 3. Sequence diagnostics
- Task description:
  - Quantify seismicity evolution for each extracted sequence and parameter setting.
  - Compute event counts, cumulative counts, moving-window seismicity rates, pre/post rate ratios, magnitude distributions, depth distributions, time-distance and radial-distance patterns, spatial concentration or expansion indicators, and post-event decay diagnostics.
  - Summarize focal-mechanism availability within sequence windows.
- Required data sources:
  - Event-centered sequence tables from Task 2
  - `source_mechanism/Snet_mecha.csv`
  - `stations/station.sta`
- Parameter selection strategy:
  - Use consistent moving-window definitions across M1/M2/M3.
  - Compute pre/post rate ratios from matched windows of equal duration whenever possible.
  - Estimate Omori-style decay only for post-event windows with sufficient counts and span.
  - Summarize mechanism presence as coverage-limited diagnostics, not as complete focal-mechanism cataloging.
- Constraints:
  - Do not force decay fitting for sparse post-event windows.
  - Treat mechanism summaries as conditional on available overlaps.
  - Use the same mainshock reference coordinates and origin times for all derived distances within each event.
- Key outputs:
  - Diagnostic summary tables of counts, cumulative counts, rates, ratios, magnitude distributions, and depth distributions
  - Post-event decay-fit parameter table with fit-quality flags
  - Radial-distance and time-distance diagnostics relative to each mainshock
  - Spatial concentration/expansion indicators
  - Mechanism availability and simple mechanism summary tables

### 4. Robustness analysis
- Task description:
  - Determine which observed sequence features remain stable as radius, time window, depth window, and magnitude threshold change.
  - Separate robust patterns from parameter-dependent patterns.
- Required data sources:
  - Diagnostic tables from Task 3
  - Extraction summary matrix from Task 2
- Parameter selection strategy:
  - Compare the full parameter grid rather than a single preferred window.
  - Assess robustness by persistence of sign, ranking, and qualitative shape across settings.
  - Use Mc ≈ 1.2 as the baseline comparison and higher thresholds as robustness checks.
- Constraints:
  - Sparse subsets are non-diagnostic, not negative evidence.
  - Do not treat one parameter choice as canonical unless it is repeatedly supported.
- Key outputs:
  - Robustness matrix for each mainshock
  - Stable vs parameter-dependent feature summary
  - Sensitivity flags for radius, time window, depth window, and magnitude threshold

### 5. Three-sequence comparison
- Task description:
  - Compare M1, M2, and M3 in terms of background activity, pre-event activity, post-event activity, burstiness, aftershock decay behavior, spatial concentration or expansion, depth structure, magnitude distribution, and sensitivity to sequence definitions.
- Required data sources:
  - Diagnostic tables from Task 3
  - Robustness summaries from Task 4
- Parameter selection strategy:
  - Use a common baseline parameter set for direct comparison first.
  - Then summarize how conclusions shift under alternate definitions.
  - Give special attention to M1/M3 local enrichment and M2 depth distinctness.
- Constraints:
  - Keep metric definitions identical across the three sequences when comparing directly.
  - Distinguish physical differences from sample-size or coverage effects.
- Key outputs:
  - Cross-event comparison table
  - Ranked summary of M1 vs M2 vs M3 for each major metric
  - Comparison-ready summary dataset for later focused analysis

### 6. Simple control comparison
- Task description:
  - Include at least one feasible control to test whether observed sequence behavior exceeds background variation.
- Required data sources:
  - `catalog/Snet_catalog_relocate.csv`
  - matched mainshock times from Task 1
- Parameter selection strategy:
  - Use one or more of:
    - background windows away from each mainshock
    - randomized mainshock times within the catalog span
    - higher magnitude-threshold comparison
    - simple pre/post background-rate comparison
  - Match control window lengths and radii to the real sequence windows when feasible.
- Constraints:
  - Control windows must not overlap the event-centered study windows.
  - Randomized times must avoid catalog edges and strong truncation effects.
- Key outputs:
  - Control comparison table
  - Background-rate benchmark statistics
  - Observed-versus-control difference metrics

### 7. Diagnostic figures
- Task description:
  - Produce publication-quality figures supporting the sequence interpretation and robustness assessment.
- Required data sources:
  - Event-centered subsets and diagnostics from Tasks 2–6
- Parameter selection strategy:
  - Use consistent axes, color scales, legends, and mainshock markers across M1/M2/M3.
  - Build the figure set around validated tables and summary metrics.
- Constraints:
  - Figures must reflect the same window definitions used in the tables.
  - Do not mix incompatible normalization choices in comparison panels.
- Key outputs:
  - Event-centered maps for M1, M2, and M3
  - Pre/post spatial comparison maps
  - Cumulative count curves
  - Moving-window rate curves
  - Post-event decay plots
  - Time-distance or radial-distance plots relative to each mainshock
  - Radius and time-window sensitivity heatmaps
  - Magnitude-threshold sensitivity plots
  - Depth-stratified sequence plots
  - Three-sequence comparison summary figure

### 8. Reusable analysis products
- Task description:
  - Package validated results into machine-readable outputs for downstream reuse.
- Required data sources:
  - Outputs from Tasks 1–7
- Parameter selection strategy:
  - Export compact tables organized by mainshock and parameter setting.
  - Preserve metadata for window definitions, thresholds, and control type.
- Constraints:
  - Do not replace scientific outputs with narrative-only artifacts.
- Key outputs:
  - Master mainshock-match table
  - Sequence summary tables
  - Robustness and sensitivity tables
  - Control-comparison table
  - Figure-ready data tables for all diagnostics and sensitivity plots