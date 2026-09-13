# Goal
Preprocess continuous Ridgecrest seismic waveform data for 2019-07-04 to 2019-07-26 into station metadata and standardized daily 3-component waveform products suitable for later deep-learning phase picking and Wood-Anderson-based magnitude estimation.

## Planning Assumptions
- Use only the provided observation data sources: continuous MiniSEED in `<DATA_ROOT>/Science2019_Ross_Ridgecrest/data/waveforms_raw` and StationXML in `<DATA_ROOT>/Science2019_Ross_Ridgecrest/data/stationxml/`.
- Date range must be hard-coded in the script with `obspy.UTCDateTime("2019-07-04T00:00:00")` to `obspy.UTCDateTime("2019-07-26T00:00:00")`, processed as 22 full UTC daily windows: 2019-07-04 through 2019-07-25.
- All time handling should use `obspy.UTCDateTime`.
- Observation preprocessing should prioritize HH* channels; if HH* is unavailable for a station-day, fall back to EH* only when three components can be formed consistently.
- `station.sta` is a derived output to be generated from StationXML, not assumed to exist.
- For phase-picking products, do not remove instrument response and do not amplitude-normalize.
- For magnitude-estimation products, remove instrument response and simulate Wood-Anderson response before saving.
- One primary task script is sufficient because metadata extraction, waveform selection, preprocessing, product writing, QC statistics, and example plotting are tightly coupled.
- Parallel execution should be implemented across station-day units, capped at 64 workers, with merged validation after batch completion.
- Success evidence must include: non-empty `station.sta`, non-empty processed daily MiniSEED outputs for expected station-days where data exist, a processing summary table, and one preprocessing example figure.

## Analysis Plan

### Task 1: Build station metadata table and channel/gain inventory
- Task description
  - Parse all StationXML files, extract station coordinates/elevation, inspect available high-gain 3-component channels, and compute one representative gain per station as the mean sensitivity of the three selected HH* or EH* channels.
- Required data sources
  - `<DATA_ROOT>/Science2019_Ross_Ridgecrest/data/stationxml/`
- Parameter selection strategy
  - For each `{network}.{station}.xml`, identify candidate channel triplets with common location code and component set Z/N/E or Z/1/2.
  - Prefer HH* triplets over EH* triplets.
  - Use channel instrument sensitivity from StationXML; if multiple valid triplets exist, choose the triplet most consistent in sample rate and availability across components.
  - Elevation written in meters from station metadata.
- Constraints
  - Output file name must be `station.sta`.
  - Output columns must be exactly `network.station,latitude,longitude,elevation,gain`.
  - Gain must be the arithmetic mean of the three selected component gains, with channel family used recorded in a QC sidecar table.
  - If no valid 3-component HH*/EH* set exists, keep station out of `station.sta` or flag it in QC output rather than inventing values.
- Key outputs
  - `station.sta`
  - Station/channel selection QC table containing station, chosen location code, channel family, component mapping, sample rate, per-component gain, mean gain, and failure reason if excluded.

### Task 2: Enumerate station-day waveform availability and define processing units
- Task description
  - Create the list of station-day jobs for the 22 full UTC daily windows, map waveform files to station/channel/day windows, and verify compatibility with StationXML metadata before waveform preprocessing.
- Required data sources
  - `<DATA_ROOT>/Science2019_Ross_Ridgecrest/data/waveforms_raw`
  - `<DATA_ROOT>/Science2019_Ross_Ridgecrest/data/stationxml/`
  - `station.sta` from Task 1
- Parameter selection strategy
  - Explicit days: 2019-07-04T00:00:00Z to 2019-07-05T00:00:00Z, and 2019-07-05T00:00:00Z to 2019-07-26T00:00:00Z.
  - Build one job per `station × day × product_type`, where product types are `phase_picking` and `magnitude`.
  - Select only channels belonging to the chosen station metadata triplet from Task 1.
  - Include files whose encoded time spans overlap the target UTC day.
- Constraints
  - Process only these 22 daily windows; no spillover beyond day boundaries in saved products.
  - If files are segmented, all overlapping files for the selected component/day must be included before merging.
  - Require consistent network, station, location, sample rate, and channel family within a station-day unit.
- Key outputs
  - Job manifest table listing station, day start/end, selected files per component, selected metadata file, chosen channel set, and availability status.

### Task 3: Generate daily 3-component preprocessing products for later phase picking
- Task description
  - For each valid station-day, load overlapping raw waveform segments, merge and gap-check traces, apply a phase-picking-oriented preprocessing pipeline, assemble a daily 3-component stream, and save one MiniSEED file per station-day.
- Required data sources
  - Waveform files from Task 2
  - Corresponding StationXML metadata
- Parameter selection strategy
  - Load each component for the full UTC day with padding only if needed for filtering edge handling; trim final saved product exactly to the day.
  - Merge segmented traces by component after sorting by time; preserve gap/overlap statistics.
  - Use detrend and de-mean; taper before filtering.
  - Apply a bandpass suitable for local earthquake phase picking, selected according to actual sample rate and channel family; a practical default is a local-event passband constrained below Nyquist and common to all three components.
  - Resample/interpolate only if required to enforce common sampling across the 3 components; prefer retaining native common rate when already consistent.
  - Fill short gaps only if methodologically acceptable for downstream picking; otherwise mark incomplete data and save only if coverage passes threshold.
  - Assemble ordered 3-component stream using component mapping Z/N/E, or Z/1/2 with mapping recorded.
