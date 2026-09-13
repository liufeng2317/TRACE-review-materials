#!/usr/bin/env python
from __future__ import annotations

import os
import sys
import traceback
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, List, Tuple

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd
from pyproj import CRS, Transformer
from tqdm import tqdm


SCRIPT_PATH = Path(__file__).resolve()
OUTPUT_DIR = Path(
    "<REPO_ROOT>/examples/ridgecrest/catalog_analysis/run/01_2_trigger_spatiotemporal_fault_Q1-v1/exp_run/outputs/02_ridgecrest_figures_and_distribution_plots"
).resolve()
METRICS_DIR = Path(
    "<REPO_ROOT>/examples/ridgecrest/catalog_analysis/run/01_2_trigger_spatiotemporal_fault_Q1-v1/exp_run/outputs/01_ridgecrest_metrics_preparation"
).resolve()

CATALOG_PATH = METRICS_DIR / "catalog_clean_projected.csv"
MAINSHOCK_PATH = METRICS_DIR / "mainshock_reference.csv"
TIME_BINS_PATH = METRICS_DIR / "canonical_time_bins.csv"
MAP_EXTENT_PATH = METRICS_DIR / "canonical_map_extent.csv"
FAULT_SEGMENTS_PATH = METRICS_DIR / "fault_segments_projected.csv"
PRE71_METRICS_PATH = METRICS_DIR / "event_fault_metrics_pre71.csv"
POST71_METRICS_PATH = METRICS_DIR / "event_fault_metrics_post71.csv"
BIN_SUMMARY_PATH = METRICS_DIR / "bin_directional_summary.csv"
ALONG_STRIKE_PATH = METRICS_DIR / "along_strike_first_activation.csv"
QUESTION_SUMMARY_PATH = METRICS_DIR / "question_metric_summary.csv"

MAX_WORKERS = min(64, max(1, (os.cpu_count() or 1)))
FIG_DPI = 200
WGS84_CRS = CRS.from_epsg(4326)
LOCAL_AEQD_CRS = CRS.from_proj4(
    "+proj=aeqd +lat_0=35.74 +lon_0=-117.55 +datum=WGS84 +units=km +no_defs"
)
NEAR_FAULT_THRESHOLDS_KM = (0.25, 0.5, 1.0, 2.0, 5.0)
SPARSE_BIN_MIN_EVENTS = 10


def log(message: str) -> None:
    print(message, flush=True)


def ensure_output_dir() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    stale_patterns = [
        "ridgecrest_time_sliced_maps_page_*.png",
        "pre_post_mainshock71_comparison.png",
        "nearest_fault_distance_overall.png",
        "nearest_fault_distance_over_time.png",
        "orientation_and_misfit_vs_time.png",
        "centroid_and_along_strike_migration.png",
        "along_strike_occupancy_through_time.png",
        "comparison_summary.csv",
        "nearest_fault_distance_bin_statistics.csv",
        "question_metric_summary_copy.csv",
        "map_panel_manifest.csv",
        "figure_manifest.csv",
        "validation_summary.csv",
        "run_metadata.csv",
    ]
    for pattern in stale_patterns:
        for path in OUTPUT_DIR.glob(pattern):
            path.unlink()
            log(f"Removed stale output: {path}")


def read_csv_datetime(path: Path, datetime_cols: List[str]) -> pd.DataFrame:
    df = pd.read_csv(path)
    for col in datetime_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], utc=True, format="mixed")
    return df


def require_columns(df: pd.DataFrame, required: List[str], df_name: str) -> None:
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"{df_name} missing required columns: {missing}")



