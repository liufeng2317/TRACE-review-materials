from __future__ import annotations

import json
import math
import shutil
import sys
import traceback
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import numpy as np
import pandas as pd


BASE_DIR = Path("<CASE_ROOT>/data")
STEP1_OUTPUT_DIR = Path("<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/01_data_verification_and_rematch")
STEP2_OUTPUT_DIR = Path("<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/02_sequence_extraction")
STEP3_OUTPUT_DIR = Path("<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/03_sequence_diagnostics")
STEP4_OUTPUT_DIR = Path("<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/04_robustness_analysis")
STEP5_OUTPUT_DIR = Path("<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/05_three_sequence_comparison")
STEP6_OUTPUT_DIR = Path("<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/06_control_comparison")
OUTPUT_DIR = Path("<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/07_figure_generation")
FIGURE_DIR = OUTPUT_DIR / "figures"
FIGURE_DATA_DIR = OUTPUT_DIR / "figure_data"

CATALOG_PATH = BASE_DIR / "catalog/Snet_catalog_relocate.csv"
MAIN_PATH = BASE_DIR / "catalog/main_earthquake.csv"
MECHA_PATH = BASE_DIR / "source_mechanism/Snet_mecha.csv"
STATION_PATH = BASE_DIR / "stations/station.sta"
MATCH_PATH = STEP1_OUTPUT_DIR / "matched_mainshocks.csv"
VERIFY_PATH = STEP1_OUTPUT_DIR / "data_verification_summary.json"

SEQ_PATH = STEP2_OUTPUT_DIR / "event_centered_sequence_table.csv"
EXTRACT_COUNTS_PATH = STEP2_OUTPUT_DIR / "sequence_extraction_counts.csv"
SEQ_VERIFY_PATH = STEP2_OUTPUT_DIR / "sequence_extraction_verification.json"
SUBSET_DIR = STEP2_OUTPUT_DIR / "figure_data"

SUMMARY_PATH = STEP3_OUTPUT_DIR / "sequence_diagnostics_metrics.csv"
WINDOW_PATH = STEP3_OUTPUT_DIR / "time_binned_rates.csv"
RADIAL_PATH = STEP3_OUTPUT_DIR / "radial_distance_summary.csv"
DEPTH_PATH = STEP3_OUTPUT_DIR / "depth_distribution_summary.csv"
MAG_PATH = STEP3_OUTPUT_DIR / "magnitude_distribution_summary.csv"
MECHA_SUMMARY_PATH = STEP3_OUTPUT_DIR / "mechanism_overlap_summary.csv"
ROBUSTNESS_INPUT_PATH = STEP3_OUTPUT_DIR / "robustness_summary.csv"
COMPARISON_PATH = STEP3_OUTPUT_DIR / "three_sequence_comparison.csv"
CONTROL_PATH = STEP3_OUTPUT_DIR / "control_summary.csv"
STEP3_VERIFY_PATH = STEP3_OUTPUT_DIR / "sequence_diagnostics_verification.json"

ROBUSTNESS_PATH = STEP4_OUTPUT_DIR / "robustness_results.csv"
SENSITIVITY_PATH = STEP4_OUTPUT_DIR / "sensitivity_summary.csv"
STABILITY_PATH = STEP4_OUTPUT_DIR / "stability_flags.csv"
GRID_PATH = STEP4_OUTPUT_DIR / "parameter_grid_summary.csv"
COMPARISON_BASELINE_PATH = STEP4_OUTPUT_DIR / "three_sequence_comparison_baseline.csv"
CONTROL_BASELINE_PATH = STEP4_OUTPUT_DIR / "control_comparison_baseline.csv"
STEP4_VERIFY_PATH = STEP4_OUTPUT_DIR / "robustness_verification.json"

