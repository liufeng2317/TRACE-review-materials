# Goal
Screen the relocated Aomori catalog for the M1-M3 event-chain structure within the local M1-M3 system, separating the M1-related dominated phase from later M1-M3 activity, and determine whether the catalog pattern is better described as pre-existing local activity, sustained activation, separated bursts, endpoint-centered activity, corridor-like activity, pre-M3 local activation, broader/background activity, migration-like behavior, endpoint switching, or M2-affected mixed behavior.

## Planning Assumptions
- Use observation catalog data only; no model data are needed.
- Primary analysis domain is the M1-M3 local union: events within 60 km of either M1 or M3.
- The relocated catalog `catalog/Snet_catalog_relocate_250601_260501.csv` is headerless and must be loaded with explicit columns: origin_time, latitude, longitude, depth_km, magnitude.
- `catalog/main_earthquake.csv` provides the authoritative M1, M2, M3 event definitions and must be used to build all event-relative time windows and geometry.
- `source_mechanism/Snet_mecha.csv` is optional and should only be used for follow-up candidate flagging; incomplete mechanism rows must not shape the primary screening conclusions.
- `stations/station.sta` is optional context for later QC and is not required for the primary catalog geometry/rate analysis.
- Time windows for the main interpretation must remain the fixed non-overlapping windows requested by the user:
  - pre-M1 baseline primary: catalog start to M1-14 d
  - pre-M1 baseline sensitivity: catalog start to M1-7 d
  - M1-related dominated phase primary: M1-14 d to M1+21 d
  - middle phase primary: M1+21 d to M3-35 d
  - pre-M3 activation primary: M3-35 d to M3
  - post-M3 context: M3 to M3+7 d and optionally M3+14 d
- Optional data-driven boundary refinements may be tested only as secondary sensitivity checks and must not replace the fixed-window interpretation.
- Distances should be geodetic/hypocentral-consistent at catalog-screening level: horizontal great-circle distance for region membership and axis projection; depth retained separately for summaries and burst descriptions.
- Corridor membership should be computed from projection onto the M1-M3 axis segment with endpoint buffers included; primary corridor-width sensitivity should compare 20 km and 30 km.
- M2-related events are to be flagged, not dropped by default; all key metrics should be reported in raw and M2-aware forms.
- One primary task script is sufficient because data loading, derived-metric construction, screening summaries, burst detection, and figure production are tightly coupled and share the same catalog table.

## Analysis Plan

### Task 1: Build the unified M1-M3 event-chain analysis table
- Task description:
  Load the relocated catalog and mainshock table, define M1/M2/M3 reference parameters, compute all event-relative time and geometry fields, assign spatial categories, and create the master event-chain table used by all later summaries and figures.
- Required data sources:
  - `catalog/Snet_catalog_relocate_250601_260501.csv`
  - `catalog/main_earthquake.csv`
  - optional context only: `source_mechanism/Snet_mecha.csv`, `stations/station.sta`
- Parameter selection strategy:
  - Read the relocated catalog with explicit columns: origin_time, latitude, longitude, depth_km, magnitude.
  - Parse event times to a unified timezone/UTC-naive timestamp convention consistent across both files.
  - Extract M1, M2, M3 origin time, latitude, longitude, depth, magnitude from `main_earthquake.csv`.
  - Compute for every catalog event:
    - time_since_M1_days
    - time_before_M3_days
    - horizontal_distance_to_M1_km
    - horizontal_distance_to_M3_km
    - horizontal_distance_to_M2_km
    - along_axis_km projected onto the M1→M3 axis
    - perpendicular_distance_to_axis_km
    - nearest_endpoint label
    - depth_km
    - magnitude
  - Define spatial membership:
    - local_union_60km: within 60 km of M1 or M3
    - M1_core_30km, M3_core_30km
    - M1_extended_60km, M3_extended_60km
    - corridor_20km and corridor_30km: projected between endpoints with endpoint buffers
    - off_corridor_local: in local_union_60km but outside selected corridor
  - Define mutually interpretable spatial categories for summaries:
    - M1-core
    - M3-core
    - corridor non-core
    - off-corridor local
    - outside local union
  - Define M2 flags:
    - M2_related_100km: within 100 km of M2
    - ambiguous_M2_overlap: events simultaneously in local_union_60km and M2-related_100km, or lying in geometry where endpoint/corridor interpretation could be M2-influenced
