# Goal

Build a clean, analysis-ready regional earthquake data foundation for the Aomori/Japan study area, quantify background seismicity and major-event context, and produce reusable tabular products plus publication-quality diagnostic figures for downstream sequence analysis.

## Planning Assumptions

- Primary observational data are the relocated regional catalog, major-earthquake reference table, focal-mechanism catalog, and station inventory in the provided data folder; no model data are needed.
- The main scientific workflow is catalog-centric and can be completed with one cohesive analysis script that performs audit, cleaning, matching, background characterization, context summaries, and figure generation.
- Time parsing must preserve original origin-time precision from the catalog fields; no assumption about temporal resolution should be inferred from decimal places alone.
- Spatial calculations for matching and regional context should use consistent geographic distance metrics suitable for local/regional scales; the exact projection or geodesic method should be fixed before execution and applied uniformly.
- Completeness magnitude and b-value estimation should use documented Gutenberg–Richter methods with an explicit, data-driven magnitude binning and completeness-selection strategy.
- “Nature-style” figures means clean, uncluttered, high-contrast, scientifically annotated plots with clear labels, legends, and consistent color semantics; output should be saved as high-resolution PNG.
- If focal-mechanism fields are sparse or partially populated, the plan should separate “availability” from “mechanism-property” analyses so missing mechanism information is not treated as failure.
- Any event matching to the main earthquakes should allow for small relocation-induced time offsets and spatial offsets, but the match criteria must be validated against the catalog’s actual event density and timing.
- The output should include both human-readable summaries and machine-readable tables for reuse in later sequence analysis.

## Analysis Plan

1. Data audit and stage-1 cleaning
   - Task description:
     - Inspect all four files for schema, record counts, data types, field availability, missing values, duplicates, and abnormal values.
     - Create a clean Stage-1 catalog containing parsed origin time, latitude, longitude, depth, magnitude, event ID if present, and quality flags.
   - Required data sources:
     - `catalog/Snet_catalog_relocate.csv`
     - `catalog/main_earthquake.csv`
     - `source_mechanism/Snet_mecha.csv`
     - `stations/station.sta`
   - Parameter selection strategy:
     - Detect and standardize datetime columns from file metadata and column names, then validate against plausible origin-time ranges.
     - Determine valid numeric ranges empirically from the catalog and flag outliers rather than hard-coding broad thresholds.
     - Assign quality flags for missing/invalid time, location, depth, magnitude, duplicate rows, and abnormal mechanism/station fields.
   - Constraints:
     - Preserve original records in a raw-audit table while producing a cleaned Stage-1 table.
     - Do not drop records silently; document all exclusions and corrections.
   - Key outputs:
     - Audit summary table for each file
     - Clean Stage-1 regional catalog
     - Cleaned reference-event table
     - Quality-flag report
     - Summary of mechanism and station-table usability

2. Major-earthquake matching
   - Task description:
     - Match each major earthquake to the nearest event in the relocated regional catalog.
     - Report time difference, spatial distance, depth difference, magnitude difference, and a match-confidence score.
   - Required data sources:
     - `catalog/main_earthquake.csv`
     - `catalog/Snet_catalog_relocate.csv` or Stage-1 cleaned catalog
   - Parameter selection strategy:
     - Use a two-stage match: first restrict by time window around each major event, then choose the nearest event using combined time-space proximity.
     - Set allowable time offset and spatial search radius from the empirical event density around each reference event.
     - Define confidence from multi-criterion agreement: temporal closeness, spatial closeness, and magnitude consistency.
   - Constraints:
     - If multiple candidates are near-tied, retain the top candidate and a short candidate list for audit.
     - If no candidate is found within the initial window, expand cautiously and record the fallback rule used.
   - Key outputs:
     - Major-event match table
     - Candidate-ranking table
     - Match confidence diagnostics

3. Regional seismicity background characterization
   - Task description:
     - Quantify spatial, temporal, magnitude, depth, and station-coverage characteristics of the full regional catalog.
     - Estimate preliminary completeness magnitude and b-value.
     - Summarize focal-mechanism availability and feature distributions.
   - Required data sources:
     - Stage-1 regional catalog
     - `stations/station.sta`
     - `source_mechanism/Snet_mecha.csv`
   - Parameter selection strategy:
     - Spatial distribution: use kernel density or gridded event density with grid spacing tied to catalog extent and station/network spacing.
     - Temporal activity: compute event counts in fixed bins and optionally smoothed rates using a window size selected from the full catalog duration.
     - Magnitude distribution: use histogram/binning grounded in catalog magnitude precision or method defaults documented in the data.
     - Depth segmentation: define shallow/intermediate/deep bins based on the empirical depth distribution, and test whether natural breaks are present.
     - Mc and b-value: estimate with Gutenberg–Richter methods using a reproducible magnitude binning and a data-driven completeness candidate set.
     - Station coverage: compute station spatial density and event-to-station proximity summaries.
     - Focal-mechanism analysis: separate “all events with mechanism record” from “events with full focal-mechanism fields.”
   - Constraints:
     - Treat sparse focal-mechanism fields as partial coverage, not as full catalog failure.
     - Use one consistent regional extent for all map-based background summaries.
   - Key outputs:
     - Regional spatial-density summary
     - Temporal-rate summary
     - Magnitude and depth distribution tables
     - Mc and b-value estimates with supporting diagnostics
     - Station coverage metrics
     - Focal-mechanism availability and distribution summaries

