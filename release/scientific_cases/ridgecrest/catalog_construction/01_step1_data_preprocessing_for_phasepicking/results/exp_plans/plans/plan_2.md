# Goal
Preprocess continuous Ridgecrest seismic waveform data for 2019-07-04 to 2019-07-26 into station-day three-component products suitable for later deep learning phase picking and magnitude estimation, while also generating a station metadata table `station.sta` and one preprocessing diagnostic figure.

## Planning Assumptions
- Observation data are available and sufficient, so only the provided waveform MiniSEED and StationXML metadata should be used.
- The used data window must be explicitly fixed in the script as:
  - start time: `UTCDateTime("2019-07-04T00:00:00")`
  - end time: `UTCDateTime("2019-07-26T00:00:00")`
  - process full UTC days: 2019-07-04 through 2019-07-25.
- Waveform organization contract:
  - input waveform root: `<DATA_ROOT>/Science2019_Ross_Ridgecrest/data/waveforms_raw`
  - input StationXML root: `<DATA_ROOT>/Science2019_Ross_Ridgecrest/data/stationxml/`
  - waveform files are station-scoped and day-bounded by filename.
- ObsPy should be the primary processing package because the workflow requires MiniSEED reading, StationXML parsing, `UTCDateTime`, merging, trimming, filtering, instrument response handling, and Wood-Anderson simulation.
- `station.sta` is a derived output and should be created from StationXML, not assumed to already exist.
- Gain in `station.sta` should be computed from the three target channels of one 3-C set, preferring `HH*` if available, otherwise `EH*`; if more than one valid epoch exists, use the epoch active during the processed date range, and average the three channel sensitivities only after confirming matching component set and units.
- “No temporary/intermediate files” applies to waveform products; in-memory processing is preferred, with only final station table, final processed MiniSEED files, and one diagnostic figure written.
- Parallelization should be implemented at the station-day level, with a hard upper bound of 64 workers and logging/progress reporting for submitted/completed jobs.
- For later phase picking, do not remove response and do not apply per-trace amplitude normalization that would distort relative amplitudes.
- For later magnitude estimation, remove instrument response and simulate Wood-Anderson response; this product should be saved separately from the phase-picking product to avoid mixed processing assumptions.

## Analysis Plan

### Task 1: Build station inventory summary and create `station.sta`
- Task description
  - Parse all StationXML files, extract station coordinates/elevation, identify the preferred 3-component high-gain set, compute average gain across the three channels, and write `station.sta`.
- Required data sources
  - `<DATA_ROOT>/Science2019_Ross_Ridgecrest/data/stationxml/`
- Parameter selection strategy
  - Enumerate all `{network}.{station}.xml` files.
  - For each station, inspect channels active during 2019-07-04 to 2019-07-26.
  - Prefer a complete `HHZ/HHN/HHE` or `HHZ/HH1/HH2` set; if unavailable, use `EHZ/EHN/EHE` or `EHZ/EH1/EH2`.
  - Use station latitude, longitude, and elevation from the station metadata level; if only channel elevation is available, verify consistency and use the common value.
  - Compute channel gain from instrument sensitivity in StationXML for the selected three components, then average the three values.
- Constraints
  - Use only channels valid in the target date range.
  - Do not average gains across mixed band codes (`HH` with `EH`) unless no consistent 3-C set exists and this fallback is explicitly logged.
  - If horizontal channels are `1/2` rather than `N/E`, preserve the station as usable and document component mapping separately in the processing summary.
- Key outputs
  - `station.sta` with rows:
    - `network.station,latitude,longitude,elevation,gain`
  - Optional machine-readable station inventory summary table including chosen channels and sample rates for downstream preprocessing consistency checks.

### Task 2: Preprocess continuous waveforms into station-day 3-C products
- Task description
  - For every station and each full UTC day in the fixed date range, load all matching waveform files, assess completeness, merge segmented traces, standardize timing and metadata, and export final 3-C station-day streams for later use.
- Required data sources
  - `<DATA_ROOT>/Science2019_Ross_Ridgecrest/data/waveforms_raw`
  - `<DATA_ROOT>/Science2019_Ross_Ridgecrest/data/stationxml/`
  - `station.sta` from Task 1
- Parameter selection strategy
  - Build explicit day windows:
    - `2019-07-04T00:00:00` to `2019-07-05T00:00:00`
    - `2019-07-05T00:00:00` to `2019-07-26T00:00:00`
  - For each station-day:
    - locate waveform files intersecting the day window
    - prefer the same component family selected in Task 1 (`HH*` first, else `EH*`)
    - read all component traces for the day
    - sort by network, station, location, channel, start time
    - merge segmented traces per component
    - trim/pad exactly to the full UTC-day window
    - require three components with common sampling rate after preprocessing; if multiple locations exist, choose the location code with the most complete 3-C coverage
- Constraints
  - Completeness check must be explicit:
    - compute expected number of samples for each component from day length and sample rate
    - report data availability fraction before and after merge
    - reject or flag station-days with major gaps or missing components
  - If gaps are small, allow merge with gap filling only if the downstream use remains valid; otherwise leave masked/zero-filled segments and record the gap statistics in a summary table.
  - Component naming should be standardized for downstream 3-C usage:
    - preserve true channel codes in MiniSEED headers
    - store streams in consistent Z/N/E or Z/1/2 order in the output stream object before writing
  - All times must use `obspy.UTCDateTime`.
  - Parallelize this task over station-days, maximum 64 cores.
  - Show progress by station-day completion count and failure/skipped counts.
