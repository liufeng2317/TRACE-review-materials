# Goal
Preprocess the Ridgecrest continuous seismic observations for the explicit UTC window 2019-07-04T00:00:00 to 2019-07-26T00:00:00 into: (1) a station metadata table `station.sta`, (2) per-station, per-day three-component MiniSEED products for later phase picking, (3) separate per-station, per-day three-component MiniSEED products for later magnitude estimation with response removal and Wood-Anderson simulation, plus (4) one preprocessing diagnostic figure and compact QC summaries.

## Planning Assumptions
- Use only the provided observation data:
  - waveform root: `<DATA_ROOT>/Science2019_Ross_Ridgecrest/data/waveforms_raw`
  - StationXML root: `<DATA_ROOT>/Science2019_Ross_Ridgecrest/data/stationxml/`
- The script must explicitly define:
  - `start_time = obspy.UTCDateTime("2019-07-04T00:00:00")`
  - `end_time = obspy.UTCDateTime("2019-07-26T00:00:00")`
  and process exactly 22 full UTC daily windows: 2019-07-04 through 2019-07-25.
- ObsPy is the primary package contract for this workflow:
  - StationXML parsing via `read_inventory(..., format="STATIONXML")`
  - waveform reading via `read()`
  - segmented trace merging via `Stream.merge()`
  - exact day trimming via `trim()`
  - response correction via `Trace.remove_response(...)`
  - Wood-Anderson simulation via `Trace.simulate(...)` after response handling
  - all time variables must use `obspy.UTCDateTime`
- For phase-picking products:
  - save three-component daily waveforms without response removal
  - do not apply amplitude normalization/whitening intended for ML input scaling
- For magnitude-estimation products:
  - remove instrument response using StationXML valid for the exact channel epoch
  - simulate Wood-Anderson response
  - save separately from the phase-picking products
- Preferred channel family is `HH*`; if no valid 3-C set exists for the target date/day, fall back to `EH*`.
- A valid 3-C set may be `Z/N/E` or `Z/1/2`; preserve original channel codes and record component mapping in QC outputs.
- Gain in `station.sta` must be the arithmetic mean of the three selected channel sensitivities from the chosen `HH*` or `EH*` triplet.
- Parallelization should be done over station-day jobs, capped at 64 workers, with progress display and final readback validation of saved outputs.
- No temporary/intermediate waveform files should be written; only final deliverables and compact QC summaries should be saved.
- Success evidence is:
  - non-empty `station.sta`
  - non-empty daily 3-C MiniSEED outputs for successful station-days
  - readable final outputs matching exact UTC day bounds
  - one diagnostic preprocessing figure
  - compact QC/summary tables

## Analysis Plan

### Task 1: Build station metadata table `station.sta`
- Task description:
  - Parse all StationXML files, identify the preferred 3-C high-gain channel set per station, extract station coordinates/elevation, compute representative gain, and write `station.sta`.
- Required data sources:
  - `<DATA_ROOT>/Science2019_Ross_Ridgecrest/data/stationxml/`
- Parameter selection strategy:
  - Enumerate all `{network}.{station}.xml` files.
  - For each station, use metadata epochs valid during 2019-07-04 to 2019-07-26.
  - Prefer a complete `HHZ/HHN/HHE` or `HHZ/HH1/HH2` triplet; if unavailable, use `EHZ/EHN/EHE` or `EHZ/EH1/EH2`.
  - Prefer a single common location code and a consistent sample rate across the three components.
  - Extract latitude, longitude, and elevation in meters from valid station metadata.
  - Extract channel sensitivity/gain from the three selected channels and compute the arithmetic mean.
- Constraints:
  - Output rows must follow exactly: `network.station,latitude,longitude,elevation,gain`
  - Do not average gains across mixed band codes unless no consistent triplet exists and that fallback is explicitly logged.
  - If no valid 3-C HH*/EH* set with usable sensitivity exists, exclude from `station.sta` and record the reason in QC output.
- Key outputs:
  - `station.sta`
  - Station QC table with station, chosen location code, chosen channel family, component mapping, sample rate, per-component gain, mean gain, and exclusion reason if any

### Task 2: Define station-day processing units and assess raw completeness
- Task description:
  - For each station and each full UTC day, discover overlapping MiniSEED files, select the target 3-C set, merge segmented traces, and compute completeness/gap statistics before final preprocessing.
