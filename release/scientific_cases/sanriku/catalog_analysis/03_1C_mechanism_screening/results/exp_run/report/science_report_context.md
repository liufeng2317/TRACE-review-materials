<science_report_context>

## Scientific Objective
<user_request>
You are an earthquake scientist and data-analysis agent.

Current task:
Analyze b-value, magnitude hierarchy, and moment-release patterns of the M1-M3 local earthquake system.

Goal:
Use the relocated/filtered Aomori active-year catalog to screen whether the M1-M3 catalog behavior is more consistent with independent ruptures, phase-separated activation, compact/swarm-like compound activation, repeated shallow local activation, or background/window effects.

This is a catalog-level screening task. Do not infer triggering, stress transfer, fluid migration, or slow slip from catalog statistics alone.

Data folder:
"<CASE_ROOT>/data"

Inputs:
- relocated/filtered catalog:
  data/Snet_catalog_relocate_250601_260501.csv
- mainshock table:
  catalog/main_earthquake.csv

Context files:
- source_mechanism/Snet_mecha.csv
- stations/station.sta

Current catalog findings to use as working context:
- The pre-M1 background baseline should stop before the M1-related lead-in. Use catalog start to M1-14d as the conservative baseline and catalog start to M1-7d as sensitivity.
- M1-M3 activity is much stronger than the conservative pre-M1 baseline.
- The M1-related lead-in and immediate phase from M1-14d to M1+21d contains most M3+/M4+/M5+ activity in the full M1-to-M3 interval.
- The M1-M3 middle phase from M1+21d to M3-35d remains active and elevated above baseline, but is much weaker than the M1-related phase.
- The final pre-M3 local activation phase from M3-35d to M3 remains clear and is stable under M2-aware comparison.
- Spatial-depth screening favors mixed M1-centered and M3-centered local overlap / separated local bursts rather than robust M1-to-M3 migration.
- M1-centered, M3-centered, along-axis, and off-axis/off-corridor contributions must be quantified separately; do not assume any spatial mechanism without subset evidence.
- The catalog-level depth pattern is shallow-dominated: most M3+ to M5+ events lie in 0-30 km, with median depths near 12-14 km, but depth-sensitive interpretations still require quality control and relocation uncertainty checks.
- M2-aware filtering has limited influence on the main interpretation, although some middle-phase counts may be modestly affected.
- These are catalog-level observations, not evidence of physical triggering.

Spatial and temporal framework:
Use a neutral M1-M3 local-zone framework. Treat these labels as geometric bookkeeping around the M1 and M3 locations, not as evidence for a corridor-controlled process:
- M1-M3 combined local zone: events within 60 km of either M1 or M3
- M1-centered and M3-centered core zones: events within 30 km of M1 or M3
- M1-centered and M3-centered extended zones: events within 60 km of M1 or M3
- along-axis/corridor-like subset: projection between M1 and M3 with perpendicular distance <=20-30 km; use this as a geometric comparison subset, not as a preferred mechanism
- M2-related events: flag but do not remove by default

For b-value interpretation, prioritize sliding-event-window analysis over single b-value estimates for manually defined phase windows. The primary b-value product should be a smooth time-evolution curve computed in statistically stable spatial domains.

Primary b-value design:
- Use the M1-M3 combined local zone as the primary spatial domain.
- Use fixed-count sliding event windows. Use 500 events as the primary window size for the M1-M3 combined local zone where data allow.
- For smaller spatial subsets, use the largest statistically stable fixed-count window feasible and report the chosen window size.
- Slide by 100 events as the primary step, and use 200-event steps as a robustness/smoothing sensitivity.
- Assign each sliding-window b-value to the median event time of that window.
- For each window, estimate Mc, b-value, uncertainty, fitting range, and reliability.
- Exclude or flag windows where Mc stability, event count above Mc, or fitting range are inadequate.
- Overlay the predefined phase boundaries on the sliding b-value time series rather than computing only one b-value per phase.

Secondary b-value diagnostics:
- Repeat sliding-window analysis for M1-centered and M3-centered extended zones if sample size supports it.
- Treat M1-centered and M3-centered core zones, along-axis/corridor-like 20/30 km subsets, off-axis/off-corridor subsets, short pre-M3 windows, and burst-level b-values as exploratory unless sample size, Mc stability, and fitting range are adequate.
- Phase-window b-values may be reported as summary descriptors, but they must not replace the sliding-window time-evolution analysis.

Analyze these subsets where data allow:
- pre-M1 baseline to M1-14d, with M1-7d sensitivity
- M1-related dominated phase: M1-14d to M1+21d
- optional M1-related sensitivity windows: M1-7d to M1+14d and M1-14d to M1+28d
- M1-M3 middle phase: M1+21d to M3-35d
- pre-M3 local activation phase: M3-35d to M3
- optional pre-M3 sensitivity windows: M3-42d to M3 and M3-28d to M3
- post-M3 context only if needed, kept separate from pre-M3 interpretation
- major rate-defined bursts from the current catalog, grouped by M1-centered, M3-centered, mixed, or off-corridor category rather than assumed M1-side/M3-side migration
- full M1-to-M3 interval

Main tasks:
1. Sliding-window b-value and completeness
Compute Mc and b-value through time using fixed-count sliding event windows. The primary analysis should use 500-event windows with 100-event steps in the M1-M3 combined local zone, with 200-event steps and M1/M3-centered extended-zone subsets as sensitivity checks where data allow. Report each window's median time, start/end time, event count, Mc, b-value, uncertainty, fitting range, and reliability. Use a graded reliability interpretation rather than a strict usable/unusable split: robust, usable with caution, exploratory, or not interpretable.

2. Phase-aware b-value interpretation
Overlay phase boundaries on the sliding b-value curve and summarize whether b-value levels or trends change across the pre-M1 baseline, M1-related dominated phase, middle phase, and pre-M3 phase. Do not rely on one b-value per phase as the primary evidence. If phase-level aggregate b-values are computed, label them as secondary summaries and compare them against the sliding-window curve.

3. Spatial b-value comparison
Compare b-value behavior across M1-centered local events, M3-centered local events, along-axis/corridor-like events, off-axis/off-corridor local events, and M1- or M3-centered extended zones only where sample size and Mc stability are adequate. Clearly state whether differences are robust, usable with caution, exploratory, or not interpretable.

4. Magnitude hierarchy
For each key subset and burst, compute largest, second-largest, and third-largest magnitudes, magnitude gaps, M4+/M5+/M6+ counts, and companion events within 0.5 and 1.0 magnitude units of the largest event.

5. Moment-release proxy
Use a magnitude-based moment proxy to compare cumulative moment release, burst-level moment release, top-event contribution, and moment release by M1-centered, M3-centered, along-axis/corridor-like, and off-axis/off-corridor categories.

6. Catalog mechanism-evidence matrix
Using b-value, magnitude hierarchy, moment release, and current spatial-depth screening results, evaluate catalog-level support for:
- independent local ruptures
- phase-separated activation between M1 and M3
- compact/swarm-like compound activation
- M1/M3-centered repeated shallow activation
- stepwise or along-axis activation candidate
- stress-interaction candidate
- fluid/diffusion-like candidate
- slow-slip-related candidate
- background/window artifact

For each hypothesis, report supporting evidence, contradicting evidence, missing evidence, confidence level, and required physical follow-up.
If focal-mechanism information is used, first audit its coverage by phase, magnitude threshold, and spatial class. If coverage is sparse or biased, report mechanism consistency as unavailable or exploratory rather than forcing a mechanism conclusion.

Robustness:
Prioritize checks that directly affect the main conclusions; do not exhaustively expand every combination of subset, threshold, window, and corridor width.
Check whether conclusions change under raw vs M2-aware event sets, 500-event versus alternative window sizes where feasible, 100-event versus 200-event sliding steps, M3+/M4+/M5+ subsets, 30 km core versus 60 km extended M1- or M3-centered definitions, 20 km vs 30 km along-axis/corridor-like width, primary versus sensitivity temporal windows, reasonable alternative Mc choices, and alternative burst-window definitions if burst detection is ambiguous.

Figures:
Generate a compact set of high-quality diagnostic figures, not exhaustive plots:
- magnitude-frequency distributions with Mc and b-value annotations
- b-value spatial comparison
- sliding-window b-value temporal evolution with phase boundaries overlaid
- sliding-window Mc and reliability timeline
- cumulative moment-release proxy curve
- burst-level moment-release and magnitude-hierarchy summary
- catalog mechanism-evidence matrix

Final report:
Provide a concise report answering:
- Are sliding-window b-value estimates reliable enough to interpret?
- Does b-value vary meaningfully through time, and do changes align with the predefined phase windows?
- Are phase-level aggregate b-values consistent with the sliding-window b-value evolution, or are they misleading because of window aggregation?
- Is M1-M3 single-event dominated, compound/swarm-like, phase-distributed, or burst-distributed in moment release?
- Are M1-related, middle-phase, pre-M3, and post-M3 context events similar or different in magnitude hierarchy and moment proxy?
- Do M1-centered and M3-centered local subsets differ from along-axis/corridor-like subsets, or are the along-axis samples too small for interpretation?
- Which mechanism hypotheses are supported, weakened, or unresolved?
- Which follow-up analyses should be prioritized next?

Important:
Do not infer physical causality from b-value, moment release, or catalog geometry alone.
High or low b-value is only a screening clue, not a mechanism.
Separate catalog-level statistical support from physical mechanism interpretation.
Do not describe the catalog as corridor-confined, M1- or M3-zone-confined, or migrating unless the statistics support that after phase separation.
Treat stress, fluid, and slow-slip interpretations as low-confidence candidates unless independent physical data are available.

The Mc and b-value can be estimated using the `seismostats` package.
</user_request>

## Planned Workflow
<experiment_plan>
# Goal
Screen whether the relocated/filtered Aomori M1-M3 local earthquake catalog is more consistent, at catalog level, with independent ruptures, phase-separated activation, compact/swarm-like compound activation, repeated shallow local activation, or background/window effects by combining sliding-window completeness/b-value analysis, magnitude hierarchy, and magnitude-based moment-release patterns, while explicitly avoiding causal physical inference from catalog statistics alone.

