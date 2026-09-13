# Data Descriptions
## TRACE_ridgecrest_relocated.csv
**Source path**: `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/TRACE_ridgecrest_relocated.csv`
### Summary
This Ridgecrest data folder contains two CSV earthquake catalogs plus a small two-row mainshock reference file. The interevent catalog is a relocated event list with 84,474 events and the exact fields needed for fixed-window spatial/temporal subsetting (`event_time, latitude, longitude, depth_km, magnitude`), while the background catalog is a larger-metadata CSV with 1,536 events that includes remappable equivalents for those same core fields.
### Detail
#### Folder Structure
- Root inspected: `<REPO_ROOT>/examples/ridgecrest/data`
- Relevant subfolders:
  - `catalog_TRACE/`
    - `TRACE_ridgecrest_relocated.csv` — primary interevent relocated catalog
    - `main_shock_events.csv` — two mainshock hypocenters/times used as spatial centers and temporal bounds
    - `visualize.ipynb` — notebook present, not required for loading the catalogs
  - `catalog_longterm/`
    - `catalog_2year_background_before_64.csv` — longer-term regional background catalog

#### Primary Files
1. **Interevent catalog**  
   Path: `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/TRACE_ridgecrest_relocated.csv`
2. **Background catalog**  
   Path: `<REPO_ROOT>/examples/ridgecrest/data/catalog_longterm/catalog_2year_background_before_64.csv`
3. **Main shocks**  
   Path: `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/main_shock_events.csv`

#### Interevent Catalog Metadata
- Format: CSV
- Size: 7,662,814 bytes (~7.4 MB)
- Shape: **84,474 rows × 5 columns**
- Columns:
  - `event_time` (`object`; parseable UTC timestamp strings with timezone offset)
  - `latitude` (`float64`)
  - `longitude` (`float64`)
  - `depth_km` (`float64`)
  - `magnitude` (`float64`)
- Missing values: none in any of the 5 columns
- Time coverage:
  - Min: `2019-07-04 00:56:37.590000+00:00`
  - Max: `2019-07-25 23:59:29.320000+00:00`
- Coordinate/value ranges:
  - Latitude: `35.27090479518505` to `36.311627795185046`
  - Longitude: `-118.06486693463452` to `-116.9939567617556`
  - Depth (km): `0.367625` to `26.3518736`
  - Magnitude: `-0.85` to `7.1`
- Example row pattern:
  - `2019-07-04 00:56:37.590000+00:00, 36.088524, -117.827908, 9.701632, 0.66`
- Notes relevant for future loading:
  - This file already matches the user-requested canonical schema.
  - Timestamps are stored as strings but parse cleanly with `pandas.to_datetime(..., utc=True)`.
  - Magnitudes are mostly recorded to 2 decimal places, with a few floating-point string artifacts showing long decimal expansions; downstream code should infer magnitude bin size carefully rather than assuming every record is perfectly rounded.

#### Background Catalog Metadata
- Format: CSV
- Size: 277,760 bytes (~272 KB)
- Shape: **1,536 rows × 30 columns**
- Core columns relevant to b-value workflows:
  - `datetime` → maps to `event_time`
  - `latR` → maps to `latitude`
  - `lonR` → maps to `longitude`
  - `depR` → maps to `depth_km`
  - `mag` → maps to `magnitude`
- Full column list:
  - `yr, mon, day, hr, min, sec, eID, latR, lonR, depR, mag, qID, cID, nbranch, qnpair, qndiffP, qndiffS, rmsP, rmsS, eh, ez, et, latC, lonC, depC, evt_type, mag_type, growclust_solution, relocation_box, datetime`
- Dtypes:
  - Mostly numeric metadata with several string/object columns (`evt_type`, `mag_type`, `growclust_solution`, `relocation_box`, `datetime`)
- Missingness:
  - No missing values in the core mapped columns `datetime, latR, lonR, depR, mag`
  - Some auxiliary relocation/quality columns have nulls, especially `cID, nbranch, qnpair, qndiffP, qndiffS, rmsP, latC, lonC, depC, mag_type, relocation_box`
- Time coverage:
  - Min: `2019-01-04 07:13:44.847000+00:00`
  - Max: `2019-07-04 17:27:35.109000+00:00`
- Coordinate/value ranges for mapped fields:
  - Latitude (`latR`): `35.00333` to `36.4985`
  - Longitude (`lonR`): `-118.49638` to `-117.00607`
  - Depth (`depR`, km): `-0.55` to `17.3`
  - Magnitude (`mag`): `-0.74` to `3.98`
