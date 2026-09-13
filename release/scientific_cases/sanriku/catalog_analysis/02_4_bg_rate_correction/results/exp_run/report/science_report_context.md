<science_report_context>

## Scientific Objective
<user_request>
You are an earthquake scientist and data-analysis agent.

Current task:
Build a regional background-rate model for the Aomori earthquake catalog.

Goal:
Use the long-term raw JMA/Hi-net catalog as the background-rate reference and the relocated/filtered active-period catalog as the fine-scale active-period dataset. Determine whether the 2025-2026 Aomori activity is exceptional relative to long-term background seismicity, and identify which regions, depth ranges, and time periods show significant rate anomalies.

Data folder:
"<CASE_ROOT>/data"

Catalogs:
- Long-term raw catalog:
  data/Snet_catalog_20200101_20260522_filter.csv
  time range: 2020-01-01 to 2026-05-22
  role: long-term background-rate reference

- Active-period relocated/filtered catalog:
  data/Snet_catalog_20251001_20260501_filter.csv
  time range: 2025-10-01 to 2026-05-01
  role: fine-scale active-period spatial, depth, and regional rate analysis

Context files:
- catalog/main_earthquake.csv
- source_mechanism/Snet_mecha.csv
- stations/station.sta

Important data rule:
Do not merge the long-term raw catalog and the active-period relocated catalog as homogeneous products.
Because the long-term catalog has broader spatial coverage, define a common analysis region from the active-period relocated catalog, with a small buffer if needed, and filter the long-term catalog to this same spatial mask before any long-term vs active-period rate comparison.
Full-region long-term statistics may be reported only as supplementary context, not as the primary basis for anomaly claims.

Main tasks:

1. Catalog crosswalk and common-region definition
Compare the two catalogs over their overlapping period and define the common analysis region.

Check:
- schema and field meanings
- spatial coverage and common spatial mask
- magnitude range and magnitude type
- depth range
- event counts by magnitude threshold
- M4+ and M5+ event matching where feasible
- magnitude, location, and depth differences
- event retention rate from raw catalog to relocated/filtered catalog
- completeness magnitude Mc by catalog and period where feasible

Clearly state which magnitude thresholds are reliable for long-term comparison.
Prioritize M>=3, M>=4, and M>=5 for cross-catalog background-rate analysis.
Use M>=1.2 only within the active-period relocated catalog unless completeness is explicitly justified.

2. Long-term background-rate reference
Using the spatially filtered 2020-2026 raw catalog, estimate long-term seismicity rates for:
- common analysis region
- M1-M3 local region
- M2 local region
- M2 outer-band region
- broader control regions

Use magnitude thresholds where feasible:
- M>=3, M>=4, M>=5, M>=6, and M>=Mc if reliable

Compute:
- monthly or rolling-window rates
- percentile ranking of the 2025-10 to 2026-05 active period
- expected background counts for comparable windows
- long-term anomaly levels for M4+, M5+, and M6+ activity

3. Active-period regional rate decomposition
Using the 2025-10 to 2026-05 relocated/filtered catalog, analyze short-term rate changes within:
- M1-M3 local region
- M2 near-field region
- M2 outer-band region
- broader background/control region

Use multiple time scales where feasible:
- daily, weekly, 14-day, monthly

Use magnitude thresholds:
- M>=1.2, M>=2, M>=3, M>=4, M>=5

Also analyze depth-stratified rates:
- 0-30 km, 30-60 km, >60 km

Mark M1, M2, and M3 times on relevant rate plots.

4. Background-rate interpretation and controls
Evaluate:
- whether the 2025-2026 active period is anomalous relative to the 2020-2026 background within the common analysis region
- whether anomalies are regional or localized
- whether the M1-M3 local region remains unusual after regional background correction
- whether M2 outer-band activity exceeds regional background expectations
- whether the three mainshock regions are synchronized within a common regional rate pulse
- whether any apparent local anomaly can be explained by burst-like background seismicity or analysis-window choices

Use simple controls where useful:
- random windows from the long-term catalog
- same-duration windows outside mainshock intervals
- shifted windows within the active period
- spatial control regions
- bootstrap confidence intervals for rate anomalies

Figures:
Generate a compact set of high-value diagnostic figures, not exhaustive plots:
- long-term regional rate time series with the active period highlighted
- active-period rate time series with M1/M2/M3 marked
- regional rate comparison among M1-M3 local, M2 near-field, M2 outer-band, and control regions
- spatial rate-anomaly map
- depth-stratified rate evolution
- long-term percentile comparison for active-period windows
- background-rate evidence matrix

Final report:
Provide a concise scientific report answering:
- Is the 2025-2026 Aomori active period exceptional relative to the 2020-2026 background within the common analysis region?
- Which regions and depth ranges show the strongest rate anomalies?
- Are the anomalies localized or part of a broader regional rate pulse?
- Does the M1-M3 local region remain anomalous after background correction?
- Can M2 outer-band activity be explained by regional background-rate changes?
- Which observations remain statistically interesting enough for later physical follow-up?

Important:
Do not treat rate anomalies as proof of triggering, slow slip, fluid migration, stress transfer, or fault interaction.
Separate long-term background anomalies from active-period rate pulses.
Separate catalog-level statistical support from physical mechanism interpretation.
Use long-term raw catalog results as background-rate reference, not as fine-scale relocated structural evidence.
</user_request>

## Planned Workflow
<experiment_plan>
# Goal
Build a regional background-rate model for the Aomori earthquake catalogs by using the 2020-01-01 to 2026-05-22 long-term raw catalog as the background-rate reference and the 2025-10-01 to 2026-05-01 relocated/filtered catalog as the fine-scale active-period dataset, while keeping the two catalogs separate, filtering the long-term catalog to a common region defined from the relocated catalog, and determining whether the 2025-2026 activity is exceptional relative to long-term background seismicity by region, depth range, and time window.

## Planning Assumptions
- Use observation catalogs only; no synthetic or model-generated seismicity data are needed.
- The primary long-term reference is `data/Snet_catalog_20200101_20260522_filter.csv`.
- The primary active-period catalog is `data/Snet_catalog_20251001_20260501_filter.csv`; if that file is absent and the available relocated counterpart is `catalog/Snet_catalog_relocate_250930_260501.csv`, document the substitution explicitly before analysis and preserve catalog identity in all outputs.
- The long-term raw catalog and the active-period relocated catalog must not be merged into a single homogeneous event list.
- All primary long-term-versus-active-period anomaly claims must use the long-term raw catalog after filtering to a common spatial mask derived from the active-period relocated catalog, with only a small documented buffer if needed.
- Full-region long-term statistics outside the common mask may be reported only as supplementary context.
- Expected shared core fields are `datetime, lat, lon, dep, mag`; timestamp formats may differ and must be normalized before overlap tests and rate calculations.
- Cross-catalog comparisons should prioritize thresholds `M>=3`, `M>=4`, and `M>=5`; `M>=6` is descriptive unless counts support stronger inference. `M>=1.2` is restricted to the active-period relocated catalog unless completeness is explicitly justified for the long-term filtered catalog in the same region.
- Completeness magnitude `Mc` must be estimated separately by catalog and relevant subset where feasible; threshold reliability must be stated explicitly before anomaly testing.
- `catalog/main_earthquake.csv` provides the M1/M2/M3 anchors for region definition and plot/event-window marking.
- `source_mechanism/Snet_mecha.csv` and `stations/station.sta` are contextual datasets for mapping and interpretation checks only, not primary rate-estimation inputs.
- Use one primary cohesive task script for catalog audit, region construction, long-term baseline estimation, active-period decomposition, anomaly testing, and figure/table generation; only add a second script if bootstrap/control resampling is large enough to be operationally independent and it consumes validated intermediate tables.

## Analysis Plan

### Task 1: Catalog audit, crosswalk, and fixed analysis-region construction
- Task description
  - Standardize the two catalogs, compare them over the overlapping period, define the common analysis region from the active-period relocated catalog, and fix all named subregions before anomaly testing.
- Required data sources
  - `data/Snet_catalog_20200101_20260522_filter.csv`
  - `data/Snet_catalog_20251001_20260501_filter.csv` or documented substitute `catalog/Snet_catalog_relocate_250930_260501.csv`
  - `catalog/main_earthquake.csv`
  - `stations/station.sta`
