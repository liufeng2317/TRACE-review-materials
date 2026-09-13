# Goal
Perform event-centered sequence analysis for the three matched major earthquakes in the Aomori regional relocated catalog, comparing pre- and post-event seismicity evolution for M1, M2, and M3, and testing robustness against changes in spatial, temporal, depth, and magnitude definitions.

## Planning Assumptions
- Primary observation data are sufficient and should be used as the main basis for all sequence analyses.
- Main working files:
  - relocated regional catalog: `catalog/Snet_catalog_relocate.csv`
  - mainshock reference table: `catalog/main_earthquake.csv`
  - focal-mechanism/source-property catalog: `source_mechanism/Snet_mecha.csv`
  - station metadata: `stations/station.sta`
- Package/data processing constraints:
  - First verify all required fields for time, latitude, longitude, depth, magnitude, and event identifiers where available.
  - Re-match the three mainshocks to the relocated catalog using tolerant time and location matching before extraction, since relocation may shift reported origin times or coordinates slightly.
  - Use the provided completeness guidance as a screening baseline: test `Mc ≈ 1.2` and then higher magnitude thresholds.
  - Station coverage and focal-mechanism availability are uneven, so mechanism-related outputs are contextual diagnostics rather than required for every sequence window.
- Package contract summary for sequence diagnostics:
  - No specialized external package is mandated by the request.
  - Core outputs should be reproducible from catalog tables with standard scientific analysis routines.
  - Any Omori-style fitting should be treated as an optional simple diagnostic and only retained if the fit is stable and data support it.

## Analysis Plan
### 1. Minimal data verification and mainshock re-matching
- Task description:
  - Load all four files and verify column availability, data types, missing values, and time parsing.
  - Confirm that the relocated catalog includes the fields needed for event-centered analysis.
  - Match M1, M2, and M3 from `main_earthquake.csv` to the relocated catalog using a small tolerance in time and location, and record the matched catalog event IDs if present.
- Required data sources:
  - `catalog/Snet_catalog_relocate.csv`
  - `catalog/main_earthquake.csv`
  - `source_mechanism/Snet_mecha.csv`
  - `stations/station.sta`
- Parameter selection strategy:
  - Use the mainshock table as the anchor list.
  - Allow small tolerances in origin time and hypocentral distance for re-matching after relocation.
  - Verify mechanism/station availability by intersecting sequence windows with these metadata tables.
- Constraints:
  - Do not assume exact equality between the mainshock table and relocated catalog.
  - Preserve the original mainshock labels M1/M2/M3 after rematching.
- Key outputs:
  - Field-check summary table
  - Matched mainshock registry with rematched catalog identifiers
  - Missing-data and coverage diagnostics for station/mechanism tables

### 2. Sequence extraction under multiple definitions
- Task description:
  - For each matched mainshock, extract surrounding events under a matrix of spatial, temporal, depth, and magnitude settings.
  - Build a consistent event-centered subset for each parameter combination.
- Required data sources:
  - `catalog/Snet_catalog_relocate.csv`
  - matched mainshock registry from Task 1
- Parameter selection strategy:
  - Radii: 30, 44, 50, 80, 100 km
  - Time windows: pre-90d, pre-60d, pre-30d, pre-7d, post-7d, post-30d, post-60d, post-90d
  - Depth windows:
    - all depths
    - mainshock-centered local depth window
    - depth-stratified bins suitable for regional clustering
  - Magnitude thresholds:
    - all events
    - M >= 1.2
    - M >= 1.5
    - M >= 2.0
    - M >= 2.5 where sample size remains usable
- Constraints:
  - Keep a consistent event-centered time origin at the mainshock origin time.
  - Use the same spatial reference and geodesic distance method across all sequences.
  - Avoid over-filtering windows that become too sparse for comparison; flag them separately.
- Key outputs:
  - A structured set of event-centered sequence tables for M1, M2, and M3
  - Metadata describing which combinations are sufficiently populated
  - Sparse-window flags for later robustness interpretation

### 3. Sequence diagnostics and quantitative summaries
- Task description:
  - For each sequence and parameter setting, compute event counts, cumulative counts, moving-window rates, pre/post rate ratios, magnitude distributions, depth distributions, and time-distance/radial-distance patterns.
  - Estimate post-event decay behavior with a simple Omori-style fit only when the post-event sample supports it.
  - Summarize focal-mechanism availability within each window and compute simple mechanism counts or class summaries where feasible.
