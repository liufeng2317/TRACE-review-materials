## Scientific Purpose

This task established the fixed geometric framework needed for all later spatiotemporal triggering analyses in the Ridgecrest sequence. Specifically, it defined and quality-controlled:
- a local metric coordinate system for distance-based analysis,
- two fixed 6 km-wide fault-oriented corridors representing the Mw 6.4-associated and Mw 7.1-associated structural trends,
- two independent 10 km-radius near-mainshock diagnostic neighborhoods around the Mw 6.4 and Mw 7.1 epicenters,
- event-level assignments of the pre-Mw 7.1 catalog into these masks.

The scientific role of this task is foundational: it determines whether later comparisons of seismic-rate evolution between Region A and Region B are based on geometrically defensible, reproducible, and spatially interpretable domains. The outputs therefore provide the evidence that the selected corridors capture the intended two fault-direction systems without obvious omission of the key Mw 6.4-to-Mw 7.1 linkage zone.

## Method and Implementation Evidence

A local projected metric system was implemented using a modified azimuthal equidistant projection centered on the Ridgecrest study area, enabling horizontal distances, along-strike projections, and corridor widths to be defined in kilometers rather than degrees. The projection definition is documented in `<PACKAGE_ROOT>/results/exp_run/outputs/01_region_geometry_assignment/metadata/region_geometry_metadata.json`.

Using the user-specified fixed geometry:
- Region A was defined with strike 39°, half-width 3 km, and finite centerline from (-117.635877, 35.555024) to (-117.463113, 35.729199), with measured centerline length 24.87 km.
- Region B was defined with strike 138°, half-width 3 km, and finite centerline from (-117.735813, 35.897499) to (-117.362520, 35.559488), with measured centerline length 50.47 km.
- The Mw6.4 and Mw7.1 diagnostic neighborhoods were implemented as independent 10 km-radius circles in projected coordinates.

Event-level outputs confirm that each catalog event was assigned quantitative geometry attributes, including projected coordinates, along-strike and across-strike coordinates for both corridors, distances to both mainshocks, and Boolean membership masks for Region A, Region B, corridor overlap, and the two mainshock neighborhoods. These fields are preserved in `<PACKAGE_ROOT>/results/exp_run/outputs/01_region_geometry_assignment/tables/event_region_assignments.csv`.

Quality control was implemented through:
- a full assignment map with mapped faults, centerlines, corridor boundaries, neighborhood circles, and event coloring by time since Mw 6.4,
- separate across-centerline histograms for Regions A and B to test corridor width adequacy,
- separate along-strike histograms for Regions A and B to test finite centerline span adequacy,
- a diagnostic map of unassigned events to evaluate whether important seismicity was omitted from the fixed corridors.

Compact quantitative summaries were stored in `<PACKAGE_ROOT>/results/exp_run/outputs/01_region_geometry_assignment/tables/region_assignment_summary.csv`.

## Key Results and Evidence Files

### 1. The fixed corridors capture the two intended seismicity lineations and their linkage zone

The assignment map shows two oblique, intersecting corridor systems:
- Region A follows the SW-NE to NE-SW trend associated with the Mw 6.4 fault system.
- Region B follows the NW-SE Little Lake / Mw 7.1 trend.
- The two corridors intersect near the central part of the mapped seismicity, creating an overlap zone that coincides with concentrated seismicity between the two source regions.

The map also shows the Mw 6.4 and Mw 7.1 mainshocks lying within the intended geometric context, with the 10 km neighborhood circles centered on the two epicentral areas. Event colors by time since Mw 6.4 indicate that both structural trends host time-evolving seismicity within the fixed domains.

Evidence:
- `<PACKAGE_ROOT>/results/exp_run/outputs/01_region_geometry_assignment/figures/fixed_corridor_assignment_map.png`
- `<PACKAGE_ROOT>/results/exp_run/outputs/01_region_geometry_assignment/metadata/region_geometry_metadata.json`

### 2. Event assignment statistics indicate strong corridor coverage with modest unassigned fraction

The assignment summary shows:
- Region A assigned event count: 2817 events, 59.24% of the catalog.
- Region B assigned event count: 2876 events, 60.48% of the catalog.
- Corridor overlap count: 1239 events, 26.06% of the catalog.
- Unassigned-to-corridors fraction: 6.33%.

These values indicate that the two fixed corridors collectively cover the dominant portion of the pre-Mw 7.1 seismicity while preserving a meaningful overlap zone rather than forcing artificial exclusivity. The relatively small unassigned fraction supports the use of these corridors as the primary domains for subsequent temporal triggering analysis.

Evidence:
- `<PACKAGE_ROOT>/results/exp_run/outputs/01_region_geometry_assignment/tables/region_assignment_summary.csv`
- `<PACKAGE_ROOT>/results/exp_run/outputs/01_region_geometry_assignment/tables/event_region_assignments.csv`

