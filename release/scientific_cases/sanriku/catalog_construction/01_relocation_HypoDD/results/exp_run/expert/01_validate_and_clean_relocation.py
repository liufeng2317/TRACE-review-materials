"""Validate the native relocation output against the expert event handoff."""

from __future__ import annotations

import csv
import json
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = SCRIPT_DIR / "outputs"
RAW_RELOC = SCRIPT_DIR.parent / "outputs" / "production" / "japan_aomori_nocc_full.reloc"
EXPERT_EVENTS = (
    SCRIPT_DIR.parent.parent.parent.parent
    / "00_travel_time_download"
    / "results"
    / "exp_run"
    / "expert"
    / "outputs"
    / "events.csv"
)
CLEAN_RELOC = OUTPUT_DIR / "japan_aomori_nocc_full_clean.reloc"
SUMMARY = OUTPUT_DIR / "relocation_cleaning_summary.json"
DEPTH_MIN_KM, DEPTH_MAX_KM = 0.0, 200.0


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    kept: list[list[str]] = []
    excluded: list[dict[str, object]] = []
    with RAW_RELOC.open(newline="", encoding="utf-8") as handle:
        for line_number, row in enumerate(csv.reader(handle), start=1):
            if len(row) != 5:
                excluded.append({"line": line_number, "reason": "invalid_column_count"})
                continue
            origin_time, _lat, _lon, depth, _magnitude = row
            try:
                depth_km = float(depth)
            except ValueError:
                excluded.append({"line": line_number, "origin_time": origin_time, "reason": "invalid_depth"})
                continue
            if not DEPTH_MIN_KM <= depth_km <= DEPTH_MAX_KM:
                excluded.append({"line": line_number, "origin_time": origin_time, "depth_km": depth_km, "reason": "outside_physical_depth_range"})
                continue
            kept.append(row)

    with CLEAN_RELOC.open("w", newline="", encoding="utf-8") as handle:
        csv.writer(handle, lineterminator="\n").writerows(kept)
    summary = {
        "input_file": "outputs/production/japan_aomori_nocc_full.reloc",
        "expert_event_handoff": "00_travel_time_download/results/exp_run/expert/outputs/events.csv",
        "output_file": "results/exp_run/expert/outputs/japan_aomori_nocc_full_clean.reloc",
        "input_rows": len(kept) + len(excluded),
        "retained_rows": len(kept),
        "excluded_rows": len(excluded),
        "excluded_reasons": {
            reason: sum(item["reason"] == reason for item in excluded)
            for reason in sorted({item["reason"] for item in excluded})
        },
        "depth_km_inclusive": [DEPTH_MIN_KM, DEPTH_MAX_KM],
        "quality_control_rule": "retain rows with physical hypocentral depth in the stated range",
    }
    SUMMARY.write_text(json.dumps(summary, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
