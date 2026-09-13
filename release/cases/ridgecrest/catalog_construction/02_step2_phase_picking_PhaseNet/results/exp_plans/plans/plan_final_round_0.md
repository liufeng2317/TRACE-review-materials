# Goal
Run deep-learning seismic phase picking with PhaseNet on the provided Ridgecrest continuous MiniSEED data for 2019-07-04 to 2019-07-26 using the original pretrained model on NPU, produce one merged daily CSV per day (`picks_YYYYMMDD.csv` for 20190704 through 20190725) with the requested schema and UTCDateTime-formatted phase times, and generate one representative figure showing the picking process.

## Planning Assumptions
- Observation data are available and sufficient, so only the provided MiniSEED files and `station.sta` metadata will be used.
- Processing window is the half-open interval:
  - `start_time = UTCDateTime("2019-07-04T00:00:00Z")`
  - `end_time = UTCDateTime("2019-07-26T00:00:00Z")`
  This corresponds to day folders `20190704` through `20190725` only.
- PhaseNet package/model contract from retrieved metadata:
  - Network model path: `<PROJECT_ROOT>/seismoagent/library/ai_module/phase_picking/model/phasenet.py`
  - Inference example path: `<PROJECT_ROOT>/seismoagent/library/ai_module/phase_picking/inference/phasenet.py`
  - Retrieved PhaseNet model args: `in_channels=3`, `classes=3`, `phases='NPS'`, `sampling_rate=100`, `norm='std'`, `filter_factor=1`
  - Retrieved default inference args: `detection_threshold=0.3`, `blinding=[0,0]`, `overlap=1500`
  - Retrieved SeisBench API indicates `model.classify(...)` should be used for discrete picks and `model.annotate(...)` can be used for diagnostic probability traces.
- The exact original pretrained checkpoint path was not returned by the retriever in this session; path not found, please retrieve again.
- NPU is explicitly required. To avoid NPU re-initialization in forked subprocesses, multiprocessing must use a spawn-based start method, and model/NPU initialization must occur inside worker initialization rather than in the parent process.
- Workflow should stay in one primary task script because discovery, QC, NPU-safe multiprocessing, inference, amplitude extraction, CSV merge, validation, and diagnostic plotting are tightly coupled.
- All exported times must remain ObsPy `UTCDateTime` ISO-8601 UTC strings ending in `Z`; no UNIX timestamps.
- Success evidence is the presence of valid daily merged CSV outputs with the exact requested header and one real diagnostic figure from processed data; worker completion alone is not sufficient.

## Analysis Plan
### Task 1: Build and run one primary PhaseNet picking workflow
- Task description
  - Create one end-to-end script that inventories the 22 requested daily folders, validates waveform and station metadata, runs NPU-safe multiprocessing PhaseNet inference per station-day file, extracts P/S picks and raw-waveform amplitudes, merges results into one CSV per day, validates merged outputs, and generates one representative diagnostic figure.
- Required data sources
  - `<CASE_ROOT>/catalog_construction/01_step1_data_preprocessing_for_phasepicking/exp_run/outputs/01_preprocess_ridgecrest_stationday_waveforms/phase_picking`
  - `<CASE_ROOT>/catalog_construction/01_step1_data_preprocessing_for_phasepicking/exp_run/outputs/01_preprocess_ridgecrest_stationday_waveforms/station.sta`
  - `<PROJECT_ROOT>/seismoagent/library/ai_module/phase_picking/model/phasenet.py`
  - Original PhaseNet pretrained weights: path not found, please retrieve again.
- Parameter selection strategy
  - Define script variables for `start_time`, `end_time`, worker count, thresholds, overlap, and NPU device selection.
  - Use one station-day MiniSEED file as the atomic multiprocessing work unit.
  - Use at least 32 worker processes with spawn-based multiprocessing.
- Constraints
  - Do not split this into separate config-only or validation-only scripts.
  - Do not initialize NPU or load PhaseNet in the parent process before worker spawn.
- Key outputs
  - `picks_20190704.csv`
  - `picks_20190705.csv`
  - One diagnostic figure for a real processed example
  - Run summary with counts of files, skips, failures, and P/S pick totals

