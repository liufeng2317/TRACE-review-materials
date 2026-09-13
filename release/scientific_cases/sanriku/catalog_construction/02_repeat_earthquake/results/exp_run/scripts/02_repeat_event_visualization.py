import json
import math
import os
import sys
import traceback
import argparse
from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.gridspec import GridSpec
from obspy import UTCDateTime
from obspy import read as obspy_read
from scipy.signal import correlate

BASE_PATH = Path("<WAVEFORM_DATA_ROOT>")
OBSERVATIONS_CSV = BASE_PATH / "metadata" / "observations.csv"
EVENTS_CSV = BASE_PATH / "metadata" / "events.csv"
STATIONS_CSV = BASE_PATH / "metadata" / "stations.csv"

ANALYSIS_OUTPUT_DIR = Path("<CASE_ROOT>/run/02_repeat_earthquake/exp_run/outputs/01_repeat_event_analysis")
OUTPUT_DIR = Path("<CASE_ROOT>/run/02_repeat_earthquake/exp_run/outputs/02_repeat_event_visualization")
SCRIPT_PATH = Path("<CASE_ROOT>/run/02_repeat_earthquake/exp_run/scripts/02_repeat_event_visualization.py")

TIME_START = pd.Timestamp("2025-11-01T00:00:00")
TIME_END = pd.Timestamp("2025-12-07T00:00:00")
PHASE_WINDOW = (-0.5, 5.5)
FILTER_BAND = (2.0, 15.0)
MAX_LAG_S = 1.5
LOOSE_CC_THRESHOLD = 0.55
STRICT_CC_THRESHOLD = 0.70
MIN_COMPONENTS_USED = 8
MIN_STATIONS_USED = 3
MAX_WAVEFORM_COMPONENTS_PER_PAIR = 4
MAX_WAVEFORM_PAIRS = 4
WAVEFORM_FIGURE_NCOLS = 2

OBS_USECOLS = [
    "evid",
    "origin_time",
    "event_latitude",
    "event_longitude",
    "event_depth_km",
    "event_magnitude",
    "station_id",
    "station_code",
    "station_latitude",
    "station_longitude",
    "component",
    "station_component",
    "sac_file",
    "p_time_after_origin_s",
    "s_time_after_origin_s",
]

plt.style.use("seaborn-v0_8-whitegrid")


def log(message: str) -> None:
    print(message, flush=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate repeat-earthquake analysis figures.")
    parser.add_argument("--base-path", type=Path, default=BASE_PATH)
    parser.add_argument("--analysis-output-dir", type=Path, default=ANALYSIS_OUTPUT_DIR)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    parser.add_argument("--time-start", default=str(TIME_START))
    parser.add_argument("--time-end", default=str(TIME_END))
    return parser.parse_args()


def apply_runtime_args(args: argparse.Namespace) -> None:
    global BASE_PATH, OBSERVATIONS_CSV, EVENTS_CSV, STATIONS_CSV
    global ANALYSIS_OUTPUT_DIR, OUTPUT_DIR, TIME_START, TIME_END

    BASE_PATH = args.base_path
    OBSERVATIONS_CSV = BASE_PATH / "metadata" / "observations.csv"
    EVENTS_CSV = BASE_PATH / "metadata" / "events.csv"
    STATIONS_CSV = BASE_PATH / "metadata" / "stations.csv"
    ANALYSIS_OUTPUT_DIR = args.analysis_output_dir
    OUTPUT_DIR = args.output_dir
    TIME_START = pd.Timestamp(args.time_start)
    TIME_END = pd.Timestamp(args.time_end)


def time_window_label() -> str:
    start = TIME_START.strftime("%Y-%m-%d")
    end_inclusive = (TIME_END - pd.Timedelta(days=1)).strftime("%Y-%m-%d")
    return f"{start} to {end_inclusive}"


def ensure_output_dir() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    stale_names = {
        "repeat_event_spatial_distribution.png",
        "repeat_event_spatial_zoom.png",
        "repeat_event_waveform_comparison.png",
        "repeat_event_family_timeline.png",
        "repeat_event_correlation_statistics.png",
        "repeat_event_statistics.png",
        "station_component_diagnostics.png",
        "analysis_summary.json",
    }
    for name in stale_names:
        stale_path = OUTPUT_DIR / name
        if stale_path.exists():
            stale_path.unlink()


def read_json(path: Path) -> Dict[str, object]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_inputs() -> Dict[str, object]:
    log(f"Loading analysis outputs from {ANALYSIS_OUTPUT_DIR}")
    candidate_pairs = pd.read_csv(ANALYSIS_OUTPUT_DIR / "candidate_event_pairs.csv", parse_dates=["origin_time_1", "origin_time_2"], low_memory=False)
    repeat_pairs = pd.read_csv(ANALYSIS_OUTPUT_DIR / "repeat_event_pairs.csv", parse_dates=["origin_time_1", "origin_time_2"], low_memory=False)
    station_cc = pd.read_csv(ANALYSIS_OUTPUT_DIR / "station_component_cc.csv", low_memory=False)
    families = pd.read_csv(ANALYSIS_OUTPUT_DIR / "repeat_event_families.csv", parse_dates=["start_time", "end_time"])
    family_members = pd.read_csv(ANALYSIS_OUTPUT_DIR / "repeat_family_members.csv", parse_dates=["origin_time"])
    analysis_summary = read_json(ANALYSIS_OUTPUT_DIR / "analysis_summary.json")

    log(f"Loading event/station metadata from {BASE_PATH / 'metadata'}")
    events = pd.read_csv(EVENTS_CSV, parse_dates=["origin_time"], low_memory=False)
    stations = pd.read_csv(STATIONS_CSV, low_memory=False)
    observations = pd.read_csv(OBSERVATIONS_CSV, usecols=OBS_USECOLS, parse_dates=["origin_time"], low_memory=False)

    observations["evid"] = observations["evid"].astype(str)
    observations["station_component"] = observations["station_component"].astype(str)
    observations["station_id"] = observations["station_id"].astype(str)
    observations["station_code"] = observations["station_code"].astype(str)
    observations["sac_file"] = observations["sac_file"].astype(str)
    events["evid"] = events["evid"].astype(str)

    window_events = events[(events["origin_time"] >= TIME_START) & (events["origin_time"] < TIME_END)].copy()
    return {
        "candidate_pairs": candidate_pairs,
        "repeat_pairs": repeat_pairs,
        "station_cc": station_cc,
        "families": families,
        "family_members": family_members,
        "analysis_summary": analysis_summary,
        "events": events,
        "window_events": window_events,
        "stations": stations,
        "observations": observations,
    }


def validate_columns(df: pd.DataFrame, required_cols: list, name: str) -> None:
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"{name} missing required columns: {missing}")


