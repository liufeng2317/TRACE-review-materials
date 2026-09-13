#!/usr/bin/env python3
"""Filter the full repeat-earthquake run to the manuscript analysis window."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


SCRIPT_DIR = Path(__file__).resolve().parent
RUN_DIR = SCRIPT_DIR.parents[0]
OUTPUTS_DIR = RUN_DIR / "outputs"
SOURCE_DIR = OUTPUTS_DIR / "01_repeat_event_analysis"
TARGET_DIR = OUTPUTS_DIR / "manuscript_aligned"

START = pd.Timestamp("2025-11-01 00:00:00")
END = pd.Timestamp("2025-12-07 00:00:00")
MAX_MAGNITUDE_DIFF = 0.8
MAX_EPICENTRAL_DISTANCE_KM = 5.0
MIN_COMMON_COMPONENTS = 40
HIGH_CONFIDENCE_CC = 0.70


def in_window(df: pd.DataFrame) -> pd.Series:
    return (
        df["origin_time_1"].between(START, END, inclusive="left")
        & df["origin_time_2"].between(START, END, inclusive="left")
    )


def build_families(pairs: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    high = pairs[
        pairs["repeat_candidate_level"].eq("high_confidence")
        & pairs["median_cc"].ge(HIGH_CONFIDENCE_CC)
    ].copy()
    parent: dict[str, str] = {}

    def find(x: str) -> str:
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: str, b: str) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    for row in high.itertuples(index=False):
        union(str(row.event_id_1), str(row.event_id_2))

    groups: dict[str, list[str]] = {}
    for event_id in parent:
        groups.setdefault(find(event_id), []).append(event_id)
    groups = {root: sorted(ids) for root, ids in groups.items() if len(ids) >= 2}
    ordered = sorted(groups.values(), key=lambda ids: (ids[0], len(ids)))
    family_map = {
        event_id: f"F{index:03d}"
        for index, ids in enumerate(ordered, start=1)
        for event_id in ids
    }

    members = []
    for event_id, family_id in family_map.items():
        row = high[
            (high["event_id_1"].astype(str) == event_id)
            | (high["event_id_2"].astype(str) == event_id)
        ].iloc[0]
        if str(row.event_id_1) == event_id:
            suffix = "1"
        else:
            suffix = "2"
        members.append(
            {
                "family_id": family_id,
                "event_id": event_id,
                "origin_time": row[f"origin_time_{suffix}"],
                "latitude": row[f"latitude_{suffix}"],
                "longitude": row[f"longitude_{suffix}"],
                "depth_km": row[f"depth_km_{suffix}"],
                "magnitude": row[f"magnitude_{suffix}"],
            }
        )
    members_df = pd.DataFrame(members)

    family_rows = []
    for family_id, sub in members_df.groupby("family_id", sort=True):
        ids = set(sub["event_id"].astype(str))
        edges = high[
            high["event_id_1"].astype(str).isin(ids)
            & high["event_id_2"].astype(str).isin(ids)
        ]
        family_rows.append(
            {
                "family_size": len(sub),
                "num_edges": len(edges),
                "start_time": sub["origin_time"].min(),
                "end_time": sub["origin_time"].max(),
                "duration_days": (
                    sub["origin_time"].max() - sub["origin_time"].min()
                ).total_seconds()
                / 86400.0,
                "median_pair_cc": edges["median_cc"].median(),
                "max_pair_cc": edges["median_cc"].max(),
                "magnitude_min": sub["magnitude"].min(),
                "magnitude_max": sub["magnitude"].max(),
                "latitude_min": sub["latitude"].min(),
                "latitude_max": sub["latitude"].max(),
                "longitude_min": sub["longitude"].min(),
                "longitude_max": sub["longitude"].max(),
                "family_id": family_id,
            }
        )
    return pd.DataFrame(family_rows), members_df


def main() -> None:
    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    candidates = pd.read_csv(
        SOURCE_DIR / "candidate_event_pairs.csv",
        dtype={"event_id_1": str, "event_id_2": str},
        parse_dates=["origin_time_1", "origin_time_2"],
        low_memory=False,
    )
    pairs = pd.read_csv(
        SOURCE_DIR / "repeat_event_pairs.csv",
        dtype={"event_id_1": str, "event_id_2": str},
        parse_dates=["origin_time_1", "origin_time_2"],
        low_memory=False,
    )
    candidate_mask = (
        in_window(candidates)
        & candidates["magnitude_diff"].le(MAX_MAGNITUDE_DIFF)
        & candidates["epicentral_distance_km"].le(MAX_EPICENTRAL_DISTANCE_KM)
        & candidates["common_station_components"].ge(MIN_COMMON_COMPONENTS)
    )
    pair_mask = (
        in_window(pairs)
        & pairs["magnitude_diff"].le(MAX_MAGNITUDE_DIFF)
        & pairs["epicentral_distance_km"].le(MAX_EPICENTRAL_DISTANCE_KM)
        & pairs["common_station_components"].ge(MIN_COMMON_COMPONENTS)
    )
    candidates = candidates.loc[candidate_mask].copy()
    pairs = pairs.loc[pair_mask].copy()
    pairs["repeat_candidate_level"] = "background"
    pairs.loc[pairs["median_cc"].ge(0.55), "repeat_candidate_level"] = "loose"
    pairs.loc[pairs["median_cc"].ge(HIGH_CONFIDENCE_CC), "repeat_candidate_level"] = (
        "high_confidence"
    )
    families, members = build_families(pairs)

    candidates.to_csv(TARGET_DIR / "candidate_event_pairs.csv", index=False)
    pairs.to_csv(TARGET_DIR / "repeat_event_pairs.csv", index=False)
    families.to_csv(TARGET_DIR / "repeat_event_families.csv", index=False)
    members.to_csv(TARGET_DIR / "repeat_family_members.csv", index=False)
    summary = {
        "source_result_set": str(SOURCE_DIR.relative_to(RUN_DIR)),
        "time_window": {"start": START.isoformat(), "end": END.isoformat()},
        "filters": {
            "magnitude_diff_max": MAX_MAGNITUDE_DIFF,
            "epicentral_distance_km_max": MAX_EPICENTRAL_DISTANCE_KM,
            "common_station_components_min": MIN_COMMON_COMPONENTS,
        },
        "counts": {
            "candidate_event_pairs": len(candidates),
            "repeat_event_pairs": len(pairs),
            "high_confidence_pairs": int(
                pairs["repeat_candidate_level"].eq("high_confidence").sum()
            ),
            "families": len(families),
            "family_members": len(members),
        },
        "note": "Post-processing of the full result set for manuscript-aligned plotting.",
    }
    (TARGET_DIR / "manuscript_alignment_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
