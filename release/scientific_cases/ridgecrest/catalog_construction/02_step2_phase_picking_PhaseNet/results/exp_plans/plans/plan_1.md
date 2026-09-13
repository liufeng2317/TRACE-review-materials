# Goal
Use the provided Ridgecrest continuous MiniSEED data and station metadata to run deep-learning seismic phase picking with PhaseNet over 2019-07-04 to 2019-07-26, producing one daily CSV of P/S picks per day and one representative diagnostic figure showing the picking process.

## Planning Assumptions
- Observation data are sufficient and should be used directly; no synthetic or model waveform data are needed beyond the requested pretrained PhaseNet model.
- PhaseNet package contract from retrieved materials:
  - Network architecture path: `<PROJECT_ROOT>/seismoagent/library/ai_module/phase_picking/model/phasenet.py`
  - Inference example path: `<PROJECT_ROOT>/seismoagent/library/ai_module/phase_picking/inference/phasenet.py`
  - User-requested pretrained model version is the original model; retrieved inference example explicitly references `<PROJECT_ROOT>/seismoagent/library/ai_module/phase_picking/pretrained/v3/phasenet/original.pt.v2`
  - PhaseNet default model args include `phases='NPS'`, `sampling_rate=100`, `norm='std'`, and default inference arguments include `detection_threshold=0.3`, `blinding=[0,0]`, `overlap=1500`
  - Preferred inference method is `model.classify(...)` to obtain discrete picks directly; `model.annotate(...)` is suitable for probability diagnostics and plotting
  - Output pick objects provide phase, peak time (`UTCDateTime`), and peak value (confidence/probability)
- NPU is explicitly requested. To avoid re-initializing NPU in forked subprocesses, multiprocessing must use a non-fork start method, with model initialization performed inside each worker rather than in the parent process.
- The workflow should remain within one primary task script because data discovery, validation, NPU-safe multiprocessing, inference, CSV writing, and diagnostic figure generation are tightly coupled.
- Only the 22 daily folders in the request window should be processed: `20190704` through `20190725`.
- All output times must remain ISO 8601 UTC strings derived from ObsPy `UTCDateTime`; no UNIX timestamps should be written.
- Station metadata file has no header and is comma-separated; first column is the station identifier matching waveform filename prefixes such as `CI.CCC`.

## Analysis Plan
### Task 1: Build and run one primary PhaseNet picking workflow script
- Task description:
  - Create a single end-to-end script that discovers day folders in the requested time window, validates waveform/station inputs, runs PhaseNet on each station-day waveform with NPU-safe multiprocessing, aggregates picks by day, writes daily CSV outputs, and generates one representative diagnostic figure.
- Required data sources:
  - Continuous MiniSEED base directory: `<CASE_ROOT>/catalog_construction/01_step1_data_preprocessing_for_phasepicking/exp_run/outputs/01_preprocess_ridgecrest_stationday_waveforms/phase_picking`
  - Station metadata: `<CASE_ROOT>/catalog_construction/01_step1_data_preprocessing_for_phasepicking/exp_run/outputs/01_preprocess_ridgecrest_stationday_waveforms/station.sta`
  - PhaseNet model file: `<PROJECT_ROOT>/seismoagent/library/ai_module/phase_picking/model/phasenet.py`
  - PhaseNet pretrained weights: `<PROJECT_ROOT>/seismoagent/library/ai_module/phase_picking/pretrained/v3/phasenet/original.pt.v2`

#### Task 1.1: Input discovery and validation
- Task description:
  - Enumerate the requested dates using script variables `start_time` and `end_time`, map them to day folders, and build a per-day list of station waveform files.
- Required data sources:
  - Daily folders `20190704` through `20190725`
  - `station.sta`
- Parameter selection strategy:
  - Set `start_time = UTCDateTime("2019-07-04T00:00:00Z")`
  - Set `end_time = UTCDateTime("2019-07-26T00:00:00Z")`
  - Convert the half-open interval `[start_time, end_time)` into day keys `20190704` through `20190725`
  - Parse station IDs from filenames using the first two dot-separated fields (`network.station`)
  - Parse `station.sta` into named fields at minimum: `station_id`, longitude/latitude/elevation if present
- Constraints:
  - Only include files whose day folder lies within the requested time window
  - Require exactly one 24-hour waveform file per station per day when available
  - Reject or log files whose station ID does not appear in `station.sta`
  - Preserve a manifest table per day listing file path, station ID, inferred start/end time from filename, and validation status
- Key outputs:
  - Day-level file manifest
  - Valid station-day workload list
  - Counts of valid files, skipped files, and missing metadata entries

#### Task 1.2: Waveform preprocessing checks before inference
- Task description:
  - Read each MiniSEED file and ensure it is usable by PhaseNet as a 3-component continuous stream.
- Required data sources:
  - Station-day MiniSEED files
- Parameter selection strategy:
  - Use ObsPy reading of each MiniSEED file
  - For each stream, verify start time, end time, number of traces, component labels, sampling rate consistency, and data type
  - Reorder components to a stable 3-component convention expected by the model input workflow, while preserving original metadata
  - If small gaps/overlaps or channel ordering issues exist, merge and sort traces before inference; if a complete 3-component stream cannot be formed, skip and log
- Constraints:
  - Do not alter absolute timing
  - Do not convert times to numeric timestamps in exported results
  - Do not assume channel codes beyond using the existing 3-component traces in the file
  - If sampling rate differs from PhaseNet’s pretrained expectation of 100 Hz, resample only if needed and record this in QC output
