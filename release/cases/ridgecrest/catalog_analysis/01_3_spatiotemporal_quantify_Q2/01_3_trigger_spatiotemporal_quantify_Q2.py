import os
import sys
sys.path.append("<REPO_ROOT>/")
from seismoagent.runing import run_seismoagent

user_request = """
You are a senior seismologist. 
Your objective is to investigate the triggering mechanism of the M7.1 earthquake by the M6.4 earthquake within the Ridgecrest earthquake sequence.
with a focus on comparing two fault-oriented regions, by characterizing the spatiotemporal patterns of seismic rate evolution:
    1) characterize whether the activation of the two regions following the Mw 6.4 is synchronous or exhibits systematic temporal offsets
    2) identify and quantify systematic differences in the seismic rate evolution and triggering behavior.
    3) identify the spatial inhomogeneity and temporal ordering of the triggering process inside each region after the Mw 6.4 mainshock,
       in order to assess whether fault activation is spatially coherent or directionally evolving

## 1. Data Sources
- Catalog Path: `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/TRACE_ridgecrest_relocated.csv`
    - the first row is the name of the columns: `event_time,latitude,longitude,depth_km,magnitude`
- Main-shock events Path: `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/main_shock_events.csv`
    - Mainshock64: magnitude 6.4
    - Mainshock71: magnitude 7.1
- Fault Path: `<REPO_ROOT>/examples/ridgecrest/data/faults/ridgecrest_surface_faults.json`
    - the format is a list of lists of [longitude, latitude]

## 2. Fault-direction-based regions
- Time Window: [catalog start time, mainshock71]
- Use a fixed, precomputed corridor definition.
- Use three fixed analysis domains:
    - All region: the full pre-Mw 7.1 catalog window in the study area.
    - Region A: the Mw 6.4-associated NE-SW/conjugate fault-direction corridor.
        - axial strike: 39.0 degrees
        - centerline start in lon/lat: longitude = -117.635877, latitude = 35.555024
        - centerline end in lon/lat: longitude = -117.463113, latitude = 35.729199
        - total corridor width: 8.0 km, i.e., 4.0 km half-width on each side of the centerline
    - Region B: the Mw 7.1-associated NW-SE/Little Lake fault-direction corridor.
        - axial strike: 138.0 degrees
        - centerline start in lon/lat: longitude = -117.735813, latitude = 35.897499
        - centerline end in lon/lat: longitude = -117.362520, latitude = 35.559488
        - total corridor width: 8.0 km, i.e., 4.0 km half-width on each side of the centerline
- Also define two fixed circular near-mainshock diagnostic domains. These are not replacements for Region A and Region B; they are local diagnostic neighborhoods for comparing activation near the two mainshock epicentral areas:
    - Mw6.4-neighborhood: circle centered at the Mw 6.4 mainshock epicenter, radius = 10 km.
    - Mw7.1-neighborhood: circle centered at the Mw 7.1 mainshock epicenter, radius = 10 km.
    - Define the circles using horizontal epicentral distance in kilometers after projecting events and mainshocks to a local metric coordinate system.
    - Events may belong to both a fault-direction corridor and a near-mainshock circular domain; keep these labels as independent diagnostic masks rather than mutually exclusive assignment classes.
- Visualization and region-definition diagnostics
    - Plot a fixed-corridor assignment map in the local metric coordinate system and/or lon/lat coordinates:
        - overlay mapped fault traces
        - plot Region A and Region B centerlines
        - plot the 8 km-wide corridor boundaries for Region A and Region B
        - plot the 10 km-radius Mw6.4-neighborhood and Mw7.1-neighborhood circular boundaries
        - overlay catalog events colored by time since the Mw 6.4 mainshock
        - mark events by assignment class: Region A, Region B and unassigned
        - overlay and label the Mw 6.4 and Mw 7.1 mainshocks
    - Plot across-centerline distance distributions for Region A and Region B:
        - x-axis: perpendicular distance to assigned centerline
        - mark the 4 km corridor half-width
        - use this figure to verify that the fixed corridors cover the assigned seismicity
    - Plot along-strike coordinate distributions for Region A and Region B:
        - x-axis: along-strike distance along the assigned centerline
        - mark the finite centerline endpoints
        - use this figure to verify that the centerline spans cover the main event clouds
    - Plot unassigned events on a separate diagnostic map to confirm that unassigned events are not concentrated in the key Mw 6.4-to-Mw 7.1 corridor.
    - Save a compact CSV summary containing assignment counts, unassigned fraction, median and 95th-percentile across-centerline distance, and along-strike coordinate range for Region A and Region B.

## 3. Seismic rate and Energy release statistic
1. Seismic rate and Energy release construction and statistical representation
    - Construct 30-minute and hourly seismic rates and Energy release for the entire catalog and each region over the time window
2. Bayesian change-point extraction based on both seismic rate and Energy release
    - Is there exist new triggered events (after the Mw 6.4 mainshock) contributed to the occurrence of the M7.1 earthquake?
3. Visualization
    - Plot seismic-rate time series for All region, Region A and Region B on the same time axis, with Mw 6.4 and Mw 7.1 marked by vertical reference lines.
    - Plot rate-change diagnostics and detected change points for All region, Region A and Region B.
    - Plot cumulative event counts for Region A and Region B together, including both raw cumulative counts and normalized cumulative fractions, so that timing differences are not confused with different total event numbers.
    - Plot energy-release time series and cumulative energy for All region, Region A and Region B, with detected change points marked and labeled.
    - Plot a separate near-mainshock neighborhood comparison for the Mw6.4-neighborhood and Mw7.1-neighborhood:
        - seismic-rate time series
        - cumulative event counts and normalized cumulative fractions
        - first sustained activity time, strongest rate-change time and peak-rate time
        - use this diagnostic to test whether the Mw7.1-neighborhood activates later than the Mw6.4-neighborhood
    - Plot normalized cumulative energy fractions for Region A and Region B as a secondary diagnostic, because raw energy can be dominated by a small number of larger events.
    - Plot Region A versus Region B rate ratio or rate difference through time as an optional diagnostic for identifying which fault-direction system dominates during each time interval.
    - Save a compact CSV summary of first event time, first sustained activity time, strongest rate-change time, peak-rate time, cumulative count and cumulative energy for All region, Region A and Region B.

## 4. Grid seismicity rate statistics and analysis
1. Split region A and B into grids of 0.5 km x 0.5 km cells
2. Construct 30-minute and hourly seismicity rates for each cell
3. Visualization
    - Plot cumulative seismicity-count maps for Region A and Region B in local metric coordinates, with the fixed centerlines and corridor boundaries overlaid:
        - color: cumulative seismicity count
        - zero-count cells should be shown in grey
    - Plot spatial first-activation-time maps for Region A and Region B as key diagnostic evidence:
        - use the 0.5 km grid cells inside each fixed corridor
        - color each activated cell by first activation time since the Mw 6.4 mainshock in hours
        - use the same color scale for Region A and Region B, ideally 0 to the Mw 7.1 occurrence time
        - draw the fixed corridor polygon/centerline in black
        - overlay and label the Mw 6.4 and Mw 7.1 mainshocks
        - make a two-panel A/B comparison figure so that Region A near-synchronous activation and delayed activation near the Mw 7.1 area in Region B can be visually compared directly
        - make an additional two-panel circular-neighborhood first-activation map for the Mw6.4-neighborhood and Mw7.1-neighborhood, using the same color scale, to directly compare local activation around the two mainshock epicenters
        - also save the underlying cell-level first-activation table with cell center lon/lat, along-strike coordinate, across-strike coordinate, distance to Mw6.4, distance to Mw7.1, event count and first activation time
    - Use time-versus-along-strike heatmaps as the primary internal-ordering visualization for each region:
        - x-axis: time since the Mw 6.4 mainshock
        - y-axis: along-strike distance along the corresponding fixed centerline
        - color: seismicity rate or event count per cell/bin
        - keep zero-count cells as a light grey background
    - Plot first-activation time versus along-strike distance for each region:
        - show individual cells or along-strike bins
        - report whether activation time suggests monotonic migration, delayed patch activation, or spatially heterogeneous activation
    - Save an along-strike binned summary table for each region, including bin center, event count, first activation time, peak-rate time and cumulative energy.
    - Optionally include secondary heatmaps sorted by distance to the Mw 6.4 and Mw 7.1 mainshocks, but these should not replace the along-strike heatmaps as the primary evidence.

## 5. Computational and software requirements
- Process each major analytical step independently and generate figures and outputs for that step.
- Use parallel computation (up to 64 cores) for computationally intensive tasks, such as seismic rate construction, grid seismicity rate statistics, etc.
- Display progress information (e.g., progress bars or logs) during long computations whenever possible.
"""

if __name__ == "__main__":

    run_name = "01_3_trigger_spatiotemporal_quantify_Q2-v1"
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
