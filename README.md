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

Materials are available under [`release/cases/ridgecrest/`](release/cases/ridgecrest/).

### Sanriku earthquake sequence

The Sanriku case demonstrates catalog construction and scientific analysis for the Sanriku region. The released construction materials cover:

- JMA catalog download and validation;
- travel-time and phase-arrival preparation;
- full-catalog HypoDD relocation;
- repeating-earthquake identification and waveform similarity analysis.

The catalog-analysis materials then examine sequence response, earthquake behavior, event relationships, background-rate correction, event chains, spatial-depth organization, focal-mechanism coverage, catalog statistics, and M1-M3 migration-related patterns. A scientific synthesis reference is included to connect the separate analysis stages with the manuscript-facing results.

The released Sanriku products include the validated relocation catalog with `25,646` events and the manuscript-aligned repeating-earthquake result set.

Materials are available under [`release/cases/sanriku/`](release/cases/sanriku/).

## Benchmark

The benchmark evaluates whether an analysis agent can complete structured scientific tasks and produce reviewable outputs. It includes Level 1 and Level 2 task definitions, evaluation summaries, selected run records, and public benchmark utilities.

Manual-reference visualization scores are based on five expert ratings on a 1-5 scale. The corresponding task definitions and evaluation summaries are available under [`release/benchmark/`](release/benchmark/).

## Release Scope

This repository focuses on the materials needed to inspect the experimental design and reported results:

- benchmark task definitions and evaluation summaries;
- case-specific execution and analysis scripts;
- experiment plans and workflow descriptions;
- selected processing and validation records;
- machine-readable result tables and summary files;
- figures and other reviewable products where included.

Large source datasets and external software environments are not duplicated in this repository. Local data and software locations are represented by public placeholders where appropriate and must be supplied separately.

## TRACE Framework Availability

The general-purpose TRACE agent framework and its internal `seismoagent` implementation are not included in this pre-publication repository. The released materials document the case-specific workflows and provide the results needed for manuscript review, but they are not intended to be a standalone copy of the complete TRACE framework.

The related framework design can be referenced through the [EarthLink project](https://github.com/OpenEarthLab/EarthLink). The complete TRACE framework source code will be released after completion of the peer-review process. Additional implementation details or private access can be provided for manuscript evaluation when required.

## Reproducibility

The public scripts document the analysis steps and parameters used for the released cases. Reproducing the workflows may require the corresponding scientific datasets, standard scientific Python packages, domain-specific tools, local data paths, and access permissions for external data services.

The released result tables and summary files should be treated as the authoritative record of the manuscript-facing outputs. Intermediate materials are included only when they support workflow inspection or validation.

## Citation and License

Please cite the associated TRACE manuscript when using these materials. A permanent citation and repository version will be added when available.

No license is currently specified for this pre-publication repository. Licensing terms will be added with the formal public software release.
