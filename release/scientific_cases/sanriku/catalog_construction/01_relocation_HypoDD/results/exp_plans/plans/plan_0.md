# Goal

Relocate the full Japan Aomori regional JMA catalog with `hypodd_runner` using the provided `phase.dat` and `station.sta` as the primary native inputs, select scientifically justified catalog-only `ph2dt` and HypoDD parameters for this dataset, execute a package-supported full-catalog windowed workflow that respects native HypoDD limits, and produce merged relocation products, run-status accounting, and figures based only on real relocation outputs.

## Planning Assumptions

- Use observation-based catalog inputs only: `phase.dat`, `station.sta`, `events.csv`, `picks.csv`, `summary.txt`, and `main_earthquake.csv`. No model catalog or synthetic relocation substitute is allowed.
- `hypodd_runner` public API for this task uses grouped parameter objects: `HypoDDInputs`, `EventSelection`, `Ph2dtParams`, `HypoDDParams`, and `RuntimeOptions`, with catalog-only entry points `run_catalog_only_relocation(...)` for one valid subset and `run_catalog_only_auto_time_windows(...)` for larger catalogs.
- In this environment, `hypo_root` must be `<LOCAL_PATH> containing native `ph2dt/ph2dt` and `hypoDD/hypoDD`.
- Package contract: `phase_format="auto"` is the safest default; if the provided `phase.dat` is valid event-block input, pass it directly as `HypoDDInputs.phase_file` and do not rebuild it from `picks.csv` by default.
- Station identifiers should remain unchanged because the provided station and phase files are already internally consistent. Add a synthetic `J.` prefix only if the chosen documented API path explicitly requires `NET.STA`; if applied, the same mapping must be propagated consistently to every generated input and every later merge key.
- Native compiled limits require package-supported splitting for this catalog size: `ph2dt.inc` `MEV=16000`, `MSTA=2400`, `MOBS=500`; `hypoDD.inc` `MAXEVE=10800`, `MAXDATA=3100000`, `MAXSTA=1300`, `MAXCL=100`. With 29,896 events, a single native run is not valid; prefer `run_catalog_only_auto_time_windows(...)`.
- Production relocation success requires non-empty native outputs such as `dt_*.ct`, `{catalog_code}.loc`, `{catalog_code}.reloc`, and `{catalog_code}.res`, plus per-window status/failure evidence and a merged relocated catalog preserving event identity.
- `HypoDDParams.iter_rows` must be explicitly defined for this scientific run. Each row format is `NITER WTCCP WTCCS WRCC WDCC WTCTP WTCTS WRCT WDCT DAMP`, and `NITER` values are cumulative endpoints.
- Parameter screening should not be done as a full-catalog sweep. Compare candidate damping / iteration schedules on a bounded diagnostic subset or representative windows, then run the full catalog once with the selected production settings.
- `dep_corr` is a depth datum correction and should default to `0.0` unless the current catalog metadata indicates a justified correction.
- HypoDD velocity model for relocation should use the supplied 1-D layer tops and Vp values, with `mod_ratio=1.73` unless a better documented ratio is derived from the current data and recorded.
- For required scientific execution, use fail-fast behavior (`continue_on_error=False`) so the first failed non-empty production window leaves native evidence for diagnosis before continuing.

## Analysis Plan

### Task 1 — Prepare, validate, and tune a production-ready `hypodd_runner` catalog-only workflow script

- Task description
  - Build one primary self-contained Python script that:
    1. validates all provided inputs and cross-file identifiers,
    2. derives region/time bounds from the actual catalog,
    3. checks native scale limits and chooses the package-supported auto-window strategy,
    4. runs a bounded diagnostic parameter screen on representative subsets/windows,
    5. selects final `Ph2dtParams` and `HypoDDParams(iter_rows=...)`,
    6. executes the full-catalog catalog-only relocation with `run_catalog_only_auto_time_windows(...)`,
    7. merges real native outputs back to the source event catalog,
    8. writes machine-readable run manifests and event accounting tables.

- Required data sources
  - Primary: `<CASE_ROOT>/data/regional/phase.dat`
  - Primary: `<CASE_ROOT>/data/regional/station.sta`
  - Support/validation: `events.csv`, `picks.csv`, `summary.txt`
  - Plot annotation support later: `main_earthquake.csv`

- Parameter selection strategy
  - Inputs and selection
    - Set `HypoDDInputs.hypo_root` to `<LOCAL_PATH>
    - Set `HypoDDInputs.phase_file` to the provided `phase.dat` after validation.
    - Set `HypoDDInputs.station_file` to the provided `station.sta`.
    - Set a catalog code specific to this run, preserving a stable prefix across all windows and merged products.
    - Set `EventSelection.ot_range`, `lat_range`, and `lon_range` from observed minima/maxima in `events.csv`, cross-checked against `summary.txt`; use slight inclusive padding only if needed by the package/API, otherwise use observed bounds directly.
    - Set `EventSelection.phase_format="auto"`.
    - Set `EventSelection.dep_corr=0.0` unless the event catalog explicitly documents a nonzero depth datum offset.
  - Input validation
    - Confirm `phase.dat` is event-block formatted and parseable.
    - Confirm all `phase.dat` event IDs map to `events.csv` event IDs and are unique over the full catalog.
    - Confirm all station codes in `phase.dat` exist in `station.sta`.
    - Confirm event count, pick count, and station count are consistent with `summary.txt`.
    - Use `picks.csv` only as a fallback cross-check when diagnosing phase inconsistencies; do not rebuild `phase.dat` in the default path.
  - Windowing strategy
    - Because 29,896 events exceed native `MAXEVE=10800`, use `run_catalog_only_auto_time_windows(...)` rather than a single-run call.
    - Start from the coarsest valid time windows supported by the package helper, targeting windows comfortably below `MAXEVE`; prefer monthly or multi-week windows and only shrink if a planned window still exceeds event/data limits or produces native limit evidence.
    - Preserve all source events in final accounting, including relocated, selected-but-unrelocated, and failed-window events.
  - `Ph2dtParams`
    - Derive candidate link thresholds from actual event density, per-event pick counts in `events.csv`, station coverage in `station.sta`, and observed total pick volume in `phase.dat`/`picks.csv`.
    - Use a conservative catalog-only linking strategy suitable for a dense regional network:
      - require a nontrivial minimum number of shared observations between event pairs,
      - cap per-pair observations to avoid unnecessary `MAXDATA` inflation,
      - cap nearest neighbors per event to control graph density,
      - keep both P and S catalog times if available in the phase file.
    - Screen a small set of candidate `Ph2dtParams` on representative dense and sparse windows, then choose one production set based on:
      - non-empty `dt_*.ct`,
      - stable relocated-event counts,
      - acceptable runtime,
      - no native limit failure,
      - improved residual behavior without excessive pair-density inflation.
  - `HypoDDParams`
    - Set `mod_top=[0.0, 5.0, 10.0, 20.0, 35.0, 50.0, 90.0]`.
    - Set `mod_vel=[5.4, 5.8, 6.2, 6.6, 7.2, 7.6, 8.05]`.
    - Set `mod_ratio=1.73` unless the current dataset provides a better documented value.
    - Use catalog-only weights: CC-related weights/cutoffs remain zero because waveform cross-correlation is not part of this task.
    - Test at least two scientifically plausible catalog-only `iter_rows` schedules on the diagnostic subset/windows, including one schedule with larger LSQR damping in the requested range such as `80-120`.
    - Example selection logic for candidates:
      - early stage: stronger catalog-time weighting with moderate distance weighting and higher damping to stabilize large-network geometry,
      - later stage: gradually reduced damping and/or tighter catalog residual weighting only if residuals improve and relocated counts remain stable.
    - Choose the final schedule from observed diagnostic evidence, not package fallback. Record the scientific rationale in a compact parameter summary table.
  - Runtime options
    - Use grouped `RuntimeOptions` supported by the package.
    - Keep time-window execution deterministic/sequential at the window level as required by the package contract.
    - Set worker count only for within-window native execution as supported by the runtime object.
    - Set `continue_on_error=False` for the production run.
    - Retain intermediate native logs and per-window outputs needed for evidence and later merging.

