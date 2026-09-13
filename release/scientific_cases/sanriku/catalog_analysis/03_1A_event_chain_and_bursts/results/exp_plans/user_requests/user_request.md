
You are an earthquake scientist and data-analysis agent.

Current task:
Analyze the M1-M3 event chain and burst structure using the relocated/filtered Aomori active-year catalog.

Goal:
Determine whether the M1-M3 local system shows pre-existing activity before M1, sustained activation between M1 and M3, separated bursts, endpoint-centered activity, pre-M3 local activation, corridor-like activity, or broader regional/background activity.

This is a catalog-level screening task. Do not infer triggering or physical causality from temporal order or spatial proximity alone.
Pay special attention to separating the M1-related swarm/aftershock-dominated phase from later M1-M3 interval activity. Do not treat the full M1-to-M3 interval as one homogeneous sequence unless the data support that interpretation.

Data folder:
"<CASE_ROOT>/data"
Inputs:
- relocated/filtered catalog:
  data/Snet_catalog_relocate_250601_260501.csv
- mainshock table:
  catalog/main_earthquake.csv
Context files:
- source_mechanism/Snet_mecha.csv
- stations/station.sta

Core design:
Use the M1-M3 local/corridor region as the primary spatial domain, not the whole catalog.
Define and compare:
1. M1-M3 local union:
   events within 60 km of either M1 or M3. This is the primary analysis region.
2. Endpoint core zones:
   events within 30 km of M1 or M3. Use these to identify near-source endpoint activity.
3. Endpoint extended zones:
   events within 60 km of M1 or M3. Use these to test broader local activation around each endpoint.
4. M1-M3 corridor:
   events projected between M1 and M3, with perpendicular distance <=20-30 km, including endpoint buffers.
5. M2-related region:
   events within 100 km of M2. Flag these events as M2-related or ambiguous rather than removing them by default, and compare raw versus M2-aware results.

Temporal-window design:
Use a small set of fixed, interpretable phase windows first, then allow limited data-driven refinements where useful. Keep the main interpretation centered on these non-overlapping windows:
1. pre-M1 background baseline:
   available catalog start to M1-14d as the conservative primary baseline, and to M1-7d as a sensitivity baseline.
   Do not use a baseline ending at M1, because the final days before M1 may already belong to the M1-related swarm-like phase.
2. M1-related dominated phase:
   M1-14d to M1+21d as the primary window, with nearby sensitivity checks such as M1-7d to M1+14d or M1-14d to M1+28d if the catalog suggests different burst boundaries.
   Treat this as the M1-related swarm/aftershock-dominated phase and discuss it separately from later M1-M3 activity.
3. M1-M3 middle phase:
   M1+21d to M3-35d as the primary window, adjusted only if the chosen M1-related or pre-M3 sensitivity boundary changes.
   This window tests whether activity persists away from the M1-related phase and before the final pre-M3 weeks.
4. pre-M3 local activation phase:
   M3-35d to M3 as the primary window, with M3-42d or M3-28d sensitivity checks if useful.
   This window tests whether there is renewed local activation before M3.
5. post-M3 context:
   M3 to M3+7d and/or M3+14d if useful, but keep it separate from all pre-M3 and M1-to-M3 interpretations.

The agent may optionally test nearby alternatives, such as a 1-2 week pre-M1 lead-in, a 2-4 week post-M1 tail, or a 2-6 week pre-M3 window, if the catalog suggests that the fixed M1-14d/M1+21d/M3-35d boundaries are poorly aligned with burst gaps. However, the primary report must remain based on the main phase windows above. Do not introduce many nested lookback windows unless they directly clarify a specific ambiguity.

Data-driven windows based on event-rate changes, burst gaps, or endpoint transitions are allowed, but they must be reported as secondary sensitivity checks. They must not merge the M1-related dominated phase with the final pre-M3 phase without explicitly quantifying the effect.

Main questions:
1. What is the M1-M3 local background activity level before M1, using a baseline that stops before the immediate pre-M1 swarm-like days?
2. How do M3+, M4+, M5+, and M6+ events evolve from M1 to M3?
3. Is there an M1-related swarm-like increase in the final 14 days or final 7 days before M1 compared with the earlier pre-M1 background baseline?
4. How much of the M1-to-M3 activity is explained by the M1-related dominated phase around M1?
5. After separately accounting for the M1-related dominated phase, is the M1-M3 middle phase sustained, burst-separated, or relatively quiet?
6. Are events mainly concentrated near M1, near M3, inside the M1-M3 corridor, or off-corridor in each time window?
7. Does activity persist through the M1-M3 interval, occur as separated bursts, or concentrate only around endpoints?
8. Is there clear local activation in the final five weeks before M3, independent of the M1-related dominated phase?
9. Does any apparent along-axis migration remain after separating the M1-related dominated phase, middle phase, and pre-M3 local activation, or is it better described as endpoint switching / mixed endpoint sequences?
10. How much of the apparent M1-M3 event chain is affected by M2-related activity?
11. Which event-chain patterns deserve follow-up in spatial-depth, b-value, migration, or mechanism screening?

