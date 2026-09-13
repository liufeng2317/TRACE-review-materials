# Data Descriptions
## regional
**Source path**: `<CASE_ROOT>/data/regional`
### Summary
This regional Aomori catalog directory contains a compact relocation-ready event set with 29,896 events, 529,165 station-event pick rows, a 371-station inventory, and a prebuilt phase file (`phase.dat`) that is internally consistent with the station list. The key identifiers needed for future `hypodd_runner` work are already aligned across `events.csv`, `picks.csv`, `phase.dat`, and `station.sta`: event IDs span 1-29896 and all 371 station codes match exactly between the pick and station files.
### Detail
#### Folder Structure
The directory contains a small set of catalog-construction outputs relevant to catalog-only relocation:

- `events.csv` — event catalog with origin metadata and pick counts.
- `picks.csv` — station-level P/S pick table keyed by `event_id`.
- `phase.dat` — primary prebuilt phase input; appears intended as the direct event/pick stream for relocation workflows.
- `station.sta` — station inventory table.
- `summary.txt` — brief catalog statistics summary.
- `main_earthquake.csv` — 3 mainshock reference points for plotting/annotation.
- `phase_new.dat` — extra phase-like file present in the folder but not part of the user-listed primary inputs.

Example paths:
- `<CASE_ROOT>/data/regional/events.csv`
- `<CASE_ROOT>/data/regional/phase.dat`
- `<CASE_ROOT>/data/regional/station.sta`

#### File Inventory and Sizes
Approximate file sizes from directory listing:

- `events.csv` — 2.6 MB
- `picks.csv` — 34 MB
- `phase.dat` — 36 MB
- `phase_new.dat` — 35 MB
- `station.sta` — 16 KB
- `summary.txt` — 180 B
- `main_earthquake.csv` — 184 B

#### Event Catalog: `events.csv`
Format: CSV with header.

Shape and schema:
- Rows: `29896`
- Columns: `8`
- Columns in order:
  - `event_id` (`int64`)
  - `origin_time` (`object`, ISO-like UTC string with trailing `Z`)
  - `latitude` (`float64`)
  - `longitude` (`float64`)
  - `depth_km` (`float64`)
  - `magnitude` (`float64`)
  - `region` (`object`)
  - `npicks` (`int64`)

Key metadata:
- `event_id` is unique for all 29,896 events.
- Event ID range: `1` to `29896`.
- `origin_time` uses UTC-compatible ISO strings such as `2025-09-30T16:09:25.360000Z`.
- Geographic range:
  - latitude: `38.5` to `42.499833`
  - longitude: `141.001` to `144.499833`
- Depth range: `0.0` to `151.0` km.
- Missing values:
  - `magnitude`: `2853` missing
  - all other fields: `0` missing

Example row pattern:
- `1,2025-09-30T16:09:25.360000Z,38.702667,142.256833,41.340,2.80,E OFF MIYAGI PREF,35`

Notes for future agents:
- `npicks` sums exactly to the number of rows in `picks.csv` (`529165`).
- `event_id` appears to be the canonical join key across all primary files.

#### Pick Table: `picks.csv`
Format: CSV with header.

Shape and schema:
- Rows: `529165`
- Columns: `7`
- Columns in order:
  - `event_id` (`int64`)
  - `station_code` (`object`)
  - `p_pick_time` (`object`)
  - `s_pick_time` (`object`)
  - `p_quality` (`object`)
  - `s_quality` (`object`)
  - `weight` (`float64`)

Key metadata:
- Unique `event_id`: `29896` (full coverage of all events)
- Unique `station_code`: `371`
- Station code overlap with `station.sta`: `371 of 371`
- Weight values observed: `0.0` and `1.0` only
- Missing / placeholder behavior:
  - `p_pick_time` has no nulls, but `91693` rows contain the string `-1`
  - `s_pick_time` has no nulls, but `184542` rows contain the string `-1`
  - `p_quality` nulls: `91693`
  - `s_quality` nulls: `184542`

Interpretation of row organization:
- Each row is one event-station association.
- A row may contain both P and S times, or a valid P time with missing S (`-1`), and in some rows P is also represented as `-1` in the CSV.
- The row count equals the total event pick-count sum from `events.csv`, so `npicks` corresponds to station-association rows rather than separate phase records.

Example row pattern:
- `1,N.313S,2025-09-30T16:09:32.740000Z,2025-09-30T16:09:38.470000Z,IP,S,1.00`

#### Phase Input: `phase.dat`
Format: plain text, comma-separated records without a CSV header row.

Observed organization:
- Total lines: `559061`
- Parsed as alternating event header records plus station pick records.
- Event header lines: `29896`
- Pick lines: `529165`

