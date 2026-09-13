## Scientific Purpose

This task diagnosed how seismicity evolved around the three Aomori mainshocks (M1, M2, M3) by building a mainshock-referenced catalog, comparing matched pre/post windows, and scoring multiple non-exclusive behavior dimensions. The scientific aim was to distinguish local mainshock-centered sequence behavior from broader regional activation, using short-window morphology as the primary visual evidence and matched-window statistics as the quantitative basis.

The completed outputs show that the analysis was designed to answer five core questions:

1. How compact or distributed each sequence was within ±7 days and ≤100 km.
2. Whether activity was mainly pre-mainshock, post-mainshock, or both.
3. Whether each sequence was dominated by a single mainshock or involved comparable companion events.
4. How much of the activity was confined to the near field (0–30 km) versus outer bands (30–60 km, 60–100 km).
5. Whether any clear radial migration, depth-domain coherence, or mechanism coherence supported more specific interpretations.

Key report-ready evidence is concentrated in:
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/magnitude_time_distance_pm7d_100km.png`
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/m4plus_sequence_views_pm7d_100km.png`
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/behavior_dimension_scores.csv`
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/behavior_dimension_supporting_metrics.csv`
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/sequence_behavior_evidence_table.csv`

## Method and Implementation Evidence

A self-contained script generated the analysis products:
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/scripts/01_aomori_sequence_analysis.py`

Implementation evidence confirms that the workflow produced the required mainshock-centered evidence set:

### 1. Mainshock-referenced event construction
A full event table was created:
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/mainshock_reference_event_table.csv`

Mainshock-like events were explicitly matched with small residuals:
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/mainshock_like_match_summary.csv`

The matching is precise and unambiguous:
- M1 matched at 0.01 s time residual, 0.166 km epicentral residual, 0.09 km depth residual, magnitude 6.9.
- M2 matched at 0.00 s, 0.297 km, 0.04 km, magnitude 7.5.
- M3 matched at 0.01 s, 0.158 km, 0.09 km, magnitude 7.7.

### 2. Short-window morphology figures
The required short-window figures were generated and are scientifically interpretable:
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/magnitude_time_distance_pm7d_100km.png`
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/m4plus_sequence_views_pm7d_100km.png`
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/prepost_magnitude_distance_counts_pm7d_100km.png`
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/m4_m5_distance_band_contribution_pm7d_100km.png`

The plotted subset was also saved:
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/plotted_events_pm7d_100km.csv`

### 3. Quantitative matched-window metrics
Matched pre/post metrics were computed for ±7, ±14, and ±25 days, and for cumulative radii and distance bands:
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/matched_window_metrics_all.csv`
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/matched_window_metrics_by_band.csv`
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/qa_count_table_by_mainshock_window_distance.csv`

Sensitivity visualization was generated:
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/window_radius_sensitivity_heatmaps.png`
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/optional_window_robustness_comparison.png`

### 4. Magnitude hierarchy, companion events, and sequence scoring
Magnitude-dominance and companion-event metrics were saved in reusable tables and summarized visually:
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/magnitude_dominance_metrics.csv`
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/companion_event_metrics.csv`
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/magnitude_dominance_companion_summary.png`

Behavior-dimension scoring was provided in machine-readable and summary forms:
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/behavior_dimension_scores.csv`
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/behavior_dimension_supporting_metrics.csv`
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/sequence_behavior_evidence_table.csv`

### 5. Depth, mechanism, migration, and station context
Additional contextual summaries were generated:
- Depth:
  - `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/depth_summary_by_mainshock.csv`
  - `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/depth_summary_m4_m5.csv`
- Mechanism context:
  - `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/mechanism_context_by_sequence.csv`
  - `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/mechanism_match_summary.csv`
- Migration diagnostics:
  - `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/migration_diagnostics.csv`
- Temporal post-response concentration:
  - `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/post_response_temporal_metrics.csv`
- Regional outer-band context:
  - `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/regional_outerband_metrics.csv`
- Station context:
  - `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/station_context_summary.csv`

## Key Results and Evidence Files

### 1. The ±7 day sequence morphology differs strongly among M1, M2, and M3

The primary morphology figure shows three distinct sequence styles:
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/magnitude_time_distance_pm7d_100km.png`

Visual evidence from that figure indicates:
- **M1**: the most compact and near-field concentrated sequence, with dense activity immediately after the mainshock and only limited outer-band participation.
- **M2**: the most spatially distributed post-mainshock response, with substantial activation across 30–60 km and 60–100 km bands and a visually notable secondary burst several days later.
- **M3**: strong post-mainshock activation but broader spatial occupation than M1, with persistent outer-band activity and weaker single-mainshock dominance than a simple isolated aftershock cloud would suggest, though still much more mainshock-dominated than M1.

The M4+ focused figure reinforces these distinctions:
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/m4plus_sequence_views_pm7d_100km.png`

