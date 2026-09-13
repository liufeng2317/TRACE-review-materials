## Scientific Purpose

This task resolved the internal spatial ordering of pre-Mw 7.1 seismic activation within the two fixed fault-oriented corridors and the two near-mainshock diagnostic neighborhoods after the Mw 6.4 Ridgecrest mainshock. The scientific aim was to determine whether activation inside each domain was spatially coherent, patchy, or directionally evolving, and to test whether the Mw 7.1-related system showed delayed activation relative to the Mw 6.4-related system.

## Method and Implementation Evidence

A fixed 0.5 km × 0.5 km grid was applied to the pre-Mw 7.1 time window for the two previously defined corridors (Region A and Region B) and the two 10 km-radius diagnostic neighborhoods around the Mw 6.4 and Mw 7.1 epicenters. For each cell, the outputs include cumulative event count, cumulative energy, first post-Mw 6.4 activation time, and peak-rate timing at 30 min and 1 h resolution. Time-versus-along-strike heatmaps were also constructed using 30 min and 1 h bins.

Implementation details are documented in `<PACKAGE_ROOT>/results/exp_run/outputs/03_gridded_activation_ordering/metadata/gridded_activation_metadata.json`, which records:
- grid cell size = 0.5 km,
- corridor and neighborhood grid size = 0.5 km,
- time resolutions = 0.5 h and 1.0 h,
- first activation defined as the first post-Mw 6.4 event time in each cell,
- peak-rate time defined as the center of the highest-count bin,
- maximum analysis window = 33.7678 h until Mw 7.1,
- parallel jobs = 64.

Primary machine-readable evidence was saved as:
- `<PACKAGE_ROOT>/results/exp_run/outputs/03_gridded_activation_ordering/tables/corridor_cell_activation_table_all_regions.csv`
- `<PACKAGE_ROOT>/results/exp_run/outputs/03_gridded_activation_ordering/tables/region_a_cell_activation_table.csv`
- `<PACKAGE_ROOT>/results/exp_run/outputs/03_gridded_activation_ordering/tables/region_b_cell_activation_table.csv`
- `<PACKAGE_ROOT>/results/exp_run/outputs/03_gridded_activation_ordering/tables/mw6.4_neighborhood_cell_activation_table.csv`
- `<PACKAGE_ROOT>/results/exp_run/outputs/03_gridded_activation_ordering/tables/mw7.1_neighborhood_cell_activation_table.csv`
- `<PACKAGE_ROOT>/results/exp_run/outputs/03_gridded_activation_ordering/tables/region_a_along_strike_summary.csv`
- `<PACKAGE_ROOT>/results/exp_run/outputs/03_gridded_activation_ordering/tables/region_b_along_strike_summary.csv`
- `<PACKAGE_ROOT>/results/exp_run/outputs/03_gridded_activation_ordering/tables/region_a_time_along_heatmap_table.csv`
- `<PACKAGE_ROOT>/results/exp_run/outputs/03_gridded_activation_ordering/tables/region_b_time_along_heatmap_table.csv`

Key visual evidence was saved as:
- `<PACKAGE_ROOT>/results/exp_run/outputs/03_gridded_activation_ordering/figures/corridor_cumulative_seismicity_maps.png`
- `<PACKAGE_ROOT>/results/exp_run/outputs/03_gridded_activation_ordering/figures/corridor_first_activation_maps.png`
- `<PACKAGE_ROOT>/results/exp_run/outputs/03_gridded_activation_ordering/figures/first_activation_vs_along_strike.png`
- `<PACKAGE_ROOT>/results/exp_run/outputs/03_gridded_activation_ordering/figures/neighborhood_first_activation_maps.png`
- `<PACKAGE_ROOT>/results/exp_run/outputs/03_gridded_activation_ordering/figures/time_vs_along_strike_heatmaps.png`

## Key Results and Evidence Files

### 1. Region A activated more broadly and earlier than Region B before Mw 7.1

Cell-level summaries show that Region A had a much larger active fraction and earlier activation than Region B:
- Region A: 403 activated cells of 600 total (67.2%), median first activation = 4.99 h.
- Region B: 411 activated cells of 1212 total (33.9%), median first activation = 7.71 h.

These values come from:
- `<PACKAGE_ROOT>/results/exp_run/outputs/03_gridded_activation_ordering/tables/region_a_cell_activation_table.csv`
- `<PACKAGE_ROOT>/results/exp_run/outputs/03_gridded_activation_ordering/tables/region_b_cell_activation_table.csv`

The map comparison in `<PACKAGE_ROOT>/results/exp_run/outputs/03_gridded_activation_ordering/figures/corridor_first_activation_maps.png` supports this: Region A shows a denser, more continuous belt of early activation aligned with its corridor, while Region B shows a more localized early core and broader delayed areas.

