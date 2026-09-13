## Scientific Purpose

This task performed event-centered sequence extraction around the three matched major earthquakes in the Aomori regional catalog, with the objective of building a reusable parameter grid for later comparative sequence analysis. The extraction was designed to support tests of pre-event versus post-event seismicity evolution around M1, M2, and M3 under multiple spatial, temporal, depth, and magnitude definitions.

The extracted products are intended to serve as the quantitative basis for later robustness assessment, aftershock decay diagnostics, and three-event comparison.

## Method and Implementation Evidence

The implementation verified that all required source fields were present in the working inputs and that the three major earthquakes were matched to the relocated catalog before sequence extraction. The verification record confirms completeness of the required fields for:

- catalog: `datetime`, `lat`, `lon`, `dep`, `mag`
- main-earthquake table: `index`, `datetime`, `lat`, `lon`, `dep`, `mag`
- focal-mechanism file: `origin_time`, `lat_deg`, `lon_deg`, `depth_km`
- station file: `latitude`, `longitude`
- matched mainshock table: `label`, `matched_datetime`, `matched_lat`, `matched_lon`, `matched_dep`, `matched_mag`

Evidence: `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/02_sequence_extraction/sequence_extraction_verification.json`

The extraction grid covered:

- radii: 30, 44, 50, 80, 100 km
- time windows: 7, 30, 60, 90 days
- depth strategies: `all`, `mainshock_window`, `stratified`
- magnitude thresholds: none, 1.2, 1.5, 2.0, 2.5
- moving-window length: 7 days

Evidence: `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/02_sequence_extraction/sequence_extraction_verification.json`

The task generated 900 sequence rows, consistent with the full parameter grid, and 1,606,311 total extracted sequence-event instances across the three mainshocks. This indicates that the event-centered extraction was successfully completed across the intended combinations.

Evidence:
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/02_sequence_extraction/sequence_extraction_counts.csv`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/02_sequence_extraction/event_centered_sequence_table.csv`

The matched major earthquakes used for centering were:

- M1: 2025-11-09 08:03:39.230000+00:00, M 6.9, 39.403276°N, 143.506006°E, 15.99 km
- M2: 2025-12-08 14:15:10.180000+00:00, M 7.5, 40.966150°N, 142.290544°E, 53.46 km
- M3: 2026-04-20 07:52:58.050000+00:00, M 7.7, 39.843359°N, 143.156462°E, 19.31 km

Evidence: `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/02_sequence_extraction/mainshock_sequence_metadata.csv`

A control comparison was also implemented using background windows away from the mainshock times. The recorded control window was 60 days long, shifted to -240 to -180 days relative to each event, with a 50 km radius.

Evidence: `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/02_sequence_extraction/sequence_control_comparison.csv`

## Key Results and Evidence Files

### 1) Successful rematch and event-centered extraction for all three mainshocks
The metadata file shows that all three target earthquakes were matched to relocated catalog entries and used as sequence centers. The catalog size used for extraction was 25,646 events for each mainshock context.

Evidence:  
`<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/02_sequence_extraction/mainshock_sequence_metadata.csv`

### 2) Full parameter-grid coverage
The extracted sequence table spans the intended grid of 5 radii × 4 time windows × 3 depth strategies × 5 magnitude settings = 300 combinations per mainshock, or 900 rows total. This confirms that the task produced a complete combinatorial extraction product for downstream robustness testing.

Evidence:  
`<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/02_sequence_extraction/sequence_extraction_counts.csv`

### 3) Strong pre/post event asymmetry is already visible in the counts
For example, at 30 km radius, 7-day window, and no magnitude threshold, M1 has 506 pre-event events versus 1424 post-event events; the corresponding pre-rate and post-rate are 72.29 and 203.43 events/day, with a rate ratio of 2.81. Similar summaries are provided in the diagnostics file across all parameter combinations.

