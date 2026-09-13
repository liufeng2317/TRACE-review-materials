"""Apply the documented expert post-processing to the JMA arrival catalog.

The authoritative source is the legacy travel-time workflow under
``examples/japan_aomori/data_downloading/travel_time``.  This step reproduces
its fixed-width parser and regional export, while retaining the complete
arrival table for events with a reported magnitude.
"""

from __future__ import annotations

import importlib
import json
import re
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[7]
SOURCE_ROOT = Path("<TRAVEL_TIME_SOURCE_ROOT>").resolve()
RAW_DIR = SOURCE_ROOT / "data" / "raw"
STATION_FILE = SOURCE_ROOT / "docs" / "station.txt"
OUTPUT_DIR = SCRIPT_DIR / "outputs"

START_DAY = "20250601"
END_DAY = "20260501"
LAT_MIN, LAT_MAX = 38.5, 42.5
LON_MIN, LON_MAX = 141.0, 144.5
DEPTH_MIN_KM, DEPTH_MAX_KM = 0.0, 200.0


def select_article_files() -> list[Path]:
    """Select five-day files through 2026-04-30 and the one-day 2026-05-01 file."""

    selected: list[Path] = []
    for path in sorted(RAW_DIR.glob("measure_*.txt")):
        match = re.fullmatch(r"measure_(\d{8})_(\d+)\.txt", path.name)
        if not match:
            continue
        day, span = match.groups()
        if day < END_DAY or (day == END_DAY and span == "1"):
            selected.append(path)
    return selected


def main() -> None:
    SOURCE_ROOT_STR = str(SOURCE_ROOT)
    if SOURCE_ROOT_STR not in sys.path:
        sys.path.insert(0, SOURCE_ROOT_STR)
    parser = importlib.import_module("parse")

    files = select_article_files()
    start = parser.parse_filter_date(START_DAY)
    end_exclusive = parser.parse_filter_date(END_DAY, is_end=True)
    parsed_events = parser.parse_files(files, "raw")
    regional_events = [
        event
        for event in parsed_events
        if parser.keep_event(
            event,
            start=start,
            end_exclusive=end_exclusive,
            min_picks=1,
            lat_min=LAT_MIN,
            lat_max=LAT_MAX,
            lon_min=LON_MIN,
            lon_max=LON_MAX,
        )
    ]
    magnitude_events = [
        event for event in regional_events if event.magnitude is not None
    ]
    expert_events = [
        event
        for event in magnitude_events
        if event.depth_km is not None
        and DEPTH_MIN_KM <= event.depth_km <= DEPTH_MAX_KM
    ]
    parser.reindex_events(expert_events)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    station_metadata = parser.load_station_metadata(STATION_FILE)
    parser.write_events_csv(expert_events, OUTPUT_DIR / "events.csv")
    parser.write_picks_csv(expert_events, OUTPUT_DIR / "picks.csv")
    parser.write_phase_dat(expert_events, OUTPUT_DIR / "phase.dat")
    parser.write_station_sta(
        expert_events, station_metadata, OUTPUT_DIR / "station.sta"
    )

    picks = [pick for event in expert_events for pick in event.picks]
    p_count = sum(pick.p_time != parser.MISSING for pick in picks)
    s_count = sum(pick.s_time != parser.MISSING for pick in picks)
    both_count = sum(
        pick.p_time != parser.MISSING and pick.s_time != parser.MISSING
        for pick in picks
    )
    weight_counts: dict[str, int] = {}
    for pick in picks:
        key = f"{pick.weight:g}"
        weight_counts[key] = weight_counts.get(key, 0) + 1

    summary = {
        "source": {
            "workflow": "examples/japan_aomori/data_downloading/travel_time",
            "raw_file_count": len(files),
        },
        "processing": [
            "Parse the selected JMA fixed-width measure files with the legacy project parser.",
            "Restrict event origin times to 2025-06-01 through 2026-05-01 inclusive in Japan Standard Time.",
            "Restrict hypocenters to 38.5-42.5 degrees north and 141.0-144.5 degrees east.",
            "Keep events with a reported magnitude; no additional magnitude threshold is applied.",
            "Keep events with a physical hypocentral depth from 0.0 through 200.0 km.",
            "Retain all parsed P/S arrivals, including records with JMA weight 0.",
            "Export the canonical events.csv, picks.csv, phase.dat, and station.sta products.",
        ],
        "counts": {
            "parsed_events": len(parsed_events),
            "regional_events_before_magnitude_filter": len(regional_events),
            "excluded_missing_magnitude_events": len(regional_events) - len(magnitude_events),
            "excluded_invalid_depth_events": len(magnitude_events) - len(expert_events),
            "events": len(expert_events),
            "picks": len(picks),
            "stations": len(
                {(pick.station_code, pick.station_number) for pick in picks}
            ),
            "p_pick_count": p_count,
            "s_pick_count": s_count,
            "both_p_and_s_count": both_count,
            "jma_weight_counts": weight_counts,
        },
        "criteria": {
            "start_day_inclusive": START_DAY,
            "end_day_inclusive": END_DAY,
            "latitude_inclusive": [LAT_MIN, LAT_MAX],
            "longitude_inclusive": [LON_MIN, LON_MAX],
            "magnitude": "reported magnitude required",
            "depth_km_inclusive": [DEPTH_MIN_KM, DEPTH_MAX_KM],
            "weight": "preserved as parsed; weight 0 is retained",
        },
        "outputs": [
            "events.csv",
            "picks.csv",
            "phase.dat",
            "station.sta",
            "expert_processing_summary.json",
        ],
    }
    with (OUTPUT_DIR / "expert_processing_summary.json").open(
        "w", encoding="utf-8"
    ) as handle:
        json.dump(summary, handle, indent=2)


if __name__ == "__main__":
    main()
