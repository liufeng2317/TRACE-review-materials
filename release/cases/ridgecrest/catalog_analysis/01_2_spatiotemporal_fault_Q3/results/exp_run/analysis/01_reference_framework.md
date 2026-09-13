## Scientific Purpose

This task established the common reference framework for the Ridgecrest inter-mainshock analysis, specifically the period between the Mw 6.4 event and the Mw 7.1 event. Its scientific role is foundational: it creates the cleaned inter-mainshock earthquake dataset, harmonized time-interval tables, fault-point tables, and shared spatial metadata needed for later kernel-density migration and geometric morphology analyses.

The outputs directly support the later scientific questions on whether seismicity between the two mainshocks evolved by spatial focusing toward the Mw 7.1 rupture zone, by spreading/defocusing, or by more complex migration across fault intersections or structurally heterogeneous zones. In particular, this task defines a single, reproducible temporal window and a common map frame so that all downstream spatial comparisons remain internally consistent.

## Method and Implementation Evidence

The implementation assembled three input sources into a common analysis-ready framework:

1. The relocated earthquake catalog at `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/TRACE_ridgecrest_relocated.csv`.
2. The two mainshock reference events at `<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/main_shock_events.csv`.
3. The mapped surface fault geometry at `<REPO_ROOT>/examples/ridgecrest/data/faults/ridgecrest_surface_faults.json`.

The task then produced a cleaned and windowed earthquake subset for the exact inter-mainshock interval, from the Mw 6.4 origin time to the Mw 7.1 origin time, and exported it as `<PACKAGE_ROOT>/results/exp_run/outputs/01_reference_framework/intermainshock_catalog_clean.csv`.

It also generated interval-definition tables for the two KDE stages and the 1-hour morphology analysis:
- `<PACKAGE_ROOT>/results/exp_run/outputs/01_reference_framework/interval_definitions_kde_stage1.csv`
- `<PACKAGE_ROOT>/results/exp_run/outputs/01_reference_framework/interval_definitions_kde_stage2.csv`
- `<PACKAGE_ROOT>/results/exp_run/outputs/01_reference_framework/interval_definitions_morphology_1h.csv`

For spatial consistency, the fault traces were converted into a point table with projected coordinates:
- `<PACKAGE_ROOT>/results/exp_run/outputs/01_reference_framework/fault_segments_table.csv`

The two mainshocks were also exported as a dedicated projected reference table:
- `<PACKAGE_ROOT>/results/exp_run/outputs/01_reference_framework/mainshock_reference_table.csv`

A machine-readable summary of cleaning, counts, time windows, map extent, and projection was recorded in:
- `<PACKAGE_ROOT>/results/exp_run/outputs/01_reference_framework/analysis_metadata.json`

No image or PDF outputs were present in this task output directory, so there were no visual products to analyze individually. This is consistent with the task scope: it is a reference-data construction step rather than a figure-generation step.

## Key Results and Evidence Files

### 1. A clean inter-mainshock earthquake dataset was successfully built with full row retention
The cleaning summary in `<PACKAGE_ROOT>/results/exp_run/outputs/01_reference_framework/analysis_metadata.json` reports:
- original catalog rows: 84,474
- rows after cleaning: 84,474
- rows removed: 0

The final inter-mainshock subset contains 4,716 events, as reported in the same JSON file under `counts.intermainshock_catalog_event_count` and verified in `<PACKAGE_ROOT>/results/exp_run/outputs/01_reference_framework/intermainshock_catalog_clean.csv` (shape: 4,716 rows × 9 columns).

This means the later migration and morphology analyses can proceed without ambiguity from ad hoc filtering or hidden data loss.

### 2. The inter-mainshock window is precisely defined and spans 33.77 hours
The exact analysis window is documented in `<PACKAGE_ROOT>/results/exp_run/outputs/01_reference_framework/analysis_metadata.json`:
- Mw 6.4 time: `2019-07-04T17:33:49.040000+00:00`
- Mw 7.1 time: `2019-07-06T03:19:53.040000+00:00`
- duration: 33.7678 hours

