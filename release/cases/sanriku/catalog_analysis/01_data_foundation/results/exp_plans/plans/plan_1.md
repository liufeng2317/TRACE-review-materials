# Goal
Build a cleaned Stage-1 earthquake catalog and a set of regional seismicity diagnostics for the Aomori/Japan study area, including major-earthquake matching, background characterization, contextual summaries around each major earthquake, publication-quality figures, and reusable data products for follow-on sequence analysis.

## Planning Assumptions
- Primary observational data are the four provided tabular files in the study data folder; no model data are needed.
- Main analysis will use the relocated regional catalog as the core event dataset, with the major-earthquake table used as a reference set, the mechanism catalog used for mechanism availability/feature analysis, and the station inventory used for coverage diagnostics.
- The task is fundamentally catalog/statistical; no waveform processing is required.
- Package/tool contract summary for this workflow:
  - Data handling can be done with standard tabular parsing and geospatial/time computations.
  - Match success should be based on explicit time, distance, depth, and magnitude tolerances or nearest-neighbor ranking, with the matching rule recorded in outputs.
  - Figures should be generated from cleaned tables and saved as high-resolution PNGs; no intermediate plot-only outputs should be treated as final scientific products.
- Use parsed origin time in a consistent timezone/format, and preserve original raw fields alongside cleaned fields when available.
- Quality flags should be attached to each Stage-1 event to record parsing issues, out-of-range values, missing optional fields, and matching status.
- For completeness magnitude and b-value estimation, use only the catalog segment that is internally consistent and above the estimated completeness threshold; if multiple candidate methods disagree, report both estimates and select one by documented rule.
- Major-earthquake context summaries should be based on local neighborhoods defined from the regional catalog and station geometry, with radii/depth windows chosen from study-area scale and event density rather than arbitrary fixed values.
- Focal-mechanism analysis should explicitly distinguish between all cataloged earthquakes and the subset with mechanism metadata available, since coverage is partial.

## Analysis Plan
### 1. Data audit and Stage-1 cleaning
- Task description:
  - Inspect schema, record counts, data types, missing values, duplicates, time ranges, spatial ranges, depth ranges, and magnitude ranges for all four files.
  - Identify abnormal or implausible values and standardize field names.
  - Build a clean Stage-1 catalog from `catalog/Snet_catalog_relocate.csv`.
- Required data sources:
  - `catalog/Snet_catalog_relocate.csv`
  - `catalog/main_earthquake.csv`
  - `source_mechanism/Snet_mecha.csv`
  - `stations/station.sta`
- Parameter selection strategy:
  - Parse time fields using the documented timestamp format present in each file; if multiple formats exist, infer and validate against ordering and range checks.
  - Normalize coordinates to numeric latitude/longitude; preserve depth in km and magnitude in the native reported scale.
  - Flag records with missing essential fields, duplicate event signatures, impossible coordinates, negative or excessive depths, or magnitudes outside a reasonable regional range.
  - Retain event IDs if present; otherwise create stable surrogate IDs from parsed time and location.
- Constraints:
  - Do not discard records silently; keep an audit log of excluded or corrected rows.
  - If multiple candidate time fields exist, select the primary origin-time field used by the catalog and retain alternates in metadata.
- Key outputs:
  - File/table: clean Stage-1 catalog with parsed time, latitude, longitude, depth, magnitude, event ID, and quality flags.
  - Audit summary table for all inputs.
  - Data-validation notes listing flagged records and corrective actions.

### 2. Major-earthquake matching
- Task description:
  - Match each event in `catalog/main_earthquake.csv` to the nearest event in the cleaned regional catalog, accounting for small relocation time shifts.
  - Report nearest match and match diagnostics.
- Required data sources:
  - Clean Stage-1 catalog from Task 1
  - `catalog/main_earthquake.csv`
- Parameter selection strategy:
  - Use a nearest-neighbor search in combined time-space-magnitude feature space, with time given highest priority and spatial proximity as a secondary constraint.
  - Set candidate windows wide enough to capture relocation shifts but narrow enough to avoid ambiguous matches; validate by inspecting event uniqueness around each reference event.
  - Compute time difference, horizontal distance, depth difference, and magnitude difference for the best match, plus an overall confidence flag.
- Constraints:
  - If more than one event falls within the candidate window, resolve ties by smallest time difference, then smallest spatial distance, then closest magnitude.
  - Explicitly note unmatched or ambiguous reference events.
- Key outputs:
  - Major-earthquake matching table with matched event ID, matched time, time offset, spatial distance, depth difference, magnitude difference, and confidence score/label.
  - Brief matching diagnostic summary.

### 3. Regional seismicity background characterization
- Task description:
  - Quantify the regional catalog’s spatiotemporal and magnitude-depth structure and produce background seismicity metrics for later hypothesis testing.
- Required data sources:
  - Clean Stage-1 catalog
  - `source_mechanism/Snet_mecha.csv`
  - `stations/station.sta`
