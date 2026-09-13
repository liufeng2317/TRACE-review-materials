import os
import sys
sys.path.append("<REPO_ROOT>/")
from seismoagent.runing import run_seismoagent

user_request = """
You are an earthquake scientist and data-analysis agent.

Current task:
Analyze long-period b-value evolution and seismicity-rate evolution in the region containing M1 and M3.

Goal:
Use the 2020-2026 Aomori catalog to describe how b-value, Mc, event rate, and spatial b-value patterns evolve around M1 and M3.
The purpose is to infer catalog-level activation-state evolution, not to prove triggering, slow slip, fluid migration, or stress transfer.

Keep the analysis simple and interpretable. Avoid over-designed model checks unless they directly clarify the b-value and activation-state evolution.

Data folder:
"<CASE_ROOT>/data"
Inputs:
- long-period filtered catalog:
  data/catalog/Snet_catalog_20200101_20260522_filter.csv
- mainshock table: catalog/main_earthquake.csv
- optional context: source_mechanism/Snet_mecha.csv, stations/station.sta

Working context:
- Treat the M1-M3 system as phase-structured: pre-M1 reference, M1-related phase, middle phase, final pre-M3 phase, and post-M3 context.
- Use b-value, Mc, rate, and spatial distribution to describe this evolution. Keep physical mechanisms as hypotheses only.

Spatial framework:
Keep the spatial design simple and scientifically targeted.

1. Primary whole study area:
   Use a simple oriented region following the M1-M3 direction, rather than a broad latitude-longitude rectangle.
   The region should cover M1, M3, and surrounding activity with at least about 60 km margin, while avoiding unrelated high-density source regions such as the southwestern cluster seen in the broad rectangle.
   A rotated rectangle or ellipse is sufficient. Output a map showing M1, M3, events, and the chosen boundary.

2. M1/M3-centered expanded subregions:
   Compute separate summaries for M1-centered and M3-centered regions to compare local behavior.
   Use 80 km radius as the primary scale and 60 km radius as a sensitivity check.

3. Optional spatial grid:
   Grid/adaptive-cell b-value maps are optional. Use them only if event count and Mc stability are adequate; otherwise skip them.

Temporal framework:
Use these phase markers mainly for interpretation of the sliding results:
- pre-M1 reference: 2020-01-01 to M1-14d, with M1-7d sensitivity
- M1-related phase: M1-14d to M1+21d
- middle phase: M1+21d to M3-35d
- final pre-M3 phase: M3-35d to M3
- post-M3 context: M3 to catalog end

Main tasks:
1. Select and document the M1-M3 study area.
   Show a map of events, M1, M3, and the chosen boundary.
   Report the boundary definition and event count inside it.

2. Estimate Mc and b-value through time.
   Use fixed-count sliding event windows for the main time series.
   Use 500-event windows with 100-event steps as the primary setting.
   Assign each b-value to the median event time of its window.
   Report Mc, b-value, uncertainty, event count, and reliability for each window.
   Also provide a smoothed temporal trend of the b-value series, such as rolling median/mean across neighboring windows or a lowess-style smoother, to make the average contrast before and after M1 easier to inspect.

3. Compare the three spatial levels.
   Repeat the sliding-window analysis for:
   - the oriented M1-M3 whole study area
   - M1-centered and M3-centered expanded subregions
   - grid/adaptive cells only if they have enough events and stable Mc

4. Compare b-value evolution with event-rate evolution.
   Interpret whether the region shows background-like behavior, sustained elevated activation, relaxation, renewed pre-M3 activation, or mixed spatial behavior.

5. Keep robustness checks limited.
   Only test alternatives that affect the main conclusion, such as oriented rectangle versus ellipse, 60/80 km subregions, Mc method, or 300/500/750-event windows.

Figures:
Generate a compact set of high-quality diagnostic figures:
- study-area selection map showing M1, M3, the earthquake distribution, and the chosen coverage boundary
- simple diagnostic showing why the oriented study area was chosen, if needed
- long-period sliding b-value time series with M1/M2/M3 and phase boundaries, including a smoothed temporal trend
- sliding Mc and reliability timeline
- event-rate and b-value comparison plot
- whole-area and M1/M3 expanded-subregion b-value comparison
- grid-cell b-value / Mc maps only if they are interpretable

Final report:
Answer concisely:
- What coverage area was used and why?
- Did the oriented M1-M3 region avoid unrelated high-density source regions better than the broad rectangle?
- What is the main temporal pattern of b-value evolution?
- How does b-value behave before and after M1?
- How does the overall M1-to-M3 b-value state compare with the pre-M1 background?
- Is the final pre-M3 phase different from the earlier M1-to-M3 interval?
- What possible catalog-level stress / activation-state change is suggested by the b-value and rate evolution?
- How do Mc and event rate evolve alongside b-value?
- Do M1-centered and M3-centered subregions behave differently?
- Are grid-cell results meaningful? If not, say they are not interpretable and do not use them as main evidence.
- What physical follow-up is most justified?

Important:
Do not claim slow slip, fluid migration, stress transfer, or triggering from b-value or rate changes alone.
Do not overinterpret b-value changes without Mc stability and adequate event counts.
Keep the report concise and focused on interpretable catalog patterns.
"""

if __name__ == "__main__":

    run_name = "03_1D_catalog_statistic_model_check"
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