MASTER_COMPARISON_PATH = STEP5_OUTPUT_DIR / "three_sequence_comparison_master.csv"
BASELINE_COMPARISON_STEP5_PATH = STEP5_OUTPUT_DIR / "three_sequence_comparison_baseline.csv"
CONTROL_SUMMARY_STEP5_PATH = STEP5_OUTPUT_DIR / "control_comparison_summary.csv"
STEP5_VERIFY_PATH = STEP5_OUTPUT_DIR / "three_sequence_comparison_verification.json"

CONTROL_OBS_RAND_PATH = STEP6_OUTPUT_DIR / "control_observed_randomized.csv"
CONTROL_RATIO_PATH = STEP6_OUTPUT_DIR / "control_pairwise_ratio.csv"
STEP6_VERIFY_PATH = STEP6_OUTPUT_DIR / "control_verification.json"

MAINSHOCKS = ["M1", "M2", "M3"]
BASELINE_RADIUS = 50.0
BASELINE_TIME = 90.0
BASELINE_DEPTH = "all"
BASELINE_MAG = np.nan
RADIUS_GRID = [30.0, 44.0, 50.0, 80.0, 100.0]
TIME_GRID = [7.0, 30.0, 60.0, 90.0]
MAG_GRID = [np.nan, 1.2, 1.5, 2.0, 2.5]
DEPTH_ORDER = ["all", "mainshock_window", "stratified"]
DPI = 300
FIGSIZE = (8.6, 5.8)


def log(msg: str) -> None:
    print(msg, flush=True)


def to_jsonable(value):
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, (np.integer, np.floating)):
        return value.item()
    if isinstance(value, (np.bool_,)):
        return bool(value)
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, (pd.Series, pd.Index)):
        return value.tolist()
    if pd.isna(value):
        return None
    return value


def clean_output_dir() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for p in OUTPUT_DIR.glob("*"):
        if p.is_dir():
            shutil.rmtree(p)
        else:
            p.unlink()
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    FIGURE_DATA_DIR.mkdir(parents=True, exist_ok=True)
    log(f"[0] Cleaned stale artifacts in {OUTPUT_DIR}")


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(str(path))
    return pd.read_csv(path)


def parse_time(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series, errors="coerce", utc=True)


def haversine_km(lat1, lon1, lat2, lon2):
    lat1 = np.radians(lat1)
    lon1 = np.radians(lon1)
    lat2 = np.radians(lat2)
    lon2 = np.radians(lon2)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2.0) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2.0) ** 2
    return 2.0 * 6371.0 * np.arcsin(np.sqrt(a))


