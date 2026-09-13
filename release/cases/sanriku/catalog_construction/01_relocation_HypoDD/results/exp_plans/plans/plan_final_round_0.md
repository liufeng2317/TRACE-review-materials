# Goal

Relocate the full Japan Aomori regional JMA catalog with `hypodd_runner` in catalog-only mode using the provided regional observation inputs, preserve native event/station identities, select scientifically justified `Ph2dtParams` and explicit `HypoDDParams(iter_rows=...)` for this catalog, execute a package-supported full-catalog windowed workflow based on real native HypoDD runs, and produce merged relocation products, full event accounting, and figures derived only from successful native outputs.

## Planning Assumptions

- Use observation data only from `<CASE_ROOT>/data/regional`: `phase.dat`, `station.sta`, `events.csv`, `picks.csv`, `summary.txt`, `main_earthquake.csv`.
- `phase.dat` is the preferred primary phase input. Do not rebuild it from `picks.csv` unless direct validation fails for the selected `hypodd_runner` API path.
- Preserve original station IDs because `phase.dat` and `station.sta` are expected to be internally consistent. Add a synthetic prefix such as `J.` only if the validated public API path explicitly requires `NET.STA`, and then apply one consistent mapping across all generated inputs and all merge/accounting logic.
- Preserve source `event_id` values and UTC-compatible ISO origin times through validation, relocation, merging, and final accounting.
- `hypodd_runner` public grouped-parameter API must be used: `HypoDDInputs`, `EventSelection`, `Ph2dtParams`, `HypoDDParams`, and `RuntimeOptions`.
- Catalog-only entry points should follow package-supported workflow: use `run_catalog_only_relocation(...)` only for bounded diagnostic subset/window tests and use `run_catalog_only_auto_time_windows(...)` for the full regional catalog if native limits are exceeded.
- In this environment, `HypoDDInputs.hypo_root` must be `<LOCAL_PATH>
- Package/native scale limits shape execution strategy:
  - `ph2dt.inc`: `MEV=16000`, `MSTA=2400`, `MOBS=500`
  - `hypoDD.inc`: `MAXEVE=10800`, `MAXDATA=3100000`, `MAXSTA=1300`, `MAXCL=100`
- Because the catalog has 29,896 events, one native full-catalog HypoDD run exceeds `MAXEVE=10800`; production execution should therefore use `run_catalog_only_auto_time_windows(...)` or another documented package-supported helper path that preserves all events in final accounting.
- `phase_format="auto"` is the safest default unless validation proves a stricter explicit format is required.
- `HypoDDParams.iter_rows` must be explicitly defined. Each row is `NITER WTCCP WTCCS WRCC WDCC WTCTP WTCTS WRCT WDCT DAMP`, and `NITER` values are cumulative iteration endpoints.
- For this catalog-only task, CC terms should remain zero in all iteration rows because waveform cross-correlation is not part of the requested workflow.
- The supplied 1-D velocity model must be used in relocation:
  - `mod_top = [0.0, 5.0, 10.0, 20.0, 35.0, 50.0, 90.0]`
  - `mod_vel = [5.4, 5.8, 6.2, 6.6, 7.2, 7.6, 8.05]`
  - `mod_ratio = 1.73` unless a better documented Vp/Vs estimate is derived from the current catalog metadata and recorded.
- `dep_corr` should default to `0.0` unless the current catalog metadata explicitly justify a nonzero depth datum correction.
- Parameter screening must be bounded to representative subsets/windows before one production full-catalog run; do not perform a broad full-catalog parameter sweep.
- For the production scientific run, use fail-fast behavior (`continue_on_error=False`) after parameter selection so failed windows leave native evidence for diagnosis.
- Full-run success requires real non-empty native outputs such as `dt_*.ct`, `{catalog_code}.loc`, `{catalog_code}.reloc`, and `{catalog_code}.res`, plus merged relocated results built from those native outputs and explicit accounting of relocated, unrelocated, and failed events.
- Empty files, unchanged original catalog rows, validation-only artifacts, schema-only outputs, mock relocation, or plotting-only products are not success.
- In native `.res` outputs, `RES [ms]` should be treated as already in milliseconds.

## Analysis Plan

### Task 1 — Build one primary self-contained `hypodd_runner` workflow script

- Task description
  - Write one cohesive Python script that performs:
    1. input validation and identity checks,
    2. native-limit assessment and supported execution-path selection,
    3. bounded parameter screening on representative windows,
    4. production full-catalog relocation with grouped `hypodd_runner` objects,
    5. merged event accounting and native-output validation,
    6. statistics and figure generation from real outputs only.
  - Keep configuration, API use, execution, immediate output checks, merged-output validation, and failure-evidence collection in the same script.

- Required data sources
  - `<CASE_ROOT>/data/regional/phase.dat`
  - `<CASE_ROOT>/data/regional/station.sta`
  - `<CASE_ROOT>/data/regional/events.csv`
  - `<CASE_ROOT>/data/regional/picks.csv`
  - `<CASE_ROOT>/data/regional/summary.txt`
  - `<CASE_ROOT>/data/regional/main_earthquake.csv`

- Parameter selection strategy
  - Set `HypoDDInputs.hypo_root` to `<LOCAL_PATH>
  - Use the provided `phase.dat` directly as `HypoDDInputs.phase_file` if validation succeeds.
  - Use the provided `station.sta` directly as `HypoDDInputs.station_file`.
  - Set one stable Aomori-specific `catalog_code` and use it consistently across diagnostic runs, production windows, merged outputs, and figure labels.
  - Use `events.csv` to derive actual full-catalog `ot_range`, `lat_range`, and `lon_range`; cross-check with `summary.txt`.
  - Set `EventSelection.phase_format="auto"` unless direct validation proves a more specific setting is required.
  - Set `EventSelection.dep_corr=0.0` unless the current metadata justify otherwise.