- Example row structure:
  - Contains both decomposed date/time fields (`yr, mon, day, hr, min, sec`) and a full timestamp string in `datetime`
- Notes relevant for future loading:
  - For consistency with the interevent catalog, future agents should rename the mapped fields to `event_time, latitude, longitude, depth_km, magnitude` before combining summary logic.
  - The file includes additional relocation/QC attributes that may help with provenance filtering, but they are not required for the requested fixed-window b-value subsets.

#### Mainshock Reference File Metadata
- Format: CSV
- Size: 176 bytes
- Shape: **2 rows × 5 columns**
- Columns:
  - `event_time`
  - `latitude`
  - `longitude`
  - `depth_km`
  - `magnitude`
- Missing values: none
- Rows:
  - `2019-07-04 17:33:49.040000+00:00, 35.70421, -117.49392, 11.864, 6.4`
  - `2019-07-06 03:19:53.040000+00:00, 35.77623, -117.59286, 1.986, 7.1`
- Notes relevant for future loading:
  - This file provides the two hypocentral centers for Mw 6.4 and Mw 7.1 local-core masks.
  - It also defines the interevent start/end bounds requested by the user.

#### Naming and Organization Conventions
- Catalogs are organized by purpose rather than by date hierarchy:
  - `catalog_TRACE/` for the relocated Ridgecrest sequence/interevent products
  - `catalog_longterm/` for the long-term background reference
- File naming is descriptive and stable:
  - `TRACE_ridgecrest_relocated.csv` indicates relocated event catalog for the sequence
  - `catalog_2year_background_before_64.csv` indicates a pre-Mw-6.4 regional background window
  - `main_shock_events.csv` indicates a small lookup/reference table

#### Schema Compatibility for Future Agents
- Directly compatible schema:
  - `TRACE_ridgecrest_relocated.csv`
  - `main_shock_events.csv`
- Requires column remapping:
  - `catalog_2year_background_before_64.csv`
    - `datetime -> event_time`
    - `latR -> latitude`
    - `lonR -> longitude`
    - `depR -> depth_km`
    - `mag -> magnitude`
- All three files can be read with `pandas.read_csv` without special parsing options; timestamps should then be converted with `utc=True`.

#### Data Quality / Parsing Notes
- Interevent and mainshock files have no nulls in required columns.
- Background file also has no nulls in the requested mapped fields, despite nulls in several auxiliary metadata columns.
- Magnitude precision appears mixed but predominantly hundredths; a few interevent records show long decimal string representations likely caused by floating-point serialization.
- Depth values include a small negative minimum in the background catalog (`-0.55 km`), so future code should not assume all depths are nonnegative.

#### Minimal Load Examples
- Interevent:
  - `pd.read_csv('.../TRACE_ridgecrest_relocated.csv')`
- Background with canonical field names:
  - read CSV, then rename `{datetime:'event_time', latR:'latitude', lonR:'longitude', depR:'depth_km', mag:'magnitude'}`
- Mainshocks:
  - `pd.read_csv('.../main_shock_events.csv')`

#### Most Relevant Fields for the Requested Workflow
- Temporal filtering: `event_time` / `datetime`
- Spatial masking and later projection: `latitude`, `longitude` (or `latR`, `lonR` before renaming)
- Depth retention in outputs: `depth_km` / `depR`
- Magnitude-frequency calculations: `magnitude` / `mag`
- Hypocenter centers and mainshock time bounds: `main_shock_events.csv`

------------------------------

## catalog_2year_background_before_64.csv
**Source path**: `<REPO_ROOT>/examples/ridgecrest/data/catalog_longterm/catalog_2year_background_before_64.csv`
### Summary
This file is a 30-column CSV background earthquake catalog with 1,536 events spanning 2019-01-04 to 2019-07-04, intended as the larger Ridgecrest regional reference prior to the Mw 6.4 mainshock. For the requested workflow, the essential fields are `datetime, latR, lonR, depR, mag`, which map cleanly to the canonical schema `event_time, latitude, longitude, depth_km, magnitude`; these core fields have no missing values.
### Detail
#### File Overview
- Path: `<REPO_ROOT>/examples/ridgecrest/data/catalog_longterm/catalog_2year_background_before_64.csv`
- Format: CSV
- Size: 277,760 bytes (~272 KB)
- Shape: **1,536 rows × 30 columns**
- Role in workflow: long-term regional background reference catalog for comparison against interevent subsets

