import os
import sys
sys.path.append("<REPO_ROOT>/")
from seismoagent.runing import run_seismoagent

user_request = """
You are an earthquake scientist and data-analysis agent.

Current task:
Analyze the final foreshock stage and rapid early aftershock expansion of the 2025 Sanriku-Oki JMA M6.9 earthquake.

Goal:
Use the relocated local catalog to quantify how seismicity changed immediately before and after the M6.9 event.
The key comparison is between:
- the final 2 days before M6.9
- the first 0.5 days after M6.9

Focus on apparent catalog migration, activated-area expansion, event-rate increase, moderate-earthquake occurrence, and final-foreshock b-value behavior. This is a catalog-screening analysis, not a proof of aseismic slip or physical triggering.

Data folder:
"<CASE_ROOT>/data"
Inputs:
- target relocated catalog:
  data/catalog/Snet_catalog_relocate_250601_260501.csv
- mainshock table:
  data/catalog/main_earthquake.csv
- optional context:
  data/source_mechanism/Snet_mecha.csv, data/stations/station.sta

Target event:
- Use M1 in main_earthquake.csv as the M6.9 Sanriku-Oki mainshock:
  2025-11-09 08:03:39.240, lat 39.402, lon 143.507, depth 15.9 km, mag 6.9.
- Re-match M1 to the relocated catalog if a near-time/near-space catalog event exists. If no better match is found, use the main_earthquake.csv coordinates as the reference epicenter.
- Identify the largest distinct event in the first 0.5 days after M6.9, expected to be M6.6 if present. This selection must exclude the M6.9 mainshock itself at relative time 0. Mark M6.9 and this largest distinct early-aftershock event on the diagnostic figures. Do not mark later events such as M6.4 if they fall outside the 0-0.5 day analysis window.

Analysis windows and region:
- Primary local-sequence radius: 80 km around M6.9.
- Display/context window: M6.9-10d to M6.9+0.5d.
- Main foreshock analysis window: M6.9-2d <= t < M6.9.
- Main early-aftershock analysis window: M6.9 < t <= M6.9+0.5d. Exclude the mainshock itself from aftershock event counts, rates, largest-event selection, aftershock b-value checks, and aftershock migration fronts.
- Use M6.9-10d to M6.9-2d only as visual/background context when useful, not as a formal phase for the main speed or hull comparison.
- Use 60 km as a compact-core sensitivity check and 100/150 km only to diagnose contamination by distant clusters.

Main tasks:
1. Build an M6.9-centered event table.
   Include origin time, relative time, epicentral distance, local east/north coordinates, depth, magnitude, and phase label.

2. Compare event rate and magnitude occurrence.
   For the two main windows, compute event counts, rates, maximum magnitude, median magnitude, and M3+/M4+/M5+ counts.

3. Check for apparent spatial expansion or migration.
   Make a time-distance plot relative to M6.9 using the 80 km local region.
   Use a 90th-percentile distance front as the main diagnostic.
   Use all events inside the 80 km local region for the front estimate.
   Use simple linear fits for apparent speed:
   - final 2 days before M6.9: use a 0.2 day bin width
   - first 0.5 days after M6.9: use a 0.025 day bin width
   Exclude sparse bins with fewer than 5 events from the front fit and from the plotted front line. Record how many bins were excluded. This is important because a low-count bin can create an unstable 90th-percentile distance front.
   Report the fitted speeds and basic fit diagnostics in a CSV/JSON summary.

4. Estimate activated area.
   Convert locations to local Cartesian coordinates relative to M6.9.
   Rotate coordinates with PCA to define along-sequence and across-sequence axes.
   For the final-2-day foreshock window and the first-0.5-day aftershock window, retain the closest 90% of events by epicentral distance from M6.9 and compute the convex-hull area, along-axis span, and across-axis span.
   Also compute an equivalent hull radius sqrt(area/pi), so the two windows can be compared as activated-area scale.
   Save the retained points and the ordered convex-hull vertices for each window. The activated-area figure must visibly draw the closed convex-hull polygon outlines and light transparent fills, not only the retained event scatter points.
   A scatter-only activated-area figure is incomplete. If convex-hull metrics are computed, the same hull vertices must also be used for plotting the hull outline/fill.

5. Check magnitude-frequency behavior.
   Estimate Mc and b-value for the final-2-day foreshock window as the primary b-value diagnostic.
   The early aftershock b-value may be computed as an exploratory check, but do not overinterpret it because early aftershock incompleteness may be severe.

Figures:
Generate a compact set of useful diagnostic figures:
- M6.9-centered map of the two analysis windows, marking M6.9 and M6.6
- time-distance plot relative to M6.9 with the two 90th-percentile front fits and speeds in the legend
- event-rate and magnitude timeline, with earlier -10 to -2 day activity shown only as context if useful
- convex-hull activated-area comparison for final-2-day foreshock versus first-0.5-day aftershock windows. Draw the retained 90% event points, the closed hull outline, and a transparent hull fill for both windows using common axis limits. Include either a third overlay panel or an inset that directly overlays the blue foreshock hull and red aftershock hull, so the envelope expansion is visually obvious. Annotate hull area, equivalent radius, along-axis span, and across-axis span. Mark M6.9 and M6.6.
- Mc / b-value diagnostic for the final-2-day window, and optional early-aftershock b-value only as exploratory

Outputs:
Do not write a narrative report.
Save figures, CSV tables, ordered hull-vertex tables, and a compact summary JSON/CSV with the key measurements and method settings.
Include an output validation table that explicitly checks:
- the ordered hull-vertex table exists and contains vertices for both windows
- the activated-area figure exists
- the activated-area figure was generated from hull vertices, not only from retained scatter points

Important:
Do not claim slow slip, aseismic slip, triggering, fluid migration, or stress transfer from the catalog alone.
Treat migration speed, convex-hull area, b-value, and event-rate changes as screening diagnostics.
Keep the analysis simple and focused on the two-window M6.9 comparison.
"""

if __name__ == "__main__":

    run_name = "04_1A_M1_migration"
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
