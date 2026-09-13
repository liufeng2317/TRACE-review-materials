import os
import sys
sys.path.append("<REPO_ROOT>/")
from seismoagent.runing import run_seismoagent

user_request = """
You are a senior seismologist and earthquake-catalog analyst.
Your objective is to compute fixed-window b-value contrasts for the Ridgecrest sequence in a simple, reproducible and diagnostic way.

# Scientific question
How do b-values in the future Mw 7.1 hypocentral region compare with the Mw 6.4 hypocentral control region, the full interevent region and the long-term regional background?
Report the contrast direction, magnitude, uncertainty and reliability without assuming the Mw 7.1 region must be lower or higher.

# Data sources
- Interevent catalog: `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/TRACE_ridgecrest_relocated.csv`
  - columns: `event_time,latitude,longitude,depth_km,magnitude`
- Background catalog: `<REPO_ROOT>/examples/ridgecrest/data/catalog_longterm/catalog_2year_background_before_64.csv`
  - map columns: `datetime` -> `event_time`, `latR` -> `latitude`, `lonR` -> `longitude`, `depR` -> `depth_km`, `mag` -> `magnitude`
- Main shocks: `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/main_shock_events.csv`

# Time windows
- Background: use the background catalog only as one larger-area regional b-value reference. For the primary reported background reference, use fixed `Mc = 1.5` so it is directly comparable with the main interevent fixed-Mc results. Also report the catalog-derived Mc result as a QC/supporting value.
- Full interevent: Mw 6.4 origin time to Mw 7.1 origin time, excluding the two mainshocks.
- Early/late interevent: split the interevent period at the fixed separator event M5.37 at `2019-07-05T11:07:52.830000Z`. Use this event only as a boundary marker and exclude it from all b-value estimates.
- Do not perform sliding-window or time-varying b-value analysis.

# Spatial domains
- Background: one larger Ridgecrest regional domain only. Do not subdivide background into Mw 6.4/Mw 7.1 local cores.
- Interevent regional reference: full Ridgecrest interevent study region.
- Interevent Mw 6.4 control: cylindrical hypocentral core centered on Mw 6.4.
- Interevent Mw 7.1 target: cylindrical hypocentral core centered on Mw 7.1.
- Primary local radius: 5 km. Radius sensitivity: 4, 5, 6 and 7 km only.
- Project coordinates to a local metric CRS and use horizontal distance for the radius masks. Keep depth in output tables.
- The Mw 6.4 and Mw 7.1 hypocenters are about 12 km apart; the primary 5 km cores do not overlap. Report overlap counts for all sensitivity radii and use exclusive nearest-hypocenter assignment if any sensitivity radius overlaps.

# b-value method
For every requested subset, report total events, Mc, n >= Mc, b-value, bootstrap uncertainty, magnitude range and reliability.
- Estimate Mc by maximum curvature.
- Also compute conservative Mc per temporal window: `Mc_conservative = max(subset Mc, full-window Mc)`.
- For the main fixed-window comparison, compute fixed-Mc results with `Mc = 1.5` for both interevent subsets and the larger-area background reference. Treat fixed `Mc = 1.5` as the primary value for cross-window/domain comparison; report automatic/conservative Mc results as QC/supporting diagnostics.
- Use the Aki-Utsu maximum-likelihood estimator with magnitude-bin correction:
  `b = log10(e) / (mean(M) - Mc + delta_M / 2)`.
- Infer `delta_M` from magnitude precision.
- Use >=1000 bootstrap samples when feasible and report median, 16th-84th percentile and standard deviation.

# Reliability rules
Compute b-values whenever at least two events remain above Mc, but classify reliability by `n >= Mc`:
- `n >= 100`: robust for primary diagnostics.
- `50 <= n < 100`: usable but moderately uncertain.
- `30 <= n < 50`: exploratory; report the value, but discuss it only if bootstrap intervals and sensitivity tests are consistent.
- `n < 30`: highly unreliable; report only for completeness.
Treat these thresholds as reporting labels rather than sharp scientific boundaries, and interpret estimates near a threshold with extra caution.
Do not use highly unreliable subsets to support conclusions. Interpret any observed low b-value only as consistent with localized stress loading, not as a deterministic precursor.

# Required outputs
Generate CSV tables for:
- cleaned catalog summaries and separator event metadata,
- unified aggregate b-values by window, domain, radius and Mc mode,
- b-value contrasts: Mw7.1-Mw6.4, Mw7.1-full region and late-early within each core,
- radius sensitivity and overlap diagnostics.

Generate figures for:
1. Interevent map with Mw6.4/Mw7.1 hypocenters and 5 km cores; optionally show 4, 6 and 7 km sensitivity circles.
2. Magnitude-frequency distributions with catalog-derived Mc, fixed `Mc = 1.5`, and fitted Gutenberg-Richter lines.
3. Main fixed-window b-value comparison using fixed `Mc = 1.5`.
   - This must explicitly show the 5 km Mw6.4 and Mw7.1 core b-values for three windows: full interevent, pre-separator, and post-separator.
   - The separator is the M5.37 event at `2019-07-05T11:07:52.830000Z`; exclude this event from b-value estimates and use it only to divide pre/post windows.
   - Plot Mw6.4 and Mw7.1 cores side by side within each window, with bootstrap uncertainty intervals and `n >= Mc` labels.
   - Include the larger-area background reference as a separate horizontal line or separate panel, not mixed in a way that obscures the pre/post core comparison.
4. Contrast plot with uncertainty intervals.
5. Radius sensitivity for interevent local cores only.
6. Time-magnitude completeness diagnostic for the interevent catalog.
7. Overlap diagnostic for 4, 5, 6 and 7 km radii.

# Computational requirements
- Keep the workflow reproducible and save all scripts, tables, figures and metadata.
- Use parallel computation up to 64 cores where useful.
- Show progress logs for long bootstrap computations.
- Use `seismostats` where appropriate for Mc, b-value, a-value calculation.
"""

if __name__ == "__main__":

    run_name = "01_4_trigger_b_value_Q0-v1"
    output_dir = "<REPO_ROOT>/examples/ridgecrest/catalog_analysis/run"

    run_seismoagent(
        request=user_request,
        run_name=run_name,
        output_dir=output_dir,
        disable_refinement=False,
        max_refinement_rounds=3,
        enable_trajectory=True,
        # resume=os.path.join(output_dir, run_name)
    )