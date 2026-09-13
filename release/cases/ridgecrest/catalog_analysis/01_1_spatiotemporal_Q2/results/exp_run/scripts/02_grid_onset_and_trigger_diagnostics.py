from __future__ import annotations

import math
import os
import shutil
import sys
import traceback
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap


CATALOG_PATH = Path(
    "<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/TRACE_ridgecrest_relocated.csv"
).resolve()
MAINSHOCK_PATH = Path(
    "<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/main_shock_events.csv"
).resolve()
ANCESTOR_OUTPUT_DIR = Path(
    "<REPO_ROOT>/examples/ridgecrest/catalog_analysis/run/01_1_trigger_spatiotemporal_Q2-v1/exp_run/outputs/01_catalog_windows_and_time_colored_maps"
).resolve()
SCRIPT_PATH = Path(__file__).resolve()
OUTPUT_DIR = Path(
    "<REPO_ROOT>/examples/ridgecrest/catalog_analysis/run/01_1_trigger_spatiotemporal_Q2-v1/exp_run/outputs/02_grid_onset_and_trigger_diagnostics"
).resolve()

EXPECTED_COLUMNS = ["event_time", "latitude", "longitude", "depth_km", "magnitude"]
GRID_SIZE_KM = 0.5
TIME_BIN_MINUTES = 30
ONSET_PERSISTENCE_FUTURE_BINS = 3
ONSET_PERSISTENCE_MIN_ACTIVE_BINS = 2
ONSET_WINDOW_HOURS = 2.0
FIG_DPI = 220
MAX_CORES = min(64, max(1, (os.cpu_count() or 1)))
REGION_HALF_WIDTH_KM = 7.5
SEGMENT_COUNT = 6


@dataclass(frozen=True)
class MainshockReference:
    label: str
    event_time: pd.Timestamp
    latitude: float
    longitude: float
    depth_km: float
    magnitude: float
    x_km: float
    y_km: float


@dataclass(frozen=True)
class OnsetRule:
    threshold_count: int
    min_total_events: int
    persistence_future_bins: int
    persistence_min_active_bins: int
    cumulative_window_bins: int
    cumulative_min_count: int


_CELL_COUNTS_ARRAY: np.ndarray | None = None
_ONSET_RULE_GLOBAL: OnsetRule | None = None


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
    if missing:
        raise ValueError(f"{source_name} missing required columns: {missing}")


def load_mainshocks() -> Tuple[MainshockReference, MainshockReference]:
    log(f"Loading mainshock table: {MAINSHOCK_PATH}")
    df = pd.read_csv(MAINSHOCK_PATH)
    validate_schema(df, "main_shock_events")
    df = df[EXPECTED_COLUMNS].copy()
    df["event_time"] = pd.to_datetime(df["event_time"], utc=True)
    for col in ["latitude", "longitude", "depth_km", "magnitude"]:
        df[col] = pd.to_numeric(df[col], errors="raise")

    proj_path = ANCESTOR_OUTPUT_DIR / "tables" / "projection_metadata.csv"
    proj = pd.read_csv(proj_path)
    required_proj = [
        "mainshock64_x_km",
        "mainshock64_y_km",
        "mainshock71_x_km",
        "mainshock71_y_km",
    ]
    missing_proj = [col for col in required_proj if col not in proj.columns]
    if missing_proj:
        raise ValueError(f"Projection metadata missing columns: {missing_proj}")
    proj_row = proj.iloc[0]

    mw64_rows = df[np.isclose(df["magnitude"], 6.4)]
    mw71_rows = df[np.isclose(df["magnitude"], 7.1)]
    if len(mw64_rows) != 1 or len(mw71_rows) != 1:
        raise ValueError("Expected unique Mw 6.4 and Mw 7.1 rows in main_shock_events.csv")

    def row_to_ref(label: str, row: pd.Series, x_col: str, y_col: str) -> MainshockReference:
        return MainshockReference(
            label=label,
            event_time=row["event_time"],
            latitude=float(row["latitude"]),
            longitude=float(row["longitude"]),
            depth_km=float(row["depth_km"]),
            magnitude=float(row["magnitude"]),
            x_km=float(proj_row[x_col]),
            y_km=float(proj_row[y_col]),
        )

    ms64 = row_to_ref("Mainshock64", mw64_rows.iloc[0], "mainshock64_x_km", "mainshock64_y_km")
    ms71 = row_to_ref("Mainshock71", mw71_rows.iloc[0], "mainshock71_x_km", "mainshock71_y_km")
    if not ms71.event_time > ms64.event_time:
        raise ValueError("Mw 7.1 event time must be later than Mw 6.4 event time")
    return ms64, ms71


def load_long_window_catalog() -> pd.DataFrame:
    long_path = ANCESTOR_OUTPUT_DIR / "tables" / "ridgecrest_window_long_64_to_71.csv"
    if long_path.exists():
        log(f"Loading long-window enriched catalog from ancestor output: {long_path}")
        df = pd.read_csv(long_path)
        required = [
            "event_time",
            "latitude",
            "longitude",
            "depth_km",
            "magnitude",
            "event_id",
            "time_rel_hr_from_64",
            "time_rel_min_from_64",
            "x_km",
            "y_km",
        ]
        missing = [col for col in required if col not in df.columns]
        if missing:
            raise ValueError(f"Ancestor long-window table missing required columns: {missing}")
        df["event_time"] = pd.to_datetime(df["event_time"], utc=True, format="mixed")
        numeric_cols = [c for c in required if c != "event_time"]
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors="raise")
        return df.sort_values("event_time").reset_index(drop=True)

    log("Ancestor long-window table not found; rebuilding from raw catalog is not implemented in this task script.")
    raise FileNotFoundError(f"Required ancestor output not found: {long_path}")


