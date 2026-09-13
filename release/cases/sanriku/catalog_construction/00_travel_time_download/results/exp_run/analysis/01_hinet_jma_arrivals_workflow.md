# JMA/Hi-net Arrival-Time Workflow

## Delivery status

The arrival-time download and parsing workflow completed using the previously
downloaded non-empty raw measure files. The workflow did not make new network
requests during this completed run.

## Input and scope

- Requested interval: 2025-06-01 through 2026-05-01, with 2026-05-02 as the
  exclusive upper bound.
- Sanriku filter: latitude 38.50-42.50 N and longitude 141.00-144.50 E.
- Existing raw input: 73 non-empty JMA measure files, including the calendar
  month-boundary files needed to cover the complete interval without overlap.

## Processing and outputs

The workflow first passed a smoke test on the first five-day file, then parsed
the complete input collection using the fixed-width 96-byte JMA record
layout. It produced full and regional event/pick tables, `phase.dat`,
`station.sta`, parser QC tables, traceability information, and validation
summaries.

## Validation

- Final validation: passed.
- Validation errors: 0.
- Invalid-length records: 0.
- Parser errors: 0.
- Orphan pick records: 0.
- Unterminated event blocks: 0.
- Regional parser-stage events: 36,838.
- Canonical expert-processed relocation input: 33,702 events and 637,812 picks.
- Regional event coordinates remain within the requested bounds.

The regional event count is the count from the travel-time parsing stage. It is
not the later arrival-matched or relocation-input count reported in the
manuscript, which is produced by downstream catalog matching and filtering.

## Evidence

The authoritative machine-readable evidence is in the task output directory,
especially `final_validation_summary.json`, `catalog_qc_summary.json`,
`events_regional.csv`, `picks_regional.csv`, `phase.dat`, and
`phase_dat_traceability.csv`.
The canonical catalog handoff is the expert-processed product under
`results/exp_run/expert/outputs/`. It contains the validated `events.csv`,
`picks.csv`, `phase.dat`, and `station.sta` files used by the subsequent
relocation step.
