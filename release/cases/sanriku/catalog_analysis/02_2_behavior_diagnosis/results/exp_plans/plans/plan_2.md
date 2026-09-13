# Goal
Diagnose and compare the mainshock-centered sequence behavior around M1, M2, and M3 in the Aomori relocated catalog by constructing matched event tables, quantifying short-window and multi-window pre/post seismicity, adding depth and focal-mechanism context, and scoring non-mutually-exclusive behavior dimensions with explicit catalog-based evidence.

## Planning Assumptions
- Use observation/catalog data only; no model data are needed.
- Primary workflow can be completed in one cohesive catalog-analysis task script because data ingestion, feature construction, metrics, figures, and behavior scoring are tightly coupled.
- Main event identity should be assigned from `main_earthquake.csv`, while “mainshock-like event” in the relocated catalog should be matched using practical tolerances on origin time and hypocentral position; if multiple candidates satisfy the tolerance, choose the nearest combined time-space-magnitude match and record ambiguity.
- Epicentral distance should be computed from event latitude/longitude to each mainshock latitude/longitude; depth difference should be signed and absolute values retained for summary.
- Short-window morphology figures must use the fixed user-specified window: relative time within ±7 days and distance <=100 km.
- Matched-window metrics must be computed for ±7, ±14, and ±25 days using both cumulative radii (<=30, <=60, <=100 km) and annular bands (0–30, 30–60, 60–100 km).
- Behavior-dimension scores must be based on quantitative metrics and event lists; visual figures are supporting evidence, not the sole basis for classification.
- Distance-band concentration alone must not be used to infer swarm/cascade/migration; it must be interpreted jointly with time ordering, magnitude hierarchy, and event-chain structure.
- Catalog evidence alone cannot confirm slow slip, swarm physics, or causal triggering; these remain candidate interpretations requiring external verification.

## Analysis Plan

### Task 1. Build the mainshock-referenced event analysis table
- Task description:
  - Load the relocated catalog and mainshock table.
  - For each catalog event relative to each of M1, M2, and M3, create a long-format sequence table with derived spatiotemporal fields and classification flags.
- Required data sources:
  - `catalog/Snet_catalog_relocate_250930_260501.csv`
  - `catalog/main_earthquake.csv`
- Parameter selection strategy:
  - Parse event origin times into a uniform datetime standard.
  - For each event-mainshock pair compute:
    - `mainshock_id`
    - `event_time`
    - `rel_time_days`
    - `rel_time_hours` for immediate-post summaries
    - `epi_dist_km`
    - `depth_diff_km` and `abs_depth_diff_km`
    - `distance_band` with bins 0–30, 30–60, 60–100, >100 km
    - cumulative-radius flags `le_30km`, `le_60km`, `le_100km`
    - pre/post flags relative to time 0
    - magnitude-bin flags, at minimum: <4, 4–<5, 5–<6, >=6
    - threshold flags: M4+, M5+, M6+
  - Mainshock-like event identification:
    - Match each mainshock to the nearest relocated event using combined tolerance on origin time, epicentral distance, depth difference, and magnitude difference.
    - Use a practical staged tolerance, e.g. narrow first-pass and broader fallback; keep final matched event ID and mismatch diagnostics.
    - If no unique match exists, retain best candidate and emit ambiguity fields for review.
- Constraints:
  - Preserve all events for every mainshock reference, even if windows overlap between sequences.
  - Do not remove broader regional events at this stage; regional-vs-local separation is a later diagnostic.
- Key outputs:
  - `mainshock_referenced_event_table.csv`
  - `mainshock_like_match_summary.csv`

### Task 2. Produce fixed-window morphology figures for direct visual comparison
- Task description:
  - Generate the required ±7 day, <=100 km diagnostic figures for all three sequences in a consistent layout.
- Required data sources:
  - `mainshock_referenced_event_table.csv`
  - `catalog/main_earthquake.csv`
- Parameter selection strategy:
  - Filter to `abs(rel_time_days) <= 7` and `epi_dist_km <= 100`.
  - Use consistent axis ranges across rows where possible for cross-mainshock comparison.
  - Marker size scales with magnitude; M4+ receives black edge; mainshock-like event shown with star.
  - Use distance-band colors consistently across all panels.
  - Exclude mainshock-like event from supporting statistics for the M4+ figure, but display it as a reference marker if useful.
- Constraints:
  - Required figure products:
    - `magnitude_time_distance_pm7d_100km.png`
    - `m4plus_sequence_views_pm7d_100km.png`
    - `prepost_magnitude_distance_counts_pm7d_100km.png`
    - `m4_m5_distance_band_contribution_pm7d_100km.png`
  - The pre/post count summary figure is supporting only and must not be used alone to diagnose sequence type.
  - The M4+/M5+ distance-band contribution figure must include both raw counts and normalized fractions/percentages.
