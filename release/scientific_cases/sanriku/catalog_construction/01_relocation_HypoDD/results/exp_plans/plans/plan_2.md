# Goal

Relocate the full Japan Aomori regional JMA catalog with `hypodd_runner` in catalog-only mode using the provided `phase.dat` and `station.sta`, produce a real merged relocated catalog with explicit accounting for all input events, and generate relocation diagnostics and publication-style figures from native HypoDD outputs only.

## Planning Assumptions

- Observation data are sufficient and should be used directly: `phase.dat` is the primary phase source, with `events.csv`, `picks.csv`, `station.sta`, `summary.txt`, and `main_earthquake.csv` used for validation, parameterization, accounting, and plotting.
- `hypodd_runner` public grouped-parameter API should be used:
  - `HypoDDInputs`, `EventSelection`, `Ph2dtParams`, `HypoDDParams`, `RuntimeOptions`
  - catalog-only entry points: `run_catalog_only_relocation(...)` for one valid small selection and `run_catalog_only_auto_time_windows(...)` for larger catalogs.
- In this environment, `hypo_root` must be `<LOCAL_PATH>
- Use `phase_format="auto"` unless validation proves a stricter format is required.
- Native compiled scale limits must shape execution strategy:
  - `ph2dt.inc`: `MEV=16000`, `MSTA=2400`, `MOBS=500`
  - `hypoDD.inc`: `MAXEVE=10800`, `MAXDATA=3100000`, `MAXSTA=1300`, `MAXCL=100`
- Because the catalog has 29,896 events, one single native HypoDD run is above `MAXEVE`; therefore the production workflow should use `run_catalog_only_auto_time_windows(...)` unless diagnostics unexpectedly show a smaller selected subset only.
- For catalog-only relocation, both bare `STA` and `NET.STA` are accepted. Since `phase.dat` and `station.sta` already match, preserve original station IDs by default; add a prefix such as `J.` only if the chosen validated `hypodd_runner` path explicitly requires it, and then apply the mapping consistently to all relevant inputs and outputs.
- `HypoDDParams.iter_rows` must be explicitly set as 10-value rows in the format `NITER WTCCP WTCCS WRCC WDCC WTCTP WTCTS WRCT WDCT DAMP`; `NITER` values are cumulative endpoints.
- `iter_rows=None` is not the scientific default for this task. Damping and catalog-differential-time weights must be chosen from the current catalog geometry and tested on bounded diagnostic windows before one production full-catalog run.
- HypoDD relocation velocity should be set with:
  - `mod_top = [0.0, 5.0, 10.0, 20.0, 35.0, 50.0, 90.0]`
  - `mod_vel = [5.4, 5.8, 6.2, 6.6, 7.2, 7.6, 8.05]`
  - `mod_ratio = 1.73` unless current metadata provide a better documented regional value.
- Catalog-only success requires non-empty native outputs including `dt_*.ct`, `{catalog_code}.loc`, `{catalog_code}.reloc`, and `{catalog_code}.res`; empty or unchanged placeholders are failure evidence, not success.
- Full-catalog success additionally requires merged accounting across windows: relocated, unrelocated, and failed events must be separated explicitly, with per-window status and log evidence retained.

## Analysis Plan

### Task 1 — Build one primary relocation-and-validation script for full-catalog catalog-only relocation

#### 1.1 Input audit and package-contract validation
- Task description: Validate the provided files, confirm that `phase.dat` can be used directly, determine whether auto-window execution is required, and derive parameter ranges and diagnostics needed for relocation setup.
- Required data sources:
  - `<CASE_ROOT>/data/regional/phase.dat`
  - `<CASE_ROOT>/data/regional/station.sta`
  - `<CASE_ROOT>/data/regional/events.csv`
  - `<CASE_ROOT>/data/regional/picks.csv`
  - `<CASE_ROOT>/data/regional/summary.txt`
- Parameter selection strategy:
  - Read `summary.txt` and `events.csv` to determine full `ot_range`, `lat_range`, and `lon_range`.
  - Use the full event population as the scientific target selection unless diagnostics reveal invalid rows requiring explicit exclusion.
  - Set `catalog_code` to an Aomori-specific identifier and keep it fixed across all run products and plots.
  - Set `phase_format="auto"` initially, then retain it if direct validation of event-block parsing succeeds.
  - Set `dep_corr` from the current catalog datum; default to `0.0` unless the input files/documentation show that a correction is necessary.
- Constraints:
  - Do not rebuild `phase.dat` from `picks.csv` unless direct validation fails.
  - Preserve event IDs exactly as stored in the source catalog and verify they remain traceable through relocation outputs.
  - Preserve original station IDs if direct matching succeeds between `phase.dat` and `station.sta`.
  - Explicitly compare total event count to native `MAXEVE`; because 29,896 > 10,800, production mode should be auto-windowed.
- Key outputs:
  - Input validation manifest table or JSON containing source paths, row counts, selected event count, station count, parsed time range, geographic range, station-ID consistency result, phase-file validation result, and chosen `hypodd_runner` execution mode.
  - A station-ID mapping table only if a `NET.STA` remap is actually required.

#### 1.2 Pre-relocation catalog diagnostics for parameterization
- Task description: Quantify the data density and pairing environment to choose defensible `Ph2dtParams` and `HypoDDParams.iter_rows`.
- Required data sources:
  - `events.csv`
  - `picks.csv`
  - `phase.dat`
  - `station.sta`
- Parameter selection strategy:
  - Compute event-level pick-count distributions from `events.csv` and/or `picks.csv`.
  - Compute station participation counts and event-station coverage.
  - Estimate event density through time to support the initial auto-window scale choice, starting from monthly or similarly coarse windows.
  - Build simple pairability diagnostics from origin-time proximity and shared-station counts on bounded subsets to guide `ph2dt` thresholds.
- Constraints:
  - Use these diagnostics to choose full-catalog production parameters, but do not treat diagnostics alone as relocation success.
  - Since this is catalog-only relocation, all nonzero HypoDD weights should be assigned to catalog differential times (`WTCTP`, `WTCTS`, `WRCT`, `WDCT`), while CC weights remain zero.
- Key outputs:
  - Pre-run diagnostic summary table with:
    - events per month or chosen coarse time unit
    - picks per event statistics
    - stations per event statistics
    - picks per station statistics
    - indicative event-link density metrics for representative dense and sparse windows

#### 1.3 Diagnostic subset screening for ph2dt and damping schedule
- Task description: Use bounded representative windows to compare a small number of scientifically justified candidate parameter sets before one production full-catalog run.
- Required data sources:
  - same validated catalog inputs as above
- Parameter selection strategy:
  - Choose at least two diagnostic windows:
    - one dense window representative of high event-link density
    - one sparse or problematic window representative of weaker linkage
  - For each diagnostic window, test a limited set of `Ph2dtParams` and `HypoDDParams.iter_rows` candidates.
  - Start with catalog-only weighting schedules such as:
    - early iterations emphasizing robust P catalog links, later iterations adding stronger S contribution if available
    - cumulative `NITER` endpoints such as 4, 8, 12
  - Compare at least one larger LSQR damping choice in the requested range, e.g., around 80–120, against a neighboring alternative; select the production damping from relocated-event count, residual behavior, convergence evidence, and run stability.
- Constraints:
  - Do not run a large parameter sweep across the full catalog.
  - `iter_rows` must be explicitly recorded for every diagnostic candidate.
  - Candidate rows must reflect catalog-only mode:
    - `WTCCP=WTCCS=WRCC=WDCC=0`
    - nonzero controls should be in `WTCTP`, `WTCTS`, `WRCT`, `WDCT`, and `DAMP`
  - Justify `WTCTP` vs `WTCTS` from phase availability and expected P/S reliability in the provided picks.
- Key outputs:
  - Diagnostic candidate comparison table with, for each tested subset run:
    - parameter set ID
    - selected window
    - `Ph2dtParams` values
    - explicit `iter_rows`
    - attempted event count
    - relocated-event count
    - unrelocated-event count
    - residual summary from `.res`
    - runtime
    - native output existence/non-emptiness
    - failure evidence paths if any
  - Selected production parameter set for the full catalog.

#### 1.4 Production full-catalog auto-window relocation
- Task description: Run the real relocation for the full catalog using the selected production parameter set and package-supported auto-windowing.
- Required data sources:
  - validated `phase.dat`
  - validated `station.sta`
  - `events.csv` for final event accounting and merge
- Parameter selection strategy:
  - Use `run_catalog_only_auto_time_windows(...)` with grouped objects:
    - `HypoDDInputs(hypo_root, phase_file, station_file, output_folder, catalog_code)`
    - `EventSelection(ot_range, lat_range, lon_range, dep_corr, phase_format="auto")`
    - chosen `Ph2dtParams`
    - chosen `HypoDDParams(mod_top, mod_vel, mod_ratio=1.73, iter_rows=selected_rows)`
    - `RuntimeOptions` sized for the current environment
  - Start with the coarsest windowing supported by the package that is likely below native limits; only shrink window size if planned windows still exceed limits or fail for scale reasons.
  - Keep `continue_on_error=False` for the required scientific run so the first non-empty failed window stops and records evidence for correction.
  - Keep the package’s window-level strategy rather than a hand-written loop.
- Constraints:
  - All windows must preserve original input event IDs in final accounting.
  - Window execution must retain native logs, traceback files, and manifest/status records.
  - Do not silently drop windows or events that fail.
  - Do not report success unless merged real native outputs are non-empty.
- Key outputs:
  - Per-window manifest/status file with:
    - window ID and time range
    - input event count
    - attempted event count
    - status
    - parameter summary
    - output folder
    - native log paths
    - failure evidence paths if applicable
  - Native per-window `dt_*.ct`, `.loc`, `.reloc`, `.res` outputs for successful windows.
  - A full-catalog merged relocated table built from real per-window `.reloc` files.
  - Separate failed-window and failed-event records.

#### 1.5 Post-run event accounting and merged catalog assembly
- Task description: Reconcile all source events against successful and failed windows and build the final analysis-ready outputs.
- Required data sources:
  - `events.csv`
  - per-window relocation outputs and manifests
- Parameter selection strategy:
  - Join on preserved `event_id`; if a windowed output lacks direct IDs, use the package-verified event identity mapping from the same run only.
  - Classify every input event into exactly one of:
    - relocated
    - attempted but unrelocated
    - failed window / failed run with explicit reason
    - excluded before run with explicit validation reason
- Constraints:
  - Do not count original unrevised hypocenters as relocated results.
  - Do not infer relocation success from `.loc` alone without non-empty `.reloc`.
  - Keep original and relocated coordinates side by side for downstream plots.
- Key outputs:
  - Final merged relocated catalog CSV with original and relocated hypocenters, event IDs, origin times, magnitudes, and relocation metadata.
  - Unrelocated-events table with explicit reasons.
  - Run-summary table listing all attempted runs/windows and evidence paths.
  - Residual summary table parsed from real `.res` files, keeping `RES [ms]` as milliseconds.

### Task 2 — Build figure products from real relocation outputs

#### 2.1 Relocation geometry figures
- Task description: Create the required map and cross-section views comparing initial and relocated hypocenters, with stations and labeled main earthquakes.
- Required data sources:
  - final merged relocated catalog
  - `events.csv` for initial locations
  - `station.sta`
  - `main_earthquake.csv`
- Parameter selection strategy:
  - Plot all relocated events in black.
  - Plot initial catalog locations for the same relocated-event subset in gray.
  - Plot stations from `station.sta`.
  - Plot the three main earthquakes from `main_earthquake.csv` in red with labels.
  - Use the same relocated-event subset consistently across map and cross sections.
- Constraints:
  - If no real relocated events exist, produce only clearly marked diagnostic/failure figures.
  - Cross sections must use relocated outputs only for relocated-event panels.
- Key outputs:
  - Lon–lat relocation map.
  - Lon–depth section.
  - Lat–depth section.

#### 2.2 Residual distribution figure
- Task description: Summarize relocation residuals from native HypoDD outputs.
- Required data sources:
  - merged residual table parsed from successful `.res` files
- Parameter selection strategy:
  - Use the package/native residual fields only; treat `RES [ms]` as already in milliseconds.
  - Show overall residual histogram/distribution and, if available, stratify by phase or by successful window.
- Constraints:
  - Do not derive residuals from `DT`.
  - Do not mix failed-window diagnostics into the scientific residual figure unless explicitly labeled as failure evidence.
- Key outputs:
  - Residual distribution panel.
  - Optional per-window residual comparison panel.

#### 2.3 Relocation shift figure
- Task description: Quantify and visualize the displacement between initial and relocated hypocenters.
- Required data sources:
  - final merged relocated catalog with original and relocated coordinates
- Parameter selection strategy:
  - Compute horizontal shift distance, depth shift, and optionally 3-D shift magnitude per relocated event.
  - Plot vector/arrows for a thinned spatial sample if the full catalog is too dense visually.
  - Show histograms or cumulative distributions of horizontal and vertical shifts.
- Constraints:
  - Use only events with verified relocated coordinates.
  - Keep the event-ID linkage intact for all displacement calculations.
- Key outputs:
  - Shift-vector map or sampled displacement arrows.
  - Horizontal-shift histogram.
  - Depth-shift histogram or signed depth-change distribution.

#### 2.4 Statistics figure
- Task description: Summarize catalog statistics before and after relocation.
- Required data sources:
  - `events.csv`
  - final merged relocated catalog
  - unrelocated/failed-event table
  - run-summary table
- Parameter selection strategy:
  - Include counts of total, attempted, relocated, unrelocated, failed, and excluded events.
  - Compare initial vs relocated depth distributions and spatial density where meaningful.
  - Add event counts per successful window and per status category.
- Constraints:
  - Do not present relocated statistics as representative of the entire input catalog without also showing the accounting fractions.
  - Separate “not relocated” from “failed to run”.
- Key outputs:
  - Statistics summary panel with event-accounting bars/tables.
  - Initial-vs-relocated depth or location distribution comparison.
  - Optional window coverage/status panel.

#### 2.5 Optional additional meaningful figures
- Task description: Add figures only if they are derived from real outputs and improve scientific interpretation.
- Required data sources:
  - merged relocated catalog
  - residual table
  - window manifest
- Parameter selection strategy:
  - Candidate additions:
    - per-window relocation yield versus event count
    - residual versus depth
    - relocation shift versus magnitude or pick count
    - station usage heat map
- Constraints:
  - Optional figures must not substitute for the required figures.
- Key outputs:
  - One or more supplementary diagnostic/scientific panels, clearly distinguished from failure evidence if applicable.

### Task 3 — Define concrete output artifacts and execution flow inside the primary script

#### 3.1 Execution flow
- Task description: Keep the workflow in one cohesive Python script that performs validation, bounded diagnostic screening, production relocation, merged accounting, and figure generation.
- Required data sources:
  - all validated regional inputs
- Parameter selection strategy:
  - Sequence:
    1. validate files and direct-use eligibility of `phase.dat`
    2. compute catalog diagnostics
    3. choose diagnostic windows
    4. run limited candidate tests
    5. select production `Ph2dtParams` and `iter_rows`
    6. run full-catalog auto-window relocation
    7. merge outputs and classify all events
    8. generate figures from real outputs only
- Constraints:
  - Keep config preparation, execution, native output checks, and failure evidence collection in the same script.
  - Use a second script only if plotting from already validated merged outputs must be rerun independently; otherwise keep one primary script.
- Key outputs:
  - One self-contained relocation workflow script.
  - Compact machine-readable summaries for manifests, run tables, and event accounting.

#### 3.2 Minimum artifact set to save
- Task description: Ensure reproducibility and explicit evidence retention.
- Required data sources:
  - primary run outputs
- Parameter selection strategy:
  - Save at minimum:
    - input-validation manifest
    - diagnostic-candidate comparison table
    - selected production-parameter summary
    - per-window run manifest/status table
    - merged relocated catalog
    - unrelocated/failed-event table
    - residual summary table
    - figure files
- Constraints:
  - Every attempted package run must have status, parameter summary, output folder, native log paths, and failure evidence if applicable.
- Key outputs:
  - Reproducible relocation evidence package centered on the real native `hypodd_runner` outputs.