- Constraints
  - Do not replace `hypodd_runner` with custom relocation code or simplified coordinate shifts.
  - Do not treat validation-only outputs, empty `.reloc`, unchanged original catalog, or plotting artifacts as relocation success.
  - Do not invent or silently rewrite event IDs.
  - Do not add a synthetic network code unless the documented API path requires it; if required, apply one consistent mapping across station, phase, and all merge logic.
  - Do not infer successful relocation from only Python-level completion; require non-empty native outputs and per-window evidence.
  - Do not run multiple full-catalog production sweeps for parameter tuning.

- Key outputs
  - One self-contained Python workflow script for validation, tuning, production relocation, merge, and accounting.
  - Input validation manifest summarizing:
    - source file paths,
    - event/station/pick counts,
    - identifier consistency checks,
    - phase/station validation results,
    - whether original station IDs were preserved.
  - Diagnostic subset/window comparison table containing for each tested candidate:
    - subset/window identifier,
    - `Ph2dtParams` summary,
    - `HypoDDParams.iter_rows` summary,
    - runtime,
    - `dt_*.ct` presence/size,
    - relocated-event count,
    - residual statistics from `.res`,
    - convergence/failure evidence.
  - Production run manifest with:
    - selected final parameters,
    - package entry point used,
    - window plan,
    - per-window status,
    - native log paths,
    - output folder names,
    - failure evidence paths where applicable.
  - Final merged relocation products:
    - merged relocated catalog with preserved event IDs,
    - initial-vs-relocated comparison table,
    - unrelocated-event table with explicit reasons,
    - failed-window / failed-event evidence table,
    - summary counts of all input events partitioned into relocated, unrelocated, and failed.

