# Goal
Perform event-centered sequence analysis for the three matched major earthquakes (M1, M2, M3) in the Aomori regional relocated catalog, quantify pre/post seismicity changes under multiple space-time-depth-magnitude definitions, and identify robust versus parameter-dependent sequence features with a simple control comparison.

## Planning Assumptions
- Primary observational sources are the relocated regional catalog `catalog/Snet_catalog_relocate.csv`, the mainshock reference table `catalog/main_earthquake.csv`, focal-mechanism catalog `source_mechanism/Snet_mecha.csv`, and station inventory `stations/station.sta`.
- The main catalog is suitable for event-centered extraction; the three mainshocks should be re-matched to the relocated catalog using both time proximity and location proximity to account for relocation shifts.
- Use the preliminary completeness threshold Mc ≈ 1.2 as the baseline screening magnitude, then repeat analyses at higher thresholds for robustness.
- Sequence results should be evaluated separately for M1, M2, and M3, with M2 explicitly checked for depth-stratified behavior.
- Station coverage and focal-mechanism availability are contextual limitations; mechanism summaries should be treated as coverage-limited diagnostics rather than complete source characterization.
- Package/program contract: no external analysis package is mandated by the request; the workflow should be built from catalog-based analysis and plotting steps, with explicit validation of the matched event list, extraction windows, and non-empty outputs before interpreting any result.
- Success evidence should include: verified input fields, matched mainshock IDs, non-empty extracted subsets for the requested windows, tabulated diagnostics, and figures for each mainshock plus comparison summaries.

## Analysis Plan
### 1) Minimal data verification and mainshock rematching
- Task description: Read all required tables, verify field availability, and rematch M1/M2/M3 into the relocated catalog before any extraction.
- Required data sources:
  - `catalog/Snet_catalog_relocate.csv`
  - `catalog/main_earthquake.csv`
  - `source_mechanism/Snet_mecha.csv`
  - `stations/station.sta`
- Parameter selection strategy:
  - Use catalog time, latitude, longitude, depth, magnitude, and any event ID fields present.
  - Rematching criteria should combine small absolute time difference and spatial proximity; if multiple candidates exist, select the best joint match and document tie-breaking.
  - Use the mainshock records as anchors for all later windows.
- Constraints:
  - Verify time parsing, coordinate units, depth units, and magnitude type consistency.
  - Confirm whether station and mechanism tables have event keys or only contextual metadata.
- Key outputs:
  - Input validation table
  - Matched mainshock table with relocated catalog IDs/indices
  - Basic catalog summary statistics for the full regional dataset
  - Data-quality notes on missing fields and coverage limits

### 2) Event-centered sequence extraction
- Task description: Extract event subsets around each mainshock using multiple radii, time windows, depth windows, and magnitude thresholds.
- Required data sources:
  - `catalog/Snet_catalog_relocate.csv`
  - rematched mainshock table from Task 1
- Parameter selection strategy:
  - Radii: 30, 44, 50, 80, 100 km
  - Time windows: pre-90d, pre-60d, pre-30d, pre-7d, post-7d, post-30d, post-60d, post-90d
  - Depth windows: all depths; mainshock-centered local depth windows; depth-stratified bins
  - Magnitude thresholds: all events, M ≥ 1.2, 1.5, 2.0, 2.5 where event counts remain sufficient
  - Define extraction windows consistently for all three mainshocks to enable comparison
- Constraints:
  - Ensure each combination produces a labeled subset, even if empty, so missingness is explicit.
  - Avoid over-interpreting sparsely populated bins.
- Key outputs:
  - Event-centered subset tables for each mainshock and parameter combination
  - Extraction summary matrix with counts by radius/time/depth/magnitude setting
  - Flags for low-sample combinations

### 3) Sequence diagnostics for each mainshock
- Task description: Compute core sequence metrics for each extracted subset.
- Required data sources:
  - Event-centered subsets from Task 2
  - Mechanism and station tables for context-dependent summaries
- Parameter selection strategy:
  - Use consistent binning for time series and radial series across M1/M2/M3.
  - Compute rates and distributions both in absolute counts and normalized forms where useful.
  - For Omori-style decay, fit only post-event windows with enough events to support a stable estimate.
- Constraints:
  - Do not fit decay curves where the post-event sample is too sparse.
  - Keep rate windows identical across mainshocks when comparing shapes.
