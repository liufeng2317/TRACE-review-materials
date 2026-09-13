from __future__ import annotations

import json
import math
import os
import sys
import traceback
from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from joblib import Parallel, delayed
from matplotlib import cm, colors
from matplotlib.lines import Line2D
from pyproj import Transformer
from scipy.spatial import Delaunay, cKDTree
from shapely.geometry import LineString, MultiPoint, Polygon
from shapely.ops import polygonize, unary_union


REFERENCE_DIR = Path(
    "<REPO_ROOT>/examples/ridgecrest/catalog_analysis/run/01_2_trigger_spatiotemporal_fault_Q3-v1/exp_run/outputs/01_reference_framework"
)
KDE_DIR = Path(
    "<REPO_ROOT>/examples/ridgecrest/catalog_analysis/run/01_2_trigger_spatiotemporal_fault_Q3-v1/exp_run/outputs/02_kde_migration_analysis"
)
OUTPUT_DIR = Path(
    "<REPO_ROOT>/examples/ridgecrest/catalog_analysis/run/01_2_trigger_spatiotemporal_fault_Q3-v1/exp_run/outputs/03_morphology_and_synthesis"
)

CATALOG_FILE = REFERENCE_DIR / "intermainshock_catalog_clean.csv"
MAINSHOCK_FILE = REFERENCE_DIR / "mainshock_reference_table.csv"
FAULT_FILE = REFERENCE_DIR / "fault_segments_table.csv"
INTERVAL_FILE = REFERENCE_DIR / "interval_definitions_morphology_1h.csv"
METADATA_FILE = REFERENCE_DIR / "analysis_metadata.json"
HOTSPOT_METRICS_FILE = KDE_DIR / "hotspot_migration_metrics.csv"

MAX_CORES = 64
FIG_DPI = 220
FAULT_SIMPLIFY_STEP = 20
FAULT_COMPLEXITY_RADIUS_M = 3000.0
ALPHA_COMPONENT_AREA_MIN_M2 = 5.0e4
ALPHA_SELECTION_QUANTILES = [0.70, 0.75, 0.80, 0.85, 0.90]
ALPHA_SELECTION_SAMPLE_SIZE = 2000
CMAP_NAME = "turbo"
CONVEX_LINEWIDTH = 1.1
ALPHA_LINEWIDTH = 1.0

REQUIRED_CATALOG_COLUMNS = ["event_time", "latitude", "longitude", "x_m", "y_m"]
REQUIRED_MAINSHOCK_COLUMNS = ["event_label", "event_time", "latitude", "longitude", "x_m", "y_m"]
REQUIRED_FAULT_COLUMNS = ["segment_id", "point_order", "longitude", "latitude", "x_m", "y_m"]
REQUIRED_INTERVAL_COLUMNS = [
    "stage",
    "interval_index",
    "interval_label",
    "start_time",
    "end_time",
    "duration_hours",
    "is_final_interval",
]


def log(message: str) -> None:
    print(message, flush=True)


def require_exists(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Required input not found: {path}")


def ensure_clean_output_dir(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    removable_files = [
        "convex_hull_metrics.csv",
        "alpha_shape_metrics.csv",
        "geometry_status_by_interval.csv",
        "convex_hull_boundaries.csv",
        "alpha_shape_boundaries.csv",
        "convex_hull_evolution.png",
        "alpha_shape_evolution.png",
        "spatiotemporal_synthesis_summary.csv",
        "interval_process_flags.csv",
        "analysis_validation_manifest.json",
        "output_inventory.csv",
    ]
    for name in removable_files:
        path = output_dir / name
        if path.exists():
            path.unlink()
            log(f"Removed stale file: {path}")


def validate_columns(df: pd.DataFrame, required: list[str], table_name: str) -> None:
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"{table_name} is missing required columns: {missing}")


def load_inputs() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, Any], pd.DataFrame | None]:
    for path in [CATALOG_FILE, MAINSHOCK_FILE, FAULT_FILE, INTERVAL_FILE, METADATA_FILE]:
        require_exists(path)

    log(f"Loading catalog: {CATALOG_FILE}")
    catalog = pd.read_csv(CATALOG_FILE)
    validate_columns(catalog, REQUIRED_CATALOG_COLUMNS, "intermainshock catalog")
    catalog["event_time"] = pd.to_datetime(catalog["event_time"], utc=True)

    log(f"Loading mainshocks: {MAINSHOCK_FILE}")
    mainshocks = pd.read_csv(MAINSHOCK_FILE)
    validate_columns(mainshocks, REQUIRED_MAINSHOCK_COLUMNS, "mainshock reference table")
    mainshocks["event_time"] = pd.to_datetime(mainshocks["event_time"], utc=True)

    log(f"Loading faults: {FAULT_FILE}")
    faults = pd.read_csv(FAULT_FILE)
    validate_columns(faults, REQUIRED_FAULT_COLUMNS, "fault segment table")

    log(f"Loading morphology intervals: {INTERVAL_FILE}")
    intervals = pd.read_csv(INTERVAL_FILE)
    validate_columns(intervals, REQUIRED_INTERVAL_COLUMNS, "morphology interval table")
    intervals["start_time"] = pd.to_datetime(intervals["start_time"], utc=True)
    intervals["end_time"] = pd.to_datetime(intervals["end_time"], utc=True)

    with METADATA_FILE.open("r", encoding="utf-8") as f:
        metadata = json.load(f)

    hotspot_metrics = None
    if HOTSPOT_METRICS_FILE.exists():
        log(f"Loading hotspot metrics: {HOTSPOT_METRICS_FILE}")
        hotspot_metrics = pd.read_csv(HOTSPOT_METRICS_FILE)
        if "start_time" in hotspot_metrics.columns:
            hotspot_metrics["start_time"] = pd.to_datetime(hotspot_metrics["start_time"], utc=True)
        if "end_time" in hotspot_metrics.columns:
            hotspot_metrics["end_time"] = pd.to_datetime(hotspot_metrics["end_time"], utc=True)
    else:
        log(f"Hotspot metrics not found; synthesis will proceed without KDE-derived hotspot diagnostics: {HOTSPOT_METRICS_FILE}")

    return catalog, mainshocks, faults, intervals, metadata, hotspot_metrics


