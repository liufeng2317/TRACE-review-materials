# Data Descriptions
## .env
**Source path**: `<CASE_ROOT>/data/hinet_account/.env`
### Summary
The data directory contains Hi-net account credentials metadata, existing regional JMA-derived event/pick/station products, station reference text, and a travel-time format PDF. The existing regional outputs are CSV-style structured catalogs plus project-specific comma-separated phase.dat/station.sta files for the Sanriku/Japan study area; no raw downloaded JMA measure chunk files were found in the inspected data tree.
### Detail
#### Folder Structure

Root inspected:
`<CASE_ROOT>/data`

Observed subdirectories:

- `hinet_account/`
  - Contains `.env` with Hi-net credential variable names.
  - File exists at: `data/hinet_account/.env`
  - Size: 54 bytes
  - Keys present: `HINET_USERNAME`, `HINET_PASSWORD`
  - Password values were not inspected or printed.
- `regional/`
  - Contains existing parsed/catalog products for the regional study area.
  - Files include: `events.csv`, `picks.csv`, `phase.dat`, `phase_new.dat`, `station.sta`, `main_earthquake.csv`, `summary.txt`.
- `stations/`
  - Contains `station.txt`, likely a station reference listing from JMA/Hi-net sources.
- `travel_time/`
  - Contains `format_e.pdf`, likely documentation for travel-time or related format conventions.

No existing raw files matching the requested future download naming pattern such as `measure_YYYYMMDD_N.txt` were observed within the inspected `data/` tree at max depth 3.

#### Credential Metadata

Credential file:
`<CASE_ROOT>/data/hinet_account/.env`

Observed variable names:

```text
HINET_USERNAME=<redacted>
HINET_PASSWORD=<redacted>
```

Future agents should load this file without logging credential values. The current file appears to define one account using username/password environment variables.

#### Existing Regional Event Catalog

File:
`data/regional/events.csv`

- Size: 2,627,700 bytes
- Rows: 29,896 data rows
- Format: CSV with header
- Columns:
  - `event_id` int64
  - `origin_time` string/object, UTC ISO timestamp with trailing `Z`
  - `latitude` float64
  - `longitude` float64
  - `depth_km` float64
  - `magnitude` float64
  - `region` string/object
  - `npicks` int64

Example rows:

```text
event_id,origin_time,latitude,longitude,depth_km,magnitude,region,npicks
1,2025-09-30T16:09:25.360000Z,38.702667,142.256833,41.34,2.8,E OFF MIYAGI PREF,35
2,2025-09-30T16:16:26.970000Z,39.417500,144.296000,44.70,0.8,FAR E OFF SANRIKU,13
3,2025-09-30T16:26:47.040000Z,39.430500,141.581667,14.63,0.1,SOUTHERN IWATE PREF,16
```

Note: This existing `events.csv` does not include a `source_file` column, although the requested future workflow asks for one.

#### Existing Regional Picks Table

File:
`data/regional/picks.csv`

- Size: 34,859,335 bytes
- Rows: 529,165 data rows
- Format: CSV with header
- Columns:
  - `event_id` int64
  - `station_code` string/object
  - `p_pick_time` string/object, UTC ISO timestamp or `-1`
  - `s_pick_time` string/object, UTC ISO timestamp or `-1`
  - `p_quality` string/object
  - `s_quality` string/object; missing values may appear as blank/NaN in pandas
  - `weight` float64

Example rows:

```text
event_id,station_code,p_pick_time,s_pick_time,p_quality,s_quality,weight
1,N.313S,2025-09-30T16:09:32.740000Z,2025-09-30T16:09:38.470000Z,IP,S,1.0
1,N.312S,2025-09-30T16:09:32.850000Z,2025-09-30T16:09:38.470000Z,IP,S,1.0
1,N.311S,2025-09-30T16:09:34.220000Z,-1,IP,,1.0
```

Note: This existing `picks.csv` does not include `station_number` or `source_file`, although the requested future workflow asks for both.

#### Existing phase.dat Convention

File:
`data/regional/phase.dat`

- Size: 36,891,502 bytes
- Format: comma-separated project convention, not a HASH-style `#`-prefixed phase file.
- Event header line format appears to be:

```text
origin_time,latitude,longitude,depth_km,magnitude,event_id
```

- Pick line format appears to be:

```text
station_code,p_pick_time,s_pick_time,unknown_or_residual,weight
```

- Missing phase arrivals are represented as `-1`.

Example block start:

```text
2025-09-30T16:09:25.360000Z,38.702667,142.256833,41.340,2.80,1
N.313S,2025-09-30T16:09:32.740000Z,2025-09-30T16:09:38.470000Z,0.000e+00,1.00
N.312S,2025-09-30T16:09:32.850000Z,2025-09-30T16:09:38.470000Z,0.000e+00,1.00
N.314S,2025-09-30T16:09:33.840000Z,2025-09-30T16:09:40.890000Z,0.000e+00,1.00
N.311S,2025-09-30T16:09:34.220000Z,-1,0.000e+00,1.00
```

A second file, `data/regional/phase_new.dat`, also exists and is similar in size: 36,033,481 bytes. Future agents should check project code or provenance before deciding which phase file is canonical.

#### Existing station.sta File

File:
`data/regional/station.sta`

- Size: 16,102 bytes
- Rows: 371 stations
- Format: CSV with header
- Columns:
  - `station_code` string/object
  - `station_number` int64
  - `latitude` float64
  - `longitude` float64
  - `elevation_m` int64
  - `matched` bool

Observed coordinate range:

- Latitude: 36.880833 to 44.118833
- Longitude: 139.245333 to 145.738833
- `matched`: all 371 rows are `True`

Example rows:

```text
station_code,station_number,latitude,longitude,elevation_m,matched
A.ASMS,5572,40.885667,140.874000,-3,True
A.CHOG,5550,41.327167,140.815333,0,True
A.HGTH,5571,40.982833,140.904000,-11,True
A.HRDA,5549,41.448833,140.881000,2,True
```

#### Existing Main Earthquake Table

File:
`data/regional/main_earthquake.csv`

- Size: 184 bytes
- Rows: 3 data rows
- Format: CSV with header
- Columns:
  - `index` string/object
  - `datetime` string/object
  - `lat` float64
  - `lon` float64
  - `dep` float64
  - `mag` float64

Example contents:

```text
index,datetime,lat,lon,dep,mag
M1,2025-11-09 08:03:39.240,39.402,143.507,15.9,6.9
M2,2025-12-08 14:15:10.180,40.968,142.288,53.5,7.5
M3,2026-04-20 07:52:58.060,39.842,143.157,19.4,7.7
```

#### Existing Parse Summary

File:
`data/regional/summary.txt`

Contents summarize the prior parsed dataset:

```text
JMA measure parse summary
raw_events: 178623
kept_events: 29896
kept_station_rows: 529165
p_picks: 437472
s_picks: 344623
lat_range: 38.5000, 42.4998
lon_range: 141.0010, 144.4998
```

This is useful for sanity-checking future regional filtering, but it should not be treated as a substitute for validating newly downloaded raw measure files.

#### Station Reference Text

File:
`data/stations/station.txt`

- Size: 215,646 bytes
- Appears to be a station listing/reference document with Japanese text and tabular station metadata.
- The first visible lines include a date-like reference and section heading for `Hokkaido District`, followed by columns such as `code`, `number`, `Latitude`, `Longitude`, `Height`, `From`, `To`, and `Seismographs`.
- The file may require encoding handling when reading; initial terminal display showed mojibake for Japanese characters.

#### Notes for Future Workflow Implementation

- Existing normalized regional tables use UTC ISO strings ending in `Z`.
- Missing arrivals in existing `picks.csv` and `phase.dat` are represented as `-1`.
- Existing `phase.dat` is comma-separated and block-oriented: one event header line followed by station pick lines; do not replace it with a whitespace-delimited or `#`-prefixed format if preserving project convention.
- The requested future parser should add fields not present in the current regional CSVs, especially `source_file` in both `events.csv` and `picks.csv`, and `station_number` in `picks.csv`.
- The requested raw JMA measure format is fixed-width with 96-byte records excluding line endings; no raw measure files were available in the inspected directory to profile directly.

------------------------------

## phase.dat
**Source path**: `data/regional/phase.dat`
### Summary
The specified `phase.dat` is an existing regional, comma-separated phase-arrival file using the project’s custom block convention rather than a HASH-style or whitespace-delimited format. It contains event header lines followed by station pick lines, with UTC ISO timestamps and `-1` used for missing P or S arrivals.
### Detail
#### File Overview

File inspected:
`<CASE_ROOT>/data/regional/phase.dat`

