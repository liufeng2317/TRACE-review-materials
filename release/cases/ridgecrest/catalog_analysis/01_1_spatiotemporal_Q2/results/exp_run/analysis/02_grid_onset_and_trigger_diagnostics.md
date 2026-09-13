## Scientific Purpose

This task aimed to quantify how aftershock activation evolved in space between the Mw 6.4 and Mw 7.1 Ridgecrest mainshocks using a reproducible 0.5 km grid and a sustained-activation onset rule. The scientific goal was to test whether post-Mw 6.4 seismicity was spatially synchronous or instead progressed in a staged, cascade-like way, with special attention to whether activation migrated toward the eventual Mw 7.1 source region.

## Method and Implementation Evidence

The implementation discretized the study area defined by the catalog between Mw 6.4 and Mw 7.1 into 0.5 km × 0.5 km cells, producing a grid of 19,758 cells spanning x = 415.0–470.5 km and y = 3904.0–3993.0 km in projected coordinates (`<PACKAGE_ROOT>/results/exp_run/outputs/02_grid_onset_and_trigger_diagnostics/tables/grid_metadata_0p5km.csv`, `<PACKAGE_ROOT>/results/exp_run/outputs/02_grid_onset_and_trigger_diagnostics/tables/grid_definition_0p5km.csv`).

For each cell, the workflow counted events in 30-minute bins over the Mw 6.4 to Mw 7.1 interval, generating local rate time series and event-to-cell assignments (`<PACKAGE_ROOT>/results/exp_run/outputs/02_grid_onset_and_trigger_diagnostics/tables/cell_rate_timeseries_30min.csv`, `<PACKAGE_ROOT>/results/exp_run/outputs/02_grid_onset_and_trigger_diagnostics/tables/event_grid_time_assignments.csv`, `<PACKAGE_ROOT>/results/exp_run/outputs/02_grid_onset_and_trigger_diagnostics/tables/cell_total_counts.csv`).

A sustained-activation onset was defined with explicit rule parameters: at least 1 event in the candidate 30-minute bin, at least 3 total events in the cell, persistence over the next 3 bins with at least 2 active future bins, and at least 3 events in a 4-bin cumulative window (`<PACKAGE_ROOT>/results/exp_run/outputs/02_grid_onset_and_trigger_diagnostics/tables/onset_rule_parameters.csv`, `<PACKAGE_ROOT>/results/exp_run/outputs/02_grid_onset_and_trigger_diagnostics/tables/onset_rule_diagnostics.csv`).

Cell-level onset status and quality were classified as robust, ambiguous, insufficient_data, or inactive, with mapped onset times and geometry metrics relative to the Mw 6.4–Mw 7.1 axis (`<PACKAGE_ROOT>/results/exp_run/outputs/02_grid_onset_and_trigger_diagnostics/tables/cell_activity_quality_flags.csv`, `<PACKAGE_ROOT>/results/exp_run/outputs/02_grid_onset_and_trigger_diagnostics/tables/cell_onset_time_summary.csv`, `<PACKAGE_ROOT>/results/exp_run/outputs/02_grid_onset_and_trigger_diagnostics/tables/cell_onset_time_summary_with_geometry.csv`, `<PACKAGE_ROOT>/results/exp_run/outputs/02_grid_onset_and_trigger_diagnostics/tables/cell_trigger_geometry_metrics.csv`).

Regional and segment-scale comparisons were then used to diagnose trigger style between the Mw 6.4 source region, the intervening corridor, and the eventual Mw 7.1 vicinity (`<PACKAGE_ROOT>/results/exp_run/outputs/02_grid_onset_and_trigger_diagnostics/tables/region_comparison_summary.csv`, `<PACKAGE_ROOT>/results/exp_run/outputs/02_grid_onset_and_trigger_diagnostics/tables/regional_activated_cell_fraction.csv`, `<PACKAGE_ROOT>/results/exp_run/outputs/02_grid_onset_and_trigger_diagnostics/tables/regional_cumulative_event_counts.csv`, `<PACKAGE_ROOT>/results/exp_run/outputs/02_grid_onset_and_trigger_diagnostics/tables/segment_level_onset_summary.csv`, `<PACKAGE_ROOT>/results/exp_run/outputs/02_grid_onset_and_trigger_diagnostics/tables/trigger_style_summary.csv`).

## Key Results and Evidence Files

### 1. The 0.5 km grid is mostly empty, and robust onset times are resolved only in a limited subset of occupied cells

The analysis region contained 19,758 cells, but only 1,086 cells were occupied by at least one event. Of these, 202 cells had robust onset estimates, 210 were ambiguous, and 674 had insufficient data; 18,672 cells were inactive. This means the onset-time interpretation is driven by a relatively sparse but spatially structured subset of the grid rather than uniform regional coverage. Evidence: `<PACKAGE_ROOT>/results/exp_run/outputs/02_grid_onset_and_trigger_diagnostics/tables/onset_qc_summary.csv`, `<PACKAGE_ROOT>/results/exp_run/outputs/02_grid_onset_and_trigger_diagnostics/tables/cell_activity_quality_flags.csv`.

