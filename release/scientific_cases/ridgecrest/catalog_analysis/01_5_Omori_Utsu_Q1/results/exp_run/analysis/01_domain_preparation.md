## Scientific Purpose

This task established the fixed spatial and temporal domain definitions needed for the later Omori-Utsu comparison during the Ridgecrest interevent period between the Mw 6.4 and Mw 7.1 mainshocks. The scientific role of this step was to create a reproducible event table for that interevent interval, assign events to the requested Mw 7.1 fault-zone corridor, and partition the corridor into northern and southern subdomains using the primary split latitude of 35.72°N, with additional split-line flags for 35.70°N and 35.74°N robustness checks.

The output of this task directly supports the later question of whether the northern part of the Mw 7.1 fault zone shows systematically smaller Omori p-values than the southern part later in the interevent period, by ensuring that the event selection and domain assignment are fixed and auditable before any rate-model fitting.

## Method and Implementation Evidence

A local metric coordinate system was used to project interevent events and the prescribed Mw 7.1 centerline/corridor geometry, allowing event positions to be expressed in kilometers and tested against the fixed 6.0 km wide corridor. The corridor geometry stored in metadata matches the requested setup: strike 138.0°, centerline start at (-117.735813, 35.897499), centerline end at (-117.362520, 35.559488), total width 6.0 km, half-width 3.0 km, and derived centerline length 50.47 km. These details are preserved in `<PACKAGE_ROOT>/results/exp_run/outputs/01_domain_preparation/domain_metadata.json`.

The interevent event table contains, for each event between the Mw 6.4 and Mw 7.1 mainshocks, the original catalog fields plus projected coordinates and domain flags needed for subsequent analysis: `t_days`, `x_km`, `y_km`, `along_strike_km`, `cross_strike_km`, `in_entire_corridor`, and boolean north/south/on-split flags for split latitudes 35.70°, 35.72°, and 35.74°. This structure is documented by `<PACKAGE_ROOT>/results/exp_run/outputs/01_domain_preparation/interevent_domain_event_table.csv`.

Consistency checks were also saved. The check table confirms that, for the primary 35.72°N split, northern plus southern counts exactly equal the entire-corridor count, with no events falling exactly on the split line. This is important because it shows the primary partition is exhaustive and non-overlapping for the corridor selection. These checks are in `<PACKAGE_ROOT>/results/exp_run/outputs/01_domain_preparation/domain_assignment_checks.csv`.

The domain-assignment diagnostic figure visually verifies that the mapped event selections are scientifically coherent: the fixed corridor follows the Mw 7.1 fault trend, the 35.72°N split line cuts the corridor as intended, and the north/south assigned subsets occupy the expected sides of the split. This figure is `<PACKAGE_ROOT>/results/exp_run/outputs/01_domain_preparation/domain_assignment_diagnostic.png`.

## Key Results and Evidence Files

1. **The interevent catalog for this task contains 4,714 events between the Mw 6.4 and Mw 7.1 mainshocks.**  
   - Evidence: `<PACKAGE_ROOT>/results/exp_run/outputs/01_domain_preparation/domain_assignment_checks.csv` reports `all_interevent_events = 4714`.  
   - Supporting metadata: `<PACKAGE_ROOT>/results/exp_run/outputs/01_domain_preparation/domain_metadata.json` gives the Mw 6.4 and Mw 7.1 times as `2019-07-04T17:33:49.040000+00:00` and `2019-07-06T03:19:53.040000+00:00`.

2. **The fixed Mw 7.1 fault-zone corridor captures 2,852 of the 4,714 interevent events across all magnitudes.**  
   - Evidence: `<PACKAGE_ROOT>/results/exp_run/outputs/01_domain_preparation/domain_counts_primary.csv` and `<PACKAGE_ROOT>/results/exp_run/outputs/01_domain_preparation/domain_assignment_checks.csv`.  
   - The event-table column `in_entire_corridor` in `<PACKAGE_ROOT>/results/exp_run/outputs/01_domain_preparation/interevent_domain_event_table.csv` preserves this assignment event by event.

3. **For the primary split at 35.72°N, the corridor partition is balanced enough to support later north-vs-south comparison, with slightly more events in the south.**  
   - Entire area: 2,852 events, including 109 with M ≥ 3.0  
   - Northern area: 1,402 events, including 50 with M ≥ 3.0  
   - Southern area: 1,450 events, including 59 with M ≥ 3.0  
   - Evidence: `<PACKAGE_ROOT>/results/exp_run/outputs/01_domain_preparation/domain_counts_primary.csv` and `<PACKAGE_ROOT>/results/exp_run/outputs/01_domain_preparation/domain_metadata.json`.

