# Goal

Investigate the spatiotemporal evolution of the Ridgecrest earthquake sequence using the relocated observational catalog, with specific focus on whether seismicity between the Mw 6.4 and Mw 7.1 mainshocks shows synchronous activation or staged/cascade-like triggering.

## Planning Assumptions

- Use only the provided observational catalog and mainshock reference table; no model data are needed.
- `TRACE_ridgecrest_relocated.csv` is the primary event catalog with required fields: `event_time`, `latitude`, `longitude`, `depth_km`, `magnitude`.
- `main_shock_events.csv` contains the authoritative Mw 6.4 and Mw 7.1 event times/epicenters used to define both analysis windows and map overlays.
- Time calculations should be performed relative to the Mw 6.4 origin time, and event times must be parsed in a timezone-consistent datetime format before filtering.
- Spatial gridding requested in kilometers requires projecting longitude/latitude to a local Cartesian system before assigning 0.5 km × 0.5 km cells; do not bin directly in degrees.
- “No color interpolation within each time bin” means categorical/discrete colors by fixed time intervals, not a continuous colormap over individual event times.
- The onset-time definition must be reproducible and physically interpretable; use an explicit sustained-activation rule based on the 30-minute local count series and require persistence beyond a single isolated bin.
- Major outputs should be produced as independent analysis stages, but data dependencies should flow from catalog preprocessing to visualization and onset mapping.
- Parallelization up to 64 cores is appropriate for per-cell time-series construction and onset detection over the spatial grid; merged outputs must be validated as non-empty before considering a task successful.

## Analysis Plan

### Task 1 — Build the event-analysis table and time windows
- Task description
  - Read the relocated catalog and mainshock reference file, validate schema, identify the Mw 6.4 and Mw 7.1 rows, derive relative times, and prepare analysis subsets for downstream tasks.
- Required data sources
  - `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/TRACE_ridgecrest_relocated.csv`
  - `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/main_shock_events.csv`
- Parameter selection strategy
  - Identify mainshock64 as the row with magnitude 6.4 and mainshock71 as the row with magnitude 7.1 from `main_shock_events.csv`.
  - Define analysis windows exactly as requested:
    - Short window: `[mainshock64, mainshock64 + 4 hours]`
    - Long window: `[mainshock64, mainshock71]`
  - Add columns to the catalog:
    - `time_rel_sec_from_64`
    - `time_rel_hr_from_64`
    - projected coordinates in km relative to a local origin near the catalog center or Mw 6.4 epicenter
    - optional event IDs generated from row index for traceability
- Constraints
  - Confirm both mainshocks are present and that Mw 7.1 occurs after Mw 6.4.
  - Remove or flag events outside the relevant windows only in derived subsets, not in the master table.
  - Validate that the long-window subset is non-empty and includes events up to but not after the Mw 7.1 origin time.
  - Keep original longitude/latitude values unchanged for plotting overlays.
- Key outputs
  - Clean master event table with relative-time and projected-coordinate fields
  - `ridgecrest_window_short_64_to_4h.csv`
  - `ridgecrest_window_long_64_to_71.csv`
  - `mainshock_reference_checked.csv`
  - basic validation table with event counts, time extents, spatial extents, and projected-grid bounds

### Task 2 — Time-colored spatial point-cloud assessment after Mw 6.4
- Task description
  - Generate two epicenter maps to visually test whether post-Mw 6.4 seismicity exhibits temporal layering in space.
- Required data sources
  - Task 1 short- and long-window event tables
  - checked mainshock reference table
- Parameter selection strategy
  - For the short window, assign each event to 30-minute bins relative to Mw 6.4:
    - [0, 0.5 h), [0.5, 1.0 h), …, [3.5, 4.0 h]
  - For the long window, assign each event to 2-hour bins relative to Mw 6.4, continuing until the Mw 7.1 time.
  - Use one discrete color per time bin and a categorical legend listing bin edges in hours from Mw 6.4.
  - Plot epicenters in longitude–latitude coordinates; overlay the Mw 6.4 and Mw 7.1 epicenters with distinct markers and labels.
  - If event density is high, preserve all points but allow small marker size and optional plotting order by time bin so earlier bins are not completely obscured.
- Constraints
  - Do not use continuous time interpolation or gradient coloring within bins.
  - Use exactly the requested time windows and bin widths.
  - Keep the same geographic extent for comparable maps where practical; if extents differ, report the chosen bounds explicitly.
  - Validate that every plotted event is assigned to exactly one bin and that empty bins are still represented in the legend or recorded in metadata.
  - Parallelize bin assignment and plotting data preparation if needed, but scientific success requires the final non-empty figures and bin-count table.
