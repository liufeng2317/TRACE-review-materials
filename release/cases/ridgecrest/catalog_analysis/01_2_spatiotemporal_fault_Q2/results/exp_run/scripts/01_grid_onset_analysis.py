from __future__ import annotations

import json
import math
import os
import shutil
import sys
import time
import traceback
from dataclasses import dataclass
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from joblib import Parallel, delayed
from matplotlib.colors import Normalize
from pyproj import CRS, Transformer


CATALOG_PATH = Path('<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/TRACE_ridgecrest_relocated.csv')
MAINSHOCK_PATH = Path('<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/main_shock_events.csv')
FAULT_PATH = Path('<REPO_ROOT>/examples/ridgecrest/data/faults/ridgecrest_surface_faults.json')
SCRIPT_PATH = Path('<REPO_ROOT>/examples/ridgecrest/catalog_analysis/run/01_2_trigger_spatiotemporal_fault_Q2-v1/exp_run/scripts/01_grid_onset_analysis.py')
OUTPUT_DIR = Path('<REPO_ROOT>/examples/ridgecrest/catalog_analysis/run/01_2_trigger_spatiotemporal_fault_Q2-v1/exp_run/outputs/01_grid_onset_analysis')

GRID_SPACING_KM = 1.0
BUFFER_KM = 5.0
TIME_BIN_MINUTES = 30
MAX_CORES = 64
EXAMPLE_SERIES_COUNT = 4
RNG_SEED = 42


@dataclass
class OnsetResult:
    onset_bin: float
    onset_minutes: float
    support_candidate_next1: float
    support_candidate_next2: float
    total_events: int
    peak_count: int
    peak_rate_per_hour: float
    confidence_class: str


def log(message: str) -> None:
    print(f'[{time.strftime("%Y-%m-%d %H:%M:%S")}] {message}', flush=True)


def prepare_output_dir(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for child in output_dir.iterdir():
        if child.is_file() and child.suffix.lower() in {'.csv', '.json', '.png', '.txt'}:
            child.unlink()
        elif child.is_dir() and child.name in {'tables', 'figures'}:
            shutil.rmtree(child)
    (output_dir / 'tables').mkdir(parents=True, exist_ok=True)
    (output_dir / 'figures').mkdir(parents=True, exist_ok=True)


def load_inputs() -> tuple[pd.DataFrame, pd.DataFrame, list[list[list[float]]]]:
    log(f'Loading catalog: {CATALOG_PATH}')
    catalog = pd.read_csv(CATALOG_PATH)
    log(f'Loading mainshocks: {MAINSHOCK_PATH}')
    main = pd.read_csv(MAINSHOCK_PATH)
    log(f'Loading faults: {FAULT_PATH}')
    with FAULT_PATH.open('r', encoding='utf-8') as f:
        faults = json.load(f)
    return catalog, main, faults


def validate_catalog(df: pd.DataFrame, name: str) -> tuple[pd.DataFrame, dict]:
    required = ['event_time', 'latitude', 'longitude', 'depth_km', 'magnitude']
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f'{name} missing required columns: {missing}')

    qc = {
        'input_rows': int(len(df)),
        'missing_required_rows': 0,
        'duplicate_rows_removed': 0,
        'invalid_numeric_rows': 0,
        'invalid_time_rows': 0,
        'retained_rows': 0,
    }

    work = df.copy()
    missing_mask = work[required].isna().any(axis=1)
    qc['missing_required_rows'] = int(missing_mask.sum())
    work = work.loc[~missing_mask].copy()

    dup_mask = work.duplicated(subset=required, keep='first')
    qc['duplicate_rows_removed'] = int(dup_mask.sum())
    work = work.loc[~dup_mask].copy()

    for c in ['latitude', 'longitude', 'depth_km', 'magnitude']:
        work[c] = pd.to_numeric(work[c], errors='coerce')
    invalid_numeric = ~np.isfinite(work[['latitude', 'longitude', 'depth_km', 'magnitude']]).all(axis=1)
    qc['invalid_numeric_rows'] = int(invalid_numeric.sum())
    work = work.loc[~invalid_numeric].copy()

    work['event_time'] = pd.to_datetime(work['event_time'], utc=True, errors='coerce')
    invalid_time = work['event_time'].isna()
    qc['invalid_time_rows'] = int(invalid_time.sum())
    work = work.loc[~invalid_time].copy()

    work = work.reset_index(drop=True)
    work['event_id'] = np.arange(len(work), dtype=np.int64)
    qc['retained_rows'] = int(len(work))
    return work, qc


def validate_faults(faults: list) -> tuple[list[np.ndarray], dict]:
    cleaned = []
    n_invalid = 0
    n_short = 0
    for poly in faults:
        if not isinstance(poly, list):
            n_invalid += 1
            continue
        arr = np.asarray(poly, dtype=float)
        if arr.ndim != 2 or arr.shape[1] != 2 or len(arr) < 2:
            n_invalid += 1
            continue
        finite = np.isfinite(arr).all(axis=1)
        arr = arr[finite]
        if len(arr) < 2:
            n_short += 1
            continue
        dedup = [arr[0]]
        for p in arr[1:]:
            if not np.allclose(p, dedup[-1]):
                dedup.append(p)
        arr = np.asarray(dedup, dtype=float)
        if len(arr) < 2:
            n_short += 1
            continue
        cleaned.append(arr)
    qc = {
        'input_fault_polylines': int(len(faults)),
        'invalid_fault_polylines': int(n_invalid),
        'too_short_fault_polylines': int(n_short),
        'retained_fault_polylines': int(len(cleaned)),
    }
    return cleaned, qc


