# HypoDD Relocation and Final Ridgecrest Catalog

This release record documents the agent-generated HypoDD relocation route and
the final catalog used in the manuscript.

## Production settings

- Window: `2019-07-04T00:00:00Z` through `2019-07-26T00:00:00Z` (22 daily
  batches).
- Input catalog: `140,505` GaMMA-associated events.
- Station subset: 30 core Ridgecrest stations.
- `ph2dt`: `MAXDIST=80`, `MAXSEP=8`, `MAXNGH=20`, `MINLNK=6`,
  `MINOBS=6`, `MAXOBS=40`.
- HypoDD: catalog `P+S` differential times, `IDAT=2`, `IPHA=3`, `DIST=80`,
  LSQR, and two weighting/damping stages with damping `120` and `80`.
- Velocity model: the same gradual 11-layer 1-D model used by GaMMA, with
  `Vp/Vs=1.73`.

## Results

The native agent-generated relocation output contains `84,475` events. After
the final agent-plus-expert validation and selection used by the manuscript,
the public final catalog contains `84,474` events. The selected events span
`2019-07-04T00:56:37.590Z` to `2019-07-25T23:59:29.320Z`.

The public files are:

- `../outputs/01_hypodd_relocation_analysis/relocated_events.csv`: final
  manuscript-analysis catalog (`84,474` events);
- `../outputs/01_hypodd_relocation_analysis/relocated_events_unadjusted.csv`:
  native agent output retained for audit (`84,475` events);
- `../outputs/01_hypodd_relocation_analysis/manuscript_catalog_summary.json`:
  final selection and daily counts;
- `../outputs/01_hypodd_relocation_analysis/relocation_statistics.json`:
  machine-readable relocation summary.

The final catalog is the result reported in the manuscript. The unadjusted
file is retained only to make the agent execution auditable and should not be
confused with the manuscript-analysis catalog.