- Key outputs
  - `time_colored_epicenters_64_to_4h`
  - `time_colored_epicenters_64_to_71`
  - per-bin event-count table for each window
  - optional supplemental figure: projected x–y version of the same maps for geometric comparison

### Task 3 — Onset-time mapping of post-Mw 6.4 activation
- Task description
  - Discretize the region, construct per-cell local seismicity-rate time series, define reproducible activation onset times, and map onset timing to evaluate synchronous versus staged triggering between Mw 6.4 and Mw 7.1.
- Required data sources
  - Task 1 long-window event table
  - checked mainshock reference table
- Parameter selection strategy
  - Define the study region from the spatial extent of events in `[mainshock64, mainshock71]`.
  - Use projected coordinates to build a regular 0.5 km × 0.5 km grid spanning that extent.
  - For each cell, count events in fixed 30-minute bins from Mw 6.4 to Mw 7.1 to form the local rate series.
  - Restrict onset analysis to cells with enough activity to support interpretation; record inactive/insufficient-data cells separately rather than forcing onset times everywhere.
  - Use a sustained-activation rule such as:
    - compute the 30-minute count series for each cell;
    - define a low-activity baseline from the earliest portion of the sequence or from zero-count expectation within the observation window;
    - onset time is the first 30-minute bin where counts exceed a stated activation threshold and remain elevated for at least a minimum persistence window (for example, activity in at least 2 of the next 3 bins, or nonzero counts sustained over multiple adjacent bins).
  - Choose the exact thresholding logic from catalog-driven diagnostics:
    - inspect the distribution of per-cell counts,
    - prefer a simple count-based rule that is reproducible and robust to sparsity,
    - keep one final rule for all cells.
  - In parallel, compute:
    - per-cell total events,
    - first-event time,
    - onset time by sustained rule,
    - delay from Mw 6.4 in hours,
    - optional uncertainty/quality flag based on persistence strength.
- Constraints
  - The final onset definition must not be a purely visual choice; it must be explicitly documented and applied uniformly across the grid.
  - Do not infer onset from a single isolated event if the stated objective is sustained increase in local seismicity rate.
  - Preserve cells with no activation as missing/undefined onset rather than assigning late times artificially.
  - Validate merged results after parallel execution:
    - non-empty grid table,
    - consistent number of cells,
    - onset times within `[0, mainshock71-mainshock64]`,
    - no duplicate cell IDs.
  - Because onset patterns may be sensitive to sparsity, include a comparison table between:
    - all occupied cells,
    - cells meeting the minimum-activity criterion,
    - cells with defined sustained onset.
- Key outputs
  - `grid_definition_0p5km.csv`
  - `cell_rate_timeseries_30min.csv` or partitioned per-cell tables plus merged summary
  - `cell_onset_time_summary.csv`
  - `cell_activity_quality_flags.csv`
  - onset-time spatial map colored from earlier/darker to later/lighter, with Mw 6.4 and Mw 7.1 epicenters overlain
  - companion figure showing occupied-but-no-onset or insufficient-data cells distinctly
  - summary table of onset-time statistics by distance and by broad spatial sector relative to the Mw 6.4–Mw 7.1 trend

### Task 4 — Diagnostic interpretation products focused on the Mw 6.4 to Mw 7.1 triggering question
- Task description
  - Produce compact diagnostics that distinguish synchronous activation from staged migration and make the trigger interpretation testable.
- Required data sources
  - Outputs from Tasks 2 and 3
  - mainshock reference table
- Parameter selection strategy
  - Define a mainshock-connecting axis from Mw 6.4 to Mw 7.1 and its perpendicular axis in projected coordinates.
  - For each occupied grid cell with defined onset time, compute:
    - along-strike distance relative to Mw 6.4,
    - cross-strike distance,
    - distance to Mw 6.4,
    - distance to Mw 7.1.
  - Compare onset time against these spatial coordinates to test for directional migration toward the Mw 7.1 hypocenter.
  - Summarize whether early onsets cluster near a limited zone and whether later onsets fill in toward other fault segments.
- Constraints
  - This task is diagnostic and should use the same onset-time definition finalized in Task 3; do not redefine onset here.
  - Interpretation must be based on observed spatial organization, not inferred rupture physics beyond what the catalog supports.
  - If no coherent onset gradient is found, preserve that outcome explicitly rather than forcing a cascade interpretation.
- Key outputs
  - scatter plot of onset time versus along-strike distance
  - scatter plot of onset time versus distance to Mw 7.1
  - optional along-strike binned median-onset profile
  - concise machine-readable summary table indicating whether observations are more consistent with:
    - synchronous activation,
    - staged/cascade-like activation,
    - mixed or inconclusive behavior