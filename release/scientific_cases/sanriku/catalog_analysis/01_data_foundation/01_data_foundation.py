import os
import sys
sys.path.append("<REPO_ROOT>/")
from seismoagent.runing import run_seismoagent

user_request = """
You are an earthquake scientist and data-analysis agent.

Goal:
Build a reliable data foundation, characterize the regional seismicity background, generate publication-quality diagnostic figures, and prepare reusable data products for further sequence analysis.

Data folder:
"<CASE_ROOT>/data"

Files:
- catalog/Snet_catalog_relocate.csv
- catalog/main_earthquake.csv
- source_mechanism/Snet_mecha.csv
- stations/station.sta

Tasks:

1. Data audit and cleaning
Inspect all files for schema, record count, time/location/depth/magnitude ranges, missing values, duplicates, abnormal values, and usable fields.
Create a clean Stage-1 catalog with parsed time, latitude, longitude, depth, magnitude, event ID if available, and quality flags.

2. Major-earthquake matching
Match the major earthquakes in main_earthquake.csv with the regional catalog (a very small time shift caused by relocation).
For each major earthquake, report the nearest matched catalog event, time difference, spatial distance, depth difference, magnitude difference, and match confidence.

3. Regional seismicity background
Characterize the regional catalog in terms of:
- spatial distribution and event density
- temporal activity rate
- magnitude distribution
- depth distribution and depth segmentation
- magnitude-depth relationship
- preliminary completeness magnitude Mc and b-value (estimated with Gutenberg-Richter law)
- station distribution and simple coverage metrics
- focal-mechanism feature and distribution

4. Mainshock regional context
For each major earthquake, summarize its regional context:
- local event density
- surrounding depth distribution
- nearby station distribution and coverage
- nearby focal-mechanism distribution and availability
- whether the event lies in a distinct spatial/depth domain
- whether later sequence analysis should use special radius, depth, or magnitude thresholds

5. Diagnostic figures
Generate **Nature-Style** publication-quality figures
- regional map of earthquakes, major earthquakes, stations, and focal mechanisms if available
- time–magnitude plot
- depth–time plot
- magnitude–depth plot
- magnitude-frequency / Mc plot / b-value plot
- spatial event-density or cluster diagnostic
- depth-distribution or cross-section diagnostic
- station coverage diagnostic
- focal-mechanism distribution and availability diagnostic
- other useful regional-background plots that support further sequence analysis and hypothesis testing

Figures should use clear labels, units, legends, readable fonts, appropriate color scales, and should be saved as high-resolution PNG.

6. Candidate patterns estimation
Identify compact, testable candidate patterns for further sequence analysis and hypothesis testing, such as:
- spatial clusters
- temporal bursts or quiet periods
- depth segmentation
- magnitude-depth-space relationships
- station-coverage effects
- focal-mechanism data gaps
- regional differences around the major earthquakes

"""
if __name__ == "__main__":

    run_name = "01_data_foundation"
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
        enable_trajectory=True
    )