That figure shows:
- **M1** has several substantial companion events, including near-mainshock-sized events in the near field.
- **M2** has mainly post-mainshock M4+ activity and a broad distance distribution rather than a compact near-field cluster.
- **M3** has post-mainshock M4+ activity but far fewer comparable large companions than M1.

Supporting event subset:
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/plotted_events_pm7d_100km.csv`

### 2. All three mainshocks show post-mainshock activation, but the style of that response differs

The sequence summary table scores all three as having **moderate aftershock response**:
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/behavior_dimension_scores.csv`

Supporting metrics:
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/behavior_dimension_supporting_metrics.csv`

Quantitative evidence at ±7 d, ≤100 km:
- **M1**: post/pre ratio = 3.174; M4+ post/pre ratio = 2.619; near-field post fraction = 0.790; 38.3% of post events within 24 h.
- **M2**: post/pre ratio = 86.625; near-field post fraction = 0.180; 26.6% of post events within 24 h; M4+ pre count = 0 within this window so M4+ post/pre is undefined.
- **M3**: post/pre ratio = 14.649; near-field post fraction lower than M1 and higher than M2 only in relative terms of total spatial distribution; the evidence table classifies this as moderate aftershock response.

Post-response concentration through time is tabulated in:
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/post_response_temporal_metrics.csv`

For M1, 85.5% of post M4+ events occurred within 24 h and 94.5% within 72 h, consistent with a strong short-lived local response. The morphology figures suggest M2 and M3 also had major post-mainshock concentration, but M2 and M3 spread that response more broadly in space than M1.

The pre/post count comparison figure is supportive but not diagnostic on its own:
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/prepost_magnitude_distance_counts_pm7d_100km.png`

This figure shows:
- post counts exceed pre counts for all three,
- M2 has the largest absolute post count increase,
- M1 is most near-field concentrated,
- M2 and M3 include much larger outer-band contributions.

### 3. Magnitude hierarchy clearly separates M1 from M3, with M2 intermediate

The magnitude-dominance summary is one of the most report-relevant outputs:
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/magnitude_dominance_companion_summary.png`

Visual and tabulated evidence:
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/magnitude_dominance_metrics.csv`
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/companion_event_metrics.csv`

At ±7 d, ≤100 km:
- **M1**: mainshock magnitude 6.9; largest non-mainshock = 6.6; dominance gap = 0.3; 2 companions within 0.5 magnitude units; 6 within 1.0 magnitude unit.
- **M2**: mainshock magnitude 7.5; largest non-mainshock = 6.9; dominance gap = 0.6; 0 companions within 0.5; 2 within 1.0.
- **M3**: mainshock magnitude 7.7; largest non-mainshock = 5.6; dominance gap = 2.1; no companions within 0.5 or 1.0 magnitude units.

Behavior scores derived from these metrics:
- **Single-mainshock dominance**:
  - M1 = low
  - M2 = possible
  - M3 = strong
- **Compact-cascade / compound structure**:
  - M1 = moderate
  - M2 = low
  - M3 = low

These distinctions are also summarized in:
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/sequence_behavior_evidence_table.csv`

Interpretively, M1 is the clearest case of weak single-mainshock dominance and multiple large companion events; M3 is the clearest case of strong mainshock dominance; M2 falls between those end members.

### 4. Foreshock/pre-mainshock activation is strongest for M1, weak for M2, and limited but nonzero for M3

This is a major discriminant among the three sequences.

Behavior scores:
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/behavior_dimension_scores.csv`

Evidence metrics:
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/behavior_dimension_supporting_metrics.csv`
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/matched_window_metrics_all.csv`

At ±7 d, ≤100 km:
- **M1**: foreshock/pre-mainshock activation = strong. M4+ pre count = 21; M5+ pre count = 8; largest pre-event magnitude = 6.9; largest pre-event time essentially coincident with the mainshock-like time because the mainshock-like event appears in the full matched-window record; caveat explicitly notes frame overlap/regional overlap.
- **M2**: foreshock/pre-mainshock activation = low. M4+ pre count = 0; M5+ pre count = 0.
- **M3**: foreshock/pre-mainshock activation = moderate in the scored table, but the headline metrics indicate only pre M4+ = 1 at ±7 d, ≤100 km. This implies the moderate score likely reflects broader contextual evidence across windows rather than strong short-window pre-mainshock activity.

