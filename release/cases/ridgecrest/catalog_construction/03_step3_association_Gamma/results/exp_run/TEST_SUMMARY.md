# Ridgecrest Step3 Gamma Test Summary

Updated: 2026-06-28

This note records the current Ridgecrest Gamma association and PhaseNet-pick input tests under `01_step3_association_Gamma/exp_run`. Metrics against the reference use the existing comparison outputs in `run/compare`, with matching tolerance `time <= 5 s` and `horizontal distance <= 10 km` unless noted otherwise.

## Current Recommendation

**Best current production/default setting:**

- PhaseNet picks: default overlap `1500`, thresholds `P=0.3`, `S=0.3`.
- Gamma association: `gamma_p03s03_noamp_eps5_os10`, `use_amplitude=False`, `dbscan_eps=5`, `oversample_factor=10`.
- Output baseline: `outputs-gamma_p03s03_noamp_eps5_os10/01_gamma_association_location_magnitude` or equivalent `outputs-picktest-threshold/gamma_p03s03_noamp_eps5_os10`.

Reason: this setting gives the highest reference recall among the full-window Gamma runs and preserves the most matched events. It is also the baseline used by the current downstream relocation tests.

**Balanced cleaner alternative:**

- PhaseNet thresholds `P=0.4`, `S=0.4`, Gamma `gamma_p03s03_noamp_eps5_os10`.
- Output: `outputs-picktest-threshold/gamma_p04s04_noamp_eps5_os10`.
- Reason: fewer candidate events and higher agent matched fraction, but lower reference recall. Use this if false positives or downstream runtime become the dominant issue.

**Do not use full-window `overlap=3000`:** PhaseNet has `in_samples=3001`; `overlap=3000` gives step `1` sample and pathological memory use. It hit about 500 GB RSS on the first station-day. Keep it disabled except for tiny debug windows.

## Full Gamma Version Comparison

| Run | Events | Matched | Recall | Agent matched | Median H km | P90 H km | Notes |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `gamma_p03s03_amp_eps15_os5` | 105,955 | 38,924 | 34.8% | 36.7% | 1.231 | 6.364 | Amplitude-enabled baseline, eps=15; fewer detections. |
| `gamma_p03s03_noamp_eps15_os5` | 167,414 | 48,234 | 43.1% | 28.8% | 1.253 | 6.289 | No amplitude, eps=15; many events but lower precision. |
| `gamma_p03s03_noamp_eps5_os10` | 156,879 | 49,527 | 44.3% | 31.6% | 1.554 | 6.328 | No amplitude, eps=5/os=10; current best full-window Gamma baseline. |

Interpretation: `gamma_p03s03_noamp_eps5_os10` is the strongest full-window Gamma result by reference recall (`44.3%`) and matched count, even though `gamma_p03s03_amp_eps15_os5` and `gamma_p03s03_noamp_eps15_os5` have slightly smaller median horizontal residuals. The goal here is not simply reducing count; `gamma_p03s03_noamp_eps5_os10` keeps substantially more valid events.

## Gamma Parameter Short-Window Test

Window: `2019-07-26` to `2019-07-10`; reference subset: SCEDC QTM all detections.

| Param set | Events | Matched | Recall | Agent matched | Median H km | P90 H km | Comment |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `eps5_os5` | 26,912 | 9,904 | 44.9% | 36.8% | 2.094 | 6.593 | Similar recall to eps5_os10; no clear gain from lower oversampling. |
| `eps5_os10` | 26,957 | 9,875 | 44.7% | 36.6% | 2.095 | 6.561 | Current full-run baseline parameter family. |
| `eps8_os10` | 29,863 | 9,647 | 43.7% | 32.3% | 1.451 | 6.319 | Best median horizontal residual, but lower recall and more fragmented candidates. |
| `eps10_os10` | 27,212 | 9,752 | 44.2% | 35.8% | 1.851 | 6.135 |  |
| `eps15_os10` | 25,919 | 9,275 | 42.0% | 35.8% | 1.649 | 6.283 |  |

