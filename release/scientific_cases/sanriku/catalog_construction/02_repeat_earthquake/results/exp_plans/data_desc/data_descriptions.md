# Data Descriptions
## base_path
**Source path**: `<WAVEFORM_DATA_ROOT>`
### Summary
This dataset is a pre-organized repeat-earthquake input package for 2025-11-01 to 2025-11-15, centered on metadata tables plus SAC waveform paths. For the requested 2025-11-01 to 2025-12-06 window, the main analysis entry point is `metadata/observations.csv`, which contains 139,992 event-station-component records across 2,581 events, with absolute SAC paths, event/station metadata, and P/S pick timing fields needed for phase-aligned waveform extraction; `metadata/event_pair_common_observations.csv` provides precomputed event-pair overlap statistics for efficient candidate screening.
### Detail
#### Folder Structure

Root directory: `<WAVEFORM_DATA_ROOT>`

Top-level contents observed:
- `metadata/` — primary tables for events, stations, per-trace observations, pairwise shared-observation counts, and phase arrivals.
- `waveforms/` — SAC files referenced by metadata.
- `selections/` — present but not inspected in detail.
- `README.md`, `dataset_summary.json` — package-level documentation/summaries.

Relevant waveform organization actually present:
- `waveforms/events/YYYYMMDD/D{evid}_20/*.SAC`
- `waveforms/supplements/YYYYMMDD/D{evid}_20/*.SAC`

Important note for future agents:
- The user guidance mentions `waveforms/by_date/...`, but this path was not present in the inspected package.
- Use `metadata/observations.csv` column `sac_file` as the authoritative locator for SAC files rather than assuming a fixed folder pattern.

Example waveform paths from `observations.csv`:
- `<WAVEFORM_DATA_ROOT>/waveforms/events/20251106/D20251106000003_20/E.SOB3.XH.SAC`
- `<WAVEFORM_DATA_ROOT>/waveforms/events/20251106/D20251106000003_20/E.SOB3.XL.SAC`

#### Key Metadata Files

Primary files under `metadata/`:
- `observations.csv` (`114,668,174` bytes)
- `event_pair_common_observations.csv` (`623,192,542` bytes)
- `events.csv` (`314,223` bytes)
- `stations.csv` (`19,093` bytes)

Other related files present:
- `observations.csv.gz`
- `event_pair_common_observations.csv.gz`
- `observations_continuous_supplement_20251106_20251112_all_events.csv`
- `phase_arrivals.csv`
- `waveforms.csv`
- `metadata_summary.json`
- `README.md`
- `archive/`

#### Main Analysis Entry: `metadata/observations.csv`

This is the most important table for future repeat-event workflows. One row corresponds to one event-station-component waveform, already combining original event waveforms and continuous SAC supplements.

Full dataset profile:
- Rows: `156,360`
- Unique events: `3,055`
- Unique stations: `328`
- Unique station-components: `1,005`
- Origin time range: `2025-11-01 00:19:06` to `2025-11-14 23:24:44`

Requested time window subset (`2025-11-01T00:00:00 <= origin_time < 2025-12-07T00:00:00`):
- Rows: `139,992`
- Unique events: `2,581`
- Unique stations: `325`

Most relevant columns for future agents:
- Event metadata:
  - `evid`
  - `origin_time`
  - `event_date`
  - `event_latitude`
  - `event_longitude`
  - `event_depth_km`
  - `event_magnitude`
  - `event_dir`
- Station / trace identity:
  - `station_id`
  - `network`
  - `station_code`
  - `station_latitude`
  - `station_longitude`
  - `station_elevation_m`
  - `component`
  - `station_component`
- SAC path / availability:
  - `sac_name`
  - `sac_file`
  - `exists`
  - `observation_source`
- Pick and timing fields:
  - `has_p_pick`
  - `has_s_pick`
  - `p_pick_time_utc`
  - `s_pick_time_utc`
  - `p_time_after_origin_s`
  - `s_time_after_origin_s`
  - `p_quality`
  - `s_quality`
  - `weight`
- Trace/window metadata, especially useful for supplement records:
  - `origin_pre_s`
  - `origin_post_s`
  - `window_start_after_origin_s`
  - `window_end_after_origin_s`
  - `window_template_sac`
  - `window_mode_used`
  - `sampling_rate_hz`
  - `npts`
  - `start_time`
  - `end_time`
- Additional provenance / matching fields:
  - `travel_time_raw_event_id`
  - `regional_event_id`
  - `regional_origin_time_utc`
  - `match_time_error_s`
  - `source_pick_station_code`
  - `source_daily_sac`
  - `source`
  - `source_file`

#### `observations.csv` Organization Notes

Waveform source mix within the requested time window:
- `continuous_sac_daily`: `108,885` rows
- `event_waveform`: `31,107` rows

SAC path existence in the requested window:
- `exists = True`: `139,992`
- No missing-file rows were seen in this subset.

Pick coverage in the requested window:
- `has_p_pick = True`: `110,469`
- `has_p_pick = False`: `29,523`
- `has_s_pick = True`: `79,191`
- `has_s_pick = False`: `60,801`

This indicates:
- P picks are more complete than S picks.
- The table supports the recommended baseline strategy of preferring S-aligned windows and falling back to P where needed.

Sampling metadata in the requested window:
- `sampling_rate_hz = 100.0`: `101,460` rows
- `sampling_rate_hz = NaN`: `38,532` rows

Interpretation:
- Many supplement-based records include explicit sample metadata.
- A substantial subset lacks populated `sampling_rate_hz/npts/start_time/end_time` fields in the CSV, so future agents may need to read SAC headers directly for authoritative trace stats where these fields are null.

Most common components in the requested window:
- `VX`, `VY`, `VZ`: `36,295` each
- `E`: `5,574`
- `N`: `5,574`
- `U`: `5,537`
- `XH`, `XL`, `YH`, `YL`, `ZH`, `ZL`: `2,037` each
- `X`, `Y`, `Z`: `657` each
- Small counts of `sU`, `sE`, `sN`, `sY`, `V`

Representative `station_component` values:
- `E.SOB3.XH`
- `E.SOB3.XL`
- `E.SOB3.YH`
- `E.SOB3.YL`
- `E.SOB3.ZH`
- `E.SOB3.ZL`
- `N.KKWH.E`
- `N.KKWH.N`
- `N.KKWH.U`
- `N.KMIH.E`
- `N.KMIH.N`
- `N.KMIH.U`

Important implication for loading/matching:
- The dataset mixes channel naming conventions (`E/N/U`, `X/Y/Z`, `XH/XL/YH/YL/ZH/ZL`, `VX/VY/VZ`, etc.).
- Exact matching by original `station_component` is feasible and consistent with the requested baseline; future agents should not assume a single 3-component convention.

#### Candidate Pair Entry: `metadata/event_pair_common_observations.csv`

This is the precomputed pair-screening table for shared observations and pairwise event geometry.

Dataset profile:
- Rows: `3,202,387`
- Rows with both events inside requested window: `2,890,580`

Columns observed:
- `event_i`
- `event_j`
- `common_station_components`
- `common_stations`
- `hypocentral_distance_km`
- `horizontal_distance_km`
- `depth_distance_km`
- `magnitude_diff`
- `time_separation_s`
- `origin_i`
- `lat_i`
- `lon_i`
- `dep_i_km`
- `mag_i`
- `origin_j`
- `lat_j`
- `lon_j`
- `dep_j_km`
- `mag_j`

Why this file matters:
- It already contains the exact screening fields emphasized in the task request: shared observation counts, horizontal distance, depth difference, magnitude difference, and time separation.
- It should be the efficient first-stage filter before any SAC reading or correlation.

Example rows indicate large shared-coverage event pairs, e.g.:
- `common_station_components` in the 400+ range
- `common_stations` around 140+
- `horizontal_distance_km`, `depth_distance_km`, `magnitude_diff`, and `time_separation_s` precomputed

#### Supporting Event Table: `metadata/events.csv`