- Constraints:
  - Do not use the whole catalog as the primary spatial domain; first restrict analysis to local_union_60km and then compare with broader/context metrics only as secondary checks.
  - Do not remove M2-related events in the master table.
  - Keep raw geometry and all alternate category flags so later sensitivities can be recomputed without rebuilding the table.
- Key outputs:
  - `M1_M3_event_chain_table.csv`
  - `M1_M3_reference_table.csv`
  - `M1_M3_spatial_category_counts.csv`

### Task 2: Assign fixed phase windows and compute baseline/rate summaries
- Task description:
  Partition the local_union catalog into the required fixed windows, compute M3+/M4+/M5+/M6+ counts and rates, compare baseline vs M1-related vs middle vs pre-M3 phases, and quantify how much of full M1-to-M3 activity is concentrated in the M1-related dominated phase.
- Required data sources:
  - `M1_M3_event_chain_table.csv` from Task 1
- Parameter selection strategy:
  - Primary fixed windows:
    - pre_M1_baseline_14d: catalog_start to M1-14 d
    - pre_M1_baseline_7d: catalog_start to M1-7 d
    - M1_dominated_primary: M1-14 d to M1+21 d
    - full_M1_to_M3: M1 to M3
    - middle_primary: M1+21 d to M3-35 d
    - pre_M3_primary: M3-35 d to M3
    - post_M3_7d and optionally post_M3_14d
  - Optional sensitivity windows only if burst gaps justify them:
    - M1-7 d to M1+14 d
    - M1-14 d to M1+28 d
    - M3-42 d to M3
    - M3-28 d to M3
  - For each window and magnitude threshold M3+, M4+, M5+, M6+ compute:
    - event count
    - window duration in days
    - rate per day
    - contribution fraction to full local_union M1-to-M3 total
    - raw and M2-aware versions
  - Compare:
    - baseline_14d vs M1_dominated_primary
    - baseline_7d vs M1_dominated_primary
    - M1_dominated_primary vs middle_primary
    - middle_primary vs pre_M3_primary
    - raw vs M2-aware in every window
- Constraints:
  - The conservative baseline for all primary rate comparisons must end at M1-14 d.
  - Any baseline ending at M1 must not be used as a primary reference.
  - Do not merge M1-dominated and pre-M3 windows into a single narrative sequence.
- Key outputs:
  - `window_magnitude_rate_summary_raw.csv`
  - `window_magnitude_rate_summary_M2aware.csv`
  - `baseline_vs_phase_comparisons.csv`
  - `phase_contribution_to_full_M1_M3_interval.csv`

### Task 3: Quantify endpoint/core/corridor/off-corridor composition by window
- Task description:
  Determine whether each phase is endpoint-centered, corridor-like, or broadly local/off-corridor by summarizing spatial composition and explicit M1-core vs M3-core contrasts.
- Required data sources:
  - `M1_M3_event_chain_table.csv`
  - window definitions from Task 2
- Parameter selection strategy:
  - For each fixed window and each magnitude threshold at minimum M3+ and M4+:
    - counts and fractions in:
      - M1-core
      - M3-core
      - corridor non-core
      - off-corridor local
    - M1_extended vs M3_extended counts
    - nearest-endpoint proportions
  - Produce both:
    - raw composition
    - M2-aware composition with M2-related events flagged and either excluded or reported separately
  - Sensitivity checks:
    - corridor width 20 km vs 30 km
    - endpoint radius emphasis 30 km vs 60 km
- Constraints:
  - Use the mutually interpretable category scheme consistently across windows.
  - Corridor interpretation must distinguish corridor non-core from endpoint cores; core events should not be absorbed into corridor totals.
- Key outputs:
  - `window_spatial_composition_raw.csv`
  - `window_spatial_composition_M2aware.csv`
  - `endpoint_vs_corridor_sensitivity.csv`