def validate_inputs(data: Dict[str, object]) -> None:
    required = {
        "candidate_pairs": ["event_id_1", "event_id_2", "epicentral_distance_km", "magnitude_diff", "common_station_components"],
        "repeat_pairs": ["event_id_1", "event_id_2", "median_cc", "num_components_used", "repeat_candidate_level"],
        "station_cc": ["event_id_1", "event_id_2", "station_component", "positive_peak_cc", "lag_s", "status"],
        "families": ["family_id", "family_size", "num_edges"],
        "family_members": ["family_id", "event_id", "origin_time", "latitude", "longitude", "magnitude"],
    }
    for key, cols in required.items():
        df = data[key]
        validate_columns(df, cols, key)
        if len(df) == 0 and key in {"candidate_pairs", "repeat_pairs", "station_cc"}:
            raise ValueError(f"{key} is empty")


def build_family_event_lookup(family_members: pd.DataFrame) -> Dict[str, str]:
    lookup = {}
    for row in family_members.itertuples(index=False):
        lookup[str(row.event_id)] = str(row.family_id)
    return lookup


def augment_repeat_pairs(repeat_pairs: pd.DataFrame, family_members: pd.DataFrame) -> pd.DataFrame:
    family_lookup = build_family_event_lookup(family_members)
    df = repeat_pairs.copy()
    validate_columns(df, ["event_id_1", "event_id_2"], "repeat_pairs_before_augment")
    df["event_id_1"] = df["event_id_1"].astype(str)
    df["event_id_2"] = df["event_id_2"].astype(str)
    df["family_id_1"] = df["event_id_1"].map(family_lookup)
    df["family_id_2"] = df["event_id_2"].map(family_lookup)
    df["same_high_conf_family"] = df["family_id_1"].notna() & (df["family_id_1"] == df["family_id_2"])
    df["family_id"] = np.where(df["same_high_conf_family"], df["family_id_1"], pd.NA)
    validate_columns(df, ["family_id_1", "family_id_2", "same_high_conf_family", "family_id"], "repeat_pairs_after_augment")
    return df


def assign_family_colors(families: pd.DataFrame) -> Dict[str, tuple]:
    family_ids = list(families.sort_values(["family_size", "family_id"], ascending=[False, True])["family_id"].astype(str))
    cmap = plt.get_cmap("tab20")
    colors = {}
    for idx, family_id in enumerate(family_ids):
        colors[family_id] = cmap(idx % 20)
    return colors


def save_figure(fig: plt.Figure, filename: str) -> str:
    path = OUTPUT_DIR / filename
    fig.savefig(path, dpi=220, bbox_inches="tight")
    plt.close(fig)
    return str(path)


def plot_spatial_map(window_events: pd.DataFrame, family_members: pd.DataFrame, repeat_pairs: pd.DataFrame, families: pd.DataFrame) -> str:
    family_colors = assign_family_colors(families)
    fig, ax = plt.subplots(figsize=(10.5, 8.5))
    ax.scatter(window_events["longitude"], window_events["latitude"], s=9, c="0.82", alpha=0.55, linewidths=0, label="All events in window")

    high_pairs = repeat_pairs[repeat_pairs["repeat_candidate_level"] == "high_confidence"].copy()
    for row in high_pairs.itertuples(index=False):
        family_id = row.family_id if pd.notna(row.family_id) else None
        color = family_colors.get(str(family_id), (0.4, 0.4, 0.4, 0.5))
        ax.plot([row.longitude_1, row.longitude_2], [row.latitude_1, row.latitude_2], color=color, lw=0.9, alpha=0.55, zorder=2)

    for row in family_members.itertuples(index=False):
        color = family_colors.get(str(row.family_id), "tab:red")
        ax.scatter(row.longitude, row.latitude, s=42 + 22 * max(float(row.magnitude) - 1.0, 0.0), color=color, edgecolor="black", linewidth=0.35, zorder=3)

    for family in families.sort_values("family_size", ascending=False).head(8).itertuples(index=False):
        sub = family_members[family_members["family_id"] == family.family_id]
        if len(sub) == 0:
            continue
        ax.text(sub["longitude"].mean(), sub["latitude"].mean(), str(family.family_id), fontsize=8, weight="bold", ha="center", va="center", zorder=4)

    ax.set_title(f"Repeat-earthquake candidates and families\nAomori aftershock window {time_window_label()}", fontsize=14)
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.legend(loc="lower left", frameon=True)
    return save_figure(fig, "repeat_event_spatial_distribution.png")