### 2. Region A was more spatially continuous; Region B was more segmented and internally heterogeneous

The cumulative seismicity maps show both regions concentrate activity along fault-parallel bands, but with different organization:
- Region A forms a narrow, comparatively continuous diagonal band with several hotspots.
- Region B is broader but more segmented, with activity concentrated in discrete axial clusters and sparser ends.

This is visible in `<PACKAGE_ROOT>/results/exp_run/outputs/03_gridded_activation_ordering/figures/corridor_cumulative_seismicity_maps.png`.

The along-strike summaries quantify where activity concentrated:
- Region A strongest bins are near 16.25–21.25 km, with first activation mostly <1.3 h and counts up to 129 events.
- Region B strongest bins are near 24.75–33.25 km, with several early bins (<0.5 h) but also an important delayed segment near 21.75 km with first activation = 10.86 h and 105 events.

Evidence:
- `<PACKAGE_ROOT>/results/exp_run/outputs/03_gridded_activation_ordering/tables/region_a_along_strike_summary.csv`
- `<PACKAGE_ROOT>/results/exp_run/outputs/03_gridded_activation_ordering/tables/region_b_along_strike_summary.csv`

### 3. Neither corridor shows simple monotonic migration; Region B exhibits stronger delayed-patch behavior

The first-activation-versus-along-strike plots explicitly test ordering:
- Region A: correlation r = -0.35 in the figure; direct table-based cell calculation gives corr ≈ -0.21 and slope ≈ -0.26 h/km.
- Region B: correlation r = -0.11 in the figure; direct cell calculation gives corr ≈ -0.32 and slope ≈ -0.41 h/km.

Despite weak negative trends, the scatter is large and not compatible with a simple propagating front. Region A is dominated by mostly rapid activation with scattered delays, whereas Region B contains clearly delayed patches superimposed on early-active segments.

This is shown in:
- `<PACKAGE_ROOT>/results/exp_run/outputs/03_gridded_activation_ordering/figures/first_activation_vs_along_strike.png`
- `<PACKAGE_ROOT>/results/exp_run/outputs/03_gridded_activation_ordering/tables/region_a_cell_activation_table.csv`
- `<PACKAGE_ROOT>/results/exp_run/outputs/03_gridded_activation_ordering/tables/region_b_cell_activation_table.csv`

The figure interpretation is consistent with heterogeneous triggering rather than steady along-strike migration.

### 4. Time-versus-along-strike heatmaps show broad early activation in Region A but banded, delayed strengthening in Region B

The 30 min heatmaps provide the clearest internal-ordering view:
- Region A shows activity across much of the along-strike range from early times, especially over approximately 15–21 km, with no single coherent migration front.
- Region B shows persistent activity in several preferred along-strike bands, but one zone near ~21–22 km strengthens later, after roughly 17–18 h, relative to earlier-active bands near ~25 km and ~32 km.

This supports delayed patch activation within Region B rather than uniform system-wide onset.

Evidence:
- `<PACKAGE_ROOT>/results/exp_run/outputs/03_gridded_activation_ordering/figures/time_vs_along_strike_heatmaps.png`
- `<PACKAGE_ROOT>/results/exp_run/outputs/03_gridded_activation_ordering/tables/region_a_time_along_heatmap_table.csv`
- `<PACKAGE_ROOT>/results/exp_run/outputs/03_gridded_activation_ordering/tables/region_b_time_along_heatmap_table.csv`

### 5. The Mw 7.1 neighborhood activated later and less extensively than the Mw 6.4 neighborhood

The circular neighborhood diagnostics isolate local behavior around the two mainshock areas:
- Mw 6.4 neighborhood: 478 activated cells of 1264 (37.8%), median first activation = 5.86 h, median 30 min peak time = 9.75 h.
- Mw 7.1 neighborhood: 299 activated cells of 1264 (23.7%), median first activation = 13.61 h, median 30 min peak time = 17.25 h.

This is strong quantitative evidence that the Mw 7.1 epicentral area activated later than the Mw 6.4 epicentral area.

Evidence tables:
- `<PACKAGE_ROOT>/results/exp_run/outputs/03_gridded_activation_ordering/tables/mw6.4_neighborhood_cell_activation_table.csv`
- `<PACKAGE_ROOT>/results/exp_run/outputs/03_gridded_activation_ordering/tables/mw7.1_neighborhood_cell_activation_table.csv`

The map comparison in `<PACKAGE_ROOT>/results/exp_run/outputs/03_gridded_activation_ordering/figures/neighborhood_first_activation_maps.png` visually agrees: the Mw 6.4 neighborhood contains more widespread early purple/blue cells, whereas the Mw 7.1 neighborhood has fewer activated cells overall and a larger share of later colors.

