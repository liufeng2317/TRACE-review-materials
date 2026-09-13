from __future__ import annotations

import math
import shutil
import sys
import time
import traceback
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.colors import Normalize
import numpy as np
import pandas as pd
from joblib import Parallel, delayed
from scipy.stats import spearmanr


SCRIPT_PATH = Path('<REPO_ROOT>/examples/ridgecrest/catalog_analysis/run/01_2_trigger_spatiotemporal_fault_Q2-v1/exp_run/scripts/03_triggering_style_diagnostics.py')
OUTPUT_DIR = Path('<REPO_ROOT>/examples/ridgecrest/catalog_analysis/run/01_2_trigger_spatiotemporal_fault_Q2-v1/exp_run/outputs/03_triggering_style_diagnostics')
GRID_TABLE_DIR = Path('<REPO_ROOT>/examples/ridgecrest/catalog_analysis/run/01_2_trigger_spatiotemporal_fault_Q2-v1/exp_run/outputs/01_grid_onset_analysis/tables')
FAULT_TABLE_DIR = Path('<REPO_ROOT>/examples/ridgecrest/catalog_analysis/run/01_2_trigger_spatiotemporal_fault_Q2-v1/exp_run/outputs/02_fault_segment_activation/tables')

TIME_BIN_MINUTES = 30
MAX_CORES = 64
MAJOR_FAULT_MIN_ACTIVATED_SEGMENTS = 8
MW71_NEIGHBORHOOD_RADIUS_KM = 3.0
EARLY_WINDOW_MIN = 60.0
MID_WINDOW_MIN = 240.0
BEND_ANGLE_THRESHOLD_DEG = 20.0


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


def require_columns(df: pd.DataFrame, required: list[str], df_name: str) -> None:
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f'{df_name} missing required columns: {missing}')


def load_csv(path: Path, required: list[str], name: str) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f'Missing required input table: {path}')
    df = pd.read_csv(path)
    require_columns(df, required, name)
    return df


def parse_datetime_mixed(series: pd.Series, name: str, allow_missing: bool = False) -> pd.Series:
    parsed = pd.to_datetime(series, utc=True, format='mixed', errors='coerce')
    if allow_missing:
        invalid_mask = parsed.isna() & series.notna()
    else:
        invalid_mask = parsed.isna()
    if invalid_mask.any():
        n_bad = int(invalid_mask.sum())
        raise ValueError(f'Failed to parse {n_bad} datetime values in {name}')
    return parsed


def load_inputs() -> dict[str, pd.DataFrame]:
    log('Loading antecedent outputs from Tasks 01 and 02')
    grid_onset = load_csv(
        GRID_TABLE_DIR / 'grid_cell_onset.csv',
        ['cell_id', 'x_center_km', 'y_center_km', 'onset_minutes', 'onset_bin', 'confidence_class', 'occupied', 'total_cell_events'],
        'grid_cell_onset',
    )
    grid_def = load_csv(
        GRID_TABLE_DIR / 'grid_definition.csv',
        ['cell_id', 'xmin_km', 'xmax_km', 'ymin_km', 'ymax_km', 'x_center_km', 'y_center_km', 'centroid_longitude', 'centroid_latitude'],
        'grid_definition',
    )
    filtered_events = load_csv(
        GRID_TABLE_DIR / 'filtered_events.csv',
        ['event_time', 'latitude', 'longitude', 'depth_km', 'magnitude', 'event_id', 'x_km', 'y_km', 'elapsed_minutes', 'elapsed_hours', 'time_bin'],
        'filtered_events',
    )
    mainshock = load_csv(
        GRID_TABLE_DIR / 'mainshock_reference_table.csv',
        ['event_time', 'latitude', 'longitude', 'depth_km', 'magnitude', 'mainshock_label', 'x_km', 'y_km', 'elapsed_minutes_since_mw64'],
        'mainshock_reference_table',
    )
    time_bins = load_csv(
        GRID_TABLE_DIR / 'time_bins.csv',
        ['time_bin', 'bin_start_utc', 'bin_end_utc', 'bin_center_minutes', 'bin_start_minutes', 'bin_end_minutes'],
        'time_bins',
    )
    segment_geom = load_csv(
        FAULT_TABLE_DIR / 'fault_segment_geometry.csv',
        ['line_id', 'segment_id', 'global_segment_id', 'segment_length_km', 'start_x_km', 'start_y_km', 'end_x_km', 'end_y_km', 'mid_x_km', 'mid_y_km', 'mid_lon', 'mid_lat', 'along_line_mid_km', 'strike_deg'],
        'fault_segment_geometry',
    )
    event_assoc = load_csv(
        FAULT_TABLE_DIR / 'event_to_fault_segment_association.csv',
        ['event_id', 'event_time', 'x_km', 'y_km', 'elapsed_minutes', 'time_bin', 'assigned_to_segment', 'distance_to_segment_km'],
        'event_to_fault_segment_association',
    )
    segment_activation = load_csv(
        FAULT_TABLE_DIR / 'fault_segment_activation_summary.csv',
        ['line_id', 'segment_id', 'global_segment_id', 'mid_x_km', 'mid_y_km', 'mid_lon', 'mid_lat', 'along_line_mid_km', 'strike_deg', 'activated', 'activation_bin', 'activation_minutes', 'activation_hours', 'total_associated_events', 'ever_associated'],
        'fault_segment_activation_summary',
    )
    segment_ts = load_csv(
        FAULT_TABLE_DIR / 'fault_segment_time_series.csv',
        ['global_segment_id', 'time_bin', 'event_count', 'rate_events_per_hour', 'cumulative_count', 'line_id', 'segment_id', 'strike_deg', 'along_line_mid_km'],
        'fault_segment_time_series',
    )
    validation_grid = load_csv(GRID_TABLE_DIR / 'validation_summary.csv', ['metric', 'value'], 'grid_validation_summary')
    validation_fault = load_csv(FAULT_TABLE_DIR / 'validation_summary.csv', ['metric', 'value'], 'fault_validation_summary')

    filtered_events['event_time'] = parse_datetime_mixed(filtered_events['event_time'], 'filtered_events.event_time')
    mainshock['event_time'] = parse_datetime_mixed(mainshock['event_time'], 'mainshock.event_time')
    time_bins['bin_start_utc'] = parse_datetime_mixed(time_bins['bin_start_utc'], 'time_bins.bin_start_utc')
    time_bins['bin_end_utc'] = parse_datetime_mixed(time_bins['bin_end_utc'], 'time_bins.bin_end_utc')
    event_assoc['event_time'] = parse_datetime_mixed(event_assoc['event_time'], 'event_assoc.event_time')
    if 'first_associated_event_time' in segment_activation.columns:
        segment_activation['first_associated_event_time'] = parse_datetime_mixed(
            segment_activation['first_associated_event_time'],
            'segment_activation.first_associated_event_time',
            allow_missing=True,
        )

    numeric_frames = [grid_onset, grid_def, filtered_events, mainshock, time_bins, segment_geom, event_assoc, segment_activation, segment_ts]
    for df in numeric_frames:
        for col in df.columns:
            if col in {'event_time', 'first_associated_event_time', 'bin_start_utc', 'bin_end_utc', 'mainshock_label', 'confidence_class'}:
                continue
            if df[col].dtype == object and col not in {'associated', 'activated', 'ever_associated', 'occupied'}:
                try:
                    df[col] = pd.to_numeric(df[col])
                except Exception:
                    pass

    event_assoc = event_assoc.rename(columns={'assigned_to_segment': 'associated'})
    require_columns(event_assoc, ['associated'], 'event_assoc_renamed')
    for flag_col in ['associated']:
        event_assoc[flag_col] = event_assoc[flag_col].astype(bool)
    for flag_col in ['activated', 'ever_associated']:
        segment_activation[flag_col] = segment_activation[flag_col].astype(bool)
    grid_onset['occupied'] = grid_onset['occupied'].astype(bool)

    return {
        'grid_onset': grid_onset,
        'grid_def': grid_def,
        'filtered_events': filtered_events,
        'mainshock': mainshock,
        'time_bins': time_bins,
        'segment_geom': segment_geom,
        'event_assoc': event_assoc,
        'segment_activation': segment_activation,
        'segment_ts': segment_ts,
        'validation_grid': validation_grid,
        'validation_fault': validation_fault,
    }


