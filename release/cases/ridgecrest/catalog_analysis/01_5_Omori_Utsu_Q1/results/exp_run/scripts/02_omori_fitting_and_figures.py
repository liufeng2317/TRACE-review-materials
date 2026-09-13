from __future__ import annotations

import json
import math
import os
import sys
import traceback
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import minimize


INPUT_DIR = Path('<REPO_ROOT>/examples/ridgecrest/catalog_analysis/run/01_5_trigger_Omori_Utsu_Q1-v2/exp_run/outputs/01_domain_preparation')
OUTPUT_DIR = Path('<REPO_ROOT>/examples/ridgecrest/catalog_analysis/run/01_5_trigger_Omori_Utsu_Q1-v2/exp_run/outputs/02_omori_fitting_and_figures')
SCRIPT_PATH = Path('<REPO_ROOT>/examples/ridgecrest/catalog_analysis/run/01_5_trigger_Omori_Utsu_Q1-v2/exp_run/scripts/02_omori_fitting_and_figures.py')

EVENT_TABLE_CSV = INPUT_DIR / 'interevent_domain_event_table.csv'
DOMAIN_COUNTS_CSV = INPUT_DIR / 'domain_counts_primary.csv'
METADATA_JSON_IN = INPUT_DIR / 'domain_metadata.json'
DOMAIN_CHECKS_CSV = INPUT_DIR / 'domain_assignment_checks.csv'

PRIMARY_FIT_CSV = OUTPUT_DIR / 'primary_fit_table.csv'
FIT_AUDIT_CSV = OUTPUT_DIR / 'fit_input_audit_table.csv'
BOOTSTRAP_SUMMARY_CSV = OUTPUT_DIR / 'bootstrap_summary.csv'
FINAL_RESULTS_CSV = OUTPUT_DIR / 'final_merged_primary_results.csv'
PANELB_RATE_CSV = OUTPUT_DIR / 'panel_b_rate_curve_support.csv'
MAIN_FIGURE_PNG = OUTPUT_DIR / 'main_two_panel_omori_comparison.png'
SPLIT_RESULTS_CSV = OUTPUT_DIR / 'split_sensitivity_results.csv'
SPLIT_FIGURE_PNG = OUTPUT_DIR / 'split_sensitivity_summary.png'
PRIMARY_COMPARISON_CSV = OUTPUT_DIR / 'north_vs_south_primary_comparison_35p72.csv'
WORKFLOW_MANIFEST_JSON = OUTPUT_DIR / 'workflow_manifest.json'
RUN_METADATA_JSON = OUTPUT_DIR / 'run_metadata.json'

OUTPUT_FILES = [
    PRIMARY_FIT_CSV,
    FIT_AUDIT_CSV,
    BOOTSTRAP_SUMMARY_CSV,
    FINAL_RESULTS_CSV,
    PANELB_RATE_CSV,
    MAIN_FIGURE_PNG,
    SPLIT_RESULTS_CSV,
    SPLIT_FIGURE_PNG,
    PRIMARY_COMPARISON_CSV,
    WORKFLOW_MANIFEST_JSON,
    RUN_METADATA_JSON,
]

PRIMARY_MAG_THRESHOLD = 3.0
PRIMARY_SPLIT_LAT = 35.72
SPLIT_LATS = [35.70, 35.72, 35.74]
PERIOD_ENDPOINTS_DAYS = [0.30, 0.50, 0.68, 0.732, 0.85, 1.00, 1.10, 1.22, 1.404]
M54_SEPARATOR_DAYS = 0.732
FINAL_PERIOD_DAYS = 1.404
MIN_EVENTS_TO_FIT = 5
BOOTSTRAP_REPLICATES = 1000
RATE_BIN_COUNT = 12
P_BOUNDS = (0.2, 2.5)
C_BOUNDS_DAYS = (1.0e-5, 1.0)
DOMAIN_SPECS = {
    'Entire area': 'in_entire_corridor',
    'Northern area': 'north_35p72',
    'Southern area': 'south_35p72',
}
DOMAIN_COLORS = {
    'Entire area': '0.45',
    'Northern area': 'tab:blue',
    'Southern area': 'tab:red',
}
OPEN_CIRCLE_THRESHOLD = 20
EPS_TIME = 1e-12


@dataclass
class FitResult:
    domain_label: str
    domain_flag_column: str
    split_latitude_deg: float | None
    period_days: float
    event_count: int
    success_flag: bool
    failure_reason: str
    p_fit: float
    c_fit: float
    k_fit: float
    log_likelihood: float
    t_min_used_days: float
    t_max_used_days: float
    sum_log_t: float
    low_count_open_circle: bool


def log(message: str) -> None:
    print(message, flush=True)


def remove_stale_outputs() -> None:
    for path in OUTPUT_FILES:
        if path.exists():
            log(f'Removing stale output: {path}')
            path.unlink()


