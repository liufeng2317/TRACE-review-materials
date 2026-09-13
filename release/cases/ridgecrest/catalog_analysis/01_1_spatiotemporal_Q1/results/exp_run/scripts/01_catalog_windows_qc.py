from __future__ import annotations

import json
import math
import os
import sys
import traceback
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List

import numpy as np
import pandas as pd


CATALOG_PATH = Path(
    "<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/TRACE_ridgecrest_relocated.csv"
)
MAINSHOCK_PATH = Path(
    "<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/main_shock_events.csv"
)
OUTPUT_DIR = Path(
    "<REPO_ROOT>/examples/ridgecrest/catalog_analysis/run/01_1_trigger_spatiotemporal_Q1-v1/exp_run/outputs/01_catalog_windows_qc"
)

EXPECTED_COLUMNS = ["event_time", "latitude", "longitude", "depth_km", "magnitude"]
DERIVED_CATALOG_COLUMNS = [
    "event_time",
    "latitude",
    "longitude",
    "depth_km",
    "magnitude",
    "x_km_local",
    "y_km_local",
    "elapsed_hours_since_mainshock64",
    "elapsed_hours_since_mainshock71",
    "sequence_segment_label",
]
PAD_DEGREES = 0.05
MAX_CORES = min(64, os.cpu_count() or 1)
STALE_OUTPUT_FILENAMES = [
    "ridgecrest_catalog_clean.csv",
    "mainshock_reference_verified.csv",
    "analysis_extent.json",
    "time_windows_whole_sequence.csv",
    "time_windows_post64_hourly.csv",
    "time_windows_comparison_intervals.csv",
    "catalog_qc_summary.json",
]


@dataclass(frozen=True)
class TimeIntervalDef:
    comparison_label: str
    interval_role: str
    start_time: pd.Timestamp
    end_time: pd.Timestamp


def log(message: str) -> None:
    print(message, flush=True)


def ensure_output_dir() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def clear_stale_outputs() -> None:
    for name in STALE_OUTPUT_FILENAMES:
        path = OUTPUT_DIR / name
        if path.exists():
            path.unlink()
            log(f"[INFO] Removed stale output: {path}")


def validate_columns(df: pd.DataFrame, path: Path) -> None:
    missing = [c for c in EXPECTED_COLUMNS if c not in df.columns]
    extra = [c for c in df.columns if c not in EXPECTED_COLUMNS]
    if missing:
        raise ValueError(f"Missing required columns in {path}: {missing}")
    if extra:
        log(f"[WARN] Extra columns found in {path.name} and retained only if useful downstream: {extra}")


def read_catalog_csv(path: Path) -> pd.DataFrame:
    log(f"[INFO] Reading CSV: {path}")
    df = pd.read_csv(path)
    validate_columns(df, path)
    return df


def clean_catalog(df: pd.DataFrame, label: str) -> tuple[pd.DataFrame, dict]:
    original_count = len(df)
    qc = {
        "dataset_label": label,
        "rows_original": int(original_count),
        "rows_dropped_missing_required": 0,
        "rows_dropped_invalid_time": 0,
        "rows_dropped_invalid_numeric": 0,
        "rows_dropped_nonfinite_coordinates": 0,
        "rows_final": None,
        "time_min": None,
        "time_max": None,
    }

    working = df.copy()
    working = working[EXPECTED_COLUMNS].copy()

    missing_mask = working[["event_time", "latitude", "longitude"]].isna().any(axis=1)
    qc["rows_dropped_missing_required"] = int(missing_mask.sum())
    working = working.loc[~missing_mask].copy()

    working["event_time"] = pd.to_datetime(working["event_time"], utc=True, errors="coerce")
    invalid_time_mask = working["event_time"].isna()
    qc["rows_dropped_invalid_time"] = int(invalid_time_mask.sum())
    working = working.loc[~invalid_time_mask].copy()

    for col in ["latitude", "longitude", "depth_km", "magnitude"]:
        working[col] = pd.to_numeric(working[col], errors="coerce")

    invalid_numeric_mask = working[["latitude", "longitude", "depth_km", "magnitude"]].isna().any(axis=1)
    qc["rows_dropped_invalid_numeric"] = int(invalid_numeric_mask.sum())
    working = working.loc[~invalid_numeric_mask].copy()

    finite_mask = np.isfinite(working["latitude"]) & np.isfinite(working["longitude"])
    qc["rows_dropped_nonfinite_coordinates"] = int((~finite_mask).sum())
    working = working.loc[finite_mask].copy()

    working = working.sort_values("event_time", kind="mergesort").reset_index(drop=True)

    qc["rows_final"] = int(len(working))
    if len(working) > 0:
        qc["time_min"] = working["event_time"].min().isoformat()
        qc["time_max"] = working["event_time"].max().isoformat()

    log(
        f"[INFO] Cleaned {label}: original={original_count}, final={len(working)}, "
        f"dropped_missing={qc['rows_dropped_missing_required']}, "
        f"dropped_invalid_time={qc['rows_dropped_invalid_time']}, "
        f"dropped_invalid_numeric={qc['rows_dropped_invalid_numeric']}, "
        f"dropped_nonfinite_coords={qc['rows_dropped_nonfinite_coordinates']}"
    )

    return working, qc