def build_local_transformer(main_df: pd.DataFrame) -> tuple[Transformer, Transformer, CRS]:
    lon0 = float(main_df['longitude'].mean())
    lat0 = float(main_df['latitude'].mean())
    proj4 = f'+proj=aeqd +lat_0={lat0} +lon_0={lon0} +datum=WGS84 +units=km +no_defs'
    crs_local = CRS.from_proj4(proj4)
    to_local = Transformer.from_crs('EPSG:4326', crs_local, always_xy=True)
    to_geo = Transformer.from_crs(crs_local, 'EPSG:4326', always_xy=True)
    return to_local, to_geo, crs_local


def project_xy(lon: np.ndarray, lat: np.ndarray, transformer: Transformer) -> tuple[np.ndarray, np.ndarray]:
    x, y = transformer.transform(lon, lat)
    return np.asarray(x, dtype=float), np.asarray(y, dtype=float)


def build_study_region(faults: list[np.ndarray], transformer: Transformer) -> tuple[pd.DataFrame, tuple[float, float, float, float], np.ndarray, np.ndarray]:
    xs_all = []
    ys_all = []
    for arr in faults:
        x, y = project_xy(arr[:, 0], arr[:, 1], transformer)
        xs_all.append(x)
        ys_all.append(y)
    xs = np.concatenate(xs_all)
    ys = np.concatenate(ys_all)
    xmin = math.floor((float(xs.min()) - BUFFER_KM) / GRID_SPACING_KM) * GRID_SPACING_KM
    xmax = math.ceil((float(xs.max()) + BUFFER_KM) / GRID_SPACING_KM) * GRID_SPACING_KM
    ymin = math.floor((float(ys.min()) - BUFFER_KM) / GRID_SPACING_KM) * GRID_SPACING_KM
    ymax = math.ceil((float(ys.max()) + BUFFER_KM) / GRID_SPACING_KM) * GRID_SPACING_KM
    bounds = (xmin, xmax, ymin, ymax)
    region_df = pd.DataFrame([
        {
            'xmin_km': xmin,
            'xmax_km': xmax,
            'ymin_km': ymin,
            'ymax_km': ymax,
            'buffer_km': BUFFER_KM,
            'grid_spacing_km': GRID_SPACING_KM,
        }
    ])
    return region_df, bounds, xs, ys


def select_mainshocks(main_df: pd.DataFrame) -> pd.DataFrame:
    mags = main_df['magnitude'].round(1)
    ms64 = main_df.loc[np.isclose(mags, 6.4)]
    ms71 = main_df.loc[np.isclose(mags, 7.1)]
    if len(ms64) != 1 or len(ms71) != 1:
        raise ValueError('Failed to identify unique Mw 6.4 and Mw 7.1 mainshocks from main_shock_events.csv')
    out = pd.concat([ms64, ms71], ignore_index=True).copy()
    out = out.sort_values('event_time').reset_index(drop=True)
    if not np.isclose(out.iloc[0]['magnitude'], 6.4) or not np.isclose(out.iloc[1]['magnitude'], 7.1):
        raise ValueError('Mainshock chronology inconsistent with expected Mw 6.4 then Mw 7.1 ordering')
    out['mainshock_label'] = ['Mainshock64', 'Mainshock71']
    return out


def filter_events(catalog: pd.DataFrame, main_df: pd.DataFrame, bounds: tuple[float, float, float, float], transformer: Transformer) -> tuple[pd.DataFrame, dict]:
    t0 = main_df.loc[main_df['mainshock_label'] == 'Mainshock64', 'event_time'].iloc[0]
    t1 = main_df.loc[main_df['mainshock_label'] == 'Mainshock71', 'event_time'].iloc[0]
    xmin, xmax, ymin, ymax = bounds
    work = catalog.copy()
    work['x_km'], work['y_km'] = project_xy(work['longitude'].to_numpy(), work['latitude'].to_numpy(), transformer)

    time_mask = (work['event_time'] >= t0) & (work['event_time'] <= t1)
    spatial_mask = (work['x_km'] >= xmin) & (work['x_km'] < xmax) & (work['y_km'] >= ymin) & (work['y_km'] < ymax)
    final = work.loc[time_mask & spatial_mask].copy()
    final = final.sort_values('event_time').reset_index(drop=True)
    final['elapsed_minutes'] = (final['event_time'] - t0).dt.total_seconds() / 60.0
    final['elapsed_hours'] = final['elapsed_minutes'] / 60.0
    final['time_bin'] = np.floor(final['elapsed_minutes'] / TIME_BIN_MINUTES).astype(int)

    qc = {
        'catalog_total_events': int(len(catalog)),
        'time_window_events': int(time_mask.sum()),
        'spatial_window_events': int(spatial_mask.sum()),
        'final_spatiotemporal_events': int(len(final)),
        't0_utc': str(t0),
        't1_utc': str(t1),
        'window_duration_minutes': float((t1 - t0).total_seconds() / 60.0),
        'window_duration_hours': float((t1 - t0).total_seconds() / 3600.0),
    }
    return final, qc


