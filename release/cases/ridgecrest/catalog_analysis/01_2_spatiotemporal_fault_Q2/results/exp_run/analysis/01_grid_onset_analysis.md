## Scientific Purpose

This task established the common spatial and temporal framework for analyzing how seismic activation evolved between the Ridgecrest Mw 6.4 and Mw 7.1 mainshocks, with emphasis on whether activation across the fault system was synchronous or progressively staged. Specifically, the task:

- validated the relocated catalog, mainshock table, and mapped fault inputs,
- defined the inter-mainshock time window from Mw 6.4 to Mw 7.1,
- expanded the fault-bounded study area by 5 km,
- discretized the region into 1 km × 1 km grid cells,
- constructed 30-minute seismicity-rate time series for each occupied cell,
- identified reproducible cell-level activation onset times based on sustained rate increase.

The outputs from this task provide the first spatially explicit evidence for whether seismic activation emerged simultaneously across the study area or evolved in a delayed, heterogeneous manner prior to the Mw 7.1 rupture.

## Method and Implementation Evidence

The implementation successfully processed the Ridgecrest inputs and produced a complete onset-analysis product suite under `<PACKAGE_ROOT>/results/exp_run/outputs/01_grid_onset_analysis`.

Key implementation evidence:

- Input validation summary is documented in `<PACKAGE_ROOT>/results/exp_run/outputs/01_grid_onset_analysis/tables/qc_summary.csv`.
  - Catalog input rows: 84,474.
  - Missing required rows, invalid numeric rows, invalid time rows, and duplicate removals were all 0 in the visible summary.
- Analysis parameters are documented in `<PACKAGE_ROOT>/results/exp_run/outputs/01_grid_onset_analysis/tables/run_parameters.csv`.
  - Time window start: 2019-07-04 17:33:49.040000+00:00.
  - Time window end: 2019-07-06 03:19:53.040000+00:00.
  - Grid spacing: 1.0 km.
  - Buffer: 5.0 km.
  - Time bin: 30 minutes.
  - Implemented onset rule: first 30-minute bin with count ≥ 2 and sustained activation defined by either candidate+next ≥ 3 or candidate+next_two ≥ 3 with nonzero post-candidate activity.
- Study area bounds are recorded in `<PACKAGE_ROOT>/results/exp_run/outputs/01_grid_onset_analysis/tables/study_region_bounds.csv`.
  - Local bounds: x = -27 to 26 km, y = -29 to 27 km.
- Mainshock reference locations are recorded in `<PACKAGE_ROOT>/results/exp_run/outputs/01_grid_onset_analysis/tables/mainshock_reference_table.csv`.
  - Mainshock64 local position: x = 4.476995 km, y = -3.994320 km.
  - Mainshock71 local position: x = -4.472965 km, y = 3.996601 km.
  - Inter-mainshock elapsed time: 2026.07 minutes (~33.77 hours).
- Time discretization is preserved in `<PACKAGE_ROOT>/results/exp_run/outputs/01_grid_onset_analysis/tables/time_bins.csv`, with 68 half-hour bins spanning the inter-mainshock interval.
- Grid geometry and per-cell onset attributes are preserved in `<PACKAGE_ROOT>/results/exp_run/outputs/01_grid_onset_analysis/tables/grid_definition.csv` and `<PACKAGE_ROOT>/results/exp_run/outputs/01_grid_onset_analysis/tables/grid_cell_onset.csv`.
- Event filtering and cell assignment are preserved in `<PACKAGE_ROOT>/results/exp_run/outputs/01_grid_onset_analysis/tables/filtered_events.csv` and `<PACKAGE_ROOT>/results/exp_run/outputs/01_grid_onset_analysis/tables/event_to_cell_assignment.csv`.
  - 4,713 filtered events were retained in the analysis window and assigned to cells.
- Cell-level 30-minute time series are preserved in `<PACKAGE_ROOT>/results/exp_run/outputs/01_grid_onset_analysis/tables/cell_time_series.csv`.

This implementation level is sufficient for later fault-segment analysis because it provides a reproducible regional onset field and quantitative timing products that can be compared with segment-level activation.

## Key Results and Evidence Files

### 1. The inter-mainshock study area captures a structurally organized, fault-aligned seismic belt rather than diffuse regional activation

The study-region overview shows a broad buffered domain enclosing both mainshocks and the mapped surface-fault network, while the filtered events cluster strongly along a central fault corridor and at an apparent structurally complex junction zone. The geometry is not consistent with uniformly distributed seismicity.

