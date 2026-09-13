# Data Descriptions
## waveforms_raw
**Source path**: `<DATA_ROOT>/Science2019_Ross_Ridgecrest/data/waveforms_raw`
### Summary
This data source contains continuous MiniSEED waveform data organized by station directory (`network.station`) plus matching StationXML metadata in a parallel directory. The waveform filenames encode network, station, location, channel, and UTC day start/end times, which is directly suitable for selecting the requested 2019-07-04 to 2019-07-26 station-day inputs and pairing them with station metadata for gain/response lookup.
### Detail
#### Overview
The Ridgecrest raw waveform archive is stored under `<DATA_ROOT>/Science2019_Ross_Ridgecrest/data/waveforms_raw` and is accompanied by per-station StationXML files under `<DATA_ROOT>/Science2019_Ross_Ridgecrest/data/stationxml`. The waveform side contains **52 station directories** and about **3032 MiniSEED files**; the StationXML side contains **50 XML files**.

For future preprocessing agents, the organization is already close to the requested station-day processing model: one directory per station and generally one MiniSEED file per channel per UTC day. The user-requested date window `2019-07-04` to `2019-07-26` can be selected directly from the filename timestamps.

#### Folder Structure
Waveforms:
- Base: `<DATA_ROOT>/Science2019_Ross_Ridgecrest/data/waveforms_raw`
- Station subdirectories follow:
  - `<DATA_ROOT>/Science2019_Ross_Ridgecrest/data/waveforms_raw/{network}.{station}/`
- Example station folders:
  - `CI.CCA`
  - `CI.CCC`
  - `CI.CGO`
  - `CI.CLC`
  - `CI.CWC`
  - `CI.DAW`

Station metadata:
- Base: `<DATA_ROOT>/Science2019_Ross_Ridgecrest/data/stationxml`
- One XML file per station:
  - `<DATA_ROOT>/Science2019_Ross_Ridgecrest/data/stationxml/{network}.{station}.xml`
- Example files:
  - `CI.CCA.xml`
  - `CI.CCC.xml`
  - `CI.CGO.xml`

#### Waveform File Naming Pattern
MiniSEED filenames follow the pattern:
- `{network}.{station}.{location}.{channel}__{start_time}__{end_time}.mseed`

Example:
- `CI.CCA..HHE__20190704T000000Z__20190705T000000Z.mseed`

Parsed fields:
- `network`: seismic network code, e.g. `CI`
- `station`: station code, e.g. `CCA`
- `location`: location code; may be empty (`..`), or values like `00`, `CC`
- `channel`: component/channel code, e.g. `HHE`, `HHN`, `HHZ`, `EH1`, `EH2`, `EHZ`, `HH1`, `HH2`
- `start_time`, `end_time`: UTC interval encoded as `YYYYMMDDTHHMMSSZ`

This naming scheme is sufficient to:
- identify station-day records without reading file contents first,
- group three components by station and day,
- filter explicitly to the requested range:
  - `20190704T000000Z` to `20190705T000000Z`
  - `20190705T000000Z` to `20190706T000000Z`
  - note that files beginning `20190706T000000Z` cover the following UTC day and would only be included if the processing convention treats the end date as inclusive of that full day.

#### Organization Relevant to Station-Day Processing
Typical organization per station:
- multiple daily files per component channel
- generally one file per channel per UTC day
- expected grouping for 3-component processing is by:
  - station directory (`network.station`)
  - day interval (`start_time`, `end_time`)
  - component family (commonly `HH*`, sometimes `EH*` or `HH1/HH2/HHZ`)

Examples of per-station file counts observed:
- `CI.CCA`: 64 files
- `CI.CCC`: 65 files
- `CI.CGO`: 64 files
- `CI.CLC`: 57 files
- `CI.DAW`: 66 files

This suggests that not every station has exactly the same day/component coverage, so future agents should expect missing days or missing components for some stations.

