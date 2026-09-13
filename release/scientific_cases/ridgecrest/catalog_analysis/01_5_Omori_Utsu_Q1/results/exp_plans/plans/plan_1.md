# Goal
Perform a primary Omori-Utsu comparison for the Ridgecrest interevent period between the Mw 6.4 and Mw 7.1 mainshocks, using the fixed Mw 7.1 fault-zone corridor and its northern/southern subdivisions, to test whether the northern subdivision shows systematically smaller fitted Omori exponent p than the southern subdivision in later cumulative periods.

## Planning Assumptions
- Use only the provided observation catalog and mainshock metadata; no model data are needed.
- Primary analysis is restricted to the interevent window `(Mw6.4 origin time, Mw7.1 origin time)` and to events with `magnitude >= 3.0`.
- Primary geometry is fixed by the user: corridor centerline from `(-117.735813, 35.897499)` to `(-117.362520, 35.559488)`, strike `138.0°`, total width `6.0 km`, with primary north/south split at latitude `35.72°N`; `35.70°N` and `35.74°N` are robustness-only splits.
- Primary cumulative period endpoints are fixed: `0.30, 0.50, 0.68, 0.732, 0.85, 1.00, 1.10, 1.22, 1.404` days after Mw 6.4.
- Primary rate model is the two-parameter pure power-law Omori form `lambda(t) = K * t^(-p)` fit by maximum likelihood, not the `K-c-p` model.
- Because `t = 0` is singular for the pure power-law model, the likelihood domain must begin at the first observed event time within each fitted window; windows with insufficient events or numerically unstable likelihoods must be marked as failed/unconstrained rather than forced.
- Bootstrap uncertainty must report at least median p, 2.5 percentile, and 97.5 percentile; for northern-domain windows with `N <= 20`, mark low-count status for open-circle plotting.
- Keep the workflow in one primary task script so that geometry definition, event assignment, fitting, bootstrap estimation, validation, and immediate scientific outputs remain coupled and consistent.

## Analysis Plan

### Task 1 — Build the interevent catalog subset and fixed domain assignments
- Task description:
  - Read the relocated catalog and the two-row mainshock file.
  - identify the Mw 6.4 and Mw 7.1 mainshocks from `main_shock_events.csv`.
  - Compute time since Mw 6.4 for every catalog event in days.
  - Restrict to the interevent window strictly between Mw 6.4 and Mw 7.1.
  - Project all interevent events and corridor endpoints into a local metric coordinate system.
  - Construct the fixed Mw 7.1 fault-zone corridor and assign events to:
    - entire corridor
    - northern subdomain (`lat > 35.72`)
    - southern subdomain (`lat < 35.72`)
  - Repeat north/south assignment for sensitivity split latitudes `35.70` and `35.74`.
- Required data sources:
  - `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/TRACE_ridgecrest_relocated.csv`
  - `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/main_shock_events.csv`
- Parameter selection strategy:
  - Parse `event_time` as UTC timestamps.
  - Identify Mw 6.4 and Mw 7.1 rows by magnitude from the two-row mainshock file.
  - Use a local tangent-plane or equivalent local metric projection centered near the corridor midpoint so distances to the centerline and along-strike coordinates are in km.
  - Define corridor membership by perpendicular distance `<= 3.0 km` from the finite centerline segment and by projection falling between the start and end points.
  - Preserve both geographic and projected coordinates in the processed event table.
- Constraints:
  - Use the user-specified geometry exactly; do not optimize strike, width, or endpoints from data.
  - Primary split is `35.72°N`; other split lines are secondary robustness checks only.
  - If an event lies exactly on a split latitude, mark it as unassigned to north/south for that split or use a documented deterministic rule; do not duplicate events across north and south.
- Key outputs:
  - Processed interevent event table with fields including original columns, `t_days_since_m64`, projected coordinates, corridor-membership flag, and north/south assignment flags for all three split latitudes.
  - Compact domain-count summary CSV for primary domains: entire, north(35.72), south(35.72).
  - Metadata file containing Mw 6.4 time, Mw 7.1 time, `0.732 day`, `1.404 day`, corridor endpoints, strike, width, and primary split latitude.