### Task 4: Detect bursts and classify their phase affiliation
- Task description:
  Identify major bursts or rate peaks within the local_union domain, describe their timing and geometry, and assign each burst to M1-dominated, middle, pre-M3, post-M3, or mixed/ambiguous behavior.
- Required data sources:
  - `M1_M3_event_chain_table.csv`
  - window assignments from Task 2
- Parameter selection strategy:
  - Use a simple catalog-level burst detector appropriate for event times:
    - daily or multi-day binned event-rate series for M3+/M4+
    - supplement with inter-event time/gap analysis to identify clear quiet gaps separating clusters
  - For each detected burst compute:
    - burst start/end time
    - duration
    - event count by threshold
    - maximum magnitude
    - median and range of depth
    - centroid latitude/longitude
    - along-axis centroid
    - dominant spatial category
    - M2-related fraction
    - assigned phase label
  - Define “major burst” using transparent thresholds such as local peaks above baseline rate and/or clusters bounded by pronounced temporal gaps; record the rule used in the output table.
- Constraints:
  - Burst detection is secondary to the fixed-window framework; bursts must be reported within or across those windows, not used to redefine the whole interpretation.
  - Do not claim causal triggering from burst ordering.
- Key outputs:
  - `burst_catalog.csv`
  - `burst_phase_assignment.csv`
  - `burst_summary_by_window.csv`

### Task 5: Test apparent migration versus endpoint switching
- Task description:
  Evaluate whether any along-axis progression remains after separating the M1-dominated, middle, and pre-M3 windows, and distinguish continuous migration from mixed endpoint sequences.
- Required data sources:
  - `M1_M3_event_chain_table.csv`
  - `burst_catalog.csv`
- Parameter selection strategy:
  - Compute for the full M1-to-M3 interval:
    - rolling or binned along-axis centroid through time
    - rolling nearest-endpoint fraction through time
  - Repeat separately for:
    - M1-dominated primary
    - middle primary
    - pre-M3 primary
  - Compare:
    - trend slope and monotonicity of along-axis centroid
    - stability of perpendicular-distance distribution
    - transitions in M1-core, corridor non-core, M3-core occupancy
  - Add M2-aware replication of the same trends.
  - Classify the pattern as:
    - robust migration-like
    - endpoint switching
    - mixed endpoint/corridor activity
    - no coherent trend
- Constraints:
  - Do not label a full-interval centroid trend as migration if it disappears after window separation.
  - If the trend is caused by mixing M1-core early events and later M3-core events, report endpoint switching/mixed sequences instead.
- Key outputs:
  - `along_axis_trend_full_vs_windowed.csv`
  - `endpoint_transition_summary.csv`
  - `migration_classification_notes.csv`

### Task 6: Compare raw and M2-aware interpretations
- Task description:
  Quantify how much M2-related activity influences event-chain metrics, figures, and qualitative classification.
- Required data sources:
  - outputs from Tasks 2–5
- Parameter selection strategy:
  - Recompute the main metrics in two versions:
    - raw local_union
    - M2-aware local_union with M2-related events separated or excluded from local M1-M3 summaries
  - Compare:
    - counts/rates by window and threshold
    - spatial composition fractions
    - burst catalog membership
    - along-axis trend metrics
    - pre-M3 activation signal strength
  - Flag conclusions as:
    - robust to M2-aware treatment
    - moderately affected
    - strongly M2-dependent / ambiguous
- Constraints:
  - M2-related events must be quantified, not assumed to be contamination.
- Key outputs:
  - `raw_vs_M2aware_comparison.csv`
  - `M2_influence_flags.csv`

### Task 7: Add a simple background/control comparison
- Task description:
  Use a minimal control comparison to distinguish whether the M1-M3 local pattern exceeds broader background behavior in time or space without expanding the study into a regional model analysis.
- Required data sources:
  - `M1_M3_event_chain_table.csv`
  - original relocated catalog
