---
author:
- TRACE
date: 2026-06-01
title: Repeating-earthquake analysis for the Sanriku case
---

# Scope

This report documents the repeating-earthquake workflow for the Sanriku case.
The analysis uses the fixed half-open time window
`2025-11-01T00:00:00 <= origin_time < 2025-12-07T00:00:00`,
covering 2025-11-01 through 2025-12-06.

The final public result is the `manuscript_aligned` result set. Its controlling
metadata file is:

`results/exp_run/outputs/manuscript_aligned/manuscript_alignment_summary.json`

The corresponding CSV files in the same directory are the authoritative
event-pair and family outputs.

# Method

The workflow reads the prepared metadata and SAC waveform index, applies the
documented event-pair screening criteria, and performs phase-aligned waveform
cross-correlation. The baseline processing uses exact `station_component`
matching, S-phase alignment with P-phase fallback, a `[-0.5, 5.5] s` phase
window, a `2-15 Hz` bandpass, and a maximum lag search of `+/-1.5 s`.

The final public results are derived from the complete result set within the
manuscript time window. The result tables preserve event-pair similarity
metrics, station-component diagnostics, and family membership for independent
review.

# Final Results

The final summary reports:

- candidate event pairs: `19,726`
- pairs with `median_cc >= 0.55`: `1,882`
- high-confidence pairs with `median_cc >= 0.70`: `783`
- high-confidence families: `147`
- family members: `477`
- largest family: `89` events

The corresponding files are:

- `candidate_event_pairs.csv`
- `repeat_event_pairs.csv`
- `repeat_event_families.csv`
- `repeat_family_members.csv`
- `manuscript_alignment_summary.json`

All files are under:

`results/exp_run/outputs/manuscript_aligned/`

# Reproduction

The public analysis scripts are:

- `results/exp_run/scripts/01_repeat_event_analysis.py`
- `results/exp_run/scripts/02_repeat_event_visualization.py`

Both scripts use the same default time window stated above. Local data and
waveform locations are represented by placeholders such as
`<WAVEFORM_DATA_ROOT>` and are supplied by the user environment at runtime.
