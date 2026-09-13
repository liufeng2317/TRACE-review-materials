from __future__ import annotations

import sys
import traceback
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde


DATA_DIR = Path(
    "<CASE_ROOT>/data"
)
OUTPUT_DIR = Path(
    "<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/03_regional_background_characterization"
)
CLEAN_DIR = Path(
    "<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/01_data_audit_cleaning"
)

CLEAN_CATALOG = CLEAN_DIR / "stage1_regional_catalog_clean.csv"
CLEAN_MECH = CLEAN_DIR / "source_mechanism_clean.csv"
CLEAN_STATIONS = CLEAN_DIR / "station_clean.csv"
CLEAN_MAIN = CLEAN_DIR / "main_earthquake_clean.csv"

EARTH_RADIUS_KM = 6371.0088
MAP_EXTENT_PAD_DEG = 0.35
MIN_MAGS_FOR_Mc = 30
DEFAULT_MAG_BIN = 0.1

plt.rcParams.update(
    {
        "figure.dpi": 160,
        "savefig.dpi": 300,
        "font.family": "DejaVu Sans",
        "font.size": 9,
        "axes.titlesize": 10,
        "axes.labelsize": 9,
        "xtick.labelsize": 8,
        "ytick.labelsize": 8,
        "legend.fontsize": 8,
        "axes.linewidth": 0.8,
        "xtick.direction": "in",
        "ytick.direction": "in",
        "xtick.top": True,
        "ytick.right": True,
    }
)


def ensure_output_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def haversine_km(lon1, lat1, lon2, lat2):
    lon1 = np.radians(lon1)
    lat1 = np.radians(lat1)
    lon2 = np.radians(lon2)
    lat2 = np.radians(lat2)
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = np.sin(dlat / 2.0) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2.0) ** 2
    return 2.0 * EARTH_RADIUS_KM * np.arcsin(np.sqrt(a))


def load_cleaned_tables() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    cat = pd.read_csv(CLEAN_CATALOG, parse_dates=["origin_time"])
    mech = pd.read_csv(CLEAN_MECH, parse_dates=["origin_time"])
    sta = pd.read_csv(CLEAN_STATIONS)
    main = pd.read_csv(CLEAN_MAIN, parse_dates=["origin_time"])
    return cat, mech, sta, main


def coerce_numeric(df: pd.DataFrame, cols: List[str]) -> pd.DataFrame:
    out = df.copy()
    for c in cols:
        if c in out.columns:
            out[c] = pd.to_numeric(out[c], errors="coerce")
    return out


def summarize_series(s: pd.Series) -> Dict[str, float]:
    s = pd.to_numeric(s, errors="coerce")
    return {
        "count": float(s.notna().sum()),
        "min": float(s.min()) if s.notna().any() else np.nan,
        "median": float(s.median()) if s.notna().any() else np.nan,
        "mean": float(s.mean()) if s.notna().any() else np.nan,
        "max": float(s.max()) if s.notna().any() else np.nan,
        "std": float(s.std(ddof=1)) if s.notna().sum() > 1 else np.nan,
    }