#### Task 1.1: Input discovery and metadata validation
- Task description
  - Enumerate the requested day folders, parse waveform filenames, and build a validated workload list cross-checked against station metadata.
- Required data sources
  - Daily folders `20190704` through `20190725`
  - `station.sta`
- Parameter selection strategy
  - Use:
    - `start_time = UTCDateTime("2019-07-04T00:00:00Z")`
    - `end_time = UTCDateTime("2019-07-26T00:00:00Z")`
  - Convert the interval `[start_time, end_time)` to day keys `20190704` through `20190725`.
  - Parse filenames of the form `{network}.{station}.{start_time}.{end_time}.mseed`.
  - Derive `station_id` from the first two dot-separated fields as `network.station`.
  - Parse `station.sta` as a comma-separated file without assuming a header; use the first field as the authoritative station key.
- Constraints
  - Only include files belonging to the requested 22 daily windows.
  - Reject or log files whose filename time span lies fully outside the requested interval.
  - Keep waveform filename station IDs unchanged for output CSVs.
  - Missing metadata matches should be logged; if station ID from filename is valid enough for picking, do not block processing unless strict station filtering is required by downstream logic.
- Key outputs
  - Validated workload manifest with day, station_id, file path, filename-derived start/end times, metadata-match flag
  - Station lookup table keyed by `network.station`
  - Counts of valid, skipped, and metadata-missing files

#### Task 1.2: Waveform read, QC, and PhaseNet input preparation
- Task description
  - Read each station-day MiniSEED file, verify it is usable for 3-component PhaseNet inference, standardize trace organization, and preserve raw waveform access for amplitude extraction.
- Required data sources
  - Station-day MiniSEED files
- Parameter selection strategy
  - Use ObsPy to read each file, sort traces, merge fragments if needed, and trim to the intersection of the filename time span with the requested global window.
  - Verify component availability, timing consistency, and sampling rate consistency.
  - Reorder traces to the input convention required by the local PhaseNet inference implementation.
  - If the data are not already at the retrieved PhaseNet sampling rate of 100 Hz, resample only if required by the actual inference interface.
- Constraints
  - Require 3-component input unless the verified local inference wrapper explicitly supports missing-channel handling.
  - Do not alter absolute timing.
  - Preserve raw or raw-equivalent waveform values for later `phase_amplitude` extraction.
  - If a file cannot form a valid 3-component stream, skip it and log the reason.
- Key outputs
  - Per-file validated 3-component stream ready for PhaseNet inference
  - QC log for sampling rate, component availability, merge decisions, and skipped files

#### Task 1.3: NPU-safe multiprocessing PhaseNet inference
- Task description
  - Run PhaseNet inference in parallel over all valid station-day files using at least 32 processes, with progress reporting and failure capture.
- Required data sources
  - Validated waveform streams from Task 1.2
  - PhaseNet model assets
- Parameter selection strategy
  - Use a spawn-based multiprocessing start method.
  - Initialize NPU runtime and load the PhaseNet model once inside each worker.
  - Use the requested original pretrained PhaseNet model after the exact checkpoint path is retrieved.
  - Use `model.classify(...)` as the primary inference path for discrete picks.
  - Start with retrieved default inference values:
    - detection threshold `0.3`
    - overlap `1500`
    - blinding `[0,0]`
  - Keep thresholds constant across both days unless the verified local wrapper exposes required phase-specific arguments.
  - Set worker count to at least 32; if a higher safe value is available, it may be used, but not fewer than 32.
- Constraints
  - No CPU-only execution branch is needed.
  - Parent process must not pre-initialize NPU.
  - Progress reporting should include day-level submission and per-file start/finish or completion counts where practical.
  - File-level failures must be captured with station ID, day, file path, and exception summary.
  - Successful worker runs do not count as success unless merged daily CSV outputs are valid.
- Key outputs
  - Per-file discrete pick records with pick time, score, phase type, and source station/day context
  - Runtime progress log
  - Failure inventory for skipped or failed files

#### Task 1.4: Pick postprocessing and raw-waveform amplitude extraction
- Task description
  - Convert discrete PhaseNet outputs into the requested schema and compute amplitude at each pick time from the waveform.
