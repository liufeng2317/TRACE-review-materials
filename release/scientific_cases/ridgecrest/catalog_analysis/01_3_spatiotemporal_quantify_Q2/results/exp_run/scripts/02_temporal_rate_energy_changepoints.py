from __future__ import annotations

import json
import math
import os
import shutil
import sys
import traceback
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.special import logsumexp as scipy_logsumexp


EVENT_TABLE_PATH = Path("<REPO_ROOT>/examples/ridgecrest/catalog_analysis/run/01_3_trigger_spatiotemporal_quantify_Q2-v1/exp_run/outputs/01_region_geometry_assignment/tables/event_region_assignments.csv")
METADATA_PATH = Path("<REPO_ROOT>/examples/ridgecrest/catalog_analysis/run/01_3_trigger_spatiotemporal_quantify_Q2-v1/exp_run/outputs/01_region_geometry_assignment/metadata/region_geometry_metadata.json")
OUTPUT_DIR = Path("<REPO_ROOT>/examples/ridgecrest/catalog_analysis/run/01_3_trigger_spatiotemporal_quantify_Q2-v1/exp_run/outputs/02_temporal_rate_energy_changepoints")

TIME_RESOLUTIONS = {
    "30min": pd.Timedelta(minutes=30),
    "1h": pd.Timedelta(hours=1),
}
DOMAIN_MASKS = {
    "All_region": "is_all_region",
    "Region_A": "in_Region_A",
    "Region_B": "in_Region_B",
    "Mw64_neighborhood": "in_Mw64_neighborhood",
    "Mw71_neighborhood": "in_Mw71_neighborhood",
}
PRIMARY_DOMAINS = ["All_region", "Region_A", "Region_B"]
NEIGHBORHOOD_DOMAINS = ["Mw64_neighborhood", "Mw71_neighborhood"]
SUSTAINED_ACTIVITY_CONSECUTIVE_BINS = 2
MAX_CHANGEPOINTS = 5
CHANGEPOINT_MIN_SEGMENT_BINS = 4
BAYES_GRID_SIZE = 60
BAYES_CP_POSTERIOR_THRESHOLD = 0.3
MAX_WORKERS = min(64, max(1, os.cpu_count() or 1))


REQUIRED_COLUMNS = [
    "event_time",
    "magnitude",
    "energy_joule",
    "hours_since_main64",
    "is_all_region",
    "in_Region_A",
    "in_Region_B",
    "in_Mw64_neighborhood",
    "in_Mw71_neighborhood",
]


def log(message: str) -> None:
    print(message, flush=True)


def reset_output_dir(output_dir: Path) -> None:
    if output_dir.exists():
        shutil.rmtree(output_dir)
    (output_dir / "figures").mkdir(parents=True, exist_ok=True)
    (output_dir / "tables").mkdir(parents=True, exist_ok=True)
    (output_dir / "metadata").mkdir(parents=True, exist_ok=True)


def require_columns(df: pd.DataFrame, required_columns: list[str], table_name: str) -> None:
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns in {table_name}: {missing}")


def load_inputs() -> tuple[pd.DataFrame, dict, pd.Timestamp, pd.Timestamp]:
    log(f"Loading event table: {EVENT_TABLE_PATH}")
    df = pd.read_csv(EVENT_TABLE_PATH, parse_dates=["event_time"])
    require_columns(df, REQUIRED_COLUMNS, "event_region_assignments.csv")
    with METADATA_PATH.open("r", encoding="utf-8") as f:
        meta = json.load(f)
    if "mainshock64" not in meta or "mainshock71" not in meta:
        raise ValueError("Metadata JSON must contain mainshock64 and mainshock71 entries.")
    main64_time = pd.Timestamp(meta["mainshock64"]["event_time"])
    main71_time = pd.Timestamp(meta["mainshock71"]["event_time"])
    if main64_time >= main71_time:
        raise ValueError("Mainshock timing metadata is invalid: Mw 6.4 must precede Mw 7.1.")
    df["event_time"] = pd.to_datetime(df["event_time"], utc=True, format="ISO8601")
    df = df.sort_values("event_time").reset_index(drop=True)
    if df.empty:
        raise ValueError("Input event table is empty.")
    catalog_start_time = pd.Timestamp(df["event_time"].min())
    if catalog_start_time > main64_time:
        raise ValueError("Event table starts after Mw 6.4, inconsistent with required analysis window.")
    if df["event_time"].max() > main71_time:
        raise ValueError("Event table contains events after Mw 7.1, inconsistent with Task 01 output.")
    return df, meta, main64_time, main71_time


def robust_normalized_change(signal: np.ndarray) -> np.ndarray:
    if signal.size < 2:
        return np.array([], dtype=float)
    diff = np.diff(signal)
    mad = np.median(np.abs(diff - np.median(diff)))
    scale = 1.4826 * mad
    if not np.isfinite(scale) or scale <= 0:
        scale = float(np.std(diff))
    if not np.isfinite(scale) or scale <= 0:
        scale = 1.0
    return diff / scale


