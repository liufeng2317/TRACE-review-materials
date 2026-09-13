from __future__ import annotations

import sys
import traceback
from pathlib import Path
from typing import Dict, List, Tuple

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
    "<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/05_diagnostic_figures"
)
STAGE1_DIR = Path(
    "<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/01_data_audit_cleaning"
)
MATCH_DIR = Path(
    "<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/02_major_earthquake_matching"
)
REGIONAL_SUMMARY_DIR = Path(
    "<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/03_regional_background_characterization"
)
CONTEXT_DIR = Path(
    "<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/04_mainshock_regional_context"
)

CLEAN_CATALOG = STAGE1_DIR / "stage1_regional_catalog_clean.csv"
CLEAN_MAIN = STAGE1_DIR / "main_earthquake_clean.csv"
CLEAN_MECH = STAGE1_DIR / "source_mechanism_clean.csv"
CLEAN_STATIONS = STAGE1_DIR / "station_clean.csv"
MATCH_TABLE = MATCH_DIR / "major_earthquake_matches.csv"
CONTEXT_TABLE = CONTEXT_DIR / "mainshock_context_summary.csv"

EARTH_RADIUS_KM = 6371.0088
plt.rcParams.update(
    {
        "figure.dpi": 160,
        "savefig.dpi": 400,
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


def log(msg: str) -> None:
    print(msg, flush=True)


def haversine_km(lon1, lat1, lon2, lat2):
    lon1 = np.radians(lon1)
    lat1 = np.radians(lat1)
    lon2 = np.radians(lon2)
    lat2 = np.radians(lat2)
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = np.sin(dlat / 2.0) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2.0) ** 2
    return 2.0 * EARTH_RADIUS_KM * np.arcsin(np.sqrt(a))


def load_tables() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    cat = pd.read_csv(CLEAN_CATALOG, parse_dates=["origin_time"])
    main = pd.read_csv(CLEAN_MAIN, parse_dates=["origin_time"])
    mech = pd.read_csv(CLEAN_MECH, parse_dates=["origin_time"], low_memory=False)
    sta = pd.read_csv(CLEAN_STATIONS)
    match = pd.read_csv(MATCH_TABLE, parse_dates=["origin_time", "matched_time"])
    return cat, main, mech, sta, match, add_mechanism_flags(mech)


def coerce_numeric(df: pd.DataFrame, cols: List[str]) -> pd.DataFrame:
    out = df.copy()
    for c in cols:
        if c in out.columns:
            out[c] = pd.to_numeric(out[c], errors="coerce")
    return out


def add_mechanism_flags(mech: pd.DataFrame) -> pd.DataFrame:
    out = mech.copy()
    geom_cols = [c for c in ["P_axis_azimuth", "P_axis_dip", "T_axis_azimuth", "T_axis_dip", "N_axis_azimuth", "N_axis_dip"] if c in out.columns]
    core_cols = [c for c in ["strike_plane1", "dip_plane1", "rake_plane1"] if c in out.columns]
    out["has_geometry"] = out[geom_cols].notna().any(axis=1) if geom_cols else False
    out["has_mechanism_core"] = out[core_cols].notna().all(axis=1) if len(core_cols) == 3 else False
    return out


def savefig(fig: plt.Figure, path: Path) -> None:
    fig.tight_layout()
    fig.savefig(path, dpi=400, bbox_inches="tight")
    plt.close(fig)


def region_extent(cat: pd.DataFrame, pad: float = 0.25) -> Tuple[float, float, float, float]:
    return (
        float(cat["longitude"].min() - pad),
        float(cat["longitude"].max() + pad),
        float(cat["latitude"].min() - pad),
        float(cat["latitude"].max() + pad),
    )


def plot_regional_map(cat: pd.DataFrame, main: pd.DataFrame, sta: pd.DataFrame, mech: pd.DataFrame, outpath: Path) -> None:
    fig, ax = plt.subplots(figsize=(7.8, 6.8))
    extent = region_extent(cat, pad=0.3)
    sc = ax.scatter(cat["longitude"], cat["latitude"], c=cat["depth_km"], s=4, alpha=0.18, cmap="viridis_r", linewidths=0, rasterized=True)
    ax.scatter(sta["longitude"], sta["latitude"], s=18, facecolors="none", edgecolors="#1f77b4", linewidths=0.8, label="Stations")
    if len(mech) and {"longitude", "latitude"}.issubset(mech.columns):
        mech_geom = mech.dropna(subset=["longitude", "latitude"])
        if len(mech_geom):
            mech_geom = add_mechanism_flags(mech_geom)
            m = mech_geom[mech_geom["has_mechanism_core"]].copy() if "has_mechanism_core" in mech_geom.columns else mech_geom
            ax.scatter(m["longitude"], m["latitude"], s=18, c="#ff7f0e", alpha=0.35, label="Focal mechanisms")
    ax.scatter(main["longitude"], main["latitude"], s=130, marker="*", c="#d62728", edgecolors="k", linewidths=0.6, label="Major earthquakes")
    ax.set_xlim(extent[0], extent[1])
    ax.set_ylim(extent[2], extent[3])
    ax.set_xlabel("Longitude (°E)")
    ax.set_ylabel("Latitude (°N)")
    ax.set_title("Aomori/Japan regional seismicity map")
    fig.colorbar(sc, ax=ax, pad=0.02, label="Depth (km)")
    ax.legend(frameon=False, loc="best")
    ax.set_aspect("equal", adjustable="box")
    savefig(fig, outpath)


def plot_time_magnitude(cat: pd.DataFrame, main: pd.DataFrame, outpath: Path) -> None:
    fig, ax = plt.subplots(figsize=(8.0, 4.8))
    cat_time = pd.to_datetime(cat["origin_time"], utc=True, errors="coerce")
    main_time = pd.to_datetime(main["origin_time"], utc=True, errors="coerce")
    ax.scatter(cat_time.dt.tz_convert(None), cat["magnitude"], s=4, alpha=0.18, c="#4c72b0", linewidths=0, rasterized=True, label="Regional catalog")
    ax.scatter(main_time.dt.tz_convert(None), main["magnitude"], s=130, marker="*", c="#d62728", edgecolors="k", linewidths=0.6, label="Major earthquakes")
    ax.set_xlabel("Origin time")
    ax.set_ylabel("Magnitude")
    ax.set_title("Temporal activity and magnitude evolution")
    ax.legend(frameon=False)
    savefig(fig, outpath)


def plot_depth_time(cat: pd.DataFrame, main: pd.DataFrame, outpath: Path) -> None:
    fig, ax = plt.subplots(figsize=(8.0, 4.8))
    cat_time = pd.to_datetime(cat["origin_time"], utc=True, errors="coerce")
    main_time = pd.to_datetime(main["origin_time"], utc=True, errors="coerce")
    ax.scatter(cat_time.dt.tz_convert(None), cat["depth_km"], s=4, alpha=0.18, c="#55a868", linewidths=0, rasterized=True, label="Regional catalog")
    ax.scatter(main_time.dt.tz_convert(None), main["depth_km"], s=130, marker="*", c="#d62728", edgecolors="k", linewidths=0.6, label="Major earthquakes")
    ax.invert_yaxis()
    ax.set_xlabel("Origin time")
    ax.set_ylabel("Depth (km)")
    ax.set_title("Depth evolution through time")
    ax.legend(frameon=False)
    savefig(fig, outpath)


def plot_magnitude_depth(cat: pd.DataFrame, main: pd.DataFrame, outpath: Path) -> None:
    fig, ax = plt.subplots(figsize=(7.2, 5.6))
    time_vals = pd.to_datetime(cat["origin_time"], utc=True, errors="coerce").astype("int64") / 1e18
    sc = ax.scatter(cat["magnitude"], cat["depth_km"], c=time_vals, s=8, alpha=0.3, cmap="magma", linewidths=0, rasterized=True)
    ax.scatter(main["magnitude"], main["depth_km"], s=130, marker="*", c="#d62728", edgecolors="k", linewidths=0.6, label="Major earthquakes")
    ax.invert_yaxis()
    ax.set_xlabel("Magnitude")
    ax.set_ylabel("Depth (km)")
    ax.set_title("Magnitude–depth relationship")
    fig.colorbar(sc, ax=ax, pad=0.02, label="Relative time")
    ax.legend(frameon=False)
    savefig(fig, outpath)


def plot_frequency_magnitude(cat: pd.DataFrame, bval: pd.DataFrame, outpath: Path) -> None:
    fig, ax = plt.subplots(figsize=(7.2, 5.6))
    mags = pd.to_numeric(cat["magnitude"], errors="coerce").dropna().values
    bin_w = 0.1
    bins = np.arange(np.floor(mags.min() / bin_w) * bin_w, np.ceil(mags.max() / bin_w) * bin_w + bin_w, bin_w)
    hist, edges = np.histogram(mags, bins=bins)
    centers = edges[:-1] + bin_w / 2.0
    cum = np.cumsum(hist[::-1])[::-1]
    ax.bar(centers, hist, width=bin_w * 0.9, color="#4c72b0", alpha=0.55, label="Frequency")
    ax2 = ax.twinx()
    ax2.plot(centers, cum, color="#d62728", lw=1.8, label="Cumulative")
    mc = float(bval["mc"].iloc[0]) if len(bval) and pd.notna(bval["mc"].iloc[0]) else np.nan
    b = float(bval["b_value"].iloc[0]) if len(bval) and pd.notna(bval["b_value"].iloc[0]) else np.nan
    if np.isfinite(mc):
        ax.axvline(mc, color="k", ls="--", lw=1.1, label=f"Mc = {mc:.2f}")
    ax.set_xlabel("Magnitude")
    ax.set_ylabel("Event count per 0.1 mag")
    ax2.set_ylabel("Cumulative count")
    ax.set_title("Magnitude–frequency distribution and preliminary completeness")
    handles1, labels1 = ax.get_legend_handles_labels()
    handles2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(handles1 + handles2, labels1 + labels2, frameon=False, loc="upper right")
    txt = f"b ≈ {b:.2f}" if np.isfinite(b) else "b not estimated"
    ax.text(0.03, 0.96, txt, transform=ax.transAxes, va="top", ha="left", fontsize=8, bbox=dict(facecolor="white", edgecolor="none", alpha=0.75))
    savefig(fig, outpath)


def plot_depth_distribution(cat: pd.DataFrame, depth_seg: pd.DataFrame, outpath: Path) -> None:
    fig, ax = plt.subplots(figsize=(7.0, 5.0))
    depths = pd.to_numeric(cat["depth_km"], errors="coerce").dropna().values
    ax.hist(depths, bins=30, color="#55a868", alpha=0.7, edgecolor="white")
    for _, row in depth_seg.iterrows():
        ax.axvspan(row["depth_min_km"], row["depth_max_km"], color="#c7e9c0", alpha=0.2)
    ax.set_xlabel("Depth (km)")
    ax.set_ylabel("Count")
    ax.set_title("Depth distribution and empirical segmentation")
    savefig(fig, outpath)


def plot_spatial_density(cat: pd.DataFrame, outpath: Path) -> None:
    fig, ax = plt.subplots(figsize=(7.6, 6.6))
    x = cat["longitude"].to_numpy()
    y = cat["latitude"].to_numpy()
    if len(cat) >= 20:
        xy = np.vstack([x, y])
        kde = gaussian_kde(xy, bw_method="scott")
        dens = kde(xy)
        order = np.argsort(dens)
        sc = ax.scatter(x[order], y[order], c=dens[order], s=6, cmap="viridis", linewidths=0, rasterized=True)
        fig.colorbar(sc, ax=ax, pad=0.02, label="Relative density")
    else:
        ax.scatter(x, y, s=6, alpha=0.5, c="#4c72b0", linewidths=0)
    ax.set_xlabel("Longitude (°E)")
    ax.set_ylabel("Latitude (°N)")
    ax.set_title("Spatial event-density diagnostic")
    ax.set_aspect("equal", adjustable="box")
    savefig(fig, outpath)


def plot_cross_section(cat: pd.DataFrame, outpath: Path) -> None:
    fig, ax = plt.subplots(figsize=(7.8, 5.2))
    lon0 = cat["longitude"].median()
    lat0 = cat["latitude"].median()
    az = np.deg2rad(35.0)
    dx = (cat["longitude"].to_numpy() - lon0) * 111.0 * np.cos(np.deg2rad(lat0))
    dy = (cat["latitude"].to_numpy() - lat0) * 111.0
    dist = dx * np.cos(az) + dy * np.sin(az)
    ax.scatter(dist, cat["depth_km"], s=4, alpha=0.18, c="#4c72b0", linewidths=0, rasterized=True)
    ax.invert_yaxis()
    ax.set_xlabel("Along-profile distance (km)")
    ax.set_ylabel("Depth (km)")
    ax.set_title("Depth cross-section diagnostic")
    savefig(fig, outpath)


def plot_station_coverage(cat: pd.DataFrame, sta: pd.DataFrame, outpath: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.8))
    ax = axes[0]
    ax.scatter(cat["longitude"], cat["latitude"], s=3, alpha=0.12, c="#4c72b0", linewidths=0, rasterized=True)
    ax.scatter(sta["longitude"], sta["latitude"], s=18, facecolors="none", edgecolors="#d62728", linewidths=0.8, label="Stations")
    ax.set_xlabel("Longitude (°E)")
    ax.set_ylabel("Latitude (°N)")
    ax.set_title("Station and catalog geometry")
    ax.legend(frameon=False)
    ax.set_aspect("equal", adjustable="box")

    ax = axes[1]
    sample = cat.sample(n=min(2000, len(cat)), random_state=42) if len(cat) > 0 else cat
    nearest = []
    for _, ev in sample.iterrows():
        d = haversine_km(sta["longitude"].values, sta["latitude"].values, ev["longitude"], ev["latitude"])
        nearest.append(np.min(d))
    nearest = np.asarray(nearest) if len(nearest) else np.array([])
    ax.hist(nearest, bins=25, color="#55a868", alpha=0.75, edgecolor="white")
    ax.set_xlabel("Nearest-station distance (km)")
    ax.set_ylabel("Sample count")
    ax.set_title("Event-to-station proximity")
    savefig(fig, outpath)


