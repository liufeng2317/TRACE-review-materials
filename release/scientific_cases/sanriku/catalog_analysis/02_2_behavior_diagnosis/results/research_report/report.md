---
author:
- TRACE
title: Mainshock-Centered Diagnosis of Sequence Behavior in the Aomori Earthquake Catalog
---

# Abstract

This report diagnoses the seismic-sequence behavior around the three principal Aomori mainshocks (M1, M2, and M3) using a mainshock-referenced earthquake table, short-window morphology figures, matched pre/post metrics across multiple windows and distance definitions, and supporting depth and focal-mechanism context. The analysis objective was to distinguish local sequence behavior from broader regional activation and to score multiple non-mutually-exclusive behavior dimensions rather than force each sequence into a single label. The principal result is that all three mainshocks show post-mainshock activation, but with clearly different organization: M1 is the most compact and near-field dominated sequence yet is weakly single-mainshock dominated and shows strong pre-mainshock activation; M2 shows the strongest broader regional activation and the most distributed post-mainshock response; and M3 is the most strongly single-mainshock dominated, with substantial post-mainshock activation but weaker evidence for comparable companion events. The catalog-based evidence does not support monotonic radial migration or a slow-slip-like interpretation for any sequence. These conclusions are comparative and diagnostic rather than causal, because the workflow did not fit ETAS/Omori or explicit background-rate models and because neighboring sequence overlap affects some pre/post contrasts.

# Scientific objective

The scientific goal of this stage was to characterize the behavior of the Aomori seismicity around three large mainshocks, denoted M1, M2, and M3, using a common reference frame centered on each mainshock. The requested emphasis was to describe how seismicity evolved before and after each mainshock, identify the most plausible behavior modes for each mainshock-centered sequence, and separate local sequence behavior from broader regional activation.

The project context specified four core implementation elements: (1) construction of a mainshock-referenced event table; (2) creation of short-window diagnostic sequence figures in a $`\pm 7`$ day and $`\leq 100`$ km frame; (3) matched pre/post quantitative metrics for multiple windows and spatial definitions; and (4) addition of depth and focal-mechanism context. The intended scientific synthesis was explicitly multi-dimensional: aftershock response, mainshock dominance, compound or swarm-like organization, pre-mainshock activation, broader regional activation, migration, and slow-slip-related screening were to be evaluated as evidence axes rather than mutually exclusive class labels.

# Implemented workflow and evidence products

The implemented workflow produced the complete requested evidence package in <a href="<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis" class="uri"><CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis</a>. The analysis was executed by a self-contained script documented in the task analysis, and the output directory contains 28 discovered products, including the required figures, metric tables, and diagnosis summaries.

The main implemented components were:

1.  **Mainshock-referenced event construction.** A unified event table was generated in <a href="<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/mainshock_reference_event_table.csv" class="uri"><CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/mainshock_reference_event_table.csv</a>, together with a dedicated matching summary in <a href="<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/mainshock_like_match_summary.csv" class="uri"><CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/mainshock_like_match_summary.csv</a>.

2.  **Short-window morphology figures.** The required $`\pm 7`$ day, $`\leq 100`$ km sequence views were produced as Figure <a href="#fig:morphology" data-reference-type="ref" data-reference="fig:morphology">1</a>, Figure <a href="#fig:m4plus" data-reference-type="ref" data-reference="fig:m4plus">2</a>, Figure <a href="#fig:prepost" data-reference-type="ref" data-reference="fig:prepost">3</a>, and Figure <a href="#fig:distancebands" data-reference-type="ref" data-reference="fig:distancebands">4</a>.

3.  **Matched pre/post metrics and robustness checks.** Exhaustive metric tables were saved as <a href="<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/matched_window_metrics_all.csv" class="uri"><CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/matched_window_metrics_all.csv</a> and <a href="<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/matched_window_metrics_by_band.csv" class="uri"><CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/matched_window_metrics_by_band.csv</a>, with curated sensitivity figures in Figure <a href="#fig:sensitivity" data-reference-type="ref" data-reference="fig:sensitivity">6</a> and Figure <a href="#fig:robustness" data-reference-type="ref" data-reference="fig:robustness">7</a>.

4.  **Behavior-dimension scoring.** Sequence-level evidence synthesis was provided in <a href="<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/behavior_dimension_scores.csv" class="uri"><CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/behavior_dimension_scores.csv</a>, <a href="<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/behavior_dimension_supporting_metrics.csv" class="uri"><CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/behavior_dimension_supporting_metrics.csv</a>, and <a href="<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/sequence_behavior_evidence_table.csv" class="uri"><CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/sequence_behavior_evidence_table.csv</a>.

