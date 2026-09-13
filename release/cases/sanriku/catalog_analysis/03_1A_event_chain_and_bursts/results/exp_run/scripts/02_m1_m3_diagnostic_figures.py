from __future__ import annotations

import math
import sys
import traceback
from pathlib import Path
from typing import Dict, List, Tuple

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Circle, Polygon, Rectangle

BASE_DIR = Path("<CASE_ROOT>")
RUN_DIR = BASE_DIR / "run" / "03_1A_event_chain_and_bursts" / "exp_run"
INPUT_DIR = RUN_DIR / "outputs" / "01_m1_m3_event_chain_analysis"
OUTPUT_DIR = RUN_DIR / "outputs" / "02_m1_m3_diagnostic_figures"

EVENT_PATH = INPUT_DIR / "m1_m3_event_chain_table.csv"
REFERENCE_PATH = INPUT_DIR / "m1_m3_reference_table.csv"
COUNTS_PATH = INPUT_DIR / "m1_m3_window_summary_counts_rates.csv"
COMPOSITION_PATH = INPUT_DIR / "m1_m3_window_summary_composition.csv"
RAW_VS_M2_PATH = INPUT_DIR / "m1_m3_raw_vs_m2aware_summary.csv"
BURST_PATH = INPUT_DIR / "m1_m3_burst_table.csv"
MIGRATION_PATH = INPUT_DIR / "m1_m3_migration_endpoint_switching_summary.csv"

CORE_RADIUS_KM = 30.0
EXTENDED_RADIUS_KM = 60.0
PRIMARY_CORRIDOR_WIDTH_KM = 20.0
SENSITIVITY_CORRIDOR_WIDTH_KM = 30.0

PHASE_WINDOWS: List[Tuple[str, str]] = [
    ("pre_M1_baseline_14d", "Pre-M1 baseline\n(start to M1-14 d)"),
    ("M1_related_primary", "M1-related dominated\n(M1-14 d to M1+21 d)"),
    ("middle_primary", "Middle phase\n(M1+21 d to M3-35 d)"),
    ("pre_M3_primary", "Pre-M3 activation\n(M3-35 d to M3)"),
    ("post_M3_7d", "Post-M3 context\n(M3 to M3+7 d)"),
]
WINDOW_COLUMNS = [name for name, _ in PHASE_WINDOWS]
WINDOW_LABELS = {name: label for name, label in PHASE_WINDOWS}

CATEGORY_COLORS = {
    "M1-core": "#d73027",
    "M3-core": "#4575b4",
    "corridor_noncore": "#1a9850",
    "off-corridor_local": "#7b3294",
    "overlap_core": "#fdae61",
    "outside_local_union": "#bdbdbd",
}
CATEGORY_ORDER = ["M1-core", "M3-core", "corridor_noncore", "off-corridor_local", "overlap_core"]
THRESHOLD_MARKERS = {3.0: "o", 4.0: "^", 5.0: "s"}
PHASE_COLORS = {
    "pre_M1_baseline_14d": "#f0f0f0",
    "M1_related_primary": "#fee08b",
    "middle_primary": "#d9ef8b",
    "pre_M3_primary": "#91bfdb",
    "post_M3_7d": "#fdae61",
}


def log(message: str) -> None:
    print(message, flush=True)


def clean_output_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    for png in path.glob("*.png"):
        png.unlink()


def validate_columns(df: pd.DataFrame, required: List[str], name: str) -> None:
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"{name} missing required columns: {missing}")



