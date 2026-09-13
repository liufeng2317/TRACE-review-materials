# Repeating-Earthquake Analysis Plan

Use the prepared metadata and SAC waveforms within
`2025-11-01T00:00:00 <= origin_time < 2025-12-07T00:00:00`.

The workflow audits the metadata, screens event pairs using shared
station-component coverage, epicentral distance, and magnitude difference,
then performs phase-aligned cross-correlation. The baseline uses exact
`station_component` matching, S-phase priority with P-phase fallback, a
`[-0.5, 5.5] s` window, `2-15 Hz` filtering, and a `+/-1.5 s` lag search.

The final public result is the manuscript-aligned result set under
`results/exp_run/outputs/manuscript_aligned/`. Its authoritative metadata file
is `manuscript_alignment_summary.json`; the accompanying CSV files provide the
event-pair and family results.