- Parameter selection strategy:
  - Spatial distribution: compute event density maps and point distributions over the catalog extent using the regional bounding box and a sensible grid resolution based on event density.
  - Temporal activity rate: compute event counts per fixed interval and smoothed rate curves, with interval length chosen to resolve catalog-scale variability without over-smoothing.
  - Magnitude distribution: compute histogram and cumulative frequency-magnitude relation; estimate completeness magnitude Mc and Gutenberg-Richter b-value using the subset above Mc.
  - Depth distribution: compute overall depth histogram and segmented depth bins informed by regional tectonic structure and data distribution.
  - Magnitude-depth relationship: examine joint distributions, robust trend summaries, and bin-wise statistics.
  - Station distribution and coverage: summarize station density relative to catalog epicenters and compute simple nearest-station / average-distance coverage metrics.
  - Focal-mechanism feature analysis: use only records with mechanism fields present; summarize geometry availability, mechanism-type counts, and quality/provenance fields if present.
- Constraints:
  - Estimate Mc before b-value; do not use the full magnitude range blindly.
  - Separate mechanism-available subset analyses from full-catalog analyses.
  - Use consistent units and clearly label all segmented statistics.
- Key outputs:
  - Regional summary statistics table.
  - Mc and b-value estimates with method notes.
  - Station coverage metrics table.
  - Focal-mechanism availability and feature summary table.
  - Derived regional background fields for plotting and reuse.

### 4. Mainshock regional context analysis
- Task description:
  - For each major earthquake, summarize local seismicity, depth structure, station support, focal-mechanism availability, and whether the event occupies a distinct domain.
- Required data sources:
  - Clean Stage-1 catalog
  - Major-earthquake matching table from Task 2
  - `source_mechanism/Snet_mecha.csv`
  - `stations/station.sta`
- Parameter selection strategy:
  - Define a local neighborhood around each major earthquake using a data-driven spatial radius based on event density and station spacing, plus a depth window centered on the matched event depth.
  - Compare local event density and depth distribution against the full-catalog background.
  - Summarize nearby station count, average epicentral distance to stations, and directional coverage proxies where feasible.
  - Compute the fraction of nearby events with focal-mechanism data and compare to regional availability.
  - Classify each major event as lying in a distinct spatial/depth domain if local distributions differ strongly from regional background.
- Constraints:
  - Use the same neighborhood definition across all major events unless the data density demands a documented adjustment.
  - Distinguish structural interpretation from measurable diagnostics; keep classification rule explicit.
- Key outputs:
  - Per-major-earthquake context table with local density, depth statistics, station coverage, mechanism availability, and domain-separation flag.
  - Recommended thresholds for later sequence analysis, such as radius, depth span, or magnitude filters, with justification tied to local context.

### 5. Diagnostic figure generation
- Task description:
  - Produce Nature-style publication-quality PNG diagnostics from cleaned and derived data products.
- Required data sources:
  - Clean Stage-1 catalog
  - Major-earthquake matching table
  - `source_mechanism/Snet_mecha.csv`
  - `stations/station.sta`
- Parameter selection strategy:
  - Regional map: plot catalog events, major earthquakes, stations, and mechanism-bearing events using consistent geographic projection and clear symbol hierarchy.
  - Time–magnitude plot: use event time along x-axis and magnitude along y-axis, with major events highlighted.
  - Depth–time plot: show depth evolution through time, emphasizing major events.
  - Magnitude–depth plot: joint scatter with density cues or bin summaries.
  - Mc / b-value plot: show frequency-magnitude distribution, completeness threshold, and fitted Gutenberg-Richter line.
  - Spatial density / cluster diagnostic: use gridded density or hexbin-style aggregation over the study area.
  - Depth distribution / cross-section: create histograms and at least one spatial cross-section or depth-binned summary.
  - Station coverage diagnostic: map stations relative to seismicity and/or plot nearest-station distance distributions.
  - Mechanism diagnostic: show mechanism availability by time, magnitude, depth, or spatial distribution, depending on field availability.
- Constraints:
  - All figures should use readable labels, units, legends, and consistent color logic; highlight major earthquakes consistently across all panels.
  - Save figures as high-resolution PNG with clear file naming tied to plot content.
- Key outputs:
  - A figure set covering the requested diagnostics plus any additional plot that materially improves interpretability.
  - Optional multi-panel summary figure for quick review.

### 6. Candidate pattern estimation for follow-up sequence analysis
- Task description:
  - Convert diagnostics into compact, testable hypotheses for later sequence analysis and hypothesis testing.
- Required data sources:
  - Clean Stage-1 catalog
  - Major-earthquake matching table
  - Regional background metrics from Tasks 3–4
  - `source_mechanism/Snet_mecha.csv`
  - `stations/station.sta`
- Parameter selection strategy:
  - Identify spatial clusters from density anomalies or localized event concentration.
  - Identify temporal bursts or quiet periods from rate anomalies relative to background.
  - Detect depth segmentation from bimodal or layered depth distributions.
  - Examine magnitude-depth-space relationships for systematic regional differences.
  - Assess whether station-coverage gradients or focal-mechanism data gaps could bias apparent patterns.
  - Compare local neighborhoods around each major earthquake to the regional background to define candidate threshold regimes.
- Constraints:
  - Keep candidate patterns compact, falsifiable, and directly linked to measurable diagnostics.
  - Avoid over-interpreting sparse mechanism subsets; clearly separate signal from coverage bias.
- Key outputs:
  - A ranked list of candidate patterns with supporting metrics, affected region/time window, and suggested thresholds for follow-up analysis.
  - Reusable summary table for sequence-analysis planning.