## Planning Assumptions
- Observation data are sufficient and must be used as primary input: `data/Snet_catalog_relocate_250601_260501.csv` and `catalog/main_earthquake.csv`; `source_mechanism/Snet_mecha.csv` and `stations/station.sta` are context/audit inputs only.
- `catalog/main_earthquake.csv` is the authoritative source for M1, M2, and M3 origin times, hypocenters, and magnitudes used to construct all phase boundaries and geometric subset anchors.
- The relocated catalog CSV is a five-column CSV with an explicit header; column roles must be verified from the named fields before analysis.
- SeismoStats package contract relevant to this task:
  - Magnitudes should be binned before Mc/b-value estimation using an explicit `delta_m`.
  - Mc methods available: `estimate_mc_maxc`, `estimate_mc_ks`, and `estimate_mc_b_stability`.
  - `estimate_mc_maxc` requires `fmd_bin`; `estimate_mc_ks` uses `delta_m` and a configurable `p_value_pass` and is slower/more conservative.
  - Calling Mc estimators overwrites catalog `mc`; each window/subset must therefore store explicit Mc estimates by method and the adopted Mc rather than relying on mutable catalog state.
  - `estimate_b` / `Catalog.estimate_b()` uses the classical estimator by default (`ClassicBValueEstimator`) and excludes magnitudes below Mc automatically.
- No SeismoStats package contract provides a built-in sliding-window or reliability-class workflow for this exact task; window construction, Mc-selection logic, and reliability grading must therefore be implemented explicitly and written to outputs.
- Magnitude discretization must not be inferred solely from decimal display; choose `delta_m` from documented metadata if available, otherwise determine an operational bin width from observed magnitude quantization and record that choice for verification.
- Sliding-window b-value evolution is the primary b-value product. Aggregate b-values for manually defined phases are secondary descriptors only.
- Reliability must be graded per window/subset as robust, usable with caution, exploratory, or not interpretable using Mc agreement/stability, number of events above Mc, fitted magnitude span, and estimator convergence/stability under reasonable Mc alternatives.
- M2-related events must be flagged but not removed by default; raw and M2-aware views are targeted robustness checks.
- Moment-release analysis is a magnitude-based proxy for internal comparison only and must not be treated as direct source-physics evidence.
- Focal-mechanism use requires a coverage audit by phase, magnitude threshold, and spatial class first; if coverage is sparse or biased, mechanism consistency must be reported as unavailable or exploratory.
- Use one primary cohesive task script to run the full catalog workflow; use one optional secondary audit script only if mechanism coverage matching/join validation is materially reusable.

## Analysis Plan
### Task 1 — Build the validated master catalog and analysis framework
- Task description:
  - Load the relocated catalog and reference tables, verify schema, standardize fields, and construct all temporal and geometric labels required for downstream statistics.
- Required data sources:
  - `data/Snet_catalog_relocate_250601_260501.csv`
  - `catalog/main_earthquake.csv`
  - `source_mechanism/Snet_mecha.csv`
  - `stations/station.sta`
- Parameter selection strategy:
  - Verify actual catalog columns by inspection and assign standardized fields for:
    - event identifier if present
    - origin time
    - latitude
    - longitude
    - depth
    - magnitude
  - Parse origin times consistently and sort the catalog chronologically.
  - Construct phase boundaries exactly from the user request and mainshock times:
    - baseline primary: catalog start to M1-14 d
    - baseline sensitivity: catalog start to M1-7 d
    - M1-related primary: M1-14 d to M1+21 d
    - M1-related sensitivities: M1-7 d to M1+14 d; M1-14 d to M1+28 d
    - middle phase: M1+21 d to M3-35 d
    - pre-M3 primary: M3-35 d to M3
    - pre-M3 sensitivities: M3-42 d to M3; M3-28 d to M3
    - post-M3 context only if needed and kept separate
    - full M1-to-M3 interval
  - Compute event-to-M1, event-to-M2, and event-to-M3 horizontal distances with one consistent geodesic method.
  - Define neutral geometric subsets:
    - combined local zone: within 60 km of either M1 or M3
    - M1 core and M3 core: within 30 km of M1 or M3
    - M1 extended and M3 extended: within 60 km of M1 or M3
    - overlap class: within both M1 and M3 extended zones
    - along-axis subsets: event projection within the M1-M3 segment and perpendicular distance <=20 km and <=30 km
    - off-axis subsets: combined local zone excluding the corresponding along-axis subset
  - Define M2-related flags using distance to M2 and time proximity to the M2 phase, preserving both raw and M2-aware masks.
  - Audit `Snet_mecha.csv` joinability:
    - direct event-id match if present
    - otherwise strict time and hypocenter proximity matching with logged tolerances and unmatched fractions
  - Inspect `station.sta` only for network-context metadata if the schema is clear.
  - Determine candidate `delta_m` from metadata if present; otherwise evaluate magnitude quantization pattern in the relocated catalog and record the chosen operational `delta_m`.
- Constraints:
  - Do not assume migration, corridor confinement, or M1/M3-centered process behavior from geometry alone.
  - Do not remove M2-related events from the primary catalog.
  - Do not use focal mechanisms in interpretation before coverage audit.
  - Depth context may be summarized, but depth-sensitive interpretation must remain qualified by catalog-level uncertainty limits.
- Key outputs:
  - `validated_catalog.csv`
  - `phase_boundaries.csv`
  - `spatial_membership.csv`
  - `catalog_validation_summary.csv`
  - `mechanism_join_audit.csv`
  - `subset_count_summary.csv`

### Task 2 — Primary sliding-window Mc and b-value analysis
- Task description:
  - Compute the primary time-evolving Mc and b-value product in the M1-M3 combined local zone using fixed-count sliding windows, then extend the same logic to larger secondary spatial subsets where sample size is adequate.
- Required data sources:
  - Outputs from Task 1
- Parameter selection strategy:
  - Primary domain: M1-M3 combined local zone.
  - Primary sliding configuration:
    - window size: 500 events
    - step: 100 events
    - sensitivity step: 200 events
    - assign each window to the median event time
  - Secondary domains if sample size supports stable windows:
    - M1 extended 60 km
    - M3 extended 60 km
  - Exploratory domains only if feasible:
    - M1 core 30 km
    - M3 core 30 km
    - along-axis 20 km
    - along-axis 30 km
    - off-axis relative to each corridor width
  - For each window:
    - bin magnitudes using the selected `delta_m`
    - estimate Mc by MAXC using `fmd_bin = delta_m`
    - estimate Mc by KS using the same `delta_m`; use default `p_value_pass` unless task-specific evidence justifies a sensitivity check
    - estimate Mc by b-stability where event counts permit
    - store all method-specific Mc values explicitly
    - adopt a reported Mc using a predefined rule based on method agreement, plausibility, and stability
    - estimate classical b-value at the adopted Mc using SeismoStats default/classical estimator
    - record uncertainty from the estimator output or the package-consistent classical uncertainty calculation
    - record total count, count above Mc, fitted minimum magnitude, maximum fitted magnitude, and fitted magnitude span
    - record failure/flag reasons when Mc or b-value estimation is unstable or unsupported
  - Reliability grading:
    - robust: Mc methods broadly consistent, count above Mc adequate, fitted span adequate, and result stable under reasonable Mc alternatives
    - usable with caution: one criterion weak but interpretation still directionally stable
    - exploratory: sparse counts, weak span, or unstable Mc agreement limit interpretation
    - not interpretable: inadequate count above Mc, failed Mc convergence, or no meaningful fitted range
  - Window-size selection for smaller subsets:
    - use the largest feasible fixed-count window that still yields several windows across the target interval
    - record the chosen window size per subset and the reason for any deviation from 500
- Constraints:
  - Sliding-window evolution is the primary b-value evidence.
  - Windows with poor completeness support must be flagged or excluded from interpretation, not treated as equivalent to robust windows.
  - Do not replace the primary classical product with positive-method outputs; if short-term incompleteness is suspected around large events, use positive-method checks only as sensitivity diagnostics.
- Key outputs:
  - `sliding_bvalue_combined_local.csv`
  - `sliding_bvalue_M1_extended.csv`
  - `sliding_bvalue_M3_extended.csv`
  - `sliding_bvalue_exploratory_subsets.csv`
  - `window_reliability_summary.csv`
  - `window_size_selection.csv`

### Task 3 — Phase-aware interpretation and aggregate b-value cross-checks
- Task description:
  - Overlay the predefined phase boundaries on the sliding-window results and test whether aggregate phase-window b-values are consistent with, or misleading relative to, the sliding-window time evolution.
- Required data sources:
  - Outputs from Task 2
  - Phase definitions from Task 1
- Parameter selection strategy:
  - For each major phase:
    - baseline
    - M1-related dominated phase
    - middle phase
    - pre-M3 local activation phase
    - post-M3 context if used
  - Summarize:
    - median and interquartile range of interpretable sliding-window b-values
    - reliability-class proportions
    - Mc stability within phase
    - whether transitions appear step-like, gradual, or unresolved
  - Compute secondary aggregate Mc and b-value summaries for:
    - baseline primary and sensitivity
    - M1-related primary and sensitivity windows
    - middle phase
    - pre-M3 primary and sensitivities
    - full M1-to-M3 interval
  - Compare each aggregate phase estimate against the corresponding sliding-window distribution occupying the same time range.
- Constraints:
  - Aggregate phase b-values must be labeled secondary summaries.
  - Do not over-interpret isolated windows near boundaries or aggregate windows with inadequate Mc stability.
- Key outputs:
  - `phase_sliding_bvalue_summary.csv`
  - `phase_aggregate_bvalue_summary.csv`
  - `phase_transition_assessment.csv`

### Task 4 — Spatial comparison of b-value behavior
- Task description:
  - Compare b-value behavior across M1-centered, M3-centered, along-axis, and off-axis local subsets only where sample size and completeness stability are adequate.
- Required data sources:
  - Outputs from Tasks 1–3
- Parameter selection strategy:
  - Priority comparison subsets:
    - combined local zone
    - M1 extended
    - M3 extended
    - along-axis 30 km
    - along-axis 20 km
    - off-axis complements
  - Secondary/exploratory if feasible:
    - M1 core
    - M3 core
    - overlap class
  - For each subset:
    - use the same `delta_m` and Mc workflow as the primary analysis
    - choose a fixed-count window size based on available counts and required temporal coverage
    - summarize analyzable-window count, reliability distribution, central b-value tendency, and overlap with major phases
  - Include raw versus M2-aware comparisons for subsets whose counts are moderately affected by M2.
- Constraints:
  - Do not claim robust spatial contrasts when windows do not overlap in time or when one subset is mostly exploratory.
  - Along-axis subsets are geometric comparison groups only.