This is a compact per-event summary table.

Columns:
- `evid`
- `origin_time`
- `event_date`
- `latitude`
- `longitude`
- `depth_km`
- `magnitude`
- `n_sac_files`
- `n_observed_stations`
- `n_components`
- `components`
- `analysis_ready`

Use cases:
- Fast event-level filtering and plotting without expanding the observation table.
- Quick checks of per-event waveform richness and component availability.

Example content shows:
- `analysis_ready` boolean exists.
- `components` is a comma-separated list such as `E,N,U,X,Y,Z,sE,sN,sU`.

#### Supporting Station Table: `metadata/stations.csv`

This is a station inventory / summary table.

Columns:
- `station_id`
- `network`
- `station_code`
- `latitude`
- `longitude`
- `elevation_m`
- `trace_count`
- `event_count`
- `component_count`
- `components`

Use cases:
- Station map context.
- Diagnosing which stations have many traces and which component sets each station supports.

Example station patterns:
- `E.SOB1` / `E.SOB2` with `XH,XL,YH,YL,ZH,ZL`
- Mixed land/ocean-bottom style component sets are present.

#### Time-Window-Relevant Coverage

For the requested analysis window (`2025-11-01` to `2025-12-06` inclusive of start, exclusive of `2025-12-07`):
- Event coverage is dense: `2,581` events in `observations.csv`
- Pair table coverage is very large: `2,890,580` event pairs with both origins inside the window
- Stations remain broad: `325` unique stations in-window
- All inspected in-window observation rows point to existing SAC files

This means future agents can likely perform the entire candidate-generation and waveform-access workflow using only local metadata and local SAC files, without any data acquisition or restructuring.

#### Naming Conventions and Access Patterns

Event directory naming:
- Event folders use pattern `D{evid}_20`
- Example: `D20251106000003_20`

Station/component SAC naming:
- SAC files use pattern `{station_component}.SAC` where `station_component` may itself include a network/station prefix and a component code.
- Examples:
  - `E.SOB3.XH.SAC`
  - `ICHINM.E.SAC`

Recommended access pattern:
1. Filter event-time range in `metadata/observations.csv` and/or `metadata/event_pair_common_observations.csv`.
2. Use `event_pair_common_observations.csv` for pairwise prescreening.
3. Join back to `observations.csv` on `evid` to retrieve shared `station_component` rows and their `sac_file` paths.
4. Use `sac_file` directly for waveform loading.

#### Potential Data Caveats

- `sampling_rate_hz`, `npts`, `start_time`, and `end_time` are not fully populated for all observation rows; some rows contain `NaN`.
- `network` can be null in some `observations.csv` rows even when `station_id` and `station_component` are usable.
- Component naming is heterogeneous; exact `station_component` matching is preferable to heuristic channel merging.
- The package contains both event-cut and continuous-supplement traces under a unified observation table; `observation_source` should be retained for provenance.

#### Minimal File Inventory for Future Agents

Use these first:
- `metadata/observations.csv` — authoritative event-station-component waveform index with SAC paths and phase picks
- `metadata/event_pair_common_observations.csv` — authoritative precomputed event-pair overlap and geometry table

Useful supporting tables:
- `metadata/events.csv` — compact per-event summary
- `metadata/stations.csv` — compact per-station summary

Optional supplementary references present but not deeply profiled here:
- `metadata/phase_arrivals.csv`
- `metadata/waveforms.csv`
- `metadata/observations_continuous_supplement_20251106_20251112_all_events.csv`

#### Practical Loading Guidance

For future coding agents, the most relevant fields to prioritize are:
- In `observations.csv`: `evid`, `origin_time`, `station_component`, `sac_file`, `exists`, `has_p_pick`, `has_s_pick`, `p_time_after_origin_s`, `s_time_after_origin_s`, `observation_source`
- In `event_pair_common_observations.csv`: `event_i`, `event_j`, `common_station_components`, `common_stations`, `horizontal_distance_km`, `depth_distance_km`, `magnitude_diff`, `time_separation_s`

These fields are sufficient to locate waveforms, verify availability, align by P/S pick relative to event origin time, and pre-screen event pairs before any computationally expensive trace processing.

------------------------------

## waveforms_by_date
**Source path**: `<WAVEFORM_DATA_ROOT>/waveforms/by_date/YYYYMMDD/D{evid}_20/*.SAC`
### Summary
This package is a prebuilt SAC waveform and metadata dataset for repeat-earthquake workflows over 2025-11-01 to 2025-11-15. The key entry point is `metadata/observations.csv`, which indexes per-event, per-station-component SAC files with event/station metadata and P/S picks; `metadata/event_pair_common_observations.csv` provides pairwise overlap and geometry fields for efficient candidate screening in the 2025-11-01 to 2025-12-06 window.
### Detail
#### Folder Structure

Base path:
`<WAVEFORM_DATA_ROOT>`

Observed top-level layout:
- `metadata/` — main CSV tables and small JSON summaries
- `waveforms/` — SAC waveform files
- `selections/` — auxiliary directory present but not profiled in detail
- `README.md`
- `dataset_summary.json`

Observed waveform subdirectories:
- `waveforms/events/YYYYMMDD/D{evid}_20/*.SAC`
- `waveforms/supplements/YYYYMMDD/D{evid}_20/*.SAC`

Important access note:
- Although the prompt references `waveforms/by_date/YYYYMMDD/D{evid}_20/*.SAC`, that path was not present in the inspected dataset.
- Future agents should use `metadata/observations.csv` field `sac_file` as the authoritative waveform locator rather than assuming a fixed waveform directory convention.

Example SAC paths from metadata:
- `<WAVEFORM_DATA_ROOT>/waveforms/events/20251106/D20251106000003_20/E.SOB3.XH.SAC`
- `<WAVEFORM_DATA_ROOT>/waveforms/events/20251106/D20251106000003_20/E.SOB3.XL.SAC`
- `<WAVEFORM_DATA_ROOT>/waveforms/events/20251106/D20251106000003_20/E.SOB3.YH.SAC`

#### Relevant Metadata Files

Most relevant files under `metadata/`:
- `observations.csv` — main per-event/station/component waveform index
- `event_pair_common_observations.csv` — precomputed pairwise shared-observation and geometry table
- `events.csv` — per-event summary table
- `stations.csv` — per-station summary table

Other related files present:
- `observations.csv.gz`
- `event_pair_common_observations.csv.gz`
- `observations_continuous_supplement_20251106_20251112_all_events.csv`
- `phase_arrivals.csv`
- `waveforms.csv`
- `metadata_summary.json`
- `phase_arrivals_summary.json`
- `README.md`
- `archive/`

#### `observations.csv` — Main Analysis Entry

This table is the primary entry point for waveform-based repeat-event workflows. One row represents one event-station-component SAC waveform, already combining original event waveform products and continuous-SAC supplement products.

Full-table size and coverage:
- File size: `114,668,174` bytes
- Rows: `156,360`
- Unique events: `3,055`
- Unique stations: `328`
- Unique station-components: `1,005`
- Origin-time range: `2025-11-01 00:19:06` to `2025-11-14 23:24:44`

Requested time window subset (`2025-11-01T00:00:00 <= origin_time < 2025-12-07T00:00:00`):
- Rows: `139,992`
- Unique events: `2,581`
- Unique stations: `325`

Most relevant columns for future agents:
- Event identity and location:
  - `evid`
  - `origin_time`
  - `event_date`
  - `event_latitude`
  - `event_longitude`
  - `event_depth_km`
  - `event_magnitude`
  - `event_dir`
- Station and component identity:
  - `station_id`
  - `network`
  - `station_code`
  - `station_latitude`
  - `station_longitude`
  - `station_elevation_m`
  - `component`
  - `station_component`
- Waveform location and provenance:
  - `sac_name`
  - `sac_file`
  - `exists`
  - `observation_source`
  - `source_file`
