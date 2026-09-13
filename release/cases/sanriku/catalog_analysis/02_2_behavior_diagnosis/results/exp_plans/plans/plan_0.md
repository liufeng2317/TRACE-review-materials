# Goal
Diagnose and compare the mainshock-centered sequence behavior around M1, M2, and M3 in the Aomori relocated earthquake catalog using observation-based catalog analysis, matched pre/post metrics, spatial-distance structure, depth/mechanism context, and curated diagnostic figures.

## Planning Assumptions
- Use observation data only: relocated event catalog, mainshock reference table, focal-mechanism table, and station table from the provided project folder.
- The primary workflow is catalog analysis in one main script; a second script is reserved for report-table assembly if separation is useful after metric generation.
- Mainshock-centered analysis should be based on explicit relative quantities computed between every catalog event and each of the three reference mainshocks.
- Practical mainshock-like identification must use a tolerance on origin time and hypocenter proximity because the mainshock row in `main_earthquake.csv` may not match catalog values exactly after relocation/rounding.
- Epicentral distance should be computed on geographic coordinates; depth difference is vertical separation only; cumulative radii and annulus bands must both be preserved because they answer different questions.
- Sequence diagnosis must be evidence-based from metric tables; summary count figures alone must not be used to infer swarm, cascade, migration, or triggering style.
- Mechanism information is contextual and sparse relative to the catalog; absence of mechanism coverage is not negative evidence.
- Figure outputs required by the user are: `magnitude_time_distance_pm7d_100km.png`, `m4plus_sequence_views_pm7d_100km.png`, `prepost_magnitude_distance_counts_pm7d_100km.png`, and `m4_m5_distance_band_contribution_pm7d_100km.png`.
- Success evidence for the main script is non-empty merged metric tables for all three mainshocks and all requested windows/spatial definitions, plus the required figure files and per-mainshock behavior-dimension summary tables.

## Analysis Plan

### Task 1: Build the unified mainshock-centered sequence analysis dataset
- Task description: Load the catalog and mainshock table, standardize fields, compute relative geometry and timing for every event-mainshock pair, identify mainshock-like catalog matches, and create the master analysis table used by all downstream metrics and figures.
- Required data sources:
  - `catalog/Snet_catalog_relocate_250930_260501.csv`
  - `catalog/main_earthquake.csv`
  - optional context joins later from `source_mechanism/Snet_mecha.csv`
- Parameter selection strategy:
  - Parse origin times into a single timezone-consistent datetime format.
  - Standardize event identifiers if absent by creating stable row IDs from source row index.
  - For each event relative to each of M1/M2/M3, compute:
    - relative time in days and hours
    - epicentral distance in km
    - depth difference in km
    - cumulative-radius membership: <=30, <=60, <=100 km
    - annulus distance band: 0-30, 30-60, 60-100 km, outside-100 km
    - pre/post flag for each window: ±7, ±14, ±25 days
    - magnitude-bin labels for all events and for thresholded sets M4+, M5+, M6+
  - Mainshock-like event tolerance should combine:
    - minimum absolute relative time to the reference mainshock
    - small epicentral-distance tolerance
    - small depth-difference tolerance
    - magnitude consistency check if multiple candidates exist
  - If no unique candidate is found under the initial tolerance, relax tolerances stepwise and retain a diagnostic flag documenting how the match was chosen.
- Constraints:
  - Keep the original catalog rows intact; do not drop events outside 100 km because broader activation metrics need the full event-mainshock table before filtering.
  - Do not infer exact magnitude precision/bin width from decimals alone; use explicit bins suitable for requested M4+/M5+/M6+ threshold summaries.
  - The mainshock-like event should be included in visualization but excluded where the user requests supporting statistics without the mainshock.
- Key outputs:
  - Master event-mainshock table with one row per event-mainshock pair
  - Mainshock-match diagnostic table with chosen catalog row, tolerance used, and ambiguity flags
  - Window-filtered derivative tables for ±7, ±14, and ±25 days

### Task 2: Generate the required ±7 day sequence-morphology figures
- Task description: Produce the three required short-window comparison figures and the M4/M5 distance-band contribution figure for visual diagnosis across M1, M2, and M3.
- Required data sources:
  - Master event-mainshock table from Task 1
  - `catalog/main_earthquake.csv` for mainshock labels/order
