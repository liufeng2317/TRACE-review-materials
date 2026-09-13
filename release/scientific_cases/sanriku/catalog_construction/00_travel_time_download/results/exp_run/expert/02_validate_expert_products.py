"""Validate products produced by the expert arrival post-processing step."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


SCRIPT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = SCRIPT_DIR / "outputs"


def main() -> None:
    events = pd.read_csv(OUTPUT_DIR / "events.csv")
    picks = pd.read_csv(OUTPUT_DIR / "picks.csv")
    stations = pd.read_csv(OUTPUT_DIR / "station.sta")
    phase_lines = (OUTPUT_DIR / "phase.dat").read_text(encoding="utf-8").splitlines()

    event_ids = set(events["event_id"])
    pick_event_ids = set(picks["event_id"])
    event_lines = [line for line in phase_lines if len(line.split(",")) == 6]
    pick_lines = [line for line in phase_lines if len(line.split(",")) == 5]
    checks = [
        {
            "check": "event_ids_unique",
            "passed": events["event_id"].is_unique,
            "value": int(events["event_id"].nunique()),
        },
        {
            "check": "event_pick_foreign_key",
            "passed": pick_event_ids.issubset(event_ids),
            "value": len(pick_event_ids - event_ids),
        },
        {
            "check": "jma_weight_values_preserved",
            "passed": picks["weight"].notna().all() and (picks["weight"] >= 0).all(),
            "value": sorted(picks["weight"].unique().tolist()),
        },
        {
            "check": "regional_bounds",
            "passed": events["latitude"].between(38.5, 42.5).all()
            and events["longitude"].between(141.0, 144.5).all(),
            "value": f"{events['latitude'].min():.6f}-{events['latitude'].max():.6f}; {events['longitude'].min():.6f}-{events['longitude'].max():.6f}",
        },
        {
            "check": "physical_depth_range",
            "passed": events["depth_km"].between(0.0, 200.0).all(),
            "value": f"{events['depth_km'].min():.3f}-{events['depth_km'].max():.3f} km",
        },
        {
            "check": "phase_event_count",
            "passed": len(event_lines) == len(events),
            "value": len(event_lines),
        },
        {
            "check": "phase_pick_count",
            "passed": len(pick_lines) == len(picks),
            "value": len(pick_lines),
        },
        {
            "check": "station_coverage",
            "passed": set(picks["station_code"]).issubset(set(stations["station_code"])),
            "value": len(set(picks["station_code"])),
        },
    ]
    checks_frame = pd.DataFrame(checks)
    checks_frame.to_csv(OUTPUT_DIR / "expert_validation.csv", index=False)
    result = {
        "passed": bool(checks_frame["passed"].all()),
        "event_count": len(events),
        "pick_count": len(picks),
        "station_count": len(stations),
        "checks": "expert/outputs/expert_validation.csv",
    }
    with (OUTPUT_DIR / "expert_validation.json").open("w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2)


if __name__ == "__main__":
    main()