5.  **Context products.** Depth, mechanism, migration, temporal concentration, and outer-band context were summarized in dedicated tables including <a href="<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/depth_summary_by_mainshock.csv" class="uri"><CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/depth_summary_by_mainshock.csv</a>, <a href="<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/mechanism_context_by_sequence.csv" class="uri"><CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/mechanism_context_by_sequence.csv</a>, <a href="<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/migration_diagnostics.csv" class="uri"><CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/migration_diagnostics.csv</a>, and <a href="<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/regional_outerband_metrics.csv" class="uri"><CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/regional_outerband_metrics.csv</a>.

# Mainshock matching and analysis frame

The mainshock-like event matching was reported as precise and unambiguous. According to the task analysis, the residuals were 0.01 s, 0.166 km, and 0.09 km for M1; 0.00 s, 0.297 km, and 0.04 km for M2; and 0.01 s, 0.158 km, and 0.09 km for M3. These small residuals support the validity of the mainshock-centered reference table and justify treating the subsequent relative-time and distance metrics as robust with respect to event association.

The principal diagnostic frame used throughout the report is the requested $`\pm 7`$ day, $`\leq 100`$ km window, because it provides the clearest direct comparison of short-window morphology around the three mainshocks. Broader windows ($`\pm 14`$ and $`\pm 25`$ days) were also computed and are used as robustness context rather than as the main figure set.

# Primary morphology results

<figure id="fig:morphology" data-latex-placement="H">
<img src="<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/magnitude_time_distance_pm7d_100km.png" style="width:98.0%" />
<figcaption>Mainshock-centered short-window morphology for M1, M2, and M3 in the requested <span class="math inline">±7</span> day and <span class="math inline"> ≤ 100</span> km frame. Left panels show magnitude versus relative time; right panels show distance to the mainshock versus relative time. This is the primary visual comparison figure for sequence morphology.</figcaption>
</figure>

<figure id="fig:m4plus" data-latex-placement="H">
<img src="<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/m4plus_sequence_views_pm7d_100km.png" style="width:98.0%" />
<figcaption>M4+ sequence views for the same <span class="math inline">±7</span> day and <span class="math inline"> ≤ 100</span> km frame. These panels emphasize the timing and distance structure of moderate and larger events and help distinguish companion-event organization from simple mainshock-aftershock patterns.</figcaption>
</figure>

The morphology figures show three clearly different sequence organizations.

#### M1.

M1 is the most compact and near-field dominated sequence. Within $`\pm 7`$ days and $`\leq 100`$ km, the diagnostic summary reports 567 pre-events and 1803 post-events, excluding the mainshock-like event, with 20 pre M4+ events and 55 post M4+ events. The same summary states a mainshock-minus-largest-companion magnitude gap of only 0.30 and six companion events within 1.0 magnitude unit. The visual pattern in Figure <a href="#fig:morphology" data-reference-type="ref" data-reference="fig:morphology">1</a> is therefore not that of a clean, isolated single-mainshock sequence; rather, it shows a compact cluster with dense post-mainshock activity superposed on already elevated pre-mainshock activity.

#### M2.

M2 shows the most spatially distributed post-mainshock response. In the same diagnostic frame, M2 has 40 pre-events and 3465 post-events, with 45 post M4+ events and no M4+ pre-events. Its post-window outer-band fraction is 0.82, indicating that most of the activity resides outside the 0–30 km near field. Figure <a href="#fig:morphology" data-reference-type="ref" data-reference="fig:morphology">1</a> and Figure <a href="#fig:m4plus" data-reference-type="ref" data-reference="fig:m4plus">2</a> together show that the sequence is dominated by a strong post-mainshock increase, but the response is regionally distributed rather than compactly centered on the mainshock.

#### M3.

M3 shows substantial post-mainshock activation but a more strongly hierarchical magnitude structure than M1. In the $`\pm 7`$ day, $`\leq 100`$ km frame, the diagnostic summary reports 201 pre-events and 2959 post-events, with 43 post M4+ events and no pre M4+ events in the compact summary file, although the supporting-metrics table reports one pre M4+ and one pre M5+ event. The mainshock-minus-largest-companion gap is 2.10, much larger than for M1 or M2. Thus M3 combines clear post-mainshock activation with strong single-mainshock dominance and only limited evidence for comparable large companions.

# Pre/post counts and distance-structure summaries

