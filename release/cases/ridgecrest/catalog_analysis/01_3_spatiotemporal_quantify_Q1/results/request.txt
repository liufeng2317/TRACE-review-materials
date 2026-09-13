
You are a senior seismologist. 
Your objective is to investigate the spatiotemporal evolution of the earthquakes for the Ridgecrest earthquake sequence, spetial attention to the trigger mechanism from Mw 6.4 to Mw 7.1 mainshock.

## 1. Data Sources
- Catalog Path: `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/TRACE_ridgecrest_relocated.csv`
    - the first row is the name of the columns: `event_time,latitude,longitude,depth_km,magnitude`
- Main-shock events Path: `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/main_shock_events.csv`
    - Mainshock64: magnitude 6.4
    - Mainshock71: magnitude 7.1
- Fault Path: `<REPO_ROOT>/examples/ridgecrest/data/faults/ridgecrest_surface_faults.json`
    - the format is a list of lists of [longitude, latitude]

## 2. Sector-based Ripley’s K-function analysis

1. Time Window and Time Intervals Definition
- Analysis window: [mainshock64, mainshock71+10 hours]
- Time Intervals: 30 minutes

2. Compute sector-based directional Ripley’s K-functions for each time interval.
    - For each time interval:
        1. Identify all event pairs with inter-event distance ≤ r.
        2. Compute the orientation angle of each inter-event vector.
        3. Bin orientations into sectors of 5° over [0°, 360°).
        4. For each sector, compute the normalized Ripley’s K-function using only event pairs within that angular range.
        5. Store K(r, θ) as the directional clustering statistic for the current time interval.

3. Visualize the Time-Direction Heatmap:
- X-axis: time intervals
- Y-axis: azimuthal direction (0–360 degrees)
- Color: sector-based Ripley’s L-function evaluated at a characteristic scale r
- Other features:
    - Highlight dominant and secondary seismic clustering directions and their temporal transitions.
    - Overlay the mainshock64 and mainshock71 epicenters timelines.

4. Visualize the Polar Rose Diagrams
- One figure for the whole time windows
    - Split the time windows into 8 representative time windows (each time window is 4 hours), spaced approximately uniformly through time
    - Arrange the subplots in a 2 × 4 grid (ordered chronologically).
    - In each panel:
        - Plot the events in longitude-latitude space, colored by the event time relative to the mainshock64
        - Generate a polar rose diagram showing directional clustering intensity derived from sector-based Ripley’s K-function on the "top right" of the panel.
        - overlay the mainshock64 and mainshock71 epicenters
    
- One figure for the time nearest to the mainshock64
    - Select 8 representative windows after the mainshock64, time intervals (30 minutes interval), spaced approximately uniformly through time
    - Arrange the subplots in a 2 × 4 grid (ordered chronologically).
    - In each panel:
        - Plot the events in longitude-latitude space, colored by the event time relative to the mainshock64
        - Generate a polar rose diagram showing directional clustering intensity derived from sector-based Ripley’s K-function on the "top right" of the panel.
        - overlay the mainshock64 and mainshock71 epicenters

- One figure for the time nearest to the mainshock71
    - Select 8 representative windows before the mainshock71, time intervals (30 minutes interval), spaced approximately uniformly through time
    - Arrange the subplots in a 2 × 4 grid (ordered chronologically).
    - In each panel:
        - Plot the events in longitude-latitude space, colored by the event time relative to the mainshock71
        - Generate a polar rose diagram showing directional clustering intensity derived from sector-based Ripley’s K-function on the "top right" of the panel.
        - overlay the mainshock64 and mainshock71 epicenters

## 3. Computational and software requirements
- Process each major analytical step independently and generate figures and outputs for that step.
- Use parallel computation (up to 64 cores) for computationally intensive tasks, such as spatial visualization, sector-based Ripley’s K-function calculation etc.
- Display progress information (e.g., progress bars or logs) during long computations whenever possible.
