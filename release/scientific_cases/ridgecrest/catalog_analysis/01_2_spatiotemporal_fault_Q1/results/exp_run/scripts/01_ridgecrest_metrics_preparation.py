#!/usr/bin/env python
from __future__ import annotations

import json
import math
import os
import sys
import traceback
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from pyproj import CRS, Transformer
from scipy.spatial import cKDTree
from tqdm import tqdm


SCRIPT_PATH = Path(__file__).resolve()
OUTPUT_DIR = Path(
    "<REPO_ROOT>/examples/ridgecrest/catalog_analysis/run/01_2_trigger_spatiotemporal_fault_Q1-v1/exp_run/outputs/01_ridgecrest_metrics_preparation"
).resolve()
CATALOG_PATH = Path(
    "<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/TRACE_ridgecrest_relocated.csv"
).resolve()
MAINSHOCK_PATH = Path(
    "<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/main_shock_events.csv"
).resolve()
FAULT_PATH = Path(
    "<REPO_ROOT>/examples/ridgecrest/data/faults/ridgecrest_surface_faults.json"
).resolve()

MAX_WORKERS = min(64, max(1, (os.cpu_count() or 1)))
EVENT_CHUNK_SIZE = 5000
SPARSE_BIN_MIN_EVENTS = 10
ALONG_STRIKE_BIN_KM = 2.0
NEAR_FAULT_THRESHOLDS_KM = (0.25, 0.5, 1.0, 2.0, 5.0)
MAP_MARGIN_KM = 5.0
LOCAL_AEQD_CRS = CRS.from_proj4(
    "+proj=aeqd +lat_0=35.74 +lon_0=-117.55 +datum=WGS84 +units=km +no_defs"
)
WGS84_CRS = CRS.from_epsg(4326)


@dataclass
class TimeBin:
    bin_id: int
    stage: str
    start: pd.Timestamp
    end: pd.Timestamp
    end_inclusive: bool
    page: int
    subplot_index: int


def log(message: str) -> None:
    print(message, flush=True)


def ensure_output_dir() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    stale_outputs = [
        "catalog_clean_projected.csv",
        "mainshock_reference.csv",
        "fault_polylines_summary.csv",
        "fault_segments_projected.csv",
        "canonical_map_extent.csv",
        "canonical_time_bins.csv",
        "event_fault_metrics_pre71.csv",
        "event_fault_metrics_post71.csv",
        "bin_directional_summary.csv",
        "along_strike_first_activation.csv",
        "question_metric_summary.csv",
        "validation_summary.csv",
        "run_metadata.csv",
    ]
    for name in stale_outputs:
        path = OUTPUT_DIR / name
        if path.exists():
            path.unlink()
            log(f"Removed stale output: {path}")


def parse_utc(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series, utc=True)


def angular_misfit_deg(a_deg: float, b_deg: float) -> float:
    if np.isnan(a_deg) or np.isnan(b_deg):
        return np.nan
    diff = abs((a_deg - b_deg + 90.0) % 180.0 - 90.0)
    return float(diff)


def strike_from_dxdy(dx: float, dy: float) -> float:
    angle = math.degrees(math.atan2(dx, dy)) % 180.0
    return float(angle)


def weighted_orientation_deg(strikes_deg: np.ndarray, weights: np.ndarray) -> float:
    if len(strikes_deg) == 0:
        return np.nan
    theta = np.deg2rad(np.asarray(strikes_deg) * 2.0)
    weights = np.asarray(weights)
    c = np.sum(weights * np.cos(theta))
    s = np.sum(weights * np.sin(theta))
    if c == 0 and s == 0:
        return np.nan
    return float((np.rad2deg(np.arctan2(s, c)) / 2.0) % 180.0)


def principal_axis_metrics(x_km: np.ndarray, y_km: np.ndarray) -> Dict[str, float]:
    n = len(x_km)
    if n < 2:
        return {
            "centroid_x_km": float(np.mean(x_km)) if n else np.nan,
            "centroid_y_km": float(np.mean(y_km)) if n else np.nan,
            "principal_strike_deg": np.nan,
            "major_spread_km": np.nan,
            "minor_spread_km": np.nan,
            "elongation_ratio": np.nan,
        }
    x0 = x_km - np.mean(x_km)
    y0 = y_km - np.mean(y_km)
    cov = np.cov(np.vstack([x0, y0]))
    vals, vecs = np.linalg.eigh(cov)
    order = np.argsort(vals)[::-1]
    vals = vals[order]
    vecs = vecs[:, order]
    principal_vec = vecs[:, 0]
    strike_deg = strike_from_dxdy(principal_vec[0], principal_vec[1])
    major = float(np.sqrt(max(vals[0], 0.0)))
    minor = float(np.sqrt(max(vals[1], 0.0)))
    elong = float(major / minor) if minor > 0 else np.inf
    return {
        "centroid_x_km": float(np.mean(x_km)),
        "centroid_y_km": float(np.mean(y_km)),
        "principal_strike_deg": strike_deg,
        "major_spread_km": major,
        "minor_spread_km": minor,
        "elongation_ratio": elong,
    }