- Constraints
  - Do not replace `hypodd_runner` with custom relocation code or hand-written relocation formulas.
  - Do not split the workflow into config-only or wrapper-only scripts.
  - Do not treat Python completion alone as success; require non-empty native outputs and valid merged relocation products.
  - Do not invent or silently alter event IDs.

- Key outputs
  - One self-contained relocation workflow script.
  - One compact parameter manifest summarizing grouped objects actually used.
  - One run registry covering every attempted diagnostic and production run/window.

#### Task 1.1 — Validate inputs and preserve identities

- Task description
  - Confirm that the provided `phase.dat` and `station.sta` are package-ready and that identifiers can be preserved through later merges.

- Required data sources
  - `phase.dat`
  - `station.sta`
  - `events.csv`
  - `picks.csv`
  - `summary.txt`

- Parameter selection strategy
  - Parse `events.csv` to determine:
    - total event count,
    - unique `event_id` count,
    - time range,
    - latitude/longitude/depth range,
    - magnitude availability,
    - optional per-event pick counts if present or derivable.
  - Parse `phase.dat` to confirm:
    - valid event-block structure,
    - non-empty event and pick sections,
    - parseable event headers,
    - usable station IDs,
    - event count consistency with the catalog.
  - Verify that all station codes referenced in `phase.dat` exist in `station.sta`.
  - Compare event counts, pick counts, and station counts against `summary.txt`.
  - Use `picks.csv` only to diagnose mismatches or validate phase availability; do not rebuild `phase.dat` in the default path.
  - Preserve original station IDs if validation succeeds.
  - If the selected validated API path requires `NET.STA`, create one explicit station mapping table and apply it consistently to all generated package inputs and later merge keys.

- Constraints
  - Do not rebuild `phase.dat` for convenience if direct validation succeeds.
  - Preserve `event_id` and origin times exactly in manifests.
  - Any fallback identity mapping based on event order must be verified against the package run/window manifest before use in merging.