def add_mainshock_projection(main_df: pd.DataFrame, transformer: Transformer, bounds: tuple[float, float, float, float]) -> pd.DataFrame:
    out = main_df.copy()
    out['x_km'], out['y_km'] = project_xy(out['longitude'].to_numpy(), out['latitude'].to_numpy(), transformer)
    t0 = out.loc[out['mainshock_label'] == 'Mainshock64', 'event_time'].iloc[0]
    out['elapsed_minutes_since_mw64'] = (out['event_time'] - t0).dt.total_seconds() / 60.0
    xmin, xmax, ymin, ymax = bounds
    inside = (out['x_km'] >= xmin) & (out['x_km'] < xmax) & (out['y_km'] >= ymin) & (out['y_km'] < ymax)
    if not bool(inside.all()):
        raise ValueError('One or both mainshocks fall outside the study region')
    return out


def build_grid(bounds: tuple[float, float, float, float], to_geo: Transformer) -> pd.DataFrame:
    xmin, xmax, ymin, ymax = bounds
    nx = int(round((xmax - xmin) / GRID_SPACING_KM))
    ny = int(round((ymax - ymin) / GRID_SPACING_KM))
    if nx <= 0 or ny <= 0:
        raise ValueError(f'Invalid grid dimensions derived from bounds={bounds}')
    log(f'Building grid with nx={nx}, ny={ny}, cells={nx * ny}')
    x_edges = xmin + np.arange(nx + 1) * GRID_SPACING_KM
    y_edges = ymin + np.arange(ny + 1) * GRID_SPACING_KM
    x0 = np.repeat(x_edges[:-1], ny)
    x1 = np.repeat(x_edges[1:], ny)
    y0 = np.tile(y_edges[:-1], nx)
    y1 = np.tile(y_edges[1:], nx)
    cx = 0.5 * (x0 + x1)
    cy = 0.5 * (y0 + y1)
    lonc, latc = to_geo.transform(cx, cy)
    cell_ids = np.arange(len(cx), dtype=np.int64)
    ix = np.repeat(np.arange(nx), ny)
    iy = np.tile(np.arange(ny), nx)
    grid = pd.DataFrame(
        {
            'cell_id': cell_ids,
            'ix': ix,
            'iy': iy,
            'xmin_km': x0,
            'xmax_km': x1,
            'ymin_km': y0,
            'ymax_km': y1,
            'x_center_km': cx,
            'y_center_km': cy,
            'centroid_longitude': lonc,
            'centroid_latitude': latc,
        }
    )
    required = {'cell_id', 'ix', 'iy', 'xmin_km', 'xmax_km', 'ymin_km', 'ymax_km', 'x_center_km', 'y_center_km', 'centroid_longitude', 'centroid_latitude'}
    if not required.issubset(grid.columns):
        raise ValueError('Grid definition missing required downstream columns')
    return grid


def assign_events_to_grid(events: pd.DataFrame, grid: pd.DataFrame, bounds: tuple[float, float, float, float]) -> pd.DataFrame:
    xmin, xmax, ymin, ymax = bounds
    nx = int(grid['ix'].max()) + 1
    ny = int(grid['iy'].max()) + 1
    work = events.copy()
    ix = np.floor((work['x_km'].to_numpy() - xmin) / GRID_SPACING_KM).astype(int)
    iy = np.floor((work['y_km'].to_numpy() - ymin) / GRID_SPACING_KM).astype(int)
    valid = (ix >= 0) & (ix < nx) & (iy >= 0) & (iy < ny)
    work = work.loc[valid].copy()
    ix = ix[valid]
    iy = iy[valid]
    work['ix'] = ix
    work['iy'] = iy
    work['cell_id'] = ix * ny + iy
    return work


def compute_time_bins(t0: pd.Timestamp, t1: pd.Timestamp) -> pd.DataFrame:
    duration_minutes = (t1 - t0).total_seconds() / 60.0
    n_bins = int(math.floor(duration_minutes / TIME_BIN_MINUTES)) + 1
    starts = [t0 + pd.Timedelta(minutes=TIME_BIN_MINUTES * i) for i in range(n_bins)]
    ends = [s + pd.Timedelta(minutes=TIME_BIN_MINUTES) for s in starts]
    return pd.DataFrame(
        {
            'time_bin': np.arange(n_bins, dtype=int),
            'bin_start_utc': starts,
            'bin_end_utc': ends,
            'bin_center_minutes': (np.arange(n_bins, dtype=float) + 0.5) * TIME_BIN_MINUTES,
            'bin_start_minutes': np.arange(n_bins, dtype=float) * TIME_BIN_MINUTES,
            'bin_end_minutes': (np.arange(n_bins, dtype=float) + 1.0) * TIME_BIN_MINUTES,
        }
    )


def build_cell_time_series(assignments: pd.DataFrame, time_bins: pd.DataFrame, n_jobs: int) -> pd.DataFrame:
    n_bins = len(time_bins)
    required = {'cell_id', 'time_bin'}
    if not required.issubset(assignments.columns):
        raise ValueError(f'Assignments missing required columns: {sorted(required - set(assignments.columns))}')
    if len(assignments) == 0:
        log('No assigned events available; returning empty cell time-series table')
        return pd.DataFrame(
            {
                'cell_id': pd.Series(dtype='int64'),
                'time_bin': pd.Series(dtype='int64'),
                'event_count': pd.Series(dtype='int64'),
                'rate_events_per_hour': pd.Series(dtype='float64'),
                'cumulative_count': pd.Series(dtype='int64'),
            }
        )

    grouped = assignments.groupby('cell_id', sort=True)
    cell_ids = list(grouped.groups.keys())
    log(f'Constructing per-cell time series for {len(cell_ids)} occupied cells using {n_jobs} workers')

    def _one(cell_id: int) -> pd.DataFrame:
        sub = grouped.get_group(cell_id)
        counts = np.bincount(sub['time_bin'].to_numpy(), minlength=n_bins)
        df = pd.DataFrame(
            {
                'cell_id': cell_id,
                'time_bin': np.arange(n_bins, dtype=int),
                'event_count': counts.astype(int),
            }
        )
        df['rate_events_per_hour'] = df['event_count'] * (60.0 / TIME_BIN_MINUTES)
        df['cumulative_count'] = df['event_count'].cumsum()
        return df

    pieces = Parallel(n_jobs=n_jobs, prefer='processes', verbose=10)(delayed(_one)(cid) for cid in cell_ids)
    out = pd.concat(pieces, ignore_index=True)
    expected_cols = {'cell_id', 'time_bin', 'event_count', 'rate_events_per_hour', 'cumulative_count'}
    if not expected_cols.issubset(out.columns):
        raise ValueError('Cell time-series table missing required downstream columns')
    return out


