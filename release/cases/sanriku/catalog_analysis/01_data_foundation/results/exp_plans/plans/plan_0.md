# Goal
Build a cleaned, analysis-ready regional earthquake data foundation from the Aomori/Japan catalog, quantify background seismicity and station/mechanism context, match the three major earthquakes to the relocated catalog, and generate reusable diagnostic products and publication-quality figures for later sequence analysis.

## Planning Assumptions
- Use observation data only: relocated regional catalog, major-earthquake reference table, source-mechanism catalog, and station inventory.
- Package contract considerations:
  - ObsPy is appropriate for time parsing, catalog-style preprocessing, and basic geographic calculations.
  - SeismoStats is appropriate for Gutenberg-Richter analysis, completeness magnitude Mc, b-value estimation, and FMD-style diagnostics.
  - Map-based figures should use station/event coordinates directly; focal-mechanism visualization is only for records with available mechanism fields.
- Main matching logic should allow a small time shift from relocation, but must still require spatial proximity and depth consistency; ambiguous matches should be flagged rather than forced.
- The clean Stage-1 catalog should preserve original values where valid, add parsed datetime, standardized numeric fields, event identifiers if present, and explicit quality flags for missing/abnormal/outlier records.
- For Mc and b-value estimation, document the chosen magnitude binning from catalog properties or a clearly stated empirical bin width; do not infer resolution only from decimal places.
- Figures should be saved as high-resolution PNG and emphasize clear scientific readability, with consistent axes, units, legends, and region-appropriate spatial extents.

## Analysis Plan
### 1) Data audit and Stage-1 cleaning
- Task description:
  - Inspect schema, record counts, field names, missingness, duplicates, time ordering, coordinate ranges, depth/magnitude ranges, and unusual or out-of-domain values for all four files.
  - Construct a clean Stage-1 catalog from `catalog/Snet_catalog_relocate.csv` with parsed origin time, latitude, longitude, depth, magnitude, event ID if available, and quality flags.
- Required data sources:
  - `catalog/Snet_catalog_relocate.csv`
  - `catalog/main_earthquake.csv`
  - `source_mechanism/Snet_mecha.csv`
  - `stations/station.sta`
- Parameter selection strategy:
  - Parse times using file-native timestamp fields; preserve original timestamp strings in audit output.
  - Define abnormal-value checks from physically plausible regional earthquake bounds and from observed catalog distribution tails.
  - Flag duplicates by identical event-time and hypocenter tuples, then verify whether any are true duplicates or near-duplicates after relocation.
- Constraints:
  - Keep all original records in the audit output; do not delete without a recorded reason.
  - If event IDs are absent or inconsistent, create deterministic surrogate IDs.
- Key outputs:
  - Audit table for each file
  - Clean Stage-1 catalog table
  - Quality-flag summary counts
  - Abnormal-value and duplicate report

### 2) Major-earthquake matching
- Task description:
  - Match the three major earthquakes to the relocated regional catalog using a nearest-neighbor approach in time and space.
  - Report nearest matched event, time difference, spatial distance, depth difference, magnitude difference, and a match-confidence score.
- Required data sources:
  - `catalog/main_earthquake.csv`
  - `catalog/Snet_catalog_relocate.csv`
- Parameter selection strategy:
  - Use a constrained search window around each reference event, centered on origin time, with a small tolerance for relocation-induced shifts.
  - Rank candidate matches by a composite metric emphasizing time proximity first, then spatial distance, then depth agreement.
- Constraints:
  - If multiple candidates are nearly tied, mark the match as ambiguous.
  - Do not assume the reference event appears exactly in the relocated catalog.
- Key outputs:
  - Major-earthquake match table
  - Match-confidence flags
  - Candidate-neighborhood diagnostics for each mainshock

### 3) Regional seismicity background characterization
- Task description:
  - Quantify spatial, temporal, magnitude, depth, and station/mechanism background properties of the regional catalog.
  - Include spatial density, activity rate, magnitude-frequency distribution, depth segmentation, magnitude-depth relation, preliminary completeness magnitude Mc, and b-value.
- Required data sources:
  - `catalog/Snet_catalog_relocate.csv`
  - `source_mechanism/Snet_mecha.csv`
  - `stations/station.sta`
