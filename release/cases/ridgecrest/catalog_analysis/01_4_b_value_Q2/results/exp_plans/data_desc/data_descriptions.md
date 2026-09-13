# Data Descriptions
## TRACE_ridgecrest_relocated.csv
**Source path**: `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/TRACE_ridgecrest_relocated.csv`
### Summary
The Ridgecrest data needed for future spatial b-value work are organized across two small folders: `catalog_TRACE` contains the relocated sequence catalog and a 2-row main-shock file, while `catalog_longterm` contains a broader 2-year background catalog for regional reference. The interevent catalog is a single 84,474-row CSV with complete `event_time, latitude, longitude, depth_km, magnitude` fields spanning 2019-07-04 to 2019-07-25; the main-shock file provides the Mw 6.4 and Mw 7.1 origin metadata needed to define analysis windows.
### Detail
#### Folder Structure

- Base Ridgecrest data area inspected:
  - `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE`
  - `<REPO_ROOT>/examples/ridgecrest/data/catalog_longterm`
- Relevant files for the requested future workflow:
  - `catalog_TRACE/TRACE_ridgecrest_relocated.csv` — primary relocated earthquake catalog used to construct interevent windows.
  - `catalog_TRACE/main_shock_events.csv` — two-event reference file containing Mw 6.4 and Mw 7.1 main shocks.
  - `catalog_longterm/catalog_2year_background_before_64.csv` — larger regional reference catalog for background/context only.
- Other file present but not profiled for science content:
  - `catalog_TRACE/visualize.ipynb`

#### Primary File: `TRACE_ridgecrest_relocated.csv`

- Path: `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/TRACE_ridgecrest_relocated.csv`
- Format: CSV
- Size: ~7.4 MB
- Shape: `84474 x 5`
- Columns:
  - `event_time` (`object` in CSV; parseable as timezone-aware UTC timestamp)
  - `latitude` (`float64`)
  - `longitude` (`float64`)
  - `depth_km` (`float64`)
  - `magnitude` (`float64`)
- Missing values:
  - No nulls detected in any of the 5 columns.

#### Key Metadata for `TRACE_ridgecrest_relocated.csv`

- Time coverage:
  - Minimum: `2019-07-04 00:56:37.590000+00:00`
  - Maximum: `2019-07-25 23:59:29.320000+00:00`
- Spatial extent:
  - Latitude: `35.27090479518505` to `36.311627795185046`
  - Longitude: `-118.06486693463452` to `-116.9939567617556`
- Depth range:
  - `0.367625` to `26.3518736` km
- Magnitude range:
  - `-0.85` to `7.1`
- Magnitude precision note:
  - Values are stored as floating point with apparent fine precision; the minimum positive step inferred from unique values is about `0.000101`.
  - For future b-value workflows, agents should not assume this is the physically meaningful reporting bin; inspect rounding/quantization before choosing `delta_M`.

#### Example Records from `TRACE_ridgecrest_relocated.csv`

- Example row fields follow the expected analysis schema directly:
  - `event_time='2019-07-04 00:56:37.590000+00:00', latitude=36.08852379518505, longitude=-117.82790782193672, depth_km=9.70163162, magnitude=0.66`
  - `event_time='2019-07-04 02:34:31.210000+00:00', latitude=36.11893979518505, longitude=-117.64291706091387, depth_km=3.79348124, magnitude=0.43`
  - `event_time='2019-07-04 03:20:28.460000+00:00', latitude=36.11053679518505, longitude=-117.62022744201748, depth_km=2.27652371, magnitude=0.88`

#### Main-Shock Reference File: `main_shock_events.csv`

- Path: `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/main_shock_events.csv`
- Format: CSV
- Size: 176 bytes
- Shape: `2 x 5`
- Columns:
  - `event_time`, `latitude`, `longitude`, `depth_km`, `magnitude`
- Missing values:
  - No nulls detected.
- Contents:
  - Two rows corresponding to the Ridgecrest Mw 6.4 and Mw 7.1 main shocks.
- Parsed entries:
  - Mw 6.4: `2019-07-04 17:33:49.040000+00:00`, lat `35.70421`, lon `-117.49392`, depth `11.864` km
  - Mw 7.1: `2019-07-06 03:19:53.040000+00:00`, lat `35.77623`, lon `-117.59286`, depth `1.986` km
- Future agents can read this file directly to define the interevent interval and to project/plot the two main-shock hypocenters.

#### Background Regional Catalog: `catalog_2year_background_before_64.csv`