- Key outputs:
  - `spatial_bvalue_comparison.csv`
  - `spatial_reliability_audit.csv`
  - `spatial_phase_overlap_summary.csv`

### Task 5 — Magnitude hierarchy analysis by phase, subset, and burst
- Task description:
  - Quantify whether the catalog is dominated by one event, a few large companions, or many moderate events across key temporal phases, spatial subsets, and major bursts.
- Required data sources:
  - Validated catalog and subset labels from Task 1
- Parameter selection strategy:
  - For each key phase, full M1-to-M3 interval, interpretable spatial subset, and major burst:
    - largest magnitude
    - second-largest magnitude
    - third-largest magnitude
    - first-second and second-third magnitude gaps
    - counts of M4+, M5+, M6+
    - counts within 0.5 and 1.0 magnitude units of the largest event
    - top-1 and top-3 contribution to event counts above selected thresholds
  - Burst definitions:
    - if a validated burst table already exists in the data folder, use it
    - otherwise detect major bursts from the combined-local-zone rate curve with a transparent, reproducible rule and classify them as M1-centered, M3-centered, mixed, or off-axis/off-corridor by event composition
- Constraints:
  - Burst-level outputs are secondary if burst segmentation is ambiguous.
  - Do not translate dominance patterns into causal triggering statements.
- Key outputs:
  - `magnitude_hierarchy_phase_subset.csv`
  - `magnitude_hierarchy_bursts.csv`
  - `burst_classification_summary.csv`

### Task 6 — Magnitude-based moment-release proxy analysis
- Task description:
  - Use a consistent magnitude-to-moment proxy to compare cumulative release, burst contributions, and dominance structure across temporal phases and spatial classes.
- Required data sources:
  - Validated catalog and subset labels from Task 1
- Parameter selection strategy:
  - Convert magnitude to a scalar moment proxy using one standard log-linear relation applied consistently across all analyses.
  - Compute:
    - cumulative moment proxy through time for the combined local zone
    - cumulative curves for M1 extended, M3 extended, along-axis, and off-axis categories
    - phase totals and shares
    - burst totals and shares
    - top-event contribution fractions
    - concentration metrics from top 1, top 3, and top decile events
  - Keep post-M3 context separate from pre-M3 interpretation.
  - Compare raw and M2-aware totals where relevant to middle-phase and full-interval interpretation.
- Constraints:
  - Treat moment proxy as comparative only.
  - Do not infer rupture physics or interaction physics from moment concentration patterns alone.
- Key outputs:
  - `moment_proxy_event_table.csv`
  - `cumulative_moment_proxy_by_subset.csv`
  - `phase_moment_proxy_summary.csv`
  - `burst_moment_proxy_summary.csv`
  - `moment_dominance_metrics.csv`

### Task 7 — Mechanism coverage audit and catalog evidence matrix
- Task description:
  - Audit focal-mechanism coverage first, then synthesize the catalog-level evidence from b-value, magnitude hierarchy, moment proxy, and current spatial-depth screening into the requested hypothesis matrix.
- Required data sources:
  - `source_mechanism/Snet_mecha.csv`
  - Outputs from Tasks 1–6
- Parameter selection strategy:
  - Coverage audit dimensions:
    - phase
    - magnitude threshold
    - spatial class
    - optional depth class if coverage permits
  - Quantify:
    - matched fraction of events
    - matched fraction among larger events
    - missingness in mechanism fields
    - representativeness or bias of available mechanism information
  - Build the hypothesis matrix for:
    - independent local ruptures
    - phase-separated activation between M1 and M3
    - compact/swarm-like compound activation
    - M1/M3-centered repeated shallow activation
    - stepwise or along-axis activation candidate
    - stress-interaction candidate
    - fluid/diffusion-like candidate
    - slow-slip-related candidate
    - background/window artifact
  - For each hypothesis report:
    - supporting catalog evidence
    - contradicting catalog evidence
    - missing evidence
    - confidence level
    - required physical follow-up
- Constraints:
  - Stress, fluid, and slow-slip candidates must remain low-confidence screening labels without independent physical data.
  - Sparse or biased focal-mechanism coverage must be labeled unavailable or exploratory.
  - Separate catalog-statistical support from physical interpretation in every hypothesis entry.
- Key outputs:
  - `mechanism_coverage_audit.csv`
  - `catalog_mechanism_evidence_matrix.csv`

### Task 8 — Targeted robustness checks for conclusion stability
- Task description:
  - Test only the user-prioritized sensitivities that could change the main interpretation of b-value reliability, temporal evolution, spatial contrasts, magnitude hierarchy, and moment dominance.
- Required data sources:
  - Outputs from Tasks 2–7
- Parameter selection strategy:
  - Evaluate conclusion stability under:
    - raw versus M2-aware event sets
    - 500-event windows versus alternative feasible window sizes in secondary subsets
    - 100-event versus 200-event sliding steps
    - M1/M3 30 km core versus 60 km extended subsets
    - along-axis width 20 km versus 30 km
    - baseline end at M1-14 d versus M1-7 d
    - pre-M3 start at M3-35 d versus M3-42 d and M3-28 d
    - reasonable alternative adopted Mc choices when methods disagree
    - M3+/M4+/M5+ descriptive hierarchy/moment summaries
    - alternative burst definitions only if burst identification is ambiguous
  - Summarize whether each sensitivity changes:
    - sliding-window interpretability
    - phase-aligned b-value variation
    - spatial-contrast interpretation
    - magnitude-hierarchy classification
    - moment-dominance classification
    - hypothesis-matrix ranking
- Constraints:
  - Do not exhaustively cross all parameter combinations.
  - Keep sensitivities affecting only exploratory subsets secondary.
- Key outputs:
  - `robustness_change_log.csv`
  - `conclusion_stability_matrix.csv`

### Primary task script organization
- Task description:
  - Use one primary analysis script to execute Tasks 1–8 end-to-end, including validation, subset construction, sliding-window computation, secondary summaries, hierarchy/moment metrics, robustness checks, immediate output validation, and failure evidence collection.
  - Use one optional secondary audit script only if mechanism matching/coverage validation is kept separate for reuse.
- Required data sources:
  - All files listed above
- Parameter selection strategy:
  - Primary execution flow:
    - ingest and validate inputs
    - define phases and subsets
    - compute sliding Mc/b-value products
    - compute phase and spatial summaries
    - compute magnitude hierarchy and moment proxy
    - audit focal-mechanism coverage
    - run targeted robustness checks
    - write all tables and figure-ready products
    - verify required outputs are non-empty for the combined local zone and key summaries
  - Save compact machine-readable outputs with the filenames listed in prior tasks.
- Constraints:
  - Successful execution requires non-empty sliding-window results for the combined local zone and non-empty phase/spatial summary tables when expected.
  - Diagnostic-only, schema-only, or partial outputs do not count as successful completion.
- Key outputs:
  - Complete machine-readable analysis package for direct report synthesis

### Diagnostic figures
- Task description:
  - Produce a compact figure set tied directly to the user’s core questions.
- Required data sources:
  - Outputs from Tasks 2–8
- Parameter selection strategy:
  - Required figures:
    - magnitude-frequency distributions with Mc and b-value annotations
    - b-value spatial comparison
    - sliding-window b-value temporal evolution with phase boundaries
    - sliding-window Mc and reliability timeline
    - cumulative moment-release proxy curve
    - burst-level moment-release and magnitude-hierarchy summary
    - catalog mechanism-evidence matrix
  - Encode reliability so robust, cautious, exploratory, and uninterpretable results are visually distinct.
  - Include only subsets that are interpretable or necessary to justify why they are not.
- Constraints:
  - Keep the figure suite compact.
  - Do not add exhaustive sensitivity plot grids.
- Key outputs:
  - Figure-ready tables for each requested diagnostic figure

### Final report synthesis targets
- Task description:
  - Ensure the outputs directly answer the requested final questions.
- Required data sources:
  - Outputs from Tasks 2–8
- Parameter selection strategy:
  - Prepare machine-readable summary fields for:
    - whether sliding-window b-value estimates are reliable enough to interpret
    - whether b-value varies meaningfully through time and aligns with predefined phases
    - whether phase-level aggregate b-values are consistent with or misleading relative to the sliding-window evolution
    - whether moment release is single-event dominated, compound/swarm-like, phase-distributed, or burst-distributed
    - whether M1-related, middle-phase, pre-M3, and post-M3 context differ in hierarchy and moment proxy
    - whether M1-centered and M3-centered subsets differ from along-axis subsets, or whether along-axis samples are too small for interpretation
    - which mechanism hypotheses are supported, weakened, or unresolved
    - which follow-up analyses should be prioritized next
- Constraints:
  - Final answers must explicitly separate catalog-level statistical support from physical mechanism interpretation.
- Key outputs:
  - `final_answer_table.csv`
  - concise final narrative report aligned to the user’s required questions
</experiment_plan>

## Implementation Trace
- Task: 01_catalog_screening_analysis
  Description: Build the validated Aomori master catalog and run the full catalog-level screening workflow for sliding-window completeness and b-value, spatial comparisons, magnitude hierarchy, moment proxy, robustness checks, figures, and machine-readable summaries.
  Ancestors: none
  Handoff JSON: <CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/log/coding_progress/task_handoff/01_catalog_screening_analysis.json
  Output directory: <CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/01_catalog_screening_analysis
  Analysis file: <CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/analysis/01_catalog_screening_analysis.md
- Task: 02_mechanism_coverage_audit
  Description: Perform a reusable standalone audit of focal-mechanism matching and representativeness by phase, magnitude level, and spatial class.
  Ancestors: 01_catalog_screening_analysis
  Handoff JSON: <CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/log/coding_progress/task_handoff/02_mechanism_coverage_audit.json
  Output directory: <CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/02_mechanism_coverage_audit
  Analysis file: <CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/analysis/02_mechanism_coverage_audit.md

