## Scientific Purpose

This task built a statistical background-rate framework for the Aomori sequence by explicitly separating two roles: the long-term raw catalog as the 2020–2026 background reference, and the active-period relocated catalog as the higher-resolution dataset for the 2025-10 to 2026-05 activation. The central scientific aim was to test whether the 2025–2026 activity was exceptional relative to background only within a common spatial domain supported by both catalogs, and then determine which regions, depth ranges, magnitude thresholds, and time windows carried the strongest anomaly signal.

The outputs directly address the required questions of whether the active period is unusual, whether anomalies are localized or regionally distributed, whether the M1–M3 local area remains anomalous after regional correction, and whether M2 outer-band activity can be explained by broader regional rate changes. The analysis is statistical only and does not infer physical triggering or source processes, consistent with the task requirements. Key summary evidence is provided in `<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/01_aomori_background_rate_analysis/summary_report.txt` and the anomaly tables under `<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/01_aomori_background_rate_analysis/tables/`.

## Method and Implementation Evidence

A common analysis region was defined from the active relocated catalog footprint with a 0.15° buffer, then the long-term raw catalog was filtered to that same mask before any long-term versus active-period comparison. The common region is documented numerically in `<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/01_aomori_background_rate_analysis/tables/region_definitions.csv` as a bounding box of 38.353003–42.532633°N and 140.851921–144.64847°E, and visually in `<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/01_aomori_background_rate_analysis/figures/01_catalog_footprints_common_region.png`. That figure shows the long-term catalog extending well beyond the relocated footprint, validating the need for spatial harmonization.

Catalog audit and crosswalk evidence indicate that the long-term raw catalog contains 227,755 events over 2020-01-01 to 2026-05-22, while the active relocated catalog contains 22,096 events over 2025-10-01 to 2026-05-01 (`/tables/catalog_qa_summary.csv`). After common-region filtering, 159,087 long-term events and 22,090 active events remain, corresponding to retention fractions of 0.6985 and 0.9997, respectively (`/tables/common_region_retention.csv`). Magnitude completeness was estimated by maximum curvature: Mc = 1.15 for the long-term common-region catalog and Mc = 1.45 for the active common-region catalog (`/tables/magnitude_completeness_summary.csv`). Threshold guidance was therefore made explicit in `/tables/threshold_reliability.csv`: M≥3, M≥4, and M≥5 are preferred for cross-catalog comparison; M≥2 is usable but may be sparse/descriptive; M≥1.2 is retained for active-period relocated analysis only unless completeness is further justified.

Overlap-period crosswalk results support treating larger events as consistent between catalogs. In the overlap period and common region, counts are similar at higher magnitudes: raw versus relocated are 1389 versus 1267 for M≥3, 280 versus 259 for M≥4, 69 versus 68 for M≥5, and 13 versus 13 for M≥6 (`/tables/overlap_threshold_counts.csv`). The matched-event diagnostics for larger events show essentially identical magnitudes and very small differences in origin time, epicentral location, and depth (`/tables/matched_large_events.csv` and `/figures/03_matched_event_differences.png`). The figure indicates time differences mostly in hundredths of a second, location differences mostly ~0.02–0.15 km, and depth differences generally within a few tenths of a kilometer, showing that large-event cross-catalog consistency is strong and that relocation mostly makes minor adjustments rather than redefining major events.

Long-term background rates were estimated from the spatially filtered raw catalog in monthly windows for the common region and subregions (`/tables/long_term_background_rates.csv`). These baseline rates were then used to compute expected counts and percentile ranks for the full active period and shorter windows (`/tables/active_period_percentile_vs_background.csv`). Active-period regional decomposition used the relocated catalog and compared `m1_m3_local_union`, `m2_near_field`, `m2_outer_band`, and `control_region`, with time evolution shown in `/figures/05_active_period_rates.png`, `/figures/06_active_region_comparison.png`, and `/figures/07_depth_stratified_rates.png`. Spatial anomaly mapping at M≥3 is provided by `/tables/spatial_anomaly_grid_M3.csv` and `/figures/08_spatial_anomaly_map_M3.png`. A synthesized evidence matrix across region, depth, and magnitude is given in `/tables/background_rate_evidence_matrix.csv` and `/figures/10_background_rate_evidence_matrix.png`.

