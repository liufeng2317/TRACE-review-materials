## Scientific Purpose

This task converts the previously derived regional background and mainshock-context diagnostics into a ranked set of **testable candidate seismic patterns** and **follow-up analysis recommendations** for later sequence analysis. The aim is to identify which patterns are most likely to matter for aftershock/sequence interpretation in the Japan Aomori catalog, and to translate those findings into practical thresholds for spatial, temporal, depth, and mechanism-based analysis.

## Method and Implementation Evidence

The implementation appears to combine summary statistics from the background catalog and the mainshock-centered context snapshots, then rank candidate hypotheses by a priority score.

Evidence of this workflow is provided by:

- `"<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/06_candidate_patterns_estimation/background_summary_snapshot.csv"`
- `"<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/06_candidate_patterns_estimation/mainshock_context_snapshot.csv"`
- `"<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/06_candidate_patterns_estimation/candidate_patterns_ranked.csv"`
- `"<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/06_candidate_patterns_estimation/candidate_patterns_summary.csv"`
- `"<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/06_candidate_patterns_estimation/followup_analysis_suggestions.csv"`

The ranked output indicates that the approach uses:
- **mainshock-specific local context metrics** such as local density ratio, station count, mechanism-record count, and depth-domain flag;
- **catalog-wide pattern flags** such as focal-mechanism data gaps;
- **priority ranking** to separate the most actionable hypotheses from lower-priority background effects.

The two figures provide visual summaries of the ranking and of the mainshock context:
- `"<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/06_candidate_patterns_estimation/figure_candidate_patterns_ranked.png"`
- `"<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/06_candidate_patterns_estimation/figure_mainshock_context_overview.png"`

## Key Results and Evidence Files

### 1) Ranked candidate patterns identify mainshock-specific context as the strongest signal

The ranked catalog shows that the highest-priority candidates are the **mainshock local-context patterns** for M1 and M3, both with priority score 1.0.

From `candidate_patterns_ranked.csv`:
- `MS_M1`: local density ratio = **7.59**, stations = **6**, mechanism records = **0**, depth flag = **typical**
- `MS_M3`: local density ratio = **5.50**, stations = **5**, mechanism records = **4**, depth flag = **typical**
- `MS_M2`: local density ratio = **2.75**, stations = **6**, mechanism records = **57**, depth flag = **distinct**

Scientific interpretation:
- **M1 and M3** stand out as the most actionable sequence-analysis targets because they sit in strongly enriched local seismic environments relative to the regional median.
- **M2** is still important, but its local-enrichment signal is weaker than M1/M3 despite much better mechanism support.

Supporting files:
- `"<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/06_candidate_patterns_estimation/candidate_patterns_ranked.csv"`
- `"<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/06_candidate_patterns_estimation/figure_candidate_patterns_ranked.png"`

### 2) Mechanism-availability gap is a major catalog-wide limitation and a candidate pattern itself

The ranked output identifies a catalog-wide focal-mechanism gap:
- `P06`: mechanism geometry available for **39.3%** of mechanism records; core mechanisms for **39.3%**
- priority score ≈ **0.607**

Scientific interpretation:
- Focal-mechanism analysis must be treated as **sparse and incomplete**, and interpretation should distinguish between true physical patterns and simple data-availability bias.
- This is especially relevant because M1 and M3 have very few or no local mechanism records in the context snapshot.

Supporting files:
- `"<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/06_candidate_patterns_estimation/candidate_patterns_ranked.csv"`
- `"<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/06_candidate_patterns_estimation/followup_analysis_suggestions.csv"`

### 3) Mainshock context suggests a common spatial/depth window, but with event-specific differences

The `mainshock_context_snapshot.csv` shows that all three major earthquakes were evaluated with the same local window:
- local radius ≈ **44.31 km**
- local depth window ≈ **26.13 km**

