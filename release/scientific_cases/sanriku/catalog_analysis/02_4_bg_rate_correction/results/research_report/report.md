---
author:
- TRACE
date: 2026-05-24
title: Regional Background-Rate Assessment of the 2025–2026 Aomori Seismic Activity
---

# Abstract

This report evaluates whether the 2025–2026 Aomori activity was exceptional relative to the 2020–2026 background seismicity, using the long-term raw JMA/Hi-net catalog as the background reference and a relocated/filtered active-period catalog as the high-resolution sequence dataset. To preserve catalog consistency, the long-term catalog was filtered to a common spatial domain defined from the relocated active-period footprint before any background comparison. The common region spans 38.353003–42.532633$`^{\circ}`$N and 140.851921–144.64847$`^{\circ}`$E. Cross-catalog audit results show that larger events are highly consistent in the overlap period and support robust long-term comparison primarily for $`M\geq 3`$, $`M\geq 4`$, and $`M\geq 5`$.

Within that harmonized domain, the 2025-10 to 2026-05 active period is clearly exceptional relative to the 2020–2026 background. In the common region, observed versus expected counts are 1267 versus 348.38 for $`M\geq 3`$, 259 versus 62.62 for $`M\geq 4`$, 68 versus 12.03 for $`M\geq 5`$, and 13 versus 1.95 for $`M\geq 6`$, corresponding to percentile ranks of about 98.5–99.6. The strongest anomaly is concentrated in the shallow 0–30 km portion of the `m1_m3_local_union`, which remains extreme after bootstrap and random-window controls. The anomaly is therefore best interpreted as a localized-to-subregional rate pulse superposed on a weaker broader regional elevation, rather than as a spatially uniform regional increase. The results are statistical only and do not demonstrate physical triggering or any specific mechanism.

# Scientific Objective

The objective was to build a regional background-rate model for the Aomori earthquake catalog system and use it to test whether the 2025–2026 activity was exceptional relative to the 2020–2026 background. The required workflow separated two catalog roles:

- the long-term raw catalog as the background-rate reference; and

- the relocated/filtered active-period catalog as the fine-scale dataset for spatial, temporal, and depth decomposition during the active interval.

A critical constraint was that the two catalogs were *not* to be merged as if they were homogeneous products. Instead, a common analysis region had to be defined from the active relocated catalog footprint, and the long-term raw catalog had to be filtered to that same spatial mask before any long-term versus active-period comparison. This report follows that requirement explicitly.

The main scientific questions were:

1.  Is the 2025–2026 Aomori active period exceptional relative to the 2020–2026 background within the common analysis region?

2.  Which regions and depth ranges show the strongest rate anomalies?

3.  Are the anomalies localized or part of a broader regional rate pulse?

4.  Does the M1–M3 local region remain anomalous after background correction?

5.  Can M2 outer-band activity be explained by broader regional background changes?

6.  Which observations are statistically strong enough to justify later physical follow-up?

# Data, Catalog Roles, and Implementation Choices

## Catalogs and actual data used

The long-term reference catalog was the raw product spanning 2020-01-01 to 2026-05-22. The requested active-period file was unavailable, and the workflow substituted the resolved relocated catalog documented in the task diagnostics. The actual active-period catalog used in the analysis was: <a href="<CASE_ROOT>/data/catalog/Snet_catalog_relocate_250930_260501.csv" class="uri"><CASE_ROOT>/data/catalog/Snet_catalog_relocate_250930_260501.csv</a>. This substitution is documented in the task outputs and should be retained in any reproducibility discussion.

## Common-region definition

A common analysis region was defined from the active relocated catalog footprint with a 0.15$`^{\circ}`$ buffer, and the long-term raw catalog was filtered to that same mask before background-rate estimation. The resulting common region is:

<div class="center">

38.353003–42.532633$`^{\circ}`$N, –144.64847$`^{\circ}`$E.

</div>

This step is essential because the long-term raw catalog extends well beyond the relocated footprint and would otherwise bias rate comparisons.

Figure <a href="#fig:footprints" data-reference-type="ref" data-reference="fig:footprints">1</a> shows the footprint mismatch and the adopted common domain.

