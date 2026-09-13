# Goal
Run PhaseNet phase picking on the Ridgecrest continuous MiniSEED archive for 2019-07-04 to 2019-07-26 using the original pretrained model on NPU, generate one merged pick CSV per day (`picks_YYYYMMDD.csv`) with the requested columns and UTCDateTime-formatted phase times, and produce one diagnostic figure illustrating the picking process.

## Planning Assumptions
- Observation data are available and sufficient, so only the provided MiniSEED files and `station.sta` metadata will be used.
- Requested model is PhaseNet with the original pretrained version. Retrieved model contract requires using the PhaseNet network and original/default inference pattern; if the explicit original checkpoint path is not retrievable from metadata, use the PhaseNet original pretrained identifier in the package loader and verify the loaded checkpoint name before execution. Full retrieved PhaseNet paths available from metadata include:
  - Network model path: `<PROJECT_ROOT>/seismoagent/library/ai_module/phase_picking/model/phasenet.py`
  - Example inference path: `<PROJECT_ROOT>/seismoagent/library/ai_module/phase_picking/inference/phasenet.py`
  - An available retrieved pretrained checkpoint path is `<PROJECT_ROOT>/seismoagent/library/ai_module/phase_picking/pretrained/v3/phasenet/geofon.pt.v2`, but this is example-specific to GEOFON and must not replace the requested “original” model unless verification shows that no original checkpoint metadata can be retrieved.
- PhaseNet/SeisBench contract from retrieved API docs: PhaseNet is a 3-component model; discrete picks are obtained through classification/aggregation from annotation probabilities; pick thresholds are controlled through phase-specific threshold arguments.
- Time handling constraint: all internal and output times must remain ISO-8601 UTC strings compatible with ObsPy `UTCDateTime`; no UNIX timestamps.
- Multiprocessing constraint: because NPU re-initialization in forked subprocesses must be avoided, the script should use a spawn-based multiprocessing start method and initialize the PhaseNet model once inside each worker process, not in the parent before pool creation.
- Processing window constraint: only folders/datasets intersecting `20190704` through `20190725` are processed; `start_time` and `end_time` must be explicit script variables for scalability.
- Output success evidence: for each day, a non-empty or explicitly validated empty `picks_YYYYMMDD.csv` with header row must be produced, and the merged daily file must contain only the required columns in the requested order. A diagnostic plot for at least one waveform case with picks overlaid must also be produced.

## Analysis Plan
### Task 1: End-to-end daily PhaseNet picking and output generation
- Task description
  - Build one primary script that scans the 22 requested daily folders, maps waveform files to stations using filename prefixes and `station.sta`, runs PhaseNet inference on NPU in parallel, extracts P and S picks with confidence scores and waveform amplitudes, merges station-level results into one CSV per day, and generates one diagnostic plot for a representative case.
- Required data sources
  - `<CASE_ROOT>/catalog_construction/01_step1_data_preprocessing_for_phasepicking/exp_run/outputs/01_preprocess_ridgecrest_stationday_waveforms/phase_picking`
  - `<CASE_ROOT>/catalog_construction/01_step1_data_preprocessing_for_phasepicking/exp_run/outputs/01_preprocess_ridgecrest_stationday_waveforms/station.sta`

#### Subtask 1.1: Inventory and metadata validation
- Task description
  - Enumerate day folders between the script variables `start_time=2019-07-04T00:00:00Z` and `end_time=2019-07-26T00:00:00Z`, collect all MiniSEED files in `20190704` through `20190725`, and parse `station.sta` into a station lookup table keyed by `network.station`.
- Required data sources
  - Phase-picking MiniSEED directory
  - `station.sta`
- Parameter selection strategy
  - Restrict folder selection to dates whose 24-hour spans overlap the requested interval.
  - Parse station identifiers from file names of the form `{network}.{station}.{start_time}.{end_time}.mseed`.
  - Treat the first field of each `station.sta` row as `station_id` and use remaining fields only for optional validation/annotation.
- Constraints
  - Reject files whose filename time range falls completely outside the requested window.
  - Log missing station metadata matches but do not block picking if the waveform filename already provides `station_id`.
  - Preserve one file per station-day as the unit of parallel work.
- Key outputs
  - Validated station-day work list for 20190704 through 20190725
  - Station metadata lookup table
  - Inventory summary table: day, station_id, file path, file time span, metadata match flag

#### Subtask 1.2: Waveform loading and preprocessing for PhaseNet
- Task description
  - For each station-day file, read the MiniSEED stream, verify three-component availability and timing consistency, standardize component naming/order for PhaseNet input, trim exactly to the file time range intersected with the requested window, and preserve original waveform values for amplitude extraction.
- Required data sources
  - Phase-picking MiniSEED files
- Parameter selection strategy
  - Use ObsPy read/load workflow for MiniSEED.
  - Derive per-file processing interval from filename start/end times, then intersect with global script window.
  - Use component order required by the inference implementation; if the package loader documents component order, follow that contract exactly; otherwise verify order from available traces and record it.
  - If sample rate differs from the model’s expected rate, resample only if required by the PhaseNet inference interface; otherwise rely on model preprocessing if supported.
