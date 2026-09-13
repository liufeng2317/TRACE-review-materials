# Goal
Investigate the spatiotemporal evolution of the 2019 Ridgecrest earthquake sequence from the Mw 6.4 mainshock to 10 hours after the Mw 7.1 mainshock, with special focus on possible directional/structural triggering between the two mainshocks using sector-based directional Ripley’s K/L analysis, time-direction heatmaps, and representative map-plus-rose visualizations.

## Planning Assumptions
- Observation data are sufficient and should be used exclusively: relocated earthquake catalog, two mainshock reference events, and mapped surface-fault geometry.
- The primary analysis should be implemented in one cohesive task script so that catalog loading, time-window construction, pair counting, directional K/L computation, QC, parallel execution, and figure generation share the same validated intermediates.
- Catalog schema is fixed as `event_time, latitude, longitude, depth_km, magnitude`; `event_time` must be parsed as UTC datetime.
- The surface-fault JSON is a plain nested list of `[longitude, latitude]` polyline coordinates, not GeoJSON; it must be loaded with standard JSON parsing and plotted directly.
- Time window for the main analysis is fixed by the user: `[mainshock64, mainshock71 + 10 hours]`.
- Base interval for the directional heatmap is fixed by the user: 30 minutes.
- Directional sectors are fixed by the user: 5° bins over `[0°, 360°)`, giving 72 sectors.
- The user requested a directional Ripley statistic at a characteristic scale `r`, but did not provide `r`; therefore `r` must be selected from data-driven nearest-neighbor and inter-event distance diagnostics and then fixed for all time intervals for comparability. A small set of candidate radii should be computed first, but one final characteristic `r` must be chosen before the main heatmap and rose products.
- Because the user requested “normalized Ripley’s K-function” and heatmap coloring by L-function, the plan should compute sectoral `K(r, θ)` and transform to a directional `L(r, θ)` anomaly relative to complete spatial randomness and/or the interval-wise directional mean; the exact normalization must be kept consistent across all intervals.
- Geographic coordinates must be projected to a local Cartesian system before pair-distance and azimuth calculations; lon/lat should still be retained for map figures.
- Inter-event vector azimuth should be computed in projected coordinates and wrapped to `[0°, 360°)`.
- Edge effects can bias Ripley statistics; a single correction strategy must be applied consistently across all intervals. If robust polygon-based correction is impractical, the analysis should explicitly use a study-window mask or convex-hull/alpha-shape approximation and report intervals with insufficient support.
- Sparse intervals can produce unstable directional K estimates; minimum-event thresholds per 30-minute interval and per 4-hour visualization window must be enforced, with windows below threshold flagged or omitted from directional interpretation.
- Parallel execution up to 64 cores should be used for interval-wise pair-statistic computation and any heavy figure assembly loops; progress logging should report completed intervals/windows and skipped low-count intervals.
- Success evidence for the main task script is not just completion of interval jobs; required merged outputs must include a non-empty interval-level directional statistics table and the requested figures.

## Analysis Plan

### Task 1 — Build the analysis-ready Ridgecrest sequence dataset and fixed study windows
- Task description:
  - Load the relocated catalog, the two mainshock reference rows, and the surface-fault geometry.
  - Restrict the catalog to the user-defined analysis window from Mw 6.4 origin time to Mw 7.1 origin time plus 10 hours.
  - Construct all required time-window definitions for the heatmap and representative panels.
- Required data sources:
  - `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/TRACE_ridgecrest_relocated.csv`
  - `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/main_shock_events.csv`
  - `<REPO_ROOT>/examples/ridgecrest/data/faults/ridgecrest_surface_faults.json`
