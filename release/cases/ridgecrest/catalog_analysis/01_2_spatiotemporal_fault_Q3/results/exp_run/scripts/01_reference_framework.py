from __future__ import annotations

import json
import math
import os
import sys
import traceback
from dataclasses import dataclass
from pathlib import Path
from typing import List

import numpy as np
import pandas as pd
from pyproj import CRS, Transformer


CATALOG_PATH = Path(
    "<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/TRACE_ridgecrest_relocated.csv"
)
MAINSHOCK_PATH = Path(
    "<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/main_shock_events.csv"
)
FAULT_PATH = Path(
    "<REPO_ROOT>/examples/ridgecrest/data/faults/ridgecrest_surface_faults.json"
)
OUTPUT_DIR = Path(
    "<REPO_ROOT>/examples/ridgecrest/catalog_analysis/run/01_2_trigger_spatiotemporal_fault_Q3-v1/exp_run/outputs/01_reference_framework"
)

EXPECTED_COLUMNS = ["event_time", "latitude", "longitude", "depth_km", "magnitude"]
PLOT_MARGIN_DEG = 0.05
STAGE1_DURATION_HOURS = 4
STAGE1_FREQ = "30min"
STAGE2_FREQ = "2h"
MORPH_FREQ = "1h"
FINAL_BIN_POLICY = "left_closed_right_open_except_final_closed"


@dataclass(frozen=True)
class IntervalSpec:
    label: str
    start: pd.Timestamp
    end: pd.Timestamp
    is_final: bool


def log(message: str) -> None:
    print(message, flush=True)


def ensure_output_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def remove_stale_outputs(output_dir: Path) -> None:
    stale_names = [
        "intermainshock_catalog_clean.csv",
        "mainshock_reference_table.csv",
        "fault_segments_table.csv",
        "interval_definitions_kde_stage1.csv",
        "interval_definitions_kde_stage2.csv",
        "interval_definitions_morphology_1h.csv",
        "analysis_metadata.json",
    ]
    for name in stale_names:
        path = output_dir / name
        if path.exists():
            path.unlink()
            log(f"Removed stale output: {path}")


def validate_columns(df: pd.DataFrame, name: str) -> None:
    missing = [c for c in EXPECTED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"{name} is missing required columns: {missing}")


def load_csv_with_time(path: Path, name: str) -> pd.DataFrame:
    log(f"Loading {name}: {path}")
    df = pd.read_csv(path)
    validate_columns(df, name)

    out = df.copy()
    out["event_time_raw"] = out["event_time"].astype(str)
    out["event_time"] = pd.to_datetime(out["event_time"], utc=True, errors="coerce")

    numeric_cols = ["latitude", "longitude", "depth_km", "magnitude"]
    for col in numeric_cols:
        out[col] = pd.to_numeric(out[col], errors="coerce")
    return out


def clean_event_table(df: pd.DataFrame, name: str) -> tuple[pd.DataFrame, dict]:
    before = len(df)
    valid_mask = (
        df["event_time"].notna()
        & df["latitude"].notna()
        & df["longitude"].notna()
        & np.isfinite(df["latitude"])
        & np.isfinite(df["longitude"])
    )
    cleaned = df.loc[valid_mask, EXPECTED_COLUMNS + ["event_time_raw"]].copy()
    cleaned = cleaned.sort_values("event_time").reset_index(drop=True)

    metadata = {
        "table_name": name,
        "rows_before_cleaning": int(before),
        "rows_after_cleaning": int(len(cleaned)),
        "rows_removed": int(before - len(cleaned)),
    }
    return cleaned, metadata