- Constraints
  - Require 3 components for standard PhaseNet inference; if a station-day lacks one component, flag and skip unless the chosen loader explicitly supports missing-channel padding.
  - Merge gaps/overlaps only if needed to create a continuous stream; document any gap handling in logs.
  - Keep a copy of the raw/working trace values needed for `phase_amplitude`.
- Key outputs
  - Per-station validated stream object ready for inference
  - Preprocessing log with skipped stations and reasons

#### Subtask 1.3: Parallel NPU PhaseNet inference
- Task description
  - Execute station-day picking with multiprocessing using at least 32 worker processes, with each worker initializing the NPU runtime and PhaseNet model inside the worker process under a spawn start method.
- Required data sources
  - Preprocessed station-day waveform streams
  - PhaseNet original pretrained model
- Parameter selection strategy
  - Set worker count to `max(32, available_npu_safe_worker_count)` while respecting system limits.
  - Initialize PhaseNet once per worker using the original pretrained identifier/checkpoint and NPU device selection variables.
  - Use PhaseNet inference/classification interface that returns discrete picks with per-pick score/probability.
  - Use P and S thresholds from the PhaseNet package defaults when not specified by the user; if explicit default thresholds are exposed by the loaded pretrained model, use them; otherwise record threshold values as script parameters and keep them constant for all files.
- Constraints
  - Do not initialize the model/NPU in the main process before worker spawning.
  - Use progress reporting for day-level submission, per-file start/finish, and per-file pick counts.
  - Batch execution is acceptable, but the final scientific output is the merged daily CSV, not successful worker completion alone.
  - If a worker fails on a file, capture the file path, exception summary, and continue processing remaining files.
- Key outputs
  - Per-station pick results containing at minimum station_id, pick time, phase label, score/probability
  - Execution log with processing status and failures

#### Subtask 1.4: Pick postprocessing and amplitude extraction
- Task description
  - Convert model outputs into the requested tabular schema and compute `phase_amplitude` from the waveform at each pick time.
- Required data sources
  - Per-station pick results
  - Original/working waveform traces
- Parameter selection strategy
  - Map phase labels to `"P"` and `"S"` only.
  - Convert each pick time to ObsPy `UTCDateTime` ISO string with trailing `Z`.
  - Extract amplitude from the raw waveform nearest the pick sample; if three components are present, use a predefined amplitude rule and keep it fixed across all files.
- Constraints
  - Because the user specified “Amplitude at phase time (from raw waveform),” do not use model probabilities or normalized tensors as amplitude.
  - The amplitude definition must be explicit in the script metadata. Recommended fixed rule: absolute amplitude on the vertical component for P picks and maximum absolute amplitude across horizontal components for S picks; if component mapping is ambiguous, use maximum absolute amplitude across all available components and record the rule.
  - Remove duplicate picks only if the inference interface can emit overlapping-window duplicates; de-duplication tolerance should be a fixed script parameter and phase-specific if needed.
- Key outputs
  - Station-level pick tables with columns:
    - `station_id`
    - `phase_time`
    - `phase_score`
    - `phase_amplitude`
    - `phase_type`

#### Subtask 1.5: Daily merge, validation, and CSV writing
- Task description
  - Concatenate all station-level picks for each day into one day file and validate schema, sort order, and day membership.
- Required data sources
  - Station-level pick tables
- Parameter selection strategy
  - Write exactly one file per processed day:
    - `picks_20190704.csv`
    - `picks_20190705.csv`
  - Sort rows by `phase_time`, then `station_id`, then `phase_type`.
  - Filter picks so that each daily file contains only picks within its 24-hour UTC day.
- Constraints
  - Always include header row with exactly:
    - `station_id,phase_time,phase_score,phase_amplitude,phase_type`
  - Validate all `phase_type` values are only `P` or `S`.
  - Validate `phase_time` strings parse back to ObsPy `UTCDateTime`.
  - If a day yields zero picks, still write the header-only CSV and record the zero-pick condition explicitly.
- Key outputs
  - `picks_20190704.csv`
  - `picks_20190705.csv`
  - Daily validation summary: file count processed, station count attempted, stations succeeded, total P picks, total S picks, total rows written

#### Subtask 1.6: Diagnostic figure for one representative case
- Task description
  - Produce one figure demonstrating the picking process on a selected station-day waveform with PhaseNet picks overlaid.
- Required data sources
  - One representative waveform file from the processed set
  - Corresponding pick results
- Parameter selection strategy
  - Choose a case with both P and S picks and visually clear signal, prioritizing a station-day with multiple confident picks.
  - Plot the three-component waveform over a selected time window around one event/pick cluster.
  - Overlay vertical markers for P and S picks and annotate with phase score values if legible.
  - Optionally include a second panel of PhaseNet probability traces if directly available from the inference interface without a separate workflow.
- Constraints
  - One case is sufficient.
  - The figure should demonstrate the relationship between waveform features and picked phase times; avoid plotting the entire 24-hour record if a focused event window is more interpretable.
- Key outputs
  - One diagnostic pick-visualization figure
  - Companion metadata record identifying station, source file, plotted time window, and number of picks shown