- Constraints
  - No response removal.
  - No trace-wise normalization or whitening that would distort amplitudes needed by downstream models.
  - Save one 3-component MiniSEED per station-day with file name `YYYYMMDD/{network}.{station}.{starttime}.{endtime}.mseed`, where `starttime` and `endtime` are exact UTC day bounds.
  - Must validate that output stream has exactly three aligned components and non-zero samples.
  - Completeness metrics must be computed before and after merge: coverage fraction, total gap duration, number of gaps, number of overlaps, final duration, and sample-rate consistency.
- Key outputs
  - Daily processed 3-component MiniSEED files for phase picking
  - Per-station-day QC CSV with completeness and preprocessing statistics

### Task 4: Generate daily 3-component preprocessing products for later magnitude estimation
- Task description
  - Starting from the same station-day waveform selection, preprocess traces for amplitude-based magnitude work by removing response to physical units and simulating Wood-Anderson response before saving 3-component daily streams.
- Required data sources
  - Waveform files from Task 2
  - StationXML metadata with response information
- Parameter selection strategy
  - Use the same station-day/component selection and merge logic as Task 3 to keep products comparable.
  - Pre-response-removal conditioning: de-mean, detrend, taper, and optional pre-filter chosen from metadata/sample rate to stabilize deconvolution.
  - Remove instrument response using StationXML; choose output units consistent with local magnitude workflow before Wood-Anderson simulation.
  - Simulate Wood-Anderson response using standard poles/zeros as implemented by the selected processing library.
  - Apply any post-simulation band limitation only if needed to suppress numerical artifacts, keeping amplitude fidelity.
- Constraints
  - Response removal must use valid metadata match for network, station, location, channel, and time.
  - If response is missing/invalid for any component, station-day magnitude product should be skipped or flagged, not silently substituted.
  - Save one 3-component MiniSEED per station-day in a separate magnitude-product namespace using the same filename pattern.
  - Final QC must record response-removal success, Wood-Anderson simulation success, units, and any failed station-days.
- Key outputs
  - Daily processed 3-component MiniSEED files for magnitude estimation
  - Per-station-day magnitude QC CSV including response/WA processing status and amplitude statistics

### Task 5: Parallel execution, progress reporting, and merged validation
- Task description
  - Execute station-day preprocessing in parallel, monitor progress, and validate merged scientific outputs after all workers finish.
- Required data sources
  - Job manifest from Task 2
  - Outputs from Tasks 3 and 4
- Parameter selection strategy
  - Parallelize over station-day units with a maximum of 64 workers; actual worker count should be `min(64, number_of_jobs, available_cores)`.
  - Use chunking sized to avoid repeated StationXML parsing overhead; reuse station metadata in worker initialization if practical.
  - Emit progress logs for submitted, running, completed, skipped, and failed jobs.
- Constraints
  - Batch completion alone is not success; final merged validation must confirm expected output files exist and are readable.
  - Collect failure evidence per job: missing files, metadata mismatch, response failure, incomplete components, empty output, or readback failure.
  - No temporary/intermediate waveform files should be written.
- Key outputs
  - Processing summary CSV/JSON with counts of total jobs, successful outputs by product type, skipped jobs, failed jobs, and failure reasons
  - Readback validation table confirming each saved MiniSEED contains three aligned traces for the exact UTC day span

### Task 6: Create one representative preprocessing figure and usage comments
- Task description
  - Produce one figure demonstrating the preprocessing workflow on a representative station-day and add concise usage comments describing how the two processed products should be used later.
- Required data sources
  - One raw station-day waveform set
  - Corresponding processed phase-picking and/or magnitude-estimation output
- Parameter selection strategy
  - Choose a station-day with complete 3-component data and successful outputs in both product branches.
  - Plot a before/after sequence that clearly shows raw segmented input, merged daily trace, filtered phase-picking product, and Wood-Anderson product for at least one component, with optional 3-component panel.
- Constraints
  - One case is sufficient.
  - Figure should emphasize preprocessing stages and data-quality effects, not interpretation.
  - Usage comments should be embedded near outputs or in a compact sidecar text/CSV field, not as a separate narrative report.
- Key outputs
  - One preprocessing example figure
  - Compact usage notes covering:
    - phase-picking product: daily 3C waveform, no response removed, no normalization, suitable for later DL picker windowing/inference
    - magnitude product: daily 3C waveform after response removal and Wood-Anderson simulation, suitable for later local-magnitude amplitude measurement

### Task 7: Final output inventory and acceptance checks
- Task description
  - Confirm all requested deliverables are present, correctly named, and scientifically usable.
- Required data sources
  - Outputs from Tasks 1–6
- Parameter selection strategy
  - Verify file naming against exact daily UTC bounds.
  - Cross-check number of output station-days against manifest and QC summaries.
  - Randomly read a subset and one full example from each product type.
- Constraints
  - Required deliverables are:
    - `station.sta`
    - processed daily 3C MiniSEED files for phase picking
    - processed daily 3C MiniSEED files for magnitude estimation
    - one preprocessing figure
    - QC/summary tables
  - Any missing category should be treated as incomplete execution.
- Key outputs
  - Final deliverable inventory table
  - Acceptance checklist with pass/fail for metadata generation, day-range restriction, 3-component assembly, response/WA processing, progress logging, and parallel execution