def add_segment_geometry_diagnostics(segment_df: pd.DataFrame) -> pd.DataFrame:
    out = segment_df.sort_values(['line_id', 'segment_id']).reset_index(drop=True).copy()
    out['segment_dx_km'] = out['end_x_km'] - out['start_x_km']
    out['segment_dy_km'] = out['end_y_km'] - out['start_y_km']
    out['segment_mid_distance_from_origin_km'] = np.hypot(out['mid_x_km'], out['mid_y_km'])
    out['bend_flag'] = False
    out['local_turn_angle_deg'] = np.nan
    for line_id, idx in out.groupby('line_id').groups.items():
        ids = list(idx)
        if len(ids) < 3:
            continue
        strikes = out.loc[ids, 'strike_deg'].to_numpy(dtype=float)
        turn = np.abs(np.diff(strikes))
        turn = np.minimum(turn, 180.0 - turn)
        for pos in range(1, len(ids) - 1):
            angle = max(turn[pos - 1], turn[pos])
            out.at[ids[pos], 'local_turn_angle_deg'] = angle
            out.at[ids[pos], 'bend_flag'] = bool(angle >= BEND_ANGLE_THRESHOLD_DEG)
    return out


def compute_system_synchrony(grid_onset: pd.DataFrame, segment_activation: pd.DataFrame) -> pd.DataFrame:
    windows = [30.0, 60.0, 120.0, 240.0]
    records: list[dict] = []

    grid_active = grid_onset.loc[np.isfinite(grid_onset['onset_minutes'])].copy()
    n_grid_total = int(grid_onset['occupied'].sum())
    n_grid_active = int(len(grid_active))
    seg_active = segment_activation.loc[segment_activation['activated']].copy()
    n_seg_total = int(len(segment_activation))
    n_seg_active = int(len(seg_active))

    for w in windows:
        records.append({
            'domain': 'grid_cells',
            'metric': f'fraction_activated_within_{int(w)}min',
            'value': float((grid_active['onset_minutes'] <= w).mean()) if n_grid_active > 0 else np.nan,
            'n_total_domain': n_grid_total,
            'n_active_domain': n_grid_active,
        })
        records.append({
            'domain': 'fault_segments',
            'metric': f'fraction_activated_within_{int(w)}min',
            'value': float((seg_active['activation_minutes'] <= w).mean()) if n_seg_active > 0 else np.nan,
            'n_total_domain': n_seg_total,
            'n_active_domain': n_seg_active,
        })

    for domain, series, total_n, active_n in [
        ('grid_cells', grid_active['onset_minutes'], n_grid_total, n_grid_active),
        ('fault_segments', seg_active['activation_minutes'], n_seg_total, n_seg_active),
    ]:
        if active_n > 0:
            quantiles = series.quantile([0.1, 0.25, 0.5, 0.75, 0.9])
            for q, val in quantiles.items():
                records.append({'domain': domain, 'metric': f'activation_time_q{int(round(q*100)):02d}_minutes', 'value': float(val), 'n_total_domain': total_n, 'n_active_domain': active_n})
            iqr = float(quantiles.loc[0.75] - quantiles.loc[0.25])
        else:
            iqr = np.nan
        records.extend([
            {'domain': domain, 'metric': 'n_total_domain', 'value': float(total_n), 'n_total_domain': total_n, 'n_active_domain': active_n},
            {'domain': domain, 'metric': 'n_active_domain', 'value': float(active_n), 'n_total_domain': total_n, 'n_active_domain': active_n},
            {'domain': domain, 'metric': 'activation_time_iqr_minutes', 'value': iqr, 'n_total_domain': total_n, 'n_active_domain': active_n},
        ])
    return pd.DataFrame(records)


