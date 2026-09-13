import os
import sys
sys.path.append("<REPO_ROOT>/")
from seismoagent.runing import run_seismoagent

# scientific question: discover the organized spatiotemporal patterns of the earthquakes after Mw 6.4 and Mw 7.1 mainshocks
user_request = """
You are a senior seismologist. 
Your objective is to investigate the spatiotemporal evolution of the earthquakes for the Ridgecrest earthquake sequence, spetial attention to the trigger mechanism from Mw 6.4 to Mw 7.1 mainshock.

## 1. Data Sources
- Catalog Path: `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/TRACE_ridgecrest_relocated.csv`
    - the first row is the name of the columns: `event_time,latitude,longitude,depth_km,magnitude`
- Main-shock events Path: `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/main_shock_events.csv`
    - Mainshock64: magnitude 6.4
    - Mainshock71: magnitude 7.1

## 2. Time-sliced spatial maps for the whole sequence
Objective: 
To analyze the spatiotemporal evolution of the Ridgecrest earthquake sequence and discover the organized spatiotemporal patterns:
    - The main characteristics of spatiotemporal patterns after Mw 6.4:
        - Is the mainshock triggering one or multiple clusters in a specific direction?
        - Is the cluster moving over time? If so, what is the direction of the movement? If not, is the cluster trigger simultaneously in multiple directions?
    - The main characteristics of spatiotemporal patterns after Mw 7.1
        - Is the direction changing before and after the mainshock? If so, what is the direction of the change? If not, is the direction static?
        - Is the new trigger direction/zone after the mainshock? If so, what is the direction of the new trigger

Plotting tasks:
- Plot a series of figures showing the spatiotemporal evolution of earthquakes over the whole sequence:
    - For the time range [mainshock64, mainshock71 + 1 day]: use a 2-hour interval
    - For the time range [mainshock71 + 1 day, mainshock71 + 5 days]: use a 6-hour interval
    - For each figure, arrange the subplots in a 2 x 4 grid (ordered chronologically).
        - In each panel:
            - Events within the time window: scatter plot with brighter color
            - Events before the time window: scatter plot in silver with higher transparency
            - Overlay the epicenters of Mw 6.4 and Mw 7.1 (when they have already occurred)
        - All subplots must have:
            - The same spatial extent
            - No colorbar
            - Identical color settings

## 3. Spatial Distribution Comparison Before and After the Mainshocks
Objective:
To identify changes in the spatial organization of earthquakes before and after the Mw 6.4 and Mw 7.1 mainshocks, and to assess whether these changes indicate the emergence of organized
    - What are the changes in spatial distribution before and after the Mw 6.4 mainshock?
    - What are the changes in spatial distribution before and after the Mw 7.1 mainshock?
    - Spetial attention to:
        - Is the migration direction changing before and after the mainshock? If so, what is the direction of the change? If not, is the direction static?
        - Is the new trigger direction/zone after the mainshock? If so, what is the direction of the new trigger

Plotting tasks:
- Plot a figure comparing the spatial distribution before and after the Mw 6.4 mainshock (overlay with different colors for before and after):
    - Before Mw 6.4 mainshock: [catalog origin time, mainshock64]
    - After Mw 6.4 mainshock: [mainshock64, mainshock71]
- Plot a figure comparing the spatial distribution before and after the Mw 7.1 mainshock (overlay with different colors for before and after):
    - Before Mw 7.1 mainshock: [mainshock64, mainshock71]
    - After Mw 7.1 mainshock: [mainshock71, mainshock71 + 2 days]

## 4. Time-sliced spatial maps for the post-mainshock64 sequence (most important)
Objective:
To characterize in detail the fine-scale spatiotemporal evolution of seismicity in longitude–latitude space following the Mw 6.4 mainshock.
    - Describe how the spatial distribution of earthquakes evolves in longitude–latitude space after the Mw 6.4 mainshock, with emphasis on local migration, clustering, and geometric changes.

Plotting tasks:
- Plot a series of figures showing the spatiotemporal evolution after Mw 6.4:
    - Use hour-by-hour temporal resolution
    - Each figure contains up to 8 hours of data
    - For each figure, arrange the subplots in a 2 x 4 grid (ordered chronologically).
        - In each panel:
            - Events in the time window: scatter plot with brighter color
            - Events before the time window: scatter plot in silver with higher transparency
            - Overlay the mainshock64 epicenter
        - All subplots must have:
            - The same spatial extent
            - No colorbar
            - Identical color settings

## 5. Computational and software requirements
- Process each major analytical step independently and generate figures and outputs for that step.
- Use parallel computation (up to 64 cores) for computationally intensive tasks, such as spatial visualization, etc.
- Display progress information (e.g., progress bars or logs) during long computations whenever possible.
"""

if __name__ == "__main__":

    run_name = "01_1_trigger_spatiotemporal_Q1-v1"
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