- Path: `<REPO_ROOT>/examples/ridgecrest/data/catalog_longterm/catalog_2year_background_before_64.csv`
- Format: CSV
- Size: ~272 KB
- Shape: `1536 x 30`
- Intended role from the request:
  - Regional context/reference only, not the primary spatial interevent mapping source.
- Columns:
  - Time decomposition: `yr, mon, day, hr, min, sec`
  - Event identifiers / clustering: `eID, qID, cID, nbranch, qnpair`
  - Relocated coordinates/magnitude: `latR, lonR, depR, mag`
  - Differential/quality metrics: `qndiffP, qndiffS, rmsP, rmsS, eh, ez, et`
  - Catalog/original coordinates: `latC, lonC, depC`
  - Event metadata: `evt_type, mag_type, growclust_solution, relocation_box`
  - Combined timestamp string: `datetime`
- Dtypes:
  - Mostly numeric (`int64`/`float64`) plus several metadata strings (`object`).
- Missingness:
  - Several relocation/cluster metadata columns contain some nulls (for example `cID`, `nbranch`, `qnpair`, `qndiffP`, `qndiffS`, `rmsP`, `latC`, `lonC`, `depC`, `mag_type`, `relocation_box` each have missing entries).
  - Core fields used for a reference b-value appear populated: `datetime`, `latR`, `lonR`, `depR`, `mag`.

#### Key Metadata for Background Catalog

- Time coverage from `datetime`:
  - Minimum: `2019-01-04 07:13:44.847000+00:00`
  - Maximum: `2019-07-04 17:27:35.109000+00:00`
- Relocated-coordinate extent:
  - `latR`: `35.00333` to `36.4985`
  - `lonR`: `-118.49638` to `-117.00607`
  - `depR`: `-0.55` to `17.3` km
  - `mag`: `-0.74` to `3.98`
- Alternate/original coordinate columns also exist:
  - `latC`: `35.00543` to `36.46506`
  - `lonC`: `-118.49789` to `-117.00447`
  - `depC`: `0.2` to `15.35` km

#### Access and Loading Notes for Future Agents

- The interevent and main-shock files already share a simple, consistent schema:
  - `event_time, latitude, longitude, depth_km, magnitude`
- The background file uses different names:
  - Time: `datetime` instead of `event_time`
  - Coordinates/depth/magnitude for relocated solutions: `latR, lonR, depR, mag`
- Practical loading pattern:
  - Parse `event_time` and `datetime` with UTC enabled.
  - For the background catalog, choose explicitly whether to use relocated (`latR/lonR/depR`) or alternate (`latC/lonC/depC`) coordinates; relocated columns appear to be the more direct analog to the primary interevent file.
- The user-specified M5.37 separator event is not stored as a dedicated row/file marker in the inspected metadata; future agents will need to apply that timestamp manually when subsetting.

#### Suggested File-Naming/Organization Interpretation

- `catalog_TRACE/TRACE_ridgecrest_relocated.csv`
  - Single sequence-wide relocated catalog, likely intended as the master earthquake list for the July 2019 Ridgecrest sequence.
- `catalog_TRACE/main_shock_events.csv`
  - Minimal helper file holding only the main shocks needed as temporal/spatial anchors.
- `catalog_longterm/catalog_2year_background_before_64.csv`
  - Longer-term regional reference catalog preceding the Mw 6.4 event.

#### Minimal Preview Schema for Coding Agents

- Interevent catalog row model:
  - `{event_time: str/datetime, latitude: float, longitude: float, depth_km: float, magnitude: float}`
- Main-shock row model:
  - Same as interevent catalog
- Background row model relevant for regional reference:
  - `{datetime: str/datetime, latR: float, lonR: float, depR: float, mag: float, ...quality/cluster metadata...}`

#### Relevance to the Requested Future Workflow

- All fields needed for later temporal filtering and spatial projection are present in the interevent and main-shock files.
- The main-shock file provides the exact Mw 6.4 and Mw 7.1 origin metadata required to construct the requested windows.
- The background file is suitable for a larger-area reference calculation but has a different schema and additional quality/cluster columns that should be harmonized before use.

------------------------------

## catalog_2year_background_before_64.csv
**Source path**: `<REPO_ROOT>/examples/ridgecrest/data/catalog_longterm/catalog_2year_background_before_64.csv`
### Summary
This regional background catalog is a single CSV with 1,536 events and 30 columns covering 2019-01-04 through just before the Mw 6.4 main shock on 2019-07-04. It includes relocated coordinates, magnitude, timing, uncertainty, and clustering/quality metadata; for future b-value reference calculations, the most relevant fields are `datetime`, `latR`, `lonR`, `depR`, and `mag`.
### Detail
#### File Overview