def build_distance_metrics(grid_onset: pd.DataFrame, segment_activation: pd.DataFrame, mainshock: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    ms64 = mainshock.loc[mainshock['mainshock_label'] == 'Mainshock64'].iloc[0]
    ms71 = mainshock.loc[mainshock['mainshock_label'] == 'Mainshock71'].iloc[0]

    grid = grid_onset.copy()
    grid['distance_to_mw64_km'] = np.hypot(grid['x_center_km'] - ms64['x_km'], grid['y_center_km'] - ms64['y_km'])
    grid['distance_to_mw71_km'] = np.hypot(grid['x_center_km'] - ms71['x_km'], grid['y_center_km'] - ms71['y_km'])

    seg = segment_activation.copy()
    seg['distance_to_mw64_km'] = np.hypot(seg['mid_x_km'] - ms64['x_km'], seg['mid_y_km'] - ms64['y_km'])
    seg['distance_to_mw71_km'] = np.hypot(seg['mid_x_km'] - ms71['x_km'], seg['mid_y_km'] - ms71['y_km'])
    return grid, seg


def compute_activation_dispersion_by_class(seg: pd.DataFrame) -> pd.DataFrame:
    active = seg.loc[seg['activated']].copy()
    if active.empty:
        return pd.DataFrame(columns=['class_type', 'class_label', 'n_segments', 'activation_time_median_minutes', 'activation_time_iqr_minutes'])

    distance_bins = [0.0, 3.0, 6.0, 10.0, 15.0, np.inf]
    distance_labels = ['0-3', '3-6', '6-10', '10-15', '15+']
    active['distance_class_mw71'] = pd.cut(active['distance_to_mw71_km'], bins=distance_bins, labels=distance_labels, include_lowest=True, right=False)
    strike_bins = np.arange(0.0, 195.0, 15.0)
    strike_labels = [f'{int(strike_bins[i])}-{int(strike_bins[i+1])}' for i in range(len(strike_bins)-1)]
    active['strike_class'] = pd.cut(active['strike_deg'], bins=strike_bins, labels=strike_labels, include_lowest=True, right=False)

    records: list[dict] = []
    for class_type, col in [('distance_to_mw71_km', 'distance_class_mw71'), ('strike_deg', 'strike_class')]:
        grouped = active.groupby(col, dropna=True)
        for label, g in grouped:
            q = g['activation_minutes'].quantile([0.25, 0.5, 0.75])
            records.append({
                'class_type': class_type,
                'class_label': str(label),
                'n_segments': int(len(g)),
                'activation_time_median_minutes': float(q.loc[0.5]),
                'activation_time_iqr_minutes': float(q.loc[0.75] - q.loc[0.25]),
            })
    return pd.DataFrame(records)


def classify_fault_style(spearman_rho: float, p_value: float, activation_span_km: float, n_activated_segments: int, n_early_jumps: int, late_residual_fraction: float) -> str:
    if n_activated_segments < MAJOR_FAULT_MIN_ACTIVATED_SEGMENTS:
        return 'complex/indeterminate'
    if np.isfinite(spearman_rho) and abs(spearman_rho) >= 0.75 and p_value <= 0.05 and activation_span_km >= 5.0:
        return 'staged/progressive'
    if np.isfinite(spearman_rho) and abs(spearman_rho) <= 0.25 and n_early_jumps <= 1 and late_residual_fraction < 0.25:
        return 'near-synchronous'
    if n_early_jumps >= 2:
        return 'jump-like'
    return 'complex/indeterminate'


def compute_line_metrics_for_group(line_id: int, line_df: pd.DataFrame) -> dict:
    activated = line_df.loc[line_df['activated']].sort_values('along_line_mid_km').copy()
    total_segments = int(len(line_df))
    n_activated = int(len(activated))
    if n_activated == 0:
        return {
            'line_id': int(line_id),
            'n_total_segments': total_segments,
            'n_activated_segments': 0,
            'activation_fraction': 0.0,
            'eligible_for_propagation': False,
            'spearman_rho': np.nan,
            'spearman_pvalue': np.nan,
            'slope_minutes_per_km': np.nan,
            'intercept_minutes': np.nan,
            'r2_linear': np.nan,
            'activation_span_km': 0.0,
            'activation_time_span_minutes': np.nan,
            'median_activation_minutes': np.nan,
            'iqr_activation_minutes': np.nan,
            'n_early_jump_pairs': 0,
            'bend_fraction_activated': float(line_df['bend_flag'].fillna(False).mean()) if 'bend_flag' in line_df.columns else np.nan,
            'late_residual_fraction': np.nan,
            'classification': 'complex/indeterminate',
        }

    x = activated['along_line_mid_km'].to_numpy(dtype=float)
    y = activated['activation_minutes'].to_numpy(dtype=float)
    rho, pval = (np.nan, np.nan)
    if n_activated >= 3 and np.nanstd(x) > 0 and np.nanstd(y) > 0:
        rho, pval = spearmanr(x, y)
    if n_activated >= 2 and np.nanstd(x) > 0:
        slope, intercept = np.polyfit(x, y, 1)
        yhat = slope * x + intercept
        ss_res = float(np.sum((y - yhat) ** 2))
        ss_tot = float(np.sum((y - np.mean(y)) ** 2))
        r2 = float(1.0 - ss_res / ss_tot) if ss_tot > 0 else np.nan
        residual = np.abs(y - yhat)
        late_residual_fraction = float(np.mean(residual > 120.0))
    else:
        slope, intercept, r2, late_residual_fraction = (np.nan, np.nan, np.nan, np.nan)

    early_threshold = float(np.nanquantile(y, 0.25)) if n_activated > 0 else np.nan
    early = activated.loc[activated['activation_minutes'] <= early_threshold].sort_values('along_line_mid_km')
    jump_pairs = 0
    if len(early) >= 2:
        gaps = np.diff(early['along_line_mid_km'].to_numpy(dtype=float))
        jump_pairs = int(np.sum(gaps > 3.0))

    q = activated['activation_minutes'].quantile([0.25, 0.5, 0.75])
    classification = classify_fault_style(rho, pval, float(x.max() - x.min()), n_activated, jump_pairs, late_residual_fraction if np.isfinite(late_residual_fraction) else 0.0)
    return {
        'line_id': int(line_id),
        'n_total_segments': total_segments,
        'n_activated_segments': n_activated,
        'activation_fraction': float(n_activated / total_segments) if total_segments > 0 else np.nan,
        'eligible_for_propagation': bool(n_activated >= MAJOR_FAULT_MIN_ACTIVATED_SEGMENTS),
        'spearman_rho': float(rho) if np.isfinite(rho) else np.nan,
        'spearman_pvalue': float(pval) if np.isfinite(pval) else np.nan,
        'slope_minutes_per_km': float(slope) if np.isfinite(slope) else np.nan,
        'intercept_minutes': float(intercept) if np.isfinite(intercept) else np.nan,
        'r2_linear': float(r2) if np.isfinite(r2) else np.nan,
        'activation_span_km': float(x.max() - x.min()) if n_activated > 0 else 0.0,
        'activation_time_span_minutes': float(y.max() - y.min()) if n_activated > 0 else np.nan,
        'median_activation_minutes': float(q.loc[0.5]),
        'iqr_activation_minutes': float(q.loc[0.75] - q.loc[0.25]),
        'n_early_jump_pairs': int(jump_pairs),
        'bend_fraction_activated': float(activated['bend_flag'].fillna(False).mean()) if 'bend_flag' in activated.columns else np.nan,
        'late_residual_fraction': float(late_residual_fraction) if np.isfinite(late_residual_fraction) else np.nan,
        'classification': classification,
    }


def compute_along_fault_metrics(seg: pd.DataFrame) -> pd.DataFrame:
    groups = list(seg.groupby('line_id'))
    n_jobs = min(MAX_CORES, max(1, len(groups)))
    log(f'Computing along-fault metrics for {len(groups)} parent faults with n_jobs={n_jobs}')
    results = Parallel(n_jobs=n_jobs, prefer='threads')(
        delayed(compute_line_metrics_for_group)(int(line_id), g.copy())
        for line_id, g in groups
    )
    out = pd.DataFrame(results).sort_values(['eligible_for_propagation', 'n_activated_segments', 'activation_fraction'], ascending=[False, False, False]).reset_index(drop=True)
    return out


def compute_cross_fault_complexity(seg: pd.DataFrame) -> pd.DataFrame:
    active = seg.loc[seg['activated']].copy()
    records: list[dict] = []
    if active.empty:
        return pd.DataFrame(columns=['metric', 'value'])

    first_by_line = active.groupby('line_id', as_index=False)['activation_minutes'].min().rename(columns={'activation_minutes': 'line_first_activation_minutes'})
    first_vals = np.sort(first_by_line['line_first_activation_minutes'].to_numpy(dtype=float))
    if len(first_vals) >= 2:
        diffs = np.diff(first_vals)
        near_coactivation = int(np.sum(diffs <= 30.0))
        jump_like = int(np.sum(diffs <= 30.0))
    else:
        near_coactivation = 0
        jump_like = 0

    early = active.loc[active['activation_minutes'] <= EARLY_WINDOW_MIN]
    mid = active.loc[(active['activation_minutes'] > EARLY_WINDOW_MIN) & (active['activation_minutes'] <= MID_WINDOW_MIN)]
    late = active.loc[active['activation_minutes'] > MID_WINDOW_MIN]

    for label, subset in [('early', early), ('mid', mid), ('late', late)]:
        records.append({'metric': f'{label}_activated_segments', 'value': float(len(subset))})
        records.append({'metric': f'{label}_activated_lines', 'value': float(subset["line_id"].nunique())})
        if len(subset) > 0 and 'bend_flag' in subset.columns:
            records.append({'metric': f'{label}_bend_fraction', 'value': float(subset['bend_flag'].fillna(False).mean())})
        else:
            records.append({'metric': f'{label}_bend_fraction', 'value': np.nan})

    records.extend([
        {'metric': 'n_active_lines', 'value': float(first_by_line['line_id'].nunique())},
        {'metric': 'line_first_activation_q25_minutes', 'value': float(first_by_line['line_first_activation_minutes'].quantile(0.25))},
        {'metric': 'line_first_activation_median_minutes', 'value': float(first_by_line['line_first_activation_minutes'].quantile(0.5))},
        {'metric': 'line_first_activation_q75_minutes', 'value': float(first_by_line['line_first_activation_minutes'].quantile(0.75))},
        {'metric': 'n_adjacent_first_line_activations_within_30min', 'value': float(near_coactivation)},
        {'metric': 'cross_fault_jump_like_pairs_within_30min', 'value': float(jump_like)},
    ])
    return pd.DataFrame(records)


def compute_mw71_context(seg: pd.DataFrame, mainshock: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    ms71 = mainshock.loc[mainshock['mainshock_label'] == 'Mainshock71'].iloc[0]
    work = seg.copy()
    work['distance_to_mw71_km'] = np.hypot(work['mid_x_km'] - ms71['x_km'], work['mid_y_km'] - ms71['y_km'])
    nearest_idx = int(work['distance_to_mw71_km'].idxmin())
    target = work.loc[[nearest_idx]].copy()
    target['is_nearest_to_mw71'] = True
    line_id = int(target['line_id'].iloc[0])
    along = float(target['along_line_mid_km'].iloc[0])

    same_line_neighbors = work.loc[(work['line_id'] == line_id) & (np.abs(work['along_line_mid_km'] - along) <= MW71_NEIGHBORHOOD_RADIUS_KM)].copy()
    spatial_neighbors = work.loc[work['distance_to_mw71_km'] <= MW71_NEIGHBORHOOD_RADIUS_KM].copy()
    active = work.loc[work['activated']].copy()

    target_activation = float(target['activation_minutes'].iloc[0]) if bool(target['activated'].iloc[0]) and np.isfinite(target['activation_minutes'].iloc[0]) else np.nan
    if active.empty or not np.isfinite(target_activation):
        percentile_system = np.nan
    else:
        percentile_system = float((active['activation_minutes'] <= target_activation).mean())

    local_active = spatial_neighbors.loc[spatial_neighbors['activated']]
    same_line_active = same_line_neighbors.loc[same_line_neighbors['activated']]
    summary = pd.DataFrame([
        {
            'target_global_segment_id': int(target['global_segment_id'].iloc[0]),
            'target_line_id': line_id,
            'target_segment_id': int(target['segment_id'].iloc[0]),
            'distance_to_mw71_km': float(target['distance_to_mw71_km'].iloc[0]),
            'target_activated': bool(target['activated'].iloc[0]),
            'target_activation_minutes': target_activation,
            'target_activation_hours': float(target['activation_hours'].iloc[0]) if np.isfinite(target['activation_hours'].iloc[0]) else np.nan,
            'system_activation_percentile_leq': percentile_system,
            'n_spatial_neighbors_within_3km': int(len(spatial_neighbors)),
            'n_same_line_neighbors_within_3km_along': int(len(same_line_neighbors)),
            'local_active_neighbor_count': int(len(local_active)),
            'same_line_active_neighbor_count': int(len(same_line_active)),
            'local_neighbor_median_activation_minutes': float(local_active['activation_minutes'].median()) if len(local_active) > 0 else np.nan,
            'same_line_neighbor_median_activation_minutes': float(same_line_active['activation_minutes'].median()) if len(same_line_active) > 0 else np.nan,
            'activation_minus_local_neighbor_median_minutes': float(target_activation - local_active['activation_minutes'].median()) if len(local_active) > 0 and np.isfinite(target_activation) else np.nan,
            'activation_minus_same_line_neighbor_median_minutes': float(target_activation - same_line_active['activation_minutes'].median()) if len(same_line_active) > 0 and np.isfinite(target_activation) else np.nan,
            'anomalously_late_vs_local': bool(np.isfinite(target_activation) and len(local_active) > 0 and target_activation > local_active['activation_minutes'].quantile(0.75)),
            'anomalously_late_vs_system': bool(np.isfinite(percentile_system) and percentile_system >= 0.75),
        }
    ])
    neighborhood = pd.concat([
        target.assign(neighborhood_type='target'),
        same_line_neighbors.assign(neighborhood_type='same_line_along_3km'),
        spatial_neighbors.assign(neighborhood_type='spatial_within_3km'),
    ], ignore_index=True)
    neighborhood = neighborhood.drop_duplicates(subset=['global_segment_id', 'neighborhood_type']).sort_values(['neighborhood_type', 'distance_to_mw71_km', 'line_id', 'segment_id']).reset_index(drop=True)
    return summary, neighborhood


def compute_event_conservation(filtered_events: pd.DataFrame, event_assoc: pd.DataFrame) -> pd.DataFrame:
    assoc = event_assoc.copy()
    associated = assoc.loc[assoc['associated']]
    out = pd.DataFrame([
        {'stage': 'filtered_events_task01', 'count': int(filtered_events['event_id'].nunique())},
        {'stage': 'fault_association_rows_task02', 'count': int(assoc['event_id'].nunique())},
        {'stage': 'associated_events_task02', 'count': int(associated['event_id'].nunique())},
        {'stage': 'unassociated_events_task02', 'count': int((~assoc['associated']).sum())},
    ])
    return out


def plot_scatter_distance(seg: pd.DataFrame, x_col: str, x_label: str, out_path: Path) -> None:
    active = seg.loc[seg['activated']].copy()
    fig, ax = plt.subplots(figsize=(8.5, 6.5))
    if not active.empty:
        sc = ax.scatter(active[x_col], active['activation_minutes'], c=active['strike_deg'], cmap='viridis', s=18, alpha=0.7, edgecolors='none')
        cbar = fig.colorbar(sc, ax=ax)
        cbar.set_label('Strike (deg)')
    ax.set_xlabel(x_label)
    ax.set_ylabel('Fault-segment activation time since Mw 6.4 (min)')
    ax.set_title(f'Activation time vs {x_label}')
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_path, dpi=200)
    plt.close(fig)


def plot_along_fault_panels(seg: pd.DataFrame, line_metrics: pd.DataFrame, out_path: Path) -> None:
    eligible = line_metrics.loc[line_metrics['eligible_for_propagation']].head(6)
    if eligible.empty:
        eligible = line_metrics.head(6)
    if eligible.empty:
        raise ValueError('No faults available to plot along-fault activation panels')
    n = len(eligible)
    ncols = 2
    nrows = int(math.ceil(n / ncols))
    fig, axes = plt.subplots(nrows, ncols, figsize=(12, 3.8 * nrows), squeeze=False)
    axes_flat = axes.ravel()
    for ax in axes_flat[n:]:
        ax.axis('off')
    for ax, (_, row) in zip(axes_flat, eligible.iterrows()):
        g = seg.loc[(seg['line_id'] == row['line_id']) & (seg['activated'])].sort_values('along_line_mid_km')
        ax.scatter(g['along_line_mid_km'], g['activation_minutes'], s=22, alpha=0.8, color='tab:blue')
        if len(g) >= 2 and np.isfinite(row['slope_minutes_per_km']):
            x = np.array([g['along_line_mid_km'].min(), g['along_line_mid_km'].max()])
            y = row['slope_minutes_per_km'] * x + row['intercept_minutes']
            ax.plot(x, y, color='tab:red', lw=1.5)
        ax.set_title(f"line_id={int(row['line_id'])} | n={int(row['n_activated_segments'])} | {row['classification']}")
        ax.set_xlabel('Along-fault distance (km)')
        ax.set_ylabel('Activation time (min)')
        ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_path, dpi=200)
    plt.close(fig)