Evidence:
- `<PACKAGE_ROOT>/results/exp_run/outputs/01_grid_onset_analysis/figures/study_region_overview.png`
- `<PACKAGE_ROOT>/results/exp_run/outputs/01_grid_onset_analysis/tables/study_region_bounds.csv`
- `<PACKAGE_ROOT>/results/exp_run/outputs/01_grid_onset_analysis/tables/filtered_events.csv`
- `<PACKAGE_ROOT>/results/exp_run/outputs/01_grid_onset_analysis/tables/mainshock_reference_table.csv`

Figure-based interpretation:
- The mapped faults form a multi-strand, intersecting system.
- Filtered events are concentrated in a narrow, elongated belt aligned with those structures.
- Mw 6.4 and Mw 7.1 lie on opposite sides of this central fault system rather than at isolated ends of a simple single-fault geometry.

Scientific relevance:
- This spatial setup already suggests that any onset pattern is likely to be structurally controlled and possibly multi-path, not merely a radially symmetric aftershock field.

### 2. Seismicity remained regionally elevated through most of the Mw 6.4–Mw 7.1 interval, so local onset timing occurred within an already active sequence

The study-area seismicity-rate plot shows sustained elevated rates across most of the 33+ hour inter-mainshock interval, with multiple bursts rather than a simple monotonic decay.

Evidence:
- `<PACKAGE_ROOT>/results/exp_run/outputs/01_grid_onset_analysis/figures/study_area_seismicity_rate.png`
- `<PACKAGE_ROOT>/results/exp_run/outputs/01_grid_onset_analysis/tables/time_bins.csv`
- `<PACKAGE_ROOT>/results/exp_run/outputs/01_grid_onset_analysis/tables/filtered_events.csv`

Figure-based interpretation:
- Rates stay roughly in the 130–150 events/hour range for much of the interval, with bursts up to ~160–170 events/hour.
- There is no prolonged quiescent interval separating early and late activity.
- The strongest late drop occurs only near the end of the window.

Scientific relevance:
- Grid-cell onset should be interpreted as local activation within a persistently energized system, not necessarily as onset from background quiescence.
- This supports the idea that local activation timing may reflect progressive structural recruitment or local stress-state thresholds.

### 3. Occupancy and event density are highly heterogeneous across the 1 km grid; onset estimates are best constrained along the main seismic corridor

Among 2,968 grid cells, only 445 were occupied, and event counts per occupied cell are strongly right-skewed. Most occupied cells contain few events, whereas a small number of cells contain many events.

Evidence:
- `<PACKAGE_ROOT>/results/exp_run/outputs/01_grid_onset_analysis/tables/grid_cell_onset.csv`
- `<PACKAGE_ROOT>/results/exp_run/outputs/01_grid_onset_analysis/tables/validation_summary.csv`
- `<PACKAGE_ROOT>/results/exp_run/outputs/01_grid_onset_analysis/figures/occupied_cells_map.png`
- `<PACKAGE_ROOT>/results/exp_run/outputs/01_grid_onset_analysis/figures/occupied_cell_event_histogram.png`

Quantitative evidence:
- Occupied grid cells: 445.
- Activated grid cells: 104.
- Occupied but no-onset cells: 341.
- Event-count distribution is strongly right-skewed, with a long tail exceeding 100 events/cell in a small number of hotspots.

Scientific relevance:
- Onset constraints are strongest in contiguous, high-count, fault-aligned cells.
- Sparse marginal cells are much less informative.
- This heterogeneity is important when later comparing apparent propagation patterns against structural controls.

### 4. Only a minority of occupied cells show clear activation, and robust onset detection is concentrated in a narrow fault-aligned corridor

The confidence map shows that robust onsets are spatially concentrated rather than distributed throughout the occupied grid. Most cells either have no onset or weak onset, and robust detections form an elongated NW-SE corridor.

Evidence:
- `<PACKAGE_ROOT>/results/exp_run/outputs/01_grid_onset_analysis/figures/grid_onset_confidence_map.png`
- `<PACKAGE_ROOT>/results/exp_run/outputs/01_grid_onset_analysis/tables/grid_cell_onset.csv`
- `<PACKAGE_ROOT>/results/exp_run/outputs/01_grid_onset_analysis/tables/validation_summary.csv`

Quantitative evidence from tables:
- Confidence classes across all cells:
  - no events: 2,523
  - no onset: 341
  - robust onset: 86
  - weak onset: 18
- Thus, only 104 of 445 occupied cells were activated, and 86 of those were robust.

Scientific interpretation:
- Activation was not a domain-wide synchronous phenomenon.
- The strongest onset evidence clusters along a central fault-related corridor and nearby southern branch.
- This supports structurally localized activation rather than homogeneous co-activation across the whole study area.