- P/S arrival information:
  - `has_p_pick`
  - `has_s_pick`
  - `p_pick_time_utc`
  - `s_pick_time_utc`
  - `p_time_after_origin_s`
  - `s_time_after_origin_s`
  - `p_quality`
  - `s_quality`
  - `weight`
- Supplement/matching metadata:
  - `travel_time_raw_event_id`
  - `regional_event_id`
  - `regional_origin_time_utc`
  - `match_time_error_s`
  - `source_pick_station_code`
  - `source_daily_sac`
  - `source`
- Window/trace metadata:
  - `origin_pre_s`
  - `origin_post_s`
  - `window_start_after_origin_s`
  - `window_end_after_origin_s`
  - `window_template_sac`
  - `window_mode_used`
  - `sampling_rate_hz`
  - `npts`
  - `start_time`
  - `end_time`
- Station coverage summary fields on each row:
  - `station_number`
  - `n_waveform_components`
  - `waveform_components`
  - `station_trace_count`
  - `station_event_count`
  - `station_component_count`
  - `station_components_available`

#### `observations.csv` Content Patterns Relevant to Repeat-Event Work

In-window waveform source mix:
- `continuous_sac_daily`: `108,885` rows
- `event_waveform`: `31,107` rows

Implication:
- The merged table already integrates both event-based and continuous supplement traces needed for downstream waveform comparison.

In-window SAC path availability:
- `exists = True`: `139,992`
- No missing paths were encountered in the inspected in-window subset.

In-window pick coverage:
- `has_p_pick = True`: `110,469`
- `has_p_pick = False`: `29,523`
- `has_s_pick = True`: `79,191`
- `has_s_pick = False`: `60,801`

Implication:
- P picks are more complete than S picks.
- The metadata supports a workflow that prefers S-aligned processing and falls back to P where S is absent.

In-window `sampling_rate_hz` distribution:
- `100.0`: `101,460`
- `NaN`: `38,532`

Implication:
- Many rows already include explicit sample-rate metadata.
- Some rows lack populated trace stats in CSV form, so future agents may need to read SAC headers directly when `sampling_rate_hz`, `npts`, `start_time`, or `end_time` are missing.

Most common in-window components:
- `VX`: `36,295`
- `VY`: `36,295`
- `VZ`: `36,295`
- `N`: `5,574`
- `E`: `5,574`
- `U`: `5,537`
- `XL`: `2,037`
- `XH`: `2,037`
- `ZL`: `2,037`
- `ZH`: `2,037`
- `YH`: `2,037`
- `YL`: `2,037`
- `X`: `657`
- `Y`: `657`
- `Z`: `657`
- smaller counts for `sU`, `sE`, `sN`, `sY`, `V`

Representative `station_component` examples:
- `E.SOB3.XH`
- `E.SOB3.XL`
- `E.SOB3.YH`
- `E.SOB3.YL`
- `E.SOB3.ZH`
- `E.SOB3.ZL`
- `N.KKWH.E`
- `N.KKWH.N`
- `N.KKWH.U`
- `N.KMIH.E`
- `N.KMIH.N`
- `N.KMIH.U`

Important interpretation for future agents:
- Channel naming is heterogeneous across stations (`E/N/U`, `X/Y/Z`, `XH/XL/YH/YL/ZH/ZL`, `VX/VY/VZ`, etc.).
- Exact matching on original `station_component` is supported and is the safest baseline for future waveform pairing.

#### `event_pair_common_observations.csv` — Pair Prescreening Table

This file is the key pairwise metadata table for candidate selection before any waveform reads.

Profile:
- File size: `623,192,542` bytes
- Rows: `3,202,387`
- Rows with both events inside the requested 2025-11-01 to 2025-12-06 window: `2,890,580`

Columns:
- `event_i`
- `event_j`
- `common_station_components`
- `common_stations`
- `hypocentral_distance_km`
- `horizontal_distance_km`
- `depth_distance_km`
- `magnitude_diff`
- `time_separation_s`
- `origin_i`
- `lat_i`
- `lon_i`
- `dep_i_km`
- `mag_i`
- `origin_j`
- `lat_j`
- `lon_j`
- `dep_j_km`
- `mag_j`

Why this is especially relevant:
- It already contains the exact pair-filtering attributes prioritized in the request: shared observation counts, horizontal distance, depth difference, magnitude difference, and time separation.
- It allows efficient prescreening without first materializing station-component overlaps from raw observations.

Example value pattern seen in sample rows:
- `common_station_components` can exceed `400`
- `common_stations` can exceed `140`
- `horizontal_distance_km`, `depth_distance_km`, and `magnitude_diff` are already precomputed per pair

#### `events.csv` — Event Summary Table

This is a compact event-level inventory useful for plotting and quick event filtering.

Columns:
- `evid`
- `origin_time`
- `event_date`
- `latitude`
- `longitude`
- `depth_km`
- `magnitude`
- `n_sac_files`
- `n_observed_stations`
- `n_components`
- `components`
- `analysis_ready`

Observed content characteristics:
- `components` is a comma-separated per-event component summary, e.g. `E,N,U,X,Y,Z,sE,sN,sU`
- `analysis_ready` is a boolean-like readiness flag

Use cases:
- Fast event scatter maps
- Event counts and per-event waveform availability checks
- Quick lookup of magnitude/location without expanding `observations.csv`

#### `stations.csv` — Station Summary Table

This is a compact station inventory / usage summary.

Columns:
- `station_id`
- `network`
- `station_code`
- `latitude`
- `longitude`
- `elevation_m`
- `trace_count`
- `event_count`
- `component_count`
- `components`

Observed content characteristics:
- Stations can have multi-channel sets such as `XH,XL,YH,YL,ZH,ZL`
- `trace_count` and `event_count` summarize station usage across the package

Use cases:
- Station maps and diagnostics
- Ranking stations by data availability
- Understanding per-station component conventions before waveform matching

#### Time-Window-Relevant Coverage Summary

For `2025-11-01` through `2025-12-06`:
- `observations.csv` contains `139,992` waveform-index rows
- These rows span `2,581` unique events and `325` unique stations
- `event_pair_common_observations.csv` contains `2,890,580` event pairs where both events fall in the requested window
- All inspected in-window observations had `exists=True`

This indicates the package is already sufficiently assembled for local repeat-event workflows based on metadata joins plus SAC reads.

#### Naming Conventions

Event folder naming:
- `D{evid}_20`
- Example: `D20251106000003_20`

Waveform file naming:
- Typically `{station_component}.SAC`
- Examples:
  - `E.SOB3.XH.SAC`
  - `ICHINM.E.SAC`

Station identifiers:
- `station_id` may include network prefix, e.g. `E.SOB1`
- `station_component` extends this with component, e.g. `E.SOB1.XH`

#### Recommended Loading Path for Future Agents

Use these tables in this order:
1. `metadata/event_pair_common_observations.csv`
   - Filter event pairs by time window and pairwise metadata fields.
2. `metadata/observations.csv`
   - Retrieve per-event shared `station_component` rows and SAC paths.
3. `metadata/events.csv` / `metadata/stations.csv`
   - Use for lightweight summaries, plotting support, and diagnostics.

Most important fields to keep when subsetting:
- From `observations.csv`:
  - `evid`, `origin_time`, `station_component`, `sac_file`, `exists`, `observation_source`, `has_p_pick`, `has_s_pick`, `p_time_after_origin_s`, `s_time_after_origin_s`, `event_latitude`, `event_longitude`, `event_depth_km`, `event_magnitude`, `station_latitude`, `station_longitude`
- From `event_pair_common_observations.csv`:
  - `event_i`, `event_j`, `common_station_components`, `common_stations`, `horizontal_distance_km`, `depth_distance_km`, `magnitude_diff`, `time_separation_s`, `origin_i`, `origin_j`

#### Data Caveats for Future Agents