- Parameter selection strategy:
  - Use the fixed short window: relative time within ±7 days and epicentral distance <=100 km.
  - Marker size should scale monotonically with magnitude using one consistent mapping across all subplots.
  - Distance-band colors must be fixed across all figures: 0-30 km, 30-60 km, 60-100 km.
  - M4+ events receive black edges in all relevant panels.
  - Mainshock-like event shown with a star and labeled consistently.
  - In `m4plus_sequence_views_pm7d_100km.png`, include only M4+ events in the plotted sample; exclude the mainshock-like event from supporting summary statistics but keep it as a reference marker.
  - In `prepost_magnitude_distance_counts_pm7d_100km.png`, summarize:
    - pre vs post magnitude-bin counts
    - pre vs post distance-band counts
    - annotations for M4+, M5+, M6+ totals
  - In `m4_m5_distance_band_contribution_pm7d_100km.png`, show both:
    - raw counts by distance band
    - normalized fractions/percentages by distance band
    for M4+ and M5+ separately across M1, M2, M3.
- Constraints:
  - Use these figures for comparison and support only; do not encode final behavioral conclusions directly into the plotting design.
  - Preserve the requested 3x2 row-column structure for the first two figures.
  - Include vertical time-zero reference lines and the requested horizontal reference lines on the appropriate panels.
  - Exclude decorative elements that do not support interpretation.
- Key outputs:
  - `magnitude_time_distance_pm7d_100km.png`
  - `m4plus_sequence_views_pm7d_100km.png`
  - `prepost_magnitude_distance_counts_pm7d_100km.png`
  - `m4_m5_distance_band_contribution_pm7d_100km.png`

### Task 3: Compute matched-window metric tables across windows and spatial definitions
- Task description: Build the exhaustive quantitative evidence tables for all requested windows and spatial definitions, including event rates, magnitude structure, distance structure, dominance metrics, companion-event counts, and sensitivity summaries.
- Required data sources:
  - Master event-mainshock table from Task 1
- Parameter selection strategy:
  - Time windows: ±7, ±14, ±25 days.
  - Spatial definitions:
    - cumulative radii: <=30, <=60, <=100 km
    - annulus bands: 0-30, 30-60, 60-100 km
  - For each mainshock, window, and spatial definition compute:
    - total event counts and rates for pre and post windows
    - M4+, M5+, M6+ counts and rates for pre and post windows
    - post/pre count ratios and rate ratios, with zero-handling flags
    - magnitude-bin counts for pre and post windows
    - largest pre and post non-mainshock events
    - top-ranked event list and magnitude-dominance gaps:
      - mainshock minus largest non-mainshock
      - gap between top non-mainshock events
    - companion-event counts within 0.5 and 1.0 magnitude units of the mainshock
    - distance-band contributions for all events and thresholded subsets
    - annulus-area-normalized activity rates where feasible for broader-activation context
    - immediate post-mainshock concentration metrics, such as first-day and first-3-day shares within the post window
    - simple decay diagnostics in the post period using short time bins
  - Build a compact sensitivity matrix over window × radius for a curated heatmap:
    - post/pre ratios
    - near-field share
    - M4+/M5+ concentration
    - dominance-gap metrics
- Constraints:
  - Keep separate tables for cumulative-radius and annulus-band analyses to avoid conflating near-field totals with outer-band structure.
  - The mainshock-like event must be excluded from non-mainshock dominance and companion statistics.
  - Any ratio with zero denominator must be flagged rather than silently inflated.
  - Optional robustness figure should only be added if ±14 d or ±25 d changes interpretation relative to ±7 d.
- Key outputs:
  - Full matched-window metric table
  - Thresholded event summary table for M4+, M5+, M6+
  - Dominance and companion-event summary table
  - Sensitivity-heatmap input table
  - Optional robustness-figure input table

### Task 4: Add depth and focal-mechanism context
- Task description: Characterize whether each mainshock-centered sequence occupies a compact or distributed depth domain and whether available focal mechanisms support a shared structural context or mixed behavior.
- Required data sources:
  - Master event-mainshock table from Task 1
  - `source_mechanism/Snet_mecha.csv`
  - `stations/station.sta` for optional network-coverage context map or coverage check
- Parameter selection strategy:
  - Summarize depth distributions for each mainshock-centered sequence within the requested short window and within expanded windows where useful:
    - all events <=100 km
    - M4+ subset
    - M5+ subset when sample size permits
  - Join focal mechanisms to catalog events using origin time and hypocentral proximity matching with explicit ambiguity flags.
  - For mechanism context summarize:
    - count of matched mechanisms per mainshock-centered sequence
    - dominant nodal-plane style categories if derivable
    - whether comparable large events share similar geometry/depth domain
    - whether outer-band events appear structurally distinct from near-field events
  - Use station metadata only for context if network geometry needs to be shown or checked for obvious spatial-coverage asymmetry in the study area.
- Constraints:
  - Mechanism interpretations must remain contextual because coverage is sparse.
  - Do not overstate structural similarity when the number of matched mechanisms is small or uncertain.