- Parameter selection strategy:
  - Parse `event_time` as timezone-aware UTC.
  - Identify the Mw 6.4 and Mw 7.1 rows from the mainshock CSV by magnitude.
  - Define 30-minute contiguous intervals spanning `[t64, t71 + 10 h]`.
  - Define 8 representative 4-hour windows approximately uniformly across the full analysis window.
  - Define 8 representative post-Mw 6.4 windows using 30-minute intervals nearest to and after Mw 6.4, spaced approximately uniformly through the early post-6.4 period up to but not beyond Mw 7.1.
  - Define 8 representative pre-Mw 7.1 windows using 30-minute intervals before Mw 7.1, spaced approximately uniformly through the late pre-7.1 period.
- Constraints:
  - Do not alter the user-specified global analysis window or 30-minute base interval.
  - Preserve all events with valid time, latitude, longitude, depth, and magnitude; only rows with missing required fields should be removed.
  - Store both lon/lat and projected x/y coordinates for downstream use.
- Key outputs:
  - Filtered analysis catalog table.
  - Mainshock metadata table with Mw 6.4 and Mw 7.1 origin times and epicenters.
  - Time-interval index table for all 30-minute bins.
  - Window-definition table for the three figure families.
  - QC summary table with event counts per interval/window.
  - Basic overview figure: sequence cumulative count and magnitude-versus-time with mainshock markers.

### Task 2 — Preprocess geometry, project coordinates, and select the characteristic Ripley scale
- Task description:
  - Convert earthquake and fault coordinates into a common local projected system for metric distance/azimuth calculations.
  - Diagnose appropriate characteristic spatial scales and choose the single `r` used in the main directional heatmap and rose diagrams.
- Required data sources:
  - Filtered catalog and mainshock table from Task 1.
  - Surface-fault geometry JSON.
- Parameter selection strategy:
  - Use a local projection centered on the Ridgecrest sequence centroid or the midpoint between the two mainshocks.
  - Compute inter-event nearest-neighbor distances and selected pair-distance distributions using either all events in the full window or a statistically representative subset if needed for speed.
  - Evaluate candidate radii tied to observed clustering scales; recommended candidates are quantiles or robust central values of nearest-neighbor and short-range pair distances.
  - Choose one characteristic `r` that is:
    - large enough to capture short-range clustering/alignment,
    - small enough to avoid washing out directional structure,
    - supported by adequate pair counts in most 30-minute intervals.
- Constraints:
  - Do not infer `r` from plotting convenience; it must come from data diagnostics.
  - Keep the final chosen `r` fixed across all intervals and representative windows.
  - If interval pair counts at the chosen `r` are too sparse in many bins, choose the next larger candidate and document the decision.
- Key outputs:
  - Projected event coordinates table.
  - Projected fault polyline dataset for overlay.
  - Radius-diagnostic table with candidate `r` values and interval support metrics.
  - Scale-selection figure(s): nearest-neighbor histogram/CDF and short-range pair-distance diagnostic plot.
  - Final parameter record including selected `r`, sector width, and event-count thresholds.

### Task 3 — Compute sector-based directional Ripley K/L statistics for each 30-minute interval
- Task description:
  - For every 30-minute interval, compute directional pair statistics within radius `r`, bin by 5° azimuth sectors, normalize to obtain sector-based `K(r, θ)`, convert to directional `L(r, θ)`, and assemble the interval-by-direction matrix used for interpretation.
- Required data sources:
  - Projected event coordinates and interval table from Tasks 1–2.
- Parameter selection strategy:
  - For each interval:
    - subset events within the interval;
    - skip or flag intervals below a minimum event threshold;
    - compute all unordered event pairs with separation `≤ r`;
    - compute pair azimuths in projected x/y;
    - bin azimuths into 72 sectors of width 5° over `[0°, 360°)`;
    - calculate directional pair counts and normalize by interval event density and sector angle fraction.
  - Convert `K(r, θ)` to `L(r, θ)` using one consistent transform for all intervals.
  - For highlighting dominant/secondary directions, identify local maxima in sectoral `L(r, θ)` after optional circular smoothing over neighboring bins.