### 5. Onset timing is strongly heterogeneous: many cells activated early after Mw 6.4, but a substantial tail of delayed activation persisted up to near Mw 7.1

The onset histogram and CDF show a strongly right-skewed distribution. Many cells activated very early, but activation continued progressively over the full inter-mainshock interval.

Evidence:
- `<PACKAGE_ROOT>/results/exp_run/outputs/01_grid_onset_analysis/figures/grid_onset_histogram_cdf.png`
- `<PACKAGE_ROOT>/results/exp_run/outputs/01_grid_onset_analysis/tables/grid_cell_onset.csv`
- `<PACKAGE_ROOT>/results/exp_run/outputs/01_grid_onset_analysis/tables/grid_onset_metrics.csv`

Quantitative evidence:
- Activated cells: 104.
- Onset-time statistics for activated cells:
  - minimum: 0.0 h
  - 25th percentile: 1.0 h
  - median: 6.25 h
  - 75th percentile: 12.625 h
  - 90th percentile: 20.85 h
  - maximum: 33.0 h
- Fractions of occupied cells activated by elapsed time:
  - within 30 min: 0.044944
  - within 60 min: 0.060674
  - within 120 min: 0.071910
  - within 240 min: 0.094382

Scientific interpretation:
- The sequence was not synchronously activated along all occupied fault-parallel cells.
- Instead, there was an early burst of local activation followed by a prolonged recruitment of additional cells over many hours.
- This is direct evidence for staged or cascading behavior at the grid scale.

### 6. The spatial onset map indicates staged activation from the Mw 6.4 neighborhood into other fault-aligned zones, including later activation nearer the Mw 7.1 area

The onset-time map is the strongest spatial evidence from this task. Darker cells, indicating early onset, cluster around the Mw 6.4 region and along a southward/central structural corridor. Lighter cells, indicating later onset, occur toward the northwest patch and peripheral zones, including near the Mw 7.1 epicentral area.

Evidence:
- `<PACKAGE_ROOT>/results/exp_run/outputs/01_grid_onset_analysis/figures/grid_onset_map.png`
- `<PACKAGE_ROOT>/results/exp_run/outputs/01_grid_onset_analysis/tables/grid_cell_onset.csv`
- `<PACKAGE_ROOT>/results/exp_run/outputs/01_grid_onset_analysis/tables/mainshock_reference_table.csv`

Figure-based interpretation:
- Earliest activation is concentrated near the Mw 6.4 epicenter and in the central-southern corridor.
- Later activation appears on the margins and in a northwestern patch that lies near the Mw 7.1 side of the system.
- Activated cells align with mapped structures rather than filling the study domain uniformly.

Scientific conclusion supported by this task:
- Activation along the overall fault direction was not synchronous.
- The map is more consistent with staged, spatially heterogeneous recruitment of cells, likely controlled by fault geometry and local conditions.
- The Mw 7.1 vicinity does not appear to be among the earliest-activated zones at this grid scale; instead it is associated with comparatively later onset than the Mw 6.4 neighborhood.

### 7. Distance from Mw 6.4 explains part, but not all, of the activation timing; the process is more complex than a simple outward trigger front

The onset-versus-distance plot and summary metric show a moderate positive association between onset time and distance to Mw 6.4, but with large scatter.

Evidence:
- `<PACKAGE_ROOT>/results/exp_run/outputs/01_grid_onset_analysis/figures/grid_onset_vs_distance_mw64.png`
- `<PACKAGE_ROOT>/results/exp_run/outputs/01_grid_onset_analysis/tables/grid_onset_metrics.csv`
- `<PACKAGE_ROOT>/results/exp_run/outputs/01_grid_onset_analysis/tables/grid_cell_onset.csv`
- `<PACKAGE_ROOT>/results/exp_run/outputs/01_grid_onset_analysis/tables/mainshock_reference_table.csv`

Quantitative evidence:
- Spearman correlation of onset time vs distance to Mw 6.4: 0.504918.
- Recomputed Pearson correlation from the cell table: 0.4770.
- Distance-binned medians for activated cells increase with distance:
  - 0–5 km: median 2.25 h
  - 5–10 km: median 5.25 h
  - 10–15 km: median 10.25 h
  - 15–20 km: median 11.50 h

But the scatter plot also shows:
- early activation at some larger distances,
- late activation in some near-source cells,
- broad overlap across distance bins.

Scientific interpretation:
- There is a regional tendency for later activation farther from Mw 6.4.
- However, the large spread means activation cannot be explained by a simple, smoothly propagating front.
- The triggering style is therefore better described as staged and structurally heterogeneous, not purely synchronous and not purely radial-distance controlled.