- Size: 36,891,502 bytes
- Total lines: 559,061
- Empty lines: 0
- Event header lines: 29,896
- Station pick lines: 529,165
- Other/unrecognized line structures: 0
- Format: plain text, comma-separated, block-oriented
- Time convention in this file: UTC ISO strings ending in `Z`
- Missing arrivals: represented as `-1`

#### Block Structure

The file is organized as repeated event blocks:

1. One event header line with 6 comma-separated fields.
2. Multiple station pick lines with 5 comma-separated fields.
3. The next 6-field timestamp line begins the next event block.

No explicit blank line or terminator line separates events in this derived `phase.dat` file.

#### Event Header Line Format

Observed event header lines have 6 fields:

```text
origin_time,latitude,longitude,depth_km,magnitude,event_id
```

Example event headers:

```text
2025-09-30T16:09:25.360000Z,38.702667,142.256833,41.340,2.80,1
2025-09-30T16:16:26.970000Z,39.417500,144.296000,44.700,0.80,2
2025-09-30T16:26:47.040000Z,39.430500,141.581667,14.630,0.10,3
```

Field interpretation:

- `origin_time`: event origin time, UTC ISO format with trailing `Z`
- `latitude`: decimal degrees
- `longitude`: decimal degrees
- `depth_km`: depth in kilometers
- `magnitude`: event magnitude
- `event_id`: integer event identifier matching the project catalog convention

#### Station Pick Line Format

Observed station pick lines have 5 fields:

```text
station_code,p_pick_time,s_pick_time,auxiliary_value,weight
```

Example pick lines:

```text
N.313S,2025-09-30T16:09:32.740000Z,2025-09-30T16:09:38.470000Z,0.000e+00,1.00
N.312S,2025-09-30T16:09:32.850000Z,2025-09-30T16:09:38.470000Z,0.000e+00,1.00
N.314S,2025-09-30T16:09:33.840000Z,2025-09-30T16:09:40.890000Z,0.000e+00,1.00
N.311S,2025-09-30T16:09:34.220000Z,-1,0.000e+00,1.00
N.310S,2025-09-30T16:09:36.260000Z,-1,0.000e+00,1.00
```

Field interpretation:

- `station_code`: station identifier, e.g. `N.313S`, `TU.SN3`, `OFUNAI`
- `p_pick_time`: P arrival timestamp in UTC ISO format, or `-1` if missing
- `s_pick_time`: S arrival timestamp in UTC ISO format, or `-1` if missing
- `auxiliary_value`: consistently formatted like `0.000e+00` in inspected examples; likely a placeholder/residual column in this project convention
- `weight`: numeric pick weight, formatted with two decimals in inspected examples, e.g. `1.00`

#### Counts and Missing-Arrival Markers

Structural counts from the file:

- Event blocks: 29,896
- Pick lines: 529,165
- Pick lines per event block:
  - Minimum observed: 3
  - Maximum observed: 42
  - First five event block pick counts: 35, 13, 16, 12, 26
- Pick lines with missing P arrival marker `-1`: 91,693
- Pick lines with missing S arrival marker `-1`: 184,542

These are descriptive file-structure counts only and should be revalidated by future agents if regenerating the file from raw JMA measure data.

#### Station Code Examples

Example station codes observed near the start of the file:

```text
N.313S
N.312S
N.314S
N.311S
N.310S
N.315S
N.KKWH
E.SOB3
TU.SN3
OFUNAI
```

#### Last Observed Lines

The file ends with station pick lines rather than a separate event terminator:

```text
N.TWWH,-1,2026-05-01T14:59:17.890000Z,0.000e+00,1.00
TENMAB,-1,2026-05-01T14:59:18.210000Z,0.000e+00,1.00
N.ASRH,-1,2026-05-01T14:59:18.780000Z,0.000e+00,1.00
N.KOSH,-1,2026-05-01T14:59:21.380000Z,0.000e+00,1.00
OHASAM,2026-05-01T14:59:06.040000Z,-1,0.000e+00,1.00
```

#### Relevance for Future Workflow Implementation

- Preserve this comma-separated block format when regenerating `phase.dat`; do not replace it with a `#`-prefixed or whitespace-delimited format.
- Use normalized CSV outputs such as `events.csv` and `picks.csv` as the primary structured products, while making `phase.dat` traceable to this convention.
- This derived file does not contain station numbers, pick quality codes, source raw filenames, or raw JMA fixed-width records. Those fields must be obtained from the parsed JMA measure files and normalized tables, not from this `phase.dat` alone.
- Raw JMA event terminator records beginning with `E` are not represented in this derived phase file.

------------------------------