def get_extent(metadata: dict[str, Any]) -> tuple[float, float, float, float]:
    extent = metadata.get("plot_extent_degrees")
    if not isinstance(extent, dict):
        raise ValueError("analysis_metadata.json missing plot_extent_degrees")
    return (
        float(extent["longitude_min_padded"]),
        float(extent["longitude_max_padded"]),
        float(extent["latitude_min_padded"]),
        float(extent["latitude_max_padded"]),
    )


def build_transformers(metadata: dict[str, Any]) -> tuple[Transformer, Transformer, int | None]:
    proj = metadata.get("projected_crs", {})
    epsg = proj.get("epsg")
    if epsg is None:
        raise ValueError("analysis_metadata.json missing projected_crs.epsg")
    lonlat_to_xy = Transformer.from_crs("EPSG:4326", f"EPSG:{epsg}", always_xy=True)
    xy_to_lonlat = Transformer.from_crs(f"EPSG:{epsg}", "EPSG:4326", always_xy=True)
    return lonlat_to_xy, xy_to_lonlat, int(epsg)


def select_interval_events(catalog: pd.DataFrame, start_time: pd.Timestamp, end_time: pd.Timestamp, is_final: bool) -> pd.DataFrame:
    if is_final:
        mask = (catalog["event_time"] >= start_time) & (catalog["event_time"] <= end_time)
    else:
        mask = (catalog["event_time"] >= start_time) & (catalog["event_time"] < end_time)
    return catalog.loc[mask].copy().sort_values("event_time").reset_index(drop=True)


def build_fault_lines(faults: pd.DataFrame) -> list[np.ndarray]:
    lines = []
    for _, seg in faults.groupby("segment_id", sort=False):
        arr = seg.sort_values("point_order")[["longitude", "latitude"]].to_numpy()
        if len(arr) >= 2:
            lines.append(arr[::FAULT_SIMPLIFY_STEP] if len(arr) > FAULT_SIMPLIFY_STEP else arr)
    return lines


def build_fault_tree(faults: pd.DataFrame) -> tuple[cKDTree, np.ndarray]:
    sampled = faults.iloc[::FAULT_SIMPLIFY_STEP].copy().reset_index(drop=True)
    coords = sampled[["x_m", "y_m"]].to_numpy()
    return cKDTree(coords), coords


def polygon_to_boundary_records(geom: Any, interval_label: str, geom_type: str, xy_to_lonlat: Transformer) -> list[dict[str, Any]]:
    if geom is None or getattr(geom, "is_empty", True):
        return []

    polygons: list[Polygon] = []
    if geom.geom_type == "Polygon":
        polygons = [geom]
    elif geom.geom_type == "MultiPolygon":
        polygons = [g for g in geom.geoms if not g.is_empty]
    else:
        return []

    rows: list[dict[str, Any]] = []
    for component_index, poly in enumerate(polygons):
        ext = np.asarray(poly.exterior.coords)
        if ext.shape[0] < 2:
            continue
        lons, lats = xy_to_lonlat.transform(ext[:, 0], ext[:, 1])
        for point_order, (x_m, y_m, lon, lat) in enumerate(zip(ext[:, 0], ext[:, 1], lons, lats)):
            rows.append(
                {
                    "interval_label": interval_label,
                    "geometry_type": geom_type,
                    "component_index": component_index,
                    "ring_type": "exterior",
                    "point_order": point_order,
                    "x_m": float(x_m),
                    "y_m": float(y_m),
                    "longitude": float(lon),
                    "latitude": float(lat),
                }
            )
    return rows


def compute_compactness(area_m2: float, perimeter_m: float) -> float:
    if not np.isfinite(area_m2) or not np.isfinite(perimeter_m) or area_m2 <= 0.0 or perimeter_m <= 0.0:
        return np.nan
    return float(4.0 * math.pi * area_m2 / (perimeter_m ** 2))


def compute_oriented_box_metrics(geom: Polygon) -> tuple[float, float, float]:
    if geom is None or geom.is_empty:
        return np.nan, np.nan, np.nan
    mrr = geom.minimum_rotated_rectangle
    coords = np.asarray(mrr.exterior.coords)
    if coords.shape[0] < 4:
        return np.nan, np.nan, np.nan
    edges = []
    for i in range(4):
        p0 = coords[i]
        p1 = coords[i + 1]
        edges.append(float(np.linalg.norm(p1 - p0)))
    unique_edges = sorted(edges[:2], reverse=True)
    major = unique_edges[0]
    minor = unique_edges[1]
    dx = coords[1, 0] - coords[0, 0]
    dy = coords[1, 1] - coords[0, 1]
    azimuth_deg = (math.degrees(math.atan2(dy, dx)) + 360.0) % 180.0
    return major, minor, azimuth_deg