def normal_logpdf(x: np.ndarray, mean: np.ndarray, std: np.ndarray) -> np.ndarray:
    var = np.maximum(std ** 2, 1e-12)
    return -0.5 * np.log(2.0 * np.pi * var) - ((x - mean) ** 2) / (2.0 * var)



def bayesian_single_changepoint_posterior(signal: np.ndarray, min_segment_bins: int) -> tuple[np.ndarray, np.ndarray]:
    signal = np.asarray(signal, dtype=float)
    n = signal.size
    candidate_idx = np.arange(min_segment_bins, n - min_segment_bins + 1, dtype=int)
    if candidate_idx.size == 0:
        return np.array([], dtype=int), np.array([], dtype=float)

    data_min = float(np.nanmin(signal))
    data_max = float(np.nanmax(signal))
    if not np.isfinite(data_min) or not np.isfinite(data_max):
        return np.array([], dtype=int), np.array([], dtype=float)
    if data_min == data_max:
        return candidate_idx, np.full(candidate_idx.size, 1.0 / candidate_idx.size)

    mean_grid = np.linspace(data_min, data_max, BAYES_GRID_SIZE)
    signal_std = float(np.nanstd(signal))
    std_floor = max(signal_std * 0.25, 1e-3)
    std_ceiling = max(signal_std * 2.5, std_floor * 1.5)
    std_grid = np.geomspace(std_floor, std_ceiling, BAYES_GRID_SIZE)
    log_prior = -math.log(candidate_idx.size) - math.log(mean_grid.size) - math.log(std_grid.size)

    log_marginals = []
    for cp in candidate_idx:
        left = signal[:cp]
        right = signal[cp:]
        left_loglike = np.empty((mean_grid.size, std_grid.size), dtype=float)
        right_loglike = np.empty((mean_grid.size, std_grid.size), dtype=float)
        for i, mean in enumerate(mean_grid):
            left_ll = normal_logpdf(left[:, None], mean, std_grid[None, :]).sum(axis=0)
            right_ll = normal_logpdf(right[:, None], mean, std_grid[None, :]).sum(axis=0)
            left_loglike[i, :] = left_ll
            right_loglike[i, :] = right_ll
        left_log_marginal = scipy_logsumexp(left_loglike.ravel() + log_prior + math.log(candidate_idx.size))
        right_log_marginal = scipy_logsumexp(right_loglike.ravel() + log_prior + math.log(candidate_idx.size))
        log_marginals.append(left_log_marginal + right_log_marginal)

    log_marginals = np.asarray(log_marginals, dtype=float)
    log_norm = scipy_logsumexp(log_marginals)
    posterior = np.exp(log_marginals - log_norm)
    return candidate_idx, posterior



def bayesian_changepoint_table_for_series(
    series_df: pd.DataFrame,
    value_col: str,
    domain: str,
    resolution: str,
    main64_time: pd.Timestamp,
) -> pd.DataFrame:
    values = series_df[value_col].to_numpy(dtype=float)
    if values.size < (2 * CHANGEPOINT_MIN_SEGMENT_BINS):
        return pd.DataFrame(columns=[
            "domain", "resolution", "observable", "cp_index", "cp_start_time", "cp_center_time",
            "hours_since_main64", "posterior_probability", "support_score", "pre_level", "post_level", "delta_level",
        ])
    cp_candidates, posterior = bayesian_single_changepoint_posterior(values, CHANGEPOINT_MIN_SEGMENT_BINS)
    if cp_candidates.size == 0:
        return pd.DataFrame(columns=[
            "domain", "resolution", "observable", "cp_index", "cp_start_time", "cp_center_time",
            "hours_since_main64", "posterior_probability", "support_score", "pre_level", "post_level", "delta_level",
        ])
    order = np.argsort(posterior)[::-1]
    records = []
    kept = 0
    for idx in order:
        if kept >= MAX_CHANGEPOINTS:
            break
        cp = int(cp_candidates[idx])
        post_prob = float(posterior[idx])
        if post_prob < BAYES_CP_POSTERIOR_THRESHOLD and kept > 0:
            continue
        pre = values[:cp]
        post = values[cp:]
        delta = float(post.mean() - pre.mean())
        pooled = np.concatenate([pre, post])
        pooled_std = float(np.std(pooled))
        support = delta / (pooled_std if pooled_std > 0 else 1.0)
        cp_start_time = pd.Timestamp(series_df.iloc[cp]["bin_start"])
        cp_center_time = pd.Timestamp(series_df.iloc[cp]["bin_center"])
        records.append({
            "domain": domain,
            "resolution": resolution,
            "observable": value_col,
            "cp_index": cp,
            "cp_start_time": cp_start_time,
            "cp_center_time": cp_center_time,
            "hours_since_main64": float((cp_center_time - main64_time) / pd.Timedelta(hours=1)),
            "posterior_probability": post_prob,
            "support_score": float(support),
            "pre_level": float(pre.mean()),
            "post_level": float(post.mean()),
            "delta_level": delta,
        })
        kept += 1
    return pd.DataFrame.from_records(records)


