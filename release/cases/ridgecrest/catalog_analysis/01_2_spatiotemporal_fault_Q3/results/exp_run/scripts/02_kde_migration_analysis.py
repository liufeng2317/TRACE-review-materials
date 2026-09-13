from __future__ import annotations

import json
import math
import os
import shutil
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
from matplotlib.colors import Normalize
from pyproj import Transformer
from scipy.ndimage import label as nd_label
from scipy.spatial import cKDTree
from scipy.stats import gaussian_kde


REFERENCE_DIR = Path(
    "<REPO_ROOT>/examples/ridgecrest/catalog_analysis/run/01_2_trigger_spatiotemporal_fault_Q3-v1/exp_run/outputs/01_reference_framework"
)
OUTPUT_DIR = Path(
    "<REPO_ROOT>/examples/ridgecrest/catalog_analysis/run/01_2_trigger_spatiotemporal_fault_Q3-v1/exp_run/outputs/02_kde_migration_analysis"
)

CATALOG_FILE = REFERENCE_DIR / "intermainshock_catalog_clean.csv"
MAINSHOCK_FILE = REFERENCE_DIR / "mainshock_reference_table.csv"
FAULT_FILE = REFERENCE_DIR / "fault_segments_table.csv"
STAGE1_FILE = REFERENCE_DIR / "interval_definitions_kde_stage1.csv"
STAGE2_FILE = REFERENCE_DIR / "interval_definitions_kde_stage2.csv"
METADATA_FILE = REFERENCE_DIR / "analysis_metadata.json"

MAX_CORES = 64
GRID_SIZE_X = 220
GRID_SIZE_Y = 220
BANDWIDTH_RULE = "scott"
LOW_SAMPLE_THRESHOLD = 3
FAULT_SIMPLIFY_STEP = 20
FAULT_COMPLEXITY_RADIUS_M = 3000.0
HOTSPOT_PATH_MARKERSIZE = 52
FIG_DPI = 220
CMAP_NAME = "magma"
PANEL_NROWS = 2
PANEL_NCOLS = 4
MIGRATION_CMAP_NAME = "turbo"
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