Mainshock-specific context:
- **M1**: 6093 local events, density ratio **7.59**, local depth median **11.91 km**, mechanism records **0**
- **M2**: 2203 local events, density ratio **2.75**, local depth median **41.92 km**, mechanism records **57**
- **M3**: 4416 local events, density ratio **5.50**, local depth median **12.61 km**, mechanism records **4**

Scientific interpretation:
- All three mainshocks occur in locally dense seismic settings, but **M1 and M3 are much more enriched than M2**.
- **M2 is depth-distinct** relative to the background, with a much deeper local median depth than the other two events.
- The analysis therefore supports **shared regional thresholds** for first-pass sequence work, but also **event-specific depth stratification**, especially for M2.

Supporting files:
- `"<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/06_candidate_patterns_estimation/mainshock_context_snapshot.csv"`
- `"<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/06_candidate_patterns_estimation/figure_mainshock_context_overview.png"`

### 4) The background summary indicates a large, usable dataset for follow-up analysis

From `candidate_patterns_summary.csv`:
- catalog events: **21741**
- mainshock events: **3**
- station count: **371**
- mechanism records: **354**

Scientific interpretation:
- The catalog is large enough for robust regional background characterization and for mainshock-centered subsetting.
- However, the mechanism sample is modest relative to the earthquake catalog, consistent with the mechanism-data-gap pattern above.

Supporting file:
- `"<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/06_candidate_patterns_estimation/candidate_patterns_summary.csv"`

### 5) Follow-up analysis suggestions are already concretely thresholded

The follow-up suggestions emphasize:
- **space**: use spatial clusters and mainshock-centered windows
- **time**: use 30-day windows for rate diagnostics and flag bursts/quiet intervals
- **depth**: split analyses by empirical depth bins and mainshock depth domains

The mainshock-specific threshold suggestion repeats:
- use radius near **44 km**
- apply depth window near **±26 km**
- consider a **higher magnitude threshold** for coda/aftershock screening

Scientific interpretation:
- These recommendations are directly usable for later sequence-analysis design, and they encode the key idea that **one-size-fits-all thresholds are not optimal** for this region.

Supporting file:
- `"<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/06_candidate_patterns_estimation/followup_analysis_suggestions.csv"`

## Limitations and Assumptions

- `background_summary_snapshot.csv` is effectively empty in the delivered output directory: the file size is 1 byte and it could not be parsed as a table. This means the task’s final ranking likely relied on other inputs or in-memory values rather than a persistent background snapshot table.
- The ranked patterns are concise and highly actionable, but they are **screening-level hypotheses**, not formal statistical tests.
- The mainshock context metrics depend on the chosen local radius and depth window; the recommended thresholds are useful, but they should still be validated in sensitivity tests.
- Mechanism-based interpretation is limited by sparse coverage: the catalog-level mechanism availability is only partial, and M1/M3 in particular have weak local mechanism support.
- The figure-based interpretation is limited to what is visually encoded in the outputs; any deeper numeric uncertainty, confidence intervals, or model diagnostics are not exposed in the provided files.
- `candidate_patterns_ranked.csv` contains only a small set of patterns, so lower-ranked or subtle effects may not be represented.

## Report-Ready Summary

The candidate-pattern estimation task successfully distilled the regional background and mainshock context into a short list of **high-priority sequence-analysis hypotheses**. The strongest patterns are **mainshock-centered local seismicity enrichment**, especially for **M1** and **M3**, followed by a **catalog-wide focal-mechanism data gap** that should be explicitly handled in any later tectonic or source-property analysis. The outputs support using a **~44 km spatial window**, a **~26 km depth window**, and **event-specific depth stratification**—particularly for the deeper M2 event. The most important reusable evidence files are `candidate_patterns_ranked.csv`, `mainshock_context_snapshot.csv`, `followup_analysis_suggestions.csv`, and the two overview figures in `figure_candidate_patterns_ranked.png` and `figure_mainshock_context_overview.png`.