def load_inputs() -> Dict[str, pd.DataFrame]:
    log(f"Loading metrics from {METRICS_DIR}")
    required_paths = [
        CATALOG_PATH,
        MAINSHOCK_PATH,
        TIME_BINS_PATH,
        MAP_EXTENT_PATH,
        FAULT_SEGMENTS_PATH,
        PRE71_METRICS_PATH,
        POST71_METRICS_PATH,
        BIN_SUMMARY_PATH,
        ALONG_STRIKE_PATH,
        QUESTION_SUMMARY_PATH,
    ]
    missing = [str(path) for path in required_paths if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Missing required metrics files: {missing}")

    catalog = read_csv_datetime(CATALOG_PATH, ["event_time"])
    mainshocks = read_csv_datetime(MAINSHOCK_PATH, ["event_time"])
    time_bins = read_csv_datetime(TIME_BINS_PATH, ["start_time", "end_time"])
    map_extent = pd.read_csv(MAP_EXTENT_PATH)
    fault_segments = pd.read_csv(FAULT_SEGMENTS_PATH)
    pre71 = read_csv_datetime(PRE71_METRICS_PATH, ["event_time"])
    post71 = read_csv_datetime(POST71_METRICS_PATH, ["event_time"])
    bin_summary = read_csv_datetime(BIN_SUMMARY_PATH, ["start_time", "end_time"])
    along_strike = read_csv_datetime(ALONG_STRIKE_PATH, ["first_activation_time"])
    question_summary = pd.read_csv(QUESTION_SUMMARY_PATH)

    require_columns(catalog, ["event_time", "longitude", "latitude"], "catalog_clean_projected.csv")
    require_columns(mainshocks, ["event_time", "longitude", "latitude", "mainshock_label"], "mainshock_reference.csv")
    require_columns(time_bins, ["bin_id", "stage", "start_time", "end_time", "end_inclusive", "page", "subplot_index", "elapsed_hours_since_mainshock64"], "canonical_time_bins.csv")
    require_columns(map_extent, ["xmin_km", "xmax_km", "ymin_km", "ymax_km"], "canonical_map_extent.csv")
    require_columns(fault_segments, ["fault_id", "segment_id", "lon1", "lat1", "lon2", "lat2"], "fault_segments_projected.csv")
    require_columns(pre71, ["event_time", "longitude", "latitude", "nearest_fault_distance_km"], "event_fault_metrics_pre71.csv")
    require_columns(post71, ["event_time", "longitude", "latitude", "nearest_fault_distance_km"], "event_fault_metrics_post71.csv")
    require_columns(bin_summary, ["bin_id", "start_time", "end_time", "event_count", "principal_strike_deg", "dominant_local_fault_strike_deg", "angular_misfit_deg", "centroid_x_km", "centroid_y_km", "along_strike_min_km", "along_strike_max_km", "cumulative_occupied_range_km"], "bin_directional_summary.csv")
    require_columns(along_strike, ["along_strike_bin_index", "first_activation_time", "along_strike_bin_start_km", "along_strike_bin_end_km"], "along_strike_first_activation.csv")
    require_columns(question_summary, ["question", "metric_name", "metric_value", "interpretation_hint"], "question_metric_summary.csv")

    if len(mainshocks) != 2:
        raise ValueError("Expected exactly two mainshock rows")
    if map_extent.empty:
        raise ValueError("Map extent file is empty")
    if time_bins.empty or bin_summary.empty:
        raise ValueError("Time bins or bin summary is empty")

    return {
        "catalog": catalog,
        "mainshocks": mainshocks,
        "time_bins": time_bins,
        "map_extent": map_extent,
        "fault_segments": fault_segments,
        "pre71": pre71,
        "post71": post71,
        "bin_summary": bin_summary,
        "along_strike": along_strike,
        "question_summary": question_summary,
    }


def build_fault_polylines(fault_segments: pd.DataFrame) -> List[np.ndarray]:
    log("Reconstructing fault polylines from segment table")
    polylines: List[np.ndarray] = []
    grouped = fault_segments.sort_values(["fault_id", "segment_id"]).groupby("fault_id", sort=False)
    for fault_id, group in tqdm(grouped, desc="Fault polyline reconstruction"):
        xy = [[group.iloc[0]["lon1"], group.iloc[0]["lat1"]]]
        for _, row in group.iterrows():
            xy.append([row["lon2"], row["lat2"]])
        polylines.append(np.asarray(xy, dtype=float))
    log(f"Reconstructed {len(polylines):,} fault polylines")
    return polylines


def select_window(df: pd.DataFrame, start: pd.Timestamp, end: pd.Timestamp, end_inclusive: bool = False) -> pd.DataFrame:
    if end_inclusive:
        mask = (df["event_time"] >= start) & (df["event_time"] <= end)
    else:
        mask = (df["event_time"] >= start) & (df["event_time"] < end)
    return df.loc[mask].copy()


def format_window_label(start: pd.Timestamp, end: pd.Timestamp) -> str:
    return f"{start.strftime('%m-%d %H:%M')} to {end.strftime('%m-%d %H:%M')} UTC"


def build_page_payloads(time_bins: pd.DataFrame, catalog: pd.DataFrame) -> List[Tuple[int, List[Dict[str, object]]]]:
    payloads: List[Tuple[int, List[Dict[str, object]]]] = []
    for page, page_df in time_bins.sort_values(["page", "subplot_index"]).groupby("page", sort=True):
        page_bins: List[Dict[str, object]] = []
        for _, row in page_df.iterrows():
            start = row["start_time"]
            end = row["end_time"]
            end_inclusive = bool(row["end_inclusive"])
            if end_inclusive:
                current_mask = (catalog["event_time"] >= start) & (catalog["event_time"] <= end)
            else:
                current_mask = (catalog["event_time"] >= start) & (catalog["event_time"] < end)
            prior_mask = (catalog["event_time"] >= time_bins["start_time"].min()) & (catalog["event_time"] < start)
            current = catalog.loc[current_mask, ["longitude", "latitude"]].to_numpy(dtype=float)
            prior = catalog.loc[prior_mask, ["longitude", "latitude"]].to_numpy(dtype=float)
            page_bins.append(
                {
                    "bin_id": int(row["bin_id"]),
                    "subplot_index": int(row["subplot_index"]),
                    "stage": row["stage"],
                    "start": start,
                    "end": end,
                    "end_inclusive": end_inclusive,
                    "current": current,
                    "prior": prior,
                    "bin_event_count": int(len(current)),
                    "prior_event_count": int(len(prior)),
                    "elapsed_hours": float(row["elapsed_hours_since_mainshock64"]),
                }
            )
        payloads.append((int(page), page_bins))
    return payloads


def plot_time_sliced_map_page(
    page: int,
    page_bins: List[Dict[str, object]],
    fault_polylines: List[np.ndarray],
    mainshocks: pd.DataFrame,
    lon_limits: Tuple[float, float],
    lat_limits: Tuple[float, float],
    output_dir: str,
) -> Dict[str, object]:
    fig, axes = plt.subplots(2, 4, figsize=(18, 9), constrained_layout=True)
    axes = axes.ravel()

    ms64 = mainshocks.loc[mainshocks["mainshock_label"] == "Mainshock64"].iloc[0]
    ms71 = mainshocks.loc[mainshocks["mainshock_label"] == "Mainshock71"].iloc[0]

    for ax in axes:
        for poly in fault_polylines:
            ax.plot(poly[:, 0], poly[:, 1], color="black", linewidth=0.35, alpha=0.55, zorder=4)
        ax.scatter(ms64["longitude"], ms64["latitude"], marker="*", s=110, color="gold", edgecolor="black", linewidth=0.8, zorder=6)
        ax.scatter(ms71["longitude"], ms71["latitude"], marker="*", s=110, color="crimson", edgecolor="black", linewidth=0.8, zorder=6)
        ax.set_xlim(*lon_limits)
        ax.set_ylim(*lat_limits)
        ax.grid(True, alpha=0.2, linewidth=0.4)
        ax.set_aspect("equal", adjustable="box")

    used_indices = set()
    panel_rows: List[Dict[str, object]] = []
    for info in page_bins:
        idx = int(info["subplot_index"])
        used_indices.add(idx)
        ax = axes[idx]
        prior = info["prior"]
        current = info["current"]
        if len(prior):
            ax.scatter(prior[:, 0], prior[:, 1], s=5, color="silver", alpha=0.22, linewidths=0, zorder=1)
        if len(current):
            ax.scatter(current[:, 0], current[:, 1], s=8, color="royalblue", alpha=0.85, linewidths=0, zorder=3)
        ax.set_title(f"Bin {info['bin_id']} | {format_window_label(info['start'], info['end'])}", fontsize=9)
        ax.text(
            0.02,
            0.98,
            f"Stage: {info['stage']}\nΔt={info['elapsed_hours']:.1f} h\nCurrent: {info['bin_event_count']}\nPrior: {info['prior_event_count']}",
            transform=ax.transAxes,
            va="top",
            ha="left",
            fontsize=8,
            bbox=dict(facecolor="white", alpha=0.75, edgecolor="none", pad=2.5),
            zorder=7,
        )
        panel_rows.append(
            {
                "page": page,
                "bin_id": int(info["bin_id"]),
                "subplot_index": idx,
                "stage": info["stage"],
                "start_time": info["start"],
                "end_time": info["end"],
                "end_inclusive": info["end_inclusive"],
                "bin_event_count": int(info["bin_event_count"]),
                "prior_event_count": int(info["prior_event_count"]),
                "elapsed_hours_since_mainshock64": float(info["elapsed_hours"]),
                "figure_path": str(Path(output_dir) / f"ridgecrest_time_sliced_maps_page_{page:02d}.png"),
            }
        )

    for i, ax in enumerate(axes):
        if i not in used_indices:
            ax.axis("off")

    axes[0].legend(
        handles=[
            Line2D([0], [0], marker="o", color="w", markerfacecolor="royalblue", markersize=6, label="Events in current window"),
            Line2D([0], [0], marker="o", color="w", markerfacecolor="silver", alpha=0.6, markersize=6, label="Earlier events since Mw 6.4"),
            Line2D([0], [0], color="black", linewidth=1.0, label="Mapped faults"),
            Line2D([0], [0], marker="*", color="w", markerfacecolor="gold", markeredgecolor="black", markersize=11, label="Mw 6.4"),
            Line2D([0], [0], marker="*", color="w", markerfacecolor="crimson", markeredgecolor="black", markersize=11, label="Mw 7.1"),
        ],
        loc="lower left",
        fontsize=8,
        framealpha=0.9,
    )
    fig.suptitle("Ridgecrest seismicity evolution from Mw 6.4 to Mw 7.1", fontsize=14)
    out_path = Path(output_dir) / f"ridgecrest_time_sliced_maps_page_{page:02d}.png"
    fig.savefig(out_path, dpi=FIG_DPI, bbox_inches="tight")
    plt.close(fig)
    return {"page": page, "figure_path": str(out_path), "panel_rows": panel_rows}


def generate_time_sliced_maps(
    time_bins: pd.DataFrame,
    catalog: pd.DataFrame,
    fault_polylines: List[np.ndarray],
    mainshocks: pd.DataFrame,
    lon_limits: Tuple[float, float],
    lat_limits: Tuple[float, float],
) -> Tuple[pd.DataFrame, List[str]]:
    payloads = build_page_payloads(time_bins, catalog)
    log(f"Generating {len(payloads)} time-sliced map pages with up to {MAX_WORKERS} workers")
    panel_rows: List[Dict[str, object]] = []
    figure_paths: List[str] = []
    workers = min(MAX_WORKERS, max(1, len(payloads)))
    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(
                plot_time_sliced_map_page,
                page,
                page_bins,
                fault_polylines,
                mainshocks,
                lon_limits,
                lat_limits,
                str(OUTPUT_DIR),
            ): page
            for page, page_bins in payloads
        }
        for future in tqdm(as_completed(futures), total=len(futures), desc="Map pages"):
            result = future.result()
            figure_paths.append(result["figure_path"])
            panel_rows.extend(result["panel_rows"])
    manifest = pd.DataFrame(panel_rows).sort_values(["page", "subplot_index"]).reset_index(drop=True)
    return manifest, sorted(figure_paths)