Header record pattern:
- `origin_time,latitude,longitude,depth_km,magnitude,event_id`
- Example:
  - `2025-09-30T16:09:25.360000Z,38.702667,142.256833,41.340,2.80,1`

Pick record pattern:
- `station_code,p_pick_time,s_pick_time,travel_or_residual_placeholder,weight`
- Example:
  - `N.313S,2025-09-30T16:09:32.740000Z,2025-09-30T16:09:38.470000Z,0.000e+00,1.00`

Consistency checks:
- Unique event IDs in header lines: `29896`
- Header event ID range: `1` to `29896`
- Header ID set exactly matches `events.csv` event IDs.
- Unique station codes in pick lines: `371`
- Station code overlap with `station.sta`: `371 of 371`
- Missing S picks are encoded with the literal string `-1` in the third field; count observed: `184542`

Important notes for future agents:
- `phase.dat` is not in classic HypoDD `phase.dat` fixed-format syntax; it is a custom comma-separated event/pick stream. It should therefore be validated against the expected `hypodd_runner` API/parser rather than assumed to be native HypoDD text.
- Despite the custom formatting, its identifiers are internally consistent and preserve original station IDs such as `A.MYGA`, `N.313S`, `TU.KSN`, etc.
- Because station codes already match `station.sta`, this dataset supports preserving original station IDs directly unless a downstream API explicitly requires a transformed `NET.STA` naming convention.

#### Station Inventory: `station.sta`
Format: CSV with header, despite the `.sta` extension.

Shape and schema:
- Rows: `371`
- Columns: `6`
- Columns:
  - `station_code` (`object`)
  - `station_number` (`int64`)
  - `latitude` (`float64`)
  - `longitude` (`float64`)
  - `elevation_m` (`int64`)
  - `matched` (`bool`)

Key metadata:
- All `371` station codes are unique.
- All `matched` values are `True`.
- Geographic range:
  - latitude: `36.880833` to `44.118833`
  - longitude: `139.245333` to `145.738833`
- No missing values detected.

Naming convention:
- Station identifiers already include network-like prefixes in the code itself, e.g. `A.ASMS`, `N.313S`, `TU.KSN`.
- This is important for relocation input generation because the existing code strings already have a dotted form and match the pick/phase files exactly.

Example row pattern:
- `A.ASMS,5572,40.885667,140.874000,-3,True`

#### Summary File: `summary.txt`
Format: short plain-text key-value summary.

Content summary:
- `raw_events: 178623`
- `kept_events: 29896`
- `kept_station_rows: 529165`
- `p_picks: 437472`
- `s_picks: 344623`
- `lat_range: 38.5000, 42.4998`
- `lon_range: 141.0010, 144.4998`

Usefulness:
- Provides a quick sanity check on catalog size and spatial domain.
- `kept_events` and `kept_station_rows` match the row counts observed in `events.csv` and `picks.csv`.

#### Main Earthquake Reference: `main_earthquake.csv`
Format: CSV with header.

Shape and schema:
- Rows: `3`
- Columns: `6`
- Columns:
  - `index`
  - `datetime`
  - `lat`
  - `lon`
  - `dep`
  - `mag`

Observed content:
- 3 labeled entries: `M1`, `M2`, `M3`
- Example timestamps use a space-separated datetime format rather than ISO `T...Z`.

Likely role:
- Plot annotation/reference only; not a core relocation input.

#### Cross-File Identifier Consistency
High-priority consistency findings for future relocation agents:

- `events.csv:event_id` uniquely spans `1..29896`.
- `picks.csv:event_id` covers the exact same 29,896 events.
- `phase.dat` header event IDs match `events.csv` exactly.
- `station.sta:station_code` matches all station codes found in both `picks.csv` and `phase.dat`.
- Existing station IDs should be preserved by default because the input files are already aligned.

#### Data Access / Loading Notes
Recommended loading patterns:

- `events.csv`, `picks.csv`, `station.sta`, and `main_earthquake.csv` can be loaded with standard CSV readers (`pandas.read_csv`).
- `phase.dat` should be read as line-based text and parsed by record type:
  - 6-field lines beginning with an ISO timestamp are event headers.
  - 5-field lines beginning with a station code are pick rows.
- Placeholder missing phase times are encoded as the string `-1`, not as blank/null.

#### Practical Notes for Future `hypodd_runner` Preparation
Relevant only as data-profile guidance, not parameter selection:

- Catalog scale is moderate-to-large for a single regional run: `29,896` events and `529,165` event-station rows.
- The prebuilt `phase.dat` is structurally complete and should be checked first before any reconstruction from `picks.csv`.
- Since station IDs already match exactly between `phase.dat` and `station.sta`, any renaming scheme must be applied consistently everywhere only if an API requires it.
- Event times in `events.csv` and header times in `phase.dat` are already UTC-compatible ISO strings suitable for identity-preserving workflows.

