---
author:
- TRACE
date: 2026-09-12
title: Implementation and Validation of a NIED Hi-net/JMA Unified Hypocenter Catalog Download Workflow for the Sanriku Region
---

# Abstract

This report documents an implemented and validated workflow for downloading, parsing, cleaning, and visualizing the authenticated NIED Hi-net/JMA unified hypocenter catalog for the Sanriku, northeast Japan study region. The workflow used the required login endpoint <https://hinetwww11.bosai.go.jp/auth/?LANG=en> and catalog endpoint <https://hinetwww11.bosai.go.jp/auth/JMA/jmalist.php>. It preserved the manuscript-aligned half-open time interval $`2025`$-06-01 $`\leq t <`$ $`2026`$-05-02, corresponding to requested records from 2025-06-01 through 2026-05-01, and applied inclusive Sanriku bounds of 38.50–42.50°N and 141.00–144.50°E after catalog parsing. The delivered ASPECT-ready CSV contains exactly the required fields `datetime,lat,lon,dep,mag`. Validation confirms 33,711 cleaned events, no missing required values, no duplicate rows, all events within the requested temporal and spatial bounds, and a generated catalog distribution figure. The workflow is scientifically usable as a cleaned input catalog, while remaining dependent on authenticated service access and not independently assessing JMA catalog completeness or uncertainty.

# Objective and Scope

The task objective was to implement and validate a reproducible workflow for the NIED Hi-net/JMA unified hypocenter catalog over the Sanriku region of northeast Japan. The workflow had six principal scientific and technical requirements:

1.  Authenticate against the NIED Hi-net service using the specified login endpoint and use the authenticated JMA catalog endpoint for catalog requests.

2.  Preserve the manuscript-aligned interval with start date 2025-06-01 and end date 2026-05-02 treated as exclusive, so the requested service coverage spans 2025-06-01 through 2026-05-01.

3.  Apply inclusive Sanriku spatial bounds only after catalog parsing: latitude 38.50–42.50°N and longitude 141.00–144.50°E.

4.  Respect the JMA service limit by splitting the query into chunks of no more than 7 days, and record the exact chunk boundaries and actual returned dates.

5.  Produce an ASPECT-ready CSV with exactly `datetime,lat,lon,dep,mag` and with filename pattern `Snet_catalog_YYYYMMDD_YYYYMMDD.csv`.

6.  Generate a catalog distribution figure suitable for visual validation of spatial, depth, and temporal coverage.

This report follows the evidence chain from implementation choices to validated outputs and then states limitations. The primary evidence files are the cleaned catalog CSV, the chunk manifest, the validation JSON, and the distribution figure listed in Table <a href="#tab:outputs" data-reference-type="ref" data-reference="tab:outputs">2</a>.

# Implementation Summary

The workflow implementation is stored in the script at <a href="<CASE_ROOT>/run/00_catalog_download/exp_run/scripts/01_download_validate_sanriku_jma_catalog.py" class="uri"><CASE_ROOT>/run/00_catalog_download/exp_run/scripts/01_download_validate_sanriku_jma_catalog.py</a>. Validation metadata record that the workflow used the authenticated Hi-net/JMA endpoints listed in Table <a href="#tab:method" data-reference-type="ref" data-reference="tab:method">1</a>. Credentials were read from the specified `.env` source unless command-line overrides were supplied; in this execution the validation JSON records `credential_source: .env`. The script used a `requests.Session` to maintain authentication state across catalog requests, and it used retry/backoff logic for network access.

<div id="tab:method">