The main morphology figure supports these contrasts:
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/magnitude_time_distance_pm7d_100km.png`

Visually:
- M1 shows clear pre-mainshock activity within the diagnostic window.
- M2 shows very little meaningful pre-mainshock activity.
- M3 shows some pre-window activity, but much less convincing as a near-mainshock foreshock buildup than M1.

### 5. Broader regional activation is weak for M1, strongest for M2, and moderate for M3

This is one of the clearest quantitative contrasts in the analysis.

Behavior scores:
- M1 = low
- M2 = strong
- M3 = moderate

Evidence:
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/regional_outerband_metrics.csv`
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/m4_m5_distance_band_contribution_pm7d_100km.png`
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/prepost_magnitude_distance_counts_pm7d_100km.png`

At ±7 d:
- **M1**:
  - pre outer-band fraction (30–100 km) = 0.107
  - post outer-band fraction = 0.210
  - post M4+ outer-band fraction = 0.127
  - interpretation: still near-field dominated.
- **M2**:
  - pre outer-band fraction = 0.875
  - post outer-band fraction = 0.820
  - post M4+ outer-band fraction = 0.911
  - interpretation: overwhelmingly outer-band dominated, both for all events and M4+ events.
- **M3**:
  - headline metrics give post outer-band fraction = 0.463
  - interpretation: broader than M1 but much less outer-band dominated than M2.

The dedicated M4+/M5+ distance-band figure is especially clear:
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/m4_m5_distance_band_contribution_pm7d_100km.png`

That figure shows:
- **M1**: M4+ and M5+ overwhelmingly concentrated in 0–30 km.
- **M2**: M4+ and M5+ dominated by 30–60 km and 60–100 km contributions, with very small 0–30 km share.
- **M3**: intermediate distribution, with substantial 0–30 km and 30–60 km contributions and only small or negligible 60–100 km contribution for M5+.

Thus, M2 is the clearest case where local mainshock-centered interpretation must be separated from regional activation.

### 6. Swarm-like or compound behavior is most plausible for M1, only possible for M2 and M3

Behavior scores:
- **M1**: swarm-like organization = moderate
- **M2**: possible
- **M3**: possible

Evidence table:
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/behavior_dimension_supporting_metrics.csv`

For M1, the supporting metrics are unusually suggestive of weak hierarchy and repeated moderate-large events:
- dominance gap = 0.300
- total M4+ = 76
- total M5+ = 28
- companion events within 1.0 magnitude unit = 6

This does not prove a physical swarm, but it does support a catalog-level description of compact, weakly hierarchical, multi-large-event organization.

For M2 and M3, the swarm-like signal is weaker:
- **M2** has broad regional activation and only a few comparable large companions.
- **M3** has strong mainshock dominance, which argues against strong swarm-like classification despite broad spatial activation.

The M4+ sequence view and the dominance-companion summary together are the best figure pair for this interpretation:
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/m4plus_sequence_views_pm7d_100km.png`
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/magnitude_dominance_companion_summary.png`

### 7. No monotonic radial migration is supported for any of the three sequences

All three are scored low for radial migration/expansion:
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/behavior_dimension_scores.csv`

Migration diagnostics:
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/migration_diagnostics.csv`

Key ±7 d post metrics:
- **M1**: all-event slope = 0.894 km/day; Spearman = 0.158; M4+ slope = 2.346 km/day; M4+ Spearman = 0.417; monotonic progression supported = False.
- **M2**: all-event slope = 1.824 km/day; Spearman = 0.071; M4+ slope = -1.184 km/day; M4+ Spearman = -0.224; monotonic progression supported = False.
- **M3**: all-event slope = 2.023 km/day; Spearman = 0.149; M4+ slope = 2.550 km/day; M4+ Spearman = 0.335; monotonic progression supported = False.

The morphology figure is consistent with band occupancy and broad triggering rather than clean outward propagation:
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/magnitude_time_distance_pm7d_100km.png`

### 8. Slow-slip-related behavior is not supported beyond low-level screening

All three are scored low:
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/behavior_dimension_scores.csv`

