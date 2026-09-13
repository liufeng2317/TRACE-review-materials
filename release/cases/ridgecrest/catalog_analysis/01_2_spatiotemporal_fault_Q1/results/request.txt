
You are a senior seismologist. 
Your objective is to investigate the spatiotemporal evolution of the earthquakes for the Ridgecrest earthquake sequence, spetial attention to the trigger mechanism from Mw 6.4 to Mw 7.1 mainshock.
The main questions are:
    - Is the triggered earthquakes along the fault direction?
    - Is the triggered earthquakes along the fault direction changing over time?
    - Is the triggered earthquakes cover all the fault direction simultaneously or evolving over time?

## 1. Data Sources
- Catalog Path: `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/TRACE_ridgecrest_relocated.csv`
    - the first row is the name of the columns: `event_time,latitude,longitude,depth_km,magnitude`
- Main-shock events Path: `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/main_shock_events.csv`
    - Mainshock64: magnitude 6.4
    - Mainshock71: magnitude 7.1
- Fault Path: `<REPO_ROOT>/examples/ridgecrest/data/faults/ridgecrest_surface_faults.json`
    - the format is a list of lists of [longitude, latitude]

## 2. Time-sliced spatial maps x fault distribution
1. Time Window and Time Intervals Definition:
    - Analysis window: [mainshock64, mainshock71]
    - Subdivision into two temporal stages:
        - Stage 1: [mainshock64, mainshock64 + 4 hours], 30-minute interval
        - Stage 2: [mainshock64 + 4 hours, mainshock71], 2 hour interval

2. Plot a series of figures showing the spatiotemporal evolution of the earthquakes after Mw 6.4 mainshock:
- Generate a sequence of spatial maps to visualize temporal changes in seismic density
- Each figure contains 8 subplots, arranged in a 2 x 4 grid
- all subplots must:
    - Events in the time window: scatter plot with brighter color
    - Events before the time window: scatter plot in silver with higher transparency
    - overlay the fault lines (top level of the figure)
    - overlay the epicenter of the Mw 6.4 and Mw 7.1 mainshocks (top level of the figure)
    - use identical spatial extents
    - Do not plot the colorbar

3. Plot a figure comparing the spatial distribution before and after the Mw 7.1 mainshock:
    - Before Mw 7.1 mainshock: [mainshock64, mainshock71]
    - After Mw 7.1 mainshock: [mainshock71, mainshock71 + 2 days]
    - overlay the fault lines (top level of the figure)
    - overlay the epicenter of the Mw 6.4 and Mw 7.1 mainshocks (top level of the figure)

## 3. Nearest fault distance statistic and analysis
1. Time window definition: [mainshock64, mainshock71]
2. Calculate the nearest fault distance for each earthquake
3. Plot the nearest fault distance distribution
4. Plot the nearest fault distance distribution change over time


## 4. Computational and software requirements
- Process each major analytical step independently and generate figures and outputs for that step.
- Use parallel computation (up to 64 cores) for computationally intensive tasks, such as spatial visualization, nearest fault distance calculation etc.
- Display progress information (e.g., progress bars or logs) during long computations whenever possible.