def build_time_bins(ms64: MainshockReference, ms71: MainshockReference) -> np.ndarray:
    duration_minutes = (ms71.event_time - ms64.event_time).total_seconds() / 60.0
    if duration_minutes <= 0:
        raise ValueError("Mainshock time interval must be positive.")
    edges = np.arange(0.0, duration_minutes + TIME_BIN_MINUTES, TIME_BIN_MINUTES, dtype=float)
    if edges[-1] < duration_minutes:
        edges = np.append(edges, duration_minutes)
    elif edges[-1] > duration_minutes:
        edges[-1] = duration_minutes
    if len(edges) < 2:
        edges = np.array([0.0, duration_minutes], dtype=float)
    return edges


def build_grid(events: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, float]]:
    required_cols = ["x_km", "y_km"]
    missing = [col for col in required_cols if col not in events.columns]
    if missing:
        raise ValueError(f"build_grid input missing required columns: {missing}")

    log("Constructing 0.5 km × 0.5 km study grid from [Mw 6.4, Mw 7.1] event extent")
    x_min = math.floor(events["x_km"].min() / GRID_SIZE_KM) * GRID_SIZE_KM
    x_max = math.ceil(events["x_km"].max() / GRID_SIZE_KM) * GRID_SIZE_KM
    y_min = math.floor(events["y_km"].min() / GRID_SIZE_KM) * GRID_SIZE_KM
    y_max = math.ceil(events["y_km"].max() / GRID_SIZE_KM) * GRID_SIZE_KM

    x_edges = np.arange(x_min, x_max + GRID_SIZE_KM, GRID_SIZE_KM)
    y_edges = np.arange(y_min, y_max + GRID_SIZE_KM, GRID_SIZE_KM)
    if len(x_edges) < 2 or len(y_edges) < 2:
        raise ValueError("Invalid grid extent: insufficient number of x/y edges")

    nx = len(x_edges) - 1
    ny = len(y_edges) - 1

    x_left = np.tile(x_edges[:-1], ny)
    x_right = np.tile(x_edges[1:], ny)
    y_bottom = np.repeat(y_edges[:-1], nx)
    y_top = np.repeat(y_edges[1:], nx)
    x_center = x_left + GRID_SIZE_KM / 2.0
    y_center = y_bottom + GRID_SIZE_KM / 2.0

    ix = np.tile(np.arange(nx, dtype=np.int32), ny)
    iy = np.repeat(np.arange(ny, dtype=np.int32), nx)
    cell_id = (iy.astype(np.int64) * nx + ix.astype(np.int64)).astype(np.int64)

    grid = pd.DataFrame(
        {
            "cell_id": cell_id,
            "ix": ix,
            "iy": iy,
            "x_left_km": x_left,
            "x_right_km": x_right,
            "y_bottom_km": y_bottom,
            "y_top_km": y_top,
            "x_center_km": x_center,
            "y_center_km": y_center,
        }
    )
    if grid["cell_id"].duplicated().any():
        raise ValueError("Grid construction produced duplicate cell_id values")

    meta = {
        "x_min_km": x_min,
        "x_max_km": x_max,
        "y_min_km": y_min,
        "y_max_km": y_max,
        "nx": nx,
        "ny": ny,
        "n_cells": len(grid),
    }
    return grid, meta


def assign_events_to_grid_and_time(events: pd.DataFrame, grid_meta: Dict[str, float], time_edges: np.ndarray) -> pd.DataFrame:
    required_cols = ["x_km", "y_km", "time_rel_min_from_64"]
    missing = [col for col in required_cols if col not in events.columns]
    if missing:
        raise ValueError(f"assign_events_to_grid_and_time input missing required columns: {missing}")

    log("Assigning events to grid cells and 30-minute time bins")
    nx = int(grid_meta["nx"])
    ny = int(grid_meta["ny"])
    x_min = float(grid_meta["x_min_km"])
    y_min = float(grid_meta["y_min_km"])

    x_index = np.floor((events["x_km"].to_numpy() - x_min) / GRID_SIZE_KM).astype(int)
    y_index = np.floor((events["y_km"].to_numpy() - y_min) / GRID_SIZE_KM).astype(int)
    x_index = np.clip(x_index, 0, nx - 1)
    y_index = np.clip(y_index, 0, ny - 1)
    cell_id = y_index * nx + x_index

    rel_min = events["time_rel_min_from_64"].to_numpy(dtype=float)
    duration_minutes = float(time_edges[-1])
    if np.any(rel_min < -1e-9) or np.any(rel_min > duration_minutes + 1e-9):
        raise ValueError("Found event times outside the [Mw 6.4, Mw 7.1] analysis interval")
    time_bin = np.searchsorted(time_edges, rel_min, side="right") - 1
    time_bin = np.where(np.isclose(rel_min, duration_minutes), len(time_edges) - 2, time_bin)
    time_bin = np.clip(time_bin, 0, len(time_edges) - 2)

    out = events.copy()
    out["grid_ix"] = x_index.astype(np.int32)
    out["grid_iy"] = y_index.astype(np.int32)
    out["cell_id"] = cell_id.astype(np.int64)
    out["time_bin_index_30min"] = time_bin.astype(np.int32)
    out["time_bin_start_min_30min"] = time_edges[time_bin]
    out["time_bin_end_min_30min"] = time_edges[time_bin + 1]
    return out


