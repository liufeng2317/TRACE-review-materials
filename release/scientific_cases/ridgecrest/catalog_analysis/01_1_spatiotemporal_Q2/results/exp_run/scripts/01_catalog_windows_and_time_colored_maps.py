from __future__ import annotations

import math
import os
import shutil
import sys
import traceback
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import ListedColormap
from pyproj import CRS, Transformer
from sklearn.decomposition import PCA


CATALOG_PATH = Path(
    "<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/TRACE_ridgecrest_relocated.csv"
).resolve()
MAINSHOCK_PATH = Path(
    "<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/main_shock_events.csv"
).resolve()
SCRIPT_PATH = Path(__file__).resolve()
OUTPUT_DIR = Path(
    "<REPO_ROOT>/examples/ridgecrest/catalog_analysis/run/01_1_trigger_spatiotemporal_Q2-v1/exp_run/outputs/01_catalog_windows_and_time_colored_maps"
).resolve()

EXPECTED_COLUMNS = ["event_time", "latitude", "longitude", "depth_km", "magnitude"]
SHORT_WINDOW_HOURS = 4.0
SHORT_BIN_MINUTES = 30
LONG_BIN_HOURS = 2
FIG_DPI = 220
N_CORES = min(64, max(1, (os.cpu_count() or 1)))


@dataclass(frozen=True)
class MainshockReference:
    label: str
    event_time: pd.Timestamp
    latitude: float
    longitude: float
    depth_km: float
    magnitude: float


@dataclass(frozen=True)
class WindowDefinition:
    name: str
    start_time: pd.Timestamp
    end_time: pd.Timestamp
    bin_minutes: int
    rel_unit_label: str


def log(message: str) -> None:
    print(message, flush=True)


