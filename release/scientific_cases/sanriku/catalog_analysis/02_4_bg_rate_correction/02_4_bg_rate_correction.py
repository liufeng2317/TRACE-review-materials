import os
import sys
sys.path.append("<REPO_ROOT>/")
from seismoagent.runing import run_seismoagent

user_request = """
You are an earthquake scientist and data-analysis agent.

Current task:
Build a regional background-rate model for the Aomori earthquake catalog.

Goal:
Use the long-term raw JMA/Hi-net catalog as the background-rate reference and the relocated/filtered active-period catalog as the fine-scale active-period dataset. Determine whether the 2025-2026 Aomori activity is exceptional relative to long-term background seismicity, and identify which regions, depth ranges, and time periods show significant rate anomalies.

Data folder:
"<CASE_ROOT>/data"

Catalogs:
- Long-term raw catalog:
  data/Snet_catalog_20200101_20260522_filter.csv
  time range: 2020-01-01 to 2026-05-22
  role: long-term background-rate reference

- Active-period relocated/filtered catalog:
  data/Snet_catalog_20251001_20260501_filter.csv
  time range: 2025-10-01 to 2026-05-01
  role: fine-scale active-period spatial, depth, and regional rate analysis

Context files:
- catalog/main_earthquake.csv
- source_mechanism/Snet_mecha.csv
- stations/station.sta

Important data rule:
Do not merge the long-term raw catalog and the active-period relocated catalog as homogeneous products.
Because the long-term catalog has broader spatial coverage, define a common analysis region from the active-period relocated catalog, with a small buffer if needed, and filter the long-term catalog to this same spatial mask before any long-term vs active-period rate comparison.
Full-region long-term statistics may be reported only as supplementary context, not as the primary basis for anomaly claims.

Main tasks:

1. Catalog crosswalk and common-region definition
Compare the two catalogs over their overlapping period and define the common analysis region.

Check:
- schema and field meanings
- spatial coverage and common spatial mask
- magnitude range and magnitude type
- depth range
- event counts by magnitude threshold
- M4+ and M5+ event matching where feasible
- magnitude, location, and depth differences
- event retention rate from raw catalog to relocated/filtered catalog
- completeness magnitude Mc by catalog and period where feasible

Clearly state which magnitude thresholds are reliable for long-term comparison.
Prioritize M>=3, M>=4, and M>=5 for cross-catalog background-rate analysis.
Use M>=1.2 only within the active-period relocated catalog unless completeness is explicitly justified.

2. Long-term background-rate reference
Using the spatially filtered 2020-2026 raw catalog, estimate long-term seismicity rates for:
- common analysis region
- M1-M3 local region
- M2 local region
- M2 outer-band region
- broader control regions

Use magnitude thresholds where feasible:
- M>=3, M>=4, M>=5, M>=6, and M>=Mc if reliable

Compute:
- monthly or rolling-window rates
- percentile ranking of the 2025-10 to 2026-05 active period
- expected background counts for comparable windows
- long-term anomaly levels for M4+, M5+, and M6+ activity

3. Active-period regional rate decomposition
Using the 2025-10 to 2026-05 relocated/filtered catalog, analyze short-term rate changes within:
- M1-M3 local region
- M2 near-field region
- M2 outer-band region
- broader background/control region

Use multiple time scales where feasible:
- daily, weekly, 14-day, monthly

Use magnitude thresholds:
- M>=1.2, M>=2, M>=3, M>=4, M>=5

Also analyze depth-stratified rates:
- 0-30 km, 30-60 km, >60 km

Mark M1, M2, and M3 times on relevant rate plots.

4. Background-rate interpretation and controls
Evaluate:
- whether the 2025-2026 active period is anomalous relative to the 2020-2026 background within the common analysis region
- whether anomalies are regional or localized
- whether the M1-M3 local region remains unusual after regional background correction
- whether M2 outer-band activity exceeds regional background expectations
- whether the three mainshock regions are synchronized within a common regional rate pulse
- whether any apparent local anomaly can be explained by burst-like background seismicity or analysis-window choices

Use simple controls where useful:
- random windows from the long-term catalog
- same-duration windows outside mainshock intervals
- shifted windows within the active period
- spatial control regions
- bootstrap confidence intervals for rate anomalies

Figures:
Generate a compact set of high-value diagnostic figures, not exhaustive plots:
- long-term regional rate time series with the active period highlighted
- active-period rate time series with M1/M2/M3 marked
- regional rate comparison among M1-M3 local, M2 near-field, M2 outer-band, and control regions
- spatial rate-anomaly map
- depth-stratified rate evolution
- long-term percentile comparison for active-period windows
- background-rate evidence matrix

Final report:
Provide a concise scientific report answering:
- Is the 2025-2026 Aomori active period exceptional relative to the 2020-2026 background within the common analysis region?
- Which regions and depth ranges show the strongest rate anomalies?
- Are the anomalies localized or part of a broader regional rate pulse?
- Does the M1-M3 local region remain anomalous after background correction?
- Can M2 outer-band activity be explained by regional background-rate changes?
- Which observations remain statistically interesting enough for later physical follow-up?

Important:
Do not treat rate anomalies as proof of triggering, slow slip, fluid migration, stress transfer, or fault interaction.
Separate long-term background anomalies from active-period rate pulses.
Separate catalog-level statistical support from physical mechanism interpretation.
Use long-term raw catalog results as background-rate reference, not as fine-scale relocated structural evidence.
"""
if __name__ == "__main__":

    run_name = "02_4_bg_rate_correction"
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
