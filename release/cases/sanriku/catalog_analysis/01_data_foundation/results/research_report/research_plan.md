# Goal
Build a reliable observational data foundation for the Aomori/Japan regional catalog, match the major earthquakes to the relocated catalog, characterize regional seismicity background and station/focal-mechanism context, generate publication-quality diagnostic figures, and prepare reusable Stage-1 products for downstream sequence analysis.

## Planning Assumptions
- Use observation data only: relocated regional catalog, major-earthquake reference table, source-mechanism catalog, and station inventory.
- Core data sources:
  - `catalog/Snet_catalog_relocate.csv`
  - `catalog/main_earthquake.csv`
  - `source_mechanism/Snet_mecha.csv`
  - `stations/station.sta`
- Package/workflow contracts relevant to implementation:
  - Tabular parsing must preserve raw columns and produce validated cleaned fields before any matching or statistical summaries.
  - Time parsing should use the file’s actual datetime/origin-time fields; do not infer temporal precision from decimal places.
  - Spatial matching and local-context summaries must use one consistent geographic distance method across the workflow.
  - Completeness magnitude Mc and Gutenberg–Richter b-value should be estimated from the cleaned catalog using a documented, data-driven magnitude binning and fitting range.
  - Focal-mechanism analysis must separate availability from mechanism-property analysis because coverage may be partial.
  - Success evidence requires non-empty cleaned tables, match tables, summary metrics, and saved figure files; diagnostic or fallback outputs are not sufficient.
- Stage-1 catalog requirements:
  - Preserve original values where valid.
  - Include parsed origin time, latitude, longitude, depth, magnitude, event ID if available, and explicit quality flags.
  - Keep a raw-audit view alongside cleaned outputs.
- Matching requirements:
  - Allow a small relocation-induced time shift, but require spatial and depth consistency.
  - If multiple candidates are close, flag ambiguity rather than forcing a match.
- Figure requirements:
  - Save Nature-style diagnostic figures as high-resolution PNG.
  - Use clear labels, units, legends, readable fonts, and consistent symbol/color conventions.

## Analysis Plan
### 1) Data audit and Stage-1 cleaning
- Task description:
  - Inspect all four files for schema, record counts, field names, missing values, duplicates, time/location/depth/magnitude ranges, abnormal values, and usable fields.
  - Construct a clean Stage-1 regional catalog from `catalog/Snet_catalog_relocate.csv`.
- Required data sources:
  - `catalog/Snet_catalog_relocate.csv`
  - `catalog/main_earthquake.csv`
  - `source_mechanism/Snet_mecha.csv`
  - `stations/station.sta`
- Parameter selection strategy:
  - Parse native time/origin-time fields from each file and validate against ordering and plausible regional date ranges.
  - Harmonize event tables to common fields: time, latitude, longitude, depth, magnitude, event ID, and source-specific metadata.
  - Flag missing essential fields, impossible coordinates, negative or excessive depths, abnormal magnitudes, parse failures, and exact or near-duplicate event signatures.
  - Preserve raw values and create deterministic surrogate IDs only when event IDs are absent or inconsistent.
- Constraints:
  - Do not silently drop records; retain audit evidence for all corrections and exclusions.
  - Do not infer field meaning from row order; verify by headers and value patterns.
  - Abnormal-value checks must be based on physical plausibility and catalog distribution, not decimal precision alone.
- Key outputs:
  - File-level audit summary tables
  - Clean Stage-1 catalog with quality flags
  - Duplicate and abnormal-value report
  - Field-mapping / usable-field summary

### 2) Major-earthquake matching
- Task description:
  - Match each major earthquake in `catalog/main_earthquake.csv` to the nearest event in the relocated regional catalog, accounting for small relocation-related time shifts.
  - Report nearest matched catalog event, time difference, spatial distance, depth difference, magnitude difference, and match confidence.
- Required data sources:
  - `catalog/main_earthquake.csv`
  - `catalog/Snet_catalog_relocate.csv`
  - Clean Stage-1 catalog from Task 1
- Parameter selection strategy:
  - Use a constrained candidate window centered on each reference origin time, then rank candidates by a composite criterion emphasizing time proximity first, followed by spatial distance, depth agreement, and magnitude agreement.
  - Store both the best match and the short candidate list for ambiguous cases.
  - Define confidence tiers from candidate uniqueness and multi-metric agreement.
- Constraints:
  - If no candidate is found in the primary window, widen cautiously and record the fallback rule used.
  - Do not assume the major event appears exactly in the relocated catalog.
  - Resolve ties explicitly and mark near-ties as ambiguous.
- Key outputs:
  - Major-earthquake match table with matched event ID, matched time, and all requested difference metrics
  - Candidate-ranking/ambiguity diagnostics
  - Match-confidence labels

### 3) Regional seismicity background characterization
- Task description:
  - Characterize the relocated regional catalog in terms of spatial distribution and event density, temporal activity rate, magnitude distribution, depth distribution and segmentation, magnitude–depth relationship, preliminary completeness magnitude Mc and b-value, station distribution and coverage metrics, and focal-mechanism feature availability/distribution.
- Required data sources:
  - `catalog/Snet_catalog_relocate.csv`
  - `source_mechanism/Snet_mecha.csv`
  - `stations/station.sta`
  - Clean Stage-1 catalog from Task 1
