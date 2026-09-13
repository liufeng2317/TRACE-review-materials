# Goal
Assess whether the M1, M2, and M3 Aomori earthquake clusters exhibit meaningful catalog-level relationships worth deeper physical follow-up, by comparing all three pairwise relationships symmetrically and separating raw catalog evidence, control-corrected evidence, and distance-aware plausibility across multiple candidate hypotheses.

## Planning Assumptions
- Use the observation-based relocated catalog as the primary evidence source; no model data are required for this task.
- Primary analysis inputs are `catalog/Snet_catalog_relocate_250930_260501.csv` and `catalog/main_earthquake.csv`; contextual interpretation uses `source_mechanism/Snet_mecha.csv` and `stations/station.sta`.
- The plan should preserve ambiguity: events are not forced into exclusive sequence membership unless uniquely supported by geometry and timing.
- Distances should be computed consistently for all event-mainshock and event-pair relations; epicentral distance, along-corridor projection, cross-corridor offset, depth difference, and relative time are all required derived quantities.
- Main task can be executed in one cohesive analysis script because data ingestion, preprocessing, relationship metrics, controls, and figure generation are tightly coupled.
- Success evidence is not just completion of metric calculations; the workflow must produce non-empty pairwise comparison tables, control-corrected summaries, ambiguity-aware event classifications, and the compact diagnostic figure set requested by the user.

## Analysis Plan

### Task 1 — Build a unified relationship-analysis dataset
- Task description:
  - Load the relocated catalog and the 3-event mainshock table.
  - Standardize event fields and derive all event-relative quantities needed for pairwise relationship testing.
  - Attach contextual mechanism and station metadata only where useful for interpretation and follow-up prioritization.
- Required data sources:
  - `catalog/Snet_catalog_relocate_250930_260501.csv`
  - `catalog/main_earthquake.csv`
  - `source_mechanism/Snet_mecha.csv`
  - `stations/station.sta`
- Parameter selection strategy:
  - Parse origin times to a common timezone-aware or explicitly timezone-naive datetime standard and verify ordering.
  - Treat M1, M2, M3 in the mainshock table as the only anchor events.
  - For each catalog event, compute:
    - relative time to each mainshock
    - epicentral distance to each mainshock
    - depth difference to each mainshock
    - nearest mainshock in epicentral distance
    - nearest mainshock in 3D hypocentral distance if depth quality is adequate
  - For each pair (M1-M2, M1-M3, M2-M3), compute:
    - pair separation distance
    - azimuth from endpoint A to endpoint B
    - event projection onto pair corridor axis
    - cross-corridor offset
    - signed distance to each endpoint along corridor
    - corridor-normalized position from one endpoint to the other
  - Join focal mechanisms by event time and location tolerance only if direct event identifiers are absent; preserve unmatched rows.
- Constraints:
  - Remove exact duplicate catalog rows if present; do not merge nearby distinct events.
  - Do not infer uncertainty from decimal precision; use only documented fields.
  - Mechanism metadata are partial and must not be used as a completeness filter for the main relationship analysis.
  - Station metadata are contextual only; use them for network-geometry sanity checks, not for catalog-event assignment.
- Key outputs:
  - Cleaned event table with derived event-mainshock metrics
  - Pairwise geometry table for the three mainshock pairs
  - Event-pair projection table for all catalog events relative to each pair
  - Optional mechanism-join summary table and station-coverage context summary

### Task 2 — Symmetric pairwise relationship screening for M1-M2, M1-M3, and M2-M3
- Task description:
  - Evaluate all three pairs with the same metric family before focusing interpretation.
  - Quantify temporal overlap, spatial overlap, intervening activity, and endpoint dominance.
- Required data sources:
  - Unified relationship-analysis dataset from Task 1