------------------------------

## events.csv
**Source path**: `<CASE_ROOT>/data/regional/events.csv`
### Summary
`events.csv` is the primary event catalog table for the regional Aomori dataset, containing 29,896 events with unique integer `event_id` values and UTC-compatible origin times. It provides the core origin metadata needed to link to `picks.csv` and `phase.dat`, including hypocenter coordinates, depth, magnitude, region label, and per-event pick counts.
### Detail
#### File Overview
- Path: `<CASE_ROOT>/data/regional/events.csv`
- Format: CSV with header row
- Approximate size: `2.6 MB`
- Rows: `29,896`
- Columns: `8`

This file is the event-level catalog for the regional dataset and appears to be the canonical source of event metadata. It is suitable as the master event table for joining with station-pick information and validating event identity preservation in downstream relocation workflows.

#### Schema
Columns in order:

1. `event_id` — `int64`
2. `origin_time` — `object` (string)
3. `latitude` — `float64`
4. `longitude` — `float64`
5. `depth_km` — `float64`
6. `magnitude` — `float64`
7. `region` — `object` (string)
8. `npicks` — `int64`

#### Column Meanings and Relevance
- `event_id`
  - Unique integer event identifier.
  - Observed range: `1` to `29896`.
  - This is the key field for linking the event catalog to pick/phase data.
  - Future agents should preserve this field exactly for relocation accounting and result merging.

- `origin_time`
  - UTC-compatible ISO timestamp strings with trailing `Z`.
  - Example: `2025-09-30T16:09:25.360000Z`
  - This format is already suitable for workflows requiring stable event identity and machine-readable origin times.

- `latitude`, `longitude`
  - Initial hypocenter epicentral coordinates in decimal degrees.
  - Observed ranges:
    - latitude: `38.5` to `42.499833`
    - longitude: `141.001` to `144.499833`
  - These define the regional study window represented in the catalog.

- `depth_km`
  - Event depth in kilometers.
  - Observed range: `0.0` to `151.0` km.

- `magnitude`
  - Event magnitude as floating-point values.
  - Missing values present; see completeness section below.

- `region`
  - Textual region description.
  - Example values include:
    - `E OFF MIYAGI PREF`
    - `FAR E OFF SANRIKU`
    - `SOUTHERN IWATE PREF`
  - Useful for labeling, filtering, or quality-control summaries, but not a join key.

- `npicks`
  - Integer count of associated pick/station rows per event.
  - This is useful for quick event-level diagnostics before relocation.

#### Completeness / Missing Values
Missing-value counts:
- `event_id`: `0`
- `origin_time`: `0`
- `latitude`: `0`
- `longitude`: `0`
- `depth_km`: `0`
- `magnitude`: `2853`
- `region`: `0`
- `npicks`: `0`

Implications for future agents:
- All events have complete origin coordinates, depth, time, region, and pick-count metadata.
- `magnitude` is optional/incomplete for a subset of events and should not be assumed present for all rows.

#### Identifier and Linking Properties
This file is structurally well suited as the master event table because:
- `event_id` is unique across all `29,896` rows.
- The event ID set spans the full catalog continuously from `1` to `29896`.
- In the broader regional dataset inspection, this same event ID set matched the header event IDs in `phase.dat` and the `event_id` values in `picks.csv`.

For future workflows, this means:
- `event_id` should be treated as the canonical join key.
- Event accounting can be done directly against this table without inventing surrogate identifiers.
- Event identity preservation should be straightforward if downstream outputs retain these IDs or provide a verified mapping back to them.

#### Spatial and Catalog Extent
Observed numeric ranges:
- Latitude: `38.5` to `42.499833`
- Longitude: `141.001` to `144.499833`
- Depth: `0.0` to `151.0` km

These ranges indicate a regional offshore/onshore northeastern Japan catalog centered on the Aomori–Sanriku–northern Tohoku area. This is useful context for future agents selecting region-aware processing options, but no scientific interpretation is performed here.

#### Example Rows
First few records follow this pattern:

- `1,2025-09-30T16:09:25.360000Z,38.702667,142.256833,41.340,2.80,E OFF MIYAGI PREF,35`
- `2,2025-09-30T16:16:26.970000Z,39.417500,144.296000,44.700,0.80,FAR E OFF SANRIKU,13`
- `3,2025-09-30T16:26:47.040000Z,39.430500,141.581667,14.630,0.10,SOUTHERN IWATE PREF,16`