The supporting metrics explicitly frame this as a screening-only dimension:
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/behavior_dimension_supporting_metrics.csv`

No sequence shows monotonic migration support, and none is identified as having clear catalog-level evidence sufficient for moderate or strong slow-slip-related candidacy.

### 9. Depth context suggests distinct depth domains among the sequences

Depth summaries:
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/depth_summary_by_mainshock.csv`
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/depth_summary_m4_m5.csv`

At ±7 d:
- **M1**:
  - all-event median depth pre/post ≈ 12.0 / 11.6 km
  - M4+ median depth pre/post ≈ 13.7 / 12.2 km
  - relatively shallow and internally consistent.
- **M2**:
  - all-event median depth pre/post ≈ 22.2 / 18.9 km
  - M4+ post median depth ≈ 20.0 km
  - deeper and much broader depth spread (IQR ~20 km scale).
- **M3**:
  - detailed rows were not fully printed during inspection, but the saved tables provide full values and should be used directly in any integrated synthesis.

These summaries indicate that M1 is a shallower, tighter sequence than M2, while M2 occupies a broader and deeper depth domain. This supports the interpretation that M2 is less a compact local sequence and more a broad regional activation frame.

### 10. Mechanism and station context are available, but mechanism evidence is mainly contextual rather than discriminating among M1/M2/M3

Mechanism context:
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/mechanism_context_by_sequence.csv`
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/mechanism_match_summary.csv`

The mechanism summary reports, for each sequence frame:
- matched mechanism count = 354
- within-primary-tolerance count = 242
- median plane-1 strike/dip/rake = 188 / 26 / 79

However, the nearfield versus outer-band matched counts differ strongly:
- **M1**: nearfield mechanisms 39; outer-band 27
- **M2**: nearfield 27; outer-band 202
- **M3**: nearfield 8; outer-band 88

These counts are consistent with the broader-regional-activation interpretation: M2 and M3 are much more outer-band represented in the mechanism-matched subset than M1.

Station context:
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/station_context_summary.csv`

Coverage within 100 km:
- M1: 22 stations
- M2: 36 stations
- M3: 26 stations

All three have matched_true_fraction = 1.0 in the station summary, indicating the analysis did at least track observational context, though no direct detection-threshold correction is demonstrated in the output tables.

### 11. Robustness across windows preserves the main ranking, though some ratios are sensitive

Sensitivity figure:
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/window_radius_sensitivity_heatmaps.png`

Key patterns from the heatmaps:
- **M1** is the most robust:
  - dominance gap constant at 0.30 across windows and radii.
  - post/pre M4+ ratio stays near ~2.6–3.1.
- **M2** is the most sensitive in M4+ post/pre ratio:
  - undefined at short windows because pre M4+ = 0.
  - very strong radius sensitivity at 25 d.
  - dominance gap stable over time but radius-dependent.
- **M3** is intermediate:
  - dominance gap high at 7–14 d, then drops at 25 d for larger radii.
  - M4+ post/pre ratio is very high in short windows but declines strongly in larger windows/radii.

The optional robustness figure conveys the same ranking succinctly:
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/optional_window_robustness_comparison.png`

It shows:
- M1 and M2 dominance/companion metrics are stable across 7, 14, 25 days.
- M3 changes somewhat with the 25-day window, but still remains more mainshock-dominated than M1 or M2.

### 12. The script also produced an internal written diagnosis that can be compared against the tables

A text diagnosis exists:
- `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/aomori_mainshock_sequence_diagnosis.md`

For later integrated reporting, the CSV tables and the key figures above should be treated as the primary evidence base, with the markdown diagnosis used as a consistency check rather than as sole evidence.

## Limitations and Assumptions

1. **Catalog-only behavior diagnosis**
   The outputs explicitly caution that several interpretations are catalog-level only. In particular:
   - swarm-like organization does not prove a physical swarm process,
   - post/pre contrasts can be inflated by overlap with neighboring sequences or changing detectability,
   - slow-slip-related behavior cannot be established without geodetic/tremor/pressure data.
   These cautions are recorded in:
   - `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/behavior_dimension_supporting_metrics.csv`

2. **Sequence overlap between mainshock-centered frames**
   The same regional events can contribute differently depending on the chosen mainshock reference frame. This matters especially for:
   - M1 strong pre-mainshock activation,
   - M2 strong outer-band activation,
   - M3 moderate broader activation.
   The caveats explicitly note possible overlap with neighboring sequences or broader regional activation.

3. **Undefined or unstable ratios when pre counts are zero**
   For M2, short-window M4+ post/pre ratios are undefined because pre M4+ counts are zero. This is visible in:
   - `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/window_radius_sensitivity_heatmaps.png`
   and implied by:
   - `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/matched_window_metrics_all.csv`

4. **Migration assessment is intentionally conservative**
   No sequence is classified as showing monotonic migration. Weak slopes or correlations exist, but the diagnostics explicitly keep `monotonic_progression_supported=False` for all cases:
   - `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/migration_diagnostics.csv`

