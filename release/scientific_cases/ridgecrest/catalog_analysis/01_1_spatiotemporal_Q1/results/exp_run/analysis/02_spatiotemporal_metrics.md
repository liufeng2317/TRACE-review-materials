## Scientific Purpose

This task computed quantitative spatiotemporal diagnostics for the Ridgecrest relocated catalog to support interpretation of earthquake migration, fault-zone orientation, spatial spread, and clustering through the Mw 6.4 to Mw 7.1 sequence. The outputs are directly relevant to the report questions on whether post-Mw 6.4 seismicity propagated in one or multiple directions, whether the organization changed approaching Mw 7.1, and whether a new trigger zone emerged after Mw 7.1.

The task did not produce figures, and no image or PDF outputs were present in `<PACKAGE_ROOT>/results/exp_run/outputs/02_spatiotemporal_metrics`. Therefore, the scientific evidence for this task is entirely contained in the CSV and JSON metric tables:
- `<PACKAGE_ROOT>/results/exp_run/outputs/02_spatiotemporal_metrics/window_metrics_whole_sequence.csv`
- `<PACKAGE_ROOT>/results/exp_run/outputs/02_spatiotemporal_metrics/window_metrics_post64_hourly.csv`
- `<PACKAGE_ROOT>/results/exp_run/outputs/02_spatiotemporal_metrics/window_cluster_metrics_whole_sequence.csv`
- `<PACKAGE_ROOT>/results/exp_run/outputs/02_spatiotemporal_metrics/window_cluster_metrics_post64_hourly.csv`
- `<PACKAGE_ROOT>/results/exp_run/outputs/02_spatiotemporal_metrics/comparison_metrics_64.csv`
- `<PACKAGE_ROOT>/results/exp_run/outputs/02_spatiotemporal_metrics/comparison_metrics_71.csv`
- `<PACKAGE_ROOT>/results/exp_run/outputs/02_spatiotemporal_metrics/migration_summary_64_to_71.json`
- `<PACKAGE_ROOT>/results/exp_run/outputs/02_spatiotemporal_metrics/migration_summary_post71.json`

## Method and Implementation Evidence

The implementation computed window-based spatial diagnostics for the relocated Ridgecrest sequence using time windows prepared by the prior QC task. Runtime configuration is documented in `<PACKAGE_ROOT>/results/exp_run/outputs/02_spatiotemporal_metrics/metrics_runtime_config.json`.

Scientifically relevant implementation elements evidenced by that configuration and the output schemas are:

- A local Cartesian reference frame was used to measure centroid positions and spatial spreads in kilometers.
- The reference along-strike axis was defined by the Mw 6.4-to-Mw 7.1 epicentral connection, with azimuth `311.8963°` and length `11.9923 km`, recorded in `<PACKAGE_ROOT>/results/exp_run/outputs/02_spatiotemporal_metrics/metrics_runtime_config.json`.
- For each time window, the task computed:
  - event count and magnitude/depth summaries,
  - centroid location,
  - principal-axis azimuth,
  - major/minor spread and anisotropy ratio,
  - footprint area,
  - centroid position in along-strike/cross-strike coordinates relative to the Mw 6.4–Mw 7.1 axis,
  - distances/azimuths from the Mw 6.4 and Mw 7.1 epicenters,
  - stepwise centroid migration and cumulative migration.
- Window-level clustering diagnostics were derived with DBSCAN using `eps = 2.5 km` and `min_samples = 12`, with cluster summaries written to:
  - `<PACKAGE_ROOT>/results/exp_run/outputs/02_spatiotemporal_metrics/window_cluster_metrics_whole_sequence.csv`
  - `<PACKAGE_ROOT>/results/exp_run/outputs/02_spatiotemporal_metrics/window_cluster_metrics_post64_hourly.csv`
- Comparison tables aggregate before/after-mainshock distributions for Mw 6.4 and Mw 7.1:
  - `<PACKAGE_ROOT>/results/exp_run/outputs/02_spatiotemporal_metrics/comparison_metrics_64.csv`
  - `<PACKAGE_ROOT>/results/exp_run/outputs/02_spatiotemporal_metrics/comparison_metrics_71.csv`
- Parallel computation was used, with `n_jobs_used = 16` and `max_cores = 64`, documented in `<PACKAGE_ROOT>/results/exp_run/outputs/02_spatiotemporal_metrics/metrics_runtime_config.json`.

## Key Results and Evidence Files