def plot_spatial_zoom(family_members: pd.DataFrame, repeat_pairs: pd.DataFrame, families: pd.DataFrame) -> str:
    family_colors = assign_family_colors(families)
    fig, ax = plt.subplots(figsize=(9.6, 7.8))
    if len(family_members) == 0:
        raise ValueError("family_members is empty; cannot make zoom map")

    pad_lon = max(0.02, 0.2 * (family_members["longitude"].max() - family_members["longitude"].min()))
    pad_lat = max(0.02, 0.2 * (family_members["latitude"].max() - family_members["latitude"].min()))
    top_family_ids = set(
        families.sort_values(["family_size", "median_pair_cc"], ascending=[False, False])["family_id"].astype(str).head(8)
    )

    high_pairs = repeat_pairs[repeat_pairs["repeat_candidate_level"] == "high_confidence"].copy()
    lowlight_pairs = high_pairs[~high_pairs["family_id"].astype(str).isin(top_family_ids)]
    for row in lowlight_pairs.itertuples(index=False):
        ax.plot(
            [row.longitude_1, row.longitude_2],
            [row.latitude_1, row.latitude_2],
            color="0.72",
            lw=0.7,
            alpha=0.35,
            zorder=1,
        )

    for row in high_pairs[high_pairs["family_id"].astype(str).isin(top_family_ids)].itertuples(index=False):
        family_id = str(row.family_id) if pd.notna(row.family_id) else None
        color = family_colors.get(family_id, (0.35, 0.35, 0.35, 0.7))
        ax.plot(
            [row.longitude_1, row.longitude_2],
            [row.latitude_1, row.latitude_2],
            color=color,
            lw=1.2,
            alpha=0.75,
            zorder=2,
        )

    for family in families.sort_values(["family_size", "median_pair_cc"], ascending=[False, False]).itertuples(index=False):
        sub = family_members[family_members["family_id"] == family.family_id].copy().sort_values("origin_time")
        family_id = str(family.family_id)
        is_top = family_id in top_family_ids
        color = family_colors.get(family_id, "tab:blue") if is_top else "0.70"
        ax.scatter(
            sub["longitude"],
            sub["latitude"],
            s=42 if is_top else 24,
            color=color,
            edgecolor="black" if is_top else "none",
            linewidth=0.35 if is_top else 0.0,
            alpha=0.95 if is_top else 0.45,
            zorder=3 if is_top else 1,
        )
        ax.plot(
            sub["longitude"],
            sub["latitude"],
            color=color,
            lw=0.9 if is_top else 0.5,
            alpha=0.60 if is_top else 0.25,
            zorder=2 if is_top else 1,
        )
        if is_top and len(sub) > 0:
            ax.text(
                sub["longitude"].median(),
                sub["latitude"].median(),
                f"{family_id}\n(n={family.family_size})",
                fontsize=8.3,
                weight="bold",
                ha="center",
                va="center",
                bbox=dict(boxstyle="round,pad=0.20", fc="white", ec=color, alpha=0.82),
                zorder=4,
            )

    ax.set_xlim(family_members["longitude"].min() - pad_lon, family_members["longitude"].max() + pad_lon)
    ax.set_ylim(family_members["latitude"].min() - pad_lat, family_members["latitude"].max() + pad_lat)
    ax.set_title("Zoomed repeat-earthquake family structure\nTop families highlighted; smaller families shown in gray", fontsize=13.5)
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.text(
        0.02,
        0.02,
        "Only the 8 largest families are directly labeled; all other high-confidence family members are retained in gray for context.",
        transform=ax.transAxes,
        fontsize=8.3,
        ha="left",
        va="bottom",
        bbox=dict(boxstyle="round,pad=0.20", fc="white", ec="0.8", alpha=0.85),
    )
    return save_figure(fig, "repeat_event_spatial_zoom.png")