def ensure_clean_output_dir(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    removable_patterns = ["*.csv", "*.png", "*.jpg", "*.jpeg", "*.json", "*.txt"]
    removed = 0
    for pattern in removable_patterns:
        for path in output_dir.glob(pattern):
            if path.is_file():
                path.unlink()
                removed += 1
    for subdir_name in ["figures", "tables", "logs"]:
        subdir = output_dir / subdir_name
        if subdir.exists():
            shutil.rmtree(subdir)
    (output_dir / "figures").mkdir(parents=True, exist_ok=True)
    (output_dir / "tables").mkdir(parents=True, exist_ok=True)
    (output_dir / "logs").mkdir(parents=True, exist_ok=True)
    log(f"Prepared clean output directory: {output_dir} (removed {removed} top-level files)")


def validate_schema(df: pd.DataFrame, source_name: str) -> None:
    missing = [col for col in EXPECTED_COLUMNS if col not in df.columns]
    extra = [col for col in df.columns if col not in EXPECTED_COLUMNS]
    if missing:
        raise ValueError(f"{source_name} missing required columns: {missing}")
    if extra:
        log(f"Warning: {source_name} has extra columns that will be ignored: {extra}")


def load_catalog() -> pd.DataFrame:
    log(f"Loading catalog: {CATALOG_PATH}")
    df = pd.read_csv(CATALOG_PATH)
    validate_schema(df, "catalog")
    df = df[EXPECTED_COLUMNS].copy()
    df["event_time"] = pd.to_datetime(df["event_time"], utc=True)
    for col in ["latitude", "longitude", "depth_km", "magnitude"]:
        df[col] = pd.to_numeric(df[col], errors="raise")
    if df[EXPECTED_COLUMNS].isna().any().any():
        raise ValueError("Catalog contains missing values in required columns.")
    df = df.sort_values("event_time").reset_index(drop=True)
    df["event_id"] = np.arange(len(df), dtype=np.int64)
    log(f"Loaded catalog rows: {len(df):,}")
    return df


def load_mainshocks() -> Tuple[MainshockReference, MainshockReference, pd.DataFrame]:
    log(f"Loading mainshock table: {MAINSHOCK_PATH}")
    df = pd.read_csv(MAINSHOCK_PATH)
    validate_schema(df, "main_shock_events")
    df = df[EXPECTED_COLUMNS].copy()
    df["event_time"] = pd.to_datetime(df["event_time"], utc=True)
    for col in ["latitude", "longitude", "depth_km", "magnitude"]:
        df[col] = pd.to_numeric(df[col], errors="raise")

    mw64_rows = df[np.isclose(df["magnitude"], 6.4)]
    mw71_rows = df[np.isclose(df["magnitude"], 7.1)]
    if len(mw64_rows) != 1 or len(mw71_rows) != 1:
        raise ValueError("Expected unique Mw 6.4 and Mw 7.1 rows in main_shock_events.csv")

    def row_to_ref(label: str, row: pd.Series) -> MainshockReference:
        return MainshockReference(
            label=label,
            event_time=row["event_time"],
            latitude=float(row["latitude"]),
            longitude=float(row["longitude"]),
            depth_km=float(row["depth_km"]),
            magnitude=float(row["magnitude"]),
        )

    ms64 = row_to_ref("Mainshock64", mw64_rows.iloc[0])
    ms71 = row_to_ref("Mainshock71", mw71_rows.iloc[0])
    if not ms71.event_time > ms64.event_time:
        raise ValueError("Mw 7.1 event time must be later than Mw 6.4 event time")

    checked = pd.DataFrame(
        [
            {
                "label": ms64.label,
                "event_time": ms64.event_time.isoformat(),
                "latitude": ms64.latitude,
                "longitude": ms64.longitude,
                "depth_km": ms64.depth_km,
                "magnitude": ms64.magnitude,
            },
            {
                "label": ms71.label,
                "event_time": ms71.event_time.isoformat(),
                "latitude": ms71.latitude,
                "longitude": ms71.longitude,
                "depth_km": ms71.depth_km,
                "magnitude": ms71.magnitude,
            },
        ]
    )
    return ms64, ms71, checked


def build_local_transformer(center_lon: float, center_lat: float) -> Tuple[Transformer, str]:
    zone = int(math.floor((center_lon + 180.0) / 6.0) + 1)
    epsg = 32600 + zone if center_lat >= 0 else 32700 + zone
    crs = CRS.from_epsg(epsg)
    transformer = Transformer.from_crs("EPSG:4326", crs, always_xy=True)
    return transformer, crs.to_string()


def add_relative_time_and_projection(
    catalog: pd.DataFrame,
    ms64: MainshockReference,
    ms71: MainshockReference,
) -> Tuple[pd.DataFrame, Dict[str, float]]:
    log("Deriving relative-time fields and projected coordinates")
    center_lon = (ms64.longitude + ms71.longitude) / 2.0
    center_lat = (ms64.latitude + ms71.latitude) / 2.0
    transformer, crs_name = build_local_transformer(center_lon, center_lat)

    x_m, y_m = transformer.transform(catalog["longitude"].to_numpy(), catalog["latitude"].to_numpy())
    ms64_x_m, ms64_y_m = transformer.transform(ms64.longitude, ms64.latitude)
    ms71_x_m, ms71_y_m = transformer.transform(ms71.longitude, ms71.latitude)

    enriched = catalog.copy()
    delta = enriched["event_time"] - ms64.event_time
    enriched["time_rel_sec_from_64"] = delta.dt.total_seconds()
    enriched["time_rel_min_from_64"] = enriched["time_rel_sec_from_64"] / 60.0
    enriched["time_rel_hr_from_64"] = enriched["time_rel_sec_from_64"] / 3600.0
    enriched["x_km"] = x_m / 1000.0
    enriched["y_km"] = y_m / 1000.0

    projection_meta = {
        "projection_crs": crs_name,
        "projection_center_lon": center_lon,
        "projection_center_lat": center_lat,
        "mainshock64_x_km": ms64_x_m / 1000.0,
        "mainshock64_y_km": ms64_y_m / 1000.0,
        "mainshock71_x_km": ms71_x_m / 1000.0,
        "mainshock71_y_km": ms71_y_m / 1000.0,
    }
    return enriched, projection_meta


def require_columns(df: pd.DataFrame, required: List[str], context: str) -> None:
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"{context} missing required columns: {missing}")