<figure id="fig:footprints" data-latex-placement="H">
<img src="<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/01_aomori_background_rate_analysis/figures/01_catalog_footprints_common_region.png" style="width:82.0%" />
<figcaption>Catalog footprints and the common analysis region used for all primary long-term versus active-period comparisons. The long-term raw catalog extends beyond the relocated active-period footprint, which justifies spatial harmonization before anomaly testing.</figcaption>
</figure>

## Catalog audit and threshold reliability

The audit established the evidence chain needed for defensible rate comparison:

- Long-term raw catalog size: 227,755 events.

- Active relocated catalog size: 22,096 events.

- After common-region filtering: 159,087 long-term events and 22,090 active-period events.

- Retention fractions: 0.6985 for the long-term catalog and 0.9997 for the active catalog.

- Estimated magnitude completeness by maximum curvature: $`M_c = 1.15`$ for the long-term common-region catalog and $`M_c = 1.45`$ for the active common-region catalog.

These results support the following threshold policy:

- **Preferred for cross-catalog background comparison:** $`M\geq 3`$, $`M\geq 4`$, $`M\geq 5`$.

- **Descriptive only:** $`M\geq 2`$ where count support is limited.

- **Restricted to active-period internal analysis:** $`M\geq 1.2`$, unless additional completeness justification is provided.

## Crosswalk consistency in the overlap period

Within the overlap period and common region, event counts are similar at larger magnitudes: raw versus relocated counts are 1389 versus 1267 for $`M\geq 3`$, 280 versus 259 for $`M\geq 4`$, 69 versus 68 for $`M\geq 5`$, and 13 versus 13 for $`M\geq 6`$. Matched-event diagnostics show essentially identical magnitudes and very small differences in origin time, location, and depth. Figure <a href="#fig:matchdiff" data-reference-type="ref" data-reference="fig:matchdiff">2</a> documents this consistency and supports the use of higher-magnitude thresholds for the long-term background comparison.

<figure id="fig:matchdiff" data-latex-placement="H">
<img src="<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/01_aomori_background_rate_analysis/figures/03_matched_event_differences.png" style="width:82.0%" />
<figcaption>Matched large-event differences between the long-term raw and relocated catalogs in the overlap period. The small timing, location, and depth offsets support strong cross-catalog consistency for larger events.</figcaption>
</figure>

# Background-Rate Modeling Strategy

The long-term background model was estimated from the spatially filtered 2020–2026 raw catalog, using monthly windows and region-specific baselines. The active-period decomposition used the relocated catalog for internal fine-scale temporal, regional, and depth structure. This separation preserves the intended roles of each catalog:

1.  the raw catalog provides the background-rate reference; and

2.  the relocated catalog provides the active-period structural detail.

The primary regions discussed in the evidence are the `common_region`, `m1_m3_local_union`, `m2_near_field`, `m2_outer_band`, and `control_region`. Depth partitions include 0–30 km, 30–60 km, and $`>60`$ km. Heavy bootstrap/random-window controls were applied only to $`M\geq 3`$, $`M\geq 4`$, and $`M\geq 5`$, with 4000 resamples per combination.

# Results

## Was the 2025–2026 active period exceptional relative to the 2020–2026 background?

Yes. Within the common region, the full active period from 2025-10 to 2026-05 is clearly exceptional relative to the long-term background. The main quantitative results are:

<div class="center">

| Threshold   | Observed | Expected | Obs./Exp. | Percentile |
|:------------|:--------:|:--------:|:---------:|:----------:|
| $`M\geq 3`$ |   1267   |  348.38  |   3.64    |   98.49    |
| $`M\geq 4`$ |   259    |  62.62   |   4.14    |   98.49    |
| $`M\geq 5`$ |    68    |  12.03   |   5.65    |   98.73    |
| $`M\geq 6`$ |    13    |   1.95   |   6.68    |   99.62    |

</div>

These statistics come from the primary background-comparison outputs of Task 01. They show that the active-period counts exceed expectation by factors of about 3.6 to 6.7 across robust thresholds, with percentile ranks near the top of the 2020–2026 distribution.

The bootstrap and random-window control analysis further strengthens this conclusion for the robust thresholds $`M\geq 3`$, $`M\geq 4`$, and $`M\geq 5`$. For the shallow common region (0–30 km), the control summary reports:

- $`M\geq 3`$: primary obs./exp. $`= 5.38`$, random percentile $`= 98.8`$, outside-period percentile $`= 100.0`$;

- $`M\geq 4`$: primary obs./exp. $`= 5.82`$, random percentile $`= 98.8`$, outside-period percentile $`= 100.0`$;