def plot_correlation_statistics(repeat_pairs: pd.DataFrame) -> str:
    fig = plt.figure(figsize=(13.5, 10.5))
    gs = GridSpec(2, 2, figure=fig)

    ax1 = fig.add_subplot(gs[0, 0])
    vals = repeat_pairs["median_cc"].dropna()
    ax1.hist(vals, bins=35, color="#4C78A8", edgecolor="white", alpha=0.88)
    ax1.axvline(LOOSE_CC_THRESHOLD, color="orange", lw=1.8, ls="--", label="Loose = 0.55")
    ax1.axvline(STRICT_CC_THRESHOLD, color="crimson", lw=1.8, ls="--", label="High-confidence = 0.70")
    ax1.set_title("Distribution of median cross-correlation")
    ax1.set_xlabel("median_cc")
    ax1.set_ylabel("Count")
    ax1.legend(frameon=True)

    ax2 = fig.add_subplot(gs[0, 1])
    sc = ax2.scatter(repeat_pairs["epicentral_distance_km"], repeat_pairs["median_cc"], c=repeat_pairs["common_station_components"], s=18, cmap="viridis", alpha=0.65, linewidths=0)
    ax2.axhline(LOOSE_CC_THRESHOLD, color="orange", lw=1.4, ls="--")
    ax2.axhline(STRICT_CC_THRESHOLD, color="crimson", lw=1.4, ls="--")
    ax2.set_title("median_cc vs epicentral distance")
    ax2.set_xlabel("Epicentral distance (km)")
    ax2.set_ylabel("median_cc")
    cbar = fig.colorbar(sc, ax=ax2)
    cbar.set_label("common_station_components")

    ax3 = fig.add_subplot(gs[1, 0])
    ax3.scatter(repeat_pairs["magnitude_diff"], repeat_pairs["median_cc"], s=16, c="#F58518", alpha=0.6, linewidths=0)
    ax3.axhline(LOOSE_CC_THRESHOLD, color="orange", lw=1.4, ls="--")
    ax3.axhline(STRICT_CC_THRESHOLD, color="crimson", lw=1.4, ls="--")
    ax3.set_title("median_cc vs magnitude difference")
    ax3.set_xlabel("Magnitude difference")
    ax3.set_ylabel("median_cc")

    ax4 = fig.add_subplot(gs[1, 1])
    ax4.scatter(repeat_pairs["common_station_components"], repeat_pairs["median_cc"], s=16, c="#54A24B", alpha=0.6, linewidths=0)
    ax4.axhline(LOOSE_CC_THRESHOLD, color="orange", lw=1.4, ls="--")
    ax4.axhline(STRICT_CC_THRESHOLD, color="crimson", lw=1.4, ls="--")
    ax4.set_title("median_cc vs shared station-components")
    ax4.set_xlabel("common_station_components")
    ax4.set_ylabel("median_cc")

    fig.suptitle("Repeat-event correlation statistics", fontsize=15, y=0.98)
    return save_figure(fig, "repeat_event_correlation_statistics.png")


def plot_repeat_statistics(repeat_pairs: pd.DataFrame, families: pd.DataFrame) -> str:
    fig = plt.figure(figsize=(13.5, 10.5))
    gs = GridSpec(2, 2, figure=fig)

    ax1 = fig.add_subplot(gs[0, 0])
    high = repeat_pairs[repeat_pairs["repeat_candidate_level"] == "high_confidence"]
    loose = repeat_pairs[repeat_pairs["repeat_candidate_level"].isin(["high_confidence", "loose"])]
    ax1.hist(loose["time_diff_s"].dropna() / 3600.0, bins=30, color="#72B7B2", alpha=0.75, label="Loose+")
    ax1.hist(high["time_diff_s"].dropna() / 3600.0, bins=30, color="#E45756", alpha=0.75, label="High-confidence")
    ax1.set_title("Inter-event time separation")
    ax1.set_xlabel("Time difference (hours)")
    ax1.set_ylabel("Pair count")
    ax1.legend(frameon=True)

    ax2 = fig.add_subplot(gs[0, 1])
    ax2.hist(loose["depth_diff_km"].dropna(), bins=25, color="#4C78A8", alpha=0.8)
    ax2.set_title("Depth-difference distribution")
    ax2.set_xlabel("Depth difference (km)")
    ax2.set_ylabel("Pair count")

    ax3 = fig.add_subplot(gs[1, 0])
    ax3.hist(loose["magnitude_diff"].dropna(), bins=25, color="#F58518", alpha=0.82)
    ax3.set_title("Magnitude-difference distribution")
    ax3.set_xlabel("Magnitude difference")
    ax3.set_ylabel("Pair count")

    ax4 = fig.add_subplot(gs[1, 1])
    if len(families) > 0:
        fam_sizes = families["family_size"].astype(int)
        bins = np.arange(fam_sizes.min(), fam_sizes.max() + 2) - 0.5
        ax4.hist(fam_sizes, bins=bins, color="#54A24B", alpha=0.85, rwidth=0.85)
    ax4.set_title("High-confidence family-size distribution")
    ax4.set_xlabel("Family size")
    ax4.set_ylabel("Count")

    fig.suptitle("Repeat-earthquake summary statistics", fontsize=15, y=0.98)
    return save_figure(fig, "repeat_event_statistics.png")


