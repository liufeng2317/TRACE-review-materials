# Goal
Prepare Ridgecrest continuous seismic data for 2019-07-04 to 2019-07-26 into station metadata and standardized per-station, per-day three-component waveform products for later phase picking and magnitude estimation, with explicit UTC day handling, parallel processing, progress reporting, and one preprocessing diagnostic figure.

## Planning Assumptions
- Use only observation data provided in `waveforms_raw` and `stationxml`; no model data are needed.
- The script must define the processing window explicitly with `obspy.UTCDateTime("2019-07-04T00:00:00")` and `obspy.UTCDateTime("2019-07-26T00:00:00")`, corresponding to the 22 full UTC daily windows 2019-07-04 through 2019-07-25.
- ObsPy is the primary package. Relevant package contract: StationXML should be read with `read_inventory(..., format="STATIONXML")`; waveform traces can be merged and trimmed with `Stream.merge()` and `trim()`; response removal uses `remove_response(inventory=..., output=..., pre_filt=..., water_level=...)`; Wood-Anderson simulation can be done with `simulate(..., paz_simulate=...)` after instrument correction or by direct response-based deconvolution followed by simulation. Success evidence is non-empty day-level three-component MiniSEED outputs and a non-empty `station.sta`.
- For deep-learning phase picking, produce three-component streams with consistent component order and sampling rate; do not remove instrument response and do not apply amplitude normalization in the saved phase-picking output.
- For magnitude estimation, remove instrument response and simulate Wood-Anderson response; horizontal components are the primary magnitude-bearing channels, but save the full three-component day stream for reuse unless channel availability forces a reduced set.
- Preferred channel family per station is HH*; if unavailable for a station-day, use EH*. Do not mix HH and EH within the same saved station-day product unless only mixed availability can form a complete 3C set; record such cases in summary statistics.
- Parallel execution should be implemented within the main processing script for station-day jobs, capped at 64 workers, with merged output validation and failure logging in the same script.

## Analysis Plan

### Task 1: Build and validate station metadata table
- Task description: Parse all StationXML files, extract station coordinates/elevation and channel response information, compute a representative gain per station, and save `station.sta`.
- Required data sources:
  - `<DATA_ROOT>/Science2019_Ross_Ridgecrest/data/stationxml/`
  - `station.sta` as derived output
- Parameter selection strategy:
  - Iterate over all `{network}.{station}.xml` files.
  - For each station, extract network code, station code, latitude, longitude, and elevation in meters from station metadata.
  - Select the preferred 3-component channel family in this order: HH* then EH*.
  - For the chosen family, identify the three orthogonal channels ending in Z/N/E or Z/1/2 when N/E are unavailable; convert 1/2 to horizontal placeholders only if needed for averaging gain and later channel grouping.
  - For each selected channel, extract overall sensitivity/gain from response metadata at the channel level; compute the station gain as the arithmetic mean of the three channel gains.
- Constraints:
  - One row per station in the exact format `network.station,latitude,longitude,elevation,gain`.
  - If multiple epochs exist, use the epoch valid during 2019-07-04 to 2019-07-26.
  - If fewer than three valid HH* channels exist, fall back to EH*.
  - If response metadata are incomplete for both HH* and EH*, still keep the station with missing-gain flag in runtime logs, but only write rows whose gain was successfully computed unless the user later requests otherwise.
- Key outputs:
  - `station.sta`
  - Validation summary table: station count, stations using HH*, stations using EH*, stations with missing/incomplete response metadata

### Task 2: Preprocess continuous waveforms into station-day three-component products
- Task description: For each station and each full UTC day in 2019-07-04 to 2019-07-26, load raw MiniSEED files, assess completeness, merge segments, preprocess into two downstream products, and save one three-component MiniSEED per station-day for phase picking and one per station-day for magnitude estimation.
- Required data sources:
  - `<DATA_ROOT>/Science2019_Ross_Ridgecrest/data/waveforms_raw`
  - `<DATA_ROOT>/Science2019_Ross_Ridgecrest/data/stationxml/`
  - `station.sta` from Task 1 for station list and metadata cross-check