- $`M\geq 5`$: primary obs./exp. $`= 7.22`$, random percentile $`= 98.5`$, outside-period percentile $`= 100.0`$.

Therefore, the active interval is not only elevated relative to the long-term mean; it also ranks among the most extreme comparable windows in the available 2020–2026 record.

## Are the anomalies localized or part of a broader regional pulse?

The results favor a **localized-to-subregional rate pulse** rather than a spatially uniform regional increase. Several lines of evidence support this interpretation.

First, region-level full-period anomaly measures differ strongly among subregions. The `m1_m3_local_union` shows the highest excess, the M2-related regions are also elevated, and the `control_region` is much weaker. For the full active period:

- `m1_m3_local_union`: obs./exp. $`= 10.51`$, 11.14, 12.35, and 12.52 for $`M\geq 3`$, $`M\geq 4`$, $`M\geq 5`$, and $`M\geq 6`$, with percentile ranks from 98.87 to 100.0.

- `m2_near_field`: obs./exp. $`= 4.82`$, 5.14, 6.35, and 6.12, with percentile ranks from 95.71 to 100.0.

- `m2_outer_band`: obs./exp. $`= 3.38`$, 2.99, 2.79, and 6.64, with percentile ranks from 98.63 to 100.0.

- `control_region`: obs./exp. $`= 0.97`$, 1.36, 1.90, and 1.22, with percentile ranks from 59.52 to 88.17 except for a sparse $`M\geq 6`$ cell.

Second, the control-resampled results show strong spatial decay. Many $`>60`$ km bins are near zero or unstable, while shallow 0–30 km bins in the M1–M3 local union, the common region, and selected M2-related zones remain strongly elevated. This combination indicates that the anomaly is not domain-wide and homogeneous.

Third, the spatial anomaly mapping from Task 01 is described as patchy rather than uniform, with strongest positive clusters near the M1–M3 and M2-related areas and mixed or negative cells elsewhere. Together, these outputs indicate a broader active interval with important regional coherence, but they do not support an interpretation of evenly elevated seismicity across the entire study domain.

## Which regions and depth ranges show the strongest anomalies?

The strongest anomaly is the shallow 0–30 km portion of the `m1_m3_local_union`. This is the most stable conclusion across the primary evidence matrix and the control-resampled analysis.

Representative Task 01 matrix values for `m1_m3_local_union | 0--30 km` are:

- $`M\geq 3`$: observed 637, expected 82.77, obs./exp. $`= 7.70`$;

- $`M\geq 4`$: observed 139, expected 15.79, obs./exp. $`= 8.80`$;

- $`M\geq 5`$: observed 44, expected 4.56, obs./exp. $`= 9.64`$.

The control summary then identifies the same cells as the top anomalies after bootstrap/random-window resampling:

- `m1_m3_local_union | 0--30 km | `$`M\geq 4`$: random ratio mean $`= 94.10`$, random percentile $`= 99.1`$, outside percentile $`= 100.0`$;

- `m1_m3_local_union | 0--30 km | `$`M\geq 5`$: random ratio mean $`= 58.97`$, random percentile $`= 99.1`$, outside percentile $`= 100.0`$;

- `m1_m3_local_union | 0--30 km | `$`M\geq 3`$: random ratio mean $`= 32.49`$, random percentile $`= 98.9`$, outside percentile $`= 100.0`$.

These cells are shown visually in Figures <a href="#fig:ratioheat" data-reference-type="ref" data-reference="fig:ratioheat">3</a> and <a href="#fig:percheat" data-reference-type="ref" data-reference="fig:percheat">4</a>.

<figure id="fig:ratioheat" data-latex-placement="H">
<img src="<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/02_aomori_bootstrap_controls/figures/01_bootstrap_control_ratio_heatmap.png" style="width:82.0%" />
<figcaption>Control-resampled anomaly ratio heatmap for selected thresholds. The dominant hotspot is the shallow <code>m1_m3_local_union</code>, with additional elevated bins in the shallow common region and selected M2-related zones.</figcaption>
</figure>

<figure id="fig:percheat" data-latex-placement="H">
<img src="<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/02_aomori_bootstrap_controls/figures/02_bootstrap_control_percentile_heatmap.png" style="width:82.0%" />
<figcaption>Control-resampled percentile heatmap. The main target bins cluster near the 99th–100th percentile, while many far-field and deep bins are weak, zero-valued, or unstable because of sparse counts.</figcaption>
</figure>

