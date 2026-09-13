# Ridgecrest Case

This directory contains the public implementation materials for the TRACE
analysis of the 2019 Ridgecrest earthquake sequence.

## Directory layout

```text
ridgecrest/
├── README.md
├── data_manifest.json
├── catalog_construction/
│   ├── 01_step1_data_preprocessing_for_phasepicking/
│   │   ├── 01_step1_data_preprocessing_for_phasepicking.py
│   │   └── results/
│   ├── 02_step2_phase_picking_PhaseNet/
│   │   ├── 02_step2_phase_picking_PhaseNet.py
│   │   └── results/
│   ├── 03_step3_association_Gamma/
│   │   ├── 03_step3_association_Gamma.py
│   │   └── results/
│   ├── 04_step4_relocation_HypoDD/
│   │   ├── 04_step4_relocation_HypoDD.py
│   │   └── results/
└── catalog_analysis/
    ├── README.md
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

## Catalog generation

`catalog_construction/` contains the workflow materials for the final production
catalog route:

1. waveform preprocessing;
2. PhaseNet phase picking;
3. GaMMA phase association and initial location;
4. HypoDD relocation.

Each stage contains an entry script and its reviewable run record:

- `<stage>.py`: the public agent-invocation script. The task description is
  embedded in this script.
- `results/`: the public run record for the corresponding stage, including
  agent-generated implementation code, trajectories, reports, and result
  summaries.

The selected production configuration is:

- PhaseNet threshold `P >= 0.4`, `S >= 0.4`;
- 47 selected stations for waveform preprocessing, followed by a 30-station
  core subset for GaMMA association and HypoDD relocation;
- GaMMA `eps=10`, oversampling `=3`, amplitude-free association;
- gradual 1-D velocity model from 0 to 8 km;
- HypoDD `H24` route with `minlink=6`, `minobs=6`, `maxsep=8`,
  and `maxngh=20`;
- global corrected catalog version
  `data-current-p04s04-eps10-os3-core30-gradual-depthcorr`.

The manuscript-analysis Ridgecrest catalog contains 84,474 events. It is the
agent-generated relocation output after final expert validation and selection.
The public final catalog is
`catalog_construction/04_step4_relocation_HypoDD/results/exp_run/outputs/01_hypodd_relocation_analysis/relocated_events.csv`.
The native 84,475-event output is retained separately as
`relocated_events_unadjusted.csv` for audit.

## Catalog analysis

`catalog_analysis/` follows the original entry-script order and contains the
generated scripts and promoted run records for:

- spatiotemporal evolution;
- fault-oriented spatial analysis;
- activation and directional diagnostics;
- b-value analysis;
- Omori-Utsu and seismicity-rate diagnostics.

The analysis materials are separated from catalog generation so that the
catalog construction and scientific interpretation workflows can be reviewed
independently. The question number is local to each script family. The primary
`Q1` in the original `01_1` run sequence is the spatiotemporal analysis.

## Data and paths

The required data sources and expected input locations are listed in
`data_manifest.json`. Paths in scripts and summaries use placeholders such as
`<DATA_ROOT>`, `<CASE_ROOT>`, `<REPO_ROOT>`, `<ENV_ROOT>`, and `<OUTPUT_ROOT>`.
The promoted analysis directories retain generated scripts, trajectories,
reports, logs, tables, and figures.

Manuscript-facing catalog correction and reference-matching scripts are not
included here; the resulting final manuscript catalog is included as the
reviewable output.