| Item | Implemented value or evidence |
|:---|:---|
| Login endpoint | <https://hinetwww11.bosai.go.jp/auth/?LANG=en> |
| Catalog endpoint | <https://hinetwww11.bosai.go.jp/auth/JMA/jmalist.php> |
| Credential source in this run | `.env`; default credential file was the requested Hi-net account file, with command-line override support retained. |
| Session handling | Authentication performed with `requests.Session`, preserving the authenticated session for subsequent catalog requests. |
| Network robustness | Requests were made through retry/backoff logic. |
| Parser strategy | The JMA fixed-width catalog table was parsed using fixed-width field positions rather than fragile comma splitting. |
| Unparseable HTML handling | The implementation saves original failed HTML/text responses to debug/raw files and reports the saved path in the error message. No parse-failure debug files were required in this successful run. |
| Optional raw responses | The optional raw-directory argument was retained. It was not used in this execution, so raw per-chunk catalog response files were not saved. |
| Implementation script | <a href="<CASE_ROOT>/run/00_catalog_download/exp_run/scripts/01_download_validate_sanriku_jma_catalog.py" class="uri"><CASE_ROOT>/run/00_catalog_download/exp_run/scripts/01_download_validate_sanriku_jma_catalog.py</a> |

Key implementation choices and validation evidence.

</div>

## Temporal Chunking

The requested time interval was implemented as a half-open interval,
``` math
\text{2025-06-01} \leq t < \text{2026-05-02},
```
which is equivalent to requesting records dated 2025-06-01 through 2026-05-01 from a date-based service. The workflow split this interval into 48 request chunks: 47 chunks of 7 days and one final chunk of 6 days. The first chunk was 2025-06-01 to 2025-06-08 exclusive, with submitted inclusive service end date 2025-06-07. The final chunk was 2026-04-26 to 2026-05-02 exclusive, with submitted inclusive service end date 2026-05-01. The maximum chunk length was therefore exactly within the required 7-day service limit.

The exact chunk-level audit is preserved in <a href="<CASE_ROOT>/run/00_catalog_download/exp_run/outputs/01_download_validate_sanriku_jma_catalog/Snet_catalog_20250601_20260502_chunk_manifest.csv" class="uri"><CASE_ROOT>/run/00_catalog_download/exp_run/outputs/01_download_validate_sanriku_jma_catalog/Snet_catalog_20250601_20260502_chunk_manifest.csv</a>. The manifest includes, for each chunk, the requested half-open boundaries, submitted service date fields, submitted inclusive end date, status, parse status, attempt count, HTTP status, response size, parsed-row count, actual returned datetime range, retained Sanriku row count, retained Sanriku datetime range, and any raw/debug file paths or messages.

## Cleaning and ASPECT Output Construction

After fixed-width parsing, the workflow applied the requested cleaning sequence. Datetimes were parsed as temporal values; latitude, longitude, depth, and magnitude were converted to numeric values; rows with missing required values were removed; the requested time interval was enforced; inclusive Sanriku spatial bounds were applied; a physical sanity check was applied; rows were sorted by datetime; and duplicate ASPECT rows were removed. The physical sanity filter removed zero rows in this run, but it is documented here because it is an additional quality-control check beyond the minimum requested steps.

The final CSV was written to:

<div class="center">

<a href="<CASE_ROOT>/run/00_catalog_download/exp_run/outputs/01_download_validate_sanriku_jma_catalog/Snet_catalog_20250601_20260502.csv" class="uri"><CASE_ROOT>/run/00_catalog_download/exp_run/outputs/01_download_validate_sanriku_jma_catalog/Snet_catalog_20250601_20260502.csv</a>

</div>

Its filename, `Snet_catalog_20250601_20260502.csv`, follows the requested naming convention and uses the exclusive end date in the second date token. The file header is exactly:

<div class="center">

`datetime,lat,lon,dep,mag`.

</div>

# Validated Outputs

<div id="tab:outputs">

