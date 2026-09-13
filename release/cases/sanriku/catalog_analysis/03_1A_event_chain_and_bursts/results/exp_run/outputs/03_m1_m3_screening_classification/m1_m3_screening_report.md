# M1-M3 screening classification

## Scope and caution
This is a catalog-level, non-causal screening summary for the M1-M3 local system. The interpretation is based on fixed windows and local/corridor geometry only. Temporal order or spatial proximity alone are not treated as evidence of triggering or physical causality.

## Reference interval
- M1 origin time: 2025-11-09T08:03:39.240000+00:00
- M3 origin time: 2026-04-20T07:52:58.060000+00:00
- Conservative pre-M1 baseline: catalog start to M1-14 d
- Sensitivity pre-M1 baseline: catalog start to M1-7 d
- M1-related dominated phase: M1-14 d to M1+21 d
- Middle phase: M1+21 d to M3-35 d
- Pre-M3 local activation phase: M3-35 d to M3

## Main screening conclusions
- **pre_existing_local_activity_before_M1**: raw=present; m2aware=present
- **M1_related_swarm_aftershock_dominated**: raw=strong; m2aware=strong
- **middle_phase_activity_after_M1_plus_21d**: raw=sustained; m2aware=sustained
- **continuous_activation_chain**: raw=not_supported; m2aware=not_supported
- **separated_bursts**: raw=yes; m2aware=yes
- **endpoint_centered_activity**: raw=yes; m2aware=yes
- **pre_M3_local_activation**: raw=clear_local_activation; m2aware=clear_local_activation
- **corridor_like_activity**: raw=no_or_mixed; m2aware=no_or_mixed
- **apparent_migration**: raw=not_robust; m2aware=not_robust
- **endpoint_switching_or_mixed_endpoint_sequences**: raw=mixed_endpoint_sequences; m2aware=mixed_endpoint_sequences
- **broader_regional_or_background_component**: raw=subordinate; m2aware=subordinate
- **M2_affected_or_ambiguous_mixed_behavior**: raw=compare_raw_and_m2aware; m2aware=compare_raw_and_m2aware

## Key evidence
- Pre-M1 local activity is clearly present: 20 M3+ events over 146.1 d (0.137/d) using the conservative baseline, and 21 M3+ using the M1-7 d sensitivity baseline.
- The M1-related dominated phase is the strongest component of the M1-M3 interval: 335 M3+ with rate ratio 23.94x relative to the conservative baseline, contributing 83.5% of full-interval M3+.
- After separating the M1-related phase, the middle phase is not empty: 79 M3+ with rate ratio 3.33x baseline, so the interval after M1+21 d is better described as sustained but weaker than the M1-related phase, not homogeneous with it.
- The final pre-M3 window also shows distinct local activity: 52 M3+ with rate ratio 6.36x baseline, consistent with pre-M3 local activation that remains after M2-aware flagging (389 M3+ for full M1-M3 versus 401 raw).
- Endpoint cores dominate more than corridor non-core activity. In the full M1-M3 interval, M1-core=0.69, M3-core=0.18, corridor non-core=0.06, off-corridor local=0.07.
- The M1-related phase is strongly M1-core weighted (M1-core 0.77, M3-core 0.15), while the pre-M3 phase still remains M1-core heavy overall (M1-core 0.67, M3-core 0.18) rather than becoming a dominant corridor sequence.
- The chain is better described as burst-separated and endpoint-centered than as a clean corridor migration: the full-interval M1-related fraction is 83.5%, while middle+pre-M3 still contribute 32.7% of M3+, indicating important later activity but not a single uniform episode.

## M2-aware comparison
- Full M1-M3 M3+ counts change from 401 raw to 389 M2-aware (3.0% removed).
- The main interpretation is therefore M2-aware but not M2-dominated: M2 flagging modestly reduces some middle/pre-M3 counts but does not remove the pre-existing activity, the strong M1-related phase, or the later pre-M3 activation signal.

## Recommended follow-up
1. Spatial-depth screening to test whether middle-phase and pre-M3 activity occupy distinct depth bands or endpoint clusters.
2. b-value / completeness screening by fixed window, since the local sample is large enough for phase-wise magnitude-frequency comparison.
3. Burst-wise migration checks only after keeping M1-related, middle, and pre-M3 windows separate.
4. Optional focal-mechanism screening for the best-sampled endpoint or burst groups only.

## Bottom-line classification
The M1-M3 local system is best screened as: **pre-existing local activity before M1**, a **strong M1-related swarm/aftershock-dominated phase**, a **non-empty but weaker middle phase after M1+21 d**, **separated bursts** rather than a homogeneous continuous sequence, **endpoint-centered activity** more than corridor-dominated activity, and **clear pre-M3 local activation** that survives M2-aware comparison. The apparent full-interval along-axis trend is **not robust enough to call continuous migration** after window separation; it is better treated as **mixed endpoint-centered behavior with possible switching/overlap, not a confirmed migrating chain**.