- Key outputs:
  - Event counts by window
  - Cumulative count curves
  - Moving-window seismicity rates
  - Pre/post rate ratios
  - Magnitude distribution summaries
  - Depth distribution summaries
  - Post-event decay diagnostics and fit parameters where feasible
  - Time-distance and radial-distance summaries
  - Spatial concentration/expansion indicators
  - Mechanism-availability counts and simple mechanism summaries

### 4) Robustness analysis across definitions
- Task description: Test whether observed sequence features persist across alternative radii, time windows, depth windows, and magnitude thresholds.
- Required data sources:
  - Diagnostic outputs from Task 3
  - Extraction summary matrix from Task 2
- Parameter selection strategy:
  - Compare the same feature class under all radii and thresholds.
  - Treat M ≥ 1.2 as the baseline and higher thresholds as robustness checks.
  - For depth, compare all-depth results with depth-stratified behavior and mainshock-centered local depth windows.
- Constraints:
  - Focus on features that repeat across parameter choices, not isolated single-setting anomalies.
  - Record where behavior changes materially with parameter choice.
- Key outputs:
  - Robustness matrix of feature stability
  - Classification of patterns as robust, conditionally robust, or parameter-dependent
  - Sensitivity tables for radius, time window, depth window, and magnitude threshold

### 5) Three-sequence comparison
- Task description: Compare M1, M2, and M3 in a consistent framework.
- Required data sources:
  - Diagnostic outputs from Task 3
  - Robustness summaries from Task 4
- Parameter selection strategy:
  - Compare the same radius/time/magnitude baseline across all three sequences first, then summarize differences across sensitivity settings.
  - Use the same rate and distribution definitions for each mainshock.
- Constraints:
  - Preserve consistent axes and normalization choices across M1/M2/M3.
  - Distinguish genuine inter-sequence differences from sample-size effects.
- Key outputs:
  - Cross-event comparison table for background activity, pre-event activity, post-event activity, burstiness, decay behavior, spatial concentration, depth structure, magnitude distribution, and sensitivity
  - Ranked comparison of which mainshock shows the strongest/weakest sequence signature

### 6) Simple control comparison
- Task description: Evaluate sequence significance against at least one background or randomized control.
- Required data sources:
  - Full relocated catalog
  - Mainshock times from Task 1
- Parameter selection strategy:
  - Use one or more feasible controls: background windows away from each mainshock, randomized mainshock times within the catalog span, and/or pre/post background-rate comparisons.
  - Match control window lengths and radii to the real sequence windows.
- Constraints:
  - Controls must be directly comparable in duration and spatial window to the real event-centered analysis.
  - Exclude controls that overlap major sequence windows or catalog gaps.
- Key outputs:
  - Control comparison table
  - Background-rate benchmark statistics
  - Difference metrics for observed versus control sequences

### 7) Diagnostic figures
- Task description: Produce publication-quality figures for each sequence and for the three-sequence comparison.
- Required data sources:
  - Event-centered subsets and diagnostic outputs from Tasks 2–6
- Parameter selection strategy:
  - Use consistent color scales, symbols, and axis conventions across all three mainshocks.
  - Include the same mainshock marker style in all event-centered plots.
- Constraints:
  - Figures should prioritize comparability and interpretability over visual complexity.
  - Do not mix incompatible normalization schemes in a single comparison figure.
- Key outputs:
  - Event-centered maps for M1, M2, M3
  - Pre/post spatial comparison maps
  - Cumulative count curves
  - Moving-window rate curves
  - Post-event decay plots
  - Time-distance or radial-distance plots
  - Radius and time-window sensitivity heatmaps
  - Magnitude-threshold sensitivity plots
  - Depth-stratified sequence plots
  - Three-sequence summary figure

### 8) Final synthesis outputs for reuse
- Task description: Assemble reusable tables and compact summaries suitable for later focused analysis on M1–M3.
- Required data sources:
  - Outputs from Tasks 1–7
- Parameter selection strategy:
  - Keep summary tables structured by mainshock and by parameter setting.
  - Preserve metadata for window definitions and control types.
- Constraints:
  - Summary products should remain machine-readable and traceable to the underlying parameter choices.
- Key outputs:
  - Master results table
  - Robustness summary table
  - Control-comparison table
  - Figure inventory with file names and mainshock coverage