#### Channel and Location Metadata Patterns
Most common channel codes in filenames:
- `HHZ`: 905 files
- `HHN`: 810 files
- `HHE`: 805 files
- `EHZ`: 152 files
- `HH1`: 95 files
- `HH2`: 94 files
- `EH2`: 86 files
- `EH1`: 85 files

Most common location codes:
- empty location code `""` (rendered as `..` in filenames): 2464 files
- `CC`: 285 files
- `00`: 283 files

Implications for future agents:
- Prefer grouping by full SEED id (`network.station.location.channel`) rather than assuming blank location codes.
- Horizontal components may appear either as `E/N` or `1/2`; code should support both when assembling three-component streams.
- For station gain averaging requested by the user, channel-family selection should likely inspect `HH*` first, then `EH*` if no `HH*` are available.

#### Time Coverage Pattern
Filename timestamps indicate daily UTC chunks. Sample high-frequency date pairs show repeated full-day coverage across July 2019. Relevant requested days are present in the archive, with example files such as:
- `<DATA_ROOT>/Science2019_Ross_Ridgecrest/data/waveforms_raw/CI.CCA/CI.CCA..HHE__20190704T000000Z__20190705T000000Z.mseed`
- `<DATA_ROOT>/Science2019_Ross_Ridgecrest/data/waveforms_raw/CI.CCA/CI.CCA..HHE__20190705T000000Z__20190706T000000Z.mseed`
- `<DATA_ROOT>/Science2019_Ross_Ridgecrest/data/waveforms_raw/CI.CCA/CI.CCA..HHE__20190706T000000Z__20190707T000000Z.mseed`

#### Sample MiniSEED File Metadata
Inspected example file:
- Path: `<DATA_ROOT>/Science2019_Ross_Ridgecrest/data/waveforms_raw/CI.CCC/CI.CCC..HHE__20190704T000000Z__20190705T000000Z.mseed`

ObsPy header summary:
- Trace id: `CI.CCC..HHE`
- Number of traces in file: `1`
- Start time: `2019-07-04T00:00:00.008300Z`
- End time: `2019-07-04T23:59:59.998300Z`
- Sampling rate: `100.0 Hz`
- Delta: `0.01 s`
- Number of samples: `8640000`
- MiniSEED encoding: `STEIM1`
- Record length: `4096`
- Byte order: `>`
- Data quality: `D`

Important observation for preprocessing code:
- Although the filename encodes exact UTC day boundaries, the actual trace start/end times may be offset by a few milliseconds from midnight. Future agents should rely on `obspy.UTCDateTime` and trim/merge explicitly rather than assuming perfect boundary alignment from filenames alone.

#### StationXML Metadata Structure
StationXML files are per station and can be read with ObsPy `read_inventory`. They contain the fields needed for:
- station coordinates,
- elevation,
- channel list,
- sample rates,
- instrument response / sensitivity information for gain and response removal.

Sample StationXML metadata examples:
- `CI.CCA.xml`
  - network: `CI`
  - station: `CCA`
  - latitude: `35.15252`
  - longitude: `-118.01649`
  - elevation_m: `710.0`
  - channels: `HHE`, `HHN`, `HHZ`
  - sample rate: `100.0`
- `CI.CCC.xml`
  - latitude: `35.52495`
  - longitude: `-117.36453`
  - elevation_m: `670.0`
  - channels: `HHE`, `HHN`, `HHZ`
  - sample rate: `100.0`
- `CI.CGO.xml`
  - latitude: `36.5504`
  - longitude: `-117.80295`
  - elevation_m: `2795.0`
  - channels: `HHE`, `HHN`, `HHZ`
  - sample rate: `100.0`

Across inspected XML files:
- typical number of channels per station: `3`
- typical sample rate: `100 Hz`
- channel triplets are commonly `HHE/HHN/HHZ`

#### Mapping Between Waveforms and Station Metadata
Expected join key:
- waveform station directory / filename prefix: `{network}.{station}`
- StationXML filename: `{network}.{station}.xml`

Example mapping:
- waveform directory: `waveforms_raw/CI.CCC/`
- station metadata: `stationxml/CI.CCC.xml`