- Parameter selection strategy
  - Parse `datetime` into one normalized time standard and coerce `lat`, `lon`, `dep`, and `mag` to numeric fields with explicit invalid-row handling.
  - Confirm schema meaning, units, missing values, duplicates, and valid ranges for magnitude and depth.
  - Define the common analysis region from the active-period relocated catalog footprint using a compact polygon-based mask if event geometry is irregular; otherwise use a bounding box. Add only a small documented buffer sufficient to retain edge events without importing large inactive raw-catalog areas.
  - Record the final region geometry explicitly and compute retained-event fractions for both catalogs.
  - Define fixed named subregions inside the common mask:
    - M1-M3 local region,
    - M2 near-field region,
    - M2 outer-band region excluding the near-field core,
    - one or more broader control regions outside the main localized clusters.
  - Choose radii/polygon limits from relocated-catalog event-density structure and M1/M2/M3 geometry, then freeze them before any anomaly significance calculations.
  - Restrict overlap crosswalks to the shared active-period time span and the common spatial mask.
  - Compute event counts by threshold `M>=1.2`, `M>=2`, `M>=3`, `M>=4`, `M>=5`, `M>=6`.
  - Match `M4+` and `M5+` events where feasible using a documented hierarchy: nearest in time first, then spatial distance, then magnitude/depth consistency; report ambiguous and unmatched cases separately.
  - Estimate `Mc` separately for:
    - long-term raw catalog in the common region,
    - active-period relocated catalog in the common region,
    - overlap subsets if sample size permits,
    - key named subregions only if event counts are adequate.
- Constraints
  - Do not use the broader long-term raw-catalog footprint as the primary anomaly domain.
  - Do not force one-to-one matching for the small-event catalogs.
  - Do not assume low-magnitude comparability across catalogs without `Mc` support.
  - Region definitions must not be tuned after looking at anomaly significance.
- Key outputs
  - Harmonized catalog QA table with schema, ranges, counts, duplicates, and null handling.
  - Common-region definition table with explicit geometry and buffer.
  - Region-definition table for M1-M3 local, M2 near-field, M2 outer-band, and control regions.
  - Overlap crosswalk table with event counts by threshold, retention rates, and matched-event residual summaries for `M4+` and `M5+`.
  - `Mc` summary table and a threshold-reliability decision table stating which thresholds are suitable for long-term comparison.
  - Diagnostic figures:
    - footprint comparison with common mask, named regions, mainshocks, and stations,
    - overlap count comparison by threshold,
    - magnitude-frequency and depth-distribution comparisons,
    - matched-event difference plots.

### Task 2: Long-term background-rate reference within the common region and controls
- Task description
  - Use the spatially filtered 2020-2026 raw catalog to estimate baseline seismicity rates and empirical null distributions for the common region and the fixed subregions.
- Required data sources
  - Spatially filtered subset of `data/Snet_catalog_20200101_20260522_filter.csv`
  - Region definitions from Task 1
  - `catalog/main_earthquake.csv`
- Parameter selection strategy
  - Compute long-term rates for:
    - common analysis region,
    - M1-M3 local region,
    - M2 near-field region,
    - M2 outer-band region,
    - broader control region(s),
    - optional supplementary full raw-catalog region kept separate from primary inference.
  - Use primary thresholds `M>=3`, `M>=4`, `M>=5`; add `M>=6` and `M>=Mc` only where counts and completeness support it.
  - Compute:
    - monthly non-overlapping counts and rates across 2020-2026,
    - rolling or sliding 7-day, 14-day, 30-day, and full-active-period-duration windows where counts are adequate,
    - expected background counts for active-period-comparable windows,
    - empirical percentile rank of the 2025-10 to 2026-05 window,
    - observed/expected ratios, excess counts, and count uncertainty intervals.
  - For sparse high-magnitude thresholds, rely on empirical window-count distributions and exact-count summaries rather than only smoothed rates.
  - If nonstationarity is visible across 2020-2026, add stratified controls such as same-calendar-month windows or year-stratified window comparisons and report whether anomaly claims depend on baseline choice.
- Constraints
  - All primary anomaly baselines must use the long-term raw catalog filtered to the common region or subregions inside it.
  - Full-region statistics outside the common mask must remain supplementary.
  - If counts are too sparse in a region-threshold combination, downgrade to descriptive rarity reporting instead of formal significance claims.
- Key outputs
  - Long-term background-rate table by region, threshold, and window length.
  - Active-period expected-versus-observed table for matched-duration windows.
  - Percentile/exceedance summary for the 2025-10 to 2026-05 interval and shorter subwindows.
  - Figures:
    - long-term common-region rate time series with the active period highlighted,
    - percentile comparison for active-period windows,
    - region-by-threshold baseline comparison panel,
    - supplementary full-region-versus-common-region context plot.

### Task 3: Active-period regional, temporal, and depth-stratified decomposition
- Task description
  - Use the relocated/filtered active-period catalog to resolve short-term rate evolution by region, threshold, and depth, and to identify whether activity is localized or part of a broader regional pulse.
- Required data sources
  - `data/Snet_catalog_20251001_20260501_filter.csv` or documented substitute `catalog/Snet_catalog_relocate_250930_260501.csv`
  - Region definitions from Task 1
  - `catalog/main_earthquake.csv`
  - `source_mechanism/Snet_mecha.csv`
- Parameter selection strategy
  - Restrict primary active-period analyses to the common region and the fixed named subregions.
  - Compute rates and cumulative counts at:
    - daily,
    - weekly,
    - 14-day rolling,
    - monthly scales.
  - Use thresholds:
    - `M>=1.2`, `M>=2`, `M>=3`, `M>=4`, `M>=5`.
  - Stratify by depth bins:
    - `0-30 km`,
    - `30-60 km`,
    - `>60 km`.
  - Mark M1, M2, and M3 origin times on all key temporal products.
  - For each region-threshold-depth combination, compute:
    - counts,
    - rates,
    - cumulative counts,
    - share of total active-period seismicity,
    - local-to-common-region or local-to-control normalized rate ratios where informative.
  - Use focal mechanism data only as optional context for notable moderate-to-large events in anomalous windows or sectors.
- Constraints
  - Fine-scale spatial and depth interpretations must use the active-period relocated catalog only.
  - `M>=1.2` remains active-period-only unless Task 1 completeness testing explicitly supports broader use.
  - Near-field and outer-band regions must remain non-overlapping.
  - Low-count bins must be flagged as unstable rather than over-interpreted.
- Key outputs
  - Active-period rate tables by region, threshold, depth bin, and timescale.
  - Burst chronology relative to M1/M2/M3.
  - Regional comparison tables for M1-M3 local, M2 near-field, M2 outer-band, and control areas.
  - Figures:
    - active-period rate time series with M1/M2/M3 markers,
    - regional comparison panel among target regions,
    - depth-stratified rate evolution,
    - cumulative-count summaries for selected thresholds.

### Task 4: Background-corrected anomaly tests, controls, and decision-ready synthesis
- Task description
  - Test whether the active-period patterns exceed long-term expectations, determine whether anomalies remain after regional correction, and summarize which findings are robust enough for later physical follow-up.
- Required data sources
  - Outputs from Tasks 1-3
  - Long-term filtered raw catalog
  - Active-period relocated catalog
  - `catalog/main_earthquake.csv`
- Parameter selection strategy
  - For each region, threshold, and key depth bin, compare active-period observations against long-term matched-duration background distributions.
  - Apply simple controls requested by the user:
    - random windows from the long-term common-region catalog,
    - same-duration windows outside mainshock-centered intervals,
    - shifted windows within the active period,
    - spatial control regions,
    - bootstrap confidence intervals for count excess, rate ratios, and percentile ranks.
  - Compute background-corrected metrics such as:
    - observed count,
    - expected count,
    - excess count,
    - observed/expected ratio,
    - empirical percentile,
    - empirical p-value or exceedance fraction,
    - local-minus-regional or local/control normalized anomaly index.
  - Evaluate specifically:
    - whether the full common region is exceptional relative to 2020-2026 background,
    - whether anomalies are broad regional pulses or localized clusters,
    - whether the M1-M3 local region remains unusual after regional correction,
    - whether M2 outer-band activity exceeds what would be expected under the broader regional pulse,
    - whether the three mainshock regions show synchronized rate peaks.
  - Construct a compact evidence matrix summarizing support level by region, threshold, depth, and timescale.