- Parameter selection strategy:
  - Use the full cleaned regional catalog for background statistics.
  - Choose temporal bins from catalog duration and event density so activity-rate variability is resolved without excessive smoothing.
  - Estimate Mc from the break in the frequency–magnitude relation and fit b-value over the linear tail above Mc using documented magnitude binning.
  - Derive depth segments from the empirical depth distribution and clearly state the segmentation rule.
  - Summarize station coverage with station density and event-to-station proximity metrics.
  - Separate focal-mechanism availability from geometry/statistics; analyze only records with usable mechanism fields.
- Constraints:
  - Report Mc and b-value as preliminary screening metrics, with the fitting range stated explicitly.
  - Do not mix full-catalog summaries with mechanism-subset summaries.
  - Use a single regional extent for all map-based background diagnostics.
- Key outputs:
  - Spatial density summaries
  - Temporal activity-rate summary
  - Magnitude histogram and frequency–magnitude distribution
  - Depth distribution and depth-bin summary
  - Magnitude–depth relationship summary
  - Preliminary Mc and b-value estimates
  - Station coverage metrics
  - Focal-mechanism availability and feature summary

### 4) Mainshock regional context assessment
- Task description:
  - For each major earthquake, summarize its local context: event density, surrounding depth distribution, nearby station distribution and coverage, nearby focal-mechanism availability, and whether it lies in a distinct spatial/depth domain.
  - Derive notes for later sequence-analysis thresholds.
- Required data sources:
  - `catalog/main_earthquake.csv`
  - `catalog/Snet_catalog_relocate.csv`
  - `source_mechanism/Snet_mecha.csv`
  - `stations/station.sta`
  - Match table from Task 2
- Parameter selection strategy:
  - Define local neighborhoods around each matched mainshock using data-driven radii and depth windows tied to regional event density and station spacing.
  - Compare local density and depth statistics against the full-catalog background.
  - Evaluate nearby station count and distance summaries relative to the local event cloud.
  - Quantify mechanism availability in the same neighborhood and compare with regional coverage.
- Constraints:
  - Keep neighborhood definitions explicit and reusable.
  - If a mainshock sits near the catalog edge, note edge effects in density and coverage metrics.
  - Treat sparse mechanism coverage as limited data availability, not as a physical absence.
- Key outputs:
  - Per-mainshock context table
  - Local-versus-regional contrast metrics
  - Suggested radius, depth, and magnitude screening notes for later sequence analysis

### 5) Diagnostic figure suite
- Task description:
  - Produce Nature-style publication-quality figures supporting audit, background characterization, and mainshock context assessment.
- Required data sources:
  - Clean Stage-1 catalog
  - Match table from Task 2
  - `source_mechanism/Snet_mecha.csv`
  - `stations/station.sta`
- Parameter selection strategy:
  - Use consistent geographic extents and symbol conventions across spatial figures.
  - Highlight major earthquakes consistently across all relevant panels.
  - Use binned or density-based representations for crowded event fields.
  - Show focal mechanisms only where usable geometry is available; otherwise show availability counts or density.
- Constraints:
  - Save figures as high-resolution PNG.
  - Ensure labels include units, legends are legible in print, and color scales remain interpretable.
  - Avoid overcrowding by using transparency, density aggregation, or multi-panel layouts.
- Key outputs:
  - Regional map of earthquakes, major earthquakes, stations, and focal mechanisms if available
  - Time–magnitude plot
  - Depth–time plot
  - Magnitude–depth plot
  - Magnitude-frequency / Mc plot / b-value plot
  - Spatial event-density or cluster diagnostic
  - Depth-distribution or cross-section diagnostic
  - Station coverage diagnostic
  - Focal-mechanism distribution and availability diagnostic
  - Any additional compact background plots that materially improve interpretability

### 6) Candidate patterns estimation
- Task description:
  - Convert the background and context results into compact, testable candidate patterns for later sequence analysis and hypothesis testing.
- Required data sources:
  - Outputs from Tasks 1–4
  - Clean Stage-1 catalog
  - Match table
  - Station summary
  - Mechanism summary
- Parameter selection strategy:
  - Identify spatial clusters from density anomalies or localized concentration.
  - Identify temporal bursts or quiet periods from rate deviations.
  - Detect depth segmentation from layered or bimodal depth distributions.
  - Examine magnitude–depth–space relationships for regional contrasts.
  - Assess station-coverage gradients and focal-mechanism data gaps as possible sampling biases.
  - Compare each mainshock neighborhood with regional background to derive event-specific candidate thresholds.
- Constraints:
  - Keep patterns observational and falsifiable; do not over-interpret mechanisms.
  - Separate catalog-wide patterns from mainshock-specific patterns.
- Key outputs:
  - Ranked candidate-pattern list
  - Suggested follow-up thresholds or masks for sequence analysis
  - Machine-readable summary table for downstream use

### Execution flow and dependencies
- Execute Task 1 first to produce the cleaned Stage-1 catalog and quality-flagged audit outputs.
- Use the cleaned Stage-1 catalog in Tasks 2–6 for all matching, summary statistics, and plotting.
- Use Task 2 outputs to anchor mainshock-specific analyses in Task 4.
- Use Task 3 outputs to define background comparison ranges and guide figure design in Task 5.
- Validate that the cleaned catalog is non-empty and that all expected major earthquakes have either a confident match or an explicitly flagged ambiguous/unmatched status before finalizing derived products.