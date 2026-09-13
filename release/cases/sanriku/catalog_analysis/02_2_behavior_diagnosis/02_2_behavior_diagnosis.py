import os
import sys
sys.path.append("<REPO_ROOT>/")
from seismoagent.runing import run_seismoagent

user_request = """
You are an earthquake scientist and data-analysis agent.

Task:
Diagnose the possible sequence behavior around M1, M2, and M3 in the Aomori earthquake catalog. The focus of this stage is to characterize each mainshock-centered sequence.

Scientific motivation:
The Aomori sequence contains three large earthquakes-clusters and multiple M4-M6 events within a short time span. 
The goal is to describe how seismicity evolved before and after each mainshock, identify the most plausible behavior modes for each sequence, and separate local sequence behavior from broader regional activation signals.

Data:
Use the project data folder:
"<CASE_ROOT>/data"

Primary inputs:
- `catalog/Snet_catalog_relocate_250930_260501.csv`
- `catalog/main_earthquake.csv`

Context inputs:
- `source_mechanism/Snet_mecha.csv`
- `stations/station.sta`

Core analysis:

1. Build a mainshock-referenced event table
For each event and each mainshock, compute relative time, epicentral distance, depth difference, distance band, and whether the event is the mainshock-like event. Use a practical tolerance to identify the mainshock-like event.

2. Visualize short-window sequence morphology (specific window)
Create diagnostic figures for visual comparison of the M1, M2, and M3 short-window sequence morphology.

Generate `magnitude_time_distance_pm7d_100km.png` as a 3x2 subplot figure:
- rows: M1, M2, M3;
- left column: magnitude versus relative time within +/-7 days and <=100 km;
- right column: distance to mainshock versus relative time for the same events;
- color points by distance band: 0-30 km, 30-60 km, 60-100 km;
- scale marker size by magnitude;
- highlight M4+ events with a black edge;
- mark the mainshock-like event with a star;
- draw vertical line at relative time 0 and horizontal reference lines for M4/M5 on magnitude panels and 30/60 km on distance panels.

Generate `m4plus_sequence_views_pm7d_100km.png` as a second 3x2 subplot figure:
- rows: M1, M2, M3;
- left column: M4+ magnitude versus relative time;
- right column: M4+ distance versus relative time, colored by magnitude;
- use the same +/-7 day and <=100 km window;
- exclude the mainshock-like event from supporting statistics but show it as a reference marker when useful.

Generate `prepost_magnitude_distance_counts_pm7d_100km.png` as a supporting summary figure, not the primary behavior-classification figure:
- compare pre/post magnitude-bin counts for each mainshock;
- compare pre/post distance-band counts for each mainshock;
- annotate M4+, M5+, and M6+ totals where possible;
- use this figure to summarize magnitude-bin and near-field versus outer-band contributions, not to diagnose swarm-like organization by itself.
- Do not use this figure alone to infer sequence type, swarm-like behavior, or triggering style. Use it only as a summary of pre/post magnitude and distance-band changes.

Generate `m4_m5_distance_band_contribution_pm7d_100km.png` to make the distance structure of moderate and large events explicit:
- show M4+ and M5+ counts by distance band for M1, M2, and M3;
- include both raw counts and normalized fractions or percentages;
- use this figure to compare whether moderate/large events are near-field dominated or distributed across 30-60 km and 60-100 km.
- Do not treat distance-band concentration alone as evidence for swarm, cascade, or migration. Interpret this figure together with magnitude hierarchy, time ordering, and event-chain structure.

3. Compute quantitative matched-window metrics

For each mainshock-cluster, compute matched pre/post statistics for ±7, ±14, and ±25 days using:
- cumulative radii: <=30 km, <=60 km, <=100 km;
- distance bands: 0-30 km, 30-60 km, 60-100 km.

Save complete metric tables for all time windows and spatial definitions, including M4+/M5+/M6+ counts, rates, post/pre ratios, magnitude-bin counts, largest events, magnitude-dominance gaps, companion-event counts, and distance-band contributions.

For visualization, do not generate separate figures for every window and spatial definition. Generate a curated set of comparison figures across M1, M2, and M3:
- pre/post magnitude-bin and distance-band summary;
- M4+/M5+ distance-band contribution figure with raw counts and normalized fractions;
- magnitude-dominance and companion-event summary;
- sensitivity heatmaps across time windows and radii;
- one optional robustness figure if ±14d or ±25d reveals a distinct pattern.

Use tables for exhaustive metrics and figures for high-level comparison.

4. Add depth and mechanism context
Summarize depth distributions for each mainshock-centered sequence, with separate summaries for M4+ and M5+ events where useful. Use focal mechanisms as contextual evidence where coverage is available, especially for checking whether events within a sequence share a similar structural domain.

5. Diagnose non-mutually-exclusive behavior dimensions

For each mainshock, evaluate the following evidence dimensions with levels: low, possible, moderate, or strong. These dimensions are evidence axes, not mutually exclusive sequence labels. A single sequence may show multiple behaviors, such as pre-mainshock activation followed by post-mainshock response, compact compound rupture, or local activation embedded in broader regional activity.

Base each score on explicit quantitative metrics from matched-window tables and event lists, not on visual impression alone. For every score, report the key metrics supporting it and the main caveats.

- Aftershock response:
Evaluate the strength of post-mainshock activation using short-window post/pre rate changes, immediate post-mainshock concentration, near-field dominance, and time-dependent decay after the mainshock. This dimension measures post-mainshock response only; it does not imply a clean single-mainshock aftershock sequence. Interpret post/pre ratios together with magnitude hierarchy, companion events, and pre-mainshock activity.

- Magnitude hierarchy and compound-event structure:
Report the magnitude gap between the mainshock and the largest non-mainshock event, gaps among the top-ranked events, the number of companion events within 0.5 and 1.0 magnitude units of the mainshock, and moment-release concentration if feasible. Separately score:
  1) single-mainshock dominance
  2) compact-cascade / compound-sequence evidence
A sequence may have strong post-mainshock activation but weak single-mainshock dominance.

- Swarm-like organization:
Evaluate whether the sequence shows weak single-mainshock dominance, repeated M4+/M5+/M6 events, small magnitude gaps, persistent or multi-peak activity, and behavior not well explained by a single post-mainshock decay. Do not equate swarm-like behavior with a confirmed physical swarm. Short-lived near-source comparable large events may indicate compact cascade, compound rupture, or compact swarm-like activity; distinguish these alternatives using duration, rate peaks, Omori/ETAS behavior, waveform similarity, relocation, and mechanism consistency.

- Foreshock or pre-mainshock activation:
Evaluate M4+/M5+ counts before the mainshock, largest pre-mainshock magnitude, timing and distance of the largest pre-mainshock event, increasing activity toward the mainshock, and whether pre-events are concentrated near the future mainshock or distributed across outer bands. Note whether pre-mainshock events may overlap with another mainshock-centered sequence or broader regional activity.

- Broader regional activation:
Evaluate the fraction and rate of all events and M4+/M5+ events in the 30–60 km and 60–100 km bands, persistence of activity outside the near field, and near-field versus outer-band contributions. Normalize by annulus area and local background rate where feasible. Do not rely only on cumulative-radius counts.

- Radial migration or expansion:
Use distance-time trends, ordered activation of distance bands, M4+ trajectories, and projected distance along relevant directions where useful. A scattered distribution across distance bands is not enough. Report a trend, regression slope, rank correlation, activation-front speed, or explicitly state that no monotonic progression is supported.

- Slow-slip-related candidate behavior:
Use catalog-level indicators only as screening evidence, such as sustained activity, broad spatial distribution, migration-like patterns, depth consistency, or repeated moderate events. Catalog evidence alone cannot establish slow slip. Do not assign moderate or strong support unless there is clear sustained migration-like activity in a plausible structural/depth domain; otherwise classify it only as an external-comparison candidate requiring GNSS, tremor, ocean-bottom pressure, or slow-slip catalog comparison.

If regional prior studies suggest known swarm activity, include swarm-like behavior as a plausible hypothesis to test, but do not assume it by default.

6. Final report:
Write a concise scientific diagnosis that includes:
1. a visual summary of the +/-7 day behavior for M1, M2, and M3;
2. a per-mainshock interpretation using the behavior dimensions above;
3. a compact evidence table showing the behavior-dimension scores and the key metrics supporting each score;
4. a short statement of what should not be over-interpreted from catalog evidence alone;
5. a short list of verification analyses that would be needed to strengthen or reject the candidate behavior interpretations.

7. Notes and Requirements:
Figure Requirements: 
- Nature publishable quality figure
- Figure should be clear and concise, with no unnecessary elements
"""
if __name__ == "__main__":

    run_name = "02_2_behavior_diagnosis"
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
        resume=os.path.join(output_dir, run_name),
        resume_stage="coding",
        resume_coding_step=1
    )