- Key outputs
  - Input validation manifest with source paths, counts, ranges, and validation results.
  - Phase/station consistency table listing missing stations, malformed headers, or duplicate IDs if any.
  - Explicit decision flag showing whether original station IDs were kept or remapped.
  - Event identity manifest for later join-back to native outputs.

#### Task 1.2 — Assess native limits and choose the production execution mode

- Task description
  - Determine the supported execution strategy for this catalog and define the windowing plan needed to stay within native HypoDD limits.

- Required data sources
  - `events.csv`
  - `phase.dat`
  - validation counts from Task 1.1

- Parameter selection strategy
  - Compare full catalog size against native limits, especially `MAXEVE=10800`.
  - Because 29,896 events exceed `MAXEVE`, set production mode to `run_catalog_only_auto_time_windows(...)`.
  - Estimate events per coarse time unit from `events.csv`; start with the coarsest likely valid windows, such as monthly or multi-week windows.
  - Reduce time-window size only if estimated or observed per-window event/data volume still exceeds native limits or produces native limit failures.
  - Preserve all selected input events in final accounting across windows.

- Constraints
  - Do not hand-write a custom batching strategy if the package-supported auto-window helper expresses the task.
  - Do not drop oversize windows or silently exclude events to satisfy limits.
  - Production run should use `continue_on_error=False` after parameter selection.

- Key outputs
  - Catalog scale check summary.
  - Window planning summary with estimated event counts per candidate coarse window.
  - Explicit production execution mode record.

#### Task 1.3 — Derive catalog diagnostics needed for `Ph2dtParams` and `iter_rows`

- Task description
  - Use actual Aomori catalog characteristics to support defensible parameter choices instead of relying on defaults.

- Required data sources
  - `events.csv`
  - `picks.csv`
  - `phase.dat`
  - `station.sta`

- Parameter selection strategy
  - Compute:
    - events per time window,
    - pick-count distribution per event,
    - station participation counts,
    - stations-per-event distribution if derivable,
    - P/S availability and relative abundance,
    - indicative link density for representative dense and sparse windows.
  - Use these diagnostics to guide:
    - minimum shared observations between event pairs,
    - nearest-neighbor or pair caps,
    - observation caps that limit `dt.ct` inflation,
    - relative P and S catalog weighting in `iter_rows`,
    - residual and distance controls.

- Constraints
  - Diagnostics are for parameterization only, not for claiming relocation success.
  - Do not infer measurement precision or bin widths from decimal places alone.

- Key outputs
  - Pre-run catalog diagnostic summary table.
  - Pairability/link-density diagnostic table for representative windows.
  - Candidate parameter ranges for `Ph2dtParams` and `HypoDDParams`.

#### Task 1.4 — Perform bounded screening of `Ph2dtParams` and explicit `HypoDDParams.iter_rows`

- Task description
  - Run a limited number of real diagnostic subset/window relocations to choose production parameters.

- Required data sources
  - validated `phase.dat`
  - validated `station.sta`
  - `events.csv`
  - diagnostics from Task 1.3

- Parameter selection strategy
  - Select at least:
    - one dense representative time window,
    - one sparser or more difficult window if temporal density varies materially.
  - Use `run_catalog_only_relocation(...)` for these diagnostic windows if they remain below native limits.
  - Test a small number of candidate `Ph2dtParams` settings shaped by observed pick coverage and event-link density.
  - Explicitly define catalog-only `iter_rows` candidates with:
    - `WTCCP=0`, `WTCCS=0`, `WRCC=0`, `WDCC=0` in all rows,
    - nonzero `WTCTP`, optional smaller `WTCTS`,
    - explicit `WRCT`, `WDCT`, and `DAMP`.
  - Compare at least two damping schedules, including one with larger LSQR damping in the requested tens-to-hundreds range such as `80–120`.
  - Choose cumulative iteration endpoints that begin conservatively and only tighten/refine if diagnostics show better residuals without unacceptable event loss or instability.
  - Record actual tested `iter_rows` values, not only narrative rationale.

