# Ridgecrest Catalog Analysis

The analysis release follows the order of the original entry scripts. Each
question directory contains the corresponding entry script at its root and
the preserved run package under `results/`.

```text
catalog_analysis/
├── 01_1_spatiotemporal_Q1/
├── 01_1_spatiotemporal_Q2/
├── 01_1_spatiotemporal_Q3/
├── 01_2_spatiotemporal_fault_Q1/
├── 01_2_spatiotemporal_fault_Q2/
├── 01_2_spatiotemporal_fault_Q3/
├── 01_3_spatiotemporal_quantify_Q1/
├── 01_3_spatiotemporal_quantify_Q2/
├── 01_4_b_value_Q0/
├── 01_4_b_value_Q1/
├── 01_4_b_value_Q2/
└── 01_5_Omori_Utsu_Q1/
```

The directory names retain the original numeric order and analysis names from
the entry scripts, with only the execution marker `trigger_` omitted. For
example, `01_1_trigger_spatiotemporal_Q1.py` is released under
`01_1_spatiotemporal_Q1/`.

The release includes scripts, plans, trajectories, reports, logs, and
reviewable result tables and figures for each promoted run. Public
placeholders such as `<REPO_ROOT>`, `<DATA_ROOT>`, `<ENV_ROOT>`, and
`<INTERNAL_ENDPOINT>` are used for environment-specific locations. Report
links use paths relative to the corresponding package so that local figures
and tables remain browsable in the release.