### Task 2 — Build figures and relocation statistics from real native outputs only

- Task description
  - Using the merged production outputs from Task 1, generate publication-style diagnostic and interpretation figures that compare initial and relocated hypocenters, summarize residuals and shifts, and display event accounting. If no real relocated catalog exists, generate only clearly labeled failure-evidence diagnostics.

- Required data sources
  - Merged relocated catalog from Task 1
  - Initial event catalog: `events.csv`
  - Station inventory: `station.sta`
  - Mainshock annotation file: `main_earthquake.csv`
  - Native residual outputs: per-window or merged `{catalog_code}.res`
  - Per-window status/accounting tables from Task 1

- Parameter selection strategy
  - Merge and identity handling
    - Join relocated events back to `events.csv` using preserved event IDs; if a windowed native output lacks explicit IDs in some step, use only a verified package-consistent identity mapping from the same run/window.
  - Residual statistics
    - Parse residuals from native `.res` outputs using the documented residual field; treat `RES [ms]` as already in milliseconds.
    - Summarize by phase type if available, and overall by mean, median, standard deviation, robust percentiles, and tail fractions.
  - Shift statistics
    - Compute horizontal shift, depth shift, and 3-D hypocentral shift between initial and relocated locations.
    - Summarize distributions overall and by magnitude, depth, and event pick count if these fields are available in `events.csv`.
  - Event accounting
    - Build counts and fractions for:
      - all input events,
      - selected events,
      - relocated events,
      - selected but not relocated events,
      - failed-window events,
      - events excluded by any explicit selection/filter.
  - Map and section extents
    - Use the actual catalog spatial bounds from `events.csv`; include stations and main earthquakes within the same region.
    - Use observed depth ranges from the initial and relocated catalogs to set section limits.

- Constraints
  - Figures must be built only from real relocation outputs from Task 1.
  - If the production relocation fails or yields no relocated events, mark every figure as diagnostic/failure evidence and do not present them as scientific success outputs.
  - Do not mix failed/unrelocated events into the relocated dataset without explicit labeling.
  - Keep initial locations visually distinct from relocated locations in every spatial comparison figure.

- Key outputs
  - Relocation map figure with three coordinated panels:
    - lon-lat map with stations, initial events in gray, relocated events in black, and main earthquakes in red,
    - lon-depth section,
    - lat-depth section.
  - Residual distribution figure:
    - histogram and/or density of native residuals,
    - cumulative or percentile view,
    - optional P/S split if supported by native output fields.
  - Relocation shift figure:
    - histogram of horizontal and depth shifts,
    - scatter of shift magnitude versus depth, magnitude, or pick count.
  - Statistic figure:
    - counts of initial vs relocated vs unrelocated/failed events,
    - depth and magnitude distributions before and after relocation,
    - pick-count or station-count summary if available.
  - Optional meaningful figures if supported by real outputs:
    - per-window relocated fraction,
    - residual reduction by window,
    - map of larger relocation shifts,
    - connectivity or pick-density diagnostics linked to relocation success.
  - Figure data tables for reproducibility:
    - plotting-ready catalog comparison table,
    - residual summary table,
    - shift summary table,
    - event accounting table.