- Do not assume `waveforms/by_date/...` exists; rely on `sac_file`.
- Some rows have null `sampling_rate_hz`, `npts`, `start_time`, or `end_time`; direct SAC header reads may still be needed.
- `network` can be null in some `observations.csv` rows even when `station_id` and `station_component` are valid.
- The dataset mixes multiple component naming schemes; avoid implicit component merging unless explicitly intended.
- The merged observation table includes both original event waveforms and supplement traces; preserve `observation_source` for provenance-aware processing.

------------------------------

## waveforms_supplements
**Source path**: `<WAVEFORM_DATA_ROOT>/waveforms/supplements/YYYYMMDD/D{evid}_20/*.SAC`
### Summary
This directory is a preassembled SAC waveform dataset with supporting metadata for repeat-earthquake screening over 2025-11-01 to 2025-11-15. For the target window 2025-11-01 to 2025-12-06, `metadata/observations.csv` is the authoritative waveform index with per-trace event/station metadata, SAC paths, and P/S picks, while `metadata/event_pair_common_observations.csv` provides precomputed shared-observation and geometry metrics for event-pair filtering.
### Detail
#### Folder Structure

Base directory:
`<WAVEFORM_DATA_ROOT>`

Observed top-level contents:
- `metadata/`
- `waveforms/`
- `selections/`
- `README.md`
- `dataset_summary.json`

Observed waveform layout relevant to future agents:
- `waveforms/events/YYYYMMDD/D{evid}_20/*.SAC`
- `waveforms/supplements/YYYYMMDD/D{evid}_20/*.SAC`

Important access guidance:
- The user prompt references `waveforms/by_date/...`, but that directory pattern was not present in the inspected package.
- Future agents should read waveform files via `metadata/observations.csv` column `sac_file`, not by assuming a single directory schema.

Example waveform paths referenced by metadata:
- `<WAVEFORM_DATA_ROOT>/waveforms/events/20251106/D20251106000003_20/E.SOB3.XH.SAC`
- `<WAVEFORM_DATA_ROOT>/waveforms/events/20251106/D20251106000003_20/E.SOB3.XL.SAC`
- `<WAVEFORM_DATA_ROOT>/waveforms/events/20251106/D20251106000003_20/E.SOB3.YH.SAC`

#### Key Metadata Files

Primary metadata files under `metadata/`:
- `observations.csv` — per event-station-component waveform index
- `event_pair_common_observations.csv` — precomputed event-pair overlap and geometry table
- `events.csv` — event summary inventory
- `stations.csv` — station summary inventory

Other related files present:
- `observations.csv.gz`
- `event_pair_common_observations.csv.gz`
- `observations_continuous_supplement_20251106_20251112_all_events.csv`
- `phase_arrivals.csv`
- `waveforms.csv`
- `metadata_summary.json`
- `phase_arrivals_summary.json`
- `README.md`
- `archive/`

#### `observations.csv` — Main Waveform Index

This is the main entry point for future agents. Each row corresponds to one event-station-component SAC waveform and includes merged records from original event waveforms and continuous waveform supplements.

Dataset profile:
- File size: `114,668,174` bytes
- Rows: `156,360`
- Unique events: `3,055`
- Unique stations: `328`
- Unique station-components: `1,005`
- Time coverage: `2025-11-01 00:19:06` to `2025-11-14 23:24:44`

Requested analysis window subset (`2025-11-01T00:00:00 <= origin_time < 2025-12-07T00:00:00`):
- Rows: `139,992`
- Unique events: `2,581`
- Unique stations: `325`

Columns observed in `observations.csv`:
- `evid`
- `origin_time`
- `event_date`
- `event_latitude`
- `event_longitude`
- `event_depth_km`
- `event_magnitude`
- `event_dir`
- `station_id`
- `network`
- `station_code`
- `station_latitude`
- `station_longitude`
- `station_elevation_m`
- `component`
- `station_component`
- `sac_name`
- `sac_file`
- `exists`
- `observation_source`
- `has_p_pick`
- `has_s_pick`
- `p_pick_time_utc`
- `s_pick_time_utc`
- `p_time_after_origin_s`
- `s_time_after_origin_s`
- `p_quality`
- `s_quality`
- `weight`
- `travel_time_raw_event_id`
- `station_number`
- `n_waveform_components`
- `waveform_components`
- `source_file`
- `station_trace_count`
- `station_event_count`
- `station_component_count`
- `station_components_available`
- `regional_event_id`
- `regional_origin_time_utc`
- `match_time_error_s`
- `source_pick_station_code`
- `source_daily_sac`
- `source`
- `origin_pre_s`
- `origin_post_s`
- `window_start_after_origin_s`
- `window_end_after_origin_s`
- `window_template_sac`
- `window_mode_used`
- `sampling_rate_hz`
- `npts`
- `start_time`
- `end_time`

#### Fields Most Relevant to Repeat-Event Work

The most directly useful fields for future agents are:
- Event info:
  - `evid`, `origin_time`, `event_latitude`, `event_longitude`, `event_depth_km`, `event_magnitude`
- Station/component identity:
  - `station_id`, `station_component`, `component`, `station_latitude`, `station_longitude`
- Waveform file access:
  - `sac_file`, `exists`, `sac_name`, `observation_source`
- Phase timing:
  - `has_p_pick`, `has_s_pick`, `p_pick_time_utc`, `s_pick_time_utc`, `p_time_after_origin_s`, `s_time_after_origin_s`
- Optional trace/window metadata:
  - `sampling_rate_hz`, `npts`, `start_time`, `end_time`, `window_mode_used`, `window_start_after_origin_s`, `window_end_after_origin_s`

These fields are sufficient to:
- subset the requested time range,
- find the shared station-components between events,
- load the corresponding SAC files,
- and interpret phase times relative to event origin time.

#### `observations.csv` Coverage and Quality Indicators

In the requested window:
- `exists = True` for all `139,992` inspected rows
- `observation_source` distribution:
  - `continuous_sac_daily`: `108,885`
  - `event_waveform`: `31,107`

Pick availability in the requested window:
- `has_p_pick = True`: `110,469`
- `has_p_pick = False`: `29,523`
- `has_s_pick = True`: `79,191`
- `has_s_pick = False`: `60,801`

Implications:
- P picks are more complete than S picks.
- The table supports a strategy that prefers S picks where available and falls back to P picks when necessary.

Trace metadata availability in the requested window:
- `sampling_rate_hz = 100.0`: `101,460`
- `sampling_rate_hz = NaN`: `38,532`

Implication:
- Not all waveform rows have complete trace metadata populated in CSV form, so future agents may need to inspect SAC headers directly for some traces.

#### Component and Station-Component Patterns

Most frequent in-window `component` values:
- `VX`: `36,295`
- `VY`: `36,295`
- `VZ`: `36,295`
- `N`: `5,574`
- `E`: `5,574`
- `U`: `5,537`
- `XL`: `2,037`
- `XH`: `2,037`
- `ZL`: `2,037`
- `ZH`: `2,037`
- `YH`: `2,037`
- `YL`: `2,037`
- `X`: `657`
- `Y`: `657`
- `Z`: `657`
- smaller counts of `sU`, `sE`, `sN`, `sY`, `V`

Representative `station_component` examples:
- `E.SOB3.XH`
- `E.SOB3.XL`
- `E.SOB3.YH`
- `E.SOB3.YL`
- `E.SOB3.ZH`
- `E.SOB3.ZL`
- `N.KKWH.E`
- `N.KKWH.N`
- `N.KKWH.U`
- `N.KMIH.E`
- `N.KMIH.N`
- `N.KMIH.U`

Practical implication:
- Channel naming is heterogeneous, including `E/N/U`, `X/Y/Z`, `XH/XL/YH/YL/ZH/ZL`, and `VX/VY/VZ`.
- Exact `station_component` matching is therefore the most reliable way to identify common observations between events.

#### `event_pair_common_observations.csv` — Pairwise Screening Table

This file is the main pairwise metadata source for prefiltering event pairs before waveform-level work.

Dataset profile:
- File size: `623,192,542` bytes
- Rows: `3,202,387`
- Rows with both events in the requested window: `2,890,580`