def validate_inputs() -> None:
    required = [EVENT_TABLE_CSV, DOMAIN_COUNTS_CSV, METADATA_JSON_IN, DOMAIN_CHECKS_CSV]
    for path in required:
        if not path.exists():
            raise FileNotFoundError(f'Required input not found: {path}')


def load_inputs() -> tuple[pd.DataFrame, dict[str, Any]]:
    log(f'Reading event table: {EVENT_TABLE_CSV}')
    events = pd.read_csv(EVENT_TABLE_CSV)
    with open(METADATA_JSON_IN, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
    required_cols = [
        'event_time', 'magnitude', 't_days',
        'in_entire_corridor', 'north_35p70', 'south_35p70',
        'north_35p72', 'south_35p72', 'north_35p74', 'south_35p74',
    ]
    missing = [c for c in required_cols if c not in events.columns]
    if missing:
        raise ValueError(f'Missing required columns in event table: {missing}')
    events['event_time'] = pd.to_datetime(events['event_time'], utc=True)
    if events['t_days'].isna().any():
        raise ValueError('Found NaN values in t_days.')
    for col in [c for c in events.columns if c.startswith(('in_', 'north_', 'south_', 'on_split_'))]:
        events[col] = events[col].astype(bool)
    events = events.sort_values('t_days').reset_index(drop=True)
    return events, metadata


def domain_specs_for_split(split_lat: float, include_entire: bool) -> list[tuple[str, str, float | None]]:
    token = f'{split_lat:.2f}'.replace('.', 'p')
    specs: list[tuple[str, str, float | None]] = []
    if include_entire:
        specs.append(('Entire area', 'in_entire_corridor', None))
    specs.append((f'Northern area @ {split_lat:.2f}', f'north_{token}', split_lat))
    specs.append((f'Southern area @ {split_lat:.2f}', f'south_{token}', split_lat))
    return specs


def stable_integral(t_min: float, t_max: float, p: float, c_days: float) -> float:
    if not (np.isfinite(t_min) and np.isfinite(t_max) and np.isfinite(p) and np.isfinite(c_days)):
        return np.nan
    if t_min < 0 or t_max <= t_min or c_days <= 0:
        return np.nan
    shifted_min = c_days + t_min
    shifted_max = c_days + t_max
    if abs(p - 1.0) < 1e-8:
        return math.log(shifted_max / shifted_min)
    log_ratio = math.log(shifted_max / shifted_min)
    exponent = 1.0 - p
    if abs(exponent * log_ratio) < 1e-6:
        return (shifted_min ** exponent) * math.expm1(exponent * log_ratio) / exponent
    return (shifted_max ** exponent - shifted_min ** exponent) / exponent


def mle_omori_utsu_from_times(
    times: np.ndarray,
    t_end_days: float,
    start_params: tuple[float, float] | None = None,
    multistart: bool = True,
) -> tuple[bool, dict[str, Any]]:
    times = np.asarray(times, dtype=float)
    times = times[np.isfinite(times)]
    times = times[(times > 0.0) & (times <= t_end_days)]
    if times.size < MIN_EVENTS_TO_FIT:
        return False, {'failure_reason': f'too_few_events_lt_{MIN_EVENTS_TO_FIT}', 'event_count': int(times.size)}
    times = np.sort(times)
    t_min = float(times.min())
    t_max = float(t_end_days)
    if t_min <= 0:
        return False, {'failure_reason': 'non_positive_event_time', 'event_count': int(times.size)}
    if t_max <= t_min:
        return False, {'failure_reason': 'degenerate_time_window', 'event_count': int(times.size)}

    n = int(times.size)
    log_c_bounds = (math.log(C_BOUNDS_DAYS[0]), math.log(C_BOUNDS_DAYS[1]))

    def objective(theta: np.ndarray) -> float:
        p = float(theta[0])
        c_days = float(math.exp(theta[1]))
        integral = stable_integral(t_min, t_max, p, c_days)
        if not np.isfinite(integral) or integral <= 0:
            return 1.0e100
        shifted = c_days + times
        if not np.isfinite(shifted).all() or np.any(shifted <= 0):
            return 1.0e100
        k = n / integral
        log_likelihood = n * math.log(k) - p * float(np.log(shifted).sum()) - k * integral
        if not np.isfinite(log_likelihood):
            return 1.0e100
        return -log_likelihood

    if start_params is not None:
        starts = [start_params]
    elif multistart:
        starts = [(p0, c0) for p0 in (0.6, 1.0, 1.4) for c0 in (C_BOUNDS_DAYS[0], 1.0e-3, 1.0e-2, 5.0e-2)]
    else:
        starts = [(1.0, 1.0e-3)]

    best = None
    for p0, c0 in starts:
        x0 = np.array([
            float(np.clip(p0, *P_BOUNDS)),
            math.log(float(np.clip(c0, *C_BOUNDS_DAYS))),
        ])
        res = minimize(
            objective,
            x0=x0,
            method='L-BFGS-B',
            bounds=[P_BOUNDS, log_c_bounds],
            options={'maxiter': 500, 'ftol': 1e-10},
        )
        if res.success and np.isfinite(res.fun) and (best is None or res.fun < best.fun):
            best = res

    if best is None:
        return False, {
            'failure_reason': 'likelihood_optimization_failed',
            'event_count': n,
            't_min_used_days': t_min,
            't_max_used_days': t_max,
        }

    p_hat = float(best.x[0])
    c_hat = float(math.exp(best.x[1]))
    integral = stable_integral(t_min, t_max, p_hat, c_hat)
    if not np.isfinite(integral) or integral <= 0:
        return False, {
            'failure_reason': 'invalid_integral_at_solution',
            'event_count': n,
            't_min_used_days': t_min,
            't_max_used_days': t_max,
        }
    k_hat = n / integral
    if not np.isfinite(k_hat) or k_hat <= 0:
        return False, {
            'failure_reason': 'invalid_k_at_solution',
            'event_count': n,
            't_min_used_days': t_min,
            't_max_used_days': t_max,
        }
    sum_log_t = float(np.log(c_hat + times).sum())
    log_likelihood = n * math.log(k_hat) - p_hat * sum_log_t - k_hat * integral
    if not np.isfinite(log_likelihood):
        return False, {
            'failure_reason': 'non_finite_log_likelihood',
            'event_count': n,
            't_min_used_days': t_min,
            't_max_used_days': t_max,
        }

    return True, {
        'failure_reason': '',
        'event_count': n,
        'p_fit': float(p_hat),
        'c_fit': float(c_hat),
        'k_fit': float(k_hat),
        'log_likelihood': float(log_likelihood),
        't_min_used_days': t_min,
        't_max_used_days': t_max,
        'sum_log_t': sum_log_t,
    }


def fit_one_window(domain_label: str, flag_column: str, split_latitude_deg: float | None, period_days: float, times: np.ndarray) -> FitResult:
    ok, payload = mle_omori_utsu_from_times(times, float(period_days))
    low_count_flag = (domain_label.startswith('Northern area') and len(times) <= OPEN_CIRCLE_THRESHOLD)
    if not ok:
        return FitResult(
            domain_label=domain_label,
            domain_flag_column=flag_column,
            split_latitude_deg=split_latitude_deg,
            period_days=float(period_days),
            event_count=int(payload.get('event_count', len(times))),
            success_flag=False,
            failure_reason=str(payload.get('failure_reason', 'fit_failed')),
            p_fit=np.nan,
            c_fit=np.nan,
            k_fit=np.nan,
            log_likelihood=np.nan,
            t_min_used_days=float(payload.get('t_min_used_days', np.nan)),
            t_max_used_days=float(payload.get('t_max_used_days', period_days)),
            sum_log_t=np.nan,
            low_count_open_circle=bool(low_count_flag),
        )
    return FitResult(
        domain_label=domain_label,
        domain_flag_column=flag_column,
        split_latitude_deg=split_latitude_deg,
        period_days=float(period_days),
        event_count=int(payload['event_count']),
        success_flag=True,
        failure_reason='',
        p_fit=float(payload['p_fit']),
        c_fit=float(payload['c_fit']),
        k_fit=float(payload['k_fit']),
        log_likelihood=float(payload['log_likelihood']),
        t_min_used_days=float(payload['t_min_used_days']),
        t_max_used_days=float(payload['t_max_used_days']),
        sum_log_t=float(payload['sum_log_t']),
        low_count_open_circle=bool(low_count_flag),
    )


def build_fit_tables(events: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    log('Building primary fit table and audit table.')
    primary_events = events.loc[events['magnitude'] >= PRIMARY_MAG_THRESHOLD].copy()
    fit_rows: list[dict[str, Any]] = []
    audit_rows: list[dict[str, Any]] = []
    for domain_label, flag_col in DOMAIN_SPECS.items():
        domain_series = primary_events[flag_col].to_numpy(dtype=bool)
        domain_times_all = primary_events.loc[domain_series, 't_days'].to_numpy(dtype=float)
        for period in PERIOD_ENDPOINTS_DAYS:
            times = domain_times_all[(domain_times_all > 0.0) & (domain_times_all <= period + EPS_TIME)]
            result = fit_one_window(domain_label, flag_col, PRIMARY_SPLIT_LAT if domain_label != 'Entire area' else None, period, times)
            fit_rows.append(result.__dict__)
            if len(times) > 0:
                for i, t in enumerate(np.sort(times), start=1):
                    audit_rows.append({
                        'domain_label': domain_label,
                        'domain_flag_column': flag_col,
                        'split_latitude_deg': PRIMARY_SPLIT_LAT if domain_label != 'Entire area' else np.nan,
                        'period_days': float(period),
                        'event_index_within_window': i,
                        'event_time_days': float(t),
                    })
            else:
                audit_rows.append({
                    'domain_label': domain_label,
                    'domain_flag_column': flag_col,
                    'split_latitude_deg': PRIMARY_SPLIT_LAT if domain_label != 'Entire area' else np.nan,
                    'period_days': float(period),
                    'event_index_within_window': np.nan,
                    'event_time_days': np.nan,
                })
    fit_df = pd.DataFrame(fit_rows)
    audit_df = pd.DataFrame(audit_rows)
    return fit_df, audit_df


def bootstrap_worker(times: np.ndarray, period_days: float, n_boot: int, seed: int, start_params: tuple[float, float] | None) -> dict[str, Any]:
    rng = np.random.default_rng(seed)
    times = np.asarray(times, dtype=float)
    n = len(times)
    p_values = []
    failures = 0
    for _ in range(n_boot):
        sample = rng.choice(times, size=n, replace=True)
        ok, payload = mle_omori_utsu_from_times(np.sort(sample), float(period_days), multistart=False, start_params=start_params)
        if ok:
            p_values.append(float(payload['p_fit']))
        else:
            failures += 1
    return {'p_values': p_values, 'failures': failures}


def summarize_bootstrap(result_row: pd.Series, times: np.ndarray, max_workers: int) -> dict[str, Any]:
    if not bool(result_row['success_flag']):
        return {
            'domain_label': result_row['domain_label'],
            'period_days': float(result_row['period_days']),
            'bootstrap_replicates_requested': BOOTSTRAP_REPLICATES,
            'bootstrap_success_count': 0,
            'bootstrap_failure_count': 0,
            'bootstrap_success_fraction': np.nan,
            'bootstrap_p_median': np.nan,
            'bootstrap_p_q025': np.nan,
            'bootstrap_p_q975': np.nan,
            'bootstrap_warning': 'primary_fit_failed',
        }
    n_workers = max(1, min(max_workers, 8, BOOTSTRAP_REPLICATES))
    replicate_splits = [BOOTSTRAP_REPLICATES // n_workers] * n_workers
    for i in range(BOOTSTRAP_REPLICATES % n_workers):
        replicate_splits[i] += 1
    seeds = np.random.SeedSequence(20250707 + int(round(1000 * float(result_row['period_days'])))).spawn(n_workers)
    start_params = None
    if np.isfinite(result_row.get('p_fit', np.nan)) and np.isfinite(result_row.get('c_fit', np.nan)):
        start_params = (float(result_row['p_fit']), float(result_row['c_fit']))
    futures = []
    all_ps: list[float] = []
    fail_count = 0
    with ProcessPoolExecutor(max_workers=n_workers) as ex:
        for child_seed, n_boot in zip(seeds, replicate_splits):
            if n_boot <= 0:
                continue
            futures.append(ex.submit(bootstrap_worker, times, float(result_row['period_days']), int(n_boot), int(child_seed.generate_state(1)[0]), start_params))
        for future in as_completed(futures):
            out = future.result()
            all_ps.extend(out['p_values'])
            fail_count += int(out['failures'])
    success_count = len(all_ps)
    success_fraction = success_count / BOOTSTRAP_REPLICATES if BOOTSTRAP_REPLICATES > 0 else np.nan
    warning = ''
    if success_count == 0:
        warning = 'all_bootstrap_replicates_failed'
        return {
            'domain_label': result_row['domain_label'],
            'period_days': float(result_row['period_days']),
            'bootstrap_replicates_requested': BOOTSTRAP_REPLICATES,
            'bootstrap_success_count': 0,
            'bootstrap_failure_count': int(fail_count),
            'bootstrap_success_fraction': success_fraction,
            'bootstrap_p_median': np.nan,
            'bootstrap_p_q025': np.nan,
            'bootstrap_p_q975': np.nan,
            'bootstrap_warning': warning,
        }
    arr = np.asarray(all_ps, dtype=float)
    if success_fraction < 0.8:
        warning = 'bootstrap_success_fraction_below_0p8'
    return {
        'domain_label': result_row['domain_label'],
        'period_days': float(result_row['period_days']),
        'bootstrap_replicates_requested': BOOTSTRAP_REPLICATES,
        'bootstrap_success_count': int(success_count),
        'bootstrap_failure_count': int(fail_count),
        'bootstrap_success_fraction': float(success_fraction),
        'bootstrap_p_median': float(np.nanmedian(arr)),
        'bootstrap_p_q025': float(np.nanpercentile(arr, 2.5)),
        'bootstrap_p_q975': float(np.nanpercentile(arr, 97.5)),
        'bootstrap_warning': warning,
    }


def run_bootstrap_for_primary(events: pd.DataFrame, fit_df: pd.DataFrame) -> pd.DataFrame:
    primary_events = events.loc[events['magnitude'] >= PRIMARY_MAG_THRESHOLD].copy()
    max_workers = max(1, min((os.cpu_count() or 1), 8))
    log(f'Running bootstrap summaries with up to {max_workers} worker processes and {BOOTSTRAP_REPLICATES} replicates per successful window.')
    summaries = []
    for idx, row in fit_df.iterrows():
        log(f'Bootstrap {idx + 1}/{len(fit_df)}: domain={row["domain_label"]}, period={row["period_days"]:.3f} day, N={row["event_count"]}, success={row["success_flag"]}')
        mask = primary_events[row['domain_flag_column']].to_numpy(dtype=bool)
        times = primary_events.loc[mask & (primary_events['t_days'] > 0.0) & (primary_events['t_days'] <= float(row['period_days']) + EPS_TIME), 't_days'].to_numpy(dtype=float)
        summaries.append(summarize_bootstrap(row, times, max_workers))
    return pd.DataFrame(summaries)


def build_panel_b_support(events: pd.DataFrame, final_entire_row: pd.Series) -> pd.DataFrame:
    primary_events = events.loc[events['magnitude'] >= PRIMARY_MAG_THRESHOLD].copy()
    times = primary_events.loc[
        primary_events['in_entire_corridor'] & (primary_events['t_days'] > 0.0) & (primary_events['t_days'] <= FINAL_PERIOD_DAYS + EPS_TIME),
        't_days'
    ].to_numpy(dtype=float)
    times = np.sort(times)
    if len(times) == 0:
        raise ValueError('No entire-area M>=3 events available for panel b.')
    t_min = max(float(times.min()), 1e-5)
    edges = np.geomspace(t_min, FINAL_PERIOD_DAYS, RATE_BIN_COUNT + 1)
    counts, edges = np.histogram(times, bins=edges)
    mids = np.sqrt(edges[:-1] * edges[1:])
    widths = np.diff(edges)
    observed = counts / widths
    fitted = float(final_entire_row['k_fit']) * np.power(float(final_entire_row['c_fit']) + mids, -float(final_entire_row['p_fit']))
    return pd.DataFrame({
        'bin_left_day': edges[:-1],
        'bin_right_day': edges[1:],
        'bin_mid_day': mids,
        'bin_width_day': widths,
        'count': counts,
        'observed_rate_day_inv': observed,
        'fitted_rate_day_inv': fitted,
    })


def make_main_figure(final_df: pd.DataFrame, panel_b_df: pd.DataFrame, metadata: dict[str, Any]) -> None:
    log(f'Creating main two-panel figure: {MAIN_FIGURE_PNG}')
    fig, axes = plt.subplots(1, 2, figsize=(12.2, 5.4), constrained_layout=True)
    ax = axes[0]

    for domain_label in ['Entire area', 'Northern area', 'Southern area']:
        sub = final_df.loc[final_df['domain_label'] == domain_label].sort_values('period_days')
        sub_success = sub.loc[sub['success_flag']].copy()
        if sub_success.empty:
            continue
        color = DOMAIN_COLORS[domain_label]
        plot_sub = sub_success.loc[
            np.isfinite(sub_success['p_fit']) &
            np.isfinite(sub_success['bootstrap_p_q025']) &
            np.isfinite(sub_success['bootstrap_p_q975'])
        ].copy()
        if plot_sub.empty:
            continue
        if domain_label == 'Northern area':
            open_mask = plot_sub['low_count_open_circle'].fillna(False).to_numpy(dtype=bool)
            filled = plot_sub.loc[~open_mask]
            open_df = plot_sub.loc[open_mask]
            if not filled.empty:
                ax.errorbar(
                    filled['period_days'], filled['p_fit'],
                    yerr=np.vstack([
                        filled['p_fit'] - filled['bootstrap_p_q025'],
                        filled['bootstrap_p_q975'] - filled['p_fit'],
                    ]),
                    fmt='o', ms=5.5, color=color, ecolor=color, elinewidth=1.0, capsize=2.5,
                    label=domain_label,
                )
            if not open_df.empty:
                ax.errorbar(
                    open_df['period_days'], open_df['p_fit'],
                    yerr=np.vstack([
                        open_df['p_fit'] - open_df['bootstrap_p_q025'],
                        open_df['bootstrap_p_q975'] - open_df['p_fit'],
                    ]),
                    fmt='o', ms=6.0, mfc='white', mec=color, color=color, ecolor=color,
                    elinewidth=1.0, capsize=2.5, label=f'{domain_label} (N≤20)',
                )
        else:
            ax.errorbar(
                plot_sub['period_days'], plot_sub['p_fit'],
                yerr=np.vstack([
                    plot_sub['p_fit'] - plot_sub['bootstrap_p_q025'],
                    plot_sub['bootstrap_p_q975'] - plot_sub['p_fit'],
                ]),
                fmt='o', ms=5.5, color=color, ecolor=color, elinewidth=1.0, capsize=2.5,
                label=domain_label,
            )

    for xpos in [0.0, M54_SEPARATOR_DAYS, FINAL_PERIOD_DAYS]:
        ax.axvline(xpos, color='0.5', ls='--', lw=1.0)
    ax.set_xlabel('Period [day]')
    ax.set_ylabel('p value')
    ax.set_xlim(-0.02, FINAL_PERIOD_DAYS + 0.05)
    ax.grid(True, color='0.9', linewidth=0.8)
    ax.legend(loc='best', fontsize=8, frameon=True)
    ax.text(0.02, 0.98, 'a', transform=ax.transAxes, ha='left', va='top', fontsize=13, fontweight='bold')

    ax2 = axes[1]
    support = panel_b_df.loc[panel_b_df['count'] > 0].copy()
    ax2.scatter(support['bin_mid_day'], support['observed_rate_day_inv'], s=26, c='k', label='Observed binned rate')
    full_curve_t = np.geomspace(panel_b_df['bin_left_day'].min(), panel_b_df['bin_right_day'].max(), 400)
    final_entire = final_df.loc[(final_df['domain_label'] == 'Entire area') & (np.isclose(final_df['period_days'], FINAL_PERIOD_DAYS))]
    if final_entire.empty:
        raise ValueError('Missing final entire-area result for panel b.')
    row = final_entire.iloc[0]
    full_curve_y = float(row['k_fit']) * np.power(float(row['c_fit']) + full_curve_t, -float(row['p_fit']))
    ax2.plot(full_curve_t, full_curve_y, color='0.35', lw=1.8, label='Fitted Omori-Utsu rate')
    ax2.set_xscale('log')
    ax2.set_yscale('log')
    ax2.set_xlabel('Time since Mw 6.4 [day]')
    ax2.set_ylabel(r'$\lambda$ [day$^{-1}$]')
    ax2.grid(True, which='both', color='0.9', linewidth=0.8)
    txt = (
        f'p = {row["p_fit"]:.2f} '\
        f'[{row["bootstrap_p_q025"]:.2f}, {row["bootstrap_p_q975"]:.2f}]\n'
        f'c = {row["c_fit"]:.3g} day\n'
        f'Period = {FINAL_PERIOD_DAYS:.3f} day\n'
        f'N = {int(row["event_count"])}'
    )
    ax2.text(0.04, 0.96, txt, transform=ax2.transAxes, ha='left', va='top', fontsize=9,
             bbox=dict(facecolor='white', edgecolor='0.8', boxstyle='round,pad=0.25'))
    ax2.legend(loc='lower left', fontsize=8, frameon=True)
    ax2.text(0.02, 0.98, 'b', transform=ax2.transAxes, ha='left', va='top', fontsize=13, fontweight='bold')

    fig.savefig(MAIN_FIGURE_PNG, dpi=240)
    plt.close(fig)


def fit_split_sensitivity(events: pd.DataFrame) -> pd.DataFrame:
    primary_events = events.loc[events['magnitude'] >= PRIMARY_MAG_THRESHOLD].copy()
    rows = []
    for split_lat in SPLIT_LATS:
        log(f'Fitting split sensitivity for split latitude {split_lat:.2f}°N')
        for domain_label, flag_col, split_value in domain_specs_for_split(split_lat, include_entire=False):
            times_all = primary_events.loc[primary_events[flag_col], 't_days'].to_numpy(dtype=float)
            for period in PERIOD_ENDPOINTS_DAYS:
                times = times_all[(times_all > 0.0) & (times_all <= period + EPS_TIME)]
                fit = fit_one_window(domain_label, flag_col, split_value, period, times)
                row = fit.__dict__.copy()
                row['base_domain'] = 'Northern area' if domain_label.startswith('Northern area') else 'Southern area'
                rows.append(row)
    split_df = pd.DataFrame(rows)
    return split_df


def make_split_figure(split_df: pd.DataFrame) -> None:
    log(f'Creating split-sensitivity figure: {SPLIT_FIGURE_PNG}')
    fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.3), sharey=True, constrained_layout=True)
    for ax, split_lat in zip(axes, SPLIT_LATS):
        for base_domain, color in [('Northern area', 'tab:blue'), ('Southern area', 'tab:red')]:
            sub = split_df.loc[
                (split_df['split_latitude_deg'] == split_lat) &
                (split_df['base_domain'] == base_domain) &
                (split_df['success_flag'])
            ].sort_values('period_days')
            if sub.empty:
                continue
            ax.plot(sub['period_days'], sub['p_fit'], marker='o', ms=4.5, color=color, label=base_domain)
        ax.axvline(M54_SEPARATOR_DAYS, color='0.6', ls='--', lw=1.0)
        ax.axvline(FINAL_PERIOD_DAYS, color='0.6', ls='--', lw=1.0)
        ax.set_title(f'Split = {split_lat:.2f}°N')
        ax.set_xlabel('Period [day]')
        ax.grid(True, color='0.9', linewidth=0.8)
    axes[0].set_ylabel('p value')
    axes[0].legend(loc='best', fontsize=8, frameon=True)
    fig.savefig(SPLIT_FIGURE_PNG, dpi=220)
    plt.close(fig)


def build_primary_comparison(final_df: pd.DataFrame) -> pd.DataFrame:
    north = final_df.loc[final_df['domain_label'] == 'Northern area'].copy()
    south = final_df.loc[final_df['domain_label'] == 'Southern area'].copy()
    merged = north.merge(south, on='period_days', suffixes=('_north', '_south'))
    rows = []
    for _, row in merged.iterrows():
        overlap = False
        if np.isfinite(row['bootstrap_p_q025_north']) and np.isfinite(row['bootstrap_p_q975_north']) and np.isfinite(row['bootstrap_p_q025_south']) and np.isfinite(row['bootstrap_p_q975_south']):
            overlap = not (row['bootstrap_p_q975_north'] < row['bootstrap_p_q025_south'] or row['bootstrap_p_q975_south'] < row['bootstrap_p_q025_north'])
        rows.append({
            'period_days': float(row['period_days']),
            'north_success_flag': bool(row['success_flag_north']),
            'south_success_flag': bool(row['success_flag_south']),
            'north_event_count': int(row['event_count_north']),
            'south_event_count': int(row['event_count_south']),
            'north_p_fit': float(row['p_fit_north']) if np.isfinite(row['p_fit_north']) else np.nan,
            'south_p_fit': float(row['p_fit_south']) if np.isfinite(row['p_fit_south']) else np.nan,
            'north_minus_south_p_fit': float(row['p_fit_north'] - row['p_fit_south']) if np.isfinite(row['p_fit_north']) and np.isfinite(row['p_fit_south']) else np.nan,
            'north_bootstrap_p_median': float(row['bootstrap_p_median_north']) if np.isfinite(row['bootstrap_p_median_north']) else np.nan,
            'south_bootstrap_p_median': float(row['bootstrap_p_median_south']) if np.isfinite(row['bootstrap_p_median_south']) else np.nan,
            'north_minus_south_bootstrap_median': float(row['bootstrap_p_median_north'] - row['bootstrap_p_median_south']) if np.isfinite(row['bootstrap_p_median_north']) and np.isfinite(row['bootstrap_p_median_south']) else np.nan,
            'bootstrap_interval_overlap_flag': bool(overlap),
            'north_low_count_open_circle': bool(row['low_count_open_circle_north']),
            'later_period_flag': bool(float(row['period_days']) >= 1.10),
        })
    return pd.DataFrame(rows).sort_values('period_days').reset_index(drop=True)


def save_run_metadata(input_metadata: dict[str, Any], fit_df: pd.DataFrame, bootstrap_df: pd.DataFrame) -> None:
    run_metadata = {
        'input_metadata_path': str(METADATA_JSON_IN),
        'event_table_path': str(EVENT_TABLE_CSV),
        'primary_magnitude_threshold': PRIMARY_MAG_THRESHOLD,
        'primary_split_latitude_deg': PRIMARY_SPLIT_LAT,
        'robustness_split_latitudes_deg': SPLIT_LATS,
        'period_endpoints_days': PERIOD_ENDPOINTS_DAYS,
        'm54_separator_period_days': M54_SEPARATOR_DAYS,
        'final_period_days': FINAL_PERIOD_DAYS,
        'minimum_events_to_fit': MIN_EVENTS_TO_FIT,
        'bootstrap_replicates': BOOTSTRAP_REPLICATES,
        'omori_utsu_rate_model': 'lambda(t) = K * (c + t)^(-p)',
        'p_bounds': P_BOUNDS,
        'c_bounds_days': C_BOUNDS_DAYS,
        'cpu_count_detected': os.cpu_count(),
        'successful_primary_windows': int(fit_df['success_flag'].sum()),
        'failed_primary_windows': int((~fit_df['success_flag']).sum()),
        'bootstrap_windows_with_warning': int((bootstrap_df['bootstrap_warning'].fillna('') != '').sum()),
        'mw64_time_utc': input_metadata['mw64_time_utc'],
        'mw71_time_utc': input_metadata['mw71_time_utc'],
        'corridor_geometry': input_metadata['corridor_geometry'],
    }
    with open(RUN_METADATA_JSON, 'w', encoding='utf-8') as f:
        json.dump(run_metadata, f, indent=2)


def save_manifest() -> None:
    manifest = {
        'outputs': [
            {'path': str(PRIMARY_FIT_CSV), 'description': 'Primary cumulative Omori-Utsu fit table for lambda(t)=K*(c+t)^(-p).'},
            {'path': str(FIT_AUDIT_CSV), 'description': 'Event-time audit table for each primary fit window.'},
            {'path': str(BOOTSTRAP_SUMMARY_CSV), 'description': 'Bootstrap uncertainty summaries for primary windows.'},
            {'path': str(FINAL_RESULTS_CSV), 'description': 'Merged primary results with fit and bootstrap fields.'},
            {'path': str(PANELB_RATE_CSV), 'description': 'Observed/fitted rate support table for main-figure panel b.'},
            {'path': str(MAIN_FIGURE_PNG), 'description': 'Required main two-panel Omori comparison figure.'},
            {'path': str(SPLIT_RESULTS_CSV), 'description': 'North/south split-sensitivity fit results for 35.70/35.72/35.74.'},
            {'path': str(SPLIT_FIGURE_PNG), 'description': 'Optional split-sensitivity summary figure.'},
            {'path': str(PRIMARY_COMPARISON_CSV), 'description': 'Primary north-vs-south comparison table for 35.72 split.'},
            {'path': str(RUN_METADATA_JSON), 'description': 'Run metadata and configuration summary.'},
            {'path': str(WORKFLOW_MANIFEST_JSON), 'description': 'Manifest of this task outputs.'},
        ]
    }
    with open(WORKFLOW_MANIFEST_JSON, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    log(f'Output directory: {OUTPUT_DIR}')
    validate_inputs()
    remove_stale_outputs()
    events, input_metadata = load_inputs()

    fit_df, audit_df = build_fit_tables(events)
    log(f'Saving primary fit table: {PRIMARY_FIT_CSV}')
    fit_df.to_csv(PRIMARY_FIT_CSV, index=False)
    log(f'Saving fit audit table: {FIT_AUDIT_CSV}')
    audit_df.to_csv(FIT_AUDIT_CSV, index=False)

    bootstrap_df = run_bootstrap_for_primary(events, fit_df)
    log(f'Saving bootstrap summary: {BOOTSTRAP_SUMMARY_CSV}')
    bootstrap_df.to_csv(BOOTSTRAP_SUMMARY_CSV, index=False)

    final_df = fit_df.merge(bootstrap_df, on=['domain_label', 'period_days'], how='left', validate='one_to_one')
    required_final_cols = [
        'domain_label', 'period_days', 'event_count', 'success_flag', 'failure_reason',
        'p_fit', 'c_fit', 'k_fit', 't_min_used_days', 't_max_used_days', 'low_count_open_circle',
        'bootstrap_p_median', 'bootstrap_p_q025', 'bootstrap_p_q975',
        'bootstrap_success_count', 'bootstrap_failure_count', 'bootstrap_success_fraction',
    ]
    missing_final = [c for c in required_final_cols if c not in final_df.columns]
    if missing_final:
        raise ValueError(f'Missing required columns after merging fit and bootstrap results: {missing_final}')
    log(f'Saving merged primary results: {FINAL_RESULTS_CSV}')
    final_df.to_csv(FINAL_RESULTS_CSV, index=False)

    final_entire = final_df.loc[(final_df['domain_label'] == 'Entire area') & (np.isclose(final_df['period_days'], FINAL_PERIOD_DAYS))]
    if final_entire.empty or not bool(final_entire.iloc[0]['success_flag']):
        raise ValueError('Final entire-area 1.404-day fit is unavailable; cannot create required panel b.')
    panel_b_df = build_panel_b_support(events, final_entire.iloc[0])
    log(f'Saving panel-b support table: {PANELB_RATE_CSV}')
    panel_b_df.to_csv(PANELB_RATE_CSV, index=False)

    make_main_figure(final_df, panel_b_df, input_metadata)

    split_df = fit_split_sensitivity(events)
    log(f'Saving split-sensitivity results: {SPLIT_RESULTS_CSV}')
    split_df.to_csv(SPLIT_RESULTS_CSV, index=False)
    make_split_figure(split_df)

    primary_comparison_df = build_primary_comparison(final_df)
    log(f'Saving primary comparison table: {PRIMARY_COMPARISON_CSV}')
    primary_comparison_df.to_csv(PRIMARY_COMPARISON_CSV, index=False)

    save_run_metadata(input_metadata, fit_df, bootstrap_df)
    save_manifest()
    log('02_omori_fitting_and_figures completed successfully.')


if __name__ == '__main__':
    try:
        main()
    except Exception:
        print(traceback.format_exc(), file=sys.stderr, flush=True)
        sys.exit(1)