- Parameter selection strategy:
  - For each pair, derive event subsets for magnitude thresholds:
    - all events
    - M3+
    - M4+
    - M5+
    - M6+ if present
  - For each threshold and pair, compute:
    - time separation between mainshocks
    - number and rate of events between the two mainshock origin times
    - number and rate in matched pre- and post-windows around each mainshock
    - event counts in distance bands around each endpoint and within the inter-endpoint corridor
    - nearest-mainshock split and ambiguous-zone fraction
    - fraction of events falling between endpoints in corridor coordinates
    - endpoint-centered versus corridor-centered concentration statistics
    - depth-distribution comparison for endpoint and corridor populations
  - Define ambiguity-aware classes per pair:
    - uniquely associated with endpoint A
    - uniquely associated with endpoint B
    - shared/overlapping
    - corridor-like
    - endpoint-centered
    - outer-cluster
    - regional/background
    - unresolved
  - Use distance bands based on physical relation to pair spacing:
    - near-endpoint inner band
    - intermediate band
    - outer band
    - corridor band using cross-corridor width scaled to pair distance and checked against fixed-width sensitivity labels in outputs
- Constraints:
  - Apply the same classification logic to all pairs.
  - Do not use only post/pre ratios to rank linkage.
  - Pairwise interpretation must keep raw metrics separate from corrected/control metrics.
  - If one pair is much farther apart than the others, interpret corridor occupancy against pair distance, not absolute counts alone.
- Key outputs:
  - Pairwise screening table with symmetric metrics for all three pairs
  - Ambiguity-aware event classification table for each pair
  - Pairwise summary scores for temporal overlap, spatial overlap, corridor occupancy, endpoint dominance, and outer-band activation

### Task 3 — Relationship-aware controls to test whether apparent linkage could arise from burst-like background seismicity or window choice
- Task description:
  - Quantify how much of the apparent pairwise relationship survives simple controls.
  - Distinguish raw co-activation from robust pair-specific evidence.
- Required data sources:
  - Unified relationship-analysis dataset from Task 1
  - Pairwise screening outputs from Task 2
- Parameter selection strategy:
  - Build matched control tests for each pair:
    - random-window controls: compare observed between-mainshock and post-mainshock counts/rates with counts from many equal-duration windows sampled within the catalog span while avoiding endpoint overlap conflicts
    - pseudo-corridor controls: rotate or laterally shift the corridor while preserving corridor length and width to test whether observed corridor occupancy exceeds generic regional density
    - endpoint-label permutation or time-shift controls where feasible to test whether nearest-mainshock asymmetry and event-chain structure are stronger than expected by chance under the same catalog density
    - local background controls: compare observed counts to surrounding annulus or side-band counts to distinguish corridor enhancement from broad regional activation
  - For each raw metric, compute corrected quantities such as:
    - observed minus control median
    - percentile or empirical p-like exceedance rank
    - standardized effect size using control spread
  - Summarize whether evidence is:
    - raw-only
    - survives controls
    - weakened strongly by controls
    - inconclusive because controls are unstable or too sparse
- Constraints:
  - Controls must preserve basic catalog density structure as much as possible.
  - Sparse M5+/M6+ populations should be treated descriptively if inferential controls are unstable.
  - Negative or null control results must be reported, not suppressed.
- Key outputs:
  - Control distribution summary table for each pair and metric family
  - Corrected pairwise evidence table
  - Flags identifying metrics likely explained by burst-like background seismicity or window-choice effects

### Task 4 — Distance-aware plausibility assessment of candidate relationship hypotheses
- Task description:
  - Translate the measured metrics into hypothesis-oriented evidence statements without inferring causation.
  - Evaluate whether pair spacing, depth offset, timing, and event distribution are more compatible with local linkage, delayed nearby activation, regional activation, or apparent association only.
- Required data sources:
  - Pairwise geometry and screening outputs from Tasks 2–3
  - Contextual focal-mechanism summary from Task 1
- Parameter selection strategy:
  - For each pair-hypothesis combination, evaluate evidence using three separated columns:
    - raw catalog evidence
    - control-corrected evidence
    - distance-aware plausibility
  - Candidate hypotheses to score:
    - independent local clusters
    - overlapping activation zones
    - delayed activation between clusters
    - linked local fault-system activation
    - corridor-like migration or expansion
    - broader regional activation
    - compound/swarm-like multi-event clustering
    - apparent relationship caused by burst-like background seismicity or window choices
  - Add additional hypotheses only if directly supported by metrics, such as:
    - endpoint-dominated dual activation without corridor linkage
    - outer-band regional cascade
  - Use qualitative evidence levels:
    - low
    - possible
    - moderate
    - strong
  - Use follow-up priority levels:
    - low
    - medium
    - high
  - Mechanism context, where available, should only upgrade follow-up priority if it aligns with catalog geometry; missing mechanisms must not count against a pair.