- Constraints
  - Do not run a large parameter sweep across the full catalog.
  - Do not use `iter_rows=None` as the scientific production default.
  - Empty `.reloc`, empty `dt_*.ct`, unstable or divergent residual behavior, or unchanged original locations are rejection evidence.
  - Use real native outputs and logs for comparison.

- Key outputs
  - Diagnostic run status table with:
    - subset/window definition,
    - attempted event count,
    - `Ph2dtParams` summary,
    - explicit `iter_rows`,
    - runtime,
    - native output presence/non-emptiness,
    - relocated-event count,
    - residual summary,
    - failure evidence paths.
  - Selected production `Ph2dtParams`.
  - Selected production `HypoDDParams`, including explicit `iter_rows` and velocity model fields.

#### Task 1.5 — Execute the production full-catalog relocation

- Task description
  - Run the full regional catalog relocation with grouped `hypodd_runner` objects and package-supported auto time windows.

- Required data sources
  - validated `phase.dat`
  - validated `station.sta`
  - full-catalog bounds from `events.csv`
  - selected parameter set from Task 1.4

- Parameter selection strategy
  - Construct:
    - `HypoDDInputs` with `hypo_root`, direct phase file, direct station file, stable `catalog_code`, and explicit output folder name,
    - `EventSelection` using full observed `ot_range`, `lat_range`, `lon_range`, `dep_corr=0.0`, `phase_format="auto"`,
    - production `Ph2dtParams`,
    - `HypoDDParams` with `mod_top`, `mod_vel`, `mod_ratio=1.73` unless updated by documented evidence, and selected explicit `iter_rows`,
    - `RuntimeOptions` sized to the current environment without replacing package window handling.
  - Use `run_catalog_only_auto_time_windows(...)` for the production run.
  - Keep the coarsest valid time windows that remain under native limits.
  - Set `continue_on_error=False` for the production scientific run.
  - Retain all package and native logs, traceback files, manifests, and per-window outputs.

- Constraints
  - Do not truncate the catalog to fit one native run.
  - Do not silently drop windows or events.
  - Successful production requires real non-empty native outputs for successful windows and a later valid merged relocated catalog.

- Key outputs
  - Per-window run manifest/status table with:
    - window ID and time range,
    - input/selected event counts,
    - status,
    - grouped-parameter summary,
    - output folder name,
    - native log paths,
    - failure evidence paths if applicable.
  - Native per-window `dt_*.ct`, `{catalog_code}.loc`, `{catalog_code}.reloc`, and `{catalog_code}.res` outputs for successful windows.
  - Production run registry covering all attempted windows.

#### Task 1.6 — Merge native outputs and account for every input event

- Task description
  - Build the final merged relocation products from real native outputs and classify all input events.

- Required data sources
  - `events.csv`
  - per-window native outputs from Task 1.5
  - event identity manifest from Task 1.1
  - production run manifest from Task 1.5

- Parameter selection strategy
  - Merge relocated events using preserved `event_id` wherever available.
  - If any native output requires a verified within-window identity mapping, use only the mapping created and validated from the same run/window.
  - Classify each input event into exactly one of:
    - relocated,
    - attempted but unrelocated,
    - failed window/run with explicit reason,
    - excluded before run only if validation documented a specific exclusion.
  - Preserve original hypocenter, relocated hypocenter, origin time, magnitude, and provenance metadata side by side.

- Constraints
  - Do not count unrelocated or failed events as relocated.
  - Do not use unchanged original catalog rows as surrogate relocation outputs.
  - Do not infer relocation success from `.loc` alone without valid non-empty `.reloc`.

