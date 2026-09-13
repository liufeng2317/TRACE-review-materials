# Repeating-Earthquake Analysis Plan

The analysis uses the fixed window
`2025-11-01T00:00:00 <= origin_time < 2025-12-07T00:00:00`.
Prepared metadata and SAC waveforms are screened and compared using exact
`station_component` matching, S-phase priority with P-phase fallback, a
`[-0.5, 5.5] s` phase window, `2-15 Hz` filtering, and a `+/-1.5 s` lag search.

The final public numerical outputs are the files in
`results/exp_run/outputs/manuscript_aligned/`, controlled by
`manuscript_alignment_summary.json`.