def subset_window(df: pd.DataFrame, window: WindowDefinition) -> pd.DataFrame:
    require_columns(df, ["event_time"], f"subset_window input for {window.name}")
    mask = (df["event_time"] >= window.start_time) & (df["event_time"] <= window.end_time)
    subset = df.loc[mask].copy().reset_index(drop=True)
    if subset.empty:
        raise ValueError(f"Window {window.name} is empty")
    return subset


def assign_time_bins(
    df: pd.DataFrame,
    window: WindowDefinition,
    reference_time: pd.Timestamp,
) -> Tuple[pd.DataFrame, pd.DataFrame, np.ndarray]:
    require_columns(df, ["event_time"], f"assign_time_bins input for {window.name}")
    subset = df.copy()
    rel_minutes = (subset["event_time"] - reference_time).dt.total_seconds() / 60.0
    subset["time_since_64_min"] = rel_minutes

    duration_minutes = (window.end_time - window.start_time).total_seconds() / 60.0
    if duration_minutes <= 0:
        raise ValueError(f"Window {window.name} has non-positive duration: {duration_minutes} minutes")

    edges = np.arange(0.0, duration_minutes + window.bin_minutes, window.bin_minutes, dtype=float)
    if edges[-1] < duration_minutes:
        edges = np.append(edges, duration_minutes)
    elif edges[-1] > duration_minutes:
        if not np.isclose(edges[-1], duration_minutes):
            edges = np.append(edges, duration_minutes)
        else:
            edges[-1] = duration_minutes
    if len(edges) < 2:
        edges = np.array([0.0, duration_minutes], dtype=float)

    rel_array = rel_minutes.to_numpy(dtype=float)
    if np.any(rel_array < -1e-9) or np.any(rel_array > duration_minutes + 1e-9):
        raise ValueError(f"Found event times outside window bounds for {window.name}")

    bin_indices = np.searchsorted(edges, rel_array, side="right") - 1
    bin_indices = np.where(np.isclose(rel_array, duration_minutes), len(edges) - 2, bin_indices)
    bin_indices = np.clip(bin_indices, 0, len(edges) - 2)

    labels = []
    starts = edges[:-1]
    ends = edges[1:]
    for start_min, end_min in zip(starts, ends):
        if window.bin_minutes < 60:
            label = f"{int(round(start_min))}-{int(round(end_min))} min"
        else:
            label = f"{start_min / 60.0:.1f}-{end_min / 60.0:.1f} h"
        labels.append(label)

    subset["time_bin_index"] = bin_indices.astype(int)
    subset["time_bin_label"] = [labels[idx] for idx in subset["time_bin_index"]]
    subset["time_bin_start_min"] = [starts[idx] for idx in subset["time_bin_index"]]
    subset["time_bin_end_min"] = [ends[idx] for idx in subset["time_bin_index"]]

    require_columns(
        subset,
        ["time_bin_index", "time_bin_label", "time_bin_start_min", "time_bin_end_min"],
        f"assign_time_bins output for {window.name}",
    )

    all_bins = pd.DataFrame(
        {
            "window_name": window.name,
            "time_bin_index": np.arange(len(starts), dtype=int),
            "time_bin_start_min": starts,
            "time_bin_end_min": ends,
            "time_bin_label": labels,
        }
    )
    counts = subset.groupby("time_bin_index", as_index=False).size().rename(columns={"size": "event_count"})
    summary = all_bins.merge(counts, on="time_bin_index", how="left", validate="one_to_one")
    summary["event_count"] = summary["event_count"].fillna(0).astype(int)
    require_columns(
        summary,
        ["window_name", "time_bin_index", "time_bin_start_min", "time_bin_end_min", "time_bin_label", "event_count"],
        f"time bin summary for {window.name}",
    )
    return subset, summary, edges