def changepoint_table_for_series(
    series_df: pd.DataFrame,
    value_col: str,
    domain: str,
    resolution: str,
    main64_time: pd.Timestamp,
) -> pd.DataFrame:
    values = series_df[value_col].to_numpy(dtype=float)
    if values.size < (2 * CHANGEPOINT_MIN_SEGMENT_BINS):
        return pd.DataFrame(columns=[
            "domain", "resolution", "observable", "cp_index", "cp_start_time", "cp_center_time",
            "hours_since_main64", "support_score", "pre_level", "post_level", "delta_level",
        ])
    cps = binary_segmentation(values, MAX_CHANGEPOINTS, CHANGEPOINT_MIN_SEGMENT_BINS)
    records = []
    for cp in cps:
        pre = values[:cp]
        post = values[cp:]
        delta = float(post.mean() - pre.mean())
        pooled = np.concatenate([pre, post])
        pooled_std = float(np.std(pooled))
        support = delta / (pooled_std if pooled_std > 0 else 1.0)
        cp_start_time = pd.Timestamp(series_df.iloc[cp]["bin_start"])
        cp_center_time = pd.Timestamp(series_df.iloc[cp]["bin_center"])
        records.append({
            "domain": domain,
            "resolution": resolution,
            "observable": value_col,
            "cp_index": int(cp),
            "cp_start_time": cp_start_time,
            "cp_center_time": cp_center_time,
            "hours_since_main64": float((cp_center_time - main64_time) / pd.Timedelta(hours=1)),
            "support_score": float(support),
            "pre_level": float(pre.mean()),
            "post_level": float(post.mean()),
            "delta_level": delta,
        })
    return pd.DataFrame.from_records(records)


def first_sustained_activity_time(post_df: pd.DataFrame) -> pd.Timestamp | pd.NaT:
    positive = (post_df["count"] > 0).to_numpy(dtype=bool)
    if positive.size < SUSTAINED_ACTIVITY_CONSECUTIVE_BINS:
        return pd.NaT
    streak = np.convolve(positive.astype(int), np.ones(SUSTAINED_ACTIVITY_CONSECUTIVE_BINS, dtype=int), mode="valid")
    idxs = np.where(streak >= SUSTAINED_ACTIVITY_CONSECUTIVE_BINS)[0]
    if idxs.size == 0:
        return pd.NaT
    return pd.Timestamp(post_df.iloc[int(idxs[0])]["bin_start"])


def strongest_positive_cp_time(cp_df: pd.DataFrame) -> pd.Timestamp | pd.NaT:
    if cp_df.empty:
        return pd.NaT
    positive = cp_df.loc[cp_df["delta_level"] > 0].copy()
    if positive.empty:
        return pd.NaT
    score_col = "posterior_probability" if "posterior_probability" in positive.columns else "support_score"
    row = positive.iloc[positive[score_col].to_numpy(dtype=float).argmax()]
    return pd.Timestamp(row["cp_center_time"])