def triangle_circumradius(a: float, b: float, c: float, area: float) -> float:
    if area <= 0.0:
        return np.inf
    return (a * b * c) / (4.0 * area)


def build_alpha_shape(points: np.ndarray, alpha_value_inv_m: float) -> tuple[Any, str, int]:
    if points.shape[0] < 4:
        return None, "too_few_points", 0

    try:
        tri = Delaunay(points)
    except Exception:
        return None, "delaunay_failed", 0

    kept_edges: set[tuple[int, int]] = set()
    accepted_triangles = 0

    for simplex in tri.simplices:
        pa, pb, pc = points[simplex]
        a = float(np.linalg.norm(pb - pc))
        b = float(np.linalg.norm(pa - pc))
        c = float(np.linalg.norm(pa - pb))
        s = 0.5 * (a + b + c)
        area_sq = s * (s - a) * (s - b) * (s - c)
        if area_sq <= 0.0:
            continue
        area = math.sqrt(area_sq)
        radius = triangle_circumradius(a, b, c, area)
        if radius <= 1.0 / alpha_value_inv_m:
            accepted_triangles += 1
            for i, j in [(0, 1), (1, 2), (2, 0)]:
                edge = tuple(sorted((int(simplex[i]), int(simplex[j]))))
                if edge in kept_edges:
                    kept_edges.remove(edge)
                else:
                    kept_edges.add(edge)

    if not kept_edges:
        return None, "no_alpha_edges", 0

    edge_lines = [LineString([points[i], points[j]]) for i, j in kept_edges]
    merged = unary_union(edge_lines)
    polygons = list(polygonize(merged))
    if not polygons:
        return None, "polygonize_failed", accepted_triangles

    filtered = [poly for poly in polygons if poly.area >= ALPHA_COMPONENT_AREA_MIN_M2]
    if not filtered:
        filtered = polygons

    geom = unary_union(filtered)
    if geom.is_empty:
        return None, "invalid_alpha_geometry", accepted_triangles
    return geom, "ok", accepted_triangles