def load_mainshocks() -> pd.DataFrame:
    df = read_csv(MAIN_PATH)
    if "index" in df.columns:
        df = df.rename(columns={"index": "mainshock"})
    elif "mainshock" not in df.columns:
        df = df.iloc[:, :6]
        df.columns = ["mainshock", "datetime", "lat", "lon", "dep", "mag"]
    df["time"] = parse_time(df["datetime"])
    for c in ["lat", "lon", "dep", "mag"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return df[["mainshock", "time", "lat", "lon", "dep", "mag"]].copy()


def load_catalog() -> pd.DataFrame:
    df = read_csv(CATALOG_PATH)
    df["datetime"] = parse_time(df["datetime"])
    for c in ["lat", "lon", "dep", "mag"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    if "event_id" not in df.columns:
        df["event_id"] = np.arange(len(df), dtype=int)
    return df.sort_values("datetime").reset_index(drop=True)


def load_mech() -> pd.DataFrame:
    df = read_csv(MECHA_PATH)
    if "origin_time" in df.columns:
        df["origin_time"] = parse_time(df["origin_time"])
    return df


def load_station() -> pd.DataFrame:
    df = read_csv(STATION_PATH)
    return df


def load_step_outputs() -> Dict[str, pd.DataFrame]:
    paths = {
        "seq": SEQ_PATH,
        "summary": SUMMARY_PATH,
        "window": WINDOW_PATH,
        "radial": RADIAL_PATH,
        "depth": DEPTH_PATH,
        "mag": MAG_PATH,
        "mecha_summary": MECHA_SUMMARY_PATH,
        "robustness": ROBUSTNESS_PATH,
        "comparison": COMPARISON_PATH,
        "control": CONTROL_PATH,
        "grid": GRID_PATH,
        "stability": STABILITY_PATH,
        "baseline_comparison": COMPARISON_BASELINE_PATH,
        "control_baseline": CONTROL_BASELINE_PATH,
        "match": MATCH_PATH,
    }
    out = {}
    for key, path in paths.items():
        if not path.exists():
            raise FileNotFoundError(f"Required input missing: {path}")
        out[key] = read_csv(path)
    return out


def setup_style() -> None:
    plt.rcParams.update({
        "figure.dpi": DPI,
        "savefig.dpi": DPI,
        "font.size": 10,
        "axes.titlesize": 11,
        "axes.labelsize": 10,
        "legend.fontsize": 8,
        "xtick.labelsize": 8,
        "ytick.labelsize": 8,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
    })


def baseline_slice(summary: pd.DataFrame) -> pd.DataFrame:
    s = summary.copy()
    s["mag_threshold"] = pd.to_numeric(s["mag_threshold"], errors="coerce")
    mask = (s["radius_km"] == BASELINE_RADIUS) & (s["time_window_days"] == BASELINE_TIME) & (s["depth_strategy"] == BASELINE_DEPTH) & (s["mag_threshold"].isna())
    out = s.loc[mask].copy()
    if out.empty:
        out = s.groupby("mainshock", as_index=False).first()
    return out


def subset_baseline_from_seq(seq: pd.DataFrame) -> pd.DataFrame:
    s = seq.copy()
    s["mag_threshold"] = pd.to_numeric(s["mag_threshold"], errors="coerce") if "mag_threshold" in s.columns else np.nan
    mask = (s["radius_km"] == BASELINE_RADIUS) & (s["time_window_days"] == BASELINE_TIME)
    if "depth_strategy" in s.columns:
        mask &= s["depth_strategy"].eq(BASELINE_DEPTH)
    if "mag_threshold" in s.columns:
        mask &= s["mag_threshold"].isna()
    out = s.loc[mask].copy()
    return out


def add_seq_geometry(seq: pd.DataFrame, match_row: pd.Series) -> pd.DataFrame:
    out = seq.copy()
    if "datetime" in out.columns and pd.api.types.is_datetime64_any_dtype(out["datetime"]):
        out["time_rel_days"] = (out["datetime"] - match_row["matched_datetime"]).dt.total_seconds() / 86400.0
    else:
        out["time_rel_days"] = pd.to_numeric(out["time_rel_days"], errors="coerce")
    out["radial_distance_km"] = haversine_km(match_row["matched_lat"], match_row["matched_lon"], out["lat"].to_numpy(), out["lon"].to_numpy())
    out["depth_rel_km"] = out["dep"] - float(match_row["matched_dep"])
    out["pre_post"] = np.where(out["time_rel_days"] < 0, "pre", np.where(out["time_rel_days"] > 0, "post", "mainshock"))
    return out


def fig_save(fig: plt.Figure, outpath: Path) -> None:
    fig.savefig(outpath, bbox_inches="tight")
    plt.close(fig)


def make_event_map(seq: pd.DataFrame, match_row: pd.Series, mainshock: str, outpath: Path) -> None:
    if seq.empty:
        return
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.8), dpi=DPI, constrained_layout=True)
    for ax, part, title in zip(axes, ["pre", "post"], ["Pre-event", "Post-event"]):
        d = seq[seq["pre_post"] == part].copy()
        if d.empty:
            ax.text(0.5, 0.5, f"No {part} events", ha="center", va="center", transform=ax.transAxes)
            continue
        sc = ax.scatter(d["lon"], d["lat"], c=d["time_rel_days"].abs(), s=np.clip((d["mag"].fillna(1.5) ** 2) * 10, 18, 150), cmap="viridis", alpha=0.82, edgecolors="none")
        ax.scatter([match_row["matched_lon"]], [match_row["matched_lat"]], marker="*", s=240, c="crimson", edgecolors="black", linewidths=0.7, zorder=5)
        ax.set_title(title)
        ax.set_xlabel("Longitude")
        ax.set_ylabel("Latitude")
        ax.grid(True, alpha=0.2)
    cbar = fig.colorbar(sc, ax=axes.ravel().tolist(), shrink=0.9, pad=0.02)
    cbar.set_label("|Time relative to mainshock| (days)")
    fig.suptitle(f"{mainshock} event-centered map")
    fig_save(fig, outpath)