def build_domain_series(args: tuple[str, str, pd.Timedelta, pd.DataFrame, pd.Timestamp, pd.Timestamp]) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    domain, mask_col, delta, df, main64_time, main71_time = args
    if mask_col not in df.columns:
        raise ValueError(f"Mask column {mask_col} is missing for domain {domain}.")
    domain_df = df.loc[df[mask_col].astype(bool)].copy()
    start_time = pd.Timestamp(df["event_time"].min()).floor(delta)
    end_time = pd.Timestamp(main71_time).ceil(delta)
    edges = pd.date_range(start=start_time, end=end_time, freq=delta)
    if edges[-1] < main71_time:
        edges = edges.append(pd.DatetimeIndex([edges[-1] + delta]))
    if len(edges) < 2:
        raise ValueError(f"Insufficient time-bin edges for {domain} at {delta}.")
    bin_start = edges[:-1]
    bin_end = edges[1:]
    bin_center = bin_start + (delta / 2)
    interval_hours = delta / pd.Timedelta(hours=1)
    counts = np.zeros(len(bin_start), dtype=int)
    energy = np.zeros(len(bin_start), dtype=float)
    if not domain_df.empty:
        event_times = domain_df["event_time"].to_numpy(dtype="datetime64[ns]")
        edge_values = edges.to_numpy(dtype="datetime64[ns]")
        idx = np.searchsorted(edge_values, event_times, side="right") - 1
        valid = (idx >= 0) & (idx < len(counts))
        idx_valid = idx[valid]
        np.add.at(counts, idx_valid, 1)
        np.add.at(energy, idx_valid, domain_df.iloc[np.flatnonzero(valid)]["energy_joule"].to_numpy(dtype=float))
    rate = counts.astype(float) / interval_hours
    cumulative_count = np.cumsum(counts)
    cumulative_energy = np.cumsum(energy)
    post_mask = bin_end > main64_time
    post_counts = counts[post_mask]
    post_energy = energy[post_mask]
    post_cum_count = np.cumsum(post_counts)
    post_cum_energy = np.cumsum(post_energy)
    total_post_count = int(post_counts.sum())
    total_post_energy = float(post_energy.sum())
    norm_count = np.full(len(counts), np.nan)
    norm_energy = np.full(len(counts), np.nan)
    if total_post_count > 0:
        norm_count[post_mask] = post_cum_count / total_post_count
    if total_post_energy > 0:
        norm_energy[post_mask] = post_cum_energy / total_post_energy
    series_df = pd.DataFrame({
        "domain": domain,
        "resolution": resolution_label(delta),
        "bin_start": bin_start,
        "bin_end": bin_end,
        "bin_center": bin_center,
        "hours_since_main64_bin_center": ((bin_center - main64_time) / pd.Timedelta(hours=1)).astype(float),
        "count": counts,
        "rate_per_hour": rate,
        "energy_joule": energy,
        "cumulative_count": cumulative_count,
        "cumulative_energy_joule": cumulative_energy,
        "normalized_cumulative_count_fraction": norm_count,
        "normalized_cumulative_energy_fraction": norm_energy,
        "rate_change_per_hour": np.r_[np.nan, np.diff(rate)],
        "energy_change_joule": np.r_[np.nan, np.diff(energy)],
        "rate_change_z": np.r_[np.nan, robust_normalized_change(rate)],
        "energy_change_z": np.r_[np.nan, robust_normalized_change(energy)],
    })
    require_columns(
        series_df,
        [
            "domain", "resolution", "bin_start", "bin_end", "bin_center",
            "count", "rate_per_hour", "energy_joule", "cumulative_count",
            "cumulative_energy_joule", "normalized_cumulative_count_fraction",
            "normalized_cumulative_energy_fraction",
        ],
        f"series_df for {domain}",
    )
    cp_rate = bayesian_changepoint_table_for_series(series_df, "rate_per_hour", domain, resolution_label(delta), main64_time)
    cp_energy = bayesian_changepoint_table_for_series(series_df, "energy_joule", domain, resolution_label(delta), main64_time)
    cp_df = pd.concat([cp_rate, cp_energy], ignore_index=True)
    first_event_time = pd.NaT
    if not domain_df.empty:
        post_event_times = domain_df.loc[domain_df["event_time"] >= main64_time, "event_time"]
        if not post_event_times.empty:
            first_event_time = pd.Timestamp(post_event_times.min())
    post_series = series_df.loc[series_df["bin_end"] > main64_time].reset_index(drop=True)
    sustained_time = first_sustained_activity_time(post_series)
    strongest_rate_time = strongest_positive_cp_time(cp_rate.loc[cp_rate["cp_center_time"] >= main64_time])
    peak_rate_time = pd.NaT
    if not post_series.empty and post_series["rate_per_hour"].max() > 0:
        peak_rate_time = pd.Timestamp(post_series.iloc[post_series["rate_per_hour"].to_numpy().argmax()]["bin_center"])
    strongest_energy_time = strongest_positive_cp_time(cp_energy.loc[cp_energy["cp_center_time"] >= main64_time])
    peak_energy_time = pd.NaT
    if not post_series.empty and post_series["energy_joule"].max() > 0:
        peak_energy_time = pd.Timestamp(post_series.iloc[post_series["energy_joule"].to_numpy().argmax()]["bin_center"])
    summary = {
        "domain": domain,
        "resolution": resolution_label(delta),
        "post_main64_event_count": total_post_count,
        "post_main64_cumulative_energy_joule": total_post_energy,
        "first_event_time": first_event_time,
        "first_event_hours_since_main64": hours_since(first_event_time, main64_time),
        "first_sustained_activity_time": sustained_time,
        "first_sustained_activity_hours_since_main64": hours_since(sustained_time, main64_time),
        "strongest_rate_change_time": strongest_rate_time,
        "strongest_rate_change_hours_since_main64": hours_since(strongest_rate_time, main64_time),
        "peak_rate_time": peak_rate_time,
        "peak_rate_hours_since_main64": hours_since(peak_rate_time, main64_time),
        "strongest_energy_change_time": strongest_energy_time,
        "strongest_energy_change_hours_since_main64": hours_since(strongest_energy_time, main64_time),
        "peak_energy_time": peak_energy_time,
        "peak_energy_hours_since_main64": hours_since(peak_energy_time, main64_time),
    }
    return series_df, cp_df, summary


def resolution_label(delta: pd.Timedelta) -> str:
    for label, value in TIME_RESOLUTIONS.items():
        if value == delta:
            return label
    return str(delta)