This direct naming alignment should make it straightforward for future agents to:
- locate metadata for each waveform station,
- build `station.sta`-style outputs from inventory fields,
- extract gains/sensitivities from the three relevant channels.

#### Data Quality / Completeness Notes
- The filename audit found **no malformed filenames** among inspected files.
- File counts differ by station, so completeness should not be assumed globally.
- Some stations may use alternate horizontal channel naming (`1/2` instead of `E/N`) or non-empty location codes.
- There are more waveform station directories (52) than StationXML files (50), so future agents should handle the possibility that a small number of waveform stations may not have a matching XML file in the metadata directory.

#### Practical Loading Guidance for Future Agents
Useful path patterns:
- All waveform files for one station:
  - `<DATA_ROOT>/Science2019_Ross_Ridgecrest/data/waveforms_raw/{network}.{station}/*.mseed`
- Requested-day files for one station (example 2019-07-04):
  - `<DATA_ROOT>/Science2019_Ross_Ridgecrest/data/waveforms_raw/{network}.{station}/*__20190704T000000Z__20190705T000000Z.mseed`
- Matching station metadata:
  - `<DATA_ROOT>/Science2019_Ross_Ridgecrest/data/stationxml/{network}.{station}.xml`

Recommended grouping fields when loading:
- `network`
- `station`
- `location`
- `channel`
- `start_time`
- `end_time`

Recommended metadata fields to inspect from StationXML for the user’s downstream workflow:
- station latitude
- station longitude
- station elevation (meters)
- channel codes
- channel sample rates
- instrument sensitivity / overall gain
- full response information for response removal and Wood-Anderson simulation

#### Relevance to the User Request
Relevant source data for the requested preprocessing workflow are present:
- continuous raw waveform MiniSEED files by station/day/component,
- per-station StationXML files needed for coordinates, elevation, gain estimation, and response removal.

The archive structure supports future scripts that explicitly define `obspy.UTCDateTime('2019-07-04T00:00:00')` through `obspy.UTCDateTime('2019-07-26T00:00:00')` (or equivalent inclusive/exclusive logic), iterate over station directories, assemble 3-component station-day streams, and pair each station with `stationxml/{network}.{station}.xml`.

------------------------------

## stationxml
**Source path**: `<DATA_ROOT>/Science2019_Ross_Ridgecrest/data/stationxml/`
### Summary
This directory contains 50 per-station StationXML files named `{network}.{station}.xml`, providing the metadata needed to map station codes to coordinates, elevation, channel configuration, sample rate, and instrument response. The files are directly suitable for building a `station.sta` table and for locating channel sensitivities and response stages required by future preprocessing agents.
### Detail
#### Overview
The station metadata archive is stored in `<DATA_ROOT>/Science2019_Ross_Ridgecrest/data/stationxml/` and contains **50 StationXML files**. Each file is named by station, typically matching waveform station identifiers via the pattern `{network}.{station}.xml`, making it easy to join waveform data and metadata by station code.

For future agents, these StationXML files contain the key fields prioritized by the user request: station latitude, longitude, elevation, channel list, location codes, sample rates, and channel-level instrument sensitivities/response metadata. This is the authoritative source for computing station-level gain summaries and for instrument response removal or Wood-Anderson simulation later in the workflow.

#### Folder Structure
Base directory:
- `<DATA_ROOT>/Science2019_Ross_Ridgecrest/data/stationxml/`

File organization pattern:
- One XML file per station
- Filename convention:
  - `{network}.{station}.xml`

Example files:
- `CI.CCA.xml`
- `CI.CCC.xml`
- `CI.CGO.xml`
- `CI.CLC.xml`
- `CI.CWC.xml`
- `CI.DAW.xml`
- `CI.DTP.xml`
- `CI.GSC.xml`
- `CI.HAR.xml`
- `CI.ISA.xml`

#### File Format
- Format: **StationXML**
- Readable with ObsPy `read_inventory`
- Contains inventory hierarchy:
  - `Network`
  - `Station`
  - `Channel`
  - `Response`