| Artifact | Absolute path |
|:---|:---|
| Cleaned ASPECT-ready catalog CSV | <a href="<CASE_ROOT>/run/00_catalog_download/exp_run/outputs/01_download_validate_sanriku_jma_catalog/Snet_catalog_20250601_20260502.csv" class="uri"><CASE_ROOT>/run/00_catalog_download/exp_run/outputs/01_download_validate_sanriku_jma_catalog/Snet_catalog_20250601_20260502.csv</a> |
| Chunk manifest CSV | <a href="<CASE_ROOT>/run/00_catalog_download/exp_run/outputs/01_download_validate_sanriku_jma_catalog/Snet_catalog_20250601_20260502_chunk_manifest.csv" class="uri"><CASE_ROOT>/run/00_catalog_download/exp_run/outputs/01_download_validate_sanriku_jma_catalog/Snet_catalog_20250601_20260502_chunk_manifest.csv</a> |
| Validation JSON | <a href="<CASE_ROOT>/run/00_catalog_download/exp_run/outputs/01_download_validate_sanriku_jma_catalog/Snet_catalog_20250601_20260502_validation.json" class="uri"><CASE_ROOT>/run/00_catalog_download/exp_run/outputs/01_download_validate_sanriku_jma_catalog/Snet_catalog_20250601_20260502_validation.json</a> |
| Catalog distribution figure | <a href="<CASE_ROOT>/run/00_catalog_download/exp_run/outputs/01_download_validate_sanriku_jma_catalog/Snet_catalog_20250601_20260502_distribution.png" class="uri"><CASE_ROOT>/run/00_catalog_download/exp_run/outputs/01_download_validate_sanriku_jma_catalog/Snet_catalog_20250601_20260502_distribution.png</a> |
| Login page debug HTML | <a href="<CASE_ROOT>/run/00_catalog_download/exp_run/outputs/01_download_validate_sanriku_jma_catalog/debug/raw/login_page.html" class="uri"><CASE_ROOT>/run/00_catalog_download/exp_run/outputs/01_download_validate_sanriku_jma_catalog/debug/raw/login_page.html</a> |
| Login response debug HTML | <a href="<CASE_ROOT>/run/00_catalog_download/exp_run/outputs/01_download_validate_sanriku_jma_catalog/debug/raw/login_response.html" class="uri"><CASE_ROOT>/run/00_catalog_download/exp_run/outputs/01_download_validate_sanriku_jma_catalog/debug/raw/login_response.html</a> |

Primary output artifacts used as report evidence. All paths are under the required run output directory.

</div>

The validation JSON at <a href="<CASE_ROOT>/run/00_catalog_download/exp_run/outputs/01_download_validate_sanriku_jma_catalog/Snet_catalog_20250601_20260502_validation.json" class="uri"><CASE_ROOT>/run/00_catalog_download/exp_run/outputs/01_download_validate_sanriku_jma_catalog/Snet_catalog_20250601_20260502_validation.json</a> reports `status: pass`. The cleaned CSV, manifest, validation JSON, and figure were locally verified to exist before preparing this report.

# Catalog Validation Results

## Final Catalog Properties

The final ASPECT-ready catalog contains 33,711 cleaned events. The validated temporal, spatial, depth, and magnitude ranges are summarized in Table <a href="#tab:catalog_stats" data-reference-type="ref" data-reference="tab:catalog_stats">3</a>. These checks verify that the catalog preserves the intended half-open time interval and inclusive spatial filtering and that no required output fields are missing.

<div id="tab:catalog_stats">

| Quantity                | Validated value                        |
|:------------------------|:---------------------------------------|
| CSV columns             | `datetime,lat,lon,dep,mag`             |
| Final event count       | 33,711                                 |
| Datetime minimum        | 2025-06-01 00:09:02.360000             |
| Datetime maximum        | 2026-05-01 23:58:44.740000             |
| Latitude range          | 38.5 to 42.5°N                         |
| Longitude range         | 141.0 to 144.5°E                       |
| Depth range             | 0.0 to 149.2 km                        |
| Magnitude range         | 0.0 to 7.7                             |
| Missing required values | 0                                      |
| Duplicate ASPECT rows   | 0                                      |
| Datetime order          | Monotonically increasing after sorting |

Validated properties of the cleaned ASPECT-ready Sanriku catalog.

</div>

The first retained record in the delivered CSV has the expected ASPECT schema and begins at 2025-06-01 00:09:02.36 with latitude 42.337°N, longitude 144.484°E, depth 16.0 km, and magnitude 1.8. This example is not used as a scientific interpretation by itself; it verifies the delivered field order and formatting.