def hours_since(ts: pd.Timestamp | pd.NaT, ref: pd.Timestamp) -> float:
    if pd.isna(ts):
        return float("nan")
    return float((pd.Timestamp(ts) - ref) / pd.Timedelta(hours=1))


def is_datetime_like_dtype(dtype: object) -> bool:
    return isinstance(dtype, pd.DatetimeTZDtype) or pd.api.types.is_datetime64_any_dtype(dtype)



def save_dataframe(df: pd.DataFrame, path: Path) -> None:
    if any(is_datetime_like_dtype(df[c].dtype) for c in df.columns):
        out = df.copy()
        for col in out.columns:
            if is_datetime_like_dtype(out[col].dtype):
                out[col] = pd.to_datetime(out[col], utc=True, format="ISO8601").astype(str)
        out.to_csv(path, index=False)
    else:
        df.to_csv(path, index=False)


def plot_primary_rate(series_lookup: dict, main64_time: pd.Timestamp, main71_time: pd.Timestamp, resolution: str, out_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(13, 5))
    colors = {"All_region": "black", "Region_A": "tab:blue", "Region_B": "tab:red"}
    for domain in PRIMARY_DOMAINS:
        sdf = series_lookup[(domain, resolution)]
        ax.plot(sdf["bin_center"], sdf["rate_per_hour"], label=domain, color=colors[domain], lw=1.6)
    ax.axvline(main64_time, color="tab:green", ls="--", lw=1.4, label="Mw 6.4")
    ax.axvline(main71_time, color="tab:purple", ls="--", lw=1.4, label="Mw 7.1")
    ax.set_ylabel("Seismic rate (events/hour)")
    ax.set_title(f"Seismic-rate time series ({resolution})")
    ax.legend(ncol=5, fontsize=9)
    ax.grid(alpha=0.3)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d\n%H:%M", tz=main64_time.tzinfo))
    fig.tight_layout()
    fig.savefig(out_path, dpi=220)
    plt.close(fig)


def plot_rate_change_diagnostics(series_lookup: dict, cp_lookup: dict, main64_time: pd.Timestamp, main71_time: pd.Timestamp, resolution: str, out_path: Path) -> None:
    fig, axes = plt.subplots(nrows=3, ncols=1, figsize=(13, 10), sharex=True)
    for ax, domain, color in zip(axes, PRIMARY_DOMAINS, ["black", "tab:blue", "tab:red"]):
        sdf = series_lookup[(domain, resolution)]
        cpdf = cp_lookup[(domain, resolution)]
        rate_cp = cpdf.loc[cpdf["observable"] == "rate_per_hour"]
        ax.plot(sdf["bin_center"], sdf["rate_change_z"], color=color, lw=1.4)
        first_cp = True
        for _, row in rate_cp.iterrows():
            ax.axvline(
                pd.Timestamp(row["cp_center_time"]),
                color="tab:orange",
                ls=":",
                lw=1.0,
                label="Rate changepoint" if first_cp else None,
            )
            first_cp = False
        ax.axvline(main64_time, color="tab:green", ls="--", lw=1.0, label="Mw 6.4")
        ax.axvline(main71_time, color="tab:purple", ls="--", lw=1.0, label="Mw 7.1")
        ax.set_ylabel(f"{domain}\nΔrate z")
        ax.grid(alpha=0.3)
    axes[0].set_title(f"Rate-change diagnostics and Bayesian change points ({resolution})")
    axes[0].legend(loc="upper right", fontsize=8)
    axes[-1].xaxis.set_major_formatter(mdates.DateFormatter("%m-%d\n%H:%M", tz=main64_time.tzinfo))
    fig.tight_layout()
    fig.savefig(out_path, dpi=220)
    plt.close(fig)


def plot_cumulative_count_comparison(series_lookup: dict, main64_time: pd.Timestamp, main71_time: pd.Timestamp, resolution: str, out_path: Path) -> None:
    fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(13, 9), sharex=True)
    colors = {"Region_A": "tab:blue", "Region_B": "tab:red"}
    for domain in ["Region_A", "Region_B"]:
        sdf = series_lookup[(domain, resolution)]
        post = sdf.loc[sdf["bin_end"] > main64_time]
        axes[0].plot(post["bin_center"], post["cumulative_count"], label=domain, color=colors[domain], lw=1.8)
        axes[1].plot(post["bin_center"], post["normalized_cumulative_count_fraction"], label=domain, color=colors[domain], lw=1.8)
    for ax in axes:
        ax.axvline(main64_time, color="tab:green", ls="--", lw=1.0)
        ax.axvline(main71_time, color="tab:purple", ls="--", lw=1.0)
        ax.grid(alpha=0.3)
    axes[0].set_ylabel("Raw cumulative count")
    axes[1].set_ylabel("Normalized cumulative count")
    axes[0].set_title(f"Region A vs Region B cumulative counts ({resolution})")
    axes[0].legend()
    axes[-1].xaxis.set_major_formatter(mdates.DateFormatter("%m-%d\n%H:%M", tz=main64_time.tzinfo))
    fig.tight_layout()
    fig.savefig(out_path, dpi=220)
    plt.close(fig)