- Parameter selection strategy:
  - Explicitly define 22 UTC daily windows:
    - 2019-07-04T00:00:00 to 2019-07-05T00:00:00
    - 2019-07-05T00:00:00 to 2019-07-26T00:00:00
  - For each station-day, search the station directory `network.station/` for files overlapping the target day.
  - Prefer a complete HH* triplet; otherwise use EH* triplet.
  - Build component mapping to Z/N/E; if only Z/1/2 exist, preserve three-component consistency and note non-cardinal horizontal naming in logs.
  - Resample all components to a common sampling rate only if channel sample rates differ; choose the native rate if all match, otherwise use the highest common stable rate supported by all three traces for that day.
- Constraints:
  - All time handling must use `obspy.UTCDateTime`.
  - No temporary/intermediate files should be saved.
  - Output naming must follow `YYYYMMDD/{network}.{station}.{starttime}.{endtime}.mseed` using precise UTC day bounds.
  - The same main script should handle parallel loading, preprocessing, logging, and final merged output checks.
  - Use progress bars or per-station-day logs during execution.
  - Cap parallel workers at 64 and reduce worker count automatically if station-day count is smaller.
- Key outputs:
  - Per-day phase-picking MiniSEED products
  - Per-day magnitude-estimation MiniSEED products
  - Per-station-day processing statistics table with completeness and channel selection

#### Task 2.1: Station-day input discovery and completeness assessment
- Task description: Determine available files for each station-day and quantify raw data completeness before preprocessing.
- Required data sources:
  - `waveforms_raw`
  - `stationxml`
- Parameter selection strategy:
  - For each target component, load all files whose encoded time span overlaps the UTC day.
  - Merge segmented traces by component.
  - Trim merged traces exactly to the day window with gap/pad handling configured to expose missing intervals.
  - Compute completeness metrics per component and per station-day:
    - expected samples from day length and sample rate
    - actual non-gap sample count
    - number and duration of gaps/overlaps
- Constraints:
  - Completeness must be checked before final preprocessing.
  - Overlaps should be resolved by merge strategy documented in logs.
  - Station-days lacking at least three usable components after merge should be excluded from final 3C output and listed in failure summary.
- Key outputs:
  - Station-day completeness CSV/JSON summary
  - Log of excluded station-days and reasons

#### Task 2.2: Phase-picking preprocessing branch
- Task description: Produce a clean, standardized 3C stream suitable for later deep-learning phase picking without response removal or saved normalization.
- Required data sources:
  - Merged station-day raw traces
  - StationXML for metadata checks
- Parameter selection strategy:
  - Apply per-trace QC:
    - remove empty or constant traces
    - detrend (demean and linear)
    - taper short edges
    - optionally remove obvious spikes or masked segments if implemented consistently across all traces
  - Apply bandpass or highpass/lowpass filtering selected to preserve local-earthquake phase content while suppressing long-period drift and high-frequency noise.
  - Align start/end times exactly to the day window and ensure all three components have identical sample count after trim/resample.
  - Assemble final component order as ZNE in the saved stream metadata where possible.
- Constraints:
  - Do not remove instrument response.
  - Do not save amplitude-normalized traces.
  - Preserve physically meaningful relative amplitudes because later models may apply their own normalization.
  - Save exactly one three-component MiniSEED per successful station-day.
- Key outputs:
  - Phase-picking station-day MiniSEED files
  - Summary of final sampling rate and component order used per station-day

#### Task 2.3: Magnitude-estimation preprocessing branch
- Task description: Produce a response-corrected and Wood-Anderson-simulated 3C stream for later local magnitude workflows.
- Required data sources:
  - Merged station-day raw traces
  - StationXML inventory with response information
