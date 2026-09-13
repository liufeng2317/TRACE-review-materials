# Plan

Perform a reviewable repeating-earthquake analysis in the fixed window
`2025-11-01T00:00:00 <= origin_time < 2025-12-07T00:00:00`.

Use prepared metadata and SAC waveforms. Screen event pairs by shared
station-component coverage, epicentral distance, and magnitude difference.
Apply exact station-component matching and phase-aligned cross-correlation
with S-phase priority, P-phase fallback, a `[-0.5, 5.5] s` window,
`2-15 Hz` filtering, and a `+/-1.5 s` lag search.

Produce standardized event-pair, station-component, family, and summary
outputs. The final public result is the manuscript-aligned result set.
