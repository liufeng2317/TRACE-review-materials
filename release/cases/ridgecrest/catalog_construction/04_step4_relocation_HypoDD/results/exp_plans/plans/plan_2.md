# Goal
Relocate the Ridgecrest earthquakes in the full-window 2019-07-04 to 2019-07-26 using the `PAL_HypoDD` Python workflow around HypoDD, then quantify and visualize differences between the original Gamma locations and the relocated catalog.

## Planning Assumptions
- Use observation-derived inputs only: Gamma phase association/location outputs and station metadata supplied in the available data sources.
- `PAL_HypoDD` package contract requires the Python workflow:
  `Config -> optional PAL2HypoDD_PhaseConverter -> read_fpha -> mk_sta -> mk_pha -> run_ph2dt -> Run_HypoDD -> merge_hypodd_output`.
- `Config` is a Python object, not YAML/JSON. In this environment, `hypo_root` must be `<PROJECT_ROOT>/software/hypoDD/HYPODD/src`.
- If the Gamma `phase_YYYYMMDD.dat` files are still in PAL/Gamma `EVENT`/`STATION` text format, first convert them with `PAL2HypoDD_PhaseConverter(...).transform()` and then use the converted phase file as `cfg.fpha`.
- `mk_pha()` filters by `ot_range`, `lat_range`, and `lon_range` before ph2dt/HypoDD; incorrect bounds can produce zero selected events or empty differential-time files.
- Native relocation success evidence must include non-empty merged outputs such as `{ctlg_code}.loc`, `{ctlg_code}.reloc`, `{ctlg_code}.pha`, and logs (`ph2dt.log`, `hypoDD.log`); conversion-only or plotting-only outputs are not success.
- Current local HYPODD compiled limits include `MAXEVE=10800`, `MAXDATA=3100000`, `MAXSTA=1300`; this full-window Ridgecrest subset and 47 stations are expected to fit a single run, but preflight counts must still be checked.
- User requires all times to remain in `obspy.UTCDateTime`-compatible ISO UTC strings or `UTCDateTime` objects during processing; do not convert times to Unix timestamps.
- User requires all parameters/settings to be defined inside the script and progress to be printed during runtime.
- `keep_grids` should be set to `False` per user request not to keep grid outputs.

## Analysis Plan

### Task 1: Build a single primary relocation-and-analysis script
- Task description:
  Create one cohesive script that ingests the two daily Gamma phase/catalog files and station metadata, prepares PAL_HypoDD inputs, runs HypoDD relocation, validates outputs, computes relocation statistics, and generates comparison figures.
- Required data sources:
  - `<CASE_ROOT>/catalog_construction/01_step3_association_Gamma/exp_run/outputs/01_gamma_association_location_magnitude/phase_20190704.dat`
  - `<CASE_ROOT>/catalog_construction/01_step3_association_Gamma/exp_run/outputs/01_gamma_association_location_magnitude/phase_20190705.dat`
  - `<CASE_ROOT>/catalog_construction/01_step3_association_Gamma/exp_run/outputs/01_gamma_association_location_magnitude/catalog_20190704.dat`
  - `<CASE_ROOT>/catalog_construction/01_step3_association_Gamma/exp_run/outputs/01_gamma_association_location_magnitude/catalog_20190705.dat`
  - `<CASE_ROOT>/catalog_construction/01_step1_data_preprocessing_for_phasepicking/exp_run/outputs/01_preprocess_ridgecrest_stationday_waveforms/station.sta`
- Parameter selection strategy:
  - Restrict to events with origin times in `[2019-07-04T00:00:00Z, 2019-07-26T00:00:00Z)`.
  - Merge the two daily phase files into one working phase file and the two daily catalog files into one original catalog table.
  - Set `ctlg_code` explicitly for this run, e.g. a full-window Ridgecrest identifier.
  - Set `ot_range` in PAL_HypoDD string format consistent with the full-window, covering 20190704 to 20190726.
  - Compute `lat_range` and `lon_range` from station metadata:
    - `lat_range = [station_lat_min - 0.1, station_lat_max + 0.1]`
    - `lon_range = [station_lon_min - 0.1, station_lon_max + 0.1]`
  - Set `num_grids=[1,1]` unless preflight shows the run exceeds compiled limits.
  - Set `keep_grids=False`.
  - Keep `dep_corr`, `xy_pad`, `num_workers`, `ph2dt_params`, and `hypoDD_reloc_params` explicitly defined in the script; start from package defaults only where needed and document any task-specific overrides in code comments or printed config summary.