- Parameter selection strategy:
  - Prefer one or both simple controls:
    - control time: earlier local_union baseline window compared with later windows
    - control space: off-corridor local or outside-local-union events over the same time windows
  - Compare normalized rates for M3+/M4+ to see whether apparent chain behavior is locally concentrated or resembles broad regional activity.
- Constraints:
  - Control analysis must remain secondary and simple.
  - Do not let broad regional activity redefine the primary local_union interpretation.
- Key outputs:
  - `control_comparison_summary.csv`

### Task 8: Produce the required diagnostic figures and compact screening products
- Task description:
  Generate the requested figure set and concise machine-readable screening outputs that support the final narrative classification.
- Required data sources:
  - outputs from Tasks 1–7
- Parameter selection strategy:
  - Required figures:
    - M1-M3 map with M3+/M4+/M5+ events colored by time and labeled by category; mark M1, M2, M3, 30 km and 60 km endpoint zones, and corridor envelope
    - magnitude-time plot from pre-M1 through M3 and short post-M3 context
    - projected along-axis distance vs time
    - distance-to-M1 and distance-to-M3 vs time
    - cumulative M4+/M5+ curves for raw and M2-aware versions
    - burst timeline summary with fixed windows marked
    - pre-M3 activation comparison before and after M2-aware treatment
    - window-separated composition chart for M1-core, M3-core, corridor non-core, off-corridor local fractions
  - Recommended annotations:
    - vertical lines at M1, M1+21 d, M3-35 d, M3, post-M3 endpoint
    - optional sensitivity boundaries only if used in text/tables
- Constraints:
  - Keep figures compact and diagnostic, not exhaustive.
  - Post-M3 context must remain visually separated from pre-M3 interpretations.
- Key outputs:
  - `fig_map_M1_M3_chain`
  - `fig_magnitude_time`
  - `fig_along_axis_time`
  - `fig_distance_to_endpoints_time`
  - `fig_cumulative_counts_raw_vs_M2aware`
  - `fig_burst_timeline`
  - `fig_preM3_activation_raw_vs_M2aware`
  - `fig_window_spatial_composition`
  - `screening_summary_table.csv`

### Task 9: Final classification and follow-up prioritization
- Task description:
  Convert the quantitative outputs into the required catalog-level screening labels and identify which follow-up analyses are justified.
- Required data sources:
  - all prior outputs
  - optional mechanism context from `source_mechanism/Snet_mecha.csv` only for follow-up recommendations
- Parameter selection strategy:
  - For each label, define evidence from prior tasks:
    - pre-existing local activity before M1: elevated baseline local_union rate or repeated pre-M1 bursts
    - M1-related swarm/aftershock-dominated: strong rate increase in M1-14 d to M1+21 d over baseline
    - quiet vs sustained middle phase: middle-phase rates and burst occupancy after removing M1-dominated phase
    - continuous activation chain: lack of major gaps plus non-endpoint continuity across windows
    - separated bursts: discrete clusters separated by low-rate intervals
    - endpoint-centered: core-zone dominance in one or both endpoints
    - pre-M3 local activation: M3-35 d to M3 increase, especially near M3-core or corridor, independent of M1 phase
    - corridor-like: substantial corridor non-core occupancy across relevant windows
    - migration-like: window-separated along-axis progression that persists after M2-aware checks
    - endpoint switching/mixed: full-interval trend explained by separate M1-core and M3-core bursts
    - broader/background activity: off-corridor or outside-local-union behavior similar to local signal
    - M2-affected: classification changes materially under M2-aware treatment
  - Recommend follow-up only where screening shows a clear unresolved pattern:
    - spatial-depth screening if bursts differ strongly in depth or endpoint depth structure
    - b-value/completeness screening if rate/magnitude differences between phases are strong enough
    - migration screening if window-separated along-axis progression persists
    - mechanism screening if pre-M3 or corridor bursts overlap with enough complete solutions in `Snet_mecha.csv`
- Constraints:
  - Keep the final report catalog-level and non-causal.
  - Mechanism interpretations must be framed as hypotheses for follow-up only.
- Key outputs:
  - `final_screening_classification.csv`
  - `followup_priority_list.csv`
  - concise final report structured around the user’s requested labels and questions