- Constraints
  - Keep catalog-level anomaly evidence separate from physical mechanism interpretation.
  - Do not treat anomaly detection or synchrony as proof of triggering, slow slip, fluid migration, stress transfer, or fault interaction.
  - If multiple-testing burden is large across many combinations, emphasize effect size, consistency across controls, and robustness category rather than binary significance alone.
  - Sparse `M5+` and `M6+` results should be reported primarily as rarity/percentile evidence.
- Key outputs
  - Background-corrected anomaly table by region, threshold, depth range, and window length.
  - Robustness/control summary showing which conclusions persist across alternative windows and controls.
  - Spatial anomaly table and map within the common region using observed-versus-expected metrics on fixed cells or polygons, masked where baseline counts are insufficient.
  - Background-rate evidence matrix answering:
    - Is the 2025-2026 active period exceptional within the common region?
    - Which regions and depth ranges show the strongest anomalies?
    - Are anomalies localized or part of a broader regional pulse?
    - Does the M1-M3 local region remain anomalous after correction?
    - Can M2 outer-band activity be explained by regional background-rate changes?
    - Which observations remain statistically interesting for later physical follow-up?
  - Compact figure set:
    - long-term regional rate time series with active period highlighted,
    - active-period rate time series with M1/M2/M3 marked,
    - regional comparison among M1-M3 local, M2 near-field, M2 outer-band, and control regions,
    - spatial rate-anomaly map,
    - depth-stratified rate evolution,
    - long-term percentile comparison for active-period windows,
    - background-rate evidence matrix.

### Task script organization and dependencies
- Primary task script: `aomori_background_rate_analysis`
  - Executes Task 1 through Task 4 in one cohesive workflow: catalog validation, common-mask creation, overlap crosswalk, completeness assessment, region construction, long-term baseline estimation, active-period decomposition, anomaly testing, and generation of summary tables/figures.
  - Success evidence:
    - non-empty common-region and subregion definitions,
    - non-empty filtered long-term and active-period subsets,
    - completed threshold-reliability table,
    - completed long-term expected-versus-observed summaries,
    - completed anomaly/evidence matrix covering the requested scientific questions.
- Optional task script: `aomori_bootstrap_controls`
  - Use only if bootstrap/random-window control calculations are operationally heavy enough to be run independently after the primary script has written validated intermediate summary tables.
  - Inputs:
    - fixed region definitions,
    - filtered long-term subsets,
    - active-period summary tables from the primary script.
  - Success evidence:
    - non-empty bootstrap/control output tables merged back into the final anomaly summary without changing the predefined regions or thresholds.
</experiment_plan>

## Implementation Trace
- Task: 01_aomori_background_rate_analysis
  Description: Audit the two catalogs, define the common analysis region, estimate long-term background rates, decompose active-period rates, and generate anomaly tables and figures.
  Ancestors: none
  Handoff JSON: <CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/log/coding_progress/task_handoff/01_aomori_background_rate_analysis.json
  Output directory: <CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/01_aomori_background_rate_analysis
  Analysis file: <CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/analysis/01_aomori_background_rate_analysis.md
- Task: 02_aomori_bootstrap_controls
  Description: Run heavy bootstrap and random-window control resampling from validated intermediate outputs and merge the results into the anomaly summary.
  Ancestors: 01_aomori_background_rate_analysis
  Handoff JSON: <CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/log/coding_progress/task_handoff/02_aomori_bootstrap_controls.json
  Output directory: <CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/02_aomori_bootstrap_controls
  Analysis file: <CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/analysis/02_aomori_bootstrap_controls.md

## Result Evidence Index
Use handoff JSON files as compact indexes to important outputs. Use per-task analyses for scientific interpretation. Inspect raw outputs only when the handoff and analysis are insufficient.
<task_evidence task="01_aomori_background_rate_analysis">
Handoff JSON: <CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/log/coding_progress/task_handoff/01_aomori_background_rate_analysis.json
{
  "meta": {
    "schema_version": 2,
    "type": "coding_task_handoff",
    "task": "01_aomori_background_rate_analysis",
    "generated_at": "2026-05-24T08:50:08.181765+00:00"
  },
  "status": {
    "state": "success",
    "stage": "analysis_done",
    "elapsed_sec": 587.551,
    "timing": {
      "total_sec": 587.551,
      "coding_agent_sec": 179.68,
      "code_review_sec": 46.508,
      "preflight_sec": 1.688,
      "script_execution_sec": 135.573,
      "result_check_sec": 68.315,
      "task_analysis_sec": 150.028
    },
    "quality_flags": [
      "task_status:success",
      "outputs_truncated"
    ]
  },
  "paths": {
    "root": "<CASE_ROOT>/run/02_4_bg_rate_correction",
    "script": "<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/scripts/01_aomori_background_rate_analysis.py",
    "output_dir": "<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/01_aomori_background_rate_analysis",
    "analysis": "<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/analysis/01_aomori_background_rate_analysis.md",
    "log": "<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/log/task/01_aomori_background_rate_analysis/log_3.txt"
  },
  "outputs": {
    "primary": [
      {
        "path": "diagnostics/context_paths_and_notes.csv",
        "absolute_path": "<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/01_aomori_background_rate_analysis/diagnostics/context_paths_and_notes.csv",
        "kind": "machine_readable"
      },
      {
        "path": "tables/active_period_percentile_vs_background.csv",
        "absolute_path": "<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/01_aomori_background_rate_analysis/tables/active_period_percentile_vs_background.csv",
        "kind": "machine_readable"
      },
      {
        "path": "tables/active_period_rates_by_region.csv",
        "absolute_path": "<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/01_aomori_background_rate_analysis/tables/active_period_rates_by_region.csv",
        "kind": "machine_readable"
      },
      {
        "path": "tables/background_rate_evidence_matrix.csv",
        "absolute_path": "<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/01_aomori_background_rate_analysis/tables/background_rate_evidence_matrix.csv",
        "kind": "machine_readable"
      },
      {
        "path": "tables/catalog_qa_summary.csv",
        "absolute_path": "<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/01_aomori_background_rate_analysis/tables/catalog_qa_summary.csv",
        "kind": "machine_readable"
      },
      {
        "path": "tables/common_region_retention.csv",
        "absolute_path": "<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/01_aomori_background_rate_analysis/tables/common_region_retention.csv",
        "kind": "machine_readable"
      },
      {
        "path": "tables/long_term_background_rates.csv",
        "absolute_path": "<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/01_aomori_background_rate_analysis/tables/long_term_background_rates.csv",
        "kind": "machine_readable"
      },
      {
        "path": "tables/magnitude_completeness_summary.csv",
        "absolute_path": "<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/01_aomori_background_rate_analysis/tables/magnitude_completeness_summary.csv",
        "kind": "machine_readable"
      }
    ],
    "all": [
      "summary_report.txt",
      "diagnostics/context_paths_and_notes.csv",
      "figures/01_catalog_footprints_common_region.png",
      "figures/02_magnitude_depth_comparison.png",
      "figures/03_matched_event_differences.png",
      "figures/04_long_term_monthly_rates.png",
      "figures/05_active_period_rates.png",
      "figures/06_active_region_comparison.png",
      "figures/07_depth_stratified_rates.png",
      "figures/08_spatial_anomaly_map_M3.png",
      "figures/09_active_period_percentiles.png",
      "figures/10_background_rate_evidence_matrix.png",
      "tables/active_period_percentile_vs_background.csv",
      "tables/active_period_rates_by_region.csv",
      "tables/background_rate_evidence_matrix.csv",
      "tables/catalog_qa_summary.csv",
      "tables/common_region_retention.csv",
      "tables/long_term_background_rates.csv",
      "tables/magnitude_completeness_summary.csv",
      "tables/matched_large_events.csv",
      "tables/overlap_threshold_counts.csv",
      "tables/region_definitions.csv",
      "tables/spatial_anomaly_grid_M3.csv",
      "tables/threshold_reliability.csv"
    ],
    "truncated": true
  },
  "notes": {
    "purpose": "Audit the two catalogs, define the common analysis region, estimate long-term background rates, decompose active-period rates, and generate anomaly tables and figures.",
    "result": "Audit the two catalogs, define the common analysis region, estimate long-term background rates, decompose active-period rates, and generate anomaly tables and figures. Status=success; outputs=24 discovered; primary=8.",
    "warnings": [],
    "assumptions": [],
    "limitations": []
  }
}
</task_evidence>