#### Usage Notes for Future Agents
- Load with a standard CSV reader such as `pandas.read_csv`.
- Treat `origin_time` as string or parse to timezone-aware datetime if needed; preserve the original ISO representation when round-tripping metadata.
- Preserve `event_id` exactly when building any relocation input/output mappings.
- Do not assume `magnitude` is complete.
- `npicks` can be used as a quick event-level data-density metric and was previously confirmed to sum to the total number of rows in `picks.csv` for the full directory dataset.

#### Minimal Access Pattern Example
Typical columns future agents will likely need first:
- `event_id`
- `origin_time`
- `latitude`
- `longitude`
- `depth_km`
- `npicks`

These are the essential event metadata fields for matching, initialization, bookkeeping, and plotting against relocation results.

------------------------------

## picks.csv
**Source path**: `<CASE_ROOT>/data/regional/picks.csv`
### Summary
`picks.csv` is the event-station pick table for the regional Aomori catalog, containing 529,165 rows across all 29,896 events and 371 unique stations. It preserves the same station codes used in `station.sta` and provides per-row P/S pick times, optional phase-quality labels, and a simple weight field, making it the main fallback source if `phase.dat` ever needs to be cross-checked or rebuilt.
### Detail
#### File Overview
- Path: `<CASE_ROOT>/data/regional/picks.csv`
- Format: CSV with header row
- Approximate size: `34 MB`
- Rows: `529,165`
- Columns: `7`

This file stores station-associated arrival information keyed by `event_id`. It is structured as one row per event-station association rather than one row per individual phase, with separate P and S time columns on the same row.

#### Schema
Columns in order:

1. `event_id` — `int64`
2. `station_code` — `object`
3. `p_pick_time` — `object`
4. `s_pick_time` — `object`
5. `p_quality` — `object`
6. `s_quality` — `object`
7. `weight` — `float64`

#### Row Organization
Each row represents a single `event_id` + `station_code` pair. The row may include:
- both a P and S arrival time,
- only a P arrival with missing S,
- or placeholder values encoded as `-1` for missing picks.

This is important for downstream agents because the row count is not the same as the total count of individual phases. Instead, it is the count of event-station associations.

#### Key Metadata
- Total rows: `529,165`
- Unique events (`event_id`): `29,896`
- Event ID range: `1` to `29896`
- Unique stations (`station_code`): `371`
- Station overlap with `station.sta`: `371 of 371`

Cross-file consistency relevant for future relocation work:
- `event_id` coverage matches the event catalog (`events.csv`) across all events.
- `station_code` values match the station inventory exactly.
- The same station naming convention also matches the prebuilt `phase.dat` station entries.

#### Column Details
- `event_id`
  - Integer identifier linking each pick row to an event in `events.csv`.
  - Suitable as the primary join key for event-level bookkeeping.

- `station_code`
  - String station identifier.
  - Examples observed elsewhere in the dataset include codes such as `N.313S`, `A.MYGA`, `TU.KSN`.
  - Existing station IDs already include a dotted network-like prefix and should be preserved unless a downstream API explicitly requires remapping.

- `p_pick_time`
  - P arrival time as string.
  - Uses UTC-compatible ISO strings with trailing `Z` when present.
  - Missing picks are represented by the literal string `-1`, not by null.

- `s_pick_time`
  - S arrival time as string.
  - Uses UTC-compatible ISO strings with trailing `Z` when present.
  - Missing S picks are also represented by the string `-1`.

- `p_quality`
  - Optional quality code for the P arrival.
  - Example observed: `IP`
  - Null when the corresponding P pick is absent or not labeled.

- `s_quality`
  - Optional quality code for the S arrival.
  - Example observed: `S`
  - Null when the corresponding S pick is absent or not labeled.

- `weight`
  - Numeric row weight.
  - Observed unique values: `0.0` and `1.0` only.
  - This is a simple field and not a multi-level weight scale in the current file.

#### Completeness / Missingness
Pandas null counts:
- `event_id`: `0`
- `station_code`: `0`
- `p_pick_time`: `0`
- `s_pick_time`: `0`
- `p_quality`: `91,693`
- `s_quality`: `184,542`
- `weight`: `0`

Important distinction:
- Although `p_pick_time` and `s_pick_time` have no CSV nulls, missing picks are encoded as the string `-1`.
- Observed placeholder counts:
  - rows with `p_pick_time == '-1'`: `91,693`
  - rows with `s_pick_time == '-1'`: `184,542`

So future agents should not use only `isna()` to detect missing arrivals; they must also treat `-1` as a missing-time sentinel.

#### Example Row Pattern
Example rows from the start of the file:

