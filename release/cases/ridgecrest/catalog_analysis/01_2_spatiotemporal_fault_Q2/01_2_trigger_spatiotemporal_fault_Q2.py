import os
import sys
sys.path.append("<REPO_ROOT>/")
from seismoagent.runing import run_seismoagent

# scientific question: discover the organized spatiotemporal patterns of the earthquakes after Mw 6.4 and Mw 7.1 mainshocks

user_request = """
You are a senior seismologist. 
Your objective is to investigate the spatiotemporal evolution of the earthquakes for the Ridgecrest earthquake sequence, spetial attention to the trigger mechanism from Mw 6.4 to Mw 7.1 mainshock.
The main questions are:
    - is the activation of the earthquakes along the fault direction synchronous?
    - is the activation of the earthquakes along the fault direction staged or cascade-like or more complex?

## 1. Data Sources
- Catalog Path: `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/TRACE_ridgecrest_relocated.csv`
    - the first row is the name of the columns: `event_time,latitude,longitude,depth_km,magnitude`
- Main-shock events Path: `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/main_shock_events.csv`
    - Mainshock64: magnitude 6.4
    - Mainshock71: magnitude 7.1
- Fault Path: `<REPO_ROOT>/examples/ridgecrest/data/faults/ridgecrest_surface_faults.json`
    - the format is a list of lists of [longitude, latitude]

## 2. Onset Time Analysis
1. Time Window Definition and Spatial discretization
    - Time Window: [mainshock64, mainshock71]
    - The study region is defined by the fault distribution, enlarge the research region by 5 km in all directions
    - Discretize the research region into a grid of 1 km × 1 km cells
2. Local seismicity rate construction
    - For each grid cell:
        - Count the number of seismic events every 30 minutes
        - Construct the local seismicity rate time series
3. Onset time definition and recording
    - Define a physically interpretable and reproducible activation time for each spatial unit:
        - Based on a sustained increase in the local seismicity rate
    - Record the onset time relative to Mw 6.4 for each spatial unit
4. Spatial mapping of onset time
    - Plot a spatial map where:
        - Each grid cell (or subregion) is colored by its onset time
        - Earlier activation = darker color
        - Later activation = lighter color
    - Overlay:
        - Mw 6.4 epicenter
        - Mw 7.1 epicenter
        - fault points

## 3. Fault-based Activation Sequence Analysis

1. Fault segmentation
   - Discretize each mapped fault polyline into contiguous fault segments of fixed arclength (e.g., 1 km per segment) if longer than the arclength, otherwise keep the original and end points.
   - Optionally enforce additional segmentation at major curvature or strike-change points.
   - Assign a unique line ID and segment ID to each fault segment.

2. Earthquake-to-fault-segment association
   - For each earthquake in the time window [mainshock64, mainshock71]:
       - Compute the minimum distance to all fault segments.
       - Assign the event to its nearest fault segment if the distance is less than 3 km.
       - Events exceeding this distance threshold are excluded from fault-segment–based analysis.

3. Fault-segment–level seismicity time series construction
   - For each fault segment:
       - Construct a seismicity time series using 30-minute bins.
       - Record the cumulative event count and instantaneous seismicity rate.

4. Definition of fault-segment activation time
   - Define a reproducible onset time for each fault segment as:
       - The first time bin in which the seismicity rate exceeds 10 events per hour.
    - Record the activation time relative to the Mw 6.4 mainshock.

5. Visualization of fault-segment activation sequence
   - Plot a fault map where:
       - Each fault segment is colored by its activation time.
       - Earlier activation = darker color; later activation = lighter color.
       - Overlay the Mw 6.4 and Mw 7.1 epicenters.
       - Overlay the events with the activation time (larger alpha, smaller size like 0.1 or 0.2).
    - plot a figure to show the fault-segment activation density vs. time
       - x-axis: time bins
       - y-axis: activated fault-segment count
       - color: activated fault-segment count (or normalized density)
    - plot a figure to show the strike × activation time density map:
        - x-axis: time bins
        - y-axis: strike angle for the activated fault-segment (corrected by the fault orientation)
        - color: activated fault-segment count (or normalized density)

6. Assessment of triggering style
   - Evaluate whether:
       - Fault segments activate nearly simultaneously (system-wide co-activation),
       - Activation propagates progressively along individual faults (intra-fault cascading),
       - Activation jumps across faults or concentrates in geometrically complex zones,
       - The Mw 7.1 rupture initiates on a fault segment that activated anomalously late.


## 4. Computational and software requirements
- Process each major analytical step independently and generate figures and outputs for that step.
- Use parallel computation (up to 64 cores) for computationally intensive tasks, such as spatial visualization, fault backbone preparation, time-distance diagram construction etc.
- Display progress information (e.g., progress bars or logs) during long computations whenever possible.
"""

if __name__ == "__main__":

    run_name = "01_2_trigger_spatiotemporal_fault_Q2-v1"
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