## Scientific Purpose

This task prepared the full Ridgecrest station-day waveform interval from 2019-07-04T00:00:00Z through 2019-07-26T00:00:00Z. The workflow created phase-picking waveforms, Wood-Anderson magnitude waveforms, station metadata, and quality-control summaries for downstream catalog construction.

## Method and Implementation Evidence

The public run configuration and generated code define the half-open UTC interval with `obspy.UTCDateTime` and use process-based parallel execution. The preprocessing workflow selects usable three-component station channels, merges and trims daily waveform records, and creates phase-picking products, magnitude products with response removal and Wood-Anderson simulation, station metadata, and per-station-day QC records.

The release does not include the large raw waveform archive. The metadata, QC tables, representative products, scripts, run plans, report, and trajectory record document how the full interval was processed.

## Key Results

The authoritative processing summary reports:

- interval: 2019-07-04T00:00:00Z to 2019-07-26T00:00:00Z;
- selected stations: 47;
- station-day jobs: 1,034;
- successful jobs: 853;
- skipped jobs: 173;
- failed jobs: 8;
- phase products: 853;
- magnitude products: 853.

The QC table contains the full station-day processing inventory. The release retains summary and representative output files while excluding the large waveform archive.

## Evidence Files

- `results/config.yaml`
- `results/exp_plans/`
- `results/exp_run/scripts/`
- `results/exp_run/output/`
- `results/exp_run/research_report/`
- `results/exp_run/analysis/`
- `results/exp_run/report/`
- `results/state/`
- `results/log/trajectory/public_run_record.jsonl`
