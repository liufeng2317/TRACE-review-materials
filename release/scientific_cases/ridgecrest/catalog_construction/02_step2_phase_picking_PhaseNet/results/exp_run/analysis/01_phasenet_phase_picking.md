## Scientific Purpose

This task applied the pretrained PhaseNet model to the full Ridgecrest station-day interval from 2019-07-04T00:00:00Z through 2019-07-26T00:00:00Z. The objective was to generate machine-readable P- and S-phase picks for downstream association and relocation.

## Method and Implementation Evidence

The public configuration, generated script, experiment plan, run summary, and manifest define the full 22 daily-window interval and the configured PhaseNet thresholds. The workflow records station-level discovery, file-level success or failure, pick counts, and output metadata. Large daily pick tables are excluded from the release; the full manifest, run summary, failure records, and trajectory record remain available for audit.

## Key Results

The authoritative full-run summary reports:

- interval: 2019-07-04T00:00:00Z to 2019-07-26T00:00:00Z;
- station metadata entries: 47;
- discovered station-day waveform products: 853;
- successful file-level inferences: 841;
- failed file-level inferences: 12;
- P picks: 1,454,311;
- S picks: 1,641,210;
- total picks: 3,095,521.

These totals are the full-window results used by the downstream catalog construction. A diagnostic example is retained as supporting evidence, while the daily pick CSV files themselves are omitted because of their size.

## Evidence Files

- `results/config.yaml`
- `results/exp_plans/`
- `results/exp_run/scripts/`
- `results/exp_run/outputs/`
- `results/exp_run/research_report/`
- `results/exp_run/analysis/`
- `results/exp_run/report/`
- `results/state/`
- `results/log/trajectory/public_run_record.jsonl`
