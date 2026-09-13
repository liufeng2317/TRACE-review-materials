## Scientific Purpose

This task evaluates whether the event-centered seismic sequence patterns around the three matched major earthquakes in the Aomori regional catalog can be explained by simple background behavior or randomized time controls. The goal is to distinguish genuine post-mainshock clustering from rate changes that might arise from catalog background variability, temporal aggregation, or chance timing.

The control analysis is scientifically important because the preceding sequence analyses indicated burst-like seismicity and strong mainshock-centered enrichment for some events, but those patterns need to be tested against null expectations. Here, the focus is on the robustness of observed post/pre rate behavior under background and randomized controls, with attention to M1, M2, and M3 individually.

## Method and Implementation Evidence

The task was implemented as a control-comparison workflow using the relocated catalog and the three matched mainshocks. Evidence from the run inventory indicates that the control analysis consumed the full sequence-analysis context, including the catalog, matched mainshock set, station inventory, and focal-mechanism availability.

Key implementation evidence:
- `[<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/06_control_comparison/input_inventory.json]`
- `[<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/06_control_comparison/manifest.json]`

The inventory confirms the task operated on:
- 25,646 catalog rows
- 3 mainshock rows and 3 matched rows
- 1,606,311 sequence rows
- 354 mechanism rows
- 371 station rows

The control design is captured in the summary tables:
- observed baseline sequence windows centered on each mainshock
- shifted background controls
- randomized controls for post-event rate comparisons

Primary machine-readable outputs used for interpretation:
- `[<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/06_control_comparison/control_summary.csv]`
- `[<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/06_control_comparison/control_background_comparison.csv]`
- `[<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/06_control_comparison/control_observed_rates.csv]`
- `[<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/06_control_comparison/control_randomized_rates.csv]`
- `[<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/06_control_comparison/control_observed_vs_randomized_summary.csv]`
- `[<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/06_control_comparison/control_significance_summary.csv]`

Two publication-style figures summarize the control test:
- `[<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/06_control_comparison/figures/control_rate_ratio_comparison.png]`
- `[<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/06_control_comparison/figures/observed_vs_randomized_post_rates.png]`

## Key Results and Evidence Files

### 1) Observed post/pre rate ratios exceed background controls for all three mainshocks

The strongest overall result is that observed post-event rates are higher than the background/shifted-control rates across M1, M2, and M3. In the observed-vs-background table, observed sequences show systematic post/pre amplification, while shifted background windows show much smaller or even sub-unity ratios in many cases.

Evidence:
- `[<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/06_control_comparison/control_background_comparison.csv]`
- `[<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/06_control_comparison/control_summary.csv]`
- Figure: `[<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/06_control_comparison/figures/control_rate_ratio_comparison.png]`

Concrete values from `control_summary.csv` at the baseline setting (radius 50 km, time window 90 d, magnitude threshold 1.2):
- M1: baseline pre-rate 5.78, post-rate 35.30, rate ratio 6.11
- M2: baseline pre-rate 0.49, post-rate 17.12, rate ratio 35.02
- M3: baseline pre-rate 8.51, post-rate 27.67, rate ratio 3.25

This shows that:
- M2 has the strongest relative post-event enhancement.
- M1 is also elevated but less extreme than M2.
- M3 has a clear increase, though with a smaller ratio than M2.

### 2) Randomized controls are consistently lower than observed post-event rates

The observed-vs-randomized tables show that randomized controls do not reproduce the observed post-event rate enhancement. Observed post-event rates are substantially above randomized medians for all three mainshocks and across multiple time-window lengths.

Evidence:
- `[<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/06_control_comparison/control_observed_vs_randomized_summary.csv]`
- `[<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/06_control_comparison/control_randomized_rates.csv]`
- Figure: `[<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/06_control_comparison/figures/observed_vs_randomized_post_rates.png]`

From `control_observed_vs_randomized_summary.csv`:
- M1 at 90 d: observed ratio median 6.11 vs randomized ratio median 0.29; observed post-rate median 35.30 vs randomized post-rate median 11.44
- M2 at 90 d: observed ratio median 35.02 vs randomized ratio median 0.50; observed post-rate median 17.12 vs randomized post-rate median 5.04
- M3 at 90 d: observed ratio median 3.25 vs randomized ratio median 0.70; observed post-rate median 27.67 vs randomized post-rate median 5.34