Columns observed:
- `event_i`
- `event_j`
- `common_station_components`
- `common_stations`
- `hypocentral_distance_km`
- `horizontal_distance_km`
- `depth_distance_km`
- `magnitude_diff`
- `time_separation_s`
- `origin_i`
- `lat_i`
- `lon_i`
- `dep_i_km`
- `mag_i`
- `origin_j`
- `lat_j`
- `lon_j`
- `dep_j_km`
- `mag_j`

Why this file is important:
- It already contains the pair-filtering fields highlighted by the user request, including shared observation counts, horizontal distance, depth difference, magnitude difference, and time separation.
- It allows future agents to efficiently rank or filter candidate pairs before loading SAC data.

Example value patterns seen in sample rows:
- `common_station_components` can be in the `400+` range
- `common_stations` can be in the `140+` range
- `horizontal_distance_km`, `depth_distance_km`, and `magnitude_diff` are already computed per pair

#### `events.csv` — Per-Event Summary

This is a compact event inventory useful for quick filtering and plotting.

Columns:
- `evid`
- `origin_time`
- `event_date`
- `latitude`
- `longitude`
- `depth_km`
- `magnitude`
- `n_sac_files`
- `n_observed_stations`
- `n_components`
- `components`
- `analysis_ready`

Use cases:
- fast event maps,
- quick event-level statistics,
- checking whether events have sufficient waveform coverage.

Observed content pattern:
- `components` is a comma-separated list such as `E,N,U,X,Y,Z,sE,sN,sU`
- `analysis_ready` is present as a readiness flag.

#### `stations.csv` — Per-Station Summary

This is a compact station inventory and usage summary.

Columns:
- `station_id`
- `network`
- `station_code`
- `latitude`
- `longitude`
- `elevation_m`
- `trace_count`
- `event_count`
- `component_count`
- `components`

Use cases:
- station diagnostics,
- map support,
- identifying common component sets for each station.

Observed station example:
- `E.SOB1` and `E.SOB2` include `XH,XL,YH,YL,ZH,ZL`

#### Naming Conventions

Event folder naming:
- `D{evid}_20`
- Example: `D20251106000003_20`

SAC file naming:
- Usually `{station_component}.SAC`
- Examples:
  - `E.SOB3.XH.SAC`
  - `ICHINM.E.SAC`

Station ID conventions:
- `station_id` may include a network-style prefix, e.g. `E.SOB1`
- `station_component` appends the component code, e.g. `E.SOB1.XH`

#### Minimal Recommended Files for Future Agents

Primary files:
- `metadata/observations.csv`
- `metadata/event_pair_common_observations.csv`

Useful supporting files:
- `metadata/events.csv`
- `metadata/stations.csv`

Optional supplementary files present:
- `metadata/phase_arrivals.csv`
- `metadata/waveforms.csv`
- `metadata/observations_continuous_supplement_20251106_20251112_all_events.csv`

#### Practical Loading Sequence

Recommended workflow for future agents:
1. Read `metadata/event_pair_common_observations.csv` to filter event pairs by time window and pairwise metadata.
2. Read `metadata/observations.csv` to obtain shared `station_component` rows and `sac_file` paths for selected events.
3. Use `metadata/events.csv` and `metadata/stations.csv` for lightweight summaries and diagnostic plotting support.

Most useful subset fields to preserve:
- From `observations.csv`:
  - `evid`, `origin_time`, `station_component`, `component`, `sac_file`, `exists`, `observation_source`, `has_p_pick`, `has_s_pick`, `p_time_after_origin_s`, `s_time_after_origin_s`, `event_latitude`, `event_longitude`, `event_depth_km`, `event_magnitude`, `station_latitude`, `station_longitude`
- From `event_pair_common_observations.csv`:
  - `event_i`, `event_j`, `common_station_components`, `common_stations`, `horizontal_distance_km`, `depth_distance_km`, `magnitude_diff`, `time_separation_s`, `origin_i`, `origin_j`

#### Data Caveats

- Do not assume `waveforms/by_date/...` exists; rely on `sac_file`.
- Some `observations.csv` rows have null `sampling_rate_hz`, `npts`, `start_time`, or `end_time`.
- `network` may be null for some observation rows even when the station and path fields are usable.
- The dataset mixes multiple component naming conventions, so implicit channel harmonization should not be assumed.
- The merged observation table includes both original event waveforms and continuous supplements, distinguished by `observation_source`.

------------------------------

## observations.csv
**Source path**: `<WAVEFORM_DATA_ROOT>/metadata/observations.csv`
### Summary
`observations.csv` is the main per-event, per-station-component waveform index for this repeat-earthquake dataset, covering 2025-11-01 to 2025-11-14 and linking each observation row to a local SAC file. For the target window 2025-11-01 to 2025-12-06, it contains 139,992 rows across 2,581 events, with event/station metadata, waveform provenance, and P/S pick timing fields needed for future agents to locate and align traces.
### Detail
#### File Overview

Source file:
`<WAVEFORM_DATA_ROOT>/metadata/observations.csv`

Role in dataset:
- Primary analysis entry point for waveform-based repeat-event workflows.
- One row corresponds to one `event-station-component` SAC waveform.
- The table already merges original event waveform products and continuous waveform supplement products.
- Future agents should use `sac_file` from this table as the authoritative path to waveform files.

#### File Statistics

Observed file size:
- `114,668,174` bytes

Full-table coverage:
- Rows: `156,360`
- Unique events (`evid`): `3,055`
- Unique stations (`station_id`): `328`
- Unique station-components (`station_component`): `1,005`
- Origin time range: `2025-11-01 00:19:06` to `2025-11-14 23:24:44`

Requested analysis window subset:
- Time filter: `2025-11-01T00:00:00 <= origin_time < 2025-12-07T00:00:00`
- Rows: `139,992`
- Unique events: `2,581`
- Unique stations: `325`

#### Column Structure

Columns observed in this file:
- `evid`
- `origin_time`
- `event_date`
- `event_latitude`
- `event_longitude`
- `event_depth_km`
- `event_magnitude`
- `event_dir`
- `station_id`
- `network`
- `station_code`
- `station_latitude`
- `station_longitude`
- `station_elevation_m`
- `component`
- `station_component`
- `sac_name`
- `sac_file`
- `exists`
- `observation_source`
- `has_p_pick`
- `has_s_pick`
- `p_pick_time_utc`
- `s_pick_time_utc`
- `p_time_after_origin_s`
- `s_time_after_origin_s`
- `p_quality`
- `s_quality`
- `weight`
- `travel_time_raw_event_id`
- `station_number`
- `n_waveform_components`
- `waveform_components`
- `source_file`
- `station_trace_count`
- `station_event_count`
- `station_component_count`
- `station_components_available`
- `regional_event_id`
- `regional_origin_time_utc`
- `match_time_error_s`
- `source_pick_station_code`
- `source_daily_sac`
- `source`
- `origin_pre_s`
- `origin_post_s`
- `window_start_after_origin_s`
- `window_end_after_origin_s`
- `window_template_sac`
- `window_mode_used`
- `sampling_rate_hz`
- `npts`
- `start_time`
- `end_time`

#### Most Relevant Fields for Future Agents

For repeat-event candidate construction and waveform access, the most important columns are:

Event metadata:
- `evid`
- `origin_time`
- `event_date`
- `event_latitude`
- `event_longitude`
- `event_depth_km`
- `event_magnitude`
- `event_dir`

Station/component identity:
- `station_id`
- `network`
- `station_code`
- `station_latitude`
- `station_longitude`
- `station_elevation_m`
- `component`
- `station_component`

Waveform file access and provenance:
- `sac_name`
- `sac_file`
- `exists`
- `observation_source`
- `source_file`

Phase timing and quality:
- `has_p_pick`
- `has_s_pick`
- `p_pick_time_utc`
- `s_pick_time_utc`
- `p_time_after_origin_s`
- `s_time_after_origin_s`
- `p_quality`
- `s_quality`
- `weight`