### 3. Region A corridor width is adequate and does not show strong boundary truncation

The Region A across-centerline histogram shows assigned events concentrated well within the ±3 km half-width, with the highest density in the corridor interior rather than at the boundaries. The distribution is somewhat asymmetric, with a slight negative-side bias, but it does not show strong edge pile-up that would suggest severe truncation.

Quantitatively:
- Region A median absolute across-centerline distance: 0.858 km.
- Region A 95th percentile absolute across-centerline distance: 2.404 km.

Because the 95th percentile remains below the 3 km half-width, the fixed width appears sufficient for capturing the intended Region A seismicity cloud.

Evidence:
- `<PACKAGE_ROOT>/results/exp_run/outputs/01_region_geometry_assignment/figures/region_a_across_centerline_distribution.png`
- `<PACKAGE_ROOT>/results/exp_run/outputs/01_region_geometry_assignment/tables/region_assignment_summary.csv`

### 4. Region B corridor width is also adequate, though its event cloud is more offset from the centerline than Region A

The Region B across-centerline histogram likewise shows most assigned events within the ±3 km bounds, with counts highest inside the corridor rather than at its edges. The distribution is somewhat shifted toward positive across-centerline values, indicating that the chosen centerline is not perfectly centered on the seismicity cloud, but the fixed width still contains the dominant cluster.

Quantitatively:
- Region B median absolute across-centerline distance: 1.028 km.
- Region B 95th percentile absolute across-centerline distance: 2.676 km.

Compared with Region A, Region B is slightly broader or more off-centered relative to its centerline, but still remains mostly contained within the prescribed half-width.

Evidence:
- `<PACKAGE_ROOT>/results/exp_run/outputs/01_region_geometry_assignment/figures/region_b_across_centerline_distribution.png`
- `<PACKAGE_ROOT>/results/exp_run/outputs/01_region_geometry_assignment/tables/region_assignment_summary.csv`

### 5. Region A centerline span closely matches the occupied along-strike seismicity extent

The Region A along-strike histogram indicates that assigned seismicity spans nearly the full finite centerline, from near the start to near the end of the 24.87 km segment, although activity is uneven and is strongest in the later part of the corridor.

Quantitatively:
- along-strike minimum: 0.206 km
- along-strike maximum: 24.861 km
- centerline length: 24.865 km

This close agreement shows that the finite Region A centerline was chosen to match the occupied event cloud rather than to overextend far beyond it.

Evidence:
- `<PACKAGE_ROOT>/results/exp_run/outputs/01_region_geometry_assignment/figures/region_a_along_strike_distribution.png`
- `<PACKAGE_ROOT>/results/exp_run/outputs/01_region_geometry_assignment/tables/region_assignment_summary.csv`

### 6. Region B centerline fully contains the seismicity but is longer than the occupied active segment

The Region B along-strike histogram shows that most assigned events occupy only a middle section of the full 50.47 km centerline, with strongest concentration roughly in the 20-35 km range and sparse occupancy near the ends.

Quantitatively:
- along-strike minimum: 0.257 km
- along-strike maximum: 49.222 km
- centerline length: 50.469 km

Thus, Region B fully contains the intended structure, but unlike Region A, its finite span exceeds the main active cloud, especially toward the ends. This is acceptable for later analysis, but should be remembered when interpreting along-strike patterns: inactive portions of the Region B corridor are part of the fixed geometry.

Evidence:
- `<PACKAGE_ROOT>/results/exp_run/outputs/01_region_geometry_assignment/figures/region_b_along_strike_distribution.png`
- `<PACKAGE_ROOT>/results/exp_run/outputs/01_region_geometry_assignment/tables/region_assignment_summary.csv`

### 7. Unassigned events do not form a missed alternative corridor through the key Mw 6.4-to-Mw 7.1 zone

The unassigned-event diagnostic map shows that events outside both corridors are mainly scattered outside the principal corridor bands and do not organize into a strong coherent linear trend through the key linkage zone. Some unassigned events occur near the central cluster, but they appear as diffuse off-fault or peripheral seismicity rather than evidence that the fixed Region A and Region B geometries miss the principal triggering pathway.

This supports the interpretation that the fixed corridors are suitable for subsequent testing of asynchronous activation, rate evolution differences, and internal triggering order.

Evidence:
- `<PACKAGE_ROOT>/results/exp_run/outputs/01_region_geometry_assignment/figures/unassigned_event_diagnostic_map.png`
- `<PACKAGE_ROOT>/results/exp_run/outputs/01_region_geometry_assignment/tables/region_assignment_summary.csv`

### 8. The event-level table preserves the masks needed for later synchronous-versus-delayed triggering tests

