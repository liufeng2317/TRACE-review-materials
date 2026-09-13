
You are an earthquake scientist and data-analysis agent.

Current task:
Analyze the spatial-depth structure, apparent migration, and burst-centroid evolution of the M1-M3 local earthquake system.

Goal:
Use the relocated/filtered Aomori active-year catalog to determine whether the M1-M3 activity is better described as endpoint switching, separated local bursts, corridor-like stepwise activation, spatial-depth coherent activation, diffuse local occupancy, or no organized migration.

This is a catalog-level screening task. Do not infer triggering or physical causality from spatial-temporal organization alone.
Use the current event-chain and burst-screening results as working context. In particular, do not treat the full M1-to-M3 interval as a homogeneous migration sequence.
Recompute the relevant spatial-depth and centroid diagnostics in this task; use the prior screening context to guide the tests, not as conclusions to copy. If the spatial-depth evidence contradicts the working context, report the contradiction clearly.

Data folder:
"<CASE_ROOT>/data"
relocated/filtered catalog:
  data/Snet_catalog_relocate_250601_260501.csv
Context files:
  - catalog/main_earthquake.csv
  - source_mechanism/Snet_mecha.csv
  - stations/station.sta

Current event-chain screening findings to use as working context:
- The pre-M1 background baseline should end before the M1-related lead-in. Use catalog start to M1-14d as the conservative baseline and catalog start to M1-7d as a sensitivity baseline.
- The M1-M3 local system shows modest pre-existing M3-class activity before M1, but no M4+ in the conservative M1-14d baseline.
- The full M1-to-M3 interval is much stronger than the conservative pre-M1 baseline.
- The M1-related dominated phase from M1-14d to M1+21d contains most large-event activity in the full M1-to-M3 interval.
- After separating the M1-related dominated phase, the M1-M3 middle phase from M1+21d to M3-35d remains active and elevated above baseline, but is much weaker than the M1-related phase.
- The final pre-M3 local activation phase from M3-35d to M3 remains clear and is stable under M2-aware comparison.
- Spatial composition is endpoint-centered rather than corridor-dominated: M1-core and M3-core fractions exceed corridor-noncore fractions in the main windows.
- Apparent along-axis migration is not robust after phase separation; mixed endpoint-centered behavior or endpoint switching/overlap is favored over continuous migration.
- M2-aware flagging has modest overall influence and does not remove the main M1-related, middle-phase, or pre-M3 conclusions, although it affects some middle-phase counts.
- These are catalog-level observations, not evidence of physical triggering.

Primary temporal phases for this task:
1. pre-M1 background baseline: catalog start to M1-14d, with catalog start to M1-7d as sensitivity.
2. M1-related dominated phase: M1-14d to M1+21d, with optional sensitivity windows M1-7d to M1+14d and M1-14d to M1+28d.
3. M1-M3 middle phase: M1+21d to M3-35d.
4. pre-M3 local activation phase: M3-35d to M3, with optional sensitivity windows M3-42d to M3 and M3-28d to M3.
5. post-M3 context: M3 to M3+7d and/or M3+14d, kept separate from pre-M3 interpretation.

Core scientific questions:
1. Do M1-M3 bursts or phase-separated centroids show systematic spatial movement through time after separating the M1-related dominated, middle, and pre-M3 phases?
2. Is there evidence for stepwise activation from M1 toward M3, or is the pattern better explained by endpoint-centered bursts / endpoint switching / overlap?
3. Are burst centroids located near M1, near M3, inside the corridor, or off-corridor?
4. Do M3+, M4+, and M5+ events show the same spatial-depth pattern?
5. Are the main bursts concentrated in a consistent depth range or structural domain?
6. Is any apparent migration robust to phase separation, M2-aware filtering, magnitude threshold, corridor width, and endpoint radius?
7. Which spatial-depth patterns deserve follow-up with relocation, waveform similarity, mechanism comparison, or stress modeling?

Spatial definitions:
Use the same M1-M3 spatial framework:
- M1-M3 local union: events within 60 km of either M1 or M3.
- Endpoint core zones: events within 30 km of M1 or M3.
- Endpoint extended zones: events within 60 km of M1 or M3.
- M1-M3 corridor: projection between M1 and M3 with perpendicular distance <=20-30 km, including endpoint buffers.
- M2-related region: events within 100 km of M2; flag but do not remove by default.

Main tasks:

1. Phase- and burst-level spatial summary
For each primary temporal phase, compute:
- event count by threshold: M3+, M4+, M5+
- largest magnitude
- centroid latitude and longitude
- median and range of depth
- median projected distance along the M1-M3 axis
- median perpendicular distance to the M1-M3 axis
- distance to M1 and M3
- endpoint/core/corridor/off-corridor composition
- M2-related fraction.

For each major burst or rate peak, compute:
- start and end time
- event count by threshold: M3+, M4+, M5+
- largest magnitude
- centroid latitude and longitude
- median and range of depth
- median projected distance along the M1-M3 axis
- median perpendicular distance to the M1-M3 axis
- distance to M1 and M3
- dominant spatial category: M1 endpoint, M3 endpoint, corridor, off-corridor, mixed, or ambiguous
- M2-related fraction.

2. Burst-centroid evolution
Track phase and burst centroids through time.
Evaluate whether centroids:
- remain near M1
- shift toward M3
- jump between endpoint zones
- occupy central corridor positions
- disperse without clear organization.

Report centroid movement distance, direction, projected-axis change, and ambiguity. Distinguish changes caused by mixing the M1-related dominated phase with later phases from changes that remain within individual phases.

3. Migration and projection diagnostics
Test whether events show:
- monotonic migration along the M1-M3 axis
- stepwise activation between burst centers
- radial expansion from M1
- convergence toward M3
- diffuse occupancy without directional trend.

Use simple quantitative diagnostics where feasible:
- projected distance versus time slope
- Spearman or Kendall correlation between time and projected distance
- median projected position by time bin
- distance-to-M1 and distance-to-M3 trends
- event-front or burst-front movement if meaningful.

Run these diagnostics separately for the M1-related dominated phase, middle phase, pre-M3 phase, and full M1-to-M3 interval. State clearly when no robust monotonic migration is supported, especially if the full-interval trend is mostly an artifact of combining endpoint-centered phases.

4. Depth-domain analysis
Analyze depth structure for:
- M1 endpoint events
- M3 endpoint events
- corridor events
- off-corridor local events
- each major burst.

Report whether the sequence is concentrated in:
- 0-30 km
- 30-60 km
- >60 km

Check whether M1, M3, and intervening M4+/M5+ events occupy a similar depth range or distinct depth domains.

5. Robustness checks
Repeat key spatial-depth and migration diagnostics for:
- M3+, M4+, and M5+ subsets
- raw and M2-aware event sets
- corridor width 20 km and 30 km
- endpoint core 30 km and endpoint extended 60 km definitions.
- primary versus sensitivity temporal windows where useful.

Do not generate exhaustive figures for all settings. Summarize robustness in tables and only plot the most informative contrasts.

Figures:
Generate a compact set of high-quality diagnostic figures:
- M1-M3 phase and burst-centroid map colored by phase/burst time
- projected distance versus time with burst centroids overlaid
- depth versus projected distance plot
- depth-time plot for M3+/M4+/M5+ events
- phase-separated centroid trajectory figure
- phase-separated endpoint/core/corridor composition figure
- raw versus M2-aware migration/projection comparison if different
- spatial-depth evidence matrix summarizing endpoint, corridor, depth-domain, and migration support

Final report:
Provide a concise report answering:
- Is M1-M3 activity better described as endpoint switching, stepwise activation, corridor-like occupancy, monotonic migration, or diffuse local occupancy?
- Do phase or burst centers move systematically from M1 toward M3 after separating the M1-related dominated phase?
- Is pre-M3 activity spatially and depth-wise connected to the middle phase and/or M1-related phase, or is it a separate endpoint-centered activation?
- Are M4+/M5+ events consistent with the same spatial-depth structure as smaller events?
- Does M2-aware filtering change the spatial-depth or migration interpretation?
- Which hypotheses should be carried into the next catalog-screening step, such as b-value, moment-release, and mechanism-evidence analysis?

Important:
Do not infer triggering, stress transfer, fluid migration, or slow slip from catalog geometry alone.
A corridor-like pattern is not equivalent to migration unless there is a robust time-ordered spatial trend.
Separate endpoint-centered bursts, stepwise activation, and smooth migration.
Do not describe a full-interval centroid shift as migration unless it remains after separating the M1-related dominated, middle, and pre-M3 phases.
Do not overstate corridor-like occupancy when endpoint-core fractions dominate corridor-noncore fractions.
Prioritize identifying which spatial-depth patterns are strong enough to justify relocation, waveform similarity, focal-mechanism, or stress-modeling follow-up.