- `1,N.313S,2025-09-30T16:09:32.740000Z,2025-09-30T16:09:38.470000Z,IP,S,1.00`
- `1,N.312S,2025-09-30T16:09:32.850000Z,2025-09-30T16:09:38.470000Z,IP,S,1.00`
- `1,N.314S,2025-09-30T16:09:33.840000Z,2025-09-30T16:09:40.890000Z,IP,S,1.00`
- `1,N.311S,2025-09-30T16:09:34.220000Z,-1,IP,,1.00`

This confirms the mixed presence/absence pattern for S arrivals on otherwise valid event-station rows.

#### Relationship to Other Files
- With `events.csv`
  - `event_id` links each pick row to a unique event.
  - The sum of `events.csv[npicks]` was previously confirmed to equal the total number of rows in `picks.csv` (`529,165`).
  - This strongly suggests that `npicks` in `events.csv` refers to the number of event-station association rows represented here.

- With `station.sta`
  - All `371` station codes in `picks.csv` are present in `station.sta`.
  - No station renaming appears necessary for internal consistency at the data level.

- With `phase.dat`
  - `phase.dat` contains the same event IDs and station codes and appears to encode the same event/pick content in a different line-based text format.
  - Because the user indicated `phase.dat` should be preferred when valid, `picks.csv` is best viewed as a structured tabular cross-check and reconstruction source rather than the default primary input.

#### Access / Loading Notes
Recommended loading pattern:
- Standard CSV reader, e.g. `pandas.read_csv(...)`
- Treat time columns as strings initially to preserve exact formatting and sentinel `-1` values.
- If parsing datetimes, convert only entries that are not `-1`.

Fields likely most important for future agents:
- `event_id`
- `station_code`
- `p_pick_time`
- `s_pick_time`
- `weight`
- optionally `p_quality`, `s_quality`

#### Practical Caveats for Future Agents
- Do not interpret one row as one phase observation; a row can contain up to two phase times.
- Preserve original station codes exactly by default because they already match the station inventory and the phase file.
- Treat `-1` as the missing-arrival sentinel in both time columns.
- Preserve `event_id` exactly if constructing any derived relocation inputs or verifying mappings back from external outputs.

------------------------------

## phase.dat
**Source path**: `<CASE_ROOT>/data/regional/phase.dat`
### Summary
`phase.dat` is a prebuilt text phase file containing 29,896 event header records followed by 529,165 station-pick records, for a total of 559,061 non-empty lines. Its event IDs and station codes are fully consistent with `events.csv` and `station.sta`, so it is structurally the most relevant primary phase source to validate first for future `hypodd_runner` workflows.
### Detail
#### File Overview
- Path: `<CASE_ROOT>/data/regional/phase.dat`
- Format: plain text, comma-separated records, no header row
- Approximate size: `36 MB`
- Total non-empty lines: `559,061`

This file is organized as an event-by-event stream rather than as a rectangular table. It alternates one event-level header record with multiple station pick records for that event.

#### Record Structure
The file contains two record types.

1. **Event header records**
   - Count: `29,896`
   - Pattern: `origin_time,latitude,longitude,depth_km,magnitude,event_id`
   - Example:
     - `2025-09-30T16:09:25.360000Z,38.702667,142.256833,41.340,2.80,1`

2. **Station pick records**
   - Count: `529,165`
   - Pattern: `station_code,p_pick_time,s_pick_time,placeholder_value,weight`
   - Example:
     - `N.313S,2025-09-30T16:09:32.740000Z,2025-09-30T16:09:38.470000Z,0.000e+00,1.00`

The observed sequence is therefore:
- one event header line,
- then all station-pick lines belonging to that event,
- then the next event header line,
- and so on.

#### Event Header Metadata
Parsed event-header properties:
- Number of header records: `29,896`
- Unique header event IDs: `29,896`
- Event ID range: `1` to `29896`
- Header event ID set matches `events.csv` exactly.

Header field meanings:
- `origin_time` — UTC-compatible ISO timestamp string with trailing `Z`
- `latitude` — decimal degrees
- `longitude` — decimal degrees
- `depth_km` — depth in kilometers
- `magnitude` — event magnitude value as text/numeric token
- `event_id` — integer event identifier

This means `phase.dat` already preserves the same event identity basis as the catalog table.

#### Station Pick Metadata
Parsed pick-line properties:
- Number of pick records: `529,165`
- Unique station codes in picks: `371`
- Station code overlap with `station.sta`: `371 of 371`

Pick field meanings:
- `station_code` — string station identifier
- `p_pick_time` — P arrival time or missing-value sentinel
- `s_pick_time` — S arrival time or missing-value sentinel
- `placeholder_value` — observed as `0.000e+00` in sampled lines
- `weight` — numeric weight, observed as `1.00` in sampled lines