def load_inputs() -> Dict[str, pd.DataFrame]:
    log(f"Loading analysis outputs from: {INPUT_DIR}")
    events = pd.read_csv(EVENT_PATH)
    refs = pd.read_csv(REFERENCE_PATH)
    counts = pd.read_csv(COUNTS_PATH)
    composition = pd.read_csv(COMPOSITION_PATH)
    raw_vs_m2 = pd.read_csv(RAW_VS_M2_PATH)
    migration = pd.read_csv(MIGRATION_PATH)
    bursts = pd.read_csv(BURST_PATH) if BURST_PATH.exists() and BURST_PATH.stat().st_size > 0 else pd.DataFrame()

    validate_columns(
        events,
        [
            "origin_time", "latitude", "longitude", "depth_km", "magnitude", "axis_length_km",
            "along_axis_km", "distance_to_M1_km", "distance_to_M3_km", "spatial_category",
            "in_local_union_60km", "M2_related_100km", "window__pre_M3_primary",
        ],
        "event_chain_table",
    )
    validate_columns(refs, ["label", "origin_time", "latitude", "longitude"], "reference_table")
    validate_columns(
        composition,
        [
            "window", "version", "fraction_M1-core", "fraction_M3-core",
            "fraction_corridor_noncore", "fraction_off-corridor_local",
        ],
        "composition_table",
    )
    validate_columns(
        migration,
        ["version", "phase", "slope_km_per_day", "time_along_axis_correlation"],
        "migration_table",
    )

    events["origin_time"] = pd.to_datetime(events["origin_time"], utc=True, format="ISO8601")
    refs["origin_time"] = pd.to_datetime(refs["origin_time"], utc=True, format="ISO8601")
    for df in [counts, composition]:
        for col in ["window_start", "window_end"]:
            df[col] = pd.to_datetime(df[col], utc=True, errors="coerce", format="ISO8601")
    if not bursts.empty:
        validate_columns(
            bursts,
            ["burst_id", "start_time", "end_time", "largest_magnitude", "dominant_spatial_category", "phase_class", "threshold_label"],
            "burst_table",
        )
        for col in ["start_time", "end_time"]:
            bursts[col] = pd.to_datetime(bursts[col], utc=True, format="ISO8601")

    return {
        "events": events,
        "refs": refs,
        "counts": counts,
        "composition": composition,
        "raw_vs_m2": raw_vs_m2,
        "migration": migration,
        "bursts": bursts,
    }


def build_reference_lookup(refs: pd.DataFrame) -> Dict[str, pd.Series]:
    return {row["label"]: row for _, row in refs.iterrows()}


def local_xy_km(lat, lon, ref_lat, ref_lon):
    lat = np.asarray(lat, dtype=float)
    lon = np.asarray(lon, dtype=float)
    x = (lon - ref_lon) * 111.32 * math.cos(math.radians(ref_lat))
    y = (lat - ref_lat) * 110.574
    return x, y


def parse_window_bounds(events: pd.DataFrame, refs_lookup: Dict[str, pd.Series]) -> Dict[str, Tuple[pd.Timestamp, pd.Timestamp]]:
    bounds: Dict[str, Tuple[pd.Timestamp, pd.Timestamp]] = {}
    min_time = events["origin_time"].min()
    max_time = events["origin_time"].max()
    m1 = refs_lookup["M1"]["origin_time"]
    m3 = refs_lookup["M3"]["origin_time"]
    bounds["pre_M1_baseline_14d"] = (min_time, m1 - pd.Timedelta(days=14))
    bounds["M1_related_primary"] = (m1 - pd.Timedelta(days=14), m1 + pd.Timedelta(days=21))
    bounds["middle_primary"] = (m1 + pd.Timedelta(days=21), m3 - pd.Timedelta(days=35))
    bounds["pre_M3_primary"] = (m3 - pd.Timedelta(days=35), m3)
    bounds["post_M3_7d"] = (m3, min(m3 + pd.Timedelta(days=7), max_time))
    return bounds


def add_time_helpers(events: pd.DataFrame, refs_lookup: Dict[str, pd.Series]) -> pd.DataFrame:
    events = events.copy()
    m1_time = refs_lookup["M1"]["origin_time"]
    events["days_relative_M1"] = (events["origin_time"] - m1_time) / pd.Timedelta(days=1)
    return events


def select_local_events(events: pd.DataFrame, magnitude_threshold: float = 3.0) -> pd.DataFrame:
    mask = events["in_local_union_60km"] & (events["magnitude"] >= magnitude_threshold)
    return events.loc[mask].copy()


def select_local_events_m2aware(events: pd.DataFrame, magnitude_threshold: float = 3.0) -> pd.DataFrame:
    mask = events["in_local_union_60km"] & (~events["M2_related_100km"]) & (events["magnitude"] >= magnitude_threshold)
    return events.loc[mask].copy()


