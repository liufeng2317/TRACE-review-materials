from __future__ import annotations

import json
import math
import os
import shutil
import sys
import traceback
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

BASE_DIR = Path(
    "<REPO_ROOT>/examples/ridgecrest/catalog_analysis/run/01_1_trigger_spatiotemporal_Q1-v1/exp_run"
)
SCRIPT_PATH = BASE_DIR / "scripts" / "03_visualization_and_evidence.py"
OUTPUT_DIR = BASE_DIR / "outputs" / "03_visualization_and_evidence"
INPUT_QC_DIR = BASE_DIR / "outputs" / "01_catalog_windows_qc"
INPUT_METRICS_DIR = BASE_DIR / "outputs" / "02_spatiotemporal_metrics"

CATALOG_CLEAN_PATH = INPUT_QC_DIR / "ridgecrest_catalog_clean.csv"
MAINSHOCK_PATH = INPUT_QC_DIR / "mainshock_reference_verified.csv"
WHOLE_WINDOWS_PATH = INPUT_QC_DIR / "time_windows_whole_sequence.csv"
POST64_WINDOWS_PATH = INPUT_QC_DIR / "time_windows_post64_hourly.csv"
COMPARISON_INTERVALS_PATH = INPUT_QC_DIR / "time_windows_comparison_intervals.csv"
EXTENT_PATH = INPUT_QC_DIR / "analysis_extent.json"

WHOLE_METRICS_PATH = INPUT_METRICS_DIR / "window_metrics_whole_sequence.csv"
POST64_METRICS_PATH = INPUT_METRICS_DIR / "window_metrics_post64_hourly.csv"
WHOLE_CLUSTERS_PATH = INPUT_METRICS_DIR / "window_cluster_metrics_whole_sequence.csv"
POST64_CLUSTERS_PATH = INPUT_METRICS_DIR / "window_cluster_metrics_post64_hourly.csv"
COMPARISON_64_PATH = INPUT_METRICS_DIR / "comparison_metrics_64.csv"
COMPARISON_71_PATH = INPUT_METRICS_DIR / "comparison_metrics_71.csv"
MIGRATION_64_TO_71_PATH = INPUT_METRICS_DIR / "migration_summary_64_to_71.json"
MIGRATION_POST71_PATH = INPUT_METRICS_DIR / "migration_summary_post71.json"

MAX_CORES = min(64, os.cpu_count() or 1)
PAGE_RENDER_WORKERS = max(1, min(MAX_CORES, 8))
FIG_DPI = 180
PANELS_PER_PAGE = 8
GRID_ROWS = 2
GRID_COLS = 4
CATALOG_READ_COLUMNS = [
    "event_time",
    "latitude",
    "longitude",
    "depth_km",
    "magnitude",
    "x_km_local",
    "y_km_local",
    "sequence_segment_label",
]

STYLE = {
    "prior_color": "silver",
    "prior_alpha": 0.26,
    "prior_size": 4,
    "current_color": "#d81b60",
    "current_alpha": 0.88,
    "current_size": 8,
    "before_color": "#1f77b4",
    "before_alpha": 0.45,
    "before_size": 5,
    "after_color": "#d62728",
    "after_alpha": 0.45,
    "after_size": 5,
    "mainshock64_color": "#222222",
    "mainshock71_color": "#ffbf00",
    "mainshock_marker": "*",
    "mainshock_size": 140,
    "mainshock_edgecolor": "white",
    "mainshock_linewidth": 0.6,
}

STALE_PATHS = [
    OUTPUT_DIR / "figures_whole_sequence_2h",
    OUTPUT_DIR / "figures_whole_sequence_6h",
    OUTPUT_DIR / "figures_post64_hourly",
    OUTPUT_DIR / "compare_before_after_mw64.png",
    OUTPUT_DIR / "compare_before_after_mw71.png",
    OUTPUT_DIR / "whole_sequence_2h_page_index.csv",
    OUTPUT_DIR / "whole_sequence_6h_page_index.csv",
    OUTPUT_DIR / "post64_hourly_page_index.csv",
    OUTPUT_DIR / "whole_sequence_render_log.json",
    OUTPUT_DIR / "post64_hourly_render_log.json",
    OUTPUT_DIR / "post64_branching_flags.csv",
    OUTPUT_DIR / "ridgecrest_triggering_evidence_summary.json",
    OUTPUT_DIR / "ridgecrest_interval_interpretation_table.csv",
    OUTPUT_DIR / "figure_window_cross_reference.csv",
    OUTPUT_DIR / "before_after_change_metrics_64.json",
    OUTPUT_DIR / "before_after_change_metrics_71.json",
    OUTPUT_DIR / "output_manifest.csv",
    OUTPUT_DIR / "validation_report.json",
    OUTPUT_DIR / "run_log.txt",
]

RUN_LOG_MESSAGES: list[str] = []


@dataclass(frozen=True)
class MainshockRef:
    label: str
    time: pd.Timestamp
    longitude: float
    latitude: float


def log(message: str) -> None:
    line = str(message)
    RUN_LOG_MESSAGES.append(line)
    print(line, flush=True)


def ensure_output_dir() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def clear_stale_outputs() -> None:
    for path in STALE_PATHS:
        if path.is_dir():
            shutil.rmtree(path)
            log(f"[INFO] Removed stale directory: {path}")
        elif path.exists():
            path.unlink()
            log(f"[INFO] Removed stale file: {path}")


def read_json(path: Path) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _json_ready(value: Any) -> Any:
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(k): _json_ready(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_ready(v) for v in value]
    if isinstance(value, np.ndarray):
        return [_json_ready(v) for v in value.tolist()]
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return None if np.isnan(value) else float(value)
    if isinstance(value, float):
        return None if math.isnan(value) else value
    if pd.isna(value):
        return None
    return value


def write_json(obj: dict[str, Any], path: Path) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(_json_ready(obj), f, indent=2, sort_keys=True)
    log(f"[INFO] Wrote JSON: {path}")


def write_csv(df: pd.DataFrame, path: Path) -> None:
    out = df.copy()
    for col in out.columns:
        if pd.api.types.is_datetime64_any_dtype(out[col]):
            out[col] = out[col].dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    out.to_csv(path, index=False)
    log(f"[INFO] Wrote CSV: {path}")