This structure supports both simple station table extraction and detailed channel/response inspection.

#### Naming and Mapping to Waveforms
StationXML filenames align with waveform station identifiers:
- waveform station directory: `{network}.{station}`
- station metadata file: `{network}.{station}.xml`

Example mapping:
- waveform folder: `waveforms_raw/CI.CCC/`
- metadata file: `stationxml/CI.CCC.xml`

This direct naming correspondence is useful for future agents that need to:
- find station coordinates for each waveform station,
- extract elevation in meters,
- identify matching channel codes (`HH*`, `EH*`),
- retrieve per-channel sensitivity/gain for averaging into `station.sta`.

#### Inventory Coverage Summary
Observed network distribution across the 50 files:
- `CI`: 30
- `ZY`: 8
- `GS`: 6
- `PB`: 4
- `NN`: 2

This means the metadata directory is not limited to a single network, so future code should not hardcode `CI` when parsing station metadata.

#### Channel Metadata Patterns
Most common channel codes across the inventory:
- `HHZ`: 53
- `HHE`: 47
- `HHN`: 47
- `EHZ`: 7
- `HH1`: 6
- `HH2`: 6
- `EH1`: 4
- `EH2`: 4

Most common location codes:
- empty location code `""`: 129
- `CC`: 27
- `00`: 18

Sample rate distribution:
- `100.0 Hz`: 168 channels
- `200.0 Hz`: 6 channels

Implications for future agents:
- Most stations are 3-component high-gain stations at 100 Hz.
- Horizontal components may be represented as `E/N` or `1/2`; grouping logic should support both.
- Location code may be blank or nonblank, so joins to waveform traces should use full SEED ids where needed.
- A small subset of channels operates at 200 Hz, so sampling rate should be checked per channel rather than assumed globally.

#### Station-Level Fields Available
Each StationXML file provides station metadata relevant to the requested station table and preprocessing workflow, including:
- `network code`
- `station code`
- `station latitude`
- `station longitude`
- `station elevation` (meters)
- `station start_date`
- `station end_date`
- `site name`
- channel inventory

Example station-level metadata from inspected files:
- `CI.CCA.xml`
  - network: `CI`
  - station: `CCA`
  - latitude: `35.15252`
  - longitude: `-118.01649`
  - elevation_m: `710.0`
  - start_date: `2002-04-04T00:00:00.000000Z`
  - end_date: `3000-01-01T00:00:00.000000Z`
  - channels: `HHE`, `HHN`, `HHZ`
- `CI.CCC.xml`
  - latitude: `35.52495`
  - longitude: `-117.36453`
  - elevation_m: `670.0`
  - channels: `HHE`, `HHN`, `HHZ`
- `CI.CGO.xml`
  - latitude: `36.5504`
  - longitude: `-117.80295`
  - elevation_m: `2795.0`
  - channels: `HHE`, `HHN`, `HHZ`

#### Channel-Level Fields Available
Each channel entry may include metadata useful for response-aware processing:
- `channel code`
- `location code`
- `azimuth`
- `dip`
- `sample_rate`
- `channel start_date`
- `channel end_date`
- `sensor type` (sometimes unset/`None` in inspected examples)
- `response stages`
- `instrument sensitivity`
- `input units`
- `output units`

Detailed example from `CI.CCA.xml`:
- Channel `HHE`
  - location_code: `""`
  - azimuth: `90.0`
  - dip: `0.0`
  - sample_rate: `100.0`
  - start_date: `2014-03-17T21:00:00.000000Z`
  - end_date: `2025-07-08T20:20:05.000000Z`
  - response_stages: `4`
  - instrument_sensitivity: `626910814.5186613`
  - input_units: `m/s`
  - output_units: `COUNTS`
- Channel `HHN`
  - azimuth: `0.0`
  - dip: `0.0`
  - instrument_sensitivity: `626910814.5186613`