def detect_onset(counts: np.ndarray) -> OnsetResult:
    total = int(counts.sum())
    peak = int(counts.max()) if len(counts) else 0
    peak_rate = peak * (60.0 / TIME_BIN_MINUTES)
    for i, c in enumerate(counts):
        if c < 2:
            continue
        next1 = int(c + (counts[i + 1] if i + 1 < len(counts) else 0))
        next2 = int(c + counts[i + 1:i + 3].sum())
        nonzero_after = bool((counts[i + 1:i + 3] > 0).any())
        sustained = (next1 >= 3) or (next2 >= 3 and nonzero_after)
        if sustained:
            confidence = 'robust onset' if (total >= 4 and next1 >= 3) else 'weak onset'
            return OnsetResult(
                onset_bin=float(i),
                onset_minutes=float(i * TIME_BIN_MINUTES),
                support_candidate_next1=float(next1),
                support_candidate_next2=float(next2),
                total_events=total,
                peak_count=peak,
                peak_rate_per_hour=float(peak_rate),
                confidence_class=confidence,
            )
    return OnsetResult(
        onset_bin=np.nan,
        onset_minutes=np.nan,
        support_candidate_next1=np.nan,
        support_candidate_next2=np.nan,
        total_events=total,
        peak_count=peak,
        peak_rate_per_hour=float(peak_rate),
        confidence_class='no onset',
    )


def compute_onset_table(cell_time_series: pd.DataFrame, grid: pd.DataFrame, assignments: pd.DataFrame, n_jobs: int) -> pd.DataFrame:
    occupied_counts = assignments.groupby('cell_id').size().rename('total_cell_events') if len(assignments) else pd.Series(dtype='int64', name='total_cell_events')
    if len(cell_time_series) == 0:
        log('No occupied cell time series available; returning grid with empty onset attributes')
        onset = grid.copy()
        onset['onset_bin'] = np.nan
        onset['onset_minutes'] = np.nan
        onset['onset_hours'] = np.nan
        onset['support_candidate_next1'] = np.nan
        onset['support_candidate_next2'] = np.nan
        onset['total_cell_events'] = 0
        onset['peak_count'] = 0
        onset['peak_rate_per_hour'] = 0.0
        onset['confidence_class'] = 'no events'
        onset['occupied'] = False
        return onset

    grouped = cell_time_series.groupby('cell_id', sort=True)
    cell_ids = list(grouped.groups.keys())
    log(f'Computing onset table for {len(cell_ids)} occupied cells using {n_jobs} workers')

    def _one(cell_id: int) -> dict:
        sub = grouped.get_group(cell_id)
        result = detect_onset(sub['event_count'].to_numpy())
        return {
            'cell_id': int(cell_id),
            'onset_bin': result.onset_bin,
            'onset_minutes': result.onset_minutes,
            'onset_hours': result.onset_minutes / 60.0 if np.isfinite(result.onset_minutes) else np.nan,
            'support_candidate_next1': result.support_candidate_next1,
            'support_candidate_next2': result.support_candidate_next2,
            'total_cell_events': result.total_events,
            'peak_count': result.peak_count,
            'peak_rate_per_hour': result.peak_rate_per_hour,
            'confidence_class': result.confidence_class,
        }

    rows = Parallel(n_jobs=n_jobs, prefer='processes', verbose=10)(delayed(_one)(cid) for cid in cell_ids)
    onset = pd.DataFrame(rows)
    onset = grid.merge(onset, on='cell_id', how='left')
    onset['occupied'] = onset['cell_id'].isin(occupied_counts.index)
    onset['total_cell_events'] = onset['total_cell_events'].fillna(0).astype(int)
    onset['peak_count'] = onset['peak_count'].fillna(0).astype(int)
    onset['peak_rate_per_hour'] = onset['peak_rate_per_hour'].fillna(0.0)
    onset['confidence_class'] = onset['confidence_class'].fillna('no events')
    expected_cols = {'cell_id', 'occupied', 'onset_bin', 'onset_minutes', 'onset_hours', 'total_cell_events', 'peak_count', 'peak_rate_per_hour', 'confidence_class'}
    if not expected_cols.issubset(onset.columns):
        raise ValueError('Grid onset table missing required downstream columns')
    return onset


def save_table(df: pd.DataFrame, path: Path) -> None:
    df.to_csv(path, index=False)
    log(f'Saved table: {path}')