def get_window_legend_handles() -> List[Rectangle]:
    handles = []
    for window_name, label in PHASE_WINDOWS:
        handles.append(Rectangle((0, 0), 1, 1, facecolor=PHASE_COLORS.get(window_name, "#efefef"), edgecolor="none", alpha=0.28, label=label.replace("\n", " ")))
    return handles



def style_time_axis(
    ax,
    refs_lookup: Dict[str, pd.Series],
    bounds: Dict[str, Tuple[pd.Timestamp, pd.Timestamp]],
    show_event_labels: bool = True,
    event_label_y: float = 0.985,
) -> None:
    for window_name, _ in PHASE_WINDOWS:
        start, end = bounds[window_name]
        if pd.notna(start) and pd.notna(end) and end > start:
            ax.axvspan(start, end, color=PHASE_COLORS.get(window_name, "#efefef"), alpha=0.28, lw=0)
    for label in ["M1", "M2", "M3"]:
        t = refs_lookup[label]["origin_time"]
        ax.axvline(t, color="black", lw=1.2, ls="--", alpha=0.9)
        if show_event_labels:
            ax.text(t, event_label_y, label, transform=ax.get_xaxis_transform(), ha="center", va="top", fontsize=8.5, fontweight="bold", bbox=dict(facecolor="white", edgecolor="none", alpha=0.75, pad=1.0))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1, tz=mdates.UTC))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m", tz=mdates.UTC))
    for tick in ax.get_xticklabels():
        tick.set_rotation(30)
        tick.set_ha("right")
    ax.grid(True, alpha=0.25)


def save_figure(fig: plt.Figure, filename: str) -> None:
    out = OUTPUT_DIR / filename
    fig.savefig(out, dpi=220, bbox_inches="tight")
    plt.close(fig)
    log(f"Saved figure: {out}")