- Constraints:
  - Use the same normalization, projection, radius, and sector definitions for all intervals.
  - Include explicit handling for intervals with low counts, zero qualifying pairs, or unstable estimates.
  - Parallelize across time intervals up to 64 cores.
  - Log progress for interval completion, skipped intervals, and pair-count summaries.
  - Do not treat per-interval files as final success unless a merged non-empty time-direction matrix is produced.
- Key outputs:
  - Interval-level directional statistics table with fields such as interval start/end, event count, pair count, sector center, `K`, `L`, normalized anomaly, and dominance rank.
  - Merged 2D matrix for heatmap plotting: time × direction.
  - Companion QC table with skipped intervals, pair-support metrics, and uncertainty flags.
  - Optional summary table of dominant and secondary directions by interval.

### Task 4 — Quantify temporal evolution relevant to Mw 6.4-to-Mw 7.1 triggering
- Task description:
  - Extract interpretable directional-evolution metrics from the interval-wise `L(r, θ)` matrix to evaluate whether preferred clustering directions migrate, rotate, intensify, or align with mapped faults and the Mw 6.4–Mw 7.1 connection geometry.
- Required data sources:
  - Directional statistics outputs from Task 3.
  - Mainshock epicenters from Task 1.
  - Surface-fault geometry from Task 2.
- Parameter selection strategy:
  - Track through time:
    - dominant azimuth,
    - secondary azimuth,
    - anisotropy strength (`max L - mean/median L` or similar),
    - angular separation between dominant direction and:
      - local mapped surface-fault strike families,
      - the great-circle or projected azimuth from Mw 6.4 epicenter to Mw 7.1 epicenter.
  - Partition the sequence into at least three physically relevant phases:
    - immediate post-Mw 6.4,
    - inter-mainshock buildup,
    - immediate post-Mw 7.1.
- Constraints:
  - Keep this as a derived analysis from Task 3 outputs rather than a separate detection workflow.
  - Do not claim causality directly from directional alignment; frame outputs as temporal-spatial consistency tests for triggering hypotheses.
  - Ensure directional comparisons use the same azimuth convention as the Ripley analysis.
- Key outputs:
  - Time series table of dominant/secondary directions and anisotropy strength.
  - Mainshock-connection azimuth table and fault-strike comparison summary.
  - Derived figure: temporal trajectories of dominant direction and anisotropy with vertical markers at Mw 6.4 and Mw 7.1.

### Task 5 — Generate the time-direction heatmap and sequence-level summary figures
- Task description:
  - Produce the principal time-direction heatmap and supporting summary plots that emphasize directional transitions from the Mw 6.4 sequence toward the Mw 7.1 rupture period.
- Required data sources:
  - Merged `L(r, θ)` matrix and derived metrics from Tasks 3–4.
  - Mainshock metadata from Task 1.
- Parameter selection strategy:
  - Heatmap:
    - x-axis: 30-minute interval centers;
    - y-axis: sector centers from 0° to 360°;
    - color: sector-based `L(r, θ)` or a centered directional anomaly at the selected `r`.
  - Overlay:
    - vertical lines for Mw 6.4 and Mw 7.1 origin times;
    - optional traces/markers for dominant and secondary directions through time.
  - Add companion panels for event counts per interval and anisotropy strength to distinguish physical changes from count-driven instability.
- Constraints:
  - Use the same fixed `r` selected in Task 2.
  - Clearly mark intervals that were skipped or under-supported.
  - Highlight both dominant and secondary directional branches only where support exceeds the QC threshold.
- Key outputs:
  - Main heatmap figure for directional `L(r, θ)` evolution.
  - Companion QC figure with interval event counts and pair counts.
  - Summary figure combining heatmap and dominant-direction trajectory.

### Task 6 — Generate the three requested 2×4 map-plus-polar-rose figure families
- Task description:
  - Produce the three figure sets requested by the user:
    1. whole analysis window represented by 8 uniformly spaced 4-hour windows,
    2. 8 representative 30-minute windows after Mw 6.4,
    3. 8 representative 30-minute windows before Mw 7.1.