- Required data sources
  - Pick results from Task 1.3
  - Raw waveform access preserved from Task 1.2
- Parameter selection strategy
  - Keep only P and S picks.
  - Convert each pick time to ObsPy `UTCDateTime` ISO-8601 string ending in `Z`.
  - Use `phase_score` from the PhaseNet pick confidence/probability returned by `classify(...)`.
  - Extract `phase_amplitude` from the nearest waveform sample at the pick time using one fixed rule:
    - P pick: absolute amplitude on the vertical component if clearly identified
    - S pick: maximum absolute amplitude across the two horizontal components if clearly identified
    - fallback: maximum absolute amplitude across all available components at the nearest sample
  - Record the amplitude rule used in the runtime metadata.
- Constraints
  - Amplitude must come from waveform space, not model probabilities or normalized inference tensors.
  - Do not shift pick times during amplitude lookup.
  - If nearest-sample lookup is used, keep that rule fixed for all files.
- Key outputs
  - Per-pick records with columns:
    - `station_id`
    - `phase_time`
    - `phase_score`
    - `phase_amplitude`
    - `phase_type`

#### Task 1.5: Daily merge, CSV writing, and immediate validation
- Task description
  - Merge station-level picks into one CSV per day, enforce the exact schema, and validate the merged scientific outputs.
- Required data sources
  - Per-pick records from Task 1.4
- Parameter selection strategy
  - Write exactly:
    - `picks_20190704.csv`
    - `picks_20190705.csv`
  - Include the exact header row:
    - `station_id,phase_time,phase_score,phase_amplitude,phase_type`
  - Sort rows by `phase_time`, then `station_id`, then `phase_type`.
  - Filter picks so each file only contains picks within its UTC day.
- Constraints
  - No UNIX timestamps in outputs.
  - Validate that:
    - `phase_type` is only `P` or `S`
    - `phase_time` parses back to ObsPy `UTCDateTime`
    - numeric fields are finite
    - station IDs remain in `network.station` form
  - If a day yields zero picks, still write a header-only CSV and record the zero-pick condition explicitly.
  - Empty or malformed merged outputs are failures unless explicitly justified by the validated run summary.
- Key outputs
  - `picks_20190704.csv`
  - `picks_20190705.csv`
  - Daily validation summary with files attempted, files succeeded, files failed, total P picks, total S picks, total rows written

#### Task 1.6: Representative picking-process figure
- Task description
  - Generate one real figure from the processed data showing the waveform and the resulting PhaseNet picks.
- Required data sources
  - One successfully processed station-day waveform
  - Corresponding pick results
  - Optional `model.annotate(...)` probability traces for the same example
- Parameter selection strategy
  - Choose one case from the processed days with clear P and S picks and good waveform quality.
  - Plot a focused time window around one picked event or pick cluster rather than the full 24-hour record.
  - Overlay P and S pick markers on the waveform.
  - If readily available from the same workflow, add aligned probability traces from `annotate(...)` to illustrate the picking process.
- Constraints
  - One case is sufficient.
  - Use actual processed results only.
  - Time labels shown in the figure must remain UTC.
- Key outputs
  - One diagnostic figure demonstrating the picking process
  - Companion metadata identifying the source station-day file and plotted UTC time window

#### Task 1.7: Final workflow validation and failure evidence collection
- Task description
  - Confirm that the end-to-end workflow succeeded both technically and scientifically.
- Required data sources
  - Daily CSV outputs
  - Runtime logs
  - Diagnostic figure
  - Station lookup from Task 1.1
- Parameter selection strategy
  - Verify that both daily CSV files exist and contain the exact requested header.
  - Check representative rows and full-schema consistency for parsable UTC times, valid phase labels, and finite score/amplitude values.
  - Cross-check CSV station IDs against the station lookup where available.
  - Confirm the diagnostic figure corresponds to a real processed file and day in the run manifest.
- Constraints
  - Per-file success is insufficient unless daily merged outputs are valid.
  - Preserve all skip and failure evidence with file-level context.
- Key outputs
  - Final validation summary
  - Failure/skip inventory
  - Run manifest linking input files, daily outputs, and the diagnostic figure