<task_evidence task="02_aomori_bootstrap_controls">
Handoff JSON: <CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/log/coding_progress/task_handoff/02_aomori_bootstrap_controls.json
{
  "meta": {
    "schema_version": 2,
    "type": "coding_task_handoff",
    "task": "02_aomori_bootstrap_controls",
    "generated_at": "2026-05-24T08:50:08.193526+00:00"
  },
  "status": {
    "state": "success",
    "stage": "analysis_done",
    "elapsed_sec": 404.722,
    "timing": {
      "total_sec": 404.722,
      "coding_agent_sec": 130.972,
      "code_review_sec": 19.537,
      "preflight_sec": 1.06,
      "script_execution_sec": 75.586,
      "result_check_sec": 69.162,
      "task_analysis_sec": 102.749
    },
    "quality_flags": [
      "task_status:success"
    ]
  },
  "paths": {
    "root": "<CASE_ROOT>/run/02_4_bg_rate_correction",
    "script": "<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/scripts/02_aomori_bootstrap_controls.py",
    "output_dir": "<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/02_aomori_bootstrap_controls",
    "analysis": "<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/analysis/02_aomori_bootstrap_controls.md",
    "log": "<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/log/task/02_aomori_bootstrap_controls/log_2.txt"
  },
  "outputs": {
    "primary": [
      {
        "path": "diagnostics/run_diagnostics.csv",
        "absolute_path": "<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/02_aomori_bootstrap_controls/diagnostics/run_diagnostics.csv",
        "kind": "machine_readable"
      },
      {
        "path": "tables/background_rate_evidence_matrix_with_controls.csv",
        "absolute_path": "<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/02_aomori_bootstrap_controls/tables/background_rate_evidence_matrix_with_controls.csv",
        "kind": "machine_readable"
      },
      {
        "path": "tables/bootstrap_random_window_controls.csv",
        "absolute_path": "<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/02_aomori_bootstrap_controls/tables/bootstrap_random_window_controls.csv",
        "kind": "machine_readable"
      },
      {
        "path": "figures/01_bootstrap_control_ratio_heatmap.png",
        "absolute_path": "<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/02_aomori_bootstrap_controls/figures/01_bootstrap_control_ratio_heatmap.png",
        "kind": "figure"
      },
      {
        "path": "figures/02_bootstrap_control_percentile_heatmap.png",
        "absolute_path": "<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/02_aomori_bootstrap_controls/figures/02_bootstrap_control_percentile_heatmap.png",
        "kind": "figure"
      },
      {
        "path": "figures/03_random_vs_outside_control_scatter.png",
        "absolute_path": "<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/02_aomori_bootstrap_controls/figures/03_random_vs_outside_control_scatter.png",
        "kind": "figure"
      },
      {
        "path": "summary_report.txt",
        "absolute_path": "<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/02_aomori_bootstrap_controls/summary_report.txt",
        "kind": "document"
      }
    ],
    "all": [
      "summary_report.txt",
      "diagnostics/run_diagnostics.csv",
      "figures/01_bootstrap_control_ratio_heatmap.png",
      "figures/02_bootstrap_control_percentile_heatmap.png",
      "figures/03_random_vs_outside_control_scatter.png",
      "tables/background_rate_evidence_matrix_with_controls.csv",
      "tables/bootstrap_random_window_controls.csv"
    ],
    "truncated": false
  },
  "notes": {
    "purpose": "Run heavy bootstrap and random-window control resampling from validated intermediate outputs and merge the results into the anomaly summary.",
    "result": "Run heavy bootstrap and random-window control resampling from validated intermediate outputs and merge the results into the anomaly summary. Status=success; outputs=7 discovered; primary=7.",
    "warnings": [],
    "assumptions": [],
    "limitations": []
  }
}
</task_evidence>


## Per-Task Scientific Analyses
<task_analysis>
Task: 01_aomori_background_rate_analysis
Description: Audit the two catalogs, define the common analysis region, estimate long-term background rates, decompose active-period rates, and generate anomaly tables and figures.
Analysis file: <CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/analysis/01_aomori_background_rate_analysis.md
Output directory: <CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/01_aomori_background_rate_analysis

## Scientific Purpose

This task built a statistical background-rate framework for the Aomori sequence by explicitly separating two roles: the long-term raw catalog as the 2020–2026 background reference, and the active-period relocated catalog as the higher-resolution dataset for the 2025-10 to 2026-05 activation. The central scientific aim was to test whether the 2025–2026 activity was exceptional relative to background only within a common spatial domain supported by both catalogs, and then determine which regions, depth ranges, magnitude thresholds, and time windows carried the strongest anomaly signal.

The outputs directly address the required questions of whether the active period is unusual, whether anomalies are localized or regionally distributed, whether the M1–M3 local area remains anomalous after regional correction, and whether M2 outer-band activity can be explained by broader regional rate changes. The analysis is statistical only and does not infer physical triggering or source processes, consistent with the task requirements. Key summary evidence is provided in `<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/01_aomori_background_rate_analysis/summary_report.txt` and the anomaly tables under `<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/01_aomori_background_rate_analysis/tables/`.

## Method and Implementation Evidence

A common analysis region was defined from the active relocated catalog footprint with a 0.15° buffer, then the long-term raw catalog was filtered to that same mask before any long-term versus active-period comparison. The common region is documented numerically in `<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/01_aomori_background_rate_analysis/tables/region_definitions.csv` as a bounding box of 38.353003–42.532633°N and 140.851921–144.64847°E, and visually in `<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/01_aomori_background_rate_analysis/figures/01_catalog_footprints_common_region.png`. That figure shows the long-term catalog extending well beyond the relocated footprint, validating the need for spatial harmonization.

Catalog audit and crosswalk evidence indicate that the long-term raw catalog contains 227,755 events over 2020-01-01 to 2026-05-22, while the active relocated catalog contains 22,096 events over 2025-10-01 to 2026-05-01 (`/tables/catalog_qa_summary.csv`). After common-region filtering, 159,087 long-term events and 22,090 active events remain, corresponding to retention fractions of 0.6985 and 0.9997, respectively (`/tables/common_region_retention.csv`). Magnitude completeness was estimated by maximum curvature: Mc = 1.15 for the long-term common-region catalog and Mc = 1.45 for the active common-region catalog (`/tables/magnitude_completeness_summary.csv`). Threshold guidance was therefore made explicit in `/tables/threshold_reliability.csv`: M≥3, M≥4, and M≥5 are preferred for cross-catalog comparison; M≥2 is usable but may be sparse/descriptive; M≥1.2 is retained for active-period relocated analysis only unless completeness is further justified.

Overlap-period crosswalk results support treating larger events as consistent between catalogs. In the overlap period and common region, counts are similar at higher magnitudes: raw versus relocated are 1389 versus 1267 for M≥3, 280 versus 259 for M≥4, 69 versus 68 for M≥5, and 13 versus 13 for M≥6 (`/tables/overlap_threshold_counts.csv`). The matched-event diagnostics for larger events show essentially identical magnitudes and very small differences in origin time, epicentral location, and depth (`/tables/matched_large_events.csv` and `/figures/03_matched_event_differences.png`). The figure indicates time differences mostly in hundredths of a second, location differences mostly ~0.02–0.15 km, and depth differences generally within a few tenths of a kilometer, showing that large-event cross-catalog consistency is strong and that relocation mostly makes minor adjustments rather than redefining major events.

Long-term background rates were estimated from the spatially filtered raw catalog in monthly windows for the common region and subregions (`/tables/long_term_background_rates.csv`). These baseline rates were then used to compute expected counts and percentile ranks for the full active period and shorter windows (`/tables/active_period_percentile_vs_background.csv`). Active-period regional decomposition used the relocated catalog and compared `m1_m3_local_union`, `m2_near_field`, `m2_outer_band`, and `control_region`, with time evolution shown in `/figures/05_active_period_rates.png`, `/figures/06_active_region_comparison.png`, and `/figures/07_depth_stratified_rates.png`. Spatial anomaly mapping at M≥3 is provided by `/tables/spatial_anomaly_grid_M3.csv` and `/figures/08_spatial_anomaly_map_M3.png`. A synthesized evidence matrix across region, depth, and magnitude is given in `/tables/background_rate_evidence_matrix.csv` and `/figures/10_background_rate_evidence_matrix.png`.

One implementation caveat is documented in `/diagnostics/context_paths_and_notes.csv`: the requested active-period file `<CASE_ROOT>/data/Snet_catalog_20251001_20260501_filter.csv` did not exist, so the analysis resolved to `<CASE_ROOT>/data/catalog/Snet_catalog_relocate_250930_260501.csv`.