#### Canonical Field Mapping for Future Agents
Use these columns to align this file with the interevent catalog schema:
- `datetime` → `event_time`
- `latR` → `latitude`
- `lonR` → `longitude`
- `depR` → `depth_km`
- `mag` → `magnitude`

These mapped fields are sufficient for:
- time filtering
- hypocentral coordinate handling
- depth retention in outputs
- magnitude-frequency / completeness workflows
- unified loading alongside the relocated interevent catalog

#### Full Column List
- `yr`
- `mon`
- `day`
- `hr`
- `min`
- `sec`
- `eID`
- `latR`
- `lonR`
- `depR`
- `mag`
- `qID`
- `cID`
- `nbranch`
- `qnpair`
- `qndiffP`
- `qndiffS`
- `rmsP`
- `rmsS`
- `eh`
- `ez`
- `et`
- `latC`
- `lonC`
- `depC`
- `evt_type`
- `mag_type`
- `growclust_solution`
- `relocation_box`
- `datetime`

#### Column Types
- Integer-like:
  - `yr, mon, day, hr, min, eID, qID`
- Floating-point:
  - `sec, latR, lonR, depR, mag, cID, nbranch, qnpair, qndiffP, qndiffS, rmsP, rmsS, eh, ez, et, latC, lonC, depC`
- Text/object:
  - `evt_type, mag_type, growclust_solution, relocation_box, datetime`

#### Core Metadata Relevant to Requested Processing
- Timestamp field:
  - `datetime` is a parseable timestamp string
  - Observed range:
    - Min: `2019-01-04 07:13:44.847000+00:00`
    - Max: `2019-07-04 17:27:35.109000+00:00`
  - Null count: `0`
- Spatial fields:
  - `latR` range: `35.00333` to `36.4985`
  - `lonR` range: `-118.49638` to `-117.00607`
  - `depR` range: `-0.55` to `17.3` km
  - Null count in mapped spatial fields: `0`
- Magnitude field:
  - `mag` range: `-0.74` to `3.98`
  - Null count: `0`
  - Decimal precision appears mostly to 2 decimal places, with some 1-decimal values
  - Observed decimal-length counts in string form: `{1: 169, 2: 1367}`

#### Missing-Value Pattern
- No missing values in the key mapped analysis fields:
  - `datetime`
  - `latR`
  - `lonR`
  - `depR`
  - `mag`
- Auxiliary metadata columns with missing values include:
  - `cID` (87)
  - `nbranch` (88)
  - `qnpair` (88)
  - `qndiffP` (88)
  - `qndiffS` (88)
  - `rmsP` (88)
  - `latC` (88)
  - `lonC` (88)
  - `depC` (88)
  - `mag_type` (88)
  - `relocation_box` (88)
- These nulls are in secondary QC/relocation attributes and do not block canonical remapping.

#### Example Record Structure
Each row contains both decomposed date/time parts and a combined timestamp, along with relocated coordinates and relocation/quality metadata. Example pattern:
- `yr, mon, day, hr, min, sec, eID, latR, lonR, depR, mag, ... , datetime`

Observed preview shows records like:
- `2019-01-04 18:39:53.314` with `latR ~ 36.46344`, `lonR ~ -117.96927`, `depR ~ 3.683`, `mag ~ 0.96`
- `2019-01-05 07:55:57.805` with `latR ~ 36.06686`, `lonR ~ -117.99501`, `depR ~ 6.619`, `mag ~ 1.85`

#### Notes for Future Loading
- Recommended load path:
  - read with `pandas.read_csv(...)`
  - rename mapped columns to canonical names
  - parse `event_time = pd.to_datetime(event_time, utc=True)`
- Because both decomposed date/time columns and `datetime` are present, future agents should prefer `datetime` as the authoritative timestamp field for alignment with the interevent catalog.
- `depR` includes a small negative minimum, so code should not assume all depths are nonnegative.
- This file contains only the larger-area regional background domain; it is not pre-split into local Mw 6.4 or Mw 7.1 cores.

#### Minimal Schema Needed by Analysis Agents
For most downstream catalog-comparison code, only these renamed fields are required:
- `event_time`
- `latitude`
- `longitude`
- `depth_km`
- `magnitude`