4. Mainshock regional context analysis
   - Task description:
     - For each major earthquake, quantify its local event density, nearby depth structure, nearby station coverage, focal-mechanism availability, and whether it occupies a distinct regional domain.
   - Required data sources:
     - Major-event match table
     - Stage-1 regional catalog
     - `stations/station.sta`
     - `source_mechanism/Snet_mecha.csv`
   - Parameter selection strategy:
     - Use one or more neighborhood radii around each matched major event, selected from local catalog density and station spacing.
     - Compute local summaries within a compact radius and, if needed, a broader comparison radius for context.
     - Define “distinct domain” using contrasts in depth distribution, local density, and station coverage relative to the full catalog.
   - Constraints:
     - Keep neighborhood definitions explicit and reusable for later sequence analysis.
     - If a major event lies near the edge of the catalog footprint, note edge effects in density and coverage metrics.
   - Key outputs:
     - Per-major-event regional context tables
     - Local-versus-regional comparison metrics
     - Suggested analysis thresholds for later sequence studies

5. Diagnostic figure generation
   - Task description:
     - Produce a compact set of high-quality figures that document the cleaned catalog, background seismicity, and major-event context.
   - Required data sources:
     - Stage-1 regional catalog
     - Major-event match table
     - `stations/station.sta`
     - `source_mechanism/Snet_mecha.csv`
   - Parameter selection strategy:
     - Use the same geographic extent and consistent color mapping across all spatial figures.
     - For magnitude, depth, and time plots, derive binning and axis limits from the cleaned catalog and the full study interval.
     - Show focal-mechanism symbols only where mechanism data exist, and visually distinguish availability from non-availability.
   - Constraints:
     - Keep figures legible and publication-oriented, with non-overlapping annotations and minimal visual clutter.
     - Save all requested figures as PNG and ensure each figure has a clear scientific caption-ready title.
   - Key outputs:
     - Regional map of earthquakes, major earthquakes, stations, and focal mechanisms
     - Time–magnitude plot
     - Depth–time plot
     - Magnitude–depth plot
     - Magnitude-frequency / Mc / b-value plot
     - Spatial event-density or cluster diagnostic
     - Depth-distribution or cross-section diagnostic
     - Station coverage diagnostic
     - Focal-mechanism distribution and availability diagnostic
     - Additional supporting background plots as needed

6. Candidate-pattern estimation for further sequence analysis
   - Task description:
     - Translate the background characterization into compact, testable hypotheses for later sequence analysis.
   - Required data sources:
     - Stage-1 regional catalog
     - Major-event context tables
     - Station coverage summary
     - Focal-mechanism availability summary
   - Parameter selection strategy:
     - Identify clusters, bursts, quiet periods, depth segmentation, and magnitude-depth-space relationships using thresholds supported by the background statistics.
     - Compare around-major-event behavior with regional background behavior to isolate event-specific patterns.
     - Flag station-coverage gaps and mechanism-data gaps that could bias later interpretations.
   - Constraints:
     - Output only testable candidate patterns and thresholds grounded in the cleaned data; do not over-interpret beyond the observed catalog.
   - Key outputs:
     - Candidate-pattern table
     - Threshold recommendations for later sequence analysis
     - Bias/coverage caution table

7. Reusable data products and handoff package
   - Task description:
     - Package the cleaned catalog and analysis summaries into a small set of reusable files for downstream analysis.
   - Required data sources:
     - Outputs from Tasks 1–6
   - Parameter selection strategy:
     - Retain a minimal but sufficient schema for later sequence work: event identity, time, hypocenter, magnitude, quality flags, major-event match labels, and local-context metrics.
   - Constraints:
     - Keep outputs versioned and internally consistent with the audit results.
   - Key outputs:
     - Clean Stage-1 catalog file
     - Major-earthquake match file
     - Regional summary tables
     - Context summary tables
     - Figure set in PNG format