## Result Evidence Index
Use handoff JSON files as compact indexes to important outputs. Use per-task analyses for scientific interpretation. Inspect raw outputs only when the handoff and analysis are insufficient.
<task_evidence task="01_catalog_screening_analysis">
Handoff JSON: <CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/log/coding_progress/task_handoff/01_catalog_screening_analysis.json
{
  "meta": {
    "schema_version": 2,
    "type": "coding_task_handoff",
    "task": "01_catalog_screening_analysis",
    "generated_at": "2026-05-25T09:08:24.825304+00:00"
  },
  "status": {
    "state": "success",
    "stage": "analysis_done",
    "elapsed_sec": 1128.375,
    "timing": {
      "total_sec": 1128.375,
      "coding_agent_sec": 292.827,
      "code_review_sec": 49.322,
      "preflight_sec": 0.559,
      "script_execution_sec": 474.844,
      "result_check_sec": 84.96,
      "task_analysis_sec": 224.691
    },
    "quality_flags": [
      "task_status:success",
      "outputs_truncated"
    ]
  },
  "paths": {
    "root": "<CASE_ROOT>/run/03_1C_mechanism_screening",
    "script": "<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/scripts/01_catalog_screening_analysis.py",
    "output_dir": "<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/01_catalog_screening_analysis",
    "analysis": "<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/analysis/01_catalog_screening_analysis.md",
    "log": "<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/log/task/01_catalog_screening_analysis/log_0.txt"
  },
  "outputs": {
    "primary": [
      {
        "path": "aggregate_vs_sliding_consistency.csv",
        "absolute_path": "<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/01_catalog_screening_analysis/aggregate_vs_sliding_consistency.csv",
        "kind": "machine_readable"
      },
      {
        "path": "burst_classification_summary.csv",
        "absolute_path": "<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/01_catalog_screening_analysis/burst_classification_summary.csv",
        "kind": "machine_readable"
      },
      {
        "path": "burst_moment_proxy_summary.csv",
        "absolute_path": "<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/01_catalog_screening_analysis/burst_moment_proxy_summary.csv",
        "kind": "machine_readable"
      },
      {
        "path": "catalog_mechanism_evidence_matrix.csv",
        "absolute_path": "<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/01_catalog_screening_analysis/catalog_mechanism_evidence_matrix.csv",
        "kind": "machine_readable"
      },
      {
        "path": "catalog_validation_summary.csv",
        "absolute_path": "<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/01_catalog_screening_analysis/catalog_validation_summary.csv",
        "kind": "machine_readable"
      },
      {
        "path": "conclusion_stability_matrix.csv",
        "absolute_path": "<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/01_catalog_screening_analysis/conclusion_stability_matrix.csv",
        "kind": "machine_readable"
      },
      {
        "path": "cumulative_moment_proxy_by_subset.csv",
        "absolute_path": "<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/01_catalog_screening_analysis/cumulative_moment_proxy_by_subset.csv",
        "kind": "machine_readable"
      },
      {
        "path": "final_answer_table.csv",
        "absolute_path": "<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/01_catalog_screening_analysis/final_answer_table.csv",
        "kind": "machine_readable"
      }
    ],
    "all": [
      "aggregate_vs_sliding_consistency.csv",
      "burst_classification_summary.csv",
      "burst_moment_proxy_summary.csv",
      "catalog_mechanism_evidence_matrix.csv",
      "catalog_validation_summary.csv",
      "conclusion_stability_matrix.csv",
      "cumulative_moment_proxy_by_subset.csv",
      "figure_burst_moment_hierarchy_summary.png",
      "figure_bvalue_spatial_comparison.png",
      "figure_catalog_mechanism_evidence_matrix.png",
      "figure_cumulative_moment_proxy.png",
      "figure_magnitude_frequency_annotations.png",
      "figure_sliding_bvalue_temporal_evolution.png",
      "figure_sliding_mc_reliability_timeline.png",
      "final_answer_table.csv",
      "magnitude_hierarchy_bursts.csv",
      "magnitude_hierarchy_phase_subset.csv",
      "mechanism_coverage_audit.csv",
      "mechanism_join_audit.csv",
      "moment_dominance_metrics.csv",
      "moment_proxy_event_table.csv",
      "phase_aggregate_bvalue_summary.csv",
      "phase_boundaries.csv",
      "phase_moment_proxy_summary.csv",
      "phase_sliding_bvalue_summary.csv",
      "phase_transition_assessment.csv",
      "robustness_change_log.csv",
      "sliding_bvalue_M1_extended.csv",
      "sliding_bvalue_M3_extended.csv",
      "sliding_bvalue_combined_local.csv",
      "sliding_bvalue_exploratory_subsets.csv",
      "spatial_bvalue_comparison.csv",
      "spatial_membership.csv",
      "spatial_phase_overlap_summary.csv",
      "spatial_reliability_audit.csv",
      "subset_count_summary.csv",
      "validated_catalog.csv",
      "window_reliability_summary.csv",
      "window_size_selection.csv"
    ],
    "truncated": true
  },
  "notes": {
    "purpose": "Build the validated Aomori master catalog and run the full catalog-level screening workflow for sliding-window completeness and b-value, spatial comparisons, magnitude hierarchy, moment proxy, robustness checks, figures, and machine-readable summaries.",
    "result": "Build the validated Aomori master catalog and run the full catalog-level screening workflow for sliding-window completeness and b-value, spatial comparisons, magnitude hierarchy, m...[truncated] Status=success; outputs=39 discovered; primary=8.",
    "warnings": [],
    "assumptions": [],
    "limitations": []
  }
}
</task_evidence>

<task_evidence task="02_mechanism_coverage_audit">
Handoff JSON: <CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/log/coding_progress/task_handoff/02_mechanism_coverage_audit.json
{
  "meta": {
    "schema_version": 2,
    "type": "coding_task_handoff",
    "task": "02_mechanism_coverage_audit",
    "generated_at": "2026-05-25T09:08:24.833419+00:00"
  },
  "status": {
    "state": "success",
    "stage": "analysis_done",
    "elapsed_sec": 521.581,
    "timing": {
      "total_sec": 521.581,
      "coding_agent_sec": 178.478,
      "code_review_sec": 43.236,
      "preflight_sec": 0.739,
      "script_execution_sec": 110.308,
      "result_check_sec": 54.453,
      "task_analysis_sec": 131.633
    },
    "quality_flags": [
      "task_status:success"
    ]
  },
  "paths": {
    "root": "<CASE_ROOT>/run/03_1C_mechanism_screening",
    "script": "<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/scripts/02_mechanism_coverage_audit.py",
    "output_dir": "<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/02_mechanism_coverage_audit",
    "analysis": "<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/analysis/02_mechanism_coverage_audit.md",
    "log": "<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/log/task/02_mechanism_coverage_audit/log_1.txt"
  },
  "outputs": {
    "primary": [
      {
        "path": "mechanism_coverage_audit.csv",
        "absolute_path": "<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/02_mechanism_coverage_audit/mechanism_coverage_audit.csv",
        "kind": "machine_readable"
      },
      {
        "path": "mechanism_coverage_by_magnitude_threshold.csv",
        "absolute_path": "<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/02_mechanism_coverage_audit/mechanism_coverage_by_magnitude_threshold.csv",
        "kind": "machine_readable"
      },
      {
        "path": "mechanism_coverage_by_phase.csv",
        "absolute_path": "<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/02_mechanism_coverage_audit/mechanism_coverage_by_phase.csv",
        "kind": "machine_readable"
      },
      {
        "path": "mechanism_coverage_by_phase_and_magnitude.csv",
        "absolute_path": "<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/02_mechanism_coverage_audit/mechanism_coverage_by_phase_and_magnitude.csv",
        "kind": "machine_readable"
      },
      {
        "path": "mechanism_coverage_by_phase_and_spatial_class.csv",
        "absolute_path": "<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/02_mechanism_coverage_audit/mechanism_coverage_by_phase_and_spatial_class.csv",
        "kind": "machine_readable"
      },
      {
        "path": "mechanism_coverage_by_spatial_class.csv",
        "absolute_path": "<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/02_mechanism_coverage_audit/mechanism_coverage_by_spatial_class.csv",
        "kind": "machine_readable"
      },
      {
        "path": "mechanism_field_completeness.csv",
        "absolute_path": "<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/02_mechanism_coverage_audit/mechanism_field_completeness.csv",
        "kind": "machine_readable"
      },
      {
        "path": "mechanism_match_pairs_basic.csv",
        "absolute_path": "<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/02_mechanism_coverage_audit/mechanism_match_pairs_basic.csv",
        "kind": "machine_readable"
      }
    ],
    "all": [
      "mechanism_coverage_audit.csv",
      "mechanism_coverage_by_magnitude_threshold.csv",
      "mechanism_coverage_by_phase.csv",
      "mechanism_coverage_by_phase_and_magnitude.csv",
      "mechanism_coverage_by_phase_and_spatial_class.csv",
      "mechanism_coverage_by_spatial_class.csv",
      "mechanism_coverage_overview.png",
      "mechanism_coverage_summary.txt",
      "mechanism_field_completeness.csv",
      "mechanism_field_completeness.png",
      "mechanism_match_pairs_basic.csv",
      "mechanism_match_pairs_with_context.csv",
      "mechanism_matching_tolerance_grid.csv",
      "mechanism_representativeness_bias.png",
      "mechanism_representativeness_tests.csv"
    ],
    "truncated": false
  },
  "notes": {
    "purpose": "Perform a reusable standalone audit of focal-mechanism matching and representativeness by phase, magnitude level, and spatial class.",
    "result": "Perform a reusable standalone audit of focal-mechanism matching and representativeness by phase, magnitude level, and spatial class. Status=success; outputs=15 discovered; primary=8.",
    "warnings": [],
    "assumptions": [],
    "limitations": []
  }
}
</task_evidence>