def fig_size_from_bounds(bounds: tuple[float, float, float, float], base: float = 10.0) -> tuple[float, float]:
    xmin, xmax, ymin, ymax = bounds
    width = xmax - xmin
    height = ymax - ymin
    if width <= 0 or height <= 0:
        return (10, 8)
    aspect = width / height
    if aspect >= 1:
        return (base, max(6.5, base / max(aspect, 1e-6)))
    return (max(6.5, base * aspect), base)


def plot_overview_map(events: pd.DataFrame, main_df: pd.DataFrame, fault_xs: np.ndarray, fault_ys: np.ndarray, bounds: tuple[float, float, float, float], outpath: Path) -> None:
    fig, ax = plt.subplots(figsize=fig_size_from_bounds(bounds, base=11))
    ax.scatter(fault_xs, fault_ys, s=0.05, c='0.5', alpha=0.5, label='Fault points', rasterized=True)
    if len(events) > 0:
        ax.scatter(events['x_km'], events['y_km'], s=1.0, c='tab:blue', alpha=0.2, label='Filtered events', rasterized=True)
    colors = {'Mainshock64': 'red', 'Mainshock71': 'gold'}
    for _, row in main_df.iterrows():
        ax.scatter(row['x_km'], row['y_km'], s=120, c=colors[row['mainshock_label']], edgecolor='black', marker='*', zorder=5, label=row['mainshock_label'])
    xmin, xmax, ymin, ymax = bounds
    ax.add_patch(plt.Rectangle((xmin, ymin), xmax - xmin, ymax - ymin, fill=False, lw=1.5, ec='black', ls='--', label='Study region'))
    ax.set_xlabel('Local x (km)')
    ax.set_ylabel('Local y (km)')
    ax.set_title('Ridgecrest study region overview')
    ax.set_aspect('equal', adjustable='box')
    handles, labels = ax.get_legend_handles_labels()
    uniq = dict(zip(labels, handles))
    ax.legend(uniq.values(), uniq.keys(), loc='best', fontsize=8)
    fig.tight_layout()
    fig.savefig(outpath, dpi=250)
    plt.close(fig)
    log(f'Saved figure: {outpath}')


def plot_occupied_cells(grid_onset: pd.DataFrame, bounds: tuple[float, float, float, float], outpath: Path) -> None:
    occ = grid_onset.loc[grid_onset['occupied']]
    fig, ax = plt.subplots(figsize=fig_size_from_bounds(bounds, base=11))
    ax.scatter(occ['x_center_km'], occ['y_center_km'], s=8, c=occ['total_cell_events'], cmap='viridis', alpha=0.8)
    ax.set_xlabel('Local x (km)')
    ax.set_ylabel('Local y (km)')
    ax.set_title('Occupied 1 km grid cells colored by event total')
    ax.set_aspect('equal', adjustable='box')
    sm = plt.cm.ScalarMappable(norm=Normalize(vmin=max(1, occ['total_cell_events'].min() if len(occ) else 1), vmax=max(1, occ['total_cell_events'].max() if len(occ) else 1)), cmap='viridis')
    fig.colorbar(sm, ax=ax, label='Events per occupied cell')
    fig.tight_layout()
    fig.savefig(outpath, dpi=250)
    plt.close(fig)
    log(f'Saved figure: {outpath}')


def plot_event_total_hist(grid_onset: pd.DataFrame, outpath: Path) -> None:
    occ = grid_onset.loc[grid_onset['occupied'], 'total_cell_events']
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(occ, bins=40, color='tab:blue', alpha=0.8)
    ax.set_xlabel('Events per occupied cell')
    ax.set_ylabel('Count of occupied cells')
    ax.set_title('Histogram of event totals per occupied cell')
    fig.tight_layout()
    fig.savefig(outpath, dpi=250)
    plt.close(fig)
    log(f'Saved figure: {outpath}')


def plot_total_rate(cell_time_series: pd.DataFrame, time_bins: pd.DataFrame, outpath: Path) -> None:
    total = cell_time_series.groupby('time_bin', as_index=False)['event_count'].sum()
    total = time_bins[['time_bin', 'bin_start_minutes']].merge(total, on='time_bin', how='left').fillna({'event_count': 0})
    total['rate_events_per_hour'] = total['event_count'] * (60.0 / TIME_BIN_MINUTES)
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(total['bin_start_minutes'] / 60.0, total['rate_events_per_hour'], color='tab:purple', lw=2)
    ax.set_xlabel('Hours since Mw 6.4')
    ax.set_ylabel('Study-area seismicity rate (events/hour)')
    ax.set_title('Total study-area seismicity rate vs time')
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(outpath, dpi=250)
    plt.close(fig)
    log(f'Saved figure: {outpath}')