4. **The primary 35.72°N split produces a clean, non-overlapping partition of the corridor.**  
   - `on_split_35p72_all_magnitudes = 0`  
   - `north_plus_south_35p72_all_magnitudes = 2852`  
   - `north_plus_south_minus_entire_35p72_all_magnitudes = 0`  
   - Evidence: `<PACKAGE_ROOT>/results/exp_run/outputs/01_domain_preparation/domain_assignment_checks.csv`.  
   - This is a key integrity result for later cumulative Omori fitting because it confirms that north and south exactly tile the corridor without double counting or ambiguous boundary cases.

5. **The diagnostic figure supports the intended spatial interpretation of the domains.**  
   - The figure shows:
     - all interevent events,
     - corridor events colored by time since Mw 6.4,
     - the Mw 7.1 centerline,
     - dashed corridor boundaries,
     - the 35.72°N split,
     - north-assigned events in blue,
     - south-assigned events in red,
     - Mw 6.4 and Mw 7.1 mainshocks as star symbols.  
   - Visual assessment indicates the corridor is aligned with the NW-SE Mw 7.1 seismicity trend, and the north/south subsets lie predominantly on the intended sides of the split.  
   - Evidence: `<PACKAGE_ROOT>/results/exp_run/outputs/01_domain_preparation/domain_assignment_diagnostic.png`.

6. **The output table is ready for later period-by-period Omori-Utsu fitting without redefining domains.**  
   - The event table already includes the required ingredients for cumulative-window filtering: event time, magnitude, time since Mw 6.4 (`t_days`), projected coordinates, corridor membership, and north/south flags for the primary and robustness split lines.  
   - Evidence: `<PACKAGE_ROOT>/results/exp_run/outputs/01_domain_preparation/interevent_domain_event_table.csv`.

## Limitations and Assumptions

- This task is limited to domain preparation and diagnostics. It does **not** perform Omori-Utsu fitting, bootstrap uncertainty estimation, or any p-value comparison yet.
- Although the overall M ≥ 3.0 counts are adequate for the full interevent interval (109 entire, 50 north, 59 south), some early cumulative periods may still have low counts, especially in the subdivided domains. That later issue is not resolved here and must be handled during fitting.
- The diagnostic figure suggests events cluster densely near the 35.72°N boundary, so later split-line sensitivity using 35.70°N and 35.74°N remains scientifically relevant even though the primary partition is clean.
- The metadata stores a truncated WKT snippet for the local projection rather than a full standalone CRS definition, though the derived projected outputs and corridor metrics indicate the projection step was successfully applied.
- The event table excerpt confirms the presence of the expected fields, but this task report does not independently re-derive the geometry from source code; it relies on the saved outputs and consistency checks.
- No warnings or failures were recorded in the handoff JSON for this task: `<PACKAGE_ROOT>/results/exp_run/log/coding_progress/task_handoff/01_domain_preparation.json`.

## Report-Ready Summary

Task 01 successfully prepared the fixed Ridgecrest interevent analysis domains required for the later Omori-Utsu comparison. Using the prescribed Mw 7.1 fault-zone corridor geometry and a local metric projection, it built an interevent event table for the period between the Mw 6.4 and Mw 7.1 mainshocks and assigned each event to the entire corridor and to north/south subdivisions for split latitudes 35.70°, 35.72°, and 35.74°. For the primary 35.72°N partition, the corridor contains 2,852 interevent events in total, divided into 1,402 northern and 1,450 southern events, with 109, 50, and 59 events respectively at the primary M ≥ 3.0 threshold. The saved integrity checks show that north plus south exactly equals the entire corridor and that no event lies exactly on the 35.72°N split, confirming a clean non-overlapping partition. The diagnostic map visually supports that the fixed corridor follows the Mw 7.1 fault trend and that the north/south assignments are spatially coherent. The main evidence files are `<PACKAGE_ROOT>/results/exp_run/outputs/01_domain_preparation/interevent_domain_event_table.csv`, `<PACKAGE_ROOT>/results/exp_run/outputs/01_domain_preparation/domain_counts_primary.csv`, `<PACKAGE_ROOT>/results/exp_run/outputs/01_domain_preparation/domain_assignment_checks.csv`, `<PACKAGE_ROOT>/results/exp_run/outputs/01_domain_preparation/domain_metadata.json`, and `<PACKAGE_ROOT>/results/exp_run/outputs/01_domain_preparation/domain_assignment_diagnostic.png`.