Optional trace/window metadata:
- `sampling_rate_hz`
- `npts`
- `start_time`
- `end_time`
- `origin_pre_s`
- `origin_post_s`
- `window_start_after_origin_s`
- `window_end_after_origin_s`
- `window_template_sac`
- `window_mode_used`

Useful provenance/matching fields:
- `travel_time_raw_event_id`
- `regional_event_id`
- `regional_origin_time_utc`
- `match_time_error_s`
- `source_pick_station_code`
- `source_daily_sac`
- `source`

#### Content Patterns Relevant to Repeat-Event Work

In-window waveform source mix (`observation_source`):
- `continuous_sac_daily`: `108,885`
- `event_waveform`: `31,107`

Interpretation:
- This table already consolidates both original event-cut traces and supplement traces extracted from continuous SAC data.
- Future agents can use a single table for loading without separate directory scans.

SAC file existence in the target time window:
- `exists = True`: `139,992`
- No missing-path rows were observed in the inspected window.

Phase-pick coverage in the target time window:
- `has_p_pick = True`: `110,469`
- `has_p_pick = False`: `29,523`
- `has_s_pick = True`: `79,191`
- `has_s_pick = False`: `60,801`

Interpretation:
- P picks are more complete than S picks.
- The metadata supports workflows that prefer S-aligned windows and use P-aligned windows as fallback.

Trace metadata availability in the target time window:
- `sampling_rate_hz = 100.0`: `101,460`
- `sampling_rate_hz = NaN`: `38,532`

Interpretation:
- Many rows include explicit sample rate metadata.
- A substantial subset lacks populated trace stats in the CSV, so some workflows may still need direct SAC-header inspection for `sampling_rate_hz`, `npts`, `start_time`, or `end_time`.

#### Component Naming and Matching Patterns

Most frequent `component` values in the target window:
- `VX`: `36,295`
- `VY`: `36,295`
- `VZ`: `36,295`
- `N`: `5,574`
- `E`: `5,574`
- `U`: `5,537`
- `XL`: `2,037`
- `XH`: `2,037`
- `ZL`: `2,037`
- `ZH`: `2,037`
- `YH`: `2,037`
- `YL`: `2,037`
- `X`: `657`
- `Y`: `657`
- `Z`: `657`
- smaller counts for `sU`, `sE`, `sN`, `sY`, `V`

Representative `station_component` examples:
- `E.SOB3.XH`
- `E.SOB3.XL`
- `E.SOB3.YH`
- `E.SOB3.YL`
- `E.SOB3.ZH`
- `E.SOB3.ZL`
- `N.KKWH.E`
- `N.KKWH.N`
- `N.KKWH.U`
- `N.KMIH.E`
- `N.KMIH.N`
- `N.KMIH.U`

Practical implication:
- The dataset mixes several component naming systems: `E/N/U`, `X/Y/Z`, `XH/XL/YH/YL/ZH/ZL`, `VX/VY/VZ`, and some `s*` variants.
- Exact `station_component` matching is therefore the most reliable way to identify common observations between events.

#### Example Row Structure

Example records show that one row contains:
- event information (`evid`, `origin_time`, location, depth, magnitude)
- station information (`station_id`, coordinates, elevation)
- component identity (`component`, `station_component`)
- absolute SAC path (`sac_file`)
- pick information (`has_p_pick`, `has_s_pick`, `p_time_after_origin_s`, `s_time_after_origin_s`)
- waveform provenance (`observation_source`, `source_file`)
- optional trace/window metadata (often null for some rows)

Representative example values observed:
- `evid`: `20251101000008`
- `event_dir`: `D20251101000008_20`
- `station_id`: `ICHINM`
- `station_component`: `ICHINM.E`
- `sac_name`: `ICHINM.E.SAC`
- `sac_file`: absolute path under `waveforms/events/...`
- `has_p_pick = True`, `has_s_pick = True`
- `p_time_after_origin_s = 5.96`
- `s_time_after_origin_s = 9.67`

#### File Naming and Path Conventions

Waveform files referenced by this table follow patterns such as:
- `waveforms/events/YYYYMMDD/D{evid}_20/{station_component}.SAC`
- `waveforms/supplements/YYYYMMDD/D{evid}_20/{station_component}.SAC`

Examples:
- `.../waveforms/events/20251106/D20251106000003_20/E.SOB3.XH.SAC`
- `.../waveforms/events/20251106/D20251106000003_20/E.SOB3.XL.SAC`

Important note:
- Even if higher-level documentation references `waveforms/by_date/...`, the inspected dataset should be accessed via `sac_file` from this CSV.

#### Recommended Use by Future Agents

Suggested use pattern:
1. Filter `origin_time` to the desired window.
2. Keep only rows with `exists=True`.
3. Group or join by `evid` and exact `station_component`.
4. Use `has_s_pick` / `s_time_after_origin_s` first and `has_p_pick` / `p_time_after_origin_s` second for phase-aligned extraction logic.
5. Load the SAC file using the absolute path in `sac_file`.

Useful minimal subset for many workflows:
- `evid`
- `origin_time`
- `event_latitude`
- `event_longitude`
- `event_depth_km`
- `event_magnitude`
- `station_id`
- `station_component`
- `component`
- `station_latitude`
- `station_longitude`
- `sac_file`
- `exists`
- `observation_source`
- `has_p_pick`
- `has_s_pick`
- `p_time_after_origin_s`
- `s_time_after_origin_s`

#### Data Caveats

- Some trace metadata fields (`sampling_rate_hz`, `npts`, `start_time`, `end_time`) are null for a substantial subset of rows.
- `network` can be null in some records even when `station_id`, `station_component`, and `sac_file` are valid.
- Component conventions are heterogeneous; future agents should avoid assuming canonical 3-component names.
- Because event and supplement traces are merged here, preserving `observation_source` is useful for provenance-aware debugging.

------------------------------

## event_pair_common_observations.csv
**Source path**: `<WAVEFORM_DATA_ROOT>/metadata/event_pair_common_observations.csv`
### Summary
`event_pair_common_observations.csv` is the precomputed event-pair screening table for this repeat-earthquake dataset, containing shared-observation counts and pairwise event geometry. It is the most efficient first-stage input for future agents to filter candidate event pairs in the 2025-11-01 to 2025-12-06 window before joining back to `observations.csv` for station-component-level waveform access.
### Detail
#### File Overview

Source file:
`<WAVEFORM_DATA_ROOT>/metadata/event_pair_common_observations.csv`

Role in dataset:
- Pairwise metadata table for candidate event-pair prescreening.
- Provides precomputed shared-observation counts and pairwise event geometry.
- Intended to be used before any SAC waveform reads, then joined with `metadata/observations.csv` for shared `station_component` waveform extraction.

#### File Statistics

Observed file size:
- `623,192,542` bytes

Coverage:
- Total rows: `3,202,387`
- Rows with both events inside the requested time window (`2025-11-01T00:00:00 <= origin_i, origin_j < 2025-12-07T00:00:00`): `2,890,580`

This indicates that the file is large but already narrowed to useful pairwise metadata, making it suitable for efficient candidate filtering by distance, magnitude difference, and shared observation count.

#### Column Structure

Columns observed in this file:
- `event_i`
- `event_j`
- `common_station_components`
- `common_stations`
- `hypocentral_distance_km`
- `horizontal_distance_km`
- `depth_distance_km`
- `magnitude_diff`
- `time_separation_s`
- `origin_i`
- `lat_i`
- `lon_i`
- `dep_i_km`
- `mag_i`
- `origin_j`
- `lat_j`
- `lon_j`
- `dep_j_km`
- `mag_j`

#### Most Relevant Fields for Future Agents

For candidate pair generation, the most important columns are:
- Pair identity:
  - `event_i`
  - `event_j`
- Shared observation counts:
  - `common_station_components`
  - `common_stations`
- Spatial separation:
  - `horizontal_distance_km`
  - `depth_distance_km`
  - `hypocentral_distance_km`