The figure interpretation is consistent:
- Observed post-event rates stay above randomized rates in every panel.
- The separation is largest for M2 and M3 at short windows.
- M1 shows the weakest but still persistent observed-vs-randomized contrast.

### 3) Short-window post-event clustering is strongest, especially for M2 and M3

The figure `observed_vs_randomized_post_rates.png` shows that observed post-event rates are highest for the shortest windows and decrease as the window length increases. This is the expected signature of short-lived aftershock clustering, and it is not reproduced by randomized controls.

Evidence:
- `[<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/06_control_comparison/figures/observed_vs_randomized_post_rates.png]`
- `[<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/06_control_comparison/control_observed_rates.csv]`

Qualitative figure reading:
- M3 has the strongest observed short-window rates.
- M1 is also strongly elevated.
- M2 is lower in absolute post-event rate than M1/M3 in this figure, but its observed-vs-randomized contrast remains strong and its rate ratio is extreme in the summary tables because the pre-event background is very low.

### 4) Control behavior is comparatively stable, suggesting the observed signal is not a null-artifact

The control rates themselves are relatively low and do not mimic the observed post-event spikes. The randomized median rate and ratio summaries remain much closer to background levels, while observed rates retain strong amplification.

Evidence:
- `[<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/06_control_comparison/control_randomized_rates.csv]`
- `[<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/06_control_comparison/control_significance_summary.csv]`

From `control_significance_summary.csv` at the baseline setting:
- M1: baseline observed rate 35.30, randomized post-rate median 6.87, randomized ratio median 0.48, observed minus randomized rate 43.35
- M2: baseline observed rate 17.12, randomized post-rate median 5.04, randomized ratio median 0.50, observed minus randomized rate 19.27
- M3: baseline observed rate 27.67, randomized post-rate median 5.34, randomized ratio median 0.70, observed minus randomized rate 38.62

These values support the conclusion that the observed post-event enhancement is not reproduced by the randomization null.

## Limitations and Assumptions

- The task provides strong control-comparison evidence, but the available outputs are summary tables and diagnostic figures rather than raw per-event residuals for every control draw. This limits deeper inference about uncertainty structure beyond the reported medians and summary metrics.
- The CSV files were not directly analyzable with the PDF tool; they were inspected through structured table reading. The evidence is still valid, but the workflow note should acknowledge the format mismatch.
- The randomized controls are summarized through medians/means and not fully detailed here; the exact randomization algorithm, number of replicates, and any seed settings are not fully visible in the inspected outputs.
- Control significance is reported in summary form, but the specific statistical test used for significance thresholds is not explicit in the visible tables.
- The task confirms that observed post-event clustering exceeds simple randomized/background expectations, but it does not by itself prove a unique physical triggering mechanism.
- Station and focal-mechanism context exists in the inventory, but this control task does not appear to exploit those datasets analytically beyond documenting availability.

## Report-Ready Summary

The control-comparison analysis demonstrates that the post-mainshock seismicity increases seen around M1, M2, and M3 are not explained by simple background windows or randomized timing controls. Across the baseline 50 km / 90 d / M≥1.2 setting, all three mainshocks show elevated post/pre ratios, with M2 exhibiting the strongest relative amplification, followed by M1 and then M3.

The most reportable conclusion is that the observed post-event clustering is robust against null comparisons:
- observed post-event rates are systematically above background/shifted controls,
- observed post-event rates are substantially above randomized medians,
- short-window post-event concentration is strongest and consistent with aftershock-like decay behavior,
- and these patterns persist across the three matched mainshocks.

Best evidence files for the integrated report:
- `[<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/06_control_comparison/control_summary.csv]`
- `[<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/06_control_comparison/control_observed_vs_randomized_summary.csv]`
- `[<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/06_control_comparison/control_significance_summary.csv]`
- `[<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/06_control_comparison/figures/control_rate_ratio_comparison.png]`
- `[<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/06_control_comparison/figures/observed_vs_randomized_post_rates.png]`