### 1. The Mw 6.4 mainshock was followed by a large expansion and a marked reorganization of seismicity relative to the pre-Mw 6.4 background

The pre-Mw 6.4 interval contained only `43` events, whereas the Mw 6.4-to-Mw 7.1 interval contained `5205` events. The centroid shifted by `10.62 km` toward azimuth `194.93°`, the principal-axis orientation changed by `33.63°`, and occupied area increased by `2319.53 km²`. The along-/cross-strike centroid changes were `-4.82 km` and `+9.46 km`, respectively, indicating that the post-Mw 6.4 sequence was displaced strongly off the pre-event distribution and became organized in a new geometry rather than merely intensifying in place.

Evidence:
- `<PACKAGE_ROOT>/results/exp_run/outputs/02_spatiotemporal_metrics/comparison_metrics_64.csv`

Important values from that file:
- Pre-Mw 6.4 principal axis: `337.57°`
- Post-Mw 6.4 principal axis: `11.20°`
- Pre-Mw 6.4 footprint area: `777.86 km²`
- Post-Mw 6.4 footprint area: `3097.39 km²`
- Pre-Mw 6.4 anisotropy ratio: `4.50`
- Post-Mw 6.4 anisotropy ratio: `1.53`

Interpretation for the report: the Mw 6.4 event initiated a much broader and less linearly concentrated aftershock domain than the sparse foreshock pattern, with a measurable change in dominant orientation.

### 2. Between Mw 6.4 and Mw 7.1, seismicity did not simply migrate as a single coherent front; it evolved in multiple clusters with modest net centroid drift but substantial cumulative internal reorganization

The summary for the Mw 6.4-to-Mw 7.1 period shows:
- `34` windows with events,
- cumulative centroid travel of `38.23 km`,
- mean centroid step distance `1.16 km`,
- net centroid shift only `1.26 km` toward azimuth `263.26°`,
- median cluster count `2`,
- multi-cluster window fraction `0.647`,
- dominant cluster fraction median `0.715`,
- orientation change class `strong_change`,
- dominant orientation `16.39°`.

Evidence:
- `<PACKAGE_ROOT>/results/exp_run/outputs/02_spatiotemporal_metrics/migration_summary_64_to_71.json`

This combination is scientifically important: the large cumulative travel but very small net displacement means the centroid wandered substantially from window to window, yet the overall center of activity remained in roughly the same area. That is more consistent with repeated activation of nearby subclusters than with smooth, one-directional migration.

Supporting window-scale evidence from `<PACKAGE_ROOT>/results/exp_run/outputs/02_spatiotemporal_metrics/window_metrics_whole_sequence.csv`:
- Early 2-hour windows after Mw 6.4 have centroid azimuths from Mw 6.4 mostly around `225–237°`, with centroid distances from Mw 6.4 around `4.4–5.7 km`.
- At the same time, the centroid azimuth from Mw 7.1 is around `153–160°`, meaning those early clusters sit southeast of the Mw 7.1 hypocentral area.
- Principal-axis azimuths in those windows vary from roughly `13.8°` to `39.0°`, indicating changing local geometry rather than a perfectly fixed lineament.

Supporting clustering evidence from `<PACKAGE_ROOT>/results/exp_run/outputs/02_spatiotemporal_metrics/window_cluster_metrics_whole_sequence.csv` and `<PACKAGE_ROOT>/results/exp_run/outputs/02_spatiotemporal_metrics/window_cluster_metrics_post64_hourly.csv`:
- Some early windows contain one dominant cluster near azimuth `~224–235°` from Mw 6.4, but later hourly windows before Mw 7.1 show `2–4` clusters.
- Near the end of the Mw 6.4-to-Mw 7.1 period, dominant cluster azimuths shift to `~272–308°` from Mw 6.4 in several windows, evidencing activation northwest of the Mw 6.4 hypocenter.

Interpretation for the report: after Mw 6.4, the sequence first concentrated in a southwestern/southern sector relative to Mw 6.4, then progressively involved additional clusters, including northwestern sectors closer to the eventual Mw 7.1 rupture zone. This supports a multi-cluster transfer of activity rather than a simple single-front trigger.

### 3. Hourly post-Mw 6.4 diagnostics show a transition from early south-to-southwest concentration to later northwestward cluster activation approaching Mw 7.1

The hourly table `<PACKAGE_ROOT>/results/exp_run/outputs/02_spatiotemporal_metrics/window_metrics_post64_hourly.csv` resolves the fine-scale evolution.