Evidence:
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/02_sequence_extraction/sequence_diagnostics_summary.csv`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/02_sequence_extraction/sequence_extraction_counts.csv`

### 4) Mechanism availability is complete in the extracted sequences
The diagnostics summary reports `mecha_available = True` for all 900 rows and nonzero mechanism-event counts in the example rows, indicating that focal-mechanism linkage was available for every extracted sequence setting, even though the later scientific interpretation may still need to account for uneven station/mechanism coverage.

Evidence:  
`<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/02_sequence_extraction/sequence_diagnostics_summary.csv`

### 5) Omori-style post-event fitting was only partially feasible
The diagnostic summary indicates that `post_omori_fit_ok` is split evenly across the grid: 450 `True` and 450 `False`. In the sampled output, 7-day sequences at 30 km for M1 did not yield a fit, while longer-window or different-strategy cases may. This means post-event decay modeling is only conditionally available and depends on the selected sequence definition.

Evidence:  
`<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/02_sequence_extraction/sequence_diagnostics_summary.csv`

### 6) Background control windows were mostly quiet, except for M3
The simple background control comparison found zero events for M1 and M2 in the selected control window, but 45 events for M3 (0.75 events/day). This suggests that the M3 background comparison window still contained moderate seismicity, so M3 control contrasts may be less conservative than for M1 and M2.

Evidence:  
`<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/02_sequence_extraction/sequence_control_comparison.csv`

### 7) Parameter sensitivity is substantial and should be treated explicitly in later analysis
The diagnostics summary shows mainshock-dependent rate-ratio ranges:

- M1: min 2.81, median 5.03, max 6.57
- M2: min 18.44, median 56.8, max infinite
- M3: min 1.80, median 5.95, max infinite

This indicates strong event-to-event heterogeneity and suggests that M2 is especially enriched relative to its pre-event background, while M1 and M3 remain elevated but less extreme.

Evidence:  
`<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/02_sequence_extraction/sequence_diagnostics_summary.csv`

## Limitations and Assumptions

- No image or PDF figures were present in the task outputs, so this task can only be assessed from machine-readable tables and verification metadata.
- The output here is extraction-focused; it does not yet include the full visual diagnostic figure set requested in the broader science brief.
- The control comparison is simple and limited to one background window definition; it is useful as a sanity check but not a full null model.
- `post_omori_fit_ok` is only partly true across the parameter grid, so Omori-style decay estimates are not universally available and should be treated as conditional diagnostics.
- The extracted counts and rates are sensitive to the chosen radius, time window, depth strategy, and magnitude threshold; later interpretation should emphasize robustness across settings rather than any single sequence definition.
- Although mechanism availability is reported as complete in the extraction outputs, the broader project guidance notes uneven station coverage and focal-mechanism availability at the catalog level, so mechanism-based interpretations should still be conservative.
- The control window for M3 contained nonzero activity, so background subtraction or pre/post contrast for M3 may be less clean than for M1 and M2.

## Report-Ready Summary

This task successfully built the event-centered sequence dataset for the three matched major Aomori earthquakes and evaluated it across a full grid of radii, time windows, depth strategies, and magnitude thresholds. The extraction confirms complete field verification, successful rematching, full grid coverage, complete mechanism availability within the extracted sequences, and strong pre/post asymmetry in event counts. The main outputs are the sequence table, counts summary, diagnostics summary, mainshock metadata, control comparison, and verification JSON, which together form the quantitative basis for the subsequent robustness and comparative sequence-analysis steps.

Key evidence files:
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/02_sequence_extraction/event_centered_sequence_table.csv`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/02_sequence_extraction/mainshock_sequence_metadata.csv`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/02_sequence_extraction/sequence_control_comparison.csv`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/02_sequence_extraction/sequence_diagnostics_summary.csv`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/02_sequence_extraction/sequence_extraction_counts.csv`
- `<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/02_sequence_extraction/sequence_extraction_verification.json`