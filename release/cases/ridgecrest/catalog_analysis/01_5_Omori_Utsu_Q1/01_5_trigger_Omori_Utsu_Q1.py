import os
import sys
sys.path.append("<REPO_ROOT>/")
from seismoagent.runing import run_seismoagent

user_request = """
You are a senior seismologist and earthquake-catalog analyst.
Your primary objective is to perform an Omori-Utsu comparison for the Ridgecrest interevent period, using the Mw 7.1 fault-zone entire area and its northern/southern subdivisions.
The main scientific question is whether the northern part of the Mw 7.1 fault-zone shows systematically smaller p-values than the southern part later in the interevent period.

## 1. Data Sources
- Catalog Path: `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/TRACE_ridgecrest_relocated.csv`
    - the first row is the name of the columns: `event_time,latitude,longitude,depth_km,magnitude`
- Main-shock events Path: `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/main_shock_events.csv`
    - Mainshock64: magnitude 6.4
    - Mainshock71: magnitude 7.1
- Primary magnitude threshold:
    - Use `M >= 3.0` as the primary threshold for the main analysis.
    - You may report lower-threshold or `Mc`-based results only as optional secondary sensitivity tests after the primary `M >= 3.0` analysis is complete.

## 2. Primary analysis domains
- Time Window: `(mainshock64, mainshock71)`
- Use a fixed Mw 7.1 fault-zone corridor as the primary Omori-Utsu analysis zone.
- Define the Mw7.1-fault-zone entire area with these fixed geometric parameters:
    - axial strike: 138.0 degrees
    - centerline start in lon/lat: longitude = -117.735813, latitude = 35.897499
    - centerline end in lon/lat: longitude = -117.362520, latitude = 35.559488
    - total corridor width: 8.0 km, i.e., 4.0 km half-width on each side of the centerline
- Inside this entire area, define:
    - Mw7.1-fault-zone northern area: events north of latitude = 35.72 degrees N
    - Mw7.1-fault-zone southern area: events south of latitude = 35.72 degrees N
- Use these three domains as the primary comparison:
    - Entire area
    - Northern area
    - Southern area
- Split-line sensitivity:
    - repeat the north/south partition for 35.70, 35.72 and 35.74 degrees N
    - treat 35.72 degrees N as the primary partition
    - use the neighboring split lines only as a robustness check, not as the main figure

## 3. Domain-definition diagnostics
- Project events and the corridor to a local metric coordinate system.
- Plot a domain-assignment figure that shows:
    - all interevent events colored by time since Mw 6.4
    - the Mw 7.1 fault-zone centerline and corridor boundary
    - the 35.72 degrees N split line
    - the events assigned to the northern area and southern area
    - the Mw 6.4 and Mw 7.1 mainshocks
- Save a compact CSV summary with domain counts for:
    - Entire area
    - Northern area
    - Southern area

## 4. Primary Omori-Utsu fitting design
1. Time reference:
   - Define `T = 0` as the origin time of the Mw 6.4 mainshock.
   - All interevent times are measured relative to this reference.

2. Periods to analyze:
   - Use cumulative periods that end at fixed times after Mw 6.4.
   - Use a fixed set of cumulative comparison periods with these specific endpoints:
       - 0.30 day
       - 0.50 day
       - 0.68 day
       - 0.732 day
       - 0.85 day
       - 1.00 day
       - 1.10 day
       - 1.22 day
       - 1.404 day
   - The periods 0.732 day and 1.404 day correspond to the M5.4 and Mw7.1 endpoints, respectively.

3. Rate model and fitting method:
   - For each domain and each cumulative period `[0, t_n]`, use only interevent events with `M >= 3.0` inside that domain and before `t_n`.
   - Fit the primary Omori-Utsu rate model of the form:
       `lambda(t) = K * (c + t)^(-p)`
     using maximum likelihood estimation.
   - Use this shifted Omori-Utsu model as the primary fit for this task.
   - Treat `K` as the rate scale, `c` as the short-time offset in days, and `p` as the decay exponent used for the north/south comparison.
   - Estimate the likelihood over the observed event times in each cumulative window and use the cumulative period endpoint `t_n` as the upper integration bound.
   - Use bounded optimization for `p` and `c` to avoid unconstrained or nonphysical estimates; document the bounds used.
   - Report fitting failures or unconstrained windows explicitly rather than forcing unstable estimates.

4. Uncertainty estimation:
   - Estimate uncertainty in `p` and `c` by bootstrap resampling.
   - Save bootstrap summaries including at least:
       - median `p`
       - 2.5 percentile
       - 97.5 percentile
       - median `c`
       - 2.5 percentile for `c`
       - 97.5 percentile for `c`
   - Also report event counts used in each fit.
   - For the northern area, if `N <= 20`, mark that period as a low-count point for plotting with an open-circle symbol in the main figure.
   - If the southern area has too few events in the earliest periods and the fit does not converge, leave those points missing rather than fabricating values.

## 5. Required outputs
- Save a CSV table for all fitted periods and all three domains with at least:
    - domain label
    - period_days
    - event count
    - success/failure flag
    - fitted `p`
    - fitted `c`
    - fitted `K`
    - bootstrap median `p`
    - bootstrap lower/upper bounds
    - bootstrap median and lower/upper bounds for `c`
    - any low-count/open-circle flag

- Save a CSV or JSON metadata file with:
    - Mw 6.4 time
    - Mw 7.1 time
    - M5.4 separator period = 0.732 day
    - final period = 1.404 day
    - corridor geometry and split latitude

## 6. Required figures
### (A) Main two-panel figure
Create a two-panel figure with the required layout and styling described below.

Panel a:
- x-axis: `Period [day]`
- y-axis: `p value`
- plot the three primary domains together:
    - Entire area in grey
    - Northern area in blue
    - Southern area in red
- use filled circles with vertical uncertainty bars for ordinary points
- use open blue circles for northern-area points with `N <= 20`
- draw vertical lines at:
    - 0 day
    - 0.732 day
    - 1.404 day
- label the panel as `a`
- make this the primary figure of the workflow

Panel b:
- use the entire-area result for the final 1.404 day period
- plot observed seismicity rate `lambda [day^-1]` versus time since Mw 6.4 on log-log axes
- overlay the fitted Omori-Utsu rate curve
- annotate the fitted `p` with uncertainty and report the fitted `c`
- annotate the period `1.404 [day]`
- label the panel as `b`

### (B) Domain-assignment diagnostic figure
- plot the fixed corridor, split line, events, and mainshocks
- make sure the figure clearly shows which events belong to the entire/north/south domains

### (C) Optional robustness figures
- If useful, add a split-line sensitivity summary for 35.70 / 35.72 / 35.74 degrees N.
- Keep this secondary; do not replace the main two-panel figure with it.

## 7. Interpretation rules
- The primary conclusion must be based on the Entire vs North vs South comparison.
- Do not replace the primary comparison with Region A, Mw6.4/Mw7.1 circles, or all-region diagnostics in this task.
- Focus on whether:
    - north and south are similar in earlier cumulative periods
    - north tends to lower p-values later in the interevent period
    - south remains comparable to or higher than the entire-area reference later in the interevent period
- Do not over-interpret windows with very low counts.
- If the trend is weak or inconsistent, report that honestly.

## 8. Computational requirements
- Process each major step independently and save outputs for that step.
- Use parallel computation for bootstrap uncertainty estimation if helpful.
- Display progress information during long computations whenever possible.
"""

if __name__ == "__main__":

    run_name = "01_5_trigger_Omori_Utsu_Q1-v2"
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