### 8. Example cell time series confirm that the onset rule distinguishes immediate, delayed, very late, and absent activation behaviors

The example-cell figure demonstrates the actual behavior underlying the onset classifier.

Evidence:
- `<PACKAGE_ROOT>/results/exp_run/outputs/01_grid_onset_analysis/figures/example_cell_time_series.png`
- `<PACKAGE_ROOT>/results/exp_run/outputs/01_grid_onset_analysis/tables/cell_time_series.csv`
- `<PACKAGE_ROOT>/results/exp_run/outputs/01_grid_onset_analysis/tables/grid_cell_onset.csv`

Visible examples include:
- immediate onset at 0.0 h,
- delayed onset at 6.5 h,
- very late onset at 33.0 h,
- no-onset behavior despite multiple counts.

Scientific relevance:
- The classification is not purely visual mapping; it is tied to explicit, reproducible time-series criteria.
- The example panels validate that heterogeneity in onset timing is a real signal in the local rate histories.

## Limitations and Assumptions

- This task analyzed only the interval between the two mainshocks. It does not include pre-Mw 6.4 background comparison or post-Mw 7.1 evolution.
- The onset definition implemented in the outputs is a grid-based sustained-count rule, not the later fault-segment rule requested in the broader project. Specifically, the rule used was count ≥ 2 in a 30-minute bin plus sustained support in following bins, as documented in `<PACKAGE_ROOT>/results/exp_run/outputs/01_grid_onset_analysis/tables/run_parameters.csv`.
- Because the study-area seismicity rate was already high immediately after Mw 6.4, local onset times should not be interpreted as emergence from a quiet background state.
- Only 104 of 445 occupied cells were classified as activated, and 341 occupied cells had no onset. Therefore, spatial onset inferences are based on a minority of occupied cells.
- Most grid cells in the full domain had no events at all (2,523 of 2,968), so the mapped onset field is inherently sparse.
- Grid-based onset estimates depend on the chosen 1 km cell size and 30-minute time binning; different discretizations could shift onset timing and confidence classifications.
- The onset-versus-distance relationship is only moderate and highly scattered, so distance-based interpretation alone is insufficient.
- The handoff flagged `outputs_truncated`, meaning the file inventory in the handoff is partial, although the requested image outputs and listed tables were available and verified.
- No PDF outputs were listed for this task, so there were no PDF products to analyze.

## Report-Ready Summary

Task 01 successfully established a reproducible grid-based onset framework for the Ridgecrest inter-mainshock interval using validated inputs, a 5 km buffered fault-bounded domain, 1 km spatial discretization, and 30-minute seismicity-rate bins. The analysis retained 4,713 events between Mw 6.4 and Mw 7.1 and mapped them onto 2,968 grid cells, of which 445 were occupied and 104 showed detectable activation onset. Core implementation evidence is preserved in `<PACKAGE_ROOT>/results/exp_run/outputs/01_grid_onset_analysis/tables/run_parameters.csv`, `<PACKAGE_ROOT>/results/exp_run/outputs/01_grid_onset_analysis/tables/grid_cell_onset.csv`, and `<PACKAGE_ROOT>/results/exp_run/outputs/01_grid_onset_analysis/tables/cell_time_series.csv`.

Scientifically, the grid-scale results argue against synchronous activation along the fault system. The onset-time distribution is strongly right-skewed, with a median activated-cell onset of 6.25 hours after Mw 6.4 and a long tail to 33 hours, documented in `<PACKAGE_ROOT>/results/exp_run/outputs/01_grid_onset_analysis/figures/grid_onset_histogram_cdf.png` and `<PACKAGE_ROOT>/results/exp_run/outputs/01_grid_onset_analysis/tables/grid_onset_metrics.csv`. The spatial onset map shows that earliest activation clustered near the Mw 6.4 area and along a central-southern fault-aligned corridor, while later activation occurred toward peripheral and northwestern zones nearer the Mw 7.1 side of the system, as shown in `<PACKAGE_ROOT>/results/exp_run/outputs/01_grid_onset_analysis/figures/grid_onset_map.png`. A moderate but scattered onset–distance relation to Mw 6.4 (Spearman 0.504918) indicates some regional outward delay but rules out a simple uniform propagation front; this is supported by `<PACKAGE_ROOT>/results/exp_run/outputs/01_grid_onset_analysis/figures/grid_onset_vs_distance_mw64.png`. Overall, this task supports a staged, structurally heterogeneous activation process between Mw 6.4 and Mw 7.1 and provides the report-ready spatial onset field needed for later fault-segment triggering analysis.