def plot_map(events: pd.DataFrame, refs_lookup: Dict[str, pd.Series]) -> None:
    log("Creating M1-M3 map figure")
    local = select_local_events(events, 3.0)
    ref_lat = float((refs_lookup["M1"]["latitude"] + refs_lookup["M3"]["latitude"]) / 2.0)
    ref_lon = float((refs_lookup["M1"]["longitude"] + refs_lookup["M3"]["longitude"]) / 2.0)
    local["x_km"], local["y_km"] = local_xy_km(local["latitude"], local["longitude"], ref_lat, ref_lon)

    fig, ax = plt.subplots(figsize=(9.5, 8.5))
    tmin = local["origin_time"].min().value
    tmax = local["origin_time"].max().value

    sc = None
    for threshold in [3.0, 4.0, 5.0]:
        mag_low = threshold
        mag_high = np.inf if threshold == 5.0 else threshold + 1.0
        sub = local[(local["magnitude"] >= mag_low) & (local["magnitude"] < mag_high)]
        if sub.empty:
            continue
        sc = ax.scatter(
            sub["longitude"],
            sub["latitude"],
            c=sub["origin_time"].astype("int64"),
            cmap="turbo",
            vmin=tmin,
            vmax=tmax,
            s=14 + (sub["magnitude"] - 2.5).clip(lower=0) ** 2 * 9,
            marker=THRESHOLD_MARKERS[threshold],
            edgecolors=[CATEGORY_COLORS.get(cat, "#666666") for cat in sub["spatial_category"]],
            linewidths=0.5,
            alpha=0.85,
            label=f"M{int(threshold)}-{int(mag_high) - 1 if np.isfinite(mag_high) else '+'}",
        )

    for label in ["M1", "M2", "M3"]:
        row = refs_lookup[label]
        ax.scatter(row["longitude"], row["latitude"], marker="*", s=260, c="black", edgecolors="white", linewidths=0.8, zorder=5)
        ax.text(row["longitude"] + 0.02, row["latitude"] + 0.015, label, fontsize=10, fontweight="bold")

    m1 = refs_lookup["M1"]
    m3 = refs_lookup["M3"]
    ax.plot([m1["longitude"], m3["longitude"]], [m1["latitude"], m3["latitude"]], color="black", lw=1.5, ls="--", alpha=0.8)

    for label in ["M1", "M3"]:
        row = refs_lookup[label]
        for radius_km, ls, alpha in [(CORE_RADIUS_KM, "-", 0.8), (EXTENDED_RADIUS_KM, ":", 0.8)]:
            rdeg = radius_km / 111.0
            circ = Circle((row["longitude"], row["latitude"]), rdeg, fill=False, ec="#444444", ls=ls, lw=1.0, alpha=alpha)
            ax.add_patch(circ)

    axis_len = float(local["axis_length_km"].iloc[0])
    box_x0 = -EXTENDED_RADIUS_KM
    box_x1 = axis_len + EXTENDED_RADIUS_KM
    m1x, m1y = local_xy_km([m1["latitude"]], [m1["longitude"]], ref_lat, ref_lon)
    m3x, m3y = local_xy_km([m3["latitude"]], [m3["longitude"]], ref_lat, ref_lon)
    m1xy = np.array([float(m1x[0]), float(m1y[0])])
    axis_vec = np.array([float(m3x[0]) - float(m1x[0]), float(m3y[0]) - float(m1y[0])])
    axis_len_xy = float(np.hypot(axis_vec[0], axis_vec[1]))
    if axis_len_xy <= 0:
        raise ValueError("Invalid M1-M3 axis length for corridor polygon")
    axis_hat = axis_vec / axis_len_xy
    perp_hat = np.array([-axis_hat[1], axis_hat[0]])
    for width, color, alpha in [(SENSITIVITY_CORRIDOR_WIDTH_KM, "#74add1", 0.10), (PRIMARY_CORRIDOR_WIDTH_KM, "#4575b4", 0.16)]:
        corners = np.array([
            m1xy + axis_hat * box_x0 + perp_hat * width,
            m1xy + axis_hat * box_x1 + perp_hat * width,
            m1xy + axis_hat * box_x1 - perp_hat * width,
            m1xy + axis_hat * box_x0 - perp_hat * width,
        ])
        poly_lon = ref_lon + corners[:, 0] / (111.32 * math.cos(math.radians(ref_lat)))
        poly_lat = ref_lat + corners[:, 1] / 110.574
        ax.add_patch(Polygon(np.column_stack([poly_lon, poly_lat]), closed=True, facecolor=color, edgecolor="none", alpha=alpha, zorder=0))

    if sc is None:
        raise ValueError("No M3+ local events available for map colorbar")
    cbar = fig.colorbar(sc, ax=ax, fraction=0.035, pad=0.02)
    cbar.ax.set_ylabel("Origin time", rotation=90)
    ticks = np.linspace(tmin, tmax, 5)
    cbar.set_ticks(ticks)
    cbar.set_ticklabels([pd.to_datetime(int(t), utc=True).strftime("%Y-%m-%d") for t in ticks])

    cat_handles = [
        Line2D([0], [0], marker="o", color="none", markerfacecolor="white", markeredgecolor=CATEGORY_COLORS[c], markeredgewidth=1.2, label=c)
        for c in ["M1-core", "M3-core", "corridor_noncore", "off-corridor_local", "overlap_core"]
    ]
    mag_handles = [
        Line2D([0], [0], marker=THRESHOLD_MARKERS[3.0], color="#555555", linestyle="None", markersize=7, label="M3-M3.9"),
        Line2D([0], [0], marker=THRESHOLD_MARKERS[4.0], color="#555555", linestyle="None", markersize=7, label="M4-M4.9"),
        Line2D([0], [0], marker=THRESHOLD_MARKERS[5.0], color="#555555", linestyle="None", markersize=7, label="M5+"),
    ]
    leg1 = ax.legend(handles=mag_handles, loc="upper left", title="Magnitude")
    ax.add_artist(leg1)
    ax.legend(handles=cat_handles, loc="lower right", title="Spatial category")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_title("M1-M3 local union map: M3+/M4+/M5+ events colored by time")
    ax.grid(True, alpha=0.2)
    save_figure(fig, "fig_m1_m3_map_time_category.png")