def estimate_alpha_parameter(catalog: pd.DataFrame) -> dict[str, Any]:
    coords = catalog[["x_m", "y_m"]].to_numpy(dtype=float)
    if coords.shape[0] > ALPHA_SELECTION_SAMPLE_SIZE:
        stride = max(1, coords.shape[0] // ALPHA_SELECTION_SAMPLE_SIZE)
        coords = coords[::stride][:ALPHA_SELECTION_SAMPLE_SIZE]

    tri = Delaunay(coords)
    radii = []
    for simplex in tri.simplices:
        pa, pb, pc = coords[simplex]
        a = float(np.linalg.norm(pb - pc))
        b = float(np.linalg.norm(pa - pc))
        c = float(np.linalg.norm(pa - pb))
        s = 0.5 * (a + b + c)
        area_sq = s * (s - a) * (s - b) * (s - c)
        if area_sq <= 0.0:
            continue
        area = math.sqrt(area_sq)
        radius = triangle_circumradius(a, b, c, area)
        if np.isfinite(radius) and radius > 0.0:
            radii.append(radius)

    if not radii:
        raise ValueError("Failed to estimate alpha parameter: no valid Delaunay circumradii.")

    radii_arr = np.asarray(radii, dtype=float)
    q_map = {str(q): float(np.quantile(radii_arr, q)) for q in ALPHA_SELECTION_QUANTILES}
    selected_radius = float(np.quantile(radii_arr, 0.80))
    alpha_value_inv_m = 1.0 / selected_radius
    return {
        "method": "delaunay_circumradius_quantile",
        "sample_point_count": int(coords.shape[0]),
        "triangle_count": int(len(radii_arr)),
        "radius_quantiles_m": q_map,
        "selected_radius_m": selected_radius,
        "selected_alpha_inv_m": alpha_value_inv_m,
    }


def extract_polygon_metrics(
    geom: Any,
    mainshock71_xy: np.ndarray,
    fault_tree: cKDTree,
    fault_coords: np.ndarray,
) -> dict[str, Any]:
    if geom is None or getattr(geom, "is_empty", True):
        return {
            "area_m2": np.nan,
            "perimeter_m": np.nan,
            "centroid_x_m": np.nan,
            "centroid_y_m": np.nan,
            "centroid_distance_to_mainshock71_m": np.nan,
            "nearest_fault_distance_m": np.nan,
            "fault_points_within_3km": np.nan,
            "compactness": np.nan,
            "major_axis_m": np.nan,
            "minor_axis_m": np.nan,
            "orientation_deg": np.nan,
            "component_count": 0,
        }

    centroid = geom.centroid
    centroid_xy = np.array([centroid.x, centroid.y], dtype=float)
    dist_main71 = float(np.linalg.norm(centroid_xy - mainshock71_xy))
    nearest_fault_dist = float(fault_tree.query(centroid_xy)[0])
    nearby_fault_count = int(len(fault_tree.query_ball_point(centroid_xy, r=FAULT_COMPLEXITY_RADIUS_M)))
    area_m2 = float(geom.area)
    perimeter_m = float(geom.length)
    compactness = compute_compactness(area_m2, perimeter_m)
    major_axis_m, minor_axis_m, orientation_deg = compute_oriented_box_metrics(geom.convex_hull if geom.geom_type != "Polygon" else geom)
    component_count = 1 if geom.geom_type == "Polygon" else len(getattr(geom, "geoms", []))
    return {
        "area_m2": area_m2,
        "perimeter_m": perimeter_m,
        "centroid_x_m": float(centroid.x),
        "centroid_y_m": float(centroid.y),
        "centroid_distance_to_mainshock71_m": dist_main71,
        "nearest_fault_distance_m": nearest_fault_dist,
        "fault_points_within_3km": nearby_fault_count,
        "compactness": compactness,
        "major_axis_m": major_axis_m,
        "minor_axis_m": minor_axis_m,
        "orientation_deg": orientation_deg,
        "component_count": int(component_count),
    }


def compute_interval_geometry(
    interval_row: dict[str, Any],
    catalog: pd.DataFrame,
    xy_to_lonlat: Transformer,
    alpha_value_inv_m: float,
    mainshock71_xy: np.ndarray,
    fault_tree: cKDTree,
    fault_coords: np.ndarray,
) -> dict[str, Any]:
    label = str(interval_row["interval_label"])
    start_time = pd.Timestamp(interval_row["start_time"])
    end_time = pd.Timestamp(interval_row["end_time"])
    is_final = bool(interval_row["is_final_interval"])
    expected_count = int(interval_row.get("event_count", -1))

    subset = select_interval_events(catalog, start_time, end_time, is_final)
    points = subset[["x_m", "y_m"]].to_numpy(dtype=float)
    event_count = int(points.shape[0])
    log(f"Processing geometry for {label}: events={event_count}, start={start_time.isoformat()}, end={end_time.isoformat()}")

    status = {
        "interval_label": label,
        "stage": str(interval_row["stage"]),
        "interval_index": int(interval_row["interval_index"]),
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "event_count_expected": expected_count,
        "event_count_actual": event_count,
        "event_count_match_reference": bool(expected_count == event_count) if expected_count >= 0 else False,
        "convex_status": "not_attempted",
        "alpha_status": "not_attempted",
    }

    convex_metrics = {
        "stage": str(interval_row["stage"]),
        "interval_index": int(interval_row["interval_index"]),
        "interval_label": label,
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "duration_hours": float(interval_row["duration_hours"]),
        "event_count_actual": event_count,
    }
    alpha_metrics = convex_metrics.copy()

    convex_boundary_rows: list[dict[str, Any]] = []
    alpha_boundary_rows: list[dict[str, Any]] = []

    if event_count < 3:
        status["convex_status"] = "too_few_points"
        status["alpha_status"] = "too_few_points"
        convex_metrics.update(
            {
                "geometry_status": "too_few_points",
                "area_m2": np.nan,
                "perimeter_m": np.nan,
                "centroid_x_m": np.nan,
                "centroid_y_m": np.nan,
                "centroid_longitude": np.nan,
                "centroid_latitude": np.nan,
                "centroid_distance_to_mainshock71_m": np.nan,
                "nearest_fault_distance_m": np.nan,
                "fault_points_within_3km": np.nan,
                "compactness": np.nan,
                "major_axis_m": np.nan,
                "minor_axis_m": np.nan,
                "orientation_deg": np.nan,
                "component_count": 0,
            }
        )
        alpha_metrics.update(convex_metrics | {"geometry_status": "too_few_points"})
        return {
            "status": status,
            "convex_metrics": convex_metrics,
            "alpha_metrics": alpha_metrics,
            "convex_boundary_rows": convex_boundary_rows,
            "alpha_boundary_rows": alpha_boundary_rows,
        }

    point_geom = MultiPoint(points)
    convex_geom = point_geom.convex_hull
    if convex_geom.geom_type != "Polygon" or convex_geom.is_empty or convex_geom.area <= 0.0:
        status["convex_status"] = "collinear_points"
        convex_metrics.update(
            {
                "geometry_status": "collinear_points",
                "area_m2": np.nan,
                "perimeter_m": np.nan,
                "centroid_x_m": np.nan,
                "centroid_y_m": np.nan,
                "centroid_longitude": np.nan,
                "centroid_latitude": np.nan,
                "centroid_distance_to_mainshock71_m": np.nan,
                "nearest_fault_distance_m": np.nan,
                "fault_points_within_3km": np.nan,
                "compactness": np.nan,
                "major_axis_m": np.nan,
                "minor_axis_m": np.nan,
                "orientation_deg": np.nan,
                "component_count": 0,
                "hull_vertex_count": int(len(points)),
            }
        )
    else:
        status["convex_status"] = "ok"
        centroid_lon, centroid_lat = xy_to_lonlat.transform(convex_geom.centroid.x, convex_geom.centroid.y)
        convex_extra = extract_polygon_metrics(convex_geom, mainshock71_xy, fault_tree, fault_coords)
        convex_metrics.update(convex_extra)
        convex_metrics.update(
            {
                "geometry_status": "ok",
                "centroid_longitude": float(centroid_lon),
                "centroid_latitude": float(centroid_lat),
                "hull_vertex_count": int(len(np.asarray(convex_geom.exterior.coords)) - 1),
            }
        )
        convex_boundary_rows = polygon_to_boundary_records(convex_geom, label, "convex_hull", xy_to_lonlat)

    alpha_geom = None
    if event_count < 4:
        status["alpha_status"] = "too_few_points"
        alpha_metrics.update(
            {
                "geometry_status": "too_few_points",
                "area_m2": np.nan,
                "perimeter_m": np.nan,
                "centroid_x_m": np.nan,
                "centroid_y_m": np.nan,
                "centroid_longitude": np.nan,
                "centroid_latitude": np.nan,
                "centroid_distance_to_mainshock71_m": np.nan,
                "nearest_fault_distance_m": np.nan,
                "fault_points_within_3km": np.nan,
                "compactness": np.nan,
                "major_axis_m": np.nan,
                "minor_axis_m": np.nan,
                "orientation_deg": np.nan,
                "component_count": 0,
                "accepted_triangle_count": 0,
            }
        )
    else:
        alpha_geom, alpha_status, accepted_triangles = build_alpha_shape(points, alpha_value_inv_m)
        status["alpha_status"] = alpha_status
        if alpha_status != "ok" or alpha_geom is None:
            alpha_metrics.update(
                {
                    "geometry_status": alpha_status,
                    "area_m2": np.nan,
                    "perimeter_m": np.nan,
                    "centroid_x_m": np.nan,
                    "centroid_y_m": np.nan,
                    "centroid_longitude": np.nan,
                    "centroid_latitude": np.nan,
                    "centroid_distance_to_mainshock71_m": np.nan,
                    "nearest_fault_distance_m": np.nan,
                    "fault_points_within_3km": np.nan,
                    "compactness": np.nan,
                    "major_axis_m": np.nan,
                    "minor_axis_m": np.nan,
                    "orientation_deg": np.nan,
                    "component_count": 0,
                    "accepted_triangle_count": int(accepted_triangles),
                }
            )
        else:
            centroid_lon, centroid_lat = xy_to_lonlat.transform(alpha_geom.centroid.x, alpha_geom.centroid.y)
            alpha_extra = extract_polygon_metrics(alpha_geom, mainshock71_xy, fault_tree, fault_coords)
            alpha_metrics.update(alpha_extra)
            alpha_metrics.update(
                {
                    "geometry_status": "ok",
                    "centroid_longitude": float(centroid_lon),
                    "centroid_latitude": float(centroid_lat),
                    "accepted_triangle_count": int(accepted_triangles),
                }
            )
            alpha_boundary_rows = polygon_to_boundary_records(alpha_geom, label, "alpha_shape", xy_to_lonlat)

    return {
        "status": status,
        "convex_metrics": convex_metrics,
        "alpha_metrics": alpha_metrics,
        "convex_boundary_rows": convex_boundary_rows,
        "alpha_boundary_rows": alpha_boundary_rows,
    }


def plot_common_overlays(ax: plt.Axes, extent_deg: tuple[float, float, float, float], fault_lines: list[np.ndarray], mainshocks: pd.DataFrame) -> None:
    min_lon, max_lon, min_lat, max_lat = extent_deg
    for line in fault_lines:
        ax.plot(line[:, 0], line[:, 1], color="0.6", linewidth=0.35, alpha=0.45, zorder=1)

    ms64 = mainshocks.loc[mainshocks["event_label"] == "Mainshock64"].iloc[0]
    ms71 = mainshocks.loc[mainshocks["event_label"] == "Mainshock71"].iloc[0]
    ax.scatter(ms64["longitude"], ms64["latitude"], marker="*", s=160, color="cyan", edgecolor="black", linewidth=0.8, zorder=6)
    ax.scatter(ms71["longitude"], ms71["latitude"], marker="*", s=180, color="yellow", edgecolor="black", linewidth=0.8, zorder=6)
    ax.set_xlim(min_lon, max_lon)
    ax.set_ylim(min_lat, max_lat)
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_aspect("equal", adjustable="box")


def add_time_colorbar(fig: plt.Figure, axes: np.ndarray, norm: colors.Normalize) -> None:
    sm = cm.ScalarMappable(norm=norm, cmap=cm.get_cmap(CMAP_NAME))
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=axes.ravel().tolist() if isinstance(axes, np.ndarray) else axes, fraction=0.026, pad=0.02)
    cbar.set_label("Hours since Mw 6.4 mainshock")