def plot_pre_post_comparison(
    pre71: pd.DataFrame,
    post71: pd.DataFrame,
    mainshocks: pd.DataFrame,
    fault_polylines: List[np.ndarray],
    lon_limits: Tuple[float, float],
    lat_limits: Tuple[float, float],
) -> Tuple[Path, pd.DataFrame]:
    log("Generating pre/post Mw 7.1 comparison figure")
    fig, axes = plt.subplots(1, 2, figsize=(14, 7), constrained_layout=True)
    windows = [
        ("Before Mw 7.1", pre71, "royalblue"),
        ("After Mw 7.1 (+2 days)", post71, "darkorange"),
    ]
    summary_rows: List[Dict[str, object]] = []
    for ax, (label, df, color) in zip(axes, windows):
        for poly in fault_polylines:
            ax.plot(poly[:, 0], poly[:, 1], color="black", linewidth=0.35, alpha=0.55, zorder=3)
        ax.scatter(df["longitude"], df["latitude"], s=5, color=color, alpha=0.45, linewidths=0, zorder=2)
        for _, ms in mainshocks.iterrows():
            marker_color = "gold" if ms["mainshock_label"] == "Mainshock64" else "crimson"
            ax.scatter(ms["longitude"], ms["latitude"], marker="*", s=150, color=marker_color, edgecolor="black", linewidth=0.8, zorder=5)
        ax.set_xlim(*lon_limits)
        ax.set_ylim(*lat_limits)
        ax.set_aspect("equal", adjustable="box")
        ax.grid(True, alpha=0.2, linewidth=0.4)
        median_distance = float(df["nearest_fault_distance_km"].median()) if len(df) else np.nan
        centroid_lon = float(df["longitude"].mean()) if len(df) else np.nan
        centroid_lat = float(df["latitude"].mean()) if len(df) else np.nan
        ax.set_title(label)
        ax.text(
            0.02,
            0.98,
            f"Events: {len(df):,}\nMedian fault dist.: {median_distance:.3f} km",
            transform=ax.transAxes,
            ha="left",
            va="top",
            fontsize=9,
            bbox=dict(facecolor="white", alpha=0.8, edgecolor="none", pad=2.5),
        )
        summary_rows.append(
            {
                "window_label": label,
                "event_count": int(len(df)),
                "median_nearest_fault_distance_km": median_distance,
                "centroid_longitude": centroid_lon,
                "centroid_latitude": centroid_lat,
            }
        )
    axes[0].legend(
        handles=[
            Line2D([0], [0], marker="o", color="w", markerfacecolor="royalblue", markersize=6, label="Before Mw 7.1 events"),
            Line2D([0], [0], marker="o", color="w", markerfacecolor="darkorange", markersize=6, label="After Mw 7.1 events"),
            Line2D([0], [0], color="black", linewidth=1.0, label="Mapped faults"),
            Line2D([0], [0], marker="*", color="w", markerfacecolor="gold", markeredgecolor="black", markersize=11, label="Mw 6.4"),
            Line2D([0], [0], marker="*", color="w", markerfacecolor="crimson", markeredgecolor="black", markersize=11, label="Mw 7.1"),
        ],
        loc="lower left",
        fontsize=8,
        framealpha=0.9,
    )
    fig.suptitle("Ridgecrest seismicity before and after the Mw 7.1 mainshock", fontsize=14)
    out_path = OUTPUT_DIR / "pre_post_mainshock71_comparison.png"
    fig.savefig(out_path, dpi=FIG_DPI, bbox_inches="tight")
    plt.close(fig)
    return out_path, pd.DataFrame(summary_rows)


