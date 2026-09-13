import os
import sys
sys.path.append("<REPO_ROOT>/")
from seismoagent.runing import run_seismoagent

user_request = """
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
"""

if __name__ == "__main__":

    run_name = "03_1C_mechanism_screening"
    output_dir = "<CASE_ROOT>/run"
    reference_papers_dir = "<CASE_ROOT>/docs/reference"
    reference_papers = os.listdir(reference_papers_dir)
    reference_papers = [os.path.join(reference_papers_dir, paper) for paper in reference_papers if paper.endswith(".pdf")]

    run_seismoagent(
        request=user_request,
        run_name=run_name,
        output_dir=output_dir,
        disable_refinement=False,
        max_refinement_rounds=3,
        enable_trajectory=True,
        # resume=os.path.join(output_dir, run_name),
        # resume_stage="coding",
        # resume_coding_step=3
    )