<figure id="fig:prepost" data-latex-placement="H">
<img src="<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/prepost_magnitude_distance_counts_pm7d_100km.png" style="width:98.0%" />
<figcaption>Supporting summary figure comparing pre/post magnitude-bin counts and distance-band counts for each mainshock in the <span class="math inline">±7</span> day, <span class="math inline"> ≤ 100</span> km frame. As specified in the workflow, this figure is used only as a summary of count changes and not as a standalone basis for inferring swarm-like organization or triggering style.</figcaption>
</figure>

<figure id="fig:distancebands" data-latex-placement="H">
<img src="<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/m4_m5_distance_band_contribution_pm7d_100km.png" style="width:98.0%" />
<figcaption>Distance-band contribution of M4+ and M5+ events across M1, M2, and M3. Raw counts and normalized fractions clarify whether moderate and larger events are near-field concentrated or distributed across the 30–60 km and 60–100 km bands. As with the workflow specification, this figure is interpreted jointly with time ordering and magnitude hierarchy rather than in isolation.</figcaption>
</figure>

Figure <a href="#fig:prepost" data-reference-type="ref" data-reference="fig:prepost">3</a> confirms that post counts exceed pre counts for all three mainshocks, but the spatial interpretation differs sharply by sequence. Figure <a href="#fig:distancebands" data-reference-type="ref" data-reference="fig:distancebands">4</a> makes the distance structure of moderate and larger events explicit:

- **M1** is near-field dominated. The task analysis reports post outer-band fractions of 0.210 for all events and 0.127 for post M4+ events, indicating that the large-event component remains strongly concentrated within 30 km.

- **M2** is outer-band dominated. The reported post outer-band fraction is 0.820 for all events and 0.911 for post M4+ events, making M2 the clearest example in which broader regional activation strongly contributes to the apparent sequence.

- **M3** is intermediate. The reported post outer-band fraction is 0.463, broader than M1 but markedly less distributed than M2.

These distance patterns are scientifically important, but the workflow explicitly cautioned that distance-band concentration alone must not be treated as evidence for swarm behavior, cascade, or migration. In this report, distance structure is therefore used jointly with timing and magnitude hierarchy.

# Quantitative evidence by behavior dimension

Table <a href="#tab:scores" data-reference-type="ref" data-reference="tab:scores">[tab:scores]</a> summarizes the behavior-dimension scores from the machine-readable evidence file. These are non-exclusive evidence levels rather than single sequence labels.

<div class="tabularx">

P1.4cmYYYYYYYY Mainshock & Aftershock response & Single-mainshock dominance & Compact cascade / compound structure & Swarm-like organization & Foreshock / pre-mainshock activation & Broader regional activation & Radial migration & Slow-slip candidate  
M1 & moderate & low & moderate & moderate & strong & low & low & low  
M2 & moderate & possible & low & possible & low & strong & low & low  
M3 & moderate & strong & low & possible & moderate & moderate & low & low  

</div>

## Aftershock response

All three sequences are scored as *moderate* aftershock response, but the supporting metrics show different styles.

- **M1:** post/pre ratio $`=3.174`$, M4+ post/pre ratio $`=2.619`$, near-field post fraction $`=0.790`$, and 38.3% of post events within 24 h.

- **M2:** post/pre ratio $`=86.625`$, near-field post fraction $`=0.180`$, and 26.6% of post events within 24 h. The M4+ post/pre ratio is undefined because the pre count is zero in this short window.

- **M3:** post/pre ratio $`=14.649`$, M4+ post/pre ratio $`=43.000`$, near-field post fraction $`=0.537`$, and 29.5% of post events within 24 h.

These metrics indicate that all three mainshocks triggered strong post-mainshock responses, but M1 concentrated that response much more locally, whereas M2 distributed it far more broadly across the 30–100 km bands.

## Magnitude hierarchy and companion-event structure

<figure id="fig:dominance" data-latex-placement="H">
<img src="<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/magnitude_dominance_companion_summary.png" style="width:92.0%" />
<figcaption>Magnitude-dominance and companion-event summary. This figure, together with the supporting tables, is central for distinguishing weak hierarchy with multiple comparable events from strong single-mainshock dominance.</figcaption>
</figure>

Magnitude hierarchy sharply separates M1 from M3, with M2 intermediate. At $`\pm 7`$ days and $`\leq 100`$ km, the task analysis reports:

- **M1:** mainshock magnitude 6.9; largest non-mainshock 6.6; dominance gap 0.3; two companions within 0.5 magnitude units and six within 1.0 magnitude unit.

- **M2:** mainshock magnitude 7.5; largest non-mainshock 6.9; dominance gap 0.6; no companions within 0.5 magnitude units and two within 1.0 magnitude unit.

- **M3:** mainshock magnitude 7.7; largest non-mainshock 5.6; dominance gap 2.1; no companions within either 0.5 or 1.0 magnitude units.