def plot_activation_stage_map(seg: pd.DataFrame, mainshock: pd.DataFrame, out_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(9.5, 8.0))
    categories = [
        ('early (<=60 min)', seg['activated'] & (seg['activation_minutes'] <= EARLY_WINDOW_MIN), '#1f78b4'),
        ('intermediate (60-240 min)', seg['activated'] & (seg['activation_minutes'] > EARLY_WINDOW_MIN) & (seg['activation_minutes'] <= MID_WINDOW_MIN), '#33a02c'),
        ('late (>240 min)', seg['activated'] & (seg['activation_minutes'] > MID_WINDOW_MIN), '#e31a1c'),
        ('never activated', ~seg['activated'], '#bdbdbd'),
    ]
    for label, mask, color in categories:
        subset = seg.loc[mask]
        if subset.empty:
            continue
        segments = [np.array([[r['start_x_km'], r['start_y_km']], [r['end_x_km'], r['end_y_km']]], dtype=float) for _, r in subset.iterrows()]
        lc = LineCollection(segments, colors=color, linewidths=1.2, alpha=0.85, label=label)
        ax.add_collection(lc)
    for _, row in mainshock.iterrows():
        marker = '*' if row['mainshock_label'] == 'Mainshock64' else '^'
        ax.scatter(row['x_km'], row['y_km'], s=180, marker=marker, edgecolor='k', facecolor='gold' if marker == '*' else 'tomato', zorder=5)
        ax.text(row['x_km'] + 0.35, row['y_km'] + 0.35, row['mainshock_label'], fontsize=9)
    ax.autoscale()
    ax.set_aspect('equal', adjustable='box')
    ax.set_xlabel('Local x (km)')
    ax.set_ylabel('Local y (km)')
    ax.set_title('Fault-segment activation stages relative to Mw 6.4')
    ax.legend(loc='best', fontsize=8, frameon=True)
    ax.grid(True, alpha=0.2)
    fig.tight_layout()
    fig.savefig(out_path, dpi=200)
    plt.close(fig)