def make_cumulative_counts(seq: pd.DataFrame, mainshock: str, outpath: Path) -> None:
    if seq.empty:
        return
    fig, ax = plt.subplots(figsize=(8.5, 5.2), dpi=DPI)
    for part, color in [("pre", "steelblue"), ("post", "crimson")]:
        d = seq[seq["pre_post"] == part].sort_values("time_rel_days")
        if d.empty:
            continue
        x = d["time_rel_days"].to_numpy()
        y = np.arange(1, len(d) + 1)
        ax.step(x, y, where="post", color=color, lw=2.2, label=f"{part} ({len(d)})")
    ax.axvline(0, color="black", lw=1.2, ls="--")
    ax.set_xlabel("Time relative to mainshock (days)")
    ax.set_ylabel("Cumulative events")
    ax.set_title(f"{mainshock} cumulative count curve")
    ax.grid(True, alpha=0.25)
    ax.legend(frameon=False)
    fig_save(fig, outpath)


def make_moving_rate(window: pd.DataFrame, mainshock: str, outpath: Path) -> None:
    if window.empty:
        return
    fig, ax = plt.subplots(figsize=(8.5, 5.2), dpi=DPI)
    for part, color in [("pre", "steelblue"), ("post", "crimson"), ("crosses_mainshock", "gray")]:
        d = window[window["pre_post"] == part].copy()
        if d.empty:
            continue
        mid = 0.5 * (d["time_bin_start_days"] + d["time_bin_end_days"])
        ax.plot(mid, d["rate_per_day"], marker="o", ms=3.5, lw=1.7, color=color, label=part)
    ax.axvline(0, color="black", lw=1.2, ls="--")
    ax.set_xlabel("Time relative to mainshock (days)")
    ax.set_ylabel("Moving-window rate (events/day)")
    ax.set_title(f"{mainshock} moving-window seismicity rate")
    ax.grid(True, alpha=0.25)
    ax.legend(frameon=False)
    fig_save(fig, outpath)


def make_decay_plot(seq: pd.DataFrame, summary_row: pd.Series, mainshock: str, outpath: Path) -> None:
    post = seq[seq["time_rel_days"] > 0].copy()
    if post.empty:
        return
    fig, ax = plt.subplots(figsize=(8.2, 5.2), dpi=DPI)
    ax.scatter(post["time_rel_days"], np.arange(1, len(post) + 1), s=10, c="crimson", alpha=0.6, label="post-event arrivals")
    if pd.notna(summary_row.get("post_omori_fit_ok", False)) and bool(summary_row.get("post_omori_fit_ok", False)):
        p = summary_row.get("post_omori_p", np.nan)
        k = summary_row.get("post_omori_k", np.nan)
        c = summary_row.get("post_omori_c", 0.01)
        t = np.logspace(np.log10(max(0.02, post["time_rel_days"].min())), np.log10(post["time_rel_days"].max()), 200)
        if pd.notna(p) and pd.notna(k):
            y = k / np.power(t + (c if pd.notna(c) else 0.01), p)
            ax2 = ax.twinx()
            ax2.plot(t, y, color="black", lw=2.0, label=f"Omori fit p={p:.2f}")
            ax2.set_ylabel("Modeled rate")
            ax2.set_yscale("log")
            ax2.legend(frameon=False, loc="upper right")
    ax.set_xscale("log")
    ax.set_xlabel("Time after mainshock (days, log scale)")
    ax.set_ylabel("Cumulative post events")
    ax.set_title(f"{mainshock} post-event decay diagnostic")
    ax.grid(True, alpha=0.25, which="both")
    ax.legend(frameon=False, loc="upper left")
    fig_save(fig, outpath)