Early hours after Mw 6.4:
- Window 0 centroid azimuth from Mw 7.1: `151.71°`
- Window 1: `154.62°`
- Window 2: `157.28°`
- Distances from Mw 7.1 remain `~11.5–13.1 km`

This indicates that immediate post-Mw 6.4 seismicity was located mostly southeast of the future Mw 7.1 area.

Late pre-Mw 7.1 hourly clustering from `<PACKAGE_ROOT>/results/exp_run/outputs/02_spatiotemporal_metrics/window_cluster_metrics_post64_hourly.csv`:
- Window 25 dominant cluster azimuth from Mw 6.4: `272.48°`
- Window 26: `287.46°`
- Window 30: `308.00°`
- Window 31: `294.26°`
- Window 32: `275.89°`
- Window 33: `276.13°`

These azimuths document late activation in the west-to-northwest quadrant relative to Mw 6.4. Some windows also show multiple clusters, for example:
- Window 26: `3` clusters
- Window 32: `4` clusters

Interpretation for the report: the detailed hourly sequence suggests that the Mw 6.4 aftershock field was not stationary. It began with activity concentrated south/southwest of the Mw 6.4 hypocenter and southeast of the Mw 7.1 hypocenter, then broadened and increasingly activated west-to-northwest subclusters closer to the eventual Mw 7.1 rupture domain. That pattern is consistent with progressive structural loading or cascading activation across interconnected fault segments.

### 4. The Mw 7.1 mainshock introduced a clearer northwest-trending organization, larger footprint, and northward/northwestward relocation of the active zone

The before/after Mw 7.1 comparison shows a major reorganization:
- Event count increased from `5205` to `8647` over the 2 days after Mw 7.1.
- Centroid shifted `14.96 km` toward azimuth `335.95°`.
- Principal-axis orientation changed by `46.34°`.
- Footprint area increased by `3142.53 km²`.
- Along-strike centroid increased by `13.66 km`; cross-strike centroid decreased by `-6.10 km`.
- The post-Mw 7.1 centroid lies only `3.82 km` from Mw 7.1 but `15.64 km` from Mw 6.4.

Evidence:
- `<PACKAGE_ROOT>/results/exp_run/outputs/02_spatiotemporal_metrics/comparison_metrics_71.csv`

Orientation also rotated from:
- Pre-Mw 7.1 principal axis: `11.20°`
- Post-Mw 7.1 principal axis: `324.87°`

Because `324.87°` is equivalent to a NW-SE trend, the post-Mw 7.1 sequence is substantially more aligned with a northwest-trending structure than the pre-Mw 7.1 interval.

Interpretation for the report: Mw 7.1 did not simply amplify the pre-existing Mw 6.4 aftershock field. It shifted the active centroid north-northwest toward the Mw 7.1 epicentral region, enlarged the rupture-zone footprint, and established a more northwest-oriented spatial organization.

### 5. After Mw 7.1, seismicity remained persistently multi-clustered, but its dominant orientation became more stable than in the Mw 6.4-to-Mw 7.1 interval

The post-Mw 7.1 summary reports:
- `16` windows with events,
- cumulative centroid distance `12.31 km`,
- mean centroid step `0.82 km`,
- net centroid shift `6.03 km` toward azimuth `139.68°`,
- median cluster count `2`,
- multi-cluster window fraction `1.0`,
- dominant cluster fraction median `0.766`,
- dominant orientation `326.16°`,
- orientation change class `stable`.

Evidence:
- `<PACKAGE_ROOT>/results/exp_run/outputs/02_spatiotemporal_metrics/migration_summary_post71.json`

Compared with the pre-Mw 7.1 stage, the post-Mw 7.1 stage is therefore characterized by:
- more persistent multi-cluster behavior (`100%` of windows versus `64.7%`),
- a stronger NW-trending dominant orientation (`326.16°`),
- less erratic orientation behavior (`stable` versus `strong_change`).

Additional support from `<PACKAGE_ROOT>/results/exp_run/outputs/02_spatiotemporal_metrics/window_cluster_metrics_whole_sequence.csv`:
- 6-hour windows after Mw 7.1 + 1 day commonly contain `2–5` clusters.
- Dominant cluster centroids are typically at azimuths `~301–311°` from Mw 6.4 and distances `~6.1–8.5 km`, indicating sustained concentration on the northwestern fault system.
- In the final listed window, the dominant cluster remains close to Mw 7.1-domain activity at azimuth `292.21°` and distance `4.89 km` from Mw 6.4, with additional secondary clusters also present in the JSON-encoded cluster centroid fields.