def verify_mainshocks(main_df: pd.DataFrame) -> pd.DataFrame:
    log("[INFO] Verifying mainshock reference rows")
    mags = sorted(main_df["magnitude"].round(1).tolist())
    if mags != [6.4, 7.1]:
        raise ValueError(f"Expected mainshock magnitudes [6.4, 7.1], found {mags}")

    ms64 = main_df.loc[np.isclose(main_df["magnitude"], 6.4)].copy()
    ms71 = main_df.loc[np.isclose(main_df["magnitude"], 7.1)].copy()
    if len(ms64) != 1 or len(ms71) != 1:
        raise ValueError("Mainshock reference file must contain exactly one Mw 6.4 row and one Mw 7.1 row")

    ms64 = ms64.iloc[0]
    ms71 = ms71.iloc[0]
    if not ms64["event_time"] < ms71["event_time"]:
        raise ValueError("Mainshock64 time must be earlier than Mainshock71 time")

    verified = pd.DataFrame(
        [
            {
                "mainshock_label": "mainshock64",
                "event_time": ms64["event_time"],
                "latitude": float(ms64["latitude"]),
                "longitude": float(ms64["longitude"]),
                "depth_km": float(ms64["depth_km"]),
                "magnitude": float(ms64["magnitude"]),
            },
            {
                "mainshock_label": "mainshock71",
                "event_time": ms71["event_time"],
                "latitude": float(ms71["latitude"]),
                "longitude": float(ms71["longitude"]),
                "depth_km": float(ms71["depth_km"]),
                "magnitude": float(ms71["magnitude"]),
            },
        ]
    )
    return verified


def build_common_extent(df: pd.DataFrame) -> dict:
    lon_min = float(df["longitude"].min())
    lon_max = float(df["longitude"].max())
    lat_min = float(df["latitude"].min())
    lat_max = float(df["latitude"].max())

    extent = {
        "longitude_min": lon_min - PAD_DEGREES,
        "longitude_max": lon_max + PAD_DEGREES,
        "latitude_min": lat_min - PAD_DEGREES,
        "latitude_max": lat_max + PAD_DEGREES,
        "padding_degrees": PAD_DEGREES,
        "derived_from": "full_clean_catalog",
    }
    return extent


def add_projected_coordinates(df: pd.DataFrame, origin_lon: float, origin_lat: float) -> pd.DataFrame:
    out = df.copy()
    lat_rad = np.deg2rad(out["latitude"].to_numpy())
    lon_rad = np.deg2rad(out["longitude"].to_numpy())
    origin_lat_rad = math.radians(origin_lat)
    origin_lon_rad = math.radians(origin_lon)
    earth_radius_km = 6371.0
    out["x_km_local"] = earth_radius_km * (lon_rad - origin_lon_rad) * math.cos(origin_lat_rad)
    out["y_km_local"] = earth_radius_km * (lat_rad - origin_lat_rad)
    return out


def add_elapsed_times(df: pd.DataFrame, ms64_time: pd.Timestamp, ms71_time: pd.Timestamp) -> pd.DataFrame:
    out = df.copy()
    out["elapsed_hours_since_mainshock64"] = (
        (out["event_time"] - ms64_time).dt.total_seconds() / 3600.0
    )
    out["elapsed_hours_since_mainshock71"] = (
        (out["event_time"] - ms71_time).dt.total_seconds() / 3600.0
    )
    conditions = [
        out["event_time"] < ms64_time,
        (out["event_time"] >= ms64_time) & (out["event_time"] < ms71_time),
        out["event_time"] >= ms71_time,
    ]
    labels = ["pre_mainshock64", "between_mainshock64_mainshock71", "post_mainshock71"]
    out["sequence_segment_label"] = np.select(conditions, labels, default="unclassified")
    return out



def assert_expected_columns(df: pd.DataFrame, expected: list[str], df_name: str) -> None:
    missing = [col for col in expected if col not in df.columns]
    if missing:
        raise ValueError(f"{df_name} is missing required downstream columns: {missing}")