### Task 2 — Generate domain-definition diagnostics
- Task description:
  - Verify that the fixed corridor and subdomain assignments are correct spatially before fitting.
  - Produce the required domain-assignment figure showing all interevent events, corridor geometry, split line, assigned north/south events, and mainshocks.
- Required data sources:
  - Processed event table and metadata from Task 1.
- Parameter selection strategy:
  - Use all interevent events for background display, colored by time since Mw 6.4.
  - Overlay corridor centerline and corridor boundaries from the projected geometry transformed back to map coordinates if needed.
  - Highlight the events assigned to the primary entire/north/south domains.
  - Plot Mw 6.4 and Mw 7.1 mainshock locations distinctly.
- Constraints:
  - This figure is diagnostic for the fixed primary geometry, not a data-driven domain search.
  - Include the `35.72°N` split line prominently; `35.70` and `35.74` should only appear in optional robustness products, not in the primary diagnostic figure unless clearly secondary.
- Key outputs:
  - Domain-assignment diagnostic figure.
  - Validated primary domain-count summary CSV.

### Task 3 — Fit cumulative Omori p-values for the three primary domains
- Task description:
  - For each primary domain (entire, north, south) and each fixed cumulative period endpoint, fit the pure power-law Omori rate model `lambda(t)=K*t^(-p)` by maximum likelihood using events with `M >= 3.0`, inside the domain, and `0 < t <= t_n`.
  - Record event counts, fit status, fitted parameters, and failure reasons.
- Required data sources:
  - Processed event table from Task 1.
  - Metadata file from Task 1.
- Parameter selection strategy:
  - Apply the primary magnitude threshold `M >= 3.0` first.
  - For each domain and endpoint `t_n`, form the cumulative sample `[0, t_n]`.
  - Use event times relative to Mw 6.4 in days.
  - Handle the singular lower bound by setting the likelihood lower integration limit to the first observed event time in the fitted sample, while fitting only if the sample contains enough events to constrain p.
  - Estimate both `K` and `p` under the truncated observation interval `[t_min, t_n]`.
  - Store explicit status categories such as `success`, `too_few_events`, `optimization_failed`, or `unconstrained`.
- Constraints:
  - Do not switch to `K-c-p` for the primary result.
  - Do not fabricate southern early-window estimates if convergence fails; leave them missing with failure flag.
  - Northern windows with `N <= 20` must be flagged as low-count/open-circle points even if a numerical fit succeeds.
  - Treat `0.732 day` and `1.404 day` as standard endpoints within the same fixed list, not special-fit windows.
- Key outputs:
  - Primary fit-results CSV with at least:
    - domain label
    - period_days
    - event count
    - success/failure flag
    - failure reason
    - fitted `p`
    - fitted `K`
    - low-count/open-circle flag

### Task 4 — Bootstrap uncertainty estimation for p
- Task description:
  - Quantify uncertainty in the fitted p-values for every successful primary-domain/period fit by bootstrap resampling.
  - Merge bootstrap summaries back into the primary fit table.
- Required data sources:
  - Per-window event-time samples and fit status from Task 3.
- Parameter selection strategy:
  - For each successful fit window, resample event times with replacement within that domain-period sample.
  - Refit the same pure power-law model for each bootstrap replicate using the same lower-bound handling rule.
  - Use enough replicates to stabilize percentile intervals while remaining computationally practical; apply parallel workers across windows or replicates.
  - Summarize bootstrap `p` by median, 2.5 percentile, and 97.5 percentile.
- Constraints:
  - Use the same model form and fitting rules in bootstrap as in the primary fit.
  - If many bootstrap replicates fail for a window, record the bootstrap-valid replicate count and mark the interval as unreliable rather than silently dropping the issue.
  - Progress reporting should be shown during bootstrap execution.