def plot_onset_map(grid_onset: pd.DataFrame, main_df: pd.DataFrame, fault_xs: np.ndarray, fault_ys: np.ndarray, bounds: tuple[float, float, float, float], outpath: Path) -> None:
    activated = grid_onset.loc[np.isfinite(grid_onset['onset_minutes'])]
    no_onset = grid_onset.loc[grid_onset['occupied'] & ~np.isfinite(grid_onset['onset_minutes'])]
    fig, ax = plt.subplots(figsize=fig_size_from_bounds(bounds, base=11))
    ax.scatter(fault_xs, fault_ys, s=0.05, c='0.7', alpha=0.35, rasterized=True)
    if len(no_onset):
        ax.scatter(no_onset['x_center_km'], no_onset['y_center_km'], s=8, c='lightgray', alpha=0.6, label='Occupied, no onset')
    sc = ax.scatter(
        activated['x_center_km'],
        activated['y_center_km'],
        s=10,
        c=activated['onset_hours'],
        cmap='Greys_r',
        alpha=0.9,
        label='Activated cells',
    )
    colors = {'Mainshock64': 'red', 'Mainshock71': 'gold'}
    for _, row in main_df.iterrows():
        ax.scatter(row['x_km'], row['y_km'], s=150, c=colors[row['mainshock_label']], edgecolor='black', marker='*', zorder=6, label=row['mainshock_label'])
    ax.set_xlabel('Local x (km)')
    ax.set_ylabel('Local y (km)')
    ax.set_title('Grid-cell activation onset time map')
    ax.set_aspect('equal', adjustable='box')
    cbar = fig.colorbar(sc, ax=ax, label='Onset time since Mw 6.4 (hours)') if len(activated) else None
    handles, labels = ax.get_legend_handles_labels()
    uniq = dict(zip(labels, handles))
    ax.legend(uniq.values(), uniq.keys(), loc='best', fontsize=8)
    fig.tight_layout()
    fig.savefig(outpath, dpi=250)
    plt.close(fig)
    log(f'Saved figure: {outpath}')


def plot_onset_histogram(grid_onset: pd.DataFrame, outpath: Path) -> None:
    vals = grid_onset.loc[np.isfinite(grid_onset['onset_hours']), 'onset_hours']
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    axes[0].hist(vals, bins=40, color='0.2', alpha=0.85)
    axes[0].set_xlabel('Onset time since Mw 6.4 (hours)')
    axes[0].set_ylabel('Activated cells')
    axes[0].set_title('Onset-time histogram')
    if len(vals):
        xs = np.sort(vals.to_numpy())
        ys = np.arange(1, len(xs) + 1) / len(xs)
        axes[1].plot(xs, ys, color='tab:blue', lw=2)
    axes[1].set_xlabel('Onset time since Mw 6.4 (hours)')
    axes[1].set_ylabel('Cumulative fraction')
    axes[1].set_title('Onset-time cumulative distribution')
    axes[1].grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(outpath, dpi=250)
    plt.close(fig)
    log(f'Saved figure: {outpath}')


def plot_onset_quality_map(grid_onset: pd.DataFrame, bounds: tuple[float, float, float, float], outpath: Path) -> None:
    fig, ax = plt.subplots(figsize=fig_size_from_bounds(bounds, base=11))
    style = {
        'robust onset': ('black', 10),
        'weak onset': ('tab:orange', 9),
        'no onset': ('lightgray', 8),
        'no events': ('white', 0),
    }
    for cls, (color, size) in style.items():
        sub = grid_onset.loc[grid_onset['confidence_class'] == cls]
        if len(sub) == 0 or size == 0:
            continue
        ax.scatter(sub['x_center_km'], sub['y_center_km'], s=size, c=color, alpha=0.8, label=cls)
    ax.set_xlabel('Local x (km)')
    ax.set_ylabel('Local y (km)')
    ax.set_title('Grid-cell onset confidence classes')
    ax.set_aspect('equal', adjustable='box')
    ax.legend(loc='best', fontsize=8)
    fig.tight_layout()
    fig.savefig(outpath, dpi=250)
    plt.close(fig)
    log(f'Saved figure: {outpath}')