def mechanism_subset(mech: pd.DataFrame) -> pd.DataFrame:
    out = mech.copy()
    geom_cols = [c for c in ["P_axis_azimuth", "P_axis_dip", "T_axis_azimuth", "T_axis_dip", "N_axis_azimuth", "N_axis_dip"] if c in out.columns]
    core_cols = [c for c in ["strike_plane1", "dip_plane1", "rake_plane1"] if c in out.columns]
    out["has_geometry"] = out[geom_cols].notna().any(axis=1) if geom_cols else False
    out["has_core"] = out[core_cols].notna().all(axis=1) if len(core_cols) == 3 else False
    return out[(out["has_geometry"] | out["has_core"]) & out["longitude"].notna() & out["latitude"].notna()]


def plot_mechanism_diagnostics(mech: pd.DataFrame, main: pd.DataFrame, outpath: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(11.0, 4.8))
    m = mechanism_subset(mech)
    ax = axes[0]
    if len(m):
        ax.scatter(m["longitude"], m["latitude"], s=14, c=m["depth_km"] if "depth_km" in m.columns else "#ff7f0e", cmap="viridis_r", alpha=0.5, linewidths=0, rasterized=True)
    ax.scatter(main["longitude"], main["latitude"], s=120, marker="*", c="#d62728", edgecolors="k", linewidths=0.6)
    ax.set_xlabel("Longitude (°E)")
    ax.set_ylabel("Latitude (°N)")
    ax.set_title("Focal-mechanism availability")
    ax.set_aspect("equal", adjustable="box")

    ax = axes[1]
    if len(m) and "strike_plane1" in m.columns:
        vals = pd.to_numeric(m["strike_plane1"], errors="coerce").dropna().values
        if len(vals):
            ax.hist(vals, bins=np.arange(0, 361, 20), color="#ff7f0e", alpha=0.75, edgecolor="white")
    ax.set_xlabel("Strike plane 1 (°)")
    ax.set_ylabel("Count")
    ax.set_title("Mechanism geometry distribution")
    savefig(fig, outpath)