def plot_station_diagnostics(station_cc: pd.DataFrame) -> str:
    used = station_cc[station_cc["status"] == "used"].copy()
    if len(used) == 0:
        raise ValueError("No used station-component rows available for diagnostics")
    used["station_code"] = used["station_code"].astype(str)
    used["station_component"] = used["station_component"].astype(str)

    top_station = (
        used.groupby("station_code")
        .agg(n_used=("positive_peak_cc", "size"), median_cc=("positive_peak_cc", "median"))
        .sort_values(["n_used", "median_cc"], ascending=[False, False])
        .head(15)
        .reset_index()
    )
    top_component = (
        used.groupby("station_component")
        .agg(n_used=("positive_peak_cc", "size"), median_cc=("positive_peak_cc", "median"))
        .sort_values(["n_used", "median_cc"], ascending=[False, False])
        .head(15)
        .reset_index()
    )

    fig = plt.figure(figsize=(13.8, 10.0))
    gs = GridSpec(2, 2, figure=fig)

    ax1 = fig.add_subplot(gs[0, 0])
    ax1.barh(top_station["station_code"], top_station["n_used"], color="#4C78A8")
    ax1.invert_yaxis()
    ax1.set_title("Top contributing stations")
    ax1.set_xlabel("Used station-component count")

    ax2 = fig.add_subplot(gs[0, 1])
    ax2.barh(top_component["station_component"], top_component["n_used"], color="#F58518")
    ax2.invert_yaxis()
    ax2.set_title("Top contributing station-components")
    ax2.set_xlabel("Used count")

    ax3 = fig.add_subplot(gs[1, 0])
    phase_order = ["S", "P"]
    phase_data = [used.loc[used["phase_used"] == ph, "positive_peak_cc"].dropna().values for ph in phase_order]
    phase_data = [arr if len(arr) else np.array([np.nan]) for arr in phase_data]
    ax3.boxplot(phase_data, tick_labels=phase_order, showfliers=False)
    ax3.set_title("CC distribution by phase alignment")
    ax3.set_ylabel("positive_peak_cc")

    ax4 = fig.add_subplot(gs[1, 1])
    ax4.hist(used["lag_s"].dropna(), bins=40, color="#54A24B", alpha=0.82)
    ax4.set_title("Lag distribution of used station-components")
    ax4.set_xlabel("Lag at positive peak (s)")
    ax4.set_ylabel("Count")

    fig.suptitle("Station/station-component diagnostics", fontsize=15, y=0.98)
    return save_figure(fig, "station_component_diagnostics.png")


def plot_family_timeline(family_members: pd.DataFrame, families: pd.DataFrame) -> str:
    family_colors = assign_family_colors(families)
    fam_order = families.sort_values(["family_size", "median_pair_cc"], ascending=[False, False])["family_id"].astype(str).tolist()
    y_lookup = {fam: idx for idx, fam in enumerate(fam_order, start=1)}

    fig, ax = plt.subplots(figsize=(13.5, 7.5))
    for family_id in fam_order:
        sub = family_members[family_members["family_id"] == family_id].copy().sort_values("origin_time")
        if len(sub) == 0:
            continue
        y = np.full(len(sub), y_lookup[family_id])
        color = family_colors.get(family_id, "tab:blue")
        sizes = 40 + 35 * np.maximum(sub["magnitude"].astype(float) - sub["magnitude"].min() + 0.2, 0.2)
        ax.scatter(sub["origin_time"], y, s=sizes, color=color, edgecolor="black", linewidth=0.4, zorder=3)
        ax.plot(sub["origin_time"], y, color=color, lw=0.9, alpha=0.55, zorder=2)

        if len(sub) > 1:
            deltas_h = np.diff(sub["origin_time"].values.astype("datetime64[s]")).astype("timedelta64[s]").astype(float) / 3600.0
            for t, d in zip(sub["origin_time"].iloc[1:], deltas_h):
                ax.text(t, y_lookup[family_id] + 0.12, f"{d:.1f} h", fontsize=6.5, rotation=30, color=color)

    ax.set_title("Repeat-event family timeline and magnitude evolution", fontsize=14)
    ax.set_xlabel("Origin time")
    ax.set_ylabel("Family")
    ax.set_yticks(list(y_lookup.values()))
    ax.set_yticklabels(list(y_lookup.keys()))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d\n%H:%M"))
    return save_figure(fig, "repeat_event_family_timeline.png")


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2.0) ** 2
    return 2.0 * r * math.asin(math.sqrt(a))


def build_observation_index(observations: pd.DataFrame) -> Dict[Tuple[str, str], Dict[str, object]]:
    cols = OBS_USECOLS
    observations = observations[(observations["origin_time"] >= TIME_START) & (observations["origin_time"] < TIME_END)].copy()
    observations = observations.sort_values(["evid", "station_component", "s_time_after_origin_s", "p_time_after_origin_s"])
    observations = observations.drop_duplicates(subset=["evid", "station_component"], keep="first")
    index = {}
    for row in observations[cols].itertuples(index=False):
        rec = dict(zip(cols, row))
        index[(str(rec["evid"]), str(rec["station_component"]))] = rec
    return index


def read_filtered_trace(sac_file: str):
    tr = obspy_read(sac_file)[0].copy()
    tr.detrend("demean")
    tr.detrend("linear")
    tr.taper(max_percentage=0.05, type="cosine")
    tr.filter("bandpass", freqmin=FILTER_BAND[0], freqmax=FILTER_BAND[1], corners=4, zerophase=True)
    return tr