def estimate_mc_bvalue(magnitudes: pd.Series, mag_bin: float = DEFAULT_MAG_BIN) -> Dict[str, float]:
    mags = pd.to_numeric(magnitudes, errors="coerce").dropna().values
    mags = mags[np.isfinite(mags)]
    if len(mags) < MIN_MAGS_FOR_Mc:
        return {
            "mc": np.nan,
            "b_value": np.nan,
            "a_value": np.nan,
            "fit_n": float(len(mags)),
            "mag_bin": mag_bin,
            "fit_min_mag": np.nan,
            "fit_max_mag": np.nan,
            "method": 1.0,
        }

    min_mag = np.floor(mags.min() / mag_bin) * mag_bin
    max_mag = np.ceil(mags.max() / mag_bin) * mag_bin
    bins = np.arange(min_mag, max_mag + mag_bin, mag_bin)
    hist, edges = np.histogram(mags, bins=bins)
    cum = np.cumsum(hist[::-1])[::-1]
    centers = edges[:-1] + mag_bin / 2.0
    valid = cum > 0
    centers = centers[valid]
    cum = cum[valid]
    if len(centers) < 3:
        return {
            "mc": np.nan,
            "b_value": np.nan,
            "a_value": np.nan,
            "fit_n": float(len(mags)),
            "mag_bin": mag_bin,
            "fit_min_mag": np.nan,
            "fit_max_mag": np.nan,
            "method": 1.0,
        }

    mc_candidates = edges[:-1]
    best = None
    for mc in mc_candidates:
        tail = mags[mags >= mc]
        if len(tail) < 20:
            continue
        m_mean = tail.mean()
        b = np.log10(np.e) / (m_mean - (mc - mag_bin / 2.0)) if m_mean > (mc - mag_bin / 2.0) else np.nan
        if not np.isfinite(b) or b <= 0:
            continue
        pred = len(mags) * 10 ** (-b * (centers - mc))
        pred = np.maximum(pred, 1e-12)
        obs = cum.astype(float)
        mse = np.mean((np.log10(obs) - np.log10(pred)) ** 2)
        score = (mse, -len(tail))
        if best is None or score < best[0]:
            best = (score, mc, b, tail)

    if best is None:
        mc = float(np.nanmedian(mags))
        tail = mags[mags >= mc]
        if len(tail) < 2:
            return {
                "mc": np.nan,
                "b_value": np.nan,
                "a_value": np.nan,
                "fit_n": float(len(mags)),
                "mag_bin": mag_bin,
                "fit_min_mag": np.nan,
                "fit_max_mag": np.nan,
                "method": 1.0,
            }
        b = np.log10(np.e) / (tail.mean() - (mc - mag_bin / 2.0))
        a = np.log10(len(tail)) + b * mc
        return {
            "mc": float(mc),
            "b_value": float(b),
            "a_value": float(a),
            "fit_n": float(len(tail)),
            "mag_bin": mag_bin,
            "fit_min_mag": float(tail.min()),
            "fit_max_mag": float(tail.max()),
            "method": 1.0,
        }

    _, mc, b, tail = best
    a = np.log10(len(tail)) + b * mc
    return {
        "mc": float(mc),
        "b_value": float(b),
        "a_value": float(a),
        "fit_n": float(len(tail)),
        "mag_bin": mag_bin,
        "fit_min_mag": float(np.min(tail)),
        "fit_max_mag": float(np.max(tail)),
        "method": 1.0,
    }


def event_density_summary(cat: pd.DataFrame) -> Dict[str, float]:
    lat_span = cat["latitude"].max() - cat["latitude"].min()
    lon_span = cat["longitude"].max() - cat["longitude"].min()
    area = max(lat_span * lon_span * 111.0 * 111.0 * np.cos(np.deg2rad(cat["latitude"].median())), 1.0)
    return {
        "n_events": float(len(cat)),
        "area_km2_approx": float(area),
        "events_per_1000_km2": float(len(cat) / area * 1000.0),
        "lat_span_deg": float(lat_span),
        "lon_span_deg": float(lon_span),
    }


def station_coverage_metrics(cat: pd.DataFrame, sta: pd.DataFrame) -> Dict[str, float]:
    if len(sta) == 0 or len(cat) == 0:
        return {"station_count": float(len(sta)), "median_nearest_station_km": np.nan, "p90_nearest_station_km": np.nan}
    dist = []
    for _, ev in cat.sample(n=min(2000, len(cat)), random_state=42).iterrows():
        d = haversine_km(sta["longitude"].values, sta["latitude"].values, ev["longitude"], ev["latitude"])
        dist.append(np.min(d))
    dist = np.asarray(dist)
    return {
        "station_count": float(len(sta)),
        "median_nearest_station_km": float(np.median(dist)),
        "p90_nearest_station_km": float(np.quantile(dist, 0.9)),
        "mean_nearest_station_km": float(np.mean(dist)),
    }