Tasks:
- Build an M1-M3 event-chain table covering the available pre-M1 period, the M1-to-M3 interval, and a short post-M3 window if useful (but do not mix with preceding windows).
- For each event, compute:
  time since M1
  time before M3
  distance to M1
  distance to M3
  projected distance along the M1-M3 axis
  perpendicular distance to the M1-M3 axis
  depth
  magnitude
  endpoint/core/extended/corridor/off-corridor category,
  M2-related or ambiguous flag.
- Summarize M3+, M4+, M5+, and M6+ counts and rates for:
  pre-M1 background baseline ending at M1-14d
  pre-M1 background baseline sensitivity ending at M1-7d
  M1-related dominated phase: M1-14d to M1+21d
  optional M1-related phase sensitivity windows such as M1-7d to M1+14d and M1-14d to M1+28d, if useful
  full M1-to-M3 interval
  inter-mainshock middle phase: M1+21d to M3-35d
  final pre-M3 local activation phase: M3-35d to M3.
- When comparing M1-to-M3 activity against a baseline, use the baseline ending at M1-14d as the conservative primary baseline and the baseline ending at M1-7d as a sensitivity check. Do not use a baseline ending exactly at M1 unless it is clearly labeled as contaminated by the M1-related swarm-like lead-in.
- For each fixed window, summarize endpoint/core/corridor/off-corridor composition and explicitly compare M1-core versus M3-core contributions.
- Detect major bursts or rate peaks where feasible, and report their timing, location, depth range, largest magnitude, dominant spatial category, and whether the burst belongs to:
  M1-related dominated phase,
  intermediate M1-M3 activity,
  pre-M3 local activation,
  post-M3 context,
  or mixed/ambiguous behavior.
- Test whether apparent migration is robust to window separation:
  compare along-axis centroid trends for the full M1-to-M3 interval versus the M1-related dominated, middle, and pre-M3 windows separately.
  If the apparent trend is mostly caused by mixing M1-core and M3-core sequences, describe it as endpoint switching or mixed endpoint activity rather than continuous migration.
- Compare raw M1-M3 event-chain metrics with M2-aware metrics.
- Compare M1-M3 local activity with a simple background/control region or control time window where feasible.
- Assess whether the event chain is continuous, burst-separated, endpoint-centered, corridor-like, pre-M3 localized, migration-like, endpoint-switching, or mixed/ambiguous.

Figures:
Generate a compact set of high-quality diagnostic figures:
- M1-M3 map with M3+/M4+/M5+ events colored by time and labeled by category;
- magnitude-time plot from pre-M1 through M3;
- projected distance versus time along the M1-M3 axis;
- distance-to-M1 and distance-to-M3 versus time;
- cumulative M4+/M5+ count curves for raw and M2-aware versions;
- burst timeline summary with pre-M1 baseline, M1-related dominated, middle, pre-M3, and post-M3 windows marked;
- pre-M3 local activation comparison before and after M2-aware flagging/filtering.
- window-separated endpoint/corridor composition figure, showing M1-core, M3-core, corridor non-core, and off-corridor local fractions for the required fixed windows.

Optional agent-designed analyses:
After completing the required diagnostics, design additional catalog-based analyses only if they directly clarify the M1-M3 event-chain question. Useful options may include:
- endpoint-radius sensitivity: 30 km vs 60 km;
- corridor-width sensitivity: 20 km vs 30 km;
- magnitude-threshold robustness: M3+, M4+, M5+, M6+;
- burst-centroid tracking through time;
- window-separated burst-centroid tracking, keeping the M1-related dominated phase separate from later activity;
- event-chain continuity or gap analysis;
- nearest-endpoint transition analysis;
- comparison with matched control windows or off-corridor regions.
Do not add analyses that do not directly help distinguish M1-related dominated activity, intermediate M1-M3 activity, continuous activation, separated bursts, endpoint-centered activity, pre-M3 local activation, corridor-like activity, apparent migration, endpoint switching, or broader regional/background activity.

Final report:
Provide a concise report identifying whether the M1-M3 interval is best described as:
- pre-existing local activity before M1;
- M1-related swarm/aftershock-dominated activity relative to the earlier pre-M1 background baseline;
- quiet or sustained intermediate M1-M3 activity after M1+21d;
- continuous activation chain;
- separated bursts;
- endpoint-centered activity;
- pre-M3 local activation;
- corridor-like activity;
- apparent migration;
- endpoint switching or mixed M1-core/M3-core sequences;
- broader regional/background activity;
- M2-affected or ambiguous mixed behavior.

Important:
Do not infer triggering from temporal order or spatial proximity alone.
Do not treat M2-related events as contamination by default; quantify their influence.
Do not define the pre-M1 background baseline as ending exactly at M1. The final 14 days before M1 should be treated as part of the M1-related dominated phase, with an M1-7d baseline cutoff used as a sensitivity check.
Do not describe along-axis centroid changes as migration unless the signal remains after separating the M1-related dominated phase from the middle and pre-M3 windows.
If the apparent migration is caused by mixing M1-core aftershocks with later M3-core or corridor events, state that explicitly.
Treat all mechanism interpretations as catalog-level hypotheses.
Prioritize deciding whether the M1-M3 catalog pattern is worth deeper spatial-depth, b-value, migration, or mechanism screening.