The window bounds are also reflected in `<PACKAGE_ROOT>/results/exp_run/outputs/01_reference_framework/intermainshock_catalog_clean.csv`, whose earliest and latest event times match those two mainshock times exactly.

Scientifically, this confirms that the reference dataset covers the full triggering interval of interest and includes both bounding mainshocks in a reproducible way.

### 3. The mainshock reference events were matched exactly to the relocated catalog
The metadata file `<PACKAGE_ROOT>/results/exp_run/outputs/01_reference_framework/analysis_metadata.json` reports zero time mismatch for both key events:
- `Mainshock64.nearest_catalog_time_difference_seconds = 0.0`
- `Mainshock71.nearest_catalog_time_difference_seconds = 0.0`

The corresponding mainshock table `<PACKAGE_ROOT>/results/exp_run/outputs/01_reference_framework/mainshock_reference_table.csv` provides the spatial coordinates needed for all later overlays:
- Mainshock64: 35.70421°N, -117.49392°E, depth 11.864 km, M6.4
- Mainshock71: 35.77623°N, -117.59286°E, depth 1.986 km, M7.1

Projected coordinates are also included:
- Mainshock64: x = 455,318.346 m; y = 3,951,254 m
- Mainshock71: x = 446,416.089 m; y = 3,959,292 m

This exact catalog alignment is critical because later hotspot tracking and envelope evolution will be interpreted relative to these two epicentral anchors.

### 4. The KDE stage definitions are internally consistent and capture the full inter-mainshock sequence
The task produced two stage tables that match the requested design:

#### Stage 1: first 4 hours after Mw 6.4, using 30-minute bins
Evidence: `<PACKAGE_ROOT>/results/exp_run/outputs/01_reference_framework/interval_definitions_kde_stage1.csv`

Key properties:
- number of intervals: 8
- duration per interval: 0.5 hour
- event counts per interval: 65 to 75
- total Stage 1 events: 550

The metadata file confirms the same totals and frequency. This is a strong basis for early-time KDE comparison because the event counts are relatively uniform across the eight half-hour bins.

#### Stage 2: from +4 hours after Mw 6.4 to Mw 7.1, using 2-hour bins
Evidence: `<PACKAGE_ROOT>/results/exp_run/outputs/01_reference_framework/interval_definitions_kde_stage2.csv`

Key properties from the metadata and interval table:
- number of intervals: 15
- nominal duration: 2 hours
- final interval shorter because it closes at the Mw 7.1 origin time
- event total: 4,166

Together, Stage 1 and Stage 2 sum exactly to the full 4,716-event inter-mainshock catalog:
- 550 + 4,166 = 4,716

The common binning policy is explicitly recorded as `left_closed_right_open_except_final_closed` in both the JSON metadata and the CSV tables. This matters scientifically because it prevents duplicated assignment of events on bin boundaries while still including the terminal Mw 7.1 event in the final interval.

### 5. The morphology framework covers the same full window at 1-hour resolution
The morphology intervals are defined in `<PACKAGE_ROOT>/results/exp_run/outputs/01_reference_framework/interval_definitions_morphology_1h.csv`.

Key properties:
- 34 intervals total
- 33 full 1-hour bins plus one final shorter bin
- final interval duration: 0.767778 hour
- event counts range from 96 to 162
- total events: 4,716

This confirms that the convex-hull and alpha-shape analyses planned for later tasks will use a complete and non-overlapping hourly segmentation of the inter-mainshock period.

### 6. A unified fault and projected spatial framework was prepared for top-level overlays
The fault geometry was transformed into a dense point table:
- `<PACKAGE_ROOT>/results/exp_run/outputs/01_reference_framework/fault_segments_table.csv`

The metadata file reports:
- fault segment count: 17,792
- fault point count: 207,549
- skipped segments: 0

This indicates complete retention of the supplied mapped fault geometry. The fault table includes longitude, latitude, point order, and projected coordinates (`x_m`, `y_m`), enabling consistent overlay in either geographic or projected space.