- Required data sources:
  - `<DATA_ROOT>/Science2019_Ross_Ridgecrest/data/waveforms_raw`
  - `<DATA_ROOT>/Science2019_Ross_Ridgecrest/data/stationxml/`
  - `station.sta` from Task 1
- Parameter selection strategy:
  - Explicit day windows:
    - 2019-07-04T00:00:00 to 2019-07-05T00:00:00
    - 2019-07-05T00:00:00 to 2019-07-26T00:00:00
  - For each station-day, search within `network.station/` for files whose filename time span overlaps the day.
  - Use the station’s preferred family from Task 1 when possible; if the preferred family is unavailable for a given day, allow fallback to the alternate valid `HH*`/`EH*` 3-C set and log the change.
  - Read all overlapping files per component, sort by time, merge segments per component, and trim exactly to the UTC day.
  - Compute per-component and per-station-day completeness:
    - expected sample count
    - actual non-gap sample count
    - coverage fraction
    - number of gaps and overlaps
    - total gap duration
    - final sample-rate consistency
- Constraints:
  - All time handling must use `obspy.UTCDateTime`.
  - Completeness must be computed before saving any final product.
  - Preserve true channel codes in metadata; standardize in-memory component order as `Z/N/E` or `Z/1/2`.
  - Station-days without three usable aligned components must be skipped and logged.
- Key outputs:
  - Station-day job/QC manifest
  - Completeness summary table with station, day, selected location, selected channels, sample rate, segment counts, coverage, gap/overlap metrics, and usable 3-C status

### Task 3: Produce phase-picking daily 3-C waveform products
- Task description:
  - Apply a phase-picking-oriented preprocessing pipeline to each valid station-day 3-C stream and save one final MiniSEED per station-day.
- Required data sources:
  - Valid merged station-day streams from Task 2
  - StationXML for metadata validation
- Parameter selection strategy:
  - Per component:
    - remove mean and linear trend
    - taper ends before filtering
    - apply a conservative local-event filter appropriate for later P/S picking, with passband chosen from the actual sample rate and kept below Nyquist
    - resample only if necessary to enforce a common rate across the 3 components; otherwise retain the common native rate
  - After preprocessing, enforce exact common start/end times and equal sample counts for all three components.
  - Save one 3-C stream per successful station-day using:
    - `YYYYMMDD/{network}.{station}.{starttime}.{endtime}.mseed`
- Constraints:
  - Do not remove instrument response.
  - Do not apply amplitude normalization, whitening, or other scaling designed for model inference.
  - Saved output must be exactly three readable traces spanning the exact UTC day bounds.
  - No temporary/intermediate waveform files.
- Key outputs:
  - Phase-picking daily MiniSEED products
  - Per-station-day phase-processing log with selected filter settings, final sample rate, component order, and any resampling performed

### Task 4: Produce magnitude-estimation daily 3-C waveform products
- Task description:
  - Starting from the same valid station-day streams, generate a separate magnitude-oriented product by removing instrument response and simulating Wood-Anderson response before saving one 3-C MiniSEED per station-day.
- Required data sources:
  - Valid merged station-day streams from Task 2
  - `<DATA_ROOT>/Science2019_Ross_Ridgecrest/data/stationxml/`
- Parameter selection strategy:
  - Per component:
    - remove mean and linear trend
    - taper
    - choose a `pre_filt` based on the component sample rate and stable usable frequency band, ensuring the upper corner remains below Nyquist
    - remove instrument response using the exact matching inventory/channel epoch
    - simulate standard Wood-Anderson response
    - retrim to the exact UTC day if edge effects appear
  - Preserve the full 3-C stream; keep horizontal channels clearly identifiable for later local-magnitude amplitude extraction.
  - Save one 3-C stream per successful station-day using the same filename convention:
    - `YYYYMMDD/{network}.{station}.{starttime}.{endtime}.mseed`
- Constraints:
  - Response removal must not proceed with missing or invalid response metadata.
  - If any component fails response removal or Wood-Anderson simulation, the magnitude product for that station-day should be skipped and logged as failed.
  - Do not silently substitute the phase-picking product.
  - Save in a separate magnitude-product output namespace from the phase-picking products.
- Key outputs:
  - Magnitude-estimation daily MiniSEED products
  - Response/WA QC table with station, day, channels, units, `pre_filt`, response-removal status, WA-simulation status, and failure reason if any