- Channel `HHZ`
  - azimuth: `0.0`
  - dip: `-90.0`
  - instrument_sensitivity: `626838832.1559094`

These fields are directly relevant to the user’s requested downstream tasks because they support:
- construction of `network.station,latitude,longitude,elevation,gain`
- gain averaging across three channels (`HH*` or `EH*`)
- response removal for magnitude-oriented preprocessing
- orientation-aware component handling if needed

#### Instrument Sensitivity / Gain Information
StationXML channel responses include instrument sensitivity values that can serve as the source for the requested `gain` field. Inspected examples show per-channel sensitivities such as:
- `CI.CCA`: ~`6.27e8` counts per (`m/s`-based sensitivity)
- `CI.CCC`: ~`6.27e8`
- `CI.CGO`: ~`6.29e8` to `6.31e8`
- `CI.DAW`: ~`3.15e8`
- `CI.GSC`: ~`2.76e9` to `3.92e9`
- `CI.ISA`: ~`3.34e9` to `5.45e9`

Important for future agents:
- Gain values vary significantly across stations and sometimes across components.
- The appropriate station-level gain summary should therefore be computed from the actual channel sensitivities in each file, rather than assumed constant across stations.
- Input/output units in inspected files are typically `m/s` to `COUNTS`, which is relevant when interpreting response removal behavior.

#### Temporal Validity Metadata
Station and channel entries include validity windows (`start_date`, `end_date`). Example:
- station `CI.CCA`: active from `2002-04-04` to `3000-01-01`
- channel `HHE` at `CI.CCA`: active from `2014-03-17T21:00:00Z` to `2025-07-08T20:20:05Z`

This is useful for future agents processing the requested date range `2019-07-04` to `2019-07-26`, because they can verify whether a channel was active during that time before using it for gain estimation or response removal.

#### Relevance to the Requested Date Range
Although StationXML is not day-sliced, the metadata contain channel validity intervals that can be checked against the requested processing window:
- start of use window: `2019-07-04T00:00:00Z`
- end of use window: `2019-07-26T00:00:00Z` or equivalent explicit UTC-day logic

Future agents should prefer channel metadata whose active dates cover the waveform interval being processed.

#### Practical Loading Guidance for Future Agents
Recommended access pattern:
- locate station file by waveform station key:
  - `<DATA_ROOT>/Science2019_Ross_Ridgecrest/data/stationxml/{network}.{station}.xml`
- read using ObsPy:
  - `read_inventory(path)`
- extract for station table:
  - `network.code`
  - `station.code`
  - `station.latitude`
  - `station.longitude`
  - `station.elevation`
  - selected channel `response.instrument_sensitivity.value`
- extract for response-aware preprocessing:
  - channel code and location code
  - full channel response
  - sample rate
  - channel active dates

When implementing `station.sta`, future agents should be prepared to:
- choose the preferred channel family (`HH*` first, else `EH*` if needed)
- average the three channel sensitivities for a station-level gain value
- handle stations with `HH1/HH2/HHZ` or `EH1/EH2/EHZ` instead of `E/N/Z`

#### Data Quality / Structural Notes
- All inspected files were readable with ObsPy.
- The inventory is highly regular: most stations have exactly 3 channels.
- Some fields such as `sensor type` may be missing or reported as `None`, so future code should not rely on that field being populated.
- Response metadata and instrument sensitivity are present in inspected examples, which is the key requirement for future magnitude-oriented preprocessing.

#### Example Metadata Record Shape for Future Use
A station-level record can be formed from each XML as:
- `network.station`
- `latitude`
- `longitude`
- `elevation_m`
- `gain` = average of selected three channel sensitivities

A channel-level record can be formed as:
- `network.station.location.channel`
- `azimuth`
- `dip`
- `sample_rate`
- `instrument_sensitivity`
- `input_units`
- `output_units`
- `start_date`
- `end_date`

These are the main metadata fields future coding agents will need to efficiently pair station metadata with waveform traces and prepare downstream preprocessing scripts.

------------------------------

