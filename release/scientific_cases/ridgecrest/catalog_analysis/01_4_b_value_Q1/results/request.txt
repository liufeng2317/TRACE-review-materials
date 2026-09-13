
You are a senior seismologist and earthquake-catalog analyst.
Your objective is to compute time-varying b-value evolution only within the Mw 6.4–Mw 7.1 interevent period in a simple, reproducible and diagnostic way.

# Scientific question
Within the Mw 6.4–Mw 7.1 interevent period, how did b-values evolve with time in the future Mw 7.1 hypocentral region compared with the Mw 6.4 hypocentral control region?
Report the direction, timing, uncertainty and reliability of the temporal changes without assuming any predefined trend.

# Data sources
- Interevent catalog: `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/TRACE_ridgecrest_relocated.csv`
  - columns: `event_time,latitude,longitude,depth_km,magnitude`
- Main shocks: `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/main_shock_events.csv`

# Time window and markers
- Analyze only events from the Mw 6.4 origin time to the Mw 7.1 origin time, excluding the two mainshocks.
- Use the fixed intermediate separator event M5.37 at `2019-07-05T11:07:52.830000Z`.
- Mark this separator event time in all time-series figures and report its time, magnitude, location, depth and hours since Mw 6.4. Remove the separator event itself from the analysis catalog before constructing any sliding event windows, so it is not included in any b-value estimate.
- Mark the Mw 7.1 origin time as the endpoint.
- Do not analyze the long-term background catalog in Q1; background b-values are only a regional reference handled by Q0.

# Spatial domains
- Mw 6.4 control core: cylindrical hypocentral region centered on Mw 6.4.
- Mw 7.1 target core: cylindrical hypocentral region centered on Mw 7.1.
- Primary local radius: 5 km.
- Optional radius sensitivity: 4, 5, 6 and 7 km, but the main time-varying comparison should use 5 km.
- Project coordinates to a local metric CRS and use horizontal distance for the radius masks. Keep depth in output tables.
- The Mw 6.4 and Mw 7.1 hypocenters are about 12 km apart; the 5 km cores do not overlap. Report overlap counts for sensitivity radii and use exclusive nearest-hypocenter assignment if any sensitivity radius overlaps.

# Time-varying b-value method
Use sliding event windows, not fixed time bins, so each b-value estimate has comparable sample size.
- Primary sliding window: N = 100 events, step = 20 events.
- If a core has too few events for N = 100 in part of the sequence, also provide an exploratory N = 50, step = 10 result and label it clearly.
- For each sliding window, record start time, end time, median/center time, hours since Mw 6.4, event count and magnitude range.
- Compute b-values using both:
  1. dynamic Mc from maximum curvature within the sliding window,
  2. fixed `Mc = 1.5` for direct comparison with Q0 fixed-window results.
- Use the Aki-Utsu maximum-likelihood estimator with magnitude-bin correction:
  `b = log10(e) / (mean(M) - Mc + delta_M / 2)`.
- Infer `delta_M` from magnitude precision.
- Use bootstrap uncertainty for each window; use >=500 bootstrap samples per window, or >=1000 if computationally feasible.

# Reliability rules
For each sliding-window estimate, report `n >= Mc` and reliability:
- `n >= 100`: robust.
- `50 <= n < 100`: usable but moderately uncertain.
- `30 <= n < 50`: exploratory; report the value, but discuss it only if bootstrap intervals and sensitivity tests are consistent.
- `n < 30`: highly unreliable; show only for completeness.
Treat these thresholds as reporting labels rather than sharp scientific boundaries, and interpret estimates near a threshold with extra caution.
Do not use highly unreliable windows to support conclusions. Interpret any observed low b-value only as consistent with localized stress loading, not as a deterministic precursor.

# Required outputs
Generate CSV tables for:
- cleaned interevent catalog and mainshock/intermediate-event metadata,
- per-window b-values for Mw 6.4 and Mw 7.1 5 km cores,
- optional radius-sensitivity time-varying b-values,
- temporal contrasts: `b_Mw7.1_core - b_Mw6.4_core` matched by nearest center time,
- pre-separator and post-separator summary statistics for each core, computed from sliding-window estimates whose center times fall before or after the separator,
- reliability and Mc diagnostics for every window.

Generate figures for:
1. Interevent map with Mw6.4/Mw7.1 hypocenters, 5 km cores and the fixed separator event.
2. Primary event-window time-series comparison for the 5 km cores using fixed `Mc = 1.5`: plot Mw6.4 core and Mw7.1 core b-values as two colored curves against hours since Mw6.4, with bootstrap uncertainty bands, event-window center times on the x axis, the fixed M5.37 separator shown as a vertical dashed line, and the Mw7.1 endpoint shown as a vertical dotted line. This figure should directly show whether the two cores have similar or different temporal b-value evolution before and after the separator.
3. Time-varying b-value curves for Mw6.4 and Mw7.1 5 km cores using dynamic Mc, with the same time axis, event markers and uncertainty-band style as the primary fixed-Mc figure.
4. Time-varying contrast curve `b_Mw7.1_core - b_Mw6.4_core` with uncertainty, plus pre/post separator summary levels if supported by reliable windows.
5. Mc and n>=Mc diagnostic curves for each core.
6. Optional radius-sensitivity panel for 4, 5, 6 and 7 km.

All time-series figures must mark the fixed separator event and the Mw7.1 endpoint. The separator event is a visual/time boundary only and must not be included in any sliding-window b-value estimate.

# Computational requirements
- Keep the workflow reproducible and save all scripts, tables, figures and metadata.
- Use parallel computation up to 64 cores where useful.
- Show progress logs for long bootstrap computations.
- Use `seismostats` where appropriate for Mc, b-value, a-value calculation.
