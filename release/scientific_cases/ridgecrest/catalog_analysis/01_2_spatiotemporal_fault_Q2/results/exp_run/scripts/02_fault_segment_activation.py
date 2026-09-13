from __future__ import annotations

import json
import math
import shutil
import sys
import time
import traceback
import os
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.colors import Normalize
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd
from joblib import Parallel, delayed
from pyproj import CRS, Transformer
from scipy.spatial import cKDTree


CATALOG_PATH = Path('<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/TRACE_ridgecrest_relocated.csv')
MAINSHOCK_PATH = Path('<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/main_shock_events.csv')
FAULT_PATH = Path('<REPO_ROOT>/examples/ridgecrest/data/faults/ridgecrest_surface_faults.json')
SCRIPT_PATH = Path('<REPO_ROOT>/examples/ridgecrest/catalog_analysis/run/01_2_trigger_spatiotemporal_fault_Q2-v1/exp_run/scripts/02_fault_segment_activation.py')
OUTPUT_DIR = Path('<REPO_ROOT>/examples/ridgecrest/catalog_analysis/run/01_2_trigger_spatiotemporal_fault_Q2-v1/exp_run/outputs/02_fault_segment_activation')
ANTECEDENT_TABLE_DIR = Path('<REPO_ROOT>/examples/ridgecrest/catalog_analysis/run/01_2_trigger_spatiotemporal_fault_Q2-v1/exp_run/outputs/01_grid_onset_analysis/tables')

TIME_BIN_MINUTES = 30
SEGMENT_TARGET_LENGTH_KM = 1.0
ASSOCIATION_THRESHOLD_KM = 3.0
ACTIVATION_COUNT_THRESHOLD = 5
MAX_CORES = 64
EVENT_MAP_ALPHA = 0.15
EVENT_MAP_SIZE = 4.0
MAJOR_FAULT_MIN_ACTIVATED_SEGMENTS = 8
RANDOM_SEED = 42
ASSOCIATION_CHUNK_SIZE = 250
FAULT_SEGMENT_CHUNK_SIZE = 500


def log(message: str) -> None:
    print(f'[{time.strftime("%Y-%m-%d %H:%M:%S")}] {message}', flush=True)


def prepare_output_dir(output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    for child in output_dir.iterdir():
        if child.is_file() and child.suffix.lower() in {'.csv', '.json', '.png', '.txt'}:
            child.unlink()
        elif child.is_dir() and child.name in {'tables', 'figures'}:
            shutil.rmtree(child)
    table_dir = output_dir / 'tables'
    fig_dir = output_dir / 'figures'
    table_dir.mkdir(parents=True, exist_ok=True)
    fig_dir.mkdir(parents=True, exist_ok=True)
    return table_dir, fig_dir


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
    if 'event_id' not in work.columns:
        work['event_id'] = np.arange(len(work), dtype=np.int64)
    qc['retained_rows'] = int(len(work))
    return work, qc


def require_columns(df: pd.DataFrame, required: list[str], df_name: str) -> None:
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f'{df_name} missing required columns: {missing}')


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
        arr = arr[np.isfinite(arr).all(axis=1)]
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


def load_mainshocks() -> pd.DataFrame:
    df = pd.read_csv(MAINSHOCK_PATH)
    df, _ = validate_catalog(df, 'mainshock_reference')
    mags = df['magnitude'].round(1)
    ms64 = df.loc[np.isclose(mags, 6.4)]
    ms71 = df.loc[np.isclose(mags, 7.1)]
    if len(ms64) != 1 or len(ms71) != 1:
        raise ValueError('Failed to identify unique Mw 6.4 and Mw 7.1 mainshocks from main_shock_events.csv')
    out = pd.concat([ms64, ms71], ignore_index=True).sort_values('event_time').reset_index(drop=True)
    out['mainshock_label'] = ['Mainshock64', 'Mainshock71']
    return out


def load_filtered_events() -> pd.DataFrame:
    path = ANTECEDENT_TABLE_DIR / 'filtered_events.csv'
    if not path.exists():
        raise FileNotFoundError(f'Missing antecedent filtered events table: {path}')
    events = pd.read_csv(path)
    events, _ = validate_catalog(events, 'filtered_events')
    for col in ['x_km', 'y_km', 'elapsed_minutes', 'elapsed_hours', 'time_bin']:
        if col not in events.columns:
            raise ValueError(f'filtered_events.csv missing required downstream column: {col}')
    events['x_km'] = pd.to_numeric(events['x_km'], errors='raise')
    events['y_km'] = pd.to_numeric(events['y_km'], errors='raise')
    events['elapsed_minutes'] = pd.to_numeric(events['elapsed_minutes'], errors='raise')
    events['elapsed_hours'] = pd.to_numeric(events['elapsed_hours'], errors='raise')
    events['time_bin'] = pd.to_numeric(events['time_bin'], errors='raise').astype(int)
    return events.sort_values('event_time').reset_index(drop=True)


def load_time_bins() -> pd.DataFrame:
    path = ANTECEDENT_TABLE_DIR / 'time_bins.csv'
    if not path.exists():
        raise FileNotFoundError(f'Missing antecedent time_bins table: {path}')
    df = pd.read_csv(path)
    required = ['time_bin', 'bin_start_utc', 'bin_end_utc', 'bin_center_minutes', 'bin_start_minutes', 'bin_end_minutes']
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f'time_bins.csv missing required columns: {missing}')
    df['time_bin'] = pd.to_numeric(df['time_bin'], errors='raise').astype(int)
    df['bin_start_utc'] = pd.to_datetime(df['bin_start_utc'], utc=True)
    df['bin_end_utc'] = pd.to_datetime(df['bin_end_utc'], utc=True)
    return df.sort_values('time_bin').reset_index(drop=True)


def load_faults_projected(to_local: Transformer) -> list[np.ndarray]:
    with FAULT_PATH.open('r', encoding='utf-8') as f:
        faults_raw = json.load(f)
    faults_geo, _ = validate_faults(faults_raw)
    projected = []
    for arr in faults_geo:
        x, y = project_xy(arr[:, 0], arr[:, 1], to_local)
        projected.append(np.column_stack([x, y]))
    return projected


def compute_orientation_strike(x0: float, y0: float, x1: float, y1: float) -> float:
    dx = x1 - x0
    dy = y1 - y0
    angle = (90.0 - math.degrees(math.atan2(dy, dx))) % 360.0
    strike = angle % 180.0
    return strike