## station.sta
**Source path**: `station.sta`
### Summary
`station.sta` is referenced in the request as a derived station table, but no existing file content was provided or inspected here. Based on the requested format, future agents should expect or produce a simple CSV-like text file with one row per station containing `network.station`, coordinates, elevation in meters, and an averaged channel gain derived from StationXML metadata.
### Detail
#### Overview
The path `station.sta` is mentioned in the request as an output-style station information table rather than as an existing inspected source file. No on-disk metadata or sample contents were provided for this file in the current context, so the description below is limited to the **expected structure** implied by the user specification.

#### Expected File Role
This file is intended to store station-level metadata needed by later preprocessing and analysis steps, especially:
- station identification
- station coordinates
- elevation
- a station-level gain summary

It is conceptually a compact lookup table derived from the StationXML inventory.

#### Expected Format
Requested row format:
- `network.station,latitude,longitude,elevation,gain`

This implies a delimited text table with **five fields per row**:
1. `network.station`
2. `latitude`
3. `longitude`
4. `elevation`
5. `gain`

Likely examples of the first field:
- `CI.CCC`
- `CI.CCA`
- `PB.B917`
- `GS.CA06`

#### Expected Column Definitions
- `network.station`
  - string station identifier joining network and station code with a dot
  - intended join key to waveform directories and StationXML filenames
- `latitude`
  - numeric latitude in decimal degrees
- `longitude`
  - numeric longitude in decimal degrees
- `elevation`
  - numeric elevation in meters
- `gain`
  - numeric station-level gain
  - defined by the request as the average gain of the three channels from `HH*` or `EH*`

#### Expected Upstream Source Mapping
The requested station table would be derived from StationXML files under:
- `<DATA_ROOT>/Science2019_Ross_Ridgecrest/data/stationxml/`

Expected mapping logic for future agents:
- `network.station` from StationXML filename `{network}.{station}.xml`
- `latitude`, `longitude`, `elevation` from station-level metadata
- `gain` from averaging three channel sensitivities, typically from:
  - `HHE`, `HHN`, `HHZ`, or
  - `EH1`, `EH2`, `EHZ` / `EHE`, `EHN`, `EHZ` depending on station inventory

#### Relationship to Waveform Data
This station table is meant to support waveform preprocessing for station-day data under:
- `<DATA_ROOT>/Science2019_Ross_Ridgecrest/data/waveforms_raw/{network}.{station}/`

Join pattern:
- waveform station directory: `{network}.{station}`
- station table key: `network.station`
- StationXML filename: `{network}.{station}.xml`

This makes `station.sta` a convenient flattened lookup file for future agents that do not want to repeatedly open StationXML during bulk processing.

#### Likely File Characteristics
Based on the request, future agents should expect:
- plain text or CSV-like file
- one line per station
- no nested structure
- small enough to load fully into memory with standard CSV readers

Possible parsing assumptions:
- comma-separated values
- no header was explicitly specified, so future agents should check whether a header exists before parsing

#### Example Expected Rows
Illustrative examples based on the requested schema only:
- `CI.CCC,35.52495,-117.36453,670.0,<gain>`
- `CI.CCA,35.15252,-118.01649,710.0,<gain>`

The `<gain>` value should be treated as a numeric field derived from StationXML instrument sensitivity metadata, not assumed from the example.

#### Validation Checks Future Agents Should Perform
If `station.sta` exists, a future agent should inspect:
- whether the file has a header row
- delimiter type (expected comma)
- number of rows
- uniqueness of `network.station`
- missing values in latitude/longitude/elevation/gain
- whether `gain` reflects `HH*` or `EH*` averaging
- consistency with available StationXML and waveform station identifiers

#### Relevance to the User Request
This file is directly relevant to the requested preprocessing workflow because it provides a compact station metadata table for:
- station lookup
- geospatial metadata
- elevation access
- gain values for magnitude-related workflows

However, in the current context it should be treated as an **expected derived metadata product**, not an already-profiled source file, because no actual file contents were inspected.

------------------------------