Beyond the M1–M3 local union, the shallow common region and selected M2-related bins are also strong. In particular:

- `common_region | 0--30 km | `$`M\geq 5`$: primary obs./exp. $`= 7.22`$, random percentile $`= 98.5`$;

- `m2_near_field | 30--60 km | `$`M\geq 4`$: primary obs./exp. $`= 5.37`$, random percentile $`= 98.2`$;

- `m2_near_field | 30--60 km | `$`M\geq 5`$: primary obs./exp. $`= 7.31`$, random percentile $`= 100.0`$;

- `m2_outer_band | 0--30 km | `$`M\geq 4`$: primary obs./exp. $`= 5.05`$, random percentile $`= 98.9`$;

- `m2_outer_band | 0--30 km | `$`M\geq 3`$: primary obs./exp. $`= 5.53`$, random percentile $`= 98.9`$.

Thus, the strongest signal is shallow, but some 30–60 km M2-related bins are also statistically notable.

## Does the M1–M3 local region remain anomalous after background correction?

Yes. This is the clearest single conclusion of the analysis. The M1–M3 local union remains strongly anomalous after:

- filtering the long-term raw catalog to the same common spatial domain,

- normalizing by long-term regional background,

- stratifying by depth, and

- applying bootstrap/random-window controls based on the long-term record.

The full-period percentile results already place this region near the top of the background distribution for every robust threshold. The control-resampled outputs then show that the shallow 0–30 km M1–M3 cells remain among the strongest anomalies in the entire matrix. This supports a firm statistical conclusion: the M1–M3 local region cannot be reduced to a minor byproduct of a weak domain-wide uplift.

## Can M2 outer-band activity be explained by broader background-rate changes?

Only partly. The evidence indicates that the M2 outer band participates in a broader regional active interval, but it also shows localized excess beyond what is seen in the control region.

For the full active period, `m2_outer_band` has percentile ranks near 98.6–100.0 for $`M\geq 3`$ through $`M\geq 6`$, with obs./exp. ratios of 3.38, 2.99, 2.79, and 6.64. In the primary evidence matrix, the shallow 0–30 km outer-band values are consistently elevated across thresholds, with obs./exp. values of 4.21 for $`M\geq 1.2`$, 4.67 for $`M\geq 2`$, 5.53 for $`M\geq 3`$, 4.39 for $`M\geq 4`$, and 4.26 for $`M\geq 5`$.

The control results strengthen this interpretation selectively rather than uniformly. The strongest supported outer-band bins are shallow 0–30 km at $`M\geq 3`$ and $`M\geq 4`$, while deeper and far-field bins are much weaker or sparse. Meanwhile, the control region remains much less elevated. Therefore, the best-supported statistical interpretation is that the M2 outer band is *not fully explained* by a generic regional background-rate rise. Instead, it appears to combine broader regional activation with its own localized enhancement, especially in the shallow depth range.

## Depth structure of the anomaly

The anomaly is dominated by shallow seismicity. Task 01 reports that the 0–30 km depth bin carries the strongest rate peaks, with secondary contribution from 30–60 km and little support for a strong $`>60`$ km anomaly. Representative values include:

- `common_region | 0--30 km | `$`M\geq 5`$: obs./exp. $`= 7.22`$;

- `common_region | 30--60 km | `$`M\geq 5`$: obs./exp. $`= 2.74`$;

- `common_region | `$`>60`$` km | `$`M\geq 5`$: obs./exp. $`= 1.00`$.

For M2-related regions, some 30–60 km bins are statistically strong, but the very deep bins remain weak or unstable. The control heatmaps also show many $`>60`$ km bins at 0 or near 0, reinforcing the interpretation that the principal anomaly is shallow to intermediate depth, not deep.

## Temporal structure: uniform rise or burst-like sequence?

The active period is burst-like rather than uniform. Task 01 identifies three main episodes aligned with M1, M2, and M3:

- an initial strong burst around M1 in mid-November 2025,

- the largest burst around M2 in December 2025,

- a renewed major burst around M3 in late April 2026.

