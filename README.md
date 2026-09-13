<p align="center">
  <img src="docs/trace-logo.svg" alt="TRACE logo" width="420">
</p>

# TRACE Review Materials

This repository contains the review materials associated with the TRACE manuscript. It provides benchmark definitions, case-specific workflows, execution scripts, processing records, and manuscript-facing result products for inspection by reviewers and readers.

## Scientific Cases

### Ridgecrest earthquake sequence

The Ridgecrest case demonstrates an end-to-end earthquake-catalog workflow for the 2019 Ridgecrest sequence. The released materials cover:

- waveform preprocessing;
- PhaseNet phase picking;
- GaMMA phase association and initial event location;
- HypoDD relocation;
- spatiotemporal, fault-oriented, activation, migration, magnitude-frequency, and Omori-Utsu analyses.

The case is designed to show how the workflow constructs a relocated earthquake catalog and then uses that catalog to investigate the spatial and temporal organization of the sequence.

Materials are available under [`release/scientific_cases/ridgecrest/`](release/scientific_cases/ridgecrest/).

### Sanriku earthquake sequence

The Sanriku case demonstrates catalog construction and scientific analysis for the Sanriku region. The released construction materials cover:

- JMA catalog download and validation;
- travel-time and phase-arrival preparation;
- full-catalog HypoDD relocation;
- repeating-earthquake identification and waveform similarity analysis.

The catalog-analysis materials then examine sequence response, earthquake behavior, event relationships, background-rate correction, event chains, spatial-depth organization, focal-mechanism coverage, catalog statistics, and M1-M3 migration-related patterns. A scientific synthesis reference is included to connect the separate analysis stages with the manuscript-facing results.

The released Sanriku products include the validated relocation catalog with `25,646` events and the manuscript-aligned repeating-earthquake result set.

Materials are available under [`release/scientific_cases/sanriku/`](release/scientific_cases/sanriku/).

## Principal Software

| Software or algorithm | Main role | Released case use |
| --- | --- | --- |
| ObsPy | Waveform, station, time, and catalog processing | Ridgecrest and Sanriku |
| PhaseNet | Deep-learning P- and S-phase picking | Ridgecrest |
| GaMMA | Phase association and initial event location | Ridgecrest |
| HypoDD | Double-difference earthquake relocation | Ridgecrest and Sanriku |
| SeismoStats | Catalog statistics, completeness, and magnitude-frequency analysis | Ridgecrest and Sanriku |

The broader model inventory includes PhaseNet, PhaseNetLight, EQTransformer, OBSTransformer, GPD, BasicPhaseAE, DPPicker, Skynet, SeisT, SeisMoLLM, MagNet, DiTingMotion, BAZ-Network, DeepDenoiser, and SeisDAE. Their task categories, registered variants, public references, and implementation areas are listed in the [software and algorithm manifest](docs/software_and_algorithm_manifest.md).

## Benchmark

The benchmark evaluates whether an analysis agent can complete structured scientific tasks and produce reviewable outputs. It includes Level 1 and Level 2 task definitions, evaluation summaries, reviewable run records, and public benchmark utilities.

Manual-reference visualization scores are based on five expert ratings on a 1-5 scale. The corresponding task definitions and evaluation summaries are available under [`release/benchmark/`](release/benchmark/).

## Release Scope

This repository focuses on the materials needed to inspect the experimental design and reported results:

- benchmark task definitions and evaluation summaries;
- case-specific execution and analysis scripts;
- experiment plans and workflow descriptions;
- processing and validation records;
- machine-readable result tables and summary files;
- figures and other reviewable products supporting the released workflows.

The repository uses public placeholders for local data and software locations. Large source datasets and external software environments are referenced separately. A full summary of the scientific software and algorithmic components is provided in the [software and algorithm manifest](docs/software_and_algorithm_manifest.md).

## TRACE Framework Availability

This repository presents the case-specific workflows and manuscript-facing results associated with TRACE. The general-purpose TRACE agent framework and its internal `seismoagent` implementation will be released after completion of the peer-review process.

The related framework design can be referenced through the [EarthLink project](https://github.com/OpenEarthLab/EarthLink). Additional implementation details or private access can be provided for manuscript evaluation when required.

## Reproducibility

The public scripts document the analysis steps and parameters used for the released cases. Reproduction uses the corresponding scientific datasets, standard scientific Python packages, domain-specific tools, local data paths, and access permissions for external data services.

The released result tables and summary files define the manuscript-facing outputs. Supporting processing materials are included for workflow inspection and validation.

## Citation and License

Please cite the associated TRACE manuscript when using these materials. A permanent citation and repository version will be added with the formal publication release.

Licensing terms will be added with the formal public software release.