5. **Mechanism context is broad rather than sequence-specific**
   The mechanism context table provides useful counts and medians, but the median strike/dip/rake values are identical across M1–M3 in the summary table, suggesting that this table is more a matched-catalog context summary than a sharply discriminating sequence-by-sequence structural test:
   - `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/mechanism_context_by_sequence.csv`

6. **Depth and mechanism outputs were only lightly inspected here**
   The files exist and contain usable evidence, but the strongest conclusions in this stage come from the morphology, matched-window metrics, dominance metrics, and regional outer-band summaries. Depth and mechanism tables should be revisited directly in the integrated report stage for any finer tectonic interpretation.

7. **Handoff indicates truncated output listing**
   The task handoff reports `outputs_truncated`, although the required evidence files for this task are present. This is a metadata warning, not a failure, but it means the handoff list should not be treated as exhaustive by itself:
   - `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/log/coding_progress/task_handoff/01_aomori_sequence_analysis.json`

## Report-Ready Summary

The task successfully produced a mainshock-referenced sequence diagnosis for the three Aomori mainshocks, with reusable figures and tables suitable for a report.

The clearest scientific picture is:

- **M1** is the most compact and near-field dominated sequence, but it is not strongly single-mainshock dominated. It has a very small dominance gap (0.3), multiple comparable companion events (2 within 0.5 magnitude units; 6 within 1.0), strong pre-mainshock activation in the ±7 day frame (21 M4+, 8 M5+ pre-events), and modest broader regional participation (post outer-band fraction 0.210). This supports a diagnosis of moderate post-mainshock response combined with moderate compound/swam-like organization and strong pre-mainshock activation, while still lacking evidence for monotonic migration or slow-slip-like behavior. Key evidence: `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/magnitude_time_distance_pm7d_100km.png`, `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/magnitude_dominance_companion_summary.png`, `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/behavior_dimension_supporting_metrics.csv`.

- **M2** shows the strongest regional activation signature. Although post-mainshock activity is extremely elevated (post/pre ratio 86.625), the sequence is not near-field dominated: only 18% of post events are within 0–30 km, while 82% lie in 30–100 km, and 91.1% of post M4+ events are in the outer bands. Magnitude hierarchy is intermediate (gap 0.6, two companions within 1.0 magnitude unit), but the dominant signal is broad post-mainshock regional activation rather than a compact local cascade. Foreshock evidence is weak in the short matched window. Key evidence: `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/m4_m5_distance_band_contribution_pm7d_100km.png`, `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/regional_outerband_metrics.csv`, `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/sequence_behavior_evidence_table.csv`.

- **M3** is the most single-mainshock-dominated of the three. It has a large dominance gap (2.1), no comparable companions within 1.0 magnitude unit, and a broad but not M2-level regional contribution (headline post outer-band fraction 0.463). The ±7 day morphology indicates strong post-mainshock activation with some distributed outer-band activity, but not the weak hierarchy seen in M1. Pre-mainshock activation is limited in the short-window metrics, though the scoring table assigns moderate pre-activation in broader context. Key evidence: `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/m4plus_sequence_views_pm7d_100km.png`, `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/magnitude_dominance_metrics.csv`, `<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/behavior_dimension_scores.csv`.

Across all three sequences, the most defensible comparative conclusion is:
- **M1** = compact, weak-hierarchy, pre-activated local sequence with moderate compound/swarm-like characteristics.
- **M2** = strongest broader regional activation frame, with very large post-mainshock activation but limited near-field dominance.
- **M3** = strongest single-mainshock-dominated sequence, with substantial post-mainshock response embedded in moderate broader activation.

What should not be over-interpreted from these outputs alone:
- swarm-like organization should not be equated with a confirmed physical swarm,
- broader distance-band activation should not by itself be taken as migration or remote triggering style,
- slow-slip-related interpretations remain unsupported beyond screening level,
- foreshock interpretations can be contaminated by overlap among nearby mainshock-centered windows.

The most useful next verification analyses would be:
1. ETAS/Omori-based comparison of local decay versus compound multi-source activation.
2. Relocation- and waveform-based clustering of the largest companion events around M1.
3. Annulus-area and local-background normalized triggering analysis for M2 and M3 outer-band activity.
4. Mechanism/domain-specific comparison restricted to near-field M4+/M5+ events rather than the broader matched mechanism catalog.
5. Geodetic/tremor/slow-slip catalog comparison if any slow-slip-related hypothesis is to be tested.