The sequence therefore contains multiple distinct pulses within a broader elevated interval. The regional decomposition indicates partial synchrony, but not perfect regional coherence: the M1–M3 local union dominates the November and late-April phases, while the M2 outer band dominates the December pulse. This supports a segmented view of the activity rather than a single homogeneous rate increase through time.

## Robustness to control-window choice

The control comparison using all long-term random windows and windows outside the active dates does not materially change the main conclusions. Figure <a href="#fig:scatter" data-reference-type="ref" data-reference="fig:scatter">5</a> shows that the two control definitions are closely aligned, with the strongest anomalies remaining strong under both schemes.

<figure id="fig:scatter" data-latex-placement="H">
<img src="<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/02_aomori_bootstrap_controls/figures/03_random_vs_outside_control_scatter.png" style="width:72.0%" />
<figcaption>Comparison of anomaly ratios using all long-term random windows versus windows outside the active dates. The close alignment indicates that the main anomaly conclusions are not an artifact of control-window definition.</figcaption>
</figure>

# Integrated Interpretation

The combined evidence supports the following interpretation.

1.  **The 2025–2026 Aomori active period is exceptional relative to the 2020–2026 background within the common analysis region.** This conclusion is supported by both direct observed-versus-expected comparisons and heavy random-window/bootstrap controls at the most reliable thresholds.

2.  **The strongest anomalies are localized, especially in the shallow M1–M3 local union.** This is the dominant result across the evidence matrix, percentile analysis, and control resampling.

3.  **The anomaly is not purely local.** The shallow common region also shows strong excess, and selected M2-related regions are statistically elevated. This indicates a broader regional active interval.

4.  **The anomaly is not spatially uniform.** The weak control-region response and weak or unstable deep/far-field bins argue against a homogeneous region-wide pulse.

5.  **The M2 outer band is statistically interesting.** Its shallow bins exceed background expectations and are stronger than the control region, so a simple explanation by broad background change alone is not adequate.

6.  **The anomaly is primarily shallow.** Intermediate-depth involvement exists in selected bins, but there is little robust evidence for a major deep anomaly.

7.  **The temporal evolution is burst-like.** The sequence contains multiple distinct pulses associated with M1, M2, and M3 rather than a single flat elevation.

# Limitations and Reporting Constraints

The conclusions above are scientifically useful but should be read with several explicit limitations.

- **Active-period file substitution.** The requested active-period filename was missing. The analysis used the resolved relocated catalog at <a href="<CASE_ROOT>/data/catalog/Snet_catalog_relocate_250930_260501.csv" class="uri"><CASE_ROOT>/data/catalog/Snet_catalog_relocate_250930_260501.csv</a>. This does not invalidate the workflow, but it should be disclosed for reproducibility.

- **Magnitude completeness uncertainty.** Completeness was estimated by maximum curvature, with $`M_c \approx 1.15`$ for the long-term common region and $`M_c \approx 1.45`$ for the active common region. Therefore, low-magnitude cross-catalog comparisons are less secure than the main $`M\geq 3`$ to $`M\geq 5`$ results.

- **Sparse-bin inflation.** Some large obs./exp. or control-ratio values arise from very small expected counts, especially in high-magnitude or depth-partitioned bins. Such values are better interpreted as rarity indicators than as precise effect-size estimates.

- **Depth consistency.** The relocated catalog is shallower and underrepresents deeper seismicity relative to the raw catalog. Consequently, negative or weak findings below 60 km should remain descriptive.

- **Finite background window.** The reference period spans 2020-01-01 to 2026-05-22. This is adequate for the requested task but does not capture possible decade-scale nonstationarity.

- **No mechanism inference.** These are catalog-level statistical results only. They do not demonstrate triggering, slow slip, fluid migration, stress transfer, or fault interaction.

# Key Evidence Files

The principal machine-readable outputs used in this report are listed below for traceability.

