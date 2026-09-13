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