Observed missingness convention:
- Missing S arrivals are encoded as the literal string `-1` in the third field.
- Count of pick lines with `s_pick_time == '-1'`: `184,542`

Because the file is line-based and not a formal CSV table with typed nulls, future agents should treat `-1` as a sentinel during parsing rather than expecting blanks or NA values.

#### Naming Conventions and Cross-File Consistency
Station-code behavior is especially important for downstream relocation preparation:
- Station codes in `phase.dat` are already in the same identifier form used in `station.sta`.
- Observed examples include codes such as:
  - `A.ASMS`
  - `A.MYGA`
  - `N.313S`
  - `TU.KSN`
- Unique station count in `phase.dat`: `371`
- Unique station count in `station.sta`: `371`
- Exact overlap: `371 of 371`

Implication for future agents:
- The original station IDs are already internally consistent and should be preserved by default.
- Any station renaming or prefixing should only be applied if a downstream parser/API explicitly requires it, and then must be applied consistently to both phase and station inputs.

#### Relationship to Other Files
- With `events.csv`
  - The event header ID set matches the event catalog exactly.
  - Header times are UTC-compatible ISO strings consistent with the event table.
  - Header metadata duplicates the essential event-origin information in a line-oriented format.

- With `picks.csv`
  - Pick-line count equals the row count of `picks.csv`: `529,165`.
  - The same station-code universe is used.
  - The file appears to encode the same event/station association content in a text stream rather than as a rectangular CSV table.

- With `station.sta`
  - All station codes found in the phase picks are present in the station inventory.
  - No identifier mismatch was found during inspection.

#### Format Caution for Future Agents
This file is named `phase.dat`, but it does **not** resemble the classic fixed-format HypoDD `phase.dat` syntax with hash-prefixed event headers. Instead, it is a custom comma-separated event/pick stream.

That distinction matters because future agents should:
- validate it against the exact parser expected by the selected `hypodd_runner` API,
- not assume that the `.dat` extension implies native HypoDD-ready formatting,
- and preserve the original lines/IDs during validation.

In other words, the file is structurally complete and internally consistent, but its compatibility with a specific relocation API depends on how that API expects phase input to be formatted.

#### Example Snippet Pattern
The first event block follows this style:
- event header line with event origin and ID
- multiple pick lines such as:
  - `N.313S,...`
  - `N.312S,...`
  - `N.314S,...`
  - `N.311S,...,-1,...`
  - `A.MYGA,...`
  - `TU.KSN,...`

This confirms that each event block can mix stations from multiple code families and that missing S picks are embedded inline using `-1`.

#### Practical Parsing Notes
Recommended parsing strategy:
- Read line-by-line.
- Split on commas.
- Classify records by pattern:
  - if there are 6 fields and the first field looks like an ISO timestamp, treat as an event header;
  - otherwise treat as a station-pick record.
- Preserve string values exactly for:
  - `event_id`
  - station codes
  - time strings
- Convert `-1` in phase-time fields to a missing marker only after classification.

#### Key Counts for Workflow Bookkeeping
Useful catalog-scale counts already extractable from this file:
- Event headers: `29,896`
- Pick rows: `529,165`
- Total lines: `559,061`
- Unique events: `29,896`
- Unique stations: `371`

These counts match the broader directory-level metadata and make this file suitable as a primary integrity-check target before any fallback reconstruction from `picks.csv` is considered.

------------------------------

## station.sta
**Source path**: `<CASE_ROOT>/data/regional/station.sta`
### Summary
`station.sta` is a CSV-formatted station inventory containing 371 unique stations with coordinates, elevation, numeric station codes, and a boolean `matched` flag. Its `station_code` values match all stations found in both `picks.csv` and `phase.dat`, so the existing identifiers are already internally consistent for future relocation input preparation.
### Detail
#### File Overview
- Path: `<CASE_ROOT>/data/regional/station.sta`
- Format: CSV with header row despite the `.sta` extension
- Approximate size: `16 KB`
- Rows: `371`
- Columns: `6`

This file is the station inventory for the regional catalog. It is small, clean, and fully populated, making it the authoritative source for station metadata in the dataset.

#### Schema
Columns in order:

1. `station_code` — `object`
2. `station_number` — `int64`
3. `latitude` — `float64`
4. `longitude` — `float64`
5. `elevation_m` — `int64`
6. `matched` — `bool`

#### Column Details
- `station_code`
  - Primary station identifier used across the dataset.
  - Unique for all 371 rows.
  - Examples include codes such as `A.ASMS`, `A.MYGA`, `N.313S`, `TU.KSN` in the broader dataset.
  - These codes already include a dotted network-like form and should generally be preserved as-is unless a downstream API requires remapping.

- `station_number`
  - Integer numeric station identifier.
  - Appears to be an auxiliary station reference code rather than the main join key.