def make_discrete_cmap(n: int) -> ListedColormap:
    base = plt.get_cmap("viridis", n)
    colors = base(np.arange(n))
    return ListedColormap(colors)


def plot_time_colored_epicenters(
    df: pd.DataFrame,
    bin_summary: pd.DataFrame,
    ms64: MainshockReference,
    ms71: MainshockReference,
    window: WindowDefinition,
    figure_path: Path,
    metadata_rows: List[Dict[str, object]],
) -> None:
    require_columns(df, ["longitude", "latitude", "time_bin_index"], f"plot input for {window.name}")
    require_columns(
        bin_summary,
        ["time_bin_index", "time_bin_label", "time_bin_start_min", "time_bin_end_min", "event_count"],
        f"bin summary for plotting {window.name}",
    )
    log(f"Creating figure: {figure_path.name}")
    n_bins = len(bin_summary)
    cmap = make_discrete_cmap(max(n_bins, 1))

    fig, ax = plt.subplots(figsize=(10.5, 8.5))

    for idx in sorted(df["time_bin_index"].unique(), reverse=True):
        part = df[df["time_bin_index"] == idx]
        ax.scatter(
            part["longitude"],
            part["latitude"],
            s=8,
            c=[cmap(idx)],
            alpha=0.85,
            linewidths=0.0,
            rasterized=False,
        )

    ax.scatter(
        ms64.longitude,
        ms64.latitude,
        s=180,
        marker="*",
        c="red",
        edgecolors="black",
        linewidths=0.8,
        label="Mw 6.4",
        zorder=5,
    )
    ax.scatter(
        ms71.longitude,
        ms71.latitude,
        s=180,
        marker="^",
        c="white",
        edgecolors="black",
        linewidths=1.0,
        label="Mw 7.1",
        zorder=5,
    )

    handles = []
    labels = []
    for _, row in bin_summary.iterrows():
        idx = int(row["time_bin_index"])
        handle = plt.Line2D(
            [0],
            [0],
            marker="o",
            color="none",
            markerfacecolor=cmap(idx),
            markeredgecolor="none",
            markersize=7,
        )
        handles.append(handle)
        labels.append(f"{row['time_bin_label']} (n={int(row['event_count'])})")
        metadata_rows.append(
            {
                "window_name": window.name,
                "time_bin_index": idx,
                "time_bin_label": row["time_bin_label"],
                "time_bin_start_min": row["time_bin_start_min"],
                "time_bin_end_min": row["time_bin_end_min"],
                "rgba": ",".join(f"{v:.6f}" for v in cmap(idx)),
            }
        )

    ms_handle1 = plt.Line2D([0], [0], marker="*", color="none", markerfacecolor="red", markeredgecolor="black", markersize=12)
    ms_handle2 = plt.Line2D([0], [0], marker="^", color="none", markerfacecolor="white", markeredgecolor="black", markersize=10)
    handles.extend([ms_handle1, ms_handle2])
    labels.extend(["Mw 6.4 epicenter", "Mw 7.1 epicenter"])

    ax.legend(handles, labels, loc="center left", bbox_to_anchor=(1.02, 0.5), frameon=True, fontsize=8)
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_title(
        f"Ridgecrest seismicity after Mw 6.4: {window.name.replace('_', ' ')}\n"
        f"Discrete time bins ({window.bin_minutes} min per bin)"
    )
    ax.grid(True, alpha=0.25, linestyle="--")
    ax.set_aspect("equal", adjustable="datalim")
    fig.tight_layout()
    fig.savefig(figure_path, dpi=FIG_DPI, bbox_inches="tight")
    plt.close(fig)