def plot_magnitude_time(events: pd.DataFrame, refs_lookup: Dict[str, pd.Series], bounds: Dict[str, Tuple[pd.Timestamp, pd.Timestamp]]) -> None:
    log("Creating magnitude-time figure")
    local = events[events["in_local_union_60km"]].copy()
    fig, ax = plt.subplots(figsize=(12, 5.5))
    for cat in CATEGORY_ORDER:
        sub = local[local["spatial_category"] == cat]
        if sub.empty:
            continue
        ax.scatter(sub["origin_time"], sub["magnitude"], s=12 + (sub["magnitude"].clip(lower=0) ** 2), c=CATEGORY_COLORS[cat], alpha=0.7, label=cat, edgecolors="none")
    style_time_axis(ax, refs_lookup, bounds)
    for y in [3, 4, 5, 6]:
        ax.axhline(y, color="#777777", lw=0.8, ls=":")
        ax.text(0.995, y, f" M{y}+", transform=ax.get_yaxis_transform(), ha="right", va="bottom", fontsize=8, color="#555555")
    ax.set_ylabel("Magnitude")
    ax.set_xlabel("Origin time")
    ax.set_title("Magnitude-time evolution in the M1-M3 local union", pad=20)
    legend1 = ax.legend(ncol=5, fontsize=8, frameon=True, loc="upper center", bbox_to_anchor=(0.5, 1.20), title="Spatial category")
    ax.add_artist(legend1)
    ax.legend(handles=get_window_legend_handles(), ncol=3, fontsize=7.5, frameon=True, loc="upper left", bbox_to_anchor=(0.0, 1.18), title="Fixed windows")
    save_figure(fig, "fig_magnitude_time_windows.png")


def plot_projected_distance(events: pd.DataFrame, refs_lookup: Dict[str, pd.Series], bounds: Dict[str, Tuple[pd.Timestamp, pd.Timestamp]], migration: pd.DataFrame) -> None:
    log("Creating projected-distance-time figure")
    local = select_local_events(events, 3.0)
    local_m2 = select_local_events_m2aware(events, 3.0)
    fig, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=True, height_ratios=[2.1, 1.0])

    for ax, sub, title in [(axes[0], local, "Raw"), (axes[1], local_m2, "M2-aware")]:
        ax.scatter(sub["origin_time"], sub["along_axis_km"], c=[CATEGORY_COLORS.get(c, "#666") for c in sub["spatial_category"]], s=10 + (sub["magnitude"] - 2.5).clip(lower=0) ** 2 * 7, alpha=0.7, edgecolors="none")
        for label in ["M1", "M3"]:
            pos = 0.0 if label == "M1" else float(sub["axis_length_km"].iloc[0])
            ax.axhline(pos, color="#333333", lw=1.0, ls="--", alpha=0.7)
        style_time_axis(ax, refs_lookup, bounds)
        ax.set_ylabel("Along-axis km\nfrom M1")
        ax.set_title(f"{title}: along-axis position versus time")

    phase_lookup = migration.set_index(["version", "phase"])
    for version, ax in [("raw", axes[0]), ("m2aware", axes[1])]:
        for phase in ["M1_related_primary", "middle_primary", "pre_M3_primary", "full_M1_to_M3"]:
            key = (version, phase)
            if key not in phase_lookup.index:
                continue
            row = phase_lookup.loc[key]
            if isinstance(row, pd.DataFrame):
                row = row.iloc[0]
            text = f"{phase}: slope={row['slope_km_per_day']:.2f} km/d, r={row['time_along_axis_correlation']:.2f}"
            ax.text(0.01, 0.97 - 0.08 * ["full_M1_to_M3", "M1_related_primary", "middle_primary", "pre_M3_primary"].index(phase), text, transform=ax.transAxes, ha="left", va="top", fontsize=8, bbox=dict(facecolor="white", alpha=0.65, edgecolor="none"))

    axes[-1].set_xlabel("Origin time")
    save_figure(fig, "fig_projected_distance_time.png")


def plot_distance_to_endpoints(events: pd.DataFrame, refs_lookup: Dict[str, pd.Series], bounds: Dict[str, Tuple[pd.Timestamp, pd.Timestamp]]) -> None:
    log("Creating endpoint-distance-time figure")
    local = select_local_events(events, 3.0)
    fig, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    axes[0].scatter(local["origin_time"], local["distance_to_M1_km"], c="#d73027", s=12 + (local["magnitude"] - 2.5).clip(lower=0) ** 2 * 7, alpha=0.65, edgecolors="none")
    axes[1].scatter(local["origin_time"], local["distance_to_M3_km"], c="#4575b4", s=12 + (local["magnitude"] - 2.5).clip(lower=0) ** 2 * 7, alpha=0.65, edgecolors="none")
    for ax, dist_label in zip(axes, ["Distance to M1 (km)", "Distance to M3 (km)"]):
        style_time_axis(ax, refs_lookup, bounds)
        ax.axhline(CORE_RADIUS_KM, color="#333333", lw=1.0, ls="--")
        ax.axhline(EXTENDED_RADIUS_KM, color="#666666", lw=1.0, ls=":")
        ax.set_ylabel(dist_label)
    axes[0].set_title("Endpoint-centered behavior through time")
    axes[1].set_xlabel("Origin time")
    save_figure(fig, "fig_distance_to_M1_M3_time.png")