- `latitude`, `longitude`
  - Station coordinates in decimal degrees.
  - Observed ranges:
    - latitude: `36.880833` to `44.118833`
    - longitude: `139.245333` to `145.738833`

- `elevation_m`
  - Station elevation in meters.
  - Integer-valued.
  - Includes negative values for some stations, indicating some sites are below sea level reference.

- `matched`
  - Boolean station-status field.
  - All rows are `True` in this file.

#### Data Quality / Completeness
Null counts:
- `station_code`: `0`
- `station_number`: `0`
- `latitude`: `0`
- `longitude`: `0`
- `elevation_m`: `0`
- `matched`: `0`

Additional checks:
- Unique station codes: `371`
- `matched` value counts: `{True: 371}`

This file is fully populated and does not show missing metadata in the inspected fields.

#### Naming Convention and Cross-File Consistency
The most important feature for future agents is the station naming consistency:
- `station_code` is the key identifier used in the inventory.
- In prior cross-file checks for the same regional dataset, all 371 station codes in this file were found in `picks.csv` and `phase.dat`.
- Overlap with `picks.csv`: `371 of 371`
- Overlap with `phase.dat`: `371 of 371`

Implication:
- The current station IDs are already internally consistent across event-phase and station metadata files.
- A synthetic prefix should not be added unless a specific downstream parser/API explicitly requires a different naming convention.
- If any remapping is ever required, this file should be updated consistently alongside the phase/pick inputs.

#### Example Rows
Representative row pattern:
- `A.ASMS,5572,40.885667,140.874000,-3,True`
- `A.CHOG,5550,41.327167,140.815333,0,True`
- `A.HGTZ,5571,40.982833,140.904000,-11,True`

This shows the file is conventional CSV and easy to load directly with standard tabular tools.

#### Practical Access Notes
Recommended loading:
- Use `pandas.read_csv(...)` directly.
- Treat `station_code` as the canonical station key.
- Preserve the exact string representation of `station_code` when building relocation inputs or validating station-phase consistency.

Fields most relevant for downstream agents:
- `station_code`
- `latitude`
- `longitude`
- `elevation_m`

`station_number` may be useful as an auxiliary reference, but `station_code` is the field that aligns with the pick/phase files.

#### Spatial Coverage Context
The station inventory spans a somewhat broader area than the event epicentral bounds seen in the event catalog, which is expected for a regional network. This makes the file suitable for plotting, station-event geometry checks, and validating whether a chosen relocation input set preserves the original station namespace.

#### File Interpretation Note
Although the file extension is `.sta`, it is not a whitespace-fixed legacy station file in the inspected dataset; it is a normal comma-separated table with a header row. Future agents should therefore parse it as CSV first rather than assuming a legacy station text layout.

------------------------------

## summary.txt
**Source path**: `<CASE_ROOT>/data/regional/summary.txt`
### Summary
`summary.txt` is a very small plain-text diagnostic file that provides top-level counts and spatial bounds for the regional catalog extraction. It is useful as a quick integrity check because its reported event, pick-row, and geographic-range values agree with the main catalog files inspected in the same directory.
### Detail
#### File Overview
- Path: `<CASE_ROOT>/data/regional/summary.txt`
- Format: plain text
- Approximate size: `180 bytes`
- Structure: short key-value summary, one item per line after a title line

This file is not a table of observations; it is a compact catalog summary intended for quick inspection. It is best used as a high-level consistency check before loading the larger CSV/text inputs.

#### Content Structure
The file begins with a title line:
- `JMA measure parse summary`

It then contains simple `key: value` lines:
- `raw_events: 178623`
- `kept_events: 29896`
- `kept_station_rows: 529165`
- `p_picks: 437472`
- `s_picks: 344623`
- `lat_range: 38.5000, 42.4998`
- `lon_range: 141.0010, 144.4998`

#### Meaning of Reported Fields
- `raw_events`
  - Total events before filtering or selection in the upstream parse step.
  - Value: `178623`

- `kept_events`
  - Number of events retained in the regional dataset.
  - Value: `29896`
  - This matches the row count of `events.csv`.

- `kept_station_rows`
  - Number of retained event-station association rows.
  - Value: `529165`
  - This matches the row count of `picks.csv` and the number of pick lines in `phase.dat`.

- `p_picks`
  - Count of P picks in the retained dataset summary.
  - Value: `437472`

- `s_picks`
  - Count of S picks in the retained dataset summary.
  - Value: `344623`

- `lat_range`
  - Latitude extent of retained events.
  - Value: `38.5000, 42.4998`

- `lon_range`
  - Longitude extent of retained events.
  - Value: `141.0010, 144.4998`