def write_run_log() -> None:
    run_log_path = OUTPUT_DIR / "run_log.txt"
    with open(run_log_path, "w", encoding="utf-8") as f:
        for line in RUN_LOG_MESSAGES:
            f.write(line + "\n")


def parse_time_columns(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    out = df.copy()
    for col in cols:
        out[col] = pd.to_datetime(out[col], utc=True, errors="raise")
    return out


def assert_columns(df: pd.DataFrame, required: list[str], name: str) -> None:
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"{name} missing required columns: {missing}")


def read_catalog() -> pd.DataFrame:
    log(f"[INFO] Reading cleaned catalog: {CATALOG_CLEAN_PATH}")
    df = pd.read_csv(CATALOG_CLEAN_PATH, usecols=CATALOG_READ_COLUMNS)
    assert_columns(df, CATALOG_READ_COLUMNS, "catalog")
    df = parse_time_columns(df, ["event_time"])
    for col in ["latitude", "longitude", "depth_km", "magnitude", "x_km_local", "y_km_local"]:
        df[col] = pd.to_numeric(df[col], errors="raise")
    df = df.sort_values("event_time", kind="mergesort").reset_index(drop=True)
    df["event_id"] = np.arange(len(df), dtype=np.int64)
    return df


def read_mainshocks() -> dict[str, MainshockRef]:
    log(f"[INFO] Reading mainshock reference: {MAINSHOCK_PATH}")
    df = pd.read_csv(MAINSHOCK_PATH)
    assert_columns(df, ["mainshock_label", "event_time", "latitude", "longitude", "magnitude"], "mainshock_reference")
    df = parse_time_columns(df, ["event_time"])
    refs: dict[str, MainshockRef] = {}
    for _, row in df.iterrows():
        refs[str(row["mainshock_label"])] = MainshockRef(
            label=str(row["mainshock_label"]),
            time=pd.Timestamp(row["event_time"]),
            longitude=float(row["longitude"]),
            latitude=float(row["latitude"]),
        )
    if set(refs.keys()) != {"mainshock64", "mainshock71"}:
        raise ValueError(f"Unexpected mainshock labels: {sorted(refs.keys())}")
    return refs


def read_windows(path: Path, required: list[str], name: str) -> pd.DataFrame:
    log(f"[INFO] Reading windows: {path}")
    df = pd.read_csv(path)
    assert_columns(df, required, name)
    df = parse_time_columns(df, ["start_time", "end_time"])
    return df.sort_values([c for c in ["window_family", "stage_label", "window_index", "global_window_id"] if c in df.columns], kind="mergesort").reset_index(drop=True)


def read_metrics(path: Path, name: str) -> pd.DataFrame:
    log(f"[INFO] Reading metrics: {path}")
    df = pd.read_csv(path)
    time_cols = [c for c in ["start_time", "end_time", "window_mid_time"] if c in df.columns]
    if time_cols:
        df = parse_time_columns(df, time_cols)
    return df


def assert_page_merge_columns(page_table: pd.DataFrame, metrics_df: pd.DataFrame, family_name: str) -> None:
    assert_columns(page_table, ["window_label", "window_index", "start_time", "end_time"], f"{family_name}_page_table")
    assert_columns(metrics_df, ["window_label", "n_events"], f"{family_name}_metrics_df")


