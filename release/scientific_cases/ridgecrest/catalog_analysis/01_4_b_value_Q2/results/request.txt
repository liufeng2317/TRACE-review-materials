
You are a senior seismologist and earthquake-catalog analyst.
Compute spatial b-value diagnostics for the Ridgecrest Mw 6.4-Mw 7.1 interevent period, and compare the future Mw 7.1 hypocentral region with the Mw 6.4 control region.

# Scientific question
Does the interevent catalog show a spatial b-value pattern near the future Mw 7.1 hypocentral/rupture region that is consistent with the Q0/Q1 local b-value results?
Report the pattern, uncertainty and reliability without assuming a predefined anomaly or precursor.

# Data sources
- Interevent catalog: `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/TRACE_ridgecrest_relocated.csv`
  - columns: `event_time,latitude,longitude,depth_km,magnitude`
- Background catalog for regional context only: `<REPO_ROOT>/examples/ridgecrest/data/catalog_longterm/catalog_2year_background_before_64.csv`
- Main shocks: `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/main_shock_events.csv`

# Time windows and markers
- Read Mw 6.4 and Mw 7.1 origin times from the main-shock file.
- Fixed separator event: M5.37 at `2019-07-05T11:07:52.830000Z`.
- Exclude Mw 6.4, Mw 7.1 and the M5.37 separator event from all b-value estimates.
- Analyze:
  1. `full_interevent`: Mw 6.4 to Mw 7.1.
  2. `pre_separator`: Mw 6.4 to M5.37.
  3. `post_separator`: M5.37 to Mw 7.1.
- Use the background catalog only to report a larger-area regional reference b-value.

# Spatial method
Use fixed-radius spatial sampling rather than adaptive rectangular kernels.
- Project events and mainshocks to a local metric coordinate system.
- Build a regular grid over the active interevent region with 0.5-1.0 km spacing.
- At each grid node, use events within a circular horizontal radius.
- Primary radius: 5 km.
- Sensitivity radii: 4, 5, 6 and 7 km.
- Do not use radii larger than 7 km in the main analysis.
- For each node, compute b only if at least 30 events remain above Mc; otherwise report NaN.
- Reliability labels by `n >= Mc`: 30-49 exploratory, 50-99 moderately uncertain, >=100 robust.

# b-value estimation
- Primary maps use fixed `Mc = 1.5` for all spatial nodes and interevent windows.
- Also compute one window-level dynamic Mc for each time window as QC.
- Do not estimate Mc separately at each grid node for the main maps.
- Use the Aki-Utsu maximum-likelihood estimator with magnitude-bin correction:
  `b = log10(e) / (mean(M) - Mc + delta_M / 2)`.
- Infer `delta_M` from magnitude precision.
- Estimate bootstrap uncertainty for valid nodes when feasible, using at least 500 samples.

# Required diagnostics
1. 5 km fixed-Mc map-view b-value maps for `full_interevent`, `pre_separator` and `post_separator`.
   - Use a common color scale.
   - Overlay Mw 6.4, M5.37, Mw 7.1 and 5 km Mw 6.4/Mw 7.1 core circles.
   - Mask no-data nodes.
2. Reliability maps for `n >= Mc`, uncertainty and reliability class.
3. `post_separator - pre_separator` difference map where both windows have valid values.
4. Mw 7.1 fault-oriented cross-section or along-strike b-value profile for the post-separator window.
5. 5 km Mw 6.4 and Mw 7.1 core b-values and FMD plots for full, pre- and post-separator windows.
6. Descriptive low-b summary using `b < 0.9` and/or the lowest 20% of valid grid nodes within each window.

# Required outputs
Generate CSV tables for cleaned window catalogs, grid-node b-values, uncertainty, `n >= Mc`, reliability, core FMD summaries, difference-map source data, low-b summaries and validation checks.

Generate figures for spatial b-value maps, reliability maps, the difference map, the Mw 7.1 fault-oriented profile, core FMD comparison and radius sensitivity.

# Interpretation rules
- Use Q2 as spatial support for Q0/Q1, not as an independent precursor claim.
- Treat sparse pre-separator maps as exploratory.
- Interpret low b-values only as consistent with localized stress loading or relatively higher differential stress.
- Do not claim deterministic prediction.

# Computational requirements
- Save scripts, tables, figures and metadata.
- Use parallel computation up to 64 cores where useful.
- Show progress logs for long bootstrap computations.
- Use `seismostats` where appropriate.