The shared plot extent is defined in `<PACKAGE_ROOT>/results/exp_run/outputs/01_reference_framework/analysis_metadata.json`:
- longitude padded range: -117.84240063769927 to -117.262835696215
- latitude padded range: 35.39951379518505 to 35.9885750704832
- margin: 0.05°

A projected CRS is also specified there:
- EPSG: 32611

This is a key technical result because later density maps, hotspot migration paths, and morphology envelopes must all share the same map frame and projection for valid comparison.

## Limitations and Assumptions

- This task is a reference-data preparation step only. It does not yet provide the KDE maps, hotspot migration figures, convex hull overlays, alpha-shape overlays, or any direct inference about focusing versus defocusing. Those scientific interpretations must be made in later tasks using these reference products.
- No image or PDF files were present in `<PACKAGE_ROOT>/results/exp_run/outputs/01_reference_framework`, so there are no figure-based results to assess at this stage.
- The final interval in Stage 2 and the final morphology interval are shorter than the nominal bin width because the analysis window ends exactly at the Mw 7.1 origin time. This is appropriate and explicitly documented, but it means those last bins are not duration-equivalent to the others.
- The fault output is a point-expanded representation of the input JSON fault geometry rather than a simplified structural interpretation. It supports overlay and spatial context, but not by itself a classification into along-strike, corner, intersection, or complex-fault zones.
- The metadata confirms zero rows removed during cleaning, but this task does not by itself evaluate detection completeness, magnitude completeness, location uncertainty, or relocation bias within the inter-mainshock sequence.
- The task establishes a projected CRS (EPSG:32611) and geographic plot extents, but it does not yet document the fixed KDE bandwidth or alpha parameter requested for later analyses; those choices should be checked in the downstream KDE and morphology tasks.

## Report-Ready Summary

Task 01 successfully built the shared reference framework for all subsequent Ridgecrest inter-mainshock analyses. The core deliverable is a clean, analysis-ready earthquake catalog spanning exactly from the Mw 6.4 mainshock at `2019-07-04T17:33:49.040000+00:00` to the Mw 7.1 mainshock at `2019-07-06T03:19:53.040000+00:00`, containing 4,716 events with both geographic and projected coordinates in `<PACKAGE_ROOT>/results/exp_run/outputs/01_reference_framework/intermainshock_catalog_clean.csv`. The two mainshocks were matched exactly to the relocated catalog with zero time discrepancy, and their reference coordinates were exported in `<PACKAGE_ROOT>/results/exp_run/outputs/01_reference_framework/mainshock_reference_table.csv`.

The task also defined the temporal binning needed for later spatiotemporal analyses: 8 half-hour KDE intervals for the first 4 hours after the Mw 6.4 event, 15 two-hour KDE intervals from +4 hours to the Mw 7.1 event, and 34 morphology intervals at 1-hour resolution, documented in `<PACKAGE_ROOT>/results/exp_run/outputs/01_reference_framework/interval_definitions_kde_stage1.csv`, `<PACKAGE_ROOT>/results/exp_run/outputs/01_reference_framework/interval_definitions_kde_stage2.csv`, and `<PACKAGE_ROOT>/results/exp_run/outputs/01_reference_framework/interval_definitions_morphology_1h.csv`. These interval tables use an explicit non-overlapping boundary rule and sum exactly to the full inter-mainshock event count.

Finally, the task established the common spatial context required for direct comparison across all later figures. The surface fault geometry was preserved completely as 17,792 segments and 207,549 points in `<PACKAGE_ROOT>/results/exp_run/outputs/01_reference_framework/fault_segments_table.csv`, and shared map extents plus projected CRS metadata were recorded in `<PACKAGE_ROOT>/results/exp_run/outputs/01_reference_framework/analysis_metadata.json`. These outputs provide the reproducible backbone for later evaluation of whether seismicity between Mw 6.4 and Mw 7.1 migrated by focusing toward the eventual Mw 7.1 rupture zone, spread laterally, or evolved in a structurally segmented manner.