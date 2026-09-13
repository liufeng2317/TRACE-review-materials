# Goal
Use the provided Ridgecrest continuous MiniSEED waveform data and station metadata to run PhaseNet phase picking for 2019-07-04 to 2019-07-26, producing one daily CSV of P/S picks per day and one illustrative figure showing the picking workflow on a representative station/day case.

## Planning Assumptions
- Observation data are available and sufficient; no synthetic or model-generated waveform data are needed.
- Requested processing window is exactly 22 daily windows: 2019-07-04 through 2019-07-25, corresponding to day folders `20190704` through `20190725`.
- Available waveform files are already preprocessed continuous 24-hour three-component MiniSEED files, one file per station per day.
- `station.sta` is the authoritative station metadata table for station identifiers and locations; the first comma-separated field matches waveform filename prefixes such as `CI.CCC`.
- PhaseNet package/model contract from retrieved information:
  - Network architecture path: `<PROJECT_ROOT>/seismoagent/library/ai_module/phase_picking/model/phasenet.py`
  - Inference example path: `<PROJECT_ROOT>/seismoagent/library/ai_module/phase_picking/inference/phasenet.py`
  - Preferred original pretrained weights path was not explicitly returned by the retriever; path not found, please retrieve again.
  - Retrieved PhaseNet contract indicates default model arguments including sampling rate 100 Hz, `norm="std"`, and default inference arguments including overlap 1500 and detection threshold 0.3.
  - SeisBench/PhaseNet supports pretrained loading plus annotation/classification workflows that convert probability annotations to discrete P/S picks.