def plot_boundary_evolution(
    boundaries: pd.DataFrame,
    metrics: pd.DataFrame,
    faults: pd.DataFrame,
    mainshocks: pd.DataFrame,
    extent_deg: tuple[float, float, float, float],
    output_path: Path,
    title: str,
    linewidth: float,
) -> None:
    fig, ax = plt.subplots(figsize=(10.5, 8.8), constrained_layout=True)
    fault_lines = build_fault_lines(faults)
    plot_common_overlays(ax, extent_deg, fault_lines, mainshocks)

    valid_metrics = metrics.loc[metrics["geometry_status"] == "ok"].copy().sort_values("interval_index")
    if valid_metrics.empty:
        ax.set_title(f"{title}\nNo valid geometry intervals")
        fig.savefig(output_path, dpi=FIG_DPI)
        plt.close(fig)
        return

    min_hour = float(valid_metrics["hours_since_mainshock64_start"].min())
    max_hour = float(valid_metrics["hours_since_mainshock64_start"].max())
    if math.isclose(min_hour, max_hour):
        max_hour = min_hour + 1.0
    norm = colors.Normalize(vmin=min_hour, vmax=max_hour)
    cmap = cm.get_cmap(CMAP_NAME)

    merged = boundaries.merge(
        valid_metrics[["interval_label", "hours_since_mainshock64_start"]],
        on="interval_label",
        how="inner",
    )
    for (interval_label, component_index), group in merged.groupby(["interval_label", "component_index"], sort=True):
        group = group.sort_values("point_order")
        hours = float(group["hours_since_mainshock64_start"].iloc[0])
        color = cmap(norm(hours))
        ax.plot(group["longitude"], group["latitude"], color=color, linewidth=linewidth, alpha=0.92, zorder=4)

    handles = [
        Line2D([0], [0], color=cmap(norm(min_hour)), linewidth=2, label="Early"),
        Line2D([0], [0], color=cmap(norm((min_hour + max_hour) / 2.0)), linewidth=2, label="Intermediate"),
        Line2D([0], [0], color=cmap(norm(max_hour)), linewidth=2, label="Late"),
        Line2D([0], [0], marker="*", color="w", markerfacecolor="cyan", markeredgecolor="black", markersize=12, linewidth=0, label="Mw 6.4"),
        Line2D([0], [0], marker="*", color="w", markerfacecolor="yellow", markeredgecolor="black", markersize=12, linewidth=0, label="Mw 7.1"),
    ]
    ax.legend(handles=handles, loc="upper right", frameon=True, fontsize=9)
    ax.set_title(title)
    add_time_colorbar(fig, np.asarray([ax]), norm)
    fig.savefig(output_path, dpi=FIG_DPI)
    plt.close(fig)
    log(f"Saved figure: {output_path}")


