from __future__ import annotations

import json
import math
import os
import sys
import traceback
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from joblib import Parallel, delayed
from scipy.spatial import ConvexHull, QhullError
from sklearn.cluster import DBSCAN

INPUT_DIR = Path(
    "<REPO_ROOT>/examples/ridgecrest/catalog_analysis/run/01_1_trigger_spatiotemporal_Q1-v1/exp_run/outputs/01_catalog_windows_qc"
)
OUTPUT_DIR = Path(
    "<REPO_ROOT>/examples/ridgecrest/catalog_analysis/run/01_1_trigger_spatiotemporal_Q1-v1/exp_run/outputs/02_spatiotemporal_metrics"
)
SCRIPT_PATH = Path(
    "<REPO_ROOT>/examples/ridgecrest/catalog_analysis/run/01_1_trigger_spatiotemporal_Q1-v1/exp_run/scripts/02_spatiotemporal_metrics.py"
)

CATALOG_CLEAN_PATH = INPUT_DIR / "ridgecrest_catalog_clean.csv"
MAINSHOCK_PATH = INPUT_DIR / "mainshock_reference_verified.csv"
WHOLE_WINDOWS_PATH = INPUT_DIR / "time_windows_whole_sequence.csv"
POST64_WINDOWS_PATH = INPUT_DIR / "time_windows_post64_hourly.csv"
COMPARISON_PATH = INPUT_DIR / "time_windows_comparison_intervals.csv"
EXTENT_PATH = INPUT_DIR / "analysis_extent.json"

MAX_CORES = min(64, os.cpu_count() or 1)
N_JOBS = max(1, min(MAX_CORES, 16))
ORIENTATION_MIN_EVENTS = 3
AREA_MIN_EVENTS = 3
CLUSTER_MIN_EVENTS = 5
DBSCAN_EPS_KM = 2.5
DBSCAN_MIN_SAMPLES = 12
GRID_STEP_KM = 2.0
HOTSPOT_BANDWIDTH_KM = 3.0
COMPARISON_INTERVAL_METRIC_COLUMNS = [
    "comparison_label",
    "interval_role",
    "start_time",
    "end_time",
    "duration_hours",
    "n_events",
    "magnitude_min",
    "magnitude_max",
    "magnitude_mean",
    "magnitude_median",
    "depth_mean_km",
    "depth_median_km",
    "centroid_x_km_local",
    "centroid_y_km_local",
    "centroid_longitude",
    "centroid_latitude",
    "principal_axis_azimuth_deg",
    "major_spread_km",
    "minor_spread_km",
    "anisotropy_ratio",
    "spatial_footprint_area_km2",
    "along_strike_centroid_km",
    "cross_strike_centroid_km",
    "along_strike_spread_km",
    "cross_strike_spread_km",
    "centroid_distance_to_mainshock64_km",
    "centroid_azimuth_from_mainshock64_deg",
    "centroid_distance_to_mainshock71_km",
    "centroid_azimuth_from_mainshock71_deg",
    "hotspot_x_km_local",
    "hotspot_y_km_local",
    "hotspot_density_value",
]
COMPARISON_CHANGE_COLUMNS = [
    "comparison_label",
    "before_interval_role",
    "after_interval_role",
    "before_event_count",
    "after_event_count",
    "event_count_change",
    "centroid_shift_dx_km",
    "centroid_shift_dy_km",
    "centroid_shift_distance_km",
    "centroid_shift_azimuth_deg",
    "principal_axis_orientation_change_deg",
    "occupied_area_change_km2",
    "along_strike_centroid_change_km",
    "cross_strike_centroid_change_km",
    "hotspot_shift_dx_km",
    "hotspot_shift_dy_km",
    "hotspot_shift_distance_km",
    "hotspot_shift_azimuth_deg",
]
STALE_OUTPUT_FILENAMES = [
    "window_metrics_whole_sequence.csv",
    "window_metrics_post64_hourly.csv",
    "window_cluster_metrics_whole_sequence.csv",
    "window_cluster_metrics_post64_hourly.csv",
    "comparison_metrics_64.csv",
    "comparison_metrics_71.csv",
    "migration_summary_64_to_71.json",
    "migration_summary_post71.json",
    "metrics_runtime_config.json",
]