- Path: `<REPO_ROOT>/examples/ridgecrest/data/catalog_longterm/catalog_2year_background_before_64.csv`
- Format: CSV
- Size: ~272 KB
- Shape: `1536 x 30`
- Role in the requested workflow:
  - Intended for larger-area regional context/reference only.
  - Not the main interevent sequence catalog.

#### Column Structure

The file contains these columns:

- Time components:
  - `yr`, `mon`, `day`, `hr`, `min`, `sec`
- Event identifiers / catalog linkage:
  - `eID`, `qID`
- Relocated hypocenter and magnitude fields most relevant for future agents:
  - `latR`, `lonR`, `depR`, `mag`
- Clustering / relocation diagnostics:
  - `cID`, `nbranch`, `qnpair`, `qndiffP`, `qndiffS`
- Residual and uncertainty fields:
  - `rmsP`, `rmsS`, `eh`, `ez`, `et`
- Alternate/original coordinate set:
  - `latC`, `lonC`, `depC`
- Event metadata:
  - `evt_type`, `mag_type`, `growclust_solution`, `relocation_box`
- Combined timestamp string:
  - `datetime`

#### Data Types

- Integer fields:
  - `yr`, `mon`, `day`, `hr`, `min`, `eID`, `qID`
- Floating-point fields:
  - `sec`, `latR`, `lonR`, `depR`, `mag`, `cID`, `nbranch`, `qnpair`, `qndiffP`, `qndiffS`, `rmsP`, `rmsS`, `eh`, `ez`, `et`, `latC`, `lonC`, `depC`
- String/object fields:
  - `evt_type`, `mag_type`, `growclust_solution`, `relocation_box`, `datetime`

#### Time Coverage

- Primary parseable timestamp field: `datetime`
- Time range:
  - Minimum: `2019-01-04 07:13:44.847000+00:00`
  - Maximum: `2019-07-04 17:27:35.109000+00:00`
- Parsing quality:
  - `datetime` parsed cleanly with no missing/invalid timestamps detected.

#### Spatial and Magnitude Extent

Using the relocated fields (`latR`, `lonR`, `depR`, `mag`):

- Latitude range: `35.00333` to `36.4985`
- Longitude range: `-118.49638` to `-117.00607`
- Depth range: `-0.55` to `17.3` km
- Magnitude range: `-0.74` to `3.98`

Using the alternate coordinate fields (`latC`, `lonC`, `depC`):

- Latitude range: `35.00543` to `36.46506`
- Longitude range: `-118.49789` to `-117.00447`
- Depth range: `0.2` to `15.35` km

#### Missing-Value Pattern

Core fields needed for a future regional-reference b-value appear populated:

- No nulls reported in:
  - `yr`, `mon`, `day`, `hr`, `min`, `sec`, `eID`, `latR`, `lonR`, `depR`, `mag`, `qID`, `rmsS`, `eh`, `ez`, `et`, `evt_type`, `growclust_solution`, `datetime`

Columns with some missing values:

- `cID`: 87 missing
- `nbranch`: 88 missing
- `qnpair`: 88 missing
- `qndiffP`: 88 missing
- `qndiffS`: 88 missing
- `rmsP`: 88 missing
- `latC`: 88 missing
- `lonC`: 88 missing
- `depC`: 88 missing
- `mag_type`: 88 missing
- `relocation_box`: 88 missing

This suggests that the relocated working coordinates (`latR/lonR/depR`) are more complete than the alternate `latC/lonC/depC` set.

#### Example Record Structure

Representative rows show the catalog stores one event per row with timing, relocated hypocenter, magnitude, and quality metadata. Example values include:

- `datetime='2019-01-04 07:13:44.847', latR=35.46101, lonR=-118.46871, depR=3.168, mag=1.25, evt_type='le', growclust_solution='gc'`
- `datetime='2019-01-04 18:39:53.314', latR=36.46344, lonR=-117.96927, depR=3.683, mag=0.96, evt_type='le', growclust_solution='gc'`
- `datetime='2019-01-05 07:55:57.805', latR=36.06686, lonR=-117.99501, depR=6.619, mag=1.85, evt_type='le', growclust_solution='gc'`

#### Most Relevant Fields for Future Agents

For the user-described future workflow, the background catalog can be reduced to a minimal reference schema:

- `datetime` → event time
- `latR` → latitude
- `lonR` → longitude
- `depR` → depth in km
- `mag` → magnitude

Useful auxiliary QC fields if needed:

- `eh`, `ez`, `et` for location/time uncertainty
- `rmsP`, `rmsS` for residual quality
- `evt_type`, `mag_type`, `growclust_solution` for filtering/metadata