def make_radial_time_plot(seq: pd.DataFrame, mainshock: str, outpath: Path) -> None:
    if seq.empty:
        return
    fig, ax = plt.subplots(figsize=(8.5, 5.5), dpi=DPI)
    d = seq.copy()
    d = d[np.isfinite(d["time_rel_days"]) & np.isfinite(d["radial_distance_km"])]
    if d.empty:
        return
    sc = ax.scatter(d["time_rel_days"], d["radial_distance_km"], c=d["mag"], cmap="plasma", s=np.clip((d["mag"].fillna(1.5) ** 2) * 10, 15, 140), alpha=0.75, edgecolors="none")
    ax.axvline(0, color="black", ls="--", lw=1.0)
    ax.set_xlabel("Time relative to mainshock (days)")
    ax.set_ylabel("Radial distance (km)")
    ax.set_title(f"{mainshock} time-distance pattern")
    ax.grid(True, alpha=0.2)
    cbar = fig.colorbar(sc, ax=ax, pad=0.01)
    cbar.set_label("Magnitude")
    fig_save(fig, outpath)


def matrix_heatmap(df: pd.DataFrame, xcol: str, ycol: str, zcol: str, title: str, outpath: Path, xlabels=None, ylabels=None, logscale: bool = False) -> None:
    if df.empty:
        return
    pivot = df.pivot(index=ycol, columns=xcol, values=zcol)
    pivot = pivot.sort_index().sort_index(axis=1)
    fig, ax = plt.subplots(figsize=(9, 5.8), dpi=DPI)
    data = pivot.to_numpy(dtype=float)
    cmap = "magma"
    if logscale:
        pos = data[np.isfinite(data) & (data > 0)]
        norm = LogNorm(vmin=max(pos.min(), 1e-3), vmax=max(pos.max(), 1e-2)) if pos.size else None
    else:
        norm = None
    im = ax.imshow(data, aspect="auto", origin="lower", cmap=cmap, norm=norm)
    ax.set_xticks(np.arange(len(pivot.columns)))
    ax.set_yticks(np.arange(len(pivot.index)))
    ax.set_xticklabels([str(v) for v in pivot.columns])
    ax.set_yticklabels([str(v) for v in pivot.index])
    ax.set_xlabel(xcol)
    ax.set_ylabel(ycol)
    ax.set_title(title)
    ax.grid(False)
    cbar = fig.colorbar(im, ax=ax, pad=0.02)
    cbar.set_label(zcol)
    fig_save(fig, outpath)


