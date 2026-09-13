# Goal
Build a robust, analysis-ready earthquake data foundation from the Aomori/Japan regional catalog, quantify regional seismicity background and mainshock context, and produce publication-quality diagnostic figures and reusable Stage-1 data products for downstream sequence analysis.

## Planning Assumptions
- Primary analysis will use the observational regional catalog, major-earthquake reference table, station inventory, and focal-mechanism catalog provided in the data folder; model data are not needed.
- Core files are tabular CSV/STA text formats and can be treated as the authoritative inputs for this workflow.
- Stage-1 output should preserve event-level information and add parsed time, standardized geographic/magnitude fields, event identifiers when available, and quality flags for auditability.
- Matching of major earthquakes to relocated catalog events should allow a small time shift and prioritize combined time–space agreement rather than time alone.
- Regional completeness and b-value estimates should be treated as preliminary screening metrics and computed from the cleaned catalog subset only.
- Package contract constraint for ObsPy-based processing: use catalog/tabular reading and time handling consistent with standard ObsPy data access patterns; if a script relies on ObsPy metadata or event-time parsing, success requires validated parsed times and non-empty outputs, not just file read confirmation.
- Output products should include machine-readable tables for cleaned catalog, match results, regional metrics, and focal-mechanism/station summaries, plus high-quality PNG figures.

## Analysis Plan
### 1) Data audit and cleaning
- Task description:
  - Inspect schema, record counts, field types, valid ranges, missingness, duplicates, abnormal values, and usable fields for all four files.
  - Build a clean Stage-1 catalog from `catalog/Snet_catalog_relocate.csv`.
- Required data sources:
  - `catalog/Snet_catalog_relocate.csv`
  - `catalog/main_earthquake.csv`
  - `source_mechanism/Snet_mecha.csv`
  - `stations/station.sta`
- Parameter selection strategy:
  - Parse time fields using the native datetime columns found in each file; if multiple time fields exist, prefer origin time.
  - Keep the full event catalog, but flag suspicious values rather than deleting unless values are clearly impossible.
  - Use file-specific schema discovery first, then apply harmonized field mapping to time, latitude, longitude, depth, magnitude, and event IDs.
- Constraints:
  - Do not infer column meaning from row order alone; verify by headers and value patterns.
  - Duplicate detection should be exact first, then near-duplicate screening for event-time/location identity if needed.
  - Abnormal values to flag include impossible coordinates, negative depths if not physically intended, and nonsensical magnitudes or times.
- Key outputs:
  - Audit summary tables for each file
  - Clean Stage-1 catalog table with parsed fields and quality flags
  - Column dictionary / field mapping table

### 2) Major-earthquake matching
- Task description:
  - Match each event in `main_earthquake.csv` to the nearest relocated catalog event and compute match diagnostics.
- Required data sources:
  - `catalog/main_earthquake.csv`
  - `catalog/Snet_catalog_relocate.csv`
- Parameter selection strategy:
  - Search within a narrow temporal window around each major event to accommodate relocation-induced shifts.
  - Use a combined score based on time difference, hypocentral distance, depth difference, and magnitude difference.
  - If multiple candidates are comparable, choose the one with the smallest time difference and report ambiguity.
- Constraints:
  - Matching should be robust to small origin-time offsets caused by relocation.
  - If no candidate falls in the primary window, widen only once and record that the match confidence is reduced.
- Key outputs:
  - Major-event match table with nearest catalog event, time difference, spatial distance, depth difference, magnitude difference, and confidence
  - Ambiguity flags for tie or near-tie matches

### 3) Regional seismicity background characterization
- Task description:
  - Quantify the regional catalog’s spatial, temporal, magnitude, depth, and station/mechanism background.
- Required data sources:
  - `catalog/Snet_catalog_relocate.csv`
  - `stations/station.sta`
  - `source_mechanism/Snet_mecha.csv`
- Parameter selection strategy:
  - Use the cleaned Stage-1 catalog as the basis for all summaries.
  - Estimate completeness magnitude Mc from the magnitude-frequency distribution using a standard screening approach on the cleaned catalog subset.
  - Estimate b-value using Gutenberg–Richter statistics above Mc.
  - Define depth segments from the empirical depth distribution and/or physically meaningful bins suggested by the catalog.
  - For station coverage, use station density and event-to-nearest-station geometry as simple proxy metrics.
  - For focal mechanisms, summarize availability and geometry fields only where present; separate complete mechanism records from partial entries.
- Constraints:
  - Compute all summary statistics on the same cleaned event subset unless a metric explicitly requires a different subset.
  - Report when mechanism or station metrics are indirect proxies rather than direct observables.
- Key outputs:
  - Spatial distribution metrics and density summaries
  - Temporal rate summaries
  - Magnitude and depth distributions
  - Magnitude–depth relationship summary
  - Preliminary Mc and b-value table
  - Station coverage metrics
  - Focal-mechanism availability and distribution summary

### 4) Mainshock regional context
- Task description:
  - For each major earthquake, summarize local seismicity context and assess whether it sits in a distinct spatial/depth domain.
- Required data sources:
  - `catalog/main_earthquake.csv`
  - `catalog/Snet_catalog_relocate.csv`
  - `stations/station.sta`
  - `source_mechanism/Snet_mecha.csv`
- Parameter selection strategy:
  - Use nested neighborhood windows around each matched major event: a compact core window for direct context and a broader window for domain comparison.
  - Compare local density, depth distribution, station coverage, and mechanism availability against regional background.
  - Test alternative neighborhood radii and depth cuts only as diagnostic comparisons, not as separate conclusions.
- Constraints:
  - Use the same matching result from Task 2 as the anchor for neighborhood statistics.
  - Distinguish between sparse data and true mechanism absence.
- Key outputs:
  - Per-mainshock context table with local density, depth profile, station coverage, mechanism availability, and domain-separation flags
  - Suggested thresholds or neighborhood settings for later sequence analysis

### 5) Diagnostic figures
- Task description:
  - Produce Nature-style diagnostic figures supporting catalog quality control and seismicity interpretation.
- Required data sources:
  - Clean Stage-1 catalog
  - Major-earthquake match table
  - Station inventory
  - Focal-mechanism catalog
- Parameter selection strategy:
  - Use consistent regional extents, color scales, and symbol conventions across figures.
  - Emphasize clear labeling of time, magnitude, depth, location, and matched-event status.
  - Use the same cleaned catalog subset and the same regional bounds for map-style panels.
- Constraints:
  - Figures should be saved as high-resolution PNG.
  - Use readable fonts, consistent legends, and panel labels suitable for manuscript reuse.
  - Do not mix unmatched raw records into figures derived from the cleaned catalog.
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

### 6) Candidate patterns estimation
- Task description:
  - Identify compact, testable patterns for future sequence analysis and hypothesis testing.
- Required data sources:
  - Clean Stage-1 catalog
  - Major-event match table
  - Station inventory
  - Focal-mechanism catalog
- Parameter selection strategy:
  - Derive candidate patterns from the strongest and most repeatable contrasts in density, rate, depth, magnitude, station coverage, and mechanism availability.
  - Prioritize patterns that can be later tested with radius-based clustering, time-window analysis, depth segmentation, and magnitude thresholds.
- Constraints:
  - Keep candidate patterns explicit and testable, not interpretive narratives.
  - Separate catalog-wide patterns from major-event-specific patterns.
- Key outputs:
  - Ranked list of candidate spatial clusters, temporal bursts/quiescence, depth segmentation, magnitude–depth–space relationships, station-coverage effects, focal-mechanism gaps, and regional contrasts around each major earthquake