def compute_distance_bin_statistics(pre71: pd.DataFrame, time_bins: pd.DataFrame) -> pd.DataFrame:
    log("Computing nearest-fault distance statistics by time bin")
    rows: List[Dict[str, object]] = []
    for _, row in tqdm(time_bins.sort_values("bin_id").iterrows(), total=len(time_bins), desc="Distance stats"):
        start = row["start_time"]
        end = row["end_time"]
        end_inclusive = bool(row["end_inclusive"])
        subset = select_window(pre71, start, end, end_inclusive)
        d = subset["nearest_fault_distance_km"].to_numpy(dtype=float)
        out = {
            "bin_id": int(row["bin_id"]),
            "stage": row["stage"],
            "start_time": start,
            "end_time": end,
            "end_inclusive": end_inclusive,
            "event_count": int(len(subset)),
            "median_km": float(np.nanmedian(d)) if len(d) else np.nan,
            "q25_km": float(np.nanquantile(d, 0.25)) if len(d) else np.nan,
            "q75_km": float(np.nanquantile(d, 0.75)) if len(d) else np.nan,
            "q90_km": float(np.nanquantile(d, 0.90)) if len(d) else np.nan,
        }
        for thr in NEAR_FAULT_THRESHOLDS_KM:
            out[f"fraction_within_{thr:.2f}km"] = float(np.mean(d <= thr)) if len(d) else np.nan
        rows.append(out)
    return pd.DataFrame(rows)