def sensitivity_heatmaps(summary: pd.DataFrame, mainshock: str, outdir: Path) -> None:
    s = summary[summary["mainshock"] == mainshock].copy()
    if s.empty:
        return
    s["mag_label"] = s["mag_threshold"].apply(lambda x: "all" if pd.isna(x) else f"M≥{float(x):.1f}")
    available_metrics = [m for m in ["rate_ratio", "n_total", "radial_q25_km", "radial_q50_km", "radial_q75_km"] if m in s.columns]
    for metric, fname, logscale in [
        ("rate_ratio", f"{mainshock}_rate_ratio_radius_time_heatmap.png", True),
        ("n_total", f"{mainshock}_count_radius_time_heatmap.png", False),
        ("radial_q50_km", f"{mainshock}_radial_median_radius_time_heatmap.png", False),
    ]:
        sub = s[(s["depth_strategy"] == "all") & (s["mag_label"].isin(["all", "M≥1.2", "M≥1.5", "M≥2.0", "M≥2.5"]))].copy()
        if sub.empty:
            continue
        sub["grid_key"] = sub["mag_label"]
        fig, axes = plt.subplots(1, len(MAG_GRID), figsize=(14, 3.2), dpi=DPI, sharey=True)
        for ax, mag_label in zip(axes, ["all", "M≥1.2", "M≥1.5", "M≥2.0", "M≥2.5"]):
            d = sub[sub["mag_label"] == mag_label].copy()
            if d.empty:
                ax.axis("off")
                continue
            pivot = d.pivot(index="time_window_days", columns="radius_km", values=metric).sort_index().sort_index(axis=1)
            arr = pivot.to_numpy(dtype=float)
            if metric == "rate_ratio":
                pos = arr[np.isfinite(arr) & (arr > 0)]
                norm = LogNorm(vmin=max(pos.min(), 1e-3), vmax=max(pos.max(), 1e-2)) if pos.size else None
            else:
                norm = None
            im = ax.imshow(arr, origin="lower", aspect="auto", cmap="viridis", norm=norm)
            ax.set_title(mag_label)
            ax.set_xticks(np.arange(len(pivot.columns)))
            ax.set_xticklabels([str(int(v)) if float(v).is_integer() else str(v) for v in pivot.columns], rotation=45, ha="right")
            ax.set_yticks(np.arange(len(pivot.index)))
            ax.set_yticklabels([str(int(v)) if float(v).is_integer() else str(v) for v in pivot.index])
            ax.set_xlabel("Radius (km)")
            ax.grid(False)
        axes[0].set_ylabel("Time window (days)")
        cbar = fig.colorbar(im, ax=axes.ravel().tolist(), shrink=0.85, pad=0.02)
        cbar.set_label(metric)
        fig.suptitle(f"{mainshock} sensitivity of {metric}")
        fig_save(fig, outdir / fname)


def make_depth_stratified_plot(summary: pd.DataFrame, mainshock: str, outpath: Path) -> None:
    s = summary[(summary["mainshock"] == mainshock) & (summary["radius_km"] == BASELINE_RADIUS) & (summary["time_window_days"] == BASELINE_TIME)].copy()
    if s.empty:
        return
    s["mag_threshold"] = pd.to_numeric(s["mag_threshold"], errors="coerce")
    fig, ax = plt.subplots(figsize=(8.5, 5.3), dpi=DPI)
    for depth_strategy, color in zip(DEPTH_ORDER, ["steelblue", "darkorange", "crimson"]):
        d = s[s["depth_strategy"] == depth_strategy].copy()
        if d.empty:
            continue
        x = d["mag_threshold"].fillna(1.0)
        y = d["rate_ratio"]
        ax.plot(x, y, marker="o", ms=4, lw=1.8, label=depth_strategy, color=color)
    ax.set_xlabel("Magnitude threshold")
    ax.set_ylabel("Post / pre rate ratio")
    ax.set_title(f"{mainshock} depth-stratified robustness")
    ax.grid(True, alpha=0.25)
    ax.legend(frameon=False)
    fig_save(fig, outpath)


def make_comparison_figure(comparison: pd.DataFrame, outpath: Path) -> None:
    if comparison.empty:
        return
    metrics = ["n_total", "n_pre", "n_post", "pre_rate", "post_rate", "rate_ratio", "burstiness_index", "post_omori_p", "radial_q50_km", "depth_q50_km"]
    fig, axes = plt.subplots(2, 5, figsize=(14, 6.4), dpi=DPI)
    axes = axes.ravel()
    for ax, metric in zip(axes, metrics):
        vals = pd.to_numeric(comparison[metric], errors="coerce")
        ax.bar(comparison["mainshock"], vals, color=["#4C72B0", "#55A868", "#C44E52"])
        ax.set_title(metric)
        ax.grid(True, axis="y", alpha=0.2)
        ax.tick_params(axis="x", rotation=0)
    fig.suptitle("Three-sequence baseline comparison")
    fig_save(fig, outpath)