Interpretation for the report: after Mw 7.1, the sequence became spatially broader and more consistently organized along the northwestern rupture system, while still retaining multiple contemporaneous clusters rather than collapsing to one compact aftershock cloud.

## Limitations and Assumptions

- No image or PDF outputs were present in `<PACKAGE_ROOT>/results/exp_run/outputs/02_spatiotemporal_metrics`; therefore, the analysis is based entirely on tabular and JSON diagnostics rather than direct map inspection.
- The interpretation depends on the chosen reference axis between Mw 6.4 and Mw 7.1, documented in `<PACKAGE_ROOT>/results/exp_run/outputs/02_spatiotemporal_metrics/metrics_runtime_config.json`. Along-strike and cross-strike changes are meaningful relative to that axis, not as absolute tectonic truth.
- Cluster identification depends on DBSCAN parameters (`eps = 2.5 km`, `min_samples = 12`). Different parameter choices could change cluster counts and dominant-cluster fractions.
- Orientation metrics are principal-axis estimates from spatial covariance and may be unstable when event geometry is broad, multi-lobed, or nearly isotropic.
- The pre-Mw 6.4 comparison is based on only `43` events, so pre/post Mw 6.4 differences are robust qualitatively but the exact pre-mainshock orientation and spread values are less statistically stable.
- Net centroid shift can be small even when physically important migration occurs across multiple branches; this is why cumulative centroid distance and cluster metrics are essential complementary evidence.
- The post-Mw 7.1 summary window begins after the Mw 7.1 mainshock and extends into later sequence evolution, but this task alone does not identify physical triggering mechanism in a causal sense; it quantifies migration and reorganization patterns that can support later mechanistic interpretation.

## Report-Ready Summary

Task 02 provides quantitative evidence that the Ridgecrest sequence evolved through staged, organized but multi-cluster spatiotemporal reconfiguration rather than through a simple single-front migration.

Before Mw 6.4, seismicity was sparse (`43` events) and had a different geometry from the large aftershock field that followed. After Mw 6.4 and before Mw 7.1, the sequence expanded dramatically to `5205` events, the active-area footprint increased by `2319.5 km²`, and the principal-axis orientation changed by `33.6°` relative to the pre-Mw 6.4 distribution, as documented in `<PACKAGE_ROOT>/results/exp_run/outputs/02_spatiotemporal_metrics/comparison_metrics_64.csv`.

The Mw 6.4-to-Mw 7.1 interval is best described as a multi-cluster transfer stage. The centroid accumulated `38.23 km` of motion across `34` windows, but the net shift was only `1.26 km`, while `64.7%` of windows contained multiple clusters and the orientation behavior is classified as `strong_change`, according to `<PACKAGE_ROOT>/results/exp_run/outputs/02_spatiotemporal_metrics/migration_summary_64_to_71.json`. Hourly post-Mw 6.4 diagnostics show that the earliest activity was concentrated south to southwest of Mw 6.4 and southeast of the future Mw 7.1 zone, while later pre-Mw 7.1 hours increasingly activated west-to-northwest clusters, evidenced by dominant-cluster azimuths shifting into the `~272–308°` range from Mw 6.4 in `<PACKAGE_ROOT>/results/exp_run/outputs/02_spatiotemporal_metrics/window_cluster_metrics_post64_hourly.csv`.

Mw 7.1 marks a stronger geometric reorganization. Relative to the Mw 6.4-to-Mw 7.1 stage, the post-Mw 7.1 two-day interval shifted the seismicity centroid `14.96 km` toward azimuth `335.95°`, increased footprint area by `3142.53 km²`, and rotated the principal axis by `46.34°` to a NW-trending orientation (`324.87°`), as shown in `<PACKAGE_ROOT>/results/exp_run/outputs/02_spatiotemporal_metrics/comparison_metrics_71.csv`. The post-Mw 7.1 stage remained multi-clustered in every analyzed window, but with a more stable dominant NW orientation (`326.16°`) than the more variable pre-Mw 7.1 stage, according to `<PACKAGE_ROOT>/results/exp_run/outputs/02_spatiotemporal_metrics/migration_summary_post71.json`.

Overall, these metrics support the interpretation that Mw 6.4 initiated distributed activation across several nearby structures, with progressive transfer toward northwestern clusters that likely prepared the Mw 7.1 rupture zone, and that Mw 7.1 then reorganized the sequence into a broader, more stably NW-trending aftershock system.