## Download and Chunk Audit

All 48 chunks completed successfully and parsed successfully. The manifest recorded HTTP status 200 for all successful chunks, and every chunk completed in one attempt. Table <a href="#tab:chunk_summary" data-reference-type="ref" data-reference="tab:chunk_summary">4</a> summarizes the chunk-level validation evidence.

<div id="tab:chunk_summary">

| Metric | Validated value |
|:---|:---|
| Total chunks requested |  |
| Chunk duration range | to 7 days |
| Status counts | success |
| Parse status counts | parsed |
| Attempt counts | All chunks completed in 1 attempt |
| HTTP status | for all successful chunks |
| Total parsed rows before regional filtering | ,338 |
| Total retained Sanriku rows | ,711 |
| Chunks with zero retained Sanriku events |  |
| Global returned datetime range before regional filtering | -06-01 00:03:37.790000 to 2026-05-01 23:58:44.740000 |
| Global retained Sanriku datetime range | -06-01 00:09:02.360000 to 2026-05-01 23:58:44.740000 |

Chunk-level download and parsing validation.

</div>

The first chunk, from 2025-06-01 to 2025-06-08 exclusive, parsed 5,359 rows and retained 502 Sanriku events. The final chunk, from 2026-04-26 to 2026-05-02 exclusive, parsed 5,328 rows and retained 1,543 Sanriku events. The final manifest row confirms that the final submitted inclusive service end date was 2026-05-01, consistent with treating 2026-05-02 as the exclusive endpoint.

## Cleaning Audit

The cleaning statistics in the validation JSON show that parsing and required-value conversion did not remove any records prior to spatial filtering. The dominant reduction was the requested Sanriku regional selection applied after parsing. Table <a href="#tab:cleaning" data-reference-type="ref" data-reference="tab:cleaning">5</a> gives the full cleaning audit.

<div id="tab:cleaning">

| Cleaning stage                                                |    Rows |
|:--------------------------------------------------------------|--------:|
| Initial parsed rows                                           | 270,338 |
| Rows after datetime/numeric parsing and missing-value removal | 270,338 |
| Rows removed for invalid datetime or numeric fields           |       0 |
| Rows after requested time filter                              | 270,338 |
| Rows removed outside requested time                           |       0 |
| Rows after Sanriku spatial filter                             |  33,711 |
| Rows removed outside Sanriku bounds                           | 236,627 |
| Rows after physical sanity filter                             |  33,711 |
| Rows removed by physical sanity filter                        |       0 |
| Duplicates removed                                            |       0 |
| Final rows                                                    |  33,711 |

Cleaning audit for the parsed JMA catalog.

</div>

These results support the conclusion that the ASPECT-ready file is a clean regional subset of the broader returned JMA catalog for the specified date range, rather than a current-date-derived or 2026-only default.

# Catalog Distribution Figure

Figure <a href="#fig:distribution" data-reference-type="ref" data-reference="fig:distribution">1</a> is the required distribution figure generated from the final cleaned CSV. It provides visual validation of the Sanriku spatial bounds, hypocentral depth distribution, and temporal clustering over the requested interval.

<figure id="fig:distribution" data-latex-placement="H">
<img src="\detokenize{<CASE_ROOT>/run/00_catalog_download/exp_run/outputs/01_download_validate_sanriku_jma_catalog/Snet_catalog_20250601_20260502_distribution.png}" style="width:98.0%" />
<figcaption>Distribution of the cleaned Hi-net/JMA Sanriku catalog for 2025-06-01 <span class="math inline"> ≤ <em>t</em>&lt;</span> 2026-05-02. The left panel maps hypocenters within the Sanriku bounds, colored by depth, with a red rectangle marking the inclusive selection box. The right panel shows 7-day event counts for the 33,711 retained events.</figcaption>
</figure>