- Constraints:
  - Temporal order and proximity alone cannot support triggering claims.
  - Distance-aware plausibility must be allowed to downgrade raw temporal relationships.
  - A pair may support more than one catalog-level hypothesis simultaneously.
- Key outputs:
  - Pair-hypothesis evidence matrix
  - Follow-up priority matrix
  - Shortlist of strongest supported relationship signals
  - List of weak, negative, and unresolved relationships

### Task 5 — High-value diagnostic figures for relationship discrimination
- Task description:
  - Produce a compact figure set that directly clarifies whether relationships are pair-specific, regional, corridor-like, ambiguous, or control-sensitive.
- Required data sources:
  - Outputs from Tasks 1–4
- Parameter selection strategy:
  - Generate the following priority figures:
    1. Pairwise relationship overview map
       - catalog epicenters, M1/M2/M3 anchors, pair corridors, distance bands, and event classes
    2. Three-panel pairwise time-distance plot
       - for each pair, event time relative to endpoints vs distance/projection position, colored by magnitude threshold and/or ambiguity class
    3. Corridor-projection versus cross-corridor offset figure
       - one panel per pair showing endpoint-centered, shared, and corridor-like populations
    4. M4+/M5+/M6+ intervening-event chain comparison
       - timeline or lollipop panels highlighting larger events between/around endpoints
    5. Corridor versus off-corridor control comparison
       - observed vs pseudo-corridor or side-band distributions for each pair
    6. Relationship evidence matrix
       - pair-hypothesis heatmap with evidence level and separate markers for raw, corrected, and distance-aware support
    7. Follow-up priority summary
       - compact ranking figure for which pair-hypothesis combinations deserve waveform/mechanism/geodetic/stress follow-up
  - Add one optional figure only if it materially clarifies a disputed interpretation:
    - depth-vs-corridor-position panel
    - nearest-mainshock ambiguity map
    - outer-band activation timeline
- Constraints:
  - Keep figure count compact and non-redundant.
  - Each figure must correspond to a specific hypothesis discrimination purpose.
  - Do not generate exhaustive map/time-series variants.
- Key outputs:
  - Compact diagnostic figure set
  - Figure-level captions or machine-readable figure summary table linking each figure to tested hypotheses

### Task 6 — Final scientific synthesis and follow-up recommendations
- Task description:
  - Assemble a concise report that answers the core question: which relationship hypotheses are supported, weak, unresolved, or likely artifacts of catalog structure and windowing.
- Required data sources:
  - Outputs from Tasks 2–5
- Parameter selection strategy:
  - Structure the report in this order:
    - pairwise evidence summary for M1-M2, M1-M3, M2-M3
    - relationship evidence matrix across hypotheses
    - strongest supported relationship signals
    - weak/negative/unresolved evidence
    - distinction between raw evidence, control-corrected evidence, and distance-aware plausibility
    - recommended next physical analyses and external data needs
  - For each pair, explicitly state:
    - what looks related in raw catalog metrics
    - what remains after controls
    - whether the spacing/geometry make local linkage plausible, only regional linkage plausible, or largely unsupported
  - Recommend follow-up data/modeling by hypothesis type:
    - waveform similarity and template matching for delayed or chain-like linkage
    - refined relocation for corridor-like or overlapping activation
    - focal mechanisms for fault-system compatibility
    - station/network geometry checks where spatial gaps may bias interpretation
    - geodetic, ocean-bottom pressure, or stress modeling for regional or broader activation hypotheses
- Constraints:
  - Do not present causal triggering conclusions.
  - Explicitly identify contradictions between metric families.
  - Preserve uncertainty where event counts are sparse or controls are unstable.
- Key outputs:
  - Final concise scientific report
  - Pairwise evidence summary table
  - Pair-hypothesis evidence matrix with evidence level and follow-up priority
  - Recommended next-step data and analysis checklist