One implementation caveat is documented in `/diagnostics/context_paths_and_notes.csv`: the requested active-period file `<CASE_ROOT>/data/Snet_catalog_20251001_20260501_filter.csv` did not exist, so the analysis resolved to `<CASE_ROOT>/data/catalog/Snet_catalog_relocate_250930_260501.csv`.

## Key Results and Evidence Files

### 1. The 2025-10 to 2026-05 activity is statistically exceptional relative to the 2020–2026 background within the common analysis region

The strongest direct evidence comes from `/tables/active_period_percentile_vs_background.csv` and `/figures/09_active_period_percentiles.png`. For the full active period in the common region, observed counts greatly exceed expected background counts:

- M≥3: observed 1267, expected 348.38, obs/exp 3.64, percentile 98.49
- M≥4: observed 259, expected 62.62, obs/exp 4.14, percentile 98.49
- M≥5: observed 68, expected 12.03, obs/exp 5.65, percentile 98.73
- M≥6: observed 13, expected 1.95, obs/exp 6.68, percentile 99.62

These values are also summarized in `/summary_report.txt`. The long-term monthly-rate figure `/figures/04_long_term_monthly_rates.png` shows that the active period stands out sharply against the 2020–2025 background in the common region, with very large spikes during the shaded active interval across M≥3, M≥4, and M≥5. Before the active period, M≥3 rates are in the tens per month and M≥4 rates in low single digits to ~10; during the active period they surge to about ~400 per month for M≥3, ~90 for M≥4, and ~30 for M≥5.

This supports a clear report-ready conclusion: within the common region, the active period is not a routine fluctuation of the 2020–2026 background and is exceptional across multiple reliable long-term thresholds.

### 2. Preferred long-term comparison thresholds are M≥3, M≥4, and M≥5; M≥1.2 should be restricted to active-period internal analysis

Completeness and overlap evidence support threshold reliability decisions. `/tables/magnitude_completeness_summary.csv` gives Mc = 1.15 for the long-term common region and Mc = 1.45 for the active common region, while `/figures/02_magnitude_depth_comparison.png` shows the relocated catalog thinning more strongly at low magnitudes and at depths >60 km. `/tables/threshold_reliability.csv` explicitly states that M≥3, M≥4, and M≥5 are preferred for cross-catalog comparison, M≥2 is descriptive only if sparse, and M≥1.2 is not reliable for long-term comparison.

The overlap counts also show that higher-magnitude event retention is strong between catalogs: 259/280 retained at M≥4, 68/69 at M≥5, and 13/13 at M≥6 (`/tables/overlap_threshold_counts.csv`). Therefore the anomaly claims based on M≥3–M≥5 are the most defensible for long-term background comparison, while low-magnitude active-period results are better interpreted as internal sequence structure rather than background-reference evidence.

### 3. The strongest anomalies are localized, not uniformly regionwide, and they concentrate in the M1–M3 local union and around the M2 system

Spatial and regional comparisons point to localized hotspots superposed on a weaker broader regional elevation. `/figures/08_spatial_anomaly_map_M3.png` maps log10(observed/expected) for M≥3 and shows patchy positive anomalies rather than a domain-wide uniform increase. The strongest positive clusters lie near approximately 142.4–143.3°E, 40.8–41.3°N and 143.2–143.8°E, 39.0–39.7°N, with mixed or negative cells elsewhere. The corresponding grid values are archived in `/tables/spatial_anomaly_grid_M3.csv`.

The region-level full active-period comparisons in `/tables/active_period_percentile_vs_background.csv` show:

- `m1_m3_local_union`: M≥3 obs/exp 10.51, percentile 98.87; M≥4 obs/exp 11.14, percentile 99.10; M≥5 obs/exp 12.35, percentile 99.10; M≥6 obs/exp 12.52, percentile 100.0
- `m2_near_field`: M≥3 obs/exp 4.82, percentile 95.71; M≥4 obs/exp 5.14, percentile 98.16; M≥5 obs/exp 6.35, percentile 100.0; M≥6 obs/exp 6.12, percentile 100.0
- `m2_outer_band`: M≥3 obs/exp 3.38, percentile 98.68; M≥4 obs/exp 2.99, percentile 98.63; M≥5 obs/exp 2.79, percentile 98.73; M≥6 obs/exp 6.64, percentile 100.0
- `control_region`: M≥3 obs/exp 0.97, percentile 59.52; M≥4 obs/exp 1.36, percentile 82.33; M≥5 obs/exp 1.90, percentile 88.17; M≥6 obs/exp 1.22, percentile 72.15

These values show that the target subregions are highly exceptional relative to background, whereas the control region is much less so. The percentile heatmap `/figures/09_active_period_percentiles.png` makes this contrast visually obvious: the target windows are mostly in the 96th–100th percentile range, while the control region is only moderate.

Thus, the anomalies are not best described as a uniform broad regional pulse; they are concentrated in specific areas, especially the M1–M3 local union and the M2-associated regions.

### 4. The M1–M3 local region remains strongly anomalous after regional background correction

This is one of the clearest results. In `/tables/background_rate_evidence_matrix.csv` and `/figures/10_background_rate_evidence_matrix.png`, the M1–M3 local union shows the highest observed/expected ratios in the matrix. Notable cells include:

- `m1_m3_local_union | 0–30 km | M≥3`: observed 637, expected 82.77, obs/exp 7.70
- `m1_m3_local_union | 0–30 km | M≥4`: observed 139, expected 15.79, obs/exp 8.80
- `m1_m3_local_union | 0–30 km | M≥5`: observed 44, expected 4.56, obs/exp 9.64
- `m1_m3_local_union | 30–60 km | M≥5`: observed 1, expected 0.09, obs/exp 10.96

The full active-period regional percentiles in `/tables/active_period_percentile_vs_background.csv` also place `m1_m3_local_union` near the top across all reliable thresholds, with 98.87–100th percentile ranks. The regional time-series figure `/figures/06_active_region_comparison.png` shows this region producing a very large early-November burst and another strong late-April burst, both much stronger than the control region. Therefore, after using the common-region background as the reference, the M1–M3 local region still remains highly anomalous and cannot be reduced to a modest byproduct of a weak regional uplift.

### 5. M2 outer-band activity exceeds background expectations and is not fully explained by the broader control-region background

The `m2_outer_band` does show significant anomaly relative to its own long-term background. In `/tables/active_period_percentile_vs_background.csv`, its active-period percentile ranks are 98.68, 98.63, 98.73, and 100.0 for M≥3 through M≥6, with obs/exp ratios of 3.38, 2.99, 2.79, and 6.64. In the evidence matrix (`/tables/background_rate_evidence_matrix.csv`), the shallow 0–30 km portion of `m2_outer_band` is consistently elevated:

- M≥1.2: 4.21
- M≥2: 4.67
- M≥3: 5.53
- M≥4: 4.39
- M≥5: 4.26

By contrast, the control region is much weaker, especially at M≥3 where the full active-period obs/exp is 0.97 with percentile 59.5 (`/tables/active_period_percentile_vs_background.csv`). The regional comparison figure `/figures/06_active_region_comparison.png` shows that the outer band hosts the largest December spike in 7-day counts, around ~2000, clearly exceeding both `m2_near_field` and the control region. These results argue that M2 outer-band activity is not adequately explained as a simple reflection of a common background rise seen everywhere; it carries its own localized excess above regional controls.

### 6. The main activation is dominated by shallow seismicity, with secondary contribution from 30–60 km and little support for strong >60 km anomalies

Depth-stratified evidence is consistent across the figure and matrix products. `/figures/07_depth_stratified_rates.png` shows that 0–30 km dominates the active-period rate evolution, with strong peaks in mid-November 2025, mid-December 2025, and late April 2026. The 30–60 km bin responds mainly during December 2025 and more weakly in late April 2026, while the ≥60 km bin remains low and noisy with no major swarm-scale escalation.

The background evidence matrix confirms this depth contrast (`/tables/background_rate_evidence_matrix.csv`). Examples:

- `common_region | 0–30 km | M≥5`: obs/exp 7.22
- `common_region | 30–60 km | M≥5`: obs/exp 2.74
- `common_region | ≥60 km | M≥5`: obs/exp 1.00

- `m2_near_field | 30–60 km | M≥5`: obs/exp 7.31
- `m2_near_field | ≥60 km | M≥5`: obs/exp 0.00

- `m2_outer_band | 0–30 km | M≥3`: obs/exp 5.53
- `m2_outer_band | ≥60 km | M≥3`: obs/exp 0.10

- `control_region | 30–60 km | M≥3`: obs/exp 0.69
- `control_region | ≥60 km | M≥3`: obs/exp 0.30

The main scientific interpretation is that the 2025–2026 anomaly is overwhelmingly a shallow-to-mid crustal phenomenon in statistical terms, with the shallow 0–30 km bin carrying the dominant signal and >60 km depths contributing little anomaly evidence.

### 7. The active period consists of multiple temporally distinct bursts rather than a single uniform rate increase

The time-series products show a burst-decay structure with three main episodes aligned with M1, M2, and M3. `/figures/05_active_period_rates.png` presents daily and 7-day counts for the relocated active catalog. It shows:

- an initial strong burst around M1 in mid-November 2025
- the largest burst around M2 in December 2025
- a renewed large burst around M3 in late April 2026
- sustained but lower background between these peaks, without full return to the early-October baseline

`/figures/06_active_region_comparison.png` adds regional structure: `m1_m3_local_union` peaks strongly in November and again in late April, `m2_outer_band` dominates the December episode, `m2_near_field` rises sharply but less strongly than the outer band in December, and the control region shows only moderate increases. This indicates partial synchrony within a broader active interval, but with important spatial segmentation of the main pulses rather than one perfectly coherent regional rate pulse.

### 8. Long-term background levels differ substantially by region, which matters for interpreting anomaly strength

The long-term monthly baselines in `/tables/long_term_background_rates.csv` show that anomaly interpretation depends on region-specific background productivity. For example, monthly M≥3 mean background counts are:

- common_region: 56.26
- m1_m3_local_union: 12.04
- m2_near_field: 4.31
- m2_outer_band: 17.91
- control_region: 24.09

For M≥4, the means are 10.16, 2.34, 0.86, 3.50, and 4.05, respectively. These differences explain why modest absolute counts can still translate into high local percentiles in low-background regions, and why common-region anomaly claims should not be substituted for local anomaly claims. The task appropriately preserved both absolute and normalized viewpoints through separate region-specific baselines.

## Limitations and Assumptions

The most important practical limitation is that the requested active-period file was not available; the analysis instead used a resolved relocated catalog path, documented in `<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/01_aomori_background_rate_analysis/diagnostics/context_paths_and_notes.csv`. Any downstream reporting should name the actual file used: `<CASE_ROOT>/data/catalog/Snet_catalog_relocate_250930_260501.csv`.

The handoff reports `outputs_truncated`, so not every internal output is indexed in the handoff JSON even though the main deliverables are present. No PDF outputs were listed among the task products, so there were no PDF documents to analyze.

Magnitude completeness differs between catalogs. `/tables/magnitude_completeness_summary.csv` shows Mc = 1.15 for the long-term common region and Mc = 1.45 for the active common region. Consequently, low-magnitude comparisons across catalogs are not equally robust. `/tables/threshold_reliability.csv` correctly warns that M≥1.2 should not be used as a primary long-term comparison threshold. Results involving M≥1.2 are useful for active-period structure but should not be over-interpreted as evidence of long-term exceptionality.

Depth coverage also differs. `/figures/02_magnitude_depth_comparison.png` shows that the relocated catalog is much more shallowly concentrated than the long-term raw catalog and underrepresents deeper seismicity. Therefore, depth-dependent anomaly interpretations, especially below 60 km, are more secure as negative or weak findings than as evidence of fine-scale deep structure.

Some very high observed/expected ratios arise from small expected counts, especially in sparse high-threshold or 30–60 km subcells. For example, `m1_m3_local_union | 30–60 km | M≥5` has obs/exp 10.96 but only one observed event against an expectation of 0.09 (`/tables/background_rate_evidence_matrix.csv`). Such cells are still informative but should be interpreted with caution because the ratio can be unstable when denominators are very small.

