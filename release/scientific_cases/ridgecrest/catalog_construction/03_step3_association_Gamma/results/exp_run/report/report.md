# GaMMA Association and Initial Location

This release record documents the agent-generated GaMMA association and
initial-location stage for the Ridgecrest sequence.

## Production settings

- Window: `2019-07-04T00:00:00Z` through `2019-07-26T00:00:00Z` (22 daily
  windows).
- Phase picks: PhaseNet thresholds `P >= 0.4` and `S >= 0.4`.
- Stations: 30 core Ridgecrest stations.
- Association: GaMMA BGMM with DBSCAN `eps=10 km`, oversampling factor `3`,
  and no amplitude term.
- Event support: at least 5 picks per event.
- Search depth: `0-30 km`.
- Velocity model: the 11-layer gradual 1-D model with `Vp/Vs=1.73`.

## Agent-generated result

The stage produced the GaMMA catalog used as input to the relocation stage:

- associated events: `140,505`;
- picks assigned to associated events (manuscript summary): `2,120,090`
- paired phase rows retained in the release validation table: `1,343,624`;
- processed period: 22 daily windows.

The machine-readable run summary is
`../outputs/01_gamma_association_location_magnitude/run_summary.json`.
Selected validation tables and diagnostic figures are retained in the same
output directory.

The GaMMA catalog is an intermediate agent output. The final manuscript
catalog is the 84,474-event catalog in the Step 4 release, after the
agent-generated relocation output was checked and validated by experts.