def build_regular_windows(
    family_name: str,
    stage_label: str,
    start_time: pd.Timestamp,
    end_time: pd.Timestamp,
    step: pd.Timedelta,
) -> pd.DataFrame:
    if not start_time < end_time:
        raise ValueError(f"Invalid window bounds for {family_name}/{stage_label}: start >= end")
    starts = list(pd.date_range(start=start_time, end=end_time, freq=step, inclusive="left"))
    records: List[dict] = []
    total_hours = step.total_seconds() / 3600.0
    for idx, win_start in enumerate(starts):
        win_end = min(win_start + step, end_time)
        records.append(
            {
                "window_family": family_name,
                "stage_label": stage_label,
                "window_index": idx,
                "window_label": f"{family_name}_{stage_label}_{idx:04d}",
                "start_time": win_start,
                "end_time": win_end,
                "duration_hours": total_hours,
                "is_terminal_partial_window": bool((win_end - win_start) < step),
            }
        )
    if not records:
        raise ValueError(f"No windows generated for {family_name}/{stage_label}")
    return pd.DataFrame.from_records(records)


def build_comparison_intervals(
    catalog_start: pd.Timestamp,
    ms64_time: pd.Timestamp,
    ms71_time: pd.Timestamp,
) -> pd.DataFrame:
    defs = [
        TimeIntervalDef("mw64", "before", catalog_start, ms64_time),
        TimeIntervalDef("mw64", "after", ms64_time, ms71_time),
        TimeIntervalDef("mw71", "before", ms64_time, ms71_time),
        TimeIntervalDef("mw71", "after", ms71_time, ms71_time + pd.Timedelta(days=2)),
    ]
    records = []
    for item in defs:
        if not item.start_time < item.end_time:
            raise ValueError(
                f"Invalid comparison interval for {item.comparison_label}/{item.interval_role}: start >= end"
            )
        records.append(
            {
                "comparison_label": item.comparison_label,
                "interval_role": item.interval_role,
                "start_time": item.start_time,
                "end_time": item.end_time,
                "duration_hours": (item.end_time - item.start_time).total_seconds() / 3600.0,
            }
        )
    return pd.DataFrame.from_records(records)


def write_csv(df: pd.DataFrame, path: Path) -> None:
    out = df.copy()
    for col in out.columns:
        if pd.api.types.is_datetime64_any_dtype(out[col]):
            out[col] = out[col].dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    out.to_csv(path, index=False)
    log(f"[INFO] Wrote CSV: {path}")


def write_json(obj: dict, path: Path) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, sort_keys=True)
    log(f"[INFO] Wrote JSON: {path}")


def summarize_windows(windows: Iterable[pd.DataFrame]) -> dict:
    summary = {}
    for df in windows:
        family = str(df["window_family"].iloc[0])
        stage = str(df["stage_label"].iloc[0])
        summary[f"{family}__{stage}"] = {
            "n_windows": int(len(df)),
            "start_time": df["start_time"].min().isoformat(),
            "end_time": df["end_time"].max().isoformat(),
        }
    return summary