The analysis is explicitly statistical and catalog-based. It does not demonstrate triggering, fault interaction, fluid movement, slow slip, or any mechanism. `/summary_report.txt` states this clearly, and that caveat should be preserved in any integrated report.

## Report-Ready Summary

A statistically defensible background-rate model was built by filtering the 2020–2026 long-term raw catalog to the same common spatial domain defined from the active relocated catalog. The common region spans 38.353003–42.532633°N and 140.851921–144.64847°E (`/tables/region_definitions.csv`; `/figures/01_catalog_footprints_common_region.png`). This step is essential because the raw catalog has broader spatial coverage than the relocated active-period catalog.

Catalog audit results show that larger events are highly consistent between catalogs in the overlap period. In the common region, overlap counts are nearly matched at M≥4, M≥5, and M≥6, and matched-event differences are very small in time, location, and depth (`/tables/overlap_threshold_counts.csv`, `/tables/matched_large_events.csv`, `/figures/03_matched_event_differences.png`). Completeness estimates indicate Mc ≈ 1.15 for the long-term common-region catalog and Mc ≈ 1.45 for the active common-region catalog (`/tables/magnitude_completeness_summary.csv`), so M≥3, M≥4, and M≥5 are the preferred thresholds for long-term anomaly claims (`/tables/threshold_reliability.csv`).

Within the common region, the 2025-10 to 2026-05 active period is clearly exceptional relative to the 2020–2026 background. Observed versus expected counts are 1267 versus 348 for M≥3, 259 versus 62.6 for M≥4, 68 versus 12.0 for M≥5, and 13 versus 1.95 for M≥6, corresponding to percentile ranks of 98.5–99.6 (`/tables/active_period_percentile_vs_background.csv`; `/figures/09_active_period_percentiles.png`; `/summary_report.txt`). The monthly time series shows the active interval as the dominant peak in the entire 2020–2026 record for the common region (`/figures/04_long_term_monthly_rates.png`).

The anomalies are not uniform across the study area. They are localized and strongest in the `m1_m3_local_union`, `m2_near_field`, and `m2_outer_band`, while the `control_region` shows only weak-to-moderate elevation (`/tables/active_period_percentile_vs_background.csv`; `/figures/06_active_region_comparison.png`; `/figures/09_active_period_percentiles.png`). The M1–M3 local union remains strongly anomalous after background correction, with full-period obs/exp ratios of 10.5, 11.1, and 12.4 at M≥3, M≥4, and M≥5, and with the highest cells in the region-depth evidence matrix (`/tables/background_rate_evidence_matrix.csv`; `/figures/10_background_rate_evidence_matrix.png`). The M2 outer band also exceeds background strongly, especially in the shallow 0–30 km bin, and its December 2025 pulse is far larger than the control-region response, indicating that it cannot be explained solely as a general regional uplift (`/tables/active_period_percentile_vs_background.csv`; `/tables/background_rate_evidence_matrix.csv`; `/figures/06_active_region_comparison.png`).

Depth decomposition shows that the anomaly is dominated by 0–30 km seismicity, with secondary 30–60 km involvement and little evidence for a strong >60 km anomaly (`/figures/07_depth_stratified_rates.png`; `/tables/background_rate_evidence_matrix.csv`). The temporal evolution is burst-like rather than uniform, with strong pulses associated with M1 in November 2025, M2 in December 2025, and M3 in late April 2026 (`/figures/05_active_period_rates.png`; `/figures/06_active_region_comparison.png`).

For later physical follow-up, the most statistically interesting observations are: (1) the high common-region exceptionality across M≥3–M≥6, (2) the persistence of strong anomaly in the M1–M3 local union after regional correction, (3) the significant and shallow-dominated excess in the M2 outer band beyond control-region behavior, and (4) the spatially patchy anomaly map indicating localized hotspots rather than a smooth domain-wide increase (`/figures/08_spatial_anomaly_map_M3.png`; `/tables/spatial_anomaly_grid_M3.csv`). These findings provide robust catalog-level support for targeted physical interpretation later, but they do not themselves establish any triggering or mechanism.