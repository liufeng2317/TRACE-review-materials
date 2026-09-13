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


DATA_DIR = Path(
    "<CASE_ROOT>/data"
)
OUTPUT_DIR = Path(
    "<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/04_mainshock_regional_context"
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

CLEAN_CATALOG = STAGE1_DIR / "stage1_regional_catalog_clean.csv"
CLEAN_MAIN = STAGE1_DIR / "main_earthquake_clean.csv"
CLEAN_MECH = STAGE1_DIR / "source_mechanism_clean.csv"
CLEAN_STATIONS = STAGE1_DIR / "station_clean.csv"
MATCH_TABLE = MATCH_DIR / "major_earthquake_matches.csv"

EARTH_RADIUS_KM = 6371.0088
plt.rcParams.update({
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
})


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


def load_tables() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    cat = pd.read_csv(CLEAN_CATALOG, parse_dates=["origin_time"])
    main = pd.read_csv(CLEAN_MAIN, parse_dates=["origin_time"])
    mech = pd.read_csv(CLEAN_MECH, parse_dates=["origin_time"])
    sta = pd.read_csv(CLEAN_STATIONS)
    match = pd.read_csv(MATCH_TABLE, parse_dates=["origin_time", "matched_time"])
    return cat, main, mech, sta, match


def coerce_numeric(df: pd.DataFrame, cols: List[str]) -> pd.DataFrame:
    out = df.copy()
    for c in cols:
        if c in out.columns:
            out[c] = pd.to_numeric(out[c], errors="coerce")
    return out


def normalize_time(df: pd.DataFrame, col: str = "origin_time") -> pd.DataFrame:
    out = df.copy()
    if col in out.columns:
        out[col] = pd.to_datetime(out[col], errors="coerce", utc=True)
    return out


def _mechanism_geometry_mask(mech: pd.DataFrame) -> pd.Series:
    geom_cols = ["P_axis_azimuth", "P_axis_dip", "T_axis_azimuth", "T_axis_dip", "N_axis_azimuth", "N_axis_dip"]
    cols = [c for c in geom_cols if c in mech.columns]
    if not cols:
        return pd.Series(False, index=mech.index)
    return mech[cols].notna().any(axis=1)


def _mechanism_core_mask(mech: pd.DataFrame) -> pd.Series:
    core_cols = ["strike_plane1", "dip_plane1", "rake_plane1"]
    cols = [c for c in core_cols if c in mech.columns]
    if len(cols) < 3:
        return pd.Series(False, index=mech.index)
    return mech[cols].notna().all(axis=1)


def local_radius_km(cat: pd.DataFrame, sta: pd.DataFrame) -> float:
    if len(cat) < 2 or len(sta) == 0:
        return 35.0
    sample = cat.sample(n=min(1500, len(cat)), random_state=11)
    nearest = []
    for _, ev in sample.iterrows():
        d = haversine_km(sta["longitude"].values, sta["latitude"].values, ev["longitude"], ev["latitude"])
        nearest.append(np.min(d))
    nearest = np.asarray(nearest)
    r = float(np.clip(np.nanmedian(nearest) * 3.0, 20.0, 80.0))
    return r


def local_context_for_event(
    main_row: pd.Series,
    cat: pd.DataFrame,
    sta: pd.DataFrame,
    mech: pd.DataFrame,
    regional_median_depth: float,
    regional_depth_iqr: float,
    regional_median_density: float,
    regional_mech_core_fraction: float,
    regional_mech_geom_fraction: float,
) -> Tuple[Dict[str, object], pd.DataFrame, pd.DataFrame]:
    lat = float(main_row["latitude"])
    lon = float(main_row["longitude"])
    depth = float(main_row["depth_km"])
    mag = float(main_row["magnitude"])
    radius_km = local_radius_km(cat, sta)
    depth_window_km = max(20.0, 1.5 * regional_depth_iqr)
    local_mask = haversine_km(lon, lat, cat["longitude"].values, cat["latitude"].values) <= radius_km
    depth_mask = (cat["depth_km"] >= depth - depth_window_km) & (cat["depth_km"] <= depth + depth_window_km)
    local_cat = cat.loc[local_mask & depth_mask].copy()
    if len(local_cat) == 0:
        local_cat = cat.loc[local_mask].copy()

    local_area_km2 = max(np.pi * radius_km**2, 1.0)
    local_density = len(local_cat) / local_area_km2
    local_depth_median = float(local_cat["depth_km"].median()) if len(local_cat) else np.nan
    local_depth_iqr = float(local_cat["depth_km"].quantile(0.75) - local_cat["depth_km"].quantile(0.25)) if len(local_cat) >= 4 else np.nan
    local_depth_p25 = float(local_cat["depth_km"].quantile(0.25)) if len(local_cat) else np.nan
    local_depth_p75 = float(local_cat["depth_km"].quantile(0.75)) if len(local_cat) else np.nan
    local_mag_median = float(local_cat["magnitude"].median()) if len(local_cat) else np.nan

    sta_dist = haversine_km(lon, lat, sta["longitude"].values, sta["latitude"].values) if len(sta) else np.asarray([])
    nearby_sta = sta.loc[sta_dist <= radius_km].copy() if len(sta) else sta.copy()
    sta_count = int(len(nearby_sta))
    sta_nearest = float(np.min(sta_dist)) if len(sta_dist) else np.nan
    sta_median_dist = float(np.median(sta_dist[sta_dist <= radius_km])) if len(nearby_sta) else np.nan
    sta_p90_dist = float(np.quantile(sta_dist[sta_dist <= radius_km], 0.9)) if len(nearby_sta) >= 2 else np.nan

    if len(mech) and {"latitude", "longitude"}.issubset(mech.columns):
        mech_dist = haversine_km(lon, lat, mech["longitude"].values, mech["latitude"].values)
        if "depth_km" in mech.columns:
            mech_local = mech.loc[(mech_dist <= radius_km) & ((mech["depth_km"].isna()) | (np.abs(mech["depth_km"] - depth) <= depth_window_km))].copy()
        else:
            mech_local = mech.loc[mech_dist <= radius_km].copy()
    else:
        mech_local = mech.iloc[0:0].copy()
    mech_geom = _mechanism_geometry_mask(mech_local)
    mech_core = _mechanism_core_mask(mech_local)
    mech_local_count = int(len(mech_local))
    mech_core_count = int(mech_core.sum()) if len(mech_local) else 0
    mech_geom_count = int(mech_geom.sum()) if len(mech_local) else 0

    dev_depth = abs(depth - regional_median_depth)
    depth_domain = "distinct" if dev_depth > max(15.0, regional_depth_iqr) else "typical"
    density_ratio = local_density / regional_median_density if regional_median_density > 0 else np.nan
    spatial_domain = "distinct" if np.isfinite(density_ratio) and (density_ratio > 2.0 or density_ratio < 0.5) else "typical"
    coverage_note = "sparse" if sta_count < 8 else ("moderate" if sta_count < 20 else "good")
    mech_note = "sparse" if mech_local_count < 3 else ("moderate" if mech_local_count < 10 else "good")
    threshold_note = []
    if radius_km <= 40:
        threshold_note.append("use compact search radius (~40 km) for sequence work")
    else:
        threshold_note.append(f"use radius near {radius_km:.0f} km for sequence work")
    if depth_window_km <= 20:
        threshold_note.append("apply tight depth window (~20 km)")
    else:
        threshold_note.append(f"apply depth window near ±{depth_window_km:.0f} km")
    if mag >= 6.0:
        threshold_note.append("consider higher magnitude threshold for coda/aftershock screening")

    context = {
        "reference_id": main_row.get("reference_id", ""),
        "matched_event_id": main_row.get("matched_event_id", ""),
        "main_time": main_row.get("origin_time", pd.NaT),
        "main_latitude": lat,
        "main_longitude": lon,
        "main_depth_km": depth,
        "main_magnitude": mag,
        "local_radius_km": radius_km,
        "local_depth_window_km": depth_window_km,
        "local_event_count": int(len(local_cat)),
        "local_event_density_per_km2": local_density,
        "regional_median_density_per_km2": regional_median_density,
        "density_ratio_to_regional_median": density_ratio,
        "local_depth_median_km": local_depth_median,
        "local_depth_iqr_km": local_depth_iqr,
        "local_depth_p25_km": local_depth_p25,
        "local_depth_p75_km": local_depth_p75,
        "regional_depth_median_km": regional_median_depth,
        "regional_depth_iqr_km": regional_depth_iqr,
        "local_magnitude_median": local_mag_median,
        "station_count_local": sta_count,
        "station_nearest_distance_km": sta_nearest,
        "station_median_distance_km": sta_median_dist,
        "station_p90_distance_km": sta_p90_dist,
        "mechanism_local_records": mech_local_count,
        "mechanism_geometry_local": mech_geom_count,
        "mechanism_core_local": mech_core_count,
        "regional_mechanism_geometry_fraction": regional_mech_geom_fraction,
        "regional_mechanism_core_fraction": regional_mech_core_fraction,
        "mechanism_geometry_fraction_local": float(mech_geom.mean()) if len(mech_local) else np.nan,
        "mechanism_core_fraction_local": float(mech_core.mean()) if len(mech_local) else np.nan,
        "depth_domain_flag": depth_domain,
        "spatial_domain_flag": spatial_domain,
        "station_coverage_note": coverage_note,
        "mechanism_coverage_note": mech_note,
        "sequence_threshold_note": "; ".join(threshold_note),
        "edge_effect_flag": bool(
            (lat <= cat["latitude"].quantile(0.05)) or (lat >= cat["latitude"].quantile(0.95)) or (lon <= cat["longitude"].quantile(0.05)) or (lon >= cat["longitude"].quantile(0.95))
        ),
    }
    return context, local_cat, nearby_sta


def plot_context_map(cat: pd.DataFrame, sta: pd.DataFrame, mech: pd.DataFrame, match: pd.DataFrame, outpath: Path) -> None:
    fig, ax = plt.subplots(figsize=(7.6, 6.6))
    sc = ax.scatter(cat["longitude"], cat["latitude"], c=cat["depth_km"], s=4, alpha=0.18, cmap="viridis_r", linewidths=0, rasterized=True)
    ax.scatter(sta["longitude"], sta["latitude"], s=18, facecolors="none", edgecolors="#1f77b4", linewidths=0.8, label="Stations")
    ax.scatter(match["longitude"], match["latitude"], s=100, marker="*", c="#d62728", edgecolors="k", linewidths=0.6, label="Major earthquakes")
    if len(mech) and {"longitude", "latitude"}.issubset(mech.columns):
        mech_plot = mech.dropna(subset=["longitude", "latitude"])
        if len(mech_plot):
            ax.scatter(mech_plot["longitude"], mech_plot["latitude"], s=18, c="#ff7f0e", alpha=0.35, label="Mechanism records")
    ax.set_xlabel("Longitude (°E)")
    ax.set_ylabel("Latitude (°N)")
    ax.set_title("Regional context of major earthquakes")
    fig.colorbar(sc, ax=ax, pad=0.02, label="Depth (km)")
    ax.legend(frameon=False, loc="best")
    ax.set_aspect("equal", adjustable="box")
    fig.tight_layout()
    fig.savefig(outpath, bbox_inches="tight")
    plt.close(fig)


def plot_context_panels(summary: pd.DataFrame, outpath: Path) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(10.0, 7.6))
    axs = axes.ravel()
    x = np.arange(len(summary))
    axs[0].bar(x, summary["local_event_count"], color="#4daf4a")
    axs[0].set_xticks(x)
    axs[0].set_xticklabels(summary["reference_id"], rotation=0)
    axs[0].set_ylabel("Local event count")
    axs[0].set_title("Local catalog density")
    axs[1].bar(x, summary["station_count_local"], color="#377eb8")
    axs[1].set_xticks(x)
    axs[1].set_xticklabels(summary["reference_id"], rotation=0)
    axs[1].set_ylabel("Nearby stations")
    axs[1].set_title("Station coverage")
    axs[2].bar(x, summary["mechanism_local_records"], color="#ff7f0e")
    axs[2].set_xticks(x)
    axs[2].set_xticklabels(summary["reference_id"], rotation=0)
    axs[2].set_ylabel("Nearby mechanism records")
    axs[2].set_title("Mechanism availability")
    axs[3].bar(x, summary["density_ratio_to_regional_median"], color="#984ea3")
    axs[3].axhline(1.0, color="k", lw=0.8, ls="--")
    axs[3].set_xticks(x)
    axs[3].set_xticklabels(summary["reference_id"], rotation=0)
    axs[3].set_ylabel("Density ratio")
    axs[3].set_title("Local vs regional density")
    for ax in axs:
        ax.grid(True, alpha=0.2)
    fig.tight_layout()
    fig.savefig(outpath, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    try:
        ensure_output_dir(OUTPUT_DIR)
        for p in OUTPUT_DIR.glob("*"):
            if p.is_file():
                p.unlink()

        cat, main, mech, sta, match = load_tables()
        cat = coerce_numeric(normalize_time(cat), ["latitude", "longitude", "depth_km", "magnitude"])
        main = coerce_numeric(normalize_time(main), ["latitude", "longitude", "depth_km", "magnitude"])
        mech = coerce_numeric(normalize_time(mech), ["latitude", "longitude", "depth_km", "mag_1", "mag_2", "strike_plane1", "dip_plane1", "rake_plane1", "P_axis_azimuth", "P_axis_dip", "T_axis_azimuth", "T_axis_dip", "N_axis_azimuth", "N_axis_dip"])
        sta = coerce_numeric(sta, ["latitude", "longitude", "elevation_m"])
        match = coerce_numeric(normalize_time(match), ["latitude", "longitude", "depth_km", "magnitude", "time_diff_sec", "distance_km", "depth_diff_km", "mag_diff", "candidate_count", "search_window_hours"])

        cat = cat.dropna(subset=["origin_time", "latitude", "longitude", "depth_km", "magnitude"]).copy()
        main = main.dropna(subset=["origin_time", "latitude", "longitude", "depth_km", "magnitude"]).copy()
        mech = mech.copy()
        sta = sta.dropna(subset=["latitude", "longitude"]).copy()
        match = match.copy()

        regional_depth_median = float(cat["depth_km"].median())
        regional_depth_iqr = float(cat["depth_km"].quantile(0.75) - cat["depth_km"].quantile(0.25))
        regional_density = len(cat) / max((cat["latitude"].max() - cat["latitude"].min()) * (cat["longitude"].max() - cat["longitude"].min()) * 111.0 * 111.0, 1.0)
        if not np.isfinite(regional_density) or regional_density <= 0:
            regional_density = float(len(cat) / max(np.pi * local_radius_km(cat, sta) ** 2, 1.0))
        regional_mech_geom_fraction = float(_mechanism_geometry_mask(mech).mean()) if len(mech) else np.nan
        regional_mech_core_fraction = float(_mechanism_core_mask(mech).mean()) if len(mech) else np.nan

        if "reference_id" not in match.columns:
            match["reference_id"] = [f"M{i+1}" for i in range(len(match))]
        if "matched_event_id" not in match.columns:
            match["matched_event_id"] = ""

        rows = []
        local_catalog_rows = []
        local_station_rows = []
        for _, mrow in match.iterrows():
            context, local_cat, nearby_sta = local_context_for_event(
                mrow,
                cat,
                sta,
                mech,
                regional_depth_median,
                regional_depth_iqr,
                regional_density,
                regional_mech_core_fraction,
                regional_mech_geom_fraction,
            )
            rows.append(context)
            if len(local_cat):
                local_cat = local_cat.copy()
                local_cat.insert(0, "reference_id", mrow.get("reference_id", ""))
                local_catalog_rows.append(local_cat)
            if len(nearby_sta):
                nearby_sta = nearby_sta.copy()
                nearby_sta.insert(0, "reference_id", mrow.get("reference_id", ""))
                local_station_rows.append(nearby_sta)

        summary = pd.DataFrame(rows)
        local_catalog = pd.concat(local_catalog_rows, ignore_index=True) if local_catalog_rows else pd.DataFrame()
        local_station = pd.concat(local_station_rows, ignore_index=True) if local_station_rows else pd.DataFrame()

        if len(summary) == 0:
            raise ValueError("No mainshock context rows were produced")

        summary.to_csv(OUTPUT_DIR / "mainshock_context_summary.csv", index=False)
        local_catalog.to_csv(OUTPUT_DIR / "mainshock_local_catalog_windows.csv", index=False)
        local_station.to_csv(OUTPUT_DIR / "mainshock_local_station_windows.csv", index=False)

        regional_context = pd.DataFrame([
            {
                "regional_event_count": len(cat),
                "regional_depth_median_km": regional_depth_median,
                "regional_depth_iqr_km": regional_depth_iqr,
                "regional_density_proxy": regional_density,
                "regional_mechanism_geometry_fraction": regional_mech_geom_fraction,
                "regional_mechanism_core_fraction": regional_mech_core_fraction,
                "regional_station_count": len(sta),
                "mainshock_count": len(match),
                "distinct_depth_domain_count": int((summary["depth_domain_flag"] == "distinct").sum()),
                "distinct_spatial_domain_count": int((summary["spatial_domain_flag"] == "distinct").sum()),
                "edge_effect_count": int(summary["edge_effect_flag"].sum()),
            }
        ])
        regional_context.to_csv(OUTPUT_DIR / "regional_context_overview.csv", index=False)

        threshold_notes = summary[["reference_id", "matched_event_id", "depth_domain_flag", "spatial_domain_flag", "station_coverage_note", "mechanism_coverage_note", "sequence_threshold_note"]].copy()
        threshold_notes.to_csv(OUTPUT_DIR / "sequence_threshold_notes.csv", index=False)

        plot_context_map(cat, sta, mech, match, OUTPUT_DIR / "figure_mainshock_regional_context_map.png")
        plot_context_panels(summary, OUTPUT_DIR / "figure_mainshock_context_panels.png")

        print("[04_mainshock_regional_context] Completed successfully.", flush=True)
        print(f"[04_mainshock_regional_context] Output directory: {OUTPUT_DIR}", flush=True)
        print(f"[04_mainshock_regional_context] Mainshocks processed: {len(summary)}", flush=True)
        print(f"[04_mainshock_regional_context] Distinct depth-domain count: {int((summary['depth_domain_flag'] == 'distinct').sum())}", flush=True)
        print(f"[04_mainshock_regional_context] Distinct spatial-domain count: {int((summary['spatial_domain_flag'] == 'distinct').sum())}", flush=True)
        print(f"[04_mainshock_regional_context] Station coverage median note: {summary['station_coverage_note'].mode().iloc[0] if len(summary) else 'n/a'}", flush=True)

    except Exception:
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