- Key outputs:
  - Depth-summary table by mainshock, window, and magnitude threshold
  - Mechanism-match table with confidence flags
  - Mechanism-context summary table
  - Optional context map or station-coverage note if needed for interpretation

### Task 5: Score the requested non-mutually-exclusive behavior dimensions
- Task description: Convert metric tables into explicit per-mainshock evidence scores for the seven requested dimensions, with supporting metrics and caveats recorded for each score.
- Required data sources:
  - Matched-window metric tables from Task 3
  - Depth/mechanism context from Task 4
  - Required figures from Task 2 for cross-checking, not primary scoring
- Parameter selection strategy:
  - Score levels: low, possible, moderate, strong.
  - For each mainshock evaluate and record:
    - Aftershock response:
      - short-window post/pre rate changes
      - first-day/first-3-day concentration
      - near-field post dominance
      - decay consistency in the post period
    - Magnitude hierarchy and compound-event structure:
      - mainshock vs largest non-mainshock gap
      - top-event spacing
      - companion counts within 0.5 and 1.0 magnitude units
      - optional moment-release concentration if feasible from magnitude
      - separate sub-scores for single-mainshock dominance and compact-cascade/compound-sequence evidence
    - Swarm-like organization:
      - weak dominance
      - repeated moderate/large events
      - multi-peak persistence
      - mismatch with simple post-mainshock decay
    - Foreshock/pre-mainshock activation:
      - pre M4+/M5+ counts
      - largest pre-event magnitude
      - timing and distance of largest pre-event
      - acceleration toward time zero if present
    - Broader regional activation:
      - fraction/rate of events and M4+/M5+ in 30-60 and 60-100 km bands
      - annulus-area-normalized comparisons
      - persistence outside the near field
    - Radial migration/expansion:
      - distance-time ordering
      - monotonic trend tests or rank correlation
      - activation-front estimate only if the ordering is coherent
    - Slow-slip-related candidate behavior:
      - sustained distributed activity
      - migration-like organization
      - plausible depth/structural consistency
      - capped conservatively unless strong catalog evidence exists
  - For every assigned score, attach:
    - the specific metric values used
    - a short caveat stating the main competing explanation or limitation
- Constraints:
  - Scores are evidence dimensions, not exclusive sequence labels.
  - Overlap among M1/M2/M3 windows must be checked explicitly so that apparent pre- or post-activity is not misattributed when another mainshock-centered sequence is nearby in time/space.
  - Do not assign moderate/strong slow-slip-related support from catalog evidence alone unless migration-like and structurally coherent evidence is clear.
- Key outputs:
  - Per-mainshock behavior-dimension score table
  - Evidence-and-caveat table with metric citations for each score
  - Cross-sequence comparison summary table

### Task 6: Assemble the concise scientific diagnosis and curated comparison products
- Task description: Synthesize the metric tables and figures into the requested final scientific diagnosis, including visual summary, per-mainshock interpretation, compact evidence table, caution statement, and verification needs.
- Required data sources:
  - Outputs from Tasks 2–5
- Parameter selection strategy:
  - Organize the final diagnosis into:
    1. visual summary of ±7 day behavior for M1, M2, M3
    2. per-mainshock interpretation across the scored dimensions
    3. compact evidence table with scores and key metrics
    4. short statement on what catalog evidence alone cannot establish
    5. short verification list needed to strengthen or reject interpretations
  - Include a curated figure set rather than exhaustive plotting for all windows.
  - Add one optional robustness figure only if extended windows materially change the interpretation.
- Constraints:
  - Keep the final interpretation concise and metric-based.
  - Do not present summary count figures as sole evidence for swarm, migration, or triggering style.
  - Distinguish local sequence behavior from broader regional activation in every per-mainshock diagnosis.
- Key outputs:
  - Final diagnosis document or structured summary table set
  - Compact evidence table for M1/M2/M3
  - Optional robustness figure if justified

### Task 7: Script organization and execution flow
- Task description: Execute the workflow with minimal cohesive scripts and explicit dependencies.
- Required data sources:
  - All sources above
- Parameter selection strategy:
  - Primary script:
    - load and validate inputs
    - build master event-mainshock table
    - identify mainshock-like events
    - compute all matched-window metrics
    - generate all required figures
    - save machine-readable tables for downstream interpretation
    - run immediate non-empty output checks
  - Secondary script:
    - read saved metric tables
    - compute behavior-dimension scores
    - assemble the concise diagnosis tables and optional robustness comparison
- Constraints:
  - Do not split plotting, metric computation, and validation into unnecessary separate scripts.
  - Successful execution requires valid merged scientific outputs, not only intermediate tables.
- Key outputs:
  - Script 1 outputs: master table, metric tables, figure files, diagnostics
  - Script 2 outputs: evidence-score tables, concise final diagnosis products