## Output Directory Structure Preview
<output_directory_structure>
<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs
├── 01_catalog_screening_analysis
│   ├── aggregate_vs_sliding_consistency.csv
│   ├── burst_classification_summary.csv
│   ├── burst_moment_proxy_summary.csv
│   ├── catalog_mechanism_evidence_matrix.csv
│   ├── catalog_validation_summary.csv
│   ├── conclusion_stability_matrix.csv
│   ├── cumulative_moment_proxy_by_subset.csv
│   ├── figure_burst_moment_hierarchy_summary.png
│   ├── figure_bvalue_spatial_comparison.png
│   ├── figure_catalog_mechanism_evidence_matrix.png
│   ├── figure_cumulative_moment_proxy.png
│   ├── figure_magnitude_frequency_annotations.png
│   ├── figure_sliding_bvalue_temporal_evolution.png
│   ├── figure_sliding_mc_reliability_timeline.png
│   ├── final_answer_table.csv
│   ├── magnitude_hierarchy_bursts.csv
│   ├── magnitude_hierarchy_phase_subset.csv
│   ├── mechanism_coverage_audit.csv
│   ├── mechanism_join_audit.csv
│   ├── moment_dominance_metrics.csv
│   ├── moment_proxy_event_table.csv
│   ├── phase_aggregate_bvalue_summary.csv
│   ├── phase_boundaries.csv
│   ├── phase_moment_proxy_summary.csv
│   ├── phase_sliding_bvalue_summary.csv
│   ├── phase_transition_assessment.csv
│   ├── robustness_change_log.csv
│   ├── sliding_bvalue_combined_local.csv
│   ├── sliding_bvalue_exploratory_subsets.csv
│   ├── sliding_bvalue_M1_extended.csv
│   ├── sliding_bvalue_M3_extended.csv
│   ├── spatial_bvalue_comparison.csv
│   ├── spatial_membership.csv
│   ├── spatial_phase_overlap_summary.csv
│   ├── spatial_reliability_audit.csv
│   ├── subset_count_summary.csv
│   ├── validated_catalog.csv
│   ├── window_reliability_summary.csv
│   └── window_size_selection.csv
└── 02_mechanism_coverage_audit
    ├── mechanism_coverage_audit.csv
    ├── mechanism_coverage_by_magnitude_threshold.csv
    ├── mechanism_coverage_by_phase_and_magnitude.csv
    ├── mechanism_coverage_by_phase_and_spatial_class.csv
    ├── mechanism_coverage_by_phase.csv
    ├── mechanism_coverage_by_spatial_class.csv
    ├── mechanism_coverage_overview.png
    ├── mechanism_coverage_summary.txt
    ├── mechanism_field_completeness.csv
    ├── mechanism_field_completeness.png
    ├── mechanism_matching_tolerance_grid.csv
    ├── mechanism_match_pairs_basic.csv
    ├── mechanism_match_pairs_with_context.csv
    ├── mechanism_representativeness_bias.png
    └── mechanism_representativeness_tests.csv

2 directories, 54 files
</output_directory_structure>

## Per-Task Scientific Analyses
<task_analysis>
Task: 01_catalog_screening_analysis
Description: Build the validated Aomori master catalog and run the full catalog-level screening workflow for sliding-window completeness and b-value, spatial comparisons, magnitude hierarchy, moment proxy, robustness checks, figures, and machine-readable summaries.
Analysis file: <CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/analysis/01_catalog_screening_analysis.md
Output directory: <CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/01_catalog_screening_analysis

## Scientific Purpose

This task screened whether the relocated/filtered Aomori active-year M1–M3 local earthquake catalog is more consistent with independent ruptures, phase-separated activation, compact/swarm-like compound activation, repeated shallow local activation, or background/window effects, using only catalog-level statistics. The implemented screening focused on:

- time-varying completeness and sliding-window b-value behavior,
- spatial contrasts among M1-centered, M3-centered, along-axis, and off-axis subsets,
- magnitude hierarchy within key phases and bursts,
- a magnitude-based moment-release proxy,
- a catalog-level mechanism-evidence matrix constrained to non-causal statistical interpretation.

The validated working catalog contains 25,646 events overall, with 9,109 events in the combined M1–M3 local zone, 7,402 in the M1 extended zone, 7,268 in the M3 extended zone, 5,148 in the along-axis 30 km subset, and 3,961 in the off-axis 30 km subset, based on `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/01_catalog_screening_analysis/catalog_validation_summary.csv` and `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/01_catalog_screening_analysis/subset_count_summary.csv`.

## Method and Implementation Evidence

A validated master catalog was built and screened in neutral geometric domains around M1 and M3, using the relocated/filtered source catalog as the core input and retaining M2-aware comparison as a robustness check rather than a default exclusion. The main implementation evidence is in:

- `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/01_catalog_screening_analysis/validated_catalog.csv`
- `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/01_catalog_screening_analysis/spatial_membership.csv`
- `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/01_catalog_screening_analysis/phase_boundaries.csv`

For b-value analysis, the primary product was a fixed-count sliding-window calculation in the combined local zone, using 500-event windows and 100-event steps, with median event time used as the window time stamp. The same 500-event window size was feasible across the main extended and comparison subsets, as documented in `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/01_catalog_screening_analysis/window_size_selection.csv`. Sliding outputs, including Mc, b, and reliability classes, are preserved in:

- `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/01_catalog_screening_analysis/sliding_bvalue_combined_local.csv`
- `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/01_catalog_screening_analysis/sliding_bvalue_M1_extended.csv`
- `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/01_catalog_screening_analysis/sliding_bvalue_M3_extended.csv`
- `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/01_catalog_screening_analysis/sliding_bvalue_exploratory_subsets.csv`
- `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/01_catalog_screening_analysis/window_reliability_summary.csv`

Phase summaries were computed as secondary descriptors, not as the primary evidence, and explicitly compared against the sliding results through:

- `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/01_catalog_screening_analysis/phase_sliding_bvalue_summary.csv`
- `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/01_catalog_screening_analysis/phase_aggregate_bvalue_summary.csv`
- `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/01_catalog_screening_analysis/aggregate_vs_sliding_consistency.csv`
- `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/01_catalog_screening_analysis/phase_transition_assessment.csv`

Magnitude hierarchy and moment proxy were quantified for phases and rate-defined bursts using machine-readable tables:

- `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/01_catalog_screening_analysis/magnitude_hierarchy_phase_subset.csv`
- `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/01_catalog_screening_analysis/magnitude_hierarchy_bursts.csv`
- `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/01_catalog_screening_analysis/phase_moment_proxy_summary.csv`
- `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/01_catalog_screening_analysis/burst_moment_proxy_summary.csv`
- `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/01_catalog_screening_analysis/moment_dominance_metrics.csv`
- `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/01_catalog_screening_analysis/cumulative_moment_proxy_by_subset.csv`

Robustness checks directly relevant to the main conclusions were logged in:

- `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/01_catalog_screening_analysis/conclusion_stability_matrix.csv`
- `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/01_catalog_screening_analysis/robustness_change_log.csv`

Mechanism screening was summarized without causal inference in:

- `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/01_catalog_screening_analysis/catalog_mechanism_evidence_matrix.csv`
- `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/01_catalog_screening_analysis/final_answer_table.csv`

The focal-mechanism audit indicates limited and uneven catalog linkage: 354 mechanism-table rows existed, 239 had good catalog matches, matched local-zone fraction was only 0.0335, and matched along-axis fraction was 0.0, from `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/01_catalog_screening_analysis/mechanism_join_audit.csv`. This supports treating mechanism-based interpretation as sparse or exploratory.

## Key Results and Evidence Files

### 1. Sliding-window b-values are usable, but only with reliability grading and caution

The final answer table explicitly classifies the sliding-window b-value results as interpretable “yes_with_caution,” citing 217 interpretable combined-local windows in the primary analysis: `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/01_catalog_screening_analysis/final_answer_table.csv`.

The primary visual evidence is `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/01_catalog_screening_analysis/figure_sliding_mc_reliability_timeline.png`, which shows:

- adopted Mc usually in the ~1.2–1.5 range,
- episodic Mc increases near the M1 and M3 intervals,
- a reliability mix dominated by exploratory windows, but with recurring robust windows,
- no visually dominant “not interpretable” population.

The spatial summary confirms that all major comparison subsets produced interpretable windows under the selected design. For example, the combined local subset had 87 windows, all interpretable, with 24 robust, 4 usable-with-caution, and 59 exploratory; M1 extended had 70 interpretable windows; M3 extended had 68; along-axis 30 km had 47; off-axis 30 km had 35. These statistics come from `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/01_catalog_screening_analysis/spatial_bvalue_comparison.csv`.

The reliability mix should still constrain interpretation. `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/01_catalog_screening_analysis/window_reliability_summary.csv` shows many windows classified exploratory, often because of Mc-method disagreement. Therefore the most defensible interpretation is that the sliding b-values are scientifically usable for screening temporal and spatial tendencies, but not for over-interpreting short-scale fluctuations.

### 2. Combined-local b-value varies through time, and the clearest phase change is a decrease into the pre-M3 phase

The main temporal figure, `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/01_catalog_screening_analysis/figure_sliding_bvalue_temporal_evolution.png`, shows non-stationary b-value behavior across the catalog year, with pronounced excursions around the M1 and M3 time markers and more moderate values during intervening periods.

Phase-summary medians from `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/01_catalog_screening_analysis/phase_sliding_bvalue_summary.csv` for the combined local zone are:

- baseline_primary: median b = 0.726, median Mc = 1.20, 4 interpretable windows,
- M1_related_primary: median b = 0.751, median Mc = 1.50, 31 interpretable windows,
- middle_primary: median b = 0.694, median Mc = 1.40, 14 interpretable windows,
- preM3_primary: median b = 0.562, median Mc = 1.25, 8 interpretable windows,
- postM3_context: median b = 0.721, median Mc = 1.50, 30 interpretable windows.

The formal transition table in `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/01_catalog_screening_analysis/phase_transition_assessment.csv` identifies:

- baseline → M1-related: broadly similar (+0.025),
- M1-related → middle: broadly similar (−0.057),
- middle → preM3: decrease (−0.132),
- preM3 → postM3: increase (+0.159).

This supports a report-ready statement that the strongest catalog-level b-value contrast is not a clean baseline-to-M1 break, but a decline from the middle phase into the final pre-M3 activation, followed by rebound in the post-M3 context.

### 3. Phase-level aggregate b-values are broadly consistent with the sliding analysis, but aggregate windows alone would understate time structure

The consistency test in `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/01_catalog_screening_analysis/final_answer_table.csv` reports the aggregate-versus-sliding comparison as “mostly_consistent,” with zero potentially misleading subset-phase combinations flagged in the evidence summary.

The aggregate phase values for the combined local zone from `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/01_catalog_screening_analysis/phase_aggregate_bvalue_summary.csv` are:

- baseline_primary: Mc 1.2, b 0.796,
- baseline_sensitivity: Mc 1.1, b 0.746,
- M1_related_primary: Mc 1.6, b 0.608,
- middle_primary: Mc ~1.4, b ~0.711,
- preM3_primary: lower-b phase, consistent with the sliding decrease.

The summary figure `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/01_catalog_screening_analysis/figure_magnitude_frequency_annotations.png` visually reinforces this by showing:

- highest aggregate b in the baseline,
- lowest aggregate b and highest Mc in the M1-related phase,
- intermediate middle-phase values,
- low pre-M3 b with relatively low Mc.

However, the sliding figure shows substantial within-phase variability near M1 and M3 that is not recoverable from one number per phase. Thus the aggregate values are acceptable descriptors, but the sliding-window results remain the primary evidence for phase-aware interpretation.

### 4. Spatial b-value differences exist, but they are modest; off-axis subsets have slightly higher median b than along-axis subsets