## Key Results and Evidence Files

### 1. The 2025-10 to 2026-05 activity is statistically exceptional relative to the 2020–2026 background within the common analysis region

The strongest direct evidence comes from `/tables/active_period_percentile_vs_background.csv` and `/figures/09_active_period_percentiles.png`. For the full active period in the common region, observed counts greatly exceed expected background counts:

- M≥3: observed 1267, expected 348.38, obs/exp 3.64, percentile 98.49
- M≥4: observed 259, expected 62.62, obs/exp 4.14, percentile 98.49
- M≥5: observed 68, expected 12.03, obs/exp 5.65, percentile 98.73
- M≥6: observed 13, expected 1.95, obs/exp 6.68, percentile 99.62

These values are also summarized in `/summary_report.txt`. The long-term monthly-rate figure `/figures/04_long_term_monthly_rates.png` shows that the active period stands out sharply against the 2020–2025 background in the common region, with very large spikes during the shaded active interval across M≥3, M≥4, and M≥5. Before the active period, M≥3 rates are in the tens per month and M≥4 rates in low single digits to ~10; during the active period they surge to about ~400 per month for M≥3, ~90 for M≥4, and ~30 for M≥5.

This supports a clear report-ready conclusion: within the common region, the active period is not a routine fluctuation of the 2020–2026 background and is exceptional across multiple reliable long-term thresholds.

### 2. Preferred long-term comparison thresholds are M≥3, M≥4, and M≥5; M≥1.2 should be restricted to active-period internal analysis

Completeness and overlap evidence support threshold reliability decisions. `/tables/magnitude_completeness_summary.csv` gives Mc = 1.15 for the long-term common region and Mc = 1.45 for the active common region, while `/figures/02_magnitude_depth_comparison.png` shows the relocated catalog thinning more strongly at low magnitudes and at depths >60 km. `/tables/threshold_reliability.csv` explicitly states that M≥3, M≥4, and M≥5 are preferred for cross-catalog comparison, M≥2 is descriptive only if sparse, and M≥1.2 is not reliable for long-term comparison.

The overlap counts also show that higher-magnitude event retention is strong between catalogs: 259/280 retained at M≥4, 68/69 at M≥5, and 13/13 at M≥6 (`/tables/overlap_threshold_counts.csv`). Therefore the anomaly claims based on M≥3–M≥5 are the most defensible for long-term background comparison, while low-magnitude active-period results are better interpreted as internal sequence structure rather than background-reference evidence.

### 3. The strongest anomalies are localized, not uniformly regionwide, and they concentrate in the M1–M3 local union and around the M2 system

Spatial and regional comparisons point to localized hotspots superposed on a weaker broader regional elevation. `/figures/08_spatial_anomaly_map_M3.png` maps log10(observed/expected) for M≥3 and shows patchy positive anomalies rather than a domain-wide uniform increase. The strongest positive clusters lie near approximately 142.4–143.3°E, 40.8–41.3°N and 143.2–143.8°E, 39.0–39.7°N, with mixed or negative cells elsewhere. The corresponding grid values are archived in `/tables/spatial_anomaly_grid_M3.csv`.

The region-level full active-period comparisons in `/tables/active_period_percentile_vs_background.csv` show:

- `m1_m3_local_union`: M≥3 obs/exp 10.51, percentile 98.87; M≥4 obs/exp 11.14, percentile 99.10; M≥5 obs/exp 12.35, percentile 99.10; M≥6 obs/exp 12.52, percentile 100.0
- `m2_near_field`: M≥3 obs/exp 4.82, percentile 95.71; M≥4 obs/exp 5.14, percentile 98.16; M≥5 obs/exp 6.35, percentile 100.0; M≥6 obs/exp 6.12, percentile 100.0
- `m2_outer_band`: M≥3 obs/exp 3.38, percentile 98.68; M≥4 obs/exp 2.99, percentile 98.63; M≥5 obs/exp 2.79, percentile 98.73; M≥6 obs/exp 6.64, percentile 100.0
- `control_region`: M≥3 obs/exp 0.97, percentile 59.52; M≥4 obs/exp 1.36, percentile 82.33; M≥5 obs/exp 1.90, percentile 88.17; M≥6 obs/exp 1.22, percentile 72.15

These values show that the target subregions are highly exceptional relative to background, whereas the control region is much less so. The percentile heatmap `/figures/09_active_period_percentiles.png` makes this contrast visually obvious: the target windows are mostly in the 96th–100th percentile range, while the control region is only moderate.

Thus, the anomalies are not best described as a uniform broad regional pulse; they are concentrated in specific areas, especially the M1–M3 local union and the M2-associated regions.

### 4. The M1–M3 local region remains strongly anomalous after regional background correction

This is one of the clearest results. In `/tables/background_rate_evidence_matrix.csv` and `/figures/10_background_rate_evidence_matrix.png`, the M1–M3 local union shows the highest observed/expected ratios in the matrix. Notable cells include:

- `m1_m3_local_union | 0–30 km | M≥3`: observed 637, expected 82.77, obs/exp 7.70
- `m1_m3_local_union | 0–30 km | M≥4`: observed 139, expected 15.79, obs/exp 8.80
- `m1_m3_local_union | 0–30 km | M≥5`: observed 44, expected 4.56, obs/exp 9.64
- `m1_m3_local_union | 30–60 km | M≥5`: observed 1, expected 0.09, obs/exp 10.96

The full active-period regional percentiles in `/tables/active_period_percentile_vs_background.csv` also place `m1_m3_local_union` near the top across all reliable thresholds, with 98.87–100th percentile ranks. The regional time-series figure `/figures/06_active_region_comparison.png` shows this region producing a very large early-November burst and another strong late-April burst, both much stronger than the control region. Therefore, after using the common-region background as the reference, the M1–M3 local region still remains highly anomalous and cannot be reduced to a modest byproduct of a weak regional uplift.

### 5. M2 outer-band activity exceeds background expectations and is not fully explained by the broader control-region background

The `m2_outer_band` does show significant anomaly relative to its own long-term background. In `/tables/active_period_percentile_vs_background.csv`, its active-period percentile ranks are 98.68, 98.63, 98.73, and 100.0 for M≥3 through M≥6, with obs/exp ratios of 3.38, 2.99, 2.79, and 6.64. In the evidence matrix (`/tables/background_rate_evidence_matrix.csv`), the shallow 0–30 km portion of `m2_outer_band` is consistently elevated:

- M≥1.2: 4.21
- M≥2: 4.67
- M≥3: 5.53
- M≥4: 4.39
- M≥5: 4.26

By contrast, the control region is much weaker, especially at M≥3 where the full active-period obs/exp is 0.97 with percentile 59.5 (`/tables/active_period_percentile_vs_background.csv`). The regional comparison figure `/figures/06_active_region_comparison.png` shows that the outer band hosts the largest December spike in 7-day counts, around ~2000, clearly exceeding both `m2_near_field` and the control region. These results argue that M2 outer-band activity is not adequately explained as a simple reflection of a common background rise seen everywhere; it carries its own localized excess above regional controls.

### 6. The main activation is dominated by shallow seismicity, with secondary contribution from 30–60 km and little support for strong >60 km anomalies

Depth-stratified evidence is consistent across the figure and matrix products. `/figures/07_depth_stratified_rates.png` shows that 0–30 km dominates the active-period rate evolution, with strong peaks in mid-November 2025, mid-December 2025, and late April 2026. The 30–60 km bin responds mainly during December 2025 and more weakly in late April 2026, while the ≥60 km bin remains low and noisy with no major swarm-scale escalation.

The background evidence matrix confirms this depth contrast (`/tables/background_rate_evidence_matrix.csv`). Examples:

- `common_region | 0–30 km | M≥5`: obs/exp 7.22
- `common_region | 30–60 km | M≥5`: obs/exp 2.74
- `common_region | ≥60 km | M≥5`: obs/exp 1.00

- `m2_near_field | 30–60 km | M≥5`: obs/exp 7.31
- `m2_near_field | ≥60 km | M≥5`: obs/exp 0.00

- `m2_outer_band | 0–30 km | M≥3`: obs/exp 5.53
- `m2_outer_band | ≥60 km | M≥3`: obs/exp 0.10

- `control_region | 30–60 km | M≥3`: obs/exp 0.69
- `control_region | ≥60 km | M≥3`: obs/exp 0.30