- Key outputs:
  - Clean per-file 3-component stream ready for inference
  - QC log containing component availability, sampling rate, merge/resample decisions, and skip reasons

#### Task 1.3: NPU-safe multiprocessing PhaseNet inference
- Task description:
  - Run parallel phase picking on the validated station-day files using at least 32 worker processes while preventing NPU initialization issues.
- Required data sources:
  - Clean waveform streams from Task 1.2
  - PhaseNet original pretrained model
- Parameter selection strategy:
  - Use multiprocessing with at least 32 processes; determine final worker count as `max(32, available_safe_worker_count)` if resources permit, otherwise keep exactly 32 as the requested baseline
  - Use a non-fork start method (`spawn` or equivalent safe method) to avoid re-initializing NPU in forked subprocesses
  - Initialize torch/NPU and load PhaseNet weights inside each worker once
  - Use `model.classify(...)` as the primary picking path
  - Start from retrieved default overlap `1500` and thresholds `P_threshold=0.3`, `S_threshold=0.3`
  - Keep thresholds identical for both days unless a hard execution issue requires verification
- Constraints:
  - No CPU-only execution path is needed
  - Parent process must not pre-initialize NPU before workers are spawned
  - Worker success is not sufficient by itself; daily merged pick output must be non-empty when picks exist and structurally valid even if some files fail
  - Show progress by day and by station/file, including processed count, failed count, and current file ID
- Key outputs:
  - Per-station/day in-memory or temporary pick records containing:
    - `station_id`
    - `phase_time` as `UTCDateTime` ISO 8601 string
    - `phase_score`
    - `phase_type`
    - auxiliary fields for internal QC such as source file and trace/component context

#### Task 1.4: Amplitude extraction at pick time
- Task description:
  - Add `phase_amplitude` to each pick from the raw waveform at the picked arrival time.
- Required data sources:
  - Original waveform trace data used for inference
  - Pick times from Task 1.3
- Parameter selection strategy:
  - For each pick, identify the sample nearest to `phase_time` on the chosen reference trace set
  - Use a consistent amplitude definition across all picks; preferred strategy is absolute amplitude from the vertical component for P picks and the maximum absolute amplitude across horizontal components for S picks if components are clearly identified, otherwise use the maximum absolute amplitude across all available components at the nearest sample
  - Record the exact amplitude extraction rule in the workflow metadata
- Constraints:
  - Amplitude must be taken from waveform space, not from model probability output
  - Do not change pick time during amplitude lookup
  - If no exact sample exists due to interpolation/resampling decisions, use nearest sample and log that method
- Key outputs:
  - Completed pick records with `phase_amplitude`

#### Task 1.5: Daily aggregation and CSV export
- Task description:
  - Merge all station results within each day and write one CSV per day in the requested schema.
- Required data sources:
  - Completed pick records from Tasks 1.3–1.4
- Parameter selection strategy:
  - Produce:
    - `picks_20190704.csv`
    - `picks_20190705.csv`
  - Write header exactly as:
    - `station_id,phase_time,phase_score,phase_amplitude,phase_type`
  - Sort rows by `phase_time`, then `station_id`, then `phase_type`
  - Format `phase_time` with ObsPy-compatible UTC ISO strings ending in `Z`
  - Keep numeric fields as plain decimal values
- Constraints:
  - One file per day containing all picks for that day
  - Include header row
  - Output must not contain UNIX timestamps
  - Empty or malformed merged CSVs are failures and must trigger diagnostic logging
- Key outputs:
  - `picks_20190704.csv`
  - `picks_20190705.csv`
  - Daily summary table with numbers of stations processed, picks per phase, and failures/skips

#### Task 1.6: Representative diagnostic figure for the picking process
- Task description:
  - Generate one figure showing how PhaseNet picked phases on a representative station-day example.
- Required data sources:
  - One successfully processed waveform file
  - Pick results from `model.classify(...)`
  - Optional probability traces from `model.annotate(...)` for the same example
- Parameter selection strategy:
  - Select one case with clear P and S detections and good signal visibility
  - Plot waveform traces for the 3 components over a focused time window around one or several picks
  - Mark P and S pick times with distinct annotations
  - If probabilities are included, add PhaseNet P and S probability curves in aligned subpanels
  - Prefer a case from the processed Ridgecrest days rather than a synthetic example
- Constraints:
  - Only one case is required
  - Figure should document the actual picking process, not just raw waveform
  - Pick times displayed in the figure must remain in UTC
- Key outputs:
  - One diagnostic figure demonstrating waveform and PhaseNet picks
  - Optional machine-readable metadata identifying the source station-day file and plotted time window

#### Task 1.7: Execution validation and failure evidence collection
- Task description:
  - Verify that the full workflow succeeded scientifically and technically.
- Required data sources:
  - CSV outputs
  - QC logs
  - Diagnostic figure
- Parameter selection strategy:
  - Validate that both daily CSV files exist and contain the required header
  - Check each row for:
    - valid `station_id`
    - parsable UTC `phase_time`
    - finite `phase_score`
    - finite `phase_amplitude`
    - `phase_type` in `{P, S}`
  - Compare CSV station IDs against `station.sta`
  - Confirm the diagnostic figure corresponds to a real processed file
- Constraints:
  - Successful multiprocessing alone does not count as success unless daily merged outputs are valid
  - Skipped files must be reported with reasons
  - NPU or multiprocessing failures must be preserved in logs with file-level context
- Key outputs:
  - Validation summary for both days
  - Failure/skip inventory
  - Final run manifest linking inputs, daily outputs, and the diagnostic figure