The spatial comparison figure `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/01_catalog_screening_analysis/figure_bvalue_spatial_comparison.png` shows all median sliding-window b-values clustering in a narrow range (~0.65–0.75), with the highest medians in off-axis subsets and the lowest in M1 core / along-axis 20 km.

Machine-readable values from `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/01_catalog_screening_analysis/spatial_bvalue_comparison.csv` are:

- combined_local: 0.714,
- combined_local_m2aware: 0.709,
- M1_extended: 0.708,
- M3_extended: 0.695,
- M1_core: 0.648,
- M3_core: 0.730,
- along_axis_20km: 0.662,
- along_axis_30km: 0.683,
- off_axis_20km: 0.746,
- off_axis_30km: 0.741,
- overlap_60km: 0.677.

All listed subsets are assigned interpretation_class = robust in that table, meaning the subset-level comparison itself is acceptable, even though many individual windows remain exploratory. `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/01_catalog_screening_analysis/spatial_reliability_audit.csv` shows the reliability mix by subset.

The key screening result is therefore modest spatial differentiation rather than a strong corridor signal. Off-axis subsets have slightly higher median b-values than along-axis subsets, and M1/M3-centered extended zones are similar to the combined-local median. This weakens any claim that the catalog is dominantly organized as a robust along-axis/corridor process.

### 5. Magnitude hierarchy differs strongly by phase: the pre-M3 phase is dominated by one extreme event, while the M1-related phase contains multiple large companions

Phase hierarchy is preserved in `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/01_catalog_screening_analysis/magnitude_hierarchy_phase_subset.csv`.

For the combined local zone:

- baseline_primary: largest 3.9, second 3.9, third 3.7; no M4+,
- M1_related_primary: largest 6.9, second 6.6, third 6.4; gap 0.3 then 0.2; 83 M4+, 30 M5+, 4 M6+; 2 companions within 0.5 magnitude units and 6 within 1.0,
- middle_primary: largest 6.1, second 6.1, third 5.6; 18 M4+, 5 M5+, 2 M6+,
- preM3_primary: largest 7.7, second 6.7, third 5.0; gap 1.0 then 1.7; 14 M4+, 3 M5+, 2 M6+; 0 companions within 0.5 and 1 within 1.0,
- full_M1_to_M3: largest 7.7, second 6.9, third 6.7.

These values show that the M1-related phase is large-event-rich and internally compound at the upper end, whereas the pre-M3 phase is much more top-heavy because the largest event stands well above the next two.

The off-axis 30 km subset emphasizes this contrast even more: in preM3_primary, largest = 7.7 while second = 3.7 and third = 3.4, giving a 4.0-unit first gap. This is direct evidence that the pre-M3 off-axis sample is overwhelmingly dominated by one very large event, from the same hierarchy table.

### 6. Moment release is strongly single-event dominated at the interval scale, with pre-M3 release overwhelming earlier phases

The cumulative-moment figure `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/01_catalog_screening_analysis/figure_cumulative_moment_proxy.png` shows an episodic release history: modest earlier steps and a dominant late jump near the M3 interval. The late increase is especially strong in the extended and off-axis subsets, while along-axis 30 km remains much lower.

Phase-level moment results from `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/01_catalog_screening_analysis/phase_moment_proxy_summary.csv` for combined_local are:

- baseline_primary: total moment proxy 5.32e15, top1 fraction 0.168,
- M1_related_primary: 5.14e19, top1 fraction 0.548, top3 fraction 0.840,
- middle_primary: 4.13e18, top1 fraction 0.430, top3 fraction 0.938,
- preM3_primary: 4.61e20, top1 fraction 0.969, top3 fraction 0.9998,
- full_M1_to_M3: 5.15e20, top1 fraction 0.868, top3 fraction 0.950,
- postM3_context: 2.01e18, top1 fraction 0.157.

Thus, nearly all full-interval moment release is concentrated in the pre-M3 phase, and that phase itself is almost entirely controlled by its single largest event.

The interval-scale dominance classification in `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/01_catalog_screening_analysis/moment_dominance_metrics.csv` is:

- combined_local: top1 fraction 0.861, single_event_dominated,
- M1_extended: 0.865, single_event_dominated,
- M3_extended: 0.863, single_event_dominated,
- off_axis_30km: 0.992, single_event_dominated,
- along_axis_30km: 0.413, few_event_dominated.

This is a key result: the overall M1–M3 local-zone interval is not moment-balanced across phases or bursts. It is dominated by one largest event, and the off-axis subset is the most extreme case.

### 7. Burst-level behavior is heterogeneous, but the largest burst dominates total release and is itself almost entirely controlled by its top event

The burst figure `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/01_catalog_screening_analysis/figure_burst_moment_hierarchy_summary.png` shows that burst_07 is overwhelmingly the largest burst in total moment proxy and has top-1 fraction near 1.0.

The tabulated burst results from `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/01_catalog_screening_analysis/burst_moment_proxy_summary.csv` are:

- burst_01, M1_centered: 2,688 events, 5.13e19 total moment proxy, top1 fraction 0.550, largest M 6.9,
- burst_02, M1_centered: 58 events, 8.62e13, top1 fraction 0.164, largest M 2.7,
- burst_03, M1_centered: 55 events, 2.02e16, top1 fraction 0.985, largest M 4.8,
- burst_04, off_corridor_or_mixed_local: 57 events, 1.78e18, top1 fraction 0.999, largest M 6.1,
- burst_05, M1_centered: 47 events, 2.09e18, top1 fraction 0.849, largest M 6.1,
- burst_06, M1_centered: 440 events, 1.43e19, top1 fraction 0.990, largest M 6.7,
- burst_07, mixed_overlap: 3,189 events, 4.49e20, top1 fraction 0.996, largest M 7.7.

This demonstrates that burst behavior is not uniformly swarm-like. Some bursts are moderately compound, especially burst_01, but the late mixed-overlap burst controls most of the moment budget and is essentially single-event dominated.

### 8. M2-aware filtering and step-size sensitivity have only minor influence on the main interpretation

Robustness testing in `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/01_catalog_screening_analysis/robustness_change_log.csv` shows:

- combined_local median b, step 100 vs step 200: 0.7137 vs 0.7023, change −0.0115, minor,
- middle-phase raw vs M2-aware aggregate b: no change,
- moment dominance raw vs M2-aware: no change.

The conclusion stability matrix in `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/01_catalog_screening_analysis/conclusion_stability_matrix.csv` marks the following as stable:

- sliding_bvalue_interpretability,
- middle_phase_M2_sensitivity,
- moment_dominance.

These outputs support the handoff context that M2-aware filtering has limited influence on the main catalog-level conclusions.

### 9. Mechanism-screening results favor phase-separated and repeated shallow local activation interpretations, while along-axis, stress, fluid, and slow-slip candidates remain weak

The mechanism figure `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/01_catalog_screening_analysis/figure_catalog_mechanism_evidence_matrix.png` ranks the highest screening support for:

- `M1_M3_centered_repeated_shallow_activation`,
- `phase_separated_activation_between_M1_and_M3`.

The full matrix in `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/01_catalog_screening_analysis/catalog_mechanism_evidence_matrix.csv` gives confidence levels and caveats:

- independent_local_ruptures: low_to_moderate; supported by identifiable separated phases and non-zero mixed/off-axis contributions, but contradicted by sustained elevated middle-phase activity.
- phase_separated_activation_between_M1_and_M3: moderate; supported by strong M1-related, weaker but elevated middle, and clear pre-M3 activation.
- compact_swarm_like_compound_activation: low_to_moderate; possible where top-event dominance is limited and companions exist, but weakened by strong event hierarchy.
- M1_M3_centered_repeated_shallow_activation: moderate; supported by spatial bookkeeping and shallow-dominated larger-event context, but not sufficient to demonstrate repeated rupture on the same structure.
- stepwise_or_along_axis_activation_candidate: low; contradicted by lack of robust corridor preference.
- stress_interaction_candidate: low; catalog statistics alone insufficient.
- fluid_diffusion_like_candidate: low; catalog geometry, b-value, and moment trends are non-diagnostic.
- slow_slip_related_candidate: low; no catalog-only support.
- background_window_artifact: low_to_moderate; some aggregation/Mc effects exist, but activity increase above baseline and phase partitioning remain clear.

The final answer table also lists the supported, weakened, and unresolved mechanism groupings and prioritizes next steps: relocation QC, waveform similarity, detection completeness, and formal change-point modeling in `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/01_catalog_screening_analysis/final_answer_table.csv`.

## Limitations and Assumptions

- Sliding-window b-values are not uniformly high-confidence. Many windows are exploratory, often due to Mc-method disagreement, so short-term oscillations near M1 and M3 should not be over-interpreted. Main evidence: `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/01_catalog_screening_analysis/window_reliability_summary.csv` and `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/01_catalog_screening_analysis/figure_sliding_mc_reliability_timeline.png`.
- Aggregate phase b-values are secondary summaries only. They are broadly consistent with the sliding analysis, but they suppress within-phase variability and therefore should not be used as the sole basis for phase interpretation. Evidence: `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/01_catalog_screening_analysis/aggregate_vs_sliding_consistency.csv`.
- Spatial contrasts are modest in amplitude. Even where subset-level comparisons are labeled robust, the median b-value spread is small, so “difference” here means relative tendency rather than a large or diagnostic separation. Evidence: `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/01_catalog_screening_analysis/spatial_bvalue_comparison.csv`.
- Moment proxy results are magnitude-based screening metrics, not physical source inversions. They identify dominance patterns but cannot establish triggering, rupture connectivity, or energy partitioning beyond catalog-level relative release.
- Mechanism information is sparse and spatially biased for the local screening problem. Of 354 mechanism rows, only 239 matched well to the catalog; matched local-zone fraction is 3.35%, and matched along-axis fraction is zero. Therefore mechanism consistency should be treated as unavailable or exploratory for most catalog classes. Evidence: `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/01_catalog_screening_analysis/mechanism_join_audit.csv`.
- The task explicitly does not support causal inference. None of the catalog statistics alone can establish stress transfer, fluid migration, slow slip, or true migration. The mechanism evidence matrix correctly treats those as low-confidence candidates requiring independent physical follow-up. Evidence: `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/01_catalog_screening_analysis/catalog_mechanism_evidence_matrix.csv`.
- The handoff notes the outputs list is truncated, but the key machine-readable summaries and all requested diagnostic images for this task were available and analyzable.