### Task 5: Parallel execution, progress reporting, and output validation
- Task description:
  - Run station-day preprocessing in parallel, provide progress information during execution, and validate final written products after all workers complete.
- Required data sources:
  - Outputs from Tasks 1–4
- Parameter selection strategy:
  - Parallelize over station-day jobs with worker count:
    - `min(64, number_of_jobs, available_cores)`
  - Reuse parsed station metadata per worker when practical to reduce repeated StationXML loading overhead.
  - Report progress for submitted, completed, skipped, and failed jobs.
  - After writing outputs, read back each saved MiniSEED to confirm:
    - file exists and is non-empty
    - exactly three traces are present
    - traces are readable
    - day bounds match the exact requested UTC interval
    - sample counts and timing are aligned across components
- Constraints:
  - Worker completion alone is not success; final scientific output validation is required.
  - Failure evidence must be collected for:
    - missing files
    - metadata mismatch
    - incomplete 3-C set
    - merge failure
    - empty output
    - response-removal failure
    - Wood-Anderson failure
    - readback failure
- Key outputs:
  - Processing summary CSV/JSON with totals by product type, successes, skips, failures, and failure reasons
  - Readback validation table for all final products

### Task 6: Generate one preprocessing diagnostic figure
- Task description:
  - Produce one representative figure showing the preprocessing path from raw merged data to the final phase-picking and magnitude-estimation products.
- Required data sources:
  - One successful station-day from Tasks 3 and 4
  - Corresponding raw merged station-day traces
- Parameter selection strategy:
  - Choose a station-day with:
    - high completeness
    - valid 3-C data
    - successful response removal and Wood-Anderson simulation
  - Show a time-aligned comparison including at least:
    - raw merged trace(s)
    - trimmed/QC trace(s)
    - final phase-picking product
    - final Wood-Anderson magnitude product
  - Record station, day, channels, sample rate, and completeness in a compact sidecar/log entry.
- Constraints:
  - One case is sufficient.
  - The figure should demonstrate preprocessing effects, not seismic interpretation.
- Key outputs:
  - One preprocessing diagnostic figure
  - Compact figure metadata entry

### Task 7: Add downstream usage comments in the script and finalize deliverables
- Task description:
  - Include concise in-script comments describing how each processed product should be used later, and confirm all requested deliverables are present.
- Required data sources:
  - Outputs from Tasks 1–6
- Parameter selection strategy:
  - Add comments near the phase-picking branch stating:
    - continuous 3-C daily waveform product
    - detrended/tapered/filtered only
    - no response removal
    - no normalization
    - intended for later deep-learning phase-picking workflows
  - Add comments near the magnitude branch stating:
    - response removed
    - Wood-Anderson simulated
    - intended for later local-magnitude amplitude measurement, especially on horizontal components
  - Verify required deliverables:
    - `station.sta`
    - phase-picking daily 3-C MiniSEED files
    - magnitude-estimation daily 3-C MiniSEED files
    - one preprocessing figure
    - QC/summary tables
- Constraints:
  - Do not create a separate narrative/report script.
  - Final acceptance requires correct date restriction, valid 3-C assembly, separate phase and magnitude products, progress reporting, and parallel execution support.
- Key outputs:
  - Final deliverable inventory table
  - Acceptance checklist with pass/fail status for each requested requirement

### Task Script Organization

#### Script 1: `preprocess_ridgecrest_stationday_waveforms`
- Task description:
  - Single primary script handling StationXML parsing, `station.sta` generation, station-day discovery, completeness assessment, phase-picking preprocessing, magnitude-estimation preprocessing, parallel execution, progress reporting, final readback validation, compact QC summary writing, and creation of one diagnostic figure.
- Required data sources:
  - `<DATA_ROOT>/Science2019_Ross_Ridgecrest/data/waveforms_raw`
  - `<DATA_ROOT>/Science2019_Ross_Ridgecrest/data/stationxml/`
- Parameter selection strategy:
  - Explicitly hard-code the full-window UTC range with `obspy.UTCDateTime`.
  - Parallelize by station-day up to 64 workers.
  - Build both downstream products from the same validated station-day raw selection to keep comparisons consistent.
- Constraints:
  - No temporary/intermediate waveform files.
  - Must include immediate output validation and failure evidence collection in the same script.
- Key outputs:
  - `station.sta`
  - phase-picking MiniSEED outputs
  - magnitude-estimation MiniSEED outputs
  - QC/summary tables
  - one preprocessing diagnostic figure