REQUIRED_CATALOG_COLUMNS = [
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
REQUIRED_WINDOW_COLUMNS = [
    "global_window_id",
    "window_family",
    "stage_label",
    "window_index",
    "window_label",
    "start_time",
    "end_time",
    "duration_hours",
    "is_terminal_partial_window",
]
REQUIRED_COMPARISON_COLUMNS = [
    "comparison_label",
    "interval_role",
    "start_time",
    "end_time",
    "duration_hours",
]


@dataclass(frozen=True)
class MainshockRef:
    label: str
    time: pd.Timestamp
    longitude: float
    latitude: float
    x_km_local: float
    y_km_local: float


@dataclass(frozen=True)
class AxisReference:
    ux: float
    uy: float
    vx: float
    vy: float
    azimuth_deg: float
    length_km: float


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


def read_json(path: Path) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def parse_time_columns(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    out = df.copy()
    for col in columns:
        out[col] = pd.to_datetime(out[col], utc=True, errors="raise")
    return out


def assert_columns(df: pd.DataFrame, expected: list[str], df_name: str) -> None:
    missing = [col for col in expected if col not in df.columns]
    if missing:
        raise ValueError(f"{df_name} missing required columns: {missing}")


def read_catalog() -> pd.DataFrame:
    log(f"[INFO] Reading catalog: {CATALOG_CLEAN_PATH}")
    df = pd.read_csv(CATALOG_CLEAN_PATH)
    assert_columns(df, REQUIRED_CATALOG_COLUMNS, "catalog")
    df = parse_time_columns(df, ["event_time"])
    for col in [
        "latitude",
        "longitude",
        "depth_km",
        "magnitude",
        "x_km_local",
        "y_km_local",
        "elapsed_hours_since_mainshock64",
        "elapsed_hours_since_mainshock71",
    ]:
        df[col] = pd.to_numeric(df[col], errors="raise")
    df = df.sort_values("event_time", kind="mergesort").reset_index(drop=True)
    return df


def read_mainshocks(catalog: pd.DataFrame) -> dict[str, MainshockRef]:
    log(f"[INFO] Reading mainshock reference: {MAINSHOCK_PATH}")
    df = pd.read_csv(MAINSHOCK_PATH)
    assert_columns(df, ["mainshock_label", "event_time", "latitude", "longitude", "depth_km", "magnitude"], "mainshocks")
    df = parse_time_columns(df, ["event_time"])
    refs: dict[str, MainshockRef] = {}
    for _, row in df.iterrows():
        lon = float(row["longitude"])
        lat = float(row["latitude"])
        x, y = project_to_local_xy(
            longitude=np.array([lon]),
            latitude=np.array([lat]),
            origin_lon=float(catalog.attrs["projection_origin_longitude"]),
            origin_lat=float(catalog.attrs["projection_origin_latitude"]),
        )
        refs[str(row["mainshock_label"])] = MainshockRef(
            label=str(row["mainshock_label"]),
            time=pd.Timestamp(row["event_time"]),
            longitude=lon,
            latitude=lat,
            x_km_local=float(x[0]),
            y_km_local=float(y[0]),
        )
    if set(refs) != {"mainshock64", "mainshock71"}:
        raise ValueError(f"Unexpected mainshock labels: {sorted(refs)}")
    return refs


def read_windows(path: Path, expected: list[str], label: str) -> pd.DataFrame:
    log(f"[INFO] Reading {label}: {path}")
    df = pd.read_csv(path)
    assert_columns(df, expected, label)
    time_cols = [col for col in ["start_time", "end_time"] if col in df.columns]
    df = parse_time_columns(df, time_cols)
    return df


def project_to_local_xy(longitude: np.ndarray, latitude: np.ndarray, origin_lon: float, origin_lat: float) -> tuple[np.ndarray, np.ndarray]:
    earth_radius_km = 6371.0
    lon_rad = np.deg2rad(longitude)
    lat_rad = np.deg2rad(latitude)
    origin_lon_rad = math.radians(origin_lon)
    origin_lat_rad = math.radians(origin_lat)
    x = earth_radius_km * (lon_rad - origin_lon_rad) * math.cos(origin_lat_rad)
    y = earth_radius_km * (lat_rad - origin_lat_rad)
    return x, y


def attach_projection_origin(catalog: pd.DataFrame, extent: dict[str, Any]) -> pd.DataFrame:
    required_keys = ["projection_origin_longitude", "projection_origin_latitude"]
    missing = [key for key in required_keys if key not in extent]
    if missing:
        raise ValueError(f"analysis_extent.json missing required keys: {missing}")
    out = catalog.copy()
    out.attrs["projection_origin_longitude"] = float(extent["projection_origin_longitude"])
    out.attrs["projection_origin_latitude"] = float(extent["projection_origin_latitude"])
    return out


def compute_axis_reference(ms64: MainshockRef, ms71: MainshockRef) -> AxisReference:
    dx = ms71.x_km_local - ms64.x_km_local
    dy = ms71.y_km_local - ms64.y_km_local
    length = float(math.hypot(dx, dy))
    if length <= 0.0:
        raise ValueError("Mainshock64 and Mainshock71 epicenters are colocated in projected coordinates")
    ux = dx / length
    uy = dy / length
    vx = -uy
    vy = ux
    azimuth = azimuth_from_components(dx, dy)
    return AxisReference(ux=ux, uy=uy, vx=vx, vy=vy, azimuth_deg=azimuth, length_km=length)


def azimuth_from_components(dx: float, dy: float) -> float:
    return float((math.degrees(math.atan2(dx, dy)) + 360.0) % 360.0)


def circular_difference_deg(a: float | None, b: float | None) -> float | None:
    if a is None or b is None or pd.isna(a) or pd.isna(b):
        return None
    diff = (float(a) - float(b) + 180.0) % 360.0 - 180.0
    return float(abs(diff))


def robust_area_km2(x: np.ndarray, y: np.ndarray) -> float | None:
    if len(x) < AREA_MIN_EVENTS:
        return None
    points = np.column_stack([x, y])
    if np.allclose(points[:, 0], points[0, 0]) and np.allclose(points[:, 1], points[0, 1]):
        return 0.0
    try:
        hull = ConvexHull(points)
        return float(hull.volume)
    except QhullError:
        return None


def principal_axis_metrics(x: np.ndarray, y: np.ndarray) -> dict[str, float | None]:
    if len(x) < ORIENTATION_MIN_EVENTS:
        return {
            "principal_axis_azimuth_deg": None,
            "major_spread_km": None,
            "minor_spread_km": None,
            "anisotropy_ratio": None,
        }
    coords = np.column_stack([x, y])
    centered = coords - coords.mean(axis=0, keepdims=True)
    cov = np.cov(centered, rowvar=False)
    if cov.shape != (2, 2) or not np.all(np.isfinite(cov)):
        return {
            "principal_axis_azimuth_deg": None,
            "major_spread_km": None,
            "minor_spread_km": None,
            "anisotropy_ratio": None,
        }
    eigvals, eigvecs = np.linalg.eigh(cov)
    order = np.argsort(eigvals)[::-1]
    eigvals = eigvals[order]
    eigvecs = eigvecs[:, order]
    major = max(float(eigvals[0]), 0.0)
    minor = max(float(eigvals[1]), 0.0)
    major_vec = eigvecs[:, 0]
    azimuth = azimuth_from_components(float(major_vec[0]), float(major_vec[1]))
    major_spread = math.sqrt(major)
    minor_spread = math.sqrt(minor)
    ratio = None if minor_spread == 0.0 else float(major_spread / minor_spread)
    return {
        "principal_axis_azimuth_deg": float(azimuth),
        "major_spread_km": float(major_spread),
        "minor_spread_km": float(minor_spread),
        "anisotropy_ratio": ratio,
    }


def centroid_metrics(x: np.ndarray, y: np.ndarray, lon: np.ndarray, lat: np.ndarray) -> dict[str, float | None]:
    if len(x) == 0:
        return {
            "centroid_x_km_local": None,
            "centroid_y_km_local": None,
            "centroid_longitude": None,
            "centroid_latitude": None,
        }
    return {
        "centroid_x_km_local": float(np.mean(x)),
        "centroid_y_km_local": float(np.mean(y)),
        "centroid_longitude": float(np.mean(lon)),
        "centroid_latitude": float(np.mean(lat)),
    }


def distance_and_azimuth_from_point(cx: float | None, cy: float | None, px: float, py: float) -> tuple[float | None, float | None]:
    if cx is None or cy is None:
        return None, None
    dx = float(cx - px)
    dy = float(cy - py)
    return float(math.hypot(dx, dy)), azimuth_from_components(dx, dy)


def axis_projection_metrics(x: np.ndarray, y: np.ndarray, origin_x: float, origin_y: float, axis_ref: AxisReference) -> dict[str, float | None]:
    if len(x) == 0:
        return {
            "along_strike_centroid_km": None,
            "cross_strike_centroid_km": None,
            "along_strike_spread_km": None,
            "cross_strike_spread_km": None,
        }
    dx = x - origin_x
    dy = y - origin_y
    along = dx * axis_ref.ux + dy * axis_ref.uy
    cross = dx * axis_ref.vx + dy * axis_ref.vy
    return {
        "along_strike_centroid_km": float(np.mean(along)),
        "cross_strike_centroid_km": float(np.mean(cross)),
        "along_strike_spread_km": float(np.std(along, ddof=1)) if len(along) >= 2 else 0.0,
        "cross_strike_spread_km": float(np.std(cross, ddof=1)) if len(cross) >= 2 else 0.0,
    }


def summarize_magnitudes(mag: np.ndarray, depth: np.ndarray) -> dict[str, float | None]:
    if len(mag) == 0:
        return {
            "magnitude_min": None,
            "magnitude_max": None,
            "magnitude_mean": None,
            "magnitude_median": None,
            "depth_mean_km": None,
            "depth_median_km": None,
        }
    return {
        "magnitude_min": float(np.min(mag)),
        "magnitude_max": float(np.max(mag)),
        "magnitude_mean": float(np.mean(mag)),
        "magnitude_median": float(np.median(mag)),
        "depth_mean_km": float(np.mean(depth)),
        "depth_median_km": float(np.median(depth)),
    }


def density_center(x: np.ndarray, y: np.ndarray, step_km: float, bandwidth_km: float) -> tuple[float | None, float | None, float | None]:
    if len(x) == 0:
        return None, None, None
    if len(x) == 1:
        return float(x[0]), float(y[0]), 1.0
    xmin, xmax = float(np.min(x)), float(np.max(x))
    ymin, ymax = float(np.min(y)), float(np.max(y))
    x_grid = np.arange(xmin - step_km, xmax + step_km + step_km, step_km)
    y_grid = np.arange(ymin - step_km, ymax + step_km + step_km, step_km)
    xx, yy = np.meshgrid(x_grid, y_grid)
    dens = np.zeros_like(xx, dtype=float)
    inv_two_sigma2 = 1.0 / (2.0 * bandwidth_km * bandwidth_km)
    for xi, yi in zip(x, y):
        dens += np.exp(-(((xx - xi) ** 2 + (yy - yi) ** 2) * inv_two_sigma2))
    idx = np.unravel_index(np.argmax(dens), dens.shape)
    return float(xx[idx]), float(yy[idx]), float(dens[idx])


def compute_window_metrics_record(
    window_row: dict[str, Any],
    catalog: pd.DataFrame,
    ms64: MainshockRef,
    ms71: MainshockRef,
    axis_ref: AxisReference,
) -> dict[str, Any]:
    start = pd.Timestamp(window_row["start_time"])
    end = pd.Timestamp(window_row["end_time"])
    subset = catalog.loc[(catalog["event_time"] >= start) & (catalog["event_time"] < end)].copy()
    n_events = int(len(subset))

    x = subset["x_km_local"].to_numpy(dtype=float)
    y = subset["y_km_local"].to_numpy(dtype=float)
    lon = subset["longitude"].to_numpy(dtype=float)
    lat = subset["latitude"].to_numpy(dtype=float)
    mag = subset["magnitude"].to_numpy(dtype=float)
    depth = subset["depth_km"].to_numpy(dtype=float)

    centroid = centroid_metrics(x, y, lon, lat)
    axis_metrics = principal_axis_metrics(x, y)
    area = robust_area_km2(x, y)
    mag_metrics = summarize_magnitudes(mag, depth)
    proj_metrics = axis_projection_metrics(x, y, ms64.x_km_local, ms64.y_km_local, axis_ref)

    dist64, az64 = distance_and_azimuth_from_point(
        centroid["centroid_x_km_local"], centroid["centroid_y_km_local"], ms64.x_km_local, ms64.y_km_local
    )
    dist71, az71 = distance_and_azimuth_from_point(
        centroid["centroid_x_km_local"], centroid["centroid_y_km_local"], ms71.x_km_local, ms71.y_km_local
    )

    record = {
        **window_row,
        "n_events": n_events,
        **mag_metrics,
        **centroid,
        **axis_metrics,
        "spatial_footprint_area_km2": area,
        **proj_metrics,
        "centroid_distance_to_mainshock64_km": dist64,
        "centroid_azimuth_from_mainshock64_deg": az64,
        "centroid_distance_to_mainshock71_km": dist71,
        "centroid_azimuth_from_mainshock71_deg": az71,
        "window_mid_time": start + (end - start) / 2,
        "window_start_hours_since_mainshock64": (start - ms64.time).total_seconds() / 3600.0,
        "window_end_hours_since_mainshock64": (end - ms64.time).total_seconds() / 3600.0,
        "window_start_hours_since_mainshock71": (start - ms71.time).total_seconds() / 3600.0,
        "window_end_hours_since_mainshock71": (end - ms71.time).total_seconds() / 3600.0,
        "orientation_event_count_sufficient": bool(n_events >= ORIENTATION_MIN_EVENTS),
        "cluster_event_count_sufficient": bool(n_events >= CLUSTER_MIN_EVENTS),
    }
    return record


def compute_cluster_metrics_record(
    window_row: dict[str, Any],
    catalog: pd.DataFrame,
    ms64: MainshockRef,
    axis_ref: AxisReference,
) -> dict[str, Any]:
    start = pd.Timestamp(window_row["start_time"])
    end = pd.Timestamp(window_row["end_time"])
    subset = catalog.loc[(catalog["event_time"] >= start) & (catalog["event_time"] < end)].copy()
    n_events = int(len(subset))

    base_record = {
        "global_window_id": int(window_row["global_window_id"]),
        "window_family": window_row["window_family"],
        "stage_label": window_row["stage_label"],
        "window_index": int(window_row["window_index"]),
        "window_label": window_row["window_label"],
        "start_time": start,
        "end_time": end,
        "n_events": n_events,
        "dbscan_eps_km": DBSCAN_EPS_KM,
        "dbscan_min_samples": DBSCAN_MIN_SAMPLES,
        "n_clusters": 0,
        "n_noise_events": n_events,
        "clustered_event_fraction": 0.0 if n_events > 0 else None,
        "dominant_cluster_fraction": None,
        "dominant_cluster_event_count": None,
        "dominant_cluster_centroid_longitude": None,
        "dominant_cluster_centroid_latitude": None,
        "dominant_cluster_centroid_x_km_local": None,
        "dominant_cluster_centroid_y_km_local": None,
        "dominant_cluster_azimuth_from_mainshock64_deg": None,
        "dominant_cluster_distance_from_mainshock64_km": None,
        "dominant_cluster_along_strike_km": None,
        "dominant_cluster_cross_strike_km": None,
        "cluster_size_json": json.dumps([], sort_keys=True),
        "cluster_centroids_json": json.dumps([], sort_keys=True),
        "cluster_azimuths_from_mainshock64_json": json.dumps([], sort_keys=True),
    }
    if n_events < CLUSTER_MIN_EVENTS:
        return base_record

    coords = subset[["x_km_local", "y_km_local"]].to_numpy(dtype=float)
    labels = DBSCAN(eps=DBSCAN_EPS_KM, min_samples=DBSCAN_MIN_SAMPLES, n_jobs=1).fit_predict(coords)
    unique_clusters = sorted([int(v) for v in np.unique(labels) if v >= 0])
    n_noise = int(np.sum(labels < 0))
    cluster_sizes: list[dict[str, Any]] = []
    centroid_payload: list[dict[str, Any]] = []
    az_payload: list[dict[str, Any]] = []
    dominant_label = None
    dominant_size = -1
    dominant_info: dict[str, Any] | None = None

    for cluster_id in unique_clusters:
        mask = labels == cluster_id
        cluster = subset.loc[mask].copy()
        size = int(len(cluster))
        cx = float(cluster["x_km_local"].mean())
        cy = float(cluster["y_km_local"].mean())
        clon = float(cluster["longitude"].mean())
        clat = float(cluster["latitude"].mean())
        dist, az = distance_and_azimuth_from_point(cx, cy, ms64.x_km_local, ms64.y_km_local)
        along = (cx - ms64.x_km_local) * axis_ref.ux + (cy - ms64.y_km_local) * axis_ref.uy
        cross = (cx - ms64.x_km_local) * axis_ref.vx + (cy - ms64.y_km_local) * axis_ref.vy
        cluster_sizes.append({"cluster_id": cluster_id, "n_events": size})
        centroid_payload.append(
            {
                "cluster_id": cluster_id,
                "x_km_local": cx,
                "y_km_local": cy,
                "longitude": clon,
                "latitude": clat,
                "n_events": size,
                "along_strike_km": float(along),
                "cross_strike_km": float(cross),
            }
        )
        az_payload.append(
            {
                "cluster_id": cluster_id,
                "azimuth_from_mainshock64_deg": az,
                "distance_from_mainshock64_km": dist,
            }
        )
        if size > dominant_size:
            dominant_label = cluster_id
            dominant_size = size
            dominant_info = {
                "centroid_longitude": clon,
                "centroid_latitude": clat,
                "centroid_x_km_local": cx,
                "centroid_y_km_local": cy,
                "azimuth": az,
                "distance": dist,
                "along": float(along),
                "cross": float(cross),
            }

    clustered_events = int(np.sum(labels >= 0))
    base_record["n_clusters"] = int(len(unique_clusters))
    base_record["n_noise_events"] = n_noise
    base_record["clustered_event_fraction"] = float(clustered_events / n_events) if n_events > 0 else None
    if dominant_label is not None and dominant_info is not None:
        base_record["dominant_cluster_fraction"] = float(dominant_size / n_events)
        base_record["dominant_cluster_event_count"] = int(dominant_size)
        base_record["dominant_cluster_centroid_longitude"] = float(dominant_info["centroid_longitude"])
        base_record["dominant_cluster_centroid_latitude"] = float(dominant_info["centroid_latitude"])
        base_record["dominant_cluster_centroid_x_km_local"] = float(dominant_info["centroid_x_km_local"])
        base_record["dominant_cluster_centroid_y_km_local"] = float(dominant_info["centroid_y_km_local"])
        base_record["dominant_cluster_azimuth_from_mainshock64_deg"] = dominant_info["azimuth"]
        base_record["dominant_cluster_distance_from_mainshock64_km"] = dominant_info["distance"]
        base_record["dominant_cluster_along_strike_km"] = float(dominant_info["along"])
        base_record["dominant_cluster_cross_strike_km"] = float(dominant_info["cross"])
    base_record["cluster_size_json"] = json.dumps(cluster_sizes, sort_keys=True)
    base_record["cluster_centroids_json"] = json.dumps(centroid_payload, sort_keys=True)
    base_record["cluster_azimuths_from_mainshock64_json"] = json.dumps(az_payload, sort_keys=True)
    return base_record


def add_consecutive_migration_metrics(metrics_df: pd.DataFrame, stage_group_columns: list[str]) -> pd.DataFrame:
    assert_columns(
        metrics_df,
        [
            *stage_group_columns,
            "window_index",
            "centroid_x_km_local",
            "centroid_y_km_local",
            "principal_axis_azimuth_deg",
        ],
        "metrics_df_before_migration",
    )
    out = metrics_df.sort_values(stage_group_columns + ["window_index"], kind="mergesort").copy()
    out["prev_centroid_x_km_local"] = out.groupby(stage_group_columns)["centroid_x_km_local"].shift(1)
    out["prev_centroid_y_km_local"] = out.groupby(stage_group_columns)["centroid_y_km_local"].shift(1)
    out["prev_principal_axis_azimuth_deg"] = out.groupby(stage_group_columns)["principal_axis_azimuth_deg"].shift(1)
    dx = out["centroid_x_km_local"] - out["prev_centroid_x_km_local"]
    dy = out["centroid_y_km_local"] - out["prev_centroid_y_km_local"]
    valid = dx.notna() & dy.notna()
    out["centroid_step_dx_km"] = np.where(valid, dx, np.nan)
    out["centroid_step_dy_km"] = np.where(valid, dy, np.nan)
    out["centroid_step_distance_km"] = np.where(valid, np.hypot(dx, dy), np.nan)
    out["centroid_step_azimuth_deg"] = np.where(valid, np.degrees(np.arctan2(dx, dy)), np.nan)
    out["centroid_step_azimuth_deg"] = (out["centroid_step_azimuth_deg"] + 360.0) % 360.0
    out["principal_axis_azimuth_change_deg"] = [
        circular_difference_deg(a, b)
        for a, b in zip(out["principal_axis_azimuth_deg"], out["prev_principal_axis_azimuth_deg"])
    ]
    out["cumulative_centroid_distance_km"] = out.groupby(stage_group_columns)["centroid_step_distance_km"].transform(
        lambda s: s.fillna(0.0).cumsum()
    )
    return out


def compute_window_family_metrics(
    windows_df: pd.DataFrame,
    catalog: pd.DataFrame,
    ms64: MainshockRef,
    ms71: MainshockRef,
    axis_ref: AxisReference,
    family_label: str,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    assert_columns(windows_df, REQUIRED_WINDOW_COLUMNS, f"{family_label}_windows_df")
    assert_columns(catalog, REQUIRED_CATALOG_COLUMNS, f"{family_label}_catalog")
    log(f"[INFO] Computing window metrics for {family_label}: n_windows={len(windows_df)}, n_jobs={N_JOBS}")
    rows = windows_df.to_dict(orient="records")
    metric_records = Parallel(n_jobs=N_JOBS, backend="loky", verbose=0)(
        delayed(compute_window_metrics_record)(row, catalog, ms64, ms71, axis_ref) for row in rows
    )
    cluster_records = Parallel(n_jobs=N_JOBS, backend="loky", verbose=0)(
        delayed(compute_cluster_metrics_record)(row, catalog, ms64, axis_ref) for row in rows
    )
    metrics_df = pd.DataFrame(metric_records)
    cluster_df = pd.DataFrame(cluster_records)
    assert_columns(
        metrics_df,
        [
            *REQUIRED_WINDOW_COLUMNS,
            "n_events",
            "centroid_x_km_local",
            "centroid_y_km_local",
            "principal_axis_azimuth_deg",
        ],
        f"{family_label}_metrics_df",
    )
    assert_columns(
        cluster_df,
        [
            "global_window_id",
            "window_family",
            "stage_label",
            "window_index",
            "window_label",
            "start_time",
            "end_time",
            "n_events",
            "n_clusters",
            "dominant_cluster_fraction",
            "clustered_event_fraction",
        ],
        f"{family_label}_cluster_df",
    )
    metrics_df = add_consecutive_migration_metrics(metrics_df, ["window_family", "stage_label"])
    log(f"[INFO] Completed {family_label}: metrics_rows={len(metrics_df)}, cluster_rows={len(cluster_df)}")
    return metrics_df, cluster_df


def compute_interval_summary(
    subset: pd.DataFrame,
    label: str,
    role: str,
    ms64: MainshockRef,
    ms71: MainshockRef,
    axis_ref: AxisReference,
) -> dict[str, Any]:
    n_events = int(len(subset))
    x = subset["x_km_local"].to_numpy(dtype=float)
    y = subset["y_km_local"].to_numpy(dtype=float)
    lon = subset["longitude"].to_numpy(dtype=float)
    lat = subset["latitude"].to_numpy(dtype=float)
    mag = subset["magnitude"].to_numpy(dtype=float)
    depth = subset["depth_km"].to_numpy(dtype=float)

    centroid = centroid_metrics(x, y, lon, lat)
    axis_metrics = principal_axis_metrics(x, y)
    proj_metrics = axis_projection_metrics(x, y, ms64.x_km_local, ms64.y_km_local, axis_ref)
    mag_metrics = summarize_magnitudes(mag, depth)
    area = robust_area_km2(x, y)
    d64, a64 = distance_and_azimuth_from_point(
        centroid["centroid_x_km_local"], centroid["centroid_y_km_local"], ms64.x_km_local, ms64.y_km_local
    )
    d71, a71 = distance_and_azimuth_from_point(
        centroid["centroid_x_km_local"], centroid["centroid_y_km_local"], ms71.x_km_local, ms71.y_km_local
    )
    hx, hy, hd = density_center(x, y, step_km=GRID_STEP_KM, bandwidth_km=HOTSPOT_BANDWIDTH_KM)
    return {
        "comparison_label": label,
        "interval_role": role,
        "n_events": n_events,
        **mag_metrics,
        **centroid,
        **axis_metrics,
        "spatial_footprint_area_km2": area,
        **proj_metrics,
        "centroid_distance_to_mainshock64_km": d64,
        "centroid_azimuth_from_mainshock64_deg": a64,
        "centroid_distance_to_mainshock71_km": d71,
        "centroid_azimuth_from_mainshock71_deg": a71,
        "hotspot_x_km_local": hx,
        "hotspot_y_km_local": hy,
        "hotspot_density_value": hd,
    }


def finalize_comparison_metrics(
    intervals_df: pd.DataFrame,
    catalog: pd.DataFrame,
    ms64: MainshockRef,
    ms71: MainshockRef,
    axis_ref: AxisReference,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    records = []
    for _, row in intervals_df.iterrows():
        start = pd.Timestamp(row["start_time"])
        end = pd.Timestamp(row["end_time"])
        subset = catalog.loc[(catalog["event_time"] >= start) & (catalog["event_time"] < end)].copy()
        rec = compute_interval_summary(
            subset=subset,
            label=str(row["comparison_label"]),
            role=str(row["interval_role"]),
            ms64=ms64,
            ms71=ms71,
            axis_ref=axis_ref,
        )
        rec["start_time"] = start
        rec["end_time"] = end
        rec["duration_hours"] = float(row["duration_hours"])
        records.append(rec)
    df = pd.DataFrame(records).sort_values(["comparison_label", "interval_role"], kind="mergesort").reset_index(drop=True)
    assert_columns(df, COMPARISON_INTERVAL_METRIC_COLUMNS, "comparison_interval_metrics")

    change_rows = []
    for label, group in df.groupby("comparison_label", sort=False):
        before = group.loc[group["interval_role"] == "before"]
        after = group.loc[group["interval_role"] == "after"]
        if len(before) != 1 or len(after) != 1:
            raise ValueError(f"Expected one before and one after interval for comparison {label}")
        b = before.iloc[0]
        a = after.iloc[0]
        dx = None
        dy = None
        dist = None
        az = None
        if pd.notna(b["centroid_x_km_local"]) and pd.notna(a["centroid_x_km_local"]):
            dx = float(a["centroid_x_km_local"] - b["centroid_x_km_local"])
            dy = float(a["centroid_y_km_local"] - b["centroid_y_km_local"])
            dist = float(math.hypot(dx, dy))
            az = azimuth_from_components(dx, dy)
        hdx = None
        hdy = None
        hdist = None
        haz = None
        if pd.notna(b["hotspot_x_km_local"]) and pd.notna(a["hotspot_x_km_local"]):
            hdx = float(a["hotspot_x_km_local"] - b["hotspot_x_km_local"])
            hdy = float(a["hotspot_y_km_local"] - b["hotspot_y_km_local"])
            hdist = float(math.hypot(hdx, hdy))
            haz = azimuth_from_components(hdx, hdy)
        change_rows.append(
            {
                "comparison_label": label,
                "before_interval_role": "before",
                "after_interval_role": "after",
                "before_event_count": int(b["n_events"]),
                "after_event_count": int(a["n_events"]),
                "event_count_change": int(a["n_events"] - b["n_events"]),
                "centroid_shift_dx_km": dx,
                "centroid_shift_dy_km": dy,
                "centroid_shift_distance_km": dist,
                "centroid_shift_azimuth_deg": az,
                "principal_axis_orientation_change_deg": circular_difference_deg(
                    a["principal_axis_azimuth_deg"], b["principal_axis_azimuth_deg"]
                ),
                "occupied_area_change_km2": (
                    float(a["spatial_footprint_area_km2"] - b["spatial_footprint_area_km2"])
                    if pd.notna(a["spatial_footprint_area_km2"]) and pd.notna(b["spatial_footprint_area_km2"])
                    else None
                ),
                "along_strike_centroid_change_km": (
                    float(a["along_strike_centroid_km"] - b["along_strike_centroid_km"])
                    if pd.notna(a["along_strike_centroid_km"]) and pd.notna(b["along_strike_centroid_km"])
                    else None
                ),
                "cross_strike_centroid_change_km": (
                    float(a["cross_strike_centroid_km"] - b["cross_strike_centroid_km"])
                    if pd.notna(a["cross_strike_centroid_km"]) and pd.notna(b["cross_strike_centroid_km"])
                    else None
                ),
                "hotspot_shift_dx_km": hdx,
                "hotspot_shift_dy_km": hdy,
                "hotspot_shift_distance_km": hdist,
                "hotspot_shift_azimuth_deg": haz,
            }
        )
    changes_df = pd.DataFrame(change_rows)
    assert_columns(changes_df, COMPARISON_CHANGE_COLUMNS, "comparison_change_metrics")
    return df, changes_df


def classify_orientation_change(series: pd.Series) -> str:
    vals = series.dropna().to_numpy(dtype=float)
    if len(vals) < 2:
        return "insufficient"
    spread = float(np.nanmax(vals) - np.nanmin(vals))
    if spread < 20.0:
        return "stable"
    if spread < 45.0:
        return "moderate_change"
    return "strong_change"


def summarize_migration(metrics_df: pd.DataFrame, cluster_df: pd.DataFrame, label: str) -> dict[str, Any]:
    assert_columns(
        metrics_df,
        [
            "window_label",
            "n_events",
            "window_mid_time",
            "centroid_x_km_local",
            "centroid_y_km_local",
            "cumulative_centroid_distance_km",
            "centroid_step_distance_km",
            "principal_axis_azimuth_deg",
            "centroid_distance_to_mainshock64_km",
            "centroid_distance_to_mainshock71_km",
        ],
        f"migration_metrics_{label}",
    )
    assert_columns(
        cluster_df,
        ["window_label", "n_clusters", "dominant_cluster_fraction", "clustered_event_fraction"],
        f"migration_cluster_{label}",
    )
    merged = metrics_df.merge(
        cluster_df[["window_label", "n_clusters", "dominant_cluster_fraction", "clustered_event_fraction"]],
        on="window_label",
        how="left",
        validate="one_to_one",
    )
    valid = merged.loc[merged["n_events"] > 0].copy()
    if valid.empty:
        return {
            "summary_label": label,
            "n_windows_total": int(len(metrics_df)),
            "n_windows_with_events": 0,
            "dominant_orientation_deg": None,
            "orientation_change_class": "insufficient",
            "net_centroid_shift_distance_km": None,
            "net_centroid_shift_azimuth_deg": None,
            "cumulative_centroid_distance_km": 0.0,
            "mean_centroid_step_distance_km": None,
            "distance_to_target_trend_slope_km_per_hour": None,
            "median_cluster_count": None,
            "multi_cluster_window_fraction": None,
            "dominant_cluster_fraction_median": None,
        }

    first = valid.iloc[0]
    last = valid.iloc[-1]
    dx = float(last["centroid_x_km_local"] - first["centroid_x_km_local"])
    dy = float(last["centroid_y_km_local"] - first["centroid_y_km_local"])

    target_col = "centroid_distance_to_mainshock71_km" if label == "64_to_71" else "centroid_distance_to_mainshock64_km"
    slope = None
    target_valid = valid.loc[valid[target_col].notna()].copy()
    if len(target_valid) >= 2:
        x = target_valid["window_mid_time"].astype("int64") / 1e9 / 3600.0
        y = target_valid[target_col].to_numpy(dtype=float)
        coeffs = np.polyfit(x, y, 1)
        slope = float(coeffs[0])

    orientation_vals = valid["principal_axis_azimuth_deg"]
    dominant_orientation = float(np.nanmedian(orientation_vals.to_numpy(dtype=float))) if orientation_vals.notna().any() else None
    summary = {
        "summary_label": label,
        "n_windows_total": int(len(metrics_df)),
        "n_windows_with_events": int(len(valid)),
        "dominant_orientation_deg": dominant_orientation,
        "orientation_change_class": classify_orientation_change(orientation_vals),
        "net_centroid_shift_distance_km": float(math.hypot(dx, dy)),
        "net_centroid_shift_azimuth_deg": azimuth_from_components(dx, dy),
        "cumulative_centroid_distance_km": float(valid["cumulative_centroid_distance_km"].fillna(0.0).max()),
        "mean_centroid_step_distance_km": (
            float(valid["centroid_step_distance_km"].dropna().mean()) if valid["centroid_step_distance_km"].notna().any() else None
        ),
        "distance_to_target_trend_slope_km_per_hour": slope,
        "median_cluster_count": float(valid["n_clusters"].median()) if valid["n_clusters"].notna().any() else None,
        "multi_cluster_window_fraction": (
            float((valid["n_clusters"].fillna(0) >= 2).mean()) if len(valid) > 0 else None
        ),
        "dominant_cluster_fraction_median": (
            float(valid["dominant_cluster_fraction"].dropna().median())
            if valid["dominant_cluster_fraction"].notna().any()
            else None
        ),
    }
    return summary


def write_csv(df: pd.DataFrame, path: Path) -> None:
    out = df.copy()
    for col in out.columns:
        if pd.api.types.is_datetime64_any_dtype(out[col]):
            out[col] = out[col].dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    out.to_csv(path, index=False)
    log(f"[INFO] Wrote CSV: {path}")


def write_json(obj: dict[str, Any], path: Path) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, sort_keys=True)
    log(f"[INFO] Wrote JSON: {path}")


def main() -> None:
    ensure_output_dir()
    clear_stale_outputs()
    log(f"[INFO] Script path: {SCRIPT_PATH}")
    log(f"[INFO] Output directory: {OUTPUT_DIR}")
    log(f"[INFO] Parallel configuration: max_cores={MAX_CORES}, n_jobs={N_JOBS}")
    log(f"[INFO] Clustering configuration: eps_km={DBSCAN_EPS_KM}, min_samples={DBSCAN_MIN_SAMPLES}")

    extent = read_json(EXTENT_PATH)
    catalog = read_catalog()
    catalog = attach_projection_origin(catalog, extent)
    mainshocks = read_mainshocks(catalog)
    ms64 = mainshocks["mainshock64"]
    ms71 = mainshocks["mainshock71"]
    axis_ref = compute_axis_reference(ms64, ms71)
    whole_windows = read_windows(WHOLE_WINDOWS_PATH, REQUIRED_WINDOW_COLUMNS, "whole_windows")
    post64_windows = read_windows(POST64_WINDOWS_PATH, REQUIRED_WINDOW_COLUMNS, "post64_windows")
    comparison_intervals = read_windows(COMPARISON_PATH, REQUIRED_COMPARISON_COLUMNS, "comparison_intervals")

    whole_metrics, whole_clusters = compute_window_family_metrics(
        windows_df=whole_windows,
        catalog=catalog,
        ms64=ms64,
        ms71=ms71,
        axis_ref=axis_ref,
        family_label="whole_sequence",
    )
    post64_metrics, post64_clusters = compute_window_family_metrics(
        windows_df=post64_windows,
        catalog=catalog,
        ms64=ms64,
        ms71=ms71,
        axis_ref=axis_ref,
        family_label="post64_hourly",
    )

    comparison_metrics, comparison_changes = finalize_comparison_metrics(
        intervals_df=comparison_intervals,
        catalog=catalog,
        ms64=ms64,
        ms71=ms71,
        axis_ref=axis_ref,
    )

    comparison_64 = comparison_metrics.loc[comparison_metrics["comparison_label"] == "mw64"].reset_index(drop=True)
    comparison_71 = comparison_metrics.loc[comparison_metrics["comparison_label"] == "mw71"].reset_index(drop=True)
    changes_64 = comparison_changes.loc[comparison_changes["comparison_label"] == "mw64"].reset_index(drop=True)
    changes_71 = comparison_changes.loc[comparison_changes["comparison_label"] == "mw71"].reset_index(drop=True)
    if len(changes_64) != 1 or len(changes_71) != 1:
        raise ValueError("Expected exactly one change-summary row for each comparison label")
    comparison_64_export = comparison_64.copy()
    comparison_71_export = comparison_71.copy()
    for col in COMPARISON_CHANGE_COLUMNS:
        if col not in comparison_64_export.columns:
            comparison_64_export[col] = np.nan
        if col not in comparison_71_export.columns:
            comparison_71_export[col] = np.nan
    for col, value in changes_64.iloc[0].items():
        comparison_64_export[col] = value
    for col, value in changes_71.iloc[0].items():
        comparison_71_export[col] = value
    assert_columns(comparison_64_export, COMPARISON_INTERVAL_METRIC_COLUMNS + COMPARISON_CHANGE_COLUMNS, "comparison_64_export")
    assert_columns(comparison_71_export, COMPARISON_INTERVAL_METRIC_COLUMNS + COMPARISON_CHANGE_COLUMNS, "comparison_71_export")

    write_csv(whole_metrics, OUTPUT_DIR / "window_metrics_whole_sequence.csv")
    write_csv(post64_metrics, OUTPUT_DIR / "window_metrics_post64_hourly.csv")
    write_csv(whole_clusters, OUTPUT_DIR / "window_cluster_metrics_whole_sequence.csv")
    write_csv(post64_clusters, OUTPUT_DIR / "window_cluster_metrics_post64_hourly.csv")
    write_csv(comparison_64_export, OUTPUT_DIR / "comparison_metrics_64.csv")
    write_csv(comparison_71_export, OUTPUT_DIR / "comparison_metrics_71.csv")

    migration_64_to_71 = summarize_migration(
        metrics_df=post64_metrics,
        cluster_df=post64_clusters,
        label="64_to_71",
    )
    post71_metrics = whole_metrics.loc[
        whole_metrics["stage_label"] == "6h_mainshock71_plus_1day_to_plus_5days"
    ].reset_index(drop=True)
    post71_clusters = whole_clusters.loc[
        whole_clusters["stage_label"] == "6h_mainshock71_plus_1day_to_plus_5days"
    ].reset_index(drop=True)
    migration_post71 = summarize_migration(
        metrics_df=post71_metrics,
        cluster_df=post71_clusters,
        label="post71",
    )

    write_json(migration_64_to_71, OUTPUT_DIR / "migration_summary_64_to_71.json")
    write_json(migration_post71, OUTPUT_DIR / "migration_summary_post71.json")
    write_json(
        {
            "script_path": str(SCRIPT_PATH),
            "input_dir": str(INPUT_DIR),
            "output_dir": str(OUTPUT_DIR),
            "max_cores": MAX_CORES,
            "n_jobs_used": N_JOBS,
            "orientation_min_events": ORIENTATION_MIN_EVENTS,
            "area_min_events": AREA_MIN_EVENTS,
            "cluster_min_events": CLUSTER_MIN_EVENTS,
            "dbscan_eps_km": DBSCAN_EPS_KM,
            "dbscan_min_samples": DBSCAN_MIN_SAMPLES,
            "grid_step_km": GRID_STEP_KM,
            "hotspot_bandwidth_km": HOTSPOT_BANDWIDTH_KM,
            "mainshock64_to_mainshock71_axis_azimuth_deg": axis_ref.azimuth_deg,
            "mainshock64_to_mainshock71_axis_length_km": axis_ref.length_km,
        },
        OUTPUT_DIR / "metrics_runtime_config.json",
    )

    log("[INFO] Task 02_spatiotemporal_metrics completed successfully")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print(traceback.format_exc(), flush=True)
        sys.exit(1)