def build_cumulative_series(events: pd.DataFrame, threshold: float, m2aware: bool) -> pd.DataFrame:
    sub = events[events["in_local_union_60km"] & (events["magnitude"] >= threshold)].copy()
    if m2aware:
        sub = sub[~sub["M2_related_100km"]].copy()
    sub = sub.sort_values("origin_time")
    sub["cum_count"] = np.arange(1, len(sub) + 1)
    return sub


def plot_cumulative_counts(events: pd.DataFrame, refs_lookup: Dict[str, pd.Series], bounds: Dict[str, Tuple[pd.Timestamp, pd.Timestamp]]) -> None:
    log("Creating cumulative counts figure")
    fig, axes = plt.subplots(2, 1, figsize=(12, 8.4), sharex=True)
    for ax, threshold in zip(axes, [4.0, 5.0]):
        raw = build_cumulative_series(events, threshold, m2aware=False)
        m2 = build_cumulative_series(events, threshold, m2aware=True)
        raw_line = None
        m2_line = None
        if not raw.empty:
            raw_line = ax.step(raw["origin_time"], raw["cum_count"], where="post", color="#1b7837", lw=2.4, label="Raw")[0]
        if not m2.empty:
            m2_line = ax.step(m2["origin_time"], m2["cum_count"], where="post", color="#762a83", lw=2.0, ls="--", label="M2-aware")[0]
        if raw_line is not None and m2_line is not None and not raw.empty and not m2.empty:
            merged = pd.merge_asof(
                raw[["origin_time", "cum_count"]].sort_values("origin_time"),
                m2[["origin_time", "cum_count"]].sort_values("origin_time"),
                on="origin_time",
                direction="nearest",
                suffixes=("_raw", "_m2"),
            )
            diff = merged["cum_count_raw"] - merged["cum_count_m2"]
            if (diff > 0).any():
                ax.fill_between(merged["origin_time"], merged["cum_count_m2"], merged["cum_count_raw"], where=diff > 0, color="#dd3497", alpha=0.18, step="post", label="Raw - M2-aware difference")
        style_time_axis(ax, refs_lookup, bounds, show_event_labels=False)
        ax.set_ylabel(f"Cumulative M{int(threshold)}+ count")
        ax.text(0.01, 0.98, f"M{int(threshold)}+", transform=ax.transAxes, ha="left", va="top", fontsize=9, fontweight="bold", bbox=dict(facecolor="white", edgecolor="none", alpha=0.8, pad=1.0))
        ax.legend(loc="upper left", ncol=3, fontsize=8)
    axes[0].set_title("Cumulative large-event counts: raw versus M2-aware", pad=20)
    axes[0].text(0.995, 1.07, "Background colors = fixed windows", transform=axes[0].transAxes, ha="right", va="bottom", fontsize=8, color="#444444")
    axes[1].set_xlabel("Origin time")
    save_figure(fig, "fig_cumulative_counts_raw_vs_M2aware.png")