Short-window result: `eps8_os10` improves median horizontal residual, but `eps5_os10` remains a safer global baseline because it has slightly higher recall and was validated in the full-window `gamma_p03s03_noamp_eps5_os10` run. A targeted follow-up could test `eps8_os10` on the full window only if location compactness becomes more important than recall.

## PhaseNet Threshold Tests with Gamma gamma_p03s03_noamp_eps5_os10

| Pick label | P thr | S thr | Events | Matched | Recall | Agent matched | Median H km | P90 H km | Recommendation |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `p03_s03` | 0.3 | 0.3 | 156,950 | 49,619 | 44.3% | 31.6% | 1.556 | 6.389 | Best recall / current default. |
| `p03_s04` | 0.3 | 0.4 | 145,783 | 48,694 | 43.5% | 33.4% | 1.568 | 6.363 |  |
| `p04_s04` | 0.4 | 0.4 | 131,520 | 47,710 | 42.6% | 36.3% | 1.554 | 6.238 | Best balanced cleaner option. |
| `p04_s05` | 0.4 | 0.5 | 119,124 | 45,616 | 40.8% | 38.3% | 1.559 | 6.218 |  |
| `p05_s05` | 0.5 | 0.5 | 107,010 | 43,250 | 38.6% | 40.4% | 1.569 | 6.048 | Too strict for recall. |

Threshold interpretation: lowering thresholds increases recall but also increases unmatched candidates. `p03_s03` is best for catalog completeness; `p04_s04` is useful when downstream association/relocation cost or spurious detections are limiting.

## NMS Pick Tests

NMS is same-day, same-station, same-phase, 1 s neighbor clustering, keeping the highest-score pick. P and S are handled separately.

| NMS input | Rows written | Threshold removed | NMS removed | File success/fail | Gamma status |
| --- | ---: | ---: | ---: | --- | --- |
| `p0p3_s0p4_nms1s` | 3,466,783 | 331,114 | 37,716 | 841/12 | Completed as `outputs-picktest-nms/gamma_nms1_p03s04_noamp_eps5_os10`; events=145,460, phase_rows=1,284,297. Compared with non-NMS `p03_s04`: events -323, matched -105, recall -0.094 percentage points, median H -0.006 km. |
| `p0p4_s0p4_nms1s` | 3,086,697 | 740,092 | 8,824 | 841/12 | Completed as `outputs-picktest-nms/gamma_nms1_p04s04_noamp_eps5_os10`; events=131,494, phase_rows=1,151,661. Compared with non-NMS `p04_s04`: events -26, matched +8, recall +0.007 percentage points, median H +0.003 km. |

NMS interpretation: NMS removes relatively few picks after thresholding and produces nearly identical association/reference metrics. It is useful as a harmless cleanup option, but it is not a meaningful lever for improving location quality. The main pick-threshold conclusion remains unchanged: use `p03_s03` for completeness and `p04_s04` when a cleaner candidate set is preferred.

## Overlap Pick Tests

| Overlap input | Pick rows | P picks | S picks | File success/fail | Gamma status |
| --- | ---: | ---: | ---: | --- | --- |
| `gamma_ov1000_p03s03_noamp_eps5_os10` | 3,745,317 | 1,809,505 | 1,935,812 | 841/12 | Gamma completed: events=154,259, phase_rows=1,373,174, matched=49,672, recall=44.38%, median H=1.566 km. Compared with overlap1500: events -2,691, matched +53, agent matched fraction +0.59 percentage points. |
| `gamma_ov1500_p03s03_noamp_eps5_os10` | 3,835,613 | 1,863,289 | 1,972,324 | 841/12 | Gamma completed: events=156,950, phase_rows=1,400,697, matched=49,619, recall=44.34%, median H=1.556 km. This remains the default/baseline-equivalent setting. |
| `gamma_ov2500_p03s03_noamp_eps5_os10` | 3,412,723 | 1,582,510 | 1,830,213 | 841/12 | PhaseNet picks complete; Gamma association not yet evaluated. |
| `overlap3000_p03_s03` | invalid | invalid | invalid | stopped | Disabled: `in_samples=3001`, overlap=3000 gives 1-sample stride and runaway memory. |