| Artifact | Absolute path |
|:---|:---|
| Artifact | Absolute path |
| Common-region footprint figure | <a href="<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/01_aomori_background_rate_analysis/figures/01_catalog_footprints_common_region.png" class="uri"><CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/01_aomori_background_rate_analysis/figures/01_catalog_footprints_common_region.png</a> |
| Matched-event difference figure | <a href="<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/01_aomori_background_rate_analysis/figures/03_matched_event_differences.png" class="uri"><CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/01_aomori_background_rate_analysis/figures/03_matched_event_differences.png</a> |
| Catalog QA summary | <a href="<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/01_aomori_background_rate_analysis/tables/catalog_qa_summary.csv" class="uri"><CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/01_aomori_background_rate_analysis/tables/catalog_qa_summary.csv</a> |
| Common-region retention | <a href="<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/01_aomori_background_rate_analysis/tables/common_region_retention.csv" class="uri"><CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/01_aomori_background_rate_analysis/tables/common_region_retention.csv</a> |
| Magnitude completeness summary | <a href="<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/01_aomori_background_rate_analysis/tables/magnitude_completeness_summary.csv" class="uri"><CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/01_aomori_background_rate_analysis/tables/magnitude_completeness_summary.csv</a> |
| Long-term background rates | <a href="<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/01_aomori_background_rate_analysis/tables/long_term_background_rates.csv" class="uri"><CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/01_aomori_background_rate_analysis/tables/long_term_background_rates.csv</a> |
| Active-period percentile summary | <a href="<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/01_aomori_background_rate_analysis/tables/active_period_percentile_vs_background.csv" class="uri"><CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/01_aomori_background_rate_analysis/tables/active_period_percentile_vs_background.csv</a> |
| Primary evidence matrix | <a href="<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/01_aomori_background_rate_analysis/tables/background_rate_evidence_matrix.csv" class="uri"><CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/01_aomori_background_rate_analysis/tables/background_rate_evidence_matrix.csv</a> |
| Control evidence matrix | <a href="<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/02_aomori_bootstrap_controls/tables/background_rate_evidence_matrix_with_controls.csv" class="uri"><CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/02_aomori_bootstrap_controls/tables/background_rate_evidence_matrix_with_controls.csv</a> |
| Bootstrap/random-window controls | <a href="<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/02_aomori_bootstrap_controls/tables/bootstrap_random_window_controls.csv" class="uri"><CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/02_aomori_bootstrap_controls/tables/bootstrap_random_window_controls.csv</a> |
| Control ratio heatmap | <a href="<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/02_aomori_bootstrap_controls/figures/01_bootstrap_control_ratio_heatmap.png" class="uri"><CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/02_aomori_bootstrap_controls/figures/01_bootstrap_control_ratio_heatmap.png</a> |
| Control percentile heatmap | <a href="<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/02_aomori_bootstrap_controls/figures/02_bootstrap_control_percentile_heatmap.png" class="uri"><CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/02_aomori_bootstrap_controls/figures/02_bootstrap_control_percentile_heatmap.png</a> |
| Control scatter plot | <a href="<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/02_aomori_bootstrap_controls/figures/03_random_vs_outside_control_scatter.png" class="uri"><CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/02_aomori_bootstrap_controls/figures/03_random_vs_outside_control_scatter.png</a> |
| Bootstrap/control text summary | <a href="<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/02_aomori_bootstrap_controls/summary_report.txt" class="uri"><CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/02_aomori_bootstrap_controls/summary_report.txt</a> |

# Conclusions

The statistical answer to the main question is clear: **the 2025–2026 Aomori active period is exceptional relative to the 2020–2026 background within the common analysis region**. The strongest evidence comes from the harmonized common-region comparison and is reinforced by bootstrap/random-window controls at $`M\geq 3`$, $`M\geq 4`$, and $`M\geq 5`$.

The most prominent anomaly is the shallow 0–30 km portion of the `m1_m3_local_union`, which remains extreme after regional correction and control resampling. Selected M2-related bins are also strongly elevated, especially the shallow `m2_outer_band` and intermediate-depth `m2_near_field`. The control region is much weaker, and many deep bins are weak or unstable. Accordingly, the anomaly is best described as a **localized-to-subregional rate pulse** rather than a spatially uniform regional increase.

For later physical follow-up, the most statistically interesting observations are:

1.  strong common-region exceptionality across robust thresholds $`M\geq 3`$–$`M\geq 5`$ and even at $`M\geq 6`$ in the primary comparison;

2.  persistent, shallow, and very strong anomaly in the `m1_m3_local_union`;

3.  shallow excess in the `m2_outer_band` beyond the control-region response;

4.  selective but notable 30–60 km enhancement in parts of the M2 near field; and

5.  a burst-like temporal structure with distinct M1, M2, and M3 pulses rather than a single uniform increase.

These findings justify targeted physical investigation, but they should remain separated from mechanism claims. The present report establishes statistical anomaly support, not causation.