def mechanism_availability(mech: pd.DataFrame) -> Dict[str, float]:
    core = (
        mech[[c for c in ["strike_plane1", "dip_plane1", "rake_plane1"] if c in mech.columns]].notna().all(axis=1)
        if {"strike_plane1", "dip_plane1", "rake_plane1"}.issubset(mech.columns)
        else pd.Series(False, index=mech.index)
    )
    geom = (
        mech[[c for c in ["P_axis_azimuth", "P_axis_dip", "T_axis_azimuth", "T_axis_dip", "N_axis_azimuth", "N_axis_dip"] if c in mech.columns]].notna().any(axis=1)
        if any(c in mech.columns for c in ["P_axis_azimuth", "P_axis_dip", "T_axis_azimuth", "T_axis_dip", "N_axis_azimuth", "N_axis_dip"])
        else pd.Series(False, index=mech.index)
    )
    return {
        "records": float(len(mech)),
        "origin_time_nonmissing": float(mech["origin_time"].notna().sum()) if "origin_time" in mech.columns else np.nan,
        "geometry_available": float(geom.sum()),
        "core_mechanism_available": float(core.sum()),
        "geometry_fraction": float(geom.mean()) if len(mech) else np.nan,
        "core_fraction": float(core.mean()) if len(mech) else np.nan,
    }


def depth_segmentation(cat: pd.DataFrame) -> pd.DataFrame:
    depths = pd.to_numeric(cat["depth_km"], errors="coerce").dropna()
    edges = np.unique(np.quantile(depths, [0, 0.25, 0.5, 0.75, 1.0]))
    if len(edges) < 5:
        edges = np.array([depths.min(), np.percentile(depths, 25), np.percentile(depths, 50), np.percentile(depths, 75), depths.max()])
    rows = []
    for lo, hi in zip(edges[:-1], edges[1:]):
        mask = (depths >= lo) & (depths <= hi)
        rows.append({"depth_min_km": float(lo), "depth_max_km": float(hi), "count": int(mask.sum())})
    return pd.DataFrame(rows)


def prepare_mechanism_subset(mech: pd.DataFrame, cat: pd.DataFrame) -> pd.DataFrame:
    if "origin_time" not in mech.columns or "origin_time" not in cat.columns:
        return mech.iloc[0:0].copy()
    cat_key = cat[["origin_time", "latitude", "longitude", "depth_km", "magnitude"]].copy()
    cat_key["time_key"] = pd.to_datetime(cat_key["origin_time"], errors="coerce").dt.tz_convert(None).dt.round("1s")
    mech_key = mech.copy()
    mech_key["time_key"] = pd.to_datetime(mech_key["origin_time"], errors="coerce", utc=True).dt.tz_convert(None).dt.round("1s")
    merged = mech_key.merge(cat_key, on="time_key", how="left", suffixes=("_mech", "_cat"))
    return merged


def plot_regional_map(cat: pd.DataFrame, main: pd.DataFrame, sta: pd.DataFrame, mech: pd.DataFrame, outpath: Path) -> None:
    fig, ax = plt.subplots(figsize=(7.2, 6.4))
    sc = ax.scatter(cat["longitude"], cat["latitude"], c=cat["depth_km"], s=4, cmap="viridis_r", alpha=0.35, linewidths=0, rasterized=True)
    ax.scatter(sta["longitude"], sta["latitude"], s=18, facecolors="none", edgecolors="#1f77b4", linewidths=0.8, label="Stations")
    ax.scatter(main["longitude"], main["latitude"], s=80, marker="*", c="#d62728", edgecolors="k", linewidths=0.5, label="Major earthquakes")
    if len(mech) > 0 and {"longitude", "latitude"}.issubset(mech.columns):
        mech_plot = mech.dropna(subset=["longitude", "latitude"])
        if len(mech_plot) > 0:
            ax.scatter(mech_plot["longitude"], mech_plot["latitude"], s=20, c="#ff7f0e", alpha=0.45, label="Mechanism records")
    ax.set_xlabel("Longitude (°E)")
    ax.set_ylabel("Latitude (°N)")
    ax.set_title("Regional seismicity and station context")
    cbar = fig.colorbar(sc, ax=ax, pad=0.02)
    cbar.set_label("Depth (km)")
    ax.legend(frameon=False, loc="best")
    ax.set_aspect("equal", adjustable="box")
    fig.tight_layout()
    fig.savefig(outpath, bbox_inches="tight")
    plt.close(fig)


def plot_time_magnitude(cat: pd.DataFrame, outpath: Path) -> None:
    fig, ax = plt.subplots(figsize=(7.0, 4.2))
    ax.scatter(cat["origin_time"], cat["magnitude"], s=4, alpha=0.25, c=cat["depth_km"], cmap="viridis_r", linewidths=0)
    ax.set_xlabel("Origin time")
    ax.set_ylabel("Magnitude")
    ax.set_title("Temporal evolution of magnitude")
    ax.grid(True, alpha=0.2)
    fig.tight_layout()
    fig.savefig(outpath, bbox_inches="tight")
    plt.close(fig)