def prepare_page_table(windows_df: pd.DataFrame, family_name: str, stage_label: str, figure_dir_name: str, file_prefix: str) -> pd.DataFrame:
    subset = windows_df.loc[windows_df["stage_label"] == stage_label].copy().reset_index(drop=True)
    if subset.empty:
        raise ValueError(f"No windows found for stage_label={stage_label}")
    subset["family_name"] = family_name
    subset["figure_dir_name"] = figure_dir_name
    subset["file_prefix"] = file_prefix
    subset["page_number"] = (np.arange(len(subset)) // PANELS_PER_PAGE) + 1
    subset["panel_position"] = (np.arange(len(subset)) % PANELS_PER_PAGE) + 1
    subset["figure_filename"] = subset["page_number"].map(lambda n: f"{file_prefix}_page_{int(n):03d}.png")
    return subset


def build_cross_reference(page_tables: list[pd.DataFrame]) -> pd.DataFrame:
    frames = []
    for table in page_tables:
        out = table[[
            "family_name",
            "figure_dir_name",
            "file_prefix",
            "page_number",
            "panel_position",
            "figure_filename",
            "window_family",
            "stage_label",
            "global_window_id",
            "window_index",
            "window_label",
            "start_time",
            "end_time",
            "duration_hours",
        ]].copy()
        frames.append(out)
    merged = pd.concat(frames, ignore_index=True)
    merged = merged.sort_values(["figure_dir_name", "page_number", "panel_position"], kind="mergesort").reset_index(drop=True)
    return merged


def _render_page_task(task: dict[str, Any]) -> dict[str, Any]:
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import pandas as pd

    catalog = pd.read_csv(task["catalog_path"], usecols=["event_time", "latitude", "longitude"])
    catalog["event_time"] = pd.to_datetime(catalog["event_time"], utc=True, errors="raise")
    catalog = catalog.sort_values("event_time", kind="mergesort").reset_index(drop=True)
    page_df = pd.DataFrame(task["page_rows"])
    page_df["start_time"] = pd.to_datetime(page_df["start_time"], utc=True, errors="raise")
    page_df["end_time"] = pd.to_datetime(page_df["end_time"], utc=True, errors="raise")

    extent = task["extent"]
    style = task["style"]
    mainshocks = task["mainshocks"]
    xlim = (extent["longitude_min"], extent["longitude_max"])
    ylim = (extent["latitude_min"], extent["latitude_max"])

    fig, axes = plt.subplots(GRID_ROWS, GRID_COLS, figsize=(16, 9), sharex=True, sharey=True)
    axes = np.array(axes).reshape(-1)

    for ax in axes:
        ax.set_xlim(*xlim)
        ax.set_ylim(*ylim)
        ax.grid(True, color="#dddddd", linewidth=0.4, alpha=0.5)
        ax.tick_params(labelsize=8)

    for i, (_, row) in enumerate(page_df.iterrows()):
        ax = axes[i]
        start = pd.Timestamp(row["start_time"])
        end = pd.Timestamp(row["end_time"])
        prior = catalog.loc[catalog["event_time"] < start]
        current = catalog.loc[(catalog["event_time"] >= start) & (catalog["event_time"] < end)]

        if len(prior) > 0:
            ax.scatter(
                prior["longitude"],
                prior["latitude"],
                s=style["prior_size"],
                c=style["prior_color"],
                alpha=style["prior_alpha"],
                linewidths=0,
                rasterized=False,
            )
        if len(current) > 0:
            ax.scatter(
                current["longitude"],
                current["latitude"],
                s=style["current_size"],
                c=style["current_color"],
                alpha=style["current_alpha"],
                linewidths=0,
                rasterized=False,
            )

        if task["overlay_mainshock64_always"] or start >= pd.Timestamp(mainshocks["mainshock64"]["time"]):
            ms = mainshocks["mainshock64"]
            ax.scatter(
                [ms["longitude"]],
                [ms["latitude"]],
                marker=style["mainshock_marker"],
                s=style["mainshock_size"],
                c=style["mainshock64_color"],
                edgecolors=style["mainshock_edgecolor"],
                linewidths=style["mainshock_linewidth"],
                zorder=5,
            )
        if task["overlay_mainshock71_when_occurred"] and start >= pd.Timestamp(mainshocks["mainshock71"]["time"]):
            ms = mainshocks["mainshock71"]
            ax.scatter(
                [ms["longitude"]],
                [ms["latitude"]],
                marker=style["mainshock_marker"],
                s=style["mainshock_size"],
                c=style["mainshock71_color"],
                edgecolors=style["mainshock_edgecolor"],
                linewidths=style["mainshock_linewidth"],
                zorder=6,
            )

        title = (
            f"{pd.Timestamp(start).strftime('%m-%d %H:%M')} to\n"
            f"{pd.Timestamp(end).strftime('%m-%d %H:%M')} UTC\n"
            f"n={int(row.get('n_events', 0) if pd.notna(row.get('n_events', np.nan)) else 0)}"
        )
        if "window_index" in row:
            title += f" | idx={int(row['window_index'])}"
        ax.set_title(title, fontsize=9)

    for j in range(len(page_df), len(axes)):
        axes[j].axis("off")

    fig.suptitle(task["suptitle"], fontsize=14)
    fig.text(0.5, 0.03, "Longitude", ha="center", fontsize=11)
    fig.text(0.02, 0.5, "Latitude", va="center", rotation="vertical", fontsize=11)
    fig.tight_layout(rect=[0.03, 0.05, 0.995, 0.95])

    output_path = Path(task["output_path"])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=task["dpi"], bbox_inches="tight")
    plt.close(fig)
    return {
        "figure_path": str(output_path),
        "page_number": int(task["page_number"]),
        "n_windows": int(len(page_df)),
        "exists": output_path.exists(),
        "size_bytes": int(output_path.stat().st_size) if output_path.exists() else 0,
    }


