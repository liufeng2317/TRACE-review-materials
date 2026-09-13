# Data Descriptions
## phase_picking
**Source path**: `<CASE_ROOT>/catalog_construction/01_step1_data_preprocessing_for_phasepicking/exp_run/outputs/01_preprocess_ridgecrest_stationday_waveforms/phase_picking`
### Summary
This data source contains preprocessed continuous MiniSEED waveform files organized by day for Ridgecrest phase-picking workflows. For the requested time window, day folders exist for 20190704 through 20190725, with one 24-hour three-component waveform file per station; station metadata is stored separately in the sibling file `station.sta`.
### Detail
#### Folder Structure
- Base waveform directory: `<CASE_ROOT>/catalog_construction/01_step1_data_preprocessing_for_phasepicking/exp_run/outputs/01_preprocess_ridgecrest_stationday_waveforms/phase_picking`
- Sibling metadata file: `<CASE_ROOT>/catalog_construction/01_step1_data_preprocessing_for_phasepicking/exp_run/outputs/01_preprocess_ridgecrest_stationday_waveforms/station.sta`
- Sibling directories at the same level as `phase_picking`: `figures`, `magnitude_wood_anderson`, `qc`

Observed day subfolders under `phase_picking`:
- `20190704/`
- `20190705/`

For the user-prioritized processing window, these are the available day folders. No `20190706/` subfolder was observed in this directory snapshot; the `20190705` files already span up to `2019-07-26T00:00:00Z`.

Example paths:
- `/.../phase_picking/20190704/CI.CCC.20190704T000000Z.20190705T000000Z.mseed`
- `/.../phase_picking/20190705/CI.CCC.20190705T000000Z.20190706T000000Z.mseed`
- `/.../station.sta`

#### File Naming and Organization
- MiniSEED naming pattern matches the user description:
  - `{network}.{station}.{start_time}.{end_time}.mseed`
- Observed examples:
  - `CI.CCA.20190704T000000Z.20190705T000000Z.mseed`
  - `CI.CCC.20190704T000000Z.20190705T000000Z.mseed`
  - `CI.CGO.20190705T000000Z.20190706T000000Z.mseed`
- Practical parsing from filename:
  - `network`: `CI`
  - `station`: e.g. `CCC`
  - `station_id` suitable for future pick outputs: `CI.CCC`
  - `start_time` / `end_time`: ISO-like UTC strings embedded in the filename
- One file appears to represent one station-day continuous record.

Observed file counts:
- `20190704`: 27 MiniSEED files
- `20190705`: 31 MiniSEED files

#### MiniSEED Metadata Relevant for Phase Picking
Head-only inspection of sample files shows consistent structure:
- Format: MiniSEED
- Traces per file: 3
- Channels: `HHE`, `HHN`, `HHZ`
- Sampling rate: `100.0 Hz`
- Samples per trace: `8,640,000`
- Approximate duration per trace: full 24 hours
- Example trace IDs:
  - `CI.CCA..HHE`
  - `CI.CCA..HHN`
  - `CI.CCA..HHZ`

Sample file metadata:
- File: `CI.CCA.20190704T000000Z.20190705T000000Z.mseed`
  - `CI.CCA..HHE`: start `2019-07-04T00:00:00.008300Z`, end `2019-07-04T23:59:59.998300Z`, `npts=8640000`, `sr=100.0`
  - `CI.CCA..HHN`: start `2019-07-04T00:00:00.008300Z`, end `2019-07-04T23:59:59.998300Z`, `npts=8640000`, `sr=100.0`
  - `CI.CCA..HHZ`: start `2019-07-04T00:00:00.008300Z`, end `2019-07-04T23:59:59.998300Z`, `npts=8640000`, `sr=100.0`
- The same pattern was observed for sampled stations `CI.CCC` and `CI.CGO`.

Important loading note for future agents:
- The actual trace start time is offset slightly from midnight (`00:00:00.008300Z`) rather than exactly `00:00:00Z`, even though the filename encodes midnight boundaries. If precise pick times are written back out, use trace/header times from ObsPy rather than assuming an exact filename boundary.

#### Station Metadata File
Path:
- `<CASE_ROOT>/catalog_construction/01_step1_data_preprocessing_for_phasepicking/exp_run/outputs/01_preprocess_ridgecrest_stationday_waveforms/station.sta`

Observed characteristics:
- Plain text, comma-separated
- No header row detected
- Number of lines: 32
- Appears to encode one station per line

Observed row pattern:
- `station_id,latitude,longitude,elevation,<extra_numeric_field>`

Example rows:
- `CI.CCA,35.152520,-118.016490,710.00,626886820.397744`
- `CI.CCC,35.524950,-117.364530,670.00,627368612.812223`
- `CI.CGO,36.550400,-117.802950,2795.00,629864666.666667`

Likely usable columns for future waveform/pick association:
1. `station_id` (e.g. `CI.CCC`)
2. `latitude`
3. `longitude`
4. `elevation`
5. an additional numeric field of unclear meaning from inspection alone