def plot_depth_time(cat: pd.DataFrame, outpath: Path) -> None:
    fig, ax = plt.subplots(figsize=(7.0, 4.2))
    ax.scatter(cat["origin_time"], cat["depth_km"], s=4, alpha=0.25, c=cat["magnitude"], cmap="plasma", linewidths=0)
    ax.invert_yaxis()
    ax.set_xlabel("Origin time")
    ax.set_ylabel("Depth (km)")
    ax.set_title("Depth through time")
    ax.grid(True, alpha=0.2)
    fig.tight_layout()
    fig.savefig(outpath, bbox_inches="tight")
    plt.close(fig)


def plot_mag_depth(cat: pd.DataFrame, outpath: Path) -> None:
    fig, ax = plt.subplots(figsize=(5.8, 5.0))
    time_int = pd.to_datetime(cat["origin_time"], errors="coerce").view("int64")
    ax.scatter(cat["depth_km"], cat["magnitude"], s=4, alpha=0.25, c=time_int, cmap="viridis", linewidths=0)
    ax.set_xlabel("Depth (km)")
    ax.set_ylabel("Magnitude")
    ax.set_title("Magnitude–depth relation")
    ax.grid(True, alpha=0.2)
    fig.tight_layout()
    fig.savefig(outpath, bbox_inches="tight")
    plt.close(fig)


def plot_mfd_mc(cat: pd.DataFrame, mc_result: Dict[str, float], outpath: Path) -> None:
    mags = pd.to_numeric(cat["magnitude"], errors="coerce").dropna().values
    mag_bin = mc_result["mag_bin"]
    bins = np.arange(np.floor(mags.min() / mag_bin) * mag_bin, np.ceil(mags.max() / mag_bin) * mag_bin + mag_bin, mag_bin)
    hist, edges = np.histogram(mags, bins=bins)
    cum = np.cumsum(hist[::-1])[::-1]
    centers = edges[:-1] + mag_bin / 2.0
    fig, ax = plt.subplots(figsize=(6.6, 5.0))
    ax.bar(centers, hist, width=mag_bin * 0.9, color="#8da0cb", edgecolor="white", label="Frequency")
    ax2 = ax.twinx()
    ax2.plot(centers, cum, color="#e41a1c", lw=1.5, marker="o", ms=3, label="Cumulative")
    if np.isfinite(mc_result["mc"]):
        ax.axvline(mc_result["mc"], color="k", ls="--", lw=1.1, label=f"Mc = {mc_result['mc']:.2f}")
    ax.set_xlabel("Magnitude")
    ax.set_ylabel("Count per bin")
    ax2.set_ylabel("Cumulative count")
    ax.set_title("Frequency–magnitude distribution and preliminary completeness")
    ax.grid(True, alpha=0.2)
    lines, labels = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(lines + lines2, labels + labels2, frameon=False, loc="upper right")
    text = f"b = {mc_result['b_value']:.2f}\nfit n = {int(mc_result['fit_n'])}\nfit range = [{mc_result['fit_min_mag']:.2f}, {mc_result['fit_max_mag']:.2f}]"
    ax.text(0.03, 0.97, text, transform=ax.transAxes, va="top", ha="left", bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="0.8", alpha=0.85))
    fig.tight_layout()
    fig.savefig(outpath, bbox_inches="tight")
    plt.close(fig)


def plot_depth_hist(cat: pd.DataFrame, depth_bins: np.ndarray, outpath: Path) -> None:
    fig, ax = plt.subplots(figsize=(6.4, 4.6))
    ax.hist(cat["depth_km"], bins=depth_bins, color="#4daf4a", edgecolor="white", alpha=0.85)
    ax.set_xlabel("Depth (km)")
    ax.set_ylabel("Event count")
    ax.set_title("Depth distribution")
    ax.grid(True, alpha=0.2)
    fig.tight_layout()
    fig.savefig(outpath, bbox_inches="tight")
    plt.close(fig)