The left panel of Figure <a href="#fig:distribution" data-reference-type="ref" data-reference="fig:distribution">1</a> spans approximately 141.0–144.5°E and 38.5–42.5°N and displays events throughout the red Sanriku bounding rectangle. Events are colored by depth from approximately 0 to 150 km. The visible distribution includes dense offshore-to-nearshore clusters, especially around 142–143.5°E and 39–42°N. Deeper events appear more common toward the western part of the mapped domain, while shallower events are widespread across central and eastern portions of the selection box.

The right panel of Figure <a href="#fig:distribution" data-reference-type="ref" data-reference="fig:distribution">1</a> summarizes temporal occurrence using 7-day bins. The event rate is not uniform through time: many bins contain several hundred events, but late 2025 includes a prominent burst exceeding 3,000 events per 7 days, and another large increase occurs around April 2026. This temporal clustering should be considered in downstream rate-based analyses, model training, or validation workflows.

# Requirement Compliance

Table <a href="#tab:compliance" data-reference-type="ref" data-reference="tab:compliance">6</a> compares the requested workflow requirements with the implemented and validated behavior.

<div id="tab:compliance">

| Requirement | Evidence of compliance |
|:---|:---|
| Requirement | Evidence of compliance |
| Use NIED Hi-net login and JMA catalog endpoints | Validation JSON records the requested login endpoint <https://hinetwww11.bosai.go.jp/auth/?LANG=en> and catalog endpoint <https://hinetwww11.bosai.go.jp/auth/JMA/jmalist.php>. |
| Read credentials from requested `.env`, with command-line overrides allowed | Validation JSON records `credential_source: .env`; implementation summary confirms override support. Credential values are not exposed in this report. |
| Use `requests.Session` | Implementation evidence confirms session-based authenticated requests. |
| Add retry and backoff | Implementation evidence confirms a retry/backoff request wrapper. |
| Save failed unparseable HTML responses to debug/raw files | Implemented; no parse-failure files were generated because all 48 chunks parsed successfully. Login/debug HTML files were saved. |
| Use manuscript-aligned interval, not a current-date or 2026-only default | Validation records start date 2025-06-01 and exclusive end date 2026-05-02; cleaned catalog spans 2025-06-01 00:09:02.360000 to 2026-05-01 23:58:44.740000. |
| Treat end date as exclusive | The final chunk is 2026-04-26 to 2026-05-02 exclusive and submitted service end date 2026-05-01. |
| Apply Sanriku bounds inclusively after parsing | Cleaning audit shows 270,338 parsed records were reduced to 33,711 after spatial filtering; final latitude and longitude ranges are exactly within 38.5–42.5°N and 141.0–144.5°E. |
| Split requests into chunks no longer than 7 days | Manifest records 48 chunks, with 47 chunks of 7 days and one final chunk of 6 days. |
| Record exact chunk boundaries and actual returned dates | Chunk manifest includes half-open chunk boundaries, submitted service dates, actual returned datetime minima and maxima, and retained Sanriku datetime ranges for each chunk. |
| Output ASPECT-ready CSV with exactly `datetime,lat,lon,dep,mag` | Delivered CSV at <a href="<CASE_ROOT>/run/00_catalog_download/exp_run/outputs/01_download_validate_sanriku_jma_catalog/Snet_catalog_20250601_20260502.csv" class="uri"><CASE_ROOT>/run/00_catalog_download/exp_run/outputs/01_download_validate_sanriku_jma_catalog/Snet_catalog_20250601_20260502.csv</a>; validation confirms exactly the required columns. |
| Use filename pattern `Snet_catalog_YYYYMMDD_YYYYMMDD.csv` | Delivered file is `Snet_catalog_20250601_20260502.csv`. |
| Generate catalog distribution figure | Figure generated at <a href="<CASE_ROOT>/run/00_catalog_download/exp_run/outputs/01_download_validate_sanriku_jma_catalog/Snet_catalog_20250601_20260502_distribution.png" class="uri"><CASE_ROOT>/run/00_catalog_download/exp_run/outputs/01_download_validate_sanriku_jma_catalog/Snet_catalog_20250601_20260502_distribution.png</a> and shown in Figure <a href="#fig:distribution" data-reference-type="ref" data-reference="fig:distribution">1</a>. |