def ensure_clean_output_dir(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    removable = [
        "kde_interval_summary.csv",
        "kde_stage1_hotspots.csv",
        "kde_stage2_hotspots.csv",
        "kde_global_normalization.json",
        "hotspot_migration_metrics.csv",
        "hotspot_migration_stage1.png",
        "hotspot_migration_stage2.png",
    ]
    for file_name in removable:
        path = output_dir / file_name
        if path.exists():
            path.unlink()
            log(f"Removed stale file: {path}")

    for path in output_dir.glob("kde_stage*_panels_page*.png"):
        path.unlink()
        log(f"Removed stale panel figure: {path}")

    arrays_dir = output_dir / "kde_arrays"
    if arrays_dir.exists():
        shutil.rmtree(arrays_dir)
        log(f"Removed stale array directory: {arrays_dir}")
    arrays_dir.mkdir(parents=True, exist_ok=True)


def require_exists(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Required input not found: {path}")



def validate_columns(df: pd.DataFrame, required: list[str], table_name: str) -> None:
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"{table_name} is missing required columns: {missing}")


def load_reference_inputs() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    for path in [CATALOG_FILE, MAINSHOCK_FILE, FAULT_FILE, STAGE1_FILE, STAGE2_FILE, METADATA_FILE]:
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

    log(f"Loading stage 1 intervals: {STAGE1_FILE}")
    stage1 = pd.read_csv(STAGE1_FILE)
    validate_columns(stage1, REQUIRED_INTERVAL_COLUMNS, "stage1 interval table")
    stage1["start_time"] = pd.to_datetime(stage1["start_time"], utc=True)
    stage1["end_time"] = pd.to_datetime(stage1["end_time"], utc=True)

    log(f"Loading stage 2 intervals: {STAGE2_FILE}")
    stage2 = pd.read_csv(STAGE2_FILE)
    validate_columns(stage2, REQUIRED_INTERVAL_COLUMNS, "stage2 interval table")
    stage2["start_time"] = pd.to_datetime(stage2["start_time"], utc=True)
    stage2["end_time"] = pd.to_datetime(stage2["end_time"], utc=True)

    with METADATA_FILE.open("r", encoding="utf-8") as f:
        metadata = json.load(f)

    return catalog, mainshocks, faults, stage1, stage2, metadata


def get_extent(metadata: dict[str, Any]) -> tuple[float, float, float, float]:
    extent = metadata.get("plot_extent_degrees")
    if not isinstance(extent, dict):
        raise ValueError("analysis_metadata.json missing plot_extent_degrees")

    padded_keys = [
        "longitude_min_padded",
        "longitude_max_padded",
        "latitude_min_padded",
        "latitude_max_padded",
    ]
    legacy_keys = ["min_longitude", "max_longitude", "min_latitude", "max_latitude"]

    if all(key in extent for key in padded_keys):
        return (
            float(extent["longitude_min_padded"]),
            float(extent["longitude_max_padded"]),
            float(extent["latitude_min_padded"]),
            float(extent["latitude_max_padded"]),
        )
    if all(key in extent for key in legacy_keys):
        return (
            float(extent["min_longitude"]),
            float(extent["max_longitude"]),
            float(extent["min_latitude"]),
            float(extent["max_latitude"]),
        )

    raise KeyError(
        "plot_extent_degrees must contain either padded keys "
        "(longitude_min_padded, longitude_max_padded, latitude_min_padded, latitude_max_padded) "
        "or legacy keys (min_longitude, max_longitude, min_latitude, max_latitude)."
    )


def get_projected_extent(catalog: pd.DataFrame, mainshocks: pd.DataFrame, faults: pd.DataFrame) -> tuple[float, float, float, float]:
    xs = np.concatenate([catalog["x_m"].to_numpy(), mainshocks["x_m"].to_numpy(), faults["x_m"].to_numpy()])
    ys = np.concatenate([catalog["y_m"].to_numpy(), mainshocks["y_m"].to_numpy(), faults["y_m"].to_numpy()])
    return float(xs.min()), float(xs.max()), float(ys.min()), float(ys.max())


def make_grid(projected_extent: tuple[float, float, float, float]) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    min_x, max_x, min_y, max_y = projected_extent
    x_grid = np.linspace(min_x, max_x, GRID_SIZE_X)
    y_grid = np.linspace(min_y, max_y, GRID_SIZE_Y)
    xx, yy = np.meshgrid(x_grid, y_grid)
    return x_grid, y_grid, xx, yy


def select_interval_events(catalog: pd.DataFrame, start_time: pd.Timestamp, end_time: pd.Timestamp, is_final: bool) -> pd.DataFrame:
    if is_final:
        mask = (catalog["event_time"] >= start_time) & (catalog["event_time"] <= end_time)
    else:
        mask = (catalog["event_time"] >= start_time) & (catalog["event_time"] < end_time)
    subset = catalog.loc[mask].copy()
    return subset.sort_values("event_time").reset_index(drop=True)


def estimate_fixed_bandwidth_m(catalog: pd.DataFrame) -> float:
    coords = np.vstack([catalog["x_m"].to_numpy(), catalog["y_m"].to_numpy()])
    kde = gaussian_kde(coords, bw_method=BANDWIDTH_RULE)
    factor = float(kde.factor)
    covariance = np.cov(coords)
    pooled_sigma = math.sqrt(float(np.trace(covariance) / 2.0))
    bandwidth_m = factor * pooled_sigma
    return bandwidth_m


def highest_density_centroid(density: np.ndarray, peak_value: float, x_grid: np.ndarray, y_grid: np.ndarray) -> tuple[float, float]:
    peak_mask = np.isclose(density, peak_value, rtol=1e-10, atol=max(1e-14, peak_value * 1e-12))
    structure = np.ones((3, 3), dtype=int)
    labels, count = nd_label(peak_mask.astype(int), structure=structure)
    if count <= 1:
        iy, ix = np.argwhere(peak_mask)[0]
        return float(x_grid[ix]), float(y_grid[iy])

    best_label = None
    best_size = -1
    for label_id in range(1, count + 1):
        current_size = int((labels == label_id).sum())
        if current_size > best_size:
            best_label = label_id
            best_size = current_size
    rows, cols = np.where(labels == best_label)
    return float(x_grid[cols].mean()), float(y_grid[rows].mean())


def compute_interval_kde(
    interval_row: dict[str, Any],
    catalog: pd.DataFrame,
    xx: np.ndarray,
    yy: np.ndarray,
    x_grid: np.ndarray,
    y_grid: np.ndarray,
    lonlat_transformer: Transformer,
    arrays_dir: str,
) -> dict[str, Any]:
    label = interval_row["interval_label"]
    start_time = pd.Timestamp(interval_row["start_time"])
    end_time = pd.Timestamp(interval_row["end_time"])
    is_final = bool(interval_row["is_final_interval"])
    stage = str(interval_row["stage"])
    expected_count = int(interval_row.get("event_count", -1))

    subset = select_interval_events(catalog, start_time, end_time, is_final)
    event_count = int(len(subset))
    status = "ok"
    hotspot_x = np.nan
    hotspot_y = np.nan
    hotspot_lon = np.nan
    hotspot_lat = np.nan
    peak_density = np.nan
    array_relpath = None

    log(f"Computing KDE for {label}: stage={stage}, events={event_count}, start={start_time.isoformat()}, end={end_time.isoformat()}")

    if event_count == 0:
        status = "no_data"
    elif event_count < LOW_SAMPLE_THRESHOLD:
        status = "too_few_events"
    else:
        coords = np.vstack([subset["x_m"].to_numpy(), subset["y_m"].to_numpy()])
        kde = gaussian_kde(coords, bw_method=BANDWIDTH_RULE)
        positions = np.vstack([xx.ravel(), yy.ravel()])
        density = kde(positions).reshape(xx.shape)
        peak_density = float(np.nanmax(density))
        hotspot_x, hotspot_y = highest_density_centroid(density, peak_density, x_grid, y_grid)
        hotspot_lon, hotspot_lat = lonlat_transformer.transform(hotspot_x, hotspot_y)
        array_path = Path(arrays_dir) / f"{label}_density.npy"
        np.save(array_path, density.astype(np.float32))
        array_relpath = f"kde_arrays/{array_path.name}"

    return {
        "stage": stage,
        "interval_index": int(interval_row["interval_index"]),
        "interval_label": label,
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "duration_hours": float(interval_row["duration_hours"]),
        "is_final_interval": is_final,
        "event_count_expected": expected_count,
        "event_count_actual": event_count,
        "event_count_match_reference": bool(expected_count == event_count) if expected_count >= 0 else False,
        "status": status,
        "peak_density": peak_density,
        "hotspot_x_m": hotspot_x,
        "hotspot_y_m": hotspot_y,
        "hotspot_longitude": hotspot_lon,
        "hotspot_latitude": hotspot_lat,
        "kde_array_relpath": array_relpath,
    }


def build_fault_lines(faults: pd.DataFrame) -> list[np.ndarray]:
    lines = []
    grouped = faults.groupby("segment_id", sort=False)
    for _, seg in grouped:
        arr = seg.sort_values("point_order")[["longitude", "latitude"]].to_numpy()
        if len(arr) >= 2:
            lines.append(arr[::FAULT_SIMPLIFY_STEP] if len(arr) > FAULT_SIMPLIFY_STEP else arr)
    return lines


def build_fault_tree(faults: pd.DataFrame) -> tuple[cKDTree, np.ndarray]:
    sampled = faults.iloc[::FAULT_SIMPLIFY_STEP].copy().reset_index(drop=True)
    coords = sampled[["x_m", "y_m"]].to_numpy()
    tree = cKDTree(coords)
    return tree, coords


def plot_common_overlays(ax: plt.Axes, extent_deg: tuple[float, float, float, float], fault_lines: list[np.ndarray], mainshocks: pd.DataFrame) -> None:
    min_lon, max_lon, min_lat, max_lat = extent_deg
    for line in fault_lines:
        ax.plot(line[:, 0], line[:, 1], color="0.55", linewidth=0.4, alpha=0.55, zorder=1)

    ms64 = mainshocks.loc[mainshocks["event_label"] == "Mainshock64"].iloc[0]
    ms71 = mainshocks.loc[mainshocks["event_label"] == "Mainshock71"].iloc[0]
    ax.scatter(ms64["longitude"], ms64["latitude"], s=80, c="deepskyblue", edgecolors="black", linewidths=0.7, marker="*", zorder=5)
    ax.scatter(ms71["longitude"], ms71["latitude"], s=90, c="gold", edgecolors="black", linewidths=0.7, marker="*", zorder=5)
    ax.set_xlim(min_lon, max_lon)
    ax.set_ylim(min_lat, max_lat)
    ax.set_aspect("equal", adjustable="box")
    ax.grid(False)


def save_kde_panel_pages(
    stage_name: str,
    stage_df: pd.DataFrame,
    extent_deg: tuple[float, float, float, float],
    xx_lon: np.ndarray,
    yy_lat: np.ndarray,
    fault_lines: list[np.ndarray],
    mainshocks: pd.DataFrame,
    output_dir: Path,
    norm: Normalize,
) -> list[str]:
    output_names: list[str] = []
    stage_df = stage_df.sort_values("interval_index").reset_index(drop=True)
    page_size = PANEL_NROWS * PANEL_NCOLS

    for page_idx, start in enumerate(range(0, len(stage_df), page_size), start=1):
        chunk = stage_df.iloc[start : start + page_size].copy()
        fig, axes = plt.subplots(PANEL_NROWS, PANEL_NCOLS, figsize=(17.2, 9.4), constrained_layout=True)
        axes_flat = axes.ravel()
        mappable = None

        for ax, (_, row) in zip(axes_flat, chunk.iterrows()):
            plot_common_overlays(ax, extent_deg, fault_lines, mainshocks)
            title = f"{row['interval_label']}\nN={int(row['event_count_actual'])}"
            if row["status"] == "ok":
                density = np.load(output_dir / row["kde_array_relpath"])
                mappable = ax.pcolormesh(xx_lon, yy_lat, density, shading="auto", cmap=CMAP_NAME, norm=norm, zorder=0)
                ax.scatter(row["hotspot_longitude"], row["hotspot_latitude"], s=28, c="cyan", edgecolors="black", linewidths=0.5, zorder=6)
                title += f"\npeak={row['peak_density']:.2e}"
            else:
                ax.text(0.5, 0.5, row["status"], transform=ax.transAxes, ha="center", va="center", fontsize=11, color="crimson")
            ax.set_title(title, fontsize=9)
            ax.set_xlabel("Longitude")
            ax.set_ylabel("Latitude")

        for ax in axes_flat[len(chunk) :]:
            ax.axis("off")
            ax.text(0.5, 0.5, "unused", transform=ax.transAxes, ha="center", va="center", fontsize=11, color="0.4")

        if mappable is not None:
            cbar = fig.colorbar(mappable, ax=axes_flat.tolist(), orientation="vertical", shrink=0.92, pad=0.015)
            cbar.set_label("KDE density", fontsize=10)
            cbar.ax.tick_params(labelsize=8)

        fig.suptitle(f"Ridgecrest KDE density evolution: {stage_name} (fixed bandwidth, common scale)", fontsize=14)
        out_name = f"kde_{stage_name}_panels_page{page_idx:02d}.png"
        out_path = output_dir / out_name
        fig.savefig(out_path, dpi=FIG_DPI)
        plt.close(fig)
        output_names.append(out_name)
        log(f"Saved KDE panel page: {out_path}")

    return output_names


def compute_hotspot_metrics(
    hotspots: pd.DataFrame,
    stage_name: str,
    mainshocks: pd.DataFrame,
    fault_tree: cKDTree,
    fault_coords: np.ndarray,
) -> pd.DataFrame:
    records: list[dict[str, Any]] = []
    if hotspots.empty:
        return pd.DataFrame(records)

    ms71 = mainshocks.loc[mainshocks["event_label"] == "Mainshock71"].iloc[0]
    prev_x = None
    prev_y = None
    cumulative_length = 0.0

    for _, row in hotspots.sort_values("interval_index").iterrows():
        x = float(row["hotspot_x_m"])
        y = float(row["hotspot_y_m"])
        if prev_x is None or np.isnan(x) or np.isnan(y):
            step_distance = np.nan
        else:
            step_distance = float(math.hypot(x - prev_x, y - prev_y))
            cumulative_length += step_distance

        if np.isnan(x) or np.isnan(y):
            dist_to_ms71 = np.nan
            nearest_fault_distance = np.nan
            nearby_fault_points = np.nan
        else:
            dist_to_ms71 = float(math.hypot(x - float(ms71["x_m"]), y - float(ms71["y_m"])))
            nearest_fault_distance = float(fault_tree.query([[x, y]], k=1)[0][0])
            nearby_fault_points = int(len(fault_tree.query_ball_point([x, y], r=FAULT_COMPLEXITY_RADIUS_M)))

        records.append(
            {
                "stage": stage_name,
                "interval_index": int(row["interval_index"]),
                "interval_label": row["interval_label"],
                "start_time": row["start_time"],
                "end_time": row["end_time"],
                "event_count_actual": int(row["event_count_actual"]),
                "peak_density": float(row["peak_density"]),
                "hotspot_x_m": x,
                "hotspot_y_m": y,
                "hotspot_longitude": float(row["hotspot_longitude"]),
                "hotspot_latitude": float(row["hotspot_latitude"]),
                "step_distance_m": step_distance,
                "cumulative_path_length_m": cumulative_length,
                "distance_to_mainshock71_m": dist_to_ms71,
                "nearest_fault_distance_m": nearest_fault_distance,
                "fault_points_within_3km": nearby_fault_points,
            }
        )
        prev_x = x
        prev_y = y

    return pd.DataFrame(records)


def plot_hotspot_migration(
    stage_name: str,
    metrics_df: pd.DataFrame,
    extent_deg: tuple[float, float, float, float],
    fault_lines: list[np.ndarray],
    mainshocks: pd.DataFrame,
    output_dir: Path,
) -> str:
    fig, ax = plt.subplots(figsize=(10.4, 8.9), constrained_layout=True)
    plot_common_overlays(ax, extent_deg, fault_lines, mainshocks)

    ms64 = mainshocks.loc[mainshocks["event_label"] == "Mainshock64"].iloc[0]
    ms71 = mainshocks.loc[mainshocks["event_label"] == "Mainshock71"].iloc[0]
    legend_handles = [
        plt.Line2D([0], [0], color="0.55", lw=1.0, alpha=0.7, label="Fault traces"),
        plt.Line2D([0], [0], marker="*", linestyle="None", markerfacecolor="deepskyblue", markeredgecolor="black", markersize=10, label="Mw 6.4 mainshock"),
        plt.Line2D([0], [0], marker="*", linestyle="None", markerfacecolor="gold", markeredgecolor="black", markersize=10, label="Mw 7.1 mainshock"),
    ]

    if not metrics_df.empty:
        ordered = metrics_df.sort_values("interval_index").reset_index(drop=True)
        cmap = plt.get_cmap(MIGRATION_CMAP_NAME)
        colors = cmap(np.linspace(0, 1, len(ordered)))
        ax.plot(
            ordered["hotspot_longitude"],
            ordered["hotspot_latitude"],
            color="black",
            linewidth=1.6,
            alpha=0.85,
            zorder=6,
            label="Hotspot migration path",
        )
        ax.scatter(
            ordered["hotspot_longitude"],
            ordered["hotspot_latitude"],
            s=HOTSPOT_PATH_MARKERSIZE,
            c=np.arange(len(ordered)),
            cmap=MIGRATION_CMAP_NAME,
            edgecolors="black",
            linewidths=0.6,
            zorder=7,
            label="Interval hotspot",
        )

        lon_range = extent_deg[1] - extent_deg[0]
        lat_range = extent_deg[3] - extent_deg[2]
        angle_cycle = np.linspace(0.0, 2.0 * np.pi, len(ordered), endpoint=False)
        dx = 0.010 * lon_range * np.cos(angle_cycle)
        dy = 0.010 * lat_range * np.sin(angle_cycle)
        for idx, (_, row) in enumerate(ordered.iterrows()):
            ax.annotate(
                str(int(row["interval_index"])),
                xy=(row["hotspot_longitude"], row["hotspot_latitude"]),
                xytext=(row["hotspot_longitude"] + dx[idx], row["hotspot_latitude"] + dy[idx]),
                fontsize=8,
                color="black",
                ha="center",
                va="center",
                bbox={"boxstyle": "round,pad=0.16", "fc": "white", "ec": "0.25", "alpha": 0.85, "lw": 0.4},
                arrowprops={"arrowstyle": "-", "color": "0.2", "lw": 0.4, "alpha": 0.75},
                zorder=8,
            )

        start_row = ordered.iloc[0]
        end_row = ordered.iloc[-1]
        ax.scatter(start_row["hotspot_longitude"], start_row["hotspot_latitude"], s=90, facecolors="none", edgecolors="lime", linewidths=1.2, zorder=9)
        ax.scatter(end_row["hotspot_longitude"], end_row["hotspot_latitude"], s=90, facecolors="none", edgecolors="red", linewidths=1.2, zorder=9)
        legend_handles.extend([
            plt.Line2D([0], [0], color="black", lw=1.6, label="Hotspot migration path"),
            plt.Line2D([0], [0], marker="o", linestyle="None", markerfacecolor=cmap(0.55), markeredgecolor="black", markersize=7, label="Interval hotspot"),
            plt.Line2D([0], [0], marker="o", linestyle="None", markerfacecolor="none", markeredgecolor="lime", markersize=8, label="Stage start hotspot"),
            plt.Line2D([0], [0], marker="o", linestyle="None", markerfacecolor="none", markeredgecolor="red", markersize=8, label="Stage end hotspot"),
        ])
        sm = plt.cm.ScalarMappable(norm=Normalize(vmin=1, vmax=len(ordered)), cmap=MIGRATION_CMAP_NAME)
        sm.set_array([])
        cbar = fig.colorbar(sm, ax=ax, orientation="vertical", shrink=0.9, pad=0.02)
        cbar.set_label("Interval index", fontsize=10)
        cbar.ax.tick_params(labelsize=8)

    ax.legend(handles=legend_handles, loc="upper left", fontsize=8, frameon=True)
    ax.set_title(f"Hotspot migration path: {stage_name}")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    out_name = f"hotspot_migration_{stage_name}.png"
    out_path = output_dir / out_name
    fig.savefig(out_path, dpi=FIG_DPI)
    plt.close(fig)
    log(f"Saved hotspot migration figure: {out_path}")
    return out_name


def main() -> None:
    ensure_clean_output_dir(OUTPUT_DIR)
    arrays_dir = OUTPUT_DIR / "kde_arrays"

    catalog, mainshocks, faults, stage1, stage2, metadata = load_reference_inputs()
    extent_deg = get_extent(metadata)
    projected_extent = get_projected_extent(catalog, mainshocks, faults)
    x_grid, y_grid, xx, yy = make_grid(projected_extent)

    crs_info = metadata.get("projected_crs")
    if not isinstance(crs_info, dict) or "epsg" not in crs_info:
        raise ValueError("analysis_metadata.json missing projected_crs.epsg required for hotspot lon/lat back-transformation")
    utm_epsg = int(crs_info["epsg"])
    lonlat_transformer = Transformer.from_crs(f"EPSG:{utm_epsg}", "EPSG:4326", always_xy=True)

    bandwidth_m = estimate_fixed_bandwidth_m(catalog)
    log(f"Estimated fixed KDE bandwidth from full inter-mainshock catalog using Scott rule: {bandwidth_m:.2f} m")

    all_intervals = pd.concat([stage1, stage2], ignore_index=True)
    interval_rows = all_intervals.to_dict(orient="records")
    n_jobs = min(MAX_CORES, os.cpu_count() or 1, max(1, len(interval_rows)))
    log(f"Launching interval-parallel KDE computation with n_jobs={n_jobs} for {len(interval_rows)} intervals")

    results = Parallel(n_jobs=n_jobs, backend="loky")(
        delayed(compute_interval_kde)(row, catalog, xx, yy, x_grid, y_grid, lonlat_transformer, str(arrays_dir))
        for row in interval_rows
    )

    summary = pd.DataFrame(results).sort_values(["stage", "interval_index"]).reset_index(drop=True)
    summary_path = OUTPUT_DIR / "kde_interval_summary.csv"
    summary.to_csv(summary_path, index=False)
    log(f"Saved interval KDE summary: {summary_path}")

    valid_peak = summary.loc[summary["status"] == "ok", "peak_density"].dropna()
    if valid_peak.empty:
        raise RuntimeError("No valid KDE intervals were computed; cannot create normalization or figures.")
    global_max = float(valid_peak.max())
    norm = Normalize(vmin=0.0, vmax=global_max)

    norm_info = {
        "bandwidth_rule": BANDWIDTH_RULE,
        "estimated_fixed_bandwidth_m": bandwidth_m,
        "grid_shape": [int(GRID_SIZE_Y), int(GRID_SIZE_X)],
        "projected_extent_m": {
            "min_x": float(projected_extent[0]),
            "max_x": float(projected_extent[1]),
            "min_y": float(projected_extent[2]),
            "max_y": float(projected_extent[3]),
        },
        "plot_extent_degrees": {
            "min_longitude": float(extent_deg[0]),
            "max_longitude": float(extent_deg[1]),
            "min_latitude": float(extent_deg[2]),
            "max_latitude": float(extent_deg[3]),
        },
        "global_peak_density_max": global_max,
        "color_scale_vmin": 0.0,
        "color_scale_vmax": global_max,
    }
    norm_path = OUTPUT_DIR / "kde_global_normalization.json"
    with norm_path.open("w", encoding="utf-8") as f:
        json.dump(norm_info, f, indent=2)
    log(f"Saved KDE normalization metadata: {norm_path}")

    xx_lon = np.linspace(extent_deg[0], extent_deg[1], GRID_SIZE_X)
    yy_lat = np.linspace(extent_deg[2], extent_deg[3], GRID_SIZE_Y)
    xx_lon2d, yy_lat2d = np.meshgrid(xx_lon, yy_lat)

    fault_lines = build_fault_lines(faults)
    stage1_summary = summary.loc[summary["stage"] == "stage1"].copy().sort_values("interval_index")
    stage2_summary = summary.loc[summary["stage"] == "stage2"].copy().sort_values("interval_index")

    stage1_hotspots = stage1_summary.loc[stage1_summary["status"] == "ok"].copy()
    stage2_hotspots = stage2_summary.loc[stage2_summary["status"] == "ok"].copy()
    stage1_hotspots.to_csv(OUTPUT_DIR / "kde_stage1_hotspots.csv", index=False)
    stage2_hotspots.to_csv(OUTPUT_DIR / "kde_stage2_hotspots.csv", index=False)
    log(f"Saved hotspot tables for stage1 and stage2")

    save_kde_panel_pages("stage1", stage1_summary, extent_deg, xx_lon2d, yy_lat2d, fault_lines, mainshocks, OUTPUT_DIR, norm)
    save_kde_panel_pages("stage2", stage2_summary, extent_deg, xx_lon2d, yy_lat2d, fault_lines, mainshocks, OUTPUT_DIR, norm)

    fault_tree, fault_coords = build_fault_tree(faults)
    metrics_stage1 = compute_hotspot_metrics(stage1_hotspots, "stage1", mainshocks, fault_tree, fault_coords)
    metrics_stage2 = compute_hotspot_metrics(stage2_hotspots, "stage2", mainshocks, fault_tree, fault_coords)
    hotspot_metrics = pd.concat([metrics_stage1, metrics_stage2], ignore_index=True)
    metrics_path = OUTPUT_DIR / "hotspot_migration_metrics.csv"
    hotspot_metrics.to_csv(metrics_path, index=False)
    log(f"Saved hotspot migration metrics: {metrics_path}")

    plot_hotspot_migration("stage1", metrics_stage1, extent_deg, fault_lines, mainshocks, OUTPUT_DIR)
    plot_hotspot_migration("stage2", metrics_stage2, extent_deg, fault_lines, mainshocks, OUTPUT_DIR)

    log("02_kde_migration_analysis completed successfully.")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print(traceback.format_exc(), flush=True)
        sys.exit(1)