def compute_pca_spatial_summary(df: pd.DataFrame, bin_summary: pd.DataFrame) -> pd.DataFrame:
    require_columns(df, ["time_bin_index", "x_km", "y_km", "longitude", "latitude"], "spatial summary input")
    require_columns(
        bin_summary,
        ["window_name", "time_bin_index", "time_bin_label", "time_bin_start_min", "time_bin_end_min", "event_count"],
        "spatial summary bin table",
    )
    log("Computing per-bin projected spatial summaries")
    rows: List[Dict[str, object]] = []
    prev_centroid = None
    for _, bin_row in bin_summary.iterrows():
        idx = int(bin_row["time_bin_index"])
        part = df[df["time_bin_index"] == idx].copy()
        record: Dict[str, object] = {
            "window_name": bin_row["window_name"],
            "time_bin_index": idx,
            "time_bin_label": bin_row["time_bin_label"],
            "time_bin_start_min": float(bin_row["time_bin_start_min"]),
            "time_bin_end_min": float(bin_row["time_bin_end_min"]),
            "event_count": int(bin_row["event_count"]),
        }
        if part.empty:
            record.update(
                {
                    "centroid_x_km": np.nan,
                    "centroid_y_km": np.nan,
                    "centroid_lon": np.nan,
                    "centroid_lat": np.nan,
                    "pca_axis1_std_km": np.nan,
                    "pca_axis2_std_km": np.nan,
                    "pca_axis1_azimuth_deg": np.nan,
                    "centroid_step_from_prev_km": np.nan,
                    "summary_quality": "empty_bin",
                }
            )
        else:
            xy = part[["x_km", "y_km"]].to_numpy()
            centroid = xy.mean(axis=0)
            record["centroid_x_km"] = centroid[0]
            record["centroid_y_km"] = centroid[1]
            record["centroid_lon"] = float(part["longitude"].mean())
            record["centroid_lat"] = float(part["latitude"].mean())
            if len(part) >= 2:
                pca = PCA(n_components=2)
                pca.fit(xy)
                stds = np.sqrt(np.maximum(pca.explained_variance_, 0.0))
                comp = pca.components_[0]
                azimuth = (90.0 - math.degrees(math.atan2(comp[1], comp[0]))) % 180.0
                record["pca_axis1_std_km"] = float(stds[0])
                record["pca_axis2_std_km"] = float(stds[1])
                record["pca_axis1_azimuth_deg"] = float(azimuth)
                record["summary_quality"] = "pca_ok" if len(part) >= 5 else "low_count_pca"
            else:
                record["pca_axis1_std_km"] = np.nan
                record["pca_axis2_std_km"] = np.nan
                record["pca_axis1_azimuth_deg"] = np.nan
                record["summary_quality"] = "single_event"
            if prev_centroid is None:
                record["centroid_step_from_prev_km"] = np.nan
            else:
                record["centroid_step_from_prev_km"] = float(np.linalg.norm(centroid - prev_centroid))
            prev_centroid = centroid
        rows.append(record)
    return pd.DataFrame(rows)


def add_mainshock_distance_metrics(
    spatial_summary: pd.DataFrame,
    projection_meta: Dict[str, float],
) -> pd.DataFrame:
    require_columns(spatial_summary, ["centroid_x_km", "centroid_y_km"], "distance metric input")
    ms64_xy = np.array([projection_meta["mainshock64_x_km"], projection_meta["mainshock64_y_km"]])
    ms71_xy = np.array([projection_meta["mainshock71_x_km"], projection_meta["mainshock71_y_km"]])
    df = spatial_summary.copy()
    centroids = df[["centroid_x_km", "centroid_y_km"]].to_numpy(dtype=float)
    dist64 = np.full(len(df), np.nan)
    dist71 = np.full(len(df), np.nan)
    good = np.isfinite(centroids).all(axis=1)
    dist64[good] = np.linalg.norm(centroids[good] - ms64_xy, axis=1)
    dist71[good] = np.linalg.norm(centroids[good] - ms71_xy, axis=1)
    df["centroid_dist_to_mw64_km"] = dist64
    df["centroid_dist_to_mw71_km"] = dist71
    return df