- NPU execution is explicitly required; multiprocessing must therefore use a process start method and worker initialization strategy that avoids NPU context re-initialization after fork.
- Multiprocessing requirement is at least 32 processes; if NPU memory or device contention limits concurrent inference, workers should still be launched at 32 processes while controlling per-worker batch size and task granularity.
- All exported phase times must remain ISO 8601 UTC strings compatible with ObsPy `UTCDateTime`, not Unix timestamps.
- Success evidence for the primary workflow is: non-empty ``picks_YYYYMMDD.csv` for 20190704 through 20190725 with the requested header/columns, plus one valid picking illustration figure and a compact runtime summary of processed files and pick counts.

## Analysis Plan

### Task 1 — Build and validate the daily phase-picking workflow
- Task description:
  - Create one primary task script that reads station metadata and daily MiniSEED files, validates waveform completeness, runs PhaseNet inference on each station-day file, extracts P/S picks and amplitudes, writes one CSV per day, and saves one example figure.
- Required data sources:
  - `<CASE_ROOT>/catalog_construction/01_step1_data_preprocessing_for_phasepicking/exp_run/outputs/01_preprocess_ridgecrest_stationday_waveforms/phase_picking`
  - `<CASE_ROOT>/catalog_construction/01_step1_data_preprocessing_for_phasepicking/exp_run/outputs/01_preprocess_ridgecrest_stationday_waveforms/station.sta`
- Parameter selection strategy:
  - Define script variables:
    - `start_time = UTCDateTime("2019-07-04T00:00:00Z")`
    - `end_time = UTCDateTime("2019-07-26T00:00:00Z")`
  - Enumerate day folders intersecting `[start_time, end_time)`, i.e., `20190704` through `20190725`.
  - Match files by day folder and filename pattern `{network}.{station}.{start}.{end}.mseed`.
  - Parse station IDs from filenames and cross-check against `station.sta`; process only files with valid station identifiers in metadata.
  - Use the user-requested PhaseNet original pretrained model once the exact original weights path is retrieved/verified.
  - Set worker count to at least 32 processes; distribute workload by station-day file.
  - Choose PhaseNet pick thresholds from model defaults first; if explicit P/S thresholds are exposed by the actual inference interface, record them in the runtime summary and use the package contract values rather than guessed custom thresholds.
- Constraints:
  - Keep config/input preparation, model initialization strategy, multiprocessing execution, output writing, and validation in the same script.
  - Use a multiprocessing start method compatible with NPU safety; do not fork an already initialized NPU context.
  - Model loading must happen inside worker initialization or a spawn-safe setup stage, not in the parent before process creation.
  - Maintain all pick times as `UTCDateTime`-style ISO strings.
  - Do not treat empty day-level output as success unless the script also records that all input files were processed and explicitly reports zero picks.
- Key outputs:
  - `picks_20190704.csv`
  - `picks_20190705.csv`
  - Daily processing summary table/JSON with counts of total files, successful files, failed files, total P picks, total S picks

#### Task 1.1 — Input discovery and metadata validation
- Task description:
  - Read `station.sta`, parse the comma-separated rows, build a station lookup keyed by the first field (`network.station`), and inventory all waveform files in the 22 daily folders.
- Required data sources:
  - `station.sta`
  - Day folders under `phase_picking/20190704` and `phase_picking/20190705`
- Parameter selection strategy:
  - Validate that each MiniSEED filename station prefix exists in `station.sta`.
  - Record stations present in waveforms but absent in metadata as skipped or warning cases.
- Constraints:
  - Assume no header row in `station.sta`.
  - Preserve original station IDs exactly as used in filenames for CSV output.
- Key outputs:
  - In-memory station lookup
  - File manifest for both days
  - Validation log of usable vs skipped files

#### Task 1.2 — Waveform read and preprocessing standardization
- Task description:
  - For each station-day file, read the MiniSEED stream, sort traces, merge if needed, verify three-component availability, harmonize sampling and timing, and prepare a continuous input stream suitable for PhaseNet.
- Required data sources:
  - Daily MiniSEED files
- Parameter selection strategy:
  - Confirm channels correspond to one three-component station-day waveform.
  - Use ObsPy to:
    - read stream
    - sort traces by starttime/channel
    - merge overlapping fragments if present
    - trim to exact day window from filename or folder date
    - check for consistent sampling rate
  - If waveform sample rate differs from PhaseNet contract sampling rate of 100 Hz, resample/interpolate to 100 Hz before inference.
  - Standardize component ordering to the order expected by the model/inference interface and document the chosen mapping.
- Constraints:
  - Do not alter absolute timing.
  - Preserve a copy/reference of raw trace data for amplitude extraction at pick times.
  - Skip files missing sufficient components for PhaseNet input, but log them explicitly.
- Key outputs:
  - Per-file validated three-component stream for inference
  - Per-file raw waveform reference for amplitude sampling
  - QC counters for missing components, sampling mismatches, and read failures

#### Task 1.3 — PhaseNet inference with multiprocessing and NPU-safe execution
- Task description:
  - Run PhaseNet inference over all valid station-day files using at least 32 processes, with progress reporting and NPU-safe worker startup.
- Required data sources:
  - Preprocessed station-day streams from Task 1.2
  - PhaseNet model assets
- Parameter selection strategy:
  - Use the retrieved PhaseNet architecture path and verified original pretrained weights path.
  - Instantiate one model per worker after worker start.
  - Use overlap based on retrieved PhaseNet default (`overlap=1500`) unless the verified local inference interface requires a different contract value.
  - Use model default detection threshold (`0.3`) unless the local inference wrapper exposes separate P/S thresholds and documents their use.
  - Use chunking/windowing exactly as required by the actual local PhaseNet inference interface; if window length is configurable, choose the package default rather than inventing a custom value.
  - Report progress by day and by file, including worker completion counts.
- Constraints:
  - Avoid any design that initializes NPU before multiprocessing worker creation.
  - Do not treat probability annotations alone as final output; convert them to discrete P and S picks.
  - Collect failure evidence per file: exception type, station ID, day, and processing stage.
- Key outputs:
  - Per-file discrete pick list with phase time, score, and phase type
  - Runtime logs showing progress and failures
  - Aggregate day-level pick collections

#### Task 1.4 — Pick-time amplitude extraction and CSV assembly
- Task description:
  - For each discrete pick, compute phase amplitude from the raw waveform at the pick time and assemble requested CSV rows.
- Required data sources:
  - Raw waveform references from Task 1.2
  - Pick outputs from Task 1.3
- Parameter selection strategy:
  - For each pick, convert the pick sample/time to `UTCDateTime` string.
  - Extract amplitude from the raw waveform nearest the pick time on a consistent component rule:
    - P picks: use vertical component if available
    - S picks: use the larger absolute amplitude among horizontal components if both are available
  - If only one valid component exists for amplitude extraction after inference, use that component and flag the rule in the summary.
  - Store:
    - `station_id`
    - `phase_time`
    - `phase_score`
    - `phase_amplitude`
    - `phase_type`
  - Sort rows first by `phase_time`, then `station_id`, then `phase_type`.
- Constraints:
  - CSV must include the exact header row requested.
  - Time strings must remain UTC ISO 8601, not epoch values.
  - Amplitude values should come from waveform data, not model probabilities or normalized inference tensors.
- Key outputs:
  - `picks_20190704.csv`
  - `picks_20190705.csv`

#### Task 1.5 — Immediate output validation
- Task description:
  - Verify the day-level CSV outputs are scientifically usable and structurally correct.
- Required data sources:
  - Daily CSV outputs
  - Processing logs
- Parameter selection strategy:
  - Check:
    - file exists
    - header matches exactly
    - all `phase_type` values are only `P` or `S`
    - all `phase_time` values parse as ObsPy `UTCDateTime`
    - all `station_id` values exist in `station.sta`
    - row count is non-zero when picks are expected from processed data
  - Produce a compact summary of pick counts by day, station, and phase type.
- Constraints:
  - Batch completion is not sufficient; merged day-level CSV must be valid and non-empty when expected.
- Key outputs:
  - Validation summary table/JSON
  - Failure/empty-output evidence if any day does not yield valid picks

### Task 2 — Produce one illustrative picking-process figure
- Task description:
  - Generate one figure for a representative station-day example showing waveform and PhaseNet-derived picks to document the picking process.
- Required data sources:
  - One successfully processed station-day waveform
  - Corresponding PhaseNet annotations or discrete picks
- Parameter selection strategy:
  - Choose one case with clear P and S picks and good waveform quality from the processed days.
  - Display:
    - three-component waveform over a limited time window around the selected event/picks
    - pick markers for P and S arrivals
    - optionally the corresponding PhaseNet probability traces if available from the inference interface
  - Select the time window centered on the strongest or clearest picked event from the chosen station-day file.
- Constraints:
  - Only one case is required.
  - Use actual workflow outputs, not schematic/mock results.
- Key outputs:
  - One picking-process figure file
  - Short machine-readable metadata record identifying chosen day, station, and plotted time window