#### Harmonization Notes

- This file does not use the same column names as the interevent catalog.
- To align with the relocated interevent CSV, future agents will likely need a rename map such as:
  - `datetime` → `event_time`
  - `latR` → `latitude`
  - `lonR` → `longitude`
  - `depR` → `depth_km`
  - `mag` → `magnitude`
- The file also contains both relocated (`latR/lonR/depR`) and alternate (`latC/lonC/depC`) coordinates; the relocated set is the cleaner direct analog to the main sequence catalog.

#### Usage Notes for Future Loading

- Recommended parsing:
  - Read with `pandas.read_csv`
  - Parse `datetime` as UTC-aware timestamps
- Recommended default coordinate choice for regional context:
  - Use `latR`, `lonR`, `depR`
- Caution:
  - Depth includes at least one negative value (`-0.55` km), so future agents should avoid assuming all depths are strictly positive.
  - Because this is a context catalog and not the interevent catalog, any future merging/filtering should keep schemas separate until explicitly harmonized.

------------------------------

## main_shock_events.csv
**Source path**: `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/main_shock_events.csv`
### Summary
This is a minimal two-row CSV containing the Mw 6.4 and Mw 7.1 Ridgecrest main shocks, with complete origin time, latitude, longitude, depth, and magnitude fields. It is the key reference file for future agents to define the interevent window and to locate the two main-shock hypocenters for spatial overlays or control/core-region extraction.
### Detail
#### File Overview

- Path: `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/main_shock_events.csv`
- Format: CSV
- Size: 176 bytes
- Shape: `2 x 5`
- Purpose in the requested workflow:
  - Provides the Mw 6.4 and Mw 7.1 origin metadata.
  - Supports construction of the interevent time window and map/profile overlays.

#### Column Structure

The file uses the same compact schema as the relocated interevent catalog:

- `event_time`
- `latitude`
- `longitude`
- `depth_km`
- `magnitude`

#### Data Types

- `event_time`: stored as string/object in CSV, parseable as UTC timestamp
- `latitude`: `float64`
- `longitude`: `float64`
- `depth_km`: `float64`
- `magnitude`: `float64`

#### Completeness

- No missing values detected in any column.
- All 2 rows contain complete hypocentral and magnitude information.

#### Event Contents

The two rows correspond to the two main shocks:

1. Mw 6.4 main shock
   - `event_time`: `2019-07-04 17:33:49.040000+00:00`
   - `latitude`: `35.70421`
   - `longitude`: `-117.49392`
   - `depth_km`: `11.864`
   - `magnitude`: `6.4`

2. Mw 7.1 main shock
   - `event_time`: `2019-07-06 03:19:53.040000+00:00`
   - `latitude`: `35.77623`
   - `longitude`: `-117.59286`
   - `depth_km`: `1.986`
   - `magnitude`: `7.1`

#### Time and Spatial Range

Because there are only two records, the file range is simply the span between these two events:

- Time range:
  - Minimum: `2019-07-04 17:33:49.040000+00:00`
  - Maximum: `2019-07-06 03:19:53.040000+00:00`
- Latitude range: `35.70421` to `35.77623`
- Longitude range: `-117.59286` to `-117.49392`
- Depth range: `1.986` to `11.864` km
- Magnitude range: `6.4` to `7.1`

#### Relevance for Future Agents

This file is the authoritative small reference table for:

- Reading the Mw 6.4 origin time as the interevent start marker.
- Reading the Mw 7.1 origin time as the interevent end marker.
- Plotting/overlaying the two main-shock hypocenters in map view.
- Defining 5 km core circles around the Mw 6.4 and Mw 7.1 hypocenters.
- Projecting the main-shock locations into a local metric coordinate system together with the event catalog.

#### Harmonization Notes

- The schema matches the primary relocated event catalog exactly:
  - `event_time, latitude, longitude, depth_km, magnitude`
- This makes it straightforward to:
  - parse timestamps consistently,
  - append or compare against the main event catalog,
  - use shared plotting/projection utilities without renaming columns.

#### Loading Notes

- Recommended parser behavior:
  - Read with `pandas.read_csv`
  - Parse `event_time` as timezone-aware UTC datetimes
- Since the file has only two rows, future agents can safely load it fully into memory and access the two events either by magnitude (`6.4`, `7.1`) or by time order.

#### Minimal Row Model

Each row follows this structure:

- `{event_time: str/datetime, latitude: float, longitude: float, depth_km: float, magnitude: float}`

This is sufficient for temporal window definition, geographic projection, and simple hypocentral reference overlays.

------------------------------

