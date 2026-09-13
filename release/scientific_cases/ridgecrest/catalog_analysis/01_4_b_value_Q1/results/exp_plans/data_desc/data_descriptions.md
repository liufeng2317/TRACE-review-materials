# Data Descriptions
## TRACE_ridgecrest_relocated.csv
**Source path**: `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/TRACE_ridgecrest_relocated.csv`
### Summary
This directory contains two key CSV inputs for the Ridgecrest sequence: a relocated event catalog with 84,474 rows and a 2-row mainshock metadata table. Both files share the same core schema (`event_time, latitude, longitude, depth_km, magnitude`), use UTC timestamps, and are directly suitable for filtering the Mw 6.4–Mw 7.1 interevent interval and constructing spatial masks around the two hypocenters.
### Detail
#### Folder Structure
- Directory: `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE`
- Relevant files for the requested workflow:
  - `TRACE_ridgecrest_relocated.csv` — relocated earthquake catalog
  - `main_shock_events.csv` — metadata for the Mw 6.4 and Mw 7.1 mainshocks
- Other file present:
  - `visualize.ipynb` — notebook in the same folder, likely exploratory/plotting support, but not required to load the catalog data

#### File Overview
1. **Relocated catalog**
   - Path: `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/TRACE_ridgecrest_relocated.csv`
   - Size: ~7.66 MB
   - Rows/columns: `84,474 x 5`
   - Header columns:
     - `event_time`
     - `latitude`
     - `longitude`
     - `depth_km`
     - `magnitude`

2. **Mainshock table**
   - Path: `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/main_shock_events.csv`
   - Size: 176 bytes
   - Rows/columns: `2 x 5`
   - Header columns match the catalog exactly:
     - `event_time`
     - `latitude`
     - `longitude`
     - `depth_km`
     - `magnitude`

#### Schema and Data Types
Both CSVs use the same flat tabular schema:
- `event_time`: timestamp string; parseable as timezone-aware UTC datetime
- `latitude`: `float64`
- `longitude`: `float64`
- `depth_km`: `float64`
- `magnitude`: `float64`

No missing values were found in either file for these fields.

#### Temporal Coverage
**Relocated catalog**
- Earliest event: `2019-07-04 00:56:37.590000+00:00`
- Latest event: `2019-07-25 23:59:29.320000+00:00`

**Mainshock file**
- Mw 6.4 origin: `2019-07-04 17:33:49.040000+00:00`
- Mw 7.1 origin: `2019-07-06 03:19:53.040000+00:00`

For the user-prioritized interevent interval, filtering the relocated catalog strictly between those two origin times yields:
- `4,714` catalog rows between the mainshocks based on time only
- The two mainshocks themselves are stored separately in `main_shock_events.csv`

#### Key Event Metadata Relevant to Future Analysis
**Mainshock hypocenters from `main_shock_events.csv`**
- Mw 6.4:
  - `event_time`: `2019-07-04 17:33:49.040000+00:00`
  - `latitude`: `35.70421`
  - `longitude`: `-117.49392`
  - `depth_km`: `11.864`
  - `magnitude`: `6.4`
- Mw 7.1:
  - `event_time`: `2019-07-06 03:19:53.040000+00:00`
  - `latitude`: `35.77623`
  - `longitude`: `-117.59286`
  - `depth_km`: `1.986`
  - `magnitude`: `7.1`

**Fixed separator event requested by the user**
- Exact timestamp searched in the relocated catalog: `2019-07-05T11:07:52.830000Z`
- Exact matching row exists in `TRACE_ridgecrest_relocated.csv`
- Separator metadata:
  - `event_time`: `2019-07-05 11:07:52.830000+00:00`
  - `latitude`: `35.758237795185046`
  - `longitude`: `-117.56793972429624`
  - `depth_km`: `6.42093878`
  - `magnitude`: `5.37`
- Time difference from requested separator timestamp: `0.0` seconds

#### Basic Value Ranges
**Relocated catalog**
- `latitude`: min `35.27090479518505`, max `36.311627795185046`, mean `35.76477956613717`
- `longitude`: min `-118.06486693463452`, max `-116.9939567617556`, mean `-117.57212935260488`
- `depth_km`: min `0.367625`, max `26.3518736`, mean `5.525718645130455`
- `magnitude`: min `-0.85`, max `7.1`, mean `1.0008796942933396`

**Mainshock table**
- `latitude`: `35.70421` to `35.77623`
- `longitude`: `-117.59286` to `-117.49392`
- `depth_km`: `1.986` to `11.864`
- `magnitude`: `6.4` to `7.1`

#### Formatting and Precision Notes
- `event_time` values are stored as strings but parse cleanly to UTC-aware datetimes.
- Magnitudes appear to be recorded mostly at `0.01` precision:
  - exact to 1 decimal: ~10.16%
  - exact to 2 decimals: ~89.55%
  - exact to 3 decimals: ~99.75%