def plot_burst_timeline(events: pd.DataFrame, refs_lookup: Dict[str, pd.Series], bounds: Dict[str, Tuple[pd.Timestamp, pd.Timestamp]], bursts: pd.DataFrame) -> None:
    log("Creating burst timeline figure")
    local = select_local_events(events, 3.0)
    fig, ax = plt.subplots(figsize=(14, 6.8))
    daily = local.set_index("origin_time").resample("1D").size()
    rolling = daily.rolling(7, center=True, min_periods=1).mean()
    ax.bar(daily.index, daily.values, width=0.9, color="#a6bddb", alpha=0.7, label="Daily M3+ local count")
    ax.plot(rolling.index, rolling.values, color="#045a8d", lw=2.0, label="7-day rolling mean")
    style_time_axis(ax, refs_lookup, bounds, show_event_labels=False)
    if not bursts.empty:
        ymax = max(float(daily.max()) if len(daily) else 1.0, 1.0)
        ax.set_ylim(0, ymax * 1.55)
        band_base = ymax * 1.02
        band_height = ymax * 0.08
        text_levels = [ymax * 1.14, ymax * 1.26, ymax * 1.38]
        color_map = {
            "M1-related dominated phase": "#f46d43",
            "intermediate M1-M3 activity": "#66bd63",
            "pre-M3 local activation": "#3288bd",
            "post-M3 context": "#fdae61",
        }
        burst_rows = bursts.sort_values(["start_time", "threshold"]).reset_index(drop=True)
        prev_text_time = [None] * len(text_levels)
        min_sep = pd.Timedelta(days=18)
        for i, (_, row) in enumerate(burst_rows.iterrows()):
            color = color_map.get(row["phase_class"], "#999999")
            x0 = mdates.date2num(row["start_time"])
            x1 = mdates.date2num(row["end_time"])
            width = max(x1 - x0, 0.8)
            ax.add_patch(Rectangle((x0, band_base), width, band_height, color=color, alpha=0.8, zorder=4))
            mid = row["start_time"] + (row["end_time"] - row["start_time"]) / 2
            available_rows = [k for k, tprev in enumerate(prev_text_time) if tprev is None or (mid - tprev) >= min_sep]
            if available_rows:
                row_idx = available_rows[0]
            else:
                row_idx = i % len(text_levels)
            prev_text_time[row_idx] = mid
            label = f"{row['burst_id']} | {row['threshold_label']} | max {row['largest_magnitude']:.1f}\n{row['dominant_spatial_category']}"
            ax.annotate(
                label,
                xy=(mid, band_base + band_height * 0.55),
                xytext=(mid, text_levels[row_idx]),
                textcoords="data",
                ha="center",
                va="bottom",
                fontsize=6.8 if len(burst_rows) > 10 else 7.2,
                bbox=dict(facecolor="white", edgecolor="none", alpha=0.8, pad=1.2),
                arrowprops=dict(arrowstyle="-", color="#666666", lw=0.6, alpha=0.8),
                zorder=5,
            )
        phase_handles = [Rectangle((0, 0), 1, 1, facecolor=color, edgecolor="none", alpha=0.8, label=label) for label, color in color_map.items()]
        legend_main = ax.legend(loc="upper left", fontsize=8)
        ax.add_artist(legend_main)
        ax.legend(handles=phase_handles, loc="upper left", bbox_to_anchor=(0.17, 1.0), fontsize=7.5, title="Burst phase class")
    ax.set_ylabel("M3+ count per day")
    ax.set_xlabel("Origin time")
    ax.set_title("Burst timeline summary with fixed windows", pad=22)
    ax.text(0.995, 1.03, "Top bars/labels summarize detected bursts", transform=ax.transAxes, ha="right", va="bottom", fontsize=8, color="#444444")
    save_figure(fig, "fig_burst_timeline_summary.png")


def plot_pre_m3_activation(events: pd.DataFrame, refs_lookup: Dict[str, pd.Series], bounds: Dict[str, Tuple[pd.Timestamp, pd.Timestamp]]) -> None:
    log("Creating pre-M3 activation figure")
    mask = events["window__pre_M3_primary"] & events["in_local_union_60km"] & (events["magnitude"] >= 3.0)
    raw = events.loc[mask].copy()
    m2 = raw.loc[~raw["M2_related_100km"]].copy()
    fig, axes = plt.subplots(1, 2, figsize=(13.5, 5.4), sharey=True)
    panel_specs = [
        (axes[0], raw, "Raw", "All local pre-M3 events retained", "#f7f7f7"),
        (axes[1], m2, "M2-aware", "M2-related local events excluded", "#fcf3ff"),
    ]
    for ax, sub, title, subtitle, facecolor in panel_specs:
        ax.set_facecolor(facecolor)
        for cat in ["M1-core", "M3-core", "corridor_noncore", "off-corridor_local", "overlap_core"]:
            d = sub[sub["spatial_category"] == cat]
            if d.empty:
                continue
            ax.scatter(d["origin_time"], d["along_axis_km"], c=CATEGORY_COLORS[cat], s=20 + (d["magnitude"] - 2.5).clip(lower=0) ** 2 * 10, alpha=0.75, edgecolors="none", label=cat)
        style_time_axis(ax, refs_lookup, bounds, show_event_labels=False)
        ax.set_title(title, pad=14)
        ax.text(0.01, 0.98, subtitle, transform=ax.transAxes, ha="left", va="top", fontsize=8, color="#444444", bbox=dict(facecolor="white", edgecolor="none", alpha=0.75, pad=1.0))
        ax.set_xlabel("Origin time")
        ax.set_ylabel("Along-axis km from M1")
    fig.suptitle("Pre-M3 local activation: raw versus M2-aware", y=0.98)
    axes[1].legend(loc="upper left", fontsize=8)
    save_figure(fig, "fig_preM3_activation_raw_vs_M2aware.png")