Compliance of the implementation with the requested catalog workflow requirements.

</div>

# Limitations and Assumptions

The workflow meets the requested implementation and validation objectives, but several limitations should accompany any scientific use of the delivered catalog:

- **Authenticated external dependency.** Reproduction requires valid NIED Hi-net credentials and continued availability of the login and catalog endpoints. Future downloads may be affected by credential access, endpoint changes, service availability, or catalog revisions by the provider.

- **Catalog completeness not independently evaluated.** Validation confirms successful download, parsing, cleaning, and regional filtering, but it does not independently assess the completeness, detection threshold, or scientific quality of the JMA unified hypocenter catalog. The reported magnitude range is 0.0–7.7, but the magnitude of completeness may vary in space, time, and especially following large sequences.

- **Limited ASPECT schema.** The required output schema contains only `datetime,lat,lon,dep,mag`. Uncertainty fields, phase counts, location quality metrics, and other catalog metadata were not retained in the ASPECT-ready CSV.

- **No full raw per-chunk response archive in this execution.** The implementation supports an optional raw-output directory, but it was not used for this run. The chunk manifest and validation JSON provide strong auditability, and login/debug HTML files were saved, but the original raw catalog response for every successful chunk is not archived here.

- **Temporal clustering affects downstream analyses.** The validated catalog contains strong event-rate bursts in late 2025 and around April 2026. Any downstream seismicity-rate, hazard, or machine-learning application should consider whether clustered sequences require declustering, weighting, or separate treatment.

- **Distribution figure is diagnostic, not exhaustive.** The figure validates spatial, depth, and temporal behavior, but it does not include magnitude-frequency analysis, completeness estimation, or uncertainty diagnostics.

- **Physical sanity filter documented.** A physical sanity filter was applied after spatial filtering and removed zero rows. This does not affect the delivered catalog but should be recognized as an additional quality-control step.

# Conclusion

A complete authenticated NIED Hi-net/JMA unified hypocenter catalog workflow was implemented and validated for the Sanriku, northeast Japan study region. The workflow used the required endpoints, read credentials from the intended source for this run, maintained an authenticated session, used retry/backoff network handling, parsed the fixed-width JMA table, enforced a half-open date interval of 2025-06-01 to 2026-05-02, split requests into 7-day-or-shorter chunks, applied inclusive Sanriku spatial bounds after parsing, and generated both a cleaned ASPECT-ready CSV and a diagnostic distribution figure.

The primary scientific output is the cleaned catalog at <a href="<CASE_ROOT>/run/00_catalog_download/exp_run/outputs/01_download_validate_sanriku_jma_catalog/Snet_catalog_20250601_20260502.csv" class="uri"><CASE_ROOT>/run/00_catalog_download/exp_run/outputs/01_download_validate_sanriku_jma_catalog/Snet_catalog_20250601_20260502.csv</a>. It contains 33,711 events with exactly `datetime,lat,lon,dep,mag`, spans 2025-06-01 00:09:02.360000 through 2026-05-01 23:58:44.740000, has depths from 0.0 to 149.2 km and magnitudes from 0.0 to 7.7, and contains no missing required values or duplicate ASPECT rows. The chunk manifest at <a href="<CASE_ROOT>/run/00_catalog_download/exp_run/outputs/01_download_validate_sanriku_jma_catalog/Snet_catalog_20250601_20260502_chunk_manifest.csv" class="uri"><CASE_ROOT>/run/00_catalog_download/exp_run/outputs/01_download_validate_sanriku_jma_catalog/Snet_catalog_20250601_20260502_chunk_manifest.csv</a> verifies that all 48 chunks succeeded and parsed correctly, with no request exceeding the 7-day limit. The distribution figure in Figure <a href="#fig:distribution" data-reference-type="ref" data-reference="fig:distribution">1</a> confirms the regional spatial selection and highlights important temporal clustering that should be considered in subsequent analyses.
