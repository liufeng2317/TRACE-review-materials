# Goal
Build a clean, analysis-ready earthquake data foundation for the Aomori/Japan study area, quantify regional seismicity background and major-earthquake context, produce publication-quality diagnostic figures, and prepare reusable summary products for downstream sequence analysis.

## Planning Assumptions
- Primary observational source is the relocated regional catalog `catalog/Snet_catalog_relocate.csv`; use model data only if observational fields are insufficient, which is not the case here.
- Major-earthquake matching should prioritize catalog time proximity first, then spatial proximity, then depth and magnitude consistency.
- The stage-1 catalog will be a derived, cleaned observational product containing at minimum parsed origin time, latitude, longitude, depth, magnitude, event identifier if available, match/quality flags, and audit flags for missing/abnormal values.
- The regional-mechanism file `source_mechanism/Snet_mecha.csv` is a mixed-completeness observational table; mechanism-based diagnostics should separate “mechanism available” from “mechanism missing”.
- Station inventory `stations/station.sta` will be treated as a static geometry product for coverage diagnostics, distance calculations, and context summaries.
- Package contract summary for any catalog/statistical workflow:
  - Use tabular CSV/STA inputs.
  - Parse dates/times explicitly before any matching or rate calculations.
  - Preserve raw columns in an audit output alongside cleaned fields.
  - Success evidence includes non-empty cleaned tables, match tables, summary statistics, and saved figure files.
- Completeness magnitude Mc and b-value will be estimated as preliminary diagnostics only, using documented magnitude bins and a clearly stated fitting range derived from the catalog’s empirical distribution, not from decimal precision.
- Nature-style figures should prioritize clear multi-panel layout, direct annotation, restrained color palettes, and consistent axis scaling across comparable panels.

## Analysis Plan

### 1) Data audit and cleaning
- Task description:
  - Inspect all four files for schema, record count, field types, coordinate/time ranges, missing values, duplicates, and abnormal or out-of-domain values.
  - Build a clean Stage-1 catalog for the relocated regional earthquake events.
- Required data sources:
  - `catalog/Snet_catalog_relocate.csv`
  - `catalog/main_earthquake.csv`
  - `source_mechanism/Snet_mecha.csv`
  - `stations/station.sta`
- Parameter selection strategy:
  - Infer datetime fields from file headers and known seismic catalog conventions; validate against monotonicity and realistic time span.
  - Identify latitude/longitude/depth/magnitude columns by schema inspection, then standardize units and column names.
  - Define abnormal-value rules from physically plausible ranges: latitude/longitude bounds, nonnegative depth check where appropriate, and magnitude range sanity screening.
  - Keep all original records unless clearly invalid; flag rather than drop when ambiguity remains.
- Constraints:
  - Do not assume event IDs exist; create synthetic IDs only if absent and clearly label them as derived.
  - Do not infer station or mechanism completeness from non-nullness of unrelated fields.
- Key outputs:
  - Clean Stage-1 catalog table with audit flags.
  - File-level audit summary table.
  - Missing-value, duplicate, and range-check summary.

### 2) Major-earthquake matching
- Task description:
  - Match each major earthquake in the reference table to the nearest event in the relocated regional catalog, accounting for the small relocation-related time shift.
  - Quantify temporal, spatial, depth, and magnitude differences and assign a match confidence score.
- Required data sources:
  - `catalog/main_earthquake.csv`
  - `catalog/Snet_catalog_relocate.csv`
- Parameter selection strategy:
  - Use a narrow time window centered on each reference origin time, then expand if no candidate is found.
  - Rank candidates by a weighted combination of absolute time difference, horizontal distance, depth difference, and magnitude difference.
  - Define confidence tiers from candidate uniqueness and multi-metric agreement.
- Constraints:
  - If multiple events satisfy the same nearest-time criterion, use spatial closeness and magnitude consistency as tie-breakers.
  - Record unmatched cases explicitly rather than forcing a match.
- Key outputs:
  - Major-event-to-catalog match table.
  - Per-event match diagnostics: time difference, distance, depth difference, magnitude difference, confidence.
  - Annotated catalog subset for matched major events.

### 3) Regional seismicity background characterization
- Task description:
  - Quantify the regional catalog’s spatial, temporal, magnitude, and depth structure, including preliminary completeness and Gutenberg–Richter diagnostics.
  - Summarize station and mechanism context.
- Required data sources:
  - `catalog/Snet_catalog_relocate.csv`
  - `stations/station.sta`
  - `source_mechanism/Snet_mecha.csv`
- Parameter selection strategy:
  - Use the full cleaned relocated catalog for background statistics.
  - For magnitude-frequency analysis, determine Mc from the break in the frequency–magnitude relation and estimate b-value over the linear tail above Mc.
  - For depth segmentation, derive bins from empirical quantiles plus geologically meaningful thresholds if evident from the data.
  - For activity-rate analysis, use a consistent time binning based on the catalog duration and event density.