def build_output_inventory(output_dir: Path) -> pd.DataFrame:
    rows = []
    for path in sorted(output_dir.iterdir()):
        if path.is_file():
            rows.append({"file_name": path.name, "bytes": int(path.stat().st_size)})
    return pd.DataFrame(rows)


def main() -> None:
    ensure_clean_output_dir(OUTPUT_DIR)
    catalog, mainshocks, faults, intervals, metadata, hotspot_metrics = load_inputs()
    extent_deg = get_extent(metadata)
    _, xy_to_lonlat, epsg = build_transformers(metadata)
    fault_tree, _fault_coords = build_fault_tree(faults)

    ms64 = mainshocks.loc[mainshocks["event_label"] == "Mainshock64"].iloc[0]
    ms71 = mainshocks.loc[mainshocks["event_label"] == "Mainshock71"].iloc[0]
    mainshock71_xy = np.array([float(ms71["x_m"]), float(ms71["y_m"])] , dtype=float)
    t64 = pd.Timestamp(ms64["event_time"])

    alpha_meta = estimate_alpha_parameter(catalog)
    alpha_value_inv_m = float(alpha_meta["selected_alpha_inv_m"])
    log(
        "Selected fixed alpha parameter "
        f"(inverse length units): {alpha_value_inv_m:.8f} 1/m "
        f"from radius {alpha_meta['selected_radius_m']:.2f} m"
    )

    interval_records = intervals.sort_values("interval_index").to_dict("records")
    n_jobs = min(MAX_CORES, max(1, os.cpu_count() or 1), len(interval_records))
    log(f"Computing interval geometries in parallel with n_jobs={n_jobs}")
    results = Parallel(n_jobs=n_jobs, backend="loky", verbose=10)(
        delayed(compute_interval_geometry)(
            interval_row=row,
            catalog=catalog,
            xy_to_lonlat=xy_to_lonlat,
            alpha_value_inv_m=alpha_value_inv_m,
            mainshock71_xy=mainshock71_xy,
            fault_tree=fault_tree,
            fault_coords=_fault_coords,
        )
        for row in interval_records
    )

    status_df = pd.DataFrame([r["status"] for r in results]).sort_values("interval_index").reset_index(drop=True)
    convex_df = pd.DataFrame([r["convex_metrics"] for r in results]).sort_values("interval_index").reset_index(drop=True)
    alpha_df = pd.DataFrame([r["alpha_metrics"] for r in results]).sort_values("interval_index").reset_index(drop=True)

    convex_boundary_rows = [row for r in results for row in r["convex_boundary_rows"]]
    alpha_boundary_rows = [row for r in results for row in r["alpha_boundary_rows"]]
    convex_boundary_df = pd.DataFrame(convex_boundary_rows)
    alpha_boundary_df = pd.DataFrame(alpha_boundary_rows)

    for df in [convex_df, alpha_df]:
        start_times = pd.to_datetime(df["start_time"], utc=True)
        end_times = pd.to_datetime(df["end_time"], utc=True)
        df["hours_since_mainshock64_start"] = (start_times - t64).dt.total_seconds() / 3600.0
        df["hours_since_mainshock64_end"] = (end_times - t64).dt.total_seconds() / 3600.0

    convex_df.to_csv(OUTPUT_DIR / "convex_hull_metrics.csv", index=False)
    alpha_df.to_csv(OUTPUT_DIR / "alpha_shape_metrics.csv", index=False)
    status_df.to_csv(OUTPUT_DIR / "geometry_status_by_interval.csv", index=False)
    convex_boundary_df.to_csv(OUTPUT_DIR / "convex_hull_boundaries.csv", index=False)
    alpha_boundary_df.to_csv(OUTPUT_DIR / "alpha_shape_boundaries.csv", index=False)
    log("Saved morphology metrics and boundary tables.")

    plot_boundary_evolution(
        boundaries=convex_boundary_df,
        metrics=convex_df,
        faults=faults,
        mainshocks=mainshocks,
        extent_deg=extent_deg,
        output_path=OUTPUT_DIR / "convex_hull_evolution.png",
        title="Ridgecrest inter-mainshock convex hull evolution (1-hour intervals)",
        linewidth=CONVEX_LINEWIDTH,
    )
    plot_boundary_evolution(
        boundaries=alpha_boundary_df,
        metrics=alpha_df,
        faults=faults,
        mainshocks=mainshocks,
        extent_deg=extent_deg,
        output_path=OUTPUT_DIR / "alpha_shape_evolution.png",
        title="Ridgecrest inter-mainshock alpha-shape evolution (1-hour intervals)",
        linewidth=ALPHA_LINEWIDTH,
    )

    synth = intervals[["interval_index", "interval_label", "start_time", "end_time", "event_count"]].copy()
    synth["start_time"] = pd.to_datetime(synth["start_time"], utc=True)
    synth["end_time"] = pd.to_datetime(synth["end_time"], utc=True)
    synth = synth.rename(columns={"event_count": "event_count_reference"})
    synth = synth.merge(
        convex_df[
            [
                "interval_label",
                "event_count_actual",
                "geometry_status",
                "area_m2",
                "perimeter_m",
                "centroid_distance_to_mainshock71_m",
                "nearest_fault_distance_m",
                "fault_points_within_3km",
                "compactness",
                "major_axis_m",
                "minor_axis_m",
                "orientation_deg",
                "hours_since_mainshock64_start",
            ]
        ].rename(
            columns={
                "geometry_status": "convex_status",
                "area_m2": "convex_area_m2",
                "perimeter_m": "convex_perimeter_m",
                "centroid_distance_to_mainshock71_m": "convex_centroid_distance_to_mainshock71_m",
                "nearest_fault_distance_m": "convex_nearest_fault_distance_m",
                "fault_points_within_3km": "convex_fault_points_within_3km",
                "compactness": "convex_compactness",
                "major_axis_m": "convex_major_axis_m",
                "minor_axis_m": "convex_minor_axis_m",
                "orientation_deg": "convex_orientation_deg",
            }
        ),
        on="interval_label",
        how="left",
    )
    synth = synth.merge(
        alpha_df[
            [
                "interval_label",
                "geometry_status",
                "area_m2",
                "perimeter_m",
                "centroid_distance_to_mainshock71_m",
                "nearest_fault_distance_m",
                "fault_points_within_3km",
                "compactness",
                "major_axis_m",
                "minor_axis_m",
                "orientation_deg",
                "component_count",
                "accepted_triangle_count",
            ]
        ].rename(
            columns={
                "geometry_status": "alpha_status",
                "area_m2": "alpha_area_m2",
                "perimeter_m": "alpha_perimeter_m",
                "centroid_distance_to_mainshock71_m": "alpha_centroid_distance_to_mainshock71_m",
                "nearest_fault_distance_m": "alpha_nearest_fault_distance_m",
                "fault_points_within_3km": "alpha_fault_points_within_3km",
                "compactness": "alpha_compactness",
                "major_axis_m": "alpha_major_axis_m",
                "minor_axis_m": "alpha_minor_axis_m",
                "orientation_deg": "alpha_orientation_deg",
            }
        ),
        on="interval_label",
        how="left",
    )

    if hotspot_metrics is not None and not hotspot_metrics.empty:
        synth = synth.merge(
            hotspot_metrics[
                [
                    "interval_label",
                    "hotspot_longitude",
                    "hotspot_latitude",
                    "step_distance_m",
                    "cumulative_path_length_m",
                    "distance_to_mainshock71_m",
                    "nearest_fault_distance_m",
                    "fault_points_within_3km",
                    "peak_density",
                ]
            ].copy().rename(
                columns={
                    "distance_to_mainshock71_m": "hotspot_distance_to_mainshock71_m",
                    "nearest_fault_distance_m": "hotspot_nearest_fault_distance_m",
                    "fault_points_within_3km": "hotspot_fault_points_within_3km",
                }
            ),
            on="interval_label",
            how="left",
        )
    else:
        synth["hotspot_longitude"] = np.nan
        synth["hotspot_latitude"] = np.nan
        synth["step_distance_m"] = np.nan
        synth["cumulative_path_length_m"] = np.nan
        synth["hotspot_distance_to_mainshock71_m"] = np.nan
        synth["hotspot_nearest_fault_distance_m"] = np.nan
        synth["hotspot_fault_points_within_3km"] = np.nan
        synth["peak_density"] = np.nan

    required_synth_columns = [
        "interval_index",
        "interval_label",
        "event_count_reference",
        "event_count_actual",
        "convex_status",
        "convex_area_m2",
        "convex_centroid_distance_to_mainshock71_m",
        "alpha_status",
        "alpha_area_m2",
        "alpha_centroid_distance_to_mainshock71_m",
        "component_count",
    ]
    if hotspot_metrics is not None and not hotspot_metrics.empty:
        required_synth_columns.extend(
            [
                "hotspot_distance_to_mainshock71_m",
                "hotspot_nearest_fault_distance_m",
                "hotspot_fault_points_within_3km",
            ]
        )
    missing_synth_columns = [col for col in required_synth_columns if col not in synth.columns]
    if missing_synth_columns:
        raise ValueError(f"Synthesis table missing required downstream columns after merges: {missing_synth_columns}")

    synth = synth.sort_values("interval_index").reset_index(drop=True)
    synth["convex_area_change_m2"] = synth["convex_area_m2"].diff()
    synth["alpha_area_change_m2"] = synth["alpha_area_m2"].diff()
    synth["convex_distance_change_to_mainshock71_m"] = synth["convex_centroid_distance_to_mainshock71_m"].diff()
    synth["alpha_distance_change_to_mainshock71_m"] = synth["alpha_centroid_distance_to_mainshock71_m"].diff()
    synth["hotspot_distance_change_to_mainshock71_m"] = synth["hotspot_distance_to_mainshock71_m"].diff()
    synth["alpha_component_count_change"] = synth["component_count"].diff()
    synth["convex_area_ratio_to_previous"] = synth["convex_area_m2"] / synth["convex_area_m2"].shift(1)
    synth["alpha_area_ratio_to_previous"] = synth["alpha_area_m2"] / synth["alpha_area_m2"].shift(1)

    def classify_interval(row: pd.Series) -> str:
        focus = False
        defocus = False
        bifurcation = False

        if pd.notna(row["alpha_component_count_change"]) and row["alpha_component_count_change"] > 0:
            bifurcation = True
        if pd.notna(row["component_count"]) and row["component_count"] >= 2:
            bifurcation = True

        if (
            pd.notna(row["convex_distance_change_to_mainshock71_m"])
            and row["convex_distance_change_to_mainshock71_m"] < 0
            and pd.notna(row["convex_area_change_m2"])
            and row["convex_area_change_m2"] < 0
        ):
            focus = True
        if (
            pd.notna(row["hotspot_distance_change_to_mainshock71_m"])
            and row["hotspot_distance_change_to_mainshock71_m"] < 0
            and pd.notna(row["alpha_area_change_m2"])
            and row["alpha_area_change_m2"] <= 0
        ):
            focus = True

        if (
            pd.notna(row["convex_area_change_m2"])
            and row["convex_area_change_m2"] > 0
            and pd.notna(row["convex_distance_change_to_mainshock71_m"])
            and row["convex_distance_change_to_mainshock71_m"] >= 0
        ):
            defocus = True
        if pd.notna(row["alpha_area_ratio_to_previous"]) and row["alpha_area_ratio_to_previous"] > 1.15:
            defocus = True

        flags = []
        if focus:
            flags.append("focusing")
        if defocus:
            flags.append("defocusing")
        if bifurcation:
            flags.append("bifurcation")
        if not flags:
            return "indeterminate"
        return ";".join(flags)

    synth["process_flag"] = synth.apply(classify_interval, axis=1)
    synth["near_complex_fault_zone"] = (
        (synth["alpha_fault_points_within_3km"].fillna(0) >= 400)
        | (synth["hotspot_fault_points_within_3km"].fillna(0) >= 400)
    )

    synth["start_time"] = synth["start_time"].dt.strftime("%Y-%m-%dT%H:%M:%S.%f%z")
    synth["end_time"] = synth["end_time"].dt.strftime("%Y-%m-%dT%H:%M:%S.%f%z")

    process_flags = synth[
        [
            "interval_index",
            "interval_label",
            "hours_since_mainshock64_start",
            "event_count_actual",
            "convex_status",
            "alpha_status",
            "process_flag",
            "near_complex_fault_zone",
            "convex_area_change_m2",
            "alpha_area_change_m2",
            "convex_distance_change_to_mainshock71_m",
            "alpha_distance_change_to_mainshock71_m",
            "hotspot_distance_change_to_mainshock71_m",
            "alpha_component_count_change",
        ]
    ].copy()
    process_flags.to_csv(OUTPUT_DIR / "interval_process_flags.csv", index=False)
    synth.to_csv(OUTPUT_DIR / "spatiotemporal_synthesis_summary.csv", index=False)
    log("Saved synthesis tables.")

    validation_manifest = {
        "task": "03_morphology_and_synthesis",
        "reference_dir": str(REFERENCE_DIR),
        "kde_dir": str(KDE_DIR),
        "output_dir": str(OUTPUT_DIR),
        "projected_epsg": epsg,
        "alpha_selection": alpha_meta,
        "interval_count_expected": int(len(intervals)),
        "interval_count_status_table": int(len(status_df)),
        "interval_count_convex_metrics": int(len(convex_df)),
        "interval_count_alpha_metrics": int(len(alpha_df)),
        "valid_convex_interval_count": int((convex_df["geometry_status"] == "ok").sum()),
        "valid_alpha_interval_count": int((alpha_df["geometry_status"] == "ok").sum()),
        "convex_boundary_vertex_count": int(len(convex_boundary_df)),
        "alpha_boundary_vertex_count": int(len(alpha_boundary_df)),
        "kde_hotspot_metrics_available": bool(hotspot_metrics is not None and not hotspot_metrics.empty),
        "outputs_present": {
            name: (OUTPUT_DIR / name).exists()
            for name in [
                "convex_hull_metrics.csv",
                "alpha_shape_metrics.csv",
                "geometry_status_by_interval.csv",
                "convex_hull_boundaries.csv",
                "alpha_shape_boundaries.csv",
                "convex_hull_evolution.png",
                "alpha_shape_evolution.png",
                "spatiotemporal_synthesis_summary.csv",
                "interval_process_flags.csv",
            ]
        },
    }
    with (OUTPUT_DIR / "analysis_validation_manifest.json").open("w", encoding="utf-8") as f:
        json.dump(validation_manifest, f, indent=2)

    inventory_df = build_output_inventory(OUTPUT_DIR)
    inventory_df.to_csv(OUTPUT_DIR / "output_inventory.csv", index=False)
    log("Saved validation manifest and output inventory.")
    log("03_morphology_and_synthesis completed successfully.")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print(traceback.format_exc(), flush=True)
        sys.exit(1)