def identify_mainshocks(df: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
    if len(df) < 2:
        raise ValueError("Mainshock table must contain at least two rows.")

    rounded = df["magnitude"].round(1)
    idx64 = rounded.sub(6.4).abs().idxmin()
    idx71 = rounded.sub(7.1).abs().idxmin()

    ms64 = df.loc[idx64].copy()
    ms71 = df.loc[idx71].copy()

    if pd.isna(ms64["event_time"]) or pd.isna(ms71["event_time"]):
        raise ValueError("Failed to identify valid event times for mainshocks.")
    if ms64["event_time"] >= ms71["event_time"]:
        raise ValueError("Mainshock64 must occur before Mainshock71.")
    return ms64, ms71


def build_interval_table(start: pd.Timestamp, end: pd.Timestamp, freq: str, stage_name: str) -> pd.DataFrame:
    if start >= end:
        raise ValueError(f"Invalid interval range for {stage_name}: start >= end")

    edges = list(pd.date_range(start=start, end=end, freq=freq, tz="UTC"))
    if not edges or edges[0] != start:
        edges = [start] + edges
    if edges[-1] != end:
        edges.append(end)

    intervals: List[IntervalSpec] = []
    for i in range(len(edges) - 1):
        left = edges[i]
        right = edges[i + 1]
        intervals.append(
            IntervalSpec(
                label=f"{stage_name}_{i + 1:02d}",
                start=left,
                end=right,
                is_final=(i == len(edges) - 2),
            )
        )

    rows = []
    for idx, interval in enumerate(intervals, start=1):
        duration_hours = (interval.end - interval.start).total_seconds() / 3600.0
        rows.append(
            {
                "stage": stage_name,
                "interval_index": idx,
                "interval_label": interval.label,
                "start_time": interval.start,
                "end_time": interval.end,
                "start_time_iso": interval.start.isoformat(),
                "end_time_iso": interval.end.isoformat(),
                "duration_hours": duration_hours,
                "is_final_interval": interval.is_final,
                "bin_inclusion_rule": FINAL_BIN_POLICY,
            }
        )
    return pd.DataFrame(rows)


def load_fault_segments(path: Path) -> tuple[pd.DataFrame, dict]:
    log(f"Loading faults: {path}")
    with path.open("r", encoding="utf-8") as f:
        segments = json.load(f)

    if not isinstance(segments, list):
        raise ValueError("Fault JSON must be a list of segments.")

    rows = []
    kept_segments = 0
    kept_points = 0
    skipped_segments = 0

    for seg_id, segment in enumerate(segments):
        if not isinstance(segment, list) or len(segment) < 2:
            skipped_segments += 1
            continue

        local_points = []
        for pt in segment:
            if not isinstance(pt, (list, tuple)) or len(pt) != 2:
                continue
            lon, lat = pt
            try:
                lon = float(lon)
                lat = float(lat)
            except Exception:
                continue
            if not (math.isfinite(lon) and math.isfinite(lat)):
                continue
            local_points.append((lon, lat))

        if len(local_points) < 2:
            skipped_segments += 1
            continue

        kept_segments += 1
        kept_points += len(local_points)
        for point_order, (lon, lat) in enumerate(local_points):
            rows.append(
                {
                    "segment_id": kept_segments - 1,
                    "source_segment_index": seg_id,
                    "point_order": point_order,
                    "longitude": lon,
                    "latitude": lat,
                }
            )

    fault_df = pd.DataFrame(rows)
    metadata = {
        "raw_segment_count": int(len(segments)),
        "kept_segment_count": int(kept_segments),
        "skipped_segment_count": int(skipped_segments),
        "kept_point_count": int(kept_points),
    }
    return fault_df, metadata


def choose_local_crs(lon_center: float, lat_center: float) -> CRS:
    zone = int(math.floor((lon_center + 180.0) / 6.0) + 1)
    epsg = 32600 + zone if lat_center >= 0 else 32700 + zone
    return CRS.from_epsg(epsg)


def project_xy(df: pd.DataFrame, transformer: Transformer, lon_col: str = "longitude", lat_col: str = "latitude") -> pd.DataFrame:
    x, y = transformer.transform(df[lon_col].to_numpy(), df[lat_col].to_numpy())
    out = df.copy()
    out["x_m"] = x
    out["y_m"] = y
    return out


def compute_extent_and_center(catalog_df: pd.DataFrame, main_df: pd.DataFrame, fault_df: pd.DataFrame) -> dict:
    lon_values = np.concatenate(
        [
            catalog_df["longitude"].to_numpy(),
            main_df["longitude"].to_numpy(),
            fault_df["longitude"].to_numpy(),
        ]
    )
    lat_values = np.concatenate(
        [
            catalog_df["latitude"].to_numpy(),
            main_df["latitude"].to_numpy(),
            fault_df["latitude"].to_numpy(),
        ]
    )

    lon_min = float(np.min(lon_values))
    lon_max = float(np.max(lon_values))
    lat_min = float(np.min(lat_values))
    lat_max = float(np.max(lat_values))

    return {
        "longitude_min": lon_min,
        "longitude_max": lon_max,
        "latitude_min": lat_min,
        "latitude_max": lat_max,
        "longitude_min_padded": lon_min - PLOT_MARGIN_DEG,
        "longitude_max_padded": lon_max + PLOT_MARGIN_DEG,
        "latitude_min_padded": lat_min - PLOT_MARGIN_DEG,
        "latitude_max_padded": lat_max + PLOT_MARGIN_DEG,
        "longitude_center": float((lon_min + lon_max) / 2.0),
        "latitude_center": float((lat_min + lat_max) / 2.0),
        "plot_margin_degrees": PLOT_MARGIN_DEG,
    }


def add_intermainshock_flags(catalog_df: pd.DataFrame, t0: pd.Timestamp, t1: pd.Timestamp) -> pd.DataFrame:
    out = catalog_df.copy()
    out["within_intermainshock_window"] = (out["event_time"] >= t0) & (out["event_time"] <= t1)
    return out.loc[out["within_intermainshock_window"]].copy().reset_index(drop=True)


def assign_interval_counts(events: pd.DataFrame, intervals: pd.DataFrame) -> pd.DataFrame:
    counts = []
    event_times = events["event_time"]
    for _, row in intervals.iterrows():
        start = row["start_time"]
        end = row["end_time"]
        if bool(row["is_final_interval"]):
            mask = (event_times >= start) & (event_times <= end)
        else:
            mask = (event_times >= start) & (event_times < end)
        counts.append(int(mask.sum()))
    out = intervals.copy()
    out["event_count"] = counts
    return out


def write_csv(df: pd.DataFrame, path: Path) -> None:
    tmp = df.copy()
    for col in tmp.columns:
        if pd.api.types.is_datetime64tz_dtype(tmp[col]):
            tmp[col] = tmp[col].dt.strftime("%Y-%m-%dT%H:%M:%S.%f%z")
    tmp.to_csv(path, index=False)
    log(f"Wrote CSV: {path}")


def build_mainshock_reference(ms64: pd.Series, ms71: pd.Series, catalog: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    rows = []
    discrepancy = {}
    for label, row in [("Mainshock64", ms64), ("Mainshock71", ms71)]:
        rounded_mag = round(float(row["magnitude"]), 1)
        catalog_match = catalog.loc[catalog["magnitude"].round(1) == rounded_mag].copy()
        time_difference_seconds = None
        if not catalog_match.empty:
            idx = (catalog_match["event_time"] - row["event_time"]).abs().idxmin()
            matched = catalog_match.loc[idx]
            time_difference_seconds = float(abs((matched["event_time"] - row["event_time"]).total_seconds()))
        discrepancy[label] = {
            "matched_catalog_event_found": bool(not catalog_match.empty),
            "nearest_catalog_time_difference_seconds": time_difference_seconds,
        }
        rows.append(
            {
                "event_label": label,
                "event_time": row["event_time"],
                "event_time_iso": row["event_time"].isoformat(),
                "latitude": float(row["latitude"]),
                "longitude": float(row["longitude"]),
                "depth_km": float(row["depth_km"]),
                "magnitude": float(row["magnitude"]),
            }
        )
    return pd.DataFrame(rows), discrepancy


def main() -> None:
    log("Starting Task 01_reference_framework")
    log(f"PID={os.getpid()}")
    ensure_output_dir(OUTPUT_DIR)
    remove_stale_outputs(OUTPUT_DIR)

    catalog_raw = load_csv_with_time(CATALOG_PATH, "catalog")
    main_raw = load_csv_with_time(MAINSHOCK_PATH, "mainshock_table")

    catalog_clean, catalog_meta = clean_event_table(catalog_raw, "catalog")
    main_clean, main_meta = clean_event_table(main_raw, "mainshock_table")
    ms64, ms71 = identify_mainshocks(main_clean)

    t64 = ms64["event_time"]
    t71 = ms71["event_time"]
    log(f"Inter-mainshock window: {t64.isoformat()} -> {t71.isoformat()}")

    inter_catalog = add_intermainshock_flags(catalog_clean, t64, t71)
    if inter_catalog.empty:
        raise ValueError("No events found in the inter-mainshock analysis window.")
    log(f"Inter-mainshock event count: {len(inter_catalog)}")

    mainshock_reference_df, discrepancy = build_mainshock_reference(ms64, ms71, catalog_clean)
    fault_df, fault_meta = load_fault_segments(FAULT_PATH)
    if fault_df.empty:
        raise ValueError("No valid fault points were parsed from the fault JSON.")

    extent = compute_extent_and_center(inter_catalog, mainshock_reference_df, fault_df)
    local_crs = choose_local_crs(extent["longitude_center"], extent["latitude_center"])
    transformer_fwd = Transformer.from_crs("EPSG:4326", local_crs, always_xy=True)

    inter_catalog = project_xy(inter_catalog, transformer_fwd)
    mainshock_reference_df = project_xy(mainshock_reference_df, transformer_fwd)
    fault_df = project_xy(fault_df, transformer_fwd)

    stage1_end = t64 + pd.Timedelta(hours=STAGE1_DURATION_HOURS)
    if stage1_end > t71:
        stage1_end = t71

    stage1_intervals = build_interval_table(t64, stage1_end, STAGE1_FREQ, "stage1")
    stage1_intervals = assign_interval_counts(inter_catalog, stage1_intervals)

    stage2_intervals = build_interval_table(stage1_end, t71, STAGE2_FREQ, "stage2")
    stage2_intervals = assign_interval_counts(inter_catalog, stage2_intervals)

    morph_intervals = build_interval_table(t64, t71, MORPH_FREQ, "morphology_1h")
    morph_intervals = assign_interval_counts(inter_catalog, morph_intervals)

    write_csv(inter_catalog, OUTPUT_DIR / "intermainshock_catalog_clean.csv")
    write_csv(mainshock_reference_df, OUTPUT_DIR / "mainshock_reference_table.csv")
    write_csv(fault_df, OUTPUT_DIR / "fault_segments_table.csv")
    write_csv(stage1_intervals, OUTPUT_DIR / "interval_definitions_kde_stage1.csv")
    write_csv(stage2_intervals, OUTPUT_DIR / "interval_definitions_kde_stage2.csv")
    write_csv(morph_intervals, OUTPUT_DIR / "interval_definitions_morphology_1h.csv")

    metadata = {
        "task": "01_reference_framework",
        "input_paths": {
            "catalog": str(CATALOG_PATH),
            "mainshock_table": str(MAINSHOCK_PATH),
            "fault_json": str(FAULT_PATH),
        },
        "output_dir": str(OUTPUT_DIR),
        "cleaning": {
            "catalog": catalog_meta,
            "mainshock_table": main_meta,
        },
        "mainshock_window": {
            "mainshock64_time": t64.isoformat(),
            "mainshock71_time": t71.isoformat(),
            "window_duration_hours": (t71 - t64).total_seconds() / 3600.0,
        },
        "mainshock_catalog_discrepancy": discrepancy,
        "interval_definitions": {
            "stage1": {
                "description": "[mainshock64, mainshock64 + 4 hours], 30-minute interval",
                "count": int(len(stage1_intervals)),
                "frequency": STAGE1_FREQ,
                "event_total": int(stage1_intervals["event_count"].sum()),
            },
            "stage2": {
                "description": "[mainshock64 + 4 hours, mainshock71], 2-hour interval",
                "count": int(len(stage2_intervals)),
                "frequency": STAGE2_FREQ,
                "event_total": int(stage2_intervals["event_count"].sum()),
            },
            "morphology_1h": {
                "description": "[mainshock64, mainshock71], 1-hour interval",
                "count": int(len(morph_intervals)),
                "frequency": MORPH_FREQ,
                "event_total": int(morph_intervals["event_count"].sum()),
            },
            "bin_policy": FINAL_BIN_POLICY,
        },
        "counts": {
            "intermainshock_catalog_event_count": int(len(inter_catalog)),
            "fault_segment_count": int(fault_meta["kept_segment_count"]),
            "fault_point_count": int(fault_meta["kept_point_count"]),
        },
        "fault_metadata": fault_meta,
        "plot_extent_degrees": extent,
        "projected_crs": {
            "epsg": local_crs.to_epsg(),
            "projjson": local_crs.to_json_dict(),
        },
    }

    metadata_path = OUTPUT_DIR / "analysis_metadata.json"
    with metadata_path.open("w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    log(f"Wrote metadata: {metadata_path}")
    log("Task 01_reference_framework completed successfully")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print(traceback.format_exc(), flush=True)
        sys.exit(1)