def plot_energy_panels(series_lookup: dict, cp_lookup: dict, main64_time: pd.Timestamp, main71_time: pd.Timestamp, resolution: str, out_path: Path) -> None:
    fig, axes = plt.subplots(nrows=3, ncols=2, figsize=(15, 11), sharex=True)
    colors = {"All_region": "black", "Region_A": "tab:blue", "Region_B": "tab:red"}
    for row, domain in enumerate(PRIMARY_DOMAINS):
        sdf = series_lookup[(domain, resolution)]
        cpdf = cp_lookup[(domain, resolution)]
        ecp = cpdf.loc[cpdf["observable"] == "energy_joule"]
        axes[row, 0].plot(sdf["bin_center"], sdf["energy_joule"], color=colors[domain], lw=1.4)
        axes[row, 1].plot(sdf["bin_center"], sdf["cumulative_energy_joule"], color=colors[domain], lw=1.4)
        first_cp = True
        for _, cp in ecp.iterrows():
            axes[row, 0].axvline(pd.Timestamp(cp["cp_center_time"]), color="tab:orange", ls=":", lw=0.9, label="Energy changepoint" if first_cp else None)
            axes[row, 1].axvline(pd.Timestamp(cp["cp_center_time"]), color="tab:orange", ls=":", lw=0.9, label="Energy changepoint" if first_cp else None)
            first_cp = False
        for ax in axes[row, :]:
            ax.axvline(main64_time, color="tab:green", ls="--", lw=0.9, label="Mw 6.4")
            ax.axvline(main71_time, color="tab:purple", ls="--", lw=0.9, label="Mw 7.1")
            ax.grid(alpha=0.3)
        axes[row, 0].set_ylabel(domain)
    axes[0, 0].set_title(f"Energy release by domain ({resolution})")
    axes[0, 1].set_title(f"Cumulative energy by domain ({resolution})")
    axes[0, 0].legend(loc="upper right", fontsize=8)
    axes[-1, 0].xaxis.set_major_formatter(mdates.DateFormatter("%m-%d\n%H:%M", tz=main64_time.tzinfo))
    axes[-1, 1].xaxis.set_major_formatter(mdates.DateFormatter("%m-%d\n%H:%M", tz=main64_time.tzinfo))
    fig.tight_layout()
    fig.savefig(out_path, dpi=220)
    plt.close(fig)


def plot_normalized_energy_fraction(series_lookup: dict, main64_time: pd.Timestamp, main71_time: pd.Timestamp, resolution: str, out_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(13, 5))
    for domain, color in [("Region_A", "tab:blue"), ("Region_B", "tab:red")]:
        sdf = series_lookup[(domain, resolution)]
        post = sdf.loc[sdf["bin_end"] > main64_time]
        ax.plot(post["bin_center"], post["normalized_cumulative_energy_fraction"], color=color, lw=1.8, label=domain)
    ax.axvline(main64_time, color="tab:green", ls="--", lw=1.0)
    ax.axvline(main71_time, color="tab:purple", ls="--", lw=1.0)
    ax.set_ylabel("Normalized cumulative energy")
    ax.set_title(f"Normalized cumulative energy fractions ({resolution})")
    ax.legend()
    ax.grid(alpha=0.3)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d\n%H:%M", tz=main64_time.tzinfo))
    fig.tight_layout()
    fig.savefig(out_path, dpi=220)
    plt.close(fig)