def make_control_figure(control: pd.DataFrame, outpath: Path) -> None:
    if control.empty:
        return
    fig, ax = plt.subplots(figsize=(8.4, 5.3), dpi=DPI)
    xcol = "time_window_days" if "time_window_days" in control.columns else ("control_window_days" if "control_window_days" in control.columns else None)
    if xcol is None:
        raise KeyError(f"Control summary missing window-length column; available columns: {list(control.columns)}")
    for mainshock, sub in control.groupby("mainshock"):
        ax.plot(sub[xcol], sub["baseline_rate_ratio"], marker="o", lw=2, label=f"{mainshock} baseline")
        if "relative_control_rate" in sub.columns:
            ax.plot(sub[xcol], sub["relative_control_rate"], marker="s", lw=1.6, ls="--", label=f"{mainshock} control rate")
    ax.set_xlabel("Window length (days)")
    ax.set_ylabel("Rate ratio / relative control rate")
    ax.set_title("Observed vs control comparison")
    ax.grid(True, alpha=0.25)
    ax.legend(frameon=False, ncol=2)
    fig_save(fig, outpath)


def make_map_overview(match: pd.DataFrame, seq: pd.DataFrame, outpath: Path) -> None:
    if seq.empty:
        return
    fig, ax = plt.subplots(figsize=(8.7, 6.5), dpi=DPI)
    sc = ax.scatter(seq["lon"], seq["lat"], c=seq["time_rel_days"], cmap="coolwarm", s=np.clip((seq["mag"].fillna(1.5) ** 2) * 6, 10, 120), alpha=0.65, edgecolors="none")
    for _, row in match.iterrows():
        label = row["mainshock"] if "mainshock" in row.index else row.get("label", row.get("mainshock_label", ""))
        ax.scatter([row["matched_lon"]], [row["matched_lat"]], marker="*", s=260, c="gold", edgecolors="black", linewidths=0.8, zorder=5)
        ax.text(row["matched_lon"] + 0.03, row["matched_lat"] + 0.03, str(label), fontsize=9, weight="bold")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_title("Event-centered regional overview")
    ax.grid(True, alpha=0.2)
    cbar = fig.colorbar(sc, ax=ax, pad=0.02)
    cbar.set_label("Time relative to mainshock (days)")
    fig_save(fig, outpath)


def export_figure_data(seq: pd.DataFrame, summary: pd.DataFrame, comparison: pd.DataFrame, control: pd.DataFrame, robustness: pd.DataFrame) -> None:
    seq.to_csv(FIGURE_DATA_DIR / "baseline_sequence_table.csv", index=False)
    summary.to_csv(FIGURE_DATA_DIR / "sequence_metrics_summary.csv", index=False)
    comparison.to_csv(FIGURE_DATA_DIR / "three_sequence_comparison.csv", index=False)
    control.to_csv(FIGURE_DATA_DIR / "control_summary.csv", index=False)
    robustness.to_csv(FIGURE_DATA_DIR / "robustness_summary.csv", index=False)


def write_verification(payload: Dict[str, object], path: Path) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, default=to_jsonable)