- Constraints:
  - All origin and pick times must be parsed with `obspy.UTCDateTime`.
  - Do not transform times to numeric timestamps for filtering or matching.
  - Preserve station names in `NET.STA` format and verify consistency between phase and station files before relocation.
  - Show run progress with clear print/log statements for:
    - file loading
    - event/station counts
    - computed bounds
    - conversion status
    - ph2dt execution
    - per-grid HypoDD execution
    - merge status
    - post-run validation
    - figure/statistics generation
- Key outputs:
  - One merged PAL_HypoDD-ready phase input file for the full-window
  - One merged original catalog table for the full-window
  - One merged relocated catalog from PAL_HypoDD/HypoDD
  - One compact machine-readable summary table of relocation statistics
  - Comparison figures between original and relocated seismicity

### Task 1.1: Preflight data audit and input harmonization
- Task description:
  Inspect and harmonize the supplied Gamma and station inputs before relocation.
- Required data sources:
  - Both `phase_YYYYMMDD.dat` files
  - Both `catalog_YYYYMMDD.dat` files
  - `station.sta`
- Parameter selection strategy:
  - Parse station file into columns: station code, latitude, longitude, elevation, extra field.
  - Parse phase files as repeated `EVENT` blocks with following `STATION` records.
  - Treat `-1` pick values as missing picks and exclude them from phase-specific counts.
  - Parse catalog rows into `origin_time`, `lat`, `lon`, `dep`, `mag`.
- Constraints:
  - Confirm station count and station code uniqueness.
  - Confirm total event counts from daily catalogs and compare against event blocks in daily phase files.
  - Confirm all event times fall within the requested full-window.
  - Check that every phase-file station code exists in station metadata; if not, stop and record mismatches.
- Key outputs:
  - Preflight counts: number of stations, total original events, total phase events, total P picks, total S picks
  - Station code mismatch table if any
  - Computed `lat_range` and `lon_range` with 0.1 padding

### Task 1.2: Prepare PAL_HypoDD-compatible inputs
- Task description:
  Convert or reformat the merged Gamma phase file into the phase format accepted by the PAL_HypoDD workflow and prepare station input.
- Required data sources:
  - Merged full-window phase file
  - `station.sta`
- Parameter selection strategy:
  - If the merged phase file remains in Gamma/PAL `EVENT`/`STATION` text form, run `PAL2HypoDD_PhaseConverter` and assign the returned file path to `cfg.fpha`.
  - Use the supplied station file directly as `cfg.fsta` if its format is accepted by `mk_sta`; otherwise create a minimally reformatted station file preserving station code, latitude, longitude, elevation.
- Constraints:
  - Do not alter event times or pick times beyond required format conversion.
  - Do not drop events solely because P or S is missing, unless the package parser requires a minimum valid pick set; if so, record how many events are removed and why.
  - After conversion, run `read_fpha(cfg.fpha)` and verify non-zero parsed events.
- Key outputs:
  - PAL_HypoDD input phase file for the full-window run
  - Validated station input file for `mk_sta`
  - Parsed phase dictionary and magnitude dictionary counts

### Task 1.3: Configure and execute HypoDD relocation
- Task description:
  Run the documented PAL_HypoDD workflow for the full-window.
- Required data sources:
  - Prepared phase file from Task 1.2
  - Station file
  - Computed ranges from Task 1.1
- Parameter selection strategy:
  - Build `Config` with explicit values for:
    - `hypo_root=<PROJECT_ROOT>/software/hypoDD/HYPODD/src`
    - `ctlg_code`
    - `fsta`
    - `fpha`
    - `ot_range`
    - `lat_range`
    - `lon_range`
    - `num_grids=[1,1]`
    - `keep_grids=False`
    - `num_workers` chosen conservatively relative to available CPU
    - `hypoDD_reloc_params` and `ph2dt_params` explicitly defined in script
  - Use `mk_sta`, `mk_pha`, `run_ph2dt`, `Run_HypoDD`, and `merge_hypodd_output` in package-required order.
- Constraints:
  - Before full run, check:
    - number of parsed events <= `MAXEVE=10800`
    - station count <= `MAXSTA=1300`
  - After `mk_pha`, verify `evid_lists.npy` contains selected events.
  - After `run_ph2dt`, verify non-empty `dt_*.ct` and non-zero ph2dt selection.
  - After HypoDD, require non-empty merged `.loc` and `.reloc`.
  - If merged relocation is empty, inspect and preserve failure evidence from `ph2dt.log`, `hypoDD.log`, and per-grid logs; do not treat the run as success.
- Key outputs:
  - Merged native HypoDD outputs:
    - `{ctlg_code}.loc`
    - `{ctlg_code}.reloc`
    - `{ctlg_code}.pha`
    - `{ctlg_code}.res`
    - `ph2dt.log`
    - `hypoDD.log`
  - Loadable original and relocated catalogs via PAL_HypoDD helpers