def plot_neighborhood_comparison(series_lookup: dict, summary_df: pd.DataFrame, main64_time: pd.Timestamp, main71_time: pd.Timestamp, resolution: str, out_path: Path) -> None:
    fig, axes = plt.subplots(nrows=3, ncols=1, figsize=(13, 12), sharex=True)
    colors = {"Mw64_neighborhood": "tab:green", "Mw71_neighborhood": "tab:purple"}
    for domain in NEIGHBORHOOD_DOMAINS:
        sdf = series_lookup[(domain, resolution)]
        post = sdf.loc[sdf["bin_end"] > main64_time]
        axes[0].plot(post["bin_center"], post["rate_per_hour"], color=colors[domain], lw=1.8, label=domain)
        axes[1].plot(post["bin_center"], post["cumulative_count"], color=colors[domain], lw=1.8)
        axes[2].plot(post["bin_center"], post["normalized_cumulative_count_fraction"], color=colors[domain], lw=1.8)
        row = summary_df.loc[(summary_df["domain"] == domain) & (summary_df["resolution"] == resolution)]
        if not row.empty:
            row = row.iloc[0]
            for ax, key, linestyle, label in [
                (axes[0], "first_sustained_activity_time", "--", f"{domain} first sustained"),
                (axes[0], "strongest_rate_change_time", ":", f"{domain} strongest rate change"),
                (axes[0], "peak_rate_time", "-.", f"{domain} peak rate")
            ]:
                if pd.notna(row[key]):
                    ax.axvline(pd.Timestamp(row[key]), color=colors[domain], ls=linestyle, lw=1.2, label=label)
    for ax in axes:
        ax.axvline(main64_time, color="black", ls="--", lw=0.9, label="Mw 6.4")
        ax.axvline(main71_time, color="black", ls=":", lw=0.9, label="Mw 7.1")
        ax.grid(alpha=0.3)
    axes[0].set_ylabel("Rate (events/hour)")
    axes[1].set_ylabel("Raw cumulative count")
    axes[2].set_ylabel("Normalized cumulative count")
    axes[0].set_title(f"Near-mainshock neighborhood comparison ({resolution})")
    handles, labels = axes[0].get_legend_handles_labels()
    unique = dict(zip(labels, handles))
    axes[0].legend(unique.values(), unique.keys(), fontsize=8, ncol=2)
    axes[-1].xaxis.set_major_formatter(mdates.DateFormatter("%m-%d\n%H:%M", tz=main64_time.tzinfo))
    fig.tight_layout()
    fig.savefig(out_path, dpi=220)
    plt.close(fig)


def plot_rate_difference(series_lookup: dict, main64_time: pd.Timestamp, main71_time: pd.Timestamp, resolution: str, out_path: Path) -> None:
    a = series_lookup[("Region_A", resolution)]
    b = series_lookup[("Region_B", resolution)]
    fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(13, 8), sharex=True)
    diff = a["rate_per_hour"].to_numpy() - b["rate_per_hour"].to_numpy()
    ratio = np.divide(
        a["rate_per_hour"].to_numpy(),
        b["rate_per_hour"].to_numpy(),
        out=np.full(len(a), np.nan),
        where=b["rate_per_hour"].to_numpy() > 0,
    )
    axes[0].plot(a["bin_center"], diff, color="tab:brown", lw=1.6)
    axes[1].plot(a["bin_center"], ratio, color="tab:cyan", lw=1.6)
    axes[0].axhline(0, color="black", lw=0.8)
    for ax in axes:
        ax.axvline(main64_time, color="tab:green", ls="--", lw=1.0)
        ax.axvline(main71_time, color="tab:purple", ls="--", lw=1.0)
        ax.grid(alpha=0.3)
    axes[0].set_ylabel("Rate difference\n(A - B)")
    axes[1].set_ylabel("Rate ratio\n(A / B)")
    axes[0].set_title(f"Region A vs Region B dominance diagnostics ({resolution})")
    axes[-1].xaxis.set_major_formatter(mdates.DateFormatter("%m-%d\n%H:%M", tz=main64_time.tzinfo))
    fig.tight_layout()
    fig.savefig(out_path, dpi=220)
    plt.close(fig)