def plot_example_cell_series(cell_time_series: pd.DataFrame, grid_onset: pd.DataFrame, time_bins: pd.DataFrame, outpath: Path) -> None:
    candidates = []
    activated = grid_onset.loc[np.isfinite(grid_onset['onset_minutes'])].sort_values('onset_minutes')
    if len(activated) > 0:
        candidates.append(int(activated.iloc[0]['cell_id']))
        candidates.append(int(activated.iloc[len(activated) // 2]['cell_id']))
        candidates.append(int(activated.iloc[-1]['cell_id']))
    no_onset = grid_onset.loc[(grid_onset['occupied']) & (~np.isfinite(grid_onset['onset_minutes']))].sort_values('total_cell_events', ascending=False)
    if len(no_onset) > 0:
        candidates.append(int(no_onset.iloc[0]['cell_id']))
    candidates = list(dict.fromkeys(candidates))[:EXAMPLE_SERIES_COUNT]
    if not candidates:
        return
    fig, axes = plt.subplots(len(candidates), 1, figsize=(10, 2.7 * len(candidates)), sharex=True)
    if len(candidates) == 1:
        axes = [axes]
    for ax, cell_id in zip(axes, candidates):
        ts = cell_time_series.loc[cell_time_series['cell_id'] == cell_id].sort_values('time_bin')
        meta = grid_onset.loc[grid_onset['cell_id'] == cell_id].iloc[0]
        hours = time_bins['bin_start_minutes'] / 60.0
        ax.bar(hours, ts['event_count'], width=TIME_BIN_MINUTES / 60.0 * 0.9, color='tab:blue', alpha=0.75)
        if np.isfinite(meta['onset_hours']):
            ax.axvline(meta['onset_hours'], color='red', lw=1.5, ls='--')
        ax.set_ylabel('Count/bin')
        ax.set_title(f'Cell {cell_id} | {meta["confidence_class"]} | total={int(meta["total_cell_events"])} | onset_h={meta["onset_hours"] if np.isfinite(meta["onset_hours"]) else "NA"}')
        ax.grid(True, alpha=0.25)
    axes[-1].set_xlabel('Hours since Mw 6.4')
    fig.tight_layout()
    fig.savefig(outpath, dpi=250)
    plt.close(fig)
    log(f'Saved figure: {outpath}')


def plot_onset_vs_distance(grid_onset: pd.DataFrame, main_df: pd.DataFrame, outpath: Path) -> None:
    ms64 = main_df.loc[main_df['mainshock_label'] == 'Mainshock64'].iloc[0]
    activated = grid_onset.loc[np.isfinite(grid_onset['onset_hours'])].copy()
    activated['distance_to_mw64_km'] = np.hypot(activated['x_center_km'] - ms64['x_km'], activated['y_center_km'] - ms64['y_km'])
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.scatter(activated['distance_to_mw64_km'], activated['onset_hours'], s=10, alpha=0.5, c='tab:blue')
    ax.set_xlabel('Distance from Mw 6.4 epicenter (km)')
    ax.set_ylabel('Onset time since Mw 6.4 (hours)')
    ax.set_title('Grid-cell onset time vs distance from Mw 6.4')
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(outpath, dpi=250)
    plt.close(fig)
    log(f'Saved figure: {outpath}')


def build_summary_tables(grid_onset: pd.DataFrame, main_df: pd.DataFrame, filtered_events: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    activated = grid_onset.loc[np.isfinite(grid_onset['onset_minutes'])].copy()
    thresholds_min = [30, 60, 120, 240]
    rows = []
    n_occ = int(grid_onset['occupied'].sum())
    n_act = len(activated)
    for thr in thresholds_min:
        count = int((activated['onset_minutes'] <= thr).sum())
        rows.append(
            {
                'metric': f'fraction_activated_within_{thr}_minutes',
                'value': float(count / n_occ) if n_occ > 0 else np.nan,
                'denominator_occupied_cells': n_occ,
                'numerator_activated_cells': count,
            }
        )
    if n_act > 0:
        for q in [0.1, 0.25, 0.5, 0.75, 0.9]:
            rows.append(
                {
                    'metric': f'onset_time_quantile_q{str(q).replace(".", "")}_hours',
                    'value': float(activated['onset_hours'].quantile(q)),
                    'denominator_occupied_cells': n_occ,
                    'numerator_activated_cells': n_act,
                }
            )
    ms64 = main_df.loc[main_df['mainshock_label'] == 'Mainshock64'].iloc[0]
    if n_act > 1:
        activated['distance_to_mw64_km'] = np.hypot(activated['x_center_km'] - ms64['x_km'], activated['y_center_km'] - ms64['y_km'])
        corr = activated[['distance_to_mw64_km', 'onset_hours']].corr(method='spearman').iloc[0, 1]
        rows.append(
            {
                'metric': 'spearman_onset_vs_distance_to_mw64',
                'value': float(corr),
                'denominator_occupied_cells': n_occ,
                'numerator_activated_cells': n_act,
            }
        )
    metrics = pd.DataFrame(rows)

    validation = pd.DataFrame([
        {'metric': 'filtered_events', 'value': int(len(filtered_events))},
        {'metric': 'occupied_grid_cells', 'value': int(grid_onset['occupied'].sum())},
        {'metric': 'activated_grid_cells', 'value': int(np.isfinite(grid_onset['onset_minutes']).sum())},
        {'metric': 'robust_onset_cells', 'value': int((grid_onset['confidence_class'] == 'robust onset').sum())},
        {'metric': 'weak_onset_cells', 'value': int((grid_onset['confidence_class'] == 'weak onset').sum())},
        {'metric': 'no_onset_occupied_cells', 'value': int(((grid_onset['occupied']) & (~np.isfinite(grid_onset['onset_minutes']))).sum())},
    ])
    return metrics, validation


def save_run_parameters(main_df: pd.DataFrame, crs_local: CRS, n_jobs: int, outpath: Path) -> None:
    t0 = main_df.loc[main_df['mainshock_label'] == 'Mainshock64', 'event_time'].iloc[0]
    t1 = main_df.loc[main_df['mainshock_label'] == 'Mainshock71', 'event_time'].iloc[0]
    params = pd.DataFrame([
        {'parameter': 'catalog_path', 'value': str(CATALOG_PATH)},
        {'parameter': 'mainshock_path', 'value': str(MAINSHOCK_PATH)},
        {'parameter': 'fault_path', 'value': str(FAULT_PATH)},
        {'parameter': 'output_dir', 'value': str(OUTPUT_DIR)},
        {'parameter': 'time_window_start_utc', 'value': str(t0)},
        {'parameter': 'time_window_end_utc', 'value': str(t1)},
        {'parameter': 'grid_spacing_km', 'value': GRID_SPACING_KM},
        {'parameter': 'buffer_km', 'value': BUFFER_KM},
        {'parameter': 'time_bin_minutes', 'value': TIME_BIN_MINUTES},
        {'parameter': 'onset_rule', 'value': 'first 30-minute bin with count>=2 and sustained activation defined by either candidate+next>=3 or candidate+next_two>=3 with nonzero post-candidate activity'},
        {'parameter': 'parallel_workers', 'value': n_jobs},
        {'parameter': 'local_projection', 'value': crs_local.to_proj4()},
    ])
    save_table(params, outpath)


def main() -> None:
    t_start = time.time()
    np.random.seed(RNG_SEED)
    prepare_output_dir(OUTPUT_DIR)
    n_jobs = min(MAX_CORES, max(1, (os.cpu_count() or 1)))
    log(f'Starting 01_grid_onset_analysis with n_jobs={n_jobs}')

    catalog_raw, main_raw, faults_raw = load_inputs()
    catalog, catalog_qc = validate_catalog(catalog_raw, 'catalog')
    main_clean, main_qc = validate_catalog(main_raw, 'mainshock table')
    faults, fault_qc = validate_faults(faults_raw)
    main_df = select_mainshocks(main_clean)
    to_local, to_geo, crs_local = build_local_transformer(main_df)
    study_region_df, bounds, fault_xs, fault_ys = build_study_region(faults, to_local)
    main_proj = add_mainshock_projection(main_df, to_local, bounds)
    filtered_events, filter_qc = filter_events(catalog, main_proj, bounds, to_local)
    if 'time_bin' in filtered_events.columns and len(time_bins := compute_time_bins(
        main_proj.loc[main_proj['mainshock_label'] == 'Mainshock64', 'event_time'].iloc[0],
        main_proj.loc[main_proj['mainshock_label'] == 'Mainshock71', 'event_time'].iloc[0],
    )) > 0:
        max_valid_bin = int(time_bins['time_bin'].max())
        bad_bin_mask = (filtered_events['time_bin'] < 0) | (filtered_events['time_bin'] > max_valid_bin)
        if bool(bad_bin_mask.any()):
            raise ValueError(f'Filtered events contain out-of-range time_bin values: {int(bad_bin_mask.sum())} rows')
    t0 = main_proj.loc[main_proj['mainshock_label'] == 'Mainshock64', 'event_time'].iloc[0]
    t1 = main_proj.loc[main_proj['mainshock_label'] == 'Mainshock71', 'event_time'].iloc[0]
    grid = build_grid(bounds, to_geo)
    assignments = assign_events_to_grid(filtered_events, grid, bounds)
    cell_time_series = build_cell_time_series(assignments, time_bins, n_jobs=n_jobs)
    grid_onset = compute_onset_table(cell_time_series, grid, assignments, n_jobs=n_jobs)

    qc_summary = pd.DataFrame([
        {'category': 'catalog', 'metric': k, 'value': v} for k, v in catalog_qc.items()
    ] + [
        {'category': 'mainshock_table', 'metric': k, 'value': v} for k, v in main_qc.items()
    ] + [
        {'category': 'faults', 'metric': k, 'value': v} for k, v in fault_qc.items()
    ] + [
        {'category': 'filtering', 'metric': k, 'value': v} for k, v in filter_qc.items()
    ])

    metrics_df, validation_df = build_summary_tables(grid_onset, main_proj, filtered_events)

    save_table(main_proj, OUTPUT_DIR / 'tables' / 'mainshock_reference_table.csv')
    save_table(study_region_df, OUTPUT_DIR / 'tables' / 'study_region_bounds.csv')
    save_table(qc_summary, OUTPUT_DIR / 'tables' / 'qc_summary.csv')
    save_table(filtered_events, OUTPUT_DIR / 'tables' / 'filtered_events.csv')
    save_table(time_bins, OUTPUT_DIR / 'tables' / 'time_bins.csv')
    save_table(grid, OUTPUT_DIR / 'tables' / 'grid_definition.csv')
    save_table(assignments, OUTPUT_DIR / 'tables' / 'event_to_cell_assignment.csv')
    save_table(cell_time_series, OUTPUT_DIR / 'tables' / 'cell_time_series.csv')
    save_table(grid_onset, OUTPUT_DIR / 'tables' / 'grid_cell_onset.csv')
    save_table(metrics_df, OUTPUT_DIR / 'tables' / 'grid_onset_metrics.csv')
    save_table(validation_df, OUTPUT_DIR / 'tables' / 'validation_summary.csv')
    save_run_parameters(main_proj, crs_local, n_jobs, OUTPUT_DIR / 'tables' / 'run_parameters.csv')

    plot_overview_map(filtered_events, main_proj, fault_xs, fault_ys, bounds, OUTPUT_DIR / 'figures' / 'study_region_overview.png')
    plot_occupied_cells(grid_onset, bounds, OUTPUT_DIR / 'figures' / 'occupied_cells_map.png')
    plot_event_total_hist(grid_onset, OUTPUT_DIR / 'figures' / 'occupied_cell_event_histogram.png')
    plot_total_rate(cell_time_series, time_bins, OUTPUT_DIR / 'figures' / 'study_area_seismicity_rate.png')
    plot_onset_map(grid_onset, main_proj, fault_xs, fault_ys, bounds, OUTPUT_DIR / 'figures' / 'grid_onset_map.png')
    plot_onset_histogram(grid_onset, OUTPUT_DIR / 'figures' / 'grid_onset_histogram_cdf.png')
    plot_onset_quality_map(grid_onset, bounds, OUTPUT_DIR / 'figures' / 'grid_onset_confidence_map.png')
    plot_example_cell_series(cell_time_series, grid_onset, time_bins, OUTPUT_DIR / 'figures' / 'example_cell_time_series.png')
    plot_onset_vs_distance(grid_onset, main_proj, OUTPUT_DIR / 'figures' / 'grid_onset_vs_distance_mw64.png')

    if len(filtered_events) == 0 or int(grid_onset['occupied'].sum()) == 0:
        raise RuntimeError('Main scientific outputs are empty: filtered_events or occupied grid cells')

    elapsed = time.time() - t_start
    log(f'Completed 01_grid_onset_analysis in {elapsed:.2f} s')


if __name__ == '__main__':
    try:
        main()
    except Exception:
        print(traceback.format_exc(), flush=True)
        sys.exit(1)