- Parameter selection strategy:
  - Start from the same merged and trimmed day traces as in Task 2.1.
  - Apply detrend and taper prior to deconvolution.
  - Select a stabilization `pre_filt` based on each station-day sampling rate and usable frequency band so that the upper corner stays below Nyquist and the lower corner avoids low-frequency amplification.
  - Remove response to displacement using StationXML inventory.
  - Simulate Wood-Anderson response using a standard Wood-Anderson PAZ definition.
  - Keep three-component output; mark horizontal channels as primary for downstream local magnitude amplitude extraction.
- Constraints:
  - Response removal requires valid metadata for the exact station/channel epoch.
  - If response removal fails for any component, the station-day magnitude product should be marked failed unless a documented rule allows dropping that station-day.
  - Water level and pre-filter choices must be logged because they affect amplitudes.
- Key outputs:
  - Magnitude-estimation station-day MiniSEED files after Wood-Anderson simulation
  - Response-processing log with selected pre-filter and any failed deconvolutions

### Task 3: Generate one diagnostic preprocessing figure
- Task description: Create one example figure demonstrating the preprocessing sequence from raw to final outputs.
- Required data sources:
  - One representative successful station-day from Task 2
  - Corresponding StationXML metadata
- Parameter selection strategy:
  - Choose a station-day with high completeness, valid 3C data, and successful response removal.
  - Show at minimum:
    - raw merged trace(s)
    - trimmed/QC trace(s)
    - phase-picking preprocessed trace(s)
    - magnitude branch after response removal and Wood-Anderson simulation
  - Prefer showing the same time window on all panels for direct comparison.
- Constraints:
  - One case is sufficient.
  - The figure should emphasize processing effects rather than event interpretation.
- Key outputs:
  - One preprocessing diagnostic figure
  - Caption metadata in a small machine-readable sidecar or log entry: station, day, selected channels, sample rate, completeness

### Task 4: Produce machine-readable processing summaries and usage comments
- Task description: Save compact summaries needed for later monitoring workflows and include comments describing how each processed product should be used.
- Required data sources:
  - Outputs from Tasks 1 to 3
- Parameter selection strategy:
  - Summarize counts of total station-days, successful phase-picking outputs, successful magnitude outputs, failed station-days, dominant failure reasons, and channel family usage.
  - Add comments in the script near each output branch describing intended downstream usage.
- Constraints:
  - Do not create a separate narrative report script.
  - Comments should explicitly distinguish the two products:
    - phase-picking product: three-component continuous waveforms, no response removal, no saved normalization, intended for deep-learning pickers
    - magnitude product: response removed and Wood-Anderson simulated, intended for local magnitude amplitude measurement on horizontal components
- Key outputs:
  - Processing summary CSV/JSON
  - Script comments documenting downstream usage rules and caveats

### Task Script Organization

#### Script 1: `build_station_table`
- Task description: Read StationXML, choose HH*/EH* triplets, compute averaged gain, and write `station.sta` plus a metadata validation summary.
- Required data sources:
  - `stationxml`
- Parameter selection strategy:
  - Single pass over all station XML files with epoch filtering for the requested dates.
- Constraints:
  - No waveform reading in this script.
- Key outputs:
  - `station.sta`
  - station metadata validation summary

#### Script 2: `preprocess_station_day_waveforms`
- Task description: Main parallel workflow for station-day discovery, completeness checks, preprocessing, output writing for both branches, progress reporting, merged-output validation, and one diagnostic figure.
- Required data sources:
  - `waveforms_raw`
  - `stationxml`
  - `station.sta`
- Parameter selection strategy:
  - Parallelize by station-day across at most 64 workers.
  - Explicitly process only the 22 daily windows requested.
- Constraints:
  - This script must include immediate output validation and failure evidence collection; successful worker execution alone is not sufficient.
- Key outputs:
  - Phase-picking MiniSEED outputs
  - Magnitude MiniSEED outputs
  - Completeness/statistics summaries
  - One preprocessing figure