def build_time_bins(mainshock64: pd.Timestamp, mainshock71: pd.Timestamp) -> List[TimeBin]:
    bins: List[TimeBin] = []
    stage1_end = mainshock64 + pd.Timedelta(hours=4)
    stage1_starts = pd.date_range(mainshock64, stage1_end, freq="30min", inclusive="left")
    bin_id = 0
    for start in stage1_starts:
        end = start + pd.Timedelta(minutes=30)
        bins.append(TimeBin(bin_id, "stage1", start, end, False, bin_id // 8 + 1, bin_id % 8))
        bin_id += 1
    stage2_starts = pd.date_range(stage1_end, mainshock71, freq="2h", inclusive="left")
    for i, start in enumerate(stage2_starts):
        end = min(start + pd.Timedelta(hours=2), mainshock71)
        end_inclusive = i == len(stage2_starts) - 1
        bins.append(TimeBin(bin_id, "stage2", start, end, end_inclusive, bin_id // 8 + 1, bin_id % 8))
        bin_id += 1
    return bins


def select_time_window(df: pd.DataFrame, start: pd.Timestamp, end: pd.Timestamp, end_inclusive: bool = False) -> pd.DataFrame:
    if end_inclusive:
        mask = (df["event_time"] >= start) & (df["event_time"] <= end)
    else:
        mask = (df["event_time"] >= start) & (df["event_time"] < end)
    return df.loc[mask].copy()


def load_catalog() -> pd.DataFrame:
    log(f"Loading catalog: {CATALOG_PATH}")
    df = pd.read_csv(CATALOG_PATH)
    expected = ["event_time", "latitude", "longitude", "depth_km", "magnitude"]
    missing = [c for c in expected if c not in df.columns]
    if missing:
        raise ValueError(f"Catalog missing columns: {missing}")
    df = df[expected].copy()
    df["event_time"] = parse_utc(df["event_time"])
    df = df.dropna(subset=["event_time", "latitude", "longitude", "depth_km", "magnitude"]).copy()
    df = df.sort_values("event_time").reset_index(drop=True)
    df["event_id"] = np.arange(len(df), dtype=np.int64)
    log(f"Catalog loaded with {len(df):,} events")
    return df


def load_mainshocks() -> pd.DataFrame:
    log(f"Loading mainshocks: {MAINSHOCK_PATH}")
    df = pd.read_csv(MAINSHOCK_PATH)
    expected = ["event_time", "latitude", "longitude", "depth_km", "magnitude"]
    missing = [c for c in expected if c not in df.columns]
    if missing:
        raise ValueError(f"Mainshock file missing columns: {missing}")
    df["event_time"] = parse_utc(df["event_time"])
    df = df.sort_values("magnitude").reset_index(drop=True)
    if len(df) < 2:
        raise ValueError("Expected at least two mainshock rows")
    ms64 = df.loc[np.isclose(df["magnitude"], 6.4)]
    ms71 = df.loc[np.isclose(df["magnitude"], 7.1)]
    if ms64.empty or ms71.empty:
        raise ValueError("Could not identify Mw 6.4 and Mw 7.1 mainshocks by magnitude")
    out = pd.concat([ms64.iloc[[0]], ms71.iloc[[0]]], ignore_index=True)
    out["mainshock_label"] = ["Mainshock64", "Mainshock71"]
    if not out.loc[0, "event_time"] < out.loc[1, "event_time"]:
        raise ValueError("Mainshock64 time must be earlier than Mainshock71")
    log("Mainshocks loaded and validated")
    return out


def load_faults() -> List[List[List[float]]]:
    log(f"Loading fault polylines: {FAULT_PATH}")
    with open(FAULT_PATH, "r", encoding="utf-8") as f:
        faults = json.load(f)
    if not isinstance(faults, list):
        raise ValueError("Fault JSON must be a list of polylines")
    valid_faults = []
    for poly in faults:
        if isinstance(poly, list) and len(poly) >= 2:
            valid_faults.append(poly)
    log(f"Loaded {len(valid_faults):,} valid fault polylines")
    return valid_faults


def add_projected_coordinates(df: pd.DataFrame, lon_col: str, lat_col: str, x_col: str, y_col: str) -> pd.DataFrame:
    required = [lon_col, lat_col]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Missing coordinate columns for projection: {missing}")
    transformer = Transformer.from_crs(WGS84_CRS, LOCAL_AEQD_CRS, always_xy=True)
    x, y = transformer.transform(df[lon_col].to_numpy(), df[lat_col].to_numpy())
    df = df.copy()
    df[x_col] = x
    df[y_col] = y
    return df


def build_fault_tables(faults: List[List[List[float]]]) -> Tuple[pd.DataFrame, pd.DataFrame]:
    transformer = Transformer.from_crs(WGS84_CRS, LOCAL_AEQD_CRS, always_xy=True)
    poly_rows = []
    seg_rows = []
    segment_id = 0
    for polyline_id, poly in enumerate(tqdm(faults, desc="Building fault segment table")):
        coords = np.asarray(poly, dtype=float)
        lon = coords[:, 0]
        lat = coords[:, 1]
        x_km, y_km = transformer.transform(lon, lat)
        poly_rows.append(
            {
                "fault_id": polyline_id,
                "n_vertices": len(coords),
                "min_lon": float(np.min(lon)),
                "max_lon": float(np.max(lon)),
                "min_lat": float(np.min(lat)),
                "max_lat": float(np.max(lat)),
                "min_x_km": float(np.min(x_km)),
                "max_x_km": float(np.max(x_km)),
                "min_y_km": float(np.min(y_km)),
                "max_y_km": float(np.max(y_km)),
                "mean_strike_deg": float(
                    weighted_orientation_deg(
                        np.array([
                            strike_from_dxdy(x_km[i + 1] - x_km[i], y_km[i + 1] - y_km[i])
                            for i in range(len(x_km) - 1)
                            if (x_km[i + 1] - x_km[i]) != 0 or (y_km[i + 1] - y_km[i]) != 0
                        ]),
                        np.array([
                            math.hypot(x_km[i + 1] - x_km[i], y_km[i + 1] - y_km[i])
                            for i in range(len(x_km) - 1)
                            if (x_km[i + 1] - x_km[i]) != 0 or (y_km[i + 1] - y_km[i]) != 0
                        ]),
                    )
                ) if len(x_km) > 1 else np.nan,
            }
        )
        for i in range(len(coords) - 1):
            x1, y1 = float(x_km[i]), float(y_km[i])
            x2, y2 = float(x_km[i + 1]), float(y_km[i + 1])
            dx = x2 - x1
            dy = y2 - y1
            length_km = math.hypot(dx, dy)
            if length_km == 0:
                continue
            seg_rows.append(
                {
                    "segment_id": segment_id,
                    "fault_id": polyline_id,
                    "x1_km": x1,
                    "y1_km": y1,
                    "x2_km": x2,
                    "y2_km": y2,
                    "mid_x_km": 0.5 * (x1 + x2),
                    "mid_y_km": 0.5 * (y1 + y2),
                    "length_km": length_km,
                    "strike_deg": strike_from_dxdy(dx, dy),
                    "lon1": float(lon[i]),
                    "lat1": float(lat[i]),
                    "lon2": float(lon[i + 1]),
                    "lat2": float(lat[i + 1]),
                }
            )
            segment_id += 1
    poly_df = pd.DataFrame(poly_rows)
    seg_df = pd.DataFrame(seg_rows)
    if seg_df.empty:
        raise ValueError("No valid fault segments were generated")
    log(f"Built fault tables with {len(poly_df):,} polylines and {len(seg_df):,} segments")
    return poly_df, seg_df


def compute_extent(catalog: pd.DataFrame, mainshocks: pd.DataFrame, fault_polys: pd.DataFrame, mainshock71_time: pd.Timestamp) -> pd.DataFrame:
    relevant_events = select_time_window(catalog, mainshocks["event_time"].min(), mainshock71_time + pd.Timedelta(days=2), True)
    xmin = min(relevant_events["x_km"].min(), mainshocks["x_km"].min(), fault_polys["min_x_km"].min()) - MAP_MARGIN_KM
    xmax = max(relevant_events["x_km"].max(), mainshocks["x_km"].max(), fault_polys["max_x_km"].max()) + MAP_MARGIN_KM
    ymin = min(relevant_events["y_km"].min(), mainshocks["y_km"].min(), fault_polys["min_y_km"].min()) - MAP_MARGIN_KM
    ymax = max(relevant_events["y_km"].max(), mainshocks["y_km"].max(), fault_polys["max_y_km"].max()) + MAP_MARGIN_KM
    extent = pd.DataFrame(
        [{
            "xmin_km": float(xmin),
            "xmax_km": float(xmax),
            "ymin_km": float(ymin),
            "ymax_km": float(ymax),
        }]
    )
    return extent


def _process_event_chunk(
    event_chunk: pd.DataFrame,
    seg_arrays: Dict[str, np.ndarray],
    kdtree_data: Dict[str, np.ndarray],
    candidate_k: int,
) -> pd.DataFrame:
    tree = cKDTree(np.column_stack([kdtree_data["mid_x_km"], kdtree_data["mid_y_km"]]))
    x = event_chunk["x_km"].to_numpy()
    y = event_chunk["y_km"].to_numpy()
    k = min(candidate_k, len(kdtree_data["mid_x_km"]))
    dists, idxs = tree.query(np.column_stack([x, y]), k=k)
    if k == 1:
        idxs = idxs[:, None]
    rows = []
    for i in range(len(event_chunk)):
        px = x[i]
        py = y[i]
        best = None
        candidate_indices = np.unique(np.atleast_1d(idxs[i]).astype(int))
        for cand in candidate_indices:
            x1 = seg_arrays["x1_km"][cand]
            y1 = seg_arrays["y1_km"][cand]
            x2 = seg_arrays["x2_km"][cand]
            y2 = seg_arrays["y2_km"][cand]
            dx = x2 - x1
            dy = y2 - y1
            seg_len2 = dx * dx + dy * dy
            t = 0.0 if seg_len2 == 0 else ((px - x1) * dx + (py - y1) * dy) / seg_len2
            t_clip = min(1.0, max(0.0, t))
            qx = x1 + t_clip * dx
            qy = y1 + t_clip * dy
            dist = math.hypot(px - qx, py - qy)
            if best is None or dist < best["nearest_fault_distance_km"]:
                best = {
                    "event_id": int(event_chunk.iloc[i]["event_id"]),
                    "nearest_segment_id": int(seg_arrays["segment_id"][cand]),
                    "nearest_fault_id": int(seg_arrays["fault_id"][cand]),
                    "nearest_fault_distance_km": float(dist),
                    "nearest_point_x_km": float(qx),
                    "nearest_point_y_km": float(qy),
                    "segment_fraction": float(t_clip),
                    "segment_length_km": float(seg_arrays["length_km"][cand]),
                    "distance_along_segment_km": float(t_clip * seg_arrays["length_km"][cand]),
                    "nearest_segment_strike_deg": float(seg_arrays["strike_deg"][cand]),
                    "segment_midpoint_distance_km": float(np.atleast_1d(dists[i])[0]) if np.ndim(dists) > 1 else float(dists[i]),
                }
        rows.append(best)
    return pd.DataFrame(rows)


def compute_event_fault_metrics(events: pd.DataFrame, seg_df: pd.DataFrame, label: str) -> pd.DataFrame:
    if events.empty:
        raise ValueError(f"No events available for metric computation in window '{label}'")
    required_event_cols = ["event_id", "event_time", "x_km", "y_km", "latitude", "longitude", "depth_km", "magnitude"]
    required_seg_cols = ["segment_id", "fault_id", "x1_km", "y1_km", "x2_km", "y2_km", "mid_x_km", "mid_y_km", "length_km", "strike_deg"]
    missing_event_cols = [c for c in required_event_cols if c not in events.columns]
    missing_seg_cols = [c for c in required_seg_cols if c not in seg_df.columns]
    if missing_event_cols:
        raise ValueError(f"Event table missing required columns for nearest-fault computation: {missing_event_cols}")
    if missing_seg_cols:
        raise ValueError(f"Fault segment table missing required columns: {missing_seg_cols}")
    log(f"Computing nearest-fault metrics for {label}: {len(events):,} events")
    seg_arrays = {col: seg_df[col].to_numpy() for col in ["segment_id", "fault_id", "x1_km", "y1_km", "x2_km", "y2_km", "length_km", "strike_deg"]}
    kdtree_data = {"mid_x_km": seg_df["mid_x_km"].to_numpy(), "mid_y_km": seg_df["mid_y_km"].to_numpy()}
    chunks = [events.iloc[i : i + EVENT_CHUNK_SIZE].copy() for i in range(0, len(events), EVENT_CHUNK_SIZE)]
    results = []
    candidate_k = 24
    with ProcessPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futures = [
            ex.submit(_process_event_chunk, chunk, seg_arrays, kdtree_data, candidate_k)
            for chunk in chunks
        ]
        for fut in tqdm(as_completed(futures), total=len(futures), desc=f"Nearest-fault {label}"):
            results.append(fut.result())
    metrics = pd.concat(results, ignore_index=True)
    expected_metric_cols = [
        "event_id",
        "nearest_segment_id",
        "nearest_fault_id",
        "nearest_fault_distance_km",
        "nearest_point_x_km",
        "nearest_point_y_km",
        "segment_fraction",
        "segment_length_km",
        "distance_along_segment_km",
        "nearest_segment_strike_deg",
        "segment_midpoint_distance_km",
    ]
    missing_metric_cols = [c for c in expected_metric_cols if c not in metrics.columns]
    if missing_metric_cols:
        raise ValueError(f"Nearest-fault metric result missing columns: {missing_metric_cols}")
    merged = events.merge(metrics, on="event_id", how="left", validate="one_to_one")
    missing = merged["nearest_fault_distance_km"].isna().sum()
    if missing:
        raise ValueError(f"Nearest-fault metric computation left {missing} events without distance values")
    log(f"Completed nearest-fault metrics for {label}")
    return merged


def build_bin_table(time_bins: List[TimeBin], events_pre71: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for b in time_bins:
        if b.end_inclusive:
            in_bin = events_pre71[(events_pre71["event_time"] >= b.start) & (events_pre71["event_time"] <= b.end)]
        else:
            in_bin = events_pre71[(events_pre71["event_time"] >= b.start) & (events_pre71["event_time"] < b.end)]
        prior = events_pre71[(events_pre71["event_time"] >= time_bins[0].start) & (events_pre71["event_time"] < b.start)]
        rows.append(
            {
                "bin_id": b.bin_id,
                "stage": b.stage,
                "start_time": b.start,
                "end_time": b.end,
                "end_inclusive": b.end_inclusive,
                "page": b.page,
                "subplot_index": b.subplot_index,
                "bin_event_count": int(len(in_bin)),
                "prior_event_count": int(len(prior)),
                "elapsed_hours_since_mainshock64": float((b.start - time_bins[0].start).total_seconds() / 3600.0),
            }
        )
    return pd.DataFrame(rows)


def summarize_one_bin(bin_row: pd.Series, event_metrics: pd.DataFrame, along_origin: float, along_axis_strike_deg: float) -> Dict[str, object]:
    start = pd.Timestamp(bin_row["start_time"])
    end = pd.Timestamp(bin_row["end_time"])
    end_inclusive = bool(bin_row["end_inclusive"])
    if end_inclusive:
        in_bin = event_metrics[(event_metrics["event_time"] >= start) & (event_metrics["event_time"] <= end)].copy()
    else:
        in_bin = event_metrics[(event_metrics["event_time"] >= start) & (event_metrics["event_time"] < end)].copy()
    out: Dict[str, object] = {
        "bin_id": int(bin_row["bin_id"]),
        "stage": bin_row["stage"],
        "start_time": start,
        "end_time": end,
        "end_inclusive": end_inclusive,
        "page": int(bin_row["page"]),
        "subplot_index": int(bin_row["subplot_index"]),
        "event_count": int(len(in_bin)),
    }
    if len(in_bin) == 0:
        out.update(
            {
                "centroid_x_km": np.nan,
                "centroid_y_km": np.nan,
                "principal_strike_deg": np.nan,
                "major_spread_km": np.nan,
                "minor_spread_km": np.nan,
                "elongation_ratio": np.nan,
                "median_nearest_fault_distance_km": np.nan,
                "q25_nearest_fault_distance_km": np.nan,
                "q75_nearest_fault_distance_km": np.nan,
                "dominant_local_fault_strike_deg": np.nan,
                "angular_misfit_deg": np.nan,
                "fraction_within_0.25km": np.nan,
                "fraction_within_0.5km": np.nan,
                "fraction_within_1.0km": np.nan,
                "fraction_within_2.0km": np.nan,
                "fraction_within_5.0km": np.nan,
                "along_strike_min_km": np.nan,
                "along_strike_max_km": np.nan,
                "along_strike_range_km": np.nan,
                "newly_activated_range_km": np.nan,
                "is_sparse_for_orientation": True,
            }
        )
        return out
    required_cols = ["x_km", "y_km", "nearest_fault_distance_km", "nearest_segment_strike_deg", "nearest_point_x_km", "nearest_point_y_km"]
    missing_cols = [c for c in required_cols if c not in in_bin.columns]
    if missing_cols:
        raise ValueError(f"Bin event metrics missing required columns: {missing_cols}")
    pmetrics = principal_axis_metrics(in_bin["x_km"].to_numpy(), in_bin["y_km"].to_numpy())
    dist = in_bin["nearest_fault_distance_km"].to_numpy()
    dominant_fault_strike = weighted_orientation_deg(
        in_bin["nearest_segment_strike_deg"].to_numpy(),
        np.maximum(1.0 / np.maximum(dist, 0.05), 1e-6),
    )
    axis_rad = math.radians(along_axis_strike_deg)
    axis_dx = math.sin(axis_rad)
    axis_dy = math.cos(axis_rad)
    nearest_dx = in_bin["nearest_point_x_km"].to_numpy()
    nearest_dy = in_bin["nearest_point_y_km"].to_numpy() - along_origin
    along_strike = nearest_dx * axis_dx + nearest_dy * axis_dy
    out.update(pmetrics)
    out.update(
        {
            "median_nearest_fault_distance_km": float(np.median(dist)),
            "q25_nearest_fault_distance_km": float(np.quantile(dist, 0.25)),
            "q75_nearest_fault_distance_km": float(np.quantile(dist, 0.75)),
            "dominant_local_fault_strike_deg": dominant_fault_strike,
            "angular_misfit_deg": angular_misfit_deg(pmetrics["principal_strike_deg"], dominant_fault_strike),
            "fraction_within_0.25km": float(np.mean(dist <= 0.25)),
            "fraction_within_0.5km": float(np.mean(dist <= 0.5)),
            "fraction_within_1.0km": float(np.mean(dist <= 1.0)),
            "fraction_within_2.0km": float(np.mean(dist <= 2.0)),
            "fraction_within_5.0km": float(np.mean(dist <= 5.0)),
            "along_strike_min_km": float(np.min(along_strike)),
            "along_strike_max_km": float(np.max(along_strike)),
            "along_strike_range_km": float(np.max(along_strike) - np.min(along_strike)),
            "newly_activated_range_km": np.nan,
            "is_sparse_for_orientation": bool(len(in_bin) < SPARSE_BIN_MIN_EVENTS),
        }
    )
    return out


def compute_bin_metrics(
    bin_df: pd.DataFrame,
    event_metrics_pre71: pd.DataFrame,
    mainshock64_x: float,
    mainshock64_y: float,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    log("Computing bin-level directional and along-strike metrics")
    required_cols = ["event_id", "event_time", "nearest_point_x_km", "nearest_point_y_km", "nearest_segment_strike_deg"]
    missing_cols = [c for c in required_cols if c not in event_metrics_pre71.columns]
    if missing_cols:
        raise ValueError(f"Event metrics table missing required columns for bin summaries: {missing_cols}")
    along_axis_strike_deg = weighted_orientation_deg(
        event_metrics_pre71["nearest_segment_strike_deg"].to_numpy(),
        np.ones(len(event_metrics_pre71), dtype=float),
    )
    rows = []
    for _, bin_row in tqdm(bin_df.iterrows(), total=len(bin_df), desc="Bin summaries"):
        rows.append(summarize_one_bin(bin_row, event_metrics_pre71, mainshock64_y, along_axis_strike_deg))
    summary = pd.DataFrame(rows).sort_values("bin_id").reset_index(drop=True)

    analysis_start = pd.Timestamp(summary["start_time"].min())
    all_nearest = event_metrics_pre71[["event_id", "event_time", "nearest_point_x_km", "nearest_point_y_km"]].copy()
    axis_rad = math.radians(along_axis_strike_deg)
    axis_dx = math.sin(axis_rad)
    axis_dy = math.cos(axis_rad)
    all_nearest["along_strike_km"] = all_nearest["nearest_point_x_km"] * axis_dx + (all_nearest["nearest_point_y_km"] - mainshock64_y) * axis_dy
    min_along = float(np.floor(all_nearest["along_strike_km"].min() / ALONG_STRIKE_BIN_KM) * ALONG_STRIKE_BIN_KM)
    max_along = float(np.ceil(all_nearest["along_strike_km"].max() / ALONG_STRIKE_BIN_KM) * ALONG_STRIKE_BIN_KM)
    edges = np.arange(min_along, max_along + ALONG_STRIKE_BIN_KM, ALONG_STRIKE_BIN_KM)
    if len(edges) < 2:
        edges = np.array([min_along, min_along + ALONG_STRIKE_BIN_KM])
    all_nearest["along_strike_bin_index"] = np.clip(np.digitize(all_nearest["along_strike_km"], edges) - 1, 0, len(edges) - 2)

    first_activation = (
        all_nearest.groupby("along_strike_bin_index", as_index=False)["event_time"].min().rename(columns={"event_time": "first_activation_time"})
    )
    first_activation["along_strike_bin_start_km"] = edges[first_activation["along_strike_bin_index"]]
    first_activation["along_strike_bin_end_km"] = edges[first_activation["along_strike_bin_index"] + 1]
    first_activation["hours_since_mainshock64"] = (
        first_activation["first_activation_time"] - analysis_start
    ).dt.total_seconds() / 3600.0

    cumulative_seen: set[int] = set()
    newly_ranges = []
    cumulative_ranges = []
    cumulative_counts = []
    for _, row in summary.iterrows():
        start = pd.Timestamp(row["start_time"])
        end = pd.Timestamp(row["end_time"])
        if bool(row["end_inclusive"]):
            in_bin = all_nearest[(all_nearest["event_time"] >= start) & (all_nearest["event_time"] <= end)]
            cumulative = all_nearest[(all_nearest["event_time"] >= analysis_start) & (all_nearest["event_time"] <= end)]
        else:
            in_bin = all_nearest[(all_nearest["event_time"] >= start) & (all_nearest["event_time"] < end)]
            cumulative = all_nearest[(all_nearest["event_time"] >= analysis_start) & (all_nearest["event_time"] < end)]
        current_bins = set(in_bin["along_strike_bin_index"].astype(int).tolist())
        new_bins = current_bins - cumulative_seen
        cumulative_seen |= current_bins
        cumulative_bins = sorted(set(cumulative["along_strike_bin_index"].astype(int).tolist()))
        cumulative_counts.append(len(cumulative_bins))
        if cumulative_bins:
            cumulative_ranges.append(float(edges[max(cumulative_bins) + 1] - edges[min(cumulative_bins)]))
        else:
            cumulative_ranges.append(np.nan)
        if new_bins:
            new_bins_sorted = sorted(new_bins)
            newly_ranges.append(float(edges[max(new_bins_sorted) + 1] - edges[min(new_bins_sorted)]))
        else:
            newly_ranges.append(0.0)
    summary["newly_activated_range_km"] = newly_ranges
    summary["cumulative_occupied_range_km"] = cumulative_ranges
    summary["cumulative_occupied_bin_count"] = cumulative_counts
    summary["reference_along_axis_strike_deg"] = along_axis_strike_deg
    summary["reference_origin_x_km"] = float(mainshock64_x)
    summary["reference_origin_y_km"] = float(mainshock64_y)
    first_activation["reference_along_axis_strike_deg"] = along_axis_strike_deg
    first_activation["reference_origin_x_km"] = float(mainshock64_x)
    first_activation["reference_origin_y_km"] = float(mainshock64_y)
    return summary, first_activation.sort_values("along_strike_bin_start_km").reset_index(drop=True)


def save_dataframe(df: pd.DataFrame, name: str) -> Path:
    path = OUTPUT_DIR / name
    df.to_csv(path, index=False)
    log(f"Saved {name}: {path}")
    return path


def build_question_summary(bin_summary: pd.DataFrame) -> pd.DataFrame:
    valid = bin_summary[~bin_summary["is_sparse_for_orientation"] & bin_summary["principal_strike_deg"].notna()].copy()
    q1 = {
        "question": "Is the triggered earthquakes along the fault direction?",
        "metric_name": "median_angular_misfit_deg",
        "metric_value": float(valid["angular_misfit_deg"].median()) if not valid.empty else np.nan,
        "interpretation_hint": "Smaller values indicate stronger alignment between event-cloud orientation and local mapped fault strike.",
    }
    q2 = {
        "question": "Is the triggered earthquakes along the fault direction changing over time?",
        "metric_name": "orientation_range_deg",
        "metric_value": float(valid["principal_strike_deg"].max() - valid["principal_strike_deg"].min()) if len(valid) >= 2 else np.nan,
        "interpretation_hint": "Larger range suggests stronger temporal evolution in event-cloud orientation.",
    }
    q3 = {
        "question": "Is the triggered earthquakes cover all the fault direction simultaneously or evolving over time?",
        "metric_name": "final_cumulative_occupied_range_km",
        "metric_value": float(bin_summary["cumulative_occupied_range_km"].dropna().iloc[-1]) if bin_summary["cumulative_occupied_range_km"].notna().any() else np.nan,
        "interpretation_hint": "Compare cumulative occupied range growth through time to distinguish simultaneous broad activation from progressive expansion.",
    }
    return pd.DataFrame([q1, q2, q3])


def build_validation_summary(
    catalog: pd.DataFrame,
    events_pre71: pd.DataFrame,
    events_post71: pd.DataFrame,
    fault_polys: pd.DataFrame,
    fault_segments: pd.DataFrame,
    bins: pd.DataFrame,
    event_metrics_pre71: pd.DataFrame,
    event_metrics_post71: pd.DataFrame,
    bin_summary: pd.DataFrame,
) -> pd.DataFrame:
    rows = [
        {"check": "catalog_event_count", "value": int(len(catalog))},
        {"check": "pre71_event_count", "value": int(len(events_pre71))},
        {"check": "post71_event_count", "value": int(len(events_post71))},
        {"check": "fault_polyline_count", "value": int(len(fault_polys))},
        {"check": "fault_segment_count", "value": int(len(fault_segments))},
        {"check": "time_bin_count", "value": int(len(bins))},
        {"check": "event_metrics_pre71_count", "value": int(len(event_metrics_pre71))},
        {"check": "event_metrics_post71_count", "value": int(len(event_metrics_post71))},
        {"check": "bin_summary_count", "value": int(len(bin_summary))},
        {"check": "empty_bins", "value": int((bin_summary["event_count"] == 0).sum())},
        {"check": "sparse_orientation_bins", "value": int(bin_summary["is_sparse_for_orientation"].sum())},
        {"check": "max_workers_used", "value": int(MAX_WORKERS)},
    ]
    return pd.DataFrame(rows)


def main() -> None:
    ensure_output_dir()
    log(f"Script path: {SCRIPT_PATH}")
    log(f"Output directory: {OUTPUT_DIR}")
    catalog = load_catalog()
    mainshocks = load_mainshocks()
    mainshocks = add_projected_coordinates(mainshocks, "longitude", "latitude", "x_km", "y_km")
    catalog = add_projected_coordinates(catalog, "longitude", "latitude", "x_km", "y_km")
    faults = load_faults()
    fault_polys, fault_segments = build_fault_tables(faults)

    mainshock64 = pd.Timestamp(mainshocks.loc[mainshocks["mainshock_label"] == "Mainshock64", "event_time"].iloc[0])
    mainshock71 = pd.Timestamp(mainshocks.loc[mainshocks["mainshock_label"] == "Mainshock71", "event_time"].iloc[0])
    post71_end = mainshock71 + pd.Timedelta(days=2)
    extent_df = compute_extent(catalog, mainshocks, fault_polys, mainshock71)
    time_bins = build_time_bins(mainshock64, mainshock71)
    time_bin_df = build_bin_table(time_bins, select_time_window(catalog, mainshock64, mainshock71, True))

    events_pre71 = select_time_window(catalog, mainshock64, mainshock71, True)
    events_post71 = select_time_window(catalog, mainshock71, post71_end, True)
    if events_pre71.empty:
        raise ValueError("No catalog events found in [mainshock64, mainshock71]")
    if events_post71.empty:
        raise ValueError("No catalog events found in [mainshock71, mainshock71 + 2 days]")

    event_metrics_pre71 = compute_event_fault_metrics(events_pre71, fault_segments, "pre71")
    event_metrics_post71 = compute_event_fault_metrics(events_post71, fault_segments, "post71")
    ms64_row = mainshocks.loc[mainshocks["mainshock_label"] == "Mainshock64"].iloc[0]
    bin_summary, first_activation = compute_bin_metrics(
        time_bin_df,
        event_metrics_pre71,
        float(ms64_row["x_km"]),
        float(ms64_row["y_km"]),
    )
    question_summary = build_question_summary(bin_summary)
    validation_summary = build_validation_summary(
        catalog,
        events_pre71,
        events_post71,
        fault_polys,
        fault_segments,
        time_bin_df,
        event_metrics_pre71,
        event_metrics_post71,
        bin_summary,
    )

    save_dataframe(catalog, "catalog_clean_projected.csv")
    save_dataframe(mainshocks, "mainshock_reference.csv")
    save_dataframe(fault_polys, "fault_polylines_summary.csv")
    save_dataframe(fault_segments, "fault_segments_projected.csv")
    save_dataframe(extent_df, "canonical_map_extent.csv")
    save_dataframe(time_bin_df, "canonical_time_bins.csv")
    save_dataframe(event_metrics_pre71, "event_fault_metrics_pre71.csv")
    save_dataframe(event_metrics_post71, "event_fault_metrics_post71.csv")
    save_dataframe(bin_summary, "bin_directional_summary.csv")
    save_dataframe(first_activation, "along_strike_first_activation.csv")
    save_dataframe(question_summary, "question_metric_summary.csv")
    save_dataframe(validation_summary, "validation_summary.csv")
    metadata = pd.DataFrame(
        [
            {"key": "local_projected_crs", "value": LOCAL_AEQD_CRS.to_proj4()},
            {"key": "max_workers", "value": str(MAX_WORKERS)},
            {"key": "event_chunk_size", "value": str(EVENT_CHUNK_SIZE)},
            {"key": "along_strike_bin_km", "value": str(ALONG_STRIKE_BIN_KM)},
            {"key": "sparse_bin_min_events", "value": str(SPARSE_BIN_MIN_EVENTS)},
            {"key": "near_fault_thresholds_km", "value": ",".join(map(str, NEAR_FAULT_THRESHOLDS_KM))},
        ]
    )
    save_dataframe(metadata, "run_metadata.csv")
    log("01_ridgecrest_metrics_preparation completed successfully")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print(traceback.format_exc(), flush=True)
        sys.exit(1)
