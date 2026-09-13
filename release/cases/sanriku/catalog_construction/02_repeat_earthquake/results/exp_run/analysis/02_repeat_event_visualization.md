## Scope

This task generates reviewable summaries from the manuscript-aligned
repeating-earthquake result set for
`2025-11-01T00:00:00 <= origin_time < 2025-12-07T00:00:00`.

## Method

The visualization script consumes the standardized event-pair,
station-component, and family tables. It uses the same baseline settings as
the analysis script: exact `station_component` matching, S-phase priority with
P-phase fallback, `[-0.5, 5.5] s` phase windows, `2-15 Hz` filtering, and a
`+/-1.5 s` lag search.

## Final Public Result

The controlling metadata file is:

`results/exp_run/outputs/manuscript_aligned/manuscript_alignment_summary.json`

The final result set contains `19,726` event pairs, `783` high-confidence pairs
with `median_cc >= 0.70`, `147` families, and `477` family members. The
corresponding CSV files in the same directory are the authoritative numerical
results. The visualization script is retained for reproducing review figures
from these standardized tables.