def main() -> None:
    try:
        clean_output_dir()
        setup_style()
        inputs = load_step_outputs()
        cat = load_catalog()
        main = load_mainshocks()
        mecha = load_mech()
        station = load_station()
        match = read_csv(MATCH_PATH)
        if "matched_datetime" in match.columns:
            match["matched_datetime"] = parse_time(match["matched_datetime"])
        seq = read_csv(SEQ_PATH)
        if "datetime" in seq.columns:
            seq["datetime"] = parse_time(seq["datetime"])
        summary = read_csv(SUMMARY_PATH)
        window = read_csv(WINDOW_PATH)
        comparison = read_csv(COMPARISON_PATH)
        control = read_csv(CONTROL_PATH)
        robustness = read_csv(ROBUSTNESS_PATH)

        baseline = subset_baseline_from_seq(seq)
        if baseline.empty:
            baseline = seq.copy()
        if "pre_post" not in baseline.columns:
            if "time_rel_days" in baseline.columns:
                baseline["pre_post"] = np.where(baseline["time_rel_days"] < 0, "pre", np.where(baseline["time_rel_days"] > 0, "post", "mainshock"))
            else:
                baseline["pre_post"] = "unknown"
        baseline["pre_post"] = baseline["pre_post"].astype(str)

        export_figure_data(baseline, summary, comparison, control, robustness)

        make_map_overview(match, baseline, FIGURE_DIR / "all_mainshocks_overview_map.png")
        match_key = "mainshock" if "mainshock" in match.columns else ("label" if "label" in match.columns else None)
        if match_key is None:
            raise KeyError(f"Matched mainshock table missing label column; available columns: {list(match.columns)}")
        base_summary = baseline_slice(summary)
        summary_key = "mainshock" if "mainshock" in base_summary.columns else ("label" if "label" in base_summary.columns else None)
        if summary_key is None:
            raise KeyError(f"Summary table missing mainshock label column; available columns: {list(base_summary.columns)}")
        seq_key = "mainshock" if "mainshock" in baseline.columns else ("label" if "label" in baseline.columns else None)
        if seq_key is None:
            raise KeyError(f"Baseline sequence table missing mainshock label column; available columns: {list(baseline.columns)}")
        for ms in MAINSHOCKS:
            mrow = match[match[match_key] == ms].iloc[0]
            srow = base_summary[base_summary[summary_key] == ms].iloc[0]
            seq_ms = baseline[baseline[seq_key] == ms].copy()
            if seq_ms.empty:
                continue
            seq_ms = add_seq_geometry(seq_ms, mrow)
            make_event_map(seq_ms, mrow, ms, FIGURE_DIR / f"{ms}_event_centered_map.png")
            make_cumulative_counts(seq_ms, ms, FIGURE_DIR / f"{ms}_cumulative_counts.png")
            ms_window = window[(window["mainshock"] == ms) & (window["radius_km"] == BASELINE_RADIUS) & (window["time_window_days"] == BASELINE_TIME)]
            make_moving_rate(ms_window, ms, FIGURE_DIR / f"{ms}_moving_rate.png")
            make_decay_plot(seq_ms, srow, ms, FIGURE_DIR / f"{ms}_post_decay.png")
            make_radial_time_plot(seq_ms, ms, FIGURE_DIR / f"{ms}_time_distance.png")
            sensitivity_heatmaps(summary, ms, FIGURE_DIR)
            make_depth_stratified_plot(summary, ms, FIGURE_DIR / f"{ms}_depth_stratified.png")

        make_comparison_figure(comparison, FIGURE_DIR / "three_sequence_comparison_summary.png")
        make_control_figure(control, FIGURE_DIR / "control_comparison_summary.png")

        verification = {
            "n_catalog": int(len(cat)),
            "n_mainshocks": int(len(main)),
            "n_mechanism_rows": int(len(mecha)),
            "n_station_rows": int(len(station)),
            "n_sequence_rows": int(len(seq)),
            "n_summary_rows": int(len(summary)),
            "n_comparison_rows": int(len(comparison)),
            "n_control_rows": int(len(control)),
            "n_robustness_rows": int(len(robustness)),
            "generated_figures": sorted([p.name for p in FIGURE_DIR.glob("*.png")]),
            "mainshock_labels": MAINSHOCKS,
        }
        write_verification(verification, OUTPUT_DIR / "figure_generation_verification.json")
        log(f"[1] Generated {len(verification['generated_figures'])} figures in {FIGURE_DIR}")
        log("[2] Figure-generation outputs complete")
    except Exception:
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