def segment_single_polyline(line_id: int, xy: np.ndarray, to_geo: Transformer) -> list[dict]:
    diffs = np.diff(xy, axis=0)
    seglens = np.sqrt((diffs ** 2).sum(axis=1))
    cum = np.concatenate([[0.0], np.cumsum(seglens)])
    total_length = float(cum[-1])
    if total_length <= 0.0:
        return []

    if total_length <= SEGMENT_TARGET_LENGTH_KM:
        positions = np.array([0.0, total_length], dtype=float)
    else:
        n_segments = max(1, int(math.ceil(total_length / SEGMENT_TARGET_LENGTH_KM)))
        positions = np.linspace(0.0, total_length, n_segments + 1)

    x_interp = np.interp(positions, cum, xy[:, 0])
    y_interp = np.interp(positions, cum, xy[:, 1])

    records = []
    for idx in range(len(positions) - 1):
        x0 = float(x_interp[idx])
        y0 = float(y_interp[idx])
        x1 = float(x_interp[idx + 1])
        y1 = float(y_interp[idx + 1])
        length_km = float(math.hypot(x1 - x0, y1 - y0))
        if length_km <= 0.0:
            continue
        xm = 0.5 * (x0 + x1)
        ym = 0.5 * (y0 + y1)
        lon0, lat0 = to_geo.transform(x0, y0)
        lon1, lat1 = to_geo.transform(x1, y1)
        lonm, latm = to_geo.transform(xm, ym)
        strike = compute_orientation_strike(x0, y0, x1, y1)
        records.append(
            {
                'line_id': int(line_id),
                'segment_id': int(idx),
                'global_segment_id': -1,
                'line_segment_count': int(len(positions) - 1),
                'line_total_length_km': total_length,
                'segment_length_km': length_km,
                'start_x_km': x0,
                'start_y_km': y0,
                'end_x_km': x1,
                'end_y_km': y1,
                'mid_x_km': xm,
                'mid_y_km': ym,
                'start_lon': lon0,
                'start_lat': lat0,
                'end_lon': lon1,
                'end_lat': lat1,
                'mid_lon': lonm,
                'mid_lat': latm,
                'along_line_start_km': float(positions[idx]),
                'along_line_end_km': float(positions[idx + 1]),
                'along_line_mid_km': float(0.5 * (positions[idx] + positions[idx + 1])),
                'raw_azimuth_deg': float((math.degrees(math.atan2(y1 - y0, x1 - x0)) + 360.0) % 360.0),
                'strike_deg': float(strike),
            }
        )
    return records


def build_fault_segments(projected_faults: list[np.ndarray], to_geo: Transformer) -> pd.DataFrame:
    n_jobs = min(MAX_CORES, max(1, len(projected_faults)))
    log(f'Discretizing {len(projected_faults)} fault polylines into ~{SEGMENT_TARGET_LENGTH_KM:.1f} km segments with n_jobs={n_jobs}')
    chunk_size = FAULT_SEGMENT_CHUNK_SIZE
    all_records: list[dict] = []
    for start in range(0, len(projected_faults), chunk_size):
        stop = min(len(projected_faults), start + chunk_size)
        log(f'  segmenting polyline chunk {start}:{stop}')
        chunk_records = Parallel(n_jobs=n_jobs, prefer='threads')(
            delayed(segment_single_polyline)(line_id, projected_faults[line_id], to_geo)
            for line_id in range(start, stop)
        )
        for recs in chunk_records:
            all_records.extend(recs)
    if not all_records:
        raise ValueError('No fault segments were generated from the provided fault polylines')
    df = pd.DataFrame(all_records)
    df = df.sort_values(['line_id', 'segment_id']).reset_index(drop=True)
    df['global_segment_id'] = np.arange(len(df), dtype=np.int64)
    return df