- Key outputs
  - A station-day completeness/statistics table including:
    - station, day, selected location, selected channels, sample rate, pre-merge segment count, data availability fraction, number/duration of gaps, final 3-C status
  - Final station-day 3-C streams passed to Task 3a and Task 3b processing branches.

### Task 3a: Produce phase-picking waveform products
- Task description
  - Apply a lightweight, phase-picking-oriented preprocessing workflow to each valid station-day 3-C stream and save one MiniSEED file per station-day.
- Required data sources
  - Station-day 3-C streams from Task 2
  - StationXML metadata for validation only
- Parameter selection strategy
  - Pipeline per component:
    - remove mean and linear trend
    - taper trace ends
    - apply a bandpass or high-pass filter appropriate for local-event P/S arrival picking, selecting corner frequencies from the actual channel/sample-rate characteristics; default choice should remain conservative and below Nyquist
    - optionally resample only if necessary to unify three components within a station-day; otherwise retain native sample rate
    - ensure exact common start/end times across all three components
  - Keep raw counts/amplitude scale except for basic detrend/filtering; do not perform instrument correction or trace-wise normalization.
- Constraints
  - No response removal.
  - No amplitude normalization designed for ML input standardization if the product is intended for general later use.
  - Output naming must follow:
    - `YYYYMMDD/{network}.{station}.{starttime}.{endtime}.mseed`
  - Use exact day start/end times in the filename.
  - No temporary waveform files.
- Key outputs
  - One phase-picking MiniSEED per valid station-day:
    - `YYYYMMDD/{network}.{station}.{starttime}.{endtime}.mseed`
  - A compact processing log with filter settings and any resampling applied.

### Task 3b: Produce magnitude-estimation waveform products with Wood-Anderson simulation
- Task description
  - Apply response-aware preprocessing to the same valid station-day 3-C streams, remove instrument response, simulate Wood-Anderson response, and save one MiniSEED file per station-day in a separate product line.
- Required data sources
  - Station-day 3-C streams from Task 2
  - StationXML metadata from `<DATA_ROOT>/Science2019_Ross_Ridgecrest/data/stationxml/`
- Parameter selection strategy
  - Pipeline per component:
    - remove mean and trend
    - taper
    - apply a pre-filter selected from the channel/sample-rate bandwidth to stabilize response removal
    - remove instrument response to physical ground motion units required by the Wood-Anderson simulation workflow
    - simulate Wood-Anderson instrument response
    - trim again to the exact UTC day bounds if convolution/deconvolution introduces edge effects
    - preserve common 3-C timing and sample rate across the stream
  - Prefer horizontal components to remain clearly identifiable because local magnitude often relies on horizontal amplitudes; still store the full 3-C stream for later flexibility.
- Constraints
  - Response removal requires valid matching inventory and response stages for the exact channel/epoch.
  - If response metadata are missing or invalid for any component, mark the station-day magnitude product as failed or partial; do not silently substitute the phase-picking product.
  - Output should be saved separately from phase-picking products to prevent confusion between counts-domain and Wood-Anderson-domain waveforms.
  - No temporary waveform files.
- Key outputs
  - One magnitude-estimation MiniSEED per valid station-day in a separate output product namespace, using the same filename convention:
    - `YYYYMMDD/{network}.{station}.{starttime}.{endtime}.mseed`
  - A response-processing summary table with units, pre-filter used, and success/failure reason.

### Task 4: Generate one preprocessing diagnostic figure
- Task description
  - Create one representative figure showing the preprocessing workflow from raw continuous data to final processed 3-C outputs.
- Required data sources
  - One representative station-day from Task 2–3 results
  - Raw station-day waveform subset and corresponding processed products
- Parameter selection strategy
  - Choose a station-day with:
    - complete 3-C coverage
    - minimal gaps
    - successful response removal and Wood-Anderson simulation
  - Plot a time-aligned comparison for one or more components showing:
    - raw merged trace
    - phase-picking preprocessed trace
    - magnitude-estimation/Wood-Anderson trace
  - Annotate the panel or caption metadata with station code, UTC day, selected channels, sample rate, and key completeness statistics.
- Constraints
  - One example is sufficient.
  - The figure should emphasize preprocessing effects, not event interpretation.
- Key outputs
  - One diagnostic preprocessing figure demonstrating merge/completeness and the two final processing branches.

### Task 5: Write usage comments and validation summaries for downstream analysis
- Task description
  - Attach concise comments/metadata summaries describing how each processed product should be used in later phase picking and magnitude workflows, and validate that final outputs are scientifically usable.
- Required data sources
  - Outputs from Tasks 1–4
- Parameter selection strategy
  - For phase-picking products, record comments such as:
    - counts-domain waveforms
    - filtered/detrended/tapered only
    - no response correction
    - suitable for later 3-C deep learning phase pickers
  - For magnitude-estimation products, record comments such as:
    - response removed
    - Wood-Anderson simulated
    - intended for later local-magnitude-style amplitude measurements
  - Summarize totals:
    - number of stations discovered
    - number of station-days requested
    - number successfully exported for phase picking
    - number successfully exported for magnitude estimation
    - number skipped and reasons
- Constraints
  - Validation must inspect final written MiniSEED files, not just upstream in-memory success.
  - A station-day batch is only successful if the final 3-C output exists, is readable, non-empty, and matches the exact requested UTC day bounds.
- Key outputs
  - Final processing summary table/CSV or JSON
  - Embedded script comments or sidecar summary text describing downstream usage assumptions for the two product types