- Magnitude and time differences:
  - `magnitude_diff`
  - `time_separation_s`
- Event origin and hypocenter metadata:
  - `origin_i`, `lat_i`, `lon_i`, `dep_i_km`, `mag_i`
  - `origin_j`, `lat_j`, `lon_j`, `dep_j_km`, `mag_j`

These fields are sufficient to:
- restrict both events to the requested analysis window,
- filter by shared observation count,
- filter or rank by horizontal distance,
- inspect depth difference and magnitude difference,
- and sort by temporal separation if needed.

#### Semantics of Key Columns

- `event_i`, `event_j`: event identifiers for a pair; designed to join against `observations.csv` via `evid`.
- `common_station_components`: number of exact shared station-component observations between the two events.
- `common_stations`: number of shared stations, regardless of how many components overlap at each station.
- `horizontal_distance_km`: horizontal epicentral separation in kilometers; this is the key spatial screening field emphasized in the task description.
- `depth_distance_km`: absolute depth difference in kilometers.
- `hypocentral_distance_km`: combined 3D event separation.
- `magnitude_diff`: absolute event magnitude difference.
- `time_separation_s`: origin-time separation in seconds.
- `origin_i`, `origin_j`: event origin timestamps for time-window filtering.
- `lat_i`, `lon_i`, `dep_i_km`, `mag_i` and corresponding `_j` fields: event hypocenter/magnitude attributes copied into the pair table.

#### Content Patterns Relevant to Repeat-Event Work

Sample rows show that this table includes pairs with large overlap, for example:
- `common_station_components` in the `400+` range
- `common_stations` around `140+`
- precomputed `horizontal_distance_km`, `depth_distance_km`, and `magnitude_diff`

Representative sampled row structure:
- `event_i`: `20251109000591`
- `event_j`: `20251109000642`
- `common_station_components`: `447`
- `common_stations`: `146`
- `horizontal_distance_km`: `10.667767989135548`
- `depth_distance_km`: `2.1`
- `magnitude_diff`: `0.3000000000000007`
- `time_separation_s`: `3059.0`
- `origin_i`: `2025-11-09 17:03:39`
- `origin_j`: `2025-11-09 17:54:38`

Another sampled pair:
- `event_i`: `20251109000241`
- `event_j`: `20251109000591`
- `common_station_components`: `435`
- `common_stations`: `142`
- `horizontal_distance_km`: `4.7142772222706935`
- `depth_distance_km`: `2.8000000000000007`
- `magnitude_diff`: `1.0`
- `time_separation_s`: `35311.0`

Practical implication:
- The file already contains the core pair-selection metadata requested for future repeat-event pipelines.
- It should be the first table filtered before any station-component-level waveform operations.

#### Time-Window Use

For the requested target window:
- Recommended filter condition is to require both `origin_i` and `origin_j` within `2025-11-01` through `2025-12-06`.
- Doing so retains `2,890,580` rows.

Because this is still a large candidate space, future agents will likely further subset using:
- `common_station_components`
- `horizontal_distance_km`
- `magnitude_diff`
- optionally `depth_distance_km`
- possibly sorting by smaller distance, smaller magnitude difference, and larger shared coverage

#### Join Relationship to Other Files

Primary downstream join target:
- `metadata/observations.csv`

Join keys:
- `event_i` -> `observations.evid`
- `event_j` -> `observations.evid`

Typical future-agent usage pattern:
1. Read this pair table.
2. Filter pairs by time window and pairwise metadata fields.
3. For retained pairs, join to `observations.csv` to find exact common `station_component` observations.
4. Use `observations.csv.sac_file` to load the actual SAC traces.

This file does not contain waveform paths itself; it is a pairwise screening layer only.

#### Relation to User-Prioritized Fields

This file directly supports the pairwise filtering criteria emphasized in the request:
- shared observation threshold: `common_station_components`
- shared station threshold/context: `common_stations`
- epicentral/horizontal distance: `horizontal_distance_km`
- depth difference for review: `depth_distance_km`
- magnitude difference: `magnitude_diff`
- time separation: `time_separation_s`

These are already materialized, so future agents do not need to recompute them from raw event coordinates for initial screening.

#### Recommended Minimal Column Subset for Loading

If memory-efficient loading is needed, the most useful subset is:
- `event_i`
- `event_j`
- `common_station_components`
- `common_stations`
- `horizontal_distance_km`
- `depth_distance_km`
- `magnitude_diff`
- `time_separation_s`
- `origin_i`
- `origin_j`

Optional extra context columns:
- `lat_i`, `lon_i`, `dep_i_km`, `mag_i`
- `lat_j`, `lon_j`, `dep_j_km`, `mag_j`
- `hypocentral_distance_km`

#### Practical Notes and Caveats

- This file is large enough that chunked reading may be preferable for repeated filtering.
- It is already sufficiently structured for direct thresholding and ranking operations without geometric recomputation.
- Column naming uses `horizontal_distance_km` and `depth_distance_km`; future agents should map these carefully if an external workflow expects names like `epicentral_distance_km` or `depth_diff_km`.
- The file contains pair metadata only; waveform existence, pick availability, and SAC paths must be taken from `observations.csv`.

#### Example Path Context

Although this file is pairwise metadata only, it belongs to the package rooted at:
`<WAVEFORM_DATA_ROOT>`

Companion files for future agents:
- `metadata/observations.csv` — per-trace waveform index with `sac_file`
- `metadata/events.csv` — event summary table
- `metadata/stations.csv` — station summary table

------------------------------

## events.csv
**Source path**: `<WAVEFORM_DATA_ROOT>/metadata/events.csv`
### Summary
`events.csv` is a compact per-event inventory for the waveform package, summarizing origin time, hypocenter, magnitude, and overall waveform/component coverage for each event. It is useful for quick event-level filtering, plotting, and validation, but future agents should use it together with `observations.csv` for waveform access and `event_pair_common_observations.csv` for candidate-pair screening.
### Detail
#### File Overview

Source file:
`<WAVEFORM_DATA_ROOT>/metadata/events.csv`

Role in dataset:
- Compact event-level summary table.
- Provides one row per event with hypocenter, magnitude, and waveform-coverage summary fields.
- Useful for quick event filtering, event maps, event count summaries, and sanity checks before joining to more detailed tables.

This file is not the primary waveform index. Future agents should use:
- `observations.csv` for per-station-component SAC paths and pick metadata
- `event_pair_common_observations.csv` for event-pair prescreening

#### File Statistics

Observed file size:
- `314,223` bytes

Based on consistency with the package-level observation table, this file is expected to summarize the same overall event set covered by the waveform package for `2025-11-01` to `2025-11-15`.

#### Column Structure

Columns observed:
- `evid`
- `origin_time`
- `event_date`
- `latitude`
- `longitude`
- `depth_km`
- `magnitude`
- `n_sac_files`
- `n_observed_stations`
- `n_components`
- `components`
- `analysis_ready`

#### Meaning of Key Fields

Core event metadata:
- `evid` — event identifier; join key to `observations.csv.evid` and pair tables
- `origin_time` — event origin timestamp
- `event_date` — calendar date of the event
- `latitude`, `longitude` — event epicenter coordinates
- `depth_km` — event depth in kilometers
- `magnitude` — event magnitude

Waveform coverage summary:
- `n_sac_files` — number of SAC files associated with the event
- `n_observed_stations` — number of stations with observations for this event
- `n_components` — number of distinct components represented for the event
- `components` — comma-separated list of component codes observed for the event
- `analysis_ready` — readiness/status flag for downstream analysis use

#### Example Content Pattern

Observed example rows indicate the file contains compact summaries like:
- Event `20251101000008`
  - `origin_time`: `2025-11-01 00:19:06`
  - `latitude`: `39.03`
  - `longitude`: `140.889`
  - `depth_km`: `8.8`
  - `magnitude`: `0.8`
  - `n_sac_files`: `63`
  - `n_observed_stations`: `20`
  - `n_components`: `9`
  - `components`: `E,N,U,X,Y,Z,sE,sN,sU`
  - `analysis_ready`: `True`