- Key outputs:
  - Bootstrap summary table for each domain-period.
  - Final merged primary-results CSV containing:
    - domain label
    - period_days
    - event count
    - success/failure flag
    - fitted `p`
    - bootstrap median `p`
    - bootstrap lower/upper bounds
    - low-count/open-circle flag
    - bootstrap valid replicate count

### Task 5 — Create the required main figure and final-period rate-fit diagnostic
- Task description:
  - Produce the required two-panel primary figure:
    - panel a: p versus cumulative period for entire/north/south
    - panel b: observed seismicity rate versus time for the final entire-area window, with fitted power-law overlay
- Required data sources:
  - Final merged results table from Task 4.
  - Entire-area event times for the `1.404 day` window from Task 3.
- Parameter selection strategy:
  - Panel a:
    - x values are the fixed cumulative endpoints.
    - Plot entire area in grey, north in blue, south in red.
    - Use filled markers and vertical uncertainty bars for ordinary successful points.
    - Use open blue circles for northern points with `N <= 20`.
    - Leave failed/missing points absent rather than interpolated.
    - Add vertical reference lines at `0`, `0.732`, and `1.404` day.
  - Panel b:
    - Use only the entire-area `1.404 day` sample.
    - Estimate observed rate from event counts in logarithmically spaced or otherwise documented time bins within the fitted interval.
    - Overlay the fitted `K*t^(-p)` curve using the entire-area final-window primary fit.
    - Annotate fitted `p` with bootstrap uncertainty and annotate `1.404 day`.
- Constraints:
  - Panel a is the primary scientific figure and must emphasize the three-domain comparison.
  - Panel b must remain tied to the final `1.404 day` entire-area fit only.
  - Do not replace missing low-count or failed fits with smoothed lines.
- Key outputs:
  - Main two-panel figure with labeled panels `a` and `b`.

### Task 6 — Optional robustness check for north/south split latitude
- Task description:
  - Repeat the north/south cumulative p-analysis for split latitudes `35.70`, `35.72`, and `35.74` to test whether the late-period north-versus-south contrast is robust to the partition line.
- Required data sources:
  - Processed event table with alternative split assignments from Task 1.
  - Same fitting/bootstrap workflow as Tasks 3–4.
- Parameter selection strategy:
  - Keep all non-split parameters fixed:
    - same corridor
    - same `M >= 3.0`
    - same cumulative endpoints
    - same pure power-law likelihood
    - same bootstrap method
  - Compare the sign and magnitude of north-minus-south `p` differences at later periods, especially near `1.10`, `1.22`, and `1.404` days.
- Constraints:
  - This is secondary and must not replace the primary `35.72°N` comparison.
  - Robustness products should be clearly labeled as sensitivity tests.
- Key outputs:
  - Optional split-sensitivity CSV summarizing north/south p estimates by split latitude and period.
  - Optional robustness figure summarizing `35.70 / 35.72 / 35.74` results.

### Task 7 — Validation and deliverable checks
- Task description:
  - Perform final consistency checks on counts, timing, geometry, fit coverage, and required outputs before scientific interpretation.
- Required data sources:
  - All outputs from Tasks 1–6.
- Parameter selection strategy:
  - Confirm Mw 6.4 and Mw 7.1 times match the metadata file.
  - Confirm `1.404 day` aligns with the Mw 7.1 endpoint from the mainshock file.
  - Verify that north + south counts do not exceed entire-domain counts for each split and period.
  - Verify that every plotted point corresponds to a row in the final results CSV.
  - Check that missing/failed fits are explicitly flagged.
- Constraints:
  - Scientific success requires valid non-empty outputs for the primary domains and periods; partial intermediate files alone are not sufficient.
- Key outputs:
  - Final validated deliverable set:
    - processed interevent/domain table
    - domain-count summary CSV
    - metadata CSV or JSON
    - primary Omori-results CSV
    - bootstrap summary or merged uncertainty table
    - domain-assignment diagnostic figure
    - main two-panel figure
    - optional split-sensitivity products if generated