- Required data sources:
  - Window-definition table from Task 1.
  - Projected/unprojected event and fault geometry from Tasks 1–2.
  - Directional Ripley statistics from Task 3.
- Parameter selection strategy:
  - For each selected window:
    - subset events in that window;
    - draw epicentral map in lon/lat with fault traces in background;
    - color events by time relative to Mw 6.4 for the whole-window and post-6.4 figures;
    - color events by time relative to Mw 7.1 for the pre-7.1 figure if clearer, while retaining consistency with the user’s requested relation when specified;
    - overlay Mw 6.4 and Mw 7.1 epicenters;
    - compute or extract window-level sectoral `K/L` at the same `r`;
    - place a polar rose inset at top-right showing directional clustering intensity.
  - Keep subplots in chronological order.
- Constraints:
  - Maintain a consistent map extent across all 8 panels within each figure family.
  - Maintain a consistent rose scaling across panels within each figure family.
  - If a selected window is too sparse, keep the panel but label it as low support rather than silently replacing it.
  - Parallelize panel preparation where useful, but validate that each complete 2×4 figure is non-empty and chronologically ordered.
- Key outputs:
  - Figure: `ridgecrest_whole_window_8panel_map_rose`
  - Figure: `ridgecrest_post64_8panel_map_rose`
  - Figure: `ridgecrest_pre71_8panel_map_rose`
  - Window-level statistics table listing event counts, pair counts, dominant direction, secondary direction, and anisotropy per panel.

### Task 7 — Export reusable analysis tables and validation diagnostics
- Task description:
  - Save compact machine-readable products needed for downstream checking and interpretation.
- Required data sources:
  - Outputs from Tasks 1–6.
- Parameter selection strategy:
  - Export:
    - cleaned filtered catalog with interval IDs,
    - interval definitions,
    - selected representative windows,
    - directional K/L statistics by interval and sector,
    - dominant-direction summary by interval,
    - window-level rose statistics,
    - scale-selection and QC summaries.
- Constraints:
  - Keep filenames explicit and tied to content.
  - Include enough metadata in each table header or sidecar record to recover the selected `r`, sector width, projection, and thresholds.
  - Final validation must confirm that all requested figure families and the merged directional statistics table exist and are non-empty.
- Key outputs:
  - `ridgecrest_interval_directional_ripley_stats.csv`
  - `ridgecrest_interval_direction_summary.csv`
  - `ridgecrest_representative_window_stats.csv`
  - `ridgecrest_scale_selection_summary.csv`
  - `ridgecrest_interval_qc_summary.csv`

### Task 8 — Interpretation-oriented checks focused on the Mw 6.4 to Mw 7.1 transition
- Task description:
  - Add targeted checks that directly support the user’s trigger-mechanism objective using already computed products.
- Required data sources:
  - Outputs from Tasks 3–7.
- Parameter selection strategy:
  - Compare directional statistics across three targeted epochs:
    - first few hours after Mw 6.4,
    - final hours before Mw 7.1,
    - first few hours after Mw 7.1.
  - Test whether dominant directions before Mw 7.1 increasingly align with:
    - the Mw 6.4-to-Mw 7.1 inter-mainshock azimuth,
    - major mapped fault trends intersecting the rupture corridor,
    - spatial migration from the Mw 6.4 cluster toward the Mw 7.1 hypocentral region.
  - Summarize these as temporal consistency indicators, not causal proof.
- Constraints:
  - Use only observation-derived catalog and fault geometry.
  - Do not introduce separate physical stress-transfer modeling, because the user requested a sector-based Ripley workflow rather than Coulomb or dynamic stress modeling.
- Key outputs:
  - Epoch-comparison table of dominant directions and anisotropy.
  - Spatial migration summary figure or panel using event centroids / density peaks by interval.
  - Trigger-focused diagnostic summary tied to the main heatmap and representative roses.