def write_validation_summary(
    catalog: pd.DataFrame,
    short_df: pd.DataFrame,
    long_df: pd.DataFrame,
    projection_meta: Dict[str, float],
    ms64: MainshockReference,
    ms71: MainshockReference,
    out_path: Path,
) -> None:
    rows = [
        {
            "dataset": "catalog_full",
            "event_count": len(catalog),
            "start_time": catalog["event_time"].min().isoformat(),
            "end_time": catalog["event_time"].max().isoformat(),
            "min_longitude": catalog["longitude"].min(),
            "max_longitude": catalog["longitude"].max(),
            "min_latitude": catalog["latitude"].min(),
            "max_latitude": catalog["latitude"].max(),
            "projection_crs": projection_meta["projection_crs"],
        },
        {
            "dataset": "window_short_64_to_4h",
            "event_count": len(short_df),
            "start_time": short_df["event_time"].min().isoformat(),
            "end_time": short_df["event_time"].max().isoformat(),
            "min_longitude": short_df["longitude"].min(),
            "max_longitude": short_df["longitude"].max(),
            "min_latitude": short_df["latitude"].min(),
            "max_latitude": short_df["latitude"].max(),
            "projection_crs": projection_meta["projection_crs"],
        },
        {
            "dataset": "window_long_64_to_71",
            "event_count": len(long_df),
            "start_time": long_df["event_time"].min().isoformat(),
            "end_time": long_df["event_time"].max().isoformat(),
            "min_longitude": long_df["longitude"].min(),
            "max_longitude": long_df["longitude"].max(),
            "min_latitude": long_df["latitude"].min(),
            "max_latitude": long_df["latitude"].max(),
            "projection_crs": projection_meta["projection_crs"],
        },
        {
            "dataset": "mainshock_reference",
            "event_count": 2,
            "start_time": ms64.event_time.isoformat(),
            "end_time": ms71.event_time.isoformat(),
            "min_longitude": min(ms64.longitude, ms71.longitude),
            "max_longitude": max(ms64.longitude, ms71.longitude),
            "min_latitude": min(ms64.latitude, ms71.latitude),
            "max_latitude": max(ms64.latitude, ms71.latitude),
            "projection_crs": projection_meta["projection_crs"],
        },
    ]
    pd.DataFrame(rows).to_csv(out_path, index=False)


