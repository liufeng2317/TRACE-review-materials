# Plan

Audit the prepared metadata and waveform index, filter both event members to
the fixed window
`2025-11-01T00:00:00 <= origin_time < 2025-12-07T00:00:00`, and generate
reviewable event-pair and family results.

Use exact `station_component` matching, S-phase priority with P-phase fallback,
a `[-0.5, 5.5] s` phase window, `2-15 Hz` filtering, and a `+/-1.5 s` lag
search. Preserve the final manuscript-aligned tables and their summary.
