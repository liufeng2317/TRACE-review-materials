
You are a senior seismologist. 
Your objective is to investigate the spatiotemporal evolution of the earthquakes for the Ridgecrest earthquake sequence, spetial attention to the trigger mechanism from Mw 6.4 to Mw 7.1 mainshock.

## 1. Data Sources
- Catalog Path: `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/TRACE_ridgecrest_relocated.csv`
    - the first row is the name of the columns: `event_time,latitude,longitude,depth_km,magnitude`
- Main-shock events Path: `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/main_shock_events.csv`
    - Mainshock64: magnitude 6.4
    - Mainshock71: magnitude 7.1

## 2. Time-Colored spatial point cloud
Visually assess whether seismicity after Mw 6.4 exhibits organized temporal layering in space.

- Prepare the time ranges for analysis:
    - A shorter time window after Mw 6.4: [mainshock64, mainshock64 + 4 hours]
    - A longer time window after Mw 6.4: [mainshock64, mainshock71]

- Scatter plot epicenters in longitude–latitude space for each time range:
    - Color events by their occurrence time relative to Mw 6.4
    - Assign a single color to all events within the same time interval:
        - 30-minute intervals for the shorter time window
        - 2-hour intervals for the longer time window
    - Overlay:
        - Mw 6.4 epicenter
        - Mw 7.1 epicenter
    - Plot requirements:
        - No color interpolation within each time bin

## 3. Onset Time Analysis
Objective:
Identify the aftershock activity after Mw 6.4 using the spatially map of the onset time
    - If activation is synchronous:
        - Colors are spatially mixed
        - No large-scale spatial segregation by time bin
    - If activation is staged or cascade-like:
        - Early time-bin colors cluster in specific regions
        - Later time-bin colors occupy distinct spatial zones
        - Spatially coherent temporal layering emerges
    
1. Spatial discretization
    - The study region is defined by the catalog data within the time window [mainshock64, mainshock71]
    - Discretize the research region into a grid of 0.5 km × 0.5 km cells

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
    
## 4. Computational and software requirements
- Process each major analytical step independently and generate figures and outputs for that step.
- Use parallel computation (up to 64 cores) for computationally intensive tasks, such as spatial visualization, onset time analysis, etc.
- Display progress information (e.g., progress bars or logs) during long computations whenever possible.