Because there is no header, future agents should assign column names explicitly when loading.

#### Access Pattern for Future Agents
Recommended lookup pattern for the requested full-window processing window:
- Day folder `20190704` -> files spanning `2019-07-04T00:00:00Z` to `2019-07-05T00:00:00Z`
- Day folder `20190705` -> files spanning `2019-07-05T00:00:00Z` to `2019-07-26T00:00:00Z`

Typical workflow-relevant joins:
- Derive `station_id` from filename as `network.station`
- Match that `station_id` to the first field of `station.sta`
- Read waveform traces with ObsPy; each file already contains the 3 components needed for common PhaseNet-style inference

#### Practical Loading Notes
- ObsPy is available in the environment and successfully reads these files.
- Sample read method used successfully: `obspy.read(path, headonly=True)`
- Since each file contains 24-hour 100 Hz 3-component data, future agents should expect large in-memory arrays if loading full waveforms rather than headers only.
- For output formatting requested by the user later, the existing data supports straightforward construction of:
  - `station_id` from filename or trace metadata
  - `phase_time` from ObsPy `UTCDateTime`
  - `phase_amplitude` from the raw waveform at pick index
  - `phase_type` from the downstream picker output

#### Summary of What Is Available
- Preprocessed station-day continuous waveform files in MiniSEED format
- Daily subfolder organization by start date
- Mostly one file per station per day
- Three-component HH? traces at 100 Hz
- Separate station metadata table keyed by `station_id`
- Available data for the user-prioritized window: `20190704` through `20190725` day folders

------------------------------

## station.sta
**Source path**: `<CASE_ROOT>/catalog_construction/01_step1_data_preprocessing_for_phasepicking/exp_run/outputs/01_preprocess_ridgecrest_stationday_waveforms/station.sta`
### Summary
`station.sta` is a plain-text, comma-separated station metadata table used to associate waveform files with station locations and identifiers. It contains 32 rows without a header, where the first field is the station identifier matching MiniSEED filename prefixes such as `CI.CCC`.
### Detail
#### File Overview
- Path: `<CASE_ROOT>/catalog_construction/01_step1_data_preprocessing_for_phasepicking/exp_run/outputs/01_preprocess_ridgecrest_stationday_waveforms/station.sta`
- Format: plain text, comma-separated values
- Header row: not present
- Number of rows: 32
- Intended role in workflow: station lookup table for mapping waveform files / pick outputs to station metadata

#### Observed Row Structure
Each row has 5 comma-separated fields:
1. `station_id`
2. `latitude`
3. `longitude`
4. `elevation`
5. `extra_numeric_field` (present but unlabeled in the file)

Observed examples:
- `CI.CCA,35.152520,-118.016490,710.00,626886820.397744`
- `CI.CCC,35.524950,-117.364530,670.00,627368612.812223`
- `CI.CGO,36.550400,-117.802950,2795.00,629864666.666667`
- `CI.CLC,35.815740,-117.597510,775.00,627369000.000000`
- `CI.CWC,36.439047,-118.080495,1569.50,629865000.000000`

#### Column Interpretation
Likely field meanings from direct inspection:
- `station_id`: network and station code combined, e.g. `CI.CCC`
- `latitude`: decimal degrees
- `longitude`: decimal degrees
- `elevation`: likely meters above sea level
- `extra_numeric_field`: additional station-related numeric metadata; meaning is not labeled in the file and should not be assumed without external documentation

#### Relationship to Waveform Files
The `station_id` field matches the leading parts of MiniSEED filenames in the sibling `phase_picking` directory.

Examples:
- Station table entry: `CI.CCC`
- Matching waveform file prefix: `CI.CCC.20190704T000000Z.20190705T000000Z.mseed`

This makes `station_id` the key field for joining:
- station metadata from `station.sta`
- waveform files in `phase_picking/YYYYMMDD/*.mseed`
- future pick records where `station_id` is expected in output CSVs

#### Loading Notes for Future Agents
Because there is no header row, future agents should assign column names explicitly when loading.

Suggested column names:
- `station_id`
- `latitude`
- `longitude`
- `elevation`
- `extra_numeric_field`

Practical parsing characteristics:
- delimiter: comma
- text encoding: readable as standard text during inspection
- no quoting or nested structures observed
- one station per line

#### Example Access Pattern
Useful for downstream code:
- Load `station.sta` as a 5-column CSV with no header.
- Use `station_id` as the join key to waveform filenames and pick output rows.
- Use `latitude`, `longitude`, and `elevation` for station metadata annotation if needed.

#### Relevant Metadata for the User-Prioritized Task
Most relevant fields for future phase-picking agents:
- `station_id`: required to label picks as values like `CI.CCC`
- `latitude`, `longitude`, `elevation`: available for station context and possible plotting/QC
- The fifth numeric field exists but is not self-describing from file inspection alone, so agents should treat it as auxiliary metadata unless external documentation clarifies it.

------------------------------