### Task 1.4: Match original and relocated events
- Task description:
  Build a reliable comparison table between the original Gamma catalog and the relocated HypoDD catalog.
- Required data sources:
  - Original merged catalog from daily `catalog_YYYYMMDD.dat`
  - PAL_HypoDD-loaded original catalog
  - PAL_HypoDD-loaded relocated catalog
  - Event IDs/order information produced during phase conversion and PAL_HypoDD preparation
- Parameter selection strategy:
  - Prefer preserved event IDs from the prepared phase / PAL_HypoDD workflow for matching.
  - If explicit IDs are not directly exposed in the final tables, match within the same run using verified preserved order or exact/near-exact origin time consistency from the PAL_HypoDD-generated original catalog, not by blindly matching relocated rows to the raw Gamma catalog row index.
- Constraints:
  - Do not assume `.reloc` contains all input events.
  - Produce a three-way accounting:
    - total original events in full-window catalog
    - events selected into HypoDD processing
    - events successfully relocated
- Key outputs:
  - Comparison table with, at minimum:
    - original origin time
    - original lat/lon/depth/mag
    - relocated lat/lon/depth
    - relocation status
    - horizontal shift
    - depth change

### Task 1.5: Compute relocation statistics
- Task description:
  Summarize how relocation changed the catalog.
- Required data sources:
  - Comparison table from Task 1.4
- Parameter selection strategy:
  - Compute:
    - total number of original events
    - total number of selected events
    - total number of relocated events
    - relocation success rate
    - lat/lon/depth ranges before and after relocation
    - horizontal displacement for each relocated event
    - summary statistics of displacement: mean, median, percentile range, maximum
    - depth change statistics
  - Use geodetic horizontal distance from original vs relocated coordinates.
- Constraints:
  - Keep times in `UTCDateTime`/ISO format in all tables.
  - Report statistics separately for:
    - full original full-window catalog
    - relocated subset
  - If magnitudes are available only in the original catalog, preserve them for plotting and subgroup summaries.
- Key outputs:
  - Relocation summary table
  - Event distribution summary by day and by relocation status
  - Optional histogram-ready arrays for plotting horizontal shift and depth change

### Task 1.6: Generate diagnostic and comparison figures
- Task description:
  Produce figures that show the spatial effect of relocation and the basic catalog statistics requested by the user.
- Required data sources:
  - Station metadata
  - Original catalog
  - Relocated catalog
  - Comparison statistics
- Parameter selection strategy:
  - Minimum figure set:
    1. Map-view comparison:
       - panel A: original Gamma epicenters
       - panel B: relocated epicenters
       - overlay station locations
    2. Direct difference map:
       - original and relocated epicenters together, connected by line segments for a representative subset or all events if visually readable
    3. Depth cross-sections:
       - longitude-depth before vs after
       - latitude-depth before vs after
    4. Statistical summary plots:
       - histogram of horizontal relocation distance
       - histogram of depth change
       - bar chart/table panel of counts: original, selected, relocated
  - Use the same geographic bounds for original and relocated map panels, based on padded station-derived region or combined event extent.
- Constraints:
  - Show clearly the difference between original and relocated event distributions.
  - Separate non-relocated events from relocated ones when needed.
  - Keep figure inputs limited to the full-window only.
- Key outputs:
  - Catalog comparison map figure
  - Cross-section figure(s)
  - Relocation statistics figure

### Task 1.7: Runtime progress and validation reporting inside the script
- Task description:
  Ensure the single script is executable as an end-to-end workflow with visible progress and immediate failure evidence collection.
- Required data sources:
  - All inputs and intermediate PAL_HypoDD outputs
- Parameter selection strategy:
  - Print progress checkpoints such as:
    - “Loading station metadata”
    - “Loading phase files”
    - “Merging full-window inputs”
    - “Computed lat/lon bounds”
    - “Converting phase file for PAL_HypoDD”
    - “Running mk_sta / mk_pha / ph2dt / HypoDD”
    - “Merging HypoDD outputs”
    - “Loading relocated catalog”
    - “Computing statistics”
    - “Saving figures”
  - Print key counts after each stage.
- Constraints:
  - Immediate stop conditions:
    - no parsed events
    - station mismatch
    - zero selected events after `mk_pha`
    - empty `dt_*.ct`
    - missing or empty merged `.reloc`
  - If failure occurs, script should preserve and report relevant native log file names rather than masking the error.
- Key outputs:
  - Console progress trace
  - Validation summary indicating whether relocation was scientifically successful and how many events were relocated