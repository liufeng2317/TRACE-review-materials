
You are an earthquake scientist and data-analysis agent.

Current task:
Perform event-centered sequence analysis for the three matched major earthquakes in the Aomori regional catalog.

Goal:
Compare the pre- and post-event seismicity evolution around M1, M2, and M3, and test whether the observed sequence patterns are robust under different spatial, temporal, depth, and magnitude definitions.

Data folder:
"<CASE_ROOT>/data"

Files:
- catalog/Snet_catalog_relocate.csv
- catalog/main_earthquake.csv
- source_mechanism/Snet_mecha.csv
- stations/station.sta

Background guidance from the previous data-foundation analysis:
- The regional catalog is large and internally consistent enough for sequence analysis.
- The three major earthquakes can be matched to the relocated catalog with high confidence.
- Regional seismicity is clustered and spatially segmented.
- Temporal activity is burst-like, so time-window sensitivity is important.
- Preliminary Mc is around 1.2 for the full catalog; use it as a screening value and test higher thresholds.
- M1 and M3 show strong local seismicity enrichment and should be compared carefully.
- M2 may be depth-distinct and should be analyzed with depth stratification.
- Station coverage and focal-mechanism availability are uneven and should be treated as contextual limitations.

Tasks:

1. Minimal data verification
Read the original files and verify the fields needed for sequence analysis:
time, latitude, longitude, depth, magnitude, event ID if available, major-earthquake records, station locations, and focal-mechanism availability.
Re-match the three major earthquakes with the regional catalog before sequence extraction, allowing for small time or location shifts caused by relocation.

2. Sequence extraction
For each major earthquake, extract surrounding events using multiple definitions:
- radii: 30, 44, 50, 80, and 100 km
- time windows: pre-90d, pre-60d, pre-30d, pre-7d, post-7d, post-30d, post-60d, and post-90d
- depth windows: all depths, local mainshock-centered depth windows, and depth-stratified windows
- magnitude thresholds: all events, M >= 1.2, M >= 1.5, M >= 2.0, and M >= 2.5 where feasible

3. Sequence diagnostics
For each sequence and parameter setting, calculate:
- event counts
- cumulative event counts
- moving-window seismicity rates
- pre/post rate ratios
- magnitude distributions
- depth distributions
- post-event rate decay diagnostics, including simple Omori-style fitting if feasible
- time-distance and radial-distance patterns relative to each mainshock
- spatial concentration or expansion indicators if visible
- focal-mechanism availability within the sequence window, and simple mechanism summaries if feasible

4. Robustness analysis
Identify which sequence features are stable across radius, time window, depth window, and magnitude threshold.
Separate robust patterns from parameter-dependent patterns.

5. Three-sequence comparison
Compare M1, M2, and M3 in terms of:
- background activity level
- pre-event activity
- post-event activity
- temporal burstiness
- aftershock decay behavior
- spatial concentration or expansion
- depth structure
- magnitude distribution
- sensitivity to sequence definitions

6. Simple control comparison
Include at least one feasible control:
- background windows away from the mainshock times
- randomized mainshock times
- comparison using higher magnitude thresholds
- or simple background-rate comparison before and after each mainshock

7. Diagnostic figures
Generate high-quality sequence-analysis figures (**Nature-style** publication-quality figures):
- event-centered maps for M1, M2, and M3
- pre/post spatial comparison maps
- cumulative count curves
- moving-window rate curves
- post-event rate decay plots
- time-distance or radial-distance plots relative to each mainshock
- radius and time-window sensitivity heatmaps
- magnitude-threshold sensitivity plots
- depth-stratified sequence plots
- three-sequence comparison summary figure

Use consistent axes, colors, labels, legends, and mainshock markers across M1/M2/M3.
The agent may design additional standard earthquake-sequence analysis plots when they help test robustness, compare the three sequences, or prepare for later M1-M3 focused analysis.

The final response can include a concise summary, but prioritize reusable sequence-analysis tables, robustness results, and publication-quality figures.