def plot_station_coverage(cat: pd.DataFrame, sta: pd.DataFrame, outpath: Path) -> None:
    sample = cat.sample(n=min(1800, len(cat)), random_state=7) if len(cat) > 1800 else cat
    nearest = []
    for _, ev in sample.iterrows():
        d = haversine_km(sta["longitude"].values, sta["latitude"].values, ev["longitude"], ev["latitude"])
        nearest.append(np.min(d))
    nearest = np.asarray(nearest)
    fig, ax = plt.subplots(figsize=(6.4, 4.6))
    ax.hist(nearest, bins=24, color="#377eb8", edgecolor="white", alpha=0.9)
    ax.set_xlabel("Nearest station distance (km)")
    ax.set_ylabel("Sampled event count")
    ax.set_title("Station coverage diagnostic")
    ax.grid(True, alpha=0.2)
    fig.tight_layout()
    fig.savefig(outpath, bbox_inches="tight")
    plt.close(fig)


def plot_density(cat: pd.DataFrame, outpath: Path) -> None:
    x = cat["longitude"].values
    y = cat["latitude"].values
    if len(cat) > 10:
        xy = np.vstack([x, y])
        z = gaussian_kde(xy)(xy)
    else:
        z = np.ones(len(cat))
    idx = np.argsort(z)
    fig, ax = plt.subplots(figsize=(7.2, 6.2))
    sc = ax.scatter(x[idx], y[idx], c=z[idx], s=4, cmap="magma", alpha=0.7, linewidths=0)
    ax.set_xlabel("Longitude (°E)")
    ax.set_ylabel("Latitude (°N)")
    ax.set_title("Spatial event-density diagnostic")
    fig.colorbar(sc, ax=ax, label="Relative density")
    ax.set_aspect("equal", adjustable="box")
    fig.tight_layout()
    fig.savefig(outpath, bbox_inches="tight")
    plt.close(fig)


def plot_mechanism_availability(mech: pd.DataFrame, outpath: Path) -> None:
    core = mech[[c for c in ["strike_plane1", "dip_plane1", "rake_plane1"] if c in mech.columns]].notna().all(axis=1) if {"strike_plane1", "dip_plane1", "rake_plane1"}.issubset(mech.columns) else pd.Series(False, index=mech.index)
    geom = mech[[c for c in ["P_axis_azimuth", "P_axis_dip", "T_axis_azimuth", "T_axis_dip", "N_axis_azimuth", "N_axis_dip"] if c in mech.columns]].notna().any(axis=1) if any(c in mech.columns for c in ["P_axis_azimuth", "P_axis_dip", "T_axis_azimuth", "T_axis_dip", "N_axis_azimuth", "N_axis_dip"]) else pd.Series(False, index=mech.index)
    categories = ["No geometry", "Geometry only", "Core mechanism"]
    counts = [int((~geom).sum()), int((geom & ~core).sum()), int(core.sum())]
    fig, ax = plt.subplots(figsize=(6.0, 4.2))
    ax.bar(categories, counts, color=["#d9d9d9", "#ffbf80", "#e34a33"])
    ax.set_ylabel("Record count")
    ax.set_title("Focal-mechanism availability")
    for i, v in enumerate(counts):
        ax.text(i, v + max(counts) * 0.02, str(v), ha="center", va="bottom")
    fig.tight_layout()
    fig.savefig(outpath, bbox_inches="tight")
    plt.close(fig)