- Key outputs
  - Final merged relocated catalog.
  - Unrelocated-event table with explicit reasons.
  - Failed-event/window table with evidence paths.
  - Final accounting summary proving all 29,896 input events are accounted for.

#### Task 1.7 — Compute residual and relocation-quality statistics

- Task description
  - Quantify relocation performance from real HypoDD outputs for scientific evaluation and plotting.

- Required data sources
  - merged relocated catalog
  - native `.res` files
  - native `.loc` and `.reloc` files
  - `events.csv`

- Parameter selection strategy
  - Parse residuals from native `.res` outputs and treat `RES [ms]` as milliseconds.
  - Compute:
    - per-window and global relocated-event counts,
    - residual mean, median, spread, percentiles, and tails,
    - optional P/S residual breakdown if fields allow,
    - horizontal shift, depth shift, and 3-D shift,
    - relocation success fractions by time window and other available event attributes.
  - Compare initial vs relocated statistics only for events with real relocated solutions.

- Constraints
  - Do not rescale residual units incorrectly.
  - Do not mix failed-window artifacts into scientific statistics unless clearly labeled as failure evidence.

- Key outputs
  - Residual summary table.
  - Relocation shift summary table.
  - Window quality summary table.
  - Plot-ready catalog comparison table.

### Task 2 — Generate required figures from real relocation outputs only

- Task description
  - Create the required figure set from the merged relocation outputs and statistics. If no real relocated events exist, generate only clearly labeled diagnostic/failure-evidence figures.

- Required data sources
  - merged relocated catalog from Task 1.6
  - `events.csv`
  - `station.sta`
  - `main_earthquake.csv`
  - residual and shift summaries from Task 1.7
  - run/accounting tables from Task 1.6

- Parameter selection strategy
  - Use the actual catalog bounds from `events.csv` and the relocated catalog to set map and section extents.
  - Use original event locations in gray and relocated event locations in black, restricted to the same relocated-event subset when making direct comparisons.
  - Plot stations from `station.sta` and main earthquakes from `main_earthquake.csv` as red contextual markers.
  - Build residual and shift figures only from successful native outputs.

- Constraints
  - Figures must be derived only from real native relocation outputs.
  - If no real relocated events exist, figures must be labeled diagnostic/failure evidence and must not satisfy success criteria.
  - Unrelocated and failed events must not be displayed as relocated results.

- Key outputs
  - Relocation map figure with:
    - lon-lat map showing stations, initial locations in gray, relocated events in black, and main earthquakes in red,
    - lon-depth section,
    - lat-depth section.
  - Residual distribution figure from native `.res` outputs.
  - Relocation shift figure showing relocation offsets relative to initial locations.
  - Statistic figure summarizing:
    - total/attempted/relocated/unrelocated/failed counts,
    - initial vs relocated depth and other available distributions.
  - Optional additional figure only if based on real outputs, such as:
    - per-window relocation yield,
    - residual reduction by window,
    - shift versus depth, magnitude, or pick count.

### Task 3 — Conditional fallback branch only if direct `phase.dat` validation fails

- Task description
  - Rebuild package-ready phase input from tabular files only if the provided `phase.dat` is proven invalid for the selected public API path.

- Required data sources
  - `events.csv`
  - `picks.csv`
  - `station.sta`

- Parameter selection strategy
  - Preserve original `event_id`, origin time, and real P/S pick times from the tabular files.
  - Preserve original station IDs unless the validated API path explicitly requires `NET.STA`; if so, apply one consistent prefix mapping and record it.
  - Re-run the same validation checks from Task 1.1 on rebuilt inputs before relocation.

- Constraints
  - This branch is not the default path.
  - Rebuilt inputs are not relocation success by themselves.
  - Do not activate this branch merely for convenience.

- Key outputs
  - Rebuilt `phase.dat` only if needed.
  - Station mapping table only if remapping is required.
  - Updated input validation manifest showing the fallback path used.