All five are available directly after renaming:
- `datetime -> event_time`
- `latR -> latitude`
- `lonR -> longitude`
- `depR -> depth_km`
- `mag -> magnitude`

#### Relationship to Other Ridgecrest Inputs
- This background file is structurally different from the interevent relocated catalog because it contains many additional relocation/QC columns.
- After renaming the five mapped fields, it becomes schema-compatible with:
  - `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/TRACE_ridgecrest_relocated.csv`
  - `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/main_shock_events.csv`

------------------------------

## main_shock_events.csv
**Source path**: `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/main_shock_events.csv`
### Summary
This file is a very small 2-row CSV containing the Mw 6.4 and Mw 7.1 Ridgecrest mainshock hypocenters and origin times. It already uses the same canonical schema as the interevent catalog (`event_time, latitude, longitude, depth_km, magnitude`), making it the direct reference table for temporal bounds and local-core spatial centers.
### Detail
#### File Overview
- Path: `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/main_shock_events.csv`
- Format: CSV
- Size: 176 bytes
- Shape: **2 rows × 5 columns**
- Primary role in workflow:
  - defines the Mw 6.4 and Mw 7.1 mainshock hypocenters
  - provides the start/end timestamps for the interevent window
  - provides local-core center coordinates for radius-based spatial masks

#### Columns
- `event_time`
- `latitude`
- `longitude`
- `depth_km`
- `magnitude`

#### Data Types
- `event_time`: string/object timestamp field, parseable to UTC datetime
- `latitude`: `float64`
- `longitude`: `float64`
- `depth_km`: `float64`
- `magnitude`: `float64`

#### Completeness / Missing Values
- No missing values in any column
- Null counts:
  - `event_time`: 0
  - `latitude`: 0
  - `longitude`: 0
  - `depth_km`: 0
  - `magnitude`: 0

#### Contents
The file contains exactly two events:
1. **Mw 6.4 mainshock**
   - `event_time`: `2019-07-04 17:33:49.040000+00:00`
   - `latitude`: `35.70421`
   - `longitude`: `-117.49392`
   - `depth_km`: `11.864`
   - `magnitude`: `6.4`
2. **Mw 7.1 mainshock**
   - `event_time`: `2019-07-06 03:19:53.040000+00:00`
   - `latitude`: `35.77623`
   - `longitude`: `-117.59286`
   - `depth_km`: `1.986`
   - `magnitude`: `7.1`

#### Value Ranges
- Time range:
  - Min: `2019-07-04 17:33:49.040000+00:00`
  - Max: `2019-07-06 03:19:53.040000+00:00`
- Latitude range: `35.70421` to `35.77623`
- Longitude range: `-117.59286` to `-117.49392`
- Depth range: `1.986` to `11.864` km
- Magnitude range: `6.4` to `7.1`

#### Relevance for Future Agents
- The file already matches the canonical schema used by the interevent catalog, so it can be read directly with no column renaming.
- Future agents can use it to:
  - identify the Mw 6.4 and Mw 7.1 hypocentral centers for local cylindrical/core masks
  - define the full interevent interval as the time between these two events
  - exclude the two mainshocks from interevent b-value subsets after time filtering
  - label plots and tables with exact mainshock metadata

#### Spatial-Mask Context
- These two hypocenters are the center points for the requested local radius masks (e.g., 4, 5, 6, 7 km).
- Because the requested workflow uses projected local metric coordinates and horizontal distance only, future agents will primarily consume:
  - `latitude`
  - `longitude`
for mask construction, while still retaining `depth_km` in outputs.

#### Temporal-Window Context
- The Mw 6.4 event time is the natural lower bound for the interevent period.
- The Mw 7.1 event time is the natural upper bound for the interevent period.
- Both events themselves should be excluded from interevent subset calculations, but this file is the authoritative source for those exclusion records and timestamps.

#### Loading Notes
- Recommended loading:
  - `pd.read_csv('<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/main_shock_events.csv')`
  - then parse `event_time` with `pd.to_datetime(..., utc=True)`
- Since the file is only two rows, future code can safely treat it as a reference/lookup table rather than a large catalog.

#### Relationship to Other Ridgecrest Inputs
- Schema-compatible with:
  - `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/TRACE_ridgecrest_relocated.csv`
- Complements the background catalog:
  - `<REPO_ROOT>/examples/ridgecrest/data/catalog_longterm/catalog_2year_background_before_64.csv`
  - background file requires column remapping, but this mainshock file does not

------------------------------