The main scientific interpretation is that the 2025–2026 anomaly is overwhelmingly a shallow-to-mid crustal phenomenon in statistical terms, with the shallow 0–30 km bin carrying the dominant signal and >60 km depths contributing little anomaly evidence.

### 7. The active period consists of multiple temporally distinct bursts rather than a single uniform rate increase

The time-series products show a burst-decay structure with three main episodes aligned with M1, M2, and M3. `/figures/05_active_period_rates.png` presents daily and 7-day counts for the relocated active catalog. It shows:

- an initial strong burst around M1 in mid-November 2025
- the largest burst around M2 in December 2025
- a renewed large burst around M3 in late April 2026
- sustained but lower background between these peaks, without full return to the early-October baseline

`/figures/06_active_region_comparison.png` adds regional structure: `m1_m3_local_union` peaks strongly in November and again in late April, `m2_outer_band` dominates the December episode, `m2_near_field` rises sharply but less strongly than the outer band in December, and the control region shows only moderate increases. This indicates partial synchrony within a broader active interval, but with important spatial segmentation of the main pulses rather than one perfectly coherent regional rate pulse.

### 8. Long-term background levels differ substantially by region, which matters for interpreting anomaly strength

The long-term monthly baselines in `/tables/long_term_background_rates.csv` show that anomaly interpretation depends on region-specific background productivity. For example, monthly M≥3 mean background counts are:

- common_region: 56.26
- m1_m3_local_union: 12.04
- m2_near_field: 4.31
- m2_outer_band: 17.91
- control_region: 24.09

For M≥4, the means are 10.16, 2.34, 0.86, 3.50, and 4.05, respectively. These differences explain why modest absolute counts can still translate into high local percentiles in low-background regions, and why common-region anomaly claims should not be substituted for local anomaly claims. The task appropriately preserved both absolute and normalized viewpoints through separate region-specific baselines.

## Limitations and Assumptions

The most important practical limitation is that the requested active-period file was not available; the analysis instead used a resolved relocated catalog path, documented in `<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/01_aomori_background_rate_analysis/diagnostics/context_paths_and_notes.csv`. Any downstream reporting should name the actual file used: `<CASE_ROOT>/data/catalog/Snet_catalog_relocate_250930_260501.csv`.

The handoff reports `outputs_truncated`, so not every internal output is indexed in the handoff JSON even though the main deliverables are present. No PDF outputs were listed among the task products, so there were no PDF documents to analyze.

Magnitude completeness differs between catalogs. `/tables/magnitude_completeness_summary.csv` shows Mc = 1.15 for the long-term common region and Mc = 1.45 for the active common region. Consequently, low-magnitude comparisons across catalogs are not equally robust. `/tables/threshold_reliability.csv` correctly warns that M≥1.2 should not be used as a primary long-term comparison threshold. Results involving M≥1.2 are useful for active-period structure but should not be over-interpreted as evidence of long-term exceptionality.

Depth coverage also differs. `/figures/02_magnitude_depth_comparison.png` shows that the relocated catalog is much more shallowly concentrated than the long-term raw catalog and underrepresents deeper seismicity. Therefore, depth-dependent anomaly interpretations, especially below 60 km, are more secure as negative or weak findings than as evidence of fine-scale deep structure.

Some very high observed/expected ratios arise from small expected counts, especially in sparse high-threshold or 30–60 km subcells. For example, `m1_m3_local_union | 30–60 km | M≥5` has obs/exp 10.96 but only one observed event against an expectation of 0.09 (`/tables/background_rate_evidence_matrix.csv`). Such cells are still informative but should be interpreted with caution because the ratio can be unstable when denominators are very small.

The analysis is explicitly statistical and catalog-based. It does not demonstrate triggering, fault interaction, fluid movement, slow slip, or any mechanism. `/summary_report.txt` states this clearly, and that caveat should be preserved in any integrated report.

## Report-Ready Summary

A statistically defensible background-rate model was built by filtering the 2020–2026 long-term raw catalog to the same common spatial domain defined from the active relocated catalog. The common region spans 38.353003–42.532633°N and 140.851921–144.64847°E (`/tables/region_definitions.csv`; `/figures/01_catalog_footprints_common_region.png`). This step is essential because the raw catalog has broader spatial coverage than the relocated active-period catalog.

Catalog audit results show that larger events are highly consistent between catalogs in the overlap period. In the common region, overlap counts are nearly matched at M≥4, M≥5, and M≥6, and matched-event differences are very small in time, location, and depth (`/tables/overlap_threshold_counts.csv`, `/tables/matched_large_events.csv`, `/figures/03_matched_event_differences.png`). Completeness estimates indicate Mc ≈ 1.15 for the long-term common-region catalog and Mc ≈ 1.45 for the active common-region catalog (`/tables/magnitude_completeness_summary.csv`), so M≥3, M≥4, and M≥5 are the preferred thresholds for long-term anomaly claims (`/tables/threshold_reliability.csv`).

Within the common region, the 2025-10 to 2026-05 active period is clearly exceptional relative to the 2020–2026 background. Observed versus expected counts are 1267 versus 348 for M≥3, 259 versus 62.6 for M≥4, 68 versus 12.0 for M≥5, and 13 versus 1.95 for M≥6, corresponding to percentile ranks of 98.5–99.6 (`/tables/active_period_percentile_vs_background.csv`; `/figures/09_active_period_percentiles.png`; `/summary_report.txt`). The monthly time series shows the active interval as the dominant peak in the entire 2020–2026 record for the common region (`/figures/04_long_term_monthly_rates.png`).

The anomalies are not uniform across the study area. They are localized and strongest in the `m1_m3_local_union`, `m2_near_field`, and `m2_outer_band`, while the `control_region` shows only weak-to-moderate elevation (`/tables/active_period_percentile_vs_background.csv`; `/figures/06_active_region_comparison.png`; `/figures/09_active_period_percentiles.png`). The M1–M3 local union remains strongly anomalous after background correction, with full-period obs/exp ratios of 10.5, 11.1, and 12.4 at M≥3, M≥4, and M≥5, and with the highest cells in the region-depth evidence matrix (`/tables/background_rate_evidence_matrix.csv`; `/figures/10_background_rate_evidence_matrix.png`). The M2 outer band also exceeds background strongly, especially in the shallow 0–30 km bin, and its December 2025 pulse is far larger than the control-region response, indicating that it cannot be explained solely as a general regional uplift (`/tables/active_period_percentile_vs_background.csv`; `/tables/background_rate_evidence_matrix.csv`; `/figures/06_active_region_comparison.png`).

Depth decomposition shows that the anomaly is dominated by 0–30 km seismicity, with secondary 30–60 km involvement and little evidence for a strong >60 km anomaly (`/figures/07_depth_stratified_rates.png`; `/tables/background_rate_evidence_matrix.csv`). The temporal evolution is burst-like rather than uniform, with strong pulses associated with M1 in November 2025, M2 in December 2025, and M3 in late April 2026 (`/figures/05_active_period_rates.png`; `/figures/06_active_region_comparison.png`).

For later physical follow-up, the most statistically interesting observations are: (1) the high common-region exceptionality across M≥3–M≥6, (2) the persistence of strong anomaly in the M1–M3 local union after regional correction, (3) the significant and shallow-dominated excess in the M2 outer band beyond control-region behavior, and (4) the spatially patchy anomaly map indicating localized hotspots rather than a smooth domain-wide increase (`/figures/08_spatial_anomaly_map_M3.png`; `/tables/spatial_anomaly_grid_M3.csv`). These findings provide robust catalog-level support for targeted physical interpretation later, but they do not themselves establish any triggering or mechanism.
</task_analysis>

<task_analysis>
Task: 02_aomori_bootstrap_controls
Description: Run heavy bootstrap and random-window control resampling from validated intermediate outputs and merge the results into the anomaly summary.
Analysis file: <CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/analysis/02_aomori_bootstrap_controls.md
Output directory: <CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/02_aomori_bootstrap_controls

## Scientific Purpose

This task adds statistical controls to the Aomori background-rate analysis by testing whether the 2025-10 to 2026-05 active-period rate anomalies remain unusual when compared with many alternative long-term windows. The scientific aim is not to reinterpret the catalogs, but to stress-test the anomaly claims from the prior background-rate analysis using:
- bootstrap/random-window comparisons against the long-term common-region catalog,
- comparisons restricted to long-term windows outside the active dates,
- shifted-window checks within the active period.