- Constraints:
  - Report Mc and b-value as preliminary; include the magnitude range used for fitting.
  - Mechanism statistics must separate “all events” from “events with available focal-mechanism fields”.
- Key outputs:
  - Spatial density summaries and gridded event-density statistics.
  - Temporal rate summary and activity histogram.
  - Magnitude histogram and magnitude-frequency relation.
  - Depth distribution and depth-segment counts.
  - Magnitude–depth relationship summary.
  - Station distribution and simple coverage metrics.
  - Mechanism availability and mechanism-field summary.

### 4) Mainshock regional context
- Task description:
  - For each major earthquake, compute local context statistics in a neighborhood around the matched event and assess whether it occupies a distinct spatial or depth domain.
- Required data sources:
  - `catalog/main_earthquake.csv`
  - `catalog/Snet_catalog_relocate.csv`
  - `stations/station.sta`
  - `source_mechanism/Snet_mecha.csv`
- Parameter selection strategy:
  - Use neighborhood windows defined by a compact spatial radius, optional depth window, and local time window around the matched event.
  - Compare each major event’s local statistics against the regional background to determine whether it is anomalous or domain-distinct.
  - Evaluate station coverage locally using distances from the event to stations.
- Constraints:
  - Neighborhood thresholds should be data-adaptive and derived from regional event density and depth spread, not arbitrary fixed values alone.
  - If mechanism data are sparse locally, report availability and avoid overinterpreting missingness.
- Key outputs:
  - Per-major-event context summaries: local event density, depth distribution, station coverage, mechanism availability.
  - Domain-distinctness flags and recommended thresholds for subsequent sequence analysis.
  - Candidate analysis settings for radius/depth/magnitude thresholds.

### 5) Diagnostic figures
- Task description:
  - Produce Nature-style figures to support audit, background characterization, and sequence-analysis planning.
- Required data sources:
  - `catalog/Snet_catalog_relocate.csv`
  - `catalog/main_earthquake.csv`
  - `stations/station.sta`
  - `source_mechanism/Snet_mecha.csv`
- Parameter selection strategy:
  - Use consistent map projections and axis limits across spatial figures.
  - Use shared color scales for magnitude or depth where comparison is intended.
  - Highlight major earthquakes distinctly from background seismicity and stations.
  - Include only mechanism events that have usable geometry fields.
- Constraints:
  - Save all figures as high-resolution PNG.
  - Ensure labels include units and that legends remain legible when printed.
  - Avoid overcrowding by using transparency, subsampling only for display if necessary, and insets or panels when helpful.
- Key outputs:
  - Regional map of earthquakes, major earthquakes, stations, and focal mechanisms.
  - Time–magnitude plot.
  - Depth–time plot.
  - Magnitude–depth plot.
  - Magnitude-frequency / Mc / b-value plot.
  - Spatial density or cluster diagnostic.
  - Depth-distribution or cross-section diagnostic.
  - Station coverage diagnostic.
  - Focal-mechanism distribution and availability diagnostic.
  - Additional compact background plots as needed for hypothesis testing.

### 6) Candidate patterns estimation
- Task description:
  - Identify compact, testable patterns that can guide later sequence analysis and hypothesis testing.
- Required data sources:
  - `catalog/Snet_catalog_relocate.csv`
  - `catalog/main_earthquake.csv`
  - `stations/station.sta`
  - `source_mechanism/Snet_mecha.csv`
- Parameter selection strategy:
  - Compare local vs regional metrics around each major earthquake.
  - Detect candidate spatial clusters via density contrasts, temporal bursts via rate changes, depth segmentation via bimodality or threshold shifts, and data gaps via station/mechanism coverage changes.
- Constraints:
  - Frame outputs as testable candidates rather than conclusions.
  - Prioritize patterns that are supported by multiple diagnostics.
- Key outputs:
  - Ranked candidate pattern list with supporting evidence.
  - Suggested thresholds for later sequence analysis, including spatial radius, depth slicing, and magnitude cutoffs.
  - Data-gap and coverage-effect flags for major earthquakes and regional subsets.

### 7) Reusable data products for downstream work
- Task description:
  - Assemble compact outputs that can be reused in later sequence or clustering analysis.
- Required data sources:
  - Cleaned catalog, match table, station table, mechanism summary, regional statistics.
- Parameter selection strategy:
  - Export a Stage-1 cleaned catalog and derived summary tables with stable column names.
  - Include match labels, local-context labels, and quality flags for each event where applicable.
- Constraints:
  - Keep derived products machine-readable and aligned with the cleaned source records.
- Key outputs:
  - Stage-1 catalog table.
  - Major-earthquake match table.
  - Regional summary metrics table.
  - Context summary table for each major earthquake.
  - Figure index listing saved PNG outputs and their associated diagnostics.