- Key outputs:
  - The four required figure files above
  - `pm7d_100km_event_subsets.csv` for reproducible figure provenance

### Task 3. Compute matched-window quantitative metrics across time windows and spatial definitions
- Task description:
  - Build exhaustive pre/post metric tables for each mainshock over ±7, ±14, and ±25 day windows and for cumulative-radius and annular-band spatial definitions.
- Required data sources:
  - `mainshock_referenced_event_table.csv`
- Parameter selection strategy:
  - Time windows: 7, 14, 25 days.
  - Spatial definitions:
    - cumulative radii: <=30, <=60, <=100 km
    - annuli: 0–30, 30–60, 60–100 km
  - For each mainshock × time window × spatial definition, compute pre and post metrics:
    - total event counts and rates
    - M4+/M5+/M6+ counts and rates
    - post/pre count and rate ratios
    - magnitude-bin counts and fractions
    - largest pre-event, largest post-event, largest non-mainshock event
    - magnitude gap between mainshock and largest non-mainshock event
    - gaps among top-ranked events
    - companion-event counts within 0.5 and 1.0 magnitude units of the mainshock
    - near-field vs outer-band contributions
    - annulus-area-normalized counts/rates where feasible
    - immediate-post concentration metrics (e.g., first 6 h, 12 h, 1 d, 3 d nested within the main window)
    - time-decay summary after the mainshock, using simple binned rate decline diagnostics
    - moment-release concentration if feasible from magnitude-derived scalar moment proxies
- Constraints:
  - Exclude the mainshock-like event from non-mainshock dominance and companion statistics where appropriate.
  - Report undefined ratios explicitly when pre counts are zero; do not silently regularize unless clearly flagged.
  - Keep cumulative-radius and annulus metrics separate to avoid interpretational mixing.
- Key outputs:
  - `matched_window_metrics_complete.csv`
  - `matched_window_metrics_summary.csv`
  - `largest_event_lists_by_window.csv`
  - `companion_event_metrics.csv`

### Task 4. Derive curated comparison figures from the metric tables
- Task description:
  - Convert exhaustive metric tables into a compact comparison set emphasizing cross-mainshock differences and robustness across windows/radii.
- Required data sources:
  - `matched_window_metrics_complete.csv`
  - `matched_window_metrics_summary.csv`
  - `companion_event_metrics.csv`
- Parameter selection strategy:
  - Produce high-level comparison figures only, not one figure per window-definition combination.
  - Required figure themes:
    - pre/post magnitude-bin and distance-band summary
    - M4+/M5+ distance-band contribution with counts and normalized fractions
    - magnitude-dominance and companion-event summary
    - sensitivity heatmaps across time windows and radii
    - one optional robustness figure if ±14 d or ±25 d reveals a distinct pattern not visible in ±7 d
  - Suggested panels:
    - heatmaps of post/pre ratios for all events, M4+, and M5+ across time window × radius
    - bar/dot summaries of mainshock-minus-largest-companion gap and counts within 0.5/1.0 magnitude units
    - near-field fraction vs outer-band fraction for M4+/M5+
- Constraints:
  - Use figures for comparison, while complete metrics remain in tables.
  - If robustness figure is added, it must address a distinct scientific contrast rather than duplicate the short-window view.
- Key outputs:
  - `magnitude_dominance_companion_summary.png`
  - `sensitivity_heatmaps_time_radius.png`
  - optional `robustness_comparison_additional_window.png`

### Task 5. Add depth and focal-mechanism context
- Task description:
  - Summarize depth structure of each mainshock-centered sequence and compare available focal mechanisms to assess whether events occupy similar structural domains.
- Required data sources:
  - `mainshock_referenced_event_table.csv`
  - `source_mechanism/Snet_mecha.csv`
  - `catalog/main_earthquake.csv`
- Parameter selection strategy:
  - For each mainshock and selected windows/spatial subsets, compute:
    - depth distribution summaries for all events and separately for M4+ and M5+
    - pre vs post depth statistics
    - depth difference relative to mainshock
  - Join mechanism records to relocated events by practical time-space matching; preserve match quality flags.
  - Summarize, where coverage exists:
    - nodal-plane and principal-axis tendencies
    - whether mechanism-bearing events cluster within one sequence and one depth domain
    - whether moderate/large companion events appear mechanism-consistent or heterogeneous
- Constraints:
  - Mechanism coverage is partial; absence of mechanism data must not be interpreted as evidence.
  - Mechanism context is supportive, not a stand-alone classifier of sequence type.