For robust cells, onset times span 0 to 32 hours after Mw 6.4, with median 8.0 hours and mean 10.68 hours. First-event times are generally earlier than onset times, consistent with the rule identifying sustained activation rather than first occurrence. Evidence: `<PACKAGE_ROOT>/results/exp_run/outputs/02_grid_onset_and_trigger_diagnostics/tables/cell_activity_quality_flags.csv`.

### 2. The onset-time map supports staged, fault-aligned activation rather than fully synchronous activation

The mapped onset times form a narrow, segmented NW-SE trending belt rather than a spatially mixed cloud. Earliest robust onset cells cluster near and just southwest of the Mw 6.4 epicentral area and along the central fault-aligned trend, while lighter colors indicate later activation toward other segments, including the branch leading toward the Mw 7.1 epicenter. Gray cells mark ambiguous or insufficiently constrained areas, so the resolved pattern is patchy but clearly not random. Evidence: `<PACKAGE_ROOT>/results/exp_run/outputs/02_grid_onset_and_trigger_diagnostics/figures/ridgecrest_onset_time_map.png`, `<PACKAGE_ROOT>/results/exp_run/outputs/02_grid_onset_and_trigger_diagnostics/tables/cell_onset_time_summary_with_geometry.csv`.

The map therefore favors a staged or cascade-like activation model: neighboring cells along fault traces tend to share similar onset timing locally, but the larger system shows coherent temporal layering from earlier to later zones. This is not the pattern expected for region-wide synchronous activation.

### 3. Activation began near Mw 6.4 and reached the Mw 7.1 vicinity substantially later

Regional comparison shows strong timing asymmetry. In the Mw 6.4 vicinity, the earliest robust onset is 0.0 h and the median onset is 5.5 h. In the Mw 7.1 vicinity, the earliest robust onset is 6.0 h and the median onset is 18.0 h. The intervening corridor is even later, with only one robust cell and a median onset of 24.0 h. Evidence: `<PACKAGE_ROOT>/results/exp_run/outputs/02_grid_onset_and_trigger_diagnostics/tables/region_comparison_summary.csv`.

This timing contrast is also visible in activated-cell fractions. By 6 h after Mw 6.4, 8.6% of Mw 6.4-vicinity cells had activated, while the Mw 7.1 vicinity had only 0.16% activated and the intervening corridor had 0%. Even by 18 h, the Mw 6.4 vicinity reached 13.7% activated while the Mw 7.1 vicinity remained at 3.3%. The corridor did not register any activated cells until 24 h. Evidence: `<PACKAGE_ROOT>/results/exp_run/outputs/02_grid_onset_and_trigger_diagnostics/tables/regional_activated_cell_fraction.csv`.

These results argue against immediate, spatially continuous propagation from Mw 6.4 directly through the corridor into the Mw 7.1 source area. Instead, they indicate strong early activation near Mw 6.4 and delayed activation closer to Mw 7.1.

### 4. Triggering behavior is best characterized as mixed rather than a simple migrating front

The trigger summary explicitly classifies the sequence as `mixed`, based on a 7.5 km half-width regional partition around an Mw 6.4–Mw 7.1 axis of length 11.99 km. The median onset times are 5.5 h in the Mw 6.4 region, 24.0 h in the intervening corridor, and 18.0 h in the Mw 7.1 region. Evidence: `<PACKAGE_ROOT>/results/exp_run/outputs/02_grid_onset_and_trigger_diagnostics/tables/trigger_style_summary.csv`.

This timing pattern does not fit a simple, steadily advancing trigger front. If activation had migrated monotonically from Mw 6.4 toward Mw 7.1, one would expect corridor activation to precede or at least track Mw 7.1-vicinity activation more closely. Instead, the corridor is sparsely active and very late, while the Mw 7.1 vicinity shows delayed but clearer activation. That combination is more consistent with heterogeneous, segmented stress transfer and delayed cascade behavior.

### 5. Segment-scale onset statistics show nonmonotonic progression along strike

The segment summary divides the Mw 6.4–Mw 7.1 axis into ~2 km bins. Median onset times vary irregularly: 13.5 h in the nearest segment, 5.0 h and 6.0 h in the next two segments, 12.5 h in the following segment, then 17.5 h near 8–10 km along strike, and 31.5 h in the farthest sampled segment. Evidence: `<PACKAGE_ROOT>/results/exp_run/outputs/02_grid_onset_and_trigger_diagnostics/tables/segment_level_onset_summary.csv`.

This confirms that activation did not advance as a simple linear wavefront. Some intermediate segments activated early, while others closer to the Mw 7.1 side were much later.

### 6. Geometry diagnostics show delayed activation tends to be farther along strike toward Mw 7.1, but not in a simple deterministic way

The geometry figure indicates broad clustering rather than a single linear trend. In the left panel, onset time versus along-strike distance from Mw 6.4 shows early onsets concentrated near the Mw 6.4 side and selected intermediate positions, with later clusters farther along strike. In the right panel, onset time versus distance to Mw 7.1 shows that the earliest onsets are not concentrated nearest to Mw 7.1; many cells closest to Mw 7.1 activate relatively late. Evidence: `<PACKAGE_ROOT>/results/exp_run/outputs/02_grid_onset_and_trigger_diagnostics/figures/onset_vs_trigger_geometry.png`.