def plot_mw71_context(neighborhood: pd.DataFrame, mainshock: pd.DataFrame, out_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(8.5, 7.5))
    base = neighborhood.drop_duplicates(subset=['global_segment_id'])
    activated = base.loc[base['activated']].copy()
    inactive = base.loc[~base['activated']].copy()
    if not inactive.empty:
        ax.scatter(inactive['mid_x_km'], inactive['mid_y_km'], c='lightgray', s=28, alpha=0.5, label='Nearby unactivated')
    if not activated.empty:
        sc = ax.scatter(activated['mid_x_km'], activated['mid_y_km'], c=activated['activation_minutes'], cmap='magma_r', s=42, alpha=0.9, label='Nearby activated')
        cbar = fig.colorbar(sc, ax=ax)
        cbar.set_label('Activation time (min)')
    target = neighborhood.loc[neighborhood['neighborhood_type'] == 'target'].iloc[0]
    ax.scatter(target['mid_x_km'], target['mid_y_km'], s=180, marker='o', facecolor='none', edgecolor='cyan', linewidth=2.0, label='Mw 7.1 nearest segment')
    for _, row in mainshock.iterrows():
        marker = '*' if row['mainshock_label'] == 'Mainshock64' else '^'
        ax.scatter(row['x_km'], row['y_km'], s=180, marker=marker, edgecolor='k', facecolor='gold' if marker == '*' else 'tomato', zorder=5)
    ms71 = mainshock.loc[mainshock['mainshock_label'] == 'Mainshock71'].iloc[0]
    ax.add_patch(plt.Circle((ms71['x_km'], ms71['y_km']), MW71_NEIGHBORHOOD_RADIUS_KM, fill=False, ls='--', lw=1.2, ec='k'))
    ax.set_aspect('equal', adjustable='box')
    ax.set_xlabel('Local x (km)')
    ax.set_ylabel('Local y (km)')
    ax.set_title('Mw 7.1 nucleation-area activation context')
    ax.legend(loc='best', fontsize=8)
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig(out_path, dpi=200)
    plt.close(fig)