This evidence supports the score pattern in Table <a href="#tab:scores" data-reference-type="ref" data-reference="tab:scores">[tab:scores]</a>: M1 has *low* single-mainshock dominance and *moderate* compact/compound organization; M3 has *strong* single-mainshock dominance and *low* compact/compound organization; M2 remains intermediate and less cleanly categorized.

## Foreshock or pre-mainshock activation

The strongest contrast among the three sequences is in pre-mainshock activation.

- **M1: strong.** Supporting metrics report 21 pre M4+ events and 8 pre M5+ events within the matched frame, making M1 the clearest case of pronounced pre-mainshock activation.

- **M2: low.** M2 has no pre M4+ or pre M5+ events in the $`\pm 7`$ day, $`\leq 100`$ km window.

- **M3: moderate.** The scored table assigns M3 a moderate level based on one pre M4+ and one pre M5+ event and on broader contextual evidence, but this is less transparent than the M1 and M2 cases. The evaluation notes therefore correctly identify this as a lower-confidence aspect of the interpretation.

The practical implication is that M1 clearly evolved within an already active local environment, while M2 did not. M3 shows some pre-mainshock activity, but not a compelling short-window foreshock buildup on the scale seen for M1.

## Broader regional activation

Broader regional activation is one of the clearest quantitative distinctions among the sequences.

- **M1: low.** Pre outer-band fraction $`=0.107`$ and post outer-band fraction $`=0.210`$.

- **M2: strong.** Pre outer-band fraction $`=0.875`$, post outer-band fraction $`=0.820`$, and post M4+ outer-band fraction $`=0.911`$.

- **M3: moderate.** Post outer-band fraction $`=0.463`$.

Thus, M2 is the clearest example in which a mainshock-centered frame captures substantial regional participation rather than a purely local cluster, whereas M1 remains dominantly local and M3 occupies an intermediate position.

## Swarm-like or compound behavior

M1 is the strongest candidate for catalog-level swarm-like or compound organization, but the evidence remains interpretive rather than definitive. Its supporting metrics include a dominance gap of 0.300, 76 total M4+ events, 28 total M5+ events, and six companions within 1.0 magnitude unit. This combination indicates weak magnitude hierarchy and repeated moderate-to-large activity within a compact frame. In contrast, M2 and M3 are only scored *possible* for swarm-like organization. For M2, broad regional activation weakens a compact-swarm interpretation; for M3, strong single-mainshock dominance argues against it.

## Migration and slow-slip screening

All three sequences are scored *low* for radial migration or expansion, and also *low* for a slow-slip-related candidate interpretation. Reported distance-time Spearman values are weak (0.158 for M1, 0.071 for M2, and 0.149 for M3), and the migration diagnostics explicitly state that monotonic progression is not supported. The analysis therefore does not support any monotonic radial migration model. Likewise, slow-slip-related interpretation remains screening-level only and is not justified without geodetic, tremor, or ocean-bottom pressure evidence.

# Depth and mechanism context

Depth summaries indicate that the three sequences occupy different depth environments, although these results are better viewed as contextual than as decisive discriminants.

For the $`\pm 7`$ day window:

- **M1** all-event median depths are 12.02 km (pre) and 11.63 km (post), with M4+ medians of 13.69 km (pre) and 12.17 km (post).

- **M2** all-event median depths are 22.17 km (pre) and 18.92 km (post), with post M4+ median depth 20.0 km; no pre M4+ events are present in this short window.

- **M3** all-event median depths are 11.38 km (pre) and 13.19 km (post); the single pre M4+ event has depth 19.31 km.

These values show that M2 is generally deeper and more vertically dispersed than M1 and M3 in the short-window comparison.

Mechanism context provides only modest discriminating power. The mechanism summary reports 354 matched events for each mainshock-centered query and identical median plane-1 strike, dip, and rake values (188$`^{\circ}`$, 26$`^{\circ}`$, and 79$`^{\circ}`$) across M1, M2, and M3. However, the spatial partitioning of the mechanism-matched subset is still informative: near-field versus outer-band counts are 39 versus 27 for M1, 27 versus 202 for M2, and 8 versus 88 for M3. This pattern is consistent with the broader conclusion that M2 is much more outer-band dominated, but the identical median mechanism values mean that focal mechanisms mainly provide contextual support rather than strong sequence-specific separation.

# Window sensitivity and robustness

<figure id="fig:sensitivity" data-latex-placement="H">
<img src="<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/window_radius_sensitivity_heatmaps.png" style="width:98.0%" />
<figcaption>Sensitivity heatmaps summarizing matched-window metrics across the requested time windows and radii. These figures are used for robustness assessment rather than as the primary morphology classifier.</figcaption>
</figure>