Overlap interpretation: `overlap1000` and `overlap1500` are effectively tied under the SCEDC space10 protocol. `overlap1000` is slightly cleaner by count and agent matched fraction, while `overlap1500` has a marginally smaller median horizontal residual and is the established baseline. The difference is too small to justify changing the production default before downstream HypoDD comparison. `overlap2500` still needs Gamma association if we want to complete the overlap sweep; `overlap3000` is invalid for full-day processing.

## Current Output Inventory

| Family | Completed runs | Notes |
| --- | --- | --- |
| threshold | `p03_s03`, `p03_s04`, `p04_s04`, `p04_s05`, `p05_s05` | Main completed pick-threshold grid. |
| nms | `gamma_nms1_p03s04_noamp_eps5_os10` | `gamma_nms1_p04s04_noamp_eps5_os10` still needs clean rerun. |
| overlap | `gamma_ov1500_p03s03_noamp_eps5_os10` | Only baseline/copy completed; run Gamma for overlap1000/2500 next. |

## Re-run Commands

Run from `examples/ridgecrest/catalog_construction/run/01_step3_association_Gamma/exp_run/scripts`:

```bash
./run_03_01_picks_threshold_gamma_p03s03_noamp_eps5_os10_assoc_test.sh
./run_03_01_picks_nms_gamma_p03s03_noamp_eps5_os10_assoc_test.sh
./run_03_01_picks_overlap_gamma_p03s03_noamp_eps5_os10_assoc_test.sh
```

PhaseNet overlap tests are generated from step2, not step3. `overlap3000` is intentionally disabled in the full-window script.

## Next Best Tests

1. Finish `gamma_nms1_p04s04_noamp_eps5_os10` Gamma association after the partial-output archival fix.
2. Run Gamma association for `gamma_ov1000_p03s03_noamp_eps5_os10` and `gamma_ov2500_p03s03_noamp_eps5_os10`, then compare against SCEDC using the same `time<=5s, space<=10km` protocol.
3. If location compactness is prioritized after overlap/NMS tests, consider a full-window `eps8_os10` Gamma run, but keep `eps5_os10` as the current production baseline until full-window evidence says otherwise.

## Magnitude Formula Correction

The `gamma_p03s03_*` waveform-derived local magnitudes were corrected on 2026-06-28. The previous implementation used:

```text
ML = log10(A_mm) + 1.11*log10(R_km) + 0.00189*R_km + 3.0
```

The corrected Hutton-Boore-style form is:

```text
ML = log10(A_mm) + 1.11*log10(R_km/100) + 0.00189*(R_km-100) + 3.0
```

This subtracts a constant offset of `2.409` from previously computed waveform ML values. Existing `outputs-gamma_p03s03_amp_eps15_os5`, `outputs-gamma_p03s03_noamp_eps15_os5`, and `outputs-gamma_p03s03_noamp_eps5_os10` event tables, station magnitude tables, `catalog_*.dat`, and `phase_*.dat` files were updated in place. Each output directory now has `magnitude_formula_correction_summary.json` as an idempotence marker.

Corrected Gamma-vs-SCEDC magnitude residuals are stored in `run/compare/reference_eval_space10_gamma_mag_corrected`:

| Run | Matched | Median mag diff | Mean mag diff | P90 mag diff |
| --- | ---: | ---: | ---: | ---: |
| `gamma_p03s03_amp_eps15_os5` | 38,924 | -0.08 | -0.136 | 0.38 |
| `gamma_p03s03_noamp_eps15_os5` | 48,234 | 0.16 | 0.126 | 0.47 |
| `gamma_p03s03_noamp_eps5_os10` | 49,527 | 0.17 | 0.120 | 0.45 |

## Reproducibility Notes

- Reference catalog: `examples/ridgecrest/data/SCEDC_ridgecrest_qtm.csv`.
- Pick source root: `examples/ridgecrest/catalog_construction/run/01_step2_phase_picking_PhaseNet/exp_run`.
- Gamma script root: `examples/ridgecrest/catalog_construction/run/01_step3_association_Gamma/exp_run/scripts`.
- Gamma comparison outputs: `examples/ridgecrest/catalog_construction/run/compare`.
- Some comparison CSVs still contain historical output path names from before directory renaming; the numerical metrics are still from the corresponding run labels.
