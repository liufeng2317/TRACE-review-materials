# Goal

Relocate the full Japan Aomori regional JMA catalog with `hypodd_runner` in catalog-only mode using the provided validated `phase.dat` and `station.sta`, produce a merged relocation result with explicit accounting for all input events, and generate relocation diagnostics and publication-style figures from real native outputs only.

## Planning Assumptions

- Observation data are available and sufficient; no model-generated picks or synthetic catalogs are needed.
- The primary relocation package is `hypodd_runner`, using its public grouped-parameter Python API: `HypoDDInputs`, `EventSelection`, `Ph2dtParams`, `HypoDDParams`, `RuntimeOptions`, and the catalog-only entry points.
- In this environment, `hypo_root` must be `<LOCAL_PATH> and it must contain native `ph2dt/ph2dt` and `hypoDD/hypoDD`.
- For catalog-only relocation, use `run_catalog_only_relocation(...)` only for small diagnostic subsets and `run_catalog_only_auto_time_windows(...)` for larger catalogs that may exceed native limits.
- Native limits documented for this package environment are:
  - `ph2dt.inc`: `MEV=16000`, `MSTA=2400`, `MOBS=500`
  - `hypoDD.inc`: `MAXEVE=10800`, `MAXDATA=3100000`, `MAXSTA=1300`, `MAXCL=100`
- Because the catalog has 29,896 events, a single native full-catalog run exceeds `MAXEVE`; therefore the production strategy should use package-supported auto time windows, with the coarsest valid windows first.
- `phase_format="auto"` is the safest default unless validation proves a more specific format.
- If the provided `phase.dat` validates as event-block phase input with matching station IDs, it should be used directly; do not rebuild from `picks.csv` by default.
- Station IDs should remain unchanged because `phase.dat` and `station.sta` are already internally consistent; only add a `J.` prefix if the chosen public API path explicitly requires `NET.STA`, and then apply the same mapping consistently to every generated input and merge table.
- `HypoDDParams.iter_rows` must be explicitly set; do not use `iter_rows=None` as the scientific production default.
- `HypoDDParams.iter_rows` rows must follow `NITER WTCCP WTCCS WRCC WDCC WTCTP WTCTS WRCT WDCT DAMP`, with cumulative `NITER` endpoints.
- For this catalog-only task, CC-related weights should remain zero and catalog-difference weights should control inversion.
- The supplied 1-D velocity model should be passed through `hypodd.mod_top`, `hypodd.mod_vel`, and `hypodd.mod_ratio`, using `Vp/Vs = 1.73` unless a better documented estimate is derived from the current dataset.
- Production success requires real non-empty native outputs, including `dt_*.ct`, `{catalog_code}.loc`, `{catalog_code}.reloc`, and `{catalog_code}.res`, plus merged event accounting across all windows.
- Empty outputs, unchanged original catalogs, validation-only checks, or plotting-only products are not success.

## Analysis Plan

### Task 1: Build one primary `hypodd_runner` relocation-and-validation script for the full catalog

#### 1.1 Input audit and package-readiness validation
- Task description: Validate that the provided regional files are internally consistent and suitable for direct `hypodd_runner` catalog-only relocation without rebuilding the phase file.
- Required data sources:
  - `<CASE_ROOT>/data/regional/events.csv`
  - `<CASE_ROOT>/data/regional/picks.csv`
  - `<CASE_ROOT>/data/regional/phase.dat`
  - `<CASE_ROOT>/data/regional/station.sta`
  - `<CASE_ROOT>/data/regional/summary.txt`
- Parameter selection strategy:
  - Use `phase.dat` as the primary phase source.
  - Use `station.sta` as the primary station source.
  - Use `events.csv` and `picks.csv` only for cross-checking counts, IDs, time ranges, and optional fallback rebuilding logic if validation fails.
  - Determine relocation selection bounds from the actual catalog extent in `events.csv` and confirm against `summary.txt`.
- Constraints:
  - Verify event count, station count, and pick-row count against the supplied summaries.
  - Confirm that all event IDs in `events.csv` are unique and span the expected full range.
  - Confirm that all station IDs referenced by `phase.dat` exist in `station.sta`.
  - Confirm that `phase.dat` is readable as event-block input with parseable event headers and station pick rows.
  - Preserve original station IDs if validation passes.
  - Preserve event IDs and UTC-compatible origin times exactly for later merge/accounting.
- Key outputs:
  - `input_manifest.json` or CSV-equivalent manifest summarizing source paths, counts, time bounds, geographic bounds, station-ID consistency, and whether direct `phase.dat` usage is valid.
  - `phase_validation_summary.csv` listing any malformed event headers, missing stations, duplicate IDs, or parse failures.
  - Decision flag indicating `use_phase_dat_directly=true/false`.

#### 1.2 Native-limit assessment and execution mode decision
- Task description: Determine whether a single run or package-supported auto-window relocation is required, and define the windowing approach that preserves all events.
- Required data sources:
  - `events.csv`
  - `phase.dat`
  - `summary.txt`
- Parameter selection strategy:
  - Compare total event count and observed data volume with native `MAXEVE` and `MAXDATA`.
  - Start with the coarsest time windows that are likely to remain below native limits, using actual event-density diagnostics from `events.csv`.
  - Prefer monthly windows initially; shrink only if a monthly window exceeds native limits or produces documented failure evidence related to scale.
- Constraints:
  - Do not hand-write custom batch loops if `run_catalog_only_auto_time_windows(...)` supports the task.
  - Preserve all input events in final accounting, including relocated, unrelocated, and failed.
  - Keep windowing deterministic and compatible with package manifests.
- Key outputs:
  - `window_planning_summary.csv` with estimated event counts per candidate coarse window.
  - Chosen execution mode recorded as `catalog_only_auto_time_windows`.
  - Selected production window granularity and justification.

#### 1.3 Diagnostic parameter screening on bounded subsets
- Task description: Use a limited subset workflow to choose scientifically justified `Ph2dtParams` and `HypoDDParams.iter_rows` before the single production full-catalog run.
- Required data sources:
  - `events.csv`
  - `phase.dat`
  - `station.sta`
  - package-generated diagnostic outputs from subset runs
- Parameter selection strategy:
  - Select at least:
    - one dense representative subset window with high event-link potential,
    - one sparser or more difficult subset window if event density varies materially through time.
  - Choose `EventSelection.ot_range`, `lat_range`, and `lon_range` directly from those subset windows.
  - Start `Ph2dtParams` from observed catalog geometry and pick coverage, explicitly setting event-pair and station-link thresholds rather than relying on package defaults.
  - For catalog-only relocation, set CC weights to zero in `iter_rows`.
  - Compare at least two scientifically plausible LSQR damping schedules, including one in the tens-to-hundreds range such as around `80-120`, because the user explicitly requested this check.
  - Use cumulative iteration schedules with staged catalog weights, for example:
    - early stage emphasizing robust catalog links and larger damping,
    - later stage reduced damping if convergence and stability improve.
  - Record actual tested `iter_rows` values, not just narrative descriptions.
- Constraints:
  - Do not run multiple competing parameter sets across the full catalog.
  - Compare subset candidates using real output evidence: runtime, number of linked/relocated events, residual distributions, shift magnitudes, instability/outlier behavior, and native failures.
  - If a candidate yields empty native outputs, inspect native logs and mark it failed rather than interpreting it as success.
- Key outputs:
  - `subset_run_status.csv` with run ID, subset definition, `Ph2dtParams`, `iter_rows`, damping values, native output presence, runtime, relocated count, and failure evidence paths.
  - `parameter_screening_summary.json` naming the selected production `Ph2dtParams` and `HypoDDParams`.
  - `production_params.json` containing the exact grouped-parameter values to be used in the full-catalog run.

#### 1.4 Production full-catalog relocation with grouped public API
- Task description: Execute the real full-catalog catalog-only relocation with `hypodd_runner` using the selected parameters and package-supported auto time windows.
- Required data sources:
  - `phase.dat`
  - `station.sta`
  - `events.csv`
  - selected grouped parameters from Task 1.3
- Parameter selection strategy:
  - Construct:
    - `HypoDDInputs` with `hypo_root="<LOCAL_PATH>"`, direct `phase_file`, direct `station_file`, `catalog_code` specific to this Aomori run, and explicit output folder name.
    - `EventSelection` using full observed origin-time range and full catalog lat/lon range from `events.csv`; set `phase_format="auto"`.
    - `Ph2dtParams` from subset screening.
    - `HypoDDParams` using:
      - `mod_top = [0.0, 5.0, 10.0, 20.0, 35.0, 50.0, 90.0]`
      - `mod_vel = [5.4, 5.8, 6.2, 6.6, 7.2, 7.6, 8.05]`
      - `mod_ratio = 1.73` unless an improved documented estimate from current data is available
      - explicit `iter_rows` from screening
    - `RuntimeOptions` with worker count chosen for within-window native execution, not for manual window parallelization.
  - Use `run_catalog_only_auto_time_windows(...)` for the production run.
  - Set production execution to fail-fast for scientific integrity unless the explicit goal becomes a diagnostic sweep.
- Constraints:
  - Keep original station IDs unless the public API path proves `NET.STA` is required.
  - If a network prefix becomes necessary, apply a single consistent mapping and write the mapping table explicitly.
  - Do not truncate events to satisfy native limits; use the package windowing helper.
  - Keep all package-generated manifests, native logs, traceback files, and per-window outputs.
- Key outputs:
  - Real non-empty native outputs per successful window: `dt_*.ct`, `{catalog_code}.loc`, `{catalog_code}.reloc`, `{catalog_code}.res`
  - package window manifest such as `time_window_manifest.json`
  - `run_status_table.csv` listing every attempted window with status, selected event count, parameter summary, output folder, native log paths, and failure evidence paths

#### 1.5 Merge, event accounting, and final relocated catalog construction
- Task description: Build the merged full-catalog result from real native outputs and explicitly account for every input event.
- Required data sources:
  - `events.csv`
  - package window manifest and per-window native outputs
  - merged/native `.reloc`, `.loc`, `.res`
- Parameter selection strategy:
  - Merge relocated events by preserved event ID when available.
  - If any window output lacks explicit IDs, use only a verified within-window event identity mapping derived from package-preserved order and the window selection manifest.
  - Join relocated outputs back to the original catalog to create three mutually exclusive event classes:
    - relocated,
    - attempted but unrelocated,
    - failed/not produced because the run/window failed.
- Constraints:
  - Do not count missing events as relocated.
  - Separate scientific unrelocation from run failure.
  - Preserve original event metadata alongside relocated coordinates and diagnostic fields.
- Key outputs:
  - `relocated_catalog.csv` with original and relocated hypocenters, shifts, and selected relocation diagnostics
  - `unrelocated_events.csv` with explicit reasons
  - `failed_events_or_windows.csv` with failure kinds and evidence paths
  - `final_accounting_summary.json` proving all 29,896 input events are accounted for

#### 1.6 Residual, convergence, and quality diagnostics from native outputs
- Task description: Quantify relocation performance from real HypoDD outputs and residual files.
- Required data sources:
  - `.res` files from successful windows
  - `.loc` and `.reloc` files
  - original `events.csv`
- Parameter selection strategy:
  - Parse residuals using the package/native output convention that `RES [ms]` is already in milliseconds.
  - Compute per-window and global diagnostics:
    - residual distribution statistics,
    - relocated-event fraction,
    - horizontal and vertical shift magnitudes,
    - depth change statistics,
    - subset-by-subset and window-by-window comparison of relocation success.
- Constraints:
  - Do not re-scale residual units incorrectly.
  - Use only real successful outputs for scientific figures; if the production run fails, figures must be labeled as failure diagnostics only.
- Key outputs:
  - `residual_statistics.csv`
  - `relocation_shift_statistics.csv`
  - `window_quality_summary.csv`

#### 1.7 Figure generation from real outputs
- Task description: Create the required publication-style figures from the merged relocation results and diagnostics.
- Required data sources:
  - `relocated_catalog.csv`
  - original `events.csv`
  - `station.sta`
  - `main_earthquake.csv`
  - `residual_statistics.csv`
  - `relocation_shift_statistics.csv`
- Parameter selection strategy:
  - Use original event locations from `events.csv` as initial hypocenters.
  - Use relocated hypocenters from `relocated_catalog.csv`.
  - Overlay the 3 main earthquakes from `main_earthquake.csv` as labeled reference events.
  - Compute plotting bounds from the union of initial and relocated event extents plus station coverage.
- Constraints:
  - Only successful relocated events may be plotted as relocated results.
  - Unrelocated and failed events should be excluded from relocated-point layers or shown separately with clear labeling.
  - If no successful relocated events exist, generate only diagnostic failure figures with explicit labeling.
- Key outputs:
  - `figure_relocation_map` containing:
    - lon-lat panel with stations, initial locations in gray, relocated events in black, main earthquakes in red
    - lon-depth panel
    - lat-depth panel
  - `figure_residual_distribution`
  - `figure_relocation_shift`
  - `figure_relocation_statistics`
  - optional additional figure:
    - event-pair/link-density or relocation-success-by-window diagnostic panel

### Task 2: Optional fallback input-preparation branch only if direct `phase.dat` validation fails
- Task description: Rebuild package-ready inputs from tabular files only if the supplied `phase.dat` is proven invalid for the chosen `hypodd_runner` API path.
- Required data sources:
  - `events.csv`
  - `picks.csv`
  - `station.sta`
- Parameter selection strategy:
  - Preserve event IDs exactly from `events.csv`.
  - Preserve real P/S times from `picks.csv`; use missing tokens only for genuinely missing phases.
  - Preserve original station IDs unless a documented API path explicitly requires `NET.STA`; if so, apply one consistent mapping and save it.
- Constraints:
  - This branch is not the default.
  - Do not rebuild merely for convenience if direct `phase.dat` use succeeds.
  - Re-run the same validation manifest after rebuilding.
- Key outputs:
  - rebuilt `phase.dat` and `station.sta` only if needed
  - `station_id_mapping.csv` only if a prefix remapping is required
  - updated `input_manifest.json`

### Task dependency and execution flow
- Task 1.1 must complete before any relocation call.
- Task 1.2 depends on Task 1.1 and determines whether auto-window execution is mandatory; for this catalog it is expected to be mandatory.
- Task 1.3 uses bounded subset runs to choose production `Ph2dtParams` and `HypoDDParams.iter_rows`.
- Task 1.4 performs the single production full-catalog relocation using the chosen grouped parameters.
- Task 1.5 merges outputs and accounts for all events.
- Task 1.6 derives diagnostics from merged/native outputs.
- Task 1.7 generates the required figures from successful relocation outputs.
- Task 2 is activated only if Task 1.1 shows that direct `phase.dat` usage is invalid for the package path being used.