The output is directly relevant to the final question of whether the 2025-2026 Aomori activity is exceptional relative to long-term background seismicity, and whether the strongest signals are localized or reflect a broader regional pulse.

## Method and Implementation Evidence

The task completed successfully according to the handoff record at `<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/log/coding_progress/task_handoff/02_aomori_bootstrap_controls.json`.

Implementation evidence from `<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/02_aomori_bootstrap_controls/diagnostics/run_diagnostics.csv` shows:
- the script used was `<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/scripts/02_aomori_bootstrap_controls.py`,
- inputs were taken from the validated outputs of Task 01 in `<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/01_aomori_background_rate_analysis`,
- the active relocated catalog used was `<CASE_ROOT>/data/catalog/Snet_catalog_relocate_250930_260501.csv`,
- only thresholds 3.0, 4.0, and 5.0 were selected for the heavy control analysis,
- `resample_n = 4000`,
- `task_count = 180`,
- `long_term_common_events = 159087`,
- `active_common_events = 22090`.

The primary machine-readable evidence files are:
- `<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/02_aomori_bootstrap_controls/tables/bootstrap_random_window_controls.csv`
- `<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/02_aomori_bootstrap_controls/tables/background_rate_evidence_matrix_with_controls.csv`

These tables include, for each region/depth/threshold/window combination:
- observed counts,
- mean expected counts from random windows and outside-active windows,
- percentile rank of the active-period window,
- exceedance fractions,
- bootstrap ratio means and confidence limits,
- shifted-window comparisons within the active period,
- a qualitative `control_support_level`.

The compact text summary at `<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/02_aomori_bootstrap_controls/summary_report.txt` confirms that the task was designed specifically to merge heavy bootstrap and random-window controls into the anomaly summary.

## Key Results and Evidence Files

### 1. The strongest active-period anomalies remain extreme after bootstrap and random-window controls

The clearest result is that the most prominent anomalies from Task 01 persist under heavy resampling controls. The summary report lists the top active-period anomalies as:
- `m1_m3_local_union | 0-30 km | M>=4`: `obs/exp(primary)=8.80`, `random_ratio_mean=94.10`, `random_percentile=99.1`, `outside_percentile=100.0`, `support=very_strong`
- `m1_m3_local_union | 0-30 km | M>=5`: `obs/exp(primary)=9.64`, `random_ratio_mean=58.97`, `random_percentile=99.1`, `outside_percentile=100.0`, `support=very_strong`
- `m1_m3_local_union | 0-30 km | M>=3`: `obs/exp(primary)=7.70`, `random_ratio_mean=32.49`, `random_percentile=98.9`, `outside_percentile=100.0`, `support=very_strong`

Evidence:
- `<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/02_aomori_bootstrap_controls/summary_report.txt`
- `<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/02_aomori_bootstrap_controls/tables/background_rate_evidence_matrix_with_controls.csv`
- `<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/02_aomori_bootstrap_controls/figures/01_bootstrap_control_ratio_heatmap.png`
- `<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/02_aomori_bootstrap_controls/figures/02_bootstrap_control_percentile_heatmap.png`

The ratio heatmap shows the dominant hotspot at `m1_m3_local_union | 0-30 km`, especially for `M>=4` (94.10), followed by `M>=5` (58.97) and `M>=3` (32.49). The percentile heatmap independently shows these same bins at about the 99th to 100th percentile. Together, these outputs support the conclusion that the local M1-M3 union region remains highly anomalous after long-term control correction.

### 2. The anomaly is not confined to one local window; it extends into the common region and selected M2-related zones, but weakens with distance

The summary report also identifies strong support for:
- `common_region | 0-30 km | M>=5`: `obs/exp(primary)=7.22`, `random_ratio_mean=30.63`, `random_percentile=98.5`, `outside_percentile=100.0`
- `common_region | 0-30 km | M>=4`: `obs/exp(primary)=5.82`, `random_ratio_mean=12.46`, `random_percentile=98.8`, `outside_percentile=100.0`
- `common_region | 0-30 km | M>=3`: `obs/exp(primary)=5.38`, `random_ratio_mean=10.07`, `random_percentile=98.8`, `outside_percentile=100.0`

Evidence:
- `<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/02_aomori_bootstrap_controls/summary_report.txt`
- `<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/02_aomori_bootstrap_controls/tables/background_rate_evidence_matrix_with_controls.csv`
- `<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/02_aomori_bootstrap_controls/figures/01_bootstrap_control_ratio_heatmap.png`

This means the active-period anomaly survives regionalization: it is not only a local artifact of the M1-M3 area, because the common-region 0-30 km bins are also strongly elevated.

At the same time, the heatmap demonstrates strong spatial decay:
- many `>=60 km` cells are near zero in ratio,
- examples include `m1_m3_local_union | >=60 km = 0.00` for all thresholds and `m2_near_field | >=60 km = 0.00` for all thresholds in the ratio heatmap.

This pattern argues for a localized-to-subregional anomaly rather than a uniformly elevated far-field regional rate.

### 3. M2 near-field and M2 outer-band anomalies are supported, but the support is selective rather than uniform

The control-resampled summary identifies several strong M2-related anomalies:
- `m2_near_field | 30-60 km | M>=4`: `obs/exp(primary)=5.37`, `random_ratio_mean=13.84`, `random_percentile=98.2`, `outside_percentile=100.0`, `support=very_strong`
- `m2_near_field | 30-60 km | M>=5`: `obs/exp(primary)=7.31`, `random_ratio_mean=12.26`, `random_percentile=100.0`, `outside_percentile=100.0`, `support=very_strong`
- `m2_near_field | 0-30 km | M>=3`: `obs/exp(primary)=4.63`, `random_ratio_mean=11.63`, `random_percentile=96.2`, `outside_percentile=100.0`, `support=strong`
- `m2_outer_band | 0-30 km | M>=4`: `obs/exp(primary)=5.05`, `random_ratio_mean=13.64`, `random_percentile=98.9`, `outside_percentile=100.0`, `support=very_strong`
- `m2_outer_band | 0-30 km | M>=3`: `obs/exp(primary)=5.53`, `random_ratio_mean=10.46`, `random_percentile=98.9`, `outside_percentile=100.0`, `support=very_strong`

Evidence:
- `<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/02_aomori_bootstrap_controls/summary_report.txt`
- `<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/02_aomori_bootstrap_controls/tables/background_rate_evidence_matrix_with_controls.csv`
- `<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/02_aomori_bootstrap_controls/figures/01_bootstrap_control_ratio_heatmap.png`
- `<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/02_aomori_bootstrap_controls/figures/02_bootstrap_control_percentile_heatmap.png`

However, support is not spatially uniform:
- `m2_near_field | 0-30 km | M>=5` is 0.00 in the ratio heatmap,
- `m2_outer_band | >=60 km` is near zero or zero in the ratio heatmap,
- percentile values in the farthest bins can be low or highly variable.

Thus, M2 outer-band activity cannot be summarized as a broad, everywhere-elevated anomaly. Instead, the controls support elevated rates mainly in selected near and intermediate distance bins, especially for `M>=3` to `M>=5` in the 0-30 km and 30-60 km bands.

### 4. The choice of control window does not materially change the main conclusions

The scatter plot directly compares bootstrap ratios computed against:
- all long-term random windows, and
- long-term windows outside the active dates.

Most points lie close to the 1:1 line, including the dense cluster of lower-valued combinations and the major outliers. The strongest anomalies remain strong under both control definitions.

Evidence:
- `<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/02_aomori_bootstrap_controls/figures/03_random_vs_outside_control_scatter.png`

The plot shows:
- a dense core near the origin close to the 1:1 reference line,
- the largest outliers still aligned near the line,
- slight tendency for points to lie above the line, implying the outside-active-date control often yields slightly stronger anomalies.

This indicates that the anomaly claims are robust to control choice. Excluding active dates from the long-term controls may sharpen the contrast somewhat, but it does not create the main anomaly pattern.

### 5. Percentile support is generally high for the main target bins, but percentile saturation and far-field instability require caution

The percentile heatmap shows many target bins in the 98th-100th percentile range, including:
- `common_region | 0-30 km` across `M>=3`, `M>=4`, `M>=5`,
- `m1_m3_local_union | 0-30 km` across all three thresholds,
- `m2_near_field | 30-60 km | M>=5 = 100`,
- `m2_outer_band | 30-60 km | M>=5 = 100`.