def main() -> None:
    ensure_output_dir()
    clear_stale_outputs()
    log(f"[INFO] Output directory: {OUTPUT_DIR}")
    log(f"[INFO] MAX_CORES setting available for downstream tasks: {MAX_CORES}")

    catalog_raw = read_catalog_csv(CATALOG_PATH)
    mainshock_raw = read_catalog_csv(MAINSHOCK_PATH)

    catalog_clean, catalog_qc = clean_catalog(catalog_raw, "ridgecrest_catalog")
    mainshock_clean, mainshock_qc = clean_catalog(mainshock_raw, "mainshock_reference")

    mainshock_verified = verify_mainshocks(mainshock_clean)
    ms64 = mainshock_verified.loc[mainshock_verified["mainshock_label"] == "mainshock64"].iloc[0]
    ms71 = mainshock_verified.loc[mainshock_verified["mainshock_label"] == "mainshock71"].iloc[0]
    ms64_time = pd.Timestamp(ms64["event_time"])
    ms71_time = pd.Timestamp(ms71["event_time"])

    extent = build_common_extent(catalog_clean)
    origin_lon = 0.5 * (extent["longitude_min"] + extent["longitude_max"])
    origin_lat = 0.5 * (extent["latitude_min"] + extent["latitude_max"])
    extent["projection_origin_longitude"] = origin_lon
    extent["projection_origin_latitude"] = origin_lat

    catalog_enriched = add_projected_coordinates(catalog_clean, origin_lon=origin_lon, origin_lat=origin_lat)
    catalog_enriched = add_elapsed_times(catalog_enriched, ms64_time=ms64_time, ms71_time=ms71_time)
    assert_expected_columns(catalog_enriched, DERIVED_CATALOG_COLUMNS, "catalog_enriched")

    whole_stage_a = build_regular_windows(
        family_name="whole_sequence",
        stage_label="2h_mainshock64_to_mainshock71_plus_1day",
        start_time=ms64_time,
        end_time=ms71_time + pd.Timedelta(days=1),
        step=pd.Timedelta(hours=2),
    )
    whole_stage_b = build_regular_windows(
        family_name="whole_sequence",
        stage_label="6h_mainshock71_plus_1day_to_plus_5days",
        start_time=ms71_time + pd.Timedelta(days=1),
        end_time=ms71_time + pd.Timedelta(days=5),
        step=pd.Timedelta(hours=6),
    )
    time_windows_whole = pd.concat([whole_stage_a, whole_stage_b], ignore_index=True)
    time_windows_whole.insert(0, "global_window_id", np.arange(len(time_windows_whole), dtype=int))

    hourly_post64 = build_regular_windows(
        family_name="post64_hourly",
        stage_label="1h_mainshock64_to_mainshock71",
        start_time=ms64_time,
        end_time=ms71_time,
        step=pd.Timedelta(hours=1),
    )
    hourly_post64.insert(0, "global_window_id", np.arange(len(hourly_post64), dtype=int))

    comparison_intervals = build_comparison_intervals(
        catalog_start=catalog_enriched["event_time"].min(),
        ms64_time=ms64_time,
        ms71_time=ms71_time,
    )
    assert_expected_columns(mainshock_verified, ["mainshock_label", *EXPECTED_COLUMNS], "mainshock_verified")
    assert_expected_columns(
        time_windows_whole,
        [
            "global_window_id",
            "window_family",
            "stage_label",
            "window_index",
            "window_label",
            "start_time",
            "end_time",
            "duration_hours",
            "is_terminal_partial_window",
        ],
        "time_windows_whole",
    )
    assert_expected_columns(
        hourly_post64,
        [
            "global_window_id",
            "window_family",
            "stage_label",
            "window_index",
            "window_label",
            "start_time",
            "end_time",
            "duration_hours",
            "is_terminal_partial_window",
        ],
        "hourly_post64",
    )
    assert_expected_columns(
        comparison_intervals,
        ["comparison_label", "interval_role", "start_time", "end_time", "duration_hours"],
        "comparison_intervals",
    )

    catalog_qc_summary = {
        "catalog_qc": catalog_qc,
        "mainshock_qc": mainshock_qc,
        "verified_mainshocks": {
            row["mainshock_label"]: {
                "event_time": pd.Timestamp(row["event_time"]).isoformat(),
                "latitude": float(row["latitude"]),
                "longitude": float(row["longitude"]),
                "depth_km": float(row["depth_km"]),
                "magnitude": float(row["magnitude"]),
            }
            for _, row in mainshock_verified.iterrows()
        },
        "common_extent": extent,
        "window_summary": {
            **summarize_windows([whole_stage_a, whole_stage_b]),
            "post64_hourly": {
                "n_windows": int(len(hourly_post64)),
                "start_time": hourly_post64["start_time"].min().isoformat(),
                "end_time": hourly_post64["end_time"].max().isoformat(),
            },
            "comparison_intervals": int(len(comparison_intervals)),
        },
        "notes": {
            "interval_convention": "half_open_start_inclusive_end_exclusive",
            "spatial_projection": "local_equirectangular_km",
            "max_cores_available_for_downstream_tasks": MAX_CORES,
        },
    }

    write_csv(catalog_enriched, OUTPUT_DIR / "ridgecrest_catalog_clean.csv")
    write_csv(mainshock_verified, OUTPUT_DIR / "mainshock_reference_verified.csv")
    write_json(extent, OUTPUT_DIR / "analysis_extent.json")
    write_csv(time_windows_whole, OUTPUT_DIR / "time_windows_whole_sequence.csv")
    write_csv(hourly_post64, OUTPUT_DIR / "time_windows_post64_hourly.csv")
    write_csv(comparison_intervals, OUTPUT_DIR / "time_windows_comparison_intervals.csv")
    write_json(catalog_qc_summary, OUTPUT_DIR / "catalog_qc_summary.json")

    log("[INFO] Task 01_catalog_windows_qc completed successfully")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print(traceback.format_exc(), flush=True)
        sys.exit(1)