def build_summary_table(cat: pd.DataFrame, mech: pd.DataFrame, sta: pd.DataFrame, mc_result: Dict[str, float]) -> pd.DataFrame:
    start = pd.to_datetime(cat["origin_time"], errors="coerce").min()
    end = pd.to_datetime(cat["origin_time"], errors="coerce").max()
    duration_years = max((end - start).total_seconds() / (365.25 * 24 * 3600), 1e-6)
    density = event_density_summary(cat)
    station_metrics = station_coverage_metrics(cat, sta)
    mech_metrics = mechanism_availability(mech)
    rows = [
        ("catalog_start", start),
        ("catalog_end", end),
        ("catalog_duration_years", duration_years),
        ("n_events", len(cat)),
        ("mean_events_per_year", len(cat) / duration_years),
        ("latitude_min", cat["latitude"].min()),
        ("latitude_max", cat["latitude"].max()),
        ("longitude_min", cat["longitude"].min()),
        ("longitude_max", cat["longitude"].max()),
        ("depth_min_km", cat["depth_km"].min()),
        ("depth_max_km", cat["depth_km"].max()),
        ("magnitude_min", cat["magnitude"].min()),
        ("magnitude_max", cat["magnitude"].max()),
        ("mean_depth_km", cat["depth_km"].mean()),
        ("median_depth_km", cat["depth_km"].median()),
        ("mean_magnitude", cat["magnitude"].mean()),
        ("median_magnitude", cat["magnitude"].median()),
        ("events_per_1000_km2", density["events_per_1000_km2"]),
        ("mc_preliminary", mc_result["mc"]),
        ("b_value_preliminary", mc_result["b_value"]),
        ("b_fit_n", mc_result["fit_n"]),
        ("b_fit_min_mag", mc_result["fit_min_mag"]),
        ("b_fit_max_mag", mc_result["fit_max_mag"]),
        ("station_count", station_metrics["station_count"]),
        ("median_nearest_station_km", station_metrics["median_nearest_station_km"]),
        ("p90_nearest_station_km", station_metrics["p90_nearest_station_km"]),
        ("mechanism_records", mech_metrics["records"]),
        ("mechanism_geometry_available", mech_metrics["geometry_available"]),
        ("mechanism_core_available", mech_metrics["core_mechanism_available"]),
        ("mechanism_geometry_fraction", mech_metrics["geometry_fraction"]),
        ("mechanism_core_fraction", mech_metrics["core_fraction"]),
    ]
    return pd.DataFrame(rows, columns=["metric", "value"])


