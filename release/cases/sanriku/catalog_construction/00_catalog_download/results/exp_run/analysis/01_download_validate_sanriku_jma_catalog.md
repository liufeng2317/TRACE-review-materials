## Scientific Purpose

This task implemented and validated a workflow to download the authenticated NIED Hi-net/JMA unified hypocenter catalog for the Sanriku, northeast Japan study region. The scientific goal was to produce an ASPECT-ready earthquake catalog for the manuscript-aligned interval from 2025-06-01 through 2026-05-01, using the half-open request interval 2025-06-01 ≤ time < 2026-05-02, and the inclusive Sanriku spatial bounds 38.50–42.50°N and 141.00–144.50°E.

The workflow output is intended to support later seismicity analysis and visualization for the Sanriku region by providing a cleaned catalog with exactly the required ASPECT columns:

`datetime,lat,lon,dep,mag`

## Method and Implementation Evidence

The implemented workflow used the NIED Hi-net authenticated JMA catalog service:

- Login endpoint: `https://hinetwww11.bosai.go.jp/auth/?LANG=en`
- Catalog endpoint: `https://hinetwww11.bosai.go.jp/auth/JMA/jmalist.php`

Implementation evidence is available in the script:

- `<CASE_ROOT>/run/00_catalog_download/exp_run/scripts/01_download_validate_sanriku_jma_catalog.py`

Key implementation features verified from the script and validation outputs include:

- Authentication was performed with `requests.Session`, preserving the authenticated session across catalog requests.
- Credentials were read from the `.env` source unless overridden. The validation JSON records `credential_source: .env`.
- Network requests used retry/backoff logic through a dedicated request wrapper.
- The manuscript-aligned time interval was fixed to:
  - start date inclusive: `2025-06-01`
  - end date exclusive: `2026-05-02`
  - requested coverage note: records cover `2025-06-01` through `2026-05-01`.
- Requests were split into 48 chunks:
  - 47 chunks of 7 days
  - 1 final chunk of 6 days
  - maximum chunk duration was therefore within the required 7-day service limit.
- The JMA catalog table was parsed with fixed-width field positions rather than comma splitting.
- Cleaning steps included:
  - datetime parsing using mixed-format parsing;
  - numeric conversion of latitude, longitude, depth, and magnitude;
  - removal of rows with missing required values;
  - half-open time filtering;
  - inclusive Sanriku spatial filtering;
  - physical sanity filtering;
  - sorting by datetime;
  - duplicate removal.
- Optional raw-response saving was retained through a raw directory argument. In this run, raw chunk files were not saved because no raw directory was provided; only login/debug HTML files were saved.

Primary validation metadata is stored in:

- `<CASE_ROOT>/run/00_catalog_download/exp_run/outputs/01_download_validate_sanriku_jma_catalog/Snet_catalog_20250601_20260502_validation.json`

Chunk-level request and parsing evidence is stored in:

- `<CASE_ROOT>/run/00_catalog_download/exp_run/outputs/01_download_validate_sanriku_jma_catalog/Snet_catalog_20250601_20260502_chunk_manifest.csv`

Login/debug HTML files are stored at:

- `<CASE_ROOT>/run/00_catalog_download/exp_run/outputs/01_download_validate_sanriku_jma_catalog/debug/raw/login_page.html`
- `<CASE_ROOT>/run/00_catalog_download/exp_run/outputs/01_download_validate_sanriku_jma_catalog/debug/raw/login_response.html`

## Key Results and Evidence Files

### Cleaned ASPECT-ready catalog

The cleaned catalog was successfully generated at:

- `<CASE_ROOT>/run/00_catalog_download/exp_run/outputs/01_download_validate_sanriku_jma_catalog/Snet_catalog_20250601_20260502.csv`

Validation confirms that the CSV contains exactly the required columns:

`datetime,lat,lon,dep,mag`

The catalog contains:

- Final event count: **33,711 events**
- Time range:
  - minimum: `2025-06-01 00:09:02.360000`
  - maximum: `2026-05-01 23:58:44.740000`
- Latitude range: **38.5 to 42.5°N**
- Longitude range: **141.0 to 144.5°E**
- Depth range: **0.0 to 149.2 km**
- Magnitude range: **0.0 to 7.7**
- Missing values in required fields: **0**
- Duplicate ASPECT rows: **0**
- Datetime order: sorted monotonically increasing

These checks were verified from both the CSV and the validation file:

- `<CASE_ROOT>/run/00_catalog_download/exp_run/outputs/01_download_validate_sanriku_jma_catalog/Snet_catalog_20250601_20260502_validation.json`

### Download and chunk validation

The chunk manifest confirms that the requested interval was split correctly and that all chunks were successfully downloaded and parsed:

- Evidence file: `<CASE_ROOT>/run/00_catalog_download/exp_run/outputs/01_download_validate_sanriku_jma_catalog/Snet_catalog_20250601_20260502_chunk_manifest.csv`

Key manifest results:

- Total chunks requested: **48**
- Chunk duration range: **6 to 7 days**
- Status counts: **48 success**
- Parse status counts: **48 parsed**
- Attempts: **all chunks completed in 1 attempt**
- HTTP status: **200 for all successful chunks**
- Total parsed rows before Sanriku filtering: **270,338**
- Total retained Sanriku rows after filtering: **33,711**
- Chunks with zero retained Sanriku events: **0**
- Global actual returned datetime range before regional filtering:
  - `2025-06-01 00:03:37.790000` to `2026-05-01 23:58:44.740000`
- Global retained Sanriku datetime range:
  - `2025-06-01 00:09:02.360000` to `2026-05-01 23:58:44.740000`