- Key outputs:
  - `depth_sequence_summary.csv`
  - `mechanism_match_summary.csv`
  - `depth_mechanism_context.png`

### Task 6. Score non-mutually-exclusive behavior dimensions for M1, M2, and M3
- Task description:
  - Evaluate each mainshock-centered sequence along the requested evidence axes and assign levels: low, possible, moderate, strong.
- Required data sources:
  - `matched_window_metrics_complete.csv`
  - `largest_event_lists_by_window.csv`
  - `companion_event_metrics.csv`
  - `depth_sequence_summary.csv`
  - `mechanism_match_summary.csv`
  - event-level subsets from Task 1/2
- Parameter selection strategy:
  - Score each dimension using explicit metrics and event lists, with a short rationale and caveats:
    - Aftershock response:
      - post/pre rate changes
      - immediate post concentration
      - near-field dominance
      - post-mainshock decay consistency
    - Magnitude hierarchy and compound-event structure:
      - mainshock-largest non-mainshock gap
      - top-event gaps
      - companion counts within 0.5 and 1.0 magnitude units
      - moment concentration if available
      - separately score single-mainshock dominance and compact-cascade/compound evidence
    - Swarm-like organization:
      - weak dominance
      - repeated M4+/M5+/M6 events
      - small magnitude gaps
      - persistent or multi-peak activity
      - poor fit to simple single-mainshock decay pattern
    - Foreshock/pre-mainshock activation:
      - M4+/M5+ counts before mainshock
      - largest pre-event magnitude
      - timing and distance of largest pre-event
      - acceleration toward time 0 where present
    - Broader regional activation:
      - fractions and rates in 30–60 and 60–100 km bands
      - annulus-area-normalized outer-band activity
      - persistence outside near field
    - Radial migration/expansion:
      - time-distance trend metrics
      - rank correlation or regression slope
      - ordered activation-front behavior if detectable
      - otherwise state no monotonic progression supported
    - Slow-slip-related candidate behavior:
      - sustained broad activity
      - plausible depth/structural consistency
      - migration-like behavior
      - assign only low/possible unless unusually coherent catalog evidence exists
  - For each score, record:
    - supporting metrics
    - contradictory metrics
    - principal caveats, including sequence overlap with other mainshocks or regional activation
- Constraints:
  - Dimensions are not mutually exclusive.
  - Do not elevate slow-slip-related candidate behavior beyond what catalog evidence supports.
  - Do not equate swarm-like organization with a confirmed physical swarm.
- Key outputs:
  - `behavior_dimension_scores.csv`
  - `behavior_dimension_evidence_table.csv`

### Task 7. Assemble concise scientific diagnosis and verification needs
- Task description:
  - Write the final stage report synthesizing visual, tabular, and metric-based evidence for the three sequences.
- Required data sources:
  - All outputs from Tasks 2–6
  - `stations/station.sta` for optional network-context map or coverage note if needed
- Parameter selection strategy:
  - Structure the report to include:
    1. concise visual summary of the ±7 day behavior for M1, M2, M3
    2. per-mainshock interpretation across the behavior dimensions
    3. compact evidence table with scores and key metrics
    4. explicit statement of what catalog evidence alone cannot establish
    5. short prioritized verification list
  - Verification list should focus on analyses most diagnostic for ambiguous cases:
    - Omori/ETAS comparison of post-mainshock decay
    - relocated subcluster and double-difference checks for compact cascade vs swarm-like behavior
    - waveform similarity/cross-correlation for repeated-source behavior
    - focal mechanism consistency tests with higher-coverage solutions
    - GNSS/tremor/ocean-bottom-pressure or SSE catalog comparison for slow-slip screening
- Constraints:
  - Keep claims tied to observed metrics.
  - Clearly separate diagnosis, hypothesis, and required external validation.
- Key outputs:
  - `aomori_mainshock_sequence_diagnosis.md`
  - `aomori_sequence_evidence_summary.csv`

### Task 8. Optional network-context check for interpretability support
- Task description:
  - Use station metadata only to provide contextual reassurance that the sequence interpretation is not obviously driven by a highly asymmetric local station footprint.
- Required data sources:
  - `stations/station.sta`
  - `catalog/main_earthquake.csv`
- Parameter selection strategy:
  - Summarize station distribution around M1, M2, and M3 and optionally overlay station/mainshock map.
  - Use only as context, not as a core diagnostic.
- Constraints:
  - Do not infer catalog completeness quantitatively from station positions alone unless metadata support it.
- Key outputs:
  - optional `station_mainshock_context.png`
  - `station_context_summary.csv`