def extract_phase_window(obs_rec: Dict[str, object], phase_used: str) -> Tuple[np.ndarray, float, np.ndarray]:
    phase_key = "s_time_after_origin_s" if phase_used == "S" else "p_time_after_origin_s"
    phase_after_origin = obs_rec.get(phase_key)
    if pd.isna(phase_after_origin):
        raise ValueError(f"missing {phase_used} pick")
    tr = read_filtered_trace(str(obs_rec["sac_file"]))
    phase_abs = UTCDateTime(pd.Timestamp(obs_rec["origin_time"]).to_pydatetime()) + float(phase_after_origin)
    win_start = phase_abs + PHASE_WINDOW[0]
    win_end = phase_abs + PHASE_WINDOW[1]
    if win_start < tr.stats.starttime or win_end > tr.stats.endtime:
        raise ValueError("window outside trace")
    sliced = tr.copy().slice(starttime=win_start, endtime=win_end, nearest_sample=False)
    data = np.asarray(sliced.data, dtype=np.float64)
    if data.size < 10 or not np.all(np.isfinite(data)):
        raise ValueError("invalid waveform data")
    data = data - np.mean(data)
    std = float(np.std(data))
    if std <= 0.0:
        raise ValueError("zero variance")
    normed = data / std
    times = np.arange(data.size) / float(sliced.stats.sampling_rate) + PHASE_WINDOW[0]
    return data, float(sliced.stats.sampling_rate), times, normed


def compute_cc(x: np.ndarray, y: np.ndarray, sr: float) -> Tuple[float, float]:
    n = min(len(x), len(y))
    if n < 10:
        raise ValueError("too few samples for cross-correlation")
    x = x[:n]
    y = y[:n]
    corr = correlate(x, y, mode="full", method="auto") / n
    lags = np.arange(-n + 1, n) / sr
    mask = np.abs(lags) <= MAX_LAG_S
    corr_m = corr[mask]
    lags_m = lags[mask]
    pos_mask = corr_m > 0
    if not np.any(pos_mask):
        raise ValueError("no positive peak")
    pos_corr = corr_m[pos_mask]
    pos_lags = lags_m[pos_mask]
    idx = int(np.argmax(pos_corr))
    return float(pos_corr[idx]), float(pos_lags[idx])


def choose_representative_pairs(repeat_pairs: pd.DataFrame, families: pd.DataFrame) -> pd.DataFrame:
    selected = []
    high = repeat_pairs[repeat_pairs["repeat_candidate_level"] == "high_confidence"].copy()
    if len(high) == 0:
        return pd.DataFrame(columns=repeat_pairs.columns)

    top_global = high.sort_values(["median_cc", "num_components_used", "num_stations_used"], ascending=[False, False, False]).head(1)
    if len(top_global):
        selected.append(top_global)

    for fam in families.sort_values(["family_size", "median_pair_cc"], ascending=[False, False]).head(MAX_WAVEFORM_PAIRS).itertuples(index=False):
        sub = high[high["family_id"] == fam.family_id].copy()
        if len(sub) == 0:
            continue
        best = sub.sort_values(["median_cc", "num_components_used", "num_stations_used"], ascending=[False, False, False]).head(1)
        selected.append(best)

    if not selected:
        return pd.DataFrame(columns=repeat_pairs.columns)
    result = pd.concat(selected, ignore_index=True)
    result = result.drop_duplicates(subset=["event_id_1", "event_id_2"])
    return result.head(MAX_WAVEFORM_PAIRS)