def plot_window_composition(composition: pd.DataFrame) -> None:
    log("Creating window composition figure")
    use = composition[composition["window"].isin(WINDOW_COLUMNS)].copy()
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.4), sharey=True)
    plot_cols = ["fraction_M1-core", "fraction_M3-core", "fraction_corridor_noncore", "fraction_off-corridor_local"]
    plot_labels = ["M1-core", "M3-core", "corridor_noncore", "off-corridor_local"]
    for ax, version, title in [(axes[0], "raw", "Raw"), (axes[1], "m2aware", "M2-aware")]:
        sub = use[use["version"] == version].copy()
        sub["window"] = pd.Categorical(sub["window"], categories=WINDOW_COLUMNS, ordered=True)
        sub = sub.sort_values("window")
        bottom = np.zeros(len(sub))
        x = np.arange(len(sub))
        for col, label in zip(plot_cols, plot_labels):
            vals = sub[col].fillna(0).to_numpy()
            ax.bar(x, vals, bottom=bottom, color=CATEGORY_COLORS[label], label=label)
            bottom += vals
        short_labels = {
            "pre_M1_baseline_14d": "Pre-M1\nbaseline",
            "M1_related_primary": "M1-related",
            "middle_primary": "Middle",
            "pre_M3_primary": "Pre-M3",
            "post_M3_7d": "Post-M3",
        }
        ax.set_xticks(x)
        ax.set_xticklabels([short_labels[w] for w in sub["window"]], rotation=0, ha="center")
        ax.set_ylim(0, 1.0)
        ax.set_ylabel("Fraction of local events")
        ax.set_title(title)
        ax.grid(True, axis="y", alpha=0.25)
    axes[1].legend(loc="upper left", bbox_to_anchor=(1.02, 1.0))
    fig.suptitle("Window-separated endpoint/corridor composition")
    fig.text(0.5, 0.02, "Background-color windows in other panels correspond to these same fixed phases.", ha="center", va="bottom", fontsize=8, color="#444444")
    save_figure(fig, "fig_window_composition_raw_vs_M2aware.png")


def main() -> None:
    log(f"Output directory: {OUTPUT_DIR}")
    clean_output_dir(OUTPUT_DIR)
    data = load_inputs()
    refs_lookup = build_reference_lookup(data["refs"])
    bounds = parse_window_bounds(data["events"], refs_lookup)
    events = add_time_helpers(data["events"], refs_lookup)

    plt.style.use("seaborn-v0_8-whitegrid")
    plt.rcParams.update({
        "font.size": 10,
        "axes.titlesize": 12,
        "axes.labelsize": 10,
        "legend.fontsize": 8,
        "figure.titlesize": 13,
    })

    plot_map(events, refs_lookup)
    plot_magnitude_time(events, refs_lookup, bounds)
    plot_projected_distance(events, refs_lookup, bounds, data["migration"])
    plot_distance_to_endpoints(events, refs_lookup, bounds)
    plot_cumulative_counts(events, refs_lookup, bounds)
    plot_burst_timeline(events, refs_lookup, bounds, data["bursts"])
    plot_pre_m3_activation(events, refs_lookup, bounds)
    plot_window_composition(data["composition"])
    log("All diagnostic figures completed successfully.")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print(traceback.format_exc(), flush=True)
        sys.exit(1)
