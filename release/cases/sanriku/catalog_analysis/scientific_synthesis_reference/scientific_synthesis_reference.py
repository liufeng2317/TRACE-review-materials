"""Run scientific synthesis preflight for the Japan Aomori example.

This script intentionally uses three explicit completed run roots. It does not
scan the whole run/ directory and does not read run/bak/.
"""

from __future__ import annotations
import sys
from pathlib import Path

sys.path.append("<REPO_ROOT>/")
from seismoagent.runing import run_scientific_synthesis

EXAMPLE_DIR = Path(__file__).resolve().parents[2]
RUN_DIR = EXAMPLE_DIR / "run"
OUTPUT_DIR = RUN_DIR / "scientific_synthesis_ref-v1"
REFERENCE_PAPERS_DIR = EXAMPLE_DIR / "reference"

RUNS = [
    RUN_DIR / "01_data_foundation",
    RUN_DIR / "02_1_sequence_response",
    RUN_DIR / "02_2_behavior_diagnosis",
    RUN_DIR / "02_3_relationship_screening",
    RUN_DIR / "02_4_bg_rate_correction",
    RUN_DIR / "03_1A_event_chain_and_bursts",
    RUN_DIR / "03_1B_spatial_depth_migration",
    RUN_DIR / "03_1C_mechanism_screening",
    RUN_DIR / "03_1D_catalog_statistic_model_check"
]

user_request = """
Focus the synthesis on the evolutionary relationship between the M1 and M3 earthquakes in the recent Aomori M7.7-area sequence.

Build a coherent scientific story for the regional seismicity evolution around the M1 and M3 earthquakes.

Use the available evidence to connect background seismicity, M1/M3 local activation, event-chain or burst behavior, spatial and depth evolution, focal-mechanism context, and background-rate/statistical checks.

For the most evidence-supported M1-M3 interpretation, identify supporting evidence, weakening or non-comparable evidence, and external validation needed to distinguish tectonic linkage, aftershock triggering, regional activation, migration-like behavior, or catalog/observational bias.
"""


def main() -> None:
    reference_papers = sorted(
        str(path)
        for path in REFERENCE_PAPERS_DIR.iterdir()
        if path.is_file() and path.suffix.lower() == ".pdf"
    )
    if not reference_papers:
        raise FileNotFoundError(f"No PDF reference papers found in {REFERENCE_PAPERS_DIR}")

    run_scientific_synthesis(
        runs=[str(path) for path in RUNS],
        synthesis_request=user_request,
        output_dir=str(OUTPUT_DIR),
        papers=reference_papers,
        use_mineru_for_papers=True,
    )


if __name__ == "__main__":
    main()