def plot_context_overview(context: pd.DataFrame, outpath: Path) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(10.2, 7.8))
    axs = axes.ravel()
    metrics = ["local_event_count", "density_ratio_to_regional_median", "station_count_local", "mechanism_local_records"]
    titles = ["Local event count", "Density ratio", "Nearby stations", "Nearby mechanisms"]
    colors = ["#4c72b0", "#dd8452", "#55a868", "#c44e52"]
    for ax, met, title, color in zip(axs, metrics, titles, colors):
        vals = pd.to_numeric(context[met], errors="coerce").dropna().values if met in context.columns else np.array([])
        ax.bar(np.arange(len(vals)), vals, color=color, alpha=0.8)
        ax.set_title(title)
        ax.set_xlabel("Major earthquake")
        ax.set_ylabel(met)
    savefig(fig, outpath)


def main() -> None:
    try:
        ensure_output_dir(OUTPUT_DIR)
        for p in OUTPUT_DIR.glob("*.png"):
            p.unlink()

        cat, main, mech, sta, match, mech_flagged = load_tables()
        cat = coerce_numeric(cat, ["latitude", "longitude", "depth_km", "magnitude"])
        main = coerce_numeric(main, ["latitude", "longitude", "depth_km", "magnitude"])
        sta = coerce_numeric(sta, ["latitude", "longitude", "elevation_m"])
        mech = coerce_numeric(mech_flagged, ["latitude", "longitude", "depth_km", "mag_1", "mag_2", "strike_plane1", "dip_plane1", "rake_plane1", "P_axis_azimuth", "P_axis_dip", "T_axis_azimuth", "T_axis_dip", "N_axis_azimuth", "N_axis_dip"])
        context = pd.read_csv(CONTEXT_TABLE)
        bval_path = REGIONAL_SUMMARY_DIR / "mc_bvalue_summary.csv"
        depth_seg_path = REGIONAL_SUMMARY_DIR / "depth_segmentation_summary.csv"
        bval = pd.read_csv(bval_path) if bval_path.exists() else pd.DataFrame()
        depth_seg = pd.read_csv(depth_seg_path) if depth_seg_path.exists() else pd.DataFrame(columns=["depth_min_km", "depth_max_km"])

        required = {
            "cat": ["origin_time", "latitude", "longitude", "depth_km", "magnitude"],
            "main": ["origin_time", "latitude", "longitude", "depth_km", "magnitude"],
            "sta": ["latitude", "longitude"],
            "match": ["origin_time", "matched_event_id", "matched_time"],
            "context": ["reference_id", "main_time", "main_latitude", "main_longitude", "main_depth_km", "main_magnitude"],
        }
        tables = {"cat": cat, "main": main, "sta": sta, "match": match, "context": context}
        for name, cols in required.items():
            missing = [c for c in cols if c not in tables[name].columns]
            if missing:
                raise ValueError(f"{name} table missing required columns: {missing}")
        if len(cat) == 0:
            raise ValueError("Cleaned catalog is empty; cannot generate diagnostic figures")
        if len(main) == 0:
            raise ValueError("Main earthquake table is empty; cannot generate diagnostic figures")

        log(f"Loaded catalog={len(cat)}, main={len(main)}, mechanism={len(mech)}, stations={len(sta)}, matches={len(match)}")
        plot_regional_map(cat, main, sta, mech, OUTPUT_DIR / "figure_01_regional_map.png")
        plot_time_magnitude(cat, main, OUTPUT_DIR / "figure_02_time_magnitude.png")
        plot_depth_time(cat, main, OUTPUT_DIR / "figure_03_depth_time.png")
        plot_magnitude_depth(cat, main, OUTPUT_DIR / "figure_04_magnitude_depth.png")
        plot_frequency_magnitude(cat, bval, OUTPUT_DIR / "figure_05_magnitude_frequency_mc_bvalue.png")
        plot_spatial_density(cat, OUTPUT_DIR / "figure_06_spatial_density.png")
        plot_depth_distribution(cat, depth_seg, OUTPUT_DIR / "figure_07_depth_distribution.png")
        plot_cross_section(cat, OUTPUT_DIR / "figure_08_depth_cross_section.png")
        plot_station_coverage(cat, sta, OUTPUT_DIR / "figure_09_station_coverage.png")
        plot_mechanism_diagnostics(mech, main, OUTPUT_DIR / "figure_10_mechanism_diagnostics.png")
        plot_context_overview(context, OUTPUT_DIR / "figure_11_mainshock_context_overview.png")

        manifest = pd.DataFrame(
            [
                {"figure_file": p.name, "exists": p.exists(), "size_bytes": p.stat().st_size if p.exists() else 0}
                for p in sorted(OUTPUT_DIR.glob("*.png"))
            ]
        )
        manifest.to_csv(OUTPUT_DIR / "figure_manifest.csv", index=False)
        log(f"Saved {len(manifest)} figure files to {OUTPUT_DIR}")

    except Exception:
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