## Report-Ready Summary

The catalog-level screening of the relocated/filtered Aomori active-year M1–M3 local system supports a cautious but coherent interpretation.

Sliding-window b-value analysis in the combined local zone is usable for interpretation with reliability grading. The primary 500-event, 100-step design produced interpretable windows across the main spatial subsets, but many windows are exploratory because Mc estimation is not uniformly stable. Accordingly, the b-value results are suitable for screening broad temporal and spatial tendencies, not for asserting fine-scale causal changes. Key evidence: `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/01_catalog_screening_analysis/figure_sliding_bvalue_temporal_evolution.png`, `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/01_catalog_screening_analysis/figure_sliding_mc_reliability_timeline.png`, and `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/01_catalog_screening_analysis/phase_sliding_bvalue_summary.csv`.

The combined-local b-value does vary through time. The clearest catalog-level shift is a decrease from the middle phase into the final pre-M3 activation, with recovery after M3. Baseline and M1-related medians are broadly similar at the sliding-window level, while the pre-M3 phase has the lowest median b. This means the most defensible phase-aware statement is not a simple monotonic progression from baseline into M1, but a more complex time evolution with a pronounced low-b pre-M3 interval. Evidence: `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/01_catalog_screening_analysis/phase_transition_assessment.csv`.

Phase-level aggregate b-values are mostly consistent with the sliding-window evolution, but they remain secondary descriptors. Aggregate values alone would miss strong within-phase variability near M1 and M3 and could oversimplify the structure of t
...[truncated]
</task_analysis>

<task_analysis>
Task: 02_mechanism_coverage_audit
Description: Perform a reusable standalone audit of focal-mechanism matching and representativeness by phase, magnitude level, and spatial class.
Analysis file: <CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/analysis/02_mechanism_coverage_audit.md
Output directory: <CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/02_mechanism_coverage_audit

## Scientific Purpose

This task audited whether focal-mechanism information from `<CASE_ROOT>/data/source_mechanism/Snet_mecha.csv` can be used as representative evidence for the relocated/filtered Aomori active-year catalog, especially within the M1-M3 screening framework. The scientific purpose was not to interpret rupture style, triggering, or mechanism evolution, but to determine whether mechanism data coverage is sufficient and balanced enough across time phase, magnitude level, and spatial class to support later catalog-level interpretation.

The audit therefore addressed three questions:

1. How many focal-mechanism rows can be confidently matched to catalog events?
2. How sparse or biased is the matched mechanism subset across phases, magnitudes, and local spatial classes?
3. Whether mechanism-based consistency statements should be treated as unavailable, exploratory, descriptive, or reusable in later synthesis.

## Method and Implementation Evidence

The task produced a reusable matching-and-audit package centered on `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/02_mechanism_coverage_audit`.

Implementation evidence shows that the workflow:
- matched mechanism metadata rows to relocated catalog events using time, horizontal distance, and depth tolerances, then audited ambiguity and match quality;
- summarized coverage at catalog-wide, phase, magnitude-threshold, and spatial-class levels;
- distinguished fully populated mechanism records from metadata-only matches;
- tested whether matched events differ systematically from unmatched events in magnitude, depth, and local distances.

Key implementation evidence files:
- overall audit metrics: `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/02_mechanism_coverage_audit/mechanism_coverage_audit.csv`
- tolerance-grid robustness: `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/02_mechanism_coverage_audit/mechanism_matching_tolerance_grid.csv`
- phase summaries: `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/02_mechanism_coverage_audit/mechanism_coverage_by_phase.csv`
- spatial summaries: `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/02_mechanism_coverage_audit/mechanism_coverage_by_spatial_class.csv`
- magnitude-threshold summaries: `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/02_mechanism_coverage_audit/mechanism_coverage_by_magnitude_threshold.csv`
- cross-tabulated phase–magnitude and phase–spatial summaries:  
  `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/02_mechanism_coverage_audit/mechanism_coverage_by_phase_and_magnitude.csv` and  
  `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/02_mechanism_coverage_audit/mechanism_coverage_by_phase_and_spatial_class.csv`
- field-level completeness: `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/02_mechanism_coverage_audit/mechanism_field_completeness.csv`
- event-level match tables:  
  `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/02_mechanism_coverage_audit/mechanism_match_pairs_basic.csv` and  
  `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/02_mechanism_coverage_audit/mechanism_match_pairs_with_context.csv`
- representativeness tests: `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/02_mechanism_coverage_audit/mechanism_representativeness_tests.csv`

Key visual evidence:
- coverage overview: `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/02_mechanism_coverage_audit/mechanism_coverage_overview.png`
- field completeness: `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/02_mechanism_coverage_audit/mechanism_field_completeness.png`
- representativeness bias diagnostics: `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/02_mechanism_coverage_audit/mechanism_representativeness_bias.png`

The task’s own textual summary in `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/02_mechanism_coverage_audit/mechanism_coverage_summary.txt` explicitly states the intended interpretation rule: focal mechanisms are unavailable for general catalog-wide phase/spatial inference and only exploratory-to-descriptive for larger-event subsets with explicit coverage reporting.

## Key Results and Evidence Files

### 1. Matching quality is technically good, but mechanism availability is extremely sparse relative to the earthquake catalog

The audit found:
- 25,646 relocated catalog events total;
- 9,109 events in the combined M1-M3 local zone;
- 354 mechanism metadata rows;
- 240 matched mechanism rows, corresponding to 67.8% of mechanism rows, but only 240 unique catalog events.

Catalog-level availability is therefore very low:
- `catalog_fraction_with_mecha_all = 0.009357` (~0.94% of all relocated events),
- `catalog_fraction_with_mecha_local_zone = 0.000878` (~0.088% of combined local-zone events).

These values are reported in `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/02_mechanism_coverage_audit/mechanism_coverage_audit.csv` and summarized in `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/02_mechanism_coverage_audit/mechanism_coverage_summary.txt`.

Match precision itself is strong:
- best tolerances: time ≤ 1.0 s, horizontal ≤ 2.0 km, depth ≤ 2.0 km;
- median differences: 0.01 s, 0.0852 km horizontal, 0.08 km depth;
- 95th percentiles: 0.02 s, 0.225845 km horizontal, 0.371 km depth;
- only 1 ambiguous mechanism row and 0 ambiguous catalog events at the top grid.

This supports the conclusion that the main limitation is not poor matching quality but sparse mechanism supply. Evidence: `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/02_mechanism_coverage_audit/mechanism_coverage_audit.csv` and `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/02_mechanism_coverage_audit/mechanism_matching_tolerance_grid.csv`.

### 2. Phase coverage is highly uneven and remains too sparse for general phase-wise mechanism interpretation

Phase-specific matched-event fractions are:
- baseline to M1-14d: 7/4163 = 0.001681
- M1-related phase: 12/3971 = 0.003022
- middle phase: 195/11295 = 0.017264
- pre-M3 phase: 13/2203 = 0.005901
- post-M3 context: 13/4016 = 0.003237

The middle phase dominates mechanism availability in both absolute count and fractional coverage. The visual pattern is clear in `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/02_mechanism_coverage_audit/mechanism_coverage_overview.png`, whose phase panel shows the middle phase as the only visibly elevated coverage bin.

However, even the best phase fraction is only ~1.7%, so the matched subset remains sparse relative to the full catalog. This means phase-based mechanism consistency is not representative for the general M1-M3 local catalog. Evidence:
- `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/02_mechanism_coverage_audit/mechanism_coverage_by_phase.csv`
- `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/02_mechanism_coverage_audit/mechanism_coverage_overview.png`
- `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/02_mechanism_coverage_audit/mechanism_coverage_summary.txt`

A useful nuance is that the complete-mechanism fraction among matched rows varies by phase:
- baseline: 57.1%
- M1-related: 50.0%
- middle: 27.2%
- pre-M3: 38.5%
- post-M3: 23.1%

So the middle phase has more matched rows but a lower share of fully populated mechanisms. Evidence: `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/02_mechanism_coverage_audit/mechanism_coverage_by_phase.csv`.

### 3. Spatial coverage is strongly biased toward M3-side/off-axis subsets and effectively absent in M1-centered and along-axis classes

Spatial-class coverage in the local framework shows:
- combined_local: 8/9109 = 0.000878
- M3_extended: 8/7268 = 0.001101
- M3_core: 4/2851 = 0.001403
- off_axis_20km: 8/4223 = 0.001894
- off_axis_30km: 8/3961 = 0.002020
- M1_extended: 0/7402
- M1_core: 0/4460
- along_axis_20km: 0/4886
- along_axis_30km: 0/5148
- overlap_60km: 0/5561

Thus, within the neutral M1-M3 local-zone bookkeeping:
- all local mechanism matches are in M3-related/off-axis classes;
- no mechanism-matched events occur in M1-centered, along-axis, or overlap classes.

This spatial imbalance is evident in both the table and the overview figure. Evidence:
- `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/02_mechanism_coverage_audit/mechanism_coverage_by_spatial_class.csv`
- `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/02_mechanism_coverage_audit/mechanism_coverage_overview.png`

This is a critical downstream result: any attempt to use focal mechanisms to compare M1-centered versus M3-centered behavior, or along-axis versus off-axis behavior, would not be representative for the local catalog and is effectively unavailable for M1-centered and along-axis classes.

### 4. Mechanism coverage improves strongly with magnitude, so any usable mechanism inference is restricted to larger events

Coverage by catalog magnitude threshold is:
- M≥3.0: 240/1350 = 0.177778
- M≥3.5: 237/617 = 0.384117
- M≥4.0: 92/266 = 0.345865
- M≥4.5: 35/145 = 0.241379
- M≥5.0: 18/69 = 0.260870

The overview figure shows this same strong rise from M≥3.0 to M≥3.5–4.0. Evidence:
- `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/02_mechanism_coverage_audit/mechanism_coverage_by_magnitude_threshold.csv`
- `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/02_mechanism_coverage_audit/mechanism_coverage_overview.png`

At higher thresholds, the fraction of matched rows with complete mechanism solutions also increases:
- M≥3.0: 29.6%
- M≥3.5: 29.1%
- M≥4.0: 44.6%
- M≥4.5: 57.1%
- M≥5.0: 61.1%

This means focal mechanisms become more usable for larger-event subsets, but that usability does not extend to the full M1-M3 M1–M3 local microearthquake population. Evidence: `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/02_mechanism_coverage_audit/mechanism_coverage_by_magnitude_threshold.csv`.