Evidence:
- `<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/02_aomori_bootstrap_controls/figures/02_bootstrap_control_percentile_heatmap.png`
- `<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/02_aomori_bootstrap_controls/tables/background_rate_evidence_matrix_with_controls.csv`

But some `>=60 km` bins show boundary values of 0 or 100, for example:
- `common_region | >=60 km | M>=3 = 0`,
- `common_region | >=60 km | M>=4 = 0`,
- `control_region | >=60 km | M>=5 = 100`,
- `m2_outer_band | >=60 km | M>=3 = 0`.

These edge values likely reflect sparse counts and ranking saturation rather than stable effect-size separation. Therefore, percentile ranks in low-count far-field bins should be treated as secondary evidence.

### 6. Control support is intentionally restricted to thresholds with stronger catalog comparability

The merged evidence matrix includes threshold 1.2 and 2.0 rows, but these rows are labeled `insufficient_control_data` and contain `NaN` in the control fields. For example, in the evidence matrix:
- `common_region | 0-30 km | 1.2` and `2.0` have observed and expected counts from the primary analysis, but no bootstrap control statistics.

Evidence:
- `<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/02_aomori_bootstrap_controls/tables/background_rate_evidence_matrix_with_controls.csv`
- `<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/02_aomori_bootstrap_controls/diagnostics/run_diagnostics.csv`

This is scientifically consistent with the broader catalog-comparison rule: the heavy cross-catalog background controls were restricted to `M>=3`, `M>=4`, and `M>=5`, which are the more defensible long-term comparison thresholds.

## Limitations and Assumptions

- This task is a control/resampling extension of prior validated outputs, not a fresh catalog audit. Its interpretation depends on the common-region definitions and region masks inherited from Task 01, whose outputs are referenced at `<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/01_aomori_background_rate_analysis`.
- Heavy controls were applied only to thresholds `M>=3`, `M>=4`, and `M>=5`, as shown in `<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/02_aomori_bootstrap_controls/diagnostics/run_diagnostics.csv`. Low-magnitude thresholds (`1.2`, `2.0`) remain unavailable for this long-term control test and are explicitly marked `insufficient_control_data` in `<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/02_aomori_bootstrap_controls/tables/background_rate_evidence_matrix_with_controls.csv`.
- Some figure labels suggest minor terminology inconsistency: the ratio heatmap title refers to bootstrap controls while the colorbar is labeled `random_ratio_mean`. This does not appear to change the underlying table values but should be standardized before publication.
- Several far-field or sparse bins produce exact 0 or 100 percentiles. These likely reflect limited counts and boundary saturation rather than precise effect magnitude; they should not be overinterpreted.
- Extremely large ratio values, such as 94.10 for `m1_m3_local_union | 0-30 km | M>=4`, are compelling but should be paired with the underlying count context from the tables rather than treated as standalone physical measures.
- This task supports statistical anomaly detection only. It does not provide evidence for triggering, slow slip, fluid migration, stress transfer, or fault interaction, and should not be used as mechanism proof.

## Report-Ready Summary

Bootstrap and random-window controls strongly support the conclusion that the 2025-10 to 2026-05 Aomori active period was exceptional relative to the 2020-2026 long-term background within the common analysis region, at least for the robust long-term comparison thresholds `M>=3`, `M>=4`, and `M>=5`. The most compelling anomaly is the `m1_m3_local_union` in the `0-30 km` depth bin, where all three thresholds show very high active/background contrasts and approximately 99th-100th percentile rankings relative to long-term control windows. Key evidence is preserved in `<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/02_aomori_bootstrap_controls/tables/background_rate_evidence_matrix_with_controls.csv`, `<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/02_aomori_bootstrap_controls/summary_report.txt`, and the ratio/percentile heatmaps.

The anomaly is not limited to a single micro-region. The `common_region | 0-30 km` bins are also strongly elevated across `M>=3` to `M>=5`, and selected M2-related regions show substantial excess as well, especially `m2_near_field | 30-60 km` and `m2_outer_band | 0-30 km`. However, the anomaly weakens sharply in many `>=60 km` bins, which argues against a spatially uniform far-field rate increase. The most defensible interpretation is therefore a localized-to-subregional rate pulse rather than a region-wide homogeneous elevation.

The M1-M3 local region remains anomalous after regional background correction and after long-term control resampling; this is the strongest and most stable result of the task. M2 outer-band activity also shows statistically elevated bins, especially at `0-30 km` for `M>=3` and `M>=4`, but the support is more selective than for the M1-M3 local union and should be described as partially explained by a broader regional pulse plus localized enhancement rather than as a uniformly independent anomaly.

The anomaly conclusions are robust to control-window choice. The scatter comparison in `<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/02_aomori_bootstrap_controls/figures/03_random_vs_outside_control_scatter.png` shows that results using all long-term random windows and windows outside the active dates are closely aligned. This makes the strongest anomaly claims suitable for later physical follow-up, while low-count far-field bins and low-magnitude thresholds should remain secondary or provisional.
</task_analysis>


## Evaluation Quality Summary
Use this evaluation metadata to disclose delivery status, scientific confidence, and important limitations in the final report.
<evaluation_quality>
{
  "delivery_status": "complete",
  "is_satisfactory": true,
  "limitations": [
    {
      "evidence": "The requested active-period file was missing and the analysis substituted data/catalog/Snet_catalog_relocate_250930_260501.csv, documented in diagnostics/context_paths_and_notes.csv.",
      "impact": "Core objectives were still addressed, but reproducibility relative to the exact requested filename/product is slightly reduced and should be disclosed in any final interpretation.",
      "severity": "medium",
      "type": "external_dependency"
    },
    {
      "evidence": "Magnitude completeness was estimated by maximum curvature and threshold reliability was simplified into preferred/descriptive categories.",
      "impact": "The main M>=3 to M>=5 anomaly conclusions are likely robust, but low-magnitude comparability and exact Mc values may be less certain than if multiple Mc methods or uncertainty bounds were applied.",
      "severity": "medium",
      "type": "method_assumption"
    },
    {
      "evidence": "Several large observed/expected ratios in the evidence matrix arise from very small expected counts in sparse high-magnitude or depth-partitioned cells.",
      "impact": "Effect sizes in sparse bins may look extreme even when count support is limited, so those cells should be interpreted as rarity indicators rather than precise anomaly magnitudes.",
      "severity": "medium",
      "type": "uncertainty"
    },
    {
      "evidence": "The long-term reference spans 2020-01-01 to 2026-05-22 only.",
      "impact": "This is sufficient for the requested task, but the background distribution may still reflect medium-term nonstationarity and may not capture rarer decade-scale behavior.",
      "severity": "low",
      "type": "data_coverage"
    },
    {
      "evidence": "Task 02 notes minor terminology inconsistency in figure labeling (bootstrap vs random_ratio_mean), and task handoff for Task 01 indicates outputs_truncated in the inventory listing.",
      "impact": "These do not undermine the conclusions but slightly reduce publication-readiness and traceability of some outputs.",
      "severity": "low",
      "type": "output_quality"
    },
    {
      "evidence": "Depth comparisons note that the relocated catalog is shallower and underrepresents deeper seismicity relative to the long-term raw catalog.",
      "impact": "Deep-bin negative or weak findings are less secure as structural interpretations and should remain descriptive.",
      "severity": "low",
      "type": "consistency"
    }
  ],
  "needs_refinement": false,
  "refinement_priority": "none",
  "scientific_confidence": "moderate"
}
</evaluation_quality>

## Report Synthesis Rules
- Start from the scientific objective and planned workflow.
- Choose the final report shape according to the request and evidence.
- If the user requested a specific format, follow that requested format unless it conflicts with factuality or available evidence.
- Treat concise result summary, technical workflow report, and research-article style report as common shapes, not fixed templates.
- Use task-specific structures when more appropriate, such as diagnostic review, data-quality assessment, method validation, benchmark comparison, or reproducibility report.
- Hybrid structures are allowed when they better serve the scientific objective.
- Do not force a fixed section template when another structure better serves the scientific request.
- Describe implementation at the level needed to understand the evidence, not as a code log.
- Tie every major result to task analyses and concrete output files from the evidence index.
- Include warnings, assumptions, partial coverage, failed items, and other limitations when present.
- Use debug logs only to explain unresolved limitations or important methodological changes.
- Do not fabricate results, citations, or file paths.

</science_report_context>