- This suggests future agents can likely infer a magnitude bin width near `0.01` for methods that require `delta_M`, but that should be confirmed during analysis rather than assumed from this metadata summary alone.

#### Example Records
**Catalog example rows**
- `2019-07-04 00:56:37.590000+00:00, 36.08852379518505, -117.82790782193672, 9.70163162, 0.66`
- `2019-07-04 02:34:31.210000+00:00, 36.11893979518505, -117.64291706091387, 3.79348124, 0.43`
- `2019-07-04 03:20:28.460000+00:00, 36.11053679518505, -117.62022744201748, 2.27652371, 0.88`

**Mainshock rows**
- `2019-07-04 17:33:49.040000+00:00, 35.70421, -117.49392, 11.864, 6.4`
- `2019-07-06 03:19:53.040000+00:00, 35.77623, -117.59286, 1.986, 7.1`

#### How Future Agents Can Use These Files
- Load both files with standard CSV readers (`pandas.read_csv`) and parse `event_time` as UTC datetimes.
- Use `main_shock_events.csv` as the authoritative source for the Mw 6.4 and Mw 7.1 hypocenter centers and origin times.
- Use `TRACE_ridgecrest_relocated.csv` as the event source for interevent filtering, separator-event removal, spatial selection, and later sliding-window construction.
- The schema is simple and uniform, so joins are not required; the mainshock file functions as a compact metadata table for centers/endpoints, while the relocated catalog provides the event sequence.

#### Naming and Organization Pattern
- Both relevant files are plain CSV tables in a single directory with descriptive names.
- Naming convention is straightforward:
  - `TRACE_ridgecrest_relocated.csv` → full relocated event catalog
  - `main_shock_events.csv` → special event metadata table for the two mainshocks
- There are no nested subdirectories to traverse for these required inputs.

------------------------------

## main_shock_events.csv
**Source path**: `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/main_shock_events.csv`
### Summary
This CSV is a compact 2-row metadata table containing the two Ridgecrest mainshocks needed to define the interevent analysis window and the centers of the Mw 6.4 control core and Mw 7.1 target core. It uses the same schema as the relocated catalog (`event_time, latitude, longitude, depth_km, magnitude`), with complete UTC timestamps and no missing values.
### Detail
#### File Structure
- Path: `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/main_shock_events.csv`
- Format: CSV
- Size: 176 bytes
- Dimensions: `2 rows x 5 columns`
- Header:
  - `event_time`
  - `latitude`
  - `longitude`
  - `depth_km`
  - `magnitude`

#### Column Metadata
- `event_time`
  - Type on read: string/object
  - Parseable as timezone-aware UTC datetime
  - No missing values
- `latitude`
  - Type: `float64`
  - No missing values
- `longitude`
  - Type: `float64`
  - No missing values
- `depth_km`
  - Type: `float64`
  - No missing values
- `magnitude`
  - Type: `float64`
  - No missing values

#### Row Contents
This file contains exactly two events, corresponding to the two mainshocks referenced in the user request.

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

#### Statistics and Ranges
- Time range:
  - Earliest: `2019-07-04 17:33:49.040000+00:00`
  - Latest: `2019-07-06 03:19:53.040000+00:00`
- `latitude`:
  - min: `35.70421`
  - max: `35.77623`
  - mean: `35.74022`
- `longitude`:
  - min: `-117.59286`
  - max: `-117.49392`
  - mean: `-117.54339`
- `depth_km`:
  - min: `1.986`
  - max: `11.864`
  - mean: `6.925`
- `magnitude`:
  - min: `6.4`
  - max: `7.1`
  - mean: `6.75`

#### Relevance for Future Agents
- Use this file as the authoritative source for:
  - the Mw 6.4 origin time that starts the interevent window,
  - the Mw 7.1 origin time that ends the interevent window,
  - the hypocenter coordinates for the two cylindrical core centers,
  - the reported depths to retain in metadata or output tables.
- Because the schema matches the relocated catalog exactly, future agents can load both files with the same parser and treat this file as a small event-metadata table.
- The two rows are sufficient to define time filtering and spatial center points; no joins or extra lookup tables are required.

#### Example Access Pattern
- Load with `pandas.read_csv(...)`
- Parse `event_time` with `pd.to_datetime(..., utc=True)`
- Identify the two mainshocks directly from the `magnitude` values (`6.4` and `7.1`) or by row order after inspection

#### File Naming and Organization
- Filename pattern is descriptive rather than encoded:
  - `main_shock_events.csv` = compact table of major reference events
- It lives alongside the full relocated catalog in:
  - `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE`
- Companion file typically used with it:
  - `TRACE_ridgecrest_relocated.csv` for the event sequence that will be filtered between these two timestamps

------------------------------