The event assignment table includes fields needed directly by later tasks:
- `hours_since_main64`
- `hours_to_main71`
- `Region_A_along_km`, `Region_A_across_km`, `in_Region_A`
- `Region_B_along_km`, `Region_B_across_km`, `in_Region_B`
- `dist_to_main64_km`, `dist_to_main71_km`
- `in_Mw64_neighborhood`, `in_Mw71_neighborhood`
- `in_corridor_overlap`
- `unassigned_to_corridors`

This means later rate, energy, and first-activation analyses can be performed consistently on the exact same fixed geometry without re-deriving region membership.

Evidence:
- `<PACKAGE_ROOT>/results/exp_run/outputs/01_region_geometry_assignment/tables/event_region_assignments.csv`

## Limitations and Assumptions

- The corridors are fixed, user-prescribed finite segments with a uniform 3 km half-width. They are intentionally not data-adaptive, so any real curvature, branching, or variable-width damage-zone structure is simplified.
- Region B appears more offset relative to its centerline than Region A, based on the across-centerline distribution and slightly larger 95th-percentile distance. This does not invalidate the corridor, but it means Region B geometry is somewhat less centered on the assigned cloud.
- Region B’s centerline is longer than the most densely occupied active segment, so later along-strike analyses must distinguish true delayed activation from inactive corridor sections that may simply reflect geometric overextension.
- A substantial overlap exists between the two corridors: 1239 events, or 26.06% of the catalog. This overlap is scientifically appropriate near the corridor intersection, but later comparative rate analyses must handle non-exclusive membership carefully to avoid double counting when comparing Region A and Region B directly.
- The diagnostic circles were implemented as 10 km-radius neighborhoods, consistent with the task specification. The user’s visualization bullet mentioned 5 km-radius circular boundaries, which is inconsistent with the main specification; the preserved metadata confirms 10 km neighborhoods were used.
- This task only establishes geometry and assignments. It does not yet provide evidence for synchronous versus delayed activation, seismic-rate change points, energy release evolution, or directional migration; those scientific questions remain for later tasks.
- No warnings or failures were recorded in the task handoff, and the task status was success according to `<PACKAGE_ROOT>/results/exp_run/log/coding_progress/task_handoff/01_region_geometry_assignment.json`.

## Report-Ready Summary

Task 01 successfully established the fixed spatial framework for the Ridgecrest triggering study using a local metric projection and two prescribed fault-oriented corridors plus two independent near-mainshock neighborhoods. The implemented geometry is fully documented in `<PACKAGE_ROOT>/results/exp_run/outputs/01_region_geometry_assignment/metadata/region_geometry_metadata.json`, and event-level assignments are preserved in `<PACKAGE_ROOT>/results/exp_run/outputs/01_region_geometry_assignment/tables/event_region_assignments.csv`.

The fixed-corridor map demonstrates that Region A and Region B capture the two main seismicity lineations and their central linkage zone between the Mw 6.4 and Mw 7.1 source regions (`<PACKAGE_ROOT>/results/exp_run/outputs/01_region_geometry_assignment/figures/fixed_corridor_assignment_map.png`). Quantitatively, Region A contains 2817 events (59.24% of the catalog), Region B contains 2876 events (60.48%), the corridor overlap contains 1239 events (26.06%), and only 6.33% of events are unassigned to both corridors (`<PACKAGE_ROOT>/results/exp_run/outputs/01_region_geometry_assignment/tables/region_assignment_summary.csv`).

Width diagnostics show that both 3 km half-width corridors are adequate: Region A has median and 95th-percentile absolute across-centerline distances of 0.858 and 2.404 km, and Region B has 1.028 and 2.676 km, respectively, indicating that most assigned events lie well inside the fixed bounds (`<PACKAGE_ROOT>/results/exp_run/outputs/01_region_geometry_assignment/figures/region_a_across_centerline_distribution.png`, `<PACKAGE_ROOT>/results/exp_run/outputs/01_region_geometry_assignment/figures/region_b_across_centerline_distribution.png`). Along-strike diagnostics show that Region A’s finite centerline closely matches the occupied event span, whereas Region B fully contains the intended trend but extends beyond the densest active segment (`<PACKAGE_ROOT>/results/exp_run/outputs/01_region_geometry_assignment/figures/region_a_along_strike_distribution.png`, `<PACKAGE_ROOT>/results/exp_run/outputs/01_region_geometry_assignment/figures/region_b_along_strike_distribution.png`).

Finally, the unassigned-event map indicates that omitted events are mostly diffuse peripheral seismicity rather than a missed coherent corridor through the key Mw 6.4-to-Mw 7.1 connection (`<PACKAGE_ROOT>/results/exp_run/outputs/01_region_geometry_assignment/figures/unassigned_event_diagnostic_map.png`). Overall, this task provides a defensible and reusable spatial basis for subsequent comparison of seismic-rate evolution, triggering delays, and internal activation ordering between the two fault-oriented regions.