def main() -> None:
    try:
        ensure_output_dir(OUTPUT_DIR)
        for p in OUTPUT_DIR.glob("*"):
            if p.is_file():
                p.unlink()

        cat, mech, sta, main = load_cleaned_tables()
        cat = coerce_numeric(cat, ["latitude", "longitude", "depth_km", "magnitude"])
        mech = coerce_numeric(mech, ["latitude", "longitude", "depth_km", "mag_1", "mag_2", "strike_plane1", "dip_plane1", "rake_plane1", "P_axis_azimuth", "P_axis_dip", "T_axis_azimuth", "T_axis_dip", "N_axis_azimuth", "N_axis_dip"])
        sta = coerce_numeric(sta, ["latitude", "longitude", "elevation_m"])
        main = coerce_numeric(main, ["latitude", "longitude", "depth_km", "magnitude"])

        cat = cat.dropna(subset=["origin_time", "latitude", "longitude", "depth_km", "magnitude"]).copy()
        mech = mech.copy()
        sta = sta.dropna(subset=["latitude", "longitude"]).copy()
        main = main.dropna(subset=["origin_time", "latitude", "longitude", "depth_km", "magnitude"]).copy()

        cat["origin_time"] = pd.to_datetime(cat["origin_time"], errors="coerce", utc=True)
        main["origin_time"] = pd.to_datetime(main["origin_time"], errors="coerce", utc=True)
        cat = cat.dropna(subset=["origin_time"]).copy()
        main = main.dropna(subset=["origin_time"]).copy()
        cat["origin_time_naive"] = cat["origin_time"].dt.tz_convert(None)
        main["origin_time_naive"] = main["origin_time"].dt.tz_convert(None)
        cat["year"] = cat["origin_time_naive"].dt.year
        cat["month"] = cat["origin_time_naive"].dt.to_period("M").astype(str)
        cat["day"] = cat["origin_time_naive"].dt.date

        mc_result = estimate_mc_bvalue(cat["magnitude"])
        depth_bins = np.unique(np.quantile(cat["depth_km"].dropna(), [0, 0.1, 0.25, 0.5, 0.75, 0.9, 1.0]))
        if len(depth_bins) < 4:
            depth_bins = np.linspace(cat["depth_km"].min(), cat["depth_km"].max(), 8)

        depth_seg = depth_segmentation(cat)
        station_metrics = station_coverage_metrics(cat, sta)
        mech_metrics = mechanism_availability(mech)
        summary = build_summary_table(cat, mech, sta, mc_result)
        mag_stats = pd.DataFrame([summarize_series(cat["magnitude"])], index=["magnitude"]).T.reset_index().rename(columns={"index": "stat"})
        depth_stats = pd.DataFrame([summarize_series(cat["depth_km"])], index=["depth_km"]).T.reset_index().rename(columns={"index": "stat"})

        temporal = cat.set_index("origin_time").resample("90D").size().reset_index(name="event_count")
        if len(temporal) == 0:
            temporal = pd.DataFrame(columns=["origin_time", "event_count"])
        spatial_extent = {
            "lat_min": float(cat["latitude"].min()),
            "lat_max": float(cat["latitude"].max()),
            "lon_min": float(cat["longitude"].min()),
            "lon_max": float(cat["longitude"].max()),
        }
        spatial_extent["lat_min"] -= MAP_EXTENT_PAD_DEG
        spatial_extent["lat_max"] += MAP_EXTENT_PAD_DEG
        spatial_extent["lon_min"] -= MAP_EXTENT_PAD_DEG
        spatial_extent["lon_max"] += MAP_EXTENT_PAD_DEG

        mech_subset = prepare_mechanism_subset(mech, cat)
        mech_avail = mech_subset["origin_time_mech"].notna().mean() if len(mech_subset) and "origin_time_mech" in mech_subset.columns else 0.0

        cat.to_csv(OUTPUT_DIR / "regional_catalog_background_clean.csv", index=False)
        mech.to_csv(OUTPUT_DIR / "mechanism_background_clean.csv", index=False)
        sta.to_csv(OUTPUT_DIR / "station_background_clean.csv", index=False)
        summary.to_csv(OUTPUT_DIR / "regional_background_summary.csv", index=False)
        depth_seg.to_csv(OUTPUT_DIR / "depth_segmentation_summary.csv", index=False)
        temporal.to_csv(OUTPUT_DIR / "temporal_activity_rate_90d.csv", index=False)
        pd.DataFrame([station_metrics]).to_csv(OUTPUT_DIR / "station_coverage_metrics.csv", index=False)
        pd.DataFrame([mech_metrics]).to_csv(OUTPUT_DIR / "mechanism_availability_metrics.csv", index=False)
        pd.DataFrame([mc_result]).to_csv(OUTPUT_DIR / "mc_bvalue_estimate.csv", index=False)
        mag_stats.to_csv(OUTPUT_DIR / "magnitude_summary_stats.csv", index=False)
        depth_stats.to_csv(OUTPUT_DIR / "depth_summary_stats.csv", index=False)
        mech_subset.to_csv(OUTPUT_DIR / "mechanism_subset_joined_to_catalog.csv", index=False)

        plot_regional_map(cat, main, sta, mech_subset, OUTPUT_DIR / "figure_regional_map.png")
        plot_time_magnitude(cat, OUTPUT_DIR / "figure_time_magnitude.png")
        plot_depth_time(cat, OUTPUT_DIR / "figure_depth_time.png")
        plot_mag_depth(cat, OUTPUT_DIR / "figure_magnitude_depth.png")
        plot_mfd_mc(cat, mc_result, OUTPUT_DIR / "figure_mfd_mc_bvalue.png")
        plot_density(cat, OUTPUT_DIR / "figure_spatial_density.png")
        plot_depth_hist(cat, depth_bins, OUTPUT_DIR / "figure_depth_distribution.png")
        plot_station_coverage(cat, sta, OUTPUT_DIR / "figure_station_coverage.png")
        plot_mechanism_availability(mech, OUTPUT_DIR / "figure_mechanism_availability.png")

        print("[03_regional_background_characterization] Completed successfully.", flush=True)
        print(f"[03_regional_background_characterization] Output directory: {OUTPUT_DIR}", flush=True)
        print(f"[03_regional_background_characterization] Events: {len(cat)}", flush=True)
        print(f"[03_regional_background_characterization] Stations: {len(sta)}", flush=True)
        print(f"[03_regional_background_characterization] Mechanism records: {len(mech)}", flush=True)
        print(f"[03_regional_background_characterization] Preliminary Mc: {mc_result['mc']:.3f}", flush=True)
        print(f"[03_regional_background_characterization] Preliminary b-value: {mc_result['b_value']:.3f}", flush=True)
        print(f"[03_regional_background_characterization] Mechanism availability (core): {mech_metrics['core_fraction']:.3f}", flush=True)
        print(f"[03_regional_background_characterization] Station median nearest distance (km): {station_metrics['median_nearest_station_km']:.2f}", flush=True)

    except Exception:
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