def plot_activation_map_comparison(grid: pd.DataFrame, seg: pd.DataFrame, out_path: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(14, 6), constrained_layout=True)
    ax0, ax1 = axes
    active_grid = grid.loc[np.isfinite(grid['onset_minutes'])]
    if not active_grid.empty:
        sc0 = ax0.scatter(active_grid['x_center_km'], active_grid['y_center_km'], c=active_grid['onset_minutes'], cmap='magma_r', s=18, alpha=0.85, edgecolors='none')
        cbar0 = fig.colorbar(sc0, ax=ax0)
        cbar0.set_label('Grid onset time (min)')
    ax0.set_title('Grid-cell onset map')
    ax0.set_aspect('equal', adjustable='box')
    ax0.grid(True, alpha=0.2)
    ax0.set_xlabel('Local x (km)')
    ax0.set_ylabel('Local y (km)')

    segments = [np.array([[r['start_x_km'], r['start_y_km']], [r['end_x_km'], r['end_y_km']]], dtype=float) for _, r in seg.iterrows()]
    values = seg['activation_minutes'].to_numpy(dtype=float)
    cmap = plt.get_cmap('magma_r')
    norm = Normalize(vmin=np.nanmin(values[np.isfinite(values)]) if np.isfinite(values).any() else 0.0,
                     vmax=np.nanmax(values[np.isfinite(values)]) if np.isfinite(values).any() else 1.0)
    colors = [cmap(norm(v)) if np.isfinite(v) else (0.8, 0.8, 0.8, 0.8) for v in values]
    lc = LineCollection(segments, colors=colors, linewidths=1.0)
    ax1.add_collection(lc)
    ax1.autoscale()
    ax1.set_title('Fault-segment activation map')
    ax1.set_aspect('equal', adjustable='box')
    ax1.grid(True, alpha=0.2)
    ax1.set_xlabel('Local x (km)')
    ax1.set_ylabel('Local y (km)')
    sm = plt.cm.ScalarMappable(norm=norm, cmap=cmap)
    cbar1 = fig.colorbar(sm, ax=ax1)
    cbar1.set_label('Fault activation time (min)')
    fig.savefig(out_path, dpi=200)
    plt.close(fig)


