#!/usr/bin/env python3
"""Run the reproducible full-window Japan Aomori HypoDD relocation."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[6]
PACKAGE_ROOT = REPO_ROOT / "seismoagent" / "library" / "basic_fun" / "HypoDD"
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from hypodd_runner import build_hypodd_inputs, run_catalog_only_auto_time_windows


DATA_DIR = (
    REPO_ROOT
    / "examples"
    / "japan_aomori"
    / "catalog_construction_from_JMA"
    / "data"
    / "hypodd_info"
)
OUTPUT_DIR = (
    REPO_ROOT
    / "examples"
    / "japan_aomori"
    / "catalog_construction_from_JMA"
    / "run"
    / "01_relocation_HypoDD"
    / "exp_run"
    / "outputs"
    / "01_hypodd_catalog_only_relocation"
    / "production"
)
INPUT_DIR = OUTPUT_DIR.parent / "inputs"
HYPODD_ROOT = (
    REPO_ROOT.parent
    / "software"
    / "hypoDD"
    / "HYPODD"
    / "src"
)

CATALOG_CODE = "japan_aomori_nocc_full"
OT_RANGE = ("2025-06-01", "2026-05-01")
LAT_RANGE = (38.5, 42.5)
LON_RANGE = (141.0, 144.5)

PH2DT_KWARGS = {
    "minwght": 0.0,
    "maxdist": 180.0,
    "maxoffset": 20.0,
    "mnb": 12,
    "limobs_pair": 8,
    "minobs_pair": 6,
    "maxobs_pair": 40,
}
HYPODD_ITER_ROWS = (
    (8, -9.0, -9.0, -9.0, -9.0, 1.0, 0.7, 0.03, 8.0, 120.0),
    (12, -9.0, -9.0, -9.0, -9.0, 0.7, 0.3, 0.02, 5.0, 80.0),
)
VELOCITY_TOP_KM = (0.0, 5.0, 10.0, 20.0, 35.0, 50.0, 90.0)
VELOCITY_VP_KM_S = (5.4, 5.8, 6.2, 6.6, 7.2, 7.6, 8.05)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    built = build_hypodd_inputs(
        events_csv=str(DATA_DIR / "events.csv"),
        picks_csv=str(DATA_DIR / "picks.csv"),
        stations_csv=str(DATA_DIR / "station.sta"),
        output_dir=str(INPUT_DIR),
    )
    print(
        f"Prepared {built.event_count} events, {built.pick_row_count} picks, "
        f"and {built.station_count} stations."
    )

    result = run_catalog_only_auto_time_windows(
        time_window_base="month",
        min_events_per_window=100,
        max_events_per_window=10800,
        clean_output=True,
        allow_partial=False,
        num_window_workers=1,
        hypo_root=str(HYPODD_ROOT),
        phase_file=built.phase_path,
        station_file=built.station_path,
        output_folder=str(OUTPUT_DIR),
        catalog_code=CATALOG_CODE,
        phase_format="auto",
        dep_corr=0.0,
        ot_range=OT_RANGE,
        lat_range=LAT_RANGE,
        lon_range=LON_RANGE,
        num_grids=(1, 1),
        xy_pad=(0.0, 0.0),
        num_workers=1,
        keep_grids=True,
        ph2dt_minwght=PH2DT_KWARGS["minwght"],
        ph2dt_maxdist=PH2DT_KWARGS["maxdist"],
        ph2dt_maxoffset=PH2DT_KWARGS["maxoffset"],
        ph2dt_mnb=PH2DT_KWARGS["mnb"],
        ph2dt_limobs_pair=PH2DT_KWARGS["limobs_pair"],
        ph2dt_minobs_pair=PH2DT_KWARGS["minobs_pair"],
        ph2dt_maxobs_pair=PH2DT_KWARGS["maxobs_pair"],
        hypodd_idata=2,
        hypodd_iphase=3,
        hypodd_maxdist=180.0,
        hypodd_minobs_cc=0,
        hypodd_minobs_ct=0,
        hypodd_istart=2,
        hypodd_isolv=2,
        hypodd_iter_rows=HYPODD_ITER_ROWS,
        vp_vs_ratio=1.73,
        velocity_model_top_km=VELOCITY_TOP_KM,
        velocity_model_vp_km_s=VELOCITY_VP_KM_S,
        hypodd_iclust=0,
    )
    print(f"Input events: {result.total_input_events}")
    print(f"Successful windows: {result.success_batches}")
    print(f"Failed windows: {result.failed_batches}")
    print(f"Initial locations: {result.merged_loc_path}")
    print(f"Relocated catalog: {result.merged_reloc_path}")
    print(f"Residuals: {result.merged_residual_path}")
    print(f"Window status: {result.batch_status_csv}")
    print(f"Window manifest: {result.manifest_path}")


if __name__ == "__main__":
    main()