def plot_waveform_comparison(representative_pairs: pd.DataFrame, station_cc: pd.DataFrame, observations: pd.DataFrame) -> Tuple[str, Dict[str, object]]:
    obs_index = build_observation_index(observations)
    diagnostics = {"pairs": [], "n_pairs_plotted": 0}
    if len(representative_pairs) == 0:
        raise ValueError("No representative pairs available for waveform plotting")

    pair_panels = []
    for pair in representative_pairs.itertuples(index=False):
        sc_sub = station_cc[
            (station_cc["event_id_1"].astype(str) == str(pair.event_id_1))
            & (station_cc["event_id_2"].astype(str) == str(pair.event_id_2))
            & (station_cc["status"] == "used")
        ].copy()
        if len(sc_sub) == 0:
            continue
        comps = []
        for row in sc_sub.itertuples(index=False):
            rec1 = obs_index.get((str(pair.event_id_1), str(row.station_component)))
            rec2 = obs_index.get((str(pair.event_id_2), str(row.station_component)))
            if rec1 is None or rec2 is None:
                continue
            evt_lat = 0.5 * (float(pair.latitude_1) + float(pair.latitude_2))
            evt_lon = 0.5 * (float(pair.longitude_1) + float(pair.longitude_2))
            dist = haversine_km(evt_lat, evt_lon, float(row.station_latitude), float(row.station_longitude))
            comps.append((row, rec1, rec2, dist))
        comps = sorted(comps, key=lambda item: item[3])[:MAX_WAVEFORM_COMPONENTS_PER_PAIR]

        overlays = []
        for row, rec1, rec2, dist in comps:
            try:
                _, sr1, times1, norm1 = extract_phase_window(rec1, str(row.phase_used))
                _, sr2, _, norm2 = extract_phase_window(rec2, str(row.phase_used))
                if abs(sr1 - sr2) > 1e-6:
                    log(
                        f"Waveform skip due to sampling-rate mismatch: {pair.event_id_1} vs {pair.event_id_2} | "
                        f"{row.station_component} | sr1={sr1} sr2={sr2}"
                    )
                    continue
                cc_val, lag = compute_cc(norm1, norm2, sr1)
                shift_samples = int(round(lag * sr1))
                aligned2 = np.full_like(norm2, np.nan)
                if shift_samples >= 0:
                    if shift_samples < len(norm2):
                        aligned2[shift_samples:] = norm2[: len(norm2) - shift_samples]
                else:
                    neg = abs(shift_samples)
                    if neg < len(norm2):
                        aligned2[: len(norm2) - neg] = norm2[neg:]
                overlays.append({
                    "station_component": row.station_component,
                    "phase_used": row.phase_used,
                    "distance_km": dist,
                    "times": times1,
                    "trace1": norm1,
                    "trace2": aligned2,
                    "cc": cc_val,
                    "lag_s": lag,
                    "meta": {
                        "event_id_1": str(pair.event_id_1),
                        "event_id_2": str(pair.event_id_2),
                        "station_component": str(row.station_component),
                        "phase_used": str(row.phase_used),
                        "distance_km": float(dist),
                        "cc": float(cc_val),
                        "lag_s": float(lag),
                    },
                })
            except Exception as exc:
                log(
                    f"Waveform overlay skip: {pair.event_id_1} vs {pair.event_id_2} | "
                    f"{row.station_component} | reason={exc}"
                )
                continue

        if overlays:
            pair_panels.append({
                "pair_label": f"{pair.event_id_1} vs {pair.event_id_2}",
                "family_id": pair.family_id if pd.notna(pair.family_id) else "NA",
                "pair_median_cc": float(pair.median_cc),
                "pair_num_components": int(pair.num_components_used),
                "pair_num_stations": int(pair.num_stations_used),
                "overlays": overlays,
            })

    if len(pair_panels) == 0:
        raise ValueError("No waveform overlays could be prepared")

    n_panels = len(pair_panels)
    ncols = min(WAVEFORM_FIGURE_NCOLS, n_panels)
    nrows = int(math.ceil(n_panels / ncols))
    fig, axes = plt.subplots(nrows, ncols, figsize=(16, 4.8 * nrows), sharex=False, sharey=False)
    axes = np.atleast_1d(axes).ravel()

    for ax, panel in zip(axes, pair_panels):
        offsets = np.arange(len(panel["overlays"]))[::-1] * 2.5
        for idx, (overlay, offset) in enumerate(zip(panel["overlays"], offsets)):
            ax.plot(overlay["times"], overlay["trace1"] + offset, color="#4C78A8", lw=1.0, label="Event 1" if idx == 0 else None)
            ax.plot(overlay["times"], overlay["trace2"] + offset, color="#E45756", lw=1.0, alpha=0.9, label="Event 2 shifted" if idx == 0 else None)
            ax.text(
                0.01,
                (offset + 0.2) / (offsets[0] + 1.6 if len(offsets) else 1.0),
                f"{overlay['station_component']}  {overlay['phase_used']}  d={overlay['distance_km']:.1f} km  CC={overlay['cc']:.2f}  lag={overlay['lag_s']:.2f} s",
                transform=ax.transAxes,
                fontsize=8.6,
                va="bottom",
                ha="left",
                bbox=dict(boxstyle="round,pad=0.18", fc="white", ec="0.82", alpha=0.78),
            )
        ax.axvline(0.0, color="black", lw=0.8, ls="--", alpha=0.8)
        ax.set_title(
            f"{panel['pair_label']} | family={panel['family_id']}\nmedian_cc={panel['pair_median_cc']:.2f}, used={panel['pair_num_components']} comps / {panel['pair_num_stations']} stations",
            fontsize=10.5,
            pad=8,
        )
        ax.set_xlabel("Time relative to aligned phase (s)")
        ax.set_ylabel("Stacked norm amp")
        if len(offsets):
            ax.set_ylim(-1.8, offsets[0] + 1.8)

    for ax in axes[n_panels:]:
        ax.axis("off")

    axes[0].legend(loc="upper right", ncol=2, frameon=True, fontsize=9)
    fig.suptitle("Representative repeat-event waveform comparisons", fontsize=15, y=0.985)
    fig.tight_layout(rect=(0.02, 0.02, 0.98, 0.965))
    path = save_figure(fig, "repeat_event_waveform_comparison.png")

    diagnostics["pairs"] = [overlay["meta"] for panel in pair_panels for overlay in panel["overlays"]]
    diagnostics["n_pairs_plotted"] = int(len(pair_panels))
    diagnostics["n_components_plotted"] = int(sum(len(panel["overlays"]) for panel in pair_panels))
    diagnostics["panels_per_pair_max"] = int(MAX_WAVEFORM_COMPONENTS_PER_PAIR)
    return path, diagnostics


def build_threshold_sensitivity(candidate_pairs: pd.DataFrame, repeat_pairs: pd.DataFrame, families: pd.DataFrame) -> Dict[str, object]:
    result = {}
    dist_thresholds = [3.0, 5.0, 10.0]
    mag_thresholds = [0.8, 1.0]
    common_thresholds = [20, 40, 60]
    cc_thresholds = [0.55, 0.70, 0.80]

    validate_columns(candidate_pairs, ["epicentral_distance_km", "magnitude_diff", "common_station_components"], "candidate_pairs_for_sensitivity")
    validate_columns(repeat_pairs, ["num_components_used", "num_stations_used", "median_cc"], "repeat_pairs_for_sensitivity")

    candidate_counts = {}
    for d in dist_thresholds:
        for m in mag_thresholds:
            for c in common_thresholds:
                mask = (
                    (candidate_pairs["epicentral_distance_km"] <= d)
                    & (candidate_pairs["magnitude_diff"] <= m)
                    & (candidate_pairs["common_station_components"] >= c)
                )
                candidate_counts[f"dist<={d}|mag<={m}|common>={c}"] = int(mask.sum())
    result["candidate_threshold_counts_from_final_csv"] = candidate_counts

    repeat_counts = {}
    valid = repeat_pairs[(repeat_pairs["num_components_used"] >= MIN_COMPONENTS_USED) & (repeat_pairs["num_stations_used"] >= MIN_STATIONS_USED)]
    for cc in cc_thresholds:
        repeat_counts[f"median_cc>={cc}"] = int((valid["median_cc"] >= cc).sum())
    result["repeat_pair_threshold_counts"] = repeat_counts
    result["n_high_confidence_families"] = int(len(families))
    result["family_size_distribution"] = families["family_size"].astype(int).value_counts().sort_index().to_dict() if len(families) else {}
    return result