def write_metadata(meta: dict, main64_time: pd.Timestamp, main71_time: pd.Timestamp, catalog_start_time: pd.Timestamp) -> None:
    out = {
        "time_resolutions": {k: str(v) for k, v in TIME_RESOLUTIONS.items()},
        "domain_masks": DOMAIN_MASKS,
        "sustained_activity_rule": f"First bin starting a run of >= {SUSTAINED_ACTIVITY_CONSECUTIVE_BINS} consecutive nonzero bins after Mw 6.4.",
        "changepoint_method": {
            "name": "bayesian single-changepoint posterior scan",
            "max_changepoints": MAX_CHANGEPOINTS,
            "min_segment_bins": CHANGEPOINT_MIN_SEGMENT_BINS,
            "mean_grid_size": BAYES_GRID_SIZE,
            "posterior_probability_threshold": BAYES_CP_POSTERIOR_THRESHOLD,
            "support_score": "(post_mean - pre_mean) / pooled_std",
        },
        "analysis_window": {
            "catalog_start_time": str(catalog_start_time),
            "mw64_time": str(main64_time),
            "mw71_time": str(main71_time),
        },
        "notes": [
            "A self-contained Bayesian changepoint scan was used to compute posterior probabilities for single mean-shift changepoints under a Gaussian likelihood with discretized mean and scale priors.",
            "Energy was taken from the ancestor event table using log10(E[J]) = 1.5*M + 4.8 from Task 01.",
            "Normalized cumulative fractions are defined only for bins after Mw 6.4.",
        ],
    }
    with (OUTPUT_DIR / "metadata" / "temporal_analysis_metadata.json").open("w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)


def main() -> None:
    reset_output_dir(OUTPUT_DIR)
    df, meta, main64_time, main71_time = load_inputs()
    catalog_start_time = pd.Timestamp(df["event_time"].min())
    log(f"Loaded {len(df):,} events. Analysis window: {catalog_start_time} to {main71_time}")
    tasks = []
    for _, delta in TIME_RESOLUTIONS.items():
        for domain, mask_col in DOMAIN_MASKS.items():
            tasks.append((domain, mask_col, delta, df, main64_time, main71_time))
    series_frames = []
    cp_frames = []
    summary_records = []
    log(f"Building time series in parallel with up to {MAX_WORKERS} workers for {len(tasks)} domain-resolution combinations.")
    with ProcessPoolExecutor(max_workers=min(MAX_WORKERS, len(tasks))) as ex:
        future_map = {ex.submit(build_domain_series, task): (task[0], resolution_label(task[2])) for task in tasks}
        for future in as_completed(future_map):
            domain, resolution = future_map[future]
            log(f"Completed domain={domain}, resolution={resolution}")
            sdf, cpdf, summary = future.result()
            if sdf.empty:
                raise ValueError(f"Empty time-series output for {domain} at {resolution}.")
            series_frames.append(sdf)
            cp_frames.append(cpdf)
            summary_records.append(summary)
    series_all = pd.concat(series_frames, ignore_index=True)
    cp_all = pd.concat(cp_frames, ignore_index=True) if cp_frames else pd.DataFrame()
    summary_df = pd.DataFrame(summary_records)
    if summary_df.empty:
        raise ValueError("Summary table is empty.")
    series_lookup = {(d, r): g.sort_values("bin_start").reset_index(drop=True) for (d, r), g in series_all.groupby(["domain", "resolution"])}
    cp_lookup = {(d, r): g.sort_values(["observable", "cp_center_time"]).reset_index(drop=True) for (d, r), g in cp_all.groupby(["domain", "resolution"])} if not cp_all.empty else {}
    log("Saving time-series and change-point tables.")
    save_dataframe(series_all.sort_values(["resolution", "domain", "bin_start"]), OUTPUT_DIR / "tables" / "domain_time_series_all.csv")
    save_dataframe(cp_all.sort_values(["resolution", "domain", "observable", "cp_center_time"]) if not cp_all.empty else pd.DataFrame(columns=["domain"]), OUTPUT_DIR / "tables" / "changepoint_summary_all.csv")
    save_dataframe(summary_df.sort_values(["resolution", "domain"]), OUTPUT_DIR / "tables" / "domain_timing_summary_all.csv")
    primary_summary = summary_df.loc[summary_df["domain"].isin(PRIMARY_DOMAINS)].copy()
    neighborhood_summary = summary_df.loc[summary_df["domain"].isin(NEIGHBORHOOD_DOMAINS)].copy()
    save_dataframe(primary_summary.sort_values(["resolution", "domain"]), OUTPUT_DIR / "tables" / "primary_domain_timing_summary.csv")
    save_dataframe(neighborhood_summary.sort_values(["resolution", "domain"]), OUTPUT_DIR / "tables" / "neighborhood_timing_summary.csv")
    for resolution in TIME_RESOLUTIONS:
        log(f"Creating figures for resolution={resolution}")
        plot_primary_rate(series_lookup, main64_time, main71_time, resolution, OUTPUT_DIR / "figures" / f"seismic_rate_primary_domains_{resolution}.png")
        plot_rate_change_diagnostics(series_lookup, cp_lookup, main64_time, main71_time, resolution, OUTPUT_DIR / "figures" / f"rate_change_diagnostics_{resolution}.png")
        plot_cumulative_count_comparison(series_lookup, main64_time, main71_time, resolution, OUTPUT_DIR / "figures" / f"cumulative_counts_region_a_vs_b_{resolution}.png")
        plot_energy_panels(series_lookup, cp_lookup, main64_time, main71_time, resolution, OUTPUT_DIR / "figures" / f"energy_panels_primary_domains_{resolution}.png")
        plot_normalized_energy_fraction(series_lookup, main64_time, main71_time, resolution, OUTPUT_DIR / "figures" / f"normalized_cumulative_energy_region_a_vs_b_{resolution}.png")
        plot_neighborhood_comparison(series_lookup, summary_df, main64_time, main71_time, resolution, OUTPUT_DIR / "figures" / f"neighborhood_comparison_{resolution}.png")
        plot_rate_difference(series_lookup, main64_time, main71_time, resolution, OUTPUT_DIR / "figures" / f"region_a_vs_b_rate_difference_ratio_{resolution}.png")
    write_metadata(meta, main64_time, main71_time, catalog_start_time)
    for domain in PRIMARY_DOMAINS:
        if summary_df.loc[(summary_df["domain"] == domain) & (summary_df["resolution"] == "30min"), "post_main64_event_count"].sum() <= 0:
            raise ValueError(f"Primary domain {domain} has zero post-Mw6.4 events in 30-minute summary.")
    if cp_all.empty:
        raise ValueError("Change-point table is empty.")
    log(f"Finished successfully. Outputs written to {OUTPUT_DIR}")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print(traceback.format_exc(), flush=True)
        sys.exit(1)