def make_validation_summary(filtered_events: pd.DataFrame, grid_onset: pd.DataFrame, event_assoc: pd.DataFrame, segment_activation: pd.DataFrame, line_metrics: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame([
        {'metric': 'number_of_filtered_events', 'value': int(filtered_events['event_id'].nunique())},
        {'metric': 'occupied_grid_cells', 'value': int(grid_onset['occupied'].sum())},
        {'metric': 'activated_grid_cells', 'value': int(np.isfinite(grid_onset['onset_minutes']).sum())},
        {'metric': 'associated_events', 'value': int(event_assoc.loc[event_assoc['associated'], 'event_id'].nunique())},
        {'metric': 'activated_fault_segments', 'value': int(segment_activation['activated'].sum())},
        {'metric': 'major_faults_eligible_for_propagation_testing', 'value': int(line_metrics['eligible_for_propagation'].sum())},
    ])


def make_run_parameters(mainshock: pd.DataFrame) -> pd.DataFrame:
    ms64 = mainshock.loc[mainshock['mainshock_label'] == 'Mainshock64'].iloc[0]
    ms71 = mainshock.loc[mainshock['mainshock_label'] == 'Mainshock71'].iloc[0]
    return pd.DataFrame([
        {'parameter': 't0_mainshock64_utc', 'value': str(ms64['event_time'])},
        {'parameter': 't1_mainshock71_utc', 'value': str(ms71['event_time'])},
        {'parameter': 'time_bin_minutes', 'value': TIME_BIN_MINUTES},
        {'parameter': 'major_fault_min_activated_segments', 'value': MAJOR_FAULT_MIN_ACTIVATED_SEGMENTS},
        {'parameter': 'mw71_neighborhood_radius_km', 'value': MW71_NEIGHBORHOOD_RADIUS_KM},
        {'parameter': 'early_window_minutes', 'value': EARLY_WINDOW_MIN},
        {'parameter': 'mid_window_minutes', 'value': MID_WINDOW_MIN},
        {'parameter': 'bend_angle_threshold_deg', 'value': BEND_ANGLE_THRESHOLD_DEG},
        {'parameter': 'max_cores', 'value': MAX_CORES},
    ])


def build_interpretation_summary(sync_metrics: pd.DataFrame, line_metrics: pd.DataFrame, cross_fault: pd.DataFrame, mw71_summary: pd.DataFrame) -> pd.DataFrame:
    def get_metric(domain: str, metric: str) -> float:
        rows = sync_metrics.loc[(sync_metrics['domain'] == domain) & (sync_metrics['metric'] == metric), 'value']
        return float(rows.iloc[0]) if len(rows) else np.nan

    seg_60 = get_metric('fault_segments', 'fraction_activated_within_60min')
    seg_240 = get_metric('fault_segments', 'fraction_activated_within_240min')
    seg_iqr = get_metric('fault_segments', 'activation_time_iqr_minutes')
    eligible = line_metrics.loc[line_metrics['eligible_for_propagation']]
    progressive_fraction = float((eligible['classification'] == 'staged/progressive').mean()) if len(eligible) > 0 else np.nan
    jump_fraction = float((eligible['classification'] == 'jump-like').mean()) if len(eligible) > 0 else np.nan
    near_sync_fraction = float((eligible['classification'] == 'near-synchronous').mean()) if len(eligible) > 0 else np.nan
    mw71 = mw71_summary.iloc[0]
    cross_jump = float(cross_fault.loc[cross_fault['metric'] == 'cross_fault_jump_like_pairs_within_30min', 'value'].iloc[0]) if 'cross_fault_jump_like_pairs_within_30min' in set(cross_fault['metric']) else np.nan

    if np.isfinite(seg_60) and seg_60 >= 0.7 and np.isfinite(seg_iqr) and seg_iqr <= 60.0:
        system_style = 'Predominantly synchronous'
    elif np.isfinite(progressive_fraction) and progressive_fraction >= 0.4:
        system_style = 'Substantial staged/progressive activation on major faults'
    elif np.isfinite(jump_fraction) and jump_fraction >= 0.3:
        system_style = 'Cross-fault jump-like or distributed complex activation'
    else:
        system_style = 'Mixed / complex activation pattern'

    return pd.DataFrame([
        {'topic': 'system_style', 'summary': system_style},
        {'topic': 'fault_segment_activation_within_60min_fraction', 'summary': f'{seg_60:.3f}' if np.isfinite(seg_60) else 'nan'},
        {'topic': 'fault_segment_activation_within_240min_fraction', 'summary': f'{seg_240:.3f}' if np.isfinite(seg_240) else 'nan'},
        {'topic': 'fault_segment_activation_iqr_minutes', 'summary': f'{seg_iqr:.2f}' if np.isfinite(seg_iqr) else 'nan'},
        {'topic': 'major_fault_progressive_fraction', 'summary': f'{progressive_fraction:.3f}' if np.isfinite(progressive_fraction) else 'nan'},
        {'topic': 'major_fault_near_synchronous_fraction', 'summary': f'{near_sync_fraction:.3f}' if np.isfinite(near_sync_fraction) else 'nan'},
        {'topic': 'major_fault_jump_like_fraction', 'summary': f'{jump_fraction:.3f}' if np.isfinite(jump_fraction) else 'nan'},
        {'topic': 'cross_fault_jump_like_pairs_within_30min', 'summary': f'{cross_jump:.1f}' if np.isfinite(cross_jump) else 'nan'},
        {'topic': 'mw71_target_segment_activation_minutes', 'summary': f"{mw71['target_activation_minutes']:.2f}" if np.isfinite(mw71['target_activation_minutes']) else 'not activated'},
        {'topic': 'mw71_target_anomalously_late_vs_local', 'summary': str(bool(mw71['anomalously_late_vs_local']))},
        {'topic': 'mw71_target_anomalously_late_vs_system', 'summary': str(bool(mw71['anomalously_late_vs_system']))},
    ])


def main() -> None:
    table_dir, fig_dir = prepare_output_dir(OUTPUT_DIR)
    log(f'Writing outputs to {OUTPUT_DIR}')
    data = load_inputs()

    segment_activation = add_segment_geometry_diagnostics(data['segment_activation'])
    missing_endpoint_cols = [c for c in ['start_x_km', 'start_y_km', 'end_x_km', 'end_y_km'] if c not in segment_activation.columns]
    if 'segment_length_km' not in segment_activation.columns or missing_endpoint_cols:
        segment_activation = segment_activation.drop(columns=['segment_length_km', 'start_x_km', 'start_y_km', 'end_x_km', 'end_y_km'], errors='ignore')
        segment_activation = segment_activation.merge(
            data['segment_geom'][['global_segment_id', 'start_x_km', 'start_y_km', 'end_x_km', 'end_y_km', 'segment_length_km']].drop_duplicates('global_segment_id'),
            on='global_segment_id',
            how='left',
            validate='one_to_one',
        )
    required_post_merge = [
        'line_id', 'segment_id', 'global_segment_id', 'mid_x_km', 'mid_y_km', 'along_line_mid_km',
        'strike_deg', 'activated', 'activation_minutes', 'start_x_km', 'start_y_km', 'end_x_km', 'end_y_km', 'segment_length_km'
    ]
    require_columns(segment_activation, required_post_merge, 'segment_activation_post_merge')
    if segment_activation[['start_x_km', 'start_y_km', 'end_x_km', 'end_y_km', 'segment_length_km']].isna().any().any():
        raise ValueError('Failed to preserve segment endpoint geometry after merge')

    grid_distance, seg_distance = build_distance_metrics(data['grid_onset'], segment_activation, data['mainshock'])
    sync_metrics = compute_system_synchrony(grid_distance, seg_distance)
    dispersion_metrics = compute_activation_dispersion_by_class(seg_distance)
    line_metrics = compute_along_fault_metrics(seg_distance)
    cross_fault = compute_cross_fault_complexity(seg_distance)
    mw71_summary, mw71_neighborhood = compute_mw71_context(seg_distance, data['mainshock'])
    event_conservation = compute_event_conservation(data['filtered_events'], data['event_assoc'])
    validation_summary = make_validation_summary(data['filtered_events'], grid_distance, data['event_assoc'], seg_distance, line_metrics)
    run_parameters = make_run_parameters(data['mainshock'])
    interpretation_summary = build_interpretation_summary(sync_metrics, line_metrics, cross_fault, mw71_summary)

    # Save tables
    grid_distance.to_csv(table_dir / 'grid_cell_onset_enriched.csv', index=False)
    seg_distance.to_csv(table_dir / 'fault_segment_activation_enriched.csv', index=False)
    sync_metrics.to_csv(table_dir / 'system_synchrony_metrics.csv', index=False)
    dispersion_metrics.to_csv(table_dir / 'activation_dispersion_by_class.csv', index=False)
    line_metrics.to_csv(table_dir / 'per_fault_propagation_metrics.csv', index=False)
    line_metrics[['line_id', 'classification', 'eligible_for_propagation', 'n_activated_segments', 'activation_fraction', 'spearman_rho', 'slope_minutes_per_km', 'activation_span_km', 'activation_time_span_minutes']].to_csv(table_dir / 'fault_classification_table.csv', index=False)
    cross_fault.to_csv(table_dir / 'cross_fault_complexity_metrics.csv', index=False)
    mw71_summary.to_csv(table_dir / 'mw71_nucleation_segment_summary.csv', index=False)
    mw71_neighborhood.to_csv(table_dir / 'mw71_nucleation_neighborhood_segments.csv', index=False)
    event_conservation.to_csv(table_dir / 'event_count_conservation.csv', index=False)
    validation_summary.to_csv(table_dir / 'validation_summary.csv', index=False)
    run_parameters.to_csv(table_dir / 'run_parameters.csv', index=False)
    interpretation_summary.to_csv(table_dir / 'interpretation_summary.csv', index=False)

    # Figures
    plot_scatter_distance(seg_distance, 'distance_to_mw64_km', 'Distance from Mw 6.4 epicenter (km)', fig_dir / 'activation_time_vs_distance_mw64.png')
    plot_scatter_distance(seg_distance, 'distance_to_mw71_km', 'Distance from Mw 7.1 epicenter (km)', fig_dir / 'activation_time_vs_distance_mw71.png')
    plot_along_fault_panels(seg_distance, line_metrics, fig_dir / 'along_fault_distance_vs_activation_time_major_faults.png')
    plot_activation_stage_map(seg_distance, data['mainshock'], fig_dir / 'early_intermediate_late_fault_segment_map.png')
    plot_mw71_context(mw71_neighborhood, data['mainshock'], fig_dir / 'mw71_nucleation_local_context.png')
    plot_activation_map_comparison(grid_distance, seg_distance, fig_dir / 'gridded_vs_fault_activation_map_comparison.png')

    # Basic validation
    if int(validation_summary.loc[validation_summary['metric'] == 'activated_fault_segments', 'value'].iloc[0]) <= 0:
        raise ValueError('No activated fault segments available in final outputs')
    if int(validation_summary.loc[validation_summary['metric'] == 'occupied_grid_cells', 'value'].iloc[0]) <= 0:
        raise ValueError('No occupied grid cells available in final outputs')
    if mw71_summary.empty:
        raise ValueError('Mw 7.1 nucleation summary is empty')

    log('Task 03 complete: triggering-style diagnostics and packaged deliverables written successfully')


if __name__ == '__main__':
    try:
        main()
    except Exception:
        print(traceback.format_exc(), flush=True)
        sys.exit(1)