- Required data sources:
  - Event-centered sequence tables from Task 2
  - `source_mechanism/Snet_mecha.csv`
  - `stations/station.sta`
- Parameter selection strategy:
  - Use multiple moving-window lengths only if they are consistent across the three sequences.
  - Define pre/post rate ratios using matched pre-event and post-event windows of equal duration whenever possible.
  - For Omori-style diagnostics, fit only to post-event windows with sufficient counts and avoid over-interpreting unstable fits.
- Constraints:
  - Keep diagnostics comparable across M1/M2/M3.
  - Treat mechanism summaries as optional if event matching to the mechanism table is incomplete.
- Key outputs:
  - Summary tables of counts, rates, ratios, and distribution statistics
  - Post-event decay parameter estimates or fit-quality flags
  - Mechanism/station coverage tables by sequence window

### 4. Robustness analysis across sequence definitions
- Task description:
  - Evaluate which observed features remain stable when changing radius, time window, depth window, and magnitude threshold.
  - Distinguish robust sequence behavior from parameter-sensitive behavior.
- Required data sources:
  - Diagnostic summaries from Task 3
- Parameter selection strategy:
  - Compare results across the full parameter grid rather than a single preferred window.
  - Define robustness by consistency of directional changes, ranking, and qualitative pattern persistence across settings.
- Constraints:
  - Report instability explicitly for sparse or marginal windows.
  - Avoid treating one parameter choice as canonical unless supported by repeated agreement.
- Key outputs:
  - Robustness matrix or ranking table
  - Stable vs parameter-dependent feature summary
  - Sensitivity flags for each mainshock

### 5. Three-sequence comparison and simple controls
- Task description:
  - Compare M1, M2, and M3 in background activity, pre-event activity, post-event activity, burstiness, decay, spatial concentration, depth structure, magnitude distribution, and sensitivity to definition choices.
  - Include at least one feasible control comparison.
- Required data sources:
  - Diagnostic summaries from Task 3
  - Event-centered sequence tables from Task 2
- Parameter selection strategy:
  - Use comparable time horizons and magnitude thresholds across all three earthquakes for direct comparison.
  - For controls, prefer at least one of:
    - background windows away from mainshock times
    - randomized mainshock-time surrogates
    - higher-threshold background-rate comparison
  - Prefer the control that is simplest to interpret and best supported by data volume.
- Constraints:
  - Control windows must avoid overlap with mainshock-centered windows.
  - Comparisons should retain the same filtering rules as the primary analysis.
- Key outputs:
  - M1/M2/M3 comparison table
  - Control-vs-event contrast table
  - Sequence ranking by activity level, burstiness, and decay strength

### 6. Diagnostic figures for publication-style presentation
- Task description:
  - Generate a compact figure set suitable for a publication-quality sequence-analysis story.
  - Use consistent axes, symbols, and mainshock markers across all three events.
- Required data sources:
  - Event-centered sequences and diagnostics from Tasks 2–5
- Parameter selection strategy:
  - Show at least one representative window per mainshock plus one sensitivity panel per major dimension:
    - event-centered maps
    - pre/post spatial comparison maps
    - cumulative count curves
    - moving-window rate curves
    - post-event decay plots
    - time-distance or radial-distance plots
    - radius and time-window sensitivity heatmaps
    - magnitude-threshold sensitivity plots
    - depth-stratified sequence plots
    - three-sequence summary comparison figure
- Constraints:
  - Keep annotations consistent across panels.
  - Use the same color semantics for pre-event, co-event/mainshock, and post-event phases.
  - Ensure each figure corresponds to validated underlying tables.
- Key outputs:
  - Figure set covering M1, M2, and M3
  - Sensitivity heatmaps and summary comparison figure
  - Representative event-centered maps and temporal evolution plots

### 7. Reusable analysis artifacts
- Task description:
  - Export compact machine-readable tables that can support later M1-M3 focused interpretation or follow-on analyses.
- Required data sources:
  - Outputs from Tasks 1–5
- Parameter selection strategy:
  - Keep exports focused on validated summaries rather than all raw intermediate subsets.
- Constraints:
  - Do not replace scientific outputs with narrative-only artifacts.
- Key outputs:
  - Mainshock match table
  - Sequence summary tables
  - Robustness/sensitivity tables
  - Figure-ready data tables