- Parameter selection strategy:
  - Use the full cleaned regional catalog for background statistics.
  - Compute temporal rates using consistent bins suitable for the catalog length and event count.
  - Estimate Mc using a recognized completeness approach and test b-value stability over plausible magnitude thresholds.
  - For mechanism diagnostics, separate records with valid focal-mechanism fields from records with only hypocenter/magnitude information.
  - For station coverage, derive simple counts and distance-based summary metrics from station coordinates relative to the regional event cloud.
- Constraints:
  - Report mechanism availability separately from mechanism geometry statistics.
  - Keep depth-segmentation thresholds data-driven and explicitly documented.
- Key outputs:
  - Spatial density statistics
  - Temporal rate summary
  - Magnitude histogram and FMD
  - Depth distribution and depth-bin summary
  - Magnitude-depth scatter diagnostics
  - Mc and b-value summary
  - Station coverage metrics
  - Focal-mechanism availability and feature summary

### 4) Mainshock regional context assessment
- Task description:
  - For each major earthquake, summarize the surrounding regional context: local density, nearby depth structure, station coverage, nearby mechanism availability, and whether it occupies a distinct spatial/depth domain.
  - Derive implications for later sequence-analysis settings.
- Required data sources:
  - `catalog/main_earthquake.csv`
  - `catalog/Snet_catalog_relocate.csv`
  - `source_mechanism/Snet_mecha.csv`
  - `stations/station.sta`
- Parameter selection strategy:
  - Evaluate multiple local neighborhoods around each mainshock using a compact set of spatial radii and depth windows derived from the regional catalog scale.
  - Compare local event density and depth statistics against the full-catalog background.
  - Assess station proximity and mechanism availability within the same neighborhoods.
- Constraints:
  - Treat the output as a context screen, not a final causal interpretation.
  - Any recommendation for later thresholds must be tied to measured local-background contrasts.
- Key outputs:
  - Per-mainshock context table
  - Local-versus-regional contrast metrics
  - Suggested radius/depth/magnitude screening notes for later sequence analysis

### 5) Diagnostic figure suite
- Task description:
  - Produce a compact set of Nature-style diagnostic figures for background characterization and workflow support.
- Required data sources:
  - `catalog/Snet_catalog_relocate.csv`
  - `catalog/main_earthquake.csv`
  - `source_mechanism/Snet_mecha.csv`
  - `stations/station.sta`
- Parameter selection strategy:
  - Use a consistent regional map extent enclosing the event cloud and stations.
  - Prefer binned or density-based representations for crowded distributions, with overlaid mainshocks and mechanisms where available.
  - Include separate panels or figures for temporal, magnitude, depth, station, and mechanism diagnostics.
- Constraints:
  - Keep axes labeled with units and use color scales that remain interpretable in print.
  - Only plot focal mechanisms where geometries are present; otherwise show availability counts.
- Key outputs:
  - Regional map of earthquakes, mainshocks, stations, and focal mechanisms if available
  - Time–magnitude plot
  - Depth–time plot
  - Magnitude–depth plot
  - Magnitude-frequency / Mc / b-value plot
  - Spatial event-density or clustering diagnostic
  - Depth-distribution or cross-section diagnostic
  - Station coverage diagnostic
  - Focal-mechanism distribution and availability diagnostic

### 6) Candidate pattern extraction for follow-up sequence analysis
- Task description:
  - Convert the background results into compact, testable candidate patterns for later hypothesis testing and sequence analysis.
- Required data sources:
  - Outputs from Tasks 1–4
- Parameter selection strategy:
  - Identify clusters, bursts, quiet periods, depth segmentation, magnitude-depth-space trends, station-coverage gradients, mechanism-data gaps, and mainshock-specific contrasts directly from the cleaned catalog and context metrics.
- Constraints:
  - Keep patterns observational and testable; do not over-interpret as mechanisms.
- Key outputs:
  - Short candidate-pattern list
  - Recommended follow-up thresholds or masks for later sequence work
  - Machine-readable summary table for downstream use

### Execution flow and dependencies
- Execute Task 1 first to create the cleaned Stage-1 catalog and quality flags.
- Use the cleaned catalog from Task 1 in Tasks 2–6 to ensure consistent event counts and field definitions.
- Use Task 2 outputs to anchor mainshock-specific context in Task 4.
- Use Task 3 outputs to define background thresholds and to guide the figure suite in Task 5.
- Consolidate all derived tables and plot files into reusable analysis artifacts after validation that the cleaned catalog is non-empty and the matched-event table contains the expected three major earthquakes.