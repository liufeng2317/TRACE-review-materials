## Scope

This task performs the repeating-earthquake analysis for the fixed window
`2025-11-01T00:00:00 <= origin_time < 2025-12-07T00:00:00`,
covering 2025-11-01 through 2025-12-06.

## Method

The analysis uses the prepared event metadata and SAC waveform index. Event
pairs are screened using shared station-component coverage, epicentral distance,
and magnitude difference. Waveforms are matched by exact `station_component`,
aligned to S arrivals when available and to P arrivals otherwise, then
processed with a `[-0.5, 5.5] s` window, a `2-15 Hz` bandpass, and a `+/-1.5 s`
lag search.

## Final Public Result

The final public result is the manuscript-aligned result set:

`results/exp_run/outputs/manuscript_aligned/`

Its controlling file is `manuscript_alignment_summary.json`. The corresponding
CSV files contain:

- `19,726` candidate event pairs;
- `1,882` pairs with `median_cc >= 0.55`;
- `783` high-confidence pairs with `median_cc >= 0.70`;
- `147` families;
- `477` family members;
- maximum family size `89`.

The result tables are accompanied by the analysis and visualization scripts in
`results/exp_run/scripts/`. Local data paths are represented by public
placeholders and are supplied at runtime.
