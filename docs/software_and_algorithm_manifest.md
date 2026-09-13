# Software and Algorithm Manifest

This document records the principal software and algorithmic components associated with the TRACE workflows. It is intended to help reviewers identify the scientific methods, external packages, and framework-level extensions represented by the public materials.

The public review repository contains case-specific scripts and curated execution records. It does not redistribute the general TRACE framework, private deployment components, credentials, pretrained checkpoints, or local retrieval indexes. Component names below refer to public packages or to repository-relative modules in the broader TRACE library; they do not expose local deployment paths.

## Components used by the released case studies

| Component | Role in the workflow | Released use | Public source or reference | Implementation note |
| --- | --- | --- | --- | --- |
| ObsPy | Seismic waveform and metadata I/O, UTC time handling, preprocessing, instrument-response support, and catalog utilities | Ridgecrest catalog construction; Sanriku catalog preparation and waveform analysis; benchmark tasks | [ObsPy](https://github.com/obspy/obspy) | Public case scripts use standard ObsPy interfaces |
| PhaseNet | Deep-learning P- and S-phase picking | Ridgecrest waveform-to-pick workflow; benchmark phase-picking tasks | [PhaseNet reference](https://doi.org/10.1093/gji/ggy423) | Model inference is accessed through the TRACE phase-picking module in the full framework |
| GaMMA | Gaussian-mixture-model phase association and initial event location | Ridgecrest catalog construction | [GaMMA](https://github.com/wayneweiqiang/GaMMA) | The released workflow records association parameters and downstream products |
| HypoDD | Double-difference earthquake relocation | Ridgecrest and Sanriku catalog construction | [HypoDD reference](https://doi.org/10.1785/0120000006) | Native HypoDD execution is wrapped by the TRACE relocation workflow |
| SeismoStats | Statistical earthquake-catalog analysis, including completeness and magnitude-frequency calculations | Ridgecrest and Sanriku catalog analysis; benchmark catalog-statistics tasks | [SeismoStats](https://github.com/swiss-seismological-service/SeismoStats) | Case scripts retain the relevant analysis parameters and result tables |
| SciPy | Numerical computation, optimization, statistics, and signal correlation | Ridgecrest and Sanriku analysis and validation scripts | [SciPy](https://github.com/scipy/scipy) | Includes correlation and numerical/statistical routines used by released scripts |
| scikit-learn | Clustering and dimensionality-reduction utilities | Supporting catalog-analysis and diagnostic workflows | [scikit-learn](https://github.com/scikit-learn/scikit-learn) | Used where clustering or feature-space diagnostics are required |
| NumPy and pandas | Array operations, tabular processing, filtering, and result-table generation | All released case studies and benchmark utilities | [NumPy](https://github.com/numpy/numpy); [pandas](https://github.com/pandas-dev/pandas) | General scientific Python dependencies |
| Matplotlib | Scientific figure generation | All released case studies and benchmark utilities | [Matplotlib](https://github.com/matplotlib/matplotlib) | Figure scripts write manuscript-facing plots and diagnostics |
| pyproj | Geographic coordinate transformation and local metric projection | Ridgecrest spatial analysis and related geospatial diagnostics | [pyproj](https://github.com/pyproj4/pyproj) | Used for distance-aware spatial calculations |

## Components used by benchmark or supporting workflows

| Component | Capability | Public use in this repository | Public source or reference | Status |
| --- | --- | --- | --- | --- |
| SeisBench | Unified access to seismological machine-learning models and datasets | Benchmark phase-picking and model-oriented tasks; framework support | [SeisBench](https://github.com/seisbench/seisbench) | Supporting benchmark/framework component |
| DASPy | Distributed Acoustic Sensing data processing, filtering, decomposition, and visualization | DAS-related benchmark tasks | [DASPy](https://github.com/HMZ-03/DASPy); [Hu and Li, 2024](https://doi.org/10.1785/0220240124) | Supporting benchmark component |
| requests | HTTP data and metadata retrieval | Case data-access scripts and benchmark download tasks | [Requests](https://github.com/psf/requests) | Infrastructure dependency rather than a scientific algorithm |
| PyYAML | Configuration-file parsing | Workflow configuration and benchmark utilities | [PyYAML](https://github.com/yaml/pyyaml) | Configuration dependency |
| joblib | Parallel and cached computation support | Selected analysis and benchmark utilities | [joblib](https://github.com/joblib/joblib) | Supporting computation dependency |
| statsmodels | Statistical smoothing and related diagnostics | Selected catalog-analysis diagnostics | [statsmodels](https://github.com/statsmodels/statsmodels) | Supporting statistical dependency |
| Shapely | Geometric objects and spatial operations | Selected spatial-analysis and plotting utilities | [Shapely](https://github.com/shapely/shapely) | Supporting geospatial dependency |
| segyio | SEG-Y seismic data input and output | Available for seismic-format benchmark/library workflows | [segyio](https://github.com/equinor/segyio) | Not a primary dependency of the released Ridgecrest or Sanriku results |

## AI model inventory

The `ai_module` library is organized by scientific task rather than as one
single model. The tables below list the registered model families and named
pretrained variants found in the broader TRACE library. Variant names identify
the model registry entries and their associated training-data domains; model
checkpoint files and local storage paths are not included in this review
repository.

### Phase picking

| Model family | Model form and output | Registered pretrained variants | Repository-relative implementation | Public source or reference |
| --- | --- | --- | --- | --- |
| PhaseNet | U-Net-style convolutional model producing noise, P-phase, and S-phase probability sequences | `instance`, `jma`, `jma_wc`, `volpick`, `scedc`, `stead`, `diting`, `ethz`, `geofon`, `lendb`, `phasenet_sn`, `iquique`, `neic`, `obs`, `original`, `pisdl` | `ai_module/phase_picking/model/phasenet.py` | [Zhu and Beroza, 2019](https://doi.org/10.1093/gji/ggy423); [SeisBench](https://github.com/seisbench/seisbench) |
| PhaseNetLight | Reduced PhaseNet-compatible convolutional model for efficient P/S picking | `phasenetlight_instance`, `phasenetlight_neic`, `phasenetlight_lendb`, `phasenetlight_scedc`, `phasenetlight_stead`, `phasenetlight_ethz`, `phasenetlight_geofon`, `phasenetlight_iquique`, `phasenetlight_obs` | `ai_module/phase_picking/model/phasenetlight.py` | [Zhu and Beroza, 2019](https://doi.org/10.1093/gji/ggy423); [SeisBench](https://github.com/seisbench/seisbench) |
| EQTransformer | Attentive deep-learning model with detection, P-phase, and S-phase outputs | `instance`, `original`, `volpick`, `scedc`, `stead`, `ethz`, `geofon`, `lendb`, `iquique`, `neic`, `obs`, `original_nonconservative` | `ai_module/phase_picking/model/eqtransformer.py` | [Mousavi et al., 2020](https://doi.org/10.1038/s41467-020-17591-w); [EQTransformer](https://github.com/smousavi05/EQTransformer) |
| OBSTransformer | EQTransformer-derived model adapted for ocean-bottom seismic data and P/S/noise classification | `obst2024` | `ai_module/phase_picking/model/obstransformer.py` | [Niksejel and Zhang, 2024](https://doi.org/10.1093/gji/ggae049) |
| GPD | Point-prediction generalized phase detector | `gpd_neic`, `gpd_instance`, `gpd_lendb`, `gpd_scedc`, `gpd_geofon`, `gpd_iquique`, `gpd_stead`, `gpd_dummy`, `gpd_ethz`, `gpd_original` | `ai_module/phase_picking/model/gpd.py` | [Generalized Phase Detection](https://arxiv.org/abs/1805.01075); [SeisBench](https://github.com/seisbench/seisbench) |
| BasicPhaseAE | Convolutional autoencoder-style phase classifier producing noise, P-phase, and S-phase sequences | `BasicPhaseAE_NEIC`, `BasicPhaseAE_INSTANCE`, `BasicPhaseAE_LenDB`, `BasicPhaseAE_SCEDC`, `BasicPhaseAE_GEOFON`, `BasicPhaseAE_Iquique`, `BasicPhaseAE_STEAD`, `BasicPhaseAE_ETHZ` | `ai_module/phase_picking/model/basicphaseae.py` | [SeisBench](https://github.com/seisbench/seisbench) |
| DPPickerp | Bidirectional-LSTM phase picker configured for P-phase inference | `dppickerp_neic`, `dppickerp_instance`, `dppickerp_scedc`, `dppickerp_geofon`, `dppickerp_iquique`, `dppickerp_stead`, `dppickerp_ethz` | `ai_module/phase_picking/model/dpppickerp.py` | [SeisBench](https://github.com/seisbench/seisbench) |
| DPPickers | Bidirectional-LSTM phase picker configured for S-phase inference | `dppickers_neic`, `dppickers_instance`, `dppickers_scedc`, `dppickers_iquique`, `dppickers_stead`, `dppickers_ethz` | `ai_module/phase_picking/model/dpppickers.py` | [SeisBench](https://github.com/seisbench/seisbench) |
| Skynet | Long-receptive-field U-Net model for regional and multiphase picking | `Original Skynet`, `Multiphase Skynet` | `ai_module/phase_picking/model/skynet.py` | [Aguilar Suarez and Beroza, 2025](https://doi.org/10.26443/seismica.v4i1.1431) |

The phase-picking implementation also exposes `VariableLengthPhaseNet` as a
code-level class for flexible input lengths. It is not a separate pretrained
registry entry in the current model list.

### Other waveform and source-parameter tasks

| Scientific task | Model families | Registered pretrained variants | Output or task-specific behavior | Repository-relative implementation | Public source or reference |
| --- | --- | --- | --- | --- | --- |
| Advanced phase picking | `SeisT-S`, `SeisT-M`, `SeisT-L`, `SeisMoLLM` | `seist_s`: DiTing_light; `seist_m`: DiTing_light; `seist_l`: STEAD, DiTing_light; `seismollm`: STEAD, DiTing_light | Joint event detection and P/S phase probability sequences | `ai_module/advanced_phase_picking` | [SeisT](https://ieeexplore.ieee.org/document/10453976); [SeisMoLLM](https://arxiv.org/abs/2502.19960) |
| Back-azimuth estimation | `SeisT-L`, `SeisMoLLM`, `BAZ_Network` | Each family provides STEAD and DiTing_light variants | Direct angle output for SeisT-L; cosine/sine output followed by angular conversion for the other two families | `ai_module/back_azimuth_estimation` | [Mousavi and Beroza, 2020](https://doi.org/10.1109/TGRS.2020.2988770); [SeisT](https://ieeexplore.ieee.org/document/10453976); [SeisMoLLM](https://arxiv.org/abs/2502.19960) |
| Epicentral-distance estimation | `SeisT-S`, `SeisT-M`, `SeisT-L`, `SeisMoLLM` | `seist_s`: DiTing_light; `seist_m`: DiTing_light; `seist_l`: STEAD, DiTing_light; `seismollm`: STEAD, DiTing_light | Scalar source-receiver distance prediction in kilometers | `ai_module/epicentral_distance_estimation` | [SeisT](https://ieeexplore.ieee.org/document/10453976); [SeisMoLLM](https://arxiv.org/abs/2502.19960) |
| First-motion polarity classification | `DiTingMotion`, `SeisT-L`, `SeisMoLLM` | Each family provides a DiTing_light variant | Two-class polarity output; DiTingMotion also returns clarity classification | `ai_module/first_motion_polarity_classification` | [DiTingMotion](https://doi.org/10.3389/feart.2023.1103914); [SeisT](https://ieeexplore.ieee.org/document/10453976); [SeisMoLLM](https://arxiv.org/abs/2502.19960) |
| Magnitude estimation | `SeisT-S`, `SeisT-M`, `SeisT-L`, `SeisMoLLM`, `MagNet` | `seist_s`: `pnw`, `seist_s_diting_light`; `seist_m`: `pnw`, `diting_light`; `seist_l`: `stead`, `diting_light`; `seismollm`: `stead`, `diting_light`; `MagNet`: `stead`, `diting_light` | Local magnitude (`ML`) prediction from waveform input | `ai_module/magnitude_estimation` | [MagNet](https://doi.org/10.1029/2019GL085976); [SeisT](https://ieeexplore.ieee.org/document/10453976); [SeisMoLLM](https://arxiv.org/abs/2502.19960) |
| Waveform denoising | `DeepDenoiser`, `SeisDAE` | `DeepDenoiser`: `original`, `urban`; `SeisDAE`: `stead_highsnr` | STFT-domain mask prediction and inverse-STFT reconstruction of denoised waveforms | `ai_module/denoise` | [DeepDenoiser](https://doi.org/10.1109/TGRS.2019.2926772); [SeisDAE](https://doi.org/10.1007/s10950-022-10097-6) |

## Additional components in the broader TRACE library

The following components are present in the broader `library` used by TRACE and document additional seismological capabilities. They are listed to make the scope of the software library explicit; their presence does not imply that every component contributes to the reported Ridgecrest or Sanriku results.

| Component or module | Algorithmic capability | Repository-relative implementation area | Status for this review release |
| --- | --- | --- | --- |
| `PALM` | STA/LTA- and kurtosis-based phase picking, P/S pick association, and initial event location | `basic_fun/PALM` | Framework extension |
| `PAL_HypoDD` | Conversion of PAL outputs and execution support for HypoDD relocation | `basic_fun/PALM/PAL_HypoDD` | Framework relocation wrapper; the released cases expose their case-specific scripts and records |
| `hypodd_runner` | Input validation, phase/station conversion, catalog-only relocation, time-window planning, native-output collection, and result accounting | `basic_fun/HypoDD/hypodd_runner` | Framework relocation runner used by the Sanriku case workflow |
| `Nonlinlocpy` | Preparation and execution helpers for NonLinLoc absolute location workflows, including velocity grids and solution parsing | `basic_fun/Nonlinlocpy` | Framework extension |
| `EQcorrscan` | Matched-filter detection, waveform cross-correlation, template analysis, and repeating-event utilities | `basic_fun/EQcorrscan` | Framework extension; the released Sanriku repeating-event scripts document their direct correlation workflow |
| `ETAS` | Epidemic-Type Aftershock Sequence modeling, completeness estimation, and seismicity simulation | `basic_fun/etas` | Framework extension |
| `bruces` | Catalog declustering and seismicity-rate analysis | `basic_fun/bruces` | Framework extension |
| `SKHASH` | Focal-mechanism inversion from first-motion polarities and S/P amplitude ratios | `basic_fun/SKHASH` | Framework extension |
| `hashpy` | HASH-related focal-mechanism utilities and polarity/amplitude-ratio support | `basic_fun/hashpy` | Framework extension |
| `Pyrocko` | Seismological data processing, waveform utilities, modeling, and geophysical computation | `basic_fun/pyrocko` | Framework extension |
| `qseek` | Data-driven earthquake detection and localization using neural phase annotations, stacking/migration, and adaptive search | `basic_fun/qseek` | Framework extension |
| MCP seismology modules | Tool interfaces for selected scientific tasks, including group- and phase-dispersion forward calculations | `MCP_Seismology` | Framework component; not required to interpret the released case outputs |

## Version and citation practice

The public case directories retain task-level parameters, workflow descriptions, and result metadata. Package versions, model checkpoint revisions, and source revisions should be fixed in the computational-environment record associated with the formal release tag. External software and model families should be cited using the public links or references in the tables above, together with the associated TRACE manuscript.

Internal retrieval databases, cached documentation, and deployment-specific agent infrastructure are not scientific analysis dependencies and are therefore not enumerated as case methods.