def build_cell_time_matrix(event_assignments: pd.DataFrame, grid: pd.DataFrame, time_edges: np.ndarray) -> Tuple[pd.DataFrame, np.ndarray]:
    n_cells = len(grid)
    n_time = len(time_edges) - 1
    log(f"Building cell-by-time count matrix: {n_cells:,} cells × {n_time:,} time bins")
    counts = np.zeros((n_cells, n_time), dtype=np.int32)

    grouped = (
        event_assignments.groupby(["cell_id", "time_bin_index_30min"]).size().reset_index(name="event_count")
    )
    counts[grouped["cell_id"].to_numpy(dtype=int), grouped["time_bin_index_30min"].to_numpy(dtype=int)] = grouped[
        "event_count"
    ].to_numpy(dtype=np.int32)

    records: List[pd.DataFrame] = []
    chunk_size = max(1, min(5000, n_cells // 8 if n_cells >= 8 else n_cells))
    for start in range(0, n_cells, chunk_size):
        stop = min(start + chunk_size, n_cells)
        chunk_counts = counts[start:stop, :]
        chunk_cell_ids = grid.iloc[start:stop]["cell_id"].to_numpy()
        chunk_df = pd.DataFrame(
            {
                "cell_id": np.repeat(chunk_cell_ids, n_time),
                "time_bin_index_30min": np.tile(np.arange(n_time, dtype=np.int32), len(chunk_cell_ids)),
                "time_bin_start_min": np.tile(time_edges[:-1], len(chunk_cell_ids)),
                "time_bin_end_min": np.tile(time_edges[1:], len(chunk_cell_ids)),
                "event_count": chunk_counts.reshape(-1),
            }
        )
        records.append(chunk_df)
        log(f"  Expanded matrix chunk {start:,}:{stop:,} to long-form rows")
    long_df = pd.concat(records, ignore_index=True)
    return long_df, counts


def choose_onset_rule(counts: np.ndarray, time_edges: np.ndarray) -> Tuple[OnsetRule, pd.DataFrame]:
    if counts.ndim != 2:
        raise ValueError(f"counts must be 2-D, got shape {counts.shape}")
    per_cell_total = counts.sum(axis=1)
    occupied_mask = per_cell_total > 0
    occupied_counts = counts[occupied_mask]
    positive_30min_counts = occupied_counts[occupied_counts > 0]
    if positive_30min_counts.size == 0:
        raise ValueError("No positive 30-minute counts found in occupied cells")

    threshold_count = int(max(1, min(2, np.percentile(positive_30min_counts, 75))))
    min_total_events = int(max(3, threshold_count + 2))
    cumulative_window_bins = max(2, int(round(ONSET_WINDOW_HOURS * 60.0 / TIME_BIN_MINUTES)))
    cumulative_sums = []
    for row in occupied_counts:
        if len(row) < cumulative_window_bins:
            cumulative_sums.append(row.sum())
        else:
            conv = np.convolve(row, np.ones(cumulative_window_bins, dtype=int), mode="valid")
            cumulative_sums.extend(conv.tolist())
    cumulative_sums = np.array(cumulative_sums, dtype=float)
    positive_cum = cumulative_sums[cumulative_sums > 0]
    if positive_cum.size == 0:
        raise ValueError("No positive cumulative counts available for onset-rule selection")
    cumulative_min_count = int(max(min_total_events, min(4, np.percentile(positive_cum, 60))))

    rule = OnsetRule(
        threshold_count=threshold_count,
        min_total_events=min_total_events,
        persistence_future_bins=ONSET_PERSISTENCE_FUTURE_BINS,
        persistence_min_active_bins=ONSET_PERSISTENCE_MIN_ACTIVE_BINS,
        cumulative_window_bins=cumulative_window_bins,
        cumulative_min_count=cumulative_min_count,
    )

    diagnostics = pd.DataFrame(
        [
            {"metric": "positive_30min_count_p50", "value": float(np.percentile(positive_30min_counts, 50))},
            {"metric": "positive_30min_count_p75", "value": float(np.percentile(positive_30min_counts, 75))},
            {"metric": "positive_30min_count_p90", "value": float(np.percentile(positive_30min_counts, 90))},
            {"metric": "occupied_cells", "value": int(occupied_mask.sum())},
            {"metric": "cells_with_total_ge_min_total_events", "value": int((per_cell_total >= min_total_events).sum())},
            {"metric": "cumulative_window_bins", "value": int(cumulative_window_bins)},
            {"metric": "cumulative_positive_p60", "value": float(np.percentile(positive_cum, 60))},
            {"metric": "selected_threshold_count", "value": int(threshold_count)},
            {"metric": "selected_min_total_events", "value": int(min_total_events)},
            {"metric": "selected_cumulative_min_count", "value": int(cumulative_min_count)},
        ]
    )
    return rule, diagnostics


def _init_onset_worker(counts_array: np.ndarray, onset_rule: OnsetRule) -> None:
    global _CELL_COUNTS_ARRAY, _ONSET_RULE_GLOBAL
    _CELL_COUNTS_ARRAY = counts_array
    _ONSET_RULE_GLOBAL = onset_rule


def _detect_onset_for_cell(cell_id: int) -> Dict[str, object]:
    counts = _CELL_COUNTS_ARRAY[cell_id]
    rule = _ONSET_RULE_GLOBAL
    total_events = int(counts.sum())
    first_positive_idx = int(np.argmax(counts > 0)) if np.any(counts > 0) else -1
    first_positive_count = int(counts[first_positive_idx]) if first_positive_idx >= 0 else 0

    if total_events == 0:
        return {
            "cell_id": int(cell_id),
            "total_events": 0,
            "first_event_bin_index": np.nan,
            "first_event_count": 0,
            "onset_bin_index": np.nan,
            "onset_count": np.nan,
            "future_active_bins": np.nan,
            "window_cumulative_count": np.nan,
            "quality_flag": "inactive",
        }

    if total_events < rule.min_total_events:
        return {
            "cell_id": int(cell_id),
            "total_events": total_events,
            "first_event_bin_index": first_positive_idx,
            "first_event_count": first_positive_count,
            "onset_bin_index": np.nan,
            "onset_count": np.nan,
            "future_active_bins": np.nan,
            "window_cumulative_count": np.nan,
            "quality_flag": "insufficient_data",
        }

    n_time = len(counts)
    for idx in range(n_time):
        current = int(counts[idx])
        if current < rule.threshold_count:
            continue
        future_end = min(n_time, idx + 1 + rule.persistence_future_bins)
        future_counts = counts[idx:future_end]
        future_active_bins = int(np.sum(future_counts >= rule.threshold_count))
        cum_end = min(n_time, idx + rule.cumulative_window_bins)
        window_cumulative = int(np.sum(counts[idx:cum_end]))
        if future_active_bins >= rule.persistence_min_active_bins and window_cumulative >= rule.cumulative_min_count:
            return {
                "cell_id": int(cell_id),
                "total_events": total_events,
                "first_event_bin_index": first_positive_idx,
                "first_event_count": first_positive_count,
                "onset_bin_index": idx,
                "onset_count": current,
                "future_active_bins": future_active_bins,
                "window_cumulative_count": window_cumulative,
                "quality_flag": "robust",
            }

    return {
        "cell_id": int(cell_id),
        "total_events": total_events,
        "first_event_bin_index": first_positive_idx,
        "first_event_count": first_positive_count,
        "onset_bin_index": np.nan,
        "onset_count": np.nan,
        "future_active_bins": np.nan,
        "window_cumulative_count": np.nan,
        "quality_flag": "ambiguous",
    }


def detect_onsets_parallel(counts: np.ndarray, rule: OnsetRule) -> pd.DataFrame:
    n_cells = counts.shape[0]
    workers = min(MAX_CORES, max(1, os.cpu_count() or 1))
    log(f"Running per-cell onset detection in parallel with {workers} workers across {n_cells:,} cells")
    chunksize = max(1, n_cells // (workers * 8))
    results: List[Dict[str, object]] = []
    processed = 0
    with ProcessPoolExecutor(max_workers=workers, initializer=_init_onset_worker, initargs=(counts, rule)) as executor:
        for result in executor.map(_detect_onset_for_cell, range(n_cells), chunksize=chunksize):
            results.append(result)
            processed += 1
            if processed % max(1, n_cells // 20) == 0 or processed == n_cells:
                log(f"  Onset detection progress: {processed:,}/{n_cells:,} cells")
    onset_df = pd.DataFrame(results).sort_values("cell_id").reset_index(drop=True)
    return onset_df


def add_onset_times(onset_df: pd.DataFrame, time_edges: np.ndarray) -> pd.DataFrame:
    required_cols = ["first_event_bin_index", "onset_bin_index"]
    missing = [col for col in required_cols if col not in onset_df.columns]
    if missing:
        raise ValueError(f"add_onset_times input missing required columns: {missing}")
    df = onset_df.copy()
    df["first_event_time_hr_from_64"] = np.where(
        df["first_event_bin_index"].notna(),
        time_edges[df["first_event_bin_index"].fillna(0).astype(int)] / 60.0,
        np.nan,
    )
    df["onset_time_hr_from_64"] = np.where(
        df["onset_bin_index"].notna(),
        time_edges[df["onset_bin_index"].fillna(0).astype(int)] / 60.0,
        np.nan,
    )
    df["onset_time_min_from_64"] = df["onset_time_hr_from_64"] * 60.0
    return df


def build_cell_summary_tables(
    grid: pd.DataFrame,
    counts: np.ndarray,
    onset_df: pd.DataFrame,
    ms64: MainshockReference,
    ms71: MainshockReference,
    time_edges: np.ndarray,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    if len(grid) != len(onset_df):
        raise ValueError(f"Grid/onset row mismatch: len(grid)={len(grid)}, len(onset_df)={len(onset_df)}")
    total_counts = counts.sum(axis=1)
    occupied = total_counts > 0
    robust = onset_df["quality_flag"].eq("robust").to_numpy()

    cell_total_counts = grid[["cell_id", "ix", "iy", "x_center_km", "y_center_km"]].copy()
    cell_total_counts["total_events"] = total_counts.astype(int)
    cell_total_counts["occupied_flag"] = occupied.astype(int)
    cell_total_counts["distance_to_mw64_km"] = np.hypot(
        cell_total_counts["x_center_km"] - ms64.x_km,
        cell_total_counts["y_center_km"] - ms64.y_km,
    )
    cell_total_counts["distance_to_mw71_km"] = np.hypot(
        cell_total_counts["x_center_km"] - ms71.x_km,
        cell_total_counts["y_center_km"] - ms71.y_km,
    )

    axis_vec = np.array([ms71.x_km - ms64.x_km, ms71.y_km - ms64.y_km], dtype=float)
    axis_len = float(np.hypot(axis_vec[0], axis_vec[1]))
    if axis_len <= 0:
        raise ValueError("Mw 6.4 and Mw 7.1 projected positions are identical; cannot define axis")
    axis_unit = axis_vec / axis_len
    perp_unit = np.array([-axis_unit[1], axis_unit[0]])

    dx = cell_total_counts["x_center_km"].to_numpy() - ms64.x_km
    dy = cell_total_counts["y_center_km"].to_numpy() - ms64.y_km
    along = dx * axis_unit[0] + dy * axis_unit[1]
    cross = dx * perp_unit[0] + dy * perp_unit[1]

    trigger_geometry = cell_total_counts[["cell_id", "x_center_km", "y_center_km"]].copy()
    trigger_geometry["distance_to_mw64_km"] = cell_total_counts["distance_to_mw64_km"]
    trigger_geometry["distance_to_mw71_km"] = cell_total_counts["distance_to_mw71_km"]
    trigger_geometry["alongstrike_km_from_mw64"] = along
    trigger_geometry["crossstrike_km_from_axis"] = cross
    trigger_geometry["axis_length_mw64_to_mw71_km"] = axis_len

    merged = grid.merge(onset_df, on="cell_id", how="left", validate="one_to_one").merge(
        trigger_geometry,
        on=["cell_id", "x_center_km", "y_center_km"],
        how="left",
        validate="one_to_one",
    )
    merged["onset_detected_flag"] = merged["quality_flag"].eq("robust").astype(int)
    merged["mw71_side_flag"] = (merged["alongstrike_km_from_mw64"] > axis_len / 2.0).astype(int)

    qc = pd.DataFrame(
        [
            {"metric": "n_grid_cells", "value": len(grid)},
            {"metric": "n_occupied_cells", "value": int(occupied.sum())},
            {"metric": "n_robust_onset_cells", "value": int(robust.sum())},
            {"metric": "n_ambiguous_cells", "value": int((onset_df['quality_flag'] == 'ambiguous').sum())},
            {"metric": "n_insufficient_data_cells", "value": int((onset_df['quality_flag'] == 'insufficient_data').sum())},
            {"metric": "n_inactive_cells", "value": int((onset_df['quality_flag'] == 'inactive').sum())},
            {"metric": "n_time_bins_30min", "value": len(time_edges) - 1},
            {"metric": "analysis_duration_hr", "value": float(time_edges[-1] / 60.0)},
        ]
    )
    return cell_total_counts, trigger_geometry, merged, qc


def save_onset_rule(rule: OnsetRule, diagnostics: pd.DataFrame, output_tables: Path) -> None:
    rule_df = pd.DataFrame(
        [
            {
                "threshold_count": rule.threshold_count,
                "min_total_events": rule.min_total_events,
                "persistence_future_bins": rule.persistence_future_bins,
                "persistence_min_active_bins": rule.persistence_min_active_bins,
                "cumulative_window_bins": rule.cumulative_window_bins,
                "cumulative_min_count": rule.cumulative_min_count,
                "time_bin_minutes": TIME_BIN_MINUTES,
                "grid_size_km": GRID_SIZE_KM,
            }
        ]
    )
    rule_df.to_csv(output_tables / "onset_rule_parameters.csv", index=False)
    diagnostics.to_csv(output_tables / "onset_rule_diagnostics.csv", index=False)


def plot_onset_map(cell_summary: pd.DataFrame, ms64: MainshockReference, ms71: MainshockReference, output_path: Path) -> None:
    log(f"Creating onset-time spatial map: {output_path}")
    fig, ax = plt.subplots(figsize=(10.5, 8.8), constrained_layout=True)

    active = cell_summary[cell_summary["quality_flag"] == "robust"].copy()
    undecided = cell_summary[cell_summary["quality_flag"].isin(["ambiguous", "insufficient_data"])].copy()

    cmap = LinearSegmentedColormap.from_list("onset_dark_to_light", ["#0b132b", "#3a506b", "#5bc0be", "#f2f2f2"])
    if not active.empty:
        sc = ax.scatter(
            active["longitude_center"],
            active["latitude_center"],
            c=active["onset_time_hr_from_64"],
            cmap=cmap,
            marker="s",
            s=20,
            linewidths=0.0,
            edgecolors="none",
            alpha=0.95,
        )
        cbar = fig.colorbar(sc, ax=ax, pad=0.02)
        cbar.set_label("Onset time after Mw 6.4 (hours)\nEarlier = darker, later = lighter")

    if not undecided.empty:
        ax.scatter(
            undecided["longitude_center"],
            undecided["latitude_center"],
            c="#9e9e9e",
            marker="s",
            s=14,
            linewidths=0.0,
            alpha=0.55,
            label="Ambiguous / insufficient-data cells",
        )

    ax.scatter(ms64.longitude, ms64.latitude, marker="*", s=260, c="#d62728", edgecolors="black", linewidths=0.8, label="Mw 6.4")
    ax.scatter(ms71.longitude, ms71.latitude, marker="^", s=170, c="#ffbf00", edgecolors="black", linewidths=0.8, label="Mw 7.1")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_title("Ridgecrest 0.5 km cell onset-time map\n[ Mw 6.4 , Mw 7.1 ] window")
    ax.grid(True, alpha=0.2, linewidth=0.5)
    ax.legend(loc="best", frameon=True)
    fig.savefig(output_path, dpi=FIG_DPI)
    plt.close(fig)


def attach_lon_lat_to_cells(cell_summary: pd.DataFrame, event_assignments: pd.DataFrame) -> pd.DataFrame:
    required_summary = ["cell_id", "total_events"]
    missing_summary = [col for col in required_summary if col not in cell_summary.columns]
    if missing_summary:
        raise ValueError(f"attach_lon_lat_to_cells cell_summary missing required columns: {missing_summary}")
    required_events = ["cell_id", "longitude", "latitude"]
    missing_events = [col for col in required_events if col not in event_assignments.columns]
    if missing_events:
        raise ValueError(f"attach_lon_lat_to_cells event_assignments missing required columns: {missing_events}")

    occupied_centers = (
        event_assignments.groupby("cell_id")[["longitude", "latitude"]]
        .median()
        .rename(columns={"longitude": "longitude_center", "latitude": "latitude_center"})
    )
    merged = cell_summary.merge(occupied_centers, on="cell_id", how="left", validate="one_to_one")
    occupied_missing = (merged["total_events"] > 0) & (merged["longitude_center"].isna() | merged["latitude_center"].isna())
    if occupied_missing.any():
        raise ValueError("Occupied cells are missing longitude/latitude center assignments")
    return merged


def plot_trigger_diagnostics(cell_summary: pd.DataFrame, ms64: MainshockReference, ms71: MainshockReference, output_path: Path) -> None:
    robust = cell_summary[cell_summary["quality_flag"] == "robust"].copy()
    log(f"Creating trigger diagnostic figure: {output_path}")
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 5.4), constrained_layout=True)

    if not robust.empty:
        axes[0].scatter(
            robust["alongstrike_km_from_mw64"],
            robust["onset_time_hr_from_64"],
            s=np.clip(robust["total_events"].to_numpy() * 2.0, 12.0, 110.0),
            c=robust["distance_to_mw71_km"],
            cmap="viridis",
            alpha=0.75,
            edgecolors="none",
        )
        axes[1].scatter(
            robust["distance_to_mw71_km"],
            robust["onset_time_hr_from_64"],
            s=np.clip(robust["total_events"].to_numpy() * 2.0, 12.0, 110.0),
            c=robust["alongstrike_km_from_mw64"],
            cmap="plasma",
            alpha=0.75,
            edgecolors="none",
        )

    axis_len = robust["axis_length_mw64_to_mw71_km"].iloc[0] if not robust.empty else math.hypot(ms71.x_km - ms64.x_km, ms71.y_km - ms64.y_km)
    axes[0].axvline(0.0, color="black", linestyle="--", linewidth=0.8)
    axes[0].axvline(axis_len, color="black", linestyle=":", linewidth=1.0)
    axes[0].set_xlabel("Along-strike distance from Mw 6.4 toward Mw 7.1 (km)")
    axes[0].set_ylabel("Onset time after Mw 6.4 (hours)")
    axes[0].set_title("Onset time vs along-strike position")
    axes[0].grid(True, alpha=0.25)

    axes[1].set_xlabel("Distance to Mw 7.1 epicenter (km)")
    axes[1].set_ylabel("Onset time after Mw 6.4 (hours)")
    axes[1].set_title("Onset time vs distance to Mw 7.1")
    axes[1].grid(True, alpha=0.25)

    fig.savefig(output_path, dpi=FIG_DPI)
    plt.close(fig)


def build_region_diagnostics(cell_summary: pd.DataFrame, event_assignments: pd.DataFrame, ms64: MainshockReference, ms71: MainshockReference) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    axis_len = float(np.hypot(ms71.x_km - ms64.x_km, ms71.y_km - ms64.y_km))

    conditions = [
        cell_summary["distance_to_mw64_km"] <= REGION_HALF_WIDTH_KM,
        cell_summary["distance_to_mw71_km"] <= REGION_HALF_WIDTH_KM,
        (
            (cell_summary["alongstrike_km_from_mw64"] >= 0.0)
            & (cell_summary["alongstrike_km_from_mw64"] <= axis_len)
            & (np.abs(cell_summary["crossstrike_km_from_axis"]) <= REGION_HALF_WIDTH_KM)
        ),
    ]
    labels = ["Mw6.4_vicinity", "Mw7.1_vicinity", "Intervening_corridor"]
    cell_summary = cell_summary.copy()
    cell_summary["region_label"] = np.select(conditions, labels, default="Outside_defined_regions")

    event_region = event_assignments[["event_id", "cell_id", "time_rel_hr_from_64"]].merge(
        cell_summary[["cell_id", "region_label"]], on="cell_id", how="left"
    )
    event_region = event_region[event_region["region_label"].isin(labels)].copy()
    event_region["time_bin_2h_index"] = np.floor(event_region["time_rel_hr_from_64"] / 2.0).astype(int)
    event_region["time_bin_2h_start_hr"] = event_region["time_bin_2h_index"] * 2.0
    event_region["time_bin_2h_end_hr"] = event_region["time_bin_2h_start_hr"] + 2.0

    regional_cumulative = (
        event_region.groupby(["region_label", "time_bin_2h_index", "time_bin_2h_start_hr", "time_bin_2h_end_hr"])
        .size()
        .reset_index(name="event_count")
        .sort_values(["region_label", "time_bin_2h_index"])
    )
    regional_cumulative["cumulative_event_count"] = regional_cumulative.groupby("region_label")["event_count"].cumsum()

    region_cells = cell_summary[cell_summary["region_label"].isin(labels)].copy()
    activated_cells = region_cells[region_cells["quality_flag"] == "robust"].copy()
    if activated_cells.empty:
        activated_fraction = pd.DataFrame(columns=["region_label", "threshold_hr", "activated_cells", "total_region_cells", "activated_fraction"])
    else:
        thresholds = np.arange(0.0, max(2.0, math.ceil(activated_cells["onset_time_hr_from_64"].max() / 2.0) * 2.0) + 0.01, 2.0)
        frac_records = []
        total_region_cells = region_cells.groupby("region_label").size().to_dict()
        for region in labels:
            region_active = activated_cells[activated_cells["region_label"] == region]
            for threshold in thresholds:
                activated_n = int((region_active["onset_time_hr_from_64"] <= threshold).sum())
                total_n = int(total_region_cells.get(region, 0))
                frac_records.append(
                    {
                        "region_label": region,
                        "threshold_hr": float(threshold),
                        "activated_cells": activated_n,
                        "total_region_cells": total_n,
                        "activated_fraction": float(activated_n / total_n) if total_n > 0 else np.nan,
                    }
                )
        activated_fraction = pd.DataFrame(frac_records)

    comparison_records = []
    for region in labels:
        region_df = region_cells[region_cells["region_label"] == region]
        robust_df = region_df[region_df["quality_flag"] == "robust"]
        comparison_records.append(
            {
                "region_label": region,
                "n_cells": int(len(region_df)),
                "n_occupied_cells": int((region_df["total_events"] > 0).sum()),
                "n_robust_onset_cells": int(len(robust_df)),
                "earliest_onset_hr": float(robust_df["onset_time_hr_from_64"].min()) if not robust_df.empty else np.nan,
                "median_onset_hr": float(robust_df["onset_time_hr_from_64"].median()) if not robust_df.empty else np.nan,
                "mean_distance_to_mw71_km": float(region_df["distance_to_mw71_km"].mean()) if not region_df.empty else np.nan,
                "mean_alongstrike_km": float(region_df["alongstrike_km_from_mw64"].mean()) if not region_df.empty else np.nan,
            }
        )
    comparison = pd.DataFrame(comparison_records)

    summary_style = "inconclusive"
    mw64_med = comparison.loc[comparison["region_label"] == "Mw6.4_vicinity", "median_onset_hr"].iloc[0]
    mw71_med = comparison.loc[comparison["region_label"] == "Mw7.1_vicinity", "median_onset_hr"].iloc[0]
    cor_med = comparison.loc[comparison["region_label"] == "Intervening_corridor", "median_onset_hr"].iloc[0]
    if np.isfinite(mw64_med) and np.isfinite(mw71_med):
        if mw71_med - mw64_med >= 4.0 and (not np.isfinite(cor_med) or mw64_med <= cor_med <= mw71_med):
            summary_style = "staged_or_cascade_like"
        elif abs(mw71_med - mw64_med) <= 2.0:
            summary_style = "synchronous_or_spatially_mixed"
        else:
            summary_style = "mixed"

    summary = pd.DataFrame(
        [
            {
                "trigger_style_summary": summary_style,
                "region_half_width_km": REGION_HALF_WIDTH_KM,
                "mw64_to_mw71_axis_length_km": axis_len,
                "mw64_median_onset_hr": mw64_med,
                "corridor_median_onset_hr": cor_med,
                "mw71_median_onset_hr": mw71_med,
            }
        ]
    )
    return cell_summary, regional_cumulative, activated_fraction, comparison, summary


def build_segment_level_summary(cell_summary: pd.DataFrame) -> pd.DataFrame:
    robust = cell_summary[cell_summary["quality_flag"] == "robust"].copy()
    if robust.empty:
        return pd.DataFrame(columns=["segment_index", "segment_start_km", "segment_end_km", "n_cells", "median_onset_hr", "min_onset_hr", "max_onset_hr"])
    axis_len = float(robust["axis_length_mw64_to_mw71_km"].iloc[0])
    edges = np.linspace(0.0, axis_len, SEGMENT_COUNT + 1)
    robust["segment_index"] = np.clip(np.searchsorted(edges, robust["alongstrike_km_from_mw64"], side="right") - 1, 0, SEGMENT_COUNT - 1)
    robust = robust[(robust["alongstrike_km_from_mw64"] >= 0.0) & (robust["alongstrike_km_from_mw64"] <= axis_len)].copy()
    summary = (
        robust.groupby("segment_index")
        .agg(
            n_cells=("cell_id", "size"),
            median_onset_hr=("onset_time_hr_from_64", "median"),
            min_onset_hr=("onset_time_hr_from_64", "min"),
            max_onset_hr=("onset_time_hr_from_64", "max"),
        )
        .reset_index()
    )
    summary["segment_start_km"] = summary["segment_index"].map(lambda i: float(edges[int(i)]))
    summary["segment_end_km"] = summary["segment_index"].map(lambda i: float(edges[int(i) + 1]))
    return summary[["segment_index", "segment_start_km", "segment_end_km", "n_cells", "median_onset_hr", "min_onset_hr", "max_onset_hr"]]


def main() -> None:
    ensure_clean_output_dir(OUTPUT_DIR)
    output_tables = OUTPUT_DIR / "tables"
    output_figures = OUTPUT_DIR / "figures"

    log(f"Task script: {SCRIPT_PATH}")
    log(f"Raw catalog path (read-only reference): {CATALOG_PATH}")

    ms64, ms71 = load_mainshocks()
    long_events = load_long_window_catalog()
    if long_events.empty:
        raise ValueError("Long-window event catalog is empty")
    log(f"Loaded long-window events: {len(long_events):,}")

    time_edges = build_time_bins(ms64, ms71)
    grid, grid_meta = build_grid(long_events)
    grid.to_csv(output_tables / "grid_definition_0p5km.csv", index=False)
    pd.DataFrame([grid_meta]).to_csv(output_tables / "grid_metadata_0p5km.csv", index=False)
    log(f"Grid built with {grid_meta['n_cells']:,} cells ({grid_meta['nx']} × {grid_meta['ny']})")

    event_assignments = assign_events_to_grid_and_time(long_events, grid_meta, time_edges)
    event_assignments.to_csv(output_tables / "event_grid_time_assignments.csv", index=False)

    cell_rate_timeseries, counts = build_cell_time_matrix(event_assignments, grid, time_edges)
    cell_rate_timeseries.to_csv(output_tables / "cell_rate_timeseries_30min.csv", index=False)

    onset_rule, onset_diagnostics = choose_onset_rule(counts, time_edges)
    save_onset_rule(onset_rule, onset_diagnostics, output_tables)
    log(
        "Selected onset rule: "
        f"threshold_count={onset_rule.threshold_count}, "
        f"min_total_events={onset_rule.min_total_events}, "
        f"persistence_future_bins={onset_rule.persistence_future_bins}, "
        f"persistence_min_active_bins={onset_rule.persistence_min_active_bins}, "
        f"cumulative_window_bins={onset_rule.cumulative_window_bins}, "
        f"cumulative_min_count={onset_rule.cumulative_min_count}"
    )

    onset_df = detect_onsets_parallel(counts, onset_rule)
    onset_df = add_onset_times(onset_df, time_edges)
    if onset_df["cell_id"].duplicated().any():
        raise ValueError("Duplicate cell_id entries found in onset results")
    valid_onsets = onset_df["onset_time_hr_from_64"].dropna()
    duration_hr = time_edges[-1] / 60.0
    if not valid_onsets.empty and ((valid_onsets < 0).any() or (valid_onsets > duration_hr + 1e-9).any()):
        raise ValueError("Detected onset times outside [Mw 6.4, Mw 7.1] interval")
    onset_df.to_csv(output_tables / "cell_activity_quality_flags.csv", index=False)
    onset_df.to_csv(output_tables / "cell_onset_time_summary.csv", index=False)

    cell_total_counts, trigger_geometry, cell_summary, qc = build_cell_summary_tables(grid, counts, onset_df, ms64, ms71, time_edges)
    cell_total_counts.to_csv(output_tables / "cell_total_counts.csv", index=False)
    trigger_geometry.to_csv(output_tables / "cell_trigger_geometry_metrics.csv", index=False)
    qc.to_csv(output_tables / "onset_qc_summary.csv", index=False)

    cell_summary = attach_lon_lat_to_cells(cell_summary, event_assignments)
    cell_summary.to_csv(output_tables / "cell_onset_time_summary_with_geometry.csv", index=False)

    plot_onset_map(cell_summary, ms64, ms71, output_figures / "ridgecrest_onset_time_map.png")
    plot_trigger_diagnostics(cell_summary, ms64, ms71, output_figures / "onset_vs_trigger_geometry.png")

    cell_summary_region, regional_cumulative, activated_fraction, comparison, summary = build_region_diagnostics(cell_summary, event_assignments, ms64, ms71)
    regional_cumulative.to_csv(output_tables / "regional_cumulative_event_counts.csv", index=False)
    activated_fraction.to_csv(output_tables / "regional_activated_cell_fraction.csv", index=False)
    comparison.to_csv(output_tables / "region_comparison_summary.csv", index=False)
    summary.to_csv(output_tables / "trigger_style_summary.csv", index=False)

    segment_summary = build_segment_level_summary(cell_summary_region)
    segment_summary.to_csv(output_tables / "segment_level_onset_summary.csv", index=False)

    log("Completed grid, onset, and trigger diagnostics successfully.")
    log(f"Outputs written to: {OUTPUT_DIR}")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print(traceback.format_exc(), flush=True)
        sys.exit(1)