#### Cross-File Consistency Notes
This summary file aligns with the larger inputs previously inspected in the same regional directory:
- `kept_events = 29896` matches `events.csv` row count.
- `kept_station_rows = 529165` matches `picks.csv` row count.
- `lat_range` and `lon_range` agree with the observed spatial ranges in `events.csv`.

That makes this file useful for a fast preflight check before running heavier parsing or relocation input validation.

#### Practical Usage for Future Agents
Recommended uses:
- Verify that the directory contents correspond to the expected regional extract.
- Confirm expected scale before loading large files.
- Compare summary counts against parsed results from `events.csv`, `picks.csv`, or `phase.dat`.

Not recommended as a primary data source for workflow construction because:
- it contains only aggregate metadata,
- it does not include event IDs, station codes, or phase timings,
- and it is not sufficient on its own for relocation input generation.

#### Parsing Notes
- The file can be read as plain text.
- A simple line-based parser splitting on the first colon is sufficient.
- `lat_range` and `lon_range` values are stored as comma-separated numeric pairs in a single text field.

#### Example Access Pattern
Future agents can treat this file as a lightweight metadata manifest containing:
- catalog scale (`raw_events`, `kept_events`, `kept_station_rows`)
- phase abundance (`p_picks`, `s_picks`)
- event spatial extent (`lat_range`, `lon_range`)

It is therefore most helpful as a diagnostic companion to the full catalog files rather than as a standalone dataset.

------------------------------

## main_earthquake.csv
**Source path**: `<CASE_ROOT>/data/regional/main_earthquake.csv`
### Summary
`main_earthquake.csv` is a small reference table containing 3 manually labeled main earthquakes intended for plotting or annotation rather than core relocation input. It stores simple event labels, origin times, coordinates, depth, and magnitude in a compact CSV format.
### Detail
#### File Overview
- Path: `<CASE_ROOT>/data/regional/main_earthquake.csv`
- Format: CSV with header row
- Approximate size: `184 bytes`
- Rows: `3`
- Columns: `6`

This file is a lightweight reference dataset. It is best treated as an auxiliary plotting/annotation layer rather than as a primary source for relocation processing.

#### Schema
Columns in order:

1. `index` — `object`
2. `datetime` — `object`
3. `lat` — `float64`
4. `lon` — `float64`
5. `dep` — `float64`
6. `mag` — `float64`

#### Column Details
- `index`
  - Short label for each main earthquake.
  - Observed values: `M1`, `M2`, `M3`
  - These are labels, not the same event IDs used in `events.csv`.

- `datetime`
  - Origin time as a string.
  - Example format: `2025-11-09 08:03:39.240`
  - Note: this is a space-separated datetime string and does not include the `T...Z` ISO style used in `events.csv` and `phase.dat`.

- `lat`, `lon`
  - Epicentral coordinates in decimal degrees.

- `dep`
  - Depth in kilometers.

- `mag`
  - Magnitude as a floating-point value.

#### Data Quality / Completeness
Null counts:
- `index`: `0`
- `datetime`: `0`
- `lat`: `0`
- `lon`: `0`
- `dep`: `0`
- `mag`: `0`

The file is complete with no missing values in the inspected fields.

#### Observed Content
All rows:
- `M1,2025-11-09 08:03:39.240,39.402,143.507,15.9,6.9`
- `M2,2025-12-08 14:15:10.180,40.968,142.288,53.5,7.5`
- `M3,2026-04-20 07:52:58.060,39.842,143.157,19.4,7.7`

#### Practical Interpretation for Future Agents
Most likely usage:
- map annotation,
- highlighting major earthquakes in relocation figures,
- adding reference markers in lon-lat and depth sections.

Less suitable for:
- event-identity joins with `events.csv`, because it does not contain `event_id`.
- direct relocation bookkeeping, because it is a tiny manually curated reference list rather than a full catalog.

#### Formatting Notes
- The file uses standard CSV formatting and can be loaded directly with `pandas.read_csv(...)`.
- If time normalization is needed for plotting or matching, `datetime` may need conversion because it is not already in the UTC-style `YYYY-MM-DDTHH:MM:SS.ssssssZ` format used elsewhere in the dataset.
- Field names differ from `events.csv` conventions:
  - `lat` vs `latitude`
  - `lon` vs `longitude`
  - `dep` vs `depth_km`
  - `datetime` vs `origin_time`

Future agents should therefore rename columns explicitly if combining this file with the main catalog for plotting.

#### Minimal Useful Fields
For figure overlays, the most relevant fields are:
- `index`
- `datetime`
- `lat`
- `lon`
- `dep`
- `mag`

These are sufficient to plot red mainshock reference points and optional text labels on map and cross-section views.

------------------------------