Phase–magnitude cross-tabulation further shows that within some phases, usable counts at high magnitude are very small; for example, baseline M≥4.5 has only 1 matched event and M1-related M≥4.5 has only 1 matched event. Evidence: `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/02_mechanism_coverage_audit/mechanism_coverage_by_phase_and_magnitude.csv`.

### 5. The matched mechanism subset is strongly magnitude-biased and often depth-biased, so it is not representative of the catalog

Representativeness tests show strong positive magnitude bias:
- all catalog: matched median M 3.8 vs unmatched 1.5, difference +2.3
- combined local: matched median M 3.7 vs unmatched 1.7, difference +2.0

Within phases, magnitude differences remain large:
- baseline: +2.9
- M1-related: +2.0
- middle: +2.3
- pre-M3: +2.6
- post-M3: +2.2

Depth bias is also substantial in several phases:
- combined local: matched median depth 30.12 km vs unmatched 12.27 km, difference +17.85 km
- baseline: +13.61 km
- M1-related: +33.415 km
- middle: +2.06 km
- pre-M3: +27.95 km
- post-M3: +23.36 km

These results are plotted in `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/02_mechanism_coverage_audit/mechanism_representativeness_bias.png`, which shows consistently positive magnitude offsets and strongly positive depth offsets except for the middle phase, where the depth bias is relatively small.

Evidence:
- `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/02_mechanism_coverage_audit/mechanism_representativeness_tests.csv`
- `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/02_mechanism_coverage_audit/mechanism_representativeness_bias.png`

Additional local spatial bias exists:
- in the combined local zone, matched events have median distance to M1 of 83.63 km versus 31.64 km for unmatched events, difference +51.98 km;
- matched events have median distance to M3 of 32.998 km versus 43.493 km for unmatched events, difference -10.50 km.

This confirms that the matched local sample is displaced away from M1 and somewhat closer to M3, consistent with the zero-coverage result in M1-centered classes. Evidence: `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/02_mechanism_coverage_audit/mechanism_representativeness_tests.csv`.

### 6. Mechanism-field completeness is internally consistent, but only for a minority of matched events

The field-completeness figure and CSV show that focal-mechanism-related fields have very similar non-null fractions, about 29–30% each, for:
- focal_mech_score
- n_mech_stations
- P/T axis azimuths
- strike/dip/rake for both nodal planes
- focal_mech_projection
- method/source descriptors

The key implication is that missingness is mostly event-level rather than field-specific: when a solution exists, it tends to include a coherent set of mechanism attributes; when absent, nearly all fields are absent. Evidence:
- `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/02_mechanism_coverage_audit/mechanism_field_completeness.png`
- `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/02_mechanism_coverage_audit/mechanism_field_completeness.csv`

This is useful for later work because it means that mechanism analyses on the matched-and-complete subset are internally coherent, but the subset is too small and biased for general inference.

### 7. Standalone conclusion for later integrated reporting

The task’s own summary gives the appropriate interpretation rule: focal mechanisms should be treated as unavailable for general catalog-wide phase/spatial inference and only exploratory-to-descriptive for larger-event subsets with explicit coverage statements. This is directly supported by the sparse fractions, strong magnitude bias, depth bias outside the middle phase, and near-zero local coverage in M1-centered and along-axis classes. Evidence:
- `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/02_mechanism_coverage_audit/mechanism_coverage_summary.txt`
- `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/02_mechanism_coverage_audit/mechanism_coverage_overview.png`
- `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/02_mechanism_coverage_audit/mechanism_representativeness_bias.png`

## Limitations and Assumptions

- This task audited coverage and representativeness only. It does not provide valid evidence for rupture style, faulting regime transitions, triggering, stress transfer, fluid migration, or slow slip.
- Mechanism matching quality is good, but catalog coverage is extremely sparse: only 240 matched events in the full catalog and only 8 in the combined M1-M3 local zone, with 0 matched events in M1-centered and along-axis local classes. This severely limits interpretability for the central local-system questions.
- The majority of matched rows are metadata-only rather than complete mechanism solutions. In the combined local zone, only 1 of 8 matched events has a complete mechanism (`complete_mechanism_fraction_of_matched = 0.125`), so even the already tiny local matched sample is mostly incomplete.
- Representativeness is strongly magnitude-biased throughout and depth-biased in most phases except the middle phase. Therefore, any apparent phase or spatial mechanism pattern in the matched subset would be confounded by sampling bias.
- The middle phase has the strongest match coverage and relatively small depth bias, but even there the matched fraction is only ~1.7%, so it is still not representative of the full phase population.
- Magnitude-threshold analyses become more favorable above M3.5–4.0, but phase-by-phase counts at high magnitude are still often small, so later use should remain descriptive or exploratory and explicitly state sample counts.
- No PDF outputs were listed for this task, so only image and tabular outputs were audited.

## Report-Ready Summary

This standalone audit shows that focal-mechanism information is technically matchable but scientifically under-representative for the M1-M3 catalog screening problem. Matching quality is strong, with best tolerances of 1 s, 2 km horizontal, and 2 km depth, median residuals of 0.01 s, 0.085 km, and 0.08 km, and essentially no ambiguity at the preferred tolerance grid (`<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/02_mechanism_coverage_audit/mechanism_coverage_audit.csv`; `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/02_mechanism_coverage_audit/mechanism_matching_tolerance_grid.csv`). However, availability is sparse: only 240 catalog events are matched across 25,646 relocated events (~0.94%), and only 8 matched events occur in the combined M1-M3 local zone (~0.088%) (`<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/02_mechanism_coverage_audit/mechanism_coverage_audit.csv`).

Coverage is strongly uneven by phase and space. The middle phase has the largest matched fraction (~1.73%), whereas baseline, M1-related, pre-M3, and post-M3 phases remain below ~0.6% (`<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/02_mechanism_coverage_audit/mechanism_coverage_by_phase.csv`; `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/02_mechanism_coverage_audit/mechanism_coverage_overview.png`). Spatially, all local matched events fall in M3-related/off-axis classes, with zero matched events in M1-centered, along-axis, and overlap classes (`<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/02_mechanism_coverage_audit/mechanism_coverage_by_spatial_class.csv`). Mechanism availability increases strongly with magnitude, reaching ~38% for M≥3.5 and ~24–26% for M≥4.5–5.0, so only larger-event subsets have potentially reusable mechanism coverage (`<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/02_mechanism_coverage_audit/mechanism_coverage_by_magnitude_threshold.csv`).

The matched mechanism subset is not representative of the catalog. Matched events are systematically larger by about +2.0 to +2.9 magnitude units across local and phase subsets, and are commonly deeper by +14 to +33 km outside the middle phase; in the combined local zone they are also displaced away from M1 and somewhat closer to M3 (`<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/02_mechanism_coverage_audit/mechanism_representativeness_tests.csv`; `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/02_mechanism_coverage_audit/mechanism_representativeness_bias.png`). Field completeness is internally consistent across strike/dip/rake and related attributes, but only for roughly 30% of matched rows, indicating event-level missingness rather than variable-specific defects (`<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/02_mechanism_coverage_audit/mechanism_field_completeness.csv`; `<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/02_mechanism_coverage_audit/mechanism_field_completeness.png`).

For the later integrated report, the defensible synthesis is: focal mechanisms are effectively unavailable for general catalog-wide inference on phase behavior or M1-vs-M3/along-axis spatial comparisons, and any mechanism-based remarks should be restricted to larger-event subsets and labeled exploratory or descriptive, not causal or representative (`<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/02_mechanism_coverage_audit/mechanism_coverage_summary.txt`).
</task_analysis>


## Evaluation Quality Summary
Use this evaluation metadata to disclose delivery status, scientific confidence, and important limitations in the final report.
<evaluation_quality>
{
  "delivery_status": "complete",
  "is_satisfactory": true,
  "limitations": [
    {
      "evidence": "Many sliding-window b-value estimates were classified as exploratory, often due to Mc-method disagreement; reliability mix is documented in window_reliability_summary.csv and figure_sliding_mc_reliability_timeline.png.",
      "impact": "Temporal b-value trends are usable for broad screening but short-timescale fluctuations and boundary-adjacent changes should not be over-interpreted.",
      "severity": "moderate",
      "type": "uncertainty"
    },
    {
      "evidence": "Primary b-value interpretation depends on adopted Mc choice within each window and agreement among MAXC/KS/stability methods was not uniform.",
      "impact": "Absolute b-values and some phase-to-phase contrasts may shift under alternative completeness choices, although major conclusions were reported as stable.",
      "severity": "moderate",
      "type": "method_assumption"
    },
    {
      "evidence": "Spatial b-value differences are small in amplitude even where subset-level summaries are labeled robust.",
      "impact": "Spatial contrasts should be interpreted as weak tendencies rather than strong diagnostic separations.",
      "severity": "low",
      "type": "output_quality"
    },
    {
      "evidence": "Mechanism coverage audit shows extremely sparse and biased focal-mechanism matching in the local system, with near-zero or zero coverage in M1-centered and along-axis classes.",
      "impact": "Mechanism consistency cannot materially support or reject the main catalog hypotheses beyond exploratory remarks for larger events.",
      "severity": "high",
      "type": "data_coverage"
    },
    {
      "evidence": "Moment-release analysis is based on a magnitude-derived proxy rather than direct source-parameter estimates.",
      "impact": "Dominance patterns are useful comparatively, but cannot establish physical rupture interaction or source-process interpretation.",
      "severity": "low",
      "type": "method_assumption"
    }
  ],
  "needs_refinement": false,
  "refinement_priority": "none",
  "scientific_confidence": "moderate"
}
</evaluation_quality>

## Report Synthesis Rules
- Start from the scientific objective and planned workflow.
- Choose the final report shape according to the request and evidence.
- If the user requested a specific format, follow that requested format unless it conflicts with factuality or available evidence.
- Treat concise result summary, technical workflow report, and research-article style report as common shapes, not fixed templates.
- Use task-specific structures when more appropriate, such as diagnostic review, data-quality assessment, method validation, benchmark comparison, or reproducibility report.
- Hybrid structures are allowed when they better serve the scientific objective.
- Do not force a fixed section template when another structure better serves the scientific request.
- Describe implementation at the level needed to understand the evidence, not as a code log.
- Tie every major result to task analyses and concrete output files from the evidence index.
- Include warnings, assumptions, partial coverage, failed items, and other limitations when present.
- Use debug logs only to explain unresolved limitations or important methodological changes.
- Do not fabricate results, citations, or file paths.

</science_report_context>