def point_to_segment_distance(px: np.ndarray, py: np.ndarray, x0: np.ndarray, y0: np.ndarray, x1: np.ndarray, y1: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    vx = x1 - x0
    vy = y1 - y0
    wx = px[:, None] - x0[None, :]
    wy = py[:, None] - y0[None, :]
    denom = vx * vx + vy * vy
    denom = np.where(denom <= 0.0, 1.0, denom)
    t = (wx * vx[None, :] + wy * vy[None, :]) / denom[None, :]
    t = np.clip(t, 0.0, 1.0)
    projx = x0[None, :] + t * vx[None, :]
    projy = y0[None, :] + t * vy[None, :]
    dx = px[:, None] - projx
    dy = py[:, None] - projy
    d2 = dx * dx + dy * dy
    idx = np.argmin(d2, axis=1)
    dist = np.sqrt(d2[np.arange(len(px)), idx])
    t_best = t[np.arange(len(px)), idx]
    return dist, idx.astype(np.int64), t_best


def associate_event_chunk(chunk: pd.DataFrame, segment_lookup: pd.DataFrame, tree: cKDTree, candidate_radius_km: float) -> pd.DataFrame:
    px = chunk['x_km'].to_numpy(dtype=float)
    py = chunk['y_km'].to_numpy(dtype=float)
    candidate_lists = tree.query_ball_point(np.column_stack([px, py]), r=candidate_radius_km)

    seg_x0 = segment_lookup['start_x_km'].to_numpy(dtype=float)
    seg_y0 = segment_lookup['start_y_km'].to_numpy(dtype=float)
    seg_x1 = segment_lookup['end_x_km'].to_numpy(dtype=float)
    seg_y1 = segment_lookup['end_y_km'].to_numpy(dtype=float)
    seg_len = segment_lookup['segment_length_km'].to_numpy(dtype=float)

    rows = []
    for local_i, (_, ev) in enumerate(chunk.iterrows()):
        cand = candidate_lists[local_i]
        if not cand:
            _, nearest_mid_idx = tree.query([px[local_i], py[local_i]], k=1)
            if np.isscalar(nearest_mid_idx):
                cand = [int(nearest_mid_idx)]
            else:
                cand = [int(nearest_mid_idx[0])]
        cand = np.asarray(sorted(set(int(i) for i in cand)), dtype=np.int64)
        dist, idx_local, t_best = point_to_segment_distance(
            np.asarray([px[local_i]]),
            np.asarray([py[local_i]]),
            seg_x0[cand],
            seg_y0[cand],
            seg_x1[cand],
            seg_y1[cand],
        )
        best_local = int(idx_local[0])
        best_tree_idx = int(cand[best_local])
        best = segment_lookup.iloc[best_tree_idx]
        along_km = float(best['along_line_start_km'] + t_best[0] * seg_len[best_tree_idx])
        distance_km = float(dist[0])
        rows.append(
            {
                'event_id': int(ev['event_id']),
                'event_time': ev['event_time'],
                'latitude': float(ev['latitude']),
                'longitude': float(ev['longitude']),
                'depth_km': float(ev['depth_km']),
                'magnitude': float(ev['magnitude']),
                'x_km': float(ev['x_km']),
                'y_km': float(ev['y_km']),
                'elapsed_minutes': float(ev['elapsed_minutes']),
                'elapsed_hours': float(ev['elapsed_hours']),
                'time_bin': int(ev['time_bin']),
                'nearest_line_id': int(best['line_id']),
                'nearest_segment_id': int(best['segment_id']),
                'global_segment_id': int(best['global_segment_id']),
                'segment_strike_deg': float(best['strike_deg']),
                'segment_mid_x_km': float(best['mid_x_km']),
                'segment_mid_y_km': float(best['mid_y_km']),
                'distance_to_segment_km': distance_km,
                'along_line_position_km': along_km,
                'assigned_to_segment': bool(distance_km < ASSOCIATION_THRESHOLD_KM),
            }
        )
    return pd.DataFrame(rows)


def associate_events_to_segments(events: pd.DataFrame, segments: pd.DataFrame) -> pd.DataFrame:
    require_columns(events, ['event_id', 'x_km', 'y_km', 'elapsed_minutes', 'elapsed_hours', 'time_bin'], 'events for association')
    require_columns(
        segments,
        [
            'global_segment_id', 'line_id', 'segment_id', 'start_x_km', 'start_y_km',
            'end_x_km', 'end_y_km', 'mid_x_km', 'mid_y_km', 'strike_deg',
            'segment_length_km', 'along_line_start_km'
        ],
        'fault segments'
    )
    tree = cKDTree(segments[['mid_x_km', 'mid_y_km']].to_numpy(dtype=float))
    segment_lookup = segments.reset_index(drop=True)
    max_half_len = float(0.5 * segments['segment_length_km'].max())
    candidate_radius_km = ASSOCIATION_THRESHOLD_KM + max_half_len + 0.25
    n_jobs = min(MAX_CORES, max(1, os_cpu_count_safe()))
    chunks = [events.iloc[i:i + ASSOCIATION_CHUNK_SIZE].copy() for i in range(0, len(events), ASSOCIATION_CHUNK_SIZE)]
    n_parallel = max(1, min(n_jobs, len(chunks)))
    log(
        f'Associating {len(events)} events to {len(segments)} segments with '
        f'n_jobs={n_parallel}, n_chunks={len(chunks)}, chunk_size={ASSOCIATION_CHUNK_SIZE}, '
        f'candidate_radius_km={candidate_radius_km:.2f}'
    )
    results = Parallel(n_jobs=n_parallel, prefer='threads')(
        delayed(associate_event_chunk)(chunk, segment_lookup, tree, candidate_radius_km)
        for chunk in chunks if len(chunk) > 0
    )
    assoc = pd.concat(results, ignore_index=True)
    assoc = assoc.sort_values('event_id').reset_index(drop=True)
    if assoc['event_id'].nunique() != len(events) or len(assoc) != len(events):
        raise ValueError('Event-to-segment association did not preserve one output row per input event')
    require_columns(
        assoc,
        ['event_id', 'global_segment_id', 'distance_to_segment_km', 'assigned_to_segment', 'nearest_line_id', 'nearest_segment_id'],
        'event_to_fault_segment_association'
    )
    return assoc


def os_cpu_count_safe() -> int:
    value = os.cpu_count() or 1
    return max(1, value)


def build_segment_time_series(associations: pd.DataFrame, segments: pd.DataFrame, time_bins: pd.DataFrame) -> pd.DataFrame:
    require_columns(associations, ['global_segment_id', 'time_bin', 'assigned_to_segment'], 'associations')
    require_columns(time_bins, ['time_bin', 'bin_start_utc', 'bin_end_utc', 'bin_center_minutes', 'bin_start_minutes', 'bin_end_minutes'], 'time_bins')
    require_columns(segments, ['global_segment_id', 'line_id', 'segment_id', 'strike_deg', 'along_line_mid_km', 'mid_x_km', 'mid_y_km', 'mid_lon', 'mid_lat'], 'segments for time series')
    assigned = associations.loc[associations['assigned_to_segment']].copy()
    if assigned.empty:
        raise ValueError('No events were assigned within the 3 km threshold; cannot build segment time series')
    n_time_bins = int(time_bins['time_bin'].max()) + 1
    counts = (
        assigned.groupby(['global_segment_id', 'time_bin'])
        .size()
        .rename('event_count')
        .reset_index()
    )
    active_segments = np.sort(counts['global_segment_id'].unique())
    full_index = pd.MultiIndex.from_product([active_segments, np.arange(n_time_bins, dtype=int)], names=['global_segment_id', 'time_bin'])
    counts = counts.set_index(['global_segment_id', 'time_bin']).reindex(full_index, fill_value=0).reset_index()
    counts['rate_events_per_hour'] = counts['event_count'] * (60.0 / TIME_BIN_MINUTES)
    counts['cumulative_count'] = counts.groupby('global_segment_id')['event_count'].cumsum()
    counts = counts.merge(
        segments[['global_segment_id', 'line_id', 'segment_id', 'strike_deg', 'along_line_mid_km', 'mid_x_km', 'mid_y_km', 'mid_lon', 'mid_lat']],
        on='global_segment_id',
        how='left',
        validate='many_to_one',
    )
    counts = counts.merge(
        time_bins[['time_bin', 'bin_start_utc', 'bin_end_utc', 'bin_center_minutes', 'bin_start_minutes', 'bin_end_minutes']],
        on='time_bin',
        how='left',
        validate='many_to_one',
    )
    require_columns(
        counts,
        [
            'global_segment_id', 'time_bin', 'event_count', 'rate_events_per_hour', 'cumulative_count',
            'line_id', 'segment_id', 'strike_deg', 'along_line_mid_km', 'bin_start_minutes'
        ],
        'fault_segment_time_series'
    )
    return counts


def summarize_segment_activation(segment_ts: pd.DataFrame, associations: pd.DataFrame, segments: pd.DataFrame) -> pd.DataFrame:
    require_columns(segment_ts, ['global_segment_id', 'time_bin', 'event_count', 'rate_events_per_hour', 'bin_start_minutes', 'cumulative_count'], 'segment time series')
    require_columns(associations, ['global_segment_id', 'assigned_to_segment', 'event_time', 'elapsed_minutes', 'event_id'], 'associations for summary')
    require_columns(segments, ['global_segment_id', 'line_id', 'segment_id'], 'segments for summary')
    assigned = associations.loc[associations['assigned_to_segment']].copy()
    first_event = (
        assigned.groupby('global_segment_id')
        .agg(
            first_associated_event_time=('event_time', 'min'),
            first_associated_event_elapsed_minutes=('elapsed_minutes', 'min'),
            total_associated_events=('event_id', 'size'),
        )
        .reset_index()
    )
    activation_rows = []
    for seg_id, grp in segment_ts.groupby('global_segment_id', sort=False):
        grp = grp.sort_values('time_bin').reset_index(drop=True)
        activation_mask = grp['event_count'] >= ACTIVATION_COUNT_THRESHOLD
        if activation_mask.any():
            act_row = grp.loc[activation_mask.idxmax()]
            activation_bin = int(act_row['time_bin'])
            activation_minutes = float(act_row['bin_start_minutes'])
            activation_hours = activation_minutes / 60.0
            activated = True
        else:
            activation_bin = np.nan
            activation_minutes = np.nan
            activation_hours = np.nan
            activated = False
        peak_idx = grp['event_count'].to_numpy().argmax()
        peak_row = grp.iloc[int(peak_idx)]
        activation_rows.append(
            {
                'global_segment_id': int(seg_id),
                'activated': bool(activated),
                'activation_bin': activation_bin,
                'activation_minutes': activation_minutes,
                'activation_hours': activation_hours,
                'peak_count': int(peak_row['event_count']),
                'peak_rate_events_per_hour': float(peak_row['rate_events_per_hour']),
                'peak_bin': int(peak_row['time_bin']),
                'peak_bin_start_minutes': float(peak_row['bin_start_minutes']),
                'max_cumulative_count': int(grp['cumulative_count'].max()),
            }
        )
    activation = pd.DataFrame(activation_rows)
    summary = segments.merge(first_event, on='global_segment_id', how='left', validate='one_to_one')
    summary = summary.merge(activation, on='global_segment_id', how='left', validate='one_to_one')
    summary['total_associated_events'] = summary['total_associated_events'].fillna(0).astype(int)
    summary['first_associated_event_elapsed_hours'] = summary['first_associated_event_elapsed_minutes'] / 60.0
    summary['activation_delay_from_first_event_minutes'] = summary['activation_minutes'] - summary['first_associated_event_elapsed_minutes']
    summary['activation_delay_from_first_event_hours'] = summary['activation_delay_from_first_event_minutes'] / 60.0
    summary['activation_threshold_count_per_bin'] = ACTIVATION_COUNT_THRESHOLD
    summary['activation_threshold_rate_per_hour'] = ACTIVATION_COUNT_THRESHOLD * (60.0 / TIME_BIN_MINUTES)
    summary['ever_associated'] = summary['total_associated_events'] > 0
    summary['activated'] = summary['activated'].fillna(False)
    require_columns(
        summary,
        [
            'global_segment_id', 'line_id', 'segment_id', 'ever_associated', 'activated',
            'activation_bin', 'activation_minutes', 'activation_hours', 'total_associated_events'
        ],
        'fault_segment_activation_summary'
    )
    return summary.sort_values(['line_id', 'segment_id']).reset_index(drop=True)


def build_activation_density(summary: pd.DataFrame, time_bins: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    require_columns(summary, ['activated', 'activation_bin', 'strike_deg'], 'summary for activation density')
    require_columns(time_bins, ['time_bin', 'bin_start_minutes', 'bin_center_minutes'], 'time_bins for activation density')
    activated = summary.loc[summary['activated'] & summary['activation_bin'].notna()].copy()
    new_counts = pd.DataFrame({'time_bin': time_bins['time_bin'].to_numpy(dtype=int)})
    if activated.empty:
        new_counts['newly_activated_segments'] = 0
    else:
        counts = activated.groupby('activation_bin').size().rename('newly_activated_segments').reset_index()
        counts = counts.rename(columns={'activation_bin': 'time_bin'})
        new_counts = new_counts.merge(counts, on='time_bin', how='left')
        new_counts['newly_activated_segments'] = new_counts['newly_activated_segments'].fillna(0).astype(int)
    new_counts['cumulative_activated_segments'] = new_counts['newly_activated_segments'].cumsum()
    total_segments = int(len(summary))
    total_active = int(summary['activated'].sum())
    new_counts['fraction_of_all_segments'] = new_counts['newly_activated_segments'] / max(total_segments, 1)
    new_counts['fraction_of_activated_segments'] = new_counts['newly_activated_segments'] / max(total_active, 1)
    new_counts = new_counts.merge(time_bins, on='time_bin', how='left', validate='one_to_one')

    strike_bins = np.arange(0.0, 181.0, 5.0)
    time_ids = time_bins['time_bin'].to_numpy(dtype=int)
    strike_hist = np.zeros((len(strike_bins) - 1, len(time_ids)), dtype=int)
    if not activated.empty:
        t_idx = activated['activation_bin'].astype(int).to_numpy()
        s_idx = np.clip(np.digitize(activated['strike_deg'].to_numpy(), strike_bins, right=False) - 1, 0, len(strike_bins) - 2)
        for si, ti in zip(s_idx, t_idx):
            if 0 <= ti < len(time_ids):
                strike_hist[si, ti] += 1
    strike_df = pd.DataFrame(
        strike_hist,
        index=[0.5 * (strike_bins[i] + strike_bins[i + 1]) for i in range(len(strike_bins) - 1)],
        columns=time_ids,
    )
    strike_long = strike_df.stack().rename('activated_segment_count').reset_index()
    strike_long.columns = ['strike_bin_center_deg', 'time_bin', 'activated_segment_count']
    strike_long = strike_long.merge(time_bins[['time_bin', 'bin_start_minutes', 'bin_center_minutes']], on='time_bin', how='left')
    strike_long['normalized_density'] = strike_long['activated_segment_count'] / max(total_active, 1)
    return new_counts, strike_df, strike_long


def build_line_activation_raster(summary: pd.DataFrame, time_bins: pd.DataFrame) -> pd.DataFrame:
    require_columns(summary, ['activated', 'line_id', 'along_line_mid_km', 'activation_bin', 'global_segment_id'], 'summary for raster')
    require_columns(time_bins, ['time_bin', 'bin_start_minutes'], 'time_bins for raster')
    activated = summary.loc[summary['activated']].copy()
    if activated.empty:
        return pd.DataFrame(columns=['line_id', 'rank_position', 'global_segment_id', 'activation_bin', 'bin_start_minutes', 'along_line_mid_km'])
    eligible_lines = activated.groupby('line_id').size()
    eligible_lines = eligible_lines.loc[eligible_lines >= MAJOR_FAULT_MIN_ACTIVATED_SEGMENTS].index.to_numpy(dtype=int)
    if len(eligible_lines) == 0:
        eligible_lines = activated.groupby('line_id').size().sort_values(ascending=False).head(10).index.to_numpy(dtype=int)
    out = activated.loc[activated['line_id'].isin(eligible_lines)].copy()
    out = out.sort_values(['line_id', 'along_line_mid_km']).reset_index(drop=True)
    out['rank_position'] = out.groupby('line_id').cumcount()
    out = out.merge(time_bins[['time_bin', 'bin_start_minutes']], left_on='activation_bin', right_on='time_bin', how='left')
    out = out.drop(columns=['time_bin'])
    return out


def save_qc_summary(path: Path, rows: list[dict]) -> None:
    pd.DataFrame(rows).to_csv(path, index=False)


def plot_segments_by_line(segments: pd.DataFrame, mainshocks: pd.DataFrame, fig_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(11, 10))
    sample = segments.copy()
    n_lines = sample['line_id'].nunique()
    cmap = plt.cm.get_cmap('tab20', min(20, max(1, n_lines)))
    lines = []
    colors = []
    for _, row in sample.iterrows():
        lines.append([(row['start_x_km'], row['start_y_km']), (row['end_x_km'], row['end_y_km'])])
        colors.append(cmap(int(row['line_id']) % cmap.N))
    lc = LineCollection(lines, colors=colors, linewidths=0.8, alpha=0.9)
    ax.add_collection(lc)
    for _, row in mainshocks.iterrows():
        marker = '*' if row['mainshock_label'] == 'Mainshock64' else 'P'
        color = 'gold' if row['mainshock_label'] == 'Mainshock64' else 'red'
        ax.scatter(row['x_km'], row['y_km'], marker=marker, s=220, c=color, edgecolors='k', linewidths=0.7, zorder=5)
    ax.set_aspect('equal', adjustable='box')
    ax.set_xlabel('X (km)')
    ax.set_ylabel('Y (km)')
    ax.set_title('Discretized Ridgecrest fault segments colored by parent line ID')
    ax.grid(alpha=0.25, linestyle=':')
    fig.tight_layout()
    fig.savefig(fig_path, dpi=220)
    plt.close(fig)


def plot_segment_length_histogram(segments: pd.DataFrame, fig_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(segments['segment_length_km'], bins=40, color='steelblue', edgecolor='black', alpha=0.85)
    ax.axvline(SEGMENT_TARGET_LENGTH_KM, color='red', linestyle='--', linewidth=1.5, label='target length')
    ax.set_xlabel('Segment length (km)')
    ax.set_ylabel('Count')
    ax.set_title('Fault segment length distribution')
    ax.legend()
    ax.grid(alpha=0.25, linestyle=':')
    fig.tight_layout()
    fig.savefig(fig_path, dpi=220)
    plt.close(fig)


def plot_strike_distribution(segments: pd.DataFrame, fig_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(segments['strike_deg'], bins=np.arange(0, 185, 5), color='darkslateblue', edgecolor='black', alpha=0.85)
    ax.set_xlabel('Orientation-corrected strike (deg, 0-180)')
    ax.set_ylabel('Segment count')
    ax.set_title('Fault segment strike distribution')
    ax.grid(alpha=0.25, linestyle=':')
    fig.tight_layout()
    fig.savefig(fig_path, dpi=220)
    plt.close(fig)


def plot_association_distance_histogram(assoc: pd.DataFrame, fig_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(assoc['distance_to_segment_km'], bins=50, color='seagreen', edgecolor='black', alpha=0.85)
    ax.axvline(ASSOCIATION_THRESHOLD_KM, color='red', linestyle='--', linewidth=1.5, label='association threshold')
    ax.set_xlabel('Nearest fault-segment distance (km)')
    ax.set_ylabel('Event count')
    ax.set_title('Nearest event-to-segment distance distribution')
    ax.legend()
    ax.grid(alpha=0.25, linestyle=':')
    fig.tight_layout()
    fig.savefig(fig_path, dpi=220)
    plt.close(fig)


def plot_associated_vs_unassociated(segments: pd.DataFrame, assoc: pd.DataFrame, mainshocks: pd.DataFrame, fig_path: Path) -> None:
    fig = plt.figure(figsize=(15, 9))
    gs = fig.add_gridspec(2, 2, width_ratios=[2.35, 1.0], height_ratios=[1.0, 1.0], wspace=0.22, hspace=0.22)
    ax_map = fig.add_subplot(gs[:, 0])
    ax_hist = fig.add_subplot(gs[0, 1])
    ax_bar = fig.add_subplot(gs[1, 1])

    lines = [[(r['start_x_km'], r['start_y_km']), (r['end_x_km'], r['end_y_km'])] for _, r in segments.iterrows()]
    lc = LineCollection(lines, colors='0.45', linewidths=0.8, alpha=0.85, zorder=1)
    ax_map.add_collection(lc)

    unassoc = assoc.loc[~assoc['assigned_to_segment']].copy()
    assigned = assoc.loc[assoc['assigned_to_segment']].copy()

    if not unassoc.empty:
        ax_map.scatter(
            unassoc['x_km'], unassoc['y_km'], s=10, c='darkorange', alpha=0.65,
            edgecolors='none', zorder=3
        )
    if not assigned.empty:
        ax_map.scatter(
            assigned['x_km'], assigned['y_km'], s=6, c='navy', alpha=0.20,
            edgecolors='none', zorder=2
        )

    mainshock_handles = []
    for _, row in mainshocks.iterrows():
        if row['mainshock_label'] == 'Mainshock64':
            marker = '*'
            color = 'gold'
            label = 'Mw 6.4 mainshock'
        else:
            marker = 'P'
            color = 'red'
            label = 'Mw 7.1 mainshock'
        ax_map.scatter(row['x_km'], row['y_km'], marker=marker, s=240, c=color, edgecolors='k', linewidths=0.8, zorder=5)
        ax_map.text(row['x_km'] + 0.45, row['y_km'] + 0.45, row['mainshock_label'], fontsize=9, weight='bold')
        mainshock_handles.append(Line2D([0], [0], marker=marker, color='w', label=label, markerfacecolor=color, markeredgecolor='k', markersize=12, linewidth=0))

    legend_handles = [
        Line2D([0], [0], color='0.45', lw=1.6, label='Fault segments'),
        Line2D([0], [0], marker='o', color='w', label=f'Associated events (n={len(assigned)})', markerfacecolor='navy', markeredgecolor='none', markersize=7, alpha=0.7),
        Line2D([0], [0], marker='o', color='w', label=f'Unassociated events (n={len(unassoc)})', markerfacecolor='darkorange', markeredgecolor='none', markersize=7, alpha=0.9),
    ] + mainshock_handles
    ax_map.legend(handles=legend_handles, loc='upper right', frameon=True, framealpha=0.95)

    ax_map.set_aspect('equal', adjustable='box')
    ax_map.set_xlabel('X (km)')
    ax_map.set_ylabel('Y (km)')
    ax_map.set_title('Associated vs unassociated events relative to discretized fault segments')
    ax_map.grid(alpha=0.25, linestyle=':')

    bins = np.linspace(0.0, max(float(assoc['distance_to_segment_km'].max()), ASSOCIATION_THRESHOLD_KM), 40)
    ax_hist.hist(assoc['distance_to_segment_km'], bins=bins, color='0.70', edgecolor='0.25', alpha=0.9)
    ax_hist.axvline(ASSOCIATION_THRESHOLD_KM, color='red', linestyle='--', linewidth=1.5, label='3 km threshold')
    ax_hist.set_xlabel('Nearest segment distance (km)')
    ax_hist.set_ylabel('Event count')
    ax_hist.set_title('Nearest-distance comparison summary')
    ax_hist.legend(loc='upper right', frameon=True)
    ax_hist.grid(alpha=0.25, linestyle=':')

    counts = np.array([len(assigned), len(unassoc)], dtype=int)
    fractions = counts / max(len(assoc), 1)
    labels = ['Associated', 'Unassociated']
    colors = ['navy', 'darkorange']
    bars = ax_bar.bar(labels, counts, color=colors, alpha=0.9, edgecolor='black', linewidth=0.7)
    for bar, count, frac in zip(bars, counts, fractions):
        ax_bar.text(bar.get_x() + bar.get_width() / 2.0, bar.get_height() + max(counts) * 0.02, f'{count}\n({frac:.1%})', ha='center', va='bottom', fontsize=10)
    ax_bar.set_ylabel('Number of events')
    ax_bar.set_title('Assignment outcome summary')
    ax_bar.grid(axis='y', alpha=0.25, linestyle=':')

    fig.tight_layout()
    fig.savefig(fig_path, dpi=220)
    plt.close(fig)


def plot_activation_map(summary: pd.DataFrame, assoc: pd.DataFrame, mainshocks: pd.DataFrame, fig_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(11, 10))
    activated = summary.loc[summary['activated'] & summary['activation_minutes'].notna()].copy()
    inactive = summary.loc[~summary['activated'] | summary['activation_minutes'].isna()].copy()
    if not inactive.empty:
        lines = [[(r['start_x_km'], r['start_y_km']), (r['end_x_km'], r['end_y_km'])] for _, r in inactive.iterrows()]
        ax.add_collection(LineCollection(lines, colors='0.8', linewidths=0.7, alpha=0.7, zorder=1))
    if not activated.empty:
        vmin = float(activated['activation_minutes'].min())
        vmax = float(activated['activation_minutes'].max())
        if math.isclose(vmin, vmax):
            vmax = vmin + TIME_BIN_MINUTES
        norm = Normalize(vmin=vmin, vmax=vmax)
        cmap = plt.cm.Greys_r
        lines = [[(r['start_x_km'], r['start_y_km']), (r['end_x_km'], r['end_y_km'])] for _, r in activated.iterrows()]
        colors = cmap(norm(activated['activation_minutes'].to_numpy()))
        lc = LineCollection(lines, colors=colors, linewidths=2.0, alpha=0.95, zorder=3)
        ax.add_collection(lc)
        sm = plt.cm.ScalarMappable(norm=norm, cmap=cmap)
        cbar = fig.colorbar(sm, ax=ax, pad=0.02, shrink=0.82)
        cbar.set_label('Segment activation time since Mw 6.4 (minutes)')
    assigned = assoc.loc[assoc['assigned_to_segment']].copy()
    if not assigned.empty:
        event_colors = 'black'
        ax.scatter(assigned['x_km'], assigned['y_km'], s=EVENT_MAP_SIZE, c=event_colors, alpha=EVENT_MAP_ALPHA, linewidths=0, zorder=2)
    for _, row in mainshocks.iterrows():
        marker = '*' if row['mainshock_label'] == 'Mainshock64' else 'P'
        color = 'gold' if row['mainshock_label'] == 'Mainshock64' else 'red'
        ax.scatter(row['x_km'], row['y_km'], marker=marker, s=240, c=color, edgecolors='k', linewidths=0.8, zorder=5)
        ax.text(row['x_km'] + 0.4, row['y_km'] + 0.4, row['mainshock_label'], fontsize=9, weight='bold')
    ax.set_aspect('equal', adjustable='box')
    ax.set_xlabel('X (km)')
    ax.set_ylabel('Y (km)')
    ax.set_title('Fault-segment activation sequence between Mw 6.4 and Mw 7.1')
    ax.grid(alpha=0.25, linestyle=':')
    fig.tight_layout()
    fig.savefig(fig_path, dpi=220)
    plt.close(fig)


def plot_activation_counts(new_counts: pd.DataFrame, fig_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(10, 5))
    x = new_counts['bin_center_minutes'] / 60.0
    y = new_counts['newly_activated_segments']
    sc = ax.scatter(x, y, c=y, cmap='viridis', s=45, edgecolors='none')
    ax.plot(x, y, color='0.35', linewidth=0.9, alpha=0.8)
    cbar = fig.colorbar(sc, ax=ax, pad=0.02)
    cbar.set_label('Newly activated segments per 30-minute bin')
    ax.set_xlabel('Time since Mw 6.4 (hours)')
    ax.set_ylabel('Activated segment count')
    ax.set_title('Fault-segment activation density vs time')
    ax.grid(alpha=0.25, linestyle=':')
    fig.tight_layout()
    fig.savefig(fig_path, dpi=220)
    plt.close(fig)


def plot_cumulative_activation(new_counts: pd.DataFrame, fig_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(new_counts['bin_center_minutes'] / 60.0, new_counts['cumulative_activated_segments'], color='darkred', linewidth=2.0)
    ax.set_xlabel('Time since Mw 6.4 (hours)')
    ax.set_ylabel('Cumulative activated segments')
    ax.set_title('Cumulative fault-segment activation through time')
    ax.grid(alpha=0.25, linestyle=':')
    fig.tight_layout()
    fig.savefig(fig_path, dpi=220)
    plt.close(fig)


def plot_strike_time_density(strike_df: pd.DataFrame, fig_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(11, 6))
    data = strike_df.to_numpy(dtype=float)
    im = ax.imshow(
        data,
        aspect='auto',
        origin='lower',
        interpolation='nearest',
        extent=[strike_df.columns.min(), strike_df.columns.max() + 1, strike_df.index.min() - 2.5, strike_df.index.max() + 2.5],
        cmap='magma',
    )
    cbar = fig.colorbar(im, ax=ax, pad=0.02)
    cbar.set_label('Activated segment count')
    ax.set_xlabel('Time bin (30-minute bins since Mw 6.4)')
    ax.set_ylabel('Strike angle (deg, corrected to 0-180)')
    ax.set_title('Strike × activation-time density map')
    fig.tight_layout()
    fig.savefig(fig_path, dpi=220)
    plt.close(fig)


def plot_major_fault_raster(raster: pd.DataFrame, fig_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(11, 8))
    if raster.empty:
        ax.text(0.5, 0.5, 'No eligible activated faults for raster plot', ha='center', va='center', transform=ax.transAxes)
        ax.set_axis_off()
    else:
        line_ids = sorted(raster['line_id'].unique())
        offset = 0
        yticks = []
        ylabels = []
        for line_id in line_ids:
            sub = raster.loc[raster['line_id'] == line_id].sort_values('rank_position')
            y = offset + sub['rank_position'].to_numpy()
            x = sub['bin_start_minutes'].to_numpy() / 60.0
            c = sub['activation_bin'].to_numpy()
            sc = ax.scatter(x, y, c=c, cmap='viridis', s=26, edgecolors='none')
            yticks.append(offset + 0.5 * (len(sub) - 1))
            ylabels.append(f'line {line_id}')
            offset += len(sub) + 2
        cbar = fig.colorbar(sc, ax=ax, pad=0.02)
        cbar.set_label('Activation time bin')
        ax.set_yticks(yticks)
        ax.set_yticklabels(ylabels)
        ax.set_xlabel('Activation time since Mw 6.4 (hours)')
        ax.set_ylabel('Ordered segment position along parent fault')
        ax.set_title('Activation raster for major parent faults')
        ax.grid(alpha=0.2, linestyle=':')
    fig.tight_layout()
    fig.savefig(fig_path, dpi=220)
    plt.close(fig)


def plot_representative_segment_series(segment_ts: pd.DataFrame, summary: pd.DataFrame, fig_path: Path) -> None:
    activated = summary.loc[summary['activated']].sort_values('activation_minutes')
    never = summary.loc[~summary['activated']].sort_values('total_associated_events', ascending=False)
    chosen_ids = []
    if not activated.empty:
        chosen_ids.append(int(activated.iloc[0]['global_segment_id']))
        chosen_ids.append(int(activated.iloc[len(activated) // 2]['global_segment_id']))
        chosen_ids.append(int(activated.iloc[-1]['global_segment_id']))
    if not never.empty:
        chosen_ids.append(int(never.iloc[0]['global_segment_id']))
    chosen_ids = list(dict.fromkeys(chosen_ids))[:4]
    if not chosen_ids:
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.text(0.5, 0.5, 'No segment time series available', ha='center', va='center', transform=ax.transAxes)
        ax.set_axis_off()
        fig.tight_layout()
        fig.savefig(fig_path, dpi=220)
        plt.close(fig)
        return
    fig, axes = plt.subplots(len(chosen_ids), 1, figsize=(10, 2.6 * len(chosen_ids)), sharex=True)
    if len(chosen_ids) == 1:
        axes = [axes]
    for ax, seg_id in zip(axes, chosen_ids):
        ts = segment_ts.loc[segment_ts['global_segment_id'] == seg_id].sort_values('time_bin')
        meta = summary.loc[summary['global_segment_id'] == seg_id].iloc[0]
        x = ts['bin_center_minutes'] / 60.0
        y = ts['event_count']
        ax.step(x, y, where='mid', color='navy', linewidth=1.6)
        ax.axhline(ACTIVATION_COUNT_THRESHOLD, color='red', linestyle='--', linewidth=1.0)
        if bool(meta['activated']) and np.isfinite(meta['activation_hours']):
            ax.axvline(meta['activation_hours'], color='darkorange', linestyle='-', linewidth=1.2)
        ax.set_ylabel('Count/bin')
        ax.set_title(
            f"segment {int(seg_id)} | line {int(meta['line_id'])} seg {int(meta['segment_id'])} | "
            f"events={int(meta['total_associated_events'])} | activated={bool(meta['activated'])}"
        )
        ax.grid(alpha=0.25, linestyle=':')
    axes[-1].set_xlabel('Time since Mw 6.4 (hours)')
    fig.tight_layout()
    fig.savefig(fig_path, dpi=220)
    plt.close(fig)


def main() -> None:
    start = time.time()
    table_dir, fig_dir = prepare_output_dir(OUTPUT_DIR)
    log('Starting fault-segment activation analysis')

    mainshocks = load_mainshocks()
    to_local, to_geo, _ = build_local_transformer(mainshocks)
    mainshocks['x_km'], mainshocks['y_km'] = project_xy(mainshocks['longitude'].to_numpy(), mainshocks['latitude'].to_numpy(), to_local)
    t0 = mainshocks.loc[mainshocks['mainshock_label'] == 'Mainshock64', 'event_time'].iloc[0]
    mainshocks['elapsed_minutes_since_mw64'] = (mainshocks['event_time'] - t0).dt.total_seconds() / 60.0

    events = load_filtered_events()
    time_bins = load_time_bins()
    projected_faults = load_faults_projected(to_local)

    log('Building fault-segment backbone')
    segments = build_fault_segments(projected_faults, to_geo)
    require_columns(
        segments,
        [
            'global_segment_id', 'line_id', 'segment_id', 'segment_length_km', 'start_x_km', 'start_y_km',
            'end_x_km', 'end_y_km', 'mid_x_km', 'mid_y_km', 'strike_deg', 'along_line_mid_km'
        ],
        'fault_segment_geometry'
    )
    segments.to_csv(table_dir / 'fault_segment_geometry.csv', index=False)

    log('Associating earthquakes to nearest fault segments')
    associations = associate_events_to_segments(events, segments)
    associations.to_csv(table_dir / 'event_to_fault_segment_association.csv', index=False)
    unassociated = associations.loc[~associations['assigned_to_segment']].copy()
    unassociated.to_csv(table_dir / 'unassociated_events.csv', index=False)

    log('Constructing fault-segment time series')
    segment_ts = build_segment_time_series(associations, segments, time_bins)
    segment_ts.to_csv(table_dir / 'fault_segment_time_series.csv', index=False)

    log('Summarizing segment activation')
    summary = summarize_segment_activation(segment_ts, associations, segments)
    summary.to_csv(table_dir / 'fault_segment_activation_summary.csv', index=False)

    log('Building activation density products')
    new_counts, strike_df, strike_long = build_activation_density(summary, time_bins)
    new_counts.to_csv(table_dir / 'fault_activation_density_vs_time.csv', index=False)
    strike_long.to_csv(table_dir / 'strike_activation_density_long.csv', index=False)
    strike_df.to_csv(table_dir / 'strike_activation_density_matrix.csv', index=True)
    raster = build_line_activation_raster(summary, time_bins)
    raster.to_csv(table_dir / 'major_fault_activation_raster.csv', index=False)

    qc_rows = [
        {'category': 'faults', 'metric': 'n_projected_polylines', 'value': int(len(projected_faults))},
        {'category': 'segments', 'metric': 'n_segments', 'value': int(len(segments))},
        {'category': 'segments', 'metric': 'median_segment_length_km', 'value': float(segments['segment_length_km'].median())},
        {'category': 'segments', 'metric': 'mean_segment_length_km', 'value': float(segments['segment_length_km'].mean())},
        {'category': 'association', 'metric': 'n_events_input', 'value': int(len(events))},
        {'category': 'association', 'metric': 'n_assigned_events', 'value': int(associations['assigned_to_segment'].sum())},
        {'category': 'association', 'metric': 'fraction_assigned_events', 'value': float(associations['assigned_to_segment'].mean())},
        {'category': 'association', 'metric': 'median_distance_km', 'value': float(associations['distance_to_segment_km'].median())},
        {'category': 'activation', 'metric': 'n_segments_with_any_associated_events', 'value': int(summary['ever_associated'].sum())},
        {'category': 'activation', 'metric': 'n_activated_segments', 'value': int(summary['activated'].sum())},
        {'category': 'activation', 'metric': 'fraction_activated_of_all_segments', 'value': float(summary['activated'].mean())},
        {'category': 'activation', 'metric': 'fraction_activated_of_associated_segments', 'value': float(summary['activated'].sum() / max(int(summary['ever_associated'].sum()), 1))},
        {'category': 'run', 'metric': 'elapsed_seconds', 'value': float(time.time() - start)},
    ]
    save_qc_summary(table_dir / 'qc_summary.csv', qc_rows)

    run_params = pd.DataFrame(
        [
            {'parameter': 'catalog_path', 'value': str(CATALOG_PATH)},
            {'parameter': 'mainshock_path', 'value': str(MAINSHOCK_PATH)},
            {'parameter': 'fault_path', 'value': str(FAULT_PATH)},
            {'parameter': 'antecedent_filtered_events', 'value': str(ANTECEDENT_TABLE_DIR / 'filtered_events.csv')},
            {'parameter': 'time_bin_minutes', 'value': TIME_BIN_MINUTES},
            {'parameter': 'segment_target_length_km', 'value': SEGMENT_TARGET_LENGTH_KM},
            {'parameter': 'association_threshold_km', 'value': ASSOCIATION_THRESHOLD_KM},
            {'parameter': 'activation_threshold_count_per_30min_bin', 'value': ACTIVATION_COUNT_THRESHOLD},
            {'parameter': 'activation_threshold_rate_per_hour', 'value': ACTIVATION_COUNT_THRESHOLD * (60.0 / TIME_BIN_MINUTES)},
            {'parameter': 'max_cores', 'value': MAX_CORES},
        ]
    )
    run_params.to_csv(table_dir / 'run_parameters.csv', index=False)

    validation = pd.DataFrame(
        [
            {'metric': 'n_filtered_events', 'value': int(len(events))},
            {'metric': 'n_fault_segments', 'value': int(len(segments))},
            {'metric': 'n_associated_events', 'value': int(associations['assigned_to_segment'].sum())},
            {'metric': 'n_unassociated_events', 'value': int((~associations['assigned_to_segment']).sum())},
            {'metric': 'n_segments_with_associated_events', 'value': int(summary['ever_associated'].sum())},
            {'metric': 'n_activated_segments', 'value': int(summary['activated'].sum())},
            {'metric': 'n_major_fault_raster_rows', 'value': int(len(raster))},
        ]
    )
    validation.to_csv(table_dir / 'validation_summary.csv', index=False)

    log('Generating figures')
    plot_segments_by_line(segments, mainshocks, fig_dir / 'fault_segments_by_line.png')
    plot_segment_length_histogram(segments, fig_dir / 'segment_length_histogram.png')
    plot_strike_distribution(segments, fig_dir / 'segment_strike_distribution.png')
    plot_association_distance_histogram(associations, fig_dir / 'nearest_distance_histogram.png')
    plot_associated_vs_unassociated(segments, associations, mainshocks, fig_dir / 'associated_vs_unassociated_events.png')
    plot_activation_map(summary, associations, mainshocks, fig_dir / 'fault_segment_activation_map.png')
    plot_activation_counts(new_counts, fig_dir / 'fault_segment_activation_density_vs_time.png')
    plot_cumulative_activation(new_counts, fig_dir / 'cumulative_fault_segment_activation.png')
    plot_strike_time_density(strike_df, fig_dir / 'strike_activation_time_density.png')
    plot_major_fault_raster(raster, fig_dir / 'major_fault_activation_raster.png')
    plot_representative_segment_series(segment_ts, summary, fig_dir / 'representative_fault_segment_time_series.png')

    if len(segments) == 0 or len(associations) == 0 or len(segment_ts) == 0 or len(summary) == 0:
        raise ValueError('One or more primary outputs are empty')
    if int(summary['activated'].sum()) == 0:
        raise ValueError('No fault segments met the activation threshold; check association or threshold logic')

    elapsed = time.time() - start
    log(f'Finished fault-segment activation analysis in {elapsed:.1f} s')


if __name__ == '__main__':
    try:
        main()
    except Exception:
        print(traceback.format_exc(), flush=True)
        sys.exit(1)