def plot_nearest_fault_distance_figures(pre71: pd.DataFrame, distance_stats: pd.DataFrame) -> Tuple[Path, Path]:
    log("Generating nearest-fault distance figures")
    distances = pre71["nearest_fault_distance_km"].dropna().to_numpy(dtype=float)
    if len(distances) == 0:
        raise ValueError("No valid nearest-fault distances available for pre-Mw7.1 events")
    fig1, axes = plt.subplots(1, 2, figsize=(12, 5), constrained_layout=True)
    upper = float(np.nanquantile(distances, 0.995))
    if not np.isfinite(upper) or upper <= 0:
        upper = float(np.nanmax(distances)) if np.isfinite(np.nanmax(distances)) else 1.0
    if upper <= 0:
        upper = 1.0
    bins = np.linspace(0.0, upper, 60)
    axes[0].hist(distances, bins=bins, color="slateblue", alpha=0.85, edgecolor="white")
    axes[0].set_xlabel("Nearest fault distance (km)")
    axes[0].set_ylabel("Event count")
    axes[0].set_title("Overall nearest-fault distance histogram")
    sorted_d = np.sort(distances)
    ecdf = np.arange(1, len(sorted_d) + 1) / len(sorted_d)
    axes[1].plot(sorted_d, ecdf, color="darkgreen", linewidth=2)
    for thr in NEAR_FAULT_THRESHOLDS_KM:
        axes[1].axvline(thr, color="gray", linestyle="--", linewidth=0.7, alpha=0.7)
    axes[1].set_xlabel("Nearest fault distance (km)")
    axes[1].set_ylabel("ECDF")
    axes[1].set_title("Overall nearest-fault distance ECDF")
    overall_path = OUTPUT_DIR / "nearest_fault_distance_overall.png"
    fig1.savefig(overall_path, dpi=FIG_DPI, bbox_inches="tight")
    plt.close(fig1)

    fig2, axes = plt.subplots(2, 1, figsize=(13, 8), sharex=True, constrained_layout=True)
    x = distance_stats["start_time"] + (distance_stats["end_time"] - distance_stats["start_time"]) / 2
    axes[0].plot(x, distance_stats["median_km"], color="midnightblue", linewidth=2, marker="o", markersize=4)
    axes[0].fill_between(x, distance_stats["q25_km"], distance_stats["q75_km"], color="cornflowerblue", alpha=0.3)
    axes[0].set_ylabel("Distance (km)")
    axes[0].set_title("Nearest-fault distance evolution: median and IQR")
    axes[0].grid(True, alpha=0.25)

    for thr in (0.5, 1.0, 2.0):
        col = f"fraction_within_{thr:.2f}km"
        axes[1].plot(x, distance_stats[col], linewidth=2, marker="o", markersize=4, label=f"≤ {thr:.1f} km")
    axes[1].set_ylabel("Fraction of events")
    axes[1].set_xlabel("Time")
    axes[1].set_ylim(-0.02, 1.02)
    axes[1].set_title("Fraction of events near mapped faults over time")
    axes[1].grid(True, alpha=0.25)
    axes[1].legend()
    time_path = OUTPUT_DIR / "nearest_fault_distance_over_time.png"
    fig2.savefig(time_path, dpi=FIG_DPI, bbox_inches="tight")
    plt.close(fig2)
    return overall_path, time_path


def plot_orientation_and_misfit(bin_summary: pd.DataFrame, question_summary: pd.DataFrame) -> Path:
    log("Generating orientation and misfit synthesis figure")
    data = bin_summary.sort_values("bin_id").copy()
    x = data["start_time"] + (data["end_time"] - data["start_time"]) / 2
    sparse_mask = data["event_count"] < SPARSE_BIN_MIN_EVENTS
    fig, axes = plt.subplots(2, 1, figsize=(13, 8), sharex=True, constrained_layout=True)

    axes[0].plot(x, data["principal_strike_deg"], color="navy", marker="o", linewidth=2, markersize=4, label="Event-cloud principal strike")
    axes[0].plot(x, data["dominant_local_fault_strike_deg"], color="firebrick", marker="s", linewidth=1.5, markersize=4, label="Dominant local fault strike")
    if sparse_mask.any():
        axes[0].scatter(x[sparse_mask], data.loc[sparse_mask, "principal_strike_deg"], color="orange", marker="x", s=35, label="Sparse bins")
    axes[0].set_ylabel("Orientation (deg)")
    axes[0].set_ylim(0, 180)
    axes[0].set_title("Event-cloud orientation and mapped-fault orientation through time")
    axes[0].grid(True, alpha=0.25)
    axes[0].legend()

    axes[1].plot(x, data["angular_misfit_deg"], color="purple", marker="o", linewidth=2, markersize=4)
    misfit_match = question_summary.loc[question_summary["metric_name"] == "median_angular_misfit_deg", "metric_value"]
    if not misfit_match.empty:
        axes[1].axhline(float(misfit_match.iloc[0]), color="gray", linestyle="--", linewidth=1, label="Median misfit")
    axes[1].set_ylabel("Angular misfit (deg)")
    axes[1].set_xlabel("Time")
    axes[1].set_ylim(bottom=0)
    axes[1].set_title("Angular misfit between event cloud and local fault strike")
    axes[1].grid(True, alpha=0.25)
    axes[1].legend()

    out_path = OUTPUT_DIR / "orientation_and_misfit_vs_time.png"
    fig.savefig(out_path, dpi=FIG_DPI, bbox_inches="tight")
    plt.close(fig)
    return out_path