- Event `20251101000433`
  - `origin_time`: `2025-11-01 00:26:18`
  - `latitude`: `39.614`
  - `longitude`: `142.956`
  - `depth_km`: `11.9`
  - `magnitude`: `1.5`
  - `n_sac_files`: `12`
  - `n_observed_stations`: `4`
  - `n_components`: `6`
  - `components`: `E,N,U,X,Y,Z`
  - `analysis_ready`: `True`

#### Relevance to Repeat-Event Work

This file is useful for future agents when they need to:
- quickly subset events by time, location, depth, or magnitude
- create event distribution maps or time series at the event level
- inspect how many waveforms or stations are available for each event
- identify whether an event has broad enough component coverage before more detailed processing

Most relevant columns for these tasks:
- `evid`
- `origin_time`
- `latitude`
- `longitude`
- `depth_km`
- `magnitude`
- `n_sac_files`
- `n_observed_stations`
- `components`
- `analysis_ready`

#### Component Summary Patterns

The `components` field is a comma-separated summary of all component codes seen for the event. Examples show that a single event may include mixed component naming conventions such as:
- `E,N,U`
- `X,Y,Z`
- `sE,sN,sU`

Implication for future agents:
- This field is useful for quick coverage checks, but not for exact waveform matching.
- Exact station-component matching should still be done via `observations.csv` using `station_component`.

#### Recommended Use with Other Files

Typical usage pattern:
1. Use `events.csv` for light event-level filtering or plotting.
2. Use `event_pair_common_observations.csv` for event-pair candidate screening.
3. Use `observations.csv` for actual shared station-component discovery and `sac_file` waveform access.

Join relationships:
- `events.csv.evid` -> `observations.csv.evid`
- `events.csv.evid` -> `event_pair_common_observations.csv.event_i` / `event_j`

#### Practical Notes for Future Agents

Recommended minimal subset if loading only essential fields:
- `evid`
- `origin_time`
- `latitude`
- `longitude`
- `depth_km`
- `magnitude`
- `n_sac_files`
- `n_observed_stations`
- `components`
- `analysis_ready`

Strengths of this file:
- Small and fast to load
- One row per event
- Convenient for overview plots and quick screening summaries

Limitations of this file:
- Does not contain SAC file paths
- Does not contain station-level or component-level pick metadata
- Does not contain pairwise overlap statistics
- Not sufficient by itself for waveform extraction or station-component pairing

#### Path Context

This file belongs to the metadata package under:
`<WAVEFORM_DATA_ROOT>/metadata/`

Companion files most relevant to future agents:
- `observations.csv` — detailed per-trace waveform index with `sac_file`
- `event_pair_common_observations.csv` — pairwise shared-observation and geometry table
- `stations.csv` — per-station summary

------------------------------

## stations.csv
**Source path**: `<WAVEFORM_DATA_ROOT>/metadata/stations.csv`
### Summary
`stations.csv` is a compact station inventory and usage summary for the waveform package, giving one row per station with location, elevation, trace counts, event counts, and available component sets. It is useful for station diagnostics, mapping, and understanding heterogeneous channel conventions, but future agents should pair it with `observations.csv` for per-trace waveform access.
### Detail
#### File Overview

Source file:
`<WAVEFORM_DATA_ROOT>/metadata/stations.csv`

Role in dataset:
- Compact per-station summary table.
- Provides one row per station with geographic location, elevation, data-volume summaries, and component availability.
- Useful for station-level diagnostics, mapping, and understanding which component conventions are present in the dataset.

This file is not the waveform index. Future agents should use:
- `observations.csv` for per-event, per-station-component SAC paths and pick metadata
- `event_pair_common_observations.csv` for event-pair screening

#### File Statistics

Observed file size:
- `19,093` bytes

This is a small inventory-style table intended for fast loading and quick station-level reference.

#### Column Structure

Columns observed:
- `station_id`
- `network`
- `station_code`
- `latitude`
- `longitude`
- `elevation_m`
- `trace_count`
- `event_count`
- `component_count`
- `components`

#### Meaning of Key Fields

Station identity:
- `station_id` — primary station identifier used in the package; often includes a network-style prefix
- `network` — network code
- `station_code` — station code without network prefix

Station location:
- `latitude`
- `longitude`
- `elevation_m`

Data availability summary:
- `trace_count` — total number of waveform traces associated with the station across the package
- `event_count` — number of distinct events observed by the station
- `component_count` — number of distinct component codes available at the station
- `components` — comma-separated list of available component names for that station

#### Example Content Pattern

Observed example rows:
- `station_id = E.SOB1`
  - `network = E`
  - `station_code = SOB1`
  - `latitude = 39.16669845581055`
  - `longitude = 143.23919677734375`
  - `elevation_m = -2480.0`
  - `trace_count = 6582`
  - `event_count = 1097`
  - `component_count = 6`
  - `components = XH,XL,YH,YL,ZH,ZL`

- `station_id = E.SOB2`
  - `network = E`
  - `station_code = SOB2`
  - `latitude = 39.20289993286133`
  - `longitude = 142.9842987060547`
  - `elevation_m = -1840.0`
  - `trace_count = 5772`
  - `event_count = 962`
  - `component_count = 6`
  - `components = XH,XL,YH,YL,ZH,ZL`

These examples show that some stations are ocean-bottom or seafloor sites with negative elevation values and multi-channel component sets.

#### Relevance to Repeat-Event Work

This file is useful for future agents when they need to:
- make station maps or station-coverage diagnostics
- identify high-coverage stations with many traces or events
- understand the component naming conventions available at each station
- check whether a station has the channels needed for exact `station_component` matching

Most relevant fields for these tasks:
- `station_id`
- `latitude`
- `longitude`
- `elevation_m`
- `trace_count`
- `event_count`
- `component_count`
- `components`

#### Component Convention Summary

The `components` field summarizes each station's available channels. Example values show heterogeneous component conventions, including:
- `XH,XL,YH,YL,ZH,ZL`

Combined with patterns seen elsewhere in the package, future agents should expect multiple station/channel conventions across the full dataset, such as:
- `E,N,U`
- `X,Y,Z`
- `XH,XL,YH,YL,ZH,ZL`
- `VX,VY,VZ`

Implication:
- This file is useful for understanding station-level component availability.
- Exact pairing of shared observations should still be done from `observations.csv` using `station_component` rather than inferred from `stations.csv` alone.

#### Relationship to Other Metadata Files

Primary joins and use with companion tables:
- `stations.csv.station_id` -> `observations.csv.station_id`
- `stations.csv.station_code` and `network` can support display or grouping, but `station_id` is the safest identifier for joins within this package.

Recommended usage pattern:
1. Use `stations.csv` to inspect station inventory and channel availability.
2. Use `observations.csv` to locate actual event-station-component rows and SAC paths.
3. Use `event_pair_common_observations.csv` to screen event pairs before per-station waveform work.

#### Practical Uses for Future Agents

Good use cases for this file:
- ranking stations by `trace_count` or `event_count`
- plotting station locations as context in repeat-event figures
- checking whether a station supports multiple channels or unusual component codes
- building summaries of which stations contribute most data

Recommended minimal subset if loading only essentials:
- `station_id`
- `latitude`
- `longitude`
- `elevation_m`
- `trace_count`
- `event_count`
- `component_count`
- `components`

#### Limitations

This file does not contain:
- event IDs
- origin times
- waveform file paths
- per-trace phase picks
- pairwise event overlap counts

Therefore it is not sufficient by itself for candidate screening or waveform loading. It is a station reference table only.

#### Path Context

This file belongs to the metadata package under:
`<WAVEFORM_DATA_ROOT>/metadata/`

Companion files most relevant to future agents:
- `observations.csv` — per-trace waveform index with `sac_file`, event metadata, and P/S picks
- `event_pair_common_observations.csv` — event-pair overlap and geometry table
- `events.csv` — compact event inventory

------------------------------