The underlying geometry table supports this interpretation. Across robust cells, onset time has a moderate positive correlation with along-strike distance from Mw 6.4 (r ≈ 0.46) and a moderate negative correlation with distance to Mw 7.1 (r ≈ -0.33), meaning later activation tends to occur farther along the Mw 6.4→Mw 7.1 direction. However, the scatter is substantial, and the figure shows multiple clusters and outliers rather than a single monotonic front. Evidence: `<PACKAGE_ROOT>/results/exp_run/outputs/02_grid_onset_and_trigger_diagnostics/tables/cell_trigger_geometry_metrics.csv`, `<PACKAGE_ROOT>/results/exp_run/outputs/02_grid_onset_and_trigger_diagnostics/tables/cell_onset_time_summary_with_geometry.csv`, `<PACKAGE_ROOT>/results/exp_run/outputs/02_grid_onset_and_trigger_diagnostics/figures/onset_vs_trigger_geometry.png`.

### 7. Event accumulation is strongly imbalanced among regions, with very limited corridor seismicity

Cumulative counts show that the Mw 6.4 vicinity accumulated 2,862 events by the end of the analysis window, while the Mw 7.1 vicinity accumulated 759 and the intervening corridor only 17. Evidence: `<PACKAGE_ROOT>/results/exp_run/outputs/02_grid_onset_and_trigger_diagnostics/tables/regional_cumulative_event_counts.csv`.

This large imbalance helps explain why the corridor has poor onset resolution and why any interpretation of continuous bridge-like triggering through the corridor should be treated cautiously.

## Limitations and Assumptions

The onset rule is reproducible and physically interpretable, but it is still a threshold-based heuristic. The chosen parameters (`threshold_count = 1`, `min_total_events = 3`, persistence over 3 future bins, cumulative count over 4 bins) may influence which cells are labeled robust, ambiguous, or insufficient (`<PACKAGE_ROOT>/results/exp_run/outputs/02_grid_onset_and_trigger_diagnostics/tables/onset_rule_parameters.csv`).

Coverage is sparse at the grid scale. Only 202 of 19,758 cells have robust onset times, and 674 occupied cells lack sufficient data for robust onset estimation. Consequently, mapped activation is discontinuous and should not be interpreted as a fully resolved front (`<PACKAGE_ROOT>/results/exp_run/outputs/02_grid_onset_and_trigger_diagnostics/tables/onset_qc_summary.csv`).

The corridor between Mw 6.4 and Mw 7.1 is especially data-poor: only 8 occupied cells and 1 robust onset cell. Therefore, conclusions about whether rupture preparation required a continuously active corridor are weakly constrained by this dataset (`<PACKAGE_ROOT>/results/exp_run/outputs/02_grid_onset_and_trigger_diagnostics/tables/region_comparison_summary.csv`).

The visual interpretation of `<PACKAGE_ROOT>/results/exp_run/outputs/02_grid_onset_and_trigger_diagnostics/figures/onset_vs_trigger_geometry.png` is partly limited because marker color and size are not explicitly documented in the rendered figure itself. The main report should therefore rely primarily on axis relationships and accompanying tables, not unlabeled symbol encodings.

All onset times are relative to the Mw 6.4 event and limited to the Mw 6.4-to-Mw 7.1 window. The results describe pre-Mw 7.1 evolution only and do not address post-Mw 7.1 behavior.

## Report-Ready Summary

A 0.5 km grid-based onset analysis of the Ridgecrest sequence between the Mw 6.4 and Mw 7.1 mainshocks shows that post-Mw 6.4 activation was not spatially synchronous. Instead, robust onset times define a segmented, fault-aligned pattern in which the earliest sustained activation occurred near the Mw 6.4 source region, while the vicinity of the future Mw 7.1 hypocentral area activated substantially later. Median robust onset is 5.5 h in the Mw 6.4 vicinity, 18.0 h near Mw 7.1, and 24.0 h in the intervening corridor, with the corridor also containing very few events and only one robust onset cell (`<PACKAGE_ROOT>/results/exp_run/outputs/02_grid_onset_and_trigger_diagnostics/tables/region_comparison_summary.csv`, `<PACKAGE_ROOT>/results/exp_run/outputs/02_grid_onset_and_trigger_diagnostics/tables/trigger_style_summary.csv`).

The onset map and geometry diagnostics indicate a mixed trigger style: activation tends overall to progress toward the Mw 7.1 side, but not as a simple monotonic front. Instead, there are discrete early and delayed activation clusters, consistent with heterogeneous stress transfer and cascade-like failure on segmented structures rather than continuous synchronous activation or a uniformly propagating trigger front (`<PACKAGE_ROOT>/results/exp_run/outputs/02_grid_onset_and_trigger_diagnostics/figures/ridgecrest_onset_time_map.png`, `<PACKAGE_ROOT>/results/exp_run/outputs/02_grid_onset_and_trigger_diagnostics/figures/onset_vs_trigger_geometry.png`).