def estimate_lonlat_from_xy(x_km: np.ndarray, y_km: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    transformer = Transformer.from_crs(LOCAL_AEQD_CRS, WGS84_CRS, always_xy=True)
    lon, lat = transformer.transform(x_km, y_km)
    return np.asarray(lon, dtype=float), np.asarray(lat, dtype=float)


def plot_centroid_and_migration(bin_summary: pd.DataFrame) -> Path:
    log("Generating centroid and along-strike migration figure")
    data = bin_summary.sort_values("bin_id").copy()
    data["mid_time"] = data["start_time"] + (data["end_time"] - data["start_time"]) / 2
    data["hours_since_start"] = (data["mid_time"] - data["mid_time"].iloc[0]).dt.total_seconds() / 3600.0
    centroid_lon, centroid_lat = estimate_lonlat_from_xy(
        data["centroid_x_km"].to_numpy(dtype=float),
        data["centroid_y_km"].to_numpy(dtype=float),
    )

    fig = plt.figure(figsize=(14, 8), constrained_layout=True)
    gs = fig.add_gridspec(2, 2, width_ratios=[1.05, 1.45], height_ratios=[1, 1])
    ax_map = fig.add_subplot(gs[:, 0])
    ax_time = fig.add_subplot(gs[0, 1])
    ax_range = fig.add_subplot(gs[1, 1], sharex=ax_time)

    point_sizes = np.clip(data["event_count"].to_numpy(dtype=float) * 1.6, 28, 220)
    sc = ax_map.scatter(
        centroid_lon,
        centroid_lat,
        c=data["hours_since_start"],
        cmap="viridis",
        s=point_sizes,
        alpha=0.9,
        edgecolor="black",
        linewidth=0.35,
        zorder=3,
    )
    ax_map.plot(centroid_lon, centroid_lat, color="gray", linewidth=1.2, alpha=0.75, zorder=2)
    ax_map.scatter(centroid_lon[0], centroid_lat[0], marker="^", s=120, color="limegreen", edgecolor="black", linewidth=0.6, zorder=4)
    ax_map.scatter(centroid_lon[-1], centroid_lat[-1], marker="s", s=120, color="crimson", edgecolor="black", linewidth=0.6, zorder=4)
    lon_pad = max(0.01, 0.12 * (float(np.nanmax(centroid_lon)) - float(np.nanmin(centroid_lon))))
    lat_pad = max(0.01, 0.12 * (float(np.nanmax(centroid_lat)) - float(np.nanmin(centroid_lat))))
    ax_map.set_xlim(float(np.nanmin(centroid_lon)) - lon_pad, float(np.nanmax(centroid_lon)) + lon_pad)
    ax_map.set_ylim(float(np.nanmin(centroid_lat)) - lat_pad, float(np.nanmax(centroid_lat)) + lat_pad)
    ax_map.set_aspect("equal", adjustable="box")
    ax_map.set_xlabel("Longitude")
    ax_map.set_ylabel("Latitude")
    ax_map.set_title("Centroid migration map")
    ax_map.grid(True, alpha=0.25)
    ax_map.text(
        0.02,
        0.98,
        "Start = green triangle\nEnd = red square\nPoint size ∝ event count",
        transform=ax_map.transAxes,
        ha="left",
        va="top",
        fontsize=8,
        bbox=dict(facecolor="white", alpha=0.8, edgecolor="none", pad=2.5),
    )
    cbar = fig.colorbar(sc, ax=ax_map, pad=0.01)
    cbar.set_label("Hours since first bin midpoint")

    ax_time.plot(data["hours_since_start"], data["centroid_x_km"], color="royalblue", linewidth=1.8, marker="o", markersize=4, label="Centroid x (km)")
    ax_time.plot(data["hours_since_start"], data["centroid_y_km"], color="firebrick", linewidth=1.8, marker="s", markersize=4, label="Centroid y (km)")
    ax_time.set_ylabel("Centroid position (km)")
    ax_time.set_title("Centroid offsets through time (projected coordinates)")
    ax_time.grid(True, alpha=0.25)
    ax_time.legend(loc="best", fontsize=8)

    ax_range.plot(data["hours_since_start"], data["along_strike_min_km"], color="teal", linewidth=1.5, marker="o", markersize=4, label="Along-strike minimum")
    ax_range.plot(data["hours_since_start"], data["along_strike_max_km"], color="darkorange", linewidth=1.5, marker="o", markersize=4, label="Along-strike maximum")
    ax_range.fill_between(
        data["hours_since_start"],
        data["along_strike_min_km"],
        data["along_strike_max_km"],
        color="tan",
        alpha=0.35,
        label="Occupied along-strike range",
    )
    ax_range.step(
        data["hours_since_start"],
        data["cumulative_occupied_range_km"],
        where="mid",
        color="black",
        linewidth=2.0,
        linestyle="--",
        label="Cumulative occupied range",
    )
    x_pad = max(0.25, 0.03 * (float(data["hours_since_start"].max()) - float(data["hours_since_start"].min())))
    ax_time.set_xlim(float(data["hours_since_start"].min()) - x_pad, float(data["hours_since_start"].max()) + x_pad)
    ax_range.set_ylabel("Along-strike distance / range (km)")
    ax_range.set_xlabel("Hours since first bin midpoint")
    ax_range.set_title("Along-strike activation extent through time")
    ax_range.grid(True, alpha=0.25)
    ax_range.legend(ncol=2, fontsize=8, loc="best")

    fig.suptitle("Ridgecrest centroid migration and along-strike evolution", fontsize=14)
    out_path = OUTPUT_DIR / "centroid_and_along_strike_migration.png"
    fig.savefig(out_path, dpi=FIG_DPI, bbox_inches="tight")
    plt.close(fig)
    return out_path


def plot_along_strike_occupancy(along_strike: pd.DataFrame, time_bins: pd.DataFrame) -> Path:
    log("Generating along-strike occupancy figure")
    if along_strike.empty:
        raise ValueError("along_strike_first_activation.csv is empty")
    first_time = time_bins["start_time"].min()
    last_time = time_bins["end_time"].max()
    active = along_strike.copy()
    active["is_activated"] = active["first_activation_time"].notna()
    active["along_strike_bin_center_km"] = (active["along_strike_bin_start_km"] + active["along_strike_bin_end_km"]) / 2.0
    active = active.sort_values("along_strike_bin_center_km")

    merged = active.merge(
        time_bins[["bin_id", "start_time", "end_time"]],
        left_on="along_strike_bin_index",
        right_on="bin_id",
        how="left",
        suffixes=("", "_binref"),
    )
    if merged["start_time"].notna().any():
        active["first_activation_bin_id"] = merged["bin_id"]
    else:
        active["first_activation_bin_id"] = np.nan

    fig, axes = plt.subplots(2, 1, figsize=(13, 8), constrained_layout=True)
    activated = active.loc[active["is_activated"]].copy()
    if not activated.empty:
        color_values = activated["hours_since_mainshock64"] if "hours_since_mainshock64" in activated.columns else activated["first_activation_bin_id"]
        scatter = axes[0].scatter(
            activated["first_activation_time"],
            activated["along_strike_bin_center_km"],
            c=color_values,
            cmap="plasma",
            s=60,
            edgecolor="black",
            linewidth=0.3,
        )
        cbar = fig.colorbar(scatter, ax=axes[0], pad=0.01)
        cbar.set_label("Hours since Mw 6.4" if "hours_since_mainshock64" in activated.columns else "Along-strike bin index")
    axes[0].set_ylabel("Along-strike position (km)")
    axes[0].set_title("First activation time of along-strike spatial bins")
    axes[0].grid(True, alpha=0.25)
    axes[0].set_xlim(first_time, last_time)

    cumulative = []
    bin_times = []
    for _, row in time_bins.sort_values("bin_id").iterrows():
        t = row["end_time"]
        if bool(row["end_inclusive"]):
            n_active = int((active["first_activation_time"] <= t).sum())
        else:
            n_active = int((active["first_activation_time"] < t).sum())
        cumulative.append(n_active)
        bin_times.append(t)
    axes[1].step(bin_times, cumulative, where="post", color="darkslateblue", linewidth=2)
    axes[1].set_ylabel("Activated along-strike bins")
    axes[1].set_xlabel("Time")
    axes[1].set_title("Cumulative first-time activation of along-strike bins")
    axes[1].grid(True, alpha=0.25)

    out_path = OUTPUT_DIR / "along_strike_occupancy_through_time.png"
    fig.savefig(out_path, dpi=FIG_DPI, bbox_inches="tight")
    plt.close(fig)
    return out_path


def build_lonlat_limits(map_extent: pd.DataFrame) -> Tuple[Tuple[float, float], Tuple[float, float]]:
    row = map_extent.iloc[0]
    transformer = Transformer.from_crs(LOCAL_AEQD_CRS, WGS84_CRS, always_xy=True)
    xs = [row["xmin_km"], row["xmax_km"], row["xmax_km"], row["xmin_km"]]
    ys = [row["ymin_km"], row["ymin_km"], row["ymax_km"], row["ymax_km"]]
    lon, lat = transformer.transform(xs, ys)
    lon_limits = (float(np.min(lon)), float(np.max(lon)))
    lat_limits = (float(np.min(lat)), float(np.max(lat)))
    return lon_limits, lat_limits


def validate_outputs(figure_paths: List[Path | str], tables: List[Path]) -> pd.DataFrame:
    rows = []
    for path_like in figure_paths + tables:
        path = Path(path_like)
        exists = path.exists()
        size = path.stat().st_size if exists else 0
        rows.append({"path": str(path), "exists": exists, "size_bytes": int(size)})
        if not exists or size <= 0:
            raise FileNotFoundError(f"Expected non-empty output missing or empty: {path}")
    return pd.DataFrame(rows)


def main() -> None:
    ensure_output_dir()
    inputs = load_inputs()

    catalog = inputs["catalog"]
    mainshocks = inputs["mainshocks"]
    time_bins = inputs["time_bins"].sort_values("bin_id").reset_index(drop=True)
    map_extent = inputs["map_extent"]
    pre71 = inputs["pre71"]
    post71 = inputs["post71"]
    bin_summary = inputs["bin_summary"]
    along_strike = inputs["along_strike"]
    question_summary = inputs["question_summary"]
    fault_polylines = build_fault_polylines(inputs["fault_segments"])
    lon_limits, lat_limits = build_lonlat_limits(map_extent)

    map_manifest, map_figures = generate_time_sliced_maps(
        time_bins=time_bins,
        catalog=catalog,
        fault_polylines=fault_polylines,
        mainshocks=mainshocks,
        lon_limits=lon_limits,
        lat_limits=lat_limits,
    )
    map_manifest_path = OUTPUT_DIR / "map_panel_manifest.csv"
    map_manifest.to_csv(map_manifest_path, index=False)
    log(f"Saved map panel manifest: {map_manifest_path}")

    comparison_fig_path, comparison_summary = plot_pre_post_comparison(
        pre71=pre71,
        post71=post71,
        mainshocks=mainshocks,
        fault_polylines=fault_polylines,
        lon_limits=lon_limits,
        lat_limits=lat_limits,
    )
    comparison_summary_path = OUTPUT_DIR / "comparison_summary.csv"
    comparison_summary.to_csv(comparison_summary_path, index=False)

    distance_stats = compute_distance_bin_statistics(pre71, time_bins)
    distance_stats_path = OUTPUT_DIR / "nearest_fault_distance_bin_statistics.csv"
    distance_stats.to_csv(distance_stats_path, index=False)
    overall_dist_path, time_dist_path = plot_nearest_fault_distance_figures(pre71, distance_stats)

    orientation_path = plot_orientation_and_misfit(bin_summary, question_summary)
    centroid_path = plot_centroid_and_migration(bin_summary)
    occupancy_path = plot_along_strike_occupancy(along_strike, time_bins)

    question_copy_path = OUTPUT_DIR / "question_metric_summary_copy.csv"
    question_summary.to_csv(question_copy_path, index=False)

    figure_manifest = pd.DataFrame(
        [
            {"figure_type": "time_sliced_map", "path": str(path)} for path in map_figures
        ]
        + [
            {"figure_type": "pre_post_comparison", "path": str(comparison_fig_path)},
            {"figure_type": "nearest_fault_distance_overall", "path": str(overall_dist_path)},
            {"figure_type": "nearest_fault_distance_over_time", "path": str(time_dist_path)},
            {"figure_type": "orientation_and_misfit", "path": str(orientation_path)},
            {"figure_type": "centroid_and_migration", "path": str(centroid_path)},
            {"figure_type": "along_strike_occupancy", "path": str(occupancy_path)},
        ]
    )
    figure_manifest_path = OUTPUT_DIR / "figure_manifest.csv"
    figure_manifest.to_csv(figure_manifest_path, index=False)

    run_metadata = pd.DataFrame(
        [
            {"key": "script_path", "value": str(SCRIPT_PATH)},
            {"key": "metrics_dir", "value": str(METRICS_DIR)},
            {"key": "output_dir", "value": str(OUTPUT_DIR)},
            {"key": "max_workers", "value": str(MAX_WORKERS)},
            {"key": "n_time_bins", "value": str(len(time_bins))},
            {"key": "n_map_pages", "value": str(map_manifest["page"].nunique())},
            {"key": "n_pre71_events", "value": str(len(pre71))},
            {"key": "n_post71_events", "value": str(len(post71))},
        ]
    )
    run_metadata_path = OUTPUT_DIR / "run_metadata.csv"
    run_metadata.to_csv(run_metadata_path, index=False)

    validation = validate_outputs(
        figure_paths=figure_manifest["path"].tolist(),
        tables=[
            map_manifest_path,
            comparison_summary_path,
            distance_stats_path,
            question_copy_path,
            figure_manifest_path,
            run_metadata_path,
        ],
    )
    validation_path = OUTPUT_DIR / "validation_summary.csv"
    validation.to_csv(validation_path, index=False)
    log(f"Validation summary saved: {validation_path}")
    log("Task 02_ridgecrest_figures_and_distribution_plots completed successfully")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print(traceback.format_exc(), file=sys.stderr, flush=True)
        sys.exit(1)