### 6. Energy release was strongly dominated by Region B and especially by the Mw 7.1 neighborhood, despite slower local activation

Cumulative energy totals show a major contrast:
- Region A cumulative energy ≈ 2.57 × 10^14
- Region B cumulative energy ≈ 3.09 × 10^15
- Mw 6.4 neighborhood cumulative energy ≈ 2.70 × 10^14
- Mw 7.1 neighborhood cumulative energy ≈ 2.83 × 10^15

Thus, the slower and sparser local activation near the Mw 7.1 area did not imply lower pre-Mw 7.1 energy release; instead, that domain accumulated much larger total energy, likely reflecting the influence of fewer larger events. This result should be interpreted together with Task 02 energy-time diagnostics.

Evidence:
- `<PACKAGE_ROOT>/results/exp_run/outputs/03_gridded_activation_ordering/tables/region_b_cell_activation_table.csv`
- `<PACKAGE_ROOT>/results/exp_run/outputs/03_gridded_activation_ordering/tables/mw7.1_neighborhood_cell_activation_table.csv`

## Limitations and Assumptions

- This task analyzes only the interval from the Mw 6.4 mainshock to immediately before the Mw 7.1 event; it does not address post-Mw 7.1 evolution.
- First activation is defined as the first observed cataloged event in a 0.5 km cell after Mw 6.4. Therefore, results depend on catalog completeness, relocation quality, and the chosen grid size.
- Spatial ordering is evaluated using fixed corridor geometry inherited from Task 01. If real fault activation deviates from the prescribed corridor centerlines or widths, some complexity may be projected into apparent heterogeneity.
- The visual and tabular evidence argues against simple monotonic migration, but this task did not fit explicit physical migration models; the conclusion is descriptive rather than mechanistic.
- Energy totals at cell or neighborhood scale can be dominated by a few larger events, so cumulative energy contrasts should be interpreted jointly with event-count and activation-time evidence.
- No warnings or failed outputs were recorded in the handoff for this task. The handoff status is success: `<PACKAGE_ROOT>/results/exp_run/log/coding_progress/task_handoff/03_gridded_activation_ordering.json`.

## Report-Ready Summary

Task 03 provides direct spatial evidence that the two fault-oriented systems responded differently after the Mw 6.4 mainshock. Region A activated earlier and more broadly, with 67.2% of corridor cells activated and median first activation at 4.99 h, whereas Region B activated less extensively (33.9% of cells) and later (median 7.71 h), based on `<PACKAGE_ROOT>/results/exp_run/outputs/03_gridded_activation_ordering/tables/region_a_cell_activation_table.csv` and `<PACKAGE_ROOT>/results/exp_run/outputs/03_gridded_activation_ordering/tables/region_b_cell_activation_table.csv`. The first-activation maps and cumulative count maps (`<PACKAGE_ROOT>/results/exp_run/outputs/03_gridded_activation_ordering/figures/corridor_first_activation_maps.png`, `<PACKAGE_ROOT>/results/exp_run/outputs/03_gridded_activation_ordering/figures/corridor_cumulative_seismicity_maps.png`) show that Region A was comparatively continuous along its axial band, while Region B was more segmented and patchy.

Internal ordering within both corridors does not support a simple end-to-end migration front. Instead, `<PACKAGE_ROOT>/results/exp_run/outputs/03_gridded_activation_ordering/figures/first_activation_vs_along_strike.png` and `<PACKAGE_ROOT>/results/exp_run/outputs/03_gridded_activation_ordering/figures/time_vs_along_strike_heatmaps.png` indicate heterogeneous triggering: Region A shows broad early activation across multiple along-strike sectors, whereas Region B contains delayed patches superimposed on a few early-active bands, including a later-strengthening segment around ~21–22 km along strike. The circular neighborhood comparison independently confirms that the Mw 7.1 epicentral area activated later than the Mw 6.4 area: the Mw 6.4 neighborhood has median first activation 5.86 h and 37.8% activated cells, while the Mw 7.1 neighborhood has median first activation 13.61 h and only 23.7% activated cells, from `<PACKAGE_ROOT>/results/exp_run/outputs/03_gridded_activation_ordering/tables/mw6.4_neighborhood_cell_activation_table.csv` and `<PACKAGE_ROOT>/results/exp_run/outputs/03_gridded_activation_ordering/tables/mw7.1_neighborhood_cell_activation_table.csv`. Overall, this task supports a model in which the Mw 6.4 rupture rapidly activated its conjugate corridor, while the Mw 7.1-related system underwent more delayed, spatially heterogeneous preparatory activation rather than synchronous, spatially uniform triggering.