<figure id="fig:robustness" data-latex-placement="H">
<img src="<CASE_ROOT>/run/02_2_behavior_diagnosis/exp_run/outputs/01_aomori_sequence_analysis/optional_window_robustness_comparison.png" style="width:90.0%" />
<figcaption>Optional robustness comparison figure summarizing changes when broader windows are considered.</figcaption>
</figure>

The broader-window products strengthen the comparative interpretation even though the report does not enumerate every metric. The key robust features are: M1 remains the most compact and weakly hierarchical sequence; M2 remains the most regionally distributed; and M3 remains the most strongly single-mainshock dominated. The main uncertainty under broader windows concerns the exact strength assigned to M3 pre-mainshock activation, because that score appears to depend on contextual evidence beyond the shortest diagnostic window.

# Integrated diagnosis by mainshock

## M1

M1 is best characterized as a compact, near-field dominated sequence with both strong pre-mainshock activation and a moderate post-mainshock response. Its very small dominance gap (0.3), multiple comparable companion events, and high counts of pre M4+ and pre M5+ events argue against a simple isolated single-mainshock-aftershock sequence. The most defensible diagnosis is therefore a combination of moderate aftershock response, moderate compound or swarm-like organization, and strong pre-mainshock activation, embedded only weakly in broader regional activation. There is no evidence for monotonic migration or a slow-slip-like pattern.

## M2

M2 is best characterized as a strong post-mainshock activation episode with substantial regional participation. It has the largest post/pre ratio, but its near-field post fraction is low and its outer-band contribution is dominant, including for M4+ events. This makes M2 the clearest case where local sequence behavior must be separated from broader regional activation. It is only weakly supported as compact or swarm-like, and it shows little evidence of foreshock-style pre-mainshock activation in the short diagnostic window.

## M3

M3 is best characterized as a strongly mainshock-dominated sequence with substantial post-mainshock activation and moderate regional breadth. Its large dominance gap (2.1) and absence of comparable companions distinguish it sharply from M1. The sequence is broader in space than M1 but much less regionally distributed than M2. The assigned moderate pre-mainshock activation score should be treated cautiously because the short-window evidence is limited; nevertheless, the broader diagnosis of strong mainshock dominance plus moderate post-mainshock response is well supported.

# Limitations and evaluation

This report follows the explicit limitations recorded in the project evidence package.

1.  **Catalog-only diagnosis.** The sequence interpretations are based primarily on catalog morphology and matched-window counts. Swarm-like organization does not prove a physical swarm process, and post/pre changes can be inflated by sequence overlap or detectability changes.

2.  **No formal background-rate modeling.** The workflow did not fit ETAS, Omori, or alternative background-rate models. This is sufficient for comparative characterization but limits causal discrimination among aftershock decay, compound sequence behavior, and regional triggering.

3.  **Overlapping frames.** The mainshock-centered windows overlap in time and space, especially for M1 pre-activity and for M2/M3 outer-band interpretations. Some apparent pre/post contrasts therefore mix local sequence behavior with neighboring activation.

4.  **Undefined or unstable ratios.** Some short-window ratios are undefined or unstable when pre counts are zero, especially for M2 M4+ metrics. The report therefore relies on multiple complementary metrics rather than on ratios alone.

5.  **Mechanism context has limited separation power.** Mechanism summaries provide contextual support but only weak sequence-specific discrimination because the median mechanism values are identical across the three sequences.

6.  **Moderate confidence.** The evaluation metadata classifies the delivery as complete and satisfactory, with overall scientific confidence rated as moderate.

# Conclusions

The Aomori catalog supports a clear comparative diagnosis of three distinct mainshock-centered sequence styles. M1 is the most compact and near-field concentrated sequence but is weakly single-mainshock dominated and shows the strongest pre-mainshock activation, making it the most plausible candidate for compact multi-large-event or swarm-like catalog organization. M2 shows the strongest broader regional activation and the most spatially distributed post-mainshock response, so its mainshock-centered frame should not be interpreted as a purely local aftershock cloud. M3 is the most strongly single-mainshock dominated sequence, with substantial post-mainshock activation but far fewer comparable large companions than M1. Across all three, the catalog evidence does not support monotonic radial migration or a slow-slip-like interpretation.

The final interpretation is therefore comparative and multi-dimensional: all three sequences exhibit post-mainshock activation, but they differ fundamentally in compactness, magnitude hierarchy, pre-mainshock buildup, and the extent to which the observed seismicity reflects local sequence behavior versus broader regional activation.