def main() -> None:
    log(f"Using up to {N_CORES} CPU cores where applicable")
    ensure_clean_output_dir(OUTPUT_DIR)

    tables_dir = OUTPUT_DIR / "tables"
    figures_dir = OUTPUT_DIR / "figures"

    catalog = load_catalog()
    ms64, ms71, mainshock_checked = load_mainshocks()
    mainshock_checked.to_csv(tables_dir / "mainshock_reference_checked.csv", index=False)

    catalog_enriched, projection_meta = add_relative_time_and_projection(catalog, ms64, ms71)
    catalog_enriched.to_csv(tables_dir / "ridgecrest_catalog_enriched.csv", index=False)

    short_window = WindowDefinition(
        name="64_to_4h",
        start_time=ms64.event_time,
        end_time=ms64.event_time + pd.Timedelta(hours=SHORT_WINDOW_HOURS),
        bin_minutes=SHORT_BIN_MINUTES,
        rel_unit_label="minutes",
    )
    long_window = WindowDefinition(
        name="64_to_71",
        start_time=ms64.event_time,
        end_time=ms71.event_time,
        bin_minutes=LONG_BIN_HOURS * 60,
        rel_unit_label="hours",
    )

    require_columns(
        catalog_enriched,
        [
            "event_id",
            "event_time",
            "latitude",
            "longitude",
            "depth_km",
            "magnitude",
            "time_rel_sec_from_64",
            "time_rel_min_from_64",
            "time_rel_hr_from_64",
            "x_km",
            "y_km",
        ],
        "catalog_enriched",
    )

    log("Extracting analysis windows")
    short_df = subset_window(catalog_enriched, short_window)
    long_df = subset_window(catalog_enriched, long_window)
    short_df.to_csv(tables_dir / "ridgecrest_window_short_64_to_4h.csv", index=False)
    long_df.to_csv(tables_dir / "ridgecrest_window_long_64_to_71.csv", index=False)

    if long_df["event_time"].max() > ms71.event_time:
        raise ValueError("Long window contains events after Mw 7.1")

    log(f"Short-window events: {len(short_df):,}")
    log(f"Long-window events: {len(long_df):,}")

    color_metadata_rows: List[Dict[str, object]] = []

    short_binned, short_bin_summary, _ = assign_time_bins(short_df, short_window, ms64.event_time)
    short_binned.to_csv(tables_dir / "ridgecrest_window_short_64_to_4h_binned.csv", index=False)
    short_bin_summary.to_csv(tables_dir / "time_bin_counts_64_to_4h.csv", index=False)
    plot_time_colored_epicenters(
        short_binned,
        short_bin_summary,
        ms64,
        ms71,
        short_window,
        figures_dir / "time_colored_epicenters_64_to_4h.png",
        color_metadata_rows,
    )

    long_binned, long_bin_summary, _ = assign_time_bins(long_df, long_window, ms64.event_time)
    long_binned.to_csv(tables_dir / "ridgecrest_window_long_64_to_71_binned.csv", index=False)
    long_bin_summary.to_csv(tables_dir / "time_bin_counts_64_to_71.csv", index=False)
    plot_time_colored_epicenters(
        long_binned,
        long_bin_summary,
        ms64,
        ms71,
        long_window,
        figures_dir / "time_colored_epicenters_64_to_71.png",
        color_metadata_rows,
    )

    plot_meta_df = pd.DataFrame(color_metadata_rows)
    require_columns(
        plot_meta_df,
        ["window_name", "time_bin_index", "time_bin_label", "time_bin_start_min", "time_bin_end_min", "rgba"],
        "plotting metadata table",
    )
    plot_meta_df.to_csv(tables_dir / "plotting_metadata_time_bin_colors.csv", index=False)

    short_spatial_summary = add_mainshock_distance_metrics(
        compute_pca_spatial_summary(short_binned, short_bin_summary), projection_meta
    )
    long_spatial_summary = add_mainshock_distance_metrics(
        compute_pca_spatial_summary(long_binned, long_bin_summary), projection_meta
    )
    spatial_summary = pd.concat([short_spatial_summary, long_spatial_summary], ignore_index=True)
    require_columns(
        spatial_summary,
        [
            "window_name",
            "time_bin_index",
            "time_bin_label",
            "event_count",
            "centroid_x_km",
            "centroid_y_km",
            "centroid_dist_to_mw64_km",
            "centroid_dist_to_mw71_km",
        ],
        "combined time bin spatial summary",
    )
    spatial_summary.to_csv(tables_dir / "time_bin_spatial_summary.csv", index=False)

    write_validation_summary(
        catalog_enriched,
        short_df,
        long_df,
        projection_meta,
        ms64,
        ms71,
        tables_dir / "validation_summary.csv",
    )

    projection_df = pd.DataFrame([projection_meta])
    projection_df.to_csv(tables_dir / "projection_metadata.csv", index=False)

    log("All outputs written successfully")
    log(f"Tables directory: {tables_dir}")
    log(f"Figures directory: {figures_dir}")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print(traceback.format_exc(), flush=True)
        sys.exit(1)