The first chunk covered `2025-06-01` to `2025-06-08` exclusive and submitted an inclusive service end date of `2025-06-07`. It parsed 5,359 rows and retained 502 Sanriku rows.

The final chunk covered `2026-04-26` to `2026-05-02` exclusive and submitted an inclusive service end date of `2026-05-01`. It parsed 5,328 rows and retained 1,543 Sanriku rows.

### Cleaning statistics

The validation JSON provides a reproducible cleaning audit:

- Evidence file: `<CASE_ROOT>/run/00_catalog_download/exp_run/outputs/01_download_validate_sanriku_jma_catalog/Snet_catalog_20250601_20260502_validation.json`

Cleaning statistics:

- Initial parsed rows: **270,338**
- Rows after datetime/numeric parsing and missing-value removal: **270,338**
- Rows removed for invalid datetime or numeric fields: **0**
- Rows after requested time filter: **270,338**
- Rows removed outside requested time: **0**
- Rows after Sanriku spatial filter: **33,711**
- Rows removed outside Sanriku bounds: **236,627**
- Rows after physical sanity filter: **33,711**
- Rows removed by physical sanity filter: **0**
- Duplicates removed: **0**
- Final rows: **33,711**

This confirms that the largest reduction came from applying the Sanriku spatial bounds after parsing the broader returned JMA catalog data.

### Catalog distribution figure

The required catalog distribution figure was generated at:

- `<CASE_ROOT>/run/00_catalog_download/exp_run/outputs/01_download_validate_sanriku_jma_catalog/Snet_catalog_20250601_20260502_distribution.png`

The figure contains two main panels:

1. **Spatial and depth distribution**
   - Longitude axis spans approximately 141.0–144.5°E.
   - Latitude axis spans approximately 38.5–42.5°N.
   - A red rectangle marks the Sanriku selection bounds.
   - Events are colored by hypocentral depth from 0 to about 150 km.
   - The plotted catalog contains events across the full Sanriku domain, with dense offshore-to-nearshore clusters between roughly 142–143.5°E and 39–42°N.
   - Deeper events are more common toward the western side of the domain, while shallower events are more common in the central and eastern portions.

2. **Temporal distribution**
   - Histogram uses 7-day bins.
   - Total plotted events: **N = 33,711**
   - Activity is temporally non-uniform.
   - Background levels during much of June–October 2025 are lower, commonly several hundred events per 7-day bin.
   - Large bursts occur in late 2025, especially around November–December, with a peak exceeding 3,000 events per 7-day bin.
   - Another major increase appears around April 2026, with a peak near 3,000 events per 7-day bin.

The figure annotation confirms:

- Catalog: Hi-net/JMA
- Time span: 2025-06-01 to 2026-05-02
- Event count: **33,711**
- Magnitude range: **M 0.0 to 7.7**
- Depth range: **0.0 to 149.2 km**

## Limitations and Assumptions

- The workflow depends on authenticated access to the NIED Hi-net/JMA catalog service. Reproduction requires valid credentials.
- The validation confirms successful download and parsing for this run, but it does not independently verify the completeness or scientific quality of the JMA catalog itself.
- No magnitude of completeness analysis was performed. The magnitude range is reported as 0.0–7.7, but completeness may vary in space, time, and after large sequences.
- No uncertainty fields were retained in the ASPECT-ready output. The required CSV contains only `datetime,lat,lon,dep,mag`.
- The distribution figure shows spatial, depth, and temporal patterns but does not include a magnitude-frequency distribution or uncertainty diagnostics.
- Raw per-chunk response files were not saved in this execution because the optional raw directory argument was not used. The chunk manifest records `raw_file_path` as empty for all chunks. Login/debug HTML files were saved, but no parse-failure debug files were produced because all chunks parsed successfully.
- The catalog contains strong temporal clustering, especially in late 2025 and April 2026. Any downstream rate-based or training/validation analysis should account for these burst-like sequences.
- The endpoint was queried in 7-day-or-shorter chunks, and all chunks returned dates within the intended half-open interval. However, the returned catalog is still service-dependent and could change if the JMA/Hi-net catalog is revised.

## Report-Ready Summary

A complete authenticated Hi-net/JMA unified hypocenter catalog workflow was implemented and validated for the Sanriku study region. The workflow used the manuscript-aligned half-open interval `2025-06-01 ≤ time < 2026-05-02`, corresponding to requested records from 2025-06-01 through 2026-05-01, and applied inclusive Sanriku bounds of 38.50–42.50°N and 141.00–144.50°E after parsing.

The resulting ASPECT-ready CSV is:

- `<CASE_ROOT>/run/00_catalog_download/exp_run/outputs/01_download_validate_sanriku_jma_catalog/Snet_catalog_20250601_20260502.csv`

It contains **33,711 cleaned events** with exactly the required fields `datetime,lat,lon,dep,mag`. The final catalog spans `2025-06-01 00:09:02.360000` to `2026-05-01 23:58:44.740000`, with depths from **0.0 to 149.2 km** and magnitudes from **0.0 to 7.7**. Validation found no missing required values, no duplicate rows, and all events within the specified time and spatial bounds.

The request audit is preserved in:

- `<CASE_ROOT>/run/00_catalog_download/exp_run/outputs/01_download_validate_sanriku_jma_catalog/Snet_catalog_20250601_20260502_chunk_manifest.csv`

All **48 chunks** succeeded and parsed correctly, with no chunk exceeding the 7-day request limit.

The main visualization is:

- `<CASE_ROOT>/run/00_catalog_download/exp_run/outputs/01_download_validate_sanriku_jma_catalog/Snet_catalog_20250601_20260502_distribution.png`

It confirms the regional spatial selection, shows depth variation across the Sanriku domain, and documents strong temporal clustering, especially around November–December 2025 and April 2026.