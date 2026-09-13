import os
import sys
sys.path.append("<REPO_ROOT>/")
from seismoagent.runing import run_seismoagent

user_request = """
You are an earthquake scientist and data-analysis agent.

Current task:
Investigate whether the M1, M2, and M3 earthquake clusters in the Aomori catalog show catalog-level relationships that are worth further scientific investigation.

Goal:
Use quantitative relationship analyses to evaluate whether these clusters are independent, weakly related, pairwise linked, part of a broader regional activation episode, or only apparently related because of burst-like background seismicity and analysis-window choices.

The purpose is not to prove triggering or a physical mechanism from the catalog alone.
The purpose is to identify which relationship hypotheses are supported, which are weak or unresolved, and which deserve follow-up with waveform, relocation, focal-mechanism, geodetic, ocean-bottom pressure, or stress-modeling analyses.

Data folder:
"<CASE_ROOT>/data"

Primary inputs:
- catalog/Snet_catalog_relocate_250930_260501.csv
- catalog/main_earthquake.csv

Context inputs:
- source_mechanism/Snet_mecha.csv
- stations/station.sta

Previous working conclusions:
- M1 is compact and near-field dominated, with weak single-mainshock dominance, strong pre-mainshock activation, and compound/swarm-like catalog organization.
- M2 shows the strongest post-mainshock activation jump, but much of its M4+/M5+ activity is distributed in the 30-100 km outer bands.
- M3 is the most strongly single-mainshock-dominated sequence, with substantial post-mainshock activation and fewer comparable companion events.
- These are catalog-level interpretations, not causal conclusions.

Core scientific question:
Do the M1, M2, and M3 clusters show meaningful catalog-level relationships, and if so, which relationship hypotheses should be prioritized for deeper physical analysis?

Candidate relationship hypotheses:
- independent local clusters
- overlapping activation zones
- delayed activation between clusters
- linked local fault-system activation
- corridor-like migration or expansion
- broader regional activation
- compound/swarm-like multi-event clustering
- apparent relationship caused by burst-like background seismicity or window choices

These are candidate hypotheses, not a closed list. The agent may propose additional relationship patterns if supported by the data.

Analysis principles:

1. Treat M1-M2, M1-M3, and M2-M3 symmetrically at first.
Evaluate all three pairwise relationships using comparable metrics before deciding which pair deserves focused interpretation.
Do not assume in advance that M1-M3, or any other pair, is the strongest relationship.

2. Use event-level relationship evidence.
For relevant M3+, M4+, M5+, and M6+ events, evaluate relative time, distance, azimuth, depth, distance band, nearest mainshock, and pairwise corridor position.

3. Preserve ambiguity.
Do not force every event into a single mainshock sequence.
Allow categories such as:
- uniquely associated with one cluster
- shared or overlapping
- corridor-like
- endpoint-centered
- outer-cluster
- regional/background
- unresolved

4. Use distance-aware interpretation.
Spatial distance is a primary evidence axis, not just background information.
For each pair, evaluate whether the epicentral separation, depth difference, and time separation are compatible with:
- local cluster linkage
- delayed activation between nearby source regions
- broader regional activation
- only regional-scale or apparent association.

Keep raw catalog evidence, control-corrected evidence, and distance-aware plausibility separate.
Do not rank a pair as high-priority based only on short time separation, raw post/pre ratio, or corridor fraction.
If raw evidence conflicts with control-corrected or distance-aware evidence, emphasize the corrected interpretation.

5. Let the agent design appropriate diagnostics.
Use standard earthquake-sequence and cluster-association methods where useful, such as:
- pairwise geometry and time separation
- intervening-event counts and rates
- M4+/M5+/M6+ event-chain analysis
- distance-time and projection analysis
- corridor versus off-corridor comparison
- nearest-mainshock and ambiguity-aware event assignment
- raw versus relationship-corrected sequence metrics
- simple background, random-window, or pseudo-corridor controls

Figures:
Generate a compact set of high-value diagnostic figures, not exhaustive plots.
Useful figure types may include:
- pairwise relationship overview map
- pairwise time-distance or corridor-projection plots
- M4+/M5+ intervening-event chain comparison
- event-association or ambiguity map
- corridor versus off-corridor comparison
- relationship hypothesis evidence matrix
- priority ranking for next physical verification

Design additional figures only if they directly clarify the relationship hypotheses.

Final report:
Provide a concise scientific report with:
- pairwise relationship evidence summary for M1-M2, M1-M3, and M2-M3
- relationship evidence matrix across all hypotheses
- evidence level for each pair-hypothesis combination: low, possible, moderate, or strong
- follow-up priority for each hypothesis: low, medium, or high
- strongest supported relationship signals
- weak, negative, or unresolved evidence
- separate raw catalog evidence, control-corrected evidence, and distance-aware plausibility for each pair
- recommended next research directions and required external data/modeling

Important:
Do not infer physical triggering from temporal order or spatial proximity alone.
Treat all relationship categories as catalog-level hypotheses.
Clearly separate raw mainshock-centered metrics from relationship-aware or corrected metrics.
Report both supporting and contradicting evidence.
Prioritize identifying promising scientific directions rather than forcing one causal story.
"""

if __name__ == "__main__":

    run_name = "02_3_relationship_screening"
    output_dir = "<CASE_ROOT>/run"
    reference_papers_dir = "<CASE_ROOT>/docs/reference"
    reference_papers = os.listdir(reference_papers_dir)
    reference_papers = [os.path.join(reference_papers_dir, paper) for paper in reference_papers if paper.endswith(".pdf")]

    run_seismoagent(
        request=user_request,
        run_name=run_name,
        output_dir=output_dir,
        disable_refinement=False,
        max_refinement_rounds=3,
        enable_trajectory=True,
        # resume=os.path.join(output_dir, run_name),
        # resume_stage="coding",
        # resume_coding_step=3
    )
