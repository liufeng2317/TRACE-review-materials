
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

## 2. Spatial Kernel Density Estimation Migration Analysis 
Objective:
To assess the spatial evolution mechanism of the aftershock cluster from Mw 6.4 to Mw 7.1 mainshock.
    - Is the aftershock clusterred at the alongstrike/corner/intersection/complex fault zones?
    - Whether the seismic culster transfer to the Mw 7.1 is progressive spatial focusing, or progressive spatial spreading or bifurcation (spatial defocusing)?

1. Time Window and Time Intervals Definition:
- Analysis window: [mainshock64, mainshock71]
- Subdivision into two temporal stages:
    - Stage 1: [mainshock64, mainshock64 + 4 hours], 30-minute interval
    - Stage 2: [mainshock64 + 4 hours, mainshock71], 2 hour interval

2. Spatial Kernel Density Estimation
- Perform 2D kernel density estimation in geographic coordinates (latitude–longitude) for each time interval.
- Use a fixed KDE bandwidth across all intervals to ensure temporal comparability.
- Use a consistent spatial grid and identical spatial extent for all KDE maps.

3. Visualization of Density Evolution
- Generate a sequence of KDE maps to visualize temporal changes in seismic density:
- Each figure contains 8 subplots, arranged in a 2 x 4 grid
- all subplots must:
    - use identical spatial extents
    - use an identical KDE bandwidth
    - share a consistent color scale to allow direct comparison
    - overlay the epicenter of the Mw 6.4 and Mw 7.1 mainshocks (at the top level)
    - overlay the fault points (at the top level)
    - Do not plot the colorbar

4. Hotspot Tracking (Qualitative)
- For each time interval, identify the primary density maximum (hotspot).
- Trace the temporal evolution of hotspot locations for Stage 1 and Stage 2
- Plot two figures showing hotspot migration paths for each stage.
    - overlay the fault points (at the top level)
    - overlay the epicenter of the Mw 6.4 and Mw 7.1 mainshocks (at the top level)

## 3. Geometric Morphological Evolution of the Seismic Point Cloud
Objective:
To evaluate whether the spatial envelope of seismicity during the inter-mainshock period exhibits:
    - Progressive contraction toward the Mw 7.1 rupture zone (geometric focusing),
    - Progressive expansion or lateral spreading (geometric defocusing), or
    - Multi-lobed or fragmented morphological evolution suggestive of spatially heterogeneous triggering.

1. Time window definition: [mainshock64, mainshock71], 1 hour interval
2. Geometric Envelope Construction:
- For each time interval:
    - Compute the convex hull of the seismic point cloud.
    - Compute the alpha-shape (with a fixed alpha parameter) to capture concave structural features.
3. Visualization of Envelope Evolution
- Generate two figures:
    - One showing the time evolution of convex hull boundaries.
    - One showing the time evolution of alpha-shape boundaries.
    - In each figure:
        - Plot the geometric envelopes from all time intervals in the same spatial frame.
        - Use color to encode time relative to the Mw 6.4 mainshock (e.g., early = cool colors, late = warm colors).
        - Overlay the epicenters of the Mw 6.4 and Mw 7.1 mainshocks (at the top level)
        - Overlay the fault points (at the top level)
        - Do not fill polygons; only plot boundary curves to avoid occlusion.

## 4. Computational and software requirements
- Process each major analytical step independently and generate figures and outputs for that step.
- Use parallel computation (up to 64 cores) for computationally intensive tasks, such as spatial visualization, geometric envelope calculation, KDE calculation, etc.
- Display progress information (e.g., progress bars or logs) during long computations whenever possible.