def render_paged_family(
    family_table: pd.DataFrame,
    metrics_df: pd.DataFrame,
    extent: dict[str, Any],
    mainshocks: dict[str, MainshockRef],
    figure_dir_name: str,
    file_prefix: str,
    family_title: str,
    overlay_mainshock64_always: bool,
    overlay_mainshock71_when_occurred: bool,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    figure_dir = OUTPUT_DIR / figure_dir_name
    figure_dir.mkdir(parents=True, exist_ok=True)

    assert_page_merge_columns(family_table, metrics_df, figure_dir_name)
    merged = family_table.merge(
        metrics_df[["window_label", "n_events"]],
        on="window_label",
        how="left",
        validate="one_to_one",
    )
    if merged["n_events"].isna().any():
        missing_labels = merged.loc[merged["n_events"].isna(), "window_label"].tolist()[:10]
        raise ValueError(f"Missing n_events after merge for {figure_dir_name}; sample window labels: {missing_labels}")
    tasks = []
    page_index_rows = []
    grouped = list(merged.groupby("page_number", sort=True))
    log(f"[INFO] Rendering family={figure_dir_name} pages={len(grouped)} workers={PAGE_RENDER_WORKERS}")

    mainshock_payload = {
        key: {
            "time": value.time.isoformat(),
            "longitude": value.longitude,
            "latitude": value.latitude,
        }
        for key, value in mainshocks.items()
    }

    for page_number, page_df in grouped:
        filename = str(page_df["figure_filename"].iloc[0])
        output_path = figure_dir / filename
        page_index_rows.append(
            {
                "family_name": str(page_df["family_name"].iloc[0]),
                "figure_dir": str(figure_dir),
                "page_number": int(page_number),
                "figure_filename": filename,
                "figure_path": str(output_path),
                "n_windows_on_page": int(len(page_df)),
                "window_index_min": int(page_df["window_index"].min()),
                "window_index_max": int(page_df["window_index"].max()),
                "start_time_min": page_df["start_time"].min(),
                "end_time_max": page_df["end_time"].max(),
            }
        )
        tasks.append(
            {
                "catalog_path": str(CATALOG_CLEAN_PATH),
                "page_rows": page_df[["window_index", "window_label", "start_time", "end_time", "n_events"]].to_dict(orient="records"),
                "extent": extent,
                "style": STYLE,
                "mainshocks": mainshock_payload,
                "overlay_mainshock64_always": overlay_mainshock64_always,
                "overlay_mainshock71_when_occurred": overlay_mainshock71_when_occurred,
                "suptitle": f"{family_title} | Page {int(page_number):03d}",
                "output_path": str(output_path),
                "dpi": FIG_DPI,
                "page_number": int(page_number),
            }
        )

    render_results: list[dict[str, Any]] = []
    with ProcessPoolExecutor(max_workers=PAGE_RENDER_WORKERS) as executor:
        future_map = {executor.submit(_render_page_task, task): task for task in tasks}
        for i, future in enumerate(as_completed(future_map), start=1):
            result = future.result()
            render_results.append(result)
            log(
                f"[INFO] Rendered {figure_dir_name} page {result['page_number']:03d}/"
                f"{len(tasks):03d}: {result['figure_path']} size={result['size_bytes']}"
            )

    page_index_df = pd.DataFrame(page_index_rows).sort_values("page_number", kind="mergesort").reset_index(drop=True)
    render_results = sorted(render_results, key=lambda x: x["page_number"])
    render_log = {
        "family_name": figure_dir_name,
        "figure_dir": str(figure_dir),
        "pages_expected": int(len(tasks)),
        "pages_rendered": int(len(render_results)),
        "workers_used": int(PAGE_RENDER_WORKERS),
        "results": render_results,
    }
    return page_index_df, render_log


def build_branching_flags(post64_metrics: pd.DataFrame, post64_clusters: pd.DataFrame) -> pd.DataFrame:
    merged = post64_metrics.merge(
        post64_clusters[["window_label", "n_clusters", "dominant_cluster_fraction", "clustered_event_fraction"]],
        on="window_label",
        how="left",
        validate="one_to_one",
    )
    merged["branching_class"] = np.select(
        [
            merged["n_events"].fillna(0) == 0,
            merged["n_clusters"].fillna(0) >= 2,
            (merged["n_clusters"].fillna(0) == 1) & (merged["dominant_cluster_fraction"].fillna(0) >= 0.6),
        ],
        ["no_events", "multi_cluster", "single_dominant_cluster"],
        default="diffuse_or_weak_cluster",
    )
    merged["orientation_class"] = np.select(
        [
            merged["principal_axis_azimuth_deg"].isna(),
            merged["principal_axis_azimuth_change_deg"].fillna(0) < 20,
            merged["principal_axis_azimuth_change_deg"].fillna(0) < 45,
        ],
        ["insufficient", "stable", "moderate_change"],
        default="strong_change",
    )
    cols = [
        "window_label",
        "window_index",
        "start_time",
        "end_time",
        "n_events",
        "n_clusters",
        "dominant_cluster_fraction",
        "clustered_event_fraction",
        "principal_axis_azimuth_deg",
        "principal_axis_azimuth_change_deg",
        "centroid_step_distance_km",
        "centroid_step_azimuth_deg",
        "branching_class",
        "orientation_class",
    ]
    return merged[cols].copy()


def _safe_float(value: Any) -> float | None:
    if value is None or (isinstance(value, float) and math.isnan(value)) or pd.isna(value):
        return None
    return float(value)


def orientation_state_from_class(label: Any) -> str:
    if label in [None, "insufficient"]:
        return "poorly_constrained"
    if label == "stable":
        return "stable"
    if label in ["moderate_change", "strong_change"]:
        return "rotating"
    return "poorly_constrained"


def motion_state_from_metrics(net_shift_km: Any, cumulative_km: Any) -> str:
    net_shift = _safe_float(net_shift_km)
    cumulative = _safe_float(cumulative_km)
    if net_shift is None:
        return "weak"
    if cumulative is not None and cumulative > max(10.0, 2.5 * net_shift):
        return "stepwise"
    if net_shift >= 5.0:
        return "systematic"
    return "weak"


def cluster_state_from_fraction(multi_cluster_fraction: Any) -> str:
    value = _safe_float(multi_cluster_fraction)
    if value is None:
        return "ambiguous"
    if value >= 0.4:
        return "multiple_simultaneous_clusters"
    if value >= 0.15:
        return "mixed_single_and_multiple_clusters"
    return "one_dominant_cluster_or_diffuse_single_zone"


def direction_label(azimuth_deg: Any) -> str:
    az = _safe_float(azimuth_deg)
    if az is None:
        return "ambiguous"
    directions = [
        (22.5, "N"),
        (67.5, "NE"),
        (112.5, "E"),
        (157.5, "SE"),
        (202.5, "S"),
        (247.5, "SW"),
        (292.5, "W"),
        (337.5, "NW"),
        (360.0, "N"),
    ]
    for threshold, label in directions:
        if az < threshold:
            return label
    return "N"


def classify_target_trend(slope_km_per_hour: Any) -> str:
    slope = _safe_float(slope_km_per_hour)
    if slope is None:
        return "ambiguous"
    if slope < -0.05:
        return "approaching_target_zone"
    if slope > 0.05:
        return "moving_away_from_target_zone"
    return "approximately_static_distance"


def new_zone_flag(change_distance_km: Any) -> str:
    dist = _safe_float(change_distance_km)
    if dist is None:
        return "ambiguous"
    if dist >= 5.0:
        return "new_zone_likely"
    return "no_clear_new_zone"


def make_interval_record(
    interval_name: str,
    orientation_change_class: Any,
    net_shift_azimuth_deg: Any,
    net_shift_distance_km: Any,
    cumulative_distance_km: Any,
    multi_cluster_fraction: Any,
    target_trend: str,
    new_zone: str,
    page_refs: list[str],
    window_start: Any,
    window_end: Any,
    note: str,
) -> dict[str, Any]:
    return {
        "interval_name": interval_name,
        "dominant_orientation_state": orientation_state_from_class(orientation_change_class),
        "net_migration_direction_azimuth_deg": _safe_float(net_shift_azimuth_deg),
        "net_migration_direction_cardinal": direction_label(net_shift_azimuth_deg),
        "net_centroid_shift_distance_km": _safe_float(net_shift_distance_km),
        "centroid_motion_state": motion_state_from_metrics(net_shift_distance_km, cumulative_distance_km),
        "cluster_organization_state": cluster_state_from_fraction(multi_cluster_fraction),
        "distance_to_target_behavior": target_trend,
        "new_activation_zone_flag": new_zone,
        "supporting_figure_pages": json.dumps(page_refs),
        "supporting_window_start": window_start,
        "supporting_window_end": window_end,
        "observational_note": note,
    }


def page_refs_for_range(page_index_df: pd.DataFrame, start: pd.Timestamp, end: pd.Timestamp) -> list[str]:
    mask = (page_index_df["end_time_max"] > start) & (page_index_df["start_time_min"] < end)
    subset = page_index_df.loc[mask].sort_values("page_number", kind="mergesort")
    return [f"{Path(row['figure_path']).name}" for _, row in subset.iterrows()]


def build_evidence_outputs(
    migration_64_to_71: dict[str, Any],
    migration_post71: dict[str, Any],
    comparison_64: pd.DataFrame,
    comparison_71: pd.DataFrame,
    comparison_change64: dict[str, Any],
    comparison_change71: dict[str, Any],
    whole_2h_index: pd.DataFrame,
    whole_6h_index: pd.DataFrame,
    post64_index: pd.DataFrame,
    ms64: MainshockRef,
    ms71: MainshockRef,
) -> tuple[dict[str, Any], pd.DataFrame, dict[str, Any], dict[str, Any]]:
    interval_rows = []

    immediate_post64_end = ms64.time + pd.Timedelta(hours=8)
    immediate_post71_end = ms71.time + pd.Timedelta(days=2)

    interval_rows.append(
        make_interval_record(
            interval_name="immediate_post_mainshock64",
            orientation_change_class=migration_64_to_71.get("orientation_change_class"),
            net_shift_azimuth_deg=migration_64_to_71.get("net_centroid_shift_azimuth_deg"),
            net_shift_distance_km=migration_64_to_71.get("net_centroid_shift_distance_km"),
            cumulative_distance_km=migration_64_to_71.get("cumulative_centroid_distance_km"),
            multi_cluster_fraction=migration_64_to_71.get("multi_cluster_window_fraction"),
            target_trend=classify_target_trend(migration_64_to_71.get("distance_to_target_trend_slope_km_per_hour")),
            new_zone=new_zone_flag(comparison_change64.get("hotspot_shift_distance_km")),
            page_refs=page_refs_for_range(post64_index, ms64.time, immediate_post64_end),
            window_start=ms64.time,
            window_end=immediate_post64_end,
            note="Hour-by-hour post-Mw 6.4 seismicity used to assess branching, local migration, and early organization.",
        )
    )
    interval_rows.append(
        make_interval_record(
            interval_name="inter_mainshock_64_to_71",
            orientation_change_class=migration_64_to_71.get("orientation_change_class"),
            net_shift_azimuth_deg=migration_64_to_71.get("net_centroid_shift_azimuth_deg"),
            net_shift_distance_km=migration_64_to_71.get("net_centroid_shift_distance_km"),
            cumulative_distance_km=migration_64_to_71.get("cumulative_centroid_distance_km"),
            multi_cluster_fraction=migration_64_to_71.get("multi_cluster_window_fraction"),
            target_trend=classify_target_trend(migration_64_to_71.get("distance_to_target_trend_slope_km_per_hour")),
            new_zone=new_zone_flag(comparison_change64.get("centroid_shift_distance_km")),
            page_refs=page_refs_for_range(post64_index, ms64.time, ms71.time),
            window_start=ms64.time,
            window_end=ms71.time,
            note="Inter-mainshock interval highlights whether activity migrates toward the later Mw 7.1 zone or activates multiple branches.",
        )
    )
    interval_rows.append(
        make_interval_record(
            interval_name="immediate_post_mainshock71",
            orientation_change_class=migration_post71.get("orientation_change_class"),
            net_shift_azimuth_deg=migration_post71.get("net_centroid_shift_azimuth_deg"),
            net_shift_distance_km=migration_post71.get("net_centroid_shift_distance_km"),
            cumulative_distance_km=migration_post71.get("cumulative_centroid_distance_km"),
            multi_cluster_fraction=migration_post71.get("multi_cluster_window_fraction"),
            target_trend=classify_target_trend(migration_post71.get("distance_to_target_trend_slope_km_per_hour")),
            new_zone=new_zone_flag(comparison_change71.get("hotspot_shift_distance_km")),
            page_refs=page_refs_for_range(whole_2h_index, ms71.time, ms71.time + pd.Timedelta(days=1)) + page_refs_for_range(whole_6h_index, ms71.time + pd.Timedelta(days=1), immediate_post71_end),
            window_start=ms71.time,
            window_end=immediate_post71_end,
            note="Post-Mw 7.1 interval combines late 2-hour pages and early 6-hour pages to assess directional reorganization and new activated zones.",
        )
    )
    interval_rows.append(
        make_interval_record(
            interval_name="before_after_mainshock64_comparison",
            orientation_change_class=(
                "insufficient" if comparison_change64.get("principal_axis_orientation_change_deg") is None else (
                    "stable" if comparison_change64["principal_axis_orientation_change_deg"] < 20 else (
                        "moderate_change" if comparison_change64["principal_axis_orientation_change_deg"] < 45 else "strong_change"
                    )
                )
            ),
            net_shift_azimuth_deg=comparison_change64.get("centroid_shift_azimuth_deg"),
            net_shift_distance_km=comparison_change64.get("centroid_shift_distance_km"),
            cumulative_distance_km=comparison_change64.get("centroid_shift_distance_km"),
            multi_cluster_fraction=None,
            target_trend="not_applicable_interval_overlay",
            new_zone=new_zone_flag(comparison_change64.get("hotspot_shift_distance_km")),
            page_refs=["compare_before_after_mw64.png"],
            window_start=ms64.time - pd.Timedelta(hours=16.619847),
            window_end=ms71.time,
            note="Overlay comparison isolates reorganization across Mw 6.4 using full before and after distributions.",
        )
    )
    interval_rows.append(
        make_interval_record(
            interval_name="before_after_mainshock71_comparison",
            orientation_change_class=(
                "insufficient" if comparison_change71.get("principal_axis_orientation_change_deg") is None else (
                    "stable" if comparison_change71["principal_axis_orientation_change_deg"] < 20 else (
                        "moderate_change" if comparison_change71["principal_axis_orientation_change_deg"] < 45 else "strong_change"
                    )
                )
            ),
            net_shift_azimuth_deg=comparison_change71.get("centroid_shift_azimuth_deg"),
            net_shift_distance_km=comparison_change71.get("centroid_shift_distance_km"),
            cumulative_distance_km=comparison_change71.get("centroid_shift_distance_km"),
            multi_cluster_fraction=None,
            target_trend="not_applicable_interval_overlay",
            new_zone=new_zone_flag(comparison_change71.get("hotspot_shift_distance_km")),
            page_refs=["compare_before_after_mw71.png"],
            window_start=ms64.time,
            window_end=ms71.time + pd.Timedelta(days=2),
            note="Overlay comparison isolates reorganization across Mw 7.1 using inter-mainshock and post-mainshock distributions.",
        )
    )

    interval_df = pd.DataFrame(interval_rows)

    evidence_summary = {
        "question_focus": "Ridgecrest spatiotemporal evolution with emphasis on transition from Mw 6.4 to Mw 7.1",
        "mainshock64_time": ms64.time.isoformat(),
        "mainshock71_time": ms71.time.isoformat(),
        "immediate_post64_summary": migration_64_to_71,
        "post71_summary": migration_post71,
        "comparison64_change": comparison_change64,
        "comparison71_change": comparison_change71,
        "key_observational_flags": {
            "post64_target_trend": classify_target_trend(migration_64_to_71.get("distance_to_target_trend_slope_km_per_hour")),
            "post64_cluster_mode": cluster_state_from_fraction(migration_64_to_71.get("multi_cluster_window_fraction")),
            "post71_cluster_mode": cluster_state_from_fraction(migration_post71.get("multi_cluster_window_fraction")),
            "post64_motion_state": motion_state_from_metrics(
                migration_64_to_71.get("net_centroid_shift_distance_km"),
                migration_64_to_71.get("cumulative_centroid_distance_km"),
            ),
            "post71_motion_state": motion_state_from_metrics(
                migration_post71.get("net_centroid_shift_distance_km"),
                migration_post71.get("cumulative_centroid_distance_km"),
            ),
            "direction_change_across_mw64": (
                "poorly_constrained"
                if comparison_change64.get("principal_axis_orientation_change_deg") is None or pd.isna(comparison_change64.get("principal_axis_orientation_change_deg"))
                else (
                    "stable"
                    if float(comparison_change64.get("principal_axis_orientation_change_deg")) < 20.0
                    else "rotating"
                )
            ),
            "direction_change_across_mw71": (
                "poorly_constrained"
                if comparison_change71.get("principal_axis_orientation_change_deg") is None or pd.isna(comparison_change71.get("principal_axis_orientation_change_deg"))
                else (
                    "stable"
                    if float(comparison_change71.get("principal_axis_orientation_change_deg")) < 20.0
                    else "rotating"
                )
            ),
            "new_zone_after_mw64": new_zone_flag(comparison_change64.get("hotspot_shift_distance_km")),
            "new_zone_after_mw71": new_zone_flag(comparison_change71.get("hotspot_shift_distance_km")),
        },
        "supporting_figures": {
            "whole_sequence_2h_pages": whole_2h_index["figure_filename"].tolist(),
            "whole_sequence_6h_pages": whole_6h_index["figure_filename"].tolist(),
            "post64_hourly_pages": post64_index["figure_filename"].tolist(),
            "comparison_figures": ["compare_before_after_mw64.png", "compare_before_after_mw71.png"],
        },
        "interpretation_table_rows": int(len(interval_df)),
        "caution": "All evidence products are descriptive observations from relocated catalog spatiotemporal patterns and do not by themselves prove a physical triggering mechanism.",
    }

    before_after64_json = {
        "comparison_label": "mw64",
        "before_after_metrics_rows": comparison_64.to_dict(orient="records"),
        "change_summary": comparison_change64,
        "comparison_figure": "compare_before_after_mw64.png",
    }
    before_after71_json = {
        "comparison_label": "mw71",
        "before_after_metrics_rows": comparison_71.to_dict(orient="records"),
        "change_summary": comparison_change71,
        "comparison_figure": "compare_before_after_mw71.png",
    }
    return evidence_summary, interval_df, before_after64_json, before_after71_json


def render_comparison_figure(
    catalog: pd.DataFrame,
    intervals_df: pd.DataFrame,
    mainshocks: dict[str, MainshockRef],
    extent: dict[str, Any],
    comparison_label: str,
    title: str,
    output_path: Path,
) -> dict[str, Any]:
    subset_intervals = intervals_df.loc[intervals_df["comparison_label"] == comparison_label].copy()
    if len(subset_intervals) != 2:
        raise ValueError(f"Expected 2 intervals for comparison {comparison_label}, found {len(subset_intervals)}")
    before_row = subset_intervals.loc[subset_intervals["interval_role"] == "before"].iloc[0]
    after_row = subset_intervals.loc[subset_intervals["interval_role"] == "after"].iloc[0]

    before = catalog.loc[(catalog["event_time"] >= before_row["start_time"]) & (catalog["event_time"] < before_row["end_time"])]
    after = catalog.loc[(catalog["event_time"] >= after_row["start_time"]) & (catalog["event_time"] < after_row["end_time"])]

    fig, ax = plt.subplots(figsize=(9, 8))
    ax.scatter(
        before["longitude"], before["latitude"], s=STYLE["before_size"], c=STYLE["before_color"], alpha=STYLE["before_alpha"], linewidths=0, label="Before"
    )
    ax.scatter(
        after["longitude"], after["latitude"], s=STYLE["after_size"], c=STYLE["after_color"], alpha=STYLE["after_alpha"], linewidths=0, label="After"
    )

    ms64 = mainshocks["mainshock64"]
    ms71 = mainshocks["mainshock71"]
    ax.scatter([ms64.longitude], [ms64.latitude], marker=STYLE["mainshock_marker"], s=STYLE["mainshock_size"], c=STYLE["mainshock64_color"], edgecolors=STYLE["mainshock_edgecolor"], linewidths=STYLE["mainshock_linewidth"], label="Mw 6.4")
    ax.scatter([ms71.longitude], [ms71.latitude], marker=STYLE["mainshock_marker"], s=STYLE["mainshock_size"], c=STYLE["mainshock71_color"], edgecolors=STYLE["mainshock_edgecolor"], linewidths=STYLE["mainshock_linewidth"], label="Mw 7.1")

    ax.set_xlim(extent["longitude_min"], extent["longitude_max"])
    ax.set_ylim(extent["latitude_min"], extent["latitude_max"])
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.grid(True, color="#dddddd", linewidth=0.4, alpha=0.5)
    ax.legend(loc="upper right", fontsize=9, frameon=True)
    ax.set_title(title, fontsize=13)

    before_text = f"Before: {pd.Timestamp(before_row['start_time']).strftime('%Y-%m-%d %H:%M')} to {pd.Timestamp(before_row['end_time']).strftime('%Y-%m-%d %H:%M')} UTC\nN={len(before)}"
    after_text = f"After: {pd.Timestamp(after_row['start_time']).strftime('%Y-%m-%d %H:%M')} to {pd.Timestamp(after_row['end_time']).strftime('%Y-%m-%d %H:%M')} UTC\nN={len(after)}"
    ax.text(0.02, 0.02, before_text + "\n" + after_text, transform=ax.transAxes, fontsize=9, va="bottom", ha="left", bbox=dict(facecolor="white", alpha=0.75, edgecolor="none"))

    fig.tight_layout()
    fig.savefig(output_path, dpi=FIG_DPI, bbox_inches="tight")
    plt.close(fig)
    log(f"[INFO] Wrote comparison figure: {output_path}")
    return {
        "figure_path": str(output_path),
        "comparison_label": comparison_label,
        "before_event_count": int(len(before)),
        "after_event_count": int(len(after)),
        "size_bytes": int(output_path.stat().st_size),
    }


def build_manifest() -> pd.DataFrame:
    rows = []
    for path in sorted(OUTPUT_DIR.rglob("*")):
        if path.is_file():
            rows.append(
                {
                    "relative_path": str(path.relative_to(OUTPUT_DIR)),
                    "absolute_path": str(path),
                    "size_bytes": int(path.stat().st_size),
                    "suffix": path.suffix.lower(),
                }
            )
    return pd.DataFrame(rows)


def validate_outputs(
    whole_2h_table: pd.DataFrame,
    whole_6h_table: pd.DataFrame,
    post64_table: pd.DataFrame,
    cross_ref: pd.DataFrame,
    page_index_2h: pd.DataFrame,
    page_index_6h: pd.DataFrame,
    page_index_post64: pd.DataFrame,
) -> dict[str, Any]:
    expected_2h_pages = int(math.ceil(len(whole_2h_table) / PANELS_PER_PAGE))
    expected_6h_pages = int(math.ceil(len(whole_6h_table) / PANELS_PER_PAGE))
    expected_post64_pages = int(math.ceil(len(post64_table) / PANELS_PER_PAGE))

    def _check_pages(page_index_df: pd.DataFrame, expected: int, label: str) -> dict[str, Any]:
        actual = int(len(page_index_df))
        all_exist = True
        nonempty = True
        for path in page_index_df["figure_path"].tolist():
            p = Path(path)
            if not p.exists():
                all_exist = False
                nonempty = False
            elif p.stat().st_size <= 0:
                nonempty = False
        return {
            "label": label,
            "pages_expected": expected,
            "pages_actual": actual,
            "all_pages_exist": all_exist,
            "all_pages_nonempty": nonempty,
            "page_count_match": actual == expected,
        }

    checks = [
        _check_pages(page_index_2h, expected_2h_pages, "whole_sequence_2h"),
        _check_pages(page_index_6h, expected_6h_pages, "whole_sequence_6h"),
        _check_pages(page_index_post64, expected_post64_pages, "post64_hourly"),
    ]

    comparison_files = [OUTPUT_DIR / "compare_before_after_mw64.png", OUTPUT_DIR / "compare_before_after_mw71.png"]
    comparison_ok = all(path.exists() and path.stat().st_size > 0 for path in comparison_files)
    cross_ref_ok = len(cross_ref) == (len(whole_2h_table) + len(whole_6h_table) + len(post64_table))

    summary_ok = all(item["page_count_match"] and item["all_pages_exist"] and item["all_pages_nonempty"] for item in checks) and comparison_ok and cross_ref_ok
    return {
        "panels_per_page": PANELS_PER_PAGE,
        "whole_sequence_2h_windows": int(len(whole_2h_table)),
        "whole_sequence_6h_windows": int(len(whole_6h_table)),
        "post64_hourly_windows": int(len(post64_table)),
        "cross_reference_rows": int(len(cross_ref)),
        "cross_reference_expected_rows": int(len(whole_2h_table) + len(whole_6h_table) + len(post64_table)),
        "cross_reference_complete": bool(cross_ref_ok),
        "comparison_figures_ok": bool(comparison_ok),
        "page_family_checks": checks,
        "overall_success": bool(summary_ok),
    }


def main() -> None:
    ensure_output_dir()
    clear_stale_outputs()
    log(f"[INFO] Script path: {SCRIPT_PATH}")
    log(f"[INFO] Output directory: {OUTPUT_DIR}")
    log(f"[INFO] Page rendering workers={PAGE_RENDER_WORKERS}, max_cores={MAX_CORES}")

    extent = read_json(EXTENT_PATH)
    catalog = read_catalog()
    mainshocks = read_mainshocks()
    ms64 = mainshocks["mainshock64"]
    ms71 = mainshocks["mainshock71"]

    whole_windows = read_windows(
        WHOLE_WINDOWS_PATH,
        ["global_window_id", "window_family", "stage_label", "window_index", "window_label", "start_time", "end_time", "duration_hours", "is_terminal_partial_window"],
        "whole_windows",
    )
    post64_windows = read_windows(
        POST64_WINDOWS_PATH,
        ["global_window_id", "window_family", "stage_label", "window_index", "window_label", "start_time", "end_time", "duration_hours", "is_terminal_partial_window"],
        "post64_windows",
    )
    comparison_intervals = read_windows(
        COMPARISON_INTERVALS_PATH,
        ["comparison_label", "interval_role", "start_time", "end_time", "duration_hours"],
        "comparison_intervals",
    )

    whole_metrics = read_metrics(WHOLE_METRICS_PATH, "whole_metrics")
    post64_metrics = read_metrics(POST64_METRICS_PATH, "post64_metrics")
    whole_clusters = read_metrics(WHOLE_CLUSTERS_PATH, "whole_clusters")
    post64_clusters = read_metrics(POST64_CLUSTERS_PATH, "post64_clusters")
    comparison_64 = read_metrics(COMPARISON_64_PATH, "comparison_64")
    comparison_71 = read_metrics(COMPARISON_71_PATH, "comparison_71")
    migration_64_to_71 = read_json(MIGRATION_64_TO_71_PATH)
    migration_post71 = read_json(MIGRATION_POST71_PATH)

    whole_2h_table = prepare_page_table(
        whole_windows,
        family_name="whole_sequence_2h",
        stage_label="2h_mainshock64_to_mainshock71_plus_1day",
        figure_dir_name="figures_whole_sequence_2h",
        file_prefix="whole_sequence_2h",
    )
    whole_6h_table = prepare_page_table(
        whole_windows,
        family_name="whole_sequence_6h",
        stage_label="6h_mainshock71_plus_1day_to_plus_5days",
        figure_dir_name="figures_whole_sequence_6h",
        file_prefix="whole_sequence_6h",
    )
    post64_table = prepare_page_table(
        post64_windows,
        family_name="post64_hourly",
        stage_label="1h_mainshock64_to_mainshock71",
        figure_dir_name="figures_post64_hourly",
        file_prefix="post64_hourly",
    )

    cross_ref = build_cross_reference([whole_2h_table, whole_6h_table, post64_table])
    write_csv(cross_ref, OUTPUT_DIR / "figure_window_cross_reference.csv")

    page_index_2h, render_log_2h = render_paged_family(
        family_table=whole_2h_table,
        metrics_df=whole_metrics,
        extent=extent,
        mainshocks=mainshocks,
        figure_dir_name="figures_whole_sequence_2h",
        file_prefix="whole_sequence_2h",
        family_title="Whole sequence evolution (2-hour windows)",
        overlay_mainshock64_always=False,
        overlay_mainshock71_when_occurred=True,
    )
    page_index_6h, render_log_6h = render_paged_family(
        family_table=whole_6h_table,
        metrics_df=whole_metrics,
        extent=extent,
        mainshocks=mainshocks,
        figure_dir_name="figures_whole_sequence_6h",
        file_prefix="whole_sequence_6h",
        family_title="Whole sequence evolution (6-hour windows after Mw 7.1 +1 day)",
        overlay_mainshock64_always=False,
        overlay_mainshock71_when_occurred=True,
    )
    page_index_post64, render_log_post64 = render_paged_family(
        family_table=post64_table,
        metrics_df=post64_metrics,
        extent=extent,
        mainshocks=mainshocks,
        figure_dir_name="figures_post64_hourly",
        file_prefix="post64_hourly",
        family_title="Post-Mw 6.4 evolution (hourly windows)",
        overlay_mainshock64_always=True,
        overlay_mainshock71_when_occurred=False,
    )

    write_csv(page_index_2h, OUTPUT_DIR / "whole_sequence_2h_page_index.csv")
    write_csv(page_index_6h, OUTPUT_DIR / "whole_sequence_6h_page_index.csv")
    write_csv(page_index_post64, OUTPUT_DIR / "post64_hourly_page_index.csv")
    write_json(render_log_2h, OUTPUT_DIR / "whole_sequence_render_log.json")
    write_json(render_log_post64, OUTPUT_DIR / "post64_hourly_render_log.json")

    branching_flags = build_branching_flags(post64_metrics, post64_clusters)
    write_csv(branching_flags, OUTPUT_DIR / "post64_branching_flags.csv")

    render_comparison_figure(
        catalog=catalog,
        intervals_df=comparison_intervals,
        mainshocks=mainshocks,
        extent=extent,
        comparison_label="mw64",
        title="Spatial distribution before and after Mw 6.4",
        output_path=OUTPUT_DIR / "compare_before_after_mw64.png",
    )
    render_comparison_figure(
        catalog=catalog,
        intervals_df=comparison_intervals,
        mainshocks=mainshocks,
        extent=extent,
        comparison_label="mw71",
        title="Spatial distribution before and after Mw 7.1",
        output_path=OUTPUT_DIR / "compare_before_after_mw71.png",
    )

    comparison_change64 = comparison_64.iloc[0][[
        "comparison_label",
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
    ]].to_dict()
    comparison_change71 = comparison_71.iloc[0][[
        "comparison_label",
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
    ]].to_dict()

    evidence_summary, interpretation_df, before_after64_json, before_after71_json = build_evidence_outputs(
        migration_64_to_71=migration_64_to_71,
        migration_post71=migration_post71,
        comparison_64=comparison_64,
        comparison_71=comparison_71,
        comparison_change64=comparison_change64,
        comparison_change71=comparison_change71,
        whole_2h_index=page_index_2h,
        whole_6h_index=page_index_6h,
        post64_index=page_index_post64,
        ms64=ms64,
        ms71=ms71,
    )
    write_json(evidence_summary, OUTPUT_DIR / "ridgecrest_triggering_evidence_summary.json")
    write_csv(interpretation_df, OUTPUT_DIR / "ridgecrest_interval_interpretation_table.csv")
    write_json(before_after64_json, OUTPUT_DIR / "before_after_change_metrics_64.json")
    write_json(before_after71_json, OUTPUT_DIR / "before_after_change_metrics_71.json")

    manifest_df = build_manifest()
    write_csv(manifest_df, OUTPUT_DIR / "output_manifest.csv")

    validation_report = validate_outputs(
        whole_2h_table=whole_2h_table,
        whole_6h_table=whole_6h_table,
        post64_table=post64_table,
        cross_ref=cross_ref,
        page_index_2h=page_index_2h,
        page_index_6h=page_index_6h,
        page_index_post64=page_index_post64,
    )
    write_json(validation_report, OUTPUT_DIR / "validation_report.json")

    if not validation_report.get("overall_success", False):
        raise RuntimeError(f"Validation failed: {validation_report}")

    log("[INFO] Task 03_visualization_and_evidence completed successfully")
    write_run_log()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print(traceback.format_exc(), flush=True)
        try:
            write_run_log()
        except Exception:
            pass
        sys.exit(1)