def sanitize_summary_text(obj):
    if isinstance(obj, dict):
        return {k: sanitize_summary_text(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [sanitize_summary_text(v) for v in obj]
    if isinstance(obj, str):
        return obj.replace(
            "S-priority then P fallback",
            "S-priority with P used only when both events lack matched S picks on the same station_component",
        ).replace(
            "fallback",
            "secondary-choice phase rule",
        )
    return obj


def update_summary_json(data: Dict[str, object], figure_paths: Dict[str, str], waveform_diag: Dict[str, object], sensitivity: Dict[str, object]) -> None:
    summary = sanitize_summary_text(data["analysis_summary"])
    summary["visualization"] = {
        "script_path": str(SCRIPT_PATH),
        "output_dir": str(OUTPUT_DIR),
        "time_window": {"start": str(TIME_START), "end": str(TIME_END)},
        "baseline_processing_chain": {
            "phase_order": ["S", "P"],
            "phase_selection_rule": "use S when both events have valid S picks on the exact same station_component; otherwise use P when both events have valid P picks on that same station_component",
            "phase_window_s": list(PHASE_WINDOW),
            "filter_band_hz": list(FILTER_BAND),
            "max_lag_s": MAX_LAG_S,
            "channel_matching": "exact station_component match; no XH/XL, YH/YL, ZH/ZL, E/N/U merging",
            "normalization": "demean, detrend, taper, 2-15 Hz bandpass, phase window extraction, unit-std normalization",
        },
        "figure_paths": figure_paths,
        "waveform_representatives": waveform_diag,
        "threshold_sensitivity": sensitivity,
        "counts": {
            "window_events": int(len(data["window_events"])),
            "candidate_pairs": int(len(data["candidate_pairs"])),
            "repeat_pairs": int(len(data["repeat_pairs"])),
            "station_component_rows": int(len(data["station_cc"])),
            "high_confidence_pairs": int((data["repeat_pairs"]["repeat_candidate_level"] == "high_confidence").sum()),
            "loose_pairs": int((data["repeat_pairs"]["repeat_candidate_level"] == "loose").sum()),
            "families": int(len(data["families"])),
            "family_members": int(len(data["family_members"])),
        },
    }
    with open(OUTPUT_DIR / "analysis_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2, default=str)


def validate_outputs(figure_paths: Dict[str, str]) -> None:
    required = [
        "repeat_event_spatial_distribution.png",
        "repeat_event_spatial_zoom.png",
        "repeat_event_waveform_comparison.png",
        "repeat_event_family_timeline.png",
        "repeat_event_correlation_statistics.png",
        "repeat_event_statistics.png",
        "station_component_diagnostics.png",
        "analysis_summary.json",
    ]
    for name in required:
        path = OUTPUT_DIR / name
        if not path.exists() or path.stat().st_size == 0:
            raise ValueError(f"Missing or empty output: {path}")
    if len(figure_paths) < 7:
        raise ValueError("Expected at least 7 figure paths")


def main() -> None:
    apply_runtime_args(parse_args())
    ensure_output_dir()
    data = load_inputs()
    validate_inputs(data)

    data["repeat_pairs"] = augment_repeat_pairs(data["repeat_pairs"], data["family_members"])

    figure_paths = {}
    figure_paths["spatial_distribution"] = plot_spatial_map(data["window_events"], data["family_members"], data["repeat_pairs"], data["families"])
    figure_paths["spatial_zoom"] = plot_spatial_zoom(data["family_members"], data["repeat_pairs"], data["families"])
    figure_paths["waveform_comparison"], waveform_diag = plot_waveform_comparison(
        choose_representative_pairs(data["repeat_pairs"], data["families"]),
        data["station_cc"],
        data["observations"],
    )
    figure_paths["family_timeline"] = plot_family_timeline(data["family_members"], data["families"])
    figure_paths["correlation_statistics"] = plot_correlation_statistics(data["repeat_pairs"])
    figure_paths["repeat_statistics"] = plot_repeat_statistics(data["repeat_pairs"], data["families"])
    figure_paths["station_component_diagnostics"] = plot_station_diagnostics(data["station_cc"])

    sensitivity = build_threshold_sensitivity(data["candidate_pairs"], data["repeat_pairs"], data["families"])
    update_summary_json(data, figure_paths, waveform_diag, sensitivity)
    validate_outputs(figure_paths)
    log("Visualization outputs generated successfully.")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print(traceback.format_exc(), file=sys.stderr, flush=True)
        sys.exit(1)
